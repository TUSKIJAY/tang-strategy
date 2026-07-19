from __future__ import annotations

import csv
import io
import json
from typing import Any, Iterable, Mapping

from .trade_records import TRADE_RECORDS_SCHEMA_VERSION, assert_no_raw_evidence_fields


GROUP_COLUMNS = (
    "trade_group_id",
    "trader_id",
    "underlying",
    "trade_date",
    "direction",
    "status",
    "review_status",
    "display_eligible",
    "reported_stats_eligible",
    "calculated_stats_eligible",
    "reported_return_pct",
    "calculated_return_pct",
    "result_conflict",
    "normalization_method",
)
LEG_COLUMNS = (
    "leg_id",
    "trade_group_id",
    "instrument_type",
    "position_side",
    "option_type",
    "strike",
    "expiry",
    "expiry_provenance",
    "contract_multiplier",
    "contract_multiplier_provenance",
)
EVENT_COLUMNS = (
    "event_id",
    "leg_id",
    "trade_group_id",
    "sequence",
    "action",
    "occurred_at",
    "time_precision",
    "time_incomplete",
    "premium",
    "quantity",
    "fees",
    "note",
)


class TradeExportError(ValueError):
    """Raised when an export payload is not the frozen public shape."""


def render_trade_exports(payload: Mapping[str, Any]) -> dict[str, str]:
    if payload.get("schema_version") != TRADE_RECORDS_SCHEMA_VERSION:
        raise TradeExportError(f"payload must use {TRADE_RECORDS_SCHEMA_VERSION}")
    groups = payload.get("trade_groups")
    if not isinstance(groups, list):
        raise TradeExportError("payload.trade_groups must be an array")
    metadata = payload.get("export_metadata")
    if not isinstance(metadata, Mapping):
        raise TradeExportError("payload.export_metadata must be an object")
    if metadata.get("includes_bars") is not False or metadata.get("raw_evidence_included") is not False:
        raise TradeExportError("trade exports must exclude bars and raw evidence")
    assert_no_raw_evidence_fields(payload)

    group_rows: list[dict[str, Any]] = []
    leg_rows: list[dict[str, Any]] = []
    event_rows: list[dict[str, Any]] = []
    seen_legs: set[str] = set()
    seen_events: set[str] = set()
    for group in groups:
        group_id = _required_text(group, "trade_group_id")
        reported = group.get("reported_outcome") or {}
        calculated = group.get("calculated_outcome") or {}
        group_rows.append(
            {
                "trade_group_id": group_id,
                "trader_id": group.get("trader_id"),
                "underlying": group.get("underlying"),
                "trade_date": group.get("trade_date"),
                "direction": group.get("direction"),
                "status": group.get("status"),
                "review_status": group.get("review_status"),
                "display_eligible": group.get("display_eligible"),
                "reported_stats_eligible": group.get("reported_stats_eligible"),
                "calculated_stats_eligible": group.get("calculated_stats_eligible"),
                "reported_return_pct": reported.get("return_pct"),
                "calculated_return_pct": calculated.get("return_pct"),
                "result_conflict": group.get("result_conflict"),
                "normalization_method": group.get("normalization_method"),
            }
        )
        legs = group.get("legs")
        if not isinstance(legs, list):
            raise TradeExportError(f"{group_id}.legs must be an array")
        for leg in legs:
            leg_id = _required_text(leg, "leg_id")
            if leg_id in seen_legs:
                raise TradeExportError(f"duplicate leg ID in export: {leg_id}")
            seen_legs.add(leg_id)
            leg_rows.append(
                {
                    "leg_id": leg_id,
                    "trade_group_id": group_id,
                    "instrument_type": leg.get("instrument_type"),
                    "position_side": leg.get("position_side"),
                    "option_type": leg.get("option_type"),
                    "strike": leg.get("strike"),
                    "expiry": leg.get("expiry"),
                    "expiry_provenance": leg.get("expiry_provenance"),
                    "contract_multiplier": leg.get("contract_multiplier"),
                    "contract_multiplier_provenance": leg.get("contract_multiplier_provenance"),
                }
            )
            events = leg.get("events")
            if not isinstance(events, list):
                raise TradeExportError(f"{leg_id}.events must be an array")
            for event in events:
                event_id = _required_text(event, "event_id")
                if event_id in seen_events:
                    raise TradeExportError(f"duplicate event ID in export: {event_id}")
                seen_events.add(event_id)
                event_rows.append(
                    {
                        "event_id": event_id,
                        "leg_id": leg_id,
                        "trade_group_id": group_id,
                        "sequence": event.get("sequence"),
                        "action": event.get("action"),
                        "occurred_at": event.get("occurred_at"),
                        "time_precision": event.get("time_precision"),
                        "time_incomplete": event.get("time_incomplete"),
                        "premium": event.get("premium"),
                        "quantity": event.get("quantity"),
                        "fees": event.get("fees"),
                        "note": event.get("note"),
                    }
                )

    group_ids = {row["trade_group_id"] for row in group_rows}
    if any(row["trade_group_id"] not in group_ids for row in leg_rows):
        raise TradeExportError("leg export contains an orphan group foreign key")
    if any(row["leg_id"] not in seen_legs for row in event_rows):
        raise TradeExportError("event export contains an orphan leg foreign key")

    json_filename = metadata.get("json_filename")
    if not isinstance(json_filename, str) or not json_filename:
        raise TradeExportError("export_metadata.json_filename must be non-empty")
    return {
        json_filename: json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n",
        "trade_groups.csv": _render_csv(GROUP_COLUMNS, group_rows),
        "trade_legs.csv": _render_csv(LEG_COLUMNS, leg_rows),
        "trade_events.csv": _render_csv(EVENT_COLUMNS, event_rows),
    }


def _render_csv(columns: tuple[str, ...], rows: Iterable[Mapping[str, Any]]) -> str:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=columns, extrasaction="raise", lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({column: _csv_value(row.get(column)) for column in columns})
    return output.getvalue()


def _csv_value(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return value


def _required_text(item: Mapping[str, Any], field: str) -> str:
    value = item.get(field)
    if not isinstance(value, str) or not value:
        raise TradeExportError(f"{field} must be a non-empty string")
    return value
