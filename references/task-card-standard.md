# 工程自足任务卡标准

> 本标准只适用于子骨架的工程任务卡，不得套用到母骨架的轻量调研/决策卡。轻量任务见 `light-task-standard.md`。

## 1. 必备元数据

`task_id`、`protocol_version`、`task_version`、`status`、`risk_level`、`target_maturity`、`product_signoff`、`engineering_signoff`、`human_review`、`blocked_from`。

`target_maturity` 只能是 `DEMO`、`PILOT`、`PRODUCTION`。它决定完成证据等级：DEMO 需要正常路径与集成，PILOT 另需异常/权限/回滚，PRODUCTION 另需 C7 生产就绪证据。

风险默认 `HIGH`。降级必须在 D 区写明理由和批准人；执行 Agent 不得自行把计费、权限、设备控制、迁移或生产发布降级。

## 2. 必备分区

- A 产品定义区：背景、目标、范围、业务规则、不做项、产品验收场景。
- B 工程设计区：垂直切片、技术契约、质量矩阵、测试计划、集成与回滚。
- C 执行证据区：实现摘要、diff/提交指针、实际测试、集成、审查、回滚证据路径。
- D 变更记录区：只追加，记录版本变化和阻塞处理；每次状态变化必须写 `日期 | 角色 | status: 源 -> 目标 | task_version=版本`，不得只改 frontmatter。
- E 双签验收区：产品、工程分别记录结论、证据路径、验收人/日期和遗留问题；关键人工评审另记。DONE 时元数据与分区结论必须一致，证据文件必须存在。

## 3. 验收矩阵

每项标“适用/不适用”，不适用写理由：空值与非法输入、重复与幂等、并发与事务、超时与重试、设备离线、权限越权、操作审计、数据精度、迁移与回滚。禁止无声删除质量项。

## 4. 写作纪律

- 母只写 A、D 和产品验收；子只写 B、C、D 和工程验收。
- 不用“已完成、基本可用、生产级”等无证据描述。
- 未运行的检查写 `NOT_RUN`，不得写 `PASS`。
- 测试证据写实际路径，不写不存在的链接。
- 新窗口只读任务卡、STATUS、手册和代码即可继续，不能依赖聊天记忆。

模板见 `templates/shared/TASK-card.md`；结构校验见 `scripts/check_delivery.py`。
