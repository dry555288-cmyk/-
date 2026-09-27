"""Only fixed technical cells. No discovery/confirmation schedule is executed."""
from __future__ import annotations
import argparse
from collections import Counter
import copy
import math
from pathlib import Path
import sys
import traceback

HOME=Path(__file__).resolve().parent
sys.path.insert(0,str(HOME))
from teacher_cell_core import (need,canonical,read,write,sha,objsha,strict_json,technical_spec,
                               run_cell,verify_cell,return_summary,ORDER)
from feature_projection import feature26,checked_mask,schedule
from realroute_smoke import activate_package,BoundContext,verify_step,bounded_call

GATE='DUAL_STOP_TEACHER_RUNNER_CODEC_MASK_RETURN_PARITY_SMOKE'
PASS='PASS_NEW_TEACHER_RUNNER_TECHNICAL_SMOKE_ONLY'


def fresh_counters():
    return {'roots_verified':0,'allowed_forced_cases':0,'inactive_rejected_before_run':0,
            'behavior_next_state_parity':0,'short_followup_cases':0,'static_controls_verified':0,
            'search_started':0,'search_returned':0,'outer_transitions_attempted':0,
            'outer_transitions_returned':0,'technical_cells_committed':0,
            'candidate_fleet_calls_including_tree_attempted':0,'candidate_fleet_calls_including_tree_returned':0}


def verify_versions(imported,expected):
    need(sys.version_info[:2]==(3,9),'BOUND_PYTHON39_REQUIRED')
    for k in ('numpy','shapely','model_version'):
        need(imported[k]==expected[k],'BOUND_IMPORT_VERSION:'+k)
    need(imported['source_isolation'] is True,'SOURCE_ISOLATION')


def validate_protocol(p):
    need(p['gate']==GATE and p['technical_only'] is True,'SMOKE_PROTOCOL_SCOPE')
    need(p['teacher_collection_authorized'] is False and p['training_authorized'] is False,'NO_BATCH')
    need(p['maximum_mcts_calls']==4 and p['maximum_outer_transitions']==104,'SMOKE_BOUND')
    need(p['one_step_cases']==98 and p['short_case_roots']==['root_00','root_06'],'SMOKE_TASKS')
    need(p['short_case_forced_action']=='0,0' and p['short_case_cap']==3,'SMOKE_SHORT_CONTRACT')


def compare_saved_transition(actual, recorded):
    """Exact nongeometric state/flags; explicit roundoff-only derived tolerances.

    Never rewrites either record. Tolerances do not alter collision thresholds,
    rewards or runtime selection. All differences are retained in the report.
    """
    differences=[]
    def walk(a,b,path):
        if isinstance(a,dict) and isinstance(b,dict):
            need(set(a)==set(b),'PARITY_KEYS:'+path)
            for k in a:walk(a[k],b[k],path+'.'+k if path else k)
        elif isinstance(a,list) and isinstance(b,list):
            need(len(a)==len(b),'PARITY_LENGTH:'+path)
            for i,(x,y) in enumerate(zip(a,b)):walk(x,y,path+f'[{i}]')
        elif a != b or isinstance(a,bool) != isinstance(b,bool):
            geom=(path=='after.minimum_internal_clearance_m' or
                  path.startswith('detail.collision_samples[') and path.endswith('.minimum_clearance_m'))
            limit=1e-9 if geom else (1e-10 if path=='reward' else 0.0)
            need(limit>0 and type(a) in (int,float) and type(b) in (int,float) and
                 math.isfinite(a) and math.isfinite(b),'EXACT_STATE_OR_FLAG_PARITY:'+path)
            error=abs(a-b)
            differences.append({'field':path,'new':a,'saved':b,'absolute_difference':error,'tolerance':limit})
            need(error<=limit,'DERIVED_ROUNDOFF_PARITY:'+path)
    for key in ('after','reward','detail'):walk(actual[key],recorded[key],key)
    return {'bit_exact_values':not differences,'derived_float_differences':differences,
            'codec_input_kinematics_commands_flags_masks_exact':True,
            'geometry_absolute_tolerance_m':1e-9,'reward_absolute_tolerance':1e-10,
            'saved_bytes_unchanged':True}


def run_smoke(package,output,*,local_fixture=False):
    """local_fixture is test-only Python API; CLI never enables it."""
    package,output=Path(package),Path(output)
    need(not output.exists(),'NATIVE_OUTPUT_EXISTS_NO_RETRY');output.mkdir(parents=True,exist_ok=False)
    counters=fresh_counters();status='HOLD_TECHNICAL_SMOKE';summaries=[];details={};rc=2
    try:
        protocol=read(package/'SMOKE_PROTOCOL.json');validate_protocol(protocol)
        imported=activate_package(package);write(output/'IMPORT_RESULT.json',imported)
        if not local_fixture:verify_versions(imported,read(package/'EXPECTED_IMPORT.json'))
        from candidate_mcts.dual_stop_adapter_v1 import action_id
        roots=read(package/'static/SELECTED_ROOTS.json')
        need([r['pilot_root_id'] for r in roots]==[f'root_{i:02d}' for i in range(12)],'TWELVE_FROZEN_ROOTS')
        spec=read(package/'static/TEACHER_PILOT_CONTRACT.json')
        need(spec['next_gate']==GATE and spec['authorization']['teacher_collection_authorized'] is False,'FROZEN_PARENT_SCOPE')
        reserved=[]
        for phase in ('discovery','confirmation'):
            saved=read(package/('static/'+phase.upper()+'_SCHEDULE.json'))
            need(saved==schedule(roots,phase),'FROZEN_SCHEDULE_IDENTITY')
            reserved.extend(c['rng_seed'] for c in saved)
        need(len(set(reserved))==768,'PHASE_STREAM_UNIQUENESS')
        tests=[]
        for r in roots:
            tests.extend(technical_spec(r,a,1,'one_step') for a in r['admissible_action_ids'])
        lookup={r['pilot_root_id']:r for r in roots}
        tests.extend(technical_spec(lookup[r],'0,0',3,'followup') for r in protocol['short_case_roots'])
        need(len(tests)==100 and len({t['cell_id'] for t in tests})==100,'TECHNICAL_CASE_IDS')
        need(len({t['rng_seed'] for t in tests})==100 and not ({t['rng_seed'] for t in tests}&set(reserved)),
             'TECHNICAL_STREAM_OVERLAP')
        write(output/'TECHNICAL_TEST_TABLE.json',tests)
        contexts={};root_report=[];saved_cases={};resolved=read(package/'static/SOURCE_RESOLVED_CONFIGS.json')
        for root in roots:
            row=root['behavior_record'];ep=row['task']['episode_uid']
            if ep not in contexts:
                ctxpath=root['context_relative_path'];need(ctxpath.startswith('payload/'),'CONTEXT_PATH_PREFIX')
                print('CONTEXT_BUILD='+ep,flush=True)
                with bounded_call(60):
                    bc=BoundContext(package,read(package/ctxpath[len('payload/'):]),counters=counters)
                expected=resolved['policy_00' if ep=='C11_100M_SEED0_EP1' else 'policy_04']
                clean=lambda x:{k:v for k,v in x.items() if k!='setup_elapsed_ms'}
                need(clean(bc.resolved)==clean(expected),'CONTEXT_RESOLVED_DRIFT')
                contexts[ep]=bc;write(output/'contexts'/(ep+'.json'),bc.resolved)
            bc=contexts[ep]
            before=copy.deepcopy(row['state']);state=bc.transition.unpack(before)
            need(canonical(bc.transition.pack(state))==canonical(before),'EXACT_NEW_STATE_ROUNDTRIP')
            need(objsha(before)==row['exact_before_state_sha256'],'SELECTED_ROOT_SHA')
            ids=[action_id(a) for a in bc.transition.active_joint_actions(state)]
            need(ids==root['admissible_action_ids'],'NATIVE_MASK_PARITY')
            need(checked_mask(row)==[a in ids for a in ORDER],'ALGEBRAIC_NATIVE_MASK_PARITY')
            ff=feature26(before)
            need(ff['float32']==root['feature26_float32'] and
                 ff['float32_le_sha256']==root['feature32_le_sha256'],'FEATURE26_PARITY')
            record=read(package/'source_steps'/(root['pilot_root_id']+'.json'))
            need(sha((package/'source_steps'/(root['pilot_root_id']+'.json')).read_bytes())==row['source_sha256'],'SOURCE_STEP_SHA')
            need(record['before']==before and record['diagnostics']['active_mask_16']==row['active_mask_16'],'SOURCE_RECORD_IDENTITY')
            hit=0;parity=None
            for aid in ORDER:
                if aid not in ids:
                    try:technical_spec(root,aid,1,'one_step')
                    except RuntimeError as ex:need(str(ex)=='SMOKE_TASK_DOMAIN','WRONG_INACTIVE_REJECTION')
                    else:raise RuntimeError('INACTIVE_ACTION_NOT_REJECTED')
                    counters['inactive_rejected_before_run']+=1
                    continue
                ts=technical_spec(root,aid,1,'one_step');td=output/'technical_cells'/ts['cell_id']
                summary=run_cell(bc,root,ts,td,counters,verify_step,bounded_call)
                summaries.append({'cell_id':ts['cell_id'],'summary':summary})
                counters['allowed_forced_cases']+=1
                if aid==row['selected_behavior_action']:
                    actual=read(td/'steps/0000.json')
                    parity=compare_saved_transition(actual,record)
                    counters['behavior_next_state_parity']+=1;hit+=1
                need(bc.transition.pack(state)==before and root['behavior_record']['state']==before,'ROOT_MUTATED_BETWEEN_ACTIONS')
            need(hit==1,'BEHAVIOR_ACTION_MISSING')
            counters['roots_verified']+=1
            if root['role']=='SINGLE_ACTION_STATIC_CONTROL':
                need(len(ids)==1,'STATIC_CONTROL_DOMAIN');counters['static_controls_verified']+=1
            root_report.append({'root_id':root['pilot_root_id'],'source_record_id':row['record_id'],
                'source_step_index':row['step_index'],'roundtrip_exact':True,'active_mask_16':[a in ids for a in ORDER],
                'feature26_exact':True,'saved_next_state_reward_detail_comparison':parity,
                'previous_segment_clearance_preserved':True,'legacy_restore_called':False,
                'initial_geometry_rebound':False,'teacher_sample':False})
            print('ROOT_PARITY='+str(counters['roots_verified'])+'/12',flush=True)
        write(output/'ROOT_CODEC_MASK_PARITY.json',root_report)
        for rid in protocol['short_case_roots']:
            root=lookup[rid];bc=contexts[root['behavior_record']['task']['episode_uid']]
            ts=technical_spec(root,'0,0',3,'followup');td=output/'technical_cells'/ts['cell_id']
            print('FOLLOWUP_SMOKE='+rid,flush=True)
            summary=run_cell(bc,root,ts,td,counters,verify_step,bounded_call)
            summaries.append({'cell_id':ts['cell_id'],'summary':summary});counters['short_followup_cases']+=1
        for item in summaries:
            verify_cell(output/'technical_cells'/item['cell_id'],item['summary']['spec'])
        need(counters['roots_verified']==counters['behavior_next_state_parity']==12,'ROOT_PARITY_COUNT')
        need(counters['allowed_forced_cases']==98 and counters['inactive_rejected_before_run']==94,'ACTION_PARITY_COUNT')
        need(counters['short_followup_cases']==2 and counters['static_controls_verified']==2,'CONTROL_COUNT')
        need(counters['technical_cells_committed']==100,'TECHNICAL_CELL_COUNT')
        need(counters['search_started']==counters['search_returned']==4,'FOLLOWUP_SEARCH_COVERAGE_INCOMPLETE')
        need(counters['outer_transitions_attempted']==counters['outer_transitions_returned']<=104,'OUTER_BOUND')
        need(counters['candidate_fleet_calls_including_tree_attempted']==counters['candidate_fleet_calls_including_tree_returned'],
             'TREE_TRANSITION_ACCOUNTING')
        details={'observed_technical_outcomes':dict(Counter(x['summary']['outcome'] for x in summaries)),
                 'technical_case_count':100,'all_committed_cases_verified':True,
                 'source_namespace':'minesim_c11_original_start_multiseed8_v1',
                 'full_discovery_cases_run':0,'full_confirmation_cases_run':0,
                 'note':'Technical cap1/3 outcomes are not formal128-step task estimates or training labels.'}
        write(output/'TECHNICAL_SUMMARIES.json',summaries)
        status=PASS if not local_fixture else 'PASS_LOCAL_FIXTURE_NOT_CLOUD_ENV';rc=0
    except BaseException as exc:
        write(output/'ERROR.json',{'type':type(exc).__name__,'reason':str(exc),'traceback':traceback.format_exc(),
                                   'automatic_retry':False})
        traceback.print_exc()
    result={'status':status,'gate':GATE,'counts':counters,'details':details,
            'local_fixture_only':local_fixture,'new_teacher_samples':0,'training_run':False,
            'model_forward_calls':0,'production_patch_installed':False,
            'discovery_authorized':False,'confirmation_authorized':False,
            'scientific_START_written':False,'automatic_retry':False,'automatic_resume':False}
    write(output/'RESULT.json',result);write(output/'RC.txt',str(rc).encode()+b'\n')
    return rc


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--package',required=True);ap.add_argument('--output',required=True)
    a=ap.parse_args();need(Path(a.package).resolve()==HOME,'WORKER_PACKAGE_HOME')
    return run_smoke(HOME,Path(a.output))


if __name__=='__main__':raise SystemExit(main())
