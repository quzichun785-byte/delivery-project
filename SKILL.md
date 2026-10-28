---
name: delivery-project
description: 以企业级可交付代码为首要目标，通过工程基线、垂直切片、可复现测试、独立审查、生产运维和母子双签防止一次性演示开发。母子结构仅用于隔离轻量调研决策与重型工程交付：母骨架让调研决策不被工程闸口拖重，子骨架严格执行代码质量流程。触发词：母子骨架、企业级交付骨架、工程交付骨架、可交付项目骨架、创建 delivery 项目。
argument-hint: <项目名（可后补）>
---

# delivery-project — 以企业级代码交付为目标的母子工程骨架

创建一套**工程质量为主、轻量决策为辅**的工作流。母子结构只是分工手段：母骨架让调研、分析和决策保持轻量，子骨架用垂直切片、真实测试、独立审查和可复现证据完成企业级代码交付。

## 一、首要决策基线

开工、生成模板、修改流程或公开分发前，必须先读 `references/delivery-charter.md`。该主纲是唯一工程决策基线，任何母子协作调整都不得削弱它。

核心关系：

1. **主角**：企业级可交付代码及其工程证据。
2. **子骨架**：承载工程基线、垂直切片、逐片集成、风险审查、成熟度、生产运维和工程验收。
3. **母骨架**：只承担轻量调研决策、工程派单和产品结果确认，防止所有任务都被迫走代码流程。
4. **公开分发、目录美观和母子形式都不是目的，技能好用并能提升交付质量才是目的。**

## 二、不可变的协作规则

1. 一对一：一个母工作区只对应一个子工作区。
2. 双目录、双身份：根目录不得放 `CLAUDE.md` 或根级 `.claude/`；进入母目录是调研决策角色，进入子目录是工程角色。
3. 跨目录只用绝对路径，禁止通过 `cd` 获得对方身份。
4. **两类任务卡分离**：母骨架的轻量调研/决策卡存母目录；工程卡存子目录，禁止用工程证据要求拖重普通调研。
5. 小决策可直接写 INBOX/DECISIONS，不必事事建卡；只有需要代码实现的决策才向子骨架派工程卡。
6. 工程卡分区授权：母写产品区，子写工程与证据区，变更只追加，验收分别签。
7. 产品问题退回 `BLOCKED_PRODUCT` 并提升 `task_version`，子不得自行缩小需求。
8. 母子双签只用于工程交付，产品验收与工程验收均为 APPROVED 才能 DONE；双签不等于生产发布。
9. 测试与集成必须真实执行并可复现；机械校验只检查结构、状态和证据，不声称能判断代码质量。
10. 不自动提交、推送、合并、部署或正式发布，除非用户另行明确授权。

## 三、生成后的目录形态

```text
{{项目根}}\
  PROJECT.md                 ← 中性登记，不是宪法
  母\
    CLAUDE.md                ← 轻量调研决策角色
    .claude\commands\
    docs\TASKS\              ← 轻量调研/决策卡
  子\
    CLAUDE.md                ← 工程开发角色
    .claude\commands\
    docs\TASKS\              ← 工程共用任务卡唯一位置
```

默认目录名为 `母`、`子`，可改为 `product`、`engineering`。根目录默认不初始化 Git；母子分别初始化由用户决定，初始化也不自动提交。

## 四、初始化步骤

### 0. 收集信息

必须拿到：项目名、一句话简介、项目根路径、产品背景与当前策略、母子目录名、是否分别初始化 Git、是否立即创建任务卡。

可选：技术栈、现有开发仓、既有测试/CI、数据红线、目标成熟度。未知写“待定”，不得编造。

### 1. 预检

- 项目根已存在时先列内容，禁止未检查就覆盖。
- 根目录已有 `CLAUDE.md` 或 `.claude/` 时，先提示身份污染，经用户决定后再生成。
- 母子任一目标目录已有同名文件时不覆盖，先报告冲突。
- 不修改 `long-project` 或其他技能，不迁移既有项目。

### 2. 生成并登记

- 根：`templates/root/PROJECT.md`。
- 母：`templates/mother/` 全部文件，并将 `templates/shared/LIGHT-task-card.md` 复制为母 `docs/TASKS/_TEMPLATE.md`。
- 子：`templates/child/` 全部文件，并将 `templates/shared/TASK-card.md` 复制为子 `docs/TASKS/_TEMPLATE.md`。
- 将 `templates/shared/PROTOCOL.md` 分别复制为母子双方的 `docs/PROTOCOL.md`，版本一致。
- 在根 `PROJECT.md` 和母 `docs/DISPATCH.md` 登记子工程卡目录绝对路径。

### 3. 初始化后验证

- 根目录无 `CLAUDE.md` 和根级 `.claude/`。
- 母子协议版本一致，轻量卡与工程卡目录分离。
- 用脚本真实绝对路径执行：`python -I <本技能目录>/scripts/check_delivery.py --pair <项目根>`。
- 轻量卡用 `--task`，工程卡也用 `--task`，脚本按所在目录和内容自动分流；可分别用 `--mother`、`--child` 批量检查。
- 列出实际创建文件、未初始化项和下一步用法；未执行验证不得写成通过。

## 五、两条任务流

### A. 母骨架轻量调研/决策流

```text
DRAFT → RESEARCH → DECIDED → DONE
```

- 只记录问题、一手证据、选项、决策及理由、后续动作。
- 不要求功能测试、集成、独立代码审查、回滚或 C3～C7 工程证据。
- 小事项直接写 INBOX/DECISIONS，不强制建卡。

### B. 子骨架工程交付流

```text
DRAFT → DISPATCHED → READY → BUILD → VERIFY → REVIEW → ACCEPT → DONE
```

- 业务切片前先执行 `/bootstrap-engineering`，基线未通过则 BLOCKED。
- 每片完成即集成；VERIFY 同时包含功能测试和集成验证。
- 风险默认 HIGH；HIGH/CRITICAL 独立审查，CRITICAL 另需人工专业评审。
- `target_maturity` 决定证据：DEMO 要 C3/C4，PILOT 另要 C6，PRODUCTION 另要 C7。
- D 区记录可机读状态历史；DONE 校验双签、人员、日期和证据，子不得单独 DONE。

详细协议见 `references/parent-child-protocol.md`、`references/task-card-standard.md`、`references/vertical-slices.md`、`references/quality-gates.md`、`references/review-protocol.md`、`references/engineering-baseline.md`。

## 六、首版范围与维护

包含：母子模板、轻量调研卡与工程卡、角色命令、基础机械校验和单元测试。暂不包含技术栈模板、自动合并/部署或复杂语义质量评分。

维护本技能时运行：

```bash
python -I -m unittest discover -s tests -v
```

技能本身按垂直切片演进：先验证轻量决策与工程派单，再验证普通和高风险工程切片，不把试验结果夸大为自动生产就绪。
