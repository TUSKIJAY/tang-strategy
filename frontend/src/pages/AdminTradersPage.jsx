import { useEffect, useMemo, useState } from 'react';
import { Api } from '../api/client.js';
import { ReviewContextPanel } from '../features/review/ReviewContextPanel.jsx';
import { TradeExportControls } from '../features/review/TradeExportControls.jsx';
import { TraderFilters } from '../features/review/TraderFilters.jsx';
import { TraderPointEditor } from '../features/review/TraderPointEditor.jsx';
import { TraderTradeList } from '../features/review/TraderTradeList.jsx';
import {
  canEditTradeRecords,
  deriveAvailableTraders,
  filterTradeGroups,
  initialTradeRecordFilters,
  reconcileTraderSelection,
  summarizeTradeGroups,
} from '../features/review/tradeRecords.js';
import {
  findDay,
  normalizeInteractiveDays,
  resolveInitialWorkspace,
  selectWorkspaceDay,
  switchTicker,
} from '../features/review/reviewWorkspace.js';

// Authenticated trader workspace (plan §3.4): every role can inspect and
// export; only admins see the form-driven point editor and registry metadata
// form. Raw JSON editing is no longer a workflow.
export function AdminTradersPage({ role = 'readonly', payloads = [], marketDays = [], onSaveRegistry, onSaveDay }) {
  const isAdmin = canEditTradeRecords(role);
  const workspaceDays = useMemo(() => normalizeInteractiveDays(marketDays), [marketDays]);
  const [workspace, setWorkspace] = useState(() => {
    const resolved = resolveInitialWorkspace({ days: normalizeInteractiveDays(marketDays) });
    return { ticker: resolved.ticker, trade_date: resolved.trade_date, key: resolved.key };
  });
  const [filters, setFilters] = useState(() => initialTradeRecordFilters());
  const [registryDoc, setRegistryDoc] = useState(null);
  const [registryDraft, setRegistryDraft] = useState(null);
  const [registryState, setRegistryState] = useState({ saving: false, error: '', success: '' });

  const payload = useMemo(
    () => payloads.find((item) => (
      item.ticker === workspace.ticker && item.trade_date === workspace.trade_date
    )) || null,
    [payloads, workspace],
  );
  const traders = useMemo(
    () => payloads.find((item) => item?.traders?.length)?.traders || [],
    [payloads],
  );
  const traderAvailability = useMemo(
    () => (payload ? deriveAvailableTraders(payload, payload.traders, filters) : { availableTraderIds: [] }),
    [payload, filters],
  );

  // Reconcile the inspection selection against availability on context change.
  useEffect(() => {
    setFilters((previous) => {
      const reconciled = reconcileTraderSelection({
        previousSelectedIds: previous ? previous.traderIds : null,
        previousFocusedId: previous?.focusedTraderId || '',
        availableTraderIds: traderAvailability.availableTraderIds,
        contextChanged: true,
      });
      return {
        ...initialTradeRecordFilters(traders),
        ticker: workspace.ticker,
        tradeDate: workspace.trade_date,
        traderIds: reconciled.selectedTraderIds,
        focusedTraderId: reconciled.focusedTraderId,
      };
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [workspace.ticker, workspace.trade_date, payload]);

  const groups = useMemo(() => filterTradeGroups(payload, filters), [payload, filters]);
  const summary = useMemo(() => summarizeTradeGroups(groups), [groups]);

  // Canonical registry metadata form (admin only).
  useEffect(() => {
    if (!isAdmin) return undefined;
    let cancelled = false;
    Api.adminTraders()
      .then((doc) => {
        if (cancelled) return;
        setRegistryDoc(doc);
        setRegistryDraft(structuredClone(doc));
      })
      .catch(() => {});
    return () => { cancelled = true; };
  }, [isAdmin]);

  const registryDirty = Boolean(
    registryDoc && registryDraft && JSON.stringify(registryDoc) !== JSON.stringify(registryDraft),
  );

  function handleSwitchTicker(ticker) {
    const current = findDay(workspaceDays, { ticker: workspace.ticker, tradeDate: workspace.trade_date });
    const next = switchTicker(workspaceDays, { day: current }, ticker);
    if (next.day) setWorkspace({ ticker: next.ticker, trade_date: next.trade_date, key: next.key });
  }

  function handleSelectDate(tradeDate) {
    const current = findDay(workspaceDays, { ticker: workspace.ticker, tradeDate: workspace.trade_date });
    const next = selectWorkspaceDay(workspaceDays, { day: current }, { ticker: workspace.ticker, tradeDate });
    if (next.day) setWorkspace({ ticker: next.ticker, trade_date: next.trade_date, key: next.key });
  }

  function updateRegistryTrader(traderId, patch) {
    setRegistryDraft((previous) => ({
      ...previous,
      traders: previous.traders.map((trader) => (
        trader.trader_id === traderId ? { ...trader, ...patch } : trader
      )),
    }));
  }

  async function saveRegistry() {
    if (!isAdmin || !registryDirty) return;
    setRegistryState({ saving: true, error: '', success: '' });
    try {
      await onSaveRegistry(registryDraft);
      const reloaded = await Api.adminTraders();
      setRegistryDoc(reloaded);
      setRegistryDraft(structuredClone(reloaded));
      setRegistryState({ saving: false, error: '', success: '注册表已保存。' });
    } catch (err) {
      setRegistryState({ saving: false, error: err.message, success: '' });
    }
  }

  return (
    <div className="admin-traders-page">
      <header>
        <div>
          <h2>交易记录 / 点位管理</h2>
          <p>
            {isAdmin
              ? '管理员：通过表单新增/编辑点位并保存；保存走服务端 schema 校验与原子替换。'
              : '只读：可检查与导出交易记录；新增/编辑点位需要管理员权限。'}
          </p>
        </div>
        <TradeExportControls payload={payload} groups={groups} filters={filters} />
      </header>
      <ReviewContextPanel
        days={workspaceDays}
        workspace={workspace}
        onSwitchTicker={handleSwitchTicker}
        onSelectDate={handleSelectDate}
      />
      <TraderFilters
        traders={traders}
        value={filters}
        onChange={setFilters}
        context={{ ticker: workspace.ticker, tradeDate: workspace.trade_date }}
        availableTraderIds={traderAvailability.availableTraderIds}
      />
      <div className="trade-stat-grid">
        <span>Groups <strong>{summary.group_count}</strong></span>
        <span>Reported win rate <strong>{summary.reported.win_rate == null ? '--' : `${(summary.reported.win_rate * 100).toFixed(1)}%`}</strong></span>
        <span>Calculated win rate <strong>{summary.calculated.win_rate == null ? '--' : `${(summary.calculated.win_rate * 100).toFixed(1)}%`}</strong></span>
      </div>
      <TraderTradeList groups={groups} traders={traders} />
      {isAdmin && (
        <TraderPointEditor role={role} marketDays={marketDays} onSaveDay={onSaveDay} />
      )}
      {isAdmin && registryDraft && (
        <section className="tp-registry" aria-label="交易者注册表">
          <h3>交易者注册表（trader_id 不可变）</h3>
          {registryDraft.traders.map((trader) => (
            <div className="tp-form-grid" key={trader.trader_id}>
              <span className="tp-field tp-readonly">{trader.trader_id}</span>
              <label className="tp-field">
                Display name
                <input value={trader.display_name} onChange={(event) => updateRegistryTrader(trader.trader_id, { display_name: event.target.value })} />
              </label>
              <label className="tp-field">
                Color
                <input value={trader.color} onChange={(event) => updateRegistryTrader(trader.trader_id, { color: event.target.value })} placeholder="#4E79A7" />
              </label>
              <label className="tp-field tp-inline">
                <input type="checkbox" checked={Boolean(trader.active)} onChange={(event) => updateRegistryTrader(trader.trader_id, { active: event.target.checked })} /> active
              </label>
              <label className="tp-field">
                Sort order
                <input value={trader.sort_order} onChange={(event) => updateRegistryTrader(trader.trader_id, { sort_order: Number(event.target.value) || 0 })} />
              </label>
            </div>
          ))}
          <div className="tp-save-row">
            <button type="button" disabled={!registryDirty || registryState.saving} onClick={saveRegistry}>
              {registryState.saving ? '保存中…' : '保存注册表'}
            </button>
            {registryState.error && <span className="tp-error" role="alert">{registryState.error}</span>}
            {registryState.success && <span className="tp-success" role="status">{registryState.success}</span>}
          </div>
        </section>
      )}
    </div>
  );
}
