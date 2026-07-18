## What changed and why

<!-- Describe the user-visible or operational outcome. -->

## Scope and data impact

- Changed areas:
- Data-impacted files/directories: none
- Out of scope:

## Verification

- [ ] `python3 scripts/check-project-harness.py --root . --profile auto`
- [ ] Relevant backend checks completed
- [ ] `cd frontend && npm run build`
- [ ] Manual Review/Backtest regression completed when logic or payload behavior changed

Evidence or notes:

## Harness and safety checklist

- [ ] `PROGRESS.md` and `HANDOFF.md` reflect the current state when the next gate changed
- [ ] No unrelated user changes are included
- [ ] No credentials, `.env` values, tokens, or generated historical artifacts are included
- [ ] Daily publish work, if any, followed `docs/daily-publish-runbook.md` and includes the rebuilt SQLite DB

## Screenshots or endpoint output

<!-- Add UI screenshots or `/api/reviews/assemble` evidence when relevant. -->
