"""Unmodified numerical definitions from the frozen Window16 original release.
Only the I/O, fold-size validation and old/new reporting are adapted in runner.py.
This module never imports MineSim, opens historical paths, or runs an experiment.
"""
from __future__ import annotations
import math, struct, time
MODELS = ['linear26_to_1', 'mlp26_64_64_16_pair03_30']
SCALE = 100.0


def need(ok, why):
    if not ok: raise RuntimeError(why)


def four_direction(a,b):
    need(len(a)==len(b)==4,'FOUR_PER_BLOCK')
    t=1e-9*max(1.,*(abs(x) for x in a+b))
    return 1 if min(a)>max(b)+t else -1 if min(b)>max(a)+t else None


def feature26(state):
    v=[]
    for name in ('A','B'):
        s=state['vehicles'][name];lo,hi=s['goal_window_m']
        p=s['route_s'];speed=s['speed_mps'];prev=s['prev_action']
        need(hi>0 and type(s['goal_reached']) is bool and
             (prev is None or type(prev) is int and prev in (0,1,2,3)),'STATE_FEATURE_SCHEMA')
        v += [p/hi,(lo-p)/hi,(hi-p)/hi,speed/15.,s['accel_mps2']/3.,
              s['target_speed_mps']/15.,(hi-p-speed*speed/6.)/hi,
              float(s['goal_reached'])]+[float(prev==a) for a in (None,0,1,2,3)]
    need(len(v)==26 and all(math.isfinite(x) for x in v),'FINITE_FEATURE26')
    return list(struct.unpack('<26f',struct.pack('<26f',*v)))


def folds_for(rows):
    folds=[]
    for group in sorted({r['source_run'] for r in rows}):
        tr=[i for i,r in enumerate(rows) if r['source_run']!=group]
        te=[i for i,r in enumerate(rows) if r['source_run']==group]
        need(tr and te and set(tr).isdisjoint(te),'FOLD_INDEX_LEAK')
        need({rows[i]['source_run'] for i in tr}.isdisjoint({rows[i]['source_run'] for i in te}),'SOURCE_RUN_LEAK')
        folds.append({'group':group,'train_indices':tr,'test_indices':te})
    return folds


def init(np,model,seed,dim=26):
    if model==MODELS[0]:return {'W0':np.zeros((dim,1)), 'b0':np.zeros(1)}
    need(model==MODELS[1],'MODEL_ID')
    rng=np.random.RandomState(seed);p={}
    for i,(a,b) in enumerate(zip([dim,64,64],[64,64,16])):
        p['W'+str(i)]=rng.normal(0.,math.sqrt((2. if i<2 else 1.)/a),(a,b));p['b'+str(i)]=np.zeros(b)
    return p


def forward(np,p,X):
    acts=[X];zs=[];n=len(p)//2
    for i in range(n):
        z=acts[-1]@p['W'+str(i)]+p['b'+str(i)];zs.append(z)
        acts.append(np.maximum(z,0.) if i<n-1 else z)
    y=acts[-1];return (y[:,0] if y.shape[1]==1 else y[:,3]-y[:,12]),acts,zs


def loss_grad(np,p,X,target):
    gap,acts,zs=forward(np,p,X);error=gap-target
    loss=float(.5*np.mean(error**2));dg=error/len(target);delta=np.zeros_like(acts[-1])
    if delta.shape[1]==1:delta[:,0]=dg
    else:delta[:,3]=dg;delta[:,12]=-dg
    grad={}
    for i in reversed(range(len(p)//2)):
        grad['W'+str(i)]=acts[i].T@delta;grad['b'+str(i)]=delta.sum(axis=0)
        if i:delta=(delta@p['W'+str(i)].T)*(zs[i-1]>0)
    return loss,grad


def adam(np,p,g,m,v,t,lr):
    for k in sorted(p):
        m[k]*=.9;m[k]+=.1*g[k];v[k]*=.999;v[k]+=.001*g[k]*g[k]
        p[k]-=lr*(m[k]/(1-.9**t))/(np.sqrt(v[k]/(1-.999**t))+1e-8)


class FitInterrupted(RuntimeError):
    def __init__(self,reason,params,updates,history):
        super().__init__(reason);self.params=params;self.updates=updates;self.history=history


def train(np,p,X,target,updates=2000,lr=.001,progress=None,deadline=None):
    need(len(target)>0 and X.shape==(len(target),26) and np.isfinite(X).all() and np.isfinite(target).all(),'TRAIN_ARRAYS')
    need(type(updates) is int and updates>0,'UPDATE_COUNT')
    m={k:np.zeros_like(v) for k,v in p.items()};v={k:np.zeros_like(a) for k,a in p.items()}
    history=[];last=0;initial=loss_grad(np,p,X,target)[0]
    try:
        for step in range(1,updates+1):
            if deadline is not None and time.monotonic()>deadline:raise RuntimeError('DIAGNOSTIC_TIME_LIMIT')
            loss,g=loss_grad(np,p,X,target)
            need(math.isfinite(loss) and all(np.isfinite(a).all() for a in g.values()),'NONFINITE_GRADIENT')
            adam(np,p,g,m,v,step,lr);last=step
            need(all(np.isfinite(a).all() for a in p.values()),'NONFINITE_PARAMETERS')
            if step==1 or step%100==0 or step==updates:
                pred,_,_=forward(np,p,X);rec={'update':step,'loss':float(.5*np.mean((pred-target)**2)),
                      'train_mean_gap_mae_reward_units':float(np.mean(np.abs(pred-target))*SCALE)}
                history.append(rec)
                if progress is not None:progress(rec)
    except (Exception,KeyboardInterrupt) as e:
        raise FitInterrupted(type(e).__name__+':'+str(e),p,last,history) from e
    return p,{'initial_loss':initial,'final_loss':history[-1]['loss'],'updates':last,'progress':history}


def preference(g):return 1 if g>1e-6 else -1 if g < -1e-6 else None


def model_object(p,model,complete,updates):
    return {'model':model,'parameters':{k:v.tolist() for k,v in p.items()},'target_scale':SCALE,
        'output_semantics':'Only gap03-minus30 / 100 supervised; other14 outputs not authorized for decisions.',
        'complete_fit':complete,'completed_updates':updates,'deployable':False,'pruning_authorized':False}
