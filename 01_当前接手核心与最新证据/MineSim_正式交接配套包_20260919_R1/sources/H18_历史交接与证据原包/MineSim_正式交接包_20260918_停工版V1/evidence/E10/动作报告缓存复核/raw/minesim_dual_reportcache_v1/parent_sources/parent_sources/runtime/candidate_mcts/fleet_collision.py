from dataclasses import dataclass
import math
from itertools import combinations
from typing import Mapping, Tuple

from .state import MCTSState


@dataclass(frozen=True)
class FleetCollisionResult:
    internal_collision: bool
    minimum_internal_clearance_m: float
    conflicting_pairs: Tuple[Tuple[str, str], ...]
    internal_safety_violation: bool = False
    safety_violating_pairs: Tuple[Tuple[str, str], ...] = ()


def evaluate_internal_fleet_collision(
    vehicle_geometries: Mapping[str, object],
    safety_margin_m: float = 0.0,
) -> FleetCollisionResult:
    if safety_margin_m < 0.0:
        raise ValueError("safety_margin_m cannot be negative.")
    tokens = tuple(sorted(vehicle_geometries))

    if len(tokens) < 2:
        return FleetCollisionResult(
            internal_collision=False,
            minimum_internal_clearance_m=float("inf"),
            conflicting_pairs=(),
        )

    minimum_clearance = float("inf")
    conflicts = []
    safety_violations = []

    for token_a, token_b in combinations(tokens, 2):
        geometry_a = vehicle_geometries[token_a]
        geometry_b = vehicle_geometries[token_b]

        clearance = float(
            geometry_a.distance(geometry_b)
        )

        minimum_clearance = min(
            minimum_clearance,
            clearance,
        )

        pair = (token_a, token_b)

        if geometry_a.intersects(geometry_b):
            conflicts.append(pair)

        if clearance <= safety_margin_m:
            safety_violations.append(pair)

    return FleetCollisionResult(
        internal_collision=bool(conflicts),
        minimum_internal_clearance_m=minimum_clearance,
        conflicting_pairs=tuple(conflicts),
        internal_safety_violation=bool(safety_violations),
        safety_violating_pairs=tuple(safety_violations),
    )


def evaluate_internal_fleet_motion(
    previous_states: Mapping[str, MCTSState],
    next_states: Mapping[str, MCTSState],
    route_geometry_caches: Mapping[str, object],
    sample_dt_s: float = 0.1,
    safety_margin_m: float = 0.0,
) -> FleetCollisionResult:
    if sample_dt_s <= 0.0:
        raise ValueError("sample_dt_s must be positive.")

    if safety_margin_m < 0.0:
        raise ValueError("safety_margin_m cannot be negative.")

    tokens = tuple(sorted(previous_states))

    if set(tokens) != set(next_states):
        raise ValueError(
            "Previous and next state tokens must match."
        )

    if set(tokens) != set(route_geometry_caches):
        raise ValueError(
            "State and geometry-cache tokens must match."
        )

    if len(tokens) < 2:
        return FleetCollisionResult(
            False,
            float("inf"),
            (),
        )

    durations = [
        next_states[t].time_s
        - previous_states[t].time_s
        for t in tokens
    ]

    if any(dt < 0.0 for dt in durations):
        raise ValueError(
            "Fleet transition duration cannot be negative."
        )

    if max(durations) - min(durations) > 1e-9:
        raise ValueError(
            "Fleet transition durations must match."
        )

    sample_count = max(
        1,
        math.ceil(durations[0] / sample_dt_s),
    )

    minimum_clearance = float("inf")
    conflicts = set()
    safety_violations = set()

    for index in range(sample_count + 1):
        fraction = index / sample_count

        geometries = {}
        for token in tokens:
            before = previous_states[token]
            after = next_states[token]

            route_s = before.route_s + (
                after.route_s - before.route_s
            ) * fraction

            geometries[token] = (
                route_geometry_caches[token]
                .geometry_at(route_s)
            )

        result = evaluate_internal_fleet_collision(
            geometries,
            safety_margin_m=safety_margin_m,
        )

        minimum_clearance = min(
            minimum_clearance,
            result.minimum_internal_clearance_m,
        )
        conflicts.update(result.conflicting_pairs)
        safety_violations.update(
            result.safety_violating_pairs
        )

    return FleetCollisionResult(
        internal_collision=bool(conflicts),
        minimum_internal_clearance_m=minimum_clearance,
        conflicting_pairs=tuple(sorted(conflicts)),
        internal_safety_violation=bool(safety_violations),
        safety_violating_pairs=tuple(
            sorted(safety_violations)
        ),
    )
