**MineSim-Dynamic**

**全项目超详细阶段性总总结与 AI 无缝接管手册**

**2026-08-25 C06 seed1 one-time execution authorization 停点版**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>当前停点（唯一有效）</strong></p>
<p>C04 seed5 新独立 current-semantic episode 已完成 full run、postexec audit 与最终冻结；C06 seed1 已完成 parent provenance、预注册、精确两处静态派生、execution admission preflight 与 one-time execution authorization。C06 尚未创建 START、尚未启动进程、尚未产生 output/evidence，one-time attempt 尚未消耗。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

| **项目**            | **当前定义**                                                                  |
|---------------------|-------------------------------------------------------------------------------|
| **Evidence cutoff** | 2026-08-25 06:12（截至 C06 seed1 one-time execution authorization Gate PASS） |
| **正式仓库**        | /root/MineSim-Dynamic                                                         |
| **冻结 HEAD**       | 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e                                      |
| **实验/证据根**     | /root/autodl-tmp                                                              |
| **神经网络证据根**  | /root/autodl-tmp/paper1_value_v3_development_only_v1                          |
| **当前下一 Gate**   | HIGH_CPU_FINAL_PREEXEC_START_RUN_CAPTURE                                      |
| **当前资源**        | LOW 已完成；下一步才切 HIGH-CPU；CUDA 必须保持禁用                            |

*用途：供下一位 AI / 工程人员在不重新扫描全项目、不重复已冻结实验、不改变科学协议的前提下，无缝继续推进。*

# **文档控制、证据口径与覆盖关系**

本文是 2026-08-24 各版综合接手文档的增量替代版。此前文档中有关“当前节点、下一步、资源判断、C04/C06 coverage 状态”的描述，如与本文冲突，以本文和当前 frozen JSON/SHA/终端证据为准；此前文档继续作为历史 provenance 使用。

| **控制项**        | **固定口径**                                                                                                                                           |
|-------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| **事实优先级**    | 当前 AutoDL 终端 / Git / 源码 / 文件 SHA / 实际运行输出 \> frozen result/manifest/lock/freeze \> 最新交接 Word \> 历史 Word \> 计划 \> 模型记忆。      |
| **工作流**        | 只读 preflight -\> static/smoke -\> 短闭环 -\> 完整实验 -\> freeze；一次只推进一个最小 Gate。                                                          |
| **失败分类**      | 必须区分 pre-runtime technical、runtime technical、scientific failure。文件名包含 PASS/final/freeze 不等于真正通过。                                   |
| **One-time 规则** | 执行前必须有 preregistration、输入 SHA、namespace absent、authorization、START、进程确认；执行后立即 CAPTURE/RC/result/log/SHA；技术失败不得自动重跑。 |
| **资源规则**      | LOW 处理 Git/SHA/AST/schema/py_compile/preflight；HIGH-CPU 处理长 MineSim/collection；HIGH-GPU 仅用于明确需要 CUDA 的训练/forward。                    |
| **作者边界**      | 本文只写“云端实际完成了什么”。并非每个脚本都具备独立作者签名，不虚构逐文件归属。                                                                       |
| **未验证规则**    | 缺少直接证据的内容标记 HOLD/未验证；不得用常识补齐。                                                                                                   |

## **快速导航**

| **章节**  | **内容**                                        |
|-----------|-------------------------------------------------|
| **1-3**   | 当前状态、发展时间线、运行架构                  |
| **4-5**   | 已冻结主线成果、Value V1/V2/V3 与 coverage 决策 |
| **6**     | C04 seed5 coverage 全链闭合                     |
| **7**     | C06 seed1 当前链与精确停点                      |
| **8**     | 下一步 HIGH-CPU one-time runbook                |
| **9**     | 故障分类、禁止事项、恢复规则                    |
| **10-12** | 路径/SHA 速查、最终接手问答、附录               |

# **1. 当前项目 30 秒状态与快速结论**

| **对象**          | **当前状态**                                 | **证据/约束**                                                                                         |
|-------------------|----------------------------------------------|-------------------------------------------------------------------------------------------------------|
| **主线阶段**      | Value V3 development-only coverage expansion | Value V2 已关闭；原固定 Value V3 9/9 folds 技术完成但仅 2/3 scene win。                               |
| **C04 coverage**  | FROZEN PASS                                  | seed5 full current-semantic episode：148 roots / 2368 action rows；技术 PASS + 科学 PASS；禁止重跑。  |
| **C06 coverage**  | AUTHORIZED_NOT_STARTED                       | seed1 prereg、static derive、admission preflight、one-time authorization 均 PASS；尚未 START/launch。 |
| **当前唯一 Gate** | HIGH_CPU_FINAL_PREEXEC_START_RUN_CAPTURE     | 下一步只能做 final preexec -\> 原子 START -\> 唯一一次 full episode -\> 立即 CAPTURE。                |
| **当前资源**      | LOW 已结束；下一步 HIGH-CPU                  | 不需要 GPU；CUDA_VISIBLE_DEVICES 必须为空。                                                           |
| **当前 blocker**  | 不是代码/协议 blocker                        | 执行授权已闭合；只差用户切高资源并执行受控 one-time run。                                             |
| **训练状态**      | HOLD                                         | C06 未采完、未 postexec freeze 前，不得合并新数据或重训 Value V3。                                    |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>最重要的停点语义</strong></p>
<p>C06 seed1 的 authorization 已创建，但 authorization 不等于执行。当前 output root、evidence root、START、CAPTURE 均不存在，process 未启动。因此 one-time attempt 仍未消耗。下一位 AI 不得把“已授权”误写成“已运行”。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

当前无需重做：MineSim baseline、Pure MCTS、单车、双车 causal benchmark、FullMine V4、Fleet-MCTS、cross-scene、Native Video V2、云端整理、C03 collection、Value V2 closure、原 Value V3 9-fold、C11 expanded coverage、C04 seed5 coverage。

当前绝对不能做：重跑 C04 seed5；绕过 C06 authorization/START 直接运行；提前创建 C06 output/evidence；自动重试；改 scenario/route/zone/reward/MCTS 参数；启用 CUDA；开始 Value V3 retraining 或 MCTS value integration。

# **2. 真实发展时间线（主线顺序）**

| **日期**               | **阶段**                              | **真实完成与意义**                                                                                                          |
|------------------------|---------------------------------------|-----------------------------------------------------------------------------------------------------------------------------|
| **2026-07-26**         | MineSim baseline 与安全操作规范       | 建立 AutoDL/Git/文件优先的工作方式；不按记忆猜 API。                                                                        |
| **2026-07-30 - 08-02** | Pure MCTS closed-loop                 | MCTSPlanner -\> search/reward -\> trajectory adapter -\> Controller/KBM；形成 strict expert。                               |
| **2026-08-03 - 08-07** | 五 Planner / budget / interface audit | 明确搜索、trajectory adapter、controller、vehicle model 的故障边界。                                                        |
| **2026-08-08 - 08-10** | 双受控 + J117                         | Jiangtong 负筛选；J117 423-step 单车；双车 NO-MCTS causal conflict + Pure MCTS multiseed。                                  |
| **2026-08-11 - 08-14** | FullMine V1 -\> Vector V4             | O(1) token lookup、Vector V2 semantic、bitmap/runtime/planner 修复；HEAD 112d2bd 冻结。                                     |
| **2026-08-14**         | Representative Pure MCTS              | 跨代表区域 3/3 PASS。                                                                                                       |
| **2026-08-15**         | Polygon21 Fleet-MCTS                  | NO-MCTS 真实物理重叠；Fleet budget64/depth8 5/5。                                                                           |
| **2026-08-16**         | Native Video + safe cleanup           | Native Video V2 final；可逆整理；科研文件删除 0。                                                                           |
| **2026-08-17 - 08-18** | Cross-scene + Paper1 safety           | C04/C11/C06；C11 安全死锁负结果；SafetyRisk/sidecar。                                                                       |
| **2026-08-21**         | current-semantic neural data chain    | V2R/zone/dynamic V2V/shadow/root diagnostic collector；C04/C11/C06 collection；Value V1 science FAIL。                      |
| **2026-08-22 - 08-24** | Value V2 / Value V3                   | Value V2 independent science FAIL 后关闭；Value V3 9/9 folds 技术 PASS、2/3 scene win，转入 coverage expansion。            |
| **2026-08-24**         | C11 expanded coverage                 | 80m+100m independent episodes、2052-root adapter、expanded V3 retry1；C11 继续失败，定位为 held-out C11 训练 support 不足。 |
| **2026-08-25**         | C04 seed5 coverage                    | 协议修复、one-step smoke、seed5 prereg/static/auth/full run/postexec freeze；148 roots / 2368 rows。                        |
| **2026-08-25**         | C06 seed1 coverage（当前）            | parent provenance、seed1 prereg、exact two-edit derivation、admission preflight、one-time authorization PASS；尚未执行。    |

| **阶段**                     | **状态**               | **当前真实结论**                                                               |
|------------------------------|------------------------|--------------------------------------------------------------------------------|
| **MineSim 原项目复现**       | PASS / FROZEN          | Dapai/Jiangtong IDM、replay、closed-loop baseline。                            |
| **Pure MCTS / 单车**         | PASS / FROZEN          | 真实 MineSim online closed-loop；J117 423 steps；FullMine representative 3/3。 |
| **双车 / causal benchmark**  | PASS / FROZEN          | A/B 同步受控；NO-MCTS exact overlap 证明 causal conflict。                     |
| **FullMine 新地图**          | PASS / FROZEN          | Vector V2 semantic + V4 bitmap/runtime/planner；Research/DEV 边界。            |
| **Fleet-MCTS / cross-scene** | PASS + 负结果          | Polygon21 5/5；C04/C06 success；C11 safe deadlock，必须保留。                  |
| **原生可视化 / 整理**        | PASS / FROZEN          | Native Video V2；可逆 cleanup。                                                |
| **Value V2**                 | CLOSED / SCIENCE FAIL  | C03 normalized regret 劣于 immediate baseline；DO_NOT_INTEGRATE。              |
| **Value V3 fixed**           | TECH PASS / NOT READY  | C04/C06 win、C11 fail；2/3，禁止调网络过 gate。                                |
| **C04 new coverage**         | FROZEN PASS            | seed5 148 roots / 2368 rows。                                                  |
| **C06 new coverage**         | AUTHORIZED_NOT_STARTED | seed1 等待 HIGH-CPU one-time execution。                                       |

# **3. 运行架构、核心调用链与科学边界**

run_simulation.py  
-\> SimulationsRunner.\_initialize()  
-\> EnvironmentSimulation.initialize()  
-\> Scenario / Map loader  
-\> Planner.initialize()  
-\> 每帧 Planner.compute_planner_trajectory()  
-\> TwoStageController.update_state()  
-\> LQR / iLQR trajectory tracking  
-\> KinematicBicycleModel.propagate_state()  
-\> Observation / Agent Update / MultiEgoRuntime  
-\> SimulationHistory / metrics / logs  
-\> 下一帧

系统边界：项目没有重写完整 MineSim。Pure MCTS / Fleet-MCTS 主要替换或扩展 Planner 决策层；规划轨迹仍由 Controller 与车辆模型真实执行。Scenario、Map、Observation、Controller、Vehicle、History/Metrics 都是科学链的一部分。

| **层**                     | **关键代码/目录**                                       | **职责与接手风险**                                                             |
|----------------------------|---------------------------------------------------------|--------------------------------------------------------------------------------|
| **Scenario / Environment** | devkit/sim_engine/environment_manager；scenario_manager | schema、location、绝对路径不可猜。                                             |
| **Map**                    | semantic/bitmap loader；FullMine runtime                | semantic identity、bitmap symlink、scale/flip、SHA 不可随意改。                |
| **Planning / Pure MCTS**   | planner/mcts/\*；trajectory_adapter                     | future trajectory 不等于下一帧状态；adapter 故障不等于搜索失败。               |
| **Multi/Fleet**            | multi_ego_runtime；fleet_state/transition/reward/search | A/B 同一 iteration；受控车必须从 external actor 中剔除。                       |
| **Control / Vehicle**      | TwoStageController；KinematicBicycleModel               | 合法 trajectory 不保证 controller 可实现；rear axle 与 footprint 不能混。      |
| **Safety**                 | exact footprint/swept geometry + sidecars               | shadow observational 不等于 hard pruning；safe 不等于任务完成。                |
| **Neural evidence**        | /root/autodl-tmp/paper1_value_v3_development_only_v1    | collector/model/evaluator 位于 evidence workspace，未集成 production planner。 |

| **合同项**             | **冻结定义**                                                           |
|------------------------|------------------------------------------------------------------------|
| **Fleet action space** | A/B 各 4 个 longitudinal action；4 x 4 = 16 joint actions。            |
| **MCTS**               | budget=64；depth=8；MCTS dt=0.5 s。                                    |
| **Simulation**         | sim dt=0.1 s；max horizon=89.0 s；max steps=890。                      |
| **Geometry**           | RouteGeometryCache；rear-axle route_s -\> geometric-center footprint。 |
| **Safety**             | exact footprint/swept overlap；shadow sidecar 不删节点。               |
| **Value integration**  | MCTS_VALUE_INTEGRATION=False；禁止提前接入 PUCT/value guidance。       |

# **4. 已冻结主线成果与不可回退边界**

## **4.1 MineSim baseline、Pure MCTS、单车与双车**

- 正式仓库只认 /root/MineSim-Dynamic；冻结 HEAD=112d2bd0f3412fc83b13d5587d2b41402d2d0f5e。

- Pure MCTS 已接入真实 closed-loop；搜索结果经 trajectory adapter、Controller 和 Kinematic Bicycle Model 执行。

- 双车体系由 MultiEgoRuntime 管理 A/B live controlled state；不能用 A history 推断 B truth。

- NO-MCTS causal benchmark 必须先证明真实物理重叠；空间路径相交不等于 temporal conflict。

## **4.2 FullMine Vector V4 与地图口径**

- FullMine current baseline：Vector V2 semantic + V4 bitmap/runtime/planner，targeted 7/7 与 old-map regression 已完成。

- “Research/DEV map 可运行”不等于 production-authoritative drivability。缺官方 mask/internal exclusion/authoring rule 的事项继续 HOLD。

- 恢复 frozen runner 的绝对路径时，优先恢复历史路径/软链接，不直接修改 runner。

## **4.3 Fleet-MCTS 与 cross-scene 科学结论**

| **场景**      | **NO-MCTS causal**   | **Fleet-MCTS**                                   | **科学含义**                              |
|---------------|----------------------|--------------------------------------------------|-------------------------------------------|
| **Polygon21** | NO-MCTS 真实物理重叠 | Fleet 5/5 PASS                                   | 干净 benchmark。                          |
| **C04**       | 真实 overlap         | authoritative success；seed5 新 coverage 也 PASS | 成功 transfer。                           |
| **C11**       | causal conflict      | 89 s / 890 steps，无碰撞但 post-conflict 未完成  | 真实安全死锁/进度失败，禁止调参抹掉。     |
| **C06**       | 真实 overlap         | 历史 seed0 success；seed1 已授权待运行           | 成功 transfer；当前补 training coverage。 |

## **4.4 原生可视化与云端整理**

- Native Video V2 final 已冻结；汇报材料必须来自 frozen map/scenario/runtime truth，不能手工改科学轨迹。

- cleanup 是可逆移动/隔离，不等于删除；90_MineSim_ARCHIVE、98_MineSim_QUARANTINE、99_MineSim_CLEANUP_MANIFEST 不可擅动。

- 已知科研文件删除数为 0；其他手动删除情况若无 live evidence，继续 HOLD。

# **5. 神经网络 / Value 主线与 coverage 扩展理由**

## **5.1 current-semantic 数据合同**

Neural Dataset Contract V1 的 raw unit 是 ONE_MCTS_ROOT_SEARCH，派生训练 unit 是 ONE_ROOT_STATE_X_ONE_JOINT_ACTION；每个 root 必须包含 16 个 joint actions，Q 为 primary target，immediate reward 为基线/辅助信息。真实 root JSONL schema 为 actionwise\[16\]，q_value 与 immediate_reward 位于每个 action item 内部，而不是 root 顶层。

ONE_MCTS_ROOT_SEARCH  
└── actionwise\[16\]  
├── joint_action_id ("A,B")  
├── action {A: int, B: int}  
├── q_value  
├── immediate_reward  
├── child_state  
└── risk_auxiliary

## **5.2 Value V1 / V2 / V3 结论**

| **阶段**              | **状态**                           | **结论**                                                                                                                  |
|-----------------------|------------------------------------|---------------------------------------------------------------------------------------------------------------------------|
| **Value V1**          | Pipeline PASS / science FAIL       | C04 126、C11 890、C06 146 roots；3-fold LOSO；held-out 排名均不达标。                                                     |
| **Value V2**          | CLOSED / SCIENCE FAIL              | ROOT_CENTERED_Q 12-\>64-\>64-\>16；C03 independent normalized regret 0.3506036 \> immediate 0.1831771；DO_NOT_INTEGRATE。 |
| **Value V3 fixed**    | 9/9 folds TECH PASS / NOT READY    | root-normalized weighted pairwise logistic；C04/C06 win、C11 fail；2/3。                                                  |
| **Expanded Value V3** | Retry1 completed / still not ready | C11 增量不能改善 held-out C11 的训练端；诊断转向补 C04/C06 coverage。                                                     |

## **5.3 为什么补 C04/C06，而不是继续堆 C11**

LEAVE_ONE_SCENE_OUT 协议下，held-out C11 时所有 C11 episode 都在 validation，训练端只剩 C04+C06。旧 support 约为 C04 fold 的 14.1%。继续只增加 C11 会扩大验证覆盖，却不会增加 held-out C11 fold 的训练监督，因此 coverage 优先级切换到 C04/C06；split 本身仍被冻结，不能为过 gate 修改。

| **数据对象**       | **规模**                    | **状态/意义**                                   |
|--------------------|-----------------------------|-------------------------------------------------|
| **历史 C04**       | 126 roots / 2016 rows       | 1 episode，success                              |
| **C04 seed5 新增** | 148 roots / 2368 rows       | 1 independent episode，success，已冻结          |
| **历史 C06**       | 146 roots / 2336 rows       | 1 episode，success                              |
| **C06 seed1 新增** | 未执行，root count 不预声明 | 已授权，等待 one-time full episode              |
| **C11**            | 80m+100m 共 1780 roots      | 两个 seed0 independent episodes；科学结果均保留 |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>冻结科学边界</strong></p>
<p>C04/C06 coverage expansion 只允许增加真实独立 episode。不得改 Value V3 架构、loss、feature、epoch、训练 seed、normalization 公式、MCTS reward、action space 或 LOSO split；Value V3 retraining 必须等 C06 postexec freeze 与新 dataset/adapter prereg 完成后另开 Gate。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# **6. C04 seed5 coverage 全链闭合（已冻结，不再触碰）**

## **6.1 从 protocol schema blocker 到 one-step smoke**

C04 1-step Fleet-MCTS development smoke 最初在 simulation/MCTS 前因旧 v1 timing/replacement admission 读取失败。只修改 development copy，将 admission 映射到 amendment_v2 的 C04_promotion schema；static diff、py_compile、protocol readback 全 PASS。唯一一次 1-step smoke 随后真实跑通 initialize -\> FleetState -\> search -\> transition -\> control trajectory -\> propagate。

## **6.2 seed5 prereg、执行与结果**

| **字段**                 | **冻结结果**                                                                                  |
|--------------------------|-----------------------------------------------------------------------------------------------|
| **Runtime seed**         | 5（最小未使用 C04 seed；performance-independent）                                             |
| **Runner RC**            | 0                                                                                             |
| **Steps / duration**     | 148 / 14.8 s                                                                                  |
| **Root records**         | 148                                                                                           |
| **Derived action rows**  | 2368                                                                                          |
| **Action contract**      | 16 actions/root；完整 4x4 joint action set；Q/immediate 全 finite                             |
| **Shadow records**       | 9472                                                                                          |
| **Fleet result**         | benchmark_success=True；completed_post_conflict=True；collision_avoided=True                  |
| **Safety/health**        | collision_or_overlap=False；physical_overlap=False；timeline_sync=True；nan=False；error=None |
| **Artifacts**            | 13 files；CAPTURE artifact SHA parity PASS                                                    |
| **Final classification** | TECHNICAL_PASS_SCIENTIFIC_PASS                                                                |

## **6.3 C04 关键冻结链**

| **对象**                  | **路径**                                                                                                                                                       | **SHA256**                                                       |
|---------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------|
| **1-step smoke freeze**   | /root/autodl-tmp/c04_fleet_mcts_1step_smoke_protocol_v2_execution_v1/C04_FLEET_MCTS_1STEP_PROTOCOL_V2_TECHNICAL_SMOKE_FREEZE_V1.json                           | c6d8ef823c5c493e7b23baa66c923a3a77c2897c51740a8895d496e92e8e1dbc |
| **seed5 prereg**          | /root/autodl-tmp/paper1_value_v3_development_only_v1/c04_seed5_development_prereg_v1/PAPER1_VALUE_V3_C04_SEED5_DEVELOPMENT_EPISODE_PREREGISTRATION_V1.json     | fb64373c2ea0fb59d2e9c912391546697d5f784fedcd4bafa7c53dcb4ed5fed2 |
| **derived runner**        | /root/autodl-tmp/paper1_value_v3_development_only_v1/c04_seed5_execution_package_v1/src/cross_scene_fleet_mcts_c04_seed5_paper1_neural_collector_current_v1.py | ac587bff24e8cffc3e0b116a173214d677554feea3d4002011940442b83e1378 |
| **static lock**           | /root/autodl-tmp/paper1_value_v3_development_only_v1/c04_seed5_execution_package_v1/PAPER1_VALUE_V3_C04_SEED5_STATIC_DERIVATION_LOCK_V1.json                   | 7e73e430f612ab5c0218b133552cc08253b308e25b1bbf0a3ee5e7bee8a386e1 |
| **post-publish closure**  | /root/autodl-tmp/paper1_value_v3_development_only_v1/c04_seed5_post_publish_binding_v1/PAPER1_VALUE_V3_C04_SEED5_POST_PUBLISH_BINDING_CLOSURE_V1.json          | 0266ce2eb5508aaa87f06afe2f486655032c5e9d92561d699a22f2d2acc40a73 |
| **authorization**         | /root/autodl-tmp/paper1_value_v3_development_only_v1/c04_seed5_execution_authorization_v1/PAPER1_VALUE_V3_C04_SEED5_ONE_TIME_EXECUTION_AUTHORIZATION_V1.json   | 2ccd8cf3fa9794d5c1239f81c8ffe2ff9fda7c5b4388708730487f53d6b36182 |
| **START**                 | /root/autodl-tmp/paper1_value_v3_development_only_v1/c04_seed5_execution_evidence_v1/START.json                                                                | 09636b17e7c730cd85fe34b03cc7aa3c5608805be11497f7e6fa0f7141874870 |
| **CAPTURE**               | /root/autodl-tmp/paper1_value_v3_development_only_v1/c04_seed5_execution_evidence_v1/CAPTURE.json                                                              | b924e79d563bb6505944ca0f22dbcf38e886baa4230d083403dde2d08cb49727 |
| **final postexec freeze** | /root/autodl-tmp/paper1_value_v3_development_only_v1/c04_seed5_postexec_acceptance_v1/PAPER1_VALUE_V3_C04_SEED5_POSTEXEC_COLLECTION_ACCEPTANCE_FREEZE_V1.json  | b0ac50052dd60ddfdc3e0a072057d7d5646fa7cd4356399000076c11f8bc09e0 |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>永久规则</strong></p>
<p>C04 seed5 one-time attempt 已消费，retry_authorized=False，automatic rerun forbidden。此前 postexec audit 因错误假设 q_values/immediate_rewards 位于 root 顶层而失败，已通过真实 actionwise[16] schema 修正；该事件不是 runtime/collection failure，未重跑 C04。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# **7. C06 seed1 coverage 当前链与精确停点**

## **7.1 历史 parent 与 seed0 closure**

C06 current-semantic parent 来自 PAPER1_NEURAL_C11_C06_CURRENT_SEMANTIC_COLLECTOR_V1_UPLOAD.zip。live extracted source 与 ZIP member byte-exact；root/dynamic/shadow helper 与当前 V3 helper trio 完全一致。历史 seed0 full episode 已 PASS：146 roots / 2336 rows、16 actions/root、benchmark success、post-conflict complete、无 overlap、timeline sync。

| **对象**                    | **路径**                                                                                                                                | **SHA256**                                                       |
|-----------------------------|-----------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------|
| **Parent package**          | /root/autodl-tmp/PAPER1_NEURAL_C11_C06_CURRENT_SEMANTIC_COLLECTOR_V1_UPLOAD.zip                                                         | 94ec9778a2899825125eaaed5c2ece50b8d0cd29390481c1e6f2ac568f052300 |
| **Parent runner**           | /root/autodl-tmp/paper1_neural_c11_c06_current_semantic_collector_v1/src/cross_scene_fleet_mcts_c06_seed0_paper1_neural_collector_v1.py | f766ea09a29757c28a89e98ccf89ecdf56c3f50fc2c4838ea8d909331711d843 |
| **Root helper**             | .../src/paper1_root_diagnostic_collector_v1.py                                                                                          | 283d2bfb38af5bd3ef1897349f1e366f862ab508250c1f262f15fd0509c4a2a6 |
| **Dynamic helper**          | .../src/paper1_dynamic_v2v_dsafe_v1.py                                                                                                  | d3fa8b666092c7b9c60654208decab38e9990e63082f32018206d1b4e76b2131 |
| **Shadow helper**           | .../src/paper1_shadow_safe_node_v1.py                                                                                                   | fc4fe915be4752996e2dd64d44d1de8b2a27f4c587f94250f9e64434fa2191e7 |
| **Historical seed0 result** | /root/autodl-tmp/paper1_neural_c11_c06_current_semantic_collector_v1/C06/cross-scene-c06-fleet-mcts-seed0-v2.json                       | 0cbec940ce6581da1669fb06f49d091267f2365c8909c0cacafe393693d3df22 |
| **Historical root summary** | .../C06/cross-scene-c06-fleet-mcts-seed0-paper1-neural-root-diagnostic-v1-summary.json                                                  | 287d22adefa6b886739067b8a5414833811b3d0d79af1c13568a548efe82d5f9 |

## **7.2 seed1 prereg 与精确两处派生**

- Observed C06 runtime seeds 仅 \[0\]；seed1 是最小未使用非负 seed，选择 outcome-independent、uses_performance=False。

- Parent root search 已经 seed=SEED，因此不允许修改 root-search seed。

- 授权 source diff 只有 2 项：SEED != 0 -\> SEED != 1；错误消息 seed0 -\> seed1 development。

- argparse default 保持 0，正式执行必须显式传 --seed 1；漏参会被 seed1-only guard 阻止。

- scenario、manifest、zone intervals、route、reward、budget/depth、DT、helper、protocol 均禁止修改。

| **对象**                   | **路径**                                                                                                                                                       | **SHA256**                                                       | **状态**                     |
|----------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------|------------------------------|
| **seed1 prereg**           | /root/autodl-tmp/paper1_value_v3_development_only_v1/c06_seed1_development_prereg_v1/PAPER1_VALUE_V3_C06_SEED1_DEVELOPMENT_EPISODE_PREREGISTRATION_V1.json     | 28d7dbd9fbf86934f8780b1c05217eecb2920e95a212e74d1130239ec71dfe17 | PREREGISTERED_EXECUTION_HOLD |
| **derived runner**         | /root/autodl-tmp/paper1_value_v3_development_only_v1/c06_seed1_execution_package_v1/src/cross_scene_fleet_mcts_c06_seed1_paper1_neural_collector_current_v1.py | 7c27789a6dd3092f54d580e8d0e23995bba6fdca18db9ba219742fc5f4525edc | STATIC PASS                  |
| **static lock**            | /root/autodl-tmp/paper1_value_v3_development_only_v1/c06_seed1_execution_package_v1/PAPER1_VALUE_V3_C06_SEED1_STATIC_DERIVATION_LOCK_V1.json                   | ee123d7673a616d1c8ebd2c067064a46757fe5448f68da849496addab8a4f0f6 | STATIC_DERIVATION_PASS       |
| **package SHA manifest**   | /root/autodl-tmp/paper1_value_v3_development_only_v1/c06_seed1_execution_package_v1/SHA256SUMS.txt                                                             | 0902785f9fa0ab87c6280138978e02bc19214095196d627ef311970f1be80404 | PASS                         |
| **one-time authorization** | /root/autodl-tmp/paper1_value_v3_development_only_v1/c06_seed1_execution_authorization_v1/PAPER1_VALUE_V3_C06_SEED1_ONE_TIME_EXECUTION_AUTHORIZATION_V1.json   | 839b1760a49b54841a09111e9322b88382481bccc1eaef44908e38cf5b3d08b6 | AUTHORIZED_NOT_STARTED       |

## **7.3 当前精确停点（2026-08-25 06:12）**

| **字段**                        | **当前值**                                                  |
|---------------------------------|-------------------------------------------------------------|
| **Authorization status**        | AUTHORIZED_NOT_STARTED                                      |
| **Authorization type**          | ONE_TIME_C06_SEED1_FULL_DEVELOPMENT_ROOT_DIAGNOSTIC_EPISODE |
| **Resource class**              | HIGH_CPU；cuda_used=False；gpu_required=False               |
| **Execution authorized**        | True                                                        |
| **Collection authorized**       | True                                                        |
| **START created**               | False                                                       |
| **Process launched**            | False                                                       |
| **One-time execution consumed** | False                                                       |
| **Retry authorized**            | False                                                       |
| **Output root**                 | ABSENT                                                      |
| **Evidence root**               | ABSENT                                                      |
| **START / CAPTURE**             | ABSENT / ABSENT                                             |
| **Current next gate**           | HIGH_CPU_FINAL_PREEXEC_START_RUN_CAPTURE                    |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>不可误读</strong></p>
<p>C06 已获得一次性执行授权，但尚未开始执行。AUTH JSON 是冻结输入，不应被改写；真正消耗 attempt 的时刻是下一 Gate 原子写入 START 并启动进程。当前不得提前创建 planned output root 或 evidence root。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## **7.4 C06 绑定的外部输入**

| **输入**                  | **路径**                                                                                                                                       | **SHA256**                                                       |
|---------------------------|------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------|
| **Semantic**              | /root/autodl-tmp/fullmine_vector_v2_targeted_runtime/maps/semantic_map/geojson_full_mine_vector_v2_dev_semantic_map.json                       | b85a3d8b28f2252ecb5bda179d514573f6333079def838cd048566f556d95cd0 |
| **Protocol amendment v2** | /root/autodl-tmp/fullmine_v4_fleet_cross_scene_v1/cross_scene_protocol_amendment_v2.json                                                       | 27d76bce3b52706eb738c3da695325ab2fb20d3350ab2aadb4e15b30740ab42f |
| **Static readiness**      | /root/autodl-tmp/fullmine_v4_fleet_cross_scene_v1/cross_scene_static_readiness_final_v1.json                                                   | 828b1f2282a7cca396577be0aab2af97231445fab1ad202dcadd6acf88c48edc |
| **B reference**           | /root/autodl-tmp/fullmine_v4_dual_candidate_v1/polygon21_b_reference_chain_audit_v1.json                                                       | 39f29de451ff64a418cdc78abdafedc568db7efffe7380064c95a8026612040e |
| **C06 loader**            | /root/autodl-tmp/fullmine_v4_fleet_cross_scene_v1/c06_loader_diag_v1/c06_loader_v1_20260817_212241/cross-scene-c06-real-loader-smoke-v2.json   | 3581e7ef6b62645d60999679f954b8b2ef3da7eecc445c3941c4af0a5ea9ed90 |
| **C06 NOMCTS**            | /root/autodl-tmp/fullmine_v4_fleet_cross_scene_v1/c06_nomcts_diag_v1/c06_nomcts_20260817_212500/cross-scene-c06-nomcts-causal-conflict-v2.json | db78f35b57ad897b50386698ddf488ab7b30343cf452ae61a9c86ab901c2f2fd |
| **C06 scenario**          | /root/autodl-tmp/fullmine_v4_fleet_cross_scene_v1/scenarios_v1/Scenario-fullmine-v4-cross-scene-c06-dual-aligned-v1.json                       | 01cfa268af7cc6df5eecb4c31defecbc55c6c876035ed88430f11479048d02d6 |
| **C06 scene manifest**    | /root/autodl-tmp/fullmine_v4_fleet_cross_scene_v1/scenarios_v1/cross_scene_c06_scenario_manifest_v1.json                                       | 4fefcfff35a20a1faff6872d89e24b742055ce722737e1aeebfc750fef269e45 |
| **C06 static A**          | /root/autodl-tmp/fullmine_v4_fleet_cross_scene_v1/static_drivability_v1/cross-scene-c06-A_result_v1.json                                       | 4d91267ec58fd101642eecea22f751b0ed3a50163f663c1adb6c272b28bb85f2 |
| **C06 static B**          | /root/autodl-tmp/fullmine_v4_fleet_cross_scene_v1/static_drivability_v1/cross-scene-c06-B_result_v1.json                                       | dac442face05c4016fda3c4d4945891d7eecdca1980f0f70baab26e279ff69b1 |

## **7.5 冻结的准确执行命令与 namespace**

/root/miniconda3/envs/minesim/bin/python -u \\  
/root/autodl-tmp/paper1_value_v3_development_only_v1/c06_seed1_execution_package_v1/src/cross_scene_fleet_mcts_c06_seed1_paper1_neural_collector_current_v1.py \\  
--source-index 6 \\  
--seed 1

| **项目**                 | **值**                                                                                                        |
|--------------------------|---------------------------------------------------------------------------------------------------------------|
| **Working directory**    | /root/MineSim-Dynamic                                                                                         |
| **PYTHONPATH**           | /root/autodl-tmp/paper1_value_v3_development_only_v1/c06_seed1_execution_package_v1/src:/root/MineSim-Dynamic |
| **OUTPUT_ROOT**          | /root/autodl-tmp/paper1_value_v3_development_only_v1/c06_seed1_development_collection_v1                      |
| **EVIDENCE_ROOT**        | /root/autodl-tmp/paper1_value_v3_development_only_v1/c06_seed1_execution_evidence_v1                          |
| **START**                | .../c06_seed1_execution_evidence_v1/START.json（当前不存在）                                                  |
| **CAPTURE**              | .../c06_seed1_execution_evidence_v1/CAPTURE.json（当前不存在）                                                |
| **CUDA_VISIBLE_DEVICES** | \<empty\>                                                                                                     |

# **8. 下一步唯一行动：HIGH-CPU final preexec -\> START -\> run -\> CAPTURE**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>下一步资源</strong></p>
<p>HIGH-CPU。Fleet-MCTS 长闭环主要使用 CPU/RAM；即使实例带 4090D，也必须保持 CUDA_VISIBLE_DEVICES=""。不要因为高资源已开启而扩大实验范围。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## **8.1 执行前必须重新确认**

1.  进入 /root/MineSim-Dynamic，激活 minesim；确认 Git HEAD 仍为 112d2bd...，tracked status 为空。

2.  重新核对 prereg、derived、static lock、package manifest、helper trio、authorization 的 SHA；AUTH_SHA 必须为 839b1760....

3.  执行 package SHA256SUMS.txt 全量校验。

4.  确认 derived process 不存在；OUTPUT_ROOT、EVIDENCE_ROOT、START、CAPTURE 全部不存在。

5.  读取 AUTH JSON，确认 status=AUTHORIZED_NOT_STARTED、attempt=1、max attempts=1、retry_authorized=False。

6.  确认 exact command、source_index=6、seed=1、max horizon=89.0、max steps=890、budget=64、depth=8、dt 合同不变。

## **8.2 原子 START 与唯一一次执行**

7.  只有所有 preexec Gate PASS 后，创建 EVIDENCE_ROOT。

8.  先写 START.json，记录 authorization/derived SHA、argv、environment、machine、attempt_number=1、one_time_execution_consumed=True。

9.  START 写盘并计算 SHA 后，才允许启动准确命令。

10. 进程结束后无论 RC=0 还是 RC=1，都立即保存 runner_rc.txt、stdout、stderr，并写 CAPTURE.json。

11. CAPTURE 必须记录 output root 是否存在、实际 artifact 列表/大小/SHA、authorization/start/runner SHA 与 retry_authorized=False。

12. 从 START 写入并启动进程开始，one-time attempt 已消费；不得再次运行。

## **8.3 Postexec 审计必须使用真实 schema**

C06 使用与 C04 相同的 current root helper，postexec auditor 必须按 actionwise\[16\] 读取 Q 与 immediate reward。不得再次假设 root 顶层存在 q_values / immediate_rewards。

- root JSONL 每行 type=PAPER1_NEURAL_ROOT_DIAGNOSTIC_V1，record_unit=ONE_MCTS_ROOT_SEARCH。

- root_action_count=16；actionwise 必须包含完整 {0,0 ... 3,3} joint action set。

- 每个 action item 的 q_value 和 immediate_reward 必须存在且 finite。

- provenance 必须 source_index=6、seed=1、mcts_budget=64、mcts_depth=8、mcts_dt_s=0.5。

- root count 不预声明；由实际 episode 完成时长决定。

## **8.4 结果分类矩阵**

| **情形**                                       | **分类**                           | **动作**                                                                         |
|------------------------------------------------|------------------------------------|----------------------------------------------------------------------------------|
| **RC=0 + artifacts 完整 + benchmark PASS**     | TECHNICAL_PASS_SCIENTIFIC_PASS     | 接受 collection，冻结科学 PASS。                                                 |
| **RC=1 + artifacts 完整 + benchmark FAIL**     | TECHNICAL_PASS_SCIENTIFIC_NEGATIVE | 接受 collection，原样保留负科学结果；不得重跑挑好结果。                          |
| **0 step / 无 output / import/path/exception** | TECHNICAL_FAILURE                  | 保存 START/CAPTURE/traceback；不得自动重跑；先单独审计是否允许 technical retry。 |
| **部分 roots 后 runtime exception**            | RUNTIME_TECHNICAL_FAILURE          | 记录已产生科学信息的范围；不得把已观察结果包装成无成本 retry。                   |

## **8.5 C06 full run 后还不能直接训练**

C06 run 完成后，必须先进行 LOW 的 postexec artifact/collection acceptance audit，生成 C06 final freeze。之后还需另开 Gate：把 C04 seed0+seed5、C06 seed0+seed1、C11 episodes 适配为 episode-aware root-level dataset，冻结新 dataset/manifest/normalization/baseline，再决定是否预注册新的 Value V3 evaluation。不能从 C06 run 直接跳到训练。

# **9. 故障分类、禁止事项与恢复规则**

## **9.1 故障分层**

| **分类**                  | **例子**                                                         | **处理**                                    |
|---------------------------|------------------------------------------------------------------|---------------------------------------------|
| **Pre-runtime technical** | CLI/import/path/env/schema/stale guard/authorization/namespace   | 通常无科学结果；只修当前 fault domain。     |
| **Runtime technical**     | Python exception、controller/adapter、write failure、OOM/SIGKILL | 记录发生在多少 step/root 后；不得自动重跑。 |
| **Scientific failure**    | benchmark 未完成、deadlock、泛化低于 baseline、安全但任务失败    | 真实科研结果；禁止调参或重跑抹掉。          |

## **9.2 当前禁止事项**

- 禁止重跑 C04 seed5，禁止修改其 13 个 output artifacts、START、CAPTURE、freeze。

- 禁止修改 C06 prereg、derived、static lock、SHA manifest、authorization；任何 SHA 漂移均应 HOLD。

- 禁止在 START 前创建 C06 planned output/evidence namespace。

- 禁止自动重试 C06；禁止因结果不好换 seed2。

- 禁止改 source6 scenario、manifest、zone intervals、route、reward、target speed、MCTS budget/depth/DT、action space。

- 禁止启用 CUDA；禁止提前训练 Value V3 或接入 MCTS value/PUCT。

- 禁止 git clean 清理未知文件；禁止擅动 90_ARCHIVE/98_QUARANTINE/99_CLEANUP_MANIFEST。

## **9.3 恢复与重连最小检查**

cd /root/MineSim-Dynamic  
source /root/miniconda3/etc/profile.d/conda.sh 2\>/dev/null \|\| true  
conda activate minesim  
export PYTHONDONTWRITEBYTECODE=1  
export CUDA_VISIBLE_DEVICES=""  
  
git rev-parse HEAD  
git status --short --untracked-files=no  
  
\# 然后按本文 SHA 表只读核验当前 Gate 的输入与 namespace。

## **9.4 已知近期技术事件（避免重复踩坑）**

| **事件**                                  | **现象**                                               | **正确结论**                                                                  |
|-------------------------------------------|--------------------------------------------------------|-------------------------------------------------------------------------------|
| **C04 protocol admission**                | 旧 v1 timing/replacement schema 与 amendment_v2 不兼容 | 已在 development copy 最小修复并冻结；不影响正式 repo。                       |
| **C04 static lock path**                  | staging path 在 atomic publish 后失效                  | 内容 SHA 不变；用独立 post-publish closure 闭合，未重写旧 lock。              |
| **C04 postexec audit**                    | 错误假设 q_values/immediate_rewards 位于 root 顶层     | 真实 schema 为 actionwise\[16\]；修审计器，不重跑实验。                       |
| **C06 admission 前误用旧 static command** | execution package 已存在导致 NAMESPACE_ALREADY_EXISTS  | 是重复运行旧 Gate，不是 C06 package 失败；随后正确 admission preflight PASS。 |
| **High-resource banner**                  | 曾见 OMP_NUM_THREADS/libgomp 警告                      | C04 runner RC0、stderr=0；下次只读记录，不修改科学代码。                      |

# **10. 当前路径与 SHA 速查**

| **对象**                     | **路径**                                                             | **状态**                                      |
|------------------------------|----------------------------------------------------------------------|-----------------------------------------------|
| **Formal repo**              | /root/MineSim-Dynamic                                                | HEAD 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e |
| **Data root**                | /root/autodl-tmp                                                     | 大文件/日志/结果                              |
| **FullMine runtime**         | /root/autodl-tmp/fullmine_vector_v2_targeted_runtime                 | semantic/map runtime                          |
| **Cross-scene evidence**     | /root/autodl-tmp/fullmine_v4_fleet_cross_scene_v1                    | C04/C11/C06/C03 evidence                      |
| **Value V3 root**            | /root/autodl-tmp/paper1_value_v3_development_only_v1                 | development-only evidence root                |
| **C11/C06 parent live root** | /root/autodl-tmp/paper1_neural_c11_c06_current_semantic_collector_v1 | historical parent + seed0 artifacts           |

## **10.1 C06 当前执行链速查**

| **对象**              | **路径**                                                                                                      | **SHA/状态**                                                     |
|-----------------------|---------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------|
| **Prereg**            | .../c06_seed1_development_prereg_v1/PAPER1_VALUE_V3_C06_SEED1_DEVELOPMENT_EPISODE_PREREGISTRATION_V1.json     | 28d7dbd9fbf86934f8780b1c05217eecb2920e95a212e74d1130239ec71dfe17 |
| **Execution package** | .../c06_seed1_execution_package_v1                                                                            | package integrity PASS                                           |
| **Derived runner**    | .../c06_seed1_execution_package_v1/src/cross_scene_fleet_mcts_c06_seed1_paper1_neural_collector_current_v1.py | 7c27789a6dd3092f54d580e8d0e23995bba6fdca18db9ba219742fc5f4525edc |
| **Static lock**       | .../c06_seed1_execution_package_v1/PAPER1_VALUE_V3_C06_SEED1_STATIC_DERIVATION_LOCK_V1.json                   | ee123d7673a616d1c8ebd2c067064a46757fe5448f68da849496addab8a4f0f6 |
| **SHA manifest**      | .../c06_seed1_execution_package_v1/SHA256SUMS.txt                                                             | 0902785f9fa0ab87c6280138978e02bc19214095196d627ef311970f1be80404 |
| **Authorization**     | .../c06_seed1_execution_authorization_v1/PAPER1_VALUE_V3_C06_SEED1_ONE_TIME_EXECUTION_AUTHORIZATION_V1.json   | 839b1760a49b54841a09111e9322b88382481bccc1eaef44908e38cf5b3d08b6 |
| **Planned output**    | .../c06_seed1_development_collection_v1                                                                       | 当前必须不存在                                                   |
| **Evidence root**     | .../c06_seed1_execution_evidence_v1                                                                           | 当前必须不存在                                                   |

## **10.2 C04 已关闭链速查**

| **对象**         | **路径/状态**                                                                                                | **SHA**                                                          |
|------------------|--------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------|
| **Final freeze** | .../c04_seed5_postexec_acceptance_v1/PAPER1_VALUE_V3_C04_SEED5_POSTEXEC_COLLECTION_ACCEPTANCE_FREEZE_V1.json | b0ac50052dd60ddfdc3e0a072057d7d5646fa7cd4356399000076c11f8bc09e0 |
| **Output root**  | .../c04_seed5_development_collection_v1；13 artifacts；禁止修改                                              | artifact SHA 已写入 freeze                                       |
| **Result**       | seed5；148 steps；14.8 s；scientific PASS                                                                    | 78fdbe692482b95f75c5595d8135da178df5525cc80927ebbcaac0064d6781c4 |
| **Root JSONL**   | 148 roots；actionwise_list_v1                                                                                | ba143a08fc6ad4da97e18009c52a69212ff7b3164fc730448229d93c7a82bde3 |
| **Root summary** | 2368 action rows；16/root                                                                                    | 18087349c3754003d7ae6cd2da9fc3fc03510e92f2cf38d997aad0386cf076b5 |

# **11. 最终快速接手问答**

| **问题**                            | **当前唯一有效答案**                                                                                                     |
|-------------------------------------|--------------------------------------------------------------------------------------------------------------------------|
| **项目真正做到哪里？**              | C04 seed5 coverage 已完整冻结；C06 seed1 已授权但未启动。                                                                |
| **当前唯一 blocker / gate？**       | HIGH_CPU_FINAL_PREEXEC_START_RUN_CAPTURE。                                                                               |
| **C06 已经运行了吗？**              | 没有。START=False、process=False、output/evidence absent。                                                               |
| **C06 one-time attempt 消耗了吗？** | 没有。只有下一 Gate 写 START 并启动进程后才消耗。                                                                        |
| **下一步需要什么资源？**            | HIGH-CPU；CUDA 禁用；不需要 HIGH-GPU。                                                                                   |
| **准确 AUTH SHA？**                 | 839b1760a49b54841a09111e9322b88382481bccc1eaef44908e38cf5b3d08b6。                                                       |
| **允许改代码吗？**                  | 不允许。derived/package/static lock/authorization 均冻结。                                                               |
| **运行失败能自动重试吗？**          | 不能。先 CAPTURE、分类、保存证据，再决定是否存在明确 technical retry。                                                   |
| **RUN_RC=1 是否自动丢弃数据？**     | 不是。benchmark success 与 collection acceptance 分离，必须看 artifacts/data contract。                                  |
| **C06 后可以直接训练吗？**          | 不能。先 postexec freeze，再建 episode-aware expanded dataset 与新评估 prereg。                                          |
| **可以重跑 C04 吗？**               | 绝对不可以。C04 one-time 已消费并 frozen PASS。                                                                          |
| **哪些长期 HOLD？**                 | production-authoritative drivability、terrain/Z/slope、V2H/full safe-node/hard pruning、Policy/PUCT、Value-guided MCTS。 |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>下一位 AI 的第一句话应是什么</strong></p>
<p>“当前 C06 seed1 authorization 已冻结（AUTH SHA=839b1760...），但 START/process/output/evidence 均不存在；先在 HIGH-CPU 上做 final preexec，所有 Gate PASS 后才原子写 START 并执行一次。”</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# **12. 附录：交接后执行与结果上传规范**

## **12.1 执行结束后的结果包建议结构**

c06_seed1_execution_evidence_v1/  
├── START.json  
├── CAPTURE.json  
├── runner_rc.txt  
├── runner_stdout.txt  
├── runner_stderr.txt  
└── （可选）SHA256SUMS.txt  
  
c06_seed1_development_collection_v1/  
├── cross-scene-c06-fleet-mcts-seed1-v2.json  
├── cross-scene-c06-fleet-mcts-seed1-v2.log  
├── ...paper1-neural-episode-manifest-v1.json  
├── ...paper1-neural-root-diagnostic-v1.jsonl  
├── ...paper1-neural-root-diagnostic-v1-summary.json  
├── ...paper1-shadow-safe-node-v1.jsonl  
└── ...paper1-shadow-safe-node-v1-summary.json  
  
注：实际 artifact inventory 以 CAPTURE 为准，不预先伪造额外文件。

## **12.2 用户返回信息的最小集合**

- 完整 final preexec / START / launch / CAPTURE 终端输出，或直接上传日志文本。

- START SHA、CAPTURE SHA、RUN_RC、output file count、process after run。

- 若有 exception，上传 runner_stderr.txt 与 CAPTURE；不要自行重跑。

- 若运行完成，上传 output/evidence 压缩包，下一步只做 LOW 的 postexec audit。

## **12.3 本文证据来源**

| **类型**         | **来源**                                                                                                                     |
|------------------|------------------------------------------------------------------------------------------------------------------------------|
| **综合历史**     | 2026-08-18/21/23/24 各版 MineSim-Dynamic 阶段总结与接手手册。                                                                |
| **工作流 Skill** | 粘贴的 markdown (1)。md：one Gate、preflight/static/full/freeze、资源与 one-time 规则。                                      |
| **C04 终端证据** | 2026-08-25 04:36 - 04:54 上传文本：schema、smoke、seed5 run、postexec freeze。                                               |
| **C06 终端证据** | 2026-08-25 04:56 - 06:12 上传文本：parent audit、seed1 prereg、static derive、admission preflight、authorization。           |
| **最终停点证据** | 粘贴的文本 (1)(20260825-061208).txt：AUTHORIZATION_GATE=PASS，AUTH_SHA=839b1760...，START/process/output/evidence 均未创建。 |
