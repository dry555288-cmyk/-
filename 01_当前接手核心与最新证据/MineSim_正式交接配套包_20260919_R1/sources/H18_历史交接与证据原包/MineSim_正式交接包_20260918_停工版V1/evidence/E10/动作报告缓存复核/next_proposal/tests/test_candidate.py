from pathlib import Path
import sys,unittest,json,math,tempfile,shutil,hashlib,zipfile,io
from dataclasses import dataclass,replace,fields
from enum import IntEnum
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent; REL=HERE.parent/'release';sys.path.insert(0,str(REL))
import action_cache as ac, gate, experiment
ROOT=HERE.parents[1]/'raw/minesim_dual_reportcache_v1'
ACTION_ACCEL={0:-3.,1:-1.5,2:0.,3:1.};VERSION='TEST_ONLY'
@dataclass(frozen=True)
class Config: dt:float=.5; goal:float=100.
@dataclass(frozen=True)
class State: position:float=1.;speed:float=2.;time:float=3.;parked:bool=False
class Model:
 def __init__(self):self.cfg=Config();self.goal_window_m=.5;self.action_to_accel=dict(ACTION_ACCEL);self.count=0;self.validations=0
 def validate(self,s):
  self.validations+=1
  if not isinstance(s,State) or not math.isfinite(s.position) or s.position<0:raise ValueError('INVALID')
 def action_report(self,s):
  self.validate(s);self.count+=1
  return ({'p':s.position+s.speed*self.cfg.dt,'allowed':s.position<=self.cfg.goal},)
class E(IntEnum):ZERO=0
class Tests(unittest.TestCase):
 def test_atoms_types(self):self.assertNotEqual(ac.atom(1),ac.atom(True));self.assertNotEqual(ac.atom(1),ac.atom(1.));self.assertNotEqual(ac.atom(0),ac.atom(E.ZERO))
 def test_signed_zero(self):self.assertNotEqual(ac.atom(-0.),ac.atom(0.))
 def test_nextafter(self):self.assertNotEqual(ac.atom(1.),ac.atom(math.nextafter(1.,2.)))
 def test_nan(self):
  with self.assertRaises(ValueError):ac.atom(float('nan'))
 def test_mutable_key(self):
  with self.assertRaises(TypeError):ac.atom([])
 def test_all_fields(self):
  c=ac.ExactReportCache(Model(),enabled=True);s=State()
  for kw in [{'time':4.},{'position':2.},{'speed':3.},{'parked':True}]:self.assertNotEqual(c.flat_dataclass(s),c.flat_dataclass(replace(s,**kw)))
 def test_type_identity(self):
  @dataclass(frozen=True)
  class Other: position:float=1.;speed:float=2.;time:float=3.;parked:bool=False
  c=ac.ExactReportCache(Model(),enabled=True);self.assertNotEqual(c.flat_dataclass(State()),c.flat_dataclass(Other()))
 def test_hit_parity(self):
  m=Model();c=ac.ExactReportCache(m,enabled=True);a=c.report(State());b=c.report(State());self.assertEqual(a,b);self.assertEqual(m.count,1);self.assertEqual(c.stats['hits'],1)
 def test_miss_output_isolation(self):
  c=ac.ExactReportCache(Model(),enabled=True);c.report(State())[0]['p']=-1;self.assertEqual(c.report(State())[0]['p'],2.)
 def test_hit_output_isolation(self):
  c=ac.ExactReportCache(Model(),enabled=True);c.report(State());c.report(State())[0]['p']=-1;self.assertEqual(c.report(State())[0]['p'],2.)
 def test_nested_report_refused(self):
  with self.assertRaises(TypeError):ac.ensure_flat_report(({'nested':[]},))
 def test_validate_every_hit(self):
  m=Model();c=ac.ExactReportCache(m,enabled=True);c.report(State());n=m.validations;c.report(State());self.assertEqual(m.validations,n+1)
 def test_validate_error_not_hidden(self):
  m=Model();c=ac.ExactReportCache(m,enabled=True);c.report(State())
  def fail(_):raise ValueError('INVALID_NOW')
  m.validate=fail
  with self.assertRaisesRegex(ValueError,'INVALID_NOW'):c.report(State())
 def test_exception_not_cached(self):
  c=ac.ExactReportCache(Model(),enabled=True)
  with self.assertRaises(ValueError):c.report(State(position=-1.))
  self.assertFalse(c.entries)
 def test_config_invalidates(self):
  m=Model();c=ac.ExactReportCache(m,enabled=True);a=c.report(State());m.cfg=replace(m.cfg,dt=1.);b=c.report(State());self.assertNotEqual(a,b);self.assertEqual(c.stats['config_invalidations'],1)
 def test_model_map_invalidates(self):
  m=Model();c=ac.ExactReportCache(m,enabled=True);c.report(State());m.action_to_accel[0]=-2.;c.report(State());self.assertEqual(m.count,2)
 def test_global_map_invalidates(self):
  m=Model();c=ac.ExactReportCache(m,enabled=True);c.report(State());v=ACTION_ACCEL[0]
  try:ACTION_ACCEL[0]=-2.;c.report(State());self.assertEqual(m.count,2)
  finally:ACTION_ACCEL[0]=v
 def test_version_invalidates(self):
  global VERSION
  m=Model();c=ac.ExactReportCache(m,enabled=True);c.report(State());v=VERSION
  try:VERSION='OTHER';c.report(State());self.assertEqual(m.count,2)
  finally:VERSION=v
 def test_window_invalidates(self):
  m=Model();c=ac.ExactReportCache(m,enabled=True);c.report(State());m.goal_window_m=.6;c.report(State());self.assertEqual(m.count,2)
 def test_baseline(self):
  m=Model();c=ac.ExactReportCache(m,enabled=False);c.report(State());c.report(State());self.assertEqual(m.count,2);self.assertFalse(c.entries)
 def test_capacity_lru(self):
  c=ac.ExactReportCache(Model(),enabled=True,capacity=2);c.report(State());c.report(State(position=2.));c.report(State());c.report(State(position=3.));n=c.stats['full_report_evaluations'];c.report(State());self.assertEqual(c.stats['full_report_evaluations'],n);c.report(State(position=2.));self.assertEqual(c.stats['full_report_evaluations'],n+1)
 def test_cross_decision(self):
  c=ac.ExactReportCache(Model(),enabled=True);c.begin_decision(0);c.report(State());c.begin_decision(1);c.report(State());self.assertEqual(c.stats['cross_decision_hits'],1)
 def test_close(self):
  m=Model();c=ac.ExactReportCache(m,enabled=True);c.install();c.report(State());c.close();self.assertNotIn('action_report',m.__dict__);self.assertFalse(c.entries)
 def test_existing_override_restore(self):
  m=Model();f=m.action_report;m.action_report=f;c=ac.ExactReportCache(m,enabled=True);c.install();c.close();self.assertIs(m.action_report,f)
 def test_double_install(self):
  c=ac.ExactReportCache(Model(),enabled=True);c.install()
  with self.assertRaises(RuntimeError):c.install()
  c.close()
 def test_capacity_invalid(self):
  for v in [0,-1,True,1.5]:
   with self.assertRaises(ValueError):ac.ExactReportCache(Model(),enabled=True,capacity=v)
 def test_claim_once(self):
  with tempfile.TemporaryDirectory() as td:
   gate.claim(Path(td))
   with self.assertRaises(RuntimeError):gate.claim(Path(td))
 def test_claim_symlink(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td);(p/gate.NAME).symlink_to(p/'missing')
   with self.assertRaises(RuntimeError):gate.claim(p)
 def test_duplicate_json(self):
  with self.assertRaises(RuntimeError):gate.parse(b'{"x":1,"x":2}')
 def test_paths(self):
  for v in ['/a','../x','a/../b','a\\b']:
   with self.assertRaises(RuntimeError):gate.safe_rel(v)
 def test_process_filter(self):
  self.assertTrue(gate.related(['bash','/root/autodl-tmp/run_dual_reportcache_flat.sh']))
  self.assertTrue(gate.related(['python','/root/autodl-tmp/minesim_dual_reportcache_flat_v1_release/gate.py']))
  self.assertFalse(gate.related(['tail','/root/autodl-tmp/run_dual_reportcache_flat.sh']))
 def test_bound_files(self):
  b=json.loads((REL/'SOURCE_BINDINGS.json').read_bytes());mp=json.loads((ROOT/'MANIFEST.json').read_bytes())
  for n,v in b['members'].items():
   raw=(ROOT/n).read_bytes();self.assertEqual({'sha256':hashlib.sha256(raw).hexdigest(),'size':len(raw)},v)
   if n!='MANIFEST.json':self.assertEqual(mp[n],v)
 def test_parent_zip_read(self):
  b=json.loads((REL/'SOURCE_BINDINGS.json').read_bytes())
  with tempfile.TemporaryDirectory() as td:
   data=Path(td);shutil.copyfile(ROOT.parents[2]/'4bb5fc89-fd14-4d31-b859-509fbff22b08.zip',data/(gate.PARENT+'.zip'))
   src,loc=gate.source_contents(data,b);self.assertEqual(len(src),64);self.assertTrue(all(v['kind']=='known_parent_zip' for v in loc.values()))
 def test_bundle(self):
  with tempfile.TemporaryDirectory() as td:
   out=Path(td)/gate.NAME;out.mkdir();gate.put(out/'RESULT.json',{'unit':True});zp,count=gate.bundle(out);self.assertTrue(zp.exists());self.assertEqual(count,1)
 def test_compare_rejects_reward_and_q(self):
  base=json.loads((ROOT/'native/coverage_policy_01__step0014/baseline_0.json').read_bytes());other=json.loads(json.dumps(base));other['diagnostics']['elapsed_ms']=0.;experiment.compare(base,other)
  other['reward']+=1.
  with self.assertRaises(RuntimeError):experiment.compare(base,other)
 def test_no_core_modification(self):
  b=json.loads((REL/'SOURCE_BINDINGS.json').read_bytes())
  for p,m in b['members'].items():
   if '/candidate_mcts/' in p:self.assertEqual(hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),m['sha256'])
 def test_protocol_unchanged_search(self):
  p=json.loads((REL/'PROTOCOL.json').read_bytes());self.assertEqual(p['max_search_calls'],8);self.assertEqual(p['mcts_config'],{'budget':64,'max_depth':8,'c_uct':1.4,'gamma':.99,'dt':.5});self.assertFalse(p['auto_retry']);self.assertFalse(p['production_install'])
if __name__=='__main__':
 log=io.StringIO();r=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests));print(log.getvalue());(HERE/'UNIT_TEST_LOG.txt').write_text(log.getvalue());(HERE/'UNIT_TEST_RESULT.json').write_text(json.dumps({'tests':r.testsRun,'failures':len(r.failures),'errors':len(r.errors),'MCTS_calls':0,'training_runs':0,'teacher_samples':0},indent=2)+'\n');sys.exit(0 if r.wasSuccessful() else 1)
