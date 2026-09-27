| **文档定位** 本文件面向下一位 AI / 工程人员。目标是在不重新扫描整个项目、不重复已冻结实验、不重新询问大量背景的前提下，安全、低成本地从当前节点继续。任何与更晚 AutoDL 终端、Git、SHA 或实际运行输出冲突的旧文档内容自动降级为历史快照。 |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

| **对象/阶段**                  | **状态**             | **当前准确结论**                                                                                                   |
|--------------------------------|----------------------|--------------------------------------------------------------------------------------------------------------------|
| 正式科学基线                   | FROZEN               | HEAD 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e；tag fullmine-vector-v4-runtime-freeze-20260814                      |
| FullMine Vector V4             | FROZEN               | Research/DEV baseline；semantic/bitmap/runtime/planner fixes 已冻结；production-authoritative drivability 仍未证明 |
| Polygon21 Fleet-MCTS           | FROZEN               | NO-MCTS 真物理冲突；Fleet-MCTS 5/5 PASS；无参数重调                                                                |
| Cross-scene C04/C11/C06        | CLOSED WITH NEGATIVE | seed0 full success 2/3；collision avoidance 3/3；C11 安全但 deadlock/progress FAIL                                 |
| Paper-1 SafetyRiskEvaluator V0 | FROZEN               | C04 126-step observational parity；result/log 字节一致；无搜索/reward/pruning 变化                                 |
| Continuous V2R                 | IN PROGRESS          | V1 module smoke PASS；V2 full parity 因 V0 JSONL 污染 FAIL-EVIDENCE；V3 隔离版已生成但云端静态 smoke 尚未执行      |
| Neural-MCTS                    | NOT STARTED          | 正式训练未开始；数据治理完成关键审计；下一步仍是安全特征/合同与 current-semantics 数据链，而非直接开 GPU           |

证据截止：2026-08-18（当前对话可见的上传文件、终端真实输出、Git/SHA/冻结证据与既有整理文档）。

# 目录与阅读顺序

- 0\. 文档使用规则、证据等级与 AI/Codex 归属边界

- 1\. 当前项目 30 秒状态与完整发展主线

- 2\. 运行架构、核心调用链、关键代码目录

- 3\. 阶段一：MineSim 原项目复现与 IDM Baseline

- 4\. 阶段二：蒙特卡洛 / Pure MCTS 接入与单车跑通

- 5\. 阶段三：双车冲突场景、MultiEgoRuntime 与 J117

- 6\. 阶段四：FullMine 新地图接入、Vector V2 → V4 冻结

- 7\. 阶段五：Fleet-MCTS 双车联合规划、多种子与跨场景动态结论

- 8\. 阶段六：原生 MineSim 可视化、视频与汇报中间层

- 9\. 阶段七：云端文件安全整理、目录系统与恢复机制

- 10\. 阶段八：数据治理、论文方法对齐与后续神经网络接入

- 11\. 重要失败/问题/排查/解决方案与永久禁忌

- 12\. 当前有效版本、SUPERSEDED/HOLD/未验证对象

- 13\. 环境、资源、依赖、Git 与文件操作不变式

- 14\. 用户—ChatGPT—Codex 协作规则与成本控制

- 15\. 云端文档生成、归档与删除情况

- 16\. 关键 Commit / Tag / SHA / 冻结证据速查

- 17\. 证据来源索引与冲突处理原则

- 18\. 快速接手区（下一位 AI 必须先读）

# 0. 文档使用规则、证据等级与 AI/Codex 归属边界

| **事实原则** 最新 AutoDL 终端 / Git / SHA / 源码 / 实际运行输出 \> frozen result/manifest/bundle \> 最新交接文档 \> 历史文档 \> 设计计划 \> 模型记忆。缺少直接证据的一律标为“未验证 / HOLD”。 |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

| **等级** | **含义**                                   | **使用规则**                     |
|----------|--------------------------------------------|----------------------------------|
| V-LIVE   | 当前云端 Git、源码、文件、SHA、运行输出    | 最高优先级；每次重连先只读核验   |
| V-FROZEN | result / manifest / SHA / tag / frozen ZIP | 长期锚点；默认不重跑、不覆盖     |
| V-DOC    | 正式 Word、整理说明、历史手册              | 补足演进；若与更晚终端冲突则降级 |
| V-DESIGN | 未来方案、论文适配、网络设计               | 不能写成已完成                   |
| HOLD     | 来源/语义不足或禁止擅动                    | 不得以常识补齐                   |

**AI/Codex 归属边界：**只把日志/旧文档明确标注为 Codex 的工作写成“Codex 完成”。2026-08-17～08-18 的 cross-scene、论文安全旁路、V2R 脚本/结果并没有可靠逐文件 Codex 作者标记，因此本文统一表述为“AI/脚本 + 用户 AutoDL 终端实际执行”。

- 可明确追溯的历史 Codex 事实：2026-08-12 存在源数据完整性审计（Codex/终端协同），随后用户要求停止 Codex、改用普通终端推进。

- 2026-08-13 曾为 Codex 准备严格 P0，只允许抓 exact failure state / 真值检查，禁止先改 mask、调 MCTS 或无边界重跑。

- 2026-08-14 有一次 bounded predicate/debug 验证，记录为 MISMATCHES_BEFORE=0、RANDOM_CASES_CHECKED=20、REAL_STATES_CHECKED=20；完成后即停止，没有启动第二个 Codex 或让其长时间 full builder/benchmark。

- 针对“今天 Codex 做了什么”：当前 2026-08-18 上传证据未单独标注任何新的 Codex 专属执行，因此不虚构归属；若另有未上传的 Codex 会话，应在补充日志后再纳入。

## 0.1 固定状态术语

| **术语**      | **含义**                             |
|---------------|--------------------------------------|
| PASS          | 当前门禁通过                         |
| FROZEN        | 绑定可复核证据，默认不重做           |
| HISTORICAL    | 历史有效但不是当前生产/科学版本      |
| SUPERSEDED    | 被后续版本替代但必须保留 provenance  |
| FAIL-EVIDENCE | 失败本身是有效诊断证据，不能简单删除 |
| INCOMPLETE    | 部分产物完成但未形成正式 release     |
| HOLD          | 禁止擅自推进或结论不足               |
| NOT STARTED   | 尚未正式开始                         |

# 1. 当前项目 30 秒状态与完整发展主线

**一句话定义：**MineSim-Dynamic 是面向露天矿无人矿卡规划的闭环仿真与算法验证工程。项目已经从原 MineSim 的 IDM/replay 复现，推进到 Pure MCTS、双受控车辆 Multi/Fleet MCTS、真实 GIS FullMine Vector V4 Research/DEV Map、Polygon21 物理冲突 benchmark、跨场景动态验证、原生 MineSim 可视化与论文导向的 safety/value-network 前置工作。正式神经网络训练仍未开始。

| **主线阶段**    | **状态**               | **当前最准确结论**                                                                             |
|-----------------|------------------------|------------------------------------------------------------------------------------------------|
| MineSim 复现    | PASS / FROZEN          | Dapai / Jiangtong IDM + replay/closed-loop 基线建立；baseline commit/tag 可回归                |
| MCTS 接入       | PASS / FROZEN          | Pure MCTS 进入真实 MineSim online closed-loop；Dapai/Jiangtong 正式结果与 448 strict expert    |
| 单车跑通        | PASS / FROZEN          | J117 Phase4C 423-step full route；FullMine Representative Pure MCTS 3/3                        |
| 双车冲突构建    | PASS / FROZEN          | J117 NO-MCTS 真重叠 + Pure MCTS 5-seed；Polygon21 构造物理冲突                                 |
| FullMine 新地图 | PASS / FROZEN          | Vector V2 semantic + V4 bitmap/runtime/planner 修复；targeted 7/7 + 旧图回归                   |
| Fleet-MCTS      | PASS + NEGATIVE RESULT | Polygon21 5/5；cross-scene C04/C06 成功、C11 安全但 deadlock，反证 universal success           |
| 原生可视化      | PASS / FROZEN          | Native Video V2 final；FullMine middleware Snapshot/OfflineAdapter/Renderer/Video V0.2 freeze  |
| 云端整理        | PASS / COMPLETE        | Phase2A–2K；顶层约 530→121；423 move/isolate；科研文件删除 0；restore gate PASS                |
| Neural 接入     | PREP / NOT STARTED     | dataset governance + paper compatibility + SafetyRisk V0 + continuous V2R 前置；GPU 训练未开始 |

## 1.1 真实演进时间线

| **日期**       | **阶段**                        | **可复核结果/意义**                                                                                                                                                               |
|----------------|---------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 2026-07-26     | 云端 baseline / AI 操作规范     | 建立 AutoDL 安全交互、Git 恢复与“先读接口再改代码”的基本纪律。                                                                                                                    |
| 2026-07-30～31 | Pure MCTS 闭环接入              | MCTSPlanner 外壳 → 状态/动作/搜索/奖励 → trajectory adapter → Controller/KBM closed-loop；经历确定性/iLQR 等修复。                                                                |
| 2026-08-01～02 | 安全迭代 + 正式 expert          | Jiangtong 几何预测 CV/CTRV、buffer/viability/clearance；commit 94693dc；Dapai199 + Jiangtong249 = 448 strict samples。                                                            |
| 2026-08-03～07 | 五 Planner / Budget             | MCTS/IDM/Frenet/Adapted Maneuver/Simple；budget 50/100/200/300；形成能力边界和接口失败教训。                                                                                      |
| 2026-08-08～10 | 双受控 + J117                   | Dapai dual mechanism；Jiangtong 负筛选；J117 real-GeoJSON pilot 单车423步、双车 NO-MCTS conflict + MCTS 5-seed。                                                                  |
| 2026-08-11～14 | FullMine V1 → Vector V4         | structural / DEV mask / O(1) lookup → Vector V2 semantic → CollisionLookup/planner fixes → V4 bitmap/runtime freeze 112d2bd。                                                     |
| 2026-08-14     | Representative Pure MCTS        | 跨代表区域 3/3 PASS 并冻结；Neural readiness 只审计、不训练。                                                                                                                     |
| 2026-08-15     | Polygon21 Fleet-MCTS            | NO-MCTS 物理重叠；Fleet budget64/depth8 5/5；freeze v2。                                                                                                                          |
| 2026-08-16     | 原生视频 + 云端整理             | Native MineSim Video V2 final；Phase2A–2K safe cleanup；Map Showcase V2 PASS，V3 编码 SIGKILL 未收口。                                                                            |
| 2026-08-17     | Middleware + cross-scene 启动   | Snapshot/OfflineAdapter/Renderer/Video 冻结；旧交接文档当时 cross-scene 还停在 C04 loader float(list)；此状态后来被 8/18 实验覆盖。                                               |
| 2026-08-18     | Cross-scene 收口 + paper safety | C04/C11/C06 dynamic 完成；C11 形成安全死锁负结果；dataset semantic compatibility 审计；Paper-1 SafetyRisk V0 C04 full parity freeze；continuous V2R 推进到 V3 static 待云端执行。 |

# 2. 运行架构、核心调用链、关键代码目录

| **系统边界** 项目没有重写完整 MineSim。MCTS/Fleet-MCTS 主要替换/扩展 Planner 决策层；轨迹仍由 TwoStageController 与 Kinematic Bicycle Model 执行。Scenario、Map、Observation、Controller、Vehicle、History/Metrics 都是科学链的一部分。 |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

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

| **层**               | **当前真实职责 / 关键目录**                                                                      | **接手风险**                                                                |
|----------------------|--------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------|
| Scenario/Environment | devkit/sim_engine/environment_manager/；scenario_manager/；EnvironmentSimulation                 | Scenario schema、location 映射、absolute path 不能猜                        |
| Map                  | devkit/sim_engine/map_manager/；semantic/bitmap loader                                           | semantic identity、bitmap symlink、scale/flip、SHA 不可随意改               |
| Planning             | devkit/sim_engine/planning/planner/；local_planner/                                              | 必须按 AbstractPlanner 真接口；planner 输出轨迹而不是下一帧状态             |
| Pure MCTS            | local_planner/mcts_planner.py + planner/mcts/\*.py                                               | 状态/reference/footprint 语义必须一致；search 与 adapter 故障域分离         |
| Multi/Fleet          | mcts/multi_ego_runtime.py、fleet_state.py、fleet_transition.py、fleet_reward.py、fleet_search.py | A/B 必须同 iteration；受控车必须从 external observation 剔除                |
| Control              | ego_simulation/two_stage_controller.py；ego_motion_controller/                                   | 合法 trajectory 不等于 controller 可实现；A2 是典型                         |
| Vehicle              | ego_simulation/ego_update_model/kinematic_bicycle_model.py                                       | rear axle / geometric center / footprint 不能混用                           |
| Safety               | environment_manager/collision_lookup.py + exact footprint geometry                               | 离散 CollisionLookup 可 false positive；科学冲突判定需 physical truth-check |
| Visualization        | PlanVisualizer2D + SimulationHistory/PlotData + MultiEgoRuntime live B                           | history 在 dual 下主要是 A，不得当作 A+B 完整真值                           |

## 2.1 Pure MCTS 模块索引

| **模块**                             | **作用**                                                                              |
|--------------------------------------|---------------------------------------------------------------------------------------|
| mcts/state.py                        | MCTSState                                                                             |
| mcts/action_space.py                 | BRAKE / DECEL / KEEP / ACCEL 离散动作                                                 |
| mcts/state_builder.py                | MineSim state → MCTSState                                                             |
| mcts/transition_model.py             | 树内轻量近似动力学                                                                    |
| mcts/geometry_transition_model.py    | 几何/footprint/外部预测；历史与当前语义差异是 dataset compatibility 关键              |
| mcts/reward.py                       | progress / speed / safety / comfort / terminal reward                                 |
| mcts/node.py + search.py             | Selection / Expansion / Rollout / Backup                                              |
| mcts/trajectory_adapter.py           | 根动作 → MineSim 可执行轨迹                                                           |
| mcts/diagnostics.py + expert_data.py | 搜索诊断与严格 expert record                                                          |
| local_planner/mcts_planner.py        | MineSim API adapter：PlannerInput / history / map / trajectory；不应塞入网络/搜索细节 |

# 3. 阶段一：MineSim 原项目复现与 IDM Baseline

**目标：**先把原项目在 AutoDL 稳定复现，建立后续 MCTS、地图和 multi-ego 改动的回归锚点。Dapai/Jiangtong 原地图和 IDM/replay 是 production behavior 对照，不能因后续算法推进而删除。

| **对象**        | **冻结值 / 结论**                                            |
|-----------------|--------------------------------------------------------------|
| 正式 repo       | /root/MineSim-Dynamic                                        |
| Conda / Python  | minesim / Python 3.9.25                                      |
| Baseline commit | 2521aa41a69a6e734c04c15a715e9530c8095ac3                     |
| Baseline tag    | idm-replay-autodl-baseline                                   |
| 原地图          | Dapai / Jiangtong；原数据保持回归锚点                        |
| 核心原则        | 先证明原 MineSim 闭环，再替换 Planner；不绕过 Controller/KBM |

## 3.1 复现阶段形成的永久规则

- Planner 返回 future trajectory；Controller 比较当前状态与 trajectory 产生控制量；KBM 再积分成下一帧。不能把 Planner 输出误当“下一位置”。

- 任何 API/配置签名先读源码/真实 YAML；禁止按模型记忆猜 Hydra 参数或 Scenario 字段。

- 终端出现错误时先保留 traceback / log / rc；不要先修改多个模块。

# 4. 阶段二：蒙特卡洛 / Pure MCTS 接入与单车跑通

**目标：**在不重写 MineSim 仿真执行层的前提下，把 MCTS 作为在线 local planner 接入真实 closed-loop；建立可训练的专家搜索记录。

| **里程碑**              | **值**                                                     |
|-------------------------|------------------------------------------------------------|
| 正式 MCTS commit        | 94693dc799fe5f325a75e8fc6d7d5e88764b4799                   |
| Tag                     | mcts-expert-dataset-v1-20260802                            |
| Dapai strict expert     | 199                                                        |
| Jiangtong strict expert | 249                                                        |
| 合计                    | 448                                                        |
| 历史 search config      | iterations=300；seed=42；target_speed=10.5 m/s             |
| 动作映射                | BRAKE=0 (-3.0), DECEL=1 (-1.5), KEEP=2 (0), ACCEL=3 (+1.0) |

| **实验设计**           | **输入**                                                             | **输出 / PASS 标准**                                                                                                   |
|------------------------|----------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------|
| Single-ego online MCTS | Scenario + current ego/obstacles + map/refline                       | 每帧 root search → action → trajectory adapter → Controller/KBM；无 exception、goal/safety/时间线按正式 evaluator 验收 |
| Expert logging         | root visits/Q/immediate reward/predicted clearance + state/obstacles | strict schema v1；每个 decision record 可追溯到 scenario/source/result                                                 |
| Budget ablation        | 只改变 search budget 50/100/200/300                                  | 不能把 budget 对任务完成度的影响混入别的算法参数                                                                       |

## 4.1 五 Planner 历史对照的正确解释

| **Planner**      | **已观察结果**                           | **严谨边界**                                    |
|------------------|------------------------------------------|-------------------------------------------------|
| MCTS             | 2/2 safe+goal                            | 只代表 Dapai/Jiangtong 正式场景，不外推全局最优 |
| IDM              | 1/2                                      | baseline 对照                                   |
| Online Frenet    | 0/2；0 collision/0 boundary 但任务未完成 | 不能只看碰撞率                                  |
| Adapted Maneuver | 0/2；67 collision frames                 | 评价当前适配版本，不等同原算法总体              |
| Simple           | 0/2；90 boundary frames                  | 能力下限参考，不是公平主比较                    |

| **关键失败：Frenet step 150** 真实根因是 Planner→MineSim trajectory 重采样接口越界：\_get_planned_trajectory() 追加索引 79，而 best_traj 长度恰为 79、有效最大索引 78。解决为外部安全重采样/适配；随后 Dapai 199、Jiangtong 249 完整跑通。以后 Planner FAIL 必须先区分“搜索失败”与“trajectory adapter/interface 失败”。 |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# 5. 阶段三：双车冲突场景、MultiEgoRuntime 与 J117

**目标：**第二辆车不再只是 replay obstacle，而是让 A/B 两辆车都成为受控对象，在同一 simulation iteration 内联合传播、联合决策，并建立“无联合规划会发生真实物理冲突”的 causal benchmark。

| **组件**                                   | **已实现语义**                                                                              |
|--------------------------------------------|---------------------------------------------------------------------------------------------|
| ControlledVehicleRuntime / MultiEgoRuntime | 按 token A/B 管理 current/next iteration，接收两条 trajectory；B 权威 live state 在 runtime |
| SimulationSetup.set_multi_ego_runtime()    | 把 multi-ego runtime 挂到 production simulation setup                                       |
| EnvironmentSimulation.propagate() dual     | trajectories 必须恰好含 A/B，再同步更新 MultiEgoRuntime                                     |
| Observation filter/partition               | 从 tracked observation 中剔除受控 A/B，防止重复 external actor / 假碰撞                     |
| FleetState                                 | A/B 两个 MCTSState 的联合表示                                                               |
| FleetTransitionModel                       | 4×4=16 joint longitudinal actions；几何联合传播                                             |
| FleetRewardModel                           | per-vehicle reward + continuous clearance soft penalty + hard collision/safety              |
| RouteGeometryCache                         | rear-axle route_s → geometric-center footprint；避免参考点混用                              |

| **场景筛选教训** 空间路线相交 ≠ 具有联合决策价值。Jiangtong Traj26 虽空间相交，但自然 ETA 差约 9.496 s；commit 94794c963f9c3eaf1873b275df6d319ca2636817 / tag jiangtong-v22-benchmark-screening-20260809 封存为负筛选。不能为了“凑场景”把它重新包装成天然冲突 benchmark。 |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

## 5.1 J117 real-GeoJSON pilot：先单车，再双车

| **实验**        | **结果 / 冻结**                                                                                                                                                                                    |
|-----------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Phase4C 单车    | commit ec1c958735b0ee76201284faacb46fccc75c7f6c；tag j117-phase4c-single-ego-closed-loop-20260810；423 steps / 42.3 s；route≈398.998 m；min clearance≈1.599 m；goal reached；全程 drivable；无异常 |
| Phase5 dual     | commit da4105b836dbbd3e702ee25fbb364109bc4e2596；tag j117-phase5-dual-ego-pure-mcts-20260810                                                                                                       |
| NO-MCTS aligned | crossing gap≈0.00070 s；min clearance=0；真实几何重叠                                                                                                                                              |
| Pure MCTS seed0 | crossing gap≈1.561 s；1 ms swept min clearance≈0.594 m；无碰撞                                                                                                                                     |
| 5-seed          | 5/5 benchmark + swept safety PASS；不重调已冻结参数                                                                                                                                                |

- Dapai A-B-only 的价值：证明 multi-ego runtime / joint search 机制可以运行；但 full scenario 有 external object-1 confound，因此不是后续唯一 benchmark。

- 双车受控车辆若没有从 external observation 过滤，会同时以“controlled + external”出现，产生 duplicate actor / 假碰撞。这是以后不得重复的接口错误。

# 6. 阶段四：FullMine 新地图接入、Vector V2 → V4 冻结

**目标：**从真实 FullMine GeoJSON 建立可由 production MineSim Map API、Planner、Controller 和 multi-ego runtime 使用的 Research/DEV 地图；严格区分“科研可复现 baseline”与“官方 production-authoritative drivability”。

| **里程碑**               | **Commit / SHA / 结论**                                                                                           |
|--------------------------|-------------------------------------------------------------------------------------------------------------------|
| Semantic lookup O(1)     | 32fb42920d8cc404b37cd25dc47cbc6fbde4d9f4；将 400k node 上重复线性查找改为已有 token2ind，解决 initialize 性能瓶颈 |
| FullMine V1 registration | d81c57154e4e5d0b4df1251cf565d9aacffaa026；tag fullmine-dev-runtime-pass-20260811                                  |
| Current V4 freeze        | 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e；tag fullmine-vector-v4-runtime-freeze-20260814                          |
| Semantic runtime SHA     | b85a3d8b28f2252ecb5bda179d514573f6333079def838cd048566f556d95cd0                                                  |
| Bitmap runtime SHA       | 51abcd5a86e5c510204a5dacc873691506d721f98982ab7f98585d4e0f7efdd0                                                  |
| CollisionLookup SHA      | 10c1d1339e742ca893fedb4aa51402addfba82e16e08f68339ea35d35ba3043b                                                  |
| IDM planner final SHA    | 541ec74985d06322656e66c48abb382030d679171341408575d936e0a069e75e                                                  |

- “V4”主要是 bitmap/runtime/planner 冻结版本；semantic 主体仍是 Vector V2：100 effective roads、553 reference paths、raw lane Z 与 8 repair provenance。不要把 V4 误写成 semantic 又重做两版。

- raw elevation 已保存，但 source_z_datum_verified=false；slope waypoint\[4\]=0 的语义未验证。任何 terrain/slope 风险模型当前 HOLD。

- FullMine V4 是科研/算法 Research/DEV baseline；production-authoritative drivability NOT PROVEN。除非得到官方 mask / drivable surface / internal exclusions / authoring rule，不允许宣称官方生产地图。

## 6.1 Bitmap / runtime 演进与不可重复做法

| **对象**        | **事实**                                              | **永久规则**                                  |
|-----------------|-------------------------------------------------------|-----------------------------------------------|
| P0 baseline     | immutable                                             | 所有 candidate 新目录，禁止原地覆盖           |
| candidate v1/v2 | additive patch；v1 +112 px；v2 cumulative +118 px     | 每版绑定 SHA，不能为“看起来通”随手补像素      |
| V3              | actual shadow trajectory 驱动，+724 px                | 必须由真实执行轨迹/footprint 证据支撑         |
| V4              | D-only +3 px；0 remove；继承 v3 strict + C/D/E direct | final bitmap frozen；不要继续 patch frozen V4 |

| **A1 endpoint** 末端异常来自 virtual lead geometry 约 4.5 m；修复只作用于 virtual endpoint（length_rear=0.0），没有篡改地图/goal。 |
|------------------------------------------------------------------------------------------------------------------------------------|

| **A2 planner blocker** 早期 leading/occupancy 假设被排除；最终根因是高曲率段 steering-rate infeasibility。修复为 steering-rate-aware local speed cap（0.26 rad/s × 80% = 0.208）+ backward braking envelope，使用 IDM decel_max。A1/A2/B1/B2 shadows 最终全到达。 |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

- GlobalRoutePathPlanner BFS target_depth=5 的限制通过 depth-safe targeted scenarios 绕开；没有为 FullMine 改全局 BFS 语义。

- 最终 targeted 7/7 + 旧 Jiangtong 回归 PASS 后才 commit/tag；已冻结，无需再跑“为了安心”的全套 map experiment。

## 6.2 FullMine Representative Pure MCTS

| **对象**                | **状态 / SHA**                                                   |
|-------------------------|------------------------------------------------------------------|
| Representative Coverage | FROZEN；跨代表区域覆盖门控完成                                   |
| Pure MCTS 3/3           | PASS / FROZEN                                                    |
| Summary SHA             | 742d0716a00364a625e01b27c693134488211c8989e4996b072739c3a500d056 |
| Freeze SHA              | 322e90d6995c410597d01925de6d77f1fd91ddb8c4c73a25c3e87446d37ac1fa |

# 7. 阶段五：Fleet-MCTS 双车联合规划、多种子与跨场景动态结论

## 7.1 Polygon21：当前最干净的冻结冲突 benchmark

| **证据对象**       | **SHA / 结果**                                                   |
|--------------------|------------------------------------------------------------------|
| Scenario           | 362eff18c7ccc88ea8dfaf083a517603566516943690d5cbe76bd1a97afc89e1 |
| Scenario manifest  | 0bde6bb1e869c3cf583947203dd41a8fc364f0a2a8130617baebd0b1e6cbad2e |
| NO-MCTS result     | 060880c8edc851e05606871cb647058d091ce8737f952b9864cc94e9d6fcfd13 |
| Fleet seed0 result | 2eeb28e1fcb1c48d826c387853ec4f9a8a1acf07c9d7e7d1c067701bd4a1398f |
| Fleet freeze v2    | b89d290c9cb06d1efb99688ee27b23898ab81d11e36023832477dc2fc834364b |

| **指标**         | **NO-MCTS**                                            | **Fleet seed0**                            |
|------------------|--------------------------------------------------------|--------------------------------------------|
| 策略             | 固定 4.5 m/s；无 acceleration/waiting/artificial delay | Fleet-MCTS；budget=64, depth=8             |
| duration / steps | 约 crossing benchmark 全程                             | 15.1 s / 151                               |
| crossing time    | A/B≈11.11111 s；gap≈5.43e-7 s                          | A=7.3198895；B=12.5564995；gap=5.2366100 s |
| 物理冲突         | first overlap 9.6 s；max overlap≈23.2148105 m² @10.7s  | no overlap                                 |
| clearance        | min center≈0.296334 m；footprint overlap               | min footprint clearance=2.065002410 m      |
| 验收             | 证明无联合规划真实冲突                                 | timeline/speed/NaN/safety/goal gates PASS  |

- 5-seed：5/5 PASS；crossing gap min/mean/max = 3.437992686 / 7.473227084 / 14.402843799 s；minimum clearance across seeds = 1.292505388 m；first-to-cross A:3, B:2；parameter retuning=False。

- 第一次 freeze v1 的 FAIL = HARNESS_STATIC_SUMMARY_SCHEMA_MISMATCH，属于 harness schema 错误；正确 freeze v2 才是正式锚点。v1 必须保留 provenance。

## 7.2 Cross-scene C04/C11/C06：动态线已收口

| **覆盖旧文档** 2026-08-17 旧 handover 写“C04 real-loader float(list) blocker”。该状态已被 2026-08-18 的真实 loader/NO-MCTS/Fleet 运行覆盖。下一位 AI 不得从旧 blocker 重新开始。 |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

| **场景** | **Loader**                                                                 | **NO-MCTS causal conflict**                                                                                | **Fleet-MCTS**                                                                                                           | **正式结论**                                              |
|----------|----------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------|
| C04      | PASS；SHA 463857eeaff2985402b01107d2cd3ef84d21b44c762ff6aaa5a7b10032096c96 | PASS；SHA 0c806c2398047db7b4780147c4f959f92ece028d779fa286510052c0d0c2af37；真实 overlap                   | seed0 SHA 47e3ff50997d6ea095fce0ea0532ca9c01ace31abdc4646980f3b92b09129ca0；seeds0–4 全 PASS                             | 成功 transfer                                             |
| C11      | PASS；SHA dae7dca77b4ccb30427e2c1db239359abf7b08cc8714288bb5c9d643fd1394f0 | PASS after horizon fix；SHA c5bd459c1e936c089237f33b189b5b8d9d072f7ceab14e0d305d01a4642fa0e7；真实 overlap | seed0 SHA 47a6d570f65953e7dea35f46eb9f8ac63975c1e9e96402f6753f3f41e839547e；no overlap but completed_post_conflict=False | 科学 FAIL：安全但 deadlock/progress failure；禁止调参抹掉 |
| C06      | PASS；SHA 3581e7ef6b62645d60999679f954b8b2ef3da7eecc445c3941c4af0a5ea9ed90 | PASS；SHA db78f35b57ad897b50386698ddf488ab7b30343cf452ae61a9c86ab901c2f2fd；真实 overlap                   | seed0 PASS；SHA 0cbec940ce6581da1669fb06f49d091267f2365c8909c0cacafe393693d3df22                                         | 成功 transfer                                             |

| **C04 seed0 关键数值**  | **值**                                   |
|-------------------------|------------------------------------------|
| duration / steps        | 12.6 s / 126                             |
| cross A / B             | 8.710389610389733 / 10.898456179025821 s |
| gap                     | 2.1880665686360885 s                     |
| min footprint clearance | 1.9653585393773396 m                     |
| overlap                 | False                                    |
| 5-seed min clearance    | 1.628420999 m                            |

| **C11 seed0 关键数值** | **值 / 解释**                                                                                 |
|------------------------|-----------------------------------------------------------------------------------------------|
| duration / steps       | 89.0 s / 890                                                                                  |
| collision              | False；collision_avoided=True                                                                 |
| min clearance          | 2.94145587 m                                                                                  |
| progress               | completed_post_conflict=False                                                                 |
| 结论                   | 安全规避碰撞，但长期无法完成冲突后进度；是后续 cooperation/deadlock/value guidance 的真实动机 |

| **C06 seed0 关键数值** | **值**        |
|------------------------|---------------|
| duration / steps       | 14.6 s / 146  |
| crossing gap           | 1.739764374 s |
| min clearance          | 2.0230128 m   |
| overlap                | False         |

**跨场景最终统计口径：**balanced seed0 full benchmark success = 2/3（C04、C06），collision avoidance = 3/3。不能把 7 个 Fleet runs 简单池化，因为 C04 有 5 seeds、C11/C06 只有 seed0，seed allocation 不平衡。C11 已反证“冻结 Fleet-MCTS 在所有场景 universal success”。

- C04 历史 loader float(list) 已解决；当前证据只能确认后续 runner 做了一元素 list/array 归一化并通过，原始失败表达式的 exact source line 未在现存提取证据中完整保留，因此本文不猜更细根因。

- C04 NO-MCTS 曾出现 NameError: MAX_STEPS，属于 harness 常量错误，修复后 causal conflict 证据 PASS。

- C11 NO-MCTS 初始 200-step 仅因 completed_post_conflict=false 判 FAIL；将 horizon 延至 21.2 s / 212 后 PASS。没有改变冲突物理或 Fleet 参数。

# 8. 阶段六：原生 MineSim 可视化、视频与汇报中间层

**固定原则：**汇报材料必须是科研证据可视化，来源于 frozen semantic/bitmap、真实 scenario/runtime state 和 MineSim 原生可视化链；禁止生成式道路、截图描线、坐标猜测或手工改科学轨迹。

## 8.1 双车原生可视化的状态真值

| **最关键状态问题** EnvironmentSimulation.history 在 dual mode 主要保留 A 的 ego/history trajectory；受控 B 的权威状态由 MultiEgoRuntime 管理。不能把 SimulationHistory 当 A+B 完整真值。Native V2 在每次 propagate 前读取 runtime.state_for("A") / state_for("B")，A 与原生 history 同帧对齐并验证 pose error≤1e-8，B 用同 iteration live state 叠加。没有 route_s 插值、CSV 坐标重建或像素反推。 |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

| **版本**        | **真实问题/结果**                                                                                                                                   | **状态**                                                                     |
|-----------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------|
| Native Video V1 | NO-MCTS raw dimensions = (1545, 3666)，布局异常；科学链可跑但不满足正式汇报                                                                         | SUPERSEDED；保留历史证据                                                     |
| Native Video V2 | NO-MCTS/Fleet raw = (1545,1073)；10 fps；NO-MCTS 145 frames；Fleet151；side-by-side145；collision frames96–118；peak overlap frame107               | FINAL / PASS                                                                 |
| V2 release      | /root/autodl-tmp/Polygon21_Native_MineSim_Report_Video_v2_20260816_161259.zip；SHA f695ba22ecd61c4a643e8ffecac483bc218de9153f95f88b4e0e3006bca03d58 | NATIVE_VIDEO_QUALITY_GATE=PASS；POLYGON21_NATIVE_MINE_SIM_VIDEO_RELEASE=PASS |

- 关于“V1/V2 打包错误”的严谨口径：现有可复核证据明确支持的是 V1 尺寸/布局失败与 V2 重新形成正式 release、绑定 ZIP SHA/帧数/ffprobe quality gate。没有足够直接证据支持另一个更具体的“ZIP 打包 exception”，因此不得凭记忆补写。

## 8.2 FullMine Map Showcase 与可视化中间层

| **对象**              | **问题/结果**                                                                                                                                                                          | **状态**                                  |
|-----------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------|
| Map Showcase V1       | 错误假设 semantic 顶层是 GeoJSON FeatureCollection；真实 MineSim semantic 是 custom dict；脚本在 SHA/schema gate 主动停止                                                              | FAILED DESIGN；正确失败，不猜 schema      |
| Map Showcase V2       | 读取真实 custom semantic；553 reference_path、402 borderline；Polygon21 真几何；3×4K；1080p/15fps/120 frames；ZIP SHA 9f78f357eecfc25ea543d163e8d472dc06abeb1fff3215ed30577267750d1e14 | PASS；历史稳定全局展示基线                |
| Map Showcase V3       | 120/120 frames 已渲染；ffmpeg libx264 SIGKILL:9；未形成 final release                                                                                                                  | INCOMPLETE；不能把 SIGKILL 猜成已证实 OOM |
| SimulationSnapshot V0 | 离线 dual replay 快照；科学状态/几何分离                                                                                                                                               | FROZEN                                    |
| OfflineAdapter V0     | 把 frozen experiment 转为 snapshot                                                                                                                                                     | FROZEN                                    |
| Renderer V0.1         | 只改视觉 hierarchy/crop/font/legend/line weight；三张 3840×2160；四 Gate PASS                                                                                                          | FROZEN                                    |
| Video V0.2            | target-anchored camera 修复 mid-pan blank；正式 middleware video freeze                                                                                                                | FROZEN                                    |

- Renderer V0 的 conflict XY 不直接存在：冻结 manifest 给的是 conflict_route_s；正确做法是用真实 semantic reference_path.waypoints + exact route station 求冲突点，禁止 hardcode。

- Recovery 曾因 OUT 环境变量未透传 KeyError；以后 wrapper 先做 required env gate。

- Polygon21 raw link_node_tokens 为 529 unique；绘图闭合重复第一个真实 node 后是 530 plotting coordinates。不能把 529/530 当数据缺失。

- Renderer V0 自动 gate 可过但 human visual FAIL；V0.1 只改 visual hierarchy，scientific constant patch count=0。科学/几何/技术/人工视觉四门必须全部过才 freeze。

# 9. 阶段七：云端文件安全整理、目录系统与恢复机制

| **整理最终结论** Phase2A–2K COMPLETE / PASS。/root/autodl-tmp 顶层约 530 → 121；423 次 move/isolate；科研文件删除 0；HEAD/SHA/symlink/compile/restore final health PASS。整理是“可逆移动/隔离”，不是 rm 清磁盘；archive/quarantine 仍占空间。 |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

| **目录**                                     | **用途 / 规则**                                                                               |
|----------------------------------------------|-----------------------------------------------------------------------------------------------|
| /root/autodl-tmp/00_MineSim_ACTIVE           | current_paths.json / env / 当前快捷软链接 / organization_tools                                |
| /root/autodl-tmp/10_MineSim_REPORTS          | 汇报/发布备份；不作为科学运行输入                                                             |
| /root/autodl-tmp/90_MineSim_ARCHIVE          | 可恢复历史归档：legacy planner、single MCTS、J117、FullMine dev、superseded media、DR/bundles |
| /root/autodl-tmp/98_MineSim_QUARANTINE       | 隔离但未授权删除；约 315.76MB（8/16 closeout 证据）；必须另行批准                             |
| /root/autodl-tmp/99_MineSim_CLEANUP_MANIFEST | Phase1–2K audit、move plan、fingerprint、health、restore provenance                           |
| CURRENT/HOLD 原路径                          | 为 frozen runner 绝对路径/软链接兼容保留；不强制搬入组织目录                                  |

| **逻辑对象**            | **当前登记路径**                                                      |
|-------------------------|-----------------------------------------------------------------------|
| formal_repo             | /root/MineSim-Dynamic                                                 |
| polygon21_current       | /root/autodl-tmp/fullmine_v4_dual_candidate_v1                        |
| cross_scene_current     | /root/autodl-tmp/fullmine_v4_fleet_cross_scene_v1                     |
| representative_mcts     | /root/autodl-tmp/fullmine_v4_mcts_representative_v1                   |
| representative_coverage | /root/autodl-tmp/fullmine_v4_representative_coverage_v1               |
| production_truth_gap    | /root/autodl-tmp/fullmine_v4_production_truth_gap_v1                  |
| runtime_current         | /root/autodl-tmp/fullmine_vector_v2_targeted_runtime                  |
| semantic_source_current | /root/autodl-tmp/new_map_fullmine_vector_v2_dev                       |
| bitmap_source_current   | /root/autodl-tmp/fullmine_vector_v4_d_current_planner_patch_candidate |
| formal_mcts_results     | /root/autodl-tmp/mcts_results                                         |
| idm_baseline_backup     | /root/autodl-tmp/minesim_idm_baseline_backup                          |
| archive_root            | /root/autodl-tmp/90_MineSim_ARCHIVE                                   |
| quarantine_root         | /root/autodl-tmp/98_MineSim_QUARANTINE                                |
| cleanup_manifest_root   | /root/autodl-tmp/99_MineSim_CLEANUP_MANIFEST                          |

## 9.1 两条 runtime 关键软链接：绝对不能随意搬

| **Runtime entry**                                                                                                        | **必须解析到**                                                                                                             |
|--------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------|
| /root/autodl-tmp/fullmine_vector_v2_targeted_runtime/maps/semantic_map/geojson_full_mine_vector_v2_dev_semantic_map.json | /root/autodl-tmp/new_map_fullmine_vector_v2_dev/maps/semantic_map/geojson_full_mine_vector_v2_dev_semantic_map.json        |
| /root/autodl-tmp/fullmine_vector_v2_targeted_runtime/maps/bitmap/geojson_full_mine_vector_v2_dev_bitmap_mask.png         | /root/autodl-tmp/fullmine_vector_v4_d_current_planner_patch_candidate/bitmap/geojson_full_mine_vector_v2_dev_only_mask.png |

- 绝对路径依赖的 frozen runner 优先“恢复历史路径/软链接”，不要直接改 frozen runner。

- AST 环境变量审计必须区分 os.environ 的 Load 与 Store；内部脚本自己设置的变量不能误报为外部依赖。历史依赖包括 SEM/BREF/CLASS_FILE/MAP_ROOT/DATA_ROOT 等，实际 runner 以源码 gate 为准。

## 9.2 Restore 入口与原则

| **Phase** | **Restore script**                                                                                |
|-----------|---------------------------------------------------------------------------------------------------|
| 2A        | /root/autodl-tmp/99_MineSim_CLEANUP_MANIFEST/phase2a_safe_move_20260816_165421/RESTORE_PHASE2A.sh |
| 2B        | .../phase2b_safe_quarantine_20260816_170221/RESTORE_PHASE2B.sh                                    |
| 2C        | .../phase2c_safe_map_archive_20260816_170828/RESTORE_PHASE2C.sh                                   |
| 2F        | .../phase2f_safe_housekeeping_20260816_172708/RESTORE_PHASE2F.sh                                  |
| 2I        | .../phase2i_safe_large_archive_20260816_174051/RESTORE_PHASE2I.sh                                 |
| 2J        | .../phase2j_final_safe_archive_20260816_174626/RESTORE_PHASE2J.sh                                 |

- 恢复前先确认原路径没有新的同名对象；按 manifest/RESTORE 脚本逆向恢复；恢复后复核 HEAD/status、关键 SHA、runtime symlink、py_compile。

- \`/root/autodl-tmp/MineSim-Dynamic\` 是约 203.75MB 的独立脏历史 workspace，HOLD；不是正式 repo 的简单副本。

- \`?? ^C\` 是历史未跟踪异常名；当前规则是保留，不为“目录漂亮”执行 git clean。

# 10. 阶段八：数据治理、论文方法对齐与后续神经网络接入

| **当前真正状态** Neural-MCTS 正式训练 NOT STARTED。当前路线已经从“直接收集数据训练”修正为：先建立跨版本语义兼容的数据合同，再按照参考论文做 Safety/Risk observable → safe-node filter → current-semantics recollection → Value Network → value-guided MCTS；C11 deadlock 是 cooperation/progress 模块的真实动机。 |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

## 10.1 Expert 数据盘点与语义兼容性

| **来源**                       | **原始数量**                 | **当前可进入 first Value target pool？** | **原因**                                                     |
|--------------------------------|------------------------------|------------------------------------------|--------------------------------------------------------------|
| Historical Dapai               | 199                          | HOLD / legacy evidence                   | 94693dc 旧 producer 语义                                     |
| Historical Jiangtong           | 249                          | HOLD / legacy evidence                   | 同上；合计448                                                |
| FullMine candidate-0002        | 182                          | 候选 current-semantic                    | strict native expert；obstacles=\[\]                         |
| FullMine candidate-0010        | 300 raw → goal 前/到 goal 84 | 84 候选                                  | formal goal step83；84–299 共216条 post-goal 必须截断        |
| FullMine recovery-0005         | 186                          | 候选 current-semantic                    | strict native expert；obstacles=\[\]                         |
| FullMine current non-post-goal | 452                          | 候选                                     | 182+84+186                                                   |
| Historical 448 + FullMine452   | 900 source records           | 不能直接混成同一 label pool              | schema 同、但 geometry/state reference producer 语义不完全同 |
| Cross-scene Fleet records      | evaluation logs              | NO                                       | 不是 single-ego strict expert schema；不得强行转             |

- sample UID duplicate groups = 0（当前盘点）。

- FullMine representative 452 的 obstacles=\[\]，只覆盖 single-ego new-map distribution，不代表 interaction states。

- Historical 448 与 current FullMine schema/action/reward/target10.5/iterations300/seed42 表面一致，但 geometry_transition_model.py 与 current mcts_planner.py 的 rear-axle/geometric-center producer wiring 已变化。因此旧 Q/visits/value label 不能假定与当前语义同质。

- 正式 split 必须按 scenario/episode 分组，绝不随机逐行 split；先 goal-truncate、dedupe、剔除 smoke/post-goal，并为每条记录绑定 source/scenario/episode/result/freeze SHA。

- current-semantics recollection preflight 已 PASS；Dapai 5-step、Jiangtong 5-step smoke 已 PASS；full recollection 暂停，等待 paper-guided safety/data contract 固化。

## 10.2 参考论文方法与项目适配边界

| **论文**                                                                                                                                                | **可吸收方法**                                                                                                                                        | **当前 HOLD / 不照抄**                                                                                        |
|---------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------|
| Safety-Critical Multi-Agent MCTS for Mixed Traffic Coordination at Unsignalized Intersections                                                           | centralized/joint state-action；V2V/V2H/V2R safety assessment；safe node pruning；multi-objective reward；hybrid rollout with learned value predictor | 不直接复制 paper d_min、reward weights、alpha、network size；V2H 尚未实现；当前 Fleet 没有显式 Π_safe         |
| Risk-aware unsignalized intersection management in unstructured mixed-traffic environment: a real-time hierarchical safety evaluation method (TRC 2026) | 风险评估思想：dynamic spatiotemporal field、车辆/边界/人类不确定性等；高层 passing order 的研究参考                                                   | passing-order tree、RA-MVSFM、lane-free、OCP、人类 sigma、terrain risk 当前 HOLD；FullMine Z/terrain 语义不足 |

- Paper-method decision bundle：PAPER_METHOD_COMPATIBILITY_DECISION_V1.zip；SHA 2c2f85767b60e139bd9d6b56a6b24d7b3a0afd95c5ca802b81ad882acb67cb41。

- 适配顺序：1) explicit Safety/Risk evaluator → 2) safe-node filter → 3) dataset contract → 4) current-semantics recollection → 5) Value Network → 6) value-guided rollout → 7) cooperation/deadlock handling → 8) tree reuse → 9) optional Policy+Value/PUCT。

## 10.3 SafetyRiskEvaluator V0：observational parity 已冻结

| **对象**         | **结果**                                                                                                                                   |
|------------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| 设计             | diagnostic-only；不改变 behavior/reward/search/tree pruning；V2V=现有 swept geometry；V2R=真实 local bitmap footprint；V2H=NOT_IMPLEMENTED |
| C04 full parity  | 126 records；authoritative Fleet result/log 字节级一致；route/direct V2R violation=0；mismatch=0；internal collision transitions=0         |
| V0 swept min V2V | 2.038038141194 m（route-geometry swept definition；不要求等于 benchmark endpoint footprint clearance）                                     |
| Freeze bundle    | PAPER1_V0_OBSERVATIONAL_FREEZE_V1.zip；SHA 714698023347899f2b3f52e13965d6507eac7c325ad681ee48167b266521460d                                |
| 边界             | paper1_safe_node_decision_available=False；连续 d_v2r 尚未由 V0 提供；不批准 Π_safe                                                        |

## 10.4 Continuous V2R：当前停点

| **版本/门禁**           | **真实结果**                                                                                                                            | **状态**                                                                  |
|-------------------------|-----------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------|
| V2R preflight           | scipy EDT 可用；10 px/m=0.1m/pixel；synthetic max abs error≈0.1m；C04 float32 3496×3496 field≈46.62MiB                                  | PASS                                                                      |
| DistanceField V1 module | 5 unittest PASS；numeric PASS；no paper parameter copy；结果 ZIP SHA 1dbd9c5a7b03fb9379f2cd9ea613c1e9cabf426d5b25e54a4a4949ac2e84be0d   | PASS                                                                      |
| Verifier marker         | final PASS echo 在 ZIP 打包后且未 tee 入 console，后验 verifier 报 MISSING_PASS_MARKERS                                                 | FALSE INCOMPLETE；不是算法失败                                            |
| Sidecar V1              | V1 record block 插入已打开的 v0_records.append 内，line≈1694 SyntaxError                                                                | SUPERSEDED；instrumentation generator bug                                 |
| Sidecar V2 static       | insertion-only / py_compile / science boundary / repo unchanged                                                                         | PASS                                                                      |
| V2 real 3-step          | field 3496×3496、48,888,064 bytes；A/B actual min 1.5m；no overlap / mismatch                                                           | PASS                                                                      |
| V2 full 126             | Fleet result/log exact parity；V0 summary exact；V1 126 valid；但 V0 JSONL SHA changed because V1 nested fields 写入 V0 direct_boundary | FAIL-EVIDENCE：diagnostic serialization contamination，非 science failure |
| Sidecar V3              | 改为独立 v1_direct_boundary；本地 LOCAL_SYNTAX_COMPILE/INSERTION_ONLY/V0_SERIALIZATION_ISOLATION 均 PASS                                | PREPARED；云端 static smoke 尚未运行                                      |

| **V2 full 126 的连续距离（仅诊断，未冻结阈值）** | **A actual** | **B actual** | **A route** | **B route** |
|--------------------------------------------------|--------------|--------------|-------------|-------------|
| min (m)                                          | 0.565685451  | 0.223606795  | 0.583095193 | 0.223606795 |
| p05                                              | 0.632455528  | 0.370416358  | 0.679892004 | 0.400000006 |
| median                                           | 1.417740285  | 1.481544554  | 1.421267033 | 1.476482272 |
| max                                              | 1.523154616  | 1.640121937  | 1.523154616 | 1.615549445 |

| **禁止误用** 这些距离来自 V2 full run 的诊断分布；因为 V2 存在 V0 JSONL serialization contamination，它们只能作 debugging/evidence，不能据此直接选 d_min。当前没有 paper d_min copy、没有 empirical correction、没有 Π_safe。 |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

| **当前 V3 文件**                                          | **SHA / 状态**                                                   |
|-----------------------------------------------------------|------------------------------------------------------------------|
| C04_PAPER1_V2R_DISTANCE_V1_SIDECAR_SOURCE_V3.zip          | 276639ed81bf00317bccde93bec9df82e84d675519cf24f6cb665c8dfe1e33ad |
| instrumented sidecar                                      | 5289fe017294a5014ad3683076068297d38279c77a839dcd28a4722bb0f5e6bf |
| RUN_C04_PAPER1_V2R_DISTANCE_V1_SIDECAR_STATIC_SMOKE_V3.sh | bbed06e0e2836325d0f8ba6a26dafb06b85f359a038083c1a7c9b48e7f531575 |
| 当前云端执行状态                                          | NOT RUN / 未验证；这是下一步最小动作                             |

# 11. 重要失败/问题/排查/解决方案与永久禁忌

| **故障域**                | **现象**                               | **根因**                                                                     | **解决方案**                                                             | **以后不能再做**                                        |
|---------------------------|----------------------------------------|------------------------------------------------------------------------------|--------------------------------------------------------------------------|---------------------------------------------------------|
| Planner/Frenet            | Dapai step150 IndexError               | resample 索引79越界，best_traj 长79                                          | 安全重采样/adapter；完整199/249跑通                                      | 先分 search fail 与 adapter/interface fail              |
| Multi-ego observation     | A/B duplicate / 假碰撞风险             | 受控车又出现在 external tracked objects                                      | controlled filter/partition                                              | 受控对象不得重复作为 external actor                     |
| Environment history       | B 状态看不到/记录不完整                | dual history 主要记录 A trajectory；B truth 在 MultiEgoRuntime               | 同 iteration 读取 runtime.state_for(B)                                   | 不得用 A history 假装 A+B                               |
| Native B visualization    | B 无法直接原生回放                     | 同上                                                                         | A 用 PlanVisualizer2D/history；B live overlay；A/history pose error≤1e-8 | 禁止 route_s/CSV/pixel 猜 B pose                        |
| Conflict screening        | Jiangtong 路线相交却无强交互           | 自然 ETA 差≈9.496s                                                           | 负筛选 freeze                                                            | 空间交叉不等于 temporal conflict                        |
| CollisionLookup           | 离散 lookup 可 false positive          | 栅格/查表与真实 footprint 几何定义不同                                       | exact physical footprint truth-check                                     | NO-MCTS causal conflict 必须物理 overlap 证据           |
| J117/Polygon NO-MCTS      | 如何证明“没规划会撞”                   | 不能靠示意图或中心点                                                         | 固定 baseline、真实 runtime、0.1s footprint/swept geometry               | 不得用人工 delay 制造冲突                               |
| FullMine init slow        | 大 semantic initialize 卡住            | 对~400k node 重复线性 scan                                                   | token2ind O(1)，commit32fb429                                            | 先 profile 算法复杂度，不要归咎 GPU                     |
| A1 endpoint               | 末端虚拟障碍/4.5m lead                 | virtual endpoint geometry                                                    | 仅 virtual endpoint length_rear=0                                        | 不要改地图/goal掩盖 planner bug                         |
| A2 blocker                | 高曲率段中途停车                       | steering-rate infeasibility，不是最终 leading/occupancy                      | speed cap + backward braking envelope                                    | 先 shadow/controller truth；不要盲补 bitmap             |
| Map/runtime links         | 搬目录后 runtime 找不到 map            | 绝对路径/softlink 依赖                                                       | current_paths + restore/symlink gate                                     | 冻结 runner 优先恢复路径，不直接改                      |
| Low-memory FullMine       | RC137/Killed                           | 2GiB cgroup 不足；高卡实际给80GiB/15CPU                                      | 免费 preflight 后再高资源                                                | 不要用2GiB硬跑大 bitmap/EDT                             |
| Map Showcase V1           | schema gate fail                       | 误把 custom semantic 当 GeoJSON FeatureCollection                            | 读真实 schema 后 V2                                                      | 文件名含 geojson 不代表结构就是 GeoJSON                 |
| Map Showcase V3           | ffmpeg SIGKILL:9                       | 当前只证实进程被杀                                                           | 保留120帧，标 INCOMPLETE                                                 | 不得无证据写“就是 OOM”                                  |
| Native Video V1           | raw (1545,3666) 布局异常               | 可视化尺寸/layout                                                            | V2 raw (1545,1073) + quality gate                                        | 科学链能跑不等于汇报质量 PASS                           |
| Renderer conflict XY      | Key/字段不存在                         | manifest 给 route_s 而非直接 XY                                              | semantic waypoints + route station 求点                                  | 禁止 hardcode conflict XY                               |
| Renderer recovery         | KeyError: OUT                          | wrapper 未透传 env                                                           | required env gate                                                        | wrapper 先验证所有外部依赖                              |
| Polygon node count        | 529 vs 530                             | 529 unique raw nodes + closure duplicate=530 plot coords                     | 分清数据点与绘图闭合                                                     | 不要把 closure 当缺节点                                 |
| Video mid-pan             | 画面阶段性空                           | camera logic                                                                 | V0.2 target-anchored camera                                              | 自动编码 PASS 后仍需 human visual gate                  |
| Long heredoc              | 命令/输出粘贴污染、乱码/空文件         | 聊天 UI 与终端内容混粘                                                       | 短块，一步一块，只复制代码                                               | 先 ls/file/sed 再删单文件；禁止清整个目录               |
| C04 loader                | TypeError float(list)                  | 旧 runner 未规范一元素 list/array 形状；exact failing source line 未完整保留 | 后续 Nx1/shape normalization runner 通过                                 | 不再从旧 doc 重跑；不猜 exact line                      |
| C04 NO-MCTS               | NameError MAX_STEPS                    | harness 常量遗漏                                                             | 最小 runner fix                                                          | harness FAIL 不等于 science FAIL                        |
| C11 NO-MCTS               | 200-step completed_post_conflict=false | horizon 不足                                                                 | 21.2s/212 steps 后 causal conflict PASS                                  | 只修时间窗，不改物理/算法                               |
| C11 Fleet                 | 无碰撞但89s不完成                      | deadlock/progress failure                                                    | 保留科学负结果                                                           | 禁止调参把负结果抹掉                                    |
| Dataset                   | 旧448与current452看似同schema          | rear-axle/geometric-center producer语义已变                                  | legacy隔离 + current-code recollection                                   | schema相同不等于 label semantics 相同                   |
| V2R unit verifier         | MISSING final PASS marker              | final echo 在打包后、未 tee console                                          | 按实际 unittest/numeric/repo gate判 PASS                                 | 验收器先确认日志采集边界                                |
| V2R sidecar V1            | SyntaxError line≈1694                  | 插入块落在未闭合 v0_records.append 内                                        | V2 移到完整 V0 record block 外                                           | instrumentation 必须本地 compile + insertion-only proof |
| V2R sidecar V2 full       | 只有 v0_jsonl_sha parity FAIL          | V1 字段污染 V0 direct_boundary serialization                                 | V3 使用独立 v1_direct_boundary                                           | 旁路必须连“输出 serialization”也隔离                    |
| Result filename semantics | 某些 baseline 文件名存在即看似成功     | immutable baseline 结果可真实包含 FAIL                                       | 永远解析 JSON gate/RC，不按文件存在判 PASS                               | 存在 ≠ 通过                                             |

# 12. 当前有效版本、SUPERSEDED/HOLD/未验证对象

| **对象**                                   | **状态**                 | **处理规则**                                                    |
|--------------------------------------------|--------------------------|-----------------------------------------------------------------|
| MineSim baseline 2521aa4                   | HISTORICAL/FROZEN        | 保留回归，不是 current HEAD                                     |
| Pure MCTS 94693dc + 448                    | HISTORICAL/FROZEN        | 专家历史证据；训练 label 语义需隔离                             |
| J117 Phase4C/5                             | FROZEN                   | 不要重跑；用于 multi-ego regression                             |
| FullMine Vector V4 112d2bd                 | CURRENT FROZEN           | 不得修改 tag；新研究从当前 source / 独立 branch/evidence dir    |
| Representative Pure MCTS 3/3               | FROZEN                   | 无需重做                                                        |
| Polygon21 Fleet freeze v2                  | FROZEN                   | 正式 benchmark；freeze v1 仅 harness failure provenance         |
| Cross-scene C04/C11/C06                    | CLOSED                   | C11 negative 要保留；不可重调成“全PASS”                         |
| Native Video V1                            | SUPERSEDED               | 保留 provenance，不用于正式汇报                                 |
| Native Video V2                            | CURRENT FINAL            | 正式仿真视频 evidence release                                   |
| Map Showcase V2                            | PASS / HISTORICAL STABLE | V3 未 final，不覆盖 V2                                          |
| Map Showcase V3                            | INCOMPLETE               | 120 frames 有，final encode/release HOLD                        |
| Middleware Snapshot/Offline/Renderer/Video | FROZEN                   | live adapter 未正式 PASS；不要把 offline freeze说成live runtime |
| FullMine production validity               | HOLD / NOT PROVEN        | 无 authoritative drivability，不得升级口径                      |
| Terrain/Z risk                             | HOLD                     | datum/slope语义未权威验证                                       |
| V2H probabilistic safety                   | NOT IMPLEMENTED          | Paper1 V0/V1 明确未实现                                         |
| Π_safe pruning                             | NOT STARTED              | 连续V2R和dynamic V2V contract未冻结前禁止接入                   |
| Neural network/checkpoint                  | NOT STARTED              | 无正式 Value/Policy model 或 checkpoint                         |
| V2R sidecar V3                             | PREPARED / CLOUD NOT RUN | 当前唯一最小下一步                                              |

# 13. 环境、资源、依赖、Git 与文件操作不变式

| **项目**         | **当前规则 / 真实观测**                                                                       |
|------------------|-----------------------------------------------------------------------------------------------|
| Repo             | /root/MineSim-Dynamic                                                                         |
| Conda            | minesim；/root/miniconda3/envs/minesim                                                        |
| Python           | 3.9.25                                                                                        |
| 低资源 cgroup    | 近期静态 smoke 实测 memory.max=2147483648（2GiB）；cpu.max=50000 100000（0.5 CPU）            |
| 高资源 cgroup    | FullMine/V2R real run 实测 memory.max=85899345920（80GiB）；cpu.max=1500000 100000（15 CPU）  |
| CUDA             | 地图/MCTS/EDT 即使高资源也 export CUDA_VISIBLE_DEVICES=""；高卡价值主要是 CPU/RAM 配额        |
| 历史 repo status | 当前期望 HEAD=112d2bd...，status 至少保留已知 \`?? ^C\`；若多出 tracked/staged 变化先只读审计 |
| 大文件           | /root/autodl-tmp；repo 只保留必要 tracked source                                              |

**所有可执行 Shell 的固定前缀：**

cd /root/MineSim-Dynamic  
source /root/miniconda3/etc/profile.d/conda.sh 2\>/dev/null \|\| true  
conda activate minesim  
export PYTHONPATH=/root/MineSim-Dynamic  
export CUDA_VISIBLE_DEVICES=""

- 交互顶层禁止裸 \`exit\`；需要失败即在子 shell \`( ... )\` 中用 \`false\` 或只打印 FAIL。

- 禁止 \`git reset --hard\`、\`git clean -fd\`、\`git add .\`。只 \`git add \<exact files\>\`；commit 前 \`git diff --check\` / \`git diff --name-only\` / \`git diff --cached --name-only\`。

- 长仿真普通终端/screen 执行；记录独立 log + rc；screen 只负责托管，不是证据源。先 \`cat run.rc \|\| echo RUNNING\` + tail/grep，避免重复启动。

- 每个 map candidate / script / result 必须绑定 SHA；临时 runtime 切图用 symlink + strong SHA gate。

# 14. 用户—ChatGPT—Codex 协作规则与成本控制

| **最新协作定义** ChatGPT 负责分析、决策、关键代码与验收设计；用户复制到 AutoDL 终端执行并返回真实输出/ZIP；复杂算法、顽固 Bug 或适合云端自主执行的边界任务，才在省钱前提下交给 Codex。Codex 不是后台无限运行的第二个 AI。 |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

| **规则**         | **固定执行方式**                                                                            |
|------------------|---------------------------------------------------------------------------------------------|
| 默认 Codex model | gpt-5.6-luna medium                                                                         |
| 升级策略         | Luna capacity/复杂算法/顽固 bug/关键终审时临时 Terra/Sol；任务完成立即降回 Luna             |
| 已知事实         | 不重复扫描/重复解释；frozen 阶段不重审                                                      |
| 任务粒度         | 每次只推进一个最小 blocker；只返回 PASS/FAIL + 必要字段                                     |
| 免费优先         | Git/status/hash/file existence/grep/py_compile/JSON audit/Shell/Python 能确认的事情不用模型 |
| 资源顺序         | 先低资源完成 read-only preflight/static/smoke；只有确认下一步需要大图/长运行才开80GiB       |
| 实验顺序         | 只读 preflight → 1–5 step smoke → 短闭环 → full experiment → freeze                         |
| 长任务           | 普通 terminal/screen；Codex 不长期挂着等待                                                  |
| 文件             | 大 log/script/result 放 /root/autodl-tmp；repo 只必要 source                                |
| 失败处理         | 只定位当前故障域；不因为一个失败回滚到全流程重审                                            |
| 安全目标         | 项目可复现/可恢复优先于目录美观、少几分钟或少几个文件                                       |

- 复杂 Codex prompt 必须包含：已冻结事实、唯一目标、允许修改文件、禁止操作、最小测试、PASS/FAIL、最终只输出字段、完成即停止。

- 如果一个 task 能在 Shell/Python 中免费得到确定答案，不应为了“让模型看看”浪费 Codex。

# 15. 云端文档生成、归档与删除情况

**严谨边界：**以下“已生成文档”来自会话中实际上传的 Word/ZIP 与 cleanup 说明；本文件无法远程枚举用户当前云端目录在 2026-08-18 此刻的全部 Word 数量，因此“云端现存精确文档数量/是否有人手动删除某个 Word”未重新做 live audit，标为未验证。能确定的是 2026-08-16 cleanup closeout：科研文件删除 0。

| **日期**   | **文档/包**                                                            | **当前定位**                                                   |
|------------|------------------------------------------------------------------------|----------------------------------------------------------------|
| 2026-07-26 | MineSim-Dynamic_普通AI与AutoDL云端交互及代码调试手册                   | HISTORICAL；奠定安全交互/Git规则                               |
| 2026-07-26 | MineSim-Dynamic_项目必备配套资料_风险清单与AI长期交接手册              | HISTORICAL                                                     |
| 2026-08-06 | MineSim-Dynamic_项目全景档案与AI长期接管超级手册                       | HISTORICAL；Pure MCTS/五Planner阶段                            |
| 2026-08-09 | MineSim-Dynamic_云端项目完整交接与工作流手册                           | HISTORICAL；J117单车闭环                                       |
| 2026-08-11 | MineSim-Dynamic_新地图项目云端交接手册                                 | HISTORICAL；FullMine V1/DEV map                                |
| 2026-08-12 | MineSim-Dynamic_项目完整进展与云端AI接管超级手册                       | HISTORICAL；Vector V2/CollisionLookup进行中                    |
| 2026-08-13 | MineSim项目云端接手与技术总览                                          | HISTORICAL；A1/A2/CollisionLookup调试                          |
| 2026-08-14 | 两份 FullMine Vector V4 / Pure MCTS 冻结长手册                         | HISTORICAL/FROZEN SNAPSHOT                                     |
| 2026-08-16 | MineSim-Dynamic_全项目阶段性总交接与AI无缝接管手册                     | HISTORICAL；整理/Native Video/当时 cross-scene static          |
| 2026-08-16 | MineSim_云端项目文件整理与维护说明（docx + md，最终整理包）            | CURRENT cleanup provenance                                     |
| 2026-08-17 | MineSim-Dynamic 全项目阶段性总交接与AI无缝接管（附件名 29570dde…docx） | HISTORICAL；其中 C04 float(list) 停点已被 8/18 覆盖            |
| 2026-08-18 | 本《全项目阶段性总总结与 AI 无缝接管手册》                             | CURRENT SESSION ARTIFACT；只有用户上传云端后才可称云端现存文件 |

- Phase2 cleanup 的文档/报告策略：正式报告备份进入 \`/root/autodl-tmp/10_MineSim_REPORTS\`；历史 planner/report 等进入 \`90_MineSim_ARCHIVE\`；不作为科学运行输入。

- 整理总结果：顶层约530→121；423 move/isolate；科研文件删除0。Quarantine 是隔离，不是授权删除；Archive 是可恢复历史，不是垃圾。

- 因为“没有删除”，整理本身不等于释放磁盘空间。若以后需要真正腾盘，必须另开只读 inventory + checksum/equivalence + 明确授权的 deletion phase。

- 本次新 Word 仅在会话侧生成；不要在文档中假设它已经复制到 \`/root/autodl-tmp/10_MineSim_REPORTS\`。用户若上传，应再记录云端路径与 SHA。

# 16. 关键 Commit / Tag / SHA / 冻结证据速查

| **里程碑**          | **Commit**                               | **Tag / 语义**                               |
|---------------------|------------------------------------------|----------------------------------------------|
| IDM baseline        | 2521aa41a69a6e734c04c15a715e9530c8095ac3 | idm-replay-autodl-baseline                   |
| Pure MCTS + expert  | 94693dc799fe5f325a75e8fc6d7d5e88764b4799 | mcts-expert-dataset-v1-20260802              |
| Jiangtong V22       | 94794c963f9c3eaf1873b275df6d319ca2636817 | jiangtong-v22-benchmark-screening-20260809   |
| J117 Phase4C        | ec1c958735b0ee76201284faacb46fccc75c7f6c | j117-phase4c-single-ego-closed-loop-20260810 |
| J117 Phase5         | da4105b836dbbd3e702ee25fbb364109bc4e2596 | j117-phase5-dual-ego-pure-mcts-20260810      |
| FullMine lookup     | 32fb42920d8cc404b37cd25dc47cbc6fbde4d9f4 | token2ind O(1)                               |
| FullMine V1         | d81c57154e4e5d0b4df1251cf565d9aacffaa026 | fullmine-dev-runtime-pass-20260811           |
| CURRENT FullMine V4 | 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e | fullmine-vector-v4-runtime-freeze-20260814   |

| **资产/冻结对象**              | **SHA256**                                                       |
|--------------------------------|------------------------------------------------------------------|
| FullMine semantic              | b85a3d8b28f2252ecb5bda179d514573f6333079def838cd048566f556d95cd0 |
| FullMine V4 bitmap             | 51abcd5a86e5c510204a5dacc873691506d721f98982ab7f98585d4e0f7efdd0 |
| CollisionLookup                | 10c1d1339e742ca893fedb4aa51402addfba82e16e08f68339ea35d35ba3043b |
| Representative MCTS summary    | 742d0716a00364a625e01b27c693134488211c8989e4996b072739c3a500d056 |
| Representative MCTS freeze     | 322e90d6995c410597d01925de6d77f1fd91ddb8c4c73a25c3e87446d37ac1fa |
| Polygon21 scenario             | 362eff18c7ccc88ea8dfaf083a517603566516943690d5cbe76bd1a97afc89e1 |
| Polygon21 NO-MCTS              | 060880c8edc851e05606871cb647058d091ce8737f952b9864cc94e9d6fcfd13 |
| Polygon21 Fleet seed0          | 2eeb28e1fcb1c48d826c387853ec4f9a8a1acf07c9d7e7d1c067701bd4a1398f |
| Polygon21 Fleet freeze v2      | b89d290c9cb06d1efb99688ee27b23898ab81d11e36023832477dc2fc834364b |
| Native Video V2                | f695ba22ecd61c4a643e8ffecac483bc218de9153f95f88b4e0e3006bca03d58 |
| Map Showcase V2                | 9f78f357eecfc25ea543d163e8d472dc06abeb1fff3215ed30577267750d1e14 |
| Cleanup Phase2K closeout ZIP   | e3d4ba27bd06c74c7ca23ed55de65208022f07d4e0cb600eb58bcbbcaaf33a4b |
| Cross-scene conclusion bundle  | 2dde3d66652097ab8319ac44693f2c035435f838799e24ff6147facc6565ca0b |
| Paper method compatibility     | 2c2f85767b60e139bd9d6b56a6b24d7b3a0afd95c5ca802b81ad882acb67cb41 |
| Paper1 V0 observational freeze | 714698023347899f2b3f52e13965d6507eac7c325ad681ee48167b266521460d |
| V2R field source ZIP           | 7ceb5a69845de9c85b9a03d4608c1f43880b7a305c42ea60995d6250a711cff0 |
| Current V3 sidecar source ZIP  | 276639ed81bf00317bccde93bec9df82e84d675519cf24f6cb665c8dfe1e33ad |
| Current V3 static runner       | bbed06e0e2836325d0f8ba6a26dafb06b85f359a038083c1a7c9b48e7f531575 |

# 17. 证据来源索引与冲突处理原则

| **证据**                                                                                                      | **主要用途**                                                                          |
|---------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------|
| 当前对话 2026-08-18 terminal/ZIP                                                                              | cross-scene 动态收口；dataset semantic audit；Paper1 safety/V2R 最新状态；优先级最高  |
| 29570dde-20f0-4c7f-90ae-089c09262608.docx                                                                     | 2026-08-17 全项目 handover；middleware / 当时 cross-scene 停点；后续已部分 superseded |
| MineSim-Dynamic_全项目阶段性总交接与AI无缝接管手册_2026-08-16.docx                                            | Native Video / cleanup / historical cloud structure                                   |
| MineSim-Dynamic_全项目最新进展_FullMine_VectorV4地图成果与PureMCTS冻结_云端AI长期接管超级手册_2026-08-14.docx | FullMine V4、Representative MCTS、Codex/资源规则                                      |
| MineSim-Dynamic_项目完整进展与云端AI接管超级手册_2026-08-12.docx                                              | Vector V2 semantic / bitmap / targeted runtime 历史                                   |
| MineSim-Dynamic_新地图项目云端交接手册_2026-08-11.docx                                                        | J117 → FullMine V1、地图 structural/runtime                                           |
| MineSim-Dynamic_云端项目完整交接与工作流手册_2026-08-09.docx                                                  | J117单车、Codex/云端 workflow                                                         |
| MineSim-Dynamic_项目全景档案与AI长期接管超级手册_2026-08-06.docx                                              | baseline/PureMCTS/五Planner早期历史                                                   |
| MineSim_云端项目文件整理最终文档包.zip / \_cleanup.md                                                         | Phase2A–2K move/isolate、current_paths、restore、删除=0                               |
| 可参考论文.7z                                                                                                 | Paper1/Paper2 方法来源；只用于 method adaptation，不替代项目事实                      |

- 文件名出现 “final / pass / v2 / freeze” 不能单独作为事实；必须核 SHA、manifest/result 内容和 PASS gate。

- 旧 Word 中的“下一阶段”如果与更晚终端冲突，旧 Word 只保留历史价值。例如 8/17 的 C04 float(list) blocker 已被 8/18 dynamic closure 覆盖。

- 任何生产/矿区真值不能从算法实验反推；地图 production validity、terrain datum、human uncertainty 等仍须外部权威来源。

# 18. 快速接手区（下一位 AI 必须先读）

| **CURRENT_STATE** 核心科研链已完成：MineSim baseline、Pure MCTS、J117 single/dual、FullMine V4、Representative Pure MCTS 3/3、Polygon21 Fleet 5/5、cross-scene dynamic C04/C11/C06（含 C11 科学负结果）、Native Video V2、cloud cleanup、Paper1 SafetyRisk V0 observational freeze。当前唯一正在推进的是 Paper1 continuous V2R sidecar V3 的云端静态验证；Neural-MCTS 正式训练尚未开始。 |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

| **事项**      | **必须记住**                                                                                                                                                                                                     |
|---------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 正式 repo     | /root/MineSim-Dynamic                                                                                                                                                                                            |
| 预期 HEAD     | 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e                                                                                                                                                                         |
| Frozen tag    | fullmine-vector-v4-runtime-freeze-20260814                                                                                                                                                                       |
| 预期 status   | 已知 \`?? ^C\` 必须保留；若出现其他 tracked/staged 变化先停下只读调查                                                                                                                                            |
| 关键数据 root | /root/autodl-tmp；先读 /root/autodl-tmp/00_MineSim_ACTIVE/current_paths.json（若当前存在）                                                                                                                       |
| 绝对不能动    | FullMine runtime semantic/bitmap symlink target、90_MineSim_ARCHIVE、98_MineSim_QUARANTINE、99_MineSim_CLEANUP_MANIFEST、/root/autodl-tmp/MineSim-Dynamic dirty historical HOLD workspace、frozen result/bundles |
| 已冻结不重做  | IDM baseline；Pure MCTS Dapai/Jiangtong；J117 single/dual；FullMine V4 targeted/oldmap; Representative MCTS；Polygon21；Native Video V2；cleanup；SafetyRisk V0                                                  |
| HOLD          | production-authoritative drivability；terrain/Z/slope risk；V2H；Paper2 passing-order/RA-MVSFM/OCP；Π_safe；正式 NN/checkpoint                                                                                   |
| 当前 next     | V2R sidecar V3 static smoke；不是 recollection full run，也不是 GPU training                                                                                                                                     |

## 18.1 下一步最小行动

**资源：**只需要低资源卡（2GiB/0.5CPU 级别即可）；CUDA 禁用。不要先开高资源卡。

| **文件**                                                                   | **预期 SHA**                                                     |
|----------------------------------------------------------------------------|------------------------------------------------------------------|
| /root/autodl-tmp/C04_PAPER1_V2R_DISTANCE_V1_SIDECAR_SOURCE_V3.zip          | 276639ed81bf00317bccde93bec9df82e84d675519cf24f6cb665c8dfe1e33ad |
| /root/autodl-tmp/RUN_C04_PAPER1_V2R_DISTANCE_V1_SIDECAR_STATIC_SMOKE_V3.sh | bbed06e0e2836325d0f8ba6a26dafb06b85f359a038083c1a7c9b48e7f531575 |

cd /root/MineSim-Dynamic  
source /root/miniconda3/etc/profile.d/conda.sh 2\>/dev/null \|\| true  
conda activate minesim  
export PYTHONPATH=/root/MineSim-Dynamic  
export CUDA_VISIBLE_DEVICES=""  
  
\# 先核 HEAD/status/source SHA/runner SHA，再在子 shell 内运行 V3 static smoke。

| **完成标准**            | **必须看到**                                                     |
|-------------------------|------------------------------------------------------------------|
| Insertion-only          | BYTE_EXACT_PARENT_RESTORATION=True；PASS V1_INSERTION_ONLY_PROOF |
| Serialization isolation | PASS V0_SERIALIZATION_ISOLATION_PROOF                            |
| Syntax                  | PASS PY_COMPILE                                                  |
| Science boundary        | PASS SCIENCE_BOUNDARY_GATE                                       |
| Repo                    | REPO_UNCHANGED=PASS                                              |
| Final                   | PASS C04_PAPER1_V2R_DISTANCE_V1_SIDECAR_STATIC_SMOKE_V3          |

**只有 V3 static PASS 后：**才开高资源卡做 C04 real 3-step V3 smoke；再 PASS 后跑 126-step full parity。V3 full parity 必须同时满足 authoritative Fleet result/log SHA unchanged、V0 JSONL/summary frozen SHA unchanged、V1 126 records 完整/no hard overlap/no mismatch。只有这门过，continuous V2R 才能冻结，然后再进入 relative heading + dynamic V2V safety threshold；仍不是直接 Π_safe / NN training。

## 18.2 继续工作前的只读检查清单

- pwd / repo root = /root/MineSim-Dynamic；conda = minesim；Python=3.9.25。

- git rev-parse HEAD = 112d2bd0…；git status 不应出现未知 tracked/staged 改动；不要清理 \`?? ^C\`。

- 核 current V3 source ZIP 与 runner SHA；如果文件名相同但 SHA 不同，立即 FAIL。

- 核 cgroup memory.max / cpu.max；static 不需高资源，real map/EDT 才需约80GiB/15CPU。

- 核 runtime semantic/bitmap 两条 symlink target 与 frozen SHA；不要为了目录整理改 target。

- 核没有重复运行的长 Python process / screen job；看 rc/log 再决定是否启动。

- 若要引用旧实验，先读 result JSON/manifest gate，不按“文件存在”判断 PASS。

- 若用户随后转向 NN，先回到 dataset contract/current-semantic recollection，不混历史448与current452 labels。

| **下一位 AI 的第一轮回答格式** 只输出 CURRENT_STATE / DIFF_FROM_EXPECTED / NEXT_ONE_STEP / RISKS-HOLD。若 preflight 与本文一致，直接推进 V3 static；不要重述整本项目、不要重跑 frozen benchmark。 |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

**— 文档结束｜Evidence cutoff: 2026-08-18 —**
