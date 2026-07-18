#!/usr/bin/env python3
"""Dependency-free structural check for the project-local harness."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


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
    "docs/exec-plans/roadmap.md",
    "docs/exec-plans/proposed/index.md",
    "docs/exec-plans/active/index.md",
    "docs/exec-plans/completed/index.md",
    "docs/exec-plans/reviews/index.md",
    "docs/decisions/index.md",
    "docs/optimization/SOP.md",
    "docs/progress-archive/index.md",
    "scripts/check-startup-doc-budget.py",
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--profile", choices=("auto", "minimal", "governed"), default="auto")
    args = parser.parse_args(argv)

    root = args.root.expanduser().resolve()
    profile = infer_profile(root) if args.profile == "auto" else args.profile
    required = list(MINIMAL) + (list(GOVERNED) if profile == "governed" else [])
    files = [{"path": relative, "present": (root / relative).is_file()} for relative in required]

    config_error = None
    try:
        config = json.loads((root / ".harness/config.json").read_text(encoding="utf-8"))
        if config.get("schema_version") != "project-harness-config-v1":
            config_error = "unsupported schema_version"
        elif config.get("profile") != profile:
            config_error = f"profile mismatch: config={config.get('profile')} requested={profile}"
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, AttributeError) as exc:
        config_error = f"{type(exc).__name__}: {exc}"

    missing = [item["path"] for item in files if not item["present"]]
    payload = {
        "schema_version": "project-local-harness-check-v1",
        "root": str(root),
        "profile": profile,
        "files": files,
        "missing": missing,
        "config_error": config_error,
        "passed": not missing and config_error is None,
    }
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    if missing:
        print("Missing harness files:", file=sys.stderr)
        for relative in missing:
            print(f"  - {relative}", file=sys.stderr)
    if config_error:
        print(f"Config error: {config_error}", file=sys.stderr)
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
