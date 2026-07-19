import { groupDatesByMonth, listTickers } from './reviewWorkspace.js';

// Shared workspace navigation (plan §3.1): ticker is the authoritative parent
// context, dates render only for the selected ticker grouped by month, and the
// selected state is visible and programmatic. Used by Data, Review, and Static
// Review so all three surfaces share one selection contract.
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

export function DateRail({ days, ticker, value, onSelect }) {
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

export function ReviewContextPanel({ days, workspace, onSwitchTicker, onSelectDate, children }) {
  const tickers = listTickers(days);
  return (
    <div className="review-context-panel">
      <TickerTabs tickers={tickers} value={workspace?.ticker || ''} onChange={onSwitchTicker} />
      <DateRail
        days={days}
        ticker={workspace?.ticker || ''}
        value={workspace?.trade_date || ''}
        onSelect={onSelectDate}
      />
      {children}
    </div>
  );
}
