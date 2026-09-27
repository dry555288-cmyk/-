#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import random
import re
import shutil
import subprocess
import sys
import time
import traceback
from dataclasses import replace

REPO = Path('/root/MineSim-Dynamic')
TMP = Path('/root/autodl-tmp')
BUNDLE = Path(__file__).resolve().parent
RUNTIME_OVERLAY = BUNDLE / 'runtime_overlay'
FROZEN_INPUTS = BUNDLE / 'frozen_inputs'

RELEASE = TMP / 'minesim_h8_guide_eager_vs_lazy_full_v1_retry2_review' / 'evidence' / 'release'
ORIGINAL_RUNTIME = RELEASE / 'parent' / 'base' / 'parent' / 'core' / 'parent' / 'parent' / 'core' / 'parent' / 'core' / 'parent' / 'runtime'
DEADLOCK_OVERLAY_RUNTIME = TMP / 'minesim_g1_deadlock_terminal_runtime_overlay_v1' / 'runtime'
G1_FREEZE = TMP / 'minesim_g1_final_freeze_v1' / 'G1_FINAL_FREEZE.json'
OLD_G2_OUT = TMP / 'minesim_g2_formal_calibration_v1'
OUT = TMP / 'minesim_g2_formal_calibration_v2'
CELLS = OUT / 'cells'

EXPECTED_HEAD = '112d2bd0f3412fc83b13d5587d2b41402d2d0f5e'
EXPECTED_G1_SHA = '5629cfd987bfd9ebe832c389464de1cad1e4678c5119ccdfa6087ff96ac65b31'
EXPECTED_ROOTS_SHA = '93b68da12484a44961d7e36d19e0b19fe76ed569c136d028bcdc80f51f9878b3'
EXPECTED_FULL_EVAL_SHA = 'a3349060c6ed4570802aa77c450f05f2392e81308a1222a16c8c3a433b340076'
EXPECTED_MAP_SHA = 'b85a3d8b28f2252ecb5bda179d514573f6333079def838cd048566f556d95cd0'
EXPECTED_DRIVABLE_TOKEN_SHA = 'de78b0bdd63a41b9222bc0bf5ba8b343c46eacf751de8d5106308b58a5ec4e21'
MAP_BASENAME = 'geojson_full_mine_vector_v2_dev_semantic_map.json'
MAP_ROOT = Path('/root/datasets/maps')
MAP_LOCATION = 'geojson_full_mine_vector_v2_dev'
EXPECTED_MAP_VERSION = 'dev-geojson-full-mine-vector-v2'
EXPECTED_MAP_LOADER_SHA = '41872d1e568cd1a68bc2c2997d7dfc3c7db93d3ef0e1959597d891902049ff34'
DRIVABLE_LAYERS = ('road', 'intersection', 'loading_area', 'unloading_area')
RUNNER_CONTRACT_VERSION = 'G2_FORMAL_CALIBRATION_V2_R2_PRODUCTION_MAP_BINDING'

EXPECTED_DEADLOCK_SOURCE_SHA = {
    '__init__.py': '7d35678f99c3e6c37e62b6bb9d91cc6f7be616d2c1a5a9d0fc164137eb8172cd',
    'action_space.py': '03ccff1923f0ed19de4765d2329489d505cfc68bfbeb0335e575cf1519953633',
    'deadlock_runtime_v1.py': 'bb6ffdb9d7f71473bb65523250ea91f3c02d676eca3549abf50eb0ce2b833d89',
    'dual_stop_adapter_v1.py': '0338011ac51f7461bb23c41ff3959777da311cba9081b4ab059df5da59a4e862',
    'dual_stop_motion_v1.py': 'e9d024a6f56b6279de41b6f0889a188a201eeef07acca425e2ea69c4ef9c0626',
    'fleet_collision.py': '41e1707c626c1f9e80ad28a46484fd984ebf5677d42c3c3cd9709688a11ef076',
    'fleet_node.py': 'a9156322e4dface34a2ab91f08404ccbe231f18d0d9c9e16e560aa266fc4617b',
    'fleet_reward.py': 'df7d4be76df69bf022e1a9465d9b9a87de20a092b32707ffc8ad4356cb364590',
    'fleet_search.py': '301945209729938eba6678c13f342e0e9ef1fee5db67664642937b030789df31',
    'fleet_state.py': '1b7efe18e2a77e96a9beb94070500ff811dd584754c03d57cb1e2e8a985c9d21',
    'fleet_transition.py': '006cd1ba4f64c5780da0bfb8de0b48555cb385655ed929b7c9d9fd269d4d77a2',
    'joint_action.py': '918f5e6e90631d28cdf6b6f8bdefb38d572c402a983b4cb622340408a968854e',
    'reward.py': 'd225ca754b2e5f6a650a35a946819276d50c027eaf66449667973c45f98ed5a5',
    'state.py': 'd0b7ab348ac02181eefc2481309945b3c281f8216df3667ff75d2ea03ae4d409',
    'transition_model.py': '9971189f68c64978b406482f2dde326cae774948a4fde025aae26dc0af64cb0c',
}
EXPECTED_REALROUTE_SMOKE_SHA = '568479648e506d80b0a06d74e2a56b75677c92b6e010d9a98219042b461ea225'
EXPECTED_RUNTIME_SUPPORT_SHA = {
    'reference_paths.json': '5a8bd32d831b7d75cc90e8db45ac9d0880dcfe10bf5c5f0db93a8a31fb0e306f',
    'definitions/frozen_codec.py': 'e5edc00e93003e834c71258d1561affbebfbde55e5637f0574ed5399247c0b43',
    'definitions/route_helpers.py': '1c10c16b8056ccd25a27cb8a12078d55d20e2457152df7361c3856ca96b0246c',
    'engine/devkit/sim_engine/planning/planner/mcts/geometry_transition_model.py': '8ac6513912c18e761426f86d532ee89774075e0f0e9d2f6bb8aa759e7960976d',
}
EXPECTED_V2R_SOURCE_SHA = {
    TMP / 'minesim_g1_exact_tick_geometry_v1' / 'g1_exact_geometry_overlay_v1.py': 'fb2896b21c872c12db6e4fad2d0fe97b71a4a553e70b5df157b6cae41ea9e81a',
    TMP / 'minesim_g1_v2r_state_contract_v1' / 'g1_v2r_state_contract_v1.py': 'ea8ddb7c9068f846660e5016952335ec055b09440e139feec2f19d6a0c59bcf7',
    TMP / 'minesim_g1_v2r_transition_overlay_v1' / 'g1_v2r_transition_overlay_v1.py': '2a3ec5377306d55ea45460a3a2938babbaf64675673b53e1f83f43d7cf6546bd',
}

BUDGETS = [4, 8, 16, 32, 64]
DEPTHS = [4, 8, 16]
GAMMA = 0.99
C_UCT = 1.4
MAX_OUTER_STEPS = 128
REPLICATES = [0]  # Stage-A coarse screen only. G2 final freeze still requires later confirmation.

DECISION_WALL_NS = 400_000_000
WORK_CUTOFF_NS = 380_000_000
RETURN_RESERVE_NS = 20_000_000

PROGRESS_CAP = 1.0
TIME_COST = -0.05
WAIT_COST_FULL = -0.10
OLD_EFFECTIVE_FIRST_GOAL = 15.0
NEW_FIRST_GOAL = 5.0
GLOBAL_BOTH_PARKED = 20.0


def need(cond, msg):
    if not cond:
        raise RuntimeError(msg)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def sh(*args, cwd=None):
    p = subprocess.run(list(args), cwd=str(cwd) if cwd else None,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       text=True, check=True)
    return p.stdout.strip()


def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode('utf-8')


def objsha(obj) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def atomic_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + '\n').encode('utf-8')
    tmp = path.with_suffix(path.suffix + '.tmp')
    with tmp.open('wb') as f:
        f.write(raw); f.flush(); os.fsync(f.fileno())
    os.replace(str(tmp), str(path))


def atomic_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    with tmp.open('w', encoding='utf-8', newline='\n') as f:
        f.write(text); f.flush(); os.fsync(f.fileno())
    os.replace(str(tmp), str(path))


def repo_precheck():
    for p, label in [(REPO, 'REPO'), (RELEASE, 'RELEASE'), (ORIGINAL_RUNTIME, 'ORIGINAL_RUNTIME'),
                     (DEADLOCK_OVERLAY_RUNTIME, 'DEADLOCK_OVERLAY_RUNTIME')]:
        need(p.is_dir(), label + '_MISSING:' + str(p))
    need(G1_FREEZE.is_file(), 'G1_FREEZE_MISSING')
    need(sha256(G1_FREEZE) == EXPECTED_G1_SHA, 'G1_FREEZE_SHA_DRIFT:' + sha256(G1_FREEZE))
    g1 = load_json(G1_FREEZE)
    need(g1.get('g1_status') == 'PASS_FROZEN', 'G1_NOT_FROZEN')
    need(g1.get('holdout_used') is False, 'HOLDOUT_ALREADY_USED')
    need(g1.get('head') == EXPECTED_HEAD, 'G1_HEAD_BINDING_DRIFT')
    need(g1.get('map_sha256') == EXPECTED_MAP_SHA, 'G1_MAP_BINDING_DRIFT')
    need(g1.get('drivable_token_set_sha256') == EXPECTED_DRIVABLE_TOKEN_SHA, 'G1_DRIVABLE_BINDING_DRIFT')

    head = sh('git', 'rev-parse', 'HEAD', cwd=REPO)
    status = [x for x in sh('git', 'status', '--porcelain=v1', cwd=REPO).splitlines() if x.strip()]
    need(head == EXPECTED_HEAD, 'HEAD_DRIFT:' + head)
    need(not [x for x in status if not x.startswith('?? ')], 'TRACKED_REPO_DIRTY:' + repr(status))
    unexpected = [x for x in status if x != '?? ^C']
    need(not unexpected, 'UNEXPECTED_UNTRACKED:' + repr(unexpected))

    need(sha256(RELEASE / 'ROOTS.json') == EXPECTED_ROOTS_SHA, 'ROOTS_SHA_DRIFT')
    need(sha256(RELEASE / 'parent' / 'full_eval.py') == EXPECTED_FULL_EVAL_SHA, 'FULL_EVAL_SHA_DRIFT')

    map_loader_live = REPO / 'devkit' / 'sim_engine' / 'map_manager' / 'minesim_map_data' / 'minesim_semanticmap_json_loader.py'
    need(map_loader_live.is_file(), 'PRODUCTION_MAP_LOADER_MISSING:' + str(map_loader_live))
    need(sha256(map_loader_live) == EXPECTED_MAP_LOADER_SHA,
         'PRODUCTION_MAP_LOADER_SHA_DRIFT:' + sha256(map_loader_live))
    map_path = MAP_ROOT / 'semantic_map' / MAP_BASENAME
    need(map_path.is_file(), 'FROZEN_SEMANTIC_MAP_MISSING:' + str(map_path))
    need(sha256(map_path) == EXPECTED_MAP_SHA, 'FROZEN_SEMANTIC_MAP_SHA_DRIFT:' + sha256(map_path))

    # The previously prepared V1 is allowed; scientific cells are not.
    old_cells = OLD_G2_OUT / 'cells'
    if old_cells.exists():
        existing = list(old_cells.glob('*.json'))
        need(not existing, 'OLD_G2_V1_SCIENTIFIC_CELLS_PRESENT:' + str(len(existing)))

    for name, expected in EXPECTED_DEADLOCK_SOURCE_SHA.items():
        p = DEADLOCK_OVERLAY_RUNTIME / 'candidate_mcts' / name
        need(p.is_file(), 'DEADLOCK_SOURCE_MISSING:' + str(p))
        need(sha256(p) == expected, 'DEADLOCK_SOURCE_SHA_DRIFT:' + name)
    for p, expected in EXPECTED_V2R_SOURCE_SHA.items():
        need(p.is_file(), 'V2R_SOURCE_MISSING:' + str(p))
        need(sha256(p) == expected, 'V2R_SOURCE_SHA_DRIFT:' + p.name)

    # The bundle carries the reviewed overlay bytes too; verify them before import.
    for name, expected in EXPECTED_DEADLOCK_SOURCE_SHA.items():
        bp = RUNTIME_OVERLAY / 'candidate_mcts' / name
        need(bp.is_file(), 'BUNDLED_DEADLOCK_SOURCE_MISSING:' + str(bp))
        need(sha256(bp) == expected, 'BUNDLED_DEADLOCK_SOURCE_SHA_DRIFT:' + name)
    bundled_v2r = {
        RUNTIME_OVERLAY / 'g1_exact_geometry_overlay_v1.py': EXPECTED_V2R_SOURCE_SHA[TMP / 'minesim_g1_exact_tick_geometry_v1' / 'g1_exact_geometry_overlay_v1.py'],
        RUNTIME_OVERLAY / 'g1_v2r_state_contract_v1.py': EXPECTED_V2R_SOURCE_SHA[TMP / 'minesim_g1_v2r_state_contract_v1' / 'g1_v2r_state_contract_v1.py'],
        RUNTIME_OVERLAY / 'g1_v2r_transition_overlay_v1.py': EXPECTED_V2R_SOURCE_SHA[TMP / 'minesim_g1_v2r_transition_overlay_v1' / 'g1_v2r_transition_overlay_v1.py'],
    }
    for bp, expected in bundled_v2r.items():
        need(bp.is_file(), 'BUNDLED_V2R_SOURCE_MISSING:' + str(bp))
        need(sha256(bp) == expected, 'BUNDLED_V2R_SOURCE_SHA_DRIFT:' + bp.name)
    native_smoke = ORIGINAL_RUNTIME / 'realroute_smoke.py'
    need(native_smoke.is_file(), 'REALROUTE_SMOKE_MISSING')
    need(sha256(native_smoke) == EXPECTED_REALROUTE_SMOKE_SHA,
         'REALROUTE_SMOKE_SHA_DRIFT:' + sha256(native_smoke))
    for rel, expected in EXPECTED_RUNTIME_SUPPORT_SHA.items():
        sp = ORIGINAL_RUNTIME / rel
        need(sp.is_file(), 'RUNTIME_SUPPORT_MISSING:' + rel)
        need(sha256(sp) == expected, 'RUNTIME_SUPPORT_SHA_DRIFT:' + rel)

    return head, status, g1


def activate_runtime():
    sys.dont_write_bytecode = True
    for p in (RUNTIME_OVERLAY, ORIGINAL_RUNTIME, ORIGINAL_RUNTIME / 'engine'):
        s = str(p)
        if s not in sys.path:
            sys.path.insert(0, s)

    import realroute_smoke as native
    # Use the already-PASS deadlock runtime. The bundled copy is evidence and code review source;
    # the live overlay is SHA-bound above.
    native.activate_package(DEADLOCK_OVERLAY_RUNTIME)

    # Make V2R modules from this immutable bundle importable after candidate_mcts activation.
    s = str(RUNTIME_OVERLAY)
    if s not in sys.path:
        sys.path.insert(0, s)

    from candidate_mcts.dual_stop_adapter_v1 import action_id, episode_status
    from candidate_mcts.fleet_search import FleetMCTSSearch, _joint_action_key, _joint_action_id
    from candidate_mcts.fleet_node import FleetMCTSNode
    from g1_exact_geometry_overlay_v1 import ExactRouteGeometryProvider
    from g1_v2r_state_contract_v1 import G1SafetyFleetStateV1
    from g1_v2r_transition_overlay_v1 import G1V2RExactDualStopFleetTransition

    return dict(native=native, action_id=action_id, episode_status=episode_status,
                FleetMCTSSearch=FleetMCTSSearch, FleetMCTSNode=FleetMCTSNode,
                joint_key=_joint_action_key, joint_id=_joint_action_id,
                ExactRouteGeometryProvider=ExactRouteGeometryProvider,
                G1SafetyFleetStateV1=G1SafetyFleetStateV1,
                G1V2RExactDualStopFleetTransition=G1V2RExactDualStopFleetTransition)


def _load_production_semantic_map_loader():
    """Use the production MineSim semantic-map loader, not a guessed GeoJSON parser."""
    import importlib
    import importlib.util

    module = None
    try:
        module = importlib.import_module(
            'devkit.sim_engine.map_manager.minesim_map_data.minesim_semanticmap_json_loader'
        )
        module_path = Path(module.__file__).resolve()
        if sha256(module_path) != EXPECTED_MAP_LOADER_SHA:
            module = None
    except Exception:
        module = None

    if module is None:
        # The frozen runtime's engine may intentionally be minimal. Load the byte-bound
        # production loader source from the checked-out repository under a private name;
        # its devkit imports still resolve against the already activated frozen engine.
        module_path = REPO / 'devkit' / 'sim_engine' / 'map_manager' / 'minesim_map_data' / 'minesim_semanticmap_json_loader.py'
        need(module_path.is_file(), 'PRODUCTION_MAP_LOADER_MISSING:' + str(module_path))
        need(sha256(module_path) == EXPECTED_MAP_LOADER_SHA,
             'PRODUCTION_MAP_LOADER_SHA_DRIFT:' + sha256(module_path))
        spec = importlib.util.spec_from_file_location('g2_production_semantic_map_loader', str(module_path))
        need(spec is not None and spec.loader is not None, 'PRODUCTION_MAP_LOADER_SPEC')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

    module_path = Path(module.__file__).resolve()
    need(sha256(module_path) == EXPECTED_MAP_LOADER_SHA,
         'ACTIVE_MAP_LOADER_SHA_DRIFT:' + sha256(module_path))
    cls = getattr(module, 'MineSimSemanticMapJsonLoader', None)
    need(cls is not None, 'PRODUCTION_MAP_LOADER_CLASS_MISSING')
    return cls, module_path


def _legacy_token_hash_diagnostics(tokens, binding_records):
    """Try common serializations for diagnosis only; legacy script bytes no longer exist.

    Identity is instead bound by the byte-identical map SHA + production loader SHA +
    exact frozen four-layer rule + 178 unique linked polygons + 29 union components +
    route endpoint containment. Never claim the old token hash was reproduced unless it is.
    """
    expected = EXPECTED_DRIVABLE_TOKEN_SHA
    rows = sorted(tokens)
    by_layer = {layer: [] for layer in DRIVABLE_LAYERS}
    for rec in binding_records:
        by_layer[rec['layer']].append(rec['polygon_token'])
    for layer in by_layer:
        by_layer[layer] = sorted(by_layer[layer])
    objects = {
        'sorted_polygon_tokens': rows,
        'tokens_object': {'tokens': rows},
        'layer_to_polygon_tokens': by_layer,
        'binding_records_sorted': sorted(binding_records, key=lambda x: (x['layer'], x['layer_token'], x['polygon_token'])),
    }
    hashes = {}
    for name, obj in objects.items():
        raw = json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')
        hashes[name] = hashlib.sha256(raw).hexdigest()
        hashes[name + '_newline'] = hashlib.sha256(raw + b'\n').hexdigest()
    matches = sorted(k for k, v in hashes.items() if v == expected)
    return hashes, matches


def build_drivable_domain():
    from shapely.ops import unary_union

    map_path = MAP_ROOT / 'semantic_map' / MAP_BASENAME
    need(map_path.is_file(), 'FROZEN_SEMANTIC_MAP_MISSING:' + str(map_path))
    need(sha256(map_path) == EXPECTED_MAP_SHA, 'MAP_SHA_DRIFT:' + sha256(map_path))

    Loader, loader_path = _load_production_semantic_map_loader()
    loader = Loader(map_root=str(MAP_ROOT), location=MAP_LOCATION)
    need(getattr(loader, 'map_version', None) == EXPECTED_MAP_VERSION,
         'MAP_VERSION_DRIFT:' + repr(getattr(loader, 'map_version', None)))

    geoms = []
    tokens = []
    binding_records = []
    category_counts = {}
    for layer in DRIVABLE_LAYERS:
        records = getattr(loader, layer, None)
        need(isinstance(records, list) and records, 'DRIVABLE_LAYER_MISSING_OR_EMPTY:' + layer)
        category_counts[layer] = len(records)
        for rec in records:
            need(isinstance(rec, dict), 'DRIVABLE_LAYER_RECORD_TYPE:' + layer)
            layer_token = rec.get('token')
            polygon_token = rec.get('link_polygon_token')
            need(isinstance(layer_token, str) and layer_token, 'DRIVABLE_LAYER_TOKEN:' + layer)
            need(isinstance(polygon_token, str) and polygon_token, 'DRIVABLE_LINK_POLYGON_TOKEN:' + layer)
            need(polygon_token in loader.token2ind.get('polygon', {}),
                 'DRIVABLE_POLYGON_TOKEN_NOT_IN_GEOMETRIC_LAYER:' + polygon_token)
            geom = loader.extract_polygon(polygon_token)
            need(hasattr(geom, 'is_empty') and not geom.is_empty and geom.is_valid,
                 'INVALID_DRIVABLE_POLYGON:' + polygon_token)
            geoms.append(geom)
            tokens.append(polygon_token)
            binding_records.append({'layer': layer, 'layer_token': layer_token, 'polygon_token': polygon_token})

    need(sum(category_counts.values()) == 178,
         'DRIVABLE_LAYER_RECORD_COUNT:' + str(sum(category_counts.values())) + ':' + repr(category_counts))
    need(len(tokens) == 178,
         'DRIVABLE_LINKED_POLYGON_RECORD_COUNT:' + str(len(tokens)))

    domain = unary_union(geoms)
    need(not domain.is_empty and domain.is_valid, 'DRIVABLE_UNION_INVALID')
    need(domain.geom_type == 'MultiPolygon', 'DRIVABLE_UNION_NOT_MULTIPOLYGON:' + domain.geom_type)
    components = len(domain.geoms)
    need(components == 29, 'DRIVABLE_COMPONENT_COUNT:' + str(components))

    # New explicit G2 fingerprint. This is not substituted for the historical G1 hash;
    # it binds exactly what this runner loaded from the immutable semantic map.
    g2_binding = {
        'schema': 'G2_DRIVABLE_DOMAIN_PRODUCTION_BINDING_V1',
        'map_sha256': EXPECTED_MAP_SHA,
        'map_loader_sha256': EXPECTED_MAP_LOADER_SHA,
        'map_location': MAP_LOCATION,
        'layers': list(DRIVABLE_LAYERS),
        'records': binding_records,
    }
    g2_binding_sha = objsha(g2_binding)
    legacy_hashes, legacy_matches = _legacy_token_hash_diagnostics(tokens, binding_records)

    return domain, {
        'binding_schema': 'G2_DRIVABLE_DOMAIN_PRODUCTION_BINDING_V1',
        'map_path': str(map_path),
        'map_sha256': sha256(map_path),
        'map_version': loader.map_version,
        'production_loader_path': str(loader_path),
        'production_loader_sha256': sha256(loader_path),
        'frozen_layers': list(DRIVABLE_LAYERS),
        'category_counts': category_counts,
        'selected_polygon_count': len(tokens),
        'unique_polygon_count': len(set(tokens)),
        'union_geom_type': domain.geom_type,
        'union_components': components,
        'g2_domain_binding_sha256': g2_binding_sha,
        'legacy_g1_token_set_sha256': EXPECTED_DRIVABLE_TOKEN_SHA,
        'legacy_token_hash_reproduction_matches': legacy_matches,
        'legacy_token_hash_candidates': legacy_hashes,
        'legacy_hash_note': (
            'REPRODUCED' if legacy_matches else
            'NOT_REDERIVED_BECAUSE_ORIGINAL_G1_DOMAIN_STAGE_SCRIPT_BYTES_ARE_NOT_PRESENT;IDENTITY_IS_BOUND_BY_EXACT_MAP_SHA+PRODUCTION_LOADER_SHA+FOUR_LAYER_RULE+178_LINKED_POLYGON_RECORDS+29_COMPONENTS+ROUTE_ENDPOINT_CHECKS'
        ),
        'selected_tokens': sorted(tokens),
    }

def load_roots():
    roots = load_json(RELEASE / 'ROOTS.json')
    need(isinstance(roots, list) and len(roots) == 4, 'EXPECTED_FOUR_G2A_ROOTS')
    need(all(r.get('task', {}).get('scene') == 'C11' for r in roots), 'G2A_ROOTS_NOT_ALL_C11')
    need(all(r.get('task', {}).get('episode_uid', '').startswith('C11_') for r in roots), 'G2A_EPISODE_LINEAGE')
    return roots


def build_exact_providers(api, bc):
    from devkit.common.actor_state.state_representation import StateSE2
    from devkit.common.actor_state.vehicle_parameters import get_mine_truck_parameters
    from devkit.common.actor_state.car_footprint import CarFootprint

    params = get_mine_truck_parameters(bc.context['vehicle_location'])
    need((float(params.length), float(params.width), float(params.rear_axle_to_center)) == (9.0, 4.0, 2.0),
         'FOOTPRINT_CONFIG_CHANGED')
    providers = {}
    for token in ('A', 'B'):
        pose = bc.context['rear_start_pose'][token]
        car = CarFootprint.build_from_rear_axle(StateSE2(float(pose['x']), float(pose['y']), float(pose['yaw'])), params)
        providers[token] = api['ExactRouteGeometryProvider'](bc.paths[token], car)
    return providers


def verify_root_origin(root):
    source_path = RELEASE / root['source_step']
    need(source_path.is_file(), 'ROOT_SOURCE_STEP_MISSING:' + str(source_path))
    raw = source_path.read_bytes()
    need(len(raw) == root['source_size'], 'ROOT_SOURCE_SIZE')
    need(hashlib.sha256(raw).hexdigest() == root['source_sha256'], 'ROOT_SOURCE_SHA')
    hist = json.loads(raw)
    need(hist['step'] == root['source_step_index_0based'], 'ROOT_SOURCE_STEP_INDEX')
    need(hist['before'] == root['state'], 'ROOT_SOURCE_BEFORE_STATE')
    need(bool(root.get('exact_before_state_sha256')), 'ROOT_EXACT_STATE_SHA_MISSING')


def build_context(api, root, drivable_domain):
    native = api['native']
    context_path = ORIGINAL_RUNTIME / 'inputs' / 'contexts' / (root['task']['episode_uid'] + '.json')
    need(context_path.is_file(), 'CONTEXT_MISSING:' + str(context_path))
    counters = dict(candidate_fleet_calls_including_tree_attempted=0,
                    candidate_fleet_calls_including_tree_returned=0)
    bc = native.BoundContext(ORIGINAL_RUNTIME, load_json(context_path), counters=counters)
    verify_root_origin(root)

    base = bc.transition.unpack(root['state'])
    need(canonical(bc.transition.pack(base)) == canonical(root['state']), 'ROOT_ROUNDTRIP')
    g1state = api['G1SafetyFleetStateV1'].from_fleet_state(base)
    providers = build_exact_providers(api, bc)
    tr = api['G1V2RExactDualStopFleetTransition'](
        bc.transition._vehicle_transitions,
        bc.transition._route_geometry_caches,
        exact_geometry_providers=providers,
        drivable_domain=drivable_domain,
        external_tokens=(), confirmed_dual_only=True,
        internal_collision_sample_dt_s=bc.transition.internal_collision_sample_dt_s,
        internal_safety_margin_m=bc.transition.internal_safety_margin_m,
    )
    state = tr.bind_initial_geometry(g1state)
    need(not state.hard_safety_violation, 'G2A_ROOT_HARD_UNDER_FROZEN_G1:' + root['root_id'])
    packed = tr.pack(state)
    need(canonical(tr.pack(tr.unpack(packed))) == canonical(packed), 'G1_V2R_CODEC_ROUNDTRIP')
    active_ids = [api['action_id'](a) for a in tr.active_joint_actions(state)]
    need(active_ids == root['expected_action_ids'], 'G2A_ROOT_ACTION_DOMAIN_DRIFT:' + root['root_id'])

    # Re-check the exact provider endpoints against the same frozen domain.
    for token, provider in providers.items():
        need(drivable_domain.covers(provider.geometry_at(provider._start_progress)), 'ROUTE_START_V2R:' + token)
        need(drivable_domain.covers(provider.geometry_at(provider._end_progress)), 'ROUTE_END_V2R:' + token)

    return bc, tr, state, providers, counters


def assert_base_reward_contract(base):
    need(hasattr(base, '_vehicle_rewards') and set(base._vehicle_rewards) == {'A', 'B'}, 'BASE_REWARD_MODELS')
    for token, model in base._vehicle_rewards.items():
        cfg = model.cfg
        expected = dict(w_progress=1.0, w_speed=0.3, w_safety=2.0, w_clearance=0.0,
                        w_comfort=0.3, collision_penalty=100.0, goal_bonus=30.0,
                        ttc_safe_s=3.0, clearance_safe_m=3.0)
        for key, value in expected.items():
            need(float(getattr(cfg, key)) == value, 'BASE_REWARD_CFG_DRIFT:%s:%s' % (token, key))
    need(float(base.internal_clearance_safe_m) == 3.0, 'BASE_INTERNAL_CLEARANCE_SAFE_DRIFT')
    need(float(base.w_internal_clearance) == 0.5, 'BASE_INTERNAL_CLEARANCE_WEIGHT_DRIFT')


class G1RewardContract:
    def __init__(self, base):
        assert_base_reward_contract(base)
        self.base = base
        self._terminal_predicate = None

    def set_terminal_predicate(self, predicate):
        self._terminal_predicate = predicate
        if hasattr(self.base, 'set_terminal_predicate'):
            self.base.set_terminal_predicate(predicate)

    def is_terminal(self, state, depth, max_depth):
        if self.base.is_terminal(state, depth, max_depth):
            return True
        return bool(self._terminal_predicate and self._terminal_predicate(state))

    @staticmethod
    def _tokens(state):
        return tuple(state.controlled_tokens)

    def _first_goal_count(self, prev, nxt):
        return sum(1 for t in self._tokens(prev)
                   if (not prev.state_for(t).goal_reached and nxt.state_for(t).goal_reached))

    def _progress_excess(self, prev, nxt):
        count = len(self._tokens(prev)); total = 0.0
        for token in self._tokens(prev):
            pv, nv = prev.state_for(token), nxt.state_for(token)
            if pv.goal_reached:
                continue
            denom = max(float(pv.target_speed_mps) * 0.5, 1e-6)
            raw = max(0.0, float(nv.route_s) - float(pv.route_s)) / denom
            total += max(0.0, raw - PROGRESS_CAP)
        return total / count

    def _stationary_unfinished_fraction(self, state):
        unfinished = [state.state_for(t) for t in self._tokens(state) if not state.state_for(t).goal_reached]
        if not unfinished:
            return 0.0
        stationary = sum(1 for s in unfinished if abs(float(s.speed_mps)) <= 1e-12)
        return stationary / len(unfinished)

    def evaluate(self, prev, nxt):
        value = float(self.base.evaluate(prev, nxt))
        value -= self._progress_excess(prev, nxt)
        first = self._first_goal_count(prev, nxt)
        if first:
            value -= first * OLD_EFFECTIVE_FIRST_GOAL
            value += first * NEW_FIRST_GOAL
        hard = bool(nxt.hard_safety_violation)
        deadlock = bool(self._terminal_predicate and self._terminal_predicate(nxt)) if (not hard and not nxt.all_goals_reached) else False
        if (not prev.all_goals_reached) and nxt.all_goals_reached and not hard:
            value += GLOBAL_BOTH_PARKED
        # Frozen G1 wording: nonterminal outer step only. Deadlock terminal gets no time/wait increment.
        if (not hard) and (not nxt.all_goals_reached) and (not deadlock):
            value += TIME_COST
            value += WAIT_COST_FULL * self._stationary_unfinished_fraction(nxt)
        need(math.isfinite(value), 'G1_REWARD_NONFINITE')
        return value


class PlanningWorkCutoff(RuntimeError):
    pass


class DeadlineBudgetSearch:
    """Iteration-budget MCTS with frozen 380/400 ms execution semantics.

    Requested budget remains the calibration variable. Work stops cooperatively at
    380 ms at iteration/selection/rollout boundaries. An incomplete iteration is
    never backed up. Caller separately rejects any return after 400 ms.
    """
    def __init__(self, api, transition_model, reward_model, action_provider,
                 budget, max_depth, seed):
        self.api = api
        self.transition = transition_model
        self.reward = reward_model
        self.base_action_provider = action_provider
        from candidate_mcts.deadlock_runtime_v1 import SafeAbsorbingDeadlockDetector
        self.deadlock_detector = SafeAbsorbingDeadlockDetector(self.base_action_provider, self.transition.step)
        self.action_provider = self._deadlock_aware_actions
        self.reward.set_terminal_predicate(self.deadlock_detector.is_deadlock)
        self.budget = int(budget); self.max_depth = int(max_depth)
        self.c_uct = C_UCT; self.gamma = GAMMA; self.seed = int(seed)
        self.rng = random.Random(self.seed)

    def _deadlock_aware_actions(self, state):
        if state.hard_safety_violation or state.all_goals_reached:
            return []
        if self.deadlock_detector.is_deadlock(state):
            return []
        return list(self.base_action_provider(state))

    def _past(self, cutoff):
        return time.perf_counter_ns() >= cutoff

    def _select_uct(self, node):
        log_parent = math.log(node.visit_count + 1.0)
        best = None; best_score = -float('inf')
        for action, child in sorted(node.children.items(), key=lambda item: self.api['joint_key'](item[0])):
            explore = self.c_uct * math.sqrt(log_parent / (child.visit_count + 1e-6))
            score = child.q + explore
            if score > best_score:
                best_score, best = score, child
        need(best is not None, 'FLEET_UCT_NO_CHILD')
        return best

    def _staged_expand(self, node, cutoff):
        if not node.untried_actions:
            return node, False
        if self._past(cutoff):
            return node, True
        index = self.rng.randrange(len(node.untried_actions))
        action = node.untried_actions[index]
        next_state = self.transition.step(node.state, action)
        if self._past(cutoff):
            return node, True
        # Commit tree mutation only after the transition has returned before cutoff.
        node.untried_actions.pop(index)
        child = self.api['FleetMCTSNode'](
            state=next_state, parent=node, action_from_parent=action, depth=node.depth + 1,
            available_actions=list(self.action_provider(next_state)),
            terminal_predicate=self.deadlock_detector.is_deadlock)
        node.children[action] = child
        return child, False

    def _rollout(self, node, cutoff):
        state = node.state; depth = node.depth; total = 0.0; discount = 1.0
        while not self.reward.is_terminal(state, depth, self.max_depth):
            if self._past(cutoff):
                return None, True
            actions = self.action_provider(state)
            if not actions:
                break
            action = self.rng.choice(actions)
            next_state = self.transition.step(state, action)
            if self._past(cutoff):
                return None, True
            step_reward = self.reward.evaluate(state, next_state)
            total += discount * step_reward
            discount *= self.gamma
            state = next_state; depth += 1
        return total, False

    def _backup_full(self, node, rollout_value):
        # Mirrors frozen FleetMCTSSearch._backup exactly.
        value = rollout_value
        current = node
        while current is not None:
            if current.parent is not None:
                immediate = self.reward.evaluate(current.parent.state, current.state)
                value = immediate + self.gamma * value
            current.visit_count += 1
            current.value_sum += value
            current = current.parent

    def _count_nodes(self, root):
        total = 1; stack = list(root.children.values())
        while stack:
            n = stack.pop(); total += 1; stack.extend(n.children.values())
        return total

    def search(self, root_state):
        if self.deadlock_detector.is_deadlock(root_state):
            raise RuntimeError('SAFE_DEADLOCK_ROOT_SEARCH_BLOCKED')
        root = self.api['FleetMCTSNode'](
            state=root_state, depth=0, available_actions=list(self.action_provider(root_state)),
            terminal_predicate=self.deadlock_detector.is_deadlock)
        if not root.untried_actions:
            raise RuntimeError('Fleet MCTS root has no children.')

        start_ns = time.perf_counter_ns(); cutoff_ns = start_ns + WORK_CUTOFF_NS
        completed = 0; started = 0; aborted = 0; stop_reason = 'REQUESTED_ITERATIONS_COMPLETED'
        for _ in range(self.budget):
            if self._past(cutoff_ns):
                stop_reason = 'WORK_CUTOFF_BEFORE_ITERATION'; break
            started += 1; node = root; abort = False
            while (not node.is_terminal(self.max_depth) and node.is_fully_expanded() and node.children):
                if self._past(cutoff_ns): abort = True; break
                node = self._select_uct(node)
            if abort:
                aborted += 1; stop_reason = 'WORK_CUTOFF_DURING_SELECTION'; break
            if not node.is_terminal(self.max_depth):
                node, abort = self._staged_expand(node, cutoff_ns)
            if abort:
                aborted += 1; stop_reason = 'WORK_CUTOFF_DURING_EXPANSION'; break
            rollout_value, abort = self._rollout(node, cutoff_ns)
            if abort:
                aborted += 1; stop_reason = 'WORK_CUTOFF_DURING_ROLLOUT'; break
            self._backup_full(node, rollout_value)
            completed += 1
        if completed < self.budget and stop_reason == 'REQUESTED_ITERATIONS_COMPLETED':
            stop_reason = 'WORK_CUTOFF'

        visited = [(a, c) for a, c in root.children.items() if c.visit_count > 0]
        elapsed_ns = time.perf_counter_ns() - start_ns
        if not visited:
            raise PlanningWorkCutoff('NO_COMPLETED_ITERATION_BEFORE_WORK_CUTOFF')
        best_action = max(visited, key=lambda item: (
            item[1].visit_count, item[1].q,
            tuple(-v for v in self.api['joint_key'](item[0]))))[0]
        diag = {
            'requested_iterations': self.budget,
            'iterations': completed,
            'completed_iterations': completed,
            'started_iterations': started,
            'aborted_incomplete_iterations': aborted,
            'stop_reason': stop_reason,
            'work_cutoff_hit': completed < self.budget,
            'work_cutoff_ms': WORK_CUTOFF_NS / 1e6,
            'elapsed_ms': elapsed_ns / 1e6,
            'seed': self.seed,
            'visits': {self.api['joint_id'](a): c.visit_count for a, c in root.children.items() if c.visit_count > 0},
            'q_values': {self.api['joint_id'](a): c.q for a, c in root.children.items() if c.visit_count > 0},
            'minimum_clearance_m': {self.api['joint_id'](a): c.state.minimum_clearance_m for a, c in root.children.items() if c.visit_count > 0},
            'expanded_nodes': self._count_nodes(root),
            'partial_iterations_never_backed_up': True,
        }
        return best_action, diag


def decision_seed(root, replicate, outer_step):
    material = {
        'schema': 'G2_PER_DECISION_PAIRED_RNG_V2',
        'root_id': root['root_id'],
        'state_sha256': root['exact_before_state_sha256'],
        'replicate': int(replicate),
        'outer_step': int(outer_step),
    }
    return int(hashlib.sha256(canonical(material)).hexdigest()[:16], 16)


def classify_state(api, state, steps, detector):
    status = api['episode_status'](state, steps, MAX_OUTER_STEPS,
        hard_event_ever=bool(state.hard_safety_violation), deadlock_detector=detector)
    mapping = {
        'BOTH_PARKED_AT_OWN_DESTINATIONS': 'SUCCESS',
        'EXECUTED_HARD_SAFETY_TERMINAL': 'HARD_SAFETY_TERMINAL',
        'SAFE_DEADLOCK': 'SAFE_DEADLOCK',
        'EVALUATION_CAP_NOT_TASK_TERMINAL': 'SAFE_INCOMPLETE_CAP',
        'RUNNING': 'RUNNING',
    }
    return mapping.get(status, status)


def cell_signature(root, budget, depth, replicate):
    return objsha({
        'schema': 'G2_FORMAL_CELL_V2', 'root_id': root['root_id'],
        'state_sha256': root['exact_before_state_sha256'], 'budget': budget,
        'depth': depth, 'replicate': replicate, 'gamma': GAMMA, 'c_uct': C_UCT,
        'deadline_ns': [WORK_CUTOFF_NS, DECISION_WALL_NS, RETURN_RESERVE_NS],
        'runner_contract_version': RUNNER_CONTRACT_VERSION,
        'g1_freeze_sha256': EXPECTED_G1_SHA, 'map_sha256': EXPECTED_MAP_SHA,
        'map_loader_sha256': EXPECTED_MAP_LOADER_SHA,
        'v2r_transition_sha256': EXPECTED_V2R_SOURCE_SHA[TMP / 'minesim_g1_v2r_transition_overlay_v1' / 'g1_v2r_transition_overlay_v1.py'],
        'deadlock_runtime_sha256': EXPECTED_DEADLOCK_SOURCE_SHA['deadlock_runtime_v1.py'],
    })


def run_episode(api, root, drivable_domain, budget, depth, replicate=0, technical_only=False):
    bc, transition, state, providers, counters = build_context(api, root, drivable_domain)
    reward = G1RewardContract(bc.system.reward)
    max_steps = 1 if technical_only else MAX_OUTER_STEPS
    rows = []; total_return = 0.0; wall_ns_total = 0; cpu_ns_total = 0
    final = 'RUNNING'; hard_event_ever = False

    # Classifier detector is created with the same consolidated transition/reward semantics.
    probe = DeadlineBudgetSearch(api, transition, reward, transition.active_joint_actions, 1, 1,
                                 decision_seed(root, replicate, 0))
    initial = classify_state(api, state, 0, probe.deadlock_detector)
    need(initial == 'RUNNING', 'ROOT_NOT_RUNNING:' + initial)

    for step in range(max_steps):
        # Fresh per-decision seed: strict paired initial RNG across budgets/depths for this root/step.
        seed = decision_seed(root, replicate, step)
        searcher = DeadlineBudgetSearch(api, transition, reward, transition.active_joint_actions,
                                        budget, depth, seed)
        status_before = classify_state(api, state, step, searcher.deadlock_detector)
        if status_before != 'RUNNING':
            final = status_before; break
        active = list(transition.active_joint_actions(state))
        if not active:
            final = 'NO_ADMITTED_ACTION'; break

        t0 = time.perf_counter_ns(); c0 = time.process_time_ns()
        try:
            action, diag = searcher.search(state)
        except PlanningWorkCutoff:
            c1 = time.process_time_ns(); t1 = time.perf_counter_ns()
            wall = t1 - t0; cpu = c1 - c0
            wall_ns_total += wall; cpu_ns_total += cpu
            final = 'PLANNING_DEADLINE_FAILURE'
            rows.append({'step': step, 'outcome': final, 'action_id': None,
                         'decision_seed': seed, 'search_wall_ms': wall / 1e6,
                         'search_cpu_ms': cpu / 1e6, 'work_cutoff_no_decision': True,
                         'outer_transition_executed': False})
            break
        c1 = time.process_time_ns(); t1 = time.perf_counter_ns()
        wall = t1 - t0; cpu = c1 - c0
        wall_ns_total += wall; cpu_ns_total += cpu
        # Frozen execution contract: a late return is never executed.
        if wall > DECISION_WALL_NS:
            final = 'PLANNING_DEADLINE_FAILURE'
            rows.append({'step': step, 'outcome': final, 'action_id': api['action_id'](action),
                         'decision_seed': seed, 'search_wall_ms': wall / 1e6,
                         'search_cpu_ms': cpu / 1e6, 'diagnostics': diag,
                         'late_return_no_execution': True, 'outer_transition_executed': False})
            break

        nxt, detail = transition.step_with_diagnostics(state, action)
        reward_value = reward.evaluate(state, nxt)
        hard_event_ever = hard_event_ever or bool(nxt.hard_safety_violation)
        total_return += (GAMMA ** step) * reward_value
        outcome = classify_state(api, nxt, step + 1, searcher.deadlock_detector)
        rows.append({
            'step': step, 'action_id': api['action_id'](action), 'reward': reward_value,
            'discounted_reward': (GAMMA ** step) * reward_value, 'outcome': outcome,
            'decision_seed': seed, 'search_wall_ms': wall / 1e6, 'search_cpu_ms': cpu / 1e6,
            'requested_iterations': diag['requested_iterations'],
            'completed_iterations': diag['completed_iterations'],
            'started_iterations': diag['started_iterations'],
            'aborted_incomplete_iterations': diag['aborted_incomplete_iterations'],
            'work_cutoff_hit': diag['work_cutoff_hit'], 'stop_reason': diag['stop_reason'],
            'visits': diag['visits'], 'q_values': diag['q_values'],
            'expanded_nodes': diag['expanded_nodes'],
            'minimum_clearance_m': diag['minimum_clearance_m'],
            'v2r_violation_after': bool(getattr(nxt, 'drivable_area_violation', False)),
            'v2r_violating_tokens_after': list(getattr(nxt, 'drivable_violating_tokens', ())),
            'transition_geometry_scope': detail.get('geometry_scope'),
            'road_boundary_status': detail.get('road_boundary_status'),
            'outer_transition_executed': True,
        })
        state = nxt; final = outcome
        if outcome != 'RUNNING':
            break

    if not technical_only and final == 'RUNNING' and len([r for r in rows if r.get('outer_transition_executed')]) >= MAX_OUTER_STEPS:
        final = 'SAFE_INCOMPLETE_CAP'

    executed_rows = [r for r in rows if r.get('outer_transition_executed')]
    return {
        'schema': 'G2_FORMAL_CELL_RESULT_V2', 'root_id': root['root_id'],
        'episode_uid': root['task']['episode_uid'], 'role': 'G2_CALIBRATION_DEVELOPMENT',
        'g9_holdout_eligible': False, 'budget': int(budget), 'depth': int(depth),
        'replicate': int(replicate), 'technical_only': bool(technical_only),
        'steps_executed': len(executed_rows), 'decision_attempts': len(rows),
        'final_outcome': final, 'discounted_return': total_return,
        'search_wall_ms_total': wall_ns_total / 1e6, 'search_cpu_ms_total': cpu_ns_total / 1e6,
        'completed_iterations_total': sum(r.get('completed_iterations', 0) for r in rows),
        'expanded_nodes_total': sum(r.get('expanded_nodes', 0) for r in rows),
        'work_cutoff_calls': sum(bool(r.get('work_cutoff_hit')) for r in rows),
        'teacher_sample': False, 'training_mask': 0, 'holdout_used': False,
        'rows': rows,
    }


def aggregate(cells):
    groups = {}
    for c in cells:
        groups.setdefault((c['budget'], c['depth']), []).append(c)
    summary = []
    taxonomy = ['SUCCESS','HARD_SAFETY_TERMINAL','SAFE_DEADLOCK','SAFE_INCOMPLETE_CAP',
                'PLANNING_DEADLINE_FAILURE','NO_ADMITTED_ACTION','RUNNING']
    for (budget, depth), rows in sorted(groups.items()):
        outcomes = {k: 0 for k in taxonomy}
        for r in rows:
            outcomes[r['final_outcome']] = outcomes.get(r['final_outcome'], 0) + 1
        n = len(rows)
        summary.append({
            'budget': budget, 'depth': depth, 'n_cells': n, 'outcomes': outcomes,
            'success_count': outcomes.get('SUCCESS', 0),
            'hard_safety_count': outcomes.get('HARD_SAFETY_TERMINAL', 0),
            'deadlock_count': outcomes.get('SAFE_DEADLOCK', 0),
            'cap_count': outcomes.get('SAFE_INCOMPLETE_CAP', 0),
            'deadline_failure_count': outcomes.get('PLANNING_DEADLINE_FAILURE', 0),
            'no_admitted_action_count': outcomes.get('NO_ADMITTED_ACTION', 0),
            'mean_discounted_return': sum(r['discounted_return'] for r in rows) / n,
            'mean_search_wall_ms_total': sum(r['search_wall_ms_total'] for r in rows) / n,
            'mean_search_cpu_ms_total': sum(r['search_cpu_ms_total'] for r in rows) / n,
            'mean_steps': sum(r['steps_executed'] for r in rows) / n,
            'mean_completed_iterations_total': sum(r['completed_iterations_total'] for r in rows) / n,
            'mean_expanded_nodes_total': sum(r['expanded_nodes_total'] for r in rows) / n,
            'work_cutoff_calls_total': sum(r['work_cutoff_calls'] for r in rows),
        })
    return summary


def write_csv(summary):
    cols = ['budget','depth','n_cells','success_count','hard_safety_count','deadlock_count','cap_count',
            'deadline_failure_count','no_admitted_action_count','mean_discounted_return',
            'mean_search_wall_ms_total','mean_search_cpu_ms_total','mean_steps',
            'mean_completed_iterations_total','mean_expanded_nodes_total','work_cutoff_calls_total']
    lines = [','.join(cols)]
    for row in summary:
        lines.append(','.join(str(row[c]) for c in cols))
    atomic_text(OUT / 'STAGE_A_SUMMARY.csv', '\n'.join(lines) + '\n')


def make_descriptive_frontier(summary):
    # No winner is frozen here. This is a descriptive screen only.
    rows = []
    for r in summary:
        execution_failures = r['deadline_failure_count'] + r['no_admitted_action_count']
        safety_failures = r['hard_safety_count']
        rows.append({**r, 'execution_failures': execution_failures, 'safety_failures': safety_failures})
    rows.sort(key=lambda r: (r['safety_failures'], r['execution_failures'], -r['success_count'],
                             -r['mean_discounted_return'], r['mean_search_cpu_ms_total'], r['budget'], r['depth']))
    return {
        'status': 'DESCRIPTIVE_ONLY_NOT_G2_FREEZE',
        'selection': 'HOLD_FOR_G2_NEXT_STAGE',
        'note': 'Stage-A has one replicate per root and only current Retry2 C11 lineage. Do not treat this ordering as a final Teacher configuration.',
        'b64_h8_anchor_present': any(r['budget'] == 64 and r['depth'] == 8 for r in rows),
        'ordered_descriptive_rows': rows,
    }


def prepare():
    print('=== G2 FORMAL CALIBRATION V2 PREPARE (LOW) ===', flush=True)
    head, status, g1 = repo_precheck()
    api = activate_runtime()
    domain, domain_evidence = build_drivable_domain()
    roots = load_roots()

    restored = []
    for root in roots:
        bc, tr, state, providers, counters = build_context(api, root, domain)
        restored.append({
            'root_id': root['root_id'], 'episode_uid': root['task']['episode_uid'],
            'scene': root['task']['scene'], 'source_sha256': root['source_sha256'],
            'state_sha256': root['exact_before_state_sha256'],
            'role': 'G2_CALIBRATION_DEVELOPMENT', 'g9_holdout_eligible': False,
            'v2r_initial_safe': not state.drivable_area_violation,
            'hard_initial_safe': not state.hard_safety_violation,
            'route_lengths': bc.goals,
            'action_ids': [api['action_id'](a) for a in tr.active_joint_actions(state)],
        })

    # Technical one-decision smoke using the consolidated runtime; not scientific calibration.
    smoke = run_episode(api, roots[0], domain, budget=1, depth=1, replicate=0, technical_only=True)
    need(smoke['decision_attempts'] <= 1, 'TECH_SMOKE_DECISION_COUNT')
    need(smoke['final_outcome'] in ('RUNNING','SUCCESS','HARD_SAFETY_TERMINAL','SAFE_DEADLOCK',
                                    'PLANNING_DEADLINE_FAILURE','NO_ADMITTED_ACTION'), 'TECH_SMOKE_OUTCOME')

    if OUT.exists():
        # Resume-safe namespace: prepare may be rerun only if no scientific cells exist.
        existing_cells = list((OUT / 'cells').glob('*.json')) if (OUT / 'cells').exists() else []
        need(not existing_cells, 'V2_OUTPUT_HAS_SCIENTIFIC_CELLS_NO_PREPARE_OVERWRITE')
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    contract = {
        'schema': 'G2_FORMAL_CALIBRATION_V2_PREPARE', 'runner_contract_version': RUNNER_CONTRACT_VERSION, 'status': 'PASS', 'resource': 'LOW',
        'head': head, 'git_status': status, 'g0': g1['g0_status'], 'g1': g1['g1_status'],
        'g2': 'READY_STAGE_A_NOT_RUN', 'g1_freeze_sha256': sha256(G1_FREEZE),
        'roots_sha256': sha256(RELEASE / 'ROOTS.json'), 'full_eval_sha256': sha256(RELEASE / 'parent' / 'full_eval.py'),
        'root_role': 'G2_CALIBRATION_DEVELOPMENT', 'g9_holdout_eligible': False,
        'root_count': len(roots), 'roots': restored,
        'matrix': {'budgets': BUDGETS, 'horizons': DEPTHS, 'replicates': REPLICATES,
                   'cells_per_root': len(BUDGETS) * len(DEPTHS) * len(REPLICATES),
                   'total_cells': len(roots) * len(BUDGETS) * len(DEPTHS) * len(REPLICATES),
                   'b64_h8_anchor': True,
                   'stage_a_scope': 'SAME_LINEAGE_C11_COARSE_CALIBRATION_NOT_CROSS_SCENE_GENERALIZATION'},
        'paired_rng': {'schema': 'G2_PER_DECISION_PAIRED_RNG_V2',
                       'seed_material': 'root_id+root_state_sha256+replicate+outer_step',
                       'budget_or_horizon_in_seed': False,
                       'strict_prefix_claim': 'WITHIN_FIXED_HORIZON_ACROSS_BUDGETS;HORIZONS_SHARE_INITIAL_DECISION_SEED_BUT_NOT_DRAW_BY_DRAW_CONSUMPTION'},
        'deadline_contract': {'decision_wall_ns': DECISION_WALL_NS, 'work_cutoff_ns': WORK_CUTOFF_NS,
                              'return_reserve_ns': RETURN_RESERVE_NS,
                              'late_return_executes_outer_transition': False,
                              'cooperative_checkpoints': 'ITERATION_SELECTION_EXPANSION_ROLLOUT_BOUNDARIES',
                              'incomplete_iteration_backup': False},
        'g1_runtime_contract': {'v2v': 'EXACT_9x4M_FOOTPRINT_AT_0.1S_TICKS',
                                'v2r': 'EXACT_FOOTPRINT_COVERED_BY_D_DRIVABLE_AT_0.1S_TICKS',
                                'deadlock': 'SAFE_ABSORBING_STATE_TRAP',
                                'progress_cap': PROGRESS_CAP, 'time_cost': TIME_COST,
                                'wait_cost_full': WAIT_COST_FULL, 'per_vehicle_first_parked': NEW_FIRST_GOAL,
                                'both_parked_global': GLOBAL_BOTH_PARKED, 'hard_penalty': -100.0},
        'drivable_domain': domain_evidence,
        'technical_smoke': smoke,
        'scientific_runtime': False, 'teacher_collection': False, 'training': False,
        'real_benchmark': False, 'holdout_used': False, 'repo_write': False,
        'stage_a': 'READY_REQUIRES_HIGH_CPU_AUTHORIZATION',
    }
    atomic_json(OUT / 'PREPARE.json', contract)
    atomic_json(OUT / 'G2_A_ROLE_MANIFEST.json', {
        'role': 'G2_CALIBRATION_DEVELOPMENT', 'roots': [r['root_id'] for r in roots],
        'scenes': ['C11'], 'g9_holdout_eligible': False,
        'teacher_collection': False, 'training': False,
        'g2_b_later': 'C04+C06+C11 FRONTIER/ANCHOR SANITY_TRANSFER_ONLY_NO_RETUNING',
    })

    print('SOURCE_BINDING = PASS')
    print('G1_FINAL_FREEZE_BINDING = PASS')
    print('DEADLOCK_RUNTIME_BINDING = PASS')
    print('V2R_OVERLAY_BINDING = PASS')
    print('DRIVABLE_MAP_SHA = PASS')
    print('PRODUCTION_MAP_LOADER_SHA = PASS')
    print('DRIVABLE_POLYGONS =', domain_evidence['selected_polygon_count'])
    print('DRIVABLE_COMPONENTS =', domain_evidence['union_components'])
    print('DRIVABLE_G2_BINDING_SHA256 =', domain_evidence['g2_domain_binding_sha256'])
    print('LEGACY_G1_TOKEN_HASH_REPRODUCED =', bool(domain_evidence['legacy_token_hash_reproduction_matches']))
    print('FORMAL_ROOT_RESTORATION = PASS')
    print('CONSOLIDATED_V2V_V2R_DEADLOCK = PASS')
    print('G1_REWARD_CONTRACT_BINDING = PASS')
    print('DEADLINE_CONTRACT = 400/380/20ms')
    print('PAIRED_RNG = PER_DECISION')
    print('ROOT_COUNT =', len(roots))
    print('TOTAL_STAGE_A_CELLS =', contract['matrix']['total_cells'])
    print('B64_H8_ANCHOR = PRESENT')
    print('TECHNICAL_SMOKE = PASS')
    print('SCIENTIFIC_RUNTIME = false')
    print('TEACHER_COLLECTION = false')
    print('HOLDOUT_USED = false')
    print('STAGE_A = READY_REQUIRES_HIGH_CPU_AUTHORIZATION')
    print('OUTPUT =', OUT)
    print('PASS:G2_FORMAL_CALIBRATION_V2_PREPARE')


def load_existing_cells(roots):
    expected = {}
    for root in roots:
        for rep in REPLICATES:
            for depth in DEPTHS:
                for budget in BUDGETS:
                    cid = '%s__R%d__B%d__H%d' % (root['root_id'], rep, budget, depth)
                    expected[cid] = (root, budget, depth, rep)
    completed = []
    CELLS.mkdir(parents=True, exist_ok=True)
    for p in CELLS.glob('*.json'):
        cid = p.stem
        need(cid in expected, 'UNKNOWN_EXISTING_CELL:' + cid)
        obj = load_json(p)
        root, budget, depth, rep = expected[cid]
        need(obj.get('cell_signature') == cell_signature(root, budget, depth, rep), 'EXISTING_CELL_SIGNATURE_DRIFT:' + cid)
        need(obj.get('status') == 'PASS', 'EXISTING_CELL_NOT_PASS:' + cid)
        completed.append(obj['result'])
    return expected, completed


def stage_a():
    print('=== G2 FORMAL CALIBRATION V2 STAGE-A (HIGH-CPU) ===', flush=True)
    need(os.environ.get('G2_HIGH_CPU_AUTHORIZED') == 'YES', 'HIGH_CPU_NOT_AUTHORIZED')
    need((OUT / 'PREPARE.json').is_file(), 'RUN_PREPARE_FIRST')
    prep = load_json(OUT / 'PREPARE.json')
    need(prep.get('status') == 'PASS', 'PREPARE_NOT_PASS')
    need(prep.get('runner_contract_version') == RUNNER_CONTRACT_VERSION, 'PREPARE_RUNNER_VERSION_DRIFT')
    need(prep.get('holdout_used') is False, 'HOLDOUT_ALREADY_USED')
    repo_precheck()
    api = activate_runtime(); domain, domain_evidence = build_drivable_domain(); roots = load_roots()
    need(domain_evidence.get('g2_domain_binding_sha256') == prep.get('drivable_domain', {}).get('g2_domain_binding_sha256'),
         'DRIVABLE_DOMAIN_BINDING_CHANGED_SINCE_PREPARE')
    expected, completed = load_existing_cells(roots)
    done_ids = {c.get('cell_id') for c in completed}
    print('RESUME_EXISTING_CELLS =', len(done_ids), flush=True)

    try:
        for cid, (root, budget, depth, rep) in expected.items():
            if cid in done_ids:
                print('CELL_SKIP_EXISTING =', cid, flush=True); continue
            print('CELL_START =', cid, flush=True)
            result = run_episode(api, root, domain, budget, depth, replicate=rep, technical_only=False)
            result['cell_id'] = cid
            record = {'status': 'PASS', 'cell_signature': cell_signature(root, budget, depth, rep), 'result': result}
            atomic_json(CELLS / (cid + '.json'), record)
            completed.append(result); done_ids.add(cid)
            print('CELL_DONE =', cid, 'OUTCOME =', result['final_outcome'],
                  'STEPS =', result['steps_executed'], 'RETURN =', result['discounted_return'], flush=True)

        need(len(completed) == len(expected) == 60, 'STAGE_A_CELL_COUNT:' + str(len(completed)))
        summary = aggregate(completed)
        frontier = make_descriptive_frontier(summary)
        atomic_json(OUT / 'STAGE_A_SUMMARY.json', {
            'schema': 'G2_FORMAL_STAGE_A_V2', 'status': 'PASS_COARSE_SCREEN',
            'cells_completed': len(completed), 'root_count': len(roots),
            'matrix_summary': summary, 'stage_a_role': 'COARSE_CALIBRATION_DEVELOPMENT',
            'g2_frozen': False, 'teacher_collection': False, 'training': False,
            'holdout_used': False, 'next': 'G2_STAGE_A_REVIEW_THEN_G2_B_OR_PAIRED_MULTI_SEED_CONFIRMATION',
        })
        atomic_json(OUT / 'STAGE_A_FRONTIER_DESCRIPTIVE.json', frontier)
        write_csv(summary)
        print('CELLS_COMPLETED = 60')
        print('B64_H8_ANCHOR_COMPLETED =', any(c['budget']==64 and c['depth']==8 for c in completed))
        print('G2_FROZEN = false')
        print('TEACHER_COLLECTION = false')
        print('TRAINING = false')
        print('HOLDOUT_USED = false')
        print('PASS:G2_FORMAL_CALIBRATION_V2_STAGE_A')
    except BaseException as exc:
        atomic_json(OUT / 'STAGE_A_FAILURE.json', {
            'stage': 'G2_FORMAL_CALIBRATION_V2_STAGE_A', 'status': 'FAIL_OR_HOLD',
            'cells_completed': len(completed), 'exception_type': type(exc).__name__,
            'exception': str(exc), 'teacher_collection': False, 'training': False,
            'holdout_used': False, 'auto_retry': False,
        })
        print('FAIL:G2_FORMAL_CALIBRATION_V2_STAGE_A')
        print(type(exc).__name__ + ':', exc)
        raise


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('mode', choices=('prepare', 'stage-a'))
    args = ap.parse_args()
    if args.mode == 'prepare': prepare()
    else: stage_a()


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        traceback.print_exc()
        raise
