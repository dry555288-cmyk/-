from pathlib import Path
import hashlib,importlib.util,json,os,shutil,sys,tempfile,unittest,contextlib,io,zipfile
BASE=Path(__file__).resolve().parent
REL=BASE/'release'
sys.path.insert(0,str(REL))
import gate

def manifest():
    m={p.name:{'size':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in REL.iterdir() if p.is_file() and p.name!='RELEASE_MANIFEST.json'}
    (REL/'RELEASE_MANIFEST.json').write_bytes(gate.canon(m))
manifest()

class Lifecycle(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.data=Path(self.tmp.name)
        self.parent=self.data/gate.PARENT
        self.parent.symlink_to(BASE/gate.PARENT,target_is_directory=True)
        # source reader refuses symlinks: use actual files via copytree for these isolated tests.
        self.parent.unlink();shutil.copytree(BASE/gate.PARENT,self.parent,ignore=shutil.ignore_patterns('__pycache__'))
        self.rel=self.data/'release';shutil.copytree(REL,self.rel,ignore=shutil.ignore_patterns('__pycache__'))
        self.obs={'resources':lambda d:{'effective_cpu':2.,'memory_available_bytes':4*2**30,'free_disk_bytes':4*2**30},
                  'git':lambda r:{'head':'TEST','status':'?? ^C'},
                  'processes':lambda:{'matches':[],'unreadable':[]}}
    def tearDown(self):self.tmp.cleanup()
    def fake(self,rt,out,protocol,progress,local_test=False):
        self.assertTrue(local_test);self.assertTrue((rt/'candidate_mcts/fleet_search.py').exists())
        out.mkdir(); counts={k:16 for k in ('search_started','search_completed','outer_steps_started','outer_steps_completed')}
        progress('POLICY_SAVED',counts,{'root_id':'SYNTHETIC','mode':'rebased','step':1})
        return {'status':'COMPLETE_DUAL_H8_SUBTREE_POLICY4_COMPARISON','tree_reuse_executed':True,'local_test':True,'counters':counts}
    def go(self,runner=None):
        with contextlib.redirect_stdout(io.StringIO()):
            return gate.execute(self.rel,self.data,self.data,local_test=True,observer=self.obs,runner=runner or self.fake)
    def test_complete_and_bundle(self):
        self.assertEqual(self.go(),0)
        with zipfile.ZipFile(self.data/(gate.NAME+'.zip')) as z:
            self.assertIsNone(z.testzip());r=json.loads(z.read(gate.NAME+'/RESULT.json'));self.assertEqual(r['rc'],0);self.assertTrue(r['local_test'])
    def test_second_run_refused(self):
        self.assertEqual(self.go(),0);before=(self.data/(gate.NAME+'.zip')).read_bytes();self.assertEqual(self.go(),2);self.assertEqual((self.data/(gate.NAME+'.zip')).read_bytes(),before)
    def test_missing_input_packaged_before_start(self):
        rel='native/coverage_policy_01__step0014/baseline_0.json';(self.parent/rel).unlink();self.assertEqual(self.go(),2)
        r=json.loads((self.data/gate.NAME/'RESULT.json').read_bytes());self.assertFalse(r['policy_start']);self.assertFalse((self.data/gate.NAME/'POLICY_START.json').exists())
    def test_bad_input_sha(self):
        (self.parent/'RC.txt').write_text('1\n');self.assertEqual(self.go(),2);r=json.loads((self.data/gate.NAME/'RESULT.json').read_bytes());self.assertEqual(r['status'],'HOLD_INPUT_BINDING')
    def test_other_process_blocks(self):
        self.obs['processes']=lambda:{'matches':[{'pid':42}],'unreadable':[]};self.assertEqual(self.go(),2)
        self.assertFalse((self.data/gate.NAME/'POLICY_START.json').exists())
    def test_runtime_exception_saved(self):
        def fail(*a,**k):raise ValueError('SYNTHETIC_EXCEPTION')
        self.assertEqual(self.go(fail),2);p=self.data/gate.NAME
        self.assertIn('SYNTHETIC_EXCEPTION',(p/'ERROR.txt').read_text());self.assertTrue((p/'CAPTURE.json').exists())
    def test_symlink_input_refused(self):
        p=self.parent/'RC.txt';p.unlink();(self.data/'other').write_text('0\n');p.symlink_to(self.data/'other');self.assertEqual(self.go(),2)
    def test_resource_prestart_hold(self):
        self.obs['resources']=lambda d:{'effective_cpu':.1,'memory_available_bytes':2**30,'free_disk_bytes':2**30};self.assertEqual(self.go(),2);self.assertFalse((self.data/gate.NAME/'POLICY_START.json').exists())
    def test_known_parent_zip_only(self):
        z=self.data/(gate.PARENT+'.zip')
        with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as out:
            for p in self.parent.rglob('*'):
                if p.is_file():out.write(p,gate.PARENT+'/'+p.relative_to(self.parent).as_posix())
        shutil.rmtree(self.parent);self.assertEqual(self.go(),0)
    def test_process_prefix(self):
        self.assertTrue(gate.related(['python','/root/autodl-tmp/minesim_dual_subtree_h8_smoke_v1_release/gate.py']))
        self.assertFalse(gate.related(['tail','/root/autodl-tmp/run_dual_subtree_h8.log']))
    def test_bad_release_sha(self):
        (self.rel/'subtree_reuse.py').write_text('changed');self.assertEqual(self.go(),2)
        self.assertFalse((self.data/gate.NAME/'POLICY_START.json').exists())
    def test_no_gpu_or_training_side_effects_in_scope(self):
        self.assertEqual(self.go(),0);r=json.loads((self.data/gate.NAME/'RESULT.json').read_bytes());self.assertEqual(r['new_teacher_traces'],0);self.assertEqual(r['training_runs'],0)

if __name__=='__main__':unittest.main(verbosity=2)
