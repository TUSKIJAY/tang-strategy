#!/usr/bin/env python3
"""Validate Tang Strategy operating-mode and lifecycle evidence without mutation."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


STATE_DIRECTORIES = {
    "proposed": "Proposed",
    "active": "Active",
    "completed": "Completed",
}

PLAN_KEYS = (
    "Lifecycle schema",
    "Status",
    "Plan slug",
    "Revision",
    "Plan author ID",
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

STATE_BLOCK_KEYS = (
    "Current plan",
    "Lifecycle status",
    "Current phase",
    "Phase state",
    "Next gate",
)

REQUIRED_PATHS = (
    "AGENTS.md",
    "INSTRUCTIONS.md",
    "PROGRESS.md",
    "HANDOFF.md",
    ".harness/config.json",
    ".github/workflows/project-harness.yml",
    "docs/README.md",
    "docs/operating-modes.md",
    "docs/decisions/2026-07-19-operating-modes-and-lifecycle-source.md",
    "docs/exec-plans/plan-template.md",
    "docs/exec-plans/proposed/index.md",
    "docs/exec-plans/active/index.md",
    "docs/exec-plans/completed/index.md",
    "docs/exec-plans/reviews/index.md",
    "docs/exec-plans/reviews/review-template.md",
    "docs/exec-plans/roadmap.md",
    "scripts/check-project-harness.py",
    "scripts/check-operating-modes.py",
)

COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
GATE_RE = re.compile(r"^[A-Za-z0-9._:@/-]+$")
ACTIVATION_RE = re.compile(r"^user-instruction:[A-Za-z0-9][A-Za-z0-9._:@/-]*$")
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
LINK_RE = re.compile(r"\[([^]]+)\]\(([^)]+)\)")
LEGACY_GIT_KEY_RE = re.compile(
    r"^- (Branch/HEAD|Current HEAD|Git state|Current worktree|Worktree status):"
)


@dataclass(frozen=True)
class Plan:
    path: Path
    directory_state: str
    metadata: dict[str, str]

    @property
    def slug(self) -> str:
        return clean_value(self.metadata.get("Plan slug", ""))

    @property
    def status(self) -> str:
        return clean_value(self.metadata.get("Status", ""))

    @property
    def revision(self) -> str:
        return clean_value(self.metadata.get("Revision", ""))

    @property
    def schema(self) -> str:
        return clean_value(self.metadata.get("Lifecycle schema", ""))


def clean_value(value: str) -> str:
    result = value.strip()
    if len(result) >= 2 and result.startswith("`") and result.endswith("`"):
        result = result[1:-1].strip()
    return result


def read_text(path: Path, label: str, errors: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        errors.append(f"{label}: cannot read {path}: {exc}")
        return ""


def parse_header_bullets(
    text: str,
    *,
    duplicate_errors: list[str] | None = None,
    label: str = "metadata",
) -> dict[str, str]:
    metadata: dict[str, str] = {}
    for line in text.splitlines():
        if line.startswith("## "):
            break
        match = re.fullmatch(r"- ([A-Za-z][A-Za-z0-9 /-]*):\s*(.*?)\s*", line)
        if match:
            key = match.group(1)
            if key in metadata and duplicate_errors is not None:
                duplicate_errors.append(f"{label} duplicate constrained key: {key}")
            metadata[key] = match.group(2)
    return metadata


def is_proposed_next_gate(value: str) -> bool:
    return bool(
        re.fullmatch(
            r"(?:design-review(?:[._:@/-].*)?|review(?:[._:@/-].*)?|revision(?:[._:@/-].*)?|"
            r"plan-revision(?:[._:@/-].*)?|activation-recording(?:[._:@/-].*)?)",
            value,
        )
    )


def resolve_inside(root: Path, base: Path, raw: str, label: str, errors: list[str]) -> Path | None:
    value = clean_value(raw)
    candidate = (root / value).resolve() if value.startswith("docs/") else (base / value).resolve()
    if candidate != root and root not in candidate.parents:
        errors.append(f"{label}: path escapes repository root: {value}")
        return None
    return candidate


def discover_plans(root: Path, errors: list[str]) -> list[Plan]:
    plans: list[Plan] = []
    seen_slugs: dict[str, Path] = {}
    for directory, expected_status in STATE_DIRECTORIES.items():
        plan_dir = root / "docs" / "exec-plans" / directory
        if not plan_dir.is_dir():
            errors.append(f"plans: missing lifecycle directory: docs/exec-plans/{directory}")
            continue
        for path in sorted(plan_dir.glob("*.md")):
            if path.name == "index.md":
                continue
            text = read_text(path, "plans", errors)
            metadata = parse_header_bullets(
                text,
                duplicate_errors=errors,
                label=f"plan metadata: {path.relative_to(root)}",
            )
            plan = Plan(path=path, directory_state=directory, metadata=metadata)
            plans.append(plan)
            missing = [key for key in PLAN_KEYS if key not in metadata]
            if missing:
                errors.append(
                    f"plan metadata: {path.relative_to(root)} missing required keys: {', '.join(missing)}"
                )
            if plan.status and plan.status != expected_status:
                errors.append(
                    f"plan status: {path.relative_to(root)} is in {directory}/ but Status={plan.status!r}; "
                    f"expected {expected_status!r}"
                )
            if plan.slug:
                previous = seen_slugs.get(plan.slug)
                if previous is not None:
                    errors.append(
                        f"plan slug: duplicate {plan.slug!r} in {previous.relative_to(root)} and "
                        f"{path.relative_to(root)}"
                    )
                else:
                    seen_slugs[plan.slug] = path
                if path.stem != plan.slug:
                    errors.append(
                        f"plan slug: {path.relative_to(root)} Plan slug={plan.slug!r} does not match filename"
                    )
            validate_plan_metadata(plan, root, errors)
    return plans


def validate_plan_metadata(plan: Plan, root: Path, errors: list[str]) -> None:
    meta = {key: clean_value(value) for key, value in plan.metadata.items()}
    relative = plan.path.relative_to(root)
    if plan.schema not in {"operating-modes-v1", "operating-modes-legacy-v1"}:
        errors.append(f"plan schema: {relative} unsupported Lifecycle schema={plan.schema!r}")
    if plan.schema == "operating-modes-legacy-v1" and plan.directory_state != "completed":
        errors.append(f"plan schema: {relative} legacy schema is allowed only in completed/")
    if plan.slug and not SLUG_RE.fullmatch(plan.slug):
        errors.append(f"plan slug: {relative} invalid slug={plan.slug!r}")
    if not plan.revision or plan.revision == "none":
        errors.append(f"plan metadata: {relative} Revision must be non-empty")
    author = meta.get("Plan author ID", "")
    if not author or author == "none":
        errors.append(f"plan metadata: {relative} Plan author ID must be non-empty")

    latest = meta.get("Latest design verdict", "")
    if latest not in {"none", "approve", "revise", "reject"}:
        errors.append(f"plan metadata: {relative} invalid Latest design verdict={latest!r}")
    independence = meta.get("Review independence", "")
    if independence not in {"none", "legacy-unattested", "attested"}:
        errors.append(f"plan metadata: {relative} invalid Review independence={independence!r}")
    phase = meta.get("Current phase", "")
    if phase != "none" and not re.fullmatch(r"phase-[0-6]", phase):
        errors.append(f"plan metadata: {relative} invalid Current phase={phase!r}")
    phase_state = meta.get("Phase state", "")
    if phase_state not in {"none", "not-started", "in-progress", "blocked", "complete"}:
        errors.append(f"plan metadata: {relative} invalid Phase state={phase_state!r}")
    for key in ("Phase entry gate", "Next gate"):
        gate = meta.get(key, "")
        if not gate or (gate != "none" and not GATE_RE.fullmatch(gate)):
            errors.append(f"plan metadata: {relative} invalid {key}={gate!r}")
    disposition = meta.get("Final disposition", "")
    if disposition not in {"none", "Completed", "Terminated", "Rejected", "Superseded", "Archived"}:
        errors.append(f"plan metadata: {relative} invalid Final disposition={disposition!r}")
    for key in ("Verified implementation commit", "Lifecycle reconciliation commit"):
        value = meta.get(key, "")
        if value != "none" and not COMMIT_RE.fullmatch(value):
            errors.append(f"plan metadata: {relative} invalid {key}={value!r}")

    reviews = parse_design_reviews(meta.get("Design reviews", ""), relative, errors)
    if reviews and latest != reviews[-1][1]:
        errors.append(
            f"plan reviews: {relative} Latest design verdict={latest!r} does not match final declared "
            f"review verdict={reviews[-1][1]!r}"
        )
    if not reviews and meta.get("Design reviews") != "none":
        errors.append(f"plan reviews: {relative} Design reviews must be none or constrained review entries")
    if not reviews and meta.get("Design reviews") == "none":
        if latest != "none" or independence != "none":
            errors.append(
                f"plan reviews: {relative} Design reviews=none requires Latest design verdict=none "
                "and Review independence=none"
            )
    elif plan.schema == "operating-modes-v1" and independence != "attested":
        errors.append(
            f"plan reviews: {relative} new-schema plans with design reviews require "
            "Review independence=attested"
        )

    review_results: list[tuple[str, str, str, Path | None, bool]] = []
    for raw_path, verdict, target_revision in reviews:
        review_path = resolve_inside(root, plan.path.parent, raw_path, "plan review", errors)
        structured = False
        if review_path is None or not review_path.is_file():
            errors.append(f"plan review: {relative} referenced review does not exist: {raw_path}")
        else:
            structured = validate_review(
                root,
                plan,
                review_path,
                verdict,
                target_revision,
                errors,
                expected_type="design",
                allow_legacy=(plan.schema == "operating-modes-legacy-v1" or target_revision != plan.revision),
            )
        review_results.append((verdict, target_revision, raw_path, review_path, structured))

    activation = meta.get("Activation evidence", "")
    if activation != "none" and not ACTIVATION_RE.fullmatch(activation):
        errors.append(
            f"plan metadata: {relative} Activation evidence must be none or a non-empty "
            "user-instruction reference"
        )
    implementation = meta.get("Implementation review", "")
    if plan.directory_state == "proposed":
        if activation != "none" or phase != "none" or phase_state != "none" or meta.get("Phase entry gate") != "none":
            errors.append(f"plan state: {relative} Proposed plan must not have activation or current phase state")
        if disposition != "none" or implementation != "none":
            errors.append(f"plan state: {relative} Proposed plan must not have disposition or implementation review")
        next_gate = meta.get("Next gate", "")
        if not is_proposed_next_gate(next_gate):
            errors.append(
                f"plan state: {relative} Proposed Next gate={next_gate!r} must be a review, revision, "
                "or activation-recording gate"
            )
    elif plan.directory_state == "active":
        matching_approve = [item for item in review_results if item[0] == "approve" and item[1] == plan.revision]
        if not matching_approve:
            errors.append(f"plan state: {relative} Active plan lacks matching-revision approve review")
        elif not any(item[4] for item in matching_approve):
            errors.append(f"plan state: {relative} matching approve review lacks constrained reviewer evidence")
        if latest != "approve":
            errors.append(f"plan state: {relative} Active plan Latest design verdict must be approve")
        if independence != "attested":
            errors.append(f"plan state: {relative} Active plan Review independence must be attested")
        if not ACTIVATION_RE.fullmatch(activation):
            errors.append(f"plan state: {relative} Active plan lacks user-instruction activation evidence")
        if phase == "none" or phase_state == "none" or meta.get("Phase entry gate") == "none":
            errors.append(f"plan state: {relative} Active plan lacks phase, phase state, or phase entry gate")
        if meta.get("Next gate") == "none":
            errors.append(f"plan state: {relative} Active plan Next gate must be non-none")
        if disposition != "none" or implementation != "none":
            errors.append(f"plan state: {relative} Active plan must not have final disposition or implementation review")
    elif plan.directory_state == "completed":
        if disposition == "none":
            errors.append(f"plan state: {relative} Completed plan lacks final disposition")
        implemented = (
            disposition == "Completed"
            or meta.get("Verified implementation commit") != "none"
            or implementation != "none"
        )
        if implemented:
            validate_implementation_review(root, plan, implementation, errors)


def parse_design_reviews(value: str, relative: Path, errors: list[str]) -> list[tuple[str, str, str]]:
    cleaned = clean_value(value)
    if cleaned == "none" or not cleaned:
        return []
    results: list[tuple[str, str, str]] = []
    for raw_item in cleaned.split(","):
        item = clean_value(raw_item)
        parts = item.rsplit("@", 2)
        if len(parts) != 3 or parts[1] not in {"approve", "revise", "reject"} or not all(parts):
            errors.append(f"plan reviews: {relative} invalid Design reviews entry={item!r}")
            continue
        results.append((parts[0], parts[1], parts[2]))
    return results


def validate_review(
    root: Path,
    plan: Plan,
    path: Path,
    declared_verdict: str,
    target_revision: str,
    errors: list[str],
    *,
    expected_type: str,
    allow_legacy: bool,
) -> bool:
    text = read_text(path, "review", errors)
    relative = path.relative_to(root)
    metadata = {
        key: clean_value(value)
        for key, value in parse_header_bullets(
            text,
            duplicate_errors=errors,
            label=f"review metadata: {relative}",
        ).items()
    }
    expected_directory = (root / "docs" / "exec-plans" / "reviews" / plan.slug).resolve()
    if path.parent.resolve() != expected_directory or path.suffix != ".md":
        errors.append(
            f"review path: {relative} must be a direct Markdown artifact under "
            f"docs/exec-plans/reviews/{plan.slug}/"
        )
    present = [key for key in REVIEW_KEYS if key in metadata]
    if not present:
        if not allow_legacy:
            errors.append(f"review metadata: {relative} lacks constrained reviewer fields")
        return False
    missing = [key for key in REVIEW_KEYS if key not in metadata]
    if missing:
        if not allow_legacy:
            errors.append(f"review metadata: {relative} missing required keys: {', '.join(missing)}")
        return False
    if metadata["Review target revision"] != target_revision:
        errors.append(
            f"review revision: {relative} target={metadata['Review target revision']!r} "
            f"declared={target_revision!r}"
        )
    target = metadata["Review target"]
    expected_target = re.compile(
        rf"docs/exec-plans/(?:proposed|active|completed)/{re.escape(plan.path.name)}"
    )
    if not expected_target.fullmatch(target):
        errors.append(
            f"review target: {relative} targets {target!r}; expected an exact canonical lifecycle path "
            f"for {plan.path.name!r}"
        )
    if metadata["Verdict"] != declared_verdict:
        errors.append(
            f"review verdict: {relative} Verdict={metadata['Verdict']!r} declared={declared_verdict!r}"
        )
    if metadata["Review type"] != expected_type:
        errors.append(
            f"review metadata: {relative} Review type={metadata['Review type']!r}; "
            f"expected {expected_type!r} for this evidence"
        )
    if metadata["Verdict"] not in {"approve", "revise", "reject", "accept"}:
        errors.append(f"review metadata: {relative} invalid Verdict={metadata['Verdict']!r}")
    if metadata["Confidence"] not in {"low", "medium", "high"}:
        errors.append(f"review metadata: {relative} invalid Confidence={metadata['Confidence']!r}")
    if metadata["Independence declaration"] != "attested":
        errors.append(f"review metadata: {relative} Independence declaration must be attested")
    if not metadata["Reviewer ID"] or not metadata["Plan author ID"] or not metadata["Evidence method"]:
        errors.append(f"review metadata: {relative} reviewer, author, and evidence fields must be non-empty")
    if metadata["Reviewer ID"] == metadata["Plan author ID"]:
        errors.append(f"review independence: {relative} Reviewer ID must differ from Plan author ID")
    plan_author = clean_value(plan.metadata.get("Plan author ID", ""))
    if metadata["Plan author ID"] != plan_author:
        errors.append(
            f"review author: {relative} Plan author ID={metadata['Plan author ID']!r} "
            f"does not match plan={plan_author!r}"
        )
    return not missing


def validate_implementation_review(root: Path, plan: Plan, value: str, errors: list[str]) -> None:
    relative = plan.path.relative_to(root)
    cleaned = clean_value(value)
    if cleaned == "none" or not cleaned.endswith("@accept"):
        errors.append(f"implementation review: {relative} implemented Completed plan requires <path>@accept")
        return
    raw_path = cleaned[:-7]
    review_path = resolve_inside(root, plan.path.parent, raw_path, "implementation review", errors)
    if review_path is None or not review_path.is_file():
        errors.append(f"implementation review: {relative} referenced review does not exist: {raw_path}")
        return
    if plan.schema == "operating-modes-legacy-v1":
        text = read_text(review_path, "implementation review", errors)
        if not re.search(r"(?:Verdict|\*\*裁决\*\*)\s*:\s*accept\b", text, flags=re.IGNORECASE):
            errors.append(f"implementation review: {review_path.relative_to(root)} lacks accept evidence")
        return
    validate_review(
        root,
        plan,
        review_path,
        "accept",
        plan.revision,
        errors,
        expected_type="implementation",
        allow_legacy=False,
    )


def parse_table_rows(path: Path, root: Path, errors: list[str]) -> list[tuple[list[str], str, str]]:
    text = read_text(path, "index", errors)
    rows: list[tuple[list[str], str, str]] = []
    sentinel_count = 0
    state_sentinel = ["None", "—", "—", "none"]
    reviews_sentinel = ["None", "—", "none", "None"]
    expected_sentinel = reviews_sentinel if path.parent.name == "reviews" else state_sentinel
    for line in text.splitlines():
        raw = line.strip()
        if not raw.startswith("|") or re.fullmatch(r"\|[\s|:-]+\|?", raw):
            continue
        body = raw[1:-1] if raw.endswith("|") else raw[1:]
        cells = [cell.strip() for cell in body.split("|")]
        if not cells or cells[0] in {"Plan", "Decision"}:
            continue
        links = list(LINK_RE.finditer(cells[0]))
        if links:
            if len(cells) != 4:
                errors.append(
                    f"index: {path.relative_to(root)} fixed row must contain exactly four cells: {line}"
                )
            if len(links) != 1 or links[0].span() != (0, len(cells[0])):
                errors.append(
                    f"index: {path.relative_to(root)} Plan cell must be exactly one standalone link: {cells[0]}"
                )
            match = links[0]
            rows.append((cells, match.group(2).strip().strip("<>"), line))
        elif cells == expected_sentinel:
            sentinel_count += 1
        else:
            errors.append(
                f"index: {path.relative_to(root)} data row must use a canonical Plan link or "
                f"exact None sentinel: {line}"
            )
    if sentinel_count > 1:
        errors.append(f"index: {path.relative_to(root)} contains duplicate None sentinel rows")
    if sentinel_count and rows:
        errors.append(f"index: {path.relative_to(root)} cannot mix a None sentinel with plan rows")
    return rows


def review_artifact_verdict(path: Path, root: Path, errors: list[str]) -> str:
    relative = path.relative_to(root)
    text = read_text(path, "reviews index", errors)
    metadata = {
        key: clean_value(value)
        for key, value in parse_header_bullets(
            text,
            duplicate_errors=errors,
            label=f"review metadata: {relative}",
        ).items()
    }
    verdict = metadata.get("Verdict", "")
    if not verdict:
        match = re.search(
            r"(?:Verdict|\*\*裁决\*\*)\s*:\s*(approve|revise|reject|accept)\b",
            text,
            flags=re.IGNORECASE,
        )
        verdict = match.group(1).lower() if match else ""
    if verdict not in {"approve", "revise", "reject", "accept"}:
        errors.append(f"reviews index: {relative} lacks a valid verdict")
    return verdict


def check_reviews_index(
    root: Path,
    plans: list[Plan],
    errors: list[str],
) -> dict[str, tuple[Path, str]]:
    review_index = root / "docs" / "exec-plans" / "reviews" / "index.md"
    review_rows = parse_table_rows(review_index, root, errors)
    row_slugs: list[str] = []
    latest_by_slug: dict[str, tuple[Path, str]] = {}
    plans_by_slug = {plan.slug: plan for plan in plans if plan.slug}
    plans_by_path = {plan.path.resolve(): plan for plan in plans}
    for cells, target, _line in review_rows:
        resolved = resolve_inside(root, review_index.parent, target, "reviews index", errors)
        if resolved is None:
            continue
        plan = plans_by_path.get(resolved)
        slug = plan.slug if plan is not None else (resolved.stem if resolved.suffix == ".md" else resolved.name)
        row_slugs.append(slug)
        plan = plan or plans_by_slug.get(slug)
        if plan is None:
            errors.append(f"reviews index: ghost plan/review row: {target}")
            continue
        if len(cells) < 4 or clean_value(cells[3]) != plan.status:
            errors.append(
                f"reviews index: {slug} lifecycle state={clean_value(cells[3]) if len(cells) > 3 else ''!r}; "
                f"expected {plan.status!r}"
            )

        listed: list[Path] = []
        if len(cells) >= 2:
            for match in LINK_RE.finditer(cells[1]):
                artifact = resolve_inside(
                    root,
                    review_index.parent,
                    match.group(2).strip().strip("<>"),
                    "reviews index artifact",
                    errors,
                )
                if artifact is not None:
                    listed.append(artifact)
        expected_directory = (root / "docs" / "exec-plans" / "reviews" / slug).resolve()
        for artifact in listed:
            if artifact.parent.resolve() != expected_directory or artifact.suffix != ".md":
                errors.append(
                    f"reviews index: {slug} artifact must be a direct Markdown file in its review directory: "
                    f"{artifact.relative_to(root) if artifact.is_relative_to(root) else artifact}"
                )
            elif not artifact.is_file():
                errors.append(f"reviews index: {slug} listed artifact does not exist: {artifact.relative_to(root)}")
        if len(listed) != len(set(listed)):
            errors.append(f"reviews index: {slug} contains duplicate review artifacts")
        expected_artifacts = (
            {path.resolve() for path in expected_directory.glob("*.md") if path.name != "index.md"}
            if expected_directory.is_dir()
            else set()
        )
        listed_set = set(listed)
        missing = sorted(str(path.relative_to(root)) for path in expected_artifacts - listed_set)
        extra = sorted(
            str(path.relative_to(root)) if path.is_relative_to(root) else str(path)
            for path in listed_set - expected_artifacts
        )
        if missing or extra:
            errors.append(
                f"reviews index: {slug} artifact set mismatch; missing={missing} extra={extra}"
            )
        if listed:
            if resolved != expected_directory or not resolved.is_dir():
                errors.append(
                    f"reviews index: {slug} row with artifacts must target its canonical review directory: "
                    f"docs/exec-plans/reviews/{slug}/"
                )
            latest_path = listed[-1]
            latest_verdict = review_artifact_verdict(latest_path, root, errors) if latest_path.is_file() else ""
            declared_latest = clean_value(cells[2]) if len(cells) > 2 else ""
            if declared_latest != latest_verdict:
                errors.append(
                    f"reviews index: {slug} latest verdict={declared_latest!r}; "
                    f"expected {latest_verdict!r} from {latest_path.name}"
                )
            latest_by_slug[slug] = (latest_path, latest_verdict)
        else:
            if resolved != plan.path.resolve():
                errors.append(
                    f"reviews index: {slug} row without artifacts must target the canonical plan path"
                )
            declared_artifacts = clean_value(cells[1]) if len(cells) > 1 else ""
            declared_latest = clean_value(cells[2]) if len(cells) > 2 else ""
            if declared_artifacts != "none" or declared_latest != "none":
                errors.append(
                    f"reviews index: {slug} empty artifact set requires Reviews=none and Latest verdict=none"
                )

    expected_review_slugs = {plan.slug for plan in plans if plan.slug}
    if len(row_slugs) != len(set(row_slugs)):
        errors.append("reviews index: duplicate plan rows")
    missing_reviews = sorted(expected_review_slugs - set(row_slugs))
    ghost_reviews = sorted(set(row_slugs) - expected_review_slugs)
    if missing_reviews:
        errors.append(f"reviews index: missing plan rows: {', '.join(missing_reviews)}")
    if ghost_reviews:
        errors.append(f"reviews index: ghost plan rows: {', '.join(ghost_reviews)}")
    return latest_by_slug


def state_index_evidence(
    root: Path,
    index: Path,
    cell: str,
    label: str,
    errors: list[str],
) -> Path | None:
    links = list(LINK_RE.finditer(cell))
    if len(links) != 1:
        errors.append(f"state index: {label} must contain exactly one evidence link")
        return None
    return resolve_inside(
        root,
        index.parent,
        links[0].group(2).strip().strip("<>"),
        "state index evidence",
        errors,
    )


def check_indexes(root: Path, plans: list[Plan], errors: list[str]) -> None:
    by_path = {plan.path.resolve(): plan for plan in plans}
    latest_reviews = check_reviews_index(root, plans, errors)
    for directory, expected_status in STATE_DIRECTORIES.items():
        index = root / "docs" / "exec-plans" / directory / "index.md"
        rows = parse_table_rows(index, root, errors)
        actual_paths: list[Path] = []
        for cells, target, _line in rows:
            resolved = resolve_inside(root, index.parent, target, "state index", errors)
            if resolved is None:
                continue
            actual_paths.append(resolved)
            plan = by_path.get(resolved)
            if plan is None:
                errors.append(f"state index: {index.relative_to(root)} has ghost plan link: {target}")
                continue
            if directory == "proposed":
                if len(cells) < 4 or clean_value(cells[1]) != "Proposed":
                    errors.append(f"state index: {index.relative_to(root)} row for {plan.slug} must use Proposed")
                if len(cells) >= 4 and clean_value(cells[3]) != clean_value(plan.metadata.get("Next gate", "")):
                    errors.append(f"state index: {index.relative_to(root)} row for {plan.slug} next gate mismatch")
                reviews = parse_design_reviews(plan.metadata.get("Design reviews", ""), plan.path.relative_to(root), errors)
                if reviews:
                    evidence = (
                        state_index_evidence(root, index, cells[2], plan.slug, errors)
                        if len(cells) >= 3
                        else None
                    )
                    expected_evidence = resolve_inside(
                        root,
                        plan.path.parent,
                        reviews[-1][0],
                        "state index evidence",
                        errors,
                    )
                    if expected_evidence is not None and evidence != expected_evidence:
                        errors.append(f"state index: {index.relative_to(root)} row for {plan.slug} review evidence mismatch")
                    if not cells[2].strip().endswith(f": {reviews[-1][1]}"):
                        errors.append(
                            f"state index: {index.relative_to(root)} row for {plan.slug} review verdict mismatch"
                        )
                elif len(cells) < 3 or clean_value(cells[2]) != "none" or LINK_RE.search(cells[2]):
                    errors.append(
                        f"state index: {index.relative_to(root)} row for {plan.slug} without design reviews "
                        "must use evidence none"
                    )
            if directory == "active":
                expected = f"{clean_value(plan.metadata.get('Current phase', ''))}:{clean_value(plan.metadata.get('Phase state', ''))}"
                if len(cells) < 4 or clean_value(cells[1]) != expected:
                    errors.append(
                        f"state index: {index.relative_to(root)} row for {plan.slug} phase={clean_value(cells[1]) if len(cells) > 1 else ''!r}; "
                        f"expected {expected!r}"
                    )
                if len(cells) >= 4 and clean_value(cells[3]) != clean_value(plan.metadata.get("Next gate", "")):
                    errors.append(f"state index: {index.relative_to(root)} row for {plan.slug} next gate mismatch")
                latest = latest_reviews.get(plan.slug)
                evidence = (
                    state_index_evidence(root, index, cells[2], plan.slug, errors)
                    if len(cells) >= 3
                    else None
                )
                if latest is None:
                    errors.append(f"state index: {index.relative_to(root)} row for {plan.slug} lacks latest review evidence")
                elif evidence != latest[0]:
                    errors.append(f"state index: {index.relative_to(root)} row for {plan.slug} latest evidence mismatch")
            if directory == "completed":
                disposition = clean_value(plan.metadata.get("Final disposition", ""))
                commit = clean_value(plan.metadata.get("Verified implementation commit", ""))
                if len(cells) < 4 or clean_value(cells[1]) != disposition or clean_value(cells[3]) != commit:
                    errors.append(f"state index: {index.relative_to(root)} row for {plan.slug} disposition/commit mismatch")
                implementation = clean_value(plan.metadata.get("Implementation review", ""))
                expected_evidence = None
                if implementation.endswith("@accept"):
                    expected_evidence = resolve_inside(
                        root,
                        plan.path.parent,
                        implementation[:-7],
                        "state index evidence",
                        errors,
                    )
                if expected_evidence is not None:
                    evidence = (
                        state_index_evidence(root, index, cells[2], plan.slug, errors)
                        if len(cells) >= 3
                        else None
                    )
                    if evidence != expected_evidence:
                        errors.append(
                            f"state index: {index.relative_to(root)} row for {plan.slug} implementation evidence mismatch"
                        )
                elif len(cells) < 3 or clean_value(cells[2]) != "none" or LINK_RE.search(cells[2]):
                    errors.append(
                        f"state index: {index.relative_to(root)} row for {plan.slug} without an implementation "
                        "review must use verification none"
                    )
        expected_paths = {plan.path.resolve() for plan in plans if plan.directory_state == directory}
        actual_set = set(actual_paths)
        if len(actual_paths) != len(actual_set):
            errors.append(f"state index: {index.relative_to(root)} contains duplicate plan rows")
        missing = sorted(str(path.relative_to(root)) for path in expected_paths - actual_set)
        ghost = sorted(str(path.relative_to(root)) for path in actual_set - expected_paths if path in by_path)
        if missing:
            errors.append(f"state index: {index.relative_to(root)} missing plan rows: {', '.join(missing)}")
        if ghost:
            errors.append(f"state index: {index.relative_to(root)} has wrong-state plan rows: {', '.join(ghost)}")


def check_roadmap(root: Path, plans: list[Plan], errors: list[str]) -> None:
    path = root / "docs" / "exec-plans" / "roadmap.md"
    text = read_text(path, "roadmap", errors)
    section: str | None = None
    actual: dict[str, set[Path]] = {key: set() for key in STATE_DIRECTORIES}
    heading_states = {"Proposed Plans": "proposed", "Active Plans": "active", "Completed Plans": "completed"}
    pattern = re.compile(
        r"^- \[[^]]+\]\((\./(proposed|active|completed)/[^)]+\.md)\) — "
        r"(Proposed|Active|Completed); canonical details: \[[^]]+\]\(\./(proposed|active|completed)/index\.md\)$"
    )
    for line in text.splitlines():
        if line.startswith("## "):
            section = heading_states.get(line[3:].strip())
            continue
        if section is None or not line.startswith("- ["):
            continue
        match = pattern.fullmatch(line)
        if not match:
            errors.append(f"roadmap: invalid constrained row in {section}: {line}")
            continue
        target, target_state, status, index_state = match.groups()
        expected_status = STATE_DIRECTORIES[section]
        if target_state != section or index_state != section or status != expected_status:
            errors.append(f"roadmap: row state mismatch in {section}: {line}")
            continue
        resolved = resolve_inside(root, path.parent, target, "roadmap", errors)
        if resolved is not None:
            actual[section].add(resolved)
    for state in STATE_DIRECTORIES:
        expected = {plan.path.resolve() for plan in plans if plan.directory_state == state}
        missing = sorted(str(item.relative_to(root)) for item in expected - actual[state])
        ghost = sorted(str(item.relative_to(root)) for item in actual[state] - expected)
        if missing:
            errors.append(f"roadmap: {state} section missing plan rows: {', '.join(missing)}")
        if ghost:
            errors.append(f"roadmap: {state} section has ghost plan rows: {', '.join(ghost)}")


def extract_state_block(path: Path, root: Path, errors: list[str]) -> dict[str, str]:
    text = read_text(path, "state block", errors)
    start = "<!-- operating-modes-state:start -->"
    end = "<!-- operating-modes-state:end -->"
    if text.count(start) != 1 or text.count(end) != 1:
        errors.append(f"state block: {path.relative_to(root)} must contain exactly one start/end marker pair")
        return {}
    body = text.split(start, 1)[1].split(end, 1)[0]
    values = {
        key: clean_value(value)
        for key, value in parse_header_bullets(
            body,
            duplicate_errors=errors,
            label=f"state block: {path.relative_to(root)}",
        ).items()
    }
    missing = [key for key in STATE_BLOCK_KEYS if key not in values]
    extra = sorted(set(values) - set(STATE_BLOCK_KEYS))
    if missing or extra:
        errors.append(
            f"state block: {path.relative_to(root)} keys mismatch; missing={missing} extra={extra}"
        )
    return {key: values.get(key, "") for key in STATE_BLOCK_KEYS}


def check_current_state(root: Path, plans: list[Plan], errors: list[str]) -> None:
    progress = extract_state_block(root / "PROGRESS.md", root, errors)
    handoff = extract_state_block(root / "HANDOFF.md", root, errors)
    if progress != handoff:
        errors.append("state block: PROGRESS.md and HANDOFF.md do not match")
    if not progress:
        return
    current_slug = progress["Current plan"]
    if current_slug == "none":
        if progress != {
            "Current plan": "none",
            "Lifecycle status": "None",
            "Current phase": "none",
            "Phase state": "none",
            "Next gate": "none",
        }:
            errors.append("state block: Current plan none requires the canonical None/none values")
        return
    matches = [plan for plan in plans if plan.slug == current_slug]
    if len(matches) != 1:
        errors.append(f"state block: Current plan={current_slug!r} does not resolve to exactly one plan")
        return
    plan = matches[0]
    expected = {
        "Current plan": plan.slug,
        "Lifecycle status": plan.status,
        "Current phase": clean_value(plan.metadata.get("Current phase", "")),
        "Phase state": clean_value(plan.metadata.get("Phase state", "")),
        "Next gate": clean_value(plan.metadata.get("Next gate", "")),
    }
    if progress != expected:
        errors.append(f"state block: current values do not match canonical plan metadata; expected={expected}")


def check_legacy_git_keys(path: Path, root: Path, errors: list[str]) -> None:
    text = read_text(path, "git evidence", errors)
    historical = False
    for number, line in enumerate(text.splitlines(), 1):
        if line == "<!-- git-evidence:historical:start -->":
            if historical:
                errors.append(f"git evidence: {path.relative_to(root)}:{number} nested historical marker")
            historical = True
            continue
        if line == "<!-- git-evidence:historical:end -->":
            if not historical:
                errors.append(f"git evidence: {path.relative_to(root)}:{number} unmatched historical end marker")
            historical = False
            continue
        if not historical and LEGACY_GIT_KEY_RE.match(line):
            errors.append(
                f"git evidence: {path.relative_to(root)}:{number} forbidden live-Git key outside historical block"
            )
    if historical:
        errors.append(f"git evidence: {path.relative_to(root)} has unclosed historical marker")


def check_required_contract(root: Path, errors: list[str]) -> list[dict[str, Any]]:
    files: list[dict[str, Any]] = []
    for relative in REQUIRED_PATHS:
        present = (root / relative).is_file()
        files.append({"path": relative, "present": present})
        if not present:
            errors.append(f"contract path: missing required file: {relative}")
    routes = {
        "AGENTS.md": "docs/operating-modes.md",
        "INSTRUCTIONS.md": "docs/operating-modes.md",
        "docs/README.md": "operating-modes.md",
        "docs/operating-modes.md": "operating-modes-v1",
    }
    for relative, token in routes.items():
        path = root / relative
        if path.is_file() and token not in read_text(path, "contract route", errors):
            errors.append(f"contract route: {relative} does not route/declare {token}")
    plan_template = root / "docs" / "exec-plans" / "plan-template.md"
    if plan_template.is_file():
        metadata = parse_header_bullets(
            read_text(plan_template, "plan template", errors),
            duplicate_errors=errors,
            label="plan template",
        )
        missing = [key for key in PLAN_KEYS if key not in metadata]
        if missing:
            errors.append(f"plan template: missing constrained keys: {', '.join(missing)}")
    review_template = root / "docs" / "exec-plans" / "reviews" / "review-template.md"
    if review_template.is_file():
        metadata = parse_header_bullets(
            read_text(review_template, "review template", errors),
            duplicate_errors=errors,
            label="review template",
        )
        missing = [key for key in REVIEW_KEYS if key not in metadata]
        if missing:
            errors.append(f"review template: missing constrained keys: {', '.join(missing)}")
    canonical_command = "python3 scripts/check-project-harness.py --root . --profile governed"
    fixture_command = "python3 -m unittest scripts.tests.test_operating_modes"
    config_path = root / ".harness" / "config.json"
    if config_path.is_file():
        try:
            config = json.loads(read_text(config_path, "verification config", errors))
        except json.JSONDecodeError as exc:
            errors.append(f"verification config: invalid JSON: {exc}")
        else:
            commands = config.get("verification_commands") if isinstance(config, dict) else None
            if not isinstance(commands, list):
                errors.append("verification config: verification_commands must be a list")
            else:
                for command in (canonical_command, fixture_command):
                    if command not in commands:
                        errors.append(f"verification config: missing required command: {command}")
                if canonical_command in commands and fixture_command in commands:
                    if commands.index(canonical_command) > commands.index(fixture_command):
                        errors.append("verification config: canonical harness command must precede fixture tests")
    workflow_path = root / ".github" / "workflows" / "project-harness.yml"
    if workflow_path.is_file():
        workflow = read_text(workflow_path, "verification workflow", errors)
        workflow_canonical = f"run: {canonical_command}"
        workflow_fixture = f"run: {fixture_command}"
        for command in (workflow_canonical, workflow_fixture):
            if command not in workflow:
                errors.append(f"verification workflow: missing required command: {command.removeprefix('run: ')}")
        if workflow_canonical in workflow and workflow_fixture in workflow:
            if workflow.index(workflow_canonical) > workflow.index(workflow_fixture):
                errors.append("verification workflow: canonical harness command must precede fixture tests")
    return files


def read_git_status(root: Path, errors: list[str]) -> list[str]:
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain=v1", "--untracked-files=all"],
            check=False,
            capture_output=True,
            text=True,
            timeout=20,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        errors.append(f"git: cannot inspect dynamic status: {type(exc).__name__}: {exc}")
        return []
    if completed.returncode != 0:
        errors.append(f"git: status failed with code {completed.returncode}: {completed.stderr.strip()}")
        return []
    return completed.stdout.splitlines()


def check_repository(root: Path) -> dict[str, Any]:
    errors: list[str] = []
    files = check_required_contract(root, errors)
    plans = discover_plans(root, errors)
    check_indexes(root, plans, errors)
    check_roadmap(root, plans, errors)
    check_current_state(root, plans, errors)
    for relative in ("PROGRESS.md", "HANDOFF.md"):
        check_legacy_git_keys(root / relative, root, errors)
    git_status = read_git_status(root, errors)
    return {
        "schema_version": "operating-modes-check-v1",
        "root": str(root),
        "files": files,
        "plans": [
            {
                "path": str(plan.path.relative_to(root)),
                "slug": plan.slug,
                "status": plan.status,
                "revision": plan.revision,
            }
            for plan in plans
        ],
        "git_status": git_status,
        "errors": errors,
        "passed": not errors,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    root = args.root.expanduser().resolve()
    payload = check_repository(root)
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    for error in payload["errors"]:
        print(f"ERROR: {error}", file=sys.stderr)
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
