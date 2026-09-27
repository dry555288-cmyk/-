"""Read-only review of saved evidence; never calls fit/solve or runs uploaded code."""
import hashlib, json, math, zipfile, collections, platform
from pathlib import Path
import numpy as np
BASE=Path('/mnt/data/minesim_dual32_scaledridge_review_20260917')
O=BASE/'original'; A=BASE/'analysis'; A.mkdir(exist_ok=True)
ARCH=Path('/mnt/data/c52820de-e363-488d-bf00-a33d2aabd956.zip')
def j(p): return json.loads((O/p).read_text())
def sha(b): return hashlib.sha256(b).hexdigest()
def close(a,b,rtol=1e-11,atol=1e-10):
    if not np.allclose(a,b,rtol=rtol,atol=atol): raise AssertionError(('numeric_mismatch',a,b))
def save(name,obj):
    (A/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
manifest=j('MANIFEST.json')
with zipfile.ZipFile(ARCH) as z:
    assert z.testzip() is None
    assert len(set(z.namelist()))==len(z.namelist())
    assert len(z.infolist())==len(manifest)+1
for name,rec in manifest.items():
    b=(O/name).read_bytes();assert len(b)==rec['size'] and sha(b)==rec['sha256'],name
binding=j('release/SOURCE_BINDINGS.json')
assert len(binding['files'])==binding['source_count']==10
pm=j('sources/MANIFEST.json')
for name,rec in binding['files'].items():
    b=(O/'sources'/name).read_bytes();assert len(b)==rec['size'] and sha(b)==rec['sha256'],name
    if name!='MANIFEST.json':assert pm[name]==rec,name
parent=Path('/mnt/data/a0c63dc1-87f0-4d9d-97ca-5eca6d9f5f4f.zip')
parent_checked=0
if parent.exists():
    with zipfile.ZipFile(parent) as z:
        prefix='minesim_dual32_interaction_fit_v1/'
        for name in binding['files']:
            assert z.read(prefix+name)==(O/'sources'/name).read_bytes(),name
            parent_checked+=1
protocol=j('EXECUTION_PROTOCOL.json');release_proto=j('release/PROTOCOL.json')
assert protocol==release_proto
assert sha((O/'release/PROTOCOL.json').read_bytes())==j('START.json')['protocol_sha256']
assert protocol['lambda']==1.0 and protocol['fits']==8
DS='sources/sources/parent/sources/sources/DATASET32.json'
ds=j(DS);rows=ds['rows'];features=j('sources/FEATURE36_MATRIX_AND_AUDIT.json')
assert sha((O/DS).read_bytes())==protocol['dataset_sha256']
assert sha((O/'sources/FEATURE36_MATRIX_AND_AUDIT.json').read_bytes())==protocol['feature_matrix_sha256']
assert len(rows)==32 and ds['observations']==512
ids=[r['root_id'] for r in rows];assert len(set(ids))==32
fr={r['root_id']:r for r in features['rows']};assert set(fr)==set(ids)
counts=collections.Counter();cells=set();gaps=[];observations=0
for r in rows:
    rid=r['root_id'];f=fr[rid]
    assert r['source_run']==f['source_run'] and r['state_sha256']==f['state_sha256']
    assert f['x36'][:26]==r['x']
    assert len(r['records'])==16
    values=collections.defaultdict(list);bv=collections.defaultdict(list)
    for rec in r['records']:
        assert rec['cell_id'] not in cells;cells.add(rec['cell_id']);observations+=1
        assert rec['root_id']==rid and rec['window_target_observed'] is True
        assert rec['target_id']==ds['target_id']
        assert math.isfinite(rec['window_return']) and 1<=rec['executed_steps']<=128
        assert rec['maximum_outer_steps']==128
        if rec['task_outcome']=='EVALUATION_CAP_NOT_TASK_TERMINAL':
            assert rec['executed_steps']==128 and rec['old_full_task_return'] is None
        counts[rec['task_outcome']]+=1
        values[rec['action_id']].append(rec['window_return'])
        bv[(rec['block'],rec['action_id'])].append(rec['window_return'])
    assert set(values)=={'0,3','3,0'} and all(len(v)==8 for v in values.values())
    means={a:math.fsum(v)/8 for a,v in values.items()}
    for a in means:close(means[a],r['mean_returns'][a])
    gap=means['0,3']-means['3,0'];close(gap,r['empirical_mean_gap03_minus30']);gaps.append(gap)
    for block in ['block0','block1']:
        for action in ['0,3','3,0']:
            assert sorted(bv[(block,action)])==sorted(r['blocks'][block][action])
X=np.array([fr[rid]['x36'] for rid in ids],dtype=float)
y=np.array([r['empirical_mean_gap03_minus30']/100 for r in rows])
assert X.shape==(32,36) and np.isfinite(X).all() and np.isfinite(y).all()
plans=j('sources/OUTER_INNER_SPLIT_PLAN.json');preds=j('PREDICTIONS.json');P={r['root_id']:r for r in preds}
assert len(plans)==8 and len(preds)==len(P)==32
folds=[];held_once=[];max_pred_error=0.;max_objective_error=0.;max_stationarity=0.
for n,f in enumerate(plans):
    tr=np.array(f['train_indices']);te=np.array(f['test_indices']);group=f['group']
    assert tr.tolist()==[i for i,r in enumerate(rows) if r['source_run']!=group]
    assert te.tolist()==[i for i,r in enumerate(rows) if r['source_run']==group]
    assert len(tr)==28 and len(te)==4 and not set(tr)&set(te)
    m=j(f'fits/fold{n:02d}/MODEL.json');res=j(f'fits/fold{n:02d}/RESULT.json');fs=j(f'fits/fold{n:02d}/FIT_START.json')
    assert m['train_root_ids']==f['train_root_ids']==[ids[i] for i in tr]
    assert m['held_root_ids']==f['test_root_ids']==[ids[i] for i in te]
    assert fs['train_root_ids']==m['train_root_ids'] and fs['held_root_ids']==m['held_root_ids']
    assert m['source_group_held']==res['group']==fs['group']==group
    assert m['lambda']==1.0 and m['target_scale']==100 and m['input_dim']==36
    assert m['deployable'] is False and m['pruning_authorized'] is False
    train=X[tr];mu=train.mean(0);sd=np.sqrt(((train-mu)**2).mean(0));active=sd>1e-12
    close(mu,m['scaler']['mean']);close(sd,m['scaler']['std_population'])
    assert active.tolist()==m['scaler']['active_columns']
    scale=np.where(active,sd,1.);close(scale,m['scaler']['scale'])
    w=np.array(m['weights']);bias=m['bias'];stored_mu=np.array(m['scaler']['mean']);stored_scale=np.array(m['scaler']['scale'])
    assert np.all(w[~active]==0)
    Z=(X-stored_mu)/stored_scale;Z[:,~active]=0
    yh=Z@w+bias;errs=yh[tr]-y[tr]
    loss=.5*np.mean(errs**2);pen=.5*sum(float(v)**2 for v in w);total=loss+pen
    for name,v in [('data_loss',loss),('l2_penalty',pen),('total',total)]:
        close(v,m['objective'][name]);max_objective_error=max(max_objective_error,abs(float(v)-m['objective'][name]))
    stationarity=float(np.linalg.norm(np.r_[Z[tr].T@errs/len(tr)+w,errs.mean()]))
    assert stationarity<1e-9;max_stationarity=max(max_stationarity,stationarity)
    mae=float(np.mean(abs(errs))*100);close(mae,m['train_mae_reward_units']);close(mae,res['train_mae'])
    constant=math.fsum(y[tr].tolist())/28*100
    assert res['held_out']==[P[ids[i]] for i in te]
    for i in te:
        p=P[ids[i]];computed=float(yh[i]*100)
        close(computed,p['prediction']);max_pred_error=max(max_pred_error,abs(computed-p['prediction']))
        close(p['constant'],constant);close(p['observed_mean_gap'],y[i]*100)
        assert p['source_run']==group and p['repeated_order_sign']==rows[i]['repeated_order_sign']
        held_once.append(ids[i])
    flagged=[int(k) for k in np.where(~active)[0] if np.any(np.abs(X[te,k]-mu[k])>1e-12)]
    assert flagged==res['train_only_constant_columns_varying_in_held']
    folds.append({'group':group,'training_states':28,'held_states':4,'training_mae':mae,'stationarity_norm':stationarity,'constant_columns':int(sum(~active)),'constant_columns_varying_in_held':flagged,
      'mae':float(np.mean([abs(P[ids[i]]['prediction']-y[i]*100) for i in te])),
      'constant_mae':float(np.mean([abs(constant-y[i]*100) for i in te]))})
assert len(set(held_once))==32 and len(held_once)==32
metrics={}
for key in ['prediction','constant','saved_raw36_ridge','saved_raw26_ridge']:
    e=np.array([p[key]-p['observed_mean_gap'] for p in preds]);metrics[key]={'mae':float(np.mean(abs(e))),'rmse':float(np.sqrt(np.mean(e**2)))}
    for metric,v in metrics[key].items():close(v,j('METRICS.json')[key][metric])
assert j('RESULT.json')['metrics']==j('METRICS.json')
assert j('RESULT.json')['rc']==0 and (O/'RC.txt').read_text().strip()=='0'
assert not j('RESULT.json')['errors'] and not j('RESULT.json')['postcheck_errors']
assert j('GIT_BEFORE.json')==j('POSTCHECK_GIT.json')
# New descriptive calculation only: values do not replace official scores or labels.
pair=j('sources/PAIRED_FEATURE_COMPARISON.json')
methods={
 'scaled_ridge36':{p['root_id']:p['prediction'] for p in preds},
 'training_fold_constant':{p['root_id']:p['constant'] for p in preds},
 'fixed03':dict.fromkeys(ids,1.),'fixed30':dict.fromkeys(ids,-1.)}
for family,rec in pair.items():
    for short,key in [('saved26','old26_prediction'),('saved36','new36_prediction')]:
        methods[family+'_'+short]={p['root_id']:p[key] for p in rec['paired_all32']}
choices={}
for name,pred in methods.items():
    loss=[];old=[];new=[];count=collections.Counter();pr=[]
    for r in rows:
        rid=r['root_id'];pv=pred[rid];action='0,3' if pv>=0 else '3,0';count[action]+=1
        means=r['mean_returns'];v=max(means['0,3'],means['3,0'])-means[action];loss.append(v)
        repeated=r['repeated_order_sign'];known_correct=None
        if repeated is not None:
            known_correct=(1 if pv>1e-6 else -1 if pv< -1e-6 else 0)==repeated
            (new if rid.startswith('coverage_') else old).append(known_correct)
        pr.append({'root_id':rid,'source_run':r['source_run'],'predicted_gap':pv,'choice':action,'observed_gap':r['empirical_mean_gap03_minus30'],'empirical_choice_loss':v,'repeated_sign':repeated,'known_order_correct':known_correct})
    choices[name]={'mean_empirical_choice_loss':math.fsum(loss)/32,'choices':dict(count),'old16':{'known':len(old),'correct':sum(old),'unknown':16-len(old)},'new16_descriptive':{'known':len(new),'correct':sum(new),'unknown':16-len(new)},'per_state':pr}
review={
 'source_zip':str(ARCH),'source_sha256':sha(ARCH.read_bytes()),'review_resource':'LOW',
 'verification':{'zip_crc':'PASS','unique_zip_members':63,'manifest_entries_verified':len(manifest),'source_bindings_verified':10,'parent_manifest_links_verified':9,'source_bytes_matched_separate_parent_zip':parent_checked,'models_read_and_checked':8,'held_predictions_recomputed':32,'train_predictions_recomputed':224,'scalers_recomputed_from_training_only':8,'objectives_and_stationarity_checked':8,'saved_observations_read':observations,'targets_recomputed_from_saved_observations':32,'max_prediction_absolute_difference_reward_units':max_pred_error,'max_objective_absolute_difference':max_objective_error,'max_stationarity_norm':max_stationarity},
 'execution_record':{'rc':0,'status':j('RESULT.json')['status'],'fits_completed':8,'time_seconds':j('TIMING.json')['eight_solves_and_readback_seconds'],'time_scope':'solves and model readback only; excludes preflight packaging upload','new_teacher_traces':0,'mcts_calls':0,'neural_fits':0,'automatic_retry':False,'git_before_after_equal':True,'git_status':j('GIT_BEFORE.json')['status']},
 'data':{'states':32,'observations':512,'groups':8,'features':36,'saved_outcomes':dict(counts),'data_sha256':protocol['dataset_sha256'],'no_raw_rollout_replay_this_review':True},
 'metrics':metrics,'folds':folds,'scientific_conclusion':'Fixed-lambda training-only scaling did not beat the constant or preceding unscaled36 ridge. Scientific negative preserved; not an execution failure.',
 'local_actions':{'new_fits':0,'optimizer_updates':0,'mcts_calls':0,'new_samples':0,'used_saved_model_forward_only':True,'connected_to_AutoDL':False,'cloud_write':False,'deletions':0},
 'limitations':['Current cloud process/resource status not observed.','No safety, deployment, speedup or cross-route generalization claim.','Only sampled fixed64s returns are available; not Q* or task-complete returns for CAP cases.','Additional action-choice-loss calculation is post-outcome descriptive, not a new holdout protocol or calibrated accuracy.']}
save('REVIEW.json',review)
save('DESCRIPTIVE_CHOICE_DIAGNOSTIC.json',{'status':'POST_OUTCOME_DESCRIPTIVE_NO_NEW_FITS','basis':'Saved outer-fold predictions; all32 states; the same saved per-action means used to construct targets.','definition':'max(mean_Y64_03, mean_Y64_30) - mean_Y64_chosen; choose03 if saved gap >=0 otherwise30','tie_rule':'Exact predicted zero selects03 for this descriptive calculation only. Existing hard-order correctness retains +/-1e-6 convention.','scope':'Two forced first actions followed by native MCTS continuation; not full16 action selection or closed-loop neural control.','unknown_rows':'Kept in empirical loss calculation, not assigned accuracy labels. Original6 and new5 relations reported separately.','selection_warning':'Reporting both fixed baselines is not authorization to select or deploy either based on this same data.','original_MAE_RMSE_fail_unchanged':True,'models':choices,'new_fits':0,'new_samples':0,'mcts_calls':0})
print(json.dumps({'verification':review['verification'],'metrics':metrics,'choices':{k:{kk:vv for kk,vv in v.items() if kk!='per_state'} for k,v in choices.items()}},ensure_ascii=False,indent=2))
