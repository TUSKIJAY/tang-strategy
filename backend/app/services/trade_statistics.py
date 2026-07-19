from __future__ import annotations

from typing import Any, Iterable, Mapping


CALCULATION_VERSION = "long-premium-v1"


class TradeCalculationError(ValueError):
    """Raised when complete-looking fills violate long-premium accounting."""


def calculate_long_premium_outcome(group: Mapping[str, Any]) -> dict[str, Any] | None:
    """Calculate a fully closed v1 group, or return None when facts are incomplete."""

    legs = group.get("legs")
    if not isinstance(legs, list) or len(legs) != 1:
        raise TradeCalculationError("v1 calculation requires exactly one leg")
    leg = legs[0]
    if leg.get("instrument_type") != "option" or leg.get("position_side") != "long":
        raise TradeCalculationError("v1 calculation supports only long option premium")
    multiplier = _positive_number(leg.get("contract_multiplier"), "contract_multiplier")
    events = leg.get("events")
    if not isinstance(events, list) or not events:
        raise TradeCalculationError("at least one event is required")

    open_quantity = 0.0
    open_cost_premium = 0.0
    total_entry_quantity = 0.0
    total_entry_premium = 0.0
    total_exit_quantity = 0.0
    total_exit_premium = 0.0
    realized_gross = 0.0
    total_fees = 0.0
    all_fees_known = True

    for index, event in enumerate(sorted(events, key=lambda item: item.get("sequence", 0))):
        action = event.get("action")
        quantity_value = event.get("quantity")
        premium_value = event.get("premium")
        if quantity_value is None or premium_value is None:
            return None
        quantity = _positive_number(quantity_value, f"events[{index}].quantity")
        premium = _nonnegative_number(premium_value, f"events[{index}].premium")
        fees = event.get("fees")
        if fees is None:
            all_fees_known = False
        else:
            total_fees += _nonnegative_number(fees, f"events[{index}].fees")

        if action in {"buy_open", "buy_add"}:
            if action == "buy_open" and total_entry_quantity > 0:
                raise TradeCalculationError("buy_open may appear only once")
            if action == "buy_add" and open_quantity <= 0:
                raise TradeCalculationError("buy_add requires an open position")
            open_cost_premium += quantity * premium
            open_quantity += quantity
            total_entry_quantity += quantity
            total_entry_premium += quantity * premium
            continue

        if action not in {"sell_partial", "sell_close"}:
            raise TradeCalculationError(f"unsupported event action: {action}")
        if open_quantity <= 0 or quantity > open_quantity + 1e-12:
            raise TradeCalculationError("sell quantity exceeds the open long position")
        average_open_premium = open_cost_premium / open_quantity
        realized_gross += quantity * (premium - average_open_premium) * multiplier
        open_quantity -= quantity
        open_cost_premium -= quantity * average_open_premium
        total_exit_quantity += quantity
        total_exit_premium += quantity * premium
        if action == "sell_close" and open_quantity > 1e-12:
            raise TradeCalculationError("sell_close must close the remaining position")
        if action == "sell_partial" and open_quantity <= 1e-12:
            raise TradeCalculationError("the final closing event must use sell_close")

    if open_quantity > 1e-12 or total_exit_quantity <= 0:
        return None
    if abs(total_entry_quantity - total_exit_quantity) > 1e-12:
        raise TradeCalculationError("closed quantity does not reconcile to entry quantity")
    if total_entry_premium <= 0:
        raise TradeCalculationError("entry premium basis must be positive")

    entry_basis = total_entry_premium * multiplier
    return {
        "return_pct": round(realized_gross / entry_basis * 100, 10),
        "gross_pnl": round(realized_gross, 10),
        "net_pnl": round(realized_gross - total_fees, 10) if all_fees_known else None,
        "closed_quantity": total_exit_quantity,
        "average_entry_premium": total_entry_premium / total_entry_quantity,
        "average_exit_premium": total_exit_premium / total_exit_quantity,
        "calculation_version": CALCULATION_VERSION,
    }


def outcome_conflict(
    reported_outcome: Mapping[str, Any] | None,
    calculated_outcome: Mapping[str, Any] | None,
) -> bool:
    if not reported_outcome or not calculated_outcome:
        return False
    reported_return = reported_outcome.get("return_pct")
    calculated_return = calculated_outcome.get("return_pct")
    if reported_return is None or calculated_return is None:
        return False
    return round(float(reported_return), 2) != round(float(calculated_return), 2)


def summarize_trade_groups(groups: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    selected = list(groups)
    reported_returns = [
        float(group["reported_outcome"]["return_pct"])
        for group in selected
        if group.get("reported_stats_eligible")
        and isinstance(group.get("reported_outcome"), Mapping)
        and group["reported_outcome"].get("return_pct") is not None
    ]
    calculated_returns = [
        float(group["calculated_outcome"]["return_pct"])
        for group in selected
        if group.get("calculated_stats_eligible")
        and isinstance(group.get("calculated_outcome"), Mapping)
        and group["calculated_outcome"].get("return_pct") is not None
    ]
    return {
        "group_count": len(selected),
        "reported": _return_summary(reported_returns),
        "calculated": _return_summary(calculated_returns),
        "conflict_count": sum(bool(group.get("result_conflict")) for group in selected),
    }


def _return_summary(values: list[float]) -> dict[str, Any]:
    return {
        "eligible_count": len(values),
        "win_count": sum(value > 0 for value in values),
        "loss_count": sum(value < 0 for value in values),
        "flat_count": sum(value == 0 for value in values),
        "average_return_pct": sum(values) / len(values) if values else None,
    }


def _positive_number(value: Any, field: str) -> float:
    number = _number(value, field)
    if number <= 0:
        raise TradeCalculationError(f"{field} must be positive")
    return number


def _nonnegative_number(value: Any, field: str) -> float:
    number = _number(value, field)
    if number < 0:
        raise TradeCalculationError(f"{field} must be non-negative")
    return number


def _number(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TradeCalculationError(f"{field} must be numeric")
    return float(value)
