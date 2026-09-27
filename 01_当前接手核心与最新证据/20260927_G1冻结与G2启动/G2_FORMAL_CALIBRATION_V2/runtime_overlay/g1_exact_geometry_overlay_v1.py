"""G1 exact-tick A/B geometry overlay V1.

Technical safety staging only:
- preserves the frozen Retry2 adapter and 1 m route caches;
- hard A/B collision evaluation uses an explicit exact route-pose provider;
- guide/phase code may continue reading transition._route_geometry_caches;
- no MCTS/Teacher experiment is run here.
"""
from __future__ import annotations

import math
from typing import Mapping, Tuple

from devkit.common.actor_state.oriented_box import OrientedBox
from devkit.common.actor_state.state_representation import StateSE2
from devkit.common.geometry.transform import translate_longitudinally

from candidate_mcts.dual_stop_adapter_v1 import (
    DualStopFleetTransition as FrozenDualStopFleetTransition,
    need,
)
from candidate_mcts.dual_stop_motion_v1 import DestinationStopTransition
from candidate_mcts.fleet_collision import evaluate_internal_fleet_collision

VERSION = "G1_EXACT_TICK_GEOMETRY_OVERLAY_V1"


class ExactRouteGeometryProvider:
    """Exact footprint from the bound route pose; no route-space cache snapping."""

    def __init__(self, ego_path, ego_box: OrientedBox):
        self._ego_path = ego_path
        self._ego_box = ego_box
        self._start_progress = float(ego_path.get_start_progress())
        self._end_progress = float(ego_path.get_end_progress())
        need(
            math.isfinite(self._start_progress)
            and math.isfinite(self._end_progress)
            and self._end_progress >= self._start_progress,
            "EXACT_ROUTE_PROGRESS_DOMAIN",
        )
        self._rear_axle_to_center_dist_m = float(
            getattr(ego_box, "rear_axle_to_center_dist", 0.0)
        )
        need(
            math.isfinite(self._rear_axle_to_center_dist_m),
            "EXACT_REAR_AXLE_OFFSET_NONFINITE",
        )

    def geometry_at(self, route_s: float):
        s = float(route_s)
        need(math.isfinite(s), "EXACT_ROUTE_S_NONFINITE")
        progress = max(self._start_progress, min(s, self._end_progress))

        path_state = self._ego_path.get_state_at_progress(progress)
        rear_axle_pose = StateSE2(
            float(path_state.x),
            float(path_state.y),
            float(path_state.heading),
        )
        center_pose = translate_longitudinally(
            rear_axle_pose,
            self._rear_axle_to_center_dist_m,
        )
        geom = OrientedBox.from_new_pose(
            self._ego_box,
            center_pose,
        ).geometry
        need(
            hasattr(geom, "is_empty")
            and not geom.is_empty
            and geom.is_valid,
            "INVALID_EXACT_GEOMETRY",
        )
        return geom


class ExactDualStopFleetTransition(FrozenDualStopFleetTransition):
    """Frozen dual-stop transition with exact geometry only for hard A/B checks."""

    def __init__(
        self,
        vehicle_transitions: Mapping[str, DestinationStopTransition],
        route_geometry_caches: Mapping[str, object],
        *,
        exact_geometry_providers: Mapping[str, object],
        external_tokens: Tuple[str, ...],
        confirmed_dual_only: bool,
        internal_collision_sample_dt_s: float,
        internal_safety_margin_m: float,
    ):
        need(
            exact_geometry_providers is not None
            and set(exact_geometry_providers) == {"A", "B"},
            "BOTH_EXACT_GEOMETRY_PROVIDERS_REQUIRED",
        )
        need(
            all(
                callable(getattr(g, "geometry_at", None))
                for g in exact_geometry_providers.values()
            ),
            "EXACT_GEOMETRY_API",
        )
        super().__init__(
            vehicle_transitions,
            route_geometry_caches,
            external_tokens=external_tokens,
            confirmed_dual_only=confirmed_dual_only,
            internal_collision_sample_dt_s=internal_collision_sample_dt_s,
            internal_safety_margin_m=internal_safety_margin_m,
        )
        self._exact_geometry_providers = dict(exact_geometry_providers)

    def _geometry(self, positions: Mapping[str, float]):
        geometries = {}
        for token in ("A", "B"):
            geom = self._exact_geometry_providers[token].geometry_at(
                positions[token]
            )
            need(
                hasattr(geom, "is_empty")
                and not geom.is_empty
                and geom.is_valid,
                "INVALID_EXACT_GEOMETRY:" + token,
            )
            geometries[token] = geom

        result = evaluate_internal_fleet_collision(
            geometries,
            self.internal_safety_margin_m,
        )
        need(
            math.isfinite(result.minimum_internal_clearance_m)
            and result.minimum_internal_clearance_m >= 0,
            "NONFINITE_EXACT_PAIR_CLEARANCE",
        )
        return result
