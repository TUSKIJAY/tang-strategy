# Training Replay Drill Redesign Plan

> Date: 2026-04-25
> Status: next implementation plan
> Scope: redesign `#training/<module_id>` only. Do not change hub, module, case, mistake, or archive pages in this pass.

## 1. Direction

The training page should stop behaving like a step-by-step rule quiz. Its next shape is a hidden-future intraday replay drill:

```text
watch bars unfold -> decide what to do -> see the market play out -> review timing, direction, and reasons
```

Primary training goal:

- Train real-time trading decisions, not rule recall.
- Keep the user inside market uncertainty before feedback appears.
- Let the user act at any bar, then grade the action by timing window and reasoning.

This replaces the earlier 7-step question flow as the main product direction. The old step/checkpoint model remains useful as a data source for explanations and reason chips, but it should no longer be the visible interaction model.

Wrong-direction signal: if implementation starts by adding more quiz steps or more explanatory panels before the user commits a trade action, it is drifting back to the rejected model.

## 2. Product Model

### 2.1 Page Structure

Use a two-column training surface:

```text
Left:  Kline replay drill
Right: action rail
```

Left column:

- `KlineView mode="lab"` remains the chart surface.
- The chart starts with future bars hidden.
- Users can switch 1m/5m and MA visibility through the existing broker-style engine toolbar.
- Replay progression during the decision phase is controlled by the right rail, not by the engine toolbar playback buttons. During `phase === 'replay'`, engine playback and step buttons must be disabled or hidden; timeframe and MA buttons remain available.
- Do not restore `Aggregate5mBand`; the 5m strip attempt was rejected as visually noisy.

Right rail:

- Current drill state: case title, module, current bar time/index, hidden/revealed status.
- Action buttons: `等待`, `做多`, `做空`, `放弃`.
- Reason chips derived from segment checkpoints.
- Decision log: waits and final submitted action.
- Review panel after submission.

### 2.2 Drill Flow

Initial state:

- Select a case for the module.
- Compute `signalIndex = segment.derived.signal_bar_index ?? case.decision_bar.bar_index`.
- Compute `drillStartIndex = clamp(signalIndex - 12, 0, last1mIndex)`.
- Use `MIN_DRILL_DISTANCE = 8` as the minimum useful distance from the signal. Use `segment.preheat_count` only as historical context metadata; do not use it as the drill start if it places the user within fewer than `MIN_DRILL_DISTANCE` bars of the signal.
- If no signal index exists, use `clamp((segment.preheat_count ?? 12) - 6, 0, last1mIndex)` and mark the drill as replay-only until an evaluable case is selected.
- Initialize `currentIndex = drillStartIndex` and `revealCutoffIndex = drillStartIndex`.
- Set `revealCutoff` to the current 1m bar index so future bars are hidden.

During replay:

- `等待` is the authoritative one-bar advance. It calls engine step/scroll control, increments `currentIndex`, sets `revealCutoffIndex = currentIndex`, and records the bar in `waitLog`.
- There is no separate `下一根` button in the first version; advancing without committing is always a wait decision.
- Do not let engine toolbar playback advance hidden future bars during replay. If playback remains visible, it must be disabled while `phase === 'replay'`.
- `做多`, `做空`, or `放弃` submits the drill decision.
- Reason chips are multi-select. They may be selected before submitting; they are not required to continue replay.

After submission:

- Lock the submitted action, submitted index, and selected reason keys.
- If the user submits while viewing 5m, capture the current 5m bar's start timestamp, switch back to 1m, locate the first 1m bar at or after that timestamp, and use that 1m index as `submittedIndex` for review.
- Force the chart back to 1m before outcome playback.
- Compute `reviewRevealTarget = min(submittedIndex + 12, last1mIndex)`.
- Set `revealCutoffIndex = reviewRevealTarget`, keep `currentIndex = submittedIndex`, then play at 1x until `currentIndex === reviewRevealTarget`.
- The user may pause outcome playback. If playback is paused, the review panel may still be opened manually.
- Then show review: timing, direction, reasons, missed rules, standard window, and next action.
- Offer `继续播放到结尾`, `重做本案例`, and `换一个案例`.

## 3. Evaluation Model

The drill allows free action at any bar, but evaluation is window-based. Do not require every bar to have a hand-authored answer.

### 3.1 Standard Inputs

Use existing static data:

- Standard index: `segment.derived.signal_bar_index`, falling back to `case.decision_bar.bar_index`.
- Confirm index: checkpoint `confirm_bar.bar_index` when present; otherwise use `signalIndex`. This fallback is intentionally strict: it creates a short valid window around the signal. If a future strategy requires waiting through a longer confirmation sequence, extend the plan with a strategy-specific `confirmWindowBars` value.
- Direction and expected action: case manifest fields first, rule/category fallback second.
- Checkpoints: `segment.derived.checkpoints`.
- Stop/space evidence: checkpoint metrics such as `stop_price` and `barrier_distance_pct`.

### 3.2 Timing Labels

For submitted action at `submittedIndex`:

- `too_early`: before `signal_bar_index`.
- `valid_window`: from `signalIndex` through `validWindowEnd`.
- `validWindowEnd = min((confirmIndex ?? signalIndex) + 1, last1mIndex)`.
- `late`: after `validWindowEnd`.

Timing is evaluated only for standard/edge tradeable cases. For anti/no-trade cases, the primary result is expected action `放弃`; timing becomes secondary explanatory text, not a separate grade.

### 3.3 Direction Labels

Resolve expected action in this order:

1. If `case.grade === 'anti'`, expected action is `放弃`.
2. If `case.answer` contains `不做`, `降级观察`, or equivalent pass wording, expected action is `放弃`.
3. If `case.direction === 'CALL'`, expected action is `做多`.
4. If `case.direction === 'PUT'`, expected action is `做空`.
5. Fallback only when case fields are missing:
   - `support_ma10` expects `做多`.
   - `reject_ma10` expects `做空`.
   - `signal_b` expects `做空`.
   - failed forbidden/filter evidence expects `放弃`.

If no expected action can be resolved, the case is replay-only and should not enter scored drill acceptance.

### 3.4 Reason Review

Reason chips are a filtered, grouped view of checkpoint keys. Do not expose every raw checkpoint blindly.

Visible groups:

- Background: `trend_ok`, `ma_alignment_ok`.
- Trigger: `touch_ma10`, `confirm_bar`, `body_not_cross`.
- Risk and space: `stop_defined`, `reward_ok`, `vwap_*`.
- No-trade filters: failed checkpoints plus `forbidden_absent` only when it carries useful no-trade explanation.

Checkpoint keys without a user-facing label or useful reason text should be hidden from chips but may still appear in the review explanation.

Review should show:

- Reasons the user selected that matched standard evidence.
- Important reasons the user missed.
- Any selected reason contradicted by failed checkpoints. A selected reason is a contradiction when its matching checkpoint has `passed === false`.

## 4. Implementation Changes

### 4.1 TrainingPage

Refactor only `TrainingPage` in `dist/pages-2.jsx`.

Replace the visible step quiz UI with drill state:

```js
{
  phase: 'replay' | 'submitted' | 'review',
  currentIndex,
  revealCutoffIndex,
  selectedReasonKeys: [],
  waitLog: [],
  submittedAction: null,
  submittedIndex: null,
  review: null
}
```

`review` structure:

```js
{
  timingLabel: 'too_early' | 'valid_window' | 'late' | 'not_scored',
  expectedAction: '做多' | '做空' | '放弃' | null,
  actionCorrect: boolean | null,
  timingCorrect: boolean | null,
  submittedIndex,
  signalIndex,
  validWindow: { start, end },
  reasonHits: [],
  reasonMisses: [],
  reasonContradictions: [],
  reviewText
}
```

When `expectedAction === null`, the drill is replay-only: set `timingLabel = 'not_scored'`, `actionCorrect = null`, and `timingCorrect = null`.

`waitLog` is a behavior log, not a second scoring system. It is used in the review panel to show how long the user waited before committing.

Keep the current case tabs, but label them as case selection, not quiz variants.

### 4.2 KlineView Integration

Use existing adapter capabilities:

- `revealCutoff` to hide future bars.
- `highlightRanges` to show standard window and review evidence after submission.
- `onPlaybackChange` / existing control callbacks for current index state.
- Existing engine 1m/5m switching with viewport time anchoring.

If `KlineView` does not expose enough current index/control state to `TrainingPage`, extend `KlineEngineAdapter` with a narrow callback instead of mutating engine private fields.

Replay phase invariant:

- `revealCutoffIndex === currentIndex`.
- Every wait advances both by one.

Submitted/review phase invariant:

- `revealCutoffIndex` may be ahead of `currentIndex` so outcome playback can run until the reveal target.

### 4.3 Data Fallback

Do not make `training/checkpoints.json` mandatory for the drill.

Training case list priority:

1. `TRAINING_ITEMS` when available.
2. Cases matching the module id.
3. Segments matching the module/category only as replay-only fallback, not as scored drill.

Reason chips and review should come from `segment.derived.checkpoints` first.

When falling back to segments without cases, use category matching only when the module-category relationship is explicit in local constants. Example: `ma10` may include `support_ma10` and `reject_ma10`. Do not infer broad category matches from display text.

### 4.4 Dormant Code

Do not invoke `Aggregate5mBand`.

The dormant helpers may remain for now, but the drill redesign should not depend on them. A later cleanup can remove them once the new direction is stable.

## 5. Acceptance Checks

Manual browser checks:

- `#training/ma10` opens without the old 7-step question panel as the primary interaction.
- Future bars are hidden at start.
- Start index is at least 8 bars before the standard signal when data permits.
- `等待` advances exactly one 1m bar, keeps future bars hidden, and adds one wait-log entry.
- Waiting 3 times and then submitting shows 3 wait-log entries in the review panel.
- User can submit `做多`, `做空`, or `放弃` at any visible bar.
- Submitting on 5m switches back to 1m for outcome playback.
- Submitting reveals up to `min(submittedIndex + 12, last1mIndex)`, plays to that target, then shows review.
- A Support MA10 action inside the standard window is reviewed as correct direction and valid timing.
- A Support MA10 action before the standard window is reviewed as too early.
- A Reject MA10 case reviews `做空` as the expected direction and `做多` as wrong direction.
- Anti or case-answer-pass examples review `放弃` as correct.
- Reason chips produce hit/miss/missing feedback based on checkpoints.
- 1m/5m toolbar switching remains visible in lab mode and stays time-centered.
- No `Aggregate5mBand` strip appears.

Regression checks:

- `KlineEngine` standalone integration test still passes.
- Hub/module/case/mistake pages still render as before.
- Existing `KlineView mode="mini"` and `mode="evidence"` behavior is unchanged.

## 6. Non-Goals

- Do not redesign the whole K-line UX outside training.
- Do not add a backend.
- Do not build a full free-trading simulator with P/L accounting.
- Do not require users to type stop prices in the first version.
- Do not add leaderboard, badges, or gamified scoring.
- Do not revive the 5m live aggregation strip.

## 7. Files To Read First

Implementation should start with this reading order:

1. `HANDOFF.md`
2. `training-replay-drill-redesign-plan.md`
3. `dist/pages-2.jsx`
4. `dist/shared.jsx`
5. `dist/kline-engine/INTEGRATION.md`
