#!/usr/bin/env python3
"""One authorized Coverage32 held-source fit/evaluation using an immutable dataset.

No simulator imports, new samples, tuning, automatic retries or deployment.
Numerical kernels are exact extracts of the frozen Window16 implementation.
All files are on the data disk; historical files and the formal repository are read only.
"""
from __future__ import annotations
import argparse, ast, collections, hashlib, io, json, math, os, shutil, signal
import stat, struct, subprocess, sys, time, traceback, types, zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

DATA = Path('/root/autodl-tmp')
REPO = Path('/root/MineSim-Dynamic')
PYTHON = Path('/root/miniconda3/envs/minesim/bin/python')
NAME = 'minesim_grouped_coverage32_fit16_v1'
RELEASE = 'minesim_grouped_coverage32_fit16_release_v1.zip'
PARENT = 'minesim_grouped_coverage32_collect256_v1'
GATE = 'COVERAGE32_FROZEN512_HELD_SOURCE_FIT16_ONCE'
COMPLETE = 'COMPLETE_COVERAGE32_FIT16_DEVELOPMENT_NOT_GENERALIZATION'
TARGET = 'DUAL_STOP_FIXED_WINDOW64_STOPPED_RETURN_V1'
MAX_FILE = 32 * 1024**2
OLD_SIGNS = {'contrast_00': 1, 'contrast_01': -1, 'contrast_04': 1,
             'contrast_05': 1, 'newroot_02': -1, 'newroot_05': 1}
THREAD_VARS = ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS',
               'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'BLIS_NUM_THREADS')

def need(ok, reason):
    if not ok:
        raise RuntimeError(reason)

def utc():
    return datetime.now(timezone.utc).isoformat()

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def canon(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(',', ':'), allow_nan=False) + '\n').encode()

def parse(raw):
    def pairs(items):
        d = {}
        for k, v in items:
            need(k not in d, 'DUPLICATE_JSON_KEY:' + k)
            d[k] = v
        return d
    def bad(v):
        raise ValueError('NONFINITE_JSON:' + v)
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=bad)

def relative(name):
    p = PurePosixPath(name)
    need(name and not p.is_absolute() and '..' not in p.parts and '\\' not in name
         and str(p) == name and name != '.', 'UNSAFE_RELATIVE_PATH')
    return name

def no_symlinks(path):
    for p in [Path(path)] + list(Path(path).parents):
        need(not p.is_symlink(), 'SYMLINK_REFUSED:' + str(p))

def metadata(path):
    s = Path(path).lstat()
    return [s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns, s.st_mode]

def read_stable(path, limit=MAX_FILE):
    path = Path(path); no_symlinks(path); before = metadata(path)
    need(stat.S_ISREG(before[-1]) and before[2] <= limit, 'SOURCE_TYPE_SIZE:' + str(path))
    fd = os.open(str(path), os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as f:
        s = os.fstat(f.fileno())
        need([s.st_dev, s.st_ino] == before[:2], 'SOURCE_OPEN_IDENTITY')
        raw = f.read(limit + 1)
    need(len(raw) == before[2] and metadata(path) == before, 'SOURCE_CHANGED:' + str(path))
    return raw

def save(path, value, raw=False):
    path = Path(path); no_symlinks(path)
    path.parent.mkdir(parents=True, exist_ok=True); no_symlinks(path.parent)
    with path.open('xb') as f:
        f.write(value if raw else canon(value)); f.flush(); os.fsync(f.fileno())

def append(path, value):
    with Path(path).open('ab') as f:
        f.write(canon(value)); f.flush()

def load_release(path):
    raw = read_stable(path)
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        names = z.namelist()
        need(len(names) == len(set(names)) and len(names) <= 20, 'RELEASE_DUPLICATES')
        mf = parse(z.read('MANIFEST.json'))
        need(set(names) == set(mf) | {'MANIFEST.json'}, 'RELEASE_MEMBER_SET')
        parts = {}
        for name, rec in mf.items():
            relative(name); b = z.read(name)
            need({'size': len(b), 'sha256': sha(b)} == rec, 'RELEASE_HASH:' + name)
            parts[name] = b
    need(parts['runner.py'] == read_stable(__file__), 'RUNNER_RELEASE_DRIFT')
    provenance = parse(parts['METHOD_PROVENANCE.json'])
    need(sha(parts['numeric_core.py']) == provenance['core_sha256'], 'CORE_HASH')
    need(sha(parts['WINDOW16_ORIGINAL_SOURCE.py']) == provenance['original_release_sha256'], 'ORIGINAL_HASH')
    # Verify exact source extraction without importing the historical module.
    original = parts['WINDOW16_ORIGINAL_SOURCE.py'].decode()
    core_source = parts['numeric_core.py'].decode()
    a = {n.name: n for n in ast.parse(original).body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
    b = {n.name: n for n in ast.parse(core_source).body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
    for name, rec in provenance['extracted_definitions'].items():
        s1 = ast.get_source_segment(original, a[name]); s2 = ast.get_source_segment(core_source, b[name])
        need(s1 == s2 and sha(s1.encode()) == rec['source_segment_sha256'], 'NUMERIC_SOURCE_DIFFERENCE:' + name)
    core = types.ModuleType('coverage32_numeric_core')
    exec(compile(core_source, 'numeric_core.py', 'exec'), core.__dict__)
    return parts, core, {'sha256': sha(raw), 'size': len(raw)}

def capture_parent(binding, out, audit=None):
    """Resolve only known paths. A present but wrong file is never silently bypassed."""
    got = {}; audit = [] if audit is None else audit; archives = {}
    try:
        for rel, expected in binding['files'].items():
            relative(rel); p = DATA/PARENT/rel; rec = {'logical_path': PARENT + '/' + rel, 'expected': expected}
            if os.path.lexists(p):
                raw = read_stable(p)
                rec.update(kind='direct', actual_path=str(p), metadata=metadata(p))
            else:
                raw = None
                for archive_name in (PARENT + '_review.zip', PARENT + '.zip'):
                    q = DATA/archive_name
                    if not q.exists():
                        continue
                    no_symlinks(q)
                    if q not in archives:
                        before = metadata(q); z = zipfile.ZipFile(q)
                        ns = z.namelist()
                        need(len(ns) == len(set(ns)), 'PARENT_ZIP_DUPLICATE_NAMES')
                        archives[q] = (z, before)
                    z, before = archives[q]
                    member = PARENT + '/' + rel
                    if member not in z.namelist():
                        continue
                    info = z.getinfo(member)
                    need(info.file_size == expected['size'], 'PARENT_ZIP_MEMBER_SIZE:' + member)
                    raw = z.read(member)
                    need(metadata(q) == before, 'PARENT_ARCHIVE_CHANGED')
                    rec.update(kind='archive_member', actual_path=str(q), member=member, metadata=before)
                    break
                need(raw is not None, 'MISSING_BOUND_INPUT:' + str(p))
            need({'size': len(raw), 'sha256': sha(raw)} == expected, 'BOUND_INPUT_DRIFT:' + rel)
            save(out/'sources'/rel, raw, True)
            got[rel] = raw; audit.append(rec)
            append(out/'INPUT_AUDIT.jsonl', rec)
        mf = parse(got['MANIFEST.json'])
        for rel, expected in binding['files'].items():
            if rel != 'MANIFEST.json':
                need(mf.get(rel) == expected, 'PARENT_MANIFEST_BINDING:' + rel)
        result = parse(got['RESULT.json'])
        need(got['RC.txt'].strip() == b'0' and result['rc'] == 0 and
             result['status'] == 'COMPLETE_COVERAGE32_NEW256_VERIFIED_NOT_MODEL_SUCCESS' and
             result['postcheck_status'] == 'PASS', 'PARENT_NOT_COMPLETE')
        need(result['new_teacher_traces'] == 256 and result['merged_observations'] == 512
             and result['merged_roots'] == 32, 'PARENT_COUNTS')
        return got, audit
    finally:
        for z, _ in archives.values():
            z.close()

def parent_postcheck(audit):
    checked = []
    for rec in audit:
        p = Path(rec['actual_path']); need(metadata(p) == rec['metadata'], 'PARENT_METADATA_CHANGED:' + str(p))
        if rec['kind'] == 'direct':
            raw = read_stable(p)
        else:
            with zipfile.ZipFile(p) as z:
                raw = z.read(rec['member'])
        need({'size': len(raw), 'sha256': sha(raw)} == rec['expected'], 'PARENT_BYTES_CHANGED:' + rec['logical_path'])
        checked.append(rec['logical_path'])
    return {'status': 'PASS', 'bound_files_unchanged': len(checked)}

def git_snapshot():
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', GIT_PAGER='cat')
    def run(args):
        r = subprocess.run(['git', '-C', str(REPO)] + args, env=env, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, timeout=30)
        need(r.returncode == 0, 'GIT_READ_FAILED:' + r.stderr.decode(errors='replace')[:500])
        return r.stdout
    return {'head': run(['rev-parse', 'HEAD']).decode().strip(),
            'status': run(['status', '--short']).decode(),
            'diff_sha256': sha(run(['diff', '--no-ext-diff', '--binary', 'HEAD']))}

def related_processes():
    """Inspect real argv script tokens; do not match grep text or a bash -c body."""
    own = os.getpid(); hits = []
    for p in Path('/proc').iterdir():
        if not p.name.isdigit() or int(p.name) == own:
            continue
        try:
            argv = [v.decode(errors='replace') for v in (p/'cmdline').read_bytes().split(b'\0') if v]
            if not argv:
                continue
            exe = Path(argv[0]).name.lower()
            if 'python' not in exe:
                continue
            if '-c' in argv[:3]:
                continue
            scripts = [v for v in argv[1:] if v.endswith('.py') and '\n' not in v]
            if any(('minesim_' in Path(v).name or Path(v).name == 'collect256.py') and
                   any(w in Path(v).name for w in ('collect', 'fit', 'diagnostic', 'teacher', 'window', 'smoke'))
                   for v in scripts):
                s = (p/'stat').read_text(); fields = s[s.rfind(')') + 2:].split()
                hits.append({'pid': int(p.name), 'ppid': int(fields[1]), 'start_ticks': int(fields[19]), 'argv': argv})
        except FileNotFoundError:
            continue
        except PermissionError as e:
            raise RuntimeError('PROCESS_VISIBILITY_HOLD:' + str(p)) from e
    return {'hits': hits, 'self_pid_excluded': own,
            'scope': 'Exact argv of project collection/fitting Python processes; no claim about unrelated jobs.'}

def resource_snapshot():
    m = {}
    for line in Path('/proc/meminfo').read_text().splitlines():
        k, v = line.split(':', 1); m[k] = int(v.split()[0]) * 1024
    available = m['MemAvailable']; limits = []
    for lp, up in [('/sys/fs/cgroup/memory.max', '/sys/fs/cgroup/memory.current'),
                   ('/sys/fs/cgroup/memory/memory.limit_in_bytes', '/sys/fs/cgroup/memory/memory.usage_in_bytes')]:
        if Path(lp).is_file() and Path(up).is_file():
            l = Path(lp).read_text().strip(); u = int(Path(up).read_text())
            limits.append({'limit_path': lp, 'limit': l, 'used': u})
            if l != 'max':
                available = min(available, int(l) - u)
    affinity = len(os.sched_getaffinity(0))
    cpus = float(affinity); quotas = []
    if Path('/sys/fs/cgroup/cpu.max').is_file():
        q, period = Path('/sys/fs/cgroup/cpu.max').read_text().split()
        quotas.append({'quota': q, 'period': int(period)})
        if q != 'max': cpus = min(cpus, int(q)/int(period))
    else:
        for root in ('/sys/fs/cgroup/cpu', '/sys/fs/cgroup/cpu,cpuacct'):
            q = Path(root)/'cpu.cfs_quota_us'; period = Path(root)/'cpu.cfs_period_us'
            if q.is_file() and period.is_file():
                qv, pv = int(q.read_text()), int(period.read_text()); quotas.append({'quota': qv, 'period': pv})
                if qv > 0: cpus = min(cpus, qv/pv)
    free = shutil.disk_usage(DATA).free
    return {'resource': 'LOW', 'effective_cpu_upper_bound': cpus, 'affinity_cpus': affinity,
            'cpu_quota_records': quotas, 'available_memory_bytes': available, 'memory_limits': limits,
            'free_disk_bytes': free, 'numeric_threads': 1, 'gpu_computation': False}

def environment():
    need(Path.cwd().resolve() == REPO.resolve(), 'FORMAL_REPO_CWD')
    need(os.environ.get('CONDA_DEFAULT_ENV') == 'minesim' and
         Path(sys.executable).resolve() == PYTHON.resolve(), 'MINESIM_ENVIRONMENT')
    need(sys.version_info[:2] == (3, 9), 'EXPECTED_CLOUD_PYTHON39')
    need(os.environ.get('CUDA_VISIBLE_DEVICES') == '', 'GPU_NOT_DISABLED')
    need(sys.dont_write_bytecode, 'BYTECODE_NOT_DISABLED')
    need(all(os.environ.get(k) == '1' for k in THREAD_VARS), 'NUMERIC_THREADS_NOT_ONE')
    import numpy as np
    need(np.__version__ == '1.23.4', 'FROZEN_NUMPY_VERSION:' + np.__version__)
    cfg = io.StringIO()
    from contextlib import redirect_stdout
    with redirect_stdout(cfg): np.show_config()
    return np, {'python': sys.version, 'numpy': np.__version__, 'executable': sys.executable,
                'conda': os.environ['CONDA_DEFAULT_ENV'], 'cwd': str(Path.cwd()),
                'gpu_visible': os.environ.get('CUDA_VISIBLE_DEVICES'),
                'numeric_threads': {k: os.environ[k] for k in THREAD_VARS}, 'numpy_config': cfg.getvalue()}

def close(a, b):
    return math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-10)

def validate_dataset(got, core, prereg):
    """Cheap in-memory schema/binding checks; no trajectory replay or re-collection."""
    ds = parse(got['DATASET32.json']); contract = parse(got['runtime/FUTURE_FITTING_CONTRACT_NOT_AUTHORIZED.json'])
    need(contract == prereg, 'PREREGISTERED_CONTRACT_DRIFT')
    expected = {'roots': 32, 'folds': 8, 'fits': 16, 'updates_per_fit': 2000, 'seed': 78003,
                'learning_rate': .001, 'beta1': .9, 'beta2': .999, 'epsilon': 1e-8,
                'target_scale': 100., 'models': core.MODELS, 'training_roots_per_fold': 28,
                'held_roots_per_fold': 4, 'target_id': TARGET, 'created_before_new_returns': True}
    need(all(contract.get(k) == v for k, v in expected.items()), 'FIXED_FIT_PARAMETERS')
    rows = ds['rows']; old = parse(got['runtime/inputs/OLD_DATASET16.json'])
    inputs = parse(got['runtime/inputs/COMBINED32_INPUTS.json'])
    newdiag = parse(got['NEW16_REPEAT_DIAGNOSTIC.json'])
    need(len(rows) == ds['roots'] == 32 and ds['observations'] == 512 and len(old['rows']) == 16, 'DATASET_COUNTS')
    need(ds['target_id'] == TARGET and ds['cross_group_exact_aliases'] == [], 'TARGET_OR_ALIAS_FLAG')
    need(ds['old_rows_unchanged'] and ds['old_known6_unknown10_unchanged'] and not ds['training_authorized']
         and not ds['deployment_authorized'], 'OLD_DATA_PERMISSIONS')
    old_by = {r['root_id']: r for r in old['rows']}; inp_by = {r['root_id']: r for r in inputs}
    new_by = {r['root_id']: r for r in newdiag['rows']}
    need(len(inp_by) == len(inputs) == 32 and len(new_by) == 16 and len(old_by) == 16, 'IDENTITY_SET_COUNTS')
    ids = [r['root_id'] for r in rows]
    need(len(ids) == len(set(ids)) and set(ids) == set(inp_by) == set(old_by) | set(new_by)
         and not (set(old_by) & set(new_by)), 'ROOT_IDENTITY_SET')
    groups = collections.Counter(r['source_run'] for r in rows)
    need(groups == {('policy_%02d' % i): 4 for i in range(8)} and sorted(groups) == ds['source_runs'], 'GROUP_COUNTS')
    identities = {}; cell_ids = set(); counts = collections.Counter()
    for r in rows:
        rid = r['root_id']; inp = inp_by[rid]
        if rid in old_by:
            need(r == old_by[rid], 'IMMUTABLE_OLD_ROW:' + rid)
            need(r['repeated_order_sign'] == OLD_SIGNS.get(rid), 'OLD6_UNKNOWN10:' + rid)
        need(r['source_run'] == inp['task']['task_id'] and r['full_state'] == inp['state'] and
             r['state_sha256'] == inp['exact_before_state_sha256'] == sha(canon(r['full_state'])), 'INPUT_STATE_IDENTITY:' + rid)
        x = core.feature26(r['full_state'])
        need(r['x'] == x and sha(struct.pack('<26f', *x)) == r['feature_sha256'], 'FEATURE_IDENTITY:' + rid)
        need(r['mask16'] == [True]*16 and not r['pruning_authorized'] and r['original_training_mask'] == 0, 'ACTION_SCOPE:' + rid)
        for kind, ident in [('state', r['state_sha256']), ('feature', r['feature_sha256'])]:
            key = (kind, ident)
            need(key not in identities or identities[key] == r['source_run'], 'CROSS_GROUP_EXACT_ALIAS:' + rid)
            identities[key] = r['source_run']
        blocks = {b: {a: [] for a in ('0,3', '3,0')} for b in ('block0', 'block1')}
        need(len(r['records']) == 16, 'RECORD_COUNT:' + rid)
        for o in r['records']:
            need(o['cell_id'] not in cell_ids, 'DUPLICATE_OBSERVATION'); cell_ids.add(o['cell_id'])
            need(o['root_id'] == rid and o['root_state_sha256'] == r['state_sha256'] and o['target_id'] == TARGET,
                 'OBSERVATION_ROOT_BINDING')
            need(o['block'] in blocks and o['action_id'] in blocks[o['block']], 'OBSERVATION_BLOCK_ACTION')
            v, n = o['window_return'], o['executed_steps']
            need(o['window_target_observed'] is True and type(v) in (int, float) and math.isfinite(v)
                 and type(n) is int and 1 <= n <= 128 and o['maximum_outer_steps'] == 128, 'WINDOW_OBSERVED')
            if o['task_outcome'] == 'EVALUATION_CAP_NOT_TASK_TERMINAL':
                need(n == 128 and o['old_full_task_return'] is None and o['old_full_task_tail_censored'] is True, 'CAP_IMPUTATION')
            else:
                need(o['task_outcome'] in ('BOTH_PARKED_AT_OWN_DESTINATIONS', 'EXECUTED_HARD_SAFETY_TERMINAL')
                     and o['old_full_task_return'] == v and o['old_full_task_tail_censored'] is False, 'TASK_TERMINAL')
            need(o['training_mask'] == 0 and o['pruning_authorized'] is False, 'LABEL_PERMISSION')
            blocks[o['block']][o['action_id']].append(v); counts[o['task_outcome']] += 1
        need(blocks == r['blocks'] and all(len(v) == 4 for b in blocks.values() for v in b.values()), 'BLOCKS_PRESERVED')
        means = {a: math.fsum(blocks['block0'][a] + blocks['block1'][a])/8 for a in ('0,3', '3,0')}
        need(all(close(means[a], r['mean_returns'][a]) for a in means) and
             close(means['0,3'] - means['3,0'], r['empirical_mean_gap03_minus30']), 'EMPIRICAL_GAP_CHECK')
        bg = [math.fsum(blocks[b]['0,3'])/4 - math.fsum(blocks[b]['3,0'])/4 for b in ('block0','block1')]
        need(all(close(a,b) for a,b in zip(bg, r['block_mean_gaps'])), 'BLOCK_GAP_CHECK')
        if rid in new_by:
            signs = [core.four_direction(blocks[b]['0,3'], blocks[b]['3,0']) for b in ('block0','block1')]
            repeated = signs[0] if signs[0] is not None and signs[0] == signs[1] else None
            need(repeated == r['repeated_order_sign'] == new_by[rid]['repeated_order_sign'], 'NEW_DESCRIPTIVE_ORDER')
    need(len(cell_ids) == 512, 'TOTAL_OBSERVATIONS')
    folds = core.folds_for(rows)
    for f in folds:
        need(len(f['train_indices']) == 28 and len(f['test_indices']) == 4, '28_4_SPLIT')
        f['train_root_ids'] = [ids[i] for i in f['train_indices']]
        f['test_root_ids'] = [ids[i] for i in f['test_indices']]
        f['train_observations'] = 448; f['held_observations'] = 64
        f['fit_unit'] = '28 equally weighted state mean gaps; not448 independent training rows'
    return ds, contract, folds, set(old_by), {'roots':32, 'observations':512, 'source_groups':dict(groups),
        'old_rows_reused_unchanged':16, 'new_input_rows':16, 'old_known_orders':6, 'old_unknown_orders':10,
        'new_descriptive_known':newdiag['known_count'], 'new_descriptive_coverage_denominator':16,
        'outcomes':dict(counts), 'cross_group_exact_aliases':[], 'new_simulation_calls':0}

def predictions(np, core, params, X, rows, fold, old_ids):
    te, tr = fold['test_indices'], fold['train_indices']
    baseline = math.fsum(rows[i]['empirical_mean_gap03_minus30'] for i in tr)/len(tr)
    pred = core.forward(np, params, X[te])[0]; result = []
    for j, i in enumerate(te):
        r = rows[i]; p = float(pred[j])*core.SCALE; g = r['empirical_mean_gap03_minus30']
        s = r['repeated_order_sign']; old = r['root_id'] in old_ids
        result.append({'root_id':r['root_id'],'source_run':r['source_run'], 'is_old16':old,
            'observed_empirical_mean_gap':g, 'predicted_mean_gap':p, 'signed_error':p-g, 'absolute_error':abs(p-g),
            'training_only_constant_gap':baseline, 'constant_absolute_error':abs(baseline-g),
            'block_mean_gaps':r['block_mean_gaps'], 'block_absolute_errors':[abs(p-v) for v in r['block_mean_gaps']],
            'ordering_subset':'OLD6_CONFIRMED' if old and s is not None else 'OLD10_UNKNOWN' if old else 'NEW16_DESCRIPTIVE',
            'repeated_order_sign':s, 'prediction_sign':core.preference(p),
            'known_order_correct':None if s is None else core.preference(p)==s,
            'fixed03_known_order_correct':None if s is None else s==1,
            'constant_known_order_correct':None if s is None else core.preference(baseline)==s,
            'unknown_not_imputed':s is None, 'not_Q_star_or_safety_label':True})
    return result

def error_stats(rows):
    if not rows:
        return {'count':0,'mae':None,'rmse':None,'constant_mae':None,'constant_rmse':None}
    n = len(rows)
    return {'count':n, 'mae':math.fsum(r['absolute_error'] for r in rows)/n,
            'rmse':math.sqrt(math.fsum(r['absolute_error']**2 for r in rows)/n),
            'constant_mae':math.fsum(r['constant_absolute_error'] for r in rows)/n,
            'constant_rmse':math.sqrt(math.fsum(r['constant_absolute_error']**2 for r in rows)/n)}

def order_stats(rows, coverage_denominator):
    known = [r for r in rows if r['repeated_order_sign'] is not None]
    return {'correct':sum(r['known_order_correct'] for r in known),'known_denominator':len(known),
            'fixed03_correct':sum(r['fixed03_known_order_correct'] for r in known),
            'constant_correct':sum(r['constant_known_order_correct'] for r in known),
            'observed_rows':len(rows),'coverage_denominator':coverage_denominator,
            'unknown_count':len(rows)-len(known), 'unknowns_not_scored':True}

def aggregate(fits, models):
    result = {}
    for m in models:
        fs = [f for f in fits if f['model']==m]; rs = [r for f in fs for r in f['held_out']]
        g = {f['group_held_out']:error_stats(f['held_out']) for f in fs}
        allstats = error_stats(rs)
        result[m] = {'completed_folds':len(fs), 'planned_folds':8, 'planned_roots':32,
            'all32_empirical_gap_errors':allstats, 'per_source_group':g,
            'source_macro_mae':None if not g else math.fsum(v['mae'] for v in g.values())/len(g),
            'old16_errors':error_stats([r for r in rs if r['is_old16']]),
            'new16_errors':error_stats([r for r in rs if not r['is_old16']]),
            'original6_orders_and10_unknown':order_stats([r for r in rs if r['is_old16']],16),
            'new16_descriptive_orders':order_stats([r for r in rs if not r['is_old16']],16),
            'mae_below_constant_in_this_development_dataset':None if not rs else allstats['mae'] < allstats['constant_mae'],
            'incomplete_is_partial_not_imputed':len(fs)!=8, 'generalization_certified':False}
    return result

def perform_fits(np, core, ds, contract, folds, old_ids, out, state):
    rows = ds['rows']; X = np.asarray([r['x'] for r in rows], dtype=np.float32).astype(np.float64)
    y = np.asarray([r['empirical_mean_gap03_minus30']/core.SCALE for r in rows], dtype=np.float64)
    completed=[]
    for no, fold in enumerate(folds):
        for model in contract['models']:
            fid='fold%02d_%s'%(no,model); dest=out/'fits'/fid; dest.mkdir(parents=True,exist_ok=False)
            state['fits_started'] += 1; state['active_fit']=fid; state['active_updates_observed']=0
            save(dest/'FIT_START.json',{'at':utc(),'seed':contract['seed'],'group':fold['group'],
                 'train_indices':fold['train_indices'],'held_indices':fold['test_indices'],
                 'test_rows_used_for_fitting':False})
            p=core.init(np,model,contract['seed'])
            save(dest/'INITIAL_MODEL.json',core.model_object(p,model,False,0))
            started=time.monotonic()
            def progress(rec):
                state['active_updates_observed']=rec['update']
                append(dest/'PROGRESS.jsonl',rec)
                if rec['update']%500==0:
                    print('FIT=%s; UPDATES=%d/2000; FITS_COMPLETED=%d/16'%(fid,rec['update'],state['fits_completed']),flush=True)
            try:
                p,hist=core.train(np,p,X[fold['train_indices']],y[fold['train_indices']],
                                 contract['updates_per_fit'],contract['learning_rate'],progress,None)
            except core.FitInterrupted as e:
                state['active_updates_observed']=e.updates
                save(dest/'PARTIAL_MODEL.json',core.model_object(e.params,model,False,e.updates))
                save(dest/'INCOMPLETE.json',{'reason':str(e),'completed_updates':e.updates,
                     'recorded_history':e.history,'automatic_resume':False})
                raise
            need(hist['updates']==2000,'UPDATE_COUNT_MISMATCH')
            save(dest/'MODEL.json',core.model_object(p,model,True,hist['updates']))
            reloaded={k:np.asarray(v,dtype=np.float64) for k,v in parse(read_stable(dest/'MODEL.json'))['parameters'].items()}
            need(np.array_equal(core.forward(np,p,X)[0],core.forward(np,reloaded,X)[0]),'MODEL_RELOAD_PARITY')
            held=predictions(np,core,reloaded,X,rows,fold,old_ids)
            rec={'fold':no,'model':model,'group_held_out':fold['group'],
                 'train_roots':fold['train_root_ids'],'test_roots':fold['test_root_ids'],
                 'training':hist,'held_out':held,'model_reload_exact':True,
                 'elapsed_seconds':time.monotonic()-started,'development_only':True,
                 'not_independent_route_test':True,'full32_refit':False,'deployable':False}
            save(dest/'RESULT.json',rec); completed.append(rec)
            state['fits_completed']+=1;state['updates_completed_in_finished_fits']+=2000
            state['active_fit']=None;state['active_updates_observed']=0
            save(out/('COMPLETED_FIT_%02d.json'%state['fits_completed']),{'directory':fid,'result_sha256':sha(canon(rec))})
            # Partial metrics are allowed but never filled in for unfinished fits.
            save(out/('PARTIAL_METRICS_%02d.json'%state['fits_completed']),aggregate(completed,contract['models']))
            print('FITS_COMPLETED=%d/16; %s; ELAPSED_FIT=%.2fs'%(state['fits_completed'],fid,rec['elapsed_seconds']),flush=True)
    return completed

def independent_readback(np, core, out, ds, folds, old_ids, models):
    """Separate forward/meter calculation from saved weights, no refitting."""
    rows=ds['rows'];X=np.asarray([r['x'] for r in rows],dtype=np.float32).astype(np.float64);fits=[]
    max_abs=0.; count=0
    for no,f in enumerate(folds):
        for model in models:
            dest=out/'fits'/('fold%02d_%s'%(no,model));obj=parse(read_stable(dest/'MODEL.json'))
            rec=parse(read_stable(dest/'RESULT.json'));p={k:np.asarray(v,dtype=np.float64) for k,v in obj['parameters'].items()}
            need(obj['complete_fit'] and obj['completed_updates']==2000 and not obj['deployable'], 'READBACK_MODEL_SCOPE')
            H=X[f['test_indices']]
            layer_count=len(p)//2
            for i in range(layer_count):
                H=np.dot(H,p['W'+str(i)])+p['b'+str(i)]
                if i<layer_count-1:H=np.where(H>0.,H,0.)
            ys=(H[:,0] if H.shape[1]==1 else H[:,3]-H[:,12])*100.
            direct=predictions(np,core,p,X,rows,f,old_ids)
            need(direct==rec['held_out'],'SAVED_PREDICTION_PARITY')
            for pv,rv in zip(ys,rec['held_out']):
                err=abs(float(pv)-rv['predicted_mean_gap']);max_abs=max(max_abs,err);count+=1
                need(close(float(pv),rv['predicted_mean_gap']), 'INDEPENDENT_FORWARD_MISMATCH')
            tr=X[f['train_indices']]
            for i in range(layer_count):
                tr=tr@p['W'+str(i)]+p['b'+str(i)]
                if i<layer_count-1:tr=np.maximum(tr,0.)
            yp=tr[:,0] if tr.shape[1]==1 else tr[:,3]-tr[:,12]
            target=np.asarray([rows[i]['empirical_mean_gap03_minus30']/100. for i in f['train_indices']])
            loss=float(.5*np.mean((yp-target)**2))
            need(close(loss,rec['training']['final_loss']),'SAVED_FINAL_LOSS_MISMATCH')
            fits.append(rec)
    metrics=aggregate(fits,models)
    return metrics, {'status':'PASS','saved_models_checked':len(fits),'held_predictions_checked':count,
         'max_independent_forward_absolute_error':max_abs,'new_training_runs':0,
         'method':'Read saved JSON weights; separately evaluate forward matrix operations and train final loss. Recompute all metrics; no fitting.'}

def text_report(metrics):
    lines=['Coverage32：512条冻结回报的分组开发诊断','',
           '执行完成不等于模型有优势；同一路线开发数据，不是新矿区盲测或安全证明。',
           '每折留出一个来源运行的全部4个状态；仅用28个训练状态的均值差拟合。','']
    for m,s in metrics.items():
        e=s['all32_empirical_gap_errors']; old=s['original6_orders_and10_unknown'];new=s['new16_descriptive_orders']
        lines += [m, '  MAE=%.8f, RMSE=%.8f; 常数基线 MAE=%.8f, RMSE=%.8f'%(e['mae'],e['rmse'],e['constant_mae'],e['constant_rmse']),
             '  原6条关系：%d/%d；固定03：%d/%d；原未知10条不评分。'%(old['correct'],old['known_denominator'],old['fixed03_correct'],old['known_denominator']),
             '  新16状态描述性关系：%d/%d；覆盖%d/16，未知%d。'%(new['correct'],new['known_denominator'],new['known_denominator'],new['unknown_count']),'']
    lines += ['比较32状态总体误差与旧Window16总体误差不是单因素消融；不要因目标分布变化宣称因果改善。',
              '无新采样、无MCTS、无部署、无全部32状态最终重拟合；不因效果不好自动加数据或换seed。']
    return '\n'.join(lines)+'\n'

def package(out):
    mf={}
    for p in sorted(out.rglob('*')):
        if p.is_file():
            no_symlinks(p);raw=read_stable(p);mf[p.relative_to(out).as_posix()]={'size':len(raw),'sha256':sha(raw)}
    save(out/'MANIFEST.json',mf)
    pending=Path(str(out)+'.zip.pending');final=Path(str(out)+'.zip')
    need(not os.path.lexists(pending) and not os.path.lexists(final),'PACKAGE_ALREADY_EXISTS')
    with zipfile.ZipFile(pending,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=3) as z:
        for rel in list(mf)+['MANIFEST.json']:z.write(out/rel,out.name+'/'+rel)
    with zipfile.ZipFile(pending) as z:
        need(len(z.namelist())==len(set(z.namelist()))==len(mf)+1,'ZIP_MEMBER_COUNT')
        need(parse(z.read(out.name+'/MANIFEST.json'))==mf,'ZIP_MANIFEST_PARITY')
        for rel,expected in mf.items():
            raw=z.read(out.name+'/'+rel)
            need({'size':len(raw),'sha256':sha(raw)}==expected,'ZIP_MEMBER_PARITY:'+rel)
    os.link(pending,final)  # create-only atomic publication; preserve pending evidence
    return final,sha(read_stable(final))

def execute(authorized=False):
    need(authorized,'EXPLICIT_FIT_AUTHORIZATION_REQUIRED')
    out=DATA/NAME; lease=DATA/(NAME+'.lease.json')
    for p in (out,lease,Path(str(out)+'.zip'),Path(str(out)+'.zip.pending')):
        need(not os.path.lexists(p),'ONE_TIME_NAMESPACE_ALREADY_EXISTS:'+str(p))
    save(lease,{'created_utc':utc(),'pid':os.getpid(),'gate':GATE,'training_authorized':True,
                'scope':'one fixed16-fit development run, no collection/deployment/retry','automatic_retry':False})
    out.mkdir(exist_ok=False)
    state={'status':'PRE_RUNTIME_TECHNICAL_HOLD','gate':GATE,'resource':'LOW','started_utc':utc(),
           'scientific_start_written':False,'fits_planned':16,'fits_started':0,'fits_completed':0,
           'updates_completed_in_finished_fits':0,'active_fit':None,'active_updates_observed':0,
           'new_teacher_traces':0,'mcts_calls':0,'training_authorized':True,'collection_authorized':False,
           'deployment_authorized':False,'pruning_authorized':False,'automatic_retry':False,
           'full32_refit':False,'errors':[],'postcheck_errors':[]}
    audit=[];before=None;release_meta=None;rc=2
    def stop(signum,frame):
        raise KeyboardInterrupt('SIGNAL_'+str(signum))
    prior={s:signal.signal(s,stop) for s in (signal.SIGTERM,signal.SIGINT,signal.SIGHUP)}
    try:
        parts,core,release_meta=load_release(DATA/RELEASE)
        for n,raw in parts.items():save(out/'release'/n,raw,True)
        save(out/'RELEASE_BINDING.json',release_meta)
        np,env=environment();save(out/'ENVIRONMENT.json',env)
        res=resource_snapshot();save(out/'RESOURCES.json',res)
        need(res['available_memory_bytes']>=256*1024**2 and res['free_disk_bytes']>=128*1024**2,
             'LOW_MEMORY_OR_DISK_HOLD')
        proc=related_processes();save(out/'PROCESSES_BEFORE.json',proc);need(not proc['hits'],'OTHER_PROJECT_RUN_HOLD')
        before=git_snapshot();save(out/'GIT_BEFORE.json',before)
        binding=parse(parts['SOURCE_BINDINGS.json']);got,audit=capture_parent(binding,out,audit)
        state['sources_verified']=len(audit)
        parent_git=parse(got['GIT_AFTER.json'])
        need(parent_git==parse(got['GIT_BEFORE.json']),'PARENT_GIT_NOT_STABLE')
        need(before['head']==parent_git['head'] and before['diff_sha256']==parent_git['diff_sha256'],'TRACKED_REPO_DRIFT')
        state['untracked_status_matches_collection']=before['status']==parent_git['status']
        ds,contract,folds,old_ids,check=validate_dataset(got,core,parse(parts['PREREGISTERED_FITTING_CONTRACT.json']))
        save(out/'INPUT_VALIDATION.json',check);save(out/'FOLDS.json',folds)
        protocol={'gate':GATE,'frozen_parent_contract_unchanged':True,'contract':contract,
           'execution_authorization':{'training':True,'fits':16,'new_collection':False,'automatic_retry':False},
           'dataset_sha256':sha(got['DATASET32.json']),'created_utc':utc(),
           'fold_order':'source_run lexicographic; original DATASET32 row order retained within train/held sets',
           'initialization':'exact Window16 kernel; seed78003 reset for every model/fold; linear zero init',
           'all_rows_used':'32 state means, 512 observations; CAP45 included for complete Y64, no bootstrap',
           'model_selection':'fixed final update2000; no early stop, no hyperparameter search',
           'readback_check':'saved model forward/metrics recomputation is not another fit',
           'execution':'one process, NumPy CPU, numeric library threads1; no simulator imports',
           'limits':'post-outcome same-route development; not independent-route validation or causal ablation',
           'fit_function_sha256':parse(parts['METHOD_PROVENANCE.json'])['extracted_definitions']['train']['source_segment_sha256']}
        save(out/'EXECUTION_PROTOCOL.json',protocol)
        save(out/'START.json',{'at':utc(),'gate':GATE,'dataset_sha256':protocol['dataset_sha256'],
            'contract_sha256':sha(got['runtime/FUTURE_FITTING_CONTRACT_NOT_AUTHORIZED.json']),
            'execution_protocol_sha256':sha(canon(protocol)),'fits':16,'seed':78003,'updates_per_fit':2000,
            'new_samples':0,'mcts_calls':0,'training_authorization':'--authorize-fit16-once'})
        state['scientific_start_written']=True;state['status']='RUNNING_COVERAGE32_FIT16'
        print('START=COVERAGE32_FIT16; ROOTS=32; OBSERVATIONS=512; GROUPS=8; NEW_SAMPLES=0; MCTS_CALLS=0',flush=True)
        t=time.monotonic();completed=perform_fits(np,core,ds,contract,folds,old_ids,out,state)
        metrics,readback=independent_readback(np,core,out,ds,folds,old_ids,contract['models'])
        need(metrics==aggregate(completed,contract['models']),'AGGREGATE_READBACK_PARITY')
        save(out/'METRICS.json',metrics);save(out/'READBACK_CHECK.json',readback)
        save(out/'SUMMARY.txt',text_report(metrics).encode(),True)
        save(out/'TIMING.json',{'fit_and_readback_seconds':time.monotonic()-t,
            'excludes_preflight_packaging_upload':True,'worker_processes':1,'numeric_threads':1})
        state.update(status=COMPLETE,metrics=metrics,roots=32,observations=512,source_groups=8,
                     model_reload_and_metric_readback='PASS',scientific_model_advantage='See held-source metrics; completion is not generalization proof')
        rc=0
    except (Exception,KeyboardInterrupt) as e:
        state['errors'].append({'type':type(e).__name__,'message':str(e)})
        state['status']='RUNTIME_TECHNICAL_HOLD' if state['scientific_start_written'] else 'PRE_RUNTIME_TECHNICAL_HOLD'
        save(out/'ERROR.txt',traceback.format_exc().encode(),True)
    finally:
        # Never overwrite the first error with an unrelated postcheck status.
        for s,h in prior.items():signal.signal(s,h)
        for label,fn in [('parent',lambda:parent_postcheck(audit)),('process',related_processes),('git',git_snapshot)]:
            if label=='parent' and not audit:continue
            if label=='git' and before is None:continue
            try:
                value=fn();save(out/('POSTCHECK_'+label.upper()+'.json'),value)
                if label=='process':need(not value['hits'],'POSTCHECK_OTHER_PROJECT_RUN')
                if label=='git':need(value==before,'POSTCHECK_GIT_CHANGED')
            except Exception as e:state['postcheck_errors'].append({'check':label,'type':type(e).__name__,'message':str(e)})
        if state['postcheck_errors']:
            if rc==0:state['status']='HOLD_POSTCHECK_COMPLETED_FITS_PRESERVED'
            rc=2
        if release_meta is not None:
            try:need(sha(read_stable(DATA/RELEASE))==release_meta['sha256'],'RELEASE_CHANGED_DURING_RUN')
            except Exception as e:
                state['postcheck_errors'].append({'check':'release','message':str(e)});rc=2
                if state['status']==COMPLETE:state['status']='HOLD_POSTCHECK_COMPLETED_FITS_PRESERVED'
        state['finished_utc']=utc();state['rc']=rc
        state['sources_verified']=len(audit)
        state['active_update_count_note']='Caught core interruptions save exact partial updates; abrupt hard-kill status must be read from preserved files, never inferred as zero.'
        save(out/'RESULT.json',state);save(out/'RC.txt',(str(rc)+'\n').encode(),True)
        save(out/'CAPTURE.json',{'finished_utc':utc(),'status':state['status'],'scientific_start_written':state['scientific_start_written'],
             'fits_completed':state['fits_completed'],'automatic_retry':False,'scope':'This process and bound files only, not full cloud inventory'})
        print('STATUS='+state['status'],flush=True)
        print('FITS_COMPLETED=%d/16; NEW_TEACHER_TRACES=0; MCTS_CALLS=0; DEPLOYMENT=False'%state['fits_completed'],flush=True)
        try:
            bundle,digest=package(out)
            print('BUNDLE='+str(bundle),flush=True);print('ZIP_VERIFIED=True; ZIP_SHA256='+digest,flush=True)
        except Exception:
            print('PACKAGING_HOLD: original output and any pending preserved. No automatic retry.\n'+traceback.format_exc(),flush=True)
            # No overwrite of the already frozen scientific RESULT/RC; separate transport status.
            print('TRANSPORT_RC=2; OUTPUT_DIR='+str(out),flush=True);rc=2
    return rc

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--authorize-fit16-once', action='store_true', required=True)
    args=p.parse_args()
    try:return execute(args.authorize_fit16_once)
    except (Exception,KeyboardInterrupt):
        print('ENTRY_HOLD: preserve existing namespace/lease/results; no automatic retry.\n'+traceback.format_exc(),flush=True)
        return 2

if __name__=='__main__':
    sys.exit(main())
