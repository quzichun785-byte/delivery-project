---
description: 子骨架建立或核验真实开发仓的工程基线
argument-hint: <开发仓绝对路径（可选）>
---

以子骨架身份执行特殊工程基线任务，不创建产品任务卡、不修改 A 区：

1. 阅读 `references/engineering-baseline.md`（若项目内无副本，使用技能绝对路径）、CLAUDE.md、TESTING、OPERATIONS、ASSETS 和开发交接手册。
2. 检查真实开发仓、锁文件、现有配置、测试和 CI；已有可用配置不得为套模板而替换。技术栈未知时先探测，不编造。
3. 逐项建立或核验：资产登记、依赖锁定、配置/密钥、启动停止、健康检查、数据库初始化/迁移/回滚、统一错误与日志、lint/typecheck、测试与数据种子、CI、模拟/真实适配契约、备份恢复和可观测性。
4. 原始输出放 `artifacts/`，在 TESTING/OPERATIONS 写实际命令和结果；未执行写 NOT_RUN，N/A 必须写理由。
5. 用另一个干净上下文或新窗口按手册复现安装、启动和测试，记录结果。
6. 基线未通过时将 STATUS 工程基线标为 BLOCKED，业务切片不得借“先开发再补”绕过；通过后记录证据和日期。
7. 更新 ASSETS、DECISIONS、STATUS 和开发交接手册。不自动提交、推送、合并或部署。
