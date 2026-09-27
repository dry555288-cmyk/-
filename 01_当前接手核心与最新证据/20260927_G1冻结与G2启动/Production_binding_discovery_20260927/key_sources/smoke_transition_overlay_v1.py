#!/usr/bin/env python3
import math

from shapely.geometry import box
from shapely.ops import unary_union

from candidate_mcts.action_space import (
    ACTION_ACCEL,
    MCTSAction,
)
from candidate_mcts.dual_stop_motion_v1 import (
    DestinationStopTransition,
    DualOnlyState,
)
from candidate_mcts.fleet_state import FleetState
from candidate_mcts.joint_action import (
    JointAction,
)
from candidate_mcts.transition_model import (
    TransitionConfig,
)

from g1_v2r_state_contract_v1 import (
    G1SafetyFleetStateV1,
)
from g1_v2r_transition_overlay_v1 import (
    G1V2RExactDualStopFleetTransition,
    VERSION,
)


class CountingRouteProvider:
    def __init__(self, y):
        self.y = float(y)
        self.calls = []

    def geometry_at(self, route_s):
        s = float(route_s)
        self.calls.append(s)
        return box(
            s,
            self.y,
            s + 1.0,
            self.y + 1.0,
        )


class DummyGuideCache:
    def __init__(self, marker):
        self.marker = marker

    def geometry_at(self, _route_s):
        # Deliberately unrelated to hard safety.
        if self.marker == "A":
            return box(
                100.0,
                100.0,
                101.0,
                101.0,
            )
        return box(
            200.0,
            200.0,
            201.0,
            201.0,
        )


def make_vehicle():
    return DualOnlyState(
        time_s=0.0,
        route_s=0.0,
        speed_mps=5.0,
        accel_mps2=0.0,
        lead_distance_m=math.inf,
        lead_rel_speed_mps=0.0,
        target_speed_mps=10.5,
        minimum_clearance_m=math.inf,
        prev_action=None,
        collision=False,
        goal_reached=False,
        parked_at_time_s=None,
    )


models = {
    token: DestinationStopTransition(
        TransitionConfig(
            dt=0.5,
            accel_max=1.0,
            decel_max=3.0,
            max_speed=15.0,
            goal_route_s=20.0,
        )
    )
    for token in ("A", "B")
}

providers = {
    "A": CountingRouteProvider(0.0),
    "B": CountingRouteProvider(10.0),
}
caches = {
    "A": DummyGuideCache("A"),
    "B": DummyGuideCache("B"),
}

# A stays within its long corridor.
# B is covered at route_s=0 only; from route_s=0.5 onward,
# its exact footprint extends beyond the short B domain.
drivable = unary_union(
    (
        box(-1.0, -1.0, 30.0, 2.0),
        box(-1.0, 9.0, 1.1, 12.0),
    )
)

transition = (
    G1V2RExactDualStopFleetTransition(
        models,
        caches,
        exact_geometry_providers=providers,
        drivable_domain=drivable,
        external_tokens=(),
        confirmed_dual_only=True,
        internal_collision_sample_dt_s=0.1,
        internal_safety_margin_m=0.0,
    )
)

initial = G1SafetyFleetStateV1.from_states(
    (
        ("A", make_vehicle()),
        ("B", make_vehicle()),
    )
)

bound = transition.bind_initial_geometry(
    initial
)

assert not bound.hard_safety_violation
assert not bound.drivable_area_violation
assert bound.drivable_violating_tokens == ()

# bind_initial_geometry adds one exact-provider call.
for token in ("A", "B"):
    assert providers[token].calls == [0.0]

# Reset counters so the step itself must produce exactly six calls.
for token in ("A", "B"):
    providers[token].calls.clear()

keep = next(
    action
    for action in MCTSAction
    if float(ACTION_ACCEL[action]) == 0.0
)

joint = JointAction.from_pairs(
    (
        ("A", keep),
        ("B", keep),
    )
)

result, diag = (
    transition.step_with_diagnostics(
        bound,
        joint,
    )
)

assert type(result) is G1SafetyFleetStateV1
assert result.drivable_area_violation
assert result.drivable_violating_tokens == ("B",)
assert result.hard_safety_violation
assert not result.internal_collision
assert not result.internal_safety_violation

expected_route_s = [
    0.0,
    0.5,
    1.0,
    1.5,
    2.0,
    2.5,
]

for token in ("A", "B"):
    assert len(providers[token].calls) == 6
    for actual, expected in zip(
        providers[token].calls,
        expected_route_s,
    ):
        assert abs(actual - expected) < 1e-12

samples = diag["collision_samples"]
assert len(samples) == 6

assert not samples[0]["drivable_area_violation"]
assert samples[0]["drivable_violating_tokens"] == []

for sample in samples[1:]:
    assert sample["drivable_area_violation"]
    assert sample["drivable_violating_tokens"] == ["B"]

assert diag["drivable_area_violation"]
assert diag["drivable_violating_tokens"] == ["B"]
assert (
    diag["road_boundary_status"]
    == "EVALUATED_EXACT_FOOTPRINT_COVERS_"
       "CALLER_BOUND_DRIVABLE_DOMAIN"
)

# Once V2R hard safety is aggregated, no further joint action is admitted.
assert transition.active_joint_actions(
    result
) == []

# New transition codec must preserve V2R terminal state exactly.
payload = transition.pack(result)
roundtrip = transition.unpack(payload)

assert roundtrip == result
assert roundtrip.hard_safety_violation
assert roundtrip.drivable_violating_tokens == ("B",)

# Guide caches remain present and unchanged.
assert transition._route_geometry_caches["A"] is caches["A"]
assert transition._route_geometry_caches["B"] is caches["B"]

print("TRANSITION_VERSION =", VERSION)
print("INITIAL_V2R_SAFE = yes")
print(
    "SAMPLE_OFFSETS_S =",
    [sample["offset_s"] for sample in samples],
)
print(
    "A_EXACT_PROVIDER_CALLS =",
    providers["A"].calls,
)
print(
    "B_EXACT_PROVIDER_CALLS =",
    providers["B"].calls,
)
print("V2V_COLLISION = False")
print("V2R_FINAL_VIOLATION = True")
print("V2R_FINAL_TOKENS = ('B',)")
print("V2R_FIRST_VIOLATION_OFFSET_S = 0.1")
print("ACTIVE_ACTIONS_AFTER_V2R_TERMINAL = 0")
print("TRANSITION_CODEC_ROUNDTRIP = PASS")
print("GUIDE_CACHE_PRESERVED = PASS")
print("EXACT_FOOTPRINT_REUSED_FOR_V2V_AND_V2R = yes")
print("PASS:G1_V2R_TRANSITION_OVERLAY_UNIT_V1")
