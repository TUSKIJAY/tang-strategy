#!/usr/bin/env python3
"""Read-only deterministic budget check for startup Markdown documents."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Budget:
    warning_lines: int
    warning_bytes: int
    hard_lines: int
    hard_bytes: int
    max_entries: int = 0  # 0 means the document is not entry-governed


# A PROGRESS.md body entry opens at column 0 with its date.
BODY_ENTRY = re.compile(r"^\d{4}-\d{2}-\d{2}: ")

BUDGETS = {
    # Policy files bloat by rule-creep, not history; a warning here means
    # dedupe/refactor (usually into docs/operating-modes.md or the runbook),
    # not archive. Warnings sit ~60% above current size so growth is flagged
    # while it is still one section, not a rewrite.
    "AGENTS.md": Budget(180, 16_384, 240, 32_768),
    "INSTRUCTIONS.md": Budget(180, 12_288, 300, 40_960),
    # PROGRESS.md is entry-governed: max_entries is the ">10 body entries"
    # archive trigger in docs/progress-archive/index.md, counted directly rather
    # than proxied through bytes. The byte/line budgets stay as the secondary
    # guard against a small number of entries growing individually huge.
    "PROGRESS.md": Budget(280, 12_288, 350, 49_152, max_entries=10),
    # HANDOFF.md is a resume-point snapshot, so it should stay near its current
    # size instead of accumulating. Its old 38,400-byte warning sat 9.5x above
    # the real file and could never fire before HANDOFF.md became a second
    # PROGRESS.md; this one follows the ~60% rule used above. Content-type drift
    # (history landing here) is caught by check-operating-modes.py, not by size.
    "HANDOFF.md": Budget(80, 4_096, 140, 12_288),
}


def evaluate(root: Path, relative: str, budget: Budget) -> dict[str, object]:
    path = root / relative
    try:
        raw = path.read_bytes()
        text = raw.decode("utf-8")
        lines = len(text.splitlines())
        byte_count = len(raw)
        entries = (
            sum(1 for line in text.splitlines() if BODY_ENTRY.match(line))
            if budget.max_entries
            else None
        )
        return {
            "path": relative,
            "lines": lines,
            "bytes": byte_count,
            "entries": entries,
            "archive_required": (
                lines >= budget.warning_lines
                or byte_count >= budget.warning_bytes
                or (entries is not None and entries > budget.max_entries)
            ),
            "hard_limit_exceeded": lines > budget.hard_lines or byte_count > budget.hard_bytes,
            "error": None,
        }
    except (OSError, UnicodeDecodeError) as exc:
        return {
            "path": relative,
            "lines": None,
            "bytes": None,
            "entries": None,
            "archive_required": True,
            "hard_limit_exceeded": True,
            "error": f"{type(exc).__name__}: {exc}",
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    root = args.root.expanduser().resolve()
    documents = [evaluate(root, path, BUDGETS[path]) for path in sorted(BUDGETS)]
    payload = {
        "schema_version": "startup-doc-budget-v1",
        "root": str(root),
        "documents": documents,
        "archive_required": any(bool(item["archive_required"]) for item in documents),
        "hard_limit_exceeded": any(bool(item["hard_limit_exceeded"]) for item in documents),
    }
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    for item in documents:
        print(
            f"{item['path']}: lines={item['lines']} bytes={item['bytes']} "
            f"entries={item['entries']} "
            f"archive_required={str(item['archive_required']).lower()} "
            f"hard_limit_exceeded={str(item['hard_limit_exceeded']).lower()}",
            file=sys.stderr,
        )
    return 1 if payload["hard_limit_exceeded"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
