**MineSim-Dynamic**

**全项目阶段性总交接与 AI 无缝接管手册**

MineSim 复现 → 蒙特卡洛/MCTS 接入 → 单车跑通 → 双车冲突场景构建 → FullMine 新地图接入  
→ Fleet-MCTS 双车联合规划与多种子验证 → 原生 MineSim 可视化与汇报材料 → 云端文件安全整理 → 后续神经网络接入

| **对象/阶段**             | **状态**          | **当前准确结论**                                                                          |
|---------------------------|-------------------|-------------------------------------------------------------------------------------------|
| 正式科学基线              | **PASS / FROZEN** | 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e / tag fullmine-vector-v4-runtime-freeze-20260814 |
| FullMine Vector V4        | **PASS / FROZEN** | Research/DEV baseline；semantic/bitmap/runtime/planner fixes 已冻结                       |
| Polygon21 Fleet-MCTS      | **PASS / FROZEN** | NO-MCTS 真物理冲突；Fleet-MCTS 5/5；无参数重调                                            |
| FullMine 可视化中间层 MVP | **PASS / FROZEN** | SimulationSnapshot V0 + OfflineAdapter V0 + Renderer V0.1 + Video V0.2；四门禁全部 PASS   |
| Cross-scene C04/C11/C06   | **HOLD**          | 静态 6/6 PASS；C04 动态 real-loader 当前停在 high-memory 后暴露的 scalar/list TypeError   |
| Neural-MCTS               | **NOT STARTED**   | 正式训练未开始；在跨场景动态线完成后进入数据治理 / Value Network 路线                     |

**证据截止：2026-08-17**

*文档定位：下一位 AI / 工程人员在不重新扫描全项目、不重复已冻结实验、不重新询问大量背景的前提下，安全、低成本地从当前节点继续。*

| **事实原则** 最新云端终端 / Git / SHA / 冻结 manifest / 实际代码执行结果 \> 最新交接文档 \> 历史文档 \> 设计计划。任何缺乏直接证据的事项一律写为“未验证 / HOLD”，不以常识补齐。 |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# 0. 文档使用规则、证据等级与状态术语

这不是论文正文，也不是宣传材料，而是一份可执行的工程与研究交接手册。它的核心目标是把“已经证实的事实、历史证据、当前 blocker、尚未开始的工作”分开，避免下一位 AI 因旧文档或记忆冲突而重做已冻结工作。

| **等级** | **含义**                                         | **使用规则**                               |
|----------|--------------------------------------------------|--------------------------------------------|
| V-LIVE   | 当前 AutoDL 终端、Git、源码、文件、SHA、运行输出 | 最高优先级；每次重连只读复核。             |
| V-FROZEN | result / manifest / SHA / tag / frozen ZIP       | 可作为长期锚点；默认不重跑、不覆盖。       |
| V-DOC    | 2026-08-16 及更早正式交接 Word                   | 补足历史链；若与更晚终端冲突，以终端为准。 |
| V-DESIGN | 计划、建议、未来网络/平台方案                    | 不能写成已完成。                           |

状态术语固定使用：PASS = 当前门禁通过；FROZEN = 已绑定可复核证据且默认不重做；HISTORICAL = 历史有效但不是当前生产/科学版本；SUPERSEDED = 已被后续版本替代但保留 provenance；INCOMPLETE = 部分产物完成但未完成正式 release；FAIL-EVIDENCE = 失败本身为有效诊断证据；HOLD = 禁止擅自推进或结论不足；NOT STARTED = 尚未正式开始。

## 0.1 AI / Codex 归属边界

用户要求纳入“今天 Codex 在云端实际完成的工作”。现有资料能够明确证明的，是多轮 AI 设计脚本 + 用户 AutoDL 终端执行 + 必要时 Codex 做边界明确任务的协作链；但 2026-08-17 的每一段 middleware / cross-scene 脚本日志并未可靠标注究竟由 Codex 还是 ChatGPT 生成，因此本手册不虚构逐文件作者。

> **•** 明确历史证据：2026-08-13 曾给 Codex 准备严格 P0，只允许抓 C/D/E exact failure state 与真值，不得先改 mask / MCTS；2026-08-12 上午也有 Codex 审计，随后用户明确停止 Codex、改为普通终端执行。
>
> **•** 2026-08-17 可以确认的真实成果：SimulationSnapshot/OfflineAdapter/Renderer/Video 中间层链完成并冻结；cross-scene 只读恢复、C04 loader 环境恢复、低内存 SIGKILL 定位、高内存复现实验均由真实终端输出证实。
>
> **•** 归属原则：若日志没有明确 Codex 标记，只写“AI/脚本 + 用户终端实际完成”，不写“Codex 完成”。技术结论只由源码、SHA、manifest、runtime 输出决定。

## 0.2 贯穿全项目的核心不变式

> **•** /root/MineSim-Dynamic 是唯一正式 Git repo；/root/autodl-tmp/MineSim-Dynamic 是脏历史工作区，HOLD。
>
> **•** 大文件、地图、日志、实验结果、临时脚本放 /root/autodl-tmp；正式 repo 仅保留必要 tracked source。
>
> **•** 冻结后的 map/scenario/result/runtime 不为“方便”改绝对路径、不覆盖 bitmap、不重命名 semantic identity。
>
> **•** 所有科学可视化必须来自真实 semantic/bitmap/runtime/frozen results；视觉层只能改颜色、线宽、字体、camera、布局、编码参数。
>
> **•** 任何 FAIL 先分类：接口 / 环境 / 数据契约 / 几何 / planner / controller / 资源 / harness；不得直接把表象当根因。

# 1. 当前项目 30 秒状态

| **一句话** 核心科学基线已经从 MineSim 原项目复现推进到 FullMine Vector V4、代表区域 Pure MCTS、Polygon21 Fleet-MCTS 5/5 和冻结可视化中间层；当前真正的研究 blocker 是 cross-scene C04 real-loader 在高内存实例中暴露的 \`float(list)\` 数据契约错误，尚未进入 C04 NO-MCTS/Fleet 动态实验；Neural-MCTS 正式训练仍未开始。 |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

| **对象/阶段**                      | **状态**          | **当前准确结论**                                                                                        |
|------------------------------------|-------------------|---------------------------------------------------------------------------------------------------------|
| MineSim Dapai/Jiangtong IDM/replay | **PASS / FROZEN** | 历史回归锚点；commit/tag 不再重做。                                                                     |
| Pure MCTS 单车                     | **PASS / FROZEN** | Dapai/Jiangtong online closed-loop + 448 strict expert。                                                |
| 五 Planner / Budget                | **HISTORICAL**    | 用于公平性与预算敏感性证据，不作为当前主线。                                                            |
| J117 单车                          | **PASS / FROZEN** | 423 steps / 42.3 s / goal reached。                                                                     |
| J117 双车 Pure MCTS                | **PASS / FROZEN** | NO-MCTS 真重叠；5 seed benchmark + swept safety 全通过。                                                |
| FullMine Vector V4                 | **PASS / FROZEN** | Vector V2 semantic + V4 bitmap/runtime + planner/CollisionLookup fixes；targeted 7/7 + Jiangtong 回归。 |
| Representative Coverage            | **PASS / FROZEN** | 带 documented limitations。                                                                             |
| Representative Pure MCTS           | **PASS / FROZEN** | 3/3，summary/freeze/tag 已冻结。                                                                        |
| Polygon21 NO-MCTS / Fleet-MCTS     | **PASS / FROZEN** | 物理冲突对照 + 5 seed 联合规划。                                                                        |
| Native MineSim Video V2            | **PASS / FROZEN** | 原生 PlanVisualizer2D / runtime 真值；V1 superseded。                                                   |
| Map Showcase V2                    | **PASS**          | 真实 semantic 全局展示稳定基线。                                                                        |
| Map Showcase V3                    | **INCOMPLETE**    | 120/120 frames 完成；ffmpeg SIGKILL；无 final release。                                                 |
| FullMine Middleware MVP            | **PASS / FROZEN** | Snapshot V0 / OfflineAdapter V0 / Renderer V0.1 / Video V0.2 四门禁完成。                               |
| Cross-scene C04/C11/C06 static     | **PASS**          | A/B 共 6 路线 static readiness final PASS。                                                             |
| Cross-scene C04 dynamic loader     | **FAIL / HOLD**   | 80 GiB 环境越过 map load 后 TypeError float(list)；需精确定位。                                         |
| Cross-scene NO-MCTS / Fleet        | **HOLD**          | C04 loader PASS 前禁止启动。C11/C06 dynamic 尚未跑。                                                    |
| Neural-MCTS                        | **NOT STARTED**   | 数据治理 / Value Network 等后续；不是当前下一刀。                                                       |

## 1.1 当前科学路线的实际顺序

历史 2026-08-16 交接文档曾把 Neural-MCTS 数据治理写成下一科学阶段；2026-08-17 用户先完成中间层 MVP 后明确返回多车科学主线，因此最新顺序已更新为：

C04 real-loader 修复 → C04 NO-MCTS causal conflict → C04 Fleet-MCTS seed0 → C04 多 seed → C11/C06 动态验证 → 多场景结论/剪枝 → dataset governance → Value Network → Value-guided MCTS → Policy+Value / PUCT → Neural-MCTS

这条最新顺序覆盖旧文档的“立即 Neural-MCTS”表述。

# 2. 项目完整时间线：从复现到当前节点

| **日期**      | **阶段**                 | **可复核结果 / 意义**                                                                                                                  |
|---------------|--------------------------|----------------------------------------------------------------------------------------------------------------------------------------|
| 2026-07-22    | 新地图接入框架           | 明确新矿区最终要形成 Raster/Bitmap + Semantic Map + Scenario，为 J117/FullMine 建立工程框架。                                          |
| 2026-07-26    | MineSim / IDM baseline   | 正式 repo /root/MineSim-Dynamic；commit 2521aa41...；tag idm-replay-autodl-baseline；建立 Git/云端安全纪律。                           |
| 2026-07-30~31 | Pure MCTS 接入           | MCTSPlanner 外壳、状态/动作/搜索/奖励/trajectory adapter 进入 MineSim；经历确定性/iLQR 接口修复。                                      |
| 2026-08-01    | Jiangtong 安全迭代       | CV/CTRV、physical buffer、viability、continuous clearance、动态冲突几何排查。                                                          |
| 2026-08-02    | 正式 MCTS + expert       | commit 94693dc...；Dapai/Jiangtong；448 strict expert samples；tag mcts-expert-dataset-v1-20260802。                                   |
| 2026-08-03~07 | 五 Planner / Budget      | MCTS/IDM/Frenet/Adapted Maneuver/Simple；统一 evaluator；Budget 50/100/200/300。                                                       |
| 2026-08-08~09 | Multi/Fleet MCTS         | FleetState + 16 joint actions；Dapai A-B-only 机制；Jiangtong V22 作为负筛选。                                                         |
| 2026-08-09    | J117 单车                | 真实 GeoJSON pilot → Map API → minimal Scenario → 423 step / 42.3 s full-route。                                                       |
| 2026-08-10    | J117 双车                | dual-ego production runtime + Pure MCTS；5-seed benchmark/swept safety PASS；commit da4105b...。                                       |
| 2026-08-11    | FullMine V1              | full structural + DEV_ONLY mask + O(1) lookup + 独立 map identity；basic single/dual runtime。                                         |
| 2026-08-12    | Vector V2                | source completeness audit；100 effective roads / 553 paths / 8 repairs / raw lane Z；15 target + 7 depth-safe scenarios。              |
| 2026-08-13    | CollisionLookup / A1/A2  | XG90G footprint 语义、exact geometry；A1 endpoint；A2 高曲率 controller 可执行性诊断。                                                 |
| 2026-08-13~14 | V3/V4 planner & bitmap   | steering-rate-aware speed profile + backward braking envelope；A1/A2/B1/B2 shadow；additive bitmap。                                   |
| 2026-08-14    | FullMine V4 freeze       | targeted 7/7 + Jiangtong regression；HEAD 112d2bd... + tag；Representative Coverage/Pure MCTS 3/3。                                    |
| 2026-08-15    | Polygon21                | FullMine V4 constructed physical-conflict benchmark；NO-MCTS physical conflict；Fleet-MCTS 5/5；freeze v2。                            |
| 2026-08-16    | 原生可视化               | Native MineSim V2；Map Showcase V2；V3 120 frames/编码未收口。                                                                         |
| 2026-08-16    | 云端安全整理             | Phase2A-2K；顶层约 530→121；423 移动/隔离；科研删除 0；restore/final health PASS。                                                     |
| 2026-08-17    | 可视化中间层 MVP         | SimulationSnapshot V0 → OfflineAdapter V0 → Renderer V0.1 → Video V0.2；科学/几何/技术/人工视觉四 Gate 全 PASS 并正式冻结。            |
| 2026-08-17    | Cross-scene 返回科研主线 | C04/C11/C06 static readiness 6/6 复核；C04 real-loader 在 2 GiB RC137；80 GiB 越过 map load 后暴露 float(list) TypeError；当前停止点。 |

# 3. MineSim 原系统与当前工程调用链

项目没有重写完整 MineSim。MCTS/Fleet-MCTS 主要替换或扩展决策层，最终 trajectory 仍经 MineSim Controller 与车辆模型执行。理解这个边界是后续 Neural-MCTS 与可视化中间层不破坏仿真真值的前提。

| **层**         | **当前真实职责 / 调用链**                                                                | **接手风险**                                                        |
|----------------|------------------------------------------------------------------------------------------|---------------------------------------------------------------------|
| Scenario       | ScenarioFileBaseInfo → MineSimDynamicScenario；场景起点/目标、dt、其他车辆轨迹、location | 绝对路径、state reference、raw location point 语义不能猜。          |
| Map            | MineSimMap + Semantic + Bitmap；semantic 给拓扑/reference path，bitmap 给 drivable mask  | runtime symlink / map identity / bitmap SHA 不能随意改。            |
| Planning       | GlobalRoutePathPlanner + IDM / MCTS / Fleet-MCTS                                         | 必须按真实 AbstractPlanner 接口；不能凭记忆猜签名。                 |
| Control        | TwoStageController → iLQR/LQR                                                            | planner trajectory 合法不代表 controller 可实现；A2 即典型。        |
| Vehicle        | Kinematic Bicycle Model / ego controller propagate                                       | rear_axle / geometric center / footprint 语义必须一致。             |
| Observation    | replay/reactive/prediction external actors                                               | dual 时必须过滤受控 A/B，否则 duplicate actor / 假碰撞。            |
| Multi-ego      | ControlledVehicleRuntime / MultiEgoRuntime                                               | A/B 同 iteration；权威 B state 不在普通 history。                   |
| Safety/Metrics | footprint + bitmap + goal + exact geometry + history/log                                 | 离散 CollisionLookup 可 false positive；必须 physical truth-check。 |
| Visualization  | PlanVisualizer2D + SimulationHistory/PlotData + live B overlay                           | history 主要是 A；不得伪装为 A+B 完整真值。                         |
| Middleware     | FullMineStateAdapter → SimulationSnapshot → Renderer                                     | 当前正式验证为冻结/离线 dual replay；live adapter 尚未正式 PASS。   |

## 3.1 Pure MCTS 模块化边界

| **模块**                                 | **角色**                                                                                    |
|------------------------------------------|---------------------------------------------------------------------------------------------|
| local_planner/mcts_planner.py            | MineSim API adapter：PlannerInput / history / map / trajectory。                            |
| mcts/state.py                            | MCTSState。                                                                                 |
| mcts/action_space.py                     | BRAKE / DECEL / KEEP / ACCEL 离散动作。                                                     |
| mcts/state_builder.py                    | MineSim 状态 → MCTSState。                                                                  |
| mcts/transition_model.py                 | 树内轻量近似动力学。                                                                        |
| mcts/reward.py                           | progress / speed / safety / comfort / terminal reward。                                     |
| mcts/node.py, mcts/search.py             | Selection / Expansion / Rollout / Backup。                                                  |
| mcts/trajectory_adapter.py               | 根动作 → MineSim 可执行轨迹。                                                               |
| mcts/diagnostics.py, mcts/expert_data.py | 搜索诊断与专家样本。                                                                        |
| Fleet modules                            | FleetState / FleetTransitionModel / FleetRewardModel / FleetMCTSSearch，对 A/B 做联合搜索。 |

| **Neural 接入边界** 未来网络最自然的切入点是 leaf value、policy prior、PUCT、adaptive budget/tree reuse；不应重写 Scenario、Controller、车辆模型或 MCTSPlanner 外壳。 |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# 4. 主线阶段一：MineSim 复现与 IDM Baseline

目标：先把原项目在云端稳定跑通，建立后续所有算法、新地图和全局源码修改的回归锚点。原 Dapai/Jiangtong 成品地图与 IDM/replay 不是“旧资产”，而是 production 行为对照。

| **项目**            | **冻结事实**                                     |
|---------------------|--------------------------------------------------|
| 正式仓库            | /root/MineSim-Dynamic                            |
| IDM baseline commit | 2521aa41a69a6e734c04c15a715e9530c8095ac3         |
| Tag                 | idm-replay-autodl-baseline                       |
| Conda               | minesim                                          |
| 项目 Python         | 3.9.25（多次 cloud preflight 实测）              |
| 原地图              | /root/datasets/maps 下 Dapai / Jiangtong；不修改 |
| 恢复备份            | /root/autodl-tmp/minesim_idm_baseline_backup     |

## 4.1 完成标准与长期意义

> **•** 正式 repo 可进入，minesim 环境可激活；Scenario/Map/Planner/Controller/vehicle loop 可运行。
>
> **•** 原成品地图不被 FullMine 开发覆盖；任何全局 planner/CollisionLookup 改动都必须做旧图 regression。
>
> **•** V4 最终回归中 Jiangtong 249 steps、0 vehicle collision、0 road boundary collision、strict safety PASS，证明旧基线仍是必要回归金标准。

| **禁止** 不能为了让当前 HEAD 看起来“干净”而 reset 到 baseline，也不能移动/覆盖 \`/root/datasets/maps\`。baseline 是历史锚点，不是当前 source HEAD。 |
|-----------------------------------------------------------------------------------------------------------------------------------------------------|

# 5. 主线阶段二：蒙特卡洛/MCTS 接入与单车跑通

项目实际接入的是 Monte Carlo Tree Search (MCTS)，现有证据没有独立“纯 Monte Carlo planner”作为另一条正式主线。Pure MCTS 使用 receding-horizon：每帧重新搜索，只执行根节点第一步动作，之后仍交给 MineSim Controller/iLQR/KBM。

| **参数 / 定义** | **历史正式值 / 范围**                                            |
|-----------------|------------------------------------------------------------------|
| 动作            | BRAKE=-3.0；DECEL=-1.5；KEEP=0；ACCEL=+1.0 m/s²                  |
| 历史正式 budget | 300；同时做过 50 / 100 / 200 / 300 消融                          |
| max_depth       | 8                                                                |
| tree_dt         | 0.5 s                                                            |
| c_uct           | 1.4                                                              |
| gamma           | 0.99（历史冻结记录；实际配置以运行时文件为准）                   |
| 输出 horizon    | 16 × 0.5 s                                                       |
| 目标速度        | 约 10 m/s                                                        |
| 障碍预测        | CV / CTRV                                                        |
| 安全            | 约 0.5 m physical buffer；历史 continuous clearance 阈值约 3.0 m |

## 5.1 正式结果与 expert data

| **对象**              | **事实**                                                                 |
|-----------------------|--------------------------------------------------------------------------|
| Commit                | 94693dc799fe5f325a75e8fc6d7d5e88764b4799                                 |
| Tag                   | mcts-expert-dataset-v1-20260802                                          |
| 正式场景              | Dapai / Jiangtong                                                        |
| Strict expert records | 448 条                                                                   |
| 样本内容              | ego、root state、selected action、action visits、Q、reward components 等 |
| 训练含义              | 只证明 expert-data 管线存在；不等于 Neural-MCTS 已训练                   |

## 5.2 五 Planner / Budget 支持性证据

| **Planner**      | **历史结果**                            | **严谨解释**                             |
|------------------|-----------------------------------------|------------------------------------------|
| MCTS             | 2/2 safe+goal；0 collision / 0 boundary | 只在两正式场景中成立，不能外推全局最优。 |
| IDM              | 1/2；Dapai 冲突                         | Jiangtong 可完成。                       |
| Online Frenet    | 0/2；0 collision / 0 boundary           | 安全但未完成任务；不能只看碰撞。         |
| Adapted Maneuver | 0/2；67 collision frames                | 评价当前适配版本，不代表原算法总体。     |
| Simple           | 0/2；90 boundary frames                 | 能力下限参考，不是公平主比较。           |

Budget 消融只改变搜索预算。Dapai 对 budget 明显敏感，历史固定时限下只有 300 进入目标；Jiangtong 在较低预算已接近饱和。这个事实后续直接支持 adaptive budget / tree reuse / value guidance 的研究动机。

## 5.3 关键失败：Frenet 接口越界

| **现象**                           | **真实根因**                                                                       | **解决**                                                    | **永久规则**                                                         |
|------------------------------------|------------------------------------------------------------------------------------|-------------------------------------------------------------|----------------------------------------------------------------------|
| Dapai 完整运行 step 150 IndexError | \_get_planned_trajectory() 重采样索引追加 79；best_traj 长度恰 79，有效最大索引 78 | 外部安全重采样/适配；之后 Dapai 199、Jiangtong 249 完整跑通 | Planner FAIL 先区分搜索失败 vs Planner→MineSim trajectory 接口失败。 |

# 6. 主线阶段三：双车冲突场景构建与 Multi/Fleet MCTS

目标：不再把第二辆车仅作为 replay obstacle，而是让 A/B 都进入受控 runtime 和联合搜索，在同一 simulation iteration 内共同决策。

| **组件**                                   | **已实现语义**                                                                                    |
|--------------------------------------------|---------------------------------------------------------------------------------------------------|
| ControlledVehicleRuntime / MultiEgoRuntime | 按 token A/B 管理两个受控车辆，统一 current/next iteration，同步接收两条 trajectory。             |
| SimulationSetup                            | set_multi_ego_runtime() 挂载 production multi-ego runtime。                                       |
| EnvironmentSimulation                      | dual propagate() 要求 trajectories 恰好包含 A/B，并同步调用 MultiEgoRuntime 更新。                |
| Observation filter                         | 稳定剔除受控 A/B，避免受控车同时作为 external actor。                                             |
| FleetState                                 | A/B 两个 MCTSState 的联合表示。                                                                   |
| FleetTransitionModel                       | 4×4 = 16 个 joint actions，A/B 物理几何联合传播。                                                 |
| FleetRewardModel                           | per-vehicle reward + internal continuous clearance soft penalty + hard collision/safety penalty。 |
| RouteGeometryCache                         | rear-axle route_s → geometric-center footprint，避免参考点混用。                                  |

## 6.1 场景筛选的真实教训

> **•** Dapai A-B-only 可以证明双受控时序分离与联合搜索机制，但 full scenario 有 external object-1 confound，因此不能作为新 benchmark 的唯一证据。
>
> **•** Jiangtong Traj26 虽有空间交叉，但自然 ETA 差约 9.496 s，不构成近同时冲突；commit 94794c963f9c3eaf1873b275df6d319ca2636817 / tag jiangtong-v22-benchmark-screening-20260809 是正式负筛选。
>
> **•** 场景筛选原则：空间交叉 ≠ 有联合决策价值。必须先证明时间上进入真实冲突窗口，再做 NO-MCTS vs Fleet-MCTS。

## 6.2 J117：真实地图 Pilot，从单车到双车

J117 是从 FullMine 原始 GeoJSON 中切出的真实 junction pilot，不是第三张原 MineSim 成品地图。其任务是先打通 GIS→Map API→Scenario→Planner→Controller→Runtime→Multi-Ego MCTS，再扩到全矿。

| **实验**             | **结果**                                                                                          |
|----------------------|---------------------------------------------------------------------------------------------------|
| Phase4C 单车         | 423 steps；42.3 s；路线约 398.998 m；min clearance≈1.599 m；goal reached；全程 drivable；无异常。 |
| NO-MCTS aligned dual | crossing gap≈0.00070 s；min clearance=0；真实几何重叠。                                           |
| Pure MCTS seed0      | crossing gap≈1.561 s；1 ms swept min clearance≈0.594 m；无碰撞。                                  |
| 5-seed robustness    | 5/5 benchmark PASS。                                                                              |
| 5-seed swept safety  | 5/5 PASS；minimum swept clearance≈0.594 m；gap≈1.35–1.97 s。                                      |

| **冻结项**    | **值**                                                     |
|---------------|------------------------------------------------------------|
| Phase5 commit | da4105b836dbbd3e702ee25fbb364109bc4e2596                   |
| Tag           | j117-phase5-dual-ego-pure-mcts-20260810                    |
| 定位          | real-map constructed benchmark / 回归区域；默认不重调 MCTS |

| **永久规则** J117 已冻结。除非 Map API / Planner / Controller / vehicle geometry 的新修改可能改变 J117，否则不要重新调 J117 MCTS；它是回归金标准。 |
|----------------------------------------------------------------------------------------------------------------------------------------------------|

# 7. 主线阶段四：FullMine 新地图接入——V1 → Vector V2 → V3/V4

| **版本语义** 当前 FullMine V4 并不是“重新造一张 V4 semantic”，而是 \`Vector V2 semantic + V4 bitmap/runtime + current planner/CollisionLookup fixes\`。semantic identity 仍是 \`geojson_full_mine_vector_v2_dev\`，不要为了命名美观重命名。 |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

## 7.1 原始数据与 frozen semantic

| **层**                                      | **数量 / 状态**                       |
|---------------------------------------------|---------------------------------------|
| road.geojson                                | 94 road polygon                       |
| road_boundary.geojson                       | 100 road 两侧边界                     |
| junction.geojson                            | 35 junction polygon                   |
| lane.geojson                                | 553 reference path / topology / raw Z |
| rgn_boundary.geojson                        | 84                                    |
| rng_load / unload / auxiliary               | 36 / 7 / 6                            |
| Frozen node                                 | 403,759                               |
| Frozen polygon / road / intersection        | 184 / 100 / 35                        |
| Frozen dubins / reference_path / borderline | 565 / 553 / 402                       |
| Waypoints                                   | 314,692                               |

> **•** Vector V2 用 8 条 provenance repair 恢复到 100 effective roads / 553 paths，并保留 raw lane Z。
>
> **•** waypoint\[3\] 保留 raw lane Z；source_z_datum_verified=false。
>
> **•** waypoint\[4\] slope 仍为 0.0；official smoothing rule 未复现，保持未验证状态。

## 7.2 大图性能与 route initialization

> **•** FullMine 早期 planner init 很慢，一个真实根因是 semantic token lookup 重复线性扫描；commit 32fb42920d8cc404b37cd25dc47cbc6fbde4d9f4 改为 token2ind O(1)。
>
> **•** 长路线另一个问题来自 GlobalRoutePathPlanner BFS target_depth=5。项目没有为赶结果大改全局 BFS，而是构造 depth-safe targeted scenarios，最终 route/refline 7/7 exact PASS。
>
> **•** Representative 阶段固定为“一场景一个 Python 进程”，避免大 semantic/bitmap 对象缓存、峰值内存和 stale state 跨场景污染。

## 7.3 CollisionLookup、车体几何与 bitmap additive-only

FullMine bitmap 是科研输入，不允许把 boundary fail 直接等价为“地图应该涂宽”。先用真实车体 footprint 与 exact predicate 判别 false positive / real physical gap，再做 additive patch；每个候选目录、manifest 和 SHA immutable。

| **历史对象**    | **真实意义**                                                                                |
|-----------------|---------------------------------------------------------------------------------------------|
| P0 baseline     | d2afc84e...；冻结基线，禁止原地修改。                                                       |
| candidate v1    | +112 pixels = 1.12 m²；历史诊断阶段。                                                       |
| candidate v2    | SHA 57514c52203aeca5c970d5a30086a58ddda7c1e179166ee3a26ff0435ed9bbd5；相对 P0 累计 +118px。 |
| V3              | 基于 A1/A2/B1/B2 actual shadow trajectory 的 exact patch；+724px。                          |
| V4 D-only       | 仅追加 3px，形成当前 bitmap runtime。                                                       |
| CollisionLookup | final SHA 10c1d1339e742ca893fedb4aa51402addfba82e16e08f68339ea35d35ba3043b。                |

## 7.4 A1 / A2 两类重要 planner 真根因

| **Case** | **错误中间判断 / 表象**                                    | **最终根因**                          | **最终修复**                                                                                                                     |
|----------|------------------------------------------------------------|---------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|
| A1       | 靠近 endpoint 停车，表面像 map/goal 问题                   | virtual endpoint 的几何 lead 约 4.5 m | 只把 virtual endpoint length_rear=0.0，不改地图/goal。                                                                           |
| A2       | 曾怀疑 leading-object / occupancy；endpoint 修复后仍停中段 | 高曲率下 steering-rate infeasible     | 按 curvature→steering，steering-rate 0.26 rad/s ×80%=0.208 反推局部 speed cap，再用 IDM decel_max 做 backward braking envelope。 |

最终 planner SHA：541ec74985d06322656e66c48abb382030d679171341408575d936e0a069e75e；behavior shadow A1/A2/B1/B2 = 308 / 555 / 523 / 330 steps，均按目标顺序到达 goal。

## 7.5 FullMine V4 正式冻结

| **冻结项**       | **当前值**                                                               |
|------------------|--------------------------------------------------------------------------|
| HEAD             | 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e                                 |
| Tag              | fullmine-vector-v4-runtime-freeze-20260814                               |
| Git status       | 反复实测 ?? ^C；历史异常未跟踪对象，禁止 git clean                       |
| Semantic SHA     | b85a3d8b28f2252ecb5bda179d514573f6333079def838cd048566f556d95cd0         |
| Bitmap SHA       | 51abcd5a86e5c510204a5dacc873691506d721f98982ab7f98585d4e0f7efdd0         |
| Final acceptance | targeted 7/7 PASS + old Jiangtong regression PASS                        |
| 严格口径         | Research / DEV baseline；production-authoritative drivability NOT PROVEN |

| **不能夸大** FullMine V4 可以称“可恢复、可复现、可承载算法实验的 Research Baseline”，不能称官方 production HD Map。现有 GeoJSON 不能唯一恢复 production internal exclusions。 |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# 8. 主线阶段五：代表区域验证与 Fleet-MCTS 双车联合规划、多种子验证

## 8.1 Representative Coverage / Pure MCTS

| **对象**                   | **冻结事实**                                                                                                                                                                                                                                  |
|----------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Representative Coverage v1 | COMPLETE + FROZEN WITH DOCUMENTED LIMITATIONS；tag fullmine-v4-representative-coverage-v1-20260814；freeze SHA bab9e77446e9c3b5747bb2721d035ca726b482418559b5f2a1018fe5e0018c5e。                                                             |
| Representative Pure MCTS   | 3/3 PASS + FROZEN；tag fullmine-v4-pure-mcts-representative-transfer-v1-20260814；freeze SHA 322e90d6995c410597d01925de6d77f1fd91ddb8c4c73a25c3e87446d37ac1fa；summary SHA 742d0716a00364a625e01b27c693134488211c8989e4996b072739c3a500d056。 |
| candidate-0010             | 017→012→018；formal goal step 83；0 collision/boundary；strict PASS。                                                                                                                                                                         |
| candidate-0002             | 394→395→397；step 182；0 collision/boundary；strict PASS。                                                                                                                                                                                    |
| recovery-0005              | 256→248→246；step 186；0 collision/boundary；strict PASS。                                                                                                                                                                                    |

## 8.2 Polygon21 benchmark 设计原则

Polygon21 是 frozen FullMine V4 中新选的 constructed physical-conflict benchmark：先用真实地图几何证明存在近同时冲突窗口；同一初始状态先跑 NO-MCTS causal baseline，再启用已经在 J117 验证的 Fleet-MCTS。PARAMETER_RETUNING=False。

| **资产**           | **路径 / SHA**                                                                                                                                                           |
|--------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Scenario           | /root/autodl-tmp/fullmine_v4_dual_candidate_v1/Scenario-fullmine-v4-polygon21-rank1-dual-aligned.json / 362eff18c7ccc88ea8dfaf083a517603566516943690d5cbe76bd1a97afc89e1 |
| Scenario manifest  | polygon21_rank1_dual_scenario_manifest_v1.json / 0bde6bb1e869c3cf583947203dd41a8fc364f0a2a8130617baebd0b1e6cbad2e                                                        |
| NO-MCTS result     | 060880c8edc851e05606871cb647058d091ce8737f952b9864cc94e9d6fcfd13                                                                                                         |
| Fleet seed0 result | 2eeb28e1fcb1c48d826c387853ec4f9a8a1acf07c9d7e7d1c067701bd4a1398f                                                                                                         |
| Fleet freeze v2    | b89d290c9cb06d1efb99688ee27b23898ab81d11e36023832477dc2fc834364b                                                                                                         |

## 8.3 NO-MCTS 物理冲突证据

> **•** baseline 固定 4.5 m/s；不允许 acceleration / waiting / artificial delay。
>
> **•** 按真实 XG90G footprint 每 0.1 s 做物理重叠检查。
>
> **•** A/B crossing time 约 11.11111 s，gap≈5.43e-7 s；首次 overlap 9.6 s；max overlap≈23.2148105 m² @ 10.7 s；min center distance≈0.296334 m。
>
> **•** 结论“无联合规划会冲突”来自真实 runtime/几何，不是静态示意图。

## 8.4 Fleet-MCTS seed0 与 5-seed

| **指标**                         | **seed0**                                          |
|----------------------------------|----------------------------------------------------|
| MCTS budget / depth              | 64 / 8                                             |
| duration / iterations            | 15.1 s / 151                                       |
| A cross                          | 7.319889502762444 s                                |
| B cross                          | 12.556499511428344 s                               |
| crossing gap                     | 5.2366100086659 s                                  |
| first to cross                   | A                                                  |
| min physical footprint clearance | 2.065002410173625 m                                |
| min center distance              | 8.19564529606273 m                                 |
| physical overlap / max overlap   | False / 0.0 m²                                     |
| timeline/speed/invalid           | sync=True；speed_cap_ok=True；nan_or_invalid=False |

| **5-seed 汇总**                | **结果**                                                     |
|--------------------------------|--------------------------------------------------------------|
| PASS / FAIL                    | 5 / 0                                                        |
| crossing gap min / mean / max  | 3.4379926855109115 / 7.473227083985728 / 14.40284379858401 s |
| minimum clearance across seeds | 1.2925053881999407 m                                         |
| first-to-cross                 | A:3；B:2                                                     |
| parameter retuning             | False                                                        |

## 8.5 Freeze v1 FAIL 的正确解释

第一次 freeze v1 的失败最终分类为 HARNESS_STATIC_SUMMARY_SCHEMA_MISMATCH，不是路线、NO-MCTS 或 Fleet-MCTS 科学结果失败。corrected freeze v2 才是正式锚点。v1 必须保留作为 harness 错误 provenance，但不得当最终结论。

# 9. 主线阶段六：原生 MineSim 可视化与汇报材料

用户的固定标准：汇报材料必须是科研证据可视化，不是 AI 重画或宣传海报。唯一允许的数据源是真实 MineSim cloud map、真实 scenario/runtime、冻结实验结果；禁止生成式道路、截图描线、坐标猜测、手工改科学轨迹。

## 9.1 双车原生可视化的状态真值问题

| **关键事实** \`EnvironmentSimulation.history\` 在 dual mode 主要保留 A 的 ego/history trajectory；受控 B 的权威状态由 \`MultiEgoRuntime\` 管理。不能直接把 SimulationHistory 当作 A+B 完整真值。 |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

Native V2 的正确方式：A 与原生 PlanVisualizer2D/history 同帧对齐；B 从同 iteration 的 MultiEgoRuntime live state 读取并叠加。producer 在每次 EnvironmentSimulation.propagate() 前抓取 runtime.state_for('A') 与 runtime.state_for('B')，并验证 A/history pose error ≤1e-8。没有 route_s 坐标重建、CSV 插值或像素反推。

## 9.2 Native Video V1 → V2

| **版本** | **真实问题 / 结果**                                                                                                                       | **状态**     |
|----------|-------------------------------------------------------------------------------------------------------------------------------------------|--------------|
| V1       | NO-MCTS raw dimensions (1545, 3666)，布局异常；科学链可跑但尺寸/视觉不满足正式汇报。                                                      | SUPERSEDED   |
| V2       | NO-MCTS/Fleet raw (1545,1073)；10 fps；NO-MCTS 145 frames；Fleet 151；side-by-side 145；collision frames 96–118；peak overlap frame 107。 | FINAL / PASS |

| **V2 Release** | **值**                                                                        |
|----------------|-------------------------------------------------------------------------------|
| ZIP            | /root/autodl-tmp/Polygon21_Native_MineSim_Report_Video_v2_20260816_161259.zip |
| SHA256         | f695ba22ecd61c4a643e8ffecac483bc218de9153f95f88b4e0e3006bca03d58              |
| Gate           | NATIVE_VIDEO_QUALITY_GATE=PASS / POLYGON21_NATIVE_MINE_SIM_VIDEO_RELEASE=PASS |

## 9.3 FullMine Map Showcase

| **版本** | **事实**                                                                                                                                                                                                    | **结论**                                           |
|----------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------|
| V1       | 错误假设 semantic 是 GeoJSON FeatureCollection；实际 MineSim semantic 是 custom dict；在 SHA/schema gate 主动停止。                                                                                         | FAILED DESIGN；正确失败方式是停止而不是猜 schema。 |
| V2       | 553 reference_path、402 borderline；Polygon21 真实几何；3×4K；1080p/15fps/120 frames；source/geometry/static/video quality PASS。ZIP SHA 9f78f357eecfc25ea543d163e8d472dc06abeb1fff3215ed30577267750d1e14。 | 当前历史稳定全局展示基线。                         |
| V3       | 只做视觉 hierarchy/panel/legend/camera；120/120 frame 已渲染；ffmpeg libx264 SIGKILL:9；无 final release。                                                                                                  | INCOMPLETE；不要把 SIGKILL 猜成已证实 OOM。        |

## 9.4 汇报四级 Gate 固化

> **1.** Scientific / Data Integrity：source SHA、frozen result、state alignment；不改科学数据。
>
> **2.** Geometry Authenticity：真实 semantic / footprint / conflict / polygon；不猜坐标。
>
> **3.** Technical Quality：分辨率、帧率、编码、文件完整性。
>
> **4.** Human Report Visual：PPT/大屏的层级、字号、路径/冲突点可读性。只有人工视觉也 PASS 才能 freeze formal final。

# 10. 主线阶段七：云端文件安全整理

目标不是“把目录弄漂亮”，而是在不删除科研证据、不破坏绝对路径、不改变 runtime symlink 的前提下，把约 530 个顶层对象压缩为可长期维护的结构。

| **Phase** | **动作**                                                          | **性质**                 |
|-----------|-------------------------------------------------------------------|--------------------------|
| 2A        | 222 历史 planner/report items → archive                           | 可恢复 move              |
| 2B        | 3 项 quarantine（npm-cache / DR restore test / malformed 0-byte） | 可恢复 quarantine        |
| 2C        | 28 旧 map-dev → archive；new_map_phase4c_tools 因真实引用保留     | move + HOLD              |
| 2D        | 广泛引用审计                                                      | read-only                |
| 2E        | exact path audit；高置信 safe candidates                          | read-only + org moves    |
| 2F        | 12 项 housekeeping / superseded media / GIF backup                | 可恢复 move              |
| 2G        | 大对象 inventory                                                  | read-only                |
| 2H        | 等价/唯一性关系审计                                               | read-only                |
| 2I        | 3 个 verified large duplicate/expanded artifacts                  | 可恢复 archive           |
| 2J        | 147 historical/debug/evidence top-level archive + regression      | 可恢复 move              |
| 2K        | HEAD/SHA/symlink/compile/restore/final health                     | read-only final closeout |

> **•** 最终 top-level count = 121。
>
> **•** 科研文件删除 = 0。
>
> **•** 约 423 个对象被 move/isolate；不是删除。
>
> **•** Phase2K final project health PASS；HEAD 仍 112d2bd...。
>
> **•** Phase2K closeout ZIP SHA：e3d4ba27bd06c74c7ca23ed55de65208022f07d4e0cb600eb58bcbbcaaf33a4b。

## 10.1 当前路径 Registry

| **逻辑对象**            | **当前路径**                                                          |
|-------------------------|-----------------------------------------------------------------------|
| formal repo             | /root/MineSim-Dynamic                                                 |
| Polygon21               | /root/autodl-tmp/fullmine_v4_dual_candidate_v1                        |
| cross-scene             | /root/autodl-tmp/fullmine_v4_fleet_cross_scene_v1                     |
| representative MCTS     | /root/autodl-tmp/fullmine_v4_mcts_representative_v1                   |
| representative coverage | /root/autodl-tmp/fullmine_v4_representative_coverage_v1               |
| production truth gap    | /root/autodl-tmp/fullmine_v4_production_truth_gap_v1                  |
| runtime current         | /root/autodl-tmp/fullmine_vector_v2_targeted_runtime                  |
| semantic source         | /root/autodl-tmp/new_map_fullmine_vector_v2_dev                       |
| bitmap source           | /root/autodl-tmp/fullmine_vector_v4_d_current_planner_patch_candidate |
| MCTS results            | /root/autodl-tmp/mcts_results                                         |
| IDM backup              | /root/autodl-tmp/minesim_idm_baseline_backup                          |
| archive                 | /root/autodl-tmp/90_MineSim_ARCHIVE                                   |
| quarantine              | /root/autodl-tmp/98_MineSim_QUARANTINE                                |
| cleanup manifests       | /root/autodl-tmp/99_MineSim_CLEANUP_MANIFEST                          |

runtime semantic symlink 必须继续解析到 Vector V2 semantic source；bitmap symlink 必须解析到 V4 D current planner patch candidate。绝对路径依赖的 frozen runner 优先通过恢复历史路径解决，不要直接改 frozen runner。

## 10.2 Restore 入口

| **Phase** | **Restore script**                                                                                |
|-----------|---------------------------------------------------------------------------------------------------|
| 2A        | /root/autodl-tmp/99_MineSim_CLEANUP_MANIFEST/phase2a_safe_move_20260816_165421/RESTORE_PHASE2A.sh |
| 2B        | .../phase2b_safe_quarantine_20260816_170221/RESTORE_PHASE2B.sh                                    |
| 2C        | .../phase2c_safe_map_archive_20260816_170828/RESTORE_PHASE2C.sh                                   |
| 2F        | .../phase2f_safe_housekeeping_20260816_172708/RESTORE_PHASE2F.sh                                  |
| 2I        | .../phase2i_safe_large_archive_20260816_174051/RESTORE_PHASE2I.sh                                 |
| 2J        | .../phase2j_final_safe_archive_20260816_174626/RESTORE_PHASE2J.sh                                 |

恢复原则：先确认原路径没有新的同名对象；按原 manifest/RESTORE 脚本逆向恢复；恢复后复核 HEAD/status、关键 SHA、runtime symlink。

# 11. 2026-08-17 工程扩展：FullMine 仿真/可视化中间层 MVP

该阶段发生在云端整理之后，但属于“原生可视化与汇报材料”的工程延伸。用户优先选择先做轻量中间层 MVP，再返回多车科学。它的目标不是替换 MineSim 内核，而是把 MineSim/MultiEgoRuntime/Planner 的零散对象统一成可重放、可重复渲染、可审计的 Snapshot。

MineSim / EnvironmentSimulation / MultiEgoRuntime / Planner  
↓  
FullMineStateAdapter  
↓  
SimulationSnapshot V0  
↓  
SourceManifest + RenderProfile  
↓  
FullMine Renderer  
↓  
4K PNG / 1080p MP4 / GIF / replay

| **当前能力** 同一份冻结科学数据可反复按 Research / Report / Video 方式渲染，只改变视觉层与 camera；无需重跑算法，也不会改道路、车辆、轨迹、冲突点或指标。 |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------|

## 11.1 SimulationSnapshot V0 / StateAdapter

> **•** 根目录：/root/autodl-tmp/fullmine_snapshot_middleware_v0；静态 build：build_20260817_131429。
>
> **•** schema：FullMineSimulationSnapshotV0；Vehicle/Planning/Safety/SimulationSnapshot dataclass；capture_pre_propagate()；JSONL writer。
>
> **•** footprint 只使用真实暴露的 car_footprint，不重建；可选缺失字段写 None 并保留 source metadata。
>
> **•** report profile 固化 4K/1080p 与四级 Gate 标准。

## 11.2 Live smoke 为什么没有作为正式能力

第一次 one-step live Fleet-MCTS middleware smoke 在 snapshot 前 RC137。低资源 cgroup 当时 memory.max=2 GiB，memory.events 的 max/oom/oom_kill 均为 0，且 guard hashes/冻结文件未变。因此当时只能写“external SIGKILL / cause unknown”，不能直接写 OOM。随后为了不破坏科学冻结链，改用已有 Native V2 frozen logs 做 offline adapter。

| **边界** 因此目前中间层正式验证的是冻结/离线真实数据链；live adapter 设计存在，但 live capture 未正式 PASS，不能宣称实时中间层已生产可用。 |
|--------------------------------------------------------------------------------------------------------------------------------------------|

## 11.3 OfflineAdapter V0：151 帧真实同步

| **指标**                      | **结果**                                                                            |
|-------------------------------|-------------------------------------------------------------------------------------|
| Output                        | /root/autodl-tmp/fullmine_snapshot_middleware_v0/offline_adapter_v0_20260817_133207 |
| Snapshot count                | 151                                                                                 |
| A history↔dual pose max error | 0.0                                                                                 |
| history↔dual time error       | 0.0                                                                                 |
| DT errors                     | 0                                                                                   |
| collision frames              | 0                                                                                   |
| max overlap                   | 0.0 m²                                                                              |
| min frame clearance           | 2.065002410173625 m                                                                 |
| A action counts               | {0:3, 1:13, 2:38, 3:97}                                                             |
| B action counts               | {0:10, 1:19, 2:37, 3:85}                                                            |
| Snapshot SHA                  | cf69851a5844866f8a3c30814d6ec4e10dcf5f9f1703b20b5616f728749e487e                    |
| Package SHA                   | 7f2f27037d87c829ffbe17d27515eb617d7c417a9806b1a1ba04c1e19fc7be87                    |

## 11.4 Renderer V0 → V0.1：真实失败与修复

| **问题**               | **错误原因**                                                             | **修复 / 结论**                                                                                                          |
|------------------------|--------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------|
| Conflict XY 不显式存在 | V0 假设 conflict source 有直接 XY；冻结 manifest 实际给 conflict_route_s | 用真实 semantic reference_path.waypoints + exact route station 计算 A/B conflict point，再取同一点；禁止 hardcode/猜测。 |
| Recovery KeyError: OUT | 环境变量没透传                                                           | 补齐 OUT；以后 wrapper 先做 required env gate。                                                                          |
| Polygon21 529 vs 530   | raw link_node_tokens 只有 529 unique，V0 误认为应有 530 real nodes       | 真实语义：529 raw semantic nodes + 重复第一个真实 node 做闭合 = 530 plotting coordinates。                               |
| V0 human visual FAIL   | 数据正确但地图线权重弱、层级/留白不适合 PPT                              | V0.1 只改 visual hierarchy/crop/font/legend/line weight；scientific constant patch count=0。                             |

> **•** 冻结冲突点：(4296.468635820087, 1754.2755686857276)；A/B semantic route station 解析结果一致，separation=0。
>
> **•** Renderer V0.1 三张图均 3840×2160；自动 Gate1/2/3 PASS；上传后人工逐图检查 Gate4 PASS。
>
> **•** V0.1 review ZIP SHA：6ceb9c2a5c133c57497c5f2ec74f3e97f94fe8193f8cf98a979768df3d3a6080。

## 11.5 Renderer 正式冻结

| **对象**            | **值**                                                                                                       |
|---------------------|--------------------------------------------------------------------------------------------------------------|
| Freeze dir          | /root/autodl-tmp/fullmine_snapshot_middleware_v0/frozen_renderer_v01_20260817_140210                         |
| Freeze manifest SHA | bd8f2e02d85572bdb024417d62f689bcf1bdd47929d9072b44287fb149f9ae5b                                             |
| Frozen ZIP          | /root/autodl-tmp/fullmine_snapshot_middleware_v0/FullMine_Middleware_Renderer_V01_FROZEN_20260817_140210.zip |
| Frozen ZIP SHA      | da56e3cd7cb1c23759cb7db7308acbd19614f31f9dd5c698807752828018993e                                             |
| Gate                | Scientific / Geometry / Technical / Human Visual = PASS                                                      |
| Repo effect         | HEAD unchanged；scientific/geometry change=0                                                                 |

## 11.6 Video V0.1 → V0.2

| **版本** | **结果**                                                                                                   | **人工视觉结论**                                                           |
|----------|------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------|
| V0.1     | 1920×1080 / 15fps / 120 frames / 8.0s；technical PASS                                                      | FAIL：约 2.8–3.4 s center+log zoom 经过大面积空白区。                      |
| V0.2     | target-anchored camera；start/end view 不变；Polygon21 real conflict point 始终留在有效视野；1.5+2.7+3.8 s | PASS：5 keyframes + 多时间点完整 MP4 检查；过渡顺滑，最终局部 dwell 足够。 |

> **•** V0.2 video SHA：efb1e90cf501a5d906f4457e5b2365ee2b007025fa464e635fcb5b6cb50c20d3。
>
> **•** Review ZIP SHA：b3e0ea5a54023e50c283b235a0901ed3e5c9702e51eff9de3c56db69d2a92e22。
>
> **•** Camera target screen anchor：global (0.7515175, 0.4126291) → local (0.5754677, 0.4491774)；只改变 viewport。

| **Video freeze**    | **值**                                                                                         |
|---------------------|------------------------------------------------------------------------------------------------|
| Freeze dir          | /root/autodl-tmp/fullmine_snapshot_middleware_v0/frozen_video_v02_20260817_142048              |
| Master manifest SHA | fd1e18f8f5382c9cb106b26a060f09ebf948d729d0532250da816e97c40585b8                               |
| Frozen ZIP          | /root/autodl-tmp/fullmine_snapshot_middleware_v0/FullMine_Video_V02_FROZEN_20260817_142048.zip |
| Frozen ZIP SHA      | ff4c15aa414eda1a863a878bc835207b79ce69882ae2a7375c4728a8808f9bb0                               |
| Four gates          | PASS                                                                                           |

## 11.7 中间层现在能实现什么 / 不能实现什么

| **能力**                                 | **当前状态**                                                                       |
|------------------------------------------|------------------------------------------------------------------------------------|
| 真实冻结双车状态标准化                   | PASS：151-frame A/B state、footprint、planning/action、安全字段 → Snapshot JSONL。 |
| 离线重放 / 重复渲染                      | PASS：同一 frozen source 可重复出 Research/Report/Video，不重跑算法。              |
| 真实地图全局→Polygon21 局部定位          | PASS：4K 图片 + 1080p/8s camera-only video。                                       |
| 科学 provenance / SHA / 4 gates          | PASS：source manifest、freeze manifest、human gate 已固化。                        |
| 实时 live adapter                        | HOLD：one-step live smoke RC137，未正式通过。                                      |
| 实时 GUI / pause / step / planner switch | NOT IMPLEMENTED。                                                                  |
| 任意多车 N 车辆通用化                    | 未验证：当前正式验证是 Polygon21 A/B 双车。                                        |
| Neural planner 显示接入                  | NOT STARTED；架构预留但未训练/接入。                                               |

# 12. 2026-08-17 当前科学主线：FullMine Cross-scene Fleet-MCTS

中间层 freeze 后立即返回多车科研。旧 handover 中“cross-scene 只到 static readiness”仍成立，但 2026-08-17 已开始 C04 dynamic real-loader，并得到新的资源与数据契约证据。

| **对象**         | **当前状态 / 证据**                                                        |
|------------------|----------------------------------------------------------------------------|
| Cross-scene root | /root/autodl-tmp/fullmine_v4_fleet_cross_scene_v1                          |
| Final set        | C04 / C11 / C06                                                            |
| Static readiness | A/B 共 6 路线 PASS；classification PASS_FINAL_SET_4_11_6_ALL_DIRECT_STATIC |
| Dynamic results  | 尚未形成 PASS；C04 loader 当前 FAIL/HOLD；C11/C06 未跑                     |

## 12.1 真实 runner 与依赖顺序

| **Runner**                               | **SHA / 关键约定**                                                                                        |
|------------------------------------------|-----------------------------------------------------------------------------------------------------------|
| cross_scene_real_loader_smoke_v3.py      | bdae2b0dfbcf2bcd19d9508eb3446814010dee788c5a832fe3be4aaa3c8a8ac8                                          |
| cross_scene_nomcts_causal_conflict_v3.py | 36d2a706ad622ebb5ddbf0806a611b4fb161386be3897397add0abb63637037d                                          |
| cross_scene_fleet_mcts_v2.py             | 00ab3c26bf42be09a3c4b6d0ec7f952bde3f22cfaead30bf5d61f67927e51f3b; MCTS_DT=0.5, budget=64, depth=8, --seed |
| Dependency gate                          | Fleet runner 先读取 canonical loader result + NO-MCTS result 并 evidence_pass()；不能跳过。               |

## 12.2 C04 冻结输入

| **项**           | **值**                                                                                  |
|------------------|-----------------------------------------------------------------------------------------|
| Scenario         | scenarios_c04_augmentation_v1/Scenario-fullmine-v4-cross-scene-c04-dual-aligned-v1.json |
| Scenario SHA     | a207a7fc6a191b880460fdefb3e03d0a4592603f8ef6a13d0c7de530d243e0ca                        |
| Manifest         | cross_scene_c04_scenario_manifest_v1.json                                               |
| Manifest SHA     | 0b1d836e1b8d44c93948d850dacfbb086c24471b004b78025f4bd5c9f17a149c                        |
| Route A          | path-000395 → path-000397 → path-000398                                                 |
| Route B          | path-000402 → path-000406 → path-000407                                                 |
| start_route_s    | A=61.19948215578566；B=128.29262421920427                                               |
| conflict_route_s | A=131.19948215578566；B=198.29262421920427                                              |
| static A/B       | both PASS                                                                               |

## 12.3 绝对环境依赖恢复

> **•** SEM = runtime semantic path；MAP_ROOT = runtime /maps；DATA_ROOT = runtime root。
>
> **•** CLASS_FILE = /root/MineSim-Dynamic/devkit/scenario_builder/minesim_scenario_json/minesim_dynamic_scenario.py。
>
> **•** BREF 主科研副本 = /root/autodl-tmp/fullmine_v4_dual_candidate_v1/polygon21_b_reference_chain_audit_v1.json；SHA 39f29de451ff64a418cdc78abdafedc568db7efffe7380064c95a8026612040e；另有 middleware guard backup 同 SHA。
>
> **•** MINESIM_DATA_ROOT / MINESIM_MAPS_ROOT 是 runner 内部 store，不是额外历史外部事实；早期 AST 检测把 store 也当 required read，已纠正。

## 12.4 低内存 RC137：现在能说什么，不能说什么

| **证据**                 | **值**                                                                              |
|--------------------------|-------------------------------------------------------------------------------------|
| low-resource memory.max  | 2,147,483,648 bytes（2 GiB）                                                        |
| trace death stage        | scenario.map_api → MineSimMapFactory → MineSimMap.load_bitmap_using_utm_local_range |
| max process RSS observed | ≈1595.13 MiB                                                                        |
| max cgroup observed      | ≈1.980 GB = 92.20% of 2 GiB                                                         |
| memory.events delta      | max=0 / oom=0 / oom_kill=0                                                          |
| exit                     | 137 / external SIGKILL                                                              |

| **准确结论** 当时不能写“已证实 OOM”；但后续 80 GiB 实例同一路径实际用到约 2.59 GiB cgroup 并越过 map load，已经实验性证明 2 GiB 环境不足以完成这条 loader 路径。SIGKILL 的内核/平台具体机制仍未验证。 |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

## 12.5 高内存复现：暴露真正软件 blocker

| **项**                     | **真实输出**                                                                                                                   |
|----------------------------|--------------------------------------------------------------------------------------------------------------------------------|
| High-memory cgroup         | 80.00 GiB                                                                                                                      |
| source identity            | loader / BREF / semantic SHA 全 PASS                                                                                           |
| resource peak              | process RSS≈2297 MiB；cgroup≈2589 MiB                                                                                          |
| map stage                  | 已成功越过此前 2 GiB 的 map/bitmap load                                                                                        |
| Frame0                     | object count=1；tokens=\['object-1'\]                                                                                          |
| Exit                       | RC=1                                                                                                                           |
| Error                      | TypeError: float() argument must be a string or a number, not 'list'                                                           |
| A/B route_s / speed / time | 均尚未赋值（None）                                                                                                             |
| FAIL report SHA            | adaa61f354a1ab3da03e413e7f1adb467bb71b40374763b8d1c158bcd1f2c8eb                                                               |
| Canonical path             | /root/autodl-tmp/fullmine_v4_fleet_cross_scene_v1/cross_scene_real_loader_reports_v2/cross-scene-c04-real-loader-smoke-v2.json |

| **当前停止点** 现在没有证据支持运行 C04 NO-MCTS。canonical-named loader report 当前是 FAIL 证据，不能因为文件存在就让 Fleet 当作通过。下一步先精确定位 \`float(list)\` 的原始行与数据形状。 |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

## 12.6 下一步最小行动与完成标准

> **1.** 继续使用高内存实例（重连后先查 cgroup；当前已证明 2 GiB 不够）。CUDA 计算仍关闭，卡的价值是 80 GiB RAM / CPU quota。
>
> **2.** 保留当前 FAIL report；建立临时 diagnostic runner copy，只增加 \`traceback.print_exc()\`，不改科学逻辑、不改地图、不改正式 repo。
>
> **3.** 运行 \`--source-index 4\`，得到准确 traceback、failing original line、source context、相关 manifest/scenario 字段的 type/shape。
>
> **4.** 只在临时 runner copy 修复 scalar/list 数据契约兼容点；loader 必须输出 \`REAL_LOADER_GATE=PASS\`，A/B route_s/speed/time 正常、checks 全 PASS。
>
> **5.** 只有 loader PASS 后，才跑 C04 NO-MCTS causal conflict；NO-MCTS 必须确认真实物理冲突并完成 post-conflict。
>
> **6.** 再运行 Fleet-MCTS seed0；满足 collision avoided / timeline sync / no invalid / speed cap / benchmark success 后才扩展 seeds。
>
> **7.** C04 完整后再复用到 C11/C06；不要三个场景一起长跑。

# 13. 重要故障、排查链与“以后不能再重复”的做法

| **故障 / 现象**                | **根因 / 当前分类**                                 | **解决 / 当前动作**                             | **以后不能再做**                                       |
|--------------------------------|-----------------------------------------------------|-------------------------------------------------|--------------------------------------------------------|
| Frenet step150 IndexError      | trajectory resample interface 越界，不是搜索无轨迹  | 安全重采样/adapter                              | 先分 Planner search vs adapter failure。               |
| dual 受控车重复                | A/B 同时留在 external observation                   | filter controlled from observation              | 受控 actor 必须从 external 剔除。                      |
| B 车原生视频缺失               | SimulationHistory 主要是 A                          | same-iteration MultiEgoRuntime live B overlay   | 绝不能用 A history 假装 A+B。                          |
| Jiangtong 空间交叉但无冲突     | ETA 差≈9.496s                                       | 负筛选并冻结                                    | 空间交叉不等于联合决策 benchmark。                     |
| CollisionLookup boundary fail  | 离散 lookup 可能 false positive                     | 真实 CarFootprint/exact geometry truth-check    | 禁止看到 FAIL 就涂宽 bitmap。                          |
| B2 fixed offset/yaw footprint  | 固定外推制造假缺口                                  | 只用 actual controller/shadow trajectory        | 禁止人工外推真实后续 footprint。                       |
| A1 endpoint                    | virtual lead geometry                               | length_rear=0.0 on virtual endpoint             | 不改 map/goal掩盖 planner endpoint 语义。              |
| A2 中途停车                    | 最终是 high-curvature steering-rate infeasible      | curvature speed cap + backward braking envelope | 中间假设必须允许被后续证据推翻。                       |
| FullMine planner init 慢       | semantic token linear lookup                        | token2ind O(1)                                  | 不要先假设 GPU 不够。                                  |
| Map Showcase V1                | 错误把 custom semantic 当 FeatureCollection         | schema audit + V2                               | source gate 后不猜 schema。                            |
| Map Showcase V3 ffmpeg SIGKILL | 外部 kill；无直接 OOM 证据                          | 保留 frames；独立低内存 encoder 是正确方向      | 没有 memory.events 证据不要写 OOM。                    |
| Native Video V1 dimensions     | 原生画布/布局错误 (1545,3666)                       | V2 (1545,1073) + 重新 release                   | 科学 PASS 不能代替视觉/技术 Gate。                     |
| Renderer conflict XY           | 冻结数据只给 route_s                                | 真实 semantic route-station evaluation          | 禁止 hardcode/猜冲突坐标。                             |
| Polygon21 529/530              | raw nodes 与 plotting closure 混淆                  | 529 real + first node repeat = 530              | 闭合点不等于额外真实 node。                            |
| Video V0.1 中段空白            | center pan 与 log zoom 独立插值                     | V0.2 target-anchored camera                     | 视觉失败只改 camera，不动科学几何。                    |
| 缺 SEM / BREF / CLASS_FILE     | 历史 runner 绝对 env 依赖                           | 从 manifest/SHA/source 恢复                     | 不猜路径；优先恢复历史路径。                           |
| AST required-env 误判          | 把 os.environ\[...\] = store 当 read                | 区分 AST Load/Store                             | 环境审计要区分读写上下文。                             |
| 2 GiB C04 loader RC137         | FullMine map load 内存压力；具体 SIGKILL 机制未证实 | 80 GiB 复现实验证实完整 path \>2GiB             | cgroup 为资源真值；大 map 动态任务不要在 2GiB 反复撞。 |
| C04 highmem TypeError          | float(list)，尚未精确定位原始行                     | HOLD：下一步 traceback-only diagnostic copy     | 未定位前禁止改 core/map 或跑 NO-MCTS。                 |
| 长 heredoc/终端乱码            | 前端拼接/复制混入输出                               | 短 ASCII block、子 shell、明确 gate             | 不要用裸 exit；不要让失败关闭 SSH。                    |
| 冻结结果文件存在 ≠ PASS        | 当前 C04 canonical-named report 就是 FAIL           | 读 status/PASS/checks/SHA                       | 下游 evidence gate 必须验证内容而非存在性。            |

## 13.1 资源与进程隔离的永久经验

> **•** free -h / nproc 可能显示宿主机 1TiB/192 CPU，不能作为容器资源真值；优先读 /sys/fs/cgroup/memory.max, memory.current, memory.events, cpu.max。
>
> **•** FullMine semantic/bitmap 很大；批量多场景时优先一场景一个 Python 进程，记录独立 rc/log/RSS/exception。
>
> **•** ffmpeg 最好在 Python semantic/map 对象退出后单独进程编码，降低峰值内存；但任何 SIGKILL 仍要读 cgroup 证据再归因。
>
> **•** 高资源 GPU 卡常常是为了获得 15 vCPU / 80 GiB RAM quota；地图、Shapely、Rasterio、Pillow、ffmpeg 主要是 CPU/RAM，CUDA_VISIBLE_DEVICES="" 仍然正确。

# 14. 当前有效版本、废弃/归档版本与 HOLD

## 14.1 当前有效 / 正式版本

| **对象/阶段**               | **状态**          | **当前准确结论**                                          |
|-----------------------------|-------------------|-----------------------------------------------------------|
| FullMine source runtime     | **PASS / FROZEN** | 112d2bd... / V4 tag / semantic b85a... / bitmap 51abcd... |
| Representative Pure MCTS    | **PASS / FROZEN** | 3/3 / freeze 322e90... / summary 742d07...                |
| Polygon21 science           | **PASS / FROZEN** | NO-MCTS + Fleet 5/5 / freeze v2 b89d29...                 |
| Native MineSim report video | **PASS / FROZEN** | V2 SHA f695ba...                                          |
| Map Showcase                | **PASS**          | V2 是稳定历史展示基线；V3 不作为 final。                  |
| Middleware static           | **PASS / FROZEN** | Renderer V0.1 freeze manifest bd8f... / ZIP da56...       |
| Middleware video            | **PASS / FROZEN** | Video V0.2 master fd1e... / ZIP ff4c...                   |

## 14.2 Superceded / historical provenance

| **对象**                               | **状态**             | **为什么不能作为当前版本**                                   |
|----------------------------------------|----------------------|--------------------------------------------------------------|
| IDM baseline / 94693dc MCTS            | HISTORICAL/FROZEN    | 重要回归/算法证据，但不是当前 FullMine source HEAD。         |
| FullMine V1                            | HISTORICAL           | 保守 structural/DEV mask，被 Vector V2/V4 功能结论覆盖。     |
| P0 / bitmap candidate v1/v2            | IMMUTABLE HISTORICAL | 诊断与 additive provenance；禁止覆盖。                       |
| stale v3_targeted_7of7_acceptance.json | INVALID / DO NOT USE | 混用旧结果世代；final 7/7 以 current-planner manifest 为准。 |
| Fleet freeze v1                        | HISTORICAL FAIL      | harness static-summary schema mismatch；final freeze v2。    |
| Native Video V1                        | SUPERSEDED           | 尺寸/layout 异常；final V2。                                 |
| 旧 Polygon21 GIF                       | BACKUP ONLY          | 不是当前 Native / middleware 正式视频。                      |
| Map Showcase V1                        | FAILED DESIGN        | 错误 FeatureCollection 假设。                                |
| Map Showcase V3                        | INCOMPLETE           | 120 frames complete，encoding failed，无 final release。     |
| Renderer V0                            | HISTORICAL           | auto科学/几何后来通过，但 Human Visual 不达标；final V0.1。  |
| Video V0.1                             | SUPERSEDED           | technical PASS、Human Visual FAIL；final V0.2。              |

## 14.3 明确 HOLD / 不可擅动

> **•** /root/autodl-tmp/MineSim-Dynamic：独立脏历史工作区；不是正式 repo；不能删。
>
> **•** new_map_phase4c_tools：存在真实引用，HOLD。
>
> **•** new_map_phase6c_full_mine_structural：历史依赖/保护链，HOLD。
>
> **•** fullmine_vector_v4_final_dr_20260814.tar.gz：compact DR 恢复证据，保留。
>
> **•** 98_MineSim_QUARANTINE：隔离不等于删除授权。
>
> **•** ?? ^C：历史未跟踪异常对象；禁止为了“clean”执行 git clean。
>
> **•** Production-authoritative FullMine drivability：NOT PROVEN。
>
> **•** 真实 FullMine 现场车型是否等同当前 XG90G：未权威确认；如不同需新 vehicle config + footprint/mask re-eval。
>
> **•** gear=-1 运营语义、elevation datum、official slope smoothing：未权威确认。
>
> **•** Cross-scene C04/C11/C06 dynamic：HOLD，当前 C04 loader 尚未 PASS。
>
> **•** Neural-MCTS training：NOT STARTED。

# 15. 运行环境、依赖关系与资源模型

| **环境项**         | **当前证据**                                                                                    |
|--------------------|-------------------------------------------------------------------------------------------------|
| 正式工作目录       | /root/MineSim-Dynamic                                                                           |
| Conda              | minesim                                                                                         |
| 正式 Python        | 3.9.25                                                                                          |
| 付费高资源实例镜像 | PyTorch 2.1.0 / Python3.10 base / Ubuntu22.04 / CUDA12.1 / RTX4090D24GB；实际 minesim 仍 3.9.25 |
| 高资源 quota       | 实测 cgroup memory.max=80 GiB；历史约 15 vCPU                                                   |
| 低资源 quota       | 实测 memory.max=2 GiB；不适合 FullMine dynamic map load                                         |
| GPU 使用原则       | 先 CUDA_VISIBLE_DEVICES=""；除正式 NN 训练等确实需要 CUDA 的阶段，不默认使用 GPU compute        |

## 15.1 每次可执行云端代码的固定前缀

cd /root/MineSim-Dynamic  
source /root/miniconda3/etc/profile.d/conda.sh 2\>/dev/null \|\| true  
conda activate minesim  
export PYTHONPATH=/root/MineSim-Dynamic

CPU/静态工作通常随后再 export CUDA_VISIBLE_DEVICES=""。交互顶层禁止裸 exit；需要失败终止时放进子 shell (...) 或打印 FAIL / 返回码。

## 15.2 Runtime symlink / absolute path 恢复规则

> **•** semantic runtime：/root/autodl-tmp/fullmine_vector_v2_targeted_runtime/maps/semantic_map/... 应解析到 /root/autodl-tmp/new_map_fullmine_vector_v2_dev/...。
>
> **•** bitmap runtime：.../maps/bitmap/geojson_full_mine_vector_v2_dev_bitmap_mask.png 应解析到 /root/autodl-tmp/fullmine_vector_v4_d_current_planner_patch_candidate/bitmap/...。
>
> **•** 冻结 runner 若依赖历史绝对路径：优先通过 cleanup manifest / restore script 恢复原路径；禁止直接批量替换 frozen runner。
>
> **•** C04 当前 loader env 必须包含 SEM/MAP_ROOT/DATA_ROOT/CLASS_FILE/BREF；这些来源已通过 manifest/SHA/source 恢复，不需要再次全盘搜索。

# 16. ChatGPT / 用户 / Codex 的协作工作流（长期固化）

| **角色 / 场景**      | **固定职责**                                                                              |
|----------------------|-------------------------------------------------------------------------------------------|
| ChatGPT              | 分析真实输出、做决策、设计最小下一步、写关键 shell/Python、解释 PASS/FAIL、维护事实边界。 |
| 用户                 | 复制命令到 AutoDL 执行、返回真实终端/文件/图像；决定是否开付费高资源卡；保留最终控制权。  |
| Codex                | 只用于复杂算法设计、顽固 bug、关键结论复核、明确边界且适合云端自主执行的繁琐工作。        |
| 免费 Shell/Python    | Git/status/hash/path/file/process/schema/机械检查、简单转换、打包、ffprobe 等；不用模型。 |
| 普通 terminal/screen | 长 build / 长仿真；Codex 不等待长作业。                                                   |

## 16.1 Codex 模型与成本策略

> **•** 默认 gpt-5.6-luna medium。
>
> **•** 中等复杂多模块联调才考虑 Terra；核心算法/关键终审才考虑 Sol。
>
> **•** 每个 Codex job 只解决一个最小问题；输出 PASS/FAIL + 必要字段，不要长篇报告。
>
> **•** 已知事实不重复问模型；已验证阶段不重审；机械真值用 Shell/Python。
>
> **•** 先免费把 preflight、数据准备、schema、路径、hash 全做完，再开高资源卡；高卡先用于 RAM/CPU quota，GPU compute 另行判断。

## 16.2 强制实验阶梯

> **1.** 只读 preflight：环境、HEAD/status、路径、SHA、依赖、输入文件。
>
> **2.** 单步 smoke：syntax/import/toy function/1–5 step，只确认接口。
>
> **3.** 短闭环：几十步/小场景，只验证 blocker 是否关闭。
>
> **4.** 完整实验：前面 gate PASS 后才跑 full / 多 seed / 高资源。
>
> **5.** Freeze：result + manifest + SHA + tag（必要时）+ regression；freeze 后默认不重做。

| **原则** 项目安全和可复现优先于目录美观、少花几分钟或“看起来进展快”。每次只推进一个最小步骤，失败只处理当前 blocker。 |
|-----------------------------------------------------------------------------------------------------------------------|

## 16.3 Git / 文件纪律

> **•** commit 前：git diff --check、git diff --name-only、git diff --cached --name-only。
>
> **•** 只允许 git add \<exact files\>；禁止 git add .。
>
> **•** 禁止 git clean -fd、禁止 reset --hard 处理“看不顺眼”的历史状态。
>
> **•** bitmap candidate / freeze asset 一旦有 manifest/SHA 即 immutable；新修复建立新目录/新 SHA。
>
> **•** 大文件、logs、temporary scripts、results 放 /root/autodl-tmp；正式 repo 只保留必要 source。

# 17. 主线阶段八：后续神经网络 / Neural-MCTS 接入

| **当前状态** 正式训练 NOT STARTED。不能把 448 expert samples、representative raw logs 或现有 PyTorch/Lightning 组件写成已训练 Value/Policy 网络。 |
|---------------------------------------------------------------------------------------------------------------------------------------------------|

现有 MCTS 结构已经把 simulator adapter 与 tree search 分开，Neural 阶段不应重写 planner/simulator。当前路线在 cross-scene 动态线完成后进入数据治理，然后优先 Value Network。

> **1.** 只读 inventory：Dapai/Jiangtong 448 strict expert + FullMine representative raw logs；每个 source/episode/scenario/result/freeze SHA 可追溯。
>
> **2.** 冻结 dataset contract：state features、action index、root visit distribution、Q/reward、return/value label、obstacle snapshot、normalization/provenance。
>
> **3.** 按 formal goal history 截断；清除 smoke、重复、post-goal；candidate-0010 等禁止把 goal 后记录混入 clean data。
>
> **4.** 按 scenario / episode 做 train/validation/test split；禁止随机逐行 split 造成时序泄漏。
>
> **5.** 输出 clean dataset manifest：输入 SHA、保留/删除计数与理由、split group、schema version、输出 SHA。
>
> **6.** CPU parser / one-batch / small-model smoke；全部 PASS 后再开 GPU 正式训练。
>
> **7.** 第一模型优先 Value Network → Value-guided MCTS；随后 Policy+Value / PUCT；再研究 adaptive budget / tree reuse。

网络层数、hidden size、最终 reward 权重目前没有冻结证据，下一位 AI 不得凭经验自行“定参数”。

# 18. 关键 Commit / Tag / SHA / Freeze 速查

| **里程碑**                          | **Commit / Tag / SHA**                                                                  |
|-------------------------------------|-----------------------------------------------------------------------------------------|
| IDM baseline                        | 2521aa41a69a6e734c04c15a715e9530c8095ac3 / idm-replay-autodl-baseline                   |
| Pure MCTS + expert                  | 94693dc799fe5f325a75e8fc6d7d5e88764b4799 / mcts-expert-dataset-v1-20260802              |
| Fleet internal reward historical    | f8ff1866789ed3d9d878f34b7cd34ab490e40121                                                |
| Jiangtong V22 screening             | 94794c963f9c3eaf1873b275df6d319ca2636817 / jiangtong-v22-benchmark-screening-20260809   |
| J117 Phase3                         | 4bd2bff28c593ee80ab8c9fe2eefecd2b009e9b6 / j117-phase3-production-map-load-20260809     |
| J117 Phase4C base                   | ec1c958735b0ee76201284faacb46fccc75c7f6c / j117-phase4c-single-ego-closed-loop-20260810 |
| J117 Phase5                         | da4105b836dbbd3e702ee25fbb364109bc4e2596 / j117-phase5-dual-ego-pure-mcts-20260810      |
| FullMine lookup                     | 32fb42920d8cc404b37cd25dc47cbc6fbde4d9f4                                                |
| FullMine V1                         | d81c57154e4e5d0b4df1251cf565d9aacffaa026 / fullmine-dev-runtime-pass-20260811           |
| CURRENT FullMine V4                 | 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e / fullmine-vector-v4-runtime-freeze-20260814   |
| Semantic                            | b85a3d8b28f2252ecb5bda179d514573f6333079def838cd048566f556d95cd0                        |
| Bitmap                              | 51abcd5a86e5c510204a5dacc873691506d721f98982ab7f98585d4e0f7efdd0                        |
| CollisionLookup                     | 10c1d1339e742ca893fedb4aa51402addfba82e16e08f68339ea35d35ba3043b                        |
| IDM planner final                   | 541ec74985d06322656e66c48abb382030d679171341408575d936e0a069e75e                        |
| Representative Pure MCTS summary    | 742d0716a00364a625e01b27c693134488211c8989e4996b072739c3a500d056                        |
| Representative Pure MCTS freeze     | 322e90d6995c410597d01925de6d77f1fd91ddb8c4c73a25c3e87446d37ac1fa                        |
| Polygon21 scenario                  | 362eff18c7ccc88ea8dfaf083a517603566516943690d5cbe76bd1a97afc89e1                        |
| Polygon21 NO-MCTS                   | 060880c8edc851e05606871cb647058d091ce8737f952b9864cc94e9d6fcfd13                        |
| Polygon21 Fleet seed0               | 2eeb28e1fcb1c48d826c387853ec4f9a8a1acf07c9d7e7d1c067701bd4a1398f                        |
| Polygon21 Fleet freeze v2           | b89d290c9cb06d1efb99688ee27b23898ab81d11e36023832477dc2fc834364b                        |
| Native Video V2                     | f695ba22ecd61c4a643e8ffecac483bc218de9153f95f88b4e0e3006bca03d58                        |
| Map Showcase V2                     | 9f78f357eecfc25ea543d163e8d472dc06abeb1fff3215ed30577267750d1e14                        |
| Snapshot JSONL V0                   | cf69851a5844866f8a3c30814d6ec4e10dcf5f9f1703b20b5616f728749e487e                        |
| Renderer V0.1 review ZIP            | 6ceb9c2a5c133c57497c5f2ec74f3e97f94fe8193f8cf98a979768df3d3a6080                        |
| Middleware Renderer freeze manifest | bd8f2e02d85572bdb024417d62f689bcf1bdd47929d9072b44287fb149f9ae5b                        |
| Middleware Renderer frozen ZIP      | da56e3cd7cb1c23759cb7db7308acbd19614f31f9dd5c698807752828018993e                        |
| Video V0.2                          | efb1e90cf501a5d906f4457e5b2365ee2b007025fa464e635fcb5b6cb50c20d3                        |
| Video V0.2 freeze manifest          | fd1e18f8f5382c9cb106b26a060f09ebf948d729d0532250da816e97c40585b8                        |
| Video V0.2 frozen ZIP               | ff4c15aa414eda1a863a878bc835207b79ce69882ae2a7375c4728a8808f9bb0                        |
| C04 loader                          | bdae2b0dfbcf2bcd19d9508eb3446814010dee788c5a832fe3be4aaa3c8a8ac8                        |
| C04 NO-MCTS runner                  | 36d2a706ad622ebb5ddbf0806a611b4fb161386be3897397add0abb63637037d                        |
| Cross-scene Fleet runner            | 00ab3c26bf42be09a3c4b6d0ec7f952bde3f22cfaead30bf5d61f67927e51f3b                        |
| C04 scenario / manifest             | a207a7fc...e0ca / 0b1d836e...149c                                                       |
| Current C04 FAIL report             | adaa61f354a1ab3da03e413e7f1adb467bb71b40374763b8d1c158bcd1f2c8eb                        |

# 19. 证据索引与文件来源

本手册优先整合以下已有正式文档、真实终端粘贴记录与当前对话输出；它们不是等权资料，遇到冲突必须按第 0 章的证据等级处理。

| **证据**                                                           | **主要覆盖**                                                                                        |
|--------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------|
| MineSim-Dynamic_全项目阶段性总交接与AI无缝接管手册_2026-08-16.docx | 截至 8/16 的完整主线、SHA/tag、故障、可视化、cleanup、Neural readiness。                            |
| 8/14 FullMine V4 接管手册                                          | V4 map/planner/CollisionLookup、Representative、资源模型、Codex 归属边界。                          |
| 8/9~8/13 交接文档                                                  | IDM/MCTS/J117、单车/双车接口、CollisionLookup、A1/A2 诊断。                                         |
| 2026-08-17 middleware terminal logs                                | Snapshot/OfflineAdapter/Renderer/Video build、SHA、Gate、freeze。                                   |
| 2026-08-17 cross-scene terminal logs                               | C04/C11/C06 static readiness、runner SHA、C04 loader env、2GiB trace、80GiB high-memory TypeError。 |
| 用户上传 Renderer/Video ZIP                                        | Human Report Visual Gate 的人工视觉审核依据。                                                       |
| Git / SHA / freeze manifests                                       | 所有“FROZEN”与 current source identity 的最高优先证据。                                             |

| **重要** 2026-08-16 的旧 handover 对“下一科学阶段”的结论已经被 2026-08-17 用户决策与真实实验覆盖。保留旧文档历史价值，但下一位 AI 应以本手册第 12/20 章为当前入口。 |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# 20. 快速接手区（下一位 AI 必须先读）

| **CURRENT_STATE** FullMine V4 / Representative Pure MCTS / Polygon21 Fleet-MCTS / Native Video V2 / FullMine Middleware MVP 都已冻结；当前科学工作在 cross-scene C04 dynamic real-loader，80 GiB 环境已越过 FullMine map load，但 loader 因 \`TypeError: float() argument must be a string or a number, not 'list'\` FAIL。NO-MCTS/Fleet 尚未允许启动。 |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

## 20.1 已冻结、默认绝对不要重做

> **•** MineSim IDM baseline / Dapai/Jiangtong regression。
>
> **•** Pure MCTS Dapai/Jiangtong 正式结果 + 448 expert。
>
> **•** J117 Phase4C 单车 full-route。
>
> **•** J117 Phase5 dual Pure MCTS 5-seed + swept safety。
>
> **•** FullMine Vector V4 semantic/bitmap/runtime/planner fixes、targeted 7/7、旧图回归、HEAD/tag。
>
> **•** Representative Coverage v1 + Representative Pure MCTS 3/3。
>
> **•** Polygon21 NO-MCTS physical conflict + Fleet-MCTS 5/5 freeze v2。
>
> **•** Polygon21 Native MineSim Video V2。
>
> **•** Phase2A-2K cleanup / restore provenance。
>
> **•** SimulationSnapshot V0 + OfflineAdapter V0 + Renderer V0.1 + Video V0.2 frozen middleware release。

## 20.2 正式仓库和关键数据在哪里

| **必须知道的对象**    | **路径 / 规则**                                                       |
|-----------------------|-----------------------------------------------------------------------|
| 正式 repo             | /root/MineSim-Dynamic；HEAD 期望 112d2bd...；不要 reset。             |
| Current path registry | /root/autodl-tmp/00_MineSim_ACTIVE/current_paths.json                 |
| FullMine runtime      | /root/autodl-tmp/fullmine_vector_v2_targeted_runtime                  |
| Semantic source       | /root/autodl-tmp/new_map_fullmine_vector_v2_dev                       |
| Bitmap source         | /root/autodl-tmp/fullmine_vector_v4_d_current_planner_patch_candidate |
| Polygon21             | /root/autodl-tmp/fullmine_v4_dual_candidate_v1                        |
| Cross-scene           | /root/autodl-tmp/fullmine_v4_fleet_cross_scene_v1                     |
| Middleware            | /root/autodl-tmp/fullmine_snapshot_middleware_v0                      |
| Cleanup / restore     | /root/autodl-tmp/99_MineSim_CLEANUP_MANIFEST                          |

## 20.3 绝对不能随意动

> **•** runtime semantic/bitmap symlink 与其 resolved targets。
>
> **•** FullMine V4 frozen bitmap/semantic/planner/CollisionLookup。
>
> **•** Polygon21 frozen science directory 与 Native V2 release。
>
> **•** middleware frozen_renderer_v01_20260817_140210、frozen_video_v02_20260817_142048 及 frozen ZIP。
>
> **•** dirty historical /root/autodl-tmp/MineSim-Dynamic、new_map_phase4c_tools、new_map_phase6c_full_mine_structural、DR tar、98_MineSim_QUARANTINE。
>
> **•** Git 未跟踪 ?? ^C；不要 clean。

## 20.4 当前 HOLD / 未验证

| **对象**                                      | **当前状态**                                         |
|-----------------------------------------------|------------------------------------------------------|
| C04 dynamic                                   | real-loader FAIL at float(list)；需 traceback 定位。 |
| C11/C06 dynamic                               | 未运行。                                             |
| Production-authoritative FullMine drivability | NOT PROVEN。                                         |
| Live SimulationSnapshot adapter               | 未正式 PASS；offline frozen dual chain PASS。        |
| Real-time FullMine GUI/platform               | 未实现。                                             |
| Neural-MCTS training                          | NOT STARTED。                                        |
| Dedicated Value/Policy/PolicyValue net        | 未建立。                                             |
| 车型 / gear / datum / official slope          | 部分未权威确认。                                     |

## 20.5 继续工作前的第一轮只读检查

cd /root/MineSim-Dynamic  
source /root/miniconda3/etc/profile.d/conda.sh 2\>/dev/null \|\| true  
conda activate minesim  
export PYTHONPATH=/root/MineSim-Dynamic  
  
pwd  
echo "ENV=\$CONDA_DEFAULT_ENV"  
python --version  
git branch --show-current  
git rev-parse HEAD  
git status --short  
  
cat /root/autodl-tmp/00_MineSim_ACTIVE/current_paths.json  
  
readlink -f /root/autodl-tmp/fullmine_vector_v2_targeted_runtime/maps/semantic_map/geojson_full_mine_vector_v2_dev_semantic_map.json  
readlink -f /root/autodl-tmp/fullmine_vector_v2_targeted_runtime/maps/bitmap/geojson_full_mine_vector_v2_dev_bitmap_mask.png  
  
sha256sum \\  
/root/autodl-tmp/fullmine_vector_v2_targeted_runtime/maps/semantic_map/geojson_full_mine_vector_v2_dev_semantic_map.json \\  
/root/autodl-tmp/fullmine_vector_v2_targeted_runtime/maps/bitmap/geojson_full_mine_vector_v2_dev_bitmap_mask.png  
  
cat /sys/fs/cgroup/memory.max 2\>/dev/null \|\| true  
cat /sys/fs/cgroup/memory.current 2\>/dev/null \|\| true  
cat /sys/fs/cgroup/memory.events 2\>/dev/null \|\| true

期望：HEAD=112d2bd...；semantic=b85a3d8...95cd0；bitmap=51abcd5...efdd0；status 历史常见 ?? ^C。若出现新的 tracked diff 或 SHA 不一致，只读调查，不 reset / clean。

## 20.6 真正的 NEXT_ONE_STEP

| **NEXT_ONE_STEP** 在 high-memory（已验证 80 GiB）实例上，保留当前 C04 FAIL report，复制 \`cross_scene_real_loader_smoke_v3.py\` 到 diagnostic 临时目录，只增加 traceback 打印，运行 \`--source-index 4\`，得到 \`float(list)\` 的准确原始行、source context 与输入字段 shape。禁止修改正式 repo、map、C04 scenario/manifest，也禁止启动 NO-MCTS。 |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

| **完成标准**          | **必须看到**                                                                                                                            |
|-----------------------|-----------------------------------------------------------------------------------------------------------------------------------------|
| 诊断 step             | 完整 traceback；failing original line；source context；相关 manifest/scenario 字段的 Python type/shape。                                |
| 临时兼容修复后 loader | REAL_LOADER_GATE=PASS；report checks 全 PASS；A/B route_s/speed/time 非 None；无错误。                                                  |
| NO-MCTS 入口          | 只有 loader PASS 才允许；必须确认真实 physical conflict + timeline sync + post-conflict complete。                                      |
| Fleet seed0 入口      | 只有 loader + NO-MCTS evidence PASS 才允许；保持 budget64/depth8/DT0.5，不为过关重调参。                                                |
| 资源                  | high-resource card 需要：为了 RAM/CPU quota；GPU compute 仍可关闭。若 reconnect 后 memory.max 回 2GiB，不运行 FullMine dynamic loader。 |

## 20.7 下一位 AI 的首条回复建议

CURRENT_STATE:  
- Frozen baselines unchanged.  
- C04 static PASS; dynamic loader FAIL/HOLD at float(list).  
- 80 GiB environment required for current loader path.  
  
DIFF_FROM_EXPECTED:  
- Report only actual new Git/SHA/path/cgroup differences.  
  
NEXT_ONE_STEP:  
- Traceback-only diagnostic copy of C04 real-loader; no core/map edit.  
  
RISKS/HOLD:  
- Do not run NO-MCTS/Fleet before loader PASS.  
- Do not touch frozen map/runtime/symlinks.  
- Neural-MCTS training not started.

| **交接完成标准** 新的 AI 读到这里，不需要重新扫描全盘、不需要重新验证 Polygon21/FullMine/中间层，也不需要重新询问项目历史；只需完成本页的只读 preflight，然后从 C04 \`float(list)\` 精确定位继续。 |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# 附录 A：报告与可视化的不可变科学规则

> **•** 唯一科学数据源：真实 MineSim cloud map / real scenario / frozen experiment results。
>
> **•** 禁止 AI generation、截图描线、pixel→coordinate 猜测、手工科学坐标修改。
>
> **•** 静态优先 3840×2160 / 16:9；必须能解释 FullMine 全局、Polygon21 位置、真实 junction、A/B frozen paths、conflict point。
>
> **•** 视觉可以改：color / font / linewidth / alpha / HUD / legend / camera / crop / resolution / fps / timing。
>
> **•** 视觉不能改：road coords / vehicle coords / trajectories / conflict point / route / experiment metrics。
>
> **•** 视频约 8s；camera changes only；V0.2 frozen schedule 1.5s global hold + 2.7s locate + 3.8s local hold。
>
> **•** 四 Gate 顺序不变：Scientific/Data Integrity → Geometry Authenticity → Technical Quality → Human Report Visual。

# 附录 B：本手册相对 2026-08-16 旧交接文档的关键更新

> **•** 旧文档中 visualization middleware 还是 DESIGN DISCUSSION ONLY；现在 Snapshot/OfflineAdapter/Renderer/Video MVP 已正式四门禁冻结。
>
> **•** 旧文档中 Map Showcase V3 是尚待收尾侧任务；现在已有独立 middleware V0.2 正式视频，V3 仍保留为 historical incomplete，不再是 blocker。
>
> **•** 旧文档中 cross-scene 仅 static readiness；现在 C04 已开始 real-loader，低资源 2GiB 失败阶段被 trace，高资源 80GiB 越过 map load 后暴露 float(list) TypeError。
>
> **•** 旧文档中下一科学阶段写 Neural dataset governance；最新用户决策改为先完成 FullMine 多场景/多车辆 Fleet-MCTS 动态线，再进入数据治理与 Neural-MCTS。
>
> **•** 中间层 formal freeze 新增 SHA：Renderer manifest bd8f... / ZIP da56...；Video master fd1e... / ZIP ff4c...。
