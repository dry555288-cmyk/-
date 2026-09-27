"""Flat, exact memoization of scalar action reports; no tree-statistics reuse.

Every request validates the state. Full dataclass fields and type-sensitive
float.hex identities remain in the key. Schema accessors are prepared once.
Returned four report dictionaries are copied independently; their values must
be immutable builtins. Geometry, rewards, RNG, action rules and Q are untouched.
"""
from __future__ import annotations
from collections import OrderedDict
from dataclasses import fields, is_dataclass
from enum import Enum
from operator import attrgetter


def atom(value):
    t = type(value)
    if t is float:
        if value != value:
            raise ValueError('NAN_CACHE_KEY')
        return (float, value.hex())
    if t in (type(None), bool, int, str):
        return (t, value)
    if isinstance(value, Enum):
        return (t, atom(value.value))
    raise TypeError('UNSUPPORTED_FLAT_KEY:' + t.__qualname__)


def clone_report(report):
    # Valid only after ensure_flat_report, or for an already-validated entry.
    return tuple(row.copy() for row in report)


def ensure_flat_report(report):
    if type(report) is not tuple:
        raise TypeError('REPORT_TUPLE_REQUIRED')
    for row in report:
        if type(row) is not dict or any(type(k) is not str for k in row):
            raise TypeError('REPORT_ROW_SCHEMA')
        if any(type(v) not in (type(None), bool, int, float, str) for v in row.values()):
            raise TypeError('MUTABLE_OR_UNSUPPORTED_REPORT_VALUE')


class ExactReportCache:
    """Interface retained for the already-tested experiment harness."""
    def __init__(self, model, *, enabled, capacity=4096):
        if type(enabled) is not bool or type(capacity) is not int or capacity < 1:
            raise ValueError('CACHE_CONFIG')
        self.model = model
        self.enabled = enabled
        self.capacity = capacity
        self.original = model.action_report
        self.had_override = 'action_report' in model.__dict__
        self.previous_override = model.__dict__.get('action_report')
        self.globals = self.original.__func__.__globals__
        self.entries = OrderedDict()
        self.config_key = None
        self.decision = -1
        self.schemas = {}
        self.stats = {'requests': 0, 'full_report_evaluations': 0, 'hits': 0,
                      'cross_decision_hits': 0, 'evictions': 0,
                      'config_invalidations': 0, 'additional_validation_calls': 0}
        self._installed = False

    def flat_dataclass(self, obj):
        typ = type(obj)
        getter = self.schemas.get(typ)
        if getter is None:
            if not is_dataclass(obj) or isinstance(obj, type):
                raise TypeError('FLAT_DATACLASS_REQUIRED')
            names = tuple(f.name for f in fields(obj))
            if len(names) < 2:
                raise TypeError('DATACLASS_SCHEMA_TOO_SHORT')
            # Source and dataclass schemas are immutable, SHA-bound in this probe.
            getter = attrgetter(*names)
            self.schemas[typ] = getter
        return (typ, tuple(map(atom, getter(obj))))

    @staticmethod
    def map_key(mapping):
        if type(mapping) is not dict:
            raise TypeError('ACTION_MAPPING_DICT_REQUIRED')
        # Insertion order is conservatively retained: reordering causes a miss,
        # never a wrong hit. Values and keys are re-read on EVERY request.
        return tuple((atom(k), atom(v)) for k, v in mapping.items())

    def configuration(self):
        a = self.model.action_to_accel
        b = self.globals['ACTION_ACCEL']
        ak = self.map_key(a)
        return (self.flat_dataclass(self.model.cfg), atom(self.model.goal_window_m),
                ak, ak if a is b else self.map_key(b), atom(self.globals['VERSION']))

    def install(self):
        if self._installed:
            raise RuntimeError('CACHE_ALREADY_INSTALLED')
        self.model.action_report = self.report
        self._installed = True

    def close(self):
        if self._installed:
            if self.had_override:
                self.model.action_report = self.previous_override
            else:
                del self.model.__dict__['action_report']
        self._installed = False
        self.entries.clear()

    def begin_decision(self, n):
        self.decision = n

    def report(self, state):
        self.stats['requests'] += 1
        if not self.enabled:
            self.stats['full_report_evaluations'] += 1
            return self.original(state)
        self.stats['additional_validation_calls'] += 1
        self.model.validate(state)
        config = self.configuration()
        if config != self.config_key:
            if self.config_key is not None:
                self.stats['config_invalidations'] += 1
            self.entries.clear()
            self.config_key = config
        key = self.flat_dataclass(state)
        entry = self.entries.get(key)
        if entry is not None:
            saved, epoch = entry
            self.entries.move_to_end(key)
            self.stats['hits'] += 1
            if epoch < self.decision:
                self.stats['cross_decision_hits'] += 1
            return clone_report(saved)
        self.stats['full_report_evaluations'] += 1
        report = self.original(state)
        ensure_flat_report(report)
        self.entries[key] = (clone_report(report), self.decision)
        if len(self.entries) > self.capacity:
            self.entries.popitem(last=False)
            self.stats['evictions'] += 1
        return report

    def snapshot(self):
        return dict(self.stats, entries=len(self.entries), decision=self.decision)
