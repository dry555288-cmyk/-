# MineSim-Dynamic 正式接手入口

**当前停工，只交接。不要运行包内脚本。**

先读 `CURRENT_STATE.json` 和主Word第1、18、24章，随后按需看 `HANDOFF.md`。

## 三条硬事实
1. 32个状态、512条回报已封存。当前不重新采集，不重做已完成预测模型。
2. 最新H8子树小试8次搜索/2次晋升已返回，H8统计语义通过；未建立稳定提速或完整任务收益。
3. `policy4` 原方案和启动器已交付，**尚未收到结果**；不要推断用户机器上一定没有启动。恢复会话先确认有无结果，有则只复核。

## 哪个文件用来接续
- `NEXT_GATE_CONTRACT.json`：原4条策略续行方案与当前禁止自动执行的边界。
- `pending_policy4/`：原源码、固定协议、启动器，原字节不变；63份输入在E13原ZIP中匹配。
- `evidence/E13/`：最新原始运行ZIP及此前独立算术复核。
- `frozen_data/DATASET32.json`：聚合数据精确副本。
- `EXPERIMENT_LEDGER.json`：分母、结果与禁重跑台账。
- `workflow/USER_SKILL_ORIGINAL.md`：本次最新原Skill，42节完整。

## 保存边界
本包只是对话容器中的证据副本，没有上传AutoDL/Library/Drive，也没有Git提交/tag。旧数据盘状态、正在运行的任务与当前计费均未查询。完整采集分卷、全部地图视频和历史逐步记录不重复包含。

不要自动执行旧包内任何 `NEXT_PROPOSAL` 或 `CURRENT_STATE`。它们是当时快照，本包根状态是文档性最新入口，但未来真实结果优先。

## 核验
`PACKAGE_MANIFEST.json`列出本包文件大小/SHA（清单和SHA256SUMS本身除外）；`SHA256SUMS`亦覆盖PACKAGE_MANIFEST。`HANDOFF_LOCAL_VERIFICATION.json`记录本次只读核验：98项当前清单、62份当前父来源、63份待执行输入及发布身份，没有新科学执行。
