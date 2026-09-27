**MineSim 神经网络辅助 MCTS  
严谨研究流程（冻结草案 V1）**

高质量 Teacher 数据 → 神经引导 → 置信剪枝 → 独立验证

基于现有 MineSim 项目证据与用户指定论文的阶段化研究协议  
版本日期：2026-09-22

**【项目规则】**本文件冻结的是“研究顺序、Gate 逻辑、数据隔离原则和验收框架”。具体 reward 权重、风险阈值、Teacher 预算、Horizon、网络规模、剪枝阈值等数值尚不在本版中强行确定；这些数值必须在对应 Gate 内通过实验或导师讨论后再冻结。

**【论文依据】**本文件仅把指定论文能够直接支持的思想作为“论文依据”；凡属于本项目进一步设计的内容均明确标为“项目规则”或“待商议”，避免把我们的工程选择包装成论文原结论。

# 0. 文档目标与不可违反的总原则

本研究的最终目标不是提高神经网络本身的分类准确率，而是在不降低任务质量和安全性的前提下，使 MCTS 用更少的在线搜索预算达到与高质量 MCTS 相同或更好的决策质量。最终评价对象是“搜索质量—计算代价”的关系，而不是单一模型精度。

**【论文依据】**Neural A\* 明确同时评价路径最优性与搜索节点减少比例，并以二者的折中作为核心目标；这直接支持“不能只看网络准确率，而要看搜索质量与搜索量的联合指标”。\[P7, Sec. 4.3, p.6; Conclusion, p.9\]

**【论文依据】**Deep-MCTS 论文不是用网络直接替代搜索，而是用两个 DNN 提供动作—状态预测和动作选择概率，再由 MCTS 重构多条未来轨迹并选取动作。\[P5, Abstract, p.1\]

**【项目规则】**研究顺序必须固定为：先定义“什么叫好决策”，再标定 Teacher 的搜索强度，再生成 Teacher 数据，再训练网络，再做无损引导，最后才做剪枝。若前置定义发生变化，后续受影响的数据或模型必须回滚，不允许继续沿用。

## 0.1 核心术语

| **术语**                     | **本项目定义**                                                                                    |
|------------------------------|---------------------------------------------------------------------------------------------------|
| **Online baseline**          | 当前真实在线比较基线；用于回答神经方法是否真的减少在线 MCTS 计算。                                |
| **Teacher MCTS**             | 使用更高预算、更充分重复并通过稳定性审计的 MCTS。它只能称“高置信 Teacher”，不能称理论最优或真值。 |
| **Policy target**            | 对合法动作的概率/偏好分布，例如由 Teacher 的 visit 分布或经审计的动作排名构造。                   |
| **Value/Q target**           | 对状态或状态—动作长期价值的估计目标。                                                             |
| **Safety filter**            | 由可解释的物理/风险规则直接判定不可行节点；优先级高于神经网络。                                   |
| **Neural guidance**          | 网络只改变搜索优先级、rollout 或叶节点估值，不删除合法动作。                                      |
| **Confidence-gated pruning** | 只有网络置信度及校准条件满足时才缩减候选；低置信或 OOD 时自动回退到完整 MCTS。                    |

# 1. 总体 Gate 流程与依赖关系

固定流程：G0 基线冻结 → G1 评价与安全体系冻结 → G2 Teacher 预算×深度收敛标定 → G3 高质量 Teacher 数据生成 → G4 标签质量审计 → G5 网络目标与离线学习 → G6 无损神经引导接入 → G7 置信剪枝 → G8 预算—质量曲线与完整闭环比较 → G9 独立 HOLDOUT 与消融。

| **Gate** | **名称**         | **核心问题**                  | **必须冻结的输出**                           |
|----------|------------------|-------------------------------|----------------------------------------------|
| **G0**   | 在线基线冻结     | 确保后续所有提升都有稳定参照  | Baseline 配置、代码、SHA、状态池与随机流冻结 |
| **G1**   | 评价/安全体系    | 先定义“什么是好决策”          | Safety constraint + 长期 utility/reward 定义 |
| **G2**   | Teacher 标定     | 确定“算到什么程度才可信”      | Teacher budget、depth/horizon、停止规则      |
| **G3**   | Teacher 数据生成 | 获得高质量、可复用搜索统计    | 全量 root statistics + 多 RNG 轨迹证据       |
| **G4**   | 标签审计         | 过滤/软化不稳定标签           | stable / uncertain / invalid 数据层级        |
| **G5**   | 网络离线学习     | 验证网络能否复现 Teacher 结构 | Policy/Value/Q 候选模型及校准结果            |
| **G6**   | 无损接入         | 先证明网络能帮助 MCTS 收敛    | 不删动作的 Neural-guided MCTS                |
| **G7**   | 剪枝             | 在质量已守住后减少分支        | confidence-gated pruning + fallback          |
| **G8**   | 端到端比较       | 证明效率提升不是局部假象      | 预算—质量曲线、CPU/节点/任务指标             |
| **G9**   | HOLDOUT          | 最终一次独立检验              | 冻结模型、阈值、K 后的独立结论               |

## 1.1 强制回滚规则

- 若 G1 的 reward、安全阈值、终止条件发生实质变化，则 G2 及之后所有以旧定义生成的 Teacher 结论失效；正式数据需重做或明确降级为历史数据。

- 若 G2 的 Teacher budget 或 horizon 发生变化，已生成数据只有在能够证明新旧 Teacher 标签等价时才允许复用；否则 G3 重做。

- 若 G3 后才发现关键输入字段未保存，禁止用后验近似“补标签”；应回到 G3 重新生成具备所需字段的数据。

- 若 G6 无损引导不能在同等质量下减少搜索，则禁止直接进入 G7 用硬剪枝“制造加速”。

- 任何 HOLDOUT 一旦被用于调 reward、网络、剪枝阈值或预算，就失去最终测试资格，必须重新冻结独立 HOLDOUT。

# 2. G0：在线 Baseline 与实验边界冻结

目的：先把“我们试图超越的 MCTS”固定下来。否则网络方案和基线同时变化，会导致无法归因。当前项目可把已经验证的 H8/400 ms 配置作为在线参照，但是否保留 Guide、tree reuse 等具体模块，要在 G0 文档中逐项列明，而不能口头默认。

**【论文依据】**MCTS 的 selection、expansion、rollout、backpropagation 是可独立扩展的不同阶段；因此实验中必须明确究竟改了哪一阶段，避免把多处变化混为一次“神经 MCTS”改动。\[P3, pp.1–2; P4, Sec. II\]

**【项目规则】**Baseline 冻结内容至少包括：代码 commit/SHA、动作空间、状态表示、Horizon、单步预算、UCT/selection 公式、rollout 策略、reward、终止条件、随机数流、场景版本、车辆动力学、合法动作 mask、日志 schema。

G0 验收：相同冻结初态与相同随机流下，重复运行能够重现同类结果；版本与哈希可核对；任何后续实验都能明确指出“只改了什么”。

# 3. G1：评价体系与 Safety Constraint 冻结

这是整个流程中最重要的逻辑前置。Teacher 的 Q、动作排序和最终标签都依赖 reward 与安全定义；因此绝不能先大量生成 Teacher 数据，再回头改 reward。

## 3.1 先分离“不可交易安全”与“可优化效用”

**【论文依据】**Safety-Critical Multi-Agent MCTS 在扩展节点后先利用 V2V、V2H、V2R 风险进行安全检查，并直接将超过阈值的节点标记为 unsafe；这说明安全可以作为搜索可行性条件，而不是完全依赖一个可被其他正奖励抵消的总 reward。\[P2, Algorithm 1 / Sec. IV-A, p.6\]

**【论文依据】**同一论文的 reward 仍然保留安全、效率、舒适性和合作等多目标，并对 horizon 内奖励进行折扣累计；这支持“安全过滤 + 安全集内长期效用”的两层设计。\[P2, Sec. IV-C, p.8\]

**【论文依据】**风险场论文通过模拟候选策略产生的未来轨迹，在时间轴上综合即时风险与长期累计风险；这支持我们避免只看当前一步净距或即时 reward。\[P1, Sec. 4 / Conclusion, pp.7, 23\]

**【项目规则】**第一层 Safety Feasibility：碰撞、越界/不可驶区域、明确超过物理/风险阈值的节点直接不可行。第二层 Utility：只在安全候选中比较任务完成、deadlock、长期进展、时间效率、平滑性/合作等。

## 3.2 Reward/Utility 的建议结构（只冻结结构，不冻结数值）

- Terminal/Completion：完成双车任务必须具有明确终局收益；未完成、超时、CAP、deadlock 必须在标签生成中可区分，不能都压成相同零分。

- Progress：使用沿 route 的长期进展，而非单纯欧氏距离，避免局部“看似靠近目标”但进入错误/冲突状态。

- Time/Efficiency：对用时、等待和不必要停滞进行成本化，但不能抵消硬安全约束。

- Smoothness/Comfort：加速度切换、jerk 或动作频繁切换可作为次级目标，防止网络学出高频振荡策略。

- Cooperation/Fairness：若双车互相礼让造成长期不推进，需要显式 deadlock/等待机制；如果后续采用合作项，应单独做消融。

- Long-horizon risk：不能只看最小瞬时 clearance；需要记录沿预测轨迹的累计风险/最危险区间，具体风险函数可参考 P1/P2 但必须适配 MineSim 几何与车辆模型。

**【待商议】**需要和导师最终确认：哪些风险作为硬约束、哪些进入 reward；clearance 与 PET/MMTTC 类指标是否适合 MineSim；deadlock 的正式定义；reward 权重和折扣因子 γ；是否采用字典序目标（安全→完成→效率）还是约束 MDP + 标量 utility。论文不能替我们直接给出 MineSim 的最佳数值。

G1 退出条件：所有 reward 项、终止条件、硬安全条件、长期评价 horizon 及单位尺度均写入协议并锁定；不得存在“后面看结果再调”的隐含参数。

# 4. G2：Teacher MCTS 的 Budget × Horizon 收敛标定

目的不是找“最大预算”，而是找“足以产生稳定标签的最小高质量预算/深度组合”。Teacher 必须比在线 baseline 更充分，但无限增加预算会造成数据采集浪费，也可能因更深 rollout 引入低概率轨迹噪声。

**【论文依据】**Safety-Critical MCTS 的复杂度同时受迭代数 K 与 rollout 深度 dmax 影响，其给出的最坏复杂度显式包含 K·dmax；该论文还先做收敛分析，观察到其任务中的 value 多在 300–600 次迭代内稳定，再把 K=1000 设为上限。这里的 300–600/1000 只属于论文场景，不能直接照搬到 MineSim。\[P2, Sec. IV-D–E, pp.9–10\]

**【论文依据】**Finnsson & Bjornsson 指出，更深的树会使单次模拟更长，从而减少根节点可获得的样本数；更宽的树又会降低被实际探索的分支比例。因此“深度越大越好”和“迭代越多越好”都没有普适性。\[P3, Game-Tree Properties, pp.2–3\]

## 4.1 标定实验设计

1.  建立独立 Calibration State Set：从不同场景、冲突阶段、相对速度、route topology、合法动作数量中分层抽取。该集合用于选 Teacher 参数，不得与最终 HOLDOUT 混用。

2.  预算采用递增档位而非一次跳到极大值。具体档位围绕当前在线预算做几何式扩展（例如 1×、2×、4×……只是设计方式，确切数值待机器预检后冻结）。

3.  Horizon/rollout depth 独立扫描，不能和预算捆绑。优先测试现有 H8/H12/H16，并视结果决定是否需要更深；如果 H16 后标签已稳定，不应为了“看得更远”机械加入 H32。

4.  每个 state×budget×depth 使用多个预注册 RNG 重复，记录完整 root action statistics，而不是只记录最终动作。

5.  对每一档同时计算：Top-1 动作一致率、Top-K 重合度、动作排名相关、Q/visit 分布变化、best-vs-second margin、closed-loop completion/safety/return，以及 CPU/迭代/节点数。

## 4.2 收敛判据（建议框架）

**【项目规则】**把“收敛”定义成多指标平台区，而不是某一个 Q 数字不再变化。Teacher 参数选择应满足：①安全与完成不随更高档预算恶化；②根动作/Top-K 跨 RNG 稳定；③相邻更高预算带来的标签变化和闭环收益已很小；④再增加计算的边际收益连续至少两个档位低于预设阈值。

**【待商议】**Top-1 一致率阈值、Top-K Jaccard 阈值、Q/visit 分布距离阈值、margin 阈值以及“边际收益很小”的 ε 需要在第一次 calibration 后基于真实噪声尺度决定，不能在看不到数据前拍脑袋。

G2 退出条件：得到一个 Teacher 配置（budget、Horizon、最大迭代/时间、rollout 策略）以及清晰的停止规则，并证明比在线 baseline 更稳定，但继续加预算已进入明显收益递减区。

# 5. G3：高质量 Teacher 数据生成

Teacher 数据的目标不是“尽量多”，而是“覆盖合理、标签可信、统计信息完整、后续任务可重用”。旧 Value V3 的经验说明，仅保存有限场景和单一 hard label 会把 Teacher 噪声直接传给网络。

**【论文依据】**场景工程论文强调开放矿山中的模糊边界、稀疏特征与 OOD 风险，并提出 Scenario Feature Extractor、Calibration & Certification、Verification & Validation 等环节提升模型鲁棒性与可信度。这支持我们把场景覆盖和独立验证作为数据工程的一部分，而不是训练后补救。\[P8, Sec. II / Fig.2 附近\]

**【论文依据】**矿山多模态轨迹预测论文指出非结构化道路下长期预测不确定性更高，并采用“多条可能轨迹 + 概率”表达未来，而不是单一路径。这提醒我们：Teacher 在模糊状态下也不应强制生成唯一硬标签。\[P6, pp.1–2\]

## 5.1 状态池构建与冻结

- 状态选择必须 outcome-blind：先基于场景、几何、相对位置/速度、冲突阶段、合法动作数等输入特征冻结状态池，再运行高预算 Teacher；不得先看 Native/Guide/MCTS 谁赢再挑状态。

- 按 physical-state lineage/episode/scene 分组，避免同一轨迹相邻状态跨 train/test 造成信息泄漏。

- 预先冻结 DEV/TRAIN、VALIDATION、FINAL HOLDOUT。FINAL HOLDOUT 在 reward、Teacher、网络、剪枝阈值全部冻结前绝不执行。

- 覆盖至少包括：冲突前/中/后、不同相对到达时间、不同速度组合、不同 route 组合、不同候选动作规模、易 deadlock 状态与普通状态。

## 5.2 每个 Teacher 样本必须保存的字段

| **类别**       | **最低保存内容**                                                                                       |
|----------------|--------------------------------------------------------------------------------------------------------|
| **输入**       | 完整决策 state、车辆运动学、route/region、合法动作 mask、场景 ID、episode/lineage ID、时间戳/step。    |
| **搜索配置**   | budget、Horizon、RNG、探索常数、rollout policy、代码 SHA、reward/safety 版本。                         |
| **根统计**     | 每个合法 action 的 visit count、Q/mean return、方差/样本数、排序、是否被 safety filter。               |
| **结果统计**   | 最终 chosen action、Top-K、best-second margin、search CPU/wall、iterations、expanded nodes。           |
| **长期结果**   | 若执行闭环：completion、task time、full return、min clearance/risk、deadline/CAP、deadlock、动作切换。 |
| **质量元数据** | 不同 RNG 之间的一致性、是否 stable/uncertain/invalid、异常/technical failure 标志。                    |

**【项目规则】**正式 Teacher 数据必须“可重新构造多种标签”。因此不能只保存 state→best action；要保留 visit/Q/ranking/安全标记，使后续可以比较 policy target、Q regression、ranking loss，而无需重跑昂贵 Teacher。

G3 退出条件：数据包完整、可哈希、可重放；所有记录具备 schema 校验；没有把 HOLDOUT 泄漏进任何设计环节。

# 6. G4：Teacher 标签质量审计与不确定性建模

高预算 MCTS 仍是随机近似算法，不能因为预算大就把其一次输出称为“ground truth”。必须先量化跨 RNG 的一致性，再决定哪些样本适合 hard label、哪些应使用 soft target、哪些应排除。

## 6.1 三层标签体系

- Stable：多个 RNG 下 Top-1/Top-K、visit 分布、Q 排序高度一致，且 margin 足够；可用于主要监督训练。

- Uncertain：不同 RNG 的优胜动作有切换，但候选集中在少数动作且价值接近；保留为 soft policy target 或 uncertainty-aware 样本，不应强塞唯一 hard label。

- Invalid：technical failure、状态/合法动作不一致、长期结果异常、Teacher 本身未达收敛条件；从正式训练与评价中剔除，但保留审计记录。

**【项目规则】**Soft target 优先来源于“多 RNG 经校准后的 visit/选择分布”，而不是人为平均 Q 后强行造概率。若不同 RNG 之间差异巨大，应先视为状态本身不确定或 Teacher 不充分，而不是归咎于网络。

## 6.2 数据分布审计

- 统计各场景、冲突阶段、动作数、速度区间、route 组合的占比，避免单一场景支配训练集。

- 检查输入特征是否出现恒为零/恒定维度、训练与在线定义不一致、单位/归一化漂移。

- 检查标签熵、margin 分布、Stable/Uncertain 比例；如果大量样本不稳定，应先回到 G2/G3，而不是加深网络。

G4 退出条件：能够明确回答“Teacher 在哪些状态可靠、哪些状态不可靠”，并形成可复现的数据清洗与 soft-label 规则。

# 7. G5：网络学习目标与离线验证

这一 Gate 的目标不是立刻决定最终网络，而是用同一 Teacher 数据比较不同学习目标，确定哪一种最能保留搜索结构，并具有低推理开销。

**【论文依据】**Deep-MCTS 用一个网络预测 action-state transition，另一个网络预测 action-selection probability，说明神经网络可以为 MCTS 提供“搜索信息”而不必直接输出最终控制。\[P5, p.1\]

**【论文依据】**Neural A\* 将学习到的 guidance map 作用于搜索，并以更少节点探索获得接近专家路径；其结论强调的是 search optimality–efficiency trade-off，而非纯分类精度。\[P7, pp.1,6,9\]

## 7.1 候选学习目标

- Policy head：预测 Teacher 的动作偏好/visit 分布。优点是直接可用于 selection prior；比只学 argmax action 更保留 Teacher 的相对偏好。

- Value head：预测 state value 或 root return，用于叶节点估值/减少深 rollout。

- Q/ranking head：预测 state-action Q 或动作排序，便于后续置信剪枝。

- Uncertainty/confidence：可由概率熵、best-second margin、深度 ensemble 或校准误差提供；不一定需要独立 head，先在 DEV 上比较。

**【项目规则】**首选候选是轻量 policy + value/Q 双任务，而不是直接复制旧 Value V3；但最终形式必须由 G4 数据性质和离线消融决定。网络复杂度优先保持小，先证明信息有效，再增加容量。

## 7.2 离线验证不能只看 accuracy

- Policy：Top-1/Top-K、cross-entropy/KL、对 stable 样本的命中率、对 uncertain 样本的概率校准。

- Value/Q：MAE/Huber、rank correlation、best-vs-second margin 保真度。

- 分组泛化：按 scene/episode/lineage 做 grouped validation；禁止随机把同一轨迹相邻状态打散。

- 推理代价：单次 forward CPU 时间必须记录，因为在线 MCTS 加速不能被网络推理吞掉。

G5 退出条件：至少存在一个轻量模型，在未见过的 DEV 分组上显著优于简单 majority/固定排序基线，并且推理代价远小于预期节省的 MCTS 计算。否则停止神经支线，回到数据/Teacher 问题。

# 8. G6：无损 Neural-guided MCTS 接入

这是和旧 K13 最大的流程区别：第一次接入网络时禁止删除动作。网络只能改变搜索顺序或估值，使我们可以单独判断“网络是否真的让 MCTS 更快收敛”。

**【论文依据】**MCTS-Minimax Hybrids 指出，均匀随机 rollout 虽可在理论极限下收敛，但更有信息的 rollout 往往能显著提升性能，因为更准确的 rollout return 会更好地引导树增长。\[P4, Sec. IV-A, p.2\]

**【论文依据】**Finnsson & Bjornsson 也说明在 playout 中使用启发式/通用信息可以让模拟更聚焦，以更快收敛到更准确的树值。\[P3, MCTS overview, p.2\]

## 8.1 接入顺序

6.  Policy prior / action ordering：所有合法动作都保留，只改变被优先尝试的次序或 UCB/PUCT 先验。

7.  若第一步有效，再测试 rollout guidance：用网络降低明显低价值 rollout 的比例，但保持安全过滤独立。

8.  若 value head 可靠，再测试 leaf/value bootstrap，观察能否缩短 rollout depth 或减少 simulation 数。

9.  每次只开一个机制，做独立消融；禁止 policy prior、value bootstrap、tree reuse、pruning 同时第一次启用。

## 8.2 无损接入的成功定义

**【项目规则】**在相同状态与 RNG 下，比较 Pure MCTS 与 Neural-guided MCTS 的预算—质量曲线。成功不是“网络动作和 Teacher 一样”，而是达到同一 completion/safety/return 目标时，Neural-guided 所需预算、iterations 或 expanded nodes 显著更少。

G6 退出条件：质量不劣于 baseline，并且出现可重复的搜索量下降；若没有，则不得进入硬剪枝。

# 9. G7：Safety-first 的 Confidence-Gated Pruning

剪枝只在 G6 证明网络信息有效之后进行。目标是把“网络帮助搜索”进一步转化为“实际减少分支”，但必须保留低置信/异常状态的回退路径。

**【论文依据】**Safety-Critical MCTS 通过风险阈值直接剪除 unsafe node，并指出 unsafe-node pruning 会降低有效 branching factor。它支持“安全剪枝优先于学习剪枝”的层级。\[P2, Sec. IV-A / IV-D, pp.6,9\]

**【论文依据】**Neural A\* 的评价表明，搜索节点减少必须和路径最优性一起看；某些方法虽然更省搜索，但会牺牲 optimality。因此我们的神经剪枝不能以“剪得多”为成功标准。\[P7, Sec.4.3–4.4, p.6\]

## 9.1 建议的剪枝层级

- 层 0：合法动作与物理约束 mask。

- 层 1：Safety filter，基于可解释风险/几何规则排除明确 unsafe 动作。

- 层 2：Neural ranking/prior，对剩余动作排序。

- 层 3：Confidence-gated pruning，仅当模型置信度、校准、OOD 检查均通过时裁剪低价值动作。

- 层 4：Fallback；低置信度、输入超出训练分布、候选 margin 小、风险接近阈值时自动恢复完整 MCTS。

**【待商议】**剪枝条件可以考虑 Top-K、累计 probability mass、best-second Q margin、ensemble agreement 等，但具体规则必须在 DEV 上预注册并做非劣效性检验后冻结。不能根据 HOLDOUT 结果再调 K。

G7 退出条件：相较 G6，计算进一步下降；同时 completion、安全代理、长期 return 不出现超过预注册容忍范围的系统性下降。

# 10. G8：端到端 Budget–Quality Curve 与统计比较

最终核心图不是单一预算下的一次结果，而是三类方法在多个预算下的质量曲线：Pure MCTS、Neural-guided MCTS、Neural-guided + pruning MCTS。

## 10.1 主要指标

| **维度**     | **建议指标**                                                                        |
|--------------|-------------------------------------------------------------------------------------|
| **任务质量** | completion rate、deadline/CAP、deadlock、full-task return、task time                |
| **安全**     | collision/hard termination、min sampled clearance、若采用则长期 risk/PET/MMTTC 代理 |
| **搜索效率** | planning CPU、wall time、iterations、expanded nodes、rollout count、每决策推理开销  |
| **稳定性**   | 动作切换、不同 RNG 方差、跨场景失败模式                                             |
| **网络贡献** | 达到固定质量阈值所需的最小预算 B\*；相对 Pure 的预算节省比例                        |

**【项目规则】**比较必须使用 matched states + paired RNG，优先报告配对效应和 bootstrap 置信区间。不要把未完成轨迹的短 task time 当成“更快”；completion/安全必须先分层。

**【论文依据】**P1 在方法比较中同时报告总通行时间、安全指标和 runtime，并通过大量独立案例/重复验证结果；这支持我们同时报告效率、安全与计算开销，而不能只报其中一个。\[P1, Sec.7.5, pp.21–23\]

G8 退出条件：能够明确回答“在相同质量目标下，神经方法节省了多少搜索预算”，并且收益在多个状态/随机流下稳定，而不是由个别轨迹驱动。

# 11. G9：独立 HOLDOUT、消融与最终冻结

HOLDOUT 只允许在 reward、Teacher 参数、网络权重、剪枝阈值、预算档位全部冻结后运行一次。其作用不是再调参，而是检验前面所有设计是否泛化。

**【论文依据】**场景工程强调 Verification & Validation 以及对 OOD/复杂场景的鲁棒性验证；这支持把最终未见场景验证作为方法可信度的一部分。\[P8\]

## 11.1 最终消融至少包括

- Pure MCTS baseline；

- 仅 policy guidance；

- 仅 value/Q guidance（若采用）；

- policy + value/Q；

- Neural guidance + pruning；

- 安全过滤开/关（若科学与安全允许，至少做离线审计，不建议用不安全配置做真实闭环）；

- 不同预算下的完整曲线，而不是只选最有利的一点。

G9 退出条件：最终报告只使用冻结配置；HOLDOUT 不再反哺训练或阈值。如果 HOLDOUT 失败，应如实记录为泛化负结果，再开启新的版本周期，而不是在原测试集上继续调参。

# 12. 数据与实验执行纪律（避免再次出现逻辑/数据错误）

- 每个 Gate 只允许一个科学变量改变；其余参数必须来自上一个冻结包。

- 每次正式运行前生成 manifest、SHA256、代码版本、输入状态哈希、RNG 预注册表。

- 先做 static check、schema check、undefined-name 检查、0-MCTS synthetic full-flow smoke，再做真实 preflight。

- 技术失败必须记录发生在多少 search / outer step；若已产生科学观测，不得假装“没跑过”并复用相同随机流。

- 所有 retry 都必须是独立 namespace，并写明为何属于 technical retry；科学结果不好不是 retry 理由。

- 所有数据包保存原始记录和汇总，不允许只保留最终均值。

- 训练日志保存逐 epoch train/validation loss、随机种子、数据 split hash、best checkpoint 选择依据。

- 网络推理开销必须计入在线预算；否则“搜索变少但总时间没变”不能算效率提升。

# 13. 关键决策点与需要导师/项目共同商议的内容

| **决策**               | **内容**                                                              | **冻结 Gate** | **为什么重要**            |
|------------------------|-----------------------------------------------------------------------|---------------|---------------------------|
| **D1 安全形式**        | 硬约束范围、风险函数、动态阈值是否采用 P1/P2 思路                     | G1            | 若改动，G2 以后全部受影响 |
| **D2 长期 reward**     | completion/progress/deadlock/time/smoothness/cooperation 的结构和权重 | G1            | Teacher 标签根本定义      |
| **D3 Teacher horizon** | H8/H12/H16 是否足够，是否需要更深                                     | G2            | 影响标签长期性与计算成本  |
| **D4 Teacher budget**  | 平台区与“足够稳定”的判据                                              | G2            | 影响 Teacher 可信度       |
| **D5 网络目标**        | policy、value/Q、ranking 或多头                                       | G5            | 决定接入点与损失函数      |
| **D6 剪枝准则**        | Top-K/概率质量/margin/ensemble、fallback 条件                         | G7            | 决定质量—效率权衡         |
| **D7 非劣效容忍**      | completion/safety/return 允许的最大下降范围                           | G7/G8         | 决定何时可宣称加速成功    |

**【项目规则】**这些 D1–D7 才是需要“商议/请教老师”的核心问题。除此之外的数据隔离、Gate 顺序、先质量后效率、HOLDOUT 不泄漏等流程原则不应反复改动。

# 14. 最终“成功”的严格定义

本项目不以“网络准确率更高”“单步 MCTS 时间更短”或“剪掉了更多动作”作为最终成功。正式成功应同时满足：

10. 在独立 HOLDOUT 上，任务完成与硬安全指标不劣于冻结 Pure MCTS 基线；

11. 在相同质量目标下，Neural-guided 或 Neural+Pruning 达到目标所需的在线预算、CPU、iterations 或 expanded nodes 显著更少；

12. 该节省不是由未完成轨迹、提前失败或更冒险的行为换来的；

13. 网络 forward 开销已经计入总在线成本；

14. 结果在多个场景和 paired RNG 上稳定，且有可审计的失败模式；

15. 最终模型、数据、代码、阈值、HOLDOUT 结果可由冻结包复现。

**【论文依据】**这一“同质量下减少搜索”的定义与 Neural A\* 的 optimality–efficiency trade-off 思路一致；同时 P1/P2 强调安全与效率必须共同评估，不能用安全退化换计算加速。\[P7; P1; P2\]

# 15. 指定论文参照与本流程中的用途边界

**\[P1\]** Bu, F., Chen, P., Yu, G., Wang, Y. Risk-aware unsignalized intersection management in unstructured mixed-traffic environment: a real-time hierarchical safety evaluation method. Transportation Research Part C, 192 (2026) 105890.  
用途边界：用于：模拟—评价范式、即时+长期风险、候选策略安全评价、同时报告安全/效率/runtime。不能直接给出 MineSim 的 reward 权重或风险阈值。

**\[P2\]** Lin, Z., Lan, J., Anagnostopoulos, C., Tian, Z., Flynn, D. Safety-Critical Multi-Agent MCTS for Mixed Traffic Coordination at Unsignalized Intersections.  
用途边界：用于：V2V/V2H/V2R 安全检查、unsafe node pruning、多目标 reward、MCTS 复杂度与收敛分析、tree reuse。论文中的 300–600 次收敛与 K=1000 仅是其场景结果。

**\[P3\]** Finnsson, H., Bjornsson, Y. Game-Tree Properties and MCTS Performance. GIGA 2011.  
用途边界：用于：解释 depth/branching factor/progression 对 MCTS 的影响，以及 informed playout 促进更快收敛的动机。不是自动驾驶领域直接参数依据。

**\[P4\]** Baier, H., Winands, M. H. M. MCTS-Minimax Hybrids. IEEE TCIAIG, 2015.  
用途边界：用于：说明更有信息的 rollout/浅层搜索可提升 MCTS return 质量；提醒 MCTS 对局部陷阱可能敏感。不能直接把 minimax 结构照搬到 MineSim。

**\[P5\]** Chen, J., Zhang, C., Luo, J., Xie, J., Wan, Y. Driving Maneuvers Prediction Based Autonomous Driving Control by Deep Monte Carlo Tree Search. IEEE TVT, 2020.  
用途边界：用于：神经网络提供动作选择概率/状态预测并服务于 MCTS，而不是直接替代 MCTS。其视觉输入、网络结构和实验平台不直接迁移。

**\[P6\]** Li, L., Chen, Z., Wang, J., Zhou, B., Yu, G., Chen, X. Multimodal Trajectory Prediction for Autonomous Driving on Unstructured Roads using Deep Convolutional Network.  
用途边界：用于：矿区非结构化道路长期预测不确定性与多模态概率表达。可启发 uncertain label/OOD 处理，但不是 MCTS Teacher 标签论文。

**\[P7\]** Yonetani, R., Taniai, T., Barekatain, M., Nishimura, M., Kanezaki, A. Path Planning using Neural A\* Search. ICML 2021.  
用途边界：用于：学习型搜索指导与“最优性—搜索效率”联合评价、减少 node exploration。不能把 differentiable A\* 机制原样视为 MCTS 方案。

**\[P8\]** Teng, S. et al. Scenario Engineering for Autonomous Transportation: A New Stage in Open-Pit Mines.  
用途边界：用于：场景特征、Calibration/Certification、Verification/Validation、OOD 与鲁棒性视角，支撑数据覆盖和独立验证。

**\[P9\]** Zhao, Z., Bi, L. A New Challenge: Path Planning for Autonomous Truck of Open-Pit Mines in The Last Transport Section. Applied Sciences, 2020.  
用途边界：用于：矿区地形/粗糙度/成本建模与 Hybrid A\* 背景；当前不直接决定神经 MCTS 的 Teacher、网络或剪枝设计。

# 附录 A：每次进入下一 Gate 前的强制检查清单

- □ 上一 Gate 是否有明确 PASS/FAIL/HOLD，而不是“感觉差不多”？

- □ 本 Gate 唯一科学变量是什么？其余参数是否冻结？

- □ 输入状态、随机流、代码和配置是否都有 SHA/manifest？

- □ 是否意外使用了 HOLDOUT 或未来结果信息？

- □ 是否有字段/schema 缺失导致后续无法重构标签？

- □ 是否把 technical failure 与 scientific negative result 混淆？

- □ 如果要 retry，失败发生前是否已经消费搜索/随机流/科学观测？

- □ 结果是否同时报告质量、安全和计算，而不是只选有利指标？

- □ 本轮结论是论文直接支持、项目实验支持，还是设计提案？三者是否清楚区分？

# 附录 B：当前建议的第一实际动作

在本流程下，下一步不是立即跑大规模 Teacher 数据，而是完成 G1：把现有 MineSim reward / safety / terminal / deadlock / progress 定义逐项抄出，与 P1/P2 的风险—安全—长期评价框架对照，形成“保留 / 修改 / 新增 / 待导师确认”四列表。只有 G1 冻结后，才值得进入 G2 的预算×Horizon 收敛标定。
