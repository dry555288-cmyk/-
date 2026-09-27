**MineSim-Dynamic**

**全项目阶段性总总结与 AI 无缝接管手册**

**2026-08-27 · Value-guided MCTS 次级 B8 矩阵 1 / 9 完成停点版**

**重点专题：今日 Technical HOLD 链、根因、修复与工程经验教训**

| **当前真实状态** Value V3 独立泛化已冻结 PASS；Pure B8 三个 runtime seeds 全部稳定；第一组 Guided B8 已执行并冻结 PASS；第二组 Guided（runtime seed 0 / model seed 20260825）已授权但尚未启动。 |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

**交接版本：V1** \| 适用对象：后续 ChatGPT / Codex / 工程执行人员

正式 repo：/root/MineSim-Dynamic \| 主 evidence root：/root/autodl-tmp/paper1_value_v3_development_only_v1

*证据截止：2026-08-27；截至 FIRST_GUIDED_POSTEXEC_FREEZE + NEXT_GUIDED_AUTH PASS*

**任何晚于本证据截点的 AutoDL 真实输出，均自动优先于本 Word。**

# **0. CURRENT_STATE｜一页接手摘要**

| **字段**                 | **当前值**                                                                                            | **接管解释**                                        |
|--------------------------|-------------------------------------------------------------------------------------------------------|-----------------------------------------------------|
| **EVIDENCE_CUTOFF**      | 2026-08-27；第一组 Guided B8 postexec freeze 已原子发布，第二组 Guided authorization 已创建且未消费。 | 最新终端 GATE_RC=0 / SUBSHELL_RC=0                  |
| **CURRENT_STAGE**        | Value-guided MCTS integration efficiency evaluation                                                   | 当前只做预注册的 Guided B8 次级矩阵                 |
| **CURRENT_GATE**         | GUIDED_B8_RUNTIME_SEED0_MODEL_SEED20260825_START_RUN_CAPTURE_FIX6R3                                   | 第二个 9 组合条件，尚未启动                         |
| **CURRENT_STATUS**       | Guided B8 completed = 1 / 9                                                                           | 第 1 组 frozen PASS；第 2 组 AUTHORIZED_NOT_STARTED |
| **LATEST_GIT_HEAD**      | 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e                                                              | tracked Git clean                                   |
| **LATEST_FROZEN_RESULT** | GUIDED_B8_RUNTIME_SEED0_MODEL_SEED20260824                                                            | 技术 PASS + 五项质量 PASS + 禁止重跑                |
| **PRIMARY_SCIENCE**      | Lower-budget criterion = SCIENTIFIC FAIL                                                              | Pure minimum stable budget 已是 prereg 最低 B8      |
| **SECONDARY_SCIENCE**    | Tree expansions / outer wall-clock = NOT_EVALUATED                                                    | 必须完成 9 个 Guided B8 条件后统一判定              |
| **NEXT_MINIMAL_ACTION**  | 先用 LOW 派生并验证第二组 START→RUN→CAPTURE wrapper；随后 HIGH-CPU 仅执行该一组。                     | 不要批量生成或并行跑余下 8 组                       |
| **RESOURCE_REQUIRED**    | LOW → HIGH-CPU；GPU 不需要                                                                            | 未来执行保持 CUDA_VISIBLE_DEVICES=""                |
| **DO_NOT_REPEAT**        | 所有 2356 training、C01 forward、Pure B8 seeds 0/1/2、第一组 Guided                                   | one-time / valid run 均不可重跑                     |
| **HOLD**                 | 完整 Guided B8 次级矩阵、最终 expansion/wall-clock 结论、production claims                            | 缺证据不得补齐                                      |

| **当前停点的最短描述** Value V3 已证明在 C01 独立场景上泛化有效；Pure B8 已稳定；“降低最低稳定预算”主判据因预注册预算下限而科学失败；Guided B8 次级矩阵完成 1/9，下一组已授权未启动。 |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

## **0.1 60 秒科学口径**

- 神经网络有用：C01 三个固定 final-model seeds 的 normalized regret 为 0.099474704 / 0.155963166 / 0.105839497，中位数 0.105839497，严格优于 frozen immediate baseline 0.295195862；INDEPENDENT_GENERALIZATION_PASS=True。

- Pure B8 已在 runtime seeds 0/1/2 全部技术有效且五项质量谓词全过，因此 pure minimum stable budget = 8。

- 预注册 budget ladder 是 \[8,16,32,64\]；Guided 不可能取得 \<8 的 minimum stable budget，所以 primary lower-budget criterion 是真实 Scientific FAIL，不允许事后增加 B4/B2。

- 第一组 Guided B8 已 PASS：308 roots、2464 tree expansions、308 Value forwards；但单组结果不能替代 9 条矩阵的最终统计。

- 当前不允许宣称“神经网络已证明降低搜索开销”或“wall-clock speedup 已证明”；这两项仍是 NOT_EVALUATED。

## **0.2 当前目录与授权状态**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>CURRENT_EVIDENCE_ROOT=/root/autodl-tmp/paper1_value_v3_development_only_v1<br />
FIX6R3_ROOT=.../value_guided_mcts_c01_secondary_b8_guided_binding_fix6r3_v1<br />
FIRST_GUIDED_FREEZE=.../value_guided_mcts_c01_secondary_b8_guided_r0_m20260824_postexec_freeze_fix6r3_v1<br />
NEXT_GUIDED_AUTH=.../value_guided_mcts_c01_secondary_b8_guided_r0_m20260825_authorization_fix6r3_v1<br />
NEXT_GUIDED_OUTPUT=.../value_guided_mcts_c01_secondary_b8_guided_execution_fix6r3_v1/guided_budget8_runtime_seed0_model_seed20260825<br />
NEXT_GUIDED_EVIDENCE=.../value_guided_mcts_c01_secondary_b8_guided_r0_m20260825_execution_evidence_fix6r3_v1</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# **目录与推荐阅读顺序**

1.  0\. CURRENT_STATE｜一页接手摘要

2.  1\. 文档控制、证据等级与交接边界

3.  2\. 项目长期主线总览

4.  3\. MineSim 运行架构与永久科学边界

5.  4\. 神经网络主线：Value V3 development → C01 independent PASS

6.  5\. Value-guided MCTS 预注册与 Pure B8 baseline

7.  6\. Guided B8 当前进度与第一组正式结果

8.  7\. 今日错误总览：全部 Technical HOLD 与唯一 Scientific FAIL

9.  8\. 今日错误逐项复盘（现象→原因→处理→证据→禁忌）

10. 9\. 由今日错误固化出的新工程标准

11. 10\. 关键路径、SHA 与状态矩阵

12. 11\. 资源、协作、文件与 Git 工作流

13. 12\. DO_NOT_REPEAT / HOLD / 不可回退项

14. 13\. 云端文档、失败 stage 与删除情况

15. 14\. 快速接手区

16. 附录 A. 今日错误时间线

17. 附录 B. 下一 Gate 的最小 PASS / FAIL 标准

| **推荐阅读** 新 AI 先读第 0、6、7、8、14 节；只有出现 SHA 或 provenance 冲突时，再回查第 2～5 节。 |
|----------------------------------------------------------------------------------------------------|

# **1. 文档控制、证据等级与交接边界**

## **1.1 事实优先级**

本版严格遵循以下证据优先级：

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>当前 AutoDL 终端真实输出 / 当前 Git / 当前源码 / 实际运行结果 / SHA<br />
&gt; frozen result / manifest / lock / START / CAPTURE / bundle<br />
&gt; 本交接 Word<br />
&gt; 历史交接文档<br />
&gt; 设计计划<br />
&gt; AI 记忆</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

- 文件名包含 PASS / final / freeze 不等于真正通过；必须结合 RC、JSON、log、SHA、manifest、gate。

- 历史交接文档中的“当前状态”已被本版覆盖；历史文档只保留 provenance。

- 缺少直接证据的一律写 HOLD / NOT VERIFIED，不用常识补齐。

## **1.2 本版主要证据源**

| **证据**                                          | **用途**                                                                          | **等级**             |
|---------------------------------------------------|-----------------------------------------------------------------------------------|----------------------|
| **最新 AutoDL 终端：第一组 Guided 正式执行**      | 证明 STRICT prestart PASS、START 写入、runner RC=0、27 秒、CAPTURE 与 checksums。 | 最高                 |
| **最新 AutoDL 终端：第一组 freeze + 第二组 auth** | 证明第一组已 frozen；第二组 AUTHORIZED_NOT_STARTED。                              | 最高                 |
| **Value V3 C01 forward freeze**                   | 证明 independent generalization PASS、3 seed regret、baseline 与 freeze SHA。     | 冻结                 |
| **Pure B8 seed0/1/2 freeze + stability decision** | 证明 Pure B8 stable、minimum stable budget=8、主判据科学失败。                    | 冻结                 |
| **FIX6R3 static repair + auth**                   | 证明 Guided binding 仅新增；Search/Reward/UCT/rollout/backup 等不变。             | 冻结                 |
| **2026-08-26 最新前序 handoff**                   | 提供 MineSim→FullMine→Fleet-MCTS 历史主线和历史路径。                             | 历史                 |
| **2026-08-25 Value V3 handoff**                   | 提供 2356-root 训练协议、12D features、9-fold development 结果。                  | 历史/冻结 provenance |

## **1.3 本版不做的事情**

- 不执行 AutoDL 全盘 live inventory；因此本 Word 是否已同步到 AutoDL 仍为 HOLD。

- 不重新读取或重跑已冻结实验。

- 不根据第一组 Guided 单点结果提前做 9 条矩阵结论。

- 不把今天的 Technical HOLD 误写成模型或算法 Scientific FAIL。

# **2. 项目长期主线总览（按真实演进组织）**

| **阶段**                 | **状态**          | **当前真实结论**                                                                        |
|--------------------------|-------------------|-----------------------------------------------------------------------------------------|
| **MineSim 复现**         | PASS / FROZEN     | IDM baseline、replay、closed-loop 基础环境已建立；无需重做。                            |
| **蒙特卡洛 / Pure MCTS** | PASS / FROZEN     | 真实 MineSim online closed-loop；search/reward/trajectory adapter/controller 链已跑通。 |
| **单车**                 | PASS / FROZEN     | J117 423-step 单车与 FullMine representative Pure MCTS 3/3。                            |
| **双车冲突场景**         | PASS / FROZEN     | NO-MCTS causal conflict、双受控运行边界与真实冲突场景。                                 |
| **FullMine 新地图**      | PASS / FROZEN     | Vector V2 semantic + Vector V4 bitmap/runtime/planner；Research/DEV 口径。              |
| **Fleet-MCTS**           | PASS + 负结果并存 | Polygon21 5/5；C04/C06 成功；C11 安全死锁负结果保留。                                   |
| **多种子 / cross-scene** | FROZEN            | C04/C11/C06 development collection、blind protocol、C01 独立场景。                      |
| **原生可视化**           | PASS / 部分 HOLD  | Native Video V2 final；部分 showcase 历史未完全收口。                                   |
| **云端整理**             | PASS / COMPLETE   | 历史证据为 move/isolate/archive；科研文件 actual delete=0。                             |
| **神经网络**             | CURRENT           | Value V3 independent PASS；Pure B8 stable；Guided B8 matrix 1/9。                       |

## **2.1 历史阶段无需重做的原因**

- MineSim/Pure MCTS/单车/双车/FullMine/Fleet-MCTS 相关历史阶段已经有真实 runtime、结果与 handoff；当前只在神经网络接入链推进。

- C11 安全死锁等负结果属于真实科学证据，不能因后续神经网络进展而删除或重解释。

- FullMine 仍是 Research/DEV map，不得表述为官方生产级 HD Map 或 authoritative drivability truth。

# **3. MineSim 运行架构与永久科学边界**

## **3.1 主运行链**

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
→ Planner.compute_planner_trajectory()<br />
→ MCTS / Fleet-MCTS search<br />
→ Trajectory Adapter<br />
→ TwoStageController.update_state()<br />
→ LQR / iLQR trajectory tracking<br />
→ KinematicBicycleModel.propagate_state()<br />
→ Agent Update Policy / Observation<br />
→ SimulationHistory / metrics / log<br />
→ next frame</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## **3.2 故障分层纪律**

| **边界**                         | **固定处理规则**                                                                  |
|----------------------------------|-----------------------------------------------------------------------------------|
| **Planner 与执行器**             | 搜索/规划轨迹合法不等于 Controller/KBM 可实现；必须分层。                         |
| **双车 truth**                   | B 的真实状态不得由 A history 推断；每辆 controlled ego 独立 observation/history。 |
| **Controlled vs external actor** | 同一车辆不能同时作为 controlled ego 与 external actor。                           |
| **空间相交 vs 时间冲突**         | 几何路径相交不自动等于 temporal conflict；需要 NO-MCTS causal evidence。          |
| **Safe vs success**              | 无碰撞不等于任务完成；deadlock 可是 Scientific FAIL。                             |
| **Static truth**                 | frozen V4 bitmap + XG90G footprint 为 primary；CollisionLookup 仅 secondary。     |
| **Safety sidecar**               | V2V/V2R/risk/shadow/safe-node 若仅 diagnostic，不得写成 hard constraint。         |

# **4. 神经网络主线：Value V3 development → C01 independent PASS**

## **4.1 Value V2 与 Value V3 的边界**

- Value V2 在 C03 independent validation 上 Scientific FAIL，已关闭为 DO_NOT_INTEGRATE；不得重跑或 retune。

- Value V3 通过 coverage expansion、2356-root episode-aware LOSO 与 3 个 fixed final full-development models，形成新的 development candidate。

## **4.2 2356-root 冻结协议**

| **项目**             | **冻结值**                                                                        |
|----------------------|-----------------------------------------------------------------------------------|
| **Dataset**          | 2356 roots；37696 action rows；6 episodes；identity=(scene,episode_uid,root_step) |
| **Architecture**     | 12 → 64 → 64 → 16；ActionConditionedValueV3PairwiseRank                           |
| **Objective**        | ROOT_NORMALIZED_WEIGHTED_PAIRWISE_LOGISTIC                                        |
| **Split**            | LEAVE_ONE_SCENE_OUT                                                               |
| **Seeds**            | 20260824 / 20260825 / 20260826                                                    |
| **Epochs / LR**      | 600 / 0.001                                                                       |
| **Best-seed / HPO**  | False / False                                                                     |
| **Output semantics** | 16 joint-action scores；joint_action_index=A\*4+B                                 |

## **4.3 Development 结果**

| **Scene** | **3-seed median regret** | **Frozen immediate baseline** | **结论** |
|-----------|--------------------------|-------------------------------|----------|
| **C04**   | 0.174277542              | 0.273804418                   | PASS     |
| **C11**   | 0.117458957              | 0.181778548                   | PASS     |
| **C06**   | 0.122468490              | 0.241806713                   | PASS     |

- VALUE_V3_SCENE_WIN_COUNT=3；DEVELOPMENT_READY=True。

## **4.4 C01 独立评价**

| **对象**                 | **值**                                          | **状态/边界**      |
|--------------------------|-------------------------------------------------|--------------------|
| **C01 dataset**          | 151 roots；state=(151,12)，Q/immediate=(151,16) | FROZEN             |
| **Immediate baseline**   | 0.2951958615926099                              | FROZEN             |
| **Seed 20260824 regret** | 0.09947470394112914                             | FROZEN             |
| **Seed 20260825 regret** | 0.15596316637663826                             | FROZEN             |
| **Seed 20260826 regret** | 0.10583949665541333                             | FROZEN             |
| **Median**               | 0.10583949665541333                             | STRICT \< baseline |
| **Classification**       | INDEPENDENT_GENERALIZATION_PASS                 | FROZEN PASS        |
| **Forward rerun**        | False                                           | One-time consumed  |

| **科学结论** 神经网络已经在独立 C01 上证明动作价值排序有用；但这不等于 production ready，也不等于 MCTS efficiency 已证明。 |
|----------------------------------------------------------------------------------------------------------------------------|

## **4.5 关键冻结 SHA**

| **对象**                        | **SHA256**                                                       |
|---------------------------------|------------------------------------------------------------------|
| **Final checkpoint 20260824**   | 496e4259eb9801f3ce70c1094be12fd0985cb03e97d606cade8dfbe9d5228633 |
| **Final checkpoint 20260825**   | 5df90947a5fdd2bc6aa525ca5eba78b6379e127e5df6ca1d0362c992caab73b5 |
| **Final checkpoint 20260826**   | 3881d39c09b02a513e44f0fe612aad42de9ff636fd07e314d327b4c6d5f132df |
| **C01 forward postexec freeze** | 254dfee4b6e92da7078dd22a58a6101e448ebe549b2b041fa706630a9143e885 |
| **C01 frozen result snapshot**  | 37795d6fb329e56a6c5c80cf6863ca86fde1bca976fbcad58862c62aa1886834 |

# **5. Value-guided MCTS 预注册与 Pure B8 baseline**

## **5.1 Guided 接入的冻结设计**

- Value 仅用于 root depth=0 的 joint-action ordering。

- 每个 root 只允许 1 次 score_12d forward；tree search 内不允许额外 forward。

- hard pruning=False；PUCT=False；UCT formula、rollout、backup、reward、transition、action provider 均不改变。

- Guided model seeds 固定为 20260824/20260825/20260826；runtime MCTS seeds 固定为 0/1/2。

- Preregistered budget ladder 固定为 \[8,16,32,64\]。

## **5.2 Pure B8 三个 runtime seeds**

| **Runtime seed** | **Root searches** | **Iterations** | **Tree expansions** | **Runner wall** | **质量** |
|------------------|-------------------|----------------|---------------------|-----------------|----------|
| **0**            | 453               | 3624           | 3624                | 34 s            | PASS     |
| **1**            | 429               | 3432           | 3432                | 31 s            | PASS     |
| **2**            | 341               | 2728           | 2728                | 26 s            | PASS     |

- 三个 seeds 均五项 quality predicates 全部为 True。

- PURE_B8_STABLE=True；PURE_MIN_STABLE_BUDGET=8。

## **5.3 主判据的真实科学失败**

| **Scientific FAIL（不是 Bug）** 预注册主判据要求 guided_min \< pure_min 且 Pure 在 guided_min 不稳定。由于 Pure 在全局最低 prereg budget B8 已稳定，Guided 无法取得 \<8；故 PRIMARY_LOWER_BUDGET_CRITERION_STATUS=SCIENTIFIC_FAIL_BY_PREREGISTERED_BUDGET_FLOOR。 |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

- 禁止事后新增 B4/B2。

- 禁止把该科学失败包装为 technical retry。

- SEARCH_COMPUTE_REDUCTION_PROVEN=False。

# **6. Guided B8 当前进度与第一组正式结果**

## **6.1 FIX6R3 接入边界**

| **对象**                                     | **冻结值**                                                       |
|----------------------------------------------|------------------------------------------------------------------|
| **FIX6R3 runner SHA**                        | ea4d7f21265be0b2409cc2b25e6f1bd2c7ad49317d593929a34752d286d5eb79 |
| **FIX6R3 meta SHA**                          | c0e1520d81ddc1b36c1e56078e2dbf1ea50c1cd6a0f2e9ad59adef5ccd25464c |
| **Pure binding changed**                     | False                                                            |
| **Guided binding added**                     | True                                                             |
| **Frozen factory reused**                    | True                                                             |
| **Search/Reward/UCT/Rollout/Backup changed** | False                                                            |

## **6.2 第一组 Guided 正式结果**

| **字段**                        | **结果**                                   |
|---------------------------------|--------------------------------------------|
| **Condition**                   | GUIDED_B8_RUNTIME_SEED0_MODEL_SEED20260824 |
| **Runner RC / wall**            | 0 / 27 s                                   |
| **Root searches**               | 308                                        |
| **MCTS iterations**             | 2464                                       |
| **Tree expansions**             | 2464                                       |
| **Value forwards**              | 308（每 root 恰好 1 次）                   |
| **Value inference sum**         | 43.11761260032654 ms                       |
| **Outer search wall-clock sum** | 6125.535920262337 ms                       |
| **Quality predicates**          | 5 / 5 True                                 |
| **Matrix accounting**           | counts=True；must_not_be_rerun=True        |

## **6.3 当前矩阵与下一授权**

| **组合**           | **状态**               | **进度** | **关键 SHA/边界**                                                     |
|--------------------|------------------------|----------|-----------------------------------------------------------------------|
| **r0 / m20260824** | FROZEN PASS            | 1 / 9    | b475d8ed0011a29582504acbe7bcb831a8227dda0ef5a40d5fe03b8efa4d30c4      |
| **r0 / m20260825** | AUTHORIZED_NOT_STARTED | next     | auth=ad49eeaa26ad46176189b220700ace7663a269dfc1a9bb5f2b7496959afdcaa1 |
| **其余 7 组**      | NOT AUTHORIZED         | pending  | 不得提前批量启动                                                      |

- 第二组 preexec review SHA=f29887e2e47f51b53262427422bc5f2137fc0cb7fb7ebf2f20be471379b1f417。

- 第二组 checkpoint SHA=5df90947a5fdd2bc6aa525ca5eba78b6379e127e5df6ca1d0362c992caab73b5。

- 第二组 authorization consumed=False；checkpoint_loaded=False；model_forward=False；MCTS=False。

# **7. 今日错误总览：全部 Technical HOLD 与唯一 Scientific FAIL**

| **核心判断** 今天大量报错的主体不是网络或 MCTS 科学失败，而是 Gate、wrapper、静态检查器和诊断代码自身的错误假设。真正科学失败只有“lower-budget criterion 因 prereg budget floor 不可能成立”。 |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

| **ID**  | **阶段**                     | **现象**                                           | **分类/边界**                    | **根因**                              |
|---------|------------------------------|----------------------------------------------------|----------------------------------|---------------------------------------|
| **E01** | Exact metric loader          | RETURNED_CALLABLE_NOT_IDENTIFIED                   | Pre-runtime；未执行模型          | 返回 local fn，审计未解析 dataflow    |
| **E02** | Development regression       | C04 exact mismatch ~3.8e-10                        | Pre-runtime；未改 science        | 浮点重算与 frozen 文本值微差          |
| **E03** | Forward harness audit        | EXPECTED_MODEL_CLASS_NOT_FOUND                     | Pre-runtime                      | 错误假设模型必须是顶层 class          |
| **E04** | Initial benchmark            | NameError: args not defined                        | Runtime technical；0 MCTS        | 在 parse_args 前使用 args             |
| **E05** | Pure zero-search diagnostics | search.\_shadow_records / \_root_records NameError | Runtime technical；auth consumed | 诊断尾部无条件访问未绑定 search       |
| **E06** | Pure finalize                | search.finalize_episode NameError                  | Runtime technical；auth consumed | 同一 zero-search 安全问题未穷举       |
| **E07** | Root-cause reveal            | 原始 search 未绑定                                 | Runtime technical；0 roots       | Pure constructor 丢失                 |
| **E08** | FIX5 static                  | AssertionError                                     | Pre-runtime                      | 源码字符串比较受缩进/格式影响         |
| **E09** | FIX5 strict wrapper          | KeyError: fix5r1_search_store_count                | Pre-START；auth 未消费           | schema key 版本未同步                 |
| **E10** | Seed2 freeze                 | prereg file No such file                           | Pre-runtime                      | 文件名漏写 AND                        |
| **E11** | Guided FIX6                  | factory ordering assertion                         | Pre-runtime                      | 未先检查真实 top-level order          |
| **E12** | Guided FIX6R1                | ast.Assign has no lineno                           | Pre-runtime                      | synthetic AST 直接 unparse            |
| **E13** | Guided FIX6R2                | Pure binding count=0                               | Pre-runtime                      | ast.unparse 单双引号格式敏感          |
| **E14** | Guided exec R0               | STATIC_FIX6_PASS vs STATIC_FIX6R3_PASS             | Pre-START；auth 未消费           | 版本化 status stale                   |
| **E15** | Guided exec R1               | checkpoint path substring assert                   | Pre-START；auth 未消费           | 源码由相邻字符串拼接                  |
| **E16** | Guided exec R2               | RuntimeError sentinel missing                      | Pre-START；auth 未消费           | sentinel 位于 tuple 参数中            |
| **E17** | 文件传输                     | 脚本 No such file                                  | 操作层；无科学影响               | Chat artifact 未完成上传 AutoDL       |
| **E18** | Shell 启动噪声               | codex-env.sh missing                               | 非 blocker                       | profile 引用缺失，与 minesim 激活无关 |

## **7.1 授权是否被消费：今天最重要的区分**

| **情况**                                       | **authorization consumed?** | **后续规则**                                                     |
|------------------------------------------------|-----------------------------|------------------------------------------------------------------|
| **Preflight/static assertion 在 START 前失败** | 否                          | 可以修 checker/wrapper 后继续使用同一授权                        |
| **START 写入后 runner 技术失败**               | 是                          | 必须冻结失败证据并新建 separate technical recovery authorization |
| **技术有效但科学质量 FAIL**                    | 是                          | 是真实科学结果，必须保留，禁止重跑挑结果                         |
| **技术有效且科学 PASS**                        | 是                          | 立即 freeze，禁止重复“确认”                                      |

# **8. 今日错误逐项复盘（经验教训重点）**

## **8.1 Exact metric loader：返回 local fn，审计误判“未知 callable”**

| **项目**         | **内容**                                                                                                            |
|------------------|---------------------------------------------------------------------------------------------------------------------|
| **现象**         | load_exact_metric_closure() 明确 return fn，但 RETURNED_CALLABLE_NAME=None，随后 RETURNED_CALLABLE_NOT_IDENTIFIED。 |
| **定性**         | Pre-runtime Technical HOLD；未消费模型/实验授权。                                                                   |
| **根因**         | 审计只看返回表达式名字，没有继续解析 fn = ns\["ranking_metrics"\] 的局部数据流。                                    |
| **排查过程**     | 读取 loader AST、返回表达式、局部赋值和 exec namespace，确认 fn 唯一绑定到 ranking_metrics。                        |
| **最终处理**     | FIX1 将 local symbol fn 解析回 ns\["ranking_metrics"\]，再审计 exact 3-parameter source/call-site/return contract。 |
| **证据**         | EXACT_3PARAM_SOURCE_CALLSITE_RETURN_CONTRACT_AUDIT=PASS；模型、训练、MCTS 均未执行。                                |
| **以后禁止重复** | 任何 loader/factory 审计必须做返回值 dataflow，不得靠 \_\_name\_\_ 或表面变量名。                                   |

## **8.2 Frozen development baseline 的 10^-10 级差异**

| **项目**         | **内容**                                                                                                                            |
|------------------|-------------------------------------------------------------------------------------------------------------------------------------|
| **现象**         | C04 runtime recomputation=0.27380441852621284，而 pretrain frozen=0.27380441814439227，脚本用 bit-exact float equality 直接失败。   |
| **定性**         | Pre-runtime Technical HOLD；无科学结果改变。                                                                                        |
| **根因**         | 相同科学口径在不同计算路径/序列化中产生约 3.8×10^-10 的浮点差；不是 metric 语义改变。                                               |
| **排查过程**     | 保留 pretrain frozen anchor，同时计算 runtime exact metric；对 C04/C11/C06 做 dual-anchor regression，并记录最大绝对差。            |
| **最终处理**     | 不修改 prereg tolerance、不替换 frozen baseline；冻结 runtime-vs-pretrain delta，最终 MAX_ABS_DELTA≈4.87×10^-10，dual-anchor PASS。 |
| **证据**         | DEVELOPMENT_DUAL_ANCHOR_REGRESSION=PASS；PRETRAIN_FROZEN_BASELINE_REPLACED=False。                                                  |
| **以后禁止重复** | 冻结科学数值不能因小数格式差异而被覆盖；也不能事后随意加 tolerance。应预先定义 dual-anchor/ULP policy。                             |

## **8.3 Model factory 审计：错误假设“必须存在顶层模型类”**

| **项目**         | **内容**                                                                                            |
|------------------|-----------------------------------------------------------------------------------------------------|
| **现象**         | FINAL_HARNESS_CLASS_NAMES=\[\]，审计抛 EXPECTED_MODEL_CLASS_NOT_FOUND。                             |
| **定性**         | Pre-runtime Technical HOLD；未加载 checkpoint。                                                     |
| **根因**         | 真实 harness 通过 build_model() 工厂构建网络，模型类不是 top-level ClassDef。                       |
| **排查过程**     | 检查 function definitions、build_model body、checkpoint schema 与训练 harness 的 factory contract。 |
| **最终处理**     | 改为 recursive model factory audit，而不是顶层 class 名审计。                                       |
| **证据**         | MODEL_FACTORY_AND_CHECKPOINT_CONTRACT_AUDIT=PASS；TORCH_LOAD_EXECUTED=False。                       |
| **以后禁止重复** | 模型 provenance 应审计构造路径、state_dict schema 和调用点；不要把代码组织形式当科学协议。          |

## **8.4 Parameterized benchmark 首次运行：args 在 parse_args 前使用**

| **项目**         | **内容**                                                                                                  |
|------------------|-----------------------------------------------------------------------------------------------------------|
| **现象**         | runner 在 RESULT_DIR = Path(args.output_root) 处 NameError: args is not defined；0 roots、Guided 未启动。 |
| **定性**         | Runtime Technical FAIL；START 后授权已消费，需 separate recovery。                                        |
| **根因**         | 派生 runner 的 argparse block 顺序错误或缺失，模块顶层先使用 args。                                       |
| **排查过程**     | 读取 traceback line 159 与 source context，确认 failure 在任何 MCTS/search 前。                           |
| **最终处理**     | 独立 technical recovery 修复 argv/parse order；不复用原失败授权。                                         |
| **证据**         | PURE_RUNNER_RC=1；PROCESS_LAUNCH_COUNT=1；SCIENTIFIC_OUTCOMES_OBSERVED=False。                            |
| **以后禁止重复** | 任何 CLI 派生脚本必须先跑 --help / parse_args smoke，并做 top-level use-before-def AST 检查。             |

## **8.5 Diagnostic wrapper 连续遮蔽原始 search 未绑定错误**

| **项目**         | **内容**                                                                                                                                                           |
|------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **现象**         | FIX2 在 total_tree_expansions/root_record_count 读取 search.\_shadow_records/\_root_records 时 NameError；FIX3 又在 search.finalize_episode(result) 处 NameError。 |
| **定性**         | Runtime Technical FAIL；FIX2/FIX3/FIX4 授权均已消费，不计科学矩阵。                                                                                                |
| **根因**         | zero-search 路径中 search 从未绑定；诊断尾部却假设 search 一定存在。每次只修一个暴露点，没有一次穷举全部 post-zero-search 引用。                                   |
| **排查过程**     | 冻结每次失败 stage；扫描 BENCHMARK_ZERO_SEARCH 之后所有 search Load；统计 guarded/unconditional references。                                                       |
| **最终处理**     | FIX4 对计数和 finalize 全部 zero-search guard，并把 result write 放到 deliberate re-raise 前，最终保留 original caught error。                                     |
| **证据**         | FIX4 result 显示 steps=0、root_search_count=0、total_mcts_iterations=0，原始错误为 NameError: search not defined。                                                 |
| **以后禁止重复** | 诊断代码不能覆盖原异常；一旦出现 zero-search，应一次性穷举所有后处理对象访问，而非“报一个修一个”。                                                                 |

## **8.6 Pure 真正根因：search constructor 丢失**

| **项目**         | **内容**                                                                                                                       |
|------------------|--------------------------------------------------------------------------------------------------------------------------------|
| **现象**         | FIX4 成功揭示原始错误：第一次 search.search() 前 search 无 Store，root_search_count=0。                                        |
| **定性**         | 原始根因是 Runtime Technical FAIL，不是 MCTS 科学失败。                                                                        |
| **根因**         | 派生 benchmark runner 未恢复冻结 parent 的 search = RootDiagnosticCollectorFleetMCTSSearchV1(...) 构造链。                     |
| **排查过程**     | 按 SHA 定位 frozen parent，检查 search Store count、guard、constructor args 与首次 use 的控制流。                              |
| **最终处理**     | FIX5R1 仅恢复 Pure binding；全部 constructor 参数原样复用，只把 class 替换为 InstrumentedPureRootDiagnosticFleetMCTSSearchV1。 |
| **证据**         | FIX4_SEARCH_STORE_COUNT=0；FIX5R1_SEARCH_STORE_COUNT=1；SEARCH_STORE_PRECEDES_FIRST_SEARCH_USE=True。                          |
| **以后禁止重复** | 任何派生 runner 必须做“definition dominance”检查：每个可能分支都要在首次 use 前绑定核心对象。                                  |

## **8.7 FIX5 静态修复第一次失败：源码字符串等价过严**

| **项目**         | **内容**                                                                                         |
|------------------|--------------------------------------------------------------------------------------------------|
| **现象**         | CREATE ROOT-CAUSE FREEZE + FIX5 在 constructor 参数比对处 AssertionError。                       |
| **定性**         | Pre-runtime Technical HOLD；未执行 MCTS。                                                        |
| **根因**         | 插入 if 后缩进/格式改变，源码 segment 字符串不同，但 AST 语义相同。                              |
| **排查过程**     | 对 parent/fixed constructor args 和 kwargs 做 ast.dump(include_attributes=False) 比较。          |
| **最终处理**     | FIX5R1 使用 AST structural parity；失败 FIX5 stage 保留不删除。                                  |
| **证据**         | PARENT_CONSTRUCTOR_ARGUMENTS_EXACTLY_REUSED=True；ONLY_CONSTRUCTOR_CLASS_NAME_CHANGED=True。     |
| **以后禁止重复** | 语义相等不要用原始 source string equality；格式敏感审计应降级为 AST 或 canonical serialization。 |

## **8.8 Versioned schema/key stale：fix5r1_search_store_count 与 STATIC_FIX6_PASS**

| **项目**         | **内容**                                                                                                                                       |
|------------------|------------------------------------------------------------------------------------------------------------------------------------------------|
| **现象**         | FIX5R1 strict wrapper 读取不存在的 fix5r1_search_store_count；首次 Guided wrapper 又要求 STATIC_FIX6_PASS，而 meta 实际为 STATIC_FIX6R3_PASS。 |
| **定性**         | Pre-START Technical HOLD；authorization 未消费。                                                                                               |
| **根因**         | 生成器版本化了 schema/status，但执行 wrapper 使用手写旧 key/旧 status。                                                                        |
| **排查过程**     | 从生成脚本静态抽取 meta/auth/review 字面量叶子；对执行 wrapper 的断言逐项对账。                                                                |
| **最终处理**     | 建立 generator-executor literal contract reconciliation；首次 Guided wrapper完成 41 项检查、0 mismatch。                                       |
| **证据**         | PRESTART_GENERATOR_EXECUTOR_CONTRACT_RECONCILIATION=PASS；FIX6R3_AUTH_META_CHECKPOINT_CROSS_BINDING=PASS。                                     |
| **以后禁止重复** | 禁止复制旧版本 status/key；版本化 artifact 必须由生成端导出 schema 或自动生成 readback。                                                       |

## **8.9 Preregistration 文件名漏写 AND**

| **项目**         | **内容**                                                                                              |
|------------------|-------------------------------------------------------------------------------------------------------|
| **现象**         | Seed2 postexec freeze 在 exact SHA gate 后直接 SUBSHELL_RC=1；目标 prereg 文件不存在。                |
| **定性**         | Pre-runtime Technical HOLD；Seed2 科学执行不受影响、不得重跑。                                        |
| **根因**         | 脚本写成 INTEGRATION_EFFICIENCY，而真实冻结文件是 INTEGRATION_AND_EFFICIENCY。                        |
| **排查过程**     | 核对 prereg root SHA256SUMS 与正式文件名。                                                            |
| **最终处理**     | R1 使用 exact filename，并增加整个 prereg root checksum 与递归内容 contract scan。                    |
| **证据**         | PREREGISTRATION_ROOT_SHA256SUMS_VERIFY=PASS；budget ladder / runtime seeds / model seeds 均读取成功。 |
| **以后禁止重复** | 路径和文件名不得凭记忆拼接；从 manifest/list/readback 获取 exact basename。                           |

## **8.10 Guided FIX6 三连错：顺序、synthetic AST、引号**

| **项目**         | **内容**                                                                                                                                                                |
|------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **现象**         | FIX6 错误断言 factory 在 Pure binding 前；FIX6R1 对无 lineno 的 synthetic ast.Assign 调 ast.unparse；FIX6R2 用 ast.unparse 文本与双引号字符串比较导致 binding count=0。 |
| **定性**         | 均为 Pre-runtime Technical HOLD；无 checkpoint/forward/MCTS。                                                                                                           |
| **根因**         | 分别属于错误控制流假设、AST location metadata 缺失、格式敏感字符串比较。                                                                                                |
| **排查过程**     | 重建真实 top-level order；改为 exact Pure source reuse 只替换 callable token；variant 条件用 AST Compare 语义匹配。                                                     |
| **最终处理**     | FIX6R3：Pure binding 不动；Guided binding 插在 factory/checkpoint map 后、首次 search use 前；只新增一个 top-level Guided If。                                          |
| **证据**         | VARIANT_CONDITION_MATCHING=AST_SEMANTIC_QUOTE_INVARIANT；FIX6R3_STATIC_REPAIR=PASS。                                                                                    |
| **以后禁止重复** | AST 也会脆弱：synthetic node 需 fix_missing_locations；条件识别不得依赖 ast.unparse 的引号/空格。                                                                       |

## **8.11 Guided strict wrapper：checkpoint path raw substring 与 nested tuple sentinel**

| **项目**         | **内容**                                                                                                                                                                          |
|------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **现象**         | R1 用 assert str(ckpt_path) in src 失败；R2 只搜 RuntimeError 的直接字符串参数，漏掉 tuple 内的 VALUE_FORWARD_OCCURRED_INSIDE_TREE_SEARCH。                                       |
| **定性**         | Pre-START Technical HOLD；授权未消费，最终 R3 才消费并 PASS。                                                                                                                     |
| **根因**         | checkpoint 路径由相邻字符串拼接，原始源码没有连续完整路径；sentinel 位于 RuntimeError((sentinel,before,after)) 的 tuple AST。                                                     |
| **排查过程**     | 把 checkpoint map/factory/search/\_expand/scorer 全改成 AST 语义检查；递归遍历 RuntimeError 参数 AST；从 frozen derivation 提取 exact search/scorer source 重放失败点后全部断言。 |
| **最终处理**     | R3 通过全部 prestart，随后正式 Guided 执行 RC=0。                                                                                                                                 |
| **证据**         | remaining_source_format_sensitive_prestart_assertions=0；exact_frozen_search_scorer_all_postfail_assertions_replay=PASS。                                                         |
| **以后禁止重复** | 长 prestart 不能只 compile；必须在 exact frozen artifacts 上 replay 所有断言，尤其是上次失败行之后。                                                                              |

## **8.12 Chat artifact ≠ AutoDL 文件；codex-env.sh 缺失不是当前 blocker**

| **项目**         | **内容**                                                                                                   |
|------------------|------------------------------------------------------------------------------------------------------------|
| **现象**         | 用户多次执行脚本得到 No such file；每次登录还出现 /root/autodl-tmp/codex-env.sh missing。                  |
| **定性**         | 操作层问题；无授权/科学影响。                                                                              |
| **根因**         | 前者是文件尚未上传/复制到 AutoDL；后者是 shell profile 的历史引用缺失，不影响显式 conda activate minesim。 |
| **排查过程**     | 确认脚本出现后再执行；所有正式脚本自身从 /root/MineSim-Dynamic + conda activate minesim 开始。             |
| **最终处理**     | 以后交付时明确“下载/上传完成后 test -f + sha256sum”；不把 profile 噪声当项目错误。                         |
| **证据**         | 实际脚本运行显示 ENV=minesim、Python 3.9.25、Git clean；所以 codex-env.sh 缺失不构成 blocker。             |
| **以后禁止重复** | 聊天里的 sandbox 文件不会自动出现在 AutoDL；No such file 也不等于文件被删除。                              |

# **9. 由今日错误固化出的新工程标准**

## **9.1 Gate / wrapper 也必须被当成待验证的软件**

- bash -n 与 embedded Python compile 只证明语法，不证明断言与真实 artifact 一致。

- 必须增加 generator → executor schema/status/SHA contract reconciliation。

- 必须在 exact frozen source/JSON 上实际 replay prestart assertions，不能只检查脚本文本。

- 任何长 prestart 失败后，下一版必须重放“失败点之后的全部断言”，避免串行暴露新错。

- 脚本需要输出断言阶段 marker，便于从终端准确定位 fault domain。

## **9.2 禁止 source-format-sensitive 审计**

- 禁止用完整路径是否是 source substring 来确认 Path 常量。

- 禁止用 ast.unparse 输出文本识别单双引号、空格或换行。

- 禁止用原始 segment 字符串 equality 判断 constructor 语义等价。

- 优先用 AST Compare / Call / Dict / Subscript / Name / Constant 等节点语义；必要时 canonical dump。

- 如果必须生成 AST，调用 ast.fix_missing_locations；更稳妥的是复用已冻结源码片段，只替换唯一 callable token。

## **9.3 Original error preservation 与 zero-search 安全**

- 诊断/收尾代码必须在 zero-search、zero-root、missing object 下安全。

- 原始 caught exception 必须在任何新 diagnostic exception 之前写入 result。

- 一旦发现 zero-search，应穷举之后全部 search/model/scorer 引用，不能逐个修。

- 技术失败是否消费授权，以 START 是否写入、process 是否启动为界，不以“有没有结果 JSON”判断。

## **9.4 Frozen metric 与浮点策略**

- Metric source、call-site、return schema、baseline 和 PASS operator 必须在 forward 前冻结。

- 不能因 10^-10 级浮点漂移替换 pretrain frozen baseline。

- 也不能事后放宽 tolerance；应使用预先定义的 dual-anchor/ULP/readback policy。

- strict \<、tolerance=0、median aggregation、no best-seed 均是科学协议，不能由 wrapper 自行修改。

## **9.5 Canonical provenance**

- SHA 相同的多个副本中，优先 canonical formal harness path；failed stage 副本只作 provenance，不作默认 parent。

- 文件名、目录名、schema_version、status 必须来自 manifest/readback，不凭记忆。

- Failed stage 统一保留，不删除、不覆盖；新修复使用新不可变 namespace。

## **9.6 新的正式交付验收清单**

| **序号** | **检查域**                  | **PASS 标准**                                      |
|----------|-----------------------------|----------------------------------------------------|
| **1**    | Shell syntax                | bash -n PASS                                       |
| **2**    | Embedded Python             | 每个 heredoc compile PASS                          |
| **3**    | Generator/Executor contract | 所有静态 literal/schema/status/SHA 0 mismatch      |
| **4**    | Exact artifact replay       | 在 frozen source/JSON 上执行 prestart assertions   |
| **5**    | Format sensitivity          | raw-source membership / quote-sensitive checks = 0 |
| **6**    | Control flow                | core object Store dominates first Load/use         |
| **7**    | Authorization boundary      | prestart 全 PASS 后才写 START                      |
| **8**    | Process boundary            | launch count 与 variant 精确；无 hidden launch     |
| **9**    | Capture                     | 无论 science PASS/FAIL 都写 CAPTURE、RC、checksums |
| **10**   | Freeze                      | 有效结果立即 freeze；禁止 rerun                    |

# **10. 关键路径、SHA 与状态矩阵**

## **10.1 当前关键路径**

| **对象**                  | **路径**                                                                                | **作用/边界**                       |
|---------------------------|-----------------------------------------------------------------------------------------|-------------------------------------|
| **正式 repo**             | /root/MineSim-Dynamic                                                                   | Git tracked source                  |
| **主 evidence root**      | /root/autodl-tmp/paper1_value_v3_development_only_v1                                    | 当前神经网络与 integration 主工作区 |
| **C01 forward freeze**    | .../independent_scene_c01_value_v3_forward_postexec_freeze_v1                           | Independent PASS                    |
| **Integration prereg**    | .../value_guided_mcts_c01_integration_efficiency_preregistration_v1                     | Budget/seeds/metrics frozen         |
| **Pure stability root**   | .../value_guided_mcts_c01_pure_b8_seed2_postexec_and_stability_decision_v1              | Pure B8 stable + primary fail       |
| **FIX6R3 root**           | .../value_guided_mcts_c01_secondary_b8_guided_binding_fix6r3_v1                         | Guided runner/meta                  |
| **First Guided evidence** | .../value_guided_mcts_c01_secondary_b8_guided_r0_m20260824_execution_evidence_fix6r3_v1 | START/CAPTURE/stdout/stderr/RC      |
| **First Guided freeze**   | .../value_guided_mcts_c01_secondary_b8_guided_r0_m20260824_postexec_freeze_fix6r3_v1    | FROZEN PASS                         |
| **Next Guided auth**      | .../value_guided_mcts_c01_secondary_b8_guided_r0_m20260825_authorization_fix6r3_v1      | AUTHORIZED_NOT_STARTED              |

## **10.2 当前关键 SHA**

| **对象**                         | **SHA256**                                                       | **状态**               |
|----------------------------------|------------------------------------------------------------------|------------------------|
| **Git HEAD**                     | 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e                         | CLEAN                  |
| **C01 forward freeze**           | 254dfee4b6e92da7078dd22a58a6101e448ebe549b2b041fa706630a9143e885 | FROZEN PASS            |
| **C01 result snapshot**          | 37795d6fb329e56a6c5c80cf6863ca86fde1bca976fbcad58862c62aa1886834 | FROZEN                 |
| **Integration prereg**           | 0ccbded4caa5bbec28c5a6b13fde9d896983dc40f4555753e38dfe5b5e7d04bb | FROZEN                 |
| **Pure B8 stability decision**   | 3e17ef39f066377be2f1344a94c7d3d6eea9f61712fc52f3682218088b25e582 | FROZEN DECISION        |
| **FIX6R3 runner**                | ea4d7f21265be0b2409cc2b25e6f1bd2c7ad49317d593929a34752d286d5eb79 | FROZEN                 |
| **FIX6R3 meta**                  | c0e1520d81ddc1b36c1e56078e2dbf1ea50c1cd6a0f2e9ad59adef5ccd25464c | FROZEN                 |
| **First Guided START**           | 7e7b16304b0918335a8f34d71727586d584a27e2a9c168eeb46b86e5311b3832 | CONSUMED               |
| **First Guided CAPTURE**         | 70a1c48645cd506136a3118da5960de34efc240de60325e5c44dd1a2b7607948 | PASS                   |
| **First Guided postexec freeze** | b475d8ed0011a29582504acbe7bcb831a8227dda0ef5a40d5fe03b8efa4d30c4 | FROZEN PASS            |
| **Next Guided auth**             | ad49eeaa26ad46176189b220700ace7663a269dfc1a9bb5f2b7496959afdcaa1 | AUTHORIZED_NOT_STARTED |
| **Next Guided preexec review**   | f29887e2e47f51b53262427422bc5f2137fc0cb7fb7ebf2f20be471379b1f417 | PASS                   |

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
export PYTHONPATH=/root/MineSim-Dynamic<br />
export PYTHONDONTWRITEBYTECODE=1</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

- GPU 是否禁用按当前 Gate 判断；当前 Guided benchmark 明确 GPU_REQUIRED=False，保持 CUDA_VISIBLE_DEVICES=""。

- 镜像模板版本不等于 minesim conda 环境；以 ENV=minesim、Python 3.9.25 的真实输出为准。

## **11.2 资源判定**

| **等级**     | **适用范围**                                        | **当前判断**            |
|--------------|-----------------------------------------------------|-------------------------|
| **LOW**      | SHA/JSON/AST/schema/py_compile/freeze/auth/document | 当前交接与 wrapper 生成 |
| **HIGH-CPU** | 长 MineSim / Guided B8 one-time run                 | 下一 Guided 条件执行    |
| **HIGH-GPU** | 正式训练或明确 CUDA forward                         | 当前不需要              |

## **11.3 ChatGPT—用户—Codex 分工**

| **角色**    | **职责**                                                                            |
|-------------|-------------------------------------------------------------------------------------|
| **ChatGPT** | 读取证据、判断 Gate、最小 patch/脚本、PASS/FAIL、结果分析、交接文档。               |
| **用户**    | AutoDL 实际执行、控制实例、上传真实输出/结果、授权重大修改/删除/重跑。              |
| **Codex**   | 只用于复杂算法/顽固 Bug/多文件调用链/独立复核；默认 Luna medium，必要时 Terra/Sol。 |

## **11.4 文件与 Git 安全**

- 大文件、日志、结果、bundle 放 /root/autodl-tmp；正式 repo 只保留必要源码。

- 长任务用 terminal/screen、独立 log、RC、START、CAPTURE。

- 未经授权不执行 git reset --hard / git clean -fd / git add .。

- 不原地覆盖 frozen artifact；修复使用新 versioned namespace。

- 不为目录美观删除 failed stage；删除必须走 inventory→checksum→授权→delete→manifest。

- 聊天文件与 AutoDL 文件严格区分；执行前 test -f + sha256sum。

# **12. DO_NOT_REPEAT / HOLD / 不可回退项**

## **12.1 最高优先级禁止事项**

- 禁止重跑 2356-root one-time development training。

- 禁止重跑 3 个 final full-development model training。

- 禁止重跑 C01 one-time forward；不得 best-seed、ensemble、retune。

- 禁止重跑 Pure B8 runtime seeds 0/1/2。

- 禁止重跑第一组 Guided r0/m20260824。

- 禁止删除/覆盖任何 START、CAPTURE、stdout/stderr/rc、checkpoint、result、metrics、SHA256SUMS、freeze。

- 禁止执行旧 FIX2/FIX3/FIX4/FIX5/FIX6 系列失败脚本。

- 禁止事后增加低于 B8 的预算以挽救 lower-budget 主结论。

- 禁止根据单条 Guided 结果宣称 expansion reduction 或 wall-clock speedup。

- 禁止把 Research/DEV map 或 diagnostic safety sidecar 写成 production safety guarantee。

## **12.2 当前 HOLD / NOT PROVEN**

| **对象**                       | **状态**       | **解除条件**                                  |
|--------------------------------|----------------|-----------------------------------------------|
| **Guided B8 matrix**           | 1/9 完成       | 需要余下 8 个 prereg 条件                     |
| **Tree expansion reduction**   | NOT_EVALUATED  | 9 条全部完成后按 frozen aggregation 判定      |
| **Outer wall-clock speedup**   | NOT_EVALUATED  | 同上                                          |
| **Full matrix execution**      | NOT AUTHORIZED | 只允许逐条件最小 Gate                         |
| **Production readiness**       | NOT PROVEN     | 当前仅 proof-of-mechanism / research evidence |
| **Production safety**          | NOT PROVEN     | 当前没有生产级地图/规则/验证                  |
| **AutoDL 最新 Word inventory** | HOLD           | 未执行 live inventory                         |

# **13. 云端文档、失败 stage 与删除情况**

## **13.1 交接文档历史**

| **文档/类别**                                        | **当前定位**                            | **说明**                          |
|------------------------------------------------------|-----------------------------------------|-----------------------------------|
| **2026-08-25 Value V3 2356-root 神经网络交接**       | HISTORICAL / FROZEN training provenance | 训练协议与 development 结果仍有效 |
| **2026-08-26 C01 checker pre-authorization handoff** | HISTORICAL                              | 当前状态已远超 checker preauth    |
| **2026-08-26 C01 exact metric 3-param hold handoff** | HISTORICAL                              | metric/forward 已后续 PASS        |
| **本文件 2026-08-27 Guided B8 1/9 停点版**           | CURRENT                                 | 当前最新权威 handoff              |
| **ChatGPT Conversation/Library copies**              | AVAILABLE / PARTIAL                     | 不等于 AutoDL 已上传              |
| **AutoDL handoff live inventory**                    | HOLD                                    | 本轮未执行                        |

## **13.2 Failed stages 与删除**

- 今天多个 FIX6/FIX6R1/FIX6R2 和前序 recovery stage 被明确 preserve，不删除、不覆盖。

- 历史 cleanup 的直接证据是 move/isolate/archive/quarantine；科研文件 actual delete=0。

- No such file、path absent、Library 无副本都不能推断为“已删除”。

- Failed stage 的完整 live inventory 未在本交接生成时重新执行，故具体数量/全部 PID 路径为 HOLD；已有终端证据中的 stage 路径继续保留。

# **14. 快速接手区（下一位 AI 必须先读）**

| **接手问题**                | **准确答案**                                                                                           |
|-----------------------------|--------------------------------------------------------------------------------------------------------|
| **1. 项目现在做到哪里？**   | Value V3 independent PASS；Pure B8 stable；Guided B8 secondary matrix 1/9。                            |
| **2. 哪些阶段无需重做？**   | MineSim/Pure MCTS/单车/双车/FullMine/Fleet 历史、2356 training、C01 forward、Pure B8、第一组 Guided。  |
| **3. 当前唯一 Gate？**      | 第二组 Guided：runtime seed0 / model seed20260825 的 START→RUN→CAPTURE。                               |
| **4. 正式 repo？**          | /root/MineSim-Dynamic                                                                                  |
| **5. 当前 evidence root？** | /root/autodl-tmp/paper1_value_v3_development_only_v1                                                   |
| **6. Git HEAD？**           | 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e                                                               |
| **7. 必核 SHA？**           | FIX6R3 runner ea4d7f...；meta c0e152...；next auth ad49ee...；review f29887...；checkpoint 5df909...。 |
| **8. 哪些路径不能动？**     | forward freeze、prereg、pure stability、FIX6R3 root、first Guided evidence/freeze、next auth。         |
| **9. 哪些实验禁止重跑？**   | 所有已消费 one-time；尤其 Pure seeds 0/1/2 和 first Guided。                                           |
| **10. 哪些对象 HOLD？**     | 剩余 8 Guided conditions、secondary expansion/wall-clock、production claims。                          |
| **11. 下一步最小行动？**    | LOW：派生并本地 replay 第二组 strict wrapper；HIGH-CPU：只执行该一组。                                 |
| **12. 本步 PASS 标准？**    | prestart contract PASS→START→1 process→RC=0→每 root 1 forward→质量 schema→CAPTURE/checksums。          |
| **13. 当前资源？**          | Wrapper 生成 LOW；实际执行 HIGH-CPU；GPU 不需要。                                                      |
| **14. 开工前 preflight？**  | process absent、output/evidence absent、auth consumed=False、SHA exact、checkpoint exact、Git clean。  |
| **15. FAIL 后停哪里？**     | 若 START 前：修 wrapper，同一 auth 可用；若 START 后：冻结 evidence，不自动重跑，单独 recovery。       |

## **14.1 下一位 AI 的推荐动作顺序**

1\. 读取本节、第 6～9 节。

2\. 确认用户没有在本交接后执行第二组 Guided；若已执行，本 Word 当前状态立即降级为历史快照。

3\. 只读核验 next auth/review/checkpoint/output/evidence namespace。

4\. 从已成功的 STRICT_R3 wrapper 派生第二组，仅改变 model seed、checkpoint、auth/review/output/evidence bindings。

5\. 做 generator-executor contract reconciliation 与 exact frozen source replay。

6\. 用户在 HIGH-CPU 实例运行一次；任何非 0 不自动 retry。

7\. 技术有效后立即 postexec freeze，再授权第三组。

# **附录 A｜今日错误时间线（按发生顺序）**

| **顺序** | **阶段**              | **错误/事件**                         | **最终处理**                              |
|----------|-----------------------|---------------------------------------|-------------------------------------------|
| **1**    | Metric Gate           | returned callable local symbol 未解析 | FIX1 dataflow audit                       |
| **2**    | Metric regression     | C04 10^-10 级 mismatch                | dual-anchor freeze                        |
| **3**    | Model audit           | 无 top-level class                    | recursive factory audit                   |
| **4**    | Initial benchmark     | args use-before-parse                 | separate recovery                         |
| **5**    | Pure diagnostics FIX2 | unconditional search.\_shadow_records | zero-search guard                         |
| **6**    | Pure diagnostics FIX3 | unconditional finalize_episode        | exhaustive post-zero scan                 |
| **7**    | FIX4                  | 揭示原始 search unbound               | FIX5R1 restore constructor                |
| **8**    | FIX5                  | source-string parity false negative   | AST parity                                |
| **9**    | FIX5 strict           | stale schema key                      | exact schema set check                    |
| **10**   | Seed2 freeze          | prereg filename typo                  | manifest/root checksum                    |
| **11**   | FIX6                  | factory order assumption              | actual control-flow audit                 |
| **12**   | FIX6R1                | synthetic AST no lineno               | exact source reuse                        |
| **13**   | FIX6R2                | quote-sensitive unparse               | AST semantic matcher                      |
| **14**   | Guided wrapper R0     | stale meta status                     | 41-item generator/executor reconciliation |
| **15**   | Guided wrapper R1     | path substring false negative         | AST checkpoint-map audit                  |
| **16**   | Guided wrapper R2     | nested tuple sentinel missed          | recursive RuntimeError AST + exact replay |
| **17**   | Guided wrapper R3     | prestart + execution PASS             | first Guided frozen                       |

# **附录 B｜下一 Gate 的最小 PASS / FAIL 标准**

## **B.1 当前下一条件**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>CONDITION=GUIDED_B8_RUNTIME_SEED0_MODEL_SEED20260825<br />
BUDGET=8<br />
RUNTIME_MCTS_SEED=0<br />
MODEL_SEED=20260825<br />
CHECKPOINT_SHA=5df90947a5fdd2bc6aa525ca5eba78b6379e127e5df6ca1d0362c992caab73b5<br />
AUTHORIZATION_SHA=ad49eeaa26ad46176189b220700ace7663a269dfc1a9bb5f2b7496959afdcaa1<br />
PREEXEC_REVIEW_SHA=f29887e2e47f51b53262427422bc5f2137fc0cb7fb7ebf2f20be471379b1f417</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## **B.2 PASS 标准**

| **检查项**          | **PASS 标准**                                                                           |
|---------------------|-----------------------------------------------------------------------------------------|
| **Preflight**       | related process absent；output/evidence absent；Git clean；all SHAs exact               |
| **Authorization**   | status=AUTHORIZED_NOT_STARTED；consumed=False；max launches=1                           |
| **Prestart**        | FIX6R3 factory/binding/checkpoint/search/scorer exact semantic replay PASS              |
| **START**           | 仅在全部 prestart PASS 后写入；consumes authorization                                   |
| **Execution**       | 单一 Guided process；Pure launch=False；automatic retry=False                           |
| **Technical**       | runner RC=0；result/metrics/root/shadow/summary 全部存在且 parse                        |
| **Instrumentation** | value_forward_count_total=root_search_count；每 metrics row forward=1；inference sum\>0 |
| **MCTS**            | iterations=root_count×8；shadow rows=tree expansions；integration flag=True             |
| **Quality**         | 五个 predicates schema 完整；PASS 或 Scientific FAIL 均保留                             |
| **Capture**         | START/CAPTURE/stdout/stderr/rc/output SHA/evidence SHA 完整                             |

## **B.3 FAIL 处理**

- START 前失败：Technical HOLD；授权未消费；只修 wrapper/prestart fault domain。

- START 后技术失败：授权已消费；冻结证据；禁止自动重跑；先判定 0 root/0 forward/已产生科学信息。

- RC=0 但 quality FAIL：这是有效 Scientific FAIL，计入次级矩阵并禁止重跑。

- 不得一次同时修模型、Search、Reward、Transition、UCT、rollout、backup 或 feature extractor。
