import { initialTradeRecordFilters, resolveTradeDate } from './tradeRecords.js';

export function TraderFilters({ traders = [], availability = {}, value, onChange }) {
  const filters = value || initialTradeRecordFilters(traders);
  const tickers = Object.keys(availability).sort();
  const dates = availability[filters.ticker] || [];
  const selectedDate = resolveTradeDate(availability, filters.ticker, filters.tradeDate);

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
      <label>
        Eligibility
        <select value={filters.eligibility} onChange={(event) => update({ eligibility: event.target.value })}>
          <option value="display">Display</option>
          <option value="reported">Reported stats</option>
          <option value="calculated">Calculated stats</option>
        </select>
      </label>
      <div className="trade-trader-options">
        {traders.map((trader) => (
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
              onClick={() => update({
                focusedTraderId: filters.focusedTraderId === trader.trader_id ? '' : trader.trader_id,
              })}
            >
              Focus
            </button>
          </div>
        ))}
      </div>
    </section>
  );
}
