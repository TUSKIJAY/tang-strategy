from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FetchRequest:
    symbol: str
    start_date: str
    end_date: str


class MarketDataProvider:
    name = "base"

    def fetch_1m(self, request: FetchRequest) -> list[dict]:
        raise NotImplementedError
