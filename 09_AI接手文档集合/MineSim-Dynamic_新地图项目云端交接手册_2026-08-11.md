**MineSim-Dynamic 新地图接入与 Full-Mine 转换项目**

**云端项目交接手册 / AI 接手指南 / 问题复盘 / 工作流规范**

**状态基线：2026-08-11**

**当前 Full-Mine 地图标签：DEV_ONLY_NOT_PRODUCTION_VALIDATED**

当前仓库 HEAD：d81c57154e4e5d0b4df1251cf565d9aacffaa026

Tag：fullmine-dev-runtime-pass-20260811

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>文档用途</strong></p>
<p>本手册以用户提供的原始地图包、会话导出的云端终端日志、Codex 当日审计/补丁输出、Git commit/tag 记录和实际运行结果为依据。目标是让新的 AI/工程人员不需要重新审计已完成阶段，即可在 AutoDL 云端快速恢复环境、理解当前技术边界、定位关键文件并从下一步继续。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# **0. 接手前 5 分钟必须读完的“当前真相”**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>最重要的结论</strong></p>
<p>完整矿区 Full-Mine 已经从原始 GeoJSON 转换为 MineSim-compatible semantic map，并生成了可被 MineSim 原生 loader 使用的 10 px/m DEV_ONLY mask；独立地图身份 geojson_full_mine_dev 已注册；single-ego 1 step / 5 s、dual-ego 1 step / 5 s 均已 PASS。当前最大的未完成项不是“能否换地图”，而是“是否有权威 production drivable surface / mask 生成依据”。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

| **项目**         | **当前值**                                                                         |
|------------------|------------------------------------------------------------------------------------|
| 仓库             | /root/MineSim-Dynamic                                                              |
| 分支             | newmap-j117-dev                                                                    |
| 当前 HEAD        | d81c57154e4e5d0b4df1251cf565d9aacffaa026                                           |
| 当前 Tag         | fullmine-dev-runtime-pass-20260811                                                 |
| DEV map location | geojson_full_mine_dev                                                              |
| DEV map version  | dev-geojson-full-mine-v1                                                           |
| DEV map root     | /root/autodl-tmp/new_map_phase6f8_full_mine_dev/maps                               |
| Semantic         | semantic_map/geojson_full_mine_dev_semantic_map.json（约 124 MB）                  |
| Mask             | bitmap/geojson_full_mine_dev_bitmap_mask.png（symlink，物理 PNG 约 3.0 MB）        |
| Mask 规则        | 3.5 m lane-centered half-width + parent clipping + road 484 excluded               |
| Mask 尺寸        | 46322 × 42411；10 px/m；0=non-drivable，255=drivable                               |
| Semantic SHA256  | e6fde56e8ee8808df67911d8f8938d5da5a49d0d1e8cc60fbd819ad233f516d5                   |
| Mask SHA256      | beefa560c2ec9811c81aedf74f2307373a785c0d79f7f44038934e46d7daad22                   |
| Git bundle       | /root/autodl-tmp/MineSim-Dynamic_fullmine_dev_runtime_20260811.bundle（已 verify） |
| 生产有效性       | FALSE：当前是 DEV_ONLY_NOT_PRODUCTION_VALIDATED，不得称为 production HD Map        |

## **0.1 接手后第一条命令**

> source /root/miniconda3/etc/profile.d/conda.sh  
> conda activate minesim  
> cd /root/MineSim-Dynamic  
> export PYTHONPATH=/root/MineSim-Dynamic  
>   
> echo "ENV=\$CONDA_DEFAULT_ENV"  
> echo "RAM=\$(cat /sys/fs/cgroup/memory.max)"  
> echo "CPU=\$(cat /sys/fs/cgroup/cpu.max)"  
> git rev-parse HEAD  
> git status --short

期望：环境为 minesim；HEAD 为 d81c57154e4e5d0b4df1251cf565d9aacffaa026；git status 为空。资源必须以 cgroup 为准，不要相信 nproc/free -h 显示的宿主机总资源。

## **0.2 新 AI 绝对不要做的事**

- 不要重新审计 Phase 3/4/5、Full-Mine structural、bitmap loader、single/dual smoke；除非出现明确回归证据。

- 不要把当前 Full-Mine mask 称为 production mask；官方广东/江西生产 mask 的生成规则并未开源。

- 不要把整个 road/junction/loading/unloading/auxiliary polygon 直接填成可行驶。

- 不要用 buffer(0) 自动修 road 332；不要静默修 road 484；不要猜 gear=-1 的运营方向；不要使用来源不明的 Z 作为高程。

- 不要把大文件、日志、试验脚本提交进 repo；全部放 /root/autodl-tmp。

- 不要让 Codex 重新跑长仿真或 full build；终端负责执行，AI 负责关键判断和代码。

# **1. 项目目标、范围与当前完成度**

项目最初目标是把用户提供的完整矿区 GIS/GeoJSON 数据接入 MineSim-Dynamic，使其不仅能被解析为 semantic map，还能走通 MineSim 原生 map API、场景、规划、控制和多车运行链。由于官方项目没有公开“原始 GIS → production bitmap mask”的地图生产工具，本项目最终形成了两条明确分开的成果线：结构语义转换（高可信、已完整验证）与 DEV_ONLY 可行驶 mask（用于软件联调，非生产有效性声明）。

| **维度**                      | **当前状态** | **结论**                                                                          |
|-------------------------------|--------------|-----------------------------------------------------------------------------------|
| 原始数据解析                  | PASS         | 8 类 GeoJSON 已完成完整索引与缺陷审计                                             |
| J117 真实数据 Pilot           | PASS         | 证明从真实源数据到 MineSim semantic/bitmap/runtime/MCTS 的最小闭环                |
| Full-Mine structural semantic | PASS         | 540 path / 177 polygon / 565 dubins_pose 等完整生成并通过引用、拓扑、来源追踪验证 |
| Full-Mine production mask     | BLOCKED      | 缺少官方/测绘权威可行驶面或生成规则                                               |
| Full-Mine DEV_ONLY mask       | PASS         | 3.5 m lane corridor 方案已生成、加载、碰撞检测可用                                |
| 独立地图注册                  | PASS         | geojson_full_mine_dev 已加入 semantic registry、bitmap registry、车辆 alias       |
| Single-ego runtime            | PASS         | 1 step + 5 s / 50 step 均通过                                                     |
| Dual-ego runtime              | PASS         | 1 step + 5 s / 50 step 均通过                                                     |
| Full-Mine 全域覆盖测试        | 未完成       | 当前运行测试主要仍在 J117 路线区域；全矿不同区域/路线尚未系统覆盖                 |

# **2. 云端环境、目录约定与资源策略**

## **2.1 目录约定**

| **路径**                      | **用途**                       | **原则**                                                            |
|-------------------------------|--------------------------------|---------------------------------------------------------------------|
| /root/MineSim-Dynamic         | 正式 Git 仓库                  | 只放必要生产源码修改；保持 clean；commit/tag 管理                   |
| /root/autodl-tmp              | AutoDL 数据盘                  | 所有大文件、地图资产、转换脚本、日志、实验结果、Git bundle 都放这里 |
| /root/miniconda3/envs/minesim | Python 环境                    | Python 3.9.25；运行 MineSim 与转换脚本                              |
| /root/datasets/maps           | 原项目已下载的广东/江西 HD Map | 仅作 production 行为对照，不修改                                    |

## **2.2 资源真实值必须看 cgroup**

项目中出现过一个非常重要的资源误判：free -h 曾显示宿主机约 1 TiB 内存、nproc 显示 192 核，但容器最初实际只有 2 GiB RAM 和约 0.5~1 CPU 配额。Full-Mine build 被 SIGKILL/rc=137 后，通过 /sys/fs/cgroup/memory.max 和 cpu.max 才定位到真实限制。

> cat /sys/fs/cgroup/memory.max  
> cat /sys/fs/cgroup/memory.current  
> cat /sys/fs/cgroup/memory.events  
> cat /sys/fs/cgroup/cpu.max

| **场景**      | **典型资源**                                      | **是否需要开卡**                                                    |
|---------------|---------------------------------------------------|---------------------------------------------------------------------|
| 低资源/关卡后 | 2 GiB RAM；0.5~1 CPU（以 cgroup 为准）            | 适合只读代码、轻量脚本、git；不适合 full mask/full runtime          |
| 高资源实例    | 80 GiB RAM；15 vCPU；RTX 4090D 24GB               | 用于 Full-Mine build、19.6 亿像素 mask、full-mask load、5 s runtime |
| GPU 本身      | 当前地图转换主要是 Python/Shapely/Rasterio/Pillow | 基本不用 GPU；开卡主要为了附带 RAM/CPU                              |

## **2.3 环境恢复标准命令**

> source /root/miniconda3/etc/profile.d/conda.sh  
> conda activate minesim  
> cd /root/MineSim-Dynamic  
> export PYTHONPATH=/root/MineSim-Dynamic

# **3. Git 基线、关键 commit/tag 与恢复资产**

| **阶段**                         | **Commit / Tag**                                                                                     | **意义**                                                |
|----------------------------------|------------------------------------------------------------------------------------------------------|---------------------------------------------------------|
| Phase 3 J117 production map load | tag: j117-phase3-production-map-load-20260809（commit 4bd2bff）                                      | J117 semantic + bitmap 已能走 production loader         |
| Phase 4C single-ego closed loop  | tag: j117-phase4c-single-ego-closed-loop-20260810（commit ec1c958735b0ee76201284faacb46fccc75c7f6c） | J117 单车闭环冻结点                                     |
| Phase 5 dual-ego + Pure MCTS     | commit da4105b836dbbd3e702ee25fbb364109bc4e2596；tag j117-phase5-dual-ego-pure-mcts-20260810         | J117 双车生产 runtime + Pure MCTS 5 seed 全通过         |
| Full-Mine 查询性能修复           | 32fb42920d8cc404b37cd25dc47cbc6fbde4d9f4                                                             | semantic polygon node 查找由全表扫描改为 token2ind O(1) |
| Full-Mine DEV 独立注册           | d81c57154e4e5d0b4df1251cf565d9aacffaa026                                                             | 注册 geojson_full_mine_dev semantic/mask/vehicle alias  |
| 当前冻结点                       | tag fullmine-dev-runtime-pass-20260811                                                               | Full-Mine DEV single/dual runtime smoke 已通过          |

## **3.1 Git bundle 恢复**

已生成并验证完整 Git bundle：/root/autodl-tmp/MineSim-Dynamic_fullmine_dev_runtime_20260811.bundle（约 15 MB，bundle verify = okay）。如果系统盘 repo 损坏，可从 bundle 恢复而不依赖网络。

> mkdir -p /root/recovery_test  
> cd /root/recovery_test  
> git clone /root/autodl-tmp/MineSim-Dynamic_fullmine_dev_runtime_20260811.bundle MineSim-Dynamic  
> cd MineSim-Dynamic  
> git checkout newmap-j117-dev  
> git show --no-patch fullmine-dev-runtime-pass-20260811

# **4. 原始新地图数据：内容、坐标与已知缺陷**

## **4.1 原始交付包**

源包：/root/autodl-tmp/地图新建相关文件.zip（会话上传的同名 ZIP）。包内包含 8 个 GeoJSON 图层和 1 张参考图片。

| **图层**              | **Feature 数量** | **作用**                                |
|-----------------------|------------------|-----------------------------------------|
| junction.geojson      | 35               | 路口/交叉区域                           |
| lane.geojson          | 553              | 道路/路口/作业区中心线与拓扑            |
| road.geojson          | 94               | 道路区域 polygon                        |
| road_boundary.geojson | 100              | 道路边界                                |
| rgn_boundary.geojson  | 84               | junction/load/unload/auxiliary 区域边界 |
| rng_load.geojson      | 36               | 装载区                                  |
| rgn_unload.geojson    | 7                | 卸载区                                  |
| rgn_auxiliary.geojson | 6                | 辅助区域                                |

## **4.2 Lane 分布**

| **rgn_type** | **类别**  | **源 lane 数** | **Full-Mine active lane 数** |
|--------------|-----------|----------------|------------------------------|
| 0            | road      | 168            | 155                          |
| 1            | junction  | 94             | 94                           |
| 2            | load      | 126            | 126                          |
| 3            | unload    | 15             | 15                           |
| 4            | auxiliary | 150            | 150                          |
| 合计         |           | 553            | 540                          |

## **4.3 坐标系统与本地坐标**

J117 Pilot 与 Full-Mine converter 采用同一坐标链：源坐标按 WGS84/EPSG:4326 读取，投影到 UTM Zone 46N（EPSG:32646），再减去固定本地原点 E0=409200.0、N0=4916800.0，得到 MineSim local XY。

> x_local = UTM_E - 409200.0  
> y_local = UTM_N - 4916800.0

当前 Full-Mine DEV raster local bounds：x=\[57.1998536286992, 4689.382435352891\]，y=\[9.526631466113031, 4250.596236802638\]。

## **4.4 源数据缺陷与不可猜测项**

| **问题**   | **证据/现象**                                                                         | **当前处理**                                                          |
|------------|---------------------------------------------------------------------------------------|-----------------------------------------------------------------------|
| road 332   | polygon 自相交；真实 invalid geometry                                                 | generic exclusion；禁止 buffer(0) 自动修复                            |
| 12 条 lane | 5163/5164/5165/5166/5171/5172/5175/5178/5179/5180/5181/5186 引用不存在的 road polygon | 显式排除；禁止 nearest-road reassignment                              |
| lane 5050  | 父 road 332 被排除                                                                    | missing_or_excluded_parent_region                                     |
| 50 条 lane | gear=-1，运营方向语义未知                                                             | 结构保留 pr→su；operational_direction_verified=false；不自动反向      |
| road 342   | polygon/boundary 名称 R#805 vs R#756 不一致                                           | 保留来源追踪，不把 name 当 authoritative                              |
| Z 值       | 源第三坐标 datum/unit 未知                                                            | 不进入 MineSim 高程；source_z_datum_verified=false                    |
| road 484   | lane 6942/6989 分别约 21.844 m / 11.156 m 跑出父 polygon；boundary 也明显不一致       | semantic 保留可追溯；DEV mask 排除 road 484 及相关两 lane，不静默修复 |

# **5. J117 Pilot：为什么先做、做到了什么**

J117 = Junction 117，不是随机版本号。它是从完整源 GeoJSON 中选出的一个真实交叉区域，用来证明完整技术链在小范围真实数据上可行，然后再泛化到 Full-Mine。Pilot 的价值是降低一次性全图调试复杂度，同时提供可以回归的“金标准区域”。

## **5.1 Pilot 路线**

| **路线** | **源 lane**        | **J117 semantic token**  | **Full-Mine semantic token**            |
|----------|--------------------|--------------------------|-----------------------------------------|
| A        | 6670 → 6674 → 5690 | path-0 → path-1 → path-2 | path-000426 → path-000430 → path-000330 |
| B        | 5691 → 6546 → 6523 | path-3 → path-4 → path-5 | path-000331 → path-000403 → path-000387 |

固定冲突点 local XY ≈ (2878.08878684574, 2799.656085037)。对齐初始进度 A=20 m，B=92 m，v0=4.5 m/s，使两车 nominal ETA 几乎相等。

## **5.2 J117 bitmap**

J117 bitmap 是明确可解释的 Pilot 规则：仅将 road 471、385、342 与 junction 117 的 polygon union 栅格化为可行驶。mask 为 mode L、0/255、10 px/m、4848×2643。它直接证明的只是这四个 polygon，不应外推为全矿 whole-polygon 规则。

## **5.3 Phase 5 双车与 Pure MCTS 结果**

| **实验**                 | **关键结果**                                                                                    |
|--------------------------|-------------------------------------------------------------------------------------------------|
| No-MCTS aligned baseline | crossing gap ≈ 0.00070 s；min clearance=0；发生真实几何重叠（用于证明冲突基线）                 |
| Pure MCTS seed 0         | crossing gap ≈ 1.561 s；1 ms swept min clearance ≈ 0.594 m；无碰撞                              |
| 5-seed robustness        | 5/5 benchmark PASS；5/5 swept PASS；最小 swept clearance ≈ 0.594 m；crossing gap 约 1.35–1.97 s |
| Dual runtime             | A/B 同步 iteration；object-1 从 external observation 过滤；single-ego regression safe           |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>J117 阶段已冻结</strong></p>
<p>Phase 3/4/5 已有 tag/commit；后续 Full-Mine 工作不应重新审计或重新调 MCTS。J117 主要作为回归区域使用。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# **6. Full-Mine structural conversion：Phase 6A–6E.1**

## **6.1 Phase 6A：从 J117 builder 中拆出“可复用逻辑”**

Codex 只读审计确认 J117 builder 中可复用部分包括：WGS84→UTM→local transform、lane vertex/yaw 保留、共享 topology node、Dubins pose、polygon/borderline/path linking、schema/reference/topology/raster/source traceability validator、manifest/report/hash。必须泛化的部分包括固定 J117 IDs、固定 6 lane、固定 crop、固定 4 个可行驶 polygon、硬编码 token/count/conflict。

## **6.2 Phase 6B：完整源数据 preflight**

preflight 证明全源对象计数稳定，所有 84 个 region boundary 可解析，但存在 road332 invalid、12 个 missing-road lane、50 个 gear=-1、未知 Z 等已知 gates。完整坐标点约 1,118,211。

## **6.3 Phase 6C：通用 structural converter**

核心脚本：/root/autodl-tmp/new_map_phase6c_tools/build_full_mine_structural.py。职责是“原始 GeoJSON → Full-Mine structural semantic + validation artifacts”，明确不做 production registration、不做 scenario、不做 planner/MCTS，也不直接生成 production mask。

| **输出对象**   | **最终数量** |
|----------------|--------------|
| node           | 400744       |
| polygon        | 177          |
| road           | 93           |
| intersection   | 35           |
| loading_area   | 36           |
| unloading_area | 7            |
| auxiliary_area | 6            |
| dubins_pose    | 565          |
| reference_path | 540          |
| borderline     | 388          |

## **6.4 Structural 显式排除**

| **原因**                          | **数量** | **说明**                                                          |
|-----------------------------------|----------|-------------------------------------------------------------------|
| missing_or_excluded_parent_region | 13       | 12 条 missing-road lane + lane 5050/road332                       |
| unresolved_parent_region          | 6        | 源 boundary 父引用无法权威解析，保留 explicit exclusion           |
| invalid_geometry                  | 1        | road 332                                                          |
| parent_region_excluded            | 1        | 依赖被排除 road332 的 boundary                                    |
| 合计                              | 21       | 每个 relevant source object 必须 represented 或 explicit excluded |

## **6.5 Phase 6E：三个系统性 correctness bug**

| **Bug**              | **症状**                                                  | **根因**                                                                   | **修复**                                                                                                              |
|----------------------|-----------------------------------------------------------|----------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------|
| Endpoint consistency | 126 个 path_endpoint_errors                               | 多个 lane 共享 source topology node，但端点 XY 不是 bit-identical          | 对每个 topology node 生成 deterministic canonical XY；仅 snap path 首尾 XY；保留内部 waypoint 与 yaw；0.25 m 安全阈值 |
| Source coverage      | source_coverage_missing=49                                | load/unload/auxiliary 已生成，但 validator 没做 source→semantic layer 映射 | road→road；junction→intersection；load→loading_area；unload→unloading_area；auxiliary→auxiliary_area                  |
| Category reporting   | full-plan active_by_region_category 曾输出 0/1/2/3/4 全 0 | key/type 统计错误                                                          | 统一使用 road/junction/load/unload/auxiliary 命名统计                                                                 |

最终 endpoint snap：134 个端点（start 76 / end 58）；max=0.1439073347 m；mean=0.0251615747 m；path_endpoint_errors=0。

## **6.6 Phase 6E.1：boundary parent 语义修复**

随后发现一个更隐蔽的结构语义 bug：rgn_boundary.geojson 的父区域应该由 rgn_type + rgn_objectid 联合决定，但旧 boundary_parent() 会跨 category 搜同 object ID。由于不同类别 ID 会重复，导致 8 个 represented boundary component 挂错父 polygon/category。修复后严格映射：1=junction，2=load，3=unload，4=auxiliary；不存在/错误声明不做跨类别猜测；road_boundary 保持独立 road_objectid 逻辑。

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>Phase 6E.1 最终 structural PASS</strong></p>
<p>path_endpoint_errors=[]；source_coverage_missing=[]；dangling_references=[]；bidirectional_failures=[]；wrong_source_boundary_parent_count=0；schema/topology/traceability PASS。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# **7. Production mask 调研与为何最终采用 DEV_ONLY mask**

## **7.1 官方 MineSim-Dynamic 的现实：只公开“用地图”，未公开“制地图”**

对仓库、Git history、map_expansion、MATLAB .fig、旧地图资产进行审计后，没有找到 production mask generator、GIS rasterizer、lane-width/buffer/erosion pipeline、obstacle/restricted layer processor 或车辆净空生成工具。README 指向外部 MineSim HD Maps v1.6 资产包；广东大排与江西江铜 mask 是成品 PNG。

## **7.2 为什么不能 whole-polygon 填满**

把现有广东/江西 semantic polygon 与 production mask 对齐后，发现每类 polygon 内都有大量 non-drivable 内部区域；因此 “road/junction/load/unload polygon 全部=255” 与原项目 production convention 冲突。

| **类别**  | **广东大排 polygon 内 drivable 比例（约）** | **江西江铜（约）** |
|-----------|---------------------------------------------|--------------------|
| road      | 74.5%                                       | 58.9%              |
| junction  | 80.8%                                       | 68.0%              |
| loading   | 68.2%                                       | 44.0%              |
| unloading | 73.9%                                       | 71.4%              |

road_block 也不是简单的“内部禁行扣除层”：production road_block polygon 自身包含混合 drivable/non-drivable 像素，无法通过 polygon-road_block 复现官方 mask。

## **7.3 10 px/m 是 collision path 的实际硬约束**

MineSimBitMapPngLoader 会从 metadata 读取 scale_PixelPerMeter，但 CollisionLookup.collision_detection() 内部硬编码 x/0.1、y/0.1，即 0.1 m/pixel = 10 px/m。因此 1/2/5 px/m 即使 loader 能裁剪，也会被 collision lookup 错误解释。RGB display 可以是其它分辨率，但 collision mask 当前必须 10 px/m（除非修改 production collision code）。

## **7.4 DEV_ONLY corridor 规则如何确定**

为软件集成测试建立一个可解释且明确非生产的 mask。先对广东/江西 production mask 测量 reference-path 到最近 non-drivable 像素的 clearance，并结合车辆宽度校准。XG90G 宽 4.0 m；NTE200 宽 6.7 m。4.0 m half-width 被 sanity check 拒绝；最终采用 3.5 m half-width，并明确只用于 DEV_ONLY。

| **规则项** | **当前 DEV_ONLY 规则**                                                                          |
|------------|-------------------------------------------------------------------------------------------------|
| 标签       | DEV_ONLY_NOT_PRODUCTION_VALIDATED                                                               |
| half-width | 3.5 m                                                                                           |
| 几何       | 每条 active lane/reference path 使用 round-ended buffer                                         |
| 裁剪       | buffer 与 declared parent polygon 相交                                                          |
| 连接       | 所有 corridor union；junction connector 一并 union，天然闭合共享 topology node                  |
| road 484   | 整条 road 及其两条异常 lane 从 DEV mask 排除                                                    |
| auxiliary  | 允许 parent-resolved lane corridor 进入 DEV mask，但不宣称 whole polygon production drivability |
| 栅格       | 10 px/m，mode L，0/255，normal top-down                                                         |

# **8. Full-Mine DEV mask 生成、加载与性能数据**

## **8.1 Generator**

脚本：/root/autodl-tmp/new_map_phase6f4_tools/build_dev_fullmine_mask.py。它复用 Phase 6 converter 的 source inventory、投影、bounds、exclusion，不加载不必要的 400k semantic node。提供 --plan / --smoke / --build。

| **Plan 项**                   | **值**                      |
|-------------------------------|-----------------------------|
| 尺寸                          | 46322 × 42411               |
| scale                         | 10 px/m                     |
| tile                          | 1024×1024；46×42=1932 tiles |
| included lane components      | 538                         |
| excluded road484 lanes        | 2                           |
| other excluded by mask policy | 0                           |
| source structural exclusions  | 21                          |

## **8.2 大图输出链问题与修复**

| **问题**            | **症状**                                                             | **修复**                                                                                       |
|---------------------|----------------------------------------------------------------------|------------------------------------------------------------------------------------------------|
| Rasterio PNG writer | BufferedDatasetWriter，不能证明直接 window write 真正 bounded-memory | 先写 tiled/deflate temporary GeoTIFF，再通过 rasterio.shutil.copy/GDAL CreateCopy 生成最终 PNG |
| 空 tile             | rasterize(\[\]) 抛 ValueError: No valid geometry objects found       | 无 geometry 的 tile 直接写 np.zeros(uint8)                                                     |
| Pillow 超大图保护   | 1.964B 像素触发 DecompressionBombError                               | generator validator 与 MineSim loader 使用 Image.MAX_IMAGE_PIXELS=None                         |
| 终端误操作          | 第一次生成 PNG 后因后续误粘清理命令被删除                            | 重新 --build；后续禁止重复 rm bitmap 目录                                                      |

## **8.3 最终 mask 资产**

| **项**              | **值**                                                                                            |
|---------------------|---------------------------------------------------------------------------------------------------|
| 物理 PNG            | /root/autodl-tmp/new_map_phase6f4_dev_mask/bitmap/geojson_full_mine_dev_only_mask.png             |
| DEV package symlink | /root/autodl-tmp/new_map_phase6f8_full_mine_dev/maps/bitmap/geojson_full_mine_dev_bitmap_mask.png |
| 文件大小            | 约 3.0 MB（高度稀疏，PNG 压缩率高）                                                               |
| SHA256              | beefa560c2ec9811c81aedf74f2307373a785c0d79f7f44038934e46d7daad22                                  |
| Transform           | 0.1 m/pixel；x origin≈57.20；y top≈4250.60；stored Y 向下                                         |

## **8.4 Loader 实测**

| **测试**           | **结果**                                                                  |
|--------------------|---------------------------------------------------------------------------|
| Local crop         | 450×450 bool；TRUE=102950；FALSE=99550；layout=normal；PASS               |
| get_maps_api local | MineSimMap 构造成功；image_ndarray_local PASS                             |
| Full mask load     | shape=(42411,46322)，bool，1.83 GiB；TRUE=37,115,992；FALSE=1,927,446,350 |
| Full mask 性能     | elapsed≈31.14 s；MAX_RSS≈7.869 GiB                                        |

# **9. Full-Mine runtime：single/dual 链路与关键生产代码修复**

## **9.1 Single-ego 初始化性能瓶颈**

Full-Mine scenario 初始化成功，但 IDM planner.initialize() 曾长时间卡在 MineSimSemanticMapJsonLoader.get_polygon_token_using_node()。根因：对每个 polygon 的每个 link_node_token，都在 self.node（约 400,744 条）中线性扫描 token；Full-Mine 下复杂度爆炸。

Loader 初始化其实已经维护 self.token2ind\[layer\]\[token\]。临时 monkey patch 验证 O(1) 查询后，单步 smoke 约 29 s 完成；随后正式修改 production loader，用 self.token2ind\["node"\] 直接索引。

| **提交**                                 | **修改**                                                          | **回归**                                    |
|------------------------------------------|-------------------------------------------------------------------|---------------------------------------------|
| 32fb42920d8cc404b37cd25dc47cbc6fbde4d9f4 | semantic node token 查找由 nested linear scan 改为 token2ind O(1) | Full-Mine one-step PASS；J117 one-step PASS |

## **9.2 Full-Mine single-ego 结果**

| **测试**      | **结果**                                                                                               |
|---------------|--------------------------------------------------------------------------------------------------------|
| 1 step        | scenario_init PASS；planner_init PASS；17 trajectory samples finite；controller_step PASS；移动≈0.45 m |
| 自动路线      | path-000426 → path-000430 → path-000330（对应源 lane 6670→6674→5690）                                  |
| 5 s / 50 step | steps=50；distance≈34.724 m；path progress +34.800 m；drivable_all_steps=true；exception=null          |

## **9.3 Full-Mine dual-ego 结果**

复用 Phase 5 MultiEgoRuntime/ControlledVehicleRuntime production path。B 仍来自 aligned scenario 中 real tracked object-1；runtime 将其转为 controlled B，并从 external observation 过滤 object-1，避免同一实体既受控又作为外部障碍重复出现。

| **检查项**                        | **结果**    |
|-----------------------------------|-------------|
| dual_initialize_ok                | True        |
| controlled_tokens_ok              | True        |
| object_1_removed_external         | True        |
| same_current_iteration            | True        |
| same_next_iteration               | True        |
| advanced_exactly_one_step         | True        |
| runtime_A_moved / B_moved         | True / True |
| object_1_still_removed_after_step | True        |
| single_ego_regression_safe        | True        |
| error                             | None        |
| production_files_changed          | False       |

Dual 5 s harness 是在已 PASS 的 single-step production path 上改为 50 次同步 propagate；运行正常结束且所有固定打印字段保持 PASS。旧脚本标题仍打印 “J117 FINAL ALIGNED PRODUCTION RUNTIME SMOKE”，只是 harness 历史名称，不代表运行时地图仍是 J117。

# **10. 独立地图身份 geojson_full_mine_dev**

## **10.1 为什么要摆脱 J117 alias**

早期 Full-Mine runtime 为减少改动，临时复用了 location="geojson_j117_pilot" 与 symlink。软件链跑通后，必须建立独立地图身份，否则后续 AI 容易混淆 map version、bitmap basename、vehicle alias 与测试资产。

## **10.2 DEV package**

| **项**            | **值**                                                              |
|-------------------|---------------------------------------------------------------------|
| map_root          | /root/autodl-tmp/new_map_phase6f8_full_mine_dev/maps                |
| location          | geojson_full_mine_dev                                               |
| version           | dev-geojson-full-mine-v1                                            |
| semantic basename | geojson_full_mine_dev_semantic_map                                  |
| mask basename     | geojson_full_mine_dev_bitmap_mask                                   |
| semantic info     | DEV_ONLY Full-Mine MineSim-compatible map; NOT PRODUCTION VALIDATED |
| mask version      | dev-geojson-full-mine-mask-v1                                       |
| vehicle alias     | XG90G（4.0 m width）                                                |

## **10.3 Repo 注册修改**

| **文件**                                                                          | **修改**                                                                                                      |
|-----------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------|
| devkit/sim_engine/map_manager/minesim_map_data/minesim_semanticmap_json_loader.py | locations / semantic_map_hashes / map_version_hashes 加 geojson_full_mine_dev；同时包含 O(1) node lookup 修复 |
| devkit/sim_engine/map_manager/minesim_map_data/minesim_bitmap_png_loader.py       | bitmap_mask registry 增加 geojson_full_mine_dev_bitmap_mask                                                   |
| devkit/common/actor_state/vehicle_parameters.py                                   | geojson_full_mine_dev → guangdong_dapai/XG90G 参数 alias                                                      |

注册 commit：d81c57154e4e5d0b4df1251cf565d9aacffaa026（Register full-mine development map）。独立 identity 下 get_maps_api local、single 1 step、single 5 s、dual 1 step、dual 5 s 均通过。

# **11. 新地图与原项目两个正式地图的异同**

| **对比项**             | **广东大排**                | **江西江铜**                | **当前 Full-Mine DEV**                             |
|------------------------|-----------------------------|-----------------------------|----------------------------------------------------|
| 身份                   | guangdong_dapai             | jiangxi_jiangtong           | geojson_full_mine_dev                              |
| 版本                   | 1.6                         | 1.5                         | dev-geojson-full-mine-v1                           |
| 地图来源               | 外部 MineSim HD Maps 成品   | 外部 MineSim HD Maps 成品   | 用户原始 8 类 GeoJSON → 本项目 converter           |
| Semantic               | 官方/成品                   | 官方/成品                   | 本项目生成；结构验证 PASS                          |
| Collision mask         | 官方成品 PNG                | 官方成品 PNG                | 本项目 DEV_ONLY corridor PNG                       |
| Mask 生成规则公开      | 否                          | 否                          | 是：3.5 m corridor + parent clip + road484 exclude |
| Mask scale             | 10 px/m                     | 10 px/m                     | 10 px/m                                            |
| Mask value             | 0/255→bool                  | 0/255→bool                  | 0/255→bool                                         |
| whole polygon=drivable | 否                          | 否                          | 否；仅 lane corridor                               |
| 车辆                   | XG90G 9×4 m                 | NTE200 13×6.7 m             | 当前 alias 为 XG90G 9×4 m                          |
| auxiliary_area         | production API 无明确层     | 同左                        | semantic 有 6 个，但 production API 支持有限       |
| single ego             | 原生可用                    | 原生可用                    | 1 step / 5 s PASS                                  |
| dual ego               | 经本项目 multi-ego 扩展可用 | 经本项目 multi-ego 扩展可用 | 1 step / 5 s PASS                                  |
| 生产真实性             | 正式资产                    | 正式资产                    | FALSE；DEV_ONLY                                    |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>准确表述</strong></p>
<p>当前新地图是“已经完全走通 MineSim 软件链的、自主从 GeoJSON 构建的 Full-Mine DEV Map”。Semantic 部分已经成熟并有完整来源追踪；与两个原生正式地图相比，仍缺的是 production drivable mask 的权威真实性与全矿运行覆盖，而不是 loader/注册/单车/双车的软件兼容性。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# **12. 过程中出现的问题、根因、解决方法与经验**

| **问题**                           | **根因/现象**                                                | **最终解决**                                                                       |
|------------------------------------|--------------------------------------------------------------|------------------------------------------------------------------------------------|
| Full build rc=137 / Killed         | 低资源容器实际 memory.max=2 GiB，free -h 却显示宿主机 1 TiB  | 检查 cgroup；开 80 GiB/15 vCPU 实例；Full build 约 24 s，峰值约 1.6 GiB cgroup     |
| nproc=192 误导                     | 看到宿主机逻辑核而非配额                                     | 以 cpu.max=1500000 100000 解释为约 15 vCPU                                         |
| /usr/bin/time 不存在               | build_rc=127，实际上 converter 未运行                        | 不用推断为 build 失败；改用 shell time/Python 资源监控                             |
| Endpoint error 126                 | 共享 topology node 的 lane 端点 XY 不完全相同                | canonical XY + endpoint-only snap；阈值 0.25 m；添加 snap metrics                  |
| Coverage missing 49                | load/unload/aux semantic layer 名称映射遗漏                  | 显式 source→semantic mapping                                                       |
| 8 个 boundary parent 错挂          | 只按 object ID 跨 category 搜索，忽略 rgn_type               | rgn_type + rgn_objectid；invalid/missing 不跨类别猜测                              |
| Whole polygon mask 不可信          | 官方广东/江西 polygon 内存在大量内部不可行驶区域；无生成算法 | 停止 production 声明；创建明确 DEV_ONLY corridor 规则                              |
| Rasterio PNG BufferedDatasetWriter | 直接 window 写 PNG 不能证明 bounded-memory                   | temporary tiled GeoTIFF → GDAL CreateCopy PNG                                      |
| 空 tile rasterize 异常             | rasterize(\[\]) ValueError                                   | empty shapes → zeros tile                                                          |
| Pillow DecompressionBombError      | Full mask 1.964B 像素超过默认 MAX_IMAGE_PIXELS               | Image.MAX_IMAGE_PIXELS=None；MineSim loader 本身也这么处理                         |
| get_maps_api wrapper 返回 None     | MineSimMap.load_bitmap_using_utm_local_range() 不返回 array  | 从 m.raster_bit_map.image_ndarray_local 读取结果                                   |
| planner.initialize 卡住            | get_polygon_token_using_node 对 400k node 重复线性扫描       | 使用已有 token2ind O(1)；commit 32fb429；J117 回归 PASS                            |
| J117 alias 混淆                    | Full-Mine 初期借 geojson_j117_pilot registry                 | 建立 geojson_full_mine_dev 独立 semantic/mask/version/vehicle 注册；commit d81c571 |
| 长 heredoc/长代码块乱码            | 聊天 UI 粘贴时行被拼接、终端输出被重复粘回 Bash              | 后续命令改成短块；一步一块；只复制代码块，不复制 prompt/output                     |
| 误生成空文件 0.1                   | 终端输出/命令片段误粘                                        | 先 ls/file/sed 检查，再 rm；禁止看到 untracked 就直接删                            |
| sha256sum -L 不支持                | 工具参数假设错误                                             | sha256sum 默认跟随 symlink；使用普通 sha256sum                                     |

# **13. 用户工作流与 Codex 成本控制规范（必须继承）**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>工作宗旨</strong></p>
<p>已知事实不重复；已验证阶段不重述；一次只让 Codex 做当前一个最小步骤；AI 负责判断和关键代码，终端负责执行与验证；便宜模型常驻，贵模型按需升级。</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

| **规则**       | **具体执行**                                                                   |
|----------------|--------------------------------------------------------------------------------|
| 默认模型       | gpt-5.6-luna medium                                                            |
| 升级策略       | Luna capacity/复杂算法/顽固 bug/关键复核时临时 Terra/Sol；完成立即切回 Luna    |
| Codex 任务粒度 | 只做一个最小 read-only audit 或一个最小 patch；禁止全仓重复扫描                |
| Codex 输出     | 只要 PASS/FAIL + 必要字段；不要求长报告                                        |
| 机械操作       | Git/status/hash/file existence/py_compile/现成脚本/full build/长仿真由终端执行 |
| 长任务         | 尽量终端前台或 screen 后台；Codex 不等待长时间仿真                             |
| 失败处理       | 只定位当前故障；不因一个失败回滚到全流程重审                                   |
| 文件位置       | 大文件/日志/脚本/结果放 /root/autodl-tmp；repo 只保留生产源码                  |
| 阶段冻结       | PASS 后 commit/tag/hash/bundle；下一阶段不重跑冻结阶段                         |
| 终端交互       | 命令短块；只复制代码块；不要把 AutoDL 提示、prompt、终端输出再次粘回 Bash      |

## **13.1 Codex 最小提示词模板**

> \<PHASE\> targeted task.  
> Use gpt-5.6-luna medium.  
>   
> Repo: /root/MineSim-Dynamic  
> Expected HEAD: \<current HEAD\>  
>   
> Do ONLY:  
> - \<当前唯一目标\>  
>   
> Allowed:  
> - inspect only necessary files  
> - edit only \<exact file\> if needed  
> - py_compile / tiny smoke  
>   
> Do NOT:  
> - re-audit completed phases  
> - run full build/simulation/MCTS  
> - modify unrelated files  
> - write long report  
>   
> Return ONLY:  
> PASS or FAIL  
> modified:  
> - ...  
> evidence:  
> - ...  
> repo_unchanged:  
> - true/false

# **14. AI/工程人员云端接手 SOP**

## **14.1 Step 1：确认环境与仓库**

> source /root/miniconda3/etc/profile.d/conda.sh  
> conda activate minesim  
> cd /root/MineSim-Dynamic  
> export PYTHONPATH=/root/MineSim-Dynamic  
>   
> git rev-parse HEAD  
> git status --short  
> git show --no-patch --decorate fullmine-dev-runtime-pass-20260811  
> cat /sys/fs/cgroup/memory.max  
> cat /sys/fs/cgroup/cpu.max

期望：HEAD=d81c571...；repo clean；tag 指向当前 commit。若不一致，先查原因，不要 reset。

## **14.2 Step 2：确认冻结资产与哈希**

> cat /root/autodl-tmp/fullmine_dev_runtime_PASS_20260811.txt  
> sha256sum /root/autodl-tmp/new_map_phase6f8_full_mine_dev/maps/semantic_map/geojson_full_mine_dev_semantic_map.json  
> sha256sum /root/autodl-tmp/new_map_phase6f8_full_mine_dev/maps/bitmap/geojson_full_mine_dev_bitmap_mask.png  
> git bundle verify /root/autodl-tmp/MineSim-Dynamic_fullmine_dev_runtime_20260811.bundle

## **14.3 Step 3：当前资产树**

> /root/autodl-tmp/  
> ├─ 地图新建相关文件.zip  
> ├─ new_map_phase6c_tools/  
> │ └─ build_full_mine_structural.py  
> ├─ new_map_phase6c_full_mine_structural/  
> │ ├─ semantic_map/geojson_full_mine_structural_semantic_map.json  
> │ ├─ validation/  
> │ ├─ conversion_manifest.json  
> │ └─ source_manifest.json  
> ├─ new_map_phase6f4_tools/  
> │ └─ build_dev_fullmine_mask.py  
> ├─ new_map_phase6f4_dev_mask/  
> │ └─ bitmap/geojson_full_mine_dev_only_mask.png  
> ├─ new_map_phase6f8_full_mine_dev/maps/  
> │ ├─ semantic_map/geojson_full_mine_dev_semantic_map.json  
> │ └─ bitmap/geojson_full_mine_dev_bitmap_mask.png -\> phase6f4 physical PNG  
> ├─ fullmine_dev_runtime_PASS_20260811.txt  
> └─ MineSim-Dynamic_fullmine_dev_runtime_20260811.bundle

## **14.4 Step 4：如果只是继续开发，不要重跑以下项目**

- Full-Mine structural build 与 endpoint/coverage/boundary-parent validators。

- Full-Mine DEV mask build、local/full loader smoke。

- J117 Phase 5 MCTS 5-seed robustness。

- Full-Mine single-ego 1 step / 5 s 与 dual-ego 1 step / 5 s。

- geojson_full_mine_dev registry smoke。

## **14.5 Step 5：何时需要重新开高资源实例**

| **任务**                                    | **低资源可做？** | **建议**                              |
|---------------------------------------------|------------------|---------------------------------------|
| 代码阅读/小 patch/git                       | 是               | 无需开卡                              |
| Full structural rebuild                     | 不建议 2 GiB     | 开 ≥8 GiB；之前 80 GiB/15vCPU 约 24 s |
| Full mask build                             | 否               | 开高资源；生成约 1m47s                |
| Full mask load / CollisionLookup 5s runtime | 否               | 需要 \>8 GiB；实测峰值 RSS≈7.87 GiB   |
| Codex 只读                                  | 通常是           | Luna medium；不要为 Codex 本身开 GPU  |

# **15. 当前明确未完成项与下一阶段建议**

## **15.1 Production validity：最重要的未完成项**

当前 Full-Mine DEV mask 的 production_validity=false。要达到与 guangdong_dapai / jiangxi_jiangtong 同级别的生产地图，必须获得至少一种权威输入：原始 drivable-surface / terrain classification、内部 obstacle/restricted polygon、官方 mask、或官方/地图提供方的 mask authoring rule。仓库和当前 GeoJSON 无法唯一恢复官方内部 exclusions。

## **15.2 下一步优先级**

| **优先级** | **任务**                       | **说明**                                                                                                                                         |
|------------|--------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------|
| P0         | 扩大 Full-Mine 路线覆盖测试    | 当前 runtime 主要证明 J117 路线区域在 Full-Mine map 上可用；应选 road/junction/load/unload/auxiliary 多个区域建立代表性 scenario，逐步覆盖全矿。 |
| P0         | 获取 authoritative drivability | 向地图提供方要 production mask / drivable surface / internal exclusions / 生成规则。                                                             |
| P1         | road 484 源数据修复            | 确认 polygon、lanes 6942/6989、road boundary 的权威版本；修复后再纳入 DEV/production mask。                                                      |
| P1         | gear=-1 运营方向               | 需要权威文档/规则，决定是否影响 planner route direction。                                                                                        |
| P1         | auxiliary_area API             | 若后续任务需要加油区/辅助区语义查询，应扩展 MineSimMapLayer/semantic API。                                                                       |
| P2         | 车辆模型策略                   | 当前 Full-Mine DEV alias 使用 XG90G；若真实矿区车辆为 NTE200 或其它车型，需要建立独立 vehicle config，而不是继续 alias。                         |
| P2         | 重新跑 Full-Mine MCTS          | 只有在多区域 runtime/route coverage 稳定后再做；J117 MCTS 已冻结，不需重跑。                                                                     |

## **15.3 任何 AI 的下一步决策树**

1.  先确认用户要的是“软件链继续开发”还是“production 地图真实性”。

2.  若是软件链：直接从新的代表性 Full-Mine route/scenario 开始，不再碰 structural/mask 基线。

3.  若是 production：先索取权威 mask/drivable surface；拿不到就保持 DEV_ONLY 标签，不允许伪造 production 结论。

4.  若出现回归：只定位当前层（semantic / bitmap / loader / planner / multi-ego），用 J117 与 frozen Full-Mine 结果做对照。

5.  任何 production 源码修改先在 /root/autodl-tmp harness 验证，再进入 repo；完成后跑 J117 regression，再 commit/tag。

# **16. 关键技术细节速查**

## **16.1 Full-Mine structural counts**

> node 400744  
> polygon 177  
> road 93  
> intersection 35  
> loading_area 36  
> unloading_area 7  
> auxiliary_area 6  
> dubins_pose 565  
> reference_path 540  
> borderline 388  
> explicit_exclusions 21

## **16.2 Full-Mine validation invariants**

> path_endpoint_errors = \[\]  
> source_coverage_missing = \[\]  
> dangling_references = \[\]  
> bidirectional_failures = \[\]  
> wrong_source_boundary_parent_count = 0  
> endpoint_snap_count = 134  
> endpoint_snap_max_m = 0.14390733467273362  
> endpoint_snap_mean_m = 0.025161574670629818

## **16.3 Mask contract**

> mode: L (8-bit grayscale)  
> stored 0 -\> runtime False -\> collision / non-drivable  
> stored 255 -\> runtime True -\> free / drivable  
> scale: 10 px/m (0.1 m/pixel)  
> stored PNG: normal top-down  
> runtime array: row 0 = min local Y after flipud  
> logical pixel_x = int((x - local_x_min) \* 10)  
> logical pixel_y = int((y - local_y_min) \* 10)

## **16.4 Current route token mapping**

> Route A:  
> 6670 -\> path-000426  
> 6674 -\> path-000430  
> 5690 -\> path-000330  
>   
> Route B:  
> 5691 -\> path-000331  
> 6546 -\> path-000403  
> 6523 -\> path-000387

# **17. 证据来源与日志索引**

本文基于用户上传的源地图包与会话中导出的真实终端/Codex 日志编写。以下是接手时最有价值的证据文件（会话附件名称），用于追溯某个结论的原始输出。

| **证据文件**                               | **主要内容**                                                     |
|--------------------------------------------|------------------------------------------------------------------|
| 地图新建相关文件.zip                       | 原始 8 类 GeoJSON 源数据                                         |
| 粘贴的文本 (1)(20260810-161150).txt        | Phase 6A J117→Full-Mine 泛化审计、源缺陷与最小计划               |
| 粘贴的文本 (1)(20260811-011010).txt        | OOM/资源诊断、源文件大小与 1,118,211 坐标点统计                  |
| 粘贴的文本 (1)(20260811-011639).txt        | 第一次 Full-Mine build 与结构 counts / validation                |
| 粘贴的文本 (1)(20260811-011734).txt        | endpoint/coverage 失败诊断                                       |
| 粘贴的文本 (1)(20260811-011842).txt        | 126 endpoint discrepancy 量级统计                                |
| 粘贴的文本 (1)(20260811-015532).txt        | production loader / bitmap contract / registry / 10 px/m 审计    |
| 粘贴的文本 (1)(20260811-021641).txt        | road/junction/load/unload/aux drivability evidence、road484 问题 |
| 粘贴的文本 (1)(20260811-024608).txt        | 官方 production mask generation pipeline 不存在的审计            |
| 粘贴的文本 (1)(20260811-031758).txt        | corridor 校准、3.5 m 结论、DEV mask generator 代码创建           |
| 粘贴的文本 (1)(20260811-034831).txt        | Full mask build、Pillow 大图问题、PNG 生成结果                   |
| 粘贴的文本 (1)(20260811-035724/035834).txt | bitmap registry、local crop loader 真实实现                      |
| 粘贴的文本 (1)(20260811-040515).txt        | J117 runtime harness 搜索与 ScenarioFileBaseInfo 使用            |
| 粘贴的文本 (1)(20260811-041102).txt        | Full-Mine one-step harness patch                                 |
| 粘贴的文本 (1)(20260811-103950).txt        | single 5 s harness 结构                                          |
| 粘贴的文本 (1)(20260811-111301).txt        | dual harness 结构与 50-step 改造依据                             |
| 粘贴的文本 (1)(20260811-112721).txt        | Full-Mine DEV package 创建与 metadata                            |
| 粘贴的文本 (1)(20260811-112916).txt        | geojson_full_mine_dev registry 修改与 local registration PASS    |

## **17.1 信息边界**

凡本文标注为“生产未验证/未知/需要权威输入”的事项，均不得被后续 AI 用一般常识补全。尤其是 production mask 内部 exclusions、gear=-1 的运营方向、源 Z datum、road484 的真实几何与 auxiliary_area 的业务语义。若用户后续提供新的权威资料，应在保留现有 DEV baseline 的前提下单独建立新版本。

**交接基线结束**

下一位 AI：先验证 HEAD / tag / hashes，再只推进“当前一个最小步骤”。
