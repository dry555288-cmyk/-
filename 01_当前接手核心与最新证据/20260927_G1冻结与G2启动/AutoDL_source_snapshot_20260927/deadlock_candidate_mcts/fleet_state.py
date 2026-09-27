from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet, Iterable, Tuple

from .state import MCTSState


def _validate_token(token: str, label: str) -> None:
    if not isinstance(token, str):
        raise TypeError(f"{label} token must be str, got {type(token)!r}.")
    if not token.strip():
        raise ValueError(f"{label} token must not be empty.")


@dataclass(frozen=True)
class FleetVehicleState:
    """
    Search state of one controlled vehicle.

    The Fleet-level token is the authoritative vehicle identity.
    MCTSState deliberately remains the existing single-vehicle
    search state and is not modified for multi-vehicle use.
    """

    token: str
    state: MCTSState

    def __post_init__(self) -> None:
        _validate_token(self.token, "Controlled vehicle")

        if not isinstance(self.state, MCTSState):
            raise TypeError(
                "state must be an MCTSState, "
                f"got {type(self.state)!r}."
            )


@dataclass(frozen=True)
class FleetState:
    """
    Immutable multi-vehicle MCTS search state.

    Vehicle tuple order is structural only. It must never be
    interpreted as right-of-way or planning priority.
    """

    vehicles: Tuple[FleetVehicleState, ...]
    internal_collision: bool = False
    minimum_internal_clearance_m: float = float("inf")
    conflicting_pairs: Tuple[Tuple[str, str], ...] = ()
    internal_safety_violation: bool = False
    safety_violating_pairs: Tuple[Tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        vehicles = tuple(
            sorted(
                self.vehicles,
                key=lambda vehicle: vehicle.token,
            )
        )
        object.__setattr__(self, "vehicles", vehicles)

        if not vehicles:
            raise ValueError(
                "FleetState requires at least one controlled vehicle."
            )

        if not all(
            isinstance(vehicle, FleetVehicleState)
            for vehicle in vehicles
        ):
            raise TypeError(
                "All FleetState entries must be FleetVehicleState."
            )

        tokens = tuple(
            vehicle.token
            for vehicle in vehicles
        )

        if len(tokens) != len(set(tokens)):
            raise ValueError(
                "Controlled vehicle tokens must be unique: "
                f"{tokens!r}"
            )

    @classmethod
    def from_states(
        cls,
        states: Iterable[Tuple[str, MCTSState]],
    ) -> "FleetState":
        """
        Build a fleet from an iterable of (token, MCTSState).

        An iterable of pairs is used instead of a dict so duplicate
        tokens can be detected instead of silently overwritten.
        """

        return cls(
            tuple(
                FleetVehicleState(
                    token=token,
                    state=state,
                )
                for token, state in states
            )
        )

    @property
    def vehicle_count(self) -> int:
        return len(self.vehicles)

    @property
    def controlled_tokens(self) -> Tuple[str, ...]:
        return tuple(
            vehicle.token
            for vehicle in self.vehicles
        )

    @property
    def controlled_token_set(self) -> FrozenSet[str]:
        return frozenset(self.controlled_tokens)

    def state_for(self, token: str) -> MCTSState:
        _validate_token(token, "Lookup")

        for vehicle in self.vehicles:
            if vehicle.token == token:
                return vehicle.state

        raise KeyError(
            f"Controlled vehicle token not found: {token!r}"
        )

    @property
    def any_collision(self) -> bool:
        return self.internal_collision or any(
            vehicle.state.collision
            for vehicle in self.vehicles
        )

    @property
    def hard_safety_violation(self) -> bool:
        return (
            self.any_collision
            or self.internal_safety_violation
        )

    @property
    def all_goals_reached(self) -> bool:
        return all(
            vehicle.state.goal_reached
            for vehicle in self.vehicles
        )

    @property
    def minimum_clearance_m(self) -> float:
        return min(
            self.minimum_internal_clearance_m,
            min(
                vehicle.state.minimum_clearance_m
                for vehicle in self.vehicles
            ),
        )

    def transition_cache_key(self) -> Tuple:
        """
        Fleet equivalent of MCTSState.transition_cache_key().

        The token is part of the key because each controlled vehicle
        can later have its own route geometry and transition context.
        """

        return tuple(
            (
                vehicle.token,
                vehicle.state.transition_cache_key(),
            )
            for vehicle in self.vehicles
        )


def validate_controlled_external_partition(
    fleet_state: FleetState,
    external_tokens: Iterable[str],
) -> FrozenSet[str]:
    """
    Enforce that a controlled vehicle can never simultaneously be
    treated as an externally predicted obstacle.
    """

    tokens = tuple(external_tokens)

    for token in tokens:
        _validate_token(token, "External vehicle")

    if len(tokens) != len(set(tokens)):
        raise ValueError(
            "External vehicle tokens must be unique: "
            f"{tokens!r}"
        )

    external_set = frozenset(tokens)

    overlap = (
        fleet_state.controlled_token_set
        & external_set
    )

    if overlap:
        raise ValueError(
            "Controlled/external token overlap is forbidden: "
            f"{sorted(overlap)!r}"
        )

    return external_set
