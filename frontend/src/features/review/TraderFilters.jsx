import { useId, useMemo, useState } from 'react';
import {
  initialTradeRecordFilters,
  resolveTradeDate,
  traderSelectionSummary,
  TRADER_CHIP_INLINE_MAX,
} from './tradeRecords.js';

// B Chip trader visibility (plan §3.2):
// - traderIds is the only visibility authority.
// - When `context` is supplied, resolved-context mirror is omitted; workspace owns day.
// - availableTraderIds drives chips; empty availability shows one neutral message.
// - <=6 chips inline; >=7 summary + Edit drawer with search/Select all/Clear.

export function TraderFilters({
  traders = [],
  availability = {},
  value,
  onChange,
  context = null,
  availableTraderIds = null,
  emptyMessage = '当前 ticker/date 没有可显示的交易者点位。',
  exportControls = null,
}) {
  const filters = value || initialTradeRecordFilters(traders);
  const tickers = Object.keys(availability).sort();
  const dates = availability[filters.ticker] || [];
  const selectedDate = resolveTradeDate(availability, filters.ticker, filters.tradeDate);
  const visibleTraders = availableTraderIds
    ? traders.filter((trader) => availableTraderIds.includes(trader.trader_id))
    : traders;
  const drawerId = useId();
  const searchId = useId();
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [search, setSearch] = useState('');

  function update(patch) {
    onChange?.({ ...filters, ...patch });
  }

  function toggleTrader(traderId) {
    const selected = new Set(filters.traderIds || []);
    if (selected.has(traderId)) selected.delete(traderId);
    else selected.add(traderId);
    // Keep UI order stable: availability/registry order of visible traders.
    const ordered = visibleTraders
      .map((trader) => trader.trader_id)
      .filter((id) => selected.has(id));
    update({ traderIds: ordered });
  }

  function selectAll() {
    update({ traderIds: visibleTraders.map((trader) => trader.trader_id) });
  }

  function clearAll() {
    update({ traderIds: [] });
  }

  const selectedSet = useMemo(
    () => new Set(filters.traderIds || []),
    [filters.traderIds],
  );
  const summary = useMemo(
    () => traderSelectionSummary(visibleTraders, filters.traderIds || []),
    [visibleTraders, filters.traderIds],
  );
  const useDrawer = visibleTraders.length > TRADER_CHIP_INLINE_MAX;
  const query = search.trim().toLowerCase();
  const displayedTraders = useMemo(() => {
    if (!query) return visibleTraders;
    return visibleTraders.filter((trader) => {
      const name = String(trader.display_name || '').toLowerCase();
      const id = String(trader.trader_id || '').toLowerCase();
      return name.includes(query) || id.includes(query);
    });
  }, [visibleTraders, query]);

  function renderChips(list) {
    return (
      <div className="trade-trader-chips" role="group" aria-label="交易者可见性">
        {list.map((trader) => {
          const pressed = selectedSet.has(trader.trader_id);
          return (
            <button
              key={trader.trader_id}
              type="button"
              className={`trade-trader-chip ${pressed ? 'active' : ''}`}
              aria-pressed={pressed}
              onClick={() => toggleTrader(trader.trader_id)}
            >
              {trader.display_name || trader.trader_id}
            </button>
          );
        })}
      </div>
    );
  }

  return (
    <section className="trade-filter-panel" aria-label="Trade record filters">
      <div className="trade-tools-head">
        <span className="trade-tools-title">Trade tools</span>
        {exportControls}
      </div>

      {!context && (
        <div className="trade-tools-row trade-context-selects">
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
        </div>
      )}

      <div className="trade-tools-row">
        <fieldset className="trade-eligibility-fieldset">
          <legend className="trade-filter-label">Eligibility</legend>
          <div className="trade-eligibility-seg" role="radiogroup" aria-label="Eligibility">
            <label className={`trade-eligibility-option ${filters.eligibility === 'display' ? 'active' : ''}`}>
              <input
                type="radio"
                name="eligibility"
                value="display"
                checked={filters.eligibility === 'display'}
                onChange={(event) => update({ eligibility: event.target.value })}
              />
              <span>Display</span>
            </label>
            <label className={`trade-eligibility-option ${filters.eligibility === 'reported' ? 'active' : ''}`}>
              <input
                type="radio"
                name="eligibility"
                value="reported"
                checked={filters.eligibility === 'reported'}
                onChange={(event) => update({ eligibility: event.target.value })}
              />
              <span>Reported</span>
            </label>
            <label className={`trade-eligibility-option ${filters.eligibility === 'calculated' ? 'active' : ''}`}>
              <input
                type="radio"
                name="eligibility"
                value="calculated"
                checked={filters.eligibility === 'calculated'}
                onChange={(event) => update({ eligibility: event.target.value })}
              />
              <span>Calculated</span>
            </label>
          </div>
        </fieldset>
      </div>

      <div className="trade-tools-row trade-traders-row">
        <span className="trade-filter-label">Traders</span>
        {availableTraderIds && visibleTraders.length === 0 ? (
          <p className="trade-trader-empty" role="status">{emptyMessage}</p>
        ) : useDrawer ? (
          <div className="trade-trader-summary-row">
            <span className="trade-trader-summary" aria-live="polite">
              {summary.selectedCount === 0
                ? 'No traders selected'
                : `${summary.selectedCount} selected · ${summary.names.join(', ')}${summary.overflow ? ` +${summary.overflow}` : ''}`}
            </span>
            <button
              type="button"
              className="trade-trader-edit"
              aria-expanded={drawerOpen}
              aria-controls={drawerId}
              onClick={() => setDrawerOpen((open) => !open)}
            >
              Edit
            </button>
            {drawerOpen && (
              <div className="trade-trader-drawer" id={drawerId}>
                <label className="trade-trader-search" htmlFor={searchId}>
                  Search traders
                  <input
                    id={searchId}
                    type="search"
                    value={search}
                    onChange={(event) => setSearch(event.target.value)}
                    placeholder="Name or ID"
                  />
                </label>
                <div className="trade-trader-drawer-actions">
                  <button type="button" onClick={selectAll}>Select all</button>
                  <button type="button" onClick={clearAll}>Clear</button>
                </div>
                {displayedTraders.length === 0 ? (
                  <p className="trade-trader-empty" role="status">No matching traders</p>
                ) : (
                  renderChips(displayedTraders)
                )}
              </div>
            )}
          </div>
        ) : (
          renderChips(visibleTraders)
        )}
      </div>
    </section>
  );
}
