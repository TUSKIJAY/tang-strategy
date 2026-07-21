from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


CHECKER = Path(__file__).resolve().parents[1] / "check-operating-modes.py"


def plan_text(slug: str, status: str, **overrides: str) -> str:
    defaults = {
        "Lifecycle schema": "`operating-modes-v1`",
        "Status": status,
        "Plan slug": f"`{slug}`",
        "Revision": "`v1`",
        "Plan author ID": "`author`",
        "Design reviews": "none",
        "Latest design verdict": "none",
        "Review independence": "none",
        "Activation evidence": "none",
        "Current phase": "none",
        "Phase state": "none",
        "Phase entry gate": "none",
        "Next gate": "design-review" if status == "Proposed" else "closed",
        "Implementation review": "none",
        "Final disposition": "none" if status != "Completed" else "Completed",
        "Verified implementation commit": "none",
        "Lifecycle reconciliation commit": "none",
    }
    defaults.update(overrides)
    bullets = "\n".join(f"- {key}: {value}" for key, value in defaults.items())
    return f"# Test Plan\n\n{bullets}\n\n## Objective\n\nTest.\n"


def review_text(plan_path: str, verdict: str = "accept") -> str:
    review_type = "implementation" if verdict == "accept" else "design"
    return f"""# Review

- Review target: `{plan_path}`
- Review target revision: `v1`
- Review type: {review_type}
- Reviewer ID: `reviewer`
- Plan author ID: `author`
- Independence declaration: `attested`
- Evidence method: repository inspection
- Verdict: {verdict}
- Confidence: high

## Findings

None.
"""


class Fixture:
    def __init__(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        base = self.root / "docs" / "exec-plans"
        for name in ("proposed", "active", "completed", "reviews"):
            (base / name).mkdir(parents=True, exist_ok=True)
        self.write_indexes()
        self.write_state()

    def close(self) -> None:
        self.temp.cleanup()

    def write(self, relative: str, text: str) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def write_indexes(self) -> None:
        self.write(
            "docs/exec-plans/proposed/index.md",
            "# Proposed\n\n| Plan | Status | Review | Next gate |\n| --- | --- | --- | --- |\n| None | — | — | none |\n",
        )
        self.write(
            "docs/exec-plans/active/index.md",
            "# Active\n\n| Plan | Current phase | Evidence | Next gate |\n| --- | --- | --- | --- |\n| None | — | — | none |\n",
        )
        self.write(
            "docs/exec-plans/completed/index.md",
            "# Completed\n\n| Plan | Disposition | Verification | Final commit |\n| --- | --- | --- | --- |\n| None | — | — | none |\n",
        )
        self.write(
            "docs/exec-plans/reviews/index.md",
            "# Reviews\n\n| Plan | Reviews | Latest verdict | Lifecycle state |\n| --- | --- | --- | --- |\n| None | — | none | None |\n",
        )
        self.write("docs/exec-plans/roadmap.md", "# Roadmap\n\nNone.\n")

    def write_state(self, *, handoff_gate: str = "none", progress_gate: str = "none") -> None:
        def block(gate: str) -> str:
            return f"""# State

<!-- operating-modes-state:start -->
- Current plan: `none`
- Lifecycle status: `None`
- Current phase: `none`
- Phase state: `none`
- Next gate: `{gate}`
<!-- operating-modes-state:end -->
"""

        self.write("PROGRESS.md", block(progress_gate))
        self.write("HANDOFF.md", block(handoff_gate))

    def add_proposed(self, slug: str = "test-plan") -> None:
        self.write(f"docs/exec-plans/proposed/{slug}.md", plan_text(slug, "Proposed"))
        self.write(
            "docs/exec-plans/proposed/index.md",
            f"# Proposed\n\n| Plan | Status | Review | Next gate |\n| --- | --- | --- | --- |\n| [Test](./{slug}.md) | Proposed | none | design-review |\n",
        )
        self.write(
            "docs/exec-plans/reviews/index.md",
            f"# Reviews\n\n| Plan | Reviews | Latest verdict | Lifecycle state |\n| --- | --- | --- | --- |\n| [Test](./{slug}/) | none | none | Proposed |\n",
        )
        self.write("docs/exec-plans/roadmap.md", f"# Roadmap\n\n- [Test](./proposed/{slug}.md)\n")

    def add_completed(self, slug: str = "done-plan", verdict: str = "accept") -> None:
        review_rel = f"../reviews/{slug}/implementation-review-001.md"
        self.write(
            f"docs/exec-plans/completed/{slug}.md",
            plan_text(slug, "Completed", **{"Implementation review": f"{review_rel}@accept"}),
        )
        self.write(
            f"docs/exec-plans/reviews/{slug}/implementation-review-001.md",
            review_text(f"docs/exec-plans/completed/{slug}.md", verdict),
        )
        self.write(
            "docs/exec-plans/completed/index.md",
            f"# Completed\n\n| Plan | Disposition | Verification | Final commit |\n| --- | --- | --- | --- |\n| [Done](./{slug}.md) | Completed | [review](../reviews/{slug}/implementation-review-001.md) | none |\n",
        )
        self.write(
            "docs/exec-plans/reviews/index.md",
            f"# Reviews\n\n| Plan | Reviews | Latest verdict | Lifecycle state |\n| --- | --- | --- | --- |\n| [Done](./{slug}/) | [review](./{slug}/implementation-review-001.md) | {verdict} | Completed |\n",
        )
        self.write("docs/exec-plans/roadmap.md", f"# Roadmap\n\n- [Done](./completed/{slug}.md)\n")

    def run(self) -> tuple[int, dict[str, object]]:
        result = subprocess.run(
            [sys.executable, str(CHECKER), "--root", str(self.root)],
            check=False,
            capture_output=True,
            text=True,
        )
        return result.returncode, json.loads(result.stdout.splitlines()[0])


class OperatingModesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fx = Fixture()

    def tearDown(self) -> None:
        self.fx.close()

    def assert_passes(self) -> None:
        code, payload = self.fx.run()
        self.assertEqual(code, 0, payload)
        self.assertTrue(payload["passed"])

    def assert_fails_with(self, phrase: str) -> None:
        code, payload = self.fx.run()
        self.assertNotEqual(code, 0, payload)
        self.assertTrue(any(phrase in error for error in payload["errors"]), payload)

    def test_empty_repository_passes(self) -> None:
        self.assert_passes()

    def test_proposed_plan_passes(self) -> None:
        self.fx.add_proposed()
        self.assert_passes()

    def test_completed_plan_with_accept_review_passes(self) -> None:
        self.fx.add_completed()
        self.assert_passes()

    def test_duplicate_plan_slug_fails(self) -> None:
        self.fx.add_proposed()
        self.fx.write("docs/exec-plans/active/test-plan.md", plan_text("test-plan", "Active"))
        self.assert_fails_with("multiple lifecycle directories")

    def test_missing_required_metadata_fails(self) -> None:
        self.fx.add_proposed()
        path = self.fx.root / "docs/exec-plans/proposed/test-plan.md"
        path.write_text(path.read_text(encoding="utf-8").replace("- Revision: `v1`\n", ""), encoding="utf-8")
        self.assert_fails_with("plan metadata missing")

    def test_status_directory_mismatch_fails(self) -> None:
        self.fx.add_proposed()
        path = self.fx.root / "docs/exec-plans/proposed/test-plan.md"
        path.write_text(path.read_text(encoding="utf-8").replace("- Status: Proposed", "- Status: Active"), encoding="utf-8")
        self.assert_fails_with("plan status mismatch")

    def test_state_index_missing_plan_fails(self) -> None:
        self.fx.add_proposed()
        self.fx.write_indexes()
        self.fx.write("docs/exec-plans/roadmap.md", "# Roadmap\n\n- [Test](./proposed/test-plan.md)\n")
        self.assert_fails_with("proposed index plan links mismatch")

    def test_roadmap_missing_plan_fails(self) -> None:
        self.fx.add_proposed()
        self.fx.write("docs/exec-plans/roadmap.md", "# Roadmap\n\nNone.\n")
        self.assert_fails_with("roadmap must link plan once")

    def test_review_latest_verdict_mismatch_fails(self) -> None:
        self.fx.add_completed()
        index = self.fx.root / "docs/exec-plans/reviews/index.md"
        index.write_text(index.read_text(encoding="utf-8").replace("| accept | Completed |", "| revise | Completed |"), encoding="utf-8")
        self.assert_fails_with("latest verdict mismatch")

    def test_completed_plan_requires_accept_verdict(self) -> None:
        self.fx.add_completed(verdict="revise")
        self.assert_fails_with("verdict is not accept")

    def test_progress_and_handoff_must_match(self) -> None:
        self.fx.write_state(handoff_gate="closed", progress_gate="none")
        self.assert_fails_with("current-state blocks differ")

    def test_none_state_has_fixed_values(self) -> None:
        self.fx.write_state(handoff_gate="closed", progress_gate="closed")
        self.assert_fails_with("does not match canonical plan")


if __name__ == "__main__":
    unittest.main()
