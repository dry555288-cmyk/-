# PAPER_METHOD_COMPATIBILITY_DECISION_V1

## Decision

**Paper 1 is technically compatible with the current MineSim/Fleet-MCTS architecture, but only as an adapted route-constrained implementation.**
The correct near-term target is not a verbatim reproduction. It is:

`current Fleet-MCTS -> explicit safety/risk evaluator -> safe-node filtering -> Value Network -> value-guided rollout -> cooperation/deadlock handling -> tree reuse`

**Paper 2 is partially compatible.**
Its `simulation -> evaluation -> search` idea is useful now, especially for vehicle/boundary risk annotation. Its full RA-MVSFM + passing-order tree + lane-free motion + OCP stack is not present in the current project and should remain a later optional branch.

## Paper 1 mapping

| Paper component | Current MineSim evidence | Decision |
|---|---|---|
| Centralized multi-agent state | `FleetState` with controlled vehicles | DIRECT |
| Joint action search | `FleetMCTSSearch`; 4x4=16 actions for A/B | DIRECT, route-constrained longitudinal adaptation |
| V2V hard geometry | `FleetTransitionModel` swept internal collision/clearance | DIRECT FOUNDATION |
| External actor prediction | single-ego `GeometryAwareTransitionModel` CV/CTRV | PARTIAL; not currently integrated into A/B-only Fleet benchmark |
| V2H probabilistic human uncertainty | no AV/HDV class-specific probabilistic collision model | MISSING |
| V2R node constraint | MineSim runtime boundary/bitmap checks exist, but no evidence they are inside MCTS tree transition | MISSING IN TREE |
| Dynamic safety threshold | current margins/clearance thresholds are fixed | MISSING |
| Unsafe-node pruning | current search uses collision/safety as terminal/penalty; expansion is not paper-style pre-pruned safe action set | PARTIAL |
| Multi-objective reward | progress/speed/safety/comfort + Fleet internal clearance | STRONG FOUNDATION |
| Waiting-aware cooperation | no accumulated waiting-time adaptive cooperation term | MISSING |
| Learned value predictor | no dedicated value predictor found | MISSING |
| Hybrid learned/random safe rollout | Fleet rollout is random; single rollout is deterministic viability preference | MISSING |
| Root visits/Q diagnostics | already recorded | DIRECT DATA FOUNDATION |
| Tree reuse | each search constructs a new root; no preserved subtree evidence | MISSING |

## Paper 2 mapping

| Paper component | Current MineSim evidence | Decision |
|---|---|---|
| Simulation-evaluation-search paradigm | MCTS transition simulation + metrics/evidence infrastructure | ADAPTABLE |
| Vehicle risk | collision/clearance geometry | ADAPTABLE |
| Boundary risk | runtime bitmap/CollisionLookup exists | ADAPTABLE AFTER TREE HOOK |
| Human uncertainty risk | not modeled probabilistically | MISSING |
| Terrain risk | FullMine terrain/elevation authority is not sufficient for paper-style calibrated risk | HOLD |
| Passing-order MCTS | current tree searches low-level joint longitudinal actions, not order permutations | DIFFERENT ARCHITECTURE |
| RA-MVSFM | not implemented | HOLD |
| Lane-free lateral freedom | current Fleet MCTS is route-constrained | HOLD |
| OCP cooperative trajectory optimizer | not implemented | HOLD |

## Important corrections to the coarse static audit

1. `road_boundary_runtime_check_present=true` means the project contains runtime road-boundary safety machinery. It does **not** prove V2R is evaluated inside every MCTS node.
2. `passing_order_tree_present=true` was a lexical/static hit and is **not sufficient evidence** of a Paper-2-style passing-order search tree.
3. `external_actor_prediction_present=true` applies to the single-ego geometry-aware transition path; the frozen C04/C11/C06 A/B-only Fleet runner uses controlled-vehicle route transitions plus internal A-B geometry and does not thereby prove mixed AV/HDV Fleet search.
4. `hard_collision_terminal_present=true` is weaker than the paper's explicit `Pi_safe` / unsafe-node pruning contract.

## Recommended implementation sequence

1. **Paper1 Safety/Risk Hook Preflight**: locate exact V2R/map APIs and the safest non-invasive hook points.
2. **SafetyRiskEvaluator V0**: read-only evaluator first; no planner behavior change.
3. **Safe-node filter V1**: opt-in search mode; compare against frozen Pure/Fleet baselines.
4. **Dataset Contract V1**: add risk/safety annotations, provenance, terminal/outcome labels; no guessed weights.
5. **Current-semantics recollection** across Dapai, Jiangtong, FullMine with scenario/episode split.
6. **Value Network V1** using MCTS return/outcome under a frozen label contract.
7. **Value-guided rollout V1** following the paper's model-guided rollout idea; mixing coefficient remains an experimental parameter.
8. **Cooperation/deadlock extension** motivated by C11 safe-but-no-progress failure.
9. **Tree reuse** after value-guidance is stable.
10. **Optional Paper-2 branch**: high-level right-of-way/risk-field study; RA-MVSFM/OCP only if separately justified.

## Frozen boundaries

- Do not copy paper reward weights, safety thresholds, rollout mixing coefficient, uncertainty coefficient, or network size without an experiment/freeze.
- Do not add steering/lane-free actions to the current Fleet-MCTS just to mimic the paper.
- Do not treat FullMine Z/terrain as authoritative terrain-risk input.
- Do not relabel C11 as success merely because it avoided collision.
- Do not modify the frozen `112d2bd...` baseline in place.
