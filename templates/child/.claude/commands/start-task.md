---
description: 子骨架接受派单并完成技术评审与 READY
argument-hint: <任务编号>
---

以子骨架身份执行，停留在子目录：

1. 读取 CLAUDE.md、STATUS、当前任务卡、QUALITY、TESTING 和开发交接手册。
2. 状态必须为 DISPATCHED 或 READY；核对 task_version、产品范围和当前代码基线。
3. 发现产品矛盾、不可实现或范围变化时，只追加 D 区 `子 | status: 当前状态 -> BLOCKED_PRODUCT` 并设置 blocked_from，不改 A 区。
4. 可实施时只补 B 区：垂直切片、技术契约、质量矩阵、测试/集成和回滚计划；不适用项写理由。
5. 风险默认 HIGH；需要降级时在 D 区记录理由和批准人，不自行降低关键任务。
6. 验收定义完整后将状态置为 READY，并在 D 区追加 `子 | status: DISPATCHED -> READY`。此命令不写业务实现，继续开发使用 build-task。
