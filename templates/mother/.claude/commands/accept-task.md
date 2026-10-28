---
description: 母骨架执行工程任务的产品验收并完成双签
argument-hint: <工程任务编号>
---

以母骨架身份执行**工程任务**产品验收，不修改任何工程证据，也不把此流程用于普通调研卡：

1. 读取子工程卡 A 区、E 区和实际交付结果，确认 task_version 与派单版本一致。
2. 子工程验收必须为 APPROVED；否则保持 ACCEPT 或退回，不签产品通过。
3. 按 A 区逐项验证业务目标、范围、不做项和产品验收场景；必要时由实际业务角色参与。
4. 通过则在 E1 写 APPROVED、验收证据路径、验收人/日期和遗留问题；不通过写 CHANGES_REQUIRED 并追加 D 区原因，禁止改子测试结论。
5. 只有 E1、E2 均为 APPROVED 才将工程任务置为 DONE，并在 D 区追加 `母（或母子） | status: ACCEPT -> DONE`；同步 DISPATCH/STATUS。双签不等于生产发布。
