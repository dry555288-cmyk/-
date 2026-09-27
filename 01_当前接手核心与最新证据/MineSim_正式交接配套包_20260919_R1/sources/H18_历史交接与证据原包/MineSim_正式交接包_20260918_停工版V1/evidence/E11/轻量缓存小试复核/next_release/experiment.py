"""Forty bounded searches for fixed-code timing, with saved warmup and balanced order.
No teacher acquisition, fitting, cache retuning, or tree-statistics reuse.
The SHA-bound parent harness and cache module are used byte-for-byte unchanged.
"""
from __future__ import annotations
from pathlib import Path
import hashlib
import importlib.util
import json
import math
import os
import time

def canon(x):
    return (json.dumps(x, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)+'\n').encode()
def need(ok,msg):
    if not ok: raise RuntimeError(msg)
def read(p): return json.loads(Path(p).read_bytes())
def write(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb') as f:
        f.write(canon(x)); f.flush(); os.fsync(f.fileno())
def cgroup_snapshot():
    out={'monotonic':time.monotonic(),'cpu_max':None,'cpu_stat':None,'path':None,'visibility_errors':[]}
    for p in ('/sys/fs/cgroup/cpu.max','/sys/fs/cgroup/cpu/cpu.cfs_quota_us','/sys/fs/cgroup/cpu/cpu.cfs_period_us'):
        try:out[p]=Path(p).read_text().strip()
        except OSError:out[p]=None
    out['cpu_max']=out['/sys/fs/cgroup/cpu.max']
    for p in ('/sys/fs/cgroup/cpu.stat','/sys/fs/cgroup/cpu/cpu.stat'):
        try:
            raw=Path(p).read_text(); values={}
            for line in raw.splitlines():
                k,v=line.split(); values[k]=int(v)
            out['cpu_stat']=values;out['path']=p;break
        except FileNotFoundError:continue
        except (OSError, ValueError) as e:out['visibility_errors'].append(str(e))
    out['affinity_count']=len(os.sched_getaffinity(0))
    try:out['loadavg']=Path('/proc/loadavg').read_text().strip()
    except OSError:out['loadavg']=None
    return out

def quota_diff(a,b):
    keys=('/sys/fs/cgroup/cpu.max','/sys/fs/cgroup/cpu/cpu.cfs_quota_us','/sys/fs/cgroup/cpu/cpu.cfs_period_us','affinity_count')
    changed=any(a.get(k)!=b.get(k) for k in keys)
    av,bv=a.get('cpu_stat'),b.get('cpu_stat')
    visible=bool(av is not None and bv is not None and 'nr_throttled' in av and 'nr_throttled' in bv and a['path']==b['path'])
    d={k:bv[k]-av[k] for k in av if k in bv} if av is not None and bv is not None else {}
    valid=visible and all(v>=0 for v in d.values())
    return {'resource_config_changed':changed,'throttle_visibility_valid':valid,'cpu_stat_delta':d,
            'observed_throttle_events':d.get('nr_throttled') if valid else None,
            'timing_environment_limited':changed or not valid or d.get('nr_throttled',1)>0,
            'interpretation':'These cgroup counters cover the cgroup, not only the benchmark. No throttling does not prove an isolated CPU or constant frequency.'}

def summarize(blocks):
    warm=[b for b in blocks if b['role']=='warmup']; measured=[b for b in blocks if b['role']=='measured']
    need(len(warm)==1 and len(measured)==4,'FIXED_BLOCK_COUNT')
    rows=[]; br=[]
    for block in measured:
        rr=[]
        for case in block['result']['cases']:
            for p in case['comparisons']:
                row=dict(p,root_id=case['root_id'],block_id=block['block_id'])
                for k in ('baseline_cpu_ms','cached_cpu_ms','baseline_wall_ms','cached_wall_ms'):
                    need(math.isfinite(row[k]) and row[k]>0,'INVALID_TIMING:'+k)
                rows.append(row);rr.append(row)
        need(len(rr)==4,'PAIRS_PER_BLOCK')
        item={'block_id':block['block_id'],'root_order':block['root_order'],'resource':block['resource_delta']}
        for metric in ('cpu','wall'):
            a=math.fsum(x['baseline_'+metric+'_ms'] for x in rr)
            c=math.fsum(x['cached_'+metric+'_ms'] for x in rr)
            item[metric+'_ratio']=c/a
        br.append(item)
    need(len(rows)==16,'MEASURED_PAIR_COUNT')
    ag={}
    for metric in ('cpu','wall'):
        a=math.fsum(x['baseline_'+metric+'_ms'] for x in rows)
        c=math.fsum(x['cached_'+metric+'_ms'] for x in rows)
        ag[metric]={'baseline_total_ms':a,'cached_total_ms':c,'baseline_mean_ms':a/16,'cached_mean_ms':c/16,'cached_over_baseline':c/a,'relative_reduction':1-c/a,'pairs_lower':sum(x['cached_'+metric+'_ms']<x['baseline_'+metric+'_ms'] for x in rows),'pairs':16,'blocks_lower':sum(b[metric+'_ratio']<1 for b in br),'blocks':4}
    limited=any(b['resource_delta']['timing_environment_limited'] for b in blocks)
    consistent=all(b['cpu_ratio']<1 and b['wall_ratio']<1 for b in br)
    if limited: conclusion='TIMING_ENVIRONMENT_LIMITED_KEEP_ALL_RESULTS_NO_AUTO_RETRY'
    elif consistent: conclusion='CONSISTENT_DIRECTION_ON_TWO_FIXED_INPUTS_ONLY_NOT_GENERALIZATION'
    else: conclusion='MIXED_OR_NO_REPRODUCIBLE_DIRECTION_ON_FIXED_INPUTS'
    return {'measured_pairs':rows,'block_summaries':br,'aggregate':ag,'timing_environment_limited':limited,'observed_direction_conclusion':conclusion,
            'general_speedup_claim_authorized':False,'deployment_authorized':False,'warmup_in_primary_metric':False,
            'selection_policy':'All sixteen successful measured pairs included; no fastest-only selection. Warmup separately retained. Four timing repetitions are not four independent driving scenes.'}

def run(runtime,output,protocol,progress,*,local_test=False,parent_run=None,snapshot_fn=None):
    runtime=Path(runtime);output=Path(output);output.mkdir(parents=True,exist_ok=False)
    need(protocol['max_search_calls']==40 and protocol['timing_repetitions']==4,'PROTOCOL_SIZE')
    need(len(protocol['root_ids'])==2 and len(protocol['blocks'])==5,'PROTOCOL_CASES')
    if parent_run is None:
        p=Path(__file__).resolve().parent/'parent_probe.py'
        need(hashlib.sha256(p.read_bytes()).hexdigest()==protocol['search_harness_sha256'],'PARENT_HARNESS_SHA')
        spec=importlib.util.spec_from_file_location('unchanged_flat_cache_probe',p)
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod); parent_run=mod.run
    snap=snapshot_fn or cgroup_snapshot
    total={'search_started':0,'search_completed':0,'outer_steps_started':0,'outer_steps_completed':0}
    blocks=[]
    for bi,design in enumerate(protocol['blocks']):
        bd=output/design['block_id'];bd.mkdir()
        order=list(protocol['root_ids'])
        if design['root_order']=='reverse':order.reverse()
        else:need(design['root_order']=='original','ROOT_ORDER')
        for rid in order:
            for step in range(2):
                src=output.parent/'parent_sources/native'/rid/('baseline_'+str(step)+'.json')
                dst=bd/'parent_sources/native'/rid/src.name;dst.parent.mkdir(parents=True,exist_ok=True)
                with dst.open('xb') as f:f.write(src.read_bytes())
        bp=dict(protocol,root_ids=order)
        write(bd/'BLOCK_PROTOCOL.json',dict(design,root_ids=order,teacher_sample=False))
        before=snap();write(bd/'RESOURCE_BEFORE.json',before)
        offset=dict(total)
        def update(event,counts,where):
            need(all(0<=counts[k]<=8 for k in total),'BLOCK_CALL_LIMIT')
            for k in total:total[k]=offset[k]+counts[k]
            need(all(v<=40 for v in total.values()),'GLOBAL_CALL_LIMIT')
            progress(event,dict(total),dict(where,block_id=design['block_id'],role=design['role']))
        start=time.monotonic()
        try:
            result=parent_run(runtime,bd/'native',bp,update,local_test=local_test)
        finally:
            after=snap();write(bd/'RESOURCE_AFTER.json',after)
        need(result['status']=='PASS_DUAL_FLAT_REPORT_CACHE_EQUIVALENCE_SMOKE','BLOCK_EQUIVALENCE_FAILED')
        need(result['counters']=={'search_started':8,'search_completed':8,'outer_steps_started':8,'outer_steps_completed':8},'BLOCK_COUNTERS')
        for k in total:need(total[k]==offset[k]+8,'PROGRESS_COUNTER_MISMATCH')
        resource=quota_diff(before,after)
        block={'block_id':design['block_id'],'role':design['role'],'root_order':design['root_order'],'result':result,'resource_delta':resource,'block_elapsed_seconds_including_setup_and_io':time.monotonic()-start}
        write(bd/'BLOCK_SUMMARY.json',block);blocks.append(block)
        print('TIMING_BLOCKS_COMPLETED='+str(bi+1)+'/5; ROLE='+design['role'],flush=True)
    analysis=summarize(blocks);write(output/'TIMING_ANALYSIS.json',analysis)
    need(all(v==40 for v in total.values()),'FINAL_COUNTERS')
    result={'status':'COMPLETE_DUAL_FLAT_CACHE_FIXED_TIMING','counters':dict(total),'warmup_searches':8,'measured_searches':32,'measured_paired_decisions':16,'root_count':2,'timing_repetitions':4,'all_recorded_semantics_equal':True,'cache_module_changed':False,'parent_search_harness_changed':False,'aggregate':analysis['aggregate'],'timing_environment_limited':analysis['timing_environment_limited'],'observed_direction_conclusion':analysis['observed_direction_conclusion'],'new_teacher_traces':0,'training_runs':0,'model_forward_calls':0,'tree_reuse_executed':False,'tree_statistics_reuse_executed':False,'pruning_authorized':False,'deployable':False,'speedup_claim_authorized':False,'auto_retry':False,'full_controller_kbm_tested':False,'dataset32_512_written':False,'local_test':local_test}
    write(output/'RESULT.json',result);return result
