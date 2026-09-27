**MineSim-Dynamic**

**项目必备配套资料、风险清单与 AI 长期交接手册**

——作为前三份文档之外的“研究治理 + 风险预案 + 长期接管”第四份总手册——

| **项目**     | **内容**                                                                                                      |
|--------------|---------------------------------------------------------------------------------------------------------------|
| 适用项目     | MineSim-Dynamic：露天矿无人矿卡规划与仿真                                                                     |
| 当前正式仓库 | /root/MineSim-Dynamic                                                                                         |
| 当前基线     | autodl-idm-baseline / 2521aa4 / idm-replay-autodl-baseline                                                    |
| 当前阶段     | IDM baseline 已冻结；Pure MCTS 尚未正式开始编码                                                               |
| 这份文档回答 | 除了前三份文档之外还缺什么、哪些东西必须建立、最可能遇到哪些技术/实验/AI 协作问题、发生问题时如何判断和处理。 |
| 主要读者     | 本人、导师、后续同学、DeepSeek/Kimi/豆包等普通 AI、未来新的 AI Agent                                          |

| **定位：**前三份文档分别回答“现在有什么”“算法怎么做”“普通 AI 怎么操作云端”。本文件补上最容易被忽视但决定项目最终能否成功复现、写论文和长期接管的部分：实验规范、测试资产、日志、版本治理、风险矩阵、数据治理、评估协议、AI 交接包与故障预案。 |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# **目录与使用说明**

1\. 四份文档如何配套：谁负责什么

2\. 除了文档，项目真正还需要哪些“实体资产”

3\. 第一优先级：建立项目内 AI_HANDOFF.md 与 PROJECT_STATUS.md

4\. 第二优先级：建立实验台账 EXPERIMENT_LOG 与结果目录规范

5\. 第三优先级：建立测试体系与最小回归场景

6\. 第四优先级：建立 Metrics 评价脚本和统一结果表

7\. 第五优先级：建立配置、随机种子与可复现性规范

8\. 数据与训练集治理：Pure MCTS 到 Neural-MCTS 时必须补齐的东西

9\. 模型与 checkpoint 治理：避免“模型能跑但不知道怎么来的”

10\. Git 与代码治理：分支、commit、tag、回滚和 AI 改码纪律

11\. 云端与环境治理：磁盘、Conda、GPU、依赖和备份

12\. Pure MCTS 最可能遇到的算法问题

13\. MineSim 集成最可能遇到的工程问题

14\. Neural-MCTS 最可能遇到的训练和搜索问题

15\. 评价实验最可能遇到的方法学问题

16\. AI 协作最可能遇到的问题：普通 AI 会怎么把你带偏

17\. 风险矩阵：严重程度、触发信号、第一检查项与处理办法

18\. 一次实验从开始到结束的标准 SOP

19\. 出问题时的故障分层决策树

20\. 给任何 AI 的“项目交接包”应包含什么

21\. 论文阶段还必须补齐哪些证据

22\. 未来 12 个里程碑与每一步的验收条件

附录 A. 推荐新增的项目文件模板

附录 B. AI 接手时的强制核验清单

附录 C. 当前项目的已知事实与当前限制

| **使用方法：**不是要求一次性把全部东西都做完。先按第 2 节的 P0/P1/P2 优先级补齐；每完成一个 MCTS 里程碑，再更新对应台账和 handoff。这样未来换 AI、换机器、换人都不会失忆。 |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# **1. 四份文档如何配套：谁负责什么**

| **文档**                                  | **主要回答**                                                     | **定位**           |
|-------------------------------------------|------------------------------------------------------------------|--------------------|
| 文档 1：云端资产说明书                    | 回答“现在云端有什么、在哪里、是什么状态”                         | 事实源/项目地图    |
| 文档 2：Pure MCTS 与 Neural-MCTS 实施手册 | 回答“算法怎么一步一步实现、怎么评价”                             | 算法施工图         |
| 文档 3：普通 AI 与 AutoDL 交互调试手册    | 回答“普通 AI 看不到云端时，人如何安全地让它写/改/调代码”         | 操作规程           |
| 文档 4：本手册                            | 回答“项目还缺哪些长期资产、会遇到哪些坑、如何形成可复现研究工程” | 风险治理与长期交接 |

四份文档不能代替代码、测试、实验日志和数据本身。一个研究项目真正可接管，必须同时具备“说明文档 + 可运行代码 + 固定环境 + 固定配置 + 测试 + 数据/结果 + 日志 + 版本历史”。

# **2. 除了文档，项目真正还需要哪些“实体资产”**

| **优先级** | **资产**                             | **推荐位置**                             | **作用**                                                      | **当前状态** |
|------------|--------------------------------------|------------------------------------------|---------------------------------------------------------------|--------------|
| P0         | AI_HANDOFF.md                        | 仓库根目录                               | 每次给 AI 的实时上下文；只写当前事实，不写长篇理论            | 尚未建立     |
| P0         | PROJECT_STATUS.md                    | 仓库根目录                               | 当前阶段、已完成/未完成、已知 bug、下一步                     | 尚未建立     |
| P0         | EXPERIMENT_LOG.md 或 experiments.csv | /root/autodl-tmp/mcts_results + 仓库索引 | 每次实验参数、commit、seed、场景、结果、结论                  | 尚未建立     |
| P0         | tests/                               | 仓库内                                   | State/Transition/Reward/Search/Planner shell 的单元与回归测试 | 尚未建立     |
| P0         | metrics/ 或 evaluation/              | 仓库内                                   | 统一计算安全/效率/舒适/计算开销指标                           | 尚未建立     |
| P1         | run scripts                          | scripts/ 或 other_scripts/               | 固定一条命令复现 baseline/MCTS/评估                           | 需要新增     |
| P1         | configs manifest                     | 仓库内 markdown/csv                      | 记录每个实验 YAML 对应哪种方法                                | 需要新增     |
| P1         | seed protocol                        | 配置 + 文档                              | 固定随机种子生成方式和重复次数                                | 需要新增     |
| P1         | dataset manifest                     | /root/autodl-tmp/mcts_data/manifest.\*   | 训练/验证/测试场景来源、样本数、生成 commit                   | 神经阶段需要 |
| P1         | checkpoint metadata                  | 每个模型旁 json/yaml                     | 模型结构、数据集、loss、seed、commit、指标                    | 神经阶段需要 |
| P2         | benchmark report generator           | evaluation/                              | 自动产出 CSV/图表/论文表格                                    | 正式实验阶段 |
| P2         | backup manifest                      | /root/autodl-tmp/backups/                | 明确哪些备份可恢复什么                                        | 建议建立     |

| **最重要：**如果只能再补三样，不是再写三份 Word，而是建立 AI_HANDOFF.md、EXPERIMENT_LOG、tests/。它们会直接决定未来 AI 是否能准确接上、实验是否可复现、改代码是否会把 baseline 弄坏。 |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# **3. 第一优先级：建立项目内 AI_HANDOFF.md 与 PROJECT_STATUS.md**

## **3.1 为什么 Word 不能替代实时 handoff**

Word 适合“稳定知识”。但 Git HEAD、最近一次实验、当前 bug、刚改了哪些文件每天都会变。把这些实时信息继续写进 Word，会很快过期。因此项目根目录必须有一个短小、可随 commit 更新的 Markdown。

> /root/MineSim-Dynamic/AI_HANDOFF.md  
> /root/MineSim-Dynamic/PROJECT_STATUS.md

## **3.2 AI_HANDOFF.md 建议只保留 10 类信息**

- 当前分支 / commit / tag。

- 当前目标：例如“正在实现 Pure MCTS Phase 3 TransitionModel”。

- 已完成里程碑与对应 commit。

- 当前真实仿真链和本阶段禁止修改的模块。

- 最近修改的文件绝对路径。

- 本次运行命令。

- 当前错误/异常，完整 traceback 保存在哪里。

- 已经验证通过的测试。

- 已知未解决问题。

- 下一步只允许做的一件事。

## **3.3 PROJECT_STATUS.md 与 AI_HANDOFF.md 的区别**

| **文件**          | **更新频率**                 | **内容**                                           |
|-------------------|------------------------------|----------------------------------------------------|
| AI_HANDOFF.md     | 几乎每次 AI 会话/每个 commit | 短、实时、面向“下一个 AI 立即接手”                 |
| PROJECT_STATUS.md | 每个阶段/每周                | 面向人和论文项目管理：里程碑、风险、实验状态、待办 |

# **4. 第二优先级：建立实验台账 EXPERIMENT_LOG 与结果目录规范**

MCTS/Neural-MCTS 最容易出现的灾难不是代码报错，而是“跑了很多实验，最后不知道哪组结果对应哪段代码和参数”。因此每一次正式运行都必须可追溯。

## **4.1 每次实验必须保存的字段**

| **字段**                  | **说明**                                        |
|---------------------------|-------------------------------------------------|
| experiment_id             | 例如 20260727_mcts_b200_d8_seed0                |
| datetime                  | 开始/结束时间                                   |
| git_commit                | 运行时 HEAD SHA，必须保存                       |
| branch                    | mcts-dev 等                                     |
| method                    | IDM / SPPMM / PureMCTS / ValueMCTS / NeuralMCTS |
| config                    | 实际 YAML 路径与关键 override                   |
| scenario                  | 场景 ID                                         |
| seed                      | MCTS/NumPy/PyTorch seed                         |
| search_budget             | 迭代数或时间预算                                |
| max_depth / gamma / c_uct | 搜索超参数                                      |
| reward_version            | 奖励函数版本/权重                               |
| result_path               | 原始输出绝对路径                                |
| metrics                   | 核心指标                                        |
| status                    | success / failed / aborted                      |
| notes                     | 异常、观察、下一步                              |

## **4.2 推荐结果目录**

> /root/autodl-tmp/mcts_results/  
> ├── experiments.csv  
> ├── pure_mcts/  
> │ └── \<experiment_id\>/  
> │ ├── config_snapshot.yaml  
> │ ├── git_commit.txt  
> │ ├── metrics.json  
> │ ├── planner_diagnostics.csv  
> │ ├── console.log  
> │ └── outputs/  
> └── neural_mcts/  
> └── \<experiment_id\>/...

| **原则：**“一个实验一个目录”；目录内必须能回答：用的哪段代码、哪份配置、哪个 seed、跑的什么场景、结果是什么。 |
|---------------------------------------------------------------------------------------------------------------|

# **5. 第三优先级：建立测试体系与最小回归场景**

普通 AI 写研究代码时，最危险的是“修一个 bug，引入另一个不明显的 bug”。测试是你和 AI 之间的客观裁判。

## **5.1 推荐测试层级**

| **层级**         | **对象**                   | **主要防什么**                            |
|------------------|----------------------------|-------------------------------------------|
| T0 静态          | py_compile / import        | 语法、循环 import、模块路径               |
| T1 纯函数        | Transition / Reward / TTC  | 固定输入得到固定输出                      |
| T2 MCTS 内核     | Node / UCB / backup / seed | 访问次数、价值回传、可复现                |
| T3 Planner 接口  | MCTSPlanner shell          | 返回 AbstractTrajectory，类型和时间戳合法 |
| T4 单场景闭环    | dapai 或 jiangtong         | 能完整跑完、不崩溃                        |
| T5 Baseline 回归 | IDM Mode 1                 | 新增 MCTS 后 IDM 仍能正常运行             |
| T6 指标回归      | 固定输出→固定 metrics      | 评价代码不随意漂移                        |
| T7 性能          | 固定 budget 的 latency     | 防止算法改动导致计算时间爆炸              |

## **5.2 最小回归场景必须固定**

当前明确存在两个场景：dapai_intersection_1_3_4 与 jiangtong_intersection_9_3_2。建议其中一个固定为“快速 smoke test”，另一个固定为“交叉验证 smoke test”。每次修改 Planner 内核后，不要随机换场景。

# **6. 第四优先级：建立 Metrics 评价脚本和统一结果表**

评价指标必须由统一脚本计算，不要让每个 AI 或每次实验临时“算一下”。否则同名指标定义会变化，论文结果不可比较。

| **指标**             | **定义**                     | **单位/方向**          | **类别**   |
|----------------------|------------------------------|------------------------|------------|
| collision            | 是否发生碰撞                 | 0/1 或 collision count | 安全       |
| min_ttc              | 整个 episode 最小 TTC        | s；越大越好            | 安全       |
| unsafe_ttc_ratio     | TTC 小于阈值的时间占比       | %                      | 安全       |
| success              | 是否到达目标                 | 0/1                    | 任务       |
| completion_time      | 完成耗时                     | s                      | 效率       |
| route_progress       | 最终路线进度                 | m 或比例               | 效率       |
| mean_speed           | 平均速度                     | m/s                    | 效率       |
| jerk_rms             | 纵向 jerk RMS                | m/s^3                  | 舒适       |
| action_switch_count  | 高层动作切换次数             | 次                     | 稳定性     |
| planner_latency_mean | Planner 平均耗时             | ms                     | 计算       |
| planner_latency_p95  | Planner P95 耗时             | ms                     | 计算       |
| planner_latency_max  | 最坏耗时                     | ms                     | 计算       |
| transition_error     | 树内模型 vs 真实下一状态误差 | 状态量误差             | 模型可信度 |

| **必须固定定义：**例如 TTC 到底按车身距离还是中心距离、collision 如何判定、completion_time 起止点是什么，都要在 metrics README 中写死。AI 不能每次凭感觉改。 |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------|

# **7. 第五优先级：建立配置、随机种子与可复现性规范**

## **7.1 MCTS 随机性必须显式管理**

- 所有 rollout 随机动作必须使用统一 RNG，不要在函数内部到处 new random.Random()。

- 固定一个 master seed，再从中派生 NumPy/MCTS/PyTorch seed。

- 正式对比至少多个 seeds；一个 seed 只能用于 debug，不能用于论文结论。

- 每个结果目录保存 seed。

## **7.2 配置快照比“记得参数”可靠**

Hydra 支持 override，因此仅保存仓库里的 yaml 不够。每次实验目录必须保存“最终 resolved config”。否则以后只知道 mcts_planner.yaml，却不知道运行时命令行改了什么。

## **7.3 版本编号建议**

> reward_version: r1  
> transition_version: t1  
> state_version: s1  
> metrics_version: m1  
> model_version: v0 (Pure MCTS) / v1 (Value) / v2 (Policy+Value)

这些不是为了形式，而是为了在结果异常时快速定位“是奖励变了、状态变了还是搜索变了”。

# **8. 数据与训练集治理：Pure MCTS 到 Neural-MCTS 时必须补齐的东西**

神经网络阶段最大风险之一是数据泄漏和伪泛化。Pure MCTS 产生的数据不能只是“随便存成 npy”。必须有 manifest。

## **8.1 每条样本至少记录**

- state 特征与 state_version；

- root visit distribution π；

- value target z 的定义；

- scenario_id、episode_id、step_id；

- 生成该样本的 git_commit；

- MCTS search 参数与 reward_version；

- 是否 collision / terminal；

- 生成时间和 seed。

## **8.2 训练/验证/测试必须按 scenario 或独立 episode 分组**

不要把同一条 episode 的相邻 frame 随机拆到 train 和 val。相邻状态高度相关，会让验证结果虚高。更严格的是按独立 scenario/参数变体分组。

## **8.3 当前场景数量是研究限制**

| **客观限制：**当前盘点明确看到两个场景。足够做原型和调试，但不足以支持强泛化结论。正式论文阶段应增加更多场景、交通密度、初始速度/间距、agent 行为参数或独立场景集。 |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# **9. 模型与 checkpoint 治理：避免“模型能跑但不知道怎么来的”**

| **必须和 checkpoint 一起保存** | **原因**                               |
|--------------------------------|----------------------------------------|
| model_state                    | PyTorch state_dict                     |
| model_config                   | 输入维度、隐藏层、输出动作数、激活函数 |
| normalization                  | state mean/std 或 scaler               |
| dataset_manifest               | 训练数据版本/样本数/划分               |
| training_config                | batch/lr/epoch/optimizer/weight_decay  |
| seed                           | 训练随机种子                           |
| git_commit                     | 训练代码版本                           |
| best_metric                    | 选择该 checkpoint 的验证指标           |
| date                           | 训练时间                               |

只保存 model.pt 是不够的。未来 AI 即使能加载权重，也无法知道输入是否标准化、动作顺序是什么、这个模型对应哪批 MCTS 数据。

# **10. Git 与代码治理：分支、commit、tag、回滚和 AI 改码纪律**

## **10.1 推荐分支结构**

> main 官方/上游基线  
> autodl-idm-baseline 已冻结复现基线  
> mcts-dev Pure MCTS 主开发  
> neural-mcts-dev Neural-MCTS 阶段（Pure MCTS 稳定后再建）

## **10.2 commit 应该按“可解释里程碑”而不是按天**

- Add MCTSPlanner shell and Hydra config

- Add MCTS state and action definitions

- Add deterministic transition and reward tests

- Add UCT search core

- Integrate MCTS with MineSim trajectory adapter

- Add evaluation metrics and benchmark scripts

- Add MCTS dataset logger

- Add value network evaluator

- Add policy-value PUCT search

## **10.3 AI 改旧文件前后必须做什么**

> git status  
> git diff -- \<target_file\>  
> \# 修改后  
> python -m py_compile \<target_file\>  
> git diff --check  
> git diff -- \<target_file\>

| **红线：**不要让普通 AI 一次修改十几个核心文件后再测试。一次只改一个明确模块；跑通后 commit。 |
|-----------------------------------------------------------------------------------------------|

# **11. 云端与环境治理：磁盘、Conda、GPU、依赖和备份**

## **11.1 当前已知状态**

| **对象**        | **状态**                                     | **建议**                                      |
|-----------------|----------------------------------------------|-----------------------------------------------|
| 系统盘          | 30G；当前约15G已用、16G可用                  | Pure MCTS 足够；不要把训练数据放系统盘        |
| 正式环境        | /root/miniconda3/envs/minesim；Python 3.9.25 | 当前 MineSim 运行环境                         |
| mappolce        | 约6.9G                                       | 旧 RL 环境；当前 MineSim 不使用，但未确认可删 |
| 数据盘          | /root/autodl-tmp                             | 后续 MCTS 数据/结果/checkpoint 优先放这里     |
| baseline backup | /root/autodl-tmp/minesim_idm_baseline_backup | 必须保留                                      |

## **11.2 PyTorch 不要提前乱装**

Pure MCTS 阶段不需要 torch。进入 Value Network 阶段再在 minesim 环境中根据 GPU 驱动/CUDA 兼容性安装。不要因为 base 或 mappolce 已有 torch，就让正式项目跨环境 import。

## **11.3 每周/每个里程碑的备份对象**

- Git commit/tag

- resolved config

- EXPERIMENT_LOG

- metrics CSV/JSON

- 重要训练数据 manifest

- 最佳 checkpoint + metadata

- 关键论文图表原始数据

# **12. Pure MCTS 最可能遇到的算法问题**

| **现象**                      | **常见原因**                                                                  | **第一处理**                                                          |
|-------------------------------|-------------------------------------------------------------------------------|-----------------------------------------------------------------------|
| MCTS 总选 KEEP/同一个动作     | reward 尺度不平衡；rollout 太短；transition 对动作响应太弱；终止奖励太大/太小 | 打印 root 每个动作 N/Q/先验，分别关闭 reward 项做消融                 |
| 动作频繁 ACCEL↔BRAKE 抖动     | 没有 jerk/action switch 惩罚；每步只看短期收益                                | 增加 action_change penalty 或最小保持时间；先记录而非盲目加大惩罚     |
| 搜索看起来随机，seed 也不稳定 | RNG 没统一；集合/dict 遍历顺序影响 expansion；tie-break 非确定                | 统一 RNG，明确 action order，固定 tie-break                           |
| 更多 iterations 反而更差      | reward/transition 本身有偏差；rollout policy 有系统性错误                     | 做 budget sweep，同时检查 transition error，而不是只增预算            |
| collision 仍然多              | 安全只依赖软 reward，碰撞代价传播太迟                                         | 加入 hard action pruning/terminal；验证 TTC 与 collision 检测         |
| MCTS 规划很保守               | collision/TTC penalty 过强；速度收益太弱；模型认为 lead 永远不会走            | 检查 reward 归一化和 lead prediction                                  |
| MCTS 太慢                     | 深度×分支×迭代数过大；节点存重对象；重复几何计算                              | profile selection/transition/reward；节点只存轻量 state；缓存可复用量 |
| Q 值爆炸/大小随深度变化       | reward 未归一化；backup discount 错；重复累计 terminal reward                 | 单元测试 1/2/3 步手算 return                                          |
| root 最终动作选错             | 错误地用最高 UCB 选最终动作                                                   | 最终用最大 visit 或最大 mean Q，UCB 仅用于树内 selection              |
| 模型 mismatch                 | 树内纵向模型与真实 iLQR+KBM/agent 回放差异大                                  | 记录 one-step transition error；必要时逐步增强 transition             |

# **13. MineSim 集成最可能遇到的工程问题**

| **问题**                    | **常见原因**                                                   | **处理原则**                                                                 |
|-----------------------------|----------------------------------------------------------------|------------------------------------------------------------------------------|
| Hydra 找不到 MCTSPlanner    | \_target\_ 路径错、包缺 \_\_init\_\_.py、运行目录/模块路径错   | 先 python import，再 Hydra instantiate                                       |
| Planner 返回类型错误        | 返回 list/ndarray 而不是 AbstractTrajectory                    | 对照 IDMPlanner 真实返回值和 AbstractPlanner 接口                            |
| 轨迹时间戳不连续            | trajectory adapter 构造 TimePoint 错                           | 对比 IDM 的 17 states 和 sampling interval                                   |
| Controller 报姿态/速度异常  | 轨迹不满足 iLQR 预期；速度跳变过大                             | 先让 adapter 输出简单平滑轨迹，再逐步增加动作效果                            |
| 车辆在地图外/route 投影失败 | route_s/geometry 使用错误坐标系                                | 复用现有 route path/project API，不自己发明坐标转换                          |
| 其他 agents 类型不对        | Mode/observation 配置被误改                                    | MCTS 第一阶段坚持 replay_policy_agents_box_track                             |
| IDM baseline 突然也跑不动   | AI 修改了共享代码、配置或环境                                  | 切 baseline 分支做回归；git diff 定位共享改动                                |
| 两个 MineSim 仓库混淆       | /root/MineSim-Dynamic 与 /root/autodl-tmp/MineSim-Dynamic 同名 | 每次 pwd + git rev-parse --show-toplevel；正式开发只用 /root/MineSim-Dynamic |
| 路径在某个脚本里仍硬编码    | 旧 /home/czf 或 /root/inputs 等残留                            | grep 全仓库，但先判断当前 Mode 是否实际走到该路径                            |

# **14. Neural-MCTS 最可能遇到的训练和搜索问题**

| **现象**                 | **常见原因**                                                | **优先检查**                                                       |
|--------------------------|-------------------------------------------------------------|--------------------------------------------------------------------|
| 训练 loss 降但搜索不变好 | value target 与搜索 return 定义不一致；网络误差在关键状态大 | 用 offline MAE/RMSE + 在线 search performance 双重验证             |
| Value 输出范围异常       | return 未归一化/激活不匹配                                  | 先统计 target 分布；决定线性输出或 tanh                            |
| Policy 只预测一个动作    | visit-count target 太尖锐；数据分布偏；动作不平衡           | 看 policy entropy/class frequency；调整温度/采样，而非先改网络深度 |
| 训练集很好、验证差       | 同 episode 泄漏；场景太少                                   | 按 scenario/episode 分组划分                                       |
| PUCT 被 prior 完全控制   | c_puct 太大或 Q/P 尺度不匹配                                | 记录 PUCT 分解项，做 c_puct sweep                                  |
| 神经网络让延迟更高       | 每个节点都重复 inference；未 batch；CPU/GPU 搬运过多        | 只在 expansion/leaf evaluation 调用；先小 MLP；测 P95 latency      |
| GPU 可用但运行更慢       | 模型太小，kernel launch/数据搬运成本大                      | 比较 CPU inference；不要默认 GPU 一定更快                          |
| checkpoint 无法复现      | 缺 normalization/model config/action order                  | 按第9节保存 metadata                                               |
| 新网络越迭代越差         | self-generated data distribution collapse                   | 保留固定 validation/benchmark，采用数据质量门控                    |

# **15. 评价实验最可能遇到的方法学问题**

- 只跑一个 seed：随机 MCTS 的结果可能只是偶然。

- 不同方法使用不同场景、不同 controller 或不同 agent policy：比较不公平。

- 调参用测试集：造成隐性过拟合。

- 只报告平均值：掩盖碰撞极端事件和 P95 latency。

- 只看 reward：reward 是算法内部代理目标，不等于真实安全/效率指标。

- 把同场景的相邻 frame 拆进训练和测试：神经网络泛化结论虚高。

- MCTS budget 不匹配：Neural-MCTS 用 200 次搜索、Pure MCTS 用 50 次，不可直接称“网络更好”。

- 运行失败样本被删除：会产生 survivorship bias。失败也必须计入 success/collision 统计。

- 多个超参数一起改：无法知道改进来自哪里。

| **论文级原则：**最终结论必须来自预先定义的 benchmark protocol，而不是挑选最漂亮的一次仿真 GIF。 |
|-------------------------------------------------------------------------------------------------|

# **16. AI 协作最可能遇到的问题：普通 AI 会怎么把你带偏**

| **AI 常见错误**        | **为什么会发生**                                   | **你的约束**                                   |
|------------------------|----------------------------------------------------|------------------------------------------------|
| 编造 MineSim API       | 模型没有真实仓库上下文，会按常见自动驾驶框架猜接口 | 要求“只根据我给的源码；未知就写 UNKNOWN”       |
| 一次改太多文件         | AI 倾向给完整大方案                                | 拆任务；一次一个文件/一个接口                  |
| 把示例代码当生产代码   | 示例常忽略 edge case、类型、时间戳                 | 先单测，再闭环；要求解释假设                   |
| 为了消除报错而破坏架构 | 例如改 AbstractPlanner、Controller 来适配错误 MCTS | 共享核心模块默认禁止修改                       |
| 误删文件/环境          | 普通 AI 看不到云端全貌                             | 删除前必须 du/ls/git status/备份；不碰 .ssh    |
| 把旧副本当正式仓库     | 同名 MineSim-Dynamic                               | 每次会话明确正式路径 /root/MineSim-Dynamic     |
| 看一段 traceback 就猜  | 真正错误可能在上游输入/配置                        | 给完整 traceback + command + git diff + config |
| 自动给“最优参数”       | MCTS/reward 参数没有通用最优                       | AI 只能给起点和 sweep 范围，最终由实验决定     |
| 生成不可复现训练代码   | 遗漏 seed、数据划分、checkpoint metadata           | 用固定模板强制包含这些字段                     |

# **17. 风险矩阵：严重程度、触发信号、第一检查项与处理办法**

| **ID** | **风险**                        | **严重度** | **概率** | **触发信号**                        | **第一检查**                    | **处理**                         |
|--------|---------------------------------|------------|----------|-------------------------------------|---------------------------------|----------------------------------|
| R1     | 误改 baseline/shared controller | 高         | 中       | IDM baseline 也异常                 | git diff + baseline branch 回归 | 立刻停止 MCTS 修改，恢复共享文件 |
| R2     | 树内 transition 严重失真        | 高         | 高       | MCTS Q 很好但真实闭环差             | one-step transition error       | 先修模型/缩短 horizon，不加网络  |
| R3     | reward hacking                  | 高         | 高       | reward 高但 TTC/jerk/成功率差       | 分项 reward + 外部 metrics      | 重定义/归一化 reward             |
| R4     | 搜索超时                        | 高         | 高       | P95 planner latency 超 frame budget | planner report/profile          | 降低 budget/depth/节点成本       |
| R5     | 随机性导致不可复现              | 中         | 高       | 同 seed 结果仍漂                    | 统一 RNG/排序/tie-break         | 先修 determinism                 |
| R6     | 训练/验证泄漏                   | 高         | 中       | val 极好，换场景崩                  | dataset manifest/split          | 按 scenario/episode 重划分       |
| R7     | 只有两个场景导致过拟合          | 高         | 高       | 方法只在已知场景好                  | 扩场景/参数变体                 | 限制论文结论强度                 |
| R8     | 环境被污染                      | 中         | 中       | import/version 突然变化             | pip freeze/conda diff           | 新环境或从 backup 重建           |
| R9     | 磁盘满                          | 中         | 中       | 写文件失败/日志中断                 | df -h + du                      | 大数据移 autodl-tmp，清缓存      |
| R10    | checkpoint 不可追溯             | 高         | 中       | 不知道模型对应哪批数据              | metadata/git commit             | 禁止无 metadata 的模型进正式结果 |
| R11    | 评价定义漂移                    | 高         | 中       | 同输出不同脚本指标不同              | metrics version + tests         | 冻结定义并版本化                 |
| R12    | AI 编造/幻觉                    | 高         | 高       | 出现仓库不存在类/方法               | 源码 grep/import                | 要求证据路径和行号               |

# **18. 一次实验从开始到结束的标准 SOP**

1.  确认路径：pwd 必须是 /root/MineSim-Dynamic，conda env 必须是 minesim。

2.  记录版本：git status 必须清晰；保存 HEAD commit。

3.  选择方法/场景/seed；不要临时混合多种修改。

4.  复制 resolved config 到 experiment 目录。

5.  运行 T0-T5 测试；baseline 回归未过则禁止正式实验。

6.  运行实验，同时保存 stdout/stderr 到 console.log。

7.  保存 planner_diagnostics：每步 action、N、Q、runtime、reward components。

8.  运行统一 metrics 脚本，生成 metrics.json/csv。

9.  把 experiment_id、commit、配置、结果写入 EXPERIMENT_LOG。

10. 检查异常：collision、失败、latency 极值不能删掉。

11. 结果达到里程碑后 git commit；否则在 notes 写明失败原因。

12. 更新 AI_HANDOFF.md：当前状态、下一步、最新错误/结论。

## **18.1 推荐一键 preflight 命令**

> cd /root/MineSim-Dynamic  
> echo "PWD=\$(pwd)"  
> echo "ENV=\$CONDA_DEFAULT_ENV"  
> python --version  
> git branch --show-current  
> git rev-parse HEAD  
> git status --short  
> df -h /

# **19. 出问题时的故障分层决策树**

> 程序启动失败？  
> ├─ 是 → Import/Hydra/路径/环境层（先别看 MCTS 数学）  
> └─ 否  
> ├─ Planner 接口报错？  
> │ ├─ 是 → trajectory/type/timepoint/interface 层  
> │ └─ 否  
> │ ├─ 仿真能跑但行为明显错误？  
> │ │ ├─ root N/Q 是否合理？ 否 → MCTS 内核/reward  
> │ │ ├─ tree predicted next state 是否接近真实？ 否 → transition model  
> │ │ └─ 高层动作合理但车辆轨迹异常？ → trajectory adapter/controller 接口  
> │ └─ 行为合理但论文指标不提升？  
> │ ├─ 统计 seed 是否足够？  
> │ ├─ benchmark 是否公平？  
> │ ├─ reward 与 metrics 是否一致？  
> │ └─ 场景是否过少/过拟合？

| **故障定位原则：**先判断“哪一层坏了”，再让 AI 看那一层的最小文件。不要把整个仓库和 500 行 traceback 一股脑让 AI 猜。 |
|----------------------------------------------------------------------------------------------------------------------|

# **20. 给任何 AI 的“项目交接包”应包含什么**

以后开启一个完全新的 AI 对话，不要只上传四份 Word。最有效的是“四份稳定文档 + 一组实时文件”。

| **类别** | **交给 AI 的内容**                          | **作用**                               |
|----------|---------------------------------------------|----------------------------------------|
| 稳定背景 | 四份 Word                                   | 项目地图、算法路线、云端操作、风险治理 |
| 实时状态 | AI_HANDOFF.md                               | 今天到底做到哪里                       |
| 代码事实 | 目标模块源码 + AbstractPlanner/相关接口源码 | 防止 AI 编造 API                       |
| 配置事实 | 本次运行 YAML / resolved config             | 防止 AI 猜参数                         |
| 版本事实 | git status + git log -3 + git diff          | 防止上下文过期                         |
| 运行事实 | 完整 command                                | 同一报错必须知道怎么触发               |
| 错误事实 | 完整 traceback/console.log                  | 不能只截最后一行                       |
| 结果事实 | metrics.json / diagnostics.csv              | 分析行为而非凭 GIF                     |

## **20.1 新 AI 开场模板**

> 你现在接手 MineSim-Dynamic MCTS 项目。  
> 正式仓库只能是 /root/MineSim-Dynamic。  
> 请先阅读我给你的 4 份项目文档和 AI_HANDOFF.md。  
> 然后只根据我提供的真实源码/配置回答，不允许编造类、方法、路径。  
> 当前任务只处理 AI_HANDOFF.md 中“下一步”一项。  
> 先输出：  
> 1. 你确认的当前 Git/算法阶段；  
> 2. 你还缺哪些真实文件；  
> 3. 你准备修改哪些文件，为什么；  
> 在我提供文件前不要直接写完整代码。

# **21. 论文阶段还必须补齐哪些证据**

| **证据**   | **必须记录什么**                                           | **论文位置** |
|------------|------------------------------------------------------------|--------------|
| 算法定义   | State/Action/Transition/Reward/UCB or PUCT 的正式数学定义  | 方法章节     |
| 系统架构图 | MineSim→Planner→trajectory→iLQR→KBM；Pure/Neural MCTS 位置 | 方法章节     |
| 参数表     | IDM/SPPMM/MCTS/Network 参数及选择原则                      | 实验设置     |
| 场景表     | 场景、交通强度、初始条件、数量、划分                       | 实验设置     |
| 评价定义   | collision/TTC/progress/jerk/latency 的精确定义             | 评价指标     |
| 重复实验   | 多 seed 均值、标准差/置信区间                              | 统计可信度   |
| 消融实验   | reward、budget、depth、Value/Policy 网络作用               | 证明贡献     |
| 计算成本   | mean/P95/max planner latency、硬件                         | 实时性       |
| 失败案例   | MCTS/Neural-MCTS 失败场景与原因                            | 客观性       |
| 复现信息   | Git commit、环境、配置、数据 manifest                      | 可复现性     |

# **22. 未来 12 个里程碑与每一步的验收条件**

| **里程碑** | **内容**                                    | **通过条件**                                    |
|------------|---------------------------------------------|-------------------------------------------------|
| M0         | 建立 mcts-dev + AI_HANDOFF + tests skeleton | IDM baseline 回归正常                           |
| M1         | MCTSPlanner shell                           | Mode 能加载 MCTSPlanner 并完整跑一个场景        |
| M2         | State/Action/StateBuilder                   | 纯函数单测全过；状态日志合理                    |
| M3         | Transition/Reward                           | 手算 case + edge case 单测通过                  |
| M4         | Pure UCT core                               | 固定 toy MDP 上能选出预期动作；seed 可复现      |
| M5         | MineSim closed-loop Pure MCTS               | 两个当前场景至少完整跑通                        |
| M6         | Metrics + diagnostics                       | IDM/SPPMM/MCTS 能用统一脚本评价                 |
| M7         | Pure MCTS parameter study                   | budget/depth/c_uct/gamma 有系统实验表           |
| M8         | Dataset logger                              | 能产生带 manifest 的 (s, pi, z)                 |
| M9         | Value Network                               | offline val 合格 + 在线搜索至少不劣于 Pure MCTS |
| M10        | Policy+Value + PUCT                         | 相同或更低搜索预算下有可验证收益                |
| M11        | Expanded benchmark + paper package          | 多场景/多seed/消融/统计/图表全部可追溯          |

# **附录 A. 推荐新增的项目文件模板**

## **A.1 AI_HANDOFF.md 模板**

> \# AI HANDOFF  
>   
> \## Repository  
> - Path: /root/MineSim-Dynamic  
> - Branch: \<branch\>  
> - Commit: \<sha\>  
> - Conda: minesim  
>   
> \## Current Goal  
> - \<只写一个当前目标\>  
>   
> \## Completed  
> - \<milestone + commit\>  
>   
> \## Files Changed Recently  
> - /root/MineSim-Dynamic/...  
>   
> \## Tests Passed  
> - \<commands + result\>  
>   
> \## Current Problem  
> - \<error or NONE\>  
> - Log: /root/autodl-tmp/...  
>   
> \## Known Constraints  
> - Do not modify controller / KBM / baseline config unless explicitly approved.  
>   
> \## Next Single Step  
> - \<exactly one task\>

## **A.2 EXPERIMENT_LOG.csv 最小表头**

> experiment_id,datetime,git_commit,branch,method,scenario,seed,config_path,search_budget,max_depth,gamma,c_uct,reward_version,result_path,status,success,collision,min_ttc,completion_time,planner_latency_mean_ms,planner_latency_p95_ms,notes

## **A.3 checkpoint metadata.yaml 模板**

> model_version: v1  
> git_commit: \<sha\>  
> model:  
> type: value_mlp  
> input_dim: \<n\>  
> hidden_dims: \[64, 64\]  
> state_version: s1  
> action_order: \[BRAKE, DECEL, KEEP, ACCEL\]  
> dataset_manifest: /root/autodl-tmp/mcts_data/.../manifest.json  
> normalization: /root/autodl-tmp/mcts_data/.../normalization.json  
> training:  
> seed: 0  
> batch_size: 256  
> learning_rate: 0.001  
> validation:  
> metric: mae  
> value: \<value\>

## **A.4 每次实验的 README 模板**

> \# Experiment \<ID\>  
>   
> Purpose: ...  
> Git commit: ...  
> Method: ...  
> Scenario: ...  
> Seed: ...  
> Config snapshot: ./config_snapshot.yaml  
> Command: ...  
> Result: ...  
> Metrics: ./metrics.json  
> Known anomaly: ...  
> Conclusion: ...  
> Next action: ...

# **附录 B. AI 接手时的强制核验清单**

- □ AI 是否明确知道正式仓库是 /root/MineSim-Dynamic，而不是 autodl-tmp 副本？

- □ AI 是否知道当前 branch/commit，而不是依据旧 Word 假设？

- □ AI 是否看过要实现接口的真实源码？

- □ AI 是否明确本阶段允许修改和禁止修改的文件？

- □ AI 是否给出最小改动而非大重构？

- □ AI 是否给出测试命令和预期结果？

- □ AI 是否解释代码中的假设、单位、类型和边界条件？

- □ AI 是否把研究超参数当“建议起点”，而不是宣称最优？

- □ AI 是否保留 seed/diagnostics/logging？

- □ AI 是否在报错时要求完整 traceback、command、diff、config？

- □ 涉及删除时是否先备份/确认归属？

- □ 涉及 neural 时是否核实 torch/CUDA，而不是跨 conda 环境借包？

# **附录 C. 当前项目的已知事实与当前限制**

| **事实**              | **当前值**                                                    |
|-----------------------|---------------------------------------------------------------|
| 正式仓库              | /root/MineSim-Dynamic                                         |
| 当前 Git              | autodl-idm-baseline @ 2521aa4；tag=idm-replay-autodl-baseline |
| 工作树                | 当前盘点时 clean                                              |
| 正式 Conda            | minesim；Python 3.9.25                                        |
| 当前 baseline Planner | IDMPlanner                                                    |
| 其他 agents           | replay_policy_agents_box_track                                |
| Ego execution         | TwoStageController → iLQR →普通 Kinematic Bicycle Model       |
| 当前明确场景          | dapai_intersection_1_3_4、jiangtong_intersection_9_3_2        |
| 系统盘                | 约49%使用，16G可用                                            |
| 历史 IDM outputs      | 已归档到 /root/autodl-tmp/minesim_idm_baseline_backup         |
| Pure MCTS 代码        | 尚未正式创建（以本文档快照时点为准）                          |
| Neural MCTS           | 尚未开始；minesim 环境当前不依赖 torch                        |

| **时间性：**以上事实是 2026-07-26 快照。未来 AI 必须以 git status、conda env、AI_HANDOFF.md 和实际文件为最新事实，Word 只作为稳定背景。 |
|-----------------------------------------------------------------------------------------------------------------------------------------|
