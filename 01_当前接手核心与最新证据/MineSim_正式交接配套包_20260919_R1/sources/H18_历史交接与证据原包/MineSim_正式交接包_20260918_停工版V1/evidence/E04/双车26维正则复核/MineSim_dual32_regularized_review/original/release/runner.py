#!/usr/bin/env python3
"""One authorized dual32 regularized comparison. Existing512 observations only.
Three pre-fixed lambdas are selected in training-source groups only. No simulator
imports, collection, old-model rerun, full32 refit, deployment or automatic retry.
"""
from __future__ import annotations
import argparse
import collections
import hashlib
import io
import json
import math
import os
import signal
import sys
import time
import traceback
import types
import zipfile
from pathlib import Path

DATA = Path('/root/autodl-tmp')
REPO = Path('/root/MineSim-Dynamic')
NAME = 'minesim_dual32_regularized_fit_v1'
RELEASE = 'minesim_dual32_regularized_fit_release_v1.zip'
PARENT = 'minesim_grouped_coverage32_fit16_v1'
GATE = 'DUAL32_FIXED512_REGULARIZED_MODELS_NESTED_GROUP_DEVELOPMENT_V1'
COMPLETE = 'COMPLETE_DUAL32_REGULARIZED_DEVELOPMENT_NOT_ACCELERATION_PROOF'


def need(ok, why):
    if not ok:
        raise RuntimeError(why)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def utc():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


def canon(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(',', ':'), allow_nan=False)+'\n').encode()


def save_early(path, value):
    # create-only bootstrap output even before the inherited helper is loaded
    path = Path(path)
    for p in [path]+list(path.parents):
        need(not p.is_symlink(), 'SYMLINK_REFUSED:'+str(p))
    with path.open('xb') as f:
        f.write(canon(value)); f.flush(); os.fsync(f.fileno())


def load_release(path):
    path = Path(path)
    for p in [path]+list(path.parents):
        need(not p.is_symlink(), 'SYMLINK_REFUSED:'+str(p))
    need(path.is_file() and path.stat().st_size < 4*1024**2, 'RELEASE_TYPE_SIZE')
    raw = path.read_bytes()
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        names = z.namelist()
        need(len(names) == len(set(names)) <= 25 and
             sum(i.file_size for i in z.infolist()) < 8*1024**2, 'RELEASE_MEMBER_LIMIT')
        mf = json.loads(z.read('MANIFEST.json'))
        need(set(names) == set(mf) | {'MANIFEST.json'}, 'RELEASE_MEMBER_SET')
        parts = {}
        for n, rec in mf.items():
            need('/' not in n and '\\' not in n and n not in ('.', '..'), 'RELEASE_UNSAFE_NAME')
            b = z.read(n)
            need({'size': len(b), 'sha256': sha(b)} == rec, 'RELEASE_CONTENT:'+n)
            parts[n] = b
    need(parts['runner.py'] == Path(__file__).read_bytes(), 'RUNNER_RELEASE_DRIFT')
    modules = []
    for n in ['parent_runner.py', 'parent_core.py', 'reg_models.py']:
        mod = types.ModuleType('dual32_'+n[:-3]); mod.__file__ = n
        exec(compile(parts[n], n, 'exec'), mod.__dict__)
        modules.append(mod)
    H, C, M = modules
    prov = H.parse(parts['METHOD_PROVENANCE.json'])
    need(sha(parts['parent_runner.py']) == prov['parent_runner_sha256'] and
         sha(parts['parent_core.py']) == prov['parent_core_sha256'], 'PARENT_HELPER_PROVENANCE')
    H.DATA, H.REPO = DATA, REPO
    return parts, H, C, M, {'sha256': sha(raw), 'size': len(raw)}


def capture_parent(H, binding, out, audit):
    """Read only12 exactly bound files, not all historical collections."""
    got = {}; archives = {}
    try:
        for rel, expected in binding['files'].items():
            H.relative(rel)
            path = DATA/PARENT/rel
            rec = {'logical_path': PARENT+'/'+rel, 'expected': expected}
            if os.path.lexists(path):
                raw = H.read_stable(path)
                rec.update(kind='direct', actual_path=str(path), metadata=H.metadata(path))
            else:
                raw = None
                for name in [PARENT+'.zip']:
                    q = DATA/name
                    if not os.path.lexists(q):
                        continue
                    H.no_symlinks(q)
                    if q not in archives:
                        before = H.metadata(q); z = zipfile.ZipFile(q)
                        names = z.namelist()
                        need(len(names) == len(set(names)), 'PARENT_ZIP_DUPLICATE_NAMES')
                        archives[q] = z, before
                    z, before = archives[q]; member = PARENT+'/'+rel
                    if member not in z.namelist():
                        continue
                    need(z.getinfo(member).file_size == expected['size'], 'PARENT_ZIP_SIZE:'+rel)
                    raw = z.read(member)
                    need(H.metadata(q) == before, 'PARENT_ZIP_CHANGED')
                    rec.update(kind='archive_member', actual_path=str(q), member=member, metadata=before)
                    break
                need(raw is not None, 'MISSING_BOUND_PARENT:'+str(path))
            need({'size': len(raw), 'sha256': sha(raw)} == expected, 'BOUND_PARENT_DRIFT:'+rel)
            H.save(out/'sources'/rel, raw, True)
            got[rel] = raw; audit.append(rec); H.append(out/'INPUT_AUDIT.jsonl', rec)
        mf = H.parse(got['MANIFEST.json'])
        need(all(rel == 'MANIFEST.json' or mf.get(rel) == expected for rel, expected in binding['files'].items()),
             'PARENT_MANIFEST_LINK')
        r = H.parse(got['RESULT.json'])
        need(got['RC.txt'].strip() == b'0' and r['rc'] == 0 and
             r['status'] == 'COMPLETE_COVERAGE32_FIT16_DEVELOPMENT_NOT_GENERALIZATION' and
             r['fits_completed'] == r['fits_started'] == 16 and not r['postcheck_errors'] and not r['errors'],
             'PARENT_FIT16_NOT_COMPLETE')
        need(r['observations'] == 512 and r['roots'] == 32 and r['source_groups'] == 8 and
             r['model_reload_and_metric_readback'] == 'PASS', 'PARENT_COUNT_OR_READBACK')
        need(H.parse(got['GIT_BEFORE.json']) == H.parse(got['POSTCHECK_GIT.json']), 'PARENT_GIT_CHANGED')
        return got
    finally:
        for z, _ in archives.values():
            z.close()


def proc_record(path):
    a = (path/'stat').read_text(); f = a[a.rfind(')')+2:].split()
    argv = [v.decode(errors='replace') for v in (path/'cmdline').read_bytes().split(b'\0') if v]
    b = (path/'stat').read_text(); g = b[b.rfind(')')+2:].split()
    need(f[1] == g[1] and f[19] == g[19], 'PROCESS_IDENTITY_CHANGED:'+str(path))
    return {'pid': int(path.name), 'ppid': int(g[1]), 'start_ticks': int(g[19]), 'argv': argv}


def is_related(argv):
    if not argv:
        return False
    exe = Path(argv[0]).name.lower()
    if not ('python' in exe or exe in ('bash', 'sh', 'dash')) or '-c' in argv[1:3]:
        return False
    # Explicit script arguments only; never match embedded shell bodies or grep text.
    for token in argv[1:]:
        if any(ch.isspace() for ch in token):
            continue
        n = Path(token).name
        if n.endswith(('.sh', '.py')) and (n == 'collect256.py' or n.startswith(('minesim_', 'run_grouped_coverage32_', 'run_dual32_', 'run_window16_'))):
            if any(s in n for s in ('collect', 'fit', 'teacher', 'window', 'smoke', 'regularized', 'diagnostic')):
                return True
    return False


def related_processes(proc_root=Path('/proc'), self_pid=None):
    own = os.getpid() if self_pid is None else self_pid
    chain = []; seen = set(); pid = own
    while pid > 0 and pid not in seen:
        seen.add(pid)
        try:
            rec = proc_record(proc_root/str(pid))
        except FileNotFoundError:
            break
        except PermissionError as e:
            raise RuntimeError('OWN_PROCESS_VISIBILITY_HOLD') from e
        chain.append(rec); pid = rec['ppid']
    need(chain and chain[0]['pid'] == own, 'OWN_PROCESS_NOT_VISIBLE')
    hits = []
    for p in proc_root.iterdir():
        if not p.name.isdigit() or int(p.name) in seen:
            continue
        try:
            rec = proc_record(p)
            if is_related(rec['argv']):
                hits.append(rec)
        except FileNotFoundError:
            continue
        except PermissionError as e:
            raise RuntimeError('PROJECT_PROCESS_VISIBILITY_HOLD:'+str(p)) from e
    return {'hits': sorted(hits, key=lambda r: r['pid']), 'own_ancestor_chain': chain,
            'scope': 'visible interpreter processes with explicit project script arguments; does not certify unrelated jobs'}


def validate_and_plan(H, C, got, parts):
    # Same feature/CAP/alias/old-row validator as the preceding completed run.
    ds_input = {k[len('sources/'):]: v for k, v in got.items() if k.startswith('sources/')}
    ds, legacy_contract, folds, old_ids, validation = H.validate_dataset(
        ds_input, C, H.parse(parts['PARENT_VALIDATION_CONTRACT.json']))
    need(folds == H.parse(got['FOLDS.json']), 'OUTER_SPLIT_DRIFT')
    protocol = H.parse(parts['PROTOCOL.json'])
    need(protocol['frozen_data']['dataset_sha256'] == sha(ds_input['DATASET32.json']), 'DATASET_SHA_PROTOCOL')
    need(protocol['models'] == ['ridge26','mlp26_8_1_l2'] and
         protocol['inner']['lambda_grid'] == [0.01,0.1,1.0] and protocol['small_mlp']['seed'] == 78004 and
         protocol['small_mlp']['updates'] == 2000 and protocol['budget']['fits_total'] == 352, 'METHOD_PROTOCOL_DRIFT')
    plans = []
    rows = ds['rows']
    for f in folds:
        tr = f['train_indices']; te = f['test_indices']
        inner = []
        for group in sorted({rows[i]['source_run'] for i in tr}):
            it = [i for i in tr if rows[i]['source_run'] != group]
            iv = [i for i in tr if rows[i]['source_run'] == group]
            need(len(it) == 24 and len(iv) == 4 and not (set(it+iv) & set(te)), 'INNER_GROUP_LEAK')
            inner.append({'group': group, 'train_indices': it, 'validation_indices': iv,
                          'train_root_ids': [rows[i]['root_id'] for i in it],
                          'validation_root_ids': [rows[i]['root_id'] for i in iv]})
        need(len(inner) == 7, 'INNER_FOLD_COUNT')
        plans.append(dict(f, inner=inner))
    return ds, plans, old_ids, validation, protocol


def independent_forward(np, obj, X):
    p = {k: np.asarray(v,dtype=np.float64) for k,v in obj['parameters'].items()}
    H = X.copy()
    for i in range(len(p)//2):
        H = np.dot(H, p['W'+str(i)]) + p['b'+str(i)]
        if i < len(p)//2-1:
            H = np.where(H > 0., H, 0.)
    return H[:,0]


def verify_saved_fit(H, M, np, dest, Xtrain, ytrain, Xvalid, expected_prediction):
    obj = H.parse(H.read_stable(dest/'MODEL.json'))
    rec = H.parse(H.read_stable(dest/'FIT_RESULT.json'))
    need(obj['complete_fit'] and not obj['deployable'] and not obj['pruning_authorized'], 'READBACK_SCOPE')
    p = {k:np.asarray(v,dtype=np.float64) for k,v in obj['parameters'].items()}
    pv = independent_forward(np,obj,Xvalid)
    need(len(pv) == len(expected_prediction) and np.allclose(pv,expected_prediction,rtol=1e-12,atol=1e-12),
         'INDEPENDENT_READBACK_PREDICTION')
    predtrain = independent_forward(np,obj,Xtrain)
    dataloss = float(.5*np.mean((predtrain-ytrain)**2))
    penalty = .5*obj['lambda']*math.fsum(float(np.sum(v*v)) for k,v in p.items() if k.startswith('W'))
    saved = rec['training']['final']
    need(H.close(dataloss,saved['data_loss']) and H.close(penalty,saved['l2_penalty']) and
         H.close(dataloss+penalty,saved['objective']), 'READBACK_LOSS_OR_REGULARIZER')
    need(np.allclose(np.asarray(rec['validation_predictions_scaled']),pv,rtol=1e-12,atol=1e-12),
         'SAVED_VALIDATION_PREDICTIONS')
    return {'status':'PASS','model':obj['model'],'validation_predictions_checked':len(pv),
            'max_prediction_error':float(np.max(np.abs(pv-np.asarray(expected_prediction)))),
            'new_fits':0}


def one_fit(H, M, np, model, lam, Xtrain, ytrain, Xvalid, train_ids, valid_ids,
            forbidden_ids, dest, state, role, descriptor, deadline):
    need(set(train_ids).isdisjoint(valid_ids) and set(train_ids+valid_ids).isdisjoint(forbidden_ids),
         'FIT_INPUT_IDENTITY_LEAK')
    dest.mkdir(parents=True,exist_ok=False)
    state['fits_started'] += 1; state['active_fit'] = descriptor; state['active_updates_observed'] = 0
    H.save(dest/'FIT_START.json',{'at':utc(),'role':role,'model':model,'lambda':lam,'fit_id':descriptor,
           'train_root_ids':train_ids,'validation_root_ids':valid_ids,'forbidden_outer_root_ids':forbidden_ids,
           'seed':M.SEED if model==M.MODELS[1] else None,'outer_held_not_used_for_selection':True})
    p = M.init(np,model,M.SEED)
    H.save(dest/'INITIAL_MODEL.json',M.dump_model(p,model,lam,False,0,False))
    def progress(rec):
        state['active_updates_observed'] = rec['update']
        H.append(dest/'PROGRESS.jsonl',rec)
    t = time.monotonic()
    try:
        p,hist = M.fit(np,model,p,Xtrain,ytrain,lam,updates=M.UPDATES,lr=M.LR,
                       progress=progress,deadline=deadline)
    except M.InterruptedFit as e:
        state['active_updates_observed'] = e.completed_updates
        H.save(dest/'PARTIAL_MODEL.json',M.dump_model(e.params,model,lam,False,e.completed_updates,e.solve_completed))
        H.save(dest/'PARTIAL_STATE.json',{'reason':str(e),'completed_updates':e.completed_updates,
               'solve_completed':e.solve_completed,'history':e.history,'automatic_resume':False})
        raise
    expected = M.UPDATES if model==M.MODELS[1] else 0
    need(hist['completed_updates']==expected,'FIT_UPDATE_COUNT')
    H.save(dest/'MODEL.json',M.dump_model(p,model,lam,True,expected,hist['closed_form_solve_completed']))
    predictions = M.forward(np,p,Xvalid)
    need(np.isfinite(predictions).all(),'NONFINITE_PREDICTIONS')
    rec = {'model':model,'lambda':lam,'role':role,'fit_id':descriptor,
           'training':hist,'validation_predictions_scaled':predictions.tolist(),
           'train_states':len(ytrain),'validation_states':len(Xvalid),
           'train_root_ids':train_ids,'validation_root_ids':valid_ids,
           'elapsed_seconds':time.monotonic()-t,'data_collection':False,'deployment':False}
    H.save(dest/'FIT_RESULT.json',rec)
    rb = verify_saved_fit(H,M,np,dest,Xtrain,ytrain,Xvalid,predictions)
    H.save(dest/'READBACK.json',rb)
    state['saved_models_readback'] += 1; state['readback_predictions'] += len(predictions)
    state['fits_completed'] += 1; state[role+'_fits_completed'] += 1
    state['mlp_updates_completed_in_finished_fits'] += expected
    state['active_fit'] = None; state['active_updates_observed'] = 0
    H.append(dest/'DONE.jsonl',
             {'fit_complete':True,'at':utc(),'role':role})
    return p,predictions,rec


def inner_select(H, M, np, model, train_rows, forbidden_ids, dest, state, deadline):
    """Receives only the outer training28 states. Outer features/labels are absent."""
    need(len(train_rows)==28 and len({r['source_run'] for r in train_rows})==7,'INNER_INPUT_28_7')
    need(not (set(r['root_id'] for r in train_rows)&set(forbidden_ids)), 'OUTER_ROWS_SUPPLIED_TO_INNER')
    X = np.asarray([r['x'] for r in train_rows],dtype=np.float32).astype(np.float64)
    y = np.asarray([r['empirical_mean_gap03_minus30']/100. for r in train_rows],dtype=np.float64)
    scores = []; groups = sorted({r['source_run'] for r in train_rows})
    for li,lam in enumerate(M.LAMBDAS):
        for gi,group in enumerate(groups):
            it = [i for i,r in enumerate(train_rows) if r['source_run']!=group]
            iv = [i for i,r in enumerate(train_rows) if r['source_run']==group]
            tid = [train_rows[i]['root_id'] for i in it]; vid = [train_rows[i]['root_id'] for i in iv]
            fit_id = dest.parent.name+'_lambda%d_inner%d'%(li,gi)
            p,pred,rec = one_fit(H,M,np,model,lam,X[it],y[it],X[iv],tid,vid,forbidden_ids,
                 dest/('lambda%d_inner%d'%(li,gi)),state,'inner',fit_id,deadline)
            mae = math.fsum(abs(float(pv)-float(y[i]))*100. for pv,i in zip(pred,iv))/len(iv)
            score = {'lambda':lam,'inner_group':group,'mae_reward_units':mae,'fit_id':fit_id,
                     'validation_root_ids':vid,'outer_held_used':False}
            scores.append(score); H.save(dest/('SCORE_lambda%d_inner%d.json'%(li,gi)),score)
    selection = M.select_lambda(scores)
    selection.update(training_root_ids=[r['root_id'] for r in train_rows],forbidden_outer_root_ids=forbidden_ids,
                     inner_fits_completed=21,scores=scores,chosen_before_outer_predictions=True)
    H.save(dest/'SELECTION.json',selection)
    return selection


def outer_records(H, C, np, rows, fold, pred, old_ids):
    tr,te=fold['train_indices'],fold['test_indices']
    baseline=math.fsum(rows[i]['empirical_mean_gap03_minus30'] for i in tr)/len(tr)
    result=[]
    for pv,i in zip(pred,te):
        r=rows[i];p=float(pv)*100.;g=r['empirical_mean_gap03_minus30'];s=r['repeated_order_sign'];old=r['root_id'] in old_ids
        result.append({'root_id':r['root_id'],'source_run':r['source_run'],'is_old16':old,
             'observed_empirical_mean_gap':g,'predicted_mean_gap':p,'signed_error':p-g,'absolute_error':abs(p-g),
             'training_only_constant_gap':baseline,'constant_absolute_error':abs(baseline-g),
             'block_mean_gaps':r['block_mean_gaps'],'block_absolute_errors':[abs(p-v) for v in r['block_mean_gaps']],
             'ordering_subset':'OLD6_CONFIRMED' if old and s is not None else 'OLD10_UNKNOWN' if old else 'NEW16_DESCRIPTIVE',
             'repeated_order_sign':s,'prediction_sign':C.preference(p),
             'known_order_correct':None if s is None else C.preference(p)==s,
             'fixed03_known_order_correct':None if s is None else s==1,
             'constant_known_order_correct':None if s is None else C.preference(baseline)==s,
             'unknown_not_imputed':s is None,'not_Q_star_or_safety_label':True})
    return result


def run_comparison(H, C, M, np, ds, plans, old_ids, out, state, protocol):
    rows=ds['rows'];completed=[];t=time.monotonic();deadline=t+protocol['budget']['runtime_wall_limit_seconds']
    X=np.asarray([r['x'] for r in rows],dtype=np.float32).astype(np.float64)
    y=np.asarray([r['empirical_mean_gap03_minus30']/100. for r in rows],dtype=np.float64)
    for fi,fold in enumerate(plans):
        tr,te=fold['train_indices'],fold['test_indices']
        for model in M.MODELS:
            dest=out/'outer'/('fold%02d_%s'%(fi,model));dest.mkdir(parents=True,exist_ok=False)
            train_rows=[rows[i] for i in tr];held_ids=[rows[i]['root_id'] for i in te]
            sel=inner_select(H,M,np,model,train_rows,held_ids,dest/'inner',state,deadline)
            H.save(dest/'OUTER_SELECTION_LOCK.json',{'at':utc(),'selected_lambda':sel['selected_lambda'],
                   'selection_sha256':sha(H.read_stable(dest/'inner'/'SELECTION.json')),
                   'outer_predictions_created':False})
            # The final model is trained on28 only. Held4 are used only after fitting.
            p,pred,rec=one_fit(H,M,np,model,sel['selected_lambda'],X[tr],y[tr],X[te],
                 [rows[i]['root_id'] for i in tr],held_ids,[],dest/'final',state,'outer',dest.name,deadline)
            held=outer_records(H,C,np,rows,fold,pred,old_ids)
            result={'model':model,'fold':fi,'group_held_out':fold['group'],
                    'selected_lambda':sel['selected_lambda'],'selection':sel['candidate_scores'],
                    'train_roots':[rows[i]['root_id'] for i in tr],'test_roots':held_ids,
                    'training':rec['training'],'held_out':held,
                    'post_outcome_development':True,'independent_route_test':False,'deployable':False}
            H.save(dest/'RESULT.json',result);completed.append(result)
            H.save(out/('PARTIAL_METRICS_%02d.json'%len(completed)),H.aggregate(completed,M.MODELS))
            H.append(out/'PROGRESS.jsonl',{'at':utc(),'outer_models_completed':len(completed),
                     'all_fits_completed':state['fits_completed'],'inner_fits_completed':state['inner_fits_completed'],
                     'elapsed_seconds':time.monotonic()-t})
            elapsed=time.monotonic()-t;eta=elapsed/max(1,state['fits_completed'])*(352-state['fits_completed'])
            print('OUTER_MODELS=%d/16; INNER_FITS=%d/336; MODEL=%s; LAMBDA=%g; ELAPSED=%.1fs; ETA=%.1fs'%(
                  len(completed),state['inner_fits_completed'],model,sel['selected_lambda'],elapsed,eta),flush=True)
    need(state['fits_completed']==352 and state['inner_fits_completed']==336 and state['outer_fits_completed']==16,
         'TOTAL_FIT_BUDGET_MISMATCH')
    # Read saved final objects again to recompute all outer metrics; no extra training.
    readback=[]
    for fi,fold in enumerate(plans):
        for model in M.MODELS:
            dest=out/'outer'/('fold%02d_%s'%(fi,model))
            obj=H.parse(H.read_stable(dest/'final'/'MODEL.json'));rec=H.parse(H.read_stable(dest/'RESULT.json'))
            pred=independent_forward(np,obj,X[fold['test_indices']])
            held=outer_records(H,C,np,rows,fold,pred,old_ids)
            for a,b in zip(held,rec['held_out']):
                need(a['root_id']==b['root_id'] and H.close(a['predicted_mean_gap'],b['predicted_mean_gap']),
                     'FINAL_READBACK_HELD')
            readback.append(dict(rec,held_out=held))
    metrics=H.aggregate(completed,M.MODELS);check=H.aggregate(readback,M.MODELS)
    for model in M.MODELS:
        for k in ('mae','rmse','constant_mae','constant_rmse'):
            need(H.close(metrics[model]['all32_empirical_gap_errors'][k],check[model]['all32_empirical_gap_errors'][k]),
                 'FINAL_READBACK_METRICS')
        fs=[r for r in completed if r['model']==model];stats=metrics[model]['all32_empirical_gap_errors']
        metrics[model]['both_MAE_and_RMSE_below_constant']=stats['mae']<stats['constant_mae'] and stats['rmse']<stats['constant_rmse']
        metrics[model]['groups_with_lower_MAE_than_constant']=sum(v['mae']<v['constant_mae'] for v in metrics[model]['per_source_group'].values())
        metrics[model]['selected_lambdas']={r['group_held_out']:r['selected_lambda'] for r in fs}
        metrics[model]['worst_held_absolute_error']=max(r['absolute_error'] for f in fs for r in f['held_out'])
        metrics[model]['is_acceleration_proof']=False
    H.save(out/'READBACK_CHECK.json',{'status':'PASS','saved_models_checked':state['saved_models_readback'],
          'inner_and_outer_predictions_checked':state['readback_predictions'],'outer_predictions':64,
          'full_trajectory_checks_repeated':False,'new_fits_for_readback':0})
    H.save(out/'TIMING.json',{'fit_selection_readback_seconds':time.monotonic()-t,
          'worker_processes':1,'numeric_threads':1,'excludes_preflight_package_upload':True})
    return metrics


def report(metrics):
    lines=['双车32状态／512条回报：正则模型开发对照','',
           '保持数据、特征、8来源外层划分不变。正则强度只在每折训练7组内部选择。',
           '336次内部小拟合+16个外层模型；不采集、不执行MCTS、不训练单车。',
           '本轮已看过历史结果，仍为同一路线事后开发；不是新的盲测或加速证明。','']
    for name,r in metrics.items():
        a=r['all32_empirical_gap_errors']
        lines += [name,'MAE=%.8f; RMSE=%.8f; constantMAE=%.8f; constantRMSE=%.8f'%(
                  a['mae'],a['rmse'],a['constant_mae'],a['constant_rmse']),
                  'Both metrics below constant: '+str(r['both_MAE_and_RMSE_below_constant']),
                  'Groups below constant MAE: %d/8'%r['groups_with_lower_MAE_than_constant'],'']
    lines += ['执行完整不要求模型赢；负结果同样封存。不得直接部署、剪枝、自动追加数据或启动单车。']
    return '\n'.join(lines)+'\n'


def execute(authorized=False):
    need(authorized,'EXPLICIT_NEW_METHOD_AUTHORIZATION_REQUIRED')
    out=DATA/NAME;lease=DATA/(NAME+'.lease.json')
    for p in [out,lease,Path(str(out)+'.zip'),Path(str(out)+'.zip.pending')]:
        need(not os.path.lexists(p),'ONE_TIME_NAMESPACE_EXISTS:'+str(p))
    save_early(lease,{'at':utc(),'pid':os.getpid(),'gate':GATE,'authorization':'new regularized comparison once',
                     'automatic_retry':False,'new_data':False})
    out.mkdir(exist_ok=False)
    state={'status':'PRE_RUNTIME_TECHNICAL_HOLD','gate':GATE,'resource':'LOW','started_utc':utc(),
           'scientific_start_written':False,'fits_planned':352,'fits_started':0,'fits_completed':0,
           'inner_fits_completed':0,'outer_fits_completed':0,'saved_models_readback':0,'readback_predictions':0,
           'mlp_updates_completed_in_finished_fits':0,'active_fit':None,'active_updates_observed':0,
           'new_teacher_traces':0,'mcts_calls':0,'old_model_retraining':0,'single_vehicle_experiments':0,
           'full32_refit':False,'deployment_authorized':False,'pruning_authorized':False,
           'automatic_retry':False,'sources_verified':0,'errors':[],'postcheck_errors':[]}
    H=None;audit=[];before=None;release_meta=None;rc=2
    def stop(signum,frame):
        raise KeyboardInterrupt('SIGNAL_'+str(signum))
    oldhandlers={s:signal.signal(s,stop) for s in (signal.SIGTERM,signal.SIGINT,signal.SIGHUP)}
    try:
        parts,H,C,M,release_meta=load_release(DATA/RELEASE)
        for name,raw in parts.items():H.save(out/'release'/name,raw,True)
        H.save(out/'RELEASE_BINDING.json',release_meta)
        np,env=H.environment();H.save(out/'ENVIRONMENT.json',env)
        res=H.resource_snapshot();H.save(out/'RESOURCES.json',res)
        need(res['available_memory_bytes']>=256*1024**2 and res['free_disk_bytes']>=128*1024**2,'LOW_RESOURCE_HOLD')
        proc=related_processes();H.save(out/'PROCESSES_BEFORE.json',proc);need(not proc['hits'],'OTHER_PROJECT_RUN_HOLD')
        before=H.git_snapshot();H.save(out/'GIT_BEFORE.json',before)
        got=capture_parent(H,H.parse(parts['SOURCE_BINDINGS.json']),out,audit);state['sources_verified']=len(audit)
        parentgit=H.parse(got['POSTCHECK_GIT.json'])
        need(before['head']==parentgit['head'] and before['diff_sha256']==parentgit['diff_sha256'],'TRACKED_REPO_DRIFT')
        state['untracked_status_matches_parent']=before['status']==parentgit['status']
        ds,plans,old_ids,validation,protocol=validate_and_plan(H,C,got,parts)
        H.save(out/'INPUT_VALIDATION.json',validation);H.save(out/'OUTER_INNER_SPLIT_PLAN.json',plans)
        H.save(out/'EXECUTION_PROTOCOL.json',protocol)
        H.save(out/'PARENT_METRICS_REFERENCE.json',{'parent_result_sha256':sha(got['RESULT.json']),
               'metrics':H.parse(got['RESULT.json'])['metrics'],'read_only_reference_not_new_fits':True})
        H.save(out/'START.json',{'at':utc(),'gate':GATE,'source_count':len(audit),
               'protocol_sha256':sha(parts['PROTOCOL.json']),'dataset_sha256':sha(got['sources/DATASET32.json']),
               'fits_total':352,'inner_fits':336,'outer_models':16,'new_observations':0,
               'authorization':'--authorize-dual32-models-once'})
        state['scientific_start_written']=True;state['status']='RUNNING_DUAL32_REGULARIZED_DEVELOPMENT'
        print('START=DUAL32_REGULARIZED; SOURCES=12/12; ROOTS=32; RETURNS=512; OUTER_MODELS=16; INNER_FITS=336; NEW_SAMPLES=0',flush=True)
        metrics=run_comparison(H,C,M,np,ds,plans,old_ids,out,state,protocol)
        H.save(out/'METRICS.json',metrics);H.save(out/'SUMMARY.txt',report(metrics).encode(),True)
        state.update(status=COMPLETE,metrics=metrics,roots=32,observations=512,source_groups=8,
                     scientific_model_advantage='see held metrics; no automatic method deployment',
                     acceleration_tested=False)
        rc=0
    except (Exception,KeyboardInterrupt) as e:
        state['errors'].append({'type':type(e).__name__,'message':str(e)})
        state['status']='RUNTIME_TECHNICAL_HOLD' if state['scientific_start_written'] else 'PRE_RUNTIME_TECHNICAL_HOLD'
        with (out/'ERROR.txt').open('x',encoding='utf-8') as f:f.write(traceback.format_exc())
    finally:
        for s,h in oldhandlers.items():signal.signal(s,h)
        if H is not None:
            checks=[]
            if audit:checks.append(('PARENT',lambda:H.parent_postcheck(audit)))
            checks.append(('PROCESS',related_processes))
            if before is not None:checks.append(('GIT',H.git_snapshot))
            for label,fn in checks:
                try:
                    v=fn();H.save(out/('POSTCHECK_'+label+'.json'),v)
                    if label=='PROCESS':need(not v['hits'],'POSTCHECK_OTHER_PROJECT_RUN')
                    if label=='GIT':need(v==before,'POSTCHECK_GIT_CHANGED')
                except Exception as e:state['postcheck_errors'].append({'check':label,'message':str(e)})
            if release_meta is not None:
                try:need(sha(H.read_stable(DATA/RELEASE))==release_meta['sha256'],'RELEASE_CHANGED_DURING_RUN')
                except Exception as e:state['postcheck_errors'].append({'check':'RELEASE','message':str(e)})
        if state['postcheck_errors']:
            if rc==0:state['status']='HOLD_POSTCHECK_COMPLETED_FITS_PRESERVED'
            rc=2
        state['sources_verified']=len(audit);state['finished_utc']=utc();state['rc']=rc
        state['hard_kill_note']='If killed outside caught exception handling, last observed updates are only a lower bound. No implicit retry.'
        save_early(out/'RESULT.json',state)
        with (out/'RC.txt').open('xb') as f:f.write((str(rc)+'\n').encode())
        save_early(out/'CAPTURE.json',{'at':utc(),'status':state['status'],'scientific_start_written':state['scientific_start_written'],
              'completed_outer_models':state['outer_fits_completed'],'all_completed_fits':state['fits_completed'],
              'new_data':0,'single_vehicle':0,'automatic_retry':False})
        print('STATUS='+state['status'],flush=True)
        print('OUTER_MODELS_COMPLETED=%d/16; INNER_FITS_COMPLETED=%d/336; SOURCES_VERIFIED=%d/12; NEW_SAMPLES=0; MCTS_CALLS=0; SINGLE_VEHICLE=0'%(
              state['outer_fits_completed'],state['inner_fits_completed'],len(audit)),flush=True)
        try:
            if H is None:raise RuntimeError('HELPER_NOT_LOADED: upload launcher log or preserved output; no invented bundle')
            bundle,digest=H.package(out)
            print('BUNDLE='+str(bundle),flush=True);print('ZIP_VERIFIED=True; ZIP_SHA256='+digest,flush=True)
        except Exception:
            print('PACKAGING_HOLD: output/pending preserved, no retry.\n'+traceback.format_exc(),flush=True)
            print('OUTPUT_DIR='+str(out),flush=True);rc=2
    return rc


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--authorize-dual32-models-once',action='store_true',required=True)
    a=p.parse_args()
    try:return execute(a.authorize_dual32_models_once)
    except (Exception,KeyboardInterrupt):
        print('ENTRY_HOLD: preserve all prior artifacts; no automatic retry.\n'+traceback.format_exc(),flush=True)
        return 2


if __name__=='__main__':
    sys.exit(main())
