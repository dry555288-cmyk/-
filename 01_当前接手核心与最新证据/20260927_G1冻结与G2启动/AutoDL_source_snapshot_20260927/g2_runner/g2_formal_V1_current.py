#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import traceback

REPO = Path("/root/MineSim-Dynamic")
TMP = Path("/root/autodl-tmp")

RELEASE = (
    TMP / "minesim_h8_guide_eager_vs_lazy_full_v1_retry2_review"
    / "evidence" / "release"
)
ORIGINAL_RUNTIME = (
    RELEASE / "parent" / "base" / "parent" / "core" / "parent"
    / "parent" / "core" / "parent" / "core" / "parent" / "runtime"
)
DEADLOCK_OVERLAY_RUNTIME = (
    TMP / "minesim_g1_deadlock_terminal_runtime_overlay_v1" / "runtime"
)
G1_FREEZE = TMP / "minesim_g1_final_freeze_v1" / "G1_FINAL_FREEZE.json"

OUT = TMP / "minesim_g2_formal_calibration_v1"
CELLS = OUT / "cells"

EXPECTED_HEAD = "112d2bd0f3412fc83b13d5587d2b41402d2d0f5e"
EXPECTED_G1_SHA = "5629cfd987bfd9ebe832c389464de1cad1e4678c5119ccdfa6087ff96ac65b31"

BUDGETS = [2, 4, 8, 16, 32]
DEPTHS = [4, 8, 12]
GAMMA = 0.99
MAX_OUTER_STEPS = 128

# Frozen G1 reward/value contract.
PROGRESS_CAP = 1.0
TIME_COST = -0.05
WAIT_COST_FULL = -0.10
OLD_EFFECTIVE_FIRST_GOAL = 15.0
NEW_FIRST_GOAL = 5.0
GLOBAL_BOTH_PARKED = 20.0


def need(cond, msg):
    if not cond:
        raise RuntimeError(msg)


def sha256(p: Path):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def sh(*args, cwd=None):
    p = subprocess.run(
        list(args),
        cwd=str(cwd) if cwd else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )
    return p.stdout.strip()


def canonical(obj):
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def objsha(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()


def load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def write_json(p: Path, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def repo_precheck():
    need(REPO.is_dir(), "REPO_MISSING")
    need(RELEASE.is_dir(), "RELEASE_MISSING")
    need(ORIGINAL_RUNTIME.is_dir(), "ORIGINAL_RUNTIME_MISSING")
    need(DEADLOCK_OVERLAY_RUNTIME.is_dir(), "DEADLOCK_OVERLAY_RUNTIME_MISSING")
    need(G1_FREEZE.is_file(), "G1_FREEZE_MISSING")
    need(sha256(G1_FREEZE) == EXPECTED_G1_SHA,
         f"G1_FREEZE_SHA_DRIFT:{sha256(G1_FREEZE)}")

    g1 = load_json(G1_FREEZE)
    need(g1.get("g1_status") == "PASS_FROZEN", "G1_NOT_FROZEN")
    need(g1.get("holdout_used") is False, "HOLDOUT_ALREADY_USED")

    head = sh("git", "rev-parse", "HEAD", cwd=REPO)
    status = [
        x for x in sh("git", "status", "--porcelain=v1", cwd=REPO).splitlines()
        if x.strip()
    ]
    need(head == EXPECTED_HEAD, f"HEAD_DRIFT:{head}")
    need(not [x for x in status if not x.startswith("?? ")],
         f"TRACKED_REPO_DIRTY:{status}")
    return head, status


def activate_runtime():
    # Use original runtime for BoundContext / input loaders, but bind candidate_mcts
    # to the G1 deadlock-integrated isolated runtime.
    sys.dont_write_bytecode = True

    original = str(ORIGINAL_RUNTIME)
    overlay = str(DEADLOCK_OVERLAY_RUNTIME)

    # realroute_smoke is from original release.
    if original not in sys.path:
        sys.path.insert(0, original)
    import realroute_smoke as native

    # Force candidate_mcts package activation from deadlock overlay.
    native.activate_package(DEADLOCK_OVERLAY_RUNTIME)

    from candidate_mcts.fleet_search import FleetMCTSSearch
    from candidate_mcts.dual_stop_adapter_v1 import action_id, episode_status

    sig = inspect.signature(episode_status)
    need("deadlock_detector" in sig.parameters,
         "DEADLOCK_INTEGRATION_NOT_PRESENT_IN_OVERLAY")

    return native, FleetMCTSSearch, action_id, episode_status


class G1RewardContract:
    def __init__(self, base):
        self.base = base

    @staticmethod
    def _tokens(state):
        return tuple(state.controlled_tokens)

    def _first_goal_count(self, prev, nxt):
        n = 0
        for token in self._tokens(prev):
            if (not prev.state_for(token).goal_reached
                    and nxt.state_for(token).goal_reached):
                n += 1
        return n

    def _progress_excess(self, prev, nxt):
        count = len(self._tokens(prev))
        total = 0.0
        for token in self._tokens(prev):
            pv = prev.state_for(token)
            nv = nxt.state_for(token)
            if pv.goal_reached:
                continue
            dt = 0.5
            denom = max(float(pv.target_speed_mps) * dt, 1e-6)
            raw = max(0.0, float(nv.route_s) - float(pv.route_s)) / denom
            total += max(0.0, raw - PROGRESS_CAP)
        return total / count

    def _stationary_unfinished_fraction(self, state):
        unfinished = [
            state.state_for(t)
            for t in self._tokens(state)
            if not state.state_for(t).goal_reached
        ]
        if not unfinished:
            return 0.0
        stationary = sum(
            1 for s in unfinished if abs(float(s.speed_mps)) <= 1e-12
        )
        return stationary / len(unfinished)

    def evaluate(self, prev, nxt):
        value = float(self.base.evaluate(prev, nxt))

        # Progress cap.
        value -= self._progress_excess(prev, nxt)

        # Replace old effective +15/vehicle with +5/vehicle.
        first_goals = self._first_goal_count(prev, nxt)
        if first_goals:
            value -= first_goals * OLD_EFFECTIVE_FIRST_GOAL
            value += first_goals * NEW_FIRST_GOAL

        hard = bool(nxt.hard_safety_violation)

        # Global completion bonus.
        if (not prev.all_goals_reached) and nxt.all_goals_reached and not hard:
            value += GLOBAL_BOTH_PARKED

        # Time/wait only on safe, nonterminal continuation.
        if (not hard) and (not nxt.all_goals_reached):
            value += TIME_COST
            value += WAIT_COST_FULL * self._stationary_unfinished_fraction(nxt)

        need(math.isfinite(value), "G1_REWARD_NONFINITE")
        return value


def load_roots():
    roots_path = RELEASE / "ROOTS.json"
    need(roots_path.is_file(), "ROOTS_JSON_MISSING")
    roots = load_json(roots_path)
    need(isinstance(roots, list) and roots, "ROOTS_EMPTY")
    return roots


def build_context(native, root):
    context_path = (
        ORIGINAL_RUNTIME / "inputs" / "contexts"
        / (root["task"]["episode_uid"] + ".json")
    )
    need(context_path.is_file(), f"CONTEXT_MISSING:{context_path}")
    tc = dict(
        candidate_fleet_calls_including_tree_attempted=0,
        candidate_fleet_calls_including_tree_returned=0,
    )
    bc = native.BoundContext(
        ORIGINAL_RUNTIME,
        load_json(context_path),
        counters=tc,
    )
    state = bc.transition.unpack(root["state"])
    packed = bc.transition.pack(state)
    need(canonical(packed) == canonical(root["state"]), "ROOT_ROUNDTRIP")

    # Bind directly to the frozen source-step bytes instead of reimplementing
    # full_eval.py's s.canon()/s.sha serialization.
    source_path = RELEASE / root["source_step"]
    need(source_path.is_file(), f"ROOT_SOURCE_STEP_MISSING:{source_path}")
    raw = source_path.read_bytes()
    need(len(raw) == root["source_size"], "ROOT_SOURCE_SIZE")
    need(hashlib.sha256(raw).hexdigest() == root["source_sha256"],
         "ROOT_SOURCE_SHA")

    hist = json.loads(raw)
    need(hist["step"] == root["source_step_index_0based"],
         "ROOT_SOURCE_STEP_INDEX")
    need(hist["before"] == root["state"],
         "ROOT_SOURCE_BEFORE_STATE")

    need(bool(root.get("exact_before_state_sha256")),
         "ROOT_EXACT_STATE_SHA_MISSING")
    return bc, state, tc


def common_seed(root):
    material = {
        "schema": "G2_COMMON_RANDOM_SEED_V1",
        "root_id": root["root_id"],
        "state_sha256": root["exact_before_state_sha256"],
        "replicate": 0,
    }
    return int(hashlib.sha256(canonical(material)).hexdigest()[:16], 16)


def classify_outcome(episode_status, state, steps, detector):
    # G1 integrated classifier.
    status = episode_status(
        state,
        steps,
        MAX_OUTER_STEPS,
        hard_event_ever=bool(state.hard_safety_violation),
        deadlock_detector=detector,
    )
    # Normalize legacy strings to frozen G1 taxonomy where needed.
    mapping = {
        "BOTH_PARKED_AT_OWN_DESTINATIONS": "SUCCESS",
        "EXECUTED_HARD_SAFETY_TERMINAL": "HARD_SAFETY_TERMINAL",
        "SAFE_DEADLOCK": "SAFE_DEADLOCK",
        "EVALUATION_CAP_NOT_TASK_TERMINAL": "SAFE_INCOMPLETE_CAP",
        "RUNNING": "RUNNING",
    }
    return mapping.get(status, status)


def run_episode(native, FleetMCTSSearch, action_id, episode_status,
                root, budget, depth, technical_only=False):
    bc, state, counters = build_context(native, root)
    reward = G1RewardContract(bc.system.reward)

    seed = common_seed(root)

    searcher = FleetMCTSSearch(
        transition_model=bc.transition,
        reward_model=reward,
        action_provider=bc.transition.active_joint_actions,
        budget=int(budget),
        max_depth=int(depth),
        c_uct=1.4,
        gamma=GAMMA,
        seed=seed,
    )
    detector = getattr(searcher, "deadlock_detector", None)
    need(detector is not None, "SEARCH_DEADLOCK_DETECTOR_MISSING")

    max_steps = 1 if technical_only else MAX_OUTER_STEPS
    rows = []
    discounted_return = 0.0
    wall_ns = 0
    cpu_ns = 0

    initial_status = classify_outcome(episode_status, state, 0, detector)
    need(initial_status == "RUNNING", f"ROOT_NOT_RUNNING:{initial_status}")

    final_outcome = "RUNNING"

    for k in range(max_steps):
        active = list(bc.transition.active_joint_actions(state))
        if not active:
            final_outcome = "NO_ADMITTED_ACTION"
            break

        t0 = time.perf_counter_ns()
        c0 = time.process_time_ns()
        try:
            action, diag = searcher.search(state)
        except Exception as exc:
            name = type(exc).__name__
            msg = str(exc)
            if "no children" in msg.lower() or "no admitted" in msg.lower():
                final_outcome = "NO_ADMITTED_ACTION"
                break
            raise
        c1 = time.process_time_ns()
        t1 = time.perf_counter_ns()

        wall = t1 - t0
        cpu = c1 - c0
        wall_ns += wall
        cpu_ns += cpu

        before = state
        nxt, detail = bc.transition.step_with_diagnostics(state, action)
        r = reward.evaluate(state, nxt)
        discounted_return += (GAMMA ** k) * r

        outcome = classify_outcome(episode_status, nxt, k + 1, detector)

        rows.append({
            "step": k,
            "action_id": action_id(action),
            "reward": r,
            "discounted_reward": (GAMMA ** k) * r,
            "outcome": outcome,
            "search_wall_ms": wall / 1e6,
            "search_cpu_ms": cpu / 1e6,
            "iterations": diag.get("iterations"),
            "elapsed_ms_native": diag.get("elapsed_ms"),
            "visits": diag.get("visits"),
            "q_values": diag.get("q_values"),
            "minimum_clearance_m": diag.get("minimum_clearance_m"),
        })

        state = nxt
        final_outcome = outcome
        if outcome != "RUNNING":
            break

    if (not technical_only
            and final_outcome == "RUNNING"
            and len(rows) >= MAX_OUTER_STEPS):
        final_outcome = "SAFE_INCOMPLETE_CAP"

    return {
        "root_id": root["root_id"],
        "episode_uid": root["task"]["episode_uid"],
        "budget": budget,
        "depth": depth,
        "seed": seed,
        "technical_only": technical_only,
        "steps": len(rows),
        "final_outcome": final_outcome,
        "discounted_return": discounted_return,
        "search_wall_ms_total": wall_ns / 1e6,
        "search_cpu_ms_total": cpu_ns / 1e6,
        "search_wall_ms_mean": (
            wall_ns / 1e6 / len(rows) if rows else None
        ),
        "search_cpu_ms_mean": (
            cpu_ns / 1e6 / len(rows) if rows else None
        ),
        "rows": rows,
        "teacher_sample": False,
        "training_mask": 0,
        "holdout_used": False,
    }


def aggregate(cells):
    groups = {}
    for c in cells:
        key = (c["budget"], c["depth"])
        groups.setdefault(key, []).append(c)

    summary = []
    for (budget, depth), rows in sorted(groups.items()):
        outcomes = {}
        for r in rows:
            outcomes[r["final_outcome"]] = outcomes.get(r["final_outcome"], 0) + 1
        summary.append({
            "budget": budget,
            "depth": depth,
            "n_roots": len(rows),
            "outcomes": outcomes,
            "success_count": outcomes.get("SUCCESS", 0),
            "hard_safety_count": outcomes.get("HARD_SAFETY_TERMINAL", 0),
            "deadlock_count": outcomes.get("SAFE_DEADLOCK", 0),
            "cap_count": outcomes.get("SAFE_INCOMPLETE_CAP", 0),
            "no_admitted_action_count": outcomes.get("NO_ADMITTED_ACTION", 0),
            "mean_discounted_return": sum(r["discounted_return"] for r in rows) / len(rows),
            "mean_search_wall_ms_total": sum(r["search_wall_ms_total"] for r in rows) / len(rows),
            "mean_search_cpu_ms_total": sum(r["search_cpu_ms_total"] for r in rows) / len(rows),
            "mean_steps": sum(r["steps"] for r in rows) / len(rows),
        })
    return summary


def prepare():
    print("=== G2 FORMAL PREPARE (LOW) ===")
    head, status = repo_precheck()
    native, FleetMCTSSearch, action_id, episode_status = activate_runtime()
    roots = load_roots()

    # Restore all formal roots, but do not search.
    restored = []
    for root in roots:
        bc, state, tc = build_context(native, root)
        ids = [
            action_id(a)
            for a in bc.transition.active_joint_actions(state)
        ]
        restored.append({
            "root_id": root["root_id"],
            "episode_uid": root["task"]["episode_uid"],
            "state_sha256": root["exact_before_state_sha256"],
            "admissible_action_ids": ids,
            "action_count": len(ids),
            "common_seed": common_seed(root),
        })

    if OUT.exists():
        raise RuntimeError(f"OUTPUT_NAMESPACE_EXISTS:{OUT}")
    OUT.mkdir(parents=True)

    result = {
        "stage": "G2_FORMAL_PREPARE_V1",
        "status": "PASS",
        "resource": "LOW",
        "head": head,
        "git_status": status,
        "g1_freeze_sha256": sha256(G1_FREEZE),
        "release_roots_sha256": sha256(RELEASE / "ROOTS.json"),
        "root_count": len(roots),
        "roots": restored,
        "matrix": {
            "budgets": BUDGETS,
            "depths": DEPTHS,
            "cells_per_root": len(BUDGETS) * len(DEPTHS),
            "total_cells": len(roots) * len(BUDGETS) * len(DEPTHS),
            "replicates": 1,
            "common_random_seed_across_budget_depth": True,
        },
        "g1_contract": {
            "progress_cap": PROGRESS_CAP,
            "time_cost": TIME_COST,
            "wait_cost_full": WAIT_COST_FULL,
            "per_vehicle_first_parked": NEW_FIRST_GOAL,
            "both_parked_global": GLOBAL_BOTH_PARKED,
            "deadlock_integration_required": True,
        },
        "stage_a": "READY_REQUIRES_HIGH_CPU_AUTHORIZATION",
        "scientific_runtime": False,
        "teacher_collection": False,
        "training": False,
        "holdout_used": False,
        "repo_write": False,
    }
    write_json(OUT / "PREPARE.json", result)

    print("HEAD =", head)
    print("G1_BINDING = PASS")
    print("DEADLOCK_OVERLAY_BINDING = PASS")
    print("FORMAL_ROOT_RESTORATION = PASS")
    print("ROOT_COUNT =", len(roots))
    print("TOTAL_STAGE_A_CELLS =", result["matrix"]["total_cells"])
    print("STAGE_A = READY_REQUIRES_HIGH_CPU_AUTHORIZATION")
    print("SCIENTIFIC_RUNTIME = false")
    print("TEACHER_COLLECTION = false")
    print("HOLDOUT_USED = false")
    print("REPO_WRITE = false")
    print("OUTPUT =", OUT)
    print("PASS:G2_FORMAL_PREPARE_V1")


def stage_a():
    print("=== G2 FORMAL STAGE-A (HIGH-CPU) ===")
    need(os.environ.get("G2_HIGH_CPU_AUTHORIZED") == "YES",
         "HIGH_CPU_NOT_AUTHORIZED")
    need((OUT / "PREPARE.json").is_file(), "RUN_PREPARE_FIRST")

    prep = load_json(OUT / "PREPARE.json")
    need(prep.get("status") == "PASS", "PREPARE_NOT_PASS")
    need(prep.get("holdout_used") is False, "HOLDOUT_ALREADY_USED")

    native, FleetMCTSSearch, action_id, episode_status = activate_runtime()
    roots = load_roots()

    CELLS.mkdir(exist_ok=False)

    # Technical smoke is part of Stage-A execution, not a separate upload.
    smoke_root = roots[0]
    smoke = run_episode(
        native, FleetMCTSSearch, action_id, episode_status,
        smoke_root, budget=1, depth=1, technical_only=True,
    )
    need(smoke["steps"] <= 1, "TECH_SMOKE_STEP_COUNT")
    write_json(OUT / "TECHNICAL_SMOKE.json", smoke)
    print("TECHNICAL_SMOKE = PASS")

    completed = []
    try:
        for root in roots:
            for depth in DEPTHS:
                for budget in BUDGETS:
                    cell_id = f"{root['root_id']}__B{budget}__H{depth}"
                    print("CELL_START =", cell_id, flush=True)
                    result = run_episode(
                        native, FleetMCTSSearch, action_id, episode_status,
                        root, budget=budget, depth=depth, technical_only=False,
                    )
                    result["cell_id"] = cell_id
                    write_json(CELLS / f"{cell_id}.json", result)
                    completed.append(result)
                    print(
                        "CELL_DONE =",
                        cell_id,
                        "OUTCOME =",
                        result["final_outcome"],
                        "STEPS =",
                        result["steps"],
                        "RETURN =",
                        result["discounted_return"],
                        flush=True,
                    )

        summary = aggregate(completed)
        write_json(OUT / "STAGE_A_SUMMARY.json", {
            "stage": "G2_FORMAL_STAGE_A_V1",
            "status": "PASS",
            "cells_completed": len(completed),
            "root_count": len(roots),
            "matrix_summary": summary,
            "teacher_collection": False,
            "training": False,
            "holdout_used": False,
        })

        # Compact CSV for quick inspection.
        csv_path = OUT / "STAGE_A_SUMMARY.csv"
        lines = [
            "budget,depth,n_roots,success_count,hard_safety_count,deadlock_count,"
            "cap_count,no_admitted_action_count,mean_discounted_return,"
            "mean_search_wall_ms_total,mean_search_cpu_ms_total,mean_steps"
        ]
        for r in summary:
            lines.append(",".join(str(r[k]) for k in (
                "budget","depth","n_roots","success_count","hard_safety_count",
                "deadlock_count","cap_count","no_admitted_action_count",
                "mean_discounted_return","mean_search_wall_ms_total",
                "mean_search_cpu_ms_total","mean_steps"
            )))
        csv_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        print("CELLS_COMPLETED =", len(completed))
        print("TEACHER_COLLECTION = false")
        print("TRAINING = false")
        print("HOLDOUT_USED = false")
        print("PASS:G2_FORMAL_STAGE_A_V1")
    except BaseException as exc:
        fail = {
            "stage": "G2_FORMAL_STAGE_A_V1",
            "status": "FAIL",
            "cells_completed": len(completed),
            "exception_type": type(exc).__name__,
            "exception": str(exc),
            "teacher_collection": False,
            "training": False,
            "holdout_used": False,
        }
        write_json(OUT / "STAGE_A_FAILURE.json", fail)
        print("FAIL:G2_FORMAL_STAGE_A_V1")
        print(type(exc).__name__ + ":", exc)
        raise


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("prepare", "stage-a"))
    args = ap.parse_args()
    if args.mode == "prepare":
        prepare()
    else:
        stage_a()


if __name__ == "__main__":
    try:
        main()
    except BaseException:
        traceback.print_exc()
        raise
