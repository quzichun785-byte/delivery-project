---
description: 母骨架启动或继续轻量调研与决策
argument-hint: <工作项或轻量任务编号（可选）>
---

以母骨架身份执行，不进入子目录、不写代码：

1. 读取 CLAUDE.md、STATUS、DECISIONS 和产品交接手册，先判断是小想法、正式调研决策，还是需要代码实现的工程任务。
2. 小想法直接记录 INBOX/DECISIONS，不强制建卡。
3. 需要正式调研时，从母 `docs/TASKS/_TEMPLATE.md` 创建轻量卡，仅写问题、一手证据、可选方案和后续动作，状态由 DRAFT 转为 RESEARCH。
4. 事实、假设、待确认分开；外部调研保留原始 URL/文件和访问日期，不编造现场事实。
5. 调研完成后使用 decide-task；只有需要代码实现时才使用 dispatch-task 派工程卡，不把普通调研拖入工程闸口。
