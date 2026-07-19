import { useEffect, useMemo, useState } from 'react';
import { Api } from '../../api/client.js';
import { ReviewContextPanel } from './ReviewContextPanel.jsx';
import { UnifiedKlineEngine } from '../../kline/UnifiedKlineEngine.jsx';
import { DAILY_REVIEW_ENGINE_OPTIONS } from './engineOptions.js';
import {
  findDay,
  normalizeInteractiveDays,
  resolveInitialWorkspace,
  selectWorkspaceDay,
  switchTicker,
} from './reviewWorkspace.js';
import { buildTradeRecordAnnotations } from './tradeRecords.js';
import {
  EDITOR_CONSTANTS,
  applyOccurredAt,
  buildNewEvent,
  buildNewGroup,
  mergeGroupIntoDay,
  preservationDiff,
  validateGroupForm,
} from './tradeCandidate.js';

// Admin-only trader point editor (plan §3.4). The canonical write base is the
// admin-only full registry/day read — never the public projection. Saving goes
// exclusively through the existing admin PUT of the complete merged day.
export function TraderPointEditor({ role, marketDays = [], onSaveDay, onSaved }) {
  const isAdmin = role === 'admin';
  const workspaceDays = useMemo(() => normalizeInteractiveDays(marketDays), [marketDays]);
  const [workspace, setWorkspace] = useState(() => {
    const resolved = resolveInitialWorkspace({ days: normalizeInteractiveDays(marketDays) });
    return { ticker: resolved.ticker, trade_date: resolved.trade_date, key: resolved.key };
  });
  const [registry, setRegistry] = useState(null);
  const [registryError, setRegistryError] = useState('');
  const [dayState, setDayState] = useState('idle'); // idle|loading|loaded|missing|error|new
  const [dayDoc, setDayDoc] = useState(null);
  const [dayError, setDayError] = useState('');
  const [traderId, setTraderId] = useState('');
  const [selection, setSelection] = useState('new');
  const [form, setForm] = useState(null);
  const [bars, setBars] = useState({ bars1m: [], bars5m: [] });
  const [saveState, setSaveState] = useState({ saving: false, error: '', success: '' });

  // Canonical admin-only registry load.
  useEffect(() => {
    if (!isAdmin) return undefined;
    let cancelled = false;
    Api.adminTraders()
      .then((doc) => {
        if (cancelled) return;
        setRegistry(doc);
        setTraderId((previous) => previous || doc.traders?.[0]?.trader_id || '');
      })
      .catch((err) => { if (!cancelled) setRegistryError(err.message); });
    return () => { cancelled = true; };
  }, [isAdmin]);

  // Canonical admin-only day load for the resolved context.
  useEffect(() => {
    if (!isAdmin || !workspace.trade_date) return undefined;
    let cancelled = false;
    setDayState('loading');
    setDayError('');
    setForm(null);
    setSaveState({ saving: false, error: '', success: '' });
    Api.adminTradeDay(workspace.trade_date)
      .then((doc) => {
        if (cancelled) return;
        setDayDoc(doc);
        setDayState('loaded');
      })
      .catch((err) => {
        if (cancelled) return;
        setDayDoc(null);
        if (err.status === 404 || /not found/i.test(String(err.message))) setDayState('missing');
        else {
          setDayState('error');
          setDayError(err.message);
        }
      });
    return () => { cancelled = true; };
  }, [isAdmin, workspace.trade_date]);

  const contextGroups = useMemo(() => (
    (dayDoc?.trade_groups || []).filter(
      (group) => group.underlying === workspace.ticker && group.trader_id === traderId,
    )
  ), [dayDoc, workspace.ticker, traderId]);

  // Re-select the form target whenever the context group list changes. A
  // new-group form is rebuilt when the context (ticker/date/trader) no longer
  // matches it, and preserved while it is being edited in the same context.
  useEffect(() => {
    if ((dayState !== 'loaded' && dayState !== 'new') || !dayDoc) return;
    if (selection !== 'new' && !contextGroups.some((group) => group.trade_group_id === selection)) {
      setSelection(contextGroups[0]?.trade_group_id || 'new');
      return;
    }
    if (selection === 'new') {
      const isCurrentContextNewForm = form?.__isNew
        && form.trade_date === workspace.trade_date
        && form.trader_id === traderId
        && form.underlying === workspace.ticker;
      if (!isCurrentContextNewForm) {
        setForm({
          ...buildNewGroup(dayDoc, { tradeDate: workspace.trade_date, traderId, underlying: workspace.ticker }),
          __isNew: true,
        });
      }
      return;
    }
    const source = contextGroups.find((group) => group.trade_group_id === selection);
    if (source) setForm(structuredClone(source));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dayState, dayDoc, contextGroups, selection, workspace.trade_date, workspace.ticker, traderId]);

  const formErrors = useMemo(() => (form ? validateGroupForm(form) : {}), [form]);
  const candidate = useMemo(
    () => (form && dayDoc ? mergeGroupIntoDay(dayDoc, stripMeta(form)) : null),
    [form, dayDoc],
  );
  const diff = useMemo(
    () => (candidate && dayDoc && form
      ? preservationDiff(dayDoc, candidate, { targetGroupId: stripMeta(form).trade_group_id })
      : null),
    [candidate, dayDoc, form],
  );

  const marketDay = useMemo(
    () => findDay(workspaceDays, { ticker: workspace.ticker, tradeDate: workspace.trade_date }),
    [workspaceDays, workspace],
  );

  // Preview bars for the resolved market day (one read-only reused engine).
  useEffect(() => {
    if (!marketDay?.ref?.id) { setBars({ bars1m: [], bars5m: [] }); return undefined; }
    let cancelled = false;
    Promise.all([Api.bars(marketDay.ref.id, '1m'), Api.bars(marketDay.ref.id, '5m')])
      .then(([one, five]) => { if (!cancelled) setBars({ bars1m: one.bars || [], bars5m: five.bars || [] }); })
      .catch(() => { if (!cancelled) setBars({ bars1m: [], bars5m: [] }); });
    return () => { cancelled = true; };
  }, [marketDay?.ref?.id]);

  const previewPayload = useMemo(() => {
    if (!form || !bars.bars1m.length) return null;
    const markers = buildTradeRecordAnnotations([stripMeta(form)], registry?.traders || [], bars.bars1m);
    return {
      meta: {
        ticker: workspace.ticker,
        date: workspace.trade_date,
        title: `${workspace.ticker} ${workspace.trade_date} 候选预览`,
        initial_timeframe: '1m',
      },
      bars_1m: bars.bars1m,
      bars_5m: bars.bars5m,
      annotations_1m: markers,
      annotations_5m: [],
    };
  }, [form, bars, registry, workspace]);

  if (!isAdmin) return null;

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

  function createDayDocument() {
    setDayDoc({
      schema_version: 'trades-day-v1',
      trade_date: workspace.trade_date,
      timezone: 'America/New_York',
      trade_groups: [],
      note_contexts: [],
    });
    setDayState('new');
  }

  function updateForm(patch) {
    setForm((previous) => ({ ...previous, ...patch }));
  }

  function updateLeg(patch) {
    setForm((previous) => ({ ...previous, legs: [{ ...previous.legs[0], ...patch }] }));
  }

  function updateEvent(index, patch) {
    setForm((previous) => ({
      ...previous,
      legs: [{
        ...previous.legs[0],
        events: previous.legs[0].events.map((event, i) => (i === index ? { ...event, ...patch } : event)),
      }],
    }));
  }

  function addEvent() {
    setForm((previous) => {
      const events = previous.legs[0].events;
      const nextSequence = events.length + 1;
      return {
        ...previous,
        legs: [{
          ...previous.legs[0],
          events: [...events, buildNewEvent(`${previous.legs[0].leg_id}_e${nextSequence}`, nextSequence)],
        }],
      };
    });
  }

  function removeEvent(index) {
    setForm((previous) => {
      const events = previous.legs[0].events
        .filter((_, i) => i !== index)
        .map((event, i) => ({ ...event, sequence: i + 1 }));
      return { ...previous, legs: [{ ...previous.legs[0], events }] };
    });
  }

  const errorCount = Object.keys(formErrors).length;
  const canSave = Boolean(
    isAdmin && form && candidate && dayDoc
    && errorCount === 0 && diff?.ok && !saveState.saving,
  );

  async function save() {
    if (!canSave) return;
    const summary = [
      `保存完整日文档 ${workspace.trade_date}？`,
      `目标 group: ${stripMeta(form).trade_group_id}`,
      diff.addedGroupIds.length ? `新增 1 个 group；` : '编辑 1 个 group；',
      `未触碰 ${diff.untouchedGroupIds.length} 个既有 group / ${dayDoc.note_contexts.length} 个 note context。`,
    ].join('\n');
    if (!window.confirm(summary)) return;
    setSaveState({ saving: true, error: '', success: '' });
    try {
      await onSaveDay(candidate);
      setSaveState({ saving: false, error: '', success: '已保存，服务端校验与投影完成。' });
      onSaved?.();
      const reloaded = await Api.adminTradeDay(workspace.trade_date);
      setDayDoc(reloaded);
      setDayState('loaded');
    } catch (err) {
      // Unsaved form state is retained; the server message is surfaced and no
      // automatic retry or partial write ever happens.
      setSaveState({ saving: false, error: err.message, success: '' });
    }
  }

  return (
    <section className="tp-editor" aria-label="交易者点位编辑器">
      <h3>交易者点位编辑</h3>
      <ReviewContextPanel
        days={workspaceDays}
        workspace={workspace}
        onSwitchTicker={handleSwitchTicker}
        onSelectDate={handleSelectDate}
      />
      {registryError && <p className="tp-error" role="alert">注册表读取失败：{registryError}</p>}
      {registry && (
        <label className="tp-field">
          Trader
          <select value={traderId} onChange={(event) => { setTraderId(event.target.value); setSelection('new'); setForm(null); }}>
            {registry.traders.map((trader) => (
              <option key={trader.trader_id} value={trader.trader_id}>{trader.display_name}（{trader.trader_id}）</option>
            ))}
          </select>
        </label>
      )}
      {dayState === 'loading' && <p role="status" aria-live="polite">正在读取 canonical 日文档…</p>}
      {dayState === 'error' && <p className="tp-error" role="alert">日文档读取失败：{dayError}</p>}
      {dayState === 'missing' && (
        <div className="tp-missing-day">
          <p>该日期还没有交易记录文档。</p>
          <button type="button" onClick={createDayDocument}>新建该日期文档</button>
        </div>
      )}
      {(dayState === 'loaded' || dayState === 'new') && dayDoc && (
        <>
          <div className="tp-group-picker" role="listbox" aria-label="选择点位">
            {contextGroups.map((group) => (
              <button
                key={group.trade_group_id}
                type="button"
                className={selection === group.trade_group_id ? 'active' : ''}
                onClick={() => setSelection(group.trade_group_id)}
              >
                {group.trade_group_id} · {group.direction} · {group.review_status}
              </button>
            ))}
            <button type="button" className={selection === 'new' ? 'active' : ''} onClick={() => setSelection('new')}>
              新增点位
            </button>
          </div>
          {form && (
            <div className="tp-form">
              <div className="tp-form-grid">
                <label className="tp-field">
                  Direction
                  <select
                    value={form.direction}
                    onChange={(event) => setForm((previous) => ({
                      ...previous,
                      direction: event.target.value,
                      legs: [{ ...previous.legs[0], option_type: event.target.value }],
                    }))}
                  >
                    {EDITOR_CONSTANTS.DIRECTIONS.map((value) => <option key={value}>{value}</option>)}
                  </select>
                </label>
                <label className="tp-field">
                  Status
                  <select value={form.status} onChange={(event) => updateForm({ status: event.target.value })}>
                    {EDITOR_CONSTANTS.RECORD_STATUSES.map((value) => <option key={value}>{value}</option>)}
                  </select>
                </label>
                <label className="tp-field">
                  Review
                  <select value={form.review_status} onChange={(event) => updateForm({ review_status: event.target.value })}>
                    {EDITOR_CONSTANTS.REVIEW_STATUSES.map((value) => <option key={value}>{value}</option>)}
                  </select>
                </label>
                <fieldset className="tp-field tp-eligibility">
                  <legend>Eligibility</legend>
                  <label><input type="checkbox" checked={form.display_eligible} onChange={(event) => updateForm({ display_eligible: event.target.checked })} /> Display</label>
                  <label><input type="checkbox" checked={form.reported_stats_eligible} onChange={(event) => updateForm({ reported_stats_eligible: event.target.checked })} /> Reported</label>
                  <label><input type="checkbox" checked={form.calculated_stats_eligible} onChange={(event) => updateForm({ calculated_stats_eligible: event.target.checked })} /> Calculated</label>
                </fieldset>
                <label className="tp-field">
                  Strike（空 = null）
                  <input
                    value={form.legs[0].strike ?? ''}
                    onChange={(event) => updateLeg({ strike: parseNumberOrNull(event.target.value) })}
                    placeholder="例如 681"
                  />
                </label>
                <label className="tp-field">
                  Expiry
                  <input value={form.legs[0].expiry || ''} onChange={(event) => updateLeg({ expiry: event.target.value })} placeholder="YYYY-MM-DD" />
                </label>
                <label className="tp-field">
                  Multiplier
                  <input value={form.legs[0].contract_multiplier ?? ''} onChange={(event) => updateLeg({ contract_multiplier: parseNumberOrNull(event.target.value) })} />
                </label>
              </div>
              <label className="tp-field">
                Notes（每行一条，provenance 记为 user_provided）
                <textarea
                  rows={2}
                  value={(form.notes || []).map((note) => note.text).join('\n')}
                  onChange={(event) => updateForm({
                    notes: event.target.value.split('\n').filter((line) => line.trim()).map((text) => ({ text, provenance: 'user_provided' })),
                  })}
                />
              </label>
              <div className="tp-events">
                <div className="tp-events-header">
                  <strong>Events</strong>
                  <button type="button" onClick={addEvent}>新增事件</button>
                </div>
                {form.legs[0].events.map((event, index) => (
                  <fieldset className="tp-event" key={event.event_id || index}>
                    <legend>#{event.sequence} {event.event_id}</legend>
                    <div className="tp-form-grid">
                      <label className="tp-field">
                        Action
                        <select value={event.action} onChange={(e) => updateEvent(index, { action: e.target.value })}>
                          {EDITOR_CONSTANTS.EVENT_ACTIONS.map((value) => <option key={value}>{value}</option>)}
                        </select>
                      </label>
                      <label className="tp-field">
                        Occurred at（ISO 带时区，空 = null）
                        <input
                          value={event.occurred_at ?? ''}
                          placeholder="2026-07-17T09:42-04:00"
                          onChange={(e) => updateEvent(index, applyOccurredAt(event, e.target.value))}
                        />
                      </label>
                      <label className="tp-field">
                        Precision
                        <select
                          value={event.time_precision ?? ''}
                          onChange={(e) => updateEvent(index, { time_precision: e.target.value || null })}
                        >
                          <option value="">（null）</option>
                          {EDITOR_CONSTANTS.TIME_PRECISIONS.map((value) => <option key={value}>{value}</option>)}
                        </select>
                      </label>
                      <label className="tp-field tp-inline">
                        <input type="checkbox" checked={Boolean(event.time_incomplete)} onChange={(e) => updateEvent(index, { time_incomplete: e.target.checked })} /> time_incomplete
                      </label>
                      {['premium', 'quantity', 'fees'].map((field) => (
                        <label className="tp-field" key={field}>
                          {field}
                          <input
                            value={event[field] ?? ''}
                            onChange={(e) => updateEvent(index, { [field]: parseNumberOrNull(e.target.value) })}
                          />
                        </label>
                      ))}
                      <label className="tp-field">
                        Note
                        <input value={event.note ?? ''} onChange={(e) => updateEvent(index, { note: e.target.value || null })} />
                      </label>
                      {['occurred_at', 'premium', 'quantity', 'fees'].map((fact) => (
                        <label className="tp-field" key={fact}>
                          provenance: {fact}
                          <select
                            value={event.fact_provenance?.[fact] || 'unknown'}
                            onChange={(e) => updateEvent(index, { fact_provenance: { ...event.fact_provenance, [fact]: e.target.value } })}
                          >
                            {EDITOR_CONSTANTS.FACT_PROVENANCE.map((value) => <option key={value}>{value}</option>)}
                          </select>
                        </label>
                      ))}
                    </div>
                    {form.legs[0].events.length > 1 && (
                      <button type="button" onClick={() => removeEvent(index)}>删除该事件</button>
                    )}
                  </fieldset>
                ))}
              </div>
              <details className="tp-normalization">
                <summary>Normalization（高级）</summary>
                <div className="tp-form-grid">
                  <label className="tp-field">
                    Method
                    <select value={form.normalization.method} onChange={(event) => updateForm({ normalization: { ...form.normalization, method: event.target.value } })}>
                      {EDITOR_CONSTANTS.NORMALIZATION_METHODS.map((value) => <option key={value}>{value}</option>)}
                    </select>
                  </label>
                  <label className="tp-field">
                    Source
                    <input value={form.normalization.source || ''} onChange={(event) => updateForm({ normalization: { ...form.normalization, source: event.target.value } })} />
                  </label>
                  <label className="tp-field">
                    Review flags（逗号分隔）
                    <input
                      value={(form.normalization.review_flags || []).join(',')}
                      onChange={(event) => updateForm({
                        normalization: {
                          ...form.normalization,
                          review_flags: event.target.value.split(',').map((flag) => flag.trim()).filter(Boolean),
                        },
                      })}
                    />
                  </label>
                </div>
              </details>
              {errorCount > 0 && (
                <ul className="tp-error" role="alert">
                  {Object.entries(formErrors).map(([path, message]) => <li key={path}><code>{path}</code>: {message}</li>)}
                </ul>
              )}
              {diff && (
                <p className={`tp-diff-badge ${diff.ok ? 'ok' : 'fail'}`}>
                  {diff.ok
                    ? `保留检查通过：未触碰 ${diff.untouchedGroupIds.length} 个 group，count delta ${diff.countDelta}`
                    : `保留检查失败：${diff.problems.join('；')}`}
                </p>
              )}
              <div className="tp-save-row">
                <button type="button" disabled={!canSave} onClick={save}>
                  {saveState.saving ? '保存中…' : '保存该日文档'}
                </button>
                {saveState.error && <span className="tp-error" role="alert">{saveState.error}</span>}
                {saveState.success && <span className="tp-success" role="status">{saveState.success}</span>}
              </div>
            </div>
          )}
          <div className="tp-preview">
            <h4>候选预览（只读图表，不会保存）</h4>
            {previewPayload ? (
              <UnifiedKlineEngine
                payload={previewPayload}
                annotations1m={previewPayload.annotations_1m}
                annotations5m={[]}
                engineOptions={DAILY_REVIEW_ENGINE_OPTIONS}
              />
            ) : (
              <p>选择或新增点位后在此预览图表标记。</p>
            )}
          </div>
        </>
      )}
    </section>
  );
}

function stripMeta(form) {
  const { __isNew, ...rest } = form;
  return rest;
}

function parseNumberOrNull(value) {
  const text = String(value).trim();
  if (!text) return null;
  const number = Number(text);
  return Number.isFinite(number) ? number : null;
}
