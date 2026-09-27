"""256-cell frozen Coverage32 continuation plumbing derived from the cloud-validated technical runner.

Only header/scope/spec admission is changed. Frozen dynamics, search, reward,
return arithmetic and per-step chain remain unchanged. No label decisions or training.
The immutable schedule's runtime_authorized=False records its static origin;
actual runtime permission comes from the separate batch START and seed lease.
"""
from __future__ import annotations
import hashlib
import json
import math
import os
from pathlib import Path
import random
import time
import traceback

SCHEMA = 'DUAL_STOP_COVERAGE32_NEW16_WINDOW64_CELL_V1'
ORDER = [f'{i},{j}' for i in range(4) for j in range(4)]
TERMINALS = ('BOTH_PARKED_AT_OWN_DESTINATIONS', 'EXECUTED_HARD_SAFETY_TERMINAL')
CAP = 'EVALUATION_CAP_NOT_TASK_TERMINAL'


def need(ok, reason):
    if not ok:
        raise RuntimeError(reason)


def canonical(x):
    return (json.dumps(x, sort_keys=True, ensure_ascii=False, separators=(',', ':'),
                       allow_nan=False) + '\n').encode('utf-8')


def sha(x):
    return hashlib.sha256(x).hexdigest()


def objsha(x):
    return sha(canonical(x))


def strict_json(b):
    def pairs(items):
        d = {}
        for k, v in items:
            need(k not in d, 'DUPLICATE_JSON_KEY:' + k)
            d[k] = v
        return d
    def bad(v):
        raise ValueError('NONFINITE_JSON:' + v)
    x = json.loads(b, object_pairs_hook=pairs, parse_constant=bad)
    def walk(v):
        if isinstance(v, float):
            need(math.isfinite(v), 'NONFINITE_JSON_FLOAT')
        elif isinstance(v, dict):
            for vv in v.values(): walk(vv)
        elif isinstance(v, list):
            for vv in v: walk(vv)
    walk(x)
    return x


def read(p):
    return strict_json(Path(p).read_bytes())


def write(p, x):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('xb') as f:
        f.write(x if isinstance(x, bytes) else canonical(x))
        f.flush(); os.fsync(f.fileno())


def rng_json(agent):
    return strict_json(canonical(agent.rng.getstate()))


def tuplify(x):
    return tuple(tuplify(y) for y in x) if isinstance(x, list) else x


def saved_status(state, steps, cap):
    need(type(steps) is int and type(cap) is int and 0 < cap <= 128 and 0 <= steps <= cap,
         'INVALID_STEP_OR_CAP')
    cars = state['vehicles']
    need(set(cars) == {'A', 'B'}, 'STATE_TOKENS')
    if state['internal_collision'] or state['internal_safety_violation'] or any(cars[t]['collision'] for t in cars):
        return TERMINALS[1]
    if all(cars[t]['goal_reached'] for t in cars):
        for v in cars.values():
            lo, hi = v['goal_window_m']
            need(lo <= v['route_s'] <= hi and v['speed_mps'] == 0, 'FALSE_PARKED_SUCCESS')
        return TERMINALS[0]
    return CAP if steps == cap else 'RUNNING'


def return_summary(rows, outcome, cap):
    need(outcome in TERMINALS + (CAP,) and 0 < len(rows) <= cap, 'INCOMPLETE_RETURN')
    need(all(type(r['reward']) in (int, float) and math.isfinite(r['reward']) for r in rows), 'BAD_REWARD')
    value = math.fsum((.99 ** i) * r['reward'] for i, r in enumerate(rows))
    terminal = outcome in TERMINALS
    return {'executed_steps': len(rows), 'maximum_outer_steps': cap,
            'discount_gamma': .99, 'discount_origin': 'forced_first_transition_k0',
            'finite_window_return': value,
            'full_task_return': value if terminal else None,
            'tail_censored': not terminal, 'bootstrapped_tail': None,
            'outcome': outcome, 'task_terminal': terminal,
            'teacher_sample': True, 'training_mask': 0,
            'scope': 'COVERAGE32_NEW16_WINDOW64_OBSERVATION_PENDING_REVIEW',
            'cap_note': '128 fresh outer steps from each selected root; censored tail is unknown.'}


def verify_diag(d, selected, seed, ids):
    need(d['iterations'] == 64 and d['seed'] == seed, 'SEARCH_BUDGET_SEED')
    need(d['active_joint_action_ids'] == ids and d['active_mask_16'] == [a in ids for a in ORDER], 'SEARCH_DOMAIN')
    need(set(d['visits']) == set(d['q_values']) == set(ids), 'SEARCH_COVERAGE')
    need(all(type(n) is int and n > 0 for n in d['visits'].values()) and sum(d['visits'].values()) == 64,
         'VISIT_ACCOUNTING')
    need(all(math.isfinite(v) for v in d['q_values'].values()), 'NONFINITE_Q')
    best = max(ids, key=lambda a: (d['visits'][a], d['q_values'][a], tuple(-int(v) for v in a.split(','))))
    need(selected == best, 'NATIVE_CHOICE_RULE')


def reward_check(bc, before, after, reward):
    """Recompute the bound dual-only scalar formula, without using evaluate()."""
    cfg = bc.context['reward_config']; fc = bc.context['fleet_config']
    vehicle_parts = {}; total = 0.0
    for t in ('A', 'B'):
        p, n = before['vehicles'][t], after['vehicles'][t]
        if p['goal_reached']:
            vehicle_parts[t] = {'parked_before': True, 'subtotal': 0.0}
            continue
        progress = cfg['w_progress'] * (max(0., n['route_s'] - p['route_s']) /
                                        max(p['target_speed_mps'] * .5, cfg['eps']))
        speed = cfg['w_speed'] * (-abs(n['speed_mps'] - n['target_speed_mps']) /
                                   max(n['target_speed_mps'], cfg['eps']))
        comfort = cfg['w_comfort'] * (-(abs(n['accel_mps2'] - p['accel_mps2']) / .5) / 10.)
        need(n['external_lead'] == {'mode':'NONE', 'distance_m':None, 'relative_speed_mps':None}
             and n['minimum_external_clearance_m'] is None, 'REWARD_DUAL_ONLY_SCOPE')
        subtotal = progress + speed + 0.0 + comfort
        bonus = cfg['goal_bonus'] if n['goal_reached'] else 0.0
        total += subtotal
        total += bonus
        vehicle_parts[t] = {'progress':progress,'speed':speed,'safety':0.0,'comfort':comfort,
                            'goal_bonus':bonus,'subtotal':subtotal + bonus}
    risk = max(0., min(1., (fc['internal_clearance_safe_m'] - after['minimum_internal_clearance_m']) /
                          fc['internal_clearance_safe_m']))
    clearance = -fc['w_internal_clearance'] * risk * risk
    hard = saved_status(after, 0, 128) == TERMINALS[1]
    penalty = -cfg['collision_penalty'] if hard else 0.0
    expected = total / 2.0 + clearance + penalty
    error = abs(expected - reward)
    need(error <= 1e-10 * max(1., abs(expected), abs(reward)), 'SCALAR_REWARD_PARITY')
    return {'vehicles':vehicle_parts,'vehicle_denominator':2,
            'internal_clearance':clearance,'hard_penalty':penalty,
            'recomputed_total':expected,'native_total':reward,'absolute_error':error}


def validate_spec(root, spec):
    from coverage32_spec import check_spec
    return check_spec(root, spec)


def verify_cell(directory, spec):
    """Read only complete cells. A missing COMMIT is NEVER a completed sample."""
    td = Path(directory)
    start = read(td/'CELL_START.json'); need(start['spec'] == spec,'CELL_SPEC')
    need(start['technical_only'] is False and start['teacher_sample'] is True and start['batch_execution_authorized'] is True,'CELL_SCOPE')
    need((td/'RC.txt').read_text().strip() == '0','CELL_RC')
    state, rng = start['initial'], start['rng_initial']
    need(objsha(state) == spec['root_state_sha256'],'CELL_ROOT_SHA')
    need(rng == strict_json(canonical(random.Random(spec['rng_seed']).getstate())), 'CELL_INITIAL_SEED')
    files = sorted((td/'steps').glob('*.json')); rows=[]; searches=0
    for k, path in enumerate(files):
        need(path.name == f'{k:04d}.json','CELL_STEP_GAP')
        r = read(path)
        need(r['step_index'] == k and r['cell_id'] == spec['cell_id'],'CELL_ROW_ID')
        need(r['before'] == state and r['rng_before'] == rng,'CELL_STATE_RNG_CHAIN')
        need(r['before_sha256'] == objsha(state) and r['after_sha256'] == objsha(r['after']),'CELL_STATE_SHA')
        need(r['rng_before_sha256'] == objsha(rng) and r['rng_after_sha256'] == objsha(r['rng_after']), 'CELL_RNG_SHA')
        need(r['active_mask_16'] == [x in r['active_ids'] for x in ORDER] and r['action_id'] in r['active_ids'], 'CELL_MASK')
        if k == 0:
            need(r['selection'] == 'FORCED_FIRST' and r['diagnostics'] is None and
                 r['action_id'] == spec['first_action_id'] and r['rng_after'] == rng,'FORCED_FIRST_ACCOUNTING')
        else:
            need(r['selection'] == 'NATIVE_B64_H8','FOLLOWUP_SELECTION')
            verify_diag(r['diagnostics'],r['action_id'],spec['rng_seed'],r['active_ids']); searches+=1
        need(saved_status(r['after'],k+1,spec['maximum_outer_steps']) == r['outcome_after_step'],'CELL_OUTCOME')
        if r['outcome_after_step'] != 'RUNNING':need(k == len(files)-1,'ROW_AFTER_TERMINAL')
        rows.append(r); state=r['after']; rng=r['rng_after']
    need(bool(rows),'EMPTY_CELL')
    summary=read(td/'SUMMARY.json')
    calculated=return_summary(rows,rows[-1]['outcome_after_step'],spec['maximum_outer_steps'])
    need(summary == {**calculated,'native_search_calls':searches,'initial':start['initial'], 'final':state,
                     'rng_final':rng,'spec':spec},'CELL_RETURN_SUMMARY')
    trace=read(td/'TRACE.json');need(trace == {'spec':spec,'rows':rows},'CELL_TRACE')
    commit=read(td/'COMMIT.json');need(commit['spec']==spec and commit['teacher_sample'] is True,'COMMIT_SCOPE')
    actual={p.relative_to(td).as_posix() for p in td.rglob('*') if p.is_file()}
    need(actual == set(commit['files'])|{'COMMIT.json'},'COMMIT_MEMBER_SET')
    for name,rec in commit['files'].items():
        p=Path(name);need(not p.is_absolute() and '..' not in p.parts and '\\' not in name,'COMMIT_PATH')
        b=(td/name).read_bytes();need(len(b)==rec['size'] and sha(b)==rec['sha256'],'COMMIT_SHA:'+name)
    events=[strict_json(b) for b in (td/'EVENTS.jsonl').read_bytes().splitlines() if b]
    need([e['seq'] for e in events] == list(range(len(events))), 'EVENT_SEQUENCE')
    saved=[e for e in events if e['event']=='STEP_SAVED']
    need(len(saved)==len(rows) and [e['step_index'] for e in saved]==list(range(len(rows))), 'STEP_EVENT_ACCOUNTING')
    for e,path in zip(saved,files):need(e['sha256']==sha(path.read_bytes()),'EVENT_STEP_SHA')
    need(sum(e['event']=='SEARCH_STARTED' for e in events)==searches and
         sum(e['event']=='SEARCH_RETURNED' for e in events)==searches,'SEARCH_EVENT_ACCOUNTING')
    return summary


def run_cell(bc, root, spec, directory, counters, step_validator, deadline_context):
    """Exactly one forced admitted first action, then bounded pinned MCTS followups.

    Exposed only to the new coverage32 worker after its START/lease checks.
    A technical exception keeps immutable completed steps, no COMMIT, no final G.
    """
    from candidate_mcts.dual_stop_adapter_v1 import action_id, episode_status
    td=Path(directory)
    validate_spec(root, spec)
    need(not os.path.lexists(td),'CELL_EXISTS_NO_RETRY')
    initial=root['behavior_record']['state']
    state=bc.transition.unpack(initial)
    need(bc.transition.pack(state) == initial and objsha(initial)==spec['root_state_sha256'],'ROOT_CODEC_PARITY')
    active={action_id(a):a for a in bc.transition.active_joint_actions(state)}
    need(list(active)==root['admissible_action_ids'] and spec['first_action_id'] in active,'FORCED_ACTION_NOT_ADMITTED')
    td.mkdir(parents=True,exist_ok=False)
    agent=bc.system.new_search(seed=spec['rng_seed']); rng0=rng_json(agent)
    write(td/'CELL_START.json',{'spec':spec,'initial':initial,'rng_initial':rng0,
                              'technical_only':False,'teacher_sample':True,'batch_execution_authorized':True,'automatic_retry':False})
    rows=[];seq=0;current_step=0
    def event(kind,**data):
        nonlocal seq
        row={'seq':seq,'event':kind,**data}
        with (td/'EVENTS.jsonl').open('ab') as f:f.write(canonical(row));f.flush();os.fsync(f.fileno())
        seq+=1
    try:
        for k in range(spec['maximum_outer_steps']):
            current_step=k; before=bc.transition.pack(state); rb=rng_json(agent)
            need(saved_status(before,k,spec['maximum_outer_steps'])=='RUNNING','ADVANCE_AFTER_TERMINAL')
            active={action_id(a):a for a in bc.transition.active_joint_actions(state)}
            ids=list(active);need(ids,'EMPTY_RUNNING_ACTION_DOMAIN')
            if k==0:
                action=active[spec['first_action_id']];diag=None;select='FORCED_FIRST'
                event('FORCED_ACTION_SELECTED',step_index=k,action_id=spec['first_action_id'])
            else:
                event('SEARCH_STARTED',step_index=k,state_sha256=objsha(before),rng_before=rb)
                counters['search_started']+=1
                with deadline_context(60): action,diag=bc.system.search(agent,state)
                counters['search_returned']+=1
                diag=strict_json(canonical(diag));select='NATIVE_B64_H8'
                verify_diag(diag,action_id(action),spec['rng_seed'],ids)
                event('SEARCH_RETURNED',step_index=k,action_id=action_id(action),rng_after=rng_json(agent))
            ra=rng_json(agent)
            need(bc.transition.pack(state)==before,'SEARCH_MUTATED_ROOT')
            event('ADVANCE_STARTED',step_index=k,action_id=action_id(action),rng_after_search=ra)
            counters['outer_transitions_attempted']+=1
            with deadline_context(60): nxt,reward,detail=bc.system.advance(state,action)
            counters['outer_transitions_returned']+=1
            step_validator(bc,state,action,nxt,reward,detail)
            after=bc.transition.pack(nxt)
            need(bc.transition.pack(state)==before and rng_json(agent)==ra,'ADVANCE_MUTATED_INPUT_OR_RNG')
            breakdown=reward_check(bc,before,after,reward)
            outcome=episode_status(nxt,k+1,spec['maximum_outer_steps'],hard_event_ever=nxt.hard_safety_violation)
            need(outcome==saved_status(after,k+1,spec['maximum_outer_steps']),'STATUS_PARITY')
            row={'schema':SCHEMA,'cell_id':spec['cell_id'],'step_index':k,'before':before,'after':after,
                 'before_sha256':objsha(before),'after_sha256':objsha(after),
                 'rng_before':rb,'rng_after':ra,'rng_before_sha256':objsha(rb),'rng_after_sha256':objsha(ra),
                 'active_ids':ids,'active_mask_16':[x in ids for x in ORDER],
                 'selection':select,'action_id':action_id(action),'diagnostics':diag,
                 'reward':reward,'reward_breakdown_check':breakdown,'detail':detail,
                 'outcome_after_step':outcome,'teacher_sample':True,'training_mask':0}
            path=td/'steps'/f'{k:04d}.json';write(path,row)
            rows.append(row);event('STEP_SAVED',step_index=k,sha256=sha(path.read_bytes()))
            state=nxt
            if outcome != 'RUNNING': break
        summary={**return_summary(rows,rows[-1]['outcome_after_step'],spec['maximum_outer_steps']),
                 'native_search_calls':sum(r['selection']=='NATIVE_B64_H8' for r in rows),
                 'initial':initial,'final':bc.transition.pack(state),'rng_final':rng_json(agent),'spec':spec}
        write(td/'TRACE.json',{'spec':spec,'rows':rows});write(td/'SUMMARY.json',summary);write(td/'RC.txt',b'0\n')
        records={p.relative_to(td).as_posix():{'size':p.stat().st_size,'sha256':sha(p.read_bytes())}
                 for p in sorted(td.rglob('*')) if p.is_file()}
        write(td/'COMMIT.json',{'schema':SCHEMA,'spec':spec,'files':records,'teacher_sample':True})
        verify_cell(td,spec)
        counters['collection_cells_committed']+=1
        return summary
    except BaseException as exc:
        # No completed SUMMARY/COMMIT is invented for an interrupted cell.
        error={'status':'TECHNICAL_MISSING_COVERAGE32_CELL','type':type(exc).__name__,'reason':str(exc),
               'traceback':traceback.format_exc(),'attempted_step_index':current_step,
               'committed_step_count':len(rows),'committed_rows_reward_sum':math.fsum(r['reward']*.99**i for i,r in enumerate(rows)),
               'final_full_task_return':None,'teacher_sample':False,'training_mask':0,'automatic_resume':False}
        if not os.path.lexists(td/'ERROR.json'):write(td/'ERROR.json',error)
        if not os.path.lexists(td/'RC.txt'):write(td/'RC.txt',b'2\n')
        raise
