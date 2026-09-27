"""Fixed-lambda train-only standardization ablation. No I/O or tuning."""
import numpy as np

LAMBDA=1.0
MIN_STD=1e-12
SCALE=100.0

def require(ok, why):
    if not ok: raise RuntimeError(why)

def prepare(X):
    X=np.asarray(X,dtype=np.float64)
    require(X.ndim==2 and len(X)>0 and np.isfinite(X).all(),'X_TRAIN_SCHEMA')
    mean=X.mean(axis=0)
    centered=X-mean
    std=np.sqrt(np.mean(centered*centered,axis=0))
    active=std>MIN_STD
    scale=np.where(active,std,1.)
    Z=centered/scale
    Z[:,~active]=0.
    return Z,{'mean':mean.tolist(),'std_population':std.tolist(),'scale':scale.tolist(),
              'active_columns':active.tolist(),'std_floor':MIN_STD,'fit_source':'training_rows_only',
              'constant_column_policy':'set transformed train and held values to zero; no learned coefficient'}

def transform(X,scaler):
    X=np.asarray(X,dtype=np.float64);mu=np.asarray(scaler['mean']);s=np.asarray(scaler['scale']);active=np.asarray(scaler['active_columns'],dtype=bool)
    require(X.ndim==2 and X.shape[1]==len(mu) and np.isfinite(X).all() and (s>0).all(),'X_TRANSFORM_SCHEMA')
    Z=(X-mu)/s;Z[:,~active]=0.
    require(np.isfinite(Z).all(),'NONFINITE_STANDARDIZED_X')
    return Z

def fit(X,y):
    X=np.asarray(X,dtype=np.float64);y=np.asarray(y,dtype=np.float64)
    require(y.ndim==1 and len(y)==len(X) and len(y)>0 and np.isfinite(y).all(),'Y_SCHEMA')
    Z,scaler=prepare(X)
    zm=Z.mean(0);ym=float(y.mean());Zc=Z-zm
    w=np.linalg.solve(Zc.T@Zc+len(y)*LAMBDA*np.eye(X.shape[1]),Zc.T@(y-ym))
    b=float(ym-zm@w);pred=Z@w+b;res=pred-y
    data=float(.5*np.mean(res**2));pen=float(.5*LAMBDA*np.sum(w*w))
    stationarity=float(np.sqrt(np.sum((Z.T@res/len(y)+LAMBDA*w)**2)+float(res.mean())**2))
    require(np.isfinite(w).all() and np.isfinite(b) and stationarity<1e-9*max(1.,float(np.linalg.norm(y))),'SOLVE_STATIONARITY')
    return {'model':'ridge36_train_standardized_lambda1','weights':w.tolist(),'bias':b,'scaler':scaler,
            'lambda':LAMBDA,'input_dim':X.shape[1],'target_scale':SCALE,
            'objective':{'data_loss':data,'l2_penalty':pen,'total':data+pen,'stationarity_norm':stationarity},
            'train_mae_reward_units':float(np.mean(abs(res))*SCALE),'complete_fit':True,
            'deployable':False,'pruning_authorized':False,'full16_action_values':False}

def predict(obj,X):
    return transform(X,obj['scaler'])@np.asarray(obj['weights'])+obj['bias']
