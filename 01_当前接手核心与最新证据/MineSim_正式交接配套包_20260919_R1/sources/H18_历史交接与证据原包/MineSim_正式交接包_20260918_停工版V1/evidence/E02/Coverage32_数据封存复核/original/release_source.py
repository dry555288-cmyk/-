"""One-shot Coverage32 new16 x two actions x eight repeats, no fitting or retry.
Reads only two pinned parent ZIPs. Executes 4 to 16 owned workers selected before START, then
verifies saved cells, builds a512-observation development dataset, and seals files.
"""
from __future__ import annotations
import argparse,hashlib,importlib.util,io,json,math,os,signal,subprocess,sys,time,traceback,zipfile
from collections import Counter
from contextlib import contextmanager
from datetime import datetime,timezone
from pathlib import Path,PurePosixPath
HOME=Path(__file__).resolve().parent
NS='minesim_grouped_coverage32_collect256_v1'
GATE='COVERAGE32_NEW16_FIXED_WINDOW64_COLLECT256_ONCE'
PASS='COMPLETE_COVERAGE32_NEW256_VERIFIED_NOT_MODEL_SUCCESS'
DATA=Path('/root/autodl-tmp'); REPO=Path('/root/MineSim-Dynamic')
ORDER=[f'{i},{j}' for i in range(4) for j in range(4)]
EXECUTION_REVISION='PARALLEL_SCHEDULING_MAX16_V1'
def need(x,s):
    if not x:raise RuntimeError(s)
def canon(x):return (json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()
def sha(b):return hashlib.sha256(b).hexdigest()
def utc():return datetime.now(timezone.utc).isoformat()
def read(p):
    def pairs(xs):
        d={}
        for k,v in xs:need(k not in d,'DUPLICATE_JSON_KEY:'+k);d[k]=v
        return d
    def bad(x):raise ValueError('NONFINITE_JSON:'+x)
    return json.loads(Path(p).read_bytes(),object_pairs_hook=pairs,parse_constant=bad)
def no_links(p):
    for q in [Path(p)]+list(Path(p).parents):need(not q.is_symlink(),'SYMLINK_REFUSED:'+str(q))
def write(p,x,raw=False):
    p=Path(p);no_links(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb') as f:f.write(x if raw else canon(x));f.flush();os.fsync(f.fileno())
def refresh(p,x):
    # Only progress files owned by this execution may be replaced.
    p=Path(p);no_links(p);tmp=Path(str(p)+'.tmp');no_links(tmp)
    with tmp.open('wb') as f:f.write(canon(x));f.flush();os.fsync(f.fileno())
    os.replace(tmp,p)
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def safe(n):
    p=PurePosixPath(n);need(n and str(p)==n and not p.is_absolute() and '..' not in p.parts and '\\' not in n,'UNSAFE_ARCHIVE_MEMBER')
def archive(raw,root='',manifest_name='MANIFEST.json'):
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        names=z.namelist();need(len(names)==len(set(names)) and len(names)<=2000,'PARENT_MEMBER_COUNT')
        need(sum(i.file_size for i in z.infolist())<128*1024**2,'PARENT_SIZE')
        for n in names:safe(n)
        m=json.loads(z.read(root+manifest_name));need(set(names)=={root+n for n in m}|{root+manifest_name},'PARENT_MEMBER_SET')
        d={n[len(root):]:z.read(n) for n in names}
        for n,r in m.items():need(len(d[n])==r['size'] and sha(d[n])==r['sha256'],'PARENT_CONTENT:'+n)
        return d,m

def verify_tree(path,manifest_name='RUNTIME_MANIFEST.json'):
    m=read(path/manifest_name)
    actual={p.relative_to(path).as_posix() for p in path.rglob('*') if p.is_file()}
    need(actual==set(m)|{manifest_name},'RUNTIME_FILESET')
    for n,r in m.items():
        safe(n);p=path/n;no_links(p);b=p.read_bytes();need(len(b)==r['size'] and sha(b)==r['sha256'],'RUNTIME_SHA:'+n)
    return m

def validate_inputs(runtime):
    from coverage32_spec import make_spec,wrapper
    roots=read(runtime/'inputs/SELECTED_NEW16.json'); tasks=read(runtime/'inputs/FUTURE_256_TASKS_NOT_AUTHORIZED.json')
    p=read(runtime/'COLLECTION_PROTOCOL.json'); old=read(runtime/'inputs/OLD_DATASET16.json');combined=read(runtime/'inputs/COMBINED32_INPUTS.json')
    for file,field in [('SELECTED_NEW16.json','new_roots_sha256'),('FUTURE_256_TASKS_NOT_AUTHORIZED.json','schedule_sha256'),('FUTURE_TEACHER_PROTOCOL.json','future_protocol_sha256'),('OLD_DATASET16.json','old_dataset_sha256'),('COMBINED32_INPUTS.json','combined32_inputs_sha256')]:
        need(sha((runtime/'inputs'/file).read_bytes())==p[field],'FROZEN_INPUT:'+file)
    validator=load(runtime/'coverage32_smoke_validator.py','frozen_schedule_only')
    validator.validate_schedule(roots,tasks,read(runtime/'SMOKE_PROTOCOL.json'))
    need(len(combined)==32 and len(old['rows'])==16 and old['observations']==256,'OLD_COMBINED_SIZE')
    need(Counter(r['task']['task_id'] for r in combined)=={f'policy_{i:02d}':4 for i in range(8)},'GROUP_BALANCE')
    need(len({r['root_id'] for r in combined})==32,'COMBINED_ROOT_ID')
    idx={r['root_id']:r for r in combined}; oldids={r['root_id'] for r in old['rows']}
    need(not oldids&{r['root_id'] for r in roots},'OLD_ROOT_RECOLLECTION')
    for r in roots:need(idx[r['root_id']]['state']==r['state'],'COMBINED_NEW_IDENTITY')
    for r in old['rows']:need(idx[r['root_id']]['state']==r['full_state'] and idx[r['root_id']]['task']['task_id']==r['source_run'],'COMBINED_OLD_IDENTITY')
    oldseeds={q['rng_seed'] for r in old['rows'] for q in r['records']}
    need(not oldseeds&{t['rng_seed'] for t in tasks},'OLD_SEED_COLLISION')
    byid={r['root_id']:r for r in roots};specs=[make_spec(byid[t['root_id']],t) for t in tasks]
    return roots,byid,tasks,specs,p,old,combined

def choose_layout(resources, original):
    """Select once, before START. Never hot-resize an already consumed batch.
    Limits use the inherited cgroup/affinity resource snapshot, not host nproc.
    The four-worker fallback retains the original 8 GiB admission threshold;
    faster layouts reserve 2 GiB per worker plus 2 GiB for parent/audit overhead.
    """
    cpu=resources['effective_cpu']; mem=resources['available_memory_bytes']
    need(type(cpu) in (int,float) and math.isfinite(cpu) and cpu>=4,'PARALLEL_CPU_RESOURCE')
    need(type(mem) is int and mem>=8*1024**3,'PARALLEL_MEMORY_RESOURCE')
    for n in range(16,3,-1):
        minmem=(8 if n==4 else 2*n+2)*1024**3
        if cpu>=n and mem>=minmem:
            return {'revision':EXECUTION_REVISION,'workers':n,
                    'cells_by_worker':[len(range(w,256,n)) for w in range(n)],
                    'minimum_effective_cpu':float(n),'minimum_available_memory_bytes':minmem,
                    'sharding':'immutable task ordinal modulo%d; independent per-cell frozen RNG; no shared RNG'%n,
                    'frozen_original_protocol_sha256':sha(canon(original)),
                    'selected_before_scientific_START':True,
                    'hot_resize':False,'automatic_retry':False,
                    'same_batch_namespace_as_original':NS,
                    'new_teacher_traces_still':256,'mcts_numeric_code_changed':False,
                    'per_step_checks_and_saved_record_audit_changed':False,
                    'observed_resources':resources}
    raise RuntimeError('NO_ALLOWED_PARALLEL_LAYOUT')

def effective_protocol(original, layout):
    need(layout['revision']==EXECUTION_REVISION and layout['workers'] in range(4,17),'PARALLEL_LAYOUT_ID')
    need(layout['frozen_original_protocol_sha256']==sha(canon(original)),'ORIGINAL_PROTOCOL_ID')
    n=layout['workers']; counts=[len(range(w,256,n)) for w in range(n)]
    need(layout['cells_by_worker']==counts,'PARALLEL_SHARD_COUNTS')
    p=dict(original)
    p.update(workers=n,cells_per_worker=counts,sharding=layout['sharding'],
             minimum_effective_cpu=layout['minimum_effective_cpu'],
             minimum_available_memory_bytes=layout['minimum_available_memory_bytes'])
    p['execution_amendment']={
        'revision':EXECUTION_REVISION,
        'original_protocol_sha256':layout['frozen_original_protocol_sha256'],
        'overridden_execution_fields':['workers','cells_per_worker','sharding','minimum_effective_cpu','minimum_available_memory_bytes'],
        'no_change_to_tasks_roots_seeds_targets_or_numerics':True,
        'explicit_parallel_layout_authorization':True}
    return p

def shard_specs(schedule, n, worker_id):
    need(type(n) is int and n in range(4,17),'WORKER_COUNT')
    need(type(worker_id) is int and worker_id in range(n),'WORKER_ID')
    need(len(schedule)==256 and [x['ordinal'] for x in schedule]==list(range(256)),'SCHEDULE_ORDINALS')
    mine=[x for x in schedule if x['ordinal']%n==worker_id]
    need(len(mine)==len(range(worker_id,256,n)),'SHARD_COUNT')
    return mine

def worker(out,worker_id):
    runtime=out/'runtime'; sys.path.insert(0,str(runtime));sys.dont_write_bytecode=True
    import coverage32_cell_core as core
    import coverage32_spec as specs
    import realroute_smoke as native
    import feature_projection as fp
    import teacher_runner_smoke as original_checks
    p=read(runtime/'COLLECTION_PROTOCOL.json');nworkers=p['workers'];need(nworkers in range(4,17) and worker_id in range(nworkers),'WORKER_ID');planned=len(range(worker_id,256,nworkers))
    wd=out/'workers'/f'worker_{worker_id}';need(not os.path.lexists(wd),'WORKER_EXISTS_NO_RETRY');wd.mkdir(parents=True)
    counts={k:0 for k in ['search_started','search_returned','outer_transitions_attempted','outer_transitions_returned','collection_cells_committed','candidate_fleet_calls_including_tree_attempted','candidate_fleet_calls_including_tree_returned']}
    summaries=[];current=None;rc=2;stage='PREPARE_NO_SCIENCE';beg=time.monotonic()
    def prog(**extra):refresh(wd/'PROGRESS.json',{'utc':utc(),'worker_id':worker_id,'stage':stage,'committed':len(summaries),'planned':planned,'current_cell':current,'counts':counts,'elapsed_s':time.monotonic()-beg,**extra})
    def interrupted(sig,frame):raise KeyboardInterrupt('OWNED_WORKER_SIGNAL_'+str(sig))
    signal.signal(signal.SIGTERM,interrupted)
    @contextmanager
    def bounded(seconds):
        need(not (out/'STOP_REQUESTED.json').exists(),'SUPERVISOR_STOP_NO_RESUME')
        with native.bounded_call(seconds):yield
    try:
        need(os.environ.get('MINESIM_COV32_SCOPE')==GATE,'WORKER_SCOPE')
        verify_tree(runtime);roots,byid,tasks,schedule,p,old,combined=validate_inputs(runtime)
        imported=native.activate_package(runtime);original_checks.verify_versions(imported,read(runtime/'EXPECTED_IMPORT.json'));write(wd/'IMPORT_RESULT.json',imported)
        from candidate_mcts.dual_stop_adapter_v1 import action_id
        contexts={}
        for r in roots:
            ep=r['task']['episode_uid']
            if ep not in contexts:
                cb=(runtime/'inputs/contexts'/(ep+'.json')).read_bytes();need(sha(cb)==r['task']['context_sha256'],'CONTEXT_SHA')
                with bounded(60):contexts[ep]=native.BoundContext(runtime,json.loads(cb),counters=counts)
                write(wd/'contexts'/(ep+'.json'),contexts[ep].resolved)
            bc=contexts[ep];clean=lambda d:{k:v for k,v in d.items() if k!='setup_elapsed_ms'}
            need(clean(bc.resolved)==clean(read(runtime/'inputs/resolved'/(r['task']['task_id']+'.json'))),'RESOLVED_CONTEXT')
            st=bc.transition.unpack(r['state']);need(canon(bc.transition.pack(st))==canon(r['state']),'RESTORE_IDENTITY')
            need([action_id(a) for a in bc.transition.active_joint_actions(st)]==ORDER and fp.checked_mask(r)==[True]*16,'INITIAL_DOMAIN')
            need(fp.feature26(r['state'])['float32']==r['feature26_float32'],'INITIAL_FEATURE')
        mine=shard_specs(schedule,nworkers,worker_id);need(len(mine)==planned,'SHARD_COUNT');write(wd/'SHARD_SCHEDULE.json',mine)
        write(wd/'READY.json',{'worker_id':worker_id,'pid':os.getpid(),'utc':utc(),'input_verified':True,'runtime_sha256':sha((runtime/'RUNTIME_MANIFEST.json').read_bytes()),'mcts_calls':0,'state_transitions':0})
        prog()
        while not (out/'START.json').exists():
            need(not (out/'STOP_REQUESTED.json').exists(),'STOP_BEFORE_START');need(time.monotonic()-beg<=p['prepare_worker_wall_limit_seconds']+30,'WAIT_START_TIMEOUT');time.sleep(.2)
        start=read(out/'START.json');lease=read(out.parent/(out.name+'.lease.json'))
        need(start['authorization_sha256']==sha(canon(lease)) and lease['permission']==GATE and start['explicit_user_authorization'] is True,'START_LEASE_AUTHORIZATION')
        need(start['schedule_sha256']==p['schedule_sha256'] and start['runtime_manifest_sha256']==sha((runtime/'RUNTIME_MANIFEST.json').read_bytes()),'START_FROZEN_INPUT')
        need(start['training_authorized'] is False and start['planned_new_traces']==256,'START_SCOPE')
        for s in mine:
            need(not (out/'STOP_REQUESTED.json').exists(),'STOP_BEFORE_NEXT_CELL');current=s['cell_id'];r=byid[s['pilot_root_id']];bc=contexts[r['task']['episode_uid']]
            stage='RUNNING';prog();t=time.monotonic();step=[0]
            def validator(*args):
                native.verify_step(*args);step[0]+=1
                if step[0]%5==0:prog(current_outer_step=step[0])
            summary=core.run_cell(bc,specs.wrapper(r),s,out/'cells'/current,counts,validator,bounded)
            record={'ordinal':s['ordinal'],'cell_id':current,'worker_id':worker_id,'root_id':s['pilot_root_id'],'block':s['block'],'action_id':s['first_action_id'],'replicate_id':s['replicate_id'],'outcome':summary['outcome'],'steps':summary['executed_steps'],'search_calls':summary['native_search_calls'],'elapsed_seconds':time.monotonic()-t,'commit_sha256':sha((out/'cells'/current/'COMMIT.json').read_bytes())}
            summaries.append(record)
            with (wd/'CELLS.jsonl').open('ab') as f:f.write(canon(record));f.flush();os.fsync(f.fileno())
            stage='CELL_COMMITTED';prog();print('WORKER=%d COMMITTED=%d/%d CELL=%s'%(worker_id,len(summaries),planned,current),flush=True)
        need(len(summaries)==counts['collection_cells_committed']==planned,'WORKER_COMPLETION')
        for a,b in [('search_started','search_returned'),('outer_transitions_attempted','outer_transitions_returned'),('candidate_fleet_calls_including_tree_attempted','candidate_fleet_calls_including_tree_returned')]:need(counts[a]==counts[b],'WORKER_COUNTER_MISMATCH:'+a)
        stage='COMPLETE';rc=0
    except BaseException as e:
        write(wd/'ERROR.json',{'stage':stage,'error':str(e),'type':type(e).__name__,'traceback':traceback.format_exc(),'current_cell':current,'counts':dict(counts),'automatic_retry':False})
    finally:
        write(wd/'RESULT.json',{'rc':rc,'stage':stage,'counts':counts,'committed_cells':summaries,'training_runs':0,'automatic_retry':False,'elapsed_seconds':time.monotonic()-beg})
        write(wd/'RC.txt',(str(rc)+'\n').encode(),True);stage='FINISHED';prog(rc=rc)
    return rc

def assemble(runtime,out):
    sys.path.insert(0,str(runtime))
    import coverage32_cell_core as core
    import feature_projection as fp
    roots,byid,tasks,specs,p,old,combined=validate_inputs(runtime)
    records=[];bad=[];notstarted=[]
    for s in specs:
        td=out/'cells'/s['cell_id']
        if not td.exists():notstarted.append(s['cell_id']);continue
        try:
            v=core.verify_cell(td,s)
            # No new simulation: reread hash/RNG/state chains and independent scalar reward arithmetic.
            config=read(runtime/'inputs/contexts'/(byid[s['pilot_root_id']]['task']['episode_uid']+'.json'))
            class C:context=config
            for path in sorted((td/'steps').glob('*.json')):
                row=core.read(path);core.reward_check(C,row['before'],row['after'],row['reward'])
            records.append({'ordinal':s['ordinal'],'root_id':s['pilot_root_id'],'source_run':s['source_run'],'cell_id':s['cell_id'],'action_id':s['first_action_id'],'block':s['block'],'replicate_id':s['replicate_id'],'rng_seed':s['rng_seed'],'root_state_sha256':s['root_state_sha256'],'executed_steps':v['executed_steps'],'maximum_outer_steps':128,'task_outcome':v['outcome'],'native_search_calls':v['native_search_calls'],'window_return':v['finite_window_return'],'window_target_observed':True,'old_full_task_return':v['full_task_return'],'old_full_task_tail_censored':v['tail_censored'],'target_id':p['target_id'],'phase':'coverage32_new16_development','training_mask':0,'pruning_authorized':False,'source_path':str(td.relative_to(out)),'commit_sha256':sha((td/'COMMIT.json').read_bytes())})
        except Exception as e:bad.append({'cell_id':s['cell_id'],'error':str(e)})
    expected={s['cell_id'] for s in specs};unexpected=sorted(x.name for x in (out/'cells').iterdir() if x.name not in expected) if (out/'cells').exists() else []
    complete=len(records)==256 and not bad and not notstarted and not unexpected
    audit={'status':'PASS_256_SAVED_CELLS' if complete else 'HOLD_PARTIAL_SAVED_CELLS','planned':256,'verified':len(records),'touched_unverified':bad,'unstarted':notstarted,'unexpected':unexpected,'outer_steps':sum(r['executed_steps'] for r in records),'mcts_calls_in_committed_cells':sum(r['native_search_calls'] for r in records),'outcomes':dict(Counter(r['task_outcome'] for r in records)),'no_simulation_during_audit':True,'rows':records}
    write(out/'COLLECTION_AUDIT.json',audit)
    if not complete:return audit
    def avg(x):return math.fsum(x)/len(x)
    def sd(x):return math.sqrt(math.fsum((a-avg(x))**2 for a in x)/(len(x)-1))
    newrows=[];relations=[]
    for root in roots:
        qs=[q for q in records if q['root_id']==root['root_id']];need(len(qs)==16,'RECORDS_PER_ROOT')
        blocks={b:{a:[q['window_return'] for q in qs if q['block']==b and q['action_id']==a] for a in ('0,3','3,0')} for b in ('block0','block1')}
        signs=[];blockdetail=[]
        for b,ab in blocks.items():
            need(all(len(v)==4 for v in ab.values()),'BLOCK_COUNT');aa,bb=ab['0,3'],ab['3,0'];tol=1e-9*max(1.,max(map(abs,aa+bb)))
            sign=1 if min(aa)>max(bb)+tol else (-1 if min(bb)>max(aa)+tol else 0);signs.append(sign)
            blockdetail.append({'block':b,'sign':sign,'tolerance':tol,'gap_mean':avg(aa)-avg(bb),'range03':[min(aa),max(aa)],'range30':[min(bb),max(bb)]})
        sign=signs[0] if signs[0]!=0 and signs[0]==signs[1] else None
        vals={a:[q['window_return'] for q in qs if q['action_id']==a] for a in ('0,3','3,0')};means={a:avg(v) for a,v in vals.items()};f=fp.feature26(root['state'])
        newrows.append({'root_id':root['root_id'],'source_run':root['task']['task_id'],'condition':root['task']['episode_uid'],'state_sha256':root['exact_before_state_sha256'],'full_state':root['state'],'x':f['float32'],'feature_sha256':f['float32_le_sha256'],'mask16':root['active_mask_16'],'records':qs,'blocks':blocks,'mean_returns':means,'block_mean_gaps':[x['gap_mean'] for x in blockdetail],'empirical_mean_gap03_minus30':means['0,3']-means['3,0'],'return_sample_sd':{a:sd(v) for a,v in vals.items()},'repeated_order_sign':sign,'hard_label_originally_unknown':True,'original_training_mask':0,'pruning_authorized':False,'regression_target_is_empirical_estimate_not_exact_truth':True})
        relations.append({'root_id':root['root_id'],'blocks':blockdetail,'repeated_order_sign':sign,'scope':'DESCRIPTIVE_DEVELOPMENT_RELATION_NOT_SAFETY_LABEL','unknown':sign is None})
    rows=old['rows']+newrows;need(len(rows)==32 and sum(len(r['records']) for r in rows)==512,'MERGED_DATASET_COUNTS')
    need(Counter(r['source_run'] for r in rows)=={f'policy_{i:02d}':4 for i in range(8)},'MERGED_GROUP_COUNTS')
    aliases=[]
    for i,r in enumerate(rows):
        for q in rows[i+1:]:
            if r['source_run']!=q['source_run'] and (r['state_sha256']==q['state_sha256'] or r['feature_sha256']==q['feature_sha256']):aliases.append([r['root_id'],q['root_id']])
    need(not aliases,'CROSS_GROUP_EXACT_STATE_OR_FEATURE_ALIAS')
    write(out/'NEW256_OBSERVATIONS.json',{'target_id':p['target_id'],'records':records,'new_observations':256,'mcts_not_neural_controlled':True})
    write(out/'NEW16_REPEAT_DIAGNOSTIC.json',{'rules_source_sha256':p['future_protocol_sha256'],'known_count':sum(x['repeated_order_sign'] is not None for x in relations),'unknown_count':sum(x['unknown'] for x in relations),'coverage_denominator':16,'rows':relations,'old6_and_unknown10_unchanged':True})
    write(out/'DATASET32.json',{'design':'KNOWN_ROUTE_POST_OUTCOME_COVERAGE_EXPANSION_NOT_BLIND_TEST','target_id':p['target_id'],'source_runs':sorted({r['source_run'] for r in rows}),'roots':32,'observations':512,'new_simulated_samples':256,'old_observations_reused':256,'old_dataset_sha256':p['old_dataset_sha256'],'old_rows_unchanged':True,'old_known6_unknown10_unchanged':True,'cross_group_exact_aliases':aliases,'rows':rows,'training_authorized':False,'deployment_authorized':False})
    return audit

def supervise(out,runtime,support,protocol):
    nworkers=protocol['workers'];need(nworkers in range(4,17),'WORKER_COUNT')
    workers=[];records=[];begin=time.monotonic();started=False;reason=None;nextprint=0.;peak={}
    def state():
        prog=[]
        for wid in range(nworkers):
            p=out/'workers'/f'worker_{wid}'/'PROGRESS.json'
            if p.exists():
                try:prog.append(read(p))
                except (ValueError,OSError):pass
        n=sum(p['committed'] for p in prog);elapsed=time.monotonic()-begin
        remaining=elapsed/max(n,1)*(256-n) if started and n>=4 else None
        d={'phase':'COLLECTING' if started else 'PREPARING_WORKERS','completed':n,'planned':256,'elapsed_seconds':elapsed,'eta_seconds':remaining,'eta_is_estimate_not_deadline':True,'workers':prog}
        refresh(out/'PROGRESS.json',d);return d
    try:
        env=dict(os.environ,MINESIM_COV32_SCOPE=GATE,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1',CUDA_VISIBLE_DEVICES='')
        for wid in range(nworkers):
            argv=[sys.executable,'-B','-u',str(out/'release/collect256.py'),'--worker',str(wid),'--out',str(out)]
            fo=(out/f'worker_{wid}.stdout.log').open('xb');fe=(out/f'worker_{wid}.stderr.log').open('xb')
            try:p=subprocess.Popen(argv,stdout=fo,stderr=fe,env=env,start_new_session=True)
            finally:fo.close();fe.close()
            ident=support.proc_record(p.pid);workers.append((wid,p,ident));records.append({'worker':wid,'identity':ident,'argv':argv,'utc':utc()})
        write(out/'OWNED_WORKERS.json',records)
        while True:
            for wid,p,ident in workers:
                code=p.poll()
                if code is not None and (code!=0 or not started):raise RuntimeError('WORKER_EXIT:'+str(wid)+':'+str(code))
            if not started and all((out/'workers'/f'worker_{wid}'/'READY.json').exists() for wid in range(nworkers)):
                runtime_sha=sha((runtime/'RUNTIME_MANIFEST.json').read_bytes())
                for wid,p,ident in workers:
                    r=read(out/'workers'/f'worker_{wid}'/'READY.json');need(r['pid']==p.pid and r['runtime_sha256']==runtime_sha and r['mcts_calls']==0 and r['state_transitions']==0,'WORKER_READY')
                write(out/'START.json',{'gate':GATE,'utc':utc(),'explicit_user_authorization':True,'planned_new_traces':256,'one_shot_consumed':True,'authorization_sha256':sha((out.parent/(out.name+'.lease.json')).read_bytes()),'schedule_sha256':protocol['schedule_sha256'],'runtime_manifest_sha256':runtime_sha,'training_authorized':False,'old_recollection_authorized':False,'worker_count':nworkers,'execution_revision':EXECUTION_REVISION})
                started=True;print('START=NEW256_COLLECTION; WORKERS=%d; TRAINING=False'%nworkers,flush=True)
            elapsed=time.monotonic()-begin
            limit=protocol['collection_wall_limit_seconds'] if started else protocol['prepare_worker_wall_limit_seconds']
            need(elapsed<=limit,'OPERATIONAL_WALL_LIMIT')
            if all(p.poll() is not None for wid,p,ident in workers):break
            v=os.statvfs(out);need(v.f_bavail*v.f_frsize>=protocol['running_disk_reserve_bytes'],'OPERATIONAL_FREE_DISK_RESERVE')
            for wid,p,ident in workers:
                if p.poll() is not None:continue
                try:
                    ss=Path('/proc',str(p.pid),'status').read_text().splitlines();rss=[x for x in ss if x.startswith('VmRSS:')];n=int(rss[0].split()[1])*1024 if rss else 0;peak[wid]=max(peak.get(wid,0),n)
                    need(n<=protocol['owned_worker_rss_limit_bytes'],'OWNED_WORKER_RSS_LIMIT:'+str(wid))
                except FileNotFoundError:pass
            if elapsed>=nextprint:
                d=state();eta='PENDING' if d['eta_seconds'] is None else '%.1fmin'%(d['eta_seconds']/60)
                print('PROGRESS=%d/256; ELAPSED=%.1fmin; ETA=%s'%(d['completed'],elapsed/60,eta),flush=True);nextprint=elapsed+30
            time.sleep(1)
        state()
        return {'started':started,'worker_rcs':[p.returncode for w,p,i in workers],'elapsed_seconds':time.monotonic()-begin,'peak_rss_by_worker':peak,'all_workers_complete':True}
    except BaseException as e:
        reason=type(e).__name__+':'+str(e)
        if not (out/'STOP_REQUESTED.json').exists():write(out/'STOP_REQUESTED.json',{'utc':utc(),'reason':reason,'automatic_retry':False,'owned_workers_only':True})
        raise
    finally:
        events=[]
        # Stop only Popen-owned unreaped children after an execution fault or user interruption.
        for wid,p,ident in workers:
            if p.poll() is None:
                now=support.proc_record(p.pid);need(now['start_ticks']==ident['start_ticks'],'OWNED_WORKER_IDENTITY_CHANGED')
                p.terminate();events.append({'worker':wid,'pid':p.pid,'signal':'SIGTERM'})
        for wid,p,ident in workers:
            if p.poll() is None:
                try:p.wait(timeout=10)
                except subprocess.TimeoutExpired:p.kill();p.wait();events.append({'worker':wid,'pid':p.pid,'signal':'SIGKILL'})
        write(out/'SUPERVISOR_FINAL.json',{'utc':utc(),'started':started,'reason':reason,'worker_rcs':{str(w):p.returncode for w,p,i in workers},'signals':events,'elapsed_seconds':time.monotonic()-begin,'peak_rss_by_worker':peak})

def review_bundle(out,full_zip,support):
    """Small exact evidence subset, clearly not a backup of all step/RNG records."""
    rd=out.parent/(out.name+'_review');need(not os.path.lexists(rd),'REVIEW_NAMESPACE_EXISTS');rd.mkdir()
    manifest=read(out/'MANIFEST.json')
    chosen=[]
    for n in manifest:
        take=(n.count('/')==0 or n.startswith(('release/','runtime/','workers/')))
        if n.startswith('cells/') and n.endswith(('/COMMIT.json','/SUMMARY.json','/CELL_START.json','/RC.txt','/ERROR.json')):take=True
        if take:write(rd/n,(out/n).read_bytes(),True);chosen.append(n)
    write(rd/'ORIGINAL_MANIFEST.json',(out/'MANIFEST.json').read_bytes(),True)
    h=hashlib.sha256()
    with full_zip.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    write(rd/'FULL_ARCHIVE_IDENTITY.json',{'file':str(full_zip),'size':full_zip.stat().st_size,'sha256':h.hexdigest(),'included_exact_members':len(chosen),'original_manifest_items':len(manifest),'omitted':'per-step and TRACE/EVENTS detail remains in full ZIP and original data directory; review package is not full disaster backup','new_samples_created_by_packaging':0})
    return support.package(rd)[0]

def execute(payload,expected_sha):
    out=DATA/NS;lease=DATA/(NS+'.lease.json'); targets=[out,lease,DATA/(NS+'.zip'),DATA/(NS+'.zip.pending'),DATA/(NS+'_review'),DATA/(NS+'_review.zip'),DATA/(NS+'_review.zip.pending')]
    for p in targets:no_links(p);need(not os.path.lexists(p),'NAMESPACE_EXISTS_NO_RETRY:'+str(p))
    out.mkdir(exist_ok=False)
    support=None;runtime=out/'runtime';inputhash=None;parentpaths=[];stage='PREFLIGHT';audit=None;rc=2;science=False;before=None;nworkers=0
    result={'status':'HOLD_PREFLIGHT','gate':GATE,'resource':'HIGH-CPU','rc':2,'errors':[],'new_teacher_traces':0,'training_runs':0,'model_forward_calls':0,'old_returns_recollected':0,'mcts_calls':0,'scientific_start_written':False,'automatic_retry':False,'automatic_resume':False,'training_authorized':False,'deployment_authorized':False}
    try:
        write(lease,{'namespace':NS,'permission':GATE,'explicit_authorization':True,'pid':os.getpid(),'utc':utc(),'automatic_retry':False})
        write(out/'REQUEST.json',{'utc':utc(),'argv':sys.argv,'resource':'HIGH-CPU'})
        no_links(payload);raw=Path(payload).read_bytes();need(sha(raw)==expected_sha,'RELEASE_PAYLOAD_SHA');release,rm=archive(raw,manifest_name='PAYLOAD_MANIFEST.json')
        for n,b in release.items():write(out/'release'/n,b,True)
        original_protocol=read(out/'release/COLLECTION_PROTOCOL.json');protocol=original_protocol
        write(out/'release_source.py',Path(__file__).read_bytes(),True)
        need(Path.cwd()==REPO and os.environ.get('CONDA_DEFAULT_ENV')=='minesim','FORMAL_ENVIRONMENT_REQUIRED');need(os.environ.get('CUDA_VISIBLE_DEVICES')=='','GPU_MUST_BE_DISABLED')
        write(out/'ENVIRONMENT.json',{'python':sys.version,'executable':sys.executable,'cwd':str(Path.cwd()),'conda':os.environ.get('CONDA_DEFAULT_ENV'),'gpu_visible':os.environ.get('CUDA_VISIBLE_DEVICES')})
        # Reuse the process/Git/resource checks from the already passed smoke unchanged.
        info=protocol['parent_smoke'];pp=DATA/(info['name']+'.zip');no_links(pp);raw=pp.read_bytes();need(sha(raw)==info['sha256'],'PASSED_SMOKE_ZIP_SHA');parent,pm=archive(raw,info['name']+'/')
        pr=json.loads(parent['RESULT.json']);need(pr['status']=='PASS_COVERAGE32_COLLECTOR_RESTORE_PARITY_SMOKE' and pr['rc']==0 and parent['RC.txt'].strip()==b'0','SMOKE_NOT_PASS')
        need(pr['restored_new_roots']==16 and pr['recorded_one_step_parity']==16 and pr['forced_one_step_cells']==32 and pr['short_followup_cells']==4 and pr['technical_cells_committed']==36 and pr['mcts_calls']==8,'SMOKE_SCOPE')
        need(pr['new_teacher_traces']==pr['training_runs']==0 and pr['postcheck_status']=='PASS' and pr['runtime_inputs_unchanged_after'] and pr['parent_unchanged_after'] and pr['git_unchanged_after'],'SMOKE_NOT_CLEANLY_COMPLETED')
        parentpaths.append((pp,info['sha256']));write(out/'PARENT_SMOKE_RESULT.json',parent['RESULT.json'],True)
        write(out/'support.py',parent['release/support.py'],True);support=load(out/'support.py','cov32_support')
        before=support.git_snapshot(REPO);write(out/'GIT_BEFORE.json',before)
        procs=support.process_snapshot();write(out/'PROCESSES_BEFORE.json',procs);need(not procs['matches'] and not procs['unreadable_pids'],'RELATED_PROCESS_OR_VISIBILITY_HOLD')
        resources=support.resources(DATA);resources['resource']='HIGH-CPU';write(out/'RESOURCES.json',resources)
        for k,lim in [('effective_cpu','minimum_effective_cpu'),('available_memory_bytes','minimum_available_memory_bytes'),('free_disk_bytes','minimum_free_disk_bytes')]:need(resources[k]>=protocol[lim],'HIGH_CPU_RESOURCE_PRECHECK:'+k)
        layout=choose_layout(resources,original_protocol);protocol=effective_protocol(original_protocol,layout);nworkers=protocol['workers']
        write(out/'EXECUTION_LAYOUT.json',layout);write(out/'EFFECTIVE_COLLECTION_PROTOCOL.json',protocol)
        result.update(workers=nworkers,execution_revision=EXECUTION_REVISION,parallel_layout_selected_before_START=True)
        print('EXECUTION_LAYOUT=WORKERS:%d; EFFECTIVE_CPU:%s; AVAILABLE_MEMORY_GIB:%.2f; FIXED_TRACES:256'%(nworkers,resources['effective_cpu'],resources['available_memory_bytes']/1024**3),flush=True)
        if nworkers==4:print('PARALLEL_NOTE=4_WORKER_FALLBACK_NO_PROMISED_SPEEDUP',flush=True)
        binding=json.loads(parent['RUNTIME_SOURCE_BINDINGS.json'])
        for n,b in parent.items():
            if n.startswith('runtime/'):
                rel=n[8:];need(sha(b)==binding[rel],'PARENT_RUNTIME_BINDING:'+rel);write(runtime/rel,b,True)
        write(runtime/'coverage32_smoke_validator.py',parent['release/coverage32_smoke.py'],True)
        # Copy only two design/data members of the pinned static freeze, never recollect old data.
        info=protocol['parent_freeze'];pp=DATA/(info['name']+'.zip');raw=support.read_stable(pp);need(sha(raw)==info['sha256'],'STATIC_PARENT_ZIP_SHA');pd,pdm=archive(raw,info['name']+'/');parentpaths.append((pp,info['sha256']))
        for n,dest in [('release/selection/COMBINED32_INPUTS.json','COMBINED32_INPUTS.json'),('sources/minesim_window16_return_gap_recovery_v1/DATASET16.json','OLD_DATASET16.json')]:write(runtime/'inputs'/dest,pd[n],True)
        for n in ['coverage32_cell_core.py','coverage32_spec.py','FUTURE_FITTING_CONTRACT_NOT_AUTHORIZED.json']:write(runtime/n,release[n],True)
        write(runtime/'COLLECTION_PROTOCOL.json',protocol);write(runtime/'EXECUTION_LAYOUT.json',layout)
        # Static task validation does not import the simulator or call search.
        sys.path.insert(0,str(runtime));validate_inputs(runtime)
        hashes={p.relative_to(runtime).as_posix():{'size':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in sorted(runtime.rglob('*')) if p.is_file()}
        write(runtime/'RUNTIME_MANIFEST.json',hashes);inputhash=sha(canon(hashes));write(out/'PARENT_BINDINGS.json',[{'path':str(p),'sha256':h} for p,h in parentpaths])
        stage='WORKER_PREPARE_THEN_COLLECTION';summary=supervise(out,runtime,support,protocol);science=summary['started'];write(out/'COLLECTION_TIMING.json',summary)
        stage='SAVED_RECORD_AUDIT_AND_DATASET_FREEZE';print('PHASE=SAVED_RECORD_AUDIT; NO_NEW_SEARCH',flush=True);audit=assemble(runtime,out);need(audit['verified']==256 and audit['status']=='PASS_256_SAVED_CELLS','INCOMPLETE_COLLECTION')
        worker_results=[read(out/'workers'/f'worker_{i}'/'RESULT.json') for i in range(nworkers)]
        need(all(w['rc']==0 and w['counts']['collection_cells_committed']==len(range(i,256,nworkers)) for i,w in enumerate(worker_results)),'WORKER_RESULT_COUNTS')
        need(sum(w['counts']['search_started'] for w in worker_results)==audit['mcts_calls_in_committed_cells']<=32512,'SEARCH_TOTAL')
        need(sum(w['counts']['outer_transitions_returned'] for w in worker_results)==audit['outer_steps']<=32768,'OUTER_TOTAL')
        result.update(status=PASS,new_teacher_traces=256,verified_new_observations=256,old_observations_reused=256,merged_observations=512,merged_roots=32,source_run_groups=8,mcts_calls=audit['mcts_calls_in_committed_cells'],outer_steps=audit['outer_steps'],outcomes=audit['outcomes']);rc=0
    except BaseException as e:
        result['errors'].append({'stage':stage,'type':type(e).__name__,'error':str(e)});write(out/'ERROR.json',{'stage':stage,'traceback':traceback.format_exc(),'automatic_retry':False})
        if (out/'START.json').exists():
            result['status']='HOLD_RUNTIME_OR_AUDIT_TECHNICAL'
            if support is not None and (runtime/'RUNTIME_MANIFEST.json').exists() and not (out/'COLLECTION_AUDIT.json').exists():
                try:audit=assemble(runtime,out)
                except BaseException as ae:write(out/'PARTIAL_AUDIT_ERROR.json',{'error':str(ae)})
    finally:
        result['scientific_start_written']=(out/'START.json').exists()
        if audit is None and (out/'COLLECTION_AUDIT.json').exists():audit=read(out/'COLLECTION_AUDIT.json')
        if audit is not None:result.update(verified_new_observations=audit['verified'],new_teacher_traces=audit['verified'],mcts_calls_in_verified_cells=audit['mcts_calls_in_committed_cells'])
        try:
            if support is not None:
                after=support.git_snapshot(REPO);write(out/'GIT_AFTER.json',after);result['git_unchanged_after']=after==before;need(before is None or after==before,'GIT_CHANGED')
                proc=support.process_snapshot();write(out/'PROCESSES_AFTER.json',proc);need(not proc['matches'] and not proc['unreadable_pids'],'RELATED_PROCESS_OR_VISIBILITY_AFTER_HOLD')
                for p,h in parentpaths:need(sha(support.read_stable(p))==h,'PARENT_CHANGED:'+str(p))
                result['parents_unchanged_after']=True
                if inputhash is not None:need(sha(canon(verify_tree(runtime)))==inputhash,'RUNTIME_CHANGED');result['runtime_unchanged_after']=True
            result['postcheck_status']='PASS' if support is not None else 'NOT_REACHED'
        except BaseException as e:rc=2;result['status']='HOLD_POSTCHECK';result['errors'].append({'stage':'POSTCHECK','error':str(e)})
        # Include attempted counts even for a partially interrupted execution.
        cs=[]
        for i in range(nworkers):
            wp=out/'workers'/f'worker_{i}'/'RESULT.json'
            if wp.exists():cs.append(read(wp)['counts'])
        result['worker_counter_coverage']=len(cs);result['mcts_calls_recorded_started']=sum(c['search_started'] for c in cs);result['mcts_calls_recorded_returned']=sum(c['search_returned'] for c in cs)
        result['mcts_calls']=result['mcts_calls_recorded_started'];result['mcts_count_complete']=(len(cs)==nworkers or not result['scientific_start_written'])
        result['mcts_count_note']='Counter coverage must be checked for interrupted workers; partial counts are not a claim of zero work.'
        result['rc']=rc;result['finished_utc']=utc();write(out/'RESULT.json',result);write(out/'RC.txt',(str(rc)+'\n').encode(),True);write(out/'CAPTURE.json',{'utc':utc(),'rc':rc,'training_run':False,'automatic_retry':False})
        print('STATUS='+result['status'],flush=True);print('NEW_OBSERVATIONS=%s/256; TRAINING_RUNS=0; OLD_RECOLLECTED=0'%result['new_teacher_traces'],flush=True)
        if support is None:
            # Same create-only basic packing for early preflight faults; no scientific START fabricated.
            support=type('Fallback',(),{'package':staticmethod(simple_package)})
        try:
            print('PHASE=PACKAGING; DO_NOT_RESTART',flush=True)
            bundle,n=support.package(out);small=review_bundle(out,bundle,support)
            print('FULL_BUNDLE='+str(bundle),flush=True);print('BUNDLE='+str(small),flush=True);print('ZIP_VERIFIED=True; MANIFEST_ITEMS='+str(n),flush=True)
        except BaseException as e:print('PACKAGING_HOLD='+repr(e)+'; PRESERVE_OUTPUT='+str(out),flush=True);rc=2
    return rc

def simple_package(out):
    m={p.relative_to(out).as_posix():{'size':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in sorted(out.rglob('*')) if p.is_file()};write(out/'MANIFEST.json',m)
    pending=out.with_suffix('.zip.pending');final=out.with_suffix('.zip');need(not os.path.lexists(pending) and not os.path.lexists(final),'BUNDLE_EXISTS')
    with pending.open('xb') as f:
        with zipfile.ZipFile(f,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
            for p in sorted(out.rglob('*')):
                if p.is_file():z.write(p,out.name+'/'+p.relative_to(out).as_posix())
        f.flush();os.fsync(f.fileno())
    with zipfile.ZipFile(pending) as z:
        for n,r in m.items():b=z.read(out.name+'/'+n);need(len(b)==r['size'] and sha(b)==r['sha256'],'ZIP_CONTENT')
    os.link(pending,final);pending.unlink();return final,len(m)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--authorize-collect256-once',action='store_true');ap.add_argument('--authorize-parallel-layout',action='store_true');ap.add_argument('--payload');ap.add_argument('--payload-sha256');ap.add_argument('--worker',type=int);ap.add_argument('--out');a=ap.parse_args()
    if a.worker is not None:
        need(a.out is not None and not a.authorize_collect256_once,'WORKER_ARGS');return worker(Path(a.out),a.worker)
    need(a.authorize_collect256_once and a.authorize_parallel_layout and a.payload and a.payload_sha256 and not a.out,'EXPLICIT_COLLECTION_AND_PARALLEL_AUTHORIZATION_REQUIRED')
    return execute(Path(a.payload),a.payload_sha256)
if __name__=='__main__':
    try:raise SystemExit(main())
    except Exception as e:print('PRESTART_HOLD='+repr(e)+'; NO_AUTO_RETRY',flush=True);traceback.print_exc();raise SystemExit(2)
