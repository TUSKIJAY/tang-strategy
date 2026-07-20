import { useState } from 'react';
import { BarChart3, BookOpen, Database, LineChart, LogOut, PanelLeftClose, PanelLeftOpen, UsersRound } from 'lucide-react';
import { clearSession, getRole } from '../api/client.js';

const NAV_ITEMS = [
  { id: 'dashboard', Icon: Database, label: 'Data' },
  { id: 'review', Icon: LineChart, label: 'Review' },
  { id: 'backtest', Icon: BarChart3, label: 'Backtest' },
  { id: 'teaching', Icon: BookOpen, label: 'Teaching' },
];

function NavItem({ active, capability, Icon, id, label, onNavigate }) {
  const accessibleName = capability ? `${label}（${capability}）` : label;

  return (
    <button
      type="button"
      className="nav-item"
      aria-current={active === id ? 'page' : undefined}
      aria-label={accessibleName}
      onClick={() => onNavigate(id)}
      title={accessibleName}
    >
      <Icon size={18} aria-hidden="true" />
      <span className="nav-label">{label}</span>
      {capability ? <span className="nav-role-badge">{capability}</span> : null}
    </button>
  );
}

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
        <nav aria-label="Primary navigation">
          <div className="nav-primary-stack">
            {NAV_ITEMS.map((item) => (
              <NavItem key={item.id} {...item} active={active} onNavigate={onNavigate} />
            ))}
          </div>
          <div className="nav-bottom-stack">
            <NavItem
              id="admin"
              Icon={UsersRound}
              label="交易记录 / 点位管理"
              capability={role === 'admin' ? '管理员可编辑' : '只读检查，编辑需要管理员'}
              active={active}
              onNavigate={onNavigate}
            />
          </div>
        </nav>
        <button className="logout" type="button" onClick={() => { clearSession(); window.location.reload(); }} title="Logout">
          <LogOut size={18} aria-hidden="true" />
          <span className="nav-label">Logout</span>
        </button>
      </aside>
      <main>{children}</main>
    </div>
  );
}
