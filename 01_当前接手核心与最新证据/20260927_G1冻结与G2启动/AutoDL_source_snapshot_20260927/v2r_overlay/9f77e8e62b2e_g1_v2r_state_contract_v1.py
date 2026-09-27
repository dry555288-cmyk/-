"""G1 V2R hard-safety state contract V1.

This is a versioned technical overlay. It does not modify the frozen FleetState
or frozen codecs. Drivable-area safety is kept distinct from V2V collision/
clearance semantics.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Mapping, Tuple

from candidate_mcts.action_space import MCTSAction
from candidate_mcts.dual_stop_motion_v1 import (
    DualOnlyState,
    VERSION,
    finite,
    need,
)
from candidate_mcts.fleet_state import FleetState

STATE_VERSION = "G1_V2R_HARD_SAFETY_STATE_V1"
CODEC = "G1_DUAL_STOP_HARD_SAFETY_STATE_CODEC_V1"


@dataclass(frozen=True)
class G1SafetyFleetStateV1(FleetState):
    """Fleet state extended only with V2R hard-safety outcome."""

    drivable_area_violation: bool = False
    drivable_violating_tokens: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        super().__post_init__()

        need(
            type(self.drivable_area_violation) is bool,
            "DRIVABLE_FLAG_TYPE",
        )
        need(
            type(self.drivable_violating_tokens) is tuple,
            "DRIVABLE_TOKENS_TUPLE",
        )

        tokens = self.drivable_violating_tokens

        need(
            all(
                type(token) is str
                and token in self.controlled_token_set
                for token in tokens
            ),
            "DRIVABLE_TOKEN_DOMAIN",
        )
        need(
            len(tokens) == len(set(tokens)),
            "DRIVABLE_TOKEN_DUPLICATE",
        )
        need(
            tokens == tuple(sorted(tokens)),
            "DRIVABLE_TOKENS_NOT_CANONICAL",
        )
        need(
            bool(tokens) == self.drivable_area_violation,
            "DRIVABLE_FLAG_TOKEN_CONSISTENCY",
        )

    @property
    def hard_safety_violation(self) -> bool:
        return bool(
            super().hard_safety_violation
            or self.drivable_area_violation
        )

    def transition_cache_key(self) -> Tuple:
        # Drivable violation can represent an intermediate-tick hard event,
        # not merely endpoint geometry, so it must not alias a safe state key.
        return super().transition_cache_key() + (
            (
                STATE_VERSION,
                self.drivable_area_violation,
                self.drivable_violating_tokens,
            ),
        )

    @classmethod
    def from_fleet_state(
        cls,
        state: FleetState,
        *,
        drivable_area_violation: bool = False,
        drivable_violating_tokens: Tuple[str, ...] = (),
    ) -> "G1SafetyFleetStateV1":
        need(
            isinstance(state, FleetState),
            "BASE_FLEET_STATE_REQUIRED",
        )
        return cls(
            vehicles=state.vehicles,
            internal_collision=state.internal_collision,
            minimum_internal_clearance_m=(
                state.minimum_internal_clearance_m
            ),
            conflicting_pairs=state.conflicting_pairs,
            internal_safety_violation=(
                state.internal_safety_violation
            ),
            safety_violating_pairs=(
                state.safety_violating_pairs
            ),
            drivable_area_violation=drivable_area_violation,
            drivable_violating_tokens=tuple(
                drivable_violating_tokens
            ),
        )


def pack_state(
    state: G1SafetyFleetStateV1,
    vehicle_transitions: Mapping[str, object],
) -> dict:
    """Versioned JSON-safe codec; frozen V1 codecs remain untouched."""

    need(
        type(state) is G1SafetyFleetStateV1,
        "G1_STATE_REQUIRED",
    )
    need(
        set(vehicle_transitions) == {"A", "B"},
        "EXACTLY_A_AND_B_REQUIRED",
    )

    cars = {}

    for token in ("A", "B"):
        vehicle = state.state_for(token)

        need(
            isinstance(vehicle, DualOnlyState),
            "DUAL_ONLY_STATE_REQUIRED",
        )

        cars[token] = {
            key: getattr(vehicle, key)
            for key in (
                "time_s",
                "route_s",
                "speed_mps",
                "accel_mps2",
                "target_speed_mps",
                "goal_reached",
                "collision",
                "parked_at_time_s",
            )
        }
        cars[token].update(
            prev_action=(
                None
                if vehicle.prev_action is None
                else int(vehicle.prev_action)
            ),
            external_lead={
                "mode": "NONE",
                "distance_m": None,
                "relative_speed_mps": None,
            },
            minimum_external_clearance_m=None,
            goal_window_m=list(
                vehicle_transitions[token].window
            ),
            acceleration_semantics="COMMANDED_NOT_MEASURED",
        )

    clearance = state.minimum_internal_clearance_m

    need(
        (
            math.isfinite(clearance)
            and clearance >= 0
        )
        or clearance == math.inf,
        "BAD_PACKED_CLEARANCE",
    )

    return {
        "schema": CODEC,
        "model_version": VERSION,
        "state_version": STATE_VERSION,
        "vehicles": cars,
        "internal_collision": state.internal_collision,
        "internal_safety_violation": (
            state.internal_safety_violation
        ),
        "minimum_internal_clearance_m": (
            None
            if clearance == math.inf
            else clearance
        ),
        "internal_clearance_status": (
            "UNMEASURED"
            if clearance == math.inf
            else "SAMPLED"
        ),
        "conflicting_pairs": [
            list(pair)
            for pair in state.conflicting_pairs
        ],
        "safety_violating_pairs": [
            list(pair)
            for pair in state.safety_violating_pairs
        ],
        "drivable_area_violation": (
            state.drivable_area_violation
        ),
        "drivable_violating_tokens": list(
            state.drivable_violating_tokens
        ),
    }


def unpack_state(
    payload: dict,
    vehicle_transitions: Mapping[str, object],
) -> G1SafetyFleetStateV1:
    need(
        isinstance(payload, dict)
        and payload.get("schema") == CODEC
        and payload.get("model_version") == VERSION
        and payload.get("state_version") == STATE_VERSION,
        "CODEC_VERSION",
    )

    expected_top = {
        "schema",
        "model_version",
        "state_version",
        "vehicles",
        "internal_collision",
        "internal_safety_violation",
        "minimum_internal_clearance_m",
        "internal_clearance_status",
        "conflicting_pairs",
        "safety_violating_pairs",
        "drivable_area_violation",
        "drivable_violating_tokens",
    }
    need(
        set(payload) == expected_top,
        "CODEC_TOPLEVEL_KEYS",
    )
    need(
        set(vehicle_transitions) == {"A", "B"},
        "EXACTLY_A_AND_B_REQUIRED",
    )
    need(
        set(payload.get("vehicles", {})) == {"A", "B"},
        "CODEC_TOKENS",
    )

    states = {}

    expected_vehicle = {
        "time_s",
        "route_s",
        "speed_mps",
        "accel_mps2",
        "target_speed_mps",
        "goal_reached",
        "collision",
        "parked_at_time_s",
        "prev_action",
        "external_lead",
        "minimum_external_clearance_m",
        "goal_window_m",
        "acceleration_semantics",
    }

    for token, row in payload["vehicles"].items():
        need(
            set(row) == expected_vehicle,
            "CODEC_VEHICLE_KEYS",
        )
        need(
            row["external_lead"] == {
                "mode": "NONE",
                "distance_m": None,
                "relative_speed_mps": None,
            },
            "CODEC_NO_EXTERNAL_SCOPE",
        )
        need(
            row["minimum_external_clearance_m"] is None,
            "CODEC_EXTERNAL_CLEARANCE",
        )
        need(
            row["goal_window_m"]
            == list(vehicle_transitions[token].window),
            "CODEC_TARGET_DRIFT",
        )
        need(
            row["acceleration_semantics"]
            == "COMMANDED_NOT_MEASURED",
            "CODEC_ACCELERATION_CONVENTION",
        )

        action = row["prev_action"]
        need(
            action is None
            or (
                type(action) is int
                and 0 <= action < 4
            ),
            "CODEC_ACTION_INDEX",
        )

        states[token] = DualOnlyState(
            **{
                key: row[key]
                for key in (
                    "time_s",
                    "route_s",
                    "speed_mps",
                    "accel_mps2",
                    "target_speed_mps",
                    "goal_reached",
                    "collision",
                    "parked_at_time_s",
                )
            },
            lead_distance_m=math.inf,
            lead_rel_speed_mps=0.0,
            minimum_clearance_m=math.inf,
            prev_action=(
                None
                if action is None
                else MCTSAction(action)
            ),
        )

    clearance = payload["minimum_internal_clearance_m"]

    if clearance is None:
        need(
            payload["internal_clearance_status"]
            == "UNMEASURED",
            "CODEC_CLEARANCE_SCOPE",
        )
        clearance = math.inf
    else:
        need(
            payload["internal_clearance_status"]
            == "SAMPLED"
            and finite(clearance, "CLEARANCE") >= 0,
            "CODEC_CLEARANCE",
        )

    for name in (
        "internal_collision",
        "internal_safety_violation",
        "drivable_area_violation",
    ):
        need(
            type(payload[name]) is bool,
            "CODEC_BOOLEAN:" + name,
        )

    def pairs(name: str):
        value = payload[name]
        need(
            isinstance(value, list)
            and all(
                item == ["A", "B"]
                for item in value
            )
            and len(value) <= 1,
            "CODEC_PAIR:" + name,
        )
        return tuple(
            tuple(item)
            for item in value
        )

    road_tokens = payload["drivable_violating_tokens"]
    need(
        type(road_tokens) is list
        and all(
            type(token) is str
            and token in ("A", "B")
            for token in road_tokens
        ),
        "CODEC_DRIVABLE_TOKENS",
    )

    base = G1SafetyFleetStateV1.from_states(
        states.items()
    )

    result = G1SafetyFleetStateV1(
        vehicles=base.vehicles,
        internal_collision=payload[
            "internal_collision"
        ],
        minimum_internal_clearance_m=clearance,
        conflicting_pairs=pairs(
            "conflicting_pairs"
        ),
        internal_safety_violation=payload[
            "internal_safety_violation"
        ],
        safety_violating_pairs=pairs(
            "safety_violating_pairs"
        ),
        drivable_area_violation=payload[
            "drivable_area_violation"
        ],
        drivable_violating_tokens=tuple(
            road_tokens
        ),
    )

    need(
        pack_state(
            result,
            vehicle_transitions,
        )
        == payload,
        "STATE_ROUNDTRIP_NOT_EXACT",
    )

    return result
