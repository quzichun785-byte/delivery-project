import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "scripts" / "check_delivery.py"
SPEC = importlib.util.spec_from_file_location("check_delivery", MODULE_PATH)
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


MAIN_FLOW = ["DRAFT", "DISPATCHED", "READY", "BUILD", "VERIFY", "REVIEW", "ACCEPT", "DONE"]


def history_for(status):
    if status in MAIN_FLOW:
        states = MAIN_FLOW[:MAIN_FLOW.index(status) + 1]
        transitions = []
        for source, target in zip(states, states[1:]):
            role = "母" if source == "DRAFT" else ("母子" if source == "ACCEPT" else "子")
            transitions.append((role, source, target))
        return transitions
    if status == "BLOCKED_PRODUCT":
        return [("母", "DRAFT", "DISPATCHED"), ("子", "DISPATCHED", "BLOCKED_PRODUCT")]
    if status == "BLOCKED":
        return [("母", "DRAFT", "DISPATCHED"), ("子", "DISPATCHED", "READY"),
                ("子", "READY", "BUILD"), ("子", "BUILD", "BLOCKED")]
    return []


def card_text(status="DONE", risk="HIGH", product="APPROVED", engineering="APPROVED", human="NOT_REQUIRED", maturity="PILOT", task_version=1, blocked_from=None):
    if blocked_from is None:
        blocked_from = "DISPATCHED" if status == "BLOCKED_PRODUCT" else ("BUILD" if status == "BLOCKED" else "NONE")
    history = "\n".join(f"- 2026-10-28 | {role} | status: {source} -> {target} | task_version={task_version}"
                        for role, source, target in history_for(status)) or "- 创建。"
    human_detail = "评审人/日期及意见：专家/2026-10-28，证据 `artifacts/human_review.md`。" if human == "APPROVED" else human
    return f"""---
task_id: TASK-001
protocol_version: "1.0"
task_version: {task_version}
status: {status}
risk_level: {risk}
target_maturity: {maturity}
product_signoff: {product}
engineering_signoff: {engineering}
human_review: {human}
blocked_from: {blocked_from}
---
# 测试任务
## A. 产品定义区（母写）
产品目标与验收。
## B. 工程设计区（子写）
工程契约与验收。
## C. 执行证据区（子写）
### C1. 实现摘要与代码指针
已实现 example.py。
### C2. 可复现环境与数据
Python 锁定版本，种子 42。
### C3. 功能测试证据
`python -m unittest`：2/2 通过，日志 `artifacts/test.log`。
### C4. 集成验证证据
集成场景通过，`artifacts/integration.log`。
### C5. 独立审查证据
独立审查通过，`artifacts/review.md`。
### C6. 回滚与其他证据
N/A：无数据库和配置变化。
### C7. 生产就绪证据
N/A：非生产目标。
## D. 变更记录区（双方追加）
{history}
## E. 双签验收区（分角色签署）
### E1. 产品验收
- 结论：{product}
- 验收场景与证据：产品场景通过，`artifacts/product_acceptance.md`。
- 验收人/日期：产品验收人/2026-10-28
- 遗留问题：无
### E2. 工程验收
- 结论：{engineering}
- 测试、集成、审查和回滚证据：`artifacts/engineering_acceptance.md`。
- 验收人/日期：工程验收人/2026-10-28
- 未验证事项：无
### E3. 关键人工专业评审
- 结论：{human}
- {human_detail}
"""


def light_task_text(status="DONE", outcome="APPROVED"):
    return f"""---
task_id: RESEARCH-001
task_kind: RESEARCH
protocol_version: "1.0"
task_version: 1
status: {status}
decision_outcome: {outcome}
blocked_from: NONE
---
# 轻量调研
## 1. 要解决的问题与期望结果
确认方案。
## 2. 一手证据与来源
官方资料和实测记录。
## 3. 可选方案与取舍
方案 A 与方案 B 的成本和风险。
## 4. 决策与理由
选择方案 A，因为证据充分。
## 5. 后续动作
形成工程派单。
## 6. 决策证据与验收记录
- 结论：{outcome}
- 决策证据路径：`artifacts/decision.md`
- 决策人/日期：产品决策人/2026-10-28
- 未决问题：无
## 7. 变更记录（只追加）
- 创建。
"""


class DeliveryCheckTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.child = self.root / "子"
        self.tasks = self.child / "docs" / "TASKS"
        self.tasks.mkdir(parents=True)
        self.artifacts = self.child / "artifacts"
        self.artifacts.mkdir()
        for name in ("test.log", "integration.log", "review.md", "production.md",
                     "product_acceptance.md", "engineering_acceptance.md", "human_review.md"):
            (self.artifacts / name).write_text("verified", encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def write_task(self, text):
        path = self.tasks / "01-test.md"
        path.write_text(text, encoding="utf-8")
        return path

    def test_valid_done_task(self):
        task = self.write_task(card_text())
        self.assertEqual(CHECK.validate_task(task), [])

    def test_done_requires_dual_signoff(self):
        task = self.write_task(card_text(product="PENDING"))
        self.assertTrue(any("双签" in item or "均为 APPROVED" in item for item in CHECK.validate_task(task)))

    def test_review_requires_test_evidence(self):
        text = card_text(status="REVIEW", product="PENDING", engineering="PENDING").replace("`python -m unittest`", "NOT_RUN")
        task = self.write_task(text)
        self.assertTrue(any("功能测试证据" in item for item in CHECK.validate_task(task)))

    def test_high_risk_requires_independent_review(self):
        text = card_text(status="REVIEW", product="PENDING", engineering="PENDING").replace("独立审查通过", "NOT_RUN")
        task = self.write_task(text)
        self.assertTrue(any("独立审查证据" in item for item in CHECK.validate_task(task)))

    def test_blocked_product_requires_origin(self):
        task = self.write_task(card_text(status="BLOCKED_PRODUCT", product="PENDING", engineering="PENDING", blocked_from="NONE"))
        self.assertTrue(any("blocked_from" in item for item in CHECK.validate_task(task)))

    def test_evidence_sections_do_not_leak_into_each_other(self):
        text = card_text(status="REVIEW", product="PENDING", engineering="PENDING")
        text = text.replace("### E3. 关键人工专业评审\nNOT_REQUIRED", "### E3. 关键人工专业评审\n{{待填}}")
        task = self.write_task(text)
        self.assertEqual(CHECK.validate_task(task), [])

    def test_target_maturity_is_required(self):
        task = self.write_task(card_text().replace("target_maturity: PILOT\n", ""))
        self.assertTrue(any("target_maturity" in item for item in CHECK.validate_task(task)))

    def test_pilot_requires_rollback_evidence(self):
        text = card_text().replace("N/A：无数据库和配置变化。", "NOT_RUN")
        task = self.write_task(text)
        self.assertTrue(any("C6" in item for item in CHECK.validate_task(task)))

    def test_production_requires_c7(self):
        task = self.write_task(card_text(maturity="PRODUCTION"))
        self.assertTrue(any("C7" in item for item in CHECK.validate_task(task)))

    def test_valid_production_task(self):
        text = card_text(maturity="PRODUCTION").replace("N/A：非生产目标。", "生产验证通过，`artifacts/production.md`。")
        task = self.write_task(text)
        self.assertEqual(CHECK.validate_task(task), [])

    def test_illegal_transition_is_rejected(self):
        text = card_text().replace("BUILD -> VERIFY", "BUILD -> REVIEW")
        task = self.write_task(text)
        self.assertTrue(any("非法状态转移" in item for item in CHECK.validate_task(task)))

    def test_current_status_must_match_last_transition(self):
        text = card_text().replace("ACCEPT -> DONE", "REVIEW -> ACCEPT")
        task = self.write_task(text)
        self.assertTrue(any("不一致" in item for item in CHECK.validate_task(task)))

    def test_signoff_requires_person_date_and_evidence(self):
        text = card_text().replace("验收人/日期：产品验收人/2026-10-28", "验收人/日期：{{待填}}")
        task = self.write_task(text)
        self.assertTrue(any("占位内容" in item for item in CHECK.validate_task(task)))

    def test_signoff_metadata_must_match_section(self):
        text = card_text().replace("### E1. 产品验收\n- 结论：APPROVED", "### E1. 产品验收\n- 结论：PENDING")
        task = self.write_task(text)
        self.assertTrue(any("与元数据" in item for item in CHECK.validate_task(task)))

    def test_signoff_evidence_file_must_exist(self):
        (self.artifacts / "product_acceptance.md").unlink()
        task = self.write_task(card_text())
        self.assertTrue(any("product_acceptance.md" in item for item in CHECK.validate_task(task)))

    def test_product_resume_requires_version_increment(self):
        text = card_text(status="DISPATCHED", product="PENDING", engineering="PENDING")
        text = text.replace("- 2026-10-28 | 母 | status: DRAFT -> DISPATCHED | task_version=1",
                            "- 2026-10-28 | 母 | status: DRAFT -> DISPATCHED | task_version=1\n- 2026-10-28 | 子 | status: DISPATCHED -> BLOCKED_PRODUCT | task_version=1\n- 2026-10-28 | 母 | status: BLOCKED_PRODUCT -> DISPATCHED | task_version=1")
        task = self.write_task(text)
        self.assertTrue(any("提升 task_version" in item for item in CHECK.validate_task(task)))

    def test_valid_product_resume(self):
        text = card_text(status="DISPATCHED", product="PENDING", engineering="PENDING", task_version=2)
        text = text.replace("- 2026-10-28 | 母 | status: DRAFT -> DISPATCHED | task_version=2",
                            "- 2026-10-28 | 母 | status: DRAFT -> DISPATCHED | task_version=1\n- 2026-10-28 | 子 | status: DISPATCHED -> BLOCKED_PRODUCT | task_version=1\n- 2026-10-28 | 母 | status: BLOCKED_PRODUCT -> DISPATCHED | task_version=2")
        task = self.write_task(text)
        self.assertEqual(CHECK.validate_task(task), [])

    def test_done_by_child_role_is_rejected(self):
        text = card_text().replace("| 母子 | status: ACCEPT -> DONE", "| 子 | status: ACCEPT -> DONE")
        task = self.write_task(text)
        self.assertTrue(any("必须由母骨架或母子共同确认" in item for item in CHECK.validate_task(task)))

    def test_blocked_from_must_match_history(self):
        task = self.write_task(card_text(status="BLOCKED", product="PENDING", engineering="PENDING", blocked_from="READY"))
        self.assertTrue(any("最后状态不一致" in item for item in CHECK.validate_task(task)))

    def test_missing_transition_history_is_rejected(self):
        text = card_text(status="REVIEW", product="PENDING", engineering="PENDING")
        text = "\n".join(line for line in text.splitlines() if " | status:" not in line)
        task = self.write_task(text)
        self.assertTrue(any("缺少 D 区结构化状态转移历史" in item for item in CHECK.validate_task(task)))

    def write_light_task(self, text):
        mother = self.root / "母"
        (mother / "artifacts").mkdir(parents=True, exist_ok=True)
        (mother / "artifacts" / "decision.md").write_text("decision", encoding="utf-8")
        tasks = mother / "docs" / "TASKS"
        tasks.mkdir(parents=True, exist_ok=True)
        path = tasks / "01-research.md"
        path.write_text(text, encoding="utf-8")
        return path

    def test_valid_light_task(self):
        task = self.write_light_task(light_task_text())
        self.assertEqual(CHECK.validate_any_task(task), [])

    def test_light_done_requires_decision_outcome(self):
        task = self.write_light_task(light_task_text(outcome="PENDING"))
        self.assertTrue(any("decision_outcome=APPROVED" in item for item in CHECK.validate_any_task(task)))

    def test_light_done_requires_evidence_file(self):
        text = light_task_text().replace("`artifacts/decision.md`", "`artifacts/missing.md`")
        task = self.write_light_task(text)
        self.assertTrue(any("决策证据路径不存在" in item for item in CHECK.validate_any_task(task)))

    def make_pair(self):
        mother = self.root / "母"
        for base in (mother, self.child):
            (base / ".claude" / "commands").mkdir(parents=True, exist_ok=True)
            (base / "docs").mkdir(parents=True, exist_ok=True)
            (base / "CLAUDE.md").write_text("role", encoding="utf-8")
            (base / "docs" / "PROTOCOL.md").write_text('---\nprotocol_version: "1.0"\n---\n', encoding="utf-8")
        (mother / "docs" / "DISPATCH.md").write_text("dispatch", encoding="utf-8")
        (mother / "docs" / "TASKS").mkdir(exist_ok=True)
        (mother / "docs" / "TASKS" / "_TEMPLATE.md").write_text("light template", encoding="utf-8")
        (self.child / "docs" / "ASSETS.md").write_text("assets", encoding="utf-8")
        (self.child / "docs" / "OPERATIONS.md").write_text("operations", encoding="utf-8")
        (self.child / ".claude" / "commands" / "bootstrap-engineering.md").write_text("baseline", encoding="utf-8")
        (self.root / "PROJECT.md").write_text("project", encoding="utf-8")
        (self.tasks / "_TEMPLATE.md").write_text("template", encoding="utf-8")
        return mother

    def test_pair_structure_and_protocol(self):
        self.make_pair()
        self.assertEqual(CHECK.validate_pair(self.root), [])

    def test_pair_rejects_root_claude(self):
        self.make_pair()
        (self.root / "CLAUDE.md").write_text("ambiguous", encoding="utf-8")
        self.assertTrue(any("身份" in item for item in CHECK.validate_pair(self.root)))

    def test_pair_requires_baseline_assets(self):
        self.make_pair()
        (self.child / "docs" / "OPERATIONS.md").unlink()
        self.assertTrue(any("OPERATIONS.md" in item for item in CHECK.validate_pair(self.root)))

    def test_pair_requires_light_template(self):
        self.make_pair()
        (self.root / "母" / "docs" / "TASKS" / "_TEMPLATE.md").unlink()
        self.assertTrue(any("_TEMPLATE.md" in item for item in CHECK.validate_pair(self.root)))


if __name__ == "__main__":
    unittest.main()
