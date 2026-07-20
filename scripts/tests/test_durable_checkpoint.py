from __future__ import annotations

import hashlib
import json
import os
import runpy
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHECKER = PROJECT_ROOT / "scripts" / "check-durable-checkpoint.py"
AUTHORITY = "user-instruction:fixture-checkpoint"


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
    )


def write(path: Path, data: str | bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, bytes):
        path.write_bytes(data)
    else:
        path.write_text(data, encoding="utf-8")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class DurableCheckpointTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.root = self.base / "repo"
        self.root.mkdir()
        commands = (
            ["git", "init", "-q"],
            ["git", "config", "user.name", "Fixture"],
            ["git", "config", "user.email", "fixture@example.com"],
            ["git", "branch", "-M", "fixture"],
        )
        for command in commands:
            completed = run(command, self.root)
            self.assertEqual(completed.returncode, 0, completed.stderr)
        self.write_plan(mode="standing", kinds="phase-exit")
        write(self.root / "docs/work.md", "baseline\n")
        self.git("add", "--", "docs/exec-plans/active/demo-plan.md", "docs/work.md")
        self.git("commit", "-qm", "fixture baseline")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def git(self, *args: str) -> str:
        completed = run(["git", *args], self.root)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return completed.stdout.strip()

    def write_plan(
        self,
        *,
        mode: str = "standing",
        kinds: str = "phase-exit",
        expected: str = "none",
        authority: str = AUTHORITY,
    ) -> None:
        write(
            self.root / "docs/exec-plans/active/demo-plan.md",
            f"""# Demo

- Lifecycle schema: `operating-modes-v2`
- Plan slug: `demo-plan`
- Revision: `r1`
- Checkpoint authority: `{authority}`
- Checkpoint authority mode: {mode}
- Checkpoint authority kinds: {kinds}
- Expected checkpoint kind: {expected}

## Body
""",
        )

    def write_review_plan(self, *, design_reviews: str, kinds: str) -> None:
        write(
            self.root / "docs/exec-plans/active/demo-plan.md",
            f"""# Demo

- Lifecycle schema: `operating-modes-v2`
- Plan slug: `demo-plan`
- Revision: `r1`
- Design reviews: {design_reviews}
- Implementation reviews: none
- Checkpoint authority: `{AUTHORITY}`
- Checkpoint authority mode: standing
- Checkpoint authority kinds: {kinds}
- Expected checkpoint kind: none

## Body
""",
        )

    def create_design_review_chain(self, *, target_kind: str = "plan-proposal") -> tuple[str, str]:
        kinds = f"{target_kind},design-review"
        self.write_review_plan(design_reviews="none", kinds=kinds)
        self.git("add", "--", "docs/exec-plans/active/demo-plan.md")
        target_request = self.request("docs/exec-plans/active/demo-plan.md", kind=target_kind)
        target_request["work_unit"] = "phase-1" if target_kind == "phase-exit" else "none"
        target_request["outcome"] = "complete"
        target = self.commit_checkpoint(target_request)

        review_relative = "docs/exec-plans/reviews/demo-plan/review-001.md"
        write(
            self.root / review_relative,
            f"""# Review

- Review target commit: `{target}`

## Findings
""",
        )
        self.write_review_plan(
            design_reviews="../reviews/demo-plan/review-001.md@approve@r1",
            kinds=kinds,
        )
        self.git("add", "--", "docs/exec-plans/active/demo-plan.md", review_relative)
        review_request = self.request(
            review_relative,
            operation="create",
            kind="design-review",
            outcome="approve",
        )
        review_request["work_unit"] = "none"
        review = self.commit_checkpoint(review_request)
        return target, review

    def request(
        self,
        path: str = "docs/work.md",
        *,
        operation: str = "modify",
        kind: str = "phase-exit",
        outcome: str = "complete",
        subject: str = "demo-plan",
        authority: str = AUTHORITY,
        baseline_blob: str | None = None,
        post_sha256: str | None = None,
        baseline_head: str | None = None,
        expected_branch: str = "fixture",
    ) -> dict[str, object]:
        head = baseline_head or self.git("rev-parse", "HEAD")
        if operation != "create" and baseline_blob is None:
            baseline_blob = self.git("rev-parse", f"{head}:{path}")
        return {
            "schema_version": "checkpoint-request-v1",
            "kind": kind,
            "subject": subject,
            "revision": "r1",
            "work_unit": "phase-1" if kind in {"phase-exit", "phase-blocked"} else "none",
            "outcome": outcome,
            "authority": authority,
            "expected_branch": expected_branch,
            "baseline_head": head,
            "paths": [
                {
                    "path": path,
                    "operation": operation,
                    "baseline_blob": baseline_blob,
                    "post_sha256": post_sha256,
                }
            ],
        }

    def json_path(self, name: str, value: dict[str, object]) -> Path:
        path = self.base / name
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def checker(self, *args: str) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
        completed = run(["python", str(CHECKER), "--root", str(self.root), *args], PROJECT_ROOT)
        payload = json.loads(completed.stdout.splitlines()[0])
        return completed, payload

    def baseline(self, request: dict[str, object]) -> tuple[Path, dict[str, object]]:
        path = self.json_path("baseline-request.json", request)
        completed, payload = self.checker(
            "--mode", "preflight", "--step", "baseline", "--request", str(path)
        )
        self.assertEqual(completed.returncode, 0, payload)
        receipt = self.json_path("receipt.json", payload)
        return receipt, payload

    def staged(
        self,
        request: dict[str, object],
        receipt: Path,
    ) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
        path = self.json_path("staged-request.json", request)
        return self.checker(
            "--mode",
            "preflight",
            "--step",
            "staged",
            "--request",
            str(path),
            "--baseline-receipt",
            str(receipt),
        )

    def prepare_modify(self, content: bytes = b"changed\n") -> tuple[dict[str, object], Path]:
        baseline_request = self.request()
        receipt, _payload = self.baseline(baseline_request)
        write(self.root / "docs/work.md", content)
        self.git("add", "--", "docs/work.md")
        staged_request = self.request(post_sha256=digest(content))
        return staged_request, receipt

    def commit_checkpoint(self, request: dict[str, object]) -> str:
        trailers = (
            ("Tang-Checkpoint", request["kind"]),
            ("Tang-Subject", request["subject"]),
            ("Tang-Revision", request["revision"]),
            ("Tang-Work-Unit", request["work_unit"]),
            ("Tang-Outcome", request["outcome"]),
            ("Tang-Authority", request["authority"]),
            ("Tang-Remote-Authority", "none"),
        )
        command = ["commit", "-m", "fixture checkpoint"]
        for key, value in trailers:
            command.extend(["-m", f"{key}: {value}"])
        self.git(*command)
        return self.git("rev-parse", "HEAD")

    def assert_error(self, completed: subprocess.CompletedProcess[str], payload: dict[str, object], needle: str) -> None:
        self.assertNotEqual(completed.returncode, 0)
        self.assertTrue(any(needle in str(item) for item in payload["errors"]), payload)

    def test_baseline_and_staged_preflight_pass(self) -> None:
        request, receipt = self.prepare_modify()
        completed, payload = self.staged(request, receipt)
        self.assertEqual(completed.returncode, 0, payload)

    def test_preexisting_staged_change_aborts(self) -> None:
        write(self.root / "other.md", "other\n")
        self.git("add", "--", "other.md")
        path = self.json_path("request.json", self.request())
        completed, payload = self.checker("--mode", "preflight", "--step", "baseline", "--request", str(path))
        self.assert_error(completed, payload, "pre-existing staged")

    def test_detached_head_aborts(self) -> None:
        self.git("checkout", "--detach", "-q")
        path = self.json_path("request.json", self.request(expected_branch="fixture"))
        completed, payload = self.checker("--mode", "preflight", "--step", "baseline", "--request", str(path))
        self.assertNotEqual(completed.returncode, 0)

    def test_repository_operation_guards_abort(self) -> None:
        git_dir = Path(self.git("rev-parse", "--git-dir"))
        if not git_dir.is_absolute():
            git_dir = self.root / git_dir
        for marker in ("MERGE_HEAD", "CHERRY_PICK_HEAD"):
            write(git_dir / marker, self.git("rev-parse", "HEAD") + "\n")
            path = self.json_path("request.json", self.request())
            completed, payload = self.checker("--mode", "preflight", "--step", "baseline", "--request", str(path))
            self.assert_error(completed, payload, "operation in progress")
            (git_dir / marker).unlink()
        (git_dir / "rebase-merge").mkdir()
        path = self.json_path("request.json", self.request())
        completed, payload = self.checker("--mode", "preflight", "--step", "baseline", "--request", str(path))
        self.assert_error(completed, payload, "operation in progress")

    def test_predirty_requested_path_aborts(self) -> None:
        write(self.root / "docs/work.md", "dirty\n")
        path = self.json_path("request.json", self.request())
        completed, payload = self.checker("--mode", "preflight", "--step", "baseline", "--request", str(path))
        self.assert_error(completed, payload, "pre-dirty")

    def test_preexisting_create_path_aborts(self) -> None:
        write(self.root / "docs/new.md", "exists\n")
        request = self.request("docs/new.md", operation="create", baseline_blob=None)
        path = self.json_path("request.json", request)
        completed, payload = self.checker("--mode", "preflight", "--step", "baseline", "--request", str(path))
        self.assert_error(completed, payload, "pre-dirty")

    def test_baseline_blob_mismatch_aborts(self) -> None:
        request = self.request(baseline_blob="0" * 40)
        path = self.json_path("request.json", request)
        completed, payload = self.checker("--mode", "preflight", "--step", "baseline", "--request", str(path))
        self.assert_error(completed, payload, "baseline blob mismatch")

    def test_branch_and_head_mismatch_abort(self) -> None:
        request = self.request(expected_branch="wrong")
        path = self.json_path("request.json", request)
        completed, payload = self.checker("--mode", "preflight", "--step", "baseline", "--request", str(path))
        self.assert_error(completed, payload, "branch mismatch")
        request = self.request(baseline_head="0" * 40, baseline_blob="0" * 40)
        path = self.json_path("request2.json", request)
        completed, payload = self.checker("--mode", "preflight", "--step", "baseline", "--request", str(path))
        self.assert_error(completed, payload, "HEAD drift")

    def test_complete_post_image_mismatch_aborts(self) -> None:
        request, receipt = self.prepare_modify()
        request["paths"][0]["post_sha256"] = "0" * 64  # type: ignore[index]
        completed, payload = self.staged(request, receipt)
        self.assert_error(completed, payload, "post-image mismatch")

    def test_staged_operation_and_extra_path_mismatch_abort(self) -> None:
        baseline_request = self.request()
        receipt, _ = self.baseline(baseline_request)
        self.git("rm", "-q", "--", "docs/work.md")
        request = self.request(post_sha256=digest(b"changed\n"), baseline_head=baseline_request["baseline_head"])
        completed, payload = self.staged(request, receipt)
        self.assert_error(completed, payload, "path/operation set mismatch")

    def test_head_drift_between_baseline_and_staged_aborts(self) -> None:
        baseline_request = self.request()
        receipt, _ = self.baseline(baseline_request)
        write(self.root / "unrelated.md", "commit\n")
        self.git("add", "--", "unrelated.md")
        self.git("commit", "-qm", "drift")
        write(self.root / "docs/work.md", "changed\n")
        self.git("add", "--", "docs/work.md")
        request = self.request(post_sha256=digest(b"changed\n"), baseline_head=baseline_request["baseline_head"])
        completed, payload = self.staged(request, receipt)
        self.assert_error(completed, payload, "HEAD drift")

    def test_unrelated_dirty_tuple_unchanged_passes_and_changed_fails(self) -> None:
        write(self.root / "notes.txt", "unrelated\n")
        request, receipt = self.prepare_modify()
        completed, payload = self.staged(request, receipt)
        self.assertEqual(completed.returncode, 0, payload)
        write(self.root / "notes.txt", "mutated\n")
        completed, payload = self.staged(request, receipt)
        self.assert_error(completed, payload, "unrelated dirty")

    def test_secret_assignment_and_pem_header_abort(self) -> None:
        for content, needle in (
            (b"api_key = real-secret\n", "secret assignment"),
            (b"-----BEGIN PRIVATE KEY-----\n", "PEM"),
        ):
            with self.subTest(content=content):
                self.git("restore", "--staged", "--", "docs/work.md") if run(["git", "diff", "--cached", "--quiet"], self.root).returncode else None
                self.git("restore", "--", "docs/work.md")
                request, receipt = self.prepare_modify(content)
                completed, payload = self.staged(request, receipt)
                self.assert_error(completed, payload, needle)

    def test_placeholder_and_gate_token_prose_pass(self) -> None:
        content = b"api_key = ${FIXTURE_KEY}\ngate-token is governance prose\n"
        request, receipt = self.prepare_modify(content)
        completed, payload = self.staged(request, receipt)
        self.assertEqual(completed.returncode, 0, payload)

    def test_denied_credential_and_generated_paths_abort(self) -> None:
        for path_name, needle in ((".env", "credential"), ("frontend/dist/out.txt", "generated")):
            with self.subTest(path=path_name):
                request = self.request(path_name, operation="create", baseline_blob=None)
                receipt, _ = self.baseline(request)
                write(self.root / path_name, "value\n")
                self.git("add", "--", path_name)
                request = self.request(
                    path_name,
                    operation="create",
                    baseline_blob=None,
                    post_sha256=digest(b"value\n"),
                    baseline_head=request["baseline_head"],
                )
                completed, payload = self.staged(request, receipt)
                self.assert_error(completed, payload, needle)
                self.git("restore", "--staged", "--", path_name)
                os.remove(self.root / path_name)

    def test_harmless_token_filename_passes(self) -> None:
        request = self.request("docs/gate-token.md", operation="create", baseline_blob=None)
        receipt, _ = self.baseline(request)
        content = b"harmless\n"
        write(self.root / "docs/gate-token.md", content)
        self.git("add", "--", "docs/gate-token.md")
        request = self.request(
            "docs/gate-token.md",
            operation="create",
            baseline_blob=None,
            post_sha256=digest(content),
            baseline_head=request["baseline_head"],
        )
        completed, payload = self.staged(request, receipt)
        self.assertEqual(completed.returncode, 0, payload)

    def test_text_size_limit_aborts(self) -> None:
        content = b"a" * 1_048_577
        request, receipt = self.prepare_modify(content)
        completed, payload = self.staged(request, receipt)
        self.assert_error(completed, payload, "exceeds 1048576")

    def test_other_binary_aborts(self) -> None:
        request, receipt = self.prepare_modify(b"\x00\xff\x00")
        completed, payload = self.staged(request, receipt)
        self.assert_error(completed, payload, "binary")

    def test_live_opt_screenshot_size_fixture_passes(self) -> None:
        source = PROJECT_ROOT / "docs/optimization/2026-07-19-review-ui-and-trader-editing/screenshots/2026-07-19-review-ui-reference-v1.png"
        self.assertEqual(source.stat().st_size, 1_688_940)
        subject = "opt-demo"
        self.write_plan()  # retain plan subject independently
        opt = self.root / f"docs/optimization/{subject}/{subject}.md"
        write(
            opt,
            f"# OPT\n\n- Checkpoint authority: `{AUTHORITY}`\n- Checkpoint authority mode: standing\n- Checkpoint authority kinds: opt-record\n",
        )
        self.git("add", "--", opt.relative_to(self.root).as_posix())
        self.git("commit", "-qm", "add opt")
        relative = f"docs/optimization/{subject}/screenshots/reference.png"
        request = self.request(relative, operation="create", kind="opt-record", subject=subject, baseline_blob=None)
        request["work_unit"] = "none"
        receipt, _ = self.baseline(request)
        data = source.read_bytes()
        write(self.root / relative, data)
        self.git("add", "--", relative)
        request = self.request(
            relative,
            operation="create",
            kind="opt-record",
            subject=subject,
            baseline_blob=None,
            post_sha256=digest(data),
            baseline_head=request["baseline_head"],
        )
        request["work_unit"] = "none"
        completed, payload = self.staged(request, receipt)
        self.assertEqual(completed.returncode, 0, payload)

    def test_oversized_opt_screenshot_aborts(self) -> None:
        subject = "opt-demo"
        opt = self.root / f"docs/optimization/{subject}/{subject}.md"
        write(opt, f"# OPT\n\n- Checkpoint authority: `{AUTHORITY}`\n- Checkpoint authority mode: standing\n- Checkpoint authority kinds: opt-record\n")
        self.git("add", "--", opt.relative_to(self.root).as_posix())
        self.git("commit", "-qm", "add opt")
        relative = f"docs/optimization/{subject}/screenshots/large.png"
        request = self.request(relative, operation="create", kind="opt-record", subject=subject, baseline_blob=None)
        request["work_unit"] = "none"
        receipt, _ = self.baseline(request)
        data = b"x" * 5_242_881
        write(self.root / relative, data)
        self.git("add", "--", relative)
        request = self.request(relative, operation="create", kind="opt-record", subject=subject, baseline_blob=None, post_sha256=digest(data), baseline_head=request["baseline_head"])
        request["work_unit"] = "none"
        completed, payload = self.staged(request, receipt)
        self.assert_error(completed, payload, "exceeds 5242880")

    def test_aggregate_size_limit_aborts_at_exact_boundary_plus_one(self) -> None:
        subject = "opt-demo"
        opt = self.root / f"docs/optimization/{subject}/{subject}.md"
        write(opt, f"# OPT\n\n- Checkpoint authority: `{AUTHORITY}`\n- Checkpoint authority mode: standing\n- Checkpoint authority kinds: opt-record\n")
        self.git("add", "--", opt.relative_to(self.root).as_posix())
        self.git("commit", "-qm", "add opt")
        head = self.git("rev-parse", "HEAD")
        sizes = [5_000_000] * 5 + [1_214_401]
        baseline_entries = []
        for index, size in enumerate(sizes):
            relative = f"docs/optimization/{subject}/screenshots/{index}.png"
            baseline_entries.append({"path": relative, "operation": "create", "baseline_blob": None, "post_sha256": None})
        base_request = self.request(kind="opt-record", subject=subject, baseline_head=head)
        base_request["work_unit"] = "none"
        base_request["paths"] = baseline_entries
        receipt, _ = self.baseline(base_request)
        entries = []
        for index, size in enumerate(sizes):
            relative = f"docs/optimization/{subject}/screenshots/{index}.png"
            data = bytes([65 + index]) * size
            write(self.root / relative, data)
            entries.append({"path": relative, "operation": "create", "baseline_blob": None, "post_sha256": digest(data)})
        self.git("add", "--", *[entry["path"] for entry in entries])
        staged_request = dict(base_request)
        staged_request["paths"] = entries
        completed, payload = self.staged(staged_request, receipt)
        self.assert_error(completed, payload, "aggregate exceeds 26214400")

    def test_valid_checkpoint_postflight_passes(self) -> None:
        request, receipt = self.prepare_modify()
        completed, payload = self.staged(request, receipt)
        self.assertEqual(completed.returncode, 0, payload)
        commit = self.commit_checkpoint(request)
        path = self.json_path("post-request.json", request)
        completed, payload = self.checker(
            "--mode", "postflight", "--request", str(path), "--baseline-receipt", str(receipt), "--commit", commit
        )
        self.assertEqual(completed.returncode, 0, payload)

    def test_postflight_rejects_missing_or_mismatched_trailers(self) -> None:
        request, receipt = self.prepare_modify()
        self.git("commit", "-qm", "missing trailers")
        path = self.json_path("post-request.json", request)
        completed, payload = self.checker("--mode", "postflight", "--request", str(path), "--baseline-receipt", str(receipt))
        self.assert_error(completed, payload, "trailers")

    def test_postflight_rejects_unrelated_dirty_content_drift(self) -> None:
        write(self.root / "notes.txt", "baseline unrelated\n")
        request, receipt = self.prepare_modify()
        completed, payload = self.staged(request, receipt)
        self.assertEqual(completed.returncode, 0, payload)
        self.commit_checkpoint(request)
        write(self.root / "notes.txt", "changed unrelated\n")
        path = self.json_path("post-request.json", request)
        completed, payload = self.checker("--mode", "postflight", "--request", str(path), "--baseline-receipt", str(receipt))
        self.assert_error(completed, payload, "unrelated dirty")

    def test_staged_request_cannot_change_immutable_baseline_fields(self) -> None:
        request, receipt = self.prepare_modify()
        request["revision"] = "r2"
        completed, payload = self.staged(request, receipt)
        self.assert_error(completed, payload, "differs from baseline request")

    def test_legacy_tolerated_audit_passes_trailerless_history(self) -> None:
        completed, payload = self.checker("--mode", "audit", "--legacy-tolerated")
        self.assertEqual(completed.returncode, 0, payload)

    def test_audit_rejects_partial_and_invalid_trailers(self) -> None:
        write(self.root / "partial.md", "x\n")
        self.git("add", "--", "partial.md")
        self.git("commit", "-m", "partial", "-m", "Tang-Checkpoint: phase-exit")
        completed, payload = self.checker("--mode", "audit", "--legacy-tolerated")
        self.assert_error(completed, payload, "partial/duplicate")

    def test_audit_rejects_invalid_checkpoint_kind(self) -> None:
        write(self.root / "invalid.md", "x\n")
        self.git("add", "--", "invalid.md")
        command = ["commit", "-m", "invalid"]
        values = {
            "Tang-Checkpoint": "not-a-kind",
            "Tang-Subject": "demo-plan",
            "Tang-Revision": "r1",
            "Tang-Work-Unit": "phase-1",
            "Tang-Outcome": "complete",
            "Tang-Authority": AUTHORITY,
            "Tang-Remote-Authority": "none",
        }
        for key, value in values.items():
            command.extend(["-m", f"{key}: {value}"])
        self.git(*command)
        completed, payload = self.checker("--mode", "audit", "--legacy-tolerated")
        self.assert_error(completed, payload, "invalid Tang-Checkpoint")

    def test_audit_rejects_outcome_kind_mismatch(self) -> None:
        write(self.root / "invalid.md", "x\n")
        self.git("add", "--", "invalid.md")
        request = self.request(outcome="blocked")
        request["outcome"] = "blocked"
        self.commit_checkpoint(request)
        completed, payload = self.checker("--mode", "audit", "--legacy-tolerated")
        self.assert_error(completed, payload, "Tang-Outcome is invalid")

    def test_plan_proposal_scope_rejects_runtime_path(self) -> None:
        self.write_plan(kinds="plan-proposal")
        self.git("add", "--", "docs/exec-plans/active/demo-plan.md")
        self.git("commit", "-qm", "proposal authority")
        write(self.root / "frontend/src/App.jsx", "export default null\n")
        self.git("add", "--", "frontend/src/App.jsx")
        self.git("commit", "-qm", "runtime baseline")
        request = self.request("frontend/src/App.jsx", kind="plan-proposal")
        request["work_unit"] = "none"
        request["outcome"] = "complete"
        path = self.json_path("request.json", request)
        completed, payload = self.checker("--mode", "preflight", "--step", "baseline", "--request", str(path))
        self.assert_error(completed, payload, "outside plan-proposal scope")

    def test_all_eleven_scope_kinds_are_fixture_pinned(self) -> None:
        allowed_scope = runpy.run_path(str(CHECKER))["allowed_scope"]
        subject = "demo-plan"
        positives = {
            "opt-record": "docs/optimization/demo-plan/demo-plan.md",
            "plan-proposal": "docs/exec-plans/proposed/demo-plan.md",
            "design-review": "docs/exec-plans/reviews/demo-plan/review-001.md",
            "proposal-revision": "docs/exec-plans/proposed/demo-plan.md",
            "activation-recording": "docs/exec-plans/active/demo-plan.md",
            "implementation-start": "docs/exec-plans/active/demo-plan.md",
            "phase-exit": "frontend/src/App.jsx",
            "phase-blocked": "docs/exec-plans/reviews/demo-plan/evidence/blocker.md",
            "implementation-review": "docs/exec-plans/reviews/demo-plan/implementation-review-001.md",
            "remediation-complete": "backend/app/main.py",
            "completed-migration": "docs/exec-plans/completed/demo-plan.md",
        }
        self.assertEqual(set(positives), {
            "opt-record", "plan-proposal", "design-review", "proposal-revision", "activation-recording",
            "implementation-start", "phase-exit", "phase-blocked", "implementation-review",
            "remediation-complete", "completed-migration",
        })
        for kind, path in positives.items():
            with self.subTest(kind=kind):
                self.assertTrue(allowed_scope(kind, subject, path))
        self.assertFalse(allowed_scope("opt-record", subject, "frontend/src/App.jsx"))

    def test_audit_rejects_one_shot_reuse(self) -> None:
        self.write_plan(mode="one-shot", kinds="phase-exit")
        self.git("add", "--", "docs/exec-plans/active/demo-plan.md")
        self.git("commit", "-qm", "one shot metadata")
        for index in (1, 2):
            write(self.root / "docs/work.md", f"checkpoint {index}\n")
            self.git("add", "--", "docs/work.md")
            request = self.request()
            self.commit_checkpoint(request)
        completed, payload = self.checker("--mode", "audit", "--legacy-tolerated")
        self.assert_error(completed, payload, "one-shot authority reused")

    def test_audit_rejects_standing_kind_escape(self) -> None:
        write(self.root / "docs/work.md", "escape\n")
        self.git("add", "--", "docs/work.md")
        request = self.request(kind="design-review", outcome="approve")
        request["work_unit"] = "none"
        self.commit_checkpoint(request)
        completed, payload = self.checker("--mode", "audit", "--legacy-tolerated")
        self.assert_error(completed, payload, "escapes constrained")

    def test_audit_rejects_missing_expected_v2_checkpoint(self) -> None:
        self.write_plan(expected="phase-exit")
        self.git("add", "--", "docs/exec-plans/active/demo-plan.md")
        self.git("commit", "-qm", "expected claim")
        completed, payload = self.checker("--mode", "audit", "--legacy-tolerated")
        self.assert_error(completed, payload, "missing expected v2 checkpoint")

    def test_audit_accepts_review_target_checkpoint_ancestry(self) -> None:
        self.create_design_review_chain()
        completed, payload = self.checker("--mode", "audit", "--legacy-tolerated")
        self.assertEqual(completed.returncode, 0, payload)

    def test_audit_rejects_review_target_checkpoint_kind_mismatch(self) -> None:
        self.create_design_review_chain(target_kind="phase-exit")
        completed, payload = self.checker("--mode", "audit", "--legacy-tolerated")
        self.assert_error(completed, payload, "target checkpoint kind/subject/revision mismatch")

    def test_audit_rejects_review_without_checkpoint_commit(self) -> None:
        self.write_review_plan(
            design_reviews="../reviews/demo-plan/review-001.md@approve@r1",
            kinds="plan-proposal,design-review",
        )
        write(
            self.root / "docs/exec-plans/reviews/demo-plan/review-001.md",
            "# Review\n\n- Review target commit: `" + self.git("rev-parse", "HEAD") + "`\n",
        )
        self.git("add", "--", "docs/exec-plans/active/demo-plan.md", "docs/exec-plans/reviews/demo-plan/review-001.md")
        self.git("commit", "-qm", "uncheckpointed review")
        completed, payload = self.checker("--mode", "audit", "--legacy-tolerated")
        self.assert_error(completed, payload, "expected exactly one design-review checkpoint")

    def test_checker_is_read_only(self) -> None:
        request = self.request()
        path = self.json_path("request.json", request)
        before = self.git("status", "--porcelain=v1")
        completed, _payload = self.checker("--mode", "preflight", "--step", "baseline", "--request", str(path))
        self.assertEqual(completed.returncode, 0)
        after = self.git("status", "--porcelain=v1")
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
