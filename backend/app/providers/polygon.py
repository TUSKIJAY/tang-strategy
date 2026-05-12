from __future__ import annotations

from .base import FetchRequest, MarketDataProvider


class PolygonProvider(MarketDataProvider):
    name = "polygon"

    def fetch_1m(self, request: FetchRequest) -> list[dict]:
        raise RuntimeError("Polygon fetch is configured for a later phase; import existing JSON for now.")
