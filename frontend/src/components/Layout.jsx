import { useState } from 'react';
import { BarChart3, BookOpen, Database, LineChart, LogOut, PanelLeftClose, PanelLeftOpen, RefreshCcw } from 'lucide-react';
import { clearSession, getRole } from '../api/client.js';

const nav = [
  ['dashboard', Database, 'Data'],
  ['review', LineChart, 'Review'],
  ['backtest', BarChart3, 'Backtest'],
  ['teaching', BookOpen, 'Teaching'],
];

export function Layout({ active, onNavigate, children }) {
  const role = getRole();
  const [collapsed, setCollapsed] = useState(() => window.localStorage?.getItem('tangStrategy:sidebarCollapsed') === 'true');

  function toggleCollapsed() {
    setCollapsed((value) => {
      const next = !value;
      try { window.localStorage?.setItem('tangStrategy:sidebarCollapsed', String(next)); } catch (_) {}
      return next;
    });
  }

  return (
    <div className={`app-shell ${collapsed ? 'nav-collapsed' : ''}`}>
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">TS</span>
          <div className="brand-copy">
            <h1>Tang Strategy</h1>
            <p>{role || 'readonly'} workspace</p>
          </div>
          <button className="sidebar-toggle" type="button" onClick={toggleCollapsed} title={collapsed ? 'Expand navigation' : 'Collapse navigation'} aria-label={collapsed ? 'Expand navigation' : 'Collapse navigation'}>
            {collapsed ? <PanelLeftOpen size={18} /> : <PanelLeftClose size={18} />}
          </button>
        </div>
        <nav>
          {nav.map(([id, Icon, label]) => (
            <button key={id} className={active === id ? 'active' : ''} onClick={() => onNavigate(id)} title={label}>
              <Icon size={18} />
              <span className="nav-label">{label}</span>
            </button>
          ))}
        </nav>
        {role === 'admin' && (
          <button className="secondary" onClick={() => onNavigate('admin')} title="Import seed">
            <RefreshCcw size={18} />
            <span className="nav-label">Import seed</span>
          </button>
        )}
        <button className="logout" onClick={() => { clearSession(); window.location.reload(); }} title="Logout">
          <LogOut size={18} />
          <span className="nav-label">Logout</span>
        </button>
      </aside>
      <main>{children}</main>
    </div>
  );
}
