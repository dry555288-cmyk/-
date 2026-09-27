"""Fixed paired policy continuation, using the unchanged H8-rebased candidate.
No teacher collection, training, fitted model, action-report cache, or repository patch.
Up to two frozen initial states x two arms x128 half-second decisions. One run only.
"""
from __future__ import annotations
from dataclasses import asdict
from pathlib import Path
import hashlib
import json
import math
import sys
import time
from verify_audit import verify, verify_rebase


def need(ok, why):
    if not ok:
        raise RuntimeError(why)


def canon(x):
    return (json.dumps(x, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)+'\n').encode()


def read(p):
    return json.loads(Path(p).read_bytes())


def write(p, obj):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('xb') as f:
        f.write(canon(obj))
        f.flush()


def tuples(x):
    return tuple(tuples(v) for v in x) if isinstance(x, list) else x


def clone(x):
    return json.loads(canon(x))


def semantic(d):
    return {k: v for k, v in d.items() if k not in ('elapsed_ms', 'reuse_accounting')}


def cold_parity(a, b):
    for key in ('before', 'after', 'action_id', 'reward', 'detail', 'rng_before', 'rng_after'):
        need(canon(a[key]) == canon(b[key]), 'COLD_NATIVE_PARITY:'+key)
    need(canon(semantic(a['diagnostics'])) == canon(semantic(b['diagnostics'])), 'COLD_DIAGNOSTICS')


def cpu_stat():
    for name in ('/sys/fs/cgroup/cpu.stat', '/sys/fs/cgroup/cpu/cpu.stat'):
        p = Path(name)
        if p.is_file():
            try:
                vals = dict((k, int(v)) for k, v in (r.split() for r in p.read_text().splitlines()))
                return {'path': name, 'values': vals}
            except (OSError, ValueError):
                pass
    return {'path': None, 'values': {}}


def percentile(x, p):
    need(x and all(math.isfinite(v) for v in x), 'INVALID_TIMES')
    s=sorted(x); t=(len(s)-1)*p; lo=int(t); hi=min(lo+1, len(s)-1)
    return s[lo]+(s[hi]-s[lo])*(t-lo)


def summarize(rows, outcome, initial, final, counts, wall, cpu, c0, c1):
    need(rows and outcome != 'RUNNING', 'UNFINISHED_POLICY')
    cpu_times=[r['timing']['full_system_search_cpu_ms'] for r in rows]
    wall_times=[r['timing']['full_system_search_wall_ms'] for r in rows]
    reuse=[r['diagnostics'].get('reuse_accounting', {}) for r in rows]
    vals=[v['minimum_clearance_m'] for r in rows for v in r['detail']['collision_samples']]
    visits_fresh=sum(r['diagnostics']['iterations'] for r in rows)
    return {'outcome': outcome, 'executed_steps':len(rows), 'model_seconds':len(rows)*.5,
      'initial_state':initial, 'final_state':final,
      'both_parked':outcome=='BOTH_PARKED_AT_OWN_DESTINATIONS',
      'hard_safety_terminal':outcome=='EXECUTED_HARD_SAFETY_TERMINAL',
      'cap':outcome=='EVALUATION_CAP_NOT_TASK_TERMINAL',
      'minimum_sampled_clearance_m':min(vals),
      'progress_m':{t:final['vehicles'][t]['route_s']-initial['vehicles'][t]['route_s'] for t in ('A','B')},
      'discounted_window_reward':math.fsum(.99**k*r['reward'] for k,r in enumerate(rows)),
      'full_task_reward':None if outcome=='EVALUATION_CAP_NOT_TASK_TERMINAL' else math.fsum(.99**k*r['reward'] for k,r in enumerate(rows)),
      'search_cpu_total_ms':math.fsum(cpu_times), 'search_wall_total_ms':math.fsum(wall_times),
      'search_cpu_mean_ms':math.fsum(cpu_times)/len(rows), 'search_wall_mean_ms':math.fsum(wall_times)/len(rows),
      'search_wall_p95_ms':percentile(wall_times,.95),
      'policy_recording_wall_seconds_including_audits_io':wall,
      'policy_recording_cpu_seconds_including_audits_io':cpu,
      'fresh_iterations_total':visits_fresh,
      'inherited_sample_contributions_total':sum(x.get('inherited_samples',0) for x in reuse),
      'tail_transitions_total':sum(x.get('tail_transitions',0) for x in reuse),
      'successful_promotions':sum(x.get('inherited_samples',0)>0 for x in reuse),
      'fallbacks_after_first':sum(i>0 and x.get('mode')=='FRESH_ROOT' for i,x in enumerate(reuse)),
      'fallback_reasons':[{'step':i,'reason':x.get('reason')} for i,x in enumerate(reuse) if i>0 and x.get('mode')=='FRESH_ROOT'],
      'max_retained_nodes':max([x.get('retained_nodes',0) for x in reuse] or [0]),
      'search_transition_calls_total':sum(r['search_transition_counts']['candidate_fleet_calls_including_tree_returned'] for r in rows),
      'transition_calls_search_plus_outer':counts,
      'cgroup_before':c0, 'cgroup_after':c1,
      'cgroup_delta':{k:c1['values'][k]-v for k,v in c0['values'].items() if k in c1['values']},
      'timing_scope':'Full system.search includes candidate sample capture, guards, tails, and stat rebuild; excludes full audit export, IO, initialization and external advance. Policy recording time reported separately, NOT a production latency.',
      'teacher_sample':False, 'training_mask':0, 'full_controller_kbm_tested':False}


def compare_pair(b, r):
    completed = b['both_parked'] and r['both_parked']
    safe = not b['hard_safety_terminal'] and not r['hard_safety_terminal']
    q = {'both_arms_complete':completed, 'no_hard_terminal_in_either':safe,
      'candidate_no_more_model_steps':r['executed_steps']<=b['executed_steps'] if completed else None,
      'candidate_total_search_cpu_lower':r['search_cpu_total_ms']<b['search_cpu_total_ms'] if completed else None,
      'candidate_total_search_wall_lower':r['search_wall_total_ms']<b['search_wall_total_ms'] if completed else None,
      'candidate_minimum_clearance_not_lower':r['minimum_sampled_clearance_m']>=b['minimum_sampled_clearance_m'] if completed else None,
      'cpu_total_change_percent':100*(r['search_cpu_total_ms']/b['search_cpu_total_ms']-1),
      'wall_total_change_percent':100*(r['search_wall_total_ms']/b['search_wall_total_ms']-1),
      'times_comparable_for_task_completion':completed,
      'scope':'Paired initial state and initial RNG; later states/actions/RNG may diverge. CAP or safety stop is not counted as a speed gain.'}
    q['strict_joint_improvement_observed_on_this_pair'] = bool(completed and safe and
        q['candidate_no_more_model_steps'] and q['candidate_total_search_cpu_lower'] and
        q['candidate_total_search_wall_lower'] and q['candidate_minimum_clearance_not_lower'])
    return q


def run(runtime, output, protocol, progress, *, local_test=False):
    runtime=Path(runtime); output=Path(output); output.mkdir(parents=True, exist_ok=False)
    need(protocol['max_search_calls']==512 and protocol['max_decisions_per_arm']==128 and len(protocol['root_ids'])==2,'FIXED_PROTOCOL')
    sys.dont_write_bytecode=True; sys.path.insert(0, str(runtime))
    import realroute_smoke as native
    imported=native.activate_package(runtime); write(output/'IMPORTS.json', imported)
    if not local_test:
        need(sys.version_info[:2]==(3,9), 'PYTHON_LINEAGE')
        expected=read(runtime/'EXPECTED_IMPORT.json')
        for key in ('numpy','shapely','model_version'):
            need(imported[key]==expected[key], 'IMPORT_DRIFT:'+key)
    import teacher_cell_core as core
    from candidate_mcts.dual_stop_adapter_v1 import action_id
    from subtree_reuse import HorizonRebasedSearch
    rows={r['root_id']:r for r in read(runtime/'inputs/SELECTED_NEW16.json')}
    counters=dict(search_started=0, search_completed=0, outer_steps_started=0, outer_steps_completed=0)
    cases=[]
    for ci,rid in enumerate(protocol['root_ids']):
        row=rows[rid]; history=read(runtime/'inputs/steps'/(rid+'.json'))
        need(canon(row['state'])==canon(history['before']) and history['forced_action'] is False, 'INPUT_BINDING')
        need(hashlib.sha256(canon(row['state'])).hexdigest()==row['exact_before_state_sha256'], 'ROOT_STATE_SHA')
        case=output/rid; case.mkdir(); summaries={}; first={}
        order=['baseline','rebased'] if ci==0 else ['rebased','baseline']
        for mode in order:
            arm=case/mode; arm.mkdir()
            tc=dict(candidate_fleet_calls_including_tree_attempted=0, candidate_fleet_calls_including_tree_returned=0)
            with native.bounded_call(90):
                bc=native.BoundContext(runtime, read(runtime/'inputs/contexts'/(row['task']['episode_uid']+'.json')), counters=tc)
            expected=read(runtime/'inputs/resolved'/(row['task']['task_id']+'.json'))
            trim=lambda x:{k:v for k,v in x.items() if k!='setup_elapsed_ms'}
            need(trim(bc.resolved)==trim(expected),'CONTEXT_DRIFT')
            state=bc.transition.unpack(row['state'])
            if mode=='baseline':
                agent=bc.system.new_search(seed=row['task']['seed'])
            else:
                def binding():
                    return canon({'context':bc.context,'goals':bc.goals,
                        'transitions':{t:asdict(bc.transition._vehicle_transitions[t].cfg) for t in ('A','B')},
                        'windows':{t:list(bc.transition._vehicle_transitions[t].window) for t in ('A','B')},
                        'rewards':{t:asdict(bc.system.reward._vehicle_rewards[t].cfg) for t in ('A','B')},
                        'clearance_safe':bc.system.reward.internal_clearance_safe_m,
                        'clearance_weight':bc.system.reward.w_internal_clearance,
                        'sample_dt':bc.transition.internal_collision_sample_dt_s,
                        'safety_margin':bc.transition.internal_safety_margin_m,
                        'geometry_identity':{t:id(bc.transition._route_geometry_caches[t]) for t in ('A','B')}})
                agent=HorizonRebasedSearch(transition_model=bc.transition,reward_model=bc.system.reward,
                    action_provider=bc.transition.active_joint_actions,budget=64,max_depth=8,c_uct=1.4,gamma=.99,
                    seed=row['task']['seed'],state_encode=bc.transition.pack,binding=binding)
            agent.rng.setstate(tuples(history['rng_before']))
            initial=bc.transition.pack(state); rr=[]; previous=None
            c0=cpu_stat(); wall0=time.perf_counter(); cpu0=time.process_time()
            outcome=core.saved_status(initial,0,128)
            need(outcome=='RUNNING','INITIAL_STATE_ALREADY_TERMINAL')
            for step in range(128):
                before=bc.transition.pack(state); rng0=core.rng_json(agent); tc0=dict(tc)
                counters['search_started']+=1
                progress('SEARCH_STARTED',counters,{'root_id':rid,'mode':mode,'step':step})
                started=time.perf_counter(); cput=time.process_time()
                with native.bounded_call(90):
                    action,diag=bc.system.search(agent,state)
                cpu_ms=(time.process_time()-cput)*1000; wall_ms=(time.perf_counter()-started)*1000
                counters['search_completed']+=1
                progress('SEARCH_RETURNED',counters,{'root_id':rid,'mode':mode,'step':step})
                rng1=core.rng_json(agent); search_tc={k:tc[k]-tc0[k] for k in tc}
                need(canon(before)==canon(bc.transition.pack(state)),'INPUT_MUTATION')
                checks=None
                if mode=='rebased':
                    audit=clone(agent.audit()); checks={'full':verify(audit,64),'accounting':clone(agent.last_meta)}
                    meta=agent.last_meta
                    need(meta['inherited_samples']+meta['new_iterations']==64 and meta['root_visit_count']==64,'ROOT_SUPPORT')
                    need(meta['child_visit_sum']+meta['root_only_sample_count']==64,'ROOT_EDGE_SUPPORT')
                    if agent.promotion_snapshot is not None:
                        prom=clone(agent.promotion_snapshot)
                        need(previous is not None,'PREVIOUS_AUDIT_REQUIRED')
                        checks['promotion']=verify(prom); checks['suffix']=verify_rebase(previous,prom)
                        write(arm/'promotions'/('%04d.json'%step), {'tree':prom,'checks':checks,
                            'rng_before':agent.promotion_rng_before,'rng_after':agent.promotion_rng_after})
                    write(arm/'trees'/('%04d.json'%step),audit); previous=audit
                    if step==0:
                        need(meta['inherited_samples']==0 and diag['iterations']==64,'COLD_SEARCH_REQUIRED')
                else:
                    need(diag['iterations']==64 and sum(diag['visits'].values())==64,'BASELINE_BUDGET')
                need(core.rng_json(agent)==rng1,'AUDIT_CHANGED_RNG')
                counters['outer_steps_started']+=1
                progress('OUTER_ADVANCE_STARTED',counters,{'root_id':rid,'mode':mode,'step':step})
                with native.bounded_call(90):
                    nxt,reward,detail=bc.system.advance(state,action)
                counters['outer_steps_completed']+=1
                progress('OUTER_ADVANCE_RETURNED',counters,{'root_id':rid,'mode':mode,'step':step})
                native.verify_step(bc,state,action,nxt,reward,detail)
                after=bc.transition.pack(nxt)
                reward_check=core.reward_check(bc,before,after,reward)
                need(core.rng_json(agent)==rng1,'ADVANCE_CHANGED_RNG')
                rec={'root_id':rid,'mode':mode,'step':step,'before':before,'after':after,
                    'action_id':action_id(action),'reward':reward,'detail':detail,'diagnostics':diag,
                    'rng_before':rng0,'rng_after':rng1,'search_transition_counts':search_tc,
                    'reward_formula_check':reward_check,'sample_rebase_check':checks,
                    'hard_safety_violation_after':nxt.hard_safety_violation,'both_parked_after':nxt.all_goals_reached,
                    'timing':{'full_system_search_cpu_ms':cpu_ms,'full_system_search_wall_ms':wall_ms,
                        'candidate_bookkeeping_included':mode=='rebased','audit_export_io_outer_advance_excluded':True},
                    'teacher_sample':False,'training_mask':0,'full_controller_kbm_tested':False}
                write(arm/'steps'/('%04d.json'%step),rec); rr.append(rec)
                if step==0:
                    saved=read(output.parent/'parent_sources'/'native'/rid/'baseline_0.json')
                    cold_parity(rec,saved); first[mode]=rec
                if mode=='baseline' and step==1:
                    cold_parity(rec,read(output.parent/'parent_sources'/'native'/rid/'baseline_1.json'))
                state=nxt
                outcome=core.saved_status(after,len(rr),128)
                progress('STEP_SAVED',counters,{'root_id':rid,'mode':mode,'step':step,'outcome':outcome})
                if outcome!='RUNNING':
                    break
            record_wall=time.perf_counter()-wall0; record_cpu=time.process_time()-cpu0; c1=cpu_stat()
            summary=summarize(rr,outcome,initial,bc.transition.pack(state),dict(tc),record_wall,record_cpu,c0,c1)
            write(arm/'SUMMARY.json',summary); summaries[mode]=summary
            progress('POLICY_SAVED',counters,{'root_id':rid,'mode':mode,'steps':len(rr),'outcome':outcome})
        cold_parity(first['baseline'],first['rebased'])
        result={'root_id':rid,'execution_order':order,'initial_rng_paired':True,'cold_first_decision_equal':True,
            'arms':summaries,'comparison':compare_pair(summaries['baseline'],summaries['rebased'])}
        write(case/'COMPARISON.json',result); cases.append(result)
    need(len(set(counters.values()))==1 and counters['search_completed']<=512,'CALL_ACCOUNTING')
    summaries=[c['arms'][m] for c in cases for m in ('baseline','rebased')]
    result={'status':'COMPLETE_DUAL_H8_SUBTREE_POLICY4_COMPARISON','cases':cases,'counters':counters,
        'policies_completed':4,'policies_both_parked':sum(s['both_parked'] for s in summaries),
        'hard_safety_terminals':sum(s['hard_safety_terminal'] for s in summaries),'cap_episodes':sum(s['cap'] for s in summaries),
        'tree_reuse_executed':any(c['arms']['rebased']['successful_promotions'] for c in cases),
        'rebase_arithmetic_verified_every_candidate_decision':True,
        'all_four_policies_complete_safely':all(s['both_parked'] for s in summaries),
        'strict_joint_improvement_in_both_pairs':all(c['comparison']['strict_joint_improvement_observed_on_this_pair'] for c in cases),
        'budget_semantics':'64 corrected inherited+new root contributions; not64 independent fresh simulations',
        'fixed_stop':'Two frozen starting states x two arms, max128 decisions each, genuine termination kept; no repeat or extra seeds',
        'new_teacher_traces':0,'training_runs':0,'model_forward_calls':0,'dataset32_512_written':False,
        'tree_statistics_rebuilt':True,'old_q_copied':False,'action_report_cache_enabled':False,
        'pruning_authorized':False,'deployable':False,'auto_retry':False,'speedup_claim_authorized':False,
        'full_controller_kbm_tested':False,'independent_routes_claimed':False,'local_test':local_test}
    write(output/'RESULT.json',result)
    return result
