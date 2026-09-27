"""Ancestor-aware process snapshot from the immediately preceding release."""
import os
from pathlib import Path

def need(ok, why):
    if not ok:
        raise RuntimeError(why)

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
            if any(s in n for s in ('collect', 'fit', 'teacher', 'window', 'smoke', 'regularized', 'interaction', 'diagnostic', 'scaledridge')):
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
