**MineSim-Dynamic**

**全项目超详细阶段性总总结与 AI 无缝接管手册（2026-08-24 晚间更新）**

Evidence cutoff：2026-08-24（截至 C11 100m causal smoke 科学 PASS、Value V3 100m collection 预注册与 derived collector 静态派生；执行授权仍 HOLD）

**主线：MineSim 复现 → 蒙特卡洛/MCTS 接入 → 单车跑通 → 双车冲突场景构建 → FullMine 新地图接入 → Fleet-MCTS 双车联合规划与多种子验证 → 原生 MineSim 可视化与汇报材料 → 云端文件安全整理 → 后续神经网络接入**

用途：供下一位 AI / 工程人员在不重新扫描全项目、不重复已冻结实验、不重新询问大量背景的前提下，安全、低成本、可复现地继续推进。

正式仓库：/root/MineSim-Dynamic  
实验数据根：/root/autodl-tmp  
当前冻结 HEAD：112d2bd0f3412fc83b13d5587d2b41402d2d0f5e

# 文档控制与证据口径

| **项目**     | **当前定义**                                                                                                                                                              |
|--------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 证据截止     | 2026-08-24；已覆盖 C03/Value V2 证据闭合、Value V3 固定 9-fold development、C11 coverage expansion、60m 技术不确定冻结、100m 科学 PASS、100m collector 预注册与静态派生。 |
| 事实优先级   | 当前 AutoDL 终端 / Git / 源码 / 文件 SHA / 实际运行输出 \> frozen result/manifest/lock/bundle \> 最新交接 Word \> 历史 Word \> 计划 \> 模型记忆。                         |
| 作者归属     | 云端脚本、锁与日志可以证明“实际完成了什么”，但并非每个文件有独立 Codex 作者签名；本文不虚构逐文件作者。                                                                   |
| 失败分类     | 必须区分 wrapper/import/path/runtime contract/technical/scientific。文件存在不等于 PASS；需结合 RC、JSON、结果字段与 gate。                                               |
| 未验证规则   | 任何缺少直接证据的内容标记“未验证/HOLD”；不得用常识补齐。                                                                                                                 |
| 文档适用范围 | 覆盖当前会话与 Library 中可读取的 MineSim 项目文档、终端日志与冻结证据；实时 AutoDL 全盘文件库存仍须单独 live inventory，未验证项继续标记 HOLD。                          |

本文整合了 2026-08-18、08-21、08-23、08-24 各版综合接手手册、RADEME、项目压缩包/冻结包、2026-08-23～08-24 终端日志，以及本轮 Value V2 closure、Value V3 9-fold、C11 60m/100m coverage 与 derived collector 静态派生的真实输出。旧文档中的“下一步”仅作为历史快照；与更晚终端结果冲突时自动降级。

证据来源：MineSim-Dynamic_全项目阶段性/超详细接手 Word（08-18/21/23/24）、RADEME.txt、20260823-20260824 终端日志、当前上传的 20260824-111044 文本，以及 AutoDL 中 SHA 绑定的 JSON/PY/result/log。

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
| 9\. 阶段六：Fleet-MCTS 联合规划、多种子与跨场景结论           | 文末：最终快速接手区（当前有效）                 |
| 10\. 阶段七：原生 MineSim 可视化与汇报材料                    | 附录 A：统一 preflight / recovery checklist      |
| 11\. 阶段八：云端文件安全整理、目录系统与恢复                 | 附录 B：本交付压缩包文件 Manifest                |
| 12\. 阶段九：后续神经网络接入与当前 C03 / Value V2 进展       |                                                  |

# 1. 当前项目 30 秒状态与快速结论

| **阶段**                        | **状态**                     | **当前真实结论**                                                                                                                          |
|---------------------------------|------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| MineSim 原项目复现              | PASS / FROZEN                | Dapai/Jiangtong IDM、replay 与 closed-loop baseline 已建立；不重做。                                                                      |
| Pure MCTS 接入                  | PASS / FROZEN                | 真实 MineSim online closed-loop 已跑通，历史 strict expert 448 条。                                                                       |
| 单车跑通                        | PASS / FROZEN                | J117 Phase4C 423 steps；FullMine representative Pure MCTS 3/3。                                                                           |
| 双车冲突场景                    | PASS / FROZEN                | J117、Polygon21 与 cross-scene 通过 NO-MCTS exact footprint overlap 建 causal benchmark。                                                 |
| FullMine 新地图                 | PASS / FROZEN                | Vector V2 semantic + V4 bitmap/runtime/planner，targeted 7/7 + old-map regression。                                                       |
| Fleet-MCTS                      | PASS + 负结果                | Polygon21 5/5；C04/C06 success；C11 安全但 deadlock，必须保留。                                                                           |
| 原生可视化                      | PASS / FROZEN                | Native Video V2 final；Map Showcase V2 stable；V3 incomplete/HOLD。                                                                       |
| 云端整理                        | PASS / COMPLETE              | 约 530→121；423 move/isolate；科研文件删除 0；restore gate PASS。                                                                         |
| C03 independent collection      | PASS / FROZEN                | 135 roots、2160 action records、8640 expansions，benchmark_success=True。                                                                 |
| Value V2 independent validation | CLOSED / SCIENCE FAIL        | C03 normalized regret 0.3506036 \> immediate 0.1831771；post-failure closure 已冻结，DO_NOT_INTEGRATE，禁止重跑、retune 或用 C03 选架构。 |
| Value V3 fixed development      | TECHNICAL PASS / NOT READY   | 12→64→64→16 + root-normalized weighted pairwise logistic；9/9 folds 完成；C04/C06 win、C11 fail；2/3，primary gate FAIL，禁止继续调网络。 |
| C11 coverage expansion          | 100m PASS / 60m INCONCLUSIVE | 现有 C11 890 roots 为单一 seed0 连续 episode；60m 一次性结果不可恢复，no retry；100m exact physical-overlap causal smoke 科学 PASS。      |
| 100m development collector      | STATIC PASS / EXECUTION HOLD | 预注册 d9a25a…；derived collector d0c024…；reverse-to-parent byte exact；collection root 未创建，历史 evidence binding audit 未完成。     |

当前真正节点：Value V2 已按 C03 独立科学失败正式关闭；Value V3 固定 3 seeds × C04/C11/C06 共 9 folds 技术完成，但严格 3/3 场景门槛仅 2/3，失败定位到 C11 coverage。现已完成 C11 60m/100m 起始距离候选的静态构造、loader/safety gate 与 NO-MCTS causal smoke：60m 因一次性运行结果不可恢复被保守冻结为 technical-inconclusive；100m 科学 PASS。随后已冻结 100m development collection preregistration，并从 parent collector 反向字节等价派生出隔离输出的 100m collector。当前唯一 blocker 是审计 derived collector 中历史 LOADER_RESULT / NOMCTS_RESULT / STATIC_CONFIG 等证据绑定究竟属于 lineage 还是 candidate-specific；在此之前 collection 未授权、未执行。

资源判断：当前下一步仅低资源 CPU，只做 read-only evidence binding audit；高资源卡可关闭。只有该审计 PASS、静态执行授权写入且 planned collection namespace 仍为空时，才考虑开启高资源卡运行唯一一次 100m Fleet-MCTS development collection。

# 2. 真实发展时间线

| **日期**          | **阶段**                                             | **真实完成与意义**                                                                                                                                                       |
|-------------------|------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 2026-07-26        | 云端 baseline / 安全操作规范                         | AutoDL 安全交互、Git 恢复、文件优先、“先读接口再改代码”。                                                                                                                |
| 2026-07-30～08-02 | Pure MCTS closed-loop                                | MCTSPlanner→search/reward→trajectory adapter→Controller/KBM；commit 94693dc；448 strict expert。                                                                         |
| 2026-08-03～07    | 五 Planner / budget / interface audit                | MCTS、IDM、Frenet、Adapted Maneuver、Simple；形成搜索/adapter/controller故障分域。                                                                                       |
| 2026-08-08～10    | 双受控 + J117                                        | Jiangtong负筛选；J117单车423步；双车NO-MCTS冲突+Pure MCTS 5-seed。                                                                                                       |
| 2026-08-11～14    | FullMine V1→Vector V4                                | O(1) token lookup、Vector V2 semantic、bitmap/runtime/planner修复；V4 freeze HEAD 112d2bd。                                                                              |
| 2026-08-14        | Representative Pure MCTS                             | 跨代表区域3/3 PASS并冻结。                                                                                                                                               |
| 2026-08-15        | Polygon21 Fleet-MCTS                                 | NO-MCTS真实物理重叠；Fleet budget64/depth8 5/5。                                                                                                                         |
| 2026-08-16        | Native Video + safe cleanup                          | Native Video V2 final；Phase2A–2K可逆整理；Map Showcase V3 SIGKILL未收口。                                                                                               |
| 2026-08-17～18    | Cross-scene + Paper1 safety                          | C04/C11/C06收口；C11安全死锁负结果；SafetyRisk V0/sidecar推进。                                                                                                          |
| 2026-08-21        | current-semantic NN链                                | V2R/zone/dynamic V2V/shadow/dataset/collector；C04/C11/C06 collection；Value V1 LOSO science FAIL。                                                                      |
| 2026-08-22～23    | Value V2 + C13 independent                           | final-dev模型冻结；C13 115 roots/1840 rows；forward一次但metric绑定失败，scientific metrics未评估，禁止重跑。                                                            |
| 2026-08-23        | replacement C03 qualification                        | C10/C14淘汰；C03 physical/static/NO-MCTS causal qualification推进并最终冻结。                                                                                            |
| 2026-08-24        | C03 collector与Value V2准备                          | one-step technical smoke PASS；Full Collection 135 roots/2160 rows PASS；metric closure与feature/model inventory PASS；真实Value V2评估未打开。                          |
| 2026-08-24        | Value V2 closure + Value V3 fixed run                | C03 independent science FAIL 后关闭 Value V2；V3 pairwise 9/9 folds 技术 PASS，C04/C06 win、C11 fail，2/3，转入 coverage expansion。                                     |
| 2026-08-24        | C11 coverage provenance + 60m/100m candidates        | 证明 890 roots=1 个 seed0 89s episode；只改变 A/B 初始 route-s 距离构造 60m/100m，scenario/manifest/static/loader/safety chain 冻结。                                    |
| 2026-08-24        | 60m/100m causal smoke                                | 60m 经 CLI/env/output-root 三类技术故障后保守冻结为 technical-inconclusive、one-time consumed；100m RC=0、真实 physical overlap、timeline sync、post-conflict complete。 |
| 2026-08-24        | 100m collection prereg + static collector derivation | 1 个新 seed0 development episode 预注册；root count 不预设；parent c9100130… 仅 5 项授权替换，derived d0c024…，reverse byte exact；执行仍 HOLD。                         |

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

# 12. 阶段九：后续神经网络接入——Value V1→V2→V3 与 C11 coverage expansion

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

## 12.7 Value V2 exact evaluator 历史静态节点（后续已在 12.8 正式闭合）

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

- 历史节点：当时尚未加载 checkpoint 或执行真实 C03 forward；该状态随后已被一次性 C03 independent evaluation、diagnostic 与 post-failure closure 覆盖。

该历史 blocker 已完成：exact feature mapping、checkpoint load/forward chain、C03 independent evaluation 与 failure closure 均已冻结；当前执行节点以 12.8～12.13 与文末“最终快速接手区”为准。

## 12.8 Value V2 证据闭合与正式停止

Value V2 的 target probe、true-neural LOSO、C03 independent evaluation 与 post-failure diagnostic 已完成证据闭合。target probe 最优候选为 ROOT_CENTERED_Q；true-neural LOSO 虽有 C11/C06 两场胜出，但三场景平均 regret=0.2432330458，差于 immediate baseline=0.2111271728。C03 独立结果 normalized regret=0.3506035818，差于 immediate=0.1831771113。因此正式决策为 VALUE_V2_CLOSED_DO_NOT_INTEGRATE_REDESIGN_REQUIRED。

- 冻结：PAPER1_VALUE_V2_POST_FAILURE_EVIDENCE_CLOSURE_V1.json，SHA256=c6ceec2751b64167f09877b406f129226b3ea21116af4e0f4f6de7cf5cdb777b。

- 永久边界：REPEAT_TARGET_PROBE=False、REPEAT_TRUE_NEURAL_LOSO=False、C03 hyperparameter tuning=False、C03 architecture selection=False、MCTS value integration=False。

- C13 one-time forward 已发生但 metrics 因 harness 绑定错误未评估；该 one-time protocol 已消耗，不能作为“再跑一次”的理由。

## 12.9 Value V3 development-only 预注册、固定运行与 C11 失败定位

Value V3 保持冻结的 12 维输入与 12→64→64→16 架构，只把训练目标改为 ROOT_NORMALIZED_WEIGHTED_PAIRWISE_LOGISTIC。固定 seeds=\[20260824, 20260825, 20260826\]，按场景 median 聚合；禁止 hyperparameter search、best-seed selection、C03/C13 使用和 MCTS integration。9/9 folds 已完整执行，技术链 PASS。

| **场景** | **3 个 seed normalized regret**   | **Median** | **Immediate baseline** | **固定结论**                          |
|----------|-----------------------------------|------------|------------------------|---------------------------------------|
| C04      | 0.1997966 / 0.1746510 / 0.1400719 | 0.1746510  | 0.2347117              | PASS                                  |
| C11      | 0.2313983 / 0.2344567 / 0.2326794 | 0.2326794  | 0.1567370              | FAIL                                  |
| C06      | 0.0896356 / 0.1023041 / 0.1716961 | 0.1023041  | 0.2419329              | PASS                                  |
| 整体     | scene median mean                 | 0.16987816 | 0.21112717             | secondary gate PASS；primary 3/3 FAIL |

- VALUE_V3_SCENE_WIN_COUNT=2；PRIMARY_GATE=False；SECONDARY_GATE=True；V3_DEVELOPMENT_READY=False。

- 固定 summary：development_execution_v1/PAPER1_VALUE_V3_DEVELOPMENT_LOSO_SUMMARY_V1.json，SHA256=8d6acdbb92ffe98d95589d9e831e32be4a729fed4e54a9731d9a755cf6ed83c6。

- 正式决策：VALUE_V3_NOT_READY_EXPAND_DEVELOPMENT_EPISODES_BEFORE_ANY_FURTHER_ARCHITECTURE_CHANGE。不能在看见 C11 失败后改 loss、seed、epoch、target、C11 权重或加入 C03。

## 12.10 C11 现有数据 provenance 与 60m/100m coverage 构造

逐 root / 逐 action identity audit 证明，development dataset 中 C11 的 890 roots、14240 action rows 全部来自同一个 current-semantic、seed0、89.0s 连续 episode；它们不是 890 个独立 episode。每个 root 恰有 16 个 joint actions，内部映射 joint_index=A\*4+B，collector 外部 joint_action_id 为字符串“ A,B ”。

| **证据对象**            | **SHA256 / 事实**                                                |
|-------------------------|------------------------------------------------------------------|
| C11 root JSONL          | 1df7528f2e47c6089e4fa137ebcdb7905b20a3f11adec01aac455e36da7be15e |
| root summary            | 4d89923c026168b128ea4219428b85eb5ac65c68ecee2256eaab90272a05adfa |
| episode manifest        | c0521ce61259103d6b87c97f5e185293a58377011bf2214733f460db03c6c54a |
| Fleet result            | 47a6d570f65953e7dea35f46eb9f8ac63975c1e9e96402f6753f3f41e839547e |
| parent collector source | c9100130f17ab27eb2495db634db46763d1b49ed7856594a366fb8c65e4ce830 |
| single-episode freeze   | 37dc72decdc819a243161b42e68248c48d1361e460897c9cd1373a20e903c4d5 |

扩展维度选择为双方相对冲突点的对称初始距离：保持 route、conflict point、seed0、MCTS budget/depth、target speed、DT、action space 与 reward/Q semantics 不变，只改变 A 的 ego_info.start_states 初始 pose，以及 B 的 TrajSegmentInfo\[0\].states 各列第 0 个值。B 后续 899 帧原始 trajectory 保持不变，并已审计其不会作为受控 B 的 post-initial runtime truth。

| **候选** | **Scenario SHA**                                                 | **Manifest SHA**                                                 | **静态/loader/safety**                            |
|----------|------------------------------------------------------------------|------------------------------------------------------------------|---------------------------------------------------|
| 60m      | cf9d06f73b6941af1d3c262d894f3a4676d9494f437237f64257562f53d21cc0 | 0281e7a30899cef4eda87309a295175e15d1de6b38cb1015b224f7d1539a0742 | 静态 content、loader smoke、initial safety 均通过 |
| 100m     | 3d71f2beeec6e0782099b65145ae944ea7560d64e5b934e3b6cdca7f40e4f5ce | b18dd8b288a37424a94e22122d6a7572f0aa88ae991d97376db5930d1d2ce8bb | 静态 content、loader smoke、initial safety 均通过 |

## 12.11 60m technical-inconclusive 与 100m causal scientific PASS

| **对象/尝试** | **真实现象**                                                                                                                 | **分类与处理**                                                                                         |
|---------------|------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------|
| 60m attempt0  | RC=2；缺少 required CLI --source-index；run_60m 未创建。                                                                     | pre-runtime CLI technical failure；冻结后仅授权一次 technical retry。                                  |
| 60m retry1    | RC=1；KeyError: 'SEM'；SEM/MAP_ROOT/DATA_ROOT/BREF 未传入。                                                                  | pre-runtime required-env technical failure；解析并 SHA 绑定历史环境后授权 retry2。                     |
| 60m retry2    | RC=1；LOG.write_text 报 FileNotFoundError，run_60m 未预创建。propagate 位于 broad Exception try 内，无法证明或否定实际传播。 | 保守冻结 technical-inconclusive；one-time 60m execution consumed；Retry3=False；不是 scientific FAIL。 |
| 100m one-time | wrapper 按预授权仅预创建空 run_100m；RC=0；result+internal log 完整落盘。                                                    | 科学 PASS；one-time consumed；rerun=False；eligible for development collection。                       |

| **100m causal 指标**   | **真实结果**                                                                     |
|------------------------|----------------------------------------------------------------------------------|
| status / PASS          | PASS / True                                                                      |
| physical overlap       | True；first=20.700000000000003s；max area=27.770186117685736m²                   |
| center / clearance     | min center distance=0.19318805484990806m；min footprint clearance=0              |
| crossing sync          | A=22.222222222222715s；B=22.222222233867658s；gap=1.164494278782513e-08s         |
| runtime completion     | duration=25.6s；iterations=256；timeline_sync=True；completed_post_conflict=True |
| validity               | nan_or_invalid=False；error=None；DT=0.1；target speed=4.5m/s                    |
| result SHA             | 39c59b5ca30703643290ab43b3b98e2eeb31379ba6ae5bc98f2e05094fc874b3                 |
| scientific pass freeze | 57addcc66b81a7a4f6bb0c2d956138a3839f047c2d151870aba4de10153ce09b                 |

- 60m final freeze SHA256=499e73c5dd0ada4182217781616610ecd1c13729c86cb2779658a14908ffa0a1。60m 被淘汰的原因是“一次性结果不可恢复”，不是证明“60m 无冲突”。

- 100m NO-MCTS runner SHA256=9cb4a9ce886dcecc1c87c65e2f014a048de407ac42999f1b3c5c319a3353733b；其 causal smoke 的 TARGET_SPEED=4.5 与后续 Fleet-MCTS collector 的 TARGET_SPEED=10.5 属于两个不同冻结合同，不得混用。

## 12.12 100m development collection 预注册与 derived collector 静态派生

100m collection 仅预注册 1 个新的 seed0 development episode；不预设 root count，保持 parent collector 的终止语义并接受实际产生的 contiguous 0..N-1 roots；每 root 固定 16 joint actions。Fleet benchmark success 不是 collection acceptance gate，避免按最终规划成败事后筛掉困难 episode。

| **对象**                   | **当前事实 / SHA**                                                                                                                                                                                  |
|----------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| collection preregistration | d9a25af02cdbf19499533d9173e27b3f8c4c8ebe93f0e67b9a4619fc5c27951c；collection_authorized=False；executed=False                                                                                       |
| parent collector           | PAPER1_NEURAL_C11_C06_CURRENT_SEMANTIC_COLLECTOR_V1_UPLOAD.zip 内 source c9100130f17ab27eb2495db634db46763d1b49ed7856594a366fb8c65e4ce830                                                           |
| derived collector          | /root/autodl-tmp/paper1_value_v3_development_only_v1/cross_scene_fleet_mcts_c11_start100m_seed0_paper1_neural_collector_v1.py；SHA d0c024de2ca9e4b1fdf033ba44b34d80451a683ace4d6c1a988e4d4cd8423311 |
| static derivation lock     | d547b2f8ee1974f585a12458ff904385567ce0fb257267f06111c5e07d711160                                                                                                                                    |
| planned output root        | /root/autodl-tmp/paper1_value_v3_development_only_v1/c11_100m_development_collection_v1；当前必须不存在                                                                                             |

派生 source 只允许 5 项替换：C11 scenario path、scenario SHA、manifest path、manifest SHA、RESULT_DIR 默认输出根。反向替换后与 parent source 字节级完全一致；MCTS_BUDGET=64、MCTS_DEPTH=8、MCTS_DT=0.5、SIM_DT=0.1、TARGET_SPEED=10.5、MAX_HORIZON_S=89.0、INTERNAL_COLLISION_SAMPLE_DT=0.1 全部保持不变。

- 静态派生 attempt0 因 parent 默认输出路径使用相邻字符串字面量，完整路径文本 count=0 而失败；失败发生在写文件前，没有产生半成品。retry1 使用 AST semantic + exact source-segment replacement 后 PASS。

- REVERSE_TO_PARENT_BYTE_EXACT=True；REVERSE_PARENT_SHA256=c9100130f17ab27eb2495db634db46763d1b49ed7856594a366fb8c65e4ce830。

- Value/ML surface unchanged；新 collector 内仍未引入 torch/checkpoint/value_network/model.forward，MCTS_value_integration=False。

## 12.13 当前唯一 blocker：derived collector 历史 evidence binding 审计

derived collector 仍保留 parent 中的历史 LOADER_RESULT、NOMCTS_RESULT、STATIC_CONFIG、STATIC_READINESS 与 PROTOCOL_AMENDMENT 绑定。现有静态派生锁明确标记 HISTORICAL_EVIDENCE_BINDING_REVIEW_REQUIRED=True。必须先只读审查 evidence_pass()、相关 assert/if、最终 provenance 字段以及旧 JSON 的 scenario/manifest/route/physical/timeline identity，判断这些对象只是算法 lineage gate，还是与当前 100m candidate identity 强绑定。

- 如果只是 SHA+PASS 的历史 lineage gate：保持 derived source 不动，在 execution authorization 额外绑定当前 100m loader/safety/causal evidence。

- 如果参与当前 candidate 的 scenario SHA、初始位置或冲突判定：必须先静态重绑定到 100m 冻结 evidence，并重新通过 reverse-equivalence/allowed-diff contract。

- 当前禁止：创建 planned collection root、启动 derived collector、执行 MCTS、自动试跑或提前授权 collection。

- 下一步资源：低资源。PASS 标准：对每个历史 evidence 对象给出 LINEAGE / CANDIDATE_SPECIFIC / HOLD 分类，并冻结审计结果。

本节证据锚点：2026-08-24 终端真实输出、当前会话上传日志、/root/autodl-tmp/paper1_value_v3_development_only_v1 下 JSON/PY 冻结文件及其 SHA；逐文件作者未签名，因此只陈述“云端实际完成”，不虚构 Codex 独立作者归属。

# 13. 重要失败、排查、修复与永久禁忌

| **故障/现象**                                    | **原因**                                                                     | **最终处理/证据**                                                           | **以后不能重复**                                                             |
|--------------------------------------------------|------------------------------------------------------------------------------|-----------------------------------------------------------------------------|------------------------------------------------------------------------------|
| Planner/Frenet step150 IndexError                | best_traj长79却访问79；adapter越界。                                         | 安全重采样后跑通；先分search/adapter/controller。                           | 禁止把adapter越界误判为MCTS失败。                                            |
| Multi-ego duplicate actor                        | A/B同时controlled+external。                                                 | controlled token从tracked observation过滤。                                 | 受控车辆绝不能重复为external obstacle。                                      |
| Environment history缺B                           | History主要保存A。                                                           | B使用MultiEgoRuntime同iteration truth。                                     | 禁止用A history假装A+B。                                                     |
| Native B可视化                                   | B不能直接从history回放。                                                     | A history + B live overlay；pose parity≤1e-8。                              | 禁止route_s/CSV/pixel猜B姿态。                                               |
| Jiangtong conflict screening                     | 空间相交但ETA差9.496s。                                                      | 负筛选freeze。                                                              | 空间交叉≠时间冲突。                                                          |
| CollisionLookup false positive                   | 离散lookup与exact footprint定义不同。                                        | causal gate用exact footprint/swept overlap。                                | 中心距/查表/示意图不能替代物理真值。                                         |
| FullMine init慢                                  | 约400k node重复线性scan。                                                    | token2ind O(1)。                                                            | 先profile复杂度，不归咎GPU。                                                 |
| A1 endpoint/A2 mid-stop                          | virtual endpoint geometry / steering-rate infeasibility。                    | virtual endpoint length_rear=0；steering-aware speed cap+backward braking。 | 不盲补bitmap或改goal。                                                       |
| Map/runtime路径失效                              | 整理移动导致绝对路径/软链接失效。                                            | current_paths+restore/symlink gate。                                        | frozen runner优先恢复路径，不直接改代码。                                    |
| Low-memory RC137                                 | 2GiB cgroup不足。                                                            | 低资源preflight后开80GiB/15CPU。                                            | 不低配硬跑大图/长仿真。                                                      |
| Map Showcase V1/V3                               | V1 schema误判；V3 SIGKILL:9。                                                | 读真实schema；V3保留120帧/HOLD。                                            | 不能无证据把SIGKILL写成OOM。                                                 |
| Native Video V1                                  | 1545×3666布局异常。                                                          | V2=1545×1073+ffprobe+human gate。                                           | 科学链可跑≠汇报质量PASS。                                                    |
| Renderer conflict XY/OUT                         | manifest给route_s；wrapper漏OUT。                                            | route station求点；required env gate。                                      | 禁止hardcode XY；wrapper先验env。                                            |
| Video mid-pan blank                              | camera逻辑。                                                                 | V0.2 target-anchored camera。                                               | 自动编码PASS不能替代human gate。                                             |
| Long heredoc/粘贴污染                            | 聊天UI与终端输出混粘。                                                       | 短块、文件优先、ls/file/sed。                                               | 禁止因粘贴异常清目录。                                                       |
| C04 loader float(list)                           | 一元素list/\[N\]\[1\]未规范。                                                | shape normalization。                                                       | 不从旧文档猜exact line。                                                     |
| C04 NO-MCTS MAX_STEPS NameError                  | harness常量遗漏。                                                            | 最小runner fix。                                                            | harness FAIL≠science FAIL。                                                  |
| C11 NO-MCTS 200-step                             | 时间窗不足导致post-conflict false。                                          | 仅延长至21.2s/212。                                                         | 不改冲突物理/算法。                                                          |
| C11 Fleet deadlock                               | 89s无碰撞但不完成。                                                          | 冻结负结果。                                                                | 禁止为全PASS调参抹掉。                                                       |
| Historical448 vs current labels                  | rear-axle/center/producer语义变化。                                          | legacy隔离+current recollection。                                           | schema相同≠label同质。                                                       |
| Collector JSON +inf/false PASS                   | allow_nan=False序列化失败；内存先append。                                    | 删未合同字段；写盘成功后append。                                            | JSONL空不能由内存summary伪装PASS。                                           |
| Collector timeline                               | root absolute vs V0 relative。                                               | 对齐origin/cadence；离线salvage。                                           | 无需重跑已完成仿真。                                                         |
| PyTorch missing                                  | 镜像≠conda env。                                                             | 安装CPU torch 2.8.0+cpu。                                                   | 不要假设基础镜像包等于env包。                                                |
| C13 Value eval metric binding                    | AST误绑main()而非ranking_metrics。                                           | 冻结failure；static fix但禁止retry。                                        | one-time独立验证失败后不得重跑/调参。                                        |
| C09/C10/C14 rejects                              | physical/static/route contract失败。                                         | 按预注册顺序冻结淘汰。                                                      | 不补图、不改planner、不重选。                                                |
| AST env audit                                    | 把os.environ Store误报Load。                                                 | 区分ctx Load/Store。                                                        | 环境依赖审计必须看AST上下文。                                                |
| C03 horizon zero slack                           | 75+15m /4.5=20s=200×0.1。                                                    | 预执行改212，无outcome-informed retuning。                                  | 运行前检查完成门时间余量。                                                   |
| C03 stale 50m check                              | 顶层75m但深层identity仍50m。                                                 | 冻结0-step technical failure，只改两处。                                    | 技术失败不等于science FAIL。                                                 |
| C03 smoke import                                 | helper模块不在script目录。                                                   | 复制byte-identical modules+import gate。                                    | 执行前必须验证import origin。                                                |
| C03 stale C13 guard                              | SOURCE_INDEX !=13/C13-only。                                                 | 完整静态remnant audit。                                                     | 派生runner不能只替换路径。                                                   |
| C03 preauth status guard                         | 旧status与新amendment同时存在。                                              | 完整runtime admission audit。                                               | 不能跑一次暴露一个guard；先全静态清点。                                      |
| One-step RC=1误判                                | 短smoke不可能完成post-conflict。                                             | 技术gate用root/actions/health，不用benchmark success。                      | RC单独不能判scientific fail。                                                |
| Value boundary字段缺失                           | root schema无显式value_model字段。                                           | executed-source audit+preauth boundary。                                    | 不能因字段缺失直接宣告forward发生/未发生。                                   |
| Metric closure依赖遗漏                           | ranking_metrics依赖spearman→pearson/average_ranks。                          | 递归exact closure+synthetic。                                               | 不能只把依赖塞白名单。                                                       |
| codex-env.sh missing                             | 登录路径缺失，来源未知。                                                     | 标路径缺失/HOLD。                                                           | 不能推断文件被删或Codex工作丢失。                                            |
| 60m smoke RC=2                                   | launcher 漏传 required --source-index 11。                                   | argparse 前退出；START/CAPTURE 证据冻结；技术失败。                         | 任何 runner 先读 argparse contract；不得假设无参数。                         |
| 60m retry KeyError 'SEM'                         | launcher 未传播 SEM/MAP_ROOT/DATA_ROOT/BREF。                                | 从历史 env 与 SHA 精确解析后才授权下一 retry。                              | 环境变量必须作为冻结输入，不能凭路径猜。                                     |
| 60m retry output-root FileNotFoundError          | runner 不创建 OUTPUT_ROOT；LOG.write_text 时目录不存在。                     | 控制流审计发现 propagate 在 broad try 内，结果不可判；one-time consumed。   | 不要以“最终写盘失败”自动推断仿真未执行；禁止直接重跑。                       |
| 100m output isolation                            | 沿用 60m launcher 会再次触发持久化故障。                                     | 预授权 wrapper 只预创建 exact empty run_100m 后执行，RC=0。                 | 非科学性修复也必须在执行前写入授权。                                         |
| 100m prereg KeyError coverage_interpretation     | 读取了错误 JSON key；实际为 single\["interpretation"\]。                     | 确认 output 未写入后，仅修 schema 读取并重做静态 prereg。                   | 先读真实 JSON schema；不能用旧 audit 的 key 套 freeze。                      |
| collector derivation DEFAULT_OUTPUT_ROOT count=0 | parent source 用相邻字符串字面量拼接默认路径，语义路径不连续出现在源码文本。 | 失败前未写 derived；retry 用 AST 定位 RESULT_DIR 整段并反向 byte-exact。    | 路径替换不能只靠 string count；对 Python literal 拼接用 AST+source segment。 |

# 14. 当前有效 / SUPERSEDED / ARCHIVE / HOLD 矩阵

| **对象**                                   | **状态**                               | **处理规则**                                                                                 |
|--------------------------------------------|----------------------------------------|----------------------------------------------------------------------------------------------|
| MineSim baseline 2521aa4                   | HISTORICAL / FROZEN                    | 保留回归；不是current HEAD。                                                                 |
| Pure MCTS 94693dc + 448                    | HISTORICAL / FROZEN                    | 专家历史证据；current-semantic隔离。                                                         |
| J117 Phase4C/5                             | FROZEN                                 | 不重跑；multi-ego regression anchor。                                                        |
| FullMine Vector V4 112d2bd                 | CURRENT FROZEN                         | 新研究在独立evidence workspace。                                                             |
| Representative Pure MCTS 3/3               | FROZEN                                 | 无需重做。                                                                                   |
| Polygon21 Fleet v2                         | FROZEN                                 | 正式benchmark；旧harness failures仅provenance。                                              |
| Cross-scene C04/C11/C06                    | CLOSED WITH NEGATIVE                   | C11 negative必须保留。                                                                       |
| Native Video V1                            | SUPERSEDED                             | 保留provenance，不用于正式汇报。                                                             |
| Native Video V2                            | CURRENT FINAL                          | 正式视频evidence。                                                                           |
| Map Showcase V2                            | PASS / HISTORICAL STABLE               | V3不覆盖V2。                                                                                 |
| Map Showcase V3                            | INCOMPLETE / HOLD                      | 120帧；encode/release未完成。                                                                |
| Paper1 V2R/heading/Omega/dynamic           | FROZEN / DIAGNOSTIC                    | 不改变planner behavior；不可外推hard safety。                                                |
| Shadow safe-node                           | OBSERVATIONAL PASS                     | hard pruning not approved。                                                                  |
| Value V1                                   | TRAINING PASS / SCIENCE FAIL           | DO_NOT_INTEGRATE。                                                                           |
| Value V2 final-dev + C03 independent       | CLOSED / SCIENCE FAIL                  | post-failure closure c6ceec…；DO_NOT_INTEGRATE；禁止 retry/retune/C03 selection。            |
| C13 one-time eval                          | FROZEN TECHNICAL FAILURE AFTER FORWARD | metrics未评估；retry forbidden。                                                             |
| C03 causal/technical smoke/full collection | CURRENT FROZEN PASS                    | 禁止重跑；数据进入Value V2静态评估准备。                                                     |
| C03 Value V2 real evaluation               | FROZEN SCIENCE FAIL / CLOSED           | normalized regret 0.3506036 \> immediate 0.1831771；不再是 HOLD。                            |
| Production drivability                     | HOLD / NOT PROVEN                      | 缺官方规则。                                                                                 |
| Terrain/Z/slope                            | HOLD                                   | datum/slope语义未验证。                                                                      |
| V2H probabilistic safety                   | NOT IMPLEMENTED                        | 阻塞full safe-node。                                                                         |
| Policy Network / PUCT                      | NOT STARTED                            | 先完成Value independent validation。                                                         |
| Value-guided MCTS                          | NOT INTEGRATED                         | MCTS_VALUE_INTEGRATION=False。                                                               |
| Value V3 fixed development 9-fold          | TECHNICAL PASS / NOT READY             | C04/C06 win、C11 fail；2/3；结构与 objective 冻结，先扩 coverage。                           |
| C11 existing 80m development episode       | FROZEN PROVENANCE                      | seed0、89s、890 roots、14240 rows；不是 890 episodes。                                       |
| C11 60m coverage candidate                 | FINAL TECHNICAL-INCONCLUSIVE           | one-time consumed；Retry3=False；非 scientific fail；禁止 collection。                       |
| C11 100m causal candidate                  | FROZEN SCIENTIFIC PASS                 | 真实 overlap + timeline sync + post-conflict complete；eligible for development collection。 |
| 100m development collection prereg         | FROZEN / NOT AUTHORIZED                | 1 episode、seed0、root count not preset；planned root 必须为空。                             |
| 100m derived collector d0c024…             | STATIC PASS / HOLD                     | reverse byte exact；历史 evidence binding audit 未完成，禁止执行。                           |

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

| **对象**                              | **SHA256**                                                       |
|---------------------------------------|------------------------------------------------------------------|
| FullMine semantic                     | b85a3d8b28f2252ecb5bda179d514573f6333079def838cd048566f556d95cd0 |
| FullMine bitmap                       | 51abcd5a86e5c510204a5dacc873691506d721f98982ab7f98585d4e0f7efdd0 |
| CollisionLookup                       | 10c1d1339e742ca893fedb4aa51402addfba82e16e08f68339ea35d35ba3043b |
| Representative MCTS freeze            | 322e90d6995c410597d01925de6d77f1fd91ddb8c4c73a25c3e87446d37ac1fa |
| Polygon21 Fleet freeze v2             | b89d290c9cb06d1efb99688ee27b23898ab81d11e36023832477dc2fc834364b |
| Native Video V2                       | f695ba22ecd61c4a643e8ffecac483bc218de9153f95f88b4e0e3006bca03d58 |
| Map Showcase V2                       | 9f78f357eecfc25ea543d163e8d472dc06abeb1fff3215ed30577267750d1e14 |
| Cleanup closeout                      | e3d4ba27bd06c74c7ca23ed55de65208022f07d4e0cb600eb58bcbbcaaf33a4b |
| Dataset Contract V1                   | 46f2e099fbe9090a02b1f9fe8a983e4f8322a2ffeba89a4700de8e278991dcda |
| Value V2 checkpoint                   | ce32cb7943a05d62ea16aee95a86f26bab7521af1d345e39f5c8a410a02ffb13 |
| Value V2 normalization                | 36ee17a182c519c41602c5d414a4e009a569660254bb4bd31fc75a3b705bc6f9 |
| Value V2 model freeze                 | a2be866144446a442cf7a8cb23a7f7ce9041a2d7b86fcded2ff8709f7a24d05b |
| C03 causal freeze                     | 6cec631084980a8273d1951f83829c55aed84766576f11b419b30eedb1566ec0 |
| C03 zone contract                     | 781da697cbac47b7d134eb5cb528faf0989a8a9e04a3ac5992491ed40b747aed |
| C03 technical smoke freeze            | 170dcb466191ccbc537bc58adb44fe032500b52c50aa2736dd822fb50b3201c3 |
| C03 Value nonexecution audit          | ea2da1717c72b658b95edc42047f0cce7a574170b565d1bb485186c299b59385 |
| C03 full collection freeze            | 15c098f72ae0187dd0bb97bd9878aa6860d47df48391e09bd9ad56eb9ac31fa8 |
| Metric closure exact                  | 962c6cd333d9432f566a124d033540a52b10ebde4ed5f87ac695a8e42586e01e |
| Metric closure synthetic              | c08e819cff26a1039165e444b92a3645d359c967109f6f4ccd107c5da93f8cfa |
| Metric closure contract               | 4a3d70acecbcc21d1ffac317039b5ced61414ef00e2de46696969c71f1890a49 |
| Feature/model inventory               | f1c2830809b34403f4dd3f554c605cf6e5a46f9111b59e27d3ff704327afc594 |
| Exact inference source inventory      | 6c561d5b28995f0360e0cac98b7682ea993e303a7fd21e5b456ec17ee75fcda8 |
| Value V2 post-failure closure         | c6ceec2751b64167f09877b406f129226b3ea21116af4e0f4f6de7cf5cdb777b |
| Value V3 preregistration              | ff6c9714925bfa3d264a1d9eac8d236cea8e9a7a5f88e4dc67394201feb6e914 |
| Value V3 development summary          | 8d6acdbb92ffe98d95589d9e831e32be4a729fed4e54a9731d9a755cf6ed83c6 |
| C11 single-episode provenance freeze  | 37dc72decdc819a243161b42e68248c48d1361e460897c9cd1373a20e903c4d5 |
| C11 60m final inconclusive freeze     | 499e73c5dd0ada4182217781616610ecd1c13729c86cb2779658a14908ffa0a1 |
| C11 100m scenario                     | 3d71f2beeec6e0782099b65145ae944ea7560d64e5b934e3b6cdca7f40e4f5ce |
| C11 100m manifest                     | b18dd8b288a37424a94e22122d6a7572f0aa88ae991d97376db5930d1d2ce8bb |
| C11 100m causal result                | 39c59b5ca30703643290ab43b3b98e2eeb31379ba6ae5bc98f2e05094fc874b3 |
| C11 100m scientific pass freeze       | 57addcc66b81a7a4f6bb0c2d956138a3839f047c2d151870aba4de10153ce09b |
| 100m collection preregistration       | d9a25af02cdbf19499533d9173e27b3f8c4c8ebe93f0e67b9a4619fc5c27951c |
| 100m parent collector source          | c9100130f17ab27eb2495db634db46763d1b49ed7856594a366fb8c65e4ce830 |
| 100m derived collector                | d0c024de2ca9e4b1fdf033ba44b34d80451a683ace4d6c1a988e4d4cd8423311 |
| 100m collector static derivation lock | d547b2f8ee1974f585a12458ff904385567ce0fb257267f06111c5e07d711160 |

# 16. 当前云端目录、依赖和恢复方式

| **逻辑对象**                 | **当前/登记路径**                                                                                                             | **规则**                                                                 |
|------------------------------|-------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| formal_repo                  | /root/MineSim-Dynamic                                                                                                         | 唯一正式repo。                                                           |
| data_root                    | /root/autodl-tmp                                                                                                              | 大文件/日志/结果。                                                       |
| current path registry        | /root/autodl-tmp/00_MineSim_ACTIVE/current_paths.json                                                                         | 重连先读。                                                               |
| FullMine runtime             | /root/autodl-tmp/fullmine_vector_v2_targeted_runtime                                                                          | 地图runtime。                                                            |
| polygon21 current            | /root/autodl-tmp/fullmine_v4_dual_candidate_v1                                                                                | 正式双车benchmark。                                                      |
| cross-scene current          | /root/autodl-tmp/fullmine_v4_fleet_cross_scene_v1                                                                             | C04/C11/C06/C03当前evidence根。                                          |
| representative MCTS          | /root/autodl-tmp/fullmine_v4_mcts_representative_v1                                                                           | 单车代表性实验。                                                         |
| C03 full collection          | .../fullmine_v4_fleet_cross_scene_v1/c03_value_v2_full_collection_v1                                                          | 135-root冻结数据。                                                       |
| Value V2 model               | /root/autodl-tmp/paper1_value_v2_final_dev_model_v1                                                                           | checkpoint/normalization/model freeze。                                  |
| Value V3 development root    | /root/autodl-tmp/paper1_value_v3_development_only_v1                                                                          | V3 prereg/training/results/C11 coverage 当前 evidence 根；正式 repo 外。 |
| reports                      | /root/autodl-tmp/10_MineSim_REPORTS                                                                                           | 正式备份策略；不是运行输入。                                             |
| archive/quarantine/manifests | 90_MineSim_ARCHIVE / 98_MineSim_QUARANTINE / 99_MineSim_CLEANUP_MANIFEST                                                      | 不可擅动；恢复用manifest。                                               |
| C11 coverage candidates      | /root/autodl-tmp/paper1_value_v3_development_only_v1/c11_coverage_candidates_v1                                               | 60m/100m scenario、manifest、loader/safety/causal smoke 与 runner。      |
| C11 causal smoke runners     | .../c11_coverage_candidates_v1/causal_conflict_smoke_runners_v1                                                               | 60m final inconclusive、100m result/pass freeze；禁止重跑。              |
| 100m derived collector       | /root/autodl-tmp/paper1_value_v3_development_only_v1/cross_scene_fleet_mcts_c11_start100m_seed0_paper1_neural_collector_v1.py | STATIC PASS；当前不得执行。                                              |
| 100m planned collection root | /root/autodl-tmp/paper1_value_v3_development_only_v1/c11_100m_development_collection_v1                                       | 当前必须不存在；只有 execution authorization 后才允许创建。              |
| parent collector package     | /root/autodl-tmp/PAPER1_NEURAL_C11_C06_CURRENT_SEMANTIC_COLLECTOR_V1_UPLOAD.zip                                               | parent source + C11/C06 historical artifacts；SHA 94ec9778…              |

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

| **对象/时间**                     | **可确认事实**                                                                                                              | **边界**                                                                          |
|-----------------------------------|-----------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| 2026-07-26～08-17历史Word         | AI接手文档.zip内包含11份阶段手册/风险清单/技术总览。                                                                        | 历史快照；当前结论需以新证据覆盖。                                                |
| 2026-08-18/21/23综合Word          | 当前会话各有原件与重复副本；均纳入本交付包。                                                                                | 8/24状态以本文为准。                                                              |
| 云端整理说明                      | MineSim_云端项目整理最终文档包.zip含DOCX+MD。                                                                               | 会话材料，完整纳入。                                                              |
| 2026-08-16 cleanup                | 530→121；423 move/isolate；科研文件删除0。                                                                                  | 可逆整理，不释放所有空间。                                                        |
| 2026-08-21 cleanup                | move99/keep3/problem0；restore存在、SHA通过。                                                                               | 之后生成新资产，顶层数量非当前实时值。                                            |
| 当前云端Word精确库存              | 截至本轮仍未执行 AutoDL 全盘 Word live inventory；不能给出云端 Word 精确数量。                                              | 未验证/HOLD；需单独只读 find+SHA inventory。                                      |
| 手动删除某Word                    | 无直接证据。                                                                                                                | 未验证/HOLD。                                                                     |
| codex-env.sh                      | No such file or directory。                                                                                                 | 仅路径缺失；处置未验证。                                                          |
| 本次新文档/包                     | 本次正式晚间更新 Word 在 ChatGPT 工作区生成；是否上传 AutoDL、放到何处及其云端 SHA 尚未发生。                               | 本次交付仅以下载链接为准；不得声称云端已备份。                                    |
| 2026-08-24 V3/C11 新生成 evidence | AutoDL 已真实生成 60m/100m freeze、100m collection prereg、derived collector 与 static derivation lock；关键 SHA 见第15节。 | 均位于 /root/autodl-tmp/paper1_value_v3_development_only_v1；不是正式 repo 源码。 |
| planned collection root           | c11_100m_development_collection_v1 当前不存在，属于预注册/静态 gate 的有意状态。                                            | 目录不存在≠被删除；禁止提前创建。                                                 |
| 当前登录磁盘观测                  | 系统盘 16G/30G（52%）；数据盘 5.3G/50G（11%）。                                                                             | 仅为本轮登录 banner 快照，后续可能变化。                                          |
| ChatGPT Library 文档副本          | 可见 2026-08-24 综合 Word 原件及 (1)/(2) 重复副本；此前 08-18/21/23 也有重复。                                              | Library 存在不等于 AutoDL 云端备份；重复副本是否删除未授权。                      |

删除总结：现有证据仍只支持“2026-08-16 科研文件删除 0”以及后续 move/isolate/archive；不能把 path missing、planned root 不存在、目录变干净、No such file 或 ChatGPT Library 副本变化推断为删除。当前没有新的明确 deletion phase。若要释放空间，必须另开只读 inventory→checksum/equivalence→用户明确授权→删除→post-delete manifest 的独立流程。

# 20. 会话材料与压缩包清单

历史 2026-08-24 综合交付包曾纳入当时可见的 62 个项目文件。此晚间更新继续引用该历史 Manifest，并新增 Value V2/V3/C11 100m 证据；本次只交付更新版 Word，不宣称已重新生成或上传新的 AutoDL 总包。

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

| **对象**                                | **HOLD原因**                                                                                                                                                                             |
|-----------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 100m derived collector evidence binding | 当前真正 blocker：历史 LOADER_RESULT/NOMCTS_RESULT/STATIC_CONFIG/STATIC_READINESS/PROTOCOL_AMENDMENT 尚未分类为 lineage 或 candidate-specific；collection execution authorization 禁止。 |
| 100m development collection execution   | prereg 与 static derivation PASS，但 collection_authorized=False、executed=False；planned output root 必须不存在。                                                                       |
| C11 60m candidate                       | one-time result technical-inconclusive；传播既未证明也未否定；Retry3=False；不得作为科学 PASS/FAIL 或 collection 输入。                                                                  |
| Value V3 candidate readiness            | 固定 9-fold 仅 2/3 scene win；V3_DEVELOPMENT_READY=False；不能接入 MCTS，先补 coverage 后重新固定 LOSO。                                                                                 |
| Production drivability                  | 缺官方 mask / internal exclusions / authoring rule；research/DEV 可用不等于 production-authoritative。                                                                                   |
| Terrain/Z/slope                         | source_z datum 与 slope waypoint 字段语义未获权威验证。                                                                                                                                  |
| V2H / Π_safe / hard pruning             | 未实现、未批准或仍为 observational；不能外推为安全控制规则。                                                                                                                             |
| Map Showcase V3                         | 120 frames 保留；encode/release incomplete；SIGKILL 原因未验证，不能写确定 OOM。                                                                                                         |
| AutoDL Word 实时库存/手动删除           | 未做 live inventory；只确认 cleanup research deletion=0。                                                                                                                                |
| codex-env.sh                            | 登录提示路径不存在；未验证何时/为何缺失，不能推断被删除。                                                                                                                                |

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

证据来源：本附录是历史 62 文件交付包的 Manifest 快照。晚间更新新增的 JSON/PY/终端证据不在该旧 Manifest 中，精确当前状态应以第 12.8～12.13、15、16、19 节及文末快速接手区为准。

# 最终快速接手区（下一位 AI 先读本节）

当前判定只以 Git/源码/SHA/冻结 JSON/终端真实输出为准。不要重新扫描全仓，不要重跑已冻结实验，不要根据文件名猜状态。

| **问题**                | **当前唯一有效答案**                                                                                                                                                                      |
|-------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 项目做到哪里            | Value V2 已关闭；Value V3 固定 9-fold 仅 2/3；C11 100m causal scientific PASS；100m collection prereg + derived collector static PASS；执行仍 HOLD。                                      |
| 当前真正 blocker        | 审计 derived collector 的历史 LOADER_RESULT/NOMCTS_RESULT/STATIC_CONFIG 等 evidence binding：LINEAGE 还是 CANDIDATE_SPECIFIC。                                                            |
| 下一步最小行动          | 仅低资源 read-only evidence binding audit；不修改 derived source、不创建 collection root、不执行 MCTS。                                                                                   |
| 下一步 PASS 标准        | 逐 evidence 对象给出路径、SHA、evidence_pass/控制条件、scenario/manifest/route/physical/timeline coupling，并冻结分类；只有全部可解释后才写 execution authorization。                     |
| 是否开高资源卡          | 否。当前低资源即可。只有 execution authorization 写入、namespace 空、inputs SHA 全 PASS 后才开高卡运行唯一一次 collection。                                                               |
| 正式 repo               | /root/MineSim-Dynamic；HEAD=112d2bd0f3412fc83b13d5587d2b41402d2d0f5e；正式 repo 不保存大日志/结果。                                                                                       |
| 当前 evidence 根        | /root/autodl-tmp/paper1_value_v3_development_only_v1                                                                                                                                      |
| derived collector       | .../cross_scene_fleet_mcts_c11_start100m_seed0_paper1_neural_collector_v1.py；SHA=d0c024de2ca9e4b1fdf033ba44b34d80451a683ace4d6c1a988e4d4cd8423311。                                      |
| planned collection root | .../c11_100m_development_collection_v1；继续工作前必须确认不存在。                                                                                                                        |
| 绝对不能动              | FullMine runtime/semantic/bitmap symlink；90_ARCHIVE/98_QUARANTINE/99_CLEANUP_MANIFEST；C03/C13/60m/100m one-time freezes；Value V2/V3 frozen designs；old paths used by frozen runners。 |
| 60m 状态                | technical-inconclusive，one-time consumed，not scientific FAIL，Retry3=False，禁止 collection。                                                                                           |
| 100m 状态               | NO-MCTS causal PASS；result 39c59b…；scientific pass freeze 57addc…；eligible 但 collection 未授权。                                                                                      |
| 当前文档/删除           | 科研文件删除 0 是唯一确认删除结论；其余均 move/archive/HOLD。AutoDL Word live inventory 未验证；本 Word 需用户下载后自行上传云端并记录 SHA。                                              |

## 继续前必须执行的只读检查

cd /root/MineSim-Dynamic  
source /root/miniconda3/etc/profile.d/conda.sh 2\>/dev/null \|\| true  
conda activate minesim  
export PYTHONPATH=/root/MineSim-Dynamic  
export CUDA_VISIBLE_DEVICES=""  
export PYTHONDONTWRITEBYTECODE=1  
  
git rev-parse HEAD  
git status --short  
cat /sys/fs/cgroup/memory.max  
cat /sys/fs/cgroup/cpu.max  
screen -ls \|\| true  
test ! -e /root/autodl-tmp/paper1_value_v3_development_only_v1/c11_100m_development_collection_v1 && echo COLLECTION_NAMESPACE_UNUSED=PASS  
sha256sum /root/autodl-tmp/paper1_value_v3_development_only_v1/cross_scene_fleet_mcts_c11_start100m_seed0_paper1_neural_collector_v1.py  
sha256sum /root/autodl-tmp/paper1_value_v3_development_only_v1/PAPER1_VALUE_V3_C11_100M_DEVELOPMENT_COLLECTOR_STATIC_DERIVATION_V1.json

## 接手时必须坚持的协作与安全规则

- ChatGPT 负责分析、决策、关键代码与验收设计；用户复制到 AutoDL 执行并返回真实结果。复杂算法、顽固 Bug、关键结论复核或适合云端自主执行的麻烦任务才交 Codex。

- Codex 默认 gpt-5.6-luna medium；只有必要时临时 Terra/Sol，当前最小步骤完成即降级。

- 每次只推进一个最小 blocker；已验证事实不重复、frozen 阶段不重审；输出只保留 PASS/FAIL 与必要字段。

- 能用 Shell/Python 免费确认的 file/process/hash/git/AST/JSON/compile 不调用模型；先完成免费前置再开高资源卡。

- 顺序固定：只读 preflight → static/loader smoke → short closure → full experiment → freeze；one-time 实验必须 START/CAPTURE，失败不得自动重跑。

- 所有可执行代码先 cd /root/MineSim-Dynamic、激活 minesim、设置 PYTHONPATH/CUDA_VISIBLE_DEVICES/PYTHONDONTWRITEBYTECODE。

- 交互顶层禁止裸 exit；失败放入子 shell 或只打印 FAIL。禁止 git reset --hard、git clean -fd、git add .、rm -rf。

- 大文件/长日志/结果统一放 /root/autodl-tmp；正式 repo 只保留必要源码修改。安全、可恢复、可复现优先于目录美观和省几分钟。

## 当前必须核验的文件与 SHA

| **对象**                | **路径**                                                                                                                                                                                         | **SHA / 状态**                                                   |
|-------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------|
| Collection prereg       | /root/autodl-tmp/paper1_value_v3_development_only_v1/PAPER1_VALUE_V3_C11_100M_DEVELOPMENT_COLLECTION_PREREGISTRATION_V1.json                                                                     | d9a25af02cdbf19499533d9173e27b3f8c4c8ebe93f0e67b9a4619fc5c27951c |
| Derived collector       | /root/autodl-tmp/paper1_value_v3_development_only_v1/cross_scene_fleet_mcts_c11_start100m_seed0_paper1_neural_collector_v1.py                                                                    | d0c024de2ca9e4b1fdf033ba44b34d80451a683ace4d6c1a988e4d4cd8423311 |
| Static derivation lock  | /root/autodl-tmp/paper1_value_v3_development_only_v1/PAPER1_VALUE_V3_C11_100M_DEVELOPMENT_COLLECTOR_STATIC_DERIVATION_V1.json                                                                    | d547b2f8ee1974f585a12458ff904385567ce0fb257267f06111c5e07d711160 |
| 100m pass freeze        | /root/autodl-tmp/paper1_value_v3_development_only_v1/c11_coverage_candidates_v1/causal_conflict_smoke_runners_v1/PAPER1_VALUE_V3_C11_100M_CAUSAL_CONFLICT_SMOKE_SCIENTIFIC_PASS_FREEZE_V1.json   | 57addcc66b81a7a4f6bb0c2d956138a3839f047c2d151870aba4de10153ce09b |
| 60m inconclusive freeze | /root/autodl-tmp/paper1_value_v3_development_only_v1/c11_coverage_candidates_v1/causal_conflict_smoke_runners_v1/PAPER1_VALUE_V3_C11_60M_CAUSAL_CONFLICT_SMOKE_FINAL_INCONCLUSIVE_FREEZE_V1.json | 499e73c5dd0ada4182217781616610ecd1c13729c86cb2779658a14908ffa0a1 |
| 100m scenario/manifest  | /root/autodl-tmp/paper1_value_v3_development_only_v1/c11_coverage_candidates_v1/                                                                                                                 | scenario 3d71f2…；manifest b18dd8…                               |

接手结论：下一步不是直接 collection、不是改网络、不是再跑 60m/100m smoke，而是低资源完成 derived collector historical evidence binding audit。
