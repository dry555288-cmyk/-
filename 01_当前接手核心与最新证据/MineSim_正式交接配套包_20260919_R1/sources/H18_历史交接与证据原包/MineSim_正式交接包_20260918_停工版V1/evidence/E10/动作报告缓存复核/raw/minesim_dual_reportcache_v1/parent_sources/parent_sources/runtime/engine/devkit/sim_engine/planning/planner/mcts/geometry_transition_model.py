from __future__ import annotations

import math
from dataclasses import dataclass, replace
from typing import Dict, Iterable, List, Tuple

from shapely.ops import unary_union
from shapely.prepared import prep

from devkit.common.actor_state.oriented_box import OrientedBox
from devkit.common.actor_state.state_representation import StateSE2
from devkit.common.geometry.transform import translate_longitudinally

from .action_space import MCTSAction
from .state import MCTSState
from .transition_model import TransitionModel


# Motion-model uncertainty band.
#
# Small yaw rates use constant velocity (CV), large yaw rates
# use constant turn rate and velocity (CTRV), and intermediate
# rates preserve both plausible future occupancies. This avoids
# a discontinuous CV-to-CTRV switch near a single threshold.
CV_ONLY_MAX_ABS_YAW_RATE_RPS = 0.10
CTRV_ONLY_MIN_ABS_YAW_RATE_RPS = 0.20

# Expand predicted obstacle occupancy to preserve clearance
# under short-horizon model and discretization error.
OBSTACLE_SAFETY_MARGIN_M = 0.5


@dataclass(frozen=True)
class ObstacleSnapshot:
    """Obstacle state captured at the beginning of one planning cycle."""

    token: str
    box: OrientedBox
    x: float
    y: float
    heading: float
    speed_mps: float
    angular_velocity_rps: float


def as_oriented_box(car_footprint) -> OrientedBox:
    """Return the OrientedBox contained in an ego car footprint."""

    return getattr(
        car_footprint,
        "oriented_box",
        car_footprint,
    )


def build_obstacle_snapshots(
    unique_observations,
) -> List[ObstacleSnapshot]:
    """Convert tracked objects into immutable prediction inputs."""

    snapshots: List[ObstacleSnapshot] = []

    for token, tracked_object in unique_observations.items():
        if str(token) == "ego":
            continue

        box = getattr(tracked_object, "box", None)
        center = getattr(tracked_object, "center", None)

        if box is None or center is None:
            continue

        velocity = getattr(
            tracked_object,
            "velocity",
            None,
        )

        if velocity is None:
            speed = 0.0
        else:
            speed = math.hypot(
                float(velocity.x),
                float(velocity.y),
            )

        snapshots.append(
            ObstacleSnapshot(
                token=str(token),
                box=box,
                x=float(center.x),
                y=float(center.y),
                heading=float(center.heading),
                speed_mps=speed,
                angular_velocity_rps=float(
                    getattr(
                        tracked_object,
                        "angular_velocity",
                        0.0,
                    )
                ),
            )
        )

    return snapshots


class RouteGeometryCache:
    """Precomputed ego vehicle polygons along the route."""

    def __init__(
        self,
        ego_path,
        ego_box: OrientedBox,
        grid_step_m: float = 0.05,
    ):
        if grid_step_m <= 0.0:
            raise ValueError(
                "grid_step_m must be positive."
            )

        self._start_progress = float(
            ego_path.get_start_progress()
        )
        self._end_progress = float(
            ego_path.get_end_progress()
        )
        self._grid_step_m = float(grid_step_m)

        # MineSim route progress is defined at the rear axle.
        # OrientedBox poses are defined at the geometric center.
        #
        # as_oriented_box(CarFootprint) preserves the CarFootprint
        # object, therefore rear_axle_to_center_dist is available
        # for production ego vehicles. Bare OrientedBox test
        # fixtures retain legacy zero-offset semantics.
        self._rear_axle_to_center_dist_m = float(
            getattr(
                ego_box,
                "rear_axle_to_center_dist",
                0.0,
            )
        )

        route_length = max(
            0.0,
            self._end_progress
            - self._start_progress,
        )

        count = (
            int(
                math.ceil(
                    route_length
                    / self._grid_step_m
                )
            )
            + 1
        )

        geometries = []

        for index in range(count):
            progress = min(
                self._end_progress,
                self._start_progress
                + index * self._grid_step_m,
            )

            path_state = (
                ego_path.get_state_at_progress(
                    progress
                )
            )

            rear_axle_pose = StateSE2(
                float(path_state.x),
                float(path_state.y),
                float(path_state.heading),
            )

            center_pose = translate_longitudinally(
                rear_axle_pose,
                self._rear_axle_to_center_dist_m,
            )

            geometries.append(
                OrientedBox.from_new_pose(
                    ego_box,
                    center_pose,
                ).geometry
            )

        self._geometries = tuple(geometries)

    @property
    def geometry_count(self) -> int:
        return len(self._geometries)

    @property
    def grid_step_m(self) -> float:
        return self._grid_step_m

    def geometry_at(self, route_s: float):
        progress = max(
            self._start_progress,
            min(
                float(route_s),
                self._end_progress,
            ),
        )

        index = int(
            round(
                (
                    progress
                    - self._start_progress
                )
                / self._grid_step_m
            )
        )

        index = max(
            0,
            min(
                index,
                len(self._geometries) - 1,
            ),
        )

        return self._geometries[index]


class GeometryAwareTransitionModel:
    """
    Wrap the longitudinal transition model with fast 2D collision checks.

    Ego motion follows route progress from MCTSState. Obstacles use a
    constant-turn-rate-and-velocity prediction during each search.
    """

    def __init__(
        self,
        base_transition: TransitionModel,
        route_geometry_cache: RouteGeometryCache,
        obstacle_snapshots: Iterable[
            ObstacleSnapshot
        ],
        max_depth: int,
        collision_sample_dt_s: float = 0.1,
    ):
        if max_depth <= 0:
            raise ValueError(
                "max_depth must be positive."
            )

        if collision_sample_dt_s <= 0.0:
            raise ValueError(
                "collision_sample_dt_s must be positive."
            )

        self.base = base_transition
        self.cfg = base_transition.cfg
        self.action_to_accel = (
            base_transition.action_to_accel
        )

        self.route_geometry_cache = (
            route_geometry_cache
        )
        self.collision_sample_dt_s = float(
            collision_sample_dt_s
        )

        self._obstacle_snapshots = tuple(
            obstacle_snapshots
        )
        self._step_cache: Dict[
            Tuple[Tuple, MCTSAction],
            MCTSState,
        ] = {}
        self._collision_step_cache: Dict[
            Tuple[Tuple, MCTSAction],
            MCTSState,
        ] = {}

        self._obstacle_lookup = (
            self._build_obstacle_lookup(
                max_depth=max_depth,
            )
        )

    @property
    def obstacle_count(self) -> int:
        return len(self._obstacle_snapshots)

    @property
    def lookup_tick_count(self) -> int:
        return len(self._obstacle_lookup)

    @staticmethod
    def _predict_cv_pose(
        snapshot: ObstacleSnapshot,
        prediction_time_s: float,
    ) -> StateSE2:
        distance = (
            snapshot.speed_mps
            * prediction_time_s
        )

        return StateSE2(
            snapshot.x
            + distance
            * math.cos(snapshot.heading),
            snapshot.y
            + distance
            * math.sin(snapshot.heading),
            snapshot.heading,
        )

    @staticmethod
    def _predict_ctrv_pose(
        snapshot: ObstacleSnapshot,
        prediction_time_s: float,
    ) -> StateSE2:
        omega = snapshot.angular_velocity_rps

        if abs(omega) < 1e-8:
            return (
                GeometryAwareTransitionModel
                ._predict_cv_pose(
                    snapshot,
                    prediction_time_s,
                )
            )

        predicted_heading = (
            snapshot.heading
            + omega * prediction_time_s
        )

        return StateSE2(
            snapshot.x
            + snapshot.speed_mps / omega
            * (
                math.sin(predicted_heading)
                - math.sin(snapshot.heading)
            ),
            snapshot.y
            + snapshot.speed_mps / omega
            * (
                -math.cos(predicted_heading)
                + math.cos(snapshot.heading)
            ),
            predicted_heading,
        )

    @classmethod
    def _predict_obstacle_poses(
        cls,
        snapshot: ObstacleSnapshot,
        prediction_time_s: float,
    ) -> Tuple[StateSE2, ...]:
        abs_omega = abs(
            snapshot.angular_velocity_rps
        )

        if (
            abs_omega
            < CV_ONLY_MAX_ABS_YAW_RATE_RPS
        ):
            return (
                cls._predict_cv_pose(
                    snapshot,
                    prediction_time_s,
                ),
            )

        if (
            abs_omega
            > CTRV_ONLY_MIN_ABS_YAW_RATE_RPS
        ):
            return (
                cls._predict_ctrv_pose(
                    snapshot,
                    prediction_time_s,
                ),
            )

        # Within the uncertainty band, keep both possible
        # occupancies instead of switching models abruptly.
        return (
            cls._predict_cv_pose(
                snapshot,
                prediction_time_s,
            ),
            cls._predict_ctrv_pose(
                snapshot,
                prediction_time_s,
            ),
        )

    @classmethod
    def _predict_obstacle_pose(
        cls,
        snapshot: ObstacleSnapshot,
        prediction_time_s: float,
    ) -> StateSE2:
        """Return one representative pose for diagnostics."""

        abs_omega = abs(
            snapshot.angular_velocity_rps
        )

        if (
            abs_omega
            < (
                CV_ONLY_MAX_ABS_YAW_RATE_RPS
                + CTRV_ONLY_MIN_ABS_YAW_RATE_RPS
            ) / 2.0
        ):
            return cls._predict_cv_pose(
                snapshot,
                prediction_time_s,
            )

        return cls._predict_ctrv_pose(
            snapshot,
            prediction_time_s,
        )

    def _build_obstacle_lookup(
        self,
        max_depth: int,
    ):
        maximum_time_s = (
            self.cfg.dt * max_depth
        )
        maximum_tick = int(
            math.ceil(
                maximum_time_s
                / self.collision_sample_dt_s
            )
        )

        lookup = {}

        for tick in range(
            1,
            maximum_tick + 1,
        ):
            prediction_time_s = (
                tick
                * self.collision_sample_dt_s
            )

            raw_geometries = []

            for snapshot in self._obstacle_snapshots:
                poses = self._predict_obstacle_poses(
                    snapshot,
                    prediction_time_s,
                )

                for pose in poses:
                    raw_geometries.append(
                        OrientedBox.from_new_pose(
                            snapshot.box,
                            pose,
                        ).geometry
                    )

            if not raw_geometries:
                continue

            raw_combined = unary_union(
                raw_geometries
            )

            # Preserve the exact hard-safety behavior:
            # each predicted occupancy is expanded before union.
            buffered_combined = unary_union(
                [
                    geometry.buffer(
                        OBSTACLE_SAFETY_MARGIN_M
                    )
                    for geometry in raw_geometries
                ]
            )

            lookup[tick] = (
                buffered_combined.bounds,
                prep(buffered_combined),
                raw_combined,
            )

        return lookup

    @staticmethod
    def _bounds_overlap(
        first,
        second,
    ) -> bool:
        return not (
            first[2] < second[0]
            or second[2] < first[0]
            or first[3] < second[1]
            or second[3] < first[1]
        )

    def _evaluate_2d_safety(
        self,
        previous_state: MCTSState,
        next_state: MCTSState,
        compute_clearance: bool = True,
    ) -> Tuple[bool, float]:
        """
        Return hard-safety violation and minimum raw 2D clearance.

        Collision uses obstacle occupancies expanded by the validated
        safety margin. When requested, clearance uses the original,
        unbuffered vehicle geometries so it represents physical polygon
        separation. Collision-only viability checks skip that expensive
        distance calculation without changing hard-safety evaluation.
        """

        duration_s = max(
            self.cfg.eps,
            next_state.time_s
            - previous_state.time_s,
        )

        sample_count = max(
            1,
            int(
                round(
                    duration_s
                    / self.collision_sample_dt_s
                )
            ),
        )

        route_delta = (
            next_state.route_s
            - previous_state.route_s
        )

        collision = False
        minimum_clearance_m = float("inf")

        for sample_index in range(
            1,
            sample_count + 1,
        ):
            fraction = (
                sample_index / sample_count
            )

            route_s = (
                previous_state.route_s
                + route_delta * fraction
            )

            absolute_time_s = (
                previous_state.time_s
                + duration_s * fraction
            )

            tick = int(
                round(
                    absolute_time_s
                    / self.collision_sample_dt_s
                )
            )

            obstacle_entry = (
                self._obstacle_lookup.get(tick)
            )

            if obstacle_entry is None:
                continue

            (
                obstacle_bounds,
                prepared_obstacles,
                raw_obstacles,
            ) = obstacle_entry

            ego_geometry = (
                self.route_geometry_cache
                .geometry_at(route_s)
            )

            if compute_clearance:
                minimum_clearance_m = min(
                    minimum_clearance_m,
                    float(
                        ego_geometry.distance(
                            raw_obstacles
                        )
                    ),
                )

            if not self._bounds_overlap(
                ego_geometry.bounds,
                obstacle_bounds,
            ):
                continue

            # Shapely intersects also treats touching boxes
            # as a collision, matching strict validation.
            if prepared_obstacles.intersects(
                ego_geometry
            ):
                collision = True

        return collision, minimum_clearance_m

    def step(
        self,
        state: MCTSState,
        action: MCTSAction,
    ) -> MCTSState:
        key = (
            state.transition_cache_key(),
            action,
        )

        cached = self._step_cache.get(key)

        if cached is not None:
            return cached

        next_state = self.base.step(
            state,
            action,
        )

        (
            collision,
            minimum_clearance_m,
        ) = self._evaluate_2d_safety(
            state,
            next_state,
        )

        result = replace(
            next_state,
            collision=collision,
            minimum_clearance_m=(
                minimum_clearance_m
            ),
        )

        self._step_cache[key] = result
        return result

    def step_collision_only(
        self,
        state: MCTSState,
        action: MCTSAction,
    ) -> MCTSState:
        """
        Return an exact hard-collision transition without clearance.

        A previously computed full transition is reused when available.
        Collision-only results are kept in a separate cache because
        their clearance value is intentionally infinite.
        """

        key = (
            state.transition_cache_key(),
            action,
        )

        full_cached = self._step_cache.get(key)

        if full_cached is not None:
            return full_cached

        cached = self._collision_step_cache.get(key)

        if cached is not None:
            return cached

        next_state = self.base.step(
            state,
            action,
        )

        collision, _ = self._evaluate_2d_safety(
            state,
            next_state,
            compute_clearance=False,
        )

        result = replace(
            next_state,
            collision=collision,
            minimum_clearance_m=float("inf"),
        )

        self._collision_step_cache[key] = result
        return result
