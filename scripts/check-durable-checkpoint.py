#!/usr/bin/env python3
"""Read-only durable checkpoint preflight, postflight, and repository audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any


REQUEST_KEYS = (
    "schema_version",
    "kind",
    "subject",
    "revision",
    "work_unit",
    "outcome",
    "authority",
    "expected_branch",
    "baseline_head",
    "paths",
)
PATH_KEYS = ("path", "operation", "baseline_blob", "post_sha256")
TRAILER_KEYS = (
    "Tang-Checkpoint",
    "Tang-Subject",
    "Tang-Revision",
    "Tang-Work-Unit",
    "Tang-Outcome",
    "Tang-Authority",
    "Tang-Remote-Authority",
)
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
OUTCOMES = {
    "opt-record": {"complete"},
    "plan-proposal": {"complete"},
    "design-review": {"approve", "revise", "reject"},
    "proposal-revision": {"complete"},
    "activation-recording": {"complete"},
    "implementation-start": {"complete"},
    "phase-exit": {"complete"},
    "phase-blocked": {"blocked"},
    "implementation-review": {"accept", "revise", "reject"},
    "remediation-complete": {"complete"},
    "completed-migration": {"complete"},
}
AUTHORITY_RE = re.compile(r"^user-instruction:[a-z0-9][a-z0-9._/-]{0,127}$")
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
HEX40_RE = re.compile(r"^[0-9a-f]{40}$")
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
WORK_UNIT_RE = re.compile(r"^(?:none|phase-[0-6]|remediation-[1-9][0-9]*)$")
SCREENSHOT_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
GENERATED_PARTS = {"node_modules", "__pycache__"}
GENERATED_PREFIXES = ("frontend/dist/", "frontend/public/reviews/")
SECRET_BASENAMES = {"credentials.json", "secrets.json", "secrets.yaml"}
SECRET_SUFFIXES = {".key", ".pem", ".p12", ".pfx"}
SECRET_ASSIGNMENT_RE = re.compile(
    r"(?i)\b(api_key|access_token|client_secret|password|private_key)\b\s*[:=]\s*(.+?)\s*$"
)
PRIVATE_KEY_RE = re.compile(r"-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----")
PLACEHOLDER_RE = re.compile(r"^(?:\$\{[^{}]+\}|<[^<>]+>|example|placeholder|redacted)$", re.I)
TEXT_LIMIT = 1_048_576
SCREENSHOT_LIMIT = 5_242_880
AGGREGATE_LIMIT = 26_214_400


class CheckFailure(Exception):
    pass


def git(root: Path, *args: str, text: bool = True) -> str | bytes:
    run_options: dict[str, Any] = {"text": text}
    if text:
        run_options.update({"encoding": "utf-8", "errors": "replace"})
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        capture_output=True,
        **run_options,
    )
    if completed.returncode != 0:
        stderr = completed.stderr.strip() if text else completed.stderr.decode("utf-8", "replace").strip()
        raise CheckFailure(f"git {' '.join(args)} failed: {stderr}")
    return completed.stdout


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CheckFailure(f"{label}: cannot read valid UTF-8 JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise CheckFailure(f"{label}: top-level value must be an object")
    return value


def exact_keys(value: dict[str, Any], expected: tuple[str, ...], label: str) -> None:
    if set(value) != set(expected):
        missing = sorted(set(expected) - set(value))
        extra = sorted(set(value) - set(expected))
        raise CheckFailure(f"{label}: exact keys required; missing={missing} extra={extra}")


def safe_path(raw: Any) -> str:
    if not isinstance(raw, str) or not raw:
        raise CheckFailure("request path must be a non-empty string")
    if "\\" in raw or raw.startswith("/") or re.match(r"^[A-Za-z]:", raw):
        raise CheckFailure(f"unsafe request path: {raw!r}")
    pure = PurePosixPath(raw)
    if any(part in {"", ".", "..", ".git"} for part in pure.parts):
        raise CheckFailure(f"unsafe request path: {raw!r}")
    if any(character in raw for character in "*?[") or ":(" in raw:
        raise CheckFailure(f"pathspec/glob syntax is forbidden: {raw!r}")
    return pure.as_posix()


def validate_request(raw: dict[str, Any], *, step: str | None = None) -> dict[str, Any]:
    exact_keys(raw, REQUEST_KEYS, "checkpoint request")
    if raw.get("schema_version") != "checkpoint-request-v1":
        raise CheckFailure("checkpoint request schema_version must be checkpoint-request-v1")
    kind = raw.get("kind")
    if kind not in CHECKPOINT_KINDS:
        raise CheckFailure(f"invalid checkpoint kind: {kind!r}")
    if raw.get("outcome") not in OUTCOMES[kind]:
        raise CheckFailure(f"invalid outcome {raw.get('outcome')!r} for {kind}")
    if not isinstance(raw.get("subject"), str) or not SLUG_RE.fullmatch(raw["subject"]):
        raise CheckFailure("subject must be a valid plan/OPT slug")
    if not isinstance(raw.get("revision"), str) or not raw["revision"]:
        raise CheckFailure("revision must be non-empty")
    if not isinstance(raw.get("work_unit"), str) or not WORK_UNIT_RE.fullmatch(raw["work_unit"]):
        raise CheckFailure("work_unit must be none, phase-N, or remediation-N")
    if not isinstance(raw.get("authority"), str) or not AUTHORITY_RE.fullmatch(raw["authority"]):
        raise CheckFailure("authority must use exact user-instruction:<lowercase-token> grammar")
    if not isinstance(raw.get("expected_branch"), str) or not raw["expected_branch"]:
        raise CheckFailure("expected_branch must be non-empty")
    if not isinstance(raw.get("baseline_head"), str) or not HEX40_RE.fullmatch(raw["baseline_head"]):
        raise CheckFailure("baseline_head must be lowercase 40-hex")
    paths = raw.get("paths")
    if not isinstance(paths, list) or not paths:
        raise CheckFailure("paths must be a non-empty array")
    normalized: list[dict[str, Any]] = []
    for index, entry in enumerate(paths):
        if not isinstance(entry, dict):
            raise CheckFailure(f"paths[{index}] must be an object")
        exact_keys(entry, PATH_KEYS, f"paths[{index}]")
        path = safe_path(entry.get("path"))
        operation = entry.get("operation")
        if operation not in {"create", "modify", "delete"}:
            raise CheckFailure(f"paths[{index}] has invalid operation")
        baseline_blob = entry.get("baseline_blob")
        post_sha = entry.get("post_sha256")
        if operation == "create":
            if baseline_blob is not None:
                raise CheckFailure(f"create path {path} requires baseline_blob null")
        elif not isinstance(baseline_blob, str) or not HEX40_RE.fullmatch(baseline_blob):
            raise CheckFailure(f"{operation} path {path} requires lowercase 40-hex baseline_blob")
        if operation == "delete":
            if post_sha is not None:
                raise CheckFailure(f"delete path {path} requires post_sha256 null")
        elif step == "baseline":
            if post_sha is not None:
                raise CheckFailure("baseline request requires every post_sha256 to be null")
        elif not isinstance(post_sha, str) or not HEX64_RE.fullmatch(post_sha):
            raise CheckFailure(f"{operation} path {path} requires lowercase 64-hex post_sha256")
        normalized.append({**entry, "path": path})
    names = [entry["path"] for entry in normalized]
    if names != sorted(names) or len(names) != len(set(names)):
        raise CheckFailure("paths must be lexically sorted and duplicate-free")
    return {**raw, "paths": normalized}


def immutable_request_digest(request: dict[str, Any]) -> str:
    value = {key: request[key] for key in REQUEST_KEYS if key != "paths"}
    value["paths"] = [
        {key: entry[key] for key in ("path", "operation", "baseline_blob")}
        for entry in request["paths"]
    ]
    return sha256_bytes(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def git_dir(root: Path) -> Path:
    raw = str(git(root, "rev-parse", "--git-dir")).strip()
    return (root / raw).resolve() if not Path(raw).is_absolute() else Path(raw).resolve()


def repository_guards(root: Path, expected_branch: str, expected_head: str) -> tuple[str, str]:
    branch = str(git(root, "symbolic-ref", "--quiet", "--short", "HEAD")).strip()
    head = str(git(root, "rev-parse", "HEAD")).strip()
    if branch != expected_branch:
        raise CheckFailure(f"branch mismatch: actual={branch!r} expected={expected_branch!r}")
    if head != expected_head:
        raise CheckFailure(f"HEAD drift: actual={head} expected={expected_head}")
    directory = git_dir(root)
    guards = (
        directory / "MERGE_HEAD",
        directory / "CHERRY_PICK_HEAD",
        directory / "rebase-merge",
        directory / "rebase-apply",
    )
    active = [path.name for path in guards if path.exists()]
    if active:
        raise CheckFailure(f"repository operation in progress: {', '.join(active)}")
    return branch, head


def index_is_empty(root: Path) -> bool:
    return not bytes(git(root, "diff", "--cached", "--name-only", "-z", text=False))


def parse_status(root: Path, excluded: set[str] | None = None) -> list[dict[str, str]]:
    excluded = excluded or set()
    raw = bytes(git(root, "-c", "core.quotepath=false", "status", "--porcelain=v1", "-z", "--untracked-files=all", text=False))
    tokens = raw.split(b"\0")
    result: list[dict[str, str]] = []
    index = 0
    while index < len(tokens) and tokens[index]:
        token = tokens[index].decode("utf-8", "surrogateescape")
        status = token[:2]
        path = token[3:]
        index += 1
        if status[0] in {"R", "C"} and index < len(tokens):
            index += 1
        if path in excluded:
            continue
        full = root / Path(path)
        state = "absent"
        if full.is_file():
            state = sha256_bytes(full.read_bytes())
        elif full.exists():
            state = "non-file"
        result.append({"path": path, "status": status, "state": state})
    return sorted(result, key=lambda item: (item["path"], item["status"], item["state"]))


def tracked_blob(root: Path, commit: str, path: str) -> str | None:
    completed = subprocess.run(
        ["git", "rev-parse", f"{commit}:{path}"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        return None
    value = completed.stdout.strip()
    return value if HEX40_RE.fullmatch(value) else None


def parse_metadata(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    metadata: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            break
        match = re.fullmatch(r"- ([A-Za-z][A-Za-z0-9 /-]*):\s*(.*?)\s*", line)
        if match:
            value = match.group(2).strip()
            if len(value) >= 2 and value.startswith("`") and value.endswith("`"):
                value = value[1:-1].strip()
            metadata[match.group(1)] = value
    return metadata


def subject_metadata(root: Path, subject: str) -> tuple[Path | None, dict[str, str]]:
    for state in ("proposed", "active", "completed"):
        path = root / "docs" / "exec-plans" / state / f"{subject}.md"
        if path.is_file():
            return path, parse_metadata(path)
    opt = root / "docs" / "optimization" / subject / f"{subject}.md"
    if opt.is_file():
        return opt, parse_metadata(opt)
    return None, {}


def validate_authority(root: Path, request: dict[str, Any]) -> None:
    _path, metadata = subject_metadata(root, request["subject"])
    if not metadata:
        raise CheckFailure(f"unknown checkpoint subject: {request['subject']}")
    if metadata.get("Lifecycle schema") == "operating-modes-v2" or "Checkpoint authority" in metadata:
        if metadata.get("Checkpoint authority") != request["authority"]:
            raise CheckFailure("request authority does not match constrained subject authority")
        mode = metadata.get("Checkpoint authority mode")
        kinds = metadata.get("Checkpoint authority kinds", "").split(",")
        if mode not in {"one-shot", "standing"} or request["kind"] not in kinds:
            raise CheckFailure("checkpoint kind is outside constrained subject authority")


def allowed_scope(kind: str, subject: str, path: str) -> bool:
    plan_paths = {
        f"docs/exec-plans/proposed/{subject}.md",
        f"docs/exec-plans/active/{subject}.md",
        f"docs/exec-plans/completed/{subject}.md",
    }
    indexes = {
        "docs/exec-plans/proposed/index.md",
        "docs/exec-plans/active/index.md",
        "docs/exec-plans/completed/index.md",
        "docs/exec-plans/reviews/index.md",
        "docs/exec-plans/roadmap.md",
        "PROGRESS.md",
        "HANDOFF.md",
    }
    review_prefix = f"docs/exec-plans/reviews/{subject}/"
    if kind == "opt-record":
        return path in {
            f"docs/optimization/{subject}/{subject}.md",
            "docs/optimization/index.md",
            "PROGRESS.md",
            "HANDOFF.md",
        } or path.startswith(f"docs/optimization/{subject}/screenshots/")
    if kind == "plan-proposal":
        return path in plan_paths | indexes or path.startswith("docs/optimization/") or path.startswith(review_prefix)
    if kind in {"design-review", "proposal-revision"}:
        return path in plan_paths | indexes or path.startswith(review_prefix) or path.startswith("docs/optimization/")
    if kind in {"activation-recording", "implementation-start", "phase-blocked", "implementation-review", "completed-migration"}:
        return path in plan_paths | indexes or path.startswith(review_prefix)
    if kind in {"phase-exit", "remediation-complete"}:
        return True
    return False


def validate_request_baseline(root: Path, request: dict[str, Any]) -> None:
    status_paths = {item["path"] for item in parse_status(root)}
    for entry in request["paths"]:
        path = entry["path"]
        full = root / Path(path)
        if not allowed_scope(request["kind"], request["subject"], path):
            raise CheckFailure(f"path is outside {request['kind']} scope: {path}")
        if full.exists() and full.is_dir():
            raise CheckFailure(f"request path names a directory: {path}")
        if path in status_paths:
            raise CheckFailure(f"requested path is pre-dirty: {path}")
        actual_blob = tracked_blob(root, request["baseline_head"], path)
        if entry["operation"] == "create":
            if full.exists() or actual_blob is not None:
                raise CheckFailure(f"create path must be absent at baseline: {path}")
        else:
            if actual_blob is None or actual_blob != entry["baseline_blob"]:
                raise CheckFailure(f"baseline blob mismatch: {path}")
            if not full.is_file():
                raise CheckFailure(f"baseline file missing: {path}")


def diff_name_status(root: Path, *, commit: str | None = None) -> dict[str, str]:
    if commit is None:
        args = ("diff", "--cached", "--name-status", "--no-renames", "-z")
    else:
        args = ("diff-tree", "--root", "--no-commit-id", "--name-status", "--no-renames", "-r", "-z", commit)
    tokens = bytes(git(root, *args, text=False)).split(b"\0")
    result: dict[str, str] = {}
    index = 0
    while index + 1 < len(tokens) and tokens[index]:
        status = tokens[index].decode("ascii", "replace")
        path = tokens[index + 1].decode("utf-8", "surrogateescape")
        index += 2
        operation = {"A": "create", "M": "modify", "D": "delete"}.get(status[:1])
        if operation is None:
            raise CheckFailure(f"unsupported diff status {status!r} for {path}")
        result[path] = operation
    return result


def blob_bytes(root: Path, path: str, *, commit: str | None = None) -> bytes:
    spec = f":{path}" if commit is None else f"{commit}:{path}"
    return bytes(git(root, "show", spec, text=False))


def denied_path(path: str) -> str | None:
    pure = PurePosixPath(path)
    name = pure.name.lower()
    if path.startswith(GENERATED_PREFIXES) or any(part in GENERATED_PARTS for part in pure.parts) or name.endswith(".pyc"):
        return "generated output"
    if name == ".env" or (name.startswith(".env.") and name != ".env.example"):
        return "credential path"
    if pure.suffix.lower() in SECRET_SUFFIXES or ".ssh" in pure.parts or name in SECRET_BASENAMES:
        return "credential path"
    return None


def added_lines(root: Path, path: str, *, commit: str | None = None) -> list[str]:
    if commit is None:
        args = ("diff", "--cached", "--unified=0", "--", path)
    else:
        parent = f"{commit}^"
        args = ("diff", "--unified=0", parent, commit, "--", path)
    output = str(git(root, *args))
    return [line[1:] for line in output.splitlines() if line.startswith("+") and not line.startswith("+++")]


def validate_added_secrets(lines: list[str], path: str) -> None:
    for line in lines:
        if PRIVATE_KEY_RE.search(line):
            raise CheckFailure(f"PEM private-key header in staged content: {path}")
        match = SECRET_ASSIGNMENT_RE.search(line)
        if not match:
            continue
        value = match.group(2).strip().rstrip(",").strip().strip("\"'").strip()
        if not PLACEHOLDER_RE.fullmatch(value):
            raise CheckFailure(f"non-placeholder secret assignment in staged content: {path}")


def validate_images_and_content(
    root: Path,
    request: dict[str, Any],
    *,
    commit: str | None = None,
) -> None:
    total = 0
    for entry in request["paths"]:
        path = entry["path"]
        reason = denied_path(path)
        if reason:
            raise CheckFailure(f"{reason} denied: {path}")
        if entry["operation"] == "delete":
            continue
        data = blob_bytes(root, path, commit=commit)
        total += len(data)
        digest = sha256_bytes(data)
        if digest != entry["post_sha256"]:
            raise CheckFailure(f"complete post-image mismatch: {path}")
        suffix = PurePosixPath(path).suffix.lower()
        is_screenshot = (
            suffix in SCREENSHOT_SUFFIXES
            and path.startswith("docs/optimization/")
            and "/screenshots/" in path
            and request["kind"] in {"opt-record", "plan-proposal"}
        )
        if is_screenshot:
            if len(data) > SCREENSHOT_LIMIT:
                raise CheckFailure(f"OPT screenshot exceeds {SCREENSHOT_LIMIT} bytes: {path}")
            continue
        try:
            data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise CheckFailure(f"other binary file denied: {path}") from exc
        if len(data) > TEXT_LIMIT:
            raise CheckFailure(f"text/source file exceeds {TEXT_LIMIT} bytes: {path}")
        validate_added_secrets(added_lines(root, path, commit=commit), path)
    if total > AGGREGATE_LIMIT:
        raise CheckFailure(f"checkpoint aggregate exceeds {AGGREGATE_LIMIT} bytes")


def load_receipt(path: Path, request: dict[str, Any]) -> dict[str, Any]:
    receipt = read_json(path, "baseline receipt")
    expected = {
        "schema_version",
        "request_identity",
        "branch",
        "baseline_head",
        "unrelated_dirty",
    }
    if set(receipt) != expected or receipt.get("schema_version") != "checkpoint-baseline-receipt-v1":
        raise CheckFailure("baseline receipt has invalid schema/keys")
    if receipt.get("request_identity") != immutable_request_digest(request):
        raise CheckFailure("staged/postflight request differs from baseline request")
    if receipt.get("branch") != request["expected_branch"] or receipt.get("baseline_head") != request["baseline_head"]:
        raise CheckFailure("baseline receipt branch/HEAD mismatch")
    if not isinstance(receipt.get("unrelated_dirty"), list):
        raise CheckFailure("baseline receipt unrelated_dirty must be an array")
    return receipt


def baseline(root: Path, request: dict[str, Any]) -> dict[str, Any]:
    if not index_is_empty(root):
        raise CheckFailure("pre-existing staged changes are forbidden")
    branch, head = repository_guards(root, request["expected_branch"], request["baseline_head"])
    validate_authority(root, request)
    validate_request_baseline(root, request)
    return {
        "schema_version": "checkpoint-baseline-receipt-v1",
        "request_identity": immutable_request_digest(request),
        "branch": branch,
        "baseline_head": head,
        "unrelated_dirty": parse_status(root),
    }


def staged(root: Path, request: dict[str, Any], receipt: dict[str, Any]) -> dict[str, Any]:
    repository_guards(root, request["expected_branch"], request["baseline_head"])
    validate_authority(root, request)
    actual = diff_name_status(root)
    expected = {entry["path"]: entry["operation"] for entry in request["paths"]}
    if actual != expected:
        raise CheckFailure(f"staged path/operation set mismatch: actual={actual} expected={expected}")
    current_unrelated = parse_status(root, excluded=set(expected))
    if current_unrelated != receipt["unrelated_dirty"]:
        raise CheckFailure("unrelated dirty path/status/content tuple changed since baseline")
    check = subprocess.run(["git", "diff", "--cached", "--check"], cwd=root, capture_output=True, text=True)
    if check.returncode != 0:
        raise CheckFailure(f"git diff --cached --check failed: {check.stdout}{check.stderr}".strip())
    validate_images_and_content(root, request)
    return {"staged_paths": sorted(actual), "validated": True}


def commit_message(root: Path, commit: str) -> str:
    return str(git(root, "show", "-s", "--format=%B", commit))


def parse_trailers(message: str) -> dict[str, str]:
    seen: dict[str, list[str]] = {key: [] for key in TRAILER_KEYS}
    tang_lines = 0
    for line in message.splitlines():
        match = re.fullmatch(r"(Tang-[A-Za-z-]+):\s*(.*?)\s*", line)
        if not match:
            continue
        tang_lines += 1
        if match.group(1) in seen:
            seen[match.group(1)].append(match.group(2))
        else:
            raise CheckFailure(f"unknown Tang trailer: {match.group(1)}")
    if tang_lines == 0:
        return {}
    duplicates = [key for key, values in seen.items() if len(values) > 1]
    missing = [key for key, values in seen.items() if len(values) != 1]
    if duplicates or missing:
        raise CheckFailure(f"partial/duplicate Tang trailer set: missing={missing} duplicates={duplicates}")
    trailers = {key: values[0] for key, values in seen.items()}
    validate_trailer_values(trailers)
    return trailers


def validate_trailer_values(trailers: dict[str, str]) -> None:
    kind = trailers["Tang-Checkpoint"]
    if kind not in CHECKPOINT_KINDS:
        raise CheckFailure(f"invalid Tang-Checkpoint: {kind!r}")
    if trailers["Tang-Outcome"] not in OUTCOMES[kind]:
        raise CheckFailure(f"Tang-Outcome is invalid for {kind}")
    if not SLUG_RE.fullmatch(trailers["Tang-Subject"]):
        raise CheckFailure("invalid Tang-Subject")
    if not trailers["Tang-Revision"]:
        raise CheckFailure("empty Tang-Revision")
    if not WORK_UNIT_RE.fullmatch(trailers["Tang-Work-Unit"]):
        raise CheckFailure("invalid Tang-Work-Unit")
    if not AUTHORITY_RE.fullmatch(trailers["Tang-Authority"]):
        raise CheckFailure("invalid Tang-Authority")
    if trailers["Tang-Remote-Authority"] != "none":
        raise CheckFailure("Tang-Remote-Authority must be none")


def postflight(
    root: Path,
    request: dict[str, Any],
    receipt: dict[str, Any],
    commitish: str,
) -> dict[str, Any]:
    commit = str(git(root, "rev-parse", f"{commitish}^{{commit}}")).strip()
    head = str(git(root, "rev-parse", "HEAD")).strip()
    if commit != head:
        raise CheckFailure("postflight commit must be current HEAD")
    branch = str(git(root, "symbolic-ref", "--quiet", "--short", "HEAD")).strip()
    if branch != request["expected_branch"]:
        raise CheckFailure("postflight branch mismatch")
    parents = str(git(root, "show", "-s", "--format=%P", commit)).split()
    if len(parents) != 1 or parents[0] != request["baseline_head"]:
        raise CheckFailure("postflight commit parent does not equal baseline_head")
    actual = diff_name_status(root, commit=commit)
    expected = {entry["path"]: entry["operation"] for entry in request["paths"]}
    if actual != expected:
        raise CheckFailure("committed path/operation set differs from request")
    trailers = parse_trailers(commit_message(root, commit))
    expected_trailers = {
        "Tang-Checkpoint": request["kind"],
        "Tang-Subject": request["subject"],
        "Tang-Revision": request["revision"],
        "Tang-Work-Unit": request["work_unit"],
        "Tang-Outcome": request["outcome"],
        "Tang-Authority": request["authority"],
        "Tang-Remote-Authority": "none",
    }
    if trailers != expected_trailers:
        raise CheckFailure("commit trailers do not exactly match request")
    validate_images_and_content(root, request, commit=commit)
    if parse_status(root) != receipt["unrelated_dirty"]:
        raise CheckFailure("unrelated dirty path/status/content tuple changed after commit")
    return {"commit": commit, "validated": True}


def git_history(root: Path) -> list[tuple[str, str]]:
    raw = bytes(git(root, "log", "--format=%H%x00%B%x00", text=False)).split(b"\0")
    result: list[tuple[str, str]] = []
    index = 0
    while index + 1 < len(raw):
        commit = raw[index].strip().decode("ascii", "replace")
        message = raw[index + 1].decode("utf-8", "replace")
        index += 2
        if HEX40_RE.fullmatch(commit):
            result.append((commit, message))
    return result


def commit_paths(root: Path, commit: str) -> set[str]:
    raw = bytes(
        git(
            root,
            "diff-tree",
            "--root",
            "--no-commit-id",
            "--name-only",
            "-r",
            "-z",
            commit,
            text=False,
        )
    )
    return {
        item.decode("utf-8", "surrogateescape")
        for item in raw.split(b"\0")
        if item
    }


def is_strict_ancestor(root: Path, ancestor: str, descendant: str) -> bool:
    if ancestor == descendant:
        return False
    completed = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=root,
        check=False,
        capture_output=True,
    )
    if completed.returncode not in {0, 1}:
        raise CheckFailure(
            f"git merge-base --is-ancestor {ancestor} {descendant} failed: "
            f"{completed.stderr.decode('utf-8', 'replace').strip()}"
        )
    return completed.returncode == 0


def resolve_review_path(root: Path, plan_path: Path, raw_path: str) -> Path | None:
    candidate = (plan_path.parent / raw_path).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    return candidate


def audit_review_chain(
    root: Path,
    plan_path: Path,
    metadata: dict[str, str],
    checkpoints: list[dict[str, str]],
    checkpoint_paths: dict[str, set[str]],
    errors: list[str],
) -> None:
    subject = metadata.get("Plan slug", "")
    revision = metadata.get("Revision", "")
    by_commit = {item["commit"]: item for item in checkpoints}
    declarations: list[tuple[str, str, str | None, str, str, set[str]]] = []

    raw_design = metadata.get("Design reviews", "none")
    if raw_design != "none":
        for item in raw_design.split(", "):
            parts = item.rsplit("@", 2)
            if len(parts) == 3:
                declarations.append(
                    (parts[0], "design-review", None, parts[1], parts[2], {"plan-proposal", "proposal-revision"})
                )

    raw_implementation = metadata.get("Implementation reviews", "none")
    if raw_implementation != "none":
        for item in raw_implementation.split(", "):
            parts = item.rsplit("@", 2)
            if len(parts) == 3 and HEX40_RE.fullmatch(parts[2]):
                declarations.append(
                    (
                        parts[0],
                        "implementation-review",
                        parts[2],
                        parts[1],
                        revision,
                        {"phase-exit", "remediation-complete"},
                    )
                )

    for raw_path, review_kind, declared_target, verdict, target_revision, target_kinds in declarations:
        review_path = resolve_review_path(root, plan_path, raw_path)
        if review_path is None or not review_path.is_file():
            errors.append(f"{plan_path.relative_to(root)}: review path unavailable for checkpoint audit: {raw_path}")
            continue
        review_relative = review_path.relative_to(root).as_posix()
        review_metadata = parse_metadata(review_path)
        target = review_metadata.get("Review target commit", "")
        if not HEX40_RE.fullmatch(target):
            errors.append(f"{review_relative}: missing valid Review target commit")
            continue
        if declared_target is not None and target != declared_target:
            errors.append(f"{review_relative}: Review target commit differs from plan declaration")

        review_commits = [
            item
            for item in checkpoints
            if item["Tang-Checkpoint"] == review_kind
            and item["Tang-Subject"] == subject
            and review_relative in checkpoint_paths[item["commit"]]
        ]
        if len(review_commits) != 1:
            errors.append(
                f"{review_relative}: expected exactly one {review_kind} checkpoint containing the review; "
                f"found {len(review_commits)}"
            )
            continue
        review_commit = review_commits[0]
        if review_commit["Tang-Revision"] != target_revision or review_commit["Tang-Outcome"] != verdict:
            errors.append(f"{review_relative}: review checkpoint subject/revision/outcome mismatch")

        target_checkpoint = by_commit.get(target)
        if target_checkpoint is None:
            errors.append(f"{review_relative}: Review target commit is not a durable checkpoint")
            continue
        if (
            target_checkpoint["Tang-Checkpoint"] not in target_kinds
            or target_checkpoint["Tang-Subject"] != subject
            or target_checkpoint["Tang-Revision"] != target_revision
        ):
            errors.append(f"{review_relative}: Review target checkpoint kind/subject/revision mismatch")
        if not is_strict_ancestor(root, target, review_commit["commit"]):
            errors.append(f"{review_relative}: Review target commit is not a strict ancestor of review checkpoint")


def audit(root: Path, legacy_tolerated: bool) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    checkpoints: list[dict[str, str]] = []
    for commit, message in git_history(root):
        try:
            trailers = parse_trailers(message)
        except CheckFailure as exc:
            errors.append(f"{commit}: {exc}")
            continue
        if not trailers:
            if not legacy_tolerated:
                warnings.append(f"{commit}: trailer-less history")
            continue
        checkpoints.append({"commit": commit, **trailers})

    one_shot_uses: dict[tuple[str, str], list[str]] = {}
    checkpoint_paths = {item["commit"]: commit_paths(root, item["commit"]) for item in checkpoints}
    for item in checkpoints:
        _path, metadata = subject_metadata(root, item["Tang-Subject"])
        if not metadata:
            errors.append(f"{item['commit']}: unknown checkpoint subject")
            continue
        if metadata.get("Lifecycle schema") == "operating-modes-v2" or "Checkpoint authority" in metadata:
            authority = metadata.get("Checkpoint authority")
            mode = metadata.get("Checkpoint authority mode")
            kinds = metadata.get("Checkpoint authority kinds", "").split(",")
            if item["Tang-Authority"] != authority or item["Tang-Checkpoint"] not in kinds:
                errors.append(f"{item['commit']}: checkpoint escapes constrained subject authority")
            if mode == "one-shot":
                one_shot_uses.setdefault((item["Tang-Authority"], item["Tang-Subject"]), []).append(item["commit"])
    for key, commits in one_shot_uses.items():
        if len(commits) > 1:
            errors.append(f"one-shot authority reused for {key[1]}: {', '.join(commits)}")

    plan_root = root / "docs" / "exec-plans"
    for state in ("proposed", "active", "completed"):
        for path in sorted((plan_root / state).glob("*.md")):
            if path.name == "index.md":
                continue
            metadata = parse_metadata(path)
            if metadata.get("Lifecycle schema") != "operating-modes-v2":
                continue
            audit_review_chain(root, path, metadata, checkpoints, checkpoint_paths, errors)
            expected = metadata.get("Expected checkpoint kind", "none")
            if expected == "none":
                continue
            subject = metadata.get("Plan slug", "")
            revision = metadata.get("Revision", "")
            matching = [
                item for item in checkpoints
                if item["Tang-Subject"] == subject and item["Tang-Revision"] == revision
            ]
            if not matching:
                errors.append(f"{path.relative_to(root)}: missing expected v2 checkpoint {expected}")
            elif matching[0]["Tang-Checkpoint"] != expected:
                errors.append(
                    f"{path.relative_to(root)}: latest checkpoint={matching[0]['Tang-Checkpoint']} expected={expected}"
                )
    return {
        "checkpoints": len(checkpoints),
        "warnings": warnings,
        "errors": errors,
        "passed": not errors,
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--root", type=Path, required=True)
    result.add_argument("--mode", choices=("preflight", "postflight", "audit"), required=True)
    result.add_argument("--step", choices=("baseline", "staged"))
    result.add_argument("--request", type=Path)
    result.add_argument("--baseline-receipt", type=Path)
    result.add_argument("--commit", default="HEAD")
    result.add_argument("--legacy-tolerated", action="store_true")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    root = args.root.resolve()
    try:
        if not (root / ".git").exists() and not str(git(root, "rev-parse", "--git-dir")).strip():
            raise CheckFailure("root is not a Git repository")
        if args.mode == "audit":
            result = audit(root, args.legacy_tolerated)
            print(json.dumps(result, sort_keys=True))
            return 0 if result["passed"] else 1
        if args.request is None:
            raise CheckFailure("--request is required")
        request = validate_request(read_json(args.request, "checkpoint request"), step=args.step)
        if args.mode == "preflight" and args.step == "baseline":
            result = baseline(root, request)
            print(json.dumps(result, sort_keys=True))
            return 0
        elif args.mode == "preflight" and args.step == "staged":
            if args.baseline_receipt is None:
                raise CheckFailure("staged preflight requires --baseline-receipt")
            result = staged(root, request, load_receipt(args.baseline_receipt, request))
        elif args.mode == "postflight":
            if args.baseline_receipt is None:
                raise CheckFailure("postflight requires --baseline-receipt")
            result = postflight(root, request, load_receipt(args.baseline_receipt, request), args.commit)
        else:
            raise CheckFailure("invalid mode/step combination")
        print(json.dumps({"errors": [], "passed": True, **result}, sort_keys=True))
        return 0
    except (CheckFailure, OSError, UnicodeDecodeError) as exc:
        print(json.dumps({"errors": [str(exc)], "passed": False}, sort_keys=True))
        return 1


if __name__ == "__main__":
    sys.exit(main())
