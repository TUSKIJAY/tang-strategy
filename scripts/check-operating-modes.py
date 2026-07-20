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

V2_PLAN_KEYS = PLAN_KEYS + (
    "Implementation start evidence",
    "Current work unit",
    "Work state",
    "Blocker evidence",
    "Implementation reviews",
    "Latest implementation verdict",
    "Checkpoint authority",
    "Checkpoint authority mode",
    "Checkpoint authority kinds",
    "Expected checkpoint kind",
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

V2_REVIEW_KEYS = REVIEW_KEYS + ("Review target commit",)

CHECKPOINT_KINDS = (
    "opt-record",
    "plan-proposal",
    "design-review",
    "proposal-revision",
    "activation-recording",
    "implementation-start",
    "phase-exit",
    "phase-blocked",
    "implementation-review",
    "remediation-complete",
    "completed-migration",
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
    "docs/decisions/2026-07-20-durable-checkpoint-governance.md",
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
DURABLE_AUTHORITY_RE = re.compile(r"^user-instruction:[a-z0-9][a-z0-9._/-]{0,127}$")
WORK_UNIT_RE = re.compile(r"(?:phase-[0-6]|remediation-[1-9][0-9]*)$")
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
LINK_RE = re.compile(r"\[([^]]+)\]\(([^)]+)\)")
LEGACY_GIT_KEY_RE = re.compile(
    r"^- (Branch/HEAD|Current HEAD|Git state|Current worktree|Worktree status):"
)
INDEX_HEADERS = {
    "proposed": ["Plan", "Status", "Review", "Next gate"],
    "active": ["Plan", "Current phase", "Evidence", "Next gate"],
    "completed": ["Plan", "Disposition", "Verification", "Final commit"],
    "reviews": ["Plan", "Reviews", "Latest verdict", "Lifecycle state"],
}


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


def inline_code_span_ranges(text: str) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    cursor = 0
    while cursor < len(text):
        if text[cursor] != "`":
            cursor += 1
            continue
        end_of_opener = cursor
        while end_of_opener < len(text) and text[end_of_opener] == "`":
            end_of_opener += 1
        delimiter_length = end_of_opener - cursor
        probe = end_of_opener
        closing_end: int | None = None
        while probe < len(text):
            next_tick = text.find("`", probe)
            if next_tick == -1:
                break
            run_end = next_tick
            while run_end < len(text) and text[run_end] == "`":
                run_end += 1
            if run_end - next_tick == delimiter_length:
                closing_end = run_end
                break
            probe = run_end
        if closing_end is None:
            cursor = end_of_opener
            continue
        ranges.append((cursor, closing_end))
        cursor = closing_end
    return ranges


def mask_full_line_code_spans(text: str) -> str:
    ranges = inline_code_span_ranges(text)
    if not ranges:
        return text
    kept: list[str] = []
    offset = 0
    for line in text.splitlines(keepends=True):
        content = line.rstrip("\r\n")
        ending = line[len(content):]
        leading = len(content) - len(content.lstrip())
        trailing = len(content.rstrip())
        content_start = offset + leading
        content_end = offset + trailing
        inside_code = content_start < content_end and any(
            start <= content_start and end >= content_end for start, end in ranges
        )
        kept.append(ending if inside_code else line)
        offset += len(line)
    return "".join(kept)


def mask_raw_html_code(text: str) -> str:
    """Mask nested raw HTML code/pre elements, failing closed when unclosed."""

    code_ranges = inline_code_span_ranges(text)
    stack: list[str] = []
    masked_ranges: list[tuple[int, int]] = []
    carrier_start: int | None = None
    tag_pattern = re.compile(r"<\s*(/?)\s*(code|pre)(?=\s|/|>)[^>]*>", re.IGNORECASE)
    for match in tag_pattern.finditer(text):
        if any(start <= match.start() and end >= match.end() for start, end in code_ranges):
            continue
        closing = bool(match.group(1))
        tag = match.group(2).lower()
        if not closing:
            if not stack:
                carrier_start = match.start()
            stack.append(tag)
            continue
        if not stack or stack[-1] != tag:
            continue
        stack.pop()
        if not stack and carrier_start is not None:
            masked_ranges.append((carrier_start, match.end()))
            carrier_start = None
    if stack and carrier_start is not None:
        masked_ranges.append((carrier_start, len(text)))
    if not masked_ranges:
        return text
    characters = list(text)
    for start, end in masked_ranges:
        for index in range(start, end):
            if characters[index] not in {"\r", "\n"}:
                characters[index] = " "
    return "".join(characters)


def operative_markdown_text(text: str) -> str:
    """Mask comments and code carriers while preserving source line positions."""

    def mask_comment(match: re.Match[str]) -> str:
        return "\n" * match.group(0).count("\n")

    without_comments = re.sub(r"<!--.*?(?:-->|$)", mask_comment, text, flags=re.DOTALL)
    kept: list[str] = []
    fence_character: str | None = None
    fence_length = 0
    for line in without_comments.splitlines():
        if fence_character is not None:
            kept.append("")
            closing = re.fullmatch(
                rf" {{0,3}}{re.escape(fence_character)}{{{fence_length},}}\s*",
                line,
            )
            if closing:
                fence_character = None
                fence_length = 0
            continue
        opening = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if opening:
            marker = opening.group(1)
            fence_character = marker[0]
            fence_length = len(marker)
            kept.append("")
            continue
        if line.startswith("    ") or line.startswith("\t"):
            kept.append("")
            continue
        kept.append(line)
    without_markdown_blocks = "\n".join(kept)
    without_raw_code = mask_raw_html_code(without_markdown_blocks)
    return mask_full_line_code_spans(without_raw_code)


def has_canonical_markdown_route(path: Path, target: Path, errors: list[str]) -> bool:
    text = operative_markdown_text(read_text(path, "contract route", errors))
    code_ranges = inline_code_span_ranges(text)
    for match in LINK_RE.finditer(text):
        if any(start <= match.start() and end >= match.end() for start, end in code_ranges):
            continue
        raw_target = match.group(2).strip().strip("<>")
        if (path.parent / raw_target).resolve() == target.resolve():
            return True
    return False


def yaml_key_value(text: str, key: str) -> str | None:
    match = re.fullmatch(
        rf"(?:{re.escape(key)}|'(?:{re.escape(key)})'|\"(?:{re.escape(key)})\")\s*:\s*(.*)",
        text,
    )
    return match.group(1) if match else None


def yaml_mapping_key(text: str) -> str | None:
    match = re.fullmatch(r"(?:([A-Za-z0-9_-]+)|'([A-Za-z0-9_-]+)'|\"([A-Za-z0-9_-]+)\")\s*:\s*.*", text)
    if not match:
        return None
    return next(value for value in match.groups() if value is not None)


def clean_yaml_scalar(value: str) -> str:
    cleaned = value.strip()
    if len(cleaned) >= 2 and cleaned[0] == cleaned[-1] and cleaned[0] in {"'", '"'}:
        cleaned = cleaned[1:-1]
    return cleaned


def yaml_single_line_source_character_allowed(character: str) -> bool:
    codepoint = ord(character)
    return (
        character == "\t"
        or 0x20 <= codepoint <= 0x7E
        or 0xA0 <= codepoint <= 0xD7FF
        or 0xE000 <= codepoint <= 0xFFFD
        or 0x10000 <= codepoint <= 0x10FFFF
    )


def decode_yaml_double_quoted(value: str) -> str | None:
    """Decode the declared single-line YAML double-quoted scalar subset."""

    if len(value) < 2 or value[0] != '"' or value[-1] != '"':
        return None
    escapes = {
        "0": "\0",
        "a": "\a",
        "b": "\b",
        "t": "\t",
        "n": "\n",
        "v": "\v",
        "f": "\f",
        "r": "\r",
        "e": "\x1b",
        " ": " ",
        '"': '"',
        "/": "/",
        "\\": "\\",
        "N": "\u0085",
        "_": "\u00a0",
        "L": "\u2028",
        "P": "\u2029",
    }
    decoded: list[str] = []
    index = 1
    end = len(value) - 1
    while index < end:
        character = value[index]
        if character == '"' or not yaml_single_line_source_character_allowed(character):
            return None
        if character != "\\":
            decoded.append(character)
            index += 1
            continue
        index += 1
        if index >= end:
            return None
        escape = value[index]
        if escape in escapes:
            decoded.append(escapes[escape])
            index += 1
            continue
        widths = {"x": 2, "u": 4, "U": 8}
        width = widths.get(escape)
        if width is None or index + width >= end:
            return None
        digits = value[index + 1 : index + 1 + width]
        if not re.fullmatch(rf"[0-9A-Fa-f]{{{width}}}", digits):
            return None
        codepoint = int(digits, 16)
        if codepoint > 0x10FFFF or 0xD800 <= codepoint <= 0xDFFF:
            return None
        decoded.append(chr(codepoint))
        index += width + 1
    return "".join(decoded)


def yaml_plain_scalar_is_numeric(value: str) -> bool:
    """Recognize YAML 1.1/1.2 numeric spellings excluded from strings."""

    patterns = (
        r"[-+]?0[bB][0-1_]+",
        r"[-+]?0[oO][0-7_]+",
        r"[-+]?0[0-7_]+",
        r"[-+]?0[xX][0-9a-fA-F_]+",
        r"[-+]?[0-9][0-9_]*",
        r"[-+]?[1-9][0-9_]*(?::[0-5]?[0-9])+",
        r"[-+]?(?:[0-9][0-9_]*)?\.[0-9_]+(?:[eE][-+]?[0-9_]+)?",
        r"[-+]?[0-9][0-9_]*\.(?:[0-9_]*)?(?:[eE][-+]?[0-9_]+)?",
        r"[-+]?[0-9][0-9_]*(?:[eE][-+]?[0-9_]+)",
        r"[-+]?[1-9][0-9_]*(?::[0-5]?[0-9])+\.[0-9_]*",
    )
    return any(re.fullmatch(pattern, value) for pattern in patterns)


def constrained_yaml_string(value: str) -> str | None:
    """Parse the declared plain/quoted YAML string subset without coercion."""

    cleaned = value.strip()
    if not cleaned:
        return None
    if cleaned.startswith('"'):
        return decode_yaml_double_quoted(cleaned)
    if cleaned.startswith("'"):
        if len(cleaned) < 2 or not cleaned.endswith("'"):
            return None
        inner = cleaned[1:-1]
        parsed: list[str] = []
        index = 0
        while index < len(inner):
            if inner[index] != "'":
                parsed.append(inner[index])
                index += 1
                continue
            if index + 1 >= len(inner) or inner[index + 1] != "'":
                return None
            parsed.append("'")
            index += 2
        return "".join(parsed)
    if cleaned[0] in "&*!#%@`{}[],|>":
        return None
    if any(character in cleaned for character in "{}[],"):
        return None
    if re.match(r"[-?:](?:\s|$)", cleaned):
        return None
    if cleaned.endswith(":") or re.search(r":\s|\s#", cleaned):
        return None
    if cleaned.lower() in {
        "null", "true", "false", "yes", "no", "on", "off", ".nan", ".inf", "+.inf", "-.inf"
    } or cleaned == "~":
        return None
    if yaml_plain_scalar_is_numeric(cleaned):
        return None
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}(?:[Tt ][0-9:.+-]+[Zz]?)?", cleaned):
        return None
    return cleaned


def direct_yaml_key_counts(lines: list[str], indent: int) -> dict[str, int]:
    counts: dict[str, int] = {}
    for line in lines:
        stripped = line.lstrip()
        if not stripped or stripped.startswith("#") or len(line) - len(stripped) != indent:
            continue
        key = yaml_mapping_key(stripped)
        if key is not None:
            counts[key] = counts.get(key, 0) + 1
    return counts


def direct_yaml_entries_are_mappings(lines: list[str], indent: int) -> bool:
    return all(
        yaml_mapping_key(line.lstrip()) is not None
        for line in lines
        if line.strip()
        and not line.lstrip().startswith("#")
        and len(line) - len(line.lstrip()) == indent
    )


def workflow_job_id_counts(lines: list[str]) -> tuple[dict[str, int], bool]:
    jobs_index = next(
        (
            index
            for index, line in enumerate(lines)
            if len(line) == len(line.lstrip())
            and yaml_mapping_key(line.strip()) == "jobs"
            and yaml_key_value(line.strip(), "jobs") == ""
        ),
        None,
    )
    if jobs_index is None:
        return {}, False
    jobs_end = len(lines)
    for index in range(jobs_index + 1, len(lines)):
        stripped = lines[index].lstrip()
        if stripped and not stripped.startswith("#") and len(lines[index]) == len(stripped):
            jobs_end = index
            break
    entries = [
        (len(lines[index]) - len(lines[index].lstrip()), lines[index].lstrip())
        for index in range(jobs_index + 1, jobs_end)
        if lines[index].strip() and not lines[index].lstrip().startswith("#")
    ]
    if not entries:
        return {}, False
    job_indent = min(indent for indent, _ in entries)
    counts: dict[str, int] = {}
    valid = True
    for indent, entry in entries:
        if indent != job_indent:
            continue
        key = yaml_mapping_key(entry)
        if key is None or yaml_key_value(entry, key) != "":
            valid = False
            continue
        counts[key] = counts.get(key, 0) + 1
    return counts, valid


def block_scalar_style(value: str) -> re.Match[str] | None:
    return re.fullmatch(r"([|>])(?:(?:([1-9])([+-])?)|(?:([+-])([1-9])?))?", value)


def normalize_block_scalar(lines: list[str], index: int, indent: int, style: str) -> tuple[str, int]:
    raw_lines: list[str] = []
    cursor = index + 1
    while cursor < len(lines):
        block_line = lines[cursor]
        block_stripped = block_line.lstrip(" ")
        block_indent = len(block_line) - len(block_stripped)
        if block_stripped and block_indent <= indent:
            break
        raw_lines.append(block_line)
        cursor += 1
    nonempty_indents = [
        len(line) - len(line.lstrip(" "))
        for line in raw_lines
        if line.strip()
    ]
    if not nonempty_indents or any("\t" in line[: len(line) - len(line.lstrip())] for line in raw_lines):
        return "", cursor
    style_match = block_scalar_style(style)
    if style_match is None:
        return "", cursor
    explicit_indent = style_match.group(2) or style_match.group(5)
    content_indent = indent + int(explicit_indent) if explicit_indent else min(nonempty_indents)
    if any(line_indent < content_indent for line_indent in nonempty_indents):
        return "", cursor
    content = [line[content_indent:] if line.strip() else "" for line in raw_lines]
    while content and content[-1] == "":
        content.pop()
    if not content:
        return "", cursor
    if style.startswith("|"):
        return "\n".join(content), cursor
    normalized = content[0]
    for previous, current in zip(content, content[1:]):
        separator = "\n" if not previous or not current else " "
        normalized += separator + current
    return normalized, cursor


def normalized_run_command(lines: list[str], index: int, indent: int, value: str) -> tuple[str, int]:
    if block_scalar_style(value) is not None:
        return normalize_block_scalar(lines, index, indent, value)
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        value = value[1:-1]
    return (value if value and not value.startswith("#") else ""), index + 1


def workflow_job_command_sequences(text: str) -> list[list[str]]:
    """Extract direct commands per unique, unconditional top-level workflow job."""
    lines = text.splitlines()
    candidates: list[tuple[int, int, str]] = []
    conditional_jobs: set[int] = set()
    conditional_steps: set[tuple[int, int]] = set()
    modified_jobs: set[int] = set()
    modified_steps: set[tuple[int, int]] = set()
    job_key_counts: dict[tuple[int, str], int] = {}
    step_key_counts: dict[tuple[int, int, str], int] = {}
    top_level_counts = direct_yaml_key_counts(lines, 0)
    job_name_counts, job_ids_valid = workflow_job_id_counts(lines)
    workflow_modified = (
        top_level_counts.get("jobs", 0) != 1
        or any(count != 1 for count in top_level_counts.values())
        or any(key in top_level_counts for key in {"defaults", "env"})
        or not direct_yaml_entries_are_mappings(lines, 0)
        or not job_ids_valid
    )
    runnable_jobs: set[int] = set()
    jobs_active = False
    jobs_indent = 0
    job_indent: int | None = None
    job_field_indent: int | None = None
    job_id = 0
    steps_indent: int | None = None
    step_indent: int | None = None
    step_field_indent: int | None = None
    step_id = 0
    index = 0
    while index < len(lines):
        line = lines[index]
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        if not stripped or stripped.startswith("#"):
            index += 1
            continue
        if indent == 0 and yaml_mapping_key(stripped) == "jobs" and yaml_key_value(stripped, "jobs") == "":
            jobs_active = True
            jobs_indent = indent
            job_indent = None
            job_field_indent = None
            steps_indent = None
            step_indent = None
            step_field_indent = None
            index += 1
            continue
        if not jobs_active:
            index += 1
            continue
        if indent <= jobs_indent:
            jobs_active = False
            job_indent = None
            job_field_indent = None
            steps_indent = None
            step_indent = None
            step_field_indent = None
            continue

        job_name = yaml_mapping_key(stripped)
        job_header = job_name is not None and yaml_key_value(stripped, job_name) == ""
        if job_header and (job_indent is None or indent <= job_indent):
            job_indent = indent
            job_field_indent = None
            job_id += 1
            steps_indent = None
            step_indent = None
            step_field_indent = None
            step_id = 0
            index += 1
            continue
        if job_indent is None or indent <= job_indent:
            index += 1
            continue
        if job_field_indent is None:
            job_field_indent = indent
        if indent == job_field_indent:
            job_key = yaml_mapping_key(stripped)
            if job_key is not None:
                count_key = (job_id, job_key)
                job_key_counts[count_key] = job_key_counts.get(count_key, 0) + 1
                if job_key_counts[count_key] > 1:
                    modified_jobs.add(job_id)
            if job_key == "if":
                conditional_jobs.add(job_id)
            if job_key not in {"name", "runs-on", "steps"}:
                modified_jobs.add(job_id)
            if job_key == "name":
                job_name = constrained_yaml_string(yaml_key_value(stripped, "name") or "")
                if job_name is None or not job_name.strip():
                    modified_jobs.add(job_id)
            if job_key == "runs-on" and clean_yaml_scalar(yaml_key_value(stripped, "runs-on") or "") == "ubuntu-latest":
                runnable_jobs.add(job_id)
            if yaml_key_value(stripped, "steps") == "":
                steps_indent = indent
                step_indent = None
                step_field_indent = None
                index += 1
                continue
            if steps_indent is not None:
                steps_indent = None
                step_indent = None
                step_field_indent = None
        if steps_indent is None or indent <= steps_indent:
            index += 1
            continue

        if step_indent is None:
            step_indent = indent
        if indent < step_indent:
            modified_jobs.add(job_id)
            index += 1
            continue
        if indent == step_indent and not stripped.startswith("- "):
            modified_jobs.add(job_id)
            index += 1
            continue
        direct_step = indent == step_indent and stripped.startswith("- ")
        if direct_step:
            step_field_indent = None
            step_id += 1
            step_value = stripped[2:].lstrip()
            step_key = yaml_mapping_key(step_value)
            if step_key is not None:
                count_key = (job_id, step_id, step_key)
                step_key_counts[count_key] = step_key_counts.get(count_key, 0) + 1
                if step_key_counts[count_key] > 1:
                    modified_steps.add((job_id, step_id))
            if step_key == "if":
                conditional_steps.add((job_id, step_id))
            if step_key not in {"name", "run"}:
                modified_steps.add((job_id, step_id))
            if step_key is None:
                modified_jobs.add(job_id)
            if step_key == "name":
                step_name = constrained_yaml_string(yaml_key_value(step_value, "name") or "")
                if step_name is None or not step_name.strip():
                    modified_steps.add((job_id, step_id))
            run_value = yaml_key_value(step_value, "run")
            if run_value is not None:
                command, index = normalized_run_command(
                    lines,
                    index,
                    indent + 2,
                    run_value,
                )
                if command:
                    candidates.append((job_id, step_id, command))
                continue
            index += 1
            continue

        if step_indent is not None and indent > step_indent and step_field_indent is None:
            step_field_indent = indent
        if step_indent is not None and indent == step_field_indent:
            step_key = yaml_mapping_key(stripped)
            if step_key is not None:
                count_key = (job_id, step_id, step_key)
                step_key_counts[count_key] = step_key_counts.get(count_key, 0) + 1
                if step_key_counts[count_key] > 1:
                    modified_steps.add((job_id, step_id))
            if step_key == "if":
                conditional_steps.add((job_id, step_id))
            if step_key not in {"name", "run"}:
                modified_steps.add((job_id, step_id))
            if step_key == "name":
                step_name = constrained_yaml_string(yaml_key_value(stripped, "name") or "")
                if step_name is None or not step_name.strip():
                    modified_steps.add((job_id, step_id))
            run_value = yaml_key_value(stripped, "run")
            if run_value is not None:
                command, index = normalized_run_command(
                    lines,
                    index,
                    indent,
                    run_value,
                )
                if command:
                    candidates.append((job_id, step_id, command))
                continue
        index += 1
    if workflow_modified or any(count != 1 for count in job_name_counts.values()):
        return []
    sequences: dict[int, list[str]] = {}
    for candidate_job, candidate_step, command in candidates:
        if (
            candidate_job in runnable_jobs
            and job_key_counts.get((candidate_job, "name"), 0) == 1
            and job_key_counts.get((candidate_job, "runs-on"), 0) == 1
            and job_key_counts.get((candidate_job, "steps"), 0) == 1
            and candidate_job not in conditional_jobs
            and candidate_job not in modified_jobs
            and (candidate_job, candidate_step) not in conditional_steps
            and (candidate_job, candidate_step) not in modified_steps
            and step_key_counts.get((candidate_job, candidate_step, "run"), 0) == 1
        ):
            sequences.setdefault(candidate_job, []).append(command)
    return [sequences[job] for job in sorted(sequences)]


def flow_sequence_values(value: str) -> list[str] | None:
    cleaned = value.strip()
    if not (cleaned.startswith("[") and cleaned.endswith("]")):
        return None
    body = cleaned[1:-1].strip()
    if not body:
        return []
    raw_items: list[str] = []
    current: list[str] = []
    quote: str | None = None
    index = 0
    while index < len(body):
        character = body[index]
        if quote is not None:
            current.append(character)
            if quote == '"' and character == "\\":
                if index + 1 >= len(body):
                    return None
                index += 1
                current.append(body[index])
            elif quote == "'" and character == "'" and index + 1 < len(body) and body[index + 1] == "'":
                index += 1
                current.append(body[index])
            elif character == quote:
                quote = None
            index += 1
            continue
        if character in {"'", '"'}:
            quote = character
            current.append(character)
        elif character == ",":
            item = "".join(current).strip()
            if not item:
                return None
            raw_items.append(item)
            current = []
        elif character in "[]{}":
            return None
        else:
            current.append(character)
        index += 1
    if quote is not None:
        return None
    final_item = "".join(current).strip()
    if final_item:
        raw_items.append(final_item)
    elif not raw_items or not body.rstrip().endswith(","):
        return None
    parsed = [constrained_yaml_string(item) for item in raw_items]
    if any(item is None or not item.strip() for item in parsed):
        return None
    return [item for item in parsed if item is not None]


def workflow_has_pull_request_main(text: str) -> bool:
    lines = text.splitlines()
    top_level_counts = direct_yaml_key_counts(lines, 0)
    if (
        top_level_counts.get("on", 0) != 1
        or any(count != 1 for count in top_level_counts.values())
        or not direct_yaml_entries_are_mappings(lines, 0)
    ):
        return False
    on_index = next(
        (
            index
            for index, line in enumerate(lines)
            if len(line) == len(line.lstrip())
            and yaml_mapping_key(line.strip()) == "on"
        ),
        None,
    )
    if on_index is None or yaml_key_value(lines[on_index].strip(), "on") != "":
        return False
    on_end = len(lines)
    for index in range(on_index + 1, len(lines)):
        stripped = lines[index].lstrip()
        if stripped and not stripped.startswith("#") and len(lines[index]) == len(stripped):
            on_end = index
            break
    event_entries = [
        (index, len(lines[index]) - len(lines[index].lstrip()), lines[index].lstrip())
        for index in range(on_index + 1, on_end)
        if lines[index].strip() and not lines[index].lstrip().startswith("#")
    ]
    if not event_entries:
        return False
    event_indent = min(indent for _, indent, _ in event_entries)
    direct_events = [(index, text) for index, indent, text in event_entries if indent == event_indent]
    event_counts: dict[str, int] = {}
    for _, event_text in direct_events:
        key = yaml_mapping_key(event_text)
        if key is None or yaml_key_value(event_text, key) != "":
            return False
        event_counts[key] = event_counts.get(key, 0) + 1
    if event_counts.get("pull_request", 0) != 1 or any(count != 1 for count in event_counts.values()):
        return False
    pull_request_index, pull_request_text = next(
        (index, event_text)
        for index, event_text in direct_events
        if yaml_mapping_key(event_text) == "pull_request"
    )
    if yaml_key_value(pull_request_text, "pull_request") != "":
        return False
    pull_request_end = on_end
    for index in range(pull_request_index + 1, on_end):
        stripped = lines[index].lstrip()
        indent = len(lines[index]) - len(stripped)
        if stripped and not stripped.startswith("#") and indent <= event_indent:
            pull_request_end = index
            break
    field_entries = [
        (index, len(lines[index]) - len(lines[index].lstrip()), lines[index].lstrip())
        for index in range(pull_request_index + 1, pull_request_end)
        if lines[index].strip() and not lines[index].lstrip().startswith("#")
    ]
    if not field_entries:
        return False
    field_indent = min(indent for _, indent, _ in field_entries)
    direct_fields = [(index, text) for index, indent, text in field_entries if indent == field_indent]
    field_counts: dict[str, int] = {}
    for _, field_text in direct_fields:
        key = yaml_mapping_key(field_text)
        if key is None:
            return False
        field_counts[key] = field_counts.get(key, 0) + 1
    if field_counts != {"branches": 1}:
        return False
    branches_index, branches_text = next(
        (index, field_text)
        for index, field_text in direct_fields
        if yaml_mapping_key(field_text) == "branches"
    )
    branches_value = yaml_key_value(branches_text, "branches")
    if branches_value is None:
        return False
    if branches_value:
        values = flow_sequence_values(branches_value)
        return values is not None and "main" in values
    branch_end = pull_request_end
    for index in range(branches_index + 1, pull_request_end):
        stripped = lines[index].lstrip()
        indent = len(lines[index]) - len(stripped)
        if stripped and not stripped.startswith("#") and indent <= field_indent:
            branch_end = index
            break
    branch_entries = [
        (len(lines[index]) - len(lines[index].lstrip()), lines[index].lstrip())
        for index in range(branches_index + 1, branch_end)
        if lines[index].strip() and not lines[index].lstrip().startswith("#")
    ]
    if not branch_entries:
        return False
    branch_indent = min(indent for indent, _ in branch_entries)
    values: list[str] = []
    for indent, branch_text in branch_entries:
        if indent != branch_indent:
            return False
        match = re.fullmatch(r"-\s+(.+?)\s*", branch_text)
        if match is None:
            return False
        value = constrained_yaml_string(match.group(1))
        if value is None or not value.strip():
            return False
        values.append(value)
    return "main" in values


def parse_header_bullets(
    text: str,
    *,
    duplicate_errors: list[str] | None = None,
    label: str = "metadata",
) -> dict[str, str]:
    metadata: dict[str, str] = {}
    for line in operative_markdown_text(text).splitlines():
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
            required_keys = V2_PLAN_KEYS if plan.schema == "operating-modes-v2" else PLAN_KEYS
            missing = [key for key in required_keys if key not in metadata]
            if missing:
                errors.append(
                    f"plan metadata: {path.relative_to(root)} missing required keys: {', '.join(missing)}"
                )
            present_required = [key for key in metadata if key in required_keys]
            if plan.schema == "operating-modes-v2" and present_required != list(required_keys):
                errors.append(
                    f"plan metadata: {path.relative_to(root)} v2 constrained keys must use the exact required order"
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
    if plan.schema not in {"operating-modes-v1", "operating-modes-v2", "operating-modes-legacy-v1"}:
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
    elif plan.schema in {"operating-modes-v1", "operating-modes-v2"} and independence != "attested":
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
                allow_legacy=(
                    plan.schema == "operating-modes-legacy-v1"
                    and plan.directory_state == "completed"
                ),
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
        if disposition != "none" or (implementation != "none" and plan.schema != "operating-modes-v2"):
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

    if plan.schema == "operating-modes-v2":
        validate_v2_plan_metadata(plan, root, errors)


def parse_implementation_reviews(
    value: str, relative: Path, errors: list[str]
) -> list[tuple[str, str, str]]:
    cleaned = clean_value(value)
    if cleaned == "none" or not cleaned:
        return []
    results: list[tuple[str, str, str]] = []
    for raw_item in cleaned.split(","):
        item = clean_value(raw_item)
        parts = item.rsplit("@", 2)
        if (
            len(parts) != 3
            or parts[1] not in {"accept", "revise", "reject"}
            or not parts[0]
            or not COMMIT_RE.fullmatch(parts[2])
        ):
            errors.append(f"plan reviews: {relative} invalid Implementation reviews entry={item!r}")
            continue
        results.append((parts[0], parts[1], parts[2]))
    return results


def validate_v2_plan_metadata(plan: Plan, root: Path, errors: list[str]) -> None:
    meta = {key: clean_value(value) for key, value in plan.metadata.items()}
    relative = plan.path.relative_to(root)

    implementation_start = meta.get("Implementation start evidence", "")
    if implementation_start != "none" and not ACTIVATION_RE.fullmatch(implementation_start):
        errors.append(
            f"plan metadata: {relative} Implementation start evidence must be none or user-instruction"
        )

    work_unit = meta.get("Current work unit", "")
    if work_unit != "none" and not WORK_UNIT_RE.fullmatch(work_unit):
        errors.append(f"plan metadata: {relative} invalid Current work unit={work_unit!r}")
    work_state = meta.get("Work state", "")
    if work_state not in {"none", "not-started", "in-progress", "blocked", "complete"}:
        errors.append(f"plan metadata: {relative} invalid Work state={work_state!r}")

    blocker = meta.get("Blocker evidence", "")
    blocked = meta.get("Phase state") == "blocked" or work_state == "blocked"
    if blocked != (blocker != "none"):
        errors.append(f"plan state: {relative} Blocker evidence must be non-none iff a state is blocked")
    if blocker != "none":
        blocker_path = resolve_inside(root, plan.path.parent, blocker, "blocker evidence", errors)
        if blocker_path is None or not blocker_path.is_file():
            errors.append(f"blocker evidence: {relative} referenced evidence does not exist: {blocker}")

    reviews = parse_implementation_reviews(meta.get("Implementation reviews", ""), relative, errors)
    latest = meta.get("Latest implementation verdict", "")
    if latest not in {"none", "accept", "revise", "reject"}:
        errors.append(f"plan metadata: {relative} invalid Latest implementation verdict={latest!r}")
    if reviews:
        if latest != reviews[-1][1]:
            errors.append(
                f"plan reviews: {relative} Latest implementation verdict={latest!r} does not match "
                f"final structured review verdict={reviews[-1][1]!r}"
            )
    elif meta.get("Implementation reviews") != "none" or latest != "none":
        errors.append(
            f"plan reviews: {relative} no structured implementation reviews requires both fields none"
        )

    for raw_path, verdict, target_commit in reviews:
        review_path = resolve_inside(root, plan.path.parent, raw_path, "implementation review", errors)
        if review_path is None or not review_path.is_file():
            errors.append(f"implementation review: {relative} referenced review does not exist: {raw_path}")
            continue
        validate_review(
            root,
            plan,
            review_path,
            verdict,
            plan.revision,
            errors,
            expected_type="implementation",
            allow_legacy=False,
        )
        review_meta = {
            key: clean_value(value)
            for key, value in parse_header_bullets(read_text(review_path, "review", errors)).items()
        }
        if review_meta.get("Review target commit") != target_commit:
            errors.append(
                f"review target commit: {review_path.relative_to(root)} metadata does not match plan declaration"
            )

    compatibility_review = meta.get("Implementation review", "")
    verified_commit = meta.get("Verified implementation commit", "")
    if latest == "accept" and reviews:
        expected_pointer = f"{reviews[-1][0]}@accept"
        if compatibility_review != expected_pointer:
            errors.append(
                f"plan reviews: {relative} accepted v2 plan requires Implementation review={expected_pointer!r}"
            )
        if verified_commit != reviews[-1][2]:
            errors.append(
                f"plan reviews: {relative} Verified implementation commit must equal accepted review target"
            )
    else:
        if compatibility_review != "none":
            errors.append(f"plan reviews: {relative} non-accepted v2 plan requires Implementation review=none")
        if verified_commit != "none":
            errors.append(f"plan reviews: {relative} non-accepted v2 plan requires Verified implementation commit=none")
    if meta.get("Lifecycle reconciliation commit") != "none":
        errors.append(f"plan metadata: {relative} v2 Lifecycle reconciliation commit must be none")

    authority = meta.get("Checkpoint authority", "")
    authority_mode = meta.get("Checkpoint authority mode", "")
    raw_kinds = meta.get("Checkpoint authority kinds", "")
    if authority == "none":
        if authority_mode != "none" or raw_kinds != "none":
            errors.append(f"plan authority: {relative} none authority requires none mode and kinds")
    else:
        if not DURABLE_AUTHORITY_RE.fullmatch(authority):
            errors.append(f"plan authority: {relative} invalid Checkpoint authority={authority!r}")
        if authority_mode not in {"one-shot", "standing"}:
            errors.append(f"plan authority: {relative} invalid Checkpoint authority mode={authority_mode!r}")
        kinds = raw_kinds.split(",") if raw_kinds else []
        ordered = [kind for kind in CHECKPOINT_KINDS if kind in kinds]
        if not kinds or kinds != ordered or len(kinds) != len(set(kinds)):
            errors.append(
                f"plan authority: {relative} Checkpoint authority kinds must be ordered, valid, and unique"
            )

    expected_kind = meta.get("Expected checkpoint kind", "")
    if expected_kind not in {"none", *CHECKPOINT_KINDS}:
        errors.append(f"plan metadata: {relative} invalid Expected checkpoint kind={expected_kind!r}")

    phase = meta.get("Current phase", "")
    phase_state = meta.get("Phase state", "")
    next_gate = meta.get("Next gate", "")
    entry_gate = meta.get("Phase entry gate", "")
    if plan.directory_state == "proposed":
        if any(
            value != "none"
            for value in (implementation_start, work_unit, work_state, blocker, meta.get("Implementation reviews"), latest)
        ):
            errors.append(f"plan state: {relative} Proposed v2 plan has implementation/work state")
        return

    if plan.directory_state == "completed":
        if phase != "none" or phase_state != "none" or work_unit != "none" or work_state != "none":
            errors.append(f"plan state: {relative} Completed v2 plan requires no current phase/work unit")
        if meta.get("Final disposition") == "Completed":
            if implementation_start == "none" or latest != "accept":
                errors.append(f"plan state: {relative} implemented Completed v2 plan requires start and accept")
            if expected_kind != "completed-migration" or next_gate != "closed":
                errors.append(
                    f"plan state: {relative} implemented Completed v2 plan requires completed-migration/closed"
                )
        return

    legal = False
    expected_entry: str | None = None
    if (
        phase == "phase-0"
        and phase_state == "not-started"
        and implementation_start == "none"
        and work_unit == "none"
        and work_state == "none"
        and next_gate == "phase-0-start"
    ):
        legal = True
        if not entry_gate.startswith("activation:user-instruction:"):
            errors.append(f"plan state: {relative} activated v2 plan requires activation entry gate")
        if expected_kind != "activation-recording":
            errors.append(f"plan state: {relative} activated v2 plan requires activation-recording checkpoint")
    elif phase_state == "not-started" and work_unit == "none" and work_state == "none":
        legal = implementation_start != "none" and next_gate == f"{phase}-start"
        phase_number = int(phase.rsplit("-", 1)[1]) if re.fullmatch(r"phase-[0-6]", phase) else -1
        expected_entry = implementation_start if phase_number == 0 else f"phase-{phase_number - 1}-exit"
        if expected_kind != ("implementation-start" if phase_number == 0 else "phase-exit"):
            errors.append(f"plan state: {relative} primary ready state has wrong Expected checkpoint kind")
    elif work_unit == phase and work_state == phase_state and phase_state in {"in-progress", "blocked"}:
        legal = implementation_start != "none"
        suffix = "recovery" if phase_state == "blocked" else "exit"
        legal = legal and next_gate == f"{phase}-{suffix}"
        phase_number = int(phase.rsplit("-", 1)[1]) if re.fullmatch(r"phase-[0-6]", phase) else -1
        expected_entry = implementation_start if phase_number == 0 else f"phase-{phase_number - 1}-exit"
        expected_for_state = "phase-blocked" if phase_state == "blocked" else (
            "implementation-start" if phase_number == 0 else "phase-exit"
        )
        if expected_kind != expected_for_state:
            errors.append(f"plan state: {relative} primary active state has wrong Expected checkpoint kind")
    elif phase == "phase-6" and phase_state == "complete" and work_unit == "none" and work_state == "none":
        legal = next_gate in {"implementation-review", "completed-migration"}
        if latest == "accept":
            legal = legal and next_gate == "completed-migration" and expected_kind == "implementation-review"
        else:
            legal = legal and next_gate == "implementation-review" and expected_kind == "phase-exit"
    elif phase == "phase-6" and work_unit.startswith("remediation-"):
        remediation_number = int(work_unit.rsplit("-", 1)[1])
        revise_count = sum(1 for _, verdict, _ in reviews if verdict == "revise")
        if not re.fullmatch(rf"{re.escape(work_unit)}:user-instruction:[A-Za-z0-9][A-Za-z0-9._:@/-]*", entry_gate):
            errors.append(f"plan state: {relative} remediation requires a dedicated user-instruction entry gate")
        if remediation_number != revise_count or latest != "revise":
            errors.append(f"plan state: {relative} remediation numbering/verdict is not sequential")
        if work_state == "not-started" and phase_state == "in-progress":
            legal = next_gate == f"{work_unit}-start" and expected_kind == "implementation-review"
        elif work_state in {"in-progress", "blocked"} and phase_state in {"in-progress", "blocked"}:
            suffix = "recovery" if work_state == "blocked" else "exit"
            legal = next_gate == f"{work_unit}-{suffix}"
            legal = legal and expected_kind == ("phase-blocked" if work_state == "blocked" else "implementation-review")
        elif work_state == "complete" and phase_state == "in-progress":
            legal = next_gate == "implementation-review" and expected_kind == "remediation-complete"

    if expected_entry is not None and entry_gate != expected_entry:
        errors.append(
            f"plan state: {relative} Phase entry gate={entry_gate!r} expected {expected_entry!r}"
        )
    if not legal:
        errors.append(f"plan state: {relative} invalid operating-modes-v2 work-unit state combination")


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
    required_review_keys = V2_REVIEW_KEYS if plan.schema == "operating-modes-v2" else REVIEW_KEYS
    present = [key for key in required_review_keys if key in metadata]
    if not present:
        if not allow_legacy:
            errors.append(f"review metadata: {relative} lacks constrained reviewer fields")
        return False
    missing = [key for key in required_review_keys if key not in metadata]
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
    if plan.schema == "operating-modes-v2":
        ordered = [key for key in metadata if key in required_review_keys]
        if ordered != list(required_review_keys):
            errors.append(f"review metadata: {relative} v2 constrained keys must use the exact required order")
        target_commit = metadata.get("Review target commit", "")
        if not COMMIT_RE.fullmatch(target_commit):
            errors.append(f"review metadata: {relative} invalid Review target commit={target_commit!r}")
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
    text = operative_markdown_text(read_text(path, "index", errors))
    rows: list[tuple[list[str], str, str]] = []
    sentinel_count = 0
    state_sentinel = ["None", "—", "—", "none"]
    reviews_sentinel = ["None", "—", "none", "None"]
    index_kind = path.parent.name
    expected_header = INDEX_HEADERS.get(index_kind)
    expected_separator = ["---", "---", "---", "---"]
    expected_sentinel = reviews_sentinel if index_kind == "reviews" else state_sentinel
    header_count = 0
    separator_count = 0
    table_roles: list[str] = []
    header_lines: list[int] = []
    separator_lines: list[int] = []
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line.startswith("|"):
            continue
        if not line.endswith("|"):
            errors.append(
                f"index: {path.relative_to(root)} table row requires a terminal delimiter: {line}"
            )
            table_roles.append("invalid")
            continue
        raw = line
        body = raw[1:-1]
        cells = [cell.strip() for cell in body.split("|")]
        if cells == expected_header:
            header_count += 1
            header_lines.append(line_number)
            table_roles.append("header")
            continue
        if cells == expected_separator:
            separator_count += 1
            separator_lines.append(line_number)
            table_roles.append("separator")
            continue
        table_roles.append("data")
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
    if expected_header is None:
        errors.append(f"index: {path.relative_to(root)} has no defined fixed-table schema")
    if header_count != 1:
        errors.append(
            f"index: {path.relative_to(root)} must contain exactly one canonical header; "
            f"found {header_count}"
        )
    if separator_count != 1:
        errors.append(
            f"index: {path.relative_to(root)} must contain exactly one canonical separator; "
            f"found {separator_count}"
        )
    if (
        len(table_roles) < 2
        or table_roles[:2] != ["header", "separator"]
        or len(header_lines) != 1
        or len(separator_lines) != 1
        or separator_lines[0] != header_lines[0] + 1
    ):
        errors.append(
            f"index: {path.relative_to(root)} canonical header must be followed immediately by separator"
        )
    if sentinel_count > 1:
        errors.append(f"index: {path.relative_to(root)} contains duplicate None sentinel rows")
    if sentinel_count and rows:
        errors.append(f"index: {path.relative_to(root)} cannot mix a None sentinel with plan rows")
    if not rows and sentinel_count != 1:
        errors.append(
            f"index: {path.relative_to(root)} empty plan set requires exactly one canonical None sentinel"
        )
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
    start_position = text.find(start)
    end_position = text.find(end)
    if start_position >= end_position:
        errors.append(f"state block: {path.relative_to(root)} start marker must precede end marker")
        return {}
    body = text[start_position + len(start):end_position]
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
    route_paths = ("AGENTS.md", "INSTRUCTIONS.md", "docs/README.md")
    route_target = root / "docs" / "operating-modes.md"
    for relative in route_paths:
        path = root / relative
        if path.is_file() and not has_canonical_markdown_route(path, route_target, errors):
            errors.append(
                f"contract route: {relative} does not contain a non-comment canonical Markdown "
                "link to docs/operating-modes.md"
            )
    contract_path = root / "docs" / "operating-modes.md"
    if contract_path.is_file():
        contract_text = operative_markdown_text(read_text(contract_path, "contract route", errors))
        if "operating-modes-v1" not in contract_text and "operating-modes-v2" not in contract_text:
            errors.append(
                "contract route: docs/operating-modes.md does not declare a supported operating-modes schema "
                "outside comments or fenced examples"
            )
    plan_template = root / "docs" / "exec-plans" / "plan-template.md"
    if plan_template.is_file():
        metadata = parse_header_bullets(
            read_text(plan_template, "plan template", errors),
            duplicate_errors=errors,
            label="plan template",
        )
        template_schema = clean_value(metadata.get("Lifecycle schema", ""))
        template_keys = V2_PLAN_KEYS if template_schema == "operating-modes-v2" else PLAN_KEYS
        missing = [key for key in template_keys if key not in metadata]
        if missing:
            errors.append(f"plan template: missing constrained keys: {', '.join(missing)}")
    review_template = root / "docs" / "exec-plans" / "reviews" / "review-template.md"
    if review_template.is_file():
        metadata = parse_header_bullets(
            read_text(review_template, "review template", errors),
            duplicate_errors=errors,
            label="review template",
        )
        template_keys = V2_REVIEW_KEYS if "Review target commit" in metadata else REVIEW_KEYS
        missing = [key for key in template_keys if key not in metadata]
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
        if not workflow_has_pull_request_main(workflow):
            errors.append("verification workflow: missing required pull_request trigger for main")
        workflow_sequences = workflow_job_command_sequences(workflow)
        for command in (canonical_command, fixture_command):
            if not any(command in sequence for sequence in workflow_sequences):
                errors.append(f"verification workflow: missing required command: {command}")
        ordered_sequence = any(
            canonical_command in sequence
            and fixture_command in sequence
            and sequence.index(canonical_command) < sequence.index(fixture_command)
            for sequence in workflow_sequences
        )
        if not ordered_sequence and any(
            canonical_command in sequence for sequence in workflow_sequences
        ) and any(fixture_command in sequence for sequence in workflow_sequences):
            errors.append(
                "verification workflow: canonical harness command and fixture tests must appear "
                "in order in the same qualifying job"
            )
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
