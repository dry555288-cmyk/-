# FullMine V4 Cross-scene Dynamic Conclusion V1

## Gate result

**PASS: cross-scene dynamic conclusion gate is closed.**

Final static set: **C04 / C11 / C06**.

All three scenes have:
- real-loader PASS;
- constant-speed NO-MCTS causal physical-conflict PASS;
- post-conflict completion and runtime validity in the authoritative NO-MCTS result.

## Fleet-MCTS result under frozen parameters

Frozen cross-scene parameters: `MCTS_DT=0.5`, `budget=64`, `depth=8`, no retuning.

| Scene | Fleet evidence | Full benchmark | Collision avoidance | Conclusion |
|---|---:|---:|---:|---|
| C04 | seeds 0-4 | 5/5 PASS | 5/5 | robust within this scene |
| C11 | seed 0 | FAIL | PASS | safe but progress/deadlock failure |
| C06 | seed 0 | PASS | PASS | seed0 transfer PASS |

Balanced seed0 comparison across the three scenes:
- full benchmark success: **2/3**
- collision avoidance: **3/3**

The C11 result is a scientific negative result, not a harness crash: it ran the full 89.0 s / 890 steps with `error=None`, no overlap, timeline sync, no invalid state, but did not complete post-conflict passage.

## Claim boundary

Supported:
- frozen-parameter Fleet-MCTS transfers successfully to more than one FullMine conflict scene;
- C04 has 5-seed within-scene robustness;
- frozen parameters are not universally successful across the final three-scene set;
- C11 exposes a safety-vs-progress failure mode that should be retained for later learning/evaluation.

Not supported:
- 3/3 cross-scene benchmark success;
- C11/C06 multiseed robustness;
- a single pooled “7-run success rate” (seed allocation is unbalanced);
- retroactive parameter tuning to remove C11;
- production-authoritative mine-wide drivability.

## Provenance

Input inventory ZIP SHA256:
`e154a78f7e03f79458e4a7c249c01ad98359f7f23311bd437080b939686de239`

Input `inventory.json` SHA256:
`2eddb51786f024324e756d7365054025f10ba4265ffaf3bdde2414ff57daca5d`

See `cross_scene_dynamic_conclusion_v1.json` for exact authoritative artifact paths and SHAs.
