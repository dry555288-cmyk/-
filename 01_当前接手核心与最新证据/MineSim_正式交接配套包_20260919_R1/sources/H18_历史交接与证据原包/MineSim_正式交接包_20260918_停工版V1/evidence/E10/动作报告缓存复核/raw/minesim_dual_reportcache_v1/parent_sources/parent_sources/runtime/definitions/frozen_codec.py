from __future__ import annotations
import math, dataclasses, random
class Hold(RuntimeError): pass
def need(ok, reason):
    if not ok: raise Hold(reason)
VEH_FIELDS = ('time_s','route_s','speed_mps','accel_mps2','lead_distance_m',
              'lead_rel_speed_mps','target_speed_mps','minimum_clearance_m',
              'prev_action','collision','goal_reached')
FLEET_FIELDS = ('vehicles','internal_collision','minimum_internal_clearance_m',
                'conflicting_pairs','internal_safety_violation','safety_violating_pairs')
def real_pack(v):
    v = float(v)
    need(not math.isnan(v) and v != -math.inf, 'INVALID_STATE_FLOAT')
    return v.hex()

def real_unpack(v, allow_inf=False):
    need(type(v) is str, 'FLOAT_HEX_NOT_STRING')
    x = float.fromhex(v)
    need((math.isfinite(x) or (allow_inf and x == math.inf)) and x.hex() == v,
         'INVALID_OR_NONCANONICAL_FLOAT_HEX')
    return x

def exact_keys(d, keys, where):
    need(type(d) is dict and set(d) == set(keys), 'SCHEMA:' + where)

def boolean(x):
    need(type(x) is bool, 'BOOL_REQUIRED')
    return x

def state_pack(state):
    need(tuple(f.name for f in dataclasses.fields(state)) == FLEET_FIELDS, 'FLEET_STATE_SCHEMA_DRIFT')
    vehicles = []
    for v in state.vehicles:
        s = v.state
        need(tuple(f.name for f in dataclasses.fields(s)) == VEH_FIELDS, 'MCTS_STATE_SCHEMA_DRIFT')
        data = {k:real_pack(getattr(s, k)) for k in VEH_FIELDS[:8]}
        data.update(prev_action=None if s.prev_action is None else int(s.prev_action),
                    collision=boolean(s.collision), goal_reached=boolean(s.goal_reached))
        vehicles.append({'token':v.token, 'state':data})
    return {'schema':'FULL_FLEET_STATE_HEX_V1', 'vehicles':vehicles,
            'internal_collision':boolean(state.internal_collision),
            'minimum_internal_clearance_m':real_pack(state.minimum_internal_clearance_m),
            'conflicting_pairs':[list(x) for x in state.conflicting_pairs],
            'internal_safety_violation':boolean(state.internal_safety_violation),
            'safety_violating_pairs':[list(x) for x in state.safety_violating_pairs]}

def state_unpack(d, api):
    exact_keys(d, ('schema', *FLEET_FIELDS), 'FLEET_SAVED')
    need(d['schema'] == 'FULL_FLEET_STATE_HEX_V1' and type(d['vehicles']) is list, 'STATE_FORMAT')
    items = []
    for v in d['vehicles']:
        exact_keys(v, ('token','state'), 'VEHICLE')
        need(type(v['token']) is str and v['token'] in ('A','B'), 'VEHICLE_TOKEN')
        z = v['state']; exact_keys(z, VEH_FIELDS, 'VEHICLE_STATE')
        kw = {k:real_unpack(z[k], allow_inf=(k=='minimum_clearance_m')) for k in VEH_FIELDS[:8]}
        a = z['prev_action']
        need(a is None or (type(a) is int and a in (0,1,2,3)), 'PREV_ACTION')
        kw.update(prev_action=None if a is None else api['MCTSAction'](a),
                  collision=boolean(z['collision']), goal_reached=boolean(z['goal_reached']))
        items.append(api['FleetVehicleState'](v['token'], api['MCTSState'](**kw)))
    need([x.token for x in items] == ['A','B'], 'VEHICLE_ORDER_OR_DUPLICATE')
    def pair_list(x):
        need(type(x) is list and all(type(p) is list and len(p)==2 and
             all(type(t) is str and t in ('A','B') for t in p) and p[0]!=p[1] for p in x), 'PAIR_LIST')
        return tuple(tuple(p) for p in x)
    result = api['FleetState'](vehicles=tuple(items),
        internal_collision=boolean(d['internal_collision']),
        minimum_internal_clearance_m=real_unpack(d['minimum_internal_clearance_m'], True),
        conflicting_pairs=pair_list(d['conflicting_pairs']),
        internal_safety_violation=boolean(d['internal_safety_violation']),
        safety_violating_pairs=pair_list(d['safety_violating_pairs']))
    need(state_pack(result)==d, 'STATE_ROUNDTRIP_NOT_EXACT')
    return result

def rng_pack(rng):
    v, seq, gauss = rng.getstate()
    need(v==3 and len(seq)==625 and gauss is None, 'RNG_STATE_SCHEMA')
    return {'version':v, 'mt_state':list(seq), 'gauss':None}

def rng_unpack(d):
    exact_keys(d, ('version','mt_state','gauss'), 'RNG')
    need(type(d['version']) is int and d['version']==3 and d['gauss'] is None and
         type(d['mt_state']) is list and len(d['mt_state'])==625 and
         all(type(x) is int and 0<=x<2**32 for x in d['mt_state'][:-1]) and
         type(d['mt_state'][-1]) is int and 0<=d['mt_state'][-1]<=624, 'RNG_INVALID')
    r = random.Random(0)
    r.setstate((3, tuple(d['mt_state']), None))
    need(rng_pack(r)==d, 'RNG_ROUNDTRIP')
    return r

def action_id(a):
    return ','.join(str(int(v)) for v in a.actions)

def terminal_flags(s):
    return {'hard_safety_violation':bool(s.hard_safety_violation),
            'all_goals_reached':bool(s.all_goals_reached)}

def is_true_terminal(s):
    return bool(s.hard_safety_violation or s.all_goals_reached)

def make_root(row,api):
    parts=[]
    for t in ('A','B'):
        v=row['root_state']['vehicles'][t]
        st=api['MCTSState'](time_s=float(row['root_state']['time_s']),route_s=float(v['route_s_m']),
            speed_mps=float(v['speed_mps']),accel_mps2=float(v['accel_mps2']),lead_distance_m=float(v['lead_distance_m']),
            lead_rel_speed_mps=float(v['lead_rel_speed_mps']),target_speed_mps=float(v['target_speed_mps']),
            collision=v['collision'],goal_reached=v['goal_reached'])
        parts.append((t,st))
    root=api['FleetState'].from_states(parts)
    need(len(api['active_joint_actions'](root))==16 and not root.hard_safety_violation and not root.all_goals_reached,'INELIGIBLE_ROOT')
    return root
