# MineSim 当前项目状态 — 2026-09-27

## 当前权威状态

- AutoDL repo：`/root/MineSim-Dynamic`
- HEAD：`112d2bd0f3412fc83b13d5587d2b41402d2d0f5e`
- tracked repo：clean；仅历史未跟踪 `?? ^C`，不得删除、修改、stage 或 clean。
- G0：**PASS_FROZEN**
- G1：**PASS_FROZEN**
- G2：**HOLD_BEFORE_SCIENTIFIC_RUNTIME_PENDING_V2_PREPARE**
- G3：NOT_STARTED
- G9 independent HOLDOUT：**UNTOUCHED**

旧文档中“G1 deadlock terminal integration 尚未执行”已过时。本文件、`G1_FINAL_FREEZE.json` 和真实 AutoDL SHA/运行结果优先。

## G1 最终冻结

Hard safety：9×4 m exact footprint，在 0.1 s ticks 同时做 V2V 与 V2R；V2R 要求 `D_drivable.covers(footprint)`。`D_drivable` 冻结为 `road ∪ intersection ∪ loading_area ∪ unloading_area`，178 polygons、29 components。map SHA256=`b85a3d8b28f2252ecb5bda179d514573f6333079def838cd048566f556d95cd0`。

Deadlock：`SAFE_ABSORBING_STATE_TRAP` 已进入 tree/reward terminal、action provider、root guard、task status。

Reward/value：progress cap=1.0；safe nonterminal outer step time=-0.05；unfinished stationary 全等待=-0.10；单车首次停稳 +5；两车完成 global +20；总 completion credit ≤+30；hard safety=-100。SAFE_DEADLOCK terminal transition 不加 time/wait。

Risk：PET/MMTTC=`DIAGNOSTIC_ONLY`；TTC/internal clearance=`UTILITY`；不新增 PET/MMTTC hard rule、pruning 或 reward term。

## G2 为什么仍是 HOLD

旧 V1 runner 的 LOW prepare 曾技术通过，但 Stage-A scientific runtime **从未启动**。逻辑审查发现 V2R/deadlock 未 consolidated、deadline/reward/RNG/anchor/resume/root-role 等问题，因此旧 V1 `stage-a` 永久 superseded。

本次 production-binding discovery 又确认：MineSim 地图不是通用 GeoJSON FeatureCollection。真实 loader 使用四个非几何层 `road/intersection/loading_area/unloading_area`，每条记录通过 `link_polygon_token` 指向 `polygon`，再由 `polygon.link_node_tokens -> node(x,y)` 构造 Shapely Polygon。生产 loader SHA256=`41872d1e568cd1a68bc2c2997d7dfc3c7db93d3ef0e1959597d891902049ff34`。

原 `G1_V2R_DRIVABLE_DOMAIN_V1_FAST.py` 字节已不在 AutoDL，所以新 V2 **不会冒充重放原脚本**。LOW prepare 将用 byte-bound production loader + exact frozen map 重构四层 union，并 fail-fast 要求 178 linked polygon records、valid MultiPolygon、29 components、真实 A/B route endpoints 被覆盖，同时保留历史 G1 token-set SHA 作为 provenance。

## G2-A 当前设计

- ROOTS：current Retry2 4 个 frozen C11 roots
- ROLE=`G2_CALIBRATION_DEVELOPMENT`
- `G9_HOLDOUT_ELIGIBLE=false`
- Budget=`[4,8,16,32,64]`
- Horizon=`[4,8,16]`
- Stage-A：4×5×3=**60 episodes**，replicate=1，仅 coarse screen
- 新 G1 contract 下包含 B64-H8 anchor
- Deadline：400 ms decision / 380 ms work cutoff / 20 ms reserve；late return 不执行 outer transition
- per-decision paired RNG：seed 只依赖 root/state/replicate/outer_step，不依赖 budget/horizon
- atomic cell + signature，可安全 resume

Stage-A 结果不能直接冻结 G2；之后仍需对 frontier 做 paired multi-seed confirmation。G2-B 只在 C04+C06+C11 上验证 shortlist/anchor，不重新调参。G2 freeze 后才允许 G3 Teacher collection。

## 当前唯一下一步

上传 `G2_FORMAL_CALIBRATION_V2` 到 AutoDL，先运行 **LOW prepare**。只有输出 `PASS:G2_FORMAL_CALIBRATION_V2_PREPARE` 后，才可复用已经获得的 HIGH-CPU 授权启动 Stage-A。

当前 V2 runner SHA256=`4ddb829d96b76a1c49ae28b82ac09a99551086ff9f1a525d9ba8b3450d170301`；V2 ZIP SHA256=`4d8e84bb4ca60e1cb7de8aed760c83797fa2b3de13e995a811166e680bcbf2b4`。**V2 prepare 尚未运行，不能提前记 PASS。**
