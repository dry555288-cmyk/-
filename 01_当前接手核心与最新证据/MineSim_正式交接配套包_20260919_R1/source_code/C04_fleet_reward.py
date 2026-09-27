from __future__ import annotations

import math
from typing import Mapping

from .fleet_state import FleetState
from .reward import RewardModel


class FleetRewardModel:
    def __init__(
        self,
        vehicle_rewards: Mapping[str, RewardModel],
        internal_clearance_safe_m: float = 3.0,
        w_internal_clearance: float = 0.0,
    ):
        self._vehicle_rewards = dict(vehicle_rewards)

        if not self._vehicle_rewards:
            raise ValueError(
                "At least one vehicle reward model is required."
            )

        self.internal_clearance_safe_m = float(
            internal_clearance_safe_m
        )
        self.w_internal_clearance = float(
            w_internal_clearance
        )

        if self.internal_clearance_safe_m <= 0.0:
            raise ValueError(
                "internal_clearance_safe_m must be positive."
            )

        if self.w_internal_clearance < 0.0:
            raise ValueError(
                "w_internal_clearance cannot be negative."
            )

    def internal_clearance_reward(
        self,
        state: FleetState,
    ) -> float:
        if self.w_internal_clearance <= 0.0:
            return 0.0

        clearance = float(
            state.minimum_internal_clearance_m
        )

        if math.isinf(clearance) and clearance > 0.0:
            return 0.0

        if not math.isfinite(clearance):
            return -self.w_internal_clearance

        risk = (
            self.internal_clearance_safe_m
            - clearance
        ) / self.internal_clearance_safe_m

        risk = max(
            0.0,
            min(1.0, risk),
        )

        return (
            -self.w_internal_clearance
            * risk
            * risk
        )

    def evaluate(
        self,
        prev_state: FleetState,
        next_state: FleetState,
    ) -> float:
        prev_tokens = set(prev_state.controlled_tokens)
        next_tokens = set(next_state.controlled_tokens)
        reward_tokens = set(self._vehicle_rewards)

        if prev_tokens != next_tokens:
            raise ValueError(
                "Previous and next fleet tokens must match."
            )

        if prev_tokens != reward_tokens:
            raise ValueError(
                "Fleet and reward-model tokens must match."
            )

        vehicle_total = 0.0
        vehicle_count = prev_state.vehicle_count

        for token in prev_state.controlled_tokens:
            prev_vehicle = prev_state.state_for(token)
            next_vehicle = next_state.state_for(token)

            if prev_vehicle.goal_reached:
                continue

            model = self._vehicle_rewards[token]

            breakdown = model.evaluate_breakdown(
                prev_vehicle,
                next_vehicle,
            )

            vehicle_total += (
                breakdown.progress
                + breakdown.speed
                + breakdown.safety
                + breakdown.comfort
            )

            if next_vehicle.goal_reached:
                vehicle_total += model.cfg.goal_bonus

        total = vehicle_total / vehicle_count

        total += self.internal_clearance_reward(
            next_state
        )

        if next_state.hard_safety_violation:
            total -= max(
                model.cfg.collision_penalty
                for model in self._vehicle_rewards.values()
            )

        return total

    def is_terminal(
        self,
        state: FleetState,
        depth: int,
        max_depth: int,
    ) -> bool:
        return (
            state.hard_safety_violation
            or state.all_goals_reached
            or depth >= max_depth
        )
