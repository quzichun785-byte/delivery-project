---
description: 母骨架将已明确的开发决策派为子骨架工程任务
argument-hint: <工程任务编号>
---

以母骨架身份执行工程派单，全程停留在母目录，使用绝对路径：

1. 先确认该事项确实需要代码实现；普通调研/决策应在母轻量卡完成，不得为了形式派成工程任务。
2. 读取 CLAUDE.md、docs/DISPATCH.md 和共享协议，确认一对一关系及当前版本。
3. 从子 `docs/TASKS/_TEMPLATE.md` 复制新工程卡，不得覆盖既有卡；只写 A 产品定义区和 D 变更区，不写 B/C 或工程验收。
4. A 区必须包含目标、范围、业务规则、不做项和可观察的产品验收场景；风险默认 HIGH，降级须在 D 区写理由和批准人。
5. 新工程卡置为 DISPATCHED，登记 DISPATCH 的绝对路径、版本和状态，并在 D 区追加 `母 | status: DRAFT -> DISPATCHED`；不自行开发。
6. 子退回 BLOCKED_PRODUCT 时，先读问题和证据，决策后修订 A、提升 task_version，并在 D 区追加 `母 | status: BLOCKED_PRODUCT -> DISPATCHED`。
7. 若轻量调研卡已完成，在其“后续动作”登记工程卡路径，避免两类任务失去关联。
