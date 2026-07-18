# Rebuild Safety Evidence

- Date: 2026-07-18
- Real tracked DB used as a rebuild target: no
- Result: pass

## Implemented Contract

- seed discovery and parsing occur before candidate promotion;
- empty/non-list bars, duplicate logical keys, missing/duplicate timestamps, invalid/non-finite OHLCV/VWAP, and seed metadata count mismatch fail nonzero;
- import runs against a fresh adjacent candidate DB;
- candidate market-day keys must exactly match discovered seed keys;
- each candidate day requires non-empty 1m/5m rows with seed, declared, actual, and distinct-index counts equal;
- SQLite integrity and foreign keys must pass;
- current market-day keys must be a subset of candidate keys by default;
- current strategy slugs and teaching keys must remain subsets regardless of date-loss override;
- `--allow-date-loss` relaxes only the intentional market-day subset gate;
- a SQLite-consistent baseline snapshot and live DB identity/byte/logical fingerprint prevent stale-candidate promotion;
- candidate and parent directory are flushed before/after same-filesystem `os.replace`;
- any failure abandons the candidate and leaves current DB bytes or a concurrent new write intact.

## Focused Tests

Command:

```bash
PYTHONWARNINGS=error::ResourceWarning PYTHONPATH=backend \
  python3 -m unittest backend.tests.test_rebuild_live_extended_db -v
```

Result: 11 tests passed.

| Test case | Result |
| --- | --- |
| no seed | refused; original bytes unchanged |
| subset seed | refused; exact missing logical day printed; bytes unchanged |
| explicit date-loss override | intentional shrink succeeded |
| candidate import exception | refused; bytes unchanged |
| corrupt/integrity-failing candidate | refused; bytes unchanged |
| date-complete candidate with empty bars | refused; bytes unchanged |
| seed metadata count mismatch | refused before candidate promotion |
| strategy shrink, including with date override | refused; bytes unchanged |
| teaching shrink | refused; bytes unchanged |
| complete superset | atomically promoted in temporary workspace |
| source drift after candidate import | refused; concurrent new write preserved |

The shared DB safety tests also passed 4/4 for consistent snapshot/promotion, ID-independent day hashes, post-validation rollback, and source-drift preservation.

## Real Six-Day Seed Against A 46-Day Copy

The promoted 46-day tracked DB was copied with SQLite backup into `/tmp/tang-rebuild-six-day.Cw9mq3/live-copy.db`. The default rebuild CLI targeted only that copy and used the repository's actual six local seed days.

```bash
cd backend
PYTHONPATH=. .venv/bin/python scripts/rebuild_live_extended_db.py \
  --db-path /tmp/tang-rebuild-six-day.Cw9mq3/live-copy.db \
  --live-extended-dir ../data/seed/market-data/live_extended \
  --strategies-dir ../strategies/json \
  --content-dir ../content
```

Result:

- exit code: 1;
- copy market days after refusal: 46;
- copy integrity: `ok`;
- byte SHA-256 before: `566025ca4c036c4e73c14e9fbf39de11585f4b1684a137dc44f689275ab865e1`;
- byte SHA-256 after: `566025ca4c036c4e73c14e9fbf39de11585f4b1684a137dc44f689275ab865e1`;
- missing list: all 40 dates present in the current DB but absent from the six-day seed, ending with `SPY|2026-07-17|extended`.

The tracked DB was not opened as a rebuild target. No fetch, broker connection, export to repository paths, publish, commit, stage, push, merge, PR, or remote setting occurred.
