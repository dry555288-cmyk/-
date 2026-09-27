from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Iterable, Tuple

from .action_space import MCTSAction, NUM_ACTIONS


def _validate_tokens(
    vehicle_tokens: Iterable[str],
) -> Tuple[str, ...]:
    tokens = tuple(vehicle_tokens)

    if not tokens:
        raise ValueError(
            "At least one controlled vehicle is required."
        )

    for token in tokens:
        if not isinstance(token, str):
            raise TypeError(
                "Vehicle token must be str."
            )
        if not token.strip():
            raise ValueError(
                "Vehicle token must not be empty."
            )

    if len(tokens) != len(set(tokens)):
        raise ValueError(
            f"Vehicle tokens must be unique: {tokens!r}"
        )

    return tokens


@dataclass(frozen=True)
class JointVehicleAction:
    token: str
    action: MCTSAction

    def __post_init__(self) -> None:
        if not isinstance(self.token, str):
            raise TypeError("token must be str.")

        if not self.token.strip():
            raise ValueError("token must not be empty.")

        if not isinstance(self.action, MCTSAction):
            raise TypeError(
                "action must be MCTSAction."
            )


@dataclass(frozen=True)
class JointAction:
    assignments: Tuple[JointVehicleAction, ...]

    def __post_init__(self) -> None:
        assignments = tuple(self.assignments)

        object.__setattr__(
            self,
            "assignments",
            assignments,
        )

        if not assignments:
            raise ValueError(
                "JointAction cannot be empty."
            )

        tokens = tuple(
            item.token for item in assignments
        )

        if len(tokens) != len(set(tokens)):
            raise ValueError(
                f"Duplicate vehicle tokens: {tokens!r}"
            )

    @classmethod
    def from_pairs(
        cls,
        pairs: Iterable[Tuple[str, MCTSAction]],
    ) -> "JointAction":
        return cls(
            tuple(
                JointVehicleAction(token, action)
                for token, action in pairs
            )
        )

    @property
    def vehicle_tokens(self) -> Tuple[str, ...]:
        return tuple(
            item.token
            for item in self.assignments
        )

    @property
    def actions(self) -> Tuple[MCTSAction, ...]:
        return tuple(
            item.action
            for item in self.assignments
        )

    def action_for(
        self,
        token: str,
    ) -> MCTSAction:
        for item in self.assignments:
            if item.token == token:
                return item.action

        raise KeyError(
            f"Unknown controlled vehicle: {token!r}"
        )


def joint_action_count(vehicle_count: int) -> int:
    if not isinstance(vehicle_count, int):
        raise TypeError(
            "vehicle_count must be int."
        )

    if vehicle_count <= 0:
        raise ValueError(
            "vehicle_count must be positive."
        )

    return NUM_ACTIONS ** vehicle_count


def enumerate_joint_actions(
    vehicle_tokens: Iterable[str],
) -> Tuple[JointAction, ...]:
    tokens = _validate_tokens(vehicle_tokens)
    actions = tuple(MCTSAction)

    return tuple(
        JointAction.from_pairs(
            zip(tokens, action_tuple)
        )
        for action_tuple in product(
            actions,
            repeat=len(tokens),
        )
    )
