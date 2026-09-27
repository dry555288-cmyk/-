"""Isolated A/B native-interface adapter with unchanged frozen UCT and reward.

Only additional modules are introduced. It is NOT installed in AutoDL or the
production repo. Geometry remains sampled at the original 0.1 s cadence: the
new s(t) is integrated piecewise, not linearly interpolated between endpoints.
The geometry_at implementation is supplied explicitly by the caller; no map,
road-boundary availability or continuous-time collision guarantee is inferred.
"""
from __future__ import annotations
from dataclasses import asdict, replace
from itertools import product
import math
from typing import Dict, Mapping, Tuple

from .action_space import MCTSAction
from .fleet_collision import evaluate_internal_fleet_collision
from .fleet_state import FleetState
from .fleet_transition import FleetTransitionModel
from .fleet_reward import FleetRewardModel
from .fleet_search import FleetMCTSSearch
from .joint_action import JointAction
from .reward import RewardConfig, RewardModel
from .transition_model import TransitionConfig
from .dual_stop_motion_v1 import VERSION, ContractError, DualOnlyState, DestinationStopTransition, finite, need

CODEC = 'DUAL_ONLY_STOP_STATE_CODEC_V1'


def action_id(action: JointAction) -> str:
    return ','.join(str(int(action.action_for(t))) for t in ('A', 'B'))


class DualStopFleetTransition(FleetTransitionModel):
    def __init__(self, vehicle_transitions: Mapping[str, DestinationStopTransition],
                 route_geometry_caches: Mapping[str, object], *,
                 external_tokens: Tuple[str, ...], confirmed_dual_only: bool,
                 internal_collision_sample_dt_s: float, internal_safety_margin_m: float):
        need(confirmed_dual_only is True and type(external_tokens) is tuple and external_tokens == (),
             'EXPLICIT_DUAL_ONLY_SCOPE_REQUIRED')
        need(set(vehicle_transitions) == {'A', 'B'}, 'EXACTLY_A_AND_B_REQUIRED')
        need(all(isinstance(m, DestinationStopTransition) for m in vehicle_transitions.values()), 'NEW_MOTION_REQUIRED')
        need(route_geometry_caches is not None and set(route_geometry_caches) == {'A', 'B'}, 'BOTH_GEOMETRY_CACHES_REQUIRED')
        need(all(callable(getattr(g, 'geometry_at', None)) for g in route_geometry_caches.values()), 'GEOMETRY_API')
        need(finite(internal_collision_sample_dt_s, 'SAMPLE_DT') == 0.1, 'UNAPPROVED_COLLISION_CADENCE')
        need(finite(internal_safety_margin_m, 'SAFETY_MARGIN') >= 0, 'NEGATIVE_SAFETY_MARGIN')
        super().__init__(vehicle_transitions, route_geometry_caches,
                         internal_collision_sample_dt_s, internal_safety_margin_m)

    def validate_fleet(self, state: FleetState) -> None:
        need(isinstance(state, FleetState) and state.controlled_tokens == ('A', 'B'), 'FLEET_TOKENS')
        for flag, pair_name in (('internal_collision', 'conflicting_pairs'),
                                ('internal_safety_violation', 'safety_violating_pairs')):
            need(type(getattr(state, flag)) is bool, 'FLEET_FLAG_TYPE')
            pairs = getattr(state, pair_name)
            need(pairs in ((), (('A', 'B'),)) and bool(pairs) == getattr(state, flag), 'FLEET_FLAG_PAIR_CONSISTENCY')
        cl = state.minimum_internal_clearance_m
        need((math.isfinite(cl) and cl >= 0) or cl == math.inf, 'FLEET_CLEARANCE_DOMAIN')
        for t in ('A', 'B'):
            self._vehicle_transitions[t].validate(state.state_for(t))
        need(state.state_for('A').time_s == state.state_for('B').time_s, 'FLEET_CLOCKS_DIFFER')

    def _geometry(self, positions: Mapping[str, float]):
        geometries = {}
        for t in ('A', 'B'):
            geom = self._route_geometry_caches[t].geometry_at(positions[t])
            # Shapely-compatible physical geometry is mandatory; no null fallback.
            need(hasattr(geom, 'is_empty') and not geom.is_empty and geom.is_valid, 'INVALID_GEOMETRY:' + t)
            geometries[t] = geom
        result = evaluate_internal_fleet_collision(geometries, self.internal_safety_margin_m)
        need(math.isfinite(result.minimum_internal_clearance_m) and result.minimum_internal_clearance_m >= 0,
             'NONFINITE_PAIR_CLEARANCE')
        return result

    def bind_initial_geometry(self, state: FleetState) -> FleetState:
        self.validate_fleet(state)
        need(not state.hard_safety_violation, 'INPUT_HARD_FLAG_CANNOT_BE_RESET')
        r = self._geometry({t: state.state_for(t).route_s for t in ('A', 'B')})
        return replace(state, internal_collision=r.internal_collision,
                       minimum_internal_clearance_m=r.minimum_internal_clearance_m,
                       conflicting_pairs=r.conflicting_pairs,
                       internal_safety_violation=r.internal_safety_violation,
                       safety_violating_pairs=r.safety_violating_pairs)

    def active_joint_actions(self, state: FleetState):
        self.validate_fleet(state)
        if state.hard_safety_violation or state.all_goals_reached:
            return []
        domains = [self._vehicle_transitions[t].actions(state.state_for(t)) for t in ('A', 'B')]
        return [JointAction.from_pairs(zip(('A', 'B'), a)) for a in product(*domains)]

    def step_with_diagnostics(self, state: FleetState, joint_action: JointAction):
        self.validate_fleet(state)
        need(not state.hard_safety_violation, 'DO_NOT_ADVANCE_HARD_TERMINAL')
        need(isinstance(joint_action, JointAction) and set(joint_action.vehicle_tokens) == {'A', 'B'}, 'ACTION_TOKENS')
        nxt, profiles, detail = {}, {}, {}
        for t in ('A', 'B'):
            model = self._vehicle_transitions[t]
            a = joint_action.action_for(t)
            before = state.state_for(t)
            # step_with_diagnostics rejects an infeasible or non-KEEP parked action.
            nxt[t], detail[t] = model.step_with_diagnostics(before, a)
            profiles[t] = model.profile(before, a)
        dt = self._vehicle_transitions['A'].cfg.dt
        n = max(1, math.ceil(dt / self.internal_collision_sample_dt_s))
        minimum = math.inf
        conflicts, unsafe, samples = set(), set(), []
        for i in range(n + 1):
            offset = dt * i / n
            positions = {t: math.fsum((state.state_for(t).route_s, profiles[t].at(offset).distance_m))
                         for t in ('A', 'B')}
            # Last sample must equal the actual transition state, not a separate integrator.
            if i == n:
                need(all(positions[t] == nxt[t].route_s for t in ('A', 'B')), 'SAMPLE_ENDPOINT_MISMATCH')
            r = self._geometry(positions)
            minimum = min(minimum, r.minimum_internal_clearance_m)
            conflicts.update(r.conflicting_pairs)
            unsafe.update(r.safety_violating_pairs)
            samples.append({'offset_s': offset, 'route_s': positions,
                            'minimum_clearance_m': r.minimum_internal_clearance_m,
                            'collision': r.internal_collision, 'safety_violation': r.internal_safety_violation})
        result = FleetState.from_states(nxt.items())
        result = replace(result, internal_collision=bool(conflicts), minimum_internal_clearance_m=minimum,
                         conflicting_pairs=tuple(sorted(conflicts)), internal_safety_violation=bool(unsafe),
                         safety_violating_pairs=tuple(sorted(unsafe)))
        return result, {'model_version': VERSION, 'vehicles': detail, 'collision_samples': samples,
                        'geometry_scope': 'SAMPLED_AB_ONLY_CALLER_BOUND_GEOMETRY_NOT_CONTINUOUS_PROOF',
                        'road_boundary_status': 'NOT_EVALUATED', 'joint_action_id': action_id(joint_action)}

    def step(self, state: FleetState, joint_action: JointAction) -> FleetState:
        return self.step_with_diagnostics(state, joint_action)[0]

    def pack(self, state: FleetState) -> Dict:
        """Versioned JSON-safe codec. NONE is distinct from absent/unknown data."""
        self.validate_fleet(state)
        cars = {}
        for t in ('A', 'B'):
            s = state.state_for(t)
            cars[t] = {k: getattr(s, k) for k in ('time_s', 'route_s', 'speed_mps', 'accel_mps2',
                       'target_speed_mps', 'goal_reached', 'collision', 'parked_at_time_s')}
            cars[t].update(prev_action=None if s.prev_action is None else int(s.prev_action),
                           external_lead={'mode': 'NONE', 'distance_m': None, 'relative_speed_mps': None},
                           minimum_external_clearance_m=None,
                           goal_window_m=list(self._vehicle_transitions[t].window),
                           acceleration_semantics='COMMANDED_NOT_MEASURED')
        clearance = state.minimum_internal_clearance_m
        need((math.isfinite(clearance) and clearance >= 0) or clearance == math.inf, 'BAD_PACKED_CLEARANCE')
        return {'schema': CODEC, 'model_version': VERSION, 'vehicles': cars,
                'internal_collision': state.internal_collision,
                'internal_safety_violation': state.internal_safety_violation,
                'minimum_internal_clearance_m': None if clearance == math.inf else clearance,
                'internal_clearance_status': 'UNMEASURED' if clearance == math.inf else 'SAMPLED',
                'conflicting_pairs': [list(p) for p in state.conflicting_pairs],
                'safety_violating_pairs': [list(p) for p in state.safety_violating_pairs]}

    def unpack(self, payload: Dict) -> FleetState:
        need(isinstance(payload, dict) and payload.get('schema') == CODEC and payload.get('model_version') == VERSION,
             'CODEC_VERSION')
        need(set(payload) == {'schema','model_version','vehicles','internal_collision','internal_safety_violation',
                              'minimum_internal_clearance_m','internal_clearance_status','conflicting_pairs','safety_violating_pairs'},
             'CODEC_TOPLEVEL_KEYS')
        need(set(payload.get('vehicles', {})) == {'A', 'B'}, 'CODEC_TOKENS')
        states = {}
        for t, row in payload['vehicles'].items():
            need(set(row) == {'time_s','route_s','speed_mps','accel_mps2','target_speed_mps','goal_reached','collision',
                              'parked_at_time_s','prev_action','external_lead','minimum_external_clearance_m',
                              'goal_window_m','acceleration_semantics'}, 'CODEC_VEHICLE_KEYS')
            need(row.get('external_lead') == {'mode': 'NONE', 'distance_m': None, 'relative_speed_mps': None},
                 'CODEC_NO_EXTERNAL_SCOPE')
            need(row.get('minimum_external_clearance_m') is None, 'CODEC_EXTERNAL_CLEARANCE')
            need(row.get('goal_window_m') == list(self._vehicle_transitions[t].window), 'CODEC_TARGET_DRIFT')
            need(row.get('acceleration_semantics') == 'COMMANDED_NOT_MEASURED', 'CODEC_ACCELERATION_CONVENTION')
            a = row['prev_action']
            need(a is None or (type(a) is int and 0 <= a < 4), 'CODEC_ACTION_INDEX')
            states[t] = DualOnlyState(**{k: row[k] for k in ('time_s', 'route_s', 'speed_mps', 'accel_mps2',
                    'target_speed_mps', 'goal_reached', 'collision', 'parked_at_time_s')},
                    lead_distance_m=math.inf, lead_rel_speed_mps=0.0,
                    prev_action=None if a is None else MCTSAction(a), minimum_clearance_m=math.inf)
        new = FleetState.from_states(states.items())
        cl = payload['minimum_internal_clearance_m']
        if cl is None:
            need(payload.get('internal_clearance_status') == 'UNMEASURED', 'CODEC_CLEARANCE_SCOPE')
            cl = math.inf
        else:
            need(payload.get('internal_clearance_status') == 'SAMPLED' and finite(cl, 'CLEARANCE') >= 0, 'CODEC_CLEARANCE')
        for name in ('internal_collision', 'internal_safety_violation'):
            need(type(payload.get(name)) is bool, 'CODEC_BOOLEAN')
        def pairs(name):
            p = payload[name]
            need(isinstance(p, list) and all(x == ['A', 'B'] for x in p) and len(p) <= 1, 'CODEC_PAIR')
            return tuple(tuple(x) for x in p)
        new = replace(new, internal_collision=payload['internal_collision'],
                      internal_safety_violation=payload['internal_safety_violation'],
                      minimum_internal_clearance_m=cl, conflicting_pairs=pairs('conflicting_pairs'),
                      safety_violating_pairs=pairs('safety_violating_pairs'))
        self.validate_fleet(new)
        return new


class CandidateSystem:
    """Exact old search/reward objects with explicitly injected new dynamics/domain.

    Factory arguments bind reward weights, safety margin and geometries; there is
    no unbound silent fallback or runtime loading of the old neural checkpoint.
    """
    def __init__(self, transition: DualStopFleetTransition,
                 reward_configs: Mapping[str, RewardConfig], *,
                 internal_clearance_safe_m: float, w_internal_clearance: float):
        need(set(reward_configs) == {'A', 'B'} and all(isinstance(c, RewardConfig) for c in reward_configs.values()),
             'EXPLICIT_REWARD_CONFIGS')
        self.transition = transition
        self.reward = FleetRewardModel(
            {t: RewardModel(reward_configs[t], dt=transition._vehicle_transitions[t].cfg.dt) for t in ('A', 'B')},
            internal_clearance_safe_m=internal_clearance_safe_m, w_internal_clearance=w_internal_clearance)

    def new_search(self, *, seed: int) -> FleetMCTSSearch:
        need(type(seed) is int and seed >= 0, 'EXPLICIT_VALID_SEED')
        return FleetMCTSSearch(transition_model=self.transition, reward_model=self.reward,
                               action_provider=self.transition.active_joint_actions,
                               budget=64, max_depth=8, c_uct=1.4, gamma=0.99, seed=seed)

    def search(self, searcher: FleetMCTSSearch, state: FleetState):
        need(searcher.transition is self.transition and searcher.reward is self.reward
             and searcher.action_provider == self.transition.active_joint_actions, 'SEARCH_BINDING_DRIFT')
        need((searcher.budget, searcher.max_depth, searcher.c_uct, searcher.gamma) == (64, 8, 1.4, 0.99), 'SEARCH_CONFIG_DRIFT')
        actions = self.transition.active_joint_actions(state)
        need(bool(actions), 'NO_SEARCH_AFTER_TASK_OR_HARD_TERMINATION')
        chosen, diagnostics = searcher.search(state)
        ids = [action_id(a) for a in actions]
        need(action_id(chosen) in ids, 'SEARCH_ACTION_NOT_FEASIBLE')
        need(set(diagnostics['visits']).issubset(ids) and set(diagnostics['q_values']) == set(diagnostics['visits']),
             'DIAGNOSTIC_ACTION_DOMAIN')
        diagnostics = {**diagnostics, 'model_version': VERSION, 'active_joint_action_ids': ids,
                       'active_mask_16': [f'{i//4},{i%4}' in ids for i in range(16)],
                       'terminal_action_constraints': {t: self.transition._vehicle_transitions[t].action_report(state.state_for(t))
                                                       for t in ('A', 'B')},
                       'missing_q_means': 'NOT_SEARCHED_OR_NOT_ADMISSIBLE_NOT_ZERO'}
        return chosen, diagnostics

    def advance(self, state: FleetState, action: JointAction):
        nxt, detail = self.transition.step_with_diagnostics(state, action)
        value = self.reward.evaluate(state, nxt)
        need(math.isfinite(value), 'REWARD_NONFINITE')
        return nxt, value, detail


def episode_status(state: FleetState, executed_steps: int, max_steps: int = 128, *, hard_event_ever: bool) -> str:
    """This only classifies a validated candidate state; no control or resampling."""
    need(all(isinstance(v.state, DualOnlyState) for v in state.vehicles) and state.controlled_tokens == ('A', 'B'),
         'CANDIDATE_STATE_REQUIRED')
    need(type(executed_steps) is int and type(max_steps) is int and 0 <= executed_steps <= max_steps and max_steps > 0,
         'STEP_COUNTER')
    need(type(hard_event_ever) is bool, 'EXPLICIT_HISTORY_FLAG_REQUIRED')
    if hard_event_ever or state.hard_safety_violation:
        return 'EXECUTED_HARD_SAFETY_TERMINAL'
    need(math.isfinite(state.minimum_internal_clearance_m) and state.minimum_internal_clearance_m >= 0,
         'GEOMETRY_EVIDENCE_REQUIRED_FOR_NONFAILURE_STATUS')
    need(state.state_for('A').time_s == state.state_for('B').time_s, 'STATUS_CLOCKS_DIFFER')
    if state.all_goals_reached:
        return 'BOTH_PARKED_AT_OWN_DESTINATIONS'
    if executed_steps == max_steps:
        return 'EVALUATION_CAP_NOT_TASK_TERMINAL'
    return 'RUNNING'
