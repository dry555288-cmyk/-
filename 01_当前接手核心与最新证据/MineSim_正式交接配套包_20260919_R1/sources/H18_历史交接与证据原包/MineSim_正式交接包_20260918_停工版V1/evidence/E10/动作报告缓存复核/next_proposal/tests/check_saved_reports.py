"""Pure scalar recomputation on SAVED tree nodes. No MCTS, advance, collection or fit."""
from pathlib import Path
import sys,json,hashlib,zipfile,importlib.util,time,statistics,cProfile,pstats,io
sys.dont_write_bytecode=True
WORK=Path('/mnt/data/minesim_reportcache_review_current')
R=WORK/'raw/minesim_dual_reportcache_v1'
runtime=R/'parent_sources/parent_sources/runtime'
sys.path.insert(0,str(runtime))
from candidate_mcts.dual_stop_motion_v1 import DestinationStopTransition,DualOnlyState
from candidate_mcts.transition_model import TransitionConfig
from candidate_mcts.action_space import MCTSAction

def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
old=module('cache_previous',R/'release/action_cache.py')
new=module('cache_flat',WORK/'next_proposal/release/action_cache.py')
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
rows=[]
with zipfile.ZipFile('/mnt/data/09bb8435-54da-4d72-b7d0-536d562ff483.zip') as z:
 for case in ['coverage_policy_01__step0014','coverage_policy_05__step0011']:
  cfg=json.loads((runtime/'inputs/resolved'/(case.split('__')[0].replace('coverage_','')+'.json')).read_bytes())['transition_config']
  for step in [0,1]:
   obs=json.loads(z.read('minesim_dual_treeprobe_v1/native/'+case+'/observed_'+str(step)+'.json'))
   for node in obs['tree']['nodes']:
    for token in ['A','B']:
     d=node['state']['vehicles'][token]
     s=DualOnlyState(**{k:d[k] for k in ['time_s','route_s','speed_mps','accel_mps2','target_speed_mps','collision','goal_reached','parked_at_time_s']},
      lead_distance_m=float('inf'),lead_rel_speed_mps=0.,minimum_clearance_m=float('inf'),prev_action=None if d['prev_action'] is None else MCTSAction(d['prev_action']))
     rows.append((case,step,token,cfg[token],s))
checked=0;seen={}
for case,step,token,cfg,s in rows:
 key=(case,token)
 if key not in seen:
  mo=DestinationStopTransition(TransitionConfig(**cfg));ca=new.ExactReportCache(mo,enabled=True);seen[key]=(mo,ca)
 m,c=seen[key];c.begin_decision(step)
 reference=m.action_report(s);first=c.report(s);again=c.report(s)
 assert canon(reference)==canon(first)==canon(again)
 first[0]['allowed']=not first[0]['allowed']
 assert canon(c.report(s))==canon(reference),'MUTATION_LEAK'
 checked+=1
# The saved node ordering is an offline micro-workload, NOT actual rollout request ordering.
# Fixed two passes over each saved-state list. Rebuild caches each repeat; rotate method order.
def timed(kind,profile=False):
 models={}; caches={}
 for case,step,token,cfg,s in rows:
  key=(case,token)
  if key not in models:
   m=DestinationStopTransition(TransitionConfig(**cfg));models[key]=m
   if kind!='original':caches[key]=(old if kind=='previous_cache' else new).ExactReportCache(m,enabled=True)
 profiler=cProfile.Profile() if profile else None
 if profiler:profiler.enable()
 start=time.process_time_ns()
 for repeat in range(2):
  for case,step,token,cfg,s in rows:
   key=(case,token)
   if kind=='original':models[key].action_report(s)
   else:caches[key].report(s)
 dt=(time.process_time_ns()-start)/1e6
 if profiler:
  profiler.disable();stream=io.StringIO();pstats.Stats(profiler,stream=stream).sort_stats('cumtime').print_stats(25)
  (WORK/'next_proposal/tests/previous_cache_profile.txt').write_text(stream.getvalue())
 return dt, {k:sum(c.stats[k] for c in caches.values()) for k in ['requests','hits','full_report_evaluations']}
methods=['original','previous_cache','flat_cache'];times={k:[] for k in methods};stats={}
for rep in range(6):
 for k in methods[rep%3:]+methods[:rep%3]:
  dt,st=timed(k);times[k].append(dt);stats[k]=st
_,_=timed('previous_cache',True)
result={'status':'PASS_SAVED_SCALAR_REPORT_EQUIVALENCE','saved_vehicle_state_records':checked,'direct_cached_value_and_mutation_isolation':True,
 'new_mcts_calls':0,'new_teacher_records':0,'new_training_runs':0,'local_python':sys.version,'cloud_executed':False,
 'microbenchmark_only':{'requests_per_repeat':len(rows)*2,'repeat_count':6,'order':'rotating original/previous_cache/flat_cache',
 'cpu_ms':times,'median_cpu_ms':{k:statistics.median(v) for k,v in times.items()},'cache_counts':stats,
 'limitations':['saved explicit tree node order, not original rollout sequence','local Python/environment, no extrapolation to complete search speed','not a statistical benchmark','no vehicle advancement']}}
(WORK/'next_proposal/tests/SAVED_REPORT_TEST.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
