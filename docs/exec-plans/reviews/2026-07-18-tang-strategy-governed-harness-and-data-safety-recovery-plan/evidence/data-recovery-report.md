# Data Recovery Evidence

- Date: 2026-07-18
- Target: `data/sqlite/tang_strategy_live_extended.db`
- Result: pass; verified candidate atomically promoted
- Remote effects: none; no fetch, broker connection, export to repository paths, commit, push, Pages workflow, or publish occurred

## Sources And Logical Mapping

| Logical day | Historical commit | Source day ID | Candidate day ID | 1m | 5m | First/last 1m | First/last 5m |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| `SPY|2026-05-15|extended` | `34caa03` | 4 | 44 | 960 | 192 | 04:00 / 19:59 ET | 04:00 / 19:55 ET |
| `SPY|2026-06-30|extended` | `1f15443` | 33 | 45 | 960 | 192 | 04:00 / 19:59 ET | 04:00 / 19:55 ET |
| `SPY|2026-07-01|extended` | `1f15443` | 34 | 46 | 960 | 192 | 04:00 / 19:59 ET | 04:00 / 19:55 ET |

Historical `market_days.id` values were recorded only as evidence. Recovery inserted by `(ticker, trade_date, session_mode)`, resolved new candidate IDs, mapped ticker by symbol, and copied bars with the resolved candidate foreign key. Source and candidate ticker IDs happened to be 1, but the implementation did not depend on that equality.

The complete safe provenance, first/last bars, OHLCV/VWAP summaries, declared/actual counts, and source paths are in `data-recovery-evidence.json`. Operator notes and credential-like metadata are not included in the evidence artifact.

## Normalized Hashes

Canonical serialization and projections are defined in the active plan and implemented once in `backend/app/services/db_safety.py`.

| Logical day | market day SHA-256 | 1m SHA-256 | 5m SHA-256 |
| --- | --- | --- | --- |
| 2026-05-15 | `2366460d1410ac140f0e097b890895938c8071733151527fd7a5f271e9e8292e` | `028c601bd48e23417f627cdda74b323c8207418e5e9d1c567265441f2a6fb941` | `b0699d8e3fac0983bb8a93b31e6b24b0bd4dfff10386c2211deecd44165076ab` |
| 2026-06-30 | `aa9524c7024f1c57d9a3a3882ccf9b746db39f95db721f2b02493ac592908d75` | `6fddb3acc8cd7b18822d441daaecb5cf50b2b024ec83b712b364e0004a756a62` | `5067437246e54691da078aada495a4271ceb467551957253083f88313bf6fe30` |
| 2026-07-01 | `120b180cd856b41d830651b3017d1321543267b58d6a127d227516b9efa32819` | `d18c99a4574b1e046979fd3452868db75ec0fb9583382c2ef6c7b40135cd0285` | `790357a86428e8f2fa33249a8b4c645f9a0ab321b555c9b53a098e39ded3fbbb` |

Each source/candidate digest pair matched.

## Preservation Proof

| Check | Before | Candidate/after | Result |
| --- | --- | --- | --- |
| Market-day count | 43 | 46 | exactly three additions |
| Original 43-day digest map | `4da75bbf46093df46a6f9daba5f3b54a5b840d46e6c08ff8e0bd83da38cac4a3` | `4da75bbf46093df46a6f9daba5f3b54a5b840d46e6c08ff8e0bd83da38cac4a3` | pass; mismatch set empty |
| Strategies table | `7c03ad9aa6b48161ab96d02b1c354fbe9f6393d26f0fe452b2b0d33534cb689a` | same | pass |
| Teaching assets table | `9ab2647fc700050a0676f416feb12554c3d6c426545fecf1990fb1ce1921fadb` | same | pass |
| Original DB bytes | `67e4fba9bcbd104c8e2aea6d6138a10f9c7d4c38198ad0384d5edf6e6de65924` | candidate `76a885c2c04749e9cc5d7b5d6f75bfd15fff9939cb47d2b05c806b4c68ba28f8` | expected binary change |
| Post-promotion DB bytes | — | `76a885c2c04749e9cc5d7b5d6f75bfd15fff9939cb47d2b05c806b4c68ba28f8` | equals verified candidate |

Promotion used a SQLite backup snapshot, shared repository write lock, baseline path identity/byte/logical fingerprint, pre-promotion drift recheck, same-directory candidate, file and directory flush, and `os.replace`. The backup remained available through post-promotion validation and was removed only after the checks passed.

## Integrity And Runtime Reachability

- `PRAGMA integrity_check`: `ok`
- `PRAGMA foreign_key_check`: 0 rows
- SPY 2026-07-17 with `tang-v4-4-slope-4-4`: 868 1m bars and 192 5m bars
- static export from the candidate and promoted DB: 46 SPY days, 9 v3/v4/v5 strategies
- 2026-06-30 exported Tang overlay: 1 trade, 0 notes, 960/192 bars
- 2026-07-01 exported Tang overlay: 1 trade, 0 notes, 960/192 bars
- export output was written only to an explicit temporary directory

## Commands

Historical sources and the isolated current DB copy:

```bash
git show '34caa03:data/sqlite/tang_strategy_live_extended.db' > /tmp/tang-recovery-test.8KhOrZ/34caa03.db
git show '1f15443:data/sqlite/tang_strategy_live_extended.db' > /tmp/tang-recovery-test.8KhOrZ/1f15443.db
python3 -c '<SQLite immutable source.backup into /tmp/current-copy.db>'
```

Focused safety tests and full isolated recovery rehearsal:

```bash
PYTHONWARNINGS=error::ResourceWarning PYTHONPATH=backend python3 -m unittest backend.tests.test_db_safety -v
cd backend
PYTHONPATH=. .venv/bin/python scripts/recover_historical_market_days.py \
  --target-db /tmp/tang-recovery-test.8KhOrZ/current-copy-2.db \
  --source 'SPY|2026-05-15|extended=/tmp/tang-recovery-test.8KhOrZ/34caa03.db' \
  --source 'SPY|2026-06-30|extended=/tmp/tang-recovery-test.8KhOrZ/1f15443.db' \
  --source 'SPY|2026-07-01|extended=/tmp/tang-recovery-test.8KhOrZ/1f15443.db' \
  --expected-before 43 --expected-after 46 --promote
```

Real candidate construction and guarded promotion used the identical command with only the target/evidence paths changed:

```bash
cd backend
PYTHONPATH=. .venv/bin/python scripts/recover_historical_market_days.py \
  --target-db ../data/sqlite/tang_strategy_live_extended.db \
  --source 'SPY|2026-05-15|extended=/tmp/tang-recovery-test.8KhOrZ/34caa03.db' \
  --source 'SPY|2026-06-30|extended=/tmp/tang-recovery-test.8KhOrZ/1f15443.db' \
  --source 'SPY|2026-07-01|extended=/tmp/tang-recovery-test.8KhOrZ/1f15443.db' \
  --expected-before 43 --expected-after 46 --promote \
  --evidence-json ../docs/exec-plans/reviews/2026-07-18-tang-strategy-governed-harness-and-data-safety-recovery-plan/evidence/data-recovery-evidence.json
```

Post-promotion verification repeated immutable count/integrity/foreign-key queries, direct `/api/reviews/assemble` function execution, and `export_static_reviews.py` to `/tmp/tang-post-recovery-export.*`.

## Publication Boundary

No TradingView/IB fetch was run. No repository `frontend/public/reviews` or `frontend/dist` output was produced. No GitHub workflow, Pages publish, commit, stage, push, merge, PR, or remote setting was invoked.
