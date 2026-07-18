#!/usr/bin/env python3
"""Dependency-free structural and contract check for the project-local harness."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


MINIMAL = (
    "AGENTS.md",
    "INSTRUCTIONS.md",
    "PROGRESS.md",
    "HANDOFF.md",
    ".harness/config.json",
    "scripts/check-project-harness.py",
)

GOVERNED = (
    "docs/README.md",
    "docs/decisions/index.md",
    "docs/decisions/decision-template.md",
    "docs/exec-plans/roadmap.md",
    "docs/exec-plans/proposed/index.md",
    "docs/exec-plans/active/index.md",
    "docs/exec-plans/completed/index.md",
    "docs/exec-plans/plan-template.md",
    "docs/exec-plans/reviews/index.md",
    "docs/exec-plans/reviews/review-template.md",
    "docs/optimization/index.md",
    "docs/optimization/SOP.md",
    "docs/optimization/record-template.md",
    "docs/progress-archive/index.md",
    "scripts/check-startup-doc-budget.py",
)

LINK_SURFACES = (
    "docs/README.md",
    "docs/exec-plans/roadmap.md",
    "docs/exec-plans/proposed/index.md",
    "docs/exec-plans/active/index.md",
    "docs/exec-plans/completed/index.md",
    "docs/exec-plans/reviews/index.md",
    "docs/decisions/index.md",
    "docs/optimization/index.md",
    "docs/progress-archive/index.md",
)

DOCS_AUTHORITY_TARGETS = (
    "../AGENTS.md",
    "../INSTRUCTIONS.md",
    "../PROGRESS.md",
    "../HANDOFF.md",
    "roadmap.md",
    "exec-plans/roadmap.md",
    "decisions/index.md",
    "optimization/index.md",
    "progress-archive/index.md",
)

LIFECYCLE_TARGETS = (
    "proposed/index.md",
    "active/index.md",
    "completed/index.md",
    "reviews/index.md",
)


def infer_profile(root: Path) -> str:
    config = root / ".harness" / "config.json"
    if config.is_file():
        try:
            value = json.loads(config.read_text(encoding="utf-8")).get("profile")
            if value in {"minimal", "governed"}:
                return value
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, AttributeError):
            pass
    return "governed" if (root / "docs/exec-plans/roadmap.md").is_file() else "minimal"


def load_config(root: Path, profile: str, errors: list[str]) -> dict[str, Any]:
    path = root / ".harness" / "config.json"
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(f"config: cannot read valid .harness/config.json: {type(exc).__name__}: {exc}")
        return {}
    if not isinstance(config, dict):
        errors.append("config: root value must be a JSON object")
        return {}
    if config.get("schema_version") != "project-harness-config-v1":
        errors.append(
            f"config: unsupported schema_version={config.get('schema_version')!r}; "
            "expected 'project-harness-config-v1'"
        )
    if config.get("profile") != profile:
        errors.append(f"config: profile mismatch: config={config.get('profile')!r} requested={profile!r}")
    commands = config.get("verification_commands")
    if not isinstance(commands, list) or not commands or not all(isinstance(item, str) and item for item in commands):
        errors.append("config: verification_commands must be a non-empty string list")
    return config


def check_github_contract(root: Path, config: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    github = config.get("github")
    result: dict[str, Any] = {"workflow": None, "pull_request_template": None, "checks": []}
    if not isinstance(github, dict):
        errors.append("config.github: object is required")
        return result

    workflow = configured_file(root, github.get("workflow"), "config.github.workflow", errors)
    template = configured_file(
        root,
        github.get("pull_request_template"),
        "config.github.pull_request_template",
        errors,
    )
    checks = github.get("checks")
    if not isinstance(checks, list) or not checks or not all(isinstance(item, str) and item for item in checks):
        errors.append("config.github.checks: must be a non-empty string list")
        checks = []

    workflow_names: list[str] = []
    if workflow is not None:
        try:
            workflow_names = workflow_job_display_names(workflow.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError) as exc:
            errors.append(f"workflow: cannot read {workflow.relative_to(root)}: {exc}")
        if not workflow_names:
            errors.append(f"workflow: no job display names found under jobs: in {workflow.relative_to(root)}")
        elif checks and workflow_names != checks:
            errors.append(
                "workflow: config.github.checks must exactly match workflow job display names in order: "
                f"config={checks} workflow={workflow_names}"
            )

    result.update({
        "workflow": str(workflow.relative_to(root)) if workflow else None,
        "pull_request_template": str(template.relative_to(root)) if template else None,
        "checks": checks,
        "workflow_job_names": workflow_names,
    })
    return result


def configured_file(
    root: Path,
    raw_value: Any,
    field: str,
    errors: list[str],
) -> Path | None:
    if not isinstance(raw_value, str) or not raw_value.strip():
        errors.append(f"{field}: non-empty repository-relative path is required")
        return None
    candidate = (root / raw_value).resolve()
    if candidate != root and root not in candidate.parents:
        errors.append(f"{field}: path escapes repository root: {raw_value}")
        return None
    if not candidate.is_file():
        errors.append(f"{field}: referenced file does not exist: {raw_value}")
        return None
    return candidate


def workflow_job_display_names(text: str) -> list[str]:
    names: list[str] = []
    in_jobs = False
    current_job: str | None = None
    current_name: str | None = None

    def finish_job() -> None:
        nonlocal current_job, current_name
        if current_job is not None:
            names.append(current_name or current_job)
        current_job = None
        current_name = None

    for raw_line in text.splitlines():
        if not in_jobs:
            if re.fullmatch(r"jobs:\s*", raw_line):
                in_jobs = True
            continue
        if raw_line and not raw_line.startswith((" ", "\t")):
            break
        job_match = re.fullmatch(r"  ([A-Za-z0-9_-]+):\s*", raw_line)
        if job_match:
            finish_job()
            current_job = job_match.group(1)
            continue
        name_match = re.fullmatch(r"    name:\s*(.+?)\s*", raw_line)
        if current_job is not None and name_match and current_name is None:
            current_name = name_match.group(1).strip("'\"")
    finish_job()
    return names


def check_markdown_contracts(root: Path, errors: list[str]) -> dict[str, list[str]]:
    checked: dict[str, list[str]] = {}
    for relative in LINK_SURFACES:
        path = root / relative
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            errors.append(f"links: cannot read {relative}: {exc}")
            continue
        targets: list[str] = []
        for match in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", text):
            raw_target = match.group(1).strip().strip("<>")
            if not raw_target or raw_target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            target_without_anchor = raw_target.split("#", 1)[0]
            resolved = (path.parent / target_without_anchor).resolve()
            targets.append(raw_target)
            if resolved != root and root not in resolved.parents:
                errors.append(f"links: {relative} target escapes repository root: {raw_target}")
            elif not resolved.exists():
                errors.append(f"links: {relative} target does not exist: {raw_target}")
        checked[relative] = targets

    docs_index = root / "docs/README.md"
    if docs_index.is_file():
        text = docs_index.read_text(encoding="utf-8")
        for target in DOCS_AUTHORITY_TARGETS:
            if target not in text:
                errors.append(f"docs authority: docs/README.md does not route {target}")

    roadmap = root / "docs/exec-plans/roadmap.md"
    if roadmap.is_file():
        text = roadmap.read_text(encoding="utf-8")
        for target in LIFECYCLE_TARGETS:
            if target not in text:
                errors.append(f"lifecycle: docs/exec-plans/roadmap.md does not route {target}")
    return checked


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--profile", choices=("auto", "minimal", "governed"), default="auto")
    args = parser.parse_args(argv)

    root = args.root.expanduser().resolve()
    profile = infer_profile(root) if args.profile == "auto" else args.profile
    required = list(MINIMAL) + (list(GOVERNED) if profile == "governed" else [])
    files = [{"path": relative, "present": (root / relative).is_file()} for relative in required]
    missing = [item["path"] for item in files if not item["present"]]
    errors = [f"files: missing required harness artifact: {relative}" for relative in missing]

    config = load_config(root, profile, errors)
    github_contract = check_github_contract(root, config, errors) if config else {}
    markdown_links = check_markdown_contracts(root, errors) if profile == "governed" else {}

    payload = {
        "schema_version": "project-local-harness-check-v2",
        "root": str(root),
        "profile": profile,
        "files": files,
        "missing": missing,
        "github_contract": github_contract,
        "markdown_links": markdown_links,
        "errors": errors,
        "passed": not errors,
    }
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
