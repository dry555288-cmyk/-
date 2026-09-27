from pathlib import Path
import json, hashlib, math, datetime, zipfile
HERE=Path(__file__).resolve().parent
r=HERE/'raw/minesim_dual_treeprobe_v1'
def rd(p):return json.loads(p.read_bytes())
def canon(x):return (json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()
def sha(b):return hashlib.sha256(b).hexdigest()
def check(x,m):
 if not x:raise AssertionError(m)
def verify_map(base,mp):
 for n,b in mp.items():
  data=(base/n).read_bytes();check(len(data)==b['size'] and sha(data)==b['sha256'],'FILE:'+n)
 return len(mp)
m=rd(r/'MANIFEST.json');nmanifest=verify_map(r,m)
check(set(m)=={p.relative_to(r).as_posix() for p in r.rglob('*') if p.is_file() and p!=r/'MANIFEST.json'},'MANIFEST_COVERAGE')
b=rd(r/'release/SOURCE_BINDINGS.json');print('bindings keys',list(b));sources=b['members'];nsource=verify_map(r/'parent_sources',sources)
pm=rd(r/'parent_sources/MANIFEST.json')
for n,v in sources.items():
 if n!='MANIFEST.json':check(pm[n]==v,'PARENT:'+n)
nrelease=verify_map(r/'release',rd(r/'release/RELEASE_MANIFEST.json'))
res=rd(r/'RESULT.json');native=rd(r/'native/RESULT.json');check(res['native_result']==native,'RESULT_NATIVE')
check((r/'RC.txt').read_bytes()==b'0\n' and res['rc']==0 and res['status']=='PASS_DUAL_TREE_REUSE_OBSERVATIONAL_PROBE','STATUS')
check(rd(r/'GIT_AFTER.json')==rd(r/'GIT_BEFORE.json'),'GIT')
protocol=rd(r/'release/PROTOCOL.json');cases=[];allroll=[];counter_sum=0;all_nodes=0
for rid in protocol['root_ids']:
 recs={md:[rd(r/'native'/rid/f'{md}_{i}.json') for i in range(2)] for md in ('baseline','observed')}
 hist=rd(r/'parent_sources/runtime/inputs/steps'/f'{rid}.json')
 for md in recs:
  for i,d in enumerate(recs[md]):
   check(d['teacher_sample'] is False and d['training_mask']==0,'NOT_TEACHER')
   check(d['diagnostics']['iterations']==64 and sum(d['diagnostics']['visits'].values())==64,'BUDGET')
   check(d['before']==(hist['before'] if i==0 else recs[md][i-1]['after']),'STATE_CHAIN')
   check(d['rng_before']==(hist['rng_before'] if i==0 else recs[md][i-1]['rng_after']),'RNG_CHAIN')
   counter_sum+=1
  first=recs[md][0]
  check(first['action_id']==hist['action_id'] and first['diagnostics']['visits']==hist['diagnostics']['visits'],'HISTORICAL_ACTIONS')
  check(first['rng_after']==hist['rng_after_search'],'HISTORICAL_RNG')
  check(all(math.isclose(v,hist['diagnostics']['q_values'][k],rel_tol=1e-10,abs_tol=1e-10) for k,v in first['diagnostics']['q_values'].items()),'HISTORICAL_Q')
 for i in range(2):
  base,obs=recs['baseline'][i],recs['observed'][i]
  fields=['before','after','action_id','reward','detail','rng_before','rng_after','search_transition_counts']
  for f in fields:check(canon(base[f])==canon(obs[f]),'PARITY:'+f)
  check(canon({k:v for k,v in base['diagnostics'].items() if k!='elapsed_ms'})==canon({k:v for k,v in obs['diagnostics'].items() if k!='elapsed_ms'}),'DIAG_PARITY')
  t=obs['tree'];nodes=t['nodes'];idx={a['index']:a for a in nodes};all_nodes+=len(nodes)
  for nd in nodes:
   check(sha(canon(nd['state']))==nd['state_sha256'],'STATE_SHA')
   check(nd['q']==(nd['value_sum']/nd['visits'] if nd['visits'] else 0),'Q_VALUE')
   children=[x for x in nodes if x['parent_index']==nd['index']]
   check(len(children)==nd['children_count'],'CHILD_COUNT')
   if nd['parent_index'] is not None:
    p=idx[nd['parent_index']];check(nd['depth']==p['depth']+1 and nd['action_path'][:-1]==p['action_path'],'PARENT_STRUCTURE')
  child=next(nd for nd in nodes if nd['action_path']==[obs['action_id']])
  subtree=[nd for nd in nodes if nd['action_path'] and nd['action_path'][0]==obs['action_id']]
  check(canon(child['state'])==canon(obs['after']),'NEXT_STATE_MATCH')
  check(len(subtree)==t['selected_child_nodes'] and len(nodes)==t['total_nodes'],'NODE_COUNTS')
  check(child['visits']==t['selected_child_visits'],'CHILD_VISITS')
  ph=obs['profile']['phase_inclusive_ms'];den=math.fsum(v['cumulative_ms'] for v in ph.values())
  check(den==obs['profile']['sum_nonoverlapping_four_phase_ms'],'PHASE_SUM')
  frac=ph['_rollout']['cumulative_ms']/den;allroll.append(frac)
  funcs=obs['profile']['all_profiled_functions'];fn=lambda tail,name: next(f for f in funcs if f['file'].endswith(tail) and f['function']==name)
  searchcalls=obs['search_transition_counts']['candidate_fleet_calls_including_tree_returned']
  check(fn('dual_stop_adapter_v1.py','step_with_diagnostics')['total_calls']==searchcalls,'TRANSITION_PROFILE_COUNT')
  check(fn('fleet_search.py','_expand')['total_calls']==64 and fn('fleet_search.py','_rollout')['total_calls']==64,'PHASE_COUNTS')
  cases.append({'root_id':rid,'decision':i,'action':obs['action_id'],'behavior_parity':'EXACT_EXCLUDING_TIMING','total_tree_nodes':len(nodes),'tree_max_depth':max(n['depth'] for n in nodes),'selected_subtree_nodes':len(subtree),'selected_subtree_fraction':len(subtree)/len(nodes),'selected_child_state_match':True,'selected_child_legal_actions_match_reported':t['selected_child_active_actions_match'],'old_residual_horizon':t['old_nominal_remaining_steps_from_child'],'fresh_horizon':8,'baseline_search_wall_ms':base['timing']['full_system_search_wall_ms'],'baseline_search_cpu_ms':base['timing']['full_system_search_cpu_ms'],'profile_phase_ms':{k:v['cumulative_ms'] for k,v in ph.items()},'rollout_share_of_four_profiled_phases':frac,'search_transition_calls':searchcalls,'explicit_expansions':64,'rollout_transition_calls_inferred_from_source':searchcalls-64,'scalar_validate_calls':fn('dual_stop_motion_v1.py','validate')['total_calls'],'scalar_action_report_calls':fn('dual_stop_motion_v1.py','action_report')['total_calls'],'node_constructor_profile_ms':fn('fleet_node.py','__init__')['self_ms']})
check(counter_sum==8,'TOTAL')
start=rd(r/'TECHNICAL_START.json')['time'];finish=res['finished_utc'];dt=(datetime.datetime.fromisoformat(finish)-datetime.datetime.fromisoformat(start)).total_seconds()
summary={'review_status':'PASS_LOCAL_RECORD_AND_HASH_REVIEW','source_archive':'09bb8435-54da-4d72-b7d0-536d562ff483.zip','source_archive_sha256':sha(Path('/mnt/data/09bb8435-54da-4d72-b7d0-536d562ff483.zip').read_bytes()),'manifest_items_verified':nmanifest,'source_bindings_verified':nsource,'release_files_verified':nrelease,'saved_search_records_reviewed':8,'baseline_observed_pairs_exact':4,'saved_tree_nodes_verified':all_nodes,'rc':0,'native_status':res['status'],'technical_duration_seconds':dt,'resource_snapshot':rd(r/'RESOURCES.json'),'cases':cases,'rollout_phase_share_min':min(allroll),'rollout_phase_share_max':max(allroll),'scope':{'local_new_MCTS_calls':0,'local_training_runs':0,'local_new_teacher_samples':0,'cloud_connected_by_reviewer':False,'tree_reuse_executed_in_source':False,'speedup_measured':False,'controller_kbm_validated':False,'action_domain_status':'Reported cloud parity; reviewer did not rerun action-provider validation'},'next_research_design':'Do not promote old Q/visits without horizon and incoming-edge-return design. Deterministic calculation caching may be tested independently if separately authorized; not a completed tree-statistics reuse implementation.'}
(HERE/'REVIEW.json').write_bytes(canon(summary))
print(json.dumps({k:v for k,v in summary.items() if k!='cases'},ensure_ascii=False,indent=2))
