"""Synthetic lifecycle testing ONLY. Does not run MCTS or load vehicle engines."""
import sys,tempfile,shutil,json,hashlib,contextlib,io
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE/'release'))
import gate
RAW=Path('/mnt/data/minesim_treeprobe_review_current/raw/minesim_dual_treeprobe_v1')
FAKE='''from pathlib import Path
import json
def run(runtime,output,protocol,progress,*,local_test=False):
 assert local_test is True
 assert (Path(runtime)/"candidate_mcts/fleet_search.py").exists()
 out=Path(output);out.mkdir()
 counters=dict(search_started=8,search_completed=8,outer_steps_started=8,outer_steps_completed=8)
 progress("SEARCH_AND_ONE_STEP_SAVED",counters,{"synthetic_only":True})
 result=dict(status="PASS_DUAL_ACTION_REPORT_CACHE_EQUIVALENCE_SMOKE",counters=counters,local_test=True,synthetic_only=True,actual_MCTS_calls=0)
 (out/"RESULT.json").write_text(json.dumps(result))
 return result
'''
def manifest(release):
 m={p.name:{'size':len(p.read_bytes()),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in release.iterdir() if p.is_file() and p.name!='RELEASE_MANIFEST.json'}
 (release/'RELEASE_MANIFEST.json').write_text(json.dumps(m))
def setup(root):
 data=root/'data';data.mkdir();p=data/gate.PARENT;shutil.copytree(RAW,p)
 rel=root/'release';shutil.copytree(HERE/'release',rel);(rel/'experiment.py').write_text(FAKE);manifest(rel)
 return data,rel
obs={'resources':lambda d:{'effective_cpu':0.5,'memory_available_bytes':2*1024**3,'free_disk_bytes':2*1024**3},'git':lambda r:{'synthetic_git':'fixed'},'processes':lambda :{'matches':[],'unreadable':[],'synthetic_only':True}}
checks=[]
for mode in ('complete','missing','bad_sha','git_changed'):
 with tempfile.TemporaryDirectory() as td:
  root=Path(td);data,rel=setup(root)
  if mode=='missing':(data/gate.PARENT/'parent_sources/runtime/reference_paths.json').unlink()
  if mode=='bad_sha':(data/gate.PARENT/'parent_sources/runtime/reference_paths.json').write_text('synthetic_corrupt_test_only')
  ob=dict(obs)
  if mode=='git_changed':
   calls=[]
   def g(r):calls.append(1);return {'synthetic_git_calls':len(calls)}
   ob['git']=g
  with contextlib.redirect_stdout(io.StringIO()):rc=gate.execute(rel,data,root,local_test=True,observer=ob)
  result=json.loads((data/gate.NAME/'RESULT.json').read_text())
  assert (data/(gate.NAME+'.zip')).exists()
  if mode=='complete':
   assert rc==0 and result['sources_verified']==65 and result['mcts_calls_completed']==8
   content=(data/gate.NAME/'RESULT.json').read_bytes()
   with contextlib.redirect_stdout(io.StringIO()):second=gate.execute(rel,data,root,local_test=True,observer=ob)
   assert second==2 and content==(data/gate.NAME/'RESULT.json').read_bytes()
  elif mode=='git_changed':assert rc==2 and result['status']=='HOLD_POSTCHECK'
  else:assert rc==2 and result['mcts_calls_started']==0 and not result['technical_start']
  checks.append({'case':mode,'status':'PASS','simulated_executor_only':True})
report={'tests_run':4,'passed':4,'actual_MCTS_calls':0,'actual_training_runs':0,'synthetic_counter_8_is_not_actual_searches':True,'cases':checks}
(HERE/'GATE_FLOW_TEST_RESULT.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
