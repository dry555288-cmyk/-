"""Current-stationary-hold guide domain evaluator adapted from the saved full32 evaluator using the byte-identical cloud-validated slim V5 / staged V4 kernel.

Only orchestration and compact evidence indexing are new. No full experiment
runs on import. The only CLI entry is full_gate through the one-time launcher.
"""
from __future__ import annotations
from dataclasses import asdict
from pathlib import Path
from collections import Counter
import importlib.util
import hashlib
import math
import random
import shutil
import sys
import time
import support as s

MODES = ('legacy_v2', 'hold_current_v1')
GATE = 'DUAL_HOLD_CURRENT_GUIDE_DOMAIN_PAIR_V1'
COMPLETE = 'COMPLETE_HOLD_CURRENT_GUIDE_DOMAIN_PAIR_V1'
BUDGET_VERSION = 'COMMON_400MS_V5_H16_HOLD_CURRENT_DOMAIN_PAIR_V1'
KERNEL_BUDGET_VERSION = 'COMMON_400MS_STAGED_COMMIT_CHECKPOINTS_V4'
EXECUTION_VARIANT = 'SLIM_CHECKPOINT_FAST_PATH_V5'
BUDGET_NS = 400_000_000


def tuples(x):
    return tuple(tuples(v) for v in x) if isinstance(x, list) else x


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def compare(a, b):
    """Keep missing windows unknown, including a failure before any action."""
    both = a['both_parked'] and b['both_parked']
    windows = a['Y64'] is not None and b['Y64'] is not None
    clearance = a['minimum_sampled_clearance_m'] is not None and b['minimum_sampled_clearance_m'] is not None
    compliant = a['budget_compliance_for_equal_time_claim'] and b['budget_compliance_for_equal_time_claim']
    ratio = lambda key: b[key]/a[key] if both and a[key] > 0 else None
    return {
        'both_completed': both,
        'candidate_model_seconds_minus_reference': b['model_seconds']-a['model_seconds'] if both else None,
        'candidate_planning_cpu_ratio': ratio('planning_cpu_plus_guide_setup_ms'),
        'candidate_planning_wall_ratio': ratio('planning_wall_plus_guide_setup_ms'),
        'candidate_Y64_minus_reference': b['Y64']-a['Y64'] if windows else None,
        'candidate_original_return_minus_reference': b['Y64']-a['Y64'] if windows else None,
        'candidate_clearance_minus_reference_m': b['minimum_sampled_clearance_m']-a['minimum_sampled_clearance_m'] if clearance else None,
        'candidate_longest_stationary_minus_reference_s': b['both_unfinished_stationary_longest_seconds']-a['both_unfinished_stationary_longest_seconds'],
        'both_arms_budget_compliant': compliant,
        'descriptive_joint_improvement': bool(both and compliant and windows and clearance
            and not a['hard_safety_terminal'] and not b['hard_safety_terminal']
            and b['model_seconds'] <= a['model_seconds'] and b['Y64'] >= a['Y64']
            and b['minimum_sampled_clearance_m'] >= a['minimum_sampled_clearance_m']
            and b['planning_cpu_plus_guide_setup_ms'] < a['planning_cpu_plus_guide_setup_ms']
            and b['planning_wall_plus_guide_setup_ms'] < a['planning_wall_plus_guide_setup_ms']),
        'not_a_pure_same_workload_speedup': True,
        'statistical_superiority_established': False,
    }


def classify_deadline(action_id, diag, elapsed_ns):
    if elapsed_ns > BUDGET_NS:
        return 'DECISION_DEADLINE_LATE_RETURN_NO_EXECUTION'
    if action_id is None or diag is None:
        return 'DECISION_DEADLINE_NO_ADMITTED_ACTION'
    return None


def check_protocol(p, root):
    s.check(p['gate']==GATE and p['budget_version']==BUDGET_VERSION,'PROTOCOL_GATE')
    expected={'budget_mode':'wall_time','decision_wall_ns':400000000,'work_cutoff_ns':380000000,
      'return_reserve_ns':20000000,'iteration_guard_factor':1.25,'normal_iteration_limit':None,
      'emergency_iteration_guard':100000,'depth_options':[16],'gamma':.99,'c_uct':1.4,'final_rule':'visit'}
    s.check(p['search']==expected,'PROTOCOL_SEARCH')
    s.check(p['kernel_budget_version']==KERNEL_BUDGET_VERSION and p['execution_variant']==EXECUTION_VARIANT,'KERNEL_VARIANT')
    s.check(p['methods']==list(MODES) and p['guided_rollout_probability']==.5,'PROTOCOL_MODES')
    s.check((p['policies'],p['pairs'],p['roots'],p['cap_steps'],p['max_policy_searches'],p['new_technical_searches'])==(2,1,1,128,256,0),'PROTOCOL_COUNTS')
    for key,name in [('source_roots_sha256','ROOTS.json'),('pair_schedule_sha256','PAIR_SCHEDULE.json')]:
        s.check(s.sha(s.read_stable(root/name))==p[key],'INPUT_SHA:'+name)
    lock=s.parse(s.read_stable(root/'DESIGN_FROZEN_BEFORE_TESTS.json'))
    s.check(lock['protocol_sha256']==s.sha(s.read_stable(root/'PROTOCOL.json')),'DESIGN_LOCK')
    for name,digest in lock['new_code_sha256'].items():
        s.check(s.sha(s.read_stable(root/name))==digest,'NEW_CODE_LOCK:'+name)
    rows=s.parse(s.read_stable(root/'ROOTS.json')); schedule=s.parse(s.read_stable(root/'PAIR_SCHEDULE.json'))
    s.check([r['root_id'] for r in rows]==['outside_hold_41p5s'],'ROOT_ORDER')
    s.check([(q['root_id'],q['horizon_steps']) for q in schedule]==[(rows[0]['root_id'],16)],'SCHEDULE_ORDER')
    by_id={r['root_id']:r for r in rows}
    for k,q in enumerate(schedule):
        r=by_id[q['root_id']]
        s.check(q['arm_order']==(list(MODES) if k%2==0 else list(reversed(MODES))),'ARM_ORDER')
        for key in ('native_seed','native_rng_initial','guide_rng_initial'):
            s.check(s.canon(q[key])==s.canon(r[key]),'RNG_BINDING:'+key)


def lightweight_diag(diag):
    """Full diagnostics stay once in RETURNED_RAW; step files reference its SHA."""
    if diag is None:
        return None
    return {k:v for k,v in diag.items() if k != 'wall_budget'}


def commit_outer(directory, ret, advance, capture, validate):
    """No delayed action can reach advance; outer return is saved before audit."""
    from decision_journal import store
    s.check(ret['failure_reason'] is None and ret['timing']['decision_wall_ns'] <= BUDGET_NS,
            'NO_EXECUTION_OF_FAILED_OR_LATE_DECISION')
    directory = Path(directory)
    store(directory/'OUTER_PRE.json', {'stage':'BEFORE_OUTER','time':s.utc(),
        'action_id':ret['proposed_action_id'],'prior_decision_verified':True})
    try:
        value = advance()
    except BaseException as exc:
        import traceback
        store(directory/'OUTER_EXCEPTION.json', {'stage':'OUTER_EXCEPTION','time':s.utc(),
            'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc(),
            'partial_return_unknown':True,'auto_retry':False})
        raise
    raw = capture(value)
    digest = store(directory/'OUTER_RETURNED_RAW.json', {'stage':'OUTER_RETURNED_NOT_YET_VALIDATED',
        'time':s.utc(),'outer_transition_executed':True,'return':raw})
    try:
        validate(value)
    except BaseException as exc:
        import traceback
        store(directory/'OUTER_AUDIT_ERROR.json', {'stage':'OUTER_AUDIT_ERROR','time':s.utc(),
            'returned_sha256':digest,'type':type(exc).__name__,'message':str(exc),
            'traceback':traceback.format_exc(),'auto_retry':False})
        raise
    store(directory/'OUTER_VERIFIED.json', {'stage':'OUTER_VERIFIED','time':s.utc(),
        'returned_sha256':digest,'physical_deployment':False})
    return value, digest



def pack_flight(controller, pack):
    """Error context only; never treat in-flight state as an outer successor."""
    d=dict(getattr(controller,'_flight',{}))
    for key in ('last_transition_input','last_transition_output'):
        if key in d:d[key]=pack(d[key])
    return d


def cooperative_call_metrics(tr):
    """Complete, late-complete and incomplete work have distinct denominators."""
    n=tr['attempted_complete_iterations'];ab=tr['aborted_incomplete_iterations']
    s.check(ab in (0,1) and tr['started_iterations']==n+ab,'COOP_ITERATION_ACCOUNTING')
    return {'started_iterations':tr['started_iterations'],
        'aborted_incomplete_iterations':ab,
        'late_completed_excluded_iterations':tr['late_completed_excluded_iterations'],
        'max_observed_checkpoint_gap_ns':None,
        'checkpoint_gap_collection':'NOT_COLLECTED',
        'clock_checks_total':tr['clock_checks_total'],
        'execution_variant':tr['execution_variant'],
        'staged_preparation_total_ns':sum(x['preparation_ns'] for x in tr['transaction_clock']),
        'staged_commit_total_ns':sum(x['commit_ns'] for x in tr['transaction_clock']),
        'staged_commit_max_ns':max((x['commit_ns'] for x in tr['transaction_clock']),default=0),
        'kernel_budget_version':tr['version'],
        'preparation_cutoff':tr['preparation_abort'] is not None,
        'cooperative_probes_restored':tr['cooperative_probes_restored'],
        'incomplete_return_is_unknown':True,'synthetic_clock':False}


def cooperative_arm_metrics(attempts):
    return {'started_iterations_total':sum(a['started_iterations'] for a in attempts),
        'natural_aborted_iterations_total':sum(a['aborted_incomplete_iterations'] for a in attempts),
        'calls_with_cooperative_abort':sum(a['aborted_incomplete_iterations']>0 for a in attempts),
        'timely_calls_with_cooperative_abort':sum(a['aborted_incomplete_iterations']>0 and a['failure_reason'] is None for a in attempts),
        'late_calls_with_cooperative_abort':sum(a['aborted_incomplete_iterations']>0 and a['decision_wall_ns']>BUDGET_NS for a in attempts),
        'calls_preparation_cutoff':sum(a['preparation_cutoff'] for a in attempts),
        'late_completed_excluded_iterations_total':sum(a['late_completed_excluded_iterations'] for a in attempts),
        'maximum_observed_checkpoint_gap_ns':None,
        'checkpoint_gap_collection':'NOT_COLLECTED',
        'clock_checks_total':sum(a['clock_checks_total'] for a in attempts),
        'staged_preparation_total_ns':sum(a['staged_preparation_total_ns'] for a in attempts),
        'staged_commit_total_ns':sum(a['staged_commit_total_ns'] for a in attempts),
        'staged_commit_max_ns':max((a['staged_commit_max_ns'] for a in attempts),default=0),
        'partial_iterations_never_counted_as_complete':True}


def regions(bc, packed, geom):
    result={}
    for token in ('A','B'):
        cache=bc.transition._route_geometry_caches[token]
        car=bc.transition.unpack(packed).state_for(token)
        distance=max(cache._start_progress,min(float(car.route_s),cache._end_progress))
        index=max(0,min(int(round((distance-cache._start_progress)/cache.grid_step_m)),len(cache._geometries)-1))
        e=geom['envelopes'][token]
        result[token]='BEFORE' if index<e['first_index'] else ('AFTER' if index>e['last_index'] else 'INSIDE')
    return result

def release_events(records):
    result={t:None for t in ('A','B')}
    for r in records:
        for t in result:
            if result[t] is None and r['regions_after'][t]=='AFTER': result[t]=(r['step']+1)*.5
    return {'first_exit_endpoint_seconds':result,'not_continuous_safety_certificate':True}


def run(release, output, protocol, progress, *, local_smoke_steps=None):
    release, output = Path(release), Path(output)
    check_protocol(protocol, release)
    s.check(local_smoke_steps in (None, 1), 'NO_LOCAL_FULL_RUN_SWITCH')
    output.mkdir(exist_ok=False)
    slim_dir=release/'base/parent/core'; staged_dir=slim_dir/'parent'
    coop_dir=staged_dir/'parent/core'; core_dir=coop_dir/'parent/core'
    parent = core_dir/'parent'; runtime = parent/'runtime'
    sys.dont_write_bytecode = True
    sys.path[:0] = [str(slim_dir), str(staged_dir), str(coop_dir), str(core_dir), str(parent), str(runtime)]
    from decision_journal import guarded_call, store
    from horizon_staged_audit import audit_staged
    from transaction_capture import capture_transaction_state
    import realroute_smoke as native
    imports = native.activate_package(runtime)
    store(output/'IMPORTS.json', {**imports, 'MCTS_calls_is_import_snapshot_not_final_count':True})
    import teacher_cell_core as core
    from intent_rollout import ConflictGuide, guidance_seed
    from candidate_mcts.dual_stop_adapter_v1 import action_id
    from deadline_search_v2 import NoAdmittedDecision, MAX_ITERATIONS
    from horizon_adapter import search_with_horizon_deadline
    from slim_checkpoint import SlimNativeSearch, SlimConflictSearch
    from hold_current_guide import HoldCurrentGuide
    from hold_audit import audit_hold
    metrics = load_module('frozen_walltime_metrics', parent/'experiment.py')
    s.check(MAX_ITERATIONS == 100000, 'EMERGENCY_GUARD_DRIFT')
    if local_smoke_steps is None:
        s.check(sys.version_info[:3] == (3,9,25), 'PYTHON_LINEAGE')
        expected = s.parse(s.read_stable(runtime/'EXPECTED_IMPORT.json'))
        for key in ('numpy','shapely','model_version'):
            s.check(imports[key] == expected[key], 'IMPORT_DRIFT:'+key)
    rows=s.parse(s.read_stable(release/'ROOTS.json'))
    schedule=s.parse(s.read_stable(release/'PAIR_SCHEDULE.json'))
    rowmap = {r['root_id']:r for r in rows}
    counts = dict(technical_search_started=0,technical_search_completed=0,policy_search_started=0,
        policy_search_completed=0,policy_search_verified=0,policy_search_no_action=0,
        outer_started=0,outer_completed=0,outer_verified=0,policies_completed=0)
    operational_deadline = time.monotonic()+protocol['operational_wall_limit_seconds']
    def guard():
        s.check(time.monotonic() < operational_deadline, 'OPERATIONAL_WALL_LIMIT_NOT_MODEL_CAP')
        s.check(shutil.disk_usage(output).free >= protocol['resources']['runtime_disk_guard_bytes'], 'RUNTIME_DISK_GUARD')
    def tick(event, **where):
        progress(event, dict(counts), where)
    def context(row):
        tc = dict(candidate_fleet_calls_including_tree_attempted=0,candidate_fleet_calls_including_tree_returned=0)
        with native.bounded_call(90):
            bc = native.BoundContext(runtime, s.parse(s.read_stable(runtime/'inputs/contexts'/(row['task']['episode_uid']+'.json'))), counters=tc)
        expected = s.parse(s.read_stable(release/'base/witness/evidence/SETUP.json'))['resolved']
        trim = lambda d:{k:v for k,v in d.items() if k != 'setup_elapsed_ms'}
        s.check(s.canon(trim(bc.resolved)) == s.canon(trim(expected)), 'CONTEXT_DRIFT')
        return bc, tc
    restored = []; geometry_checked = set()
    geometry_expected = s.parse(s.read_stable(release/'base/witness/evidence/GUIDE_GEOMETRY.json'))
    for row in rows:
        guard(); rid=row['root_id']
        raw = s.read_stable(release/row['source_step']); hist=s.parse(raw)
        s.check(len(raw)==row['source_size'] and s.sha(raw)==row['source_sha256'], 'STEP_ORIGIN_SHA')
        s.check(s.canon(hist['before'])==s.canon(row['state']) and hist['step']==row['source_step_index_0based'], 'ROOT_ORIGIN')
        s.check(s.sha(s.canon(row['state']))==row['exact_before_state_sha256'], 'STATE_SHA')
        bc,tc = context(row); st=bc.transition.unpack(row['state'])
        s.check(s.canon(bc.transition.pack(st))==s.canon(row['state']), 'ROOT_ROUNDTRIP')
        ids=[action_id(a) for a in bc.transition.active_joint_actions(st)]
        s.check(ids==['%d,%d'%(i,j) for i in range(4) for j in range(4)], 'SAVED_ACTION_DOMAIN')
        ep=row['task']['episode_uid']
        if ep not in geometry_checked:
            with native.bounded_call(90):g=ConflictGuide(bc.transition)
            actual={'envelopes':{t:asdict(e) for t,e in g.envelopes.items()},
                'route_cache_start':{t:g.caches[t]._start_progress for t in ('A','B')},
                'route_cache_end':{t:g.caches[t]._end_progress for t in ('A','B')},
                'cache_size':{t:len(g.caches[t]._geometries) for t in ('A','B')}}
            s.check(actual['envelopes']==geometry_expected['envelopes'], 'INPUT_GEOMETRY_DRIFT')
            geometry_checked.add(ep); del g
        check_guide=ConflictGuide(bc.transition)
        observed_intentions=list(check_guide.intentions(st,check_guide.reports(st)))
        s.check(observed_intentions==row['expected_initial_intentions'],'INITIAL_GUIDE_DOMAIN_DRIFT')
        del check_guide
        restored.append({'root_id':rid,'source_sha256':row['source_sha256'],'codec_roundtrip':True,
            'all16_legal':True,'new_searches':0})
    store(output/'INPUT_RESTORATION.json', restored)
    store(output/'PREFLIGHT.json', {'input_count':1,'technical_searches':0,
        'cloud_v5_78_smoke_reused_as_evidence':True,'old78_smoke_reexecuted':False})
    store(output/'POLICY_START.json', {'time':s.utc(),'local_integration':local_smoke_steps is not None,
        'new_budget_namespace':True,'old_partial_not_resumed':True})
    tick('POLICY_START', local=local_smoke_steps is not None)
    cases=[]; actual_schedule=schedule
    cap=128 if local_smoke_steps is None else 1
    for pair in actual_schedule:
        rid=pair['root_id'];row=rowmap[rid];pid=pair['pair_id'];horizon=pair['horizon_steps']; summaries={}
        for mode in pair['arm_order']:
            guard();arm=output/'pairs'/pid/mode;arm.mkdir(parents=True,exist_ok=False)
            setup_cpu=time.process_time();setup_wall=time.perf_counter();bc,tc=context(row)
            setup={'native_context_cpu_ms':(time.process_time()-setup_cpu)*1000.,
                'native_context_wall_ms':(time.perf_counter()-setup_wall)*1000.,
                'guide_cpu_ms':0.,'guide_wall_ms':0.,'guide_cost_in_first_decision':True}
            state=bc.transition.unpack(row['state']); is_v2=True; is_candidate=mode=='hold_current_v1'
            holder={'controller':None,'guide':None,'action':None,'diag':None,'timing':{},'initial_guide_rng':None}
            records=[];attempts=[];c0=metrics.cpu_stat();w0=time.perf_counter();ct0=time.process_time()
            s.check(core.saved_status(bc.transition.pack(state),0,128)=='RUNNING','ROOT_TERMINAL')
            store(arm/'ARM_START.json',{'time':s.utc(),'pair':pair,'root_id':rid,'mode':mode,
                'source_task':row['task'],'before':row['state'],'local_integration':local_smoke_steps is not None})
            tick('ARM_START',pair=pid,root=rid,mode=mode,replicate=pair['replicate_id'])
            status='RUNNING'
            for step in range(cap):
                guard(); before=bc.transition.pack(state);tc0=dict(tc)
                previous=holder['controller']
                rng0=core.rng_json(previous) if previous is not None else pair['native_rng_initial']
                grng0=previous.guide_rng.getstate() if previous is not None else pair['guide_rng_initial']
                holder.update(action=None,diag=None,timing={})
                original_bindings={(objname,attr):(attr in vars(obj),vars(obj).get(attr))
                    for objname,obj,attrs in [('transition',bc.transition,('step','_geometry','active_joint_actions')),
                                             ('reward',bc.system.reward,('evaluate','is_terminal'))]
                    for attr in attrs}
                scalar_bindings=[(m,k,k in vars(m),vars(m).get(k))
                    for m in bc.transition._vehicle_transitions.values() for k in ('validate','action_report')]
                call_dir=arm/'calls'/('%04d'%step)
                pre={'pair_id':pid,'root_id':rid,'mode':mode,'step':step,'before':before,
                    'rng_before':rng0,'guide_rng_before':grng0,'budget_version':BUDGET_VERSION,
                    'first_call_includes_cold_build':previous is None,'teacher_sample':False,'horizon_steps':horizon}
                def call():
                    counts['policy_search_started']+=1
                    tick('DECISION_START',pair=pid,mode=mode,step=step)
                    start_wall=time.perf_counter_ns();start_cpu=time.process_time_ns()
                    try:
                        with native.bounded_call(90):
                            if holder['controller'] is None:
                                if is_v2:
                                    gc=time.process_time_ns();gw=time.perf_counter_ns()
                                    holder['guide']=(HoldCurrentGuide if is_candidate else ConflictGuide)(bc.transition)
                                    setup['guide_wall_ms']=(time.perf_counter_ns()-gw)/1.e6
                                    setup['guide_cpu_ms']=(time.process_time_ns()-gc)/1.e6
                                cls=SlimConflictSearch if is_v2 else SlimNativeSearch
                                agent=cls(transition_model=bc.transition,reward_model=bc.system.reward,
                                    action_provider=bc.transition.active_joint_actions,budget=MAX_ITERATIONS,
                                    max_depth=horizon,c_uct=1.4,gamma=.99,seed=pair['native_seed'],
                                    guide=holder['guide'],alpha=.5 if is_v2 else 0.,
                                    policy_seed=guidance_seed(pair['native_rng_initial']),root_rule='visit')
                                agent.rng.setstate(tuples(pair['native_rng_initial']))
                                agent.guide_rng.setstate(tuples(pair['guide_rng_initial']))
                                holder['controller']=agent;holder['initial_guide_rng']=agent.guide_rng.getstate()
                            agent=holder['controller']
                            if is_candidate: holder['guide'].reset_call()
                            agent.arm_deadline(start_wall)
                            try:
                                holder['action'],holder['diag']=search_with_horizon_deadline(bc.system,agent,state,horizon)
                            except NoAdmittedDecision:
                                pass
                    finally:
                        wall_ns=time.perf_counter_ns()-start_wall;cpu_ns=time.process_time_ns()-start_cpu
                        holder['timing']={'decision_wall_ns':wall_ns,'decision_cpu_ns':cpu_ns,
                            'decision_wall_ms':wall_ns/1.e6,'decision_cpu_ms':cpu_ns/1.e6,
                            'includes_cold_guide_first_call':step==0,'includes_backup_operand_capture':True,
                            'includes_guidance_and_symmetric_root_trace':True,
                            'includes_cooperative_checkpoints_and_partial_work_capture':True,
                            'excludes_io_outer_step_and_postchecks':True,'requested_wall_budget_ms':400.}
                    aid=None if holder['action'] is None else action_id(holder['action'])
                    reason=classify_deadline(aid,holder['diag'],holder['timing']['decision_wall_ns'])
                    counts['policy_search_completed']+=1
                    return {'proposed_action_id':aid,'failure_reason':reason,
                        'timing':dict(holder['timing']),'action_executed':False,
                        'snapshot_contains_full_diagnostics':True}
                def snapshot():
                    c=holder['controller'];root=getattr(c,'active_root_for_failure',None)
                    root_data=None if root is None else {'n':root.visit_count,'w':root.value_sum,
                        'children':{action_id(a):{'n':v.visit_count,'w':v.value_sum} for a,v in root.children.items()}}
                    return {'diagnostics':holder['diag'],
                        'root_updates':getattr(c,'root_updates',[]),'backup_receipts':getattr(c,'backup_receipts',[]),
                        'rollouts':getattr(c,'rollout_records',[]),'wall_budget':getattr(c,'last_budget_trace',None),
                        'rng_after':None if c is None else core.rng_json(c),
                        'guide_rng_after':None if c is None else c.guide_rng.getstate(),
                        'state_after_search':bc.transition.pack(state),'partial_active_root':root_data,
                        'timing':dict(holder['timing']),'initial_guide_rng':holder['initial_guide_rng'],
                        'partial_iteration':None if c is None else c.export_partial_iteration(bc.transition.pack),
                        'inflight_or_last_work_for_error_context':pack_flight(c,bc.transition.pack),
                        'phase':getattr(c,'_phase',None),
                        'cutoff_event':getattr(c,'cutoff_event',None),
                        'staged_transaction':getattr(c,'_draft_view',None),
                        'hold_current_diagnostics':holder['guide'].call_diagnostics() if is_candidate and holder['guide'] is not None else None,
                        'hold_current_certificates':holder['guide'].certificates if is_candidate and holder['guide'] is not None and step==0 else None,
                        'transaction_runtime_observation':capture_transaction_state(c) if c is not None else None}
                def validate(ret,raw):
                    s.check(s.canon(raw['state_after_search'])==s.canon(before),'ROOT_MUTATION')
                    s.check(holder['controller'].max_depth==horizon,'REQUESTED_HORIZON_DRIFT')
                    tr=raw['wall_budget'];s.check(tr['version']==KERNEL_BUDGET_VERSION and tr['execution_variant']==EXECUTION_VARIANT,'BUDGET_VERSION_DRIFT')
                    s.check(tr['checkpoints'] is None and tr['max_observed_checkpoint_gap_ns'] is None and tr['largest_checkpoint_gap'] is None,'UNRECORDED_IS_NOT_ZERO')
                    s.check(tr['checkpoint_diagnostics']['clock_decimation'] is False,'POLL_FREQUENCY_DRIFT')
                    s.check(tr['technical_fixed_iterations'] is None,'TECHNICAL_MODE_NOT_POLICY')
                    s.check(not tr['emergency_resource_guard_triggered'],'EMERGENCY_GUARD_NO_EXECUTION')
                    audit=audit_staged(holder['controller'],raw['diagnostics'],raw['partial_iteration'],
                        allow_no_action=ret['failure_reason'] is not None)
                    for (objname,attr),(own,oldvalue) in original_bindings.items():
                        obj=bc.transition if objname=='transition' else bc.system.reward
                        s.check((attr in vars(obj))==own and vars(obj).get(attr) is oldvalue,
                                'COOPERATIVE_WRAPPER_NOT_RESTORED:'+objname+':'+attr)
                    for model,key,own,value in scalar_bindings:
                        s.check((key in vars(model))==own and vars(model).get(key) is value,'SCALAR_WRAPPER_NOT_RESTORED:'+key)
                    s.check(holder['controller'].action_provider==bc.transition.active_joint_actions,
                            'ACTION_PROVIDER_NOT_RESTORED_BEFORE_OUTER')
                    if ret['proposed_action_id'] is not None:
                        d=raw['diagnostics']
                        s.check(d['evaluation_horizon_steps']==horizon,'RETURNED_HORIZON_DRIFT')
                        s.check(d['final_root_selection']['rule']=='visit' and
                            ret['proposed_action_id']==d['final_root_selection']['chosen_action_id'],'FINAL_ACTION_DRIFT')
                        s.check(ret['proposed_action_id'] in d['active_joint_action_ids'],'ACTION_NOT_LEGAL')
                    if step==0:
                        s.check(s.canon(raw['initial_guide_rng'])==s.canon(grng0),'INITIAL_GUIDE_RNG')
                    if is_candidate:
                        audit.update(audit_hold(holder['guide'],raw['hold_current_diagnostics']))
                    return {**audit,'actual_return_within400ms':ret['timing']['decision_wall_ns']<=BUDGET_NS,
                        'eligible_for_outer_execution':ret['failure_reason'] is None}
                ret,raw,audit=guarded_call(call_dir,pre,call,snapshot,validate,
                    on_raw_saved=lambda *_:tick('RETURNED_RAW_SAVED',pair=pid,mode=mode,step=step))
                counts['policy_search_verified']+=1
                hold_counts={} if not is_candidate else raw['hold_current_diagnostics']['counts']
                raw_sig=s.sha(s.read_stable(call_dir/'RETURNED_RAW.json'))
                tr=raw['wall_budget'];timing=ret['timing'];reason=ret['failure_reason']
                attempt={**timing,'hold_current_counts':hold_counts,'horizon_steps':horizon,'step':step,'failure_reason':reason,
                    'admitted_iterations':tr['admitted_iterations'],'attempted_iterations':tr['attempted_complete_iterations'],
                    'iteration_safety_cap_reached':False,'emergency_resource_guard_triggered':False,
                    'stop_reason':tr['stop_reason'],'legacy2048_exceeded':tr['attempted_complete_iterations']>2048,
                    'legacy_abs_1e9_would_fail':audit['legacy_abs_1e9_would_fail'],
                    **cooperative_call_metrics(tr),
                    'exact_ordered_replay':True,'call_receipt_sha256':raw_sig,
                    'call_receipt_path':'calls/%04d/RETURNED_RAW.json'%step}
                attempts.append(attempt)
                if step==0:
                    store(arm/'SETUP.json',{'resolved':bc.resolved,'timing':setup,'pair':pair,'root_id':rid})
                    if is_v2:
                        guide=holder['guide']
                        if is_candidate:store(arm/'HOLD_CELL_CERTIFICATES.json',guide.certificates)
                        store(arm/'GUIDE_GEOMETRY.json',{'envelopes':{t:asdict(e) for t,e in guide.envelopes.items()},
                            'build_checks':guide.build_pair_checks,'build_charged_inside_first_decision':True,'not_safety_proof':True})
                if reason is not None:
                    counts['policy_search_no_action']+=1;status=reason
                    store(arm/'deadline_failure.json',{'outcome':reason,'before':before,'step':step,
                        'call_receipt_path':attempt['call_receipt_path'],'call_receipt_sha256':raw_sig,
                        'no_outer_transition':True,'proposed_not_executed_action_id':ret['proposed_action_id'],
                        'Y64':None,'full_task_return':None,'not_a_physical_safe_stop':True})
                    tick('DEADLINE_FAILURE_SAVED',pair=pid,mode=mode,step=step,reason=reason)
                    break
                tc_delta={k:tc[k]-tc0[k] for k in tc}
                def advance():
                    counts['outer_started']+=1
                    with native.bounded_call(90):value=bc.system.advance(state,holder['action'])
                    counts['outer_completed']+=1
                    return value
                def outer_capture(value):
                    nxt,reward,detail=value
                    return {'before':before,'after':bc.transition.pack(nxt),'reward':reward,'detail':detail,
                        'action_id':ret['proposed_action_id'],'call_receipt_sha256':raw_sig}
                def outer_validate(value):
                    nxt,reward,detail=value
                    native.verify_step(bc,state,holder['action'],nxt,reward,detail)
                    core.reward_check(bc,before,bc.transition.pack(nxt),reward)
                (nxt,reward,detail),outer_sha=commit_outer(call_dir,ret,advance,outer_capture,outer_validate)
                counts['outer_verified']+=1;after=bc.transition.pack(nxt)
                intentions=Counter(r.get('initial_intention') for r in raw['rollouts'])
                rec={'pair_id':pid,'replicate_id':pair['replicate_id'],'root_id':rid,'mode':mode,'step':step,
                    'before':before,'after':after,'action_id':ret['proposed_action_id'],'reward':reward,'detail':detail,
                    'diagnostics':lightweight_diag(raw['diagnostics']),
                    'rng_before':rng0,'rng_after':raw['rng_after'],'guide_rng_before':grng0,'guide_rng_after':raw['guide_rng_after'],
                    'rule_detail':{},'horizon_steps':horizon,'regions_before':regions(bc,before,geometry_expected),'regions_after':regions(bc,after,geometry_expected),'transition_counts':tc_delta,'timing':timing,
                    'initial_intention_counts':{t:intentions[t] for t in ('A','B','FREE')},
                    'call_receipt_path':'../'+attempt['call_receipt_path'],'call_receipt_sha256':raw_sig,
                    'outer_raw_sha256':outer_sha,'full_search_arrays_are_in_call_receipt':True,
                    'hold_current_counts':hold_counts,'teacher_sample':False,'training_mask':0,'full_controller_kbm_tested':False}
                store(arm/'steps'/('%04d.json'%step),rec)
                records.append(rec);state=nxt;status=core.saved_status(after,len(records),128)
                tick('STEP_SAVED',pair=pid,mode=mode,step=step,status=status)
                # Retain light steps, not many previous full search trees/receipt arrays.
                del raw,ret,audit
                if status!='RUNNING':break
            if status=='RUNNING':
                s.check(local_smoke_steps==1,'UNFINISHED_FULL_ARM');status='SMOKE_LIMIT_NOT_TASK_RESULT'
            summary=metrics.summarize_timed(records,status,setup,time.perf_counter()-w0,
                time.process_time()-ct0,c0,metrics.cpu_stat(),attempts,row['state'])
            summary['initial_intention_counts']={t:sum(r['initial_intention_counts'][t] for r in records) for t in ('A','B','FREE')}
            summary['hold_current_counts']={key:sum(a['hold_current_counts'].get(key,0) for a in attempts) for key in ('eligibility_checks','eligible','selected_guided_actions','delegated_legacy_actions','unavailable')}
            summary.update(horizon_steps=horizon,source_elapsed_model_seconds=row['source_elapsed_model_seconds'],
                root_before=row['state'],release_events=release_events(records),local_counterfactual=True,pair_id=pid,root_id=rid,source_task_id=row['task']['task_id'],replicate_id=pair['replicate_id'],
                seed=pair['native_seed'],root_rule='visit',budget_version=BUDGET_VERSION,
                emergency_resource_guard_calls=0,legacy2048_exceeded_calls=sum(a['legacy2048_exceeded'] for a in attempts),
                legacy_abs_1e9_would_fail_calls=sum(a['legacy_abs_1e9_would_fail'] for a in attempts),
                durable_calls_audited=len(attempts),old_partial_not_resumed=True,
                **cooperative_arm_metrics(attempts))
            store(arm/'DECISION_BUDGET_SUMMARY.json',attempts)
            store(arm/'SUMMARY.json',summary);summaries[mode]=summary
            counts['policies_completed']+=1
            tick('ARM_SAVED',pair=pid,root=rid,mode=mode,status=status,steps=len(records))
            # Drop completed arm's context/controller; no policy RNG is shared across arms.
            holder.clear();del state,bc,records,attempts
        case={'pair_id':pid,'root_id':rid,'source_task_id':row['task']['task_id'],'replicate_id':pair['replicate_id'],
            'horizon_steps':horizon,'arm_order':pair['arm_order'],'arms':summaries,'comparison':compare(summaries['legacy_v2'],summaries['hold_current_v1'])}
        store(output/'pairs'/pid/'COMPARISON.json',case);cases.append(case)
        tick('PAIR_SAVED',pair=pid,pairs_completed=len(cases))
    s.check(counts['technical_search_started']==counts['technical_search_completed']==0,'OLD_TECH_REEXECUTED')
    s.check(counts['policy_search_started']==counts['policy_search_completed']==counts['policy_search_verified'], 'INCOMPLETE_SEARCH_TRANSACTION')
    s.check(counts['outer_started']==counts['outer_completed']==counts['outer_verified'], 'INCOMPLETE_OUTER_TRANSACTION')
    expected=2
    s.check(counts['policies_completed']==expected,'RECORD_COUNT')
    summary={'pairs':1,'methods':{m:cases[0]['arms'][m] for m in MODES},
        'comparison':cases[0]['comparison'],'all_trials_retained':True,
        'no_statistical_or_safety_superiority_claim':True}
    result={'status':COMPLETE if local_smoke_steps is None else 'LOCAL_ONE_STEP_INTEGRATION_COMPLETE',
        'budget_version':BUDGET_VERSION,'cases':cases,'counts':counts,'summary':summary,
        'records_completed':expected,'roots':1,'replicates_per_root':1,'horizons':[16],
        'local_smoke_steps':local_smoke_steps,'route_pair_count':1,'blind_test':False,
        'task_completions_by_method':{m:sum(c['arms'][m]['both_parked'] for c in cases) for m in MODES},
        'new_teacher_traces':0,'training_runs':0,'model_forward_calls':0,'deployed':False,
        'dataset32_512_written':False,'old_trials_merged':False,'old_CAP_extended':False,
        'kernel_budget_version':KERNEL_BUDGET_VERSION,'execution_variant':EXECUTION_VARIANT,
        'superiority_established':False,'record_completion_not_algorithm_success':True,
        'cost_scope':protocol['timing_scope']}
    store(output/'RESULT.json',result);tick('EVALUATION_COMPLETE',status=result['status'])
    return result
