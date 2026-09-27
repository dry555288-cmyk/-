**MineSim-Dynamic**

**Value V3 Confidence-Gated Top-K Root Pruning**

**项目交接文档｜K13 运行价值评审完成版 V1**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>当前唯一 Gate<br />
</strong>BUILD_DEVELOPMENT_ONLY_MATCHED_RUNTIME_PROBE_K13_B16_B32_PRESTART<br />
K=13 与 tau_prune=1.2940582036972046 已由 development-only 冻结评分数据选定；尚未冻结 formal pruning protocol，尚未运行任何 formal pruning experiment。</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

| **字段**           | **当前值**                               |
|--------------------|------------------------------------------|
| 文档日期           | 2026-08-31                               |
| Git HEAD           | 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e |
| 冻结 tau_order     | 0.06767839193344116                      |
| 当前候选 K         | 13                                       |
| 当前候选 tau_prune | 1.2940582036972046                       |
| 正式实验状态       | 未开始 / 不得擅自进入                    |

本文档用于下一位研究者 / 下一轮会话无损续接。优先级：当前终端与冻结 SHA \> 本文档 \> 更早历史。

# **0. 一页交接摘要**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>最重要结论<br />
</strong>K=8 在冻结的 453 个 model-root pair 上扫描 425 个 tau_prune 候选后无任何合格阈值；按 Top-K retention 对 K 的单调性，K&lt;8 同样被排除。随后按预注册 K-ladder（9→15）搜索，K=13 是首个满足 pooled 及三个 model seed 均 ≥99% Top-K target retention 的非平凡 K。选定 tau_prune=1.2940582036972046，高置信触发覆盖率约 39.29%，高置信子集 178/453，三个 model seed retention 均为 100%，最小单 seed support=49。</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

| **主题**       | **交接结论**                                                                                                              |
|----------------|---------------------------------------------------------------------------------------------------------------------------|
| Formal 基线    | 27-cell confidence-gated formal matrix 已冻结；旧 formal 分支永不回跑、永不调参。                                         |
| 开发数据       | Pure-MCTS target collection：3 个 runtime seeds × 151 roots = 453 raw；实际仅 151 unique roots，三 seed target 完全一致。 |
| Value 离线评分 | 151 unique roots × 3 frozen model seeds = 453 forwards；scored dataset 已恢复并冻结有效。                                 |
| K=8 结论       | 425 个 threshold-induced subsets，0 eligible；tau_prune 未选定，科学上拒绝 K≤8。                                          |
| K-ladder 结论  | K=9–12 无解；K=13 首次有解；K=14 同样可行但剪枝更弱；K=15 coverage 更大但仅剪 1/16。                                      |
| 当前候选       | K=13, tau_prune=1.2940582036972046；触发时 16→13 actions，条件剪枝 18.75%。                                               |
| 运行价值       | 平均 candidate reduction 仅约 7.37%，且 scorer forward 在每个 root 上都先执行，因此必须做 matched runtime probe。         |
| 下一步         | 只构建 development-only matched runtime probe：B16/B32，pruning-off vs frozen K13。B8 明确排除。                          |

# **1. 权威性、冻结规则与禁区**

以下规则是继续项目时的硬约束，违反任一条都会污染证据链：

- 事实优先级：当前终端 / Git / 源码 / runtime / SHA \> 冻结 artifact \> 最新交接文档 \> 更早历史 \> 计划。

- 任何 one-shot namespace 一旦 START_WRITTEN=True，即永久消费；PASS/FAIL 均不得原 namespace 重跑。

- 旧 formal 27-cell matrix、旧 confidence-gated controller/runner、旧 formal 结果均不可修改、不可重跑、不可用于反向调 tau_prune。

- 技术失败与科学失败必须严格分开；技术失败不改变科学结论，科学 HOLD 不能通过降低标准或事后改规则“修成 PASS”。

- 当前 K=13 与 tau_prune 是 development-only frozen-score 选择结果；在 runtime-value probe 前不得改变。

- 下一阶段仍不是 formal。只有 matched development runtime probe 显示可复现的实际 runtime/expansion 优势，才有资格考虑冻结 formal protocol。

# **2. 不可变 formal 基线**

| **项目**              | **冻结值 / 结论**                                                |
|-----------------------|------------------------------------------------------------------|
| Git HEAD              | 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e                         |
| 冻结 tau_order        | 0.06767839193344116                                              |
| 27-cell formal matrix | B8: 3/9；B16: 8/9；B32: 9/9；B32 首次稳定                        |
| Pure B8 baseline      | 3432 expansions；6763.0108 ms                                    |
| Confidence-gated B32  | 6528 expansions；14137.5239 ms                                   |
| formal matrix SHA     | c69180cd98c93edc04b08cb9cb762675f0fa7a1b710c744a30fec37d68cc2932 |
| parent controller SHA | 0ed2d1ff33a66198bf59b25e1117274ddc61440bf52dec1052d4aa553a52a2f9 |

解释：root-order-only confidence gating 并不会减少 action 数、iterations、rollout、backup，反而增加 neural forward，因此这一轮研究才转向 root-level Top-K pruning。

# **3. 当前 Top-K pruning 机制**

三段式 root-only 机制保持不变，tree 内部 MCTS 不改：

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>margin &lt; tau_order<br />
-&gt; PURE_FULL<br />
<br />
tau_order &lt;= margin &lt; tau_prune<br />
-&gt; NEURAL_ORDER_FULL<br />
<br />
margin &gt;= tau_prune<br />
-&gt; NEURAL_TOPK_PRUNED<br />
<br />
异常空候选<br />
-&gt; PRUNE_RECOVERY_FULL</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

当前选定参数：

| **参数**     | **值**              | **含义**                              |
|--------------|---------------------|---------------------------------------|
| tau_order    | 0.06767839193344116 | 冻结的 neural ordering 门槛           |
| K            | 13                  | 高置信 root 保留 Top-13 / 16          |
| tau_prune    | 1.2940582036972046  | development-only 冻结评分数据选择结果 |
| 条件剪枝比例 | 3/16 = 18.75%       | 仅在 NEURAL_TOPK_PRUNED root 生效     |

# **4. 核心代码与绑定**

| **组件**                  | **文件**                                                | **SHA256**                                                       |
|---------------------------|---------------------------------------------------------|------------------------------------------------------------------|
| Top-K controller          | paper1_value_confidence_gated_topk_pruning_search_v1.py | 5104d9c2c9363ec9acd51ea7849fe306d7632ab07577ceb2b2ccca74a4c93350 |
| K8 patched runner         | paper1_value_confidence_gated_topk_pruning_runner_v1.py | 35b51c3c121967d07c64b85ad1c66f719545fa091eab597046cc7ff7ccadb3f9 |
| Value scorer              | paper1_value_v3_root_scorer_v1.py                       | 7ffea187ec9e55bdd72f796a376826d6b3656380ac53a88c6d3416d023db5709 |
| 12D feature helper        | paper1_value_v3_online_root_features_v1.py              | f75b1c09854d2645a3e4d47a6381e33578b74c1a8f9fc95e35a8db22b474f6b1 |
| Root diagnostic collector | paper1_root_diagnostic_collector_v1.py                  | 283d2bfb38af5bd3ef1897349f1e366f862ab508250c1f262f15fd0509c4a2a6 |
| Dynamic V2V               | paper1_dynamic_v2v_dsafe_v1.py                          | d3fa8b666092c7b9c60654208decab38e9990e63082f32018206d1b4e76b2131 |
| Shadow safe node          | paper1_shadow_safe_node_v1.py                           | fc4fe915be4752996e2dd64d44d1de8b2a27f4c587f94250f9e64434fa2191e7 |

# **5. 关键 action-space / ranking 语义**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>scores = score_12d(x) # shape = (16,)<br />
<br />
ranked_indices = sorted(<br />
range(16),<br />
key=lambda idx: (-float(scores[idx]), int(idx))<br />
)<br />
<br />
action_id(idx) = f"{idx // 4},{idx % 4}"<br />
confidence_margin = top1_score - top2_score</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

- 16 个输出分量与 joint-action ID 一一对应：0→0,0；1→0,1；…；15→3,3。

- 同分 tie-break：较小 canonical index 优先。

- online controller 固定对完整 range(16) 排序；不是先按 snapshot feasible-mask 过滤。

- scorer forward 发生在 prune threshold 判断之前，因此每个 root 都要支付一次 neural forward。

# **6. 已完成技术里程碑（按证据链）**

| **里程碑**                         | **状态**                      | **结论**                                                                   |
|------------------------------------|-------------------------------|----------------------------------------------------------------------------|
| Parent/interface audit             | PASS                          | 证明 root-only pruning 可仅 mask depth=0 untried_actions，深层 MCTS 不变。 |
| New controller static parity       | PASS                          | 无 rollout/backup/UCT/budget 改动；tau_order 原值保留。                    |
| Pruning-off smoke                  | PASS                          | 16→16，0 prune，1 forward，机制 parity 成立。                              |
| K8 mechanism smoke                 | PASS                          | 16→8，ratio=0.5，allowed IDs 精确等于 neural ranking\[:8\]。               |
| Retention source audit             | PASS_NEEDS_NEW_DEV_COLLECTION | 历史 dev artifact 不足以直接做 99% retention calibration。                 |
| Pure target collector 4-root retry | PASS                          | root_snapshot / 12D / Pure target / budget 全部有效。                      |
| Mature dev collection              | PASS                          | runtime seeds 101/102/103，各 151 roots。                                  |
| Collection freeze                  | PASS                          | 453 raw = 151 unique roots × 3 完全重复；target disagreement=0。           |
| Frozen Value scoring               | PASS via recovery             | 151 roots × 3 model seeds = 453 forwards；scored dataset frozen valid。    |
| K8 tau scan                        | Scientific HOLD               | 425 candidates，0 eligible。                                               |
| K-ladder 9–15                      | PASS_CANDIDATE_FOUND          | K13 首个可行；K/tau 冻结为当前候选。                                       |
| K13 runtime-value static review    | PASS_BUILD_RUNTIME_PROBE      | B8 无结构收益；B16/B32 值得 matched probe。                                |

# **7. Development target collection 与数据冻结**

## **7.1 Pure target collector**

成熟采集使用 canonical independent Pure-MCTS target collector，target budget=64、depth=8、dt=0.5，不依赖 Value V3，不使用 formal 结果。runtime seeds 固定为 101/102/103，与 formal runtime seeds 0/1/2 不重叠。

| **runtime seed** | **roots** | **结果**              | **是否允许重跑** |
|------------------|-----------|-----------------------|------------------|
| 101              | 151       | PASS / benchmark PASS | 否               |
| 102              | 151       | PASS / benchmark PASS | 否               |
| 103              | 151       | PASS / benchmark PASS | 否               |

## **7.2 453 raw 并非 453 个独立 root**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>统计独立性结论<br />
</strong>RAW_TOTAL_SAMPLE_COUNT=453，但 UNIQUE_ROOT_SNAPSHOT_COUNT=151，UNIQUE_FEATURE_12D_COUNT=151。每个 unique root 在 101/102/103 三个 Pure runtime seed 下重复一次，并且 root target disagreement=0、feature target disagreement=0。后续有效独立 root 数必须按 151 处理，不得把 453 当作独立 calibration n。</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

| **artifact**              | **SHA256**                                                       |
|---------------------------|------------------------------------------------------------------|
| Raw combined              | f4a6c4c35b9e7a769234b99721c8ad167dae3de508f6a2ab6fb6023c7ff441b2 |
| Mature collection freeze  | 3919a72634d6f136bceb476113e8fe7409105807e1d4f8dede405f1e0133f4df |
| Unique151 scoring dataset | 257d161b0b6fac397d71f24a98bfe6bb3579bf932a4eb54a45ec3368d2a09394 |

# **8. Frozen Value V3 离线评分**

三个 frozen Value V3 checkpoints 分别对 151 unique roots 评分，共 453 model-root pairs。中途发生两类纯技术问题：先漏复制 scorer 的本地 feature helper；之后成功分支的 SystemExit(0) 被 except BaseException 自捕获。两者均未改变最终 scored dataset；后者通过独立 recovery 对 453 rows 全量重算 ranking/action-id/target-rank/margin 后冻结为有效。

| **model seed** | **checkpoint SHA256**                                            | **forwards** |
|----------------|------------------------------------------------------------------|--------------|
| 20260824       | 496e4259eb9801f3ce70c1094be12fd0985cb03e97d606cade8dfbe9d5228633 | 151          |
| 20260825       | 5df90947a5fdd2bc6aa525ca5eba78b6379e127e5df6ca1d0362c992caab73b5 | 151          |
| 20260826       | 3881d39c09b02a513e44f0fe612aad42de9ff636fd07e314d327b4c6d5f132df | 151          |

| **artifact**          | **SHA256**                                                       |
|-----------------------|------------------------------------------------------------------|
| Scored JSONL          | df6709547e18d9a3efed292d7faba952e802d3162330ecb3009253b32f7a3eb7 |
| Scoring summary       | d44fdf8942c018c0af0cf21bc1fa5e2384ff494c7eac86e0e2c51fd331801048 |
| Scored dataset freeze | c086c1879bb811c9d475cd343eff5aba9267268e6f632e90d832e3f66adff4cb |
| Semantic validation   | 30541ae67b7b44c55af7f089432a0c40162375fed709cc542437b0656764b1d3 |

全部 151 roots 上的 Top-8 retention（仅诊断，不作为最终 pruning 安全结论）：

| **模型** | **Top-8 retention** |
|----------|---------------------|
| 20260824 | 0.8741721854304636  |
| 20260825 | 0.8543046357615894  |
| 20260826 | 0.8278145695364238  |
| pooled   | 0.8520971302428256  |

# **9. K=8 科学结论与 K-ladder**

## **9.1 K=8：科学 HOLD**

| **指标**                      | **值**             |
|-------------------------------|--------------------|
| Distinct margin               | 453                |
| margin \> tau_order pairs     | 425                |
| tau candidates                | 425                |
| eligible candidates           | 0                  |
| tau_order+ pooled retention   | 0.8588235294117647 |
| 20260824 tau_order+ retention | 0.8888888888888888 |
| 20260825 tau_order+ retention | 0.8482758620689655 |
| 20260826 tau_order+ retention | 0.8382352941176471 |

冻结 eligibility：tau_prune \> tau_order；pooled Top-K retention ≥ 0.99；三个 model seed 单独 retention 均 ≥ 0.99；每个 model seed 高置信 n\>0。K=8 对全部 425 个非空阈值子集均无解。

单调性推论：对同一 high-confidence subset，Top-K retention 随 K 单调不减；因此 K\<8 不可能优于 K=8，K=4 被数学上直接排除，不应再浪费算力。

## **9.2 K-ladder 9→15：K13 首次可行**

| **K** | **eligible 数** | **selected tau**   | **pooled retention** | **pooled coverage** |
|-------|-----------------|--------------------|----------------------|---------------------|
| K=9   | 0               | —                  | —                    | —                   |
| K=10  | 0               | —                  | —                    | —                   |
| K=11  | 0               | —                  | —                    | —                   |
| K=12  | 0               | —                  | —                    | —                   |
| K=13  | 106             | 1.2940582036972046 | 1.0000               | 0.3929359823        |
| K=14  | 106             | 1.2940582036972046 | 1.0000               | 0.3929359823        |
| K=15  | 258             | 0.3655426800251007 | 0.9969696970         | 0.7284768212        |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>为何选 K=13 而不是 K=15<br />
</strong>K-ladder 在运行前已冻结规则：先按 K=9→15 升序寻找，跨 K 选择“最小的有解 K”，以最大化 action pruning；同一 K 内选择最低合格 tau，以最大化 coverage。因此 K13 是预注册规则下的唯一全局选择，不允许看完结果后改选 K15。</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## **9.3 K13 冻结安全统计**

| **指标**                     | **K13 冻结值**      |
|------------------------------|---------------------|
| tau_prune                    | 1.2940582036972046  |
| 高置信 pairs                 | 178 / 453           |
| pooled retention             | 1.0                 |
| pooled coverage              | 0.39293598233995586 |
| 20260824 support / retention | 66 / 1.0            |
| 20260825 support / retention | 49 / 1.0            |
| 20260826 support / retention | 63 / 1.0            |
| 高置信失败数                 | 0                   |
| 触发时删 action              | 3 / 16              |
| 条件剪枝比例                 | 18.75%              |

# **10. K13 运行价值静态评审（当前最新状态）**

此节是当前最新 Gate 的输出，也是本交接文档最关键的续接点。该评审未加载 checkpoint、未 forward、未跑 MCTS，只基于冻结 scores 与当前 controller 源码进行结构性 runtime leverage 分析。

| **模式**           | **pairs** | **占比** |
|--------------------|-----------|----------|
| PURE_FULL          | 28        | 6.18%    |
| NEURAL_ORDER_FULL  | 247       | 54.53%   |
| NEURAL_TOPK_PRUNED | 178       | 39.29%   |

| **model seed** | **K13 prune roots** | **coverage** |
|----------------|---------------------|--------------|
| 20260824       | 66 / 151            | 43.71%       |
| 20260825       | 49 / 151            | 32.45%       |
| 20260826       | 63 / 151            | 41.72%       |

| **指标**                               | **值**              |
|----------------------------------------|---------------------|
| 条件删 action 数                       | 3                   |
| 条件 root-action prune ratio           | 0.1875              |
| 平均每 root 删除 actions               | 1.1788079470198676  |
| 平均 candidate count                   | 14.821192052980132  |
| 平均 candidate reduction ratio         | 0.07367549668874172 |
| score_12d 行                           | 121                 |
| 首个 prune threshold 逻辑行            | 152                 |
| scorer forward 是否先于 prune decision | True                |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>工程含义<br />
</strong>K13 在触发 root 上只从 16 降到 13；由于只在约 39.29% roots 触发，折算平均 candidate reduction 约 7.37%。与此同时 neural scorer 在所有 root 上都先执行，所以这 7.37% 的结构性减少不等于 7.37% wall-time 收益，实际收益可能被 forward 开销抵消。必须用 matched runtime probe 实测。</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## **10.1 Budget 结构性收益**

| **Budget** | **触发时 slots saved** | **期望 saved/root** | **有结构收益** | **解释**                                           |
|------------|------------------------|---------------------|----------------|----------------------------------------------------|
| B8         | 0                      | 0.0000              | False          | K13 \> B8，根本无法减少 root-child expansion slots |
| B16        | 3                      | 1.1788079470        | True           | 理论平均节省约 7.37% of budget                     |
| B32        | 3                      | 1.1788079470        | True           | 理论平均节省约 3.68% of budget                     |

结论：B8 明确排除；只对 B16/B32 构建 development-only matched runtime probe。

# **11. 当前唯一下一步（必须从这里续接）**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>NEXT<br />
</strong>BUILD_DEVELOPMENT_ONLY_MATCHED_RUNTIME_PROBE_K13_B16_B32_PRESTART</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

下一步先在 LOW / CPU-only 构建 prestart，不直接运行。运行 probe 时建议使用 HIGH CPU-only，memory ≥8 GiB，80 GiB 已验证安全。

Probe 必须冻结：

- K=13，不再调整。

- tau_prune=1.2940582036972046，不再调整。

- tau_order=0.06767839193344116，不再调整。

- Budget 只测 B16、B32；B8 不测。

- 对照配置：PRUNING_OFF_NEURAL_ORDER_FULL vs K13_SELECTED_PRUNING。

- model seeds：20260824 / 20260825 / 20260826。

- 同一比较内必须 matched scene + runtime seed；不能换场景或只挑好结果。

- runtime probe 只用于判断工程收益，不得用结果反向调 K/tau。

必须采集的最小指标：

| **指标**                   | **用途**                       |
|----------------------------|--------------------------------|
| episode_wall_time_ms       | 最终工程收益                   |
| mcts_elapsed_ms            | MCTS 本体时延                  |
| expansion_count            | 是否实际减少搜索扩展           |
| root_expanded_action_count | root-level 剪枝是否真正生效    |
| value_forward_count        | neural 开销是否完全支付        |
| prune_activation_count     | 触发次数                       |
| prune_activation_fraction  | 实际触发率是否接近开发冻结数据 |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>进入 formal 的门槛<br />
</strong>只有 K13 在 B16 或 B32 上相对 pruning-off 出现可复现的 runtime / expansion 优势，才考虑冻结 formal pruning protocol。若没有实际优势，则应科学上拒绝 K13，即使其 high-confidence retention=100%。</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# **12. One-shot namespace / 重跑禁令台账**

| **namespace**                                       | **状态** | **说明**                                                                                     |
|-----------------------------------------------------|----------|----------------------------------------------------------------------------------------------|
| technical_smoke_4roots_v1                           | 已消费   | 技术失败：旧 runtime asset path 缺失；不得重跑                                               |
| technical_smoke_4roots_asset_rebind_retry1_v1       | 已消费   | PASS；4-root collector smoke                                                                 |
| mature_dev_collection_v1/seed_101_v1                | 已消费   | PASS；151 roots                                                                              |
| mature_dev_collection_v1/seed_102_v1                | 已消费   | PASS；151 roots                                                                              |
| mature_dev_collection_v1/seed_103_v1                | 已消费   | PASS；151 roots                                                                              |
| frozen_value_v3_offline_scoring_execution_v1        | 已消费   | 技术失败：漏本地 feature helper；0 forward                                                   |
| frozen_value_v3_offline_scoring_execution_retry1_v1 | 已消费   | 453 forwards 全完成；post-success SystemExit bookkeeping bug；scored data 已 recovery freeze |

# **13. 已踩坑与必须保留的防护**

| **坑**                          | **防护规则**                                                                                                                                                                                       |
|---------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 源码 raw-text 路径替换          | 相邻字符串 literal 会让完整运行时路径在源文本中不连续，导致 replacement_count=0。关键 Python 修改用 AST binding/line rewrite，并做 normalized-AST parity。                                         |
| 依赖闭包漏复制                  | 曾缺 paper1_root_diagnostic_collector_v1；后又缺 paper1_value_v3_online_root_features_v1。任何新 isolated src namespace 必须递归扫描同目录 paper1\_\* imports，并在 START 前做 import-only probe。 |
| executor 提前 mkdir output_root | runner 自己要求 output root 启动前不存在。executor 不得抢先创建 runtime output dir。                                                                                                               |
| tee 只抓 stdout                 | python ... \| tee ... 不包含 stderr traceback。调试/一次性运行使用 2\>&1 \| tee ...。                                                                                                              |
| except BaseException            | 会捕获 SystemExit(0)，把成功错误地覆盖成失败。后续 executor 用 except Exception 或在 try 外 return/exit。                                                                                          |
| one-shot 重跑                   | 只要 START_WRITTEN=True 即永久消费，不得为了修脚本原 namespace 再跑。                                                                                                                              |
| 453 当独立样本                  | 453 raw 是 151 roots × 3 Pure runtime seeds 完全重复；有效独立 root n=151。                                                                                                                        |
| formal 结果参与调参             | 禁止。K/tau 均来自 development-only frozen-score calibration。                                                                                                                                     |

# **14. 关键 artifact / SHA 台账**

| **artifact**               | **SHA256**                                                       |
|----------------------------|------------------------------------------------------------------|
| Git HEAD                   | 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e                         |
| K8 mechanism freeze        | 5f6b38cd4ce04fe695e0fab7d314da8678f6b4eef8439fc65ef5ce4f563e20a0 |
| Pruning-off parity freeze  | f08115e34dea37abc0c38259a78112025cfc82900f6429d8a02c473701d69785 |
| Collector technical freeze | df7f661902004ea02c660285946dd5e9722e032f92fa6f623d0b6c90ad8c6c1f |
| Mature collection freeze   | 3919a72634d6f136bceb476113e8fe7409105807e1d4f8dede405f1e0133f4df |
| Unique151 dataset          | 257d161b0b6fac397d71f24a98bfe6bb3579bf932a4eb54a45ec3368d2a09394 |
| Scored 453 JSONL           | df6709547e18d9a3efed292d7faba952e802d3162330ecb3009253b32f7a3eb7 |
| Scored dataset freeze      | c086c1879bb811c9d475cd343eff5aba9267268e6f632e90d832e3f66adff4cb |
| K8 tau selection           | 49f4eaf3fa8a962b4095a537c85418d0f4d6ed3632e45c3c8916e312e59c0bc7 |
| K-ladder protocol          | c4a48aa703efb34c4921f5bd8f464a0a894e55fca06b705242e9e46ac271592e |
| K-ladder review            | ee861d132d9fa4c214a8c24726595f1454b1fe2a2239162930e0da3daed543ed |
| K13 runtime-value review   | f981626043e389be3071238cffcb1fccb158d439d40cf1218abd2b4fe4cb06ac |
| K13 review manifest        | b515d1a252c989b5baabb1d66d2316c442f70409b89bd5b48ef68d2cc102e452 |

# **15. 关键绝对路径**

| /root/MineSim-Dynamic |
|-----------------------|

| /root/autodl-tmp/paper1_value_v3_confidence_gated_topk_pruning_dev_v1/ |
|------------------------------------------------------------------------|

| /root/autodl-tmp/paper1_value_v3_confidence_gated_topk_pruning_dev_v1/frozen_value_v3_offline_scoring_execution_retry1_v1/ |
|----------------------------------------------------------------------------------------------------------------------------|

| /root/autodl-tmp/paper1_value_v3_confidence_gated_topk_pruning_dev_v1/frozen_value_v3_offline_scoring_retry1_postsuccess_recovery_v1/ |
|---------------------------------------------------------------------------------------------------------------------------------------|

| /root/autodl-tmp/paper1_value_v3_confidence_gated_topk_pruning_dev_v1/tau_prune_selection_from_frozen_scores_v1/ |
|------------------------------------------------------------------------------------------------------------------|

| /root/autodl-tmp/paper1_value_v3_confidence_gated_topk_pruning_dev_v1/k_ladder_direction_review_from_frozen_scores_v1/ |
|------------------------------------------------------------------------------------------------------------------------|

| /root/autodl-tmp/paper1_value_v3_confidence_gated_topk_pruning_dev_v1/selected_k13_coverage_runtime_value_review_v1/ |
|----------------------------------------------------------------------------------------------------------------------|

# **16. 下一会话 / 下一研究者开工检查清单**

1.  确认 Git HEAD 仍为 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e。

2.  确认 selected K13 runtime-value review JSON SHA=f981626043e389be3071238cffcb1fccb158d439d40cf1218abd2b4fe4cb06ac。

3.  确认 K=13、tau_prune=1.2940582036972046、tau_order=0.06767839193344116，禁止重选。

4.  只构建 development-only matched runtime probe prestart；不要跳到 formal。

5.  B8 不测；B16/B32 各做 pruning-off vs K13 matched 对照。

6.  运行前 preflight dependency closure、output-root lifecycle、resource gate；START 前不得产生 MCTS/forward。

7.  一旦新 runtime namespace START_WRITTEN=True，记录 SHA 后视为永久消费。

8.  Probe 完成后先判断 runtime/expansion 是否有可复现优势，再决定“freeze formal protocol”或“reject K13”。

# **17. 当前停止点的科学解释**

当前研究已经从“是否能安全剪枝”推进到“安全剪枝是否有工程价值”。K13 在 development-only 高置信子集上实现了 100% Top-13 target retention，说明 Value V3 的 confidence margin 确实能筛出一部分非常可靠的 root；但 K13 只在约 39.29% roots 触发，且每次仅删 3/16 actions，折算平均 candidate reduction 约 7.37%。与此同时 scorer forward 对所有 root 都先执行。

因此现在最不应该做的是继续调 K/tau 或直接跑 formal；最应该做的是用 matched B16/B32 development runtime probe 回答一个简单问题：这 7.37% 的结构性候选减少，是否足以在真实搜索中抵消 neural forward 并降低 wall time / expansions。若答案是否定的，K13 应被科学上终止，而不是降低安全标准。

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>交接终点<br />
</strong>本交接文档截止于 K13 runtime-value static review PASS。<br />
下一步尚未构建 matched runtime probe prestart。<br />
请从 Gate：BUILD_DEVELOPMENT_ONLY_MATCHED_RUNTIME_PROBE_K13_B16_B32_PRESTART 继续。</th>
</tr>
</thead>
<tbody>
</tbody>
</table>
