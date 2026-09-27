import math
from dataclasses import dataclass

from .state import MCTSState


@dataclass(frozen=True)
class RewardConfig:
    """Weights and thresholds used by the MCTS reward model."""

    w_progress: float = 1.0
    w_speed: float = 0.3
    w_safety: float = 2.0
    w_clearance: float = 0.0
    w_comfort: float = 0.3
    collision_penalty: float = 100.0
    goal_bonus: float = 30.0
    ttc_safe_s: float = 3.0
    clearance_safe_m: float = 3.0
    eps: float = 1e-6


@dataclass(frozen=True)
class RewardBreakdown:
    """
    Weighted reward contributions for one state transition.

    The five component fields sum exactly to ``total``.
    """

    progress: float
    speed: float
    safety: float
    comfort: float
    terminal: float
    total: float


class RewardModel:
    """Evaluate progress, speed, safety, comfort, and terminal reward."""

    def __init__(
        self,
        config: RewardConfig,
        dt: float,
    ):
        if dt <= 0.0:
            raise ValueError("dt must be positive.")

        if config.clearance_safe_m <= 0.0:
            raise ValueError(
                "clearance_safe_m must be positive."
            )

        self.cfg = config
        self.dt = float(dt)

    def _raw_clearance_penalty(
        self,
        state: MCTSState,
    ) -> float:
        """
        Return a bounded continuous 2D-clearance penalty.

        The penalty is zero at or above the safe-clearance threshold
        and decreases quadratically toward -1.0 as clearance reaches
        zero. Positive infinity means no predicted obstacle.
        """

        clearance_m = state.minimum_clearance_m

        if (
            math.isinf(clearance_m)
            and clearance_m > 0.0
        ):
            return 0.0

        if not math.isfinite(clearance_m):
            return -1.0

        normalized_risk = (
            self.cfg.clearance_safe_m
            - clearance_m
        ) / self.cfg.clearance_safe_m

        normalized_risk = max(
            0.0,
            min(1.0, normalized_risk),
        )

        return -normalized_risk * normalized_risk

    def evaluate_breakdown(
        self,
        prev_state: MCTSState,
        next_state: MCTSState,
    ) -> RewardBreakdown:
        """Return the weighted reward components for one transition."""

        cfg = self.cfg

        # Progress reward, normalized by nominal target-speed progress.
        route_progress = max(
            0.0,
            next_state.route_s - prev_state.route_s,
        )
        progress_denominator = max(
            prev_state.target_speed_mps * self.dt,
            cfg.eps,
        )
        raw_progress = (
            route_progress
            / progress_denominator
        )

        # Penalize deviation from target speed.
        target_speed_denominator = max(
            next_state.target_speed_mps,
            cfg.eps,
        )
        raw_speed = (
            -abs(
                next_state.speed_mps
                - next_state.target_speed_mps
            )
            / target_speed_denominator
        )

        # Legacy scalar TTC term. The formal planner keeps this
        # disabled because not every obstacle follows the ego route.
        closing_speed = max(
            0.0,
            -next_state.lead_rel_speed_mps,
        )

        if closing_speed <= cfg.eps:
            raw_safety = 0.0
        else:
            time_to_collision = (
                next_state.lead_distance_m
                / closing_speed
            )
            raw_safety = -max(
                0.0,
                (
                    cfg.ttc_safe_s
                    - time_to_collision
                )
                / cfg.ttc_safe_s,
            )

        # Jerk-like comfort penalty.
        jerk_mps3 = (
            abs(
                next_state.accel_mps2
                - prev_state.accel_mps2
            )
            / self.dt
        )
        raw_comfort = -jerk_mps3 / 10.0

        terminal = 0.0

        if next_state.collision:
            terminal -= cfg.collision_penalty

        if next_state.goal_reached:
            terminal += cfg.goal_bonus

        raw_clearance = (
            self._raw_clearance_penalty(
                next_state
            )
        )

        progress = cfg.w_progress * raw_progress
        speed = cfg.w_speed * raw_speed
        safety = (
            cfg.w_safety * raw_safety
            + cfg.w_clearance * raw_clearance
        )
        comfort = cfg.w_comfort * raw_comfort

        total = (
            progress
            + speed
            + safety
            + comfort
            + terminal
        )

        return RewardBreakdown(
            progress=progress,
            speed=speed,
            safety=safety,
            comfort=comfort,
            terminal=terminal,
            total=total,
        )

    def evaluate(
        self,
        prev_state: MCTSState,
        next_state: MCTSState,
    ) -> float:
        """
        Return the scalar reward used by MCTS search.

        This hot-path implementation intentionally avoids creating a
        RewardBreakdown object during every tree expansion and rollout.
        """

        cfg = self.cfg

        route_progress = max(
            0.0,
            next_state.route_s - prev_state.route_s,
        )
        progress_denominator = max(
            prev_state.target_speed_mps * self.dt,
            cfg.eps,
        )
        progress = (
            cfg.w_progress
            * route_progress
            / progress_denominator
        )

        target_speed_denominator = max(
            next_state.target_speed_mps,
            cfg.eps,
        )
        speed = (
            cfg.w_speed
            * (
                -abs(
                    next_state.speed_mps
                    - next_state.target_speed_mps
                )
                / target_speed_denominator
            )
        )

        closing_speed = max(
            0.0,
            -next_state.lead_rel_speed_mps,
        )

        if closing_speed <= cfg.eps:
            ttc_safety = 0.0
        else:
            time_to_collision = (
                next_state.lead_distance_m
                / closing_speed
            )
            raw_safety = -max(
                0.0,
                (
                    cfg.ttc_safe_s
                    - time_to_collision
                )
                / cfg.ttc_safe_s,
            )
            ttc_safety = (
                cfg.w_safety * raw_safety
            )

        clearance_safety = (
            cfg.w_clearance
            * self._raw_clearance_penalty(
                next_state
            )
        )

        safety = (
            ttc_safety
            + clearance_safety
        )

        jerk_mps3 = (
            abs(
                next_state.accel_mps2
                - prev_state.accel_mps2
            )
            / self.dt
        )
        comfort = (
            cfg.w_comfort
            * (-jerk_mps3 / 10.0)
        )

        terminal = 0.0

        if next_state.collision:
            terminal -= cfg.collision_penalty

        if next_state.goal_reached:
            terminal += cfg.goal_bonus

        return (
            progress
            + speed
            + safety
            + comfort
            + terminal
        )

    def is_terminal(
        self,
        state: MCTSState,
        depth: int,
        max_depth: int,
    ) -> bool:
        """Return whether search should stop at this state."""

        return (
            state.collision
            or state.goal_reached
            or depth >= max_depth
        )
