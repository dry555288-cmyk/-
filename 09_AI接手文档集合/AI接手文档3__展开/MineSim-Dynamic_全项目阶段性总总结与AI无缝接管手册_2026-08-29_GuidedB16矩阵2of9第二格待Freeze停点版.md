**MineSim-Dynamic**

**全项目阶段性总总结与 AI 无缝接管手册**

**2026-08-29 · Guided B16 矩阵 2 / 9 技术有效**

**1 / 9 已冻结；第 2 格已执行并发布证据，待 immutable freeze 停点版**

**重点专题：B8 9/9 封口、B16 两格真实结果、OMP 环境绑定与下一最小 Gate**

| **当前真实状态** Value V3 独立 C01 泛化已冻结 PASS；Guided B8 9/9 已冻结但 B8 不稳定；Guided B16 第 1 格已冻结 Scientific FAIL，第 2 格已完成 Technical PASS + Scientific PASS，output/evidence manifests 均复核 PASS，但尚未 postexec freeze。下一步只允许 LOW 冻结第 2 格，禁止直接授权第 3 格。 |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

**交接版本：V1 \| 适用对象：后续 ChatGPT / Codex / 工程执行人员**

正式 repo：/root/MineSim-Dynamic

主 evidence root：/root/autodl-tmp/paper1_value_v3_development_only_v1

*证据截止：截至 GUIDED_B16_RUNTIME_SEED0_MODEL_SEED20260825 START→RUN→CAPTURE 完成、FINAL_RC=0；尚未 postexec freeze。*

**任何晚于本证据截点的 AutoDL 真实输出，均自动优先于本 Word。**

# 0. CURRENT_STATE｜一页接手摘要

| **字段**                  | **当前值**                                                                               | **接管解释**                                                                              |
|---------------------------|------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------|
| **EVIDENCE_CUTOFF**       | 2026-08-29；B16 第 2 格 START→RUN→CAPTURE 已完成，FINAL_RC=0；postexec freeze 尚未创建。 | 最新终端结果优先；本 Word 不把未冻结结果伪装为 frozen。                                   |
| **CURRENT_STAGE**         | Value-guided MCTS integration efficiency evaluation · Guided B16 matrix                  | B8 已封口；当前推进 preregistered B16 9-cell matrix。                                     |
| **CURRENT_GATE**          | LOW_POSTEXEC_FREEZE_GUIDED_B16_RUNTIME_SEED0_MODEL_SEED20260825                          | 只读核验并原子发布第 2 格 immutable freeze。                                              |
| **CURRENT_STATUS**        | B16 技术有效执行 2/9；immutable frozen 1/9                                               | 第 1 格 FROZEN Scientific FAIL；第 2 格 evidence published、freeze pending。              |
| **LATEST_GIT_HEAD**       | 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e                                                 | tracked Git clean；branch 名未在最新终端证据中复核，勿新建/切换分支。                     |
| **LATEST_FROZEN_RESULT**  | GUIDED_B16_RUNTIME_SEED0_MODEL_SEED20260824                                              | Technical PASS + Scientific FAIL；freeze SHA b05f047c...；禁止重跑。                      |
| **LATEST_VALID_UNFROZEN** | GUIDED_B16_RUNTIME_SEED0_MODEL_SEED20260825                                              | Technical PASS + Scientific PASS；254 roots / 4064 expansions / 254 forwards；待 freeze。 |
| **CURRENT_ENV**           | minesim · Python 3.9.25 · CUDA_VISIBLE_DEVICES="" · OMP_NUM_THREADS=1                    | 第 2 格已显式绑定 OMP=1 且 environment warnings=\[\]。                                    |
| **CURRENT_SCIENCE**       | B16 第 1 格 FAIL、第 2 格 PASS；B16 stability 未判定                                     | 必须完成 9 个 technical-valid cells 后才能按 prereg 判 stable。                           |
| **CURRENT_BLOCKER**       | 无算法 blocker；存在未闭合的证据边界                                                     | 第 2 格未 freeze 是唯一必须先关闭的 Gate。                                                |
| **NEXT_MINIMAL_ACTION**   | LOW：核第 2 格 START/CAPTURE/result/manifests，发布 postexec PASS freeze                 | freeze 后再构建 CellSpec V3 + frozen 2-cell regression。                                  |
| **RESOURCE_REQUIRED**     | LOW only                                                                                 | 不得为 freeze 加载 checkpoint、forward 或 MCTS。                                          |
| **DO_NOT_REPEAT**         | B8 全部 9 格；B16 第 1 格；B16 第 2 格                                                   | 第 2 格 authorization 已由 START 消耗；任何重跑均违反 one-time contract。                 |
| **HOLD**                  | B16 第 3 格授权、B16 稳定性结论、secondary final claims、production claims               | 证据不足不得补齐；不得提前选择“最好 model/runtime seed”。                                 |

| **当前停点的最短描述** B8 9/9 已冻结；B16 第 1 格已冻结 Scientific FAIL，第 2 格已技术有效执行并科学 PASS，但尚未 freeze。下一位 AI 的唯一动作是 LOW 冻结第 2 格；禁止直接生成第 3 格 authorization。 |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

## 0.1 60 秒科学口径

- **神经网络已经真实介入：**Value V3 每个 MCTS root 仅做 1 次 12D→16 joint-action score forward，只改变 root depth=0 的动作展开顺序。

- **搜索算法主体没有被替换：**hard pruning=False、PUCT=False，UCT、rollout、backup、reward、transition、action provider 均保持原协议。

- **B8 已完整封口：**9/9 技术有效，6 PASS + 3 Scientific FAIL；三个 FAIL 全部集中在 model seed 20260825，因此 GUIDED_B8_STABLE=False。

- **B16 当前两格：**R0/M20260824 = Scientific FAIL；R0/M20260825 = Scientific PASS。两格技术链均闭合，但只有第一格完成 immutable freeze。

- **不能提前下最终结论：**B16 stability 需要 9/9 technical-valid cells；secondary expansion/wall-clock gate 需要 guided_min_stable_budget 确定后才能正式判定。

## 0.2 当前 Guided B16 状态矩阵

| **Runtime seed** | **Model 20260824**                | **Model 20260825**                       | **Model 20260826**        |
|------------------|-----------------------------------|------------------------------------------|---------------------------|
| **runtime 0**    | M20260824：FROZEN Scientific FAIL | M20260825：EXECUTED PASS，FREEZE PENDING | M20260826：NOT AUTHORIZED |
| **runtime 1**    | NOT AUTHORIZED                    | NOT AUTHORIZED                           | NOT AUTHORIZED            |
| **runtime 2**    | NOT AUTHORIZED                    | NOT AUTHORIZED                           | NOT AUTHORIZED            |

## 0.3 当前停点的一句话接管

| **一句话接管** B16 逻辑计数已到 2/9，但 authoritative frozen state 仍为 1/9；先在 LOW 将 R0/M20260825 的 Technical PASS + Scientific PASS 原子冻结，再更新 CellSpec 到 2/9，之后才允许处理 R0/M20260826。 |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# 目录与推荐阅读顺序

**1.** 0. CURRENT_STATE｜一页接手摘要

**2.** 1. 文档控制、证据等级与交接边界

**3.** 2. 项目长期主线总览

**4.** 3. MineSim 运行架构与永久科学边界

**5.** 4. 神经网络主线：Value V3 → C01 independent PASS → root ordering

**6.** 5. 预注册、Pure B8 与 Guided B8 最终封口

**7.** 6. Guided B16 设计与当前 2/9 真实结果

**8.** 7. 当前精确停点：第 2 格 evidence 已发布、freeze pending

**9.** 8. 错误、warning 与工程复盘

**10.** 9. 已固化的新工程标准

**11.** 10. 关键路径、SHA 与状态矩阵

**12.** 11. 资源、协作、文件与 Git 工作流

**13.** 12. DO_NOT_REPEAT / HOLD / NOT PROVEN

**14.** 13. 云端文档、failed stage 与删除边界

**15.** 14. 快速接手区（下一位 AI 必须先读）

**16.** 附录 A. 关键进度时间线

**17.** 附录 B. 下一 Gate 最小 PASS / FAIL 标准

**18.** 附录 C. 术语与状态解释

| **推荐阅读** 新 AI 先读第 0、6、7、8、9、14 节与附录 B；只有出现 SHA / provenance 冲突时，再回查第 2～5 节。 |
|--------------------------------------------------------------------------------------------------------------|

# 1. 文档控制、证据等级与交接边界

## 1.1 文档控制

| **项目**             | **值**                                                 | **边界**                                        |
|----------------------|--------------------------------------------------------|-------------------------------------------------|
| **文档版本**         | V1                                                     | 本轮 B16 2/9 技术有效、第二格待 Freeze 停点版。 |
| **适用对象**         | 后续 ChatGPT / Codex / 工程执行人员                    | 目标是无需重新扫描全项目即可继续。              |
| **正式 repo**        | /root/MineSim-Dynamic                                  | 唯一正式 tracked source。                       |
| **主 evidence root** | /root/autodl-tmp/paper1_value_v3_development_only_v1   | 结果、manifest、freeze、auth、CellSpec 主根。   |
| **证据截止**         | B16 R0/M20260825 FINAL_RC=0 之后、postexec freeze 之前 | 任何后续真实输出自动覆盖本 Word。               |
| **当前资源**         | LOW                                                    | 只做 freeze，不执行 runner。                    |

## 1.2 证据优先级

**1.** 当前 AutoDL 终端、Git、源码、真实运行输出与现场 SHA。

**2.** 已冻结 result / manifest / START / CAPTURE / authorization / preexec / freeze JSON。

**3.** 本交接 Word。

**4.** 历史交接 Word 与历史 bundle。

**5.** 研究计划、草稿、待办。

**6.** AI 记忆或无直接证据的推断。

| **硬规则** 文件名包含 PASS / final / freeze 并不等于证据成立；必须以内容、SHA、manifest 校验和真实状态字段为准。缺少直接证据时标记 HOLD / NOT VERIFIED，不得用常识补齐。 |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

## 1.3 状态词的精确定义

| **状态**                    | **含义**                                                      | **处理**                                    |
|-----------------------------|---------------------------------------------------------------|---------------------------------------------|
| **FROZEN**                  | 已发布 immutable freeze，SHA/manifest 闭合                    | 禁止重跑、禁止原地修改。                    |
| **EXECUTED_VALID_UNFROZEN** | START→RUN→CAPTURE 技术有效，evidence 已发布，但 freeze 未发布 | 当前第 2 格状态。                           |
| **AUTHORIZED_NOT_STARTED**  | authorization 已创建，START 未写入、consumed=False            | 可继续 prestart；不可视为已运行。           |
| **SCIENTIFIC FAIL**         | 程序、identity、instrumentation 均有效，但质量谓词未通过      | 必须计入矩阵并冻结，不是 retry 理由。       |
| **TECHNICAL HOLD/FAIL**     | identity、artifact、schema、runtime 或证据链不满足            | 不得计入矩阵；是否允许 retry 必须另行授权。 |
| **NOT AUTHORIZED**          | 不存在可消费的 one-time auth                                  | 不得启动。                                  |
| **HOLD / NOT EVALUATED**    | 当前证据不足以形成结论                                        | 不得改写为 PASS/FAIL。                      |

## 1.4 本版不做的事情

- 不重新运行 B8 或 B16 已启动的任何 cell。

- 不把第 2 格未冻结结果写成 FROZEN。

- 不创建第 3 格 authorization。

- 不改变 OMP、CUDA、runner、checkpoint、搜索算法或预注册。

- 不进行全盘删除，不声明历史 failed stage 已清理。

- 不发布 B16 stability、secondary final claim 或 production-ready 结论。

# 2. 项目长期主线总览

MineSim-Dynamic 的主线不是“单独训练一个网络”，而是把矿区多车冲突闭环、可复现 MCTS、冻结评价协议和神经网络根节点排序逐层接通。当前已越过复现与接入阶段，正在验证 Value-guided MCTS 是否能在固定 3×3 seed 矩阵下达到稳定质量，并形成可审计的效率结论。

| **阶段**                           | **状态**                 | **当前结论**                                                    |
|------------------------------------|--------------------------|-----------------------------------------------------------------|
| **MineSim 原项目复现**             | PASS / HISTORICAL        | Dapai / Jiangtong 闭环、IDM / Replay 等基础已完成。             |
| **Pure MCTS / Multi-Fleet MCTS**   | PASS / FROZEN EVIDENCE   | 单车、多车、16 joint actions、双车冲突 benchmark 已有真实证据。 |
| **Full-Mine / 新地图**             | RESEARCH / DEV           | 可用于研究闭环；不等于官方生产级 HD Map。                       |
| **Value V2**                       | SCIENTIFIC FAIL / CLOSED | C03 independent validation 未通过；DO_NOT_INTEGRATE。           |
| **Value V3 2356-root development** | FROZEN                   | 2356 roots、37696 action rows、LOSO、3 fixed seeds。            |
| **C01 independent forward**        | FROZEN PASS              | 证明动作价值排序在独立 C01 上有用。                             |
| **Integration preregistration**    | FROZEN                   | budget ladder \[8,16,32,64\]，runtime/model seeds 与指标固定。  |
| **Pure B8**                        | FROZEN STABLE            | runtime seeds 0/1/2 全 PASS，pure minimum stable budget=8。     |
| **Guided B8**                      | FROZEN 9/9，UNSTABLE     | 6 PASS + 3 FAIL；B8 描述性降开销，不构成 final secondary gate。 |
| **Guided B16**                     | CURRENT                  | 2/9 技术有效；1/9 frozen；第 2 格待 freeze。                    |

## 2.1 当前真正的研究问题

- 不是“网络能否跑起来”：Value V3 已训练、已独立评价、已接入真实 MCTS。

- 不是“是否改变 MCTS”：当前协议只允许根节点动作排序，不允许改 UCT / rollout / backup / reward。

- 当前问题是：在固定 model seeds × runtime seeds 下，最低哪个 prereg budget 能让 9/9 Guided runs 全部通过质量？

- 只有确定 guided_min_stable_budget 后，才能与 Pure minimum stable budget=8 的 expansion / outer wall-clock 中位数做最终 gate。

## 2.2 历史阶段为何不应重做

- 2356-root training、C01 forward、Pure B8、Guided B8 已有一整套 frozen provenance；重做只会破坏可比性。

- 历史负结果同样属于科学证据，例如 Value V2 independent FAIL、B8 的三个 Scientific FAIL。

- 当前 runner/checkpoints/Git HEAD 均已由 SHA 锁定；下一步是证据封口，不是工程重构。

# 3. MineSim 运行架构与永久科学边界

## 3.1 真实闭环

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>Scenario / Map<br />
→ Planner.initialize()<br />
→ 每帧 compute_trajectory()<br />
→ Controller<br />
→ Kinematic vehicle model<br />
→ Ego / actor state update<br />
→ collision / completion / metrics<br />
→ 下一帧重新规划</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

Planner 输出的是未来轨迹，不是下一帧车辆位置；搜索层、轨迹层、控制层和车辆动力学层必须分开诊断。

## 3.2 Value-guided MCTS 的允许介入点

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>当前 root state<br />
→ 12D feature builder<br />
→ Value V3 forward（每个 root 仅 1 次）<br />
→ 16 个 joint-action scores<br />
→ 仅排序 root depth=0 的 expansion order<br />
→ 后续 tree search 按原 MCTS 运行</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

| **机制**                               | **冻结值**   | **边界**     |
|----------------------------------------|--------------|--------------|
| **Value forward**                      | 每 root 1 次 | 允许         |
| **root depth=0 joint-action ordering** | 改变展开先后 | 允许         |
| **hard pruning**                       | False        | 禁止改变     |
| **PUCT**                               | False        | 禁止改变     |
| **UCT formula**                        | unchanged    | 禁止改变     |
| **rollout policy**                     | unchanged    | 禁止改变     |
| **backup / reward / transition**       | unchanged    | 禁止改变     |
| **action provider**                    | unchanged    | 禁止改变     |
| **best seed selection**                | False        | 禁止事后挑选 |

## 3.3 日志解释陷阱

| **旧 banner 不等于真实 variant** stdout 仍显示 “J117 ALIGNED REAL PRODUCTION PURE-MCTS CONFLICT BENCHMARK”，但 authoritative 字段是 benchmark_variant=guided、integration_variant=ROOT_ONLY_VALUE_ACTION_ORDER_GUIDANCE_V1、mcts_value_integration_executed=True。不得仅凭 banner 把 Guided 误判成 Pure。 |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

## 3.4 永久生产边界

- production_ready=False、production_safety_proven=False。

- 当前结果是冻结研究 benchmark，不等于真实矿区部署验收。

- 无权威 production drivability / HD Map truth 时，不得升级地图或安全结论。

# 4. 神经网络主线：Value V3 → C01 independent PASS → root ordering

## 4.1 2356-root 冻结训练协议

| **项目**             | **冻结值**                                                                          |
|----------------------|-------------------------------------------------------------------------------------|
| **Dataset**          | 2356 roots；37696 action rows；6 episodes；identity=(scene, episode_uid, root_step) |
| **Architecture**     | 12 → 64 → 64 → 16；ActionConditionedValueV3PairwiseRank                             |
| **Objective**        | ROOT_NORMALIZED_WEIGHTED_PAIRWISE_LOGISTIC                                          |
| **Split**            | LEAVE_ONE_SCENE_OUT                                                                 |
| **Final seeds**      | 20260824 / 20260825 / 20260826                                                      |
| **Epochs / LR**      | 600 / 0.001                                                                         |
| **Best-seed / HPO**  | False / False                                                                       |
| **Output semantics** | 16 joint-action scores；joint_action_index = A\*4+B                                 |

## 4.2 C01 独立泛化结果

| **对象**                      | **Normalized regret / 状态**    | **结论**             |
|-------------------------------|---------------------------------|----------------------|
| **Frozen immediate baseline** | 0.2951958615926099              | 比较基线             |
| **Model seed 20260824**       | 0.09947470394112914             | PASS candidate       |
| **Model seed 20260825**       | 0.15596316637663826             | PASS candidate       |
| **Model seed 20260826**       | 0.10583949665541333             | PASS candidate       |
| **3-seed median**             | 0.10583949665541333             | strictly \< baseline |
| **Classification**            | INDEPENDENT_GENERALIZATION_PASS | FROZEN PASS          |

科学口径：这证明网络在独立 C01 上能够提供有用的动作价值排序；它不自动证明 MCTS search compute reduction、wall-clock speedup 或 production safety。

## 4.3 三个 final checkpoint

| **Model seed** | **checkpoint.pt SHA256**                                         |
|----------------|------------------------------------------------------------------|
| **20260824**   | 496e4259eb9801f3ce70c1094be12fd0985cb03e97d606cade8dfbe9d5228633 |
| **20260825**   | 5df90947a5fdd2bc6aa525ca5eba78b6379e127e5df6ca1d0362c992caab73b5 |
| **20260826**   | 3881d39c09b02a513e44f0fe612aad42de9ff636fd07e314d327b4c6d5f132df |

## 4.4 当前介入进度

- B8 9-cell matrix 已完整跑完，说明网络 forward、root ordering、artifact collection 与 matrix protocol 已真实闭环。

- B16 已跑 2 格：第 1 格网络做 890 次 forward；第 2 格网络做 254 次 forward。

- 每个 root 的 metrics 必须 value_forward_count=1，result 的 value_forward_count_total 必须等于 root_search_count。

# 5. 预注册、Pure B8 与 Guided B8 最终封口

## 5.1 冻结预注册

| **项目**                     | **冻结规则**                                                                   |
|------------------------------|--------------------------------------------------------------------------------|
| **Budget ladder**            | \[8, 16, 32, 64\]                                                              |
| **Runtime MCTS seeds**       | \[0, 1, 2\]                                                                    |
| **Guided model seeds**       | \[20260824, 20260825, 20260826\]                                               |
| **Guided stable**            | 同一 budget 的 9 个 model×runtime 条件全部 per-run quality PASS                |
| **Guided min stable budget** | 满足 stable 的最小 prereg budget                                               |
| **Expansion secondary**      | median Guided TOTAL_TREE_EXPANSIONS @ guided_min \< median Pure @ pure_min     |
| **Wall-clock gate**          | median Guided OUTER_SEARCH_WALLCLOCK_MS @ guided_min \< median Pure @ pure_min |

## 5.2 Pure B8 baseline

| **Runtime seed** | **Root searches** | **Iterations** | **Tree expansions** | **质量** |
|------------------|-------------------|----------------|---------------------|----------|
| **0**            | 453               | 3624           | 3624                | PASS     |
| **1**            | 429               | 3432           | 3432                | PASS     |
| **2**            | 341               | 2728           | 2728                | PASS     |

- PURE_B8_STABLE=True；PURE_MIN_STABLE_BUDGET=8。

- 因此“Guided 获得更低最低稳定预算”的 primary criterion 因预算下限而真实 Scientific FAIL。

- 禁止事后新增 B4 / B2，禁止把该科学失败包装成 technical retry。

## 5.3 Guided B8 9-cell 最终矩阵

| **Condition**    | **Science** | **Roots** | **Expansions** |
|------------------|-------------|-----------|----------------|
| **R0/M20260824** | PASS        | 308       | 2464           |
| **R0/M20260825** | FAIL        | 890       | 7120           |
| **R0/M20260826** | PASS        | 331       | 2648           |
| **R1/M20260824** | PASS        | 326       | 2608           |
| **R1/M20260825** | FAIL        | 890       | 7120           |
| **R1/M20260826** | PASS        | 291       | 2328           |
| **R2/M20260824** | PASS        | 283       | 2264           |
| **R2/M20260825** | FAIL        | 890       | 7120           |
| **R2/M20260826** | PASS        | 330       | 2640           |

- 最终 6 PASS + 3 Scientific FAIL；三个 FAIL 全部位于 model seed 20260825。

- GUIDED_B8_STABLE=False，因此 B8 不能替代 guided_min_stable_budget。

## 5.4 B8 描述性效率结果（不是 final gate）

| **指标**                    | **Guided**                      | **Pure**                 | **描述性差异**        |
|-----------------------------|---------------------------------|--------------------------|-----------------------|
| **Tree expansions median**  | Guided B8 all9 = 2640           | Pure B8 = 3432           | 描述性下降 23.076923% |
| **Outer wall-clock median** | Guided B8 all9 = 6358.152736 ms | Pure B8 = 6763.010833 ms | 描述性下降 5.986359%  |

| **不可越界** 这些数值可以作为 B8 descriptive evidence，但由于 B8 不稳定，不能升级成 prereg tree-expansion reduction PASS 或 wall-clock speedup PASS。下一 prereg budget 是 B16。 |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# 6. Guided B16 设计与当前 2/9 真实结果

## 6.1 B16 设计边界

- Budget 从 8 增至 16；network hook、runner、scenario、runtime/model seed universe 和质量谓词保持不变。

- 9 个 canonical cells 顺序为 R0/M24、R0/M25、R0/M26、R1/M24、R1/M25、R1/M26、R2/M24、R2/M25、R2/M26。

- 每格 one-time authorization；START 写入即消费；Technical PASS 下 Science PASS/FAIL 均计入矩阵。

- B16 stability 只能在 9 个 technical-valid cells 全部完成后判定。

## 6.2 第 1 格：R0/M20260824（已冻结 Scientific FAIL）

| **项目**                            | **冻结值**                                                                                                  |
|-------------------------------------|-------------------------------------------------------------------------------------------------------------|
| **Condition**                       | GUIDED_B16_RUNTIME_SEED0_MODEL_SEED20260824                                                                 |
| **Technical / Science**             | PASS / FAIL                                                                                                 |
| **Quality predicates**              | Completion=False；No collision=True；No invalid=True；No runtime error=True；Post-conflict completion=False |
| **Roots / iterations / expansions** | 890 / 14240 / 14240                                                                                         |
| **Value forwards**                  | 890                                                                                                         |
| **Core / outer wall**               | 29058.812305 ms / 30319.119874 ms                                                                           |
| **Value inference**                 | 115.606561 ms                                                                                               |
| **Runner wall**                     | 52.367515050 s                                                                                              |
| **OMP**                             | stdout evidence 中出现 libgomp invalid-value warning；技术有效性不变；exact raw value 未持久化              |
| **Freeze SHA**                      | b05f047c0abc7268252d733296d631f965f4b4fc5779b993ed6e8127c9da94c4                                            |

## 6.3 第 2 格：R0/M20260825（已执行，待 Freeze）

| **项目**                            | **当前证据**                                                                                        |
|-------------------------------------|-----------------------------------------------------------------------------------------------------|
| **Condition**                       | GUIDED_B16_RUNTIME_SEED0_MODEL_SEED20260825                                                         |
| **Technical / Science**             | PASS / PASS                                                                                         |
| **Quality predicates**              | 五项全部 True                                                                                       |
| **Roots / iterations / expansions** | 254 / 4064 / 4064                                                                                   |
| **Value forwards**                  | 254                                                                                                 |
| **Core / outer wall**               | 8208.690464 ms / 8580.236688 ms                                                                     |
| **Value inference**                 | 32.844096 ms                                                                                        |
| **Runner wall**                     | 30.127432421 s                                                                                      |
| **Crossing**                        | A=9.642500 s；B=22.188124 s；gap=12.545624 s；first=A                                               |
| **Minimum clearance**               | 1.579398883 m；collision=False；physical_overlap=False                                              |
| **OMP**                             | OMP_NUM_THREADS=1 显式绑定；environment warnings=\[\]                                               |
| **Evidence state**                  | START consumed；CAPTURE/evidence/output manifests published and reverified；postexec freeze pending |

## 6.4 两格对比的正确解释

- 同一 runtime seed=0 下，model seed 20260824 在 B16 未完成任务，model seed 20260825 完成任务。

- 这说明模型 seed 对 root ordering 结果仍有显著影响；但禁止据此选择“最好 seed”。

- 第二格根搜索数较少是任务更早完成后的结果，不应在矩阵未完成时单独包装成最终效率结论。

- 第一格 OMP exact raw value 未持久化；第二格及后续显式 OMP=1。任何最终 wall-clock 汇总必须保留该 provenance 注释。

# 7. 当前精确停点：第 2 格 evidence 已发布、freeze pending

## 7.1 已经完成且不可回退

| **对象**                | **当前事实**                                                                |
|-------------------------|-----------------------------------------------------------------------------|
| **One-time START**      | 已写入；authorization consumed=True；reusable=False                         |
| **Runner**              | RC=0；status=PASS                                                           |
| **Identity**            | runtime seed=0；model seed=20260825；budget=16；CellSpec V2 match           |
| **Instrumentation**     | 254 roots；4064 iterations/expansions；254 forwards；每 root 1 forward      |
| **Quality**             | 五项谓词全部 True                                                           |
| **Environment**         | OMP_NUM_THREADS=1；无 environment warnings                                  |
| **Evidence publish**    | CAPTURE、stdout/stderr、RC、wall、output manifest、evidence manifest 已发布 |
| **Post-publish verify** | evidence SHA256SUMS PASS；output SHA256SUMS PASS                            |
| **Matrix logic**        | before=1；after technical valid=2；counts_toward=True                       |

## 7.2 尚未完成

- 未创建第 2 格 postexec immutable freeze。

- 未将 authoritative B16 CellSpec 从 1/9 更新为 2/9。

- 未构建 frozen 2-cell regression。

- 未授权第 3 格 R0/M20260826。

- 未判定 B16 stable / unstable。

## 7.3 下一最小动作（唯一合法动作）

| **NEXT_MINIMAL_ACTION** 保持 LOW，创建一个新的 immutable namespace，对 R0/M20260825 做 postexec PASS freeze。必须核验 runner RC=0、status=PASS、五项 quality=True、254/4064/254 计数、OMP=1、warnings=\[\]、START self-binding、CellSpec/Auth/Preexec/Runner/Checkpoint SHA、output/evidence manifests；然后原子发布 freeze，并再次证明原始 result/CAPTURE 未修改。 |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

## 7.4 freeze 完成后的顺序

**1.** 构建 B16 CellSpec V3：current_matrix_count=2，matrix_remaining=7，occupied=\[\[0,20260824\],\[0,20260825\]\]，next=\[0,20260826\]。

**2.** 构建 frozen 2-cell regression：第 1 格 FAIL、第 2 格 PASS 的 identity、budget16 instrumentation、quality preservation 全部回归。

**3.** 保持 OMP_NUM_THREADS=1 显式绑定政策；不得反推第一格 exact raw OMP。

**4.** 单独授权 R0/M20260826；不得批量授权剩余 7 格。

## 7.5 建议 freeze 的预期事实面（不是已创建文件）

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>CONDITION=GUIDED_B16_RUNTIME_SEED0_MODEL_SEED20260825<br />
TECHNICAL_STATUS=PASS<br />
SCIENTIFIC_RESULT=PASS<br />
COUNTS_TOWARD_B16_MATRIX=True<br />
MATRIX_COUNT_BEFORE=1<br />
MATRIX_COUNT_AFTER=2<br />
ROOT_SEARCH_COUNT=254<br />
TOTAL_TREE_EXPANSIONS=4064<br />
VALUE_FORWARD_COUNT_TOTAL=254<br />
OMP_NUM_THREADS=1<br />
ENVIRONMENT_WARNINGS=[]<br />
SAME_CONDITION_RERUN_AUTHORIZED=False<br />
POSTHOC_TUNING_AUTHORIZED=False</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

*注意：freeze root / JSON 文件名尚未由真实 LOW gate 创建，下一位 AI 可提出新 immutable namespace，但必须先确认该 namespace 不存在。*

# 8. 错误、warning 与工程复盘

| **问题**                        | **现象/根因**                                                           | **固化处理**                                                                 |
|---------------------------------|-------------------------------------------------------------------------|------------------------------------------------------------------------------|
| **E1：capture hardcoded seed**  | 旧 wrapper 校验 result.seed 时残留 seed=0，导致 TOP_LEVEL_SEED_MISMATCH | 改为 CellSpec + helper.validate_result_identity；禁止 literal seed compare。 |
| **E2：字符串 cardinality 假设** | checkpoint SHA 实际有 3 个合法语义角色，旧派生器写死 count=2            | 改为 semantic-role audit，不再把“出现次数”当正确性。                         |
| **E3：全局 token replacement**  | seed/model/budget/schema 字符串替换造成 stale token、错误路径与版本标签 | B16 改为 spec-driven template render，禁止裸 seed 全局替换。                 |
| **E4：heredoc 关键词误识别**    | authorization_consumed_by_start 同时出现在 START 与 postrun block       | 使用 AST 识别 start={...} / capture={...} 结构。                             |
| **E5：source schema 残留**      | B8 source wrapper 曾保留更早 cell schema label                          | 读取 source provenance，再对新 target 结构化绑定；不修改 frozen source。     |
| **E6：OMP warning**             | B16 第 1 格 stderr: libgomp Invalid value for OMP_NUM_THREADS           | 第 1 格保留为非致命环境 warning；第 2 格起显式 export OMP_NUM_THREADS=1。    |
| **E7：旧 stdout banner**        | Banner 含 PURE-MCTS，但 authoritative benchmark_variant=guided          | 只看结构化 result 字段，不看标题字符串。                                     |
| **E8：外部 shell 噪声**         | /root/autodl-tmp/codex-env.sh 不存在；曾有脚本未上传导致 No such file   | 当前协议直接 source conda；这些错误无 START、无项目变更。                    |

## 8.1 OMP warning 的严格口径

- 第 1 格的 warning 已冻结，不改变 Technical PASS，也不授权重跑。

- 第 1 格 exact OMP raw value 未写入 evidence，不能事后声称它当时就是 1。

- 当前 shell 审计观察为 OMP_NUM_THREADS=1，且第 2 格 wrapper 显式 export 1；第 2 格 warnings=\[\]。

- 后续 B16 高资源 wrapper 应继续显式绑定 1，并将该值写入 START/CAPTURE。

- 最终 wall-clock 结论若包含第 1 格，必须保留环境 provenance note。

## 8.2 为什么这次第二格是可信 PASS

- 运行前 exact SHA、namespace absence、CellSpec V2、frozen 1-cell regression 和 OMP binding 全部通过。

- 运行后 result identity、quality predicates、root/metrics/shadow 计数和 value-forward 数全部闭合。

- CAPTURE strict errors=\[\]；evidence/output manifests 在 publish 后再次校验 PASS。

- FINAL_RC=0 来自 Technical PASS，而不是简单等同 runner RC。

# 9. 已固化的新工程标准

| **标准**                       | **强制要求**                                                                              |
|--------------------------------|-------------------------------------------------------------------------------------------|
| **S1 单一真源**                | CellSpec 是 condition、checkpoint、output、artifact names、matrix accounting 的唯一来源。 |
| **S2 Spec-driven render**      | 新 wrapper 由结构化模板渲染，不从旧 wrapper 做大范围字符串替换。                          |
| **S3 Exact SHA**               | CellSpec/Auth/Preexec/Runner/Meta/Checkpoint/parent freeze 均核 exact SHA。               |
| **S4 Manifest replay**         | prestart 与 postpublish 都执行 sha256sum -c。                                             |
| **S5 AST role identification** | START/CAPTURE 通过 AST dict assignment 识别，不靠关键词。                                 |
| **S6 Full prestart**           | 所有断言必须在 START boundary 前真实 replay；缺 marker 即 HOLD。                          |
| **S7 One-time authorization**  | START 即消费；技术有效无论 Science PASS/FAIL 都禁止 rerun。                               |
| **S8 Outcome-consistent RC**   | runner PASS→RC0；runner FAIL→RC1；其余组合为 technical failure。                          |
| **S9 Capture always**          | Science PASS/FAIL 或 technical failure 均写 CAPTURE、RC、stdout/stderr 与 checksums。     |
| **S10 Immediate freeze**       | 技术有效结果先 freeze，再更新矩阵，再授权下一格。                                         |
| **S11 Environment binding**    | 后续 B16 wrapper 显式 OMP_NUM_THREADS=1、CUDA_VISIBLE_DEVICES=""。                        |
| **S12 No posthoc selection**   | 禁止挑 best model/runtime seed，禁止脱离 prereg ladder 调 budget。                        |

## 9.1 建议的高效流水线

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>LOW: freeze 当前 technical-valid cell<br />
→ LOW: 构建下一版 CellSpec + frozen-N-cell regression<br />
→ LOW: 单格 auth + spec-driven wrapper + full prestart<br />
→ HIGH-CPU: 仅执行该一格<br />
→ 立刻回 LOW<br />
→ 重复，直到 9/9</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

效率提升来自“固定模板 + 单一 CellSpec + 自动回归”，不是跳过 freeze、prestart 或 one-time boundary。

# 10. 关键路径、SHA 与状态矩阵

## 10.1 当前关键路径

| **对象**                | **路径**                                                                                                              | **作用/边界**                            |
|-------------------------|-----------------------------------------------------------------------------------------------------------------------|------------------------------------------|
| **正式 repo**           | /root/MineSim-Dynamic                                                                                                 | Git tracked source                       |
| **主 evidence root**    | /root/autodl-tmp/paper1_value_v3_development_only_v1                                                                  | 所有当前 Value/MCTS 证据                 |
| **B8 final 9/9 freeze** | .../value_guided_mcts_c01_secondary_b8_guided_r2_m20260826_postexec_cellspec4_final_9of9_freeze_v1                    | B8 matrix complete                       |
| **B8 secondary status** | .../value_guided_mcts_c01_secondary_b8_descriptive_and_prereg_gate_status_freeze_v1                                   | B8 unstable；next budget B16             |
| **B16 CellSpec V2**     | .../value_guided_mcts_c01_guided_b16_cellspec_v2                                                                      | authoritative frozen matrix=1/9          |
| **B16 cell1 freeze**    | .../value_guided_mcts_c01_secondary_b16_guided_r0_m20260824_postexec_scientific_fail_freeze_v1                        | FROZEN FAIL                              |
| **B16 cell2 auth**      | .../value_guided_mcts_c01_secondary_b16_guided_r0_m20260825_authorization_fix6r3_cellspecb16_v1                       | consumed by START                        |
| **B16 cell2 output**    | .../value_guided_mcts_c01_secondary_b16_guided_execution_fix6r3_v1/guided_budget16_runtime_seed0_model_seed20260825   | result + metrics                         |
| **B16 cell2 evidence**  | .../value_guided_mcts_c01_secondary_b16_guided_r0_m20260825_execution_evidence_fix6r3_cellspecb16_v1                  | START/CAPTURE/stdout/stderr/RC/manifests |
| **B16 cell2 wrapper**   | /root/autodl-tmp/C01_VALUE_GUIDED_MCTS_GUIDED_B16_R0_M20260825_START_RUN_CAPTURE_FIX6R3_CELLSPECB16V2_FAILFAST_V1.txt | 已执行，禁止再次运行                     |

## 10.2 当前关键 SHA

| **对象**                         | **SHA256**                                                       | **状态**     |
|----------------------------------|------------------------------------------------------------------|--------------|
| **Git HEAD**                     | 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e                         | CLEAN        |
| **Integration prereg**           | 0ccbded4caa5bbec28c5a6b13fde9d896983dc40f4555753e38dfe5b5e7d04bb | FROZEN       |
| **Pure B8 stability**            | 3e17ef39f066377be2f1344a94c7d3d6eea9f61712fc52f3682218088b25e582 | FROZEN       |
| **B8 final 9/9 freeze**          | 33158323b3432806dc72586bc905379ffa4bfd1a5ad90cf623cf18f6306490c8 | FROZEN       |
| **B8 secondary status freeze**   | 46ea14c53e9a035d84057c1907ce36f25a105c601819dc71f0e201c832cf9a55 | FROZEN       |
| **FIX6R3 runner**                | ea4d7f21265be0b2409cc2b25e6f1bd2c7ad49317d593929a34752d286d5eb79 | FROZEN       |
| **FIX6R3 meta**                  | c0e1520d81ddc1b36c1e56078e2dbf1ea50c1cd6a0f2e9ad59adef5ccd25464c | FROZEN       |
| **B16 CellSpec V2**              | f38f944b5c9fee82ff511ad1a976fc204d14a8c4f97f4b25161404db310ac05e | CURRENT      |
| **B16 frozen 1-cell regression** | 7253d80a0c4b8b3d09282ef1bbefb0d05ffd3df7aa1c2ea8dcb5ae7855721d42 | FROZEN       |
| **B16 OMP audit**                | 8f826ae62476eb7d74670eae9b391964ef5406f39693e838b78beaaf55192251 | FROZEN AUDIT |
| **B16 cell1 freeze**             | b05f047c0abc7268252d733296d631f965f4b4fc5779b993ed6e8127c9da94c4 | FROZEN FAIL  |
| **B16 cell2 auth**               | 303ab00a4e32e635df74e61ef276404c956368e418bdefa06b469e48852f5cd6 | CONSUMED     |
| **B16 cell2 preexec**            | a176bccb87bce1462581b6a6bdc288cc6cf6f51f8b4ae9dea0fdf780178ad547 | PASS         |
| **B16 cell2 wrapper**            | d614226992c3f12f934b5c349f0c3e043029eb7a2c2246d273b53fc84ed6ef5a | EXECUTED     |
| **Checkpoint 20260825**          | 5df90947a5fdd2bc6aa525ca5eba78b6379e127e5df6ca1d0362c992caab73b5 | FROZEN       |

## 10.3 B16 当前 authoritative 状态层次

| **层**            | **计数/状态**          | **解释**                         |
|-------------------|------------------------|----------------------------------|
| **CellSpec V2**   | current_matrix_count=1 | FROZEN source of truth           |
| **Cell1 freeze**  | matrix_after=1         | FROZEN                           |
| **Cell2 CAPTURE** | matrix_after=2         | VALID evidence, not yet frozen   |
| **Cell2 freeze**  | 不存在                 | NEXT GATE                        |
| **CellSpec V3**   | 不存在                 | 不得提前创建为 authoritative 2/9 |

# 11. 资源、协作、文件与 Git 工作流

## 11.1 固定执行环境

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
export CUDA_VISIBLE_DEVICES=""<br />
export OMP_NUM_THREADS="1"<br />
<br />
git rev-parse HEAD<br />
git status --short --untracked-files=no</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

- 当前 Git HEAD 必须是 112d2bd0...，tracked Git clean。

- 当前 branch 名不在最新证据中；不要新建或切换分支，需写代码前先真实读取 branch。

- B16 freeze / CellSpec / authorization / diagnostics 使用 LOW。

- 只有 full prestart PASS 后的单格 execution 使用 HIGH-CPU；GPU_REQUIRED=False。

## 11.2 ChatGPT / 用户 / Codex 分工

| **角色**    | **职责**                                       | **边界**                            |
|-------------|------------------------------------------------|-------------------------------------|
| **ChatGPT** | 证据分析、Gate 决策、脚本生成、文档与 SHA 口径 | 不得声称未运行结果。                |
| **用户**    | 上传脚本、在 AutoDL 执行、回传完整终端输出     | 一次只执行明确放行的命令。          |
| **Codex**   | 复杂源码重构或顽固 bug；当前 Gate 不需要       | 不得以 Codex 替代 frozen protocol。 |

## 11.3 当前文件操作纪律

- 新的 freeze / CellSpec 使用新 immutable namespace；不覆盖历史。

- 不执行 git reset --hard、git clean -fd、git add . 或未经审计的 rm -rf。

- 不修改 frozen JSON、manifest、START、CAPTURE、result、checkpoint。

- 对 B16 cell2 freeze，先确认目标 root/stage 不存在，再原子 publish。

# 12. DO_NOT_REPEAT / HOLD / NOT PROVEN

## 12.1 DO_NOT_REPEAT

- 不要再次执行 B16 R0/M20260824 wrapper：已消费、已冻结。

- 不要再次执行 B16 R0/M20260825 wrapper：已消费、已技术有效。

- 不要重跑任何 Guided B8 cell。

- 不要因 Science FAIL 调参或换 seed；FAIL 是矩阵的一部分。

- 不要为消除第一格 OMP warning 重跑第一格。

- 不要依赖 /root/autodl-tmp/codex-env.sh；当前脚本直接激活 minesim。

- 不要从 stdout 的 PURE-MCTS banner 推断 variant。

## 12.2 HOLD

| **对象**                             | **状态**           | **边界**                                  |
|--------------------------------------|--------------------|-------------------------------------------|
| **B16 R0/M20260826 authorization**   | HOLD               | 必须先 freeze 第 2 格并发布 CellSpec V3。 |
| **B16 stability**                    | NOT EVALUATED      | 必须完成 9 technical-valid cells。        |
| **guided_min_stable_budget**         | UNDETERMINED       | B8 不稳定；B16 尚未完成。                 |
| **Tree-expansion secondary gate**    | NOT EVALUATED      | 需 guided_min stable budget。             |
| **Outer wall-clock gate**            | NOT EVALUATED      | 同上，并保留第一格 OMP provenance note。  |
| **Best model/runtime seed**          | FORBIDDEN          | 预注册明确不允许。                        |
| **Production ready / safety proven** | FALSE / NOT PROVEN | 研究 benchmark 不等于生产验收。           |
| **AutoDL 全盘删除状态**              | HOLD               | 本交接未执行 live inventory 或删除。      |

## 12.3 当前可以说、不能说

| **口径**   | **表述**                                                                                             |
|------------|------------------------------------------------------------------------------------------------------|
| **可以说** | Value V3 已独立 C01 PASS；已真实介入 root ordering；B8 9/9 完成但不稳定；B16 前两格一 FAIL 一 PASS。 |
| **不能说** | B16 已稳定；guided_min stable budget=16；神经网络已证明稳定降低 compute；已 production ready。       |

# 13. 云端文档、failed stage 与删除边界

| **文档/类别**                                  | **定位**                                | **说明**                                |
|------------------------------------------------|-----------------------------------------|-----------------------------------------|
| **2026-08-25 Value V3 2356-root 神经网络交接** | HISTORICAL / FROZEN training provenance | 训练协议与 development 结果仍有效。     |
| **2026-08-27 Guided B8 1/9 交接**              | HISTORICAL                              | 已被后续 B8 9/9 与本 B16 handoff 覆盖。 |
| **2026-08-29 B8 4/9 line275 交接**             | HISTORICAL ERROR PROVENANCE             | 脆弱断言与修复经验仍有效。              |
| **本文件**                                     | CURRENT HANDOFF                         | 截至 B16 第 2 格执行完成、待 freeze。   |
| **Conversation / Library copies**              | AVAILABLE / PARTIAL                     | 不等于 AutoDL 已同步。                  |
| **AutoDL handoff live inventory**              | HOLD                                    | 本轮未全盘扫描。                        |

## 13.1 Failed stage / 删除纪律

- 历史 failed stage、diagnostic、错误 wrapper 默认保留，不删除、不覆盖。

- 新修复使用新 namespace 和新 SHA；旧失败文件用于 provenance。

- 本交接未执行任何项目文件删除。

- 终端中的 “No such file or directory” 仅说明脚本未上传/路径不存在，不代表需要清理项目目录。

# 14. 快速接手区（下一位 AI 必须先读）

| **接手问题**               | **准确答案**                                                                                       |
|----------------------------|----------------------------------------------------------------------------------------------------|
| **1. 项目现在做到哪里？**  | B8 9/9 frozen；B16 2/9 technical-valid，其中 1/9 frozen，第 2 格待 freeze。                        |
| **2. 当前唯一 Gate？**     | LOW freeze GUIDED_B16_RUNTIME_SEED0_MODEL_SEED20260825。                                           |
| **3. 第 2 格真实结果？**   | Technical PASS + Scientific PASS；254 roots、4064 expansions、254 forwards；OMP=1；warnings=\[\]。 |
| **4. 第 1 格怎么办？**     | 已 FROZEN Scientific FAIL；禁止重跑；保留 OMP warning provenance。                                 |
| **5. 能否直接跑第 3 格？** | 不能。必须 freeze 第 2 格并构建 CellSpec V3。                                                      |
| **6. 正式 repo？**         | /root/MineSim-Dynamic                                                                              |
| **7. Evidence root？**     | /root/autodl-tmp/paper1_value_v3_development_only_v1                                               |
| **8. Git HEAD？**          | 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e，tracked clean。                                          |
| **9. 当前资源？**          | LOW；freeze 不得 load checkpoint / forward / MCTS。                                                |
| **10. OMP？**              | 后续 wrapper 显式 OMP_NUM_THREADS=1；第一格 exact raw value 不得倒推。                             |
| **11. 网络介入点？**       | 每 root 1 次 forward，仅 root depth=0 joint-action ordering。                                      |
| **12. 最终结论到哪？**     | B16 stability 与 secondary final claims 均 NOT EVALUATED。                                         |

## 14.1 下一位 AI 的 10 分钟动作清单

**1.** 读取第 0、6、7、8、9、14 节。

**2.** 在 AutoDL LOW 确认 repo HEAD / tracked clean / 无 B16 相关进程。

**3.** 读取并校验 CellSpec V2、regression1、OMP audit、cell2 auth/preexec/wrapper、cell2 evidence/output manifests。

**4.** 生成 cell2 postexec PASS freeze；不执行 runner。

**5.** 核对 254 roots、4064 expansions、254 forwards、五项 quality=True、OMP=1、warnings=\[\]。

**6.** 原子 publish freeze 并再次 sha256sum -c。

**7.** 创建 CellSpec V3 + frozen 2-cell regression；next cell 必须是 \[0,20260826\]。

**8.** 停止；下一格 authorization 需单独 Gate。

## 14.2 接手前禁止动作

| **禁止** 不要再次运行 cell2 wrapper；不要创建第 3 格 authorization；不要修改 OMP 策略；不要重写第一格 warning；不要发布 B16 stable 或 speedup 结论。 |
|------------------------------------------------------------------------------------------------------------------------------------------------------|

# 附录 A. 关键进度时间线

| **时间**           | **事件**                                                                                           |
|--------------------|----------------------------------------------------------------------------------------------------|
| **2026-08-25**     | Value V3 2356-root training 完成，形成 3 fixed final checkpoints。                                 |
| **2026-08-26/27**  | C01 independent forward PASS；integration prereg、Pure B8 stable 与 primary floor FAIL 固化。      |
| **2026-08-27～29** | Guided B8 9-cell matrix 完成并冻结：6 PASS + 3 FAIL，B8 unstable。                                 |
| **2026-08-29**     | B8 descriptive / prereg gate status freeze：guided_min stable budget 未定，next budget B16。       |
| **2026-08-29**     | B16 CellSpec V1 建立；第 1 格 R0/M24 执行 Technical PASS + Scientific FAIL。                       |
| **2026-08-29**     | 第 1 格 freeze 发布；B16 authoritative matrix=1/9。                                                |
| **2026-08-29**     | OMP audit 观察 current shell OMP_NUM_THREADS=1；未倒推第一格 exact raw value。                     |
| **2026-08-29**     | B16 CellSpec V2 + frozen 1-cell regression 发布。                                                  |
| **2026-08-29**     | 第 2 格 R0/M25 在 OMP=1 下执行：Technical PASS + Scientific PASS；evidence/output manifests PASS。 |
| **CURRENT**        | 第 2 格 postexec freeze 未创建；停在 LOW freeze gate。                                             |

# 附录 B. 下一 Gate 的最小 PASS / FAIL 标准

## B.1 LOW postexec freeze 必须 PASS

| **序号** | **检查域**       | **PASS 标准**                                                                                     |
|----------|------------------|---------------------------------------------------------------------------------------------------|
| **1**    | Shell / Python   | freeze script bash -n PASS；embedded Python compile PASS。                                        |
| **2**    | Process boundary | 无 R0/M20260825 相关进程；evidence stage 不存在。                                                 |
| **3**    | Immutable inputs | CellSpec V2、regression1、OMP audit、auth、preexec、wrapper、runner、meta、checkpoint exact SHA。 |
| **4**    | Manifests        | B16 V2 / auth / runner / evidence / output sha256sum -c 全 PASS。                                 |
| **5**    | START            | authorization consumed=True；wrapper/auth/preexec/cellspec self-binding PASS；OMP=1。             |
| **6**    | CAPTURE          | classification=TECHNICAL_PASS_SCIENTIFIC_PASS；strict errors=\[\]。                               |
| **7**    | Result identity  | seed=0；model=20260825；budget=16；variant=guided；error=None。                                   |
| **8**    | Science          | 五项 quality predicates 全 True。                                                                 |
| **9**    | Instrumentation  | roots=254；metrics=254；expansions=iterations=4064；forwards=254。                                |
| **10**   | Environment      | OMP_NUM_THREADS=1；environment warnings=\[\]。                                                    |
| **11**   | Matrix           | before=1；after=2；counts_toward=True；remaining=7。                                              |
| **12**   | Publish          | freeze SHA256SUMS PASS；readback PASS；original result/CAPTURE unchanged。                        |

## B.2 任一出现即 HOLD

- 任何 exact SHA 或 manifest mismatch。

- CAPTURE technical_pass=False，或 strict errors 非空。

- runner RC/status 不符合 PASS→0 / FAIL→1。

- roots/metrics/shadow/forward 计数不闭合。

- OMP binding 与 START/CAPTURE 不一致，或第二格出现未记录 warning。

- 目标 freeze root/stage 已存在。

- 冻结过程发生 checkpoint load、model forward、MCTS 或 wrapper reexecution。

| **失败处理** HOLD 只做只读定位；绝对不能重新执行 cell2。若 freeze 脚本自身有 bug，发布新 freeze script namespace，仍读取同一 frozen execution evidence。 |
|----------------------------------------------------------------------------------------------------------------------------------------------------------|

## B.3 freeze 后 CellSpec V3 的最小标准

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>current_matrix_count = 2<br />
required_matrix_count = 9<br />
matrix_remaining = 7<br />
occupied_cells = [[0,20260824], [0,20260825]]<br />
next_cell = [0,20260826]<br />
all_2_cells_pass_identity_regression = True<br />
all_2_cells_pass_budget16_instrumentation_regression = True<br />
all_scientific_fail_cells_preserved = True<br />
next_cell_authorized = False<br />
OMP_NUM_THREADS policy = explicit 1</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 附录 C. 术语与状态解释

| **术语**                          | **含义**                                                                                            |
|-----------------------------------|-----------------------------------------------------------------------------------------------------|
| **Root search**                   | 一次 MCTS 根节点调用；当前每 root 做 1 次 Value forward。                                           |
| **Tree expansion / iteration**    | 当前 budget16 下 technical-valid 结果要求 total iterations = roots × 16，并与 shadow records 闭合。 |
| **Scientific PASS**               | 所有预注册质量谓词满足；不自动等于 production ready。                                               |
| **Scientific FAIL**               | 技术链有效，但至少一个质量谓词为 False；仍计入矩阵。                                                |
| **Technical PASS**                | 身份、执行、artifact、计数、manifest、环境与证据链都满足。                                          |
| **Outer wall-clock**              | metrics 中 outer_elapsed_ms / result outer_search_wallclock_ms_sum；不是 wrapper runner wall。      |
| **Frozen count**                  | 已有 immutable freeze 的矩阵格数。                                                                  |
| **Logical technical-valid count** | CAPTURE 已认定技术有效的格数；当前比 frozen count 多 1。                                            |
| **One-time auth**                 | 只允许一次 process launch；START 写入即消费。                                                       |
| **HOLD**                          | 不代表失败；表示当前证据不足或边界未闭合。                                                          |

| **最终交接结论** 当前项目已经从“神经网络是否介入”推进到“B16 9-cell 稳定性验证”。网络接入、B8 全矩阵和 B16 前两格均有真实 evidence。当前没有算法 blocker，只有一项证据封口任务：LOW 冻结 B16 R0/M20260825。完成 freeze 之前，任何第 3 格执行或 B16 稳定性结论均越界。 |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
