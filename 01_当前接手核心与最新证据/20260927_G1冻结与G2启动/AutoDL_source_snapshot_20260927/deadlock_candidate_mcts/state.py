from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

from .action_space import MCTSAction


@dataclass(frozen=True)
class MCTSState:
    """
    Immutable state representation for the MCTS search tree.
    """

    time_s: float
    route_s: float
    speed_mps: float
    accel_mps2: float
    lead_distance_m: float
    lead_rel_speed_mps: float
    target_speed_mps: float
    minimum_clearance_m: float = float("inf")
    prev_action: Optional[MCTSAction] = None
    collision: bool = False
    goal_reached: bool = False

    def transition_cache_key(
        self,
    ) -> Tuple[
        float,
        float,
        float,
        float,
        float,
        float,
        bool,
        bool,
    ]:
        """
        Return the exact fields determining future transitions.

        Current acceleration only affects reward through jerk; the
        selected action directly determines the next acceleration.
        Previous action and prior-transition clearance do not affect
        future dynamics or geometry.
        """

        return (
            self.time_s,
            self.route_s,
            self.speed_mps,
            self.lead_distance_m,
            self.lead_rel_speed_mps,
            self.target_speed_mps,
            self.collision,
            self.goal_reached,
        )
