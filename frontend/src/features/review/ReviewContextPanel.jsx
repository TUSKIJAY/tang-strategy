import { useEffect, useMemo, useState } from 'react';
import {
  enterMonthBrowseMode,
  enterRecentBrowseMode,
  groupDatesByMonth,
  initializeProgressiveBrowseState,
  listTickers,
  projectProgressiveDateRail,
  stepBrowsedMonth,
} from './reviewWorkspace.js';

// Shared workspace navigation (plan §3.1): ticker is the authoritative parent
// context, dates render only for the selected ticker, and the selected state is
// visible and programmatic. Used by Data, Review, Admin, and Static Review.
// Progressive mode is opt-in via dateNavigation="progressive" (Review + Data).

export function TickerTabs({ tickers, value, onChange }) {
  return (
    <div className="ticker-tabs" role="tablist" aria-label="Ticker workspace">
      {tickers.map((ticker) => (
        <button
          key={ticker}
          type="button"
          role="tab"
          aria-selected={ticker === value}
          className={ticker === value ? 'active' : ''}
          onClick={() => onChange?.(ticker)}
        >
          {ticker}
        </button>
      ))}
    </div>
  );
}

export function DateRail({
  days,
  ticker,
  value,
  onSelect,
  dateNavigation = 'exhaustive',
}) {
  const progressive = dateNavigation === 'progressive';
  const [browseState, setBrowseState] = useState(() => (
    progressive
      ? initializeProgressiveBrowseState(days, ticker, value)
      : { browseMode: 'recent', browsedMonth: '' }
  ));

  // Reinitialize presentation only when ticker or inventory changes.
  // Day-chip selection must preserve browseMode (plan §3.1); value is not a
  // reinit trigger — chip onClick already keeps month mode / browsedMonth.
  useEffect(() => {
    if (!progressive) return;
    setBrowseState(initializeProgressiveBrowseState(days, ticker, value));
    // value intentionally omitted: chip select must not reset browseMode.
    // eslint-disable-next-line react-hooks/exhaustive-deps -- reinit on ticker/inventory only
  }, [progressive, days, ticker]);

  const projection = useMemo(() => {
    if (!progressive) return null;
    return projectProgressiveDateRail({
      days,
      ticker,
      selectedDate: value,
      browseMode: browseState.browseMode,
      browsedMonth: browseState.browsedMonth,
    });
  }, [progressive, days, ticker, value, browseState.browseMode, browseState.browsedMonth]);

  if (!progressive) {
    const months = groupDatesByMonth(days, ticker);
    return (
      <div className="date-rail" aria-label={`${ticker} market days`}>
        {months.map((month) => (
          <div className="date-rail-month" key={month.month}>
            <div className="date-rail-month-label">{month.month}</div>
            <div className="date-rail-dates">
              {month.dates.map((date) => (
                <button
                  key={date}
                  type="button"
                  aria-pressed={date === value}
                  className={date === value ? 'active' : ''}
                  title={date}
                  aria-label={`${ticker} ${date}`}
                  onClick={() => onSelect?.(date)}
                >
                  {date.slice(5)}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
    );
  }

  const mode = projection.browseMode;
  const pressed = projection.pressedDate;

  return (
    <div className="date-rail date-rail--progressive" aria-label={`${ticker} market days`}>
      <div className="date-rail-mode" role="group" aria-label="日期浏览模式">
        <button
          type="button"
          className={mode === 'recent' ? 'active' : ''}
          aria-pressed={mode === 'recent'}
          onClick={() => setBrowseState(enterRecentBrowseMode(
            days,
            ticker,
            value,
            browseState.browsedMonth,
          ))}
        >
          最近
        </button>
        <button
          type="button"
          className={mode === 'month' ? 'active' : ''}
          aria-pressed={mode === 'month'}
          onClick={() => setBrowseState(enterMonthBrowseMode(days, ticker, value))}
        >
          按月
        </button>
      </div>

      {mode === 'month' && projection.monthBar && (
        <div className="date-rail-month-bar">
          <button
            type="button"
            className="date-rail-month-nav"
            aria-label="上一个月"
            disabled={!projection.monthBar.canOlder}
            onClick={() => setBrowseState(stepBrowsedMonth(
              days,
              ticker,
              projection.browsedMonth,
              'older',
            ))}
          >
            ‹
          </button>
          <div className="date-rail-month-identity" aria-live="polite">
            {projection.monthBar.month || '--'}
          </div>
          <button
            type="button"
            className="date-rail-month-nav"
            aria-label="下一个月"
            disabled={!projection.monthBar.canNewer}
            onClick={() => setBrowseState(stepBrowsedMonth(
              days,
              ticker,
              projection.browsedMonth,
              'newer',
            ))}
          >
            ›
          </button>
        </div>
      )}

      <div className={`date-rail-dates ${mode === 'month' ? 'day-only' : ''}`}>
        {projection.dates.map((date) => (
          <button
            key={date}
            type="button"
            aria-pressed={date === pressed}
            className={date === pressed ? 'active' : ''}
            title={date}
            aria-label={`${ticker} ${date}`}
            onClick={() => {
              onSelect?.(date);
              if (mode === 'month') {
                setBrowseState({ browseMode: 'month', browsedMonth: date.slice(0, 7) });
              }
            }}
          >
            {projection.chipLabels[date]}
          </button>
        ))}
      </div>
      <div className="date-rail-meta" aria-live="polite">{projection.meta}</div>
    </div>
  );
}

export function ReviewContextPanel({
  days,
  workspace,
  onSwitchTicker,
  onSelectDate,
  dateNavigation = 'exhaustive',
  children,
}) {
  const tickers = listTickers(days);
  return (
    <div className="review-context-panel">
      <TickerTabs tickers={tickers} value={workspace?.ticker || ''} onChange={onSwitchTicker} />
      <DateRail
        days={days}
        ticker={workspace?.ticker || ''}
        value={workspace?.trade_date || ''}
        onSelect={onSelectDate}
        dateNavigation={dateNavigation}
      />
      {children}
    </div>
  );
}
