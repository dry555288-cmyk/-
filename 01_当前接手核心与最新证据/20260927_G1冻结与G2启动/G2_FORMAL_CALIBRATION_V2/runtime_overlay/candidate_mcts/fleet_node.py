from typing import Callable, List, Optional, Dict, Tuple
from .fleet_state import FleetState
from .joint_action import JointAction

class FleetMCTSNode:
    """
    A node in the MCTS search tree.
    """

    def __init__(
        self,
        state: FleetState,
        parent: Optional['FleetMCTSNode'] = None,
        action_from_parent: Optional[JointAction] = None,
        depth: int = 0,
        available_actions: List[JointAction] = None,
        terminal_predicate: Optional[Callable[[FleetState], bool]] = None,
    ):
        self.state: FleetState = state
        self.parent: Optional['FleetMCTSNode'] = parent
        self.action_from_parent: Optional[JointAction] = action_from_parent
        self.depth: int = depth
        self.children: Dict[JointAction, 'FleetMCTSNode'] = {}
        self.untried_actions: List[JointAction] = available_actions if available_actions is not None else []
        self.visit_count: int = 0
        self.value_sum: float = 0.0
        self.terminal_predicate = terminal_predicate

    @property
    def q(self) -> float:
        """Average value of this node."""
        return self.value_sum / self.visit_count if self.visit_count > 0 else 0.0

    def is_fully_expanded(self) -> bool:
        """Check if all possible actions have been tried."""
        return len(self.untried_actions) == 0

    def is_terminal(self, max_depth: int) -> bool:
        """Check hard/task/depth terminal plus injected deadlock terminal."""
        if self.state.hard_safety_violation or self.state.all_goals_reached or self.depth >= max_depth:
            return True
        return bool(self.terminal_predicate and self.terminal_predicate(self.state))
