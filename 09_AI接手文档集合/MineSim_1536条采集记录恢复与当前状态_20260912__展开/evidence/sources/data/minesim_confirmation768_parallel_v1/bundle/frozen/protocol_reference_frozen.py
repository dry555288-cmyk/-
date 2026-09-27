"""Pure-data reference rules for a proposed MineSim teacher pilot.

No project imports, MCTS, model loading, random sampling, or cloud access.
These helpers specify a DEVELOPMENT protocol, not a certified pruning rule.
"""
from __future__ import annotations
from itertools import combinations
from math import isfinite, sqrt, fsum
from typing import Any, Sequence


def finite_number(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and isfinite(v)


def select_states(pool: dict, spec: dict) -> dict:
    """Select existing records using only the explicit blind-state projection.

    The caller must SHA-bind the source projection first. Full-state/context
    reconstruction is deliberately outside the scope of this function.
    """
    rows = pool['rows']
    if not rows:
        raise ValueError('empty pool')
    ids = [r['pilot_id'] for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError('duplicate identity')
    for r in rows:
        if len(r['feature12']) != 12 or not all(map(finite_number, r['feature12'])):
            raise ValueError('invalid feature vector')
        if not isinstance(r['root_step'], int) or isinstance(r['root_step'], bool):
            raise ValueError('invalid step')
    dims = spec['feature_indices_for_distance']
    means = [fsum(r['feature12'][j] for r in rows) / len(rows) for j in dims]
    scales = [sqrt(fsum((r['feature12'][j] - m) ** 2 for r in rows) / len(rows))
              for j, m in zip(dims, means)]
    scales = [s if s > 0 else 1.0 for s in scales]
    selected, seen, decisions = [], set(), []
    for episode in spec['episodes_in_fixed_order']:
        allowed = sorted((r for r in rows if r['episode_uid'] == episode
                          and r['both_goal_false'] is True
                          and r['both_initial_collision_false'] is True
                          and r['feature_sha256_float32'] not in seen),
                         key=lambda r: (r['root_step'], r['pilot_id']))
        pairs = [(a, b) for a, b in combinations(allowed, 2)
                 if a['feature_sha256_float32'] != b['feature_sha256_float32']]
        if not pairs:
            raise ValueError('HOLD: fewer than two unique eligible states: ' + episode)
        scored = []
        for a, b in pairs:
            distance2 = fsum(((a['feature12'][j] - b['feature12'][j]) / s) ** 2
                            for j, s in zip(dims, scales))
            key = (-distance2, a['root_step'], a['pilot_id'], b['root_step'], b['pilot_id'])
            scored.append((key, a, b))
        key, a, b = min(scored, key=lambda v: v[0])
        selected.extend([a, b])
        seen.update([a['feature_sha256_float32'], b['feature_sha256_float32']])
        decisions.append({'episode_uid': episode, 'eligible_pairs': len(pairs),
                          'selected': [a['pilot_id'], b['pilot_id']], 'distance_squared': -key[0]})
    if len(selected) != spec['root_count']:
        raise ValueError('root quota mismatch')
    return {'status': 'DESIGN_SELECTION_ONLY_NOT_RUNTIME_BINDING',
            'selected': selected, 'scale_dimensions': dims, 'scale_mean': means,
            'scale_std_guarded': scales, 'decisions': decisions,
            'selected_unique_feature_count': len(seen)}


def empirical_pair(discovery_i: Sequence[dict], discovery_j: Sequence[dict],
                   confirm_i: Sequence[dict], confirm_j: Sequence[dict],
                   repeats: int = 4, atol: float = 1e-8) -> dict:
    """Return a provisional empirical order or an explicit unknown.

    Each synthetic/future observation contains {return, terminal}; terminal is
    GOAL, HARD, or CAP. HARD is a valid return and never removed. CAP is a valid
    finite-window observation, but not eligible for this long-return label.
    No outcome from historical trajectories is passed to this helper in V1.
    """
    if not isinstance(repeats, int) or isinstance(repeats, bool) or repeats < 1:
        raise ValueError('bad repeats')
    if not finite_number(atol) or atol < 0:
        raise ValueError('bad numeric guard')

    def unknown(reason: str, candidate=None) -> dict:
        return {'mask': 0, 'direction': None, 'reason': reason,
                'discovery_direction': candidate, 'certified': False}

    batches = [discovery_i, discovery_j, confirm_i, confirm_j]
    for batch in batches:
        if len(batch) != repeats:
            return unknown('HOLD_MISSING_OR_INVALID')
        for item in batch:
            if not isinstance(item, dict) or not finite_number(item.get('return')):
                return unknown('HOLD_MISSING_OR_INVALID')
            if item.get('terminal') not in {'GOAL', 'HARD', 'CAP'}:
                return unknown('HOLD_MISSING_OR_INVALID')
    if any(o['terminal'] == 'CAP' for b in batches for o in b):
        return unknown('UNKNOWN_TAIL_CENSORED')
    di, dj, ci, cj = [[float(o['return']) for o in b] for b in batches]

    def sep(x, y):
        if min(x) - max(y) > atol:
            return 1
        if min(y) - max(x) > atol:
            return -1
        return 0

    direction = sep(di, dj)
    if direction == 0:
        gap = max(min(di) - max(dj), min(dj) - max(di))
        return unknown('UNKNOWN_NUMERIC_RESOLUTION' if 0 <= gap <= atol
                       else 'UNKNOWN_OVERLAPPING_RETURNS')
    if sep(ci, cj) != direction or sep(di + ci, dj + cj) != direction:
        return unknown('UNKNOWN_CONFIRMATION', direction)
    g = min(di + ci) - max(dj + cj) if direction > 0 else min(dj + cj) - max(di + ci)
    return {'mask': 1, 'direction': direction, 'reason': 'EMPIRICAL_REPEATED_ORDER_NOT_CERTIFIED',
            'discovery_direction': direction, 'combined_observed_range_gap': g,
            'certified': False}


def grouped_splits(selected: Sequence[dict]) -> list[dict]:
    """Episode-blocked design, preserving whole state + all its action repeats."""
    folds = []
    for ep in sorted(set(r['episode_uid'] for r in selected)):
        test = [r for r in selected if r['episode_uid'] == ep]
        keys = {r['feature_sha256_float32'] for r in test}
        train = [r for r in selected if r['episode_uid'] != ep
                 and r['feature_sha256_float32'] not in keys]
        folds.append({'heldout_episode': ep, 'train_root_ids': [r['pilot_id'] for r in train],
                      'heldout_root_ids': [r['pilot_id'] for r in test],
                      'not_independent_final_test': True, 'training_executed': False,
                      'state_context_identity_guard': 'REQUIRED_AT_RUNTIME_BINDING_AND_TRAINING_PREFLIGHT'})
    return folds


def validate_spec(p: dict) -> None:
    if p['status'] != 'DESIGN_ONLY_NOT_AUTHORIZATION' or any(p['permissions'].values()):
        raise ValueError('design must not authorize execution')
    s = p['sampling']; roots = p['selection']['root_count']
    actions = s['actions']
    if actions != [[a, b] for a in range(4) for b in range(4)]:
        raise ValueError('canonical16 missing or reordered')
    seeds = []
    total = 0
    for stage in ['discovery', 'confirmation']:
        b = s[stage]; n = b['outer_repeats_per_action']
        if n != 4 or len(b['proposed_seeds']) != n:
            raise ValueError('repeat count')
        if b['planned_trajectories'] != roots * 16 * n:
            raise ValueError('batch count')
        total += b['planned_trajectories']; seeds.extend(b['proposed_seeds'])
    if len(set(seeds + [s['proposed_technical_seed']])) != len(seeds) + 1:
        raise ValueError('overlapping proposed streams')
    if total != s['planned_total_trajectories'] or s['outer_repeats_total_per_action'] != 8:
        raise ValueError('total count')
    e = p['inherited_execution']; cap = e['cap_steps_including_first']
    if e['dt_s'] * cap != e['cap_seconds'] or (e['policy_budget'], e['policy_max_depth'], e['gamma']) != (64, 8, 0.99):
        raise ValueError('changed policy/horizon')
    if (total * cap != s['maximum_execution_transitions'] or total * (cap - 1) != s['maximum_policy_calls']
        or total * (cap - 1) * e['policy_budget'] != s['maximum_policy_iterations']):
        raise ValueError('resource-count mismatch')
    if p['labels']['comparison_atol'] != 1e-8:
        raise ValueError('changed technical guard')
    if s['confirmation']['allow_promote_discovery_unknown'] or not s['confirmation']['collect_all_actions']:
        raise ValueError('confirmation selection leakage')
