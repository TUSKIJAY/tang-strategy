from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


REPO_DIR = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    db_path: Path = Path(os.environ.get("TANG_DB_PATH", REPO_DIR / "data" / "sqlite" / "tang_strategy_live_extended.db"))
    seed_dir: Path = Path(os.environ.get("TANG_SEED_DIR", REPO_DIR / "data" / "seed"))
    live_extended_dir: Path = Path(os.environ.get("TANG_LIVE_EXTENDED_DIR", REPO_DIR / "data" / "seed" / "market-data" / "live_extended"))
    strategies_dir: Path = Path(os.environ.get("TANG_STRATEGIES_DIR", REPO_DIR / "strategies" / "json"))
    content_dir: Path = Path(os.environ.get("TANG_CONTENT_DIR", REPO_DIR / "content"))
    admin_password: str = os.environ.get("TANG_ADMIN_PASSWORD", "admin-change-me")
    readonly_password: str = os.environ.get("TANG_READONLY_PASSWORD", "readonly-change-me")
    jwt_secret: str = os.environ.get("TANG_JWT_SECRET", "dev-secret-change-me")
    token_ttl_seconds: int = int(os.environ.get("TANG_TOKEN_TTL_SECONDS", "86400"))
    polygon_api_key: str = os.environ.get("POLYGON_API_KEY", "")
    ibkr_host: str = os.environ.get("IBKR_HOST", "127.0.0.1")
    ibkr_port: int = int(os.environ.get("IBKR_PORT", "4001"))


settings = Settings()
