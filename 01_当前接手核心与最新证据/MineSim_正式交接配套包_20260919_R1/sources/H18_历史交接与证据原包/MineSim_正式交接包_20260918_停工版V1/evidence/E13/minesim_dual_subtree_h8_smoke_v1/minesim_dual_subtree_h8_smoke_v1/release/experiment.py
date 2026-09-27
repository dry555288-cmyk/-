"""Two existing dual-car fixtures, two decisions, native vs sample-rebased subtree.
Eight searches at most; no teacher collection, NN inference or deployment.
"""
from __future__ import annotations
from pathlib import Path
from dataclasses import asdict
import hashlib,json,sys,time
from verify_audit import verify,verify_rebase


def canon(x):return (json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()
def read(p):return json.loads(Path(p).read_bytes())
def need(ok,text):
    if not ok:raise RuntimeError(text)
def write(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb') as f:f.write(canon(x))
def tuples(x):return tuple(tuples(v) for v in x) if isinstance(x,list) else x
def sem(d):return {k:v for k,v in d.items() if k not in ('elapsed_ms','reuse_accounting')}
def jsonclone(x):return json.loads(canon(x))
def compare_native(a,b):
    for k in ('before','after','action_id','reward','detail','rng_before','rng_after'):
        need(canon(a[k])==canon(b[k]),'COLD_NATIVE_PARITY:'+k)
    need(canon(sem(a['diagnostics']))==canon(sem(b['diagnostics'])),'COLD_NATIVE_DIAGNOSTICS')


def run(runtime,output,protocol,progress,*,local_test=False):
    runtime=Path(runtime);output=Path(output);output.mkdir(parents=True,exist_ok=False)
    need(protocol['max_search_calls']==8 and protocol['decisions_per_case']==2,'FIXED_PROTOCOL')
    sys.dont_write_bytecode=True;sys.path.insert(0,str(runtime))
    import realroute_smoke as native
    imported=native.activate_package(runtime);write(output/'IMPORTS.json',imported)
    if not local_test:
        need(sys.version_info[:2]==(3,9),'PYTHON_LINEAGE')
        expected=read(runtime/'EXPECTED_IMPORT.json')
        for k in ('numpy','shapely','model_version'):need(imported[k]==expected[k],'IMPORT_DRIFT:'+k)
    from candidate_mcts.dual_stop_adapter_v1 import action_id
    from subtree_reuse import HorizonRebasedSearch
    import teacher_cell_core as core
    rows={r['root_id']:r for r in read(runtime/'inputs/SELECTED_NEW16.json')}
    counts={'search_started':0,'search_completed':0,'outer_steps_started':0,'outer_steps_completed':0}
    cases=[];allchecks=[];any_safety=False;actual_reuse=0
    for ci,rid in enumerate(protocol['root_ids']):
        row=rows[rid];history=read(runtime/'inputs/steps'/(rid+'.json'))
        need(canon(row['state'])==canon(history['before']) and history['forced_action'] is False,'INPUT_BINDING')
        need(hashlib.sha256(canon(row['state'])).hexdigest()==row['exact_before_state_sha256'],'ROOT_STATE_SHA')
        case=output/rid;case.mkdir();runs={};audits={}
        order=['baseline','rebased'] if ci==0 else ['rebased','baseline']
        for mode in order:
            tc={'candidate_fleet_calls_including_tree_attempted':0,'candidate_fleet_calls_including_tree_returned':0}
            with native.bounded_call(90):bc=native.BoundContext(runtime,read(runtime/'inputs/contexts'/(row['task']['episode_uid']+'.json')),counters=tc)
            expected=read(runtime/'inputs/resolved'/(row['task']['task_id']+'.json'))
            need({k:v for k,v in bc.resolved.items() if k!='setup_elapsed_ms'}=={k:v for k,v in expected.items() if k!='setup_elapsed_ms'},'CONTEXT_DRIFT')
            state=bc.transition.unpack(row['state'])
            if mode=='baseline':agent=bc.system.new_search(seed=row['task']['seed'])
            else:
                def binding():
                    # Source files/route arrays are SHA-checked outside; also guard the live scalar configuration.
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
            rr=[];last_audit=None
            for step in range(2):
                if state.hard_safety_violation or state.all_goals_reached:
                    # A valid terminal is kept; do not force a search merely to hit the expected call count.
                    break
                before=bc.transition.pack(state);rng0=core.rng_json(agent);tc0=dict(tc)
                counts['search_started']+=1;progress('SEARCH_STARTED',counts,{'root_id':rid,'mode':mode,'step':step})
                begin=time.perf_counter();cpu=time.process_time()
                with native.bounded_call(90):action,diag=bc.system.search(agent,state)
                wall=(time.perf_counter()-begin)*1000.;cput=(time.process_time()-cpu)*1000.
                counts['search_completed']+=1;progress('SEARCH_RETURNED',counts,{'root_id':rid,'mode':mode,'step':step})
                search_calls={k:tc[k]-tc0[k] for k in tc};rng1=core.rng_json(agent)
                need(canon(before)==canon(bc.transition.pack(state)),'INPUT_MUTATION')
                audit=None;checks=None
                if mode=='rebased':
                    audit=jsonclone(agent.audit());checks={'full':verify(audit,64),'accounting':agent.last_meta}
                    meta=agent.last_meta
                    need(meta['new_iterations']+meta['inherited_samples']==64 and meta['root_visit_count']==64,'ROOT_INFORMATION_ACCOUNTING')
                    need(meta['child_visit_sum']+meta['root_only_sample_count']==64,'ROOT_VS_EDGE_VISITS')
                    if agent.promotion_snapshot is not None:
                        promotion=jsonclone(agent.promotion_snapshot)
                        checks['promotion']=verify(promotion)
                        need(last_audit is not None,'PARENT_AUDIT_REQUIRED')
                        checks['suffix']=verify_rebase(last_audit,promotion)
                        write(case/('promotion_'+str(step)+'.json'),{'tree':promotion,'checks':checks,
                          'rng_before':agent.promotion_rng_before,'rng_after':agent.promotion_rng_after})
                        actual_reuse+=1
                    if step==0:need(meta['inherited_samples']==0 and diag['iterations']==64,'FIRST_SEARCH_NOT_COLD')
                    write(case/('tree_'+str(step)+'.json'),audit)
                    last_audit=audit
                else:need(diag['iterations']==64 and sum(diag['visits'].values())==64,'NATIVE_BUDGET')
                need(core.rng_json(agent)==rng1,'AUDIT_CONSUMED_RNG')
                counts['outer_steps_started']+=1;progress('OUTER_ADVANCE_STARTED',counts,{'root_id':rid,'mode':mode,'step':step})
                with native.bounded_call(90):nxt,reward,detail=bc.system.advance(state,action)
                counts['outer_steps_completed']+=1;progress('OUTER_ADVANCE_RETURNED',counts,{'root_id':rid,'mode':mode,'step':step})
                native.verify_step(bc,state,action,nxt,reward,detail)
                reward_check=core.reward_check(bc,before,bc.transition.pack(nxt),reward)
                need(core.rng_json(agent)==rng1,'ADVANCE_CONSUMED_RNG')
                record={'root_id':rid,'mode':mode,'step':step,'before':before,'after':bc.transition.pack(nxt),
                  'action_id':action_id(action),'reward':reward,'detail':detail,'diagnostics':diag,'rng_before':rng0,'rng_after':rng1,
                  'search_transition_counts':search_calls,'reward_formula_check':reward_check,'sample_rebase_check':checks,
                  'hard_safety_violation_after':nxt.hard_safety_violation,'both_parked_after':nxt.all_goals_reached,
                  'timing':{'full_system_search_wall_ms':wall,'full_system_search_cpu_ms':cput,
                    'trace_capture_rebase_tail_completion_stat_rebuild_included':mode=='rebased',
                    'outer_advance_io_and_postsearch_full_audit_excluded':True,'formal_speed_test':False},
                  'teacher_sample':False,'training_mask':0,'full_controller_kbm_tested':False}
                write(case/(mode+'_'+str(step)+'.json'),record);rr.append(record);any_safety|=nxt.hard_safety_violation
                if mode=='baseline':
                    old=read(output.parent/'parent_sources'/protocol['baseline_relative'] /rid/('baseline_'+str(step)+'.json'))
                    compare_native(record,old)
                state=nxt;progress('SEARCH_AND_ONE_STEP_SAVED',counts,{'root_id':rid,'mode':mode,'step':step})
            runs[mode]=rr
        need(len(runs['baseline'])==len(runs['rebased'])==2,'SHORT_WINDOW_EARLY_TERMINAL_SAVED')
        compare_native(runs['baseline'][0],runs['rebased'][0])
        need(canon(runs['baseline'][1]['before'])==canon(runs['rebased'][1]['before']),'SECOND_START_NOT_PAIRED')
        a,b=runs['baseline'][1],runs['rebased'][1]
        cases.append({'root_id':rid,'execution_order':order,'cold_parity':'EXACT_EXCEPT_TIMING',
          'second_action_same':a['action_id']==b['action_id'],'second_before_same':True,
          'rebased_accounting':b['diagnostics']['reuse_accounting'],
          'baseline_two_search_cpu_ms':sum(r['timing']['full_system_search_cpu_ms'] for r in runs['baseline']),
          'rebased_two_search_cpu_ms':sum(r['timing']['full_system_search_cpu_ms'] for r in runs['rebased']),
          'baseline_two_search_wall_ms':sum(r['timing']['full_system_search_wall_ms'] for r in runs['baseline']),
          'rebased_two_search_wall_ms':sum(r['timing']['full_system_search_wall_ms'] for r in runs['rebased']),
          'second_decision_timings':{'baseline':a['timing'],'rebased':b['timing']},
          'transition_counts':{m:sum(r['search_transition_counts']['candidate_fleet_calls_including_tree_returned'] for r in runs[m]) for m in runs},
          'scope':'Two decisions, not task completion, independent routes, or production timing.'})
    need(all(v==8 for v in counts.values()),'SEARCH_BOUND_NOT_CLOSED')
    result={'status':('COMPLETE_DUAL_H8_SUBTREE_REBASE_SMOKE_SAFETY_NEGATIVE' if any_safety else
                     'PASS_DUAL_H8_SUBTREE_REBASE_SEMANTICS' if actual_reuse==2 else
                     'COMPLETE_DUAL_H8_SUBTREE_REBASE_FALLBACK_ONLY'),
            'counters':counts,'cases':cases,'successful_promotions':actual_reuse,
            'horizon':8,'budget_semantics':'64 root sample contributions = inherited corrected samples + new iterations, not 64 fresh simulations',
            'tree_reuse_executed':actual_reuse>0,'tree_statistics_rebuilt':True,'old_q_copied':False,
            'action_report_cache_enabled':False,'new_teacher_traces':0,'training_runs':0,'model_forward_calls':0,
            'dataset32_512_written':False,'pruning_authorized':False,'deployable':False,'auto_retry':False,
            'speedup_claim_authorized':False,'full_controller_kbm_tested':False,'technical_only':True,'local_test':local_test}
    write(output/'RESULT.json',result);return result
