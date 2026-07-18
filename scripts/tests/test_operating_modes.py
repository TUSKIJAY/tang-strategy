from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHECKER = PROJECT_ROOT / "scripts" / "check-operating-modes.py"
HARNESS_CHECKER = PROJECT_ROOT / "scripts" / "check-project-harness.py"

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


def write(root: Path, relative: str, text: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, check=False, capture_output=True, text=True, timeout=30)


def state_block(status: str, phase: str, phase_state: str, next_gate: str) -> str:
    return (
        "<!-- operating-modes-state:start -->\n"
        "- Current plan: `demo-plan`\n"
        f"- Lifecycle status: `{status}`\n"
        f"- Current phase: `{phase}`\n"
        f"- Phase state: `{phase_state}`\n"
        f"- Next gate: `{next_gate}`\n"
        "<!-- operating-modes-state:end -->\n"
    )


def active_plan() -> str:
    return """# Demo Plan

- Lifecycle schema: `operating-modes-v1`
- Status: Active
- Plan slug: `demo-plan`
- Revision: `r1`
- Plan author ID: `author-1`
- Design reviews: ../reviews/demo-plan/review-001.md@approve@r1
- Latest design verdict: approve
- Review independence: attested
- Activation evidence: `user-instruction:fixture-activation`
- Current phase: phase-1
- Phase state: complete
- Phase entry gate: `phase-0-complete`
- Next gate: phase-2-start
- Implementation review: none
- Final disposition: none
- Verified implementation commit: none
- Lifecycle reconciliation commit: none

## Scope

Fixture plan.
"""


def design_review() -> str:
    return """# Review 001

- Review target: `docs/exec-plans/proposed/demo-plan.md`
- Review target revision: `r1`
- Review type: design
- Reviewer ID: `reviewer-1`
- Plan author ID: `author-1`
- Independence declaration: `attested`
- Evidence method: independent fixture inspection
- Verdict: approve
- Confidence: high

## Findings

None.
"""


def build_governed_fixture(root: Path) -> None:
    write(
        root,
        "AGENTS.md",
        "# Agents\n\nUse [the operating modes contract](./docs/operating-modes.md).\n\n发布 SPY YYYY-MM-DD\n拉一下 YYYY-MM-DD 的 SPY 然后更新页面\npublish SPY review for YYYY-MM-DD\npush 5/20 SPY\n",
    )
    write(
        root,
        "INSTRUCTIONS.md",
        "# Instructions\n\nUse [the operating modes contract](./docs/operating-modes.md).\n",
    )
    block = state_block("Active", "phase-1", "complete", "phase-2-start")
    write(root, "PROGRESS.md", f"# Progress\n\n{block}")
    write(root, "HANDOFF.md", f"# Handoff\n\n{block}")
    config = {
        "schema_version": "project-harness-config-v1",
        "profile": "governed",
        "verification_commands": [
            "python3 scripts/check-project-harness.py --root . --profile governed",
            "python3 -m unittest scripts.tests.test_operating_modes",
        ],
        "github": {
            "workflow": ".github/workflows/project-harness.yml",
            "pull_request_template": ".github/pull_request_template.md",
            "checks": ["Harness structure"],
        },
    }
    write(root, ".harness/config.json", json.dumps(config))
    write(
        root,
        ".github/workflows/project-harness.yml",
        "name: Test\n\non: workflow_dispatch\n\njobs:\n  harness:\n    name: Harness structure\n    runs-on: ubuntu-latest\n    steps:\n      - run: python3 scripts/check-project-harness.py --root . --profile governed\n      - run: python3 -m unittest scripts.tests.test_operating_modes\n",
    )
    write(root, ".github/pull_request_template.md", "# PR\n")
    write(
        root,
        ".github/workflows/publish-static-reviews.yml",
        "on:\n  push:\n    branches:\n      - main\n\njobs:\n  publish:\n    steps:\n      - run: PYTHONPATH=. python scripts/export_static_reviews.py\n      - run: npm run build:static-reviews\n      - run: git push --force origin gh-pages\n",
    )
    write(root, "scripts/check-project-harness.py", "# fixture path\n")
    write(root, "scripts/check-operating-modes.py", "# fixture path\n")
    write(root, "scripts/check-startup-doc-budget.py", "# fixture path\n")

    for relative in (
        "docs/architecture.md",
        "docs/roadmap.md",
        "docs/planning.md",
        "docs/decisions/index.md",
        "docs/decisions/decision-template.md",
        "docs/optimization/index.md",
        "docs/optimization/SOP.md",
        "docs/optimization/record-template.md",
        "docs/progress-archive/index.md",
    ):
        write(root, relative, f"# {Path(relative).stem}\n")
    write(
        root,
        "docs/daily-publish-runbook.md",
        "# Runbook\n\nTV default, IB exception only\n\nDo not preflight, open, or restart IB Gateway before the TV attempt.\nNever mix TV and IB bars inside one market day.\n\nPYTHONPATH=. python scripts/rebuild_live_extended_db.py\n\nnormal automation must never use it\n",
    )
    write(
        root,
        "docs/operating-modes.md",
        "# Contract\n\n`operating-modes-v1`\n\nrequested -> date_resolved -> fetched -> quality_passed -> candidate_verified -> local_accepted -> publish_authorized -> committed -> published -> hosted_verified\n\n### Local Update Gate\n\n### Publish Gate\n",
    )
    import_line = "market_day_id = None if args.skip_import else import_market_json(output_path)\n"
    write(root, "backend/scripts/fetch_tv_live_extended_day.py", import_line)
    write(root, "backend/scripts/fetch_ib_live_extended_day.py", import_line)
    write(
        root,
        "backend/scripts/rebuild_live_extended_db.py",
        'description = "Rebuild live_extended into a verified candidate and atomically promote it."\nflag = "--allow-date-loss"\n',
    )
    write(
        root,
        "docs/decisions/2026-07-19-operating-modes-and-lifecycle-source.md",
        "# Decision\n\n- Status: Accepted\n",
    )
    write(
        root,
        "docs/README.md",
        """# Docs

- [Agents](../AGENTS.md)
- [Instructions](../INSTRUCTIONS.md)
- [Progress](../PROGRESS.md)
- [Handoff](../HANDOFF.md)
- [Roadmap](./roadmap.md)
- [Exec](./exec-plans/roadmap.md)
- [Decisions](./decisions/index.md)
- [Optimization](./optimization/index.md)
- [Archive](./progress-archive/index.md)
- [Operating modes](./operating-modes.md)
""",
    )
    plan_template = "# Plan\n\n" + "\n".join(
        f"- {key}: none" for key in PLAN_KEYS
    ) + "\n\n## Body\n"
    review_template = "# Review\n\n" + "\n".join(
        f"- {key}: value" for key in REVIEW_KEYS
    ) + "\n\n## Body\n"
    write(root, "docs/exec-plans/plan-template.md", plan_template)
    write(root, "docs/exec-plans/reviews/review-template.md", review_template)
    write(root, "docs/exec-plans/active/demo-plan.md", active_plan())
    write(root, "docs/exec-plans/reviews/demo-plan/review-001.md", design_review())
    write(
        root,
        "docs/exec-plans/proposed/index.md",
        "# Proposed\n\n| Plan | Status | Review | Next gate |\n| --- | --- | --- | --- |\n| None | — | — | none |\n",
    )
    write(
        root,
        "docs/exec-plans/active/index.md",
        "# Active\n\n| Plan | Current phase | Evidence | Next gate |\n| --- | --- | --- | --- |\n"
        "| [Demo](./demo-plan.md) | phase-1:complete | [review-001](../reviews/demo-plan/review-001.md) | phase-2-start |\n",
    )
    write(
        root,
        "docs/exec-plans/completed/index.md",
        "# Completed\n\n| Plan | Disposition | Verification | Final commit |\n| --- | --- | --- | --- |\n| None | — | — | none |\n",
    )
    write(
        root,
        "docs/exec-plans/reviews/index.md",
        "# Reviews\n\n| Plan | Reviews | Latest verdict | Lifecycle state |\n| --- | --- | --- | --- |\n"
        "| [Demo](./demo-plan/) | [review-001](./demo-plan/review-001.md) | approve | Active |\n",
    )
    write(
        root,
        "docs/exec-plans/roadmap.md",
        """# Roadmap

[Proposed](./proposed/index.md) [Active](./active/index.md) [Completed](./completed/index.md) [Reviews](./reviews/index.md)

## Active Plans

- [Demo](./active/demo-plan.md) — Active; canonical details: [active index](./active/index.md)

## Proposed Plans

None.

## Completed Plans

None.
""",
    )
    init_git(root)


def init_git(root: Path) -> None:
    for command in (
        ["git", "init", "-q"],
        ["git", "config", "user.name", "Fixture"],
        ["git", "config", "user.email", "fixture@example.com"],
        ["git", "add", "."],
        ["git", "commit", "-qm", "fixture"],
    ):
        completed = run(command, root)
        if completed.returncode != 0:
            raise RuntimeError(completed.stderr)


class OperatingModesCheckerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "repo"
        self.root.mkdir()
        build_governed_fixture(self.root)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def check(self) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
        completed = run(["python3", str(CHECKER), "--root", str(self.root)], PROJECT_ROOT)
        payload = json.loads(completed.stdout.splitlines()[0])
        return completed, payload

    def assert_error(self, needle: str) -> None:
        completed, payload = self.check()
        self.assertNotEqual(completed.returncode, 0)
        self.assertTrue(any(needle in str(item) for item in payload["errors"]), payload["errors"])

    def replace(self, relative: str, old: str, new: str) -> None:
        path = self.root / relative
        path.write_text(path.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")

    def make_proposed(self) -> None:
        source = self.root / "docs/exec-plans/active/demo-plan.md"
        target = self.root / "docs/exec-plans/proposed/demo-plan.md"
        source.rename(target)
        text = target.read_text(encoding="utf-8")
        replacements = {
            "- Status: Active": "- Status: Proposed",
            "- Activation evidence: `user-instruction:fixture-activation`": "- Activation evidence: none",
            "- Current phase: phase-1": "- Current phase: none",
            "- Phase state: complete": "- Phase state: none",
            "- Phase entry gate: `phase-0-complete`": "- Phase entry gate: none",
            "- Next gate: phase-2-start": "- Next gate: activation-recording",
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        target.write_text(text, encoding="utf-8")
        write(
            self.root,
            "docs/exec-plans/active/index.md",
            "# Active\n\n| Plan | Current phase | Evidence | Next gate |\n| --- | --- | --- | --- |\n| None | — | — | none |\n",
        )
        write(
            self.root,
            "docs/exec-plans/proposed/index.md",
            "# Proposed\n\n| Plan | Status | Review | Next gate |\n| --- | --- | --- | --- |\n"
            "| [Demo](./demo-plan.md) | Proposed | [review-001](../reviews/demo-plan/review-001.md): approve | activation-recording |\n",
        )
        self.replace("docs/exec-plans/reviews/index.md", "| approve | Active |", "| approve | Proposed |")
        write(
            self.root,
            "docs/exec-plans/roadmap.md",
            """# Roadmap

[Proposed](./proposed/index.md) [Active](./active/index.md) [Completed](./completed/index.md) [Reviews](./reviews/index.md)

## Active Plans

None.

## Proposed Plans

- [Demo](./proposed/demo-plan.md) — Proposed; canonical details: [proposed index](./proposed/index.md)

## Completed Plans

None.
""",
        )
        block = state_block("Proposed", "none", "none", "activation-recording")
        write(self.root, "PROGRESS.md", f"# Progress\n\n{block}")
        write(self.root, "HANDOFF.md", f"# Handoff\n\n{block}")

    def make_completed(self) -> None:
        source = self.root / "docs/exec-plans/active/demo-plan.md"
        target = self.root / "docs/exec-plans/completed/demo-plan.md"
        source.rename(target)
        text = target.read_text(encoding="utf-8")
        replacements = {
            "- Status: Active": "- Status: Completed",
            "- Current phase: phase-1": "- Current phase: none",
            "- Phase state: complete": "- Phase state: none",
            "- Phase entry gate: `phase-0-complete`": "- Phase entry gate: none",
            "- Next gate: phase-2-start": "- Next gate: closed",
            "- Implementation review: none": "- Implementation review: ../reviews/demo-plan/implementation-review-001.md@accept",
            "- Final disposition: none": "- Final disposition: Completed",
            "- Verified implementation commit: none": "- Verified implementation commit: `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`",
            "- Lifecycle reconciliation commit: none": "- Lifecycle reconciliation commit: `bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb`",
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        target.write_text(text, encoding="utf-8")
        write(
            self.root,
            "docs/exec-plans/reviews/demo-plan/implementation-review-001.md",
            """# Implementation Review

- Review target: `docs/exec-plans/active/demo-plan.md`
- Review target revision: `r1`
- Review type: implementation
- Reviewer ID: `reviewer-2`
- Plan author ID: `author-1`
- Independence declaration: `attested`
- Evidence method: independent implementation inspection
- Verdict: accept
- Confidence: high

## Findings

None.
""",
        )
        write(
            self.root,
            "docs/exec-plans/active/index.md",
            "# Active\n\n| Plan | Current phase | Evidence | Next gate |\n| --- | --- | --- | --- |\n| None | — | — | none |\n",
        )
        write(
            self.root,
            "docs/exec-plans/completed/index.md",
            "# Completed\n\n| Plan | Disposition | Verification | Final commit |\n| --- | --- | --- | --- |\n"
            "| [Demo](./demo-plan.md) | Completed | [implementation review](../reviews/demo-plan/implementation-review-001.md) | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa |\n",
        )
        write(
            self.root,
            "docs/exec-plans/reviews/index.md",
            "# Reviews\n\n| Plan | Reviews | Latest verdict | Lifecycle state |\n| --- | --- | --- | --- |\n"
            "| [Demo](./demo-plan/) | [review-001](./demo-plan/review-001.md), [implementation-review-001](./demo-plan/implementation-review-001.md) | accept | Completed |\n",
        )
        write(
            self.root,
            "docs/exec-plans/roadmap.md",
            """# Roadmap

[Proposed](./proposed/index.md) [Active](./active/index.md) [Completed](./completed/index.md) [Reviews](./reviews/index.md)

## Active Plans

None.

## Proposed Plans

None.

## Completed Plans

- [Demo](./completed/demo-plan.md) — Completed; canonical details: [completed index](./completed/index.md)
""",
        )
        block = state_block("Completed", "none", "none", "closed")
        write(self.root, "PROGRESS.md", f"# Progress\n\n{block}")
        write(self.root, "HANDOFF.md", f"# Handoff\n\n{block}")

    def make_pre_review_proposed(self) -> None:
        self.make_proposed()
        self.replace(
            "docs/exec-plans/proposed/demo-plan.md",
            "- Design reviews: ../reviews/demo-plan/review-001.md@approve@r1",
            "- Design reviews: none",
        )
        self.replace(
            "docs/exec-plans/proposed/demo-plan.md",
            "- Latest design verdict: approve",
            "- Latest design verdict: none",
        )
        self.replace(
            "docs/exec-plans/proposed/demo-plan.md",
            "- Review independence: attested",
            "- Review independence: none",
        )
        review = self.root / "docs/exec-plans/reviews/demo-plan/review-001.md"
        review.unlink()
        review.parent.rmdir()
        write(
            self.root,
            "docs/exec-plans/proposed/index.md",
            "# Proposed\n\n| Plan | Status | Review | Next gate |\n| --- | --- | --- | --- |\n"
            "| [Demo](./demo-plan.md) | Proposed | none | activation-recording |\n",
        )
        write(
            self.root,
            "docs/exec-plans/reviews/index.md",
            "# Reviews\n\n| Plan | Reviews | Latest verdict | Lifecycle state |\n| --- | --- | --- | --- |\n"
            "| [Demo](../proposed/demo-plan.md) | none | none | Proposed |\n",
        )

    def make_nonimplemented_completed(self) -> None:
        self.make_completed()
        replacements = {
            "- Design reviews: ../reviews/demo-plan/review-001.md@approve@r1": "- Design reviews: none",
            "- Latest design verdict: approve": "- Latest design verdict: none",
            "- Review independence: attested": "- Review independence: none",
            "- Implementation review: ../reviews/demo-plan/implementation-review-001.md@accept": "- Implementation review: none",
            "- Final disposition: Completed": "- Final disposition: Rejected",
            "- Verified implementation commit: `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`": "- Verified implementation commit: none",
            "- Lifecycle reconciliation commit: `bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb`": "- Lifecycle reconciliation commit: none",
        }
        for old, new in replacements.items():
            self.replace("docs/exec-plans/completed/demo-plan.md", old, new)
        review_dir = self.root / "docs/exec-plans/reviews/demo-plan"
        (review_dir / "review-001.md").unlink()
        (review_dir / "implementation-review-001.md").unlink()
        review_dir.rmdir()
        write(
            self.root,
            "docs/exec-plans/completed/index.md",
            "# Completed\n\n| Plan | Disposition | Verification | Final commit |\n| --- | --- | --- | --- |\n"
            "| [Demo](./demo-plan.md) | Rejected | none | none |\n",
        )
        write(
            self.root,
            "docs/exec-plans/reviews/index.md",
            "# Reviews\n\n| Plan | Reviews | Latest verdict | Lifecycle state |\n| --- | --- | --- | --- |\n"
            "| [Demo](../completed/demo-plan.md) | none | none | Completed |\n",
        )

    def test_valid_active_fixture_passes(self) -> None:
        completed, payload = self.check()
        self.assertEqual(completed.returncode, 0, payload["errors"])
        self.assertTrue(payload["passed"])

    def test_duplicate_slug_across_directories_fails(self) -> None:
        shutil.copy2(
            self.root / "docs/exec-plans/active/demo-plan.md",
            self.root / "docs/exec-plans/proposed/demo-plan.md",
        )
        self.assert_error("duplicate 'demo-plan'")

    def test_status_directory_mismatch_fails(self) -> None:
        self.replace("docs/exec-plans/active/demo-plan.md", "- Status: Active", "- Status: Proposed")
        self.assert_error("expected 'Active'")

    def test_missing_state_index_row_fails(self) -> None:
        write(
            self.root,
            "docs/exec-plans/active/index.md",
            "# Active\n\n| Plan | Current phase | Evidence | Next gate |\n| --- | --- | --- | --- |\n| None | — | — | none |\n",
        )
        self.assert_error("missing plan rows")

    def test_duplicate_state_index_row_fails(self) -> None:
        path = self.root / "docs/exec-plans/active/index.md"
        row = "| [Demo](./demo-plan.md) | phase-1:complete | [review-001](../reviews/demo-plan/review-001.md) | phase-2-start |\n"
        path.write_text(path.read_text(encoding="utf-8") + row, encoding="utf-8")
        self.assert_error("contains duplicate plan rows")

    def test_ghost_state_index_row_fails(self) -> None:
        path = self.root / "docs/exec-plans/active/index.md"
        row = "| [Ghost](./ghost-plan.md) | phase-1:complete | [review](../reviews/demo-plan/review-001.md) | phase-2-start |\n"
        path.write_text(path.read_text(encoding="utf-8") + row, encoding="utf-8")
        self.assert_error("ghost plan link")

    def test_reviews_index_state_mismatch_fails(self) -> None:
        self.replace("docs/exec-plans/reviews/index.md", "| approve | Active |", "| approve | Proposed |")
        self.assert_error("lifecycle state='Proposed'")

    def test_roadmap_state_mismatch_fails(self) -> None:
        self.replace(
            "docs/exec-plans/roadmap.md",
            "— Active; canonical details: [active index](./active/index.md)",
            "— Proposed; canonical details: [active index](./active/index.md)",
        )
        self.assert_error("row state mismatch")

    def test_active_without_matching_approve_fails(self) -> None:
        self.replace(
            "docs/exec-plans/active/demo-plan.md",
            "- Design reviews: ../reviews/demo-plan/review-001.md@approve@r1",
            "- Design reviews: none",
        )
        self.replace("docs/exec-plans/active/demo-plan.md", "- Latest design verdict: approve", "- Latest design verdict: none")
        self.assert_error("lacks matching-revision approve review")

    def test_active_without_activation_fails(self) -> None:
        self.replace(
            "docs/exec-plans/active/demo-plan.md",
            "- Activation evidence: `user-instruction:fixture-activation`",
            "- Activation evidence: none",
        )
        self.assert_error("lacks user-instruction activation evidence")

    def test_active_rejects_empty_activation_reference(self) -> None:
        self.replace(
            "docs/exec-plans/active/demo-plan.md",
            "- Activation evidence: `user-instruction:fixture-activation`",
            "- Activation evidence: `user-instruction:`",
        )
        self.assert_error("Activation evidence must be none or a non-empty user-instruction reference")

    def test_active_next_gate_must_be_non_none(self) -> None:
        for relative in (
            "docs/exec-plans/active/demo-plan.md",
            "docs/exec-plans/active/index.md",
            "PROGRESS.md",
            "HANDOFF.md",
        ):
            self.replace(relative, "phase-2-start", "none")
        self.assert_error("Active plan Next gate must be non-none")

    def test_active_without_independence_attestation_fails(self) -> None:
        self.replace("docs/exec-plans/active/demo-plan.md", "- Review independence: attested", "- Review independence: none")
        self.assert_error("Review independence must be attested")

    def test_proposed_with_approve_and_no_activation_passes(self) -> None:
        self.make_proposed()
        completed, payload = self.check()
        self.assertEqual(completed.returncode, 0, payload["errors"])

    def test_pre_review_proposed_with_none_evidence_passes(self) -> None:
        self.make_pre_review_proposed()
        completed, payload = self.check()
        self.assertEqual(completed.returncode, 0, payload["errors"])

    def test_pre_review_proposed_bogus_evidence_link_fails(self) -> None:
        self.make_pre_review_proposed()
        self.replace(
            "docs/exec-plans/proposed/index.md",
            "| Proposed | none | activation-recording |",
            "| Proposed | [none](../plan-template.md) | activation-recording |",
        )
        self.assert_error("without design reviews must use evidence none")

    def test_no_design_reviews_rejects_declared_approve(self) -> None:
        self.make_pre_review_proposed()
        self.replace(
            "docs/exec-plans/proposed/demo-plan.md",
            "- Latest design verdict: none",
            "- Latest design verdict: approve",
        )
        self.assert_error("Design reviews=none requires Latest design verdict=none")

    def test_no_design_reviews_rejects_independence_attestation(self) -> None:
        self.make_pre_review_proposed()
        self.replace(
            "docs/exec-plans/proposed/demo-plan.md",
            "- Review independence: none",
            "- Review independence: attested",
        )
        self.assert_error("Design reviews=none requires Latest design verdict=none")

    def test_new_schema_design_reviews_require_independence_attestation(self) -> None:
        self.make_proposed()
        self.replace(
            "docs/exec-plans/proposed/demo-plan.md",
            "- Review independence: attested",
            "- Review independence: none",
        )
        self.assert_error("new-schema plans with design reviews require Review independence=attested")

    def test_every_plan_requires_a_reviews_index_row(self) -> None:
        self.make_pre_review_proposed()
        write(
            self.root,
            "docs/exec-plans/reviews/index.md",
            "# Reviews\n\n| Plan | Reviews | Latest verdict | Lifecycle state |\n| --- | --- | --- | --- |\n"
            "| None | none | none | None |\n",
        )
        self.assert_error("reviews index: missing plan rows: demo-plan")

    def test_active_without_phase_fails(self) -> None:
        self.replace("docs/exec-plans/active/demo-plan.md", "- Current phase: phase-1", "- Current phase: none")
        self.assert_error("lacks phase, phase state, or phase entry gate")

    def test_valid_completed_plan_passes(self) -> None:
        self.make_completed()
        completed, payload = self.check()
        self.assertEqual(completed.returncode, 0, payload["errors"])

    def test_nonimplemented_completed_with_none_verification_passes(self) -> None:
        self.make_nonimplemented_completed()
        completed, payload = self.check()
        self.assertEqual(completed.returncode, 0, payload["errors"])

    def test_nonimplemented_completed_bogus_verification_link_fails(self) -> None:
        self.make_nonimplemented_completed()
        self.replace(
            "docs/exec-plans/completed/index.md",
            "| Rejected | none | none |",
            "| Rejected | [none](../plan-template.md) | none |",
        )
        self.assert_error("without an implementation review must use verification none")

    def test_completed_disposition_requires_accept_even_without_commits(self) -> None:
        self.make_nonimplemented_completed()
        self.replace(
            "docs/exec-plans/completed/demo-plan.md",
            "- Final disposition: Rejected",
            "- Final disposition: Completed",
        )
        self.replace(
            "docs/exec-plans/completed/index.md",
            "| Rejected | none | none |",
            "| Completed | none | none |",
        )
        self.assert_error("implemented Completed plan requires <path>@accept")

    def test_state_index_plan_cell_rejects_second_link(self) -> None:
        self.replace(
            "docs/exec-plans/active/index.md",
            "[Demo](./demo-plan.md)",
            "[Demo](./demo-plan.md) [bogus](../plan-template.md)",
        )
        self.assert_error("Plan cell must be exactly one standalone link")

    def test_reviews_index_plan_cell_rejects_second_link(self) -> None:
        self.replace(
            "docs/exec-plans/reviews/index.md",
            "[Demo](./demo-plan/)",
            "[Demo](./demo-plan/) [bogus](../plan-template.md)",
        )
        self.assert_error("Plan cell must be exactly one standalone link")

    def test_fixed_index_row_rejects_extra_cell(self) -> None:
        self.replace(
            "docs/exec-plans/active/index.md",
            "| phase-2-start |",
            "| phase-2-start | extra |",
        )
        self.assert_error("fixed row must contain exactly four cells")

    def test_all_indexes_reject_trailing_empty_fifth_cell(self) -> None:
        cases = (
            ("docs/exec-plans/proposed/index.md", "| None | — | — | none |"),
            ("docs/exec-plans/active/index.md", "| [Demo](./demo-plan.md) | phase-1:complete | [review-001](../reviews/demo-plan/review-001.md) | phase-2-start |"),
            ("docs/exec-plans/completed/index.md", "| None | — | — | none |"),
            ("docs/exec-plans/reviews/index.md", "| [Demo](./demo-plan/) | [review-001](./demo-plan/review-001.md) | approve | Active |"),
        )
        for relative, row in cases:
            with self.subTest(index=relative):
                self.replace(relative, row, f"{row}|")
                completed, payload = self.check()
                self.assertNotEqual(completed.returncode, 0)
                self.assertTrue(
                    any("exactly four cells" in str(item) or "exact None sentinel" in str(item) for item in payload["errors"]),
                    payload["errors"],
                )
                self.replace(relative, f"{row}|", row)

    def test_index_rejects_arbitrary_no_link_data_row(self) -> None:
        path = self.root / "docs/exec-plans/active/index.md"
        path.write_text(
            path.read_text(encoding="utf-8") + "| forged | x | y | z |\n",
            encoding="utf-8",
        )
        self.assert_error("data row must use a canonical Plan link or exact None sentinel")

    def test_index_rejects_none_sentinel_mixed_with_plan_rows(self) -> None:
        path = self.root / "docs/exec-plans/active/index.md"
        path.write_text(
            path.read_text(encoding="utf-8") + "| None | — | — | none |\n",
            encoding="utf-8",
        )
        self.assert_error("cannot mix a None sentinel with plan rows")

    def test_empty_state_indexes_require_canonical_sentinel(self) -> None:
        cases = (
            "docs/exec-plans/proposed/index.md",
            "docs/exec-plans/completed/index.md",
        )
        for relative in cases:
            with self.subTest(index=relative):
                self.replace(relative, "| None | — | — | none |\n", "")
                self.assert_error("empty plan set requires exactly one canonical None sentinel")
                self.replace(relative, "| --- | --- | --- | --- |\n", "| --- | --- | --- | --- |\n| None | — | — | none |\n")

    def test_empty_reviews_index_requires_canonical_sentinel(self) -> None:
        (self.root / "docs/exec-plans/active/demo-plan.md").unlink()
        shutil.rmtree(self.root / "docs/exec-plans/reviews/demo-plan")
        write(
            self.root,
            "docs/exec-plans/active/index.md",
            "# Active\n\n| Plan | Current phase | Evidence | Next gate |\n"
            "| --- | --- | --- | --- |\n| None | — | — | none |\n",
        )
        write(
            self.root,
            "docs/exec-plans/reviews/index.md",
            "# Reviews\n\n| Plan | Reviews | Latest verdict | Lifecycle state |\n"
            "| --- | --- | --- | --- |\n",
        )
        write(
            self.root,
            "docs/exec-plans/roadmap.md",
            "# Roadmap\n\n## Active Plans\n\nNone.\n\n## Proposed Plans\n\nNone.\n\n"
            "## Completed Plans\n\nNone.\n",
        )
        none_block = (
            "<!-- operating-modes-state:start -->\n"
            "- Current plan: `none`\n"
            "- Lifecycle status: `None`\n"
            "- Current phase: `none`\n"
            "- Phase state: `none`\n"
            "- Next gate: `none`\n"
            "<!-- operating-modes-state:end -->\n"
        )
        write(self.root, "PROGRESS.md", f"# Progress\n\n{none_block}")
        write(self.root, "HANDOFF.md", f"# Handoff\n\n{none_block}")
        self.assert_error("empty plan set requires exactly one canonical None sentinel")

    def test_reserved_header_words_cannot_masquerade_as_data_rows(self) -> None:
        path = self.root / "docs/exec-plans/active/index.md"
        for first_cell in ("Plan", "Decision"):
            with self.subTest(first_cell=first_cell):
                forged = f"| {first_cell} | forged | x | y |\n"
                path.write_text(path.read_text(encoding="utf-8") + forged, encoding="utf-8")
                self.assert_error("data row must use a canonical Plan link or exact None sentinel")
                self.replace("docs/exec-plans/active/index.md", forged, "")

    def test_index_header_rejects_extra_cell(self) -> None:
        self.replace(
            "docs/exec-plans/active/index.md",
            "| Plan | Current phase | Evidence | Next gate |",
            "| Plan | Current phase | Evidence | Next gate | forged |",
        )
        self.assert_error("must contain exactly one canonical header")

    def test_index_header_and_separator_must_be_adjacent(self) -> None:
        self.replace(
            "docs/exec-plans/active/index.md",
            "| Plan | Current phase | Evidence | Next gate |\n| --- | --- | --- | --- |",
            "| Plan | Current phase | Evidence | Next gate |\nintervening prose\n| --- | --- | --- | --- |",
        )
        self.assert_error("canonical header must be followed immediately by separator")

    def test_index_tables_inside_html_comments_do_not_count(self) -> None:
        for relative in (
            "docs/exec-plans/proposed/index.md",
            "docs/exec-plans/active/index.md",
            "docs/exec-plans/completed/index.md",
            "docs/exec-plans/reviews/index.md",
        ):
            with self.subTest(index=relative):
                path = self.root / relative
                original = path.read_text(encoding="utf-8")
                header = original.index("| Plan |")
                commented = original[:header] + "<!--\n" + original[header:].rstrip() + "\n-->\n"
                path.write_text(commented, encoding="utf-8")
                self.assert_error("must contain exactly one canonical header")
                path.write_text(original, encoding="utf-8")

    def test_index_table_inside_fenced_code_does_not_count(self) -> None:
        path = self.root / "docs/exec-plans/active/index.md"
        original = path.read_text(encoding="utf-8")
        header = original.index("| Plan |")
        fenced = original[:header] + "```text\n" + original[header:].rstrip() + "\n```\n"
        path.write_text(fenced, encoding="utf-8")
        self.assert_error("must contain exactly one canonical header")

    def test_indented_code_table_does_not_count(self) -> None:
        path = self.root / "docs/exec-plans/active/index.md"
        original = path.read_text(encoding="utf-8")
        lines = original.splitlines()
        coded = "\n".join(f"    {line}" if line.startswith("|") else line for line in lines) + "\n"
        path.write_text(coded, encoding="utf-8")
        self.assert_error("must contain exactly one canonical header")

    def test_index_rows_require_terminal_delimiter(self) -> None:
        cases = (
            (
                "docs/exec-plans/active/index.md",
                "| [Demo](./demo-plan.md) | phase-1:complete | [review-001](../reviews/demo-plan/review-001.md) | phase-2-start |",
            ),
            ("docs/exec-plans/proposed/index.md", "| None | — | — | none |"),
            ("docs/exec-plans/completed/index.md", "| Plan | Disposition | Verification | Final commit |"),
            ("docs/exec-plans/reviews/index.md", "| --- | --- | --- | --- |"),
        )
        for relative, row in cases:
            with self.subTest(index=relative):
                self.replace(relative, row, row[:-1])
                self.assert_error("table row requires a terminal delimiter")
                self.replace(relative, row[:-1], row)

    def test_migrated_legacy_completed_plan_passes_without_rewriting_reviews(self) -> None:
        self.make_completed()
        self.replace(
            "docs/exec-plans/completed/demo-plan.md",
            "- Lifecycle schema: `operating-modes-v1`",
            "- Lifecycle schema: `operating-modes-legacy-v1`",
        )
        write(
            self.root,
            "docs/exec-plans/reviews/demo-plan/review-001.md",
            "# Historical Design Review\n\n**裁决**: approve\n\nHistorical prose stays untouched.\n",
        )
        write(
            self.root,
            "docs/exec-plans/reviews/demo-plan/implementation-review-001.md",
            "# Historical Implementation Review\n\n**裁决**: accept\n\nHistorical prose stays untouched.\n",
        )
        completed, payload = self.check()
        self.assertEqual(completed.returncode, 0, payload["errors"])

    def test_completed_plan_without_disposition_fails(self) -> None:
        self.make_completed()
        self.replace("docs/exec-plans/completed/demo-plan.md", "- Final disposition: Completed", "- Final disposition: none")
        self.assert_error("Completed plan lacks final disposition")

    def test_completed_implemented_plan_without_accept_review_fails(self) -> None:
        self.make_completed()
        self.replace(
            "docs/exec-plans/completed/demo-plan.md",
            "- Implementation review: ../reviews/demo-plan/implementation-review-001.md@accept",
            "- Implementation review: none",
        )
        self.assert_error("requires <path>@accept")

    def test_state_blocks_must_match(self) -> None:
        self.replace("HANDOFF.md", "- Next gate: `phase-2-start`", "- Next gate: `wrong-gate`")
        self.assert_error("PROGRESS.md and HANDOFF.md do not match")

    def test_state_block_rejects_reversed_markers(self) -> None:
        for relative in ("PROGRESS.md", "HANDOFF.md"):
            self.replace(
                relative,
                "<!-- operating-modes-state:start -->",
                "<!-- operating-modes-state:temporary -->",
            )
            self.replace(
                relative,
                "<!-- operating-modes-state:end -->",
                "<!-- operating-modes-state:start -->",
            )
            self.replace(
                relative,
                "<!-- operating-modes-state:temporary -->",
                "<!-- operating-modes-state:end -->",
            )
        self.assert_error("start marker must precede end marker")

    def test_forbidden_live_git_key_fails(self) -> None:
        path = self.root / "PROGRESS.md"
        path.write_text(path.read_text(encoding="utf-8") + "\n- Git state: unstaged/uncommitted diff\n", encoding="utf-8")
        self.assert_error("forbidden live-Git key outside historical block")

    def test_historical_git_marker_is_ignored(self) -> None:
        path = self.root / "PROGRESS.md"
        path.write_text(
            path.read_text(encoding="utf-8")
            + "\n<!-- git-evidence:historical:start -->\n"
            + "- Verified at: `2026-07-19`\n"
            + "- Verified commit: `1111111111111111111111111111111111111111`\n"
            + "- Git state: unstaged/uncommitted diff\n"
            + "<!-- git-evidence:historical:end -->\n",
            encoding="utf-8",
        )
        completed, payload = self.check()
        self.assertEqual(completed.returncode, 0, payload["errors"])

    def test_missing_contract_path_fails_specifically(self) -> None:
        (self.root / "docs/operating-modes.md").unlink()
        self.assert_error("missing required file: docs/operating-modes.md")

    def test_same_plan_author_and_reviewer_fails(self) -> None:
        self.replace("docs/exec-plans/reviews/demo-plan/review-001.md", "- Reviewer ID: `reviewer-1`", "- Reviewer ID: `author-1`")
        self.assert_error("Reviewer ID must differ")

    def test_duplicate_plan_metadata_key_fails(self) -> None:
        self.replace(
            "docs/exec-plans/active/demo-plan.md",
            "- Status: Active",
            "- Status: Proposed\n- Status: Active",
        )
        self.assert_error("duplicate constrained key: Status")

    def test_plan_metadata_inside_html_comment_does_not_count(self) -> None:
        self.replace("docs/exec-plans/active/demo-plan.md", "# Demo Plan\n\n", "# Demo Plan\n\n<!--\n")
        self.replace("docs/exec-plans/active/demo-plan.md", "\n## Scope", "\n-->\n\n## Scope")
        self.assert_error("missing required keys")

    def test_duplicate_review_verdict_key_fails(self) -> None:
        self.replace(
            "docs/exec-plans/reviews/demo-plan/review-001.md",
            "- Verdict: approve",
            "- Verdict: reject\n- Verdict: approve",
        )
        self.assert_error("duplicate constrained key: Verdict")

    def test_review_metadata_inside_html_comment_does_not_count(self) -> None:
        self.replace(
            "docs/exec-plans/reviews/demo-plan/review-001.md",
            "# Review 001\n\n",
            "# Review 001\n\n<!--\n",
        )
        self.replace(
            "docs/exec-plans/reviews/demo-plan/review-001.md",
            "\n## Findings",
            "\n-->\n\n## Findings",
        )
        self.assert_error("lacks constrained reviewer fields")

    def test_template_metadata_inside_html_comment_does_not_count(self) -> None:
        self.replace("docs/exec-plans/plan-template.md", "# Plan\n\n", "# Plan\n\n<!--\n")
        self.replace("docs/exec-plans/plan-template.md", "\n\n## Body", "\n-->\n\n## Body")
        self.assert_error("plan template: missing constrained keys")

    def test_duplicate_current_state_key_fails(self) -> None:
        self.replace(
            "PROGRESS.md",
            "- Phase state: `complete`",
            "- Phase state: `blocked`\n- Phase state: `complete`",
        )
        self.assert_error("duplicate constrained key: Phase state")

    def test_duplicate_template_key_fails(self) -> None:
        self.replace(
            "docs/exec-plans/plan-template.md",
            "- Status: none",
            "- Status: Proposed\n- Status: none",
        )
        self.assert_error("plan template duplicate constrained key: Status")

    def test_design_review_type_must_be_design(self) -> None:
        self.replace(
            "docs/exec-plans/reviews/demo-plan/review-001.md",
            "- Review type: design",
            "- Review type: implementation",
        )
        self.assert_error("expected 'design' for this evidence")

    def test_implementation_review_type_must_be_implementation(self) -> None:
        self.make_completed()
        self.replace(
            "docs/exec-plans/reviews/demo-plan/implementation-review-001.md",
            "- Review type: implementation",
            "- Review type: design",
        )
        self.assert_error("expected 'implementation' for this evidence")

    def test_review_target_requires_exact_canonical_plan_path(self) -> None:
        self.replace(
            "docs/exec-plans/reviews/demo-plan/review-001.md",
            "docs/exec-plans/proposed/demo-plan.md",
            "unrelated/location/demo-plan.md",
        )
        self.assert_error("expected an exact canonical lifecycle path")

    def test_review_revision_must_match_declared_revision(self) -> None:
        self.replace("docs/exec-plans/reviews/demo-plan/review-001.md", "- Review target revision: `r1`", "- Review target revision: `r2`")
        self.assert_error("target='r2' declared='r1'")

    def test_reviews_index_latest_verdict_must_match_last_artifact(self) -> None:
        self.replace("docs/exec-plans/reviews/index.md", "| approve | Active |", "| reject | Active |")
        self.assert_error("latest verdict='reject'; expected 'approve'")

    def test_reviews_index_must_list_every_review_artifact(self) -> None:
        write(self.root, "docs/exec-plans/reviews/demo-plan/review-002.md", "# Review 002\n\n**裁决**: revise\n")
        self.assert_error("artifact set mismatch")

    def test_active_index_evidence_must_match_latest_review_artifact(self) -> None:
        write(
            self.root,
            "docs/exec-plans/reviews/demo-plan/review-002.md",
            "# Review 002\n\n**裁决**: revise\n",
        )
        self.replace(
            "docs/exec-plans/reviews/index.md",
            "[review-001](./demo-plan/review-001.md) | approve",
            "[review-001](./demo-plan/review-001.md), [review-002](./demo-plan/review-002.md) | revise",
        )
        self.assert_error("latest evidence mismatch")

    def test_completed_index_evidence_must_match_implementation_review(self) -> None:
        self.make_completed()
        self.replace(
            "docs/exec-plans/completed/index.md",
            "../reviews/demo-plan/implementation-review-001.md",
            "../reviews/demo-plan/review-001.md",
        )
        self.assert_error("implementation evidence mismatch")

    def test_proposed_next_gate_rejects_publish_authority(self) -> None:
        self.make_proposed()
        for relative in (
            "docs/exec-plans/proposed/demo-plan.md",
            "docs/exec-plans/proposed/index.md",
            "PROGRESS.md",
            "HANDOFF.md",
        ):
            self.replace(relative, "activation-recording", "publish-now")
        self.assert_error("must be a review, revision, or activation-recording gate")

    def test_all_proposed_gate_prefixes_allow_delimited_suffixes(self) -> None:
        self.make_proposed()
        previous = "activation-recording"
        for gate in (
            "design-review-r2",
            "review-round-2",
            "revision-v2",
            "plan-revision-v2",
            "activation-recording-user",
        ):
            with self.subTest(gate=gate):
                for relative in (
                    "docs/exec-plans/proposed/demo-plan.md",
                    "docs/exec-plans/proposed/index.md",
                    "PROGRESS.md",
                    "HANDOFF.md",
                ):
                    self.replace(relative, previous, gate)
                completed, payload = self.check()
                self.assertEqual(completed.returncode, 0, payload["errors"])
                previous = gate

    def test_matching_review_requires_all_reviewer_fields(self) -> None:
        self.replace(
            "docs/exec-plans/reviews/demo-plan/review-001.md",
            "- Evidence method: independent fixture inspection\n",
            "",
        )
        self.assert_error("missing required keys: Evidence method")

    def test_new_schema_prior_revision_review_requires_structured_metadata(self) -> None:
        self.replace("docs/exec-plans/active/demo-plan.md", "- Revision: `r1`", "- Revision: `r2`")
        self.replace(
            "docs/exec-plans/active/demo-plan.md",
            "- Design reviews: ../reviews/demo-plan/review-001.md@approve@r1",
            "- Design reviews: ../reviews/demo-plan/review-001.md@approve@r1, "
            "../reviews/demo-plan/review-002.md@approve@r2",
        )
        write(
            self.root,
            "docs/exec-plans/reviews/demo-plan/review-001.md",
            "# Historical Review\n\n**裁决**: approve\n\nUnstructured historical prose.\n",
        )
        write(
            self.root,
            "docs/exec-plans/reviews/demo-plan/review-002.md",
            design_review()
            .replace("# Review 001", "# Review 002")
            .replace("- Review target revision: `r1`", "- Review target revision: `r2`")
            .replace("- Reviewer ID: `reviewer-1`", "- Reviewer ID: `reviewer-2`"),
        )
        self.replace(
            "docs/exec-plans/reviews/index.md",
            "[review-001](./demo-plan/review-001.md) | approve",
            "[review-001](./demo-plan/review-001.md), [review-002](./demo-plan/review-002.md) | approve",
        )
        self.replace(
            "docs/exec-plans/active/index.md",
            "[review-001](../reviews/demo-plan/review-001.md)",
            "[review-002](../reviews/demo-plan/review-002.md)",
        )
        self.assert_error("review-001.md lacks constrained reviewer fields")

    def test_router_must_link_normative_contract(self) -> None:
        self.replace("AGENTS.md", "docs/operating-modes.md", "docs/missing-modes.md")
        self.assert_error("AGENTS.md does not contain a non-comment canonical Markdown link")

    def test_router_comment_only_token_does_not_count(self) -> None:
        write(
            self.root,
            "AGENTS.md",
            "# Agents\n\n<!-- [dead route](./docs/operating-modes.md) -->\n",
        )
        self.assert_error("AGENTS.md does not contain a non-comment canonical Markdown link")

    def test_router_unclosed_comment_token_does_not_count(self) -> None:
        write(
            self.root,
            "AGENTS.md",
            "# Agents\n\n<!-- [dead route](./docs/operating-modes.md)\n",
        )
        self.assert_error("AGENTS.md does not contain a non-comment canonical Markdown link")

    def test_router_inline_code_pseudo_link_does_not_count(self) -> None:
        write(
            self.root,
            "AGENTS.md",
            "# Agents\n\n`[dead route](./docs/operating-modes.md)`\n",
        )
        self.assert_error("AGENTS.md does not contain a non-comment canonical Markdown link")

    def test_router_indented_code_pseudo_link_does_not_count(self) -> None:
        write(
            self.root,
            "AGENTS.md",
            "# Agents\n\n    [dead route](./docs/operating-modes.md)\n",
        )
        self.assert_error("AGENTS.md does not contain a non-comment canonical Markdown link")

    def test_config_requires_fixture_command(self) -> None:
        path = self.root / ".harness/config.json"
        config = json.loads(path.read_text(encoding="utf-8"))
        config["verification_commands"].remove("python3 -m unittest scripts.tests.test_operating_modes")
        path.write_text(json.dumps(config), encoding="utf-8")
        self.assert_error("verification config: missing required command")

    def test_config_requires_canonical_command_before_fixtures(self) -> None:
        path = self.root / ".harness/config.json"
        config = json.loads(path.read_text(encoding="utf-8"))
        config["verification_commands"].reverse()
        path.write_text(json.dumps(config), encoding="utf-8")
        self.assert_error("canonical harness command must precede fixture tests")

    def test_workflow_requires_fixture_command(self) -> None:
        self.replace(
            ".github/workflows/project-harness.yml",
            "run: python3 -m unittest scripts.tests.test_operating_modes",
            "run: echo missing-fixture-command",
        )
        self.assert_error("verification workflow: missing required command")

    def test_workflow_comment_only_commands_do_not_count(self) -> None:
        for command in (
            "python3 scripts/check-project-harness.py --root . --profile governed",
            "python3 -m unittest scripts.tests.test_operating_modes",
        ):
            self.replace(
                ".github/workflows/project-harness.yml",
                f"      - run: {command}",
                f"      # - run: {command}",
            )
        self.assert_error("verification workflow: missing required command")

    def test_workflow_block_run_values_are_supported(self) -> None:
        for command in (
            "python3 scripts/check-project-harness.py --root . --profile governed",
            "python3 -m unittest scripts.tests.test_operating_modes",
        ):
            self.replace(
                ".github/workflows/project-harness.yml",
                f"      - run: {command}",
                f"      - run: |\n          {command}",
            )
        completed, payload = self.check()
        self.assertEqual(completed.returncode, 0, payload["errors"])

    def test_workflow_quoted_inline_run_values_are_supported(self) -> None:
        for command in (
            "python3 scripts/check-project-harness.py --root . --profile governed",
            "python3 -m unittest scripts.tests.test_operating_modes",
        ):
            self.replace(
                ".github/workflows/project-harness.yml",
                f"      - run: {command}",
                f"      - run: '{command}'",
            )
        completed, payload = self.check()
        self.assertEqual(completed.returncode, 0, payload["errors"])

    def test_workflow_folded_single_command_run_values_are_supported(self) -> None:
        for command in (
            "python3 scripts/check-project-harness.py --root . --profile governed",
            "python3 -m unittest scripts.tests.test_operating_modes",
        ):
            self.replace(
                ".github/workflows/project-harness.yml",
                f"      - run: {command}",
                f"      - run: >\n          {command}",
            )
        completed, payload = self.check()
        self.assertEqual(completed.returncode, 0, payload["errors"])

    def test_nested_workflow_run_key_is_not_a_step_command(self) -> None:
        command = "python3 -m unittest scripts.tests.test_operating_modes"
        self.replace(
            ".github/workflows/project-harness.yml",
            f"      - run: {command}",
            "      - name: Dead nested value\n"
            "        with:\n"
            f"          run: {command}",
        )
        self.assert_error("verification workflow: missing required command")

    def test_non_job_steps_do_not_count_as_workflow_commands(self) -> None:
        workflow = (self.root / ".github/workflows/project-harness.yml").read_text(encoding="utf-8")
        workflow = workflow.replace("jobs:", "x-dead:", 1)
        write(self.root, ".github/workflows/project-harness.yml", workflow)
        self.assert_error("verification workflow: missing required command")

    def test_conditional_workflow_step_does_not_count(self) -> None:
        command = "python3 -m unittest scripts.tests.test_operating_modes"
        self.replace(
            ".github/workflows/project-harness.yml",
            f"      - run: {command}",
            f"      - if: false\n        run: {command}",
        )
        self.assert_error("verification workflow: missing required command")

    def test_conditional_workflow_job_does_not_count(self) -> None:
        self.replace(
            ".github/workflows/project-harness.yml",
            "  harness:\n    name:",
            "  harness:\n    if: true\n    name:",
        )
        self.assert_error("verification workflow: missing required command")

    def test_dead_shell_branch_does_not_count_as_workflow_command(self) -> None:
        command = "python3 -m unittest scripts.tests.test_operating_modes"
        self.replace(
            ".github/workflows/project-harness.yml",
            f"      - run: {command}",
            "      - run: |\n"
            "          if false; then\n"
            f"            {command}\n"
            "          fi",
        )
        self.assert_error("verification workflow: missing required command")

    def test_heredoc_body_does_not_count_as_workflow_command(self) -> None:
        command = "python3 -m unittest scripts.tests.test_operating_modes"
        self.replace(
            ".github/workflows/project-harness.yml",
            f"      - run: {command}",
            "      - run: |\n"
            "          cat <<'EOF'\n"
            f"          {command}\n"
            "          EOF",
        )
        self.assert_error("verification workflow: missing required command")

    def test_command_after_early_exit_does_not_count(self) -> None:
        command = "python3 -m unittest scripts.tests.test_operating_modes"
        self.replace(
            ".github/workflows/project-harness.yml",
            f"      - run: {command}",
            "      - run: |\n"
            "          exit 0\n"
            f"          {command}",
        )
        self.assert_error("verification workflow: missing required command")

    def test_daily_trigger_prose_is_outside_lifecycle_checker(self) -> None:
        self.replace("AGENTS.md", "push 5/20 SPY", "removed trigger")
        completed, payload = self.check()
        self.assertEqual(completed.returncode, 0, payload["errors"])

    def test_runbook_prose_is_outside_lifecycle_checker(self) -> None:
        self.replace(
            "docs/daily-publish-runbook.md",
            "Do not preflight, open, or restart IB Gateway before the TV attempt.",
            "Gateway first",
        )
        completed, payload = self.check()
        self.assertEqual(completed.returncode, 0, payload["errors"])

    def test_pages_workflow_source_is_outside_lifecycle_checker(self) -> None:
        self.replace(
            ".github/workflows/publish-static-reviews.yml",
            "git push --force origin gh-pages",
            "echo no publish",
        )
        completed, payload = self.check()
        self.assertEqual(completed.returncode, 0, payload["errors"])

    def test_commented_adapter_token_does_not_create_lifecycle_evidence(self) -> None:
        self.replace(
            "backend/scripts/fetch_tv_live_extended_day.py",
            "market_day_id = None if args.skip_import else import_market_json(output_path)",
            "# market_day_id = None if args.skip_import else import_market_json(output_path)\nmarket_day_id = None",
        )
        completed, payload = self.check()
        self.assertEqual(completed.returncode, 0, payload["errors"])

    def test_equivalent_adapter_refactor_does_not_fail_lifecycle_checker(self) -> None:
        self.replace(
            "backend/scripts/fetch_tv_live_extended_day.py",
            "market_day_id = None if args.skip_import else import_market_json(output_path)",
            "if args.skip_import:\n    market_day_id = None\nelse:\n    market_day_id = import_market_json(output_path)",
        )
        completed, payload = self.check()
        self.assertEqual(completed.returncode, 0, payload["errors"])

    def test_runtime_compatibility_files_are_not_required_lifecycle_formats(self) -> None:
        for relative in (
            ".github/workflows/publish-static-reviews.yml",
            "docs/daily-publish-runbook.md",
            "backend/scripts/fetch_tv_live_extended_day.py",
            "backend/scripts/fetch_ib_live_extended_day.py",
            "backend/scripts/rebuild_live_extended_db.py",
        ):
            (self.root / relative).unlink()
        completed, payload = self.check()
        self.assertEqual(completed.returncode, 0, payload["errors"])

    def test_checker_is_read_only(self) -> None:
        before = {
            str(path.relative_to(self.root)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in self.root.rglob("*")
            if path.is_file() and ".git" not in path.parts
        }
        status_before = run(["git", "status", "--porcelain=v1", "--untracked-files=all"], self.root).stdout
        completed, payload = self.check()
        self.assertEqual(completed.returncode, 0, payload["errors"])
        after = {
            str(path.relative_to(self.root)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in self.root.rglob("*")
            if path.is_file() and ".git" not in path.parts
        }
        status_after = run(["git", "status", "--porcelain=v1", "--untracked-files=all"], self.root).stdout
        self.assertEqual(before, after)
        self.assertEqual(status_before, status_after)

    def test_governed_harness_composes_external_root(self) -> None:
        completed = run(
            ["python3", str(HARNESS_CHECKER), "--root", str(self.root), "--profile", "governed"],
            PROJECT_ROOT,
        )
        payload = json.loads(completed.stdout.splitlines()[0])
        self.assertEqual(completed.returncode, 0, payload["errors"])
        self.assertTrue(payload["operating_modes"]["passed"])

    def test_minimal_harness_does_not_compose_operating_modes(self) -> None:
        minimal = Path(self.temp.name) / "minimal"
        minimal.mkdir()
        for relative in ("AGENTS.md", "INSTRUCTIONS.md", "PROGRESS.md", "HANDOFF.md", "scripts/check-project-harness.py"):
            write(minimal, relative, "# Minimal\n")
        config = {
            "schema_version": "project-harness-config-v1",
            "profile": "minimal",
            "verification_commands": ["true"],
            "github": {
                "workflow": ".github/workflows/check.yml",
                "pull_request_template": ".github/pull_request_template.md",
                "checks": ["Check"],
            },
        }
        write(minimal, ".harness/config.json", json.dumps(config))
        write(minimal, ".github/workflows/check.yml", "jobs:\n  check:\n    name: Check\n    runs-on: ubuntu-latest\n")
        write(minimal, ".github/pull_request_template.md", "# PR\n")
        init_git(minimal)
        completed = run(
            ["python3", str(HARNESS_CHECKER), "--root", str(minimal), "--profile", "minimal"],
            PROJECT_ROOT,
        )
        payload = json.loads(completed.stdout.splitlines()[0])
        self.assertEqual(completed.returncode, 0, payload["errors"])
        self.assertEqual(payload["operating_modes"], {})


if __name__ == "__main__":
    unittest.main()
