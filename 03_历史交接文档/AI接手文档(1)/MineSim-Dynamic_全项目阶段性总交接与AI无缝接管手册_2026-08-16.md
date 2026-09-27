**MineSim-Dynamic 全项目阶段性总交接与 AI 无缝接管手册**

MineSim 复现 → Pure MCTS → 单车/双车 → FullMine → Fleet-MCTS → 原生可视化 → 云端整理 → Neural-MCTS 准备

证据截止：2026-08-16  
**文档定位：下一位 AI / 工程人员可在不重复扫描、不重复实验的前提下直接接手云端  
**事实原则：最新云端终端 / Git / SHA / 冻结结果 \> 外置 artifact \> 最新交接文档 \> 历史文档 \> 研究计划

<table>
<colgroup>
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>正式科学基线<br />
112d2bd…</strong></th>
<th><strong>FullMine V4<br />
FROZEN</strong></th>
<th><strong>Polygon21 Fleet-MCTS<br />
5/5 PASS</strong></th>
<th><strong>Neural-MCTS<br />
NOT STARTED</strong></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

| **最重要的接管结论：**当前科学主线不是重新做 MineSim、重新找双车场景或重新验证 FullMine 地图；这些核心阶段已经冻结。下一科学阶段是 Neural-MCTS 的数据集治理/构建，首先只做数据契约与 clean dataset builder，不应直接开 GPU 训练。另有一个不阻塞科研的汇报侧任务：FullMine Map Showcase V3 已渲染完 120 帧但 ffmpeg 编码被 SIGKILL，尚未形成最终 V3 release。 |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

**本手册不把“看起来合理”当作事实。任何证据不足的事项均标为 HOLD / 未验证。**

# 0. 文档使用规则、证据等级与状态术语

本文件是阶段性“总交接手册”，不是论文正文，也不是面向外部宣传的项目介绍。它的目标是把从 MineSim 原项目复现、MCTS 接入、双车联合规划、新地图工程、原生可视化到云端整理的真实链路压缩成可执行的接手上下文。接手者必须先区分“已冻结事实”“历史阶段事实”“设计决策”“仍未验证事项”，不得使用旧 Word 覆盖后来的终端证据。

| **等级**     | **含义**                                                           | **使用规则**                                 |
|--------------|--------------------------------------------------------------------|----------------------------------------------|
| V-LIVE       | 当前 AutoDL 终端、Git、源码、实际文件、实时 SHA、真实运行输出      | 最高优先级；重连后仍需重新只读核验。         |
| V-ARTIFACT   | /root/autodl-tmp 中 result / manifest / freeze / log / release ZIP | 直接支持工程状态；必须核对路径、版本与 SHA。 |
| V-DOC        | 最新交接文档和本手册                                               | 用于接手；若与 live 冲突，live 优先。        |
| HIST         | 旧阶段 Word、旧备份、被替代版本                                    | 解释历史，不得覆盖后续结果。                 |
| DESIGN       | 人为构造场景、评价门槛、工作流、可视化规则                         | 可作为约束，但不能冒充天然数据事实。         |
| HOLD/UNKNOWN | 资料不足、外部权威输入缺失或尚未执行                               | 必须明确写未验证；禁止凭常识补齐。           |

| **状态术语：**PASS=当前定义下验证通过；FROZEN=有 commit/tag/freeze/SHA 等锚点，默认不重做；HISTORICAL=历史可复现但不是当前最终版本；HOLD=保留且暂不动；NOT STARTED=尚未实施；INCOMPLETE=开始过但未完成最终门禁。 |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

## 0.1 主要证据源索引

| **ID**   | **证据**                                                           | **主要支持**                                                                                         |
|----------|--------------------------------------------------------------------|------------------------------------------------------------------------------------------------------|
| **S01**  | 2026-08-06《项目全景档案与 AI 长期接管超级手册》                   | IDM baseline、Pure MCTS、五 Planner、448 专家样本、Budget、公平性与早期工程修复。                    |
| **S02**  | 2026-08-09《云端项目完整交接与工作流手册》                         | Multi/Fleet MCTS 架构、J117 Phase1-4C、云端安全规则、阶段 commit/tag。                               |
| **S03**  | 2026-08-11《新地图项目云端交接手册》                               | J117 Phase5、FullMine V1、structural converter、DEV_ONLY 边界。                                      |
| **S04**  | 2026-08-12《项目完整进展与云端 AI 接管超级手册》                   | Vector V2 100 roads/553 paths、targeted runtime、CollisionLookup 初步诊断。                          |
| **S05**  | 2026-08-13《项目云端接手与技术总览》                               | CollisionLookup、A1 endpoint、A2 中途停车、shadow 工作流。                                           |
| **S06**  | 2026-08-14《FullMine Vector V4 地图成果与 Pure MCTS 冻结接管手册》 | A2 真根因、V3/V4 exact patch、7/7、旧图回归、112d2bd freeze、Representative MCTS、Neural readiness。 |
| **T01**  | 2026-08-15~16 Polygon21 cloud terminal / freeze 记录               | NO-MCTS physical conflict、Fleet-MCTS 5 seed、freeze v2、tag、关键 SHA。                             |
| **T02**  | 2026-08-16 Polygon21 Native Video V1/V2 terminal 记录              | 原生 PlanVisualizer2D、A/B 状态来源、V1 尺寸错误、V2 release。                                       |
| **S07**  | 2026-08-16《MineSim 云端项目文件整理与维护说明》                   | Phase2A-2K、current_paths、HOLD、ARCHIVE/QUARANTINE、restore、最终 health。                          |
| **T03**  | 2026-08-16 semantic schema / Map Showcase V1-V3 terminal           | MineSim 自定义 semantic schema、4K/1080p 可视化链、V3 SIGKILL 未收口。                               |
| **LIVE** | 本对话用户直接粘贴的 Git/terminal 输出                             | 8/16 最新 HEAD/status、渲染、编码与生成结果；在本手册内视为最新直接证据。                            |

## 0.2 AI/Codex 归属说明

用户要求把“今天 Codex 在云端实际完成的工作”纳入总结。为了避免虚构归属，本手册只把日志/旧文档明确写明 Codex 的动作称为 Codex 工作；对于 2026-08-16 的 Polygon21 冻结、Native Video、Map Showcase、文件整理等，能够确定的是“AI/脚本 + 用户云端终端协作实际完成或执行”，但若单个日志没有明确标注由 Codex 还是 ChatGPT 生成脚本，则不强行归因。接手者应延续这一事实边界。

# 1. 当前项目 30 秒状态与完整主线

项目一句话定义：MineSim-Dynamic 是面向露天矿无人矿卡规划的闭环仿真/算法验证工程；当前已经从原始 MineSim 的 IDM/replay 复现，推进到 Pure MCTS、Multi/Fleet MCTS、真实 GIS 新地图 FullMine Vector V4 Research Baseline、Polygon21 双车物理冲突 benchmark 与原生 MineSim 可视化。神经网络阶段尚未开始正式训练。

| **主线/分支**                       | **状态**               | **当前最准确结论**                                                                      |
|-------------------------------------|------------------------|-----------------------------------------------------------------------------------------|
| **MineSim 原项目复现**              | PASS / FROZEN          | Dapai / Jiangtong IDM + replay/闭环基线已建立。                                         |
| **Pure MCTS 接入**                  | PASS / FROZEN          | 真实 MineSim online closed-loop；Dapai/Jiangtong 正式结果 + 448 strict expert samples。 |
| **五 Planner + Budget**             | PASS / HISTORICAL      | MCTS/IDM/Frenet/Adapted Maneuver/Simple；Budget 50/100/200/300。                        |
| **J117 单车**                       | PASS / FROZEN          | 真实 GeoJSON pilot，423 steps / 42.3 s / goal reached。                                 |
| **J117 双车 Pure MCTS**             | PASS / FROZEN          | NO-MCTS 真冲突；seed0 + 5-seed swept safety 通过。                                      |
| **FullMine Vector V4 Research Map** | COMPLETE / FROZEN      | Vector V2 semantic + V4 bitmap/runtime + planner/CollisionLookup 修复；7/7 + 旧图回归。 |
| **Representative Pure MCTS**        | 3/3 PASS / FROZEN      | 跨代表区域 transfer 已冻结。                                                            |
| **Polygon21 Fleet-MCTS**            | 5/5 PASS / FROZEN      | NO-MCTS physical conflict；Fleet-MCTS 无重调参，5 seed 全通过。                         |
| **跨场景 Fleet 集合 C04/C11/C06**   | STATIC READY / HOLD    | 6/6 路线静态门控通过；real-loader/NO-MCTS/Fleet 动态实验未完成。                        |
| **Native MineSim 视频**             | V2 FINAL / PASS        | 原生 NO-MCTS/Fleet/side-by-side release 已冻结。                                        |
| **FullMine Map Showcase**           | V2 PASS；V3 INCOMPLETE | V2 数据/技术通过；V3 120 帧已渲染但 ffmpeg SIGKILL，未形成最终 V3 release。             |
| **云端文件整理**                    | Phase2K COMPLETE       | 顶层约 530→121；423 移动/隔离；科研文件删除 0；restore 完整。                           |
| **Neural-MCTS**                     | NOT STARTED            | readiness audit 已做；需要 clean dataset builder，不能直接训练。                        |

| **当前真正的科学下一步：**不是重新跑 Polygon21，不是重做 FullMine 地图，也不是先改可视化平台；应先做 Neural-MCTS 数据治理：只读 inventory → 冻结数据契约 → clean dataset builder → 按 episode/scenario split → 小样本 smoke。完成这些前不需要开 4090D。 |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

| **当前并行但不阻塞的侧任务：**Map Showcase V3 的最后编码/人工视觉门禁尚未闭合；可以以后复用现有 120 帧低内存编码，不应重新读取/渲染整个 semantic map。 |
|--------------------------------------------------------------------------------------------------------------------------------------------------------|

# 2. 项目完整时间线：从 MineSim 复现到 2026-08-16

| **日期**      | **阶段**                            | **可复核结果/意义**                                                                                                               |
|---------------|-------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------|
| 2026-07-22    | 新地图接入框架                      | 明确新矿区必须形成 Raster/Bitmap + Semantic Map + Scenario 三类成果；为后续 J117/FullMine 建立概念框架。                          |
| 2026-07-26    | IDM baseline                        | 正式仓库 /root/MineSim-Dynamic；commit 2521aa41…；tag idm-replay-autodl-baseline；建立云端/Git/AI 安全纪律。                      |
| 2026-07-30~31 | Pure MCTS 闭环                      | MCTSPlanner 外壳、状态/动作/搜索/奖励/轨迹适配进入 MineSim；经历 iLQR/确定性修复。                                                |
| 2026-08-01    | Jiangtong 安全迭代                  | CV/CTRV、0.5 m buffer、viability、clearance、动态冲突几何排查。                                                                   |
| 2026-08-02    | 正式 MCTS + expert                  | commit 94693dc…；Dapai/Jiangtong；448 strict expert samples；tag mcts-expert-dataset-v1-20260802。                                |
| 2026-08-03~07 | 五 Planner / fairness / Budget      | Frenet/Maneuver/Simple 适配，统一 evaluator；Budget 50/100/200/300。                                                              |
| 2026-08-08~09 | Multi/Fleet MCTS                    | FleetState + 16 joint actions；Dapai A-B-only 形成时序分离；Jiangtong V22 负筛选。                                                |
| 2026-08-09    | J117 Phase1-4C                      | 真实 GeoJSON pilot→Map API→minimal Scenario→423 step/42.3 s 单车 full-route。                                                     |
| 2026-08-10    | J117 Phase5                         | dual-ego production runtime + Pure MCTS；5 seed benchmark/swept safety PASS；commit da4105b…。                                    |
| 2026-08-11    | FullMine V1                         | full structural + DEV_ONLY mask + token2ind O(1) + 独立 map identity；single/dual smoke；tag fullmine-dev-runtime-pass-20260811。 |
| 2026-08-12    | Vector V2                           | source completeness audit；100 effective roads / 553 paths / 8 repairs / raw lane Z；15 target + 7 depth-safe scenarios。         |
| 2026-08-13    | CollisionLookup + planner debugging | XG90G 前后悬/梯形语义错误、exact SAT；A1 endpoint 4.5 m virtual lead；A2 深入诊断。                                               |
| 2026-08-13~14 | A2 最终 planner 修复                | steering-rate-aware speed profile + backward braking envelope；A1/A2/B1/B2 shadows 全通过。                                       |
| 2026-08-14    | FullMine V3/V4 + freeze             | V3 actual shadow trajectory +724px；V4 D-only +3px；targeted 7/7 + Jiangtong regression；commit 112d2bd… + tag。                  |
| 2026-08-14    | Representative Coverage / Pure MCTS | 代表区域 coverage 冻结；Representative Pure MCTS 3/3 PASS；Neural readiness 只审计不训练。                                        |
| 2026-08-15    | Polygon21 conflict benchmark        | FullMine V4 Polygon21 新区域 constructed physical-conflict benchmark；NO-MCTS 冲突；Fleet-MCTS 5/5；freeze v2 + tag。             |
| 2026-08-16    | Native MineSim reporting            | NO-MCTS/Fleet 冻结链重跑 + PlanVisualizer2D 原生渲染；V1 尺寸问题修复到 V2；release PASS。                                        |
| 2026-08-16    | 云端安全整理                        | Phase2A-2K；530→121；0 删除；current_paths、ARCHIVE、QUARANTINE、restore、final health PASS。                                     |
| 2026-08-16    | FullMine 全局地图展示               | V1 schema 假设失败→真实 MineSim custom schema audit→V2 真实数据渲染 PASS；V3 仅视觉升级但编码 SIGKILL，未 final。                 |

# 3. MineSim 原系统与当前工程调用链

必须先理解系统边界：本项目没有重写完整 MineSim。地图、Scenario、Planner、Controller、车辆模型、Observation/agent 更新和安全/日志共同构成闭环；MCTS 主要替换/扩展 Planner 决策层，并通过 trajectory adapter 继续走 MineSim Controller 与车辆模型。

| **层**             | **当前真实职责/调用链**                                                                                                             | **接手风险**                                                                  |
|--------------------|-------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------|
| **Map / Scenario** | ScenarioFileBaseInfo → MineSimDynamicScenario → get_maps_api / MineSimMap；Semantic + Bitmap 决定拓扑与可行驶真值。                 | semantic identity、bitmap symlink、绝对路径不能随意改。                       |
| **Planner**        | planner.initialize() 建 global route/refline；每帧 compute trajectory。IDM/Pure MCTS/Fleet MCTS 均需服从 AbstractPlanner/真实接口。 | 不要按 AI 记忆猜签名/Hydra 参数。                                             |
| **Control**        | TwoStageController → iLQR/LQR 跟踪轨迹。                                                                                            | planner 输出合法不等于 controller 一定可实现，高曲率/速度会暴露可执行性问题。 |
| **Vehicle**        | Kinematic Bicycle Model / ego controller propagate。                                                                                | rear axle / center / footprint 语义必须统一。                                 |
| **Observation**    | replay/reactive/prediction 更新外部 actor；multi-ego 需把受控 A/B 从 external observation 过滤。                                    | 受控车辆重复作为 external 会造成假碰撞/重复对象。                             |
| **Safety/Metrics** | vehicle footprint + bitmap + goal + history/log；CollisionLookup + exact geometry。                                                 | 离散 lookup 可能 false positive；必须用物理几何 truth-check。                 |
| **Visualization**  | PlanVisualizer2D + SimulationHistory/PlotData；双车 B 需要 MultiEgoRuntime live state 补齐。                                        | history 不是双车完整真值，不能把 A history 当作 A+B。                         |

## 3.1 Pure MCTS 模块化原则

| **模块**                             | **角色**                                                                            |
|--------------------------------------|-------------------------------------------------------------------------------------|
| local_planner/mcts_planner.py        | MineSim API 适配层：PlannerInput / history / map / trajectory；不应塞搜索内核细节。 |
| mcts/state.py                        | MCTSState。                                                                         |
| mcts/action_space.py                 | 离散动作 BRAKE / DECEL / KEEP / ACCEL。                                             |
| mcts/state_builder.py                | MineSim 状态 → MCTSState。                                                          |
| mcts/transition_model.py             | 树内轻量近似动力学。                                                                |
| mcts/reward.py                       | progress/speed/safety/comfort/terminal 等 reward。                                  |
| mcts/node.py / search.py             | Selection / Expansion / Rollout / Backup。                                          |
| mcts/trajectory_adapter.py           | 把根动作转回 MineSim 可执行轨迹。                                                   |
| mcts/diagnostics.py / expert_data.py | 搜索诊断与专家记录。                                                                |

| **未来 Neural-MCTS 为什么不该重写 Planner：**现有架构已经把 MineSim adapter 与纯 MCTS search 分开。未来神经网络最自然的切入点是 leaf evaluation / prior / PUCT，而不是重新实现 Scenario、Controller 或 MCTSPlanner 外壳。 |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# 4. 主线阶段一：MineSim 复现与 IDM Baseline

目标：先保证原系统能在云端稳定复现，建立后续算法开发的回归锚点。原项目中 Dapai / Jiangtong 成品地图与 IDM/replay 闭环是后续所有 MCTS、新地图修复和 old-map regression 的参照。

| **项目**                | **冻结事实**                                                                 |
|-------------------------|------------------------------------------------------------------------------|
| **正式仓库**            | /root/MineSim-Dynamic                                                        |
| **IDM baseline commit** | 2521aa41a69a6e734c04c15a715e9530c8095ac3                                     |
| **baseline tag**        | idm-replay-autodl-baseline                                                   |
| **正式 Conda**          | minesim                                                                      |
| **正式项目 Python**     | 3.9.25（多份 8/12~8/16 cloud preflight 实际输出）                            |
| **原成品地图**          | /root/datasets/maps 中 Dapai / Jiangtong；作为 production 行为对照，不修改。 |
| **历史恢复备份**        | /root/autodl-tmp/minesim_idm_baseline_backup                                 |

## 4.1 完成标准

- MineSim 正式仓库可进入、环境可激活、Scenario/Map/Planner/Controller/vehicle loop 可运行。

- 旧成品地图不被新地图开发覆盖；后续任何全局修复必须做 Dapai/Jiangtong regression。

- baseline commit/tag 是历史锚点，不因为后续 MCTS/FullMine 开发而回退覆盖当前成果。

## 4.2 后续实践中暴露出的 baseline 价值

FullMine 阶段修改了 CollisionLookup 和 IDM planner 行为，这些都是全局代码。最终 V4 冻结前使用旧 Jiangtong 回归确认 249 steps、0 vehicle collision、0 road boundary collision，并保持 strict safety；因此旧地图不是“过时资产”，而是生产行为回归基准。

# 5. 主线阶段二：Pure MCTS 接入与单车跑通

目标：在不重写 MineSim 执行栈的前提下，把纵向反应式决策替换为多步树搜索，并保持输出仍由 MineSim Controller/iLQR/KBM 执行。Pure MCTS 在每帧重新搜索并只执行根节点第一步动作，属于 receding-horizon MCTS。

| **参数/定义**              | **历史正式值/范围**                                  |
|----------------------------|------------------------------------------------------|
| **动作**                   | BRAKE=-3.0 m/s²；DECEL=-1.5；KEEP=0；ACCEL=+1.0。    |
| **历史正式 Search Budget** | 300；另完成 50 / 100 / 200 / 300 消融。              |
| **max_depth**              | 8                                                    |
| **tree_dt**                | 0.5 s                                                |
| **c_uct**                  | 1.4                                                  |
| **gamma**                  | 0.99（历史正式记录）；配置必须以运行时冻结文件为准。 |
| **输出 horizon**           | 16 × 0.5 s                                           |
| **目标速度**               | 约 10 m/s，历史比较中 accel/decel 与 IDM 对齐。      |
| **障碍预测**               | CV / CTRV                                            |
| **几何安全**               | 约 0.5 m physical buffer；连续净距阈值历史约 3.0 m。 |

## 5.1 2026-08-02 正式 MCTS 结果与专家数据

在 commit 94693dc799fe5f325a75e8fc6d7d5e88764b4799 上完成 Dapai 与 Jiangtong 正式 MCTS/IDM 运行及 expert 采集，tag 为 mcts-expert-dataset-v1-20260802。严格专家样本共 448 条，包含 ego、MCTS root state、选中动作、action visits、Q 值、reward 分量等。

| **训练边界：**448 样本只证明 expert-data 管线可用，不代表 Neural-MCTS 已训练。样本来自连续时间序列和少数场景，禁止随机逐行 train/val split；必须按 scenario / episode 分组，避免时序泄漏。 |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

## 5.2 五 Planner 与 Budget 作为支持性证据

| **Planner**      | **Safe Goal** | **碰撞帧** | **边界帧** | **严谨解释**                                      |
|------------------|---------------|------------|------------|---------------------------------------------------|
| MCTS             | 2/2           | 0          | 0          | 在这两场景中唯一 2/2；不能外推为全场景/总体最优。 |
| IDM              | 1/2           | 21         | 0          | Jiangtong 可完成；Dapai 冲突。                    |
| Online Frenet    | 0/2           | 0          | 0          | 安全但未完成任务；不能只看碰撞。                  |
| Adapted Maneuver | 0/2           | 67         | 0          | 评价当前适配版，不代表原算法总体。                |
| Simple           | 0/2           | 0          | 90         | 能力下限参考，不是公平主比较。                    |

Budget 50/100/200/300 的消融只改变搜索预算。Dapai 对预算明显敏感，历史固定时限下只有 300 进入目标；Jiangtong 在较低预算已接近饱和。这个事实直接引出 adaptive budget / tree reuse / value guidance，但当时优先级被“缺少第二个干净多车 benchmark”和新地图链路所取代。

## 5.3 单车阶段重要问题：Frenet 接口越界

首次 Dapai Frenet 完整运行在 step 150 失败，根因不是候选搜索没有轨迹，而是 \`\_get_planned_trajectory()\` 的重采样索引列表追加 79；当 best_traj 长度恰为 79 时有效索引只到 78，触发 IndexError。解决方案是外部安全重采样/适配，随后 Dapai 199 步、Jiangtong 249 步完整跑通。以后遇到 Planner FAIL 必须先分辨“搜索失败”还是“Planner→MineSim trajectory 接口失败”。

# 6. 主线阶段三：双车冲突场景构建与 Multi/Fleet MCTS

目标：从单车 MCTS 走向两辆受控矿卡在同一仿真 iteration 内联合决策。核心不是简单把一辆 replay 车辆当障碍，而是把 A/B 都放入 FleetState，联合传播、联合 reward，并保证两辆受控车从 external observation 中剔除。

| **组件**                                   | **已实现语义**                                                                                    |
|--------------------------------------------|---------------------------------------------------------------------------------------------------|
| ControlledVehicleRuntime / MultiEgoRuntime | 按 token A/B 管理两个受控车辆，统一 current/next iteration，同步接收两条 trajectory。             |
| SimulationSetup.set_multi_ego_runtime()    | 生产链正式挂载 multi-ego runtime。                                                                |
| EnvironmentSimulation.propagate()          | dual 模式要求 trajectories 恰好包含 A/B；再调用 MultiEgoRuntime 同步更新。                        |
| filter/partition controlled                | 从 tracked observation 中稳定提取并剔除 A/B，避免受控车重复作为 external actor。                  |
| FleetState                                 | 联合表示 A/B MCTSState。                                                                          |
| FleetTransitionModel                       | 16 个联合动作；受控 A/B 几何真实耦合。                                                            |
| FleetRewardModel                           | per-vehicle reward + internal continuous clearance soft penalty + hard safety/collision penalty。 |
| RouteGeometryCache                         | rear-axle route_s → geometric center footprint，避免参考点混用。                                  |

## 6.1 Dapai：机制证据而非唯一 benchmark

Dapai A-B-only 已形成双受控时序分离证据，但 full scenario 存在 external object-1 confound，因此后续不把它作为新 benchmark 的唯一证据。Dapai 的价值是验证 multi-ego 机制和联合搜索链能够工作。

## 6.2 Jiangtong V22：负筛选是有效结果

Jiangtong Traj26 虽有空间交叉，但自然 ETA 存在约 9.496 s 级时序差，不构成近同时双车冲突。因此 \`jiangtong-v22-benchmark-screening-20260809\` 被正式封存为负筛选结果。接手者不得为了“凑第二场景”重新把它包装成天然冲突 benchmark。

| **场景筛选原则：**有空间交叉 ≠ 有联合决策价值。必须先证明时间上会进入真实冲突窗口，再比较 NO-MCTS 与 Fleet-MCTS。 |
|-------------------------------------------------------------------------------------------------------------------|

# 7. 主线阶段四：J117 真实地图 Pilot——单车到双车

J117（Junction 117）不是第三张原始 MineSim 成品地图，而是从用户 FullMine 原始 GeoJSON 中切出的真实 junction pilot。其使命是先打通“真实 GIS → MineSim Map API → Scenario → Planner → Controller → Runtime → Multi-Ego MCTS”，再扩展到整个 FullMine。

## 7.1 Phase1-4C 单车

| **指标**                        | **结果**                              |
|---------------------------------|---------------------------------------|
| **Route A（历史 J117）**        | 6670 → 6674 → 5690                    |
| **Route B（历史 J117）**        | 5691 → 6546 → 6523                    |
| **Phase4C steps**               | 423                                   |
| **仿真时长**                    | 42.3 s                                |
| **路线距离**                    | 约 398.998 m                          |
| **最小 clearance**              | 约 1.599 m                            |
| **goal / drivable / exception** | goal reached / 全程 drivable / 无异常 |

## 7.2 Phase5 双车 Pure MCTS

| **实验**                 | **结果**                                                                              |
|--------------------------|---------------------------------------------------------------------------------------|
| NO-MCTS aligned baseline | crossing gap ≈ 0.00070 s；min clearance=0；发生真实几何重叠。                         |
| Pure MCTS seed0          | crossing gap ≈ 1.561 s；1 ms swept min clearance ≈ 0.594 m；无碰撞。                  |
| 5-seed robustness        | 5/5 benchmark PASS。                                                                  |
| 5-seed swept safety      | 5/5 PASS；最小 swept clearance ≈ 0.594 m；gap 约 1.35–1.97 s。                        |
| 同步机制                 | A/B 同 iteration；object-1 从 external observation 过滤；single-ego regression safe。 |

| **冻结项**        | **值**                                                            |
|-------------------|-------------------------------------------------------------------|
| **Phase5 commit** | da4105b836dbbd3e702ee25fbb364109bc4e2596                          |
| **Tag**           | j117-phase5-dual-ego-pure-mcts-20260810                           |
| **阶段语义**      | J117 real-map constructed benchmark / 回归区域；默认不重调 MCTS。 |

| **J117 已冻结：**除非 production source 的 Map API、Planner、Controller、车辆几何发生会影响 J117 的修改，否则不要重新调 J117 MCTS。J117 后续主要作为回归金标准。 |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# 8. 主线阶段五：FullMine 新地图接入——V1 → Vector V2 → V3/V4

FullMine 才是本项目真正的新全矿地图。严格版本语义不是“重新造了一张 V4 semantic”，而是：\`Vector V2 semantic + 最终 V4 bitmap/runtime freeze + 当前 planner/CollisionLookup 修复\`。map identity 继续保留 \`geojson_full_mine_vector_v2_dev\`，这是为了维持已验证的 semantic identity，不应为了名字美观重命名冻结资产。

## 8.1 原始数据与 semantic 结果

| **原始层**            | **Feature 数** | **用途**                      |
|-----------------------|----------------|-------------------------------|
| road.geojson          | 94             | road polygon                  |
| road_boundary.geojson | 100            | road 两侧边界                 |
| junction.geojson      | 35             | junction polygon              |
| lane.geojson          | 553            | reference path / topology / Z |
| rgn_boundary.geojson  | 84             | 作业区 / junction 边界        |
| rng_load.geojson      | 36             | loading region                |
| rgn_unload.geojson    | 7              | unloading region              |
| rgn_auxiliary.geojson | 6              | auxiliary region              |

Vector V1 是保守可运行基线；8/12 source completeness audit 证明一些早期“缺失/异常”来自 validator/layer mapping、cross-category ID 绑定和保守排除，不应永久当作源数据缺失。Vector V2 通过 8 条 provenance repair 恢复到 100 effective roads / 553 reference paths，并保留 raw lane Z。

| **当前 frozen semantic 关键数量**    | **值**                                                       |
|--------------------------------------|--------------------------------------------------------------|
| **node（8/16 custom schema audit）** | 403,759                                                      |
| **polygon**                          | 184                                                          |
| **road**                             | 100                                                          |
| **intersection**                     | 35                                                           |
| **loading / unloading / auxiliary**  | 36 / 7 / 6                                                   |
| **dubins_pose**                      | 565                                                          |
| **reference_path**                   | 553                                                          |
| **borderline**                       | 402                                                          |
| **waypoints（8/12统计）**            | 314,692                                                      |
| **elevation policy**                 | raw lane Z 写 waypoint\[3\]；source_z_datum_verified=false。 |
| **slope**                            | waypoint\[4\] 仍为 0.0；official smoothing rule 未复现。     |

## 8.2 大图性能与路径初始化

FullMine 大图早期 planner init 很慢，根因之一是 polygon token lookup 重复线性扫描，而不是“GPU 不够”。修复 commit 32fb42920d8cc404b37cd25dc47cbc6fbde4d9f4 将 semantic node lookup 改为 token2ind O(1)。长 A/B route 的另一类问题来自 GlobalRoutePathPlanner BFS \`target_depth=5\`，项目没有大改全局 planner，而是构建 depth-safe targeted scenarios，使 route/refline 7/7 exact PASS。

## 8.3 Bitmap 只允许 additive / immutable

FullMine bitmap 的核心治理规则是 additive-only：历史候选一旦产生 manifest/SHA 即视为 immutable；新的 physical gap 必须建立新目录/新 manifest/新 SHA。不能覆盖 P0/candidate v1/v2，也不能看到 boundary fail 就直接“涂宽道路”。

| **历史/最终资产**                   | **意义**                                                             |
|-------------------------------------|----------------------------------------------------------------------|
| P0 baseline SHA d2afc84e…           | 2026-08-13 接手冻结基线；禁止原地修改。                              |
| candidate v1                        | +112 pixels = 1.12 m²（历史诊断阶段）。                              |
| candidate v2 SHA 57514c52…          | 相对 P0 累计 +118px = 1.18 m²；历史 immutable。                      |
| V3 exact final A/B trajectory patch | 基于最终 planner 的 A1/A2/B1/B2 actual shadow trajectories；+724px。 |
| V4 D-only exact patch               | current-planner D 在 v3 暴露真实 3px gap；72-state shadow → +3px。   |
| Final V4 bitmap SHA                 | 51abcd5a86e5c510204a5dacc873691506d721f98982ab7f98585d4e0f7efdd0     |

# 9. FullMine 核心问题复盘：症状、误判、根因、解决

| **症状**                                | **容易误判**               | **最终根因**                                                           | **最终解决**                                                                           |
|-----------------------------------------|----------------------------|------------------------------------------------------------------------|----------------------------------------------------------------------------------------|
| V1 endpoint 126 errors                  | lane/road 数据坏           | 共享 topology endpoint XY 不是 bit-identical                           | 按 topo node canonical endpoint snapping。                                             |
| source coverage missing 49              | 源数据缺失                 | validator layer mapping 不完整                                         | 补齐 road/junction/load/unload/aux mapping。                                           |
| boundary parent 8 错挂                  | boundary 数据不可靠        | cross-category 只按 ID 查；ID 可重复                                   | 按 rgn_type + objectid 严格绑定。                                                      |
| V1 93 roads/540 paths                   | 源只能做到这些             | 保守排除 missing/self-intersection/mismatch road                       | source audit + 8 provenance repairs → 100/553。                                        |
| 大图 planner init 极慢                  | CPU/GPU 不够               | polygon token lookup 反复线性扫描                                      | token2ind O(1)。                                                                       |
| C/D/E boundary collision                | bitmap 大缺口              | 先有 XG90G footprint 前后悬/梯形语义错，再有离散 lookup false positive | 对齐 CarFootprint + exact SAT；只在真 physical gap 后补少量像素。                      |
| A1 goal 前约 4.84m 停车                 | goal polygon/地图错        | free-road route endpoint 被当 4.5m 虚拟前车                            | virtual endpoint length_rear=0.0；数学 regression + shadow 验证。                      |
| A2 step250 中途停车                     | endpoint 或 leading object | 旧 9–11 m/s 在高曲率段要求 steering-rate 超过可实现范围                | steering-rate-aware speed cap + backward braking envelope。                            |
| B2 fixed offset 扫出 227px              | 需要补大片 mask            | 固定 lateral/yaw error 外推 25m，忽略 controller 后续纠偏              | 拒绝 patch；只用 actual shadow trajectory。                                            |
| V3 pixel-by-pixel \>8.5h                | 算法必须慢                 | 每 state/pixel Shapely exact intersection 太重                         | 小 raster window + NumPy broadphase + ambiguous edge exact predicate。                 |
| cached/chunked RC137                    | 随机挂                     | 旧 2GiB cgroup 内存峰值                                                | 先看 cgroup；高资源时并行；不把宿主机 free -h 当真值。                                 |
| 7/7 一度只剩 5/7                        | V4 回归失败                | 混用了 stale manifest/旧 C/D/E JSON                                    | 重新 current-planner 单场跑并绑定 SHA 世代。                                           |
| FullMine MCTS 启动失败                  | MCTS 不支持新地图          | ScenarioOrganizer 入口只识别 dapai/jiangtong                           | benchmark harness 使用 explicit ScenarioFileBaseInfo adapter，不改 tracked organizer。 |
| 1-step MCTS RC1                         | MCTS runtime failure       | benchmark 后置 assert steps\>3                                         | 用 5-step smoke 获取 clean RC0；区分 harness gate 与算法失败。                         |
| candidate0010 300-step final-point FAIL | MCTS 到不了 goal           | simulation 到 goal 后未自动停止；step83 已到达还继续走                 | formal rear-axle goal history audit；旧 final-point FAIL 作废。                        |

## 9.1 A1 endpoint 4.5 m bug 的定量闭环

A1 已访问三个 targets，却在 goal 前约 4.84 m 停车。IDM free-road virtual lead 使用 \`length_rear = ego.length/2 = 4.5m\`，但 route endpoint 本质上是零长度停止点。结合 min_gap=1m、rear axle→center≈2m、goal 为 path end 前3m，理论提前量 4.5+1+2-3=4.5m，与实测 4.8369m 高度一致。最终只把 virtual endpoint 的 \`length_rear\` 改为 0.0，而不是改地图/goal。

## 9.2 A2 真根因与最终 planner

A2 在 endpoint 修复后仍停于 path-000299 中段，route remaining≈274.44m，第三 target path-000301 起点仍在≈242.61m 前方，因此 endpoint 被排除。leading-object/occupancy 是合理中间假设，但后续证据最终指向高曲率下 steering-rate infeasible。最终方案：从 refline curvature 计算 \`delta=atan(wheel_base\*curvature)\`，按 station 求 steering change，以 steering-rate limit 0.26 rad/s 的 80%（0.208 rad/s）反推局部速度 cap，再用 IDM \`decel_max\` 做 backward braking envelope。最终 planner SHA \`541ec74985d06322656e66c48abb382030d679171341408575d936e0a069e75e\`；behavior shadow A1/A2/B1/B2 分别 308/555/523/330 steps，均按目标顺序到达 goal。

# 10. FullMine Vector V4 最终冻结与代表区域验证

| **冻结项**              | **当前值**                                                                 |
|-------------------------|----------------------------------------------------------------------------|
| **正式 HEAD**           | 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e                                   |
| **V4 tag**              | fullmine-vector-v4-runtime-freeze-20260814                                 |
| **最后已知 Git status** | ?? ^C（历史零字节未跟踪对象；整理前后不变；不得 git clean）。              |
| **semantic identity**   | geojson_full_mine_vector_v2_dev                                            |
| **semantic SHA**        | b85a3d8b28f2252ecb5bda179d514573f6333079def838cd048566f556d95cd0           |
| **bitmap SHA**          | 51abcd5a86e5c510204a5dacc873691506d721f98982ab7f98585d4e0f7efdd0           |
| **final acceptance**    | targeted 7/7 PASS + old Jiangtong regression PASS。                        |
| **地图口径**            | Research / DEV baseline；production-authoritative drivability NOT PROVEN。 |

| **不可夸大：**FullMine V4 可以称“可恢复、可复现、可承载算法实验的 Research Baseline”，不能称官方 production HD Map。现有 GeoJSON 无法唯一恢复官方 production mask 的 internal exclusions；权威 drivability 仍依赖外部数据。 |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

## 10.1 Representative Coverage 与 Pure MCTS

地图冻结后，项目没有只停留在 repair/J117，而是做了 representative coverage 和 Pure MCTS transfer。Representative Coverage v1 已冻结（带 documented limitations）；Representative Pure MCTS 3/3 PASS + freeze。其意义是证明 frozen V4 在不同代表区域可以承载正式算法链，但仍不是统计意义上的全矿生产安全证明。

| **对象**                   | **状态/锚点**                                                                                                                                                                             |
|----------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Representative Coverage v1 | COMPLETE + FROZEN WITH DOCUMENTED LIMITATIONS；tag \`fullmine-v4-representative-coverage-v1-20260814\`；freeze SHA \`bab9e77446e9c3b5747bb2721d035ca726b482418559b5f2a1018fe5e0018c5e\`。 |
| Representative Pure MCTS   | 3/3 PASS + FROZEN；tag \`fullmine-v4-pure-mcts-representative-transfer-v1-20260814\`；freeze SHA \`322e90d6995c410597d01925de6d77f1fd91ddb8c4c73a25c3e87446d37ac1fa\`。                   |

# 11. 主线阶段六：Polygon21 Fleet-MCTS 双车联合规划与多种子验证

Polygon21 是 FullMine V4 中选出的新区域 constructed physical-conflict benchmark。构造原则是先用真实地图几何确认存在碰撞窗口，再复用已经验证的 J117 Phase5 dual-ego production chain，用同一初始状态先跑 NO-MCTS causal baseline，再启用 Fleet-MCTS。Fleet-MCTS 使用历史参数迁移，\`PARAMETER_RETUNING=False\`。

## 11.1 冻结场景与关键资产

| **对象**           | **路径/文件**                                                                                         | **SHA256**                                                       |
|--------------------|-------------------------------------------------------------------------------------------------------|------------------------------------------------------------------|
| Scenario           | /root/autodl-tmp/fullmine_v4_dual_candidate_v1/Scenario-fullmine-v4-polygon21-rank1-dual-aligned.json | 362eff18c7ccc88ea8dfaf083a517603566516943690d5cbe76bd1a97afc89e1 |
| Scenario manifest  | polygon21_rank1_dual_scenario_manifest_v1.json                                                        | 0bde6bb1e869c3cf583947203dd41a8fc364f0a2a8130617baebd0b1e6cbad2e |
| NO-MCTS runner     | polygon21_rank1_nomcts_conflict_baseline_v1.py                                                        | e80de93bf25dd45a248152ab0bf8b2539ab9692f7f57195e91db9a5c60bfb378 |
| NO-MCTS result     | polygon21_rank1_nomcts_conflict_baseline_result_v1.json                                               | 060880c8edc851e05606871cb647058d091ce8737f952b9864cc94e9d6fcfd13 |
| Fleet runner       | polygon21_rank1_fleet_mcts_transfer_v2.py                                                             | 5a90a164e2542c6bfdf310e13c5f516e798f3331cf2bcf9898eb890693b83552 |
| Fleet seed0 result | polygon21_rank1_fleet_mcts_transfer_result_v2.json                                                    | 2eeb28e1fcb1c48d826c387853ec4f9a8a1acf07c9d7e7d1c067701bd4a1398f |
| Fleet freeze v2    | polygon21_rank1_fleet_mcts_freeze_v2.json                                                             | b89d290c9cb06d1efb99688ee27b23898ab81d11e36023832477dc2fc834364b |

| **冻结事实**           | **值**                                                              |
|------------------------|---------------------------------------------------------------------|
| **冲突中心（约）**     | (4296.4686, 1754.2756) m                                            |
| **车型**               | XG90G，9 m × 4 m；rear-axle reference：front +6.5 m / rear -2.5 m。 |
| **Tag**                | fullmine-v4-polygon21-fleet-mcts-conflict-v1-20260815               |
| **Tag target**         | 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e                            |
| **地图 authoritative** | false；constructed research benchmark。                             |

## 11.2 NO-MCTS：必须先证明真实物理冲突

NO-MCTS baseline 固定 4.5 m/s，不允许 acceleration / waiting / artificial delay，用真实 XG90G footprint 每 0.1 s 检查物理重叠。两车 crossing time 几乎相同（约 11.11111 s），crossing gap≈5.43e-7 s；首次 overlap 9.6 s，最大 overlap 23.2148105 m² @ 10.7 s，最小 center distance 0.296334 m。因此“没有联合规划会冲突”是实际 runtime/几何证据，不是静态示意。

## 11.3 Fleet-MCTS seed0

| **指标**                                | **seed0**                                            |
|-----------------------------------------|------------------------------------------------------|
| **MCTS budget / depth**                 | 64 / 8                                               |
| **duration / iterations**               | 15.1 s / 151                                         |
| **A cross**                             | 7.319889502762444 s                                  |
| **B cross**                             | 12.556499511428344 s                                 |
| **crossing gap**                        | 5.2366100086659 s                                    |
| **first to cross**                      | A                                                    |
| **min physical footprint clearance**    | 2.065002410173625 m                                  |
| **min center distance**                 | 8.19564529606273 m                                   |
| **physical overlap / max overlap area** | False / 0.0 m²                                       |
| **timeline / speed cap / invalid**      | sync=True / speed_cap_ok=True / nan_or_invalid=False |
| **benchmark_success**                   | True                                                 |

## 11.4 五种子冻结结论

| **指标**                               | **5-seed freeze v2** |
|----------------------------------------|----------------------|
| **PASS / FAIL**                        | 5 / 0                |
| **crossing gap min**                   | 3.4379926855109115 s |
| **crossing gap mean**                  | 7.473227083985728 s  |
| **crossing gap max**                   | 14.40284379858401 s  |
| **minimum clearance across all seeds** | 1.2925053881999407 m |
| **first-to-cross**                     | A:3，B:2             |
| **parameter retuning**                 | False                |

## 11.5 Freeze v1 的“FAIL”为什么不能误读

第一次 freeze v1 出现的失败被最终分类为 \`HARNESS_STATIC_SUMMARY_SCHEMA_MISMATCH\`，不是静态路线、NO-MCTS 或 Fleet-MCTS 科学结果失败。最终 corrected freeze v2 验证 A/B static route exact、NO-MCTS conflict、Fleet 5/5、no retuning 后通过并绑定 annotated tag。v1 保留为 harness 错误历史证据，不删除，但不能作为最终冻结锚点。

# 12. FullMine 跨场景 Fleet-MCTS：当前只到 Static Readiness

2026-08-15 还做了跨场景 Fleet-MCTS 候选筛选。最终候选从原始 \[C09, C11, C06\] 按预登记 backup 顺序收敛为 \[C04, C11, C06\]，最终三场景 A/B 共 6 条路线通过 actual-planner refline、XG90G physical footprint 和 CollisionLookup 静态门控。

| **严禁错误表述：**这个分支目前只能写“static readiness closed”。real-loader、NO-MCTS causal-conflict 和 Fleet-MCTS dynamic experiments 尚未完成，cross-scene MCTS result count 在 static close 时仍为 0。不要写成“FullMine 跨场景 Fleet-MCTS benchmark 已完成”。 |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

该分支不阻塞当前 Neural-MCTS 数据集治理；如果后续论文需要跨场景 Fleet 统计，再从 frozen V4 / current path registry 另开动态实验分支。

# 13. 主线阶段七：原生 MineSim 可视化与汇报材料

用户明确拒绝“看起来像 AI 生成”的假地图/动画，因此汇报材料必须由真实 semantic/bitmap、真实 runtime state 和 MineSim 原生可视化链生成。Native Video 的目标不是制作宣传动画，而是把冻结 NO-MCTS/Fleet-MCTS 的真实运行放进 PlanVisualizer2D 体系，并生成可验证的 side-by-side 对照。

## 13.1 双车可视化最关键的状态问题

Multi-ego production integration 中，\`EnvironmentSimulation.history\` 在 dual mode 仍把 \`trajectories\['A'\]\` 作为 history trajectory；受控 B 的实时状态由 \`MultiEgoRuntime\` 管理。因此不能直接拿 SimulationHistory 假装包含 A/B 完整状态。Native V2 的解决方案是在保持每一帧 A 的原生 PlanVisualizer2D/history 对齐的同时，从同 iteration 的 MultiEgoRuntime 读取 live B state 并叠加到原生画面。没有使用 route_s 插值、CSV 坐标重建或像素反推。

## 13.2 Native Video V1 → V2

| **版本** | **问题/结果**                                                                                                        | **状态**                   |
|----------|----------------------------------------------------------------------------------------------------------------------|----------------------------|
| V1       | 原生 NO-MCTS raw dimensions 出现 (1545, 3666)，布局异常；即使科学链可跑，视觉/尺寸不满足正式汇报。                   | SUPERSEDED；保留历史证据。 |
| V2       | NO-MCTS/Fleet raw native dimensions 都为 (1545,1073)；10 fps 编码；side-by-side 145 frames；collision clip/preview。 | FINAL / PASS               |

| **V2 release**                    | **值**                                                                        |
|-----------------------------------|-------------------------------------------------------------------------------|
| **路径**                          | /root/autodl-tmp/Polygon21_Native_MineSim_Report_Video_v2_20260816_161259.zip |
| **SHA256**                        | f695ba22ecd61c4a643e8ffecac483bc218de9153f95f88b4e0e3006bca03d58              |
| **NO-MCTS frames**                | 145                                                                           |
| **Fleet frames**                  | 151                                                                           |
| **comparison frames**             | 145                                                                           |
| **NO-MCTS collision frame range** | 96:118                                                                        |
| **NO-MCTS peak overlap frame**    | 107                                                                           |
| **Quality Gate**                  | NATIVE_VIDEO_QUALITY_GATE=PASS；POLYGON21_NATIVE_MINE_SIM_VIDEO_RELEASE=PASS  |
| **正式 repo**                     | 渲染前后 status 保持 \`?? ^C\`，未改 frozen science。                         |

| **当前正式仿真视频：**Native MineSim V2 是当前正式汇报/证据版本。旧 GIF V4 ZIP 只作备份；Native V1 只作失败/修复 provenance。 |
|-------------------------------------------------------------------------------------------------------------------------------|

# 14. 2026-08-16 FullMine 全局地图展示：真实代码生成，不是 AI 图

这一分支是汇报侧任务，用于让观众直观看到“新 FullMine 整体长什么样、Polygon21 在哪里”。它不是闭环仿真结果，不应替代 Native MineSim 视频。所有地图几何必须直接读取 frozen semantic map。

## 14.1 V1：错误假设 GeoJSON FeatureCollection

V1 脚本对文件名中的 \`geojson\_\` 做了错误结构假设，要求顶层 \`type=FeatureCollection\`，但 MineSim semantic file 实际是 custom dict。脚本在 source SHA gate 后主动停止，没有为了出图猜 schema。这是正确失败方式。

## 14.2 真实 MineSim semantic schema 审计

8/16 只读审计确认顶层直接包含 node / polygon / road / intersection / loading_area / unloading_area / auxiliary_area / dubins_pose / reference_path / borderline 等列表；当前 frozen file 中 node=403,759、polygon=184、road=100、intersection=35、reference_path=553、borderline=402。六条 Polygon21 frozen path ID 均在真实 reference_path / polygon links 中找到。

| **Polygon21 frozen route** | **waypoint 数** |
|----------------------------|-----------------|
| A: path-000120             | 803             |
| A: path-000466             | 337             |
| A: path-000379             | 166             |
| B: path-000370             | 172             |
| B: path-000491             | 308             |
| B: path-000210             | 847             |

\`polygon-000021\` 被确认 type=intersection，并链接 \`path-000466\`、\`path-000491\` 等 connector；冲突点到 A/B 路线的最小距离分别约 0.000048 m / 0.000034 m，且在 Polygon21 内部。云端存在 Noto Sans CJK SC 字体，可用于中文汇报。

## 14.3 V2 与 V3 当前状态

| **版本**        | **事实**                                                                                                                                                          | **结论**                                                           |
|-----------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------|
| Map Showcase V2 | 3张4K PNG + 1080p/15fps/120帧视频；source/geometry/static/video quality gate PASS；release SHA 9f78f357eecfc25ea543d163e8d472dc06abeb1fff3215ed30577267750d1e14。 | 数据真实性/技术 PASS；作为当前稳定全局地图展示基线。               |
| Map Showcase V3 | 仅做 line hierarchy、panel、legend、camera timing 视觉升级；source/geometry/static PASS，120/120 帧完成；ffmpeg libx264 在编码时 SIGKILL:9。                      | INCOMPLETE；未生成最终 V3 release。不要把 SIGKILL 猜成已证实 OOM。 |

| **V3 以后怎么收尾：**只复用 \`/root/autodl-tmp/fullmine_map_showcase_v3_20260816_183153/frames\` 做低内存独立 ffmpeg 编码 + ffprobe + ZIP；不要重新渲染 120 帧。先读 cgroup memory.events，只有证据支持时才归因为 OOM。该任务不阻塞科研。 |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# 15. 汇报图片/视频统一标准

汇报材料的第一原则是“科研证据可视化，不是宣传海报”。任何 AI 接手后，不能为了好看用生成式图像重画地图/道路/轨迹。视觉参数可以调整，但科学数据、轨迹、冲突点、时间与净距不能改。

| **类别**                    | **标准**                                                                                                                               |
|-----------------------------|----------------------------------------------------------------------------------------------------------------------------------------|
| **真实性**                  | semantic-map / bitmap / runtime state / frozen result 是唯一数据源；禁止 AI 生成道路、截图描线、像素反推、route_s 伪重建。             |
| **静态图**                  | 优先 3840×2160 / 16:9；至少保留 FullMine 全局、Polygon21 局部、全局→局部组合图。                                                       |
| **视觉层级**                | A/B 路线 \> 冲突点 \> 路口边界 \> 普通道路 \> 辅助 reference line；A 蓝、B 橙、冲突红。                                                |
| **字体**                    | Noto Sans CJK SC；投屏可读，不塞长段说明。                                                                                             |
| **数值**                    | 画面可显示 5.24 s / 2.07 m 等四舍五入值；manifest/result 保留原始精度。                                                                |
| **Map Showcase Video**      | 1080p，约8s；V3设计节奏 0–1.5s 全局、1.5–4.2s平滑 zoom、4.2–8s局部 hold；只改变相机视野。                                              |
| **Native Simulation Video** | 必须使用真实 MineSim/PlanVisualizer2D/Runtime 状态；不能把 Map Showcase 叫实时仿真。                                                   |
| **四级 gate**               | Scientific/Data Integrity → Geometry Authenticity → Technical Quality → Human Final Report Visual Gate。四项全 PASS 才称正式汇报终版。 |

# 16. 主线阶段八：云端文件安全整理（Phase2A-2K）

用户明确要求“文件别丢失、代码路径慢慢改、安全优先”。因此整理不是批量移动全部文件，更不是清理磁盘；策略是 audit → 可逆移动/隔离 → exact dependency audit → 大对象关系审计 → final regression。任何存在绝对路径、runtime symlink 或用途不明确的对象优先保持原位。

<table>
<colgroup>
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>最终健康<br />
PASS</strong></th>
<th><strong>科研删除<br />
0</strong></th>
<th><strong>顶层条目<br />
530→121</strong></th>
<th><strong>移动/隔离<br />
423</strong></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## 16.1 最终目录体系

| **目录**                                     | **用途**                                                                                                |
|----------------------------------------------|---------------------------------------------------------------------------------------------------------|
| /root/autodl-tmp/00_MineSim_ACTIVE           | current_paths.json/env、当前快捷软链接、organization_tools。                                            |
| /root/autodl-tmp/10_MineSim_REPORTS          | 汇报/发布备份；不作为科学运行输入。                                                                     |
| /root/autodl-tmp/90_MineSim_ARCHIVE          | 可恢复历史归档：legacy planner、single MCTS、J117、FullMine development、superseded media、DR/bundles。 |
| /root/autodl-tmp/98_MineSim_QUARANTINE       | 隔离但未授权删除；当前约315.76MB。                                                                      |
| /root/autodl-tmp/99_MineSim_CLEANUP_MANIFEST | Phase1-2K audit、move plans、fingerprints、health、restore provenance。                                 |
| CURRENT/HOLD 原路径                          | 为绝对路径/软链接/冻结 runner 兼容保留，不强制塞入组织目录。                                            |

## 16.2 Current Path Registry

| **Key**                     | **Current absolute path**                                             |
|-----------------------------|-----------------------------------------------------------------------|
| **formal_repo**             | /root/MineSim-Dynamic                                                 |
| **polygon21_current**       | /root/autodl-tmp/fullmine_v4_dual_candidate_v1                        |
| **cross_scene_current**     | /root/autodl-tmp/fullmine_v4_fleet_cross_scene_v1                     |
| **representative_mcts**     | /root/autodl-tmp/fullmine_v4_mcts_representative_v1                   |
| **representative_coverage** | /root/autodl-tmp/fullmine_v4_representative_coverage_v1               |
| **production_truth_gap**    | /root/autodl-tmp/fullmine_v4_production_truth_gap_v1                  |
| **runtime_current**         | /root/autodl-tmp/fullmine_vector_v2_targeted_runtime                  |
| **semantic_source_current** | /root/autodl-tmp/new_map_fullmine_vector_v2_dev                       |
| **bitmap_source_current**   | /root/autodl-tmp/fullmine_vector_v4_d_current_planner_patch_candidate |
| **formal_mcts_results**     | /root/autodl-tmp/mcts_results                                         |
| **idm_baseline_backup**     | /root/autodl-tmp/minesim_idm_baseline_backup                          |
| **archive_root**            | /root/autodl-tmp/90_MineSim_ARCHIVE                                   |
| **cleanup_manifest_root**   | /root/autodl-tmp/99_MineSim_CLEANUP_MANIFEST                          |

## 16.3 Runtime 两条关键软链接：绝对不能随意搬

| **Runtime entry**                                                                                                        | **Resolved target**                                                                                                        |
|--------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------|
| /root/autodl-tmp/fullmine_vector_v2_targeted_runtime/maps/semantic_map/geojson_full_mine_vector_v2_dev_semantic_map.json | /root/autodl-tmp/new_map_fullmine_vector_v2_dev/maps/semantic_map/geojson_full_mine_vector_v2_dev_semantic_map.json        |
| /root/autodl-tmp/fullmine_vector_v2_targeted_runtime/maps/bitmap/geojson_full_mine_vector_v2_dev_bitmap_mask.png         | /root/autodl-tmp/fullmine_vector_v4_d_current_planner_patch_candidate/bitmap/geojson_full_mine_vector_v2_dev_only_mask.png |

## 16.4 Phase2A-2K 操作摘要

| **阶段** | **动作**                                                                 | **性质**              |
|----------|--------------------------------------------------------------------------|-----------------------|
| 2A       | 222历史 planner/report items 移入 archive                                | move，可恢复          |
| 2B       | 3项 quarantine（npm-cache / v4 DR restore test / malformed 0-byte）      | quarantine，可恢复    |
| 2C       | 28旧 map-development items archive；new_map_phase4c_tools 因真实引用保留 | move + HOLD           |
| 2D       | 广泛只读引用审计                                                         | read-only             |
| 2E       | exact path audit；整理工具收口；3项高置信 safe candidates                | read-only + org moves |
| 2F       | 12项 housekeeping，包括 superseded media / GIF backup                    | move，可恢复          |
| 2G       | 大对象 read-only inventory                                               | read-only             |
| 2H       | 大对象等价/唯一性关系审计                                                | read-only             |
| 2I       | 3个已验证 large duplicate/expanded artifacts archive                     | move，可恢复          |
| 2J       | 147 historical/debug/evidence top-level archive + final regression       | move，可恢复          |
| 2K       | final read-only closeout；HEAD/SHA/symlink/compile/restore gate          | read-only final       |

# 17. HOLD、归档、废弃版本与恢复机制

## 17.1 明确 HOLD（不要擅自移动/删除）

- \`/root/autodl-tmp/MineSim-Dynamic\`：约203.75MB 的独立脏历史工作区，不是正式 \`/root/MineSim-Dynamic\` 的简单重复；HOLD。

- \`new_map_phase4c_tools\`：已证实被 \`new_map_fullmine_vector_v2_dev\` 的 smoke 脚本真实引用；只有逐模块迁移后才处理。

- \`new_map_phase6c_full_mine_structural\`：受早期保护/历史依赖链约束；保留。

- \`fullmine_vector_v4_final_dr_20260814.tar.gz\`：完整 compact DR 恢复证据；保留。

- Polygon21 Native Video V2 生产脚本/包/source bundle：最终可复现链；保留。

- \`98_MineSim_QUARANTINE\` 中对象：隔离不等于授权删除。

- \`?? ^C\`：历史未跟踪零字节异常名；已知不在 commit/tag，禁止为追求“clean”执行 git clean。

## 17.2 已经被替代但应保留 provenance 的版本

| **对象**                               | **状态**             | **为什么不作为当前版本**                                          |
|----------------------------------------|----------------------|-------------------------------------------------------------------|
| IDM baseline / 94693dc MCTS baseline   | HISTORICAL/FROZEN    | 历史回归/算法证据，不是当前 FullMine source HEAD。                |
| FullMine V1                            | HISTORICAL           | 保守 structural/DEV mask；后续 Vector V2/V4 覆盖功能结论。        |
| P0/candidate v1/v2 bitmap              | IMMUTABLE HISTORICAL | 诊断过程与 additive provenance；不能覆盖。                        |
| stale v3_targeted_7of7_acceptance.json | INVALID / DO NOT USE | 混用旧结果世代；最终 7/7 以 current-planner final manifest 为准。 |
| Fleet freeze v1                        | HISTORICAL FAIL      | harness static-summary schema mismatch；final 用 freeze v2。      |
| Native Video V1                        | SUPERSEDED           | raw dimension/layout 异常；final 用 V2。                          |
| Polygon21_FleetMCTS_Report_GIFs_v4.zip | BACKUP ONLY          | 非当前正式原生视频。                                              |
| Map Showcase V1                        | FAILED DESIGN        | 错误假设 FeatureCollection；已被真实 schema V2 替代。             |
| Map Showcase V3                        | INCOMPLETE           | visual-only；120 frames complete，但编码 SIGKILL，未 release。    |

## 17.3 Restore scripts

| **Phase** | **Restore path**                                                                                           |
|-----------|------------------------------------------------------------------------------------------------------------|
| 2A        | /root/autodl-tmp/99_MineSim_CLEANUP_MANIFEST/phase2a_safe_move_20260816_165421/RESTORE_PHASE2A.sh          |
| 2B        | /root/autodl-tmp/99_MineSim_CLEANUP_MANIFEST/phase2b_safe_quarantine_20260816_170221/RESTORE_PHASE2B.sh    |
| 2C        | /root/autodl-tmp/99_MineSim_CLEANUP_MANIFEST/phase2c_safe_map_archive_20260816_170828/RESTORE_PHASE2C.sh   |
| 2F        | /root/autodl-tmp/99_MineSim_CLEANUP_MANIFEST/phase2f_safe_housekeeping_20260816_172708/RESTORE_PHASE2F.sh  |
| 2I        | /root/autodl-tmp/99_MineSim_CLEANUP_MANIFEST/phase2i_safe_large_archive_20260816_174051/RESTORE_PHASE2I.sh |
| 2J        | /root/autodl-tmp/99_MineSim_CLEANUP_MANIFEST/phase2j_final_safe_archive_20260816_174626/RESTORE_PHASE2J.sh |

恢复原则：先确认原路径不存在新的同名对象；再按原 manifest/RESTORE 脚本逆向恢复；恢复后复核 HEAD/status、关键 SHA、runtime symlink。冻结实验优先恢复历史路径，而不是修改冻结 runner 的绝对路径。

| **Final closeout**       | **值**                                                                              |
|--------------------------|-------------------------------------------------------------------------------------|
| 路径                     | /root/autodl-tmp/99_MineSim_CLEANUP_MANIFEST/phase2k_final_closeout_20260816_175006 |
| Closeout ZIP SHA         | e3d4ba27bd06c74c7ca23ed55de65208022f07d4e0cb600eb58bcbbcaaf33a4b                    |
| Final top-level count    | 121                                                                                 |
| Scientific files deleted | 0                                                                                   |

# 18. 固化工作流：ChatGPT、用户、Codex 与 AutoDL 的分工

这是项目安全性的组成部分，不是沟通偏好。任何新 AI 如果绕开这套工作流，很容易重复已验证阶段、误删历史资产、让 Codex 空耗卡时，或把一次局部失败扩大成全仓扫描。

| **角色/原则** | **强制规则**                                                                                                                                                          |
|---------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **ChatGPT**   | 负责事实梳理、决策、最小步骤设计、关键代码/patch、结果解释与门禁。                                                                                                    |
| **用户**      | 通常复制命令到云端执行，将真实 terminal output / artifact 回粘；保留最终开卡/付费决策。                                                                               |
| **Codex**     | 仅复杂算法设计、顽固 bug、适合云端自主执行的麻烦任务；默认 gpt-5.6-luna medium，仅必要时升级 Terra/Sol；一次只做当前最小步骤；只回 PASS/FAIL + 必要字段；不写长报告。 |
| **终端**      | Git/status/hash/file existence/简单 Python/Shell 等机械真值检查全部优先终端完成，不消耗模型。                                                                         |
| **长仿真**    | 普通终端/screen 后台运行并写进度/日志；避免 Codex 一直等待、反复查询。                                                                                                |
| **资源**      | 先免费完成 preflight/smoke/数据准备，再开高资源卡；高卡主要价值可能是 RAM/CPU，不默认等于 GPU 有收益。                                                                |
| **文件**      | 大文件、日志、临时脚本、results → /root/autodl-tmp；正式 repo 只保留必要 tracked source。                                                                             |
| **Git**       | 不 git clean -fd；不 reset --hard；不 git add .；只精确 stage 已审计文件。                                                                                            |
| **失败**      | 只定位当前 blocker，不重新扫描全部仓库，不重跑已冻结阶段。                                                                                                            |

## 18.1 强制测试阶梯

1.  只读 preflight：环境、HEAD/status、路径、SHA、依赖、输入文件。

2.  单步 smoke：语法/import/toy function/1–5 step，确认接口而非性能。

3.  短闭环：几十步/小场景，只验证 blocker 是否关闭。

4.  完整实验：只有前面 gate PASS 后才跑 full/5-seed/高资源。

5.  Freeze：result + manifest + SHA + tag（必要时）+ regression；随后默认不重做。

## 18.2 每段可执行代码的固定前缀

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>cd /root/MineSim-Dynamic<br />
source /root/miniconda3/etc/profile.d/conda.sh 2&gt;/dev/null || true<br />
conda activate minesim<br />
export PYTHONPATH=/root/MineSim-Dynamic<br />
export CUDA_VISIBLE_DEVICES=""</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

交互终端顶层绝不使用裸 \`exit\`。需要失败终止时，把逻辑放进子 shell \`(...)\`，或只打印 \`FAIL\`/返回码，让 SSH 会话保持。用户已经遇到过顶层 exit 关闭终端的问题，此规则必须长期保留。

## 18.3 AutoDL 资源真值

项目历史多次出现 \`free -h\` / \`nproc\` 显示宿主机级 1TiB/192 CPU，而真实容器可能仅约2GiB/低CPU。资源真值应优先读取 \`/sys/fs/cgroup/memory.max\`、\`memory.current\`、\`memory.events\`、\`cpu.max\`。地图/Shapely/Rasterio/Pillow/ffmpeg CPU 渲染通常不从 RTX 4090D 获得直接加速。

用户当前可选择的付费实例镜像为 PyTorch 2.1.0 / Python 3.10 / Ubuntu 22.04 / CUDA 12.1 / RTX4090D 24GB / 15 vCPU / 80GB，约￥1.88–1.98/小时；但现有 \`minesim\` 正式环境实际为 Python 3.9.25。未来神经训练不应为了使用新镜像覆盖现有仿真环境，优先隔离训练环境并做兼容性 smoke。

# 19. 故障处理手册：以后不能再重复的做法

| **不能再做**                                           | **正确替代**                                                                                   |
|--------------------------------------------------------|------------------------------------------------------------------------------------------------|
| 看到地图 boundary FAIL 就涂宽 bitmap                   | 禁止。先用官方 CarFootprint/物理 footprint + exact predicate 分类 false positive vs real gap。 |
| 看到 A2 停车就一直追 leading object                    | 禁止固化中间假设。A2 最终根因是 steering-rate infeasible；假设必须允许被后续证据推翻。         |
| 用 fixed offset/yaw 外推真实后续 footprint             | 禁止。B2 已证明会制造 227px 假缺口；只用 actual controller/shadow trajectory。                 |
| 四个 shadow 场景共用一个 Python 进程                   | 不推荐。状态/occupancy/stale frame 容易混；后续按单场景独立进程和 result provenance。          |
| 用 history 直接画 A+B                                  | 错误。dual history 主要记录 A；B 用 MultiEgoRuntime same-iteration live state。                |
| 用截图/视频像素重建地图/轨迹                           | 禁止。汇报几何必须直接读 semantic/reference_path/borderline/runtime state。                    |
| 因为目录乱就批量移动 frozen assets                     | 禁止。先 exact reference/symlink audit，逐模块迁移；current/HOLD 保持原位。                    |
| 因为有同名 \`/root/autodl-tmp/MineSim-Dynamic\` 就删除 | 禁止。它是独立 dirty historical repo copy，非简单 duplicate。                                  |
| 为了 clean 执行 git clean/reset                        | 禁止。\`?? ^C\` 等历史 untracked 不是项目失败；clean/reset 可能毁掉证据。                      |
| 长任务让 Codex 一直 wait/poll                          | 浪费钱。终端/screen 后台跑，输出进度文件，AI 只做决策与结果解释。                              |
| 把旧 Word 状态当当前状态                               | 禁止。8/09“J117 双车未做”、8/12“Vector V2 in progress”等都已被后续事实覆盖。                   |
| 把 harness/schema/后置 assert FAIL 当算法 FAIL         | 禁止。freeze v1 schema mismatch、1-step steps\>3 都已证明需要分层分类。                        |
| 把 production truth 说成已证明                         | 禁止。FullMine 是 Research/DEV baseline，权威 production drivability 仍未获得。                |

# 20. 主线阶段九：后续神经网络 / Neural-MCTS 接入

截至 2026-08-16，Neural-MCTS 训练仍然 NOT STARTED。当前项目已有 Pure MCTS expert schema、Dapai/Jiangtong 448 strict samples、FullMine representative decision logs 和通用 PyTorch/Lightning 基础设施，但 MCTS 目录里没有 dedicated ValueNetwork/PolicyNetwork/PolicyValueNetwork，也没有正式 checkpoint / PUCT 训练结论。

## 20.1 当前 raw inventory 不能直接叫训练集

| **来源**                    | **Raw samples**                                    |
|-----------------------------|----------------------------------------------------|
| FullMine candidate-0002     | 182                                                |
| candidate-0010 full         | 300（但 step83 已正式到 goal，之后继续记录）       |
| candidate-0010 1-step smoke | 1                                                  |
| candidate-0010 5-step smoke | 5                                                  |
| recovery-0005               | 186                                                |
| TOTAL_FULLMINE_SAMPLES      | 674（包含 smoke / 重复 / post-goal，不能直接训练） |

## 20.2 下一最小科学行动：Clean Dataset Builder

1\. 只读扫描 current expert records，冻结 source inventory；不修改 frozen result。

2\. 定义数据契约：state features、action index、root visit distribution、return/value label、obstacle snapshot、normalization provenance。

3\. 按 formal goal history 截断；删除 smoke、重复、post-goal 样本；每条记录携带 scenario/source/freeze SHA。

4\. 按 scenario / episode 做 train/validation/test split；禁止随机逐行 split。

5\. 生成 dataset manifest：输入文件 SHA、保留/删除计数、理由、split group、schema version。

6\. 先做 CPU 级 parser/one-batch/small-model smoke；只有数据 gate 和训练代码 smoke 都 PASS 后才考虑开 4090D。

| **完成标准：**dataset builder 输出可重复、无 smoke/post-goal 泄漏、每条样本可追溯到 frozen source，split 不跨同一 episode，且整个过程不修改 112d2bd frozen runtime。达到此标准后，才进入 Value Network / Policy-Value / PUCT 的模型实验。 |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

## 20.3 可研究的 Neural-MCTS 路线

历史 Budget 消融表明固定高预算存在状态无关冗余。因而 Neural 阶段更有价值的方向是：Value Network 替代部分 rollout、Policy prior + Value 进入 PUCT、adaptive search budget、tree reuse，而不是直接把固定 Budget 300 套到所有状态。具体网络层数/隐藏维度/最终 reward 权重不能由 AI 单方面决定，必须由冻结数据与实验指标确定。

# 21. 可选未来工程分支：FullMine 自有可视化层（尚未开始）

2026-08-16 讨论过把 MineSim 原始可视化逐步转成项目自己的视觉体系，但用户明确决定“先不做”。因此这里只记录设计，不视为已实现成果。

- 近期可安全改：颜色、字体、线宽、透明度、车辆配色、HUD、legend、导出图片/视频；这些属于 visualization theme，不应影响 simulation state。

- 更关键的中间层设想：MineSim / MultiEgoRuntime → \`SimulationSnapshot\` → \`FullMineRenderer\`，统一 A/B/other actor、planning、safety、map state，再输出 Research / Report / Video mode。

- 如果实现，目标是减少 renderer 对 EnvironmentSimulation/MultiEgoRuntime 零散内部对象的直接依赖，并为未来 Neural planner 保持相同显示接口。

- 这不是“换颜色就叫自研平台”。若底层仍基于 MineSim，论文/汇报应准确表述为“基于 MineSim 构建的 FullMine-CoSim 多车协同仿真与可视化平台”等，软件 license/attribution 在正式开源前另做审计。

| **当前状态：**DESIGN DISCUSSION ONLY / NOT STARTED；不是当前 blocker，也不是 Neural-MCTS 前置条件。 |
|-----------------------------------------------------------------------------------------------------|

# 22. 当前关键 Commit / Tag / SHA 速查

| **里程碑**               | **Commit**                               | **Tag/语义**                                 |
|--------------------------|------------------------------------------|----------------------------------------------|
| IDM baseline             | 2521aa41a69a6e734c04c15a715e9530c8095ac3 | idm-replay-autodl-baseline                   |
| Pure MCTS + expert       | 94693dc799fe5f325a75e8fc6d7d5e88764b4799 | mcts-expert-dataset-v1-20260802              |
| Fleet internal reward    | f8ff1866789ed3d9d878f34b7cd34ab490e40121 | 历史多车节点                                 |
| Jiangtong V22            | 94794c963f9c3eaf1873b275df6d319ca2636817 | jiangtong-v22-benchmark-screening-20260809   |
| J117 Phase3              | 4bd2bff28c593ee80ab8c9fe2eefecd2b009e9b6 | j117-phase3-production-map-load-20260809     |
| J117 Phase4C base        | ec1c958735b0ee76201284faacb46fccc75c7f6c | j117-phase4c-single-ego-closed-loop-20260810 |
| J117 Phase5              | da4105b836dbbd3e702ee25fbb364109bc4e2596 | j117-phase5-dual-ego-pure-mcts-20260810      |
| FullMine lookup          | 32fb42920d8cc404b37cd25dc47cbc6fbde4d9f4 | token2ind O(1)                               |
| FullMine V1 registration | d81c57154e4e5d0b4df1251cf565d9aacffaa026 | fullmine-dev-runtime-pass-20260811           |
| CURRENT V4 freeze        | 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e | fullmine-vector-v4-runtime-freeze-20260814   |

| **资产**                    | **SHA256**                                                                                       |
|-----------------------------|--------------------------------------------------------------------------------------------------|
| FullMine semantic runtime   | b85a3d8b28f2252ecb5bda179d514573f6333079def838cd048566f556d95cd0                                 |
| FullMine V4 bitmap runtime  | 51abcd5a86e5c510204a5dacc873691506d721f98982ab7f98585d4e0f7efdd0                                 |
| Polygon21 Scenario          | 362eff18c7ccc88ea8dfaf083a517603566516943690d5cbe76bd1a97afc89e1                                 |
| Polygon21 Scenario manifest | 0bde6bb1e869c3cf583947203dd41a8fc364f0a2a8130617baebd0b1e6cbad2e                                 |
| NO-MCTS result              | 060880c8edc851e05606871cb647058d091ce8737f952b9864cc94e9d6fcfd13                                 |
| Fleet result seed0          | 2eeb28e1fcb1c48d826c387853ec4f9a8a1acf07c9d7e7d1c067701bd4a1398f                                 |
| Fleet freeze v2             | b89d290c9cb06d1efb99688ee27b23898ab81d11e36023832477dc2fc834364b                                 |
| Native Video V2 release     | f695ba22ecd61c4a643e8ffecac483bc218de9153f95f88b4e0e3006bca03d58                                 |
| Map Showcase V2 release     | 9f78f357eecfc25ea543d163e8d472dc06abeb1fff3215ed30577267750d1e14                                 |
| Map Showcase V3 scripts ZIP | 83b800cddf07a5043992badfadba644b41c5b66cd2188180b7a87fd78252692c（脚本包，不是 final V3 output） |
| Phase2K closeout ZIP        | e3d4ba27bd06c74c7ca23ed55de65208022f07d4e0cb600eb58bcbbcaaf33a4b                                 |

# 23. 快速接手区（下一位 AI 必须先读）

| **一句话当前状态：**FullMine Vector V4 Research Map 已冻结；Representative Pure MCTS 3/3 与 Polygon21 Fleet-MCTS 5/5 已冻结；Native MineSim V2 汇报 release 已完成；云端 Phase2K 安全整理完成；当前科学下一阶段是 Neural-MCTS clean dataset builder，训练尚未开始。 |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

## 23.1 哪些已经冻结，默认不要重做

- MineSim IDM baseline / Dapai/Jiangtong 原基线。

- Pure MCTS Dapai/Jiangtong 正式结果与 448 expert samples。

- J117 Phase4C 单车 full-route。

- J117 Phase5 dual-ego Pure MCTS 5-seed + swept safety。

- FullMine Vector V4 semantic/bitmap/runtime/planner fixes、targeted 7/7、旧图回归、commit/tag。

- Representative Coverage v1 与 Representative Pure MCTS 3/3。

- Polygon21 NO-MCTS physical conflict 与 Fleet-MCTS 5/5 freeze v2。

- Polygon21 Native MineSim Report Video V2。

- 云端 Phase2A-2K 文件整理及 restore provenance。

## 23.2 当前绝对不能随意动的路径/对象

- \`/root/MineSim-Dynamic\`：唯一正式 Git repo。

- \`/root/autodl-tmp/fullmine_vector_v2_targeted_runtime\`：当前 runtime root。

- \`/root/autodl-tmp/new_map_fullmine_vector_v2_dev\`：semantic resolved target。

- \`/root/autodl-tmp/fullmine_vector_v4_d_current_planner_patch_candidate\`：bitmap resolved target。

- \`/root/autodl-tmp/fullmine_v4_dual_candidate_v1\`：Polygon21 frozen work/evidence。

- \`/root/autodl-tmp/99_MineSim_CLEANUP_MANIFEST\`：整理 provenance / restore。

- \`/root/autodl-tmp/MineSim-Dynamic\`：dirty historical repo HOLD，不是正式 repo，但不能删。

- \`new_map_phase4c_tools\`：真实当前引用 HOLD。

- \`98_MineSim_QUARANTINE\`：没有删除授权。

## 23.3 当前 HOLD / 未证明

| **对象**                                                      | **当前准确状态**                                                                                 |
|---------------------------------------------------------------|--------------------------------------------------------------------------------------------------|
| Production-authoritative FullMine drivability                 | NOT PROVEN；需要数据方 authoritative mask/drivable surface/internal exclusions/authoring rules。 |
| Cross-scene C04/C11/C06 Fleet benchmark                       | 仅 static readiness；dynamic NO-MCTS/Fleet 未做。                                                |
| Neural-MCTS                                                   | training NOT STARTED；dedicated MCTS Value/Policy network 未建立。                               |
| Map Showcase V3                                               | 120 frames complete；ffmpeg SIGKILL；final release 未生成；side-task。                           |
| 真实 FullMine 现场车型                                        | 若不是 XG90G，需独立 vehicle config + footprint/mask 重评；当前没有权威确认。                    |
| gear=-1 的运营语义、elevation datum、official slope smoothing | 未权威确认；保持已有 provenance/flag。                                                           |
| 自有 FullMine visualization middleware/platform               | 只讨论设计，NOT STARTED。                                                                        |

## 23.4 接手后第一轮只读 Preflight

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>cd /root/MineSim-Dynamic<br />
source /root/miniconda3/etc/profile.d/conda.sh 2&gt;/dev/null || true<br />
conda activate minesim<br />
export PYTHONPATH=/root/MineSim-Dynamic<br />
export CUDA_VISIBLE_DEVICES=""<br />
<br />
(<br />
echo "===== ENV / GIT ====="<br />
pwd<br />
echo "ENV=$CONDA_DEFAULT_ENV"<br />
python --version<br />
git branch --show-current<br />
git rev-parse HEAD<br />
git status --short<br />
<br />
echo "===== CURRENT PATH REGISTRY ====="<br />
cat /root/autodl-tmp/00_MineSim_ACTIVE/current_paths.json 2&gt;/dev/null || echo "CURRENT_PATHS=FAIL"<br />
<br />
echo "===== RUNTIME LINKS ====="<br />
readlink -f /root/autodl-tmp/fullmine_vector_v2_targeted_runtime/maps/semantic_map/geojson_full_mine_vector_v2_dev_semantic_map.json<br />
readlink -f /root/autodl-tmp/fullmine_vector_v2_targeted_runtime/maps/bitmap/geojson_full_mine_vector_v2_dev_bitmap_mask.png<br />
<br />
echo "===== CORE SHA ====="<br />
sha256sum /root/autodl-tmp/fullmine_vector_v2_targeted_runtime/maps/semantic_map/geojson_full_mine_vector_v2_dev_semantic_map.json /root/autodl-tmp/fullmine_vector_v2_targeted_runtime/maps/bitmap/geojson_full_mine_vector_v2_dev_bitmap_mask.png /root/autodl-tmp/fullmine_v4_dual_candidate_v1/Scenario-fullmine-v4-polygon21-rank1-dual-aligned.json /root/autodl-tmp/fullmine_v4_dual_candidate_v1/polygon21_rank1_fleet_mcts_freeze_v2.json<br />
<br />
echo "===== CGROUP ====="<br />
cat /sys/fs/cgroup/cpu.max 2&gt;/dev/null || true<br />
cat /sys/fs/cgroup/memory.max 2&gt;/dev/null || true<br />
cat /sys/fs/cgroup/memory.current 2&gt;/dev/null || true<br />
<br />
echo "PREFLIGHT=COMPLETE"<br />
)</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## 23.5 Preflight 期望与异常处理

| **检查**            | **期望/规则**                                                                   |
|---------------------|---------------------------------------------------------------------------------|
| HEAD                | 期望 \`112d2bd0f3412fc83b13d5587d2b41402d2d0f5e\`；不一致时只读调查，不 reset。 |
| status              | 历史最后已知 \`?? ^C\`；如果新增 tracked diff，先 diff，不 clean。              |
| branch              | 8/16 最后输出未再次显示，不能凭历史假定；只读记录实际 branch。                  |
| semantic SHA        | b85a3d8…95cd0                                                                   |
| bitmap SHA          | 51abcd5…efdd0                                                                   |
| Polygon21 freeze v2 | b89d290…364b                                                                    |
| symlink             | resolved target 必须仍指向 current semantic / V4 bitmap roots。                 |
| cgroup              | 作为实际 CPU/RAM 真值；不要用宿主机 nproc/free -h 直接决定开卡。                |

## 23.6 下一步最小行动（科学主线）

| **NEXT_ONE_STEP：**只读盘点现有 Dapai/Jiangtong 448 expert + FullMine representative raw logs，建立 Neural-MCTS dataset contract / builder 设计清单。不要训练、不要改 frozen runtime、不要开高资源卡。 |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

| **完成标准**        | **必须满足**                                                                 |
|---------------------|------------------------------------------------------------------------------|
| **Input inventory** | 每个 source file / episode / scenario / result/freeze SHA 可追溯。           |
| **Goal truncation** | candidate-0010 等按 formal goal history 截断，post-goal 不进 clean dataset。 |
| **Dedup/smoke**     | 1-step/5-step smoke 和重复样本明确剔除并计数。                               |
| **Schema**          | state/action/visits/Q/reward/label/obstacle/provenance 字段固定版本。        |
| **Split**           | 按 scenario/episode 分组；无随机逐行 leakage。                               |
| **Output**          | clean dataset manifest + counts + SHA；不需要 GPU。                          |

## 23.7 什么时候才开 4090D

只有当 dataset builder、split、训练代码 import/compile、one-batch 或小模型 smoke 都 PASS，且下一步确实需要 PyTorch 训练吞吐时才开高资源卡。开卡前先把训练输入、checkpoint 目录、配置与日志路径准备好；开卡后避免重新做 Git/hash/map audit。当前 map/可视化/数据清洗步骤不需要 GPU。

## 23.8 下一位 AI 的回答格式建议

接手后第一轮不要重述整本手册，只需要输出四项：\`CURRENT_STATE\`、\`DIFF_FROM_EXPECTED\`、\`NEXT_ONE_STEP\`、\`RISKS/HOLD\`。如果所有 preflight 与文档一致，直接推进 dataset builder preflight。

# 附录 A. 当前目录与科学/汇报资产边界

| **类别**           | **应放位置**                                          | **注意**                              |
|--------------------|-------------------------------------------------------|---------------------------------------|
| 正式源码           | /root/MineSim-Dynamic                                 | 只放必要 tracked source；精确 stage。 |
| 当前科学 workspace | /root/autodl-tmp/\<versioned_workspace\>              | 登记到 current_paths；避免顶层散落。  |
| 正式结果           | /root/autodl-tmp/mcts_results 或当前 frozen workspace | result/manifest/SHA/freeze 绑定。     |
| 汇报图片/视频      | /root/autodl-tmp/10_MineSim_REPORTS/\<topic\>/        | 不作为仿真输入。                      |
| 历史实验           | /root/autodl-tmp/90_MineSim_ARCHIVE/\<category\>/     | 可恢复，不删除。                      |
| 暂不能删           | /root/autodl-tmp/98_MineSim_QUARANTINE                | 必须另行授权。                        |
| 审计/restore       | /root/autodl-tmp/99_MineSim_CLEANUP_MANIFEST          | 长期保留 provenance。                 |
| 运维工具           | /root/autodl-tmp/00_MineSim_ACTIVE/organization_tools | 不要再散落顶层。                      |

# 附录 B. 最终口径：论文/汇报中能说与不能说

| **可以严谨地说**                                                                                       | **不能说**                                           |
|--------------------------------------------------------------------------------------------------------|------------------------------------------------------|
| Pure MCTS 已进入 MineSim online closed-loop，并在已评估 Dapai/Jiangtong 正式基线中得到 2/2 Safe Goal。 | MCTS 已证明在所有矿山场景全面优于所有规划器。        |
| J117 是 real-map constructed benchmark，NO-MCTS 有真实重叠，Pure MCTS 5-seed/swept safety 通过。       | J117 是 MineSim 原项目第三张官方成品地图。           |
| FullMine Vector V4 是可恢复、可复现、可承载算法实验的 Research/DEV baseline。                          | FullMine V4 是官方 production-authoritative HD Map。 |
| Polygon21 NO-MCTS 发生 physical overlap，Fleet-MCTS 5/5 无重调参通过。                                 | 5/5 即证明全矿/所有种子绝对安全。                    |
| Native V2 是真实 MineSim/Runtime 状态生成的汇报视频。                                                  | Map Showcase 是实时仿真。                            |
| Neural-MCTS 有 expert schema 和 raw inventory，readiness 已审计。                                      | Neural-MCTS 已训练或已有正式网络/checkpoint。        |
| 云端已完成可逆安全整理，科研文件 0 删除。                                                              | ARCHIVE/QUARANTINE 都是垃圾、可以直接 rm。           |

# 附录 C. 文档维护规则

- 每次新的 frozen science milestone，追加“日期、commit/tag、result/freeze SHA、路径、PASS gate”，不要把旧阶段文字原地改成新事实。

- 若文件路径因后续安全迁移改变，优先更新 \`current_paths.json\` 和本手册 Current Path Registry；冻结 runner 的历史绝对路径不要批量 search/replace。

- 若新 live terminal 与本手册冲突，把冲突标成“旧快照已被覆盖”，不要为了让文档一致而 reset 云端。

- 新增论文结论必须区分：已有研究/系统提供了什么 → 本项目做了什么 → 解决了什么具体问题 → 证据是什么；不得把实现工作包装成无证据的普适创新。

- 任何 AI 生成新的 Word/报告前，应先核验最终 HEAD、关键 SHA、current_paths 和最新 freeze，不从文件名猜“final”。

| **本手册的最终作用：**下一位 AI 不应重新问“项目做到了哪里、地图在哪、MCTS 跑过没有、双车 benchmark 有没有、哪些能删”。它应在 5–10 分钟内完成只读 preflight，并把工作直接推进到当前未完成的最小 gate。 |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
