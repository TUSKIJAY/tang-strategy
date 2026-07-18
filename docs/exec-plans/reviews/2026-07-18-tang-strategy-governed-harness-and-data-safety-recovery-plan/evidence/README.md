# Verification Evidence

This directory stores sanitized, reproducible evidence for the active governed recovery plan.

- `data-recovery-evidence.json` records the historical source commits/DB paths, normalized hashes, counts, integrity results, runtime/export reachability, and atomic promotion result.
- `data-recovery-report.md` summarizes the commands and acceptance checks in human-readable form.
- `rebuild-safety-report.md` records the fail-closed rebuild contract and isolated refusal/success tests.
- `full-verification-report.md` records the final repository, backend, frontend, browser, data, documentation, and boundary checks.
- `implementation-acceptance.md` is the delivery document submitted for independent final acceptance review.
- `../implementation-review-001.md` records the independent final verdict: `accept` with `high` confidence.

Evidence must not contain credentials, secret values, tokens used for authentication, or unredacted private configuration. A database drift fingerprint is an integrity value, not authentication material.
