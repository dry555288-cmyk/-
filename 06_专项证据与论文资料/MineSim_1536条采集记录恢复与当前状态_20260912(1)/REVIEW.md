# MineSim近期采集记录恢复与当前接续状态

证据范围：用户上传的 `ff729b4a-d20f-4dad-877d-fbaffe10e3bc.zip`，以及本对话中此前已恢复的候选模型、smoke和policy4原始HOLD记录。仅检查本地上传副本，没有连接AutoDL，没有运行实验或修改源文件。

## 本轮结论

**PASS：104份定向源文件已完整导出，三阶段采集记录的身份、数量与来源得到核对。旧模型的768条discovery + 768条confirmation采集台账已接上。不需要重采这1536条。**

这不是“1536条原始轨迹全量恢复”，也不是标签、安全或新停车模型的认证。两个大型批次目录的逐cell轨迹没有随本次选择性导出全部带回。

## 一、实际验证范围

- ZIP CRC通过；EXPORT_MANIFEST的112个成员大小和SHA全部匹配（113个ZIP成员中清单自身不计入）。
- 104份源副本均完整、读取期间及捕获结束时稳定，并与前次inventory一致。
- 72项本地记录一致性检查全部通过；详见 `LOCAL_RECORD_REVIEW.json` 与 `review_saved_records.py`。检查没有执行输入脚本或搜索算法。
- 原批次清单的已捕获子集：remaining390为28/2834项；cell377为19/136项；confirmation768为48/5519项，均匹配。未捕获项不声称重新校验。
- 390/768条批次的worker进度、任务ID、ordinal、outcome和声明COMMIT SHA与各自audit及原manifest一致。除cell377外，大部分COMMIT是清单元数据对照，不是本地重新读取全部原始COMMIT及逐步轨迹。

## 二、丢失期间的三个阶段

时间均为原始文件记录的UTC。

| 阶段 | 完成时间 | 实际状态 | 数量与边界 |
|---|---|---|---|
| 剩余390条discovery并行采集 | 2026-09-11 11:48:31 | COMPLETE_REMAINING390_COLLECTION_NOT_LABEL_CERTIFICATION，RC0 | 390/390；四worker为97/97/98/98；无未启动、无已触及未验证；当时仍保留cell377未完状态 |
| cell377尾段续接 | 2026-09-11 13:10:17 | COMPLETE_CELL377_CONTINUATION_PENDING_EXTERNAL_REVIEW，RC0 | 原20步保留；新增33步；共53步、52次搜索；不是重跑已完成样本 |
| confirmation768并行采集 | 2026-09-11 15:32:16 | COMPLETE_CONFIRMATION768_COLLECTION_PENDING_REVIEW，RC0 | 768/768；四worker各192；seed52000–52003；discovery未重采 |

来源分别为：
- `evidence/sources/data/minesim_discovery_remaining390_parallel_v1/{RESULT,CAPTURE,COLLECTION_AUDIT}.json`
- `evidence/sources/data/minesim_discovery_cell377_tail_continuation_v1/{RESULT,JOIN_VALIDATION}.json`
- `evidence/sources/data/minesim_confirmation768_parallel_v1/{RESULT,CAPTURE,COLLECTION_AUDIT}.json`

后一个批次保存的原discovery台账由377条原运行保留、390条补采、1条续接组成。三部分无重复、合计768。补采390条与台账的COMMIT SHA逐项一致；cell377台账SHA与本次实际COMMIT文件一致。

### cell377续接核对

108个事件的序号与前项SHA链连续；53个STEP_RETURNED和trace逐步一致；相邻状态连续；第一步强制动作、随后52次搜索。旧20步与新33步的折扣回报之和和记录值一致，浮点差异小于1e-10。

完整记录回报61.73287376681323；前缀19.779739041616107；尾段局部回报51.293286310106446；gamma0.99。旧恢复过程中的四次技术重放不被当成新增样本。由于中断分段，该样本的连续整段墙钟时间仍为HOLD，不能用于伪造完整执行耗时。

## 三、恢复的旧模型结果分布

| 批次 | 配置路线终点BOTH_CONFIGURED_ROUTE_ENDS | EXECUTED_HARD_SAFETY_TERMINAL | EVALUATION_CAP_NOT_TASK_TERMINAL | 合计 |
|---|---:|---:|---:|---:|
| Discovery | 420 | 201 | 147 | 768 |
| Confirmation | 425 | 193 | 150 | 768 |
| 合计 | 845 | 394 | 297 | 1536 |

Discovery来自保存的768条台账/observations；confirmation从768条audit与worker进度重新统计。每条由冻结root、强制首动作和固定seed定义，不是1536个独立的从头自主驾驶测试，因此不把845/1536称为新模型自主成功率。硬安全终止不等同于394次碰撞。达到评价上限不自动等于已证实永久死锁。

| 场景与批次 | 路线终点 | 硬安全终止 | 评价上限 |
|---|---:|---:|---:|
| C04 discovery | 253 | 3 | 0 |
| C04 confirmation | 252 | 4 | 0 |
| C06 discovery | 128 | 125 | 3 |
| C06 confirmation | 128 | 124 | 4 |
| C11 discovery | 39 | 73 | 144 |
| C11 confirmation | 45 | 65 | 146 |

以上分布只能解释此固定旧模型采样设计；不能推导其他模型、未见场景或真实车辆安全。

## 四、273候选关系不是111最终关系的原始证据

确认批次在启动前绑定的discovery候选文件共有273条候选关系：C04为141，C06为119，C11为13；总1440对中，718对为UNKNOWN_OVERLAPPING_RETURNS，449对为UNKNOWN_TAIL_CENSORED。所有training_mask仍为0。候选冻结时间2026-09-11 13:34:39 UTC，早于confirmation启动15:05:15 UTC；对应SHA已交叉核对。

`confirmed_labels_computed=false`是确认采集脚本结束时的状态，不证明后来没有分析。已有较晚候选回归记录明确引用 `old_111_relations_not_relabelled=true`，但本次没有恢复111条最终关系的原始表，也没有重新计算或认证它们。既不能把273叫作273条最终标签，也不能把历史“待复核”重新设为项目当前阻塞。

## 五、旧终点定义与新停车模型必须分开

cell377原trace最后A车 `goal_reached=true`，但速度为15m/s；B车0m/s。可见旧模型BOTH_CONFIGURED_ROUTE_ENDS并不要求两车均停稳。这是旧任务定义的边界，不把它改写成新模型失败。

后续新契约 `DUAL_ONLY_DESTINATION_STOP_CANDIDATE_V1` 要求各自后轴在终点前0.5米窗口内且速度严格为0，保留已停车辆的车体参与碰撞检查；契约明确 `old_teacher_labels_compatible_with_new_version=false`。因此这1536条旧结果和后续停车候选版本分开保存。

来源：`CELL377_FINAL_STATE_EXCERPT.json`、原cell377 trace，以及 `later_stage_reference/dual_stop_contract.json`。

## 六、当前接续位置

当前最新直接证据仍是：新停车候选合成回归通过 → 真实路线技术smoke通过（2026-09-12 08:22 UTC）→ 原policy4尝试在启动前HOLD（2026-09-12 09:13 UTC）。

原policy4 `START_WRITTEN=false`、RC2，错误 `CPU_QUOTA_LOW_OR_UNKNOWN`；当时有效CPU0.5核，内存余量1727209472字节。原协议要求至少2有效核、2GiB可用内存。尚未进入四策略科学执行。这不构成四条策略失败，也不能排除未找回的其他后续尝试。

已检索范围内没有后续policy4结果，但搜索有边界，不声称全局没有其他尝试。此次恢复收束，不再因确认批次的历史pending字段倒退，也不再无目的全盘搜索。

下一最小行动建议：准备policy4启动前技术恢复契约，保留原四任务、seed、payload和旧namespace；先完成LOW级源码/输入绑定和重复执行防护，再在明确授权且资源充足时启动新namespace。当前不批准重跑、不自动启用seed或运行原--launch。

当前阅读与准备资源LOW；实际原policy4运行须满足至少2有效CPU核、2GiB可用内存，GPU禁用。是否需开高资源实例以执行当时cgroup为准，不把上一轮0.5核误当成永久机器配置。

## 七、保存边界

本目录是证据副本和接手状态，不是全量原始数据备份，不代替云端三个原始ZIP。三个原ZIP仅在导出时通过metadata确认存在，本次没有校验它们的完整字节。云端pre/post Git记录相同，HEAD为112d2bd0f3412fc83b13d5587d2b41402d2d0f5e，status为`?? ^C`；只说“前后未变”，不说“工作树clean”。没有检查当前实时Git/进程/资源。

原结果、失败、评价上限均保留。未进行采集、模型forward、训练、标签重算、生产补丁或文件删除。
