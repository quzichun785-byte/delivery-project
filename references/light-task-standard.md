# 轻量调研/决策卡标准

## 1. 什么时候使用

- 需要调研背景、比较方案、确认业务规则或形成开发决策时使用。
- 小决策直接写 INBOX 或 DECISIONS，不必建卡；只有需要代码实现时才向子骨架派工程卡。

## 2. 主流程

```text
DRAFT → RESEARCH → DECIDED → DONE
```

BLOCKED 只表示证据或责任人未就绪，解除后恢复 blocked_from。

## 3. 与工程卡的区别

轻量卡不写功能测试、集成、独立代码审查、回滚、target_maturity 或 C3～C7 工程证据，也不需要母子双签。DONE 只要求：问题清楚、证据可查、选项及取舍明确、决策与理由完整、后续动作明确。

## 4. 必备字段

- `task_kind`：RESEARCH 或 DECISION；
- `status`：DRAFT/RESEARCH/DECIDED/DONE/BLOCKED；
- `decision_outcome`：PENDING/APPROVED/CHANGES_REQUIRED；
- 一手证据、决策与理由、后续动作、决策人/日期和证据路径。

只有需要代码实现时才派工程卡，进入子骨架完整工程流程，不给普通调研增加工程负担。
