#!/usr/bin/env python3
"""Read-only deterministic budget check for startup Markdown documents."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Budget:
    warning_lines: int
    warning_bytes: int
    hard_lines: int
    hard_bytes: int


BUDGETS = {
    "AGENTS.md": Budget(180, 24_576, 240, 32_768),
    "INSTRUCTIONS.md": Budget(220, 30_720, 300, 40_960),
    "PROGRESS.md": Budget(280, 38_400, 350, 49_152),
    "HANDOFF.md": Budget(176, 38_400, 220, 49_152),
}


def evaluate(root: Path, relative: str, budget: Budget) -> dict[str, object]:
    path = root / relative
    try:
        raw = path.read_bytes()
        text = raw.decode("utf-8")
        lines = len(text.splitlines())
        byte_count = len(raw)
        return {
            "path": relative,
            "lines": lines,
            "bytes": byte_count,
            "archive_required": lines >= budget.warning_lines or byte_count >= budget.warning_bytes,
            "hard_limit_exceeded": lines > budget.hard_lines or byte_count > budget.hard_bytes,
            "error": None,
        }
    except (OSError, UnicodeDecodeError) as exc:
        return {
            "path": relative,
            "lines": None,
            "bytes": None,
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
            f"archive_required={str(item['archive_required']).lower()} "
            f"hard_limit_exceeded={str(item['hard_limit_exceeded']).lower()}",
            file=sys.stderr,
        )
    return 1 if payload["hard_limit_exceeded"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
