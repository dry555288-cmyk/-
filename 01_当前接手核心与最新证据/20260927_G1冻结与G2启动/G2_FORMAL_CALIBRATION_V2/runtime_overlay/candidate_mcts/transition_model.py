from dataclasses import dataclass
from typing import Dict

from .action_space import ACTION_ACCEL, MCTSAction
from .state import MCTSState


@dataclass(frozen=True)
class TransitionConfig:
    dt: float = 0.5
    accel_max: float = 1.0
    decel_max: float = 3.0
    max_speed: float = 15.0
    collision_distance: float = 2.0
    eps: float = 1e-6
    goal_route_s: float = float("inf")

class TransitionModel:
    def __init__(
        self,
        config: TransitionConfig,
        action_to_accel: Dict[MCTSAction, float] = ACTION_ACCEL,
    ):
        self.cfg = config
        self.action_to_accel = action_to_accel

    def step(self, state: MCTSState, action: MCTSAction) -> MCTSState:
        dt = self.cfg.dt

        acceleration = self.action_to_accel[action]
        acceleration = max(
            -self.cfg.decel_max,
            min(self.cfg.accel_max, acceleration),
        )

        speed_0 = max(0.0, state.speed_mps)
        speed_1 = max(
            0.0,
            min(self.cfg.max_speed, speed_0 + acceleration * dt),
        )

        ego_distance = 0.5 * (speed_0 + speed_1) * dt
        route_s = state.route_s + ego_distance

        # Signed longitudinal velocity projected onto the ego route.
        # A negative value represents an oncoming vehicle and must reduce
        # the longitudinal gap instead of being clamped to zero.
        lead_speed = (
            speed_0 + state.lead_rel_speed_mps
        )
        lead_distance = (
            state.lead_distance_m
            + lead_speed * dt
            - ego_distance
        )

        collision = lead_distance <= self.cfg.collision_distance

        return MCTSState(
            time_s=state.time_s + dt,
            route_s=route_s,
            speed_mps=speed_1,
            accel_mps2=acceleration,
            lead_distance_m=max(0.0, lead_distance),
            lead_rel_speed_mps=lead_speed - speed_1,
            target_speed_mps=state.target_speed_mps,
            # The scalar transition model has no 2D geometry.
            minimum_clearance_m=float("inf"),
            prev_action=action,
            collision=collision,
            goal_reached=(
                state.goal_reached
                or route_s >= self.cfg.goal_route_s
            ),
        )

    def step_collision_only(
        self,
        state: MCTSState,
        action: MCTSAction,
    ) -> MCTSState:
        """
        Return the next state when only collision status is required.

        Scalar transitions have no expensive geometric clearance
        calculation, so their collision-only path is identical to the
        normal transition.
        """

        return self.step(state, action)
