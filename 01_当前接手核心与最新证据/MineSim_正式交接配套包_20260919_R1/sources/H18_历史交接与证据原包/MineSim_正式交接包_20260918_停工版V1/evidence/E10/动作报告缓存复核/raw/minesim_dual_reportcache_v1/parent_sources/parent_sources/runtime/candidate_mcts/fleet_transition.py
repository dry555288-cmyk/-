from __future__ import annotations

from dataclasses import replace
from typing import Mapping, Optional

from .action_space import MCTSAction
from .fleet_collision import evaluate_internal_fleet_motion
from .fleet_state import FleetState, FleetVehicleState
from .joint_action import JointAction
from .transition_model import TransitionModel


class FleetTransitionModel:
    """
    Synchronously advance all controlled vehicles.

    Every vehicle transition is computed from the same input
    FleetState. No updated vehicle state is visible to another
    vehicle during the same fleet transition.
    """

    def __init__(
        self,
        vehicle_transitions: Mapping[str, TransitionModel],
        route_geometry_caches: Optional[Mapping[str, object]] = None,
        internal_collision_sample_dt_s: float = 0.1,
        internal_safety_margin_m: float = 0.0,
    ):
        self._vehicle_transitions = dict(
            vehicle_transitions
        )

        self._route_geometry_caches = (
            None
            if route_geometry_caches is None
            else dict(route_geometry_caches)
        )

        if internal_collision_sample_dt_s <= 0.0:
            raise ValueError(
                "internal_collision_sample_dt_s must be positive."
            )

        self.internal_collision_sample_dt_s = float(
            internal_collision_sample_dt_s
        )

        if internal_safety_margin_m < 0.0:
            raise ValueError(
                "internal_safety_margin_m cannot be negative."
            )

        self.internal_safety_margin_m = float(
            internal_safety_margin_m
        )

        if not self._vehicle_transitions:
            raise ValueError(
                "At least one vehicle transition is required."
            )

        if self._route_geometry_caches is not None:
            if set(self._route_geometry_caches) != set(
                self._vehicle_transitions
            ):
                raise ValueError(
                    "Geometry-cache tokens must match "
                    "transition-model tokens."
                )

    def step(
        self,
        fleet_state: FleetState,
        joint_action: JointAction,
    ) -> FleetState:
        state_tokens = set(
            fleet_state.controlled_tokens
        )

        action_tokens = set(
            joint_action.vehicle_tokens
        )

        transition_tokens = set(
            self._vehicle_transitions
        )

        if state_tokens != action_tokens:
            raise ValueError(
                "FleetState and JointAction tokens must match."
            )

        if state_tokens != transition_tokens:
            raise ValueError(
                "FleetState and transition-model tokens must match."
            )

        next_vehicles = []

        for vehicle in fleet_state.vehicles:
            token = vehicle.token

            if vehicle.state.goal_reached:
                transition = self._vehicle_transitions[token]
                held_state = replace(
                    vehicle.state,
                    speed_mps=0.0,
                    accel_mps2=0.0,
                )
                next_state = transition.step(
                    held_state,
                    MCTSAction.KEEP,
                )
            else:
                next_state = (
                    self._vehicle_transitions[token].step(
                        vehicle.state,
                        joint_action.action_for(token),
                    )
                )

            next_vehicles.append(
                FleetVehicleState(
                    token=token,
                    state=next_state,
                )
            )

        if self._route_geometry_caches is None:
            return FleetState(
                vehicles=tuple(next_vehicles),
            )

        previous_states = {
            vehicle.token: vehicle.state
            for vehicle in fleet_state.vehicles
        }

        next_states = {
            vehicle.token: vehicle.state
            for vehicle in next_vehicles
        }

        collision_result = evaluate_internal_fleet_motion(
            previous_states,
            next_states,
            self._route_geometry_caches,
            sample_dt_s=self.internal_collision_sample_dt_s,
            safety_margin_m=self.internal_safety_margin_m,
        )

        return FleetState(
            vehicles=tuple(next_vehicles),
            internal_collision=(
                collision_result.internal_collision
            ),
            minimum_internal_clearance_m=(
                collision_result
                .minimum_internal_clearance_m
            ),
            conflicting_pairs=(
                collision_result.conflicting_pairs
            ),
            internal_safety_violation=(
                collision_result.internal_safety_violation
            ),
            safety_violating_pairs=(
                collision_result.safety_violating_pairs
            ),
        )
