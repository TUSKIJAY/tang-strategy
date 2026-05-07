from __future__ import annotations

from app.settings import settings
from app.services.importer import import_default_seed


def rebuild_db() -> None:
    seed_files = sorted(settings.live_extended_dir.glob("**/*.json"))
    market_day_files = [path for path in seed_files if path.name.startswith("SPY_") or path.name.startswith("SPX_")]
    if not market_day_files:
        print(
            f"Refusing to rebuild: no SPY_/SPX_ market-day JSON files found under {settings.live_extended_dir}. "
            "Place files as YYYY-MM-DD/SPY_YYYY-MM-DD.json first."
        )
        return

    if settings.db_path.exists():
        settings.db_path.unlink()
    result = import_default_seed()
    print(f"Rebuilt sqlite DB at {settings.db_path}: {result}")


if __name__ == "__main__":
    rebuild_db()
