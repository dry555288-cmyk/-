**MineSim-Dynamic**

**全项目阶段性总总结与 AI 无缝接管手册**

**2026-08-26 · C01 静态 Checker 两进程授权前停点版**

| **字段**         | **当前值**                                                                                |
|------------------|-------------------------------------------------------------------------------------------|
| **证据截止**     | 2026-08-26；截至 C01 checker harness runtime-cardinality diagnostic，DIAGNOSTIC_RC=0      |
| **当前真实状态** | HARNESS_DERIVED_PASS / RUNTIME_CARDINALITY_DIAGNOSTIC_PASS / AUTHORIZATION_V2_NOT_CREATED |
| **当前 Gate**    | C01_STATIC_BITMAP_CHECKER_STATIC_REVIEW_TWO_PROCESS_AND_ONE_TIME_AUTHORIZATION_V2         |
| **当前资源**     | LOW；现在不要开高资源卡                                                                   |
| **下一执行资源** | 授权 PASS 后的 authoritative checker execution：HIGH-CPU / 大内存；GPU 不需要             |
| **唯一下一步**   | 上传并执行 C01_CHECKER_STATIC_REVIEW_AND_TWO_PROCESS_AUTH_V2.txt（当前尚未执行）          |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>最重要的状态边界</strong><br />
用户已明确说明：上一条交付的 C01_CHECKER_STATIC_REVIEW_AND_TWO_PROCESS_AUTH_V2.txt 还没有执行。因此当前不存在 Authorization V2、START、checker result 或新的 scientific classification。Authorization 不等于 execution。</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

交接版本：V1｜适用对象：后续 ChatGPT / Codex / 工程执行人员｜正式 repo：/root/MineSim-Dynamic｜数据根：/root/autodl-tmp

# **0. CURRENT_STATE｜一页接手摘要**

| **字段**                  | **当前值**                                                                                                      | **接管解释**                                                |
|---------------------------|-----------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------|
| **EVIDENCE_CUTOFF**       | 2026-08-26；最新已执行证据为 runtime-cardinality diagnostic RC=0                                                | 后续 V2 review/auth 文件尚未执行                            |
| **CURRENT_STAGE**         | Value V3 brand-new independent scene（C01）qualification                                                        | 当前在 static bitmap checker pre-execution                  |
| **CURRENT_GATE**          | C01 static checker 两进程 static review + one-time authorization V2                                             | 当前唯一 Gate                                               |
| **CURRENT_STATUS**        | HARNESS_DERIVED_PASS；CARDINALITY_DIAGNOSTIC_PASS；AUTH_V2_NOT_CREATED                                          | 无 checker 科学结果                                         |
| **LATEST_GIT_HEAD**       | 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e                                                                        | tracked Git clean                                           |
| **CURRENT_EVIDENCE_ROOT** | /root/autodl-tmp/paper1_value_v3_development_only_v1                                                            | 重点子目录见路径速查                                        |
| **LATEST_FROZEN_RESULT**  | C01 static assets postexec freeze + checker harness derivation lock                                             | 静态输入和 harness 已冻结                                   |
| **NEXT_MINIMAL_ACTION**   | LOW：执行 C01_CHECKER_STATIC_REVIEW_AND_TWO_PROCESS_AUTH_V2.txt                                                 | 只做 review/auth，不执行 checker                            |
| **PASS_STANDARD**         | Review PASS + Auth PASS + AUTHORIZED_NOT_STARTED + process launches=2 + checker calls=2 + checker not executed  | check root/evidence 仍应不存在                              |
| **RESOURCE_REQUIRED**     | LOW                                                                                                             | 下一真实 checker execution 才需要 HIGH-CPU/内存，GPU 不需要 |
| **DO_NOT_REPEAT**         | 不得重跑训练、C01 scene/static asset generation、builder、harness derivation                                    | 不得手工绕过 authorization/START                            |
| **HOLD_ITEMS**            | C01 bitmap qualification、NO-MCTS causal qualification、Value V3 independent evaluation、MCTS Value integration | 均尚未得到当前 C01 结果                                     |
| **LATEST_HANDOFF**        | MineSim-Dynamic_全项目阶段性总总结与AI无缝接管手册_2026-08-26_C01静态Checker两进程授权前停点版.docx             | 本文件是新的当前状态入口                                    |

## **0.1 30 秒解释**

- **神经网络训练本身已经结束并冻结：**2356-root episode-aware LOSO 正式训练技术 PASS、3/3 scene win、DEVELOPMENT_READY=True；当前不是继续训练。

- **当前工作已经进入独立场景验证：**C01 已完成 physical/scene/static-asset 链，checker 输入和 harness 也已经派生。

- **最新诊断只解决执行基数：**derived harness 通过 --vehicle A/B 运行；一个进程只检查一个候选，因此完整检查需要 A、B 两个顺序进程。

- **当前尚未授权、更未执行 checker：**C01 static bitmap qualification 仍为 NOT_EVALUATED。

- **下一步仍是 LOW：**只冻结两进程 one-time authorization；真正 checker execution 后续单独进行。

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>当前停点的最短描述</strong><br />
C01 static assets 与 checker harness 已冻结；两进程执行模型已静态确认；Authorization V2 尚未创建。</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# **1. 文档控制、证据等级与冲突处理**

| **项目**                   | **当前定义**                                                                                                                           |
|----------------------------|----------------------------------------------------------------------------------------------------------------------------------------|
| **事实优先级**             | 最新 AutoDL 终端 / Git / 源码 / SHA / 实际输出 \> frozen result/manifest/lock/bundle \> 本交接 Word \> 历史 Word \> 计划 \> 模型记忆。 |
| **本版证据截止**           | 截至用户上传的 C01_CHECKER_HARNESS_RUNTIME_CARDINALITY_DIAGNOSTIC 终端全文，DIAGNOSTIC_RC=0。                                          |
| **未执行声明**             | C01_CHECKER_STATIC_REVIEW_AND_TWO_PROCESS_AUTH_V2.txt 已在本对话生成，但用户明确说明尚未执行；AutoDL 是否已上传该文件也未验证。        |
| **未验证规则**             | 缺少直接证据的一律写 HOLD / NOT VERIFIED，不根据常识补齐。                                                                             |
| **失败分类**               | 严格区分 static-review assertion、harness contract、technical launch、scientific result。文件存在不等于 PASS。                         |
| **ChatGPT 与 AutoDL 文件** | ChatGPT 中存在的 DOCX/TXT 不等于 AutoDL 中已存在；只有用户上传并由终端 SHA/readback 证明后，才能称云端现存。                           |
| **本版覆盖范围**           | 历史主线简要整合；重点完整覆盖 2356-root closure、独立场景协议、C01 scene/static/checker harness 链和当前停点。                        |

## **1.1 本版主要证据源**

- 最新 AutoDL 终端全文：C01 checker harness runtime-cardinality diagnostic（DIAGNOSTIC_RC=0）。

- C01 checker harness 派生结果与 SHA：harness / transformation meta / derivation lock。

- C01 static asset postexec freeze、A/B static scenarios、static manifest。

- Checker input binding、harness parent comparison、Strategy V2。

- 2026-08-25 2356-root 神经网络阶段性交接文档与 2026-08-24/25 全项目手册，用于历史主线和已冻结事实。

- 本对话中连续的 AutoDL 终端日志、SHA gate、START/CAPTURE/freeze 结果。

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>严谨边界</strong><br />
本次没有执行 AutoDL 全盘 live inventory，也没有核验本交接 DOCX 是否已上传云端。路径 absent 只说明当前 Gate 前的 namespace guard，并不等于删除。</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## **1.2 推荐阅读顺序**

1.  先读第 0 节 CURRENT_STATE，明确当前 Gate、资源和禁止事项。

2.  再读第 5～7 节，掌握 Value V3 → C01 → static checker 的当前链。

3.  执行人员必须读第 10、11、14 节：路径/SHA、资源规则、DO_NOT_REPEAT。

4.  只有出现 SHA 冲突或 provenance 不清时，才回查第 2～4 节历史主线。

5.  最后读“快速接手区”，按一个最小 Gate 继续。

# **2. 项目主线总览（按真实演进组织）**

| **阶段**                 | **状态**                                       | **当前真实结论**                                                                                    |
|--------------------------|------------------------------------------------|-----------------------------------------------------------------------------------------------------|
| **MineSim 复现**         | **PASS / FROZEN**                              | IDM baseline、replay、closed-loop 基础环境已建立；不重做。                                          |
| **蒙特卡洛 / Pure MCTS** | **PASS / FROZEN**                              | 真实 MineSim online closed-loop、search/reward/trajectory adapter/controller 链已跑通。             |
| **单车**                 | **PASS / FROZEN**                              | J117 423-step 单车与 FullMine representative Pure MCTS 3/3。                                        |
| **双车冲突场景**         | **PASS / FROZEN**                              | NO-MCTS causal conflict、双受控运行边界与真实冲突场景。                                             |
| **FullMine 新地图**      | **PASS / FROZEN**                              | Vector V2 semantic + Vector V4 bitmap/runtime/planner；HEAD 112d2bd。                               |
| **Fleet-MCTS**           | **PASS + 负结果并存**                          | Polygon21 5/5；cross-scene C04/C06 成功；C11 安全死锁负结果必须保留。                               |
| **多种子 / cross-scene** | **FROZEN**                                     | C04/C11/C06 development collection、独立 replacement qualification 与 blind protocol。              |
| **原生可视化**           | **PASS / 部分 HOLD**                           | Native Video V2 final；部分 showcase V3 历史未收口。                                                |
| **云端整理**             | **PASS / COMPLETE**                            | 历史证据为 move/isolate/archive；科研文件 actual delete=0；后续删除仍需独立授权。                   |
| **神经网络**             | Value V3 DEVELOPMENT READY；独立场景验证进行中 | Value V2 science FAIL 已关闭；2356-root Value V3 3/3 PASS；当前推进 C01 independent qualification。 |

## **2.1 当前最重要的科学口径**

- Value V3 可以称为 development candidate ready，但不能称为 independent-generalization PASS、production ready 或 MCTS-integrated。

- C01 目前只有 physical/scene/static-assets/harness 准备链 PASS；authoritative bitmap checker 尚未运行，所以 C01 static qualification 仍未评估。

- Historical C03/C13 只用于算法与 harness provenance，不能把它们的科学结果复用为 C01 结论。

- CollisionLookup 是 secondary diagnostic；当前 frozen V4 bitmap 上的 XG90G physical footprint 才是 static checker 的 primary truth。

- Scientific FAIL 是结果，不是必须修成 PASS 的 Bug；Technical FAIL 先定位 fault domain，不自动重试。

# **3. 运行架构、核心调用链与边界**

**MineSim 主运行链**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>run_simulation.py<br />
→ SimulationsRunner._initialize()<br />
→ EnvironmentSimulation.initialize()<br />
→ Scenario / Map loader<br />
→ Planner.initialize()<br />
→ Planner.compute_planner_trajectory()<br />
→ TwoStageController.update_state()<br />
→ LQR / iLQR trajectory tracking<br />
→ KinematicBicycleModel.propagate_state()<br />
→ Agent Update Policy / Observation<br />
→ SimulationHistory / metrics / log<br />
→ next frame</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

| **边界**                  | **当前处理规则**                                                                                |
|---------------------------|-------------------------------------------------------------------------------------------------|
| **Planner 与执行器**      | 搜索或规划轨迹合法，不等于 Controller/KBM 必然可实现；故障必须分层。                            |
| **双车 truth**            | B 的真实状态不得由 A history 推断；每个受控车辆的 observation/history 必须独立。                |
| **受控与 external actor** | 同一车辆不能同时作为 controlled ego 与 external actor。                                         |
| **空间相交与时间冲突**    | 路径几何相交不自动等于 temporal conflict；必须有时序/causal evidence。                          |
| **safe 与 success**       | 无碰撞不等于任务完成；deadlock 可以是 scientific FAIL。                                         |
| **Static bitmap truth**   | XG90G footprint on frozen V4 bitmap 是 primary truth；CollisionLookup 是 secondary diagnostic。 |
| **地图口径**              | Research/DEV map 不得表述为 production-authoritative HD map 或官方可行驶真值。                  |

# **4. 神经网络主线：Value V2 → Value V3 → 独立场景**

## **4.1 Value V2 独立验证已关闭**

- Value V2 在 C03 independent validation 上科学 FAIL，post-failure closure 已冻结。

- 结论是 DO_NOT_INTEGRATE；禁止重跑、retune 或用 C03 重新选架构。

- 该失败保留为真实科学证据，不应被后续 Value V3 进展覆盖或“修成 PASS”。

## **4.2 固定 Value V3 与 coverage expansion**

| **阶段**                         | **技术结果**                                    | **科学结果**                                | **决策**                                                  |
|----------------------------------|-------------------------------------------------|---------------------------------------------|-----------------------------------------------------------|
| 原固定 9-fold                    | 9/9 folds PASS                                  | C04/C06 win，C11 fail；2/3                  | 不改架构；扩充 development coverage                       |
| 2052-root expanded Retry1        | RC=0；9 folds                                   | 仍为 2/3；C11 fail                          | 继续查 heldout C11 training support，不允许 Retry2/retune |
| 2356-root episode-aware 正式训练 | RC=0；9 checkpoints + 9 predictions + 1 summary | 3/3 scene win；primary=True；secondary=True | DEVELOPMENT_READY=True；进入 independent scene protocol   |

## **4.3 2356-root 冻结训练协议**

| **项目**            | **冻结值**                                                                          |
|---------------------|-------------------------------------------------------------------------------------|
| **Dataset**         | 2356 roots；37696 action rows；6 episodes；identity=(scene, episode_uid, root_step) |
| **Model**           | ActionConditionedValueV3PairwiseRank；12 → 64 → 64 → 16                             |
| **Objective**       | ROOT_NORMALIZED_WEIGHTED_PAIRWISE_LOGISTIC                                          |
| **Split**           | LEAVE_ONE_SCENE_OUT                                                                 |
| **Seeds**           | 20260824 / 20260825 / 20260826                                                      |
| **Epochs / LR**     | 600 / 0.001                                                                         |
| **Best-seed / HPO** | False / False                                                                       |
| **Readiness**       | 3/3 scene win；DEVELOPMENT_READY=True；不是独立泛化结论                             |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>永久训练边界</strong><br />
不得重跑 2356-root one-time training；不得 best-seed、retune、改 normalization、loss、LR、epoch、scene weight；不得把 9 个 LOSO checkpoint 当作已冻结的全场景 deployment model。</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## **4.4 2356-root postexec closure 与 independent-scene 入口**

- Closure sidecar 最终已读回 FROZEN_PASS，分类为 TECHNICAL_PASS_SCIENTIFIC_PASS_DEVELOPMENT_READY。

- Blind rule 冻结：历史暴露 source index 排除后，以 ascending integer source_index 选择第一个 eligible identity；禁止人工 override 或 performance screening。

- Canonical physical pool 首次 reveal 后没有全新 eligible source；因此进入 preselection raw-source extension protocol。

- Raw preselection universe 中未暴露 identities 为 \[1, 2, 5, 7, 8\]；最终 C01/source_index=1 进入独立场景链。

| **关键对象**            | **SHA256**                                                       | **状态**                      |
|-------------------------|------------------------------------------------------------------|-------------------------------|
| 2356 postexec closure   | f0d73da76d492a87aa73793834650d1f61b57876849047cb554cf95af7fc538d | **FROZEN PASS**               |
| Blind selection rule    | 55a4d8c69a751330e790467fe3d38d15f0a166381bf4194d92c768ccf93788ec | **FROZEN**                    |
| Exact PHYS binding lock | 4191d7e0a9cd413a5e31fc8f4a88d7231e8a195fa4b3602163d043f8752f4975 | **FROZEN**                    |
| Canonical PHYS          | 6c5c0e85837afc27c9a96948f35e39fa780db1e62ed4dff31762e433454a2317 | **FROZEN**                    |
| Initial pool reveal     | 6ed0f9b810a7a9e67668f20d5a35c79afaa39ccf53244de7ce5dcf16f306c63e | NO NEW ELIGIBLE；转 extension |

# **5. C01 独立场景：physical、scene 与 static asset 链**

## **5.1 C01 选择与科学边界**

| **项目**                   | **当前事实**                                                                    |
|----------------------------|---------------------------------------------------------------------------------|
| **Scene identity**         | C01；source_index=1                                                             |
| **选择规则**               | 来自冻结 blind/extension protocol；不是 performance screening，不允许人工换候选 |
| **Physical qualification** | PRESERVED_FROZEN_PASS                                                           |
| **Scene generation**       | FROZEN_PASS                                                                     |
| **地图/路线变更**          | False；不得改 map/route/start/goal/conflict/scan interval                       |
| **Value V3 forward**       | False；尚未授权                                                                 |
| **MCTS Value integration** | False / FORBIDDEN                                                               |

| **C01 对象**                | **路径/标识**                                                                 | **SHA256**                                                       |
|-----------------------------|-------------------------------------------------------------------------------|------------------------------------------------------------------|
| Generation postexec freeze  | .../independent_scene_c01_static_generation_retry2_postexec_freeze_v1/...json | 8830e3c2f5cea527441235be99dccceda6b999012a5a3575e7baf543e56ab499 |
| Scenario                    | Scenario-fullmine-v4-cross-scene-c01-dual-aligned-v1.json                     | ea7e813768ffd58e705d72abe44a6a15e802f4285ff4ed9943c0e143b7fbf950 |
| Source manifest             | cross_scene_c01_scenario_manifest_v1.json                                     | 0fb47416d137c4dce66e55d4b52d5ffec6e89d53281d505b17d449523384b19b |
| Static qualification bundle | C01_STATIC_QUALIFICATION_BUNDLE_V1.json                                       | 1a6e0970bbc667d687ca6f65fe1fae776aafb92b848c94e1fab71112af6186a5 |

## **5.2 Static asset builder 的一次性执行**

- 从冻结 C03/C14/generic builder lineage 派生 C01 builder，只改变 C01 identity/manifest 绑定；helper algorithm 和 static policy 不变。

- 一次性 authorization 已消费；START → namespace repair → builder 仅运行 1 次 → CAPTURE。

- builder RC=0，stderr 空，生成 2 个 static scenario + 1 个 static manifest，随后 postexec freeze。

- builder rerun、retry、static asset regeneration 均未授权，永久禁止直接重跑。

| **对象**               | **SHA256**                                                       | **状态**        |
|------------------------|------------------------------------------------------------------|-----------------|
| Builder parent binding | b1344d087d460cc9f01c361f9569cf733cfcfd25f32053290cb0987cb9b0c766 | **FROZEN PASS** |
| Derived static builder | 3a111138dac483871a1eac2c7b5ede71d99617d5efa9ba0bb3c6e0a1f533803e | **FROZEN**      |
| Transformation meta    | 5f74b0aeee3d86df8d19ec2c763c9f4185a0c4e1ffade6183f9fd5a53a0510ac | **FROZEN**      |
| Derivation lock        | 3469c85a9b76134837848d30f394734aa8d87416843710ac0b802e9074005e5e | **FROZEN**      |
| One-time builder auth  | 37a265e3c8eaac491433ea6486e8aa18eb586798b38887015e23d72648a10772 | **CONSUMED**    |
| Harness repair         | 7a46ac54b856274ef5d5e1f7472aac52f156f39397f9a91e3b4189351c64b457 | **FROZEN**      |
| Builder START          | a8a686f8b0d6a31051ae5eacfef11e19df658e381905716ef82e8abe80dd4bfe | **CONSUMED**    |
| Builder CAPTURE        | 330ef9129d567c16b347a2a0e1458041a83462cb1b555143256165f8b2b21f05 | **RC=0 / PASS** |

## **5.3 C01 static assets 的冻结内容**

| **候选** | **Expected route**        | **Start s** | **Conflict s** | **Goal s** | **Scan** | **Scenario SHA**                                                 |
|----------|---------------------------|-------------|----------------|------------|----------|------------------------------------------------------------------|
| C01-A    | path-000120 → path-000466 | 135.662400  | 185.662400     | 200.662400 | 65.0 m   | 6d78363192a31cd3c04beb8ab07d37766e3ffd902ab2a2aacd53acb7c5d81bd3 |
| C01-B    | path-000370 → path-000491 | 17.405307   | 67.405307      | 82.405307  | 65.0 m   | d57a08d3a83500b756cb0de3a4e53dfe5f1302c75c13b5b41561eee8bd396459 |

| **冻结对象**                 | **SHA256**                                                       | **边界**                                |
|------------------------------|------------------------------------------------------------------|-----------------------------------------|
| Static manifest              | 64d9db319cf3673743f0fe0832e5bc5bbb38459c4b8d443a63aae702bc1562bb | **PASS；candidate_count=2**             |
| Static asset postexec freeze | b834db1efbb8295eadd5a2c8dbe49f5038d1343799a6c3f0b8c4e46b8560caf9 | **FROZEN_STATIC_ASSETS_GENERATED_PASS** |

# **6. C01 authoritative static bitmap checker 链**

## **6.1 Checker 与 canonical runtime inputs**

| **输入**              | **路径**                                                                                                                 | **SHA256**                                                       |
|-----------------------|--------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------|
| Authoritative checker | /root/autodl-tmp/fullmine_v4_representative_coverage_v1/static_xg90g_drivability_gate_v1.py                              | 41e7f73708c52fd0a7d4d84485ec066a98803ac10ea17f4abbeaf322e312aa24 |
| Canonical bitmap      | /root/autodl-tmp/fullmine_vector_v2_targeted_runtime/maps/bitmap/geojson_full_mine_vector_v2_dev_bitmap_mask.png         | 51abcd5a86e5c510204a5dacc873691506d721f98982ab7f98585d4e0f7efdd0 |
| Canonical semantic    | /root/autodl-tmp/fullmine_vector_v2_targeted_runtime/maps/semantic_map/geojson_full_mine_vector_v2_dev_semantic_map.json | b85a3d8b28f2252ecb5bda179d514573f6333079def838cd048566f556d95cd0 |
| Collision lookup      | /root/MineSim-Dynamic/devkit/sim_engine/environment_manager/collision_lookup.py                                          | 10c1d1339e742ca893fedb4aa51402addfba82e16e08f68339ea35d35ba3043b |

- Checker source modification is not authorized；bitmap/semantic/collision lookup 均不得改变。

- sample spacing、vehicle geometry、route、candidate selection、physical result 都不得修改。

- 历史 C03/C13 结果只提供 algorithm/harness provenance，不可直接复制 C01 outcome。

## **6.2 Harness parent 选择与 Strategy V2**

| **候选 parent**   | **结论** | **原因**                                                                                                                                 |
|-------------------|----------|------------------------------------------------------------------------------------------------------------------------------------------|
| C04 direct runner | REJECTED | 存在第二条 retry_manifest → gate.run_candidate 路径，超出 C03 每候选一次 checker precedent。                                             |
| C13 V1            | REJECTED | C13-B expected planner route contract 被截断，缺少最后一个 path token。                                                                  |
| C13 V2            | SELECTED | 单 direct call、无 retry；仅修正 planner-route expectation，scenario/map/start/goal/conflict/scan/planner source/source route 均未改变。 |

| **对象**                  | **SHA256**                                                       | **状态**        |
|---------------------------|------------------------------------------------------------------|-----------------|
| Checker input binding     | a70b68e30b4210069079f77370dd949753576b3c6bfdfb2cafff992527ae7fbd | **FROZEN PASS** |
| Harness parent comparison | 0ce13f6449e55061728aa6a0ba321099f330fb02ad28feb81c7d921a1ab93b21 | **FROZEN PASS** |
| Strategy V2               | 19f42890b6fad2627f0af15e0e70f992ee342ff48df40f1fd4c02ce6b12002d9 | C13 V2 SELECTED |

## **6.3 Derived C01 checker harness**

| **对象**                            | **SHA256**                                                       | **状态**                         |
|-------------------------------------|------------------------------------------------------------------|----------------------------------|
| run_c01_static_bitmap_checker_v1.py | 9cc0d688fccce62bd25d29f49412673a91078dce29e49e2e39cea22295c2e1c2 | **DERIVED / NOT EXECUTED**       |
| Transformation meta                 | d29e3c0f7960cfa1684e945e495fbba854e00b48eb60036164152cf48d320510 | **FROZEN**                       |
| Derivation lock                     | 1ff4aa2a7e31bd00f7af529babaead7b039ab0a9d050e432ea66c68296d72be8 | **NOT AUTHORIZED FOR EXECUTION** |
| Harness SHA256SUMS                  | 27273844987de1589e8d38a107163eb31d1d78b48a290e3a828bcd8bc7010e4f | **READBACK PASS**                |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>当前不可误读</strong><br />
Harness 已派生并冻结，不等于 harness 已运行；Derivation lock 明确为 STATIC_DERIVATION_PASS_NOT_AUTHORIZED_FOR_EXECUTION。</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# **7. Runtime cardinality diagnostic 与当前精确停点**

## **7.1 诊断得到的真实执行模型**

**静态确定的两进程执行基数**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>Process 1<br />
/root/miniconda3/envs/minesim/bin/python run_c01_static_bitmap_checker_v1.py --vehicle A<br />
→ gate.run_candidate("cross-scene-c01-A", manifest, semantic)<br />
→ cross-scene-c01-A_static_result_highres_v1.json<br />
<br />
Process 2<br />
/root/miniconda3/envs/minesim/bin/python run_c01_static_bitmap_checker_v1.py --vehicle B<br />
→ gate.run_candidate("cross-scene-c01-B", manifest, semantic)<br />
→ cross-scene-c01-B_static_result_highres_v1.json</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

| **诊断项**              | **真实结果**                                                    |
|-------------------------|-----------------------------------------------------------------|
| **main() CLI**          | --vehicle，required=True，choices=\[A,B\]                       |
| **每个 harness 进程**   | 只运行一个 vehicle / 一个 candidate                             |
| **每进程 checker call** | 1 次 gate.run_candidate(cid, manifest, semantic)                |
| **完整 C01 检查**       | 需要 2 个顺序 harness process launches：A → B                   |
| **结果数**              | 每进程 1 个；总计 2 个 result JSON                              |
| **Retry path**          | 不存在 retry_manifest                                           |
| **Output root**         | harness 不执行 mkdir；runner 必须在 START 后、process 1 前创建  |
| **Latest diagnostic**   | DIAGNOSTIC_RC=0；只读；无文件修改、无授权、无 checker execution |

## **7.2 当前 namespace 状态**

| **对象**                | **当前状态** | **路径**                                                                                                                    |
|-------------------------|--------------|-----------------------------------------------------------------------------------------------------------------------------|
| C01 static check root   | **ABSENT**   | /root/autodl-tmp/paper1_value_v3_development_only_v1/independent_scene_c01_static_bitmap_check_v1                           |
| Authorization V2 root   | **ABSENT**   | /root/autodl-tmp/paper1_value_v3_development_only_v1/independent_scene_c01_static_bitmap_checker_execution_authorization_v2 |
| Execution evidence root | **ABSENT**   | /root/autodl-tmp/paper1_value_v3_development_only_v1/independent_scene_c01_static_bitmap_checker_execution_evidence_v1      |
| Checker/harness process | **ABSENT**   | 无相关 Python process                                                                                                       |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>当前状态结论</strong><br />
截至交接：只读 runtime-cardinality diagnostic PASS；Authorization V2 尚未创建；START、check root、A/B result、CAPTURE 均不存在。</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# **8. 当前唯一 Gate 与尚未执行的交付文件**

| **字段**                 | **内容**                                                                          |
|--------------------------|-----------------------------------------------------------------------------------|
| **文件名**               | C01_CHECKER_STATIC_REVIEW_AND_TWO_PROCESS_AUTH_V2.txt                             |
| **ChatGPT artifact SHA** | 21f2f4cd7be92b1facec3d6cbce5bee6959a985844e83722b0c8140ef4107573                  |
| **建议 AutoDL 目标路径** | /root/autodl-tmp/C01_CHECKER_STATIC_REVIEW_AND_TWO_PROCESS_AUTH_V2.txt            |
| **当前状态**             | DELIVERED_IN_CHAT / USER_CONFIRMED_NOT_EXECUTED / AUTODL_UPLOAD_HOLD              |
| **当前资源**             | LOW；4090 不用开                                                                  |
| **本步作用**             | 重新做 exact two-process static review，并冻结 one-time Authorization V2          |
| **本步明确不做**         | 不创建 START、不创建 check root、不运行 A/B harness、不执行 authoritative checker |

**下一最小执行命令（用户当前尚未执行）**

| bash /root/autodl-tmp/C01_CHECKER_STATIC_REVIEW_AND_TWO_PROCESS_AUTH_V2.txt |
|-----------------------------------------------------------------------------|

## **8.1 本步 PASS 标准**

- \`REVIEW_AUTH_V2_RC=0\`。

- \`STATIC_REVIEW_GATE=PASS\` 与 \`AUTHORIZATION_GATE=PASS\`。

- \`AUTHORIZATION_CONSUMED=False\`；\`HARNESS_EXECUTED=False\`；\`STATIC_CHECKER_EXECUTED=False\`。

- \`EXECUTION_BUNDLE_COUNT_AUTHORIZED=1\`。

- \`HARNESS_PROCESS_LAUNCH_COUNT_AUTHORIZED=2\`。

- 进程顺序固定为 A → B；每进程 checker call=1；总 checker calls=2。

- check root、result A/B、execution evidence root 在授权结束时仍不存在。

## **8.2 本步 FAIL 处理**

- 保存并上传完整终端输出；明确 failure 属于 static review、schema、SHA、namespace 还是 authorization readback。

- 不自动重跑，不手工创建 authorization，不预创建 check root/evidence。

- 只定位当前 fault domain；不得改 checker、bitmap、semantic、route、vehicle geometry 或 static assets。

- 重新定义最小 PASS 标准后再给一个诊断 Gate。

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>不要越过本步</strong><br />
即使已知两进程模型，也不得直接运行 --vehicle A/B。必须先让 Authorization V2 通过并保持 AUTHORIZED_NOT_STARTED。</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# **9. 当前阶段的重要失败、原因与永久经验**

| **现象/领域**               | **原因**                                                                      | **最终处理**                                                                 | **以后禁止重复**                                   |
|-----------------------------|-------------------------------------------------------------------------------|------------------------------------------------------------------------------|----------------------------------------------------|
| Closure schema binding      | readback 从错误 nested key 取 development_ready/decision                      | 改为 summary.V3_DEVELOPMENT_READY / summary.DECISION；只改 sidecar           | 不要把 schema mismatch 当 scientific fail          |
| torch.load compatibility    | PyTorch 2.6+ 默认 weights_only=True，历史可信 checkpoint 含 numpy reconstruct | sidecar 指定 weights_only=False；不改 checkpoint/训练                        | 只对可信冻结 checkpoint 使用；不扩大修改           |
| Canonical pool no eligible  | physical qualified pool \[6,9,11\] 全被历史/development exclusion 排除        | 冻结 HOLD 后审计 raw preselection universe，进入 extension protocol          | 不得改 blind rule 或按性能挑 candidate             |
| Builder raw-string review   | MANIFEST 路径由相邻字符串拼接，源码 substring 不连续                          | 改用 AST semantic binding                                                    | 路径审计优先 AST，不靠脆弱字符串计数               |
| Builder output namespace    | 历史 builder 预期 STATICDIR 已存在，不自行 mkdir                              | 冻结 pre-START harness repair；START 后 mkdir、process 前确认 outputs absent | 不要为此改 builder 科学逻辑                        |
| Harness parent ambiguity    | C04/C13 V1/V2 都能直接调用 checker                                            | C04 因 retry 路径淘汰；C13 V1 因 route contract 截断淘汰；选 C13 V2          | 不得凭源码相似度直接选 parent                      |
| Harness derivation MANIFEST | parent absolute MANIFEST 是 AST Constant，但不是连续 source substring         | AST 定位整个 assignment 并替换                                               | 不要 raw replace evaluated path                    |
| Candidate prefix count      | C13 prefix 同时用于 candidate id 与 output filename，共 2 处                  | 要求 2→2 AST exact patch                                                     | 不要假设 identity literal 只出现一次               |
| Static review cardinality   | 错误假设一个 process 内有 A/B for-loop                                        | runtime-cardinality diagnostic 证明 main CLI 每进程一个 vehicle              | 执行基数必须从 entrypoint/argparse/call graph 恢复 |

## **9.1 最近两次 static review FAIL 的精确含义**

- 原 review：要求 run_candidate 必须位于字面量 \[A,B\] 循环，发生 assertion；未创建 authorization。

- FIX1：放宽为 manifest loop，但诊断显示 run_candidate 的 ancestor for count=0；再次在 static review 停止。

- 这两次都没有创建 check root、auth root、evidence root，也没有执行 harness/checker。

- 最终诊断确认：A/B 由 CLI 参数选择，必须两个独立进程。

# **10. 关键路径速查**

| **对象**                    | **路径**                                                                       | **作用/边界**                                        |
|-----------------------------|--------------------------------------------------------------------------------|------------------------------------------------------|
| **正式仓库**                | /root/MineSim-Dynamic                                                          | Git tracked source；不要把历史 workspace 当正式 repo |
| **大文件/实验根**           | /root/autodl-tmp                                                               | 数据、日志、sidecar、模型、结果                      |
| **Value V3 root**           | /root/autodl-tmp/paper1_value_v3_development_only_v1                           | 当前主工作区                                         |
| **FullMine runtime**        | /root/autodl-tmp/fullmine_vector_v2_targeted_runtime                           | semantic/bitmap runtime                              |
| **Cross-scene root**        | /root/autodl-tmp/fullmine_v4_fleet_cross_scene_v1                              | 历史 C03/C13 provenance                              |
| **C01 static prep**         | .../independent_scene_c01_static_bitmap_prep_v1                                | A/B static assets + manifest；已冻结                 |
| **Static asset postfreeze** | .../independent_scene_c01_static_asset_generation_postexec_freeze_v1           | b834db...                                            |
| **Checker binding**         | .../independent_scene_c01_static_bitmap_checker_binding_v1                     | a70b68...                                            |
| **Parent comparison**       | .../independent_scene_c01_static_bitmap_harness_parent_comparison_v1           | 0ce13f...                                            |
| **Strategy V2**             | .../independent_scene_c01_static_bitmap_checker_harness_derivation_strategy_v2 | 19f428...                                            |
| **Derived harness**         | .../independent_scene_c01_static_bitmap_checker_harness_v1                     | 9cc0d...；not executed                               |
| **Planned check root**      | .../independent_scene_c01_static_bitmap_check_v1                               | 当前 ABSENT；不得提前创建                            |
| **Planned auth V2 root**    | .../independent_scene_c01_static_bitmap_checker_execution_authorization_v2     | 当前 ABSENT                                          |
| **Planned evidence root**   | .../independent_scene_c01_static_bitmap_checker_execution_evidence_v1          | 当前 ABSENT                                          |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>路径纪律</strong><br />
大数据、结果和 sidecar 放 /root/autodl-tmp；正式 repo 只保留必要源码。路径 missing 不等于删除，目录美观不优先于科研可恢复性。</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# **11. 当前关键 SHA / 状态矩阵**

| **对象**                   | **SHA256**                                                       | **当前状态**       |
|----------------------------|------------------------------------------------------------------|--------------------|
| Git HEAD                   | 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e                         | **FROZEN / CLEAN** |
| C01 scenario               | ea7e813768ffd58e705d72abe44a6a15e802f4285ff4ed9943c0e143b7fbf950 | **FROZEN**         |
| C01 source manifest        | 0fb47416d137c4dce66e55d4b52d5ffec6e89d53281d505b17d449523384b19b | **FROZEN**         |
| C01 bundle                 | 1a6e0970bbc667d687ca6f65fe1fae776aafb92b848c94e1fab71112af6186a5 | **FROZEN**         |
| C01 static A               | 6d78363192a31cd3c04beb8ab07d37766e3ffd902ab2a2aacd53acb7c5d81bd3 | **FROZEN**         |
| C01 static B               | d57a08d3a83500b756cb0de3a4e53dfe5f1302c75c13b5b41561eee8bd396459 | **FROZEN**         |
| C01 static manifest        | 64d9db319cf3673743f0fe0832e5bc5bbb38459c4b8d443a63aae702bc1562bb | **FROZEN PASS**    |
| Static postexec freeze     | b834db1efbb8295eadd5a2c8dbe49f5038d1343799a6c3f0b8c4e46b8560caf9 | **FROZEN PASS**    |
| Authoritative checker      | 41e7f73708c52fd0a7d4d84485ec066a98803ac10ea17f4abbeaf322e312aa24 | UNCHANGED          |
| Canonical semantic         | b85a3d8b28f2252ecb5bda179d514573f6333079def838cd048566f556d95cd0 | UNCHANGED          |
| Canonical bitmap           | 51abcd5a86e5c510204a5dacc873691506d721f98982ab7f98585d4e0f7efdd0 | UNCHANGED          |
| Collision lookup           | 10c1d1339e742ca893fedb4aa51402addfba82e16e08f68339ea35d35ba3043b | UNCHANGED          |
| Checker input binding      | a70b68e30b4210069079f77370dd949753576b3c6bfdfb2cafff992527ae7fbd | **FROZEN PASS**    |
| Harness comparison         | 0ce13f6449e55061728aa6a0ba321099f330fb02ad28feb81c7d921a1ab93b21 | **FROZEN PASS**    |
| Strategy V2                | 19f42890b6fad2627f0af15e0e70f992ee342ff48df40f1fd4c02ce6b12002d9 | **FROZEN PASS**    |
| Derived harness            | 9cc0d688fccce62bd25d29f49412673a91078dce29e49e2e39cea22295c2e1c2 | **NOT EXECUTED**   |
| Harness meta               | d29e3c0f7960cfa1684e945e495fbba854e00b48eb60036164152cf48d320510 | **FROZEN**         |
| Harness derivation lock    | 1ff4aa2a7e31bd00f7af529babaead7b039ab0a9d050e432ea66c68296d72be8 | **NOT AUTHORIZED** |
| Pending review/auth V2 TXT | 21f2f4cd7be92b1facec3d6cbce5bee6959a985844e83722b0c8140ef4107573 | **NOT EXECUTED**   |

## **11.1 关键对象状态矩阵**

| **对象**                         | **状态**                         | **解释**                  |
|----------------------------------|----------------------------------|---------------------------|
| 2356-root Value V3 training      | **CONSUMED / FROZEN PASS**       | 绝对不得重跑              |
| 2356 postexec closure            | **FROZEN PASS**                  | Development-ready closure |
| C01 blind/physical/scene         | **FROZEN PASS**                  | source_index=1            |
| C01 static asset generation      | **CONSUMED / FROZEN PASS**       | 不得 regenerate           |
| Checker input binding            | **FROZEN PASS**                  | checker/map inputs exact  |
| Harness Strategy V2              | **FROZEN PASS**                  | C13 V2 parent             |
| C01 derived harness              | **STATIC DERIVATION PASS**       | not authorized/executed   |
| Runtime cardinality diagnostic   | **PASS**                         | 2 processes: A then B     |
| Static review/auth V2            | **NOT STARTED**                  | 当前唯一 Gate             |
| Authoritative checker execution  | **NOT AUTHORIZED / NOT STARTED** | future HIGH-CPU           |
| C01 bitmap qualification         | **NOT EVALUATED**                | HOLD                      |
| C01 NO-MCTS causal qualification | **NOT AUTHORIZED**               | HOLD                      |
| Value V3 independent evaluation  | **NOT AUTHORIZED**               | HOLD                      |
| MCTS Value integration           | **FALSE / FORBIDDEN**            | HOLD                      |

# **12. 环境、资源与统一执行规范**

| **资源等级** | **适用范围**                                             | **当前判断**                               |
|--------------|----------------------------------------------------------|--------------------------------------------|
| LOW          | SHA/JSON/AST/static review/authorization/freeze/document | 当前 Gate；现在使用                        |
| HIGH-CPU     | 长 MineSim、bitmap checker、大内存/长 CPU、多个顺序候选  | 授权 PASS 后 checker execution；GPU 不需要 |
| HIGH-GPU     | 正式神经网络训练或明确 CUDA forward                      | 当前禁止/不需要                            |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>资源提醒</strong><br />
现在仍然是 LOW，不要因为“下一步以后可能需要高资源”提前开卡。真实 checker execution 才切 HIGH-CPU/内存；即便使用带 4090D 的实例，也保持 CUDA_VISIBLE_DEVICES=""，仅使用 CPU/RAM。</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

**所有当前 static/checker 任务的固定环境前缀**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>cd /root/MineSim-Dynamic<br />
source /root/miniconda3/etc/profile.d/conda.sh 2&gt;/dev/null || true<br />
conda activate minesim<br />
<br />
export PYTHONPATH=/root/MineSim-Dynamic<br />
export PYTHONDONTWRITEBYTECODE=1<br />
export CUDA_VISIBLE_DEVICES=""</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## **12.1 长任务与交互安全**

- 长 CPU 仿真/checker 执行使用普通 terminal 或 screen，独立 log、RC、START、CAPTURE；ChatGPT 无需在线等待。

- 交互顶层禁止裸 exit；失败用 subshell + false 或只打印 FAIL，避免退出 SSH。

- 系统盘小；大数据、日志、结果继续放 /root/autodl-tmp。

- 不要在当前 low-resource review/auth Gate 预创建 future output/evidence namespace。

## **12.2 Git 与文件安全**

- 未经明确授权，不执行 git reset --hard、git clean -fd、git add .。

- 不为目录美观删除 untracked；不原地覆盖 frozen artifact。

- 核心源码修改优先最小 patch；当前 checker/map/harness frozen inputs 不允许修改。

- 删除必须走 read-only inventory → checksum/equivalence → 用户授权 → delete → post-delete manifest。

# **13. ChatGPT—用户—Codex 协作与文件规则**

| **角色**    | **职责**                                                                                       |
|-------------|------------------------------------------------------------------------------------------------|
| **ChatGPT** | 读取证据、判断 Gate、设计最小步骤、写关键脚本、定义 PASS/FAIL、结果分析、生成交接文档。        |
| **用户**    | 在 AutoDL 实际执行、返回真实输出、控制实例开关、上传 artifact、授权重大修改/删除/受限重跑。    |
| **Codex**   | 只用于复杂算法、顽固 Bug、多文件调用链或关键独立复核；默认 Luna medium，必要时临时 Terra/Sol。 |

- 每次只推进一个最小 Gate。

- 能用 Shell/Python 免费完成的 SHA/grep/find/diff/JSON/AST/process/schema，不使用模型或高资源。

- 长代码优先文件交付；聊天只保留用途、保存位置、执行方法、PASS 标准。

- 大量结果保存在 /root/autodl-tmp，可按 STEP_NAME/{manifest,result,rc,SHA256SUMS,run.log,START,CAPTURE,artifacts} 组织。

- PASS 后只给下一个最小步骤；FAIL 后保存证据，不自动重跑、不扩大修改。

# **14. 永久禁忌、不可回退项与 HOLD**

## **14.1 DO_NOT_REPEAT**

- 不得重跑 2356-root one-time training，也不得 best-seed/retune。

- 不得重选 C01 source identity，不得改变 blind rule 或按表现筛选 candidate。

- 不得重新生成 C01 scenario、source manifest、bundle、static A/B 或 static manifest。

- 不得重跑 C01 static builder；builder authorization/START 已消费。

- 不得重新派生 checker harness，除非出现 frozen SHA 损坏并完成独立 provenance 审计。

- 不得修改 authoritative checker、bitmap、semantic、CollisionLookup、sample spacing、vehicle geometry、route、start/goal/conflict。

- 不得绕过 Authorization V2/START 直接执行 --vehicle A 或 B。

- 不得把 A+B 当成一个 harness process；真实模型是两个顺序 process。

- 不得自动 retry；无论 future checker science PASS/FAIL，都必须先 CAPTURE/freeze。

- 不得启动 Value V3 C01 forward 或 MCTS Value integration。

## **14.2 HOLD / NOT PROVEN**

| **对象**                              | **当前状态**          | **何时才能解除**                                                                 |
|---------------------------------------|-----------------------|----------------------------------------------------------------------------------|
| C01 static bitmap qualification       | **NOT_EVALUATED**     | Authorization V2 → START → A/B two-process checker → CAPTURE → scientific freeze |
| C01 NO-MCTS causal qualification      | **NOT_AUTHORIZED**    | static bitmap result闭合后另行预注册                                             |
| Value V3 independent scene evaluation | **NOT_AUTHORIZED**    | C01 independent qualification 全链闭合且单独 prereg                              |
| MCTS Value integration                | **FALSE / FORBIDDEN** | 独立 blind evaluation PASS 后仍需新的 integration gate                           |
| Production drivability/safety         | **NOT PROVEN**        | 需要外部权威地图/规则/验证，不可由当前实验反推                                   |
| AutoDL 最新 Word live inventory       | **HOLD**              | 单独执行 live inventory；ChatGPT Library 副本不等于云端存在                      |

# **15. 交接文档、云端副本与删除情况**

| **文档/类别**                                                                                           | **当前定位**                                                                             |
|---------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------|
| **2026-08-24 当前最终更新版 / 协议审计停点版**                                                          | HISTORICAL 主线骨架；当前节点已被 8/25–8/26 证据覆盖。                                   |
| **2026-08-25 C06 授权停点版**                                                                           | HISTORICAL；C06 已被后续 2356 training/closure/C01 链覆盖。                              |
| **2026-08-25 2356-root 神经网络阶段性交接**                                                             | HISTORICAL/FROZEN training provenance；其 closure 待确认状态已被后续 closure PASS 覆盖。 |
| **MineSim-Dynamic_全项目阶段性总总结与AI无缝接管手册_2026-08-26_C01静态Checker两进程授权前停点版.docx** | CURRENT；本次最新 handoff。                                                              |
| **ChatGPT Library/Conversation 副本**                                                                   | 可作为交接 artifact；不等于 AutoDL 已上传。                                              |
| **AutoDL 当前 handoff live inventory**                                                                  | HOLD；本轮未执行。                                                                       |

- 历史 cleanup 的直接证据是 move/isolate/archive/quarantine，科研文件 actual delete=0。

- 当前 C01 链只新增 sidecar、lock、scenario/static artifacts 和 harness；没有本轮 delete 证据。

- 路径 absent、No such file、Library 无副本都不能推断为“已删除”。

# **16. 快速接手区（下一位 AI 必须先读）**

| **接手问题**                      | **准确答案**                                                                                                                                         |
|-----------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------|
| **1. 项目现在做到哪里？**         | Value V3 training/closure 已冻结；C01 static assets 和 checker harness 已冻结；两进程执行模型诊断 PASS；Authorization V2 尚未创建。                  |
| **2. 哪些阶段无需重做？**         | MineSim/Pure MCTS/单车/双车/Vector V4/Fleet 历史阶段、2356 training、C01 physical/scene/static assets、checker binding/strategy/harness derivation。 |
| **3. 当前唯一 Gate？**            | C01 static checker two-process static review + one-time authorization V2。                                                                           |
| **4. 正式 repo？**                | /root/MineSim-Dynamic                                                                                                                                |
| **5. 当前 evidence root？**       | /root/autodl-tmp/paper1_value_v3_development_only_v1                                                                                                 |
| **6. Git HEAD？**                 | 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e                                                                                                             |
| **7. 必核 SHA？**                 | 9cc0d... harness；64d9d... manifest；41e7f... checker；b85a3... semantic；51abcd... bitmap；21f2f... pending TXT。                                   |
| **8. 哪些路径不能动？**           | static prep/postfreeze、checker input binding、Strategy V2、harness root、canonical runtime maps/checker。                                           |
| **9. 禁止重跑什么？**             | 2356 training、C01 scene/static asset builder、harness derivation；禁止直接跑 checker。                                                              |
| **10. HOLD？**                    | C01 static qualification、NO-MCTS、independent Value V3 evaluation、MCTS integration、production claims。                                            |
| **11. 下一最小行动？**            | LOW：上传并执行 C01_CHECKER_STATIC_REVIEW_AND_TWO_PROCESS_AUTH_V2.txt。                                                                              |
| **12. PASS 标准？**               | Review/Auth PASS；Auth status AUTHORIZED_NOT_STARTED；2 process launches / 2 checker calls；checker仍未执行。                                        |
| **13. 当前资源？**                | LOW。                                                                                                                                                |
| **14. 下一真实 execution 资源？** | HIGH-CPU/大内存，GPU 不需要，CUDA_VISIBLE_DEVICES=""。                                                                                               |
| **15. FAIL 后停哪里？**           | 停在 static review/auth fault domain；保留完整终端输出，不创建 START/check root，不自动重跑。                                                        |

## **16.1 新 AI 开工前的最小 preflight**

6.  确认用户没有执行 pending V2 review/auth；若已执行，必须先读取真实终端输出，本文当前状态立即降级为历史快照。

7.  核 Git HEAD=112d2bd... 且 tracked clean。

8.  核 check root / auth V2 root / evidence root 均 absent。

9.  核 pending TXT SHA=21f2f4cd...；AutoDL 若无文件，先上传，不重写。

10. 当前只运行 LOW review/auth；不要运行 A/B checker。

11. PASS 后先分析 Authorization V2 readback，再单独设计 HIGH-CPU START→mkdir→A→B→CAPTURE。

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>最终接管原则</strong><br />
真实证据 &gt; AI 推测；最新证据 &gt; 历史文档；冻结结果 &gt; 模型记忆；安全和可恢复 &gt; 目录美观；一个 Gate &gt; 同时推进多个方向。</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# **附录 A：当前 pending 文件的状态清单**

| **项目**                   | **值**                                                           |
|----------------------------|------------------------------------------------------------------|
| **Conversation file**      | C01_CHECKER_STATIC_REVIEW_AND_TWO_PROCESS_AUTH_V2.txt            |
| **SHA256**                 | 21f2f4cd7be92b1facec3d6cbce5bee6959a985844e83722b0c8140ef4107573 |
| **User statement**         | “先做到这一步，你上面给的我还没做”                               |
| **Execution status**       | NOT EXECUTED                                                     |
| **Authorization V2**       | NOT CREATED                                                      |
| **Checker execution**      | NOT STARTED                                                      |
| **Resource now**           | LOW                                                              |
| **Expected next resource** | HIGH-CPU/Memory; GPU not required                                |

# **附录 B：下一执行后的期望终端关键字段**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>REVIEW_AUTH_V2_RC=0<br />
RESOURCE=LOW<br />
STATIC_REVIEW_GATE=PASS<br />
AUTHORIZATION_GATE=PASS<br />
AUTHORIZATION_CONSUMED=False<br />
EXECUTION_BUNDLE_COUNT_AUTHORIZED=1<br />
HARNESS_PROCESS_LAUNCH_COUNT_AUTHORIZED=2<br />
PROCESS_1=--vehicle_A<br />
PROCESS_2=--vehicle_B<br />
CHECKER_CALLS_TOTAL_AUTHORIZED=2<br />
HARNESS_EXECUTED=False<br />
STATIC_CHECKER_EXECUTED=False<br />
STATIC_BITMAP_QUALIFICATION=NOT_EVALUATED<br />
NEXT=C01_STATIC_BITMAP_CHECKER_TWO_PROCESS_ONE_TIME_EXECUTION_START_RUN_CAPTURE<br />
NEXT_RESOURCE=HIGH_CPU_OR_MEMORY_GPU_NOT_REQUIRED</th>
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
<th><strong>交接终点</strong><br />
本文件停在 Authorization V2 之前。任何更新后的真实 AutoDL 输出优先于本 Word；若 pending 文件已执行，必须从新输出重新建立 CURRENT_STATE。</th>
</tr>
</thead>
<tbody>
</tbody>
</table>
