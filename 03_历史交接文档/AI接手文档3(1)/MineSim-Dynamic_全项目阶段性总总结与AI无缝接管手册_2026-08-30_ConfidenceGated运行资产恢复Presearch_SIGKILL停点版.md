**MineSim-Dynamic**

**全项目阶段性总总结与 AI 无缝接管手册**

*2026-08-30 · Value V3 机制诊断闭环、Confidence-Gated Root Ordering 与运行资产恢复停点版*

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>当前权威停止点</strong></p>
<p>byte-exact canonical bitmap 与 semantic 已恢复到新 recovery namespace；recovery pre-search probe runner 已派生并通过静态行序检查，但真实 pre-search replay 以 RC=-9（SIGKILL）结束。未到达 PRESEARCH_POINT，未捕获 Python 原始异常；原因尚未证明。Attempt 5 未创建，SIGKILL/OOM 只读诊断按用户要求暂不执行。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

| **字段**             | **当前值**                                                                               |
|----------------------|------------------------------------------------------------------------------------------|
| **文档版本**         | V1.0 · 当前权威 handoff                                                                  |
| **证据截止**         | **2026-08-30；截至 RUNTIME_RECOVERY_PRESEARCH_VALIDATION_GATE=HOLD**                     |
| **当前阶段**         | Confidence-Gated Root Ordering 新机制分支 · runtime recovery / pre-search validation     |
| **当前科学状态**     | NO_VALID_CONFIDENCE_GATED_MCTS_RESULT；27-cell matrix 未启动                             |
| **当前技术状态**     | **RECOVERED_ASSETS_BYTE_EXACT_PASS；PRESEARCH_REPLAY_RC=-9；CAUSE=HOLD**                 |
| **当前资源**         | PAUSED；恢复工作时下一步为 LOW / CPU-only；GPU 不需要                                    |
| **当前唯一 blocker** | 解释 recovery pre-search replay 的 SIGKILL(-9)：OOM / cgroup / host termination 尚未证明 |
| **用户指令**         | 此处停点；暂不执行 SIGKILL diagnosis                                                     |
| **正式 repo**        | /root/MineSim-Dynamic                                                                    |
| **主 evidence root** | /root/autodl-tmp/paper1_value_v3_development_only_v1                                     |

*用途：交接给下一位 ChatGPT / Codex / 工程执行人员。任何晚于本证据截点的 AutoDL 终端、Git、源码、START/CAPTURE/result/freeze 自动优先于本 Word。*

# **0. CURRENT_STATE｜一页接手摘要**

| **字段**                  | **当前值 / 接管解释**                                                                                                          |
|---------------------------|--------------------------------------------------------------------------------------------------------------------------------|
| **EVIDENCE_CUTOFF**       | 2026-08-30；最新执行证据为 runtime recovery pre-search replay：RC=-9、point=False、original_exception=False。                  |
| **CURRENT_STAGE**         | **Value-guided MCTS root-order-only 分支已 COMPLETE/FROZEN；当前为全新 confidence-gated root-ordering exploratory branch。**   |
| **CURRENT_GATE**          | RUNTIME_RECOVERY_PRESEARCH_SIGKILL_CAUSE_DIAGNOSIS（按用户要求尚未执行）。                                                     |
| **CURRENT_STATUS**        | **offline mechanism diagnosis COMPLETE；threshold/controller/cellspec frozen；closed-loop safe smoke 尚未技术通过。**          |
| **LATEST_GIT_HEAD**       | 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e；最近成功 preflight 均要求 tracked clean。                                            |
| **CURRENT_EVIDENCE_ROOT** | /root/autodl-tmp/paper1_value_v3_development_only_v1/paper1_value_v3_confidence_gated_root_order_v1                            |
| **LATEST_FROZEN_RESULT**  | 36-cell offline mechanism diagnosis + exact stratified association；不是 confidence-gated MCTS 科学结果。                      |
| **CURRENT_BLOCKER**       | recovered runtime pre-search probe 被 SIGKILL；无 stderr，未到达 pre-search marker，当前不能写 OOM。                           |
| **NEXT_MINIMAL_ACTION**   | 用户恢复时：LOW 只读执行 SIGKILL diagnosis，读取 cgroup memory.events、/proc/meminfo、kernel OOM 与 bitmap header。            |
| **PASS_STANDARD**         | 给出 OOM_SUPPORTED 或 CAUSE_NOT_PROVEN 的证据化分类；不创建 Attempt5、不 forward、不 MCTS。                                    |
| **RESOURCE_REQUIRED**     | LOW / CPU-only；仅在 OOM 被支持且重新授权高内存 probe 时才切 HIGH-CPU；HIGH-GPU 不需要。                                       |
| **DO_NOT_REPEAT**         | 所有 root-order-only B8/B16/B32/B64；offline one-root/full36；Confidence smoke Attempt1/2/3/4；runtime recovery replay。       |
| **HOLD_ITEMS**            | SIGKILL cause、checkpoint 是否在该次 recovery replay 中完成加载、Attempt5 authorization、27-cell scientific matrix、系统收益。 |
| **LATEST_HANDOFF**        | **本 Word。此前 2026-08-30 ValueGuidedMCTS 闭环与文件整理终版降为 frozen baseline / historical current-state。**               |

## **0.1 60 秒科学口径**

- Value V3 模型级能力成立：C01 independent 3-seed median regret=0.1058394967，优于 frozen immediate baseline=0.2951958616。

- naive root-order-only integration 的完整 36-cell 闭环已经冻结为负收益：Pure 首次稳定 B8，Guided 首次稳定 B64，稳定预算、expansions 和 wall-clock 均更差。

- 随后对全部 36 个 frozen Guided cells 做了 12,142-root offline mechanism diagnosis；Scientific FAIL cells 与更低 score margin、更低 neural/MCTS 一致率、更差 selected-action neural rank 显著相关。

- 新 confidence-gated 机制已预注册：margin\>=0.06767839193344116 使用 neural root ordering；否则回退 original Pure root random ordering；不改 UCT、rollout、backup、reward、transition、action space。

- 但新机制目前没有任何技术有效的 closed-loop MCTS 结果。当前只完成资产恢复与 pre-search 探路；最后一次 probe 被 SIGKILL(-9)，原因 HOLD。

## **0.2 当前分支状态图**

| **分支 / 阶段**                              | **状态**              | **当前结论**                                                                                            |
|----------------------------------------------|-----------------------|---------------------------------------------------------------------------------------------------------|
| **A. Value-guided root-order-only baseline** | **COMPLETE / FROZEN** | B8 6/9；B16 7/9；B32 8/9；B64 9/9；最终系统收益为负。                                                   |
| **B. Offline mechanism diagnosis**           | **COMPLETE / FROZEN** | 36 cells、12,142 roots、27,216 exact permutations；4/4 指标方向一致且 Holm 显著。                       |
| **C. Confidence-gated design/build**         | PRESTART BUILT        | threshold/controller/runner/27-cell CellSpec/static review 已冻结。                                     |
| **D. Safe-smoke technical chain**            | **TECHNICAL HOLD**    | Attempt1 import；Attempt2 semantic path；Attempt3 masked error；Attempt4 bitmap path。均无有效 search。 |
| **E. Runtime asset recovery**                | **BYTE-EXACT PASS**   | bitmap/semantic 在新 namespace 恢复，SHA 与 canonical 完全一致。                                        |
| **F. Recovery pre-search validation**        | **HOLD**              | RC=-9；no point；no Python exception；Attempt5 未创建。                                                 |

## **0.3 当前停点的最短描述**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>一句话接管</strong></p>
<p>旧 root-order-only 分支与 offline mechanism diagnosis 已冻结；confidence gate 代码和阈值已冻结，但 closed-loop 尚未跑通。canonical bitmap/semantic 已用 byte-exact 副本恢复到新 runtime root；pre-search validation 被 SIGKILL(-9)，原因未诊断。用户明确要求停在这里，Attempt5 不存在。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# **目录与推荐阅读顺序**

- 0\. CURRENT_STATE｜一页接手摘要

- 1\. 文档控制、证据等级与状态词典

- 2\. 项目长期主线总览

- 3\. MineSim 运行架构与永久科学边界

- 4\. Value V3 与 root-order-only 完整冻结基线

- 5\. Offline mechanism diagnosis：one-root → full36 → association

- 6\. Confidence-gated 机制预注册、阈值与代码边界

- 7\. Confidence-gated safe-smoke / prestart 全时间线

- 8\. 运行资产丢失表象、byte-exact 恢复与当前 SIGKILL 停点

- 9\. 本轮重要失败复盘（现象→原因→排查→处理→证据→禁止重复）

- 10\. 关键路径、SHA 与状态矩阵

- 11\. 资源、协作、文件与 Git 工作流

- 12\. DO_NOT_REPEAT / HOLD / 不可回退项

- 13\. 云端文档、归档、删除与恢复边界

- 14\. 快速接手区

- 附录 A. 本轮时间线

- 附录 B. 下一 Gate 的 PASS / FAIL 标准

- 附录 C. 论文与科学表述边界

**推荐阅读：新 AI 先读第 0、5、6、7、8、12、14 节；只有发生 SHA/provenance 冲突时再回查第 2～4 节。**

# **1. 文档控制、证据等级与状态词典**

## **1.1 事实优先级**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>固定证据优先级</strong></p>
<p>当前 AutoDL 终端 / 当前 Git / 当前源码 / 实际运行结果 / SHA &gt; frozen result / manifest / lock / START / CAPTURE &gt; 本交接 Word &gt; 历史 handoff &gt; 设计计划 &gt; AI 记忆。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

- 文件名含 PASS、final、freeze、V2 不等于真实通过；必须结合 RC、JSON 字段、log、SHA、manifest 与 Gate。

- 历史 handoff 中的“下一步”若被后续证据覆盖，只保留 provenance，不再作为当前指令。

- 当前缺少直接证据的事项写 HOLD；尤其 RC=-9 的原因不能自动写成 OOM。

- ChatGPT 附件存在不等于 AutoDL 已上传；AutoDL path missing 不等于文件实际删除。

## **1.2 本版主要证据源**

| **证据**                                                        | **用途**                                            | **等级**            |
|-----------------------------------------------------------------|-----------------------------------------------------|---------------------|
| **2026-08-30 ValueGuidedMCTS 闭环终版 Word**                    | root-order-only 36-cell 结果、最终效率、数据盘整理  | **Frozen baseline** |
| **当前 AutoDL 终端：one-root/full36/offline association**       | 机制诊断、阈值与新分支依据                          | 最高                |
| **Confidence-gated build/prestart logs**                        | controller/runner/CellSpec/threshold/static binding | 当前                |
| **Safe-smoke Attempt1–4 START/CAPTURE/stdout/stderr/diagnosis** | 技术失败边界与禁止重跑                              | 当前                |
| **Bitmap recovery discovery + runtime recovery log**            | byte-exact 资产恢复与 RC=-9 当前停点                | 最新                |
| **MineSim-Dynamic 项目统一工作流 Skill**                        | 交接结构、资源、one-time、freeze 与协作规范         | 流程约束            |

## **1.3 状态词典**

| **术语**                     | **准确含义**                                                           |
|------------------------------|------------------------------------------------------------------------|
| **FROZEN**                   | 已有不可变 result/decision/freeze/SHA；默认只读，不覆盖、不重跑。      |
| **Technical PASS**           | 技术链、身份、输入、输出、计数、instrumentation 全部有效。             |
| **Scientific PASS**          | Technical PASS 且预注册质量谓词全部通过。                              |
| **Scientific FAIL**          | Technical PASS 但科学谓词不全过；是真实负结果，必须计入并冻结。        |
| **Technical HOLD / FAILURE** | 路径、import、schema、资源、进程、validator 等问题；不形成新科学结论。 |
| **AUTHORIZED_NOT_STARTED**   | authorization 已创建但 START 未写；只允许继续 prestart。               |
| **START consumed**           | START_WRITTEN=True 后同条件不可重跑，即便 SSH/postcheck 失败。         |
| **HOLD / NOT PROVEN**        | 直接证据不足；不得用推测补齐。                                         |
| **SUPERSEDED / HISTORICAL**  | 后续证据已覆盖当前状态，但仍保留 provenance。                          |

## **1.4 本版不做的事情**

- 不执行尚未运行的 SIGKILL/OOM diagnosis；只记录其为 pending。

- 不重跑 recovery pre-search replay，也不创建 Attempt5。

- 不把 RC=-9 直接解释为 OOM，不把 recovery probe 写成科学实验。

- 不修改任何旧 START/CAPTURE/result/freeze、canonical archive 或 recovered assets。

- 不宣称 confidence-gated MCTS 已有效，也不开始 27-cell matrix。

# **2. 项目长期主线总览**

| **阶段**                           | **状态**                     | **当前真实结论**                                                           |
|------------------------------------|------------------------------|----------------------------------------------------------------------------|
| **MineSim 原项目复现**             | **PASS / FROZEN**            | IDM、replay、closed-loop 基础已建立。                                      |
| **蒙特卡洛 / Pure MCTS**           | **PASS / FROZEN**            | 真实 online search/reward/trajectory/controller 链跑通。                   |
| **单车**                           | **PASS / FROZEN**            | J117 与 FullMine representative 单车闭环已验证。                           |
| **双车冲突场景**                   | **PASS + 负结果**            | NO-MCTS causal conflict、双 controlled ego 与 temporal conflict 边界形成。 |
| **FullMine 新地图**                | **PASS / Research-DEV**      | Vector V2 semantic + V4 bitmap/runtime；不得写 production-authoritative。  |
| **Fleet-MCTS**                     | **PASS + Scientific FAIL**   | 成功场景与 C11 safe deadlock 等真实负结果并存。                            |
| **多种子 / cross-scene**           | **FROZEN**                   | C04/C11/C06 development、blind C01 与多 seed 协议。                        |
| **原生可视化**                     | **PASS / 部分 HOLD**         | Native Video 主线完成，历史 showcase 仅作 provenance。                     |
| **云端文件整理**                   | **COMPLETE**                 | 顶层 746→23；仅 \_\_pycache\_\_ 实际删除，其余可逆移动。                   |
| **Value V2**                       | CLOSED                       | 独立验证 FAIL，DO_NOT_INTEGRATE。                                          |
| **Value V3**                       | **INDEPENDENT PASS**         | 12D→16 scores，模型级 action-ranking signal 成立。                         |
| **Root-order-only Guided MCTS**    | **COMPLETE / FROZEN**        | B8/B16/B32/B64 完成；系统稳定性与效率收益为负。                            |
| **Offline mechanism diagnosis**    | **COMPLETE / FROZEN**        | 36 cells / 12,142 roots；低 confidence 与 FAIL 强关联。                    |
| **Confidence-gated root ordering** | **CURRENT / TECHNICAL HOLD** | 设计与阈值冻结；closed-loop 尚未技术通过。                                 |

## **2.1 当前新增分支与旧终版的关系**

2026-08-30 的“ValueGuidedMCTS 闭环与文件整理终版”仍是 naive root-order-only 分支的权威终版。当前工作不是改写或续跑该分支，而是依据其建议建立的全新 confidence-gated 分支。旧结果继续作为 immutable negative baseline。

# **3. MineSim 运行架构与永久科学边界**

## **3.1 主运行链**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>run_simulation / benchmark runner<br />
→ EnvironmentSimulation.initialize()<br />
→ Scenario / semantic map / bitmap loader<br />
→ Planner.initialize() / planner trajectory<br />
→ Fleet-MCTS search<br />
→ Trajectory Adapter<br />
→ TwoStageController / LQR-iLQR<br />
→ KinematicBicycleModel<br />
→ Observation / MultiEgoRuntime<br />
→ history / metrics / result / logs</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## **3.2 故障分层纪律**

| **层**                            | **固定边界**                                                                       |
|-----------------------------------|------------------------------------------------------------------------------------|
| **Scenario / Map**                | 输入路径、semantic、bitmap、地图 loader；当前 RC=-9 仍位于 pre-search runtime 层。 |
| **Planner**                       | 轨迹合法性与 route 绑定；不等于 controller 可实现。                                |
| **MCTS / Search**                 | 只有非零 search metrics/root records 才能证明实际 search。                         |
| **Controller / Vehicle model**    | 执行异常不等于 search 失败。                                                       |
| **Observation / MultiEgoRuntime** | 每辆 controlled ego 独立 truth/history；B 不由 A 推断。                            |
| **Collision / Safety**            | safe 不等于 success；CollisionLookup 不等于 exact footprint truth。                |
| **Metrics / History**             | 后处理 NameError 可能遮蔽前置真实异常；必须恢复原始异常。                          |

## **3.3 当前故障层定位**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>当前不是 MCTS 科学失败</strong></p>
<p>recovery replay 未到达 pre-search marker，且 marker 位于 BENCHMARK_SEARCH_DIAGNOSTICS 初始化与 search.search() 之前。因此 model forward 和 MCTS search 未发生；当前属于 runtime/process termination Technical HOLD。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# **4. Value V3 与 root-order-only 完整冻结基线**

## **4.1 Value V3 冻结协议**

| **项目**              | **冻结值**                                              |
|-----------------------|---------------------------------------------------------|
| **Dataset**           | 2356 roots；37696 action rows；6 episodes               |
| **Identity**          | (scene, episode_uid, root_step)                         |
| **Input / output**    | 12D root features → 16 joint-action scores              |
| **Architecture**      | 12 → 64 → 64 → 16；ActionConditionedValueV3PairwiseRank |
| **Objective**         | ROOT_NORMALIZED_WEIGHTED_PAIRWISE_LOGISTIC              |
| **Split**             | LEAVE_ONE_SCENE_OUT                                     |
| **Final model seeds** | 20260824 / 20260825 / 20260826                          |
| **Epochs / LR**       | 600 / 0.001                                             |
| **Best-seed / HPO**   | False / False                                           |
| **Action index**      | joint_action_index = action_A \* 4 + action_B           |

## **4.2 C01 independent result**

| **对象**                       | **结果**                            |
|--------------------------------|-------------------------------------|
| **Immediate baseline**         | 0.2951958615926099                  |
| **Model seed 20260824 regret** | 0.09947470394112914                 |
| **Model seed 20260825 regret** | 0.15596316637663826                 |
| **Model seed 20260826 regret** | 0.10583949665541333                 |
| **3-seed median**              | 0.10583949665541333 \< baseline     |
| **Classification**             | **INDEPENDENT_GENERALIZATION_PASS** |

## **4.3 Root-order-only 36-cell matrix**

| **Budget** | **R0/M24** | **R0/M25** | **R0/M26** | **R1/M24** | **R1/M25** | **R1/M26** | **R2/M24** | **R2/M25** | **R2/M26** |
|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|
| **B8**     | P          | F          | P          | P          | F          | P          | P          | F          | P          |
| **B16**    | F          | P          | P          | F          | P          | P          | P          | P          | P          |
| **B32**    | P          | P          | P          | P          | P          | P          | P          | P          | F          |
| **B64**    | P          | P          | P          | P          | P          | P          | P          | P          | P          |

*P=Scientific PASS；F=Technical PASS / Scientific FAIL。所有 F 均已冻结，不允许挑 seed 重跑。*

## **4.4 最终系统结论**

| **指标**                                 | **Pure**   | **Root-order-only Guided** | **结论**     |
|------------------------------------------|------------|----------------------------|--------------|
| **Minimum stable budget**                | Pure B8    | Guided B64                 | Guided 更差  |
| **Median total_tree_expansions**         | 3432       | 9664                       | 2.82×        |
| **Median outer_search_wallclock_ms_sum** | 6763.01 ms | 20098.90 ms                | 2.97×        |
| **Primary lower-budget claim**           | —          | Scientific FAIL            | **REJECTED** |
| **Secondary efficiency claim**           | —          | Scientific FAIL            | **REJECTED** |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>准确表述</strong></p>
<p>Value V3 独立 ranking signal 成立，但 naive root-order-only integration 没有把该信号转化为更低稳定预算或更低真实搜索成本。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# **5. Offline mechanism diagnosis：one-root → full36 → association**

## **5.1 诊断目的与科学边界**

该阶段不重跑 MCTS，而是读取 frozen root snapshots，使用 frozen checkpoints 做 offline score forward，恢复 16-action score/ranking/margin，并与 frozen cell-level Scientific PASS/FAIL 关联。它用于机制诊断，不产生新的闭环因果结论。

## **5.2 One-root pilot**

| **字段**           | **结果**                                                         |
|--------------------|------------------------------------------------------------------|
| **Root identity**  | C01 / B16 / runtime0 / model20260824 / root_step0 / search_call0 |
| **Feature**        | \[4.5,4.5,0,0,50,49.999996,0,3.009468,0.957943,0,0,1\]           |
| **Forward count**  | 1                                                                |
| **Top1**           | action 3,3；score 5.020596027374268                              |
| **Top2**           | action 2,3；score 3.401560068130493                              |
| **Margin**         | 1.6190359592437744                                               |
| **MCTS execution** | 0                                                                |
| **Status**         | **TECHNICAL PASS / FROZEN**                                      |

## **5.3 Full36 offline diagnosis**

| **字段**                        | **结果**                                                                                    |
|---------------------------------|---------------------------------------------------------------------------------------------|
| **Guided cell count**           | 36                                                                                          |
| **Total frozen roots**          | 12,142                                                                                      |
| **B8 / B16 / B32 / B64 roots**  | 4539 / 3607 / 2436 / 1560                                                                   |
| **Checkpoint loads**            | 3 total；每个 model seed 1 次                                                               |
| **Model forwards**              | **12,142；每 frozen root 1 次**                                                             |
| **MCTS / rollout / controller** | 0 / 0 / 0                                                                                   |
| **Output**                      | **one JSONL row per root；16 scores/ranking/top1/top2/margin + partial frozen MCTS fields** |
| **Status**                      | **TECHNICAL PASS / FROZEN**                                                                 |

## **5.4 Cell-level exact association**

| **指标**                             | **FAIL-PASS budget-centered effect** | **Exact p**  | **Holm p**   | **方向**  | **Direction OK** |
|--------------------------------------|--------------------------------------|--------------|--------------|-----------|------------------|
| **margin_median**                    | -0.8400447441                        | 3.674309e-05 | 0.0001469724 | FAIL 更低 | True             |
| **top1_equals_frozen_selected_rate** | -0.0838197481                        | 3.674309e-05 | 0.0001469724 | FAIL 更低 | True             |
| **selected_neural_rank_median**      | +1.4888888889                        | 0.0004409171 | 0.0004409171 | FAIL 更差 | True             |
| **top1_equals_partial_best_q_rate**  | -0.0838425830                        | 3.674309e-05 | 0.0001469724 | FAIL 更低 | True             |

统计单位为 36 个 cells，而不是 12,142 个 roots；按 budget 保持每层 FAIL 数量，精确枚举 27,216 种合法分配，避免 root-level 伪重复。

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>机制解释（探索性）</strong></p>
<p>Scientific FAIL cells 与低 margin、neural/MCTS disagreement 和更差 selected-action neural rank 强关联。该证据支持测试 confidence gate，但不证明 gate 一定改善闭环。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# **6. Confidence-gated 机制预注册、阈值与代码边界**

## **6.1 Frozen mechanism**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>每个 root：<br />
1) 提取 frozen 12D features<br />
2) Value V3 forward exactly once → 16 scores<br />
3) margin = top1_score - top2_score<br />
4) if margin &gt;= 0.06767839193344116:<br />
use neural root ordering<br />
else:<br />
use original Pure-MCTS root random ordering<br />
5) 后续 UCT / rollout / backup / reward / transition 不变</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## **6.2 Threshold derivation**

| **字段**                 | **冻结值**                                                           |
|--------------------------|----------------------------------------------------------------------|
| **Confidence statistic** | top1_top2_margin                                                     |
| **Frozen threshold**     | 0.06767839193344116                                                  |
| **Rule**                 | 六个 frozen Scientific-FAIL cells 的 cell-level margin_median 中位数 |
| **Selection timing**     | 任何新 confidence-gated MCTS execution 之前                          |
| **Threshold sweep**      | 禁止                                                                 |
| **Entropy**              | V1 不使用；normalization rule 未预先冻结                             |

## **6.3 New branch CellSpec**

| **字段**                 | **值**                                         |
|--------------------------|------------------------------------------------|
| **Namespace**            | paper1_value_v3_confidence_gated_root_order_v1 |
| **Budget ladder**        | \[8, 16, 32\]                                  |
| **Runtime seeds**        | \[0, 1, 2\]                                    |
| **Model seeds**          | \[20260824, 20260825, 20260826\]               |
| **Cell count**           | 27                                             |
| **Stable criterion**     | **9/9 Scientific PASS per budget**             |
| **Primary PASS**         | first stable budget \<=16                      |
| **Partial success**      | first stable budget ==32                       |
| **Primary FAIL**         | no stable budget through 32                    |
| **Current matrix state** | 0/27；未启动                                   |

## **6.4 Invariants**

- 每 root exactly one Value forward；tree search 内不 forward。

- 只改变 root depth-zero ordering；不剪枝、不 PUCT、不 selective expansion。

- 低 confidence fallback 使用原 naive Guided 已经消耗的同一 rng.randrange draw，尽量保持 RNG stream。

- UCT、rollout、backup、reward、transition、action provider/action space 不改。

- 三个 final checkpoints 不训练、不 fine-tune、不选择最佳 seed。

# **7. Confidence-gated safe-smoke / prestart 全时间线**

## **7.1 构建与授权前结果**

| **阶段**                 | **状态**        | **结论**                                                         |
|--------------------------|-----------------|------------------------------------------------------------------|
| **LOW build**            | **PASS**        | threshold/controller/static audit frozen                         |
| **Runner + CellSpec**    | **PASS**        | new runner + 27-cell contract + prestart review                  |
| **CLI discovery**        | **PASS**        | source-index=1；seed=0；guided；B8；model20260824                |
| **Scientific execution** | **NOT STARTED** | 后续尝试均为 technical smoke / diagnostics；无有效 search result |

## **7.2 Attempts / probes**

| **对象**                          | **执行状态**        | **阶段**              | **现象/错误**                                            | **已证明边界**                                    | **重跑**         |
|-----------------------------------|---------------------|-----------------------|----------------------------------------------------------|---------------------------------------------------|------------------|
| **Attempt1 safe smoke**           | START yes / RC1     | Import                | ModuleNotFoundError: paper1_root_diagnostic_collector_v1 | 0 output；no checkpoint/forward/MCTS              | NO RERUN         |
| **Attempt2 safe smoke**           | START yes / RC1     | Input guard           | canonical semantic path missing                          | output absent；no checkpoint/forward/MCTS         | NO RERUN         |
| **Attempt3 V1 prestart**          | NO START            | Controller bug        | SEMANTIC_SHA_PARSE=\[\]；empty manifest 后误打印 PASS    | false PASS 已撤回；无 auth/wrapper                | SUPERSEDED       |
| **Attempt3 V2 safe smoke**        | START yes / RC1     | Runtime before search | NameError BENCHMARK_SEARCH_DIAGNOSTICS                   | 4 constructor-side files；0 search metrics/result | NO RERUN         |
| **Attempt4 error probe**          | START yes / RC1     | Diagnostic pre-search | 恢复原始 FileNotFoundError: bitmap path                  | checkpoint constructed；no forward/MCTS           | NO RERUN         |
| **Attempt5 exact-name discovery** | NO START            | Read-only             | candidate=0 under /root/autodl-tmp exact name            | HOLD；Attempt5 not created                        | N/A              |
| **Wide recovery discovery**       | NO START            | Read-only             | 2 byte-exact bitmap aliases found                        | canonical content recovered                       | **PASS**         |
| **Runtime recovery pre-search**   | NO scientific START | Diagnostic replay     | RC=-9 / SIGKILL / no stderr                              | no marker；no forward/MCTS；cause HOLD            | **DO NOT RERUN** |

## **7.3 为什么当前仍没有 confidence-gated MCTS 科学结果**

- Attempt1 在 import 阶段退出。

- Attempt2 在 seven-input guard 之前/期间退出。

- Attempt3 仅创建 root/shadow collector 的 NO_RECORDS summaries；JSONL 为 0 bytes，search metrics/result 均不存在。

- Attempt4 是故意在 search 之前恢复原始异常的诊断 probe。

- runtime recovery replay 在 pre-search marker 之前被 SIGKILL；marker 又位于 model forward / search 之前。

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>禁止误读</strong></p>
<p>不能把“runner 被调用”“output root 创建”“checkpoint 可能加载”写成“MCTS 已执行”。当前新分支有效 root search count=0。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# **8. 运行资产恢复与当前 SIGKILL 停点**

## **8.1 绝对路径债务与资产 missing**

2026-08-30 数据盘整理将大量历史项目移动到 90_MineSim_ARCHIVE / 99_OLD_RESEARCH_HISTORY。旧 runner 仍硬编码 /root/autodl-tmp/fullmine_vector_v2_targeted_runtime，导致 semantic 和 bitmap 的 canonical 路径失效。该现象是路径迁移，不等于科学内容丢失。

## **8.2 Byte-exact recovery evidence**

<table>
<colgroup>
<col style="width: 33%" />
<col style="width: 33%" />
<col style="width: 33%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>对象</strong></th>
<th><strong>SHA256</strong></th>
<th><strong>恢复来源</strong></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td><strong>Canonical semantic SHA</strong></td>
<td>b85a3d8b28f2252ecb5bda179d514573<br />
f6333079def838cd048566f556d95cd0</td>
<td>//root/autodl-tmp<br />
/99_OLD_RESEARCH_HISTORY_20260830<br />
/fullmine_vector_v2_targeted_runtime/maps<br />
/semantic_map<br />
/geojson_full_mine_vector_v2_dev_semantic_map.json</td>
</tr>
<tr class="even">
<td><strong>Canonical bitmap SHA</strong></td>
<td>51abcd5a86e5c510204a5dacc8736915<br />
06d721f98982ab7f98585d4e0f7efdd0</td>
<td>//root/autodl-tmp/90_MineSim_ARCHIVE<br />
/06_dr_and_bundles<br />
/fullmine_vector_v4_final_dr_20260814/map<br />
/bitmap_v4.png</td>
</tr>
<tr class="odd">
<td><strong>Second bitmap alias</strong></td>
<td>51abcd5a86e5c510204a5dacc8736915<br />
06d721f98982ab7f98585d4e0f7efdd0</td>
<td>//root/autodl-tmp<br />
/99_OLD_RESEARCH_HISTORY_20260830<br />
/fullmine_vector_v4_d_current_planner_patch_candidate<br />
/bitmap<br />
/geojson_full_mine_vector_v2_dev_only_mask.png</td>
</tr>
</tbody>
</table>

## **8.3 New recovery namespace**

<table>
<colgroup>
<col style="width: 50%" />
<col style="width: 50%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>字段</strong></th>
<th><strong>值</strong></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td><strong>Recovery root</strong></td>
<td>//root/autodl-tmp<br />
/paper1_value_v3_development_only_v1<br />
/paper1_value_v3_confidence_gated_root_order_v1<br />
/recovered_canonical_runtime_assets_v1</td>
</tr>
<tr class="even">
<td><strong>Recovered bitmap</strong></td>
<td>//root/autodl-tmp<br />
/paper1_value_v3_development_only_v1<br />
/paper1_value_v3_confidence_gated_root_order_v1<br />
/recovered_canonical_runtime_assets_v1/maps<br />
/bitmap<br />
/geojson_full_mine_vector_v2_dev_bitmap_mask.png</td>
</tr>
<tr class="odd">
<td><strong>Recovered semantic</strong></td>
<td>//root/autodl-tmp<br />
/paper1_value_v3_development_only_v1<br />
/paper1_value_v3_confidence_gated_root_order_v1<br />
/recovered_canonical_runtime_assets_v1/maps<br />
/semantic_map<br />
/geojson_full_mine_vector_v2_dev_semantic_map.json</td>
</tr>
<tr class="even">
<td><strong>Recovered bitmap SHA</strong></td>
<td>51abcd5a86e5c510204a5dacc8736915<br />
06d721f98982ab7f98585d4e0f7efdd0</td>
</tr>
<tr class="odd">
<td><strong>Recovered semantic SHA</strong></td>
<td>b85a3d8b28f2252ecb5bda179d514573<br />
f6333079def838cd048566f556d95cd0</td>
</tr>
<tr class="even">
<td><strong>Old archive mutation</strong></td>
<td>False</td>
</tr>
<tr class="odd">
<td><strong>Scientific input content changed</strong></td>
<td>False</td>
</tr>
</tbody>
</table>

## **8.4 Current recovery pre-search result**

<table>
<colgroup>
<col style="width: 50%" />
<col style="width: 50%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>字段</strong></th>
<th><strong>当前值</strong></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td><strong>Recovery runner SHA</strong></td>
<td>1f89e447a41e573866627611a0f0a432<br />
673005bd4be3c0708013420b21ddf5c4</td>
</tr>
<tr class="even">
<td><strong>Probe line order</strong></td>
<td><strong>PASS：presearch point &lt; BENCHMARK_SEARCH_DIAGNOSTICS init &lt; search.search</strong></td>
</tr>
<tr class="odd">
<td><strong>PRESEARCH_REPLAY_RC</strong></td>
<td>-9</td>
</tr>
<tr class="even">
<td><strong>PRESEARCH_POINT_REACHED</strong></td>
<td>False</td>
</tr>
<tr class="odd">
<td><strong>ORIGINAL_EXCEPTION_SURFACED</strong></td>
<td>False</td>
</tr>
<tr class="even">
<td><strong>stderr</strong></td>
<td>empty</td>
</tr>
<tr class="odd">
<td><strong>Status</strong></td>
<td><strong>FAIL_UNEXPECTED_OUTCOME / Technical HOLD</strong></td>
</tr>
<tr class="even">
<td><strong>Checkpoint load status</strong></td>
<td><strong>HOLD：code path expected load before probe, but SIGKILL timing not independently captured</strong></td>
</tr>
<tr class="odd">
<td><strong>Model forward</strong></td>
<td>False by control-flow boundary</td>
</tr>
<tr class="even">
<td><strong>MCTS search</strong></td>
<td>False by control-flow boundary</td>
</tr>
<tr class="odd">
<td><strong>Attempt5</strong></td>
<td><strong>NOT CREATED</strong></td>
</tr>
</tbody>
</table>

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>当前唯一 blocker</strong></p>
<p>解释 RC=-9。OOM 是合理假设，但目前没有 memory.events / kernel OOM / cgroup 证据，因此必须保持 CAUSE=HOLD。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## **8.5 用户明确停点**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>PAUSED BY USER</strong></p>
<p>用户明确要求：SIGKILL diagnosis 先不做，项目推进停在此处。下一位 AI 不得自动执行 pending diagnosis、不得重跑 recovery replay、不得创建 Attempt5。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# **9. 本轮重要失败复盘**

*以下均按“现象 → 原因 → 排查 → 处理 → 证据 → 禁止重复”记录。大部分是 Technical failure，不是 confidence-gated 机制的 Scientific FAIL。*

## **CG-E01 Attempt1 import failure**

| **项目**                | **内容**                                                                                   |
|-------------------------|--------------------------------------------------------------------------------------------|
| **现象**                | 新 runner 启动即 ModuleNotFoundError；output root 不存在。                                 |
| **原因 / 当前解释**     | PYTHONPATH 只含 repo + new src，未包含 FIX6R3 sibling modules。                            |
| **排查过程**            | 读取 stderr；静态扫描 paper1\_\* imports；证明失败在 import、0 checkpoint/forward/search。 |
| **最终处理 / 当前状态** | 新 Attempt2 namespace 仅增加 FIX6R3 src 到 PYTHONPATH。                                    |
| **证据**                | Attempt1 capture=083715…；diagnosis=f278be…；no rerun。                                    |
| **以后禁止重复**        | 禁止把“本地模块能被 AST 发现”当作运行时 PYTHONPATH 已绑定。                                |

## **CG-E02 Attempt2 semantic missing**

| **项目**                | **内容**                                                                                |
|-------------------------|-----------------------------------------------------------------------------------------|
| **现象**                | runner 在 seven-input guard 抛 missing_input canonical semantic。                       |
| **原因 / 当前解释**     | 数据盘整理后原 absolute root 不存在；runner 仍硬编码旧路径。                            |
| **排查过程**            | 读取 guard/source；确认 output=absent、0 checkpoint/forward/search；搜索同名 semantic。 |
| **最终处理 / 当前状态** | 发现 3 个内容完全相同的 semantic 候选，进入新 Attempt3 prestart。                       |
| **证据**                | Attempt2 diagnosis=316d85…；candidate SHA=b85a…d95cd0。                                 |
| **以后禁止重复**        | 禁止把 path missing 写成 file deleted；先做 SHA/equivalence。                           |

## **CG-E03 Attempt3 V1 false PASS**

| **项目**                | **内容**                                                                                                    |
|-------------------------|-------------------------------------------------------------------------------------------------------------|
| **现象**                | Python AssertionError 后 audit/auth/wrapper 均不存在，但 shell 最后打印 PASS；manifest SHA 是空文件 e3b0…。 |
| **原因 / 当前解释**     | bash controller 未 fail-closed；子步骤失败后仍执行尾部 PASS。                                               |
| **排查过程**            | partial artifact audit；确认 START=0、auth/wrapper absent、evidence dir empty。                             |
| **最终处理 / 当前状态** | 撤回 PASS；新增 recovery source audit；后续 controller 强制 fail-closed。                                   |
| **证据**                | False-pass recovery audit SHA=222972…；空 manifest 仅作为历史 debris。                                      |
| **以后禁止重复**        | 禁止仅凭最后一行 PASS；必须检查前序 traceback、产物、manifest 是否非空。                                    |

## **CG-E04 Attempt3 NameError masking**

| **项目**                | **内容**                                                                                                     |
|-------------------------|--------------------------------------------------------------------------------------------------------------|
| **现象**                | postprocessing 报 BENCHMARK_SEARCH_DIAGNOSTICS undefined；只有 4 个 NO_RECORDS/空 JSONL。                    |
| **原因 / 当前解释**     | 该变量在 try 内初始化；simulation.initialize 之前/期间的异常被 except 吞掉，后处理再触发二次 NameError。     |
| **排查过程**            | 三份 runner AST 对比；确认 init 未丢失；control-flow audit 定位 scorer outside try、init/search inside try。 |
| **最终处理 / 当前状态** | 建立 Attempt4 diagnostic-only probe，在 except 中 re-raise 原始异常，并在 search 前截止。                    |
| **证据**                | Attempt3 capture=e41f…；diagnosis=f223…；source audit=746266…；fast audit=e884…。                            |
| **以后禁止重复**        | 禁止直接在全局补 \[\] 掩盖原始异常；必须恢复第一个 fault。                                                   |

## **CG-E05 Slow AST audit**

| **项目**                | **内容**                                                     |
|-------------------------|--------------------------------------------------------------|
| **现象**                | 只读 control-flow audit 长时间不结束，被 Ctrl+C。            |
| **原因 / 当前解释**     | 对大量 AST 节点反复 ast.get_source_segment，复杂度过高。     |
| **排查过程**            | KeyboardInterrupt 栈明确停在 ast.py get_source_segment。     |
| **最终处理 / 当前状态** | 改为快速版，只定位 scorer/init/search/try/handler 几个节点。 |
| **证据**                | Fast audit 秒级完成；SHA=e884…；旧慢 audit 无 mutation。     |
| **以后禁止重复**        | 禁止为局部控制流问题全量格式化 AST；先做定点节点分析。       |

## **CG-E06 Attempt4 bitmap missing**

| **项目**                | **内容**                                                                    |
|-------------------------|-----------------------------------------------------------------------------|
| **现象**                | simulation.initialize → bitmap loader 抛 FileNotFoundError。                |
| **原因 / 当前解释**     | semantic 虽恢复，但 archived runtime root 下缺 canonical bitmap。           |
| **排查过程**            | Attempt4 probe 成功恢复原始 traceback，证明在 model forward/search 前失败。 |
| **最终处理 / 当前状态** | 只读 exact-name discovery；随后扩大到 alias + SHA + generator provenance。  |
| **证据**                | Attempt4 capture=47304…；bitmap canonical SHA=51abcd…f7efdd0。              |
| **以后禁止重复**        | 禁止只恢复一个输入后直接 scientific run；Map runtime 依赖必须成套审计。     |

## **CG-E07 Exact-name search false negative**

| **项目**                | **内容**                                                                    |
|-------------------------|-----------------------------------------------------------------------------|
| **现象**                | 同名 bitmap candidate=0，初看像 frozen input lost。                         |
| **原因 / 当前解释**     | 真实副本被归档且改名；exact basename 搜索不足。                             |
| **排查过程**            | 扩大到 /root、/mnt、90/99 archive 的 likely PNG aliases，并逐个算 SHA。     |
| **最终处理 / 当前状态** | 找到 2 个 byte-exact alias，不需要重建。                                    |
| **证据**                | Recovery discovery SHA=3d0af…；两份 SHA 均 51abcd…。                        |
| **以后禁止重复**        | 禁止把“同名文件=0”解释为内容丢失；对二进制资产必须做 hash alias discovery。 |

## **CG-E08 Recovery pre-search SIGKILL**

| **项目**                | **内容**                                                                                       |
|-------------------------|------------------------------------------------------------------------------------------------|
| **现象**                | byte-exact recovery PASS 后，pre-search replay RC=-9、无 stderr、无 marker。                   |
| **原因 / 当前解释**     | 当前原因未知；可能是 OOM/cgroup/host kill，但尚无证据。                                        |
| **排查过程**            | 已准备只读 SIGKILL diagnosis，计划检查 memory.events、meminfo、kernel log、bitmap dimensions。 |
| **最终处理 / 当前状态** | 按用户指令停点；不运行 diagnosis、不创建 Attempt5。                                            |
| **证据**                | Recovery runner=1f89…；PRESEARCH_REPLAY_RC=-9；Attempt5=False。                                |
| **以后禁止重复**        | 禁止自动写 OOM；禁止在资源原因未证明前重跑或升级到 scientific Attempt5。                       |

# **10. 关键路径、SHA 与状态矩阵**

## **10.1 当前关键路径**

<table>
<colgroup>
<col style="width: 33%" />
<col style="width: 33%" />
<col style="width: 33%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>对象</strong></th>
<th><strong>路径</strong></th>
<th><strong>状态 / 作用</strong></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td><strong>正式 repo</strong></td>
<td>/root/MineSim-Dynamic</td>
<td>Git tracked source</td>
</tr>
<tr class="even">
<td><strong>主 evidence root</strong></td>
<td>//root/autodl-tmp<br />
/paper1_value_v3_development_only_v1</td>
<td>Value V3 + integration</td>
</tr>
<tr class="odd">
<td><strong>旧 root-order baseline</strong></td>
<td>...<br />
/value_guided_mcts_c01_secondary_b8_guided_binding_fix6r3_v1</td>
<td><strong>FROZEN</strong></td>
</tr>
<tr class="even">
<td><strong>Offline diagnosis</strong></td>
<td>...<br />
/paper1_value_v3_offline_mechanism_diagnosis_v1</td>
<td><strong>FROZEN</strong></td>
</tr>
<tr class="odd">
<td><strong>Confidence-gated current</strong></td>
<td>...<br />
/paper1_value_v3_confidence_gated_root_order_v1</td>
<td><strong>CURRENT</strong></td>
</tr>
<tr class="even">
<td><strong>Recovered assets</strong></td>
<td>...<br />
/paper1_value_v3_confidence_gated_root_order_v1<br />
/recovered_canonical_runtime_assets_v1</td>
<td><strong>CURRENT / preserve</strong></td>
</tr>
<tr class="odd">
<td><strong>Recovery runner</strong></td>
<td>.../src<br />
/paper1_value_confidence_gated_runtime_recovery_presearch_probe_v1.py</td>
<td>SHA 1f89…</td>
</tr>
<tr class="even">
<td><strong>Recovery probe result</strong></td>
<td>...<br />
/RUNTIME_RECOVERY_PRESEARCH_PROBE_RESULT_V1.json</td>
<td><strong>RC=-9；SHA HOLD</strong></td>
</tr>
<tr class="odd">
<td><strong>Pending SIGKILL diagnosis</strong></td>
<td>//root/autodl-tmp<br />
/C01_VALUE_V3_CONFIDENCE_GATED_RUNTIME_RECOVERY_PRESEARCH_SIGKILL_DIAGNOSIS_V1.py</td>
<td><strong>AutoDL existence HOLD；not executed</strong></td>
</tr>
</tbody>
</table>

## **10.2 核心 frozen SHA**

<table>
<colgroup>
<col style="width: 33%" />
<col style="width: 33%" />
<col style="width: 33%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>对象</strong></th>
<th><strong>SHA256</strong></th>
<th><strong>状态</strong></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td><strong>Git HEAD</strong></td>
<td>112d2bd0f3412fc83b13d5587d2b4140<br />
2d2d0f5e</td>
<td><strong>FROZEN</strong></td>
</tr>
<tr class="even">
<td><strong>FIX6R3 runner</strong></td>
<td>ea4d7f21265be0b2409cc2b25e6f1bd2<br />
c7ad49317d593929a34752d286d5eb79</td>
<td><strong>FROZEN</strong></td>
</tr>
<tr class="odd">
<td><strong>Root-order source</strong></td>
<td>71163cf56cc30beaceb14d99487375f9<br />
c705bfc7bfc581636c55fae91984a49a</td>
<td><strong>FROZEN</strong></td>
</tr>
<tr class="even">
<td><strong>Online feature source</strong></td>
<td>f75b1c09854d2645a3e4d47a6381e335<br />
78b74c1a8f9fc95e35a8db22b474f6b1</td>
<td><strong>FROZEN</strong></td>
</tr>
<tr class="odd">
<td><strong>Root scorer source</strong></td>
<td>7ffea187ec9e55bdd72f796a376826d6<br />
b3656380ac53a88c6d3416d023db5709</td>
<td><strong>FROZEN</strong></td>
</tr>
<tr class="even">
<td><strong>Checkpoint 20260824</strong></td>
<td>496e4259eb9801f3ce70c1094be12fd0<br />
985cb03e97d606cade8dfbe9d5228633</td>
<td><strong>FROZEN</strong></td>
</tr>
<tr class="odd">
<td><strong>Checkpoint 20260825</strong></td>
<td>5df90947a5fdd2bc6aa525ca5eba78b6<br />
379e127e5df6ca1d0362c992caab73b5</td>
<td><strong>FROZEN</strong></td>
</tr>
<tr class="even">
<td><strong>Checkpoint 20260826</strong></td>
<td>3881d39c09b02a513e44f0fe612aad42<br />
de9ff636fd07e314d327b4c6d5f132df</td>
<td><strong>FROZEN</strong></td>
</tr>
<tr class="odd">
<td><strong>B64 final decision V2</strong></td>
<td>71eeda99345740bc06e58518620e15bc<br />
99f0f7eb87a6fb70ee7d52516bd89fca</td>
<td><strong>FROZEN</strong></td>
</tr>
<tr class="even">
<td><strong>One-root result</strong></td>
<td>22e60af91e2c19c271e68e68bdbfe56b<br />
b7c44fafb50666c504d4c5bf5b3579b3</td>
<td><strong>FROZEN</strong></td>
</tr>
<tr class="odd">
<td><strong>One-root freeze</strong></td>
<td>8d3df668b327711fbee00963674051d8<br />
32fc4ab607caefb2865884375f2baa98</td>
<td><strong>FROZEN</strong></td>
</tr>
<tr class="even">
<td><strong>Full36 rows</strong></td>
<td>674a59b15fb6883369d93aec8aba375c<br />
2df3c0256496f93f04a34e5fd9e15e09</td>
<td><strong>FROZEN</strong></td>
</tr>
<tr class="odd">
<td><strong>Full36 result</strong></td>
<td>b4d68184245107e451b78e22eebeb249<br />
a03001b6f8f89981974f6892d629b0c2</td>
<td><strong>FROZEN</strong></td>
</tr>
<tr class="even">
<td><strong>Full36 freeze</strong></td>
<td>22965ce70e88fee2f00242f9bf0aa415<br />
667ddcd4a5d0e700d9b6267f55b081ec</td>
<td><strong>FROZEN</strong></td>
</tr>
<tr class="odd">
<td><strong>Association result</strong></td>
<td>518a167a6f6ff80ce58c57e38934ef35<br />
4b9a6de18eb553ae5045d3525cfc16e6</td>
<td><strong>FROZEN</strong></td>
</tr>
<tr class="even">
<td><strong>Threshold contract</strong></td>
<td>7ec878383e3fb134c999f22e277fe91f<br />
01f8f9a6c1bce2ece79b13fbf78cbcec</td>
<td><strong>FROZEN</strong></td>
</tr>
<tr class="odd">
<td><strong>Confidence controller</strong></td>
<td>0ed2d1ff33a66198bf59b25e1117274d<br />
dc61440bf52dec1052d4aa553a52a2f9</td>
<td><strong>FROZEN</strong></td>
</tr>
<tr class="even">
<td><strong>Confidence runner</strong></td>
<td>64ad4300b01bd4fee5ed7c6a33375346<br />
c08f84beac0156aa6febf413c8e81386</td>
<td><strong>FROZEN BUILD</strong></td>
</tr>
<tr class="odd">
<td><strong>Confidence CellSpec</strong></td>
<td>b87d09bd3c63066f99414c405751c0d6<br />
bd59497f602983ee201340b6c97f68ae</td>
<td><strong>FROZEN PRESTART</strong></td>
</tr>
<tr class="even">
<td><strong>Attempt3 derived runner</strong></td>
<td>84c6d8bda982903343f00633d99866a8<br />
d667715c69102803d53d49b3150cbf81</td>
<td>NO RERUN</td>
</tr>
<tr class="odd">
<td><strong>Attempt4 probe runner</strong></td>
<td>04082477925f205b1cfea8d59a1fcd51<br />
bb39980db75f093392ea8ae7d1c21b0a</td>
<td>NO RERUN</td>
</tr>
<tr class="even">
<td><strong>Recovery discovery</strong></td>
<td>3d0af90f25038871c30010dcfb5e5484<br />
ecf76ff897ba94b1b5608d28de2f0e2c</td>
<td><strong>PASS</strong></td>
</tr>
<tr class="odd">
<td><strong>Recovery runner</strong></td>
<td>1f89e447a41e573866627611a0f0a432<br />
673005bd4be3c0708013420b21ddf5c4</td>
<td><strong>CURRENT HOLD</strong></td>
</tr>
<tr class="even">
<td><strong>Canonical bitmap</strong></td>
<td>51abcd5a86e5c510204a5dacc8736915<br />
06d721f98982ab7f98585d4e0f7efdd0</td>
<td>BYTE-EXACT</td>
</tr>
<tr class="odd">
<td><strong>Canonical semantic</strong></td>
<td>b85a3d8b28f2252ecb5bda179d514573<br />
f6333079def838cd048566f556d95cd0</td>
<td>BYTE-EXACT</td>
</tr>
</tbody>
</table>

## **10.3 当前 pending attachment**

<table>
<colgroup>
<col style="width: 50%" />
<col style="width: 50%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>字段</strong></th>
<th><strong>值</strong></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td><strong>文件</strong></td>
<td>C01_VALUE_V3_CONFIDENCE_GATED_RUNTIME_RECOVERY_PRESEARCH_SIGKILL_DIAGNOSIS_V1.py</td>
</tr>
<tr class="even">
<td><strong>ChatGPT /mnt/data SHA</strong></td>
<td>62f4e9fcb45dcaa59b5bddc21240ccdf<br />
4bf42402168bf38ec1b74051301a2659</td>
</tr>
<tr class="odd">
<td><strong>AutoDL existence</strong></td>
<td><strong>HOLD / 未验证</strong></td>
</tr>
<tr class="even">
<td><strong>Execution</strong></td>
<td><strong>NOT EXECUTED（用户明确暂缓）</strong></td>
</tr>
<tr class="odd">
<td><strong>Scope</strong></td>
<td>read-only cgroup/meminfo/dmesg/bitmap-header diagnosis；no checkpoint/forward/MCTS</td>
</tr>
</tbody>
</table>

# **11. 资源、协作、文件与 Git 工作流**

## **11.1 固定执行环境**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>cd /root/MineSim-Dynamic<br />
source /root/miniconda3/etc/profile.d/conda.sh 2&gt;/dev/null || true<br />
conda activate minesim<br />
<br />
export PYTHONPATH=/root/MineSim-Dynamic<br />
export PYTHONDONTWRITEBYTECODE=1<br />
# 是否禁用 GPU 按当前 Gate 判断<br />
export CUDA_VISIBLE_DEVICES=""<br />
export OMP_NUM_THREADS=1</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## **11.2 当前与后续资源判断**

| **时点**              | **资源**          | **说明**                                         |
|-----------------------|-------------------|--------------------------------------------------|
| **现在**              | PAUSED            | 不执行任务。                                     |
| **恢复后的下一 Gate** | LOW / CPU-only    | SIGKILL diagnosis；不需要 GPU。                  |
| **条件性后续**        | HIGH-CPU / 大内存 | 仅在 OOM 证据支持且新 presearch probe 获授权后。 |
| **HIGH-GPU**          | **NOT NEEDED**    | 当前不训练、不做大规模 CUDA forward。            |

## **11.3 ChatGPT—用户—Codex 分工**

| **角色**    | **职责**                                                                        |
|-------------|---------------------------------------------------------------------------------|
| **ChatGPT** | 读取证据、判断唯一 Gate、生成最小脚本、定义 PASS/FAIL、分析结果、制作 handoff。 |
| **用户**    | AutoDL 实际执行、控制实例、上传真实输出、授权删除/重大修改/受限重跑。           |
| **Codex**   | 仅复杂算法/顽固 Bug/多文件调用链/独立复核；默认 Luna medium，必要时 Terra/Sol。 |

## **11.4 成熟运行规则**

- 一次只推进一个最小 Gate；已验证阶段不重复。

- 能用 Shell/Python 免费完成的 SHA、JSON、AST、inventory 不用模型。

- 长仿真用 terminal/screen、独立 log、RC、START、CAPTURE；但 screen 不是所有短任务的硬要求。

- 正式 one-time：prereg → exact input SHA → namespace absent → auth → START → one process → CAPTURE/freeze。

- START 后无自动 retry；Scientific FAIL 原样保留。

- 禁止 git reset --hard、git clean -fd、git add .，除非用户明确授权。

- 大文件、日志、result 放 /root/autodl-tmp；正式 repo 只保留必要源码。

- 交互顶层禁止裸 exit；失败脚本必须 fail-closed，不能前面报错最后打印 PASS。

# **12. DO_NOT_REPEAT / HOLD / 不可回退项**

## **12.1 最高优先级禁止事项**

- 禁止重跑 2356-root training、三个 final model、C01 one-time forward。

- 禁止重跑 Pure B8 及任何 B8/B16/B32/B64 root-order-only cell。

- 禁止重跑 offline one-root/full36 diagnosis；只读聚合已完成。

- 禁止重跑 confidence-gated Attempt1、Attempt2、Attempt3 V2、Attempt4 probe。

- 禁止再次执行 runtime recovery + presearch validation V1；recovery namespace 已创建，当前结果 RC=-9。

- 禁止创建 Attempt5，直到 SIGKILL cause 被证据化且新的 presearch validation 获明确授权。

- 禁止删除或覆盖 recovered assets、current logs、START/CAPTURE、empty/NO_RECORDS diagnostics。

- 禁止把 RC=-9 写成 OOM，禁止把 output root existence 写成 MCTS executed。

- 禁止修改旧 root-order-only final decision 或以新机制覆盖其 negative baseline。

- 禁止为了消除 codex-env.sh 登录告警随意恢复未知脚本；该告警与 MineSim 科学结果分离。

## **12.2 当前 HOLD / NOT PROVEN**

| **对象**                                  | **状态**           | **解除条件 / 说明**                                    |
|-------------------------------------------|--------------------|--------------------------------------------------------|
| **SIGKILL(-9) cause**                     | **HOLD**           | 执行只读 resource diagnosis。                          |
| **OOM**                                   | **NOT PROVEN**     | 需要 cgroup/kernel/memory evidence。                   |
| **Recovery replay checkpoint load**       | **HOLD**           | process 被 kill，未做独立 marker capture。             |
| **Confidence-gated safe smoke**           | **NOT PASSED**     | 尚无非零 search metrics/result。                       |
| **Attempt5**                              | **NOT CREATED**    | 必须先完成 resource diagnosis + presearch validation。 |
| **27-cell matrix**                        | **NOT AUTHORIZED** | technical smoke 通过后才可按 CellSpec 推进。           |
| **Confidence-gated stability/efficiency** | **NOT EVALUATED**  | 无科学 cells。                                         |
| **Production readiness/safety**           | **NOT PROVEN**     | Research/DEV branch；无生产级地图/验证。               |
| **AutoDL 当前 handoff Word**              | **HOLD**           | 本文件在 ChatGPT / sandbox 生成；尚未上传 AutoDL。     |

# **13. 云端文档、归档、删除与恢复边界**

## **13.1 Handoff 历史**

| **文档**                                   | **定位**                | **说明**                                                                     |
|--------------------------------------------|-------------------------|------------------------------------------------------------------------------|
| **2026-08-24 全项目 handoff**              | HISTORICAL              | MineSim→Fleet/FullMine provenance；Complete ZIP central directory 曾不完整。 |
| **2026-08-25 Value V3 2356-root handoff**  | **HISTORICAL / FROZEN** | training/data/model provenance。                                             |
| **2026-08-26 C01 metric/checker handoffs** | HISTORICAL              | C01 forward/static checker 阶段 provenance。                                 |
| **2026-08-27 Guided B8 1/9**               | HISTORICAL              | 早期 integration progress。                                                  |
| **2026-08-29 B8 4/9 / B16 2/9**            | HISTORICAL              | 矩阵推进和错误复盘。                                                         |
| **2026-08-30 ValueGuidedMCTS 闭环终版**    | **FROZEN BASELINE**     | naive root-order-only 36-cell 与 cleanup 权威终版。                          |
| **本文件**                                 | **CURRENT**             | offline mechanism + confidence-gated technical chain + RC=-9 stop。          |

## **13.2 数据盘整理与当前路径债务**

- 顶层 746→23；78 ZIP、9 smoke/preflight、50 C04/C06/C11、69 old paper1、431 loose files、83 historical research、7 independent envs 已分类归档。

- 唯一直接删除项是 \_\_pycache\_\_；其他动作是 move/isolate/archive/quarantine，不能写“科研文件已删除”。

- 当前 semantic/bitmap path missing 正是绝对路径在 archive 后失效的实例；内容通过 SHA alias discovery 得以恢复。

- 恢复应单文件/新 namespace，不应整目录回滚到顶层，也不应修改 archive 原件。

## **13.3 ChatGPT / Library 与 AutoDL 区分**

| **位置**                         | **准确边界**                                                                |
|----------------------------------|-----------------------------------------------------------------------------|
| **ChatGPT Conversation/Library** | 存在本轮日志粘贴、历史 handoff、当前生成脚本与本 Word。                     |
| **AutoDL**                       | 存在已执行脚本、evidence、recovered runtime root；本 Word 是否上传为 HOLD。 |
| **Pending SIGKILL script**       | ChatGPT attachment 可用；AutoDL existence 未验证。                          |
| **No such file**                 | 仅证明路径当前不可访问，不证明 actual delete。                              |

# **14. 快速接手区（下一位 AI 必须先读）**

| **接手问题**                | **准确答案**                                                                                                         |
|-----------------------------|----------------------------------------------------------------------------------------------------------------------|
| **1. 项目现在做到哪里？**   | root-order-only 分支 COMPLETE/FROZEN；offline diagnosis COMPLETE/FROZEN；confidence gate technical pre-search HOLD。 |
| **2. 哪些阶段无需重做？**   | MineSim/Pure/Fleet/FullMine/Value V3、B8–B64、one-root/full36 association、threshold/controller build。              |
| **3. 当前唯一 blocker？**   | recovery pre-search replay RC=-9；SIGKILL cause 未证明。                                                             |
| **4. 正式 repo？**          | /root/MineSim-Dynamic                                                                                                |
| **5. 当前 evidence root？** | /root/autodl-tmp/paper1_value_v3_development_only_v1/paper1_value_v3_confidence_gated_root_order_v1                  |
| **6. Git HEAD？**           | 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e                                                                             |
| **7. 必核 SHA？**           | recovery runner 1f89…；bitmap 51abcd…；semantic b85a…；threshold 7ec878…；controller 0ed2…。                         |
| **8. 哪些路径不能动？**     | 所有 old final decisions、offline diagnosis、Attempt1–4 evidence、recovered_canonical_runtime_assets_v1。            |
| **9. 哪些实验禁止重跑？**   | 所有已 START/FROZEN；尤其 Attempts1–4 和 recovery presearch replay。                                                 |
| **10. 哪些对象 HOLD？**     | SIGKILL cause、Attempt5、27-cell matrix、confidence-gated scientific claims。                                        |
| **11. 下一步最小行动？**    | 仅在用户继续时，LOW 只读运行 SIGKILL resource diagnosis。                                                            |
| **12. 本步 PASS 标准？**    | 证据化分类 OOM_SUPPORTED 或 CAUSE_NOT_PROVEN；Attempt5 仍 absent；no forward/MCTS。                                  |
| **13. 当前资源？**          | PAUSED；下一步 LOW / CPU-only；不需要 GPU。                                                                          |
| **14. 开工前 preflight？**  | Git/sha/process/diagnosis output absence/recovery artifact readback/Attempt5 absence。                               |
| **15. FAIL 后停哪里？**     | 保存 memory/cgroup/kernel evidence；HOLD；不重跑 recovery，不建 Attempt5。                                           |

## **14.1 推荐接手顺序**

1.  先确认用户在本 handoff 后没有继续执行 SIGKILL diagnosis 或新 probe；若有，新终端证据优先。

2.  只读核验 current recovery root、runner/result/log、Attempt5 absence 与相关进程。

3.  确认 pending diagnosis script 已上传 AutoDL 且 SHA 与 ChatGPT attachment 一致。

4.  经用户同意后运行一次只读 diagnosis；不要启动 high-memory probe 或 MCTS。

5.  依据 diagnosis 再决定：资源性新 probe、进一步证据收集，或继续 HOLD。

# **附录 A｜本轮关键时间线**

| **序号** | **阶段**                   | **结果**                                                                  |
|----------|----------------------------|---------------------------------------------------------------------------|
| **1**    | Root-order-only closed     | B64 9/9；Pure B8 vs Guided B64 系统负收益冻结。                           |
| **2**    | One-root offline pilot     | 1 forward；16 scores/ranking/margin PASS。                                |
| **3**    | Full36 offline diagnosis   | 36 cells / 12142 roots / 3 checkpoint loads / 12142 forwards。            |
| **4**    | Association                | 6 FAIL vs 30 PASS；27216 exact permutations；4 metrics Holm significant。 |
| **5**    | Threshold/controller build | margin threshold=0.0676783919；controller/runner/CellSpec frozen。        |
| **6**    | Attempt1                   | import failure；no runtime. No rerun。                                    |
| **7**    | Attempt2                   | semantic absolute path missing；no checkpoint/search。                    |
| **8**    | Attempt3 V1 prestart       | false PASS controller bug；no auth/start。                                |
| **9**    | Attempt3 V2                | NameError masked earlier exception；0 search records。                    |
| **10**   | Attempt4 probe             | 恢复 bitmap FileNotFoundError；no forward/search。                        |
| **11**   | Bitmap discovery           | exact-name 0；wide alias search found 2 byte-exact copies。               |
| **12**   | Runtime recovery           | new byte-exact runtime root created。                                     |
| **13**   | Recovery presearch         | RC=-9 SIGKILL；no marker；cause HOLD。                                    |
| **14**   | User stop                  | SIGKILL diagnosis deferred；Attempt5 not created。                        |

# **附录 B｜下一 Gate 的最小 PASS / FAIL 标准**

## **B.1 当前 pending Gate**

| **字段**                 | **要求**                                                                              |
|--------------------------|---------------------------------------------------------------------------------------|
| **Gate**                 | RUNTIME_RECOVERY_PRESEARCH_SIGKILL_DIAGNOSIS                                          |
| **Resource**             | LOW / CPU-only                                                                        |
| **Input**                | recovery probe result/stdout/stderr/output root + recovered bitmap                    |
| **Read-only checks**     | cgroup memory.current/peak/max/events；/proc/meminfo；dmesg/journal OOM；PNG header。 |
| **Mutation**             | 仅新 diagnosis JSON/TXT；不得修改 recovery assets。                                   |
| **Scientific execution** | None                                                                                  |
| **Attempt5**             | must remain absent                                                                    |

## **B.2 PASS 标准**

- 绑定当前 recovery result 和 bitmap SHA，确认 runner_rc=-9。

- 输出 memory/cgroup/kernel evidence，并给出 TECHNICAL_RESOURCE_FAILURE_SIGKILL_OOM_SUPPORTED 或 TECHNICAL_SIGKILL_CAUSE_NOT_YET_PROVEN。

- 本诊断不加载 checkpoint、不 forward、不 MCTS；Attempt5 不创建。

- 若 OOM_SUPPORTED，只允许下一步设计新 high-memory presearch authorization，不能直接科学执行。

## **B.3 FAIL / HOLD 标准**

- evidence 文件或 SHA 不匹配；停止，不猜。

- cgroup/kernel 权限不足且无法证明原因；分类 CAUSE_NOT_PROVEN。

- 发现 unexpected process/output/Attempt5 artifact；保存 inventory 并停止。

- 任何情况下都不重跑 recovery presearch V1。

# **附录 C｜论文与科学表述边界**

| **Claim**                                                  | **状态**                             | **证据边界**                                     |
|------------------------------------------------------------|--------------------------------------|--------------------------------------------------|
| **Value V3 learns action-ranking signal**                  | SUPPORTED                            | C01 independent regret PASS。                    |
| **Naive root-order-only improves system efficiency**       | **REJECTED**                         | Guided stable at B64；cost worse than Pure B8。  |
| **Low confidence/disagreement associates with fail cells** | SUPPORTED AS EXPLORATORY ASSOCIATION | 36-cell exact stratified analysis。              |
| **Confidence gating improves closed-loop MCTS**            | **NOT EVALUATED**                    | No valid confidence-gated search/result。        |
| **Current RC=-9 is OOM**                                   | **NOT PROVEN**                       | Resource diagnosis not run。                     |
| **Canonical map assets were scientifically lost**          | **REJECTED**                         | byte-exact semantic/bitmap copies recovered。    |
| **Current branch production-ready**                        | **NOT SUPPORTED**                    | Technical smoke incomplete；Research/DEV scope。 |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>最终交接一句话</strong></p>
<p>Value V3 的模型级排序能力与 naive root-order-only 的系统负结果均已冻结；offline evidence 支持 confidence gate，但新分支尚无有效 MCTS 结果。canonical map assets 已 byte-exact 恢复，当前唯一停点是 recovery pre-search RC=-9 的未诊断 SIGKILL；用户要求暂不继续，Attempt5 不存在。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>
