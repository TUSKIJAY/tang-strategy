import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';
import { getToken } from './api/client.js';
import { Layout } from './components/Layout.jsx';
import { LoginPage } from './pages/LoginPage.jsx';
import { DashboardPage } from './pages/DashboardPage.jsx';
import { ReviewPage } from './pages/ReviewPage.jsx';
import { BacktestPage } from './pages/BacktestPage.jsx';
import { TeachingPage } from './pages/TeachingPage.jsx';
import { StaticReviewsApp } from './pages/StaticReviewsApp.jsx';
import './pages/AdminTradersPage.jsx';
import './styles.css';

function App() {
  const [authenticated, setAuthenticated] = useState(Boolean(getToken()));
  const [active, setActive] = useState('dashboard');
  const [state, setState] = useState({ tickers: [], marketDays: [], strategies: [], selectedDayId: '', selectedStrategyId: '' });

  if (!authenticated) return <LoginPage onLogin={() => setAuthenticated(true)} />;

  return (
    <Layout active={active} onNavigate={setActive}>
      {active === 'dashboard' && <DashboardPage state={state} setState={setState} />}
      {active === 'review' && <ReviewPage state={state} setState={setState} />}
      {active === 'backtest' && <BacktestPage state={state} setState={setState} />}
      {active === 'teaching' && <TeachingPage state={state} setState={setState} />}
      {active === 'admin' && <DashboardPage state={state} setState={setState} />}
    </Layout>
  );
}

createRoot(document.getElementById('root')).render(
  import.meta.env.VITE_STATIC_REVIEWS === 'true' ? <StaticReviewsApp /> : <App />,
);
