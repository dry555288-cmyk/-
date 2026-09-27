import sys, math, unittest, tempfile, json, hashlib, shutil
from pathlib import Path
from dataclasses import dataclass, replace
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE/'release'))
from action_cache import ExactReportCache, identity
import gate
ACTION_ACCEL={0:-3.0,1:-1.5,2:0.0,3:1.0};VERSION='TEST_ONLY'
@dataclass(frozen=True)
class Config:dt:float=0.5;goal:float=100.0
@dataclass(frozen=True)
class State:position:float=1.0;speed:float=2.0;time:float=3.0;parked:bool=False
class Model:
 def __init__(self):self.cfg=Config();self.goal_window_m=0.5;self.action_to_accel=dict(ACTION_ACCEL);self.count=0
 def validate(self,s):
  if not isinstance(s,State) or not math.isfinite(s.position) or s.position<0:raise ValueError('INVALID')
 def action_report(self,s):
  self.validate(s);self.count+=1
  return ({'p':s.position+s.speed*self.cfg.dt,'allowed':s.position<=self.cfg.goal},)
class Tests(unittest.TestCase):
 def test_key_types(self):self.assertNotEqual(identity(True),identity(1));self.assertNotEqual(identity(1),identity(1.0))
 def test_signed_zero(self):self.assertNotEqual(identity(-0.),identity(0.))
 def test_tiny_value(self):self.assertNotEqual(identity(1.),identity(math.nextafter(1.,2.)))
 def test_nan_rejected(self):
  with self.assertRaises(ValueError):identity(float('nan'))
 def test_all_state_fields(self):
  s=State()
  for kw in ({'time':4.0},{'speed':3.0},{'position':2.0},{'parked':True}):self.assertNotEqual(identity(s),identity(replace(s,**kw)))
 def test_cache_equivalence(self):
  m=Model();c=ExactReportCache(m,enabled=True);c.install();a=m.action_report(State());b=m.action_report(State());self.assertEqual(a,b);self.assertEqual(m.count,1);self.assertEqual(c.stats['hits'],1);c.close()
 def test_returns_not_shared(self):
  m=Model();c=ExactReportCache(m,enabled=True);c.install();a=m.action_report(State());a[0]['allowed']=False
  self.assertTrue(m.action_report(State())[0]['allowed']);c.close()
 def test_invalid_not_cached(self):
  m=Model();c=ExactReportCache(m,enabled=True);c.install();m.action_report(State())
  with self.assertRaises(ValueError):m.action_report(State(position=-1.0))
  self.assertEqual(len(c.entries),1);c.close()
 def test_config_invalidated(self):
  m=Model();c=ExactReportCache(m,enabled=True);c.install();a=m.action_report(State());m.cfg=replace(m.cfg,dt=1.0);b=m.action_report(State());self.assertNotEqual(a,b);self.assertEqual(c.stats['config_invalidations'],1);c.close()
 def test_action_map_invalidated(self):
  m=Model();c=ExactReportCache(m,enabled=True);c.install();m.action_report(State());m.action_to_accel[0]=-2.;m.action_report(State());self.assertEqual(m.count,2);c.close()
 def test_window_invalidated(self):
  m=Model();c=ExactReportCache(m,enabled=True);c.install();m.action_report(State());m.goal_window_m=0.6;m.action_report(State());self.assertEqual(m.count,2);c.close()
 def test_baseline_does_not_cache(self):
  m=Model();c=ExactReportCache(m,enabled=False);c.install();m.action_report(State());m.action_report(State());self.assertEqual(m.count,2);self.assertEqual(len(c.entries),0);c.close()
 def test_capacity(self):
  m=Model();c=ExactReportCache(m,enabled=True,capacity=1);c.install();m.action_report(State());m.action_report(State(position=2.0));m.action_report(State());self.assertEqual(c.stats['evictions'],2);self.assertEqual(len(c.entries),1);c.close()
 def test_cross_decision(self):
  m=Model();c=ExactReportCache(m,enabled=True);c.install();c.begin_decision(0);m.action_report(State());c.begin_decision(1);m.action_report(State());self.assertEqual(c.stats['cross_decision_hits'],1);c.close()
 def test_close_restores_method(self):
  m=Model();c=ExactReportCache(m,enabled=True);c.install();c.close();self.assertNotIn('action_report',m.__dict__);self.assertEqual(m.action_report.__func__,Model.action_report)
 def test_overridden_method_restored(self):
  m=Model();old=m.action_report;m.action_report=old;c=ExactReportCache(m,enabled=True);c.install();c.close();self.assertIs(m.__dict__['action_report'],old)
 def test_install_twice_refused(self):
  m=Model();c=ExactReportCache(m,enabled=True);c.install()
  with self.assertRaises(RuntimeError):c.install()
  c.close()
 def test_no_shared_context(self):
  a,b=Model(),Model();ca,cb=ExactReportCache(a,enabled=True),ExactReportCache(b,enabled=True);ca.report(State());cb.report(State());self.assertEqual((a.count,b.count),(1,1))
 def test_invalid_capacity(self):
  with self.assertRaises(ValueError):ExactReportCache(Model(),enabled=True,capacity=0)
 def test_source_original_not_modified(self):
  source=(Path('/mnt/data/minesim_treeprobe_review_current/raw/minesim_dual_treeprobe_v1/parent_sources/runtime/candidate_mcts/dual_stop_motion_v1.py')).read_bytes()
  c=ExactReportCache(Model(),enabled=True);c.report(State());c.close()
  self.assertEqual(source,(Path('/mnt/data/minesim_treeprobe_review_current/raw/minesim_dual_treeprobe_v1/parent_sources/runtime/candidate_mcts/dual_stop_motion_v1.py')).read_bytes())
 def test_claim_once(self):
  with tempfile.TemporaryDirectory() as td:
   d=Path(td);gate.claim(d)
   with self.assertRaises(RuntimeError):gate.claim(d)
 def test_claim_symlink_refused(self):
  with tempfile.TemporaryDirectory() as td:
   d=Path(td);(d/gate.NAME).symlink_to(d/'absent')
   with self.assertRaises(RuntimeError):gate.claim(d)
 def test_parser_duplicate_refused(self):
  with self.assertRaises(RuntimeError):gate.parse(b'{"x":1,"x":2}')
 def test_safe_rel(self):
  for s in ['../x','/a','a/../b','a\\b']:
   with self.assertRaises(RuntimeError):gate.safe_rel(s)
 def test_process_only_real_executor(self):
  self.assertTrue(gate.related(['bash','/root/autodl-tmp/run_dual_reportcache.sh','--authorize-reportcache-once']))
  self.assertFalse(gate.related(['tail','/root/autodl-tmp/run_dual_reportcache.sh']))
 def test_bundling(self):
  with tempfile.TemporaryDirectory() as td:
   d=Path(td);out=d/gate.NAME;out.mkdir();gate.put(out/'RESULT.json',{'only':'unit test'});zp,n=gate.bundle(out);self.assertTrue(zp.exists());self.assertEqual(n,1)
 def test_parity_detects_changes(self):
  import experiment
  base={k:0 for k in ('before','action_id','after','reward','detail','rng_before','rng_after','search_transition_counts')};base['diagnostics']={'elapsed_ms':1,'q_values':[0.]}
  other=json.loads(json.dumps(base));other['diagnostics']['elapsed_ms']=200;experiment.compare(base,other)
  other['diagnostics']['q_values']=[1.]
  with self.assertRaises(RuntimeError):experiment.compare(base,other)
 def test_source_bindings_true(self):
  b=gate.parse((HERE/'release/SOURCE_BINDINGS.json').read_bytes());root=Path('/mnt/data/minesim_treeprobe_review_current/raw/minesim_dual_treeprobe_v1');mp=gate.parse((root/'MANIFEST.json').read_bytes())
  for n,v in b['members'].items():
   raw=(root/n).read_bytes();self.assertEqual({'sha256':hashlib.sha256(raw).hexdigest(),'size':len(raw)},v)
   if n!='MANIFEST.json':self.assertEqual(mp[n],v)
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
 (HERE/'UNIT_TEST_RESULT.json').write_text(json.dumps({'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'real_MCTS_calls':0,'training_runs':0,'teacher_samples':0},indent=2)+'\n')
 sys.exit(0 if result.wasSuccessful() else 1)
