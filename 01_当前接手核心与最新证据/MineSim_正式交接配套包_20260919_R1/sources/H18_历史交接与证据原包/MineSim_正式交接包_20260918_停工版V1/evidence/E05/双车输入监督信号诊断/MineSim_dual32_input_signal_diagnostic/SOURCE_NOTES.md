# 本次使用的源码位置

## parent_core.py

15: def four_direction(a,b):
16:     need(len(a)==len(b)==4,'FOUR_PER_BLOCK')
17:     t=1e-9*max(1.,*(abs(x) for x in a+b))
18:     return 1 if min(a)>max(b)+t else -1 if min(b)>max(a)+t else None
19: 
20: 
21: def feature26(state):
22:     v=[]
23:     for name in ('A','B'):
24:         s=state['vehicles'][name];lo,hi=s['goal_window_m']
25:         p=s['route_s'];speed=s['speed_mps'];prev=s['prev_action']
26:         need(hi>0 and type(s['goal_reached']) is bool and
27:              (prev is None or type(prev) is int and prev in (0,1,2,3)),'STATE_FEATURE_SCHEMA')
28:         v += [p/hi,(lo-p)/hi,(hi-p)/hi,speed/15.,s['accel_mps2']/3.,
29:               s['target_speed_mps']/15.,(hi-p-speed*speed/6.)/hi,
30:               float(s['goal_reached'])]+[float(prev==a) for a in (None,0,1,2,3)]
31:     need(len(v)==26 and all(math.isfinite(x) for x in v),'FINITE_FEATURE26')
32:     return list(struct.unpack('<26f',struct.pack('<26f',*v)))
33: 
34: 

## dual_stop_adapter_v1.py

91:     def step_with_diagnostics(self, state: FleetState, joint_action: JointAction):
92:         self.validate_fleet(state)
93:         need(not state.hard_safety_violation, 'DO_NOT_ADVANCE_HARD_TERMINAL')
94:         need(isinstance(joint_action, JointAction) and set(joint_action.vehicle_tokens) == {'A', 'B'}, 'ACTION_TOKENS')
95:         nxt, profiles, detail = {}, {}, {}
96:         for t in ('A', 'B'):
97:             model = self._vehicle_transitions[t]
98:             a = joint_action.action_for(t)
99:             before = state.state_for(t)
100:             # step_with_diagnostics rejects an infeasible or non-KEEP parked action.
101:             nxt[t], detail[t] = model.step_with_diagnostics(before, a)
102:             profiles[t] = model.profile(before, a)
103:         dt = self._vehicle_transitions['A'].cfg.dt
104:         n = max(1, math.ceil(dt / self.internal_collision_sample_dt_s))
105:         minimum = math.inf
106:         conflicts, unsafe, samples = set(), set(), []
107:         for i in range(n + 1):
108:             offset = dt * i / n
109:             positions = {t: math.fsum((state.state_for(t).route_s, profiles[t].at(offset).distance_m))
110:                          for t in ('A', 'B')}
111:             # Last sample must equal the actual transition state, not a separate integrator.
112:             if i == n:
113:                 need(all(positions[t] == nxt[t].route_s for t in ('A', 'B')), 'SAMPLE_ENDPOINT_MISMATCH')
114:             r = self._geometry(positions)
115:             minimum = min(minimum, r.minimum_internal_clearance_m)
116:             conflicts.update(r.conflicting_pairs)
117:             unsafe.update(r.safety_violating_pairs)
118:             samples.append({'offset_s': offset, 'route_s': positions,
119:                             'minimum_clearance_m': r.minimum_internal_clearance_m,
120:                             'collision': r.internal_collision, 'safety_violation': r.internal_safety_violation})
121:         result = FleetState.from_states(nxt.items())
122:         result = replace(result, internal_collision=bool(conflicts), minimum_internal_clearance_m=minimum,
123:                          conflicting_pairs=tuple(sorted(conflicts)), internal_safety_violation=bool(unsafe),
124:                          safety_violating_pairs=tuple(sorted(unsafe)))
125:         return result, {'model_version': VERSION, 'vehicles': detail, 'collision_samples': samples,
126:                         'geometry_scope': 'SAMPLED_AB_ONLY_CALLER_BOUND_GEOMETRY_NOT_CONTINUOUS_PROOF',
127:                         'road_boundary_status': 'NOT_EVALUATED', 'joint_action_id': action_id(joint_action)}

132:     def pack(self, state: FleetState) -> Dict:
133:         """Versioned JSON-safe codec. NONE is distinct from absent/unknown data."""
134:         self.validate_fleet(state)
135:         cars = {}
136:         for t in ('A', 'B'):
137:             s = state.state_for(t)
138:             cars[t] = {k: getattr(s, k) for k in ('time_s', 'route_s', 'speed_mps', 'accel_mps2',
139:                        'target_speed_mps', 'goal_reached', 'collision', 'parked_at_time_s')}
140:             cars[t].update(prev_action=None if s.prev_action is None else int(s.prev_action),
141:                            external_lead={'mode': 'NONE', 'distance_m': None, 'relative_speed_mps': None},
142:                            minimum_external_clearance_m=None,
143:                            goal_window_m=list(self._vehicle_transitions[t].window),
144:                            acceleration_semantics='COMMANDED_NOT_MEASURED')
145:         clearance = state.minimum_internal_clearance_m
146:         need((math.isfinite(clearance) and clearance >= 0) or clearance == math.inf, 'BAD_PACKED_CLEARANCE')
147:         return {'schema': CODEC, 'model_version': VERSION, 'vehicles': cars,
148:                 'internal_collision': state.internal_collision,
149:                 'internal_safety_violation': state.internal_safety_violation,
150:                 'minimum_internal_clearance_m': None if clearance == math.inf else clearance,
151:                 'internal_clearance_status': 'UNMEASURED' if clearance == math.inf else 'SAMPLED',
152:                 'conflicting_pairs': [list(p) for p in state.conflicting_pairs],
153:                 'safety_violating_pairs': [list(p) for p in state.safety_violating_pairs]}

