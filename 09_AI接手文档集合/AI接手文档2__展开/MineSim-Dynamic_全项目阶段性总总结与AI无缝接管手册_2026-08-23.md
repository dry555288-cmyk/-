**MineSim-Dynamic**

**全项目阶段性总总结与 AI 无缝接管手册**

Evidence cutoff: 2026-08-23（截至 technical retry \#1 高资源执行前的 preauth-binding KeyError）

主线：MineSim 复现 → 蒙特卡洛/MCTS 接入 → 单车跑通 → 双车冲突场景构建 → FullMine 新地图接入 → Fleet-MCTS 双车联合规划与多种子验证 → 原生 MineSim 可视化与汇报材料 → 云端文件安全整理 → 后续神经网络接入

**用途：任何新的 AI / 工程人员无需重新扫描全项目、无需重复实验，即可从当前冻结节点安全继续。**

# 0. 文档定位、证据等级与口径

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>文档定位</strong></p>
<p>本手册是 2026-08-21 版交接手册的证据更新版，加入 2026-08-23 的 Value V2 / C13 独立验证、replacement candidate、C03 physical/static/NO-MCTS qualification 全链以及当前 technical retry #1 的真实停点。所有新结论以当前终端输出、冻结 JSON/lock/SHA、源码合同和已上传日志为准。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

| **证据等级** | **含义**                                             | **使用规则**                                               |
|--------------|------------------------------------------------------|------------------------------------------------------------|
| V-LIVE       | 当前 AutoDL 终端、Git、源码、文件、SHA、实际运行输出 | 最高优先级；当前 turn 的终端结果可覆盖旧 Word 的“下一步”。 |
| V-FROZEN     | result / manifest / lock / bundle / SHA / tag        | 长期锚点；默认不重跑、不覆盖。                             |
| V-DOC        | 正式 Word、整理说明、历史手册                        | 补足发展过程；若与更晚 live evidence 冲突则降级。          |
| V-DESIGN     | 未来方案、论文适配、拟议网络/算法                    | 不能写成已完成。                                           |
| HOLD         | 来源不足、外部权威缺失、技术门未过或禁止擅动         | 必须显式写“未验证/HOLD”，不得常识补齐。                    |

> • AI/Codex 归属边界：现有云端脚本、终端日志、ZIP/JSON/lock 能证明“云端实际完成了什么”，但并非每个文件都有独立 Codex 作者签名。本手册不虚构逐文件作者归属；只记录可核验执行事实。
>
> • 失败分类必须区分 harness / wrapper / import / path / runtime contract / scientific fail。文件存在不等于 PASS；必须解析 RC、JSON 字段和 gate。
>
> • FullMine V4 是 Research/DEV 冻结 baseline；production-authoritative drivability 仍未被官方规则证明。terrain/Z/slope 等外部权威不足事项继续 HOLD。

# 1. 当前项目 30 秒状态

| **主线阶段**       | **状态**                     | **当前最准确结论**                                                                                                                                                                                                         |
|--------------------|------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| MineSim 复现       | PASS / FROZEN                | Dapai/Jiangtong IDM、replay 与 closed-loop baseline 已建立，历史 commit/tag 可回归。                                                                                                                                       |
| 蒙特卡洛/MCTS 接入 | PASS / FROZEN                | Pure MCTS 已进入真实 MineSim online closed-loop；448 strict historical expert。                                                                                                                                            |
| 单车跑通           | PASS / FROZEN                | J117 Phase4C 423-step full route；FullMine Representative Pure MCTS 3/3。                                                                                                                                                  |
| 双车冲突场景构建   | PASS / FROZEN                | J117、Polygon21 和 cross-scene 使用 NO-MCTS 物理 footprint overlap 建立 causal conflict benchmark。                                                                                                                        |
| FullMine 新地图    | PASS / FROZEN                | Vector V2 semantic + V4 bitmap/runtime/planner；targeted 7/7 + old-map regression。                                                                                                                                        |
| Fleet-MCTS         | PASS + NEGATIVE RESULT       | Polygon21 budget64/depth8 5/5；C04/C06 成功；C11 安全但 deadlock/progress FAIL，必须保留。                                                                                                                                 |
| 原生可视化         | PASS / FROZEN                | Native Video V2 final；Map Showcase V2 stable；V3 incomplete/HOLD。                                                                                                                                                        |
| 云端整理           | PASS / COMPLETE              | Phase2A–2K；约 530→121；423 move/isolate；科研文件删除 0；restore gate PASS。                                                                                                                                              |
| 神经网络接入       | DEVELOPMENT / NOT INTEGRATED | V1 LOSO science FAIL；Value V2 final-dev model 已冻结；C13 one-time eval 因 metric-binding technical failure 未得到科学指标；replacement scene 当前推进到 C03 NO-MCTS causal qualification，MCTS_VALUE_INTEGRATION=False。 |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>当前真正停点（2026-08-23）</strong></p>
<p>C03 已完成 physical conflict PASS 与 A/B static bitmap direct PASS。第一次 C03 NO-MCTS causal attempt 在 0 iteration 因派生 runner 残留 50m runtime identity check 技术失败，已冻结；随后只修两处 identity check 并冻结 manual technical retry #1。最新一次高资源执行在真正启动 retry #1 前的 PREAUTH BINDING 处出现 KeyError: 'old_attempt_artifacts'，因此 retry #1 尚未开始、未写 START、未产生 retry1 result/log，也未消耗技术重试资格。当前 blocker 是执行 wrapper 的 schema key 不一致，不是 C03 科学失败。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 2. 真实发展时间线

| **日期**          | **阶段**                              | **可复核结果 / 意义**                                                                                                                                                                     |
|-------------------|---------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 2026-07-26        | 云端 baseline / 安全操作规范          | 建立 AutoDL 安全交互、Git 恢复、文件优先和“先读接口再改代码”的纪律。                                                                                                                      |
| 2026-07-30～08-02 | Pure MCTS closed-loop                 | MCTSPlanner → state/action/search/reward → trajectory adapter → Controller/KBM；commit 94693dc；448 strict expert。                                                                       |
| 2026-08-03～07    | 五 Planner / budget / interface audit | MCTS、IDM、Frenet、Adapted Maneuver、Simple；形成算法能力边界和 adapter 故障分域。                                                                                                        |
| 2026-08-08～10    | 双受控 + J117                         | Jiangtong conflict 负筛选；J117 单车 423 steps；双车 NO-MCTS conflict + Pure MCTS 5-seed。                                                                                                |
| 2026-08-11～14    | FullMine V1 → Vector V4               | O(1) token lookup、Vector V2 semantic、bitmap/runtime/planner 修复；V4 freeze HEAD 112d2bd。                                                                                              |
| 2026-08-14        | Representative Pure MCTS              | 跨代表区域 3/3 PASS 并冻结。                                                                                                                                                              |
| 2026-08-15        | Polygon21 Fleet-MCTS                  | NO-MCTS 真实物理重叠；Fleet budget64/depth8 5/5；freeze v2。                                                                                                                              |
| 2026-08-16        | Native Video + safe cleanup           | Native MineSim Video V2 final；Phase2A–2K safe cleanup；Map Showcase V3 SIGKILL 未收口。                                                                                                  |
| 2026-08-17～18    | Cross-scene + Paper1 safety           | C04/C11/C06 动态收口；C11 安全死锁；SafetyRisk V0 observational freeze；V2R 推进。                                                                                                        |
| 2026-08-21        | Safety/data → current-semantic NN     | V2R/zone/dynamic V2V/shadow/dataset/collector 全链完成；C04 smoke；C11/C06 recollection；three-scene LOSO science FAIL；V1 failure diagnostic。                                           |
| 2026-08-22～23    | Value V2 / independent validation     | Value V2 final-dev model冻结；C13独立数据115 roots/1840 rows；one-time eval forward 1 次但 metrics binding technical failure，retry 永久禁止；blind replacement selection 固化。          |
| 2026-08-23        | C10/C14/C03 replacement qualification | C10、C14 static 淘汰；C03 physical PASS、static A/B 451 samples 各 0 bad；进入 NO-MCTS causal gate。                                                                                      |
| 2026-08-23 当前   | C03 causal technical qualification    | attempt1 0 iteration technical failure（stale 50m identity check）；manual retry \#1 correction/preauth 已冻结；retry1 高资源 wrapper 在 PREAUTH BINDING KeyError 前停止，retry1 未执行。 |

# 3. 运行架构、核心调用链与依赖边界

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>系统边界</strong></p>
<p>项目没有重写完整 MineSim。MCTS/Fleet-MCTS 主要替换/扩展 Planner 决策层；真实未来轨迹仍由 TwoStageController 与 Kinematic Bicycle Model 执行。Scenario、Map、Observation、Controller、Vehicle、History/Metrics 都是科学链的一部分，不能绕过。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

run_simulation.py  
→ SimulationsRunner.\_initialize()  
→ EnvironmentSimulation.initialize()  
→ Scenario / Map loader  
→ Planner.initialize()  
→ 每帧 Planner.compute_planner_trajectory()  
→ TwoStageController.update_state()  
→ LQR / iLQR trajectory tracking  
→ KinematicBicycleModel.propagate_state()  
→ Agent Update Policy / Observation  
→ SimulationHistory / metrics / log  
→ 下一帧

| **项目**                                      | **当前事实 / 处理规则**                                               |
|-----------------------------------------------|-----------------------------------------------------------------------|
| 正式 repo                                     | /root/MineSim-Dynamic                                                 |
| 当前 frozen HEAD                              | 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e                              |
| Frozen tag                                    | fullmine-vector-v4-runtime-freeze-20260814                            |
| 主要结果/大文件 root                          | /root/autodl-tmp                                                      |
| 当前 cross-scene / neural 工作区              | /root/autodl-tmp/fullmine_v4_fleet_cross_scene_v1                     |
| FullMine runtime                              | /root/autodl-tmp/fullmine_vector_v2_targeted_runtime                  |
| Semantic source                               | /root/autodl-tmp/new_map_fullmine_vector_v2_dev                       |
| Bitmap source/current planner patch candidate | /root/autodl-tmp/fullmine_vector_v4_d_current_planner_patch_candidate |

# 4. 阶段一：MineSim 原项目复现与 IDM Baseline

目标：在 AutoDL 稳定复现原 MineSim，建立后续 MCTS、地图、multi-ego 和 neural 研究的回归锚点。

> • 核对真实 YAML / Hydra / Scenario / Planner / Controller API，不按模型记忆猜字段。
>
> • 确认 Planner 产生 future trajectory；Controller 计算控制；KBM 传播下一帧。Planner 结果不能被当作直接位置更新。
>
> • 建立 IDM/replay baseline commit/tag，Dapai/Jiangtong 原地图与 baseline 作为后续回归证据永久保留。
>
> • PASS：可初始化、逐帧 closed-loop 运行、无异常、结果/日志可追溯、Git 状态符合预期。

| **里程碑**   | **Commit / Tag**                                                      | **定位**                     |
|--------------|-----------------------------------------------------------------------|------------------------------|
| IDM baseline | 2521aa41a69a6e734c04c15a715e9530c8095ac3 / idm-replay-autodl-baseline | HISTORICAL / FROZEN 回归锚点 |

# 5. 阶段二：蒙特卡洛 / Pure MCTS 接入

目标：不重写 MineSim 执行层，在真实 closed-loop 中接入 Pure MCTS，并形成可追溯的专家搜索数据。

> • MCTSPlanner 外壳完成 state/action/search/reward 与 trajectory adapter 的连接；后续由 Controller/KBM 执行真实闭环。
>
> • Jiangtong 安全迭代加入 CV/CTRV 几何预测、buffer、viability、clearance 等机制；过程中始终区分搜索逻辑、trajectory adapter、controller 和 model propagation 故障域。
>
> • Dapai199 + Jiangtong249 = 448 strict historical expert samples；它们是历史专家证据，不与后续 current-semantic label 混同。
>
> • 五 Planner / budget 50/100/200/300 的比较形成能力边界；不是所有 planner 都适配同一 trajectory contract。

| **对象**           | **Commit / 结果**                                                                     | **状态**            |
|--------------------|---------------------------------------------------------------------------------------|---------------------|
| Pure MCTS + expert | 94693dc799fe5f325a75e8fc6d7d5e88764b4799 / mcts-expert-dataset-v1-20260802            | HISTORICAL / FROZEN |
| Jiangtong V22      | 94794c963f9c3eaf1873b275df6d319ca2636817 / jiangtong-v22-benchmark-screening-20260809 | HISTORICAL / FROZEN |

# 6. 阶段三：单车跑通

目标：用 real-GeoJSON / real MineSim closed-loop 证明单车从初始化到终点完整执行，不把局部 planner smoke 误当成 full-route 成功。

> • J117 Phase4C 单车 full route：423 steps，成为后续 multi-ego regression anchor。
>
> • FullMine 后续 Representative Pure MCTS 在跨代表区域 3/3 PASS，证明当前 Research/DEV runtime 上的单车规划链可工作。

| **对象**                    | **Commit / SHA**                                                                        | **状态** |
|-----------------------------|-----------------------------------------------------------------------------------------|----------|
| J117 Phase4C                | ec1c958735b0ee76201284faacb46fccc75c7f6c / j117-phase4c-single-ego-closed-loop-20260810 | FROZEN   |
| Representative MCTS summary | 742d0716a00364a625e01b27c693134488211c8989e4996b072739c3a500d056                        | FROZEN   |
| Representative MCTS freeze  | 322e90d6995c410597d01925de6d77f1fd91ddb8c4c73a25c3e87446d37ac1fa                        | FROZEN   |

# 7. 阶段四：双车冲突场景构建、MultiEgoRuntime 与 causal benchmark

目标：A/B 都成为受控对象，在同一 simulation iteration 内传播和决策，并建立“没有联合规划时会出现真实物理冲突”的因果对照。

> • MultiEgoRuntime 管理双受控车辆权威状态；受控 token 必须从 external tracked observation 过滤，避免同一 actor 同时 controlled + external 造成假碰撞。
>
> • EnvironmentSimulation.history 在 dual mode 主要保存 A 的 ego/history；B 的权威状态来自 MultiEgoRuntime。任何 A+B 可视化/分析不得假装 history 包含完整 B。
>
> • Jiangtong 虽有路径空间相交，但自然 ETA 差约 9.496s，交互弱，因此被负筛选；空间相交不等于 temporal conflict。
>
> • J117/Polygon21 的 NO-MCTS causal gate 使用固定速度、真实 footprint/swept overlap、post-conflict completion，不使用示意图或中心距代替物理真值。

| **对象**           | **结果**                                                                           | **状态**               |
|--------------------|------------------------------------------------------------------------------------|------------------------|
| J117 Phase5        | da4105b836dbbd3e702ee25fbb364109bc4e2596 / j117-phase5-dual-ego-pure-mcts-20260810 | FROZEN                 |
| Polygon21 scenario | 362eff18c7ccc88ea8dfaf083a517603566516943690d5cbe76bd1a97afc89e1                   | FROZEN                 |
| Polygon21 NO-MCTS  | 060880c8edc851e05606871cb647058d091ce8737f952b9864cc94e9d6fcfd13                   | FROZEN causal baseline |

# 8. 阶段五：FullMine 新地图接入与 Vector V4 冻结

目标：把真实 FullMine semantic/bitmap 资产接入 MineSim Map API、Planner、Controller 与 multi-ego runtime，同时严格区分 Research/DEV 可复现性与 production-authoritative 真值。

> • Vector V2 semantic 当前审计：403,759 nodes、100 roads、35 intersections、184 polygons、553 reference paths、402 borderlines、565 dubins poses、36 loading、7 unloading、6 auxiliary。
>
> • 大 semantic 初始化瓶颈来自约 40 万节点重复线性 scan；通过 token2ind O(1) lookup 修复，不归咎 GPU。
>
> • Bitmap/runtime/planner 经 targeted fixes 后形成 FullMine V4 frozen baseline；targeted 7/7 + Jiangtong old-map regression PASS。
>
> • semantic 保留 raw lane Z 和 repair provenance，但 source_z_datum_verified=false；slope waypoint\[4\]=0 的语义未权威验证，因此 terrain/Z/slope risk HOLD。
>
> • FullMine V4 仍没有官方 authoritative mask/internal exclusions/authoring rule，production-authoritative drivability NOT PROVEN。

| **对象**            | **Commit / SHA**                                                                      | **状态**       |
|---------------------|---------------------------------------------------------------------------------------|----------------|
| FullMine lookup     | 32fb42920d8cc404b37cd25dc47cbc6fbde4d9f4                                              | token2ind O(1) |
| FullMine V1         | d81c57154e4e5d0b4df1251cf565d9aacffaa026 / fullmine-dev-runtime-pass-20260811         | HISTORICAL     |
| FullMine V4         | 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e / fullmine-vector-v4-runtime-freeze-20260814 | CURRENT FROZEN |
| Semantic SHA        | b85a3d8b28f2252ecb5bda179d514573f6333079def838cd048566f556d95cd0                      | FROZEN         |
| Bitmap SHA          | 51abcd5a86e5c510204a5dacc873691506d721f98982ab7f98585d4e0f7efdd0                      | FROZEN         |
| CollisionLookup SHA | 10c1d1339e742ca893fedb4aa51402addfba82e16e08f68339ea35d35ba3043b                      | FROZEN         |

# 9. 阶段六：Fleet-MCTS 双车联合规划、多种子与跨场景结论

## 9.1 Polygon21 正式 benchmark

> • NO-MCTS 先证明同步无联合规划下存在真实物理重叠；Fleet-MCTS 再作为联合规划策略验证。
>
> • Fleet 参数：budget=64、depth=8；5/5 seeds 通过正式 benchmark。
>
> • 多种子结论不能与 seed 分配不均的 cross-scene 结果简单池化。

| **对象**                  | **SHA256**                                                       | **状态** |
|---------------------------|------------------------------------------------------------------|----------|
| Polygon21 Fleet seed0     | 2eeb28e1fcb1c48d826c387853ec4f9a8a1acf07c9d7e7d1c067701bd4a1398f | PASS     |
| Polygon21 Fleet freeze v2 | b89d290c9cb06d1efb99688ee27b23898ab81d11e36023832477dc2fc834364b | FROZEN   |

## 9.2 Cross-scene C04/C11/C06

| **场景** | **NO-MCTS causal**                                                                                | **Fleet-MCTS**                                                                                                              | **科学含义**                            |
|----------|---------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------|-----------------------------------------|
| C04      | PASS；真实 overlap；result SHA 0c806c2398047db7b4780147c4f959f92ece028d779fa286510052c0d0c2af37   | 成功 transfer；authoritative Fleet SHA 47e3ff50997d6ea095fce0ea0532ca9c01ace31abdc4646980f3b92b09129ca0                     | 成功跨场景。                            |
| C11      | horizon fix 后 PASS；NO-MCTS SHA c5bd459c1e936c089237f33b189b5b8d9d072f7ceab14e0d305d01a4642fa0e7 | 89s/890；无碰撞但 completed_post_conflict=False；Fleet SHA 47a6d570f65953e7dea35f46eb9f8ac63975c1e9e96402f6753f3f41e839547e | 真实安全死锁/进度失败；必须保留负结果。 |
| C06      | PASS；真实 overlap；NO-MCTS SHA db78f35b57ad897b50386698ddf488ab7b30343cf452ae61a9c86ab901c2f2fd  | 成功 transfer；Fleet SHA 0cbec940ce6581da1669fb06f49d091267f2365c8909c0cacafe393693d3df22                                   | 成功跨场景。                            |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>跨场景正式口径</strong></p>
<p>balanced seed0 full benchmark success=2/3（C04、C06），collision avoidance=3/3。C11 反证“冻结 Fleet-MCTS 在所有场景 universal success”。不得为得到全 PASS 而调参抹掉 C11。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 10. 阶段七：原生 MineSim 可视化与汇报材料

> • Native Video V1：NO-MCTS raw dimensions=(1545,3666)，科学链可跑但正式汇报布局异常，SUPERSEDED。
>
> • Native Video V2：NO-MCTS/Fleet raw=(1545,1073)，10fps；A 从原生 history，同 iteration B 从 MultiEgoRuntime live state overlay；A pose parity≤1e-8；最终 release FROZEN。
>
> • Renderer 的 conflict XY 不在 manifest 中直接提供；应使用 semantic reference_path.waypoints + exact route station 求点，禁止 hardcode。
>
> • Map Showcase V2 PASS / historical stable；V3 仅证实 ffmpeg SIGKILL:9 并保留 120 frames，原因不能擅自写成 OOM，状态 INCOMPLETE/HOLD。
>
> • 自动编码 PASS 不能替代 human visual gate；V0.2 target-anchored camera 修复 mid-pan blank。

| **对象**        | **SHA / 状态**                                                                            |
|-----------------|-------------------------------------------------------------------------------------------|
| Native Video V2 | f695ba22ecd61c4a643e8ffecac483bc218de9153f95f88b4e0e3006bca03d58 / CURRENT FINAL          |
| Map Showcase V2 | 9f78f357eecfc25ea543d163e8d472dc06abeb1fff3215ed30577267750d1e14 / PASS HISTORICAL STABLE |
| Map Showcase V3 | INCOMPLETE / HOLD；120 frames；final encode/release 未完成                                |

# 11. 阶段八：云端文件安全整理、目录体系与恢复

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>整理结论</strong></p>
<p>Phase2A–2K COMPLETE/PASS：/root/autodl-tmp 顶层约 530 → 121；记录 423 次 move/isolate；科研文件删除 0；HEAD/SHA/symlink/compile/restore final health PASS。整理是可逆移动/隔离，不是 rm 清盘；Archive/Quarantine 仍占空间。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

| **目录**                                     | **用途 / 规则**                                                                              |
|----------------------------------------------|----------------------------------------------------------------------------------------------|
| /root/autodl-tmp/00_MineSim_ACTIVE           | current_paths.json / env / 当前快捷软链接 / organization_tools。                             |
| /root/autodl-tmp/10_MineSim_REPORTS          | 正式汇报/发布备份；不作为科学运行输入。                                                      |
| /root/autodl-tmp/90_MineSim_ARCHIVE          | 可恢复历史归档；legacy planner、single MCTS、J117、FullMine dev、superseded media、bundles。 |
| /root/autodl-tmp/98_MineSim_QUARANTINE       | 隔离但未授权删除；8/16 closeout 约 315.76MB。                                                |
| /root/autodl-tmp/99_MineSim_CLEANUP_MANIFEST | Phase1–2K audit、move plan、fingerprint、health、restore provenance。                        |
| /root/autodl-tmp/MineSim-Dynamic             | 约203.75MB独立脏历史 workspace；HOLD；不是正式 repo 简单副本。                               |

> • 两条 runtime 关键软链接：runtime semantic 必须指向 new_map_fullmine_vector_v2_dev 的 semantic；runtime bitmap 必须指向 fullmine_vector_v4_d_current_planner_patch_candidate 的 bitmap。不要随意搬 target。
>
> • 冻结 runner 若依赖绝对路径，优先恢复历史路径/软链接，不直接修改 frozen runner。
>
> • 已知 \`?? ^C\` 是历史未跟踪异常名；不要为了目录美观执行 git clean。
>
> • 恢复必须使用对应 cleanup manifest 的 RESTORE 脚本逆序执行；恢复后核 HEAD/status、关键 SHA、symlink 和 py_compile。

# 12. 阶段九：后续神经网络接入——从 safety/data sidecar 到 Value V2

## 12.1 8/21 前置：Safety/data/current-semantic 链

| **对象**               | **结果 / 状态**                                        | **关键 SHA**                                                     |
|------------------------|--------------------------------------------------------|------------------------------------------------------------------|
| Continuous V2R V3      | C04 126-step full parity；不改 authoritative Fleet/V0  | 0231cda732ac4859985d4be451d01ade6f6e121892721ce9e6317dce430d64a4 |
| Heading/approach       | RouteAdapter heading；C04/C11/C06 approach=70/80/100m  | a27653c237118077a939001ae00aa2014bea3d15ec08f8393ba3e6aca7acb314 |
| Omega_int              | 35 intersections contract                              | a6b1de3c643c331b9a5d27f6544fa1266d4b3ff155f6de754cc94e8716db32c0 |
| Pair binding/Omega_app | AND_BOTH binding/Omega_app                             | 2e516d95200f5297e9e4a3a83445cc29462fc61beefe527c8022e0648fe89905 |
| Dynamic V2V d_safe     | 126 records；behavior/reward/search/pruning unchanged  | 3bcbbcb3623b07c3e8a162e24c5b63303b866cf9d149a68d083c30b5f7856193 |
| Shadow safe-node       | OBSERVATIONAL PASS；hard pruning not approved          | 7dc9a66c41cdb0dba78762dbc9606b7c103da32177eb2d730d94e95f70ab34b9 |
| Dataset Contract V1    | root-search raw + root×joint-action derived；Q primary | 46f2e099fbe9090a02b1f9fe8a983e4f8322a2ffeba89a4700de8e278991dcda |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>安全边界</strong></p>
<p>这些 sidecar / shadow 证据不等于 hard safety rule。MS_LOW 仅是 experimental/shadow candidate；20 roots 出现 16/16 全 reject、22 个真实执行动作也被 reject，因此 hard pruning 仍未批准。V2H probabilistic safety 未实现。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## 12.2 Value Network V1：pipeline PASS，跨场景科学 FAIL

> • C04 root collector：126 roots / 2016 action rows；C04 单 episode 24→64→64→1 smoke，train Pearson 0.880，仅证明 pipeline。
>
> • C11/C06 current-semantic collection：C11 890 roots/14240 rows（deadlock episode），C06 146 roots/2336 rows（success）；三场景共 1162 roots / 18592 root-action rows。
>
> • Formal split：leave-one-scene-episode-out，3 folds，normalization 只用 train fold，scene-balanced SmoothL1，600 epochs/fold。
>
> • 三个 held-out Top1 均低于随机 1/16=6.25%；normalized regret 均差于 immediate_reward。PROVISIONAL_VALUE_GUIDANCE_READY=False。
>
> • Decision=DO_NOT_INTEGRATE_VALUE_NETWORK_INTO_MCTS。当前 V1 不能靠“多训几轮”直接修复。

| **对象**                  | **SHA256**                                                       |
|---------------------------|------------------------------------------------------------------|
| C04 root collector result | daa9bc9e278aabf54b26e9858a08b0d58fb8192a2511f57f7d15bd4098a20422 |
| C04 Value V1 checkpoint   | 6c223729cbbba3044b972fd7a90f4121e883fd34c9a6093f2b8e18597cf11413 |
| C11/C06 collector result  | 94ec9778a2899825125eaaed5c2ece50b8d0cd29390481c1e6f2ac568f052300 |
| Three-scene LOSO result   | 7c296200504ed75ca216a46bc74427703f99a9d5c75f35b0b1bd7e20fd10cdf1 |
| LOSO summary              | ac1d46ca91d6813e868121ced41e8751479ed2f4d4d6afd437921313e42b6e5a |
| V1 failure diagnostic     | d16b2f0805235a5aedc07909e763329984588b3bed145fb46557a97388a1b6fa |

## 12.3 Value V2 final-dev model（8/22～8/23 已冻结）

| **项目**          | **当前事实 / 处理规则**                                          |
|-------------------|------------------------------------------------------------------|
| Target            | ROOT_CENTERED_Q                                                  |
| 训练场景          | C04 / C11 / C06（全部属于 DEVELOPMENT EVIDENCE）                 |
| 网络              | 12 → 64 → 64 → 16                                                |
| checkpoint        | paper1_value_v2_final_dev_pre_c13.pt                             |
| checkpoint SHA    | ce32cb7943a05d62ea16aee95a86f26bab7521af1d345e39f5c8a410a02ffb13 |
| normalization SHA | 36ee17a182c519c41602c5d414a4e009a569660254bb4bd31fc75a3b705bc6f9 |
| model freeze SHA  | a2be866144446a442cf7a8cb23a7f7ce9041a2d7b86fcded2ff8709f7a24d05b |
| MCTS integration  | False；仍未接入                                                  |

## 12.4 C13 独立数据与一次性 Value V2 evaluation：forward 已发生，科学指标未评估

> • C13 独立数据：115 roots / 1840 rows；full collection freeze SHA c41714c323789945474db3004a7c6ab21acc963faa3807bd4452d708a296bdac。
>
> • C13 one-time evaluation 预检查通过后执行：Value model forward call count=1，prediction shape=\[115,16\]。
>
> • metric-binding harness 错把后面的零参数 main() 绑定成指标函数，触发 TypeError: main() takes 0 positional arguments but 3 were given。真正指标函数确认是 ranking_metrics(q, pred, immediate)。
>
> • prediction artifact 未持久化、scientific metrics 未评估；C13 scientific gate=HOLD_NOT_EVALUATED。由于 one-time protocol 已消耗，retry_authorized=False，C13 永久禁止重跑。
>
> • 静态 metric fix 已冻结（SHA 2a9e0d1d3b5f5cc276eb2995d61056300275e588d87e0e2cc24bd939a89d2440），但永远不应用于 C13 重试。
>
> • C13-B static caveat（两个孤立 DEV-mask 单像素 hole）原样保留；未授权补图。

| **对象**                                 | **SHA / 状态**                                                                                                  |
|------------------------------------------|-----------------------------------------------------------------------------------------------------------------|
| C13 collection freeze                    | c41714c323789945474db3004a7c6ab21acc963faa3807bd4452d708a296bdac / FROZEN                                       |
| C13 schema lock                          | 796a3ee137f00fef5b5f8ff9f3ffdd6b1882c10ca4d1db37581c391ee6330b31                                                |
| C13 selection lock                       | 7782e2d82eaafe52b82e6378692ee49b94da9f424c0b729e61a1c4ef19130205                                                |
| C13 one-time eval technical failure lock | 50c072076805e983e23dc14150bd70574dfb5b1c964f718d783a53fea806e538 / FROZEN_TECHNICAL_FAILURE_AFTER_MODEL_FORWARD |
| Metric binding static fix                | 2a9e0d1d3b5f5cc276eb2995d61056300275e588d87e0e2cc24bd939a89d2440 / NOT APPLIED TO C13                           |

## 12.5 Replacement independent scene：预注册、C09/C10/C14/C03

> • 为避免在看候选值后人为挑场景，先冻结 blind preregistration：排除 C04/C06/C09/C11/C13；要求 Fleet=0、Neural=0、Collector=0；NOMCTS 不是排除条件。
>
> • 排序规则冻结为：angle novelty DESC \> distance to nearest existing benchmark DESC \> minimum endpoint margin DESC \> pair option count DESC \> source index ASC。
>
> • 最终 eligible 排名固定为 C10（rank1）→ C14（rank2）→ C03（rank3），不得 reselection / rescoring。

| **候选** | **Physical**                | **Static qualification**                                                                                                                | **最终状态 / 原因**                               |
|----------|-----------------------------|-----------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------|
| C09      | geometry conflict PASS      | B exact frozen-route fallback physical_drivable=False；28 bad poses / 71 unique bad pixels，坏区跨 conflict                             | REJECT；不跑 NO-MCTS；不补 bitmap，不改 planner。 |
| C10      | per-candidate physical PASS | A direct PASS；B direct technical exception 后 exact frozen-route fallback physical_drivable=False；16 bad poses / 39 unique bad pixels | REJECT / FROZEN。                                 |
| C14      | per-candidate physical PASS | A direct PASS；B route_exact_match=False（expected route 被截断，实际多 path-000323），未进入 bitmap scan                               | REJECT；NONTECHNICAL_ROUTE_CONTRACT_FAILURE。     |
| C03      | per-candidate physical PASS | A/B direct static PASS；各451 samples，0 bad pose，0 unique bad pixel                                                                   | STATIC PASS；进入 NO-MCTS causal qualification。  |

| **关键 lock**                   | **SHA256**                                                       |
|---------------------------------|------------------------------------------------------------------|
| Replacement preregistration     | e838ee70992d3cc8a3183d21e3dc34b8db4f7801652044356439bf94e87e903c |
| Replacement candidate selection | 18f6fa4996d1d4aba45d3fe7ad378ea89fd596983aa02b6037ed8d07bf15b65e |
| C10 final rejection             | 92d4b761a7045676bc0d3c15b9a2e823da159d3ea35a0e35d2ecf70991c8689e |
| C14 final rejection             | 590d2b753f97d4c78fbc04c95b43bb525217f6e9b2ec5d09933df80244ba8d22 |
| C03 entry lock                  | cc154fa9a257cab38f6519013a94298241c8388b0f4af7ac3e6736307892dc2f |

## 12.6 C03 physical / static qualification（已冻结）

| **项目**              | **当前事实 / 处理规则**                                                                                                                           |
|-----------------------|---------------------------------------------------------------------------------------------------------------------------------------------------|
| C03 candidate         | source 3；polygon-000024；path A path-000546；path B path-000548；station A 63.3420136560992；station B 30.15527615570293；symmetric approach 75m |
| Physical route A      | path-000379 → path-000546 → path-000095                                                                                                           |
| Physical route B      | path-000003 → path-000548 → path-000549                                                                                                           |
| Physical result SHA   | 1ca34c2860266cb14121214987db6f87747252d6e4189dca7f784709d7f9901f                                                                                  |
| Physical lock SHA     | c308ffa6c55d917ee73237aa645a16aa46461313006220e0b7cc911f76261ce2                                                                                  |
| Dual scenario SHA     | df4698f2e0de3ed99649349583d6f1c4c95020b4e8fdb91f8bccbaca17592adf                                                                                  |
| Scenario manifest SHA | 061887ed6b632f4648978b62363dab78125de3665ed3368997cd4bb85c056d33                                                                                  |
| Static A              | route exact；90m scan；451 samples；physical_drivable=True；0 bad；result SHA 0453d93f41123f1ffaea0c348c23c19d9750d1c6723c5a8a79411218eec7361b    |
| Static B              | route exact；90m scan；451 samples；physical_drivable=True；0 bad；result SHA 066bac4c935524d95408e7809bfbc066504b81ed152dc13d09e62720c72addf9    |
| Static direct lock    | b7490746098d1a61248e225cf66db4ed532db1f8f02268ab6d19bfdd10433060 / PASS_C03_STATIC_BITMAP_QUALIFICATION                                           |

## 12.7 C03 NO-MCTS causal qualification：2026-08-23 全部真实推进

| **步骤**                     | **结果 / 解释**                                                                                                                                                                                                         | **关键 SHA**                                                                                                                                                                                                                                                                                                              |
|------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Runner discovery             | 12 candidates；heuristic top 并列7，不按分数选择；绑定 C13 independent causal fix1 parent runner。                                                                                                                      | parent 7ec6b065462f335321832ca756d6c5039621f7de60096c79cce34271b6f5e5aa                                                                                                                                                                                                                                                   |
| Parent source contract       | 校正 os.environ Load/Store 审计；冻结 helper/source/result schema。                                                                                                                                                     | env fix df1b333d32443097b827d2d38ba44cb0c45716d722e9095ba36b6fcc4dc00711；contract 0645826052d35d4aa4a97582047d93ac0bb8daab6476fc988ee48bd8af7b6e3a                                                                                                                                                                       |
| Initial C03 child            | 仅 identity/route/hash/static metadata 与 frozen 75m candidate rebound；DT=0.1、speed=4.5、post=15、MAX_STEPS=200。                                                                                                     | runner e72e35104fbdd46f25532f1345e4047bc581ac7fb20b4a0508fb17d51168e4ff；derive df2545354ac7d237e326c77965014b0cb482115de9b23ebddb9e882d37fbc8fa                                                                                                                                                                          |
| Pre-execution horizon review | 75+15=90m；4.5m/s 需20.0s，恰等于200×0.1=20.0s，零余量；参考 C11 200-step precedent，预执行 only 改 MAX_STEPS→212。                                                                                                     | horizon runner 2861355241c45c6e21ea5a703ac4b6ad4bb62d213df4f241c021a3dea2098bf4；derive 572a60aaf4f4c05ad0deeb2a40c53514d1e3a93c4b1f6681c6510b15fd9f1bda；new preauth 49f82de58d627f499d090fb973156f83681aecc8047eb27b75922d309863adc0                                                                                    |
| Attempt \#1                  | 高资源80GiB/15CPU；START 已写；runner RC=1；RESULT/LOG 均生成，但 iterations=0，error=RuntimeError: A_loaded_approach_not_50m。没有任何 causal trajectory step。                                                        | START 85ebe0243dece58e815d9148459d7d79e17839d1afb136bc0483d8dfe0d7650b；capture 2181c9966ae4a0f9d0587062dc01dbe3ad3545e2f541909c3e972e57b92b98de；result 52b4cf7d59c84d2032452b56a28498aaa54381f5acbcde7f574625d0d714d99d；log 37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570                           |
| Technical failure freeze     | Manifest A/B approach=75m；loaded A=74.99999999999986、B=74.99999780866457；runner APPROACH_M=75；精确定位两处 stale \`actual_approach - 50.0\` identity check。科学结果未评估。                                        | technical failure lock b6d31c088bf07799c4b546d6a7a80e159bb99ba2e36c1ee15fab8ca8305e56f9                                                                                                                                                                                                                                   |
| Manual technical retry fix   | 只把两处 50.0 改为 APPROACH_M；tolerance 1e-3、helper、DT、speed、approach、post、MAX_STEPS、route、causal dynamics 全不变。                                                                                            | corrected runner eba4fbb6d4b2c63217cd19510406dbbde99a4937fb5dd8ca498336687198b4c5；fix lock 4ff91e19a6e34ed4618e86b7b22305ac35a39025d6a5bce2b1c81e5e8838c06f；exception db7f1df8fe5a79edd336cc73a796aab82cbb75e2db4d2a867107b97dc516e6eb；retry1 preauth 471b17145802db66015f06cdcca99eaadbf6edbda0726146c3262b3d52a98293 |
| Latest current stop          | 高资源 retry1 gate：80GiB/15CPU，RETRY1_OUTPUTS_ABSENT=PASS；在 PREAUTH BINDING 读取 \`e\["old_attempt_artifacts"\]\` 时 KeyError。失败发生在写 retry1 START 之前，因此 retry1 未执行、未消耗；不是 scientific result。 | 当前无 retry1 START/CAPTURE/result/log；下一步只修 wrapper schema key。                                                                                                                                                                                                                                                   |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>当前 C03 科学口径</strong></p>
<p>Attempt #1 = FROZEN zero-iteration technical failure；C03 causal outcome NOT EVALUATED；SCIENTIFIC_FAIL=False。Manual technical retry #1 的 corrected runner 与 preauth 已冻结，但 retry #1 尚未真正开始。第三次执行问题尚未发生；当前只允许在修复 wrapper schema 后按既有 retry1 preauth 执行一次。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 13. 重要问题、失败、原因、修复与永久禁忌

| **故障/现象**                          | **原因**                                                          | **解决 / 当前证据**                                                         | **以后不能再做**                                 |
|----------------------------------------|-------------------------------------------------------------------|-----------------------------------------------------------------------------|--------------------------------------------------|
| Planner/Frenet step150 IndexError      | best_traj 长79却访问79；trajectory resample/adapter 越界          | 安全重采样后199/249跑通；先分 search/adapter/controller                     | 不要把 adapter 越界误判为 MCTS 搜索失败          |
| Multi-ego duplicate actor              | A/B 同时 controlled + external，产生假碰撞                        | controlled token 从 tracked observation 过滤                                | 受控车辆绝不能重复作为 external obstacle         |
| Environment history 缺 B               | SimulationHistory 主要记录 A；B truth 在 MultiEgoRuntime          | 同 iteration runtime.state_for(B)                                           | 禁止用 A history 假装完整 A+B                    |
| Native B visualization                 | B 无法直接用 history 回放                                         | A 用 history，B live overlay；pose parity≤1e-8                              | 禁止 route_s/CSV/pixel 猜 B 姿态                 |
| Jiangtong conflict screening           | 路径空间相交但自然 ETA 差约9.496s                                 | 负筛选 freeze                                                               | 空间交叉≠时间冲突                                |
| CollisionLookup false positive         | 离散 lookup 与 exact footprint 定义不同                           | NO-MCTS causal gate 用 exact footprint/swept overlap                        | 中心距/查表/示意图不能替代物理真值               |
| FullMine init slow                     | 约400k node重复线性 scan                                          | token2ind O(1)                                                              | 先 profile 复杂度，不归咎 GPU                    |
| A1 endpoint / A2 mid-stop              | virtual endpoint geometry / steering-rate infeasibility           | virtual endpoint length_rear=0；steering-aware speed cap + backward braking | 不要盲补 bitmap 或改 goal                        |
| Map/runtime path                       | 整理后绝对路径/软链接失效                                         | current_paths + restore/symlink gate                                        | 冻结 runner 优先恢复路径，不直接改代码           |
| Low-memory RC137                       | 2GiB cgroup 不足                                                  | 先低资源 preflight，长仿真才80GiB/15CPU                                     | 不要低配硬跑大图/长仿真                          |
| Map Showcase V1/V3                     | V1 schema误判；V3 ffmpeg SIGKILL:9                                | 读真实 schema；V3保留120帧/HOLD                                             | 不能无证据把 SIGKILL 写成 OOM                    |
| Native Video V1                        | raw=(1545,3666)布局异常                                           | V2=(1545,1073)+ffprobe+human gate                                           | 科学链可跑≠汇报质量 PASS                         |
| Renderer conflict XY / OUT KeyError    | manifest 给 route_s；wrapper漏传OUT                               | semantic route station 求点；required env gate                              | 禁止 hardcode XY；wrapper 必须先校验 env         |
| Video mid-pan blank                    | camera logic                                                      | V0.2 target-anchored camera                                                 | 最终必须 human visual gate                       |
| Long heredoc / 粘贴污染                | 聊天 UI 与终端输出混粘                                            | 短块、文件优先、先 ls/file/sed                                              | 禁止因粘贴异常清整个目录                         |
| C04 loader float(list)                 | 一元素 list / \[N\]\[1\] shape 未规范                             | shape normalization                                                         | 不从旧文档重跑、不猜 exact failing line          |
| C04 NO-MCTS MAX_STEPS NameError        | harness 常量遗漏                                                  | 最小 runner fix                                                             | harness FAIL≠science FAIL                        |
| C11 NO-MCTS 200-step                   | completed_post_conflict=false；时间窗不足                         | 延到21.2s/212，仅改 horizon                                                 | 不改冲突物理/算法                                |
| C11 Fleet deadlock                     | 89s无碰撞但不完成                                                 | 冻结负结果                                                                  | 禁止为“全PASS”调参抹掉                           |
| Historical 448 vs current labels       | producer/rear-axle/center语义已变                                 | legacy隔离 + current-code recollection                                      | schema相同≠label语义同质                         |
| Collector JSON +inf / false PASS       | allow_nan=False 序列化失败；先内存append后写盘                    | 删除未合同化字段；严格序列化后再append                                      | JSONL空不能由内存summary伪装PASS                 |
| Full collector timeline                | root absolute vs V0 relative time                                 | 对齐 origin/cadence；离线 salvage                                           | 无需重跑已完成仿真                               |
| PyTorch missing                        | 镜像≠conda env                                                    | 安装 CPU torch 2.8.0+cpu                                                    | 不要假设镜像包等于 env 包                        |
| C13 one-time Value eval metric binding | AST错误绑定main()而非ranking_metrics                              | 冻结 failure；静态修复但禁止 C13 retry                                      | one-time 独立验证失败后不得重跑/调参             |
| C09 static reject                      | fallback仍28 bad / 71 bad pixels且跨conflict                      | 负筛选冻结                                                                  | 不补图、不为独立候选改 planner                   |
| C10 static reject                      | B fallback physical_drivable=False，16 bad / 39 pixels            | 冻结淘汰                                                                    | 按预注册顺序转 C14                               |
| C14 static reject                      | B expected route truncated，route_exact_match=False               | NONTECHNICAL_ROUTE_CONTRACT_FAILURE                                         | 不把 route contract failure 当 map physical fail |
| C03 parent env audit                   | 旧 preflight 把 os.environ Store 也叫 env_loads                   | 区分 Load/Store；MINESIM_DATA_ROOT/MAPS_ROOT 是 Store                       | AST env 审计必须区分 ctx                         |
| C03 horizon zero slack                 | 75+15m /4.5=20s 恰等于200×0.1                                     | 预执行改212；无 outcome-informed retuning                                   | 运行前先检查完成门的时间余量                     |
| C03 attempt1 stale 50m runtime check   | 顶层 approach=75，但深层 identity check仍50                       | 冻结0-step technical failure；只改两处 identity check                       | 技术失败不等于 C03 science FAIL                  |
| C03 retry1 PREAUTH binding KeyError    | wrapper期待 \`old_attempt_artifacts\`，实际 exception schema 不同 | 当前下一步低资源只读对齐 schema；runner/preauth 不改                        | retry1 未启动前不得误记为第二次执行              |
| codex-env.sh missing                   | 登录提示路径缺失；来源不明                                        | 标路径缺失/处置未验证                                                       | 不能据此推断被删或 Codex 工作丢失                |

# 14. 当前有效版本、SUPERSEDED / HOLD / 未验证对象

| **对象**                                  | **状态**                               | **处理规则**                                                                     |
|-------------------------------------------|----------------------------------------|----------------------------------------------------------------------------------|
| MineSim baseline 2521aa4                  | HISTORICAL / FROZEN                    | 保留回归；不是 current HEAD。                                                    |
| Pure MCTS 94693dc + 448                   | HISTORICAL / FROZEN                    | 专家历史证据；current-semantic label 需隔离。                                    |
| J117 Phase4C/5                            | FROZEN                                 | 不重跑；multi-ego regression anchor。                                            |
| FullMine Vector V4 112d2bd                | CURRENT FROZEN                         | 不得修改 frozen tag；新研究在独立 evidence workspace。                           |
| Representative Pure MCTS 3/3              | FROZEN                                 | 无需重做。                                                                       |
| Polygon21 Fleet freeze v2                 | FROZEN                                 | 正式 benchmark；旧 harness failures 仅 provenance。                              |
| Cross-scene C04/C11/C06                   | CLOSED WITH NEGATIVE                   | C11 negative 必须保留。                                                          |
| Native Video V1                           | SUPERSEDED                             | 保留 provenance，不用于正式汇报。                                                |
| Native Video V2                           | CURRENT FINAL                          | 正式视频 evidence release。                                                      |
| Map Showcase V2                           | PASS / HISTORICAL STABLE               | V3 未 final，不覆盖 V2。                                                         |
| Map Showcase V3                           | INCOMPLETE / HOLD                      | 120 frames；final encode/release 未完成。                                        |
| Paper1 V2R/heading/Omega/pair/dynamic V2V | FROZEN / DIAGNOSTIC                    | 不改变 planner behavior；不得外推 hard safety。                                  |
| Shadow safe-node                          | OBSERVATIONAL PASS                     | hard pruning not approved。                                                      |
| Value V1                                  | FORMAL TRAINING PASS / SCIENCE FAIL    | DO_NOT_INTEGRATE；development evidence。                                         |
| Value V2 final-dev model                  | FROZEN DEVELOPMENT MODEL               | 尚无有效 independent science PASS；不得接入 MCTS。                               |
| C13 one-time independent eval             | FROZEN TECHNICAL FAILURE AFTER FORWARD | scientific metrics NOT EVALUATED；retry forbidden。                              |
| C10                                       | FROZEN STATIC REJECT                   | 永久关闭。                                                                       |
| C14                                       | FROZEN STATIC REJECT                   | 永久关闭。                                                                       |
| C03                                       | STATIC PASS / CAUSAL HOLD              | attempt1 zero-step technical failure；retry1 preauth ready，但 retry1 尚未执行。 |
| FullMine production validity              | HOLD / NOT PROVEN                      | 缺官方 drivability / authoring rule。                                            |
| Terrain/Z/slope risk                      | HOLD                                   | datum/slope语义未权威验证。                                                      |
| V2H probabilistic safety                  | NOT IMPLEMENTED                        | 阻塞 full safe-node。                                                            |
| Policy Network / PUCT                     | NOT STARTED                            | 先完成 Value independent validation。                                            |
| Value-guided MCTS                         | NOT INTEGRATED                         | MCTS_VALUE_INTEGRATION=False。                                                   |

# 15. 环境、资源、运行与恢复规范

| **项目**      | **当前规则 / 真实观测**                                                                         |
|---------------|-------------------------------------------------------------------------------------------------|
| 正式 repo     | /root/MineSim-Dynamic                                                                           |
| Conda env     | minesim；/root/miniconda3/envs/minesim                                                          |
| Python        | 3.9.25（实际激活环境）                                                                          |
| PyTorch       | 2.8.0+cpu（后安装）；不要假设镜像自带等于 env 已装。                                            |
| 低资源 cgroup | 约 2GiB / 0.5 CPU；CUDA disabled。                                                              |
| 高资源 cgroup | memory.max=85899345920（80GiB）；cpu.max=1500000 100000（15 CPU）。                             |
| 高资源 GPU    | RTX 4090D 24GB×1；本项目多数 MCTS/collector/causal 运行仍 CUDA 禁用，高资源价值主要是 RAM/CPU。 |
| 大文件        | /root/autodl-tmp；正式 repo 只保留必要 tracked source。                                         |

## 15.1 所有可执行代码固定前缀

cd /root/MineSim-Dynamic  
source /root/miniconda3/etc/profile.d/conda.sh 2\>/dev/null \|\| true  
conda activate minesim  
export PYTHONPATH=/root/MineSim-Dynamic  
export CUDA_VISIBLE_DEVICES=""

> • 交互顶层禁止裸 \`exit\`；需要失败终止时放入子 shell \`( ... )\` 用 \`false\`，或只打印 FAIL。
>
> • 禁止 \`git reset --hard\`、\`git clean -fd\`、\`git add .\`；只 add 精确文件；commit 前 diff/check/name-only。
>
> • 长仿真使用普通 terminal/screen，独立 log + rc；screen 只是托管，不是证据源。
>
> • 每个 map candidate / script / result 必须绑定 SHA；临时 runtime 切图使用 symlink + strong SHA gate。
>
> • 任何 one-time / retry-limited 实验先写 START lock，再执行；失败后不得自动 rerun。

## 15.2 统一只读 preflight

pwd  
git rev-parse HEAD  
git status --short  
cat /sys/fs/cgroup/memory.max  
cat /sys/fs/cgroup/cpu.max  
screen -ls  
ps -eo pid,etime,%cpu,%mem,cmd \| grep -E 'MineSim\|paper1\|mcts' \| grep -v grep \|\| true  
sha256sum \<current input artifacts\>

# 16. 用户—ChatGPT—Codex 协作规则与成本控制（已固化）

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>协作定义</strong></p>
<p>ChatGPT 负责分析、决策、关键代码与验收设计；用户负责把代码复制到 AutoDL 云端执行并返回真实终端输出/文件；复杂算法、顽固 Bug、关键结论复核或适合云端自主执行的麻烦任务才在省钱前提下交给 Codex。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

| **规则**         | **固定执行方式**                                                                            |
|------------------|---------------------------------------------------------------------------------------------|
| 默认 Codex model | gpt-5.6-luna medium。                                                                       |
| 升级策略         | 必要时才临时 Terra/Sol；任务完成立即降回 Luna。                                             |
| 已知事实         | 不重复扫描、不重复解释；已 frozen 阶段不重审。                                              |
| 任务粒度         | 每次只推进一个最小 blocker；只返回 PASS/FAIL 与必要字段。                                   |
| 免费优先         | file/process/hash/git/grep/py_compile/JSON audit 能用 Shell/Python 免费确认的事情不用模型。 |
| 资源顺序         | 先免费/低资源完成 read-only preflight/static/smoke；确需长仿真/大图才开高资源。             |
| 实验顺序         | 只读 preflight → smoke → 短闭环 → 完整实验 → freeze。                                       |
| 长任务           | 普通 terminal/screen；不让 Codex 长时间等待。                                               |
| 文件策略         | 大源码、日志、JSON/CSV、视频、ZIP 放 /root/autodl-tmp；聊天只传任务、短字段、error tail。   |
| 失败处理         | 只定位当前故障域；一个 FAIL 不回滚到全仓扫描。                                              |
| 安全优先         | 可复现、可恢复、结果质量优先于目录美观、省几分钟或少几个文件。                              |

> • 复杂 Codex prompt 必须包含：已冻结事实、唯一目标、允许修改文件、禁止操作、最小测试、PASS/FAIL、最终输出字段、完成即停止。
>
> • 长仿真不由模型“等结果”；普通终端运行，模型只基于持久化进度/日志/结果继续分析。

# 17. 云端文档生成、归档、移动与删除情况

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>可以确定的删除事实</strong></p>
<p>截至现有证据，2026-08-16 Phase2A–2K 科研文件删除 0；2026-08-21 assistant package cleanup 也是 move/archive，不是 deletion。Quarantine 是隔离，不是删除授权；Archive 是可恢复历史。目录变干净不等于释放磁盘空间。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

> • 2026-08-16：顶层约 530→121，423 move/isolate；final health/restore PASS。
>
> • 2026-08-21：assistant package cleanup closeout 记录 move manifest=99、keep manifest=3、problem_count=0、restore script 存在、SHA 验证通过；随后又生成大量 Paper1/NN 资产，因此“当时顶层3个文件”只是瞬时状态。
>
> • 旧 C11/C06 upload ZIP 顶层缺失后在 90_MineSim_ARCHIVE/.../30_review_hold 找到，证明 path missing ≠ deleted。
>
> • \`/root/autodl-tmp/codex-env.sh: No such file or directory\` 只能标记为“路径缺失/处置未验证”，不能推断被删。
>
> • 若以后要真正腾空间，必须另开 deletion phase：只读 inventory → checksum/equivalence → 明确授权 → 删除；不能把 cleanup move 当删除许可。

| **文档/包**                                                        | **当前定位**                                                                              |
|--------------------------------------------------------------------|-------------------------------------------------------------------------------------------|
| MineSim-Dynamic_普通AI与AutoDL云端交互及代码调试手册（2026-07-26） | HISTORICAL；安全交互/Git规则。                                                            |
| MineSim-Dynamic_项目全景档案与AI长期接管超级手册（2026-08-06）     | HISTORICAL；Pure MCTS/五 Planner。                                                        |
| MineSim-Dynamic_云端项目完整交接与工作流手册（2026-08-09）         | HISTORICAL；J117 单车。                                                                   |
| MineSim-Dynamic_新地图项目云端交接手册（2026-08-11）               | HISTORICAL；FullMine V1。                                                                 |
| MineSim-Dynamic_全项目阶段性总总结与AI无缝接管手册_2026-08-18      | 上一版综合手册；neural 状态已被 8/21/8/23 更新覆盖。                                      |
| MineSim-Dynamic_全项目阶段性总总结与AI无缝接管手册_2026-08-21      | 当前重要历史基线；本 8/23 版在其上追加 Value V2 / replacement / C03。                     |
| 本 2026-08-23 Word                                                 | 本会话生成 artifact；只有实际上传到 AutoDL 指定目录并记录 SHA 后，才能称“云端现存 Word”。 |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>Word 精确云端库存：HOLD</strong></p>
<p>现有证据没有做 2026-08-23 的全云端 Word live inventory，也没有证据证明某个 Word 被人工删除。因此“云端现存 Word 精确数量 / 是否有人手动删过某份 Word”仍未验证。当前会话中可见的 Word/ZIP 是上传到 ChatGPT 会话的证据，不等同于它们必然还位于 AutoDL 某个路径。正式报告备份策略仍是 `/root/autodl-tmp/10_MineSim_REPORTS`。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 18. 关键 Commit / Tag / SHA / 冻结证据速查

| **里程碑**          | **Commit / Tag / SHA**                                                                |
|---------------------|---------------------------------------------------------------------------------------|
| IDM baseline        | 2521aa41a69a6e734c04c15a715e9530c8095ac3 / idm-replay-autodl-baseline                 |
| Pure MCTS + expert  | 94693dc799fe5f325a75e8fc6d7d5e88764b4799 / mcts-expert-dataset-v1-20260802            |
| Jiangtong V22       | 94794c963f9c3eaf1873b275df6d319ca2636817                                              |
| J117 Phase4C        | ec1c958735b0ee76201284faacb46fccc75c7f6c                                              |
| J117 Phase5         | da4105b836dbbd3e702ee25fbb364109bc4e2596                                              |
| FullMine lookup     | 32fb42920d8cc404b37cd25dc47cbc6fbde4d9f4                                              |
| FullMine V1         | d81c57154e4e5d0b4df1251cf565d9aacffaa026                                              |
| CURRENT FullMine V4 | 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e / fullmine-vector-v4-runtime-freeze-20260814 |

| **对象**                   | **SHA256**                                                       |
|----------------------------|------------------------------------------------------------------|
| FullMine semantic          | b85a3d8b28f2252ecb5bda179d514573f6333079def838cd048566f556d95cd0 |
| FullMine V4 bitmap         | 51abcd5a86e5c510204a5dacc873691506d721f98982ab7f98585d4e0f7efdd0 |
| CollisionLookup            | 10c1d1339e742ca893fedb4aa51402addfba82e16e08f68339ea35d35ba3043b |
| Representative MCTS freeze | 322e90d6995c410597d01925de6d77f1fd91ddb8c4c73a25c3e87446d37ac1fa |
| Polygon21 Fleet freeze v2  | b89d290c9cb06d1efb99688ee27b23898ab81d11e36023832477dc2fc834364b |
| Native Video V2            | f695ba22ecd61c4a643e8ffecac483bc218de9153f95f88b4e0e3006bca03d58 |
| Map Showcase V2            | 9f78f357eecfc25ea543d163e8d472dc06abeb1fff3215ed30577267750d1e14 |
| Cleanup Phase2K closeout   | e3d4ba27bd06c74c7ca23ed55de65208022f07d4e0cb600eb58bcbbcaaf33a4b |

| **2026-08-23 Value V2 / C03 关键对象** | **SHA256 / 状态**                                                                           |
|----------------------------------------|---------------------------------------------------------------------------------------------|
| Value V2 checkpoint                    | ce32cb7943a05d62ea16aee95a86f26bab7521af1d345e39f5c8a410a02ffb13                            |
| Value V2 model freeze                  | a2be866144446a442cf7a8cb23a7f7ce9041a2d7b86fcded2ff8709f7a24d05b                            |
| C13 collection freeze                  | c41714c323789945474db3004a7c6ab21acc963faa3807bd4452d708a296bdac                            |
| C13 eval technical failure lock        | 50c072076805e983e23dc14150bd70574dfb5b1c964f718d783a53fea806e538                            |
| Replacement prereg                     | e838ee70992d3cc8a3183d21e3dc34b8db4f7801652044356439bf94e87e903c                            |
| Replacement selection                  | 18f6fa4996d1d4aba45d3fe7ad378ea89fd596983aa02b6037ed8d07bf15b65e                            |
| C03 physical lock                      | c308ffa6c55d917ee73237aa645a16aa46461313006220e0b7cc911f76261ce2                            |
| C03 scenario                           | df4698f2e0de3ed99649349583d6f1c4c95020b4e8fdb91f8bccbaca17592adf                            |
| C03 static direct lock                 | b7490746098d1a61248e225cf66db4ed532db1f8f02268ab6d19bfdd10433060                            |
| C03 NO-MCTS parent contract            | 0645826052d35d4aa4a97582047d93ac0bb8daab6476fc988ee48bd8af7b6e3a                            |
| C03 attempt1 result                    | 52b4cf7d59c84d2032452b56a28498aaa54381f5acbcde7f574625d0d714d99d / zero-step technical fail |
| C03 technical failure lock             | b6d31c088bf07799c4b546d6a7a80e159bb99ba2e36c1ee15fab8ca8305e56f9                            |
| Corrected retry1 runner                | eba4fbb6d4b2c63217cd19510406dbbde99a4937fb5dd8ca498336687198b4c5                            |
| Runtime contract fix lock              | 4ff91e19a6e34ed4618e86b7b22305ac35a39025d6a5bce2b1c81e5e8838c06f                            |
| Manual retry exception lock            | db7f1df8fe5a79edd336cc73a796aab82cbb75e2db4d2a867107b97dc516e6eb                            |
| Retry1 preauth                         | 471b17145802db66015f06cdcca99eaadbf6edbda0726146c3262b3d52a98293 / prepared, NOT EXECUTED   |

# 19. 当前云端目录结构与绝对不能动的对象

| **逻辑对象**            | **当前登记路径 / 说明**                                               |
|-------------------------|-----------------------------------------------------------------------|
| formal_repo             | /root/MineSim-Dynamic                                                 |
| polygon21_current       | /root/autodl-tmp/fullmine_v4_dual_candidate_v1                        |
| cross_scene_current     | /root/autodl-tmp/fullmine_v4_fleet_cross_scene_v1                     |
| representative_mcts     | /root/autodl-tmp/fullmine_v4_mcts_representative_v1                   |
| representative_coverage | /root/autodl-tmp/fullmine_v4_representative_coverage_v1               |
| production_truth_gap    | /root/autodl-tmp/fullmine_v4_production_truth_gap_v1                  |
| runtime_current         | /root/autodl-tmp/fullmine_vector_v2_targeted_runtime                  |
| semantic_source_current | /root/autodl-tmp/new_map_fullmine_vector_v2_dev                       |
| bitmap_source_current   | /root/autodl-tmp/fullmine_vector_v4_d_current_planner_patch_candidate |
| formal_mcts_results     | /root/autodl-tmp/mcts_results                                         |
| idm_baseline_backup     | /root/autodl-tmp/minesim_idm_baseline_backup                          |
| archive_root            | /root/autodl-tmp/90_MineSim_ARCHIVE                                   |
| quarantine_root         | /root/autodl-tmp/98_MineSim_QUARANTINE                                |
| cleanup_manifest_root   | /root/autodl-tmp/99_MineSim_CLEANUP_MANIFEST                          |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>绝对不能随意动</strong></p>
<p>runtime semantic/bitmap symlink target、90_MineSim_ARCHIVE、98_MineSim_QUARANTINE、99_MineSim_CLEANUP_MANIFEST、dirty historical workspace、任何 frozen result/lock/bundle、C13 one-time failure证据、C10/C14/C03 qualification locks。任何“整理”都不能覆盖科学 provenance。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 20. 证据来源索引与冲突处理原则

| **证据来源**                                                     | **主要用途**                                                                                                                                     |
|------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------|
| 2026-08-21《全项目阶段性总总结与AI无缝接管手册》                 | 7/26～8/21 baseline/Pure MCTS/J117/FullMine/Fleet/visual/cleanup/Paper1/Value V1 的综合基线。                                                    |
| 2026-08-23 长 transcript \`粘贴的文本 (1)(20260823-141316).txt\` | C13 one-time eval、metric binding failure、replacement blind/pre-reg、C09/C10/C14/C03 主流程。                                                   |
| 2026-08-23 \`...160813.txt\`                                     | C03 A/B static direct checker 451 samples、0 bad、static PASS。                                                                                  |
| 2026-08-23 \`...161256.txt\`                                     | NO-MCTS runner discovery、C13 fix1 parent runner 与历史 causal evidence。                                                                        |
| 2026-08-23 \`...162138.txt\`                                     | parent source contract、helper/env/result schema。                                                                                               |
| 2026-08-23 \`...163434.txt\`                                     | C03 runner derivation/horizon review、attempt1 开始前证据与相关锁。                                                                              |
| 当前本对话终端输出（后续未上传为文件）                           | C03 attempt1 zero-step technical failure、failure freeze、runtime contract fix、manual retry preauth、以及最新 retry1 preauth-binding KeyError。 |
| AI接手文档 / 原项目复现 / 蒙特卡洛实现 / 地图更换等上传包        | 历史细节与原始资产；若与 live/frozen 冲突，降级为历史背景。                                                                                      |

> • 旧 Word 的“当前下一步”只保留历史价值。8/21 写的“V2 interaction/target probe next”已被 8/23 的实际执行覆盖。
>
> • 文件名和路径不是事实本身；必须核 SHA、manifest、JSON 字段、RC、PASS gate。
>
> • 失败不自动等于代码错误，也不自动等于科学 FAIL；先确定 failure domain。
>
> • 生产真值不能从算法实验反推；production drivability、terrain datum、authoring rules 仍需外部权威。

# 21. 快速接手区：下一位 AI 只读这一节即可继续

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>CURRENT_STATE</strong></p>
<p>核心仿真/MCTS/地图/Fleet/视频/cleanup 均已冻结，不重做。Value V1 跨场景失败；Value V2 final-dev model 已冻结但没有有效独立科学评估。C13 one-time eval 因 metric-binding technical failure 已封存且禁止重跑。Replacement 候选 C10/C14 已淘汰，C03 physical/static PASS。C03 causal attempt1 是 0-step technical failure；manual technical retry #1 corrected runner + preauth 已冻结，但 retry1 还没有真正执行。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

| **事项**               | **必须记住**                                                                                                                                                                                                                                |
|------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 正式 repo              | /root/MineSim-Dynamic                                                                                                                                                                                                                       |
| 预期 HEAD              | 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e                                                                                                                                                                                                    |
| Frozen tag             | fullmine-vector-v4-runtime-freeze-20260814                                                                                                                                                                                                  |
| 关键数据 root          | /root/autodl-tmp；优先读 00_MineSim_ACTIVE/current_paths.json（若存在）。                                                                                                                                                                   |
| 已冻结不重做           | IDM baseline、Pure MCTS、J117、FullMine V4、Representative MCTS、Polygon21 Fleet、C04/C11/C06、Native Video V2、cleanup、V2R/zone/dynamic V2V/shadow/data、Value V1 failure、C13 one-time failure、C10/C14 rejection、C03 physical/static。 |
| 当前 HOLD              | C03 causal scientific result；production-authoritative drivability；terrain/Z；V2H；hard pruning；Policy/PUCT；Value-guided MCTS。                                                                                                          |
| MCTS Value integration | False；严禁提前接入。                                                                                                                                                                                                                       |

## 21.1 当前真正 blocker

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>BLOCKER</strong></p>
<p>Retry1 高资源 wrapper 在 PREAUTH BINDING 读取不存在的 `old_attempt_artifacts` key 时 KeyError。该错误发生在写 retry1 START lock 之前，所以 retry1 execution count 仍为 0，corrected runner / manual retry exception / retry1 preauth 不需要重做。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

> • 最可能的 schema mismatch：manual retry exception 生成时使用的是 \`old_attempt_artifacts_preserved\`，而执行 wrapper 读取 \`old_attempt_artifacts\`。这是 wrapper contract bug，必须先用实际 JSON key 只读确认，不凭记忆直接改。
>
> • 当前高资源卡已经没有必要继续开；先降到低资源。
>
> • 不要删除任何 retry1 预授权资产，不要重做 C03 runner，不要重跑 attempt1。

## 21.2 下一步最小行动

> 1\. 低资源、CUDA disabled：只读读取 \`C03_NOMCTS_MANUAL_TECHNICAL_RETRY_EXCEPTION_LOCK_V1.json\` 与 \`C03_NOMCTS_TECHNICAL_RETRY1_PREAUTHORIZATION_V1.json\` 的 top-level keys / nested schema；同时确认 retry1 START/CAPTURE/result/log 仍全部不存在。
>
> 2\. 仅修复执行 wrapper 的 key binding；不得改变 corrected runner SHA、fix lock、exception lock、retry1 preauth、science constants、route、map、bitmap。
>
> 3\. 静态 py_compile / source contract PASS 后，才重新开 80GiB/15CPU 高资源卡，按同一个 retry1 preauth 执行 technical retry \#1 一次。
>
> 4\. retry1 结果分类：protocol_integrity=True 且 causal gate 全满足 → PASS；protocol_integrity=True 但 causal gate 不满足 → SCIENTIFIC FAIL；protocol_integrity=False → TECHNICAL HOLD。任何情况下都不自动第三次执行。

## 21.3 下一步完成标准

| **阶段**                  | **PASS 标准**                                                                                                                                                                                                                                                 |
|---------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 低资源 wrapper schema fix | 实际 JSON key 与 wrapper 绑定一致；retry1 outputs absent；runner/preauth SHA 不变；REPO_UNCHANGED=PASS。                                                                                                                                                      |
| 高资源 retry1 preflight   | memory ≥64GiB；所有 frozen SHA gate PASS；retry1 START/CAPTURE/result/log 在开始前不存在；overall attempt=2、technical retry=1。                                                                                                                              |
| retry1 science PASS       | result parse OK；input hashes、route、constants、initial alignment、timeline、speed、B-reference/controlled-observation 全部 protocol-integrity PASS；physical_overlap=True；causal_conflict_confirmed=True；completed_post_conflict=True；status/PASS=True。 |
| retry1 science FAIL       | protocol_integrity=True，但 causal PASS contract 不满足；冻结真实负结果，C03 淘汰且预注册候选集合耗尽。                                                                                                                                                       |
| retry1 technical HOLD     | protocol_integrity=False；冻结 retry1 technical hold；不自动第三次执行。                                                                                                                                                                                      |

## 21.4 继续前必须先检查

> • pwd / conda / Python；git rev-parse HEAD；git status --short。当前最新失败后未打印最终 REPO_UNCHANGED tail，因此下一位 AI 必须重新核 tracked/staged 状态。
>
> • 确认 \`?? ^C\` 历史异常名仍按原规则处理；不要 git clean。
>
> • 检查 retry1 outputs：\`C03_NOMCTS_TECHNICAL_RETRY1_EXECUTION_STARTED_V1.json\`、capture、retry1 result/log、stdout/stderr/rc 是否均不存在。若任一存在，立即 HOLD，禁止再次执行。
>
> • 核 corrected runner SHA=eba4fbb6...、runtime fix lock=4ff91e19...、manual exception=db7f1df8...、retry1 preauth=471b1714...。
>
> • 不要运行 Value model、Collector 或 MCTS integration；当前 C03 causal gate 尚未完成。

— 文档结束 \| Evidence cutoff: 2026-08-23 current conversation —
