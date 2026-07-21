import { useEffect, useMemo, useRef, useState } from 'react';
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
import {
  appendTraderDraft,
  associateRegistryServerError,
  createTraderDraft,
  removeUnsavedTrader,
} from '../features/review/traderRegistry.js';

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
  const [createDraft, setCreateDraft] = useState(null);
  const [createErrors, setCreateErrors] = useState({});
  const [stagedTraderIndex, setStagedTraderIndex] = useState(null);
  const [registryFieldErrors, setRegistryFieldErrors] = useState({});
  const registryControlRefs = useRef(new Map());

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
        availableTraderIds: traderAvailability.availableTraderIds,
        contextChanged: true,
      });
      return {
        ...initialTradeRecordFilters(traders),
        ticker: workspace.ticker,
        tradeDate: workspace.trade_date,
        traderIds: reconciled.selectedTraderIds,
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

  function updateRegistryTrader(index, field, value) {
    setRegistryDraft((previous) => ({
      ...previous,
      traders: previous.traders.map((trader, traderIndex) => (
        traderIndex === index ? { ...trader, [field]: value } : trader
      )),
    }));
    setRegistryFieldErrors((previous) => {
      const next = { ...previous };
      delete next[`${index}.${field}`];
      return next;
    });
    setRegistryState((previous) => ({ ...previous, error: '', success: '' }));
  }

  function setRegistryControlRef(index, field, node) {
    const key = `${index}.${field}`;
    if (node) registryControlRefs.current.set(key, node);
    else registryControlRefs.current.delete(key);
  }

  function focusRegistryControl(fieldPath) {
    window.requestAnimationFrame(() => registryControlRefs.current.get(fieldPath)?.focus());
  }

  function openCreateTrader() {
    setCreateDraft(createTraderDraft(registryDraft));
    setCreateErrors({});
    setRegistryState({ saving: false, error: '', success: '' });
  }

  function updateCreateTrader(field, value) {
    setCreateDraft((previous) => ({ ...previous, [field]: value }));
    setCreateErrors((previous) => {
      const next = { ...previous };
      delete next[field];
      return next;
    });
  }

  function addCreateTraderToDraft() {
    const result = appendTraderDraft(registryDraft, createDraft);
    if (Object.keys(result.fieldErrors).length) {
      setCreateErrors(result.fieldErrors);
      const firstField = Object.keys(result.fieldErrors)[0];
      window.requestAnimationFrame(() => document.getElementById(`create-trader-${firstField}`)?.focus());
      return;
    }
    const nextIndex = result.registry.traders.length - 1;
    setRegistryDraft(result.registry);
    setStagedTraderIndex(nextIndex);
    setCreateDraft(null);
    setCreateErrors({});
    setRegistryState({ saving: false, error: '', success: '已添加到完整注册表草稿，尚未保存。' });
  }

  function removeStagedTrader() {
    if (stagedTraderIndex == null) return;
    setRegistryDraft((previous) => removeUnsavedTrader(previous, stagedTraderIndex));
    setStagedTraderIndex(null);
    setRegistryFieldErrors({});
    setRegistryState({ saving: false, error: '', success: '未保存的交易者已移除。' });
  }

  async function saveRegistry() {
    if (!isAdmin || !registryDirty) return;
    let candidate = registryDraft;
    if (stagedTraderIndex != null) {
      const base = removeUnsavedTrader(registryDraft, stagedTraderIndex);
      const appended = appendTraderDraft(base, registryDraft.traders[stagedTraderIndex]);
      if (Object.keys(appended.fieldErrors).length) {
        const mapped = Object.fromEntries(
          Object.entries(appended.fieldErrors).map(([field, message]) => [`${stagedTraderIndex}.${field}`, message]),
        );
        setRegistryFieldErrors(mapped);
        setRegistryState({ saving: false, error: '请先修正新增交易者字段。', success: '' });
        const firstField = Object.keys(appended.fieldErrors)[0];
        focusRegistryControl(`${stagedTraderIndex}.${firstField}`);
        return;
      }
      candidate = appended.registry;
    }
    setRegistryState({ saving: true, error: '', success: '' });
    setRegistryFieldErrors({});
    try {
      await onSaveRegistry(candidate);
      const reloaded = await Api.adminTraders();
      setRegistryDoc(reloaded);
      setRegistryDraft(structuredClone(reloaded));
      setCreateDraft(null);
      setCreateErrors({});
      setStagedTraderIndex(null);
      setRegistryFieldErrors({});
      setRegistryState({ saving: false, error: '', success: '注册表已保存。' });
    } catch (err) {
      const associated = associateRegistryServerError(err.message, {
        rowCount: registryDraft.traders.length,
        controlPaths: new Set(registryControlRefs.current.keys()),
      });
      if (associated.fieldPath) {
        setRegistryFieldErrors({ [associated.fieldPath]: associated.message });
        focusRegistryControl(associated.fieldPath);
      }
      setRegistryState({ saving: false, error: associated.message, success: '' });
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
        exportControls={<TradeExportControls payload={payload} groups={groups} filters={filters} />}
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
          <div className="tp-registry-header">
            <div>
              <h3>交易者注册表</h3>
              <p>已保存的 trader_id 不可变；新增交易者先加入完整草稿，再统一保存。</p>
            </div>
            <button
              className="tp-add-trader-button"
              type="button"
              aria-expanded={Boolean(createDraft)}
              disabled={Boolean(createDraft) || stagedTraderIndex != null || registryState.saving}
              onClick={openCreateTrader}
            >
              新增交易者
            </button>
          </div>

          {createDraft && (
            <div className="tp-create-card" aria-label="新增交易者草稿">
              <div className="tp-create-card-header">
                <strong>新增交易者</strong>
                <span className="tp-unsaved-badge">未加入草稿</span>
              </div>
              <div className="tp-form-grid">
                <label className="tp-field">
                  trader_id
                  <input
                    id="create-trader-trader_id"
                    value={createDraft.trader_id}
                    onChange={(event) => updateCreateTrader('trader_id', event.target.value)}
                    aria-invalid={Boolean(createErrors.trader_id)}
                    aria-describedby={createErrors.trader_id ? 'create-error-trader_id' : undefined}
                    autoFocus
                  />
                  {createErrors.trader_id && <span id="create-error-trader_id" className="tp-error" role="alert">{createErrors.trader_id}</span>}
                </label>
                <label className="tp-field">
                  Display name
                  <input
                    id="create-trader-display_name"
                    value={createDraft.display_name}
                    onChange={(event) => updateCreateTrader('display_name', event.target.value)}
                    aria-invalid={Boolean(createErrors.display_name)}
                    aria-describedby={createErrors.display_name ? 'create-error-display_name' : undefined}
                  />
                  {createErrors.display_name && <span id="create-error-display_name" className="tp-error" role="alert">{createErrors.display_name}</span>}
                </label>
                <label className="tp-field">
                  Color
                  <input
                    id="create-trader-color"
                    value={createDraft.color}
                    onChange={(event) => updateCreateTrader('color', event.target.value)}
                    placeholder="#3366CC"
                    aria-invalid={Boolean(createErrors.color)}
                    aria-describedby={createErrors.color ? 'create-error-color' : undefined}
                  />
                  {createErrors.color && <span id="create-error-color" className="tp-error" role="alert">{createErrors.color}</span>}
                </label>
                <label className="tp-field tp-inline">
                  <input
                    id="create-trader-active"
                    type="checkbox"
                    checked={Boolean(createDraft.active)}
                    onChange={(event) => updateCreateTrader('active', event.target.checked)}
                  /> active
                </label>
                <label className="tp-field">
                  Sort order
                  <input
                    id="create-trader-sort_order"
                    inputMode="numeric"
                    value={createDraft.sort_order}
                    onChange={(event) => updateCreateTrader('sort_order', event.target.value)}
                    aria-invalid={Boolean(createErrors.sort_order)}
                    aria-describedby={createErrors.sort_order ? 'create-error-sort_order' : undefined}
                  />
                  {createErrors.sort_order && <span id="create-error-sort_order" className="tp-error" role="alert">{createErrors.sort_order}</span>}
                </label>
              </div>
              <div className="tp-create-actions">
                <button type="button" onClick={addCreateTraderToDraft}>添加到草稿</button>
                <button type="button" className="tp-button-muted" onClick={() => { setCreateDraft(null); setCreateErrors({}); }}>取消</button>
              </div>
            </div>
          )}

          {registryDraft.traders.map((trader, index) => {
            const isUnsaved = index === stagedTraderIndex;
            const errorId = (field) => `registry-error-${index}-${field}`;
            return (
            <div className={`tp-form-grid tp-registry-row ${isUnsaved ? 'is-unsaved' : ''}`} key={`registry-row-${index}`}>
              {isUnsaved ? (
                <label className="tp-field">
                  trader_id
                  <input
                    ref={(node) => setRegistryControlRef(index, 'trader_id', node)}
                    value={trader.trader_id}
                    onChange={(event) => updateRegistryTrader(index, 'trader_id', event.target.value)}
                    aria-invalid={Boolean(registryFieldErrors[`${index}.trader_id`])}
                    aria-describedby={registryFieldErrors[`${index}.trader_id`] ? errorId('trader_id') : undefined}
                  />
                  {registryFieldErrors[`${index}.trader_id`] && <span id={errorId('trader_id')} className="tp-error" role="alert">{registryFieldErrors[`${index}.trader_id`]}</span>}
                </label>
              ) : <span className="tp-field tp-readonly">{trader.trader_id}</span>}
              <label className="tp-field">
                Display name
                <input
                  ref={(node) => setRegistryControlRef(index, 'display_name', node)}
                  value={trader.display_name}
                  onChange={(event) => updateRegistryTrader(index, 'display_name', event.target.value)}
                  aria-invalid={Boolean(registryFieldErrors[`${index}.display_name`])}
                  aria-describedby={registryFieldErrors[`${index}.display_name`] ? errorId('display_name') : undefined}
                />
                {registryFieldErrors[`${index}.display_name`] && <span id={errorId('display_name')} className="tp-error" role="alert">{registryFieldErrors[`${index}.display_name`]}</span>}
              </label>
              <label className="tp-field">
                Color
                <input
                  ref={(node) => setRegistryControlRef(index, 'color', node)}
                  value={trader.color}
                  onChange={(event) => updateRegistryTrader(index, 'color', event.target.value)}
                  placeholder="#4E79A7"
                  aria-invalid={Boolean(registryFieldErrors[`${index}.color`])}
                  aria-describedby={registryFieldErrors[`${index}.color`] ? errorId('color') : undefined}
                />
                {registryFieldErrors[`${index}.color`] && <span id={errorId('color')} className="tp-error" role="alert">{registryFieldErrors[`${index}.color`]}</span>}
              </label>
              <label className="tp-field tp-inline">
                <input
                  ref={(node) => setRegistryControlRef(index, 'active', node)}
                  type="checkbox"
                  checked={Boolean(trader.active)}
                  onChange={(event) => updateRegistryTrader(index, 'active', event.target.checked)}
                  aria-invalid={Boolean(registryFieldErrors[`${index}.active`])}
                  aria-describedby={registryFieldErrors[`${index}.active`] ? errorId('active') : undefined}
                /> active
                {registryFieldErrors[`${index}.active`] && <span id={errorId('active')} className="tp-error" role="alert">{registryFieldErrors[`${index}.active`]}</span>}
              </label>
              <label className="tp-field">
                Sort order
                <input
                  ref={(node) => setRegistryControlRef(index, 'sort_order', node)}
                  inputMode="numeric"
                  value={trader.sort_order}
                  onChange={(event) => updateRegistryTrader(index, 'sort_order', isUnsaved ? event.target.value : Number(event.target.value) || 0)}
                  aria-invalid={Boolean(registryFieldErrors[`${index}.sort_order`])}
                  aria-describedby={registryFieldErrors[`${index}.sort_order`] ? errorId('sort_order') : undefined}
                />
                {registryFieldErrors[`${index}.sort_order`] && <span id={errorId('sort_order')} className="tp-error" role="alert">{registryFieldErrors[`${index}.sort_order`]}</span>}
              </label>
              {isUnsaved && (
                <div className="tp-unsaved-actions">
                  <span className="tp-unsaved-badge">未保存</span>
                  <button type="button" className="tp-button-muted" onClick={removeStagedTrader}>移除未保存项</button>
                </div>
              )}
            </div>
            );
          })}
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
