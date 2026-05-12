# Tang Strategy Frontend

Vite React client for review, browser-side scanning/backtesting, statistics, and teaching content.

## Run locally

```bash
npm install
npm run dev
```

The Vite dev server proxies `/api` to `http://localhost:8000`.

## Build

```bash
npm run build
```

The first scanner module is intentionally isolated in `src/features/review/scanner.js` so the full legacy Daily Review scanner can be ported without changing page or API contracts.
