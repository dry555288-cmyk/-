#!/usr/bin/env python3
"""One fixed train-only scaling ablation, eight ridge solves; no MCTS or collection."""
import argparse,hashlib,io,json,math,os,signal,sys,time,traceback,types,zipfile
from pathlib import Path
DATA=Path('/root/autodl-tmp');REPO=Path('/root/MineSim-Dynamic')
NAME='minesim_dual32_scaledridge_fit_v1'
RELEASE='minesim_dual32_scaledridge_release_v1.zip'
PARENT='minesim_dual32_interaction_fit_v1'
DS='sources/parent/sources/sources/DATASET32.json'
COMPLETE='COMPLETE_DUAL32_SCALING_ABLATION_NOT_ACCELERATION_PROOF'

def need(ok,reason):
    if not ok:raise RuntimeError(reason)

def sha(raw):return hashlib.sha256(raw).hexdigest()

def load_release():
    q=DATA/RELEASE
    for p in [q]+list(q.parents):need(not p.is_symlink(),'RELEASE_SYMLINK')
    raw=q.read_bytes();need(len(raw)<4*1024**2,'RELEASE_SIZE')
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        names=z.namelist();need(len(names)==len(set(names))<=20,'RELEASE_MEMBERS')
        need(sum(i.file_size for i in z.infolist())<8*1024**2,'RELEASE_EXPANSION_LIMIT')
        mf=json.loads(z.read('MANIFEST.json'));need(set(names)==set(mf)|{'MANIFEST.json'},'RELEASE_MANIFEST_SET')
        parts={}
        for n,meta in mf.items():
            need('/' not in n and '\\' not in n and n not in ('.','..'),'RELEASE_PATH')
            b=z.read(n);need(meta=={'size':len(b),'sha256':sha(b)},'RELEASE_BYTES:'+n);parts[n]=b
    need(parts['runner.py']==Path(__file__).read_bytes(),'RELEASE_RUNNER_DRIFT')
    mods=[]
    for n in ['io_helpers.py','process_checks.py','scaled_ridge.py']:
        m=types.ModuleType('scale8_'+n[:-3]);m.__file__=n
        exec(compile(parts[n],n,'exec'),m.__dict__);mods.append(m)
    H,P,K=mods;H.DATA=DATA;H.REPO=REPO
    return parts,H,P,K,{'size':len(raw),'sha256':sha(raw)}

def capture(H,binding,out,audit):
    need(binding['parent_namespace']==PARENT and binding['source_count']==len(binding['files'])==10,'BINDING_SCHEMA')
    got={};archives={}
    try:
        for rel,expected in binding['files'].items():
            H.relative(rel);p=DATA/PARENT/rel
            rec={'logical_path':PARENT+'/'+rel,'expected':expected}
            if os.path.lexists(p):
                raw=H.read_stable(p);rec.update(kind='direct',actual_path=str(p),metadata=H.metadata(p))
            else:
                q=DATA/(PARENT+'.zip');need(os.path.lexists(q),'MISSING_SOURCE:'+str(p));H.no_symlinks(q)
                if q not in archives:
                    meta=H.metadata(q);z=zipfile.ZipFile(q);ns=z.namelist();need(len(ns)==len(set(ns)),'PARENT_DUPLICATE_MEMBERS');archives[q]=z,meta
                z,meta=archives[q];member=PARENT+'/'+rel
                need(member in z.namelist() and z.getinfo(member).file_size==expected['size'],'PARENT_MEMBER:'+member)
                raw=z.read(member);need(H.metadata(q)==meta,'PARENT_ZIP_CHANGED')
                rec.update(kind='archive_member',actual_path=str(q),metadata=meta,member=member)
            need({'size':len(raw),'sha256':sha(raw)}==expected,'SOURCE_SHA:'+rel)
            H.save(out/'sources'/rel,raw,True);audit.append(rec);H.append(out/'INPUT_AUDIT.jsonl',rec);got[rel]=raw
        mf=H.parse(got['MANIFEST.json'])
        for n,m in binding['files'].items():
            if n!='MANIFEST.json':need(mf.get(n)==m,'PARENT_MANIFEST_LINK:'+n)
        return got
    finally:
        for z,_ in archives.values():z.close()

def validate(H,np,got,protocol):
    parent=H.parse(got['RESULT.json']);prior=H.parse(got['EXECUTION_PROTOCOL.json'])
    need(got['RC.txt'].strip()==b'0' and parent['rc']==0 and parent['status']=='COMPLETE_DUAL32_INTERACTION_FEATURE_DEVELOPMENT_NOT_ACCELERATION_PROOF','PARENT_NOT_COMPLETE')
    need(parent['fits_completed']==352 and parent['outer_fits_completed']==16 and parent['inner_fits_completed']==336 and not parent['errors'] and not parent['postcheck_errors'],'PARENT_COUNTS_ERRORS')
    need(H.parse(got['GIT_BEFORE.json'])==H.parse(got['POSTCHECK_GIT.json']),'PARENT_GIT_DRIFT')
    need(set(parent['metrics']['ridge36']['selected_lambdas'].values())=={1.0},'PRESERVED_PRIOR_LAMBDA')
    need(protocol['lambda']==1.0 and protocol['fits']==8 and protocol['inner_fits']==0 and protocol['scaler_sd_floor']==1e-12,'PROTOCOL_NUMERIC_DRIFT')
    need(sha(got[DS])==protocol['dataset_sha256'] and sha(got['FEATURE36_MATRIX_AND_AUDIT.json'])==protocol['feature_matrix_sha256'],'DATA_PROTOCOL_SHA')
    ds=H.parse(got[DS]);fa=H.parse(got['FEATURE36_MATRIX_AND_AUDIT.json']);rows=ds['rows'];by={r['root_id']:r for r in fa['rows']}
    need(len(rows)==len(by)==32 and ds['observations']==512 and ds['roots']==32,'DATASET_COUNTS')
    need(ds['target_id']=='DUAL_STOP_FIXED_WINDOW64_STOPPED_RETURN_V1' and not ds['cross_group_exact_aliases'],'DATASET_TARGET_ALIAS')
    ids=[r['root_id'] for r in rows];need(len(set(ids))==32 and set(ids)==set(by),'ROOT_IDENTITIES')
    cellids=set();outcomes={};X=[];y=[]
    for r in rows:
        rid=r['root_id'];fr=by[rid]
        need(fr['source_run']==r['source_run'] and fr['state_sha256']==r['state_sha256'],'FEATURE_STATE_BINDING')
        need(len(fr['x36'])==36 and fr['x36'][:26]==r['x'],'FEATURE36_PREFIX')
        need(r['mask16']==[True]*16 and not r['pruning_authorized'],'ROOT_MASK')
        samples=r['records'];need(len(samples)==16,'OBSERVATION_PER_ROOT')
        for s in samples:
            need(s['cell_id'] not in cellids and s['root_id']==rid and s['window_target_observed'] is True,'OBSERVATION_ID_WINDOW')
            cellids.add(s['cell_id']);outcomes[s['task_outcome']]=outcomes.get(s['task_outcome'],0)+1
            need(1<=s['executed_steps']<=128 and s['maximum_outer_steps']==128 and math.isfinite(s['window_return']),'WINDOW_LENGTH')
            if s['task_outcome']=='EVALUATION_CAP_NOT_TASK_TERMINAL':need(s['executed_steps']==128 and s['old_full_task_return'] is None,'CAP_SEMANTICS')
        means={}
        for action in ('0,3','3,0'):
            vals=[s['window_return'] for s in samples if s['action_id']==action];need(len(vals)==8,'ACTION_REPEATS');means[action]=math.fsum(vals)/8
        need(H.close(means['0,3']-means['3,0'],r['empirical_mean_gap03_minus30']),'EMPIRICAL_TARGET')
        X.append(fr['x36']);y.append(r['empirical_mean_gap03_minus30']/100.)
    need(len(cellids)==512 and outcomes=={'BOTH_PARKED_AT_OWN_DESTINATIONS':467,'EVALUATION_CAP_NOT_TASK_TERMINAL':45},'OBSERVATION_TOTALS')
    plans=H.parse(got['OUTER_INNER_SPLIT_PLAN.json']);need(len(plans)==8,'OUTER_FOLDS')
    groups=sorted({r['source_run'] for r in rows});need(groups==['policy_%02d'%i for i in range(8)],'GROUP_NAMES')
    for f,g in zip(plans,groups):
        tr=[i for i,r in enumerate(rows) if r['source_run']!=g];te=[i for i,r in enumerate(rows) if r['source_run']==g]
        need(f['group']==g and f['train_indices']==tr and f['test_indices']==te and len(tr)==28 and len(te)==4,'FOLD_INDICES')
        need(f['train_root_ids']==[ids[i] for i in tr] and f['test_root_ids']==[ids[i] for i in te],'FOLD_IDENTITIES')
    pair=H.parse(got['PAIRED_FEATURE_COMPARISON.json'])['ridge36']['paired_all32'];old={r['root_id']:r for r in pair}
    need(set(old)==set(ids) and len(pair)==32,'PAIRED_REFERENCE_SET')
    for r in rows:need(old[r['root_id']]['observed_mean_gap']==r['empirical_mean_gap03_minus30'],'PAIRED_TARGET')
    X=np.asarray(X,dtype=np.float64);y=np.asarray(y,dtype=np.float64)
    need(X.shape==(32,36) and y.shape==(32,) and np.isfinite(X).all() and np.isfinite(y).all(),'NUMERIC_DATA')
    return rows,X,y,plans,old

def aggregate(np,records):
    need(len(records)==32 and len({a['root_id'] for a in records})==32,'METRICS_ALL32')
    result={}
    for key in ['prediction','constant','saved_raw36_ridge','saved_raw26_ridge']:
        e=np.asarray([a[key]-a['observed_mean_gap'] for a in records]);result[key]={'mae':float(np.mean(abs(e))),'rmse':float(np.sqrt(np.mean(e*e)))}
    result['numerically_below_constant_and_raw36']=all(result['prediction'][k]<result[m][k] for k in ['mae','rmse'] for m in ['constant','saved_raw36_ridge'])
    result['subsets']={}
    for subset in ['old16','new16']:
        rs=[r for r in records if r['subset']==subset];known=[r for r in rs if r['repeated_order_sign'] is not None]
        result['subsets'][subset]={'count':len(rs),'ordering_known':len(known),'ordering_unknown':len(rs)-len(known),'mae':float(np.mean([abs(r['prediction']-r['observed_mean_gap']) for r in rs])),
            'order_correct':sum((1 if r['prediction']>1e-6 else -1 if r['prediction']< -1e-6 else 0)==r['repeated_order_sign'] for r in known),
            'fixed03_correct':sum(r['repeated_order_sign']==1 for r in known),'unknowns_not_scored':True}
    result['no_significance_or_safety_claim']=True
    return result

def run_folds(H,K,np,out,rows,X,y,plans,old,state):
    completed=[];started=time.monotonic()
    for i,f in enumerate(plans):
        need(time.monotonic()-started<120,'FIT_TIME_LIMIT')
        tr,te=f['train_indices'],f['test_indices'];dest=out/'fits'/('fold%02d'%i)
        start={'at':H.utc(),'group':f['group'],'train_root_ids':f['train_root_ids'],'held_root_ids':f['test_root_ids'],'lambda':1.,'preprocessing_training_only':True}
        H.save(dest/'FIT_START.json',start);state['fits_started']+=1;state['active_fit']=i
        model=K.fit(X[tr],y[tr]);model.update(train_root_ids=f['train_root_ids'],held_root_ids=f['test_root_ids'],source_group_held=f['group'])
        H.save(dest/'MODEL.json',model)
        predicted=K.predict(model,X[te])*100.;trainpred=K.predict(model,X[tr]);const=math.fsum(y[tr].tolist())/len(tr)*100.
        loaded=H.parse(H.read_stable(dest/'MODEL.json'))
        # Independent saved-model evaluation, no new solve.
        mu=np.asarray(loaded['scaler']['mean']);s=np.asarray(loaded['scaler']['scale']);active=np.asarray(loaded['scaler']['active_columns'],dtype=bool);w=np.asarray(loaded['weights'])
        z=(X[te]-mu)/s;z[:,~active]=0.;reloaded=(z@w+loaded['bias'])*100.
        need(np.allclose(predicted,reloaded,rtol=1e-12,atol=1e-10),'MODEL_READBACK')
        zt=(X[tr]-mu)/s;zt[:,~active]=0.;res=zt@w+loaded['bias']-y[tr]
        need(H.close(.5*np.mean(res**2),loaded['objective']['data_loss']) and H.close(.5*np.sum(w*w),loaded['objective']['l2_penalty']),'OBJECTIVE_READBACK')
        held=[]
        for j,pv in zip(te,predicted):
            r=rows[j];ref=old[r['root_id']]
            held.append({'root_id':r['root_id'],'source_run':r['source_run'],'subset':'new16' if r['root_id'].startswith('coverage_') else 'old16','observed_mean_gap':r['empirical_mean_gap03_minus30'],'prediction':float(pv),'constant':const,'saved_raw36_ridge':ref['new36_prediction'],'saved_raw26_ridge':ref['old26_prediction'],'repeated_order_sign':r['repeated_order_sign'],'CAP_samples_retained':True})
        flagged=[int(k) for k in np.where(~active)[0] if np.any(np.abs(X[te,k]-mu[k])>1e-12)]
        H.save(dest/'RESULT.json',{'group':f['group'],'held_out':held,'train_mae':float(np.mean(abs(trainpred-y[tr]))*100),'train_only_constant_columns_varying_in_held':flagged,'readback_max_abs_error':float(np.max(abs(predicted-reloaded))),'new_samples':0,'deployable':False})
        completed+=held;state['fits_completed']+=1;state['saved_models_readback']+=1;state['active_fit']=None
        H.append(out/'PROGRESS.jsonl',{'at':H.utc(),'fits_completed':state['fits_completed'],'fits_planned':8})
        print('FITS_COMPLETED=%d/8; INNER_FITS=0; OPTIMIZER_UPDATES=0; NEW_SAMPLES=0'%state['fits_completed'],flush=True)
    metrics=aggregate(np,completed)
    H.save(out/'PREDICTIONS.json',completed);H.save(out/'METRICS.json',metrics)
    H.save(out/'TIMING.json',{'eight_solves_and_readback_seconds':time.monotonic()-started,'excludes_preflight_packaging_upload':True})
    return metrics

def execute(authorized):
    need(authorized,'EXPLICIT_SCALING_ABLATION_AUTHORIZATION_REQUIRED')
    parts,H,P,K,release_meta=load_release()
    out=DATA/NAME;lease=DATA/(NAME+'.lease.json')
    for p in [out,lease,Path(str(out)+'.zip'),Path(str(out)+'.zip.pending')]:
        H.no_symlinks(p);need(not os.path.lexists(p),'ONE_TIME_NAMESPACE_EXISTS:'+str(p))
    H.save(lease,{'at':H.utc(),'pid':os.getpid(),'automatic_retry':False,'authorization':'eight new standardized ridge folds once; no new data'})
    out.mkdir(exist_ok=False)
    state={'status':'PRE_RUNTIME_TECHNICAL_HOLD','resource':'LOW','scientific_start_written':False,'fits_started':0,'fits_completed':0,'saved_models_readback':0,'fits_planned':8,'inner_fits':0,'optimizer_updates':0,'active_fit':None,'new_teacher_traces':0,'mcts_calls':0,'single_vehicle_experiments':0,'neural_fits':0,'full32_refit':False,'automatic_retry':False,'deployment_authorized':False,'pruning_authorized':False,'errors':[],'postcheck_errors':[]}
    audit=[];before=None;rc=2
    def stop(signum,frame):raise KeyboardInterrupt('SIGNAL_'+str(signum))
    handlers={s:signal.signal(s,stop) for s in [signal.SIGTERM,signal.SIGINT,signal.SIGHUP]}
    try:
        for n,b in parts.items():H.save(out/'release'/n,b,True)
        H.save(out/'RELEASE_BINDING.json',release_meta)
        np,env=H.environment();H.save(out/'ENVIRONMENT.json',env)
        res=H.resource_snapshot();H.save(out/'RESOURCES.json',res);need(res['available_memory_bytes']>=256*1024**2 and res['free_disk_bytes']>=64*1024**2,'LOW_RESOURCE_HOLD')
        pr=P.related_processes();H.save(out/'PROCESSES_BEFORE.json',pr);need(not pr['hits'],'OTHER_PROJECT_PROCESS')
        before=H.git_snapshot();H.save(out/'GIT_BEFORE.json',before)
        got=capture(H,H.parse(parts['SOURCE_BINDINGS.json']),out,audit)
        pg=H.parse(got['POSTCHECK_GIT.json']);need(before['head']==pg['head'] and before['diff_sha256']==pg['diff_sha256'],'TRACKED_REPO_DRIFT')
        protocol=H.parse(parts['PROTOCOL.json']);rows,X,y,plans,old=validate(H,np,got,protocol)
        H.save(out/'EXECUTION_PROTOCOL.json',protocol)
        H.save(out/'INPUT_VALIDATION.json',{'sources':10,'states':32,'returns':512,'outcomes_unchanged':True,'source_groups':8,'features':36,'old_unknowns_unchanged':True})
        H.save(out/'START.json',{'at':H.utc(),'protocol_sha256':sha(parts['PROTOCOL.json']),'gate':protocol['gate'],'fits':8,'new_samples':0})
        state['scientific_start_written']=True;state['active_stage']='EIGHT_FIXED_SCALING_FOLDS'
        print('START=DUAL32_SCALING_ABLATION; ROOTS=32; RETURNS=512; FITS=8; INNER_FITS=0; GPU=False',flush=True)
        metrics=run_folds(H,K,np,out,rows,X,y,plans,old,state)
        state.update(status=COMPLETE,metrics=metrics,observations=512,roots=32,source_groups=8,numerical_advantage=metrics['numerically_below_constant_and_raw36'],acceleration_tested=False);rc=0
    except (Exception,KeyboardInterrupt) as e:
        state['errors'].append({'type':type(e).__name__,'message':str(e)});state['status']='RUNTIME_TECHNICAL_HOLD' if state['scientific_start_written'] else 'PRE_RUNTIME_TECHNICAL_HOLD';H.save(out/'ERROR.txt',traceback.format_exc().encode(),True)
    finally:
        for s,h in handlers.items():signal.signal(s,h)
        checks=[]
        if audit:checks.append(('PARENT',lambda:H.parent_postcheck(audit)))
        checks.append(('PROCESS',P.related_processes))
        if before is not None:checks.append(('GIT',H.git_snapshot))
        for label,fn in checks:
            try:
                value=fn();H.save(out/('POSTCHECK_'+label+'.json'),value)
                if label=='PROCESS':need(not value['hits'],'POSTCHECK_RELATED_PROCESS')
                if label=='GIT':need(value==before,'POSTCHECK_GIT_CHANGED')
            except Exception as e:state['postcheck_errors'].append({'check':label,'message':str(e)})
        try:need(sha(H.read_stable(DATA/RELEASE))==release_meta['sha256'],'RELEASE_DRIFT')
        except Exception as e:state['postcheck_errors'].append({'check':'RELEASE','message':str(e)})
        if state['postcheck_errors']:
            if rc==0:state['status']='HOLD_POSTCHECK_FITS_PRESERVED'
            rc=2
        state.update(finished_utc=H.utc(),rc=rc,sources_verified=len(audit))
        H.save(out/'RESULT.json',state);H.save(out/'RC.txt',(str(rc)+'\n').encode(),True)
        H.save(out/'CAPTURE.json',{'at':H.utc(),'fits_completed':state['fits_completed'],'scientific_start_written':state['scientific_start_written'],'automatic_retry':False})
        print('STATUS='+state['status'],flush=True);print('FITS_COMPLETED=%d/8; SOURCES_VERIFIED=%d/10; NEW_SAMPLES=0; MCTS_CALLS=0'%(state['fits_completed'],len(audit)),flush=True)
        if rc==0:print('NUMERICAL_ADVANTAGE='+str(state['numerical_advantage'])+'; ACCELERATION_TESTED=False',flush=True)
        try:
            bundle,digest=H.package(out);print('BUNDLE='+str(bundle),flush=True);print('ZIP_VERIFIED=True; ZIP_SHA256='+digest,flush=True)
        except Exception:
            print('PACKAGING_HOLD: preserve output/pending; no retry.\n'+traceback.format_exc(),flush=True);print('OUTPUT_DIR='+str(out),flush=True);rc=2
    return rc

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--authorize-scale8-once',action='store_true',required=True);a=p.parse_args()
    try:return execute(a.authorize_scale8_once)
    except (Exception,KeyboardInterrupt):
        print('ENTRY_HOLD: original files protected; upload launcher log.\n'+traceback.format_exc(),flush=True);return 2
if __name__=='__main__':sys.exit(main())
