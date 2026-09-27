#!/usr/bin/env python3
"""Review exported MineSim records locally; never import or run experiment code.

This checks only captured bytes and record consistency. It does not certify
uncaptured trajectories, physical safety, ranking labels, or retry permission.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path, PurePosixPath


def read_json(path):
    def unique(pairs):
        ans = {}
        for k, v in pairs:
            if k in ans:
                raise ValueError('Duplicate JSON key: ' + k)
            ans[k] = v
        return ans
    def nonfinite(x):
        raise ValueError('Nonfinite JSON number: ' + x)
    return json.loads(Path(path).read_bytes(), object_pairs_hook=unique,
                      parse_constant=nonfinite)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def safe_member(root, name):
    rel = PurePosixPath(name)
    if rel.is_absolute() or '..' in rel.parts or '\\' in name:
        raise ValueError('Unsafe member: ' + name)
    p = root / name
    if p.is_symlink() or not p.resolve().is_relative_to(root.resolve()):
        raise ValueError('Escaping/symlink member: ' + name)
    return p


def review(root):
    checks = []
    def check(name, condition, **details):
        checks.append(dict(name=name, passed=bool(condition), **details))
    def match(p, rec):
        return p.is_file() and p.stat().st_size == rec['size'] and sha(p) == rec['sha256']
    export = read_json(root / 'RESULT.json')
    manifest = read_json(root / 'EXPORT_MANIFEST.json')
    check('export_manifest', all(match(safe_member(root, n), r) for n,r in manifest.items()), entries=len(manifest))
    capture = read_json(root / 'SOURCE_CAPTURE_MANIFEST.json')
    check('all_104_source_copies', len(capture) == export['copied_files'] == export['expected_files'] == 104)
    check('source_capture_integrity_and_stability', all(
        match(safe_member(root, r['archive_member']), r) and all(r[k] is True for k in
        ('full_file','stable_during_read','stable_through_capture','matches_prior_inventory')) for r in capture))
    check('export_scope', export['status'] == 'PASS_LOCATED_RECORDS_EXPORTED_ONLY' and export['experiments_run'] == 0 and export['signals_sent'] == 0 and export['issues'] == [] and export['fatal'] is None)
    data = root / 'sources/data'
    stages = ('minesim_discovery_remaining390_parallel_v1',
              'minesim_discovery_cell377_tail_continuation_v1',
              'minesim_confirmation768_parallel_v1')
    subset_reports = {}
    stage_reports = {}
    for stage in stages:
        p = data / stage
        original_manifest = read_json(p / 'MANIFEST.json')
        available = {n: r for n, r in original_manifest.items() if safe_member(p, n).is_file()}
        check(stage + ':original_manifest_captured_subset', all(match(safe_member(p, n), r) for n, r in available.items()), present=len(available), total_entries=len(original_manifest))
        subset_reports[stage] = dict(present_entries=len(available), original_entries=len(original_manifest), full_original_archive_reverified=False)
        result, start, cap = (read_json(p / f) for f in ('RESULT.json','START.json','CAPTURE.json'))
        check(stage + ':RC', (p / 'RC.txt').read_text().strip() == '0')
        pre, post = (read_json(p / f) for f in ('PREFLIGHT.json','POSTCHECK.json'))
        check(stage + ':saved_git_snapshot_unchanged', pre['git'] == post['git'])
        check(stage + ':no_retry_training_pruning', result['automatic_retry'] is False and result['automatic_resume'] is False and result['training_started'] is False and result['pruning_started'] is False)
        stage_reports[stage] = dict(status=result['status'], start=start, capture=cap,
                                   source_result='sources/data/' + stage + '/RESULT.json')
        if stage == stages[1]:
            continue
        audit, schedule = (read_json(p / f) for f in ('COLLECTION_AUDIT.json','SCHEDULE.json'))
        n = 390 if stage == stages[0] else 768
        known = {x['cell_id']: x for x in schedule}
        rows = audit['cells']; audit_by_id = {x['cell_id']: x for x in rows}
        check(stage + ':schedule_audit_count_ids', len(known) == len(schedule) == len(audit_by_id) == len(rows) == n and set(known) == set(audit_by_id))
        check(stage + ':ordinal_identity', all(known[r['cell_id']]['ordinal'] == r['ordinal'] for r in rows))
        check(stage + ':committed_only', all(r['state'] == 'VERIFIED_COMMITTED' for r in rows) and audit['unstarted'] == audit['touched_unverified'] == 0 and not audit['verification_errors'] and not audit['progress_errors'])
        outcomes = dict(Counter(r['outcome'] for r in rows))
        check(stage + ':outcomes', outcomes == audit['outcomes'] == result['outcomes'])
        check(stage + ':forced_first_search_accounting', audit['new_transitions'] - audit['new_searches'] == n and all(audit[k] == result[k] for k in ('new_transitions','new_searches')))
        check(stage + ':declared_commit_hashes_match_original_manifest', all(
            original_manifest['parallel/cells/' + r['cell_id'] + '/COMMIT.json']['sha256'] == r['commit_sha256'] for r in rows), note='Metadata cross-check; uncaptured COMMIT bytes were not hashed.')
        worker_rows = []; assignments=[]
        for worker in range(4):
            wp = p / ('parallel/workers/worker_' + str(worker))
            wr = read_json(wp / 'RESULT.json')
            progress = [json.loads(x) for x in (wp / 'PROGRESS.jsonl').read_text().splitlines()]
            check(stage + ':worker_' + str(worker), wr['error'] is None and wr['current_cell'] is None and len(progress) == wr['assigned'] == len(wr['committed_ids']) and [x['cell_id'] for x in progress] == wr['committed_ids'])
            check(stage + ':worker_audit_' + str(worker), all(all(r[k] == audit_by_id[r['cell_id']][k] for k in ('cell_id','commit_sha256','ordinal','outcome')) for r in progress))
            worker_rows += progress; assignments.append(wr['assigned'])
        check(stage + ':worker_partition', len(worker_rows) == len({r['cell_id'] for r in worker_rows}) == n and {r['cell_id'] for r in worker_rows} == set(known))
        phase = read_json(p / 'parallel/PHASE_RESULT.json')
        check(stage + ':phase_complete', phase['worker_rc'] == [0,0,0,0] and phase['fault'] is None and phase['commit_files'] == n)
        auth = read_json(p / 'AUTHORIZATION.json')
        check(stage + ':runner_source_hash', sha(p / 'runner.py.txt') == auth['script_sha256'])
        sk = 'subset_schedule_sha256' if stage == stages[0] else 'schedule_sha256'
        check(stage + ':schedule_hash', sha(p / 'SCHEDULE.json') == auth[sk])
        stage_reports[stage].update(outcomes=outcomes, worker_assignments=assignments,
            new_searches=audit['new_searches'], new_transitions=audit['new_transitions'],
            by_scene={s:dict(Counter(r['outcome'] for r in rows if known[r['cell_id']]['scene'] == s)) for s in sorted({x['scene'] for x in schedule})})

    p = data / stages[1]; cell = p / 'cell'
    commit = read_json(cell / 'COMMIT.json'); trace = read_json(cell / 'trace.json')
    result = read_json(p / 'RESULT.json'); join = read_json(p / 'JOIN_VALIDATION.json')
    check('cell377:actual_COMMIT_files', all(match(safe_member(cell, n), r) for n,r in commit['files'].items()), entries=len(commit['files']))
    steps = trace['steps']; gamma = trace['policy_config']['gamma']
    check('cell377:steps_and_state_chain', len(steps) == 53 and [x['step_index'] for x in steps] == list(range(53)) and all(steps[i]['before'] == steps[i-1]['after'] for i in range(1,53)) and trace['initial_state'] == steps[0]['before'] and trace['final_state'] == steps[-1]['after'])
    check('cell377:forced_first_and_52_searches', [s['forced_action'] for s in steps] == [True] + [False]*52 and sum(s['decision'] is not None for s in steps) == trace['native_search_calls'] == 52)
    prefix = sum(gamma**i * s['reward'] for i,s in enumerate(steps[:20]))
    tail = sum(gamma**i * s['reward'] for i,s in enumerate(steps[20:]))
    total = sum(gamma**i * s['reward'] for i,s in enumerate(steps))
    check('cell377:return_sum_and_join', all(math.isclose(a,b,rel_tol=0,abs_tol=1e-10) for a,b in [(prefix,result['prefix_return']),(tail,result['tail_local_return']),(total,result['full_return']),(total,prefix+gamma**20*tail),(total,trace['finite_window_return']),(total,commit['finite_window_return'])]))
    raw_lines = (cell / 'events.jsonl').read_bytes().splitlines(keepends=True)
    events = [json.loads(x) for x in raw_lines]
    check('cell377:event_hash_chain', len(events) == 108 and all(x['sequence'] == i and x['previous_event_sha256'] == (None if i==0 else hashlib.sha256(raw_lines[i-1]).hexdigest()) for i,x in enumerate(events)))
    returned = [x['event']['row'] for x in events if x['event']['kind']=='STEP_RETURNED']
    check('cell377:events_match_trace', returned == steps)
    check('cell377:terminal_record', steps[-1]['terminal_flags'] == {'all_goals_reached':True,'hard_safety_violation':False} and commit['outcome'] == trace['outcome'] == result['outcome'] == 'BOTH_CONFIGURED_ROUTE_ENDS')
    final_speeds = {v['token']:float.fromhex(v['state']['speed_mps']) for v in trace['final_state']['vehicles']}
    stage_reports[stages[1]].update(preserved_steps=20,new_steps=33,total_steps=53,final_recorded_speeds_mps=final_speeds,
        full_return=total,return_join_error=total-prefix-gamma**20*tail,
        whole_sample_wall_status=trace['timing']['whole_sample_wall_status'])

    frozen = data / stages[2] / 'bundle/frozen'
    ledger = read_json(frozen / 'prior_DISCOVERY_LEDGER_768.json')
    obs = read_json(frozen / 'OBSERVATIONS_768.json')
    byid = {r['cell_id']:r for r in ledger}; byobs={r['cell_id']:r for r in obs}
    check('discovery:full_ledger_identity_768', len(ledger)==len(obs)==len(byid)==len(byobs)==768 and set(byid)==set(byobs) and {r['ordinal'] for r in ledger}==set(range(768)))
    check('discovery:ledger_observations_agree', all(all(byid[r['cell_id']][k]==r[k] for k in ('outcome','ordinal','root_id','action_id','seed','steps','searches','context_sha256')) and byid[r['cell_id']]['finite_window_return']==r['return'] for r in obs))
    segments=dict(Counter(r['collection_segment'] for r in ledger))
    check('discovery:segments', segments=={'ORIGINAL_SERIAL_PRESERVED':377,'PARALLEL_REMAINING390':390,'RECOVERED_PREFIX20_PLUS_TAIL33':1})
    audit390 = read_json(data / stages[0] / 'COLLECTION_AUDIT.json')
    check('discovery:ledger390_matches_audit', all(all(byid[r['cell_id']][k]==r[k] for k in ('commit_sha256','outcome','ordinal')) for r in audit390['cells']))
    check('discovery:joined377_hash_matches_ledger', byid[commit['cell_id']]['commit_sha256'] == sha(cell/'COMMIT.json') and byid[commit['cell_id']]['finite_window_return'] == total)
    freeze = read_json(frozen/'CANDIDATE_FREEZE.json')
    for key,fn in [('all_pairs_sha256','ALL_PAIRS_1440.json'),('candidate_file_sha256','DISCOVERY_CANDIDATES.json'),('observations_sha256','OBSERVATIONS_768.json'),('prior_ledger_sha256','prior_DISCOVERY_LEDGER_768.json'),('protocol_sha256','PROTOCOL.json')]:
        check('candidate_freeze:'+fn, sha(frozen/fn)==freeze[key])
    pairs=read_json(frozen/'ALL_PAIRS_1440.json');candidates=read_json(frozen/'DISCOVERY_CANDIDATES.json')
    check('candidate_freeze:273_of_1440_record_partition', len(pairs)==1440 and len(candidates)==freeze['candidate_count']==273 and candidates==[r for r in pairs if r['candidate_mask']==1])
    check('candidate_freeze:not_training_labels', all(r['training_mask']==0 and r['training_direction'] is None and r['certified'] is False for r in pairs))
    check('candidate_freeze:bound_before_confirmation', freeze['created_utc'] < stage_reports[stages[2]]['start']['at_utc'] and freeze['candidate_file_sha256']==read_json(data/stages[2]/'AUTHORIZATION.json')['candidate_sha256'])
    dcounts=dict(Counter(x['outcome'] for x in ledger));ccounts=stage_reports[stages[2]]['outcomes']
    combined=dict(Counter(dcounts)+Counter(ccounts))
    return dict(status='PASS_CAPTURED_RECORDS_AND_ACCOUNTING_ONLY' if all(x['passed'] for x in checks) else 'HOLD_LOCAL_RECORD_INCONSISTENCY',
        reviewed_at_utc=datetime.now(timezone.utc).isoformat(), checks=checks,
        checks_passed=sum(x['passed'] for x in checks),checks_total=len(checks),
        original_manifest_subsets=subset_reports,stages=stage_reports,
        discovery_segments=segments,discovery_outcomes=dcounts,confirmation_outcomes=ccounts,combined_outcomes=combined,
        discovery_candidates=273,candidate_by_scene=dict(Counter(r['scene'] for r in candidates)),
        discovery_pair_reasons=dict(Counter(r['reason'] for r in pairs)),
        uncaptured_confirmation_raw_cells=768,
        limits=['All 1536 raw trajectory files were NOT exported or independently recomputed.',
                'Most COMMIT hashes were compared as metadata, not from raw COMMIT bytes.',
                'No geometry/safety certification, final confirmation-label extraction, training, experiment, or retry authorization.'])


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--evidence-root',required=True,type=Path)
    ap.add_argument('--output',required=True,type=Path)
    args=ap.parse_args()
    report=review(args.evidence_root)
    with args.output.open('x',encoding='utf-8') as f:
        json.dump(report,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
    print(report['status'],str(report['checks_passed'])+'/'+str(report['checks_total']))
    for row in report['checks']:
        if not row['passed']:print('HOLD',row['name'])
    return 0 if report['status'].startswith('PASS_') else 2

if __name__=='__main__':
    raise SystemExit(main())
