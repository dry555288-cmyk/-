审计日期：2026-09-06

审计性质：上传资料、历史源码摘录及论文原文的只读审计。未连接 AutoDL 实时环境，未重训模型，未运行 MCTS，未修改冻结实验。

本次任务：一是检查训练数据、监督标签、训练收敛及验收标准；二是解释当前网络与剪枝实际采用的方法、公式、接入位置和论文来源。

**核心结论：目前可以确认“模型通过了指定离线排序标准”，但不能确认“训练已经充分收敛、数据没有问题”。数据覆盖、恒定特征、标签可靠性和在线分布一致性仍有实质性审计缺口。不能把闭环失败直接归咎于数据，也不能提前排除数据问题。**

文中证据标记：\[文档\] 指项目交接记录；\[源码\] 指实际取得的历史代码摘录；\[计算\] 指基于已给数值的复算；\[推断\] 指有条件的分析；\[HOLD\] 指缺少直接证据；\[论文\] 指原文方法，不自动等于项目已实现。文末 \[D\] 为项目资料，\[S\] 为源码摘录，\[P\] 为论文。

# 1. 先回答你的两个问题

## 1.1 训练数据到底有没有问题？

现在还不能给出“数据完全没有问题”的结论。已经找到一个需要优先排查的特征问题，以及几个明确的证据缺口。

**第一，两个加速度输入没有变化。** 2356-root 训练交接文档第4节及附录A记载，A_accel_mps2、B_accel_mps2 在三个 LOSO 训练折中均为零均值、零标准差，归一化时把标准差改为1。也就是说，按该记录，网络没有从这两个输入列学到“加速度变化如何影响动作优劣”。这是文档已经暴露的特征支持缺失，不是本次凭闭环表现猜测的现象；但原因仍需原始数组、collector 和在线 feature helper 核实。\[文档：D1\]

**第二，2356 个根节点来自3个场景、6段 episode，并不是2356个独立场景。** C11占1780个根节点，约75.55%；C04和C06分别只有274、302个。训练采用场景等权损失，缓解了损失权重上的失衡，但没有增加道路、冲突类型、速度组合或困难状态的覆盖。\[文档：D1；计算\]

**第三，尚未拿到足以判定训练收敛的逐轮证据。** 已取得的父训练函数固定跑600轮，只反复更新一个 final_train_loss，并在训练结束后做验证预测。该函数中没有逐epoch的训练/验证历史、早停或最优epoch选择。这意味着“执行完成”和“离线通过”有证据，“优化已稳定、没有过拟合或欠拟合”仍是HOLD。\[源码：S1、S2\]

**第四，监督标签的搜索精度未得到独立证明。** 标签是有限预算 MCTS 的动作Q估计，不是矿卡真实最优动作的权威答案。现有资料说明了采集合同，但没有提供2356个根节点对应的完整动作访问数、回报方差、预算稳定性和关键状态标签一致性。本次不能确认标签噪声是否足以影响排序与剪枝。\[文档：D2；HOLD\]

因此，这次检查的结论是：**发现值得优先追查的数据/特征风险，且训练收敛证据不完整；但尚未证明原始训练文件损坏、标签普遍错误，或数据是闭环失败的唯一根因。**

## 1.2 有没有达到原来的标准？

有，但必须说清“哪一种标准”。2356-root 版本通过了预注册的三场景离线排序标准；后续全开发集模型也通过了C01独立离线评价。与此同时，神经引导闭环没有超过Pure MCTS，K13也未达到冻结的可复现端到端加速目标。这些结论并不矛盾。\[D1、D3、D4、D6\]

| **判断对象**              | **已有证据**                                | **本次结论**         |
|---------------------------|---------------------------------------------|----------------------|
| 训练是否真正执行完成      | 9次LOSO训练产物；RC=0；stderr为空           | 文档记录通过         |
| 三场景离线排序是否达标    | C04/C11/C06的三模型中位regret均低于各自基线 | 原定开发标准通过     |
| C01独立离线排序是否达标   | 中位regret约0.10584，基线约0.29520          | 原定独立评价通过     |
| 600轮是否足以收敛         | 未取得完整逐轮训练/验证曲线                 | HOLD                 |
| 数据是否覆盖在线困难状态  | 仅3场景6段训练episode；缺逐状态覆盖审计     | HOLD，不足以宣称充分 |
| 教师Q标签是否稳定可信     | 缺完整访问数、方差和预算稳定性证据          | HOLD                 |
| 神经引导是否优于Pure MCTS | Pure B8稳定，置信排序需要B32                | 当前协议下未达到     |
| K13是否稳定端到端加速     | 三组matched运行方向不一致                   | 冻结负结论           |

## 1.3 对此前判断的修正

“网络学到了一些排序信息”有离线指标支持；“问题主要不在数据，而在接入架构”则缺少排除数据因素的充分证据。更严谨的定位应是：**数据/标签、优化过程、训练—在线一致性、搜索接入方式，共同构成待审计的四个环节。** 本报告不通过重新解释指标来改变已有负结果。

# 2. 本次实际检查了什么，尚未检查什么

## 2.1 已完成的只读检查

已展开AI接手文档相关ZIP，定向阅读2356-root训练交接、C06采集合同、C01独立评价与最终模型交接、置信排序和K13交接。已读取历史训练源码摘录中的数据构建、归一化、成对排序损失、训练循环与模型保存逻辑。已核对Paper1/Paper2原文与项目兼容性决策，并复算样本数、场景占比及三组K13根层展开量。\[D1—D9、S1—S2、P1—P2\]

本次取得的训练交接ZIP主要提供文档。**截至本报告生成，尚未取得可在本地逐元素复核的2356-root原始NPZ、对应原始collector JSONL、最新三份实际checkpoint，以及完整训练日志。** 文档列出的云端路径和SHA不是本次已经读取了这些云端文件的证明。

## 2.2 本次不能直接宣布通过的检查

没有原数组，就不能复核NaN/Inf、重复样本、动作列错位、跨集合重叠和Q标签分布。没有实际trainer与checkpoint，就不能重新绑定最新模型的全部超参数、归一化统计和实际载入行为。没有逐轮日志，就不能判断loss平台期、验证退化、最佳epoch及优化停止是否充分。

因此，本报告属于**证据审计与方法复原**，不是“原始训练数据逐行验收完成”。文件不存在于当前会话也不等于它已从AutoDL删除；缺失项保持HOLD。

# 3. 先把模型版本和三类数据分开

## 3.1 Value V2与Value V3不是同一种训练目标

部分后期总览把Value V3也写成ROOT_CENTERED_Q；但更具体的2356-root训练记录、8月30日最终交接和父源码一致指向：当前V3模型类型为ActionConditionedValueV3PairwiseRank，目标是ROOT_NORMALIZED_WEIGHTED_PAIRWISE_LOGISTIC。ROOT_CENTERED_Q属于此前Value V2的关键表述。两者共享12→64→64→16架构，不代表损失函数相同。\[D1§3、D2§5、D3§5、S1\]

本报告据此显式区分：**V3是利用MCTS动作Q标签训练的16动作评分/排序网络，不应直接写成“对中心化Q做均方回归的V2”。** 最新checkpoint中具体metadata是否仍有旧字段，需对实际文件只读核验；这里不擅自替换历史文件。\[HOLD\]

## 3.2 三类数据承担不同任务

| **数据**           | **已知规模**                               | **用途**                           | **不能混淆的地方**                                 |
|--------------------|--------------------------------------------|------------------------------------|----------------------------------------------------|
| Value V3开发训练集 | 2356 roots；3场景、6 episodes；37696动作行 | LOSO开发评价，之后全开发集固定训练 | 37696动作行不是37696个独立状态                     |
| C01独立离线评价集  | 交接记录为151 roots；三个固定模型分别评价  | 检查未参与训练的C01排序表现        | 不是训练集，也不等同闭环证明                       |
| K13开发校准集      | 453 raw记录，去重后151 roots               | 三模型评分，选择K与剪枝阈值        | 453 raw及453 model-root pairs都不是453个独立根状态 |

来源：\[D1、D3、D5、D6\]。C01与K13两处都出现151这个数字，不能仅凭计数判定是同一数据，也不能仅凭runtime seed不同判定彼此状态独立；需要root snapshot/hash交叉核对。

## 3.3 9个LOSO模型与3个最终模型不同

LOSO是3个留出场景，每个场景配3个模型随机种子，共9次训练。它不是9个彼此独立的验证场景。后续部署候选则在全部2356个冻结development roots上，按固定协议训练3个最终模型。在线使用的是这些最终模型，而不是看过LOSO结果后随意挑出的某一折checkpoint。\[D1§1、D3§5、D5\]

最终模型种子为20260824、20260825、20260826。K13三组已完成的matched runtime使用model seed 20260824；不能把三模型校准结果写成每次在线都执行三个模型集成推理。\[D4、D6、D7\]

# 4. 2356-root训练集的具体审计

## 4.1 样本与episode组成

| **场景** | **Episode UID**    | **根节点数** |
|----------|--------------------|--------------|
| C04      | C04_FROZEN_EP0     | 126          |
| C04      | C04_SEED5_EP1      | 148          |
| C11      | C11_80M_SEED0_EP0  | 890          |
| C11      | C11_100M_SEED0_EP1 | 890          |
| C06      | C06_FROZEN_EP0     | 146          |
| C06      | C06_SEED1_EP1      | 156          |
| 合计     | 3场景、6段episode  | 2356         |

\[D1§2\]。C11两段都是890步，但起始距离不同；不能只凭相同步数就认定重复，也不能把文档中的“独立episode”理解为已经证明统计独立。需要状态序列哈希及近重复分析。

统计结果：C04为274/2356≈11.63%；C11为1780/2356≈75.55%；C06为302/2356≈12.82%。每个root有16动作列，因此2356×16=37696只是展开记录数。\[计算\]

## 4.2 什么地方已经做对了

数据身份采用(scene, episode_uid, root_step)，能区分C11两段都从step0开始的序列。若只用(scene, root_step)，就可能把两个episode的同一步错误合并；记录已经明确禁止这种flatten行为。\[D1§2\]

LOSO按场景整体留出，而不是随机打散相邻帧。归一化均值、标准差只使用本折训练状态，不使用留出场景。数据扩展记录要求保留旧2052-root前缀。这些都是已有的防泄漏与可追溯措施，但本次还没有原数组逐项复算。\[D1§2—4\]

| **留出场景** | **训练roots** | **验证roots** | **训练/验证episode数** |
|--------------|---------------|---------------|------------------------|
| C04          | 2082          | 274           | 4 / 2                  |
| C11          | 576           | 1780          | 4 / 2                  |
| C06          | 2054          | 302           | 4 / 2                  |

## 4.3 数据覆盖不足为什么是合理怀疑

2356个根节点的数目本身不能说明是否足够。大量相邻状态来自同一次通行或停车过程，信息增量可能很小。网络是否见过让行、停止后再启动、近同时进入冲突区、速度不对称、改变动作后回到安全区等状态，需要按episode和交互阶段统计，不能靠总行数回答。\[推断\]

已有历史证据支持“覆盖确实影响过效果”：最初V3在C04/C06通过、C11失败；后来新增C04 seed5和C06 seed1共304个根节点，把heldout C11时的训练支持从272提高到576，2356版本的C11中位regret下降至0.117458957并通过基线。由于留出的C11完全不参与该折训练，这种改变来自训练侧支持的扩展，而不是把C11验证样本放进训练。\[D1§1、§2；D2§5\]

这是一条支持数据因素重要性的历史线索，不是“当前闭环失败已经由数据不足证实”的因果实验。不同版本的验证集和基线也有变化，不能无条件把所有跨版本数值放在同一条学习曲线上。

## 4.4 场景等权不等于样本质量均衡

父训练代码先计算每个root的损失，再取同场景root平均，最后对训练场景等权平均。因此，虽然C11占全部根节点的75.55%，不能说它必然占总训练损失的75.55%。在包含两个训练场景的LOSO折中，两场景的总损失权重各为一半。\[S1、S2；D1§3\]

但三个问题仍存在。其一，同一场景内部的连续停车或高度相似状态仍按root计数。其二，pooled mean/std按训练root统计，不是先按场景等权统计。其三，等权只能改变已有数据的贡献，不能补出未采集的交互情况。\[推断\]

## 4.5 两个加速度特征是首要核查点

D1附录A的三个fold都给出：第2、3列mean=0；原始std=0；guard后std=1。对训练数据而言，标准化后这两列仍为0。标准差置1只是避免除零，并没有创造加速度信息。

存在两种不同的在线情形，必须分开处理。

**情形A：在线也一直传0。** 那么训练/在线未必不一致，但12维中的两个通道实际不起作用，模型没有利用这部分动态信息。需要确认这是否是有意的state contract，还是collector/feature helper没有取得真实量。

**情形B：在线传入非零加速度。** 那么网络会接收到训练中从未出现的取值支持。以第一层线性映射为例，某输入列恒0时，该列权重从数据损失得到的梯度为0；没有额外约束时，这些权重可能保留初始化影响。在线非零输入便可能引入未经训练支持的输出变化。这个结论是条件性的数学分析，不是已经确认在线发生了该错误。\[S1；推断\]

最小核查对象是原始root状态中的accel字段、NPZ的对应两列、实际online helper提取结果，以及最终checkpoint的feature_mean/std。不能仅根据车辆有加减速，就断言记录中的加速度字段也一定正确；也不能直接把0替换成速度差分后继续用旧模型。

## 4.6 标签不是“绝对真值”

采集合同要求每个root的actionwise\[16\]包含joint_action_id、action、q_value、immediate_reward、child_state和risk_auxiliary。Q是主监督来源；immediate reward用作对照或辅助信息。它们位于每个action item内部，不在root顶层。\[D2§5\]

相关Fleet采集合同记录budget=64、depth=8、tree dt=0.5 s。64是有限搜索预算，不是“标签已收敛”的证明。8×0.5 s名义上对应4 s树深时域；精确回报是否还包含其他终端或rollout贡献，仍以实际collector/transition/reward源码为准。\[D2§3、§8；推断\]

需要检查：各动作被访问几次；Q是累计回报还是平均回报；未访问动作如何编码；终止/碰撞分支的标签与有效性掩码是否一致；不同episode的reward版本是否相同；同状态重复搜索的首选动作是否稳定；关键动作间Q差是否小于估计噪声。现有交接记录不足以逐root回答这些问题。\[HOLD\]

高预算Pure-MCTS得到的argmax也是“在该搜索配置下的教师动作”，不是实际道路最优动作的证明。剪枝校准器的teacher budget=64同样不能直接替代标签精度审计。\[D6\]

## 4.7 失败episode不是天然脏数据，但目标必须匹配

历史C11存在无碰撞但长时间停滞、post-conflict未完成的真实负结果。保留失败episode本身是合理的：它可以提供危险或困难状态。问题在于，这些状态上的监督Q是否真的包含促进最终通行的有效偏好，还是只反映短时避碰与有限视野下的保守响应。\[D2§4；D9\]

不能把“从失败轨迹采集”直接等同于“标签错误”，也不能把“Q都是finite”直接等同于“教师能够指导脱困”。需要按停车持续时间、距冲突点距离、动作Q差和实际终止原因做已有数据诊断，而不是删除所有负样本。

## 4.8 尚未完成的逐样本检查

| **检查项**       | **最小检查内容**                               | **本次状态**                   |
|------------------|------------------------------------------------|--------------------------------|
| 文件与数组完整性 | SHA、keys、shape、dtype、finite、数组长度一致  | 文档有合同；未复算原NPZ        |
| 身份唯一性       | 三元root key是否重复、episode内step是否连续    | HOLD                           |
| 动作映射         | 每root恰有16个唯一动作；A\*4+B与Q列一致        | 文档有合同；实际数组HOLD       |
| 重复和近重复     | 相同X不同Q、跨episode重复、长停车近重复        | HOLD                           |
| 数据泄漏         | train/dev/evaluation/calibration的snapshot交集 | HOLD；不能只看seed编号         |
| 标签支持         | visit_count、Q范围、并列最优、未访问动作       | HOLD                           |
| 动作分布         | 教师argmax直方图、关键让行/制动动作覆盖        | HOLD                           |
| 在线一致性       | feature order、单位、时间对齐、normalization   | 历史绑定存在；本次live复核HOLD |

# 5. “收敛”必须拆成三个问题

## 5.1 数据够不够，不等于优化收不收敛

数据集是固定记录，本身通常不谈“训练收敛”。这里至少有三件事：模型优化是否稳定；教师MCTS的动作Q估计是否随预算/采样稳定；增加独立episode后验证误差是否趋于饱和。它们分别需要训练曲线、标签搜索稳定性证据和样本规模学习曲线，不能相互替代。

本次没有取得后二者的完整证据，也没有取得最新训练的逐epoch曲线。因此不能用某一个regret值同时回答这三个问题。

## 5.2 已取得的训练函数实际做了什么

历史父函数train_fold的关键顺序如下。这是源码摘录的语义缩写，不是要你执行的脚本。\[S1、S2\]

> 按 heldout scene 划分 train / validation
>
> 仅由 X_train 计算 mean / std
>
> 建立模型；Adam(lr=0.001)
>
> 重复 600 个 epoch：
>
> 对全部训练 roots 前向计算 scores
>
> 计算每 root 的 weighted pairwise loss
>
> 每场景取 root mean，再对场景等权 mean
>
> backward；optimizer.step
>
> final_train_loss = 当前 loss 标量
>
> 训练结束后：
>
> model.eval；验证集前向；计算 ranking_metrics
>
> 保存 checkpoint、predictions、final_train_loss

该函数没有在每轮保存训练与验证loss序列。final_train_loss被覆盖600次，不能据此画出600点收敛曲线。函数是在一次optimizer.step前计算loss、step后保存这个标量，因此最后一个标量还对应最终参数更新前的loss；这是小的日志对齐细节，不能单独解释闭环失败。

D1记载2356 derived harness的算法核心保持与父版本一致；D3也记录最终方法的600轮/0.001配置。但本次没有最新all2356训练函数的完整文件，不能据此断言其他模块从未记录TensorBoard或额外日志。正确结论是“已取得函数中没有，最新外部日志未取得”，不是“云端绝对没有曲线”。

## 5.3 判断训练收敛至少要看到什么

首先要有epoch、train loss、validation loss或validation ranking metric的时序。其次要看最后一段曲线是否仍明显下降、验证是否先改善后恶化，以及三个种子是否给出一致趋势。最后还要检查参数/梯度是否finite、是否有梯度爆炸，以及保存的是最后epoch还是预定选择规则对应的epoch。

若需要一个描述性平台指标，可定义相邻两个长度为w的窗口：

> D_loss(t,w) = \|mean(L\[t-w+1:t\]) - mean(L\[t-2w+1:t-w\])\|
>
> / max(\|mean(L\[t-2w+1:t-w\])\|, epsilon)

这是本报告提出的诊断统计，不是原项目已有验收门槛，也不是通用“收敛定理”。w、阈值和持续窗口数必须事先定义；还应结合验证指标，不能看到一个平坦训练loss就宣布泛化可靠。若历史从未保存这些量，只能承认收敛无法追溯，不得从最终checkpoint虚构一条曲线。

## 5.4 什么情况提示欠拟合、过拟合或数据问题

训练和验证都差，且训练仍明显下降，提示优化预算不足或模型尚未拟合；训练持续改善而验证恶化，提示过拟合；训练稳定但同一X对应互相矛盾的动作偏好，提示特征不充分或标签噪声；离线验证好而在线输入超出训练支持，则优先核查分布与接入契约。以上都是诊断方向，不是本次已经观测到的完整曲线事实。

不建议现在直接增加epoch、换网络、重采集或降低剪枝门槛。先读取原有证据，才能判断下一次独立实验究竟要验证哪个假设。

# 6. 已通过的离线标准是什么

## 6.1 2356-root LOSO结果

评价规则是：每个留出场景对3个固定模型种子取normalized regret中位数，再与该场景冻结的immediate baseline比较。regret越低越好。下表按D1保留的精度列出，不是本次重跑结果。

| **留出场景** | **seed24**  | **seed25**  | **seed26**  | **中位regret** | **immediate基线** |
|--------------|-------------|-------------|-------------|----------------|-------------------|
| C04          | 0.181987592 | 0.155618844 | 0.174277542 | 0.174277542    | 0.273804418       |
| C11          | 0.116699341 | 0.120093067 | 0.117458957 | 0.117458957    | 0.181778548       |
| C06          | 0.088145494 | 0.128795213 | 0.122468490 | 0.122468490    | 0.241806713       |

其中seed24/25/26分别指20260824/20260825/20260826。三个场景都满足median \< baseline。三场景中位数再平均约0.138068330，对照约0.232463226；据此，原定primary 3/3和secondary平均比较均通过。\[D1§7；计算\]

## 6.2 C01独立评价结果

三个最终模型在C01上的regret分别为0.09947470394112914、0.15596316637663826、0.10583949665541333。中位数0.10583949665541333低于冻结immediate基线0.2951958615926099，交接记为INDEPENDENT_GENERALIZATION_PASS。\[D3§5\]

这支持“在该独立场景和标签口径上有可利用的排序能力”。它不意味着89.416%的准确率，也不意味着89.416%的安全概率，更不保证Top-13对未来状态有99%以上的保留率。regret、Top-1 accuracy、Top-K retention和碰撞率是不同指标。

## 6.3 normalized regret公式的证据边界

设教师动作值为Q_r(a)，网络选择a_hat，教师最佳动作为a_star，则动作选择的未归一化遗憾可表达为：

> a_hat(r) = argmax_a f_theta(x_r)\[a\]
>
> a_star(r) = argmax_a Q_r(a)
>
> regret(r) = Q_r(a_star) - Q_r(a_hat)

归一化一般写为regret(r)/D_r，其中D_r是冻结评价器规定的尺度。常见尺度是max(Q_r)-min(Q_r)，但**本次未取得项目exact ranking_metrics完整函数体，不能把这个常见尺度及其epsilon、全相等处理、tie-break，冒充已核验的冻结实现。** 项目明确要求调用ranking_metrics(q, pred, immediate)三参数闭包；正式复算应继续使用该原函数，不重写一个“看起来等价”的版本。\[D5；HOLD\]

本报告引用的regret结果来自原交接记录；上述第一组公式解释其动作选择遗憾含义，未用于擅自重算或替换项目现有指标。

# 7. 当前神经网络用什么方法和公式

## 7.1 网络类型：小型全连接动作评分器

当前方法名称可写为：**基于MCTS动作Q监督的场景均衡成对排序网络（Value V3）**。它属于离线监督排序：从已采集状态与教师动作Q中学习动作相对优劣。现有证据不支持把它写成DQN的在线TD学习、PPO策略优化或AlphaZero自对弈训练。\[D1、D3、S1\]

输入x属于R^12，输出f_theta(x)属于R^16。架构为两层64单元隐藏层，使用ReLU，末层输出16个实值分数：

> z = Normalize_frozen(x)
>
> h1 = ReLU(W1 z + b1) W1: 64 x 12
>
> h2 = ReLU(W2 h1 + b2) W2: 64 x 64
>
> f_theta(x) = W3 h2 + b3 W3: 16 x 64
>
> ReLU(u) = max(0, u)

12→64→64→16这一带偏置全连接结构共6032个参数，这是结构计算，不是样本量合格判据。架构的ReLU实现由前代模型记录及V3架构保持合同支持；最新实际state_dict/模型类仍应与冻结SHA绑定。\[D1、D2、S1；计算\]

## 7.2 输入特征与动作索引

| **索引** | **冻结字段**                                          | **说明与边界**                                 |
|----------|-------------------------------------------------------|------------------------------------------------|
| 0、1     | A_speed_mps / B_speed_mps                             | 当前两车速度，m/s                              |
| 2、3     | A_accel_mps2 / B_accel_mps2                           | 当前加速度字段；训练记录为恒零                 |
| 4、5     | A_remaining_to_conflict_m / B_remaining_to_conflict_m | 到冻结冲突定义的剩余距离；不能用未来轨迹反推   |
| 6        | delta_v_abs_mps                                       | 两车速度差绝对值                               |
| 7、8     | delta_heading_abs_rad / delta_heading_over_pi         | 航向差及除以π的表达；两者信息相关              |
| 9、10    | I_Omega_app_AND / I_Omega_int_AND                     | 冻结feature builder中的几何区域AND特征         |
| 11       | alpha3                                                | 冻结交互特征；具体构造需原helper，不凭字段名猜 |

两车各有4个离散纵向动作，联合动作列采用canonical映射：

> i = 4\*a + b, a,b in {0,1,2,3}
>
> a = floor(i/4), b = i mod 4, i in {0,...,15}

历史Pure MCTS动作包括BRAKE=-3.0、DECEL=-1.5、KEEP=0、ACCEL=+1.0 m/s²。但当前provider中整数0/1/2/3与这些动作名称的逐项绑定，仍需真实动作定义核验，不能单凭名字列表顺序填写代码。\[D4§4；D6§5\]

## 7.3 输入归一化

对于训练折的第j列，父代码使用pooled training roots的总体标准差，即NumPy std默认ddof=0：

> mu_j = (1/n_train) \* sum_r x_rj
>
> sigma_j = sqrt((1/n_train) \* sum_r (x_rj-mu_j)^2)
>
> sigma_safe_j = 1.0 if sigma_j \<= 1e-12 else sigma_j
>
> z_rj = (x_rj-mu_j) / sigma_safe_j

LOSO留出场景只套用训练折统计；最终all2356模型应使用自己冻结的全开发集统计。不能拿C11留出折的mean/std去配最终checkpoint，也不能在线按当前episode重新估计统计。\[D1§4；S1、S2\]

## 7.4 实际训练损失：加权成对logistic排序

这是本次从父源码完整恢复的核心公式。\[S1：torch_pairwise_root_loss\]

对根节点r，Q_ri为教师对动作i的值，s_ri=f_theta(x_r)\[i\]为网络分数。对每一对i\<j：

> Delta_rij = Q_ri - Q_rj
>
> sign_rij = sign(Delta_rij)
>
> D_r = max(max_i Q_ri - min_i Q_ri, 1e-12)
>
> w_rij = abs(Delta_rij) / D_r
>
> P_r = {(i,j): 0 \<= i \< j \< 16, Delta_rij != 0}

每root最多有16×15/2=120个不重复动作对。Q相等的动作对不计入有效集合。

> W_r = sum\_(i,j in P_r) w_rij
>
> ell_r = \[sum\_(i,j in P_r) w_rij \* softplus(-sign_rij\*(s_ri-s_rj))\] / W_r
>
> softplus(u) = log(1 + exp(u))

当W_r不大于1e-12时，PyTorch函数返回可微的零损失。实现用F.softplus，避免直接exp带来的数值不稳定。

直观上，若教师认为动作i优于j，训练就推动s_i大于s_j；动作间教师Q差更大，对应的排序错误权重更大。对每root再按总权重归一化，最后执行场景均衡：

> L(theta) = (1 / number_of_train_scenes)
>
> \* sum_scene \[ (1 / roots_in_scene) \* sum_r_in_scene ell_r \]

这不是逐动作Q的MSE，也不是把完整episode成败直接当作唯一监督。网络分数主要表达相对次序；对同一个root全部分数加上相同常数，成对损失不变，因此不能把分数绝对值解释为已校准的物理收益。

## 7.5 该损失有什么值得审计的地方

Q差为0的动作对被跳过，但只要差非零就可能进入训练。若很多root的Q范围极小、差异来自采样噪声，按root归一化后仍可能形成有效排序监督。需要先统计真实Q范围、近并列动作和访问数，才能判断影响；目前不能仅凭公式说标签已经出错。\[S1；推断\]

同一个12D状态若因未编码的路线位置、历史让行状态或搜索噪声而对应不同排序，模型会遇到不可同时满足的监督。需要查询“相同/近似X但教师首选不同”的比例。根状态压缩到12维未必是充分状态表示，尤其不能默认alpha3或两个AND指标已包含所有几何与时序信息。\[推断；HOLD\]

## 7.6 优化器与训练流程

父源码使用torch.optim.Adam(model.parameters(), lr=LR)，每个epoch对该折全部训练roots计算一次loss，属于full-batch更新，而非每轮随机采样大量独立mini-batch。\[S1、S2\]

Adam的原理可概括为梯度一阶、二阶矩估计及偏差修正：\[论文：P4\]

> g_t = grad_theta L(theta\_(t-1))
>
> m_t = beta1\*m\_(t-1) + (1-beta1)\*g_t
>
> v_t = beta2\*v\_(t-1) + (1-beta2)\*(g_t)^2
>
> mhat_t = m_t / (1-beta1^t)
>
> vhat_t = v_t / (1-beta2^t)
>
> theta_t = theta\_(t-1) - eta\*mhat_t/(sqrt(vhat_t)+epsilon)

600轮和eta=0.001在V3记录中明确。beta、epsilon、weight decay等没有在2356交接表中逐项冻结；不能只凭库的常见默认值把它们当作最新checkpoint已核验配置。上述Adam公式用于说明优化机制，不是对未知参数补值。

# 8. 神经网络到底怎样接入MCTS

## 8.1 接入点在根节点动作入口，不在整棵树所有节点

真实方法链路为：当前A/B状态 → 冻结12D特征 → checkpoint对应归一化 → Value V3前向一次 → 16个动作分数 → 根动作排序或mask → 原MCTS搜索 → 执行本轮首个动作 → Controller/Vehicle Model推进 → 下一帧重新规划。\[D3§6；D4；D7\]

网络不直接输出油门、刹车和转向，不代替车辆模型，不在每个深层节点计算policy/value，也没有把所有rollout都替换成神经预测。因而“神经网络已接入”成立，“已实现完整AlphaZero式Neural-MCTS”不成立。

## 8.2 评分排序与置信门控

实际排序针对完整range(16)，按分数降序，同分时canonical index较小者优先：

> ranked = sorted(range(16), key=lambda i: (-float(score\[i\]), i))
>
> m = score\[ranked\[0\]\] - score\[ranked\[1\]\]

m是最高分与次高分之间的间隔。它不是softmax概率，也不是经过概率校准的“正确率置信度”。网络推理发生在计算m及阈值判断之前，所以PURE_FULL回退也已经支付一次forward成本。\[D6§5；D7§2.4\]

早期“先hard_safety_filter，再给feasible集合排序”的方案图，不能代替后续明确的完整16维排序实现。实际feasible掩码、untried_actions消费顺序和空集恢复需以冻结controller为准。特别是列表最终通过pop()还是pop(0)消费，会影响排序方向；这是应检查的接口契约，本次没有证据表明现有实现方向错误。\[D6§5；推断\]

## 8.3 MCTS里仍然保留什么

MCTS仍执行selection、expansion、rollout、backup。UCT的一般原理形式如下，其中Q_bar是搜索样本平均回报，不是上面的网络score：\[论文：P3\]

> UCT(s,a) = Q_bar(s,a) + c \* sqrt(log N(s) / N(s,a))
>
> Q_bar(s,a) = W(s,a) / N(s,a)

未访问动作的处理通常需要单独规则。有限时域回报的一般表示为：

> G = sum\_(k=0 to H-1) gamma^k \* r_k

这里给的是原理公式。当前FleetMCTSSearch的c、discount、终止项、rollout细节、reward各项权重及最后选动作的规则，未在本次取得的完整源码中逐项复核；不能把论文参数或早期单车参数自动复制成当前双车运行参数。已有交接支持的是：Value V3 root-order/root-mask接入没有改动深层UCT、rollout、backup与冻结budget。\[D3、D6、D7\]

## 8.4 为什么只排序未必加速

固定budget下，改变“先搜索哪个动作”不自动减少迭代数。若要获得净收益，排序必须让更小预算达到同样稳定性，或改善轨迹使总决策步数减少，而且收益还要覆盖网络推理成本。\[推断\]

现有正式结果说明这一条件尚未相对Pure成立。Pure在B8有9/9稳定锚点；naive无条件排序首次稳定为B64；confidence-gated首次稳定为B32。置信门控相对naive的首次稳定预算和成本有所改善，但B8成功数反而从naive的6/9降至3/9，不能说门控在所有预算上都更好。\[D3、D7\]

| **方法**                    | **首次9/9稳定预算** | **该预算下中位历史expansions** | **中位outer-search wall时间** |
|-----------------------------|---------------------|--------------------------------|-------------------------------|
| Pure MCTS                   | B8                  | 3432                           | 6763.0108 ms                  |
| Naive root-order            | B64                 | 9664                           | 20098.9015 ms                 |
| Confidence-gated root-order | B32                 | 6528                           | 14137.5239 ms                 |

以上是旧比较口径的expansions，不能与下一节新增加的actual root-child expanded统计混用；这也不是所有场景算法优劣的普遍排名。\[D4、D7\]

# 9. K13剪枝用什么方法和公式

## 9.1 方法名称和剪枝位置

当前是**置信门控的根节点Top-K动作剪枝**，K冻结为13。它仅对depth=0的untried_actions/candidate set施加mask。高置信root从16个动作中保留神经排序前13个，移除最后3个；深层节点的UCT、rollout、backup和budget不改。\[D6§3—6；D7§3\]

这是一种学习排序驱动的候选过滤，不是“已经证明这3个动作不安全，所以删掉”。被删动作的共同点是网络排序靠后，不是满足一条已证明的物理不可行判据。

## 9.2 四种运行模式

冻结阈值：tau_order=0.06767839193344116；tau_prune=1.2940582036972046；K=13。

| **条件**                      | **模式**            | **根候选集合与顺序**         |
|-------------------------------|---------------------|------------------------------|
| m \< tau_order                | PURE_FULL           | 保留全部16动作，回到Pure顺序 |
| tau_order ≤ m \< tau_prune    | NEURAL_ORDER_FULL   | 保留全部16动作，用神经排序   |
| m ≥ tau_prune                 | NEURAL_TOPK_PRUNED  | 保留神经Top-13               |
| mask/feasible交互后异常空集合 | PRUNE_RECOVERY_FULL | 恢复完整可用候选，避免空集   |

网络forward发生在所有模式之前。PURE_FULL不是“本root没有调用网络”。空集恢复也不保证不会误剪关键动作：只要剩下的13个非空，关键动作被删不一定触发这种保护。\[D6、D7；推断\]

## 9.3 K和阈值怎样选出

校准集合中，runtime seeds 101/102/103各采151条记录，但三组root snapshot、12D特征和teacher target完全重复。去重后是151个不同root记录，再由3个冻结模型评分，得到453个model-root pair。\[D6§7—8\]

定义高置信集合和目标保留率：

> H_m(tau) = {r : margin_m(r) \>= tau}
>
> coverage(tau) = number_of_high_confidence_pairs / 453
>
> retention_m(K,tau) = mean\_(r in H_m(tau))
>
> 1\[teacher_action(r) belongs to TopK_m(r)\]

pooled retention按全部模型的高置信pair合并计算。冻结eligibility要求tau_prune \> tau_order；pooled retention≥0.99；三个model seed各自retention≥0.99；每个模型高置信样本数\>0。\[D6§9\]

K8扫描425个非空阈值诱导子集，无解。在相同评分、相同阈值集合和相同规则下，Top-K retention随K增大不下降，因此K\<8也不能达标。随后预注册按K=9至15升序寻找“最小有解K”，同一K取最低合格tau，最终选K13。这里的“无解”只针对这份冻结数据和规则，不是证明任何模型或任何场景的K8都不可行。

## 9.4 校准结果能证明什么

高置信集合178/453≈39.2936%，三个模型支持数66、49、63，观察到的Top-13 teacher retention均为100%。每次激活少3个动作，条件剪枝比例3/16=18.75%；折算该静态校准分布的平均候选缩减为：

> (178 / 453) \* (3 / 16) = 0.0736754967 ≈ 7.37%

100%只是校准样本中未观察到教师动作落在Top-13外；阈值也是在这些数据上选出来的，且模型之间共享root、root之间可能连续相关。因此它不是未来状态的安全保证，也不是独立测试集上已证明的99%可靠性。\[D6；计算\]

## 9.5 为什么top1-top2间隔未必适合证明Top-13安全

当前margin衡量第一名与第二名的分离，而剪枝的边界在第13名与第14名。前者大，并不在数学上保证教师关键动作一定处于前13，也不保证第13与第14名之间的判断稳定。

例如，一个模型给自己偏爱的错误动作很高分，top1-top2可以很大，同时把真正关键动作排在第14名。这是逻辑反例，不是伪造一条项目实验记录。它说明置信门控必须靠独立校准与在线诊断验证，不能只凭“间隔大”当作正确性证明。\[推断\]

此外，将所有score乘以正数会保留动作排名，但会放大margin。排序regret可以完全不变，固定阈值下的剪枝激活率却改变。成对排序loss与margin门控的尺度联系，正是需要检查三个模型分数分布、训练稳定性和校准迁移的原因，而不是立即事后重选tau的理由。

# 10. 为什么剪枝真实发生了，整体反而更慢

## 10.1 对照不是Pure MCTS

已完成matched probe的OFF组为PRUNING_OFF_NEURAL_ORDER_FULL，仍有Value V3推理与神经排序；K13组在相同场景、runtime seed、model seed与budget下额外做Top-13 mask。因此这组实验隔离的是“在已有神经排序上增加剪枝”，不能把OFF误称为Pure MCTS。\[D7§3.6\]

## 10.2 三组冻结结果

| **配对实验**  | **roots：OFF→K13** | **激活root / 直接删动作** | **根层实际展开变化** | **MCTS耗时变化** | **episode wall变化** |
|---------------|--------------------|---------------------------|----------------------|------------------|----------------------|
| B16 / seed101 | 269→163            | 22 / 66                   | -40.94%              | -34.20%          | 未直接记录           |
| B16 / seed102 | 178→347            | 202 / 606                 | +73.67%              | +81.88%          | +83.28%              |
| B32 / seed101 | 152→238            | 96 / 288                  | +44.74%              | +34.44%          | +35.26%              |

来源：\[D4§8、D7§3.7\]。三组都满足“每个激活root删除3动作”。剪枝并非没有接进去；不稳定的是整个闭环访问的root数和累计代价。B16 seed101缺失episode wall，不能用MCTS累计时间替它补值。

## 10.3 局部减少与轨迹变长的精确分解

在这三组记录满足每个未剪root展开16个根动作、剪枝root展开13个的统计条件下，设N为整个episode访问root数，A为激活剪枝root数：

> E_OFF = 16 \* N_OFF
>
> E_K13 = 16 \* N_K13 - 3 \* A
>
> Delta_E = 16 \* (N_K13-N_OFF) - 3\*A

这只分解根层实际动作展开，不是任意MCTS的全树节点数恒等式，尤其不能无条件用于B8。

B16 seed101：16×(163-269)-66=-1762，4304→2542。大部分减少来自root数下降，而不是直接删除的66个动作。

B16 seed102：16×(347-178)-606=2098，2848→4946。多访问169个root带来的2704个根动作展开，超过局部节省606个。

B32 seed101：16×(238-152)-288=1088，2432→3520。预算变大仍没有阻止轨迹/root数增加。\[计算；D7§3.8\]

## 10.4 这与数据问题有什么关系

不准确或支持不足的排序可能改变根节点搜索资源分配，进而改变所选动作、下一状态和后续轨迹。另一方面，即使教师动作仍保留在Top-13，移除其他动作也可能改变有限预算下的访问分配，使最终选择变化。因此“teacher retention=100%”不保证闭环policy不变。\[推断\]

可以同时成立的是：数据对某些关键状态支持不足；网络在平均离线指标上尚可；Top-K机制真实生效；剪枝改变策略后使episode更长。现有冻结结果尚不能量化这些因素各占多少。需要已保存的逐root诊断，而非只看最终三张耗时图。

最终工程结论保持：局部神经候选缩减成立；当前冻结B16/B32协议下的可复现端到端加速不成立。\[D4§8\]

# 11. 参考哪篇论文：必须区分直接来源与方法关联

## 11.1 Paper1是项目的重要参考，但不是当前实现的逐字复现

\[P1\] Lin、Lan、Anagnostopoulos、Tian、Flynn，Safety-Critical Multi-Agent MCTS for Mixed Traffic Coordination at Unsignalized Intersections，IEEE TITS，2025，DOI: 10.1109/TITS.2025.3598727。用户参考包中的362388.pdf为作者接受稿。项目PAPER_METHOD_COMPATIBILITY_DECISION_V1明确将其定位为adapted route-constrained implementation，而非verbatim reproduction。\[D8；P1\]

论文第6—7页提供安全节点判据、联合动作树和混合rollout。式(22)的核心是同时满足V2V风险阈值、V2H风险阈值以及V2R最小道路距离才把节点标为safe：

> safe(n) = \[Risk_V2V(n) \<= threshold_V2V\]
>
> AND \[Risk_V2H(n) \<= threshold_V2H\]
>
> AND \[distance_V2R(n) \>= d_min\]

以上为保留原条件的解释写法。它基于安全判据排除节点，与当前按神经分数删除最后3个动作不是同一机制。

论文式(26)写出的混合rollout为：

> pi_rollout = alpha\*pi_model + (1-alpha)\*pi_random
>
> pi_model = argmax\_(pi in Pi_safe) Q_pred(s, pi)
>
> pi_random ~ Uniform(Pi_safe)

其中Q_pred是learned value predictor。论文确实讨论了学习预测器，但本次核对的原文并没有给出项目这套12→64→64→16、2356-root训练、场景等权pairwise loss、600 epochs、K13及两个tau的完整配置。**不能说这些具体参数与损失“都是论文原样规定的”。**

更重要的是，论文把learned predictor用于rollout策略；项目当前把网络用于root排序/mask，深层rollout未被替换。这是接入位置的实质区别，不是简单参数微调。\[P1第7页式(26)；D3、D6\]

## 11.2 Paper2是风险评估架构参考，不是V3与K13训练配方

\[P2\] Fan Bu、Peng Chen、Guizhen Yu、Yunpeng Wang，Risk-aware unsignalized intersection management in unstructured mixed-traffic environment: a real-time hierarchical safety evaluation method，Transportation Research Part C，192，105890，2026，DOI: 10.1016/j.trc.2026.105890。用户包中为1-s2.0-S0968090X26003761-main.pdf。

项目兼容性文档支持借鉴其simulation→evaluation→search思路；其RA-MVSFM、通行次序搜索、lane-free运动与OCP不是当前root-level纵向联合动作网络的现成实现。不能将K13或pairwise损失归为该论文已经验证的模块。\[D8；P2\]

## 11.3 UCT与RankNet分别提供什么基础

\[P3\] Kocsis与Szepesvári的Bandit Based Monte-Carlo Planning（ECML 2006）是UCT的原始基础文献。它解释MCTS如何用上置信界平衡探索与利用；不直接提供当前12D网络和K13门控。

\[P5\] Burges等的Learning to Rank using Gradient Descent（2005，RankNet）提供神经成对概率排序的经典思路。V3的softplus(-sign(DeltaQ)×score差)属于相同的成对logistic损失家族；项目又加入Q差权重、root归一化和scene-balanced聚合。\[论文：P5；源码：S1\]

这里把RankNet列为**数学方法关联与可补充引用的基础文献**，而不是声称已经找到项目开发者当时明确引用RankNet的历史记录。当前可核实的直接算法来源仍是项目自身冻结训练源码。

## 11.4 方法—论文—实际实现对照

| **项目组件**           | **来源关系**                 | **实际边界**                              |
|------------------------|------------------------------|-------------------------------------------|
| UCT/MCTS搜索基础       | P3；P1也使用UCB树搜索        | 当前常数及实现需原Fleet源码               |
| 多车安全与协同规划方向 | P1为明确参考，D8有兼容性映射 | 固定路线纵向动作适配，不是全部混行框架    |
| 学习预测器辅助树搜索   | P1式(26)为相关动机           | 论文是混合rollout；项目是root排序/mask    |
| 12→64→64→16网络        | 项目冻结设计D1/D3            | 未找到由某论文规定该精确层数的证据        |
| 加权成对logistic loss  | 项目源码S1；与P5同损失家族   | Q权重和scene聚合为项目具体设计            |
| Adam优化               | 父源码S1/S2；P4为原始论文    | 精确完整超参数需实际trainer               |
| top1-top2置信门控      | 项目冻结controller与阈值     | 未核实与某篇论文一一对应的推导            |
| K13与tau_prune         | 项目development-only校准规则 | 数据选择结果，不是论文固定常数            |
| 根级Top-K删除          | 项目controller               | 不等于P1基于风险阈值的unsafe-node pruning |

可用于论文/汇报的准确表述是：本项目借鉴安全关键多车MCTS的研究思路，在现有route-constrained Fleet-MCTS上训练动作排序网络，并以置信门控方式影响根动作顺序及候选集合；具体pairwise训练与K13规则来自项目冻结设计和开发校准，而非对参考论文所有模块的直接复现。

# 12. 本次审计后的最小下一步

## 12.1 当前只做训练证据核验，不启动新训练

本次任务的Gate应为“训练数据与训练证据只读审计”，资源LOW。此前交接的视觉资产任务暂不作为本次要执行的任务。已消费的2356训练、正式27-cell、K13 B16/B32 namespace保持不动。

下一步最有价值的不是再写一份算法计划，而是取得下面四组已有文件，完成原始证据绑定。可以合成一个ZIP上传；不需要重新粘贴历史聊天。

| **文件组**      | **最小内容**                                                                             | **用来回答什么**                         |
|-----------------|------------------------------------------------------------------------------------------|------------------------------------------|
| 训练数据组      | 2356-root NPZ、dataset manifest、feature/action schema、原有数据质量报告                 | 恒零、重复、finite、身份和标签列是否正确 |
| 实际训练组      | 2356 derived trainer；最终all2356 trainer/config；已存在stdout/stderr/summary与epoch日志 | 究竟怎样训练，有无收敛历史及标准         |
| 模型与评价组    | 三个最终checkpoint的metadata/normalization；exact ranking_metrics源码；冻结C01结果       | 模型、特征、损失、评价口径是否匹配       |
| 原始/在线诊断组 | 原有collector source及代表性root JSONL；已保存online feature/margin/action日志           | 加速度语义、Q支持和训练—在线差异         |

原始JSONL可能较大；先提供其manifest、schema及当前已保存的少量关键状态记录即可，不要求为了审计额外跑一轮MCTS。实际checkpoint若上传，本地加载也应采用安全方式；本报告没有执行pickle/torch反序列化或模型forward。

## 12.2 原始审计的PASS与HOLD边界

结构检查的PASS要求：文件SHA与冻结绑定一致；数组shape正确；必要数字finite；每root身份无冲突；16动作映射完整且无错位；train/evaluation隔离符合原协议；训练与在线feature order和normalization一致。若某项异常，应报告具体root/列/episode及数量，而不是直接修改原文件。

收敛检查只有在拿到对应epoch历史后才能下结论。若不存在历史曲线，则保留CONVERGENCE_NOT_ESTABLISHED；即便最终训练结果通过离线标准，也不把缺少收敛证据改写成PASS。后续若确需新增有曲线的诊断训练，必须另立新协议和命名空间，不能借“审计”重跑旧one-shot。

数据充分性、标签搜索稳定性和跨场景泛化不存在一个仅凭“2356条、600轮”的自动PASS。它们需要与当前研究目标相匹配的预定标准；本报告没有事后虚构这些标准。

# 13. 最终结论

**你的怀疑有依据，而且现有材料不足以排除训练数据问题。** 最值得先检查的是两个加速度特征为何恒零、6段episode提供了多少有效状态变化、有限预算教师Q是否稳定，以及在线输入是否落在训练支持范围内。

但“训练数据有疑点”不等于“离线训练没有达标”。2356-root版本通过了原定三场景排序标准，C01也通过了独立离线标准；这证明了有限范围内的学习信号，不证明优化充分收敛、剪枝安全或闭环加速。

当前实际方法是：**MCTS动作Q监督 → 场景均衡的加权成对排序网络 → 根节点16动作排序 → top1-top2置信门控 → 高置信Top-13根候选mask → 原MCTS与原闭环执行。** 它不是参考论文完整的learned rollout/安全节点剪枝复现。

数据、优化、特征一致性、搜索策略扰动四个环节都需要保留在原因分析中。现有K13局部机制成立、端到端加速不成立的冻结结论保持有效；本次只读审计不修改这些科研结果。

# 附录A. 关键证据路径与哈希

以下云端路径及哈希来自原交接记录，**是后续比对目标，不是本次对AutoDL实时文件的复核结果**。路径若因归档改变，应依据manifest恢复关联，不能把missing直接当成删除。

**A1. 2356-root数据**

> /root/autodl-tmp/paper1_value_v3_development_only_v1/
>
> expanded_2356_development_input_v1/
>
> paper1_value_v3_expanded_2356_episode_aware_root_dataset_v1.npz
>
> SHA256:
>
> 106936a30e4c55b10b7968de2534e822c262db50c21494cca354700d78a70a27

**A2. 2356 derived trainer**

> /root/autodl-tmp/paper1_value_v3_development_only_v1/
>
> expanded_2356_harness_static_v1/
>
> paper1_value_v3_pairwise_rank_training_pipeline_expanded_2356_v1.py
>
> SHA256:
>
> 753bcf28eb689a86291b55e8c6c9f8578e9333c978cbd3253743c747ebfd400c

**A3. 父V3 trainer（本次取得的是其历史源码打印摘录）**

> /root/autodl-tmp/paper1_value_v3_development_only_v1/
>
> paper1_value_v3_pairwise_rank_training_pipeline_v1.py
>
> SHA256:
>
> 3192664cc439a7150fa5d688a2ea0026b59b9e484e64f5b4de32d91f65e6f648

**A4. LOSO结果与日志根目录**

> /root/autodl-tmp/paper1_value_v3_development_only_v1/
>
> expanded_2356_development_execution_v1/
>
> PAPER1_VALUE_V3_DEVELOPMENT_LOSO_SUMMARY_V1.json
>
> Summary SHA256:
>
> 87302b40142043bcce413d268543c21b51be0a5b8052b921c6260294e63dfccc
>
> 同一研究根目录下：
>
> expanded_2356_training_execution_evidence_v1/
>
> START.json / CAPTURE.json
>
> runner_stdout.txt / runner_stderr.txt / runner_rc.txt

**A5. 最终三模型**

> value_v3_full_development_final_candidate_v1/
>
> seed_20260824_final_all2356/checkpoint.pt
>
> 496e4259eb9801f3ce70c1094be12fd0985cb03e97d606cade8dfbe9d5228633
>
> seed_20260825_final_all2356/checkpoint.pt
>
> 5df90947a5fdd2bc6aa525ca5eba78b6379e127e5df6ca1d0362c992caab73b5
>
> seed_20260826_final_all2356/checkpoint.pt
>
> 3881d39c09b02a513e44f0fe612aad42de9ff636fd07e314d327b4c6d5f132df

A5为原交接中的相对研究路径；准确当前绝对路径需manifest/live inventory绑定，不能盲目拼接目录。\[D5\]

**A6. 当前Top-K controller和K13最终结论**

> paper1_value_confidence_gated_topk_pruning_search_v1.py
>
> 5104d9c2c9363ec9acd51ea7849fe306d7632ab07577ceb2b2ccca74a4c93350
>
> Final K13 decision JSON:
>
> 5c1ec038a3a9593616dc93e3bd0cafc0d9bf2bb109dcc498aa7cf99c32eec58e
>
> Evidence root:
>
> /root/autodl-tmp/paper1_value_v3_confidence_gated_topk_pruning_dev_v1/
>
> matched_runtime_probe_k13_b16_b32_v2

# 附录B. 项目资料、源码摘录与论文来源

## B1. 项目资料

\[D1\] AI接手文档2.zip 内《MineSim-Dynamic_ValueV3_2356root_神经网络阶段性交接文档_2026-08-25_训练完成待闭环.docx》。重点：§1开发门槛；§2数据/episode；§3训练；§4与附录A归一化；§7结果；§12哈希。本次本地文档SHA256：d0cac98fc4d699b52d4cf68319026d5a9a96f78c8cfb12e51a62e2c222418a57。AI接手文档3中有同名副本。

\[D2\] AI接手文档2.zip 内《MineSim-Dynamic_全项目超详细阶段性总总结与AI无缝接管手册_2026-08-25_C06授权停点版.docx》。重点：Fleet采集预算、actionwise\[16\]标签合同、V2/V3区别、C11负结果与coverage扩展。本次本地SHA256：1c5778737d0fc801600d5122fed384511e1e65d4709093c453f61643b6fdbed8。

\[D3\] AI接手文档3.zip 内《MineSim-Dynamic_全项目最终交接与AI无缝接管手册_2026-08-30_ValueGuidedMCTS闭环与文件整理终版.docx》。重点：§5最终V3方法/C01评价；§6root-order真实接入。本次本地SHA256：cd4602a4da5e1931a54c8151d2122156b4687392b96fcac1bba1759f476e4864。

\[D4\] 《MineSim_Dynamic_正式交接文档_20260831.docx》。重点：§7—8 K13参数与matched runtime最终负结论；§10 one-shot台账；§11关键文件绑定。该文档用于最新运行状态；网络训练目标的细节应同时对照更具体的D1/D3/S1，不把总览旧字段静默当作无冲突事实。

\[D5\] AI接手文档3.zip 内《MineSim-Dynamic_全项目阶段性总总结与AI无缝接管手册_2026-08-26_C01评价数据冻结_ExactMetric三参数签名故障停点版.docx》。重点：最终all2356 checkpoint、C01数据和exact metric接口。

\[D6\] 《MineSim_ValueV3_ConfidenceGated_TopKPruning_项目交接文档_K13运行价值评审完成版_V1.docx》。重点：§5完整16动作排序；§7—10校准去重、pairwise评分、K-ladder和静态缩减。其“下一步尚未probe”已被D4取代，但机制与校准证据仍有价值。

\[D7\] 《MineSim_Dynamic_阶段汇报.docx》及同名PDF，V4三部分汇报。重点：第二部分网络；第三部分剪枝、matched OFF对照和根展开量分解。DOCX与PDF分页不同，按小节定位。

\[D8\] PAPER_METHOD_COMPATIBILITY_DECISION_V1(1).zip 内同名MD与JSON，特别是Paper1/Paper2 mapping和“非逐字复现”结论。该文件记录的是当时的适配评审，历史“Value missing”不能覆盖后续已接入V3的事实。

\[D9\] CROSS_SCENE_DYNAMIC_CONCLUSION_V1(1).zip 内cross_scene_dynamic_conclusion_v1.json。重点：Fleet budget/depth/dt及C11安全但进度失败。它是历史场景证据，不替代当前V3结果。

## B2. 取得的历史源码摘录

\[S1\] Library中的《粘贴的文本 (1)(20260824-131306).txt》。含父trainer实际打印的numpy_pairwise_root_loss、torch_pairwise_root_loss、train_fold完整函数段。核心函数在原Python文件中标注行号：numpy loss 497—577；torch loss 749—848；train_fold 888—1181。本次本地日志文件SHA256：95109ce5b44cc44370153ab8c4ea148cee14c715abe1726ea4dea6c30babb0bf。日志SHA与其引用的Python SHA不是同一对象。

\[S2\] Library中的《粘贴的文本 (1)(20260824-131644).txt》。含数据构建与V3 train_fold摘录，同时也含V2函数；本报告按版本区分，未把V2训练细节直接当成V3。本次本地日志SHA256：816f1a1bf84b5a2967b223041840f4d056da83f1c0fc6da9cb8a3c2291b7c8a7。

源码摘录揭示真实历史实现，但不是本次登录AutoDL后重新取得的当前源码；其与2356版本的联系由D1的派生合同支持，最新live绑定仍需核验。

## B3. 论文与引用用途

\[P1\] Lin Z, Lan J, Anagnostopoulos C, Tian Z, Flynn D. Safety-Critical Multi-Agent MCTS for Mixed Traffic Coordination at Unsignalized Intersections. IEEE Transactions on Intelligent Transportation Systems, 2025. DOI: 10.1109/TITS.2025.3598727. 用户参考包362388.pdf；已核对作者机构Glasgow公开记录。关键位置：第6页式(20)动作空间；第7页式(22)安全判据、式(25)UCB、式(26)混合rollout。

\[P2\] Bu F, Chen P, Yu G, Wang Y. Risk-aware unsignalized intersection management in unstructured mixed-traffic environment: a real-time hierarchical safety evaluation method. Transportation Research Part C: Emerging Technologies, 2026, 192:105890. DOI: 10.1016/j.trc.2026.105890. 用户参考包PDF与Elsevier页面核对；用于区分风险评估/通行次序框架与本项目root动作网络。

\[P3\] Kocsis L, Szepesvári C. Bandit Based Monte-Carlo Planning. Machine Learning: ECML 2006. Lecture Notes in Computer Science, 4212:282–293. DOI: 10.1007/11871842_29. Springer官方记录核对；用于UCT基础。

\[P4\] Kingma D P, Ba J. Adam: A Method for Stochastic Optimization. ICLR, 2015; arXiv:1412.6980. 原始作者论文核对；用于Adam更新原理，不为本项目的收敛背书。

\[P5\] Burges C J C, Shaked T, Renshaw E, Lazier A, Deeds M, Hamilton N, Hullender G. Learning to Rank using Gradient Descent. ICML, 2005:89–96. DOI: 10.1145/1102351.1102363；Microsoft Research技术报告MSR-TR-2005-06。用于解释RankNet成对logistic损失家族；未确认项目历史上曾显式引用此论文。

本报告所有新增分析均用于解释与审计，不构成修改冻结数据、重选模型/阈值或重跑正式实验的授权。
