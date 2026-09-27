# 20260927 MineSim Git 一次性增量更新

本更新将知识库从“G1 deadlock 尚未集成”的旧状态推进到当前真实状态：G1 已 PASS_FROZEN；G2 尚未开始 scientific Stage-A，当前唯一 Gate 是 G2 V2 LOW prepare。

内容包括：
1. 最新 authoritative CURRENT_PROJECT_STATUS md/json；
2. 真实 AutoDL source snapshot（deadlock runtime、V2R/exact geometry、ROOTS/full_eval、G1 final freeze、patched G2 V1）；
3. production-binding discovery 报告与关键真实 map-loader 源码；
4. 最终待执行的 G2_FORMAL_CALIBRATION_V2 源码与冻结输入；
5. 根目录 MINE_SIM_CURRENT_STATUS.md/json 入口，供以后 AI 优先读取。

注意：安装此 Git 更新不等于 G2 prepare PASS；prepare 仍需在 AutoDL 实际执行并回传证据。
