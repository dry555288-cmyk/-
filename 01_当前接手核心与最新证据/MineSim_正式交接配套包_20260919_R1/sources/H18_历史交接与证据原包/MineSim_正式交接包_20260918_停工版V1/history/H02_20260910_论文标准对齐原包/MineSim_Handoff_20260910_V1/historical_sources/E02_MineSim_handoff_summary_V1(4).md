# MineSim 项目阶段性接手总结 V1

## 项目总体路线

MineSim复现 → 蒙特卡洛/MCTS接入 → 单车跑通 → 双车冲突场景构建 → FullMine新地图接入 → Fleet-MCTS双车联合规划与多种子验证 → 原生MineSim可视化与汇报材料 → 云端文件安全整理 → 后续神经网络接入。  
  
当前节点：C03 Full Collection 已冻结PASS，正在准备Value V2 inference chain。

## 已冻结成果

C03 one-step smoke：root=1，16 joint actions，MCTS expansion=64，search semantics unchanged。  
Freeze SHA：170dcb466191ccbc537bc58adb44fe032500b52c50aa2736dd822fb50b3201c3。  
  
C03 Full Collection：135 roots，2160 derived actions，8640 shadow expansion，benchmark_success=True，collision_or_overlap=False。  
Freeze SHA：15c098f72ae0187dd0bb97bd9878aa6860d47df48391e09bd9ad56eb9ac31fa8。

## 当前环境与目录

正式仓库：/root/MineSim-Dynamic  
实验数据：/root/autodl-tmp  
Git HEAD：112d2bd0f3412fc83b13d5587d2b41402d2d0f5e  
  
原则：正式仓库仅保留必要源码，实验结果放autodl-tmp。

## Value V2状态

已完成model freeze、normalization、metric closure和feature mapping静态检查。  
  
模型：ROOT_CENTERED_Q，12-\>64-\>64-\>16。  
12维feature：A_speed_mps、B_speed_mps、A_accel_mps2、B_accel_mps2、A_remaining_to_conflict_m、B_remaining_to_conflict_m、delta_v_abs_mps、delta_heading_abs_rad、delta_heading_over_pi、I_Omega_app_AND、I_Omega_int_AND、alpha3。  
  
当前HOLD：未执行C03 Value forward，未计算C03 prediction和metrics。

## 关键问题记录

C13 stale guard：通过fresh recovery protocol解决。  
Python import路径问题：通过模块复制和import gate解决。  
Preauth冲突：关闭旧协议，建立新协议。  
One-step RC=1：确认不是技术失败，而是短时smoke无法完成post-conflict。  
Value model边界：通过源码审计和授权边界证明未执行。

## 协作规则

采用：只读preflight → smoke → 短闭环 → 完整实验。  
  
ChatGPT负责分析、决策和关键代码；用户负责云端执行；复杂算法和顽固Bug才使用Codex。  
代码执行必须进入/root/MineSim-Dynamic，激活minesim环境，设置PYTHONPATH。

## 云端文件整理

已确认关键结果位于/root/autodl-tmp，Git保持clean，冻结文件和SHA链保存。  
  
未确认：全部历史目录删除情况、最终磁盘清理情况。因此文件清理状态标记HOLD。

## 快速接手区

无需重做：MineSim复现、MCTS接入、双车冲突验证、C03 Full Collection。  
  
禁止修改：冻结JSON、SHA绑定文件、runtime结果。  
  
下一步：锁定feature builder → normalization → checkpoint load → model forward → prediction → metric完整链路。  
  
当前无需高资源卡；真实forward/evaluation前再开高资源。
