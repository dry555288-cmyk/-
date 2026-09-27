"""Read-only review of the supplied archive. No simulation, fitting or model imports."""
from pathlib import Path
import zipfile, json, hashlib, math, random, struct, time
from collections import Counter
from datetime import datetime

HERE=Path(__file__).resolve().parent
ARCHIVE=HERE/'minesim_grouped_coverage32_collect256_v1.reassembled.zip'
PREFIX='minesim_grouped_coverage32_collect256_v1/'

def canon(x):
    return (json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()
def sha(b): return hashlib.sha256(b).hexdigest()
def require(ok, message):
    if not ok: raise ValueError(message)
def old_status(s, k, cap):
    cars=s['vehicles']
    hard=s['internal_collision'] or s['internal_safety_violation'] or any(v['collision'] for v in cars.values())
    if hard:return 'HARD_SAFETY_TERMINAL'
    if all(v['goal_reached'] for v in cars.values()):
        require(all(v['goal_window_m'][0]<=v['route_s']<=v['goal_window_m'][1] and v['speed_mps']==0 for v in cars.values()),'FALSE_PARKED')
        return 'BOTH_PARKED_AT_OWN_DESTINATIONS'
    return 'EVALUATION_CAP_NOT_TASK_TERMINAL' if k==cap else 'RUNNING'
def reward_value(before,after,context):
    cfg=context['reward_config'];fc=context['fleet_config'];total=0.
    for t in ['A','B']:
        p=before['vehicles'][t];n=after['vehicles'][t]
        if p['goal_reached']: continue
        progress=cfg['w_progress']*max(0.,n['route_s']-p['route_s'])/max(p['target_speed_mps']*.5,cfg['eps'])
        speed=cfg['w_speed']*(-abs(n['speed_mps']-n['target_speed_mps'])/max(n['target_speed_mps'],cfg['eps']))
        comfort=cfg['w_comfort']*(-(abs(n['accel_mps2']-p['accel_mps2'])/.5)/10.)
        require(n['external_lead']=={'mode':'NONE','distance_m':None,'relative_speed_mps':None} and n['minimum_external_clearance_m'] is None,'EXTERNAL_SCOPE')
        total+=progress+speed+0.+comfort
        total+=cfg['goal_bonus'] if n['goal_reached'] else 0.
    risk=max(0.,min(1.,(fc['internal_clearance_safe_m']-after['minimum_internal_clearance_m'])/fc['internal_clearance_safe_m']))
    hard=after['internal_collision'] or after['internal_safety_violation'] or any(v['collision'] for v in after['vehicles'].values())
    return total/2.-fc['w_internal_clearance']*risk*risk-(cfg['collision_penalty'] if hard else 0.)
def features(s):
    x=[]
    for t in ['A','B']:
        v=s['vehicles'][t];lo,hi=v['goal_window_m'];p=v['route_s'];u=v['speed_mps']
        x.extend([p/hi,(lo-p)/hi,(hi-p)/hi,u/15.,v['accel_mps2']/3.,v['target_speed_mps']/15.,(hi-p-u*u/6.)/hi,float(v['goal_reached'])])
        x.extend(float(v['prev_action']==a) for a in (None,0,1,2,3))
    b=struct.pack('<26f',*x)
    return list(struct.unpack('<26f',b)),sha(b)

t0=time.monotonic(); checked=[]; errors=[]; max_reward_error=0.;max_return_error=0.;all_steps=0;all_searches=0
with zipfile.ZipFile(ARCHIVE) as z:
    def raw(rel):return z.read(PREFIX+rel)
    def get(rel):return json.loads(raw(rel))
    manifest=get('MANIFEST.json');result=get('RESULT.json');protocol=get('EFFECTIVE_COLLECTION_PROTOCOL.json')
    tasks=get('runtime/inputs/FUTURE_256_TASKS_NOT_AUTHORIZED.json')
    roots={r['root_id']:r for r in get('runtime/inputs/SELECTED_NEW16.json')}
    observations=get('NEW256_OBSERVATIONS.json')['records'];obs_byid={r['cell_id']:r for r in observations}
    require(len(tasks)==len(obs_byid)==len(observations)==256,'OBS_COUNTS')
    require({s['cell_id'] for s in tasks}==set(obs_byid),'TASK_SET')
    order=[f'{a},{b}' for a in range(4) for b in range(4)]
    for task in tasks:
        cell=task['cell_id'];cp='cells/'+cell+'/'
        try:
            root=roots[task['root_id']];obs=obs_byid[cell]
            start=get(cp+'CELL_START.json');summary=get(cp+'SUMMARY.json');commit=get(cp+'COMMIT.json');trace=get(cp+'TRACE.json')
            spec=start['spec'];require(spec['static_task']==task,'SCHEDULE_CONTENT');require(summary['spec']==commit['spec']==trace['spec']==spec,'SPEC_BINDING')
            require(start['initial']==root['state'] and sha(canon(start['initial']))==task['state_sha256'],'ROOT_BINDING')
            require(start['technical_only'] is False and start['teacher_sample'] is True and start['batch_execution_authorized'] is True,'FORMAL_SAMPLE')
            require(raw(cp+'RC.txt').strip()==b'0','CELL_RC')
            require(commit['teacher_sample'] is True and summary['teacher_sample'] is True,'SAMPLE_SCOPE')
            actual={n[len(cp):] for n in manifest if n.startswith(cp)}
            require(actual==set(commit['files'])|{'COMMIT.json'},'COMMIT_MEMBER_SET')
            require(all(manifest[cp+n]==meta for n,meta in commit['files'].items()),'COMMIT_OUTER_MANIFEST_MATCH')
            require(sha(raw(cp+'COMMIT.json'))==obs['commit_sha256'],'OBS_COMMIT_SHA')
            rows=trace['rows'];steps=sorted(n for n in commit['files'] if n.startswith('steps/'))
            require(steps==[f'steps/{i:04d}.json' for i in range(len(rows))],'STEP_NAMES')
            require(0<len(rows)<=128,'STEP_CAP')
            state=start['initial'];rng=start['rng_initial']
            require(rng==json.loads(canon(random.Random(task['rng_seed']).getstate())),'INITIAL_RNG')
            context=get('runtime/inputs/contexts/'+root['task']['episode_uid']+'.json')
            cell_reward_error=0.;searches=0
            for k,step in enumerate(rows):
                require(step==get(cp+steps[k]),'TRACE_STEP_CONTENT')
                require(step['step_index']==k and step['cell_id']==cell,'STEP_ID')
                require(step['before']==state and step['rng_before']==rng,'STATE_RNG_CHAIN')
                for key in ['before','after','rng_before','rng_after']:
                    require(step[key+'_sha256']==sha(canon(step[key])),'HASH_'+key)
                active=step['active_ids'];action=step['action_id']
                require(step['active_mask_16']==[a in active for a in order] and action in active,'ACTION_MASK')
                if k==0:
                    require(step['selection']=='FORCED_FIRST' and step['diagnostics'] is None and action==task['first_action_id'] and step['rng_after']==rng,'FORCED_ACTION')
                else:
                    d=step['diagnostics'];searches+=1
                    require(step['selection']=='NATIVE_B64_H8' and d['iterations']==64 and d['seed']==task['rng_seed'],'SEARCH_PROTOCOL')
                    require(d['active_joint_action_ids']==active and d['active_mask_16']==step['active_mask_16'],'SEARCH_DOMAIN')
                    require(set(d['visits'])==set(d['q_values'])==set(active) and sum(d['visits'].values())==64 and all(isinstance(v,int) and v>0 for v in d['visits'].values()),'VISITS')
                    require(all(math.isfinite(q) for q in d['q_values'].values()),'FINITE_Q')
                    chosen=max(active,key=lambda a:(d['visits'][a],d['q_values'][a],tuple(-int(x) for x in a.split(','))))
                    require(chosen==action,'SAVED_SEARCH_CHOICE')
                require(math.isfinite(step['reward']),'FINITE_REWARD')
                er=abs(step['reward']-reward_value(state,step['after'],context));cell_reward_error=max(cell_reward_error,er)
                require(er<=1e-10*max(1.,abs(step['reward']),abs(reward_value(state,step['after'],context))),'REWARD_FORMULA')
                require(old_status(step['after'],k+1,128)==step['outcome_after_step'],'STOP_SEMANTICS')
                if k<len(rows)-1:require(step['outcome_after_step']=='RUNNING','AFTER_TERMINAL_STEP')
                state=step['after'];rng=step['rng_after']
            require(summary['initial']==start['initial'] and summary['final']==state and summary['rng_final']==rng,'SUMMARY_STATE_RNG')
            require(summary['executed_steps']==obs['executed_steps']==len(rows) and summary['native_search_calls']==obs['native_search_calls']==searches,'CELL_COUNT')
            require(summary['outcome']==obs['task_outcome']==rows[-1]['outcome_after_step']!='RUNNING','TERMINAL')
            ret=math.fsum((.99**i)*r['reward'] for i,r in enumerate(rows))
            reterr=abs(ret-summary['finite_window_return']);max_return_error=max(max_return_error,reterr)
            require(ret==summary['finite_window_return']==obs['window_return'],'WINDOW_RETURN_EXACT')
            require(summary['discount_origin']=='forced_first_transition_k0' and summary['discount_gamma']==.99 and obs['window_target_observed'] is True,'TARGET_RULE')
            is_cap=summary['outcome']=='EVALUATION_CAP_NOT_TASK_TERMINAL'
            require(summary['tail_censored']==obs['old_full_task_tail_censored']==is_cap,'CENSOR_FLAG')
            require(summary['full_task_return']==obs['old_full_task_return']==(None if is_cap else ret),'FULL_TASK_RETURN')
            require(not is_cap or len(rows)==128,'COMPLETE_CAP_WINDOW')
            for a,b in [('action_id','first_action_id'),('root_id','root_id'),('source_run','source_run'),('replicate_id','replicate_id'),('rng_seed','rng_seed'),('block','block'),('ordinal','ordinal'),('root_state_sha256','state_sha256')]:require(obs[a]==task[b],'OBS_'+a)
            events=[json.loads(b) for b in raw(cp+'EVENTS.jsonl').splitlines() if b]
            require([e['seq'] for e in events]==list(range(len(events))),'EVENT_SEQUENCE')
            saved=[e for e in events if e['event']=='STEP_SAVED']
            require([e['step_index'] for e in saved]==list(range(len(rows))),'STEP_EVENTS')
            require(all(e['sha256']==manifest[cp+steps[i]]['sha256'] for i,e in enumerate(saved)),'EVENT_STEP_SHA')
            for event in ['SEARCH_STARTED','SEARCH_RETURNED']:require(sum(e['event']==event for e in events)==searches,'SEARCH_EVENTS')
            all_steps+=len(rows);all_searches+=searches;max_reward_error=max(max_reward_error,cell_reward_error)
            checked.append({'cell_id':cell,'source_run':task['source_run'],'root_id':task['root_id'],'steps':len(rows),'searches':searches,'outcome':summary['outcome'],'window_return':ret,'reward_formula_max_absolute_error':cell_reward_error})
        except Exception as exc: errors.append({'cell_id':cell,'error':str(exc)})
    require(not errors,'CELL_REVIEW_ERRORS:'+str(errors[:4]))
    dataset=get('DATASET32.json');old=get('runtime/inputs/OLD_DATASET16.json');rows=dataset['rows']
    old_ids={r['root_id'] for r in old['rows']};rmap={r['root_id']:r for r in rows}
    require(len(rows)==len(rmap)==32 and dataset['roots']==32,'ROOT32')
    require([r for r in rows if r['root_id'] in old_ids]==old['rows'],'OLD_ROWS_UNCHANGED')
    require(sha(raw('runtime/inputs/OLD_DATASET16.json'))==dataset['old_dataset_sha256']==protocol['old_dataset_sha256'],'OLD_DATASET_SHA')
    counts=Counter(r['source_run'] for r in rows);require(counts=={f'policy_{i:02d}':4 for i in range(8)},'SOURCE_GROUPS')
    seen=[];mean_max_error=0.;relation_signs={};cap_rows=[]
    for r in rows:
        records=r['records'];require(len(records)==16,'REPEATS_PER_ROOT')
        require(Counter(q['action_id'] for q in records)=={'0,3':8,'3,0':8},'ACTION_BALANCE')
        require(Counter((q['block'],q['action_id']) for q in records)=={(b,a):4 for b in ['block0','block1'] for a in ['0,3','3,0']},'BLOCK_BALANCE')
        f,fh=features(r['full_state']);require(f==r['x'] and fh==r['feature_sha256'] and sha(canon(r['full_state']))==r['state_sha256'],'FEATURE_STATE_SHA')
        seen.extend((r['root_id'],q['action_id'],q['replicate_id'],q['block']) for q in records)
        means={a:math.fsum(q['window_return'] for q in records if q['action_id']==a)/8 for a in ['0,3','3,0']}
        gap=means['0,3']-means['3,0'];mean_max_error=max(mean_max_error,abs(gap-r['empirical_mean_gap03_minus30']))
        require(abs(gap-r['empirical_mean_gap03_minus30'])<=1e-12,'EMPIRICAL_GAP')
        if r['root_id'] not in old_ids:
            require(records==[q for q in observations if q['root_id']==r['root_id']],'NEW_ROWS_OBSERVATIONS')
            require(set(q['replicate_id'] for q in records)==set(range(82000,82008)),'FIXED_REPLICATES')
            signs=[]
            for b in ['block0','block1']:
                aa=[q['window_return'] for q in records if q['block']==b and q['action_id']=='0,3'];bb=[q['window_return'] for q in records if q['block']==b and q['action_id']=='3,0']
                tolerance=1e-9*max(1.,max(map(abs,aa+bb)))
                signs.append(1 if min(aa)>max(bb)+tolerance else -1 if min(bb)>max(aa)+tolerance else 0)
            sign=signs[0] if signs[0]!=0 and signs[0]==signs[1] else None
            require(sign==r['repeated_order_sign'],'REPEATED_DIRECTION')
            relation_signs[r['root_id']]=sign
        cap_rows.extend(q for q in records if q['task_outcome']=='EVALUATION_CAP_NOT_TASK_TERMINAL')
    require(len(seen)==len(set(seen))==512,'OBS512_UNIQUE')
    cross_alias=[]
    for i,r in enumerate(rows):
        for q in rows[i+1:]:
            if r['source_run']!=q['source_run'] and (r['feature_sha256']==q['feature_sha256'] or r['state_sha256']==q['state_sha256']):cross_alias.append([r['root_id'],q['root_id']])
    require(not cross_alias,'CROSS_GROUP_EXACT_ALIAS')
    worker_rows=[]
    for w in range(16):
        wd=f'workers/worker_{w}/';wr=get(wd+'RESULT.json');schedule=get(wd+'SHARD_SCHEDULE.json')
        require(raw(wd+'RC.txt').strip()==b'0' and wr['rc']==0,'WORKER_RC')
        worker_rows.append({'worker':w,'rc':0,'counts':wr['counts']})
    require(all_steps==result['outer_steps']==11592 and all_searches==result['mcts_calls']==11336,'RESULT_TOTALS')
    require(get('GIT_BEFORE.json')==get('GIT_AFTER.json'),'GIT_SNAPSHOTS')
    require(int(raw('RC.txt'))==0 and result['status']=='COMPLETE_COVERAGE32_NEW256_VERIFIED_NOT_MODEL_SUCCESS' and result['postcheck_status']=='PASS','FINAL_STATUS')
    require(result['training_runs']==0 and result['model_forward_calls']==0 and result['old_returns_recollected']==0,'EXECUTION_SCOPE')
    for rel in ['runtime/FUTURE_FITTING_CONTRACT_NOT_AUTHORIZED.json','runtime/inputs/OLD_DATASET16.json','runtime/inputs/COMBINED32_INPUTS.json','runtime/inputs/SELECTED_NEW16.json','runtime/inputs/FUTURE_256_TASKS_NOT_AUTHORIZED.json','runtime/inputs/FUTURE_TEACHER_PROTOCOL.json','PARENT_BINDINGS.json','RESOURCES.json','ENVIRONMENT.json']:
        (HERE/'original'/Path(rel).name).write_bytes(raw(rel))
    review={
      'status':'PASS_DATA_COLLECTION_AND_MERGED_DATASET_REVIEW_NOT_MODEL_SUCCESS',
      'archive':str(ARCHIVE),'manifest_review':'MANIFEST_REVIEW.json',
      'verified_new_cells':len(checked),'saved_steps_checked':all_steps,'recorded_searches_checked':all_searches,
      'window_returns_recomputed_exactly':len(checked),'max_window_return_absolute_error':max_return_error,
      'reward_formula_relative_tolerance_from_frozen_code':1e-10,'max_scalar_reward_absolute_error':max_reward_error,
      'new_outcomes':dict(Counter(r['outcome'] for r in checked)),
      'merged_roots':32,'merged_observations':512,'old_observations_reused_unchanged':256,
      'merged_outcomes':dict(Counter(q['task_outcome'] for r in rows for q in r['records'])),
      'source_groups':dict(counts),'cross_group_exact_aliases':cross_alias,
      'empirical_gap_max_absolute_error':mean_max_error,
      'old_hard_order_known':sum(r['repeated_order_sign'] is not None for r in old['rows']),
      'old_order_unknown':sum(r['repeated_order_sign'] is None for r in old['rows']),
      'new_descriptive_repeated_orders':dict(Counter(str(v) for v in relation_signs.values())),
      'new_descriptive_coverage_denominator':16,'new_descriptive_not_safety_labels':True,
      'cloud_worker_elapsed_seconds':get('COLLECTION_TIMING.json')['elapsed_seconds'],
      'cloud_start_to_result_seconds':(datetime.fromisoformat(result['finished_utc'])-datetime.fromisoformat(get('START.json')['utc'])).total_seconds(),
      'timing_excludes_final_zip_and_upload':True,
      'git_before_after_unchanged':True,'git_status':get('GIT_AFTER.json')['status'],
      'training_runs_in_recorded_execution':0,'model_forward_in_recorded_execution':0,
      'this_review_simulation_runs':0,'this_review_mcts_calls':0,'this_review_training_runs':0,'this_review_remote_connections':0,
      'review_scope':'All supplied recorded state/RNG/action/reward/commit chains and dataset aggregate arithmetic; no re-simulation, no independent physical-road or continuous geometry certification. Live cloud state not queried.',
      'inherited_from_execution_result':{'parents_unchanged_after':result['parents_unchanged_after'],'runtime_unchanged_after':result['runtime_unchanged_after'],'postcheck_status':result['postcheck_status']},
      'errors':errors,'review_elapsed_seconds':time.monotonic()-t0,
    }
    (HERE/'CELL_REVIEW.json').write_text(json.dumps(checked,ensure_ascii=False,indent=2)+'\n')
    (HERE/'REVIEW.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(review,ensure_ascii=False,indent=2))
