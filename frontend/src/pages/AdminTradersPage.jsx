import { useMemo, useState } from 'react';
import { TradeExportControls } from '../features/review/TradeExportControls.jsx';
import { TraderFilters } from '../features/review/TraderFilters.jsx';
import { TraderTradeList } from '../features/review/TraderTradeList.jsx';
import {
  buildTradeAvailability,
  canEditTradeRecords,
  filterTradeGroups,
  initialTradeRecordFilters,
  resolveTradeDate,
  summarizeTradeGroups,
} from '../features/review/tradeRecords.js';

export function AdminTradersPage({ role = 'readonly', payloads = [], onSaveRegistry, onSaveDay }) {
  const traders = payloads[0]?.traders || [];
  const [filters, setFilters] = useState(() => initialTradeRecordFilters(traders));
  const [registryText, setRegistryText] = useState(() => JSON.stringify({ schema_version: 'traders-v1', traders }, null, 2));
  const [dayText, setDayText] = useState('');
  const availability = useMemo(() => buildTradeAvailability(payloads), [payloads]);
  const resolvedFilters = useMemo(() => ({
    ...filters,
    tradeDate: resolveTradeDate(availability, filters.ticker, filters.tradeDate),
  }), [availability, filters]);
  const payload = payloads.find((item) => (
    item.ticker === resolvedFilters.ticker && item.trade_date === resolvedFilters.tradeDate
  )) || payloads[0];
  const groups = useMemo(
    () => filterTradeGroups(payload, resolvedFilters),
    [payload, resolvedFilters],
  );
  const summary = useMemo(() => summarizeTradeGroups(groups), [groups]);
  const isAdmin = canEditTradeRecords(role);

  function parseAndSave(raw, handler) {
    if (!isAdmin) return;
    handler?.(JSON.parse(raw));
  }

  return (
    <div className="admin-traders-page">
      <header>
        <div>
          <h2>Trader records fixture workspace</h2>
          <p>Phase 4 preview only; live backend routes are not registered.</p>
        </div>
        <TradeExportControls payload={payload} groups={groups} filters={resolvedFilters} />
      </header>
      <TraderFilters traders={traders} availability={availability} value={resolvedFilters} onChange={setFilters} />
      <div className="trade-stat-grid">
        <span>Groups <strong>{summary.group_count}</strong></span>
        <span>Reported win rate <strong>{summary.reported.win_rate == null ? '--' : `${(summary.reported.win_rate * 100).toFixed(1)}%`}</strong></span>
        <span>Calculated win rate <strong>{summary.calculated.win_rate == null ? '--' : `${(summary.calculated.win_rate * 100).toFixed(1)}%`}</strong></span>
      </div>
      <TraderTradeList groups={groups} traders={traders} />
      <section className="trade-admin-editors" aria-disabled={!isAdmin}>
        <label>
          Trader registry JSON
          <textarea value={registryText} onChange={(event) => setRegistryText(event.target.value)} disabled={!isAdmin} />
          <button type="button" disabled={!isAdmin} onClick={() => parseAndSave(registryText, onSaveRegistry)}>Validate registry candidate</button>
        </label>
        <label>
          Daily record JSON
          <textarea value={dayText} onChange={(event) => setDayText(event.target.value)} disabled={!isAdmin} />
          <button type="button" disabled={!isAdmin || !dayText} onClick={() => parseAndSave(dayText, onSaveDay)}>Validate daily candidate</button>
        </label>
      </section>
    </div>
  );
}
