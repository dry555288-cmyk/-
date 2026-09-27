**MineSim-Dynamic**

**全项目进展、FullMine Vector V4 新地图冻结与云端 AI 长期接管超级手册**

从 IDM Baseline / Pure MCTS / 五 Planner / J117 Pilot / Full-Mine V1 / Vector V2 到最终 V4 Runtime Freeze

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>当前冻结结论</strong></p>
<p>科研 / 算法 benchmark 新地图：READY + FROZEN</p>
<p>Production-authoritative drivability：NOT PROVEN</p>
<p>Final commit: 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e</p>
<p>Final tag: fullmine-vector-v4-runtime-freeze-20260814</p>
<p>Final bitmap SHA256: 51abcd5a86e5c510204a5dacc873691506d721f98982ab7f98585d4e0f7efdd0</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

文档定位：项目交接 / 云端恢复 / AI 接手 / 地图完成度解释 / 问题复盘 / 后续研究路线

证据截止：2026-08-14 AutoDL 终端、Git、SHA、runtime 输出 + 用户上传历史交接文档

# **0. 先读这一章：五分钟接管摘要与事实规则**

## **0.1 30 秒结论**

项目已经从“能不能把新矿区数据转成 MineSim 地图”推进到“FullMine Vector V4 作为科研/算法基线已经完成 targeted runtime 验收并用 Git commit/tag 冻结”的阶段。当前新地图的 semantic 主体仍是 Vector V2：100 个 effective road、553 条 reference_path、565 个 dubins_pose、184 个 polygon，并保存 314,692 个 lane waypoint 的 raw elevation；V3/V4 主要是围绕真实闭环轨迹做 bitmap additive patch 和最终 runtime freeze，不应误解为 semantic 又重做了两版。

最终 targeted acceptance 为 7/7：A1/A2/B1/B2 在 v3 strict 下通过，并由 v4 “只新增 3 个可行驶像素、0 removed、0 other change”的单调性继承；C/D/E 在最终 v4 下直接 strict 通过。另对旧 Jiangtong 场景做了 249 step IDM 回归，车辆碰撞 0、道路边界碰撞 0、strict safety=True。源码五文件通过 py_compile 和 git diff --check，精确 stage 后提交为 112d2bd…，annotated tag 为 fullmine-vector-v4-runtime-freeze-20260814。

因此，当前地图可以作为 FullMine 后续单车/双车规划、IDM/Pure MCTS/Fleet MCTS 场景扩展与 benchmark 的正式研究基线；但仍不能宣称它与广东大排/江西江铜的成品 production mask 同级，也不能宣称全矿每一米、每种车型、每种运营方向都已经穷举验证。Production validity 的主要阻塞已从“代码/地图结构问题”转变为“缺权威 drivable surface、内部禁行/障碍层、官方 mask authoring rule 与真实运营语义”。

## **0.2 当前唯一应视为“最新真相”的锚点**

| **项目**                        | **当前值**                                                       |
|---------------------------------|------------------------------------------------------------------|
| **正式仓库**                    | /root/MineSim-Dynamic                                            |
| **Conda**                       | minesim；Python 3.9.25                                           |
| **分支**                        | newmap-j117-dev                                                  |
| **冻结 commit**                 | 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e                         |
| **冻结 tag**                    | fullmine-vector-v4-runtime-freeze-20260814                       |
| **Final V4 bitmap SHA**         | 51abcd5a86e5c510204a5dacc873691506d721f98982ab7f98585d4e0f7efdd0 |
| **Final targeted manifest SHA** | f8d95af33ebc71b88ace93c3e538bec3761e80d7a9b610a2bed7408fada4ea2b |
| **Final freeze manifest SHA**   | 30326ee281799410359900c00ca2b1f4a89290f9f0ba9366d30e8c939f4bfdaa |
| **Postcommit record SHA**       | 5a6287cd6433641cfc33ce725bf0e4f1f8dc1796b91d86dbd5bebf3c39968300 |
| **当前工作区最后一次状态**      | 仅 ?? ^C；未进入 commit/tag；不要 git clean                      |

## **0.3 事实等级与文档冲突处理**

| **标签**                   | **含义**                                        | **使用规则**                       |
|----------------------------|-------------------------------------------------|------------------------------------|
| **\[V\] Verified**         | 当前 Git / 终端 / SHA / 代码 / runtime 直接支持 | 可作为当前事实；重连云端后仍先复核 |
| **\[D\] Derived**          | 由已验证数据计算出的推导                        | 可用，但必须写清计算定义与前提     |
| **\[DD\] Design Decision** | 为了集成/实验做的工程选择                       | 不能冒充真实矿场事实               |
| **\[H\] Historical**       | 旧 Word、旧 commit、旧实验快照                  | 只用于理解演进，不能覆盖当前云端   |
| **\[U\] Unknown**          | 资料不足或缺权威语义                            | 必须显式保留未知，禁止静默猜测     |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>事实优先级</strong></p>
<p>1) 当前 AutoDL Git / 源码 / terminal / SHA / runtime</p>
<p>2) /root/autodl-tmp 中 manifest、validation JSON、result JSON、log</p>
<p>3) 本手册（2026-08-14）</p>
<p>4) 2026-08-13 / 08-12 / 08-11 / 08-09 / 08-06 历史交接文档</p>
<p>5) 示例代码、旧假设、模型记忆</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## **0.4 接手后绝对不要直接做的事情**

> **•** 不要 git clean -fd、git reset --hard、git add .；仓库长期存在有价值的 untracked/backup。
>
> **•** 不要修改 frozen tag；任何后续地图/算法工作都从 112d2bd… / final tag 新开分支。
>
> **•** 不要覆盖 d2af、candidate v1/v2/v3/v4 任何 bitmap；新 patch 必须新目录、新 SHA、additive-only。
>
> **•** 不要把旧 combined C/D/E JSON 或 stale v3 7/7 manifest 当最终证据；它们曾造成 5/7 假汇总。
>
> **•** 不要因为 CollisionLookup 命中黑像素就直接扩大 mask；必须先用标准物理 footprint / exact positive-area truth 判定。
>
> **•** 不要把 FullMine V4 称为“官方 production HD Map”；当前是 DEV/Research map，production drivability 尚无权威输入。
>
> **•** 不要按 XY 接近自动合并不同 topology ID；FullMine auxiliary gear transition 中存在真实“同 XY / 不同 topo”。
>
> **•** 不要自动修 lane6713 的 Z seam、gear=-1 方向或 slope；这些仍缺权威规则。
>
> **•** 不要把 terminal 的 No screen session found（启动前清旧 session）误判为新任务失败；先看 rc/log/Python process。
>
> **•** 不要在交互 shell 的长脚本尾部随意 exit；之前已导致终端被关闭。

## **0.5 新 AI 第一轮只读核验命令**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>cd /root/MineSim-Dynamic<br />
source /root/miniconda3/etc/profile.d/conda.sh 2&gt;/dev/null || true<br />
conda activate minesim<br />
export CUDA_VISIBLE_DEVICES=""<br />
<br />
git branch --show-current<br />
git rev-parse HEAD<br />
git status --short<br />
git show --no-patch --decorate fullmine-vector-v4-runtime-freeze-20260814<br />
cat /sys/fs/cgroup/cpu.max<br />
cat /sys/fs/cgroup/memory.max</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

期望 HEAD 为 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e，tag 指向该 commit；最后一次已知 status 只剩 \`?? ^C\`。如果实际不一致，只读调查原因，不要 reset。

# **1. 本手册的证据来源、覆盖范围与 Codex/AI 归属说明**

## **1.1 用户提供/上传的主要资料**

| **日期**      | **资料**                                         | **主要用途**                                                             |
|---------------|--------------------------------------------------|--------------------------------------------------------------------------|
| 2026-08-06    | MineSim-Dynamic_项目全景档案与AI长期接管超级手册 | IDM/MCTS/五 Planner、早期 benchmark、工程历史                            |
| 2026-08-09    | MineSim-Dynamic_云端项目完整交接与工作流手册     | 云端、Codex、Git、安全纪律、J117 前后状态                                |
| 2026-08-11    | MineSim-Dynamic_新地图项目云端交接手册           | J117→FullMine V1 structural/mask/identity、与 Dapai/Jiangtong 对比       |
| 2026-08-12    | MineSim-Dynamic_项目完整进展与云端AI接管超级手册 | Vector V2 semantic、bitmap、15 target、7 scenarios、CollisionLookup 起点 |
| 2026-08-13    | MineSim项目云端接手与技术总览                    | CollisionLookup、candidate v1/v2、A/B shadow、A1 endpoint、A2 blocker    |
| 2026-08-13~14 | 多份 terminal 对话/粘贴日志                      | 真实 cloud 输出、SHA、shadow/V3 builder、planner 修复、v4、final freeze  |
| 2026-08-14    | 当前对话直接 terminal 输出                       | 7/7、旧图回归、static/stage/freeze/commit/tag 最终事实                   |

本手册不是简单把旧 Word 拼接在一起。旧文档只作为历史证据；任何状态冲突都用更晚的 cloud terminal、源码 SHA 和 runtime 结果覆盖。例如 8 月 12 日文档仍写 Targeted Runtime “IN PROGRESS”，而 8 月 14 日已经完成 7/7、旧图回归、commit/tag。

## **1.2 关于“今天 Codex 做了什么”的严谨表述**

可从真实对话记录确认：本轮曾为 Codex 准备严格的 P0 任务，只允许抓 C/D/E exact failure state 和执行真值检查，明确禁止先改 mask、调 MCTS 或跑无关全量实验；同时用户一直强调省钱优先，Codex 默认使用 gpt-5.6-luna medium，只有真正困难/关键复核才临时升 Terra/Sol。机械检查、hash、长 build、runtime 由普通 terminal/Python 执行。

后续很多脚本/修复是在“聊天 AI 设计 + 用户 AutoDL 终端执行 + 必要时 Codex 做边界明确的代码/诊断任务”的混合流程中形成。现有资料并不能可靠标注每一行 V3 builder 或 planner patch 的“作者是谁”，因此本手册不虚构归属；所有技术结论均以最终源码、SHA、manifest 和 runtime 输出为事实源。这比把成果简单标记为“Codex 写的”更可复核。

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>证据锚点（用于接手者复核）</strong></p>
<p>• 历史 Codex 模型/成本规范：默认 Luna medium；shell/python 完成不需模型的查询。</p>
<p>• 2026-08-13 terminal 记录：CODEX_TASK_P0.txt 只抓 exact failure state/真值，不改 mask/MCTS。</p>
<p>• 2026-08-14 最终验收、Git freeze 均由 AutoDL terminal 输出直接确认。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# **2. 项目定义、研究主线与 MineSim 当前闭环架构**

## **2.1 一句话定义**

MineSim-Dynamic 是面向露天矿非结构化道路无人矿卡的场景化闭环仿真与规划研究项目。当前项目不是“只写一个 MCTS”，而是四条相互依赖的主线：MineSim 仿真链可靠复现、规划算法（IDM/Pure MCTS/Fleet MCTS）、benchmark/场景设计、真实 GIS 新矿区地图工程。

## **2.2 当前闭环调用链**

| **层**         | **当前实现**                                                  | **作用**                                                         |
|----------------|---------------------------------------------------------------|------------------------------------------------------------------|
| Scenario       | Scenario JSON / ScenarioFileBaseInfo / MineSimDynamicScenario | 起点、目标、dt/max_t、其他车辆轨迹、map location                 |
| Map            | MineSimMap + Semantic + Bitmap                                | semantic 提供 road/path/topology；bitmap 提供道路边界/可行驶栅格 |
| Planning       | GlobalRoutePathPlanner + AbstractIDMPlanner / MCTS            | 初始化全局路线/refline；每帧 compute trajectory                  |
| Control        | TwoStageController -\> iLQR/LQR                               | 跟踪 planner 轨迹并输出控制                                      |
| Ego update     | Kinematic Bicycle Model / controller propagate                | 按车辆模型积分到下一帧                                           |
| Observation    | replay/reactive/prediction                                    | 更新其他 actor，并将当前 observation 送给下一次 planner          |
| Safety/Metrics | vehicle geometry + bitmap + goal + history                    | 碰撞、道路边界、goal、效率、平顺、日志                           |

新地图工作为什么复杂：semantic、bitmap、scenario、planner、controller、vehicle geometry 任一层出现参考点/尺度/拓扑不一致，都可能被“地图越界”表象掩盖。此次 CollisionLookup 与 planner 的两个历史 bug 正是通过真实 closed-loop 把问题暴露出来。

## **2.3 当前研究主线状态**

| **子系统**               | **状态**        | **当前事实**                                                         |
|--------------------------|-----------------|----------------------------------------------------------------------|
| **IDM baseline**         | PASS/FROZEN     | 历史稳定锚点，仍是重要回归 planner                                   |
| **Pure MCTS 单车**       | PASS            | Dapai/Jiangtong 有正式闭环结果；448 strict expert samples            |
| **五 Planner + Budget**  | PASS/HISTORICAL | MCTS/IDM/Adapted Frenet/Adapted Maneuver/Simple；预算 50/100/200/300 |
| **Fleet/Multi MCTS**     | PASS            | Dapai 双受控机制 + J117 dual-ego Pure MCTS 5 seed                    |
| **J117 Pilot**           | FROZEN          | 真实 GIS 小区域金标准回归                                            |
| **FullMine Vector V4**   | FROZEN          | 7/7 targeted + old-map regression + commit/tag                       |
| **FullMine 多区域 MCTS** | NEXT            | 软件接口具备；尚未形成全矿代表性统计 benchmark                       |
| **Neural-MCTS**          | NOT STARTED     | 有专家样本/路线；无正式网络、checkpoint、PUCT 训练结论               |

# **3. 项目完整时间线：从 IDM Baseline 到 FullMine V4 Freeze**

| **日期**        | **阶段**                       | **结果/意义**                                                                                                                           |
|-----------------|--------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------|
| 2026-07-22      | 新地图接入框架                 | 明确 Raster/Semantic/Scenario 三类地图成果与新矿区接入思路。                                                                            |
| 2026-07-26      | IDM Baseline                   | commit 2521aa4…；tag idm-replay-autodl-baseline；建立云端/Git/AI 安全规范。                                                             |
| 2026-07-30~31   | Pure MCTS 闭环                 | MCTSPlanner 外壳、状态/动作/搜索/奖励、轨迹适配、iLQR/确定性修复。                                                                      |
| 2026-08-01      | Jiangtong 几何/安全            | CV/CTRV、buffer、viability、clearance 等迭代。                                                                                          |
| 2026-08-02      | MCTS 正式结果 + 专家数据       | commit 94693dc…；Dapai/Jiangtong；448 strict expert samples。                                                                           |
| 2026-08-03~07   | 五 Planner / fairness / Budget | 统一 evaluator；Adapted Frenet/Maneuver/Simple；budget 50/100/200/300。                                                                 |
| 2026-08-08~09   | Multi/Fleet MCTS               | Dapai 双受控时序机制；Jiangtong V22 因约 +9.496s 时序差被负筛选。                                                                       |
| 2026-08-09      | J117 Phase1-4C                 | 真实 GeoJSON pilot -\> Map API -\> minimal Scenario -\> 423 step/42.3s 单车全路线。                                                     |
| 2026-08-10      | J117 Phase5                    | dual-ego production runtime + Pure MCTS；5 seeds benchmark/swept safety 通过；commit da4105b。                                          |
| 2026-08-11      | FullMine V1                    | full structural、DEV_ONLY mask、token2ind O(1)、独立 geojson_full_mine_dev；single/dual smoke；tag fullmine-dev-runtime-pass-20260811。 |
| 2026-08-12 上午 | 源数据最大利用审计             | 6 missing roads、road332/484、Z、topology；从保守排除转为有 provenance 的有效修复。                                                     |
| 2026-08-12 中午 | Vector V2 Semantic             | 100 effective roads / 553 paths / 8 repairs / raw lane Z；V1-\>V2 增量回归。                                                            |
| 2026-08-12 下午 | V2 Bitmap + Targeted           | lane5186 5px；15 lanes；7 depth-safe scenarios；planner route 7/7。                                                                     |
| 2026-08-13      | CollisionLookup + C/D/E        | XG90G 前后悬/梯形 bug + exact SAT fallback；candidate v1/v2；C/D/E 一度关闭。                                                           |
| 2026-08-13      | A/B shadow + planner           | A1 route-end virtual lead 4.5m bug；A2 中途停车进一步诊断；形成独立 shadow workflow。                                                   |
| 2026-08-13~14   | Steering-rate planner fix      | A2 真正 blocker 收敛为高速下转向速率不可行；建立曲率/转向速率 speed profile + backward braking envelope；A/B shadows 全通过。           |
| 2026-08-14      | V3 exact trajectory patch      | 基于 A1/A2/B1/B2 最终真实轨迹 exact footprint 扫描，+724px，A/B strict 全通过。                                                         |
| 2026-08-14      | V4 D patch                     | current-planner D 在 v3 step66 暴露 3px 真物理 gap；72-state shadow -\> v4 +3px；D/C/E v4 strict 通过。                                 |
| 2026-08-14      | 最终 7/7 + 旧图回归            | final acceptance 7/7；Jiangtong IDM 249 steps，0 vehicle collision、0 road boundary collision。                                         |
| 2026-08-14      | Git freeze                     | 5-file static/stage gate -\> commit 112d2bd… -\> annotated tag fullmine-vector-v4-runtime-freeze-20260814。                             |

# **4. 新地图与原项目两个成品地图的异同：到底“做到什么程度”**

## **4.1 先澄清三张地图与 J117 的关系**

“之前的两个地图”指原项目中已经作为成品资产使用的广东大排（guangdong_dapai, v1.6）与江西江铜（jiangxi_jiangtong, v1.5）。J117 不是第三张原始地图，而是从用户 FullMine 原始 GeoJSON 中切出的真实 junction pilot，用来证明新 GIS 数据能够贯通 Map API -\> Scenario -\> Planner -\> Controller -\> Runtime/MCTS。FullMine 才是本轮真正的新全矿地图。

FullMine 当前通常被简称“Vector V4”，但严格分层应写成：Vector V2 semantic + 最终 V4 bitmap/runtime freeze + 当前 planner/CollisionLookup 修复。目录和 map identity 仍保留 \`geojson_full_mine_vector_v2_dev\`，这是为了保持已经验证的 semantic identity；不要为了名字好看而重命名冻结资产。

## **4.2 三张地图详细对比**

| **对比项**                        | **广东大排**                   | **江西江铜**              | **FullMine Vector V4**                                                          |
|-----------------------------------|--------------------------------|---------------------------|---------------------------------------------------------------------------------|
| **身份**                          | guangdong_dapai                | jiangxi_jiangtong         | geojson_full_mine_vector_v2_dev / V4 runtime freeze                             |
| **原始来源**                      | 外部 MineSim HD Maps 成品      | 外部 MineSim HD Maps 成品 | 用户原始 8 类 GeoJSON -\> 本项目 converter + source/effective provenance        |
| **版本/定位**                     | 1.6；原项目成品资产            | 1.5；原项目成品资产       | DEV/Research；final runtime tag 20260814                                        |
| **Semantic**                      | 成品 semantic                  | 成品 semantic             | 本项目生成；100 effective roads / 553 reference_path / 565 dubins / 184 polygon |
| **Bitmap**                        | 成品 PNG mask                  | 成品 PNG mask             | 本项目 DEV mask；d2af -\> v1 -\> v2 -\> v3 -\> v4 additive evidence chain       |
| **Mask authoring rule**           | 未公开                         | 未公开                    | 工程规则/patch 证据透明；但不等于权威 production rule                           |
| **Scale/值**                      | 10 px/m；0/255-\>bool          | 10 px/m；0/255-\>bool     | 10 px/m；0/255-\>bool；46322x42411                                              |
| **whole polygon=drivable**        | 否                             | 否                        | 否；明确拒绝 whole-polygon 填白                                                 |
| **主要车辆**                      | XG90G 9x4m                     | NTE200 13x6.7m            | 当前 FullMine alias/targeted 几何使用 XG90G 9x4m                                |
| **Semantic 可追溯性**             | 只有成品资产；authoring 不透明 | 同左                      | 强：source inventory 与 8 repair records 分离，repair 有 provenance             |
| **Production drivability 权威性** | 高于新地图：成品资产           | 高于新地图：成品资产      | 未证明；缺 authoritative drivable surface/internal exclusions                   |
| **单/双车接口**                   | 原生/本项目扩展可用            | 原生/本项目扩展可用       | Map API + single/dual 基础 runtime 已通过；7 targeted closed-loop 已验收        |
| **MCTS 证据**                     | 历史单车/多车 benchmark        | 历史单车 benchmark        | J117 上 Pure MCTS 已证明同源 GIS 链；FullMine V4 全矿代表性 MCTS 尚未形成       |
| **auxiliary**                     | 原 production API 支持有限     | 同左                      | semantic 有 6 auxiliary_area；API 后续如需再扩                                  |
| **最安全表述**                    | 原项目成品地图                 | 原项目成品地图            | 科研/benchmark-ready 的新地图；不是 production-certified                        |

## **4.3 为什么不能用“polygon 全白”复制老地图**

对 Dapai/Jiangtong 成品 semantic polygon 与成品 mask 的审计已经证明：polygon 内存在大量 non-drivable 内部区域。约略 drivable 比例：Dapai road 74.5%、junction 80.8%、loading 68.2%、unloading 73.9%；Jiangtong road 58.9%、junction 68.0%、loading 44.0%、unloading 71.4%。因此，“只要在 road/junction/load/unload polygon 内就全部可行驶”与原项目成品地图习惯不一致。

| **类别**  | **Dapai polygon 内 drivable（约）** | **Jiangtong（约）** |
|-----------|-------------------------------------|---------------------|
| road      | 74.5%                               | 58.9%               |
| junction  | 80.8%                               | 68.0%               |
| loading   | 68.2%                               | 44.0%               |
| unloading | 73.9%                               | 71.4%               |

## **4.4 新地图当前能做什么**

> **•** 作为 MineSim-compatible 研究地图加载：Semantic/Bitmap 走 production Map API 路径，支持 road/reference_path/topology 查询。
>
> **•** 构造并运行新的单车/双车 Scenario；已有 basic single/dual smoke 及 7 个 targeted real closed-loop 证据。
>
> **•** 在已验证路径上使用当前 IDM/控制器/KBM 完成 route exact、target order、goal、drivable 全套闭环验收。
>
> **•** 作为后续 Pure MCTS / Fleet MCTS 全矿 benchmark 的正式基线：软件接口已经具备；后续应从 frozen tag 新建实验分支。
>
> **•** 支持从 553 条 reference_path 中继续抽取代表路线；尤其可扩充 road/junction/loading/unloading/auxiliary 多区域 coverage。
>
> **•** 使用 raw lane Z 作为 semantic elevation candidate，支持比纯 2D 更丰富的地图语义；但 slope 仍为 0，datum/smoothing 未权威验证。
>
> **•** 精确回放/复核当前 15 条重点 target lane：13 条 V2 recovered lanes + road484 的 6942/6989。

## **4.5 新地图当前不能证明什么**

> **•** 不能证明与真实矿区 production 可行驶区域逐像素一致。
>
> **•** 不能证明 553 条 path、100 个 effective road 的每一米都已被 closed-loop 穷举。7/7 是针对 15 个重点 target lane 的深度验证。
>
> **•** 不能证明 gear=-1 的 50 条 lane 运营方向已由矿方确认；当前保持 source topology orientation。
>
> **•** 不能证明 boundary/polygon Z 可作为高程真值；当前只信 lane Z，且 slope authoring rule 未完整复现。
>
> **•** 不能证明 Jiangtong 的 NTE200 CollisionLookup 车型分支语义正确；selector 是历史 bug，目前仍会实例化 XG90G。
>
> **•** 不能宣称 FullMine 上 Pure/Fleet MCTS 已形成全矿统计结论；目前 J117 双车 MCTS 最完整。
>
> **•** 不能宣称 Neural-MCTS 已训练完成。

# **5. J117 Pilot：为什么它是新地图工程的金标准小区域**

## **5.1 Pilot 的目的**

J117 = Junction 117。它从完整 FullMine 原始 GeoJSON 中选出一个真实交叉区域，先把 WGS84/UTM/local 坐标、semantic、bitmap、Map API、Scenario、IDM、Controller、KBM、dual-ego/MCTS 全链跑通，再扩展到全矿。其价值是把“地图工程问题”和“全图规模问题”分开，并提供后续 FullMine 代码改动的回归锚点。

## **5.2 Pilot 路线与 MCTS 证据**

| **路线** | **源 lane**            | **FullMine semantic token**                 |
|----------|------------------------|---------------------------------------------|
| A        | 6670 -\> 6674 -\> 5690 | path-000426 -\> path-000430 -\> path-000330 |
| B        | 5691 -\> 6546 -\> 6523 | path-000331 -\> path-000403 -\> path-000387 |

固定冲突点 local XY 约 (2878.0888, 2799.6561)。Phase 4C 单车全路线完成 423 steps / 42.3s；Phase 5 dual-ego 中 No-MCTS aligned baseline 几乎同时过冲突点并发生真实重叠，而 Pure MCTS seed0 将 crossing gap 拉开到约 1.561s，1ms swept min clearance 约 0.594m；5 seeds benchmark 5/5 PASS、swept 5/5 PASS。J117 随后冻结，不应在 FullMine 地图收尾阶段重复调 MCTS。

# **6. FullMine V1：从原始 8 类 GeoJSON 到可运行全矿结构基线**

## **6.1 原始数据与坐标链**

原始 source package 包含 road、road_boundary、junction、lane、rgn_boundary、loading、unloading、auxiliary 八类 GeoJSON；所有源 GeoJSON 声明 EPSG:4326。项目坐标链固定为 WGS84 -\> UTM Zone 46N (EPSG:32646) -\> MineSim local，E0=409200.0、N0=4916800.0。

| **源图层**            | **Feature 数** | **作用**                                   |
|-----------------------|----------------|--------------------------------------------|
| road.geojson          | 94             | road polygon                               |
| road_boundary.geojson | 100            | road 两侧边界                              |
| junction.geojson      | 35             | intersection region                        |
| lane.geojson          | 553            | reference path / topology / lane Z         |
| rgn_boundary.geojson  | 84             | junction/load/unload/aux boundary          |
| rng_load.geojson      | 36             | loading region                             |
| rgn_unload.geojson    | 7              | unloading region                           |
| rgn_auxiliary.geojson | 6              | auxiliary region                           |
| 1.png                 | 1              | 1799x1050 普通截图，仅视觉参考，无地理参考 |

全量 source preflight 处理过约 1.118M coordinate points。V1 的意义不是“源数据利用率最高”，而是先建立可靠、保守、可回归的软件基线。

## **6.2 V1 structural 输出与系统性 correctness 修复**

| **对象**       | **V1 典型数量** |
|----------------|-----------------|
| node           | 400,744         |
| polygon        | 177             |
| road           | 93              |
| intersection   | 35              |
| loading_area   | 36              |
| unloading_area | 7               |
| auxiliary_area | 6               |
| reference_path | 540             |
| dubins_pose    | 565             |
| borderline     | 388             |

V1/Phase6E 修掉的最关键不是单个几何点，而是三类系统性 correctness bug：

> **•** Endpoint consistency：126 个 path endpoint errors。根因是多个 lane 共享 source topology node，但 endpoint XY 不是 bit-identical。解决：每个 topo node deterministic canonical XY，只 snap path 首尾，0.25m 安全阈值；最终 134 个 endpoint snap（start76/end58），max≈0.143907m，path_endpoint_errors=0。
>
> **•** Source coverage missing 49：validator 没有把 load/unload/auxiliary 映射到 semantic layer。解决：road-\>road、junction-\>intersection、load-\>loading_area、unload-\>unloading_area、auxiliary-\>auxiliary_area。
>
> **•** Boundary parent 错挂 8 个 component：旧 boundary_parent 只按 object ID 跨 category 搜，ID 在不同类别会重复。解决：严格 rgn_type+rgn_objectid，invalid/missing 不跨类别猜测。

最终 structural validators：path_endpoint_errors=\[\]、source_coverage_missing=\[\]、dangling_references=\[\]、bidirectional_failures=\[\]、wrong_source_boundary_parent_count=0。

## **6.3 V1 DEV_ONLY mask 与为什么不冒充 production**

仓库和 Git history 未发现从原始 GIS 生成 Dapai/Jiangtong production mask 的 authoring pipeline；原项目提供的是 finished PNG。结合成品 polygon-mask 审计，whole-polygon 填白不可信。因此 V1 采用透明但保守的 lane-centered corridor + parent clipping 规则，并明确 \`DEV_ONLY_NOT_PRODUCTION_VALIDATED\`。这一步的价值是可解释、可回归，而不是“还原官方 mask”。

Full-Mine 大图第一次 planner.initialize 极慢的根因也在 V1 暴露：get_polygon_token_using_node() 对约 400k node 重复线性扫描。利用已有 token2ind 改成 O(1) 后，J117/FullMine 回归通过，commit 32fb429；随后从临时 J117 alias 独立为 geojson_full_mine_dev，commit d81c571、tag fullmine-dev-runtime-pass-20260811。

# **7. FullMine Vector V2 Semantic：从保守 V1 到“最大化源数据利用率”**

## **7.1 V1 为什么只有 93 roads / 540 paths**

V1 遵循“不能猜”的保守策略：road332 自交、6 个 source road polygon 缺失、road484 polygon/boundary/lane 版本不一致等异常被排除，所以 V1 是软件基线，不是数据利用率上限。8 月 12 日对 source 内部冗余（road boundary、lane、已有正常 road）做交叉验证后，证据足以把这些异常从“排除”升级为“有 provenance 的 effective repair”。

## **7.2 六个 missing roads、road332、road484 的 8 条 repair records**

| **Road**                | **Effective 策略**                         | **证据逻辑**                                                                                                                                   |
|-------------------------|--------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------|
| 339/340/353/356/357/360 | derive_missing_road_from_boundary          | road polygon 缺失，但两条 road_boundary + 对应 lane；在正常 roads 上验证 boundary closure 规则后恢复                                           |
| 332                     | repair_source_road_make_valid_keep_largest | source 自相交为极小 sliver；make_valid 后保留主 polygon，lane5050 在主道路内                                                                   |
| 484                     | replace_source_road_geometry_from_boundary | source polygon 与 lane/boundary 偏差 11-22m，证据支持 source version stale；effective 使用 boundary-derived polygon，原 source 保留 provenance |

关键工程原则是 source/effective 分离：source roads 仍然是 94，不把派生的 6 个 road 冒充源数据；所有 8 条 repair 独立记录 provenance。

## **7.3 V2 最终 semantic 数量与 V1 增量回归**

| **层**         | **Vector V2**                    |
|----------------|----------------------------------|
| polygon        | 184                              |
| road           | 100 effective（source 仍 94）    |
| intersection   | 35                               |
| loading_area   | 36                               |
| unloading_area | 7                                |
| auxiliary_area | 6                                |
| reference_path | 553                              |
| dubins_pose    | 565                              |
| borderline     | 402                              |
| waypoints      | 314,692；保存 raw lane elevation |

V1 reference_path=540，V2=553；shared=540，added=13，removed=0。新增 lane IDs：5050、5163、5164、5165、5166、5171、5172、5175、5178、5179、5180、5181、5186。V1 已验证路径 internal XY/yaw 不漂移，属于严格增量完善。

## **7.4 Topology 与 elevation 的“能用/不能瞎修”边界**

> **•** 同 topo ID 的 endpoint 存在厘米级甚至约0.2m XY 偏差，因此 canonical snapping 必要；但不同 topo ID 可有完全相同 XY，约45对集中在 auxiliary gear transition。禁止按距离 merge 不同 topo ID。
>
> **•** gear=-1 共50条：auxiliary 48、loading 1、unloading 1；road/junction 0。业务运营方向未权威验证，保持 stored topology orientation。
>
> **•** 553 lanes / 314,692 points 全有 Z，range≈1009.048236–1321.0。全量“XY≈0但Z显著跳变”的严重异常主要来自 boundary，lane 质量明显更高。
>
> **•** lane6713 有唯一 hard internal +0.519112m seam：保留 raw Z + QA，不凭空平滑。
>
> **•** V2 waypoint\[3\] 使用 raw lane elevation；slope 仍为 0.0，因为官方 smoothing/slope authoring rule 未完整复现；source_z_datum_verified 仍为 false。

# **8. Vector V2 Bitmap 与 Targeted 场景：从“地图能加载”到“真实矿卡 footprint 能跑”**

## **8.1 15 条重点 lane 与 frozen/additive 策略**

重点集合 = 13 条 V2 新恢复 lanes + road484 两条 lanes 6942/6989。15/15 centerline waypoint 在 frozen V2 bitmap 上 coverage=1.0；进一步用标准 XG90G 9x4m、rear-axle reference 的实际车辆 footprint 审计。绝大多数 endpoint failure 只是车头/车尾跨相邻 region 的 overhang；采用 0.5m endpoint guard 后只剩 lane5186 真正 deep-interior gap，最终以 parent-safe swept patch 加 5 pixels。

| **类别**         | **Lane IDs**                                                                 |
|------------------|------------------------------------------------------------------------------|
| V2 recovered 13  | 5050, 5163, 5164, 5165, 5166, 5171, 5172, 5175, 5178, 5179, 5180, 5181, 5186 |
| road484 targeted | 6942, 6989                                                                   |

## **8.2 为什么没有直接用“from-source full rebuild”替换 frozen mask**

可复现 V2 bitmap builder 能从 source 重新生成 100 effective roads/553 lanes，且 road484 active；但 full rebuild candidate 与历史 frozen V2 比较出现 added=1779、removed=2772，差异 100% 集中于 8 个 repaired roads 的 raster edge discretization。虽然 full rebuild 对 V1 是 monotonic，但直接替换已通过 runtime 的 frozen baseline 会引入无必要的回归面。最终策略：frozen V2 + 经真值验证的 additive patch；可复现 builder 保留作为来源解释工具，而不强行替换运行基线。

## **8.3 大 PNG 与局部审计策略**

FullMine bitmap 约 46322x42411 @10px/m，约 1.964B pixels。Pillow 默认会触发 DecompressionBomb；反复整图解码也浪费内存。因此建立 tiled TIFF 审计缓存（512x512 blocks，约1.844GiB）并优先用 rasterio window 做局部 footprint truth。大 raster pipeline 也避免直接依赖 PNG window writer，优先 tiled GeoTIFF -\> CreateCopy PNG。

## **8.4 BFS target_depth=5：为什么 15 lanes 被拆成 7 个场景**

最初希望用 5 个长场景覆盖 15 lanes，但 A/B 约 13 path 的长 route 在 planner.initialize 报 “refline_smooth data is missing or incomplete”。真正根因不是 semantic 缺路，而是 GlobalRoutePathPlanner 的 BFS hard-code target_depth=5：start depth=0，最多找到 6 token。工程上没有为了地图测试去改全局 route planner，而是在 benchmark/scenario 设计侧把长链拆成 depth-safe 6-token 场景。

| **Scenario**        | **Expected Route lanes**                | **Targets**    | **Length** | **max_t** |
|---------------------|-----------------------------------------|----------------|------------|-----------|
| A1_RECOVERED_EAST_1 | 5182-\>5164-\>5185-\>5181-\>5168-\>5166 | 5164,5181,5166 | ~203.226m  | 90s       |
| A2_RECOVERED_EAST_2 | 5170-\>5172-\>5174-\>5186-\>5177-\>5179 | 5172,5186,5179 | ~402.066m  | 140s      |
| B1_RECOVERED_WEST_1 | 5121-\>5178-\>5176-\>5175-\>5173-\>5171 | 5178,5175,5171 | ~395.826m  | 130s      |
| B2_RECOVERED_WEST_2 | 5169-\>5165-\>5167-\>5180-\>5184-\>5163 | 5165,5180,5163 | ~226.200m  | 90s       |
| C_ROAD332           | 5043-\>5050-\>5051                      | 5050           | ~55.843m   | 60s       |
| D_ROAD484_FORWARD_A | 6952-\>6942-\>6943                      | 6942           | ~54.104m   | 60s       |
| E_ROAD484_FORWARD_B | 6988-\>6989-\>6990                      | 6989           | ~37.340m   | 60s       |

# **9. C/D/E Runtime 与 CollisionLookup：如何区分“地图缺口”和“验证器 bug”**

## **9.1 初始症状**

C/D/E targeted closed-loop 已经真实执行 planner.compute_trajectory() 与 simulation.propagate()，route exact，车辆也实际向前；但在接近 path interface 时被道路边界检查判定为 collision。继续盲目给 mask 加白像素会把验证器自身的错误吞进地图，因此停止扩 mask，转而审计 CollisionLookup 与标准 CarFootprint。

## **9.2 XG90G 几何根因 1：前后悬反置 + 梯形**

标准 rear-axle XG90G footprint 应为后 -2.5m、前 +6.5m、宽 4m。旧 CollisionLookup 却定义 collision_lrear=6.5、collision_lhead=2.5；并且 p1.x 还使用 -collision_lrear/2，导致四点不是矩形而是梯形。旧 lookup 纵向覆盖约 \[-6.5,+2.6\]m，与实际车辆方向完全相反。

修复：XG90G collision_lrear 6.5-\>2.5，collision_lhead 2.5-\>6.5；p1.x 从 -lrear/2 改为 -lrear。几何 regression 得到 p0=(-2.5,-2)、p1=(-2.5,+2)、p2=(+6.5,+2)、p3=(+6.5,-2)，lookup yaw0 范围约 \[-2.4,+6.6\]m。

## **9.3 根因 2：0.2m lookup 栅格的保守侧向假阳性**

前后悬修正后，C/D 仍各有少量 lookup 黑像素，但标准物理 footprint 与这些像素没有正面积重叠；残余侧向超出约 0.079–0.207m，来自 0.2m lookup 离散栅格的保守扩张。最终没有缩车、没有取消 lookup、也没有继续扩地图，而是在 lookup 首先命中 0.1m 黑 pixel 时，使用真实车辆 oriented rectangle 与该 pixel square 做 exact SAT intersection；只有真实相交才 collision。

回归要求同时满足：残余 false positive 被过滤、故意放入真实 physical pixel 仍报告 collision、all-white image 保持 collision-free；并重新跑 polygon rectangle/longitudinal direction regression。最终 CollisionLookup SHA 冻结为 10c1d1339e742ca893fedb4aa51402addfba82e16e08f68339ea35d35ba3043b。

## **9.4 CollisionLookup 修好后，C/D 暴露的才是真地图小缝**

修复验证器后，C/D failure 往后移动并出现真实 standard footprint overlap：动态 corridor truth 表明 C、D 各需 3 pixels = 0.03m²。candidate v2 = candidate v1 + 这 6 pixels；strict streaming 验证 ADDED=6、REMOVED=0、OTHER_CHANGED=0。此时 C=78 steps PASS、D=75 steps PASS，E 先前 55 steps PASS。

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>关键方法论</strong></p>
<p>一个“越界”失败至少有三种可能：地图真的缺口、CollisionLookup 离散/几何错误、planner/controller 轨迹本身不可行。必须先找 root cause，再决定改哪一层。此次项目没有用“把地图涂白”掩盖验证器错误。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# **10. A/B Shadow 与 Planner：A1 endpoint bug、A2 中途停车到最终 steering-rate 解法**

## **10.1 为什么要做 shadow harness**

A/B 在早期 mask 上很快触发 first_bad。如果 formal harness 一碰黑 pixel 就 raise，只能看到第一处 failure，无法知道 controller/vehicle 后续真实会怎样纠正。于是复制 formal harness 生成 shadow 版本：保持 route、planner、controller、dynamics、candidate 完全不变，只把 mask failure 从“raise”改为“记录并继续”；每 0.1s 保存真实 (x,y,yaw,v)，formal harness SHA 保持不变。这样最终 mask patch 可以依据真实闭环轨迹，而不是固定误差外推。

这一步还解决了 B2 的一个重要陷阱：固定保持 failure 时 lateral_offset≈0.242m、yaw_offset≈0.113rad 外推 25m，会产生 227px 假“缺口”，因为真实 controller 后续会纠偏。该结果被明确拒绝，没有写进 v3。

## **10.2 A1：route endpoint 被当作 4.5m 长的虚拟前车**

A1 已访问三个 targets，却在 goal 前约 4.84m 提前停车。IDM free-road virtual lead 使用 \`length_rear = ego_state.car_footprint.length / 2 = 4.5m\`；而 route endpoint 本质是一个零长度停止点。结合 min_gap=1m、rear axle-\>center=2m、goal 设为 path end 前3m，理论提前量 = 4.5+1+2-3 = 4.5m，与实测 4.8369m 高度一致。

最小修复只改语义：virtual route endpoint 的 length_rear=0.0。数学 regression legacy error=4.5m、fixed=0；A1 fixed shadow goal=True。这个修复保留到最终 planner。

## **10.3 A2：先排除 endpoint，再推翻“leading-object”中间假设**

A2 endpoint 修复后仍约 step250 停在 path-000299 中段：route remaining≈274.44m，第三 target path-000301/lane5179 起点还在≈242.61m 前方，所以 route endpoint 被严格排除。当时下一嫌疑是 occupancy/leading-object 误选，这是合理的中间假设；但后续对 planner 行为、轨迹和可执行性继续排查后，最终 blocker 收敛为“旧 9–11m/s 速度在某些高曲率段要求的 steering-rate 超过车辆/控制可实现范围”，而不是 route、mask 或 tracked object 本身。

## **10.4 最终 steering-rate-aware speed profile**

> **•** 从 refline curvature 计算 steering angle：delta = atan(wheel_base \* curvature)。
>
> **•** 按 station 对 delta 求导，得到每米路径需要的 steering change。
>
> **•** 以 steering-rate limit 0.26 rad/s 的 80% 作为利用上限，即 0.208 rad/s，反推出局部速度 cap。
>
> **•** 把 raw curvature/rate cap 与基础 target velocity 取 min。
>
> **•** 使用已有 IDM decel_max 做 backward braking envelope，让车辆在进入急弯前有足够距离减速，而不是到弯中才降速。
>
> **•** 运行时按当前 route station 动态查速度目标/horizon；同时保留 A1 的 \`length_rear=0.0\`。

最终 planner SHA：541ec74985d06322656e66c48abb382030d679171341408575d936e0a069e75e。最终 behavior shadow：A1 308 steps，A2 555，B1 523，B2 330，四个场景均按目标顺序访问并到达 goal。

# **11. V3/V4 Bitmap：用最终真实闭环轨迹做 exact physical patch**

## **11.1 V3 为什么必须基于“最终 planner 的真实 trajectories”**

A1 endpoint 修复、A2 steering-rate speed profile 都会改变车辆在路上的具体姿态。如果仍使用旧 planner 的失败 pose、恒曲率 corridor 或固定 offset 外推，就会把已经不再发生的 footprint 误差写进 mask。因此最终 v3 只读取 final planner 下 A1/A2/B1/B2 的 actual shadow_trajectory，并要求每个 trajectory/result/provenance 与 planner SHA 对上。

## **11.2 V3 builder 的性能/正确性演进**

> **•** 最初逐 pixel Shapely exact intersection 的实现运行超过 8.5 小时，证明正确但生产效率不可接受。
>
> **•** 尝试 NumPy/vectorized SAT：出现 correctness mismatch 或收益不足，拒绝作为 production scanner。
>
> **•** 尝试 rasterize hybrid：可保持 exact boundary truth，但速度仍不理想。
>
> **•** cached/chunked 版本在旧 2GiB cgroup 下出现内存峰值/RC137；这不是算法“随机挂”，而是容器硬限制。
>
> **•** 最终 analytic exact scanner：每个 state 只读 footprint 周围小 raster window；NumPy 做明显 inside/outside broadphase；边界歧义 pixel 才调用 Shapely \`intersection.area \> 1e-12\` exact predicate。
>
> **•** 生产版并行化：多 worker，各自打开 raster；在高资源实例上使用 8 workers。先做 reference-vs-optimized correctness smoke，再做 production scan。

最终 builder 路径：\`/root/autodl-tmp/minesim_p0_preflight/build_v3_from_final_ab_trajectories.py\`。注意：性能优化从未允许改变“正面积物理相交才算 missing”的定义。

## **11.3 V3 final patch 结果**

| **Scenario**  | **final trajectory missing pixels** |
|---------------|-------------------------------------|
| A1            | 83                                  |
| A2            | 176                                 |
| B1            | 348                                 |
| B2            | 117                                 |
| Global unique | 724 pixels = 7.24m²                 |

V3 以 candidate v2 SHA 57514c… 为 source，added=724、removed=0、other=0；四条最终 trajectories 复扫 remaining missing 全部为0。V3 candidate SHA=5a11d523b9931dc99d4267eeb6145ff5674d29ba56fda0749bc06a28aa2c8d7e。随后 A1/A2/B1/B2 formal strict 全部 PASS。

## **11.4 为什么 V3 之后还出现 V4：D step66 是新的真实物理 gap**

为了避免把旧 C/D/E 结果和新 planner 混在一起，C/D/E 重新在 current planner + v3 下运行。C PASS，但 D 在 step66 失败。对 D state 做 exact Shapely positive-area footprint truth：v3/v2 都有 3 个真实 missing pixels，不是 CollisionLookup false positive；nearest route 为 path-000511/lane6943，车辆已经过 target 6942。

因此没有手工只补 step66，而是先跑 D-only current-planner shadow，得到完整 72-state trajectory；整个轨迹只有 step66 一个 mask failure。V4 builder 对全 72 states 扫描，exact missing=3，added=3、removed=0、other=0、remaining=0，candidate SHA=51abcd5a86e5c510204a5dacc873691506d721f98982ab7f98585d4e0f7efdd0。D v4 strict 71 steps PASS。

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>证据锚点（用于接手者复核）</strong></p>
<p>• V4 patch report: /root/autodl-tmp/minesim_p0_preflight/D_v4_current_shadow_patch_report.json</p>
<p>• SOURCE_V3_SHA=5a11d523...；TRAJECTORY_STATES=72；ADDED=3；REMOVED=0；OTHER_CHANGED=0；D_REMAINING_MISSING=0。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## **11.5 从 d2af 到 v4 的 additive 演化**

| **阶段**           | **SHA 前缀** | **含义**                                                      |
|--------------------|--------------|---------------------------------------------------------------|
| d2af baseline      | d2afc84e...  | V2 frozen/additive baseline，已含 lane5186 5px physical patch |
| candidate v1       | 7c586421...  | 相对 d2af +112px / 1.12m²，C/D/E interface truth              |
| candidate v2       | 57514c52...  | v1 +6px；相对 d2af 累计 +118px                                |
| candidate v3       | 5a11d523...  | v2 +724px / 7.24m²，final A/B trajectories                    |
| candidate v4 FINAL | 51abcd5a...  | v3 +3px / 0.03m²，current-planner D full shadow               |

按 verified counts 推导，最终 v4 相对 d2af 基线共增加 845 pixels = 8.45m²；若把 d2af 之前 lane5186 的 5px 也计入，则相对更早 frozen V2 链累计约 850px = 8.50m²。这个面积很小，说明最终验收不是通过大范围“涂白”获得，而是多轮 exact trajectory / physical footprint 的局部补缝。

# **12. Final Targeted Acceptance：7/7 到底意味着什么**

## **12.1 最终 acceptance matrix**

| **Scenario**        | **steps** | **target visits**           | **结果** | **证据层**                          |
|---------------------|-----------|-----------------------------|----------|-------------------------------------|
| A1_RECOVERED_EAST_1 | 308       | 5164@27, 5181@189, 5166@289 | PASS     | strict v3 + additive v4 inheritance |
| A2_RECOVERED_EAST_2 | 555       | 5172@24, 5186@167, 5179@501 | PASS     | strict v3 + additive v4 inheritance |
| B1_RECOVERED_WEST_1 | 523       | 5178@22, 5175@404, 5171@468 | PASS     | strict v3 + additive v4 inheritance |
| B2_RECOVERED_WEST_2 | 330       | 5165@33, 5180@73, 5163@271  | PASS     | strict v3 + additive v4 inheritance |
| C_ROAD332           | 116       | 5050@26                     | PASS     | direct strict v4                    |
| D_ROAD484_FORWARD_A | 71        | 6942@22                     | PASS     | direct strict v4                    |
| E_ROAD484_FORWARD_B | 53        | 6989@23                     | PASS     | direct strict v4                    |

每个 strict PASS 不只是“程序正常退出”：还要求 route_exact_match=True、all_targets_visited=True、target_visit_order_ok=True、goal_reached=True、drivable_all_steps=True、first_non_drivable_step=None、exception=None。最终 acceptance manifest PASS_COUNT=7，SHA=f8d95af3…。

## **12.2 为什么 A/B 可以从 v3 继承到 v4**

A/B 的直接 strict run 在 v3 上；v4 相比 v3 仅把 D current trajectory 中 3 个黑像素改为白，REMOVED=0、OTHER_CHANGED=0。对已经 \`drivable_all_steps=True\` 的 A/B 来说，纯 additive drivable mask 不可能把原来的可行驶状态变成不可行驶，因此 final manifest 显式标记 \`strict_v3_additive_inheritance\`。C/D/E 为 direct v4。

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>证据透明性提示</strong></p>
<p>如果将来论文/审稿要求“7 个场景必须全部直接在完全相同的 bitmap SHA 上重跑”，可从 frozen tag 额外重跑 A/B v4 作为增强证据；当前工程 freeze 的逻辑是严格的 additive monotonic inheritance，并未伪装成 direct v4。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## **12.3 一次重要失败：stale manifest 混用了旧 C/D/E JSON**

曾生成 \`/root/autodl-tmp/minesim_p0_preflight/v3_targeted_7of7_acceptance.json\`（SHA 25f9c00d…），错误复用了旧 combined CDE result：A/B PASS、C/D 旧失败、E PASS，结果只有 5/7。这个 manifest 被立即判定为 INVALID/STALE，绝不能冻结。随后 C/D/E 在 current planner/当前 bitmap 下重新单场景运行，D 才真正暴露 v3 step66 的 3px physical gap，最终促成 v4。

可复用规则：最终验收 manifest 必须绑定 planner SHA、harness SHA、CollisionLookup SHA、bitmap SHA、每个 scenario result SHA；“文件名一样”不等于同一证据世代。

# **13. 旧图回归与 NTE200：为什么最终 freeze 前还要跑 Jiangtong**

## **13.1 NTE200 selector 是历史 bug，不是本轮引入**

当前 \`CollisionLookup.\_\_init\_\_\` 中，\`VehicleType.MineTruck_NTE200\` 分支实际仍实例化 \`MineTruckXG90G()\`；对比 base HEAD 与 current source 证明两者相同，因此这是 pre-existing selector bug。真正的 MineTruckNTE200 class 参数存在：length=13.0、width=6.7、collision_w=5.5、collision_lrear=1.6、collision_lhead=7.2，但 selector 没用它。

本轮没有“顺手修 NTE selector”，因为那会在 7/7 收口时突然扩大 scope；但我们改了 XG90G CollisionLookup 公共几何/精确 filter，而 Jiangtong 旧场景实际 selector 又走 XG90G，所以必须做真实 old-map runtime regression。

## **13.2 Jiangtong IDM 249-step regression**

| **指标**                      | **最终输出**                   |
|-------------------------------|--------------------------------|
| Scenario                      | jiangtong_intersection_9_3_2   |
| Planner                       | IDM                            |
| RC                            | 0                              |
| VEHICLE_COLLISION_COUNT       | 0                              |
| ROAD_BOUNDARY_COLLISION_COUNT | 0                              |
| STRICT_SAFETY_CHECK_PASSED    | True                           |
| STEPS_EXECUTED                | 249                            |
| SIMULATION_RUNNING            | False                          |
| FINAL_X/Y                     | 1328.461787 / 2316.794498      |
| FINAL_SPEED                   | 9.345223 m/s                   |
| 结束标志                      | FULL SCENARIO EXECUTION PASSED |

结论：当前五文件改动没有破坏已存在的 Jiangtong IDM 软件链。这个 regression 不能证明 selector 语义正确，只证明“在历史 selector 行为下，旧图真实 runtime 没有被本轮变化破坏”。NTE selector 仍应作为独立 bug ticket，在新分支中修并补 NTE200 专用 regression。

# **14. 最终静态门禁、源码冻结、Commit 与 Tag**

## **14.1 五个正式源码文件**

| **文件**                           | **SHA256**                                                       | **本轮关键作用**                                         |
|------------------------------------|------------------------------------------------------------------|----------------------------------------------------------|
| vehicle_parameters.py              | e14a32f88bca707de5a6d9661188259be7a9112bbefb1b0d90bd4d22358c4977 | FullMine vehicle/location 注册相关                       |
| collision_lookup.py                | 10c1d1339e742ca893fedb4aa51402addfba82e16e08f68339ea35d35ba3043b | XG90G 几何 + exact pixel SAT filter                      |
| minesim_bitmap_png_loader.py       | 3bad8ebe750c2b56a02ac8ffeef4eaf81424f81a4727aa272b2345919b9bc651 | 新地图 bitmap registry/loader                            |
| minesim_semanticmap_json_loader.py | 41872d1e568cd1a68bc2c2997d7dfc3c7db93d3ef0e1959597d891902049ff34 | 新地图 semantic registry/loader                          |
| abstract_idm_planner.py            | 541ec74985d06322656e66c48abb382030d679171341408575d936e0a069e75e | route-end zero-length lead + steering-rate speed profile |

static gate：上述五文件 \`python -m py_compile\` PASS，\`git diff --check\` PASS；精确 \`git add\` 只 stage 这 5 个文件，staged diff check PASS。precommit patch SHA=f30da9f4…。

## **14.2 最终 Git 锚点**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>正式冻结</strong></p>
<p>Commit: 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e</p>
<p>Message: fullmine: freeze vector v4 runtime fixes</p>
<p>Diff: 5 files changed, 262 insertions(+), 9 deletions(-)</p>
<p>Tag: fullmine-vector-v4-runtime-freeze-20260814</p>
<p>Postcommit record SHA: 5a6287cd6433641cfc33ce725bf0e4f1f8dc1796b91d86dbd5bebf3c39968300</p>
<p>Final known worktree: ?? ^C only</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

\`^C\` 是误粘产生的 untracked 零字节历史垃圾，未进入 commit/tag。本轮没有用 git clean；后续若要删除，也必须先明确 \`ls -l ./^C\`/file 后只删该精确文件。

## **14.3 一个必须提醒下一位 AI 的备份风险**

Git tag 冻结的是源码，不会自动把 \`/root/autodl-tmp\` 下 1.9B-pixel bitmap、manifest、logs、shadow trajectories 一起写入 Git。当前对话已创建 final bitmap、targeted manifest、freeze record，但没有看到“V4 final map archive + Git bundle”的明确最终动作。因此下一位 AI 如果要做灾备，第一步应只读检查是否已有 20260814 final archive/bundle；不存在时再单独创建。不要把 8 月 11 日 V1 bundle 误当 V4 bundle。

# **15. 云端关键资产、路径、SHA 与“哪些不能覆盖”**

| **资产**              | **绝对路径**                                                                                                               | **规则/证据**                                                        |
|-----------------------|----------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------|
| 正式 repo             | /root/MineSim-Dynamic                                                                                                      | Git source；只精确修改/stage                                         |
| 原两张成品地图        | /root/datasets/maps                                                                                                        | Dapai/Jiangtong reference；本轮不修改                                |
| Targeted runtime root | /root/autodl-tmp/fullmine_vector_v2_targeted_runtime                                                                       | semantic + runtime bitmap symlink + harness/results                  |
| V2 semantic           | .../maps/semantic_map/geojson_full_mine_vector_v2_dev_semantic_map.json                                                    | SHA b85a3d8b28f2252ecb5bda179d514573f6333079def838cd048566f556d95cd0 |
| Final V4 bitmap       | /root/autodl-tmp/fullmine_vector_v4_d_current_planner_patch_candidate/bitmap/geojson_full_mine_vector_v2_dev_only_mask.png | SHA 51abcd5a...；IMMUTABLE                                           |
| Formal harness        | /root/autodl-tmp/fullmine_vector_v2_targeted_runtime/targeted_closed_loop_runtime.py                                       | SHA 59a71806...                                                      |
| Shadow harness        | /root/autodl-tmp/fullmine_vector_v2_targeted_runtime/targeted_closed_loop_runtime_shadow.py                                | SHA aa735933...；只用于收集真实后续轨迹                              |
| V3 builder            | /root/autodl-tmp/minesim_p0_preflight/build_v3_from_final_ab_trajectories.py                                               | final A/B exact trajectory patch builder                             |
| V3 report             | /root/autodl-tmp/minesim_p0_preflight/final_ab_v3_missing_pixels.json                                                      | A1/A2/B1/B2 83/176/348/117；union724                                 |
| D V4 builder          | /root/autodl-tmp/minesim_p0_preflight/build_D_v4_from_current_shadow.py                                                    | current planner D 72-state exact patch                               |
| D V4 report           | /root/autodl-tmp/minesim_p0_preflight/D_v4_current_shadow_patch_report.json                                                | +3px / removed0 / other0                                             |
| Final 7/7 manifest    | /root/autodl-tmp/minesim_p0_preflight/v4_targeted_7of7_acceptance_final.json                                               | SHA f8d95af3...                                                      |
| Oldmap regression     | /root/autodl-tmp/minesim_p0_preflight/oldmap_jiangtong_idm_v4                                                              | run.log / run.rc / summary.txt                                       |
| Precommit patch       | /root/autodl-tmp/minesim_p0_preflight/final_precommit_source.patch                                                         | SHA f30da9f4...                                                      |
| Freeze manifest       | /root/autodl-tmp/minesim_p0_preflight/fullmine_v4_final_freeze_manifest.json                                               | SHA 30326ee2...                                                      |
| Postcommit freeze     | /root/autodl-tmp/minesim_p0_preflight/fullmine_v4_postcommit_freeze.json                                                   | record SHA 5a6287cd...                                               |
| STALE manifest        | /root/autodl-tmp/minesim_p0_preflight/v3_targeted_7of7_acceptance.json                                                     | INVALID；SHA25f9...；DO NOT USE                                      |

# **16. 全过程问题库：症状 -\> 根因 -\> 解决 -\> 可复用规则**

| **症状/问题**                           | **根因**                                                  | **解决**                                                         | **可复用规则**                                        |
|-----------------------------------------|-----------------------------------------------------------|------------------------------------------------------------------|-------------------------------------------------------|
| **full build RC137/Killed**             | 实际 cgroup memory.max 只有2GiB，free -h 显示宿主机大内存 | 先读 cgroup；需要时开 80GiB/15vCPU 实例                          | 资源真值看 cgroup，不看 nproc/free                    |
| **nproc=192 误导**                      | 宿主逻辑核可见，不等于 CPU quota                          | cpu.max=1500000/100000 -\> ~15 vCPU                              | 任何大任务前先算 quota                                |
| **/usr/bin/time 不存在**                | 镜像缺工具                                                | shell/Python 计时                                                | 命令不存在不等于 build fail                           |
| **endpoint errors 126**                 | same topo node 的 lane endpoint XY 不 bit-identical       | deterministic canonical XY + endpoint-only snap                  | 只在同 topo ID 内 snap                                |
| **不同 topo ID 同 XY**                  | auxiliary gear transition 有真实语义                      | 禁止 XY merge                                                    | topo ID 优先于距离                                    |
| **source coverage missing 49**          | validator layer mapping 漏 load/unload/aux                | 显式 source-\>semantic mapping                                   | validator 也必须随 schema 扩展                        |
| **8 boundary parent 错挂**              | 仅按 object ID 跨 category 搜                             | rgn_type+rgn_objectid                                            | 类别语义不能靠“同 ID”猜                               |
| **road332 self-intersection**           | 极小 sliver                                               | make_valid + keep largest + provenance                           | 几何修复要量化 sliver，而非 buffer(0) 盲修            |
| **6 missing road polygons**             | road.geojson 缺失，但 boundary/lane 完整                  | 在正常 road 上 cross-validate 后 boundary-derived reconstruction | 利用源内部冗余，不做 nearest road 猜测                |
| **road326 candidate initially invalid** | boundary closure 微自交                                   | make_valid 后主 polygon IoU/Hausdorff 回归                       | 一次 validity FAIL 先诊断，不否定方法                 |
| **road484 lane 超出 source polygon**    | source version 与 boundary/lane 不一致                    | boundary-derived effective geometry + source provenance          | 版本一致性强证据，但不等于 production authority       |
| **polygon/boundary Z 跳变**             | geometry layer Z 质量差                                   | elevation 只取 lane Z                                            | 不同 layer 的 Z 可信度分开                            |
| **lane6713 +0.519m seam**               | 唯一 hard lane internal jump                              | raw Z + QA，不平滑                                               | 未知项优先保留，不伪造                                |
| **大 PNG DecompressionBomb**            | 约1.964B pixels 超 Pillow 默认                            | 可信资产禁上限/优先 tiled rasterio                               | 超大图不要反复 PIL 全量解码                           |
| **PNG window writer 风险**              | BufferedDatasetWriter 不证明 bounded-memory               | temporary tiled GeoTIFF -\> CreateCopy PNG                       | 大 raster 先 tiled                                    |
| **rasterize(\[\]) ValueError**          | 空 tile 无 shapes                                         | 空 tile 直接 zeros                                               | tile pipeline 必须处理空块                            |
| **planner.initialize 卡住**             | 400k node nested linear scan                              | token2ind O(1)，commit32fb429                                    | 大图会放大算法复杂度                                  |
| **J117 alias 混淆 FullMine**            | 早期复用 pilot identity                                   | 建立独立 geojson_full_mine_dev                                   | 每张地图独立 location/version/basename                |
| **V2 full rebuild 与 frozen 有差异**    | 8 repaired roads 边缘 raster discretization               | 保留 builder，但 runtime 用 frozen+verified additive             | 可复现不等于必须替换已验证 baseline                   |
| **lane5186 deep interior gap**          | 急弯车辆角点超出简单 corridor                             | parent-safe 5px swept patch                                      | centerline coverage 不等于 vehicle footprint coverage |
| **A/B refline_smooth missing**          | BFS target_depth=5 导致长 route 根本没找到                | 拆成 6-token depth-safe scenarios                                | 错误消息可能是上游失败的二次症状                      |
| **C/D/E 初始边界碰撞**                  | CollisionLookup rear/head 反置 + p1/2 梯形                | 修 XG90G geometry                                                | 验证器本身也必须审计                                  |
| **修几何后仍有 C/D false positive**     | 0.2m lookup 保守栅格超出物理车身                          | lookup black hit 后 exact SAT pixel-vs-rectangle                 | 不取消粗 lookup；只精确复核候选                       |
| **修 lookup 后 C/D 新 failure**         | 真实 footprint 正面积 overlap                             | 各 +3px candidate v2                                             | 先真值分类，再 patch map                              |
| **B2 fixed-offset 扫出 227px**          | 把瞬时 lateral/yaw error 固定外推25m                      | 拒绝 patch；改用 shadow actual trajectory                        | 扫描边界未闭合时不得造 patch                          |
| **A1 goal 前 4.84m 停车**               | virtual route endpoint 被当作 4.5m half-length lead       | length_rear=0.0                                                  | 语义对象不要复用物理前车长度                          |
| **A2 step250 中途停车**                 | 最终 root cause 是 steering-rate infeasible at old speed  | rate-aware speed profile + backward braking                      | 中间 hypothesis（leading object）可被后续证据推翻     |
| **V3 pixel-by-pixel \>8.5h**            | 每 state/pixel Shapely 太重                               | window + NumPy broadphase + exact ambiguous edge                 | 优化必须保留 exact predicate                          |
| **vectorized SAT mismatch/收益差**      | 近边界数值/实现正确性风险                                 | 拒绝 production 使用                                             | 速度不能换掉 truth definition                         |
| **cached/chunked RC137**                | 2GiB cgroup 内存峰值                                      | 换高 RAM + streaming/worker-own-raster                           | OOM 首先看资源，不盲改算法语义                        |
| **A/B 四场景同进程硬终止**              | 生命周期/内存累积，trap 未执行风险                        | one heavy scenario per Python process                            | 长场景隔离进程；rc/log独立                            |
| **runtime symlink 可能残留**            | hard kill 时 trap 不执行                                  | 每次前后 SHA/readlink 强校验；原子 symlink switch                | 不要假设 restore 已发生                               |
| **D v3 current planner step66**         | 3px exact positive-area physical gap                      | D full72-state shadow -\> v4 +3px                                | 不要只补第一失败 pixel；补完整真实 trajectory         |
| **stale 7/7 manifest 只有5/7**          | 复用了旧 combined CDE JSON                                | 判 INVALID；当前 SHA 下重跑 C/D/E                                | final manifest 必须绑定每个结果世代/SHA               |
| **NTE200 selector 选到 XG90G**          | 历史代码分支错误                                          | 本轮不扩大 scope；旧 Jiangtong runtime regression                | pre-existing bug 与本轮 regression 要区分             |
| **长 heredoc/代码块乱码**               | 聊天 UI 把长代码/输出拼进 Bash                            | 短 ASCII block；一步一块                                         | 只复制代码，不复制 prompt/output                      |
| **交互终端被 exit**                     | 脚本末尾/误操作关闭 shell                                 | 默认不在交互末尾裸 exit                                          | 脚本 return code 与 shell 存活分开                    |
| **No screen session found**             | 启动前清理旧 session 时正常提示                           | 看新 session/rc/log                                              | 不要把清理提示当启动失败                              |
| **sha256sum -L 假设错误**               | 工具选项不存在/行为理解错                                 | 普通 sha256sum 默认跟随 symlink                                  | 先验证工具真实行为                                    |
| **untracked ^C**                        | 终端误粘残留                                              | 未 stage/commit；精确核验后再决定是否删                          | 绝不因 untracked 就 git clean                         |

# **17. 用户实际工作流：AI / Codex / AutoDL 如何协作才最省钱、最安全**

## **17.1 标准循环：观察 -\> 计划 -\> 执行 -\> 验收 -\> 冻结**

| **步骤** | **实际规则**                                                             |
|----------|--------------------------------------------------------------------------|
| **观察** | 只读核验环境、Git、SHA、目标文件/log；不先改。                           |
| **计划** | AI 只给当前一个最小目标、为什么做、PASS/FAIL 条件；不重述全项目。        |
| **执行** | 用户 AutoDL terminal 跑机械命令；AI/Codex 只写关键代码/诊断。            |
| **验收** | 只看当前 gate；失败先找第一根因，不回到全仓重审。                        |
| **冻结** | PASS 后写 manifest/hash；需要时 exact stage/commit/tag；下一阶段不重跑。 |

## **17.2 每段 terminal 命令的统一前缀**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>cd /root/MineSim-Dynamic<br />
source /root/miniconda3/etc/profile.d/conda.sh 2&gt;/dev/null || true<br />
conda activate minesim</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

静态/CPU 诊断追加 \`export CUDA_VISIBLE_DEVICES=""\`；真正 runtime/GPU 需要时才 \`unset CUDA_VISIBLE_DEVICES\`。但要注意：AutoDL “GPU 实例”还同时决定 CPU/RAM cgroup，V3 builder 即使隐藏 CUDA，也受益于 15vCPU/80GiB。

## **17.3 Codex 成本策略（当前可用，但必须边界清晰）**

| **任务**                                       | **推荐方式**                                                   |
|------------------------------------------------|----------------------------------------------------------------|
| git/status/hash/file existence/grep/py_compile | 直接 shell/Python，不花模型额度                                |
| 小范围代码审计/最小 patch                      | Codex gpt-5.6-luna medium                                      |
| 中等复杂多模块 bug                             | 必要时 Terra medium/high                                       |
| 核心算法/顽固 closed-loop/关键终审             | 仅必要时 Sol high；完成立即回 Luna                             |
| 长 build / runtime / screen 等待               | terminal 执行；Codex 不负责长期挂着等                          |
| Codex 输出                                     | 只要 PASS/FAIL + modified/evidence；不写长报告，不重复已知事实 |

重要：用户当前不是“永远禁止 Codex”，而是“省钱优先、只有边界明确且确实有价值时用”。8 月 12 日曾临时要求停止 Codex；随后又明确允许困难工作在省钱前提下交给 Codex。最新工作流应以后一条为准。

## **17.4 长任务 / screen / SSH**

> **•** 长任务统一写独立 log + rc 文件；screen 只是进程托管，不是证据源。
>
> **•** 启动前 \`screen -S name -X quit\` 返回 No screen session found 很常见，通常只说明“旧 session 不存在”。
>
> **•** 状态查询优先 \`cat run.rc \|\| echo RUNNING\` + \`tail/grep log\`；不要因为看不到即时输出而重复启动。
>
> **•** \`screen=Dead\` + 无 Python + rc 缺失才是可疑硬终止；此时先审 runtime symlink/trap 是否恢复。
>
> **•** Heavy scenario 一次一个 Python process；A/B 早期同进程硬终止已经证明隔离更稳。

## **17.5 Git 与资产纪律**

> **•** 任何 commit 前：git diff --check；git diff --name-only；git diff --cached --name-only。
>
> **•** 只允许 \`git add \<exact files\>\`；禁止 add .。
>
> **•** 大地图/结果/log/中间 builder 全部放 /root/autodl-tmp；repo 只放必要 production source。
>
> **•** bitmap patch 目录不可原地覆盖：baseline/v1/v2/v3/v4 都 immutable。
>
> **•** 每个 map candidate 都绑定 SHA；临时 runtime 切图用 symlink + strong SHA gate。
>
> **•** 最终 tag 冻结后，任何后续修改先创建新 branch；不要在 tag 上继续工作。

## **17.6 Terminal 乱码后的新规则**

真实对话中长 heredoc/长 Python 块多次被前端拼接，甚至出现 \`PY ...\` 与终端输出混到命令里的乱码。因此以后 shell 指令以短 ASCII block 为默认；长脚本先生成文件并 \`bash -n\` / \`py_compile\`，再运行；文档/中文解释与 terminal code 分开。

# **18. AutoDL 资源模型：为什么“开 GPU 卡”其实常常是为了 CPU/RAM**

## **18.1 已实测的两种 cgroup**

| **实例状态**      | **cgroup CPU**           | **memory.max** | **GPU**             | **实际影响**                                        |
|-------------------|--------------------------|----------------|---------------------|-----------------------------------------------------|
| 低资源/卡未完全开 | 50000/100000 ~= 0.5 CPU  | 2GiB           | 无/不可用           | Full bitmap/scan 极慢；cached builder RC137         |
| 固定 4090D 实例   | 1500000/100000 = 15 vCPU | 80GiB          | RTX 4090 D 24564MiB | V3/V4 builder/runtime 稳定；CPU scanner 可隐藏 CUDA |

\`nproc=192\`、\`free -h\` 接近宿主机值曾严重误导资源判断。后续任何大任务都先读 \`/sys/fs/cgroup/cpu.max\` 与 \`memory.max\`。地图 conversion/footprint scanner 主要是 CPU/RAM 工作，GPU 本身价值不大；但 AutoDL 的 GPU 套餐会连带提供更高 CPU/RAM quota。

# **19. 新 AI/工程人员云端接手 SOP：10 分钟内定位正确阶段**

## **19.1 Step 1：环境 / Git / 资源**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>cd /root/MineSim-Dynamic<br />
source /root/miniconda3/etc/profile.d/conda.sh 2&gt;/dev/null || true<br />
conda activate minesim<br />
export CUDA_VISIBLE_DEVICES=""<br />
<br />
pwd<br />
python --version<br />
git branch --show-current<br />
git rev-parse HEAD<br />
git status --short<br />
git show --no-patch --decorate fullmine-vector-v4-runtime-freeze-20260814<br />
cat /sys/fs/cgroup/cpu.max<br />
cat /sys/fs/cgroup/memory.max</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

若 HEAD/tag 不符，先解释“为什么变了”。不要 reset 回 112d2bd；新工作可能已经在后续分支。只有当用户明确要回到 freeze baseline 时，才从 tag 新建 branch。

## **19.2 Step 2：关键 SHA 只读复核**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>P0=/root/autodl-tmp/minesim_p0_preflight<br />
R=/root/autodl-tmp/fullmine_vector_v2_targeted_runtime<br />
<br />
sha256sum /root/autodl-tmp/fullmine_vector_v4_d_current_planner_patch_candidate/bitmap/geojson_full_mine_vector_v2_dev_only_mask.png "$P0/v4_targeted_7of7_acceptance_final.json" devkit/sim_engine/environment_manager/collision_lookup.py devkit/sim_engine/planning/planner/abstract_idm_planner.py</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

期望分别为 51abcd5a…、f8d95af3…、10c1d133…、541ec749…。若不一致，先查文件是否被后续分支修改，禁止直接覆盖。

## **19.3 Step 3：理解“当前完成”和“下一步”**

| **如果目标是…**           | **不要重做…**               | **正确起点**                                                                        |
|---------------------------|-----------------------------|-------------------------------------------------------------------------------------|
| 继续地图覆盖              | 不要重跑 A-E / 不重建 V1/V2 | 从 final tag 开新分支，选 road/junction/loading/unloading/aux representative routes |
| 跑 FullMine MCTS          | 不要再调 J117               | 从 final tag 构建 FullMine scenario/benchmark，先 smoke 再 full                     |
| 修 NTE200 selector        | 不要混入 V4 map commit      | 单独 bug branch；selector fix + NTE geometry + Jiangtong regression                 |
| 拿到 production mask/规则 | 不要覆盖 V4                 | 建立 V5/production-candidate 新版本，与 V4 做差分/回归                              |
| 做 Neural-MCTS            | 不要声称已有网络            | 先扩大场景/数据，按 scenario/time split；再 Value/Policy/PUCT                       |

## **19.4 接手者需要知道的当前“不要重跑”清单**

> **•** J117 Phase3/4/5、5-seed Pure MCTS robustness（除非 production source 变动会影响其链路）。
>
> **•** FullMine V1 structural build 与 endpoint/coverage/boundary-parent validators。
>
> **•** Vector V2 540-\>553 path 增量验证、8 repair provenance、7 depth-safe route preflight。
>
> **•** CollisionLookup XG90G geometry/SAT regression，除非 collision_lookup.py 发生新 diff。
>
> **•** A1/A2/B1/B2 final planner blocker 诊断；当前 planner SHA 541ec 已通过。
>
> **•** V3/v4 已 frozen 的 bitmap 构建；除非要重现证据或新 planner/vehicle 改变轨迹。

# **20. 地图完成度的最终定义、当前结论与后续优先级**

## **20.1 如果目标是“科研/论文/算法 benchmark 新地图”**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>结论：已完成并冻结</strong></p>
<p>Semantic/topology：完成</p>
<p>Map API / loader：完成</p>
<p>15重点lane static + route：完成</p>
<p>7 targeted closed-loop：完成（含明确 v3-&gt;v4 inheritance）</p>
<p>旧 Jiangtong runtime regression：完成</p>
<p>最终 SHA/manifest/commit/tag：完成</p>
<p>=&gt; FullMine Vector V4 可作为正式 Research Baseline。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## **20.2 如果目标是“production-authoritative 全矿地图”**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>结论：尚未具备声明条件</strong></p>
<p>缺少至少一种权威输入：production mask、drivable surface、internal obstacle/restricted polygon、authoring rule。</p>
<p>此外仍有 gear=-1 运营语义、真实车型、NTE selector、slope/datum、auxiliary API 与全矿 representative coverage 等问题。</p>
<p>这些已不是“把几行代码修好”就能消除的未知。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## **20.3 推荐后续路线（按价值/风险排序）**

| **优先级** | **任务**                                             | **目的**                                                                                    |
|------------|------------------------------------------------------|---------------------------------------------------------------------------------------------|
| **P0**     | 做 final disaster-recovery archive / Git bundle 检查 | 确保 v4 bitmap + manifests + source tag 能脱离当前实例恢复；先检查是否已存在，勿重复/覆盖。 |
| **P0**     | 全矿 representative coverage                         | road/junction/loading/unloading/auxiliary 各选代表路线；不只围绕 repair/J117。              |
| **P0**     | 获取 authoritative drivability                       | 向数据方索取 production mask/drivable surface/internal exclusions/authoring rule。          |
| **P1**     | NTE200 selector 独立 bug ticket                      | 修 selector 后做 NTE geometry + Jiangtong 旧图 regression；不要混入 frozen V4。             |
| **P1**     | 真实车型确认                                         | 如果 FullMine 现场不是 XG90G，建立独立 vehicle config 并重新评估 footprint/mask。           |
| **P1**     | auxiliary semantic API                               | 若后续 benchmark 需要辅助区/加油区语义查询，再扩 MineSimMapLayer。                          |
| **P2**     | FullMine 多场景 Pure/Fleet MCTS                      | 在地图 coverage 稳定后，从 frozen tag 建新的算法实验分支。                                  |
| **P2**     | Neural-MCTS / adaptive budget                        | 利用更多场景与严格 split，优先解决“何时需要高预算/如何复用树”而非直接堆固定 300。           |

# **21. 关键 Commit/Tag 速查与版本语义**

| **Commit/Tag**                                            | **阶段**                        | **意义**                               |
|-----------------------------------------------------------|---------------------------------|----------------------------------------|
| 2521aa4…                                                  | idm-replay-autodl-baseline      | IDM baseline 锚点                      |
| 94693dc…                                                  | MCTS/expert baseline            | Pure MCTS、两场景正式结果、448专家样本 |
| f8ff186…                                                  | Fleet internal clearance reward | 多车内部净距 reward                    |
| 94794c… / tag jiangtong-v22-benchmark-screening-20260809  | Jiangtong V22                   | 第二 benchmark 负筛选                  |
| 4bd2bff… / tag j117-phase3-production-map-load-20260809   | J117 Phase3                     | Map API loader milestone               |
| ec1c958…                                                  | J117 minimal scenario           | Phase4B minimal Scenario               |
| da4105b… / tag j117-phase5-dual-ego-pure-mcts-20260810    | J117 Phase5                     | dual-ego + Pure MCTS 5 seed            |
| 32fb429…                                                  | FullMine semantic lookup        | token2ind O(1) 大图性能修复            |
| d81c571… / tag fullmine-dev-runtime-pass-20260811         | FullMine V1                     | 独立 map identity + basic runtime      |
| 112d2bd… / tag fullmine-vector-v4-runtime-freeze-20260814 | FINAL CURRENT                   | Vector V4 runtime fixes + final freeze |

# **22. 可直接复制给下一位 AI 的最终接管 Prompt**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>You are taking over the MineSim-Dynamic project on AutoDL.<br />
<br />
Read the 2026-08-14 FullMine Vector V4 handoff document first.<br />
<br />
Repository: /root/MineSim-Dynamic<br />
Conda env: minesim<br />
Python: 3.9.25<br />
Expected frozen commit: 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e<br />
Frozen tag: fullmine-vector-v4-runtime-freeze-20260814<br />
<br />
Current final map:<br />
- semantic identity: geojson_full_mine_vector_v2_dev<br />
- semantic: 100 effective roads / 553 reference paths / 565 dubins poses<br />
- final V4 bitmap SHA256: 51abcd5a86e5c510204a5dacc873691506d721f98982ab7f98585d4e0f7efdd0<br />
- final targeted manifest SHA256: f8d95af33ebc71b88ace93c3e538bec3761e80d7a9b610a2bed7408fada4ea2b<br />
- final targeted acceptance: 7/7 PASS<br />
- legacy Jiangtong IDM regression: 249 steps, 0 vehicle collision, 0 road-boundary collision, strict safety PASS<br />
<br />
Critical source SHAs:<br />
- collision_lookup.py = 10c1d1339e742ca893fedb4aa51402addfba82e16e08f68339ea35d35ba3043b<br />
- abstract_idm_planner.py = 541ec74985d06322656e66c48abb382030d679171341408575d936e0a069e75e<br />
<br />
Rules:<br />
1. First do read-only git/status/SHA/cgroup checks. Never reset to make the state look right.<br />
2. Never use git clean -fd, git reset --hard, or git add .<br />
3. Never overwrite d2af/candidate-v1/v2/v3/v4 bitmaps. New work gets a new directory and SHA.<br />
4. Static/CPU work: export CUDA_VISIBLE_DEVICES="". Runtime only: unset CUDA_VISIBLE_DEVICES when needed.<br />
5. For long tasks, use one heavy scenario per Python process and write .log + .rc. Use screen if SSH risk is real.<br />
6. Diagnose the first/root error before changing code or mask.<br />
7. The NTE200 CollisionLookup selector currently instantiates XG90G. This is a PRE-EXISTING known issue and was not fixed in the V4 freeze.<br />
8. V4 is a research/benchmark map, not production-authoritative drivability.<br />
9. Do not reuse the stale v3_targeted_7of7_acceptance.json. Use v4_targeted_7of7_acceptance_final.json.<br />
10. Keep terminal commands short and ASCII-only when possible; the chat UI has mangled long heredocs before.<br />
<br />
If continuing map work, branch from the frozen tag and add representative whole-mine coverage.<br />
If continuing algorithm work, branch from the frozen tag and build FullMine scenarios/MCTS without modifying the frozen map.<br />
<br />
Return only:<br />
CURRENT_STATE<br />
NEXT_ONE_STEP<br />
RISKS<br />
Do not re-audit completed phases unless new strict evidence requires it.</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# **23. 接手者自检：读完后必须能回答的问题**

> **1.** 为什么 FullMine “Vector V4” 的 semantic 仍叫 Vector V2？
>
> **2.** 为什么 Dapai/Jiangtong 的成品 polygon 不能推导出“whole polygon=drivable”？
>
> **3.** V1 的 93 roads/540 paths 与 V2 的 100/553 差在哪？6 missing roads、road332、road484 分别如何处理？
>
> **4.** 为什么不同 topo ID 即使 XY 完全相同也不能 merge？
>
> **5.** 为什么 lane5186 5px 与后续 C/D/E/A/B patches 都要求 physical footprint truth？
>
> **6.** 为什么 A/B 长 route 的 refline_smooth error 真根因是 BFS target_depth=5？
>
> **7.** CollisionLookup 修复前为什么 lookup longitudinal range 方向相反？p1/2 又造成了什么？
>
> **8.** 为什么修完 CollisionLookup 之后 C/D 仍各需要 3 个真实 pixels？
>
> **9.** 为什么 B2 fixed-offset 227px 扫描不能做 v3？
>
> **10.** A1 提前约4.84m停车如何由 virtual lead 4.5m 推导出来？
>
> **11.** A2 为什么最终不是 route endpoint/leading-object，而是 steering-rate infeasibility？
>
> **12.** V3 builder 为什么从 pixel Shapely 演进到 window+NumPy broadphase+exact Shapely boundary？
>
> **13.** 为什么 final 7/7 中 A/B 是 v3 strict inheritance，而 C/D/E 是 direct v4？
>
> **14.** 为什么 stale v3 manifest 必须禁止使用？
>
> **15.** NTE200 selector bug 为什么被记录但没有塞进 final V4 commit？
>
> **16.** 为什么 Git tag 不等于完整地图灾备？
>
> **17.** 下一位 AI 看到 \`?? ^C\` 为什么不能直接 git clean？

# **附录 A. 证据索引：关键结论应该去哪里复核**

| **主题**                                               | **证据源**                                                                           |
|--------------------------------------------------------|--------------------------------------------------------------------------------------|
| FullMine V1 structural/mask/old-map comparison         | MineSim-Dynamic_新地图项目云端交接手册_2026-08-11.docx                               |
| Vector V2 semantic/bitmap/15 target/7 scenarios        | MineSim-Dynamic_项目完整进展与云端AI接管超级手册_2026-08-12.docx                     |
| CollisionLookup/candidate v1-v2/A1 endpoint/A2中途停车 | MineSim项目云端接手与技术总览_2026-08-13(1).docx                                     |
| 长对话/terminal 原始证据                               | 粘贴的文本 (1)(20260813-130803).txt 及 20260813-155108/161756、20260814 多份补充日志 |
| V4 D patch / C/E final / 7/7 manifest                  | 20260814-062315 terminal log + final direct terminal outputs                         |
| Oldmap regression / static/stage/commit/tag            | 2026-08-14 当前对话 direct terminal output；本手册生成时的最新事实源                 |

接手时如旧 Word 与 final commit/tag 冲突，以当前 Git/terminal 为准。文档中的路径可能在后续人为归档后变化，因此“SHA + manifest 内容”比“文件名看起来像 final”更重要。

# **附录 B. 当前状态一句话版**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>最终一句话</strong></p>
<p>FullMine semantic 已从 V1 的保守可运行基线提升到 Vector V2 的 100 effective roads / 553 paths / raw lane Z / 8 repair provenance；bitmap 又通过 CollisionLookup 真值分类、planner 可执行性修复、A/B/D final shadow exact footprint 逐步演进到 V4；当前 targeted 7/7、旧 Jiangtong 回归、static gate、commit/tag 全部通过，足以作为科研/算法 baseline，但 production-authoritative drivability 仍需外部权威数据。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

--- 文档结束 / Evidence cutoff: 2026-08-14 ---
