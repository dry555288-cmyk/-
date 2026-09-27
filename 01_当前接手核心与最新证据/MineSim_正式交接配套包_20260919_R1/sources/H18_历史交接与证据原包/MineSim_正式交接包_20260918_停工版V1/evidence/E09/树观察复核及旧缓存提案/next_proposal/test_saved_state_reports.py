"""Recompute scalar action reports on saved nodes only; ZERO MCTS searches."""
from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
r=Path('/mnt/data/minesim_treeprobe_review_current/raw/minesim_dual_treeprobe_v1')
runtime=r/'parent_sources/runtime'
sys.path.insert(0,str(runtime));sys.path.insert(0,str(HERE/'release'))
from action_cache import ExactReportCache
from candidate_mcts.dual_stop_motion_v1 import DestinationStopTransition,DualOnlyState
from candidate_mcts.transition_model import TransitionConfig
from candidate_mcts.action_space import MCTSAction

def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
rows=[];checked=0
for case in ['coverage_policy_01__step0014','coverage_policy_05__step0011']:
 rid=case.split('__')[0].replace('coverage_','')
 resolved=json.loads((runtime/'inputs/resolved'/f'{rid}.json').read_bytes())
 models={t:DestinationStopTransition(TransitionConfig(**resolved['transition_config'][t])) for t in ('A','B')}
 cache={t:ExactReportCache(models[t],enabled=True) for t in models}
 for c in cache.values():c.install()
 try:
  for step in (0,1):
   for c in cache.values():c.begin_decision(step)
   obs=json.loads((r/'native'/case/f'observed_{step}.json').read_bytes())
   for node in obs['tree']['nodes']:
    for t,m in models.items():
     d=node['state']['vehicles'][t]
     s=DualOnlyState(**{k:d[k] for k in ('time_s','route_s','speed_mps','accel_mps2','target_speed_mps','collision','goal_reached','parked_at_time_s')},
                    lead_distance_m=float('inf'),lead_rel_speed_mps=0.0,minimum_clearance_m=float('inf'),prev_action=None if d['prev_action'] is None else MCTSAction(d['prev_action']))
     old=cache[t].original(s); a=m.action_report(s); b=m.action_report(s)
     assert canon(old)==canon(a)==canon(b),(case,node['index'],t)
     checked+=1
  rows.append({'case':case,'vehicle_cache_counters':{t:c.snapshot() for t,c in cache.items()}})
 finally:
  for c in cache.values():c.close()
 assert all('action_report' not in m.__dict__ for m in models.values())
result={'status':'PASS_SCALAR_REPORT_PARITY_ON_SAVED_TREE_NODES','vehicle_states_checked':checked,'cached_calls':checked*2,
        'source':'260 node snapshots / 4 observed searches; each node has A/B; not independent scenes',
        'new_MCTS_searches':0,'new_teacher_samples':0,'new_training_runs':0,
        'local_python':sys.version,'cloud_test_done':False,'full_search_parity_tested':False,'cases':rows}
(HERE/'SAVED_STATE_REPORT_TEST.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2))
