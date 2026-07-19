# Tang Strategy

Tang Strategy is a FastAPI and React/Vite workspace for authenticated market-day review, browser-side strategy backtesting, teaching replay, and static GitHub Pages reviews.

## Runtime Model

- Interactive mode: React calls the FastAPI bearer-auth API and reads the tracked SQLite DB.
- Static Pages mode: CI exports review JSON from the same tracked DB, builds `StaticReviewsApp`, and publishes `frontend/dist` to `gh-pages`.
- Daily source mode: the repository SPY/QQQ pair orchestrator attempts TradingView first; IB Gateway is fallback-only after TV retries or a named hard quality-gate failure.
- Database rebuild: seed data imports into a fresh candidate, validates semantic/integrity/superset gates, and is atomically promoted only when safe.

The runtime and Pages data source is `data/sqlite/tang_strategy_live_extended.db`. Gitignored files under `data/seed/market-data/live_extended/` are local fetch/import inputs, not the committed publication input.

## Layout

- `backend/app/` — API, auth, DB schema/access, imports, and review assembly.
- `backend/scripts/` — TV/IB fetchers, safe rebuild, recovery, and static export.
- `backend/tests/` — data-quality and DB-safety tests.
- `frontend/src/` — Data, Review, Backtest, Teaching, scanner, and shared kline UI.
- `strategies/` — strategy JSON plus the canonical [`STRATEGY.md`](./strategies/STRATEGY.md).
- `content/` — teaching/rule/case assets plus normalized trader registry and SPY/QQQ trade records.
- `data/` — local seed contract and tracked SQLite runtime.
- `docs/` — product/architecture docs plus controlled governed lifecycle records; generated site output does not live here.

## Run The Stack

```bash
cp .env.example .env
docker compose up --build
```

Open `http://localhost:18080`; the backend is published at `http://localhost:18091` by the Docker workspace.

Backend only:

```bash
cd backend
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. uvicorn app.main:app --reload
```

Frontend only:

```bash
cd frontend
npm install
npm run dev
```

## Safe Rebuild

```bash
cd backend
PYTHONPATH=. python scripts/rebuild_live_extended_db.py
```

The default command rejects empty/invalid candidates, date loss, non-market key shrink, integrity failures, and concurrent source drift. Do not use `--allow-date-loss` in daily publication or normal automation.

The default daily market-data entry is `PYTHONPATH=. python scripts/update_spy_qqq_market_day.py <YYYY-MM-DD> --provider tradingview` from `backend/`. It accepts both tickers from one provider through one candidate or preserves the prior pair and DB.

## Verification And Documentation

Use [`AGENTS.md`](./AGENTS.md) for repository rules, [`INSTRUCTIONS.md`](./INSTRUCTIONS.md) for stable contracts, [`docs/README.md`](./docs/README.md) for the documentation authority map, and [`docs/daily-publish-runbook.md`](./docs/daily-publish-runbook.md) for separately authorized daily publication.
