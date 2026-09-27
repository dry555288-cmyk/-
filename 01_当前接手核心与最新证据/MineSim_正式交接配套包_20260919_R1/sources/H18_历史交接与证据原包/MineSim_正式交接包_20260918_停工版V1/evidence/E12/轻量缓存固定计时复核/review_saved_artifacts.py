"""Read-only audit of saved artifacts. Does not import project code or run MCTS."""
from pathlib import Path, PurePosixPath
from collections import Counter
from datetime import datetime, timezone
import hashlib, json, math, zipfile

INPUT=Path('/mnt/data/bee7eb3b-ba0d-4f0e-ac72-9daa097d2712.zip')
OUT=Path('/mnt/data/minesim_cachetiming_review_20260918')
PREFIX='minesim_dual_cachetiming_v1/'
OUT.mkdir(exist_ok=True)
def sha(raw): return hashlib.sha256(raw).hexdigest()
def canonical(o):return json.dumps(o,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False)
def same(a,b): return canonical(a)==canonical(b)
def close(a,b):return math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-9)
def save(name,obj):
 p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')

def compare_semantic(a,b):
 keys=('before','action_id','after','reward','detail','rng_before','rng_after','search_transition_counts','reward_formula_check')
 for k in keys:assert same(a[k],b[k]),'PARITY_'+k
 da={k:v for k,v in a['diagnostics'].items() if k!='elapsed_ms'}
 db={k:v for k,v in b['diagnostics'].items() if k!='elapsed_ms'}
 assert same(da,db),'PARITY_DIAGNOSTICS'

with zipfile.ZipFile(INPUT) as z:
 names=[n for n in z.namelist() if not n.endswith('/')]
 assert len(set(names))==len(names)
 for n in names:
  q=PurePosixPath(n)
  assert not q.is_absolute() and '..' not in q.parts and n.startswith(PREFIX)
 crc=z.testzip();assert crc is None,crc
 def raw(n):return z.read(PREFIX+n)
 def read(n):return json.loads(raw(n))
 manifest=read('MANIFEST.json')
 assert set(names)=={PREFIX+n for n in manifest}|{PREFIX+'MANIFEST.json'}
 for n,m in manifest.items():
  r=raw(n);assert len(r)==m['size'] and sha(r)==m['sha256'],n
 binding=read('release/SOURCE_BINDINGS.json'); provenance=read('SOURCE_PROVENANCE.json')
 assert set(binding['members'])==set(provenance)
 for n,m in binding['members'].items():
  r=raw('parent_sources/'+n)
  assert len(r)==m['size'] and sha(r)==m['sha256'],n
  if n!='MANIFEST.json':assert read('parent_sources/MANIFEST.json')[n]==m,('PARENT',n)
 release=read('release/RELEASE_MANIFEST.json')
 for n,m in release.items():
  r=raw('release/'+n);assert len(r)==m['size'] and sha(r)==m['sha256'],n
 protocol=read('release/PROTOCOL.json')
 assert sha(raw('release/action_cache.py'))==protocol['cache_module_sha256']
 assert sha(raw('release/parent_probe.py'))==protocol['search_harness_sha256']
 assert raw('release/action_cache.py')==raw('parent_sources/release/action_cache.py')
 assert raw('release/parent_probe.py')==raw('parent_sources/release/experiment.py')
 result=read('RESULT.json');native=read('native/RESULT.json'); stored=read('native/TIMING_ANALYSIS.json')
 assert result['rc']==int(raw('RC.txt'))==0
 assert result['native_result']==native and result['postcheck']=='PASS'
 assert result['sources_verified']==len(binding['members'])==69
 assert raw('GIT_BEFORE.json')==raw('GIT_AFTER.json')

 rows=[];blocks=[];allrecords=[];parity=0;chain=0
 for design in protocol['blocks']:
  bid=design['block_id'];path='native/'+bid+'/'
  summary=read(path+'BLOCK_SUMMARY.json'); res=summary['result']
  assert read(path+'native/RESULT.json')==res
  assert res['status']=='PASS_DUAL_FLAT_REPORT_CACHE_EQUIVALENCE_SMOKE'
  assert res['counters']=={k:8 for k in ('search_started','search_completed','outer_steps_started','outer_steps_completed')}
  cases=[]
  for case in res['cases']:
   rid=case['root_id']; bymode={}
   for mode in ('baseline','cached'):
    rr=[read(path+'native/'+rid+'/'+mode+'_'+str(s)+'.json') for s in (0,1)]
    for s,r in enumerate(rr):
     assert r['root_id']==rid and r['mode']==mode and r['step']==s
     assert r['teacher_sample'] is False and r['training_mask']==0
     assert r['diagnostics']['iterations']==sum(r['diagnostics']['visits'].values())==64
     assert r['timing']['full_planner_timing'] is False
     assert r['timing']['cprofile_enabled'] is False
     for tk in ('full_system_search_wall_ms','full_system_search_cpu_ms'):assert math.isfinite(r['timing'][tk]) and r['timing'][tk]>0
     chk=r['reward_formula_check']
     val=math.fsum(v['subtotal'] for v in chk['vehicles'].values())/chk['vehicle_denominator']+chk['internal_clearance']+chk['hard_penalty']
     assert close(val,r['reward']) and close(chk['recomputed_total'],r['reward'])
     allrecords.append(r)
    assert same(rr[0]['after'],rr[1]['before']) and same(rr[0]['rng_after'],rr[1]['rng_before']);chain+=1
    bymode[mode]=rr
   for s in (0,1):
    a=bymode['baseline'][s];c=bymode['cached'][s]
    compare_semantic(a,c)
    compare_semantic(a,read('parent_sources/native/'+rid+'/baseline_'+str(s)+'.json'));parity+=1
    def delta(r,k):return sum(r['cache_after_search'][t][k]-r['cache_before_search'][t][k] for t in ('A','B'))
    row={'block_id':bid,'root_id':rid,'decision':s,'role':design['role'],'parity':'EXACT_EXCEPT_TIMING'}
    for metric in ('cpu','wall'):
     row['baseline_'+metric+'_ms']=a['timing']['full_system_search_'+metric+'_ms']
     row['cached_'+metric+'_ms']=c['timing']['full_system_search_'+metric+'_ms']
    row.update(action_report_requests=delta(c,'requests'),cache_hits=delta(c,'hits'),full_reports_computed=delta(c,'full_report_evaluations'),baseline_full_reports_computed=delta(a,'full_report_evaluations'),cross_decision_hits=delta(c,'cross_decision_hits'))
    row['hit_rate']=row['cache_hits']/row['action_report_requests']
    assert row['action_report_requests']==row['cache_hits']+row['full_reports_computed']==delta(a,'requests')
    original=case['comparisons'][s]
    for k,v in original.items():assert row[k]==v,(bid,rid,s,k)
    rows.append(row);cases.append(row)
  before=read(path+'RESOURCE_BEFORE.json');after=read(path+'RESOURCE_AFTER.json')
  ds={k:after['cpu_stat'][k]-v for k,v in before['cpu_stat'].items() if k in after['cpu_stat']}
  assert ds==summary['resource_delta']['cpu_stat_delta']
  assert before['cpu_max']==after['cpu_max']=='1600000 100000'
  br={'block_id':bid,'role':design['role'],'root_order':design['root_order'],'nr_throttled_delta':ds['nr_throttled'],'throttled_usec_delta':ds['throttled_usec'],'elapsed_including_setup_io_s':summary['block_elapsed_seconds_including_setup_and_io']}
  for metric in ('cpu','wall'):
   a=math.fsum(r['baseline_'+metric+'_ms'] for r in cases);c=math.fsum(r['cached_'+metric+'_ms'] for r in cases)
   br[metric+'_cached_over_baseline']=c/a
  blocks.append(br)
 measured=[r for r in rows if r['role']=='measured'];mb=[r for r in blocks if r['role']=='measured']
 assert len(allrecords)==40 and parity==20 and chain==20 and len(measured)==16
 agg={}
 for metric in ('cpu','wall'):
  a=math.fsum(r['baseline_'+metric+'_ms'] for r in measured);c=math.fsum(r['cached_'+metric+'_ms'] for r in measured)
  val={'baseline_total_ms':a,'cached_total_ms':c,'baseline_mean_ms':a/16,'cached_mean_ms':c/16,'cached_over_baseline':c/a,'relative_reduction':1-c/a,'pairs_lower':sum(r['cached_'+metric+'_ms']<r['baseline_'+metric+'_ms'] for r in measured),'pairs':16,'blocks_lower':sum(r[metric+'_cached_over_baseline']<1 for r in mb),'blocks':4}
  for k,v in val.items():assert close(v,stored['aggregate'][metric][k]),(metric,k)
  agg[metric]=val
 assert same(result['native_result']['aggregate'],stored['aggregate'])
 for r,old in zip(measured,stored['measured_pairs']):assert same({k:v for k,v in r.items() if k!='role'},old)
 for r in blocks:assert r['nr_throttled_delta']==0 and r['throttled_usec_delta']==0
 event=[json.loads(l) for l in raw('EVENTS.jsonl').splitlines() if l]
 cnt=Counter(e['event'] for e in event)
 assert all(cnt[k]==40 for k in ('SEARCH_STARTED','SEARCH_RETURNED','OUTER_ADVANCE_STARTED','OUTER_ADVANCE_RETURNED','SEARCH_AND_ONE_STEP_SAVED'))
 assert len(event)==200
 t0=datetime.fromisoformat(read('TECHNICAL_START.json')['time']);t1=datetime.fromisoformat(read('CAPTURE.json')['finished_utc'])
 counts={k:sum(r[k] for r in measured) for k in ('action_report_requests','cache_hits','full_reports_computed','baseline_full_reports_computed','cross_decision_hits')}
 counts['hit_rate']=counts['cache_hits']/counts['action_report_requests']
 review={
 'review_status':'PASS_SAVED_ARTIFACT_INTEGRITY_AND_RECOMPUTATION',
 'reviewed_utc':datetime.now(timezone.utc).isoformat(),
 'input_zip':str(INPUT),'input_zip_sha256':sha(INPUT.read_bytes()),
 'execution_status':result['status'],'execution_rc':result['rc'],
 'zip_file_members':len(names),'manifest_verified':len(manifest),'source_bindings_verified':len(binding['members']),
 'release_files_verified':len(release),'zip_crc_errors':0,
 'saved_search_records_verified':len(allrecords),'semantic_pairs_verified_including_warmup':parity,
 'state_rng_chains_verified':chain,'measured_pairs':len(measured),'measured_searches':32,'warmup_searches':8,
 'aggregate_recomputed':agg,'measured_cache_counts':counts,'block_analysis':blocks,
 'duration_technical_start_to_capture_seconds':(t1-t0).total_seconds(),
 'recorded_effective_cpu':read('RESOURCES.json')['effective_cpu'],
 'all_recorded_windows_have_zero_new_cgroup_throttling':True,
 'environment_note':'Cgroup quota and counters were recorded in the uploaded run, not checked live here; zero new throttling does not establish CPU isolation or a fixed clock.',
 'git_pre_post_identical':True,'git_status_recorded':read('GIT_BEFORE.json')['status'],
 'method_note':'Baseline and candidate both use the saved counting wrapper. Primary timing is full system.search including wrapper/cache access; model/context setup, cache installation, outer advance, disk I/O and full Controller/KBM are excluded.',
 'observed_conclusion':native['observed_direction_conclusion'],
 'scientific_interpretation':'Measured cached search time increased about 6.77%; only 1/4 blocks and 7/16 measured decision pairs improved. No stable speedup demonstrated on the fixed fixtures. Do not claim significance, fleet-wide slowdown, or that all caching/tree reuse is ineffective.',
 'review_activity':{'MCTS_calls':0,'training_runs':0,'model_forwards':0,'simulation_advances':0,'cloud_access':False,'original_artifacts_modified':False},
 'preserved_run_boundaries':{k:native[k] for k in ('new_teacher_traces','training_runs','model_forward_calls','tree_reuse_executed','tree_statistics_reuse_executed','pruning_authorized','deployable','full_controller_kbm_tested','dataset32_512_written')}
 }
 save('REVIEW.json',review);save('analysis/RECOMPUTED_TIMING.json',{'aggregate':agg,'measured_cache_counts':counts,'blocks':blocks,'pairs_including_warmup':rows})
 for n in ['RESULT.json','RC.txt','RESOURCES.json','ENVIRONMENT.json','GIT_BEFORE.json','GIT_AFTER.json','TECHNICAL_START.json','CAPTURE.json','native/RESULT.json','native/TIMING_ANALYSIS.json','release/PROTOCOL.json','release/action_cache.py','release/parent_probe.py']:
  p=OUT/'original'/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw(n))
print(json.dumps({k:review[k] for k in ('manifest_verified','source_bindings_verified','saved_search_records_verified','aggregate_recomputed','measured_cache_counts','duration_technical_start_to_capture_seconds')},indent=2))
