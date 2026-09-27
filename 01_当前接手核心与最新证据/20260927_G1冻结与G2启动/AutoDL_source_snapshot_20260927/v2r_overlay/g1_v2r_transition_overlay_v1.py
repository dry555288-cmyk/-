"""G1 V2R exact-tick transition overlay V1.

Technical overlay only:
- exact route-pose footprints are generated once per 0.1 s safety tick;
- the same exact footprints feed V2V and V2R checks;
- V2R uses drivable_domain.covers(footprint), so boundary contact is allowed;
- V2R violations are aggregated into G1SafetyFleetStateV1;
- frozen guide/phase 1 m caches are preserved but are not used for hard safety.
"""
from __future__ import annotations

import math
from dataclasses import replace
from typing import Mapping, Tuple

from shapely.prepared import prep

from candidate_mcts.dual_stop_adapter_v1 import (
    need,
    action_id,
)
from candidate_mcts.dual_stop_motion_v1 import (
    DestinationStopTransition,
)
from candidate_mcts.fleet_collision import (
    evaluate_internal_fleet_collision,
)
from candidate_mcts.fleet_state import FleetState
from candidate_mcts.joint_action import JointAction

from g1_exact_geometry_overlay_v1 import (
    ExactDualStopFleetTransition,
)
from g1_v2r_state_contract_v1 import (
    G1SafetyFleetStateV1,
    STATE_VERSION,
    pack_state,
    unpack_state,
)

VERSION = "G1_V2R_EXACT_TICK_TRANSITION_OVERLAY_V1"


class G1V2RExactDualStopFleetTransition(
    ExactDualStopFleetTransition
):
    """Exact V2V + V2R hard safety on the frozen 0.1 s time lattice."""

    def __init__(
        self,
        vehicle_transitions: Mapping[
            str,
            DestinationStopTransition,
        ],
        route_geometry_caches: Mapping[str, object],
        *,
        exact_geometry_providers: Mapping[str, object],
        drivable_domain,
        external_tokens: Tuple[str, ...],
        confirmed_dual_only: bool,
        internal_collision_sample_dt_s: float,
        internal_safety_margin_m: float,
    ):
        need(
            drivable_domain is not None
            and hasattr(drivable_domain, "covers")
            and hasattr(drivable_domain, "is_valid")
            and hasattr(drivable_domain, "is_empty"),
            "DRIVABLE_DOMAIN_API",
        )
        need(
            bool(drivable_domain.is_valid)
            and not bool(drivable_domain.is_empty),
            "INVALID_DRIVABLE_DOMAIN",
        )

        super().__init__(
            vehicle_transitions,
            route_geometry_caches,
            exact_geometry_providers=(
                exact_geometry_providers
            ),
            external_tokens=external_tokens,
            confirmed_dual_only=confirmed_dual_only,
            internal_collision_sample_dt_s=(
                internal_collision_sample_dt_s
            ),
            internal_safety_margin_m=(
                internal_safety_margin_m
            ),
        )

        self._drivable_domain = drivable_domain
        self._prepared_drivable_domain = prep(
            drivable_domain
        )

    def validate_fleet(self, state: FleetState) -> None:
        need(
            isinstance(state, G1SafetyFleetStateV1),
            "G1_V2R_STATE_REQUIRED",
        )
        super().validate_fleet(state)

    def _domain_covers(self, geometry) -> bool:
        prepared_covers = getattr(
            self._prepared_drivable_domain,
            "covers",
            None,
        )
        if callable(prepared_covers):
            return bool(prepared_covers(geometry))

        return bool(
            self._drivable_domain.covers(
                geometry
            )
        )

    def _evaluate_exact_tick(
        self,
        positions: Mapping[str, float],
    ):
        geometries = {}

        for token in ("A", "B"):
            geometry = (
                self._exact_geometry_providers[
                    token
                ].geometry_at(
                    positions[token]
                )
            )
            need(
                hasattr(geometry, "is_empty")
                and not geometry.is_empty
                and geometry.is_valid,
                "INVALID_EXACT_GEOMETRY:"
                + token,
            )
            geometries[token] = geometry

        v2v = evaluate_internal_fleet_collision(
            geometries,
            self.internal_safety_margin_m,
        )

        need(
            math.isfinite(
                v2v.minimum_internal_clearance_m
            )
            and (
                v2v.minimum_internal_clearance_m
                >= 0
            ),
            "NONFINITE_EXACT_PAIR_CLEARANCE",
        )

        violating_tokens = tuple(
            token
            for token in ("A", "B")
            if not self._domain_covers(
                geometries[token]
            )
        )

        return v2v, violating_tokens

    def bind_initial_geometry(
        self,
        state: FleetState,
    ) -> G1SafetyFleetStateV1:
        self.validate_fleet(state)

        need(
            not state.hard_safety_violation,
            "INPUT_HARD_FLAG_CANNOT_BE_RESET",
        )

        positions = {
            token: state.state_for(token).route_s
            for token in ("A", "B")
        }

        v2v, road_tokens = (
            self._evaluate_exact_tick(
                positions
            )
        )

        base = replace(
            state,
            internal_collision=(
                v2v.internal_collision
            ),
            minimum_internal_clearance_m=(
                v2v.minimum_internal_clearance_m
            ),
            conflicting_pairs=(
                v2v.conflicting_pairs
            ),
            internal_safety_violation=(
                v2v.internal_safety_violation
            ),
            safety_violating_pairs=(
                v2v.safety_violating_pairs
            ),
            drivable_area_violation=bool(
                road_tokens
            ),
            drivable_violating_tokens=tuple(
                road_tokens
            ),
        )

        self.validate_fleet(base)
        return base

    def step_with_diagnostics(
        self,
        state: FleetState,
        joint_action: JointAction,
    ):
        self.validate_fleet(state)

        need(
            not state.hard_safety_violation,
            "DO_NOT_ADVANCE_HARD_TERMINAL",
        )
        need(
            isinstance(
                joint_action,
                JointAction,
            )
            and set(
                joint_action.vehicle_tokens
            )
            == {"A", "B"},
            "ACTION_TOKENS",
        )

        nxt = {}
        profiles = {}
        detail = {}

        for token in ("A", "B"):
            model = self._vehicle_transitions[
                token
            ]
            action = joint_action.action_for(
                token
            )
            before = state.state_for(token)

            nxt[token], detail[token] = (
                model.step_with_diagnostics(
                    before,
                    action,
                )
            )
            profiles[token] = model.profile(
                before,
                action,
            )

        dt = self._vehicle_transitions[
            "A"
        ].cfg.dt
        n = max(
            1,
            math.ceil(
                dt
                / self.internal_collision_sample_dt_s
            ),
        )

        minimum = math.inf
        conflicts = set()
        unsafe_pairs = set()
        road_unsafe_tokens = set()
        samples = []

        for i in range(n + 1):
            offset = dt * i / n

            positions = {
                token: math.fsum(
                    (
                        state.state_for(
                            token
                        ).route_s,
                        profiles[token].at(
                            offset
                        ).distance_m,
                    )
                )
                for token in ("A", "B")
            }

            if i == n:
                need(
                    all(
                        positions[token]
                        == nxt[token].route_s
                        for token
                        in ("A", "B")
                    ),
                    "SAMPLE_ENDPOINT_MISMATCH",
                )

            v2v, road_tokens = (
                self._evaluate_exact_tick(
                    positions
                )
            )

            minimum = min(
                minimum,
                v2v.minimum_internal_clearance_m,
            )
            conflicts.update(
                v2v.conflicting_pairs
            )
            unsafe_pairs.update(
                v2v.safety_violating_pairs
            )
            road_unsafe_tokens.update(
                road_tokens
            )

            samples.append(
                {
                    "offset_s": offset,
                    "route_s": positions,
                    "minimum_clearance_m": (
                        v2v.minimum_internal_clearance_m
                    ),
                    "collision": (
                        v2v.internal_collision
                    ),
                    "v2v_safety_violation": (
                        v2v.internal_safety_violation
                    ),
                    "drivable_area_violation": (
                        bool(road_tokens)
                    ),
                    "drivable_violating_tokens": (
                        list(road_tokens)
                    ),
                }
            )

        base = FleetState.from_states(
            nxt.items()
        )
        base = replace(
            base,
            internal_collision=bool(
                conflicts
            ),
            minimum_internal_clearance_m=(
                minimum
            ),
            conflicting_pairs=tuple(
                sorted(conflicts)
            ),
            internal_safety_violation=bool(
                unsafe_pairs
            ),
            safety_violating_pairs=tuple(
                sorted(unsafe_pairs)
            ),
        )

        result = (
            G1SafetyFleetStateV1
            .from_fleet_state(
                base,
                drivable_area_violation=bool(
                    road_unsafe_tokens
                ),
                drivable_violating_tokens=(
                    tuple(
                        sorted(
                            road_unsafe_tokens
                        )
                    )
                ),
            )
        )

        self.validate_fleet(result)

        diagnostics = {
            "model_version": VERSION,
            "state_version": STATE_VERSION,
            "vehicles": detail,
            "collision_samples": samples,
            "geometry_scope": (
                "SAMPLED_0P1S_AB_EXACT_ROUTE_POSE_"
                "V2V_AND_V2R_NOT_CONTINUOUS_PROOF"
            ),
            "road_boundary_status": (
                "EVALUATED_EXACT_FOOTPRINT_COVERS_"
                "CALLER_BOUND_DRIVABLE_DOMAIN"
            ),
            "drivable_area_violation": (
                result.drivable_area_violation
            ),
            "drivable_violating_tokens": list(
                result.drivable_violating_tokens
            ),
            "joint_action_id": action_id(
                joint_action
            ),
        }

        return result, diagnostics

    def pack(
        self,
        state: FleetState,
    ) -> dict:
        self.validate_fleet(state)
        return pack_state(
            state,
            self._vehicle_transitions,
        )

    def unpack(
        self,
        payload: dict,
    ) -> G1SafetyFleetStateV1:
        state = unpack_state(
            payload,
            self._vehicle_transitions,
        )
        self.validate_fleet(state)
        return state
