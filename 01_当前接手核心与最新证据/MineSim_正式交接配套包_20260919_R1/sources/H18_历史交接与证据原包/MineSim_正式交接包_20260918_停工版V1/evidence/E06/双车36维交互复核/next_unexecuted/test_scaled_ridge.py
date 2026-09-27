import unittest,sys,json,tempfile,hashlib,zipfile,copy,subprocess
from unittest.mock import patch
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).parent))
import scaled_ridge as K
import runner as R
import io_helpers as H
import process_checks as P
BASE=Path(__file__).parent
CURRENT=Path('/mnt/data/minesim_dual32_interaction_review_20260917/original')

class TestNumerics(unittest.TestCase):
 def setUp(self):
  self.rng=np.random.RandomState(13007);self.X=self.rng.normal(size=(28,36));self.X[:,3]=.7;self.X[:,4]=self.X[:,0]*2;self.y=self.rng.normal(size=28)
 def test_population_center_scale(self):
  z,s=K.prepare(self.X);a=np.asarray(s['active_columns']);self.assertTrue(np.allclose(z[:,a].mean(0),0));self.assertTrue(np.allclose((z[:,a]**2).mean(0),1));self.assertTrue((z[:,~a]==0).all())
 def test_train_only_no_held_dependency(self):
  z,s=K.prepare(self.X);old=copy.deepcopy(s);K.transform(np.ones((4,36))*1e8,s);self.assertEqual(old,s)
 def test_constant_held_new_values_zeroed(self):
  _,s=K.prepare(self.X);held=self.X[:4].copy();held[:,3]=100;self.assertTrue((K.transform(held,s)[:,3]==0).all())
 def test_closed_form_matches_augmented_lstsq_synthetic(self):
  m=K.fit(self.X,self.y);z=K.transform(self.X,m['scaler']);a=np.column_stack([z,np.ones(28)]);pen=np.column_stack([np.sqrt(28)*np.eye(36),np.zeros(36)]);coef=np.linalg.lstsq(np.vstack([a,pen]),np.r_[self.y,np.zeros(36)],rcond=None)[0];self.assertTrue(np.allclose(coef[:-1],m['weights']));self.assertAlmostEqual(coef[-1],m['bias'])
 def test_save_reload_forward(self):
  m=K.fit(self.X,self.y);loaded=json.loads(json.dumps(m));self.assertTrue(np.array_equal(K.predict(m,self.X),K.predict(loaded,self.X)))
 def test_permuted_train_rows(self):
  a=K.fit(self.X,self.y);ix=self.rng.permutation(28);b=K.fit(self.X[ix],self.y[ix]);self.assertTrue(np.allclose(K.predict(a,self.X),K.predict(b,self.X),rtol=1e-10,atol=1e-10))
 def test_column_scaling_invariance_active(self):
  a=K.fit(self.X,self.y);f=np.linspace(.3,9,36);b=K.fit(self.X*f,self.y);self.assertTrue(np.allclose(K.predict(a,self.X),K.predict(b,self.X*f)))
 def test_singular_features_ridge_finite(self):
  a=K.fit(np.tile(np.arange(28.)[:,None],(1,36)),self.y);self.assertTrue(np.isfinite(a['weights']).all())
 def test_constant_target(self):
  m=K.fit(self.X,np.ones(28)*2);self.assertTrue(np.allclose(m['weights'],0));self.assertTrue(np.allclose(K.predict(m,self.X),2))
 def test_no_valid_columns(self):
  m=K.fit(np.ones((28,36)),self.y);self.assertTrue(np.allclose(K.predict(m,np.ones((4,36))*9),self.y.mean()))
 def test_nan_rejected(self):
  x=self.X.copy();x[0,0]=np.nan
  with self.assertRaises(RuntimeError):K.fit(x,self.y)
 def test_inf_target_rejected(self):
  y=self.y.copy();y[0]=np.inf
  with self.assertRaises(RuntimeError):K.fit(self.X,y)
 def test_empty_rejected(self):
  with self.assertRaises(RuntimeError):K.fit(self.X[:0],self.y[:0])
 def test_mismatched_target(self):
  with self.assertRaises(RuntimeError):K.fit(self.X,self.y[:10])
 def test_wrong_transform_dimension(self):
  m=K.fit(self.X,self.y)
  with self.assertRaises(RuntimeError):K.predict(m,self.X[:,:5])
 def test_no_training_permissions(self):
  m=K.fit(self.X,self.y);self.assertFalse(m['deployable']);self.assertFalse(m['pruning_authorized']);self.assertEqual(m['lambda'],1.)

class TestSources(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.data=Path(self.tmp.name);self.prev=R.DATA;self.prevH=H.DATA;R.DATA=self.data;H.DATA=self.data
  self.binding=json.loads((BASE/'SOURCE_BINDINGS.json').read_text());self.out=self.data/'test_output';self.out.mkdir()
 def tearDown(self):R.DATA=self.prev;H.DATA=self.prevH;self.tmp.cleanup()
 def make(self):
  for n in self.binding['files']:
   p=self.data/R.PARENT/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((CURRENT/n).read_bytes())
 def test_real_sources_capture_validation_no_fit(self):
  self.make();audit=[];got=R.capture(H,self.binding,self.out,audit);rows,x,y,plans,old=R.validate(H,np,got,json.loads((BASE/'PROTOCOL.json').read_text()));self.assertEqual(x.shape,(32,36));self.assertEqual(len(audit),10);self.assertEqual(H.parent_postcheck(audit)['status'],'PASS')
 def test_bound_archive_fallback_no_fit(self):
  with zipfile.ZipFile(self.data/(R.PARENT+'.zip'),'w') as z:
   for n in self.binding['files']:z.writestr(R.PARENT+'/'+n,(CURRENT/n).read_bytes())
  got=R.capture(H,self.binding,self.out,[]);self.assertEqual(len(got),10)
 def test_missing_source_hold(self):
  with self.assertRaisesRegex(RuntimeError,'MISSING_SOURCE'):R.capture(H,self.binding,self.out,[])
 def test_wrong_present_bytes_not_bypassed(self):
  self.make();(self.data/R.PARENT/'RESULT.json').write_text('{}')
  with self.assertRaisesRegex(RuntimeError,'SOURCE_SHA'):R.capture(H,self.binding,self.out,[])
 def test_symlink_rejected(self):
  self.make();p=self.data/R.PARENT/'RC.txt';p.unlink();p.symlink_to(CURRENT/'RC.txt')
  with self.assertRaisesRegex(RuntimeError,'SYMLINK'):R.capture(H,self.binding,self.out,[])
 def test_postcheck_source_change(self):
  self.make();audit=[];R.capture(H,self.binding,self.out,audit);(self.data/R.PARENT/'RC.txt').write_text('1\n')
  with self.assertRaises(RuntimeError):H.parent_postcheck(audit)
 def test_outcomes_targets_unchanged(self):
  self.make();got=R.capture(H,self.binding,self.out,[]);p=json.loads((BASE/'PROTOCOL.json').read_text());b=json.loads(got[R.DS]);b['rows'][0]['empirical_mean_gap03_minus30']+=1;got[R.DS]=H.canon(b);p['dataset_sha256']=H.sha(got[R.DS])
  with self.assertRaisesRegex(RuntimeError,'EMPIRICAL_TARGET'):R.validate(H,np,got,p)
 def test_outer_leak_rejected(self):
  self.make();got=R.capture(H,self.binding,self.out,[]);b=json.loads(got['OUTER_INNER_SPLIT_PLAN.json']);b[0]['train_indices'].append(b[0]['test_indices'][0]);got['OUTER_INNER_SPLIT_PLAN.json']=H.canon(b)
  with self.assertRaisesRegex(RuntimeError,'FOLD_INDICES'):R.validate(H,np,got,json.loads((BASE/'PROTOCOL.json').read_text()))
 def test_input_feature_prefix_drift(self):
  self.make();got=R.capture(H,self.binding,self.out,[]);b=json.loads(got['FEATURE36_MATRIX_AND_AUDIT.json']);b['rows'][0]['x36'][0]+=1;got['FEATURE36_MATRIX_AND_AUDIT.json']=H.canon(b);p=json.loads((BASE/'PROTOCOL.json').read_text());p['feature_matrix_sha256']=H.sha(got['FEATURE36_MATRIX_AND_AUDIT.json'])
  with self.assertRaisesRegex(RuntimeError,'FEATURE36_PREFIX'):R.validate(H,np,got,p)
 def test_authorization_before_writes(self):
  with self.assertRaisesRegex(RuntimeError,'EXPLICIT'):R.execute(False)
  self.assertFalse((self.data/R.NAME).exists())
 def test_process_matches_new_launcher(self):self.assertTrue(P.is_related(['bash','/root/autodl-tmp/run_dual32_scaledridge.sh','--authorize-scale8-once']))
 def test_process_does_not_match_shell_body(self):self.assertFalse(P.is_related(['bash','-c','echo run_dual32_scaledridge.sh']))
 def test_process_does_not_match_grep(self):self.assertFalse(P.is_related(['grep','run_dual32_scaledridge.sh']))
 def test_synthetic_eight_fold_pipeline(self):
  rng=np.random.RandomState(291);X=rng.normal(size=(32,36));y=rng.normal(size=32);rows=[];plans=[];old={}
  for i in range(32):
   rid=('contrast_' if i<16 else 'coverage_')+'synthetic_%02d'%i;rows.append({'root_id':rid,'source_run':'policy_%02d'%(i//4),'empirical_mean_gap03_minus30':float(y[i]*100),'repeated_order_sign':None});old[rid]={'new36_prediction':0.,'old26_prediction':0.}
  for j in range(8):
   tr=[i for i in range(32) if i//4!=j];te=[i for i in range(32) if i//4==j];plans.append({'group':'policy_%02d'%j,'train_indices':tr,'test_indices':te,'train_root_ids':[rows[i]['root_id'] for i in tr],'test_root_ids':[rows[i]['root_id'] for i in te]})
  state={'fits_started':0,'fits_completed':0,'saved_models_readback':0,'active_fit':None};m=R.run_folds(H,K,np,self.out,rows,X,y,plans,old,state);self.assertEqual(state['fits_completed'],8);self.assertEqual(state['saved_models_readback'],8);self.assertEqual(m['subsets']['old16']['count'],16);bundle,digest=H.package(self.out);self.assertTrue(bundle.exists())
 def fake_release(self):
  raw=b'synthetic release fixture, never a cloud experiment';(self.data/R.RELEASE).write_bytes(raw)
  parts={n:(BASE/n).read_bytes() for n in ['PROTOCOL.json','SOURCE_BINDINGS.json']}
  return parts,H,P,K,{'sha256':H.sha(raw),'size':len(raw)}
 def test_duplicate_namespace_refused_without_removal(self):
  rel=self.fake_release();old=self.data/(R.NAME+'.lease.json');old.write_text('existing')
  with patch.object(R,'load_release',return_value=rel):
   with self.assertRaisesRegex(RuntimeError,'ONE_TIME_NAMESPACE_EXISTS'):R.execute(True)
  self.assertEqual(old.read_text(),'existing');self.assertFalse((self.data/R.NAME).exists())
 def test_preflight_failure_packaged_no_start(self):
  rel=self.fake_release()
  with patch.object(R,'load_release',return_value=rel),patch.object(H,'environment',side_effect=RuntimeError('SYNTHETIC_ENV_HOLD')),patch.object(P,'related_processes',return_value={'hits':[]}):
   self.assertEqual(R.execute(True),2)
  rr=json.loads((self.data/R.NAME/'RESULT.json').read_text());self.assertFalse(rr['scientific_start_written']);self.assertEqual(rr['fits_started'],0);self.assertTrue((self.data/(R.NAME+'.zip')).exists())
 def test_after_start_failure_preserved_without_retry(self):
  self.make();rel=self.fake_release();pg=json.loads((CURRENT/'POSTCHECK_GIT.json').read_text())
  with patch.object(R,'load_release',return_value=rel),patch.object(H,'environment',return_value=(np,{'synthetic_environment':True})),patch.object(H,'resource_snapshot',return_value={'available_memory_bytes':1024**3,'free_disk_bytes':1024**3}),patch.object(P,'related_processes',return_value={'hits':[]}),patch.object(H,'git_snapshot',return_value=pg),patch.object(R,'run_folds',side_effect=RuntimeError('SYNTHETIC_AFTER_START_STOP')) as rf:
   self.assertEqual(R.execute(True),2);self.assertEqual(rf.call_count,1)
  rr=json.loads((self.data/R.NAME/'RESULT.json').read_text());self.assertTrue(rr['scientific_start_written']);self.assertEqual(rr['fits_started'],0);self.assertEqual(rr['fits_completed'],0);self.assertEqual(rr['status'],'RUNTIME_TECHNICAL_HOLD');self.assertFalse(rr['automatic_retry'])
 def test_existing_source_not_overwritten(self):
  self.make();before=(self.data/R.PARENT/'RESULT.json').read_bytes();R.capture(H,self.binding,self.out,[]);self.assertEqual(before,(self.data/R.PARENT/'RESULT.json').read_bytes())

if __name__=='__main__':unittest.main(verbosity=2)
