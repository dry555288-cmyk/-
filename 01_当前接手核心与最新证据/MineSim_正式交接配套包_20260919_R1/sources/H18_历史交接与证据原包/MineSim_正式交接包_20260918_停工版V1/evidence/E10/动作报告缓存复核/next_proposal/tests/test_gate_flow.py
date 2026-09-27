"""Gate lifecycle tests use a synthetic runner; NEVER call a real search."""
from pathlib import Path
import sys,tempfile,shutil,json,hashlib,contextlib,io
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;REL=HERE.parent/'release';sys.path.insert(0,str(REL));import gate
ROOT=HERE.parents[1]/'raw/minesim_dual_reportcache_v1'
obs={'resources':lambda _: {'effective_cpu':1.,'memory_available_bytes':2*1024**3,'free_disk_bytes':1024**3,'resource':'LOW'},
 'git':lambda _: {'head':'SYNTHETIC','status':'','staged_diff_sha256':'SYNTHETIC','unstaged_diff_sha256':'SYNTHETIC'},
 'processes':lambda: {'matches':[],'unreadable':[],'ancestors':[]}}
logs=[]
for kind in ['synthetic_success','missing_source','bad_sha','related_process']:
 with tempfile.TemporaryDirectory() as td:
  td=Path(td);data=td/'data';data.mkdir();release=td/'release';shutil.copytree(REL,release)
  bindings=json.loads((release/'SOURCE_BINDINGS.json').read_bytes())
  for rel in bindings['members']:
   d=data/gate.PARENT/rel;d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/rel,d)
  (release/'experiment.py').write_text('''from pathlib import Path\nimport json\ndef run(runtime,output,protocol,progress,*,local_test=False):\n assert local_test\n Path(output).mkdir()\n progress('SYNTHETIC_ONLY',{'search_started':0,'search_completed':0,'outer_steps_started':0,'outer_steps_completed':0},{'test':True})\n result={'status':'SYNTHETIC_GATE_ONLY_NOT_MCTS','local_test':True,'new_mcts_calls':0}\n (Path(output)/'RESULT.json').write_text(json.dumps(result))\n return result\n''')
  m={p.name:{'size':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in release.iterdir() if p.name!='RELEASE_MANIFEST.json'};(release/'RELEASE_MANIFEST.json').write_text(json.dumps(m))
  observers=dict(obs)
  if kind=='missing_source':(data/gate.PARENT/'RC.txt').unlink()
  if kind=='bad_sha':(data/gate.PARENT/'RC.txt').write_text('2\n')
  if kind=='related_process':observers['processes']=lambda:{'matches':[{'synthetic':True}],'unreadable':[],'ancestors':[]}
  stream=io.StringIO()
  with contextlib.redirect_stdout(stream):rc=gate.execute(release,data,td,local_test=True,observer=observers)
  result=json.loads((data/gate.NAME/'RESULT.json').read_bytes())
  assert rc==(0 if kind=='synthetic_success' else 2)
  assert (data/(gate.NAME+'.zip')).exists()
  assert result.get('mcts_calls_started',0)==0
  if kind!='synthetic_success':assert result['technical_start']==False
  if kind=='synthetic_success':
   with contextlib.redirect_stdout(stream):rc2=gate.execute(release,data,td,local_test=True,observer=observers)
   assert rc2==2
  logs.append({'case':kind,'rc':rc,'status':result['status'],'bundle_saved':True,'new_mcts_calls':0,'log':stream.getvalue()})
(HERE/'GATE_FLOW_RESULT.json').write_text(json.dumps({'cases':logs,'cases_passed':len(logs),'synthetic_runner_only':True,'real_MCTS_calls':0},ensure_ascii=False,indent=2)+'\n')
print('GATE_SYNTHETIC_CASES_PASS='+str(len(logs)))
