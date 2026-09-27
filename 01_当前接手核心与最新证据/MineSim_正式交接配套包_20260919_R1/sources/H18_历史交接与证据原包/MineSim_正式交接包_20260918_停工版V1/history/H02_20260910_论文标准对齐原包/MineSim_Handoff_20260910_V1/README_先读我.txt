MineSim-Dynamic 正式交接包｜论文标准对齐版 V1
证据截止：2026-09-10

先读什么
1. 正式Word：MineSim_Dynamic_正式交接_论文标准对齐版_V1_20260910.docx
   当前渲染为42页、17章、53组编号公式；含目录、公式/来源索引，末尾为15问快速接手区。
2. CURRENT_STATE.json：机器可读当前阶段、下一Gate、HOLD与授权边界。
3. NEXT_GATE_CONTRACT.json：下一步只读评价契约要求；不是已执行实验。

交接终点
旧Value V3/K13分支的工程结论不改，新诊断模型未替换旧模型；教师、覆盖、时域、完整策略回报及任务指标诊断已串联。当前按用户同意的论文参考，对齐安全—完成—通行效率—搜索代价评价。统计保证分支独立HOLD，ε未定不再阻塞一般开发对照。
下一最小Gate：PAPER_ALIGNED_EVALUATION_CONTRACT_PREFLIGHT。
本包不批准直接改奖励、换阈值、重采2356条、重训、上线或恢复剪枝。

其他文件
同名TXT/Markdown为主文内容镜像；TXT保留公式的文本/LaTeX表示，精细公式排版以Word为准。
formula_index.json：53组公式的LaTeX与所在章节；含义、来源及适用条件仍须读正文。
evidence_inventory.csv/json：34个源证据的文件名、当前本地副本、完整SHA、包内副本位置。未包含的大型原始ZIP从原会话附件或云端原目录定位，不重复塞入本包。
experiment_ledger.csv/json：25项关键实验/技术恢复记录；非全盘START清单，未列出的旧目录也不得自动重跑。
supporting_reports/：用户原始Skill及小型步骤报告，保留原文；其中历史“下一步”不覆盖本交接。
historical_sources/：历史Word和设计/过程记录，只用于溯源，禁止把旧Gate当当前Gate。
document_quality_check.json：本轮实际文档与源副本检查范围。
SHA256SUMS：本包文件完整性清单，不是AutoDL实时状态证明。

必须分清
本次仅创建交接文件，没有运行新MCTS/训练/状态推进，没有修改旧数据、Git、软链接或删除科研资产。
历史报告的核验数量和测试数为原步骤记录，本次未重新执行全部历史实验。
AutoDL live文件、软链接、进程、删除与当前Git均未实时查询；最近返回的Git快照含?? ^C，未变化不等于clean。
本Word/包尚未确认上传到AutoDL或Library。不要由sandbox副本推断云端存在。
所有已消费START命名空间保留，不原名重跑、不为取得PASS换seed或降低阈值。

论文边界
正文把论文原方法、论文实验配置/观察、项目实际实现、拟采用适配分开。PET/TTC的1.5秒是代理风险参考，0.8/0.6是特定复合风险阈值，均不是碰撞概率；映射未完成前不自动写入当前硬约束。
Neural A*的规划质量与扩展开销评价可借鉴，但不等于本项目已有最优Q或固定Top13安全证明。

代码交付约定
后续仅主程序以可下载脚本交付；启动、screen、监控与结果检查用聊天内可复制集成代码。每一步写明论文、公式、项目适配及自定阈值。
