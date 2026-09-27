**MineSim-Dynamic**

**全项目阶段性总总结与 AI 无缝接管手册**

**2026-08-26 · C01 评价数据冻结完成 / Exact Metric 三参数签名故障停点版**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>CURRENT STOP POINT</strong></p>
<p>C01 Pure-MCTS 151-root 独立评价数据集已冻结；Exact Metric / Immediate Baseline Gate 在恢复评分函数时因实际签名为 (q, pred, immediate)，而脚本错误假定为两个参数而技术 HOLD。神经网络尚未读取 C01，独立泛化结果尚未产生。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

| **字段**     | **内容**                                                                                                  |
|--------------|-----------------------------------------------------------------------------------------------------------|
| 交接版本     | V2｜完整更新至 C01 evaluation dataset freeze + exact metric signature technical HOLD                      |
| 适用对象     | 后续 ChatGPT / Codex / 工程执行人员 / 论文证据整理人员                                                    |
| 正式仓库     | /root/MineSim-Dynamic                                                                                     |
| 科研数据根   | /root/autodl-tmp/paper1_value_v3_development_only_v1                                                      |
| Git HEAD     | 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e                                                                  |
| 证据截止     | 2026-08-26；最新执行证据为 C01 exact metric closure Gate RC=1，故障为 callable signature mismatch         |
| 当前允许动作 | LOW / 只读或静态诊断：恢复 (q, pred, immediate) 的真实调用与返回契约，先处理可能遗留的 stage namespace    |
| 当前禁止动作 | 不得重训、不得重跑 C01 MCTS collection、不得运行旧 metric Gate、不得提前执行 Value forward、不得接入 MCTS |

内部科研交接材料｜所有 PASS / HOLD 均以冻结 JSON、START/CAPTURE、SHA256 和最新终端为准

# **0. CURRENT_STATE｜一页接手摘要**

| **字段**              | **当前值**                                                                             | **接管解释**                                                                      |
|-----------------------|----------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| CURRENT_STAGE         | Value V3 brand-new independent scene C01 evaluation                                    | C01 标签采集和评价数据已完成；当前正在冻结评分尺子，而不是继续训练或重新跑 MCTS。 |
| LATEST_FROZEN_PASS    | C01 Pure-MCTS postexec acceptance + 151-root evaluation dataset                        | 数据集 SHA=1427901d...；151 roots、2,416 action rows；Value 未参与采集。          |
| CURRENT_GATE_RESULT   | Exact metric closure Gate：RC=1 / TECHNICAL HOLD                                       | 所有输入 SHA 与 namespace gate 通过；失败发生在评分 callable 接口审计。           |
| EXACT_FAILURE         | AssertionError: METRIC_SIGNATURE_NOT_TWO_PARAMETERS; actual='(q, pred, immediate)'     | 脚本错误假定评分函数只有两个参数；不是 C01 数据、模型、MCTS 或科学结果失败。      |
| PUBLISHED_METRIC_ROOT | ABSENT / 未原子发布                                                                    | 失败发生在 stage 内部；正式 metric freeze 与 C01 immediate baseline 均未生成。    |
| POSSIBLE_STAGE        | .independent_scene_c01_value_v3_metric_and_immediate_baseline_v1.stage.\* 可能遗留     | 下一执行人员先做 live inventory；禁止直接再次执行原 Gate。                        |
| VALUE_STATUS          | 3 个 full-development final models 已冻结；C01 forward 未授权、未执行                  | 网络已经训练好，但还没参加 C01 这场独立考试。                                     |
| SCIENTIFIC_STATUS     | INDEPENDENT_GENERALIZATION_PASS=False / NOT EVALUATED                                  | 目前不能称独立泛化 PASS、production ready 或 MCTS-integrated。                    |
| NEXT_MINIMAL_ACTION   | LOW：Exact metric 3-parameter source/call-site/return-contract audit + FIX1 derivation | 先恢复原评分函数，不猜公式，不加载 checkpoint。                                   |
| RESOURCE              | LOW；GPU 不需要                                                                        | 真正 Value forward 的资源与命令要由后续冻结 harness 再确定。                      |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>30 秒解释</strong></p>
<p>神经网络训练和最终三模型都已经结束；C01 的 MCTS “标准答案”也已经采集并整理成考试数据。当前卡住的是评分程序的接口：真实评分函数需要 q、pred、immediate 三个输入，而刚才的冻结脚本只按两个输入设计。因此现在要修“评分尺子”，不是重训网络，也不是重跑 C01。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## **0.1 当前对象状态矩阵**

| **对象**                                          | **状态**                   | **当前含义**                                                   |
|---------------------------------------------------|----------------------------|----------------------------------------------------------------|
| **2356-root Value V3 development training**       | **CONSUMED / FROZEN PASS** | 9-fold 正式训练完成；3/3 development scene win；绝对不得重跑。 |
| **3 个 full-development final models**            | **CONSUMED / FROZEN PASS** | 固定 seeds 20260824/25/26；无 best-seed selection。            |
| **C01 physical / static / NO-MCTS qualification** | **FROZEN PASS**            | 场景、静态可行驶性和真实 causal conflict 已冻结。              |
| **C01 Pure-MCTS target collection**               | **FROZEN PASS**            | 技术恢复后唯一成功执行；151 roots；Value 未参与。              |
| **C01 independent evaluation dataset**            | **FROZEN PASS**            | 151×12 state；151×16 Q/immediate；root_step 0..150。           |
| **Exact metric closure**                          | **TECHNICAL HOLD**         | 实际 callable=(q,pred,immediate)，旧 Gate 的两参数断言错误。   |
| **C01 immediate baseline**                        | **NOT FROZEN**             | 尚未得到任何可用 baseline 数值。                               |
| **C01 Value forward harness**                     | **NOT CREATED**            | 必须等 metric/baseline freeze 完成。                           |
| **C01 Value forward authorization**               | **NOT AUTHORIZED**         | 不得手工加载三个 checkpoint 试跑。                             |
| **C01 Value forward**                             | **NOT EXECUTED**           | C01 数据仍保持未被网络查看的独立测试状态。                     |
| **Independent generalization**                    | **NOT EVALUATED**          | 没有 PASS 或 FAIL 结果。                                       |
| **MCTS Value integration**                        | **FALSE / FORBIDDEN**      | 独立验证完成前永久保持 False。                                 |

## **0.2 本版相对上一交接文档的关键更新**

- C01 authoritative static bitmap qualification 已完成并冻结 PASS；不再停留在 checker pre-authorization。

- C01 NO-MCTS causal conflict 已完成并冻结 PASS，确认同一路口在恒速无规划基线下产生真实物理重叠。

- Value V3 final full-development 3-seed models 已训练、捕获并 postexec freeze；C01 数据未进入训练。

- C01 Pure-MCTS target collection 已经经历一次 argparse 技术失败和一次独立技术恢复；恢复执行 RC=0、151 roots。

- C01 independent evaluation NPZ 已原子发布并冻结；当前唯一故障域已前移到 exact metric / immediate baseline。

- 最新失败是新 Gate 自身的参数数量假设错误，不改变任何既有 frozen science。

# **1. 文档控制、证据等级与冲突处理**

## **1.1 本版主要证据源**

| **证据**                                                          | **用途**                                               | **可信边界**                     |
|-------------------------------------------------------------------|--------------------------------------------------------|----------------------------------|
| 最新 AutoDL 终端：C01 postexec dataset freeze + exact metric Gate | 确定当前 live stop point、RC、SHA gate、失败断言       | 最新执行证据优先。               |
| C01 evaluation dataset freeze objects                             | 确定 151-root NPZ、manifest、freeze 与 SHA             | 正式原子发布对象。               |
| C01 recovery START/CAPTURE/raw SHA manifests                      | 确定唯一成功 MCTS collection 的过程与文件完整性        | 不可删除或覆盖。                 |
| 2356-root Value V3 development / final-model freezes              | 确定训练、模型、normalization、seed 和 checkpoint 边界 | 不得重训或 best-seed。           |
| 上一版全项目 AI 无缝接管手册                                      | 提供 C01 static checker 以前的历史主线                 | 其中“当前状态”已过期，本版取代。 |
| 2026-08-25 神经网络阶段性交接文档                                 | 提供 2356-root 训练协议和 development 结果             | 只用于已冻结 development 事实。  |

## **1.2 事实优先级**

| **优先级** | **证据类型**                                            | **处理规则**                                          |
|------------|---------------------------------------------------------|-------------------------------------------------------|
| 1          | 最新实际终端 / Git / 源码 / SHA / 真实输出              | 与旧交接冲突时，以最新实际证据为准。                  |
| 2          | START / CAPTURE / freeze / manifest / lock / SHA256SUMS | 正式 frozen science 与 one-time execution 边界。      |
| 3          | 历史终端日志、review/audit sidecar                      | 用于 provenance 与故障域，不自动升级为当前科学结论。  |
| 4          | 交接文档叙述                                            | 只做导航；不得覆盖上级证据。                          |
| 5          | 模型推断或自然语言猜测                                  | 没有 exact source / artifact 支持时不得写入冻结结论。 |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>严谨边界</strong></p>
<p>本交接文档不能访问 AutoDL 的实时文件系统，因此“可能存在失败 stage”必须由下一位执行者现场核验。正式 METRIC_ROOT 因未到 atomic publish 可以判定未发布；但隐藏 stage 是否遗留，不能从当前终端片段直接断言不存在。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## **1.3 Technical HOLD 与 Scientific FAIL 的区分**

| **类别**              | **本项目定义**                                                               | **当前案例**                                                            |
|-----------------------|------------------------------------------------------------------------------|-------------------------------------------------------------------------|
| Technical HOLD / FAIL | 代码、接口、SHA、namespace、启动命令或捕获链问题；没有得到可解释科学结果。   | 当前 metric Gate 将真实三参数 callable 错判为两参数，属于技术接口错误。 |
| Scientific FAIL       | 协议正确执行后，冻结指标未达到预注册 PASS 条件。                             | C01 尚未执行 Value forward，因此没有独立泛化 Scientific FAIL。          |
| Scientific PASS       | 协议、数据、模型、metric、aggregation 与阈值均预先冻结，真实执行后满足条件。 | 当前只存在 development-ready PASS；C01 independent PASS 尚未产生。      |

## **1.4 推荐阅读顺序**

1\. 先读第 0 节，确认当前停点与禁止事项。

2\. 再读第 7～9 节，掌握 C01 collection、dataset 和最新 exact metric 故障。

3\. 执行人员必须读第 10～13 节：路径/SHA、namespace、资源和 DO_NOT_REPEAT。

4\. 只有 SHA 冲突或 provenance 不清时，才回查第 3～6 节历史与 C01 全链。

5\. 最后按第 14 节“快速接手区”做一个最小 LOW Gate，不得跳步。

# **2. 项目主线总览（按真实演进组织）**

| **阶段**                                | **状态**                      | **当前真实结论**                                                     |
|-----------------------------------------|-------------------------------|----------------------------------------------------------------------|
| MineSim 基础复现                        | PASS / FROZEN                 | IDM baseline、replay、closed-loop 基础环境已建立；不重做。           |
| Pure MCTS / 单车                        | PASS / FROZEN                 | 真实 MineSim online closed-loop 和 search/reward/controller 链跑通。 |
| 双车 Fleet-MCTS                         | PASS + 负结果并存             | C04/C06 成功；C11 safety deadlock 负结果保留。                       |
| Value V2 independent validation         | SCIENTIFIC FAIL / CLOSED      | C03 真实失败；DO_NOT_INTEGRATE；禁止“修成 PASS”。                    |
| Value V3 2356-root development          | CONSUMED / FROZEN PASS        | 6 episodes、9 folds、3/3 scene win、DEVELOPMENT_READY=True。         |
| Value V3 final full-development fit     | CONSUMED / FROZEN PASS        | 3 个固定 seed 全数据模型已训练并冻结。                               |
| C01 blind selection / physical / static | FROZEN PASS                   | source_index=1；场景、静态资产、bitmap truth 均固定。                |
| C01 NO-MCTS causal baseline             | FROZEN PASS                   | 恒速无规划基线真实重叠，证明场景具备 causal conflict。               |
| C01 Pure-MCTS target collection         | FROZEN PASS                   | 技术恢复后唯一成功执行；151 roots；collision avoided。               |
| C01 independent evaluation dataset      | FROZEN PASS                   | 与 development adapter 完全同 schema；网络尚未读取。                 |
| C01 exact metric / immediate baseline   | TECHNICAL HOLD                | 真实 callable 为 (q,pred,immediate)；当前 Gate 参数假设错误。        |
| C01 Value forward                       | NOT AUTHORIZED / NOT EXECUTED | 待 metric baseline freeze 与静态 harness/authorization。             |
| MCTS Value integration                  | FALSE / FORBIDDEN             | 独立评估前禁止接入或宣称效率提升。                                   |

## **2.1 当前可以写进论文或汇报的结论**

- Value V3 已完成 development-stage 2356-root episode-aware 验证，并在 C04/C11/C06 三个 development scenes 上以三固定 seed 中位数优于 frozen immediate baseline。

- C01 是未参与 Value V3 development 设计/训练的独立场景；其物理、静态、causal conflict 与 Pure-MCTS target collection 链均已完成。

- C01 151-root evaluation dataset 已冻结，可作为后续独立模型评估输入。

- 到当前为止没有任何 C01 neural prediction，因此不能写“Value V3 在 C01 上泛化成功”。

## **2.2 当前绝对不能写的结论**

- 不能称 Value V3 independent-generalization PASS。

- 不能称 production ready、safety proven、deployment model 或 production-authoritative HD-map validation。

- 不能称 Neural-MCTS 已完成，或已证明减少 MCTS 计算量。

- 不能把 C01 Pure-MCTS 运行成功当成 Value V3 的成绩。

- 不能因 current metric Gate 技术失败而否定已冻结的 C01 dataset、MCTS collection 或 Value V3 development model。

# **3. 运行架构、数据链与科学边界**

## **3.1 MineSim 主运行链**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>run_simulation.py<br />
-&gt; SimulationsRunner._initialize()<br />
-&gt; EnvironmentSimulation.initialize()<br />
-&gt; Scenario / Map loader<br />
-&gt; Planner.initialize()<br />
-&gt; Planner.compute_planner_trajectory()<br />
-&gt; TwoStageController.update_state()<br />
-&gt; LQR / iLQR trajectory tracking<br />
-&gt; KinematicBicycleModel.propagate_state()<br />
-&gt; Agent Update Policy / Observation<br />
-&gt; SimulationHistory / metrics / log<br />
-&gt; next frame</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## **3.2 Value V3 独立评价链**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>C01 scenario/static/no-MCTS qualification<br />
-&gt; Pure-MCTS target collection (Value not used)<br />
-&gt; raw root JSONL: 151 roots x 16 actions<br />
-&gt; exact adapter -&gt; C01 frozen NPZ<br />
-&gt; exact metric closure + immediate baseline [CURRENT HOLD]<br />
-&gt; static Value forward harness<br />
-&gt; one-time authorization<br />
-&gt; 3 fixed final-model seeds, separate forward<br />
-&gt; per-seed normalized regret<br />
-&gt; median of 3 fixed seeds<br />
-&gt; compare with frozen C01 immediate baseline<br />
-&gt; PASS / Scientific FAIL<br />
-&gt; only then discuss MCTS integration</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## **3.3 永久边界**

| **边界**         | **当前处理规则**                                                                             |
|------------------|----------------------------------------------------------------------------------------------|
| Planner 与执行器 | 搜索轨迹合法不等于 Controller/KBM 可实现；故障必须分层。                                     |
| 双车 truth       | B 的真实状态不得由 A history 推断；每个受控车辆 observation/history 独立。                   |
| 时空冲突         | 路径几何相交不自动等于 temporal conflict；必须有 NO-MCTS causal evidence。                   |
| Safe 与 success  | 无碰撞不等于任务完成；deadlock 可以是 scientific FAIL。                                      |
| Static truth     | frozen V4 bitmap + XG90G physical footprint 为 primary truth；CollisionLookup 仅 secondary。 |
| Research map     | 不得表述为生产级官方 HD map 或生产可行驶真值。                                               |
| Value target     | Pure-MCTS Q 是目标；Value 不得参与 target collection。                                       |
| Independent test | C01 在评分规则、baseline 和 decision gate 冻结前不得被 final models 查看。                   |

## **3.4 关于终端提示符 \`(base)\`**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>环境说明</strong></p>
<p>Gate 内部日志显示 ENV=minesim、Python=3.9.25，说明脚本在 subshell 中已正确激活 minesim。脚本结束后返回父 shell 时提示符仍可能显示 `(base)`，这不是本次故障，也不代表 Gate 在 base 环境执行。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# **4. 神经网络主线：Value V3 development 与 final models**

## **4.1 用通俗话说明神经网络做到哪里**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>一句话</strong></p>
<p>网络已经训练完并冻结，三套最终模型也已保存；C01 的标准答案数据已经准备好，但评分规则还没成功冻结，所以网络还没正式参加 C01 这场独立考试。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## **4.2 2356-root development dataset**

| **Episode UID**    | **Scene** | **Roots** | **角色**           |
|--------------------|-----------|-----------|--------------------|
| C04_FROZEN_EP0     | C04       | 126       | 历史冻结 episode   |
| C04_SEED5_EP1      | C04       | 148       | coverage expansion |
| C11_80M_SEED0_EP0  | C11       | 890       | 80 m episode       |
| C11_100M_SEED0_EP1 | C11       | 890       | 100 m episode      |
| C06_FROZEN_EP0     | C06       | 146       | 历史冻结 episode   |
| C06_SEED1_EP1      | C06       | 156       | coverage expansion |
| 合计               | \-        | 2,356     | 37,696 action rows |

## **4.3 冻结训练协议**

| **项目**        | **冻结值**                                                               |
|-----------------|--------------------------------------------------------------------------|
| Model           | ActionConditionedValueV3PairwiseRank                                     |
| Architecture    | 12 -\> 64 -\> 64 -\> 16                                                  |
| Objective       | ROOT_NORMALIZED_WEIGHTED_PAIRWISE_LOGISTIC                               |
| Split           | LEAVE_ONE_SCENE_OUT                                                      |
| Seeds           | 20260824 / 20260825 / 20260826                                           |
| Epochs / LR     | 600 / 0.001                                                              |
| Best-seed / HPO | False / False                                                            |
| Normalization   | 每个 heldout fold 仅使用 train roots pooled mean/std；zero std guard=1.0 |

## **4.4 Development 科学结果**

| **Scene** | **3 seeds normalized regret**           | **Median**  | **Frozen immediate baseline** | **结论** |
|-----------|-----------------------------------------|-------------|-------------------------------|----------|
| C04       | 0.181987592 / 0.155618844 / 0.174277542 | 0.174277542 | 0.273804418                   | WIN      |
| C11       | 0.116699341 / 0.120093067 / 0.117458957 | 0.117458957 | 0.181778548                   | WIN      |
| C06       | 0.088145494 / 0.128795213 / 0.122468490 | 0.122468490 | 0.241806713                   | WIN      |

- VALUE_V3_SCENE_WIN_COUNT=3；PRIMARY_GATE=True；SECONDARY_GATE=True；DEVELOPMENT_READY=True。

- 该结果支持 development candidate，不等于 C01 independent-generalization。

- 9 个 LOSO checkpoints 只用于 cross-validation，不能当作 final deployment models。

## **4.5 Final full-development 3-seed models**

| **Seed** | **Checkpoint 路径**                                                                    | **SHA256**                                                       | **状态** |
|----------|----------------------------------------------------------------------------------------|------------------------------------------------------------------|----------|
| 20260824 | value_v3_full_development_final_candidate_v1/seed_20260824_final_all2356/checkpoint.pt | 496e4259eb9801f3ce70c1094be12fd0985cb03e97d606cade8dfbe9d5228633 | FROZEN   |
| 20260825 | value_v3_full_development_final_candidate_v1/seed_20260825_final_all2356/checkpoint.pt | 5df90947a5fdd2bc6aa525ca5eba78b6379e127e5df6ca1d0362c992caab73b5 | FROZEN   |
| 20260826 | value_v3_full_development_final_candidate_v1/seed_20260826_final_all2356/checkpoint.pt | 3881d39c09b02a513e44f0fe612aad42de9ff636fd07e314d327b4c6d5f132df | FROZEN   |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>Final model policy</strong></p>
<p>三个 fixed-seed final models 必须分别在 C01 上前向，随后只对三个 normalized regret 取中位数。禁止 best-seed selection；是否做 inference ensemble 已冻结为 False。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# **5. C01 独立场景：qualification 与 frozen protocol**

## **5.1 C01 选择边界**

- C01/source_index=1 由 blind ascending source-index rule 选择，不按性能筛选。

- C01 未参与 2356-root development scene set（C04/C11/C06）。

- Historical C03/C13 只提供算法和 harness provenance，科学结果不能复制给 C01。

## **5.2 已冻结 qualification**

| **对象**                             | **状态**        | **当前含义**                                                       |
|--------------------------------------|-----------------|--------------------------------------------------------------------|
| **C01 scenario / manifest / bundle** | **FROZEN PASS** | 双车 route、initial speed、approach 和 conflict identity 已固定。  |
| **Static bitmap qualification**      | **FROZEN PASS** | A/B XG90G physical footprint 在 frozen bitmap 上可行。             |
| **NO-MCTS causal conflict**          | **FROZEN PASS** | 恒速基线产生真实 physical overlap，并完成 post-conflict。          |
| **Current-semantic zone contract**   | **FROZEN PASS** | Omega_int / Omega_app 与 development semantic 回归通过。           |
| **Pure-MCTS collection harness**     | **FROZEN PASS** | canonical C06 parent；C01 scene/evidence/zone 绑定；Value absent。 |

## **5.3 C01 zone contract**

| **Zone**  | **Vehicle A route_s**                     | **Vehicle B route_s**                    |
|-----------|-------------------------------------------|------------------------------------------|
| Omega_int | \[148.16486148617483, 217.7019464945087\] | \[34.3714315185727, 98.7650537953662\]   |
| Omega_app | \[135.6624002793114, 217.7019464945087\]  | \[17.405306611374414, 98.7650537953662\] |

## **5.4 C01 target collection protocol**

| **项目**                         | **冻结值**                                     |
|----------------------------------|------------------------------------------------|
| source_index / seed              | 1 / 0                                          |
| MCTS budget / depth              | 64 / 8                                         |
| c_uct / gamma                    | 1.4 / 0.99                                     |
| MCTS dt                          | 0.5 s                                          |
| Joint actions                    | 16；index=A\*4+B                               |
| Primary target                   | actionwise\[joint_action_id\].q_value          |
| Immediate baseline source        | actionwise\[joint_action_id\].immediate_reward |
| Value model used in collection   | False                                          |
| Retry / rerun for better science | False / False                                  |

# **6. C01 Pure-MCTS target collection：原授权失败与技术恢复**

## **6.1 原一次性授权的技术失败**

| **节点**               | **结果**                                        | **科学含义**                                   |
|------------------------|-------------------------------------------------|------------------------------------------------|
| Original authorization | SHA=d0529a77...；1 process / 1 episode          | 授权本身冻结。                                 |
| Original START         | SHA=b1e71272...；authorization consumed forever | 原授权不可复用。                               |
| Actual argv            | \[python, runner\]                              | 遗漏 runner 必需的 --source-index。            |
| Runner                 | RC=2；argparse missing --source-index           | 在 MCTS constructor 前退出。                   |
| Raw output             | 0 files / 0 roots                               | 没有产生任何科学标签。                         |
| Failure freeze         | SHA=1f549f9b...                                 | 分类为 execution-interface technical failure。 |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>关键判定</strong></p>
<p>原失败不是 C01 科学失败：parse_args() 先于 RootDiagnosticCollectorFleetMCTSSearchV1 构造，故 MCTS search 未进入，Value 也未使用。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## **6.2 独立技术恢复**

| python runner.py --source-index 1 --seed 0 |
|--------------------------------------------|

| **对象**               | **SHA / 结果**                                                   |
|------------------------|------------------------------------------------------------------|
| Recovery authorization | 58e26185d55d20d10afb9ac6e76ec01963b3fc95fdfb97bfbd27a4fcbd26d05d |
| Recovery START         | b95e728c24c794d73a0f34ad7f70b5c9d932f6497931111cba99b581b0cbcb61 |
| Recovery CAPTURE       | 7cfaa8899be6f4b02db9246222e7f5a4bc6dcfc211fec5e152ad339b2c5935fb |
| Evidence SHA256SUMS    | 4413f27bde98c36e4e233c62df2e7befc0d5eccb366138107ad128e59f51977c |
| Raw SHA256SUMS         | 17b8c5ecf3a736699d1f6cd255c38ba79e6b332cbdd296c64dc769ba7b921fe3 |

## **6.3 Recovery 实际结果**

| **指标**                            | **结果**                      |
|-------------------------------------|-------------------------------|
| Runner RC                           | 0                             |
| Root count / action rows            | 151 / 2,416                   |
| Root steps                          | 0..150 contiguous             |
| Actions per root                    | 16；canonical IDs 0,0 ... 3,3 |
| Q / immediate                       | finite / finite               |
| Benchmark success                   | True                          |
| Collision avoided                   | True                          |
| Physical overlap                    | False                         |
| Minimum footprint clearance         | 2.065002410173625 m           |
| Crossing time gap                   | 5.236610008665906 s           |
| Episode selected/filtered after run | False                         |
| Value model used                    | False                         |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>解释边界</strong></p>
<p>上述 PASS 是 Pure-MCTS 目标采集 episode 的真实结果，证明标签采集过程有效；它不是 Value V3 在 C01 上的预测结果，也不能直接证明神经网络提高了效率或安全性。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# **7. C01 independent evaluation dataset：已冻结**

## **7.1 Schema**

| **Key**          | **Shape** | **Dtype / identity**               |
|------------------|-----------|------------------------------------|
| state            | (151, 12) | float32                            |
| q_value          | (151, 16) | float32                            |
| immediate_reward | (151, 16) | float32                            |
| scene            | (151,)    | C01                                |
| episode_uid      | (151,)    | C01_SEED0_EP0                      |
| root_step        | (151,)    | int64；0..150                      |
| feature_names    | (12,)     | 与 development adapter exact match |

## **7.2 Frozen objects**

| **对象**             | **路径**                                                                                                                                 | **SHA256**                                                       |
|----------------------|------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------|
| Dataset              | independent_scene_c01_value_v3_evaluation_dataset_v1/paper1_value_v3_c01_independent_episode_aware_root_dataset_v1.npz                   | 1427901d6eda446967c87a75c98b4fd066b01d0daf3a0041f11e145858e3f0f0 |
| Manifest             | independent_scene_c01_value_v3_evaluation_dataset_v1/PAPER1_VALUE_V3_C01_INDEPENDENT_ROOT_DATASET_MANIFEST_V1.json                       | fd4a2c6794e0d2805fda3314da58167d13fe6c9b925fa3d36df0568554a6bfda |
| Postexec/data freeze | independent_scene_c01_value_v3_evaluation_dataset_v1/PAPER1_VALUE_V3_C01_PURE_MCTS_TARGET_COLLECTION_POSTEXEC_AND_DATASET_FREEZE_V1.json | 94ca80de05580fe91d9937fcf3883b329d6cdd93c2c2bd908510bf57622d0fe1 |
| SHA256SUMS           | independent_scene_c01_value_v3_evaluation_dataset_v1/SHA256SUMS.txt                                                                      | fe490031ce64a0a5179f95aaad0e8af458ce5c4c144ac4d41644d42adfd0f63c |

## **7.3 Content fingerprints**

| **Array**        | **Content SHA256**                                               |
|------------------|------------------------------------------------------------------|
| state            | 105f747fc3dd37ae6bf102b145fe4d0ff9fcdcd65ed9a503e7376d41d77576c2 |
| q_value          | 4dfd8939658f3dc72389d89c1dbaf4fde18ec7b26e4cd630e93e64bc0a88b96f |
| immediate_reward | 3f06555235ae16a50dc08a3a96c25ec0d776223d50959e6e969dbf5b524e5748 |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>当前数据边界</strong></p>
<p>C01 dataset 已经准备好，但“准备好数据”不等于“可以直接跑网络”。评分函数、immediate baseline、三 seed aggregation 和严格 PASS operator 必须先冻结。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# **8. 当前精确停点：Exact Metric 三参数签名故障**

## **8.1 本次 Gate 已通过的部分**

- Git HEAD、tracked clean、minesim Python 环境全部通过。

- METRIC_ROOT、future Value namespaces 在 Gate 开始时均 absent。

- C01 dataset / manifest / freeze / SHA256SUMS 全部 exact SHA PASS。

- Development dataset、training harness、baseline freeze、derivation contract、summary、closure 全部 exact SHA PASS。

- C01 preregistration 与 final-model freeze exact SHA PASS。

- C01 dataset SHA256SUMS 完整校验 PASS。

## **8.2 失败原文**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>========== EXACT METRIC RECOVERY + DEVELOPMENT REGRESSION ==========<br />
Traceback (most recent call last):<br />
File "&lt;stdin&gt;", line 163, in &lt;module&gt;<br />
AssertionError: ('METRIC_SIGNATURE_NOT_TWO_PARAMETERS', '(q, pred, immediate)')<br />
SUBSHELL_RC=1</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## **8.3 精确故障分类**

| **字段**                  | **判定**                                                                         |
|---------------------------|----------------------------------------------------------------------------------|
| FAULT_DOMAIN              | EXACT_METRIC_INTERFACE / RECOVERY_GATE_ASSUMPTION                                |
| 错误假设                  | 脚本要求 recovered callable 只有两个参数。                                       |
| 真实接口                  | (q, pred, immediate)                                                             |
| 失败位置                  | inspect.signature(metric_fn) 后的参数数量断言；尚未进入 development regression。 |
| C01 baseline              | 未计算、未冻结。                                                                 |
| Value checkpoint          | 未加载。                                                                         |
| C01 Value forward         | 未授权、未执行。                                                                 |
| MCTS                      | 本 Gate 未执行。                                                                 |
| Scientific outcome        | NOT OBSERVED；不能判定 independent PASS/FAIL。                                   |
| Published metric artifact | 无；atomic publish 未到达。                                                      |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>为什么不能直接把断言改成 3</strong></p>
<p>虽然签名顺序已经显示 q、pred、immediate，但还必须从 frozen function body 和历史 call site 确认：第三参数如何参与 normalized regret、返回对象有哪些字段、immediate baseline 是函数内部输出还是外部另算。仅凭参数名猜调用语义，会改变评分协议。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## **8.4 当前已知与未知**

| **类别**   | **内容**                                                                                                                  |
|------------|---------------------------------------------------------------------------------------------------------------------------|
| 已知       | byte-exact 2356 training harness 中 load_exact_metric_closure() 返回 callable。                                           |
| 已知       | 返回 callable 的 inspect.signature 为 (q, pred, immediate)。                                                              |
| 已知       | development 输出包含 normalized_regret 与 immediate_regret；历史 PASS 以 normalized regret 对 frozen immediate baseline。 |
| 未知       | callable 内部对三个数组的 exact shape/dtype/ordering/assertions。                                                         |
| 未知       | callable 返回 dict 的 exact schema 与 normalized_regret 字段路径。                                                        |
| 未知       | C01 immediate baseline 的 exact 调用方式与最终数值。                                                                      |
| 待核验推断 | 三参数设计可能用于同一次调用同时计算模型 regret 与 immediate baseline；必须由源码确认，不能作为修复依据。                 |

## **8.5 Namespace 风险**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>正式目标 root（未发布）：<br />
/root/autodl-tmp/paper1_value_v3_development_only_v1/<br />
independent_scene_c01_value_v3_metric_and_immediate_baseline_v1<br />
<br />
可能遗留的失败 stage pattern：<br />
/root/autodl-tmp/paper1_value_v3_development_only_v1/<br />
.independent_scene_c01_value_v3_metric_and_immediate_baseline_v1.stage.*</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

- 脚本在调用失败前已经执行 mkdir -p "\$STAGE"，因此 stage 可能存在。

- 下一个 Gate 必须先只读 inventory；不得直接运行原脚本，因为它既可能被 stage guard 拦截，也会重复同一错误假设。

- 若 stage 存在，清理、隔离或复用必须写入独立 technical recovery contract，不能手工 rm 后假装没有发生。

# **9. 下一最小 Gate：Exact Metric 3-parameter recovery**

## **9.1 只允许的下一步**

- LOW / read-only：检查 metric root、失败 stage、Value/MCTS 进程和 future namespaces。

- AST/source audit：读取 byte-exact training harness 的 load_exact_metric_closure() 698–768 行。

- 读取 returned callable 的 source/bytecode/signature/return schema，不调用 build_model/train_fold/execute_development。

- 定位 frozen development harness 中该 callable 的历史 call site，确认 q、pred、immediate 的 exact shape 与顺序。

- 用 development dataset 重算 C04/C11/C06 immediate baseline，必须恢复 0.273804418 / 0.181778548 / 0.241806713。

- 回归全部通过后，才能计算并冻结 C01 immediate baseline。

- 在任何 Value forward 前，冻结 3 fixed seeds separate evaluation、median aggregation、strict \`\<\` PASS operator、equality=Scientific FAIL。

## **9.2 下一 Gate 的最小 PASS 标准**

| **检查项**             | **PASS 标准**                                                                 |
|------------------------|-------------------------------------------------------------------------------|
| Namespace              | 正式 METRIC_ROOT absent；失败 stage 已被明确分类；future Value roots absent。 |
| Source identity        | training harness SHA=753bcf28...；loader source/AST/code SHA 写入证据。       |
| Callable contract      | exact signature=(q,pred,immediate)；参数角色与 return schema 唯一明确。       |
| No neural execution    | checkpoint loaded=False；build_model/train_fold/execute_development 未调用。  |
| Development regression | C04/C11/C06 三场 exact immediate baseline 全部复现 frozen values。            |
| C01 baseline           | 151-root immediate baseline finite，并原子发布 freeze。                       |
| Decision rule          | 3 fixed seeds separately；median；PASS iff median \< baseline；tolerance=0。  |
| Boundary               | Value forward authorized=False；executed=False；integration=False。           |

## **9.3 只读现场检查命令**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>V3=/root/autodl-tmp/paper1_value_v3_development_only_v1<br />
<br />
find "$V3" -maxdepth 1 -name '.independent_scene_c01_value_v3_metric_and_immediate_baseline_v1.stage.*' -print<br />
test -e "$V3/independent_scene_c01_value_v3_metric_and_immediate_baseline_v1" &amp;&amp; echo METRIC_ROOT_PRESENT || echo METRIC_ROOT_ABSENT<br />
test -e "$V3/independent_scene_c01_value_v3_evaluation_v1" &amp;&amp; echo EVAL_ROOT_PRESENT || echo EVAL_ROOT_ABSENT<br />
ps -eo pid,etime,%cpu,%mem,args | grep -Ei 'value.*v3.*c01|c01.*value.*v3|fleet_mcts' | grep -v grep || true</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>当前不要执行的命令</strong></p>
<p>不要再次运行 C01_VALUE_V3_EXACT_METRIC_CLOSURE_AND_IMMEDIATE_BASELINE_FREEZE_V1.txt。该文件 SHA=9878a968...，其两参数断言已被实际证据证明错误。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# **10. 关键路径与 SHA256 速查**

## **10.1 Development 与 final-model chain**

| **对象**                    | **相对 V3 root 路径**                                                                                                                           | **SHA256**                                                       |
|-----------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------|
| 2356 dataset                | expanded_2356_development_input_v1/paper1_value_v3_expanded_2356_episode_aware_root_dataset_v1.npz                                              | 106936a30e4c55b10b7968de2534e822c262db50c21494cca354700d78a70a27 |
| 2356 manifest               | expanded_2356_development_input_v1/PAPER1_VALUE_V3_EXPANDED_2356_EPISODE_AWARE_ROOT_DATASET_MANIFEST_V1.json                                    | 0828fe303cfef86bd35144a31bb4e62022a9f3ac5521abec71f46a14c401a1ea |
| 2356 dataset freeze         | expanded_2356_development_input_v1/PAPER1_VALUE_V3_EXPANDED_2356_EPISODE_AWARE_ROOT_DATASET_FREEZE_V1.json                                      | fe6652e6057f95c0113d7594cce8bb1b6e5e3b457fbdee3ba7c4981c8662c12d |
| Adapter build contract      | expanded_2356_adapter_build_contract_v1/PAPER1_VALUE_V3_2356_ROOT_EPISODE_AWARE_ADAPTER_BUILD_CONTRACT_V1.json                                  | 9c5ea534dd4388d6d6ea3274bfb23a67bcbd45887b99fa3602570088e2bbb3f3 |
| Immediate baseline freeze   | expanded_2356_baseline_harness_derivation_contract_v1/PAPER1_VALUE_V3_2356_IMMEDIATE_BASELINE_FREEZE_V1.json                                    | 97194bcb671953cf44f4c8741712f840b75fde4d0a04077af6b6bf3d0da6abee |
| Harness derivation contract | expanded_2356_baseline_harness_derivation_contract_v1/PAPER1_VALUE_V3_2356_HARNESS_DERIVATION_CONTRACT_V1.json                                  | 1d2d816821e06a876ca436a51a0cf2be8ea6aa0e41686793618a5b5576b80d03 |
| Training harness            | expanded_2356_harness_static_v1/paper1_value_v3_pairwise_rank_training_pipeline_expanded_2356_v1.py                                             | 753bcf28eb689a86291b55e8c6c9f8578e9333c978cbd3253743c747ebfd400c |
| Development summary         | expanded_2356_development_execution_v1/PAPER1_VALUE_V3_DEVELOPMENT_LOSO_SUMMARY_V1.json                                                         | 87302b40142043bcce413d268543c21b51be0a5b8052b921c6260294e63dfccc |
| Development closure         | expanded_2356_postexec_closure_v1/PAPER1_VALUE_V3_EXPANDED_2356_POSTEXEC_TECHNICAL_SCIENTIFIC_CLOSURE_V1.json                                   | f0d73da76d492a87aa73793834650d1f61b57876849047cb554cf95af7fc538d |
| C01 preregistration         | independent_scene_c01_value_v3_evaluation_preregistration_v1/PAPER1_VALUE_V3_C01_INDEPENDENT_EVALUATION_PREREGISTRATION_V1.json                 | 279023aefb3a70f8043ff53859e16df018c0e5233fe3d22c94904441891856fb |
| Final-model postexec freeze | value_v3_full_development_final_candidate_postexec_freeze_v1/PAPER1_VALUE_V3_FULL_DEVELOPMENT_FINAL_CANDIDATE_POSTEXEC_TECHNICAL_FREEZE_V1.json | ad21dd29e70c62c78a8da84692ca10bcce074e2d841c5bcbb199fc04b2f3fbcb |

## **10.2 C01 qualification / collection chain**

| **对象**                  | **路径或说明**                                                                                                                                    | **SHA256**                                                       |
|---------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------|
| Scenario                  | /root/autodl-tmp/fullmine_v4_fleet_cross_scene_v1/scenarios_c01_static_qualification_v1/Scenario-fullmine-v4-cross-scene-c01-dual-aligned-v1.json | ea7e813768ffd58e705d72abe44a6a15e802f4285ff4ed9943c0e143b7fbf950 |
| Scenario manifest         | /root/autodl-tmp/fullmine_v4_fleet_cross_scene_v1/scenarios_c01_static_qualification_v1/cross_scene_c01_scenario_manifest_v1.json                 | 0fb47416d137c4dce66e55d4b52d5ffec6e89d53281d505b17d449523384b19b |
| Static bundle             | /root/autodl-tmp/fullmine_v4_fleet_cross_scene_v1/scenarios_c01_static_qualification_v1/C01_STATIC_QUALIFICATION_BUNDLE_V1.json                   | 1a6e0970bbc667d687ca6f65fe1fae776aafb92b848c94e1fab71112af6186a5 |
| Static bitmap freeze      | independent_scene_c01_static_bitmap_checker_postexec_freeze_v1/...FREEZE_V1.json                                                                  | 3ab62509aac7192188e841045b60ca17910622c54b1c8f8470f480845833817c |
| NO-MCTS freeze            | independent_scene_c01_nomcts_causal_postexec_freeze_v1/...FREEZE_V1.json                                                                          | e98d7e930a8cd68b370f50a97996ab4e00b4ce2ea840494e266c06f9ef9ae914 |
| Protocol binding          | independent_scene_c01_value_v3_target_collection_parent_binding_v1/...BINDING_FIX1_V1.json                                                        | 9a2efc17ecac54c9ff204fc204a0d714e368b6de9e822384aa66dac5557abf66 |
| Zone contract             | independent_scene_c01_current_semantic_zone_contract_v1/PAPER1_VALUE_V3_C01_CURRENT_SEMANTIC_ZONE_CONTRACT_V1.json                                | f65efedc45487e19b6d75c6011db6546b0cdef90caf858da0cfa986bd7fabfe6 |
| Collection harness freeze | independent_scene_c01_value_v3_target_collection_harness_v1/PAPER1_VALUE_V3_C01_PURE_MCTS_TARGET_COLLECTION_HARNESS_STATIC_FREEZE_V1.json         | 849ca4aad066eee516ab87a08f144c4f866bb53dc0c3f633e20ede438912a35a |
| Derived runner            | independent_scene_c01_value_v3_target_collection_harness_v1/src/cross_scene_fleet_mcts_c01_seed0_value_v3_independent_target_collector_v1.py      | 43061ad1c7bb14f82772a8647fedb6c50f01ce1de084760563b6064bd76e30a4 |
| Six-episode compatibility | six_episode_producer_compatibility_postaudit_closure_v1/...CLOSURE_FIX1_V1.json                                                                   | ab8d4c223fc93b15286e5e4e2680e914e6a8c96ba2324d846341226be9c357ff |

## **10.3 C01 execution / dataset / current Gate**

| **对象**                          | **路径或角色**                                                                                                | **SHA256**                                                       |
|-----------------------------------|---------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------|
| Original authorization            | independent_scene_c01_value_v3_target_collection_execution_authorization_v1/...AUTHORIZATION_V1.json          | d0529a77dd71fc28ebdc4b2779d83ea208c975fdd01592198d79efa322d8fdb2 |
| Original START                    | independent_scene_c01_value_v3_target_collection_execution_evidence_v1/START.json                             | b1e71272f71971a03b0a1af38e831373c5b0407ccdfb784434ffd5cc02fcd5bc |
| Original CAPTURE                  | independent_scene_c01_value_v3_target_collection_execution_evidence_v1/CAPTURE.json                           | c4aaa47c4e069480fa21b68cce57801fdebc09a6f2977c29b7092d420705334c |
| Original technical failure freeze | independent_scene_c01_value_v3_target_collection_technical_failure_freeze_v1/...FREEZE_V1.json                | 1f549f9baf1d085ee6af89ac21767abd1609c6b0c3cf9424b71a35adb8ce8084 |
| Recovery authorization            | independent_scene_c01_value_v3_target_collection_technical_recovery_authorization_v1/...AUTHORIZATION_V1.json | 58e26185d55d20d10afb9ac6e76ec01963b3fc95fdfb97bfbd27a4fcbd26d05d |
| Recovery START                    | independent_scene_c01_value_v3_target_collection_technical_recovery_execution_evidence_v1/START.json          | b95e728c24c794d73a0f34ad7f70b5c9d932f6497931111cba99b581b0cbcb61 |
| Recovery CAPTURE                  | independent_scene_c01_value_v3_target_collection_technical_recovery_execution_evidence_v1/CAPTURE.json        | 7cfaa8899be6f4b02db9246222e7f5a4bc6dcfc211fec5e152ad339b2c5935fb |
| C01 evaluation dataset            | independent_scene_c01_value_v3_evaluation_dataset_v1/...root_dataset_v1.npz                                   | 1427901d6eda446967c87a75c98b4fd066b01d0daf3a0041f11e145858e3f0f0 |
| C01 dataset manifest              | independent_scene_c01_value_v3_evaluation_dataset_v1/...MANIFEST_V1.json                                      | fd4a2c6794e0d2805fda3314da58167d13fe6c9b925fa3d36df0568554a6bfda |
| C01 postexec/data freeze          | independent_scene_c01_value_v3_evaluation_dataset_v1/...FREEZE_V1.json                                        | 94ca80de05580fe91d9937fcf3883b329d6cdd93c2c2bd908510bf57622d0fe1 |
| Failed metric Gate script         | /root/autodl-tmp/C01_VALUE_V3_EXACT_METRIC_CLOSURE_AND_IMMEDIATE_BASELINE_FREEZE_V1.txt                       | 9878a968c270f1410ba17b49eadc16acafb5369f076e7fdee3efcc181ed19fd9 |

# **11. 当前 namespace 与文件完整性**

## **11.1 已知存在**

- Development dataset / harness / summary / closure。

- 3 个 final-model checkpoint 与 final-model postexec freeze。

- C01 scenario、static bitmap freeze、NO-MCTS freeze、zone/binding/harness。

- Original failed authorization/START/CAPTURE/failure freeze。

- Recovery authorization/START/CAPTURE/evidence/raw outputs。

- C01 evaluation dataset root、manifest、postexec freeze、SHA256SUMS。

## **11.2 已知未正式发布**

- independent_scene_c01_value_v3_metric_and_immediate_baseline_v1（正式 root 未到 atomic publish）。

- independent_scene_c01_value_v3_forward_harness_v1。

- independent_scene_c01_value_v3_forward_execution_authorization_v1。

- independent_scene_c01_value_v3_evaluation_v1。

## **11.3 必须现场核验**

- 失败后是否存在 \`.independent_scene_c01_value_v3_metric_and_immediate_baseline_v1.stage.\*\`。

- 是否存在任何残留 Value/MCTS Python process。

- 正式 METRIC_ROOT 仍 absent；若出现则必须先停止并做 provenance 审计。

# **12. 资源规则与执行纪律**

| **任务**                          | **资源**                  | **GPU**      | **规则**                                          |
|-----------------------------------|---------------------------|--------------|---------------------------------------------------|
| 当前 exact metric interface audit | LOW                       | 不需要       | 只读源码/AST/bytecode/JSON；不得加载 checkpoint。 |
| Metric FIX1 + baseline freeze     | LOW                       | 不需要       | 只计算 numpy metric；先 development regression。  |
| Value forward harness derivation  | LOW                       | 不需要       | static-only；不执行模型。                         |
| Value forward execution           | 待未来 authorization 冻结 | 预计可不需要 | 必须 one-time START/CAPTURE；不得提前执行。       |
| MCTS integration                  | 未授权                    | \-           | 独立结果完成前禁止。                              |

- 长期 HIGH-CPU 命令建议 screen 后台运行；当前 LOW Gate 不需要。

- 任何 one-time authorization 在 START 后永久消费；失败也不得自动重试。

- 所有正式输出必须 atomic publish，并保存 SHA256SUMS。

- 不要因终端返回 \`(base)\` 而重复运行；以 Gate 内 ENV=minesim 为准。

# **13. DO_NOT_REPEAT｜永久禁止事项**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>最高优先级</strong></p>
<p>所有已消费 one-time execution、START/CAPTURE、raw outputs、checkpoint 和 freeze 都是科研证据，不得为“让结果更好看”而覆盖、筛选、删除或重复。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

- 禁止重跑 2356-root one-time 9-fold training。

- 禁止重跑 3 个 full-development final-model training。

- 禁止 best-seed selection、HPO、retune、改 epochs/LR/loss/normalization/scene weights。

- 禁止重生成 C01 scenario、static assets、bitmap qualification 或 NO-MCTS causal result。

- 禁止重跑 C01 Pure-MCTS target collection；成功 recovery 已是唯一 accepted target collection。

- 禁止删除或覆盖 original/recovery START、CAPTURE、stdout/stderr/rc、RAW_SHA256SUMS、raw JSONL。

- 禁止再次执行旧 exact metric Gate（SHA=9878a968...）。

- 禁止仅把“两参数断言”改成“三参数”后直接运行；必须先确认 exact source/call-site/return schema。

- 禁止在 C01 immediate baseline freeze 前加载 final checkpoint 或进行 forward。

- 禁止挑选单个 seed、做 inference ensemble 或修改 median aggregation。

- 禁止把 equality 解释成 PASS；未来已冻结方向必须为 strict \`\<\`。

- 禁止把 Pure-MCTS benchmark PASS 转写成 Value V3 independent PASS。

- 禁止在 independent validation 完成前接入 MCTS、宣称计算量下降或安全性提升。

# **14. 快速接手区｜后续 AI / 工程人员按此继续**

## **14.1 60 秒状态复述**

| **问题**                         | **正确回答**                                                               |
|----------------------------------|----------------------------------------------------------------------------|
| 网络训练完了吗？                 | 完了。2356 development 和 3 个 final full-development models 均冻结。      |
| C01 标签有了吗？                 | 有。Pure-MCTS recovery collection 151 roots 已冻结。                       |
| C01 数据集有了吗？               | 有。NPZ SHA=1427901d...，151×12 / 151×16。                                 |
| 网络看过 C01 吗？                | 没有。Value forward 未授权、未执行。                                       |
| 现在为什么停？                   | Exact metric callable 实际是 (q,pred,immediate)，旧 Gate 错按两参数设计。  |
| 下一步是什么？                   | LOW：先审计三参数 exact metric 与失败 stage，再派生 FIX1 baseline freeze。 |
| 可以重跑旧脚本吗？               | 不可以。                                                                   |
| 可以直接加载 checkpoint 试试吗？ | 不可以。                                                                   |

## **14.2 下一位执行者的动作顺序**

1\. 读取本节、第 8 节、第 9 节和第 13 节。

2\. 在 AutoDL 上只读核验 stage / metric root / process。

3\. 生成一个新的 FIX1 source-contract audit，不调用模型。

4\. 上传完整输出；只有 exact metric contract PASS 后才生成 baseline freeze Gate。

5\. baseline freeze PASS 后，再派生 Value forward harness / authorization。

6\. 任何 HOLD 都只处理该 fault domain，不回退到训练、场景或 MCTS collection。

## **14.3 当前最新失败的最短交接口径**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>CURRENT_STAGE=C01_EXACT_METRIC_AND_IMMEDIATE_BASELINE_PRE_FORWARD<br />
C01_DATASET=FROZEN_PASS_151_ROOTS<br />
EXACT_METRIC_GATE=TECHNICAL_HOLD<br />
FAULT=EXPECTED_2_PARAMS_BUT_ACTUAL_SIGNATURE_IS_(q,pred,immediate)<br />
METRIC_ROOT_PUBLISHED=False<br />
C01_IMMEDIATE_BASELINE_FROZEN=False<br />
VALUE_CHECKPOINT_LOADED=False<br />
C01_VALUE_FORWARD_AUTHORIZED=False<br />
C01_VALUE_FORWARD_EXECUTED=False<br />
INDEPENDENT_GENERALIZATION_PASS=False<br />
MCTS_VALUE_INTEGRATION=False<br />
NEXT=LOW_EXACT_3_PARAMETER_METRIC_SOURCE_CALLSITE_RETURN_CONTRACT_AUDIT</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# **附录 A｜关键时间线（当前链）**

| **顺序** | **事件**                                  | **结果**                                                              |
|----------|-------------------------------------------|-----------------------------------------------------------------------|
| 1        | Value V3 2356-root development training   | 9 folds RC=0；3/3 scene win；DEVELOPMENT_READY。                      |
| 2        | 3 个 full-development final models        | 固定 seeds 20260824/25/26；postexec freeze PASS。                     |
| 3        | C01 static bitmap qualification           | FROZEN PASS。                                                         |
| 4        | C01 NO-MCTS causal conflict               | FROZEN PASS；真实 physical overlap。                                  |
| 5        | C01 Pure-MCTS collection original attempt | argparse RC=2；0 raw / 0 roots；MCTS 未进入。                         |
| 6        | Separate technical recovery               | corrected argv；RC=0；151 roots；collision avoided。                  |
| 7        | C01 evaluation dataset freeze             | NPZ / manifest / freeze 原子发布；SHA 完整。                          |
| 8        | Exact metric baseline Gate                | SHA gates PASS；signature assertion HOLD：actual (q,pred,immediate)。 |
| 9        | 当前停点                                  | 等待 exact 3-parameter metric recovery FIX1；网络尚未 forward。       |

# **附录 B｜术语速查**

| **术语**               | **在本项目中的含义**                                                    |
|------------------------|-------------------------------------------------------------------------|
| Pure-MCTS target       | 在 Value 不参与时，由 frozen Fleet-MCTS 产生的 Q / immediate labels。   |
| Root                   | 一次 MCTS root search 的 12-D state + 16 joint-action target rows。     |
| Immediate baseline     | 使用同一 exact metric，以 immediate_reward 作为 score 的冻结对照。      |
| Normalized regret      | 由 frozen exact metric closure 定义；不能自行改公式。                   |
| Development-ready      | development scenes 上达到 gate；不等于 independent generalization。     |
| Independent evaluation | C01 未参与训练/选择；metric、baseline、aggregation 先冻结，再 forward。 |
| Technical recovery     | 只修执行接口，不改科学协议、场景、seed 或 MCTS 参数。                   |
| Atomic publish         | stage 全部通过后一次性 mv 到正式 root，避免半成品被当作 frozen result。 |

# **附录 C｜文档版本记录**

| **版本**   | **证据截点**       | **主要停点**                                                               |
|------------|--------------------|----------------------------------------------------------------------------|
| V1         | 2026-08-26 earlier | C01 static checker 两进程授权前。                                          |
| V2（本版） | 2026-08-26 latest  | C01 evaluation dataset 已冻结；Exact Metric callable 三参数签名技术 HOLD。 |
