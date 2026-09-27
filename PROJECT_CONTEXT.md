# PROJECT_CONTEXT — MineSim-Dynamic

## 当前权威入口

当前优先参考 `00_最新交接与研究流程/MineSim_G1_交接文档_20260926.md`。更早交接用于 provenance / 历史证据，不应覆盖 2026-09-26 的最新状态。

## 当前主目标

用神经网络直接辅助 MCTS，在不降低任务质量与硬安全质量的前提下，减少在线搜索预算、CPU、iterations 或 expanded nodes，并把网络 forward 开销计入总成本。

## 当前阶段

- G0：baseline / provenance 已冻结。
- G1：仍为 HOLD，处于后半段；V2V/V2R exact-tick hard safety 和 deadlock definition 已获得多项 PASS，但 deadlock terminal integration 与 reward/value contract 尚未闭环。
- G2 Teacher Budget × Depth：HOLD / 未授权。
- G3–G9：尚未开始。

## 当前下一 Gate

`G1_DEADLOCK_TERMINAL_INTEGRATION_V1`

恢复执行前应先确认 live repo HEAD / status 与最新交接一致；不要把本地资料快照当作云端实时状态。

## 当前明确禁止提前做

- 不提前进入 G2 Teacher Budget×Depth。
- 不采新 Teacher。
- 不训练神经网络。
- 不做 hard pruning。
- 不跑最终 HOLDOUT。
- 已冻结且输入 SHA / HEAD 未变化的 Gate 不重复运行。

## 研究路线

G0 baseline freeze → G1 evaluation/safety/long-term value → G2 Teacher Budget×Depth → G3 high-quality Teacher → G4 label audit → G5 network → G6 lossless neural-guided MCTS → G7 confidence-gated pruning → G8 budget-quality curves → G9 independent HOLDOUT。

## 文件使用原则

1. 最新交接 > 更早交接。
2. live terminal / Git / SHA / frozen artifact > 本地文档摘要。
3. Frozen result 不因换会话自动重跑。
4. Technical FAIL 与 Scientific FAIL 分开记录。
5. 先保证质量与安全，再验证搜索效率；不能用失败、未完成或更冒险的轨迹换取“更快”。
