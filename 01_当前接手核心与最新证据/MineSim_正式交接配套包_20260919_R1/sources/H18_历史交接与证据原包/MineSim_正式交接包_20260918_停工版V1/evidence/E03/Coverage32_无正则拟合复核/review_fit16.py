"""Read-only local review of an uploaded completed fit bundle.
No source module is imported from the bundle; no optimization or simulator is run.
"""
from pathlib import Path, PurePosixPath
import ast, collections, hashlib, json, math, os, struct, zipfile
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
import numpy as np

BASE=Path('/mnt/data')
OUT=BASE/'MineSim_Coverage32_拟合结果复核_20260917'
ORIG=OUT/'original';ORIG.mkdir(exist_ok=True)
ZIP=BASE/'6e732d05-11e0-466b-8442-b22a9d65fb57.zip'
PREFIX='minesim_grouped_coverage32_fit16_v1/'
Z=zipfile.ZipFile(ZIP)
def sha(b):return hashlib.sha256(b).hexdigest()
def raw(n):return Z.read(PREFIX+n)
def obj(n):return json.loads(raw(n))
def canon(x):return (json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
def save(n,o):
 p=OUT/n;p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(o,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def must(x,msg):
 if not x:raise AssertionError(msg)
def close(a,b,why):
 must(math.isclose(float(a),float(b),rel_tol=1e-12,abs_tol=1e-10),f'{why}: {a} != {b}')

must(len(Z.namelist())==len(set(Z.namelist())),'duplicate archive names')
for n in Z.namelist():
 p=PurePosixPath(n)
 must(not p.is_absolute() and '..' not in p.parts and n.startswith(PREFIX),'unsafe member')
must(Z.testzip() is None,'CRC')
manifest=obj('MANIFEST.json')
must(set(Z.namelist())=={PREFIX+n for n in manifest}|{PREFIX+'MANIFEST.json'},'manifest coverage')
for name,meta in manifest.items():
 b=raw(name);must(len(b)==meta['size'] and sha(b)==meta['sha256'],'manifest '+name)

binding=obj('release/SOURCE_BINDINGS.json')
for n,v in binding['files'].items():
 b=raw('sources/'+n);must(len(b)==v['size'] and sha(b)==v['sha256'],'source binding '+n)
parent_manifest=obj('sources/MANIFEST.json')
for n,v in binding['files'].items():
 if n!='MANIFEST.json':must(parent_manifest[n]==v,'parent manifest '+n)

prep=zipfile.ZipFile(BASE/'MineSim_Coverage32_512条分组拟合协议与技术测试.zip')
for n in ['runner.py','numeric_core.py','SOURCE_BINDINGS.json','METHOD_PROVENANCE.json','PREREGISTERED_FITTING_CONTRACT.json']:
 must(raw('release/'+n)==prep.read(n),'prerun release drift '+n)
prior=zipfile.ZipFile(BASE/'MineSim_Coverage32_数据采集完成与512条核验.zip')
for a,b in [('sources/DATASET32.json','original/DATASET32.json'),
 ('sources/runtime/inputs/OLD_DATASET16.json','original/OLD_DATASET16.json'),
 ('sources/runtime/FUTURE_FITTING_CONTRACT_NOT_AUTHORIZED.json','original/FUTURE_FITTING_CONTRACT_NOT_AUTHORIZED.json')]:
 must(raw(a)==prior.read(b),'prior frozen file drift '+a)

method=obj('release/METHOD_PROVENANCE.json')
coretext=raw('release/numeric_core.py').decode();oldtext=raw('release/WINDOW16_ORIGINAL_SOURCE.py').decode()
must(sha(coretext.encode())==method['core_sha256'],'core SHA')
must(sha(oldtext.encode())==method['original_release_sha256'],'original SHA')
ct={n.name:n for n in ast.parse(coretext).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
ot={n.name:n for n in ast.parse(oldtext).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
for name,v in method['extracted_definitions'].items():
 a=ast.get_source_segment(coretext,ct[name]);b=ast.get_source_segment(oldtext,ot[name])
 must(a==b and sha(b.encode())==v['source_segment_sha256'],'kernel source segment '+name)

result=obj('RESULT.json');ds=obj('sources/DATASET32.json');rows=ds['rows']
contract=obj('release/PREREGISTERED_FITTING_CONTRACT.json');execution=obj('EXECUTION_PROTOCOL.json')
must(raw('release/PREREGISTERED_FITTING_CONTRACT.json')==raw('sources/runtime/FUTURE_FITTING_CONTRACT_NOT_AUTHORIZED.json'),'contract bytes')
must(execution['contract']==contract and execution['execution_authorization']['training'] is True,'execution authority')
must(result['rc']==0 and raw('RC.txt').strip()==b'0','rc')
must(result['fits_completed']==result['fits_started']==result['fits_planned']==16,'fits')
must(result['updates_completed_in_finished_fits']==32000 and not result['errors'] and not result['postcheck_errors'],'execution errors')
for k in ['deployment_authorized','pruning_authorized','collection_authorized','automatic_retry','full32_refit']:
 must(result[k] is False,'permission '+k)
must(result['new_teacher_traces']==result['mcts_calls']==0,'sample counter')
must(obj('GIT_BEFORE.json')==obj('POSTCHECK_GIT.json')==obj('sources/GIT_AFTER.json'),'Git changed')
must(obj('POSTCHECK_PARENT.json')=={'bound_files_unchanged':11,'status':'PASS'},'parent postcheck')
must(not obj('POSTCHECK_PROCESS.json')['hits'],'process postcheck')

old=obj('sources/runtime/inputs/OLD_DATASET16.json');oldby={r['root_id']:r for r in old['rows']};oldids=set(oldby)
inp={r['root_id']:r for r in obj('sources/runtime/inputs/COMBINED32_INPUTS.json')}
newdiag=obj('sources/NEW16_REPEAT_DIAGNOSTIC.json');newby={r['root_id']:r for r in newdiag['rows']}
must(len(rows)==len(inp)==len(set(r['root_id'] for r in rows))==32,'rows')
must(collections.Counter(r['source_run'] for r in rows)=={f'policy_{i:02d}':4 for i in range(8)},'groups')
ids=set();outcomes=collections.Counter();identity_groups={};target_recalc=[]
def feature(state):
 values=[]
 for who in ['A','B']:
  v=state['vehicles'][who];lo,hi=v['goal_window_m'];s=v['route_s'];speed=v['speed_mps']
  values.extend([s/hi,(lo-s)/hi,(hi-s)/hi,speed/15,v['accel_mps2']/3,v['target_speed_mps']/15,(hi-s-speed**2/6)/hi,float(v['goal_reached'])])
  values.extend(float(v['prev_action']==x) for x in [None,0,1,2,3])
 return list(struct.unpack('<26f',struct.pack('<26f',*values)))
for r in rows:
 rid=r['root_id'];i=inp[rid]
 if rid in oldids:must(r==oldby[rid],'old row changed')
 must(r['full_state']==i['state'] and r['state_sha256']==i['exact_before_state_sha256']==sha(canon(r['full_state'])),'state binding')
 must(r['source_run']==i['task']['task_id'],'source_run')
 must(feature(r['full_state'])==r['x'],'feature values')
 must(sha(struct.pack('<26f',*r['x']))==r['feature_sha256'],'feature SHA')
 must(r['mask16']==[True]*16 and r['original_training_mask']==0 and not r['pruning_authorized'],'action scope')
 for key in ['state_sha256','feature_sha256']:
  ident=(key,r[key]);must(ident not in identity_groups or identity_groups[ident]==r['source_run'],'cross group alias')
  identity_groups[ident]=r['source_run']
 blocks={b:{a:[] for a in ['0,3','3,0']} for b in ['block0','block1']}
 must(len(r['records'])==16,'records per root')
 for o in r['records']:
  must(o['cell_id'] not in ids,'duplicate cell');ids.add(o['cell_id'])
  must(o['root_id']==rid and o['root_state_sha256']==r['state_sha256'] and o['target_id']==ds['target_id'],'record binding')
  must(o['window_target_observed'] and math.isfinite(o['window_return']) and o['maximum_outer_steps']==128 and 1<=o['executed_steps']<=128,'observed window')
  if o['task_outcome']=='EVALUATION_CAP_NOT_TASK_TERMINAL':must(o['executed_steps']==128 and o['old_full_task_return'] is None and o['old_full_task_tail_censored'],'CAP semantics')
  else:must(o['old_full_task_return']==o['window_return'] and not o['old_full_task_tail_censored'],'terminal semantics')
  must(o['training_mask']==0 and o['pruning_authorized'] is False,'original mask')
  blocks[o['block']][o['action_id']].append(o['window_return']);outcomes[o['task_outcome']]+=1
 must(blocks==r['blocks'] and all(len(v)==4 for b in blocks.values() for v in b.values()),'blocks')
 means={a:math.fsum(blocks['block0'][a]+blocks['block1'][a])/8 for a in ['0,3','3,0']}
 gap=means['0,3']-means['3,0'];close(gap,r['empirical_mean_gap03_minus30'],'gap')
 for a in means:close(means[a],r['mean_returns'][a],'mean return')
 bg=[math.fsum(blocks[b]['0,3'])/4-math.fsum(blocks[b]['3,0'])/4 for b in ['block0','block1']]
 for a,b in zip(bg,r['block_mean_gaps']):close(a,b,'block gap')
 if rid not in oldids:
  signs=[]
  for b in blocks.values():
   a,c=b['0,3'],b['3,0'];tol=1e-9*max(1.,*(abs(x) for x in a+c))
   signs.append(1 if min(a)>max(c)+tol else -1 if min(c)>max(a)+tol else None)
  sign=signs[0] if signs[0] is not None and signs[0]==signs[1] else None
  must(sign==r['repeated_order_sign']==newby[rid]['repeated_order_sign'],'new repeated order')
 target_recalc.append(gap)
must(len(ids)==512,'total observations')

X=np.array([r['x'] for r in rows],dtype=np.float32).astype(np.float64)
y=np.array(target_recalc,dtype=np.float64)/100
folds=obj('FOLDS.json');must(len(folds)==8,'fold count')
models=contract['models'];fits=[];predictions={m:[] for m in models};train_stats=[]
max_pred_diff=max_loss_diff=0.;checked=0

def forward_weights(parameters,XX):
 h=XX.copy();layers=len(parameters)//2
 for idx in range(layers):
  h=np.dot(h,np.array(parameters['W'+str(idx)],dtype=np.float64))+np.array(parameters['b'+str(idx)],dtype=np.float64)
  if idx<layers-1:h=np.maximum(h,0)
 return h[:,0] if h.shape[1]==1 else h[:,3]-h[:,12]

def sgn(v):return 1 if v>1e-6 else -1 if v< -1e-6 else None

def errors(rr):
 n=len(rr);a=[r['absolute_error'] for r in rr];b=[r['constant_absolute_error'] for r in rr]
 return {'count':n,'mae':math.fsum(a)/n,'rmse':math.sqrt(math.fsum(v*v for v in a)/n),'constant_mae':math.fsum(b)/n,'constant_rmse':math.sqrt(math.fsum(v*v for v in b)/n)}

def orders(rr):
 known=[r for r in rr if r['repeated_order_sign'] is not None]
 return {'correct':sum(r['known_order_correct'] for r in known),'known_denominator':len(known),'fixed03_correct':sum(r['fixed03_known_order_correct'] for r in known),'constant_correct':sum(r['constant_known_order_correct'] for r in known),'observed_rows':len(rr),'coverage_denominator':16,'unknown_count':len(rr)-len(known),'unknowns_not_scored':True}

for no,f in enumerate(folds):
 tr=[i for i,r in enumerate(rows) if r['source_run']!=f['group']];te=[i for i,r in enumerate(rows) if r['source_run']==f['group']]
 must(tr==f['train_indices'] and te==f['test_indices'] and len(tr)==28 and len(te)==4,'source leaveout')
 must({rows[i]['source_run'] for i in tr}.isdisjoint({rows[i]['source_run'] for i in te}),'group leak')
 c=math.fsum(target_recalc[i] for i in tr)/28
 for model in models:
  dest=f'fits/fold{no:02d}_{model}/';record=obj(dest+'RESULT.json');params=obj(dest+'MODEL.json');initial=obj(dest+'INITIAL_MODEL.json');start=obj(dest+'FIT_START.json')
  must(params['complete_fit'] and params['completed_updates']==2000 and not params['deployable'] and not params['pruning_authorized'],'model status')
  must(record['training']['updates']==2000 and record['group_held_out']==f['group'],'fit count')
  must(start['seed']==78003 and start['train_indices']==tr and start['held_indices']==te and not start['test_rows_used_for_fitting'],'fit start')
  must(record['train_roots']==[rows[i]['root_id'] for i in tr] and record['test_roots']==[rows[i]['root_id'] for i in te],'fit ids')
  progress=[json.loads(line) for line in raw(dest+'PROGRESS.jsonl').splitlines()]
  must(progress==record['training']['progress'] and [p['update'] for p in progress]==[1]+list(range(100,2001,100)),'progress')
  held=forward_weights(params['parameters'],X[te])*100
  trainpred=forward_weights(params['parameters'],X[tr]);loss=float(.5*np.mean((trainpred-y[tr])**2));mae=float(np.mean(abs(trainpred-y[tr]))*100)
  iloss=float(.5*np.mean((forward_weights(initial['parameters'],X[tr])-y[tr])**2))
  close(loss,record['training']['final_loss'],'loss');close(mae,progress[-1]['train_mean_gap_mae_reward_units'],'train mae');close(iloss,record['training']['initial_loss'],'initial loss')
  max_loss_diff=max(max_loss_diff,abs(loss-record['training']['final_loss']))
  train_stats.append({'model':model,'source_group':f['group'],'train_mae':mae,'final_loss':loss,'initial_loss':iloss,'parameters_count':sum(np.asarray(v).size for v in params['parameters'].values())})
  generated=[]
  for j,i in enumerate(te):
   r=rows[i];saved=record['held_out'][j];pv=float(held[j]);g=target_recalc[i];sign=r['repeated_order_sign'];isold=r['root_id'] in oldids
   must(saved['root_id']==r['root_id'] and saved['source_run']==f['group'],'prediction id')
   close(pv,saved['predicted_mean_gap'],'prediction');max_pred_diff=max(max_pred_diff,abs(pv-saved['predicted_mean_gap']));checked+=1
   for k,v in [('observed_empirical_mean_gap',g),('training_only_constant_gap',c),('signed_error',pv-g),('absolute_error',abs(pv-g)),('constant_absolute_error',abs(c-g))]:close(v,saved[k],k)
   must(saved['is_old16']==isold and saved['repeated_order_sign']==sign and saved['prediction_sign']==sgn(pv),'order metadata')
   must(saved['known_order_correct']==(None if sign is None else sgn(pv)==sign) and saved['fixed03_known_order_correct']==(None if sign is None else sign==1) and saved['constant_known_order_correct']==(None if sign is None else sgn(c)==sign),'order scores')
   must(saved['unknown_not_imputed']==(sign is None),'unknown')
   # Independent reconstructed prediction record; values used below are not read from saved metrics.
   rr=dict(saved);rr.update(predicted_mean_gap=pv,signed_error=pv-g,absolute_error=abs(pv-g),training_only_constant_gap=c,constant_absolute_error=abs(c-g))
   generated.append(rr)
  predictions[model].extend(generated);fits.append(record)
  complete=obj(f'COMPLETED_FIT_{2*no+models.index(model)+1:02d}.json')
  must(complete['result_sha256']==sha(raw(dest+'RESULT.json')),'completed marker SHA')

recomputed={}
for m in models:
 rr=predictions[m];groups={g:errors([r for r in rr if r['source_run']==g]) for g in sorted({r['source_run'] for r in rr})}
 allstats=errors(rr)
 recomputed[m]={'all32_empirical_gap_errors':allstats,'old16_errors':errors([r for r in rr if r['is_old16']]),'new16_errors':errors([r for r in rr if not r['is_old16']]),'per_source_group':groups,'source_macro_mae':math.fsum(v['mae'] for v in groups.values())/8,'original6_orders_and10_unknown':orders([r for r in rr if r['is_old16']]),'new16_descriptive_orders':orders([r for r in rr if not r['is_old16']])}
 saved=obj('METRICS.json')[m]
 for key,v in recomputed[m].items():
  def compare(a,b,path):
   if isinstance(a,dict):
    must(set(a)==set(b),'keys '+path)
    for k in a:compare(a[k],b[k],path+'.'+k)
   elif isinstance(a,(bool,str)) or a is None:must(a==b,path)
   else:close(a,b,path)
  compare(v,saved[key],m+'.'+key)
must(obj('METRICS.json')==result['metrics'],'metrics result parity')

# Descriptive review of already saved values only. Does not change labels or select a model.
oldres=json.loads((BASE/'MineSim_Window16_结果复核_20260917/original/RESULT.json').read_text())
comparison={m:{'same_old16_before_mae':oldres['metrics'][m]['held_sample_mean_gap_mae'],'same_old16_after_mae':recomputed[m]['old16_errors']['mae'],'constant_before_mae':oldres['metrics'][m]['constant_train_mean_gap_mae'],'constant_after_mae':recomputed[m]['old16_errors']['constant_mae'],'interpretation':'Post-outcome development comparison on unchanged old16 rows, training population changed. Not a blinded causal effect.'} for m in models}
row_summary=[]
for r in rows:
 v=r['full_state']['vehicles']
 row_summary.append({'root_id':r['root_id'],'source_run':r['source_run'],'old16':r['root_id'] in oldids,'mean_gap':r['empirical_mean_gap03_minus30'],'block0_gap':r['block_mean_gaps'][0],'block1_gap':r['block_mean_gaps'][1],'block_gap_abs_difference':abs(r['block_mean_gaps'][0]-r['block_mean_gaps'][1]),'repeated_order_sign':r['repeated_order_sign'],'A_route_s':v['A']['route_s'],'B_route_s':v['B']['route_s'],'A_speed':v['A']['speed_mps'],'B_speed':v['B']['speed_mps']})

diagnostic={'scope':'DESCRIPTIVE_POST_RESULT_NO_NEW_FITS_NO_LABEL_CHANGES','train_fit_summary':{},'old16_same_row_comparison':comparison,'per_root':row_summary,'limitations':['Same known route; not independent-route generalization.','512 return observations aggregate to32 state targets; each fit trains on28 state targets.','No dataset-wide cause identified solely from this review.','Observed block variability does not define a noise floor or statistical safety guarantee.']}
for m in models:
 tr=[v for v in train_stats if v['model']==m]
 diagnostic['train_fit_summary'][m]={'train_mae_min':min(v['train_mae'] for v in tr),'train_mae_max':max(v['train_mae'] for v in tr),'train_mae_mean':math.fsum(v['train_mae'] for v in tr)/8,'parameters_count':tr[0]['parameters_count'],'held_mae_better_than_constant_groups':sum(v['mae']<v['constant_mae'] for v in recomputed[m]['per_source_group'].values()),'top5_held_errors':sorted(predictions[m],key=lambda v:v['absolute_error'],reverse=True)[:5]}
for name,subset in [('old16',[r for r in row_summary if r['old16']]),('new16',[r for r in row_summary if not r['old16']])]:
 diagnostic[name+'_descriptive_target_summary']={'n':len(subset),'mean_abs_gap':math.fsum(abs(r['mean_gap']) for r in subset)/len(subset),'median_abs_gap':float(np.median([abs(r['mean_gap']) for r in subset])),'max_abs_gap':max(abs(r['mean_gap']) for r in subset),'mean_abs_block_gap_difference':math.fsum(r['block_gap_abs_difference'] for r in subset)/len(subset),'known_repeated_orders':sum(r['repeated_order_sign'] is not None for r in subset)}

review={'review_scope':'Current uploaded fit bundle and exact frozen parent subset only; no AutoDL connection, no original code execution, no training or simulation. Prior full trajectory audit not repeated.','archive_name':ZIP.name,'archive_sha256':sha(ZIP.read_bytes()),'zip_members':len(Z.namelist()),'manifest_verified':len(manifest),'crc':'PASS','parent_bound_files_verified':len(binding['files']),'release_files_identical_to_prerun_preparation':5,'exact_numerical_definitions_verified':len(method['extracted_definitions']),'data_identical_to_previous_frozen_dataset':True,'old16_rows_unchanged':True,'unique_return_records':len(ids),'state_feature_bindings_verified':32,'source_groups':8,'group_splits_28_train_4_held_verified':8,'saved_models_forward_checked':16,'held_predictions_independently_recomputed':checked,'initial_and_final_losses_recomputed':16,'maximum_prediction_absolute_difference_reward_units':max_pred_diff,'maximum_final_loss_absolute_difference':max_loss_diff,'original_run_status':result['status'],'original_run_rc':result['rc'],'original_fits_completed':16,'updates_each':2000,'run_new_teacher_traces':0,'run_mcts_calls':0,'this_review_new_fits':0,'this_review_new_mcts':0,'run_fit_and_readback_seconds':obj('TIMING.json')['fit_and_readback_seconds'],'postchecks_pass':True,'git_snapshot':obj('POSTCHECK_GIT.json'),'scientific_conclusion':'Neither model improves primary held-source32 MAE or RMSE over training-only constant baseline in this development dataset.','new_collection_authorized':False,'new_training_authorized':False,'deployment_authorized':False,'pruning_authorized':False,'metrics_recomputed':recomputed}
save('REVIEW.json',review);save('DESCRIPTIVE_DIAGNOSTIC.json',diagnostic);save('RECOMPUTED_METRICS.json',recomputed);save('HELD_PREDICTIONS_RECOMPUTED.json',predictions);save('TRAIN_FIT_SUMMARY.json',train_stats)
for name in ['RESULT.json','METRICS.json','TIMING.json','EXECUTION_PROTOCOL.json','INPUT_VALIDATION.json','FOLDS.json','POSTCHECK_GIT.json','MANIFEST.json','sources/DATASET32.json','sources/runtime/inputs/OLD_DATASET16.json','release/PREREGISTERED_FITTING_CONTRACT.json']:
 path=ORIG/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw(name))
print(json.dumps({k:review[k] for k in ['manifest_verified','parent_bound_files_verified','saved_models_forward_checked','held_predictions_independently_recomputed','maximum_prediction_absolute_difference_reward_units','maximum_final_loss_absolute_difference','run_fit_and_readback_seconds']},indent=2))
for m in models:
 print(m,recomputed[m]['all32_empirical_gap_errors'])
 print('TRAIN', {k:v for k,v in diagnostic['train_fit_summary'][m].items() if k!='top5_held_errors'})
 print('OLD',comparison[m])
 print('TOP ERRORS',[(x['root_id'],round(x['observed_empirical_mean_gap'],3),round(x['predicted_mean_gap'],3)) for x in diagnostic['train_fit_summary'][m]['top5_held_errors']])
print('NEW',diagnostic['new16_descriptive_target_summary'])
