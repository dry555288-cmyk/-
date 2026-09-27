#!/usr/bin/env python3
"""Export 104 already located MineSim records; never execute or alter an experiment.

Python 3.9+, standard library only. Only --collect-readonly is a cloud action.
No directory search, source import, archive extraction, process signal, training,
resume, repair, original-file overwrite or original-archive rewrite is performed.
The three full batch archives are metadata-only, NOT included or certified.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import sys
import traceback
import zipfile

DATA = Path('/root/autodl-tmp')
REPO = Path('/root/MineSim-Dynamic')
PREFIX = Path('/root/miniconda3/envs/minesim')
NAME = 'minesim_recent_stage_evidence_export_v1'
GATE = 'LOCATED_RECENT_STAGE_RECORDS_EXPORT_ONLY'
MIB = 1024**2
MAX_FILE = 4*MIB
MAX_TOTAL = 32*MIB
RESERVE = 64*MIB
PLAN_SHA256 = 'adc15da7a7048c70732a8c44b419d0fd89e532309d87259844383ba1c0087ab5'
PLAN_TEXT = '{\n  "gate": "LOCATED_RECENT_STAGE_RECORDS_EXPORT_ONLY",\n  "plan_source": "26054d15-f09f-4ac8-b1f1-3e57fcbbfbcc.zip / INVENTORY.json",\n  "source_inventory_sha256": "e57023b054c02fdff204f7a219f3c9d6090f630f818101b3223a55d38855f881",\n  "roots": [\n    "minesim_discovery_remaining390_parallel_v1",\n    "minesim_discovery_cell377_tail_continuation_v1",\n    "minesim_confirmation768_parallel_v1"\n  ],\n  "copy_files": [\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1.screen.log",\n      "size": 19959,\n      "mtime_ns": 1789140748834320662\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1.screen_rc.txt",\n      "size": 2,\n      "mtime_ns": 1789140748838320310\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/AUTHORIZATION.json",\n      "size": 1562,\n      "mtime_ns": 1789139115594580006\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/CAPTURE.json",\n      "size": 156,\n      "mtime_ns": 1789140736701718514\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/COLLECTION_AUDIT.json",\n      "size": 162994,\n      "mtime_ns": 1789140735653449228\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/IMPORT_PROBE.stderr.txt",\n      "size": 0,\n      "mtime_ns": 1789139115526536090\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/IMPORT_PROBE.stdout.txt",\n      "size": 2977,\n      "mtime_ns": 1789139115522533506\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/MANIFEST.json",\n      "size": 845760,\n      "mtime_ns": 1789140737741943163\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/POSTCHECK.json",\n      "size": 282915,\n      "mtime_ns": 1789140736693716568\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/PREFLIGHT.json",\n      "size": 284791,\n      "mtime_ns": 1789139115542546423\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/RC.txt",\n      "size": 2,\n      "mtime_ns": 1789140736701718514\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/RESULT.json",\n      "size": 1040,\n      "mtime_ns": 1789140736697717541\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/SCHEDULE.json",\n      "size": 379572,\n      "mtime_ns": 1789139115598582589\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/SEED_LEASE.json",\n      "size": 427,\n      "mtime_ns": 1789139115598582589\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/START.json",\n      "size": 266,\n      "mtime_ns": 1789139115602585172\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/bundle/BINDINGS_LIVE_FILES.json",\n      "size": 238350,\n      "mtime_ns": 1789139114401809873\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/bundle/CONFIRMATION_SCHEDULE.json",\n      "size": 379572,\n      "mtime_ns": 1789139114401809873\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/bundle/CONFIRMATION_SPEC.json",\n      "size": 20361,\n      "mtime_ns": 1789139114405812458\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/bundle/EXECUTION_PAYLOAD_MANIFEST.json",\n      "size": 16337,\n      "mtime_ns": 1789139114405812458\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/bundle/PAYLOAD_MANIFEST.json",\n      "size": 14483,\n      "mtime_ns": 1789139114405812458\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/bundle/RELEASE_PROTOCOL.json",\n      "size": 396512,\n      "mtime_ns": 1789139114405812458\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/bundle/REVIEWED_COLLECTORS.json",\n      "size": 688,\n      "mtime_ns": 1789139114405812458\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/bundle/SOURCE_BINDINGS.json",\n      "size": 19435,\n      "mtime_ns": 1789139114409815044\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/bundle/WORKER_ASSIGNMENTS.json",\n      "size": 25370,\n      "mtime_ns": 1789139114409815044\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/bundle/frozen/ALL_PAIRS_1440.json",\n      "size": 1015182,\n      "mtime_ns": 1789139114417820215\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/bundle/frozen/CANDIDATE_FREEZE.json",\n      "size": 2034,\n      "mtime_ns": 1789139114421822800\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/bundle/frozen/CANDIDATE_LIMITATIONS_AND_SPLIT_SUPPORT.json",\n      "size": 3527,\n      "mtime_ns": 1789139114421822800\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/bundle/frozen/CONFIRMATION_HANDOFF.json",\n      "size": 1331,\n      "mtime_ns": 1789139114421822800\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/bundle/frozen/DISCOVERY_CANDIDATES.json",\n      "size": 193904,\n      "mtime_ns": 1789139114421822800\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/bundle/frozen/EPISODE_SPLITS_DESIGN.json",\n      "size": 4382,\n      "mtime_ns": 1789139114425825386\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/bundle/frozen/OBSERVATIONS_768.json",\n      "size": 896221,\n      "mtime_ns": 1789139114425825386\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/bundle/frozen/PLANNED_CELLS_1536.csv",\n      "size": 138116,\n      "mtime_ns": 1789139114425825386\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/bundle/frozen/PROTOCOL.json",\n      "size": 15581,\n      "mtime_ns": 1789139114425825386\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/bundle/frozen/SELECTED_12_ROOTS_DESIGN.json",\n      "size": 11377,\n      "mtime_ns": 1789139114425825386\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/bundle/frozen/prior_DISCOVERY_LEDGER_768.json",\n      "size": 853788,\n      "mtime_ns": 1789139114425825386\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/bundle/frozen/protocol_reference_frozen.py",\n      "size": 8444,\n      "mtime_ns": 1789139114429827971\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/parallel/PHASE_RESULT.json",\n      "size": 189,\n      "mtime_ns": 1789140717506481597\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/parallel/PROCESSES.json",\n      "size": 379684,\n      "mtime_ns": 1789139115638608422\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/parallel/workers/worker_0/PROGRESS.jsonl",\n      "size": 35096,\n      "mtime_ns": 1789140673349123329\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/parallel/workers/worker_0/RESULT.json",\n      "size": 6534,\n      "mtime_ns": 1789140673349123329\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/parallel/workers/worker_0/START.json",\n      "size": 95016,\n      "mtime_ns": 1789139116467142921\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/parallel/workers/worker_1/PROGRESS.jsonl",\n      "size": 35087,\n      "mtime_ns": 1789140717051626776\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/parallel/workers/worker_1/RESULT.json",\n      "size": 6534,\n      "mtime_ns": 1789140717051626776\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/parallel/workers/worker_1/START.json",\n      "size": 95016,\n      "mtime_ns": 1789139116611235844\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/parallel/workers/worker_2/PROGRESS.jsonl",\n      "size": 35088,\n      "mtime_ns": 1789140701300035060\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/parallel/workers/worker_2/RESULT.json",\n      "size": 6533,\n      "mtime_ns": 1789140701303964916\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/parallel/workers/worker_2/START.json",\n      "size": 95017,\n      "mtime_ns": 1789139116619241006\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/parallel/workers/worker_3/PROGRESS.jsonl",\n      "size": 35106,\n      "mtime_ns": 1789140696441684684\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/parallel/workers/worker_3/RESULT.json",\n      "size": 6533,\n      "mtime_ns": 1789140696441684684\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/parallel/workers/worker_3/START.json",\n      "size": 95017,\n      "mtime_ns": 1789139116639253912\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1/runner.py.txt",\n      "size": 1590799,\n      "mtime_ns": 1789139114477858995\n    },\n    {\n      "relative_path": "minesim_discovery_cell377_tail_continuation_v1.screen.log",\n      "size": 8232,\n      "mtime_ns": 1789132217556247729\n    },\n    {\n      "relative_path": "minesim_discovery_cell377_tail_continuation_v1.screen_rc.txt",\n      "size": 2,\n      "mtime_ns": 1789132217676243772\n    },\n    {\n      "relative_path": "minesim_discovery_cell377_tail_continuation_v1/AUTHORIZATION.json",\n      "size": 1164,\n      "mtime_ns": 1789132198864865841\n    },\n    {\n      "relative_path": "minesim_discovery_cell377_tail_continuation_v1/CAPTURE.json",\n      "size": 290,\n      "mtime_ns": 1789132217096262897\n    },\n    {\n      "relative_path": "minesim_discovery_cell377_tail_continuation_v1/JOIN_VALIDATION.json",\n      "size": 661,\n      "mtime_ns": 1789132216964267250\n    },\n    {\n      "relative_path": "minesim_discovery_cell377_tail_continuation_v1/MANIFEST.json",\n      "size": 18419,\n      "mtime_ns": 1789132217168260523\n    },\n    {\n      "relative_path": "minesim_discovery_cell377_tail_continuation_v1/POSTCHECK.json",\n      "size": 199,\n      "mtime_ns": 1789132217076263557\n    },\n    {\n      "relative_path": "minesim_discovery_cell377_tail_continuation_v1/PREFLIGHT.json",\n      "size": 7580,\n      "mtime_ns": 1789132198860865973\n    },\n    {\n      "relative_path": "minesim_discovery_cell377_tail_continuation_v1/PROGRESS.jsonl",\n      "size": 5972,\n      "mtime_ns": 1789132216688276354\n    },\n    {\n      "relative_path": "minesim_discovery_cell377_tail_continuation_v1/RC.txt",\n      "size": 2,\n      "mtime_ns": 1789132217096262897\n    },\n    {\n      "relative_path": "minesim_discovery_cell377_tail_continuation_v1/RECONSTRUCTED_CONTEXT.json",\n      "size": 884,\n      "mtime_ns": 1789132204176689824\n    },\n    {\n      "relative_path": "minesim_discovery_cell377_tail_continuation_v1/REQUEST.json",\n      "size": 253,\n      "mtime_ns": 1789132196576941745\n    },\n    {\n      "relative_path": "minesim_discovery_cell377_tail_continuation_v1/RESULT.json",\n      "size": 881,\n      "mtime_ns": 1789132217096262897\n    },\n    {\n      "relative_path": "minesim_discovery_cell377_tail_continuation_v1/START.json",\n      "size": 447,\n      "mtime_ns": 1789132198864865841\n    },\n    {\n      "relative_path": "minesim_discovery_cell377_tail_continuation_v1/STATIC_INPUT_CHECK.json",\n      "size": 1163,\n      "mtime_ns": 1789132198464879108\n    },\n    {\n      "relative_path": "minesim_discovery_cell377_tail_continuation_v1/cell/CELL_START.json",\n      "size": 565,\n      "mtime_ns": 1789132204176689824\n    },\n    {\n      "relative_path": "minesim_discovery_cell377_tail_continuation_v1/cell/COMMIT.json",\n      "size": 1162,\n      "mtime_ns": 1789132217096262897\n    },\n    {\n      "relative_path": "minesim_discovery_cell377_tail_continuation_v1/cell/RESOLVED_CONTEXT.json",\n      "size": 884,\n      "mtime_ns": 1789132204176689824\n    },\n    {\n      "relative_path": "minesim_discovery_cell377_tail_continuation_v1/cell/events.jsonl",\n      "size": 263767,\n      "mtime_ns": 1789132216756274111\n    },\n    {\n      "relative_path": "minesim_discovery_cell377_tail_continuation_v1/cell/metric_view.json",\n      "size": 191877,\n      "mtime_ns": 1789132216884269889\n    },\n    {\n      "relative_path": "minesim_discovery_cell377_tail_continuation_v1/cell/metrics.json",\n      "size": 4450,\n      "mtime_ns": 1789132216884269889\n    },\n    {\n      "relative_path": "minesim_discovery_cell377_tail_continuation_v1/cell/trace.json",\n      "size": 219533,\n      "mtime_ns": 1789132216768273716\n    },\n    {\n      "relative_path": "minesim_discovery_remaining390_parallel_v1.screen.log",\n      "size": 25131,\n      "mtime_ns": 1789127319322618977\n    },\n    {\n      "relative_path": "minesim_discovery_remaining390_parallel_v1.screen_rc.txt",\n      "size": 2,\n      "mtime_ns": 1789127319322618977\n    },\n    {\n      "relative_path": "minesim_discovery_remaining390_parallel_v1/AUTHORIZATION.json",\n      "size": 1623,\n      "mtime_ns": 1789125623265047802\n    },\n    {\n      "relative_path": "minesim_discovery_remaining390_parallel_v1/CAPTURE.json",\n      "size": 166,\n      "mtime_ns": 1789127311114835538\n    },\n    {\n      "relative_path": "minesim_discovery_remaining390_parallel_v1/CELL_LEASE.json",\n      "size": 12064,\n      "mtime_ns": 1789125623269047682\n    },\n    {\n      "relative_path": "minesim_discovery_remaining390_parallel_v1/COLLECTION_AUDIT.json",\n      "size": 82350,\n      "mtime_ns": 1789127310398854429\n    },\n    {\n      "relative_path": "minesim_discovery_remaining390_parallel_v1/MANIFEST.json",\n      "size": 425224,\n      "mtime_ns": 1789127311734819179\n    },\n    {\n      "relative_path": "minesim_discovery_remaining390_parallel_v1/POSTCHECK.json",\n      "size": 3121,\n      "mtime_ns": 1789127311110835643\n    },\n    {\n      "relative_path": "minesim_discovery_remaining390_parallel_v1/PREFLIGHT.json",\n      "size": 3416,\n      "mtime_ns": 1789125623261047923\n    },\n    {\n      "relative_path": "minesim_discovery_remaining390_parallel_v1/RC.txt",\n      "size": 2,\n      "mtime_ns": 1789127311118835432\n    },\n    {\n      "relative_path": "minesim_discovery_remaining390_parallel_v1/RESULT.json",\n      "size": 928,\n      "mtime_ns": 1789127311114835538\n    },\n    {\n      "relative_path": "minesim_discovery_remaining390_parallel_v1/SCHEDULE.json",\n      "size": 191368,\n      "mtime_ns": 1789125623273047561\n    },\n    {\n      "relative_path": "minesim_discovery_remaining390_parallel_v1/START.json",\n      "size": 292,\n      "mtime_ns": 1789125623277047441\n    },\n    {\n      "relative_path": "minesim_discovery_remaining390_parallel_v1/bundle/BOUNDARY.json",\n      "size": 427315,\n      "mtime_ns": 1789125623205049610\n    },\n    {\n      "relative_path": "minesim_discovery_remaining390_parallel_v1/bundle/MANIFEST.json",\n      "size": 10463,\n      "mtime_ns": 1789125623209049490\n    },\n    {\n      "relative_path": "minesim_discovery_remaining390_parallel_v1/bundle/PROTOCOL.json",\n      "size": 210021,\n      "mtime_ns": 1789125623209049490\n    },\n    {\n      "relative_path": "minesim_discovery_remaining390_parallel_v1/parallel/PHASE_RESULT.json",\n      "size": 185,\n      "mtime_ns": 1789127297591192397\n    },\n    {\n      "relative_path": "minesim_discovery_remaining390_parallel_v1/parallel/PROCESSES.json",\n      "size": 191480,\n      "mtime_ns": 1789125623301046718\n    },\n    {\n      "relative_path": "minesim_discovery_remaining390_parallel_v1/parallel/workers/worker_0/PROGRESS.jsonl",\n      "size": 17599,\n      "mtime_ns": 1789126808648144179\n    },\n    {\n      "relative_path": "minesim_discovery_remaining390_parallel_v1/parallel/workers/worker_0/RESULT.json",\n      "size": 3103,\n      "mtime_ns": 1789126808652144073\n    },\n    {\n      "relative_path": "minesim_discovery_remaining390_parallel_v1/parallel/workers/worker_0/START.json",\n      "size": 47718,\n      "mtime_ns": 1789125623613037315\n    },\n    {\n      "relative_path": "minesim_discovery_remaining390_parallel_v1/parallel/workers/worker_1/PROGRESS.jsonl",\n      "size": 17584,\n      "mtime_ns": 1789126755545559186\n    },\n    {\n      "relative_path": "minesim_discovery_remaining390_parallel_v1/parallel/workers/worker_1/RESULT.json",\n      "size": 3104,\n      "mtime_ns": 1789126755545559186\n    },\n    {\n      "relative_path": "minesim_discovery_remaining390_parallel_v1/parallel/workers/worker_1/START.json",\n      "size": 47718,\n      "mtime_ns": 1789125623781032253\n    },\n    {\n      "relative_path": "minesim_discovery_remaining390_parallel_v1/parallel/workers/worker_2/PROGRESS.jsonl",\n      "size": 17744,\n      "mtime_ns": 1789126725930349338\n    },\n    {\n      "relative_path": "minesim_discovery_remaining390_parallel_v1/parallel/workers/worker_2/RESULT.json",\n      "size": 3134,\n      "mtime_ns": 1789126725930349338\n    },\n    {\n      "relative_path": "minesim_discovery_remaining390_parallel_v1/parallel/workers/worker_2/START.json",\n      "size": 48207,\n      "mtime_ns": 1789125623829030806\n    },\n    {\n      "relative_path": "minesim_discovery_remaining390_parallel_v1/parallel/workers/worker_3/PROGRESS.jsonl",\n      "size": 17768,\n      "mtime_ns": 1789127297035207069\n    },\n    {\n      "relative_path": "minesim_discovery_remaining390_parallel_v1/parallel/workers/worker_3/RESULT.json",\n      "size": 3134,\n      "mtime_ns": 1789127297035207069\n    },\n    {\n      "relative_path": "minesim_discovery_remaining390_parallel_v1/parallel/workers/worker_3/START.json",\n      "size": 48207,\n      "mtime_ns": 1789125623809031408\n    },\n    {\n      "relative_path": "minesim_discovery_remaining390_parallel_v1/runner.py.txt",\n      "size": 1183244,\n      "mtime_ns": 1789125623261047923\n    }\n  ],\n  "archives_metadata_only": [\n    {\n      "relative_path": "minesim_discovery_remaining390_parallel_v1.zip",\n      "size": 85059607,\n      "mtime_ns": 1789127316646689579\n    },\n    {\n      "relative_path": "minesim_discovery_cell377_tail_continuation_v1.zip",\n      "size": 1131404,\n      "mtime_ns": 1789132217468250630\n    },\n    {\n      "relative_path": "minesim_confirmation768_parallel_v1.zip",\n      "size": 132348877,\n      "mtime_ns": 1789140744894539738\n    }\n  ],\n  "scope": "Copy only listed files. No filesystem search, archive expansion, experiment invocation, teacher generation, training, repair, resume or source mutation. Original full batch ZIPs are NOT included. Frozen candidate files are historical provenance, not certified confirmation labels."\n}\n'


def need(ok, reason):
    if not ok:
        raise RuntimeError(reason)


def now():
    return datetime.now(timezone.utc).isoformat()


def encode(obj):
    return (json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2,
                       allow_nan=False)+'\n').encode('utf-8')


def strict_json(raw):
    def pairs(items):
        out = {}
        for k, v in items:
            need(k not in out, 'DUPLICATE_JSON_KEY:'+k)
            out[k] = v
        return out
    def bad(x):
        raise ValueError('NONFINITE_JSON:'+x)
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=bad)


def safe_rel(name):
    need(isinstance(name, str) and name and '\\' not in name and '\x00' not in name,
         'INVALID_RELATIVE_PATH')
    p = PurePosixPath(name)
    need(bool(p.parts) and not p.is_absolute() and '..' not in p.parts and '.' not in p.parts and
         str(p) == name and ':' not in p.parts[0], 'UNSAFE_RELATIVE_PATH:'+name)
    return p.parts


def metadata(st):
    # atime can change because of reading; it is not a content-change indicator.
    return dict(size=st.st_size, dev=st.st_dev, inode=st.st_ino,
                mode=st.st_mode, mtime_ns=st.st_mtime_ns, ctime_ns=st.st_ctime_ns)


def open_ro(root, rel):
    parts = safe_rel(rel)
    fd = os.open(str(root), os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in parts[:-1]:
            nxt = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = nxt
        srcfd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
    finally:
        os.close(fd)
    if not stat.S_ISREG(os.fstat(srcfd).st_mode):
        os.close(srcfd)
        raise RuntimeError('NOT_REGULAR_SOURCE:'+rel)
    return os.fdopen(srcfd, 'rb')


def probe_metadata(root, rel):
    with open_ro(root, rel) as f:
        return metadata(os.fstat(f.fileno()))


def read_small(root, rel, cap=MAX_FILE):
    with open_ro(root, rel) as f:
        before = metadata(os.fstat(f.fileno()))
        need(before['size'] <= cap, 'SMALL_READ_LIMIT:'+rel)
        data = f.read(cap+1)
        need(len(data) == before['size'] and metadata(os.fstat(f.fileno())) == before,
             'SMALL_SOURCE_CHANGED:'+rel)
    need(probe_metadata(root, rel) == before, 'SMALL_SOURCE_REPLACED:'+rel)
    return data


def write_new(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as f:
        f.write(raw)
        f.flush()
        os.fsync(f.fileno())


def digest_stream(f, cap):
    h = hashlib.sha256()
    n = 0
    while True:
        b = f.read(min(MIB, cap-n+1))
        if not b:
            return {'size': n, 'sha256': h.hexdigest()}
        n += len(b)
        need(n <= cap, 'HASH_SIZE_LIMIT')
        h.update(b)


def digest_file(path, cap=64*MIB):
    need(path.is_file() and not path.is_symlink(), 'NOT_REGULAR_OUTPUT:'+str(path))
    with path.open('rb') as f:
        return digest_stream(f, cap)


def load_plan():
    raw = PLAN_TEXT.encode('utf-8')
    need(hashlib.sha256(raw).hexdigest() == PLAN_SHA256, 'EXPORT_PLAN_SHA')
    plan = strict_json(raw)
    need(plan['gate'] == GATE and len(plan['copy_files']) == 104, 'EXPORT_PLAN_SCOPE')
    need(len({r['relative_path'] for r in plan['copy_files']}) == 104, 'DUPLICATE_PLAN_PATH')
    for r in plan['copy_files'] + plan['archives_metadata_only']:
        safe_rel(r['relative_path'])
    need(sum(r['size'] for r in plan['copy_files']) < MAX_TOTAL, 'EXPORT_PLAN_SIZE')
    return plan


def copy_record(root, out, expected, remaining):
    rel = expected['relative_path']
    row = {'source_relative_path': rel, 'expected_from_inventory': expected,
           'archive_member': 'sources/data/'+rel}
    with open_ro(root, rel) as src:
        before = metadata(os.fstat(src.fileno()))
        need(before['size'] <= MAX_FILE and before['size'] <= remaining, 'COPY_SIZE_LIMIT:'+rel)
        need(shutil.disk_usage(out).free > before['size']+RESERVE, 'DISK_RESERVE')
        dest = out/row['archive_member']
        dest.parent.mkdir(parents=True, exist_ok=True)
        h, size = hashlib.sha256(), 0
        # Read only the size observed at open, not an unbounded growing file.
        with dest.open('xb') as dst:
            while size < before['size']:
                b = src.read(min(MIB, before['size']-size))
                if not b:
                    break
                dst.write(b)
                h.update(b)
                size += len(b)
            dst.flush()
            os.fsync(dst.fileno())
        after_fd = metadata(os.fstat(src.fileno()))
    after_path = probe_metadata(root, rel)
    row.update(source_before=before, source_after=after_path, size=size,
               sha256=h.hexdigest(), full_file=(size == before['size']),
               stable_during_read=(before == after_fd == after_path),
               matches_prior_inventory=all(before[k] == expected[k] for k in ('size','mtime_ns')))
    return row


def package(out):
    """Hash new copies only. Original sources and ZIPs are never rewritten."""
    pending, final = Path(str(out)+'.zip.pending'), Path(str(out)+'.zip')
    need(not os.path.lexists(pending) and not os.path.lexists(final), 'PACKAGE_EXISTS_NO_OVERWRITE')
    files = {}
    for p in sorted(out.rglob('*')):  # This is ONLY the new export directory.
        need(not p.is_symlink(), 'OUTPUT_SYMLINK')
        if p.is_file():
            files[p.relative_to(out).as_posix()] = digest_file(p)
    total = sum(r['size'] for r in files.values())
    need(total < 48*MIB, 'REPORT_TOTAL_LIMIT')
    need(shutil.disk_usage(out).free > 2*total+RESERVE, 'PACKAGE_DISK_GUARD')
    write_new(out/'EXPORT_MANIFEST.json', encode(files))
    with zipfile.ZipFile(pending, 'x', zipfile.ZIP_DEFLATED, compresslevel=1) as z:
        for rel in sorted(files):
            z.write(out/rel, rel)
        z.write(out/'EXPORT_MANIFEST.json', 'EXPORT_MANIFEST.json')
    with zipfile.ZipFile(pending) as z:
        need(len(z.namelist()) == len(set(z.namelist())), 'DUPLICATE_PACKAGE_MEMBER')
        need(set(z.namelist()) == set(files)|{'EXPORT_MANIFEST.json'}, 'PACKAGE_MEMBER_SET')
        for rel, expected in files.items():
            with z.open(rel) as f:
                need(digest_stream(f, expected['size']) == expected, 'PACKAGE_HASH:'+rel)
        need(strict_json(z.read('EXPORT_MANIFEST.json')) == files, 'PACKAGE_MANIFEST')
    # Exclusive publication, preserving the verified pending copy intentionally.
    with pending.open('rb') as src, final.open('xb') as dst:
        shutil.copyfileobj(src, dst, MIB)
        dst.flush()
        os.fsync(dst.fileno())
    d = digest_file(final)
    need(d == digest_file(pending), 'PUBLISHED_PACKAGE_HASH')
    write_new(out/'BUNDLE_COMPLETE.json', encode({'bundle': str(final), **d,
              'ZIP_VERIFIED': True, 'pending_retained_intentionally': True, 'at_utc': now()}))
    return final


def existing(out):
    print('EXISTING_EXPORT_NAMESPACE; NO_RECOLLECTION; NO_EXPERIMENT_ACTION', flush=True)
    try:
        need(out.is_dir() and not out.is_symlink(), 'EXISTING_EXPORT_DIRECTORY')
        d = strict_json(read_small(out, 'BUNDLE_COMPLETE.json'))
        final = Path(str(out)+'.zip')
        need(d['bundle'] == str(final) and digest_file(final) ==
             {'size': d['size'], 'sha256': d['sha256']}, 'EXISTING_BUNDLE_HASH')
        print('ZIP_VERIFIED=True\nBUNDLE='+str(final), flush=True)
    except Exception as exc:
        print('HOLD_EXISTING_EXPORT:'+str(exc)+'\nPRESERVE_DIRECTORY='+str(out), flush=True)
    return 2


def collect(root, plan, *, test_fixture=False):
    """Root/plan overrides are for local fixture tests, never exposed in cloud CLI."""
    root = Path(root)
    need(root.is_dir() and not root.is_symlink(), 'DATA_ROOT_MISSING_OR_SYMLINK')
    out = root/NAME
    if any(os.path.lexists(p) for p in (out, Path(str(out)+'.zip'), Path(str(out)+'.zip.pending'))):
        return existing(out)
    need(shutil.disk_usage(root).free > 3*MAX_TOTAL+RESERVE, 'EXPORT_DISK_GUARD')
    out.mkdir(mode=0o700)
    write_new(out/'EXPORT_PLAN.json', encode(plan))
    write_new(out/'REQUEST.json', encode({'gate': GATE, 'at_utc': now(),
              'test_fixture_only': test_fixture, 'experiments_run': 0, 'signals_sent': 0,
              'restart_resume_authorized': False, 'original_sources_modified': False}))
    if not test_fixture:
        write_new(out/'exporter_source.py', Path(__file__).read_bytes())
    rows, problems, archives, total, fatal = [], [], [], 0, None
    print('EXPORTING_LOCATED_RECORDS_ONLY; NO_SEARCH; NO_EXPERIMENT', flush=True)
    try:
        for i, expected in enumerate(plan['copy_files']):
            try:
                row = copy_record(root, out, expected, MAX_TOTAL-total)
                total += row['size']
                rows.append(row)
                if not all(row[k] for k in ('full_file','stable_during_read','matches_prior_inventory')):
                    problems.append({'path': expected['relative_path'], 'reason': 'PARTIAL_CHANGED_OR_DIFFERENT_FROM_INVENTORY'})
            except Exception as exc:
                problems.append({'path': expected['relative_path'], 'reason': type(exc).__name__+':'+str(exc)})
            if (i+1) % 20 == 0:
                print('FILES_PROCESSED=%d/%d' % (i+1, len(plan['copy_files'])), flush=True)
        for expected in plan['archives_metadata_only']:
            row = {'path': expected['relative_path'], 'full_archive_copied': False,
                   'full_archive_integrity': 'NOT_CHECKED_METADATA_ONLY'}
            try:
                actual = probe_metadata(root, expected['relative_path'])
                row.update(observed=actual, matches_prior_inventory=all(
                    actual[k] == expected[k] for k in ('size','mtime_ns')))
            except Exception as exc:
                row['error'] = type(exc).__name__+':'+str(exc)
            archives.append(row)
    except BaseException as exc:
        fatal = {'type': type(exc).__name__, 'reason': str(exc), 'traceback': traceback.format_exc()}
    for row in rows:
        try:
            row['stable_through_capture'] = (probe_metadata(root, row['source_relative_path']) == row['source_after'])
        except Exception as exc:
            row['stable_through_capture'] = False
            row['postcheck_error'] = str(exc)
        if not row['stable_through_capture']:
            problems.append({'path': row['source_relative_path'], 'reason': 'SOURCE_POSTCHECK_CHANGED'})
    ok = fatal is None and not problems and len(rows) == len(plan['copy_files'])
    result = {'gate': GATE, 'status': 'PASS_LOCATED_RECORDS_EXPORTED_ONLY' if ok else 'HOLD_PARTIAL_EXPORT',
              'at_utc': now(), 'expected_files': len(plan['copy_files']), 'copied_files': len(rows),
              'copied_bytes': total, 'issues': problems, 'fatal': fatal,
              'experiments_run': 0, 'signals_sent': 0, 'training_run': False,
              'restart_resume_authorized': False, 'scientific_success_certified': False,
              'original_manifest_validation': 'NOT_PERFORMED_RAW_MANIFESTS_PRESERVED_FOR_REVIEW',
              'scope': 'Selective evidence copies only, not a replacement for full batch archives. Frozen candidate files retain their historical role; no labels are recomputed or approved.'}
    write_new(out/'SOURCE_CAPTURE_MANIFEST.json', encode(rows))
    write_new(out/'ARCHIVES_METADATA_ONLY.json', encode(archives))
    write_new(out/'RESULT.json', encode(result))
    write_new(out/'RC.txt', b'0\n' if ok else b'2\n')
    write_new(out/'README.txt', b'Read-only export of exactly listed old records. No original data or code executed/modified.\nOnly this export namespace was created. No restart or scientific-success authorization.\nFull batch ZIPs NOT copied. Original manifests are preserved verbatim, not regenerated.\nThe .zip.pending duplicate is retained intentionally. Upload BUNDLE only.\n')
    final = package(out)
    print('EXPORT_STATUS='+result['status'], flush=True)
    print('COPIED_FILES=%d/%d' % (len(rows), len(plan['copy_files'])), flush=True)
    print('EXPERIMENTS_RUN=0\nSIGNALS_SENT=0\nZIP_VERIFIED=True\nBUNDLE='+str(final), flush=True)
    return 0 if ok else 2


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--collect-readonly', action='store_true')
    args = ap.parse_args()
    if not args.collect_readonly:
        print('NO_ACTION; use --collect-readonly')
        return 2
    need(Path.cwd().resolve() == REPO.resolve(), 'CWD_NOT_FORMAL_REPO')
    need(os.environ.get('CONDA_DEFAULT_ENV') == 'minesim', 'CONDA_ENV')
    need(Path(sys.prefix).resolve() == PREFIX.resolve(), 'PYTHON_PREFIX')
    need(sys.version_info[:2] >= (3,9), 'PYTHON39_OR_NEWER_REQUIRED')
    need(os.environ.get('CUDA_VISIBLE_DEVICES') == '', 'GPU_MUST_BE_DISABLED')
    return collect(DATA, load_plan())


if __name__ == '__main__':
    try:
        rc = main()
    except (Exception, KeyboardInterrupt) as exc:
        print('HOLD_EXPORT:'+type(exc).__name__+':'+str(exc), flush=True)
        traceback.print_exc()
        print('PRESERVE_EXPORT_DIRECTORY_AND_PENDING; NO_AUTO_RETRY_OR_EXPERIMENT_ACTION', flush=True)
        rc = 2
    raise SystemExit(rc)
