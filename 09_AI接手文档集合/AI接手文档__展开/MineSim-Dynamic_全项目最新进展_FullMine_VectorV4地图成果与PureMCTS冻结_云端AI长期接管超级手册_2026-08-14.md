**MineSim-Dynamic**

**全项目最新进展、FullMine Vector V4 地图成果、Representative Coverage 与 Pure MCTS 冻结、云端 AI 长期接管超级手册**

从 IDM Baseline / Pure MCTS / 五 Planner / Fleet-MCTS / J117 Pilot / FullMine V1→Vector V2→V3→V4 / Representative Coverage 到 Pure MCTS Representative Transfer Freeze

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>当前最终结论</strong></p>
<p>科研 / 算法 benchmark 新地图：READY + FROZEN</p>
<p>Representative Coverage v1：FROZEN WITH DOCUMENTED LIMITATIONS</p>
<p>Pure MCTS Representative Transfer v1：3/3 PASS + FROZEN</p>
<p>Production-authoritative drivability：NOT PROVEN</p>
<p>Frozen base commit: 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e</p>
<p>V4 bitmap SHA256: 51abcd5a86e5c510204a5dacc873691506d721f98982ab7f98585d4e0f7efdd0</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

文档定位：项目总交接 / 云端恢复 / AI 接手 / 地图制作全流程 / 问题复盘 / 算法基线 / 当前下一步

证据截止：2026-08-14 当前会话最新 AutoDL 终端、Git、SHA、runtime、Coverage/MCTS freeze 输出 + 用户历史交接资料

# 0. 先读这一章：五分钟接管摘要与事实规则

## 0.1 30 秒结论

项目已经从“能不能把新矿区数据转成 MineSim 地图”推进到“FullMine Vector V4 作为科研/算法基线已经完成 targeted runtime 验收并用 Git commit/tag 冻结”的阶段。当前新地图的 semantic 主体仍是 Vector V2：100 个 effective road、553 条 reference_path、565 个 dubins_pose、184 个 polygon，并保存 314,692 个 lane waypoint 的 raw elevation；V3/V4 主要是围绕真实闭环轨迹做 bitmap additive patch 和最终 runtime freeze，不应误解为 semantic 又重做了两版。

最终 targeted acceptance 为 7/7：A1/A2/B1/B2 在 v3 strict 下通过，并由 v4 “只新增 3 个可行驶像素、0 removed、0 other change”的单调性继承；C/D/E 在最终 v4 下直接 strict 通过。另对旧 Jiangtong 场景做了 249 step IDM 回归，车辆碰撞 0、道路边界碰撞 0、strict safety=True。源码五文件通过 py_compile 和 git diff --check，精确 stage 后提交为 112d2bd…，annotated tag 为 fullmine-vector-v4-runtime-freeze-20260814。

因此，当前地图不仅可以作为 FullMine 后续单车/双车规划、IDM/Pure MCTS/Fleet MCTS 的正式研究基线，而且已经完成全矿 Representative Coverage v1 与三场 Pure MCTS representative transfer。仍需严格保留边界：它不是官方 production-authoritative drivability，也没有穷举全矿每一条 path/每一米可行驶面。

## 0.2 当前唯一应视为“最新真相”的锚点

| **项目**                       | **当前值**                                                                 |
|--------------------------------|----------------------------------------------------------------------------|
| 正式仓库                       | /root/MineSim-Dynamic                                                      |
| Conda                          | minesim；Python 3.9.25                                                     |
| 当前工作分支                   | fullmine-v4-mcts-representative-dev；HEAD 仍为 frozen base commit 112d2bd… |
| 冻结 commit                    | 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e                                   |
| 冻结 tag                       | fullmine-vector-v4-runtime-freeze-20260814                                 |
| Final V4 bitmap SHA            | 51abcd5a86e5c510204a5dacc873691506d721f98982ab7f98585d4e0f7efdd0           |
| Final targeted manifest SHA    | f8d95af33ebc71b88ace93c3e538bec3761e80d7a9b610a2bed7408fada4ea2b           |
| Final freeze manifest SHA      | 30326ee281799410359900c00ca2b1f4a89290f9f0ba9366d30e8c939f4bfdaa           |
| Postcommit record SHA          | 5a6287cd6433641cfc33ce725bf0e4f1f8dc1796b91d86dbd5bebf3c39968300           |
| 当前工作区最后一次状态         | 仅 ?? ^C；未进入任何正式 commit/tag；禁止误清理                            |
| Representative Coverage freeze | bab9e77446e9c3b5747bb2721d035ca726b482418559b5f2a1018fe5e0018c5e           |
| Representative Coverage tag    | fullmine-v4-representative-coverage-v1-20260814                            |
| Pure MCTS summary SHA          | 742d0716a00364a625e01b27c693134488211c8989e4996b072739c3a500d056           |
| Pure MCTS freeze SHA           | 322e90d6995c410597d01925de6d77f1fd91ddb8c4c73a25c3e87446d37ac1fa           |
| Pure MCTS tag                  | fullmine-v4-pure-mcts-representative-transfer-v1-20260814                  |
| Disaster-Recovery              | Git bundle + archive 独立 restore PASS；详见第24章                         |

## 0.3 事实等级与文档冲突处理

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

## 0.4 接手后绝对不要直接做的事情

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

## 0.5 新 AI 第一轮只读核验命令

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

# 1. 本手册的证据来源、覆盖范围与 Codex/AI 归属说明

## 1.1 用户提供/上传的主要资料

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

## 1.2 关于“今天 Codex 做了什么”的严谨表述

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

# 2. 项目定义、研究主线与 MineSim 当前闭环架构

## 2.1 一句话定义

MineSim-Dynamic 是面向露天矿非结构化道路无人矿卡的场景化闭环仿真与规划研究项目。当前项目不是“只写一个 MCTS”，而是四条相互依赖的主线：MineSim 仿真链可靠复现、规划算法（IDM/Pure MCTS/Fleet MCTS）、benchmark/场景设计、真实 GIS 新矿区地图工程。

## 2.2 当前闭环调用链

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

## 2.3 当前研究主线状态

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

# 3. 项目完整时间线：从 IDM Baseline 到 FullMine V4 Freeze

| **日期**        | **阶段**                             | **结果/意义**                                                                                                                                                                                 |
|-----------------|--------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 2026-07-22      | 新地图接入框架                       | 明确 Raster/Semantic/Scenario 三类地图成果与新矿区接入思路。                                                                                                                                  |
| 2026-07-26      | IDM Baseline                         | commit 2521aa4…；tag idm-replay-autodl-baseline；建立云端/Git/AI 安全规范。                                                                                                                   |
| 2026-07-30~31   | Pure MCTS 闭环                       | MCTSPlanner 外壳、状态/动作/搜索/奖励、轨迹适配、iLQR/确定性修复。                                                                                                                            |
| 2026-08-01      | Jiangtong 几何/安全                  | CV/CTRV、buffer、viability、clearance 等迭代。                                                                                                                                                |
| 2026-08-02      | MCTS 正式结果 + 专家数据             | commit 94693dc…；Dapai/Jiangtong；448 strict expert samples。                                                                                                                                 |
| 2026-08-03~07   | 五 Planner / fairness / Budget       | 统一 evaluator；Adapted Frenet/Maneuver/Simple；budget 50/100/200/300。                                                                                                                       |
| 2026-08-08~09   | Multi/Fleet MCTS                     | Dapai 双受控时序机制；Jiangtong V22 因约 +9.496s 时序差被负筛选。                                                                                                                             |
| 2026-08-09      | J117 Phase1-4C                       | 真实 GeoJSON pilot -\> Map API -\> minimal Scenario -\> 423 step/42.3s 单车全路线。                                                                                                           |
| 2026-08-10      | J117 Phase5                          | dual-ego production runtime + Pure MCTS；5 seeds benchmark/swept safety 通过；commit da4105b。                                                                                                |
| 2026-08-11      | FullMine V1                          | full structural、DEV_ONLY mask、token2ind O(1)、独立 geojson_full_mine_dev；single/dual smoke；tag fullmine-dev-runtime-pass-20260811。                                                       |
| 2026-08-12 上午 | 源数据最大利用审计                   | 6 missing roads、road332/484、Z、topology；从保守排除转为有 provenance 的有效修复。                                                                                                           |
| 2026-08-12 中午 | Vector V2 Semantic                   | 100 effective roads / 553 paths / 8 repairs / raw lane Z；V1-\>V2 增量回归。                                                                                                                  |
| 2026-08-12 下午 | V2 Bitmap + Targeted                 | lane5186 5px；15 lanes；7 depth-safe scenarios；planner route 7/7。                                                                                                                           |
| 2026-08-13      | CollisionLookup + C/D/E              | XG90G 前后悬/梯形 bug + exact SAT fallback；candidate v1/v2；C/D/E 一度关闭。                                                                                                                 |
| 2026-08-13      | A/B shadow + planner                 | A1 route-end virtual lead 4.5m bug；A2 中途停车进一步诊断；形成独立 shadow workflow。                                                                                                         |
| 2026-08-13~14   | Steering-rate planner fix            | A2 真正 blocker 收敛为高速下转向速率不可行；建立曲率/转向速率 speed profile + backward braking envelope；A/B shadows 全通过。                                                                 |
| 2026-08-14      | V3 exact trajectory patch            | 基于 A1/A2/B1/B2 最终真实轨迹 exact footprint 扫描，+724px，A/B strict 全通过。                                                                                                               |
| 2026-08-14      | V4 D patch                           | current-planner D 在 v3 step66 暴露 3px 真物理 gap；72-state shadow -\> v4 +3px；D/C/E v4 strict 通过。                                                                                       |
| 2026-08-14      | 最终 7/7 + 旧图回归                  | final acceptance 7/7；Jiangtong IDM 249 steps，0 vehicle collision、0 road boundary collision。                                                                                               |
| 2026-08-14      | Git freeze                           | 5-file static/stage gate -\> commit 112d2bd… -\> annotated tag fullmine-vector-v4-runtime-freeze-20260814。                                                                                   |
| 2026-08-14 P0   | Disaster Recovery                    | 最终 Git bundle + archive 独立恢复验证 PASS；V4 可脱离当前实例恢复。                                                                                                                          |
| 2026-08-14 晚间 | Representative Coverage v1           | 13 route init 全过；static coverage 9 validated / 4 limitations / 2 unavailable；3 条 IDM closed-loop 3/3；freeze/tag 完成。                                                                  |
| 2026-08-14 晚间 | Pure MCTS Representative Transfer v1 | FullMine unloading/road/intersection 三场 Pure MCTS closed-loop 3/3 PASS；goal contract 修正后冻结 summary/freeze/tag。                                                                       |
| 2026-08-14 最新 | Neural-MCTS readiness audit          | 仅做 source/data inventory；未训练神经网络。发现 expert_data schema 已存在、通用 PyTorch training 框架存在、FullMine 当前 raw decision samples 674（含 smoke/过终点冗余，不能直接当训练集）。 |

# 4. 新地图与原项目两个成品地图的异同：到底“做到什么程度”

## 4.1 先澄清三张地图与 J117 的关系

“之前的两个地图”指原项目中已经作为成品资产使用的广东大排（guangdong_dapai, v1.6）与江西江铜（jiangxi_jiangtong, v1.5）。J117 不是第三张原始地图，而是从用户 FullMine 原始 GeoJSON 中切出的真实 junction pilot，用来证明新 GIS 数据能够贯通 Map API -\> Scenario -\> Planner -\> Controller -\> Runtime/MCTS。FullMine 才是本轮真正的新全矿地图。

FullMine 当前通常被简称“Vector V4”，但严格分层应写成：Vector V2 semantic + 最终 V4 bitmap/runtime freeze + 当前 planner/CollisionLookup 修复。目录和 map identity 仍保留 \`geojson_full_mine_vector_v2_dev\`，这是为了保持已经验证的 semantic identity；不要为了名字好看而重命名冻结资产。

## 4.2 三张地图详细对比

| **对比项**                    | **广东大排**                   | **江西江铜**              | **FullMine Vector V4**                                                                                                                              |
|-------------------------------|--------------------------------|---------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| 身份                          | guangdong_dapai                | jiangxi_jiangtong         | geojson_full_mine_vector_v2_dev / V4 runtime freeze                                                                                                 |
| 原始来源                      | 外部 MineSim HD Maps 成品      | 外部 MineSim HD Maps 成品 | 用户原始 8 类 GeoJSON -\> 本项目 converter + source/effective provenance                                                                            |
| 版本/定位                     | 1.6；原项目成品资产            | 1.5；原项目成品资产       | DEV/Research；final runtime tag 20260814                                                                                                            |
| Semantic                      | 成品 semantic                  | 成品 semantic             | 本项目生成；100 effective roads / 553 reference_path / 565 dubins / 184 polygon                                                                     |
| Bitmap                        | 成品 PNG mask                  | 成品 PNG mask             | 本项目 DEV mask；d2af -\> v1 -\> v2 -\> v3 -\> v4 additive evidence chain                                                                           |
| Mask authoring rule           | 未公开                         | 未公开                    | 工程规则/patch 证据透明；但不等于权威 production rule                                                                                               |
| Scale/值                      | 10 px/m；0/255-\>bool          | 10 px/m；0/255-\>bool     | 10 px/m；0/255-\>bool；46322x42411                                                                                                                  |
| whole polygon=drivable        | 否                             | 否                        | 否；明确拒绝 whole-polygon 填白                                                                                                                     |
| 主要车辆                      | XG90G 9x4m                     | NTE200 13x6.7m            | 当前 FullMine alias/targeted 几何使用 XG90G 9x4m                                                                                                    |
| Semantic 可追溯性             | 只有成品资产；authoring 不透明 | 同左                      | 强：source inventory 与 8 repair records 分离，repair 有 provenance                                                                                 |
| Production drivability 权威性 | 高于新地图：成品资产           | 高于新地图：成品资产      | 未证明；缺 authoritative drivable surface/internal exclusions                                                                                       |
| 单/双车接口                   | 原生/本项目扩展可用            | 原生/本项目扩展可用       | Map API + single/dual 基础 runtime 已通过；7 targeted closed-loop + Representative IDM/Pure-MCTS 验收已通过。                                       |
| MCTS 证据                     | 历史单车/多车 benchmark        | 历史单车 benchmark        | J117 Pure/Fleet MCTS 已证明同源 GIS 链；FullMine V4 Representative Pure MCTS 3/3 PASS 并冻结；FullMine Fleet 正式 representative benchmark 尚未做。 |
| auxiliary                     | 原 production API 支持有限     | 同左                      | semantic 有 6 auxiliary_area；API 后续如需再扩                                                                                                      |
| 最安全表述                    | 原项目成品地图                 | 原项目成品地图            | 科研/benchmark-ready 的新地图；不是 production-certified                                                                                            |

## 4.3 为什么不能用“polygon 全白”复制老地图

对 Dapai/Jiangtong 成品 semantic polygon 与成品 mask 的审计已经证明：polygon 内存在大量 non-drivable 内部区域。约略 drivable 比例：Dapai road 74.5%、junction 80.8%、loading 68.2%、unloading 73.9%；Jiangtong road 58.9%、junction 68.0%、loading 44.0%、unloading 71.4%。因此，“只要在 road/junction/load/unload polygon 内就全部可行驶”与原项目成品地图习惯不一致。

| **类别**  | **Dapai polygon 内 drivable（约）** | **Jiangtong（约）** |
|-----------|-------------------------------------|---------------------|
| road      | 74.5%                               | 58.9%               |
| junction  | 80.8%                               | 68.0%               |
| loading   | 68.2%                               | 44.0%               |
| unloading | 73.9%                               | 71.4%               |

## 4.4 新地图当前能做什么

> **•** 作为 MineSim-compatible 研究地图加载：Semantic/Bitmap 走 production Map API 路径，支持 road/reference_path/topology 查询。
>
> **•** 构造并运行新的单车/双车 Scenario；已有 basic single/dual smoke 及 7 个 targeted real closed-loop 证据。
>
> **•** 在已验证路径上使用当前 IDM/控制器/KBM 完成 route exact、target order、goal、drivable 全套闭环验收。
>
> • Pure MCTS 已在 FullMine Representative 三场完成 3/3 closed-loop PASS 并冻结；Fleet/Multi-MCTS 的 FullMine 正式代表性实验仍可作为下一阶段。
>
> • 已从 553 条 reference_path 中完成 Representative Coverage v1：覆盖 road/intersection/loading/unloading/auxiliary 与 west/central/east 组合，13 个候选 route 初始化 13/13；最终 static coverage 为 9 validated / 4 documented limitations / 2 unavailable。
>
> **•** 使用 raw lane Z 作为 semantic elevation candidate，支持比纯 2D 更丰富的地图语义；但 slope 仍为 0，datum/smoothing 未权威验证。
>
> **•** 精确回放/复核当前 15 条重点 target lane：13 条 V2 recovered lanes + road484 的 6942/6989。

## 4.5 新地图当前不能证明什么

> **•** 不能证明与真实矿区 production 可行驶区域逐像素一致。
>
> • 不能证明 553 条 path、100 个 effective road 的每一米都已被 closed-loop 穷举。当前证据已经从“15 条重点 lane + 7 targeted 场景”扩展到“Representative Coverage v1”，但这仍是代表性覆盖，不是 exhaustive coverage。
>
> **•** 不能证明 gear=-1 的 50 条 lane 运营方向已由矿方确认；当前保持 source topology orientation。
>
> **•** 不能证明 boundary/polygon Z 可作为高程真值；当前只信 lane Z，且 slope authoring rule 未完整复现。
>
> **•** 不能证明 Jiangtong 的 NTE200 CollisionLookup 车型分支语义正确；selector 是历史 bug，目前仍会实例化 XG90G。
>
> • 不能宣称 Pure/Fleet MCTS 已在 FullMine 全矿形成统计普适结论。当前 Pure MCTS representative transfer 为 3/3 PASS；FullMine Fleet/Multi-MCTS 正式场景与更大规模统计仍未完成。
>
> **•** 不能宣称 Neural-MCTS 已训练完成。

# 5. J117 Pilot：为什么它是新地图工程的金标准小区域

## 5.1 Pilot 的目的

J117 = Junction 117。它从完整 FullMine 原始 GeoJSON 中选出一个真实交叉区域，先把 WGS84/UTM/local 坐标、semantic、bitmap、Map API、Scenario、IDM、Controller、KBM、dual-ego/MCTS 全链跑通，再扩展到全矿。其价值是把“地图工程问题”和“全图规模问题”分开，并提供后续 FullMine 代码改动的回归锚点。

## 5.2 Pilot 路线与 MCTS 证据

| **路线** | **源 lane**            | **FullMine semantic token**                 |
|----------|------------------------|---------------------------------------------|
| A        | 6670 -\> 6674 -\> 5690 | path-000426 -\> path-000430 -\> path-000330 |
| B        | 5691 -\> 6546 -\> 6523 | path-000331 -\> path-000403 -\> path-000387 |

固定冲突点 local XY 约 (2878.0888, 2799.6561)。Phase 4C 单车全路线完成 423 steps / 42.3s；Phase 5 dual-ego 中 No-MCTS aligned baseline 几乎同时过冲突点并发生真实重叠，而 Pure MCTS seed0 将 crossing gap 拉开到约 1.561s，1ms swept min clearance 约 0.594m；5 seeds benchmark 5/5 PASS、swept 5/5 PASS。J117 随后冻结，不应在 FullMine 地图收尾阶段重复调 MCTS。

# 6. FullMine V1：从原始 8 类 GeoJSON 到可运行全矿结构基线

## 6.1 原始数据与坐标链

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

## 6.2 V1 structural 输出与系统性 correctness 修复

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

## 6.3 V1 DEV_ONLY mask 与为什么不冒充 production

仓库和 Git history 未发现从原始 GIS 生成 Dapai/Jiangtong production mask 的 authoring pipeline；原项目提供的是 finished PNG。结合成品 polygon-mask 审计，whole-polygon 填白不可信。因此 V1 采用透明但保守的 lane-centered corridor + parent clipping 规则，并明确 \`DEV_ONLY_NOT_PRODUCTION_VALIDATED\`。这一步的价值是可解释、可回归，而不是“还原官方 mask”。

Full-Mine 大图第一次 planner.initialize 极慢的根因也在 V1 暴露：get_polygon_token_using_node() 对约 400k node 重复线性扫描。利用已有 token2ind 改成 O(1) 后，J117/FullMine 回归通过，commit 32fb429；随后从临时 J117 alias 独立为 geojson_full_mine_dev，commit d81c571、tag fullmine-dev-runtime-pass-20260811。

# 7. FullMine Vector V2 Semantic：从保守 V1 到“最大化源数据利用率”

## 7.1 V1 为什么只有 93 roads / 540 paths

V1 遵循“不能猜”的保守策略：road332 自交、6 个 source road polygon 缺失、road484 polygon/boundary/lane 版本不一致等异常被排除，所以 V1 是软件基线，不是数据利用率上限。8 月 12 日对 source 内部冗余（road boundary、lane、已有正常 road）做交叉验证后，证据足以把这些异常从“排除”升级为“有 provenance 的 effective repair”。

## 7.2 六个 missing roads、road332、road484 的 8 条 repair records

| **Road**                | **Effective 策略**                         | **证据逻辑**                                                                                                                                   |
|-------------------------|--------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------|
| 339/340/353/356/357/360 | derive_missing_road_from_boundary          | road polygon 缺失，但两条 road_boundary + 对应 lane；在正常 roads 上验证 boundary closure 规则后恢复                                           |
| 332                     | repair_source_road_make_valid_keep_largest | source 自相交为极小 sliver；make_valid 后保留主 polygon，lane5050 在主道路内                                                                   |
| 484                     | replace_source_road_geometry_from_boundary | source polygon 与 lane/boundary 偏差 11-22m，证据支持 source version stale；effective 使用 boundary-derived polygon，原 source 保留 provenance |

关键工程原则是 source/effective 分离：source roads 仍然是 94，不把派生的 6 个 road 冒充源数据；所有 8 条 repair 独立记录 provenance。

## 7.3 V2 最终 semantic 数量与 V1 增量回归

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

## 7.4 Topology 与 elevation 的“能用/不能瞎修”边界

> **•** 同 topo ID 的 endpoint 存在厘米级甚至约0.2m XY 偏差，因此 canonical snapping 必要；但不同 topo ID 可有完全相同 XY，约45对集中在 auxiliary gear transition。禁止按距离 merge 不同 topo ID。
>
> **•** gear=-1 共50条：auxiliary 48、loading 1、unloading 1；road/junction 0。业务运营方向未权威验证，保持 stored topology orientation。
>
> **•** 553 lanes / 314,692 points 全有 Z，range≈1009.048236–1321.0。全量“XY≈0但Z显著跳变”的严重异常主要来自 boundary，lane 质量明显更高。
>
> **•** lane6713 有唯一 hard internal +0.519112m seam：保留 raw Z + QA，不凭空平滑。
>
> **•** V2 waypoint\[3\] 使用 raw lane elevation；slope 仍为 0.0，因为官方 smoothing/slope authoring rule 未完整复现；source_z_datum_verified 仍为 false。

# 8. Vector V2 Bitmap 与 Targeted 场景：从“地图能加载”到“真实矿卡 footprint 能跑”

## 8.1 15 条重点 lane 与 frozen/additive 策略

重点集合 = 13 条 V2 新恢复 lanes + road484 两条 lanes 6942/6989。15/15 centerline waypoint 在 frozen V2 bitmap 上 coverage=1.0；进一步用标准 XG90G 9x4m、rear-axle reference 的实际车辆 footprint 审计。绝大多数 endpoint failure 只是车头/车尾跨相邻 region 的 overhang；采用 0.5m endpoint guard 后只剩 lane5186 真正 deep-interior gap，最终以 parent-safe swept patch 加 5 pixels。

| **类别**         | **Lane IDs**                                                                 |
|------------------|------------------------------------------------------------------------------|
| V2 recovered 13  | 5050, 5163, 5164, 5165, 5166, 5171, 5172, 5175, 5178, 5179, 5180, 5181, 5186 |
| road484 targeted | 6942, 6989                                                                   |

## 8.2 为什么没有直接用“from-source full rebuild”替换 frozen mask

可复现 V2 bitmap builder 能从 source 重新生成 100 effective roads/553 lanes，且 road484 active；但 full rebuild candidate 与历史 frozen V2 比较出现 added=1779、removed=2772，差异 100% 集中于 8 个 repaired roads 的 raster edge discretization。虽然 full rebuild 对 V1 是 monotonic，但直接替换已通过 runtime 的 frozen baseline 会引入无必要的回归面。最终策略：frozen V2 + 经真值验证的 additive patch；可复现 builder 保留作为来源解释工具，而不强行替换运行基线。

## 8.3 大 PNG 与局部审计策略

FullMine bitmap 约 46322x42411 @10px/m，约 1.964B pixels。Pillow 默认会触发 DecompressionBomb；反复整图解码也浪费内存。因此建立 tiled TIFF 审计缓存（512x512 blocks，约1.844GiB）并优先用 rasterio window 做局部 footprint truth。大 raster pipeline 也避免直接依赖 PNG window writer，优先 tiled GeoTIFF -\> CreateCopy PNG。

## 8.4 BFS target_depth=5：为什么 15 lanes 被拆成 7 个场景

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

# 9. C/D/E Runtime 与 CollisionLookup：如何区分“地图缺口”和“验证器 bug”

## 9.1 初始症状

C/D/E targeted closed-loop 已经真实执行 planner.compute_trajectory() 与 simulation.propagate()，route exact，车辆也实际向前；但在接近 path interface 时被道路边界检查判定为 collision。继续盲目给 mask 加白像素会把验证器自身的错误吞进地图，因此停止扩 mask，转而审计 CollisionLookup 与标准 CarFootprint。

## 9.2 XG90G 几何根因 1：前后悬反置 + 梯形

标准 rear-axle XG90G footprint 应为后 -2.5m、前 +6.5m、宽 4m。旧 CollisionLookup 却定义 collision_lrear=6.5、collision_lhead=2.5；并且 p1.x 还使用 -collision_lrear/2，导致四点不是矩形而是梯形。旧 lookup 纵向覆盖约 \[-6.5,+2.6\]m，与实际车辆方向完全相反。

修复：XG90G collision_lrear 6.5-\>2.5，collision_lhead 2.5-\>6.5；p1.x 从 -lrear/2 改为 -lrear。几何 regression 得到 p0=(-2.5,-2)、p1=(-2.5,+2)、p2=(+6.5,+2)、p3=(+6.5,-2)，lookup yaw0 范围约 \[-2.4,+6.6\]m。

## 9.3 根因 2：0.2m lookup 栅格的保守侧向假阳性

前后悬修正后，C/D 仍各有少量 lookup 黑像素，但标准物理 footprint 与这些像素没有正面积重叠；残余侧向超出约 0.079–0.207m，来自 0.2m lookup 离散栅格的保守扩张。最终没有缩车、没有取消 lookup、也没有继续扩地图，而是在 lookup 首先命中 0.1m 黑 pixel 时，使用真实车辆 oriented rectangle 与该 pixel square 做 exact SAT intersection；只有真实相交才 collision。

回归要求同时满足：残余 false positive 被过滤、故意放入真实 physical pixel 仍报告 collision、all-white image 保持 collision-free；并重新跑 polygon rectangle/longitudinal direction regression。最终 CollisionLookup SHA 冻结为 10c1d1339e742ca893fedb4aa51402addfba82e16e08f68339ea35d35ba3043b。

## 9.4 CollisionLookup 修好后，C/D 暴露的才是真地图小缝

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

# 10. A/B Shadow 与 Planner：A1 endpoint bug、A2 中途停车到最终 steering-rate 解法

## 10.1 为什么要做 shadow harness

A/B 在早期 mask 上很快触发 first_bad。如果 formal harness 一碰黑 pixel 就 raise，只能看到第一处 failure，无法知道 controller/vehicle 后续真实会怎样纠正。于是复制 formal harness 生成 shadow 版本：保持 route、planner、controller、dynamics、candidate 完全不变，只把 mask failure 从“raise”改为“记录并继续”；每 0.1s 保存真实 (x,y,yaw,v)，formal harness SHA 保持不变。这样最终 mask patch 可以依据真实闭环轨迹，而不是固定误差外推。

这一步还解决了 B2 的一个重要陷阱：固定保持 failure 时 lateral_offset≈0.242m、yaw_offset≈0.113rad 外推 25m，会产生 227px 假“缺口”，因为真实 controller 后续会纠偏。该结果被明确拒绝，没有写进 v3。

## 10.2 A1：route endpoint 被当作 4.5m 长的虚拟前车

A1 已访问三个 targets，却在 goal 前约 4.84m 提前停车。IDM free-road virtual lead 使用 \`length_rear = ego_state.car_footprint.length / 2 = 4.5m\`；而 route endpoint 本质是一个零长度停止点。结合 min_gap=1m、rear axle-\>center=2m、goal 设为 path end 前3m，理论提前量 = 4.5+1+2-3 = 4.5m，与实测 4.8369m 高度一致。

最小修复只改语义：virtual route endpoint 的 length_rear=0.0。数学 regression legacy error=4.5m、fixed=0；A1 fixed shadow goal=True。这个修复保留到最终 planner。

## 10.3 A2：先排除 endpoint，再推翻“leading-object”中间假设

A2 endpoint 修复后仍约 step250 停在 path-000299 中段：route remaining≈274.44m，第三 target path-000301/lane5179 起点还在≈242.61m 前方，所以 route endpoint 被严格排除。当时下一嫌疑是 occupancy/leading-object 误选，这是合理的中间假设；但后续对 planner 行为、轨迹和可执行性继续排查后，最终 blocker 收敛为“旧 9–11m/s 速度在某些高曲率段要求的 steering-rate 超过车辆/控制可实现范围”，而不是 route、mask 或 tracked object 本身。

## 10.4 最终 steering-rate-aware speed profile

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

# 11. V3/V4 Bitmap：用最终真实闭环轨迹做 exact physical patch

## 11.1 V3 为什么必须基于“最终 planner 的真实 trajectories”

A1 endpoint 修复、A2 steering-rate speed profile 都会改变车辆在路上的具体姿态。如果仍使用旧 planner 的失败 pose、恒曲率 corridor 或固定 offset 外推，就会把已经不再发生的 footprint 误差写进 mask。因此最终 v3 只读取 final planner 下 A1/A2/B1/B2 的 actual shadow_trajectory，并要求每个 trajectory/result/provenance 与 planner SHA 对上。

## 11.2 V3 builder 的性能/正确性演进

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

## 11.3 V3 final patch 结果

| **Scenario**  | **final trajectory missing pixels** |
|---------------|-------------------------------------|
| A1            | 83                                  |
| A2            | 176                                 |
| B1            | 348                                 |
| B2            | 117                                 |
| Global unique | 724 pixels = 7.24m²                 |

V3 以 candidate v2 SHA 57514c… 为 source，added=724、removed=0、other=0；四条最终 trajectories 复扫 remaining missing 全部为0。V3 candidate SHA=5a11d523b9931dc99d4267eeb6145ff5674d29ba56fda0749bc06a28aa2c8d7e。随后 A1/A2/B1/B2 formal strict 全部 PASS。

## 11.4 为什么 V3 之后还出现 V4：D step66 是新的真实物理 gap

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

## 11.5 从 d2af 到 v4 的 additive 演化

| **阶段**           | **SHA 前缀** | **含义**                                                      |
|--------------------|--------------|---------------------------------------------------------------|
| d2af baseline      | d2afc84e...  | V2 frozen/additive baseline，已含 lane5186 5px physical patch |
| candidate v1       | 7c586421...  | 相对 d2af +112px / 1.12m²，C/D/E interface truth              |
| candidate v2       | 57514c52...  | v1 +6px；相对 d2af 累计 +118px                                |
| candidate v3       | 5a11d523...  | v2 +724px / 7.24m²，final A/B trajectories                    |
| candidate v4 FINAL | 51abcd5a...  | v3 +3px / 0.03m²，current-planner D full shadow               |

按 verified counts 推导，最终 v4 相对 d2af 基线共增加 845 pixels = 8.45m²；若把 d2af 之前 lane5186 的 5px 也计入，则相对更早 frozen V2 链累计约 850px = 8.50m²。这个面积很小，说明最终验收不是通过大范围“涂白”获得，而是多轮 exact trajectory / physical footprint 的局部补缝。

# 12. Final Targeted Acceptance：7/7 到底意味着什么

## 12.1 最终 acceptance matrix

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

## 12.2 为什么 A/B 可以从 v3 继承到 v4

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

## 12.3 一次重要失败：stale manifest 混用了旧 C/D/E JSON

曾生成 \`/root/autodl-tmp/minesim_p0_preflight/v3_targeted_7of7_acceptance.json\`（SHA 25f9c00d…），错误复用了旧 combined CDE result：A/B PASS、C/D 旧失败、E PASS，结果只有 5/7。这个 manifest 被立即判定为 INVALID/STALE，绝不能冻结。随后 C/D/E 在 current planner/当前 bitmap 下重新单场景运行，D 才真正暴露 v3 step66 的 3px physical gap，最终促成 v4。

可复用规则：最终验收 manifest 必须绑定 planner SHA、harness SHA、CollisionLookup SHA、bitmap SHA、每个 scenario result SHA；“文件名一样”不等于同一证据世代。

# 13. 旧图回归与 NTE200：为什么最终 freeze 前还要跑 Jiangtong

## 13.1 NTE200 selector 是历史 bug，不是本轮引入

当前 \`CollisionLookup.\_\_init\_\_\` 中，\`VehicleType.MineTruck_NTE200\` 分支实际仍实例化 \`MineTruckXG90G()\`；对比 base HEAD 与 current source 证明两者相同，因此这是 pre-existing selector bug。真正的 MineTruckNTE200 class 参数存在：length=13.0、width=6.7、collision_w=5.5、collision_lrear=1.6、collision_lhead=7.2，但 selector 没用它。

本轮没有“顺手修 NTE selector”，因为那会在 7/7 收口时突然扩大 scope；但我们改了 XG90G CollisionLookup 公共几何/精确 filter，而 Jiangtong 旧场景实际 selector 又走 XG90G，所以必须做真实 old-map runtime regression。

## 13.2 Jiangtong IDM 249-step regression

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

# 14. 最终静态门禁、源码冻结、Commit 与 Tag

## 14.1 五个正式源码文件

| **文件**                           | **SHA256**                                                       | **本轮关键作用**                                         |
|------------------------------------|------------------------------------------------------------------|----------------------------------------------------------|
| vehicle_parameters.py              | e14a32f88bca707de5a6d9661188259be7a9112bbefb1b0d90bd4d22358c4977 | FullMine vehicle/location 注册相关                       |
| collision_lookup.py                | 10c1d1339e742ca893fedb4aa51402addfba82e16e08f68339ea35d35ba3043b | XG90G 几何 + exact pixel SAT filter                      |
| minesim_bitmap_png_loader.py       | 3bad8ebe750c2b56a02ac8ffeef4eaf81424f81a4727aa272b2345919b9bc651 | 新地图 bitmap registry/loader                            |
| minesim_semanticmap_json_loader.py | 41872d1e568cd1a68bc2c2997d7dfc3c7db93d3ef0e1959597d891902049ff34 | 新地图 semantic registry/loader                          |
| abstract_idm_planner.py            | 541ec74985d06322656e66c48abb382030d679171341408575d936e0a069e75e | route-end zero-length lead + steering-rate speed profile |

static gate：上述五文件 \`python -m py_compile\` PASS，\`git diff --check\` PASS；精确 \`git add\` 只 stage 这 5 个文件，staged diff check PASS。precommit patch SHA=f30da9f4…。

## 14.2 最终 Git 锚点

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

## 14.3 一个必须提醒下一位 AI 的备份风险

Git tag 冻结的是源码，不会自动把 \`/root/autodl-tmp\` 下 1.9B-pixel bitmap、manifest、logs、shadow trajectories 一起写入 Git。当前对话已创建 final bitmap、targeted manifest、freeze record，但没有看到“V4 final map archive + Git bundle”的明确最终动作。因此下一位 AI 如果要做灾备，第一步应只读检查是否已有 20260814 final archive/bundle；不存在时再单独创建。不要把 8 月 11 日 V1 bundle 误当 V4 bundle。

# 15. 云端关键资产、路径、SHA 与“哪些不能覆盖”

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

# 16. 全过程问题库：症状 -\> 根因 -\> 解决 -\> 可复用规则

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

# 17. 用户实际工作流：AI / Codex / AutoDL 如何协作才最省钱、最安全

## 17.1 标准循环：观察 -\> 计划 -\> 执行 -\> 验收 -\> 冻结

| **步骤** | **实际规则**                                                             |
|----------|--------------------------------------------------------------------------|
| **观察** | 只读核验环境、Git、SHA、目标文件/log；不先改。                           |
| **计划** | AI 只给当前一个最小目标、为什么做、PASS/FAIL 条件；不重述全项目。        |
| **执行** | 用户 AutoDL terminal 跑机械命令；AI/Codex 只写关键代码/诊断。            |
| **验收** | 只看当前 gate；失败先找第一根因，不回到全仓重审。                        |
| **冻结** | PASS 后写 manifest/hash；需要时 exact stage/commit/tag；下一阶段不重跑。 |

## 17.2 每段 terminal 命令的统一前缀

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

## 17.3 Codex 成本策略（当前可用，但必须边界清晰）

| **任务**                                       | **推荐方式**                                                   |
|------------------------------------------------|----------------------------------------------------------------|
| git/status/hash/file existence/grep/py_compile | 直接 shell/Python，不花模型额度                                |
| 小范围代码审计/最小 patch                      | Codex gpt-5.6-luna medium                                      |
| 中等复杂多模块 bug                             | 必要时 Terra medium/high                                       |
| 核心算法/顽固 closed-loop/关键终审             | 仅必要时 Sol high；完成立即回 Luna                             |
| 长 build / runtime / screen 等待               | terminal 执行；Codex 不负责长期挂着等                          |
| Codex 输出                                     | 只要 PASS/FAIL + modified/evidence；不写长报告，不重复已知事实 |

重要：用户当前不是“永远禁止 Codex”，而是“省钱优先、只有边界明确且确实有价值时用”。8 月 12 日曾临时要求停止 Codex；随后又明确允许困难工作在省钱前提下交给 Codex。最新工作流应以后一条为准。

## 17.4 长任务 / screen / SSH

> **•** 长任务统一写独立 log + rc 文件；screen 只是进程托管，不是证据源。
>
> **•** 启动前 \`screen -S name -X quit\` 返回 No screen session found 很常见，通常只说明“旧 session 不存在”。
>
> **•** 状态查询优先 \`cat run.rc \|\| echo RUNNING\` + \`tail/grep log\`；不要因为看不到即时输出而重复启动。
>
> **•** \`screen=Dead\` + 无 Python + rc 缺失才是可疑硬终止；此时先审 runtime symlink/trap 是否恢复。
>
> **•** Heavy scenario 一次一个 Python process；A/B 早期同进程硬终止已经证明隔离更稳。

## 17.5 Git 与资产纪律

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

## 17.6 Terminal 乱码后的新规则

真实对话中长 heredoc/长 Python 块多次被前端拼接，甚至出现 \`PY ...\` 与终端输出混到命令里的乱码。因此以后 shell 指令以短 ASCII block 为默认；长脚本先生成文件并 \`bash -n\` / \`py_compile\`，再运行；文档/中文解释与 terminal code 分开。

# 18. AutoDL 资源模型：为什么“开 GPU 卡”其实常常是为了 CPU/RAM

## 18.1 已实测的两种 cgroup

| **实例状态**      | **cgroup CPU**           | **memory.max** | **GPU**             | **实际影响**                                        |
|-------------------|--------------------------|----------------|---------------------|-----------------------------------------------------|
| 低资源/卡未完全开 | 50000/100000 ~= 0.5 CPU  | 2GiB           | 无/不可用           | Full bitmap/scan 极慢；cached builder RC137         |
| 固定 4090D 实例   | 1500000/100000 = 15 vCPU | 80GiB          | RTX 4090 D 24564MiB | V3/V4 builder/runtime 稳定；CPU scanner 可隐藏 CUDA |

\`nproc=192\`、\`free -h\` 接近宿主机值曾严重误导资源判断。后续任何大任务都先读 \`/sys/fs/cgroup/cpu.max\` 与 \`memory.max\`。地图 conversion/footprint scanner 主要是 CPU/RAM 工作，GPU 本身价值不大；但 AutoDL 的 GPU 套餐会连带提供更高 CPU/RAM quota。

# 19. 新 AI/工程人员云端接手 SOP：10 分钟内定位正确阶段

## 19.1 Step 1：环境 / Git / 资源

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

## 19.2 Step 2：关键 SHA 只读复核

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

## 19.3 Step 3：理解“当前完成”和“下一步”

| **如果目标是…**           | **不要重做…**               | **正确起点**                                                                        |
|---------------------------|-----------------------------|-------------------------------------------------------------------------------------|
| 继续地图覆盖              | 不要重跑 A-E / 不重建 V1/V2 | 从 final tag 开新分支，选 road/junction/loading/unloading/aux representative routes |
| 跑 FullMine MCTS          | 不要再调 J117               | 从 final tag 构建 FullMine scenario/benchmark，先 smoke 再 full                     |
| 修 NTE200 selector        | 不要混入 V4 map commit      | 单独 bug branch；selector fix + NTE geometry + Jiangtong regression                 |
| 拿到 production mask/规则 | 不要覆盖 V4                 | 建立 V5/production-candidate 新版本，与 V4 做差分/回归                              |
| 做 Neural-MCTS            | 不要声称已有网络            | 先扩大场景/数据，按 scenario/time split；再 Value/Policy/PUCT                       |

## 19.4 接手者需要知道的当前“不要重跑”清单

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

# 20. 地图完成度的最终定义、当前结论与后续优先级

## 20.1 如果目标是“科研/论文/算法 benchmark 新地图”

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>结论：科研/论文/算法 benchmark 地图主线已完成并冻结<br />
Semantic/topology：完成<br />
Map API / loader：完成<br />
15 重点 lane static + route：完成<br />
7 targeted closed-loop：完成<br />
Representative Coverage v1：完成并冻结（9 validated / 4 limitations / 2 unavailable）<br />
Representative IDM closed-loop：3/3 PASS<br />
Representative Pure MCTS：3/3 PASS + freeze/tag<br />
旧 Jiangtong regression：完成<br />
Final V4 SHA/manifest/commit/tag + DR：完成<br />
=&gt; FullMine Vector V4 可作为正式 Research Baseline 与后续算法实验母版。</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## 20.2 如果目标是“production-authoritative 全矿地图”

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>结论：production-authoritative 全矿地图仍未具备声明条件<br />
缺少至少一种权威输入：production mask、drivable surface、internal obstacle/restricted polygon、mask authoring rule。<br />
Representative Coverage 已完成，但它不能替代 production truth，也不是 exhaustive coverage。<br />
仍需关注：gear=-1 运营语义、真实车型确认、NTE200 selector 技术债、slope/datum、auxiliary API（若算法需要）。<br />
这些问题不能靠继续“补白像素”证明。</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## 20.3 推荐后续路线（按价值/风险排序）

| **状态/优先级** | **任务**                       | **目的**                                                                               |
|-----------------|--------------------------------|----------------------------------------------------------------------------------------|
| DONE            | Final disaster-recovery        | bundle/archive 独立恢复已 PASS；禁止重复覆盖。                                         |
| DONE            | Representative Coverage v1     | 已完成 static -\> IDM smoke -\> freeze/tag；保留 documented limitations。              |
| OPEN-P0         | 获取 authoritative drivability | 向数据方索取 production mask/drivable surface/internal exclusions/authoring rule。     |
| OPEN-P1         | NTE200 selector 独立 bug       | 单独 bug branch 修复；不要混入 frozen V4；修后做 NTE geometry + Jiangtong regression。 |
| OPEN-P1         | 真实车型确认                   | 若 FullMine 现场车型不是 XG90G，建立独立 vehicle config 并重新评估 footprint/mask。    |
| OPTIONAL-P1     | auxiliary semantic API         | 只有后续 planner/benchmark 真需要 aux 查询时再扩 MineSimMapLayer。                     |
| NEXT-P2         | FullMine Fleet/Multi-MCTS      | 地图与 Pure MCTS baseline 已稳定，可从 frozen evidence 构造双车冲突代表场景。          |
| PAUSED-P2       | Neural-MCTS / adaptive budget  | 仅完成 readiness audit；用户当前明确先暂停，后续从数据契约/严格 split 开始。           |

# 21. 关键 Commit/Tag 速查与版本语义

| **Commit/Tag**                                                           | **阶段**                             | **意义**                                                                   |
|--------------------------------------------------------------------------|--------------------------------------|----------------------------------------------------------------------------|
| 2521aa4…                                                                 | idm-replay-autodl-baseline           | IDM baseline 锚点                                                          |
| 94693dc…                                                                 | MCTS/expert baseline                 | Pure MCTS、两场景正式结果、448专家样本                                     |
| f8ff186…                                                                 | Fleet internal clearance reward      | 多车内部净距 reward                                                        |
| 94794c… / tag jiangtong-v22-benchmark-screening-20260809                 | Jiangtong V22                        | 第二 benchmark 负筛选                                                      |
| 4bd2bff… / tag j117-phase3-production-map-load-20260809                  | J117 Phase3                          | Map API loader milestone                                                   |
| ec1c958…                                                                 | J117 minimal scenario                | Phase4B minimal Scenario                                                   |
| da4105b… / tag j117-phase5-dual-ego-pure-mcts-20260810                   | J117 Phase5                          | dual-ego + Pure MCTS 5 seed                                                |
| 32fb429…                                                                 | FullMine semantic lookup             | token2ind O(1) 大图性能修复                                                |
| d81c571… / tag fullmine-dev-runtime-pass-20260811                        | FullMine V1                          | 独立 map identity + basic runtime                                          |
| 112d2bd… / tag fullmine-vector-v4-runtime-freeze-20260814                | FINAL CURRENT                        | Vector V4 runtime fixes + final freeze                                     |
| 112d2bd… / tag fullmine-v4-representative-coverage-v1-20260814           | Representative Coverage v1           | 同一 frozen V4 commit 上冻结覆盖证据；不修改 bitmap。                      |
| 112d2bd… / tag fullmine-v4-pure-mcts-representative-transfer-v1-20260814 | Pure MCTS Representative Transfer v1 | 同一 frozen V4 commit 上冻结三场 Pure MCTS transfer 证据；不修改地图源码。 |

# 22. 可直接复制给下一位 AI 的最终接管 Prompt

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>You are taking over the MineSim-Dynamic project on AutoDL.<br />
<br />
Repository: /root/MineSim-Dynamic<br />
Conda env: minesim<br />
Python: 3.9.25<br />
Current known branch: fullmine-v4-mcts-representative-dev<br />
Frozen base commit: 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e<br />
Base map tag: fullmine-vector-v4-runtime-freeze-20260814<br />
Coverage tag: fullmine-v4-representative-coverage-v1-20260814<br />
Pure MCTS tag: fullmine-v4-pure-mcts-representative-transfer-v1-20260814<br />
<br />
Current final map:<br />
- semantic identity: geojson_full_mine_vector_v2_dev<br />
- semantic: 100 effective roads / 553 reference paths / 565 dubins poses / 184 polygons<br />
- V4 bitmap SHA256: 51abcd5a86e5c510204a5dacc873691506d721f98982ab7f98585d4e0f7efdd0<br />
- targeted acceptance: 7/7 PASS<br />
- Representative Coverage v1: frozen with documented limitations<br />
- Representative IDM smoke: 3/3 PASS<br />
- Representative Pure MCTS: 3/3 PASS<br />
- production-authoritative drivability: NOT PROVEN<br />
<br />
Critical rules:<br />
1. First read-only check git/status/SHA/cgroup. Never reset to make state look right.<br />
2. Never use git clean -fd, git reset --hard, or git add .<br />
3. Never overwrite d2af/candidate-v1/v2/v3/v4 bitmaps. Any new production map work gets a new version/SHA.<br />
4. Every executable shell block starts with cd /root/MineSim-Dynamic + source conda + conda activate minesim.<br />
5. No naked top-level exit in interactive commands.<br />
6. Static/CPU work uses CUDA_VISIBLE_DEVICES="". Heavy jobs: one scenario per Python process, log + rc, screen when SSH risk exists.<br />
7. Diagnose root truth before changing code/mask. CollisionLookup false-positive, controller infeasibility, planner bugs and actual mask gaps were all observed historically.<br />
8. NTE200 selector -&gt; XG90G is pre-existing technical debt; fix separately.<br />
9. FullMine V4 is research/benchmark-ready, not production-certified.<br />
10. Representative limitations are coverage/materialization limits, not proof of production defects.<br />
11. Do not rerun frozen phases unless hashes/source/vehicle/planner changed or evidence corruption is suspected.<br />
12. Neural-MCTS has NOT started training. Latest work only audited source/data readiness.<br />
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

# 23. 接手者自检：读完后必须能回答的问题

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

# 附录 A. 证据索引：关键结论应该去哪里复核

| **主题**                                               | **证据源**                                                                                                                                               |
|--------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------|
| FullMine V1 structural/mask/old-map comparison         | MineSim-Dynamic_新地图项目云端交接手册_2026-08-11.docx                                                                                                   |
| Vector V2 semantic/bitmap/15 target/7 scenarios        | MineSim-Dynamic_项目完整进展与云端AI接管超级手册_2026-08-12.docx                                                                                         |
| CollisionLookup/candidate v1-v2/A1 endpoint/A2中途停车 | MineSim项目云端接手与技术总览_2026-08-13(1).docx                                                                                                         |
| 长对话/terminal 原始证据                               | 粘贴的文本 (1)(20260813-130803).txt 及 20260813-155108/161756、20260814 多份补充日志                                                                     |
| V4 D patch / C/E final / 7/7 manifest                  | 20260814-062315 terminal log + final direct terminal outputs                                                                                             |
| Oldmap regression / static/stage/commit/tag            | 2026-08-14 当前对话 direct terminal output；本手册生成时的最新事实源                                                                                     |
| Representative Coverage v1                             | candidate manifest / route-init / static coverage / IDM smoke / representative_coverage_v1_final_freeze.json（2026-08-14 当前对话终端证据）              |
| Pure MCTS Representative Transfer v1                   | candidate-0010 goal-history audit；candidate-0002/recovery-0005 goal-stop acceptance；pure_mcts_representative_transfer_summary_v1.json + freeze_v1.json |
| Latest neural readiness audit                          | 20260814-130836 terminal output：source inventory / expert schema / sample count；仅 readiness，不代表训练完成。                                         |

接手时如旧 Word 与 final commit/tag 冲突，以当前 Git/terminal 为准。文档中的路径可能在后续人为归档后变化，因此“SHA + manifest 内容”比“文件名看起来像 final”更重要。

# 附录 B. 当前状态一句话版

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>最终一句话<br />
FullMine 已从 V1 的保守可运行基线，演进到 Vector V2 的 100 effective roads / 553 paths / raw lane Z / 8 repair provenance，再经过 CollisionLookup 真值修复、A1 route-end 修复、A2 steering-rate-aware speed profile、V3 +724px 与 V4 +3px exact physical patch，形成 frozen V4；随后又完成 Representative Coverage v1 与 Pure MCTS Representative Transfer 3/3。当前它是可恢复、可复现、可承载正式算法实验的 Research Baseline，但 production-authoritative drivability 仍必须依赖外部权威输入。</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

*--- 以下为 2026-08-14 同日最新增补：Representative Coverage / Pure MCTS / Neural readiness / 最终接管状态 ---*

# 24. P0 Disaster Recovery：V4 不再依赖当前 AutoDL 实例

## 24.1 为什么地图冻结之后还必须做灾备

Git tag 只能保证进入 Git 的源码与提交可恢复，不能自动带走 /root/autodl-tmp 中的大 bitmap、semantic、manifest、runtime evidence、scenario inputs 与验证脚本。FullMine V4 的关键地图资产恰好大量位于 autodl-tmp，因此“commit/tag 完成”不等于“整张研究地图可以脱离当前容器恢复”。

## 24.2 最终 DR 资产与结果

| **对象**          | **路径**                                                                  | **SHA256 / 结果**                                                |
|-------------------|---------------------------------------------------------------------------|------------------------------------------------------------------|
| Git bundle        | /root/autodl-tmp/MineSim-Dynamic_fullmine_vector_v4_final_20260814.bundle | d52abc76e5e0d903a5bbf5ee7e087fd1341b54ebb7aae3c51ad1316a1f91cb5f |
| 地图/证据 archive | /root/autodl-tmp/fullmine_vector_v4_final_dr_20260814.tar.gz              | 2d6c79af6301ccb59c57fa78693b7c81e10270f13491bb9903139c2c62a4dac0 |
| 独立恢复测试      | 新目录/独立 clone + 归档还原                                              | PASS；不依赖原工作目录才能读取 frozen commit/tag 与 V4 资产      |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>接管规则</strong></p>
<p>P0 Disaster Recovery 已 CLOSED；除非资产损坏/迁移，不要重复创建覆盖同名 bundle/archive。</p>
<p>恢复时先校验 SHA，再使用 bundle/tag 和 archive；不要把“能 git clone”误当成“地图数据已完整恢复”。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 25. FullMine V4 Representative Coverage v1：从“重点修复区”升级到“全矿多类别代表性验证”

## 25.1 为什么 V4 7/7 以后还要做 Representative Coverage

V4 targeted 7/7 是非常深的闭环验证，但它围绕 V2 新恢复 lane、road484、A/B/C/D/E 等高风险/高价值位置展开。它证明“这些难点已经被打通”，却不能自动代表整个矿区 west/central/east 与 road/intersection/loading/unloading/auxiliary 的不同区域。因此 V4 冻结后没有继续补 bitmap，而是把地图作为不可变基线，只做只读式 Representative Coverage。

这一步的研究意义是把“局部深验证”与“全矿代表性”分开：前者回答 difficult repairs 是否正确，后者回答同一 frozen map 在不同地理区域和不同功能类别上是否具备可用的 scenario/materialization/route/runtime 代表性。

## 25.2 候选生成：13 个不重复 coverage cell

| **类别**     | **west**       | **central**    | **east**       | **说明**                                               |
|--------------|----------------|----------------|----------------|--------------------------------------------------------|
| road         | candidate-0001 | candidate-0002 | candidate-0003 | 普通道路三地区均有候选                                 |
| intersection | candidate-0004 | candidate-0005 | candidate-0006 | 交叉区三地区均有候选                                   |
| loading      | candidate-0007 | candidate-0008 | candidate-0009 | 装载区三地区均有候选                                   |
| unloading    | —              | candidate-0010 | —              | 现有合同只获得 central；west/east 后续保持 unavailable |
| auxiliary    | candidate-0011 | candidate-0012 | candidate-0013 | 辅助区三地区候选齐全                                   |

Candidate manifest v3 的核心原则不是“随便抽 13 条”，而是：每个 cell 尽量只选一条、避免历史已反复验证的 route overlap、保证 predecessor 至少 10m、successor 至少 3m，使 start/goal 能合法 materialize。最终 candidate manifest SHA=0888016770a468ed927e594362707e8f456e945c129f1db0e2c1732020412bf7。

## 25.3 Route initialization：13/13 PASS

13 个代表场景逐场新 Python 进程做 Scenario/Map API/Planner route initialization，全部 RC=0、route_exact=True。原始 route-init summary SHA=6e93a22d0295f31c611c0c76be7d7795e1290a0965f04db8ec58f95d804fde47。这一步证明：全矿代表场景不是“表格里的候选”，而是真能被当前 MineSim route planner 初始化的 scenario。

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>为什么“一场景一个 Python 进程”被固定为工作流</strong></p>
<p>FullMine semantic/bitmap 大，单进程批量重用对象容易混入缓存、内存峰值与错误状态。</p>
<p>逐场进程可以单独记录 rc/log/RSS/exception，失败时只定位该场，不把前一场状态带入下一场。</p>
<p>这是 Representative Coverage、后续 Pure MCTS transfer 都沿用的稳定模式。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## 25.4 Static coverage final：9 validated / 4 limitations / 2 unavailable

| **类别**     | **west**    | **central**     | **east**    |
|--------------|-------------|-----------------|-------------|
| road         | PASS        | PASS            | PASS        |
| intersection | PASS        | PASS (recovery) | PASS        |
| loading      | PASS        | PASS (recovery) | LIMITATION  |
| unloading    | UNAVAILABLE | PASS            | UNAVAILABLE |
| auxiliary    | LIMITATION  | LIMITATION      | LIMITATION  |

最终 static gate 状态是 READY_WITH_DOCUMENTED_LIMITATIONS：9 个代表 cell 完成验证，4 个明确保留 limitation，2 个 unavailable。最重要的表述边界：这些 limitation/unavailable 是“frozen research bitmap + scenario/materialization contract 的验证边界”，不是在宣称真实矿区对应区域存在 production 缺陷。

static_coverage_final_manifest_v1.json SHA=a66383efd21ccffee292d6980609824c2d68a4f34fa3c0f72c76cfd03d46064d；最终 coverage summary SHA=a7a19dc99cbf4c22ce21ec9afa70b9ce05c006f9af2461602a7c642b17fe2ccd。

## 25.5 Representative IDM closed-loop：3/3 PASS

| **Case**       | **类别/区域**          | **长度** | **Route**                         | **结果** |
|----------------|------------------------|----------|-----------------------------------|----------|
| candidate-0010 | unloading / central    | 71.107m  | path-000017 -\> 000012 -\> 000018 | PASS     |
| candidate-0002 | road / central         | 176.455m | path-000394 -\> 000395 -\> 000397 | PASS     |
| recovery-0005  | intersection / central | 181.345m | path-000256 -\> 000248 -\> 000246 | PASS     |

三条路线选择的是经过 static gate 后的最短干净代表 case，用于把“route init”提升为“真实 closed-loop”。三场都实际到达目标并通过安全检查。最终 corrected IDM summary v2 SHA=5fec6dc56bc38209f85a1c33be8a6716616a841ade1057ee358ff4b603676013。之所以强调 v2，是因为 v1 aggregator 曾错误把实际 PASS 汇总成 PRECHECK failure；修的是汇总证据，不是仿真本身。

## 25.6 Coverage freeze

| **证据**                 | **值**                                                                                               |
|--------------------------|------------------------------------------------------------------------------------------------------|
| Final freeze JSON        | /root/autodl-tmp/fullmine_v4_representative_coverage_v1/representative_coverage_v1_final_freeze.json |
| Freeze SHA               | bab9e77446e9c3b5747bb2721d035ca726b482418559b5f2a1018fe5e0018c5e                                     |
| 状态                     | FROZEN_WITH_DOCUMENTED_LIMITATIONS                                                                   |
| Tag                      | fullmine-v4-representative-coverage-v1-20260814                                                      |
| Tag target               | 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e                                                             |
| frozen_v4_modified       | false                                                                                                |
| production_authoritative | false                                                                                                |

# 26. FullMine V4 Pure MCTS Representative Transfer v1：旧图算法正式迁移到新地图

## 26.1 为什么先做 Pure MCTS，而不是直接 Neural-MCTS

Dapai/Jiangtong/J117 上 Pure MCTS 已经是成熟基线。进入 FullMine 后，如果直接加入神经网络，就无法区分“新地图适配问题”与“网络/训练问题”。因此先使用 Representative Coverage 已验证的同三场场景做 Pure MCTS transfer：只有 Pure MCTS 在 frozen V4 上稳定通过，后续 Value/Policy 网络才有可信 baseline。

## 26.2 第一个 blocker：ScenarioOrganizer 不认识 FullMine

tracked \`planner_ab_benchmark.py\` 使用 ScenarioOrganizer.load；当前 organizer 通过 scenario_name 前缀只映射 jiangtong -\> jiangxi_jiangtong、dapai -\> guangdong_dapai，其他前缀直接报地图 location 错误。FullMine 的 downstream bitmap/semantic/vehicle loader 实际已经注册，所以问题不在地图，而在 benchmark 的入口组织器。

解决策略没有去修改 tracked ScenarioOrganizer，而是在 \`/root/autodl-tmp/fullmine_v4_mcts_representative_v1/fullmine_benchmark_adapter_v1.py\` 中做进程内 adapter：显式构造 ScenarioFileBaseInfo(location="geojson_full_mine_vector_v2_dev")，再复用 tracked benchmark 的 planner/simulation/安全检查主循环。这样不会为了一个实验入口把 frozen repo 行为改掉。Base adapter SHA=f51fae7cc866a6c6f9871ac076c2547d662f1f0ba24bd530525a9e71905265ba。

## 26.3 第二个“假失败”：1-step smoke 的 benchmark 后置断言

candidate-0010 的 1-step smoke 已经输出正确 location、MCTSPlanner、正确 route、ACCEL、0 collision、strict safety=True，但 process RC=1。根因不是 MCTS，而是 benchmark 末尾硬编码 \`assert steps \> 3\`；任何 max-steps=1 都必然 AssertionError。因此将 runtime contract 记为 PASS，把 RC1 解释为 KNOWN_MINIMUM_STEP_POSTCONDITION，随后跑 5-step smoke 得到干净 RC=0。

## 26.4 第三个“假失败”：只看 300-step 最终位置把已到达 goal 的轨迹误判失败

candidate-0010 完整 300-step run 中，route exact、安全检查均通过，但最终位置距 goal polygon 约 2.7468m、SIMULATION_RUNNING=True，于是最初 final-point acceptance 判 FAIL。进一步 goal-stop probe 发现 MCTS root 已经超过 internal goal_route_s，树在 depth=1 即 goal=True；真正问题是 EnvironmentSimulation 并不会因为进入 goal polygon 自动 stop，它只在 time controller 到期或内部 flag 被置 false 时结束。

随后按 formal targeted harness 的同一规则做历史审计：正式 goal contract 是 \`goal_polygon.covers(Point(current.rear_axle.x, current.rear_axle.y))\`。结果 candidate-0010 的 FIRST_INTERNAL_GOAL_STEP=83、FIRST_REAR_GOAL_STEP=83、FIRST_FORMAL_GOAL_STEP=83，完全对齐。因此旧的“300 步最终位置 FAIL”被正式 SUPERSEDED。Goal-history audit SHA=9db2c97b291d88c17681fbaf8ef60d3633c8a65c39854b948a8b75c9e1ca2030。

## 26.5 Goal-stop test adapter：只修 benchmark 终止语义，不改 MCTS/地图

剩余两场使用临时 \`fullmine_benchmark_goal_stop_adapter_v2.py\`：每次 \`is_simulation_running()\` 前检查 rear axle 是否被 scenario goal polygon covers；第一次进入就设置内部 simulation flag 为 false。该 adapter 是测试 harness 语义修正，不修改 MCTSPlanner、Reward/Search/Transition，也不修改 V4 bitmap。Adapter v2 SHA=54ee1e768d4bb7005ee10586e148282298c5557c39ed8f927a2076a32baa9493；acceptance script SHA=41c1083a8389c1d3b2f8b2b820ec9a1d8c7bbcc043935ecdd281d88b817fc60a。

## 26.6 三场最终结果：3/3 PASS

| **Case**       | **Route**           | **到达 formal goal** | **碰撞/边界**        | **结果** |
|----------------|---------------------|----------------------|----------------------|----------|
| candidate-0010 | 017 -\> 012 -\> 018 | step 83              | 0 / 0；strict safety | PASS     |
| candidate-0002 | 394 -\> 395 -\> 397 | step 182             | 0 / 0；strict safety | PASS     |
| recovery-0005  | 256 -\> 248 -\> 246 | step 186             | 0 / 0；strict safety | PASS     |

candidate-0002 acceptance SHA=8d66f68165d0f88772478b63eb1b8d7b6989ba771b861a9e5c7072f73322e92c；recovery-0005 acceptance SHA=117cb4359e4c2e97a8796bfc293adcb9f89db4d4542260eec8963cae93148316。Pure MCTS representative summary SHA=742d0716a00364a625e01b27c693134488211c8989e4996b072739c3a500d056。运行后 frozen bitmap/semantic SHA 均保持不变。

## 26.7 Pure MCTS freeze

| **证据**    | **值**                                                                                               |
|-------------|------------------------------------------------------------------------------------------------------|
| Freeze JSON | /root/autodl-tmp/fullmine_v4_mcts_representative_v1/pure_mcts_representative_transfer_freeze_v1.json |
| Freeze SHA  | 322e90d6995c410597d01925de6d77f1fd91ddb8c4c73a25c3e87446d37ac1fa                                     |
| Summary SHA | 742d0716a00364a625e01b27c693134488211c8989e4996b072739c3a500d056                                     |
| Tag         | fullmine-v4-pure-mcts-representative-transfer-v1-20260814                                            |
| Tag target  | 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e                                                             |
| 最终结论    | FullMine V4 Pure MCTS Representative Transfer v1 = COMPLETE / FROZEN                                 |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>重要解释：为什么三个 tag 都可能指向同一个 commit</strong></p>
<p>V4 map tag 冻结的是 tracked source + map runtime base。</p>
<p>Representative Coverage 与 Pure MCTS transfer 的新增证据主要位于 /root/autodl-tmp，且明确不修改 frozen V4 tracked map/source，因此它们可以作为“evidence milestone tag”指向同一 112d2bd commit。</p>
<p>真正区分后续阶段的是各自 freeze JSON/SHA 与外部 evidence 目录，而不是必须制造一个新的源码 commit。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 27. 2026-08-14 最新 Neural-MCTS readiness audit：只审计，不训练

## 27.1 当前源码里已经有什么

最新只读 inventory 表明：MCTS 专用目录已有 \`expert_data.py\` 与完整 search/reward/geometry/fleet test；项目通用 planning/training 下已有 PyTorch、LightningModuleWrapper、Raster/Vector/LaneGCN 等训练基础设施，但 MCTS 目录中没有现成的 dedicated ValueNetwork/PolicyNetwork/PolicyValueNetwork 实现。也就是说，Neural-MCTS 不是“已有网络只差跑一下”，而是仍需明确数据契约与网络角色。

## 27.2 Expert sample schema 已经准备得比较完整

| **字段组** | **当前包含**                                                                                    |
|------------|-------------------------------------------------------------------------------------------------|
| ego        | center(x,y,heading)、velocity、acceleration、tire steering、box length/width/height             |
| mcts_root  | route_s、speed、accel、lead distance/relative speed、target speed、goal_route_s、goal_remaining |
| expert     | action、action_index、acceleration                                                              |
| search     | iterations、seed、visits、q_values、immediate_rewards、predicted_clearance                      |
| obstacles  | 序列化 obstacle snapshots；当前三条 FullMine representative case 均为 0 obstacles               |

## 27.3 当前数据量只能称为“raw inventory”，不能直接叫训练集

当前 FullMine 决策日志扫描得到 TOTAL_FULLMINE_SAMPLES=674：candidate-0002 182、candidate-0010 full 300、candidate-0010 1-step smoke 1、5-step smoke 5、recovery-0005 186。这个 674 不能直接用于训练，因为包含 smoke 重复样本，而且 candidate-0010 full 在 step83 已正式到达 goal 后仍继续记录到 300。正确下一步应先建立 dataset builder：按 formal goal 截断、删除 smoke/重复、记录 scenario/source/freeze SHA，再做 train/validation/test split。

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>当前 Neural-MCTS 状态</strong></p>
<p>训练：NOT STARTED。</p>
<p>网络：MCTS 专用 Value/Policy 网络尚未建立。</p>
<p>已有基础：Pure MCTS expert schema、历史 Dapai/Jiangtong expert dataset、FullMine representative decision logs、通用 PyTorch/Lightning training infrastructure。</p>
<p>用户当前明确要求先暂停神经网络，优先把项目与地图成果整理清楚。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 28. 地图主线全流程总复盘：任何 AI 必须按这条链理解 V4

## 28.1 一张图的逻辑链

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>8类真实GeoJSON<br />
-&gt; WGS84 / UTM46N / MineSim local<br />
-&gt; FullMine V1 conservative structural baseline<br />
-&gt; source completeness audit<br />
-&gt; Vector V2 semantic: 100 roads / 553 paths / 8 repair provenance / raw lane Z<br />
-&gt; frozen/additive bitmap strategy<br />
-&gt; 15 target lanes + 7 depth-safe scenarios<br />
-&gt; CollisionLookup geometry + exact SAT truth<br />
-&gt; A1 route-end planner fix<br />
-&gt; A2 steering-rate-aware speed profile<br />
-&gt; V3 exact final A/B trajectory patch (+724px)<br />
-&gt; C/D/E current-planner rerun<br />
-&gt; V4 D exact patch (+3px)<br />
-&gt; targeted 7/7 + old Jiangtong regression<br />
-&gt; commit/tag + disaster recovery<br />
-&gt; Representative Coverage v1<br />
-&gt; Representative IDM 3/3<br />
-&gt; Representative Pure MCTS 3/3 + freeze</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## 28.2 各阶段“当时看到的症状”和“最后证明的根因”

| **阶段/症状**                       | **最初容易误判**           | **最终根因**                                                        | **最终解决**                                                       |
|-------------------------------------|----------------------------|---------------------------------------------------------------------|--------------------------------------------------------------------|
| V1 endpoint 126 errors              | lane/road 数据坏           | 共享 topo endpoint XY 非 bit-identical                              | 按 topo node canonical endpoint snapping                           |
| source coverage missing 49          | 源数据缺失                 | validator layer mapping 不完整                                      | 补 road/junction/load/unload/aux layer mapping                     |
| boundary parent 8 错挂              | boundary 数据不可靠        | 跨 category 只按 ID 查，ID 可重复                                   | 按 rgn_type + objectid 严格绑定                                    |
| V1 93 roads/540 paths               | 源数据只能做到这么多       | 保守排除 missing/self-intersection/mismatch road                    | V2 做 source audit + 8 provenance repairs -\> 100/553              |
| 大图 planner init 极慢              | CPU/GPU 不够               | polygon token lookup 重复线性扫描                                   | token2ind O(1)                                                     |
| 长 A/B route refline_smooth 缺失    | semantic 少路              | GlobalRoutePathPlanner BFS target_depth=5                           | 不改全局 planner；拆成 depth-safe 场景                             |
| C/D/E boundary collision            | bitmap 缺口                | 先有 CollisionLookup XG90G 前后悬反置+梯形；再有离散 false positive | 修几何 + exact SAT；之后才补真实 3px/3px                           |
| A1 goal 前 4.84m 停车               | goal polygon/地图错        | free-road route endpoint 被当 4.5m 虚拟前车                         | virtual endpoint length_rear=0.0                                   |
| A2 中途停车                         | endpoint 或 leading object | 高曲率段 steering-rate infeasible                                   | steering-rate-aware speed cap + backward braking envelope          |
| B2 fixed offset 推出 227px 缺口     | 需要补大片 mask            | 固定外推忽略 controller 后续纠偏                                    | 拒绝该 patch；用 actual shadow trajectory                          |
| V3 后 D step66 再失败               | 验证器又错                 | current planner 下真实 3px physical gap                             | D-only shadow + 全轨迹 exact scan -\> V4 +3px                      |
| 7/7 一度只有 5/7                    | V4 回归失败                | stale manifest 混用旧 C/D/E JSON                                    | 重新 current-planner 单场跑 + 绑定 SHA 世代                        |
| FullMine MCTS 启动失败              | MCTS 不支持新地图          | ScenarioOrganizer 入口仅识别 dapai/jiangtong                        | 临时 explicit ScenarioFileBaseInfo adapter，不改 tracked organizer |
| 1-step MCTS RC1                     | MCTS runtime failure       | benchmark assert steps \> 3                                         | 识别为后置门槛；5-step smoke 获取干净 RC0                          |
| candidate0010 300-step final goal外 | MCTS 到不了 goal           | simulation 到 goal 不自动停止，车已在 step83 到达后继续走           | formal rear-axle goal history audit；旧 final-point FAIL 作废      |

## 28.3 为什么这张新地图与 Dapai/Jiangtong 的价值不同

Dapai/Jiangtong 的优势是“原项目已经交付成品 semantic + bitmap”，因此 production 资产权威性高于 FullMine；FullMine 的优势是“从真实 GIS 到 MineSim Research Map 的 authoring / repair / validation / runtime / freeze 过程完全可追溯”。论文中应把这两种优势分开：旧图用于成熟 benchmark 对照，新图用于证明方法能从既有两图扩展到真实 GIS 派生的大型第三地图，同时展现地图构建与验证方法。

| **维度**          | **Dapai/Jiangtong**                              | **FullMine Vector V4**                                  |
|-------------------|--------------------------------------------------|---------------------------------------------------------|
| 资产形态          | 原项目成品 semantic + bitmap                     | 真实 GeoJSON 经本项目构建 semantic + research bitmap    |
| authoring rule    | 成品可用，但生成过程/production mask rule 不透明 | source/repair/patch/SHA/evidence chain 可追溯           |
| 算法基线          | IDM、Pure MCTS；Dapai 有多车冲突证据             | IDM representative 3/3；Pure MCTS representative 3/3    |
| production 权威性 | 高于 FullMine（原项目成品资产）                  | NOT PROVEN；缺 official drivability / exclusions / rule |
| 研究贡献          | 成熟对照 benchmark                               | 第三张真实 GIS 派生研究地图 + 完整工程验证链            |

# 29. 最新问题库增补：Representative Coverage 与 Pure MCTS 阶段

| **问题**                                | **判定/根因**                                                              | **解决办法**                                                           | **以后怎么做**                                                       |
|-----------------------------------------|----------------------------------------------------------------------------|------------------------------------------------------------------------|----------------------------------------------------------------------|
| Coverage 某些 cell 无法形成 PASS        | 可能是 materialization/route/bitmap 合同限制，不能直接叫 production defect | 保留 LIMITATION / UNAVAILABLE；用 recovery candidate 只替换可验证 cell | 所有 limitation 必须写清“research coverage boundary”，禁止生产缺陷化 |
| IDM smoke v1 汇总误判                   | aggregator bug，实际三场运行结果为 PASS                                    | 生成 corrected summary v2；冻结只引用 v2 SHA                           | 验收看场景事实字段，不只看上层汇总字符串                             |
| ScenarioOrganizer 不支持 FullMine 前缀  | 入口代码只识别 dapai/jiangtong                                             | 进程内 adapter 显式注入 location                                       | 实验适配优先外部 wrapper；避免污染 frozen repo                       |
| 1-step MCTS AssertionError              | benchmark 最后要求 steps\>3                                                | 5-step smoke；1-step只作为 runtime contract evidence                   | 先读 traceback；RC 非0不自动等于 planner failure                     |
| goal 后继续仿真导致 final-point FAIL    | EnvironmentSimulation 不按 goal polygon自动 stop                           | goal-history audit + goal-stop test adapter                            | 终点验收必须使用 formal goal contract/first hit，而不是只看最后一帧  |
| 终端粘贴 \`git status --short、\`       | 中文顿号被拼进 shell 参数                                                  | 命令块保持 ASCII；执行后看真正任务是否已启动                           | Terminal 乱码/尾巴错误先区分主任务与打印命令                         |
| 674 raw expert samples 容易被误当训练集 | 含 smoke 重复 + candidate0010 goal 后过采样                                | 未来 dataset builder 先 goal-truncate/dedupe                           | 训练集必须绑定 scenario/freeze/source SHA 与 split 规则              |

# 30. 用户最终工作流：为什么这套流程能让 AI 长期接管而不把云端做乱

## 30.1 五步闭环

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>1) OBSERVE 只读 Git / SHA / cgroup / source / log，先认当前真相<br />
2) PLAN 每次只定义一个 blocker 和一个下一步，不重做已冻结工作<br />
3) EXECUTE 短命令用户 terminal；复杂边界清晰任务可交 Codex；大产物放 autodl-tmp<br />
4) ACCEPT 看 route/goal/target/drivable/collision/exception/RC/SHA，不用“看起来能跑”代替验收<br />
5) FREEZE manifest + SHA + tag；必要时 DR bundle/archive；然后进入新 branch / 新 evidence dir</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## 30.2 Shell 不可违反的规则

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>cd /root/MineSim-Dynamic<br />
source /root/miniconda3/etc/profile.d/conda.sh 2&gt;/dev/null || true<br />
conda activate minesim<br />
export PYTHONPATH=/root/MineSim-Dynamic<br />
export CUDA_VISIBLE_DEVICES="" # CPU/static default<br />
<br />
# Interactive top level: no naked exit<br />
# Never: git clean -fd / git reset --hard / git add .</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## 30.3 资源与成本

低配实例的真实 cgroup 曾只有约 0.5 CPU / 2GiB；FullMine 大图 builder/cache 在该环境下出现 RC137/Killed。高资源实例实测约 15 vCPU / 80GiB，GPU 常常并不是 MineSim 地图/MCTS 本身的关键，开 4090D 的真实价值主要是得到 CPU/RAM 配额。因此先 CPU/static 前置、再按需开高资源，避免用昂贵实例做 grep/JSON/静态审计。

## 30.4 Codex 的最终定位

Codex 不作为“后台无限跑的第二个 AI”。适合：边界明确、代码量稍大、能用 PASS/FAIL 收口的单一任务。今日已有一次 bounded predicate/debug 验证，已看到 MISMATCHES_BEFORE=0、RANDOM_CASES_CHECKED=20、REAL_STATES_CHECKED=20 后即停止继续扩展，不重复启动第二个 Codex、不让它无边界重跑 full builder/benchmark。日常仍以聊天 AI 设计步骤 + 用户 AutoDL 执行 + 回贴真实结果为主。

# 31. 2026-08-14 最新云端接管快照与下一步边界

| **项目**       | **最新已知状态**                                                       |
|----------------|------------------------------------------------------------------------|
| Repository     | /root/MineSim-Dynamic                                                  |
| Conda / Python | minesim / Python 3.9.25                                                |
| 当前工作分支   | fullmine-v4-mcts-representative-dev                                    |
| HEAD           | 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e                               |
| V4 map tag     | fullmine-vector-v4-runtime-freeze-20260814                             |
| Coverage tag   | fullmine-v4-representative-coverage-v1-20260814                        |
| Pure MCTS tag  | fullmine-v4-pure-mcts-representative-transfer-v1-20260814              |
| 工作区         | 仅历史 untracked \`?? ^C\`；不要清                                     |
| 地图           | Research/benchmark READY + FROZEN；production-authoritative NOT PROVEN |
| Coverage       | FROZEN_WITH_DOCUMENTED_LIMITATIONS                                     |
| Pure MCTS      | Representative Transfer 3/3 PASS + FROZEN                              |
| Neural-MCTS    | 仅 readiness audit；训练 NOT STARTED；当前暂停                         |

## 31.1 如果下一位 AI 继续“地图”

> • 不要修改 V4。只有拿到 official production mask / drivable surface / internal restricted polygons / authoring rule / 权威车型信息时，才新建 V5 或 production-candidate。
>
> • 如果只是为了“更全”，不要再围绕已通过 A-E 补像素。当前 Representative Coverage 已完成；真正的下一层地图价值是 authoritative truth 或明确需求下的 exhaustive audit。
>
> • NTE200 selector 修复必须单独 bug branch；它是代码技术债，不是 FullMine 地图的一部分。

## 31.2 如果下一位 AI 继续“算法”

> • Pure MCTS representative baseline 已冻结，不要继续调参把 baseline 做漂。
>
> • FullMine Fleet/Multi-MCTS 可以成为下一条非神经算法路线：从已验证 intersection 场景构造双车冲突，不修改 frozen map。
>
> • Neural-MCTS 若恢复，第一步不是开 GPU 训练，而是先做 dataset contract：formal-goal 截断、去 smoke/重复、数据 split、feature/label 定义、baseline metrics。

## 31.3 任何 AI 接手后的第一轮，只做以下只读核验

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>cd /root/MineSim-Dynamic<br />
source /root/miniconda3/etc/profile.d/conda.sh 2&gt;/dev/null || true<br />
conda activate minesim<br />
export PYTHONPATH=/root/MineSim-Dynamic<br />
export CUDA_VISIBLE_DEVICES=""<br />
<br />
git branch --show-current<br />
git rev-parse HEAD<br />
git status --short<br />
git show --no-patch --decorate fullmine-vector-v4-runtime-freeze-20260814<br />
git show --no-patch --decorate fullmine-v4-representative-coverage-v1-20260814<br />
git show --no-patch --decorate fullmine-v4-pure-mcts-representative-transfer-v1-20260814<br />
cat /sys/fs/cgroup/cpu.max<br />
cat /sys/fs/cgroup/memory.max</th>
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
<th><p><strong>只有这一步读完后才能决定下一步</strong></p>
<p>如果 HEAD/tag/SHA 与本手册不同：先解释后续工作造成的变化，不要 reset。</p>
<p>如果关键 frozen asset SHA 不同：先调查谁改了、为什么改；不要直接用备份覆盖。</p>
<p>如果只是 `?? ^C`：保持不动，它不在 commit/tag。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 附录 C. 2026-08-14 最新关键证据 SHA/路径速查

| **证据**                | **路径 / 标识**                                                                                                            | **SHA / 状态**                                                   |
|-------------------------|----------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------|
| V4 bitmap               | /root/autodl-tmp/fullmine_vector_v4_d_current_planner_patch_candidate/bitmap/geojson_full_mine_vector_v2_dev_only_mask.png | 51abcd5a86e5c510204a5dacc873691506d721f98982ab7f98585d4e0f7efdd0 |
| V4 semantic             | runtime semantic symlink -\> Vector V2 semantic                                                                            | b85a3d8b28f2252ecb5bda179d514573f6333079def838cd048566f556d95cd0 |
| Targeted harness        | /root/autodl-tmp/fullmine_vector_v2_targeted_runtime/targeted_closed_loop_runtime.py                                       | 59a71806a95c580643f018e1ef47b005aa95ae69420ef3238536b311913939f3 |
| CollisionLookup         | devkit/sim_engine/environment_manager/collision_lookup.py                                                                  | 10c1d1339e742ca893fedb4aa51402addfba82e16e08f68339ea35d35ba3043b |
| AbstractIDMPlanner      | devkit/sim_engine/planning/planner/abstract_idm_planner.py                                                                 | 541ec74985d06322656e66c48abb382030d679171341408575d936e0a069e75e |
| Coverage final static   | .../static_coverage_final_manifest_v1.json                                                                                 | a66383efd21ccffee292d6980609824c2d68a4f34fa3c0f72c76cfd03d46064d |
| Coverage IDM summary v2 | .../idm_closed_loop_smoke_v1/idm_closed_loop_smoke_summary_v2.json                                                         | 5fec6dc56bc38209f85a1c33be8a6716616a841ade1057ee358ff4b603676013 |
| Coverage freeze         | .../representative_coverage_v1_final_freeze.json                                                                           | bab9e77446e9c3b5747bb2721d035ca726b482418559b5f2a1018fe5e0018c5e |
| Pure MCTS summary       | .../pure_mcts_representative_transfer_summary_v1.json                                                                      | 742d0716a00364a625e01b27c693134488211c8989e4996b072739c3a500d056 |
| Pure MCTS freeze        | .../pure_mcts_representative_transfer_freeze_v1.json                                                                       | 322e90d6995c410597d01925de6d77f1fd91ddb8c4c73a25c3e87446d37ac1fa |
| DR Git bundle           | /root/autodl-tmp/MineSim-Dynamic_fullmine_vector_v4_final_20260814.bundle                                                  | d52abc76e5e0d903a5bbf5ee7e087fd1341b54ebb7aae3c51ad1316a1f91cb5f |
| DR archive              | /root/autodl-tmp/fullmine_vector_v4_final_dr_20260814.tar.gz                                                               | 2d6c79af6301ccb59c57fa78693b7c81e10270f13491bb9903139c2c62a4dac0 |

# 附录 D. 接手者自检（最新 25 问）

1\. 为什么 Vector V4 的 semantic identity 仍叫 geojson_full_mine_vector_v2_dev？

2\. V1 93 roads/540 paths 到 V2 100/553 的 7 roads/13 paths 是怎么恢复的？8 repair provenance 为什么必须和 source 分开？

3\. 为什么 Dapai/Jiangtong polygon 内并非 whole-polygon drivable，FullMine 也不能把 polygon 全白？

4\. 为什么不同 topo ID 即使 XY 相同也不能 merge？

5\. 为什么 lane6713 Z seam 保留 raw QA，而不是自动平滑？

6\. 为什么 FullMine 大图需要 token2ind O(1)？

7\. 为什么 BFS target_depth=5 导致长 A/B route 被拆分，而不是去改 global planner？

8\. CollisionLookup 的 XG90G 前后悬反置/梯形具体怎么导致假边界？

9\. 为什么 exact SAT 过滤后 C/D 仍各需要少量真实 pixels？

10\. 为什么 A1 的 4.84m 提前停车可以由 4.5m virtual lead + min_gap + rear-to-center - goal offset 推出来？

11\. A2 为什么最终是 steering-rate infeasibility，而不是 route endpoint/leading object？

12\. 为什么 B2 fixed-offset 227px 扫描被拒绝？

13\. V3 +724px 和 V4 +3px 各自基于什么 trajectory truth？

14\. 为什么 A/B 可以从 v3 strict 继承到 additive v4，而 C/D/E 要 direct v4？

15\. 为什么 stale 5/7 manifest 必须作废？

16\. 为什么 disaster recovery 不能只靠 Git tag？

17\. Representative Coverage v1 的 9 validated / 4 limitation / 2 unavailable 各代表什么，为什么不是 production defect？

18\. 为什么 Representative IDM 只选三条最短干净 case，而不是把 13 条全部重跑？

19\. 为什么 ScenarioOrganizer 的 FullMine blocker 用 adapter 解决而不是改 tracked organizer？

20\. 为什么 1-step MCTS RC1 不是 MCTS 失败？

21\. 为什么 candidate-0010 的 300-step final-point FAIL 被 step83 formal goal history PASS 推翻？

22\. 为什么 goal-stop adapter 是 benchmark harness 修正，不是 MCTS 算法修改？

23\. Pure MCTS 3/3 freeze 为什么可以和 V4 map tag 指向同一个 commit？

24\. 为什么当前 674 raw expert samples 不能直接训练 Neural-MCTS？

25\. 下一位 AI 为什么看到 \`?? ^C\`、旧 backup、旧 manifest 都不能擅自 clean/reset/复用？

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>最终当前状态</strong></p>
<p>FullMine Vector V4 Research Map：COMPLETE + FROZEN。</p>
<p>Representative Coverage v1：COMPLETE + FROZEN WITH DOCUMENTED LIMITATIONS。</p>
<p>Pure MCTS Representative Transfer v1：3/3 PASS + FROZEN。</p>
<p>Production-authoritative drivability：NOT PROVEN。</p>
<p>Neural-MCTS：只完成 readiness audit，训练未开始，当前按用户要求暂停。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

*--- 文档结束 / Evidence cutoff: 2026-08-14 current conversation ---*

**FullMine V4 跨场景 Fleet-MCTS benchmark：候选筛选与 static readiness**

说明：以下为 2026-08-15 新增内容。前文保持原文和 2026-08-14 的证据口径不变，本补充只记录今天新增完成、实际验证或明确停止的工作。

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>更新后的阶段结论</strong></p>
<p>截至 2026-08-15，FullMine V4 的跨场景 Fleet-MCTS 候选已从原始 [C09, C11, C06] 按预先登记的 backup 顺序收敛为 [C04, C11, C06]。最终三场景 A/B 共 6 条路线均通过 actual-planner refline、XG90G physical footprint 和 CollisionLookup 的静态门控；static close 时 cross-scene MCTS result count 仍为 0。最终集合的 real-loader、NO-MCTS causal-conflict 和 Fleet-MCTS 动态实验尚未开始，因此当前最准确的表述是“FullMine 跨场景 benchmark 的 static readiness 已闭合”，不能写成“FullMine Fleet-MCTS benchmark 已完成”。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

**1. 今天为什么先做场景门控，而不是直接跑 MCTS**

昨天的工作已经证明 FullMine V4 可以承载单车 Pure MCTS，也完成了 Polygon21 双车 Fleet-MCTS 的 constructed benchmark。今天继续往前时，重点不再是“搜索器能不能跑”，而是把 FullMine 上用于跨场景迁移的实验场景先筛干净。原因很直接：如果受控车辆沿冻结 V4 道路本身就不能以 XG90G 真实 footprint 通过，后面的 NO-MCTS 或 MCTS 结果都没有解释价值。

因此今天采用的顺序是：先用真实几何构造同步冲突，再做 Scenario materialization，随后对 A、B 两条路线分别执行 actual planner + frozen bitmap 的 static drivability gate。只有 A/B 都通过，场景才允许进入 real-loader、NO-MCTS 和 Fleet-MCTS。这个顺序也用于避免“先看 MCTS 成绩，再挑容易成功的场景”。

**2. 候选集合如何从 C09/C11/C06 收敛到 C04/C11/C06**

第二批跨场景实验最初预先登记的 primary 为 \[C09, C11, C06\]，backup 顺序为 \[C13, C04\]。C11 和 C06 的 A/B static gate 均直接通过；变化主要发生在 C09、C13 两个候选上。两次替换都发生在任何 cross-scene MCTS 结果产生之前，并分别留下 protocol amendment 和失败证据。

| **候选** | **预先角色** | **当天实测结果**                                                                                                                                                                                         | **处理**     |
|----------|--------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------|
| C09      | Primary      | 物理冲突构造通过；B 的 standalone planner 初始化存在局部限制。后续用冻结 route 做 physical fallback，并回放 authored B 状态，确认坏区跨越冲突区：连续扫描 28 个 bad poses，authored B 14 个 bad frames。 | 淘汰         |
| C11      | Primary      | A/B actual-planner static 均通过；route exact，physical drivability=True，bad pose=0，CollisionLookup=True。                                                                                             | 保留         |
| C06      | Primary      | A/B actual-planner static 均通过；route exact，physical drivability=True，bad pose=0，CollisionLookup=True。                                                                                             | 保留         |
| C13      | Backup 1     | Scenario materialization 通过；A static 通过。B 修正了“expected route 被截短”的 harness 问题后真正进入 direct-planner bitmap scan，结果 48 个 bad poses，CollisionLookup=False。                         | 淘汰         |
| C04      | Backup 2     | 按第二份 protocol amendment 递补。Scenario/manifest/bundle 生成通过；A/B static 均 direct planner PASS，未使用 route-contract retry，bad pose=0。                                                        | 纳入最终集合 |

这里需要特别区分两类失败。C09 最初的 standalone planner 异常本身不能说明道路不可行驶，所以后续又做了独立 physical fallback 和 authored-state 回放；最终是物理证据决定淘汰。C13-B 则在 route expectation 修正后已经拿到真实 planner refline，并完成 65 m bitmap 扫描，48 个 bad poses 属于直接 static gate 失败。两者都不是因为 MCTS 表现不好而被替换。

**3. 最终 static readiness：三场景、六条路线全部闭合**

最终 intended set 为 \[C04, C11, C06\]。三场景的同步 approach 分别为 70 m、80 m 和 100 m；速度仍为 4.5 m/s，StartTime、route、车辆几何和冲突点均未为了通过门控而调整。static gate 只检查从各自起点到 conflict+15 m 的区间，判定以 XG90G footprint 与 frozen V4 bitmap 的精确相交为主，CollisionLookup 作为第二诊断。

<table>
<colgroup>
<col style="width: 7%" />
<col style="width: 27%" />
<col style="width: 12%" />
<col style="width: 42%" />
<col style="width: 9%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>场景</strong></th>
<th><strong>benchmark full route</strong></th>
<th><strong>同步 approach</strong></th>
<th><strong>static gate（start→conflict+15 m）</strong></th>
<th><strong>结论</strong></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>C04</td>
<td>A: 395→397→398<br />
B: 402→406→407</td>
<td>70 m</td>
<td>A: 85.000 m / 427 samples / 0 bad<br />
B: 84.997 m / 426 samples / 0 bad</td>
<td>PASS</td>
</tr>
<tr class="even">
<td>C11</td>
<td>A: 246→249→242<br />
B: 243→263→265</td>
<td>80 m</td>
<td>A: 94.9995 m / 476 samples / 0 bad<br />
B: 94.9981 m / 476 samples / 0 bad</td>
<td>PASS</td>
</tr>
<tr class="odd">
<td>C06</td>
<td>A: 355→365→009<br />
B: 008→368→070</td>
<td>100 m</td>
<td>A: 114.9997 m / 576 samples / 0 bad<br />
B: 114.9997 m / 576 samples / 0 bad</td>
<td>PASS</td>
</tr>
</tbody>
</table>

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>最终 static readiness 记录</strong></p>
<p>final_intended_source_indices=[4,11,6]；direct actual-planner static PASS=6/6；physical drivability PASS=6/6；all bad pose count zero=True；all CollisionLookup pass=True；MCTS result count at static close=0。最终报告：cross_scene_static_readiness_final_v1.json，SHA256=828b1f2282a7cca396577be0aab2af97231445fab1ad202dcadd6acf88c48edc。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

**4. 为什么这套场景筛选经得起查验**

今天的筛选过程没有使用 cross-scene MCTS 的性能结果作为选择依据。C09 被淘汰后先形成 protocol amendment v1，再启用 C13；C13 static 失败后又形成 protocol amendment v2，再启用 C04。最终 static readiness 关闭时，cross-scene MCTS result count 仍为 0。也就是说，最终集合 \[C04, C11, C06\] 是在看任何跨场景 MCTS 成绩之前确定的。

同时，失败候选没有删除。C09 的 planner limitation、physical fallback、authored B bad frames，以及 C13-B 的 direct-planner 48 bad poses 都作为负证据保留。整个过程中没有修改 V4 bitmap、planner 源码、候选 route、approach、速度或 StartTime 去“救”某个场景。C04 是最后一个预先登记的 backup；如果它也失败，就必须重新定义场景选择协议，而不能继续从剩余候选中顺延。

这套结论仍然只适用于冻结的 FullMine V4 Research Map。它说明最终三组 constructed cross-scene benchmark 在当前研究地图上通过了静态可行驶性前置门控，不等同于矿方 production-certified drivability。前文关于 production truth gap 的边界保持不变。

**5. 当前真正停在哪里**

static readiness 完成后，已经把 real-loader、NO-MCTS causal-conflict 和 Fleet-MCTS runner 参数化到最终集合 \[C04, C11, C06\]，并完成 py_compile。运行前又做了一次 provenance 审计，发现 v2 runner 尚未把 protocol amendment v2 和 final static readiness 作为运行时 SHA gate；因此没有直接放行动态实验。随后尝试派生 v3 时，因为目录中已经存在同名 v3 文件，按“不覆盖未知/既有证据”的规则安全停止。

因此截至本次补充截止，最终集合的 real-loader、NO-MCTS 和 Fleet-MCTS 都还没有正式执行。这不是算法运行失败，而是执行入口的证据链还需整理干净。下一步应保留现有 v3 文件作为中断证据，从已验证 v2 重新派生一套干净 runner，再按 real-loader → NO-MCTS → Fleet-MCTS seed0 的顺序运行。只有 seed0 三场全部完成后，才考虑继续做 seeds 1–4 的跨场景随机稳健性。

| **内容**                            | **当前状态** | **截至 2026-08-15 的准确表述**                                               |
|-------------------------------------|--------------|------------------------------------------------------------------------------|
| 最终 cross-scene 场景集合           | 完成         | \[C04, C11, C06\]；由预声明 primary/backup 规则和 static gate 确定           |
| 最终 static readiness               | 完成         | 6/6 direct actual-planner static PASS；0 bad poses；6/6 CollisionLookup PASS |
| C09 / C13 负证据                    | 保留         | 均在任何 cross-scene MCTS 结果出现之前被 static validity gate 排除           |
| Real-loader（最终集合）             | 未运行       | runner 已参数化/编译；正式执行前仍需补齐 protocol/readiness provenance gate  |
| NO-MCTS causal conflict（最终集合） | 未运行       | 等待 real-loader 通过后执行                                                  |
| Fleet-MCTS cross-scene（最终集合）  | 未运行       | 等待 static + loader + NO-MCTS 前置证据闭合后，先跑 seed0                    |
| Neural-MCTS                         | 未训练       | 仍按原计划后置，不在当前阶段启动                                             |

**补充附录：2026-08-15 新增证据锚点**

下表仅列今天新增或今天形成关键作用的证据。路径均位于 /root/autodl-tmp/fullmine_v4_fleet_cross_scene_v1，除特别说明外不属于正式仓库源码修改。

<table>
<colgroup>
<col style="width: 24%" />
<col style="width: 75%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>证据</strong></th>
<th><strong>锚点</strong></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>C09 failure localization</td>
<td>static_drivability_v1/cross-scene-c09-B_failure_localization_v2.json<br />
SHA 90615f838631f65975bfb4f5e87ca7f92b4a35fce65cbf0d1c886f3fe6db29b4</td>
</tr>
<tr class="even">
<td>Protocol amendment v1</td>
<td>cross_scene_protocol_amendment_v1.json<br />
SHA 8a825a8a2b9dd999b851e7dc97c50ed1360f7a2516b90ffd2b06875e98b49656</td>
</tr>
<tr class="odd">
<td>C13-B direct static failure</td>
<td>c13_static_prep_v2/cross-scene-c13-B_static_result_v2.json<br />
SHA 2174540a4334e75da08137b060bd6ab369739ed25f3b1ed00356cb3ec7bbe5d5</td>
</tr>
<tr class="even">
<td>Protocol amendment v2</td>
<td>cross_scene_protocol_amendment_v2.json<br />
SHA 27d76bce3b52706eb738c3da695325ab2fb20d3350ab2aadb4e15b30740ab42f</td>
</tr>
<tr class="odd">
<td>C04 Scenario</td>
<td>scenarios_c04_augmentation_v1/Scenario-fullmine-v4-cross-scene-c04-dual-aligned-v1.json<br />
SHA a207a7fc6a191b880460fdefb3e03d0a4592603f8ef6a13d0c7de530d243e0ca</td>
</tr>
<tr class="even">
<td>C04 manifest</td>
<td>scenarios_c04_augmentation_v1/cross_scene_c04_scenario_manifest_v1.json<br />
SHA 0b1d836e1b8d44c93948d850dacfbb086c24471b004b78025f4bd5c9f17a149c</td>
</tr>
<tr class="odd">
<td>C04-A static PASS</td>
<td>c04_static_prep_v1/cross-scene-c04-A_static_result_v1.json<br />
SHA 654f263ac3b262ac046f14c70b8424807b115a1d469526cbfe0cbba624d6eed4</td>
</tr>
<tr class="even">
<td>C04-B static PASS</td>
<td>c04_static_prep_v1/cross-scene-c04-B_static_result_v1.json<br />
SHA d6187a5099440d08eea16e29101c10162bff505f9dbf1b253c15e24888fa2aee</td>
</tr>
<tr class="odd">
<td>C11 A/B static PASS</td>
<td>A SHA 765a31f5cf6b7c08f000660b1761733930c48c16c72c0d52ebf66fe3e7473ff2<br />
B SHA 011a10cf714c950f5aee37713747a5b7cb5b589436e14d87cd8d2d47c01c4d34</td>
</tr>
<tr class="even">
<td>C06 A/B static PASS</td>
<td>A SHA 4d91267ec58fd101642eecea22f751b0ed3a50163f663c1adb6c272b28bb85f2<br />
B SHA dac442face05c4016fda3c4d4945891d7eecdca1980f0f70baab26e279ff69b1</td>
</tr>
<tr class="odd">
<td>Final static readiness</td>
<td>cross_scene_static_readiness_final_v1.json<br />
SHA 828b1f2282a7cca396577be0aab2af97231445fab1ad202dcadd6acf88c48edc</td>
</tr>
<tr class="even">
<td>Runtime runner v2（暂不执行）</td>
<td>loader SHA bdae2b0dfbcf2bcd19d9508eb3446814010dee788c5a832fe3be4aaa3c8a8ac8<br />
NO-MCTS SHA 36d2a706ad622ebb5ddbf0806a611b4fb161386be3897397add0abb63637037d<br />
Fleet-MCTS SHA 00ab3c26bf42be09a3c4b6d0ec7f952bde3f22cfaead30bf5d61f67927e51f3b；均已编译，但 provenance gate 未闭合，未运行</td>
</tr>
</tbody>
</table>

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>本次补充的汇报口径</strong></p>
<p>可以写：FullMine V4 跨场景 Fleet-MCTS benchmark 的候选筛选与静态有效性验证已经完成，最终集合为 C04/C11/C06，三场景六条路线 static 6/6 PASS。暂时不能写：FullMine 跨场景 Fleet-MCTS 已完成或已证明跨场景协同有效，因为最终集合的 real-loader、NO-MCTS 和 Fleet-MCTS 动态实验尚未正式执行。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>
