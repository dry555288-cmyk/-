from pathlib import Path
import copy,hashlib,importlib.util,json,shutil,tempfile,types,unittest,zipfile,ast
from unittest.mock import patch
R=Path('/mnt/data/minesim_flatcache_timing_release_v1')
P=Path('/mnt/data/minesim_flatcache_review_current/raw/minesim_dual_reportcache_flat_v1')
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
exp=load('timing_test_exp',R/'experiment.py');gate=load('timing_test_gate',R/'gate.py')
protocol=json.loads((R/'PROTOCOL.json').read_text());binding=json.loads((R/'SOURCE_BINDINGS.json').read_text())
parent_result=json.loads((P/'native/RESULT.json').read_text())
def snapshot():return {'path':'test/cpu.stat','cpu_stat':{'nr_throttled':0,'usage_usec':10},'/sys/fs/cgroup/cpu.max':'200000 100000','/sys/fs/cgroup/cpu/cpu.cfs_quota_us':None,'/sys/fs/cgroup/cpu/cpu.cfs_period_us':None,'affinity_count':2}
def fake_parent(runtime,out,pr,progress,local_test=False):
 out=Path(out);out.mkdir();result=copy.deepcopy(parent_result)
 result['cases']=sorted(result['cases'],key=lambda c:pr['root_ids'].index(c['root_id']))
 counts=dict(search_started=0,search_completed=0,outer_steps_started=0,outer_steps_completed=0)
 for case in result['cases']:
  for mode in case['order']:
   for step in range(2):
    for k in counts:counts[k]+=1
    progress('SEARCH_AND_ONE_STEP_SAVED',counts,{'root_id':case['root_id'],'mode':mode,'step':step})
 result['local_test']=True;exp.write(out/'RESULT.json',result);return result

def fill_sources(data):
 for rel in binding['members']:
  p=data/gate.PARENT/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((P/rel).read_bytes())

def blocks_fixture(cpu_ratio=.8,wall_ratio=.8):
 blocks=[]
 for des in protocol['blocks']:
  result=copy.deepcopy(parent_result)
  for c in result['cases']:
   for row in c['comparisons']:
    row['cached_cpu_ms']=row['baseline_cpu_ms']*cpu_ratio;row['cached_wall_ms']=row['baseline_wall_ms']*wall_ratio
  blocks.append(dict(des,result=result,resource_delta={'timing_environment_limited':False}))
 return blocks
class Tests(unittest.TestCase):
 def test_01_python39_syntax(self):
  for f in R.glob('*.py'):ast.parse(f.read_text(),feature_version=(3,9))
 def test_02_candidate_byte_identical(self):self.assertEqual((R/'action_cache.py').read_bytes(),(P/'release/action_cache.py').read_bytes())
 def test_03_search_harness_byte_identical(self):self.assertEqual((R/'parent_probe.py').read_bytes(),(P/'release/experiment.py').read_bytes())
 def test_04_protocol_count(self):self.assertEqual(protocol['warmup_search_calls']+protocol['measured_search_calls'],40)
 def test_05_balanced_order(self):self.assertEqual([b['root_order'] for b in protocol['blocks'][1:]],['original','reverse','original','reverse'])
 def test_06_release_verify(self):self.assertEqual(len(gate.verify_release(R)),6)
 def test_07_all_bindings(self):
  for rel,m in binding['members'].items():self.assertEqual(m,{'size':(P/rel).stat().st_size,'sha256':hashlib.sha256((P/rel).read_bytes()).hexdigest()})
 def test_08_parent_manifest(self):
  d=json.loads((P/'MANIFEST.json').read_text())
  for rel,m in binding['members'].items():
   if rel!='MANIFEST.json':self.assertEqual(d[rel],m)
 def test_09_related_timing_launcher(self):self.assertTrue(gate.related(['bash','/root/autodl-tmp/run_dual_cachetiming.sh','--authorize-cachetiming-once']))
 def test_10_tail_not_conflict(self):self.assertFalse(gate.related(['tail','-f','/root/autodl-tmp/run_dual_cachetiming.log']))
 def test_11_other_collection_conflict(self):self.assertTrue(gate.related(['python','/root/autodl-tmp/minesim_grouped_coverage32_collect256.py']))
 def test_12_no_throttle(self):self.assertFalse(exp.quota_diff(snapshot(),snapshot())['timing_environment_limited'])
 def test_13_throttle_limited(self):
  b=snapshot();b['cpu_stat']['nr_throttled']=1;self.assertTrue(exp.quota_diff(snapshot(),b)['timing_environment_limited'])
 def test_14_missing_stat(self):
  b=snapshot();b['cpu_stat']=None;self.assertTrue(exp.quota_diff(snapshot(),b)['timing_environment_limited'])
 def test_15_changed_quota(self):
  b=snapshot();b['/sys/fs/cgroup/cpu.max']='50000 100000';self.assertTrue(exp.quota_diff(snapshot(),b)['timing_environment_limited'])
 def test_16_reset_stat(self):
  b=snapshot();b['cpu_stat']['usage_usec']=0;self.assertTrue(exp.quota_diff(snapshot(),b)['timing_environment_limited'])
 def test_17_summarize_fixed_pairs(self):self.assertEqual(exp.summarize(blocks_fixture())['aggregate']['cpu']['pairs'],16)
 def test_18_warmup_excluded(self):
  blocks=blocks_fixture();blocks[0]['result']['cases'][0]['comparisons'][0]['cached_cpu_ms']=1e20
  self.assertAlmostEqual(exp.summarize(blocks)['aggregate']['cpu']['cached_over_baseline'],.8)
 def test_19_no_best_trial_selection(self):
  blocks=blocks_fixture();blocks[2]['result']['cases'][0]['comparisons'][0]['cached_cpu_ms']*=10
  self.assertEqual(exp.summarize(blocks)['observed_direction_conclusion'],'MIXED_OR_NO_REPRODUCIBLE_DIRECTION_ON_FIXED_INPUTS')
 def test_20_limited_even_if_faster(self):
  blocks=blocks_fixture();blocks[2]['resource_delta']['timing_environment_limited']=True
  self.assertEqual(exp.summarize(blocks)['observed_direction_conclusion'],'TIMING_ENVIRONMENT_LIMITED_KEEP_ALL_RESULTS_NO_AUTO_RETRY')
 def test_21_nonfinite_rejected(self):
  b=blocks_fixture();b[1]['result']['cases'][0]['comparisons'][0]['cached_cpu_ms']=float('nan')
  with self.assertRaises(RuntimeError):exp.summarize(b)
 def test_22_extra_block_rejected(self):
  b=blocks_fixture();b.append(b[-1])
  with self.assertRaises(RuntimeError):exp.summarize(b)
 def test_23_mock40_driver(self):
  with tempfile.TemporaryDirectory() as t:
   d=Path(t);shutil.copytree(P/'native',d/'parent_sources/native')
   seen=[];res=exp.run(d/'unused_runtime',d/'native',protocol,lambda e,c,w:seen.append(dict(c)),local_test=True,parent_run=fake_parent,snapshot_fn=snapshot)
   self.assertEqual(res['counters']['search_completed'],40);self.assertEqual(len(seen),40)
   self.assertEqual(res['measured_searches'],32);self.assertEqual(res['warmup_searches'],8)
   self.assertFalse(res['deployable']);self.assertFalse(res['dataset32_512_written'])
 def test_24_stops_on_failed_parity(self):
  with tempfile.TemporaryDirectory() as t:
   d=Path(t);shutil.copytree(P/'native',d/'parent_sources/native')
   def fail(*a,**kw):
    x=fake_parent(*a,**kw);x['status']='FAIL';return x
   with self.assertRaisesRegex(RuntimeError,'BLOCK_EQUIVALENCE_FAILED'):exp.run(d/'runtime',d/'native',protocol,lambda *a:None,local_test=True,parent_run=fail,snapshot_fn=snapshot)
   self.assertFalse((d/'native/measure_01').exists());self.assertTrue((d/'native/warmup/RESOURCE_AFTER.json').exists())
 def test_25_namespace_refuses_reuse(self):
  with tempfile.TemporaryDirectory() as t:
   gate.claim(Path(t))
   with self.assertRaisesRegex(RuntimeError,'EXISTING_NAMESPACE'):gate.claim(Path(t))
 def test_26_symlink_refused(self):
  with tempfile.TemporaryDirectory() as t:
   d=Path(t);(d/'s').symlink_to('/tmp')
   with self.assertRaises(RuntimeError):gate.read_stable(d/'s/f')
 def test_27_sources_exact_directory(self):
  with tempfile.TemporaryDirectory() as t:
   d=Path(t);fill_sources(d);a,loc=gate.source_contents(d,binding);self.assertEqual(len(a),69)
 def test_28_bad_sha_rejected(self):
  with tempfile.TemporaryDirectory() as t:
   d=Path(t);fill_sources(d);(d/gate.PARENT/'RESULT.json').write_bytes(b'{}')
   with self.assertRaisesRegex(RuntimeError,'PARENT_SHA_OR_SIZE'):gate.source_contents(d,binding)
 def test_29_missing_source_rejected(self):
  with tempfile.TemporaryDirectory() as t:
   with self.assertRaises(FileNotFoundError):gate.source_contents(Path(t),binding)
 def test_30_low_resources_no_search(self):
  with tempfile.TemporaryDirectory() as t:
   d=Path(t);obs={'resources':lambda d:{'effective_cpu':.5,'memory_available_bytes':5*1024**3,'free_disk_bytes':5*1024**3},'processes':lambda:{'matches':[],'unreadable':[]}}
   rc=gate.execute(R,data=d,repo=d,local_test=True,observer=obs)
   result=json.loads((d/gate.NAME/'RESULT.json').read_text());self.assertEqual(rc,2);self.assertFalse(result['technical_start']);self.assertEqual(result['mcts_calls_started'],0);self.assertTrue((d/(gate.NAME+'.zip')).exists())
 def test_31_mock_full_lifecycle(self):
  with tempfile.TemporaryDirectory() as t:
   d=Path(t);fill_sources(d)
   obs={'resources':lambda d:{'effective_cpu':4,'memory_available_bytes':5*1024**3,'free_disk_bytes':5*1024**3},'processes':lambda:{'matches':[],'unreadable':[]},'git':lambda d:{'head':'synthetic','status':'original-untracked'}}
   def driver(runtime,out,pr,prog,**kw):return exp.run(runtime,out,pr,prog,parent_run=fake_parent,snapshot_fn=snapshot,**kw)
   module=types.SimpleNamespace(run=driver);spec=types.SimpleNamespace(loader=types.SimpleNamespace(exec_module=lambda m:None))
   with patch.object(gate.importlib.util,'spec_from_file_location',return_value=spec),patch.object(gate.importlib.util,'module_from_spec',return_value=module):
    rc=gate.execute(R,data=d,repo=d,local_test=True,observer=obs)
   result=json.loads((d/gate.NAME/'RESULT.json').read_text());self.assertEqual(rc,0);self.assertEqual(result['mcts_calls_completed'],40);self.assertEqual(result['sources_verified'],69)
   with zipfile.ZipFile(d/(gate.NAME+'.zip')) as z:self.assertIsNone(z.testzip())
   self.assertEqual((d/gate.PARENT/'RESULT.json').read_bytes(),(P/'RESULT.json').read_bytes())

if __name__=='__main__':
 suite=unittest.defaultTestLoader.loadTestsFromTestCase(Tests)
 result=unittest.TextTestRunner(verbosity=2).run(suite)
 summary={'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'successful':result.wasSuccessful(),'local_scope':'Static checks, arithmetic tests and synthetic/replayed lifecycle only. Forty mocked counter callbacks are not executed MCTS searches. Source files checked byte-for-byte.','actual_mcts_calls':0,'actual_model_fits':0,'teacher_samples':0,'cloud_executed':False}
 Path('/mnt/data/minesim_flatcache_review_current/analysis/TIMING_RELEASE_TESTS.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
 raise SystemExit(0 if result.wasSuccessful() else 1)
