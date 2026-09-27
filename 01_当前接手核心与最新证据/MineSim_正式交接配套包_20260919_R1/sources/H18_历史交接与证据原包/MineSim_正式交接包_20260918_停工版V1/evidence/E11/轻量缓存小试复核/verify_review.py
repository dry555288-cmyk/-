from pathlib import Path
import json,hashlib,math,statistics,zipfile
from datetime import datetime,timezone
base=Path('/mnt/data/minesim_flatcache_review_current')
r=base/'raw/minesim_dual_reportcache_flat_v1'
def read(f): return json.loads((r/f).read_bytes())
def canonical(x):return (json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()
def check_meta(p,m):
 b=p.read_bytes();assert len(b)==m['size'] and hashlib.sha256(b).hexdigest()==m['sha256'],str(p)
manifest=read('MANIFEST.json')
for f,m in manifest.items():check_meta(r/f,m)
assert {p.relative_to(r).as_posix() for p in r.rglob('*') if p.is_file()}==set(manifest)|{'MANIFEST.json'}
bind=read('release/SOURCE_BINDINGS.json');pm=read('parent_sources/MANIFEST.json')
for f,m in bind['members'].items():
 check_meta(r/'parent_sources'/f,m)
 if f!='MANIFEST.json':assert pm[f]==m,f
for f,m in read('release/RELEASE_MANIFEST.json').items():check_meta(r/'release'/f,m)
assert read('GIT_BEFORE.json')==read('GIT_AFTER.json')
res=read('RESULT.json');nat=read('native/RESULT.json')
assert res['native_result']==nat and res['rc']==0 and (r/'RC.txt').read_bytes()==b'0\n'
assert not res['errors'] and res['postcheck']=='PASS'
fields=('before','action_id','after','reward','detail','rng_before','rng_after','search_transition_counts','reward_formula_check')
def compare(a,b):
 for k in fields:assert canonical(a[k])==canonical(b[k]),k
 for akey in ('iterations','visits','q_values','active_mask_16','active_joint_action_ids','terminal_action_constraints','immediate_rewards','seed','vehicle_tokens','model_version','minimum_clearance_m','missing_q_means'):
  assert canonical(a['diagnostics'][akey])==canonical(b['diagnostics'][akey]),akey
 assert {k:v for k,v in a['diagnostics'].items() if k!='elapsed_ms'}=={k:v for k,v in b['diagnostics'].items() if k!='elapsed_ms'}
rows=[];records=[]
for case in nat['cases']:
 rid=case['root_id']
 for d in range(2):
  a=read(f'native/{rid}/baseline_{d}.json');b=read(f'native/{rid}/cached_{d}.json')
  old=read(f'parent_sources/native/{rid}/baseline_{d}.json')
  compare(a,b);compare(a,old)
  for rec in (a,b):
   assert rec['diagnostics']['iterations']==64 and sum(rec['diagnostics']['visits'].values())==64
   assert rec['teacher_sample'] is False and rec['training_mask']==0
   rc=rec['reward_formula_check'];vehicle=[]
   for v in rc['vehicles'].values():
    v_sum=sum(v[k] for k in ('comfort','goal_bonus','progress','safety','speed'));assert math.isclose(v_sum,v['subtotal'],abs_tol=1e-14);vehicle.append(v_sum)
   rew=sum(vehicle)/rc['vehicle_denominator']+rc['internal_clearance']+rc['hard_penalty']
   assert math.isclose(rew,rec['reward'],abs_tol=1e-14)
   assert rec['rng_before']!=rec['rng_after']
   if d:
    prev=read(f'native/{rid}/{rec["mode"]}_0.json')
    assert canonical(prev['after'])==canonical(rec['before']) and canonical(prev['rng_after'])==canonical(rec['rng_before'])
   records.append(rec)
  def diff(rec,k):return sum(rec['cache_after_search'][v][k]-rec['cache_before_search'][v][k] for v in ('A','B'))
  assert diff(a,'requests')==diff(b,'requests')==diff(b,'hits')+diff(b,'full_report_evaluations')
  assert diff(a,'full_report_evaluations')==diff(a,'requests')
  row={'root_id':rid,'decision':d,'requests':diff(b,'requests'),'hits':diff(b,'hits'),'full_reports_baseline':diff(a,'full_report_evaluations'),'full_reports_cached':diff(b,'full_report_evaluations'),'cross_decision_hits':diff(b,'cross_decision_hits')}
  for t in ('cpu','wall'):
   row['baseline_'+t+'_ms']=a['timing']['full_system_search_'+t+'_ms'];row['cached_'+t+'_ms']=b['timing']['full_system_search_'+t+'_ms']
   row[t+'_cached_over_baseline']=row['cached_'+t+'_ms']/row['baseline_'+t+'_ms']
  rows.append(row)
assert len(records)==8 and len(rows)==4
stats={}
for t in ('cpu','wall'):
 x=[row['baseline_'+t+'_ms'] for row in rows];y=[row['cached_'+t+'_ms'] for row in rows]
 stats[t]={'baseline_mean_ms':statistics.mean(x),'cached_mean_ms':statistics.mean(y),'baseline_sum_ms':sum(x),'cached_sum_ms':sum(y),'ratio_of_sums_cached_over_baseline':sum(y)/sum(x),'relative_reduction':1-sum(y)/sum(x),'pairs_lower':sum(b<a for a,b in zip(x,y)),'pairs_total':len(x),'paired_ratios':[b/a for a,b in zip(x,y)]}
req=sum(x['requests'] for x in rows);hits=sum(x['hits'] for x in rows);compute=sum(x['full_reports_cached'] for x in rows)
summary={'review_scope':'Local file, saved record, arithmetic verification only; no MCTS, no training, no new simulation; no connection to cloud','source_zip':{'filename':'263c0d6b-bdce-4571-a7ad-abaec07963e1.zip','sha256':hashlib.sha256(Path('/mnt/data/263c0d6b-bdce-4571-a7ad-abaec07963e1.zip').read_bytes()).hexdigest()},'review_created_utc':datetime.now(timezone.utc).isoformat(),'archive_members_including_manifest':len(manifest)+1,'manifest_entries_verified':len(manifest),'bound_parent_files_verified':len(bind['members']),'release_files_verified':len(read('release/RELEASE_MANIFEST.json')),'saved_record_count':8,'fresh_pair_equivalence_verified':4,'historical_baseline_equivalence_verified':4,'recorded_result_status':res['status'],'rc':res['rc'],'git_unchanged':True,'git_clean':False,'git_status':read('GIT_BEFORE.json')['status'],'sources_unchanged_as_reported':res['bound_sources_unchanged'],'resources_as_reported':read('RESOURCES.json'),'mcts_calls_in_original_experiment':8,'mcts_calls_in_this_review':0,'training_in_this_review':0,'new_teacher_traces':0,'cache_totals':{'requests':req,'hits':hits,'hit_rate':hits/req,'full_reports_baseline':req,'full_reports_cached':compute,'cross_decision_hits':sum(x['cross_decision_hits'] for x in rows)},'timing':stats,'scientific_conclusion':'Exact saved behavior parity in four pairs. Descriptive aggregate CPU and wall reductions, but mixed per-pair effects and 0.5 effective CPU. No stable or production speedup established. Cache, not tree-statistics reuse.','safety_scope':'Outer saved geometry samples and counts match; unchanged collision/geometry source binding checked, but no complete controller/KBM/continuous-safety proof.','next_proposal_not_executed':'Only fixed-code, balanced timing characterization on non-half-core-quota CPU; no candidate retuning or teacher recollection; new explicit authorization required.'}
(base/'analysis/REVIEW.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
(base/'analysis/PAIRED_TIMING.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(summary,ensure_ascii=False,indent=2))
