**MineSim-Dynamic**

**全项目阶段性总总结与 AI 无缝接管手册**

*MineSim 复现 → 蒙特卡洛/MCTS 接入 → 单车跑通 → 双车冲突场景构建 → FullMine 新地图接入 → Fleet-MCTS 双车联合规划与多种子验证 → 原生 MineSim 可视化与汇报材料 → 云端文件安全整理 → 后续神经网络接入*

| **文档定位** 本文件面向下一位 AI / 工程人员。目标是在不重新扫描整个项目、不重复已冻结实验、不重新询问大量背景的前提下，安全、低成本地从当前节点继续。事实优先级为：当前 AutoDL 终端/Git/SHA/源码/实际输出 \> 冻结结果与 manifest \> 最新交接文档 \> 历史文档 \> 设计计划。缺少直接证据的一律标为“未验证/HOLD”。 |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

| **对象/阶段**                       | **状态**                            | **当前准确结论**                                                                                                                                                       |
|-------------------------------------|-------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **正式科学仓库**                    | FROZEN                              | HEAD 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e；tag fullmine-vector-v4-runtime-freeze-20260814；8/21 全部旁路脚本均 REPO_UNCHANGED=PASS。                               |
| **核心仿真与地图链**                | PASS / FROZEN                       | IDM baseline、Pure MCTS、J117 single/dual、FullMine Vector V4、Representative Pure MCTS 3/3、Polygon21 Fleet 5/5 已冻结，不得重做。                                    |
| **Cross-scene C04/C11/C06**         | CLOSED WITH NEGATIVE                | C04/C06 success；C11 无碰撞但安全死锁。C11 负结果是合作/进度价值学习的真实动机，禁止调参抹掉。                                                                         |
| **Paper1 safety sidecars**          | FROZEN / OBSERVATIONAL              | V2R、runtime heading、approach、Omega_int、pair binding/Omega_app、Dynamic V2V 已冻结；未改变 behavior/reward/search/pruning。                                         |
| **Shadow safe-node**                | PASS / HARD PRUNING NOT APPROVED    | C04 8064 child observations；20 次 root 16/16 全被 MS_LOW 判 unsafe；22 个真实执行动作也被 reject，证明 shadow label 只能作辅助风险特征。                              |
| **Current-semantic neural dataset** | PASS                                | C04+C11+C06 共 1162 roots / 18592 root-action rows；按整个 scene/episode 分组，禁止 random row split。                                                                 |
| **Value Network V1**                | PIPELINE PASS / GENERALIZATION FAIL | C04 单 episode pipeline 跑通；三场景 LOSO 跨场景排序失败，PROVISIONAL_VALUE_GUIDANCE_READY=False，禁止接入 MCTS。                                                      |
| **当前唯一 next**                   | PREPARED / NOT RUN                  | 运行 Value Network V2 interaction/target probe：joint-action×relative-state interaction，比较 root-centered Q、root-zscore Q、residual-to-immediate。低资源 CPU 即可。 |

证据截止：2026-08-21。当前 8/21 云端可复核完成项来自 AI/脚本与用户 AutoDL 终端真实执行；现有证据没有为每个文件提供独立 Codex 作者标记，因此本文不虚构“某文件由 Codex 完成”的归属。

**目录与阅读顺序**

| **章节** | **主题**                                                 |
|----------|----------------------------------------------------------|
| **0**    | 文档使用规则、证据等级与 AI/Codex 归属边界               |
| **1**    | 当前项目 30 秒状态、真实发展时间线与 2026-08-21 完成清单 |
| **2**    | 运行架构、核心调用链、关键代码与目录依赖                 |
| **3**    | 阶段一：MineSim 原项目复现与 IDM Baseline                |
| **4**    | 阶段二：蒙特卡洛 / Pure MCTS 接入与单车跑通              |
| **5**    | 阶段三：双车冲突场景、MultiEgoRuntime 与 J117            |
| **6**    | 阶段四：FullMine 新地图接入、Vector V2 → V4 冻结         |
| **7**    | 阶段五：Fleet-MCTS 双车联合规划、多种子与跨场景结论      |
| **8**    | 阶段六：原生 MineSim 可视化、Native Video 与汇报材料     |
| **9**    | 阶段七：云端文件安全整理、目录体系与恢复机制             |
| **10**   | 阶段八：Paper1 safety/data/value 前置与神经网络真实进展  |
| **11**   | 重要问题、失败、原因、修复与永久禁忌                     |
| **12**   | 当前有效版本、SUPERSEDED/HOLD/未验证对象                 |
| **13**   | 环境、资源、依赖、运行与恢复规范                         |
| **14**   | 用户—ChatGPT—Codex 协作规则与成本控制                    |
| **15**   | 云端文档生成、归档、移动与删除情况                       |
| **16**   | 关键 Commit / Tag / SHA / 冻结证据速查                   |
| **17**   | 证据来源索引与冲突处理原则                               |
| **18**   | 快速接手区：下一位 AI 必须先读                           |

**0. 文档使用规则、证据等级与 AI/Codex 归属边界**

| **事实原则** 最新 AutoDL 终端 / Git / SHA / 源码 / 实际运行输出 \> frozen result/manifest/bundle \> 最新交接文档 \> 历史文档 \> 设计计划 \> 模型记忆。文件名含 final/pass/v2/freeze 不等于通过，必须解析内容与 gate。 |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

| **等级**     | **含义**                                   | **使用规则**                       |
|--------------|--------------------------------------------|------------------------------------|
| **V-LIVE**   | 当前云端 Git、源码、文件、SHA、运行输出    | 最高优先级；每次重连先只读核验。   |
| **V-FROZEN** | result / manifest / SHA / tag / frozen ZIP | 长期锚点；默认不重跑、不覆盖。     |
| **V-DOC**    | 正式 Word、整理说明、历史手册              | 补足演进；若与更晚终端冲突则降级。 |
| **V-DESIGN** | 未来方案、论文适配、网络设计               | 不能写成已完成。                   |
| **HOLD**     | 来源/语义不足、外部权威缺失或禁止擅动      | 不得以常识补齐。                   |

| **术语**                   | **准确含义**                                    |
|----------------------------|-------------------------------------------------|
| **PASS**                   | 当前门禁通过。                                  |
| **FROZEN**                 | 绑定可复核证据，默认不重做。                    |
| **HISTORICAL**             | 历史有效，但不是当前科学/生产版本。             |
| **SUPERSEDED**             | 被后续版本替代，但必须保留 provenance。         |
| **FAIL-EVIDENCE**          | 失败本身是有效诊断证据，不能删除或改写成 PASS。 |
| **INCOMPLETE**             | 部分产物完成，但未形成正式 release。            |
| **DEVELOPMENT EVIDENCE**   | 已用于方案选择，不能再当最终独立泛化验证。      |
| **HOLD / NOT IMPLEMENTED** | 未验证、未实现或不具备授权，禁止写成已完成。    |

**AI/Codex 归属边界：**2026-08-21 的全部关键结论都有云端脚本/终端输出、ZIP、JSON 或 SHA 支撑，但现有包未提供可靠的逐文件 Codex 作者签名。本文统一表述为“AI/脚本 + 用户 AutoDL 终端实际执行”。Codex 的默认模型、升级策略与任务边界属于用户固化的协作规则，不等于每个 8/21 文件都由 Codex 生成。

**1. 当前项目 30 秒状态、真实发展时间线与 2026-08-21 完成清单**

| **一句话定义** MineSim-Dynamic 是面向露天矿无人矿卡规划的真实 closed-loop 仿真与算法验证工程。当前已从原 MineSim IDM/replay 复现，推进至 Pure MCTS、双受控 Fleet-MCTS、FullMine Research/DEV 地图、原生可视化、Paper1 safety sidecars 和 current-semantic Value Network 数据链。神经网络已经“介入并训练”，但尚未被批准接入 MCTS。 |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

| **主线阶段**           | **状态**                         | **当前最准确结论**                                                                                            |
|------------------------|----------------------------------|---------------------------------------------------------------------------------------------------------------|
| **MineSim 复现**       | PASS / FROZEN                    | Dapai/Jiangtong IDM、replay 与 closed-loop baseline 建立；commit/tag 可回归。                                 |
| **蒙特卡洛/MCTS 接入** | PASS / FROZEN                    | Pure MCTS 进入 MineSim online closed-loop；Dapai199 + Jiangtong249 = 448 strict historical expert。           |
| **单车跑通**           | PASS / FROZEN                    | J117 Phase4C 423-step full route；FullMine Representative Pure MCTS 3/3。                                     |
| **双车冲突构建**       | PASS / FROZEN                    | J117 与 Polygon21 建立“NO-MCTS 会发生真实物理重叠”的 causal benchmark。                                       |
| **FullMine 新地图**    | PASS / FROZEN                    | Vector V2 semantic + V4 bitmap/runtime/planner；targeted 7/7 + old-map regression。                           |
| **Fleet-MCTS**         | PASS + NEGATIVE RESULT           | Polygon21 5/5；C04/C06 成功；C11 安全但死锁，反证 universal success。                                         |
| **原生可视化**         | PASS / FROZEN                    | Native Video V2 final；Map Showcase V2 stable；V3 incomplete。                                                |
| **云端整理**           | PASS / COMPLETE                  | Phase2A–2K；约 530→121；423 move/isolate；科研文件删除 0；restore gate PASS。                                 |
| **Paper1 safety/data** | PASS / FROZEN                    | V2R、heading/approach、Omega_int、pair binding、dynamic V2V、shadow、dataset contract 与 collector 链已完成。 |
| **神经网络**           | FORMAL TRAINING DONE / NOT READY | C04 smoke PASS；three-scene LOSO generalization FAIL；V1 不得接入 MCTS；V2 interaction/target probe 已准备。  |

**1.1 真实演进时间线**

| **日期**              | **阶段**                              | **可复核结果/意义**                                                                                                                   |
|-----------------------|---------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------|
| **2026-07-26**        | 云端 baseline / 安全操作规范          | 建立 AutoDL 安全交互、Git 恢复、文件优先与“先读接口再改代码”的纪律。                                                                  |
| **2026-07-30～08-02** | Pure MCTS closed-loop                 | MCTSPlanner → state/action/search/reward → trajectory adapter → Controller/KBM；commit 94693dc；448 strict expert。                   |
| **2026-08-03～07**    | 五 Planner / budget / interface audit | MCTS、IDM、Frenet、Adapted Maneuver、Simple；形成算法能力边界和 trajectory adapter 故障分域。                                         |
| **2026-08-08～10**    | 双受控 + J117                         | Jiangtong 负筛选；J117 单车 423 steps；双车 NO-MCTS conflict + Pure MCTS 5-seed。                                                     |
| **2026-08-11～14**    | FullMine V1 → Vector V4               | O(1) token lookup、Vector V2 semantic、bitmap/runtime/planner 修复、V4 freeze HEAD 112d2bd。                                          |
| **2026-08-14**        | Representative Pure MCTS              | 跨代表区域 3/3 PASS 并冻结。                                                                                                          |
| **2026-08-15**        | Polygon21 Fleet-MCTS                  | NO-MCTS 真实物理重叠；Fleet budget64/depth8 5/5；freeze v2。                                                                          |
| **2026-08-16**        | Native Video + safe cleanup           | Native MineSim Video V2 final；Phase2A–2K safe cleanup；Map Showcase V3 SIGKILL 未收口。                                              |
| **2026-08-17～18**    | Cross-scene + Paper1 safety start     | C04/C11/C06 动态收口；C11 安全死锁；SafetyRisk V0 observational freeze；V2R 推进。                                                    |
| **2026-08-21**        | Safety sidecar → current-semantic NN  | V2R/zone/dynamic V2V/shadow/dataset/collector 全链完成；C04 NN smoke；C11/C06 recollection；three-scene LOSO；V1 failure diagnostic。 |

**1.2 2026-08-21 云端实际完成项（按证据，不虚构作者归属）**

| **完成项**                              | **状态**                         | **关键结果 / SHA**                                                                                                | **资源与流程**                          |
|-----------------------------------------|----------------------------------|-------------------------------------------------------------------------------------------------------------------|-----------------------------------------|
| **Continuous V2R V3**                   | FROZEN PASS                      | C04 126-step full parity；V2R freeze SHA 0231cda7…；authoritative Fleet/V0 均保持。                               | 先低资源 static，再高资源 3-step/full。 |
| **Runtime heading + approach**          | FROZEN PASS                      | RouteAdapter heading；C04/C11/C06 approach=70/80/100m；freeze SHA a27653c2…。                                     | 低资源。                                |
| **Omega_int + pair binding/Omega_app**  | FROZEN PASS                      | Omega_int SHA a6b1de3c…；AND_BOTH binding/Omega_app SHA 2e516d95…。                                               | 低资源。                                |
| **Dynamic V2V d_safe sidecar**          | FROZEN PASS                      | 126 records；behavior/reward/search/pruning unchanged；freeze SHA 3bcbbcb3…。                                     | 高资源 full126，GPU禁用。               |
| **Shadow safe-node**                    | OBSERVATION PASS                 | 8064 child；359 depth1 reject；20 roots 16/16 reject；22 selected actions reject；hard pruning not approved。     | static→3-step→full。                    |
| **Neural Dataset Contract V1**          | FROZEN V1                        | root-search raw unit；root×joint-action derived unit；Q primary；visits/margin/outcome auxiliary；SHA 46f2e099…。 | 低资源。                                |
| **C04 Root Diagnostic Collector**       | PASS                             | 126 roots/2016 action rows；Q std 15.1987；behavior parity；result ZIP SHA daa9bc9e…。                            | static→smoke→full+salvage。             |
| **C04 Value Network pipeline smoke**    | PASS / NON-FORMAL                | 24→64→64→1；train Pearson 0.880；checkpoint SHA 6c223729…；no generalization claim。                              | CPU torch 2.8.0。                       |
| **C11/C06 current-semantic collection** | PASS                             | C11 890 roots/14240 rows deadlock；C06 146 roots/2336 rows success；combined ZIP SHA 94ec9778…。                  | screen，高资源，GPU禁用。               |
| **Three-scene LOSO Value V1**           | FORMAL SPLIT PASS / SCIENCE FAIL | 18592 rows；3-fold leave-one-scene-out；readiness=False；result ZIP SHA 7c296200…。                               | 低资源 CPU。                            |
| **Value V1 failure diagnostic**         | PASS                             | Decision=DO_NOT_INTEGRATE_VALUE_NETWORK_INTO_MCTS；result ZIP SHA d16b2f08…。                                     | 低资源，无重训。                        |
| **Value V2 interaction/target probe**   | PREPARED / NOT RUN               | Delivery SHA e14aafd8…；比较 root-centered Q、root-zscore Q、residual-to-immediate；不跑仿真、不接MCTS。          | 当前唯一 next，低资源。                 |

**2. 运行架构、核心调用链、关键代码与目录依赖**

| **系统边界** 项目没有重写完整 MineSim。MCTS/Fleet-MCTS 主要替换/扩展 Planner 决策层；未来轨迹仍由 TwoStageController 与 Kinematic Bicycle Model 执行。Scenario、Map、Observation、Controller、Vehicle、History/Metrics 都属于科学链，不能绕过。 |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>run_simulation.py<br />
→ SimulationsRunner._initialize()<br />
→ EnvironmentSimulation.initialize()<br />
→ Scenario / Map loader<br />
→ Planner.initialize()<br />
→ 每帧 Planner.compute_planner_trajectory()<br />
→ TwoStageController.update_state()<br />
→ LQR / iLQR trajectory tracking<br />
→ KinematicBicycleModel.propagate_state()<br />
→ Agent Update Policy / Observation<br />
→ SimulationHistory / metrics / log<br />
→ 下一帧</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

| **层**                   | **当前真实职责 / 关键目录**                                                                      | **接手风险**                                                                     |
|--------------------------|--------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------|
| **Scenario/Environment** | devkit/sim_engine/environment_manager/；scenario_manager/；EnvironmentSimulation                 | Scenario schema、location 映射、绝对路径不能猜。                                 |
| **Map**                  | devkit/sim_engine/map_manager/；semantic/bitmap loader                                           | semantic identity、bitmap symlink、scale/flip、SHA 不可随意改。                  |
| **Planning**             | devkit/sim_engine/planning/planner/；local_planner/                                              | 必须遵守 AbstractPlanner；Planner 输出 future trajectory，不是下一帧状态。       |
| **Pure MCTS**            | local_planner/mcts_planner.py + planner/mcts/\*.py                                               | rear axle / center / footprint / reward producer 语义必须一致。                  |
| **Multi/Fleet**          | mcts/multi_ego_runtime.py、fleet_state.py、fleet_transition.py、fleet_reward.py、fleet_search.py | A/B 同 iteration；受控车必须从 external observation 剔除。                       |
| **Control**              | ego_simulation/two_stage_controller.py；ego_motion_controller/                                   | 合法 trajectory 不等于 controller 可实现；A2 是典型。                            |
| **Vehicle**              | ego_simulation/ego_update_model/kinematic_bicycle_model.py                                       | rear axle、geometric center、footprint 不得混用。                                |
| **Safety**               | collision_lookup.py + exact footprint/swept geometry + Paper1 sidecars                           | 离散 lookup 可 false positive；sidecar 只能按冻结语义使用。                      |
| **Visualization**        | PlanVisualizer2D + SimulationHistory/PlotData + MultiEgoRuntime live B                           | dual history 主要是 A；B truth 在 runtime。                                      |
| **Neural sidecars**      | /root/autodl-tmp/.../src/paper1\_\*；未写入正式 repo                                             | 当前网络、collector、probe 均为 evidence workspace；不得假称已集成生产 planner。 |

**2.1 Pure MCTS / Fleet / Paper1 sidecar 模块索引**

| **模块**                                                                          | **作用**                                                                 |
|-----------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| **mcts/state.py**                                                                 | MCTSState                                                                |
| **mcts/action_space.py**                                                          | BRAKE / DECEL / KEEP / ACCEL 离散动作                                    |
| **mcts/state_builder.py**                                                         | MineSim state → MCTSState                                                |
| **mcts/transition_model.py**                                                      | 树内轻量近似动力学                                                       |
| **mcts/geometry_transition_model.py**                                             | 几何/footprint/外部预测；历史与当前语义差异是 dataset compatibility 关键 |
| **mcts/search.py**                                                                | Pure MCTS selection/expand/rollout/backprop                              |
| **mcts/reward_model.py**                                                          | 目标/安全/进度奖励                                                       |
| **mcts/trajectory_adapter.py**                                                    | root action → MineSim 可执行轨迹                                         |
| **mcts/diagnostics.py + expert_data.py**                                          | root visits/Q/immediate reward/clearance 与 strict expert record         |
| **mcts/multi_ego_runtime.py**                                                     | A/B live controlled state                                                |
| **mcts/fleet_state.py / fleet_transition.py / fleet_reward.py / fleet_search.py** | 双车联合状态、16 joint actions、联合搜索与奖励                           |
| **paper1_v2r_distance_field_v1.py**                                               | 连续 V2R 距离旁路                                                        |
| **paper1_dynamic_v2v_dsafe_v1.py**                                                | dynamic V2V d_safe 诊断                                                  |
| **paper1_shadow_safe_node_v1.py**                                                 | child expansion shadow risk；不删节点                                    |
| **paper1_root_diagnostic_collector_v1.py**                                        | root search + 16 action Q/visits/risk/provenance 数据采集                |
| **paper1_value_network_v1.py**                                                    | 24→64→64→1 Value Network V1；当前只作开发证据                            |

**3. 阶段一：MineSim 原项目复现与 IDM Baseline**

**目标：**先把原项目在 AutoDL 稳定复现，建立后续 MCTS、地图和 multi-ego 改动的回归锚点。Dapai/Jiangtong 原地图、IDM/replay 与 controller/KBM closed-loop 不能因后续算法推进而删除。

| **项目**            | **当前规则 / 真实观测**                                        |
|---------------------|----------------------------------------------------------------|
| **正式 repo**       | /root/MineSim-Dynamic                                          |
| **Baseline commit** | 2521aa41a69a6e734c04c15a715e9530c8095ac3                       |
| **Baseline tag**    | idm-replay-autodl-baseline                                     |
| **原地图/数据**     | Dapai / Jiangtong；保留为 regression anchor。                  |
| **执行原则**        | 先证明原 MineSim 闭环，再替换 Planner；不绕过 Controller/KBM。 |

**3.1 实际工作与 PASS 标准**

> • 核真实配置/YAML/API 签名并完成 AutoDL 环境启动；不按模型记忆猜 Hydra 或 Scenario 字段。
>
> • 确认 Planner 返回 future trajectory，Controller 计算控制，KBM 传播下一帧；不能把 Planner 结果误当直接位置。
>
> • 建立 baseline commit/tag 与 IDM/replay 结果，为后续 MCTS、地图、multi-ego 形成字节/行为回归锚点。
>
> • PASS：仿真可初始化、每帧闭环执行、无异常、结果/日志可追溯、Git 状态与基线一致。

| **永久规则** 终端出现错误时先保留 traceback、log、rc 和当前 Git/SHA；只定位当前故障域，不同时修改多个模块。 |
|-------------------------------------------------------------------------------------------------------------|

**4. 阶段二：蒙特卡洛 / Pure MCTS 接入与单车跑通**

**目标：**在不重写 MineSim 仿真执行层的前提下，将 Pure MCTS 作为 online local planner 接入真实 closed-loop，并建立可追溯的专家搜索记录。

| **项目**               | **当前规则 / 真实观测**                                |
|------------------------|--------------------------------------------------------|
| **正式 MCTS commit**   | 94693dc799fe5f325a75e8fc6d7d5e88764b4799               |
| **Tag**                | mcts-expert-dataset-v1-20260802                        |
| **Strict expert**      | Dapai 199 + Jiangtong 249 = 448 historical records     |
| **历史 search config** | iterations=300；seed=42；target_speed=10.5 m/s         |
| **动作编码**           | BRAKE=0(-3.0), DECEL=1(-1.5), KEEP=2(0), ACCEL=3(+1.0) |

| **实验设计**               | **输入**                                       | **输出 / PASS 标准**                                                                                                    |
|----------------------------|------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------|
| **Single-ego online MCTS** | Scenario + current ego/obstacles + map/refline | 每帧 root search → action → trajectory adapter → Controller/KBM；无 exception，按 goal/safety/timeline evaluator 验收。 |
| **Expert logging**         | root state + obstacles + action domain         | visits/Q/immediate reward/predicted clearance；strict schema；每个 record 可追溯到 scenario/source/result。             |
| **五 Planner 对照**        | MCTS/IDM/Frenet/Adapted Maneuver/Simple        | 用于能力与接口边界，不把少量场景结果外推为全局优越性。                                                                  |

| **关键接口失败** Frenet Dapai step150 的真实根因不是搜索失败，而是 Planner→MineSim trajectory 重采样越界：追加索引79时 best_traj 长度恰为79、最大合法索引78。外部安全重采样后 Dapai199/Jiangtong249 完整跑通。以后 Planner FAIL 必须先区分 search、adapter、controller 三个故障域。 |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

**5. 阶段三：双车冲突场景、MultiEgoRuntime 与 J117**

**目标：**第二辆车不再只是 replay obstacle，而是让 A/B 都成为受控对象，在同一 simulation iteration 内联合传播、联合决策，并建立“无联合规划会发生真实物理冲突”的 causal benchmark。

| **组件**                                       | **已实现语义**                                                                                |
|------------------------------------------------|-----------------------------------------------------------------------------------------------|
| **ControlledVehicleRuntime / MultiEgoRuntime** | 按 token A/B 管理 current/next iteration，接收两条 trajectory；B 权威 live state 在 runtime。 |
| **SimulationSetup.set_multi_ego_runtime()**    | 把 multi-ego runtime 挂到 production simulation setup。                                       |
| **EnvironmentSimulation.propagate()**          | dual trajectories 必须恰好含 A/B，再同步更新 MultiEgoRuntime。                                |
| **Observation filter/partition**               | 从 tracked observation 剔除受控 A/B，防止 controlled+external duplicate actor / 假碰撞。      |
| **FleetState / FleetTransitionModel**          | A/B 联合状态；4×4=16 joint longitudinal actions；几何联合传播。                               |
| **FleetRewardModel**                           | per-vehicle reward + continuous clearance soft penalty + hard collision/safety。              |
| **RouteGeometryCache**                         | rear-axle route_s → geometric-center footprint，避免参考点混用。                              |

| **场景筛选教训** 空间路线相交不等于有联合决策价值。Jiangtong Traj26 虽空间相交，但自然 ETA 差约9.496s；commit 94794c963f9c3eaf1873b275df6d319ca2636817 / tag jiangtong-v22-benchmark-screening-20260809 作为负筛选冻结。禁止为了“凑场景”包装成天然冲突。 |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

**5.1 J117 real-GeoJSON pilot**

| **实验**           | **结果 / 冻结**                                                                                                                                                                              |
|--------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Phase4C 单车**   | commit ec1c958735b0ee76201284faacb46fccc75c7f6c；tag j117-phase4c-single-ego-closed-loop-20260810；423 steps / 42.3s；route≈398.998m；min clearance≈1.599m；goal reached；drivable；无异常。 |
| **Phase5 dual**    | commit da4105b836dbbd3e702ee25fbb364109bc4e2596；tag j117-phase5-dual-ego-pure-mcts-20260810；NO-MCTS 真实重叠 + Pure MCTS 5-seed 验证。                                                     |
| **Dapai A-B-only** | 证明 multi-ego runtime / joint search 机制可运行；full scenario 存 external object-1 confound，不作为唯一 benchmark。                                                                        |

**6. 阶段四：FullMine 新地图接入、Vector V2 → V4 冻结**

**目标：**从真实 FullMine semantic/bitmap 资产建立可由 MineSim Map API、Planner、Controller 与 multi-ego runtime 使用的 Research/DEV 地图；严格区分科研可复现 baseline 与官方 production-authoritative drivability。

| **里程碑**                   | **Commit / SHA / 结论**                                                                    |
|------------------------------|--------------------------------------------------------------------------------------------|
| **Semantic lookup O(1)**     | 32fb42920d8cc404b37cd25dc47cbc6fbde4d9f4；用 token2ind 替代约400k node上的重复线性扫描。   |
| **FullMine V1 registration** | d81c57154e4e5d0b4df1251cf565d9aacffaa026；tag fullmine-dev-runtime-pass-20260811。         |
| **Current V4 freeze**        | 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e；tag fullmine-vector-v4-runtime-freeze-20260814。 |
| **Semantic runtime**         | b85a3d8b28f2252ecb5bda179d514573f6333079def838cd048566f556d95cd0。                         |
| **Bitmap runtime**           | 51abcd5a86e5c510204a5dacc873691506d721f98982ab7f98585d4e0f7efdd0。                         |
| **CollisionLookup**          | 10c1d1339e742ca893fedb4aa51402addfba82e16e08f68339ea35d35ba3043b。                         |
| **IDM planner final**        | 541ec74985d06322656e66c48abb382030d679171341408575d936e0a069e75e。                         |

**6.1 当前 semantic 事实与边界**

> • “V4”主要是 bitmap/runtime/planner 冻结版本；semantic 主体仍是 Vector V2。当前语义审计：403,759 nodes、100 roads、35 intersections、184 polygons、553 reference paths、402 borderlines、565 dubins poses、36 loading、7 unloading、6 auxiliary。
>
> • semantic 保留 raw lane Z 与 8 repair provenance，但 source_z_datum_verified=false；slope waypoint\[4\]=0 的语义未验证，terrain/Z/slope risk 继续 HOLD。
>
> • FullMine V4 是 Research/DEV baseline；没有官方 authoritative mask、internal exclusions 与 authoring rule，因此 production-authoritative drivability NOT PROVEN。
>
> • GlobalRoutePathPlanner BFS target_depth=5 的限制通过 depth-safe targeted scenarios 绕开；没有修改全局 BFS 语义。最终 targeted 7/7 + Jiangtong regression PASS 后才冻结。

**6.2 Bitmap/runtime 演进中的关键问题**

| **对象/问题**        | **真实结论**                                                                             | **永久规则**                                 |
|----------------------|------------------------------------------------------------------------------------------|----------------------------------------------|
| **P0 baseline**      | immutable；candidate 必须新目录。                                                        | 禁止原地覆盖。                               |
| **Candidate v1/v2**  | additive patch，v1 +112px，v2 cumulative +118px。                                        | 每版绑定 SHA；不能为了“看起来通”随手补像素。 |
| **A1 endpoint**      | virtual lead geometry 约4.5m；仅 virtual endpoint length_rear=0.0。                      | 不改地图/goal掩盖 planner bug。              |
| **A2 blocker**       | 高曲率段 steering-rate infeasibility；speed cap 0.208rad/s + backward braking envelope。 | 先看 controller truth，不盲补 bitmap。       |
| **Low-memory RC137** | 2GiB cgroup不足；高卡80GiB/15CPU。                                                       | 所有大 bitmap/EDT 先免费 preflight，再开卡。 |

**6.3 FullMine Representative Pure MCTS**

| **项目**                    | **当前规则 / 真实观测**                                          |
|-----------------------------|------------------------------------------------------------------|
| **Representative Coverage** | FROZEN；跨代表区域覆盖门控完成。                                 |
| **Pure MCTS**               | 3/3 PASS / FROZEN。                                              |
| **Summary SHA**             | 742d0716a00364a625e01b27c693134488211c8989e4996b072739c3a500d056 |
| **Freeze SHA**              | 322e90d6995c410597d01925de6d77f1fd91ddb8c4c73a25c3e87446d37ac1fa |

**7. 阶段五：Fleet-MCTS 双车联合规划、多种子与跨场景结论**

**7.1 Polygon21：冻结的干净冲突 benchmark**

| **证据对象**           | **SHA / 结果**                                                   |
|------------------------|------------------------------------------------------------------|
| **Scenario**           | 362eff18c7ccc88ea8dfaf083a517603566516943690d5cbe76bd1a97afc89e1 |
| **Scenario manifest**  | 0bde6bb1e869c3cf583947203dd41a8fc364f0a2a8130617baebd0b1e6cbad2e |
| **NO-MCTS result**     | 060880c8edc851e05606871cb647058d091ce8737f952b9864cc94e9d6fcfd13 |
| **Fleet seed0 result** | 2eeb28e1fcb1c48d826c387853ec4f9a8a1acf07c9d7e7d1c067701bd4a1398f |
| **Fleet freeze v2**    | b89d290c9cb06d1efb99688ee27b23898ab81d11e36023832477dc2fc834364b |

| **指标**     | **NO-MCTS**                                            | **Fleet seed0**                                                                             |
|--------------|--------------------------------------------------------|---------------------------------------------------------------------------------------------|
| **策略**     | 固定4.5m/s；无 acceleration/waiting/artificial delay。 | Fleet-MCTS；budget=64, depth=8。                                                            |
| **碰撞判定** | 0.1s exact footprint/swept physical overlap。          | physical overlap=False；collision avoided。                                                 |
| **多种子**   | 用于 causal baseline。                                 | seeds0–4：5/5 PASS；first-to-cross A:3, B:2；parameter retuning=False。                     |
| **安全指标** | 真实物理重叠。                                         | crossing gap min/mean/max=3.43799/7.47323/14.40284s；min clearance across seeds=1.292505m。 |

| **Freeze v1 的处理** 第一次 freeze v1 的 FAIL=HARNESS_STATIC_SUMMARY_SCHEMA_MISMATCH，是 harness schema 错误；freeze v2 才是正式锚点。v1 必须保留 provenance，不能删掉假装从未失败。 |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

**7.2 Cross-scene C04/C11/C06：动态线已收口**

| **场景** | **Loader / NO-MCTS**                                 | **Fleet-MCTS**                                                                                                                     | **正式结论**                                                                       |
|----------|------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| **C04**  | Loader PASS；NO-MCTS 真实 overlap PASS。             | seed0 result SHA 47e3ff50997d6ea095fce0ea0532ca9c01ace31abdc4646980f3b92b09129ca0；seeds0–4 全 PASS。                              | 成功 transfer；12.6s/126 steps；gap 2.1881s；min clearance 1.9654m。               |
| **C11**  | Loader PASS；NO-MCTS horizon fix 后 21.2s/212 PASS。 | seed0 SHA 47a6d570f65953e7dea35f46eb9f8ac63975c1e9e96402f6753f3f41e839547e；89s/890；no collision；completed_post_conflict=False。 | 科学 FAIL：安全但 deadlock/progress failure；min clearance 2.9415m；禁止调参抹掉。 |
| **C06**  | Loader PASS；NO-MCTS 25.6s/256 真实 overlap PASS。   | seed0 SHA 0cbec940ce6581da1669fb06f49d091267f2365c8909c0cacafe393693d3df22；14.6s/146；gap≈1.7398s；min clearance≈2.023m。         | 成功 transfer。                                                                    |

> • Balanced seed0 full benchmark success=2/3（C04、C06），collision avoidance=3/3。不能把 C04 5 seeds 与 C11/C06 seed0 简单池化。
>
> • C11 反证冻结 Fleet-MCTS 在所有场景 universal success；也是后续 cooperation/deadlock/value guidance 的真实动机。
>
> • NO-MCTS/Fleet 对照必须使用物理 footprint overlap 与 post-conflict gate，不得以文件名、中心点距离或示意图代替。

**8. 阶段六：原生 MineSim 可视化、Native Video 与汇报材料**

| **固定原则** 汇报材料必须来源于 frozen semantic/bitmap、真实 scenario/runtime state 与 MineSim 原生可视化链。禁止生成式道路、截图描线、像素反推、CSV 坐标重建或手工改变科学轨迹。 |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

**8.1 双车状态真值与受控 B 可视化**

EnvironmentSimulation.history 在 dual mode 主要保留 A 的 ego/history trajectory；受控 B 的权威状态由 MultiEgoRuntime 管理。Native V2 在每次 propagate 前读取 runtime.state_for("A") / state_for("B")；A 与原生 history 同帧对齐并验证 pose error≤1e-8，B 使用同 iteration live state overlay。不能把 SimulationHistory 当 A+B 完整真值。

| **版本**            | **真实问题/结果**                                                                                                           | **状态**                              |
|---------------------|-----------------------------------------------------------------------------------------------------------------------------|---------------------------------------|
| **Native Video V1** | NO-MCTS raw dimensions=(1545,3666)，布局异常；科学链可跑但不满足正式汇报。                                                  | SUPERSEDED；保留历史证据。            |
| **Native Video V2** | NO-MCTS/Fleet raw=(1545,1073)；10fps；NO-MCTS145 frames；Fleet151；side-by-side145；collision frames96–118；peak frame107。 | FINAL / PASS；release SHA f695ba22…。 |
| **关于“打包错误”**  | 当前直接证据支持 V1 尺寸/layout 失败与 V2 重新形成绑定SHA的正式 release；更具体的 ZIP exception 未保存直接证据。            | 未验证/HOLD；不得凭记忆补写。         |

**8.2 FullMine Map Showcase / middleware**

| **对象**                                       | **问题/结果**                                                                                             | **状态**                                     |
|------------------------------------------------|-----------------------------------------------------------------------------------------------------------|----------------------------------------------|
| **Map Showcase V1**                            | 错误假设 semantic 顶层是 GeoJSON FeatureCollection；真实是 custom dict；脚本在 SHA/schema gate 主动停止。 | FAILED DESIGN；正确失败。                    |
| **Map Showcase V2**                            | 读取真实 custom semantic；553 reference_path、402 borderline；Polygon21 真几何；1080p/15fps/120 frames。  | PASS；stable baseline；SHA 9f78f357…。       |
| **Map Showcase V3**                            | ffmpeg SIGKILL:9；只证实进程被杀；保留120帧。                                                             | INCOMPLETE；不得写成“确定 OOM”。             |
| **Renderer conflict XY**                       | manifest 给 conflict_route_s，不给直接 XY；用 semantic waypoints + route station 求点。                   | FIXED；禁止 hardcode。                       |
| **Renderer env**                               | Recovery 曾 KeyError: OUT，因为 wrapper 未透传 required env。                                             | 以后 wrapper 先做 env gate。                 |
| **Polygon node 529/530**                       | 529 unique raw nodes；闭合绘图重复首点后530 coordinates。                                                 | 分清数据与绘图闭合。                         |
| **Middleware Snapshot/Offline/Renderer/Video** | offline freeze 已完成。                                                                                   | FROZEN；live adapter 未正式 PASS，禁止混称。 |

**9. 阶段七：云端文件安全整理、目录体系与恢复机制**

| **整理最终结论** Phase2A–2K COMPLETE/PASS。/root/autodl-tmp 顶层约530→121；记录423次 move/isolate；科研文件删除0；HEAD/SHA/symlink/compile/restore final health PASS。整理是可逆移动/隔离，不是 rm 清盘。 |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

| **目录**                                         | **用途 / 规则**                                                                                                       |
|--------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------|
| **/root/autodl-tmp/00_MineSim_ACTIVE**           | current_paths.json/env、快捷软链接、organization_tools。                                                              |
| **/root/autodl-tmp/10_MineSim_REPORTS**          | 汇报/发布备份；不作为科学运行输入。                                                                                   |
| **/root/autodl-tmp/90_MineSim_ARCHIVE**          | 可恢复历史归档：legacy planner、single MCTS、J117、FullMine dev、superseded media、DR/bundles、assistant deliveries。 |
| **/root/autodl-tmp/98_MineSim_QUARANTINE**       | 隔离但未授权删除；8/16 closeout约315.76MB。                                                                           |
| **/root/autodl-tmp/99_MineSim_CLEANUP_MANIFEST** | Phase1–2K audit、move plan、fingerprint、health、restore provenance。                                                 |

**9.1 当前注册路径与两条绝对不能随意搬的 runtime 软链接**

| **逻辑对象**                | **当前登记路径**                                                      |
|-----------------------------|-----------------------------------------------------------------------|
| **formal_repo**             | /root/MineSim-Dynamic                                                 |
| **polygon21_current**       | /root/autodl-tmp/fullmine_v4_dual_candidate_v1                        |
| **cross_scene_current**     | /root/autodl-tmp/fullmine_v4_fleet_cross_scene_v1                     |
| **representative_mcts**     | /root/autodl-tmp/fullmine_v4_mcts_representative_v1                   |
| **representative_coverage** | /root/autodl-tmp/fullmine_v4_representative_coverage_v1               |
| **runtime_current**         | /root/autodl-tmp/fullmine_vector_v2_targeted_runtime                  |
| **semantic_source_current** | /root/autodl-tmp/new_map_fullmine_vector_v2_dev                       |
| **bitmap_source_current**   | /root/autodl-tmp/fullmine_vector_v4_d_current_planner_patch_candidate |
| **formal_mcts_results**     | /root/autodl-tmp/mcts_results                                         |
| **idm_baseline_backup**     | /root/autodl-tmp/minesim_idm_baseline_backup                          |

| **Runtime entry**                                                                                                            | **必须解析到**                                                                                                             |
|------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------|
| **/root/autodl-tmp/fullmine_vector_v2_targeted_runtime/maps/semantic_map/geojson_full_mine_vector_v2_dev_semantic_map.json** | /root/autodl-tmp/new_map_fullmine_vector_v2_dev/maps/semantic_map/geojson_full_mine_vector_v2_dev_semantic_map.json        |
| **/root/autodl-tmp/fullmine_vector_v2_targeted_runtime/maps/bitmap/geojson_full_mine_vector_v2_dev_bitmap_mask.png**         | /root/autodl-tmp/fullmine_vector_v4_d_current_planner_patch_candidate/bitmap/geojson_full_mine_vector_v2_dev_only_mask.png |

> • 冻结 runner 存在绝对路径依赖时，优先恢复历史路径/软链接，不直接改 frozen runner。
>
> • AST 环境变量审计必须区分 os.environ 的 Load 与 Store；内部脚本自己设置的变量不能误报外部依赖。
>
> • /root/autodl-tmp/MineSim-Dynamic 是约203.75MB独立脏历史 workspace，HOLD；不是正式 repo 的简单副本。
>
> • 已知 \`?? ^C\` 是历史未跟踪异常名；不要为目录美观执行 git clean。

**9.2 Restore 入口**

| **阶段** | **恢复脚本**                                                                                      |
|----------|---------------------------------------------------------------------------------------------------|
| **2A**   | /root/autodl-tmp/99_MineSim_CLEANUP_MANIFEST/phase2a_safe_move_20260816_165421/RESTORE_PHASE2A.sh |
| **2B**   | .../phase2b_safe_quarantine_20260816_170221/RESTORE_PHASE2B.sh                                    |
| **2C**   | .../phase2c_safe_map_archive_20260816_170828/RESTORE_PHASE2C.sh                                   |
| **2F**   | .../phase2f_safe_housekeeping_20260816_172708/RESTORE_PHASE2F.sh                                  |
| **2I**   | .../phase2i_safe_large_archive_20260816_174051/RESTORE_PHASE2I.sh                                 |
| **2J**   | .../phase2j_final_safe_archive_20260816_174626/RESTORE_PHASE2J.sh                                 |

**恢复原则：**恢复前确认原路径没有新同名对象；只用 manifest 对应 RESTORE 脚本逆序恢复；恢复后复核 HEAD/status、关键 SHA、runtime symlink 与 py_compile。

**10. 阶段八：Paper1 safety/data/value 前置与神经网络真实进展**

| **当前准确状态** 神经网络已经完成数据链、PyTorch pipeline 和三场景正式分组训练，但 V1 跨场景 action ranking 失败，明确禁止接入 MCTS。当前不是“神经网络未开始”，也不是“可以上线 Value-guided MCTS”，而是进入 V2 target/interaction 诊断设计阶段。 |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

**10.1 Continuous V2R V3：从旁路污染到正式冻结**

| **门禁/问题**    | **真实结果**                                                                                             | **状态/规则**                                                                     |
|------------------|----------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| **V2R module**   | EDT/scale/numeric/unittest PASS；diagnostic only。                                                       | PASS。                                                                            |
| **V1 sidecar**   | 插入块落在未闭合 v0_records.append 内，SyntaxError。                                                     | 移动到完整 V0 block 外；以后 insertion-only + py_compile。                        |
| **V2 full126**   | V1 字段污染 V0 direct_boundary serialization，只有 v0_jsonl parity FAIL。                                | FAIL-EVIDENCE；V3 使用独立 v1_direct_boundary。                                   |
| **V3 static**    | insertion-only、byte-exact parent restoration、serialization isolation、compile、science boundary PASS。 | PASS。                                                                            |
| **V3 real/full** | authoritative Fleet result/log 与 V0 frozen SHA 保持；V1 126 records。                                   | V2R freeze SHA 0231cda732ac4859985d4be451d01ade6f6e121892721ce9e6317dce430d64a4。 |

**10.2 Runtime heading、approach、Omega_int、pair binding/Omega_app**

| **合同**           | **冻结语义**                                                                                                                        | **SHA / 边界**                                                                                                    |
|--------------------|-------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------|
| **Route heading**  | RouteAdapter.get_state_at_progress(route_s).heading；relative heading=wrapped abs difference。                                      | Approach freeze a27653c237118077a939001ae00aa2014bea3d15ec08f8393ba3e6aca7acb314；manifest angle仅历史screening。 |
| **Raw approach**   | conflict_s-approach_distance \<= route_s \< conflict_s；C04/C11/C06=70/80/100m。                                                    | FROZEN。                                                                                                          |
| **Omega_int**      | semantic intersection.link_polygon_token→polygon.link_node_tokens→node\[x,y\]；route与polygon交段、包含 conflict point 的唯一分量。 | Omega_int freeze a6b1de3c643c331b9a5d27f6544fa1266d4b3ff155f6de754cc94e8716db32c0。                               |
| **Omega_app**      | union(raw frozen approach interval, frozen Omega_int interval)，恢复 Omega_int⊂Omega_app。                                          | Pair/Omega_app freeze 2e516d95200f5297e9e4a3a83445cc29462fc61beefe527c8022e0648fe89905。                          |
| **Pair indicator** | I_Omega=1 iff A in route-specific zone AND B in route-specific zone；OR仅 sensitivity。                                             | AND_BOTH_VEHICLES_IN_ZONE；alpha3=1+I_app+I_int，overlap cumulative。                                             |

**10.3 Dynamic V2V d_safe：冻结的是旁路，不是 hard rule**

| **项目**             | **当前规则 / 真实观测**                                                                                          |
|----------------------|------------------------------------------------------------------------------------------------------------------|
| **Freeze ZIP**       | PAPER1_DYNAMIC_V2V_SIDECAR_V1_FREEZE.zip；SHA 3bcbbcb3623b07c3e8a162e24c5b63303b866cf9d149a68d083c30b5f7856193。 |
| **Record count**     | 126；Fleet/V0/V2R byte-exact parity。                                                                            |
| **Heading / pair**   | RouteAdapter heading；AND pair binding；alpha3 cumulative。                                                      |
| **MS_LOW**           | d_base=2.0, kappa_v=0.5, v_ref=10.5, beta1=0.2, beta2=0.1；19/126 violations，window 82–100。                    |
| **MS_MID**           | 2.5 / 1.0 / 10.5 / 0.5 / 0.25；34/126，window 74–107。                                                           |
| **MS_HIGH**          | 3.0 / 1.5 / 10.5 / 0.5 / 0.25；45/126，window 68–112。                                                           |
| **Science boundary** | behavior/reward/search/tree pruning unchanged；final parameters not selected；V2H NOT_IMPLEMENTED。              |

**Parameter shortlist decision：**MS_LOW 只被选为 primary experimental/shadow candidate，MS_MID 为 sensitivity；HARD_PRUNING_APPROVED=False。Decision JSON SHA 4ac609753d314ba60f79553bd95a23e5713cdff72401a790f842939bbb79a13d。

**10.4 Shadow safe-node：为什么 MS_LOW 不能直接 hard prune**

| **指标**                           | **C04 full126 真实值**                                                                                               |
|------------------------------------|----------------------------------------------------------------------------------------------------------------------|
| **MCTS search / expansion**        | 126 searches × budget64 = 8064 child observations。                                                                  |
| **All child shadow reject**        | 1422 / 8064 = 17.63%；均为 dynamic_only。                                                                            |
| **Depth1 root actions**            | 359 / 2016 被 reject。                                                                                               |
| **有任何 root reject 的 search**   | 27 / 126；首次 search 76。                                                                                           |
| **16/16 root actions 全被 reject** | 连续20次，search 80–99。                                                                                             |
| **实际 selected action 被 reject** | 22 / 126 = 17.46%。                                                                                                  |
| **结论**                           | dataset 可使用 shadow label；hard pruning 不批准；full Paper1 safe-node 仍缺 V2R_TREE_NODE_GATE 和 V2H_PROBABILITY。 |

| **科学含义** 成功通行轨迹在核心冲突区仍会被 MS_LOW 把全部16个动作标成 unsafe；因此 shadow_v2v_safe_node_reject 只能作辅助风险特征，不是 unsafe ground truth，更不能训练成简单 stop/go 网络。 |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

**10.5 Dataset Contract 与 Root Diagnostic Collector**

| **对象**              | **冻结/实现内容**                                                                                                 |
|-----------------------|-------------------------------------------------------------------------------------------------------------------|
| **Raw record**        | ONE_MCTS_ROOT_SEARCH。                                                                                            |
| **Derived record**    | ONE_ROOT_STATE × ONE_JOINT_ACTION；每 root 16 actions。                                                           |
| **Primary target**    | q_value。                                                                                                         |
| **Auxiliary**         | normalized_root_visits、episode outcome、continuous V2V margin、shadow reject；shadow binary label 不是 primary。 |
| **Input features V1** | 16 root-state scalars + A/B各4维 one-hot = 24维。                                                                 |
| **Split rule**        | 按 whole scenario/episode group；random row split forbidden。                                                     |
| **Provenance**        | git/map/scenario/manifest/seed/budget/depth/dt/source/safety contract SHA。                                       |
| **V2H**               | NOT_IMPLEMENTED；不阻塞第一版 Value pipeline，但阻塞 full safe-node。                                             |

| **项目**                 | **当前规则 / 真实观测**                                                                                                                               |
|--------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Dataset Contract SHA** | 46f2e099fbe9090a02b1f9fe8a983e4f8322a2ffeba89a4700de8e278991dcda                                                                                      |
| **C04 collector result** | 126 roots / 2016 rows；Q min/max/mean/std=-93.9544/6.8994/-0.9325/15.1987；ZIP SHA daa9bc9e278aabf54b26e9858a08b0d58fb8192a2511f57f7d15bd4098a20422。 |
| **Timeline contract**    | root_state.time_s=absolute runtime；V0 time_s=relative simulation；V0 next_time_s=absolute transition-end；0.1s cadence。                             |
| **Behavior boundary**    | Collector 只读 super().search diagnostics；不额外 transition/reward/RNG，不改 search/pruning。                                                        |

**10.6 Value Network V1：单 episode pipeline 跑通**

| **项目**       | **结果**                                                                                               |
|----------------|--------------------------------------------------------------------------------------------------------|
| **数据**       | C04 seed0；126 roots / 2016 samples；24-D；无 train/val split，仅 pipeline smoke。                     |
| **网络**       | MLP 24→64→64→1，ReLU；raw MCTS Q regression；Adam，800 epochs。                                        |
| **训练结果**   | baseline RMSE 15.1987；train RMSE 7.2570；ratio 0.4775；MAE 2.4042；Pearson 0.8800；root Top1 19.84%。 |
| **Checkpoint** | 6c223729cbbba3044b972fd7a90f4121e883fd34c9a6093f2b8e18597cf11413。                                     |
| **边界**       | formal_training=False；formal_validation=False；generalization claim=False；MCTS integration=False。   |

**10.7 C11/C06 current-semantic collector：正负 episode 都已采集**

| **场景**        | **Roots / rows / Q std** | **Outcome / 行为保护**                                                                                                               |
|-----------------|--------------------------|--------------------------------------------------------------------------------------------------------------------------------------|
| **C11**         | 890 / 14240 / 27.5648    | SAFE_INCOMPLETE_OR_DEADLOCK；新 result SHA 与权威 47a6d570… byte-exact。                                                             |
| **C06**         | 146 / 2336 / 17.7777     | SUCCESSFUL_PASS；新 result SHA 与权威 0cbec940… byte-exact。                                                                         |
| **与 C04 合并** | 1162 roots / 18592 rows  | 3 episode groups：C04 success、C11 deadlock、C06 success；ZIP SHA 94ec9778a2899825125eaaed5c2ece50b8d0cd29390481c1e6f2ac568f052300。 |

为避免把 C04 zone 错套到新场景，Shadow V1 从硬编码 C04_ZONE_INTERVALS 改为注入 scene-specific frozen intervals；Root Collector 将同一 zone object 传给 Shadow。改动只影响观察字段，不改变 MCTS 行为。

**10.8 Three-scene LOSO formal Value V1：流程 PASS、科学 FAIL**

| **Held-out** | **RMSE** | **Global Spearman** | **Mean root Spearman** | **Top1** | **Normalized regret** | **Immediate baseline regret** |
|--------------|----------|---------------------|------------------------|----------|-----------------------|-------------------------------|
| **C04**      | 80.6713  | 0.1472              | -0.04346               | 2.38%    | 0.35835               | 0.23471                       |
| **C11**      | 32.5175  | 0.1866              | 0.02473                | 0.79%    | 0.24435               | 0.15674                       |
| **C06**      | 40.3005  | -0.6862             | -0.43153               | 0%       | 0.57098               | 0.24193                       |

> • Split=leave-one-scene-episode-out；3 folds；normalization只用训练 fold；scene-balanced SmoothL1；600 epochs/fold。
>
> • 三个 held-out Top1 均低于随机 1/16=6.25%；三个 fold 的 normalized regret 均差于 immediate_reward。
>
> • PROVISIONAL_VALUE_GUIDANCE_READY=False；formal result ZIP SHA 7c296200504ed75ca216a46bc74427703f99a9d5c75f35b0b1bd7e20fd10cdf1；summary SHA ac1d46ca91d6813e868121ced41e8751479ed2f4d4d6afd437921313e42b6e5a。
>
> • 结论：当前 24-D raw-Q V1 不能接入 MCTS；不是“多训几轮”即可自动解决。

**10.9 V1 failure diagnostic：已确认的 target/feature shift 与诊断局限**

| **诊断**                    | **C04**                             | **C11**                                  | **C06**                                 |
|-----------------------------|-------------------------------------|------------------------------------------|-----------------------------------------|
| **Median root Q span**      | 2.5804                              | 94.1761                                  | 2.5034                                  |
| **Median root Q std**       | 0.6943                              | 25.2764                                  | 0.6855                                  |
| **Immediate reward regret** | 0.2347                              | 0.1567                                   | 0.2419                                  |
| **Formal V1 regret**        | 0.3583                              | 0.2443                                   | 0.5710                                  |
| **Feature OOD 示例**        | A/B route_s 大量越界；delta_v shift | A/B speed约89–90%越界；A heading100%越界 | A/B route_s 100%越界；A heading100%越界 |

| **重要修正** 上一轮 additive ridge 的四套 state feature 结果完全相同，并不能证明 relative feature 无用。原因是同一 root 的16个动作共享相同 state，线性 state-only 部分只给所有动作加公共常数；排序只由 action bias 决定。诊断真实证明的是“全局 action bias 不够”，而不是“状态表示无关”。 |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

| **项目**                   | **当前规则 / 真实观测**                                                                        |
|----------------------------|------------------------------------------------------------------------------------------------|
| **Failure diagnostic ZIP** | d16b2f0805235a5aedc07909e763329984588b3bed145fb46557a97388a1b6fa                               |
| **Decision**               | DO_NOT_INTEGRATE_VALUE_NETWORK_INTO_MCTS                                                       |
| **Formal evidence status** | C04/C11/C06 已全部参与 V2 设计诊断；从此属于 DEVELOPMENT EVIDENCE。                            |
| **Final claim boundary**   | 后续 V2 若在同三场景上变好，也不能作为最终独立泛化证明；必须增加未参与设计的新 scene/episode。 |

**10.10 当前真正下一步：Value Network V2 interaction/target probe**

| **对象**            | **当前状态 / 语义**                                                                                                                                       |
|---------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Delivery**        | /root/autodl-tmp/PAPER1_VALUE_NETWORK_V2_INTERACTION_TARGET_PROBE_V1_DELIVERY.zip；SHA e14aafd8c1b859a7f967b1f5eb4e33d0a7cb900dcb29b23ec1d316d52268c356。 |
| **Source / runner** | source acd7fd3b1bdc804251248afaf4b67178f5d75c86934d66850f624c0334b443e5；runner 4c1e6e046e637a42563dcbc7cb8c92da361c6f52474dc268111c5e18ee7ddf6d。        |
| **Probe model**     | scene+root balanced ridge，显式 joint-action × relative-state interactions；去除 absolute route_s/heading。                                               |
| **Targets**         | root-centered Q；root-zscore Q；residual-to-immediate（score=immediate+learned residual）。                                                               |
| **资源**            | 低资源 2GiB/0.5CPU；GPU禁用；不跑仿真、不重训MLP、不接MCTS。                                                                                              |
| **完成标准**        | PASS ...V2_INTERACTION_TARGET_PROBE_V1；输出 BEST_CANDIDATE、win_count、DECISION。                                                                        |
| **分支**            | 若某候选≥2/3 held-out场景的 regret 优于 immediate baseline，进入真正 V2 neural design；否则先扩充 current-semantic episodes。                             |

**11. 重要问题、失败、原因、修复与永久禁忌**

| **故障/现象**                        | **原因**                                         | **解决/证据**                                                   | **以后不能再做**                                                                |
|--------------------------------------|--------------------------------------------------|-----------------------------------------------------------------|---------------------------------------------------------------------------------|
| **Planner/Frenet step150**           | IndexError；best_traj 长79却访问79。             | trajectory resample/adapter 越界，不是搜索失败。                | 安全重采样后199/249跑通；先分 search/adapter/controller。                       |
| **Multi-ego duplicate actor**        | A/B 同时 controlled+external，产生假碰撞。       | 受控 token 未从 tracked observation 过滤。                      | controlled filter/partition；受控车不得重复为 external。                        |
| **Environment history 缺 B**         | dual history 看不到完整 B。                      | SimulationHistory 主要记录 A；B truth 在 MultiEgoRuntime。      | 同 iteration runtime.state_for(B)；禁止用 A history 假装 A+B。                  |
| **Native B visualization**           | B 无法直接用原生 history 回放。                  | 同上。                                                          | A用history，B live overlay；pose parity≤1e-8；禁止route_s/CSV/pixel猜姿态。     |
| **Jiangtong conflict screening**     | 路线空间相交但交互弱。                           | 自然 ETA 差约9.496s。                                           | 负筛选 freeze；空间交叉≠temporal conflict。                                     |
| **CollisionLookup false positive**   | 离散 lookup 可能报碰撞而 footprint 不重叠。      | 栅格/查表定义与 exact geometry 不同。                           | NO-MCTS causal gate 必须 exact footprint/swept physical overlap。               |
| **NO-MCTS benchmark**                | 仅靠示意图/中心距无法证明。                      | 缺少物理真值与 post-conflict gate。                             | 固定4.5m/s、无人工delay、0.1s footprint/swept、完成冲突后进度。                 |
| **FullMine init slow**               | 大 semantic initialize 卡住。                    | 约400k node重复线性 scan。                                      | token2ind O(1)；先profile复杂度，不归咎GPU。                                    |
| **A1 endpoint**                      | 末端约4.5m virtual lead。                        | virtual endpoint geometry。                                     | 仅 virtual endpoint length_rear=0；不改地图/goal。                              |
| **A2 mid-stop**                      | 高曲率段停车。                                   | steering-rate infeasibility，不是最终 leading/occupancy。       | steering-aware speed cap + backward braking；不要盲补bitmap。                   |
| **Map/runtime path**                 | 整理后找不到 map。                               | absolute path / symlink dependency。                            | current_paths + restore/symlink gate；冻结runner优先恢复路径。                  |
| **Low-memory RC137**                 | 2GiB 下 Killed。                                 | cgroup RAM/CPU 不足。                                           | 先低资源 preflight；确需大图/长仿真才开80GiB/15CPU。                            |
| **Map Showcase V1**                  | schema gate fail。                               | 误把 custom semantic 当 GeoJSON FeatureCollection。             | 读取真实schema；文件名含geojson不等于GeoJSON。                                  |
| **Map Showcase V3**                  | ffmpeg SIGKILL:9。                               | 只知进程被杀。                                                  | 保留120帧标INCOMPLETE；不得无证据说OOM。                                        |
| **Native Video V1**                  | raw=(1545,3666)布局异常。                        | 尺寸/layout不适合正式汇报。                                     | V2=(1545,1073)+ffprobe/human gate；科学链能跑≠汇报PASS。                        |
| **Native ZIP packaging**             | 用户历史提到打包问题。                           | 现存直接证据不足以定位具体ZIP exception。                       | 仅记录为未验证/HOLD，不凭记忆补写。                                             |
| **Renderer conflict XY**             | Key不存在。                                      | manifest提供route_s而非XY。                                     | semantic waypoints+route station求点；禁止hardcode。                            |
| **Renderer OUT KeyError**            | 恢复脚本缺OUT。                                  | wrapper未透传required env。                                     | wrapper先做全部外部依赖gate。                                                   |
| **Polygon 529/530**                  | 节点数量看似不一致。                             | 529 unique + closure duplicate=530 plot coords。                | 分清原始数据与绘图闭合。                                                        |
| **Video mid-pan 空画面**             | 自动编码可过但画面阶段性空。                     | camera logic。                                                  | V0.2 target-anchored camera；最终必须human visual gate。                        |
| **Long heredoc / 粘贴污染**          | 命令与输出混粘、乱码/空文件。                    | 聊天UI与终端内容混合。                                          | 文件优先、短块；先ls/file/sed；禁止清整个目录。                                 |
| **C04 loader float(list)**           | 旧runner TypeError。                             | 一元素list/\[N\]\[1\]未规范；exact failing line未完整保留。     | 后续shape normalization通过；不从旧doc重跑，不猜exact line。                    |
| **C04 NO-MCTS MAX_STEPS**            | NameError。                                      | harness常量遗漏。                                               | 最小runner fix；harness FAIL≠science FAIL。                                     |
| **C11 NO-MCTS 200-step**             | completed_post_conflict=false。                  | horizon不足。                                                   | 延长到21.2s/212；只改时间窗，不改物理/算法。                                    |
| **C11 Fleet deadlock**               | 89s无碰撞但不完成。                              | 安全规避后合作/进度失败。                                       | 保留负结果；禁止为“全PASS”调参抹掉。                                            |
| **Historical 448 vs current labels** | schema看似相同。                                 | rear-axle/center producer wiring已变。                          | legacy隔离；current-code recollection；schema相同≠label语义同质。               |
| **V2R missing source/runner**        | 脚本继续执行并出现空SHA/RC127。                  | 文件未上传到预期路径，gate wrapper没有及时停。                  | 先file gate并在子shell失败；缺文件是操作/path问题，不是science fail。           |
| **V3 static forbidden term**         | 误报 FORBIDDEN...tree_pruning。                  | 字符串出现在science-boundary/manifest，不代表真实rewire。       | 静态审计需区分代码调用与元数据文本。                                            |
| **V3 real import**                   | ModuleNotFound paper1_safety_risk_evaluator_v0。 | runtime PYTHONPATH未包含解压src。                               | ADD_SRC_DIR_TO_RUNTIME_PYTHONPATH；先import contract preflight。                |
| **Omega_int decode**                 | 35 intersections decode count=0。                | intersection存link_polygon_token，不是直接几何。                | 按intersection→polygon→nodes链解析。                                            |
| **Dynamic next_time cadence**        | 0.1比较FAIL。                                    | absolute timestamp浮点差0.0999999/0.10000014。                  | 使用冻结时间序列与容差；不要精确等号。                                          |
| **Shadow hard prune**                | 20 roots 16/16 reject，22 selected reject。      | MS_LOW只是风险margin，不是可行性ground truth。                  | 只作auxiliary feature；hard pruning=False。                                     |
| **Collector JSON +inf**              | Out of range float values。                      | root minimum_clearance_m 尚为+inf且allow_nan=False。            | 删除未合同化字段；先serialize成功再append。                                     |
| **Collector false PASS summary**     | JSONL空但内存summary PASS。                      | 先append内存、后序列化失败。                                    | append only after strict serialization。                                        |
| **Full collector timeline**          | ROOT_V0_TIME:0。                                 | root absolute time与V0 relative time直接比较。                  | 对齐origin与next_time cadence；离线salvage，无需重跑。                          |
| **PyTorch missing**                  | ModuleNotFound torch。                           | minesim env虽在PyTorch镜像上但未装torch。                       | 安装CPU torch；正式记录2.8.0+cpu；不要假设镜像包等于env包。                     |
| **旧C11/C06包“丢失”**                | 顶层路径不存在。                                 | 已归档到90_MineSim_ARCHIVE/.../30_review_hold。                 | 先全盘/Archive locator；path missing≠deleted。                                  |
| **Approach freeze SHA**              | 预期2e516…但实际a276…                            | 把不同冻结对象SHA混为一谈。                                     | a276=heading/approach文件对象；2e516=pair/Omega_app对象；先内容reconciliation。 |
| **Shadow C04 zone hardcode**         | 直接跑C11/C06会污染alpha3/risk。                 | module固定C04_ZONE_INTERVALS。                                  | 改为注入scene-specific frozen intervals；behavior byte-exact gate。             |
| **Single-episode NN**                | C04训练指标好但无法说明泛化。                    | 一个episode、无独立验证。                                       | 只作pipeline smoke；禁止random row split/泛化claim。                            |
| **LOSO Value V1**                    | 三fold Top1均低于随机且regret差于immediate。     | raw-Q/feature OOD/目标结构不足。                                | DO_NOT_INTEGRATE；先V2诊断。                                                    |
| **Additive ridge diagnostic**        | 删不同state特征结果完全相同。                    | 同root state常数且无state-action interaction，只剩action bias。 | V2 probe必须显式joint-action×state interaction。                                |
| **Result file exists**               | 文件名看似成功但内容可FAIL。                     | immutable baseline/result可含真实失败。                         | 永远解析JSON、RC、manifest gate；存在≠通过。                                    |
| **codex-env.sh missing**             | 登录提示No such file。                           | 现有证据不能区分删除/移动/路径变化。                            | 标“路径缺失、处置未验证”；不要据此推断Codex工作丢失。                           |

**12. 当前有效版本、SUPERSEDED/HOLD/未验证对象**

| **对象**                                      | **状态**                            | **处理规则**                                                   |
|-----------------------------------------------|-------------------------------------|----------------------------------------------------------------|
| **MineSim baseline 2521aa4**                  | HISTORICAL / FROZEN                 | 保留回归；不是 current HEAD。                                  |
| **Pure MCTS 94693dc + 448**                   | HISTORICAL / FROZEN                 | 专家历史证据；训练label语义需隔离。                            |
| **J117 Phase4C/5**                            | FROZEN                              | 不重跑；multi-ego regression anchor。                          |
| **FullMine Vector V4 112d2bd**                | CURRENT FROZEN                      | 不得修改 frozen tag；新研究使用独立 evidence workspace。       |
| **Representative Pure MCTS 3/3**              | FROZEN                              | 无需重做。                                                     |
| **Polygon21 Fleet freeze v2**                 | FROZEN                              | 正式 benchmark；freeze v1 仅 harness failure provenance。      |
| **Cross-scene C04/C11/C06**                   | CLOSED WITH NEGATIVE                | C11 negative 必须保留。                                        |
| **Native Video V1**                           | SUPERSEDED                          | 保留 provenance，不用于正式汇报。                              |
| **Native Video V2**                           | CURRENT FINAL                       | 正式视频 evidence release。                                    |
| **Map Showcase V2**                           | PASS / HISTORICAL STABLE            | V3未final，不覆盖V2。                                          |
| **Map Showcase V3**                           | INCOMPLETE / HOLD                   | 120 frames；final encode/release未完成。                       |
| **Middleware offline chain**                  | FROZEN                              | live adapter 未正式 PASS。                                     |
| **Paper1 V2R/heading/Omega/pair/dynamic V2V** | FROZEN / DIAGNOSTIC                 | 不改变planner行为；不得外推hard safety。                       |
| **Shadow safe-node**                          | OBSERVATIONAL PASS                  | hard pruning not approved；full safe-node缺V2R tree gate/V2H。 |
| **Dataset Contract / Collector**              | CURRENT FROZEN DATA CHAIN           | 18592 current-semantic rows；按episode分组。                   |
| **Value Network V1 C04 smoke**                | PIPELINE PASS                       | 非正式、无泛化claim。                                          |
| **Three-scene Value V1**                      | FORMAL TRAINING PASS / SCIENCE FAIL | readiness=False；DEVELOPMENT EVIDENCE；不得接MCTS。            |
| **Value V1 failure diagnostic**               | CURRENT DIAGNOSTIC PASS             | Decision=DO_NOT_INTEGRATE。                                    |
| **Value V2 interaction/target probe**         | PREPARED / NOT RUN                  | 当前唯一next。                                                 |
| **FullMine production validity**              | HOLD / NOT PROVEN                   | 缺官方drivability与authoring rule。                            |
| **Terrain/Z/slope risk**                      | HOLD                                | datum/slope语义未权威验证。                                    |
| **V2H probabilistic safety**                  | NOT IMPLEMENTED                     | 阻塞full Paper1 safe-node。                                    |
| **Π_safe hard pruning**                       | NOT APPROVED                        | Shadow证据已反对直接MS_LOW hard prune。                        |
| **Policy Network / PUCT**                     | NOT STARTED                         | 先解决Value V2与新独立验证。                                   |
| **Value-guided MCTS**                         | NOT INTEGRATED                      | 禁止在V2证据前接入。                                           |

**13. 环境、资源、依赖、运行与恢复规范**

| **项目**           | **当前规则 / 真实观测**                                                                     |
|--------------------|---------------------------------------------------------------------------------------------|
| **正式 repo**      | /root/MineSim-Dynamic                                                                       |
| **Conda env**      | minesim；/root/miniconda3/envs/minesim                                                      |
| **Project Python** | 3.9.25（实际激活环境）；不要用镜像宣传的Python3.10替代事实。                                |
| **PyTorch**        | 最初 minesim 环境缺 torch；后安装 CPU torch 2.8.0+cpu；正式 LOSO 使用该版本。               |
| **低资源 cgroup**  | memory.max=2147483648（2GiB）；cpu.max=50000 100000（0.5 CPU）。                            |
| **高资源 cgroup**  | memory.max=85899345920（80GiB）；cpu.max=1500000 100000（15 CPU）。                         |
| **高资源卡**       | RTX 4090D 24GB×1，约1.88–1.98元/小时；当前MCTS/EDT/collector均CUDA禁用，价值主要是RAM/CPU。 |
| **系统/数据盘**    | 系统盘30GB、数据盘50GB；最后可见用量只是历史瞬时值，当前精确容量未live audit。              |
| **Git**            | 预期HEAD=112d2bd…；至少保留已知 \`?? ^C\`；未知tracked/staged变化先停下。                   |
| **大文件**         | /root/autodl-tmp；正式repo只保留必要tracked source。                                        |

**13.1 所有可执行代码的固定前缀**

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

> • 交互顶层禁止裸 exit；需要失败终止时放入子 shell \`( ... )\` 中用 false，或只打印 FAIL。
>
> • 禁止 git reset --hard、git clean -fd、git add .；只 add 精确文件；commit前 diff/check/name-only。
>
> • 长仿真用普通终端/screen，独立 log+rc；screen只是托管，不是证据源。先看rc/log/process，避免重复启动。
>
> • 每个 map candidate/script/result 必须绑定 SHA；临时runtime切图使用symlink + strong SHA gate。
>
> • 大源码/日志/JSON/CSV/图片/视频用文件或ZIP上传，聊天只传任务、短字段、error tail。

**13.2 继续前的统一只读 preflight**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>pwd<br />
git rev-parse HEAD<br />
git status --short<br />
cat /sys/fs/cgroup/memory.max<br />
cat /sys/fs/cgroup/cpu.max<br />
screen -ls<br />
ps -eo pid,etime,%cpu,%mem,cmd | grep -E 'MineSim|paper1|mcts' | grep -v grep || true<br />
sha256sum &lt;current input artifacts&gt;</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

**14. 用户—ChatGPT—Codex 协作规则与成本控制**

| **最新协作定义** ChatGPT 负责分析、决策、关键代码与验收设计；用户复制到 AutoDL 终端执行并返回真实输出/ZIP；只有复杂算法、顽固 Bug、关键结论复核或明显适合云端自主执行的麻烦任务，才在省钱前提下交给 Codex。Codex 不是后台无限运行的第二个 AI。 |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

| **规则**             | **固定执行方式**                                                                       |
|----------------------|----------------------------------------------------------------------------------------|
| **默认 Codex model** | gpt-5.6-luna medium。                                                                  |
| **升级策略**         | 必要时临时 Terra/Sol；任务完成立即降回 Luna。                                          |
| **已知事实**         | 不重复扫描、不重复解释；frozen阶段不重审。                                             |
| **任务粒度**         | 每次只推进一个最小 blocker；Codex只返回PASS/FAIL与必要字段，不写长报告。               |
| **免费优先**         | file/process/hash/git/grep/py_compile/JSON audit等能用Shell/Python确定的事情不用模型。 |
| **资源顺序**         | 先低资源read-only preflight/static/smoke；确需大图/长仿真才开80GiB。                   |
| **实验顺序**         | 只读preflight → 单步smoke → 短闭环 → 完整实验 → freeze。                               |
| **长任务**           | 普通terminal/screen；不让Codex长时间等待。                                             |
| **文件优先**         | 几百行源码、长日志和结果不贴聊天；通常3–6个当前相关文件；大结果包ZIP上传。             |
| **补丁方式**         | 小修改优先unified diff；长脚本/核心文件优先可直接使用的.py/.sh/.patch。                |
| **失败处理**         | 只定位当前故障域；一个FAIL不回滚到全仓扫描。                                           |
| **安全优先**         | 可复现/可恢复/结果质量优先于目录美观、省几分钟或少几个文件。                           |

复杂 Codex prompt 必须包含：已冻结事实、唯一目标、允许修改文件、禁止操作、最小测试、PASS/FAIL、最终输出字段、完成即停止。

**15. 云端文档生成、归档、移动与删除情况**

| **严谨边界** 以下“已生成文档”来自实际上传的 Word/ZIP 与 cleanup 说明。当前没有做 2026-08-21 全云端 Word 数量的 live audit，因此“云端现存精确文档数/是否有人手动删过某个 Word”仍为未验证。能确定的是：8/16 科研文件删除0；8/21 assistant package cleanup也是移动/归档，不是删除。 |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

| **日期**       | **文档/包**                                               | **当前定位**                                          |
|----------------|-----------------------------------------------------------|-------------------------------------------------------|
| **2026-07-26** | MineSim-Dynamic_普通AI与AutoDL云端交互及代码调试手册      | HISTORICAL；安全交互/Git规则。                        |
| **2026-07-26** | MineSim-Dynamic_项目必备配套资料_风险清单与AI长期交接手册 | HISTORICAL。                                          |
| **2026-08-06** | MineSim-Dynamic_项目全景档案与AI长期接管超级手册          | HISTORICAL；Pure MCTS/五Planner。                     |
| **2026-08-09** | MineSim-Dynamic_云端项目完整交接与工作流手册              | HISTORICAL；J117单车。                                |
| **2026-08-11** | MineSim-Dynamic_新地图项目云端交接手册                    | HISTORICAL；FullMine V1。                             |
| **2026-08-12** | MineSim-Dynamic_项目完整进展与云端AI接管超级手册          | HISTORICAL；Vector V2/CollisionLookup。               |
| **2026-08-13** | MineSim项目云端接手与技术总览                             | HISTORICAL。                                          |
| **2026-08-14** | 两份 FullMine Vector V4 / Pure MCTS 冻结长手册            | HISTORICAL/FROZEN SNAPSHOT。                          |
| **2026-08-16** | MineSim-Dynamic_全项目阶段性总交接与AI无缝接管手册        | HISTORICAL；Native Video/cleanup/cross-scene static。 |
| **2026-08-16** | MineSim_云端项目文件整理与维护说明（docx+md）             | CURRENT cleanup provenance。                          |
| **2026-08-17** | MineSim-Dynamic 全项目阶段性总交接与AI无缝接管            | HISTORICAL；C04 float(list)停点已被后续覆盖。         |
| **2026-08-18** | MineSim-Dynamic_全项目阶段性总总结与AI无缝接管手册        | 上一版综合手册；其Neural/V2R next已被8/21覆盖。       |
| **2026-08-21** | 本《全项目阶段性总总结与AI无缝接管手册》                  | 新会话artifact；只有用户上传到云端后才可称云端现存。  |

**15.1 已验证的移动/删除事实**

> • 2026-08-16 Phase2A–2K：约530→121；423 move/isolate；科研文件删除0；Quarantine不是删除授权，Archive不是垃圾。
>
> • 2026-08-21 assistant package cleanup closeout：move manifest=99、keep manifest=3、problem_count=0、restore script存在、SHA验证通过；属于归档移动。随后新Paper1/NN包继续生成，因此该“3个顶层文件”只是当时瞬时状态。
>
> • 旧 C11_FLEET_SEED0_V1_UPLOAD.zip / C06_FLEET_SEED0_V1_UPLOAD.zip 顶层缺失时，最终在 \`/root/autodl-tmp/90_MineSim_ARCHIVE/assistant_deliveries_pre_neural_v1/30_review_hold/\` 找到，证明路径缺失不等于删除。
>
> • 登录反复出现 \`/root/autodl-tmp/codex-env.sh: No such file or directory\`；现有证据不足以判断它被删、被移或本来不在该路径，标为“路径缺失/处置未验证”。
>
> • 因为整理坚持0删除，目录变干净不等于释放磁盘。若要真正清空间，必须单独建立只读inventory、checksum/equivalence和明确授权的deletion phase。

**15.2 8/21 新生成的非Word科学/开发文档**

> • 大量 JSON/JSONL/manifest/SHA256SUMS、Shell/Python sidecar、ZIP freeze/result、NPZ dataset、PT checkpoint 与日志已生成，主要位于 /root/autodl-tmp。
>
> • 关键当前文件：Dynamic V2V freeze、Dataset Contract V1、C04 collector、C11/C06 collector、Three-scene LOSO result、V1 failure diagnostic、V2 interaction probe delivery。
>
> • 这些对象未全部重新纳入8/16目录治理；在当前V2诊断结束前不要为“顶层好看”移动它们。

**16. 关键 Commit / Tag / SHA / 冻结证据速查**

**16.1 Commit / Tag**

| **里程碑**              | **Commit**                               | **Tag / 语义**                               |
|-------------------------|------------------------------------------|----------------------------------------------|
| **IDM baseline**        | 2521aa41a69a6e734c04c15a715e9530c8095ac3 | idm-replay-autodl-baseline                   |
| **Pure MCTS + expert**  | 94693dc799fe5f325a75e8fc6d7d5e88764b4799 | mcts-expert-dataset-v1-20260802              |
| **Jiangtong V22**       | 94794c963f9c3eaf1873b275df6d319ca2636817 | jiangtong-v22-benchmark-screening-20260809   |
| **J117 Phase4C**        | ec1c958735b0ee76201284faacb46fccc75c7f6c | j117-phase4c-single-ego-closed-loop-20260810 |
| **J117 Phase5**         | da4105b836dbbd3e702ee25fbb364109bc4e2596 | j117-phase5-dual-ego-pure-mcts-20260810      |
| **FullMine lookup**     | 32fb42920d8cc404b37cd25dc47cbc6fbde4d9f4 | token2ind O(1)                               |
| **FullMine V1**         | d81c57154e4e5d0b4df1251cf565d9aacffaa026 | fullmine-dev-runtime-pass-20260811           |
| **CURRENT FullMine V4** | 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e | fullmine-vector-v4-runtime-freeze-20260814   |

**16.2 基础与可视化冻结对象**

| **对象**                        | **SHA256**                                                       |
|---------------------------------|------------------------------------------------------------------|
| **FullMine semantic**           | b85a3d8b28f2252ecb5bda179d514573f6333079def838cd048566f556d95cd0 |
| **FullMine V4 bitmap**          | 51abcd5a86e5c510204a5dacc873691506d721f98982ab7f98585d4e0f7efdd0 |
| **CollisionLookup**             | 10c1d1339e742ca893fedb4aa51402addfba82e16e08f68339ea35d35ba3043b |
| **Representative MCTS summary** | 742d0716a00364a625e01b27c693134488211c8989e4996b072739c3a500d056 |
| **Representative MCTS freeze**  | 322e90d6995c410597d01925de6d77f1fd91ddb8c4c73a25c3e87446d37ac1fa |
| **Polygon21 scenario**          | 362eff18c7ccc88ea8dfaf083a517603566516943690d5cbe76bd1a97afc89e1 |
| **Polygon21 NO-MCTS**           | 060880c8edc851e05606871cb647058d091ce8737f952b9864cc94e9d6fcfd13 |
| **Polygon21 Fleet seed0**       | 2eeb28e1fcb1c48d826c387853ec4f9a8a1acf07c9d7e7d1c067701bd4a1398f |
| **Polygon21 Fleet freeze v2**   | b89d290c9cb06d1efb99688ee27b23898ab81d11e36023832477dc2fc834364b |
| **Native Video V2**             | f695ba22ecd61c4a643e8ffecac483bc218de9153f95f88b4e0e3006bca03d58 |
| **Map Showcase V2**             | 9f78f357eecfc25ea543d163e8d472dc06abeb1fff3215ed30577267750d1e14 |
| **Cleanup Phase2K closeout**    | e3d4ba27bd06c74c7ca23ed55de65208022f07d4e0cb600eb58bcbbcaaf33a4b |

**16.3 8/21 Paper1 / Neural 关键对象**

| **对象**                            | **SHA256**                                                       |
|-------------------------------------|------------------------------------------------------------------|
| **C04 authoritative Fleet result**  | 47e3ff50997d6ea095fce0ea0532ca9c01ace31abdc4646980f3b92b09129ca0 |
| **C11 authoritative Fleet result**  | 47a6d570f65953e7dea35f46eb9f8ac63975c1e9e96402f6753f3f41e839547e |
| **C06 authoritative Fleet result**  | 0cbec940ce6581da1669fb06f49d091267f2365c8909c0cacafe393693d3df22 |
| **V2R freeze**                      | 0231cda732ac4859985d4be451d01ade6f6e121892721ce9e6317dce430d64a4 |
| **Heading/approach freeze**         | a27653c237118077a939001ae00aa2014bea3d15ec08f8393ba3e6aca7acb314 |
| **Omega_int freeze**                | a6b1de3c643c331b9a5d27f6544fa1266d4b3ff155f6de754cc94e8716db32c0 |
| **Pair binding / Omega_app freeze** | 2e516d95200f5297e9e4a3a83445cc29462fc61beefe527c8022e0648fe89905 |
| **Dynamic V2V freeze**              | 3bcbbcb3623b07c3e8a162e24c5b63303b866cf9d149a68d083c30b5f7856193 |
| **Dynamic V2V JSONL**               | a86269bec9bd3a776ca1e8120f0175c838485ae31f15a53c6a2b706af0b17939 |
| **Dynamic V2V summary**             | 3ed7e2e8066a370ee685c7bfe5a92e1bce52778e043a216e632e08fe5d6e9b47 |
| **Shadow full126 result ZIP**       | 7dc9a66c41cdb0dba78762dbc9606b7c103da32177eb2d730d94e95f70ab34b9 |
| **Dataset Contract V1**             | 46f2e099fbe9090a02b1f9fe8a983e4f8322a2ffeba89a4700de8e278991dcda |
| **C04 root collector result**       | daa9bc9e278aabf54b26e9858a08b0d58fb8192a2511f57f7d15bd4098a20422 |
| **C04 Value V1 checkpoint**         | 6c223729cbbba3044b972fd7a90f4121e883fd34c9a6093f2b8e18597cf11413 |
| **C11/C06 collector result**        | 94ec9778a2899825125eaaed5c2ece50b8d0cd29390481c1e6f2ac568f052300 |
| **Three-scene LOSO result**         | 7c296200504ed75ca216a46bc74427703f99a9d5c75f35b0b1bd7e20fd10cdf1 |
| **LOSO formal summary**             | ac1d46ca91d6813e868121ced41e8751479ed2f4d4d6afd437921313e42b6e5a |
| **V1 failure diagnostic result**    | d16b2f0805235a5aedc07909e763329984588b3bed145fb46557a97388a1b6fa |
| **V2 interaction probe delivery**   | e14aafd8c1b859a7f967b1f5eb4e33d0a7cb900dcb29b23ec1d316d52268c356 |

**17. 证据来源索引与冲突处理原则**

| **证据**                                                                        | **主要用途 / 优先级**                                                                       |
|---------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------|
| **2026-08-21 当前对话终端/ZIP/JSON**                                            | V2R→Dynamic V2V→Shadow→Dataset→Collector→Value V1/V2 最新状态；最高优先级。                 |
| **MineSim-Dynamic_全项目阶段性总总结与AI无缝接管手册_2026-08-18.docx**          | baseline/Pure MCTS/J117/FullMine/Fleet/visual/cleanup 历史综合；被8/21 neural进展部分更新。 |
| **MineSim_云端项目文件整理最终文档包.zip / cleanup.md**                         | Phase2A–2K、current_paths、restore、HARD HOLD、删除=0。                                     |
| **AI接手文档(1).zip**                                                           | 7/26～8/17 共11份历史Word，补足演进。                                                       |
| **Dynamic V2V freeze / Shadow full / C04 collector / V1 pipeline attached ZIP** | 直接JSON/manifest/SHA证据。                                                                 |
| **C11/C06 current-semantic terminal output**                                    | 890/146 roots、行为SHA byte-exact、94ec result。                                            |
| **Three-scene LOSO terminal output**                                            | 三个fold正式指标、readiness=False、7c296 result。                                           |
| **V1 failure diagnostic result ZIP**                                            | Q scale、feature OOD、ridge结构局限与DO_NOT_INTEGRATE。                                     |
| **可参考论文.7z**                                                               | 方法适配来源；不替代项目事实，不复制paper参数。                                             |

> • 旧 Word 的“下一阶段”若与更晚终端冲突，旧 Word 只保留历史价值。8/18 的“V2R V3 static next / Neural not started”已被8/21结果覆盖。
>
> • 文件名和路径不是事实本身；必须核SHA、manifest、JSON字段、RC、PASS gate。
>
> • 生产/矿区真值不能从算法实验反推；production drivability、terrain datum、human uncertainty 仍需外部权威。
>
> • 失败不自动等于代码错误；必须区分 harness/import/path/wrapper/science 失败。

**18. 快速接手区：下一位 AI 必须先读**

| **CURRENT_STATE** 核心仿真链已冻结；Paper1 safety/data current-semantic collector 已完成；神经网络 V1 已正式训练但跨场景失败，明确禁止接入 MCTS。当前唯一下一步是低资源执行 V2 interaction/target probe，并根据≥2/3 held-out 场景是否优于 immediate_reward 决定进入 V2 neural design 或先扩充 episode。 |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

| **事项**          | **必须记住**                                                                                                                                                        |
|-------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **正式 repo**     | /root/MineSim-Dynamic                                                                                                                                               |
| **预期 HEAD**     | 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e                                                                                                                            |
| **Frozen tag**    | fullmine-vector-v4-runtime-freeze-20260814                                                                                                                          |
| **预期 status**   | 已知 \`?? ^C\` 必须保留；未知tracked/staged变化先停下。                                                                                                             |
| **关键数据 root** | /root/autodl-tmp；若存在先读 00_MineSim_ACTIVE/current_paths.json。                                                                                                 |
| **绝对不能动**    | runtime semantic/bitmap symlink target、90_MineSim_ARCHIVE、98_MineSim_QUARANTINE、99_MineSim_CLEANUP_MANIFEST、dirty historical workspace、frozen result/bundles。 |
| **已冻结不重做**  | IDM baseline、Pure MCTS、J117、FullMine V4、Representative MCTS、Polygon21、cross-scene、Native Video V2、cleanup、V2R/zone/dynamic V2V/shadow/data collector。     |
| **当前开发证据**  | C04/C11/C06 current-semantic 18592 rows；Value V1 LOSO与failure diagnostic。                                                                                        |
| **HOLD**          | production-authoritative drivability、terrain/Z、V2H、full safe-node、hard pruning、Policy/PUCT、Value-guided MCTS、最终泛化claim。                                 |
| **当前 next**     | Value V2 interaction/target probe V1；不是新仿真、不是GPU训练、不是MCTS集成。                                                                                       |

**18.1 下一步最小行动**

| **项目**   | **当前规则 / 真实观测**                                                                                                                                   |
|------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|
| **资源**   | 低资源 2GiB / 0.5CPU；CUDA禁用；不需要高资源卡或screen。                                                                                                  |
| **输入1**  | /root/autodl-tmp/PAPER1_THREE_SCENE_LOSO_VALUE_NETWORK_V1_UPLOAD.zip；SHA 7c296200504ed75ca216a46bc74427703f99a9d5c75f35b0b1bd7e20fd10cdf1。              |
| **输入2**  | /root/autodl-tmp/PAPER1_VALUE_NETWORK_V2_INTERACTION_TARGET_PROBE_V1_DELIVERY.zip；SHA e14aafd8c1b859a7f967b1f5eb4e33d0a7cb900dcb29b23ec1d316d52268c356。 |
| **Runner** | 包内 RUN_PAPER1_VALUE_NETWORK_V2_INTERACTION_TARGET_PROBE_V1.sh；runner SHA 4c1e6e046e637a42563dcbc7cb8c92da361c6f52474dc268111c5e18ee7ddf6d。            |
| **输出**   | /root/autodl-tmp/PAPER1_VALUE_NETWORK_V2_INTERACTION_TARGET_PROBE_V1_UPLOAD.zip。                                                                         |

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
# 先核 HEAD/status、formal result SHA、delivery SHA，再在子 shell 中运行包内 runner。</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

| **完成标准**        | **必须看到 / 解释**                                                                                            |
|---------------------|----------------------------------------------------------------------------------------------------------------|
| **Evidence**        | PASS EVIDENCE_SHA_GATE；REPO_UNCHANGED=PASS。                                                                  |
| **Probe**           | PASS V2_INTERACTION_TARGET_PROBE；每个 held-out 场景输出三个 target 候选的 root Spearman/Top1/regret。         |
| **Decision fields** | BEST_CANDIDATE、BEST_CANDIDATE_IMMEDIATE_REGRET_WIN_COUNT、DECISION。                                          |
| **Final**           | PASS PAPER1_VALUE_NETWORK_V2_INTERACTION_TARGET_PROBE_V1。                                                     |
| **分支A**           | win_count≥2：支持 scene-invariant interaction + 新target 路线，进入真正 V2 neural design；仍需新独立验证数据。 |
| **分支B**           | win_count\<2：不堆网络，先采更多 current-semantic scene/episode。                                              |

**18.2 继续前必须先检查**

> • pwd/repo、conda、Python=3.9.25；torch可导入（当前2.8.0+cpu）。
>
> • git HEAD=112d2bd…；status仅已知 \`?? ^C\`；不要清理。
>
> • formal LOSO result 7c296… 与 V2 delivery e14a… SHA一致。
>
> • 没有重复screen/Python任务；当前步骤不需高资源。
>
> • 不要把 V1 checkpoint 6c223… 接到 fleet_search；不要启用 hard pruning。
>
> • 若 V2 方案根据C04/C11/C06结果选定，立即登记这三场景为development evidence，后续final claim必须用新未见数据。

| **下一位 AI 第一轮回答格式** 只输出 CURRENT_STATE / DIFF_FROM_EXPECTED / NEXT_ONE_STEP / RESOURCE / RISKS-HOLD。若 preflight 与本文一致，直接推进 V2 probe；不要重述整本项目、不要重跑任何 frozen benchmark。 |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

— 文档结束｜Evidence cutoff: 2026-08-21 —
