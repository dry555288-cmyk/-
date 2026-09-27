from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Sequence, Tuple

@dataclass(frozen=True)
class DeadlockDecision:
    is_deadlock: bool
    reason: str
    admitted_actions: int = 0
    safe_stationary_actions: int = 0
    hard_terminal_actions: int = 0
    safe_escape_actions: int = 0

def _state_key(state: Any) -> Tuple[Any, ...]:
    return (state.transition_cache_key(), state.hard_safety_violation, state.all_goals_reached, tuple((t, state.state_for(t).goal_reached, float(state.state_for(t).speed_mps), float(state.state_for(t).route_s)) for t in state.controlled_tokens))

class SafeAbsorbingDeadlockDetector:
    def __init__(self, action_provider: Callable[[Any], Sequence[Any]], transition_step: Callable[[Any, Any], Any], *, stationary_eps: float = 0.0, progress_eps: float = 0.0):
        self.action_provider = action_provider
        self.transition_step = transition_step
        self.stationary_eps = float(stationary_eps)
        self.progress_eps = float(progress_eps)
        self._memo: Dict[Tuple[Any, ...], DeadlockDecision] = {}

    def inspect(self, state: Any) -> DeadlockDecision:
        key = _state_key(state)
        if key in self._memo:
            return self._memo[key]
        if state.hard_safety_violation:
            d = DeadlockDecision(False, "HARD_SAFETY_TERMINAL"); self._memo[key]=d; return d
        if state.all_goals_reached:
            d = DeadlockDecision(False, "SUCCESS_TERMINAL"); self._memo[key]=d; return d
        unfinished=[t for t in state.controlled_tokens if not state.state_for(t).goal_reached]
        if any(abs(float(state.state_for(t).speed_mps)) > self.stationary_eps for t in unfinished):
            d = DeadlockDecision(False, "UNFINISHED_VEHICLE_MOVING"); self._memo[key]=d; return d
        actions=list(self.action_provider(state))
        if not actions:
            d = DeadlockDecision(False, "NO_ADMITTED_ACTION"); self._memo[key]=d; return d
        before={t: float(state.state_for(t).route_s) for t in unfinished}
        safe_stationary=hard=escape=0
        for action in actions:
            nxt=self.transition_step(state, action)
            if nxt.hard_safety_violation:
                hard += 1; continue
            escaped=bool(nxt.all_goals_reached)
            if not escaped:
                for t in unfinished:
                    nv=nxt.state_for(t)
                    if nv.goal_reached or float(nv.route_s) > before[t] + self.progress_eps or abs(float(nv.speed_mps)) > self.stationary_eps:
                        escaped=True; break
            if escaped: escape += 1
            else: safe_stationary += 1
        if escape > 0: d=DeadlockDecision(False,"SAFE_ESCAPE_EXISTS",len(actions),safe_stationary,hard,escape)
        elif safe_stationary > 0: d=DeadlockDecision(True,"SAFE_ABSORBING_DEADLOCK",len(actions),safe_stationary,hard,0)
        else: d=DeadlockDecision(False,"NO_SAFE_STATIONARY_CONTINUATION",len(actions),0,hard,0)
        self._memo[key]=d; return d

    def is_deadlock(self, state: Any) -> bool:
        return self.inspect(state).is_deadlock
