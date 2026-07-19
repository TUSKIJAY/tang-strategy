import { useEffect, useMemo, useState } from 'react';
import { Api, getRole } from '../api/client.js';
import { preferredActivationWickStrategy } from '../features/review/session.js';
import { ReviewContextPanel } from '../features/review/ReviewContextPanel.jsx';
import {
  findDay,
  normalizeInteractiveDays,
  resolveInitialWorkspace,
  switchTicker,
} from '../features/review/reviewWorkspace.js';

export function DashboardPage({ state, setState, onNavigate }) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [importResult, setImportResult] = useState(null);
  const workspaceDays = useMemo(() => normalizeInteractiveDays(state.marketDays), [state.marketDays]);
  const workspace = useMemo(() => {
    const explicit = state.marketDays.find((day) => day.id === Number(state.selectedDayId));
    if (explicit) return { ticker: explicit.ticker, trade_date: explicit.trade_date, key: String(explicit.id) };
    const resolved = resolveInitialWorkspace({ days: workspaceDays });
    return resolved.day
      ? { ticker: resolved.ticker, trade_date: resolved.trade_date, key: resolved.key }
      : { ticker: '', trade_date: '', key: '' };
  }, [state.marketDays, state.selectedDayId, workspaceDays]);

  function handleSwitchTicker(ticker) {
    const current = findDay(workspaceDays, { ticker: workspace.ticker, tradeDate: workspace.trade_date });
    const next = switchTicker(workspaceDays, { day: current }, ticker);
    if (next.day?.ref) setState((prev) => ({ ...prev, selectedDayId: next.day.ref.id }));
  }

  function openReviewDay(tradeDate) {
    const day = findDay(workspaceDays, { ticker: workspace.ticker, tradeDate });
    if (!day?.ref) return;
    setState((prev) => ({ ...prev, selectedDayId: day.ref.id }));
    onNavigate?.('review');
  }

  async function load() {
    setLoading(true);
    setError('');
    try {
      const [tickers, marketDays, strategies] = await Promise.all([
        Api.tickers(),
        Api.marketDays(),
        Api.strategies(),
      ]);
      setState((prev) => {
        const preferred = preferredActivationWickStrategy(strategies);
        return {
          ...prev,
          tickers,
          marketDays,
          strategies,
          selectedStrategyId: prev.selectedStrategyId || preferred?.id || '',
        };
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function importSeed() {
    setImportResult(null);
    const result = await Api.importSeed();
    setImportResult(result);
    await load();
  }

  return (
    <section className="page">
      <div className="page-header">
        <p className="eyebrow">SQLite workspace</p>
        <h2>Market data and strategies</h2>
        <p>Data is served by FastAPI and persisted in SQLite. Review and backtest calculations run in the browser.</p>
      </div>
      {error && <div className="error">{error}</div>}
      {getRole() === 'admin' && <button onClick={importSeed}>Import default seed</button>}
      {importResult && <pre>{JSON.stringify(importResult, null, 2)}</pre>}
      {loading ? <p>Loading...</p> : (
        <div className="grid three">
          <Metric label="Tickers" value={state.tickers.length} />
          <Metric label="Market days" value={state.marketDays.length} />
          <Metric label="Strategies" value={state.strategies.length} />
        </div>
      )}
      <div className="panel">
        <h3>Market days</h3>
        <ReviewContextPanel
          days={workspaceDays}
          workspace={workspace}
          onSwitchTicker={handleSwitchTicker}
          onSelectDate={openReviewDay}
        />
      </div>
    </section>
  );
}

function Metric({ label, value }) {
  return <div className="metric"><span>{label}</span><strong>{value}</strong></div>;
}
