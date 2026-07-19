from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Iterable, Mapping

from app.services.trade_records import (
    NEW_YORK_ZONE,
    TRADE_DAY_SCHEMA_VERSION,
    occurred_at_from_local_time,
    validate_trade_day,
    validate_trader_registry,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE_DIR = REPOSITORY_ROOT / "content" / "trader-trades"
DEFAULT_OUTPUT_DIR = REPOSITORY_ROOT / "content"
TANG_REGISTRY = {
    "schema_version": "traders-v1",
    "traders": [
        {
            "trader_id": "tang",
            "display_name": "Tang",
            "color": "#E45756",
            "active": True,
            "sort_order": 10,
        }
    ],
}

_SIGNED_PERCENT_RE = re.compile(r"(?P<pct>[+-]\d+(?:\.\d+)?)%")
_POSITION_PERCENT_RE = re.compile(r"(?P<pct>\d+(?:\.\d+)?)%\s*仓位")
_AMBIGUOUS_END_RE = re.compile(r"(?<![+\-])(?P<pct>\d+(?:\.\d+)?)%\s*结束")
_APPROXIMATE_TIME_RE = re.compile(r"(?P<time>\d{1,2}:\d{2})\s*附近")
_RESULT_VERB_RE = re.compile(r"反馈|止盈|止损|出清|出场")


def classify_legacy_note(note: str) -> dict[str, Any]:
    position_matches = [float(match.group("pct")) for match in _POSITION_PERCENT_RE.finditer(note)]
    ambiguous_match = _AMBIGUOUS_END_RE.search(note)
    reported_return_pct: float | None = None
    matched_rule: str | None = None
    exit_time: str | None = None
    exit_time_precision: str | None = None

    for match in _SIGNED_PERCENT_RE.finditer(note):
        window_start = max(0, match.start() - 40)
        window_end = min(len(note), match.end() + 16)
        context = note[window_start:window_end]
        if not _RESULT_VERB_RE.search(context):
            continue
        reported_return_pct = float(match.group("pct"))
        matched_rule = "allow_explicit_signed_result_with_result_verb"
        prefix = note[: match.start()]
        approximate_times = list(_APPROXIMATE_TIME_RE.finditer(prefix))
        if approximate_times:
            exit_time = _normalize_time(approximate_times[-1].group("time"))
            exit_time_precision = "approximate"
        break

    review_flags: list[str] = []
    non_extraction_reason: str | None = None
    if reported_return_pct is None:
        if ambiguous_match:
            review_flags.append("ambiguous_exit_percentage")
            non_extraction_reason = "review_ambiguous_unsigned_percentage_with_end_word"
        elif position_matches:
            non_extraction_reason = "deny_position_size_percentage"
        else:
            non_extraction_reason = "no_allowlisted_reported_result"

    return {
        "reported_return_pct": reported_return_pct,
        "exit_time": exit_time,
        "exit_time_precision": exit_time_precision,
        "matched_rule": matched_rule,
        "non_extraction_reason": non_extraction_reason,
        "position_size_percentages": position_matches,
        "review_flags": review_flags,
        "review_required": bool(review_flags),
    }


def legacy_trade_to_group(
    source_path: Path,
    trade_date: str,
    ticker: str,
    source_index: int,
    trade: Mapping[str, Any],
    trader_id: str = "tang",
) -> tuple[dict[str, Any], dict[str, Any]]:
    source_name = _repository_path(source_path)
    sequence = source_index + 1
    group_id = f"tg_{trade_date.replace('-', '')}_{trader_id}_{ticker.lower()}_{sequence:03d}"
    leg_id = f"{group_id}_l1"
    entry_event_id = f"{leg_id}_e1"
    classification = classify_legacy_note(str(trade.get("note") or ""))
    entry_time = _normalize_time(str(trade["time"]))
    entry_timestamp = occurred_at_from_local_time(trade_date, entry_time, "minute")

    events: list[dict[str, Any]] = [
        {
            "event_id": entry_event_id,
            "sequence": 1,
            "action": str(trade.get("action") or "buy_open"),
            "occurred_at": entry_timestamp,
            "time_precision": "minute",
            "time_incomplete": False,
            "premium": None,
            "quantity": None,
            "fees": None,
            "note": None,
            "fact_provenance": {
                "occurred_at": "legacy_preserved",
                "premium": "unknown",
                "quantity": "unknown",
                "fees": "unknown",
            },
        }
    ]
    if classification["exit_time"] is not None:
        events.append(
            {
                "event_id": f"{leg_id}_e2",
                "sequence": 2,
                "action": "sell_close",
                "occurred_at": occurred_at_from_local_time(
                    trade_date,
                    classification["exit_time"],
                    classification["exit_time_precision"],
                ),
                "time_precision": classification["exit_time_precision"],
                "time_incomplete": False,
                "premium": None,
                "quantity": None,
                "fees": None,
                "note": "Exit time extracted conservatively from the preserved legacy note.",
                "fact_provenance": {
                    "occurred_at": "legacy_rule_extract",
                    "premium": "unknown",
                    "quantity": "unknown",
                    "fees": "unknown",
                },
            }
        )

    reported_return = classification["reported_return_pct"]
    reported_outcome = (
        {
            "return_pct": reported_return,
            "gross_pnl": None,
            "net_pnl": None,
            "provenance": "legacy_rule_extract",
            "note": "Reported percentage extracted from the preserved legacy note; no fill was inferred.",
        }
        if reported_return is not None
        else None
    )
    expiry = trade.get("expiry") or trade_date
    expiry_provenance = "legacy_preserved" if trade.get("expiry") else "rule_default"
    method = (
        "legacy_rule_extract"
        if reported_return is not None or classification["exit_time"] is not None
        else "legacy_preserve"
    )
    group = {
        "trade_group_id": group_id,
        "trader_id": trader_id,
        "underlying": ticker,
        "trade_date": trade_date,
        "direction": str(trade["side"]).upper(),
        "status": "active",
        "review_status": "pending" if classification["review_required"] else "verified",
        "display_eligible": True,
        "reported_stats_eligible": reported_outcome is not None,
        "calculated_stats_eligible": False,
        "supersedes_trade_group_id": None,
        "legs": [
            {
                "leg_id": leg_id,
                "instrument_type": "option",
                "position_side": "long",
                "option_type": str(trade["side"]).upper(),
                "strike": trade.get("strike"),
                "expiry": expiry,
                "expiry_provenance": expiry_provenance,
                "contract_multiplier": 100,
                "contract_multiplier_provenance": "rule_default",
                "events": events,
            }
        ],
        "reported_outcome": reported_outcome,
        "calculated_outcome": None,
        "result_conflict": False,
        "notes": [
            {
                "text": str(trade.get("note") or ""),
                "provenance": "legacy_preserved",
            }
        ],
        "normalization": {
            "method": method,
            "source": str(trade.get("source") or "legacy_record"),
            "source_path": source_name,
            "source_index": source_index,
            "review_flags": classification["review_flags"],
        },
    }
    report_row = {
        "kind": "trade",
        "source_path": source_name,
        "source_index": source_index,
        "trade_group_id": group_id,
        "source_time": trade.get("time"),
        "source_side": trade.get("side"),
        "source_strike": trade.get("strike"),
        "source_expiry": trade.get("expiry"),
        "source_action": trade.get("action"),
        "source_reason_type": trade.get("reason_type"),
        "source_note": trade.get("note"),
        **classification,
    }
    return group, report_row


def legacy_day_to_canonical(
    source_path: Path,
    payload: Mapping[str, Any],
    trader_id: str = "tang",
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    source_name = _repository_path(source_path)
    trade_date = str(payload["date"])
    ticker = str(payload["ticker"]).upper()
    groups: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []
    for source_index, trade in enumerate(payload.get("trades") or []):
        group, row = legacy_trade_to_group(
            source_path,
            trade_date,
            ticker,
            source_index,
            trade,
            trader_id=trader_id,
        )
        groups.append(group)
        rows.append(row)

    contexts = []
    for source_index, note in enumerate(payload.get("notes") or []):
        context_id = f"ctx_{trade_date.replace('-', '')}_{trader_id}_{ticker.lower()}_{source_index + 1:03d}"
        contexts.append(
            {
                "context_id": context_id,
                "trader_id": trader_id,
                "underlying": ticker,
                "trade_date": trade_date,
                "text": str(note),
                "status": "active",
                "review_status": "verified",
                "normalization": {
                    "method": "legacy_preserve",
                    "source": "legacy_day_note",
                    "source_path": source_name,
                    "source_index": source_index,
                    "review_flags": [],
                },
            }
        )
        rows.append(
            {
                "kind": "day_context",
                "source_path": source_name,
                "source_index": source_index,
                "context_id": context_id,
                "source_note": note,
                "matched_rule": "preserve_day_context",
                "non_extraction_reason": "not_a_trade_result",
                "review_required": False,
            }
        )
    return (
        {
            "schema_version": TRADE_DAY_SCHEMA_VERSION,
            "trade_date": trade_date,
            "timezone": NEW_YORK_ZONE,
            "trade_groups": groups,
            "note_contexts": contexts,
        },
        rows,
    )


def classify_legacy_corpus(
    source_paths: Iterable[Path],
    trader_id: str = "tang",
) -> dict[str, Any]:
    days: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []
    source_targets: list[dict[str, str]] = []
    for source_path in sorted(source_paths):
        payload = json.loads(source_path.read_text(encoding="utf-8"))
        day, day_rows = legacy_day_to_canonical(source_path, payload, trader_id=trader_id)
        days.append(day)
        rows.extend(day_rows)
        source_targets.append(
            {
                "source_path": _repository_path(source_path),
                "target_path": f"content/trades/{day['trade_date']}.json",
            }
        )
    trade_rows = [row for row in rows if row["kind"] == "trade"]
    context_rows = [row for row in rows if row["kind"] == "day_context"]
    return {
        "source_files": len(days),
        "trade_rows": len(trade_rows),
        "day_context_rows": len(context_rows),
        "reported_return_rows": sum(row["reported_return_pct"] is not None for row in trade_rows),
        "review_required_rows": sum(bool(row["review_required"]) for row in trade_rows),
        "source_targets": source_targets,
        "rows": rows,
        "days": days,
    }


def render_canonical_documents(
    result: Mapping[str, Any],
    registry: Mapping[str, Any] = TANG_REGISTRY,
) -> dict[str, str]:
    """Return the complete deterministic migration output without writing by default."""

    registry_data = validate_trader_registry(registry)
    days = result.get("days")
    if not isinstance(days, list):
        raise ValueError("classification result must include a days list")
    repository_ids: set[str] = set()
    validated_days = [
        validate_trade_day(day, registry_data, repository_ids=repository_ids)
        for day in days
    ]
    documents = {
        "traders/index.json": _canonical_document(registry_data),
    }
    for day in validated_days:
        documents[f"trades/{day['trade_date']}.json"] = _canonical_document(day)
    return documents


def _normalize_time(value: str) -> str:
    parts = value.strip().split(":")
    if len(parts) != 2:
        raise ValueError(f"invalid legacy time: {value}")
    hour, minute = (int(part) for part in parts)
    if not 0 <= hour <= 23 or not 0 <= minute <= 59:
        raise ValueError(f"invalid legacy time: {value}")
    return f"{hour:02d}:{minute:02d}"


def _repository_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPOSITORY_ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


def _canonical_document(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=False, indent=2) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Classify legacy Tang records without writing canonical content by default."
    )
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--write-canonical",
        action="store_true",
        help="Explicitly write the validated registry and daily canonical documents.",
    )
    args = parser.parse_args()
    result = classify_legacy_corpus(args.source_dir.glob("*.json"))
    documents = render_canonical_documents(result)
    if args.write_canonical:
        for relative_path, content in documents.items():
            target = args.output_dir / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
    summary = {key: value for key, value in result.items() if key not in {"days", "rows"}}
    summary["canonical_documents"] = len(documents)
    summary["wrote_canonical"] = bool(args.write_canonical)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
