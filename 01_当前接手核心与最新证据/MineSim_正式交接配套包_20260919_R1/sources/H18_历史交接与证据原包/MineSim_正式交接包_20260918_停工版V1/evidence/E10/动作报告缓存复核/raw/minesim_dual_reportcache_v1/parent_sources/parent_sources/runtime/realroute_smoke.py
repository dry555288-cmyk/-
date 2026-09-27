"""Small route-bound NEW MODEL smoke; never a teacher/production runner.

Uses the latest CandidateRegression adapters verbatim. Native routes/legacy roots
are converted explicitly; old rollout labels are NOT used as expected new values.
The only complete toy trips are declared near-goal, scripted braking fixtures.
"""
from __future__ import annotations
import argparse
from contextlib import contextmanager
import dataclasses
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import signal
import sys
import time
import traceback


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


def canonical(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=False,
                       separators=(',', ':'), allow_nan=False) + '\n').encode('utf-8')


def pairs_unique(items):
    result = {}
    for k, v in items:
        need(k not in result, 'DUPLICATE_JSON_KEY:' + k)
        result[k] = v
    return result


def read(path):
    def invalid(value):
        raise ValueError('NONFINITE_JSON:' + value)
    return json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=pairs_unique,
                      parse_constant=invalid)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_new(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as f:
        f.write(canonical(obj))
        f.flush()
        os.fsync(f.fileno())


def load_definition(path, name, additions=None):
    ns = {'__name__': name, '__file__': str(path)}
    ns.update(additions or {})
    exec(compile(Path(path).read_bytes(), str(path), 'exec'), ns)
    return ns


@contextmanager
def bounded_call(seconds):
    """Operational limit only; no change to model time, dynamics or sampling."""
    def expired(signum, frame):
        raise TimeoutError('TECHNICAL_CALL_WALL_LIMIT')
    previous = signal.getsignal(signal.SIGALRM)
    signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


def jsonable(value):
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [jsonable(x) for x in value]
    if isinstance(value, float):
        need(math.isfinite(value), 'NONFINITE_LOG_VALUE')
    return value


def activate_package(package):
    package = Path(package).resolve()
    # Never shadow a loaded native/candidate module with another revision.
    for name, mod in list(sys.modules.items()):
        if name == 'candidate_mcts' or name.startswith('candidate_mcts.'):
            f = getattr(mod, '__file__', None)
            need(f is not None and (package / 'candidate_mcts') in Path(f).resolve().parents,
                 'PRELOADED_CANDIDATE_OUTSIDE_PACKAGE:' + name)
        if name == 'devkit' or name.startswith('devkit.'):
            f = getattr(mod, '__file__', None)
            need(f is not None and (package / 'engine') in Path(f).resolve().parents,
                 'PRELOADED_DEVKIT_OUTSIDE_PACKAGE:' + name)
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(package))
    sys.path.insert(1, str(package / 'engine'))
    from candidate_mcts.dual_stop_adapter_v1 import CandidateSystem, DualStopFleetTransition
    from candidate_mcts.dual_stop_motion_v1 import DestinationStopTransition, VERSION
    from candidate_mcts.fleet_state import FleetState
    from candidate_mcts.state import MCTSState
    from candidate_mcts.action_space import MCTSAction
    from candidate_mcts.fleet_search import active_joint_actions
    from devkit.sim_engine.planning.planner.mcts.geometry_transition_model import RouteGeometryCache
    from devkit.common.actor_state.vehicle_parameters import get_mine_truck_parameters
    import numpy
    import shapely
    return {'python': sys.version, 'numpy': numpy.__version__, 'shapely': shapely.__version__,
            'model_version': VERSION,
            'adapter_file': str(Path(sys.modules['candidate_mcts.dual_stop_adapter_v1'].__file__).resolve()),
            'motion_file': str(Path(sys.modules['candidate_mcts.dual_stop_motion_v1'].__file__).resolve()),
            'source_isolation': True, 'MCTS_calls': 0, 'state_transitions': 0}


class BoundContext:
    def __init__(self, package, context, *, counters):
        from shapely.geometry import LineString
        from devkit.common.actor_state.state_representation import StateSE2, ProgressStateSE2
        from devkit.common.actor_state.vehicle_parameters import get_mine_truck_parameters
        from devkit.common.actor_state.car_footprint import CarFootprint
        from devkit.sim_engine.planning.planner.mcts.geometry_transition_model import RouteGeometryCache
        from candidate_mcts.dual_stop_motion_v1 import DestinationStopTransition
        from candidate_mcts.dual_stop_adapter_v1 import CandidateSystem, DualStopFleetTransition
        from candidate_mcts.transition_model import TransitionConfig
        from candidate_mcts.reward import RewardConfig
        from candidate_mcts.fleet_state import FleetState
        from candidate_mcts.state import MCTSState
        from candidate_mcts.action_space import MCTSAction
        from candidate_mcts.fleet_search import active_joint_actions
        self.context = context
        self.api = {'FleetState': FleetState, 'MCTSState': MCTSState,
                    'MCTSAction': MCTSAction, 'active_joint_actions': active_joint_actions}
        self.codec = load_definition(package / 'definitions/frozen_codec.py', 'bound_legacy_codec')
        need(context['external_geometry_wrapper'] is False, 'BOUND_EXTERNAL_SCOPE_CHANGED')
        need(context['cache_grid_step_m'] == 1.0, 'CACHE_CONFIGURATION_CHANGED')
        need(context['root_defaults_from_source'] == {
            'minimum_clearance_m': '+inf', 'prev_action': None, 'collision': False,
            'goal_reached': False}, 'ROOT_DEFAULTS_SOURCE_CHANGED')
        refs = read(package / 'reference_paths.json')['reference_path']
        records = {r['token']: r for r in refs}
        need(len(records) == len(refs) == 18, 'REFERENCE_COUNT')
        ns = load_definition(package / 'definitions/route_helpers.py', 'bound_route_helpers',
                             {'records': records, 'math': math, 'LineString': LineString,
                              'ProgressStateSE2': ProgressStateSE2})
        start = time.perf_counter()
        lines = {t: ns['make_line'](context['route_tokens'][t]) for t in ('A', 'B')}
        self.paths = {t: ns['RouteAdapter'](lines[t]) for t in ('A', 'B')}
        self.goals = {t: float(lines[t].length) for t in ('A', 'B')}
        params = get_mine_truck_parameters(context['vehicle_location'])
        need((params.length, params.width, params.rear_axle_to_center) == (9., 4., 2.), 'FOOTPRINT_CONFIG_CHANGED')
        models, caches = {}, {}
        for t in ('A', 'B'):
            p = context['rear_start_pose'][t]
            car = CarFootprint.build_from_rear_axle(StateSE2(p['x'], p['y'], p['yaw']), params)
            caches[t] = RouteGeometryCache(self.paths[t], car, grid_step_m=1.0)
            models[t] = DestinationStopTransition(TransitionConfig(
                **context['transition_config'], goal_route_s=self.goals[t]))
        class CountedTransition(DualStopFleetTransition):
            def step_with_diagnostics(inner, state, action):
                counters['candidate_fleet_calls_including_tree_attempted'] += 1
                result = super().step_with_diagnostics(state, action)
                counters['candidate_fleet_calls_including_tree_returned'] += 1
                return result
        fc = context['fleet_config']
        self.transition = CountedTransition(models, caches, external_tokens=(), confirmed_dual_only=True,
            internal_collision_sample_dt_s=fc['internal_collision_sample_dt_s'],
            internal_safety_margin_m=fc['internal_safety_margin_m'])
        self.system = CandidateSystem(self.transition,
            {t: RewardConfig(**context['reward_config']) for t in ('A', 'B')},
            internal_clearance_safe_m=fc['internal_clearance_safe_m'],
            w_internal_clearance=fc['w_internal_clearance'])
        self.resolved = {'episode_uid': context['episode_uid'], 'route_tokens': context['route_tokens'],
            'route_lengths': self.goals, 'transition_config': {t: dataclasses.asdict(models[t].cfg) for t in models},
            'reward_config': context['reward_config'], 'fleet_config': fc,
            'goal_windows': {t: list(models[t].window) for t in models},
            'setup_elapsed_ms': 1000 * (time.perf_counter() - start),
            'cache_geometry_counts': {t: caches[t].geometry_count for t in caches},
            'geometry_cache_step_m': 1.0, 'traffic': 'EXPLICIT_AB_ONLY_NO_EXTERNAL_ACTOR',
            'road_free_space_status': 'HOLD_NOT_EVALUATED'}

    def restore(self, raw):
        need(raw['provenance'] == self.context['provenance'], 'RAW_EPISODE_IDENTITY')
        old = self.codec['make_root'](raw, self.api)
        before = canonical(self.codec['state_pack'](old))
        states, conversions = {}, {}
        for t in ('A', 'B'):
            states[t], conversions[t] = self.transition._vehicle_transitions[t].convert_legacy(
                old.state_for(t), confirmed_dual_only=True, external_tokens=())
            for key in ('route_s', 'speed_mps', 'time_s', 'accel_mps2', 'target_speed_mps', 'prev_action'):
                need(getattr(states[t], key) == getattr(old.state_for(t), key), 'ROOT_KINEMATICS_CHANGED:' + key)
        new = self.transition.bind_initial_geometry(self.api['FleetState'].from_states(states.items()))
        need(canonical(self.codec['state_pack'](old)) == before, 'OLD_ROOT_MUTATED')
        return new, {'vehicles': conversions, 'legacy_snapshot': self.codec['state_pack'](old),
                     'old_bytes_not_overwritten': True, 'model_change_not_old_trajectory_replay': True}


def verify_step(bc, before, action, after, reward, detail):
    """Internal contract checks, not an independent physical-safety certificate."""
    from candidate_mcts.action_space import ACTION_ACCEL
    m = bc.transition
    need(math.isfinite(reward), 'NONFINITE_REWARD')
    need(canonical(m.pack(m.unpack(m.pack(after)))) == canonical(m.pack(after)), 'NEW_CODEC_ROUNDTRIP')
    samples = detail['collision_samples']
    need(len(samples) == 6 and samples[0]['offset_s'] == 0 and samples[-1]['offset_s'] == .5, 'COLLISION_SAMPLE_CLOCK')
    for t in ('A', 'B'):
        x, y = before.state_for(t), after.state_for(t)
        need(y.time_s == x.time_s + .5, 'STEP_TIME')
        need(x.route_s <= y.route_s <= bc.goals[t] and 0 <= y.speed_mps <= 15, 'STEP_STATE_BOUND')
        need(y.lead_distance_m == math.inf and y.lead_rel_speed_mps == 0 and not y.collision, 'PHANTOM_LEAD_REINTRODUCED')
        model = m._vehicle_transitions[t]
        need(y.goal_reached == model.is_parked_position(y.route_s, y.speed_mps), 'FALSE_GOAL')
        for row in samples:
            s = math.fsum((x.route_s, model.profile(x, action.action_for(t)).at(row['offset_s']).distance_m))
            need(row['route_s'][t] == s, 'SAMPLED_POSITION_DIFFERENT_DYNAMICS')
        if x.goal_reached:
            need(action.action_for(t) == bc.api['MCTSAction'].KEEP and y.route_s == x.route_s and
                 y.speed_mps == 0 and y.parked_at_time_s == x.parked_at_time_s, 'PARKED_CAR_CHANGED')
        else:
            need(y.accel_mps2 == ACTION_ACCEL[action.action_for(t)], 'COMMAND_MEANING_CHANGED')
    need(before.state_for('A').time_s == before.state_for('B').time_s and
         after.state_for('A').time_s == after.state_for('B').time_s, 'CLOCKS_UNSYNCHRONIZED')
    need(after.internal_collision == any(x['collision'] for x in samples), 'COLLISION_FLAG_MISMATCH')
    need(after.internal_safety_violation == any(x['safety_violation'] for x in samples), 'SAFETY_FLAG_MISMATCH')
    need(after.minimum_internal_clearance_m == min(x['minimum_clearance_m'] for x in samples), 'MINIMUM_CLEARANCE_MISMATCH')


def run_smoke(package, output, *, synthetic_fixture=False, context_factory=BoundContext):
    from candidate_mcts.action_space import MCTSAction
    from candidate_mcts.joint_action import JointAction
    from candidate_mcts.dual_stop_adapter_v1 import action_id, episode_status
    from candidate_mcts.dual_stop_motion_v1 import DualOnlyState, VERSION
    output = Path(output)
    need(not os.path.lexists(output), 'SMOKE_OUTPUT_EXISTS_NO_RETRY')
    output.mkdir()
    counters = {'actions_considered': 0, 'one_step_transitions': 0, 'rejected_initial_actions': 0,
                'search_started': 0, 'search_returned': 0, 'search_outer_steps': 0,
                'scripted_goal_outer_steps': 0, 'candidate_fleet_calls_including_tree_attempted': 0,
                'candidate_fleet_calls_including_tree_returned': 0}
    def progress(stage, done, total):
        row = {'stage': stage, 'completed': done, 'total': total, 'counts': dict(counters)}
        with (output / 'PROGRESS.jsonl').open('ab') as f:
            f.write(canonical(row)); f.flush()
        print(json.dumps(row, ensure_ascii=False), flush=True)
    contexts, roots = {}, {}
    binding_rows = read(package / 'ROOT_BINDINGS.json')['roots']
    protocol = read(package / 'SMOKE_PROTOCOL.json')
    try:
        need(len(binding_rows) == 12 and [r['pilot_id'] for r in binding_rows] == protocol['root_order'], 'ROOT_SCHEDULE_MISMATCH')
        for index, b in enumerate(binding_rows):
            context_file, raw_file = package / b['context_path'], package / b['raw_path']
            need(digest(context_file) == b['context_sha256'] and digest(raw_file) == b['record_sha256'], 'SOURCE_SHA_MISMATCH')
            ep = b['episode_uid']
            if ep not in contexts:
                progress('CONTEXT_BUILD_STARTED', len(contexts), 6)
                with bounded_call(protocol['limits']['per_search_or_context_wall_seconds']):
                    contexts[ep] = context_factory(package, read(context_file), counters=counters)
                write_new(output / 'contexts' / (ep + '.json'), contexts[ep].resolved)
            bc = contexts[ep]
            raw = read(raw_file)
            raw_sha = digest(raw_file)
            state, conversion = bc.restore(raw)
            need(not state.hard_safety_violation and not state.all_goals_reached, 'INITIAL_ROOT_NOT_ELIGIBLE:' + b['pilot_id'])
            roots[b['pilot_id']] = (state, bc)
            before = bc.transition.pack(state)
            active = {action_id(a): a for a in bc.transition.active_joint_actions(state)}
            rows = []
            for i in range(16):
                aid = f'{i//4},{i%4}'
                counters['actions_considered'] += 1
                if aid not in active:
                    counters['rejected_initial_actions'] += 1
                    rows.append({'action_id': aid, 'allowed': False, 'q_value': None,
                                 'meaning': 'REJECTED_BY_TERMINAL_CONSTRAINT_NOT_ZERO_Q'})
                    continue
                nxt, reward, detail = bc.system.advance(state, active[aid])
                counters['one_step_transitions'] += 1
                verify_step(bc, state, active[aid], nxt, reward, detail)
                rows.append({'action_id': aid, 'allowed': True, 'after': bc.transition.pack(nxt),
                             'reward': reward, 'detail': detail,
                             'outcome': episode_status(nxt, 1, 128, hard_event_ever=nxt.hard_safety_violation)})
            need(bc.transition.pack(state) == before and digest(raw_file) == raw_sha, 'ROOT_OR_RAW_CHANGED')
            write_new(output / 'one_step' / (b['pilot_id'] + '.json'),
                      {'root_id': b['pilot_id'], 'raw_sha256': raw_sha, 'conversion': conversion,
                       'initial': before, 'active_ids': list(active), 'rows': rows,
                       'not_expected_equal_to_legacy': True})
            progress('TWELVE_ROOT_ACTION_CHECKS', index + 1, 12)
        need(counters['actions_considered'] == 192, 'ACTION_CHECK_COUNT')
        # Short recurrent search; each task has its own fixed RNG, not re-seeded at step 2.
        for index, task in enumerate(protocol['search_tasks']):
            state, bc = roots[task['root_id']]
            agent = bc.system.new_search(seed=task['technical_seed'])
            rows = []
            for step in range(task['maximum_outer_steps']):
                if state.hard_safety_violation or state.all_goals_reached:
                    break
                before = bc.transition.pack(state)
                rng_before = jsonable(agent.rng.getstate())
                counters['search_started'] += 1
                progress('NATIVE_SEARCH_STARTED', counters['search_returned'], protocol['search_calls_upper_bound'])
                started = time.perf_counter()
                with bounded_call(protocol['limits']['per_search_or_context_wall_seconds']):
                    action, diag = bc.system.search(agent, state)
                counters['search_returned'] += 1
                elapsed = (time.perf_counter() - started) * 1000
                rng_after_search = jsonable(agent.rng.getstate())
                need(sum(diag['visits'].values()) == 64 and diag['iterations'] == 64, 'NATIVE_SEARCH_BUDGET')
                need(all(math.isfinite(v) for v in diag['q_values'].values()), 'NONFINITE_Q')
                need(set(diag['visits']) == set(diag['active_joint_action_ids']), 'ROOT_ACTION_COVERAGE')
                nxt, reward, detail = bc.system.advance(state, action)
                counters['search_outer_steps'] += 1
                verify_step(bc, state, action, nxt, reward, detail)
                need(jsonable(agent.rng.getstate()) == rng_after_search, 'OUTER_TRANSITION_CONSUMED_SEARCH_RNG')
                row = {'step_index': step, 'before': before, 'after': bc.transition.pack(nxt),
                       'action_id': action_id(action), 'diagnostics': jsonable(diag),
                       'wrapper_search_elapsed_ms': elapsed, 'reward': reward, 'detail': detail,
                       'rng_before': rng_before, 'rng_after_search': rng_after_search,
                       'technical_window_not_task_timeout': True}
                rows.append(row)
                write_new(output / 'searches' / f'{index:02d}_step{step}.json', row)
                state = nxt
            write_new(output / 'searches' / f'{index:02d}_SUMMARY.json',
                      {'task': task, 'returned_steps': len(rows), 'final': bc.transition.pack(state),
                       'end_reason': episode_status(state, len(rows), 128, hard_event_ever=state.hard_safety_violation)
                       if state.hard_safety_violation or state.all_goals_reached else 'TECHNICAL_WINDOW_END',
                       'teacher_sample': False})
            progress('THREE_SHORT_SEARCH_TASKS', index + 1, len(protocol['search_tasks']))
        # 6 role-symmetric controlled fixtures: two steps; one car stops at step 1,
        # holds its footprint at step 2 while the second stops. Not MCTS success.
        for index, task in enumerate(protocol['scripted_goal_tasks']):
            bc = contexts[task['episode_uid']]
            cars = {}
            first = task['first_stopper']
            for t in ('A', 'B'):
                v = task['first_v0'] if t == first else task['second_v0']
                s = bc.goals[t] - v*v/6.0 - task['target_remaining_at_stop_m']
                cars[t] = DualOnlyState(time_s=0., route_s=s, speed_mps=v, accel_mps2=0.,
                    lead_distance_m=math.inf, lead_rel_speed_mps=0., target_speed_mps=10.5)
            state = bc.transition.bind_initial_geometry(bc.api['FleetState'].from_states(cars.items()))
            need(not state.hard_safety_violation, 'SCRIPTED_INITIAL_GEOMETRY_FAILED')
            initial = bc.transition.pack(state)
            rows = []
            for step in range(2):
                need(not state.all_goals_reached and not state.hard_safety_violation, 'SCRIPTED_PREMATURE_TERMINAL')
                action = JointAction.from_pairs((t, MCTSAction.KEEP if state.state_for(t).goal_reached else MCTSAction.BRAKE)
                                               for t in ('A', 'B'))
                before = bc.transition.pack(state)
                nxt, reward, detail = bc.system.advance(state, action)
                counters['scripted_goal_outer_steps'] += 1
                verify_step(bc, state, action, nxt, reward, detail)
                need(not nxt.hard_safety_violation, 'SCRIPTED_PARKING_GEOMETRY_FAILED')
                rows.append({'step_index': step, 'before': before, 'after': bc.transition.pack(nxt),
                             'action_id': action_id(action), 'reward': reward, 'detail': detail})
                if step == 0:
                    second = 'B' if first == 'A' else 'A'
                    need(nxt.state_for(first).goal_reached and not nxt.state_for(second).goal_reached,
                         'SCRIPTED_FIRST_STOPPER_MISMATCH')
                state = nxt
            need(state.all_goals_reached, 'SCRIPTED_BOTH_NOT_PARKED')
            write_new(output / 'scripted_goals' / f'{index:02d}.json',
                      {'task': task, 'synthetic_near_goal_fixture': True, 'scripted_actions_not_search': True,
                       'initial': initial, 'rows': rows, 'final_outcome': episode_status(state, 2, 128, hard_event_ever=False)})
            progress('SIX_SCRIPTED_PARK_AND_WAIT', index + 1, 6)
        need(counters['search_started'] == counters['search_returned'] <= 6, 'SEARCH_ACCOUNTING')
        need(counters['scripted_goal_outer_steps'] == 12, 'SCRIPTED_COUNT')
        result = {'status': 'PASS_REAL_ROUTE_CANDIDATE_TECHNICAL_SMOKE_ONLY', 'model_version': VERSION,
                  'synthetic_fixture_only': synthetic_fixture, 'counts': counters,
                  'new_teacher_samples': 0, 'training_run': False, 'production_patch_installed': False,
                  'road_free_space_status': 'HOLD', 'Controller_KBM_run': False,
                  'C11_deadlock_solved': 'NOT_EVALUATED',
                  'geometry_scope': '0.1s_SAMPLED_AB_WITH_INHERITED_1m_CACHE_NOT_CONTINUOUS_CERTIFICATE'}
        write_new(output / 'RESULT.json', result)
        return result
    except (Exception, KeyboardInterrupt) as exc:
        write_new(output / 'ERROR.json', {'type': type(exc).__name__, 'reason': str(exc),
                  'traceback': traceback.format_exc(), 'counters': counters, 'automatic_retry': False})
        raise


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--package', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--probe-only', action='store_true')
    args = ap.parse_args()
    p = Path(args.package).resolve()
    try:
        info = activate_package(p)
        if args.probe_only:
            write_new(Path(args.output), info)
            print('IMPORT_ONLY_PASS; NO_MCTS; NO_STATE_TRANSITIONS', flush=True)
            return 0
        need(os.environ.get('MINESIM_DUALSTOP_SCOPE') == 'DUAL_ONLY_REAL_ROUTE_CANDIDATE_SMOKE', 'EXPLICIT_TECHNICAL_SCOPE_REQUIRED')
        result = run_smoke(p, Path(args.output))
        print(json.dumps(result), flush=True)
        return 0
    except (Exception, KeyboardInterrupt):
        traceback.print_exc()
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
