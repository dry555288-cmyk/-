"""Read-only replay of saved inference and metrics, never a model fit."""
from pathlib import Path
import hashlib,json,math,zipfile,struct,platform
import numpy as np
ROOT=Path(__file__).resolve().parent
P=ROOT/'original'
OUT=ROOT/'analysis'; OUT.mkdir(exist_ok=True)
def read(p):return json.loads(p.read_text())
def save(name,obj):(OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def sha(b):return hashlib.sha256(b).hexdigest()
def near(a,b):
 assert np.allclose(a,b,rtol=1e-10,atol=1e-10), ('numeric mismatch',a,b)
# All bytes checked once, original run and selected parent bindings only.
manifest=read(P/'MANIFEST.json')
for name,meta in manifest.items():
 b=(P/name).read_bytes();assert len(b)==meta['size'] and sha(b)==meta['sha256'],name
with zipfile.ZipFile('/mnt/data/a0c63dc1-87f0-4d9d-97ca-5eca6d9f5f4f.zip') as z:
 assert z.testzip() is None
bindings=read(P/'release/SOURCE_BINDINGS.json')['files']
for name,meta in bindings.items():
 b=(P/'sources'/name).read_bytes();assert len(b)==meta['size'] and sha(b)==meta['sha256'],name
 parent=read(P/'sources'/meta['manifest_label'])
 if meta['relative_path']!='MANIFEST.json':
  assert parent[meta['relative_path']]['size']==meta['size'] and parent[meta['relative_path']]['sha256']==meta['sha256'],name
result=read(P/'RESULT.json');assert result['rc']==0 and (P/'RC.txt').read_text().strip()=='0'
assert not result['errors'] and not result['postcheck_errors']
assert read(P/'GIT_BEFORE.json')==read(P/'POSTCHECK_GIT.json')
data=read(P/'sources/parent/sources/sources/DATASET32.json')['rows']
fa=read(P/'FEATURE36_MATRIX_AND_AUDIT.json')
features={r['root_id']:r for r in fa['rows']}; rows={r['root_id']:r for r in data}
assert len(data)==len(features)==32
records=0
for r in data:
 base=[]
 for label in ('A','B'):
  a=r['full_state']['vehicles'][label];lo,hi=a['goal_window_m'];s,v=a['route_s'],a['speed_mps'];prev=a['prev_action']
  base += [s/hi,(lo-s)/hi,(hi-s)/hi,v/15,a['accel_mps2']/3,a['target_speed_mps']/15,(hi-s-v*v/6)/hi,float(a['goal_reached'])]+[float(prev==j) for j in (None,0,1,2,3)]
 base=list(struct.unpack('<26f',struct.pack('<26f',*base)));assert base==r['x']
 ctx=read(P/'sources/contexts'/ (r['condition']+'.json'))
 dist=[];valid=[];passed=[];eta=[];speeds=[];ratios=[]
 for label in ('A','B'):
  a=r['full_state']['vehicles'][label];d=ctx['conflict_route_s'][label]-a['route_s'];v=a['speed_mps']
  dist.append(d);speeds.append(v);valid.append(d>=0 and v>0);passed.append(d<0);ratios.append(d/a['goal_window_m'][1]);eta.append(d/(d+64*v) if valid[-1] else 0.)
 both=all(valid);gap=0.
 if both:
  # Algebraically equivalent to the release, independently arranged.
  speedscale=max(speeds);ua,ub=speeds[0]/speedscale,speeds[1]/speedscale
  num=dist[0]*ub-dist[1]*ua
  gap=num/(64*ua*speeds[1]+abs(num))
 extra=ratios+[float(v) for v in passed]+eta+[float(v) for v in valid]+[gap,float(both)]
 x36=list(struct.unpack('<36f',struct.pack('<36f',*(base+extra))))
 assert x36==features[r['root_id']]['x36'], r['root_id']
 a=r['records'];records+=len(a);assert len(a)==16
 for action in ('0,3','3,0'):
  rr=[v for block in r['blocks'].values() for v in block[action]]
  assert len(rr)==8;near(math.fsum(rr)/8,r['mean_returns'][action])
 near(r['empirical_mean_gap03_minus30'],r['mean_returns']['0,3']-r['mean_returns']['3,0'])
assert records==512
maxerr=0.;fits=0;preds=0;split_checks=0
for f in sorted((P/'outer').glob('**/FIT_RESULT.json')):
 rec=read(f);model=read(f.parent/'MODEL.json');start=read(f.parent/'FIT_START.json')
 tr=rec['train_root_ids'];va=rec['validation_root_ids'];forbidden=start['forbidden_outer_root_ids']
 assert set(tr).isdisjoint(va) and set(tr).isdisjoint(forbidden) and set(va).isdisjoint(forbidden)
 assert {rows[x]['source_run'] for x in tr}.isdisjoint({rows[x]['source_run'] for x in va})
 split_checks+=1
 X=np.array([features[k]['x36'] for k in tr]);Xv=np.array([features[k]['x36'] for k in va]);y=np.array([rows[k]['empirical_mean_gap03_minus30']/100 for k in tr])
 W={k:np.array(v,dtype=float) for k,v in model['parameters'].items()}
 def forward(x):
  a=x@W['W0']+W['b0']
  return (np.maximum(a,0)@W['W1']+W['b1'])[:,0] if 'W1' in W else a[:,0]
 ph=forward(Xv);pt=forward(X);expected=np.array(rec['validation_predictions_scaled'])
 near(ph,expected);maxerr=max(maxerr,float(np.max(np.abs(ph-expected))));preds+=len(va)
 residual=pt-y;lam=rec['lambda'];pen=.5*lam*math.fsum(float((v*v).sum()) for k,v in W.items() if k.startswith('W'))
 final=rec['training']['final'];near(.5*np.mean(residual**2),final['data_loss']);near(pen,final['l2_penalty']);near(.5*np.mean(residual**2)+pen,final['objective']);near(np.mean(abs(residual))*100,final['train_mae_reward_units'])
 fits+=1
# Check the selection and saved outer metrics; do not fit alternatives.
metrics=read(P/'METRICS.json');fold_diagnostics=[]
for modelid in ['ridge36','mlp36_8_1_l2']:
 allrows=[]
 for f in sorted((P/'outer').glob('fold*_'+modelid+'/RESULT.json')):
  rr=read(f);tr=rr['train_roots'];held=rr['held_out'];selected=rr['selected_lambda']
  recomputed=[]
  for li,lam in enumerate([.01,.1,1.]):
   scores=[]
   for inner in range(7):
    ar=read(f.parent/'inner'/('lambda%d_inner%d'%(li,inner))/'FIT_RESULT.json')
    yp=np.array(ar['validation_predictions_scaled'])*100;yy=np.array([rows[x]['empirical_mean_gap03_minus30'] for x in ar['validation_root_ids']])
    scores.append(float(np.mean(abs(yp-yy))))
   avg=math.fsum(scores)/7;recomputed.append((avg,-lam))
   near(avg,rr['selection'][li]['group_macro_mae_reward_units'])
  assert selected==-min(recomputed)[1]
  const=math.fsum(rows[k]['empirical_mean_gap03_minus30'] for k in tr)/len(tr)
  X=np.array([features[k]['x36'] for k in tr]);Xt=np.array([features[a['root_id']]['x36'] for a in held]);y=np.array([rows[k]['empirical_mean_gap03_minus30']/100 for k in tr]);
  model=read(f.parent/'final/MODEL.json');w={k:np.array(v) for k,v in model['parameters'].items()}
  for a in held:near(a['training_only_constant_gap'],const)
  pred=np.array([a['predicted_mean_gap'] for a in held]);truth=np.array([a['observed_empirical_mean_gap'] for a in held])
  eig=np.linalg.eigvalsh((X-X.mean(0)).T@(X-X.mean(0))/len(tr));positive=eig[eig>1e-12]
  fd={'model':modelid,'held_group':rr['group_held_out'],'selected_lambda':selected,'train_mae_reward_units':rr['training']['final']['train_mae_reward_units'],'predictions':pred.tolist(),'observed_mean_gaps':truth.tolist(),'constant_mean_gap':const,'held_prediction_range':float(np.ptp(pred)),'max_difference_from_constant':float(np.max(abs(pred-const))),'positive_covariance_eigenvalues':positive.tolist(),'ridge_directional_shrink_factors_if_same_lambda':(positive/(positive+selected)).tolist()}
  if 'W1' in w:
   ht=np.maximum(Xt@w['W0']+w['b0'],0);htr=np.maximum(X@w['W0']+w['b0'],0)
   fd.update({'train_nonzero_hidden_units':int((np.abs(htr).max(axis=0)>1e-12).sum()),'held_nonzero_hidden_units':int((np.abs(ht).max(axis=0)>1e-12).sum()),'added_weight_norm':float(np.linalg.norm(w['W0'][26:])),'hidden_output_norm':float(np.linalg.norm(w['W1']))})
  fold_diagnostics.append(fd);allrows+=held
 truth=np.array([r['observed_empirical_mean_gap'] for r in allrows]);pred=np.array([r['predicted_mean_gap'] for r in allrows]);base=np.array([r['training_only_constant_gap'] for r in allrows]);mm=metrics[modelid]['all32_empirical_gap_errors']
 for name,a in [('mae',np.mean(abs(pred-truth))),('rmse',np.sqrt(np.mean((pred-truth)**2))),('constant_mae',np.mean(abs(base-truth))),('constant_rmse',np.sqrt(np.mean((base-truth)**2)))]:near(mm[name],a)
# Descriptive current-fold signal scales, all outcomes remain untouched.
X=np.array([features[r['root_id']]['x36'] for r in data]);names=['base26_%02d'%i for i in range(26)]+fa['new_features']
scale_table=[{'index':i,'name':names[i],'min':float(X[:,i].min()),'max':float(X[:,i].max()),'std32_descriptive_not_training':float(X[:,i].std()),'train_fold_std_min':min(float(np.array([features[r['root_id']]['x36'][i] for r in data if r['source_run']!=g]).std()) for g in sorted({r['source_run'] for r in data}))} for i in range(36)]
review={'scope':'Uploaded current interaction-fit bundle only. Source and saved inference checks; no refit or simulation.','status':'PASS_RECORD_AND_SAVED_INFERENCE_REVIEW','scientific_advantage':False,'zip_sha256':sha(Path('/mnt/data/a0c63dc1-87f0-4d9d-97ca-5eca6d9f5f4f.zip').read_bytes()),'manifest_items_checked':len(manifest),'source_bindings_checked':len(bindings),'features32_recomputed_exact':32,'stored_return_observations_checked':records,'saved_models_independent_forward':fits,'saved_validation_predictions_independent_forward':preds,'split_checks':split_checks,'max_saved_prediction_difference_scaled':maxerr,'git_before_after_equal':True,'git_status_not_clean':read(P/'GIT_BEFORE.json')['status'],'original_run_fit_seconds':read(P/'TIMING.json')['fit_selection_readback_seconds'],'review_new_fits':0,'review_MCTS_calls':0,'online_acceleration_tested':False,'deployment_authorized':False,'python_review':platform.python_version(),'numpy_review':np.__version__,'numeric_comparison_rtol':1e-10,'numeric_comparison_atol':1e-10}
save('REVIEW.json',review);save('FOLD_MECHANISM.json',fold_diagnostics);save('FEATURE_SCALES.json',scale_table)
print(json.dumps(review,ensure_ascii=False,indent=2))
for d in fold_diagnostics:
 if d['model'].startswith('mlp'):print(d['held_group'],'lambda',d['selected_lambda'],'range',d['held_prediction_range'],'from_const',d['max_difference_from_constant'],'addedWnorm',d['added_weight_norm'],'hidden_units',d['held_nonzero_hidden_units'])
for d in scale_table[26:]:print(d['name'],'std',d['std32_descriptive_not_training'],'minmax',d['min'],d['max'])
