# Cross-Platform TradingView Acceptance

## Phase 0 Prerequisite Assessment

| Platform/evidence | State | Evidence |
| --- | --- | --- |
| macOS real TV pair receipt | not run | Real provider access is not authorized. |
| Windows real TV pair receipt | not run | No reproducible Windows receipt was supplied or run. |
| IB fallback receipt | not run | IB/Gateway access is not authorized and no named TV hard failure opened fallback. |
| Current macOS `ZoneInfo("America/New_York")` lookup | pass | System `python3` resolved the IANA key on this host. |
| Windows IANA data availability | environment prerequisite | Must be proven by the future pinned Windows receipt; it is not inferred from macOS or an offline fixture. |

Kimi review-007's Windows observation is an environment prerequisite at this phase, not a required repository dependency edit:

- CPython `zoneinfo` uses the system timezone database and falls back to the first-party `tzdata` package; Windows commonly lacks a system IANA database.
- The reviewed Windows receipt installs `backend/requirements-tv.txt`, which pins `pandas==2.3.3`; the pandas 2.3 dependency contract includes `tzdata` as a required dependency for environments that need it.
- The project workflow also installs `requirements-tv.txt`, not only `requirements.txt`, before backend tests.
- Phase 5 remains fail-closed unless an actual Windows pinned-runtime receipt proves `America/New_York`, DST/standard offsets, calendar, quality, and pair atomicity.

Therefore no `backend/requirements*.txt` change is required for Phase 0-5 offline implementation. If the actual Windows pinned installation cannot resolve the IANA key, that receipt fails and the plan must be revised before any out-of-manifest requirements edit or Phase 6 entry.

Phase 1 created an isolated macOS environment from the unchanged `backend/requirements-tv.txt`. Resolution installed `pandas=2.3.3`, `pandas_market_calendars=5.4.0`, and transitive `tzdata=2026.3`; `ZoneInfo("America/New_York")` resolved and the complete 52-test backend suite passed. This is local dependency/validator evidence only, not a real macOS TV pair receipt and not a Windows receipt.

References:

- [Python `zoneinfo` data sources](https://docs.python.org/3/library/zoneinfo.html#data-sources)
- [pandas 2.3 installation dependencies](https://pandas.pydata.org/pandas-docs/version/2.3/getting_started/install.html#dependencies)

No real provider, broker, Windows, Pages, or hosted evidence is reported as pass.

## Phase 5 Offline Runtime And External Gate

The pinned macOS offline runtime passed with Python 3.13.5, pandas 2.3.3, pandas-market-calendars 5.4.0, exchange-calendars 4.13.2, and transitive tzdata 2026.3. `America/New_York` resolved to UTC-05:00 on 2026-01-15 and UTC-04:00 on 2026-07-15. The NYSE calendar, exact `ts` date/offset/instant plus `t` agreement, pair atomicity, pair-level contention, tracked-target refusal, provider-subprocess bootstrap, ticker-specific TradingView exchange routing, and POSIX/Windows lock code paths passed in 13 pair tests. These offline tests are not Windows or provider receipts by themselves.

### Authorized macOS real-provider receipt

Result: pass for macOS, using real anonymous TradingView access on 2026-07-19 for NYSE trade date 2026-07-17. Provider payloads, accepted temporary seeds, the candidate DB, and the complete JSON receipt remain outside the repository under `/tmp/tang-tv-macos-receipt.YKi5Y6/`.

| Evidence | Result |
| --- | --- |
| Receipt | `/tmp/tang-tv-macos-receipt.YKi5Y6/macos-tv-pair-receipt.json`; SHA-256 `6d9c4d4c9c5fd0fa7728ac5a8231373fc3c5ab69adf3e5518654b79014bf3f1a` |
| Runtime | macOS 26.5.2 arm64; Python 3.13.5; pandas 2.3.3; pandas-market-calendars 5.4.0; exchange-calendars 4.13.2; tzdata 2026.3; tvdatafeed commit `e6f6aaa7de439ac6e454d9b26d2760ded8dc4923` |
| Timezone | `America/New_York` resolved to `-05:00` on 2026-01-15 and `-04:00` on 2026-07-15 |
| SPY provider payload | `AMEX:SPY`; 868/192 total 1m/5m bars; exact RTH 390/78; zero missing or duplicate RTH minutes; SHA-256 `2086f4fe32f81794ca53cd8fe51122eb89d5103777213043649edb58780caa97` |
| QQQ provider payload | `NASDAQ:QQQ`; 915/191 total 1m/5m bars; exact RTH 390/78; zero missing or duplicate RTH minutes; SHA-256 `990fa5dccaabf145c4afcfdf3e5e33c7abc07877642d11dd17c1bd40d36e2a81` |
| Pair identity/quality | same date/session/provider; NYSE calendar; `synthetic_padding=false`; exact `ts` date/offset/instant plus `t` agreement; staged and accepted-seed hashes identical |
| Temporary candidate | 46 -> 47 market days because SPY 2026-07-17 already existed and QQQ was added; 45 non-target grandfathered days preserved; integrity `ok`; zero foreign-key failures; candidate SHA-256 `6932afc21e9e57a736837ffc39b5385d57bd3698a81a90ff9718ca1d7fc86fc7` |
| Tracked DB | before/after `76a885c2c04749e9cc5d7b5d6f75bfd15fff9939cb47d2b05c806b4c68ba28f8`; unchanged |
| Cleanup | zero warnings; no repository seed, tracked DB, Git, workflow, Pages, or hosted mutation |

The first authorized invocation stopped before any network request because the pair child process inherited a cwd-relative `PYTHONPATH`; the orchestrator now prepends the absolute backend path and the regression is pinned. The next invocation reached TradingView, accepted SPY, and rejected the pair before any DB/seed acceptance when QQQ was incorrectly requested as `AMEX:QQQ`; the orchestrator now maps SPY to AMEX and QQQ to NASDAQ, with command-level tests. Neither failed attempt changed the temporary DB, accepted seeds, or tracked DB. The provider failure was fully explained by the routing defect, so no IB call was made.

These are offline implementation facts, not provider receipts:

| Required external evidence | Final Phase 5 state | Reason |
| --- | --- | --- |
| macOS real TradingView SPY/QQQ pair | pass | Pinned-runtime receipt above passed against real TradingView with exact pair quality and temporary-candidate acceptance. |
| Windows real TradingView SPY/QQQ pair | not run | User explicitly deferred validation until preparing and pulling the repository on Windows; simulated Windows branches do not qualify. A plan-scoped `codex/project-harness` checkpoint commit/push is now explicitly authorized for that transfer, but the Windows receipt remains not run until the pulled HEAD is verified and the real command completes. |
| IB complete-pair fallback | not run | The transient QQQ failure was traced to and fixed as an AMEX/NASDAQ routing defect, after which the complete TV pair passed; IB was neither needed nor authorized. |
| Pages/hosted workflow | not run | Publication and remote workflow authority were not granted. |

### Deferred Windows continuation procedure

This is a prepared continuation procedure, not a Windows receipt. Run it only after the Windows checkout contains the authorized Phase 5 checkpoint on branch `codex/project-harness` and its HEAD matches the commit named in the transfer handoff. The user has explicitly authorized one plan-scoped checkpoint commit/push for this purpose; that Git transfer is not evidence that Windows validation passed.

Prerequisites:

- Windows has Git and the Python launcher with CPython 3.13 available as `py -3.13`.
- The checkout branch/HEAD and `git status --short --branch` are captured before execution.
- Network access to TradingView is available. Real TradingView access is authorized only for this receipt; IB/Gateway, Pages, publication, Phase 6, and tracked-DB promotion remain unauthorized.
- Run the following in PowerShell from the repository root. It creates an isolated pinned runtime and keeps every provider/candidate artifact under a unique `%TEMP%` directory.

```powershell
$ErrorActionPreference = "Stop"
$repo = (Get-Location).Path
$receiptRoot = Join-Path $env:TEMP ("tang-tv-windows-receipt-" + [guid]::NewGuid().ToString("N"))
$venv = Join-Path $receiptRoot "venv"
$dbCopy = Join-Path $receiptRoot "live.db"
$accepted = Join-Path $receiptRoot "accepted-seeds"

New-Item -ItemType Directory -Path $receiptRoot -Force | Out-Null
New-Item -ItemType Directory -Path $accepted -Force | Out-Null

git branch --show-current | Tee-Object (Join-Path $receiptRoot "branch.txt")
git rev-parse HEAD | Tee-Object (Join-Path $receiptRoot "head.txt")
git status --short --branch | Tee-Object (Join-Path $receiptRoot "git-status.txt")
Get-ComputerInfo |
  Select-Object WindowsProductName, WindowsVersion, OsBuildNumber, OsArchitecture |
  ConvertTo-Json |
  Set-Content (Join-Path $receiptRoot "windows-runtime.json")

py -3.13 -m venv $venv
$python = Join-Path $venv "Scripts\python.exe"
& $python -m pip install --upgrade pip
& $python -m pip install -r (Join-Path $repo "backend\requirements-tv.txt")
$env:PYTHONPATH = Join-Path $repo "backend"

& $python -c "from datetime import datetime; from zoneinfo import ZoneInfo; z=ZoneInfo('America/New_York'); print(datetime(2026,1,15,12,tzinfo=z).isoformat()); print(datetime(2026,7,15,12,tzinfo=z).isoformat())" |
  Tee-Object (Join-Path $receiptRoot "timezone.txt")
& $python -m unittest discover -s (Join-Path $repo "backend\tests") -p "test_update_spy_qqq_market_day.py" 2>&1 |
  Tee-Object (Join-Path $receiptRoot "focused-tests.log")
if ($LASTEXITCODE -ne 0) { throw "Focused pair tests failed" }

Copy-Item (Join-Path $repo "data\sqlite\tang_strategy_live_extended.db") $dbCopy
$trackedBefore = (Get-FileHash (Join-Path $repo "data\sqlite\tang_strategy_live_extended.db") -Algorithm SHA256).Hash.ToLower()
& $python (Join-Path $repo "backend\scripts\update_spy_qqq_market_day.py") `
  --provider tradingview `
  --db-path $dbCopy `
  --accepted-seed-dir $accepted `
  --repo-dir $repo 2>&1 |
  Tee-Object (Join-Path $receiptRoot "pair-run.log")
$pairExit = $LASTEXITCODE
if ($pairExit -ne 0) { throw "TradingView pair receipt failed with exit code $pairExit" }

$trackedAfter = (Get-FileHash (Join-Path $repo "data\sqlite\tang_strategy_live_extended.db") -Algorithm SHA256).Hash.ToLower()
if ($trackedBefore -ne $trackedAfter) { throw "Tracked DB changed during isolated receipt" }
"tracked_before=$trackedBefore" | Set-Content (Join-Path $receiptRoot "tracked-db-sha256.txt")
"tracked_after=$trackedAfter" | Add-Content (Join-Path $receiptRoot "tracked-db-sha256.txt")

& $python -c "import sqlite3,sys; c=sqlite3.connect(sys.argv[1]); print(c.execute('PRAGMA integrity_check').fetchone()[0]); print(len(c.execute('PRAGMA foreign_key_check').fetchall()))" $dbCopy |
  Tee-Object (Join-Path $receiptRoot "candidate-db-check.txt")
& $python -m pip freeze | Set-Content (Join-Path $receiptRoot "pip-freeze.txt")
Get-FileHash (Join-Path $receiptRoot "pair-run.log") -Algorithm SHA256
Write-Output "receipt_root=$receiptRoot"
```

The receipt passes only if the focused tests and pair command exit zero, the output proves both SPY and QQQ have exact 390/78 RTH bars with no missing or duplicate RTH timestamps, the candidate DB reports `ok` and zero foreign-key failures, and the tracked DB before/after hashes are identical. Retain the receipt directory, including the console logs, temporary DB, accepted seed pair, runtime metadata, and `pip-freeze.txt`. If TradingView fails, report the exact ticker and failed quality/provider gate and stop; do not silently switch to IB. Do not stage, commit, push, publish, or enter Phase 6 as part of this procedure.

Accordingly, Phase 5 is `Blocked`, not complete: the macOS receipt passed and the Windows receipt is user-deferred until the Windows checkout is prepared. The next gate remains `phase-5-external-tv-receipts`; Phase 6 is forbidden and the current SPY/Tang default/public contract remains unchanged.
