**MineSim-Dynamic**

**项目完整进展、云端接管与工作流超级手册**

IDM Baseline → Pure MCTS → 五 Planner / Budget → J117 → Full-Mine → Vector V2 → Targeted Runtime

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>文档定位</strong></p>
<p>本文件不是阶段性摘要，而是面向“下一位 AI / 工程人员可直接接手 AutoDL 云端”的完整事实手册。内容综合了 2026-07-22 至 2026-08-12 的项目文档、Git/终端输出、当日 Codex/AI 审计记录、Full-Mine / Vector V2 构建与运行证据，以及当前尚未闭合的 CollisionLookup 诊断。任何旧文档中的状态只作为历史快照；接手时仍以实时云端 Git、文件哈希和终端输出为最高事实源。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

| **项目**           | **当前值**                                                                                                                                              |
|--------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------|
| **文档日期**       | 2026-08-12                                                                                                                                              |
| **当前工程主线**   | Full-Mine Vector V2 地图完善与 targeted closed-loop runtime 验收                                                                                        |
| **当前地图身份**   | geojson_full_mine_vector_v2_dev / version=dev-geojson-full-mine-vector-v2                                                                               |
| **当前地图性质**   | DEV / Research；production drivable-mask truth 仍未获得权威输入                                                                                         |
| **证据截止点**     | C/D/E targeted runtime 已运动并定位首次 mask failure；CollisionLookup 几何定义不一致已坐实；“官方 CarFootprint 对 failure state 的最终真值检查”尚未执行 |
| **正式仓库**       | /root/MineSim-Dynamic                                                                                                                                   |
| **Conda / Python** | minesim / Python 3.9.25                                                                                                                                 |

用途：项目交接 / 云端恢复 / AI 接管 / 问题复盘 / 后续实验规划

# **目录与快速导航**

- 0\. 接手前 5 分钟必须读完的“当前真相”

- 1\. 项目定义、研究主线与系统边界

- 2\. 事实源、证据等级与时间冲突处理规则

- 3\. 项目完整时间线：从地图方案、IDM Baseline 到 Vector V2

- 4\. AutoDL 云端、Git、目录资产与版本冻结点

- 5\. MineSim 原系统架构与当前闭环调用链

- 6\. IDM Baseline、Pure MCTS、专家数据与 Neural-MCTS 边界

- 7\. 五 Planner、公平在线比较、Budget 消融与多车 MCTS

- 8\. J117 真实地图 Pilot：Phase 1–5 的完整闭环

- 9\. Full-Mine V1：Structural → DEV Mask → 独立身份 → Runtime

- 10\. 2026-08-12 源数据最大利用审计：六条缺失 road、332、484、Z、Topology

- 11\. Full-Mine Vector V2 Semantic：修复策略、Builder、回归与基本 Runtime

- 12\. Vector V2 DEV Bitmap：冻结版、5186 五像素补丁、可复现 Builder 与取舍

- 13\. Targeted Runtime：15 条重点 Lane、7 场景、BFS depth=5 与 7/7 Route PASS

- 14\. 当前正在排查的核心问题：CollisionLookup 与官方车辆几何不一致

- 15\. 全过程问题库：症状 → 根因 → 解决 → 可复用规则

- 16\. 云端关键资产、绝对路径、哈希与“不要覆盖”的文件

- 17\. 用户实际工作流与 AI/终端协作规范（当前：不用 Codex）

- 18\. 当前下一步、验收门与后续地图完善路线

- 19\. 风险边界、未知项与论文/汇报中禁止越界的表述

- 20\. 可直接交给下一位 AI 的接管 Prompt

- 附录 A. Commit/Tag 速查

- 附录 B. Vector V2 关键数量、Target Lane/Route 速查

- 附录 C. 证据文件索引与阅读优先级

# **0. 接手前 5 分钟必须读完的“当前真相”**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>30 秒结论</strong></p>
<p>MineSim-Dynamic 已从 IDM baseline 推进到 Pure MCTS、五 Planner 在线闭环比较、搜索预算消融、双受控车辆 Fleet MCTS、J117 真实地图闭环以及 Full-Mine 全矿地图。当前不是“地图能否加载”的阶段：Full-Mine Vector V2 Semantic 已补全到 100 road / 553 reference_path，并通过基础 single/dual runtime；当前只剩 targeted runtime 的最后验收与 CollisionLookup 历史几何实现一致性问题。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

| **子系统/阶段**                  | **状态**            | **当前事实**                                                                                         |
|----------------------------------|---------------------|------------------------------------------------------------------------------------------------------|
| **IDM baseline**                 | \[PASS\]            | 2521aa4 / idm-replay-autodl-baseline，历史稳定锚点                                                   |
| **Pure MCTS 单车**               | \[PASS\]            | Dapai/Jiangtong 闭环、几何安全、专家样本已完成；不等于全场景安全                                     |
| **五 Planner 在线比较**          | \[PASS\]            | MCTS/IDM/Online Frenet/Online Adapted Maneuver + Simple 下限；2 场景结果已冻结                       |
| **MCTS Budget 50/100/200/300**   | \[PASS\]            | Dapai 对预算敏感；Jiangtong 低预算已近饱和                                                           |
| **Multi/Fleet MCTS**             | \[PASS\]            | Dapai 双受控机制证据、J117 Phase5 双车 Pure MCTS 5 seed 全通过                                       |
| **J117 真实地图**                | \[PASS\]            | Map API + minimal Scenario + single full route + dual runtime + Pure MCTS                            |
| **Full-Mine V1**                 | \[PASS\]            | geojson_full_mine_dev；single/dual 1-step/5s 均通过；DEV_ONLY mask                                   |
| **Full-Mine Vector V2 Semantic** | \[PASS\]            | 100 road、553 paths、8 road repair provenance、raw lane Z 写入                                       |
| **Vector V2 基础 runtime**       | \[PASS\]            | single 1-step/5s + dual 1-step/5s 全 PASS                                                            |
| **15 条重点 path 静态验证**      | \[PASS\]            | 13 新恢复 path + road484 两条；中心线与真实 XG90G footprint 内部问题已清零                           |
| **7 个 targeted planner route**  | \[PASS\]            | 7/7 actual route 与期望逐 token 一致，refline_smooth 成功                                            |
| **Targeted real closed-loop**    | \[IN PROGRESS\]     | C/D/E 已真实运动；当前失败来自 CollisionLookup 道路边界检查，正在区分历史 lookup bug 与真实 mask gap |
| **Production drivable mask**     | \[UNKNOWN/BLOCKED\] | 源 GeoJSON 缺少权威内部禁行/障碍层；不能声称与 Dapai/Jiangtong production mask 同级                  |
| **Neural-MCTS**                  | \[NOT STARTED\]     | 已有专家数据与研究路线，但没有正式 Value/Policy/PUCT 训练结论                                        |

## **0.1 接手后第一条命令**

所有后续终端代码都必须先重新进入 minesim 环境并进入正式仓库。用户已明确要求：今后每个代码块前都加这三行。接手 AI 不应假设新 shell 已经在正确环境。

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>source /root/miniconda3/etc/profile.d/conda.sh<br />
conda activate minesim<br />
cd /root/MineSim-Dynamic<br />
export PYTHONPATH=/root/MineSim-Dynamic<br />
<br />
echo "ENV=$CONDA_DEFAULT_ENV"<br />
python --version<br />
pwd<br />
<br />
git branch --show-current<br />
git rev-parse HEAD<br />
git status --short --branch<br />
<br />
echo "memory.max=$(cat /sys/fs/cgroup/memory.max 2&gt;/dev/null || true)"<br />
echo "cpu.max=$(cat /sys/fs/cgroup/cpu.max 2&gt;/dev/null || true)</th>
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
<th><p><strong>Git 重要提醒</strong></p>
<p>旧 Full-Mine 冻结点明确为 newmap-j117-dev @ d81c571... / tag fullmine-dev-runtime-pass-20260811；但 2026-08-12 Vector V2 注册已在运行环境中生效，而本轮对话没有给出其最终 commit/tag。下一位 AI 必须先看实时 git status/diff，不能把 d81c571 当作“Vector V2 当前 HEAD”强行 reset 回去。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## **0.2 当前绝对不要做的事情**

- 不要 git clean -fd、git reset --hard、git add .，也不要批量删除未知 untracked / .bak / YAML / 临时工具。

- 不要覆盖 /root/autodl-tmp/new_map_phase6f8_full_mine_dev 或旧 geojson_full_mine_dev；V1 是重要回归基线。

- 不要把 Vector V2 / additive mask 称为 production-authoritative HD Map。

- 不要为了让 CollisionLookup 通过而继续扩大 bitmap；其车辆几何定义目前与官方 CarFootprint/ScenarioController 不一致。

- 不要重新跑已经冻结的 J117 Phase3/4/5、Full-Mine V1 basic smoke、Vector V2 7/7 planner route，除非出现明确回归证据。

- 不要自动修 lane 6713 的 Z seam；保留 raw Z + QA 标记，不凭空平滑。

- 不要把不同 topo ID 仅因 XY 接近或相同就合并；相同 XY/不同 topo 在 auxiliary gear transition 中有真实语义。

- 不要把整个 road/junction/load/unload/auxiliary polygon 全部涂白作为 production mask。

- 当前用户已明确“不用 Codex 了，我们自己跑”；除非用户再次改变决定，不要主动把任务交给 Codex。

# **1. 项目定义、研究主线与系统边界**

## **1.1 一句话定义**

MineSim-Dynamic 是面向露天矿非结构化道路自动驾驶矿卡的场景化闭环仿真与规划研究项目。用户的项目不是单一“写一个 MCTS”，而是由四条互相依赖的主线组成：仿真平台复现、规划算法、真实/构造 benchmark、新矿区地图工程。

| **主线**       | **目标**                                                                            | **当前状态**                                                                           |
|----------------|-------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------|
| 仿真与闭环工程 | 确保 Scenario → Map → Planner → Controller → Vehicle Model → Observation 能稳定运行 | \[PASS\] 基线、J117、Full-Mine 均走通                                                  |
| 规划算法       | IDM 基线 → Pure MCTS → multi/Fleet MCTS；未来才是 Neural-MCTS                       | \[PASS\] Pure/Multi；\[NOT STARTED\] 正式 NN                                           |
| Benchmark      | Dapai/Jiangtong → J117 real-map constructed benchmark → Full-Mine 多区域覆盖        | \[PASS\] 前三；\[IN PROGRESS\] Full-Mine 扩展                                          |
| 地图工程       | 真实 GeoJSON → Semantic/Bitmap → Map API → Runtime；尽可能恢复 Full-Mine            | \[PASS\] Vector V2 semantic；\[IN PROGRESS\] targeted runtime；production truth 仍未知 |

## **1.2 当前工作的真正重点**

截至本手册，算法主线并没有停滞在早期 MCTS 实现；J117 双受控 Pure MCTS 已形成 5-seed 证据，Full-Mine V2 也已经完成 semantic 和基础 runtime。当前工程优先级是把全矿地图尽可能完善并建立可信的 targeted runtime coverage，然后再回到更广场景 MCTS / Neural-MCTS。

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>当前不要混淆的两件事</strong></p>
<p>“软件链可运行”与“production 地图真实性”是不同命题。Vector V2 已经能被 MineSim loader/Map API/Planner 使用，并通过多个闭环 smoke；但现有 GeoJSON 无法唯一恢复官方 production mask 内部 exclusions。因此当前成果应准确称为 Full-Mine Vector V2 DEV/Research Map。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# **2. 事实源、证据等级与时间冲突处理规则**

项目历史跨度长、文档多且状态变化快。任何接手 AI 必须使用“最新、最直接、最可复核”的证据覆盖旧快照。

| **等级**       | **证据**                                                                      | **使用规则**                        |
|----------------|-------------------------------------------------------------------------------|-------------------------------------|
| \[V-LIVE\]     | 当前 AutoDL 终端、Git、源码、实时文件/哈希、实际运行输出                      | 最高；重连后必须重新核验            |
| \[V-ARTIFACT\] | /root/autodl-tmp 下 manifest、validation JSON、日志、冻结文件、runtime result | 直接支持工程状态；注意路径与版本    |
| \[V-DOC\]      | 2026-08-12 终端/Codex 会话导出与本手册                                        | 用于交接；若和 live 冲突，live 优先 |
| \[H\]          | 2026-08-11 / 08-09 / 08-06 / 07-26 Word                                       | 只解释当时状态，不可覆盖后续进展    |
| \[D\]          | 由已核验几何/统计推导出的判断                                                 | 可用于工程决策，但需保留计算定义    |
| \[U\]          | 资料不足/无权威定义                                                           | 不得用常识补成事实                  |

## **2.1 已发生过的典型“旧文档覆盖新事实”风险**

- 2026-07-26 文档写“Pure MCTS 尚未开始”，但 8 月 2 日已经完成两场景闭环、448 专家样本。

- 2026-08-09 文档写“J117 双车 Pure MCTS 尚未开始”，但 8 月 10 日 Phase 5 已冻结并完成 5 seed。

- 2026-08-11 Full-Mine V1 手册把 road332、6 条 missing-road、road484 作为排除项；8 月 12 日基于源内部证据已经高置信修复，Vector V2 不再沿用这些排除。

- 早期文档将源 Z 标为“datum/unit unknown，因此不进入 semantic”；8 月 12 日全量异常审计证明 lane Z 质量明显高于 boundary Z，因此 Vector V2 已将 raw lane Z 写入 waypoint elevation，但仍保持 source_z_datum_verified=false。

# **3. 项目完整时间线：从地图方案、IDM Baseline 到 Vector V2**

| **日期**        | **阶段**                         | **结果/意义**                                                                                                                                                                         |
|-----------------|----------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 2026-07-22      | 地图接入框架                     | 明确 Raster Map + Semantic Map + Scenario 三类成果与新矿区接入思路。                                                                                                                  |
| 2026-07-26      | IDM Baseline 冻结                | /root/MineSim-Dynamic；commit 2521aa4；tag idm-replay-autodl-baseline；建立云端/Git/AI 协作规范。                                                                                     |
| 2026-07-30~31   | Pure MCTS 闭环                   | MCTSPlanner 外壳→状态/动作/搜索/奖励→轨迹适配→闭环；经历确定性/iLQR 等修复。                                                                                                          |
| 2026-08-01      | Jiangtong 几何预测与安全         | CV/CTRV、0.5m buffer、viability、clearance 等安全迭代。                                                                                                                               |
| 2026-08-02      | MCTS 正式结果 + 专家数据         | commit 94693dc；Dapai/Jiangtong；448 strict expert samples；Neural-MCTS 未训练。                                                                                                      |
| 2026-08-03~07   | 五 Planner + 在线公平性 + Budget | Frenet/Maneuver/Simple 工程适配；统一 evaluator；Budget 50/100/200/300。                                                                                                              |
| 2026-08-08~09   | 多车 MCTS / 第二 benchmark 筛选  | Dapai 双受控时序机制；Jiangtong V22 负筛选；转向真实 GeoJSON 新地图。                                                                                                                 |
| 2026-08-09      | J117 Phase1–4C                   | J117 pilot → Map API → minimal Scenario → 423 step / 42.3s 单车 full-route 闭环。                                                                                                     |
| 2026-08-10      | J117 Phase5                      | dual-ego production runtime + Pure MCTS；commit da4105b；5 seed benchmark/swept safety 通过。                                                                                         |
| 2026-08-11      | Full-Mine V1                     | Full structural + DEV_ONLY mask + O(1) semantic lookup + 独立 geojson_full_mine_dev；single/dual 1-step/5s PASS；tag fullmine-dev-runtime-pass-20260811。                             |
| 2026-08-12 上午 | 源数据最大利用审计               | Codex/终端审计 6 missing roads、road332/484、Z、topology；随后用户明确停止 Codex，改为自己终端执行。                                                                                  |
| 2026-08-12 中午 | Vector V2 Semantic               | 100 roads / 553 paths / 8 repair records；raw lane Z；V1→V2 严格增量回归 PASS；Map API + single/dual runtime PASS。                                                                   |
| 2026-08-12 下午 | Vector V2 Bitmap/Targeted        | V2 freeze mask；lane5186 5-pixel physical patch；15-target static PASS；7 depth-safe scenarios；planner route 7/7 PASS。                                                              |
| 2026-08-12 当前 | CollisionLookup 诊断             | C/D/E targeted runtime 已真实运动，但 lookup 判边界碰撞；源码显示 lookup 前后方向与 CarFootprint/ScenarioController 约定相反；下一步做官方 CarFootprint 对 failure state 的真值检查。 |

# **4. AutoDL 云端、Git、目录资产与版本冻结点**

## **4.1 固定路径与环境**

| **项目**       | **规则/当前事实**                                                                            |
|----------------|----------------------------------------------------------------------------------------------|
| 正式仓库       | /root/MineSim-Dynamic；只在这里修改 tracked production code                                  |
| 数据盘         | /root/autodl-tmp；地图大文件、转换工具、日志、实验、临时 harness、bundle 全部优先放这里      |
| 环境           | /root/miniconda3/envs/minesim；Python 3.9.25                                                 |
| 原项目成品地图 | /root/datasets/maps；广东大排/江西江铜，仅作 production 行为对照，禁止修改                   |
| 资源判断       | 以 /sys/fs/cgroup/memory.max 与 cpu.max 为权威；free -h / nproc 可能展示宿主机或大卡可见值   |
| 大卡策略       | 地图 full PNG / full mask load / runtime 需要 RAM；GPU 对 Shapely/Rasterio/Pillow 基本无收益 |

## **4.2 关键 Git 里程碑**

| **Commit** | **Tag/状态**                                         | **意义**                                                                                |
|------------|------------------------------------------------------|-----------------------------------------------------------------------------------------|
| 2521aa41…  | idm-replay-autodl-baseline                           | IDM + replay 基线锚点                                                                   |
| 94693dc…   | mcts-expert-dataset-v1-20260802                      | Pure MCTS 两场景正式结果 + 448 专家样本                                                 |
| f8ff186…   | multi-mcts-dev 历史节点                              | Fleet internal clearance reward                                                         |
| 94794c9…   | jiangtong-v22-benchmark-screening-20260809           | Jiangtong 第二冲突 benchmark 负筛选封存                                                 |
| 4bd2bff…   | j117-phase3-production-map-load-20260809             | J117 semantic/bitmap 注册到 production Map API                                          |
| ec1c958…   | j117-phase4b-minimal-scenario-20260809 / phase4c tag | J117 minimal Scenario/no-agent horizon + single full route                              |
| da4105b…   | j117-phase5-dual-ego-pure-mcts-20260810              | J117 dual-ego production runtime + Pure MCTS                                            |
| 32fb429…   | —                                                    | Full-Mine semantic node lookup 改 token2ind O(1)                                        |
| d81c571…   | fullmine-dev-runtime-pass-20260811                   | 注册 geojson_full_mine_dev；V1 single/dual smoke 冻结                                   |
| Vector V2  | TBD：对话未给最终 commit/tag                         | 三 production registry 文件已能工作，但接手必须审 git diff/status 后再决定是否/如何提交 |

## **4.3 Git 安全纪律**

- 每次准备 commit 前：git diff --check；git diff --name-only；git diff --cached --name-only；只允许精确 git add \<file1\> \<file2\>。

- 仓库历史上存在重要 untracked 辅助文件与备份；即使当前某次 status 干净，也不使用 git clean -fd。

- 大文件和结果不提交 repo；保持源码 commit 小而可审计。

- 任何 Vector V2 freeze 前必须先核验旧 d81c571 基线与当前工作树差异，不能用 reset 把 8 月 12 日工作覆盖掉。

# **5. MineSim 原系统架构与当前闭环调用链**

MineSim 原论文定位为面向露天矿无人矿卡规划任务的场景化闭环仿真系统。地图由 Raster/Bitmap 与 Semantic Map 协同提供几何、拓扑和道路边界；Scenario 定义一次任务；Planner 输出未来轨迹；Controller 跟踪轨迹；车辆模型积分下一帧；其他 agent 由 replay/reactive/预测策略更新。

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>MineSim Semantic 的关键格式</strong></p>
<p>原论文定义 reference_path waypoint 约为 [x, y, yaw, elevation, slope]；borderline 记录 [x, y, elevation]。Vector V2 正是基于这一格式把 raw lane Z 恢复到 waypoint[3]，但由于 slope 生成/平滑规则未完整复现，waypoint[4] 仍保持 0.0。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

| **层**         | **当前项目中的真实调用链**                                                |
|----------------|---------------------------------------------------------------------------|
| Scenario / Map | ScenarioFileBaseInfo → MineSimDynamicScenario → get_maps_api / MineSimMap |
| Planning       | planner.initialize() 先生成 global route/refline；每帧 compute_trajectory |
| Control        | TwoStageController → iLQR/LQR tracker（按配置）                           |
| Vehicle update | Kinematic Bicycle Model / ego controller propagate                        |
| Observation    | 更新其他 actor 与 observation；进入下一 iteration                         |
| Safety/metrics | 车辆几何、道路 bitmap、goal polygon、history/log                          |

## **5.1 当前地图接口必须区分三类数据**

| **数据**     | **作用**                                                  | **当前 Full-Mine V2**                                      |
|--------------|-----------------------------------------------------------|------------------------------------------------------------|
| Semantic Map | road/polygon/borderline/reference_path/topology/elevation | 高可信，100 road / 553 path；8 repair provenance           |
| Bitmap mask  | 可行驶/不可行驶栅格；CollisionLookup 使用 10 px/m         | DEV/Research；当前 active candidate = frozen V2 + 5 pixels |
| Scenario     | 起点、目标、多车、dt/max_t                                | targeted runtime 已构建 7 depth-safe 场景                  |

# **6. IDM Baseline、Pure MCTS、专家数据与 Neural-MCTS 边界**

## **6.1 IDM Baseline**

IDMPlanner 是当前工程的重要对照和复用基座。它依赖全局 reference route，根据当前 leading object 的距离、相对速度、目标速度、headway 与最小间距计算纵向加速度，计算快、沿 route 稳定，但不显式搜索未来多步动作序列。

## **6.2 Pure MCTS 的接入方式**

Pure MCTS 没有推翻 MineSim 的整个规划器结构，而是继承 AbstractIDMPlanner，复用路线、观测、轨迹接口和下游控制链，把纵向决策替换为离散动作树搜索。

| **项目** | **正式/历史核心参数**                                                              |
|----------|------------------------------------------------------------------------------------|
| 动作     | BRAKE=-3.0；DECEL=-1.5；KEEP=0；ACCEL=+1.0 m/s²                                    |
| 搜索     | Budget=300；max_depth=8；tree dt=0.5 s；c_uct=1.4；gamma=0.99                      |
| 障碍预测 | CV / CTRV；中间角速度区间保留两种占用；碰撞采样约 0.1 s                            |
| 硬安全   | 障碍物 polygon buffer 0.5 m 后与 ego footprint 相交即 collision                    |
| 连续安全 | 物理净距 \<3.0 m 进入二次 penalty；weight 0.5                                      |
| 输出     | 选中根动作 → route-aligned 未来 EgoState → InterpolatedTrajectory → Controller/KBM |

## **6.3 2026-08-02 正式两场景结果**

| **场景**  | **MCTS**                                                         | **IDM**                                        | **正确解读**                                                            |
|-----------|------------------------------------------------------------------|------------------------------------------------|-------------------------------------------------------------------------|
| Dapai     | 0 collision；0 boundary；min clearance 0.522 m；mean v 6.416 m/s | 21 collision frames；未安全完成                | MCTS 多步/几何预测在此横向冲突有明显价值；但安全余量紧、计算慢、jerk 高 |
| Jiangtong | 0 collision；min clearance 2.260 m；mean v 9.008 m/s             | 0 collision；min clearance 2.341 m；更快更平滑 | 低冲突下 MCTS 额外计算收益有限；不支持“所有场景都更优”                  |

## **6.4 专家数据与 Neural-MCTS**

两场景共形成 448 条 strict expert samples；动作分布约 ACCEL 322 / KEEP 51 / DECEL 41 / BRAKE 34。它为未来 Value/Policy 学习提供数据接口，但当前样本来自连续时间序列和仅两个场景，不能随机按行切分，否则存在时序泄漏。

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>必须保持的边界</strong></p>
<p>当前没有正式训练 Value Network、Policy Network、Policy-Value 或 PUCT。任何下一位 AI 都不得把研究路线写成已完成成果。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# **7. 五 Planner、公平在线比较、Budget 消融与多车 MCTS**

## **7.1 五 Planner 的角色**

| **Planner**             | **核心逻辑**                                   | **信息条件/定位**              |
|-------------------------|------------------------------------------------|--------------------------------|
| MCTS                    | 四纵向动作树搜索；当前观测 + CV/CTRV；多步前瞻 | 核心方法                       |
| IDM                     | leading object 驱动的反应式纵向控制            | 轻量反应式基线                 |
| Online Frenet           | Frenet 二维多项式候选 + 约束筛选               | 公共在线预测；经典采样基线     |
| Online Adapted Maneuver | 分段 jerk 机动 + Frenet 横向候选               | 适配版复杂采样；必须标 Adapted |
| Simple                  | 固定加速度/转角运动学直行                      | 信息最少；仅能力下限           |

## **7.2 统一闭环结果（Dapai + Jiangtong）**

| **Planner**             | **Safe Goal** | **累计车辆碰撞帧** | **累计边界帧** | **解释**                                         |
|-------------------------|---------------|--------------------|----------------|--------------------------------------------------|
| MCTS                    | 2/2           | 0                  | 0              | 当前两场景唯一 2/2；只是描述性，不代表总体成功率 |
| IDM                     | 1/2           | 21                 | 0              | Jiangtong 可用、Dapai 冲突                       |
| Online Frenet           | 0/2           | 0                  | 0              | 安全但未完成任务；不能只看碰撞                   |
| Online Adapted Maneuver | 0/2           | 67                 | 0              | 评价当前适配版，不代表原始方法总体               |
| Simple                  | 0/2           | 0                  | 90             | 下限参考                                         |

## **7.3 Search Budget 结论**

Budget 50/100/200/300 的消融只改变搜索预算，其余固定。Dapai 只有 300 在固定时限内进入目标，低预算仍距目标约 1.48/1.07/1.09 m；Jiangtong 四档均在相同 step 附近完成，轨迹差极小。说明固定高预算存在场景/状态无关冗余，后续 adaptive budget / tree reuse / value guidance 是自然方向。

## **7.4 Multi/Fleet MCTS 与 benchmark 选择**

多车阶段把两个受控车辆放入 FleetState，16 个联合动作由 FleetTransitionModel 联合传播，FleetRewardModel 既包含 per-vehicle 奖励，也包含内部连续净距与 hard safety。Dapai A-B only 已形成“B 先过、A 后过”的时序分离证据；full-external 的 object1 会 preempt 目标交互，因此被识别为 benchmark confounder，而不是继续通过调 reward 强行“让它成功”。

Jiangtong V22 虽存在空间交叉，但真实 actor 到达与 ego 最早 ETA 相差约 +9.496 s，不构成天然近同时冲突，因此封存为负筛选结果。项目由此转向 J117 real-map constructed benchmark。

# **8. J117 真实地图 Pilot：Phase 1–5 的完整闭环**

## **8.1 为什么先做 Pilot**

J117 = Junction 117。它不是随机版本号，而是从真实 Full-Mine GeoJSON 中选出的交叉区域，用来先证明“真实源数据 → MineSim Map API → Scenario → Planner → Controller → Runtime/MCTS”链路，再扩到全矿。

| **阶段**    | **关键结果**                                                                                      |
|-------------|---------------------------------------------------------------------------------------------------|
| Phase 1/1.5 | 源数据审计与语义消歧；EPSG:32646；J117 作为优先 pilot；避开 gear=-1/road332/missing-road 等未解项 |
| Phase 2     | 构建 J117 bitmap + semantic；Raster/Semantic validation PASS                                      |
| Phase 3     | 注册 geojson_j117_pilot 到 production Map API；commit 4bd2bff                                     |
| Phase 4B    | minimal Scenario，XG90G alias，无 agent horizon；commit ec1c958                                   |
| Phase 4C    | 1 step → 5s → full route；423 steps / 42.3s / 398.998m / min clearance≈1.599m / goal reached      |
| Phase 5     | dual-ego production runtime + Pure MCTS；commit da4105b；5-seed benchmark 与 swept safety 全通过  |

## **8.2 J117 当前作用**

J117 已经是冻结回归区域。后续 Full-Mine/Vector V2 工作不应重新调 J117 MCTS。只有 production 源码发生可能影响 Map API/Planner/Controller 的修改时，才用 J117 做最小回归。

# **9. Full-Mine V1：Structural → DEV Mask → 独立身份 → Runtime**

## **9.1 V1 structural 基线**

| **层**         | **V1 数量** |
|----------------|-------------|
| node           | 400,744     |
| polygon        | 177         |
| road           | 93          |
| intersection   | 35          |
| loading_area   | 36          |
| unloading_area | 7           |
| auxiliary_area | 6           |
| dubins_pose    | 565         |
| reference_path | 540         |
| borderline     | 388         |

V1 之所以只有 540 paths / 93 roads，是因为当时基于“不能猜”的保守原则显式排除了 road332、6 个缺失 road 的 12 条 lane，以及 road484 的 mask 等异常。这个版本的意义是建立了可运行、可回归的 Full-Mine 软件基线，而不是源数据利用率的上限。

## **9.2 V1 structural 过程中修掉的系统性 bug**

| **问题**                    | **根因**                                                   | **最终修复**                                                                |
|-----------------------------|------------------------------------------------------------|-----------------------------------------------------------------------------|
| 126 个 path endpoint errors | 相同 source topo node 的 lane endpoint XY 不 bit-identical | 同 topo ID 建 deterministic canonical XY；只 snap path 首尾；安全阈值 0.25m |
| source_coverage_missing=49  | load/unload/aux 已生成但 validator layer 映射遗漏          | 显式 source→semantic mapping                                                |
| 8 个 boundary parent 错挂   | 只按 object ID 跨 category 搜索，忽略 rgn_type             | rgn_type + rgn_objectid 联合解析；禁止跨类别猜                              |

## **9.3 V1 DEV_ONLY mask**

官方 MineSim 只公开成品 Dapai/Jiangtong maps，没有公开原始 GIS → production bitmap 的 authoring pipeline；对官方成品分析又证明 polygon 内存在大量 non-drivable 内部区域，因此 whole-polygon=drivable 不可信。V1 最终采用 lane-centered ±3.5m corridor + parent clipping，10 px/m，明确 DEV_ONLY_NOT_PRODUCTION_VALIDATED。

| **项目**                 | **V1 值**                                                                                         |
|--------------------------|---------------------------------------------------------------------------------------------------|
| 物理 PNG                 | /root/autodl-tmp/new_map_phase6f4_dev_mask/bitmap/geojson_full_mine_dev_only_mask.png             |
| runtime symlink          | /root/autodl-tmp/new_map_phase6f8_full_mine_dev/maps/bitmap/geojson_full_mine_dev_bitmap_mask.png |
| 尺寸                     | 46322 × 42411；10 px/m；0/255                                                                     |
| included lane components | 538；road484 两条 lane 排除                                                                       |
| Full mask load           | shape=(42411,46322) bool；约 1.83GiB；历史峰值 RSS≈7.87GiB                                        |

## **9.4 性能修复与独立地图身份**

Full-Mine 大图首次 planner.initialize 卡住，根因是 get_polygon_token_using_node() 对约 400k node 做重复线性扫描。利用已有 token2ind 改为 O(1) 查询后，Full-Mine/J117 回归通过，commit=32fb429。随后从早期 J117 alias 脱离，注册独立 location=geojson_full_mine_dev，commit=d81c571，tag=fullmine-dev-runtime-pass-20260811。

V1 独立身份下 single-ego 1 step / 5s 与 dual-ego 1 step / 5s 全部 PASS。这个冻结点是 Vector V2 的历史回归基线。

# **10. 2026-08-12 源数据最大利用审计：六条缺失 road、332、484、Z、Topology**

## **10.1 原始源包**

| **图层**              | **Feature 数** | **作用**                                   |
|-----------------------|----------------|--------------------------------------------|
| road.geojson          | 94             | road polygon                               |
| road_boundary.geojson | 100            | road 两侧边界                              |
| junction.geojson      | 35             | 交叉区域                                   |
| lane.geojson          | 553            | reference path / topology / source Z       |
| rgn_boundary.geojson  | 84             | junction/load/unload/aux boundary          |
| rng_load.geojson      | 36             | loading region                             |
| rgn_unload.geojson    | 7              | unloading region                           |
| rgn_auxiliary.geojson | 6              | auxiliary region                           |
| 1.png                 | 1              | 1799×1050 普通截图，仅视觉参考，无地理参考 |

全部 GeoJSON 声明 EPSG:4326；项目坐标链固定为 WGS84 → UTM Zone 46N（EPSG:32646）→ MineSim local，E0=409200.0，N0=4916800.0。

## **10.2 当日 Codex 只读审计与随后直接终端工作**

8 月 12 日早期曾让 Codex 做最小只读审计：定位 source ZIP 与 structural builder；核实六个 missing road；对 boundary→polygon 做正常 road 交叉验证。Codex 发现 road326 candidate validity/Hausdorff 异常后，用户明确要求“别用 Codex 了，我们自己跑”。从此后 road326/332/484、Z、V2 builder、bitmap、runtime 全部按“聊天 AI 给最小命令 → 用户终端执行 → 回传输出”继续。

## **10.3 六个缺失 road：从“不可处理”升级为高置信可恢复**

| **Road ID** | **源内部证据**                                     |
|-------------|----------------------------------------------------|
| 339         | road absent；boundary 2 components；lane 5175/5186 |
| 340         | road absent；boundary 2；lane 5180/5181            |
| 353         | road absent；boundary 2；lane 5165/5166            |
| 356         | road absent；boundary 2；lane 5178/5179            |
| 357         | road absent；boundary 2；lane 5171/5172            |
| 360         | road absent；boundary 2；lane 5163/5164            |

关键证据不是“边界看起来像道路”，而是：对已有正常 road 用两条 road_boundary 闭合重建 polygon，IoU 基本接近 1；road326 的异常经 make_valid 后只剩极小 sliver，主 polygon 与 source 几乎一致。六个缺失 road 使用同一规则后均 valid，且对应 12 条 lane 全部 contained。

## **10.4 road 326：为什么一次 FAIL 不代表方法失败**

Codex 全量交叉验证时 92 个 normal roads 中 91 个 candidate valid，IoU_min≈0.9999957，但 road326 candidate invalid 且初始 Hausdorff≈0.408m。进一步诊断表明 raw boundary closure 出现自交；make_valid 后主 polygon≈4343.077071m²，sliver≈0.000118904m²，sliver ratio≈2.74×10^-8，IoU≈0.9999988，Hausdorff≈0.000574m。因此 boundary→road reconstruction 仍被支持，不能因为一次几何 validity gate 就否定方法。

## **10.5 road 332：极小自交毛刺，保留主 polygon**

source road332 自相交；boundary/source 几何几乎一致；lane5050 完整位于主道路内。make_valid 后主要 polygon≈519.277152m²，异常 sliver 总面积约 0.000090m²，sliver ratio≈1.73×10^-7。Vector V2 的策略是 make_valid → 保留最大 polygon → provenance 记录，不用 buffer(0) 随意重构。

## **10.6 road 484：高置信版本不一致，而不是 lane 错**

| **证据**                           | **结果**                                                                  |
|------------------------------------|---------------------------------------------------------------------------|
| source polygon area                | ≈560.526 m²                                                               |
| boundary-derived area              | ≈1205.573 m²                                                              |
| source vs boundary IoU             | ≈0.139293                                                                 |
| Hausdorff                          | ≈39.1 m                                                                   |
| source road 与 Junction125 overlap | ≈344.593 m²，约 61.48%；远高于其他 road                                   |
| source road 到 Loading278          | 最近约 10.946 m，不合理断开                                               |
| boundary-derived                   | 完整包含 lanes 6942 / 6989；两边均连接 Junction125 ↔ Loading278           |
| 版本                               | road484=2026-07-23；road_boundary/lanes/Junction125/Loading278=2026-07-24 |

结论：road484 是唯一明显的 source version mismatch。Vector V2 用 boundary-derived polygon 作为 effective geometry，但原 source 仍保留在 provenance；这并不意味着“整个 polygon production-authoritative drivable”。

## **10.7 Topology：Topo ID 优先，XY 只能在同 ID 内 canonicalize**

同一个 topo node 的多个 lane endpoint 存在厘米级甚至约 0.2m XY 偏差，所以 canonical snapping 是必要的；但不同 topo ID 可能拥有完全相同 XY。全量审计发现约 45 个“exact XY / different topo”配对全部集中在 auxiliary 的 gear transition（通常 -1/+1）。因此绝对不能按距离阈值把不同 topo ID 自动 merge。

gear=-1 共 50 条：auxiliary 48、loading 1、unloading 1、road/junction 0。它们的业务运营方向仍未权威验证；保持 stored topology orientation，不擅自反向。

## **10.8 Z / elevation：lane 可用，boundary 不可用**

| **项目**               | **审计结果**                                                                    |
|------------------------|---------------------------------------------------------------------------------|
| lane Z                 | 553 lanes / 314,692 points 全有 Z；min≈1009.048236，max=1321.0                  |
| 硬异常总审计           | 约 715,313 line segments；“XY≈0 但 Z 显著变化”的 16 段全部来自 boundary，lane=0 |
| \|ΔZ\|\>0.25m          | 总 533；lane=1；road_boundary=332；rgn_boundary=200                             |
| 唯一 hard lane anomaly | lane6713 / road476：+0.519112m 单步 seam；保留 raw Z + QA，不凭空修             |
| lane6723               | 局部 +0.084339m，不能仅凭阈值判错                                               |
| 官方对照               | Dapai 有持续约 -44.5° 陡坡，单步 ΔZ max≈0.233145m；说明“坡大”本身不是错误       |
| shared topo Z seam     | 官方地图也允许；Dapai 某些共享 topo seam \>0.1m，最大约1.6177m；不强制拉平      |
| 边界 Z                 | 出现同 XY 掉 15m 等异常；不作为 elevation truth                                 |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>Vector V2 Z 工程政策</strong></p>
<p>reference_path waypoint[3] = raw lane Z；waypoint[4] slope = 0.0；source_z_datum_verified=false；borderline elevation 暂不采用 raw boundary Z。当前 slope vehicle model 仍是 TODO/不支持状态，因此现有 runtime 不消费 slope。route progress 继续使用 2D XY length。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# **11. Full-Mine Vector V2 Semantic：修复策略、Builder、回归与基本 Runtime**

## **11.1 核心 Builder 与 source/effective 分离**

| **项目**        | **路径/值**                                                                                                         |
|-----------------|---------------------------------------------------------------------------------------------------------------------|
| V2 builder      | /root/autodl-tmp/fullmine_vector_v2_dev/build_full_mine_vector_v2.py                                                |
| Source ZIP      | /root/autodl-tmp/地图新建相关文件.zip                                                                               |
| identity        | geojson_full_mine_vector_v2_dev                                                                                     |
| version         | dev-geojson-full-mine-vector-v2                                                                                     |
| semantic output | /root/autodl-tmp/new_map_fullmine_vector_v2_dev/maps/semantic_map/geojson_full_mine_vector_v2_dev_semantic_map.json |
| semantic SHA256 | b85a3d8b28f2252ecb5bda179d514573f6333079def838cd048566f556d95cd0                                                    |

builder 引入 build_effective_indexes(source_indexes)，严格区分 source inventory 与 effective geometry。source roads 始终仍是 94，不把派生 6 road 冒充成源文件；8 条 repair 独立记录 provenance。

## **11.2 八条 repair records**

| **Road**                          | **Effective 策略**                         |
|-----------------------------------|--------------------------------------------|
| 339 / 340 / 353 / 356 / 357 / 360 | derive_missing_road_from_boundary          |
| 332                               | repair_source_road_make_valid_keep_largest |
| 484                               | replace_source_road_geometry_from_boundary |

## **11.3 Vector V2 最终 semantic counts**

| **层**         | **V2 数量/信息**                     |
|----------------|--------------------------------------|
| polygon        | 184                                  |
| road           | 100                                  |
| intersection   | 35                                   |
| loading_area   | 36                                   |
| unloading_area | 7                                    |
| auxiliary_area | 6                                    |
| reference_path | 553                                  |
| dubins_pose    | 565                                  |
| borderline     | 402                                  |
| waypoints      | 314,692；全部保存 raw lane elevation |

特殊 road readback 面积：332=519.277157；339=301.684859；340=910.559799；353=147.825611；356=492.636277；357=494.285901；360=585.132336；484=1205.572541 m²。所有 8 条均 valid。

## **11.4 V2 对 V1 的严格增量回归**

| **检查**                      | **结果**                                           |
|-------------------------------|----------------------------------------------------|
| V1 reference_path             | 540                                                |
| V2 reference_path             | 553                                                |
| shared                        | 540                                                |
| added                         | 13                                                 |
| removed                       | 0                                                  |
| internal XY drift             | 0                                                  |
| internal yaw drift            | 0                                                  |
| endpoint XY changed           | 5；max≈0.075797m，属于 canonical endpoint/拓扑增量 |
| lost incoming/outgoing        | 0 / 0                                              |
| added incoming/outgoing edges | 13 / 13                                            |

新增 13 lane IDs：5050, 5163, 5164, 5165, 5166, 5171, 5172, 5175, 5178, 5179, 5180, 5181, 5186。这个回归是“Vector V2 在旧 Full-Mine 540 条已验证路径上做严格增量完善”的关键证据。

## **11.5 Map API / 基础 runtime**

Vector V2 已在 vehicle_parameters.py、minesim_bitmap_png_loader.py、minesim_semanticmap_json_loader.py 三个 production 位置按旧 Full-Mine 模式注册，get_maps_api() 能返回 MineSimMap，road=100 / refpath=553 / dubins=565；bitmap 仍 lazy。

| **测试**      | **结果**                                                                                  |
|---------------|-------------------------------------------------------------------------------------------|
| single 1-step | PASS；trajectory finite；ego≈0.45m；v 4.5→4.614                                           |
| single 5s     | PASS；50 steps；distance≈34.724m；progress +34.800m；v≈8.938；drivable all steps          |
| dual 1-step   | PASS；A/B 同 iteration；object1 从 external observation 移除；A/B 均移动                  |
| dual 5s       | PASS；50 steps / 5.0s；advanced_exactly_5s；A/B moved；single regression safe；error=None |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>尚未冻结的版本管理点</strong></p>
<p>对话证明 V2 production registration 运行有效，但没有给出其最终 commit/tag。下一步真正 freeze 前必须先审 git diff，确认只包含授权文件，再 commit/tag/bundle；不要在本文中虚构版本号。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# **12. Vector V2 DEV Bitmap：冻结版、5186 五像素补丁、可复现 Builder 与取舍**

## **12.1 Frozen Vector V2 DEV mask**

| **项目**     | **值**                                                                                                      |
|--------------|-------------------------------------------------------------------------------------------------------------|
| 物理文件     | /root/autodl-tmp/fullmine_vector_v2_dev_mask/bitmap/geojson_full_mine_vector_v2_dev_only_mask.png           |
| runtime link | /root/autodl-tmp/new_map_fullmine_vector_v2_dev/maps/bitmap/geojson_full_mine_vector_v2_dev_bitmap_mask.png |
| SHA256       | 9f27eaaa42642b2a0daba7591268cb5fbedaed9da25c4fbdde500a6a7ec14ba3                                            |
| 尺寸/分辨率  | 46322×42411；10 px/m                                                                                        |
| 相对 V1      | added=306,667 pixels；removed=0；新增≈3066.67m²                                                             |
| Freeze 文本  | /root/autodl-tmp/new_map_fullmine_vector_v2_dev/VECTOR_V2_DEV_FREEZE.txt                                    |

## **12.2 15 条重点 path 静态中心线与 footprint**

目标集合 = 13 条 V2 新恢复 path + road484 的 lanes 6942/6989。15/15 centerline waypoint 在 frozen V2 bitmap 上 coverage=1.0。随后用官方 XG90G 9×4m、rear-axle reference 的 CarFootprint 做逐 waypoint footprint 审计。

绝大多数 footprint failure 都在 path 首尾，符合车辆前悬 6.5m / 后悬 2.5m 跨越 adjacent region 的接口 overhang；采用 0.5m relaxed endpoint guard 后只剩 lane5186 真正 deep-interior case。

## **12.3 lane 5186：唯一真实内部 corridor 缺口**

| **指标**               | **结果**                             |
|------------------------|--------------------------------------|
| 位置                   | lane5186 / road339，idx 30–34        |
| 局部曲率               | 约 0.097–0.101 1/m；半径约 9.9–10.3m |
| 3.5m corridor          | 不足以完全覆盖 XG90G 外侧车角        |
| max corner distance    | ≈3.626304m                           |
| 额外 swept vector area | ≈0.337136515m²                       |
| 超出 parent road339    | 0m²；parent geometry 足够            |
| 实际 raster 新增       | 5 pixels = 0.05m²                    |

## **12.4 Additive candidate：当前最稳 mask 候选**

| **项目**                    | **值**                                                                                                            |
|-----------------------------|-------------------------------------------------------------------------------------------------------------------|
| 文件                        | /root/autodl-tmp/fullmine_vector_v2_additive_patch_candidate/bitmap/geojson_full_mine_vector_v2_dev_only_mask.png |
| SHA256                      | d2afc84e7286d72f7fcd9a9b2000ca3701e322e06831dc11d0d0ac63325fccef                                                  |
| 相对 frozen V2              | added=5；removed=0；disk pixel exact=True                                                                         |
| manifest                    | /root/autodl-tmp/fullmine_vector_v2_additive_patch_candidate/vector_v2_additive_patch_manifest.json               |
| 15-target static regression | PASS；centerline all pass；deep interior +0.5m count=0；5186 idx30–34 pass                                        |

## **12.5 为什么没有采用“from-source 全量重建 mask”替换 frozen V2**

为了把历史一次性 V2 mask 过程固化为可复现代码，创建了 /root/autodl-tmp/fullmine_vector_v2_dev/build_fullmine_vector_v2_dev_mask.py；PLAN/BUILD 均能成功，94 source roads →100 effective，553 lane，road484 active，5186 swept patch parent-safe。

但其 full rebuild candidate 与 frozen V2 比较出现 added=1779、removed=2772（净 -993）。进一步 set-theoretic attribution 证明：candidate 没有删除任何 V1 像素（monotonic vs V1），所有差异 100% 集中在 8 条 repaired roads，属于 repaired-road rasterization 与历史 frozen 过程的边缘离散差。为了最小回归风险，决定不让 full rebuild 直接替换已通过 runtime 的 frozen V2，而采用“frozen V2 + 明确验证的 additive patch”策略。

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>可复现 Builder 的定位</strong></p>
<p>保留它作为 from-source 几何/生成参考，不把它当当前 runtime 真值。未来若要重新从源构建新版本，必须重新做 V1/V2/additive 三方像素回归和 runtime 验收。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## **12.6 大 PNG 审计优化**

Pillow 会把 1.964B 像素 PNG 判为 DecompressionBomb；为了避免每次全解码，已经生成 tiled TIFF 审计缓存：/root/autodl-tmp/new_map_fullmine_vector_v2_dev/maps/bitmap/geojson_full_mine_vector_v2_dev_bitmap_mask_tiled.tif，46322×42411、uint8、512×512 blocks、约1.844GiB。后续局部窗口审计优先 rasterio window/tiled cache。

# **13. Targeted Runtime：15 条重点 Lane、7 场景、BFS depth=5 与 7/7 Route PASS**

## **13.1 15 条重点 lane**

| **类别**        | **Lane IDs**                                                                 |
|-----------------|------------------------------------------------------------------------------|
| V2 新恢复 13 条 | 5050, 5163, 5164, 5165, 5166, 5171, 5172, 5175, 5178, 5179, 5180, 5181, 5186 |
| road484 重点    | 6942, 6989                                                                   |

## **13.2 初始 5 组压缩与长链问题**

静态拓扑压缩发现两个 6-lane component、road332 单独、road484 两个方向单独，理论上可用 5 个 scenario 覆盖全部 15 条 lane。A/B 两条 core 分别约 827m/815m，但 planner.initialize() 抛出“refline_smooth data is missing or incomplete”。

## **13.3 真正根因：GlobalRoutePathPlanner BFS hard-code target_depth=5**

源码审计确认 search_route_path(..., target_depth=5)，start path depth=0，只有 depth\<5 时继续展开，因此最多到达 depth=5，即一条 route 最多 6 个 path token。原 A/B 各需要约 13 path，实际是 route search 根本没找到，外层 IDM 只因为 refline_smooth 仍为 None 而抛了误导性报错。

解决原则：不为了地图测试修改 global planner。把长链拆成 depth-safe 场景，保持原生 target_depth=5，从 benchmark 设计侧适配。

## **13.4 最终 7 个 depth-safe 场景**

| **Scenario**        | **Expected Route (lane IDs)** | **Target lanes** | **Tokens** | **估计路程** | **max_t** |
|---------------------|-------------------------------|------------------|------------|--------------|-----------|
| A1_RECOVERED_EAST_1 | 5182→5164→5185→5181→5168→5166 | 5164,5181,5166   | 6 / depth5 | ≈203.226m    | 90s       |
| A2_RECOVERED_EAST_2 | 5170→5172→5174→5186→5177→5179 | 5172,5186,5179   | 6 / depth5 | ≈402.066m    | 140s      |
| B1_RECOVERED_WEST_1 | 5121→5178→5176→5175→5173→5171 | 5178,5175,5171   | 6 / depth5 | ≈395.826m    | 130s      |
| B2_RECOVERED_WEST_2 | 5169→5165→5167→5180→5184→5163 | 5165,5180,5163   | 6 / depth5 | ≈226.200m    | 90s       |
| C_ROAD332           | 5043→5050→5051                | 5050             | 3          | ≈55.843m     | 60s       |
| D_ROAD484_FORWARD_A | 6952→6942→6943                | 6942             | 3          | ≈54.104m     | 60s       |
| E_ROAD484_FORWARD_B | 6988→6989→6990                | 6989             | 3          | ≈37.340m     | 60s       |

## **13.5 7/7 planner route preflight**

新 manifest：/root/autodl-tmp/fullmine_vector_v2_targeted_runtime/targeted_scenario_manifest_depth5.json。隔离 map root 使用 Vector V2 semantic + d2af additive bitmap，完全不动 frozen baseline。

| **检查**                                 | **结果**     |
|------------------------------------------|--------------|
| SCENARIO_COUNT                           | 7            |
| PASS_COUNT / FAIL_COUNT                  | 7 / 0        |
| ROUTE_EXACT_MATCH                        | 7/7 True     |
| EXPECTED_FULL_ORDERED                    | 7/7 True     |
| CORE_ORDERED                             | 7/7 True     |
| TARGET_ORDERED                           | 7/7 True     |
| START_PATH_EXPECTED / GOAL_PATH_EXPECTED | 7/7 True     |
| refline_smooth                           | 7/7 成功生成 |

相关文件：targeted_planner_route_preflight_depth5.py / .json / .log 均位于 /root/autodl-tmp/fullmine_vector_v2_targeted_runtime/。这一层已经正式封账，不应再重新拆 route。

# **14. 当前正在排查的核心问题：CollisionLookup 与官方车辆几何不一致**

## **14.1 C/D/E 真实 closed-loop 已经发生了什么**

targeted_closed_loop_runtime.py 已真实执行 planner.compute_trajectory() 与 simulation.propagate()。C/D/E 的 planner route 均 exact match，车辆确实向前运动；失败发生在 harness 使用 CollisionLookup 做道路边界检测时。

| **Scenario**        | **首次 lookup failure** | **nearest route / remaining** | **已知运动证据**                             |
|---------------------|-------------------------|-------------------------------|----------------------------------------------|
| C_ROAD332           | step 9 / 0.9s           | lane5043；remaining≈2.710846m | distance≈4.448734m；尚未访问5050             |
| D_ROAD484_FORWARD_A | step 64 / 6.4s          | lane6942；remaining≈2.360921m | distance≈41.530133m；6942 已在 step22 被访问 |
| E_ROAD484_FORWARD_B | step 15 / 1.5s          | lane6988；remaining≈2.184904m | distance≈7.821299m；尚未进入6989 interior    |

三个首次失败都距离当前 path 尾部仅约 2–3m，非常符合“车辆 footprint 已跨到下一 region 接口”的位置特征。

## **14.2 interface swept-envelope probe：只解决 E，C/D 仍被 lookup 判碰撞**

| **Interface** | **新增像素** | **outside parent** | **CollisionLookup after patch** |
|---------------|--------------|--------------------|---------------------------------|
| 5043→5050     | 41 (0.41m²)  | ≈0.005205m²        | 仍 True                         |
| 6942→6943     | 22 (0.22m²)  | ≈0.001146m²        | 仍 True                         |
| 6988→6989     | 39 (0.39m²)  | ≈0.000422m²        | False（被解决）                 |

这一步证明“接口 swept envelope”思路部分有效，但也提示 C/D 剩余 failure 可能不是 bitmap 缺口，而是 CollisionLookup 自己的占用几何与 CarFootprint 不一致。于是停止继续 patch PNG，转去读源码。

## **14.3 CollisionLookup 的几何定义冲突**

| **对象/代码**                                 | **纵向范围（yaw=0 / 相同 x,y reference）**        |
|-----------------------------------------------|---------------------------------------------------|
| 官方 XG90G 参数                               | locationPoint2Head=+6.5m；locationPoint2Rear=2.5m |
| CarFootprint.build_from_rear_axle             | \[-2.5, +6.5\]m；width=4m                         |
| scenario_controller.calculate_vehicle_corners | same x/y：front=+6.5；rear=-2.5                   |
| CollisionLookup lookup 实测                   | 约 \[-6.4,+2.6\]m；width≈4m，前后方向基本反置     |

collision_lookup.py 中 MineTruckXG90G 定义 collision_lrear=6.5、collision_lhead=2.5；一个角点还使用 -collision_lrear/2，导致 lookup 形状并非标准 rear-axle rectangle。scenario_controller 又把 observation.vehicle_info\["ego"\]\[x/y/yaw\] 直接传入 CollisionLookup，而同一 x/y 在 calculate_vehicle_corners 中按 front+6.5/rear-2.5 解释。由此可以确认：MineSim 内部当前至少存在道路 CollisionLookup 与官方 CarFootprint/ScenarioController 车辆参考点约定的不一致。

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>另一个潜在源码异常（尚未触碰）</strong></p>
<p>CollisionLookup.__init__ 中 VehicleType.MineTruck_NTE200 分支目前也实例化 MineTruckXG90G。Full-Mine 当前使用 XG90G，因此本轮未修这个问题；下一位 AI 不应顺手改，除非单独建立 NTE200 回归任务。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## **14.4 当前 EXACT NEXT STEP（本手册生成时尚未执行）**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>当前最小验证</strong></p>
<p>取 C/D/E 三个真实 failure state，不再使用 CollisionLookup；用官方 CarFootprint.build_from_rear_axle(9×4m, rear=-2.5/front=+6.5) 直接逐 pixel 检查 d2af additive bitmap。若三者 BAD_PIXELS=0，则把这三次 CollisionLookup failure 定性为假阳性，并停止给 mask 加接口补丁；若某场景 BAD_PIXELS&gt;0，只补那些真实物理 footprint 缺口。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

这一步完成前，不能宣称 C/D/E targeted closed-loop PASS，也不能宣称所有 mask interface 已无问题；但同样不能继续为了满足 suspect CollisionLookup 去扩大 mask。

# **15. 全过程问题库：症状 → 根因 → 解决 → 可复用规则**

| **症状/问题**                            | **根因**                                                     | **解决**                                            | **可复用规则**                             |
|------------------------------------------|--------------------------------------------------------------|-----------------------------------------------------|--------------------------------------------|
| 云端 full build rc=137/Killed            | 容器真实 memory.max 只有2GiB，free -h 显示宿主机大内存       | 读 cgroup；必要时开高 RAM CPU 卡                    | 资源真值看 cgroup，不看表面 nproc/free     |
| nproc=192 / free=1TiB 误判               | 宿主/容器资源可见性差异                                      | cpu.max/memory.max 作为门禁                         | 任何大任务先读 cgroup                      |
| /usr/bin/time 不存在                     | 镜像缺工具                                                   | 不用它；用 shell/Python 计时                        | 命令不存在不等于程序失败                   |
| Frenet index79 越界                      | 数组长度79但硬编码 append(79)                                | 按实际最小长度 clamp/last valid                     | 接口重采样必须按真实数组边界               |
| Maneuver 内存/碰撞/接口复杂              | 候选历史、SAT、后轴语义等多处工程问题                        | 外部 Adapted wrapper；明确方法学影响                | 运行时补丁必须标注，不冒充原始算法         |
| Simple 跨地图车型错配                    | 硬编码 guangdong_dapai 车型                                  | 按 scenario initial vehicle 参数重建 model          | 车型必须来自场景/地图而非默认              |
| 旧文档状态落后                           | 项目进展快                                                   | live Git/terminal \> old Word                       | 文档必须有时间戳与证据等级                 |
| Jiangtong 第二 benchmark 无效            | 空间交叉但时间相差约9.5s                                     | 负筛选封存，不调参数强制造冲突                      | 空间冲突≠时序冲突                          |
| Dapai full-external 目标交互被打断       | object1 dominant confounder                                  | A-B only 形成干净机制证据                           | 不要把 benchmark confounder 当 reward 问题 |
| Full-Mine endpoint errors                | 共享 topo endpoint XY 不一致                                 | same topo deterministic canonical XY                | 只在同 topo ID 内 snap                     |
| 不同 topo ID 同 XY                       | auxiliary gear transition                                    | 禁止按 XY merge                                     | Topo ID 是第一事实                         |
| source coverage missing                  | validator layer mapping 漏项                                 | 显式 source→semantic layer map                      | validation 也必须覆盖新 layer              |
| boundary parent 错挂                     | 跨类别只按 object ID 搜                                      | rgn_type+rgn_objectid                               | 类别语义不能被“最近/同ID”替代              |
| road332 invalid                          | 极小 self-intersection sliver                                | make_valid 保留最大 polygon + provenance            | 几何修复必须定量评估 sliver                |
| 6 missing roads                          | road.geojson 漏 polygon                                      | 两 boundary + lane +正常 road cross-validation 重建 | 用源内部冗余恢复，不做 nearest-road 猜测   |
| road326 candidate invalid                | boundary closure 微自交                                      | make_valid 后 sliver ratio极小；IoU/Hausdorff恢复   | validity FAIL 要先诊断，不要否定整体方法   |
| road484 大偏差                           | source polygon 版本旧于 boundary/lane                        | boundary-derived effective geometry + provenance    | 版本一致性是强证据；不静默覆盖源           |
| polygon Z异常                            | polygon/boundary Z存在垂直跳                                 | elevation只取lane Z                                 | 不同 geometry layer 的 Z可信度必须分开     |
| lane6713 +0.519m seam                    | 唯一 hard lane internal jump                                 | raw Z保留+QA，不瞎平滑                              | 异常标记优先于伪造修正                     |
| 大 PNG Pillow DecompressionBomb          | 1.964B pixels 超默认限制                                     | 可信资产禁用上限/改 rasterio/tiled window           | 超大图避免 PIL 全量反复打开                |
| Rasterio PNG window写风险                | PNG BufferedDatasetWriter 不是明确 bounded-memory            | temporary tiled GeoTIFF → CreateCopy                | 大 raster 先 tiled 再转 PNG                |
| rasterize(\[\]) ValueError               | 空 tile 无 geometry                                          | 直接 zeros tile                                     | tile pipeline 必须处理空块                 |
| planner.initialize 超慢                  | 400k node nested linear scan                                 | token2ind O(1)，commit32fb429                       | 大图下算法复杂度会暴露                     |
| J117 alias 混淆 Full-Mine                | 初期借用 pilot identity                                      | 独立 geojson_full_mine_dev                          | 每张地图独立 location/version/basename     |
| V2 full rebuild 与 freeze 像素不完全一致 | 8 repaired roads raster边缘离散差                            | 保留 full builder作参考；runtime 用 frozen+additive | 可复现≠必须替换已验证基线                  |
| lane5186 deep interior failure           | 急弯时车角需要\>3.5m corridor                                | parent-safe swept patch，仅5px                      | 车辆 footprint 能揭示中心线buffer盲点      |
| A/B refline_smooth missing               | 真正是 BFS target_depth=5 route search失败                   | 拆为6-token depth-safe scenarios                    | 错误消息可能是上游失败的二次症状           |
| C/D/E distance_travelled 输出0           | exception 前总距离未写回 record                              | failure probe 在 raise 前写 diagnostics             | 异常路径也要持久化中间状态                 |
| C/D/E CollisionLookup 边界碰撞           | lookup 车辆前后定义与 CarFootprint/ScenarioController 不一致 | 停止扩mask；改做官方 footprint 真值检查             | 验证工具本身也需要一致性审计               |
| 长 heredoc/代码块乱码                    | 聊天前端将长块/输出混拼                                      | 缩短代码块、一步一块                                | 只复制代码，不复制 prompt/output           |
| 终端意外退出                             | 脚本/命令显式 exit 或 SSH中断                                | 默认不在交互shell最后 exit；用户偏好主页面直接跑    | 测试脚本返回码与 shell 存活分开            |
| sha256sum -L 假设                        | 工具参数不存在/行为理解错                                    | 普通 sha256sum 默认跟随 symlink                     | 先查工具真实行为                           |

# **16. 云端关键资产、绝对路径、哈希与“不要覆盖”的文件**

## **16.1 仓库与恢复资产**

| **资产**               | **路径/说明**                                                                          |
|------------------------|----------------------------------------------------------------------------------------|
| 正式 repo              | /root/MineSim-Dynamic                                                                  |
| 旧 Full-Mine V1 bundle | /root/autodl-tmp/MineSim-Dynamic_fullmine_dev_runtime_20260811.bundle（历史已 verify） |
| 旧 Full-Mine freeze    | d81c571 / tag fullmine-dev-runtime-pass-20260811                                       |
| 原官方成品地图         | /root/datasets/maps                                                                    |

## **16.2 源数据与 Builder**

| **资产**                             | **路径**                                                                               |
|--------------------------------------|----------------------------------------------------------------------------------------|
| 原始 GIS ZIP                         | /root/autodl-tmp/地图新建相关文件.zip                                                  |
| V1 structural builder                | /root/autodl-tmp/phase6e1_fullmine_structural_FINAL_PASS/build_full_mine_structural.py |
| V1 mask builder                      | /root/autodl-tmp/new_map_phase6f4_tools/build_dev_fullmine_mask.py                     |
| V2 semantic builder                  | /root/autodl-tmp/fullmine_vector_v2_dev/build_full_mine_vector_v2.py                   |
| V2 reproducible mask builder（参考） | /root/autodl-tmp/fullmine_vector_v2_dev/build_fullmine_vector_v2_dev_mask.py           |

## **16.3 Current Vector V2 package / mask**

| **资产**                   | **路径 / SHA**                                                                                                      |
|----------------------------|---------------------------------------------------------------------------------------------------------------------|
| V2 semantic                | /root/autodl-tmp/new_map_fullmine_vector_v2_dev/maps/semantic_map/geojson_full_mine_vector_v2_dev_semantic_map.json |
| Semantic SHA               | b85a3d8b28f2252ecb5bda179d514573f6333079def838cd048566f556d95cd0                                                    |
| Frozen V2 mask             | /root/autodl-tmp/fullmine_vector_v2_dev_mask/bitmap/geojson_full_mine_vector_v2_dev_only_mask.png                   |
| Frozen mask SHA            | 9f27eaaa42642b2a0daba7591268cb5fbedaed9da25c4fbdde500a6a7ec14ba3                                                    |
| Additive current candidate | /root/autodl-tmp/fullmine_vector_v2_additive_patch_candidate/bitmap/geojson_full_mine_vector_v2_dev_only_mask.png   |
| Additive SHA               | d2afc84e7286d72f7fcd9a9b2000ca3701e322e06831dc11d0d0ac63325fccef                                                    |
| Additive manifest          | /root/autodl-tmp/fullmine_vector_v2_additive_patch_candidate/vector_v2_additive_patch_manifest.json                 |
| Tiled audit TIFF           | /root/autodl-tmp/new_map_fullmine_vector_v2_dev/maps/bitmap/geojson_full_mine_vector_v2_dev_bitmap_mask_tiled.tif   |

## **16.4 Targeted runtime assets**

| **资产**              | **路径**                                                                                |
|-----------------------|-----------------------------------------------------------------------------------------|
| Root                  | /root/autodl-tmp/fullmine_vector_v2_targeted_runtime                                    |
| Depth5 manifest       | .../targeted_scenario_manifest_depth5.json                                              |
| Isolated map root     | .../maps（semantic→V2 semantic；bitmap→d2af additive candidate）                        |
| 7/7 route preflight   | .../targeted_planner_route_preflight_depth5.py / .json / .log                           |
| Closed-loop harness   | .../targeted_closed_loop_runtime.py                                                     |
| CDE runtime JSON      | .../targeted_closed_loop_runtime_C_ROAD332_D_ROAD484_FORWARD_A_E_ROAD484_FORWARD_B.json |
| CDE failure probe log | .../targeted_mask_failure_probe_CDE.log                                                 |

# **17. 用户实际工作流与 AI/终端协作规范（当前：不用 Codex）**

## **17.1 当前首要规则**

- 已知事实不重复；已验证阶段不重述。新 AI 先读 handoff，不要再从 Phase1 开始扫。

- 一次只推进当前一个最小步骤；每一步有明确 PASS/FAIL gate。

- AI 负责判断、设计最小验证和关键代码；用户在 AutoDL 普通终端执行并回传原始输出。

- 用户已明确“别用 Codex 了，我们自己跑”；当前工作流不再把任务交给 Codex。历史 Codex 只作为 8 月 12 日前半段证据。

- 机械动作（hash、file existence、grep、py_compile、run existing script）由普通终端完成。

- 大文件、日志、测试 harness、候选地图全部放 /root/autodl-tmp；正式仓库只保留必要 production source edits。

- 任何 terminal 代码块必须先 source conda → activate minesim → cd /root/MineSim-Dynamic。

- 用户偏好主页面直接跑；只有确实长且 SSH 风险高时才建议 screen，不能强制。

- 不要在代码块末尾随意 exit，避免把用户交互终端关掉。

- 长代码块曾两次在前端乱码；优先短脚本、短 patch、一步一块。

## **17.2 标准“观察 → 计划 → 执行 → 验收 → 冻结”循环**

1.  观察：只读核验当前环境、路径、git status、目标文件/日志；不先改。

2.  计划：AI 只给当前最小目的和 PASS/FAIL 条件；不重新描述整个项目。

3.  执行：用户普通终端运行；长任务先把前置静态检查做完，最后才开高资源卡。

4.  验收：只看当前 gate；失败只定位当前层，不回到全仓重审。

5.  冻结：关键阶段写 manifest/hash；必要时审 git diff 后精确 commit/tag/bundle。

## **17.3 资源策略**

| **任务**                                   | **推荐资源**                                               |
|--------------------------------------------|------------------------------------------------------------|
| grep/源码阅读/GeoJSON小范围/JSON preflight | 关卡/小卡即可                                              |
| tiled TIFF window audit                    | 小卡即可；避免全 PNG 解码                                  |
| full PNG decode / full footprint batch     | 建议大 RAM CPU；GPU无必要                                  |
| MineSim Full-Mine runtime                  | 建议至少16GB RAM，32GB更稳；历史 full mask路径峰值约7.87GB |
| 大卡 1TiB/192 可见值                       | 可用但通常过度；仍建议读 cgroup 真值                       |
| MCTS/NN 训练（未来）                       | 届时才考虑 GPU；当前地图工程 GPU价值低                     |

## **17.4 每次新终端的模板**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>source /root/miniconda3/etc/profile.d/conda.sh<br />
conda activate minesim<br />
cd /root/MineSim-Dynamic<br />
export PYTHONPATH=/root/MineSim-Dynamic<br />
<br />
echo "CONDA=$CONDA_DEFAULT_ENV"<br />
python --version<br />
pwd<br />
<br />
git status --short --branch</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## **17.5 终端输出回传规则**

- 回传完整 Traceback 的首尾，不只发最后一句。

- 不要把 \`(minesim) root@...#\` prompt 再粘回 Bash。

- 不要把 AI 的“预期输出示例”连同命令一起粘贴。

- 如果前端把长代码混入输出，立即停止，改成更短块；不要继续在损坏脚本上补丁叠补丁。

- 对 long runtime：记录 log/result JSON，不仅依赖屏幕输出。

# **18. 当前下一步、验收门与后续地图完善路线**

## **18.1 当前唯一应先做的步骤**

对 C/D/E 的真实 failure state，使用官方 CarFootprint 而不是 CollisionLookup，直接检查 d2af additive mask。该检查只需回答 BAD_PIXELS 是否为 0。

| **结果**                | **下一步**                                                                                                                                       |
|-------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------|
| C/D/E 全部 BAD_PIXELS=0 | 记录 CollisionLookup false-positive evidence；targeted harness 的“地图真实性”判据改用官方 CarFootprint+bitmap；继续跑 C/D/E；不要再 patch mask。 |
| 部分 BAD_PIXELS\>0      | 只对这些场景做真实 physical gap 差集；补 parent-supported 必要像素；重新静态 footprint + closed-loop。                                           |

## **18.2 Targeted runtime 全部通过后的冻结门**

- C/D/E closed-loop：route exact、target visited、goal reached、CarFootprint drivable all steps。

- A1/A2/B1/B2 用同一 harness 运行，覆盖其 12 个 recovered target lanes；必须按 target order 访问并到 goal。

- 汇总 15 target lanes 的真实 runtime coverage，而不是只看 planner preflight。

- 审 Vector V2 当前 git diff；确认 production 修改集合；py_compile / regression；再决定 commit/tag（名称 TBD，不预先虚构）。

- 生成 Vector V2 freeze manifest（semantic SHA、final mask SHA、scenario/run JSON、known issues）、Git bundle。

## **18.3 地图“尽可能完善”的后续路线**

| **优先级** | **任务**                             | **目的**                                                                                                |
|------------|--------------------------------------|---------------------------------------------------------------------------------------------------------|
| P0         | 完成 15-target real closed-loop      | 证明本轮 8 repair / 13 recovered path / road484 的真实软件执行                                          |
| P0         | 全矿代表性区域 coverage              | 继续选择 road/junction/loading/unloading/auxiliary 的 representative routes；不只验证 J117/repair roads |
| P0         | 获取 authoritative drivability       | 向数据提供方索取 production mask / drivable surface / internal exclusions / mask authoring rule         |
| P1         | CollisionLookup 单独 bug ticket      | 把 XG90G 前后参考点与 NTE200 分支问题独立处理；避免把地图验收和引擎 bug 混在一起                        |
| P1         | auxiliary semantic API（如后续需要） | 当前 semantic 有6个 auxiliary_area，但 production API 支持有限                                          |
| P1         | 真实车型确认                         | 当前 Full-Mine alias XG90G；若现场真实车辆不同，建立独立 vehicle config                                 |
| P2         | Full-Mine 多场景 MCTS                | 地图 runtime coverage 稳定后再把算法主线扩到全矿                                                        |
| P2         | Neural-MCTS / adaptive budget        | 基于更多场景数据，优先解决“何时需要高预算”而不是盲目固定300                                             |

# **19. 风险边界、未知项与论文/汇报中禁止越界的表述**

| **项目**           | **当前可说**                                                                | **不能说**                                                                      |
|--------------------|-----------------------------------------------------------------------------|---------------------------------------------------------------------------------|
| Vector V2 Semantic | 源 GIS 高度可追溯；100 effective roads / 553 paths；8 repairs 有 provenance | “官方 production HD map”                                                        |
| Bitmap             | DEV/Research mask；当前 additive candidate 只做明确最小补丁                 | “等同官方 Dapai/Jiangtong production mask”                                      |
| road484            | 证据强烈支持 source polygon stale，effective 使用 boundary-derived          | “boundary-derived 就是官方最终可行驶面”                                         |
| Elevation          | raw lane Z 高置信可作为 semantic elevation candidate；datum 未验证          | “绝对高程基准已验证”                                                            |
| Slope              | 官方单位为 degree；当前生成规则未完整复现，V2 slope=0                       | “已经恢复完整坡度模型”                                                          |
| CollisionLookup    | 存在明确几何不一致证据                                                      | 在官方 CarFootprint failure-state check 前直接说所有 runtime failure 都是假阳性 |
| MCTS               | 当前有限场景有明确安全/任务收益；J117双车5 seed有机制证据                   | “全场景安全/全面优于所有 planner”                                               |
| Neural-MCTS        | 未来路线、有448早期专家样本                                                 | “已经训练完成网络/已经实现 PUCT”                                                |

# **20. 可直接交给下一位 AI 的接管 Prompt**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>使用方式</strong></p>
<p>把下面内容连同本 Word 一并交给新 AI。新 AI 第一个动作只能是只读核验，不得 reset/clean，也不得重新跑已冻结阶段。</p></th>
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
<th>source /root/miniconda3/etc/profile.d/conda.sh<br />
conda activate minesim<br />
cd /root/MineSim-Dynamic<br />
你正在接管 MineSim-Dynamic。先完整阅读《MineSim-Dynamic_项目完整进展与云端AI接管超级手册_2026-08-12.docx》。<br />
<br />
事实优先级：live AutoDL/Git &gt; 2026-08-12 runtime/log/artifact &gt; 本手册 &gt; 2026-08-11/08-09/08-06 历史文档。<br />
<br />
正式 repo=/root/MineSim-Dynamic，conda=minesim，Python=3.9.25。不要 git clean -fd / reset --hard / add .。<br />
<br />
当前旧冻结基线：newmap-j117-dev @ d81c571，tag fullmine-dev-runtime-pass-20260811。注意：Vector V2 注册已经在运行环境中生效，但最终 commit/tag 未在对话中明确，必须先 git status/diff，不能假设 d81c571 仍是当前 V2 HEAD。<br />
<br />
当前地图：geojson_full_mine_vector_v2_dev，semantic=100 roads/553 paths，8 road repair provenance；semantic SHA=b85a3d8...。当前 runtime bitmap candidate 是 frozen V2 + lane5186 5 pixels，SHA=d2afc84e...。不要替换为 full rebuild candidate。<br />
<br />
7 个 depth-safe targeted scenarios 的 planner route 已 7/7 exact PASS，不再重做 route search。当前 closed-loop 只卡在 C/D/E 的道路边界判定：CollisionLookup XG90G lookup extents 约[-6.4,+2.6]，与官方 rear-axle CarFootprint [-2.5,+6.5] 相反；ScenarioController 同一 x/y 也按 front+6.5/rear-2.5 解释。<br />
<br />
当前唯一下一步：使用官方 CarFootprint 对 C/D/E 已记录 failure state 直接检查 d2af additive bitmap 的 BAD_PIXELS。若全 0，停止给 mask 打补丁，记录 CollisionLookup false positive，继续 C/D/E/A1/A2/B1/B2 targeted runtime；若非 0，只修真实 physical gap。<br />
<br />
用户工作流：任何终端代码前先 source conda + activate minesim + cd /root/MineSim-Dynamic；一次只做一个最小步骤；用户普通终端执行；当前不要用 Codex；大文件/日志放 /root/autodl-tmp；长代码块拆短，终端不要自动 exit。<br />
<br />
先只读核验 git status、关键文件存在性与当前 result JSON，然后告诉用户：CURRENT_STATE / NEXT_ONE_STEP / RISKS。不要重新讲已完成阶段。</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# **附录 A. Commit / Tag 速查**

| **阶段**                   | **Commit/Tag**                                        | **状态**                               |
|----------------------------|-------------------------------------------------------|----------------------------------------|
| IDM baseline               | 2521aa41… / idm-replay-autodl-baseline                | 历史稳定锚点                           |
| Pure MCTS + expert         | 94693dc… / mcts-expert-dataset-v1-20260802            | 已冻结                                 |
| Fleet reward / Dapai multi | f8ff186…                                              | 历史多车节点                           |
| Jiangtong V22 screening    | 94794c9… / jiangtong-v22-benchmark-screening-20260809 | 已封存负结果                           |
| J117 Map API               | 4bd2bff… / j117-phase3-production-map-load-20260809   | 已冻结                                 |
| J117 minimal/full-route    | ec1c958… / phase4b & phase4c tags                     | 已冻结                                 |
| J117 dual Pure MCTS        | da4105b… / j117-phase5-dual-ego-pure-mcts-20260810    | 已冻结                                 |
| Full-Mine lookup perf      | 32fb429…                                              | 已提交                                 |
| Full-Mine V1 registration  | d81c571… / fullmine-dev-runtime-pass-20260811         | 旧 Full-Mine 冻结点                    |
| Vector V2                  | commit/tag TBD                                        | 运行证据存在；必须 live Git 审计后冻结 |

# **附录 B. Vector V2 关键数量、Target Lane/Route 速查**

| **指标**        | **值**                                |
|-----------------|---------------------------------------|
| source roads    | 94                                    |
| effective roads | 100                                   |
| repair records  | 8                                     |
| polygons        | 184                                   |
| reference_path  | 553                                   |
| dubins_pose     | 565                                   |
| borderline      | 402                                   |
| waypoint        | 314,692                               |
| elevation range | 1009.048236–1321.000000               |
| slope           | 0.0（未复现 official smoothing rule） |
| frozen mask     | 46322×42411 @10px/m；SHA 9f27eaaa…    |
| additive mask   | frozen + 5px；SHA d2afc84e…           |

| **Lane** | **V2 path token/备注**                   |
|----------|------------------------------------------|
| 5050     | path-000254；road332 restored            |
| 5163     | path-000285                              |
| 5164     | path-000286                              |
| 5165     | path-000287                              |
| 5166     | path-000288                              |
| 5171     | path-000293                              |
| 5172     | path-000294                              |
| 5175     | path-000297                              |
| 5178     | path-000300                              |
| 5179     | path-000301                              |
| 5180     | path-000302                              |
| 5181     | path-000303                              |
| 5186     | path-000308；lane interior 5-pixel patch |
| 6942     | path-000510；road484                     |
| 6989     | path-000542；road484                     |

# **附录 C. 证据文件索引与阅读优先级**

| **ID** | **证据源**                                                                        | **主要支持**                                                                         |
|--------|-----------------------------------------------------------------------------------|--------------------------------------------------------------------------------------|
| S0     | 2026-08-12 当前聊天 + 终端上传：154012 / 154456 / 155502 / 155706 / 155821 等 txt | Vector V2 planner/runtime、CollisionLookup、CarFootprint/ScenarioController 最新证据 |
| S1     | 粘贴的文本 (1).txt（2026-08-12 长记录）                                           | 当日 Codex/终端源审计、road修复、Z审计、V2 semantic/mask/runtime 的完整演进          |
| S2     | MineSim-Dynamic_新地图项目云端交接手册_2026-08-11.docx                            | Full-Mine V1 基线、DEV mask、single/dual runtime、问题复盘、工作流                   |
| S3     | MineSim-Dynamic_云端项目完整交接与工作流手册_2026-08-09.docx                      | J117 Phase1–4C、多车 MCTS 背景、AutoDL/Codex 历史工作流                              |
| S4     | MineSim-Dynamic_项目全景档案与AI长期接管超级手册_2026-08-06.docx                  | IDM→Pure MCTS→五 Planner 历史、实验治理、云端风险                                    |
| S5     | MineSim-Dynamic_MCTS接入与实验评估报告_20260802.docx                              | MCTS 方法、参数、两场景正式结果、448专家样本                                         |
| S6     | MineSim-Dynamic_MCTS在线闭环对比与搜索预算分析2026-08-07.docx/pdf                 | 五 Planner 在线公平性与 Budget 50/100/200/300                                        |
| S7     | 矿山项目原论文.pdf                                                                | MineSim 原系统、semantic layer、elevation/slope/vehicle 参数的官方论文依据           |
| S8     | 地图新建相关文件.zip                                                              | Full-Mine 原始 8 类 GeoJSON + 1.png；任何 V2 source truth 的根源                     |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>最终接管原则</strong></p>
<p>本手册的目标不是让下一位 AI “从头再验证一次”，而是让它知道哪些阶段已经冻结、哪些结论来自什么证据、当前只剩哪一个最小未闭合 gate。任何 AI 如果不能在 5–10 分钟内指出“当前下一步是官方 CarFootprint 对 C/D/E failure state 的 bitmap 真值检查”，说明它尚未真正接管项目。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>
