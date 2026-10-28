---
description: 子骨架执行独立审查、修复与复测
argument-hint: <任务编号>
---

以子骨架身份组织独立审查：

1. 仅在 REVIEW 状态执行。HIGH/CRITICAL 必须将任务卡、实际 diff 和原始测试证据交给干净上下文的独立 Agent；LOW/MEDIUM 按任务卡说明轻量审查。
2. 独立审查只查不改，重点检查需求漂移、边界、权限、并发幂等、错误吞噬、弱断言、部署回滚和范围外修改。
3. 主执行者逐项复核，合理项修复后重新运行相关测试与集成场景；审查者无发现也允许，不凑数。
4. 未解决问题不得隐藏；必要时在 D 区追加 REVIEW -> BUILD/BLOCKED，CRITICAL 尚需 E3 人工专业评审时保持未满足。
5. 所有进入 ACCEPT 的条件满足后，将状态置为 ACCEPT，在 D 区追加 `子 | status: REVIEW -> ACCEPT`，产品/工程验收保持 PENDING。
