#!/usr/bin/env python3
"""Apply a structured /save-brain payload to project local-state files."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

LEGACY_SESSION_KEYS = (
    "working_on",
    "pending_tasks",
    "decisions_made",
    "recent_changes",
    "errors_encountered",
)
LEGACY_HANDOFF_SECTIONS = (
    ("working_on", "Working on", False),
    ("done", "DONE", True),
    ("remaining", "REMAINING", True),
    ("key_decisions", "KEY DECISIONS", True),
    ("notes_for_next_session", "NOTES FOR NEXT SESSION", True),
    ("key_files", "KEY FILES", True),
)
CANONICAL_REQUIRED_HANDOFF_SECTIONS = (
    ("current_work", "Current Work", False),
    ("working_set", "Working Set", True),
    ("decisions", "Decisions", True),
    ("verification", "Verification", True),
    ("next_actions", "Next Actions", True),
    ("blockers", "Blockers", True),
)
CANONICAL_OPTIONAL_HANDOFF_SECTIONS = (
    ("notes", "Notes", True),
    ("risks", "Risks", True),
    ("references", "References", True),
)
CANONICAL_HANDOFF_SECTIONS = CANONICAL_REQUIRED_HANDOFF_SECTIONS + CANONICAL_OPTIONAL_HANDOFF_SECTIONS
MIGRATION_HANDOFF_KEYS = (
    ("status", "Status", False),
    ("compressed_context", "Compressed Context", False),
    ("relevant_flow", "Relevant Flow", True),
    ("code_references", "Code References", True),
    ("done_this_session", "Done This Session", True),
    ("remaining_next", "Remaining / Next", True),
    ("gotchas", "Gotchas", True),
)
LEGACY_HANDOFF_KEYS = tuple(key for key, _title, _bullets in LEGACY_HANDOFF_SECTIONS)
MIGRATION_HANDOFF_KEYS_ONLY = tuple(key for key, _title, _bullets in MIGRATION_HANDOFF_KEYS)
CANONICAL_HANDOFF_KEYS = tuple(key for key, _title, _bullets in CANONICAL_HANDOFF_SECTIONS)
HANDOFF_KEYS = LEGACY_HANDOFF_KEYS + MIGRATION_HANDOFF_KEYS_ONLY + CANONICAL_HANDOFF_KEYS
HANDOFF_KEY_TARGETS = {
    "working_on": "current_work",
    "done": "notes",
    "remaining": "next_actions",
    "key_decisions": "decisions",
    "notes_for_next_session": "notes",
    "key_files": "working_set",
    "status": "current_work",
    "compressed_context": "notes",
    "relevant_flow": "working_set",
    "code_references": "working_set",
    "done_this_session": "notes",
    "remaining_next": "next_actions",
    "gotchas": "risks",
}
# Root AGENTS Template sections (references/state-templates.md in claude-project-state).
AGENTS_TEMPLATE_SECTIONS = frozenset(
    {
        "Project Scope",
        "Source Of Truth",
        "Repository Structure",
        "Architecture Constraints",
        "Commands And Verification",
        "Project-Specific Safety",
        "Maintenance Rules",
    }
)
# Sections that only ever describe session state. Deliberately excludes the
# ambiguous "Decisions"/"Verification", which a project may legitimately own as
# durable guidance; a hard gate must not produce false positives.
HANDOFF_ONLY_SECTIONS = frozenset(
    {
        "Current Work",
        "Working Set",
        "Next Actions",
        "Blockers",
        "Progress",
    }
)
HANDOFF_TOTAL_BUDGETS = {
    "lines": (80, 100, 120),
    "chars": (6000, 8000, 10000),
}
HANDOFF_ITEM_BUDGETS = {
    "Current Work": (3, 3, 5),
    "Working Set": (8, 8, 12),
    "Decisions": (8, 8, 12),
    "Verification": (6, 6, 10),
    "Next Actions": (6, 6, 10),
    "Blockers": (5, 5, 8),
    "Notes": (4, 4, 6),
    "Risks": (4, 4, 6),
    "References": (4, 4, 6),
}
CANONICAL_REQUIRED_HANDOFF_TITLES = tuple(title for _key, title, _bullets in CANONICAL_REQUIRED_HANDOFF_SECTIONS)
CANONICAL_OPTIONAL_HANDOFF_TITLES = tuple(title for _key, title, _bullets in CANONICAL_OPTIONAL_HANDOFF_SECTIONS)


class PayloadError(ValueError):
    """Raised when the save payload is malformed."""


def write_text_if_changed(path: Path, content: str) -> bool:
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    if current == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def git_holds_current(path: Path) -> bool:
    """True when path is tracked and identical to HEAD, so overwriting loses nothing git cannot restore."""
    def git(*args: str) -> int:
        try:
            return subprocess.run(["git", "-C", str(path.parent), *args], capture_output=True).returncode
        except OSError:
            return 1
    return git("ls-files", "--error-unmatch", "--", path.name) == 0 and git("diff", "--quiet", "HEAD", "--", path.name) == 0


def archive_before_overwrite(project_root: Path, path: Path, content: str, result: dict[str, Any]) -> None:
    """Copy an uncommitted or untracked file into <root>/.archived/ before save-brain replaces it."""
    if not path.exists():
        return
    current = path.read_text(encoding="utf-8")
    if current == content or git_holds_current(path):
        return
    archive_dir = project_root / ".archived"
    archive_dir.mkdir(parents=True, exist_ok=True)
    target = archive_dir / f"{path.name}.{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    target.write_text(current, encoding="utf-8")
    result.setdefault("archived_files", []).append(str(target))


def normalize_project_agents_markdown(value: Any) -> str:
    if not isinstance(value, str):
        raise PayloadError("project_agents_md must be a Markdown string")
    text = value.strip()
    if not text:
        raise PayloadError("project_agents_md must not be empty")
    if not text.startswith("# AGENTS.md"):
        raise PayloadError("project_agents_md must start with '# AGENTS.md'")
    if "## " not in text:
        raise PayloadError("project_agents_md must include at least one section heading")
    return text + ("\n" if not text.endswith("\n") else "")


def validate_project_agents_markdown(text: str) -> dict[str, Any]:
    """Check durable AGENTS.md for leaked session state and template drift.

    Two levels, deliberately asymmetric:
      * hard failure - a handoff-only section leaked in. This is the harm the
        AGENTS/handoff split exists to prevent, so the caller must refuse the
        write.
      * drift - a heading outside the Root AGENTS Template. Projects legitimately
        extend the template, so this is reported and still written.
    Judgment rules (entry admission filter, promotion threshold) are NOT checked
    here; they are documented as self-review checklists, not gates.
    """
    headings = [line[3:].strip() for line in text.splitlines() if line.startswith("## ")]
    lines = text.splitlines()
    leaked = [heading for heading in headings if heading in HANDOFF_ONLY_SECTIONS]
    non_template = [heading for heading in headings if heading not in AGENTS_TEMPLATE_SECTIONS]
    hard_failures = [
        {"name": f"handoff section in AGENTS.md: {heading}", "level": "fail"} for heading in leaked
    ]
    if hard_failures:
        status = "leaked-handoff-state"
    elif non_template:
        status = "drift"
    else:
        status = "ok"
    return {
        "status": status,
        "hard_failures": hard_failures,
        "leaked_handoff_sections": leaked,
        "non_template_headings": non_template,
        "heading_count": len(headings),
        "headings": headings,
        "line_count": len(lines),
        "char_count": len(text),
    }


def load_payload(args: argparse.Namespace) -> dict[str, Any]:
    if args.payload_file:
        raw_payload = Path(args.payload_file).read_text(encoding="utf-8")
    else:
        raw_payload = sys.stdin.read()
    if not raw_payload.strip():
        raise PayloadError("missing JSON payload")
    try:
        payload = json.loads(raw_payload)
    except json.JSONDecodeError as exc:
        raise PayloadError(f"invalid payload JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise PayloadError("payload must be a JSON object")
    return payload


def stringify_lines(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [line.strip() for line in value.splitlines() if line.strip()]
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    raise PayloadError("handoff section values must be strings or lists")


def add_handoff_values(target: dict[str, list[str]], key: str, value: Any) -> None:
    values = stringify_lines(value)
    if not values:
        return
    target.setdefault(key, []).extend(values)


def canonicalize_handoff(handoff: dict[str, Any]) -> dict[str, list[str]]:
    canonical: dict[str, list[str]] = {key: [] for key, _title, _bullets in CANONICAL_REQUIRED_HANDOFF_SECTIONS}
    for key, _title, _bullets in CANONICAL_OPTIONAL_HANDOFF_SECTIONS:
        if key in handoff:
            canonical[key] = []

    for key, value in handoff.items():
        if key in CANONICAL_HANDOFF_KEYS:
            add_handoff_values(canonical, key, value)
            continue
        target_key = HANDOFF_KEY_TARGETS.get(key)
        if target_key:
            add_handoff_values(canonical, target_key, value)
    return canonical


def handoff_item_count(values: list[str]) -> int:
    return len(values)


def validate_budget(name: str, count: int, budget: tuple[int, int, int]) -> dict[str, Any] | None:
    target, warning, failure = budget
    if count > failure:
        return {
            "name": name,
            "count": count,
            "target": target,
            "warning": warning,
            "failure": failure,
            "level": "fail",
        }
    if count > warning:
        return {
            "name": name,
            "count": count,
            "target": target,
            "warning": warning,
            "failure": failure,
            "level": "warn",
        }
    return None


def validate_handoff_sections(sections: dict[str, list[str]]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    for key, title, _bullets in CANONICAL_HANDOFF_SECTIONS:
        issue = validate_budget(
            f"{title} items",
            handoff_item_count(sections.get(key, [])),
            HANDOFF_ITEM_BUDGETS[title],
        )
        if issue:
            issues.append(issue)
    return issues


def validate_handoff_headings(text: str, sections: dict[str, list[str]]) -> dict[str, Any] | None:
    headings = [line[3:].strip() for line in text.splitlines() if line.startswith("## ")]
    optional_titles = [
        title
        for key, title, _bullets in CANONICAL_OPTIONAL_HANDOFF_SECTIONS
        if key in sections
    ]
    expected = [*CANONICAL_REQUIRED_HANDOFF_TITLES, *optional_titles]
    if headings == expected:
        return None
    return {
        "name": "heading order",
        "count": len(headings),
        "expected": expected,
        "actual": headings,
        "level": "fail",
    }


def validate_handoff_text(text: str, sections: dict[str, list[str]]) -> dict[str, Any]:
    lines = text.splitlines()
    issues = validate_handoff_sections(sections)
    heading_issue = validate_handoff_headings(text, sections)
    if heading_issue:
        issues.append(heading_issue)
    for name, count in (("lines", len(lines)), ("chars", len(text))):
        issue = validate_budget(name, count, HANDOFF_TOTAL_BUDGETS[name])
        if issue:
            issues.append(issue)
    hard_failures = [issue for issue in issues if issue["level"] == "fail"]
    return {
        "status": "oversized" if issues else "ok",
        "issues": issues,
        "hard_failures": hard_failures,
        "line_count": len(lines),
        "char_count": len(text),
    }


def render_section(title: str, values: list[str], *, bullets: bool = True) -> list[str]:
    lines = [f"## {title}", ""]
    if not values:
        empty_value = "None"
        lines.extend([f"- {empty_value}" if bullets else empty_value, ""])
        return lines
    if not bullets:
        lines.extend([*values, ""])
        return lines
    lines.extend([f"- {value}" for value in values])
    lines.append("")
    return lines


def build_handoff_text(payload: dict[str, Any]) -> str:
    handoff = payload.get("handoff", payload.get("handover"))
    if not isinstance(handoff, dict):
        raise PayloadError("handoff must be an object")
    unknown = sorted(set(handoff) - set(HANDOFF_KEYS))
    if unknown:
        raise PayloadError(f"unsupported handoff keys: {', '.join(unknown)}")

    canonical = canonicalize_handoff(handoff)
    lines = ["# Handoff", ""]
    for key, title, bullets in CANONICAL_HANDOFF_SECTIONS:
        if key in canonical:
            lines.extend(render_section(title, canonical.get(key, []), bullets=bullets))
    text = "\n".join(lines).rstrip() + "\n"
    validation = validate_handoff_text(text, canonical)
    if validation["hard_failures"]:
        names = ", ".join(f'{issue["name"]} {issue["count"]}>{issue["failure"]}' for issue in validation["hard_failures"])
        raise PayloadError(f"handoff validation failed: {names}")
    return text


def apply_payload(project_root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {"status": "ok", "project_root": str(project_root), "changed_files": []}
    ignored_session_keys = sorted(key for key in LEGACY_SESSION_KEYS if key in payload)
    if ignored_session_keys:
        result["ignored_legacy_session_keys"] = ignored_session_keys

    # Render and validate every target before writing any of them. A rejected
    # payload must leave the working tree untouched, otherwise a refused
    # AGENTS.md still ships a written handoff.md.
    handoff_text: str | None = None
    handoff: Any = None
    if "handoff" in payload or "handover" in payload:
        handoff_text = build_handoff_text(payload)
        handoff = payload.get("handoff", payload.get("handover"))
        if (
            isinstance(handoff, dict)
            and not any(canonicalize_handoff(handoff).values())
            and (project_root / "handoff.md").exists()
        ):
            raise PayloadError("empty handoff payload would overwrite existing handoff.md")

    agents_payload = payload.get("project_agents_md", payload.get("agents_md"))
    agents_text: str | None = None
    agents_validation: dict[str, Any] | None = None
    if agents_payload is not None:
        agents_text = normalize_project_agents_markdown(agents_payload)
        agents_validation = validate_project_agents_markdown(agents_text)
        if agents_validation["hard_failures"]:
            names = ", ".join(issue["name"] for issue in agents_validation["hard_failures"])
            raise PayloadError(f"AGENTS.md validation failed: {names}")

    if handoff_text is not None:
        handoff_path = project_root / "handoff.md"
        result["handoff_validation"] = validate_handoff_text(handoff_text, canonicalize_handoff(handoff))
        archive_before_overwrite(project_root, handoff_path, handoff_text, result)
        add_change(result, handoff_path, write_text_if_changed(handoff_path, handoff_text))

    if agents_text is not None:
        agents_path = project_root / "AGENTS.md"
        result["agents_validation"] = agents_validation
        archive_before_overwrite(project_root, agents_path, agents_text, result)
        changed = write_text_if_changed(agents_path, agents_text)
        result["agents_md_changed"] = changed
        if changed:
            result["changed_files"].append(str(agents_path))

    return result


def add_change(result: dict[str, Any], path: Path, changed: bool) -> None:
    key = path.name.replace(".", "_")
    result[f"{key}_changed"] = changed
    if changed:
        result["changed_files"].append(str(path))


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply structured /save-brain JSON payload.")
    parser.add_argument("--project-root", default=".", help="Project root containing handoff.md and AGENTS.md.")
    parser.add_argument("--payload-file", help="Read payload JSON from this file instead of stdin.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        payload = load_payload(args)
        result = apply_payload(Path(args.project_root).resolve(), payload)
    except (OSError, PayloadError) as exc:
        result = {"status": "error", "reason": str(exc)}
        sys.stderr.write(json.dumps(result, ensure_ascii=False) + "\n")
        return 2
    sys.stdout.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
