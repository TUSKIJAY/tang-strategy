#!/usr/bin/env python3
"""Small lifecycle consistency checker for Tang Strategy."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


STATE_DIRS = {
    "proposed": "Proposed",
    "active": "Active",
    "completed": "Completed",
}

PLAN_KEYS = (
    "Lifecycle schema",
    "Status",
    "Plan slug",
    "Revision",
    "Design reviews",
    "Latest design verdict",
    "Review independence",
    "Activation evidence",
    "Current phase",
    "Phase state",
    "Phase entry gate",
    "Next gate",
    "Implementation review",
    "Final disposition",
    "Verified implementation commit",
    "Lifecycle reconciliation commit",
)

REVIEW_KEYS = (
    "Review target",
    "Review target revision",
    "Review type",
    "Reviewer ID",
    "Plan author ID",
    "Independence declaration",
    "Evidence method",
    "Verdict",
    "Confidence",
)

STATE_KEYS = (
    "Current plan",
    "Lifecycle status",
    "Current phase",
    "Phase state",
    "Next gate",
)

VERDICTS = {"approve", "revise", "reject", "accept"}

# PROGRESS.md is the running lifecycle log; HANDOFF.md is only the latest resume
# point (AGENTS.md startup contract, docs/operating-modes.md section 6). History
# reaches HANDOFF.md by pasting a dated bullet out of PROGRESS.md, so that shape
# is the one this checker can reject deterministically. It is a shape rule, not a
# semantic one: undated history prose still passes, and the structural guard is
# that HANDOFF.md holds no history section at all.
HANDOFF_LOG_ENTRY = re.compile(r"^- \d{4}-\d{2}-\d{2}: ")


@dataclass(frozen=True)
class Plan:
    path: Path
    state_dir: str
    metadata: dict[str, str]

    @property
    def slug(self) -> str:
        return self.metadata.get("Plan slug", "")


def clean_value(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == "`":
        return value[1:-1].strip()
    return value


def metadata(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in text.splitlines():
        if line.startswith("## "):
            break
        match = re.match(r"^- ([A-Za-z][A-Za-z ]+):\s*(.*?)\s*$", line)
        if match and match.group(1) not in result:
            result[match.group(1)] = clean_value(match.group(2))
    return result


def markdown_targets(text: str) -> list[str]:
    return [match.group(1).strip().strip("<>") for match in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", text)]


def resolve_target(source: Path, target: str, root: Path) -> Path | None:
    raw = target.split("#", 1)[0]
    if not raw or re.match(r"^[a-z]+://", raw):
        return None
    candidate = (source.parent / raw).resolve()
    if candidate == root or root in candidate.parents:
        return candidate
    return None


def discover_plans(root: Path, errors: list[str]) -> dict[str, Plan]:
    plans: dict[str, Plan] = {}
    for state_dir, expected_status in STATE_DIRS.items():
        directory = root / "docs" / "exec-plans" / state_dir
        for path in sorted(directory.glob("*-plan.md")):
            try:
                values = metadata(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError) as exc:
                errors.append(f"plan unreadable: {path.relative_to(root)}: {exc}")
                continue

            missing = [key for key in PLAN_KEYS if not values.get(key)]
            if missing:
                errors.append(f"plan metadata missing: {path.relative_to(root)}: {', '.join(missing)}")

            slug = values.get("Plan slug", "")
            if slug != path.stem:
                errors.append(f"plan slug mismatch: {path.relative_to(root)}: {slug!r}")
            if slug in plans:
                errors.append(
                    f"plan appears in multiple lifecycle directories: {slug}: "
                    f"{plans[slug].path.relative_to(root)}, {path.relative_to(root)}"
                )
            else:
                plans[slug] = Plan(path=path, state_dir=state_dir, metadata=values)

            if values.get("Status") != expected_status:
                errors.append(
                    f"plan status mismatch: {path.relative_to(root)}: "
                    f"expected {expected_status}, got {values.get('Status')!r}"
                )
            check_plan_state(path, state_dir, values, root, errors)
    return plans


def check_plan_state(
    path: Path,
    state_dir: str,
    values: dict[str, str],
    root: Path,
    errors: list[str],
) -> None:
    label = str(path.relative_to(root))
    if state_dir == "proposed":
        if values.get("Activation evidence") != "none":
            errors.append(f"proposed plan has activation evidence: {label}")
        if values.get("Next gate") in {None, "", "none", "closed"}:
            errors.append(f"proposed plan needs a next gate: {label}")
    elif state_dir == "active":
        for key in ("Activation evidence", "Current phase", "Phase state", "Next gate"):
            if values.get(key) in {None, "", "none", "closed"}:
                errors.append(f"active plan has no {key}: {label}")
    else:
        expected = {
            "Current phase": "none",
            "Phase state": "none",
            "Next gate": "closed",
        }
        for key, wanted in expected.items():
            if values.get(key) != wanted:
                errors.append(f"completed plan {key} must be {wanted}: {label}")
        if values.get("Final disposition") in {None, "", "none"}:
            errors.append(f"completed plan needs Final disposition: {label}")
        if values.get("Final disposition") == "Completed":
            check_accepted_implementation_review(path, values, root, errors)


def check_accepted_implementation_review(
    plan_path: Path,
    values: dict[str, str],
    root: Path,
    errors: list[str],
) -> None:
    raw = clean_value(values.get("Implementation review", ""))
    if not raw.endswith("@accept"):
        errors.append(f"completed implementation lacks accepted review: {plan_path.relative_to(root)}")
        return
    target = raw[:-7]
    candidate = (plan_path.parent / target).resolve()
    if not candidate.is_file():
        candidate = (root / target).resolve()
    if not candidate.is_file():
        errors.append(f"implementation review missing: {plan_path.relative_to(root)}: {target}")
        return
    verdict = metadata(candidate.read_text(encoding="utf-8")).get("Verdict")
    if verdict and verdict != "accept":
        errors.append(f"implementation review verdict is not accept: {candidate.relative_to(root)}")


def check_state_indexes(root: Path, plans: dict[str, Plan], errors: list[str]) -> None:
    base = root / "docs" / "exec-plans"
    for state_dir in STATE_DIRS:
        index = base / state_dir / "index.md"
        text = index.read_text(encoding="utf-8")
        linked: list[Path] = []
        for target in markdown_targets(text):
            resolved = resolve_target(index, target, root)
            if resolved and resolved.parent == base / state_dir and resolved.name.endswith("-plan.md"):
                linked.append(resolved)
        expected = sorted(plan.path.resolve() for plan in plans.values() if plan.state_dir == state_dir)
        if sorted(linked) != expected:
            shown = [str(path.relative_to(root)) for path in linked]
            wanted = [str(path.relative_to(root)) for path in expected]
            errors.append(f"{state_dir} index plan links mismatch: found={shown} expected={wanted}")

    roadmap = base / "roadmap.md"
    roadmap_links = [
        resolved
        for target in markdown_targets(roadmap.read_text(encoding="utf-8"))
        if (resolved := resolve_target(roadmap, target, root)) and resolved.name.endswith("-plan.md")
    ]
    for plan in plans.values():
        count = roadmap_links.count(plan.path.resolve())
        if count != 1:
            errors.append(f"roadmap must link plan once: {plan.slug}: found {count}")


def check_reviews(root: Path, plans: dict[str, Plan], errors: list[str]) -> None:
    index = root / "docs" / "exec-plans" / "reviews" / "index.md"
    lines = index.read_text(encoding="utf-8").splitlines()
    for plan in plans.values():
        row = next((line for line in lines if line.startswith("|") and f"/{plan.slug}/" in line), None)
        if row is None:
            errors.append(f"reviews index missing plan row: {plan.slug}")
            continue
        cells = [cell.strip() for cell in row.strip().strip("|").split("|")]
        if len(cells) != 4:
            errors.append(f"reviews index row must have four cells: {plan.slug}")
            continue

        review_dir = index.parent / plan.slug
        expected_files = sorted(path.resolve() for path in review_dir.glob("*.md"))
        linked_files: list[Path] = []
        verdicts: list[str] = []
        for target in markdown_targets(cells[1]):
            resolved = resolve_target(index, target, root)
            if resolved and resolved.parent == review_dir.resolve() and resolved.suffix == ".md":
                linked_files.append(resolved)
                if resolved.is_file():
                    values = metadata(resolved.read_text(encoding="utf-8"))
                    verdict = values.get("Verdict")
                    if verdict:
                        verdicts.append(verdict)
                        check_review_metadata(resolved, plan, values, root, errors)
        if sorted(linked_files) != expected_files:
            errors.append(f"reviews index artifact links mismatch: {plan.slug}")
        if verdicts:
            latest = verdicts[-1]
        elif plan.metadata.get("Implementation review", "").endswith("@accept"):
            latest = "accept"
        else:
            latest = "none"
        if cells[2] != latest:
            errors.append(f"reviews index latest verdict mismatch: {plan.slug}: {cells[2]!r} != {latest!r}")
        if cells[3] != STATE_DIRS[plan.state_dir]:
            errors.append(f"reviews index lifecycle state mismatch: {plan.slug}")


def check_review_metadata(
    path: Path,
    plan: Plan,
    values: dict[str, str],
    root: Path,
    errors: list[str],
) -> None:
    missing = [key for key in REVIEW_KEYS if not values.get(key)]
    if missing:
        errors.append(f"review metadata missing: {path.relative_to(root)}: {', '.join(missing)}")
        return
    if values["Verdict"] not in VERDICTS:
        errors.append(f"review verdict invalid: {path.relative_to(root)}: {values['Verdict']!r}")
    if Path(values["Review target"]).name != plan.path.name:
        errors.append(f"review target filename mismatch: {path.relative_to(root)}")


def current_state(path: Path, root: Path, errors: list[str]) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    start = "<!-- operating-modes-state:start -->"
    end = "<!-- operating-modes-state:end -->"
    if text.count(start) != 1 or text.count(end) != 1:
        errors.append(f"state block markers invalid: {path.relative_to(root)}")
        return {}
    body = text.split(start, 1)[1].split(end, 1)[0]
    values = metadata(body)
    missing = [key for key in STATE_KEYS if not values.get(key)]
    if missing:
        errors.append(f"state block metadata missing: {path.relative_to(root)}: {', '.join(missing)}")
    return {key: values.get(key, "") for key in STATE_KEYS}


def check_current_state(root: Path, plans: dict[str, Plan], errors: list[str]) -> None:
    progress = current_state(root / "PROGRESS.md", root, errors)
    handoff = current_state(root / "HANDOFF.md", root, errors)
    if progress != handoff:
        errors.append("PROGRESS.md and HANDOFF.md current-state blocks differ")
        return
    slug = progress.get("Current plan")
    if slug == "none":
        expected = {
            "Current plan": "none",
            "Lifecycle status": "None",
            "Current phase": "none",
            "Phase state": "none",
            "Next gate": "none",
        }
    elif slug in plans:
        plan = plans[slug]
        expected = {
            "Current plan": slug,
            "Lifecycle status": STATE_DIRS[plan.state_dir],
            "Current phase": plan.metadata.get("Current phase", ""),
            "Phase state": plan.metadata.get("Phase state", ""),
            "Next gate": plan.metadata.get("Next gate", ""),
        }
    else:
        errors.append(f"current-state plan does not exist: {slug!r}")
        return
    if progress != expected:
        errors.append(f"current-state block does not match canonical plan: found={progress} expected={expected}")


def check_handoff_role(root: Path, errors: list[str]) -> None:
    path = root / "HANDOFF.md"
    numbers = [
        number
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1)
        if HANDOFF_LOG_ENTRY.match(line)
    ]
    if numbers:
        located = ", ".join(str(number) for number in numbers)
        errors.append(
            f"HANDOFF.md carries dated log entries at line {located}: "
            "history belongs in PROGRESS.md or docs/progress-archive/, "
            "and a blocker is written as current state, not as a dated entry"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    root = args.root.expanduser().resolve()
    errors: list[str] = []

    plans = discover_plans(root, errors)
    check_state_indexes(root, plans, errors)
    check_reviews(root, plans, errors)
    check_current_state(root, plans, errors)
    check_handoff_role(root, errors)

    payload = {
        "schema_version": "operating-modes-check-simple-v1",
        "root": str(root),
        "plans": [
            {
                "path": str(plan.path.relative_to(root)),
                "slug": plan.slug,
                "status": plan.metadata.get("Status"),
            }
            for plan in sorted(plans.values(), key=lambda item: str(item.path))
        ],
        "errors": errors,
        "passed": not errors,
    }
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
