"""Candidate only: one-step subtree promotion with finite-horizon sample rebasing.

NOT a verbatim paper reproduction and NOT the closed action-report cache.
Every reused Monte Carlo sample has the old first reward removed and is extended
with the unchanged native rollout policy until H transitions or a true terminal.
All node sums/counts are then rebuilt, rather than copying stale H-1 Q values.
The root accounting target is B total samples: m inherited + (B-m) fresh.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
import time
from candidate_mcts.fleet_search import FleetMCTSSearch, _joint_action_id, _joint_action_key
from candidate_mcts.fleet_node import FleetMCTSNode


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def discounted(rewards, gamma):
    # Match the parent's forward rollout arithmetic, not a different sum routine.
    total, factor = 0.0, 1.0
    for r in rewards:
        total += factor * r
        factor *= gamma
    return total


@dataclass(frozen=True)
class Sample:
    uid: tuple
    nodes: tuple           # Explicit selection/expansion path, NOT rollout nodes.
    states: tuple          # Entire sampled path, including rollout.
    actions: tuple
    rewards: tuple
    origin: str
    inherited_from: object = None
    tail_actions_added: int = 0


class HorizonRebasedSearch(FleetMCTSSearch):
    def __init__(self, *args, state_encode, binding, **kwargs):
        super().__init__(*args, **kwargs)
        require(type(self.max_depth) is int and self.max_depth >= 1, 'BAD_HORIZON')
        require(type(self.budget) is int and self.budget >= 1, 'BAD_BUDGET')
        require(0 < self.gamma <= 1 and math.isfinite(self.gamma), 'BAD_GAMMA')
        self.encode = state_encode
        self.binding = binding
        self.last_root = None
        self.last_action = None
        self.last_binding = None
        self.samples = []
        self.round_id = 0
        self.last_meta = {}
        self._tail = None
        self._uid_counter = 0
        self.promotion_snapshot = None
        self.promotion_rng_before = None
        self.promotion_rng_after = None

    def _is_absorbing(self, state):
        return bool(state.hard_safety_violation or state.all_goals_reached)

    def _nodes(self, root):
        result, stack, seen = [], [root], set()
        while stack:
            n = stack.pop()
            require(id(n) not in seen, 'TREE_CYCLE')
            seen.add(id(n)); result.append(n)
            # Dict insertion order is preserved, including after promotion.
            stack.extend(reversed(list(n.children.values())))
        return result

    def _rollout(self, node):
        state, depth = node.state, node.depth
        states, actions, rewards = [state], [], []
        total, factor = 0.0, 1.0
        while not self.reward.is_terminal(state, depth, self.max_depth):
            choices = self.action_provider(state)
            if not choices:
                break
            action = self.rng.choice(choices)
            nxt = self.transition.step(state, action)
            r = self.reward.evaluate(state, nxt)
            total += factor * r
            factor *= self.gamma
            states.append(nxt); actions.append(action); rewards.append(r)
            state, depth = nxt, depth + 1
        self._tail = (tuple(states), tuple(actions), tuple(rewards), total)
        return total

    def _backup(self, node, rollout_value):
        # Preserve the parent's exact backup and evaluation order on fresh samples.
        current, value = node, rollout_value
        reverse_nodes, reverse_rewards = [], []
        while current is not None:
            reverse_nodes.append(current)
            if current.parent is not None:
                immediate = self.reward.evaluate(current.parent.state, current.state)
                reverse_rewards.append(immediate)
                value = immediate + self.gamma * value
            current.visit_count += 1
            current.value_sum += value
            current = current.parent
        path = tuple(reversed(reverse_nodes))
        ts, ta, tr, tv = self._tail
        require(tv == rollout_value and ts[0] is node.state, 'ROLLOUT_TRACE_BINDING')
        sample = Sample((self.round_id, self._uid_counter), path,
                        tuple(n.state for n in path) + ts[1:],
                        tuple(n.action_from_parent for n in path[1:]) + ta,
                        tuple(reversed(reverse_rewards)) + tr, 'NEW_ITERATION')
        self._uid_counter += 1
        self._validate_sample(sample)
        self.samples.append(sample)

    def _validate_sample(self, sample):
        require(len(sample.states) == len(sample.actions) + 1 == len(sample.rewards) + 1,
                'SAMPLE_LENGTH')
        require(0 <= len(sample.actions) <= self.max_depth, 'SAMPLE_EXCEEDS_HORIZON')
        require(len(sample.actions) == self.max_depth or self._is_absorbing(sample.states[-1]),
                'NONTERMINAL_SHORT_SAMPLE_NOT_REUSABLE')
        require(sample.nodes and len(sample.nodes) <= len(sample.states), 'BAD_EXPLICIT_PATH')
        require(all(n.state == sample.states[i] for i, n in enumerate(sample.nodes)), 'PATH_STATE')
        require(all(math.isfinite(r) for r in sample.rewards), 'NONFINITE_REWARD')

    def _accumulate_saved(self, sample):
        leaf_depth = len(sample.nodes) - 1
        value = discounted(sample.rewards[leaf_depth:], self.gamma)
        for i in range(leaf_depth, -1, -1):
            node = sample.nodes[i]
            if i:
                value = sample.rewards[i-1] + self.gamma * value
            node.visit_count += 1
            node.value_sum += value

    def _fallback(self, state, reason):
        self.samples = []
        root = FleetMCTSNode(state=state, depth=0,
                             available_actions=list(self.action_provider(state)))
        self.promotion_snapshot = None
        return root, {'mode':'FRESH_ROOT', 'reason':reason, 'inherited_samples':0,
                      'retained_nodes':0, 'tail_transitions':0, 'carried_old_q_directly':False}

    def _prepare(self, state, signature):
        self.promotion_rng_before = self.rng.getstate()
        if self.last_root is None:
            return self._fallback(state, 'FIRST_DECISION')
        if signature != self.last_binding:
            return self._fallback(state, 'MODEL_ROUTE_CONFIG_CHANGED')
        child = self.last_root.children.get(self.last_action)
        if child is None:
            return self._fallback(state, 'SELECTED_CHILD_MISSING')
        if child.state != state or self.encode(child.state) != self.encode(state):
            return self._fallback(state, 'EXECUTED_STATE_MISMATCH')
        nodes = self._nodes(child)
        # Validate all retained action domains before mutating a tree or drawing RNG.
        for n in nodes:
            domain = list(self.action_provider(n.state))
            stored = list(n.children) + list(n.untried_actions)
            if len(set(stored)) != len(stored) or set(domain) != set(stored):
                return self._fallback(state, 'RETAINED_ACTION_DOMAIN_MISMATCH')
        previous = self.samples
        kept = [s for s in previous if len(s.nodes)>1 and s.nodes[1] is child]
        require(len(kept) == child.visit_count and len(kept) <= self.budget, 'INHERITED_SUPPORT_COUNT')
        require(len({s.uid for s in kept}) == len(kept), 'DUPLICATE_INHERITED_SAMPLE')
        require(len(kept)>0, 'EMPTY_SELECTED_CHILD_SUPPORT')
        offset = child.depth
        require(offset == 1, 'ONLY_ONE_EXECUTED_ACTION_REUSE')
        child.parent = None
        child.action_from_parent = None
        for n in nodes:
            n.depth -= offset
            n.visit_count = 0
            n.value_sum = 0.0
        self.samples = []
        extensions = 0
        for s in kept:
            states, actions, rewards = list(s.states[1:]), list(s.actions[1:]), list(s.rewards[1:])
            require(states and states[0] == state, 'REBASE_START')
            count = 0
            # In a one-step shift, each nonterminal sample needs exactly one tail transition.
            while len(actions) < self.max_depth and not self._is_absorbing(states[-1]):
                choices = self.action_provider(states[-1])
                require(bool(choices), 'TAIL_NO_ACTIONS_WITHOUT_TERMINAL')
                action = self.rng.choice(choices)
                nxt = self.transition.step(states[-1], action)
                reward = self.reward.evaluate(states[-1], nxt)
                states.append(nxt); actions.append(action); rewards.append(reward)
                count += 1
            require(count <= 1, 'UNEXPECTED_MULTI_STEP_TAIL')
            extensions += count
            rebased = Sample(s.uid, s.nodes[1:], tuple(states), tuple(actions), tuple(rewards),
                             'REBASED_INHERITED_SAMPLE',
                             {'old_round':self.round_id-1, 'old_length':len(s.actions),
                              'removed_first_reward':s.rewards[0],
                              'old_rewards':s.rewards, 'old_action_ids':tuple(_joint_action_id(a) for a in s.actions)}, count)
            self._validate_sample(rebased)
            self._accumulate_saved(rebased)
            self.samples.append(rebased)
        require(child.visit_count == len(kept), 'PROMOTED_ROOT_COUNT')
        self.promotion_rng_after = self.rng.getstate()
        self.promotion_snapshot = self.audit(child, include_states=False)
        return child, {'mode':'H8_SUFFIX_REBASED_SUBTREE', 'reason':'EXACT_STATE_AND_BINDING',
                       'inherited_samples':len(kept), 'retained_nodes':len(nodes),
                       'tail_transitions':extensions, 'carried_old_q_directly':False,
                       'old_nominal_remaining_horizon':self.max_depth-1,
                       'new_root_horizon':self.max_depth,
                       'inherited_sample_information_is_not_independent':True}

    def search(self, root_state):
        started = time.perf_counter()
        signature = (self.budget, self.max_depth, self.c_uct, self.gamma, self.binding())
        self.round_id += 1; self._uid_counter = 0
        require(not self._is_absorbing(root_state), 'NO_SEARCH_AFTER_TRUE_TERMINAL')
        root, meta = self._prepare(root_state, signature)
        if meta['inherited_samples'] == 0:
            self.promotion_rng_after = self.rng.getstate()
        fresh = self.budget - meta['inherited_samples']
        for _ in range(fresh):
            node = root
            while not node.is_terminal(self.max_depth) and node.is_fully_expanded() and node.children:
                node = self._select_uct(node)
            if not node.is_terminal(self.max_depth):
                node = self._expand(node)
            value = self._rollout(node)
            self._backup(node, value)
        require(root.children and root.visit_count == self.budget and len(self.samples) == self.budget,
                'FINAL_ROOT_BUDGET')
        chosen = max(root.children.items(), key=lambda item:(item[1].visit_count, item[1].q,
                           tuple(-v for v in _joint_action_key(item[0]))))[0]
        # The standard keys preserve native meaning except iterations: it counts NEW work.
        diagnostics = {'elapsed_ms':(time.perf_counter()-started)*1000,
                       'iterations':fresh, 'seed':self.seed, 'vehicle_tokens':root_state.controlled_tokens,
                       'visits':{_joint_action_id(a):c.visit_count for a,c in root.children.items()},
                       'q_values':{_joint_action_id(a):c.q for a,c in root.children.items()},
                       'immediate_rewards':{_joint_action_id(a):self.reward.evaluate(root_state,c.state)
                                            for a,c in root.children.items()},
                       'minimum_clearance_m':{_joint_action_id(a):c.state.minimum_clearance_m
                                               for a,c in root.children.items()}}
        meta.update(new_iterations=fresh, target_root_samples=self.budget,
                    root_visit_count=root.visit_count, child_visit_sum=sum(c.visit_count for c in root.children.values()),
                    root_only_sample_count=sum(len(s.nodes)==1 for s in self.samples),
                    node_count=len(self._nodes(root)), max_depth=self.max_depth,
                    tree_statistics_rebuilt=True, action_report_cache_used=False)
        self.last_root, self.last_action, self.last_binding = root, chosen, signature
        self.last_meta = meta
        diagnostics['reuse_accounting'] = meta
        return chosen, diagnostics

    def audit(self, root=None, *, include_states=True):
        root = root or self.last_root
        nodes = self._nodes(root)
        ids = {id(n):i for i,n in enumerate(nodes)}
        samples=[]
        for s in self.samples:
            samples.append({'uid':list(s.uid), 'path_nodes':[ids[id(n)] for n in s.nodes],
                'action_ids':[_joint_action_id(a) for a in s.actions], 'rewards':list(s.rewards),
                'states':[self.encode(x) for x in s.states] if include_states else None, 'origin':s.origin,
                'inherited_from':s.inherited_from, 'tail_actions_added':s.tail_actions_added,
                'true_terminal':self._is_absorbing(s.states[-1])})
        return {'nodes':[{'id':ids[id(n)],'parent':None if n.parent is None else ids[id(n.parent)],
                     'depth':n.depth,'state':self.encode(n.state) if include_states else None,'visits':n.visit_count,'value_sum':n.value_sum,
                     'q':n.q,'action_from_parent':None if n.action_from_parent is None else _joint_action_id(n.action_from_parent),
                     'children':{_joint_action_id(a):ids[id(c)] for a,c in n.children.items()},
                     'untried':[_joint_action_id(a) for a in n.untried_actions]} for n in nodes],
                'samples':samples,'gamma':self.gamma,'horizon':self.max_depth,
                'root_visits':root.visit_count,'same_mc_observation_may_support_multiple_nodes':True}
