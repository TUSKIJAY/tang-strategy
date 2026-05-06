# Seed data directory

`data/seed/market-data/live_extended/` is the active drop location for source minute JSON to be imported by backend.

Keep this directory empty until new fetches are available; re-run the backend rebuild command after placing new files:

```bash
cd backend
PYTHONPATH=. python scripts/rebuild_live_extended_db.py
```
