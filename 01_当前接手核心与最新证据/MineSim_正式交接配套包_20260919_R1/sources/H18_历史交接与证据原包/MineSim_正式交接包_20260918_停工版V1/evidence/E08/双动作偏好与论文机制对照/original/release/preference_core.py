"""Fixed cost-weighted two-action preference study. No simulator or sklearn calls.
A,B are nonnegative empirical cost masses, not independent labels or safety truth.
"""
import math

LAMBDA=1.0
SD_FLOOR=1e-12
GRAD_TOL=1e-9
MAX_UPDATES=64
MAX_BACKTRACK=24
ARMIJO=1e-4

def need(ok,reason):
    if not ok:raise RuntimeError(reason)

def pair_masses(y03,y30):
    """All cross comparisons are deterministic arithmetic reuse, not new samples."""
    a=[float(v) for v in y03];b=[float(v) for v in y30]
    need(len(a)>0 and len(b)>0 and all(math.isfinite(v) for v in a+b),'PAIR_INPUT')
    ds=[u-v for u in a for v in b]
    need(all(math.isfinite(v) for v in ds),'PAIR_OVERFLOW')
    pos=math.fsum(max(v,0.) for v in ds)/len(ds)
    neg=math.fsum(max(-v,0.) for v in ds)/len(ds)
    gap=math.fsum(a)/len(a)-math.fsum(b)/len(b)
    need(math.isclose(pos-neg,gap,rel_tol=1e-12,abs_tol=1e-10),'COST_GAP_IDENTITY')
    return {'A':pos,'B':neg,'empirical_mean_gap':gap,'cost_balance':pos/(pos+neg) if pos+neg>0 else None,
            'pair_comparisons':len(ds),'observations_used':len(a)+len(b),'new_observations':0,
            'independent_pair_count_claimed':False,'hard_label_created':False}

def sigmoid(x):
    import numpy as np
    x=np.asarray(x,dtype=np.float64);out=np.empty_like(x)
    m=x>=0.;out[m]=1./(1.+np.exp(-x[m]));v=np.exp(x[~m]);out[~m]=v/(1.+v)
    return out

def scaler_fit(X):
    import numpy as np
    X=np.asarray(X,dtype=np.float64)
    need(X.ndim==2 and len(X)>0 and np.isfinite(X).all(),'SCALER_INPUT')
    mu=np.mean(X,axis=0);sd=np.std(X,axis=0,ddof=0);active=sd>SD_FLOOR
    return {'mean':mu.tolist(),'scale':np.where(active,sd,1.).tolist(),
            'population_std':sd.tolist(),'active_columns':active.tolist(),'std_floor':SD_FLOOR,
            'trained_only_on_training_rows':True}

def transform(scaler,X):
    import numpy as np
    X=np.asarray(X,dtype=np.float64);mu=np.asarray(scaler['mean']);s=np.asarray(scaler['scale']);act=np.asarray(scaler['active_columns'],dtype=bool)
    need(X.ndim==2 and X.shape[1]==len(mu) and np.isfinite(X).all(),'TRANSFORM_INPUT')
    Z=(X-mu)/s;Z[:,~act]=0.;need(np.isfinite(Z).all(),'TRANSFORM_NONFINITE');return Z

def objective_gradient_hessian(theta,Z,A,B,C,lam=LAMBDA):
    import numpy as np
    theta=np.asarray(theta,dtype=np.float64);Z=np.asarray(Z,dtype=np.float64);A=np.asarray(A,dtype=np.float64);B=np.asarray(B,dtype=np.float64)
    need(Z.ndim==2 and theta.shape==(Z.shape[1]+1,) and A.shape==B.shape==(len(Z),) and C>0 and math.isfinite(C),'OBJECTIVE_SHAPE')
    need(np.isfinite(theta).all() and np.isfinite(Z).all() and np.isfinite(A).all() and np.isfinite(B).all() and np.all(A>=0) and np.all(B>=0) and lam>0,'OBJECTIVE_VALUES')
    a=A/C;b=B/C;n=len(Z);F=np.column_stack((Z,np.ones(n)));f=F@theta;p=sigmoid(f)
    data=float(np.mean(a*np.logaddexp(0.,-f)+b*np.logaddexp(0.,f)))
    penalty=float(.5*lam*np.dot(theta[:-1],theta[:-1]));g=F.T@((a+b)*p-a)/n;g[:-1]+=lam*theta[:-1]
    W=(a+b)*p*(1.-p);h=(F.T*W)@F/n;h[:-1,:-1]+=lam*np.eye(Z.shape[1])
    return data+penalty,g,h,{'data_loss':data,'l2_penalty':penalty,'total':data+penalty}

def fit(X,A,B,progress=None):
    """Training-only deterministic Newton fit. No validation arguments exist."""
    import numpy as np
    X=np.asarray(X,dtype=np.float64);A=np.asarray(A,dtype=np.float64);B=np.asarray(B,dtype=np.float64)
    need(X.ndim==2 and len(X)>0 and A.shape==B.shape==(len(X),) and np.isfinite(X).all(),'FIT_SHAPE')
    need(np.isfinite(A).all() and np.isfinite(B).all() and np.all(A>=0) and np.all(B>=0),'FIT_COSTS')
    scaler=scaler_fit(X);Z=transform(scaler,X);sa=math.fsum(A.tolist());sb=math.fsum(B.tolist());C=(sa+sb)/len(X)
    base={'method':'COST_WEIGHTED_LOGISTIC_TWO_ACTION_V1','scaler':scaler,'input_dim':X.shape[1],
          'lambda':LAMBDA,'C_training_mean_total_cost':C,'training_sumA':sa,'training_sumB':sb,
          'bias_penalized':False,'deployable':False,'pruning_authorized':False,'score_is_safety_probability':False}
    if sa==0. or sb==0.:
        score=.5 if C==0. else 1. if sb==0. else 0.
        rec={'update':0,'mode':'ANALYTIC_BOUNDARY','constant_score':score,'training_objective_infimum':0.}
        if progress:progress(rec)
        base.update(mode='ANALYTIC_BOUNDARY',constant_score=score,weights=[0.]*X.shape[1],bias=None,
                    updates=0,converged=True,objective_infimum=0.,finite_logit_available=C==0.,history=[rec])
        return base
    theta=np.zeros(X.shape[1]+1);theta[-1]=math.log(sa)-math.log(sb);history=[]
    for update in range(MAX_UPDATES+1):
        value,grad,hess,obj=objective_gradient_hessian(theta,Z,A,B,C)
        ginfty=float(np.max(np.abs(grad)))
        rec={'update':update,'objective':obj,'gradient_inf':ginfty,'parameters':theta.tolist()}
        history.append(rec)
        if progress:progress(rec)
        if ginfty<=GRAD_TOL:
            base.update(mode='FINITE_LOGIT',weights=theta[:-1].tolist(),bias=float(theta[-1]),updates=update,
                        converged=True,gradient_inf=ginfty,objective=obj,history=history)
            return base
        need(update<MAX_UPDATES,'NEWTON_MAX_UPDATES_NO_RETRY')
        direction=np.linalg.solve(hess,grad);descent=float(np.dot(grad,direction))
        need(math.isfinite(descent) and descent>0,'NEWTON_DIRECTION')
        accepted=False
        for bt in range(MAX_BACKTRACK):
            alpha=2.**(-bt);candidate=theta-alpha*direction
            trial,_,_,_=objective_gradient_hessian(candidate,Z,A,B,C)
            if trial<=value-ARMIJO*alpha*descent:
                theta=candidate;rec['accepted_step']=alpha;accepted=True;break
        need(accepted,'NEWTON_LINESEARCH_NO_RETRY')
    raise RuntimeError('UNREACHABLE')

def predict(model,X):
    import numpy as np
    X=np.asarray(X,dtype=np.float64);need(X.ndim==2 and X.shape[1]==model['input_dim'] and np.isfinite(X).all(),'PREDICT_INPUT')
    if model['mode']=='ANALYTIC_BOUNDARY':
        scores=np.full(len(X),model['constant_score']);logits=[0. if model['constant_score']==.5 else None]*len(X)
        actions=['0,3' if model['constant_score']>=.5 else '3,0']*len(X)
    else:
        f=transform(model['scaler'],X)@np.asarray(model['weights'])+model['bias'];scores=sigmoid(f);logits=f.tolist()
        actions=['0,3' if v>=0. else '3,0' for v in f]
    return {'logits':logits,'scores':scores.tolist(),'actions':actions}

def choice_loss(mean03,mean30,action):
    need(action in ('0,3','3,0'),'CHOICE_ACTION')
    need(math.isfinite(mean03) and math.isfinite(mean30),'CHOICE_VALUES')
    return max(mean03,mean30)-(mean03 if action=='0,3' else mean30)

def held_cost_loss(model,X,A,B):
    """Held outputs cannot flow back into fit. Use training C, never held-normalization."""
    import numpy as np
    A=np.asarray(A,dtype=np.float64);B=np.asarray(B,dtype=np.float64);C=model['C_training_mean_total_cost']
    if C==0:return {'value':None,'reason':'training_total_cost_zero; no arbitrary denominator'}
    if model['mode']=='ANALYTIC_BOUNDARY':
        opposite=B if model['constant_score']==1. else A
        return {'value':0. if np.all(opposite==0) else None,'reason':'zero' if np.all(opposite==0) else 'infinite_loss_at_boundary; preserved_without_clipping'}
    f=transform(model['scaler'],X)@np.asarray(model['weights'])+model['bias']
    return {'value':float(np.mean((A/C)*np.logaddexp(0.,-f)+(B/C)*np.logaddexp(0.,f))),'reason':None}
