---
protocol_version: "1.0"
---

# 母子协作协议（项目内副本）

## 主目标
企业级可交付代码是主角；母子结构只用于避免轻量调研决策被重型工程流程拖慢。公开发布、目录形式或母子本身都不是目的。

## 身份与路径
1. 一对一；根目录无 CLAUDE.md 和根级 .claude/。进入母目录是轻量调研决策角色，进入子目录是工程角色。
2. 跨目录只用绝对路径，禁止为读写而 cd 到对方目录。
3. 小决策可直接写 INBOX/DECISIONS，不必事事建卡。

## 两类任务卡
1. 母 `docs/TASKS/` 存轻量调研/决策卡：`DRAFT → RESEARCH → DECIDED → DONE`。只要求一手证据、方案取舍、决策理由和后续动作，不要求测试、集成、独立代码审查、回滚或 C3～C7。
2. 子 `docs/TASKS/` 存工程共用卡：`DRAFT → DISPATCHED → READY → BUILD → VERIFY → REVIEW → ACCEPT → DONE`。只有需要代码实现的决策才进入此流程。
3. 母 `docs/DISPATCH.md` 只登记工程卡指针和状态，不复制正文。

## 工程卡权限
- 母写 A 产品定义区、D 变更区及 E 产品验收；子写 B 工程区、C 证据区、D 变更区及 E 工程验收。D 只能追加。
- 子发现产品矛盾、不可实现或范围变化时置 BLOCKED_PRODUCT，不改 A 区；母修订并提升 task_version 后重新 DISPATCHED。
- 每次状态变化在 D 区追加 `日期 | 角色 | status: 源 -> 目标 | task_version=版本`，当前状态必须与最后转移一致。
- 最终 DONE 必须由母或母子共同确认；子只能签 E2，不能单独改 DONE。

## 工程证据
1. 首个业务切片前执行 bootstrap-engineering，基线未通过则业务切片 BLOCKED。
2. VERIFY 同时包含功能测试和集成验证；未执行写 NOT_RUN，不得写 PASS。
3. 风险默认 HIGH；HIGH/CRITICAL 独立审查，关键生产事项另需人工专业评审。
4. target_maturity：DEMO 要 C3/C4，PILOT 另要 C6 异常/权限/回滚或合理 N/A，PRODUCTION 另要 C7 生产就绪证据。
5. DONE 时 E1/E2 结论、证据路径、验收人/日期和遗留问题必须完整且与 frontmatter 一致，不接受空双签。
6. 开发仓、模拟器、部署、旧代码、交付物及证据目录登记 docs/ASSETS.md；生产运维状态记录 docs/OPERATIONS.md。

## 外部动作
不自动提交、推送、合并、部署或正式发布；这些动作需用户另行明确授权。
