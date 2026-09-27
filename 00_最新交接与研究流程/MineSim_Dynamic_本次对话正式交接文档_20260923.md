**MineSim-Dynamic**

**本次对话正式交接文档**

从 H8 / ConflictGuide 工程支线到“神经网络真正提升 MCTS 搜索效率”的主线重构

Evidence cutoff：2026-09-23（以本次对话中已上传资料、终端回传记录和正式文档为限）

| **使用说明：**本文件用于下一位 AI / 工程人员快速接手。本文件只总结本次对话中完成、确认、冻结或改变方向的内容；历史更早的项目事实仍以正式 frozen result、manifest、Git、SHA 和最新权威 handoff 为准。缺少当前 AutoDL 直接证据的字段统一标记为 HOLD。 |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# 快速接手区

| **问题**                   | **当前结论**                                                                                                                  |
|----------------------------|-------------------------------------------------------------------------------------------------------------------------------|
| 项目现在做到哪里？         | 已经完成 H8 / ConflictGuide 若干工程与 selector 实验，并在本次对话中正式把研究主线切回“神经网络直接辅助 MCTS，提高搜索效率”。 |
| 当前唯一有效 Gate          | G1：Teacher 评价体系 / Safety constraint / 长期 Reward 重审。现在不应先跑新 Teacher 数据。                                    |
| 当前资源                   | LOW。只需文献、代码/Reward 审计、数学定义与协议设计；未到 HIGH-CPU / HIGH-GPU。                                               |
| 当前正式 repo              | /root/MineSim-Dynamic                                                                                                         |
| 大文件/实验数据目录        | /root/autodl-tmp                                                                                                              |
| 当前 Git HEAD              | HOLD：本次对话未重新读取 live Git。                                                                                           |
| 当前 AutoDL live inventory | HOLD：用户取消了数据盘全量 inventory；未执行整理。                                                                            |
| 已经冻结无需重跑           | Eager vs Lazy Retry2、Guide Selector DEV64 Retry1 等本次对话已分析完成的正式实验。                                            |
| 当前不应做                 | 不直接训练新网络；不先跑大规模 Teacher；不先做硬剪枝；不碰 HOLDOUT；不删除云端科研资产。                                      |
| 下一步最小行动             | 把现有 MineSim reward / safety / terminal / deadlock / progress 与论文框架逐项对照，形成 G1 数学定义与保留/修改/新增清单。    |

| **主线已经改变：**此前计划中的 GUIDE_SELECTOR_DEV_DATA_STABILIZATION_V1（56 policies）不再是当前默认下一步。Guide Selector 分支保留为历史科研支线，只有用户明确重新启用时才继续。 |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# 1. 本次对话的起点与证据纪律

本次对话不是从零开始。用户带入了此前多个 MineSim 实验、正式日志、Retry 结果、状态池冻结资料和历史交接包。本轮首先恢复这些证据的层级关系，然后继续推进。整个过程遵循用户提供的《MineSim-Dynamic 项目统一工作流 Skill》：真实终端/源码/SHA/正式结果优先于历史文档与 AI 记忆；一次只推进一个 Gate；正式实验必须按 preflight → static/smoke → 短闭环 → 完整实验 → freeze 的顺序；Technical FAIL 与 Scientific FAIL 必须区分；one-time / retry-limited 实验不得自动重跑。

- 正式仓库保持：/root/MineSim-Dynamic。

- 大型实验、日志、模型、bundle 优先放：/root/autodl-tmp。

- 当前对话后半段明确进入 HANDOFF MODE，本交接文档即为该模式产物。

- 数据盘整理遵循“只读 inventory → checksum/equivalence → 用户授权 → delete → post-delete manifest”；本轮没有进入 delete。

# 2. 本次对话读取与核验了哪些资料

本轮先后读取/展开了两批项目归档和一组论文。其主要作用不是覆盖最新实验，而是恢复 provenance、核对历史算法路线、确认 MineSim 原项目与后续扩展的边界。

| **资料组**                             | **本次用途与结论**                                                                                                                   |
|----------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------|
| 第二批去冗余：地图与原项目复现         | 确认 MineSim 原始底座、地图/GeoJSON、IDMPlanner/replay 复现资料；明确原论文 benchmark 与后续 Fleet-MCTS/Value/Guide 扩展不是同一层。 |
| 第二批去冗余：参考论文、方向与效果对比 | 确认外层 ZIP 正常；内嵌 7z 在当时环境不可直接完整展开，因此未把未解析内容当作新证据。                                                |
| 历史损坏大包分片 A/B                   | 按 manifest 重新拼接后字节/SHA 可对应，但原始重组对象本身仍为损坏 ZIP；因此保存为历史原始字节证据，不作为可解析正式实验包。          |
| 当前接手核心与最新证据                 | 恢复截至 9 月 19 日的权威历史底座；确认当时 H16→H8 阶段式方案里 H8 实际未触发，后续需要直接 H8/H16 对照。                            |
| 历史交接文档                           | 恢复 Value V3、Confidence Gating、K13 pruning 的真实收益与负结论。                                                                   |
| 专项证据与论文资料                     | 恢复跨场景 Fleet-MCTS、1536 条历史采集、SafetyRiskEvaluator、Paper 1/2 兼容性以及旧数据边界。                                        |

# 3. H8 / ConflictGuide 工程支线：本轮确认的最终结论

对旧结果重新梳理后，本轮没有继续把“冲突前 H16、冲突后 H8”当作既定事实。后续真实结果已经支持：在当前开发条件下，固定 H8 是强基线，H12/H16 并不天然更优。

## 3.1 Eager certificate vs Lazy certificate Retry2

| **项目**             | **结果**                                                                                                                  |
|----------------------|---------------------------------------------------------------------------------------------------------------------------|
| 技术状态             | PASS；8/8 完整记录；此前 Retry1 的 audit_hold / RNG 技术问题闭环。                                                        |
| 公平成功对照（3 对） | Lazy 相对 eager：任务时间约 -0.88%，累计规划 CPU 约 -1.09%，admitted iterations +39.5%，动作切换 +6.1%，return 约 -2.0%。 |
| 净距                 | 公平对照平均 sampled minimum clearance 1.249 m → 1.019 m；4/4 pair 的 lazy 最小净距均低于 eager。                         |
| 证书触发             | 4 条 lazy 完整轨迹均保持 UNBUILT，build_attempts = 0；说明该批轨迹中 eager 的提前证书计算确属未被使用的前置成本。         |
| 最终科研判定         | MIXED；保留为 experimental engineering optimization，但不替换默认 baseline，不宣称整体性能/安全性更优。                   |

## 3.2 Native H8 vs Guide H8：为什么 Guide 不能直接当默认

Matched 对照与后续 DEV64 均表明 Guide 的平均整体收益很小，同时存在状态依赖和安全裕度下降。其真正价值更像“某些状态有用的 search guidance”，而不是全局替代 Native。

# 4. Guide Selector 分支：做了什么、为什么冻结

## 4.1 Oracle headroom

4 个物理状态的 hindsight oracle 显示：state01→Guide、state02→Native、state03→Guide、state04→Guide。相对始终 Guide，理论上还能获得约 1.9% 的任务时间和约 2.0% 的规划 CPU 改善，并改善平均净距。这说明“是否启用 Guide”存在状态依赖，因此 selector 概念不是无意义。

## 4.2 状态池扩展与 DEV/HOLDOUT/RESERVE 冻结

从历史 Native 轨迹中重建 Guide-active 状态区域，按原 ConflictGuide.region() 的 rounded cache-index 规则核验 BEFORE/INSIDE/AFTER，并与显式 regions_before 记录交叉验证。最终冻结 31 个合格唯一状态：DEV 16、HOLDOUT 8、RESERVE 7。HOLDOUT 从冻结后起不得在模型/阈值冻结前执行。

## 4.3 DEV64 正式 matched evaluation

| **指标**           | **结果**                                                                                    |
|--------------------|---------------------------------------------------------------------------------------------|
| 技术执行           | PASS；64/64；POLICY_SEARCH_COMPLETED=5379；OUTER_COMPLETED=5378；RC=0；HOLDOUT 未执行。     |
| 双方都成功的 26 对 | Guide 相对 Native：任务时间 -0.77%，规划 CPU -0.80%，完整回报 +0.55%，最小采样净距 -5.53%。 |
| 状态级偏好         | Guide-preferred 9/16；Native-preferred 7/16。                                               |
| 随机稳定性         | 仅 9/16 状态两组 RNG 同向；7/16 混合：guide_dev_01/02/04/05/06/11/15。                      |
| 轻量可分性         | Logistic Regression LOOCV 37.5%；Small MLP 31.3%；Always-Guide baseline 56.25%。            |
| 当时结论           | DO NOT TRAIN THE GUIDE SELECTOR YET。原计划是增补 56 policies 做数据稳定化。                |

| **本轮新的战略判断：**虽然 Guide Selector 有一定 oracle headroom，但它并没有直接解决用户最关心的“显著提高 MCTS 搜索效率”。因此用户决定把 Guide Selector 冻结为历史支线，重新设计更直接的 Neural-MCTS 主线。 |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# 5. 重新审视旧神经网络 / 剪枝路线

本次对话重新阅读历史交接与论文后，明确旧 Value V3 / Confidence Gating / K13 并非“网络完全失败”，而是“网络学到了一些信号，但未稳定转化为端到端搜索效率”。

| **旧问题**           | **本轮统一解释**                                                                        |
|----------------------|-----------------------------------------------------------------------------------------|
| 数据覆盖不足         | 2356 个 root 实际来自 3 场景 / 6 episode，且 C11 约占 75.55%；训练分布偏。              |
| 教师标签不是真值     | 教师 Q 来自有限预算 MCTS，存在 RNG 和 budget 误差；硬标签可能把教师噪声当成绝对真值。   |
| 输入特征质量问题     | 旧审计曾发现两个 acceleration 输入长期为 0，说明数据管线本身也需要审计。                |
| 网络接入点不够省计算 | 旧 root-order 主要改变 16 个根动作的展开顺序，但 rollout/backup 等大头仍继续执行。      |
| K13 硬剪枝闭环副作用 | 单步候选数减少并不等于完整任务 CPU 下降；闭环轨迹变化可能使后续规划变难，吃掉局部收益。 |
| 结论                 | 不应该原样复制 Value V3 + 固定 K13；要重新定义 Teacher、网络目标和接入/剪枝顺序。       |

# 6. 本轮针对新路线完成的论文审查

用户提出新的四点设想后，本轮集中阅读 9 篇相关资料，用于确定“哪些设计可以有论文依据，哪些仍需项目内验证或请教老师”。

| **论文/资料**                                                                                 | **对新路线的直接启发**                                                                                                                                                               |
|-----------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Safety-Critical Multi-Agent MCTS for Mixed Traffic Coordination at Unsignalized Intersections | 把安全约束与优化目标分层；不安全节点可先过滤；reward 再平衡 safety/efficiency/cooperation；给出 K、dmax 与复杂度关系，并展示约 300–600 iteration 的收敛平台、K=1000 的裕量设置思路。 |
| Driving Maneuvers Prediction Based Autonomous Driving Control by Deep MCTS                    | 网络不是替代 MCTS，而是给 MCTS 提供 action-state transition 和 action-selection probability，搜索再重构未来轨迹。                                                                    |
| Path Planning using Neural A\* Search                                                         | 评价神经搜索时不能只看网络准确率，核心要同时看“规划质量/最优性”与“搜索节点减少量”的 trade-off。                                                                                      |
| MCTS-Minimax Hybrids                                                                          | informed rollout 可以提高 rollout return 质量、加快搜索收敛；提醒 MCTS 的长远优势与 shallow trap 风险。                                                                              |
| Game-Tree Properties and MCTS Performance                                                     | 搜索深度增加会拉长单次 simulation、减少 root 样本；树宽与深度存在平衡，支持 budget×depth 不能只单向加大。                                                                            |
| Risk-aware unsignalized intersection management…                                              | 用“模拟未来轨迹→逐时刻风险→长期累计风险”评价候选策略，支持重新设计长期安全/风险评价。                                                                                                |
| Multimodal Trajectory Prediction…                                                             | 矿区非结构化道路的人类驾驶轨迹存在多模态与长期不确定性，未来若把外车预测纳入 MCTS，应考虑概率分布而非单轨迹。                                                                        |
| Scenario Engineering for Autonomous Transportation…                                           | 支持开发/验证时重视场景覆盖、Calibration & Certification、Verification & Validation、OOD 和鲁棒性。                                                                                  |
| A New Challenge: Path Planning for Autonomous Truck…                                          | 矿区路径评价应考虑 terrain/roughness 等成本，但这属于路径/环境层参考，不直接决定 Neural-MCTS 网络结构。                                                                              |

# 7. 本轮正式重构出的新研究主线

用户明确提出：重新跑更高质量、真正收敛的 Teacher 数据；标定“再加预算也基本无收益”的最大有效点；网络先保证决策质量再提高效率；剪枝评分与 reward/远期评价要重新按论文审查。基于此，本轮把总体流程冻结为 G0–G9。

| **Gate**                     | **核心问题**                       | **关键逻辑 / 退出条件**                                                                                                                                                                         |
|------------------------------|------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| G0 基线冻结                  | 和谁比较？                         | 保留现有 Pure/Native H8（当前在线基线）作为固定参照；不在新研究过程中随意改基线。                                                                                                               |
| G1 评价体系重构              | 什么叫好决策？                     | 先定义 hard safety constraint 与 long-horizon utility；明确 collision/boundary/risk、completion、deadlock、progress、efficiency、comfort/cooperation 的层级。评价定义未冻结前不生成新 Teacher。 |
| G2 Teacher Budget×Depth 标定 | MCTS 要算到哪里才可信？            | 对搜索 budget/iterations 与 rollout depth/horizon 分开扫描；用 root action 稳定性、排名稳定性、Q gap、闭环任务效果和边际收益找 knee point。                                                     |
| G3 高质量 Teacher 数据       | 怎样避免再次得到低质量标签？       | 多场景、多物理状态、多 RNG；一次保存完整 root statistics，而非只存 best action。                                                                                                                |
| G4 标签审计                  | 哪些样本真的能学？                 | 按 Stable / Uncertain / Invalid 分类；不把有限预算 MCTS 当绝对真值；按 scene/episode/lineage 分 train/val/holdout，防止相邻状态泄漏。                                                           |
| G5 网络学习                  | 学 policy、value、Q 还是 ranking？ | 先离线比较目标和结构，不接硬剪枝；成功标准不只看 top-1 accuracy。                                                                                                                               |
| G6 无损 Neural-guided MCTS   | 网络是否真正帮助搜索？             | 保留全部合法动作，只用 prior/ordering/rollout/leaf-value 等 guidance；证明在同等质量下所需 simulations/budget 更低。                                                                            |
| G7 Confidence-Gated Pruning  | 如何把省下的计算真正兑现？         | 仅在 G6 已证明质量不降后引入剪枝；Safety Filter 在前；网络低置信/OOD 时退回完整 MCTS；不再固定 K13。                                                                                            |
| G8 Budget–Quality 曲线       | 效率提升是否是端到端的？           | 比较 Pure MCTS、Neural-guided、Neural+Pruning 的 budget→quality 曲线，而不是只看局部单步耗时。                                                                                                  |
| G9 独立 HOLDOUT              | 是否可泛化？                       | 网络、阈值、pruning 规则全部冻结后再跑独立 HOLDOUT；不得边看结果边调参。                                                                                                                        |

# 8. 新流程中最关键的逻辑约束

1.  Reward / Safety 必须先冻结，再跑大规模 Teacher。否则 reward 一改，旧 Teacher Q/排序/标签可能整体失效。

2.  Teacher budget 与 rollout depth 不是同一个参数。需要分开标定；“预算越大”“步数越深”都不等于更好。

3.  Teacher 数据必须保存完整 root statistics：合法动作、visit count、Q/return 分布、ranking、safety flag、rollout 数、terminal/completion、clearance/risk 和最终动作。

4.  多 RNG 的作用不是简单取多数票，而是估计 Teacher 标签稳定性和不确定性。稳定样本可 hard/soft label；不稳定样本不能假装是绝对真值。

5.  第一次网络接入禁止硬剪枝。先证明网络能让 MCTS 在更低 budget 下达到相同质量，再允许剪枝。

6.  最终成功标准从“网络准确率高”改为“同等安全/任务质量下，MCTS 所需 budget/simulation 明显下降”。

7.  Safety 不能因为工程上被计算出来就自动升级为 hard rule。只有 frozen gate 证明的 safety constraint 才可用于正式 pruning。

# 9. 本次对话已生成的正式研究流程文档

本轮已经生成《MineSim 神经网络辅助 MCTS 严谨研究流程 V1》Word 文档，用于把上述 G0–G9 研究流程、论文依据、PASS/FAIL 逻辑、Teacher 质量、网络接入和剪枝顺序固化。该文档是新主线的设计依据之一，但仍低于未来 AutoDL live 源码 / Git / frozen result 的证据优先级。

- ChatGPT 当前会话副本：MineSim_神经网络辅助MCTS_严谨研究流程_V1.docx。

- AutoDL 是否已有同名副本：HOLD（本次未重新做 live inventory）。

# 10. 云端数据盘整理：本轮做到哪里

用户随后要求“只整理数据盘下面的文件”。本轮给出过一个只读 inventory 脚本，目标是扫描 /root/autodl-tmp、统计 SHA/大文件/扩展名/重复文件并生成 inventory ZIP。但是用户认为脚本过慢，明确取消继续运行。因此云端整理没有真正开始。

| **事项**                              | **当前状态**                                                                                        |
|---------------------------------------|-----------------------------------------------------------------------------------------------------|
| 数据盘只读 inventory                  | CANCELLED / NOT COMPLETED                                                                           |
| move / isolate / archive / quarantine | 未执行                                                                                              |
| actual delete                         | 未执行                                                                                              |
| post-delete manifest                  | 不适用                                                                                              |
| 当前 /root/autodl-tmp live 状态       | HOLD；不能根据聊天推断哪些文件仍在/已移。                                                           |
| 后续如需整理                          | 改用更快的分层 inventory：先 ls/du/find 元数据，不先对所有文件计算 SHA；确定候选后再局部 checksum。 |

| **严禁误写：**本次对话不能写“数据盘已整理”“某文件已删除”。用户明确在 inventory 阶段就停止了，且没有任何 delete 授权。 |
|-----------------------------------------------------------------------------------------------------------------------|

# 11. 当前唯一有效 Gate 与下一步

| **资源：**LOW。当前不需要 HIGH-CPU，也不需要 HIGH-GPU。 |
|---------------------------------------------------------|

当前唯一有效 Gate：G1_TEACHER_EVALUATION_AND_SAFETY_REWARD_DESIGN_V1（可用此名称继续，也可在正式 preregistration 时改成更规范的项目命名）。

下一步不是运行 MineSim，而是把当前 MineSim 中已有的 reward / safety / terminal / progress / deadlock / clearance/risk 实现逐项提取出来，与本轮论文框架做一张“保留 / 修改 / 新增 / 仅诊断 / HOLD / 需请教老师”的对照表，并形成第一版数学定义。

| **G1 必须产出**                    | **PASS 标准**                                                                                          |
|------------------------------------|--------------------------------------------------------------------------------------------------------|
| Safety constraint 定义             | 明确哪些事件/指标是不可交易的 hard filter，哪些仅是 diagnostic sidecar，避免把观察指标误写成安全保证。 |
| Long-horizon utility / reward 定义 | 明确 completion、deadlock、progress、效率、平滑/协作的层级、折扣和 horizon 作用。                      |
| 旧 reward 对照表                   | 每个旧项标注 KEEP / MODIFY / DROP / HOLD，并说明论文或项目证据。                                       |
| Teacher label contract             | 明确未来保存 Q/visits/ranking/return distribution/safety 等字段；禁止只保存 best action。              |
| G2 preregistration 草案            | 明确 budget×depth 的候选档位与收敛判据，但 G1 未 PASS 前不执行。                                       |

# 12. 禁止重复 / 禁止提前做的事项

- 不要自动重跑 Eager vs Lazy Retry2；其科学结论已形成。

- 不要自动重跑 Guide Selector DEV64 Retry1；其 64/64 正式结果已形成。

- 不要继续执行原计划 56-policy Guide Selector 数据稳定化，除非用户明确恢复该支线。

- 不要直接训练 Value V4 / 新 MLP / 新深网；G1–G4 未完成前训练没有可靠 Teacher 基础。

- 不要直接恢复固定 K13 或先剪枝后验证。新流程规定 G6 无损 guidance PASS 后才进入 G7 pruning。

- 不要因为文献给出 K=1000、300–600 iteration 收敛就照搬数值到 MineSim；那只是论文场景证据，我们自己的 G2 必须独立标定。

- 不要把 sampled clearance、risk sidecar 等诊断量自动升级成 hard production safety rule。

- 不要在 AutoDL 上做未授权删除；当前数据盘 live inventory 仍为 HOLD。

# 13. 证据状态与 HOLD 项

| **对象**                                             | **状态**                                                                       |
|------------------------------------------------------|--------------------------------------------------------------------------------|
| 本次对话的上传归档 / 论文                            | 已读取到足以支持当前研究流程的层面；部分历史内嵌 7z 未完整解析，不作额外推断。 |
| H8/Guide/eager-lazy/DEV64 结果                       | 以本次对话中用户回传的正式日志与结果汇总为当前有效历史证据。                   |
| 最新 AutoDL Git HEAD / git status                    | HOLD：未在本轮结束前重新采集。                                                 |
| 最新 /root/autodl-tmp 文件清单                       | HOLD：inventory 已取消。                                                       |
| 当前 AutoDL 上是否存在本轮生成 Word                  | HOLD：ChatGPT 会话副本存在，但未验证上传回 AutoDL。                            |
| 未来 Teacher budget、depth、reward 权重、safety 阈值 | HOLD：必须经 G1/G2 冻结，不能从论文数值直接抄。                                |

# 14. 下一位 AI 必须继续遵守的工作流

1\. 先读本交接 + 当前 Skill + 最新 AutoDL terminal/Git/frozen artifact；不要无目的重扫所有历史包。

2\. 每次只推进一个最小 Gate。

3\. 执行顺序固定：只读 preflight → static/smoke → 短闭环 → 完整实验 → freeze。

4\. Technical FAIL 先定位 fault domain；Scientific FAIL 是科研结果，不自动调参重跑。

5\. One-time / retry-limited 实验执行前必须 preregistration、输入 SHA、namespace absent、authorization；失败后先判断已经消费多少 scientific information。

6\. LOW 能完成的前置工作不要开高资源。Teacher 大规模 collection 才考虑 HIGH-CPU；正式网络训练才考虑 HIGH-GPU。

7\. 长任务用普通 terminal/screen + 独立 log/progress/RC/START/CAPTURE；不要让模型在线等。

8\. 核心源码优先最小 patch；禁止未授权 git reset --hard / git clean -fd / git add .。

9\. 科研资产删除必须单独授权；move/archive/quarantine 与 delete 必须严格区分。

# 15. 本轮重点参考文献（用于研究设计，不代表参数可直接照搬）

- Bu, F. et al. Risk-aware unsignalized intersection management in unstructured mixed-traffic environment: a real-time hierarchical safety evaluation method. Transportation Research Part C, 2026, 192:105890.

- Lin, Z. et al. Safety-Critical Multi-Agent MCTS for Mixed Traffic Coordination at Unsignalized Intersections.

- Finnsson, H., Bjornsson, Y. Game-Tree Properties and MCTS Performance.

- Baier, H., Winands, M. H. M. MCTS-Minimax Hybrids. IEEE Transactions on Computational Intelligence and AI in Games, 2015.

- Chen, J. et al. Driving Maneuvers Prediction Based Autonomous Driving Control by Deep Monte Carlo Tree Search. IEEE Transactions on Vehicular Technology, 2020.

- Li, L. et al. Multimodal Trajectory Prediction for Autonomous Driving on Unstructured Roads using Deep Convolutional Network.

- Yonetani, R. et al. Path Planning using Neural A\* Search. ICML, 2021.

- Teng, S. et al. Scenario Engineering for Autonomous Transportation: A New Stage in Open-Pit Mines.

- Zhao, Z., Bi, L. A New Challenge: Path Planning for Autonomous Truck of Open-Pit Mines in The Last Transport Section. Applied Sciences, 2020.

# 16. 最终交接结论

| **当前主线：**Guide Selector 已冻结为历史支线。当前主线是：重新定义 Teacher 的评价体系与安全/长期价值 → 标定可靠但不浪费的 MCTS budget×depth → 生成高质量多 RNG Teacher → 审计标签稳定性 → 训练 policy/value/Q/ranking 网络 → 先无损引导 MCTS → 再做 confidence-gated pruning → 用 budget–quality 曲线与独立 HOLDOUT 证明真实效率提升。 |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

| **当前立即动作：**只做 G1。不要跑新数据，不要训练网络，不要剪枝，不要整理/删除云端文件。先把现有 MineSim reward/safety 代码与论文逐项对齐并形成数学定义。 |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------|
