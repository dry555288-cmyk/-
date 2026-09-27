# MineSim 云端项目文件整理与维护说明

> 最终状态：**PASS**。本次整理以“文件不丢失、当前项目不受影响、路径逐步迁移”为第一原则。整个整理过程未删除科研文件。

## 1. 整理结果总览

| 指标 | 最终结果 |
|---|---:|
| 首次盘点顶层条目 | 约 530 项 |
| 最终顶层条目 | 121 项 |
| 顶层减少 | 409 项（77.2%） |
| 已记录移动/隔离操作 | 423 项 |
| 科研文件删除 | **0** |
| 正式仓库 HEAD | `112d2bd0f3412fc83b13d5587d2b41402d2d0f5e` |
| 最终项目健康检查 | **PASS** |

**重要说明：** 本次工作重点是安全归档和目录治理，不是强制释放磁盘空间。由于没有执行删除，归档和隔离内容仍占用磁盘；后续如需清空间，应另做“删除审批”，不能直接删除归档或 HOLD 内容。

## 2. 当前目录体系

```text
/root/autodl-tmp/
├── 00_MineSim_ACTIVE/              # 当前路径注册、快捷入口、整理工具
├── 10_MineSim_REPORTS/             # 汇报素材/发布备份
├── 90_MineSim_ARCHIVE/             # 可恢复历史归档
├── 98_MineSim_QUARANTINE/          # 隔离区，尚未授权删除
├── 99_MineSim_CLEANUP_MANIFEST/    # 全部整理证据、manifest、restore 脚本
├── [CURRENT REGISTERED ROOTS]       # 当前运行路径，保持原位
└── [HARD HOLD / REVIEW]             # 为保证兼容性暂不移动
```

之所以没有把所有文件强行塞进五个目录，是为了避免破坏历史脚本中的绝对路径、runtime 软链接以及冻结实验的可复现性。

## 3. 当前路径注册表

| 名称 | 路径 |
|---|---|
| `formal_repo` | `/root/MineSim-Dynamic` |
| `polygon21_current` | `/root/autodl-tmp/fullmine_v4_dual_candidate_v1` |
| `cross_scene_current` | `/root/autodl-tmp/fullmine_v4_fleet_cross_scene_v1` |
| `representative_mcts` | `/root/autodl-tmp/fullmine_v4_mcts_representative_v1` |
| `representative_coverage` | `/root/autodl-tmp/fullmine_v4_representative_coverage_v1` |
| `production_truth_gap` | `/root/autodl-tmp/fullmine_v4_production_truth_gap_v1` |
| `runtime_current` | `/root/autodl-tmp/fullmine_vector_v2_targeted_runtime` |
| `semantic_source_current` | `/root/autodl-tmp/new_map_fullmine_vector_v2_dev` |
| `bitmap_source_current` | `/root/autodl-tmp/fullmine_vector_v4_d_current_planner_patch_candidate` |
| `formal_mcts_results` | `/root/autodl-tmp/mcts_results` |
| `idm_baseline_backup` | `/root/autodl-tmp/minesim_idm_baseline_backup` |
| `archive_root` | `/root/autodl-tmp/90_MineSim_ARCHIVE` |
| `cleanup_manifest_root` | `/root/autodl-tmp/99_MineSim_CLEANUP_MANIFEST` |

### 3.1 Runtime 软链接（禁止随意修改）

| Runtime 入口 | 当前真实目标 |
|---|---|
| `/root/autodl-tmp/fullmine_vector_v2_targeted_runtime/maps/semantic_map/geojson_full_mine_vector_v2_dev_semantic_map.json` | `/root/autodl-tmp/new_map_fullmine_vector_v2_dev/maps/semantic_map/geojson_full_mine_vector_v2_dev_semantic_map.json` |
| `/root/autodl-tmp/fullmine_vector_v2_targeted_runtime/maps/bitmap/geojson_full_mine_vector_v2_dev_bitmap_mask.png` | `/root/autodl-tmp/fullmine_vector_v4_d_current_planner_patch_candidate/bitmap/geojson_full_mine_vector_v2_dev_only_mask.png` |

## 4. 冻结/关键资产校验

以下对象在最终 closeout 中全部通过 SHA256 校验：

| 资产 | SHA256 |
|---|---|
| `scenario` | `362eff18c7ccc88ea8dfaf083a517603566516943690d5cbe76bd1a97afc89e1` |
| `scenario_manifest` | `0bde6bb1e869c3cf583947203dd41a8fc364f0a2a8130617baebd0b1e6cbad2e` |
| `nomcts_result` | `060880c8edc851e05606871cb647058d091ce8737f952b9864cc94e9d6fcfd13` |
| `fleet_result` | `2eeb28e1fcb1c48d826c387853ec4f9a8a1acf07c9d7e7d1c067701bd4a1398f` |
| `freeze_v2` | `b89d290c9cb06d1efb99688ee27b23898ab81d11e36023832477dc2fc834364b` |
| `semantic_runtime` | `b85a3d8b28f2252ecb5bda179d514573f6333079def838cd048566f556d95cd0` |
| `bitmap_runtime` | `51abcd5a86e5c510204a5dacc873691506d721f98982ab7f98585d4e0f7efdd0` |
| `native_video_v2_release` | `f695ba22ecd61c4a643e8ffecac483bc218de9153f95f88b4e0e3006bca03d58` |

最终还通过了：**runtime symlink gate、关键源码只读编译 gate、current work-root gate、Dapai native-reference gate、restore-script gate**。

## 5. 组织目录用途

### 5.1 `00_MineSim_ACTIVE`

- 保存 `current_paths.json` / `current_paths.env`，作为未来逐步路径治理的统一入口。
- 提供 `polygon21`、`cross_scene`、`runtime`、`mcts_results`、`archive`、`cleanup_manifests` 等快捷软链接。
- `organization_tools/` 保存整理过程脚本；以后不要再把整理工具散落到 `/root/autodl-tmp` 顶层。

### 5.2 `10_MineSim_REPORTS`

- 仅放汇报/发布素材，不作为科学运行输入。
- 当前包含 Polygon21 GIF V4 备份。最终 Native MP4 V2 release 因完整性校验和既有路径约束暂时继续原位保留。

### 5.3 `90_MineSim_ARCHIVE`

当前一级结构：

- `00_organization_tools`
- `01_legacy_planner_20260730_0807`
- `02_single_vehicle_mcts_20260807`
- `03_j117_20260809_0810`
- `04_fullmine_map_development_20260809_0813`
- `05_superseded_report_media`
- `06_dr_and_bundles`
- `ARCHIVE_INDEX.md`

归档原则：历史文件可以移动，但不删除；每次移动均保留 manifest、pre/post fingerprint 与恢复脚本。

### 5.4 `98_MineSim_QUARANTINE`

当前隔离区约 **315.76 MB**，主要包括：

- `arnings.filterwarnings(\`：0.00 MB
- `npm-cache`：127.41 MB
- `v4_dr_restore_test_aDH7P8`：188.35 MB

**隔离不等于删除授权。** 在没有新的显式确认之前，不要清空此目录。

### 5.5 `99_MineSim_CLEANUP_MANIFEST`

- 保存 Phase 1～2K 的审计、移动计划、指纹、回滚记录和最终健康检查。
- 这是整理过程的 provenance 证据目录；应长期保留。

## 6. 整理阶段记录

| 阶段 | 状态 | 移动/隔离项 | 删除 | 主要动作 |
|---|---:|---:|---:|---|
| 2A | PASS | 222 | 0 | 归档早期 planner / fairness / superseded media；全量指纹校验 |
| 2B | PASS | 3 | 0 | 3 个明确临时对象进入可逆隔离区 |
| 2C | PASS | 28 | 0 | 归档 28 个旧地图开发阶段对象；有引用的对象自动 HOLD |
| 2E | PASS | 8 | 0 | 收纳 8 个整理工具并进行精确绝对路径依赖审计 |
| 2F | PASS | 12 | 0 | 12 个小规模高置信历史/汇报对象归档 |
| 2I | PASS | 3 | 0 | 3 个大对象安全归档；重复/DR 等价关系重新验证 |
| 2J | PASS | 147 | 0 | 147 个零精确依赖历史调试/证据对象最终批量归档，并做回归 gate |

读-only 审计阶段（2D、2G、2H、2K）没有执行科研对象移动；2K 为最终 closeout。

## 7. 最终顶层分类

| 分类 | 数量 | 大小 | 处理原则 |
|---|---:|---:|---|
| CURRENT_REGISTERED | 10 | 1.35 GB | 当前注册路径，原位保持 |
| HARD_HOLD | 26 | 373.23 MB | 有历史唯一性/真实引用/兼容性原因，禁止贸然移动 |
| ORGANIZATION_INFRASTRUCTURE | 5 | 1.32 GB | 整理体系本身 |
| OUTSIDE_MINESIM_SCOPE | 7 | 1.79 GB | 其他项目或环境，不属于本次 MineSim 整理范围 |
| REMAINING_SUPPORT_OR_REVIEW | 73 | 111.86 MB | 支持性/用途待确认内容，安全起见原位保留 |

## 8. HARD HOLD：后续禁止直接移动/删除

以下 26 项在最终 closeout 中仍被明确 HOLD：

- `MineSim-Dynamic`（203.75 MB）
- `new_map_phase6c_full_mine_structural`（123.80 MB）
- `fullmine_vector_v4_final_dr_20260814.tar.gz`（41.55 MB）
- `.autodl`（2.50 MB）
- `fullmine_v4_coverage_tools`（0.59 MB）
- `out_case1`（0.29 MB）
- `planner_checkpoints`（0.27 MB）
- `idm_analysis`（0.12 MB）
- `.ipynb_checkpoints`（0.10 MB）
- `polygon21_native_video_source_bundle_v1.zip`（0.06 MB）
- `polygon21_native_video_production_v2.py`（0.05 MB）
- `new_map_phase4c_tools`（0.04 MB）
- `zt_dro_case2_sweep.py`（0.03 MB）
- `fullmine_v4_representative_route_candidate_generator.py.before_selection_fix_4925904f.py`（0.02 MB）
- `fullmine_v4_representative_route_candidate_generator_v3.py`（0.02 MB）
- `Polygon21_Native_Video_Production_Scripts_v2.zip`（0.02 MB）
- `derived_multi_tasks`（0.01 MB）
- `a_route_parity_current`（0.01 MB）
- `a_route_parity_current.log`（0.00 MB）
- `codex-env.sh`（0.00 MB）
- `POLYGON21_NATIVE_VIDEO_V2_README.txt`（0.00 MB）
- `run_polygon21_native_video_v2.sh`（0.00 MB）
- `mcts_checkpoints`（0.00 MB）
- `mcts_data`（0.00 MB）
- `multi_b_route_input`（0.00 MB）
- `out_case2_dro`（0.00 MB）

其中最重要的几项：

- `/root/autodl-tmp/MineSim-Dynamic`：约 203.75 MB，是**独立脏历史工作区**，与正式仓库并非简单重复；不能删除。
- `new_map_phase6c_full_mine_structural`：受早期保护链约束，继续保留。
- `new_map_phase4c_tools`：已确认存在真实当前引用，必须等引用逐模块迁移后再处理。
- `fullmine_vector_v4_final_dr_20260814.tar.gz`：完整 DR 压缩归档，继续作为 compact 恢复证据保留。
- Polygon21 Native Video V2 的生产脚本/脚本包/source bundle：作为最终视频可复现链保留。

## 9. 剩余 Support / Review

最终仍有 73 个顶层支持性或待复核对象，总计约 **111.86 MB**。这些对象没有被强制搬走，是为了避免因用途不明确而破坏后续复现。完整清单如下：

| 名称 | 大小 |
|---|---:|
| `mcts_quality_benchmark_v1_20260806` | 29.64 MB |
| `fair_runtime_audit_dapai_20260806` | 23.87 MB |
| `Polygon21_Native_MineSim_Report_Video_v2_20260816_161259.zip` | 9.63 MB |
| `jiangtong_online_frenet_memorysafe_20260806` | 7.06 MB |
| `minesim_p0_preflight` | 6.92 MB |
| `mcts_budget_ablation_20260807` | 5.82 MB |
| `online_frenet_v1_smoke_20260806` | 4.69 MB |
| `new_map_phase2_j117` | 3.57 MB |
| `new_map_phase3_maps` | 3.22 MB |
| `fullmine_vector_v2_additive_patch_candidate` | 2.94 MB |
| `new_map_phase6f4_dev_mask` | 2.94 MB |
| `fullmine_vector_v2_dev_mask` | 2.68 MB |
| `new_map_phase5d_tools` | 1.97 MB |
| `jiangtong_online_five_planner_full_20260806` | 1.60 MB |
| `dapai_online_four_planner_full_20260806` | 1.35 MB |
| `fair_planner_audit_20260806` | 0.79 MB |
| `__pycache__` | 0.77 MB |
| `mcts_two_scenario_final_summary_20260807` | 0.58 MB |
| `fullmine_vector_v2_dev` | 0.19 MB |
| `j117_full_context_audit.txt` | 0.15 MB |
| `mcts_analysis` | 0.13 MB |
| `mcts_analysis_fixed` | 0.13 MB |
| `j117_phase5_untracked_archive_20260810` | 0.09 MB |
| `jiangtong_frenet_single_input_20260806` | 0.09 MB |
| `new_map_phase2_build_tools` | 0.08 MB |
| `new_map_phase6g_runtime` | 0.08 MB |
| `dapai_three_planner_smoke_input` | 0.06 MB |
| `j117_phase5_final_backup_20260810` | 0.06 MB |
| `mcts_idm_native_full_comparison.py` | 0.05 MB |
| `j117_multi_ego_source_contract_v1.txt` | 0.04 MB |
| `maneuver_sat_rear_axle_center_v4_20260805_223049` | 0.04 MB |
| `new_map_phase5c_tools` | 0.04 MB |
| `new_map_phase4b_j117` | 0.04 MB |
| `common_predictor_real_scene_audit_20260806` | 0.04 MB |
| `fair_mcts_object_filter_audit_20260806` | 0.03 MB |
| `fair_mcts_radius_filter_audit_20260806` | 0.03 MB |
| `fair_mcts_effective_config_20260806` | 0.03 MB |
| `new_map_phase3_j117` | 0.03 MB |
| `new_map_phase3_tools` | 0.03 MB |
| `fair_maneuver_effective_config_20260806` | 0.02 MB |
| `check_bg1_aligned_physical_gate.py` | 0.02 MB |
| `check_bg1_aligned_projected_gate.py` | 0.02 MB |
| `fair_frenet_effective_config_20260806` | 0.02 MB |
| `fair_idm_effective_config_20260806` | 0.02 MB |
| `five_planner_benchmark.py` | 0.02 MB |
| `fullmine_v4_representative_route_candidate_generator.py` | 0.02 MB |
| `jiangtong_temporal_feasibility_v22_step2b.py` | 0.02 MB |
| `minesim_p0_preflight.zip` | 0.02 MB |
| `jiangtong_spatial_conflict_v22_step2a.log` | 0.02 MB |
| `mcts_native_render_smoke_5steps.py` | 0.02 MB |
| `test.py` | 0.02 MB |
| `j117_phase6b_preflight.py` | 0.01 MB |
| `new_map_phase5b_tools` | 0.01 MB |
| `check_bg1_aligned_physical_gate.log` | 0.01 MB |
| `check_bg1_aligned_projected_gate.log` | 0.01 MB |
| `five_planner_factory.py` | 0.01 MB |
| `frenet_safe_resample_dapai_full199_20260806_094110.log` | 0.01 MB |
| `frenet_safe_resample_jiangtong_full249_20260806_100618.log` | 0.01 MB |
| `frenet_safe_resample_patch_20260806` | 0.01 MB |
| `maneuver_jiangtong_full249_20260806_103715.log` | 0.01 MB |
| `mcts_native_render_smoke_5steps.log` | 0.01 MB |
| `simple_jiangtong_full249_20260806_112642.log` | 0.01 MB |
| `simple_scenario_vehicle_patch_20260806` | 0.01 MB |
| `v21.py` | 0.01 MB |
| `jiangtong_temporal_feasibility_v22_step2b.log` | 0.00 MB |
| `jiangtong_temporal_feasibility_v22_step2b_before_production_loader.log` | 0.00 MB |
| `jiangtong_v22_step2b_final_summary_20260809.md` | 0.00 MB |
| `jiangtong_v22_step2b_log_index_20260809.txt` | 0.00 MB |
| `n2_h8_margin55_seed5_19.log` | 0.00 MB |
| `simple_dapai_full199_20260806_112107.log` | 0.00 MB |
| `mcts_smoke_dapai_inputs` | 0.00 MB |
| `mcts_smoke_jiangtong_inputs` | 0.00 MB |
| `Untitled Folder` | 0.00 MB |

## 10. 恢复机制

每个有移动动作的阶段均保留恢复脚本：

| 阶段 | 恢复脚本 |
|---|---|
| 2A | `/root/autodl-tmp/99_MineSim_CLEANUP_MANIFEST/phase2a_safe_move_20260816_165421/RESTORE_PHASE2A.sh` |
| 2B | `/root/autodl-tmp/99_MineSim_CLEANUP_MANIFEST/phase2b_safe_quarantine_20260816_170221/RESTORE_PHASE2B.sh` |
| 2C | `/root/autodl-tmp/99_MineSim_CLEANUP_MANIFEST/phase2c_safe_map_archive_20260816_170828/RESTORE_PHASE2C.sh` |
| 2F | `/root/autodl-tmp/99_MineSim_CLEANUP_MANIFEST/phase2f_safe_housekeeping_20260816_172708/RESTORE_PHASE2F.sh` |
| 2I | `/root/autodl-tmp/99_MineSim_CLEANUP_MANIFEST/phase2i_safe_large_archive_20260816_174051/RESTORE_PHASE2I.sh` |
| 2J | `/root/autodl-tmp/99_MineSim_CLEANUP_MANIFEST/phase2j_final_safe_archive_20260816_174626/RESTORE_PHASE2J.sh` |

恢复原则：

1. 不要直接手工把归档文件拖回去。
2. 先确认当前没有新的同名目标。
3. 使用对应 `RESTORE_PHASE*.sh`，其逆序恢复逻辑与当时 move manifest 一致。
4. 恢复后必须重新跑关键 SHA、runtime symlink 和 Git status 检查。

## 11. 后续文件放置规范

- **当前科学代码/数据**：优先写入已有 current root；对于新主题，优先建立新的版本化 workspace，再写入 `current_paths.json`，不要随意散落顶层。
- **汇报图、视频、PPT 资产**：`/root/autodl-tmp/10_MineSim_REPORTS/<topic>/`。
- **历史实验、被替代版本**：`/root/autodl-tmp/90_MineSim_ARCHIVE/<category>/`。
- **确认是临时但暂不能删的内容**：`/root/autodl-tmp/98_MineSim_QUARANTINE/`。
- **审计/整理 manifest、恢复脚本**：`/root/autodl-tmp/99_MineSim_CLEANUP_MANIFEST/`。
- **整理脚本**：`/root/autodl-tmp/00_MineSim_ACTIVE/organization_tools/`，不要再放顶层。

## 12. 路径迁移规则

- **禁止**全仓库 `grep + 全局替换` 旧绝对路径。
- 冻结 runner/result/map 不因“目录整齐”而改路径。
- 当前开发代码按模块逐个迁移到 `current_paths.env` / `current_paths.json`。
- 一个模块改完后必须做相应 regression，再改下一个。
- 只有当某旧路径的**真实文本引用和外部 symlink 引用都归零**后，才进入下一轮归档评估。

## 13. 磁盘清理建议（当前不执行）

- 当前隔离区约 315.76 MB，是未来最优先的删除审查对象。
- 由于本次整理坚持“0 删除”，**目录已经明显变干净，但磁盘容量不会按归档规模释放**。
- 如果以后需要腾空间，应单独建立删除审批：先验证 archive/tar/freeze 可恢复，再删除 quarantine 或已证明冗余的展开副本。
- 不建议当前直接删除旧 `MineSim-Dynamic`、受保护地图、DR tar 或任何冻结证据。

## 14. 最终结论

- `/root/autodl-tmp` 顶层由约 **530** 项降至 **121** 项，减少约 **77.2%**。
- 已记录 **423** 项安全移动/隔离操作，科研文件删除为 **0**。
- 当前正式仓库、Polygon21、cross-scene、MCTS results、FullMine runtime 与 Dapai native reference 均通过最终健康检查。
- 现阶段建议停止继续“为了整齐而移动”文件；后续工作应以科研任务为主，路径只在实际维护模块时逐步迁移。
