"""User-approved, isolated destination-stop motion candidate; NOT a controller.

A command is held for dt. Speed reaches 0/vmax by integration, then remains
at that bound for the rest of the step. No route/velocity snapping is used.
Only the approved ideal settings are supported in V1. There is no safety or
tracking guarantee beyond the explicitly checked one-dimensional envelope.
"""
from __future__ import annotations
from dataclasses import dataclass, replace
import math
from fractions import Fraction
from typing import Dict, Optional, Tuple

from .action_space import ACTION_ACCEL, MCTSAction
from .state import MCTSState
from .transition_model import TransitionConfig, TransitionModel

VERSION = 'DUAL_ONLY_DESTINATION_STOP_CANDIDATE_V1'


class ContractError(ValueError):
    """An input/model binding is invalid. Never silently repair a frozen input."""


class TerminalInfeasible(ContractError):
    """Longitudinal goal bound cannot be honored; NOT an A/B collision flag."""


def need(ok: bool, reason: str) -> None:
    if not ok:
        raise ContractError(reason)


def finite(value: float, name: str) -> float:
    need(not isinstance(value, bool) and isinstance(value, (int, float)), name + ':TYPE')
    value = float(value)
    need(math.isfinite(value), name + ':NONFINITE')
    return value


@dataclass(frozen=True)
class MotionPoint:
    distance_m: float
    speed_mps: float
    actual_accel_mps2: float


@dataclass(frozen=True)
class BoundedMotion:
    v0: float
    command_accel: float
    dt: float = 0.5
    vmax: float = 15.0

    def __post_init__(self) -> None:
        for name in ('v0', 'command_accel', 'dt', 'vmax'):
            finite(getattr(self, name), name)
        need(self.dt > 0 and self.vmax > 0 and 0 <= self.v0 <= self.vmax, 'MOTION_DOMAIN')

    @property
    def zero_time(self) -> Optional[float]:
        if self.v0 == 0 and self.command_accel <= 0:
            return 0.0
        if self.command_accel < 0:
            t = self.v0 / -self.command_accel
            return t if t <= self.dt else None
        return None

    def at(self, time_in_step: float) -> MotionPoint:
        t = finite(time_in_step, 'SAMPLE_TIME')
        need(0 <= t <= self.dt, 'SAMPLE_OUTSIDE_STEP')
        v, a = self.v0, self.command_accel
        if a < 0:
            hit = v / -a
            if t >= hit:
                return MotionPoint(v * v / (-2.0 * a), 0.0, 0.0)
        elif a > 0:
            hit = (self.vmax - v) / a
            if t >= hit:
                distance = math.fsum(((v + self.vmax) * hit * 0.5, self.vmax * (t - hit)))
                return MotionPoint(distance, self.vmax, 0.0)
        else:
            return MotionPoint(v * t, v, 0.0)
        return MotionPoint(v * t + 0.5 * a * t * t, v + a * t, a)


@dataclass(frozen=True)
class DualOnlyState(MCTSState):
    """Native-compatible state with an explicit no-external-object contract.

    The inherited lead slots MUST be +inf/0, which are numeric compatibility
    sentinels, not a measured gap or a third vehicle. The versioned codec emits
    null/NONE rather than serializing an infinite distance as physical evidence.
    accel_mps2 retains the old commanded-acceleration reward convention; actual
    endpoint/mean acceleration is recorded separately in step diagnostics.
    """
    model_version: str = VERSION
    external_lead_mode: str = 'NONE'
    parked_at_time_s: Optional[float] = None

    def transition_cache_key(self) -> Tuple:
        return super().transition_cache_key() + (self.model_version, self.external_lead_mode)


class DestinationStopTransition(TransitionModel):
    """New scalar adapter, leaving frozen TransitionModel unchanged."""
    def __init__(self, config: TransitionConfig, goal_window_m: float = 0.5):
        need(isinstance(config, TransitionConfig), 'TRANSITION_CONFIG_TYPE')
        goal = finite(config.goal_route_s, 'GOAL_ROUTE_S')
        need(goal >= 0.5, 'GOAL_ROUTE_TOO_SHORT')
        need((config.dt, config.accel_max, config.decel_max, config.max_speed)
             == (0.5, 1.0, 3.0, 15.0), 'UNAPPROVED_DYNAMICS_CONFIG')
        need(finite(goal_window_m, 'GOAL_WINDOW') == 0.5, 'UNAPPROVED_GOAL_WINDOW')
        need(tuple(float(ACTION_ACCEL[a]) for a in MCTSAction) == (-3., -1.5, 0., 1.), 'ACTION_MAPPING_DRIFT')
        super().__init__(config)
        self.goal_window_m = goal_window_m

    @property
    def window(self) -> Tuple[float, float]:
        return self.cfg.goal_route_s - self.goal_window_m, self.cfg.goal_route_s

    def is_parked_position(self, s: float, v: float) -> bool:
        low, upper = self.window
        return low <= s <= upper and v == 0.0

    def validate(self, state: DualOnlyState) -> None:
        need(isinstance(state, DualOnlyState), 'LEGACY_STATE_REQUIRES_EXPLICIT_CONVERSION')
        need(state.model_version == VERSION and state.external_lead_mode == 'NONE', 'STATE_SCOPE_MISMATCH')
        need(state.lead_distance_m == math.inf and state.lead_rel_speed_mps == 0.0,
             'EXTERNAL_COMPATIBILITY_SLOTS_NOT_NEUTRAL')
        need(state.minimum_clearance_m == math.inf, 'UNEXPECTED_EXTERNAL_CLEARANCE')
        for n in ('time_s', 'route_s', 'speed_mps', 'accel_mps2', 'target_speed_mps'):
            finite(getattr(state, n), 'STATE.' + n)
        need(state.time_s >= 0 and 0 <= state.route_s <= self.cfg.goal_route_s, 'STATE_TIME_OR_ROUTE_BOUND')
        need(0 <= state.speed_mps <= self.cfg.max_speed, 'STATE_SPEED_BOUND')
        need(state.target_speed_mps > 0, 'CRUISE_NORMALIZER_MUST_REMAIN_POSITIVE')
        need(type(state.goal_reached) is bool and type(state.collision) is bool, 'STATE_FLAG_TYPE')
        need(not state.collision, 'EXTERNAL_COLLISION_FLAG_CANNOT_BE_ERASED')
        need(state.prev_action is None or isinstance(state.prev_action, MCTSAction), 'PREVIOUS_ACTION_TYPE')
        need(state.goal_reached == self.is_parked_position(state.route_s, state.speed_mps), 'PARKED_FLAG_INCONSISTENT')
        if state.goal_reached:
            t = finite(state.parked_at_time_s, 'PARKED_TIME')
            need(0 <= t <= state.time_s, 'PARKED_TIME_OUTSIDE_HISTORY')
        else:
            need(state.parked_at_time_s is None, 'UNPARKED_WITH_PARKED_TIMESTAMP')

    def convert_legacy(self, state: MCTSState, *, confirmed_dual_only: bool,
                       external_tokens: Tuple[str, ...]) -> Tuple[DualOnlyState, Dict]:
        """Explicit MODEL CHANGE, not a replay or a rewrite of old observations."""
        need(confirmed_dual_only is True and type(external_tokens) is tuple and external_tokens == (),
             'EXPLICIT_EMPTY_EXTERNAL_SCOPE_REQUIRED')
        need(isinstance(state, MCTSState) and not isinstance(state, DualOnlyState), 'LEGACY_CONVERSION_INPUT')
        need(type(state.collision) is bool and not state.collision, 'OLD_HARD_FLAG_NOT_REINTERPRETED')
        need(type(state.goal_reached) is bool, 'OLD_GOAL_FLAG_TYPE')
        for n in ('time_s', 'route_s', 'speed_mps', 'accel_mps2', 'target_speed_mps'):
            finite(getattr(state, n), n)
        parked = self.is_parked_position(state.route_s, state.speed_mps)
        need(not state.goal_reached or parked, 'OLD_CROSSING_GOAL_IS_NOT_PARKING')
        new = DualOnlyState(
            time_s=state.time_s, route_s=state.route_s, speed_mps=state.speed_mps,
            accel_mps2=state.accel_mps2, lead_distance_m=math.inf, lead_rel_speed_mps=0.0,
            target_speed_mps=state.target_speed_mps, minimum_clearance_m=math.inf,
            prev_action=state.prev_action, collision=False, goal_reached=parked,
            parked_at_time_s=state.time_s if parked else None)
        self.validate(new)
        audit = {'conversion': 'EXPLICIT_NEW_MODEL_NOT_OLD_TRAJECTORY_REPLAY',
                 'old_lead_distance_m': state.lead_distance_m,
                 'old_lead_rel_speed_mps': state.lead_rel_speed_mps,
                 'new_external_lead_mode': 'NONE', 'old_goal_flag': state.goal_reached,
                 'initial_parked_under_new_contract': parked,
                 'position_speed_time_unchanged': True, 'original_state_mutated': False}
        return new, audit

    def profile(self, state: DualOnlyState, action: MCTSAction) -> BoundedMotion:
        self.validate(state)
        need(isinstance(action, MCTSAction), 'ACTION_ENUM_REQUIRED')
        # Already parked may only receive the original KEEP action, not an override.
        return BoundedMotion(state.speed_mps, float(ACTION_ACCEL[action]), self.cfg.dt, self.cfg.max_speed)

    def action_report(self, state: DualOnlyState) -> Tuple[Dict, ...]:
        self.validate(state)
        rows = []
        upper = self.cfg.goal_route_s
        for action in MCTSAction:
            end = self.profile(state, action).at(self.cfg.dt)
            s1 = math.fsum((state.route_s, end.distance_m))
            stop = math.fsum((s1, end.speed_mps * end.speed_mps / (2.0 * self.cfg.decel_max)))
            finite(stop, 'STOPPING_BOUND')
            # Resolve comparisons extremely close to the bound with exact arithmetic
            # on the supplied binary floats. The ULP band only selects computation
            # precision: it NEVER enlarges the physical goal or permits overshoot.
            exact_margin = None
            band = 16 * math.ulp(max(1.0, abs(stop), abs(upper), abs(state.route_s)))
            if abs(stop - upper) <= band:
                qv = Fraction(state.speed_mps)
                qa = Fraction(float(ACTION_ACCEL[action]))
                qt = Fraction(self.cfg.dt)
                qcap = Fraction(self.cfg.max_speed)
                if qa < 0 and qv + qa * qt <= 0:
                    qdistance = qv * qv / (-2 * qa)
                    qnext_v = Fraction(0)
                elif qa > 0 and qv + qa * qt >= qcap:
                    hit = (qcap - qv) / qa
                    qdistance = (qv + qcap) * hit / 2 + qcap * (qt - hit)
                    qnext_v = qcap
                else:
                    qdistance = qv * qt + qa * qt * qt / 2
                    qnext_v = qv + qa * qt
                qstop = Fraction(state.route_s) + qdistance + qnext_v * qnext_v / (2 * Fraction(self.cfg.decel_max))
                exact_margin = Fraction(upper) - qstop
                allowed = exact_margin >= 0 and s1 <= upper
                stop = float(qstop)
            else:
                allowed = stop <= upper and s1 <= upper
            reason = None if allowed else 'CANNOT_STOP_BY_GOAL_UPPER'
            if state.goal_reached:
                allowed = action == MCTSAction.KEEP
                reason = None if allowed else 'PARKED_KEEP_ONLY'
            rows.append({'action_index': int(action), 'command_accel_mps2': float(ACTION_ACCEL[action]),
                         'next_route_s': s1, 'next_speed_mps': end.speed_mps,
                         'earliest_stop_route_s': stop, 'allowed': allowed, 'rejection_reason': reason,
                         'exact_boundary_checked': exact_margin is not None,
                         'exact_boundary_margin_m': None if exact_margin is None else str(exact_margin)})
        return tuple(rows)

    def actions(self, state: DualOnlyState) -> Tuple[MCTSAction, ...]:
        result = tuple(MCTSAction(r['action_index']) for r in self.action_report(state) if r['allowed'])
        if not result:
            raise TerminalInfeasible('NO_LONGITUDINALLY_FEASIBLE_ACTION; NO_FULL_ACTION_FALLBACK')
        return result

    def step_with_diagnostics(self, state: DualOnlyState, action: MCTSAction) -> Tuple[DualOnlyState, Dict]:
        reports = self.action_report(state)
        need(isinstance(action, MCTSAction), 'ACTION_ENUM_REQUIRED')
        if not reports[int(action)]['allowed']:
            raise TerminalInfeasible('REJECTED_EXECUTION_ACTION:' + str(int(action)))
        profile = self.profile(state, action)
        end = profile.at(self.cfg.dt)
        s1 = reports[int(action)]['next_route_s']
        parked = self.is_parked_position(s1, end.speed_mps)
        event_time = state.parked_at_time_s
        newly_parked = parked and not state.goal_reached
        if newly_parked:
            need(profile.zero_time is not None, 'PARKING_REQUIRES_REAL_ZERO_SPEED_EVENT')
            event_time = state.time_s + profile.zero_time
        next_state = replace(state, time_s=state.time_s + self.cfg.dt, route_s=s1,
                             speed_mps=end.speed_mps, accel_mps2=0.0 if state.goal_reached else float(ACTION_ACCEL[action]),
                             prev_action=action, goal_reached=parked, parked_at_time_s=event_time)
        self.validate(next_state)
        details = {'model_version': VERSION, 'action_index': int(action),
                   'command_accel_mps2': float(ACTION_ACCEL[action]),
                   'actual_accel_end_mps2': end.actual_accel_mps2,
                   'actual_accel_step_mean_mps2': (end.speed_mps - state.speed_mps) / self.cfg.dt,
                   'speed_zero_offset_s': profile.zero_time,
                   'newly_parked': newly_parked, 'parked_event_time_s': event_time,
                   'observed_time_s': next_state.time_s,
                   'rear_axle_remaining_m': self.cfg.goal_route_s - s1,
                   'reward_acceleration_convention': 'COMMAND_NOT_MEASURED_JERK',
                   'longitudinal_actions': reports}
        return next_state, details

    def step(self, state: DualOnlyState, action: MCTSAction) -> DualOnlyState:
        return self.step_with_diagnostics(state, action)[0]
