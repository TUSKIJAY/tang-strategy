import { useEffect, useState } from 'react';
import { Api, getRole } from '../api/client.js';

export function DashboardPage({ state, setState }) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [importResult, setImportResult] = useState(null);

  async function load() {
    setLoading(true);
    setError('');
    try {
      const [tickers, marketDays, strategies] = await Promise.all([
        Api.tickers(),
        Api.marketDays(),
        Api.strategies(),
      ]);
      setState((prev) => ({ ...prev, tickers, marketDays, strategies }));
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
        <h3>Recent market days</h3>
        <div className="table">
          {state.marketDays.slice(0, 20).map((day) => (
            <button key={day.id} onClick={() => setState((prev) => ({ ...prev, selectedDayId: day.id }))}>
              <span>{day.ticker}</span>
              <span>{day.trade_date}</span>
              <span>{day.bar_count_1m} x 1m</span>
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}

function Metric({ label, value }) {
  return <div className="metric"><span>{label}</span><strong>{value}</strong></div>;
}
