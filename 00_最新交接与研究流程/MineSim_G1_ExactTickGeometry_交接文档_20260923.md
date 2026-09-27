# MineSim-Dynamic 神经网络辅助 MCTS 研究交接文档
**版本**：G1 Safety Contract / Exact-Tick Geometry Overlay 阶段交接  
**日期**：2026-09-23  
**项目目录**：`/root/MineSim-Dynamic`  
**数据/实验目录**：`/root/autodl-tmp`  
**当前资源等级**：`LOW`  
**当前总阶段**：`G1`  
**下一阶段 G2 状态**：`HOLD`

---

## 1. 当前结论

当前研究主线保持不变：

> 神经网络直接辅助 MCTS，在不降低任务质量与安全质量的前提下，降低在线搜索预算、CPU、迭代数或节点数，并计入网络前向开销。

当前尚未进入 Teacher Budget×Depth、Teacher 数据采集、训练、剪枝或 HOLDOUT。**唯一有效总 Gate 仍然是 G1：评价 / 安全 / 长期价值契约冻结。**

本轮工作的重点是 G1 中的 hard-safety 几何精确性。截至本交接点，已确认：

1. frozen Retry2 当前 A/B 碰撞检查在每个 0.1 s tick 上使用真实 `BoundedMotion.at(offset)` 的 route position，**不存在 active path 的 0.09 m 线性参数化误差**。
2. hard-safety 所用 footprint 仍来自 `RouteGeometryCache.geometry_at(route_s)`。
3. active cache 为 **1.0 m grid + `round()` 最近格点 lookup**，因此 hard-safety footprint 存在 route-space quantization。
4. 对真实 frozen A/B route 的只读分析得到：A `0.827865658937 m`，B `0.825798103362 m`，pairwise certification gap 上界 `1.653663762299 m`。
5. 当前 hard margin 为 `0.0 m`，所以 cached footprints 不相交不能推出 exact route-pose footprints 不相交。
6. 已建立新的 `/root/autodl-tmp` technical overlay，**不修改 repo、不修改 frozen Retry2 release、不运行 MCTS/Teacher**，并完成 unit smoke。

---

## 2. 当前 Git / 环境冻结状态

```text
HEAD = 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e
tracked repo changes = none
pre-existing untracked = ./^C
```

`./^C` 是历史遗留空文件，**禁止删除或修改**。

Repo 中正式 geometry source：

```text
/root/MineSim-Dynamic/devkit/sim_engine/planning/planner/mcts/geometry_transition_model.py
SHA256 = 8ac6513912c18e761426f86d532ee89774075e0f0e9d2f6bb8aa759e7960976d
```

该文件与 frozen Retry2 runtime 对应文件 byte-identical。

Frozen adapter：

```text
candidate_mcts/dual_stop_adapter_v1.py
SHA256 = 04710705edeea28bf38560fc4e3ce8ee319fc0b6679dbf00bd4c61d897cd4961
```

该 adapter **不是 Git repo tracked source**；provenance 已确认它属于 experiment-only frozen lineage，角色为：

```text
frozen_native_dependency_or_input
```

因此：不得修改 Retry2 frozen release；不得假装 repo 已拥有 `candidate_mcts/dual_stop_adapter_v1.py`；后续 G1 safety 修复必须进入新的 versioned technical namespace，或之后经过明确 Gate 决定正式 source placement。

---

## 3. 已完成的 G1 safety 子 Gate

### 3.1 `G1_ROAD_GEOMETRY_BINDING_V1 = PASS`

已确认 active map：`geojson_full_mine_vector_v2_dev`，`MAP_VERSION = dev-geojson-full-mine-vector-v2`。

Route binding：

```text
A: path-000246 → polygon-000119 road
   path-000249 → polygon-000014 intersection
   path-000242 → polygon-000115 road
B: path-000243 → polygon-000115 road
   path-000263 → polygon-000014 intersection
   path-000265 → polygon-000122 road
```

候选 drivable union：`polygon-000119 ∪ polygon-000014 ∪ polygon-000115 ∪ polygon-000122`。

注意：**V2R hard predicate 仍未实现**；当前 runtime diagnostics 明确为 `road_boundary_status = NOT_EVALUATED`。

### 3.2 `G1_SAFETY_THRESHOLD_ROLE_V1 = PASS`

```text
HARD_V2V_GEOMETRIC_MARGIN_BASELINE = 0.0 m
SOFT_INTERNAL_CLEARANCE_REFERENCE = 3.0 m
SOFT_INTERNAL_CLEARANCE_WEIGHT = 0.5
LEGACY_SCALAR_COLLISION_DISTANCE = 2.0 m
BASE_CLEARANCE_REWARD_WEIGHT = 0.0
```

冻结角色：

```text
PHYSICAL_COLLISION          → HARD
OFF_DRIVABLE_FOOTPRINT      → HARD
POSITIVE_CLEARANCE_BUFFER   → UTILITY / DIAGNOSTIC
DYNAMIC_RISK_MARGIN         → DIAGNOSTIC_ONLY, DEFER HARD PROMOTION
```

### 3.3 `G1_HARD_SAFETY_MARGIN_SPEC_V1 = PASS`

```text
V2V: physical footprint contact/intersection = HARD
V2R: full footprint must remain inside drivable region = HARD
positive clearance buffer: not promoted to HARD in V1
```

### 3.4 `G1_SWEPT_SAFETY_EXACTNESS_V1 = SCIENTIFIC_FAIL`

旧判断：`sampled safe != continuous-time safe`。后续进一步收敛后，V1 当前可验证 safety time domain 被限制为 `0.1 s simulation-time lattice`。连续两个 tick 之间的 collision-free **不在 V1 中声称**，只作为 limitation / stronger future diagnostic。

### 3.5 `G1_ACTIVE_GEOMETRY_MOTION_MODEL_V1 = PASS`

```text
POSE_SOURCE         = ego_path.get_state_at_progress(route_s)
HEADING_SOURCE      = path_state.heading
ROUTE_POSE_ORIGIN   = rear axle
FOOTPRINT_SIZE      = 9.0 m × 4.0 m
REAR_AXLE_TO_CENTER = 2.0 m
ACTIVE_GRID_STEP    = 1.0 m
GEOMETRY_LOOKUP     = nearest cached footprint via round()
```

### 3.6 `G1_ROUTE_HEADING_BOUND_V1 = PASS`

真实 route helper：`route_s = LineString arc length [m]`，`position = line.interpolate(s)`，`heading = atan2(p1 - p0)`。

```text
eps = min(0.5, max(0.05, line.length / 1000.0))
```

只读数值：

```text
A:
ROUTE_LENGTH_M = 494.197407459527
HEADING_EPS_M = 0.494197407460
MAX_HEADING_SNAP_RAD = 0.048214995367
MAX_HEADING_SNAP_DEG = 2.762515743791
WORST_ROUTE_S_SNAP_M = 0.500000000000
CONSERVATIVE_FOOTPRINT_HAUSDORFF_BOUND_M = 0.827865658937

B:
ROUTE_LENGTH_M = 624.608434873028
HEADING_EPS_M = 0.500000000000
MAX_HEADING_SNAP_RAD = 0.047910888140
MAX_HEADING_SNAP_DEG = 2.745091683163
WORST_ROUTE_S_SNAP_M = 0.500000000000
CONSERVATIVE_FOOTPRINT_HAUSDORFF_BOUND_M = 0.825798103362
```

Pairwise conservative bound：`1.653663762299 m`。

### 3.7 `G1_TEMPORAL_ROUTE_MOTION_BOUND_V1 = PASS`

```text
dt = 0.5 s
vmax = 15 m/s
actions = {-3.0, -1.5, 0.0, +1.0} m/s²
collision cadence = 0.1 s
MAX_DELTA_ROUTE_S_PER_0P5S = 7.5 m
MAX_DELTA_ROUTE_S_PER_0P1S_LINEAR_INTERVAL = 1.5 m
```

### 3.8 `G1_TEMPORAL_PARAMETERIZATION_ERROR_V1 = PASS, RESULT NOT APPLICABLE TO ACTIVE PATH`

Analytic endpoint-linearized checker result：最大连续误差 `0.09375 m`，最大 0.1 s tick 误差 `0.09 m`。但 active adapter 后续证明每 tick 直接使用 `profiles[t].at(offset)`，因此冻结修正：

```text
ACTIVE_TICK_ROUTE_S_EXACTNESS = PASS
TEMPORAL_PARAMETERIZATION_ERROR_ACTIVE_PATH = 0
OLD_0.09m_RESULT = NOT_APPLICABLE_TO_ACTIVE_DUAL_STOP_PATH
```

### 3.9 `G1_SIM_TICK_GEOMETRY_EXACTNESS_V1 = PARTIAL PASS`

```text
offset = 0, 0.1, 0.2, 0.3, 0.4, 0.5
route_s = exact BoundedMotion.at(offset)
```

真正剩余 gap：`exact route_s → RouteGeometryCache.geometry_at(route_s) → nearest 1.0 m cached footprint`。

### 3.10 `G1_EXACT_GEOMETRY_PROVIDER_V1 = PASS`

Repo `geometry_transition_model.py` 中不存在独立 `exact_geometry_at()` helper。可复用 exact geometry recipe：

```text
route_s clamp
→ ego_path.get_state_at_progress(route_s)
→ rear_axle_pose
→ translate_longitudinally(rear_axle_to_center)
→ OrientedBox.from_new_pose(ego_box, center_pose).geometry
```

### 3.11 `G1_EXACT_GEOMETRY_PATCH_TARGET_BINDING_V1 = PASS`

正式 repo geometry target：

```text
/root/MineSim-Dynamic/devkit/sim_engine/planning/planner/mcts/geometry_transition_model.py
```

Repo adapter target：`ABSENT`。

### 3.12 `G1_ADAPTER_SOURCE_OWNERSHIP_V1 = PASS`

```text
ADAPTER_OWNERSHIP = EXPERIMENT_ONLY_FROZEN
TRACKED_REPO_OWNER = NONE
```

Frozen lineage 可追到：

```text
original/minesim_c11_original_start_multiseed8_v1/
payload/candidate_mcts/dual_stop_adapter_v1.py
```

provenance role：`frozen_native_dependency_or_input`。

---

## 4. 最新通过 Gate

### `G1_EXACT_TICK_GEOMETRY_OVERLAY_STAGE_V1 = PASS`

技术 overlay namespace：

```text
/root/autodl-tmp/minesim_g1_exact_tick_geometry_v1
```

生成文件：

```text
g1_exact_geometry_overlay_v1.py
SHA256 = fb2896b21c872c12db6e4fad2d0fe97b71a4a553e70b5df157b6cae41ea9e81a
size = 4808

smoke_v1.py
SHA256 = 77125fe0fd4e2646185fc410db316c01230dbe326dd1ce7ba668b146cd4fb110
size = 3714
```

Staging launcher：

```text
G1_EXACT_TICK_GEOMETRY_OVERLAY_STAGE_V1.py
SHA256 = 2ea04d8462dc3e54e39b368946d68ef44f7374d7c1a34b788e6c32238243609f
```

Unit smoke 关键结果：

```text
OVERLAY_VERSION = G1_EXACT_TICK_GEOMETRY_OVERLAY_V1
CACHE_QUERY_S = 0.49
CACHED_CENTROID_X = -0.0
EXACT_CENTROID_X = 0.4900000000000001
FROZEN_CACHE_COLLISION = False
EXACT_PROVIDER_COLLISION = True
GUIDE_CACHE_PRESERVED = yes
PASS:G1_EXACT_TICK_GEOMETRY_OVERLAY_UNIT_V1
```

安全属性：

```text
REPO_WRITE = false
SCIENTIFIC_RUNTIME = false
TEACHER_COLLECTION = false
GIT_STATUS_AFTER = ['?? ^C']
PASS:G1_EXACT_TICK_GEOMETRY_OVERLAY_STAGE_V1
```

含义：exact provider 确实绕过 1 m cache snapping；hard-safety `_geometry()` 可以使用 exact provider；原 frozen cache 仍可供 guide/phase diagnostics 使用；repo 与 frozen Retry2 release 均未改；未进行任何科学实验。

---

## 5. 当前唯一 blocker / Gate

```text
G1_EXACT_TICK_GEOMETRY_REALROUTE_SMOKE_V1
```

目标：在真实 frozen A/B route 上验证 exact provider 与 frozen cache provider 的绑定、pose、clearance/collision 调用链；证明 hard-safety technical overlay 在真实 route 上使用 exact geometry，而 guide cache 仍保持原 1 m grid 语义。

当前状态：

```text
G1_EXACT_TICK_GEOMETRY_REALROUTE_SMOKE_V1 = NOT_RUN
```

---

## 6. 下一步最小行动

下一步不要改 repo，不跑 Teacher，不跑 full MCTS。先构造 read-only / technical real-route smoke，输入直接使用 frozen Retry2：

```text
runtime/reference_paths.json
runtime/definitions/route_helpers.py
runtime/inputs/contexts/C11_100M_SEED0_EP1.json
runtime/inputs/contexts/C11_80M_SEED0_EP0.json
```

Smoke 至少验证：

```text
A/B route tokens exact match
vehicle params = (9,4,2)
cache grid = 1.0 m
exact provider route pose == RouteAdapter exact pose
exact provider != cache lookup at non-grid route_s
exact hard-safety _geometry() uses exact provider
guide cache object remains frozen cache
repo status unchanged
no MCTS search
no Teacher collection
no training
```

建议 PASS 标准：

```text
REAL_ROUTE_BINDING = PASS
EXACT_PROVIDER_ROUTE_POSE = PASS
HARD_SAFETY_USES_EXACT_GEOMETRY = PASS
GUIDE_CACHE_PRESERVED = PASS
REPO_WRITE = false
SCIENTIFIC_RUNTIME = false
TEACHER_COLLECTION = false
```

---

## 7. G1 尚未完成的核心事项

即使 exact-tick A/B geometry technical chain 继续 PASS，**整个 G1 仍然 HOLD**。后续仍需逐 Gate 冻结：

```text
1. V2R road/drivable footprint hard predicate
2. deadlock formal terminal definition
3. time/wait utility
4. speed/comfort utility scale
5. success bonus bound
6. deadlock penalty bound
7. utility weights
8. gamma / horizon unit contract
9. long-horizon risk horizon / aggregation / unit scale
10. hard-safety / task-terminal / utility 最终完整 contract
```

特别是当前 `road_boundary_status = NOT_EVALUATED`，不能因为 V2V exact geometry 修复就宣称 V2R 已解决。

---

## 8. Outcome taxonomy

```text
SUCCESS
HARD_SAFETY_TERMINAL
SAFE_DEADLOCK
SAFE_INCOMPLETE_CAP
PLANNING_DEADLINE_FAILURE
NO_ADMITTED_ACTION
RUNNING
```

其中：destination-stop 才是 success；route-end alone 不是 success；CAP128 是 evaluation stop，不是 task terminal；deadline/no admitted action 是 execution failure；deadlock numeric definition 仍 HOLD。

---

## 9. Hard / utility / diagnostic 角色

```text
PHYSICAL_INVALID
- illegal action
- invalid state

HARD_CONSTRAINT
- physical A/B footprint collision
- future V2R off-drivable footprint

TASK_TERMINAL
- destination-stop success
- future formal safe-deadlock failure

UTILITY
- route progress
- bounded speed/efficiency
- comfort / jerk
- future per-step time/wait
- current positive-clearance shaping

DIAGNOSTIC_ONLY
- Y64
- stationary diagnostics
- CPU/wall/iterations/nodes
- PET/MMTTC/risk sidecars initially
- continuous-between-ticks collision proof in V1
```

---

## 10. 明确禁止事项

```text
- 不进入 G2 Teacher Budget×Depth
- 不采新 Teacher
- 不训练神经网络
- 不做 hard pruning
- 不跑 HOLDOUT
- 不修改 frozen Retry2 release
- 不删除 ./^C
- 不 git reset --hard
- 不 git clean -fd
- 不 git add .
- 不把 3 m soft clearance 偷偷升级为 hard threshold
- 不把 0.09 m analytic linearization error 继续当成 active runtime error
- 不把 exact-tick V2V overlay PASS 误写成整个 G1 PASS
- 不把 V2V exact geometry PASS 误写成 V2R 已解决
```

---

## 11. 关键路径

```text
Repo:
/root/MineSim-Dynamic

Frozen Retry2:
/root/autodl-tmp/minesim_h8_guide_eager_vs_lazy_full_v1_retry2/

Review/release:
/root/autodl-tmp/minesim_h8_guide_eager_vs_lazy_full_v1_retry2_review/evidence/release

Current G1 exact geometry overlay:
/root/autodl-tmp/minesim_g1_exact_tick_geometry_v1
```

关键 frozen files：

```text
candidate_mcts/dual_stop_adapter_v1.py
candidate_mcts/dual_stop_motion_v1.py
candidate_mcts/fleet_collision.py
definitions/route_helpers.py
engine/devkit/sim_engine/planning/planner/mcts/geometry_transition_model.py
reference_paths.json
inputs/contexts/C11_100M_SEED0_EP1.json
inputs/contexts/C11_80M_SEED0_EP0.json
```

---

## 12. 继续工作的标准开场

```text
资源：LOW

当前总 Gate：
G1 = HOLD

最近已 PASS：
G1_EXACT_TICK_GEOMETRY_OVERLAY_STAGE_V1

当前唯一下一 Gate：
G1_EXACT_TICK_GEOMETRY_REALROUTE_SMOKE_V1

本步：
真实 frozen A/B route technical smoke，只验证 exact geometry hard-safety 技术链。

PASS：
real-route binding / exact provider / hard-safety exact geometry /
guide cache preservation / repo unchanged 全部通过。

FAIL：
仅定位 real-route overlay technical binding。
不扩大到 reward / deadlock / Teacher / network。

下一阶段：
G2 不允许进入。
```

---

## 13. 最终交接状态

```text
PROJECT = MineSim-Dynamic neural-guided MCTS
HEAD = 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e

G0 = frozen baseline available
G1 = HOLD
G2+ = NOT AUTHORIZED

LATEST_GATE = G1_EXACT_TICK_GEOMETRY_OVERLAY_STAGE_V1
LATEST_GATE_RESULT = PASS

REPO_WRITE = false
SCIENTIFIC_RUNTIME = false
TEACHER_COLLECTION = false

NEXT_GATE = G1_EXACT_TICK_GEOMETRY_REALROUTE_SMOKE_V1
RESOURCE = LOW
```

**交接到此为止。**
