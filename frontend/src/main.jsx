import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Api, getRole, getToken } from './api/client.js';
import { Layout } from './components/Layout.jsx';
import { LoginPage } from './pages/LoginPage.jsx';
import { DashboardPage } from './pages/DashboardPage.jsx';
import { ReviewPage } from './pages/ReviewPage.jsx';
import { BacktestPage } from './pages/BacktestPage.jsx';
import { TeachingPage } from './pages/TeachingPage.jsx';
import { StaticReviewsApp } from './pages/StaticReviewsApp.jsx';
import { AdminTradersPage } from './pages/AdminTradersPage.jsx';
import './styles.css';

function App() {
  const [authenticated, setAuthenticated] = useState(Boolean(getToken()));
  const [active, setActive] = useState('dashboard');
  const [state, setState] = useState({ tickers: [], marketDays: [], strategies: [], selectedDayId: '', selectedStrategyId: '' });
  const [tradeRecordPayloads, setTradeRecordPayloads] = useState([]);

  async function loadTradeRecords() {
    const [spy, qqq] = await Promise.all([
      Api.tradeRecords({ ticker: 'SPY' }),
      Api.tradeRecords({ ticker: 'QQQ' }),
    ]);
    setTradeRecordPayloads([...spy, ...qqq]);
  }

  useEffect(() => {
    if (active === 'admin') loadTradeRecords().catch(() => setTradeRecordPayloads([]));
  }, [active]);

  async function saveTraders(payload) {
    await Api.saveTraders(payload);
    await loadTradeRecords();
  }

  async function saveTradeDay(payload) {
    await Api.saveTradeRecords(payload);
    await loadTradeRecords();
  }

  if (!authenticated) return <LoginPage onLogin={() => setAuthenticated(true)} />;

  return (
    <Layout active={active} onNavigate={setActive}>
      {active === 'dashboard' && <DashboardPage state={state} setState={setState} />}
      {active === 'review' && <ReviewPage state={state} setState={setState} />}
      {active === 'backtest' && <BacktestPage state={state} setState={setState} />}
      {active === 'teaching' && <TeachingPage state={state} setState={setState} />}
      {active === 'admin' && (
        <AdminTradersPage
          role={getRole()}
          payloads={tradeRecordPayloads}
          onSaveRegistry={saveTraders}
          onSaveDay={saveTradeDay}
        />
      )}
    </Layout>
  );
}

createRoot(document.getElementById('root')).render(
  import.meta.env.VITE_STATIC_REVIEWS === 'true' ? <StaticReviewsApp /> : <App />,
);
