from __future__ import annotations

import math
import random
import time

from itertools import product
from typing import Callable, Dict, List, Optional, Tuple

from .action_space import MCTSAction
from .fleet_node import FleetMCTSNode
from .fleet_reward import FleetRewardModel
from .fleet_state import FleetState
from .fleet_transition import FleetTransitionModel
from .joint_action import JointAction


def active_joint_actions(
    state: FleetState,
) -> List[JointAction]:
    tokens = tuple(sorted(state.controlled_tokens))
    domains = []

    for token in tokens:
        vehicle_state = state.state_for(token)

        if vehicle_state.goal_reached:
            domains.append((MCTSAction.KEEP,))
        else:
            domains.append(tuple(MCTSAction))

    return [
        JointAction.from_pairs(
            zip(tokens, actions)
        )
        for actions in product(*domains)
    ]


def _joint_action_key(
    action: JointAction,
) -> Tuple[int, ...]:
    return tuple(
        int(item)
        for item in action.actions
    )


def _joint_action_id(
    action: JointAction,
) -> str:
    return ",".join(
        str(value)
        for value in _joint_action_key(action)
    )


class FleetMCTSSearch:
    def __init__(
        self,
        transition_model: FleetTransitionModel,
        reward_model: FleetRewardModel,
        action_provider: Callable[
            [FleetState],
            List[JointAction],
        ] = active_joint_actions,
        budget: int = 300,
        max_depth: int = 8,
        c_uct: float = 1.4,
        gamma: float = 0.99,
        seed: int = 0,
    ):
        self.transition = transition_model
        self.reward = reward_model
        self.action_provider = action_provider
        self.budget = budget
        self.max_depth = max_depth
        self.c_uct = c_uct
        self.gamma = gamma
        self.rng = random.Random(seed)
        self.seed = seed

    def search(
        self,
        root_state: FleetState,
    ) -> Tuple[JointAction, Dict]:
        root = FleetMCTSNode(
            state=root_state,
            depth=0,
            available_actions=list(
                self.action_provider(root_state)
            ),
        )

        start_time = time.perf_counter()

        for _ in range(self.budget):
            node = root

            while (
                not node.is_terminal(self.max_depth)
                and node.is_fully_expanded()
                and node.children
            ):
                node = self._select_uct(node)

            if not node.is_terminal(self.max_depth):
                node = self._expand(node)

            rollout_value = self._rollout(node)
            self._backup(node, rollout_value)

        if not root.children:
            raise RuntimeError(
                "Fleet MCTS root has no children."
            )

        best_action = max(
            root.children.items(),
            key=lambda item: (
                item[1].visit_count,
                item[1].q,
                tuple(
                    -value
                    for value in _joint_action_key(
                        item[0]
                    )
                ),
            ),
        )[0]

        diagnostics = {
            "elapsed_ms": (
                time.perf_counter() - start_time
            ) * 1000.0,
            "iterations": self.budget,
            "seed": self.seed,
            "vehicle_tokens": root_state.controlled_tokens,
            "visits": {
                _joint_action_id(action):
                child.visit_count
                for action, child in root.children.items()
            },
            "q_values": {
                _joint_action_id(action):
                child.q
                for action, child in root.children.items()
            },
            "immediate_rewards": {
                _joint_action_id(action):
                self.reward.evaluate(
                    root_state,
                    child.state,
                )
                for action, child in root.children.items()
            },
            "minimum_clearance_m": {
                _joint_action_id(action):
                child.state.minimum_clearance_m
                for action, child in root.children.items()
            },
        }

        return best_action, diagnostics

    def _select_uct(
        self,
        node: FleetMCTSNode,
    ) -> FleetMCTSNode:
        log_parent = math.log(
            node.visit_count + 1.0
        )

        best_child: Optional[FleetMCTSNode] = None
        best_score = -float("inf")

        for action, child in sorted(
            node.children.items(),
            key=lambda item: _joint_action_key(
                item[0]
            ),
        ):
            explore = self.c_uct * math.sqrt(
                log_parent
                / (child.visit_count + 1e-6)
            )

            score = child.q + explore

            if score > best_score:
                best_score = score
                best_child = child

        if best_child is None:
            raise RuntimeError(
                "Fleet UCT selection found no child."
            )

        return best_child

    def _expand(
        self,
        node: FleetMCTSNode,
    ) -> FleetMCTSNode:
        if not node.untried_actions:
            return node

        index = self.rng.randrange(
            len(node.untried_actions)
        )

        action = node.untried_actions.pop(index)

        next_state = self.transition.step(
            node.state,
            action,
        )

        child = FleetMCTSNode(
            state=next_state,
            parent=node,
            action_from_parent=action,
            depth=node.depth + 1,
            available_actions=list(
                self.action_provider(next_state)
            ),
        )

        node.children[action] = child
        return child

    def _rollout(
        self,
        node: FleetMCTSNode,
    ) -> float:
        state = node.state
        depth = node.depth
        total_reward = 0.0
        discount = 1.0

        while not self.reward.is_terminal(
            state,
            depth,
            self.max_depth,
        ):
            actions = self.action_provider(state)

            if not actions:
                break

            action = self.rng.choice(actions)

            next_state = self.transition.step(
                state,
                action,
            )

            step_reward = self.reward.evaluate(
                state,
                next_state,
            )

            total_reward += (
                discount * step_reward
            )

            discount *= self.gamma
            state = next_state
            depth += 1

        return total_reward

    def _backup(
        self,
        node: FleetMCTSNode,
        rollout_value: float,
    ) -> None:
        value = rollout_value
        current: Optional[FleetMCTSNode] = node

        while current is not None:
            if current.parent is not None:
                immediate_reward = self.reward.evaluate(
                    current.parent.state,
                    current.state,
                )

                value = (
                    immediate_reward
                    + self.gamma * value
                )

            current.visit_count += 1
            current.value_sum += value
            current = current.parent
