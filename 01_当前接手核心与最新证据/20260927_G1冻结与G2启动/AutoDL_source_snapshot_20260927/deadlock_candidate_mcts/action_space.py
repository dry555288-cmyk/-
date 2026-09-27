from enum import IntEnum
from typing import Dict

class MCTSAction(IntEnum):
    """
    Discrete actions for the MCTS planner.
    The order of actions is fixed for reproducibility and will be used as indices in policy vectors.
    """
    BRAKE = 0
    DECEL = 1
    KEEP = 2
    ACCEL = 3

# Mapping from action to a longitudinal acceleration value (m/s^2).
# These are initial values and should be tuned based on experimental results.
ACTION_ACCEL: Dict[MCTSAction, float] = {
    MCTSAction.BRAKE: -3.0,
    MCTSAction.DECEL: -1.5,
    MCTSAction.KEEP: 0.0,
    MCTSAction.ACCEL: 1.0,
}

# Total number of actions
NUM_ACTIONS = len(MCTSAction)
