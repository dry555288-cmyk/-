**MineSim-Dynamic**

**云端项目完整交接与工作流手册**

**Pure MCTS 多车规划 + J117 真实地图接入 + 单车闭环验证**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>文档定位</strong></p>
<p>本文件依据用户上传的项目手册、2026-08-09 Codex 终端记录、云端 Git/代码输出、地图源数据审计、哈希与闭环测试结果整理。目标是：即使原对话中断，新的 AI 只要按本文的启动清单重新核验云端，就能在 5–10 分钟内理解当前项目、定位关键资产、避免破坏性操作，并从正确阶段继续。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

| **项目**      | **当前值 / 说明**                                                                                            |
|---------------|--------------------------------------------------------------------------------------------------------------|
| 证据截止      | 2026-08-09，已完成 Phase 4C-3 完整单车闭环（S2 -\> G1）                                                      |
| 正式仓库      | /root/MineSim-Dynamic                                                                                        |
| 预期当前分支  | newmap-j117-dev                                                                                              |
| 预期当前 HEAD | ec1c958735b0ee76201284faacb46fccc75c7f6c                                                                     |
| 当前核心状态  | J117 pilot HD Map 已被 production Map API 加载；minimal Scenario 已构造；IDM + iLQR + KBM 已全程安全到达目标 |
| 下一研究阶段  | 先固化 Phase 4C 结果与项目文档，再设计 Phase 5 双受控车辆 constructed conflict benchmark                     |

**重要：**本文是交接事实源，不是云端实时状态的替代品。任何 AI 接管时必须重新核验 Git、环境、文件哈希、当前进程与磁盘位置。

# 0. 五分钟接管摘要

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>30 秒结论</strong></p>
<p>MineSim-Dynamic 已从 IDM baseline 发展到 Pure MCTS、多车联合 MCTS 与 Dapai 双车时序协调证据；Jiangtong 经严格筛选后确认不具备天然近同时冲突。为获得第二个干净 benchmark，项目使用真实矿区 GeoJSON 构建 J117 pilot HD Map。该地图已完成 Raster/Semantic 转换、production Loader/Map API 加载、最小单车 Scenario 构造，并由默认 IDMPlanner + TwoStageController + iLQR + Kinematic Bicycle Model 完成 S2 -&gt; G1 全路线闭环：423 steps、42.3 s、全程可行驶、无异常。当前尚未在 J117 上运行双车 Pure MCTS。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

| **维度**      | **当前权威状态**                                                                                        |
|---------------|---------------------------------------------------------------------------------------------------------|
| 研究主线      | 露天矿无人矿卡闭环规划；核心创新仍是 Pure MCTS / multi-vehicle Fleet MCTS。                             |
| 新地图主线    | 真实 GeoJSON -\> J117 局部 HD Map -\> production Map API -\> minimal Scenario -\> 单车完整闭环。        |
| 正式 Git      | branch: newmap-j117-dev；HEAD: ec1c958735b0ee76201284faacb46fccc75c7f6c。                               |
| Phase 4C 结果 | goal reached = TRUE；423 steps；42.3 s；总路程 398.998 m；min clearance 1.5986 m。                      |
| 运行组件      | IDMPlanner -\> TwoStageController -\> iLQR tracker -\> Kinematic Bicycle Model；不是 MCTS。             |
| 地图身份      | geojson_j117_pilot；真实地图数据、局部 pilot、内部版本 pilot-geojson-j117-v1。                          |
| 关键限制      | 真实车辆型号、现场转向许可、源数据第三坐标 datum/unit 仍未知；当前采用 XG90G 集成别名与 2D flat model。 |
| 尚未完成      | 标准 run_simulation/ScenarioOrganizer 接入；Phase 5 双车 constructed benchmark；J117 上的 Pure MCTS。   |

## 0.1 新 AI 首次登录必须执行

**只读核验命令**

cd /root/MineSim-Dynamic \|\| exit 1  
conda activate minesim  
python --version  
  
git branch --show-current  
git rev-parse HEAD  
git status --short --branch  
git log -5 --oneline --decorate  
git tag --points-at HEAD  
  
ps -eo pid,stat,etimes,%cpu,%mem,args \| grep -E 'full_route_closed_loop\|MineSim\|python' \| grep -v grep \|\| true

预期看到 newmap-j117-dev @ ec1c958...，tracked/staged clean；但仓库存在历史未跟踪文件，不能把“git status 有 ??”误判为本轮修改。

## 0.2 绝对禁止的操作

- 不要在 /root/autodl-tmp/MineSim-Dynamic 副本上开发；正式仓库只有 /root/MineSim-Dynamic。

- 不要使用 git add .、git clean -fd、git reset --hard、rm -rf；重要 multi-ego 辅助代码、备份与异常文件名仍可能未跟踪。

- 不要把 J117 Phase 4C 说成 MCTS 成功；该阶段使用 IDMPlanner 验证地图/Scenario/控制链。

- 不要声称已经训练 Neural-MCTS；448 条专家样本只验证了数据管线，尚无正式神经网络训练结论。

- 不要把 J117 构造场景说成天然回放冲突；正确称谓是 real-map constructed benchmark。

- 不要擅自修复 gear=-1、road 332、12 条 missing-road-reference lane 或 road342 名称差异；pilot 已通过明确排除/保留差异来保证可追溯。

# 目录与阅读顺序

1.  1\. 项目定义、研究目标与系统边界

2.  2\. 事实源、证据等级与当前状态优先级

3.  3\. AutoDL 云端环境、Codex 与目录资产

4.  4\. Git 演进、分支、Commit 与 Tag

5.  5\. Pure MCTS / 多车 MCTS 的现有系统架构

6.  6\. 既有 benchmark 证据：五 Planner、Dapai 与 Jiangtong

7.  7\. 为什么构建 J117 新地图，以及源数据事实

8.  8\. J117 新地图全过程：Phase 1 到 Phase 4C

9.  9\. 当前 J117 地图、Scenario 与闭环的精确规格

10. 10\. 代码修改、外置脚本与关键资产索引

11. 11\. 全过程问题、根因、解决方法与经验

12. 12\. 用户当前工作流：AI + Codex + Git + AutoDL

13. 13\. 新 AI 云端接管 Runbook

14. 14\. 风险边界、Remaining UNKNOWN 与表达规范

15. 15\. 下一阶段路线图与决策门

16. 附录 A. 绝对路径索引

17. 附录 B. Commit / Tag / SHA256 速查

18. 附录 C. 可直接复制给新 AI 的接管 Prompt

19. 附录 D. 证据来源清单

# 1. 项目定义、研究目标与系统边界

## 1.1 一句话定义

MineSim-Dynamic 是面向露天矿非结构化道路自动驾驶矿卡的场景化闭环规划仿真项目。用户的核心研究主线是在已复现的 IDM + Replay 基础上实现 Pure MCTS，并进一步扩展为双受控车辆的联合搜索，以研究复杂冲突场景中的安全、任务完成与时序协调。

## 1.2 当前研究问题

- 单车层面：多步 MCTS 是否能在真实闭环中比反应式/采样式方法更一致地兼顾安全与到达目标？

- 多车层面：两个受控矿卡是否能在同一冲突区形成非规则硬编码的时序分离，而不是由外部 actor 或固定优先级主导？

- benchmark 层面：如何区分天然回放冲突、外部交通混杂和明确标注的 constructed benchmark？

- 地图层面：如何从真实 GIS/GeoJSON 资料构建 MineSim 可加载、可搜索、可闭环的 HD Map？

- 工程层面：如何在 0.5 CPU、2 GB RAM、无 GPU 的 AutoDL 实例上，以可追溯、可回退、低风险的方式推进长链路实验？

## 1.3 当前算法边界

| **项目**           | **当前定义**                                                                                             |
|--------------------|----------------------------------------------------------------------------------------------------------|
| 核心算法           | Pure MCTS；当前不存在正式 Value Network、Policy-Value Network 或 PUCT 训练结果。                         |
| 单车动作           | BRAKE / DECEL / KEEP / ACCEL 四个纵向动作。                                                              |
| 双车动作           | 4 x 4 = 16 个联合动作。                                                                                  |
| 正式多车搜索参数   | budget=300，depth=8，c_uct=1.4，gamma=0.99，seed=0。                                                     |
| 受控车辆耦合       | FleetState + FleetTransitionModel + FleetRewardModel；A/B 使用真实 footprint 几何耦合。                  |
| 外部车辆           | 作为 CV/CTRV 预测 actor 加入外部碰撞/清距，不是受控 MCTS agent。                                         |
| 安全机制           | hard geometry margin=0.5 m；internal clearance soft reward: safe=3.0 m, weight=0.5。                     |
| 坐标语义           | route progress 以 rear axle 定义；footprint 以 geometric center 构造，已完成 rear-axle -\> center 对齐。 |
| 当前 J117 单车验证 | 使用 IDMPlanner，而不是 MCTS，用于隔离地图、Scenario、Controller 和 vehicle model 的集成风险。           |

## 1.4 当前最重要的边界表达

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>严谨表述</strong></p>
<p>“J117 新地图的 production 加载、minimal Scenario 构造与单车 IDM 闭环已经通过；J117 上的双车 Pure MCTS 尚未开始。”这句话同时准确表达了完成项与未完成项。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 2. 事实源、证据等级与当前状态优先级

## 2.1 证据等级

| **标记**         | **含义**                                                          | **使用规则**                          |
|------------------|-------------------------------------------------------------------|---------------------------------------|
| \[V\] 已核验事实 | 由当前终端输出、Git、源码、哈希、生产 Loader 或闭环运行直接支持。 | 可作为当前事实；重连云端后仍需复核。  |
| \[D\] 数据推导   | 从已核验坐标、时间、几何、统计量计算得到。                        | 可用于分析；必须保留计算定义。        |
| \[DD\] 设计决策  | 为集成/实验明确选择的参数或范围。                                 | 不能冒充真实矿场事实。                |
| \[H\] 历史快照   | 旧 Word、旧分支、旧实验记录。                                     | 用于理解演进，不能覆盖当前 Git/代码。 |
| \[U\] 未知       | 当前资料不足或无权威语义。                                        | 不得静默填默认值。                    |

## 2.2 当前事实源优先级

20. 一级：/root/MineSim-Dynamic 当前 Git、源码与运行中的进程。

21. 二级：/root/autodl-tmp 中各 Phase 的 manifest、validation JSON、SHA256 与脚本。

22. 三级：本手册及 2026-08-09 最新交接文档。

23. 四级：2026-08-06 全景手册、2026-08-07 实验报告及更早 Word。

24. 最低：示例代码、旧说明中的假定字段或未在当前分支核验的 API。

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>为什么必须这样做</strong></p>
<p>项目历史中曾出现旧文档写“尚未开始 MCTS”，而云端实际上已经完成 Pure MCTS、448 条专家数据、多车联合搜索和正式实验。任何 AI 都必须把“当前云端”置于“旧文档”之上。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 3. AutoDL 云端环境、Codex 与目录资产

## 3.1 当前运行环境

| **项目**   | **值 / 规则**                                                                 |
|------------|-------------------------------------------------------------------------------|
| 正式仓库   | /root/MineSim-Dynamic                                                         |
| 正式 Conda | /root/miniconda3/envs/minesim；环境名 minesim                                 |
| Python     | 3.9.25（历史与当前生产链均以此为基准）                                        |
| 当前实例   | CPU-only；历史交接记录为 0.5 CPU、2 GB RAM、无 GPU；接管时重新核验            |
| 系统盘原则 | 系统盘已有用途；大型数据、地图产物、日志、工具、缓存全部优先 /root/autodl-tmp |
| 长任务原则 | 使用 screen 或可监控的后台任务；记录 PID、日志、进度文件，防止 SSH/Codex 中断 |

## 3.2 Codex CLI 安装与当前用法

| **项目**     | **当前事实**                                                                                              |
|--------------|-----------------------------------------------------------------------------------------------------------|
| Node         | v22.17.0，/root/autodl-tmp/nodejs/node                                                                    |
| npm          | 10.9.2；global=/root/autodl-tmp/npm-global；cache=/root/autodl-tmp/npm-cache                              |
| Codex CLI    | codex-cli 0.147.0；/root/autodl-tmp/npm-global/bin/codex                                                  |
| CODEX_HOME   | /root/autodl-tmp/codex-home                                                                               |
| 环境脚本     | /root/autodl-tmp/codex-env.sh；新 shell 先 source                                                         |
| Provider     | codexcn；base_url=https://api2.codexcn.com/v1                                                             |
| 认证         | Key 存于 /root/autodl-tmp/codex-home/auth.json 的 OPENAI_API_KEY 字段，不在 shell 环境变量；不得 cat/截图 |
| 当前成本模式 | 交互会话已切换为 gpt-5.6-luna medium；新会话需用 /model 再确认，配置默认值可能不同                        |

**Codex 启动**

source /root/autodl-tmp/codex-env.sh  
cd /root/MineSim-Dynamic  
codex  
\# 进入后：/model -\> gpt-5.6-luna -\> Medium

## 3.3 模型与额度策略

| **任务类型**                                            | **推荐模型**                                             |
|---------------------------------------------------------|----------------------------------------------------------|
| git status / stage / commit / tag、小范围脚本、常规测试 | gpt-5.6-luna medium                                      |
| 中等复杂 bug、多个模块联调                              | gpt-5.6-terra medium/high                                |
| MCTS 核心算法、复杂闭环故障、关键研究结论终审           | gpt-5.6-sol high                                         |
| 不需要模型的查询                                        | 直接 shell/curl/python，例如 /v1/models、sha256、ps、git |

成本控制经验：长会话会反复携带上下文；应把任务分成小门控阶段，已经验证的阶段不重跑，结果尽量写入短 manifest/summary，下一轮只引用路径和 PASS 状态。

## 3.4 关键目录与资产隔离

| **路径**                                  | **作用**                             | **操作规则**                                            |
|-------------------------------------------|--------------------------------------|---------------------------------------------------------|
| /root/MineSim-Dynamic                     | 唯一正式 Git 仓库                    | 源码修改、commit、tag；先 pwd；禁止把数据大文件塞进仓库 |
| /root/autodl-tmp/MineSim-Dynamic          | 历史副本                             | 不是正式仓库；暂勿删除，但禁止在此开发                  |
| /root/datasets/maps                       | 原 Dapai/Jiangtong production 地图根 | Phase 3 明确未修改                                      |
| /root/autodl-tmp/new_map_phase3_maps/maps | J117 shadow map root                 | Phase 3/4 direct harness 使用                           |
| /root/autodl-tmp/mcts_data                | MCTS/NN 数据规划目录                 | 大数据、样本、manifest                                  |
| /root/autodl-tmp/mcts_results             | 实验结果与日志                       | 每次正式结果应绑定 commit/参数/场景/seed                |
| /root/autodl-tmp/mcts_checkpoints         | 未来网络权重                         | 当前无正式 NN checkpoint                                |

# 4. Git 演进、分支、Commit 与 Tag

## 4.1 版本演进时间线

| **阶段**                        | **Branch / Commit**                                                      | **意义**                                                                       |
|---------------------------------|--------------------------------------------------------------------------|--------------------------------------------------------------------------------|
| 稳定 IDM baseline               | autodl-idm-baseline @ 2521aa41a69a6e734c04c15a715e9530c8095ac3           | 已知可运行锚点；tag idm-replay-autodl-baseline                                 |
| Pure MCTS / 五 Planner 正式结果 | fix-ilqr-determinism-20260731 @ 94693dc799fe5f325a75e8fc6d7d5e88764b4799 | 两场景 MCTS/IDM、448 专家样本、五 Planner 与 budget 结果基线                   |
| 多车 FleetRewardModel           | multi-mcts-dev @ f8ff1866789ed3d9d878f34b7cd34ab490e40121                | 内部连续安全距离 reward、Dapai 双车证据链                                      |
| Jiangtong V22 文档封存          | multi-mcts-dev @ 94794c963f9c3eaf1873b275df6d319ca2636817                | 更新 AI_HANDOFF/PROJECT_STATUS；tag jiangtong-v22-benchmark-screening-20260809 |
| J117 Map API 注册               | newmap-j117-dev @ 4bd2bff28c593ee80ab8c9fe2eefecd2b009e9b6               | 两个 Loader 最小注册；tag j117-phase3-production-map-load-20260809             |
| J117 minimal Scenario 支持      | newmap-j117-dev @ ec1c958735b0ee76201284faacb46fccc75c7f6c               | XG90G alias + no-agent horizon；tag j117-phase4b-minimal-scenario-20260809     |
| J117 Phase 4C 完整闭环          | 仍为 ec1c958；无 tracked 修改                                            | 外置 harness 证明单车闭环 PASS；尚未写入 tracked 项目文档/新 commit            |

## 4.2 当前 Git 真实状态

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>当前权威预期</strong></p>
<p>branch = newmap-j117-dev；HEAD = ec1c958735b0ee76201284faacb46fccc75c7f6c；tracked working tree clean；staged empty。Phase 4C 结果由外置脚本和终端输出支持，不对应新的代码 commit。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## 4.3 未跟踪文件风险

仓库长期存在一批历史未跟踪/备份文件。以下示例在多轮 status 中反复出现，接管 AI 不得清理：

- devkit/sim_engine/planning/planner/mcts/multi_ego_task.py

- devkit/sim_engine/planning/planner/mcts/multi_ego_task_builder.py

- devkit/sim_engine/planning/planner/mcts/test/test_multi_ego_task.py

- simulation_mode_mcts\_\*.yaml、\*.bak、\*.before_trajectory、run_simulation.py.bak、idm_planner.py.bak、mcts_planner.py.bak、reward.py.bak

- 异常名称：0:、=、math.pi、self.jerk_max、self.v_max

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>操作规则</strong></p>
<p>只允许逐文件 review 后使用精确 git add &lt;file1&gt; &lt;file2&gt;。任何阶段先做 git diff --check、git diff --name-only、git diff --cached --name-only；只有集合严格等于授权文件时才提交。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 5. Pure MCTS / 多车 MCTS 的现有系统架构

## 5.1 MineSim 闭环主链

**Production 闭环**

Scenario / HD Map  
-\> MineSimDynamicScenario  
-\> EnvironmentSimulation.initialize()  
-\> Planner.initialize()  
-\> while simulation is running:  
planner_input = get_planner_input()  
trajectory = planner.compute_trajectory()  
propagate(trajectory)  
-\> time_controller.next_iteration()  
-\> ego_controller.update_state()  
-\> observations.update_observation()

## 5.2 Pure MCTS 数据流

**多车 MCTS 架构**

Environment / observations  
-\> controlled A + controlled B + external actors  
-\> FleetState  
-\> Pure MCTS joint search (N=2: 16 joint actions)  
-\> FleetTransitionModel  
longitudinal dynamics  
route geometry / rear-axle semantics  
internal A-B geometry  
external CV/CTRV geometry  
-\> FleetRewardModel  
per-vehicle reward  
internal clearance soft penalty  
hard collision/safety penalty  
-\> best joint action  
-\> controller / vehicle model closed-loop execution

## 5.3 关键组件现状

| **组件**             | **现状 / 语义**                                                                         |
|----------------------|-----------------------------------------------------------------------------------------|
| MCTSPlanner          | 已实现单车闭环，并扩展 multi-ego runtime/adapter。                                      |
| FleetState           | 联合表示两个受控车辆状态。                                                              |
| FleetTransitionModel | 联合动作传播；受控车辆间不是固定 replay，而是真实几何耦合。                             |
| FleetRewardModel     | 包含内部连续安全距离 soft reward 与 hard safety penalty。                               |
| RouteGeometryCache   | 以 rear-axle route_s 查询，再平移到 geometric center 生成 footprint；防止坐标语义混用。 |
| Trajectory adapter   | 把选中纵向动作转为 MineSim 可执行轨迹，并交由 controller/iLQR/KBM 执行。                |
| Neural-MCTS          | 未开始正式训练；禁止声称已有网络。                                                      |

# 6. 既有 benchmark 证据：五 Planner、Dapai 与 Jiangtong

## 6.1 五 Planner 与预算结果（历史正式基线 94693dc）

| **Planner**             | **两场景 Safe Goal** | **碰撞帧** | **边界帧** | **解读**                                                 |
|-------------------------|----------------------|------------|------------|----------------------------------------------------------|
| MCTS                    | 2/2                  | 0          | 0          | 当前两场景中唯一同时完成 2/2 Safe Goal；不等于全局最优。 |
| IDM                     | 1/2                  | 21         | 0          | Jiangtong 完成；Dapai 碰撞且未到达；明显更快。           |
| Online Frenet           | 0/2                  | 0          | 0          | 保守但未到达；只看碰撞会高估。                           |
| Online Adapted Maneuver | 0/2                  | 67         | 0          | 评价的是当前适配版，不代表原算法总体。                   |
| Simple                  | 0/2                  | 0          | 90         | 仅作为能力下限，不属于公平主比较。                       |

Budget 50/100/200/300 消融显示：Dapai 对预算敏感，Jiangtong 在低预算已接近饱和；固定 300 可能存在状态无关的计算冗余。这一现象曾指向 adaptive budget / tree reuse / value network，但后来优先级被“缺少第二个干净多车 benchmark”取代。

## 6.2 Dapai 多车机制证据

| **实验**                | **结果**                       | **关键量**                                                                                  | **研究结论**                             |
|-------------------------|--------------------------------|---------------------------------------------------------------------------------------------|------------------------------------------|
| v14 tree mechanism      | 深层树分支 soft clearance 激活 | hard coupling 改变联合策略；soft reward 进一步抑制同步加速                                  | 约束在树内提前影响决策，不只是执行后修正 |
| v15 A-B only            | B 先过，A 后过                 | projected ETA diff≈0.332 s；B step49；A step71；min actual=8.4586 m；min predicted=7.8702 m | 正式双受控时序协调证据                   |
| v16 + object1 + object3 | 目标交互被提前打断             | A/B 无碰撞但未形成目标先后通过                                                              | 外部交通混杂，不能解释为协同成功         |
| v17 + object3           | 与 v15 几乎一致                | B step49；A step71                                                                          | object3 不是主要混杂                     |
| v18 + object1           | 复现 preemption                | B 早期反复 BRAKE；mean search≈1747 ms                                                       | object1 是 dominant external confounder  |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>关键研究判断</strong></p>
<p>不要继续调 reward 迫使 full-external Dapai “一定通过”。那会把 benchmark 设计问题误当成算法问题。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## 6.3 Jiangtong V22 负结果与封存

| **量**                  | **结果**                             |
|-------------------------|--------------------------------------|
| authoritative ego route | path-94 -\> path-100 -\> path-117    |
| 唯一真实空间交叉 actor  | Traj 26 / PickupTruck_GreatWall_POER |
| 冲突点                  | (1371.406141532, 2285.739827170)     |
| actor 记录到达时间      | 2.592884522 s                        |
| ego 最早可达 ETA        | 12.088970414 s                       |
| signed ETA difference   | +9.496085891 s                       |
| 空间冲突                | YES                                  |
| 天然近同时冲突          | NO                                   |

**结论：**Jiangtong 不适合作为第二个天然多车冲突 benchmark；不得通过 StartTime、初速度、轨迹、route、reward、margin、budget、depth 或 seed 强行制造冲突。该结论已在 94794c9 文档 commit 与 annotated tag 中封存。

# 7. 为什么构建 J117 新地图，以及源数据事实

## 7.1 研究动机

Dapai 已有较强多车机制证据，但 full-external 存在 object1 混杂；Jiangtong 仅有空间交叉，没有时间冲突。当前本地 canonical 场景目录与 Git/归档资产审计后仍只有 Dapai、Jiangtong 两个唯一场景。因此项目转向：用真实矿区 GeoJSON 构建一张新地图，并在其上设计明确标注的 constructed conflict benchmark。

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>正确定位</strong></p>
<p>地图几何来自真实源数据；车辆起点、目标和未来双车近同时到达时序属于实验设计。论文中应称 real-map constructed benchmark，而不是 natural replay benchmark。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## 7.2 源 ZIP 与图层

| **成员**              | **Feature 数 / 类型**                    | **用途**                                  |
|-----------------------|------------------------------------------|-------------------------------------------|
| 1.png                 | 1799 x 1050 RGB preview                  | 仅作预览，不能作为二值 mask               |
| junction.geojson      | 35 Polygon                               | intersection / polygon                    |
| lane.geojson          | 553 LineString                           | reference_path / connector / topology     |
| road.geojson          | 94 Polygon（93 valid + road332 invalid） | road / polygon / drivable source          |
| road_boundary.geojson | 100 MultiLineString                      | road borderline source                    |
| rgn_boundary.geojson  | 84 MultiLineString                       | junction/region borderline source         |
| rng_load.geojson      | 36 Polygon                               | loading region；pilot 不整区设为 drivable |
| rgn_unload.geojson    | 7 Polygon                                | unloading region；同上                    |
| rgn_auxiliary.geojson | 6 Polygon                                | auxiliary region；同上                    |

源 archive 路径：/root/autodl-tmp/地图新建相关文件.zip；SHA256 = 1e499fd92d3d76ae7167960d492e8760fc8aa7b73180458c0e90aefa07e1a44d。所有 GeoJSON 声明 EPSG:4326。

## 7.3 源数据已核验的重要事实

- 全数据经纬度范围约 91.86017331–91.91806106 E、44.39940097–44.43691009 N；全部落在 UTM 46N。

- lane object_id 全部唯一；553 条 LineString 全部有效。

- pr_toponode_id -\> LineString first endpoint、su_toponode_id -\> last endpoint 的共享节点支持率均为 100%。

- 这只证明 stored topology orientation，不自动等于真实运营方向；50 条 gear=-1 lane 的业务语义未被权威说明。

- rgn_type 1/2/3/4 与 junction/loading/unloading/auxiliary 通过 rgn_objectid 完整匹配；rgn_type=0 有 12 条 lane 引用缺失 road Polygon。

- road 332 存在真实 self-intersection；buffer(0) 会把 Polygon 变成 MultiPolygon，故不能自动修复。

- loading/unloading/auxiliary 的 lane corridor 结构有支持，但整块 Polygon 可行驶无证据。

## 7.4 Pilot 选择

| **项目**             | **J117 / C#236**                                                        |
|----------------------|-------------------------------------------------------------------------|
| junction object_id   | 117                                                                     |
| 真实 route A         | 6670 -\> 6674 -\> 5690                                                  |
| 真实 route B         | 5691 -\> 6546 -\> 6523                                                  |
| 交叉角               | 约 62.006°                                                              |
| 最小可追溯 approach  | 411.695 m                                                               |
| 最小可追溯 departure | 360.900 m                                                               |
| connector            | 6674、6546；均真实属于 junction117                                      |
| 冲突点               | EPSG:32646 (412078.088786846, 4919599.656085037)                        |
| 源缺陷隔离           | 不涉及 gear=-1、road332、missing-road lane、loading/unloading/auxiliary |

# 8. J117 新地图全过程：Phase 1 到 Phase 4C

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>总流程</strong></p>
<p>Real GeoJSON audit -&gt; semantics resolution -&gt; design freeze -&gt; temporary Raster/Semantic build -&gt; independent validation -&gt; production Map API -&gt; minimal Scenario -&gt; 1-step smoke -&gt; 5-second loop -&gt; full-route closed loop。每一阶段通过后才进入下一阶段。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## 8.1 Phase 1：真实源数据审计

目标：不生成地图、不改正式仓库，只回答“源数据是否足够、各字段能否映射、哪个交叉口最适合 pilot”。

| **产物**   | **路径**                                                       |
|------------|----------------------------------------------------------------|
| 审计报告   | /root/autodl-tmp/new_map_phase1_audit_20260809.md              |
| 图层统计   | /root/autodl-tmp/new_map_phase1_layer_stats_20260809.json      |
| 拓扑统计   | /root/autodl-tmp/new_map_phase1_topology_stats_20260809.json   |
| pilot 候选 | /root/autodl-tmp/new_map_phase1_pilot_candidates_20260809.json |
| 工具       | /root/autodl-tmp/new_map_phase1_tools/new_map_phase1_audit.py  |

关键结果：EPSG:32646 可作为 benchmark 标准米制投影；J117 为 TOP1；正式仓库 tracked/staged diff=0。

## 8.2 Phase 1.5：关键语义消歧

| **未知/缺陷**               | **结论与处理**                                                                |
|-----------------------------|-------------------------------------------------------------------------------|
| gear=-1                     | UNRESOLVED；production 不读取该字段；pilot 只用 gear=1 lane                   |
| road332                     | NEEDS_MANUAL_REVIEW；距 pilot 约 1.4 km；pilot 排除                           |
| 12 条 missing-road lane     | 对应 boundary 存在，推导为缺失 Polygon likely；pilot 排除，不自动重挂         |
| loading/unloading/auxiliary | full polygon drivable unsupported；lane corridor structurally supported       |
| J117 Route A/B              | 全部 gear=1、topology 连续、真实 connector、内部 Point 相交；READY_FOR_PHASE2 |

## 8.3 Phase 2 Design Freeze

| **冻结项**    | **值**                                                                          |
|---------------|---------------------------------------------------------------------------------|
| CRS           | EPSG:32646 / WGS84 UTM 46N                                                      |
| local origin  | E0=409200.0, N0=4916800.0；x=E-E0, y=N-N0                                       |
| pilot content | road 471 + road 385 + road 342 + junction117                                    |
| crop          | local x=\[2454.5,2939.3\], y=\[2721.7,2986.0\]                                  |
| scale/layout  | 10 px/m；normal layout                                                          |
| Raster size   | 4848 x 2643                                                                     |
| waypoint      | preserve source vertices；nominal interval 0.2 m                                |
| yaw           | centered unit tangent；range \[0,2pi)                                           |
| height/slope  | 0.0 / 0.0；2D flat pilot design decision                                        |
| borderline    | FACT source boundary only；9 components                                         |
| tokens        | suffix == array index；10685 nodes, 4 polygons, 6 paths, 8 poses, 9 borderlines |

Design Freeze 文件：/root/autodl-tmp/new_map_phase2_design_freeze_20260809.md / .json；PHASE2_DESIGN_FREEZE_PASS=TRUE。

## 8.4 Phase 2 Conversion Build

| **项目**            | **结果**                                                                               |
|---------------------|----------------------------------------------------------------------------------------|
| Bitmap              | /root/autodl-tmp/new_map_phase2_j117/bitmap/geojson_j117_pilot_bitmap_mask.png         |
| Semantic            | /root/autodl-tmp/new_map_phase2_j117/semantic_map/geojson_j117_pilot_semantic_map.json |
| Bitmap SHA          | 65fb1c88196468a4b7640d5c82bf854807d0ab93716d26f1f9f8cd4704245ac4                       |
| Semantic SHA        | 1aef7e1054fb8f54004ee96fbd4e7afc984180c52735446cb0224d79e4286afa                       |
| Raster validation   | correct IoU=1.0；centroid error≈0.001 m；NO_MIRROR/TRANSLATION/ROTATION/SCALE_MISMATCH |
| Semantic validation | 29 项关键检查全部 PASS；token/index/reference/topology/source traceability 均通过      |
| 状态                | PHASE2_PILOT_CONVERSION_PASS=TRUE                                                      |

## 8.5 Phase 3：Production Map API

将 Phase 2 两个 artifact 复制到 shadow root /root/autodl-tmp/new_map_phase3_maps/maps，并只对两个 Loader 做最小 location/version 注册。

| **代码文件**                       | **修改**                                                      |
|------------------------------------|---------------------------------------------------------------|
| minesim_bitmap_png_loader.py       | geojson_j117_pilot -\> geojson_j117_pilot_bitmap_mask         |
| minesim_semanticmap_json_loader.py | 新增 location、semantic hash 与 pilot-geojson-j117-v1 version |

production get_maps_api()、31 个 token 查询、4 个 Polygon 重建、6 个 path object、8 个 pose、pure graph、bitmap crop 与点测试全部 PASS；exception=0。Commit 4bd2bff，tag j117-phase3-production-map-load-20260809。

## 8.6 Phase 4A：Minimal Scenario Preflight

| **问题**        | **核验结果**                                                                                                                          |
|-----------------|---------------------------------------------------------------------------------------------------------------------------------------|
| Scenario schema | 顶层固定为 SceneName, SceneType, dt, CntVehicle, TrajSegmentInfo, bounds, max_t, goal, ego_info；无 location/link_map/static_obstacle |
| location 来源   | 由 Scenario 文件名映射；standard ScenarioOrganizer 当前只支持 dapai/jiangtong                                                         |
| vehicle 参数    | 按 location factory 获取；pilot 当前需显式 alias                                                                                      |
| no-agent        | TrajSegmentInfo=\[\] 原本只生成 1 帧，iteration 0 reached_end                                                                         |
| 车型几何        | Route A: XG90G/NTE200 均适配；Route B: NTE200 approach 需复核                                                                         |
| 推荐            | Route A；S2 start；G1 goal；首次集成用 XG90G                                                                                          |

## 8.7 Phase 4B：Minimal Scenario Build

| **冻结设计**       | **值**                                                                                            |
|--------------------|---------------------------------------------------------------------------------------------------|
| 车辆               | XG90G（集成 alias，不代表真实矿区车型）                                                           |
| 路线               | Route A: 6670 -\> 6674 -\> 5690 / path-0 -\> path-1 -\> path-2                                    |
| 起点 S2            | route_s=146.5630523455206；rear axle=(2633.3256179327054, 2808.0365124886757, 6.2253828755975595) |
| 目标中心 G1        | route_s=553.3376665446767；(2779.0722681073316, 2883.2362333456595, 3.0948698977503604)           |
| goal polygon       | 14 x 8 m CCW rectangle；strict point containment；不要求停车                                      |
| dt / speed / max_t | 0.1 s / 4.5 m/s / 150 s                                                                           |
| no-agent horizon   | 1501 frames；active step 0..1499；step1500 terminal sentinel                                      |

Scenario：/root/autodl-tmp/new_map_phase4b_j117/inputs/Scenario-geojson_j117_pilot_minimal_route_a.json；SHA256=6581c351fdf945d88166a63e2ea1497522548339a37ef2896e7df3df225a91d8。

Committed code: vehicle_parameters.py 对 pilot alias 到 XG90G；minesim_dynamic_scenario.py 在无 agent 时使用 max_t 构造空帧。Commit ec1c958，tag j117-phase4b-minimal-scenario-20260809。

## 8.8 Phase 4C：闭环分级验证

| **阶段**             | **结果**                                                                   | **意义**                              |
|----------------------|----------------------------------------------------------------------------|---------------------------------------|
| 4C-1：1 step         | 17 点 finite trajectory；propagate PASS；前进 0.45 m；drivable             | Planner/Controller/Model 首次真实联通 |
| 4C-2：50 steps / 5 s | 34.72 m；v 4.5-\>8.94；min clearance 3.527 m；全程 drivable                | 连续控制无快速发散                    |
| 4C-3：Full route     | 423 steps；42.3 s；398.998 m；goal reached；min clearance 1.5986 m；无异常 | J117 单车 production 闭环完成         |

# 9. 当前 J117 地图、Scenario 与闭环的精确规格

## 9.1 地图对象映射

| **MineSim token**          | **真实 source**                                                          |
|----------------------------|--------------------------------------------------------------------------|
| polygon-0 / intersection-0 | junction 117 / C#236                                                     |
| polygon-1 / road-0         | road 471 / R#1014                                                        |
| polygon-2 / road-1         | road 385 / R#910                                                         |
| polygon-3 / road-2         | road 342 / R#805                                                         |
| path-0                     | lane 6670 / base_path                                                    |
| path-1                     | lane 6674 / connector_path                                               |
| path-2                     | lane 5690 / base_path                                                    |
| path-3                     | lane 5691 / base_path                                                    |
| path-4                     | lane 6546 / connector_path                                               |
| path-5                     | lane 6523 / base_path                                                    |
| dubinspose-0..7            | topo 7956,7959,7953,6443,6442,7954,7797,7950                             |
| borderline-0..8            | 3 road_boundary records的6个 component + rgn_boundary 419的3个 component |

## 9.2 Scenario JSON

**最小 Schema 语义**

SceneName / SceneType  
dt = 0.1  
CntVehicle = 0  
TrajSegmentInfo = \[\]  
x_min/x_max/y_min/y_max = full frozen pilot local range  
max_t = 150.0  
goal = 14 x 8 m CCW polygon around G1  
ego_info.start_states = S2 rear-axle pose, v=4.5, yawrate=0, acc=0

Standard ScenarioOrganizer 尚未注册 geojson_j117_pilot\_ 前缀，且标准 run_simulation.main 会把 MINESIM_MAPS_ROOT 覆盖为 /root/datasets/maps。因此 Phase 4 使用 direct shadow-root harness，而不是标准 runner。

## 9.3 Phase 4C-3 完整闭环结果

| **指标**               | **结果**                                                              |
|------------------------|-----------------------------------------------------------------------|
| goal reached           | TRUE                                                                  |
| steps / simulated time | 423 / 42.3 s                                                          |
| start                  | x=2633.3256179, y=2808.0365125, yaw=6.2253829, v=4.5                  |
| final                  | x=2785.8772663, y=2882.9416894, yaw=3.0980735, v=4.2038865            |
| total distance         | 398.9976494 m                                                         |
| speed range            | 4.2038865–10.4068018 m/s                                              |
| min clearance          | 1.59859246 m                                                          |
| path transitions       | step0 path-0；step232 path-1；step287 path-2                          |
| final path progress    | 402.8713915 m                                                         |
| goal semantics         | rear-axle point strictly contained in PlanningProblemGoalTask polygon |
| drivable               | TRUE for all checked steps                                            |
| exceptions             | NONE                                                                  |
| repo diff              | tracked=0, staged=0                                                   |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>重要解释</strong></p>
<p>Phase 4C PASS 证明新地图、Scenario、IDM 规划、iLQR 控制和车辆模型能完整闭环；它没有证明 J117 上的 Pure MCTS，更没有证明双车协同。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 10. 代码修改、外置脚本与关键资产索引

## 10.1 已提交的正式代码修改

| **Commit** | **文件**                           | **修改边界**                                               |
|------------|------------------------------------|------------------------------------------------------------|
| 4bd2bff    | minesim_bitmap_png_loader.py       | 只增加 pilot bitmap 映射                                   |
| 4bd2bff    | minesim_semanticmap_json_loader.py | 只增加 pilot location/semantic/version 映射                |
| ec1c958    | vehicle_parameters.py              | pilot location 归一到 guangdong_dapai / XG90G 分支         |
| ec1c958    | minesim_dynamic_scenario.py        | 无 dynamic metadata 时，max_track_time_s 取 Scenario max_t |

## 10.2 外置脚本（不在正式 Git）

| **阶段**       | **脚本 / 目录**                                                       |
|----------------|-----------------------------------------------------------------------|
| Phase 1        | /root/autodl-tmp/new_map_phase1_tools/                                |
| Phase 1.5      | /root/autodl-tmp/new_map_phase1_5_tools/                              |
| Phase 2 design | /root/autodl-tmp/new_map_phase2_design_tools/                         |
| Phase 2 build  | /root/autodl-tmp/new_map_phase2_build_tools/build_j117_pilot.py       |
| Phase 3 tests  | /root/autodl-tmp/new_map_phase3_tools/test_j117_production_map_api.py |
| Phase 4A       | /root/autodl-tmp/new_map_phase4a_tools/                               |
| Phase 4B       | /root/autodl-tmp/new_map_phase4b_tools/build_and_test_phase4b.py      |
| Phase 4C-1     | /root/autodl-tmp/new_map_phase4c_tools/first_closed_loop_smoke.py     |
| Phase 4C-2     | /root/autodl-tmp/new_map_phase4c_tools/short_closed_loop_5s.py        |
| Phase 4C-3     | /root/autodl-tmp/new_map_phase4c_tools/full_route_closed_loop.py      |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>当前证据持久化风险</strong></p>
<p>Phase 4C-3 脚本把最终 JSON 打印到终端，当前记录主要存在 Codex transcript/本 Word 中；未看到专门的 result JSON 写入云端。下一步应先把完整结果持久化为 /root/autodl-tmp 下的 JSON/MD，并更新 tracked AI_HANDOFF.md / PROJECT_STATUS.md。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## 10.3 当前应优先备份的外置资产

- /root/autodl-tmp/地图新建相关文件.zip

- /root/autodl-tmp/new_map_phase1\_\* 与 new_map_phase1_5\_\*

- /root/autodl-tmp/new_map_phase2_design_freeze_20260809.\*

- /root/autodl-tmp/new_map_phase2_j117/

- /root/autodl-tmp/new_map_phase3_maps/maps/ 与 new_map_phase3_j117/

- /root/autodl-tmp/new_map_phase4a_preflight_20260809.\*

- /root/autodl-tmp/new_map_phase4b_j117/ 与 new_map_phase4b_tools/

- /root/autodl-tmp/new_map_phase4c_tools/

# 11. 全过程问题、根因、解决方法与经验

本节不是简单错误列表，而是把“症状 -\> 根因 -\> 解决 -\> 可复用经验”整理为接管 AI 的故障手册。

| **类别**  | **问题 / 症状**                                           | **解决方法**                                                                                | **可复用经验**                                          |
|-----------|-----------------------------------------------------------|---------------------------------------------------------------------------------------------|---------------------------------------------------------|
| 环境      | 系统盘小，Node/npm/Codex 默认会写系统盘                   | 安装包、global、cache、CODEX_HOME 全部放 /root/autodl-tmp；环境脚本统一 PATH                | 大型依赖/缓存先设计落盘位置，再安装                     |
| 环境      | AutoDL 无 Node/npm                                        | 下载 Node 22.17.0 x64 tar 到数据盘，设置 npm prefix/cache，再安装 @openai/codex             | 优先便携安装，避免 apt/系统盘污染                       |
| Codex     | bwrap: no permissions to create namespace                 | 只对明确只读/低风险命令逐次批准在 sandbox 外执行；不改 kernel sysctl                        | 容器限制不是项目错误；审批最窄权限                      |
| Codex     | Key 环境变量为空但 Codex 可用                             | 发现 Key 在 CODEX_HOME/auth.json；安全读取字段，不 cat/截图                                 | 认证文件与 shell env 要区分                             |
| Codex     | Python urllib 请求 /v1/models 返回 Cloudflare 1010        | 改用 curl + User-Agent，并临时从 auth.json 读取 key                                         | 不调用模型的接口查询应直接 shell，避免烧额度            |
| 成本      | Sol high 长会话消耗快                                     | 查询可用模型后切 gpt-5.6-luna medium；Sol 仅用于难题                                        | 按任务分层选模型；小任务不用前沿模型                    |
| 成本      | /model gpt-5.4-mini 口头显示切换但状态栏仍 Sol            | 以 /model picker 的 current 标记和底部状态为准；选择 Luna                                   | 模型状态以 UI current 为事实，不信自然语言回复          |
| 项目路径  | 误把 /root/autodl-tmp/MineSim-Dynamic 当正式仓库          | 以 .git 与项目手册核验，固定 /root/MineSim-Dynamic 为唯一正式仓库                           | 每次第一条命令 pwd + git rev-parse --show-toplevel      |
| 文档      | 旧 handoff 仍写 MCTS 未开始                               | 用当前 Git/源码更新 AI_HANDOFF/PROJECT_STATUS；旧文档降级为历史快照                         | 事实源必须有时间戳和优先级                              |
| Git       | 大量重要 untracked 与备份                                 | 禁止 git clean/add .；逐文件 stage review、commit、tag                                      | 工作区“脏”不等于可以清理                                |
| benchmark | 旧五 Planner 信息流不完全公平                             | 区分 CURRENT_OBSERVATION、oracle future、能力下限；主比较谨慎解释                           | 先审计信息流，再做排名                                  |
| benchmark | Dapai full external 不形成目标 A-B 协调                   | 四条件归因识别 object1 为 dominant confounder                                               | 不要靠调 reward 把场景问题变成算法“成功”                |
| benchmark | Jiangtong 有空间交叉但无时间冲突                          | Step2B 计算真实 actor arrival 与 ego earliest ETA；差 +9.496 s                              | 空间冲突与时序冲突必须分开                              |
| 地图      | 1.png 看似地图但不是 mask                                 | 仅作 preview；从真实 road/junction Polygon 栅格化 0/1 mask                                  | 展示图不能替代可复现栅格                                |
| 地图      | GeoJSON 是 EPSG:4326，经纬度不能直接当米                  | 投影 EPSG:32646，冻结 E0/N0 局部坐标                                                        | Raster/Semantic/Scenario 必须共用同一坐标定义           |
| 地图      | road332 Polygon self-intersection                         | 诊断 buffer(0) 会变 MultiPolygon；pilot 排除，等待权威修复                                  | 几何“可修”不等于语义可自动修                            |
| 地图      | 12 条 lane 引用缺失 road Polygon                          | 发现对应 boundary，推断源 Polygon 缺失；pilot 排除，不挂最近 road                           | 距离最近不是拓扑证据                                    |
| 地图      | gear=-1 语义未知                                          | 源码/文档无权威解释；pilot 只用 gear=1                                                      | 字段名不能替代数据规范                                  |
| 地图      | loading/unloading/auxiliary 整区可行驶无证据              | 只认 lane corridor 结构支持；pilot 不纳入整区                                               | 真实作业区不等于自由行驶面                              |
| 地图      | road342 Polygon 与 boundary 名称不一致                    | 按 road_objectid 与 bbox 保持关联，同时记录 SOURCE_NAME_MISMATCH                            | 保留源差异，不擅自改名                                  |
| 边界      | 真实 boundary 在 region 接口处开放                        | 验证开放段由另一个真实 region 支持；不补画、不闭合                                          | 开放接口是语义，不是“缺线”                              |
| Phase2    | Pillow DecompressionBombError 扫描超大可信 production PNG | 临时脚本解除像素上限，仅用于本地可信资产                                                    | 安全保护可按可信边界局部调整，不改 production           |
| Phase2    | Shapely 对 1281 万像素逐点 contains 太慢                  | 改用 rasterio.features.rasterize，保持相同几何/分辨率                                       | 选择标准矢量栅格化工具，避免 O(N pixels x complex geom) |
| Phase2    | Path.write_text(newline=...) 在 Python 3.9 报错           | 移除不支持参数，完整重跑保证同一批 artifacts/hashes                                         | 兼容性修复后要整批重建                                  |
| Phase2    | 像素中心极值与矢量尖端差 0.125 m 误判平移                 | 用像素单元 footprint bbox 判断；保留 center warning                                         | 验证指标必须符合离散栅格语义                            |
| Scenario  | no-agent 只有 1 帧，iteration0 立即结束                   | 无 metadata 时按 max_t 生成 0..150.0 共 1501 帧，最后帧为 sentinel                          | 时间控制的 frame/active-step 语义要显式核验 off-by-one  |
| Scenario  | 标准 runner 不识别 geojson 文件名前缀且覆盖 maps root     | Phase4 使用 direct shadow-root harness；标准集成留后续                                      | 先验证核心对象，再改公共入口                            |
| Scenario  | 真实车辆型号未知                                          | pilot location 暂时 alias 到 XG90G，明确为 integration design decision                      | 集成车型不等于矿场事实                                  |
| Goal      | 目标成功语义不清                                          | 读 PlanningProblemGoalTask，确认 strict point containment、不要求停车；设计 14x8 m CCW goal | 先读 production success semantics，再设计目标           |
| Harness   | numpy.int64 无法 JSON 序列化                              | 临时 harness 将 NumPy scalar 转 Python scalar；不改 production                              | 报告层问题与算法层问题要分离                            |
| Harness   | InterpolatedPath 无 get_progress_at_point                 | 使用现有 get_nearest_arc_length_from_position                                               | 先查现有 API，避免发明接口                              |
| 长任务    | 完整闭环无中间输出，难判断进度                            | 用 ps 的 CPU TIME/STAT/RSS 判断仍在计算；以后每 N step 写 progress file                     | 长任务必须可观测                                        |
| 长任务    | 同一 full-route 启动出两个进程                            | ps 识别 PID，仅 kill 较早重复进程，保留当前测试                                             | 不要 killall；只终止明确重复进程                        |
| 模型      | 长线程 context compacted / capacity interrupt             | 从已完成阶段恢复，不重跑；把阶段结果写入文件                                                | 上下文中断不等于技术失败                                |

# 12. 用户当前工作流：AI + Codex + Git + AutoDL

## 12.1 标准门控式工作流

| **步骤**            | **执行方式**                                                                                   |
|---------------------|------------------------------------------------------------------------------------------------|
| 1\. 定义唯一目标    | 一次只解决一个明确问题；先写禁止事项和输出边界。                                               |
| 2\. 只读 Preflight  | 核验 branch/HEAD/status、路径、API、字段与现有产物；不立即改代码。                             |
| 3\. 事实分类        | 每个结论标为 FACT / DERIVED / DESIGN DECISION / UNKNOWN。                                      |
| 4\. Design Freeze   | 在生成/修改前冻结坐标、参数、source scope、token、目标与验收条件。                             |
| 5\. 数据盘 Build    | 脚本、地图、日志、manifest 只写 /root/autodl-tmp；正式 repo 保持 clean。                       |
| 6\. 独立验证        | strict JSON、hash、geometry、topology、raster orientation、source traceability。               |
| 7\. Production 验证 | 让 MineSim 自己的 Loader/Map API/Scenario/Controller 使用 artifact，而不是只信自写 validator。 |
| 8\. 逐级运行        | schema -\> production load -\> Scenario -\> 1 step -\> 5 s -\> full route。                    |
| 9\. Git review      | diff --check -\> 精确 stage -\> cached review -\> commit -\> tag。                             |
| 10\. 文档封存       | 更新 handoff/status，记录路径、SHA、参数、失败与下一门。                                       |

## 12.2 每轮 Codex Prompt 的推荐结构

**Prompt 模板**

任务名称 / 当前阶段  
已冻结事实与路径  
本轮唯一目标  
允许修改的文件（精确列表）  
禁止操作  
需要执行的最小检查/测试  
PASS/FAIL 标准  
最终只输出的字段  
执行完停止，不自动进入下一阶段

## 12.3 为什么这个工作流有效

- 减少 AI 把历史计划误当成当前事实。

- 把地图、Scenario、Planner、Controller 的故障域拆开，错误定位更清楚。

- 外置大数据与临时脚本，保护系统盘和 Git 历史。

- 每个重要节点有 commit/tag，可安全回退。

- 通过小规模 smoke 降低 0.5 CPU 上的无效长运行。

- 严格结果字段减少大模型上下文与额度消耗。

# 13. 新 AI 云端接管 Runbook

## 13.1 第一轮只读检查

**接管命令**

cd /root/MineSim-Dynamic \|\| exit 1  
conda activate minesim  
  
echo "ENV=\$CONDA_DEFAULT_ENV"  
python --version  
pwd  
git rev-parse --show-toplevel  
git branch --show-current  
git rev-parse HEAD  
git status --short --branch  
git log -8 --oneline --decorate  
git tag --points-at HEAD  
  
ls -ld /root/autodl-tmp/new_map_phase2_j117 /root/autodl-tmp/new_map_phase3_maps/maps /root/autodl-tmp/new_map_phase4b_j117 /root/autodl-tmp/new_map_phase4c_tools  
  
ps -eo pid,stat,etimes,%cpu,%mem,args \| grep -E 'full_route_closed_loop\|MineSim\|python' \| grep -v grep \|\| true

## 13.2 预期值与偏差处理

| **检查**           | **预期**                                 | **若不一致**                                    |
|--------------------|------------------------------------------|-------------------------------------------------|
| branch             | newmap-j117-dev                          | 停止修改，读取 git log/branch，确认是否有人推进 |
| HEAD               | ec1c958735b0ee76201284faacb46fccc75c7f6c | 不要 reset；先审计后续 commit                   |
| tracked diff       | empty                                    | 逐文件报告，判断是否是用户新工作                |
| staged diff        | empty                                    | 不要覆盖；先 git diff --cached                  |
| Conda              | minesim                                  | 不要在 base 跑生产测试                          |
| Python             | 3.9.25                                   | 核验依赖兼容                                    |
| shadow maps        | 存在且 hashes 未变                       | 停止运行，先恢复 artifact                       |
| full-route process | 通常无                                   | 若有，查看 PID/CPU TIME/输出，不 killall        |

## 13.3 接管后先读的文件

- 本 Word（当前总览）

- /root/MineSim-Dynamic/AI_HANDOFF.md 与 PROJECT_STATUS.md（注意它们可能还未更新到 Phase 4C）

- /root/autodl-tmp/new_map_phase2_design_freeze_20260809.json

- /root/autodl-tmp/new_map_phase2_j117/conversion_manifest.json

- /root/autodl-tmp/new_map_phase3_j117/report/new_map_phase3_j117_report.md

- /root/autodl-tmp/new_map_phase4b_j117/report/new_map_phase4b_j117_report.md

- /root/autodl-tmp/new_map_phase4c_tools/full_route_closed_loop.py

## 13.4 不要立即重跑的昂贵步骤

- Phase 1 全 GeoJSON 审计

- Phase 2 全量 map build / production PNG 全扫描

- Phase 4C full-route 423-step 闭环（在弱 CPU 上约 1.5 小时 wall-clock）

- Dapai/Jiangtong 全 benchmark 和 MCTS budget 消融

**先验证现有 artifacts/hashes；**只有结果文件缺失、哈希不一致或代码发生变化时才重跑。

# 14. 风险边界、Remaining UNKNOWN 与表达规范

## 14.1 仍然未知 / 未完成

| **项目**                          | **状态与影响**                                          |
|-----------------------------------|---------------------------------------------------------|
| 新矿区真实车型                    | UNKNOWN；XG90G 仅为 minimal integration alias。         |
| 现场转向许可                      | UNKNOWN；source topology/geometry 不等于运营许可。      |
| 第三坐标 datum/unit               | UNKNOWN；保留统计但 height/slope=0。                    |
| 全矿区转换                        | 未做；当前仅 J117 pilot crop。                          |
| road332 / missing roads / gear=-1 | pilot 外仍未解决。                                      |
| 标准 runner                       | ScenarioOrganizer 前缀与 map root override 尚未接入。   |
| J117 Pure MCTS                    | 未运行。                                                |
| J117 双车 benchmark               | 未构造。                                                |
| Phase4C 持久结果文件              | 未明确存在；终端输出已核验，建议补写 JSON/文档 commit。 |
| Neural-MCTS                       | 未训练；448 样本不足以支撑网络结论。                    |

## 14.2 论文/汇报中可以说什么

- Pure MCTS 在 Dapai/Jiangtong 两个历史场景中获得 2/2 Safe Goal（限定场景）。

- Dapai A-B-only 显示联合 MCTS 可形成 B 先、A 后的时序分离；object1 是目标交互的外部混杂。

- Jiangtong Traj26 仅空间交叉，时间上相差约 9.50 s，不是天然近同时 benchmark。

- J117 基于真实 GeoJSON 构建，已通过 production Map API 和单车 IDM 闭环。

- J117 后续双车场景属于 real-map constructed benchmark。

## 14.3 不能说什么

- 不能说系统已证明全场景安全。

- 不能把 v16/v18 未碰撞说成协同成功。

- 不能说 Jiangtong 是第二个双矿卡 benchmark。

- 不能说 J117 Phase4C 是 MCTS 成功。

- 不能把 XG90G 说成新矿区真实车型。

- 不能把 flat height=0 说成真实地形。

- 不能说已经训练 Neural-MCTS。

# 15. 下一阶段路线图与决策门

## 15.1 推荐的第一步：先固化 Phase 4C

| **动作**                                                            | **理由**                                                 |
|---------------------------------------------------------------------|----------------------------------------------------------|
| 将 full-route 最终 JSON 写入 /root/autodl-tmp/new_map_phase4c_j117/ | 当前结果主要在终端 transcript，需云端持久证据            |
| 更新 AI_HANDOFF.md / PROJECT_STATUS.md                              | tracked 文档仍以 V22 为主要收口，未完整记录 J117 Phase4C |
| 创建 docs-only commit + annotated tag                               | 让 Phase4C 成为可追溯里程碑；可指向包含文档的新增 commit |
| 备份 Phase1–4 外置目录与 source ZIP                                 | 防止实例重置或误删                                       |

## 15.2 Phase 5：J117 双受控车辆 benchmark

**建议流程**

J117 real map  
-\> Route A controlled vehicle A  
-\> Route B controlled vehicle B  
-\> choose starts / speeds from real path geometry  
-\> design near-simultaneous ETA (explicit DESIGN DECISION)  
-\> 30–40 step preflight  
-\> Pure MCTS A-B-only closed loop  
-\> geometry / timing / clearance / goal metrics  
-\> compare with IDM or fixed-budget baselines  
-\> only then consider external actors / algorithm ablations

| **Gate**       | **通过条件**                                                                    |
|----------------|---------------------------------------------------------------------------------|
| P5-1 几何      | 两车 footprints 在各自 approach/connector/departure 全程可行；不依赖未授权 lane |
| P5-2 时序      | projected ETA 差明确接近，且不是通过篡改真实 replay 声称天然冲突                |
| P5-3 预检      | 30–40 steps 无初始化/Controller/越界问题                                        |
| P5-4 Pure MCTS | A/B 受控、联合动作、内部几何 reward 正常，外部 actor 默认不加入                 |
| P5-5 正式结果  | goal/through-order/clearance/search time/seed/commit/artifact hashes 完整       |

## 15.3 算法深化顺序

25. 先建立第二个干净多车 benchmark，再做 adaptive budget / tree reuse / safety pruning。

26. Neural-MCTS 前先扩充多场景、多 seed 数据；按 scenario/episode 切分，避免时序泄漏。

27. 448 条样本只适合验证 schema；若继续网络路线，先 Value Network，再考虑 policy-value + PUCT。

# 附录 A. 绝对路径索引

| **绝对路径**                              | **作用**                                          |
|-------------------------------------------|---------------------------------------------------|
| /root/MineSim-Dynamic                     | 正式 Git 仓库                                     |
| /root/MineSim-Dynamic/inputs              | 正式原有 Scenario（当前 J117 Scenario 不在此）    |
| /root/miniconda3/envs/minesim             | Conda 环境                                        |
| /root/datasets/maps                       | Dapai/Jiangtong production maps                   |
| /root/autodl-tmp/地图新建相关文件.zip     | 新地图真实 source archive                         |
| /root/autodl-tmp/new_map_phase2_j117      | J117 Bitmap/Semantic/manifests/validation/overlay |
| /root/autodl-tmp/new_map_phase3_maps/maps | J117 shadow production map root                   |
| /root/autodl-tmp/new_map_phase3_j117      | production Map API test outputs                   |
| /root/autodl-tmp/new_map_phase4b_j117     | minimal Scenario 与测试报告                       |
| /root/autodl-tmp/new_map_phase4c_tools    | 1-step / 5s / full-route harness                  |
| /root/autodl-tmp/codex-home               | Codex config/auth/cache home                      |
| /root/autodl-tmp/codex-env.sh             | Codex 环境入口                                    |
| /root/autodl-tmp/mcts_data                | MCTS 数据                                         |
| /root/autodl-tmp/mcts_results             | MCTS 实验结果                                     |
| /root/autodl-tmp/mcts_checkpoints         | 未来 NN 权重                                      |

# 附录 B. Commit / Tag / SHA256 速查

| **类型** | **标识**                                                         | **说明**                              |
|----------|------------------------------------------------------------------|---------------------------------------|
| Commit   | 2521aa41a69a6e734c04c15a715e9530c8095ac3                         | IDM baseline                          |
| Tag      | idm-replay-autodl-baseline                                       | baseline 锚点                         |
| Commit   | 94693dc799fe5f325a75e8fc6d7d5e88764b4799                         | MCTS/IDM/专家数据/五 Planner 正式基线 |
| Tag      | mcts-expert-dataset-v1-20260802                                  | 448 专家样本                          |
| Commit   | f8ff1866789ed3d9d878f34b7cd34ab490e40121                         | Fleet internal clearance reward       |
| Commit   | 94794c963f9c3eaf1873b275df6d319ca2636817                         | Jiangtong V22 文档收口                |
| Tag      | jiangtong-v22-benchmark-screening-20260809                       | V22 milestone                         |
| Commit   | 4bd2bff28c593ee80ab8c9fe2eefecd2b009e9b6                         | J117 loader registration              |
| Tag      | j117-phase3-production-map-load-20260809                         | Map API milestone                     |
| Commit   | ec1c958735b0ee76201284faacb46fccc75c7f6c                         | J117 minimal Scenario support         |
| Tag      | j117-phase4b-minimal-scenario-20260809                           | minimal Scenario milestone            |
| SHA256   | 1e499fd92d3d76ae7167960d492e8760fc8aa7b73180458c0e90aefa07e1a44d | source ZIP                            |
| SHA256   | 65fb1c88196468a4b7640d5c82bf854807d0ab93716d26f1f9f8cd4704245ac4 | J117 bitmap                           |
| SHA256   | 1aef7e1054fb8f54004ee96fbd4e7afc984180c52735446cb0224d79e4286afa | J117 semantic                         |
| SHA256   | 6581c351fdf945d88166a63e2ea1497522548339a37ef2896e7df3df225a91d8 | J117 minimal Scenario                 |

# 附录 C. 可直接复制给新 AI 的接管 Prompt

你正在接管 MineSim-Dynamic 露天矿无人矿卡规划项目。  
  
请先阅读《MineSim-Dynamic 云端项目完整交接与工作流手册（2026-08-09）》；但必须重新核验云端，不能把文档当实时状态替代品。  
  
正式仓库：/root/MineSim-Dynamic  
预期 branch：newmap-j117-dev  
预期 HEAD：ec1c958735b0ee76201284faacb46fccc75c7f6c  
Conda：minesim / Python 3.9.25  
数据与临时资产：/root/autodl-tmp  
  
当前已完成：  
1) Pure MCTS 与多车 Fleet MCTS；  
2) Dapai 双车 A-B-only 时序协调证据；  
3) Jiangtong V22 负筛选并封存；  
4) 真实 GeoJSON -\> J117 pilot Raster/Semantic；  
5) production Map API PASS；  
6) minimal XG90G single-ego Scenario PASS；  
7) IDMPlanner + iLQR + KBM S2-\>G1 完整闭环 PASS（423 steps, 42.3s）。  
  
当前未完成：  
- J117 standard runner integration；  
- J117 双车 constructed benchmark；  
- J117 Pure MCTS；  
- Neural-MCTS 训练。  
  
规则：  
- 先只读核验 branch/HEAD/status/进程/paths/hashes；  
- 不 git add . / git clean / reset --hard / rm -rf；  
- 不处理已有 untracked 文件；  
- 不把 Phase4C 说成 MCTS；  
- FACT / DERIVED / DESIGN DECISION / UNKNOWN 分开；  
- 一次只做一个小步骤，给出 PASS/FAIL 门槛；  
- 大文件、日志、脚本、结果写 /root/autodl-tmp。  
  
第一轮只输出：  
A. 当前理解；  
B. 与预期状态的差异；  
C. 必须复核的事实；  
D. 下一条最小只读命令；  
不要修改任何文件。

# 附录 D. 证据来源清单

| **编号** | **文件 / 证据**                                                    | **用途**                                                               |
|----------|--------------------------------------------------------------------|------------------------------------------------------------------------|
| S1       | MineSim-Dynamic_项目全景档案与AI长期接管超级手册_2026-08-06.docx   | 历史全景、环境、MCTS、五 Planner、公平性与旧路径                       |
| S2       | MineSim-Dynamic_MCTS在线闭环对比与搜索预算分析2026-08-07.docx/pdf  | 五 Planner、Safe Goal、Budget 消融                                     |
| S3       | 0271e6a8-73d9-4d62-acaf-a337b294927e.docx                          | 2026-08-09 多车 MCTS、Dapai 机制、V22 停点                             |
| S4       | MineSim-Dynamic地图更换方案.docx/pdf                               | Raster/Semantic/Scenario 数据分类与地图制作原则                        |
| S5       | MineSim-Dynamic新地图代码接入.docx/pdf                             | Loader、location、token、Scenario 接入原则                             |
| S6       | MineSim-Dynamic_AutoDL云端项目环境与文件资产说明书_2026-07-26.docx | 云端资产、系统盘与数据盘规则                                           |
| S7       | MineSim-Dynamic_Git入门与项目版本管理学习手册_2026-07-26.docx      | 正式仓库、分支、commit/tag 与 Git 风险                                 |
| T1–T16   | 2026-08-09 各“粘贴的文本”Codex 终端记录                            | Phase1–Phase4C 的实际命令、代码输出、异常、修复、commit/tag 与闭环结果 |
| SRC      | 地图新建相关 ZIP / 8 个 GeoJSON + preview PNG                      | 新地图真实 source                                                      |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>文档终止点</strong></p>
<p>截至本手册证据截止，Phase 4C 单车完整闭环已通过；Phase 5 双车 constructed benchmark 尚未开始。任何后续 AI 必须先将这一状态与当前云端重新对齐。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>
