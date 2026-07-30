from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "write-build-provenance.py"
SPEC = importlib.util.spec_from_file_location("write_build_provenance", SCRIPT)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class BuildProvenanceTests(unittest.TestCase):
    def test_manifest_contains_only_public_build_identity(self) -> None:
        value = module.build_manifest(
            "a" * 40,
            "2026-07-30T08:00:00Z",
        )
        self.assertEqual(
            value,
            {
                "schema_version": 1,
                "commit_sha": "a" * 40,
                "built_at": "2026-07-30T08:00:00Z",
            },
        )

    def test_invalid_sha_and_non_utc_time_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            module.build_manifest("main", "2026-07-30T08:00:00Z")
        with self.assertRaises(ValueError):
            module.build_manifest("a" * 40, "2026-07-30T08:00:00-04:00")

    def test_atomic_writer_emits_compact_json(self) -> None:
        value = module.build_manifest("b" * 40, "2026-07-30T08:00:00+00:00")
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "nested" / "build-manifest.json"
            module.write_manifest(path, value)
            self.assertEqual(json.loads(path.read_text()), value)

    def test_pages_workflow_writes_manifest_after_build_before_publish(self) -> None:
        workflow = (
            Path(__file__).resolve().parents[2]
            / ".github/workflows/publish-static-reviews.yml"
        ).read_text(encoding="utf-8")
        build = workflow.index("- name: Build static review site")
        provenance = workflow.index("- name: Bind build provenance to source commit")
        publish = workflow.index("- name: Publish to gh-pages branch")
        self.assertLess(build, provenance)
        self.assertLess(provenance, publish)
        self.assertIn('--commit-sha "$GITHUB_SHA"', workflow)
        self.assertIn("frontend/dist/build-manifest.json", workflow)


if __name__ == "__main__":
    unittest.main()
