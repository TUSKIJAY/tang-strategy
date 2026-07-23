#!/usr/bin/env python3
"""Run the verification battery defined in .harness/config.json.

The command list lives only in `.harness/config.json` (`verification_commands`);
this runner executes it and never defines commands of its own. Commands are
POSIX shell lines and run through bash: native on macOS/Linux, Git Bash on
Windows (present wherever Git is installed).
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

FAILURE_TAIL_LINES = 40

WINDOWS_BASH_FALLBACKS = (
    Path("C:/Program Files/Git/bin/bash.exe"),
    Path("C:/Program Files (x86)/Git/bin/bash.exe"),
)


def find_bash() -> str | None:
    found = shutil.which("bash")
    if found:
        return found
    for candidate in WINDOWS_BASH_FALLBACKS:
        if candidate.is_file():
            return str(candidate)
    return None


def load_commands(root: Path) -> list[str]:
    config_path = root / ".harness" / "config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    commands = config.get("verification_commands")
    if not isinstance(commands, list) or not all(isinstance(c, str) and c.strip() for c in commands):
        raise ValueError(".harness/config.json: verification_commands must be a non-empty string list")
    return commands


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--list", action="store_true", help="print the commands without running them")
    parser.add_argument(
        "--only",
        action="append",
        default=[],
        metavar="SUBSTR",
        help="run only commands containing this substring (repeatable)",
    )
    parser.add_argument("--verbose", action="store_true", help="stream command output instead of capturing it")
    args = parser.parse_args(argv)
    root = args.root.expanduser().resolve()

    try:
        commands = load_commands(root)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"verify: {exc}", file=sys.stderr)
        return 2
    if args.only:
        commands = [c for c in commands if any(s in c for s in args.only)]
        if not commands:
            print(f"verify: no verification command matches --only {args.only}", file=sys.stderr)
            return 2

    if args.list:
        for command in commands:
            print(command)
        return 0

    bash = find_bash()
    if bash is None:
        print("verify: bash not found; install Git (Windows) or use a POSIX shell environment", file=sys.stderr)
        return 2

    failures: list[str] = []
    total = len(commands)
    for index, command in enumerate(commands, start=1):
        started = time.monotonic()
        if args.verbose:
            print(f"[{index}/{total}] RUN   {command}", flush=True)
            result = subprocess.run([bash, "-c", command], cwd=root)
            output = ""
        else:
            result = subprocess.run(
                [bash, "-c", command],
                cwd=root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            output = (result.stdout or "") + (result.stderr or "")
        elapsed = time.monotonic() - started
        status = "PASS" if result.returncode == 0 else "FAIL"
        print(f"[{index}/{total}] {status}  {elapsed:6.1f}s  {command}", flush=True)
        if result.returncode != 0:
            failures.append(command)
            if output:
                tail = output.splitlines()[-FAILURE_TAIL_LINES:]
                for line in tail:
                    print(f"    | {line}")

    print(f"verify: {total - len(failures)} passed, {len(failures)} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
