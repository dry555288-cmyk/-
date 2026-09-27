**MineSim-Dynamic**

**全项目阶段性总总结与 AI 无缝接管手册**

**2026-08-29 · Value-guided MCTS 次级 B8 矩阵 4 / 9 完成停点版**

**当前停点：第 5 格 R1 / M20260825 · PRE-START line 275 AssertionError**

重点专题：协议 erratum、post-START artifact-binding 重分类、wrapper / prestart 连续错误复盘

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>当前真实状态</strong></p>
<p>Value V3 独立泛化已冻结 PASS；Pure B8 三个 runtime seeds 全部稳定；Guided B8 次级矩阵已完成并冻结 4 / 9。第 5 格（runtime seed 1 / model seed 20260825）已授权但尚未启动，当前仅在 LOW 的 wrapper derivation / full-prestart replay 中，于 STRICT GUIDED PRESTART 的 Python line 275 发生无消息 AssertionError。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

交接版本：V1 \| 适用对象：后续 ChatGPT / Codex / 工程执行人员

正式 repo：/root/MineSim-Dynamic

主 evidence root：/root/autodl-tmp/paper1_value_v3_development_only_v1

证据截止：2026-08-29；截至 R1/M20260825 MATRIX4_ARTIFACTBINDING1_V3 full-prestart replay FAIL

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>证据优先级声明</strong></p>
<p>任何晚于本证据截点的 AutoDL 真实终端输出、Git、源码、SHA、START/CAPTURE/result/freeze 均自动优先于本 Word。本文件是可恢复的当前权威 handoff，不是对未来状态的永久承诺。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 0. CURRENT_STATE｜一页接手摘要

| **字段**                 | **当前值**                                                   | **接管解释**                                                                                                                             |
|--------------------------|--------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------|
| **EVIDENCE_CUTOFF**      | **2026-08-29；最新 V3 full-prestart replay**                 | 当前最新终端已证明 exact SHA、artifact binding、Matrix4 bridge 与 legacy compat 均到达；随后在 prestart Python line 275 AssertionError。 |
| **CURRENT_STAGE**        | **Value-guided MCTS integration efficiency evaluation**      | 仅推进预注册 Guided B8 次级矩阵；训练、C01 forward、Pure B8 均已冻结。                                                                   |
| **CURRENT_GATE**         | **R1/M20260825 wrapper derivation + full prestart**          | 目标条件 GUIDED_B8_RUNTIME_SEED1_MODEL_SEED20260825，尚未 START。                                                                        |
| **CURRENT_STATUS**       | **Guided B8 completed = 4 / 9**                              | 前四格已按冻结/erratum/窄重分类计入；第五格 AUTHORIZED_NOT_STARTED。                                                                     |
| **LATEST_GIT_HEAD**      | **112d2bd0f3412fc83b13d5587d2b41402d2d0f5e**                 | 最新终端显示 tracked Git clean。                                                                                                         |
| **LATEST_FROZEN_RESULT** | **R1/M20260824 · Technical PASS + Scientific PASS**          | 原 CAPTURE 因 seed0 文件名硬编码误判 HOLD；后由完整 seed1 artifact 证据窄重分类并冻结为第 4 格。                                         |
| **PRIMARY_SCIENCE**      | **SCIENTIFIC_FAIL_BY_PREREGISTERED_BUDGET_FLOOR**            | Pure 在最低预注册 B8 已稳定；禁止事后增加 B4/B2。                                                                                        |
| **SECONDARY_SCIENCE**    | **Tree expansion / wall-clock = NOT_EVALUATED**              | 必须完成全部 9 格后按 frozen aggregation 统一判断。                                                                                      |
| **CURRENT_BLOCKER**      | **STRICT PRESTART Python line 275 AssertionError**           | 已通过 FROZEN_JSON_MUTATED=False；失败断言的源码与实际值尚未定位，必须写 HOLD。                                                          |
| **NEXT_MINIMAL_ACTION**  | **LOW：只读 line-275 assert-surface diagnostic**             | 从 V3 最终 prestart heredoc 编号打印 line 250–290、所有 assert AST 与实值；不发布 child、不写 START。                                    |
| **RESOURCE_REQUIRED**    | **LOW**                                                      | 当前不需要 HIGH-CPU / HIGH-GPU；只有 full prestart 全 PASS 后才允许 HIGH-CPU 单次执行。                                                  |
| **DO_NOT_REPEAT**        | **所有已消费 one-time 与已冻结结果**                         | 尤其 Pure B8、r0/m24、r0/m25、r0/m26、r1/m24；也不要重跑 R1/M25 的 V1/V2/V3 失败 derivation。                                            |
| **HOLD**                 | **第 5 格 child wrapper、其余 4 格、最终 efficiency claims** | 当前 intended child 未发布；完整矩阵、expansion reduction、wall-clock speedup、production claims 均未证明。                              |

## 0.1 60 秒科学口径

- Value V3 已在独立 C01 上证明动作价值排序有用：三个固定 final-model seeds 的 normalized regret 中位数严格优于 frozen immediate baseline；INDEPENDENT_GENERALIZATION_PASS 已冻结。

- Pure B8 在 runtime seeds 0/1/2 全部技术有效且五项质量谓词全过，因此 PURE_MIN_STABLE_BUDGET=8。

- 预注册 budget ladder 为 \[8,16,32,64\]；Guided 不可能获得 \<8 的最低稳定预算，所以 primary lower-budget criterion 是真实 Scientific FAIL，不是待修 Bug。

- Guided B8 次级矩阵已计入 4 格：3 个 Scientific PASS、1 个 Scientific FAIL；当前不能据此宣布稳定降低 tree expansion 或 wall-clock。

- 当前第 5 格尚未启动；所有失败都在 START 前的 wrapper/prestart Gate，授权未消费。

## 0.2 Guided B8 矩阵一览

| **组合**       | **状态**                | **矩阵进度** | **关键结果 / 边界**                                                                                                   |
|----------------|-------------------------|--------------|-----------------------------------------------------------------------------------------------------------------------|
| r0 / m20260824 | FROZEN PASS             | 1/9          | 308 roots；2464 expansions；308 forwards；5/5 quality。                                                               |
| r0 / m20260825 | FROZEN Scientific FAIL  | 2/9          | 890 roots；7120 expansions；890 forwards；completion/post-conflict 两项 FAIL；按 outcome-consistent RC erratum 计入。 |
| r0 / m20260826 | FROZEN PASS             | 3/9          | 331 roots；2648 expansions；331 forwards；5/5 quality；postcheck manifest 故障不否定结果。                            |
| r1 / m20260824 | FROZEN PASS（窄重分类） | 4/9          | 326 roots；2608 expansions；326 forwards；5/5 quality；capture seed0 文件名错误已由 immutable decision/freeze 纠正。  |
| r1 / m20260825 | AUTHORIZED_NOT_STARTED  | current      | AUTH=805abb…；PREEXEC=87a852…；checkpoint=5df909…；output/evidence absent。                                           |
| r1 / m20260826 | NOT AUTHORIZED          | pending      | 不得提前启动。                                                                                                        |
| r2 / m20260824 | NOT AUTHORIZED          | pending      | 不得提前启动。                                                                                                        |
| r2 / m20260825 | NOT AUTHORIZED          | pending      | 不得提前启动。                                                                                                        |
| r2 / m20260826 | NOT AUTHORIZED          | pending      | 不得提前启动。                                                                                                        |

## 0.3 当前停点的最短描述

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>一句话接管</strong></p>
<p>矩阵 4/9 已冻结；第 5 格 R1/M20260825 的 one-time authorization 已创建且未消费。V3 派生器已修复 exact SHA、seed1 artifact filenames、Matrix4 bridge、legacy compatibility 注入顺序，但 exact prestart replay 在 FROZEN_JSON_MUTATED=False 之后的 Python line 275 仍无消息 AssertionError；下一步仅做 LOW 只读断言定位。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 目录与推荐阅读顺序

1.  1\. 0. CURRENT_STATE｜一页接手摘要

2.  2\. 1. 文档控制、证据等级与交接边界

3.  3\. 2. 项目长期主线总览

4.  4\. 3. MineSim 运行架构与永久科学边界

5.  5\. 4. 神经网络主线：Value V3 development → C01 independent PASS

6.  6\. 5. Value-guided MCTS 预注册、Pure B8 与协议 erratum

7.  7\. 6. Guided B8 当前 4/9 结果与正式冻结

8.  8\. 7. 当前第 5 格停点：R1/M20260825 PRE-START line 275 HOLD

9.  9\. 8. 2026-08-28/29 新错误总览

10. 10\. 9. 新错误逐项复盘（现象→原因→排查→处理→证据→禁止重复）

11. 11\. 10. 由本轮错误固化出的工程标准

12. 12\. 11. 关键路径、SHA 与状态矩阵

13. 13\. 12. 资源、协作、文件与 Git 工作流

14. 14\. 13. DO_NOT_REPEAT / HOLD / 不可回退项

15. 15\. 14. 云端文档、失败 stage 与删除情况

16. 16\. 15. 快速接手区

17. 17\. 附录 A. 本轮错误时间线

18. 18\. 附录 B. 当前下一 Gate 的最小 PASS / FAIL 标准

推荐阅读：新 AI 先读第 0、6、7、8、9、15 节；只有出现 SHA 或 provenance 冲突时，再回查第 2～5 节。

# 1. 文档控制、证据等级与交接边界

## 1.1 事实优先级

当前 AutoDL 终端 / Git / 源码 / 实际运行结果 / SHA  
\> frozen result / manifest / START / CAPTURE / decision / freeze  
\> 本交接 Word  
\> 历史交接  
\> 设计计划  
\> AI 记忆

- 文件名包含 PASS / final / freeze 不等于真正通过；必须同时看 RC、JSON、log、SHA、manifest 与 Gate。

- 历史交接中的“当前状态”已被本版覆盖，但历史科学结论和 provenance 仍保留。

- 缺少直接证据的字段写 HOLD / NOT VERIFIED；尤其当前 line 275 的具体断言不能凭猜测补齐。

- ChatGPT 附件存在不等于 AutoDL 已上传；AutoDL path missing 也不等于文件已删除。

## 1.2 本版主要证据源

| **证据**                                      | **用途**                                                                                                                    | **等级**    |
|-----------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------|-------------|
| 2026-08-29 最新 V3 终端                       | 证明 Matrix4/seed1 artifact/compat/exact SHA 前置检查通过，line 275 prestart AssertionError，child/output/evidence absent。 | 最高        |
| R1/M20260825 auth + preexec                   | 证明第 5 格 AUTHORIZED_NOT_STARTED、launch=1、retry=False、artifact-binding failure prestart blocking。                     | 冻结        |
| R1/M20260824 filename-binding decision/freeze | 证明第 4 格窄重分类为 Technical PASS + Scientific PASS，matrix=4/9。                                                        | 冻结        |
| R0/M20260826 postexec freeze                  | 证明第 3 格 PASS，331 roots/2648 expansions/331 forwards。                                                                  | 冻结        |
| Outcome-consistent exit-code erratum          | 证明 PASS→RC0、FAIL→RC1 的统一技术完成规则，科学端点不变。                                                                  | 冻结决策    |
| R0/M20260825 result/evidence                  | 证明 Scientific FAIL 完整且 instrumentation closed，890 roots/7120 expansions/890 forwards。                                | 冻结/重分类 |
| 2026-08-27 1/9 handoff                        | 提供 MineSim→Value V3 的历史主线与前序错误复盘。                                                                            | 历史权威    |

## 1.3 本版不做的事情

- 不重新运行 AutoDL live inventory；因此本 Word 是否已经上传到 AutoDL 为 HOLD。

- 不读取或重跑已冻结训练、C01 forward、Pure B8、已消费 Guided 条件。

- 不把当前 line 275 断言猜成某个特定 schema/key；必须下一步只读定位。

- 不因 4/9 的中间结果提前宣称 tree expansion reduction 或 wall-clock speedup。

- 不修改现有 AUTH/PREEXEC/freeze/START/CAPTURE/result；本次只生成 Word。

## 1.4 状态词典

| **状态**               | **含义**                                                                     |
|------------------------|------------------------------------------------------------------------------|
| FROZEN                 | 已有不可变 result/decision/freeze 与 checksum；默认不覆盖、不重跑。          |
| AUTHORIZED_NOT_STARTED | one-time authorization 已创建，但 START 未写入；仅可继续通过 prestart Gate。 |
| Technical HOLD         | Gate/验证器/路径/schema 等技术问题，当前不形成新的科学结论。                 |
| Scientific FAIL        | 技术有效的真实科研负结果；必须计入矩阵并禁止挑结果重跑。                     |
| SUPERSEDED             | 历史方案已被更新证据覆盖，但用于 provenance。                                |
| HOLD / NOT EVALUATED   | 直接证据不足或完整矩阵未完成。                                               |

# 2. 项目长期主线总览（按真实演进组织）

| **阶段**             | **状态**          | **当前真实结论**                                                                         |
|----------------------|-------------------|------------------------------------------------------------------------------------------|
| MineSim 复现         | PASS / FROZEN     | IDM baseline、replay、closed-loop 基础环境已建立；无需重做。                             |
| 蒙特卡洛 / Pure MCTS | PASS / FROZEN     | 真实 MineSim online closed-loop；search/reward/trajectory/controller 链已跑通。          |
| 单车                 | PASS / FROZEN     | J117 423-step 单车与 FullMine representative Pure MCTS 3/3。                             |
| 双车冲突场景         | PASS / FROZEN     | NO-MCTS causal conflict、双受控运行边界与真实冲突场景。                                  |
| FullMine 新地图      | PASS / FROZEN     | Vector V2 semantic + Vector V4 bitmap/runtime/planner；Research/DEV 口径。               |
| Fleet-MCTS           | PASS + 负结果并存 | Polygon21 5/5；C04/C06 成功；C11 安全死锁负结果保留。                                    |
| 多种子 / cross-scene | FROZEN            | C04/C11/C06 development collection、blind protocol、C01 独立场景。                       |
| 原生可视化           | PASS / 部分 HOLD  | Native Video V2 final；部分 showcase 历史未完全收口。                                    |
| 云端整理             | PASS / COMPLETE   | 历史证据为 move/isolate/archive；科研文件 actual delete=0（前序证据）。                  |
| 神经网络             | CURRENT           | Value V3 independent PASS；Pure B8 stable；Guided B8 matrix 4/9；第 5 格 prestart HOLD。 |

## 2.1 历史阶段无需重做的原因

- MineSim/Pure MCTS/单车/双车/FullMine/Fleet-MCTS 已有真实 runtime、结果和前序 handoff；当前只在神经网络接入与效率评价推进。

- C11 安全死锁等负结果属于真实科学证据，不能因后续网络进展而删除或重解释。

- FullMine 仍是 Research/DEV map，不得表述为官方生产级 HD Map 或 authoritative drivability truth。

- 历史清理只证明 move/isolate/archive/quarantine；除非存在直接 delete manifest，否则不得写“已删除”。

# 3. MineSim 运行架构与永久科学边界

## 3.1 主运行链

run_simulation.py  
→ SimulationsRunner.\_initialize()  
→ EnvironmentSimulation.initialize()  
→ Scenario / Map loader  
→ Planner.initialize()  
→ Planner.compute_planner_trajectory()  
→ MCTS / Fleet-MCTS search  
→ Trajectory Adapter  
→ TwoStageController.update_state()  
→ LQR / iLQR trajectory tracking  
→ KinematicBicycleModel.propagate_state()  
→ Agent Update Policy / Observation  
→ SimulationHistory / metrics / log  
→ next frame

## 3.2 故障分层纪律

| **边界**                     | **固定处理规则**                                                                  |
|------------------------------|-----------------------------------------------------------------------------------|
| Planner vs 执行器            | 搜索/规划轨迹合法不等于 Controller/KBM 可实现；必须分层。                         |
| 双车 truth                   | B 的真实状态不得由 A history 推断；每辆 controlled ego 独立 observation/history。 |
| Controlled vs external actor | 同一车辆不能同时作为 controlled ego 与 external actor。                           |
| 空间相交 vs 时间冲突         | 几何路径相交不自动等于 temporal conflict；需要 NO-MCTS causal evidence。          |
| Safe vs success              | 无碰撞不等于任务完成；deadlock 可以是 Scientific FAIL。                           |
| Static truth                 | frozen V4 bitmap + XG90G footprint 为 primary；CollisionLookup 仅 secondary。     |
| Safety sidecar               | V2V/V2R/risk/shadow/safe-node 若仅 diagnostic，不得写成 hard constraint。         |

# 4. 神经网络主线：Value V3 development → C01 independent PASS

## 4.1 Value V2 与 Value V3 边界

- Value V2 在 C03 independent validation 上 Scientific FAIL，已关闭为 DO_NOT_INTEGRATE；不得重跑或 retune。

- Value V3 通过 coverage expansion、2356-root episode-aware LOSO 与 3 个 fixed final full-development models，形成新的 development candidate。

## 4.2 2356-root 冻结协议

| **项目**         | **冻结值**                                                                        |
|------------------|-----------------------------------------------------------------------------------|
| Dataset          | 2356 roots；37696 action rows；6 episodes；identity=(scene,episode_uid,root_step) |
| Architecture     | 12 → 64 → 64 → 16；ActionConditionedValueV3PairwiseRank                           |
| Objective        | ROOT_NORMALIZED_WEIGHTED_PAIRWISE_LOGISTIC                                        |
| Split            | LEAVE_ONE_SCENE_OUT                                                               |
| Seeds            | 20260824 / 20260825 / 20260826                                                    |
| Epochs / LR      | 600 / 0.001                                                                       |
| Best-seed / HPO  | False / False                                                                     |
| Output semantics | 16 joint-action scores；joint_action_index=A\*4+B                                 |

## 4.3 Development 与 C01 独立结果

| **对象**        | **3-seed / frozen result**                                                                 | **结论**                        |
|-----------------|--------------------------------------------------------------------------------------------|---------------------------------|
| C04             | median regret 0.174277542 \< baseline 0.273804418                                          | PASS                            |
| C11             | median regret 0.117458957 \< baseline 0.181778548                                          | PASS                            |
| C06             | median regret 0.122468490 \< baseline 0.241806713                                          | PASS                            |
| C01 independent | regret 0.099474704 / 0.155963166 / 0.105839497；median 0.105839497 \< baseline 0.295195862 | INDEPENDENT_GENERALIZATION_PASS |

## 4.4 三个 final checkpoint SHA

| **Model seed** | **SHA256**                                                       | **状态**                |
|----------------|------------------------------------------------------------------|-------------------------|
| 20260824       | 496e4259eb9801f3ce70c1094be12fd0985cb03e97d606cade8dfbe9d5228633 | FROZEN                  |
| 20260825       | 5df90947a5fdd2bc6aa525ca5eba78b6379e127e5df6ca1d0362c992caab73b5 | FROZEN / current target |
| 20260826       | 3881d39c09b02a513e44f0fe612aad42de9ff636fd07e314d327b4c6d5f132df | FROZEN                  |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>科学边界</strong></p>
<p>C01 PASS 证明网络能改善动作价值排序；不等于 production ready，也不等于 MCTS efficiency 已证明。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 5. Value-guided MCTS 预注册、Pure B8 与协议 erratum

## 5.1 Guided 接入冻结设计

- Value 仅用于 root depth=0 的 joint-action ordering。

- 每个 root 只允许 1 次 score_12d forward；tree search 内不允许额外 forward。

- hard pruning=False；PUCT=False；UCT formula、rollout、backup、reward、transition、action provider 均不改变。

- Guided model seeds 固定为 20260824/20260825/20260826；runtime MCTS seeds 固定为 0/1/2。

- Preregistered budget ladder 固定为 \[8,16,32,64\]。

## 5.2 Pure B8 baseline

| **Runtime seed** | **Root searches** | **Iterations** | **Tree expansions** | **Runner wall** | **质量** |
|------------------|-------------------|----------------|---------------------|-----------------|----------|
| 0                | 453               | 3624           | 3624                | 34 s            | PASS     |
| 1                | 429               | 3432           | 3432                | 31 s            | PASS     |
| 2                | 341               | 2728           | 2728                | 26 s            | PASS     |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>主判据的真实 Scientific FAIL</strong></p>
<p>Pure 在最低预注册 B8 已稳定，Guided 无法取得 &lt;8 的 minimum stable budget；PRIMARY_LOWER_BUDGET_CRITERION_STATUS=SCIENTIFIC_FAIL_BY_PREREGISTERED_BUDGET_FLOOR。禁止事后新增 B4/B2。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## 5.3 Outcome-consistent exit-code erratum

PASS result → runner RC = 0  
FAIL result → runner RC = 1  
共同要求：result/artifacts 完整、无 runtime error、nonzero search、instrumentation closed  
其他 RC/status 组合 → Technical failure

- erratum 只修正 technical exit-code interpretation，不改 scientific endpoints、quality predicates、Search/Reward/UCT/rollout/backup、budget ladder、model 或 checkpoint。

- 如果仍要求所有可计入结果都 RC=0，会系统性排除 Scientific FAIL，形成 outcome-dependent censoring。

- 该 erratum 透明标记为 post-outcome，并统一适用于 9 个 Guided B8 条件；不允许同条件重跑或调参。

# 6. Guided B8 当前 4/9 结果与正式冻结

## 6.1 FIX6R3 固定接入边界

| **对象**                                 | **冻结值**                                                       |
|------------------------------------------|------------------------------------------------------------------|
| FIX6R3 runner SHA                        | ea4d7f21265be0b2409cc2b25e6f1bd2c7ad49317d593929a34752d286d5eb79 |
| FIX6R3 meta SHA                          | c0e1520d81ddc1b36c1e56078e2dbf1ea50c1cd6a0f2e9ad59adef5ccd25464c |
| Pure binding changed                     | False                                                            |
| Guided binding added                     | True                                                             |
| Frozen factory reused                    | True                                                             |
| Search/Reward/UCT/Rollout/Backup changed | False                                                            |

## 6.2 四个已计入条件

| **条件**     | **科学结果**     | **RC** | **Roots** | **Expansions** | **Forwards** | **Quality** | **冻结说明**                                                                         |
|--------------|------------------|--------|-----------|----------------|--------------|-------------|--------------------------------------------------------------------------------------|
| r0/m20260824 | PASS             | 0      | 308       | 2464           | 308          | 5/5 True    | 直接 postexec freeze；must_not_be_rerun。                                            |
| r0/m20260825 | Scientific FAIL  | 1      | 890       | 7120           | 890          | 3/5 True    | BENCHMARK_COMPLETION_SUCCESS 与 POST_CONFLICT_COMPLETION=False；erratum 后技术有效。 |
| r0/m20260826 | PASS             | 0      | 331       | 2648           | 331          | 5/5 True    | wrapper postcheck AUTH manifest basename 失败；独立证据闭环后 freeze。               |
| r1/m20260824 | PASS（窄重分类） | 0      | 326       | 2608           | 326          | 5/5 True    | runner 输出 seed1；capture 错找 seed0；immutable decision/freeze 接受。              |

## 6.3 关键正式决策与 SHA

| **对象**                               | **SHA256**                                                       | **作用**                                          |
|----------------------------------------|------------------------------------------------------------------|---------------------------------------------------|
| Protocol erratum                       | b847e16fa972b59ce3f12a607bc06ac3909a1f55785cd76202e0f61e4e643250 | PASS→RC0 / FAIL→RC1 outcome-consistent 技术完成。 |
| R0/M20260825 discrepancy freeze        | 1c9eead2f384e2072c7773ab48bcca5eafdb661b4904fa12307fedce16ca41fb | 冻结 runner/prereg RC 契约冲突，禁止重跑。        |
| R0/M20260826 postexec freeze           | da567a9e3114cbf105da22f4008cccab27708b707b45d99b0f8a1a88da0ccf83 | 第三格 PASS；matrix=3/9。                         |
| R1/M20260824 artifact-binding decision | 9b81205214991e4e0934c1ddec3ae91eb76bd017938be9ef20fbd86683b23185 | 第四格窄重分类 PASS；matrix=4/9。                 |

## 6.4 当前第 5 格 authorization

| **字段**                 | **值**                                                                               |
|--------------------------|--------------------------------------------------------------------------------------|
| Condition                | GUIDED_B8_RUNTIME_SEED1_MODEL_SEED20260825                                           |
| Budget / runtime / model | 8 / 1 / 20260825                                                                     |
| Checkpoint SHA           | 5df90947a5fdd2bc6aa525ca5eba78b6379e127e5df6ca1d0362c992caab73b5                     |
| Authorization SHA        | 805abb852bc410757dd4287751cd12cbf66a7000d50c9b8031c1ca902d7fa50d                     |
| Preexec SHA              | 87a852f015c9bbd8088b84331c41b6e21bf3510c840eddb83721dcd48a11f415                     |
| Status                   | AUTHORIZED_NOT_STARTED；consumed=False；max launches=1；automatic retry=False        |
| Output / evidence        | ABSENT / ABSENT                                                                      |
| Artifact contract        | active capture 必须使用 seed1 result/root/shadow 文件名；seed0 active binding 禁止。 |

# 7. 当前第 5 格停点：R1/M20260825 PRE-START line 275 HOLD

## 7.1 V3 已经证明通过的部分

- PARENT、AUTH、PREEXEC、Matrix4 decision、erratum、checkpoint 全部 exact SHA PASS。

- child/output/evidence/related process 均 absent；authorization 未消费。

- canonical shell bindings（AUTH_ROOT/AUTH/PREEXEC/CKPT/GUIDED_OUTPUT/EVIDENCE）与 exact SHA gate 已逐行重写并 shadow 验证。

- active seed1 artifact assignments 5/5 正确；active seed0 capture binding=ABSENT。

- Matrix4 legacy auth/review compatibility 已分别在初次 load 后注入，并证明早于第一次 legacy key read。

- obsolete Matrix3 bridge 已删除；Matrix4 decision + artifact-binding prestart bridge PASS。

- capture outcome-consistent RC AST、technical_pass=len(errors)==0、matrix accounting=5 if technical else 4、AUTH postcheck manifest、FINAL_RC exit 均 PASS。

## 7.2 最新 full-prestart replay 的准确停止位置

MATRIX4_AUTH_LEGACY_INMEMORY_COMPAT=PASS  
MATRIX4_REVIEW_LEGACY_INMEMORY_COMPAT=PASS  
MATRIX4_LEGACY_INMEMORY_COMPAT=PASS  
THIRD_GUIDED_SCHEMA_ADAPTER_ERRATUM1=PASS  
PROTOCOL_ERRATUM_PRESTART_BINDING=PASS  
MATRIX_COUNT_BEFORE_EXECUTION=4_OF_9  
MATRIX4_ARTIFACT_BINDING1_PRESTART=PASS  
RUNTIME_SEED1_ARTIFACT_FILENAME_CONTRACT_PRESTART=PASS  
STALE_SEED0_ACTIVE_CAPTURE_BINDING_FORBIDDEN_PRESTART=True  
FROZEN_JSON_MUTATED=False  
Traceback: File "\<stdin\>", line 275, AssertionError

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>定性</strong></p>
<p>Pre-START Technical HOLD。没有 START、没有 checkpoint load、没有 model forward、没有 MCTS、没有 child wrapper 发布；现有 authorization 仍可继续用于修复后的下一版 prestart Gate。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## 7.3 当前不知道、不能猜的内容

- line 275 对应的具体 assert 源码。

- 失败值是 schema/status/count/checkpoint map 还是其他 inherited assertion。

- 是否只需一处最小兼容层，还是存在同一 fault domain 的多个后续 assertion。

## 7.4 下一步唯一最小动作（建议脚本名）

C01_GUIDED_B8_R1_M20260825_PRESTART_LINE275_ASSERT_SURFACE_READONLY_DIAGNOSTIC_V1.txt

19. 资源 LOW；只读。

20. 从当前 V3 derivation 精确构造最终 prestart heredoc，但不执行 runner、不发布 child。

21. 给 heredoc 每行编号，打印 line 250–290；列出每个 assert 的 lineno、source、依赖字段与实际值。

22. 在临时副本中逐 assertion 运行或显式捕获，唯一定位 line 275 的真实断言。

23. 结束时重新证明 auth consumed=False、output/evidence absent、START=False、checkpoint/forward/MCTS=False。

## 7.5 当前 Gate 的 PASS / FAIL 标准

| **类型** | **标准**                                                                                                      |
|----------|---------------------------------------------------------------------------------------------------------------|
| PASS     | 精确输出 line 275 assert 源码、左右值/字段、失败类别、唯一 fault domain；无任何 mutation/START/forward/MCTS。 |
| FAIL     | 无法唯一定位断言，或发现多个无法区分的 assertion；保存完整 numbered surface 后停止，不猜、不 patch。          |
| 禁止     | 直接重跑 V3；直接生成 V4 patch；开启 HIGH-CPU；执行 intended child；修改冻结 JSON。                           |

# 8. 2026-08-28/29 新错误总览

本节从前序 handoff 的 E18 继续编号。大量错误属于 Gate/wrapper/diagnostic 自身，不是网络或 MCTS 科学失败；真正 Scientific FAIL 仍只有预注册主判据和 r0/m20260825 的任务质量结果。

<table>
<colgroup>
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>ID / 阶段</strong></th>
<th><strong>现象</strong></th>
<th><strong>分类/边界</strong></th>
<th><strong>根因</strong></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>E19<br />
Derivation auth audit</td>
<td>AUTH_ALREADY_CONSUMED [False, True]</td>
<td>Pre-START</td>
<td>字段名模糊匹配把 authorization_consumed=False 与 start_consumes_authorization=True 混为同一状态。</td>
</tr>
<tr class="even">
<td>E20<br />
Strict prestart</td>
<td>KeyError: fix6_runner_sha256</td>
<td>Pre-START</td>
<td>auth schema key 层级/名称与 wrapper 手写断言不一致。</td>
</tr>
<tr class="odd">
<td>E21<br />
Diagnostic</td>
<td>PRESTART_BLOCK_MATCH_COUNT=0</td>
<td>Read-only technical</td>
<td>依赖精确 heredoc/source 文本定位，遇到格式变化失效。</td>
</tr>
<tr class="even">
<td>E22<br />
Checkpoint/remaining adapter</td>
<td>expected map mismatch / bool-int mismatch</td>
<td>Pre-START</td>
<td>当前 target ckpt 被误用于共享 3-model map；remaining bool 与 count 语义混用。</td>
</tr>
<tr class="odd">
<td>E23<br />
R0/M20260825 result</td>
<td>完整 Scientific FAIL 却 runner RC=1</td>
<td>Post-START protocol discrepancy</td>
<td>runner FAIL→RC1 与 prereg universal RC0 gate 冲突。</td>
</tr>
<tr class="even">
<td>E24<br />
Erratum capture patch</td>
<td>technical_pass assign count=2 / candidate=0</td>
<td>Pre-START</td>
<td>错误假设 technical_pass 唯一且直接包含 RC；真实为初始化 + len(errors)==0。</td>
</tr>
<tr class="odd">
<td>E25<br />
Capture control flow</td>
<td>补丁打在 technical_pass 而非 outer gate</td>
<td>Pre-START</td>
<td>RC0 直接包住整套 strict validation；应扩展 outer gate。</td>
</tr>
<tr class="even">
<td>E26<br />
Prestart token audit</td>
<td>AUTH SHA “缺失”</td>
<td>Pre-START false negative</td>
<td>SHA 在 shell prefix，checker 错要求重复出现在 Python body。</td>
</tr>
<tr class="odd">
<td>E27<br />
Auth checksum</td>
<td>SHA256SUMS.txt missing</td>
<td>Pre-START/Postcheck</td>
<td>新 auth root 使用 AUTHORIZATION_SHA256SUMS.txt，旧 wrapper basename stale。</td>
</tr>
<tr class="even">
<td>E28<br />
Checksum selector</td>
<td>candidate count=2</td>
<td>Pre-START checker</td>
<td>窗口同时包含 FIX6 root 和 auth checksum；错误假设唯一。</td>
</tr>
<tr class="odd">
<td>E29<br />
Legacy schema</td>
<td>completed count=1 / review key missing</td>
<td>Pre-START</td>
<td>旧 Matrix1/Matrix2 adapter 未跟进 2/9、3/9 与新 PREEXEC schema。</td>
</tr>
<tr class="even">
<td>E30<br />
Shared model map</td>
<td>20260825 key 被改成 20260826</td>
<td>Pre-START</td>
<td>只保护 int key，漏保护字符串 seed-key dict。</td>
</tr>
<tr class="odd">
<td>E31<br />
R0/M20260826 postcheck</td>
<td>runner/capture PASS 后 postcheck FAIL</td>
<td>Post-CAPTURE bookkeeping</td>
<td>AUTH_ROOT 后验仍使用旧 manifest basename。</td>
</tr>
<tr class="even">
<td>E32<br />
Read-only diagnostic V1</td>
<td>capture top-level fields=None</td>
<td>Diagnostic false negative</td>
<td>真实字段部分嵌套；诊断脚本假设顶层。</td>
</tr>
<tr class="odd">
<td>E33<br />
Read-only diagnostic V2</td>
<td>manifest file not found</td>
<td>Diagnostic false negative</td>
<td>manifest 在 EVIDENCE，校验 cwd 在 OUTPUT；只传 basename。</td>
</tr>
<tr class="even">
<td>E34<br />
Postexec freeze V1</td>
<td>stability decision missing</td>
<td>Freeze preflight</td>
<td>凭记忆猜目录名，而不是按唯一文件名/manifest 发现。</td>
</tr>
<tr class="odd">
<td>E35<br />
R1/M20260824 derivation</td>
<td>旧 condition residual</td>
<td>Pre-START</td>
<td>共享 universe 保护错误地跳过了长 condition/namespace token。</td>
</tr>
<tr class="even">
<td>E36<br />
Residual audit</td>
<td>历史 provenance 被判 active stale</td>
<td>Pre-START checker</td>
<td>全局零残留规则没有区分历史 freeze 路径与活跃执行绑定。</td>
</tr>
<tr class="odd">
<td>E37<br />
R1/M20260824 capture</td>
<td>seed1 runner 完整，capture 报 seed0 files missing</td>
<td>Post-START Technical HOLD</td>
<td>active RESULT/ROOT/SHADOW 文件名硬编码 seed0。</td>
</tr>
<tr class="even">
<td>E38<br />
R1/M20260825 V1</td>
<td>EXACT SHA gate 在 auth print 前失败</td>
<td>Pre-START</td>
<td>顶层 AUTH/PREEXEC/CKPT 路径/文件名未 canonical 重写。</td>
</tr>
<tr class="odd">
<td>E39<br />
R1/M20260825 V2</td>
<td>KeyError first_guided_postexec_freeze_sha256</td>
<td>Pre-START</td>
<td>legacy compatibility 注入到最后一次 assignment 后，早期 assertion 先读取缺失 key。</td>
</tr>
<tr class="even">
<td>E40<br />
R1/M20260825 V3</td>
<td>line 275 AssertionError</td>
<td>Pre-START current blocker</td>
<td>exact fault domain 尚未定位；必须下一步只读编号诊断。</td>
</tr>
</tbody>
</table>

# 9. 新错误逐项复盘（经验教训重点）

## 9.1 AUTH_ALREADY_CONSUMED：状态字段与策略字段被名称匹配混淆

| **项目**            | **内容**                                                                                                                                                       |
|---------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 现象                | 派生脚本读取 authorization 后抛 ('AUTH_ALREADY_CONSUMED',\[False,True\])，但只读 schema 诊断明确 authorization_consumed=False、status=AUTHORIZED_NOT_STARTED。 |
| 定性                | Pre-START Technical HOLD；无 child/output/evidence，无科学执行。                                                                                               |
| 根因                | checker 按字段名包含 consumed 收集值，把当前状态 authorization_consumed=False 与策略 start_consumes_authorization=True 一并解释为“是否已消费”。                |
| 排查过程            | 只读打印全部 relevant/status/consume fields，区分状态字段、策略字段与 future rule。                                                                            |
| 最终处理 / 当前状态 | 后续只按明确 schema path 读取 authorization_consumed；策略字段只作为 policy，不参与 current-state 判定。                                                       |
| 证据                | AUTH_SCHEMA_READONLY_DIAGNOSTIC=PASS；CHECKPOINT_LOADED=False；MCTS_EXECUTED=False。                                                                           |
| 以后禁止重复        | 禁止模糊 key-name 搜索决定 one-time 状态；必须使用 exact schema path。                                                                                         |

## 9.2 Schema / checkpoint map / remaining：共享协议与当前条件混在一起

| **项目**            | **内容**                                                                                                                                            |
|---------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| 现象                | 连续出现 fix6_runner_sha256 KeyError、checkpoint_map mismatch、secondary remaining bool/count mismatch。                                            |
| 定性                | 全部 Pre-START Technical HOLD；authorization 未消费。                                                                                               |
| 根因                | 版本化 auth/review 字段未同步；当前 target ckpt 变量被写进共享 3-model map；legacy remaining 字段既被当 bool 又被当 count。                         |
| 排查过程            | AST 提取 literal schema；将 20260824/25/26 checkpoint map 改为 canonical literals；显式区分 completed count、remaining count 与 boolean remaining。 |
| 最终处理 / 当前状态 | 通过 schema adapter、canonical checkpoint map 与 matrix count bridge；共享结构后来又增加 int/string key 双保护。                                    |
| 证据                | CHECKPOINT_MAP_AST_SEMANTIC_CONTRACT=PASS；LEGACY_BOOLEAN_REMAINING_BRIDGE=PASS。                                                                   |
| 以后禁止重复        | 禁止用当前条件变量构造共享 prereg map；禁止一个字段同时承担 bool 与 integer 语义。                                                                  |

## 9.3 R0/M20260825：runner RC1 与 prereg RC0 gate 的协议矛盾

| **项目**            | **内容**                                                                                                                                           |
|---------------------|----------------------------------------------------------------------------------------------------------------------------------------------------|
| 现象                | runner 产生完整 result/metrics/root/shadow，status=FAIL、error=None、890 roots/7120 expansions/890 forwards，但 wrapper 因 RC1 判 Technical HOLD。 |
| 定性                | 真实 Scientific FAIL + post-START protocol discrepancy；授权已消费，禁止重跑。                                                                     |
| 根因                | 冻结 runner 明确 PASS→RC0、FAIL→RC1；冻结 prereg 却把 universal RC0 当技术有效条件，导致 Scientific FAIL 被系统性剔除。                            |
| 排查过程            | AST 审计 runner status/exit；闭合 instrumentation；先 discrepancy freeze，再 formal erratum decision。                                             |
| 最终处理 / 当前状态 | 接受窄 outcome-consistent exit-code erratum：PASS/0 或 FAIL/1，其他技术要求不变，统一适用于 9 格。                                                 |
| 证据                | Protocol erratum SHA=b847e16f…；第二格矩阵计入 Scientific FAIL。                                                                                   |
| 以后禁止重复        | 禁止把 Scientific FAIL 包装成 retry；禁止只因 RC1 忽略完整科学结果。                                                                               |

## 9.4 technical_pass 与 outer gate：补丁层级判断错误

| **项目**            | **内容**                                                                                                                   |
|---------------------|----------------------------------------------------------------------------------------------------------------------------|
| 现象                | checker 先要求 technical_pass 只有一次，实际有初始化 False 与最终 len(errors)==0；随后尝试找 RC compare 得到 0 candidate。 |
| 定性                | Pre-START Technical HOLD。                                                                                                 |
| 根因                | RC 不直接参与 technical_pass 表达式；真正控制 strict validation 的是外层 if runner_rc==0。                                 |
| 排查过程            | 只读列出 errors mutation、RC-dependent IF、technical_pass dataflow 和 classification surface，定位唯一 outer gate。        |
| 最终处理 / 当前状态 | 把 outer gate 扩展为 RC0 或 (RC1 且 result.status=FAIL)，并保留同一完整 strict validation body。                           |
| 证据                | RC1_STATUS_FAIL_ENTERS_SAME_STRICT_VALIDATION_BODY=True；TECHNICAL_PASS_FINAL_SEMANTICS=LEN_ERRORS_EQ_0。                  |
| 以后禁止重复        | 禁止根据变量名猜控制流；必须做 AST/dataflow，补丁应落在真实支配节点。                                                      |

## 9.5 Token scope 与 checksum manifest：Python body、shell prefix、目录 basename 三层混淆

| **项目**            | **内容**                                                                                                                                        |
|---------------------|-------------------------------------------------------------------------------------------------------------------------------------------------|
| 现象                | 先报 auth/preexec SHA 不在 prestart body；后又报 SHA256SUMS.txt missing；再出现 checksum candidate count=2。                                    |
| 定性                | Pre-START 或 post-CAPTURE bookkeeping Technical HOLD。                                                                                          |
| 根因                | SHA 可以合法绑定在 shell prefix；新 auth root 的 manifest basename 是 AUTHORIZATION_SHA256SUMS.txt；局部窗口同时有 FIX6 root 与 auth checksum。 |
| 排查过程            | 区分 body-required token 与 prefix-required token；按“auth verify marker 前最后一个 checksum command”定位；证明 FIX6 legacy command 不变。      |
| 最终处理 / 当前状态 | prestart 与 postcheck 均显式使用 AUTHORIZATION_SHA256SUMS.txt；manifest 路径使用绝对路径 + target cwd。                                         |
| 证据                | AUTH_SHA_BOUND_BEFORE_PRESTART_CUTOFF=True；TARGET_AUTHORIZATION_SHA256SUMS_VERIFY=PASS。                                                       |
| 以后禁止重复        | 禁止要求同一 SHA 在多个层重复出现；禁止凭目录习惯猜 manifest basename。                                                                         |

## 9.6 Shared universe 保护：字符串 seed key 与长 token 的两次误伤

| **项目**            | **内容**                                                                                                            |
|---------------------|---------------------------------------------------------------------------------------------------------------------|
| 现象                | R0/M26 共享 meta map 变为 20260824/20260826/20260826；R1/M24 又因 protected lines 跳过长 token 而残留旧 condition。 |
| 定性                | Pre-START Technical HOLD。                                                                                          |
| 根因                | 第一次只保护 int key，漏字符串 key；第二次把共享“数值保护”错误扩展到长 condition/namespace 字符串。                 |
| 排查过程            | 对 int/string seed-key dict 均 AST 保护；把长 token 全局替换与裸数值替换分离；历史 provenance 另行允许。            |
| 最终处理 / 当前状态 | 共享 \[20260824,20260825,20260826\]、\[0,1,2\] 保持；active namespace 更新；历史 freeze path 保留。                 |
| 证据                | META_CHECKPOINT_CONTRACT_CANONICAL=PASS；ACTIVE_BINDING_RESIDUAL_AUDIT=PASS。                                       |
| 以后禁止重复        | 禁止把“共享数值 universe”与“历史 provenance/长 namespace token”用同一规则处理。                                     |

## 9.7 R0/M20260826：科学执行 PASS 后的 wrapper/diagnostic/freeze 连锁假设

| **项目**            | **内容**                                                                                                                                     |
|---------------------|----------------------------------------------------------------------------------------------------------------------------------------------|
| 现象                | runner/capture PASS 后 postcheck 因旧 auth manifest basename 失败；后续诊断又依次误假设 capture 顶层字段、manifest cwd、stability 固定目录。 |
| 定性                | Post-CAPTURE bookkeeping + diagnostic false negatives；原科学结果有效，不重跑。                                                              |
| 根因                | wrapper 与诊断脚本自身未适应新 schema/路径；“结果是否有效”与“收尾脚本是否成功”被混在一起。                                                   |
| 排查过程            | 直接读取 result/metrics/root/shadow、重验 output/auth checksum；逐次修正诊断，而不运行模型；freeze 按唯一 filename 发现 stability/prereg。   |
| 最终处理 / 当前状态 | 发布 postexec freeze，matrix 2→3。                                                                                                           |
| 证据                | 331 roots、2648 expansions、331 forwards、5/5 quality；freeze SHA=da567a9e…。                                                                |
| 以后禁止重复        | 禁止因 postcheck/diagnostic Bug 重跑有效 one-time；诊断也必须有 schema/path 自检。                                                           |

## 9.8 R1/M20260824：active binding、历史 provenance 与 runtime artifact filenames

| **项目**            | **内容**                                                                                                                                            |
|---------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| 现象                | 派生先因旧 condition residual 失败；修后又误把历史 Matrix3 freeze 路径中的旧 condition 当 active stale；正式执行后 capture 报 seed0 files missing。 |
| 定性                | 前两项 Pre-START HOLD；第三项 Post-START Technical HOLD，但 runner scientific PASS。                                                                |
| 根因                | 长 token 与共享 universe 保护耦合；全局 residual 规则不识别历史 provenance；parent wrapper active filenames 固定 seed0。                            |
| 排查过程            | 建立 provenance-aware residual audit；运行后只读验证 seed1 artifacts 和 checksum，逐一 cross-map 5 个 capture errors 到 stale seed0 filenames。     |
| 最终处理 / 当前状态 | 发布窄 artifact-binding reclassification decision/freeze；不改 CAPTURE、不重跑 wrapper，matrix 3→4。                                                |
| 证据                | 326 roots、2608 expansions、326 forwards、5/5 quality；decision SHA=9b812052…。                                                                     |
| 以后禁止重复        | active execution binding 必须 runtime-seed-aware；历史 provenance 允许保留旧 seed，但不得驱动 capture。                                             |

## 9.9 R1/M20260825 V1/V2/V3：exact SHA → compat 顺序 → line 275

| **项目**            | **内容**                                                                                                                                                                  |
|---------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 现象                | V1 在 exact SHA gate 未打印 AUTH 即退出；V2 修好 canonical shell/SHA 后 KeyError first_guided_postexec_freeze_sha256；V3 修好 compat 顺序后仍在 line 275 AssertionError。 |
| 定性                | 均为 Pre-START Technical HOLD；auth consumed=False，child/output/evidence absent。                                                                                        |
| 根因                | V1 的顶层 AUTH/PREEXEC/CKPT 未 canonical；V2 compatibility 按最后 assignment 注入，早期 assertion 先读 key；V3 的剩余断言原因尚未定位。                                   |
| 排查过程            | V2 强制逐角色重写 shell bindings 与 exact SHA，并在临时 replay 插 marker；V3 分拆 auth/review compatibility 并证明早于第一次 legacy read。                                |
| 最终处理 / 当前状态 | V3 已通过 exact SHA、artifact binding、Matrix4 bridge、compat order；当前停止，下一步只读 line-275 assertion surface。                                                    |
| 证据                | 最新终端：FROZEN_JSON_MUTATED=False 后 line 275 AssertionError；DERIVE_REPLAY_RC=1；SUBSHELL_RC=1。                                                                       |
| 以后禁止重复        | 禁止在未看到 line 275 源码前继续 patch；禁止直接 HIGH-CPU 或发布 child。                                                                                                  |

## 9.10 文件传输与 shell 噪声：No such file / codex-env.sh

| **项目**            | **内容**                                                                                                    |
|---------------------|-------------------------------------------------------------------------------------------------------------|
| 现象                | 聊天附件尚未上传到 AutoDL 时执行脚本得到 No such file；登录反复提示 /root/autodl-tmp/codex-env.sh missing。 |
| 定性                | 操作层 / shell profile 噪声；不构成科学或授权失败。                                                         |
| 根因                | ChatGPT sandbox 与 AutoDL 文件系统独立；profile 引用历史脚本缺失，但正式脚本显式激活 minesim。              |
| 排查过程            | 确认文件上传后 test -f/sha256sum；以 ENV=minesim、Python 3.9.25、Git clean 为准。                           |
| 最终处理 / 当前状态 | 不把 codex-env.sh missing 当当前 blocker；不据 No such file 推断删除。                                      |
| 证据                | 多次正式脚本均显示 ENV=minesim。                                                                            |
| 以后禁止重复        | 交付时必须明确“先下载/上传，再执行”；聊天文件不会自动出现在 AutoDL。                                        |

# 10. 由本轮错误固化出的工程标准

| **标准**                           | **执行规则**                                                                                                        |
|------------------------------------|---------------------------------------------------------------------------------------------------------------------|
| Gate / wrapper 也是软件            | bash -n 与 compile 只证明语法；必须在 exact frozen artifacts 上执行 full prestart replay，并为每个阶段输出 marker。 |
| Active binding 与 provenance 分离  | 当前 AUTH/output/evidence/capture bindings 必须零旧值；历史 freeze/decision 路径可保留旧 condition，不得全局误删。  |
| 共享 universe 与条件值分离         | \[0,1,2\]、\[20260824,20260825,20260826\] 通过 AST 保护；长 namespace token 不受该保护。                            |
| Runtime artifact filename contract | RESULT/ROOT/SHADOW 名称必须由 runtime seed 推导；active seed0/seed1 不允许硬编码错位。                              |
| Canonical shell gate               | AUTH_ROOT/AUTH/PREEXEC/CKPT/output/evidence 与 exact SHA checks 按变量角色直接重写并 shadow hash。                  |
| Compatibility 注入顺序             | legacy in-memory alias 必须紧跟初次对象 load，且证明早于第一次 legacy key read。                                    |
| Outcome-consistent RC              | PASS/0 与 FAIL/1 都进入同一 strict validation；technical_pass 仍由完整 errors closure 决定。                        |
| Matrix accounting authoritative    | 每格执行前 count 来自最新 frozen decision；capture 当前格技术有效才 +1，技术无效保持。                              |
| Post-CAPTURE 与科学结果分离        | 收尾 manifest/path Bug 不自动否定已闭合 result；先只读独立验证，禁止重跑。                                          |
| 诊断脚本也要验收                   | 字段层级、manifest path/cwd、unique filename discovery、HOLD 边界必须自检。                                         |
| 失败点之后全量 replay              | 不能“报一个修一个”；每次修复必须重放上次失败行之后全部 assertion。                                                  |
| 新版本不可变 namespace             | 失败脚本/stage 保留；修复用 V2/V3/V4 新名称，不覆盖原文件。                                                         |

## 10.1 新的正式 wrapper 交付验收清单

| **\#** | **检查域**             | **PASS 标准**                                                            |
|--------|------------------------|--------------------------------------------------------------------------|
| 1      | Shell syntax           | bash -n PASS                                                             |
| 2      | Embedded Python        | 全部 heredoc compile PASS                                                |
| 3      | Exact SHA gate         | AUTH/PREEXEC/checkpoint 实际 hash 与 child check line 完全一致           |
| 4      | Shared universes       | model/runtime lists/maps canonical，无 duplicate key                     |
| 5      | Active namespace       | current condition/output/auth/evidence 全部正向存在；旧 active binding=0 |
| 6      | Historical provenance  | 仅允许在已标记 provenance block 内出现旧 condition                       |
| 7      | Artifact filenames     | RESULT/ROOT/SHADOW 与 runtime seed 一致；active stale seed0/seed1=0      |
| 8      | Legacy compatibility   | 注入早于第一次 key read；frozen JSON mutated=False                       |
| 9      | RC/capture             | outcome-consistent gate exact；technical_pass=len(errors)==0             |
| 10     | Matrix count           | current freeze count + current technically valid condition               |
| 11     | Postcheck              | AUTHORIZATION_SHA256SUMS.txt 与 target cwd/absolute manifest path 正确   |
| 12     | Full prestart          | exact frozen replay RC=0，失败点之后所有 markers PASS                    |
| 13     | Authorization boundary | 所有 prestart PASS 后才写 START                                          |
| 14     | Process boundary       | launch=1；Pure=False；retry=False；no hidden launch                      |
| 15     | Freeze                 | 有效 science PASS/FAIL 都立即 freeze；禁止 rerun                         |

# 11. 关键路径、SHA 与状态矩阵

## 11.1 当前关键路径

| **对象**              | **路径**                                                                                                                         | **作用 / 状态**                       |
|-----------------------|----------------------------------------------------------------------------------------------------------------------------------|---------------------------------------|
| 正式 repo             | /root/MineSim-Dynamic                                                                                                            | Git tracked source；当前 HEAD clean。 |
| 主 evidence root      | /root/autodl-tmp/paper1_value_v3_development_only_v1                                                                             | 神经网络与 integration 主工作区。     |
| FIX6R3 root           | .../value_guided_mcts_c01_secondary_b8_guided_binding_fix6r3_v1                                                                  | 冻结 runner/meta/source。             |
| Protocol erratum      | .../value_guided_mcts_c01_secondary_b8_protocol_contract_erratum_decision_v1                                                     | outcome-consistent RC。               |
| Matrix3 freeze        | .../guided_r0_m20260826_postexec_freeze_fix6r3_erratum1_v2                                                                       | r0/m26 PASS，matrix=3。               |
| Matrix4 decision      | .../guided_r1_m20260824_poststart_filename_binding_discrepancy_decision_and_freeze_v1                                            | r1/m24 重分类 PASS，matrix=4。        |
| Current auth root     | .../guided_r1_m20260825_authorization_fix6r3_erratum1_artifactbinding1_v1                                                        | AUTHORIZED_NOT_STARTED。              |
| Current output        | .../guided_execution_fix6r3_v1/guided_budget8_runtime_seed1_model_seed20260825                                                   | ABSENT。                              |
| Current evidence      | .../guided_r1_m20260825_execution_evidence_fix6r3_erratum1_artifactbinding1_v1                                                   | ABSENT。                              |
| Current V3 derivation | /root/autodl-tmp/C01_GUIDED_B8_R1_M20260825_DERIVE_AND_FULL_PRESTART_REPLAY_MATRIX4_ARTIFACTBINDING1_V3.txt                      | 已执行；prestart line 275 FAIL。      |
| Intended child        | /root/autodl-tmp/C01_VALUE_GUIDED_MCTS_GUIDED_B8_R1_M20260825_START_RUN_CAPTURE_FIX6R3_STRICT_R3_MATRIX4_ARTIFACTBINDING1_V3.txt | ABSENT；不得执行。                    |

## 11.2 当前关键 SHA

| **对象**                     | **SHA256**                                                       | **状态**                   |
|------------------------------|------------------------------------------------------------------|----------------------------|
| Git HEAD                     | 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e                         | CLEAN                      |
| Integration prereg           | 0ccbded4caa5bbec28c5a6b13fde9d896983dc40f4555753e38dfe5b5e7d04bb | FROZEN                     |
| Pure B8 stability decision   | 3e17ef39f066377be2f1344a94c7d3d6eea9f61712fc52f3682218088b25e582 | FROZEN                     |
| FIX6R3 runner                | ea4d7f21265be0b2409cc2b25e6f1bd2c7ad49317d593929a34752d286d5eb79 | FROZEN                     |
| FIX6R3 meta                  | c0e1520d81ddc1b36c1e56078e2dbf1ea50c1cd6a0f2e9ad59adef5ccd25464c | FROZEN                     |
| Protocol erratum             | b847e16fa972b59ce3f12a607bc06ac3909a1f55785cd76202e0f61e4e643250 | FROZEN                     |
| R0/M25 discrepancy freeze    | 1c9eead2f384e2072c7773ab48bcca5eafdb661b4904fa12307fedce16ca41fb | FROZEN                     |
| R0/M26 postexec freeze       | da567a9e3114cbf105da22f4008cccab27708b707b45d99b0f8a1a88da0ccf83 | FROZEN PASS                |
| R1/M24 decision/freeze       | 9b81205214991e4e0934c1ddec3ae91eb76bd017938be9ef20fbd86683b23185 | FROZEN PASS                |
| Current checkpoint           | 5df90947a5fdd2bc6aa525ca5eba78b6379e127e5df6ca1d0362c992caab73b5 | FROZEN                     |
| Current auth                 | 805abb852bc410757dd4287751cd12cbf66a7000d50c9b8031c1ca902d7fa50d | AUTHORIZED_NOT_STARTED     |
| Current preexec              | 87a852f015c9bbd8088b84331c41b6e21bf3510c840eddb83721dcd48a11f415 | PASS                       |
| Current V3 derivation script | ebe8617550598b7810440804e0e035e0cfbde159dd30ef9d87ab64a5479c703f | Prestart FAIL / historical |

# 12. 资源、协作、文件与 Git 工作流

## 12.1 固定执行环境

cd /root/MineSim-Dynamic  
source /root/miniconda3/etc/profile.d/conda.sh 2\>/dev/null \|\| true  
conda activate minesim  
export PYTHONPATH=/root/MineSim-Dynamic  
export PYTHONDONTWRITEBYTECODE=1

GPU 是否启用按当前 Gate 判断。当前下一步为 LOW，只读；不需要 GPU。正式 Guided benchmark 需要 HIGH-CPU，仍设置 CUDA_VISIBLE_DEVICES=""。

## 12.2 资源判定

| **等级** | **适用范围**                                                           | **当前判断**                       |
|----------|------------------------------------------------------------------------|------------------------------------|
| LOW      | SHA/JSON/AST/schema/py_compile/preflight/freeze/auth/document/只读诊断 | 当前 line-275 diagnostic           |
| HIGH-CPU | 长 MineSim / Guided B8 one-time run                                    | 只有 full prestart PASS 后才可开启 |
| HIGH-GPU | 正式训练或明确 CUDA forward                                            | 当前不需要                         |

## 12.3 ChatGPT—用户—Codex 分工

| **角色** | **职责**                                                                            |
|----------|-------------------------------------------------------------------------------------|
| ChatGPT  | 读取证据、判断 Gate、最小 patch/脚本、PASS/FAIL、结果分析、交接文档。               |
| 用户     | AutoDL 实际执行、控制实例、上传真实输出/结果、授权重大修改/删除/重跑。              |
| Codex    | 仅复杂算法/顽固 Bug/多文件调用链/独立复核；默认 Luna medium，必要时临时 Terra/Sol。 |

## 12.4 文件与 Git 安全

- 大文件、日志、结果、bundle 放 /root/autodl-tmp；正式 repo 只保留必要源码。

- 长任务用 terminal/screen、独立 log、RC、START、CAPTURE。

- 未经授权不执行 git reset --hard / git clean -fd / git add .。

- 不原地覆盖 frozen artifact；修复使用新 versioned namespace。

- 不为目录美观删除 failed stage；删除必须 inventory→checksum→授权→delete→manifest。

- 聊天文件与 AutoDL 文件严格区分；执行前 test -f + sha256sum。

- 交互顶层禁止裸 exit；失败用子 shell 或仅打印 FAIL。

# 13. DO_NOT_REPEAT / HOLD / 不可回退项

## 13.1 最高优先级禁止事项

- 禁止重跑 2356-root one-time development training 与三个 final model training。

- 禁止重跑 C01 one-time forward；不得 best-seed、ensemble、retune。

- 禁止重跑 Pure B8 runtime seeds 0/1/2。

- 禁止重跑已消费 Guided：r0/m24、r0/m25、r0/m26、r1/m24。

- 禁止执行 R1/M20260824 正式 wrapper 再“确认”一次；其结果已冻结。

- 禁止运行当前 R1/M20260825 intended child；它尚未发布。

- 禁止重复执行 V1/V2/V3 derivation 期待不同结果；下一步必须是新的只读 diagnostic。

- 禁止删除/覆盖 START、CAPTURE、stdout/stderr/rc、checkpoint、result、metrics、SHA256SUMS、decision/freeze。

- 禁止事后增加低于 B8 的预算挽救 primary lower-budget 结论。

- 禁止根据 4 格中间数据宣称 expansion reduction / wall-clock speedup。

- 禁止把 Research/DEV map 或 diagnostic sidecar 写成 production safety guarantee。

## 13.2 当前 HOLD / NOT PROVEN

| **对象**                   | **状态**       | **解除条件**                                                  |
|----------------------------|----------------|---------------------------------------------------------------|
| Guided B8 matrix           | 4/9 完成       | 完成余下 5 个 prereg 条件。                                   |
| Current 5th child wrapper  | NOT PUBLISHED  | line-275 fault domain 明确并修复，full prestart replay RC=0。 |
| Tree expansion reduction   | NOT_EVALUATED  | 9 格完成后按 frozen aggregation 判定。                        |
| Outer wall-clock speedup   | NOT_EVALUATED  | 同上。                                                        |
| Full matrix execution      | NOT AUTHORIZED | 只允许逐条件最小 Gate。                                       |
| Production readiness       | NOT PROVEN     | 当前仅 proof-of-mechanism / research evidence。               |
| Production safety          | NOT PROVEN     | 没有生产级地图/规则/验证。                                    |
| AutoDL 最新 Word inventory | HOLD           | 本轮未执行 live inventory。                                   |

# 14. 云端文档、失败 stage 与删除情况

## 14.1 交接文档历史

| **文档**                                      | **定位**                                | **说明**                                 |
|-----------------------------------------------|-----------------------------------------|------------------------------------------|
| 2026-08-24 全项目超详细 handoff               | HISTORICAL                              | MineSim→Fleet/FullMine 主线 provenance。 |
| 2026-08-25 Value V3 2356-root handoff         | HISTORICAL / FROZEN training provenance | 训练协议与 development 结果仍有效。      |
| 2026-08-26 C01 exact metric / checker handoff | HISTORICAL                              | metric/forward 已后续 PASS。             |
| 2026-08-27 Guided B8 1/9 handoff              | HISTORICAL                              | 此前最新；当前状态已推进到 4/9。         |
| 本文件 2026-08-29 4/9 + line275 HOLD          | CURRENT                                 | 当前最新权威 handoff。                   |
| ChatGPT Conversation/Library copies           | AVAILABLE / PARTIAL                     | 不等于 AutoDL 已上传。                   |
| AutoDL handoff live inventory                 | HOLD                                    | 本轮未执行。                             |

## 14.2 Failed stages 与删除

- 本轮 V1/V2/V3 derivation、多个 diagnostic/freeze 修复 stage 均应 preserve，不删除、不覆盖。

- 此前 cleanup 的直接证据是 move/isolate/archive/quarantine；科研文件 actual delete=0（历史证据）。

- No such file、path absent、Library 无副本不能推断为“已删除”。

- 当前 failed stage 的完整 AutoDL live inventory 未重新执行，具体数量和全部路径为 HOLD。

# 15. 快速接手区（下一位 AI 必须先读）

| **接手问题**                  | **准确答案**                                                                                                 |
|-------------------------------|--------------------------------------------------------------------------------------------------------------|
| 1\. 项目现在做到哪里？        | Value V3 independent PASS；Pure B8 stable；Guided B8 secondary matrix 4/9。                                  |
| 2\. 哪些阶段无需重做？        | MineSim/Pure MCTS/单车/双车/FullMine/Fleet 历史、2356 training、C01 forward、Pure B8、前四个 Guided 条件。   |
| 3\. 当前唯一 blocker / gate？ | 第 5 格 R1/M20260825 的 full-prestart Python line 275 AssertionError；START 前。                             |
| 4\. 正式 repo？               | /root/MineSim-Dynamic                                                                                        |
| 5\. 当前 evidence root？      | /root/autodl-tmp/paper1_value_v3_development_only_v1                                                         |
| 6\. Git HEAD？                | 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e                                                                     |
| 7\. 必核 SHA？                | runner ea4d7f…；meta c0e152…；matrix4 decision 9b8120…；auth 805abb…；preexec 87a852…；checkpoint 5df909…。  |
| 8\. 哪些路径不能动？          | prereg、pure stability、FIX6R3 root、protocol erratum、四格 evidence/decision/freeze、current auth/preexec。 |
| 9\. 哪些实验禁止重跑？        | 所有已消费 one-time；尤其 Pure seeds 0/1/2 和前四格 Guided。                                                 |
| 10\. 哪些对象 HOLD？          | 第 5 格 child、剩余 5 格、secondary expansion/wall-clock、production claims。                                |
| 11\. 下一步最小行动？         | LOW：只读提取 V3 最终 prestart line 250–290 与 assert AST，定位 line 275。                                   |
| 12\. 本步 PASS 标准？         | 唯一确定 line 275 assert 源码、字段/实际值/fault domain；auth 仍未消费；无 child/START/forward/MCTS。        |
| 13\. 当前资源？               | LOW；不需要 GPU。                                                                                            |
| 14\. 开工前 preflight？       | process absent、output/evidence absent、auth consumed=False、SHA exact、Git clean、V3 child absent。         |
| 15\. FAIL 后停哪里？          | 保存完整 numbered assertion surface；不猜、不 patch、不启动 HIGH-CPU。                                       |

## 15.1 下一位 AI 的推荐动作顺序

24. 先读本节、第 6～10 节。

25. 确认用户没有在本交接后继续执行任何 R1/M20260825 修复；若有，新的 AutoDL 输出自动优先。

26. 只读核验 current auth/preexec/checkpoint/output/evidence/related process。

27. 基于 V3 生成 line-275 assertion-surface diagnostic，不生成 V4 patch。

28. 诊断 PASS 后再设计一个最小 V4；V4 必须重放 line 275 之后全部 assertions。

29. 只有 full prestart RC=0、child 原子发布后，才通知用户开启 HIGH-CPU 单次执行。

30. 正式执行后无论 Scientific PASS/FAIL，技术有效就立即 freeze；任何技术失败均禁止自动重跑。

# 附录 A｜本轮错误时间线（按发生顺序）

| **顺序** | **阶段**                         | **错误 / 事件**                                   |
|----------|----------------------------------|---------------------------------------------------|
| 1        | E19 Derivation auth audit        | AUTH_ALREADY_CONSUMED \[False, True\]             |
| 2        | E20 Strict prestart              | KeyError: fix6_runner_sha256                      |
| 3        | E21 Diagnostic                   | PRESTART_BLOCK_MATCH_COUNT=0                      |
| 4        | E22 Checkpoint/remaining adapter | expected map mismatch / bool-int mismatch         |
| 5        | E23 R0/M20260825 result          | 完整 Scientific FAIL 却 runner RC=1               |
| 6        | E24 Erratum capture patch        | technical_pass assign count=2 / candidate=0       |
| 7        | E25 Capture control flow         | 补丁打在 technical_pass 而非 outer gate           |
| 8        | E26 Prestart token audit         | AUTH SHA “缺失”                                   |
| 9        | E27 Auth checksum                | SHA256SUMS.txt missing                            |
| 10       | E28 Checksum selector            | candidate count=2                                 |
| 11       | E29 Legacy schema                | completed count=1 / review key missing            |
| 12       | E30 Shared model map             | 20260825 key 被改成 20260826                      |
| 13       | E31 R0/M20260826 postcheck       | runner/capture PASS 后 postcheck FAIL             |
| 14       | E32 Read-only diagnostic V1      | capture top-level fields=None                     |
| 15       | E33 Read-only diagnostic V2      | manifest file not found                           |
| 16       | E34 Postexec freeze V1           | stability decision missing                        |
| 17       | E35 R1/M20260824 derivation      | 旧 condition residual                             |
| 18       | E36 Residual audit               | 历史 provenance 被判 active stale                 |
| 19       | E37 R1/M20260824 capture         | seed1 runner 完整，capture 报 seed0 files missing |
| 20       | E38 R1/M20260825 V1              | EXACT SHA gate 在 auth print 前失败               |
| 21       | E39 R1/M20260825 V2              | KeyError first_guided_postexec_freeze_sha256      |
| 22       | E40 R1/M20260825 V3              | line 275 AssertionError                           |

# 附录 B｜当前下一 Gate 的最小 PASS / FAIL 标准

## B.1 当前下一条件

CONDITION=GUIDED_B8_RUNTIME_SEED1_MODEL_SEED20260825  
BUDGET=8  
RUNTIME_MCTS_SEED=1  
MODEL_SEED=20260825  
CHECKPOINT_SHA=5df90947a5fdd2bc6aa525ca5eba78b6379e127e5df6ca1d0362c992caab73b5  
AUTHORIZATION_SHA=805abb852bc410757dd4287751cd12cbf66a7000d50c9b8031c1ca902d7fa50d  
PREEXEC_REVIEW_SHA=87a852f015c9bbd8088b84331c41b6e21bf3510c840eddb83721dcd48a11f415  
MATRIX_COUNT_BEFORE=4_OF_9

## B.2 当前只读诊断 PASS 标准

| **检查项**        | **PASS 标准**                                                                     |
|-------------------|-----------------------------------------------------------------------------------|
| Preflight         | related process absent；output/evidence/child absent；Git clean；all SHAs exact。 |
| Authorization     | status=AUTHORIZED_NOT_STARTED；consumed=False；max launches=1；retry=False。      |
| Source extraction | V3 最终 prestart heredoc 与 AutoDL 执行版本一致，编号稳定。                       |
| Assertion surface | 打印 line 250–290；列出 line 275 的 assert source、依赖字段、实际值。             |
| Classification    | 明确是 schema/status/count/path/map/其他哪一类 Pre-START fault domain。           |
| Boundary          | START=False；checkpoint_loaded=False；forward=False；MCTS=False；mutation=False。 |

## B.3 FAIL 处理

- 如果 line 275 仍不能唯一定位：保存完整 numbered prestart block 与所有 assert 列表，停止。

- 如果发现多个同域 stale assertions：一次性列全，但仍不 patch，先返回证据。

- 不得直接运行正式 wrapper、不得写 START、不得开 HIGH-CPU。

# 附录 C｜完整矩阵完成后的最终评价边界

- 必须等待 9 个 Guided B8 条件全部形成技术有效的 Scientific PASS/FAIL。

- 按 prereg frozen aggregation 比较 Guided 与 Pure 的 total_tree_expansions / outer search wall-clock。

- 中间单格、单 runtime seed 或单 model seed 不得替代最终统计。

- 即使最终没有 expansion reduction，也不能否定 Value V3 的 C01 independent ranking PASS；二者是不同科学问题。

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>交接完成标准</strong></p>
<p>新 AI 只需读取 CURRENT_STATE、Guided matrix、当前 blocker、错误复盘和快速接手区，即可在不重扫全项目、不重复实验、不重问背景的情况下继续。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>
