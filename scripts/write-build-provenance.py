#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from datetime import datetime
from pathlib import Path


SHA40 = re.compile(r"^[0-9a-f]{40}$")


def build_manifest(commit_sha: str, built_at: str) -> dict[str, object]:
    if not SHA40.fullmatch(commit_sha):
        raise ValueError("commit_sha must be a lowercase 40-character Git SHA")
    try:
        parsed = datetime.fromisoformat(built_at.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("built_at must be RFC3339") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("built_at must include a UTC offset")
    if parsed.utcoffset().total_seconds() != 0:
        raise ValueError("built_at must be UTC")
    return {
        "schema_version": 1,
        "commit_sha": commit_sha,
        "built_at": built_at,
    }


def write_manifest(path: Path, manifest: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, raw_temporary = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    temporary = Path(raw_temporary)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(manifest, handle, separators=(",", ":"), sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--commit-sha", required=True)
    parser.add_argument("--built-at", required=True)
    args = parser.parse_args()
    write_manifest(args.output, build_manifest(args.commit_sha, args.built_at))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
