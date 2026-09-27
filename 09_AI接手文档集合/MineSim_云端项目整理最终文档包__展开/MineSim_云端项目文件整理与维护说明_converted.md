**MineSim 云端项目文件整理与维护说明**

安全整理终版 · 2026-08-16

<table>
<colgroup>
<col style="width: 50%" />
<col style="width: 50%" />
</colgroup>
<thead>
<tr class="header">
<th>最终健康状态<br />
<strong>PASS</strong></th>
<th>科研文件删除<br />
<strong>0</strong></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>顶层条目<br />
<strong>约 530 → 121</strong></td>
<td>安全移动/隔离记录<br />
<strong>423</strong></td>
</tr>
</tbody>
</table>

**整理原则：文件不丢失 \> 项目不受影响 \> 可恢复 \> 目录整洁 \> 磁盘释放**

# **1. 整理结果总览**

首次盘点时 \`/root/autodl-tmp\` 顶层约有 530 个条目；最终 closeout 时为 121 个，减少 409 个（约 77.2%）。整个整理过程共记录 423 项移动/隔离操作，科研文件删除数始终为 0。

| **指标**                    | **结果**                                    |
|-----------------------------|---------------------------------------------|
| 正式仓库 HEAD               | 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e    |
| 最终 Git status             | ?? ^C（历史遗留未跟踪文件，整理前后未变化） |
| 最终顶层条目                | 121                                         |
| 最终项目健康检查            | PASS                                        |
| Critical SHA gate           | PASS                                        |
| Runtime symlink gate        | PASS                                        |
| Source compile gate         | PASS                                        |
| Dapai native-reference gate | PASS                                        |
| Restore-script gate         | PASS                                        |

**磁盘空间说明：** 本次坚持 0 删除，因此大量内容只是从顶层移动到 ARCHIVE / QUARANTINE，目录显著变干净，但磁盘空间不会按归档规模释放。

# **2. 最终目录体系**

> /root/autodl-tmp/  
> ├── 00_MineSim_ACTIVE/ \# 当前路径注册、快捷入口、整理工具  
> ├── 10_MineSim_REPORTS/ \# 汇报素材 / 发布备份  
> ├── 90_MineSim_ARCHIVE/ \# 可恢复历史归档  
> ├── 98_MineSim_QUARANTINE/ \# 隔离区，尚未授权删除  
> ├── 99_MineSim_CLEANUP_MANIFEST/ \# 全部整理证据、manifest、restore  
> ├── \[CURRENT REGISTERED ROOTS\] \# 当前科学运行路径，原位保持  
> └── \[HARD HOLD / REVIEW\] \# 兼容性优先，暂不移动

没有把全部 MineSim 文件强制塞进 5 个组织目录，是有意设计：当前实验中仍存在绝对路径、历史冻结 runner 和 runtime 软链接。为了可复现性，CURRENT 和 HOLD 对象继续保持原路径。

# **3. 当前路径注册表（Current Path Registry）**

| **名称**                | **当前路径**                                                          |
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
| cleanup_manifest_root   | /root/autodl-tmp/99_MineSim_CLEANUP_MANIFEST                          |

## **3.1 Runtime 软链接**

以下两条软链接是 FullMine 当前 runtime 的关键入口，后续整理时必须同时检查 raw target 与 resolved target。

| **Runtime 入口**                                                                                                         | **Resolved target**                                                                                                        |
|--------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------|
| /root/autodl-tmp/fullmine_vector_v2_targeted_runtime/maps/semantic_map/geojson_full_mine_vector_v2_dev_semantic_map.json | /root/autodl-tmp/new_map_fullmine_vector_v2_dev/maps/semantic_map/geojson_full_mine_vector_v2_dev_semantic_map.json        |
| /root/autodl-tmp/fullmine_vector_v2_targeted_runtime/maps/bitmap/geojson_full_mine_vector_v2_dev_bitmap_mask.png         | /root/autodl-tmp/fullmine_vector_v4_d_current_planner_patch_candidate/bitmap/geojson_full_mine_vector_v2_dev_only_mask.png |

# **4. 冻结与关键资产**

最终 closeout 对以下关键资产逐项重新计算 SHA256，并与冻结值比较，全部 PASS。

| **资产**                | **SHA256**                                                       |
|-------------------------|------------------------------------------------------------------|
| scenario                | 362eff18c7ccc88ea8dfaf083a517603566516943690d5cbe76bd1a97afc89e1 |
| scenario_manifest       | 0bde6bb1e869c3cf583947203dd41a8fc364f0a2a8130617baebd0b1e6cbad2e |
| nomcts_result           | 060880c8edc851e05606871cb647058d091ce8737f952b9864cc94e9d6fcfd13 |
| fleet_result            | 2eeb28e1fcb1c48d826c387853ec4f9a8a1acf07c9d7e7d1c067701bd4a1398f |
| freeze_v2               | b89d290c9cb06d1efb99688ee27b23898ab81d11e36023832477dc2fc834364b |
| semantic_runtime        | b85a3d8b28f2252ecb5bda179d514573f6333079def838cd048566f556d95cd0 |
| bitmap_runtime          | 51abcd5a86e5c510204a5dacc873691506d721f98982ab7f98585d4e0f7efdd0 |
| native_video_v2_release | f695ba22ecd61c4a643e8ffecac483bc218de9153f95f88b4e0e3006bca03d58 |

# **5. 组织目录用途**

## **5.1 00_MineSim_ACTIVE**

- 保存 current_paths.json / current_paths.env，作为后续逐模块路径迁移的统一入口。

- 提供 polygon21、cross_scene、runtime、mcts_results、archive、cleanup_manifests 等软链接。

- organization_tools/ 专门保存整理/运维脚本，后续不要再把这类工具散落到 /root/autodl-tmp 顶层。

## **5.2 10_MineSim_REPORTS**

- 只用于汇报、展示和发布备份，不作为核心仿真输入。

- 当前包含 Polygon21 GIF V4 备份；Native MP4 V2 最终 release 继续原位保留并通过 SHA 校验。

## **5.3 90_MineSim_ARCHIVE**

一级归档结构如下：

- 00_organization_tools

- 01_legacy_planner_20260730_0807

- 02_single_vehicle_mcts_20260807

- 03_j117_20260809_0810

- 04_fullmine_map_development_20260809_0813

- 05_superseded_report_media

- 06_dr_and_bundles

- ARCHIVE_INDEX.md

归档内容不是垃圾：它们保留了历史实验、旧 planner、J117 调试链、FullMine 地图开发过程、被替代的汇报媒体、DR/bundle 等可复现证据。

## **5.4 98_MineSim_QUARANTINE**

当前隔离区约 315.76 MB，尚未授权删除。直接子项：

| **对象**                  | **大小**  |
|---------------------------|-----------|
| arnings.filterwarnings(\\ | 0.00 MB   |
| npm-cache                 | 127.41 MB |
| v4_dr_restore_test_aDH7P8 | 188.35 MB |

## **5.5 99_MineSim_CLEANUP_MANIFEST**

保存各阶段审计、move plan、pre/post fingerprint、回滚证据、最终 health report 与恢复脚本。此目录是整个整理过程的 provenance，应长期保留。

# **6. 整理阶段记录**

| **阶段** | **状态** | **移动/隔离** | **删除** | **主要动作**                                                 |
|----------|----------|---------------|----------|--------------------------------------------------------------|
| 2A       | PASS     | 222           | 0        | 归档早期 planner / fairness / superseded media；全量指纹校验 |
| 2B       | PASS     | 3             | 0        | 3 个明确临时对象进入可逆隔离区                               |
| 2C       | PASS     | 28            | 0        | 归档 28 个旧地图开发阶段对象；有引用的对象自动 HOLD          |
| 2E       | PASS     | 8             | 0        | 收纳 8 个整理工具并进行精确绝对路径依赖审计                  |
| 2F       | PASS     | 12            | 0        | 12 个小规模高置信历史/汇报对象归档                           |
| 2I       | PASS     | 3             | 0        | 3 个大对象安全归档；重复/DR 等价关系重新验证                 |
| 2J       | PASS     | 147           | 0        | 147 个零精确依赖历史调试/证据对象最终批量归档，并做回归 gate |

2D、2G、2H、2K 为只读审计/最终验收阶段，没有执行科研对象移动。

# **7. 最终顶层分类**

| **分类**                    | **数量** | **大小**  | **处理原则**                                   |
|-----------------------------|----------|-----------|------------------------------------------------|
| CURRENT_REGISTERED          | 10       | 1.35 GB   | 当前注册路径，原位保持                         |
| HARD_HOLD                   | 26       | 373.23 MB | 有历史唯一性/真实引用/兼容性原因，禁止贸然移动 |
| ORGANIZATION_INFRASTRUCTURE | 5        | 1.32 GB   | 整理体系本身                                   |
| OUTSIDE_MINESIM_SCOPE       | 7        | 1.79 GB   | 其他项目或环境，不属于本次 MineSim 整理范围    |
| REMAINING_SUPPORT_OR_REVIEW | 73       | 111.86 MB | 支持性/用途待确认内容，安全起见原位保留        |

# **8. HARD HOLD：不得直接移动或删除**

以下 26 个对象被最终 closeout 明确保留。HOLD 的含义是“安全优先，暂不处理”，并不代表它们永远不能迁移。

| **名称**                                                                                 | **大小**  |
|------------------------------------------------------------------------------------------|-----------|
| MineSim-Dynamic                                                                          | 203.75 MB |
| new_map_phase6c_full_mine_structural                                                     | 123.80 MB |
| fullmine_vector_v4_final_dr_20260814.tar.gz                                              | 41.55 MB  |
| .autodl                                                                                  | 2.50 MB   |
| fullmine_v4_coverage_tools                                                               | 0.59 MB   |
| out_case1                                                                                | 0.29 MB   |
| planner_checkpoints                                                                      | 0.27 MB   |
| idm_analysis                                                                             | 0.12 MB   |
| .ipynb_checkpoints                                                                       | 0.10 MB   |
| polygon21_native_video_source_bundle_v1.zip                                              | 0.06 MB   |
| polygon21_native_video_production_v2.py                                                  | 0.05 MB   |
| new_map_phase4c_tools                                                                    | 0.04 MB   |
| zt_dro_case2_sweep.py                                                                    | 0.03 MB   |
| fullmine_v4_representative_route_candidate_generator.py.before_selection_fix_4925904f.py | 0.02 MB   |
| fullmine_v4_representative_route_candidate_generator_v3.py                               | 0.02 MB   |
| Polygon21_Native_Video_Production_Scripts_v2.zip                                         | 0.02 MB   |
| derived_multi_tasks                                                                      | 0.01 MB   |
| a_route_parity_current                                                                   | 0.01 MB   |
| a_route_parity_current.log                                                               | 0.00 MB   |
| codex-env.sh                                                                             | 0.00 MB   |
| POLYGON21_NATIVE_VIDEO_V2_README.txt                                                     | 0.00 MB   |
| run_polygon21_native_video_v2.sh                                                         | 0.00 MB   |
| mcts_checkpoints                                                                         | 0.00 MB   |
| mcts_data                                                                                | 0.00 MB   |
| multi_b_route_input                                                                      | 0.00 MB   |
| out_case2_dro                                                                            | 0.00 MB   |

其中最关键的 5 类：

- \`MineSim-Dynamic\`（/root/autodl-tmp 下旧副本）：独立脏历史工作区，不是正式仓库的简单重复。

- \`new_map_phase6c_full_mine_structural\`：历史保护链保留。

- \`new_map_phase4c_tools\`：精确审计确认存在真实当前引用，须先迁移引用。

- \`fullmine_vector_v4_final_dr_20260814.tar.gz\`：完整 compact DR 恢复包，继续保留。

- Polygon21 Native Video V2 的生产脚本、脚本包与 source bundle：构成最终汇报视频的可复现链。

# **9. 剩余 Support / Review**

最终仍有 73 个顶层支持性或待复核对象（约 111.86 MB）。它们未被强制归档，原因是用途/历史关系尚不足以支持无风险迁移。

| **名称**                                                               | **大小** |
|------------------------------------------------------------------------|----------|
| mcts_quality_benchmark_v1_20260806                                     | 29.64 MB |
| fair_runtime_audit_dapai_20260806                                      | 23.87 MB |
| Polygon21_Native_MineSim_Report_Video_v2_20260816_161259.zip           | 9.63 MB  |
| jiangtong_online_frenet_memorysafe_20260806                            | 7.06 MB  |
| minesim_p0_preflight                                                   | 6.92 MB  |
| mcts_budget_ablation_20260807                                          | 5.82 MB  |
| online_frenet_v1_smoke_20260806                                        | 4.69 MB  |
| new_map_phase2_j117                                                    | 3.57 MB  |
| new_map_phase3_maps                                                    | 3.22 MB  |
| fullmine_vector_v2_additive_patch_candidate                            | 2.94 MB  |
| new_map_phase6f4_dev_mask                                              | 2.94 MB  |
| fullmine_vector_v2_dev_mask                                            | 2.68 MB  |
| new_map_phase5d_tools                                                  | 1.97 MB  |
| jiangtong_online_five_planner_full_20260806                            | 1.60 MB  |
| dapai_online_four_planner_full_20260806                                | 1.35 MB  |
| fair_planner_audit_20260806                                            | 0.79 MB  |
| \_\_pycache\_\_                                                        | 0.77 MB  |
| mcts_two_scenario_final_summary_20260807                               | 0.58 MB  |
| fullmine_vector_v2_dev                                                 | 0.19 MB  |
| j117_full_context_audit.txt                                            | 0.15 MB  |
| mcts_analysis                                                          | 0.13 MB  |
| mcts_analysis_fixed                                                    | 0.13 MB  |
| j117_phase5_untracked_archive_20260810                                 | 0.09 MB  |
| jiangtong_frenet_single_input_20260806                                 | 0.09 MB  |
| new_map_phase2_build_tools                                             | 0.08 MB  |
| new_map_phase6g_runtime                                                | 0.08 MB  |
| dapai_three_planner_smoke_input                                        | 0.06 MB  |
| j117_phase5_final_backup_20260810                                      | 0.06 MB  |
| mcts_idm_native_full_comparison.py                                     | 0.05 MB  |
| j117_multi_ego_source_contract_v1.txt                                  | 0.04 MB  |
| maneuver_sat_rear_axle_center_v4_20260805_223049                       | 0.04 MB  |
| new_map_phase5c_tools                                                  | 0.04 MB  |
| new_map_phase4b_j117                                                   | 0.04 MB  |
| common_predictor_real_scene_audit_20260806                             | 0.04 MB  |
| fair_mcts_object_filter_audit_20260806                                 | 0.03 MB  |
| fair_mcts_radius_filter_audit_20260806                                 | 0.03 MB  |
| fair_mcts_effective_config_20260806                                    | 0.03 MB  |
| new_map_phase3_j117                                                    | 0.03 MB  |
| new_map_phase3_tools                                                   | 0.03 MB  |
| fair_maneuver_effective_config_20260806                                | 0.02 MB  |
| check_bg1_aligned_physical_gate.py                                     | 0.02 MB  |
| check_bg1_aligned_projected_gate.py                                    | 0.02 MB  |
| fair_frenet_effective_config_20260806                                  | 0.02 MB  |
| fair_idm_effective_config_20260806                                     | 0.02 MB  |
| five_planner_benchmark.py                                              | 0.02 MB  |
| fullmine_v4_representative_route_candidate_generator.py                | 0.02 MB  |
| jiangtong_temporal_feasibility_v22_step2b.py                           | 0.02 MB  |
| minesim_p0_preflight.zip                                               | 0.02 MB  |
| jiangtong_spatial_conflict_v22_step2a.log                              | 0.02 MB  |
| mcts_native_render_smoke_5steps.py                                     | 0.02 MB  |
| test.py                                                                | 0.02 MB  |
| j117_phase6b_preflight.py                                              | 0.01 MB  |
| new_map_phase5b_tools                                                  | 0.01 MB  |
| check_bg1_aligned_physical_gate.log                                    | 0.01 MB  |
| check_bg1_aligned_projected_gate.log                                   | 0.01 MB  |
| five_planner_factory.py                                                | 0.01 MB  |
| frenet_safe_resample_dapai_full199_20260806_094110.log                 | 0.01 MB  |
| frenet_safe_resample_jiangtong_full249_20260806_100618.log             | 0.01 MB  |
| frenet_safe_resample_patch_20260806                                    | 0.01 MB  |
| maneuver_jiangtong_full249_20260806_103715.log                         | 0.01 MB  |
| mcts_native_render_smoke_5steps.log                                    | 0.01 MB  |
| simple_jiangtong_full249_20260806_112642.log                           | 0.01 MB  |
| simple_scenario_vehicle_patch_20260806                                 | 0.01 MB  |
| v21.py                                                                 | 0.01 MB  |
| jiangtong_temporal_feasibility_v22_step2b.log                          | 0.00 MB  |
| jiangtong_temporal_feasibility_v22_step2b_before_production_loader.log | 0.00 MB  |
| jiangtong_v22_step2b_final_summary_20260809.md                         | 0.00 MB  |
| jiangtong_v22_step2b_log_index_20260809.txt                            | 0.00 MB  |
| n2_h8_margin55_seed5_19.log                                            | 0.00 MB  |
| simple_dapai_full199_20260806_112107.log                               | 0.00 MB  |
| mcts_smoke_dapai_inputs                                                | 0.00 MB  |
| mcts_smoke_jiangtong_inputs                                            | 0.00 MB  |
| Untitled Folder                                                        | 0.00 MB  |

# **10. 恢复机制**

每个有移动动作的阶段都保留 RESTORE 脚本。发生兼容性问题时，应优先按原 manifest 逆向恢复，而不是手工复制。

| **阶段** | **恢复脚本**                                                                                               |
|----------|------------------------------------------------------------------------------------------------------------|
| 2A       | /root/autodl-tmp/99_MineSim_CLEANUP_MANIFEST/phase2a_safe_move_20260816_165421/RESTORE_PHASE2A.sh          |
| 2B       | /root/autodl-tmp/99_MineSim_CLEANUP_MANIFEST/phase2b_safe_quarantine_20260816_170221/RESTORE_PHASE2B.sh    |
| 2C       | /root/autodl-tmp/99_MineSim_CLEANUP_MANIFEST/phase2c_safe_map_archive_20260816_170828/RESTORE_PHASE2C.sh   |
| 2F       | /root/autodl-tmp/99_MineSim_CLEANUP_MANIFEST/phase2f_safe_housekeeping_20260816_172708/RESTORE_PHASE2F.sh  |
| 2I       | /root/autodl-tmp/99_MineSim_CLEANUP_MANIFEST/phase2i_safe_large_archive_20260816_174051/RESTORE_PHASE2I.sh |
| 2J       | /root/autodl-tmp/99_MineSim_CLEANUP_MANIFEST/phase2j_final_safe_archive_20260816_174626/RESTORE_PHASE2J.sh |

- 恢复前先确认原路径不存在新的同名对象。

- 运行对应 RESTORE_PHASE\*.sh。

- 恢复后重新验证 Git HEAD/status、关键 SHA 与 runtime symlink。

- 任何冻结实验如果要复现，优先恢复历史路径，而不是修改冻结 runner。

# **11. 后续文件放置规范**

| **类型**              | **推荐位置/规则**                                                                  |
|-----------------------|------------------------------------------------------------------------------------|
| 新/current 科学工作   | 优先建立版本化 workspace 并注册进 current_paths.json；不要重新把大量实验散落顶层。 |
| 汇报图/视频/PPT       | /root/autodl-tmp/10_MineSim_REPORTS/\<topic\>/                                     |
| 历史实验/被替代版本   | /root/autodl-tmp/90_MineSim_ARCHIVE/\<category\>/                                  |
| 暂不能删的临时内容    | /root/autodl-tmp/98_MineSim_QUARANTINE/                                            |
| 审计/manifest/restore | /root/autodl-tmp/99_MineSim_CLEANUP_MANIFEST/                                      |
| 整理/运维脚本         | /root/autodl-tmp/00_MineSim_ACTIVE/organization_tools/                             |

# **12. 路径迁移规则**

- 禁止全仓库 grep 后全局替换 /root/autodl-tmp 的旧绝对路径。

- 冻结 runner、result、map、freeze/tag 证据不因目录美观而改动。

- 当前开发代码按模块逐个迁移到 current_paths.env / current_paths.json。

- 每迁移一个模块，先跑相应 regression，再处理下一个模块。

- 只有当旧路径的精确文本引用与外部 symlink 引用都归零后，才进入归档评估。

# **13. 磁盘清理建议（当前未执行）**

当前目录治理已经完成，但“归档”不会释放空间。若以后确实需要腾磁盘，应另开删除审批流程。

- 优先审查 98_MineSim_QUARANTINE（约 315.76 MB），其中 npm-cache 和 restore test 是最可能的删除候选。

- 删除前要确认对应正式 DR/tar、freeze、恢复证据仍完整。

- 不要直接删除旧 MineSim-Dynamic、受保护地图、DR tar、冻结 result/log 或 provenance 目录。

- 建议删除也继续保留 deletion manifest + SHA + 审批记录。

# **14. 最终结论**

- /root/autodl-tmp 顶层由约 530 项降至 121 项，减少 409 项（约 77.2%）。

- 已记录 423 项安全移动/隔离操作，科研文件删除始终为 0。

- 正式仓库、Polygon21、cross-scene、MCTS results、FullMine runtime 与 Dapai native reference 均通过最终健康检查。

- 当前应停止为了“更整齐”继续大规模搬文件；后续优先推进科研任务，路径只在实际维护模块时逐步迁移。
