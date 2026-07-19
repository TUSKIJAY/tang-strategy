import { initialTradeRecordFilters, resolveTradeDate } from './tradeRecords.js';

// Trader filter contract (plan §3.1/§3.3):
// - When `context` is provided, ticker/date render only as readonly mirrors of
//   the resolved workspace; this component never owns editable ticker/date
//   authority in that mode.
// - When `availableTraderIds` is provided, only traders with a displayable
//   group in the resolved context render; an empty availability set shows one
//   neutral message instead of the global registry.
// The legacy select-based branch remains only until the Review/Static/Admin
// pages are rewired to the shared workspace in Phases 2-3.
export function TraderFilters({
  traders = [],
  availability = {},
  value,
  onChange,
  context = null,
  availableTraderIds = null,
  emptyMessage = '当前 ticker/date 没有可显示的交易者点位。',
}) {
  const filters = value || initialTradeRecordFilters(traders);
  const tickers = Object.keys(availability).sort();
  const dates = availability[filters.ticker] || [];
  const selectedDate = resolveTradeDate(availability, filters.ticker, filters.tradeDate);
  const visibleTraders = availableTraderIds
    ? traders.filter((trader) => availableTraderIds.includes(trader.trader_id))
    : traders;

  function update(patch) {
    onChange?.({ ...filters, ...patch });
  }

  function toggleTrader(traderId) {
    const selected = new Set(filters.traderIds || []);
    if (selected.has(traderId)) selected.delete(traderId);
    else selected.add(traderId);
    update({ traderIds: [...selected], focusedTraderId: '' });
  }

  return (
    <section className="trade-filter-panel" aria-label="Trade record filters">
      {context ? (
        <div className="trade-context-mirror" aria-label="当前复盘上下文">
          <span className="trade-context-mirror-item" aria-label="Ticker" aria-readonly="true">
            {context.ticker}
          </span>
          <span className="trade-context-mirror-item" aria-label="Date" aria-readonly="true">
            {context.tradeDate}
          </span>
        </div>
      ) : (
        <>
          <label>
            Ticker
            <select
              value={filters.ticker}
              onChange={(event) => update({
                ticker: event.target.value,
                tradeDate: availability[event.target.value]?.at(-1) || '',
              })}
            >
              {tickers.map((ticker) => <option key={ticker}>{ticker}</option>)}
            </select>
          </label>
          <label>
            Date
            <select value={selectedDate} onChange={(event) => update({ tradeDate: event.target.value })}>
              {dates.map((date) => <option key={date}>{date}</option>)}
            </select>
          </label>
        </>
      )}
      <label>
        Eligibility
        <select value={filters.eligibility} onChange={(event) => update({ eligibility: event.target.value })}>
          <option value="display">Display</option>
          <option value="reported">Reported stats</option>
          <option value="calculated">Calculated stats</option>
        </select>
      </label>
      {availableTraderIds && visibleTraders.length === 0 ? (
        <p className="trade-trader-empty" role="status">{emptyMessage}</p>
      ) : (
        <div className="trade-trader-options">
          {visibleTraders.map((trader) => (
            <div key={trader.trader_id} className="trade-trader-option" style={{ '--trader-color': trader.color }}>
              <label>
                <input
                  type="checkbox"
                  checked={(filters.traderIds || []).includes(trader.trader_id)}
                  onChange={() => toggleTrader(trader.trader_id)}
                />
                <span>{trader.display_name}</span>
              </label>
              <button
                type="button"
                className={filters.focusedTraderId === trader.trader_id ? 'active' : ''}
                aria-pressed={filters.focusedTraderId === trader.trader_id}
                onClick={() => update({
                  focusedTraderId: filters.focusedTraderId === trader.trader_id ? '' : trader.trader_id,
                })}
              >
                Focus
              </button>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
