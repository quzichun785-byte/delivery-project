# delivery-project

**A mother–child workflow for enterprise-grade code delivery, not a one-shot code generator.**

一套以**企业级可交付代码**为目标的 Agent 工作流骨架：用工程基线、垂直切片、可复现测试、独立审查、生产运维和双签验收，防止“看起来能跑、实际上不能交付”。

母子结构只是实现手段：**子骨架负责工程交付，母骨架让调研和决策不被工程闸口拖重。**

## 为什么需要它

Agent 一回合生成整个系统时，常见的问题不是完全不能运行，而是：

- 只覆盖正常路径，忽略异常、权限、并发和幂等；
- 没有真实测试，只有“已经测过”的文字总结；
- 各模块分别看起来合理，集成后才发现契约不一致；
- 没有迁移、回滚、备份恢复和运维交接；
- 用一张截图或一次点击就宣称“生产就绪”。

`delivery-project` 把“完成”改成一条可验证的流程，而不是一句 Agent 自我评价。

## 核心设计

### 主角：企业级工程交付

- 真实开发仓工程基线；
- 垂直切片，每片完成即集成；
- 功能测试与集成验证；
- 可复现环境、依赖、数据种子和原始日志；
- 默认 HIGH 的风险分级与独立 Agent 审查；
- DEMO / PILOT / PRODUCTION 成熟度证据；
- 状态转移、执行角色和母子双签机械校验；
- 生产运维与仓外资产登记。

### 配角：轻量调研与决策

- 小想法直接记录，不必事事建卡；
- 正式调研使用轻量卡：`DRAFT → RESEARCH → DECIDED → DONE`；
- 只有需要写代码的决策才进入工程流程；
- 普通调研不需要测试、回滚或工程双签。

## 目录与身份

```text
项目根/
  PROJECT.md          # 中性登记，不是宪法
  母/
    CLAUDE.md         # 轻量调研与决策身份
    docs/TASKS/       # 轻量调研卡
  子/
    CLAUDE.md         # 工程开发身份
    docs/TASKS/       # 工程共用任务卡
```

- 根目录刻意没有 `CLAUDE.md`，避免角色污染；
- 母子分别在自己的目录启动 Agent；
- 跨目录只用绝对路径，不能通过 `cd` 获得对方身份；
- 工程卡采用 A–E 分区授权，母写产品定义，子写工程和证据；
- 产品验收与工程验收均为 `APPROVED` 才能 `DONE`，子不能单独完成。

## 两条任务流

### 轻量调研与决策

```text
DRAFT → RESEARCH → DECIDED → DONE
```

只要求问题、一手证据、方案取舍、决策理由和后续动作。

### 工程交付

```text
DRAFT → DISPATCHED → READY → BUILD → VERIFY → REVIEW → ACCEPT → DONE
```

首个业务切片前还需执行 `/bootstrap-engineering`，建立真实开发仓的工程基线。

## 快速开始

### 1. 安装技能

将仓库放入 Claude Code 的技能目录：

```bash
git clone https://github.com/quzichun785-byte/delivery-project.git
```

然后放入：

- Windows：`%USERPROFILE%\.claude\skills\delivery-project`
- Linux/macOS：`~/.claude/skills/delivery-project`

也可以放在项目的 `.claude/skills/delivery-project` 目录中。

### 2. 创建母子工作区

在 Claude Code 中调用：

```text
/delivery-project
```

按提示提供项目名、项目根路径、母子目录名和 Git 策略。未知技术栈写“待定”，不要编造。

### 3. 日常任务顺序

母窗口：

```text
/start-product
/decide-task 01
/dispatch-task 01
```

子窗口：

```text
/bootstrap-engineering   # 首次
/start-task 01
/build-task 01
/verify-task 01
/review-task 01
/accept-task 01          # 只签工程，保持 ACCEPT
```

最后回母窗口：

```text
/accept-task 01          # 产品验收，双签后 DONE
```

完整说明见 [USAGE.md](USAGE.md)，轻量示例见 [examples/README.md](examples/README.md)。

## 机械校验

```bash
# 校验母子目录、协议和两类任务卡
python -I scripts/check_delivery.py --pair /path/to/project

# 自动识别一张轻量卡或工程卡
python -I scripts/check_delivery.py --task /path/to/task.md

# 分别批量校验
python -I scripts/check_delivery.py --mother /path/to/project/母
python -I scripts/check_delivery.py --child /path/to/project/子
```

校验覆盖：

- 根目录身份污染；
- 轻量决策结论与证据；
- 工程状态转移、角色与版本；
- 测试、集成、独立审查和回滚证据；
- 成熟度对应证据；
- 双签人员、日期、结论和证据文件。

**它只检查结构与证据，不证明代码架构合理、测试一定有效或验收人一定有权限。**

## 风险与成熟度

| 维度 | 取值 | 作用 |
|---|---|---|
| 风险 | LOW / MEDIUM / HIGH / CRITICAL | 决定独立审查和人工专业评审强度 |
| 成熟度 | DEMO / PILOT / PRODUCTION | 决定需要多少测试、回滚和生产运维证据 |

风险默认 `HIGH`，降级必须在任务卡 D 区写明理由和批准人。

## 仓库结构

```text
SKILL.md                  # 技能入口与生成规则
USAGE.md                  # 中文使用手册
references/               # 工程主纲和协作/质量标准
templates/                # 母子模板、轻量卡与工程卡
scripts/check_delivery.py # 基础机械校验
tests/                    # 校验脚本单元测试
examples/                 # 轻量决策与工程派单示例
.github/workflows/        # 本仓库自身的测试
```

## 运行测试

仅依赖 Python 标准库：

```bash
python -I -m unittest discover -s tests -v
```

当前基线：**27 个测试**，覆盖轻量调研卡、工程卡、状态转移、角色权限、成熟度、双签和证据路径。

## 边界与非目标

- 不自动生成“生产级”业务系统；
- 不自动提交、推送、合并、部署或发布；
- 不预置具体语言、框架或 CI 模板；
- 不承诺 Agent 无需人工判断即可替代专业评审；
- 不用文档完整度代替真实工程质量；
- 公开分发和星标数量不是设计目标，工作流是否真的好用才重要。

## License

[MIT](LICENSE)
