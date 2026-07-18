# Teaching System

The Teaching page explains Tang Strategy behavior using the same DB payload and kline engine used by Review and Backtest.

## Runtime Entry

- Navigation entry: `Teaching` in the interactive React app (the app uses internal view state rather than a `/teaching` browser route).
- Data source: backend assembled review payload.
- Content source: `content/teaching/checkpoints.json`, `content/cases/index.json`, and `content/rules/compiled/index.json`.
- Strategy source: `strategies/json/*.json`.

## Core Execution Model

- SPY is the primary teaching example; other tickers should use the same data contract.
- 5m provides trend context.
- 1m provides trigger and confirmation detail.
- Heikin-Ashi candles are the main interpretation layer.
- MA and VWAP lines are context filters, not automatic trade permissions.

## Key Indicator Semantics

- `MA10`: primary trigger anchor.
- `MA20` and `MA30`: short-term alignment context.
- `MA50` and `MA200`: structural support/resistance context only after market validation.
- `VWAP`: liquidity and value reference, especially near reversal or barrier zones.

## Validated Level Rule

Do not describe MA50, MA200, or VWAP as mechanically valid support/resistance. A level is useful only when recent price action has tested it and produced a clear reaction.

Useful evidence:

- repeated touch and rejection/support
- close/sequence behavior around the level
- successful or failed retest after a break
- role swap from support to resistance, or resistance to support

## Pattern Digest

Use these groups when labeling teaching cases:

- Trend continuation and MA10 support/reject.
- Cross-level break through MA50, MA200, or VWAP.
- Weakening structure: shrinking bodies, long tails, failed continuation.
- Abrupt reversal after compression or extended trend.

## Case Review Checklist

- Classify the case as standard, edge, or anti before writing lesson copy.
- Confirm 5m trend context.
- Confirm the 1m trigger bar and confirmation bar.
- Verify whether referenced key levels were actually validated by prior price action.
- Check if target space is blocked by dense MA/VWAP structure.
- Keep lesson wording measurable: touch, close cross, retest, reaction strength, continuation, invalidation.

## Implementation Rule

Update content and checkpoint wording first. Change strategy JSON or backend-derived schema only after the teaching copy exposes a clear reusable rule.
