from __future__ import annotations

from .base import FetchRequest, MarketDataProvider


class IbkrProvider(MarketDataProvider):
    name = "ibkr"

    def fetch_1m(self, request: FetchRequest) -> list[dict]:
        raise RuntimeError("IBKR fetch is configured for a later phase; import existing JSON for now.")
