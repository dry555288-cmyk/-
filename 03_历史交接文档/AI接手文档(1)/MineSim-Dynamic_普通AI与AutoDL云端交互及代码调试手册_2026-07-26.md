**MineSim-Dynamic**

**普通 AI 与 AutoDL 云端交互及代码调试手册**

适用于 DeepSeek、Kimi、豆包等普通聊天/编码模型，不依赖 AI 直接连接云端

| **项目**        | **当前事实**                                                                                                      |
|-----------------|-------------------------------------------------------------------------------------------------------------------|
| 正式项目目录    | /root/MineSim-Dynamic                                                                                             |
| 当前 Git 分支   | autodl-idm-baseline                                                                                               |
| Baseline Commit | 2521aa41a69a6e734c04c15a715e9530c8095ac3                                                                          |
| Baseline Tag    | idm-replay-autodl-baseline                                                                                        |
| 当前 Conda 环境 | minesim                                                                                                           |
| Python          | 3.9.25                                                                                                            |
| 当前系统盘      | 30G，总已用约15G，可用约16G（49%）                                                                                |
| 文档目标        | 让没有云端工具权限的普通 AI 通过“你复制命令→AutoDL 执行→你回传输出”的方式，安全地分析、写代码、测试、排错和回滚。 |

| **最重要的一句话：**普通 AI 默认看不到你的 AutoDL、不能自动 SSH、不能自己读文件、也不能知道“刚刚终端发生了什么”。你是中间的执行者。正确方法是建立严格的人机循环，而不是假设 AI 能直接操作云端。 |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# **目录与使用方法**

1\. 普通 AI 到底能不能“操作” AutoDL：能力边界

2\. 你的 MineSim 云端当前状态：AI 每次都应知道的事实

3\. 标准人机交互循环：观察 → 计划 → 修改 → 验证 → 提交

4\. 第一次把项目交给一个新 AI：上下文怎么喂

5\. AutoDL 终端基础命令：普通 AI 最常让你执行什么

6\. 如何把云端文件正确交给 AI 阅读

7\. 如何让普通 AI 写代码：新建文件、修改文件、Patch 三种方式

8\. MineSim 项目代码应该怎么写：目录、接口、Hydra 配置规则

9\. 每次改代码后必须执行的测试阶梯

10\. 报错以后怎么办：标准错误采集包

11\. 高频错误分类与处理方法

12\. Git：如何保证 AI 写错了也能一键回去

13\. AI 编码 Prompt 模板：可直接复制给 DeepSeek/Kimi/豆包

14\. Pure MCTS/Neural-MCTS 开发时的 AI 协作方式

15\. 安全与隐私：绝对不要发给普通 AI 的内容

16\. 一次完整示范：从“我要新增 MCTSPlanner”到跑通

17\. 交接模板：换一个 AI 时怎么让它立刻接上

18\. 最终检查表：什么时候可以说“这个改动完成了”

| **配套文档：**本手册应和《MineSim-Dynamic AutoDL云端项目环境与文件资产说明书》以及《MineSim-Dynamic 纯MCTS与神经网络增强实施手册》一起使用：前者回答“现在有什么”，后者回答“研究算法怎么做”，本手册回答“普通 AI 怎么和云端配合把代码真正做出来”。 |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# **1. 普通 AI 到底能不能“操作” AutoDL：能力边界**

以普通网页/APP 里的 DeepSeek、Kimi、豆包为例，它们通常只是对话模型。除非你额外配置了远程终端插件、Agent、MCP 或 IDE 连接，否则它们不能直接进入你的 AutoDL。

| **能力**                   | **普通 AI 默认状态** | **正确做法**                                                  |
|----------------------------|----------------------|---------------------------------------------------------------|
| 查看 /root/MineSim-Dynamic | 不能直接查看         | 你用终端 cat/sed/find/git diff，把内容复制给 AI，或上传文件   |
| 执行 bash 命令             | 不能                 | AI 生成命令，你在 AutoDL Terminal 执行，再回传完整输出        |
| 修改文件                   | 不能直接改           | AI 给出新文件内容或 patch，你执行写入/应用                    |
| 知道当前 Git 状态          | 不知道               | 每次重要修改前提供 git status / branch / log                  |
| 知道当前 Conda 环境        | 不知道               | 提供 echo \$CONDA_DEFAULT_ENV、which python、python --version |
| 判断代码是否真的跑通       | 仅凭代码不能确认     | 必须以 AutoDL 实际运行结果、测试、日志为准                    |
| 自动记住上次会话所有背景   | 不能保证             | 每次新会话发送“项目上下文包”                                  |

## **1.1 正确的人机关系**

> 普通 AI = 代码顾问 / 代码生成器 / 调试分析器  
> 你 = 云端执行者 + 最终确认者  
> AutoDL = 唯一真实运行环境  
> Git = 安全绳 / 时间机器

结论：AI 说“应该可以”不算完成；只有 AutoDL 的真实命令输出和 Git diff 才算事实。

# **2. 你的 MineSim 云端当前状态：AI 每次都应知道的事实**

| **事实**              | **当前值**                                   | **给 AI 的意义**                                                     |
|-----------------------|----------------------------------------------|----------------------------------------------------------------------|
| 正式仓库              | /root/MineSim-Dynamic                        | AI 只能围绕这个目录修改当前项目                                      |
| 当前分支              | autodl-idm-baseline                          | 这是 MCTS 开发前固定 baseline；尚未创建 mcts-dev                     |
| 当前 commit           | 2521aa4                                      | baseline 已打 tag idm-replay-autodl-baseline                         |
| Conda                 | minesim                                      | /root/miniconda3/envs/minesim；Python 3.9.25                         |
| 数据根目录            | /root/datasets                               | 地图 /root/datasets/maps；场景库 /root/datasets/scenario-library-all |
| 当前 planner baseline | IDMPlanner                                   | Mode 1 = IDM + Replay + iLQR + KBM                                   |
| Controller            | TwoStageController + iLQR                    | 第一阶段 MCTS 不改 controller                                        |
| Ego update            | Kinematic Bicycle Model                      | 第一阶段 MCTS 不改 KBM                                               |
| 历史 baseline 备份    | /root/autodl-tmp/minesim_idm_baseline_backup | 代码 patch、环境、配置、outputs 都已备份                             |
| 大文件位置            | /root/autodl-tmp                             | 以后训练数据 / checkpoint / 大量日志优先放这里                       |

| **禁止 AI 自作主张：**任何普通 AI 如果在没有阅读 AbstractPlanner、IDMPlanner、现有 YAML 的情况下就直接编造 MineSim API，应停止采用其代码。先让它读真实源码，再写。 |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# **3. 标准人机交互循环：观察 → 计划 → 修改 → 验证 → 提交**

> 第 0 步 确认你在正确环境/目录/Git 分支  
> ↓  
> 第 1 步 只读观察：让 AI 要什么文件，就把真实文件给它  
> ↓  
> 第 2 步 AI 先给“修改计划”，不要立即写代码  
> ↓  
> 第 3 步 一次只改一个小目标  
> ↓  
> 第 4 步 AutoDL 执行静态检查 / import / 单元测试 / 仿真  
> ↓  
> 第 5 步 出错：把完整错误包回传 AI，不猜  
> ↓  
> 第 6 步 跑通后 git diff 人工检查  
> ↓  
> 第 7 步 git add + git commit 保存里程碑

## **3.1 每次会话开始先执行“四件套”**

> cd /root/MineSim-Dynamic  
> echo "ENV=\$CONDA_DEFAULT_ENV"  
> which python  
> python --version  
> git branch --show-current  
> git status --short

你希望看到 minesim、Python 3.9.25、正确开发分支，并且知道工作树当前是否干净。

# **4. 第一次把项目交给一个新 AI：上下文怎么喂**

不要对新 AI 只说“帮我写 MCTS”。它不知道 MineSim 的接口。第一次必须先给一个简洁但足够的“项目上下文包”。

## **4.1 推荐的固定开场 Prompt**

> 你是我的 Python/MineSim 代码助手。你不能直接访问我的 AutoDL，必须以我提供的真实文件和终端输出为准。  
>   
> 项目事实：  
> 1. 正式仓库：/root/MineSim-Dynamic  
> 2. Conda：minesim，Python 3.9.25  
> 3. 当前 baseline：autodl-idm-baseline，commit 2521aa4，tag idm-replay-autodl-baseline  
> 4. 当前仿真链：IDMPlanner -\> AbstractTrajectory -\> TwoStageController -\> iLQR -\> Kinematic Bicycle Model  
> 5. 其他 agents 当前用 replay_policy_agents_box_track  
> 6. 第一阶段只替换 Planner，不修改 Controller、KBM 和原 IDM 算法  
> 7. 数据：/root/datasets；大文件放 /root/autodl-tmp  
>   
> 协作规则：  
> - 不得编造 MineSim API；需要接口时先向我要对应源码。  
> - 一次只实现一个小模块。  
> - 修改旧文件优先给 unified diff；新文件可以给完整内容。  
> - 每次代码都必须附：为什么这样写、依赖哪些真实接口、执行命令、成功标准、失败时应收集什么日志。  
> - 不允许让我直接 rm -rf 项目、Conda、.git、.ssh。  
> - 不确定就明确写 UNKNOWN，不要猜。  
>   
> 现在先不要写代码。先告诉我：完成【这里写本次目标】之前，你需要我提供哪些真实文件？

## **4.2 为什么先让 AI 要文件**

- 减少 API 幻觉：模型不能把 NuPlan、CARLA、Gym 的接口误套进 MineSim。

- 减少“大改一堆然后不知道错在哪”的情况。

- 让 AI 的每一个 import、class、method signature 都有源码依据。

# **5. AutoDL 终端基础命令：普通 AI 最常让你执行什么**

## **5.1 看位置、环境、磁盘**

> pwd  
> cd /root/MineSim-Dynamic  
> echo \$CONDA_DEFAULT_ENV  
> which python  
> python --version  
> df -h /  
> du -sh /root/MineSim-Dynamic /root/datasets /root/autodl-tmp 2\>/dev/null

## **5.2 看 Git**

> git branch --show-current  
> git status  
> git log -5 --oneline --decorate  
> git diff  
> git diff --stat  
> git diff -- path/to/file.py

## **5.3 找文件**

> find /root/MineSim-Dynamic -type f -name "\*planner\*.py" \| sort  
> find /root/MineSim-Dynamic/devkit/script/config/sim_engine -type f -name "\*.yaml" \| sort  
> grep -RIn "class IDMPlanner" /root/MineSim-Dynamic/devkit \| head -20  
> grep -RIn "compute_planner_trajectory" /root/MineSim-Dynamic/devkit/sim_engine/planning \| head -50

## **5.4 看文件内容**

> \# 小文件全部看  
> cat path/to/file.py  
>   
> \# 大文件按行看，推荐这种  
> sed -n '1,220p' path/to/file.py  
> sed -n '220,440p' path/to/file.py  
>   
> \# 带行号，便于 AI 精确讨论  
> nl -ba path/to/file.py \| sed -n '1,220p'

## **5.5 你之前最容易犯的复制错误**

| **不要复制提示符和输出：**终端里的“(minesim) root@autodl-container...#”不是命令。也不要把上一次 ls/du 输出重新粘进 Bash。只复制 AI 明确给你的代码块内容。 |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------|

# **6. 如何把云端文件正确交给 AI 阅读**

普通 AI 质量高度依赖你给它的“真实上下文”。文件太少会猜，文件太多会淹没重点。

## **6.1 三种推荐方法**

| **情况**                  | **推荐方法**                         | **原因**                               |
|---------------------------|--------------------------------------|----------------------------------------|
| 文件 \< 300 行            | 直接 cat 或上传文件                  | 上下文完整                             |
| 文件较长                  | nl -ba + sed 分段                    | 保留行号，AI 可准确指出修改位置        |
| 多个关联文件              | 一次上传 3~6 个关键文件              | 让 AI 看接口调用链，不要一次丢整个仓库 |
| 只定位某个 class/function | grep 找行号，再 sed 上下各 80~150 行 | 减少无关上下文                         |

## **6.2 MineSim 开发时常见“最小文件组”**

| **任务**           | **至少给 AI 的真实文件**                                                                             |
|--------------------|------------------------------------------------------------------------------------------------------|
| 新增 Planner       | abstract_planner.py + 一个现有可运行 planner（优先 idm_planner.py）+ 对应 planner YAML + Mode 1 YAML |
| 改 trajectory 输出 | AbstractTrajectory/InterpolatedTrajectory 相关定义 + IDMPlanner 生成 trajectory 的源码               |
| 接 Controller      | two_stage_controller_ilqr_tracker_KBM.yaml + TwoStageController 类源码 + planner 输出类型            |
| 做 MCTS State      | PlannerInput/SimulationHistory/EgoState/Observation 真实定义 + IDMPlanner 当前读取方式               |
| Hydra 报错         | 失败 YAML + \_target\_ 对应 Python 类 + 完整 traceback                                               |

# **7. 如何让普通 AI 写代码：新建文件、修改文件、Patch 三种方式**

## **7.1 方法 A：新建小文件，完整覆盖写入**

适合新建 mcts/state.py 这类文件。让 AI 输出“完整文件内容”，然后在 AutoDL 使用 here-document。

> mkdir -p /root/MineSim-Dynamic/devkit/sim_engine/planning/planner/mcts  
>   
> cat \> /root/MineSim-Dynamic/devkit/sim_engine/planning/planner/mcts/state.py \<\<'PY'  
> \# 把 AI 给出的完整 Python 文件内容粘在这里  
> PY  
>   
> python -m py_compile /root/MineSim-Dynamic/devkit/sim_engine/planning/planner/mcts/state.py

| **here-document 规则：**结束标记 PY 必须单独占一行，前后不要有空格；开始和结束都用同一个标记。代码中可以包含引号而不会被 shell 展开。 |
|---------------------------------------------------------------------------------------------------------------------------------------|

## **7.2 方法 B：修改旧文件，优先让 AI 给 unified diff**

这是最推荐的方法。不要让普通 AI 把一个 600 行旧文件全部重写，因为很容易删除你已有的 AutoDL 适配。

> \# 1. 让 AI 输出一个标准 unified diff  
> \# 2. 把它保存成临时 patch，例如：  
> cat \> /tmp/mcts_change.patch \<\<'PATCH'  
> ...AI 输出的 diff...  
> PATCH  
>   
> \# 3. 先检查，不真正修改  
> cd /root/MineSim-Dynamic  
> git apply --check /tmp/mcts_change.patch  
>   
> \# 4. check 成功后再应用  
> git apply /tmp/mcts_change.patch  
>   
> \# 5. 马上查看实际变化  
> git diff --stat  
> git diff

为什么这样安全：git apply --check 会先判断 patch 是否和你当前文件匹配；失败时不会部分乱改。

## **7.3 方法 C：文件很小且确定要重写**

只有新文件、测试文件或明确可整体替换的短文件才适合。任何核心旧文件重写前先执行 git status 和 git diff。

## **7.4 AI 输出代码时必须要求这五项**

- 目标文件绝对路径

- 完整 import 列表以及每个 import 的来源依据

- 代码本体或 unified diff

- 执行/测试命令

- 成功标准与可能失败点

# **8. MineSim 项目代码应该怎么写：目录、接口、Hydra 配置规则**

## **8.1 MCTS 推荐目录**

> /root/MineSim-Dynamic/devkit/sim_engine/planning/planner/  
> ├── local_planner/  
> │ ├── idm_planner.py  
> │ └── mcts_planner.py \# MineSim 适配层  
> └── mcts/  
> ├── \_\_init\_\_.py  
> ├── state.py \# MCTSState  
> ├── action_space.py \# ACCEL/KEEP/DECEL/BRAKE  
> ├── state_builder.py \# MineSim -\> MCTSState  
> ├── transition_model.py \# 树内近似动力学  
> ├── reward.py  
> ├── node.py  
> ├── search.py  
> ├── trajectory_adapter.py  
> └── diagnostics.py

## **8.2 为什么 MCTSPlanner 和搜索内核要分开**

- mcts_planner.py 只负责 MineSim API：PlannerInput、history、map、trajectory。

- mcts/\*.py 尽量写成普通 Python、纯函数和 dataclass，便于普通 AI 单独测试。

- 如果 search.py 出错，不应同时依赖 Hydra、Controller 和地图加载。

- 未来神经网络只替换 leaf evaluation / prior，不需要重写 MineSim Planner 外壳。

## **8.3 Planner 必须服从真实 AbstractPlanner**

普通 AI 写 MCTSPlanner 前必须读：

> /root/MineSim-Dynamic/devkit/sim_engine/planning/planner/abstract_planner.py  
> /root/MineSim-Dynamic/devkit/sim_engine/planning/planner/local_planner/idm_planner.py

并严格匹配 name()、initialize(...)、observation_type()、compute_planner_trajectory(...) 等真实签名。签名以你云端源码为唯一标准，不以 AI 记忆为标准。

## **8.4 Hydra YAML 的基本规则**

> \# 示例结构（类路径必须以你的真实 Python 文件为准）  
> \_target\_: devkit.sim_engine.planning.planner.local_planner.mcts_planner.MCTSPlanner  
>   
> search_budget: 200  
> max_depth: 6  
> c_uct: 1.4  
> gamma: 0.98

注意：这只是结构示意。真正参数名必须和 MCTSPlanner.\_\_init\_\_ 完全一致；Hydra 报“unexpected keyword argument”时首先检查这里。

# **9. 每次改代码后必须执行的测试阶梯**

不要改完就直接跑完整仿真。按成本从低到高逐层测试，某层失败就停在该层。

| **层级**           | **命令/方法**                                               | **通过标准**                                       |
|--------------------|-------------------------------------------------------------|----------------------------------------------------|
| L0 Git 检查        | git diff --check                                            | 无 trailing whitespace/error                       |
| L1 语法            | python -m py_compile path/to/changed.py                     | 无输出即通过                                       |
| L2 Import          | python -c "from ... import MCTSPlanner; print(MCTSPlanner)" | 能正确 import                                      |
| L3 纯函数/单元测试 | pytest 某个 mcts 测试或简短 Python assert                   | State/transition/reward/search 独立正确            |
| L4 Hydra 构造      | 运行最小 config/instantiate 测试                            | \_target\_ 能找到；构造参数匹配                    |
| L5 Planner shell   | MCTSPlanner 暂时复用 IDM 输出 trajectory                    | MineSim 能进入自定义 Planner 并产生合法 trajectory |
| L6 单场景短仿真    | 固定一个已知场景                                            | Controller/KBM 能闭环执行                          |
| L7 回归            | 同一 baseline 场景 IDM 再跑一次                             | 新增代码没有破坏 IDM baseline                      |

## **9.1 常用检查命令**

> cd /root/MineSim-Dynamic  
>   
> \# Python 语法  
> python -m py_compile devkit/sim_engine/planning/planner/local_planner/mcts_planner.py  
>   
> \# Git whitespace  
> git diff --check  
>   
> \# 看改动  
> git diff --stat  
> git diff  
>   
> \# 确认没有误改 baseline 文件  
> git status --short

# **10. 报错以后怎么办：标准错误采集包**

最差的问法是：“它报错了，怎么办？”普通 AI 没有足够事实，会开始猜。正确做法是一次把错误上下文收齐。

## **10.1 每次报错都给 AI 这 7 样东西**

1.  你实际执行的完整命令（不要改写）

2.  从 Traceback 第一行到最后一行的完整文本，不只截最后一句

3.  当前 git branch --show-current 与 git status --short

4.  刚修改文件的 git diff

5.  报错文件相关代码，带行号 nl -ba ... \| sed -n

6.  当前 echo \$CONDA_DEFAULT_ENV、which python、python --version

7.  你原本期望发生什么、实际上发生什么

## **10.2 一键生成“调试状态包”**

> cd /root/MineSim-Dynamic  
> {  
> echo "===== TIME ====="; date  
> echo "===== PWD ====="; pwd  
> echo "===== ENV ====="; echo "\$CONDA_DEFAULT_ENV"; which python; python --version  
> echo "===== GIT ====="; git branch --show-current; git status --short  
> echo "===== DIFF STAT ====="; git diff --stat  
> } 2\>&1 \| tee /root/autodl-tmp/ai_debug_context.txt

然后把这个 txt 加上完整 traceback 一起发给普通 AI。不要把 /root/.ssh、token、密码、私有密钥加入状态包。

# **11. 高频错误分类与处理方法**

| **报错/症状**                                     | **常见根因**                                            | **第一处理动作**                                                        |
|---------------------------------------------------|---------------------------------------------------------|-------------------------------------------------------------------------|
| bash: syntax error near unexpected token root@... | 把终端提示符也复制进了 Bash                             | 只复制代码块，不复制 “(minesim) root@...#”                              |
| bash: xxx: command not found                      | 把程序输出/表格文字粘回终端，或命令不存在               | Ctrl+C 回到提示符；重新只复制命令；which xxx 检查工具                   |
| ModuleNotFoundError                               | Conda 环境错误 / import 路径错 / 包未安装               | echo \$CONDA_DEFAULT_ENV；which python；检查 import 的真实模块路径      |
| ImportError                                       | 类名/函数名与源码不一致，或循环 import                  | grep 真实定义；不要让 AI 猜；检查依赖方向                               |
| SyntaxError / IndentationError                    | 粘贴代码损坏、缩进错、here-doc 边界错                   | python -m py_compile；带行号打开报错位置                                |
| Hydra Error locating target                       | \_target\_ 路径错或 Python 模块不能 import              | 先手动 python -c import；再核对 YAML \_target\_                         |
| unexpected keyword argument                       | YAML 参数名和 \_\_init\_\_ 不匹配                       | 让 AI 对照真实构造函数逐项核对                                          |
| FileNotFoundError                                 | 仍使用旧绝对路径                                        | 先 ls；确认 /root/datasets、/root/MineSim-Dynamic/inputs 等当前真实路径 |
| AttributeError                                    | AI 编造了对象属性或当前对象类型与预期不同               | 打印 type(obj)；grep 类定义；查看真实 API                               |
| TypeError in trajectory/controller                | Planner 输出类型/时间戳/状态维度不满足 Controller       | 对照 IDMPlanner 如何创建 InterpolatedTrajectory；不要自行创造格式       |
| simulation 运行但车不动                           | 动作到 trajectory adapter 没生效、速度单位/时间步错误   | 打印 root action、target speed、首几个 EgoState；先验证 adapter         |
| MCTS 全选同一个动作                               | reward 尺度失衡 / transition 错 / UCB/backup bug        | 固定 toy state 单元测试 N/W/Q，检查归一化 reward                        |
| MCTS 很慢                                         | 搜索 budget/depth 过大、树内调用重型 MineSim 对象       | profile；树内只使用轻量 state；统计 iterations/s、P95 planner time      |
| CUDA / torch 报错                                 | 当前 minesim 尚未固定 PyTorch；base/mappolce GPU 包混杂 | Pure MCTS 阶段不要碰；神经网络阶段单独确认 torch/CUDA 后再安装          |
| No space left on device                           | 系统盘写满                                              | df -h /；大日志/数据移到 /root/autodl-tmp；不要删除 .ssh/.git/minesim   |
| git apply does not apply                          | patch 基于不同版本或上下文变化                          | 不要强行 -f；git status + 文件真实内容发回 AI 重做 patch                |

## **11.1 遇到错误时不要做的事**

- 不要连续修改五个文件“试试看”。

- 不要一报 ImportError 就 pip install 一个名字相似的包。

- 不要为了修 Hydra 报错而修改 Controller/KBM。

- 不要用 rm -rf 清理你不理解的目录。

- 不要让 AI 在没看到真实 traceback 的情况下“猜一个修复”。

# **12. Git：如何保证 AI 写错了也能一键回去**

## **12.1 开发前从 baseline 建分支**

> cd /root/MineSim-Dynamic  
> git status  
> git switch -c mcts-dev  
> git branch --show-current

当前文档快照中 mcts-dev 尚未创建，所以第一次真正开发时执行一次即可。

## **12.2 一次只提交一个可解释里程碑**

> git add devkit/sim_engine/planning/planner/local_planner/mcts_planner.py \\  
> devkit/script/config/sim_engine/planner/mcts_planner.yaml  
> git diff --cached  
> git commit -m "Add MCTS planner shell"

## **12.3 AI 写坏了，尚未 commit**

> \# 先看你会丢掉什么  
> git diff -- path/to/file.py  
>   
> \# 仅恢复某个已跟踪文件  
> git restore path/to/file.py

| **不要盲目 git reset --hard：**它会丢掉所有未提交改动。除非你已经确认没有任何需要保留的工作，否则不用它。 |
|-----------------------------------------------------------------------------------------------------------|

## **12.4 新增文件写坏了**

如果是未跟踪新文件，先 git status --short 确认具体路径，再手工删除那个单独文件。不要执行 git clean -fd，除非你完全理解会删除哪些文件。

# **13. AI 编码 Prompt 模板：可直接复制给 DeepSeek/Kimi/豆包**

## **13.1 “先读接口，不写代码” Prompt**

> 我准备实现 MineSim 的 MCTSPlanner。你现在只做接口分析，不写代码。  
> 我会依次给你 abstract_planner.py、idm_planner.py、idm_planner.yaml、Mode 1 YAML。  
> 请输出：  
> 1. 自定义 Planner 必须实现的方法和精确签名；  
> 2. initialize 能获得什么；  
> 3. compute_planner_trajectory 能获得什么；  
> 4. 返回值的精确类型；  
> 5. IDMPlanner 中可以复用但不应修改的部分；  
> 6. 你仍然不知道的内容写 UNKNOWN，并告诉我要哪个文件。  
> 禁止根据 NuPlan/CARLA 经验编造接口。

## **13.2 “生成新文件” Prompt**

> 基于我刚提供的真实源码，请新建【绝对路径】。  
> 要求：  
> - 只实现【一个明确目标】；  
> - Python 3.9 可运行；  
> - 不修改 Controller/KBM/IDM；  
> - 使用 type hints；  
> - 对关键假设写注释；  
> - 输出“完整文件内容”，不要省略；  
> - 文件后面给出 py_compile、import test 和最小功能测试命令；  
> - 最后解释为什么每个 import 和接口调用在我的真实源码中是成立的。

## **13.3 “修改旧文件，只给 Patch” Prompt**

> 我会给你当前文件的带行号内容和 git diff。  
> 请只做【目标】。不要重写整个文件。  
> 输出标准 unified diff，路径以仓库根目录为基准。  
> 要求：  
> 1. 不删除无关 AutoDL 路径适配；  
> 2. 不改任何未要求的接口；  
> 3. patch 后告诉我执行 git apply --check /tmp/change.patch、git apply、py_compile、git diff 的命令；  
> 4. 说明该 patch 可能失败的上下文条件。

## **13.4 “报错诊断” Prompt**

> 下面是真实 AutoDL 错误。请先诊断，不要直接重构。  
> 我会提供：执行命令、完整 traceback、git status、git diff、报错代码行和环境信息。  
> 请按以下格式回答：  
> A. 最可能根因（按概率排序，不超过3个）  
> B. 每个根因对应的证据  
> C. 还缺什么信息  
> D. 最小修复方案  
> E. 修复后的验证命令  
> F. 若修复失败，下一步需要我返回什么输出  
> 禁止用“重装所有环境”作为第一方案。

## **13.5 “代码审查” Prompt**

> 这是我当前 git diff。请只做 code review，不写新功能。  
> 重点检查：  
> - 是否破坏 MineSim AbstractPlanner 接口；  
> - 是否有错误绝对路径；  
> - 是否引入 Python 3.9 不兼容语法；  
> - 是否把真实 MineSim 对象错误塞进 MCTS Tree；  
> - reward/transition 是否有单位错误；  
> - UCT/backup 是否数学上不一致；  
> - 是否存在随机种子不可复现；  
> - 是否会导致每帧重新加载大模型/大地图；  
> - 是否缺少异常处理、日志或指标。  
> 每个问题必须引用 diff 中具体行。

# **14. Pure MCTS / Neural-MCTS 开发时的 AI 协作方式**

## **14.1 Pure MCTS 阶段**

| **模块**              | **让 AI 做什么**                             | **你在 AutoDL 怎么验证**                     |
|-----------------------|----------------------------------------------|----------------------------------------------|
| state.py              | 设计小型 dataclass；字段单位、范围、终止标志 | 纯 Python 构造 + repr/assert                 |
| action_space.py       | 固定离散动作与目标加速度映射                 | 枚举/字典单测                                |
| transition_model.py   | 实现轻量运动学，不调用重型 MineSim           | 给手算 toy state 比对数值                    |
| reward.py             | 拆成 progress/speed/safety/comfort/terminal  | 逐项打印 reward component                    |
| node.py               | N/W/Q/children/parent                        | 手工展开 2 层树验证计数                      |
| search.py             | Selection/Expansion/Rollout/Backup           | 固定 seed，toy MDP 检查最佳动作              |
| trajectory_adapter.py | 把根动作转换为 MineSim trajectory            | 先不用 MCTS，直接给 KEEP/ACCEL 测 Controller |
| mcts_planner.py       | MineSim 适配，不放搜索细节                   | Mode MCTS shell 进入 Planner 并返回合法轨迹  |

## **14.2 神经网络阶段**

普通 AI 最容易犯的错误是“一上来就写 PPO/SAC”。你的既定路线是 Pure MCTS 先成为 teacher，再训练 Value 或 Policy-Value 网络。

> Pure MCTS 闭环稳定  
> ↓  
> 记录 (state, root_visit_distribution, return) = (s, π, z)  
> ↓  
> Value Network：V(s) 替代部分 rollout  
> ↓  
> Policy + Value：P(a\|s), V(s)  
> ↓  
> PUCT：Q + prior + exploration  
> ↓  
> Neural-MCTS

让 AI 写神经网络前必须先把数据格式、state 归一化、action 索引、train/val scenario split 固定下来，否则模型代码写得再漂亮也不可复现。

## **14.3 AI 绝不能替你决定的研究参数**

- 最终 reward 权重

- MCTS budget / depth / c_uct / gamma 的最优值

- 网络层数和隐藏维度的最终选择

- 是否宣称算法优于 IDM/SPPMM

- 论文统计显著性结论

AI 可以建议起始值和搜索范围，但最终必须由实验指标决定。

# **15. 安全与隐私：绝对不要发给普通 AI 的内容**

| **内容**                        | **原因**                        | **处理方法**                                   |
|---------------------------------|---------------------------------|------------------------------------------------|
| /root/.ssh 内部文件             | 可能包含私钥、known_hosts、配置 | 不要 cat，不要上传；只告诉 AI “存在但禁止读取” |
| API key / token / 密码          | 账号风险                        | 用环境变量名称描述，不提供值                   |
| 浏览器 cookie / AutoDL 登录信息 | 账户风险                        | 永不复制                                       |
| 老师/合作方未公开数据           | 保密风险                        | 先确认许可；必要时只描述 schema                |
| 整个 .git 目录                  | 无必要且可能很大                | 用 git log/status/diff 提供需要的信息          |

## **15.1 可以放心给 AI 的常见信息**

- 公开源码文件

- 你自己写的 MCTS 文件

- Hydra YAML（不含密码）

- 完整 Python traceback

- git diff / git log

- Conda 包版本列表

- 非敏感数据 schema 和少量脱敏示例

# **16. 一次完整示范：从“我要新增 MCTSPlanner”到跑通**

下面不是让你现在立刻执行，而是演示以后和普通 AI 的标准操作顺序。

## **第 1 步：建立开发分支**

> cd /root/MineSim-Dynamic  
> git status  
> git switch -c mcts-dev  
> git status

## **第 2 步：向 AI 提供接口源码**

> nl -ba devkit/sim_engine/planning/planner/abstract_planner.py \| sed -n '1,260p'  
> nl -ba devkit/sim_engine/planning/planner/local_planner/idm_planner.py \| sed -n '1,260p'  
> cat devkit/script/config/sim_engine/planner/idm_planner.yaml  
> cat devkit/script/config/sim_engine/simulation_mode_1_default_replay_test_mode.yaml

把输出发给 AI，并使用“13.1 先读接口”Prompt。

## **第 3 步：先让 AI 写假的 MCTSPlanner 壳**

第一版不做树搜索。类名叫 MCTSPlanner，但内部暂时按已确认的方式返回和 IDM 等价的合法 trajectory。目的：只验证 Hydra 和 Planner→Controller 接口。

## **第 4 步：AI 给新文件，AutoDL 写入**

> \# 示例：AI 给完整 mcts_planner.py 后  
> cat \> devkit/sim_engine/planning/planner/local_planner/mcts_planner.py \<\<'PY'  
> ...完整代码...  
> PY  
> python -m py_compile devkit/sim_engine/planning/planner/local_planner/mcts_planner.py

## **第 5 步：增加 planner YAML 和独立 mode YAML**

让 AI 基于真实 idm_planner.yaml、Mode 1 YAML 做“最小差异复制”，不要修改原 Mode 1。这样 IDM baseline 永远还能直接运行。

## **第 6 步：静态验证**

> git diff --check  
> git status --short  
> git diff  
> python -m py_compile devkit/sim_engine/planning/planner/local_planner/mcts_planner.py

## **第 7 步：运行最小仿真**

使用新建的 MCTS 测试 mode。发生错误时，不让 AI凭最后一行猜，而是按第 10 节收集完整错误包。

## **第 8 步：壳跑通后 commit**

> git add devkit/sim_engine/planning/planner/local_planner/mcts_planner.py \\  
> devkit/script/config/sim_engine/planner/mcts_planner.yaml \\  
> devkit/script/config/sim_engine/simulation_mode_mcts_test.yaml  
> git diff --cached  
> git commit -m "Add MCTS planner shell and test mode"

## **第 9 步：再让 AI 写纯 MCTS 内核**

这时才开始 state/action/transition/reward/node/search，而且每写一个模块都独立测试、独立 commit。不要一次要求“生成整个 MCTS 系统”。

# **17. 交接模板：换一个 AI 时怎么让它立刻接上**

不同 AI 之间没有共享记忆。最稳的方法是每次维护一个“小型状态包”。你可以把下面内容复制给任何新模型。

> 【MineSim 项目交接包】  
> 项目：MineSim-Dynamic 自动矿卡规划  
> 正式仓库：/root/MineSim-Dynamic  
> 开发分支：\<填 git branch --show-current\>  
> HEAD：\<填 git log -1 --oneline\>  
> 环境：minesim / Python 3.9.25  
> 当前仿真链：Planner -\> AbstractTrajectory -\> TwoStageController -\> iLQR -\> KBM  
> 其他 agents：Replay Policy（当前开发阶段）  
> 数据：/root/datasets  
> 大文件：/root/autodl-tmp  
>   
> 当前目标：\<一句话\>  
> 已完成：\<3-6条\>  
> 当前失败点：\<没有就写 None\>  
> 最近执行命令：\<完整命令\>  
> 最近错误：\<完整 traceback 或 None\>  
> 当前 git status：\<粘贴\>  
> 当前 git diff：\<粘贴或说明 clean\>  
>   
> 限制：  
> - 不改 Controller/KBM/IDM baseline；  
> - 不编造 API；  
> - 一次只做一个小模块；  
> - 任何修改必须带测试命令；  
> - 修改旧文件优先 unified diff。

## **17.1 更推荐：在项目里维护 AI_HANDOFF.md**

可以在未来 mcts-dev 分支新建一个纯说明文件，例如 /root/MineSim-Dynamic/docs/AI_HANDOFF.md，记录“当前目标、已完成、未完成、最近 commit、怎么运行、已知 bug”。它不应该存密码或敏感信息。这样换 DeepSeek/Kimi/豆包时，只需上传这一份加当前 diff。

# **18. 最终检查表：什么时候可以说“这个改动完成了”**

- □ 我知道当前所在分支，且不是在 baseline 分支上随意开发。

- □ AI 写代码前看过需要的真实 MineSim 接口文件。

- □ 没有修改 /root/.ssh、Conda base、Controller、KBM 或 IDM baseline（除非任务明确要求）。

- □ 新文件路径符合项目结构，旧文件修改通过 git diff 核对。

- □ python -m py_compile 通过。

- □ import test 通过。

- □ 该模块有最小可重复测试，随机算法设置了 seed。

- □ Hydra \_target\_ 和 \_\_init\_\_ 参数完全匹配。

- □ 单场景仿真在 AutoDL 真正运行过，而不是 AI 口头判断。

- □ Planner 输出能被现有 iLQR + KBM 接受。

- □ 没有新生成大文件塞满系统盘；大数据放 /root/autodl-tmp。

- □ git diff --check 通过。

- □ 改动已形成一个语义清晰的 Git commit。

- □ 我记录了运行命令、参数、场景和结果，之后能复现。

# **结语：把普通 AI 当“聪明但看不到云端的程序员”**

普通 AI 完全可以帮助你把 Pure MCTS 和 Neural-MCTS 做出来，但前提是你不给它“想象云端”的机会。你负责提供事实、执行命令、保存版本和判断实验；AI 负责阅读真实源码、提出最小改动、生成代码和解释错误。

> 事实来自 AutoDL  
> 代码通过 Git 管理  
> 接口以真实源码为准  
> 一步一测  
> 一错一包  
> 一里程碑一 commit

**遵守这六句话，即使以后换 DeepSeek、Kimi、豆包或其他基础模型，也能把同一个 MineSim 项目稳定地继续推进。**
