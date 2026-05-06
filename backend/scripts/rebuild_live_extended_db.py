from __future__ import annotations

from app.settings import settings
from app.services.importer import import_default_seed


def rebuild_db() -> None:
    if settings.db_path.exists():
        settings.db_path.unlink()
    result = import_default_seed()
    print(f"Rebuilt sqlite DB at {settings.db_path}: {result}")


if __name__ == "__main__":
    rebuild_db()
