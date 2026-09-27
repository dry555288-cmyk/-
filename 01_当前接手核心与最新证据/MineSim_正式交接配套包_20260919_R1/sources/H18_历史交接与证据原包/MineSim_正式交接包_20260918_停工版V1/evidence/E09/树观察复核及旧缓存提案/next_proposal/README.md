# 双车确定性动作可行性报告缓存：单次技术对照

资源 LOW，单进程CPU；不需要GPU。复用刚刚完成的treeprobe结果，不重采512条数据。

## 为什么不直接搬旧树的Q
当前证据仅支持选定子节点状态匹配；旧剩余7步和新8步的估值口径不同，旧Q还包含进入节点的奖励。本版本不复用Q/visit，不预填节点，不剪枝。

本次只缓存 `DestinationStopTransition.action_report` 的确定性输出。调用时仍验证完整车辆状态，键包含完整状态、所有TransitionConfig字段、目标窗口、动作映射和版本。匹配失败执行原函数；配置变化清空缓存；返回深拷贝；每车最多4096条，不写入生产仓库。

## 固定范围
- 2个已有fixture，沿用原rng_before与seed，每个2步。
- 每个fixture分别运行原版和缓存版，合计最多8次MCTS、8次外层模型一步推进；两fixture对照顺序交错。
- B64/H8、0.5秒步长、0.1秒碰撞采样、奖励、动作域规则、随机流不变。
- 计数和计时覆盖全部缓存开销。不启用cProfile。
- 这是完整搜索等价小试，不是大型benchmark；即使本次耗时下降也不能直接宣称通用实时提速。
- PASS要求行为一致、记录完整、原件未变。命中率/CPU和wall耗时单独报告，不能为提速改判失败样本。

## 执行
仅上传 `run_dual_reportcache.sh` 到 `/root/autodl-tmp`，运行：

```bash
bash /root/autodl-tmp/run_dual_reportcache.sh --authorize-reportcache-once
```

该命令授权新目录中的一次技术测试；不授权部署、采集、训练、删除或自动重试。读取已完成 `minesim_dual_treeprobe_v1` 目录或同名ZIP，不扫描全部数据盘。输出为 `minesim_dual_reportcache_v1.zip`，回传这一包即可。

HOLD时保留结果、lease、日志和pending。有BUNDLE传对应ZIP，否则传LAUNCHER_LOG；不删除，不自动重跑。以前的treeprobe命令不再执行。

## 本地测试范围
UNIT_TEST_RESULT.json：28项缓存/来源/生命周期单元检查。
GATE_FLOW_TEST_RESULT.json：4项合成生命周期流程（计数为模拟，实际MCTS=0）。
SAVED_STATE_REPORT_TEST.json：260份已保存树节点中的520个车辆状态，原版与缓存版动作报告复算一致；不是520个独立状态/场景，不运行MCTS，不生成教师标签。

尚未在真实状态上执行新版本完整MCTS A/B，也未在AutoDL执行；完整搜索等价性由此次单独授权的云端技术小试确认。
