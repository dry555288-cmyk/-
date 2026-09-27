#!/usr/bin/env python3
"""Fixed-code balanced timing only; no candidate changes, collection, training or deployment."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path, PurePosixPath
import platform
import shutil
import signal
import stat
import subprocess
import sys
import time
import traceback
import zipfile
from datetime import datetime, timezone

NAME='minesim_dual_cachetiming_v1'
PARENT='minesim_dual_reportcache_flat_v1'
DATA=Path('/root/autodl-tmp')
REPO=Path('/root/MineSim-Dynamic')

def check(ok,text):
    if not ok:raise RuntimeError(text)

def canon(x):return (json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()
def sha(b):return hashlib.sha256(b).hexdigest()
def utc():return datetime.now(timezone.utc).isoformat()

def parse(b):
    def pairs(xs):
        out={}
        for k,v in xs:check(k not in out,'DUPLICATE_JSON_KEY:'+k);out[k]=v
        return out
    def bad(x):raise ValueError('NONFINITE_JSON:'+x)
    return json.loads(b,object_pairs_hook=pairs,parse_constant=bad)

def safe_rel(s):
    p=PurePosixPath(s)
    check(bool(s) and not p.is_absolute() and '..' not in p.parts and '\\' not in s and str(p)==s,'UNSAFE_PATH:'+s)
    return p

def no_symlink(p):
    for q in [p]+list(p.parents):check(not q.is_symlink(),'SYMLINK_REFUSED:'+str(q))

def read_stable(p):
    p=Path(p);no_symlink(p)
    with p.open('rb') as f:
        a=os.fstat(f.fileno());check(stat.S_ISREG(a.st_mode),'NOT_REGULAR:'+str(p));b=f.read();c=os.fstat(f.fileno())
    d=p.stat();sig=lambda x:(x.st_dev,x.st_ino,x.st_size,x.st_mtime_ns,x.st_ctime_ns)
    check(sig(a)==sig(c)==sig(d) and len(b)==a.st_size,'SOURCE_CHANGED_DURING_READ:'+str(p))
    return b

def put(p,x,raw=False):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb') as f:f.write(x if raw else canon(x));f.flush();os.fsync(f.fileno())

def git_state(repo):
    def call(args):
        env=dict(os.environ,GIT_OPTIONAL_LOCKS='0')
        return subprocess.run(['git','-C',str(repo)]+args,check=True,capture_output=True,timeout=20,env=env).stdout
    return {'head':call(['rev-parse','HEAD']).decode().strip(),
            'status':call(['status','--porcelain=v1','--untracked-files=normal']).decode(),
            'unstaged_diff_sha256':sha(call(['diff','--no-ext-diff','--binary'])),
            'staged_diff_sha256':sha(call(['diff','--cached','--no-ext-diff','--binary']))}

def related(argv):
    if not argv:return False
    exe=Path(argv[0]).name
    if not (exe.startswith('python') or exe in ('bash','sh','screen')):return False
    prefixes=('run_dual_cachetiming','minesim_dual_cachetiming','run_dual_reportcache','minesim_dual_reportcache','run_dual32_','run_dual_tree','minesim_dual32_','minesim_dual_tree',
              'run_grouped_coverage32','minesim_grouped_coverage32','minesim_dual_stop',
              'minesim_c11_original_start','minesim_window16','run_window16')
    # Match executable script arguments, not e.g. tail/grep arguments containing a log filename.
    return any(any(part.startswith(prefixes) for part in Path(a).parts) and Path(a).suffix in ('.py','.sh') for a in argv[1:])

def proc(pid):
    p=Path('/proc')/str(pid)
    a=(p/'stat').read_text(); fields=a[a.rfind(')')+2:].split()
    cmd=(p/'cmdline').read_bytes().split(b'\0');argv=[x.decode(errors='replace') for x in cmd if x]
    b=(p/'stat').read_text();fs=b[b.rfind(')')+2:].split()
    check(fields[19]==fs[19] and fields[1]==fs[1],'PID_CHANGED_DURING_READ')
    return {'pid':pid,'ppid':int(fields[1]),'start_ticks':fields[19],'state':fields[0],'argv':argv}

def processes():
    ancestors=[];ex=set();p=os.getpid()
    while p>0 and p not in ex:
        r=proc(p);ancestors.append(r);ex.add(p);p=r['ppid']
    matches=[];unreadable=[]
    for path in Path('/proc').iterdir():
        if not path.name.isdigit() or int(path.name) in ex:continue
        try:r=proc(int(path.name))
        except FileNotFoundError:
            if path.exists():unreadable.append(path.name)
            continue
        except (OSError,RuntimeError,ValueError,IndexError) as e:
            unreadable.append({'pid':path.name,'error':str(e)});continue
        if related(r['argv']):matches.append(r)
    return {'scope':'Current PID namespace; executable-related scripts only; self and exact ancestors excluded',
            'matches':matches,'unreadable':unreadable,'ancestors':ancestors}

def resources(data):
    def txt(p):
        try:return Path(p).read_text().strip()
        except OSError:return None
    aff=len(os.sched_getaffinity(0));cpu=float(aff)
    cm=txt('/sys/fs/cgroup/cpu.max')
    q=txt('/sys/fs/cgroup/cpu/cpu.cfs_quota_us');period=txt('/sys/fs/cgroup/cpu/cpu.cfs_period_us')
    if cm and cm.split()[0]!='max':cpu=min(cpu,float(cm.split()[0])/float(cm.split()[1]))
    elif q and period and int(q)>0:cpu=min(cpu,int(q)/int(period))
    info=dict((k,v.strip()) for k,v in (s.split(':',1) for s in Path('/proc/meminfo').read_text().splitlines()))
    avail=int(info['MemAvailable'].split()[0])*1024
    ml=txt('/sys/fs/cgroup/memory.max') or txt('/sys/fs/cgroup/memory/memory.limit_in_bytes')
    mu=txt('/sys/fs/cgroup/memory.current') or txt('/sys/fs/cgroup/memory/memory.usage_in_bytes')
    if ml and mu and ml!='max':avail=min(avail,max(0,int(ml)-int(mu)))
    return {'resource':'HIGH-CPU','effective_cpu':cpu,'affinity':aff,'memory_available_bytes':avail,
            'free_disk_bytes':shutil.disk_usage(data).free,'gpu_needed':False,'cpu_max_raw':cm}

def claim(data):
    targets=[data/NAME,data/(NAME+'.lease.json'),data/(NAME+'.zip'),data/(NAME+'.zip.pending')]
    for p in targets:
        no_symlink(p);check(not os.path.lexists(p),'EXISTING_NAMESPACE_NO_RETRY:'+str(p))
    put(targets[1],{'claimed_utc':utc(),'pid':os.getpid(),'technical_only':True,'max_search_calls':40,
                    'collection':False,'training':False,'retry_authorized':False})
    targets[0].mkdir()
    return targets[0]

def source_contents(data,bindings):
    """Read ONE known parent. No recursive disk scan and no synthetic replacement input."""
    contents={};locations={};archive=None;archive_raw=None
    try:
        for rel,b in bindings['members'].items():
            safe_rel(rel);path=data/PARENT/rel
            if os.path.lexists(path):
                raw=read_stable(path);loc={'kind':'known_directory','path':str(path)}
            else:
                if archive is None:
                    zp=data/(PARENT+'.zip');archive_raw=read_stable(zp)
                    archive=zipfile.ZipFile(io.BytesIO(archive_raw));names=archive.namelist()
                    check(len(names)==len(set(names)),'DUPLICATE_ARCHIVE_MEMBERS')
                opts=[n for n in (PARENT+'/'+rel,rel) if n in archive.namelist()]
                check(len(opts)==1,'MISSING_OR_AMBIGUOUS_PARENT_MEMBER:'+rel)
                raw=archive.read(opts[0]);loc={'kind':'known_parent_zip','path':str(data/(PARENT+'.zip')),
                    'member':opts[0],'archive_sha256':sha(archive_raw)}
            check(len(raw)==b['size'] and sha(raw)==b['sha256'],'PARENT_SHA_OR_SIZE:'+rel)
            contents[rel]=raw;locations[rel]=loc
        manifest=parse(contents['MANIFEST.json'])
        for rel,b in bindings['members'].items():
            if rel!='MANIFEST.json':check(manifest.get(rel)==b,'PARENT_MANIFEST_BINDING:'+rel)
        result=parse(contents['RESULT.json'])
        check(contents['RC.txt']==b'0\n' and result['rc']==0 and result['status']=='PASS_DUAL_FLAT_REPORT_CACHE_EQUIVALENCE_SMOKE','PARENT_STATUS')
        return contents,locations
    finally:
        if archive is not None:archive.close()

def verify_release(release):
    m=parse(read_stable(release/'RELEASE_MANIFEST.json'))
    for n,b in m.items():
        safe_rel(n);raw=read_stable(release/n)
        check(len(raw)==b['size'] and sha(raw)==b['sha256'],'RELEASE_DRIFT:'+n)
    return m

def bundle(out):
    manifest={}
    for p in sorted(out.rglob('*')):
        no_symlink(p)
        if p.is_file():b=read_stable(p);manifest[p.relative_to(out).as_posix()]={'size':len(b),'sha256':sha(b)}
    put(out/'MANIFEST.json',manifest)
    pending=out.parent/(NAME+'.zip.pending');final=out.parent/(NAME+'.zip')
    check(not os.path.lexists(pending) and not os.path.lexists(final),'ZIP_ALREADY_EXISTS')
    with pending.open('xb') as f:
        with zipfile.ZipFile(f,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
            for p in sorted(out.rglob('*')):
                if p.is_file():z.write(p,out.name+'/'+p.relative_to(out).as_posix())
        f.flush();os.fsync(f.fileno())
    with zipfile.ZipFile(pending) as z:
        check(len(z.namelist())==len(manifest)+1,'BUNDLE_MEMBER_COUNT')
        for n,b in manifest.items():
            raw=z.read(out.name+'/'+n);check(len(raw)==b['size'] and sha(raw)==b['sha256'],'BUNDLE_VERIFY:'+n)
        check(parse(z.read(out.name+'/MANIFEST.json'))==manifest,'BUNDLE_MANIFEST')
    # Only our own, just-verified pending file is removed, never an old result/protection file.
    os.link(pending,final);pending.unlink()
    return final,len(manifest)

def execute(release,data=DATA,repo=REPO,*,local_test=False,observer=None):
    out=None;state={'status':'HOLD_PRESTART','technical_start':False,'mcts_calls_started':0,
        'mcts_calls_completed':0,'new_teacher_traces':0,'training_runs':0,'model_forward_calls':0,
        'tree_reuse_executed':False,'deterministic_cache_authorized':True,'collection_authorized':False,'training_authorized':False,
        'retry_authorized':False,'resource':'HIGH-CPU','local_test':local_test,'errors':[]}
    g0=None;src=None;locations=None;rc=2;stage='CLAIM'
    try:
        out=claim(data)
        put(out/'REQUEST.json',{'time':utc(),'scope':'Fixed-code warmup8 plus balanced measured32 searches, max40; no teacher samples or Q/visits reuse',
                              'authorization':'--authorize-cachetiming-once','collection':False,'training':False})
        stage='RELEASE';rm=verify_release(release)
        for n in list(rm)+['RELEASE_MANIFEST.json']:put(out/'release'/n,read_stable(release/n),raw=True)
        bindings=parse(read_stable(release/'SOURCE_BINDINGS.json'));protocol=parse(read_stable(release/'PROTOCOL.json'))
        stage='ENVIRONMENT'
        put(out/'ENVIRONMENT.json',{'python':sys.version,'executable':sys.executable,'conda':os.environ.get('CONDA_DEFAULT_ENV'),
            'cwd':str(Path.cwd()),'gpu_visible':os.environ.get('CUDA_VISIBLE_DEVICES'),'local_test':local_test})
        if not local_test:
            check(Path.cwd().resolve()==repo.resolve() and os.environ.get('CONDA_DEFAULT_ENV')=='minesim','WRONG_REPO_OR_ENV')
            check(os.environ.get('CUDA_VISIBLE_DEVICES')=='','GPU_MUST_BE_UNUSED')
        res=(observer['resources'](data) if observer else resources(data));put(out/'RESOURCES.json',res)
        check(res['effective_cpu']>=2 and res['memory_available_bytes']>=2*1024**3 and res['free_disk_bytes']>=1024**3,'TIMING_RESOURCE_PREFLIGHT')
        g0=observer['git'](repo) if observer else git_state(repo);put(out/'GIT_BEFORE.json',g0)
        p0=observer['processes']() if observer else processes();put(out/'PROCESSES_BEFORE.json',p0)
        check(not p0['matches'] and not p0['unreadable'],'RELATED_PROCESS_OR_VISIBILITY_HOLD')
        stage='INPUT_BINDING';src,locations=source_contents(data,bindings);put(out/'SOURCE_PROVENANCE.json',locations)
        for rel,raw in src.items():put(out/'parent_sources'/rel,raw,raw=True)
        state['sources_verified']=len(src)
        check(read_stable(out/'release/action_cache.py')==src['release/action_cache.py'],'CANDIDATE_MUST_BE_UNCHANGED')
        check(read_stable(out/'release/parent_probe.py')==src['release/experiment.py'],'SEARCH_HARNESS_MUST_BE_UNCHANGED')
        check(verify_release(out/'release')==rm,'CAPTURED_RELEASE_DRIFT')
        spec=importlib.util.spec_from_file_location('fixedcache_timing_native',out/'release/experiment.py')
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
        stage='TECHNICAL_PROBE';put(out/'TECHNICAL_START.json',{'time':utc(),'max_mcts_calls':40,
            'teacher_sample':False,'new_Y64_returns':0,'benchmark_run':True,'fixed_fixture_timing_only':True});state['technical_start']=True
        def progress(event,counts,where):
            state['mcts_calls_started']=counts['search_started'];state['mcts_calls_completed']=counts['search_completed'];state['counters']=dict(counts)
            row={'time':utc(),'event':event,'counters':dict(counts),'where':where}
            with (out/'EVENTS.jsonl').open('ab') as f:f.write(canon(row));f.flush();os.fsync(f.fileno())
            if event=='SEARCH_AND_ONE_STEP_SAVED':print('SEARCHES_COMPLETED='+str(counts['search_completed'])+'/40',flush=True)
        result=mod.run(out/'parent_sources/parent_sources/parent_sources/parent_sources/runtime',out/'native',protocol,progress,local_test=local_test)
        state['native_result']=result;state['status']=result['status'];rc=0
    except BaseException as e:
        state['status']='HOLD_'+stage;state['errors'].append({'stage':stage,'type':type(e).__name__,'message':str(e)})
        if out is not None:put(out/'ERROR.txt',traceback.format_exc().encode(),raw=True)
        else:print('HOLD='+str(e),flush=True)
    finally:
        if out is not None:
            post_errors=[]
            if g0 is not None:
                try:
                    g1=observer['git'](repo) if observer else git_state(repo);put(out/'GIT_AFTER.json',g1)
                    check(g1==g0,'GIT_CHANGED');state['git_unchanged']=True
                except BaseException as e:post_errors.append(str(e))
            if src is not None:
                try:
                    check(verify_release(release)==rm and verify_release(out/'release')==rm,'RELEASE_CHANGED_AFTER')
                    again,loc2=source_contents(data,bindings);check(again==src and loc2==locations,'SOURCE_CHANGED_AFTER')
                    state['bound_sources_unchanged']=True
                except BaseException as e:post_errors.append(str(e))
            try:
                ps=observer['processes']() if observer else processes();put(out/'PROCESSES_AFTER.json',ps)
                check(not ps['matches'] and not ps['unreadable'],'POST_RELATED_PROCESS_HOLD')
            except BaseException as e:post_errors.append(str(e))
            if post_errors:
                state['pre_postcheck_status']=state['status'];state['status']='HOLD_POSTCHECK';rc=2
                state['errors'].append({'stage':'POSTCHECK','messages':post_errors})
            state['postcheck']='PASS' if not post_errors else 'HOLD';state['rc']=rc;state['finished_utc']=utc()
            put(out/'RESULT.json',state);put(out/'RC.txt',(str(rc)+'\n').encode(),raw=True)
            put(out/'CAPTURE.json',{'finished_utc':utc(),'status':state['status'],'rc':rc})
            print('STATUS='+state['status'],flush=True)
            print('MCTS_CALLS='+str(state['mcts_calls_completed'])+'/40; NEW_TEACHER_TRACES=0; TRAINING_RUNS=0; TREE_REUSE_EXECUTED=False',flush=True)
            try:
                zp,n=bundle(out);print('BUNDLE='+str(zp),flush=True);print('ZIP_VERIFIED=True; MANIFEST_ITEMS='+str(n),flush=True)
            except BaseException:
                print('BUNDLE_HOLD_KEEP_DIRECTORY_AND_PENDING\n'+traceback.format_exc(),flush=True);rc=2
    return rc

def main():
    p=argparse.ArgumentParser();p.add_argument('--authorize-cachetiming-once',action='store_true',required=True);p.parse_args()
    return execute(Path(__file__).resolve().parent)
if __name__=='__main__':sys.exit(main())
