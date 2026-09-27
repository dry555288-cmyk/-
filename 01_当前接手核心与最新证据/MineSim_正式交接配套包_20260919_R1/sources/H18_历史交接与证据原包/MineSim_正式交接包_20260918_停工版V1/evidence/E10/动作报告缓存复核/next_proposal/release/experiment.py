"""Two fixtures x two decisions x baseline/cached; at most eight searches.
Not tree-statistics reuse, a new benchmark, teacher collection or deployment.
"""
from __future__ import annotations
from pathlib import Path
import hashlib,json,math,sys,time

def canon(x):return (json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()
def read(p):return json.loads(Path(p).read_bytes())
def need(x,t):
    if not x:raise RuntimeError(t)
def write(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb') as f:f.write(canon(x))
def tuples(x):return tuple(tuples(v) for v in x) if isinstance(x,list) else x
def semantic(d):return {k:v for k,v in d.items() if k!='elapsed_ms'}
def compare(a,b):
    for k in ('before','action_id','after','reward','detail','rng_before','rng_after','search_transition_counts','reward_formula_check'):
        need(canon(a[k])==canon(b[k]),'CACHE_BEHAVIOR_CHANGED:'+k)
    need(canon(semantic(a['diagnostics']))==canon(semantic(b['diagnostics'])),'CACHE_DIAGNOSTICS_CHANGED')

def run(runtime,output,protocol,progress,*,local_test=False):
    runtime=Path(runtime);output=Path(output);output.mkdir(parents=True,exist_ok=False)
    sys.dont_write_bytecode=True
    sys.path.insert(0,str(Path(__file__).resolve().parent));sys.path.insert(0,str(runtime))
    from action_cache import ExactReportCache
    import realroute_smoke as native
    imported=native.activate_package(runtime);write(output/'IMPORTS.json',imported)
    if not local_test:
        need(sys.version_info[:2]==(3,9),'PYTHON_LINEAGE')
        expected=read(runtime/'EXPECTED_IMPORT.json')
        for k in ('numpy','shapely','model_version'):need(imported[k]==expected[k],'IMPORT_DRIFT:'+k)
    from candidate_mcts.dual_stop_adapter_v1 import action_id
    import teacher_cell_core as core
    selected={x['root_id']:x for x in read(runtime/'inputs/SELECTED_NEW16.json')}
    counts={'search_started':0,'search_completed':0,'outer_steps_started':0,'outer_steps_completed':0}
    cases=[];records=[]
    for ci,rid in enumerate(protocol['root_ids']):
        row=selected[rid];historical=read(runtime/'inputs/steps'/(rid+'.json'))
        need(canon(row['state'])==canon(historical['before']) and not historical['forced_action'],'SOURCE_STATE')
        need(hashlib.sha256(canon(row['state'])).hexdigest()==row['exact_before_state_sha256'],'ROOT_SHA')
        case=output/rid;case.mkdir()
        runs={}
        order=('baseline','cached') if ci==0 else ('cached','baseline')
        for mode in order:
            tc={'candidate_fleet_calls_including_tree_attempted':0,'candidate_fleet_calls_including_tree_returned':0}
            with native.bounded_call(90):bc=native.BoundContext(runtime,read(runtime/'inputs/contexts'/(row['task']['episode_uid']+'.json')),counters=tc)
            resolved=read(runtime/'inputs/resolved'/(row['task']['task_id']+'.json'))
            need({k:v for k,v in bc.resolved.items() if k!='setup_elapsed_ms'}=={k:v for k,v in resolved.items() if k!='setup_elapsed_ms'},'CONTEXT_DRIFT')
            state=bc.transition.unpack(row['state']);searcher=bc.system.new_search(seed=row['task']['seed'])
            searcher.rng.setstate(tuples(historical['rng_before']))
            caches={t:ExactReportCache(bc.transition._vehicle_transitions[t],enabled=mode=='cached',capacity=4096) for t in ('A','B')}
            for cache in caches.values():cache.install()
            rr=[]
            try:
                for step in range(2):
                    for cache in caches.values():cache.begin_decision(step)
                    before=bc.transition.pack(state);rng_before=core.rng_json(searcher)
                    cache0={t:c.snapshot() for t,c in caches.items()};tc0=dict(tc)
                    counts['search_started']+=1;progress('SEARCH_STARTED',counts,{'root_id':rid,'mode':mode,'step':step})
                    start=time.perf_counter();cpu=time.process_time()
                    with native.bounded_call(90):action,diag=bc.system.search(searcher,state)
                    elapsed=(time.perf_counter()-start)*1000;cpu_ms=(time.process_time()-cpu)*1000
                    counts['search_completed']+=1;progress('SEARCH_RETURNED',counts,{'root_id':rid,'mode':mode,'step':step})
                    cache1={t:c.snapshot() for t,c in caches.items()};search_calls={k:tc[k]-tc0[k] for k in tc}
                    need(canon(before)==canon(bc.transition.pack(state)),'INPUT_MUTATED')
                    need(diag['iterations']==64 and sum(diag['visits'].values())==64,'BUDGET')
                    rng_after=core.rng_json(searcher)
                    counts['outer_steps_started']+=1;progress('OUTER_ADVANCE_STARTED',counts,{'root_id':rid,'mode':mode,'step':step})
                    with native.bounded_call(90):after,reward,detail=bc.system.advance(state,action)
                    counts['outer_steps_completed']+=1;progress('OUTER_ADVANCE_RETURNED',counts,{'root_id':rid,'mode':mode,'step':step})
                    native.verify_step(bc,state,action,after,reward,detail)
                    check=core.reward_check(bc,before,bc.transition.pack(after),reward)
                    need(core.rng_json(searcher)==rng_after,'OUTER_RNG_CHANGED')
                    rec={'root_id':rid,'mode':mode,'step':step,'before':before,'after':bc.transition.pack(after),'action_id':action_id(action),
                         'reward':reward,'detail':detail,'diagnostics':diag,'rng_before':rng_before,'rng_after':rng_after,
                         'search_transition_counts':search_calls,'reward_formula_check':check,'cache_before_search':cache0,'cache_after_search':cache1,
                         'timing':{'full_system_search_wall_ms':elapsed,'full_system_search_cpu_ms':cpu_ms,'cprofile_enabled':False,
                                   'cache_key_validation_lookup_copy_included':True,'full_planner_timing':False},
                         'teacher_sample':False,'training_mask':0}
                    write(case/(mode+'_'+str(step)+'.json'),rec);rr.append(rec);records.append(rec);state=after
                    progress('SEARCH_AND_ONE_STEP_SAVED',counts,{'root_id':rid,'mode':mode,'step':step})
            finally:
                for cache in caches.values():cache.close()
                need(all('action_report' not in bc.transition._vehicle_transitions[t].__dict__ for t in ('A','B')),'CACHE_NOT_RESTORED')
            runs[mode]=rr
        comparisons=[]
        for step in range(2):
            base,new=runs['baseline'][step],runs['cached'][step];compare(base,new)
            # Confirm unchanged actions, visits and states relative to the prior probe without rerunning it.
            old=read(output.parent/'parent_sources/native'/rid/('baseline_'+str(step)+'.json'))
            compare(base,old)
            need(base['action_id']==old['action_id'] and base['diagnostics']['visits']==old['diagnostics']['visits'],'PARENT_BASELINE_CHANGED')
            need(canon(base['after'])==canon(old['after']) and canon(base['rng_after'])==canon(old['rng_after']),'PARENT_STATE_RNG_CHANGED')
            need(all(math.isclose(v,old['diagnostics']['q_values'][a],rel_tol=1e-10,abs_tol=1e-10) for a,v in base['diagnostics']['q_values'].items()),'PARENT_Q_CHANGED')
            def delta(rec,key):return sum(rec['cache_after_search'][t][key]-rec['cache_before_search'][t][key] for t in ('A','B'))
            requests=delta(new,'requests');hits=delta(new,'hits');miss=delta(new,'full_report_evaluations')
            need(requests==hits+miss and requests==delta(base,'requests'),'CACHE_ACCOUNTING')
            comparisons.append({'decision':step,'parity':'EXACT_EXCEPT_TIMING','action_report_requests':requests,'cache_hits':hits,
                                'full_reports_computed':miss,'baseline_full_reports_computed':delta(base,'full_report_evaluations'),
                                'cross_decision_hits':delta(new,'cross_decision_hits'),'hit_rate':hits/requests if requests else 0,
                                'baseline_wall_ms':base['timing']['full_system_search_wall_ms'],'cached_wall_ms':new['timing']['full_system_search_wall_ms'],
                                'baseline_cpu_ms':base['timing']['full_system_search_cpu_ms'],'cached_cpu_ms':new['timing']['full_system_search_cpu_ms']})
        cases.append({'root_id':rid,'order':order,'comparisons':comparisons})
    need(counts['search_completed']==counts['search_started']==8 and counts['outer_steps_started']==counts['outer_steps_completed']==8,'COUNTERS')
    total_hits=sum(x['cache_hits'] for c in cases for x in c['comparisons'])
    result={'status':'PASS_DUAL_FLAT_REPORT_CACHE_EQUIVALENCE_SMOKE','cases':cases,'counters':counts,'cache_hits':total_hits,
            'cache_effect_observed':total_hits>0,'new_teacher_traces':0,'training_runs':0,'model_forward_calls':0,'data_collection':0,
            'tree_reuse_executed':False,'tree_statistics_reuse_executed':False,'deterministic_action_report_cache_executed':True,'cache_implementation':'flat_exact_key_and_immutable_value_row_copy_v1',
            'search_budget':64,'max_depth':8,'all_geometry_samples_kept':True,'deployable':False,'pruning_authorized':False,
            'speedup_claim_authorized':False,'timing_scope':'four paired decisions, alternating case order, descriptive only; CPU quota may be low',
            'full_controller_kbm_tested':False,'technical_only':True,'dataset32_512_written':False,'local_test':local_test}
    write(output/'RESULT.json',result);return result
