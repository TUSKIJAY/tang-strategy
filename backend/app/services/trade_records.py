from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import tempfile
from datetime import date, datetime
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


TRADER_SCHEMA_VERSION = "traders-v1"
TRADE_DAY_SCHEMA_VERSION = "trades-day-v1"
TRADE_RECORDS_SCHEMA_VERSION = "trade-records-v1"
NEW_YORK_ZONE = "America/New_York"

UNDERLYINGS = {"SPY", "QQQ"}
DIRECTIONS = {"CALL", "PUT"}
RECORD_STATUSES = {"active", "voided", "superseded"}
REVIEW_STATUSES = {"pending", "verified"}
EVENT_ACTIONS = {"buy_open", "buy_add", "sell_partial", "sell_close"}
TIME_PRECISIONS = {"exact", "minute", "approximate"}
FACT_PROVENANCE = {
    "user_provided",
    "legacy_preserved",
    "legacy_rule_extract",
    "rule_default",
    "unknown",
}

TRADER_FIELDS = {"trader_id", "display_name", "color", "active", "sort_order"}
DAY_FIELDS = {"schema_version", "trade_date", "timezone", "trade_groups", "note_contexts"}
GROUP_FIELDS = {
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
    "supersedes_trade_group_id",
    "legs",
    "reported_outcome",
    "calculated_outcome",
    "result_conflict",
    "notes",
    "normalization",
}
LEG_FIELDS = {
    "leg_id",
    "instrument_type",
    "position_side",
    "option_type",
    "strike",
    "expiry",
    "expiry_provenance",
    "contract_multiplier",
    "contract_multiplier_provenance",
    "events",
}
EVENT_FIELDS = {
    "event_id",
    "sequence",
    "action",
    "occurred_at",
    "time_precision",
    "time_incomplete",
    "premium",
    "quantity",
    "fees",
    "note",
    "fact_provenance",
}
NOTE_FIELDS = {"text", "provenance"}
NORMALIZATION_FIELDS = {"method", "source", "source_path", "source_index", "review_flags"}
CONTEXT_FIELDS = {
    "context_id",
    "trader_id",
    "underlying",
    "trade_date",
    "text",
    "status",
    "review_status",
    "normalization",
}
REPORTED_OUTCOME_FIELDS = {"return_pct", "gross_pnl", "net_pnl", "provenance", "note"}
CALCULATED_OUTCOME_FIELDS = {
    "return_pct",
    "gross_pnl",
    "net_pnl",
    "closed_quantity",
    "average_entry_premium",
    "average_exit_premium",
    "calculation_version",
}

PUBLIC_TRADER_FIELDS = ("trader_id", "display_name", "color", "active", "sort_order")
PUBLIC_GROUP_FIELDS = (
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
    "supersedes_trade_group_id",
    "legs",
    "reported_outcome",
    "calculated_outcome",
    "result_conflict",
    "notes",
)
PUBLIC_CONTEXT_FIELDS = (
    "context_id",
    "trader_id",
    "underlying",
    "trade_date",
    "text",
    "status",
    "review_status",
)

FORBIDDEN_EVIDENCE_KEYS = {
    "attachment",
    "attachments",
    "chat_export",
    "chat_transcript",
    "discord_export",
    "evidence_blob",
    "image_base64",
    "raw_chat",
    "raw_evidence",
    "raw_message",
    "screenshot",
    "screenshots",
}

_TRADER_ID_RE = re.compile(r"^[a-z][a-z0-9_]{1,63}$")
_STABLE_ID_RE = re.compile(r"^[a-z][a-z0-9_]{2,191}$")
_GROUP_ID_RE = re.compile(r"^tg_[a-z0-9_]{3,124}$")
_CONTEXT_ID_RE = re.compile(r"^ctx_[a-z0-9_]{3,124}$")
_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
_EXPLICIT_OFFSET_RE = re.compile(r"(?:Z|[+-]\d{2}:\d{2})$")


class TradeValidationError(ValueError):
    """Raised when canonical trade content violates the frozen contract."""


class TradeAuthorizationError(PermissionError):
    """Raised by unregistered service handlers when a role exceeds its authority."""


def load_trader_registry(path: Path) -> dict[str, Any]:
    return validate_trader_registry(_load_json(path))


def validate_trader_registry(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = copy.deepcopy(dict(payload))
    _require_exact_keys(data, {"schema_version", "traders"}, "registry")
    if data["schema_version"] != TRADER_SCHEMA_VERSION:
        _fail("registry.schema_version", f"must be {TRADER_SCHEMA_VERSION}")
    traders = _require_list(data["traders"], "registry.traders")
    seen_ids: set[str] = set()
    seen_colors: set[str] = set()
    seen_orders: set[int] = set()
    for index, trader in enumerate(traders):
        path = f"registry.traders[{index}]"
        item = _require_mapping(trader, path)
        _require_exact_keys(item, TRADER_FIELDS, path)
        trader_id = _require_string(item["trader_id"], f"{path}.trader_id")
        if not _TRADER_ID_RE.fullmatch(trader_id):
            _fail(f"{path}.trader_id", "must be a stable lowercase slug")
        if trader_id in seen_ids:
            _fail(f"{path}.trader_id", f"duplicate trader ID {trader_id}")
        seen_ids.add(trader_id)
        _require_nonempty_string(item["display_name"], f"{path}.display_name")
        color = _require_string(item["color"], f"{path}.color")
        if not _COLOR_RE.fullmatch(color):
            _fail(f"{path}.color", "must be a six-digit hex color")
        normalized_color = color.lower()
        if normalized_color in seen_colors:
            _fail(f"{path}.color", "active trader colors must remain distinct")
        seen_colors.add(normalized_color)
        _require_bool(item["active"], f"{path}.active")
        sort_order = _require_nonnegative_int(item["sort_order"], f"{path}.sort_order")
        if sort_order in seen_orders:
            _fail(f"{path}.sort_order", "must be unique")
        seen_orders.add(sort_order)
    assert_no_raw_evidence_fields(data)
    return data


def normalize_trade_day(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Apply only declared rule defaults; never infer fills, times, or outcomes."""

    data = copy.deepcopy(dict(payload))
    trade_date = data.get("trade_date")
    for group in data.get("trade_groups", []):
        if not isinstance(group, dict):
            continue
        group.setdefault("trade_date", trade_date)
        group.setdefault("supersedes_trade_group_id", None)
        for leg in group.get("legs", []):
            if not isinstance(leg, dict):
                continue
            if not leg.get("expiry"):
                leg["expiry"] = trade_date
                leg["expiry_provenance"] = "rule_default"
            if leg.get("contract_multiplier") is None:
                leg["contract_multiplier"] = 100
                leg["contract_multiplier_provenance"] = "rule_default"
    return data


def load_trade_day(
    path: Path,
    registry: Mapping[str, Any],
    repository_ids: set[str] | None = None,
) -> dict[str, Any]:
    return validate_trade_day(_load_json(path), registry, repository_ids=repository_ids)


def validate_trade_day(
    payload: Mapping[str, Any],
    registry: Mapping[str, Any],
    repository_ids: set[str] | None = None,
) -> dict[str, Any]:
    data = normalize_trade_day(payload)
    registry_data = validate_trader_registry(registry)
    trader_ids = {item["trader_id"] for item in registry_data["traders"]}
    _require_exact_keys(data, DAY_FIELDS, "trade_day")
    if data["schema_version"] != TRADE_DAY_SCHEMA_VERSION:
        _fail("trade_day.schema_version", f"must be {TRADE_DAY_SCHEMA_VERSION}")
    trade_date = _require_date(data["trade_date"], "trade_day.trade_date")
    if data["timezone"] != NEW_YORK_ZONE:
        _fail("trade_day.timezone", f"must be {NEW_YORK_ZONE}")
    try:
        timezone = ZoneInfo(NEW_YORK_ZONE)
    except ZoneInfoNotFoundError as exc:
        raise TradeValidationError(
            f"trade_day.timezone: IANA data for {NEW_YORK_ZONE} is unavailable"
        ) from exc

    seen_ids = repository_ids if repository_ids is not None else set()
    local_ids: set[str] = set()
    groups = _require_list(data["trade_groups"], "trade_day.trade_groups")
    for group_index, group in enumerate(groups):
        _validate_group(
            _require_mapping(group, f"trade_day.trade_groups[{group_index}]"),
            f"trade_day.trade_groups[{group_index}]",
            trade_date,
            timezone,
            trader_ids,
            seen_ids,
            local_ids,
        )
    contexts = _require_list(data["note_contexts"], "trade_day.note_contexts")
    for context_index, context in enumerate(contexts):
        _validate_context(
            _require_mapping(context, f"trade_day.note_contexts[{context_index}]"),
            f"trade_day.note_contexts[{context_index}]",
            trade_date,
            trader_ids,
            seen_ids,
            local_ids,
        )
    if repository_ids is not None:
        repository_ids.update(local_ids)
    assert_no_raw_evidence_fields(data)
    return data


def validate_trade_repository(
    paths: Iterable[Path],
    registry: Mapping[str, Any],
) -> list[dict[str, Any]]:
    seen_ids: set[str] = set()
    days = [load_trade_day(path, registry, repository_ids=seen_ids) for path in sorted(paths)]
    dates = [day["trade_date"] for day in days]
    if len(dates) != len(set(dates)):
        _fail("trade_repository", "contains duplicate daily files for one trade date")
    return days


def occurred_at_from_local_time(
    trade_date: str,
    local_time: str,
    precision: str = "minute",
) -> str:
    parsed_date = _require_date(trade_date, "trade_date")
    if precision not in TIME_PRECISIONS:
        _fail("precision", f"must be one of {sorted(TIME_PRECISIONS)}")
    try:
        parsed_time = datetime.strptime(local_time.strip(), "%H:%M").time()
    except (TypeError, ValueError) as exc:
        raise TradeValidationError("local_time: must use HH:MM") from exc
    try:
        timezone = ZoneInfo(NEW_YORK_ZONE)
    except ZoneInfoNotFoundError as exc:
        raise TradeValidationError(f"IANA data for {NEW_YORK_ZONE} is unavailable") from exc
    return datetime.combine(parsed_date, parsed_time, tzinfo=timezone).isoformat(timespec="minutes")


def build_trade_records_payload(
    registry: Mapping[str, Any],
    trade_day: Mapping[str, Any],
    ticker: str,
    trader_ids: Sequence[str] | None = None,
    statuses: Sequence[str] | None = None,
    review_statuses: Sequence[str] | None = None,
    display_only: bool = False,
) -> dict[str, Any]:
    registry_data = validate_trader_registry(registry)
    day = validate_trade_day(trade_day, registry_data)
    selected_ticker = ticker.upper()
    if selected_ticker not in UNDERLYINGS:
        _fail("ticker", f"must be one of {sorted(UNDERLYINGS)}")
    trader_filter = set(trader_ids or [])
    status_filter = set(statuses or RECORD_STATUSES)
    review_filter = set(review_statuses or REVIEW_STATUSES)
    if not status_filter <= RECORD_STATUSES:
        _fail("statuses", "contains an unsupported record status")
    if not review_filter <= REVIEW_STATUSES:
        _fail("review_statuses", "contains an unsupported review status")
    known_traders = {item["trader_id"] for item in registry_data["traders"]}
    if not trader_filter <= known_traders:
        _fail("trader_ids", "contains an unknown trader ID")

    selected_groups = []
    for group in day["trade_groups"]:
        if group["underlying"] != selected_ticker:
            continue
        if trader_filter and group["trader_id"] not in trader_filter:
            continue
        if group["status"] not in status_filter or group["review_status"] not in review_filter:
            continue
        if display_only and not group["display_eligible"]:
            continue
        selected_groups.append(_public_group(group))

    selected_contexts = []
    for context in day["note_contexts"]:
        if context["underlying"] != selected_ticker:
            continue
        if trader_filter and context["trader_id"] not in trader_filter:
            continue
        if context["status"] not in status_filter or context["review_status"] not in review_filter:
            continue
        selected_contexts.append(_public_context(context))

    referenced_traders = {group["trader_id"] for group in selected_groups}
    referenced_traders.update(context["trader_id"] for context in selected_contexts)
    traders = [
        {field: item[field] for field in PUBLIC_TRADER_FIELDS}
        for item in registry_data["traders"]
        if item["active"] or item["trader_id"] in referenced_traders
    ]
    traders.sort(key=lambda item: (item["sort_order"], item["trader_id"]))
    selected_groups.sort(key=_group_sort_key)
    selected_contexts.sort(key=lambda item: (item["trader_id"], item["context_id"]))

    selection = {
        "ticker": selected_ticker,
        "trade_date": day["trade_date"],
        "trader_ids": sorted(trader_filter),
        "statuses": sorted(status_filter),
        "review_statuses": sorted(review_filter),
        "display_only": display_only,
    }
    payload = {
        "schema_version": TRADE_RECORDS_SCHEMA_VERSION,
        "ticker": selected_ticker,
        "trade_date": day["trade_date"],
        "traders": traders,
        "trade_groups": selected_groups,
        "note_contexts": selected_contexts,
        "counts": {
            "trade_groups_total": len(selected_groups),
            "display_eligible_groups": sum(bool(group["display_eligible"]) for group in selected_groups),
            "reported_stats_eligible_groups": sum(
                bool(group["reported_stats_eligible"]) for group in selected_groups
            ),
            "calculated_stats_eligible_groups": sum(
                bool(group["calculated_stats_eligible"]) for group in selected_groups
            ),
            "note_contexts_total": len(selected_contexts),
        },
        "export_metadata": {
            "selection": selection,
            "json_filename": f"trade_records_{selected_ticker.lower()}_{day['trade_date']}.json",
            "csv_filenames": ["trade_groups.csv", "trade_legs.csv", "trade_events.csv"],
            "includes_bars": False,
            "raw_evidence_included": False,
        },
    }
    assert_no_raw_evidence_fields(payload)
    return payload


def handle_trade_records_read(
    role: str,
    content_dir: Path,
    ticker: str,
    trade_date: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    trader_ids: Sequence[str] | None = None,
    statuses: Sequence[str] | None = None,
    review_statuses: Sequence[str] | None = None,
    eligibility: str | None = None,
) -> list[dict[str, Any]]:
    """Exercise the future read contract without registering a FastAPI route."""

    _require_read_role(role)
    if trade_date is not None and (date_from is not None or date_to is not None):
        _fail("selection", "trade_date cannot be combined with date_from/date_to")
    if eligibility not in {None, "display", "reported", "calculated"}:
        _fail("eligibility", "must be display, reported, calculated, or null")
    start = _require_date(date_from, "date_from") if date_from is not None else None
    end = _require_date(date_to, "date_to") if date_to is not None else None
    exact = _require_date(trade_date, "trade_date") if trade_date is not None else None
    if start is not None and end is not None and start > end:
        _fail("date_range", "date_from must be on or before date_to")

    root = content_dir.expanduser().resolve()
    registry = load_trader_registry(root / "traders" / "index.json")
    days = validate_trade_repository((root / "trades").glob("*.json"), registry)
    selected_days = []
    for day in days:
        current = _require_date(day["trade_date"], "trade_day.trade_date")
        if exact is not None and current != exact:
            continue
        if start is not None and current < start:
            continue
        if end is not None and current > end:
            continue
        selected_days.append(day)
    if exact is not None and not selected_days:
        selected_days = [{
            "schema_version": TRADE_DAY_SCHEMA_VERSION,
            "trade_date": exact.isoformat(),
            "timezone": NEW_YORK_ZONE,
            "trade_groups": [],
            "note_contexts": [],
        }]

    payloads = []
    for day in selected_days:
        payload = build_trade_records_payload(
            registry,
            day,
            ticker,
            trader_ids=trader_ids,
            statuses=statuses,
            review_statuses=review_statuses,
            display_only=eligibility == "display",
        )
        if eligibility in {"reported", "calculated"}:
            field = f"{eligibility}_stats_eligible"
            payload["trade_groups"] = [group for group in payload["trade_groups"] if group[field]]
            _refresh_payload_counts(payload)
        payloads.append(payload)
    return payloads


def handle_trade_day_admin_write(
    role: str,
    content_dir: Path,
    payload: Mapping[str, Any],
    replace: Callable[[str | bytes | os.PathLike[str] | os.PathLike[bytes], str | bytes | os.PathLike[str] | os.PathLike[bytes]], None] = os.replace,
) -> dict[str, Any]:
    """Validate a whole repository candidate before atomically replacing one daily file."""

    _require_admin_role(role)
    root = content_dir.expanduser().resolve()
    registry = load_trader_registry(root / "traders" / "index.json")
    trade_date = _require_date(payload.get("trade_date"), "trade_day.trade_date").isoformat()
    paths = sorted((root / "trades").glob("*.json"))
    repository_ids: set[str] = set()
    for path in paths:
        if path.stem != trade_date:
            load_trade_day(path, registry, repository_ids=repository_ids)
    validated = validate_trade_day(payload, registry, repository_ids=repository_ids)
    target = root / "trades" / f"{trade_date}.json"
    serialized = _canonical_document(validated)
    _atomic_replace_text(target, serialized, replace)
    return {
        "path": str(target),
        "trade_date": trade_date,
        "trade_groups": len(validated["trade_groups"]),
        "note_contexts": len(validated["note_contexts"]),
        "sha256": hashlib.sha256(serialized.encode("utf-8")).hexdigest(),
    }


def handle_trader_registry_admin_write(
    role: str,
    content_dir: Path,
    payload: Mapping[str, Any],
    replace: Callable[[str | bytes | os.PathLike[str] | os.PathLike[bytes], str | bytes | os.PathLike[str] | os.PathLike[bytes]], None] = os.replace,
) -> dict[str, Any]:
    """Validate all canonical days against a candidate registry before replacement."""

    _require_admin_role(role)
    root = content_dir.expanduser().resolve()
    validated = validate_trader_registry(payload)
    validate_trade_repository((root / "trades").glob("*.json"), validated)
    target = root / "traders" / "index.json"
    serialized = _canonical_document(validated)
    _atomic_replace_text(target, serialized, replace)
    return {
        "path": str(target),
        "traders": len(validated["traders"]),
        "sha256": hashlib.sha256(serialized.encode("utf-8")).hexdigest(),
    }


def assert_no_raw_evidence_fields(payload: Any, path: str = "root") -> None:
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            normalized = str(key).strip().lower().replace("-", "_")
            if normalized in FORBIDDEN_EVIDENCE_KEYS:
                _fail(f"{path}.{key}", "raw evidence fields are forbidden")
            assert_no_raw_evidence_fields(value, f"{path}.{key}")
    elif isinstance(payload, list):
        for index, value in enumerate(payload):
            assert_no_raw_evidence_fields(value, f"{path}[{index}]")


def _require_read_role(role: str) -> None:
    if role not in {"readonly", "admin"}:
        raise TradeAuthorizationError("readonly or admin role required")


def _require_admin_role(role: str) -> None:
    if role != "admin":
        raise TradeAuthorizationError("admin role required")


def _refresh_payload_counts(payload: dict[str, Any]) -> None:
    groups = payload["trade_groups"]
    payload["counts"].update({
        "trade_groups_total": len(groups),
        "display_eligible_groups": sum(bool(group["display_eligible"]) for group in groups),
        "reported_stats_eligible_groups": sum(
            bool(group["reported_stats_eligible"]) for group in groups
        ),
        "calculated_stats_eligible_groups": sum(
            bool(group["calculated_stats_eligible"]) for group in groups
        ),
    })


def _canonical_document(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=False, indent=2) + "\n"


def _atomic_replace_text(
    target: Path,
    content: str,
    replace: Callable[[str | bytes | os.PathLike[str] | os.PathLike[bytes], str | bytes | os.PathLike[str] | os.PathLike[bytes]], None],
) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor, raw_temporary = tempfile.mkstemp(
        prefix=f".{target.name}.",
        suffix=".candidate",
        dir=target.parent,
    )
    temporary = Path(raw_temporary)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        replace(temporary, target)
        directory_descriptor = os.open(target.parent, os.O_RDONLY)
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
    finally:
        if temporary.exists():
            temporary.unlink()


def _validate_group(
    group: dict[str, Any],
    path: str,
    trade_date: date,
    timezone: ZoneInfo,
    trader_ids: set[str],
    repository_ids: set[str],
    local_ids: set[str],
) -> None:
    required = GROUP_FIELDS - {"supersedes_trade_group_id"}
    _require_exact_keys(group, GROUP_FIELDS, path, required=required)
    group_id = _require_string(group["trade_group_id"], f"{path}.trade_group_id")
    if not _GROUP_ID_RE.fullmatch(group_id):
        _fail(f"{path}.trade_group_id", "must be a persisted tg_ stable ID")
    _register_id(group_id, f"{path}.trade_group_id", repository_ids, local_ids)
    trader_id = _require_string(group["trader_id"], f"{path}.trader_id")
    if trader_id not in trader_ids:
        _fail(f"{path}.trader_id", f"unknown trader {trader_id}")
    if group["underlying"] not in UNDERLYINGS:
        _fail(f"{path}.underlying", f"must be one of {sorted(UNDERLYINGS)}")
    if _require_date(group["trade_date"], f"{path}.trade_date") != trade_date:
        _fail(f"{path}.trade_date", "must match the daily file date")
    if group["direction"] not in DIRECTIONS:
        _fail(f"{path}.direction", f"must be one of {sorted(DIRECTIONS)}")
    if group["status"] not in RECORD_STATUSES:
        _fail(f"{path}.status", "unsupported record status")
    if group["review_status"] not in REVIEW_STATUSES:
        _fail(f"{path}.review_status", "unsupported review status")
    for field in ("display_eligible", "reported_stats_eligible", "calculated_stats_eligible", "result_conflict"):
        _require_bool(group[field], f"{path}.{field}")
    supersedes = group.get("supersedes_trade_group_id")
    if supersedes is not None:
        _require_string(supersedes, f"{path}.supersedes_trade_group_id")
        if supersedes == group_id:
            _fail(f"{path}.supersedes_trade_group_id", "cannot reference itself")
    if group["status"] != "active" and any(
        group[field]
        for field in ("display_eligible", "reported_stats_eligible", "calculated_stats_eligible")
    ):
        _fail(path, "voided or superseded records cannot remain eligible")

    legs = _require_list(group["legs"], f"{path}.legs")
    if len(legs) != 1:
        _fail(f"{path}.legs", "v1 permits exactly one long-premium option leg")
    _validate_leg(
        _require_mapping(legs[0], f"{path}.legs[0]"),
        f"{path}.legs[0]",
        group,
        trade_date,
        timezone,
        repository_ids,
        local_ids,
    )
    notes = _require_list(group["notes"], f"{path}.notes")
    for note_index, note in enumerate(notes):
        _validate_note(_require_mapping(note, f"{path}.notes[{note_index}]"), f"{path}.notes[{note_index}]")
    _validate_normalization(
        _require_mapping(group["normalization"], f"{path}.normalization"),
        f"{path}.normalization",
    )
    _validate_reported_outcome(group["reported_outcome"], f"{path}.reported_outcome")
    _validate_calculated_outcome(group["calculated_outcome"], f"{path}.calculated_outcome")
    if group["reported_stats_eligible"] and group["reported_outcome"] is None:
        _fail(f"{path}.reported_stats_eligible", "requires a reported outcome")
    if group["calculated_stats_eligible"] and group["calculated_outcome"] is None:
        _fail(f"{path}.calculated_stats_eligible", "requires a calculated outcome")
    if group["calculated_stats_eligible"]:
        from .trade_statistics import TradeCalculationError, calculate_long_premium_outcome

        try:
            calculated = calculate_long_premium_outcome(group)
        except TradeCalculationError as exc:
            raise TradeValidationError(f"{path}.calculated_outcome: {exc}") from exc
        if calculated is None:
            _fail(f"{path}.calculated_stats_eligible", "requires fully closed complete fills")
        if calculated != group["calculated_outcome"]:
            _fail(f"{path}.calculated_outcome", "does not match long-premium-v1 calculation")
    expected_conflict = _outcomes_conflict(group["reported_outcome"], group["calculated_outcome"])
    if group["result_conflict"] != expected_conflict:
        _fail(f"{path}.result_conflict", f"must be {str(expected_conflict).lower()}")


def _validate_leg(
    leg: dict[str, Any],
    path: str,
    group: Mapping[str, Any],
    trade_date: date,
    timezone: ZoneInfo,
    repository_ids: set[str],
    local_ids: set[str],
) -> None:
    _require_exact_keys(leg, LEG_FIELDS, path)
    leg_id = _require_string(leg["leg_id"], f"{path}.leg_id")
    if not _STABLE_ID_RE.fullmatch(leg_id) or not leg_id.startswith(f"{group['trade_group_id']}_l"):
        _fail(f"{path}.leg_id", "must be a persisted child ID of the trade group")
    _register_id(leg_id, f"{path}.leg_id", repository_ids, local_ids)
    if leg["instrument_type"] != "option" or leg["position_side"] != "long":
        _fail(path, "v1 permits only long option legs")
    if leg["option_type"] != group["direction"]:
        _fail(f"{path}.option_type", "must match group direction")
    _require_optional_positive_number(leg["strike"], f"{path}.strike")
    expiry = _require_date(leg["expiry"], f"{path}.expiry")
    if expiry != trade_date:
        _fail(f"{path}.expiry", "v1 permits only same-day 0DTE expiry")
    if leg["expiry_provenance"] not in {"user_provided", "legacy_preserved", "rule_default"}:
        _fail(f"{path}.expiry_provenance", "unsupported provenance")
    _require_positive_number(leg["contract_multiplier"], f"{path}.contract_multiplier")
    if leg["contract_multiplier_provenance"] not in {"user_provided", "rule_default"}:
        _fail(f"{path}.contract_multiplier_provenance", "unsupported provenance")
    events = _require_list(leg["events"], f"{path}.events")
    if not events:
        _fail(f"{path}.events", "must contain at least one event")
    actions: list[str] = []
    timestamps: list[datetime] = []
    for index, event in enumerate(events):
        event_path = f"{path}.events[{index}]"
        parsed_time = _validate_event(
            _require_mapping(event, event_path),
            event_path,
            leg_id,
            trade_date,
            timezone,
            repository_ids,
            local_ids,
        )
        if event["sequence"] != index + 1:
            _fail(f"{event_path}.sequence", "must be contiguous and match event order")
        actions.append(event["action"])
        if parsed_time is not None:
            timestamps.append(parsed_time)
    if actions[0] != "buy_open":
        _fail(f"{path}.events[0].action", "the first event must be buy_open")
    if any(action == "buy_open" for action in actions[1:]):
        _fail(f"{path}.events", "buy_open may appear only once")
    if timestamps != sorted(timestamps):
        _fail(f"{path}.events", "known event timestamps must be chronological")


def _validate_event(
    event: dict[str, Any],
    path: str,
    leg_id: str,
    trade_date: date,
    timezone: ZoneInfo,
    repository_ids: set[str],
    local_ids: set[str],
) -> datetime | None:
    _require_exact_keys(event, EVENT_FIELDS, path)
    event_id = _require_string(event["event_id"], f"{path}.event_id")
    if not _STABLE_ID_RE.fullmatch(event_id) or not event_id.startswith(f"{leg_id}_e"):
        _fail(f"{path}.event_id", "must be a persisted child ID of the leg")
    _register_id(event_id, f"{path}.event_id", repository_ids, local_ids)
    _require_positive_int(event["sequence"], f"{path}.sequence")
    if event["action"] not in EVENT_ACTIONS:
        _fail(f"{path}.action", "unsupported event action")
    time_incomplete = _require_bool(event["time_incomplete"], f"{path}.time_incomplete")
    occurred_at = event["occurred_at"]
    precision = event["time_precision"]
    parsed_time: datetime | None = None
    if occurred_at is None:
        if not time_incomplete or precision is not None:
            _fail(path, "missing occurred_at requires time_incomplete=true and time_precision=null")
    else:
        if time_incomplete:
            _fail(f"{path}.time_incomplete", "must be false when occurred_at is present")
        if precision not in TIME_PRECISIONS:
            _fail(f"{path}.time_precision", "must describe the known timestamp")
        occurred_text = _require_string(occurred_at, f"{path}.occurred_at")
        if not _EXPLICIT_OFFSET_RE.search(occurred_text):
            _fail(f"{path}.occurred_at", "must include an explicit UTC offset")
        try:
            parsed_time = datetime.fromisoformat(occurred_text.replace("Z", "+00:00"))
        except ValueError as exc:
            raise TradeValidationError(f"{path}.occurred_at: invalid ISO-8601 timestamp") from exc
        if parsed_time.tzinfo is None:
            _fail(f"{path}.occurred_at", "must be timezone-aware")
        local = parsed_time.astimezone(timezone)
        if local.date() != trade_date:
            _fail(f"{path}.occurred_at", "must resolve to the daily New York trade date")
        expected_offset = local.replace(tzinfo=None).replace(tzinfo=timezone, fold=local.fold).utcoffset()
        if parsed_time.utcoffset() != expected_offset:
            _fail(f"{path}.occurred_at", "offset does not match America/New_York rules")
    _require_optional_nonnegative_number(event["premium"], f"{path}.premium")
    _require_optional_positive_number(event["quantity"], f"{path}.quantity")
    _require_optional_nonnegative_number(event["fees"], f"{path}.fees")
    if event["note"] is not None:
        _require_nonempty_string(event["note"], f"{path}.note")
    provenance = _require_mapping(event["fact_provenance"], f"{path}.fact_provenance")
    for key, value in provenance.items():
        _require_nonempty_string(key, f"{path}.fact_provenance key")
        if value not in FACT_PROVENANCE:
            _fail(f"{path}.fact_provenance.{key}", "unsupported provenance")
    return parsed_time


def _validate_note(note: dict[str, Any], path: str) -> None:
    _require_exact_keys(note, NOTE_FIELDS, path)
    _require_nonempty_string(note["text"], f"{path}.text")
    if note["provenance"] not in {"user_provided", "legacy_preserved", "normalized_summary"}:
        _fail(f"{path}.provenance", "unsupported note provenance")


def _validate_normalization(normalization: dict[str, Any], path: str) -> None:
    required = {"method", "source", "review_flags"}
    _require_exact_keys(normalization, NORMALIZATION_FIELDS, path, required=required)
    if normalization["method"] not in {
        "manual_normalization",
        "legacy_preserve",
        "legacy_rule_extract",
    }:
        _fail(f"{path}.method", "unsupported normalization method")
    _require_nonempty_string(normalization["source"], f"{path}.source")
    if normalization.get("source_path") is not None:
        _require_nonempty_string(normalization["source_path"], f"{path}.source_path")
    if normalization.get("source_index") is not None:
        _require_nonnegative_int(normalization["source_index"], f"{path}.source_index")
    flags = _require_list(normalization["review_flags"], f"{path}.review_flags")
    if len(flags) != len(set(flags)):
        _fail(f"{path}.review_flags", "must not contain duplicates")
    for index, flag in enumerate(flags):
        _require_nonempty_string(flag, f"{path}.review_flags[{index}]")


def _validate_context(
    context: dict[str, Any],
    path: str,
    trade_date: date,
    trader_ids: set[str],
    repository_ids: set[str],
    local_ids: set[str],
) -> None:
    _require_exact_keys(context, CONTEXT_FIELDS, path)
    context_id = _require_string(context["context_id"], f"{path}.context_id")
    if not _CONTEXT_ID_RE.fullmatch(context_id):
        _fail(f"{path}.context_id", "must be a persisted ctx_ stable ID")
    _register_id(context_id, f"{path}.context_id", repository_ids, local_ids)
    if context["trader_id"] not in trader_ids:
        _fail(f"{path}.trader_id", "references an unknown trader")
    if context["underlying"] not in UNDERLYINGS:
        _fail(f"{path}.underlying", "unsupported underlying")
    if _require_date(context["trade_date"], f"{path}.trade_date") != trade_date:
        _fail(f"{path}.trade_date", "must match the daily file date")
    _require_nonempty_string(context["text"], f"{path}.text")
    if context["status"] not in RECORD_STATUSES:
        _fail(f"{path}.status", "unsupported record status")
    if context["review_status"] not in REVIEW_STATUSES:
        _fail(f"{path}.review_status", "unsupported review status")
    _validate_normalization(
        _require_mapping(context["normalization"], f"{path}.normalization"),
        f"{path}.normalization",
    )


def _validate_reported_outcome(outcome: Any, path: str) -> None:
    if outcome is None:
        return
    item = _require_mapping(outcome, path)
    _require_exact_keys(item, REPORTED_OUTCOME_FIELDS, path)
    for field in ("return_pct", "gross_pnl", "net_pnl"):
        _require_optional_number(item[field], f"{path}.{field}")
    if item["return_pct"] is None and item["gross_pnl"] is None and item["net_pnl"] is None:
        _fail(path, "must contain at least one explicitly reported result")
    _require_nonempty_string(item["provenance"], f"{path}.provenance")
    if item["note"] is not None:
        _require_nonempty_string(item["note"], f"{path}.note")


def _validate_calculated_outcome(outcome: Any, path: str) -> None:
    if outcome is None:
        return
    item = _require_mapping(outcome, path)
    _require_exact_keys(item, CALCULATED_OUTCOME_FIELDS, path)
    for field in ("return_pct", "gross_pnl"):
        _require_number(item[field], f"{path}.{field}")
    _require_optional_number(item["net_pnl"], f"{path}.net_pnl")
    for field in ("closed_quantity", "average_entry_premium", "average_exit_premium"):
        _require_nonnegative_number(item[field], f"{path}.{field}")
    if item["closed_quantity"] <= 0:
        _fail(f"{path}.closed_quantity", "must be positive")
    if item["calculation_version"] != "long-premium-v1":
        _fail(f"{path}.calculation_version", "unsupported calculation version")


def _outcomes_conflict(reported: Any, calculated: Any) -> bool:
    if not isinstance(reported, Mapping) or not isinstance(calculated, Mapping):
        return False
    reported_return = reported.get("return_pct")
    calculated_return = calculated.get("return_pct")
    if reported_return is None or calculated_return is None:
        return False
    return round(float(reported_return), 2) != round(float(calculated_return), 2)


def _public_group(group: Mapping[str, Any]) -> dict[str, Any]:
    result = {field: copy.deepcopy(group.get(field)) for field in PUBLIC_GROUP_FIELDS}
    result["normalization_method"] = group["normalization"]["method"]
    return result


def _public_context(context: Mapping[str, Any]) -> dict[str, Any]:
    result = {field: copy.deepcopy(context[field]) for field in PUBLIC_CONTEXT_FIELDS}
    result["normalization_method"] = context["normalization"]["method"]
    return result


def _group_sort_key(group: Mapping[str, Any]) -> tuple[str, str, str]:
    first_event = group["legs"][0]["events"][0]
    return (first_event["occurred_at"] or "9999", group["trader_id"], group["trade_group_id"])


def _register_id(value: str, path: str, repository_ids: set[str], local_ids: set[str]) -> None:
    if value in repository_ids or value in local_ids:
        _fail(path, f"duplicate stable ID {value}")
    local_ids.add(value)


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise TradeValidationError(f"{path}: unable to load canonical JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise TradeValidationError(f"{path}: top-level JSON value must be an object")
    return payload


def _require_exact_keys(
    item: Mapping[str, Any],
    allowed: set[str],
    path: str,
    required: set[str] | None = None,
) -> None:
    keys = set(item)
    required_keys = allowed if required is None else required
    missing = sorted(required_keys - keys)
    extra = sorted(keys - allowed)
    if missing:
        _fail(path, f"missing fields: {', '.join(missing)}")
    if extra:
        _fail(path, f"unsupported fields: {', '.join(extra)}")


def _require_mapping(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        _fail(path, "must be an object")
    return value


def _require_list(value: Any, path: str) -> list[Any]:
    if not isinstance(value, list):
        _fail(path, "must be an array")
    return value


def _require_string(value: Any, path: str) -> str:
    if not isinstance(value, str):
        _fail(path, "must be a string")
    return value


def _require_nonempty_string(value: Any, path: str) -> str:
    text = _require_string(value, path)
    if not text.strip():
        _fail(path, "must not be empty")
    return text


def _require_bool(value: Any, path: str) -> bool:
    if not isinstance(value, bool):
        _fail(path, "must be a boolean")
    return value


def _require_date(value: Any, path: str) -> date:
    text = _require_string(value, path)
    try:
        return date.fromisoformat(text)
    except ValueError as exc:
        raise TradeValidationError(f"{path}: must be an ISO date") from exc


def _require_number(value: Any, path: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        _fail(path, "must be a number")
    return float(value)


def _require_optional_number(value: Any, path: str) -> float | None:
    return None if value is None else _require_number(value, path)


def _require_nonnegative_number(value: Any, path: str) -> float:
    number = _require_number(value, path)
    if number < 0:
        _fail(path, "must be non-negative")
    return number


def _require_optional_nonnegative_number(value: Any, path: str) -> float | None:
    return None if value is None else _require_nonnegative_number(value, path)


def _require_positive_number(value: Any, path: str) -> float:
    number = _require_number(value, path)
    if number <= 0:
        _fail(path, "must be positive")
    return number


def _require_optional_positive_number(value: Any, path: str) -> float | None:
    return None if value is None else _require_positive_number(value, path)


def _require_nonnegative_int(value: Any, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        _fail(path, "must be a non-negative integer")
    return value


def _require_positive_int(value: Any, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        _fail(path, "must be a positive integer")
    return value


def _fail(path: str, message: str) -> None:
    raise TradeValidationError(f"{path}: {message}")
