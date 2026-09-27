"""Read-only audit of uploaded saved artifacts. No fitting, simulator or remote I/O."""
from pathlib import Path
import json, hashlib, math, collections, zipfile
import numpy as np
ROOT=Path('/mnt/data/minesim_dual32_regularized_review_20260917')
R=ROOT/'original'
UPLOAD=Path('/mnt/data/29eb52f0-03f5-4951-894b-6f08b39acf68.zip')
def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def check(a,b,where):
    if not np.allclose(a,b,rtol=1e-10,atol=1e-10,equal_nan=False):
        raise AssertionError((where,a,b))
def avg(a): return math.fsum(float(v) for v in a)/len(a)
def dump(n,x): (ROOT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def forward(model,X):
    p={k:np.asarray(v,dtype=float) for k,v in model['parameters'].items()}
    h=X
    for i in range(len(p)//2):
        h=h @ p['W'+str(i)] + p['b'+str(i)]
        if i<len(p)//2-1: h=np.maximum(h,0)
    return h[:,0]
manifest=load(R/'MANIFEST.json')
for path,e in manifest.items():
    assert (R/path).is_file(),path
    assert (R/path).stat().st_size==e['size'],path
    assert sha(R/path)==e['sha256'],path
assert {str(p.relative_to(R)) for p in R.rglob('*') if p.is_file()}==set(manifest)|{'MANIFEST.json'}
with zipfile.ZipFile(UPLOAD) as z: assert z.testzip() is None
bindings=load(R/'release/SOURCE_BINDINGS.json')['files']
for path,e in bindings.items():
    assert (R/'sources'/path).stat().st_size==e['size'],path
    assert sha(R/'sources'/path)==e['sha256'],path
res=load(R/'RESULT.json');proto=load(R/'EXECUTION_PROTOCOL.json')
assert (R/'RC.txt').read_text().strip()=='0' and res['rc']==0
assert not res['errors'] and not res['postcheck_errors']
assert res['inner_fits_completed']==336 and res['outer_fits_completed']==16
assert res['mcts_calls']==res['new_teacher_traces']==res['single_vehicle_experiments']==0
assert not res['full32_refit'] and not res['deployment_authorized'] and not res['pruning_authorized']
assert sha(R/'GIT_BEFORE.json')==sha(R/'POSTCHECK_GIT.json')
assert load(R/'POSTCHECK_PARENT.json')=={'bound_files_unchanged':12,'status':'PASS'}
ds=load(R/'sources/sources/DATASET32.json');rows=ds['rows'];ids=[v['root_id'] for v in rows];idx={v:i for i,v in enumerate(ids)}
assert len(ids)==len(set(ids))==32 and collections.Counter(v['source_run'] for v in rows)=={f'policy_{i:02}':4 for i in range(8)}
assert proto['frozen_data']['dataset_sha256']==sha(R/'sources/sources/DATASET32.json')
X=np.asarray([v['x'] for v in rows],dtype=np.float32).astype(float)
yraw=np.array([v['empirical_mean_gap03_minus30'] for v in rows]);y=yraw/100
assert X.shape==(32,26) and np.isfinite(X).all() and np.isfinite(y).all()
record_ids=[];outcomes=collections.Counter();maxmeanerr=0
for row in rows:
    records=row['records'];assert len(records)==16 and len(set(v['cell_id'] for v in records))==16
    record_ids.extend(v['cell_id'] for v in records)
    means={}
    for a in ['0,3','3,0']:
        vals=[v['window_return'] for v in records if v['action_id']==a];assert len(vals)==8
        means[a]=avg(vals);check(means[a],row['mean_returns'][a],row['root_id']+' mean')
        for b in ['block0','block1']:
            bvals=[v['window_return'] for v in records if v['action_id']==a and v['block']==b]
            assert len(bvals)==4;check(bvals,row['blocks'][b][a],'block values')
    gap=means['0,3']-means['3,0'];check(gap,row['empirical_mean_gap03_minus30'],'mean gap')
    maxmeanerr=max(maxmeanerr,abs(gap-row['empirical_mean_gap03_minus30']))
    for rec in records:
        outcomes[rec['task_outcome']]+=1;assert rec['window_target_observed'] is True
        assert rec['root_id']==row['root_id'] and rec['root_state_sha256']==row['state_sha256']
        if rec['task_outcome']=='EVALUATION_CAP_NOT_TASK_TERMINAL':
            assert rec['executed_steps']==128 and rec['old_full_task_return'] is None
assert len(record_ids)==len(set(record_ids))==512
folds=load(R/'sources/FOLDS.json');plans=load(R/'OUTER_INNER_SPLIT_PLAN.json')
assert len(folds)==len(plans)==8
for f,pl in zip(folds,plans):
    assert all(pl[k]==v for k,v in f.items())
    tr=f['train_indices'];te=f['test_indices']
    assert len(tr)==28 and len(te)==4 and set(tr).isdisjoint(te) and set(tr+te)==set(range(32))
    assert [ids[i] for i in tr]==f['train_root_ids'] and [ids[i] for i in te]==f['test_root_ids']
    assert all(rows[i]['source_run']==f['group'] for i in te) and all(rows[i]['source_run']!=f['group'] for i in tr)
    for inn in pl['inner']:
        assert set(inn['train_indices']+inn['validation_indices'])==set(tr)
        assert len(inn['train_indices'])==24 and len(inn['validation_indices'])==4
        assert set(inn['train_indices']).isdisjoint(inn['validation_indices'])
        assert all(rows[i]['source_run']==inn['group'] for i in inn['validation_indices'])
# Replay saved parameters only: 352 models, 1408 held/validation predictions.
fitdirs=sorted(p.parent for p in (R/'outer').rglob('FIT_RESULT.json'))
assert len(fitdirs)==352
maxp=maxloss=0.;replays=0;counts=collections.Counter();cached={};ridge_grad=0
for p in fitdirs:
    m=load(p/'MODEL.json');fr=load(p/'FIT_RESULT.json');st=load(p/'FIT_START.json')
    tid=fr['train_root_ids'];vid=fr['validation_root_ids'];forbid=st['forbidden_outer_root_ids']
    assert tid==st['train_root_ids'] and vid==st['validation_root_ids']
    assert set(tid).isdisjoint(vid) and set(tid+vid).isdisjoint(forbid)
    ti=[idx[v] for v in tid];vi=[idx[v] for v in vid]
    assert {rows[i]['source_run'] for i in ti}.isdisjoint({rows[i]['source_run'] for i in vi})
    assert len(ti)==(24 if fr['role']=='inner' else 28) and len(vi)==4
    assert m['complete_fit'] and not m['deployable'] and not m['pruning_authorized']
    assert m['lambda']==fr['lambda']==st['lambda'] and m['model']==fr['model']==st['model']
    assert m['lambda'] in [.01,.1,1.] and m['target_scale']==100.
    if m['model']=='mlp26_8_1_l2': assert m['completed_updates']==2000 and m['seed']==78004
    else: assert m['closed_form_solve_completed'] and m['completed_updates']==0
    pv=forward(m,X[vi]);pt=forward(m,X[ti]);actual=np.array(fr['validation_predictions_scaled'])
    check(pv,actual,'saved prediction '+str(p));maxp=max(maxp,float(max(abs(pv-actual))))
    err=pt-y[ti]
    par={k:np.array(v,dtype=float) for k,v in m['parameters'].items()}
    loss=float(.5*np.mean(err**2));penalty=float(.5*m['lambda']*math.fsum(float(np.sum(v*v)) for k,v in par.items() if k.startswith('W')))
    train=fr['training']['final'];calc={'data_loss':loss,'l2_penalty':penalty,'objective':loss+penalty,'train_mae_reward_units':float(np.mean(abs(err))*100.)}
    for k,v in calc.items():check(v,train[k],k);maxloss=max(maxloss,abs(v-train[k]))
    if m['model']=='ridge26':
        gw=X[ti].T@err/len(ti)+m['lambda']*par['W0'][:,0];gb=avg(err)
        gn=math.sqrt(float(gw@gw)+gb*gb);assert gn<1e-9;ridge_grad=max(ridge_grad,gn)
    counts[(fr['role'],fr['model'])]+=1;replays+=len(pv);cached[str(p.relative_to(R))]=(pv,calc)
# Independently select lambdas from saved inner validation outputs, and compare all final reporting.
selcheck=0;outer_by_model=collections.defaultdict(list);collapse=[];outermae={}
for f in folds:
    fi=folds.index(f)
    for model in ['ridge26','mlp26_8_1_l2']:
        p=R/'outer'/f'fold{fi:02}_{model}';sel=load(p/'inner/SELECTION.json');outer=load(p/'RESULT.json');lock=load(p/'OUTER_SELECTION_LOCK.json')
        assert sel['training_root_ids']==f['train_root_ids'] and sel['forbidden_outer_root_ids']==f['test_root_ids']
        assert not sel['outer_held_out_used'] and sel['chosen_before_outer_predictions']
        scores=[]
        groups=sorted({rows[i]['source_run'] for i in f['train_indices']})
        for li,lam in enumerate([.01,.1,1.]):
            for gi,group in enumerate(groups):
                q=p/'inner'/f'lambda{li}_inner{gi}';fr=load(q/'FIT_RESULT.json');
                pv=cached[str(q.relative_to(R))][0];vi=[idx[v] for v in fr['validation_root_ids']]
                mae=avg(abs(pv-y[vi])*100.)
                sc=load(p/'inner'/f'SCORE_lambda{li}_inner{gi}.json')
                assert sc['lambda']==lam and sc['inner_group']==group and not sc['outer_held_used']
                check(mae,sc['mae_reward_units'],'inner MAE');scores.append((lam,mae))
        cand=[{'lambda':lam,'score':avg([v for a,v in scores if a==lam])} for lam in [.01,.1,1.]]
        chosen=min(cand,key=lambda e:(e['score'],-e['lambda']))['lambda']
        assert chosen==sel['selected_lambda']==outer['selected_lambda']==lock['selected_lambda']
        assert lock['at']<=load(p/'final/FIT_START.json')['at']
        for entry in sel['candidate_scores']:
            check(entry['group_macro_mae_reward_units'],next(v['score'] for v in cand if v['lambda']==entry['lambda']),'lambda avg')
        selcheck+=1
        pred=cached[str((p/'final').relative_to(R))][0]*100.;baseline=avg(yraw[f['train_indices']])
        held=outer['held_out']; assert [h['root_id'] for h in held]==f['test_root_ids']
        for h,pr,i in zip(held,pred,f['test_indices']):
            check(pr,h['predicted_mean_gap'],'outer prediction');check(yraw[i],h['observed_empirical_mean_gap'],'outer target');check(baseline,h['training_only_constant_gap'],'baseline')
            check(abs(pr-yraw[i]),h['absolute_error'],'abs error')
            rs=rows[i]['repeated_order_sign'];assert rs==h['repeated_order_sign']
            sign=1 if pr>1e-6 else -1 if pr< -1e-6 else None
            assert h['known_order_correct']==(None if rs is None else sign==rs)
        outer_by_model[model].extend(held)
        collapse.append({'model':model,'source_group':f['group'],'lambda':chosen,'training_constant_gap':baseline,'held_prediction_min':float(min(pred)),'held_prediction_max':float(max(pred)),'held_prediction_range':float(np.ptp(pred)),'max_abs_difference_from_constant':float(max(abs(pred-baseline))),'held_empirical_gap_range':float(np.ptp(yraw[f['test_indices']])),'train_mae':cached[str((p/'final').relative_to(R))][1]['train_mae_reward_units']})
allmetrics={}
for model,held in outer_by_model.items():
    assert len(held)==32 and len({h['root_id'] for h in held})==32
    ee=[h['signed_error'] for h in held];ce=[h['training_only_constant_gap']-h['observed_empirical_mean_gap'] for h in held]
    metrics={'mae':avg([abs(x) for x in ee]),'rmse':math.sqrt(avg([x*x for x in ee])),'constant_mae':avg([abs(x) for x in ce]),'constant_rmse':math.sqrt(avg([x*x for x in ce]))}
    for k,v in metrics.items():check(v,res['metrics'][model]['all32_empirical_gap_errors'][k],model+k)
    for key,subset in [('old16_errors',[h for h in held if h['is_old16']]),('new16_errors',[h for h in held if not h['is_old16']])]:
        for metric,val in [('mae',avg([h['absolute_error'] for h in subset])),('rmse',math.sqrt(avg([h['signed_error']**2 for h in subset]))),('constant_mae',avg([h['constant_absolute_error'] for h in subset])),('constant_rmse',math.sqrt(avg([h['constant_absolute_error']**2 for h in subset])))]:check(val,res['metrics'][model][key][metric],key+metric)
    for key,isold in [('original6_orders_and10_unknown',True),('new16_descriptive_orders',False)]:
        hh=[h for h in held if h['is_old16']==isold];known=[h for h in hh if h['repeated_order_sign'] is not None]
        expected={'correct':sum(h['known_order_correct'] for h in known),'known_denominator':len(known),'coverage_denominator':16,'unknown_count':16-len(known),'fixed03_correct':sum(h['fixed03_known_order_correct'] for h in known),'constant_correct':sum(h['constant_known_order_correct'] for h in known)}
        assert all(res['metrics'][model][key][k]==v for k,v in expected.items())
    allmetrics[model]=metrics
mlpc=[c for c in collapse if c['model']=='mlp26_8_1_l2'];lambda1=[c for c in mlpc if c['lambda']==1.]
known_examples={model:[h for h in held if h['ordering_subset']=='OLD6_CONFIRMED'] for model,held in outer_by_model.items()}
diag={'scope':'POST_OUTCOME_DESCRIPTIVE_REPLAY_OF_SAVED_MODELS_NOT_NEW_FIT','per_fold_prediction_collapse':collapse,'mlp_lambda1_folds':len(lambda1),'mlp_lambda1_held_states':4*len(lambda1),'mlp_lambda1_max_prediction_range':max(c['held_prediction_range'] for c in lambda1),'mlp_lambda1_max_abs_deviation_from_constant':max(c['max_abs_difference_from_constant'] for c in lambda1),'all32_mae_delta_constant_minus_mlp':allmetrics['mlp26_8_1_l2']['constant_mae']-allmetrics['mlp26_8_1_l2']['mae'],'mae_relative_reduction_percent':100*(allmetrics['mlp26_8_1_l2']['constant_mae']-allmetrics['mlp26_8_1_l2']['mae'])/allmetrics['mlp26_8_1_l2']['constant_mae'],'old6_examples':known_examples,'metrics':allmetrics,'interpretation':'Saved small-MLP predictions are near training means in 5 of 8 folds; small aggregate MAE improvement is not a useful state-conditional decision advantage and RMSE is worse. L2, architecture, optimizer seed and selection differ from previous models, so this is not a single-factor L2 ablation. No safety/pruning/acceleration or independent-route generalization claim.'}
review={'status':'PASS_LOCAL_ARTIFACT_AND_SAVED_MODEL_REVIEW','upload_name':UPLOAD.name,'upload_sha256':sha(UPLOAD),'zip_crc':'PASS','manifest_items':len(manifest),'manifest_size_sha_pass':len(manifest),'source_binding_files':len(bindings),'source_bindings_pass':len(bindings),'original_rc':res['rc'],'original_status':res['status'],'counts':{str(k):v for k,v in counts.items()},'saved_models_replayed':len(fitdirs),'saved_validation_predictions_replayed':replays,'outer_selection_choices_recomputed':selcheck,'max_abs_scaled_prediction_error':maxp,'max_abs_loss_or_train_mae_error':maxloss,'max_ridge_stationarity_gradient_norm':ridge_grad,'observation_rows_checked_from_saved_returns':len(record_ids),'max_abs_return_mean_gap_error':maxmeanerr,'original_outcomes':dict(outcomes),'outer_group_splits_match_frozen_parent':True,'inner_splits_exclude_outer_groups':True,'chosen_lambdas_match_inner_scores':True,'local_new_fits':0,'local_new_samples':0,'local_mcts_calls':0,'remote_connection':False,'full_trajectory_replay':False,'inputs_and_previous_results_modified':False,'git_before_after_same':True,'git_status_saved':load(R/'GIT_BEFORE.json'),'timing_as_reported_by_cloud':load(R/'TIMING.json'),'numeric_comparison_tolerance':{'rtol':1e-10,'atol':1e-10},'note':'SHA and CRC are byte checks. Prediction/objective replay does not retrain or prove correctness of physical modeling. Full old collection audit not repeated. Selection/fold identities and saved input roles independently checked.'}
dump('REVIEW.json',review);dump('DESCRIPTIVE_DIAGNOSTIC.json',diag);dump('RECOMPUTED_METRICS.json',allmetrics)
print(json.dumps(review,ensure_ascii=False,indent=2));print('DIAGNOSTIC_SUMMARY',json.dumps({k:v for k,v in diag.items() if k not in ['per_fold_prediction_collapse','old6_examples']},ensure_ascii=False,indent=2))
print('MLP FOLDS',json.dumps(mlpc,ensure_ascii=False,indent=2))
