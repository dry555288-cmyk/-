"""Static new-model pilot preparation. Python 3.9 stdlib; no simulator imports."""
from __future__ import annotations
import hashlib
import json
import math
import struct
from fractions import Fraction

MODEL = 'DUAL_ONLY_DESTINATION_STOP_CANDIDATE_V1'
CODEC = 'DUAL_ONLY_STOP_STATE_CODEC_V1'
SCHEMA = 'DUAL_STOP_ROUTE_BOUND_FEATURE26_V1'
ACTION_ORDER = [f'{i},{j}' for i in range(4) for j in range(4)]
ACCELS = (-3.0, -1.5, 0.0, 1.0)
EPISODES = ['C11_100M_SEED0_EP1', 'C11_80M_SEED0_EP0']
PHASES = {'discovery': [76000,76001,76002,76003],
          'confirmation': [77000,77001,77002,77003]}
STRATA = ['START_FULL','CLOSE_RECORDED_SEGMENT_FULL',
          'BRAKING_RESTRICTED_MULTI','BRAKING_TIGHT_MULTI',
          'ONE_PARKED_MULTI','SINGLE_ACTION_CONTROL']
FEATURE_NAMES = [t + '_' + n for t in ('A','B') for n in (
    'route_fraction','remaining_to_goal_lower_fraction','remaining_to_goal_upper_fraction',
    'speed_over_15','command_accel_over_3','target_speed_over_15',
    'braking_margin_fraction','parked','previous_NONE','previous_BRAKE',
    'previous_DECEL','previous_KEEP','previous_ACCEL')]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(obj):
    return (json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':'),
                       allow_nan=False)+'\n').encode('utf-8')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def strict_json(data):
    def pairs(items):
        d={}
        for k,v in items:
            need(k not in d,'DUPLICATE_JSON_KEY:'+k);d[k]=v
        return d
    def bad(s):
        raise ValueError('NONFINITE_JSON:'+s)
    result=json.loads(data,object_pairs_hook=pairs,parse_constant=bad)
    def check(x):
        if isinstance(x,float): need(math.isfinite(x),'NONFINITE_JSON_FLOAT')
        elif isinstance(x,dict):
            for v in x.values(): check(v)
        elif isinstance(x,list):
            for v in x: check(v)
    check(result)
    return result


def finite(x,name):
    need(type(x) in (int,float) and math.isfinite(x),'INVALID_NUMBER:'+name)
    return float(x)


def validate_state(s):
    need(isinstance(s,dict) and s.get('schema')==CODEC and s.get('model_version')==MODEL,'STATE_VERSION')
    need(set(s['vehicles'])=={'A','B'},'EXACTLY_A_B')
    for flag,pairs in [('internal_collision','conflicting_pairs'),
                       ('internal_safety_violation','safety_violating_pairs')]:
        need(type(s[flag]) is bool,'FLAG_TYPE')
        need(s[pairs] in ([],[['A','B']]) and bool(s[pairs])==s[flag],'FLAG_PAIRS')
        need(not s[flag],'HARD_TERMINAL_ROOT')
    need(s['internal_clearance_status']=='SAMPLED' and
         finite(s['minimum_internal_clearance_m'],'clearance')>=0,'ROOT_CLEARANCE_UNAVAILABLE')
    for t in ('A','B'):
        v=s['vehicles'][t]
        need(v['acceleration_semantics']=='COMMANDED_NOT_MEASURED','ACCEL_SEMANTICS')
        need(v['external_lead']=={'mode':'NONE','distance_m':None,'relative_speed_mps':None}
             and v['minimum_external_clearance_m'] is None,'EXTERNAL_SCOPE')
        need(type(v['collision']) is bool and not v['collision'],'EXTERNAL_COLLISION')
        need(type(v['goal_reached']) is bool,'PARK_FLAG')
        lo,hi=[finite(x,'goal') for x in v['goal_window_m']]
        need(hi>=.5 and hi-lo==.5,'GOAL_WINDOW')
        pos=finite(v['route_s'],'route_s'); speed=finite(v['speed_mps'],'speed')
        need(0<=pos<=hi and 0<=speed<=15,'STATE_DOMAIN')
        need(finite(v['target_speed_mps'],'target')>0,'TARGET_SPEED')
        finite(v['accel_mps2'],'command_accel')
        tm=finite(v['time_s'],'time');need(tm>=0,'TIME_DOMAIN')
        prev=v['prev_action']
        need(prev is None or type(prev) is int and prev in range(4),'PREVIOUS_ACTION')
        parked=lo<=pos<=hi and speed==0
        need(v['goal_reached']==parked,'PARK_SEMANTICS')
        if parked:
            pt=finite(v['parked_at_time_s'],'parked_at');need(0<=pt<=tm,'PARK_TIME')
        else: need(v['parked_at_time_s'] is None,'UNPARKED_TIMESTAMP')
    need(s['vehicles']['A']['time_s']==s['vehicles']['B']['time_s'],'CLOCKS_DIFFER')
    need(not all(v['goal_reached'] for v in s['vehicles'].values()),'COMPLETED_ROOT')


def feature26(s):
    """Route-bound projection, not a universal state representation or network."""
    validate_state(s)
    xs=[]
    for t in ('A','B'):
        v=s['vehicles'][t];lo,hi=v['goal_window_m'];p=v['route_s'];u=v['speed_mps']
        xs += [p/hi,(lo-p)/hi,(hi-p)/hi,u/15.,v['accel_mps2']/3.,
               v['target_speed_mps']/15.,(hi-p-u*u/6.)/hi,float(v['goal_reached'])]
        xs += [float(v['prev_action']==a) for a in (None,0,1,2,3)]
    need(len(xs)==26 and all(math.isfinite(x) for x in xs),'FEATURES_FINITE26')
    b=struct.pack('<26f',*xs)
    f32=list(struct.unpack('<26f',b))
    need(all(math.isfinite(x) for x in f32),'FEATURE_FLOAT32_OVERFLOW')
    return {'schema':SCHEMA,'feature_order':FEATURE_NAMES,'float64':xs,'float32':f32,
            'float32_le_sha256':digest(b)}


def scalar_action_mask(v):
    """Algebraic mask audit only; no state object is advanced or simulator called.

    Mirrors the frozen motion source's float arithmetic and Fraction boundary
    branch. The recorded mask is authoritative and must equal this audit.
    """
    ans=[];p=v['route_s'];u=v['speed_mps'];upper=v['goal_window_m'][1];dt=.5
    for a in ACCELS:
        if a<0 and dt>=u/-a:
            distance=u*u/(-2*a);v1=0.
        elif a>0 and dt>=(15.-u)/a:
            hit=(15.-u)/a;distance=math.fsum(((u+15.)*hit*.5,15.*(dt-hit)));v1=15.
        elif a==0: distance=u*dt;v1=u
        else: distance=u*dt+.5*a*dt*dt;v1=u+a*dt
        s1=math.fsum((p,distance));stop=math.fsum((s1,v1*v1/6.))
        band=16*math.ulp(max(1.,abs(stop),abs(upper),abs(p)))
        if abs(stop-upper)<=band:
            qv,qa,qt,qmax=map(Fraction,(u,a,dt,15.))
            if qa<0 and qv+qa*qt<=0: qd=qv*qv/(-2*qa);q1=Fraction(0)
            elif qa>0 and qv+qa*qt>=qmax:
                hit=(qmax-qv)/qa;qd=(qv+qmax)*hit/2+qmax*(qt-hit);q1=qmax
            else: qd=qv*qt+qa*qt*qt/2;q1=qv+qa*qt
            ok=Fraction(upper)-(Fraction(p)+qd+q1*q1/6)>=0 and s1<=upper
        else: ok=stop<=upper and s1<=upper
        if v['goal_reached']: ok=a==0
        ans.append(bool(ok))
    return ans


def checked_mask(row):
    validate_state(row['state'])
    a=scalar_action_mask(row['state']['vehicles']['A']);b=scalar_action_mask(row['state']['vehicles']['B'])
    mask=[x and y for x in a for y in b]
    observed=row['active_mask_16']
    need(len(observed)==16 and all(type(x) is bool for x in observed),'MASK_TYPE')
    need(row['action_order_16']==ACTION_ORDER,'ACTION_ORDER')
    need(mask==observed and sum(mask)==row['active_action_count'] and any(mask),'MASK_MISMATCH')
    return mask


def select_roots(rows):
    need(len({r['record_id'] for r in rows})==len(rows),'DUPLICATE_RECORD_IDS')
    chosen=[]
    for ep in EPISODES:
        pool=[r for r in rows if r['task']['episode_uid']==ep]
        count=lambda r:sum(v['goal_reached'] for v in r['state']['vehicles'].values())
        first=lambda r:(r['step_index'],r['record_id'])
        defs=[
            (lambda r:r['step_index']==0 and r['active_action_count']==16,first),
            (lambda r:r['step_index']>0 and count(r)==0 and r['active_action_count']==16,
             lambda r:(r['state']['minimum_internal_clearance_m'],r['record_id'])),
            (lambda r:count(r)==0 and 4<r['active_action_count']<16,first),
            (lambda r:count(r)==0 and 1<r['active_action_count']<=4,first),
            (lambda r:count(r)==1 and r['active_action_count']>1,first),
            (lambda r:r['active_action_count']==1,lambda r:(count(r)!=1,r['step_index'],r['record_id']))]
        for name,(predicate,key) in zip(STRATA,defs):
            candidates=[r for r in pool if predicate(r)]
            need(bool(candidates),'EMPTY_STRATUM:'+ep+':'+name)
            r=min(candidates,key=key)
            chosen.append({'pilot_root_id':f'root_{len(chosen):02d}', 'stratum':name,
                           'eligible_pool_count':len(candidates),
                           'role':'SINGLE_ACTION_STATIC_CONTROL' if r['active_action_count']==1 else 'TEACHER_DECISION_ROOT',
                           'behavior_record':r})
    need(len({x['behavior_record']['exact_before_state_sha256'] for x in chosen})==12,'DUPLICATE_SELECTED_STATE')
    return chosen


def schedule(selected,phase):
    need(phase in PHASES,'PHASE')
    rows=[]
    for root in selected:
        r=root['behavior_record']
        if root['role']!='TEACHER_DECISION_ROOT':continue
        for j,allowed in enumerate(r['active_mask_16']):
            if not allowed:continue
            action=ACTION_ORDER[j]
            for rep_index,rep in enumerate(PHASES[phase]):
                seed_material={'schema':'DUAL_STOP_TEACHER_RNG_V1','phase':phase,
                               'state_sha256':r['exact_before_state_sha256'],
                               'action_id':action,'replicate_id':rep}
                seed=int(digest(canonical(seed_material))[:16],16)
                rows.append({'cell_id':f'{phase}__{root["pilot_root_id"]}__a{j:02d}__r{rep}',
                             'ordinal':len(rows),'phase':phase,'pilot_root_id':root['pilot_root_id'],
                             'source_record_id':r['record_id'],'root_state_sha256':r['exact_before_state_sha256'],
                             'first_action_id':action,'action_index':j,'replicate_id':rep,'replicate_index':rep_index,'rng_seed':seed,
                             'rng_derivation':seed_material,'maximum_outer_steps':128,
                             'max_followup_search_calls':127,'runtime_authorized':False})
    need(len(rows)==384,'SCHEDULE_COUNT_384')
    need(len({r['cell_id'] for r in rows})==len(rows),'DUPLICATE_CELL')
    need(len({r['rng_seed'] for r in rows})==len(rows),'DUPLICATE_RNG')
    return rows


def summarize_action(samples):
    """Prospective label rule; synthetic tests only until genuine labels exist."""
    if len(samples)!=4:return {'status':'MISSING_REPLICATES'}
    if {r.get('replicate_index') for r in samples}!={0,1,2,3}:return {'status':'REPLICATE_ID_MISMATCH'}
    if any(not r.get('technical_complete') for r in samples):return {'status':'TECHNICAL_MISSING'}
    allowed={'BOTH_PARKED_AT_OWN_DESTINATIONS','EXECUTED_HARD_SAFETY_TERMINAL','EVALUATION_CAP_NOT_TASK_TERMINAL'}
    if any(r.get('outcome') not in allowed for r in samples):return {'status':'BAD_OUTCOME'}
    vals=[finite(r['discounted_return'],'sample_return') for r in samples]
    if any(r['outcome']=='EVALUATION_CAP_NOT_TASK_TERMINAL' for r in samples):
        return {'status':'UNKNOWN_CENSORED_TASK_TAIL','finite_window_values':vals}
    return {'status':'COMPLETE_TERMINAL_BLOCK','min':min(vals),'max':max(vals),'values':vals}


def pair_direction(a,b):
    aa,bb=summarize_action(a),summarize_action(b)
    if aa['status']!='COMPLETE_TERMINAL_BLOCK' or bb['status']!='COMPLETE_TERMINAL_BLOCK':
        return {'status':'UNRESOLVED','a':aa['status'],'b':bb['status'],'direction':None}
    tol=1e-9*max([1.]+[abs(x) for x in aa['values']+bb['values']])
    if aa['min']>bb['max']+tol:d='A_GT_B'
    elif bb['min']>aa['max']+tol:d='B_GT_A'
    else:d=None
    return {'status':'EMPIRICALLY_SEPARATED' if d else 'OVERLAPPING_OR_NUMERICALLY_INDISTINGUISHABLE',
            'direction':d,'numerical_tolerance':tol,'confidence_level':None}


def confirmed_pair(d_a,d_b,c_a,c_b):
    d,c=pair_direction(d_a,d_b),pair_direction(c_a,c_b)
    if d['direction'] and d['direction']==c['direction']:status='REPLICATED_ORDER_CANDIDATE'
    elif d['direction'] and c['direction'] and d['direction']!=c['direction']:status='CONFLICT_BETWEEN_BLOCKS'
    else:status='UNCONFIRMED'
    return {'status':status,'discovery':d,'confirmation':c,
            'training_mask':0,'safety_pruning_authorized':False,'confidence_level':None}
