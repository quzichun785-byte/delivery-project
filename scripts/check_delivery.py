#!/usr/bin/env python3
"""delivery-project 基础结构校验。

只检查目录、协议、任务卡必填项、状态、双签及证据占位/路径；
不判断测试是否有效，也不判断代码是否达到生产质量。
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

STATUSES = {
    "DRAFT", "DISPATCHED", "READY", "BUILD", "VERIFY", "REVIEW",
    "ACCEPT", "DONE", "BLOCKED", "BLOCKED_PRODUCT",
}
SIGNOFFS = {"PENDING", "APPROVED", "CHANGES_REQUIRED"}
RISKS = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
MATURITIES = {"DEMO", "PILOT", "PRODUCTION"}
HUMAN_REVIEW = {"NOT_REQUIRED", "PENDING", "APPROVED", "CHANGES_REQUIRED"}
REQUIRED_FIELDS = (
    "task_id", "protocol_version", "task_version", "status", "risk_level",
    "target_maturity", "product_signoff", "engineering_signoff", "human_review", "blocked_from",
)
REQUIRED_SECTIONS = (
    "## A. 产品定义区", "## B. 工程设计区", "## C. 执行证据区",
    "## D. 变更记录区", "## E. 双签验收区",
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("缺少 YAML frontmatter 起始 ---")
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration as exc:
        raise ValueError("缺少 YAML frontmatter 结束 ---") from exc
    data: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def section(text: str, marker: str) -> str:
    start = text.find(marker)
    if start < 0:
        return ""
    remainder = text[start + len(marker):]
    next_heading = re.search(r"\n#{2,3}\s", remainder)
    end = len(text) if next_heading is None else start + len(marker) + next_heading.start()
    return text[start:end]


def has_unresolved(text: str) -> bool:
    return "{{" in text or "}}" in text


def evidence_missing(text: str) -> bool:
    return not text.strip() or "NOT_RUN" in text or bool(re.search(r"\bNONE\b", text)) or has_unresolved(text)


def evidence_paths(text: str) -> list[str]:
    """只提取反引号中、带扩展名的证据路径，避免把命令当路径。"""
    candidates = re.findall(r"`([^`\n]+)`", text)
    result = []
    for item in candidates:
        value = item.strip()
        if not value or "{{" in value or " " in value:
            continue
        if re.search(r"\.[A-Za-z0-9]{1,8}$", value) and ("/" in value or "\\" in value):
            result.append(value)
    return result


ALLOWED_TRANSITIONS = {
    "DRAFT": {"DISPATCHED", "BLOCKED", "BLOCKED_PRODUCT"},
    "DISPATCHED": {"READY", "BLOCKED", "BLOCKED_PRODUCT"},
    "READY": {"BUILD", "BLOCKED", "BLOCKED_PRODUCT"},
    "BUILD": {"VERIFY", "BLOCKED", "BLOCKED_PRODUCT"},
    "VERIFY": {"REVIEW", "BUILD", "BLOCKED", "BLOCKED_PRODUCT"},
    "REVIEW": {"ACCEPT", "BUILD", "BLOCKED", "BLOCKED_PRODUCT"},
    "ACCEPT": {"DONE", "BUILD", "BLOCKED", "BLOCKED_PRODUCT"},
    "BLOCKED": {"DISPATCHED", "READY", "BUILD", "VERIFY", "REVIEW", "ACCEPT"},
    "BLOCKED_PRODUCT": {"DISPATCHED"},
    "DONE": set(),
}
RECOVERABLE_STATES = {"DRAFT", "DISPATCHED", "READY", "BUILD", "VERIFY", "REVIEW", "ACCEPT"}
LIGHT_STATUSES = {"DRAFT", "RESEARCH", "DECIDED", "DONE", "BLOCKED"}
LIGHT_KINDS = {"RESEARCH", "DECISION"}
LIGHT_OUTCOMES = {"PENDING", "APPROVED", "CHANGES_REQUIRED"}
LIGHT_SECTIONS = (
    "## 1. 要解决的问题", "## 2. 一手证据", "## 3. 可选方案",
    "## 4. 决策与理由", "## 5. 后续动作", "## 6. 决策证据",
)


def transition_history(text: str) -> list[tuple[str, str, str]]:
    history_text = section(text, "## D. 变更记录区")
    pattern = r"\|\s*(母|子|母子)\s*\|\s*status:\s*([A-Z_]+)\s*->\s*([A-Z_]+)"
    return re.findall(pattern, history_text)


def signoff_conclusion(text: str) -> str | None:
    match = re.search(r"-\s*结论：\s*([A-Z_]+)", text)
    return match.group(1) if match else None


def validate_task(path: Path, check_paths: bool = True) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f"任务卡不存在：{path}"]
    text = read_text(path)
    try:
        meta = frontmatter(text)
    except ValueError as exc:
        return [f"{path.name}: {exc}"]

    for field in REQUIRED_FIELDS:
        if field not in meta or not meta[field]:
            errors.append(f"缺少元数据 {field}")
    for marker in REQUIRED_SECTIONS:
        if marker not in text:
            errors.append(f"缺少分区 {marker}")
    if errors:
        return [f"{path.name}: {item}" for item in errors]

    status = meta["status"]
    risk = meta["risk_level"]
    maturity = meta["target_maturity"]
    if status not in STATUSES:
        errors.append(f"未知状态 {status}")
    if risk not in RISKS:
        errors.append(f"未知风险级别 {risk}")
    if maturity not in MATURITIES:
        errors.append(f"未知目标成熟度 {maturity}")
    for field in ("product_signoff", "engineering_signoff"):
        if meta[field] not in SIGNOFFS:
            errors.append(f"{field} 非法取值 {meta[field]}")
    if meta["human_review"] not in HUMAN_REVIEW:
        errors.append(f"human_review 非法取值 {meta['human_review']}")
    try:
        task_version = int(meta["task_version"])
        if task_version < 1:
            errors.append("task_version 必须 >= 1")
    except ValueError:
        task_version = 0
        errors.append("task_version 必须为整数")

    history = transition_history(text)
    if status not in {"DRAFT", "DISPATCHED"} and not history:
        errors.append(f"{status} 缺少 D 区结构化状态转移历史")
    for role, source, target in history:
        if target not in ALLOWED_TRANSITIONS.get(source, set()):
            errors.append(f"非法状态转移 {source} -> {target}")
        if source == "BLOCKED_PRODUCT" and target == "DISPATCHED" and role != "母":
            errors.append("BLOCKED_PRODUCT 重新派单必须由母骨架处理")
        if source == "ACCEPT" and target == "DONE" and role not in {"母", "母子"}:
            errors.append("DONE 必须由母骨架或母子共同确认")
    if history and history[-1][2] != status:
        errors.append(f"当前状态 {status} 与最后转移目标 {history[-1][2]} 不一致")
    if status in {"REVIEW", "ACCEPT", "DONE"} and history and history[0][1] != "DRAFT":
        errors.append("REVIEW 及以后状态必须从 DRAFT 起有完整转移链")
    if status == "DONE" and history and history[-1][1:] != ("ACCEPT", "DONE"):
        errors.append("DONE 的最后一步必须是 ACCEPT -> DONE")

    if status in {"BLOCKED", "BLOCKED_PRODUCT"}:
        if meta["blocked_from"] == "NONE":
            errors.append(f"{status} 必须在 blocked_from 记录此前状态")
        elif meta["blocked_from"] not in RECOVERABLE_STATES:
            errors.append(f"blocked_from 不是可恢复状态：{meta['blocked_from']}")
        if history and meta["blocked_from"] != history[-1][1]:
            errors.append("blocked_from 与进入阻塞前的最后状态不一致")
    if status == "DISPATCHED" and history and history[-1][1] == "BLOCKED_PRODUCT" and task_version < 2:
        errors.append("产品问题重新派单必须提升 task_version")

    c1 = section(text, "### C1.")
    c3 = section(text, "### C3.")
    c4 = section(text, "### C4.")
    c5 = section(text, "### C5.")
    c6 = section(text, "### C6.")
    c7 = section(text, "### C7.")

    if status in {"REVIEW", "ACCEPT", "DONE"}:
        for name, body in (("功能测试证据 C3", c3), ("集成验证证据 C4", c4)):
            if evidence_missing(body):
                errors.append(f"{status} 缺少已执行的{name}")
        if risk in {"HIGH", "CRITICAL"} and evidence_missing(c5):
            errors.append(f"{status} 的 {risk} 任务缺少独立审查证据 C5")

    if status in {"ACCEPT", "DONE"} and maturity in {"PILOT", "PRODUCTION"} and evidence_missing(c6):
        errors.append(f"{status} 的 {maturity} 任务缺少 C6 异常/权限/回滚证据或合理 N/A")
    if status in {"ACCEPT", "DONE"} and maturity == "PRODUCTION" and (evidence_missing(c7) or "N/A" in c7):
        errors.append(f"{status} 的 PRODUCTION 任务缺少 C7 生产就绪证据（不可用 N/A 代替）")

    e1 = section(text, "### E1.")
    e2 = section(text, "### E2.")
    e3 = section(text, "### E3.")
    for field, body, label in (("product_signoff", e1, "产品"), ("engineering_signoff", e2, "工程")):
        conclusion = signoff_conclusion(body)
        if conclusion and conclusion != meta[field]:
            errors.append(f"{label}验收分区结论 {conclusion} 与元数据 {meta[field]} 不一致")

    signoff_evidence = ""
    if status == "DONE":
        if meta["product_signoff"] != "APPROVED" or meta["engineering_signoff"] != "APPROVED":
            errors.append("DONE 必须产品验收与工程验收均为 APPROVED")
        if risk == "CRITICAL" and meta["human_review"] != "APPROVED":
            errors.append("CRITICAL 任务 DONE 前必须人工专业评审 APPROVED")
        if not c1 or "NONE" in c1 or has_unresolved(c1):
            errors.append("DONE 缺少实际实现摘要/代码指针 C1")

        for label, body, required_labels in (
            ("产品", e1, ("验收场景与证据", "验收人/日期", "遗留问题")),
            ("工程", e2, ("测试、集成、审查和回滚证据", "验收人/日期", "未验证事项")),
        ):
            if has_unresolved(body):
                errors.append(f"DONE 的{label}验收仍有未填写占位内容")
            if signoff_conclusion(body) != "APPROVED":
                errors.append(f"DONE 的{label}验收分区必须为 APPROVED")
            for required_label in required_labels:
                if required_label not in body:
                    errors.append(f"DONE 的{label}验收缺少字段：{required_label}")
            paths = evidence_paths(body)
            if not paths:
                errors.append(f"DONE 的{label}验收缺少可检查的证据路径")
            signoff_evidence += body

        if risk == "CRITICAL":
            if has_unresolved(e3) or "评审人/日期" not in e3:
                errors.append("CRITICAL 的人工专业评审缺少结论、人员或日期")
            if not evidence_paths(e3):
                errors.append("CRITICAL 的人工专业评审缺少证据路径")
            signoff_evidence += e3

    if check_paths and status in {"REVIEW", "ACCEPT", "DONE"}:
        child_root = path.parents[2] if len(path.parents) > 2 else path.parent
        evidence_text = c3 + c4 + c5 + c6 + (c7 if maturity == "PRODUCTION" else "") + signoff_evidence
        for raw in evidence_paths(evidence_text):
            candidate = Path(raw)
            if not candidate.is_absolute():
                candidate = child_root / candidate
            if not candidate.exists():
                errors.append(f"证据路径不存在：{raw}")

    return [f"{path.name}: {item}" for item in errors]


def is_light_task(path: Path) -> bool:
    try:
        return "task_kind" in frontmatter(read_text(path))
    except (OSError, ValueError):
        return False


def validate_light_task(path: Path, check_paths: bool = True) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f"轻量任务卡不存在：{path}"]
    text = read_text(path)
    try:
        meta = frontmatter(text)
    except ValueError as exc:
        return [f"{path.name}: {exc}"]

    for field in ("task_kind", "protocol_version", "task_version", "status", "decision_outcome", "blocked_from"):
        if field not in meta or not meta[field]:
            errors.append(f"轻量卡缺少元数据 {field}")
    for marker in LIGHT_SECTIONS:
        if marker not in text:
            errors.append(f"轻量卡缺少分区 {marker}")
    if errors:
        return [f"{path.name}: {item}" for item in errors]

    status = meta["status"]
    if meta["task_kind"] not in LIGHT_KINDS:
        errors.append(f"轻量卡 task_kind 非法：{meta['task_kind']}")
    if status not in LIGHT_STATUSES:
        errors.append(f"轻量卡状态非法：{status}")
    if meta["decision_outcome"] not in LIGHT_OUTCOMES:
        errors.append(f"轻量卡 decision_outcome 非法：{meta['decision_outcome']}")
    try:
        if int(meta["task_version"]) < 1:
            errors.append("轻量卡 task_version 必须 >= 1")
    except ValueError:
        errors.append("轻量卡 task_version 必须为整数")
    if status == "BLOCKED" and meta["blocked_from"] not in {"DRAFT", "RESEARCH", "DECIDED"}:
        errors.append("轻量卡 BLOCKED 必须填写可恢复的 blocked_from")

    if status in {"DECIDED", "DONE"}:
        decision = section(text, "## 4. 决策与理由")
        if not decision or has_unresolved(decision) or "PENDING" in decision:
            errors.append(f"{status} 的轻量卡缺少明确决策与理由")
    if status == "DONE":
        if meta["decision_outcome"] != "APPROVED":
            errors.append("轻量卡 DONE 必须 decision_outcome=APPROVED")
        record = section(text, "## 6. 决策证据")
        if has_unresolved(record) or "决策人/日期" not in record:
            errors.append("轻量卡 DONE 缺少决策人/日期或存在占位内容")
        paths = evidence_paths(record)
        if not paths:
            errors.append("轻量卡 DONE 缺少决策证据路径")
        if check_paths:
            mother_root = path.parents[2] if len(path.parents) > 2 else path.parent
            for raw in paths:
                candidate = Path(raw)
                if not candidate.is_absolute():
                    candidate = mother_root / candidate
                if not candidate.exists():
                    errors.append(f"轻量卡决策证据路径不存在：{raw}")
    return [f"{path.name}: {item}" for item in errors]


def validate_any_task(path: Path) -> list[str]:
    return validate_light_task(path) if is_light_task(path) else validate_task(path)


def validate_pair(root: Path, mother_name: str = "母", child_name: str = "子") -> list[str]:
    errors: list[str] = []
    if not root.is_dir():
        return [f"项目根不存在：{root}"]
    if (root / "CLAUDE.md").exists():
        errors.append("项目根不得存在 CLAUDE.md（会污染母子身份）")
    if (root / ".claude").exists():
        errors.append("项目根不得存在 .claude/（会污染母子身份）")

    mother = root / mother_name
    child = root / child_name
    required = [
        root / "PROJECT.md", mother / "CLAUDE.md", mother / "docs" / "PROTOCOL.md",
        mother / "docs" / "DISPATCH.md", mother / ".claude" / "commands",
        mother / "docs" / "TASKS" / "_TEMPLATE.md",
        child / "CLAUDE.md", child / "docs" / "PROTOCOL.md",
        child / "docs" / "ASSETS.md", child / "docs" / "OPERATIONS.md",
        child / "docs" / "TASKS" / "_TEMPLATE.md", child / ".claude" / "commands",
        child / ".claude" / "commands" / "bootstrap-engineering.md",
    ]
    for item in required:
        if not item.exists():
            errors.append(f"缺少骨架文件/目录：{item}")
    if errors:
        return errors

    try:
        mother_version = frontmatter(read_text(mother / "docs" / "PROTOCOL.md"))["protocol_version"]
        child_version = frontmatter(read_text(child / "docs" / "PROTOCOL.md"))["protocol_version"]
        if mother_version != child_version:
            errors.append(f"母子协议版本不一致：{mother_version} != {child_version}")
    except (ValueError, KeyError) as exc:
        errors.append(f"协议 frontmatter 无效：{exc}")

    tasks_dir = child / "docs" / "TASKS"
    if tasks_dir.is_dir():
        for task in sorted(tasks_dir.glob("*.md")):
            if task.name.startswith("_") or task.name == "README.md":
                continue
            errors.extend(validate_task(task))

    light_dir = mother / "docs" / "TASKS"
    if light_dir.is_dir():
        for task in sorted(light_dir.glob("*.md")):
            if task.name.startswith("_") or task.name == "README.md":
                continue
            errors.extend(validate_light_task(task))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--task", type=Path, help="校验一张任务卡")
    group.add_argument("--pair", type=Path, help="校验母子项目根")
    group.add_argument("--child", type=Path, help="校验子骨架中的实际工程卡")
    group.add_argument("--mother", type=Path, help="校验母骨架中的轻量调研/决策卡")
    parser.add_argument("--mother-name", default="母")
    parser.add_argument("--child-name", default="子")
    args = parser.parse_args()

    if args.task:
        errors = validate_any_task(args.task)
        subject = str(args.task)
    elif args.pair:
        errors = validate_pair(args.pair, args.mother_name, args.child_name)
        subject = str(args.pair)
    elif args.mother:
        light_dir = args.mother / "docs" / "TASKS"
        errors = [] if light_dir.is_dir() else [f"轻量任务卡目录不存在：{light_dir}"]
        if not errors:
            for task in sorted(light_dir.glob("*.md")):
                if not task.name.startswith("_") and task.name != "README.md":
                    errors.extend(validate_light_task(task))
        subject = str(args.mother)
    else:
        tasks_dir = args.child / "docs" / "TASKS"
        errors = [] if tasks_dir.is_dir() else [f"任务卡目录不存在：{tasks_dir}"]
        if not errors:
            for task in sorted(tasks_dir.glob("*.md")):
                if not task.name.startswith("_") and task.name != "README.md":
                    errors.extend(validate_task(task))
        subject = str(args.child)

    if errors:
        print(f"[FAIL] {subject}")
        for error in errors:
            print(f" - {error}")
        return 1
    print(f"[OK] {subject}：结构与证据基础校验通过（不代表代码质量证明）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
