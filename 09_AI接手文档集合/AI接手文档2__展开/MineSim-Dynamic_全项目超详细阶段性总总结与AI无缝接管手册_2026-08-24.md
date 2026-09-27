**MineSim-Dynamic**

**全项目超详细阶段性总总结与 AI 无缝接管手册**

Evidence cutoff：2026-08-24（包含 C03 Full Collection 与 Value V2 静态接入最新进展）

**主线：MineSim 复现 → 蒙特卡洛/MCTS 接入 → 单车跑通 → 双车冲突场景构建 → FullMine 新地图接入 → Fleet-MCTS 双车联合规划与多种子验证 → 原生 MineSim 可视化与汇报材料 → 云端文件安全整理 → 后续神经网络接入**

用途：供下一位 AI / 工程人员在不重新扫描全项目、不重复已冻结实验、不重新询问大量背景的前提下，安全、低成本、可复现地继续推进。

正式仓库：/root/MineSim-Dynamic  
实验数据根：/root/autodl-tmp  
当前冻结 HEAD：112d2bd0f3412fc83b13d5587d2b41402d2d0f5e

# 文档控制与证据口径

| **项目**     | **当前定义**                                                                                                                                      |
|--------------|---------------------------------------------------------------------------------------------------------------------------------------------------|
| 证据截止     | 2026-08-24；包含本轮 C03 causal/technical smoke/full collection 与 Value V2 evaluator 静态清点。                                                  |
| 事实优先级   | 当前 AutoDL 终端 / Git / 源码 / 文件 SHA / 实际运行输出 \> frozen result/manifest/lock/bundle \> 最新交接 Word \> 历史 Word \> 计划 \> 模型记忆。 |
| 作者归属     | 云端脚本、锁与日志可以证明“实际完成了什么”，但并非每个文件有独立 Codex 作者签名；本文不虚构逐文件作者。                                           |
| 失败分类     | 必须区分 wrapper/import/path/runtime contract/technical/scientific。文件存在不等于 PASS；需结合 RC、JSON、结果字段与 gate。                       |
| 未验证规则   | 任何缺少直接证据的内容标记“未验证/HOLD”；不得用常识补齐。                                                                                         |
| 文档适用范围 | 当前综合接手文档覆盖会话中可见项目材料；不等于实时枚举 AutoDL 上全部文件。                                                                        |

本文整合了 2026-08-18、08-21、08-23 三版综合接手手册、RADEME、项目压缩包/冻结包、2026-08-23～08-24 终端日志，以及本轮 C03 与 Value V2 静态审计的真实输出。旧文档中的“下一步”仅作为历史快照；与更晚终端结果冲突时自动降级。

证据来源：MineSim-Dynamic_全项目阶段性总总结与AI无缝接管手册_2026-08-18/21/23.docx；RADEME.txt；20260823-20260824 终端日志。

# 静态目录

| **目录 1–12**                                                 | **目录 13–23**                                   |
|---------------------------------------------------------------|--------------------------------------------------|
| 1\. 当前项目 30 秒状态与快速结论                              | 13\. 重要失败、排查与永久禁忌                    |
| 2\. 真实发展时间线                                            | 14\. 当前有效 / SUPERSEDED / ARCHIVE / HOLD 矩阵 |
| 3\. 运行架构、核心调用链与依赖边界                            | 15\. 关键 Commit / Tag / SHA 速查                |
| 4\. 阶段一：MineSim 原项目复现与 IDM Baseline                 | 16\. 当前云端目录、依赖和恢复方式                |
| 5\. 阶段二：蒙特卡洛 / Pure MCTS 接入                         | 17\. 运行环境、资源与统一命令规范                |
| 6\. 阶段三：单车跑通                                          | 18\. 用户—ChatGPT—Codex 协作规则                 |
| 7\. 阶段四：双车冲突场景、MultiEgoRuntime 与 causal benchmark | 19\. 文档生成、归档、移动与删除情况              |
| 8\. 阶段五：FullMine 新地图接入与 Vector V4 冻结              | 20\. 会话材料与压缩包清单                        |
| 9\. 阶段六：Fleet-MCTS 联合规划、多种子与跨场景结论           | 21\. 快速接手区                                  |
| 10\. 阶段七：原生 MineSim 可视化与汇报材料                    | 附录 A：统一 preflight / recovery checklist      |
| 11\. 阶段八：云端文件安全整理、目录系统与恢复                 | 附录 B：本交付压缩包文件 Manifest                |
| 12\. 阶段九：后续神经网络接入与当前 C03 / Value V2 进展       |                                                  |

# 1. 当前项目 30 秒状态与快速结论

| **阶段**                   | **状态**           | **当前真实结论**                                                                                                                               |
|----------------------------|--------------------|------------------------------------------------------------------------------------------------------------------------------------------------|
| MineSim 原项目复现         | PASS / FROZEN      | Dapai/Jiangtong IDM、replay 与 closed-loop baseline 已建立；不重做。                                                                           |
| Pure MCTS 接入             | PASS / FROZEN      | 真实 MineSim online closed-loop 已跑通，历史 strict expert 448 条。                                                                            |
| 单车跑通                   | PASS / FROZEN      | J117 Phase4C 423 steps；FullMine representative Pure MCTS 3/3。                                                                                |
| 双车冲突场景               | PASS / FROZEN      | J117、Polygon21 与 cross-scene 通过 NO-MCTS exact footprint overlap 建 causal benchmark。                                                      |
| FullMine 新地图            | PASS / FROZEN      | Vector V2 semantic + V4 bitmap/runtime/planner，targeted 7/7 + old-map regression。                                                            |
| Fleet-MCTS                 | PASS + 负结果      | Polygon21 5/5；C04/C06 success；C11 安全但 deadlock，必须保留。                                                                                |
| 原生可视化                 | PASS / FROZEN      | Native Video V2 final；Map Showcase V2 stable；V3 incomplete/HOLD。                                                                            |
| 云端整理                   | PASS / COMPLETE    | 约 530→121；423 move/isolate；科研文件删除 0；restore gate PASS。                                                                              |
| C03 independent collection | PASS / FROZEN      | 135 roots、2160 action records、8640 expansions，benchmark_success=True。                                                                      |
| Value V2 接入              | STATIC PREP / HOLD | metric closure、feature/model inventory、inference source inventory已锁；真实 C03 checkpoint load/forward/prediction/metrics均未执行、未授权。 |

当前真正节点：C03 full collection 已冻结，Value V2 evaluation 的 metric 侧已完成 exact closure synthetic PASS；12维冻结 feature 顺序、normalization 与模型结构已确认。下一步不是训练或直接 forward，而是低资源锁定“嵌套 JSON feature mapping + 已证明的 checkpoint load/forward chain”，再做 synthetic checkpoint-compatible forward；真实 C03 one-time evaluation 仍未授权。

资源判断：当前下一步仅低资源 CPU；不要开高资源卡。只有完整 evaluator 静态链和 synthetic forward PASS 后，才讨论唯一一次真实 C03 Value V2 forward。

# 2. 真实发展时间线

| **日期**          | **阶段**                              | **真实完成与意义**                                                                                                                              |
|-------------------|---------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------|
| 2026-07-26        | 云端 baseline / 安全操作规范          | AutoDL 安全交互、Git 恢复、文件优先、“先读接口再改代码”。                                                                                       |
| 2026-07-30～08-02 | Pure MCTS closed-loop                 | MCTSPlanner→search/reward→trajectory adapter→Controller/KBM；commit 94693dc；448 strict expert。                                                |
| 2026-08-03～07    | 五 Planner / budget / interface audit | MCTS、IDM、Frenet、Adapted Maneuver、Simple；形成搜索/adapter/controller故障分域。                                                              |
| 2026-08-08～10    | 双受控 + J117                         | Jiangtong负筛选；J117单车423步；双车NO-MCTS冲突+Pure MCTS 5-seed。                                                                              |
| 2026-08-11～14    | FullMine V1→Vector V4                 | O(1) token lookup、Vector V2 semantic、bitmap/runtime/planner修复；V4 freeze HEAD 112d2bd。                                                     |
| 2026-08-14        | Representative Pure MCTS              | 跨代表区域3/3 PASS并冻结。                                                                                                                      |
| 2026-08-15        | Polygon21 Fleet-MCTS                  | NO-MCTS真实物理重叠；Fleet budget64/depth8 5/5。                                                                                                |
| 2026-08-16        | Native Video + safe cleanup           | Native Video V2 final；Phase2A–2K可逆整理；Map Showcase V3 SIGKILL未收口。                                                                      |
| 2026-08-17～18    | Cross-scene + Paper1 safety           | C04/C11/C06收口；C11安全死锁负结果；SafetyRisk V0/sidecar推进。                                                                                 |
| 2026-08-21        | current-semantic NN链                 | V2R/zone/dynamic V2V/shadow/dataset/collector；C04/C11/C06 collection；Value V1 LOSO science FAIL。                                             |
| 2026-08-22～23    | Value V2 + C13 independent            | final-dev模型冻结；C13 115 roots/1840 rows；forward一次但metric绑定失败，scientific metrics未评估，禁止重跑。                                   |
| 2026-08-23        | replacement C03 qualification         | C10/C14淘汰；C03 physical/static/NO-MCTS causal qualification推进并最终冻结。                                                                   |
| 2026-08-24        | C03 collector与Value V2准备           | one-step technical smoke PASS；Full Collection 135 roots/2160 rows PASS；metric closure与feature/model inventory PASS；真实Value V2评估未打开。 |

# 3. 运行架构、核心调用链与依赖边界

run_simulation.py  
→ SimulationsRunner.\_initialize()  
→ EnvironmentSimulation.initialize()  
→ Scenario / Map loader  
→ Planner.initialize()  
→ 每帧 Planner.compute_planner_trajectory()  
→ TwoStageController.update_state()  
→ LQR / iLQR trajectory tracking  
→ KinematicBicycleModel.propagate_state()  
→ Agent Update Policy / Observation  
→ SimulationHistory / metrics / log  
→ 下一帧

系统边界：项目没有重写完整 MineSim。Pure MCTS / Fleet-MCTS 主要替换或扩展 Planner 决策层；规划轨迹仍必须由 Controller 和车辆模型真实执行。Scenario、Map、Observation、Controller、Vehicle、History/Metrics 都是科学链的一部分，不能绕过。

| **层**               | **关键代码/目录**                                                                | **职责与接手风险**                                                             |
|----------------------|----------------------------------------------------------------------------------|--------------------------------------------------------------------------------|
| Scenario/Environment | devkit/sim_engine/environment_manager/；scenario_manager/；EnvironmentSimulation | Scenario schema、location、绝对路径不可猜。                                    |
| Map                  | devkit/sim_engine/map_manager/；semantic/bitmap loader                           | semantic identity、bitmap symlink、scale/flip、SHA不可随意改。                 |
| Planning             | devkit/sim_engine/planning/planner/；local_planner/                              | 遵守AbstractPlanner；future trajectory不是下一帧状态。                         |
| Pure MCTS            | local_planner/mcts_planner.py；planner/mcts/\*.py                                | state/action/search/reward/geometry/adapter语义必须一致。                      |
| Multi/Fleet          | mcts/multi_ego_runtime.py；fleet_state/transition/reward/search.py               | A/B同iteration；受控车必须从external observation剔除。                         |
| Control              | ego_simulation/two_stage_controller.py；ego_motion_controller/                   | 合法trajectory不等于controller可实现；A2是典型。                               |
| Vehicle              | ego_simulation/ego_update_model/kinematic_bicycle_model.py                       | rear axle、geometric center、footprint不可混用。                               |
| Safety               | collision_lookup.py + exact footprint/swept geometry + Paper1 sidecars           | 离散lookup可false positive；sidecar不等于hard rule。                           |
| Visualization        | PlanVisualizer2D + SimulationHistory/PlotData + MultiEgoRuntime live B           | dual history主要是A；B truth在runtime。                                        |
| Neural evidence      | /root/autodl-tmp/.../paper1\_\*                                                  | 当前网络/collector/evaluator位于evidence workspace，未集成production planner。 |

| **核心模块**                            | **作用**                                                |
|-----------------------------------------|---------------------------------------------------------|
| mcts/state.py                           | MCTSState。                                             |
| mcts/action_space.py                    | BRAKE/DECEL/KEEP/ACCEL。                                |
| mcts/state_builder.py                   | MineSim state→MCTSState。                               |
| mcts/transition_model.py                | 树内轻量近似动力学。                                    |
| mcts/geometry_transition_model.py       | 几何/footprint/外部预测；历史/current label兼容性关键。 |
| mcts/search.py                          | selection/expand/rollout/backprop。                     |
| mcts/reward_model.py                    | 目标/安全/进度奖励。                                    |
| mcts/trajectory_adapter.py              | root action→MineSim可执行轨迹。                         |
| mcts/diagnostics.py + expert_data.py    | Q/visits/immediate/clearance与strict expert。           |
| mcts/multi_ego_runtime.py               | A/B live controlled state。                             |
| fleet_state/transition/reward/search.py | 双车联合状态、16 joint actions、联合搜索与奖励。        |
| paper1_v2r_distance_field_v1.py         | 连续V2R旁路。                                           |
| paper1_dynamic_v2v_dsafe_v1.py          | dynamic V2V d_safe诊断。                                |
| paper1_shadow_safe_node_v1.py           | child expansion shadow risk，不删节点。                 |
| paper1_root_diagnostic_collector_v1.py  | root+16 action Q/visits/risk/provenance。               |

# 4. 阶段一：MineSim 原项目复现与 IDM Baseline

目标：在 AutoDL 稳定复现原 MineSim，建立后续 MCTS、地图、multi-ego 与 neural 研究的永久回归锚点。Dapai/Jiangtong 原地图、IDM/replay 与 closed-loop baseline 不能因后续推进而删除。

- 核对真实 YAML/Hydra/Scenario/Planner/Controller API，不按模型记忆猜字段。

- 确认 Planner 输出 future trajectory；Controller 计算控制；Kinematic Bicycle Model 传播下一帧。

- 建立 baseline commit/tag 与 IDM/replay 视频/结果，作为行为回归锚点。

- PASS：初始化成功、逐帧闭环、无异常、结果/日志可追溯、Git状态符合预期。

| **对象**            | **Commit/Tag**                                                        | **状态**            |
|---------------------|-----------------------------------------------------------------------|---------------------|
| IDM/replay baseline | 2521aa41a69a6e734c04c15a715e9530c8095ac3 / idm-replay-autodl-baseline | HISTORICAL / FROZEN |
| 原项目复现资料      | 原项目复现.zip：论文、函数说明、Dapai/Jiangtong视频、项目地址         | 会话材料；完整保留  |

恢复原则：正式仓库只认 /root/MineSim-Dynamic；/root/autodl-tmp/MineSim-Dynamic 是约203.75MB的独立脏历史 workspace，HOLD，不得当作正式 repo 的简单副本。

# 5. 阶段二：蒙特卡洛 / Pure MCTS 接入

目标：不重写 MineSim 执行层，把 Pure MCTS 作为 online local planner 接入真实 closed-loop，并形成可追溯专家搜索记录。

| **合同项**         | **冻结/历史定义**                                                       |
|--------------------|-------------------------------------------------------------------------|
| 动作空间           | BRAKE -3.0；DECEL -1.5；KEEP 0；ACCEL +1.0 m/s²。                       |
| 历史正式 Pure MCTS | budget=300；depth=8；tree_dt=0.5s；c_uct=1.4；gamma=0.99。              |
| 障碍预测           | CV/CTRV；footprint buffer约0.5m；连续净距阈值约3m。                     |
| 专家数据           | Dapai199 + Jiangtong249 = 448 strict historical expert samples。        |
| 重要边界           | 历史448与current-semantic producer/rear-axle/center语义不同，不能混同。 |

已完成五 Planner 与 budget 50/100/200/300 比较。结论不是“所有 planner 同样适配”，而是明确了搜索逻辑、trajectory adapter、controller、vehicle model 的故障域。

典型故障：Frenet/adapter 在 step150 出现 best_traj 长79却访问79的 IndexError；通过安全重采样后跑通。永久规则：adapter越界不能直接归因于MCTS搜索失败。

| **历史锚点**       | **Commit/Tag**                                                             | **状态**                 |
|--------------------|----------------------------------------------------------------------------|--------------------------|
| Pure MCTS + expert | 94693dc799fe5f325a75e8fc6d7d5e88764b4799 / mcts-expert-dataset-v1-20260802 | FROZEN                   |
| Monte Carlo材料    | 蒙特卡洛实现.7z；蒙特卡洛效果对比.7z                                       | 会话原始压缩包，完整保留 |

# 6. 阶段三：单车跑通

目标：证明 real-GeoJSON / real MineSim closed-loop 从初始化到终点完整执行，不把局部 planner smoke 误当 full-route success。

| **实验**                          | **结果**                                                                                      | **冻结锚点**                                                                               |
|-----------------------------------|-----------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------|
| J117 Phase4C                      | 423 steps / 42.3s；route≈398.998m；min clearance≈1.599m；goal reached；全程drivable；无异常。 | ec1c958735b0ee76201284faacb46fccc75c7f6c / j117-phase4c-single-ego-closed-loop-20260810    |
| FullMine Representative Pure MCTS | 跨代表区域3/3 PASS。                                                                          | Summary 742d0716…；Freeze 322e90d6995c410597d01925de6d77f1fd91ddb8c4c73a25c3e87446d37ac1fa |

# 7. 阶段四：双车冲突场景、MultiEgoRuntime 与 causal benchmark

目标：A/B 都成为受控对象，在同一 simulation iteration 内联合传播/决策；并先证明“没有联合规划会发生真实物理冲突”，形成 causal benchmark。

| **机制**                                   | **真实职责/规则**                                                                      |
|--------------------------------------------|----------------------------------------------------------------------------------------|
| ControlledVehicleRuntime / MultiEgoRuntime | 按token管理A/B current/next state；接收两条trajectory；B权威live state在runtime。      |
| SimulationSetup.set_multi_ego_runtime()    | 把multi-ego runtime挂到production setup。                                              |
| EnvironmentSimulation.propagate()          | dual trajectories必须恰好含A/B，再同步更新MultiEgoRuntime。                            |
| Observation filter/partition               | 从tracked observation剔除受控A/B，防止controlled+external duplicate actor/假碰撞。     |
| History边界                                | SimulationHistory在dual mode主要记录A；B不应从history伪造。                            |
| 碰撞真值                                   | NO-MCTS causal gate使用0.1s exact footprint/swept overlap + post-conflict completion。 |

Jiangtong Traj26 虽空间路径相交，但自然 ETA 差约9.496s，交互弱，已作为负筛选冻结；禁止通过改StartTime/速度/route/reward/budget/seed人为包装为天然冲突。

| **对象**             | **结果/冻结**                                                                                   |
|----------------------|-------------------------------------------------------------------------------------------------|
| Jiangtong V22        | 94794c963f9c3eaf1873b275df6d319ca2636817 / jiangtong-v22-benchmark-screening-20260809；负筛选。 |
| J117 Phase5          | da4105b836dbbd3e702ee25fbb364109bc4e2596 / j117-phase5-dual-ego-pure-mcts-20260810。            |
| J117 NO-MCTS aligned | crossing gap≈0.00070s；min clearance=0；真实几何重叠。                                          |
| J117 Pure MCTS seed0 | crossing gap≈1.561s；1ms swept min clearance≈0.594m；无碰撞。                                   |

# 8. 阶段五：FullMine 新地图接入与 Vector V4 冻结

目标：从真实 FullMine GeoJSON 构建可被 MineSim Map API、Planner、Controller 与 multi-ego runtime 使用的 Research/DEV 地图；严格区分“科研可复现 baseline”和“production-authoritative drivability”。

| **Semantic审计对象** | **数量** |
|----------------------|----------|
| nodes                | 403,759  |
| effective roads      | 100      |
| intersections        | 35       |
| polygons             | 184      |
| reference paths      | 553      |
| borderlines          | 402      |
| dubins poses         | 565      |
| loading              | 36       |
| unloading            | 7        |
| auxiliary            | 6        |

- 大 semantic 初始化慢的根因是约40万节点重复线性scan；token2ind O(1)修复，commit 32fb42920d8cc404b37cd25dc47cbc6fbde4d9f4。

- FullMine V1：d81c57154e4e5d0b4df1251cf565d9aacffaa026 / fullmine-dev-runtime-pass-20260811。

- Current V4：112d2bd0f3412fc83b13d5587d2b41402d2d0f5e / fullmine-vector-v4-runtime-freeze-20260814。

- “V4”主要指bitmap/runtime/planner冻结；semantic主体仍是Vector V2。

- targeted 7/7 + Jiangtong old-map regression PASS；GlobalRoutePathPlanner BFS target_depth=5通过depth-safe scenarios绕开，未改全局BFS语义。

| **对象**           | **SHA256/状态**                                                           |
|--------------------|---------------------------------------------------------------------------|
| FullMine semantic  | b85a3d8b28f2252ecb5bda179d514573f6333079def838cd048566f556d95cd0 / FROZEN |
| FullMine V4 bitmap | 51abcd5a86e5c510204a5dacc873691506d721f98982ab7f98585d4e0f7efdd0 / FROZEN |
| CollisionLookup    | 10c1d1339e742ca893fedb4aa51402addfba82e16e08f68339ea35d35ba3043b / FROZEN |
| IDM planner final  | 541ec74985d06322656e66c48abb382030d679171341408575d936e0a069e75e          |

| **问题**            | **真实结论**                                                                          | **永久规则**                                |
|---------------------|---------------------------------------------------------------------------------------|---------------------------------------------|
| P0 baseline         | immutable；candidate必须新目录。                                                      | 禁止原地覆盖。                              |
| Candidate v1/v2     | additive patch；v1+112px，v2累计+118px。                                              | 每版绑定SHA；不能为“看起来通”随手补像素。   |
| A1 endpoint         | virtual lead geometry约4.5m；仅virtual endpoint length_rear=0。                       | 不改地图/goal掩盖planner bug。              |
| A2 mid-stop         | 高曲率steering-rate infeasibility；speed cap 0.208rad/s + backward braking envelope。 | 先看controller truth，不盲补bitmap。        |
| Production validity | 缺官方mask/internal exclusions/authoring rule。                                       | production-authoritative drivability HOLD。 |
| Terrain/Z/slope     | source_z_datum_verified=false；slope waypoint\[4\]语义未验证。                        | terrain/Z/slope risk HOLD。                 |

# 9. 阶段六：Fleet-MCTS 双车联合规划、多种子与跨场景结论

联合状态：controlled A + controlled B + external actors → FleetState → 4×4=16 joint longitudinal actions → FleetTransitionModel/FleetRewardModel → 两车closed-loop执行。

| **参数/规则**   | **冻结定义**                                                                                       |
|-----------------|----------------------------------------------------------------------------------------------------|
| 正式 Fleet 参数 | budget=64；depth=8；MCTS dt=0.5s；16 joint actions。                                               |
| 几何            | RouteGeometryCache：rear-axle route_s→geometric-center footprint。                                 |
| 奖励            | per-vehicle progress/safety/efficiency + internal clearance soft penalty + hard collision/safety。 |
| NO-MCTS对照     | 固定速度、无artificial delay；exact footprint/swept overlap。                                      |
| 多种子统计      | Polygon21 seeds0–4：5/5 PASS；first-to-cross A:3，B:2；无参数重调。                                |

| **场景**  | **NO-MCTS causal**                                                                          | **Fleet-MCTS**                                                                         | **科学含义**                      |
|-----------|---------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------|-----------------------------------|
| Polygon21 | 真实物理重叠；result SHA 060880c8edc851e05606871cb647058d091ce8737f952b9864cc94e9d6fcfd13。 | 5/5 PASS；freeze v2 b89d290c9cb06d1efb99688ee27b23898ab81d11e36023832477dc2fc834364b。 | 干净benchmark。                   |
| C04       | 真实overlap；0c806c23…                                                                      | authoritative Fleet 47e3ff50… success。                                                | 成功transfer。                    |
| C11       | horizon fix后causal PASS；c5bd459c…                                                         | 89s/890，无碰撞但completed_post_conflict=False；47a6d570…                              | 真实安全死锁/进度失败，必须保留。 |
| C06       | 真实overlap；db78f35b…                                                                      | 0cbec940… success。                                                                    | 成功transfer。                    |

跨场景正式口径：balanced seed0 full benchmark success=2/3（C04、C06），collision avoidance=3/3。不能把C04 5 seeds与C11/C06 seed0简单池化；禁止为“全PASS”调参抹掉C11。

# 10. 阶段七：原生 MineSim 可视化与汇报材料

固定原则：汇报材料必须来自 frozen semantic/bitmap、真实 scenario/runtime state 和 MineSim 原生可视化链。禁止生成式道路、截图描线、像素反推、CSV坐标重建或手工改科学轨迹。

## 10.1 双车状态真值与受控 B 可视化

EnvironmentSimulation.history 在 dual mode 主要保留 A 的 ego/history trajectory；B 的权威状态由 MultiEgoRuntime 管理。Native V2 在 propagate 前读取 runtime.state_for("A") / state_for("B")；A 与原生 history 同帧 pose parity≤1e-8，B 使用同 iteration live overlay。

永久禁忌：不能用A history假装完整A+B；不能用route_s/CSV/pixel猜B姿态；不能让受控B同时作为external actor。

## 10.2 Native Video V1/V2 与 Map Showcase

| **版本/对象**        | **真实问题/结果**                                                                                                | **状态**                                                                            |
|----------------------|------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|
| Native Video V1      | NO-MCTS raw dimensions=(1545,3666)，布局异常；科学链可跑但不满足正式汇报。                                       | SUPERSEDED                                                                          |
| Native Video V2      | NO-MCTS/Fleet raw=(1545,1073)，10fps；NO-MCTS145帧、Fleet151、side-by-side145；collision frames96–118，peak107。 | FINAL / PASS；SHA f695ba22ecd61c4a643e8ffecac483bc218de9153f95f88b4e0e3006bca03d58  |
| “打包错误”口径       | 直接证据仅支持V1尺寸/layout失败与V2形成绑定SHA release；更具体ZIP exception无直接证据。                          | 未验证/HOLD                                                                         |
| Map Showcase V1      | 误把semantic顶层当GeoJSON FeatureCollection；真实为custom dict；schema gate主动停止。                            | FAILED DESIGN                                                                       |
| Map Showcase V2      | 真实custom semantic；553 reference_path、402 borderline；Polygon21真几何；1080p/15fps/120帧。                    | PASS / stable；SHA 9f78f357eecfc25ea543d163e8d472dc06abeb1fff3215ed30577267750d1e14 |
| Map Showcase V3      | ffmpeg SIGKILL:9；仅证实进程被杀；保留120帧。                                                                    | INCOMPLETE/HOLD，不能写成确定OOM                                                    |
| Renderer conflict XY | manifest仅给route_s；用semantic waypoints + exact route station求点。                                            | FIXED；禁止hardcode                                                                 |
| Video mid-pan blank  | camera logic问题。                                                                                               | V0.2 target-anchored camera修复；仍需human visual gate                              |

# 11. 阶段八：云端文件安全整理、目录体系与恢复

整理原则：可逆移动/隔离，不等于删除。目录变干净不等于释放磁盘；Archive/Quarantine仍占空间。

| **目录**                                     | **用途/规则**                                                                                                      |
|----------------------------------------------|--------------------------------------------------------------------------------------------------------------------|
| /root/autodl-tmp/00_MineSim_ACTIVE           | current_paths.json、env、快捷软链接、organization_tools。                                                          |
| /root/autodl-tmp/10_MineSim_REPORTS          | 汇报/发布备份；不作为科学运行输入。                                                                                |
| /root/autodl-tmp/90_MineSim_ARCHIVE          | 可恢复历史归档：legacy planner、single MCTS、J117、FullMine dev、superseded media、bundles、assistant deliveries。 |
| /root/autodl-tmp/98_MineSim_QUARANTINE       | 隔离但未授权删除；8/16 closeout约315.76MB。                                                                        |
| /root/autodl-tmp/99_MineSim_CLEANUP_MANIFEST | Phase1–2K audit/move/fingerprint/health/restore provenance。                                                       |
| /root/autodl-tmp/MineSim-Dynamic             | 约203.75MB独立脏历史workspace；HOLD。                                                                              |

| **整理事实**                         | **已验证结果**                                                                                                           |
|--------------------------------------|--------------------------------------------------------------------------------------------------------------------------|
| 2026-08-16 Phase2A–2K                | 顶层约530→121；423 move/isolate；科研文件删除0；HEAD/SHA/symlink/compile/restore health PASS。                           |
| 2026-08-21 assistant package cleanup | move manifest=99；keep manifest=3；problem_count=0；restore script存在、SHA通过；之后又生成新资产，3个顶层只是瞬时状态。 |
| 旧C11/C06 upload ZIP                 | 顶层缺失后在90_MineSim_ARCHIVE/.../30_review_hold找到，证明path missing≠deleted。                                        |
| codex-env.sh                         | 登录提示No such file；只能标记路径缺失/处置未验证，不能推断被删。                                                        |
| 真正删除                             | 必须另开deletion phase：只读inventory→checksum/equivalence→明确授权→删除。                                               |

## 11.1 绝对路径与 runtime 软链接

- Frozen runner存在绝对路径依赖时，优先恢复历史路径/软链接，不直接改frozen runner。

- runtime semantic必须指向new_map_fullmine_vector_v2_dev对应semantic；runtime bitmap必须指向fullmine_vector_v4_d_current_planner_patch_candidate对应bitmap。

- 恢复前确认原路径无新同名对象；只用manifest对应RESTORE脚本逆序恢复。

- 恢复后复核HEAD/status、关键SHA、symlink target与py_compile。

- 已知 \`?? ^C\` 为历史未跟踪异常名；禁止为了美观git clean。

# 12. 阶段九：后续神经网络接入与当前 C03 / Value V2 进展

## 12.1 Safety/data/current-semantic 前置链

| **对象**                 | **状态/结论**                                                       | **关键SHA/边界**                                                 |
|--------------------------|---------------------------------------------------------------------|------------------------------------------------------------------|
| Continuous V2R V3        | FROZEN PASS；C04 126-step full parity；不改authoritative Fleet/V0。 | 0231cda732ac4859985d4be451d01ade6f6e121892721ce9e6317dce430d64a4 |
| Runtime heading/approach | FROZEN PASS；C04/C11/C06 approach=70/80/100m。                      | a27653c2…                                                        |
| Omega_int + pair binding | FROZEN PASS；AND_BOTH；Omega_app。                                  | Omega_int a6b1de3c…；pair 2e516d95…                              |
| Dynamic V2V d_safe       | 126 records；behavior/reward/search/pruning unchanged。             | 3bcbbcb3623b07c3e8a162e24c5b63303b866cf9d149a68d083c30b5f7856193 |
| Shadow safe-node         | 8064 child；20 roots出现16/16 reject；22 selected actions也reject。 | HARD_PRUNING_APPROVED=False                                      |
| Dataset Contract V1      | root-search raw；root×joint-action derived；Q primary。             | 46f2e099fbe9090a02b1f9fe8a983e4f8322a2ffeba89a4700de8e278991dcda |

## 12.2 Value Network V1：流程 PASS、科学 FAIL

- C04 collector：126 roots/2016 action rows；单episode24→64→64→1 pipeline smoke，train Pearson 0.880，仅证明pipeline。

- C11 890 roots/14240 rows（deadlock）；C06 146 roots/2336 rows（success）；合计1162 roots/18592 rows。

- Formal split=leave-one-scene-episode-out；3 folds；normalization只用train fold；scene-balanced SmoothL1；600 epochs/fold。

- 三个held-out Top1均低于随机1/16=6.25%；normalized regret均差于immediate_reward。

- Decision=DO_NOT_INTEGRATE_VALUE_NETWORK_INTO_MCTS；不能用“多训几轮”绕过科学FAIL。

## 12.3 Value V2 final-dev 与 C13 one-time failure

| **对象**          | **真实状态**                                                                                                                      |
|-------------------|-----------------------------------------------------------------------------------------------------------------------------------|
| 模型              | ROOT_CENTERED_Q；12→64→64→16；训练场景C04/C11/C06。                                                                               |
| Checkpoint SHA    | ce32cb7943a05d62ea16aee95a86f26bab7521af1d345e39f5c8a410a02ffb13                                                                  |
| Normalization SHA | 36ee17a182c519c41602c5d414a4e009a569660254bb4bd31fc75a3b705bc6f9                                                                  |
| Model freeze SHA  | a2be866144446a442cf7a8cb23a7f7ce9041a2d7b86fcded2ff8709f7a24d05b                                                                  |
| C13数据           | 115 roots/1840 rows；full collection freeze c41714c3…                                                                             |
| C13 evaluation    | forward call count=1；prediction shape=\[115,16\]；metric harness错绑零参数main()，TypeError；prediction未持久化，metrics未评估。 |
| C13规则           | scientific gate=HOLD_NOT_EVALUATED；one-time protocol已消耗，retry_authorized=False，永久禁止重跑。                               |

## 12.4 Replacement 预注册与 C03 qualification

为避免看值后挑场景，blind preregistration 排除 C04/C06/C09/C11/C13；排序固定为 angle novelty DESC \> distance DESC \> endpoint margin DESC \> pair count DESC \> source index ASC；eligible C10→C14→C03，不得reselection/rescoring。

| **候选** | **结果**                                                                                   |
|----------|--------------------------------------------------------------------------------------------|
| C10      | B fallback physical_drivable=False；16 bad/39 pixels；FROZEN STATIC REJECT。               |
| C14      | B expected route truncated；route_exact_match=False；NONTECHNICAL_ROUTE_CONTRACT_FAILURE。 |
| C03      | physical PASS；A/B static direct各451 samples、0 bad；进入causal qualification并最终PASS。 |

| **C03关键对象**       | **SHA / 结果**                                                   |
|-----------------------|------------------------------------------------------------------|
| Entry lock            | cc154fa9a257cab38f6519013a94298241c8388b0f4af7ac3e6736307892dc2f |
| Physical lock         | c308ffa6c55d917ee73237aa645a16aa46461313006220e0b7cc911f76261ce2 |
| Scenario              | df4698f2e0de3ed99649349583d6f1c4c95020b4e8fdb91f8bccbaca17592adf |
| Manifest              | 061887ed6b632f4648978b62363dab78125de3665ed3368997cd4bb85c056d33 |
| Static lock           | b7490746098d1a61248e225cf66db4ed532db1f8f02268ab6d19bfdd10433060 |
| NO-MCTS causal freeze | 6cec631084980a8273d1951f83829c55aed84766576f11b419b30eedb1566ec0 |
| Zone contract         | 781da697cbac47b7d134eb5cb528faf0989a8a9e04a3ac5992491ed40b747aed |

## 12.5 2026-08-23～08-24 云端实际完成工作（最新）

归属边界：以下为 AI/ChatGPT/Codex 设计的脚本与用户 AutoDL 终端实际执行形成的证据；逐文件是否由 Codex 生成未全部具备作者签名，因此本文只写“云端实际完成”，不虚构作者。

| **工作项**                 | **真实过程/结果**                                                                                        | **冻结/当前意义**                                                                       |
|----------------------------|----------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|
| C03 NO-MCTS causal         | 初次attempt出现stale 50m identity check，0 iterations；修正后technical retry执行成功。                   | causal freeze 6cec6310…；额外C03 causal执行禁止。                                       |
| Collector binding/zone     | C03 route/conflict/Omega_app/Omega_int/AND semantics静态锁定。                                           | binding c1505688…；zone 781da697…                                                       |
| Smoke attempt1             | ModuleNotFoundError: paper1_root_diagnostic_collector_v1；runtime files=0。                              | 纯import technical failure。                                                            |
| Smoke retry1               | 残留 C13 source-index guard；runtime files=0。                                                           | 纯pre-runtime technical failure。                                                       |
| Amendment                  | 旧FROZEN_PRE_C03_COLLECTION_RUNTIME status guard残留；runtime files=0。                                  | 关闭旧protocol并做full static admission audit。                                         |
| Fresh recovery smoke       | 真正执行1 step；1 root、16 actions、64 expansions；benchmark因0.1s不完整而RC=1，但technical smoke PASS。 | technical smoke freeze 170dcb466191ccbc537bc58adb44fe032500b52c50aa2736dd822fb50b3201c3 |
| Value nonexecution audit   | 执行源码链无torch/load/forward；checkpoint仅SHA/provenance。                                             | ea2da1717c72b658b95edc42047f0cce7a574170b565d1bb485186c299b59385                        |
| C03 Full Collection        | RC=0；135 roots；2160 records；8640 expansions；13.5s；post-conflict complete；无碰撞。                  | freeze 15c098f72ae0187dd0bb97bd9878aa6860d47df48391e09bd9ad56eb9ac31fa8                 |
| Metric closure             | average_ranks→pearson→spearman→ranking_metrics exact source extraction；synthetic PASS。                 | closure 962c6cd3…；synthetic c08e819c…；contract 4a3d70ac…                              |
| Feature/model inventory    | 12 frozen features、normalization顺序、ActionConditionedValueV2 12→64→64→16。                            | inventory f1c2830809b34403f4dd3f554c605cf6e5a46f9111b59e27d3ff704327afc594              |
| Inference source inventory | 确认feature嵌套在vehicles+pair_features；当前候选中未找到真正C13 forward harness。                       | inventory 6c561d5b28995f0360e0cac98b7682ea993e303a7fd21e5b456ec17ee75fcda8              |

## 12.6 C03 Full Collection 正式结果

| **指标**                    | **结果**                            |
|-----------------------------|-------------------------------------|
| runner_process_rc           | 0                                   |
| root_record_count           | 135                                 |
| derived_action_record_count | 2160                                |
| shadow expansion records    | 8640                                |
| duration / iterations       | 13.5s / 135                         |
| A/B conflict cross time     | 9.3010869565s / 11.7212022543s      |
| crossing gap                | 2.4201152977s；A first              |
| min footprint clearance     | 2.382908179m                        |
| min center distance         | 8.444768132m                        |
| collision/overlap           | False / False                       |
| completed_post_conflict     | True                                |
| benchmark_success           | True                                |
| timeline sync / error       | True / None                         |
| Value forward               | False；MCTS value integration=False |

## 12.7 当前 Value V2 exact evaluator 状态

| **索引** | **冻结特征名**            |
|----------|---------------------------|
| 0        | A_speed_mps               |
| 1        | B_speed_mps               |
| 2        | A_accel_mps2              |
| 3        | B_accel_mps2              |
| 4        | A_remaining_to_conflict_m |
| 5        | B_remaining_to_conflict_m |
| 6        | delta_v_abs_mps           |
| 7        | delta_heading_abs_rad     |
| 8        | delta_heading_over_pi     |
| 9        | I_Omega_app_AND           |
| 10       | I_Omega_int_AND           |
| 11       | alpha3                    |

- normalization feature_names与上述顺序完全一致；indices=\[2,3,4,5,6,7,10,11,12,13,14,15\]。

- root_state结构：车辆速度/加速度/remaining在root_state.vehicles；delta/heading/alpha3/AND indicators在root_state.pair_features。

- metric closure exact：average_ranks、pearson、spearman、ranking_metrics(q,pred,immediate)，synthetic PASS。

- model class：ActionConditionedValueV2(nn.Module)，Linear(12,64)→ReLU→Linear(64,64)→ReLU→Linear(64,16)。

- 当前未加载checkpoint、未执行真实C03 forward、未计算prediction或metrics，VALUE_V2_EVALUATION_AUTHORIZED=False。

当前下一步（低资源）：完成 exact nested JSON-path feature mapping 与全 /root/autodl-tmp 历史 C13 forward harness 搜索，锁定 proven checkpoint load→ActionConditionedValueV2(12)→load_state_dict→normalization→eval/no_grad→\[N,16\] 链。若仍找不到历史 harness，基于 exact producer+feature mapping 构造 evaluator，但必须先做 synthetic checkpoint-compatible forward。

# 13. 重要失败、排查、修复与永久禁忌

| **故障/现象**                     | **原因**                                                  | **最终处理/证据**                                                           | **以后不能重复**                           |
|-----------------------------------|-----------------------------------------------------------|-----------------------------------------------------------------------------|--------------------------------------------|
| Planner/Frenet step150 IndexError | best_traj长79却访问79；adapter越界。                      | 安全重采样后跑通；先分search/adapter/controller。                           | 禁止把adapter越界误判为MCTS失败。          |
| Multi-ego duplicate actor         | A/B同时controlled+external。                              | controlled token从tracked observation过滤。                                 | 受控车辆绝不能重复为external obstacle。    |
| Environment history缺B            | History主要保存A。                                        | B使用MultiEgoRuntime同iteration truth。                                     | 禁止用A history假装A+B。                   |
| Native B可视化                    | B不能直接从history回放。                                  | A history + B live overlay；pose parity≤1e-8。                              | 禁止route_s/CSV/pixel猜B姿态。             |
| Jiangtong conflict screening      | 空间相交但ETA差9.496s。                                   | 负筛选freeze。                                                              | 空间交叉≠时间冲突。                        |
| CollisionLookup false positive    | 离散lookup与exact footprint定义不同。                     | causal gate用exact footprint/swept overlap。                                | 中心距/查表/示意图不能替代物理真值。       |
| FullMine init慢                   | 约400k node重复线性scan。                                 | token2ind O(1)。                                                            | 先profile复杂度，不归咎GPU。               |
| A1 endpoint/A2 mid-stop           | virtual endpoint geometry / steering-rate infeasibility。 | virtual endpoint length_rear=0；steering-aware speed cap+backward braking。 | 不盲补bitmap或改goal。                     |
| Map/runtime路径失效               | 整理移动导致绝对路径/软链接失效。                         | current_paths+restore/symlink gate。                                        | frozen runner优先恢复路径，不直接改代码。  |
| Low-memory RC137                  | 2GiB cgroup不足。                                         | 低资源preflight后开80GiB/15CPU。                                            | 不低配硬跑大图/长仿真。                    |
| Map Showcase V1/V3                | V1 schema误判；V3 SIGKILL:9。                             | 读真实schema；V3保留120帧/HOLD。                                            | 不能无证据把SIGKILL写成OOM。               |
| Native Video V1                   | 1545×3666布局异常。                                       | V2=1545×1073+ffprobe+human gate。                                           | 科学链可跑≠汇报质量PASS。                  |
| Renderer conflict XY/OUT          | manifest给route_s；wrapper漏OUT。                         | route station求点；required env gate。                                      | 禁止hardcode XY；wrapper先验env。          |
| Video mid-pan blank               | camera逻辑。                                              | V0.2 target-anchored camera。                                               | 自动编码PASS不能替代human gate。           |
| Long heredoc/粘贴污染             | 聊天UI与终端输出混粘。                                    | 短块、文件优先、ls/file/sed。                                               | 禁止因粘贴异常清目录。                     |
| C04 loader float(list)            | 一元素list/\[N\]\[1\]未规范。                             | shape normalization。                                                       | 不从旧文档猜exact line。                   |
| C04 NO-MCTS MAX_STEPS NameError   | harness常量遗漏。                                         | 最小runner fix。                                                            | harness FAIL≠science FAIL。                |
| C11 NO-MCTS 200-step              | 时间窗不足导致post-conflict false。                       | 仅延长至21.2s/212。                                                         | 不改冲突物理/算法。                        |
| C11 Fleet deadlock                | 89s无碰撞但不完成。                                       | 冻结负结果。                                                                | 禁止为全PASS调参抹掉。                     |
| Historical448 vs current labels   | rear-axle/center/producer语义变化。                       | legacy隔离+current recollection。                                           | schema相同≠label同质。                     |
| Collector JSON +inf/false PASS    | allow_nan=False序列化失败；内存先append。                 | 删未合同字段；写盘成功后append。                                            | JSONL空不能由内存summary伪装PASS。         |
| Collector timeline                | root absolute vs V0 relative。                            | 对齐origin/cadence；离线salvage。                                           | 无需重跑已完成仿真。                       |
| PyTorch missing                   | 镜像≠conda env。                                          | 安装CPU torch 2.8.0+cpu。                                                   | 不要假设基础镜像包等于env包。              |
| C13 Value eval metric binding     | AST误绑main()而非ranking_metrics。                        | 冻结failure；static fix但禁止retry。                                        | one-time独立验证失败后不得重跑/调参。      |
| C09/C10/C14 rejects               | physical/static/route contract失败。                      | 按预注册顺序冻结淘汰。                                                      | 不补图、不改planner、不重选。              |
| AST env audit                     | 把os.environ Store误报Load。                              | 区分ctx Load/Store。                                                        | 环境依赖审计必须看AST上下文。              |
| C03 horizon zero slack            | 75+15m /4.5=20s=200×0.1。                                 | 预执行改212，无outcome-informed retuning。                                  | 运行前检查完成门时间余量。                 |
| C03 stale 50m check               | 顶层75m但深层identity仍50m。                              | 冻结0-step technical failure，只改两处。                                    | 技术失败不等于science FAIL。               |
| C03 smoke import                  | helper模块不在script目录。                                | 复制byte-identical modules+import gate。                                    | 执行前必须验证import origin。              |
| C03 stale C13 guard               | SOURCE_INDEX !=13/C13-only。                              | 完整静态remnant audit。                                                     | 派生runner不能只替换路径。                 |
| C03 preauth status guard          | 旧status与新amendment同时存在。                           | 完整runtime admission audit。                                               | 不能跑一次暴露一个guard；先全静态清点。    |
| One-step RC=1误判                 | 短smoke不可能完成post-conflict。                          | 技术gate用root/actions/health，不用benchmark success。                      | RC单独不能判scientific fail。              |
| Value boundary字段缺失            | root schema无显式value_model字段。                        | executed-source audit+preauth boundary。                                    | 不能因字段缺失直接宣告forward发生/未发生。 |
| Metric closure依赖遗漏            | ranking_metrics依赖spearman→pearson/average_ranks。       | 递归exact closure+synthetic。                                               | 不能只把依赖塞白名单。                     |
| codex-env.sh missing              | 登录路径缺失，来源未知。                                  | 标路径缺失/HOLD。                                                           | 不能推断文件被删或Codex工作丢失。          |

# 14. 当前有效 / SUPERSEDED / ARCHIVE / HOLD 矩阵

| **对象**                                   | **状态**                               | **处理规则**                                    |
|--------------------------------------------|----------------------------------------|-------------------------------------------------|
| MineSim baseline 2521aa4                   | HISTORICAL / FROZEN                    | 保留回归；不是current HEAD。                    |
| Pure MCTS 94693dc + 448                    | HISTORICAL / FROZEN                    | 专家历史证据；current-semantic隔离。            |
| J117 Phase4C/5                             | FROZEN                                 | 不重跑；multi-ego regression anchor。           |
| FullMine Vector V4 112d2bd                 | CURRENT FROZEN                         | 新研究在独立evidence workspace。                |
| Representative Pure MCTS 3/3               | FROZEN                                 | 无需重做。                                      |
| Polygon21 Fleet v2                         | FROZEN                                 | 正式benchmark；旧harness failures仅provenance。 |
| Cross-scene C04/C11/C06                    | CLOSED WITH NEGATIVE                   | C11 negative必须保留。                          |
| Native Video V1                            | SUPERSEDED                             | 保留provenance，不用于正式汇报。                |
| Native Video V2                            | CURRENT FINAL                          | 正式视频evidence。                              |
| Map Showcase V2                            | PASS / HISTORICAL STABLE               | V3不覆盖V2。                                    |
| Map Showcase V3                            | INCOMPLETE / HOLD                      | 120帧；encode/release未完成。                   |
| Paper1 V2R/heading/Omega/dynamic           | FROZEN / DIAGNOSTIC                    | 不改变planner behavior；不可外推hard safety。   |
| Shadow safe-node                           | OBSERVATIONAL PASS                     | hard pruning not approved。                     |
| Value V1                                   | TRAINING PASS / SCIENCE FAIL           | DO_NOT_INTEGRATE。                              |
| Value V2 final-dev model                   | FROZEN DEVELOPMENT MODEL               | 尚无有效independent science PASS。              |
| C13 one-time eval                          | FROZEN TECHNICAL FAILURE AFTER FORWARD | metrics未评估；retry forbidden。                |
| C03 causal/technical smoke/full collection | CURRENT FROZEN PASS                    | 禁止重跑；数据进入Value V2静态评估准备。        |
| C03 Value V2 real evaluation               | HOLD / NOT AUTHORIZED                  | checkpoint未加载；prediction/metrics未计算。    |
| Production drivability                     | HOLD / NOT PROVEN                      | 缺官方规则。                                    |
| Terrain/Z/slope                            | HOLD                                   | datum/slope语义未验证。                         |
| V2H probabilistic safety                   | NOT IMPLEMENTED                        | 阻塞full safe-node。                            |
| Policy Network / PUCT                      | NOT STARTED                            | 先完成Value independent validation。            |
| Value-guided MCTS                          | NOT INTEGRATED                         | MCTS_VALUE_INTEGRATION=False。                  |

# 15. 关键 Commit / Tag / SHA 速查

| **里程碑**         | **Commit**                               | **Tag/说明**                                 |
|--------------------|------------------------------------------|----------------------------------------------|
| IDM baseline       | 2521aa41a69a6e734c04c15a715e9530c8095ac3 | idm-replay-autodl-baseline                   |
| Pure MCTS + expert | 94693dc799fe5f325a75e8fc6d7d5e88764b4799 | mcts-expert-dataset-v1-20260802              |
| Jiangtong V22      | 94794c963f9c3eaf1873b275df6d319ca2636817 | jiangtong-v22-benchmark-screening-20260809   |
| J117 Phase4C       | ec1c958735b0ee76201284faacb46fccc75c7f6c | j117-phase4c-single-ego-closed-loop-20260810 |
| J117 Phase5        | da4105b836dbbd3e702ee25fbb364109bc4e2596 | j117-phase5-dual-ego-pure-mcts-20260810      |
| FullMine lookup    | 32fb42920d8cc404b37cd25dc47cbc6fbde4d9f4 | token2ind O(1)                               |
| FullMine V1        | d81c57154e4e5d0b4df1251cf565d9aacffaa026 | fullmine-dev-runtime-pass-20260811           |
| FullMine V4        | 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e | fullmine-vector-v4-runtime-freeze-20260814   |

| **对象**                         | **SHA256**                                                       |
|----------------------------------|------------------------------------------------------------------|
| FullMine semantic                | b85a3d8b28f2252ecb5bda179d514573f6333079def838cd048566f556d95cd0 |
| FullMine bitmap                  | 51abcd5a86e5c510204a5dacc873691506d721f98982ab7f98585d4e0f7efdd0 |
| CollisionLookup                  | 10c1d1339e742ca893fedb4aa51402addfba82e16e08f68339ea35d35ba3043b |
| Representative MCTS freeze       | 322e90d6995c410597d01925de6d77f1fd91ddb8c4c73a25c3e87446d37ac1fa |
| Polygon21 Fleet freeze v2        | b89d290c9cb06d1efb99688ee27b23898ab81d11e36023832477dc2fc834364b |
| Native Video V2                  | f695ba22ecd61c4a643e8ffecac483bc218de9153f95f88b4e0e3006bca03d58 |
| Map Showcase V2                  | 9f78f357eecfc25ea543d163e8d472dc06abeb1fff3215ed30577267750d1e14 |
| Cleanup closeout                 | e3d4ba27bd06c74c7ca23ed55de65208022f07d4e0cb600eb58bcbbcaaf33a4b |
| Dataset Contract V1              | 46f2e099fbe9090a02b1f9fe8a983e4f8322a2ffeba89a4700de8e278991dcda |
| Value V2 checkpoint              | ce32cb7943a05d62ea16aee95a86f26bab7521af1d345e39f5c8a410a02ffb13 |
| Value V2 normalization           | 36ee17a182c519c41602c5d414a4e009a569660254bb4bd31fc75a3b705bc6f9 |
| Value V2 model freeze            | a2be866144446a442cf7a8cb23a7f7ce9041a2d7b86fcded2ff8709f7a24d05b |
| C03 causal freeze                | 6cec631084980a8273d1951f83829c55aed84766576f11b419b30eedb1566ec0 |
| C03 zone contract                | 781da697cbac47b7d134eb5cb528faf0989a8a9e04a3ac5992491ed40b747aed |
| C03 technical smoke freeze       | 170dcb466191ccbc537bc58adb44fe032500b52c50aa2736dd822fb50b3201c3 |
| C03 Value nonexecution audit     | ea2da1717c72b658b95edc42047f0cce7a574170b565d1bb485186c299b59385 |
| C03 full collection freeze       | 15c098f72ae0187dd0bb97bd9878aa6860d47df48391e09bd9ad56eb9ac31fa8 |
| Metric closure exact             | 962c6cd333d9432f566a124d033540a52b10ebde4ed5f87ac695a8e42586e01e |
| Metric closure synthetic         | c08e819cff26a1039165e444b92a3645d359c967109f6f4ccd107c5da93f8cfa |
| Metric closure contract          | 4a3d70acecbcc21d1ffac317039b5ced61414ef00e2de46696969c71f1890a49 |
| Feature/model inventory          | f1c2830809b34403f4dd3f554c605cf6e5a46f9111b59e27d3ff704327afc594 |
| Exact inference source inventory | 6c561d5b28995f0360e0cac98b7682ea993e303a7fd21e5b456ec17ee75fcda8 |

# 16. 当前云端目录、依赖和恢复方式

| **逻辑对象**                 | **当前/登记路径**                                                        | **规则**                                                  |
|------------------------------|--------------------------------------------------------------------------|-----------------------------------------------------------|
| formal_repo                  | /root/MineSim-Dynamic                                                    | 唯一正式repo。                                            |
| data_root                    | /root/autodl-tmp                                                         | 大文件/日志/结果。                                        |
| current path registry        | /root/autodl-tmp/00_MineSim_ACTIVE/current_paths.json                    | 重连先读。                                                |
| FullMine runtime             | /root/autodl-tmp/fullmine_vector_v2_targeted_runtime                     | 地图runtime。                                             |
| polygon21 current            | /root/autodl-tmp/fullmine_v4_dual_candidate_v1                           | 正式双车benchmark。                                       |
| cross-scene current          | /root/autodl-tmp/fullmine_v4_fleet_cross_scene_v1                        | C04/C11/C06/C03当前evidence根。                           |
| representative MCTS          | /root/autodl-tmp/fullmine_v4_mcts_representative_v1                      | 单车代表性实验。                                          |
| C03 full collection          | .../fullmine_v4_fleet_cross_scene_v1/c03_value_v2_full_collection_v1     | 135-root冻结数据。                                        |
| Value V2 model               | /root/autodl-tmp/paper1_value_v2_final_dev_model_v1                      | checkpoint/normalization/model freeze。                   |
| C03 evaluator prep           | .../c03_value_v2_one_time_evaluation_v1                                  | metric/feature/inference inventories；真实forward未授权。 |
| reports                      | /root/autodl-tmp/10_MineSim_REPORTS                                      | 正式备份策略；不是运行输入。                              |
| archive/quarantine/manifests | 90_MineSim_ARCHIVE / 98_MineSim_QUARANTINE / 99_MineSim_CLEANUP_MANIFEST | 不可擅动；恢复用manifest。                                |

## 16.1 恢复流程

1.  先进入正式仓库、激活minesim、关闭GPU。

2.  只读核HEAD/status/cgroup/process/current_paths。

3.  确认目标原路径无新同名对象。

4.  按对应cleanup manifest的RESTORE脚本逆序恢复。

5.  复核关键SHA、semantic/bitmap symlink target、py_compile。

6.  不得使用git reset --hard、git clean -fd、git add .或rm -rf。

# 17. 运行环境、资源与统一命令规范

| **项目**   | **真实规则/观测**                                                            |
|------------|------------------------------------------------------------------------------|
| 正式repo   | /root/MineSim-Dynamic                                                        |
| Conda env  | minesim；/root/miniconda3/envs/minesim                                       |
| 实际Python | 3.9.25（当前激活环境）                                                       |
| PyTorch    | active env曾安装2.8.0+cpu；基础实例模板标称2.1.0/CUDA12.1，不可混同。        |
| 低资源     | 约2GiB / 0.5 CPU；CUDA disabled。                                            |
| 高资源     | RTX4090D 24GB×1、15 vCPU、80GB、30GB系统盘、50GB数据盘；约1.88–1.98元/小时。 |
| 资源策略   | 先免费Shell/Python；确需计算再开高卡；长仿真普通terminal/screen。            |

## 17.1 所有可执行代码固定前缀

cd /root/MineSim-Dynamic  
source /root/miniconda3/etc/profile.d/conda.sh 2\>/dev/null \|\| true  
conda activate minesim  
export PYTHONPATH=/root/MineSim-Dynamic  
export CUDA_VISIBLE_DEVICES=""

## 17.2 统一只读 preflight

pwd  
git rev-parse HEAD  
git status --short  
cat /sys/fs/cgroup/memory.max  
cat /sys/fs/cgroup/cpu.max  
screen -ls  
ps -eo pid,etime,%cpu,%mem,cmd \| grep -E 'MineSim\|paper1\|mcts' \| grep -v grep \|\| true  
sha256sum \<current input artifacts\>

- 交互顶层禁止裸exit；失败终止放子shell \`( ... )\` 用false，或只打印FAIL。

- 任何one-time/retry-limited实验先写START lock；执行后立即CAPTURE；失败不得自动rerun。

- 大源码/日志/JSON/CSV/图片/视频/ZIP用文件上传；聊天只传任务、短字段、error tail。

- 项目安全、可恢复、可复现、结果质量优先于目录美观和省几分钟。

# 18. 用户—ChatGPT—Codex 协作规则

| **规则**     | **固定执行方式**                                                                          |
|--------------|-------------------------------------------------------------------------------------------|
| 角色         | ChatGPT负责分析、决策、关键代码、验收设计；用户复制到AutoDL执行并返回真实输出/文件。      |
| Codex使用    | 只在复杂算法、顽固Bug、关键结论复核或适合云端自主执行的麻烦任务使用。                     |
| 默认模型     | gpt-5.6-luna medium；必要时临时Terra/Sol，完成即降回Luna。                                |
| 已知事实     | 不重复扫描、不重复解释；已frozen阶段不重审。                                              |
| 任务粒度     | 每次只推进一个最小blocker；只返回PASS/FAIL与必要字段。                                    |
| 免费优先     | file/process/hash/git/grep/py_compile/JSON audit可用Shell/Python确认的不用模型。          |
| 资源顺序     | 先低资源preflight/static/smoke；确需长仿真/大图才开高卡。                                 |
| 实验顺序     | 只读preflight→smoke→短闭环→完整实验→freeze。                                              |
| 长任务       | 普通terminal/screen；不让Codex长时间等待。                                                |
| 文件策略     | 大文件放/root/autodl-tmp；正式repo只保必要源码。                                          |
| Codex prompt | 必须写已冻结事实、唯一目标、允许修改、禁止操作、最小测试、PASS/FAIL、输出字段、完成即停。 |

# 19. 文档生成、归档、移动与删除情况

| **对象/时间**             | **可确认事实**                                       | **边界**                                        |
|---------------------------|------------------------------------------------------|-------------------------------------------------|
| 2026-07-26～08-17历史Word | AI接手文档.zip内包含11份阶段手册/风险清单/技术总览。 | 历史快照；当前结论需以新证据覆盖。              |
| 2026-08-18/21/23综合Word  | 当前会话各有原件与重复副本；均纳入本交付包。         | 8/24状态以本文为准。                            |
| 云端整理说明              | MineSim_云端项目整理最终文档包.zip含DOCX+MD。        | 会话材料，完整纳入。                            |
| 2026-08-16 cleanup        | 530→121；423 move/isolate；科研文件删除0。           | 可逆整理，不释放所有空间。                      |
| 2026-08-21 cleanup        | move99/keep3/problem0；restore存在、SHA通过。        | 之后生成新资产，顶层数量非当前实时值。          |
| 当前云端Word精确库存      | 未做2026-08-24 live inventory。                      | 未验证/HOLD。                                   |
| 手动删除某Word            | 无直接证据。                                         | 未验证/HOLD。                                   |
| codex-env.sh              | No such file or directory。                          | 仅路径缺失；处置未验证。                        |
| 本次新文档/包             | 在ChatGPT会话生成。                                  | 除非用户上传AutoDL并记录SHA，不得称云端已备份。 |

删除总结：现有证据只支持“科研文件删除0”和后续move/archive；不能把path missing、目录变干净或No such file推断为删除。若要真正清盘，必须单独授权deletion phase。

# 20. 会话材料与压缩包清单

本次打包纳入当前会话可见的全部 62 个项目文件（历史Word、原始ZIP/7z、冻结包、C03脚本、终端日志与前一版摘要）。新生成的本超详细Word与Manifest另行加入最终ZIP。

| **压缩包**                                 | **已知内容/处理**                                                                   |
|--------------------------------------------|-------------------------------------------------------------------------------------|
| AI接手文档.zip / (1)/(2)                   | 历史交接Word集合；原版包含11份2026-07-26～08-17手册。                               |
| 原项目复现.zip                             | 原论文/函数说明、Dapai/Jiangtong IDM视频、项目地址等。                              |
| 地图新建相关文件.zip                       | FullMine GIS/GeoJSON原始资料：junction/lane/road/boundary/load/unload/auxiliary等。 |
| MineSim地图更换.7z                         | 地图更换相关原始包；本环境未展开内容，完整保留。                                    |
| 蒙特卡洛实现.7z                            | MCTS/Monte Carlo实现资料；完整保留。                                                |
| 蒙特卡洛效果对比.7z                        | 效果对比资料；完整保留。                                                            |
| 接下来方向.7z                              | 后续研究方向资料；完整保留。                                                        |
| 可参考论文.7z                              | 参考论文资料；完整保留。                                                            |
| CROSS_SCENE_DYNAMIC_CONCLUSION_V1.zip      | cross-scene结论JSON/MD/source inventory/SHA。                                       |
| PAPER_METHOD_COMPATIBILITY_DECISION_V1.zip | paper method compatibility decision JSON/MD/SHA。                                   |
| PAPER1_V0_OBSERVATIONAL_FREEZE_V1.zip      | SafetyRisk V0 observational freeze及source evidence。                               |
| MineSim_云端项目整理最终文档包.zip         | 云端文件整理说明DOCX+MD。                                                           |

7z内容未在当前容器中解包审计，原因是当前环境无7z读取工具；这是“内容索引未验证”，不是文件缺失。原7z文件已原样纳入最终总包。

# 21. 快速接手区（下一位 AI 优先只读本节）

## 21.1 当前做到哪里

- C03 NO-MCTS causal、one-step technical smoke、Full Collection均已冻结PASS；禁止重做。

- C03 Full Collection：135 roots、2160 action records、8640 expansions、benchmark_success=True、无碰撞。

- Value V2 checkpoint/normalization/model freeze已锁；metric exact closure synthetic PASS。

- Feature/model static inventory与exact inference source inventory已完成。

- 真实C03 checkpoint load、model forward、prediction、metrics均未发生，evaluation未授权。

## 21.2 哪些阶段无需重做

- IDM/replay baseline

- Pure MCTS 448 historical expert

- J117 single/dual

- FullMine V4 targeted/old-map

- Representative Pure MCTS 3/3

- Polygon21 Fleet seeds0–4

- Cross-scene C04/C11/C06

- Native Video V2

- Phase2A–2K cleanup

- C03 causal/smoke/full collection

- metric closure synthetic test

## 21.3 绝对不能动的路径/对象

- /root/MineSim-Dynamic frozen HEAD/tag；不得reset/clean。

- FullMine semantic/bitmap symlink targets；不得为目录整理移动。

- /root/autodl-tmp/90_MineSim_ARCHIVE、98_MineSim_QUARANTINE、99_MineSim_CLEANUP_MANIFEST。

- C03 frozen JSON/lock/result/runtime artifacts；不得覆盖或重跑。

- C13 one-time evaluation evidence；永久禁止retry。

- Value V2 checkpoint/normalization/model freeze；不得改权重、refit normalization或retune after C03。

## 21.4 当前 HOLD

| **对象**                                | **HOLD原因**                                                            |
|-----------------------------------------|-------------------------------------------------------------------------|
| C03 Value V2 real evaluation            | inference load/forward chain尚未锁定；未授权。                          |
| Historical C13 proven evaluator harness | 现有11个.py候选无torch.load/load_state_dict；需全/root/autodl-tmp搜索。 |
| Exact nested feature mapping            | 结构已知，下一步需要按vehicles+pair_features路径正式冻结。              |
| Production drivability                  | 缺官方mask/authoring rule。                                             |
| Terrain/Z/slope                         | datum与slope语义未权威验证。                                            |
| V2H / Π_safe / hard pruning             | 未实现或未批准。                                                        |
| 云端Word实时库存/手动删除               | 未做live inventory。                                                    |
| Map Showcase V3                         | encode/release未完成，SIGKILL原因未验证。                               |

## 21.5 当前真正下一步

低资源执行“C03 exact nested JSON feature mapping + 全 /root/autodl-tmp 历史 C13 forward harness 搜索”。完成标准：

7.  12个feature按冻结顺序从root_state.vehicles与root_state.pair_features精确提取，得到(135,12)，全部finite；delta_v、heading/pi、Omega AND、alpha3语义逐root通过。

8.  找到唯一可复核的checkpoint load/forward harness，或明确证明无历史harness可复用。

9.  在不加载真实C03 checkpoint的情况下，先锁定producer/model class/load_state_dict/eval/no_grad/\[N,16\]合同。

10. synthetic checkpoint-compatible forward PASS 后，才能创建真正one-time C03 Value V2 evaluation preauth。

11. 真实forward前必须再次确认C03 metrics未打开、repo clean、所有SHA一致。

资源：当前低资源；不要开高卡。只有真正one-time forward/evaluation时再决定是否开高资源。

## 21.6 继续前必须先检查

cd /root/MineSim-Dynamic  
source /root/miniconda3/etc/profile.d/conda.sh 2\>/dev/null \|\| true  
conda activate minesim  
export PYTHONPATH=/root/MineSim-Dynamic  
export CUDA_VISIBLE_DEVICES=""  
  
git rev-parse HEAD \# 必须 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e  
git status --short \# 不得出现未知 tracked/staged 改动  
sha256sum \<C03 full freeze\> \<model freeze\> \<checkpoint\> \<normalization\> \<metric contract\> \<feature inventory\>

# 附录 A：统一执行 / 恢复 Checklist

- □ 确认当前任务是低资源还是高资源；不要默认开卡。

- □ 确认正式repo路径与minesim环境。

- □ 核HEAD、status、cgroup、process、screen。

- □ 核输入文件存在与SHA。

- □ 确认输出目录/START/CAPTURE/result原先不存在。

- □ compile/import/static gate。

- □ 写START后只执行授权次数。

- □ 无论RC如何立即写CAPTURE；禁止自动重跑。

- □ 按technical/scientific分类，不用文件名或RC单独判断。

- □ 冻结PASS/FAIL/HOLD并记录next。

- □ 长日志/结果写/root/autodl-tmp并压缩上传。

- □ 任何cleanup/restore均使用manifest，不凭目录美观操作。

# 附录 B：本交付包文件 Manifest

| **文件名**                                                            | **分类**        | **字节数** | **SHA256**                                                       |
|-----------------------------------------------------------------------|-----------------|------------|------------------------------------------------------------------|
| AI接手文档(1).zip                                                     | 原始/历史压缩包 | 1010571    | b0cd18a661ec5a07990a762e0086496d5c364363ad8e4c5a9308442a071625d8 |
| AI接手文档(2).zip                                                     | 原始/历史压缩包 | 1189654    | 0d84f9cadc2e1250b2f6434edb62c865a4abe3726d9888b75156ef8437a70a13 |
| AI接手文档.zip                                                        | 原始/历史压缩包 | 1189654    | 0d84f9cadc2e1250b2f6434edb62c865a4abe3726d9888b75156ef8437a70a13 |
| CROSS_SCENE_DYNAMIC_CONCLUSION_V1(1).zip                              | 原始/历史压缩包 | 6886       | 2dde3d66652097ab8319ac44693f2c035435f838799e24ff6147facc6565ca0b |
| CROSS_SCENE_DYNAMIC_CONCLUSION_V1.zip                                 | 原始/历史压缩包 | 6886       | 2dde3d66652097ab8319ac44693f2c035435f838799e24ff6147facc6565ca0b |
| MineSim-Dynamic_全项目阶段性总总结与AI无缝接管手册_2026-08-18(1).docx | 历史/阶段Word   | 85735      | 47108531428772ae91128bd212ff5bc884c9d9d78fc2bf4667bfc3ec17a619ef |
| MineSim-Dynamic_全项目阶段性总总结与AI无缝接管手册_2026-08-18.docx    | 历史/阶段Word   | 85735      | 47108531428772ae91128bd212ff5bc884c9d9d78fc2bf4667bfc3ec17a619ef |
| MineSim-Dynamic_全项目阶段性总总结与AI无缝接管手册_2026-08-21(1).docx | 历史/阶段Word   | 91471      | 84d630f961346411fc08bc5a8e7329d6cf4607cc0ae6ad7d4ef040a06a3d1d7d |
| MineSim-Dynamic_全项目阶段性总总结与AI无缝接管手册_2026-08-21.docx    | 历史/阶段Word   | 91471      | 84d630f961346411fc08bc5a8e7329d6cf4607cc0ae6ad7d4ef040a06a3d1d7d |
| MineSim-Dynamic_全项目阶段性总总结与AI无缝接管手册_2026-08-23(1).docx | 历史/阶段Word   | 75243      | e260c2414b83e3fa13ea78733c77f2943a063f7d8f6ad6c23123e035fdd5872a |
| MineSim-Dynamic_全项目阶段性总总结与AI无缝接管手册_2026-08-23.docx    | 历史/阶段Word   | 75243      | e260c2414b83e3fa13ea78733c77f2943a063f7d8f6ad6c23123e035fdd5872a |
| MineSim_handoff_summary_V1.docx                                       | 历史/阶段Word   | 38468      | 24d5392af05f332e182413e589ee50d8226d9b71333325285d6b275740724ba3 |
| MineSim_云端项目整理最终文档包(1).zip                                 | 原始/历史压缩包 | 53552      | b421fae9b0f36b948b5fda716f874f09256a670846a6e8fa41752b4620240251 |
| MineSim_云端项目整理最终文档包.zip                                    | 原始/历史压缩包 | 53552      | b421fae9b0f36b948b5fda716f874f09256a670846a6e8fa41752b4620240251 |
| MineSim_阶段性接手总结_V1(1).docx                                     | 历史/阶段Word   | 38631      | 447708c4e54749bd1d3345a0923aa665f54f7c8184087568491b3b8a59dcb98f |
| MineSim_阶段性接手总结_V1.docx                                        | 历史/阶段Word   | 38631      | 447708c4e54749bd1d3345a0923aa665f54f7c8184087568491b3b8a59dcb98f |
| MineSim地图更换.7z                                                    | 原始/历史压缩包 | 1043429    | e66b8e2154b43a05a58590eae9376497f68e1c8426bf2cbd8e876c7a64664114 |
| PAPER1_V0_OBSERVATIONAL_FREEZE_V1(1).zip                              | 原始/历史压缩包 | 4542       | 714698023347899f2b3f52e13965d6507eac7c325ad681ee48167b266521460d |
| PAPER1_V0_OBSERVATIONAL_FREEZE_V1.zip                                 | 原始/历史压缩包 | 4542       | 714698023347899f2b3f52e13965d6507eac7c325ad681ee48167b266521460d |
| PAPER_METHOD_COMPATIBILITY_DECISION_V1(1).zip                         | 原始/历史压缩包 | 3658       | 2c2f85767b60e139bd9d6b56a6b24d7b3a0afd95c5ca802b81ad882acb67cb41 |
| PAPER_METHOD_COMPATIBILITY_DECISION_V1.zip                            | 原始/历史压缩包 | 3658       | 2c2f85767b60e139bd9d6b56a6b24d7b3a0afd95c5ca802b81ad882acb67cb41 |
| RADEME.txt                                                            | 其他项目材料    | 41285      | 6ffd910cbbe9fb6b56af4b37153b96120dd3ea0dbd74d141732e601fc7935ac8 |
| RUN_C03_AMENDMENT_ONE_STEP_SMOKE_ONCE_V1.sh                           | C03脚本/代码    | 10318      | 17b8b49c36219047f9babf2aaaa42b217f363e52e552a80f187f420789f74521 |
| RUN_C03_COLLECTION_PREAUTH_STATIC_FREEZE_V1.sh                        | C03脚本/代码    | 12627      | bf040b9c0f81e1e24b1328ae1c26c5e4627d6f93ebc37cfac617e93dd7fedb6e |
| RUN_C03_CURRENT_SEMANTIC_ZONE_CONTRACT_V1.sh                          | C03脚本/代码    | 30121      | 1c9bab20db05ad9b3b4282940b38dcbbfd4afdf5911a9f1877c1f1790201dadb |
| RUN_C03_FULL_STATIC_RUNTIME_ADMISSION_AUDIT_V1.sh                     | C03脚本/代码    | 5055       | ea213457da28e29a4b050d859048456af6819ae78c9acb80cd36697a96a332c2 |
| RUN_C03_NOMCTS_TECHNICAL_RETRY1_V1.sh                                 | C03脚本/代码    | 14849      | 4a5d2065d56e8cc2d0526a4baa9c059b9fb27c7b64dcf9530da021e96b548507 |
| RUN_C03_ONE_STEP_COLLECTOR_SMOKE_ONCE_V1.sh                           | C03脚本/代码    | 8439       | ab5caf74cbc514e33b82c4937ec97c96f98898939edf486a930d8a12449f4f5a |
| RUN_C03_ONE_STEP_SMOKE_TECHNICAL_RETRY1_ONCE_V1.sh                    | C03脚本/代码    | 11019      | de0764266a40ceac5dc991a23b23f4a3829f9e87aaff699b0b9513c4f3e9d178 |
| RUN_C03_RUNTIME_SMOKE_PROTOCOL_AMENDMENT_V1_STATIC.sh                 | C03脚本/代码    | 14792      | 16f4d4a6357b801408f8f9f447b2ea9a982e2627a08e41f1fd78c19c440977a4 |
| RUN_C03_SMOKE_IMPORT_FIX_AND_RETRY1_PREAUTH_V1.sh                     | C03脚本/代码    | 12207      | 83a17354e8e739f2c64059018420f30f828781573d3deae8777186eb1224208f |
| RUN_C03_STATIC_REVIEW_AND_SMOKE_PREAUTH_V1.sh                         | C03脚本/代码    | 13650      | 925928ec26e1de99ca49f73fd5a9145398de31c16a530250fd52e6f54b11c7be |
| RUN_DERIVE_C03_RUNTIME_RUNNER_STATIC_V1.sh                            | C03脚本/代码    | 17058      | 43c9f1311aa5da02a465bff59cbde98567dbeb2e935828c897f8c2ec2a1d316c |
| c03_current_semantic_collector_binding_v1.py                          | C03脚本/代码    | 8253       | c15056887bf481e67fed01ffbe90c26d6553c5fe2377e5c4bb9f7408f5e99a01 |
| 原项目复现.zip                                                        | 原始/历史压缩包 | 20644638   | bee262cbdc9aa366ae22af6dc6b7565707bd00534e9426ea5bb0a62d81d27516 |
| 可参考论文.7z                                                         | 原始/历史压缩包 | 22895976   | 79a0707d2dfdd42b04c8622b505b371885ec558af1183db3db67f1e6af5b6f5c |
| 地图新建相关文件.zip                                                  | 原始/历史压缩包 | 9776650    | 1e499fd92d3d76ae7167960d492e8760fc8aa7b73180458c0e90aefa07e1a44d |
| 接下来方向.7z                                                         | 原始/历史压缩包 | 32351216   | 43b15ae6b089887f99efdd18ff04681793e5f693e0f0592ae76ef2dbdbd60c69 |
| 粘贴的文本 (1)(20260823-173304).txt                                   | 终端日志上传    | 5806       | 741485e5aa35d41aa07ae4605009969ca8f6975fb813835dce98709cf71aa8fc |
| 粘贴的文本 (1)(20260823-173500).txt                                   | 终端日志上传    | 5851       | 690dbcdf9ce48aee83dba8e85a9b2fbb76eb5fa3dcab8ea4c38f6344a2ef1c8c |
| 粘贴的文本 (1)(20260823-174609).txt                                   | 终端日志上传    | 6373       | 77e16f59e01f2004b24d0c735aa05c175684f9e812c4bdc34a984a4dd6f69542 |
| 粘贴的文本 (1)(20260823-175108).txt                                   | 终端日志上传    | 64673      | e8f3fbbf423b04915053c3a33bf9cd90ad489fd6cf0b4a86af84f9cd85da6c94 |
| 粘贴的文本 (1)(20260824-022534).txt                                   | 终端日志上传    | 18449      | 6deb544473465bc76fff2c8aaa17ba699d31c2917b01a44047054f42f4b0bc38 |
| 粘贴的文本 (1)(20260824-022640).txt                                   | 终端日志上传    | 63075      | 3d78938acd365e217ed13e93997344d1d6808ca365ce15c7b6ac3978c47e86dc |
| 粘贴的文本 (1)(20260824-022948).txt                                   | 终端日志上传    | 31486      | 821bfa041352fa3847ab78923fe7b5143538abd22037c5083c513d7c250f53b2 |
| 粘贴的文本 (1)(20260824-023223).txt                                   | 终端日志上传    | 17444      | 96e4f4091830947d45090719c8b0cac5061e577513c67a7ed0970e1f3ed8f1b7 |
| 粘贴的文本 (1)(20260824-023346).txt                                   | 终端日志上传    | 32255      | ba71dfefc61cda2e7f7b674209a9c55523480664a13f79db2a0dd6f64a43be64 |
| 粘贴的文本 (1)(20260824-023540).txt                                   | 终端日志上传    | 27197      | bd6ee48f933d445a8a4cb6cfff0b72a15cfd4d07c0c9e334b4fa64948abc2f74 |
| 粘贴的文本 (1)(20260824-023926).txt                                   | 终端日志上传    | 28771      | c48931e1635cf7ced5b4b1f0b7be44d4be309beaebc9b27488e0d3297b3724c7 |
| 粘贴的文本 (1)(20260824-024635).txt                                   | 终端日志上传    | 26891      | fa89b3cdcca83728c0a2435bac2474383068fac188a772517b7a959e59bd4dba |
| 粘贴的文本 (1)(20260824-030307).txt                                   | 终端日志上传    | 5762       | 5d480768caba32e819abb16eef92b4e7fc4c16b4f12c529747016f6293703ac6 |
| 粘贴的文本 (1)(20260824-030601).txt                                   | 终端日志上传    | 37218      | 1f3c4f7f5bbd78ad02e55f5db3195a284d0a43591cf6e71fb5a8c4d722b90bcf |
| 粘贴的文本 (1)(20260824-032316).txt                                   | 终端日志上传    | 37598      | e5507d638a48755db8ce565872ee8728ca4c29675b2664dba82433b671daddf4 |
| 粘贴的文本 (1)(20260824-033455).txt                                   | 终端日志上传    | 6667       | 6809fb1e95722f214069ecb50a96a4c46b627c7abd7c68c1d2a11700552a93b4 |
| 粘贴的文本 (1)(20260824-033845).txt                                   | 终端日志上传    | 13905      | 85831795abc3fe6dabb34d54f0f2ce8484485a45682bdfce9c5d823cc95bce8b |
| 粘贴的文本 (1)(20260824-035015).txt                                   | 终端日志上传    | 8478       | 31e543c02c22dc7c66437b06fa8a23fc6deed2d03cfe979fe66506c56fefd40f |
| 粘贴的文本 (1)(20260824-040412).txt                                   | 终端日志上传    | 6111       | beff607b647c0d09ff1d28de7e128d886b6f135ad348e1ce1fd8dfc1df1298e7 |
| 粘贴的文本 (1)(20260824-040639).txt                                   | 终端日志上传    | 9893       | ef52e36e2824e7df983f3ba3d0eaac337b0438585e12a04767f96d1b8275d11d |
| 粘贴的文本 (1)(20260824-040825).txt                                   | 终端日志上传    | 25031      | e5bde8b51b40fbc01d71b2e6cb3bd4b3ac0ecf97b742780adb43defda437d020 |
| 粘贴的文本 (1)(20260824-041126).txt                                   | 终端日志上传    | 9037       | 4f0784b083e878bd3f21f12c10136a2b98dd42b2785c077e683b5b1509319baa |
| 蒙特卡洛实现.7z                                                       | 原始/历史压缩包 | 27994648   | 719bed9d7fe82d453eb0cded6bb60f0b5ddb06419724c0a2d4fe3674e3387bd9 |
| 蒙特卡洛效果对比.7z                                                   | 原始/历史压缩包 | 1651563    | 4c719ebbc86304b26e3d598e57aaa557ec2b0d79dd3dcc488620acc4247aa3ee |

证据来源：本附录由打包时工作区可见的 62 个项目源文件生成；不包含为内部分析临时生成的 extracted 文本。精确范围以最终 ZIP 内 PACKAGE_COMPLETE_MANIFEST.csv 为准。
