import { BarChart3, BookOpen, Database, LineChart, LogOut, RefreshCcw } from 'lucide-react';
import { clearSession, getRole } from '../api/client.js';

const nav = [
  ['dashboard', Database, 'Data'],
  ['review', LineChart, 'Review'],
  ['backtest', BarChart3, 'Backtest'],
  ['teaching', BookOpen, 'Teaching'],
];

export function Layout({ active, onNavigate, children }) {
  const role = getRole();
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">TS</span>
          <div>
            <h1>Tang Strategy</h1>
            <p>{role || 'readonly'} workspace</p>
          </div>
        </div>
        <nav>
          {nav.map(([id, Icon, label]) => (
            <button key={id} className={active === id ? 'active' : ''} onClick={() => onNavigate(id)}>
              <Icon size={18} />
              {label}
            </button>
          ))}
        </nav>
        {role === 'admin' && (
          <button className="secondary" onClick={() => onNavigate('admin')}>
            <RefreshCcw size={18} />
            Import seed
          </button>
        )}
        <button className="logout" onClick={() => { clearSession(); window.location.reload(); }}>
          <LogOut size={18} />
          Logout
        </button>
      </aside>
      <main>{children}</main>
    </div>
  );
}
