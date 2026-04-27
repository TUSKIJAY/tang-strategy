/**
 * KlineDevPanel — 可拆卸的开发者工具面板
 *
 * 用法：
 *   <script src="kline-devpanel.js"></script>
 *   const panel = new KlineDevPanel(engine);  // engine = KlineEngine 实例
 *   // panel.destroy() 可随时移除
 *
 * 设计原则：
 *   - 只通过 KlineEngine 公共 API + EventBus 通信
 *   - 不依赖引擎内部实现细节
 *   - 产品页面不引入此脚本即可完全隔离
 */
(function () {
  'use strict';

  const PANEL_CSS = `
    .kline-devpanel {
      position: fixed;
      bottom: 16px;
      right: 16px;
      z-index: 9999;
      width: 320px;
      max-height: 460px;
      overflow-y: auto;
      background: rgba(18, 18, 18, 0.95);
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: 12px;
      backdrop-filter: blur(14px);
      box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
      font-family: 'JetBrains Mono', 'Consolas', monospace;
      font-size: 11px;
      color: rgba(255, 255, 255, 0.8);
      user-select: none;
    }

    .kline-devpanel__header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 8px 12px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
      cursor: move;
    }

    .kline-devpanel__title {
      font-weight: 600;
      font-size: 11px;
      color: rgba(255, 255, 255, 0.6);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .kline-devpanel__close {
      background: none;
      border: none;
      color: rgba(255, 255, 255, 0.4);
      cursor: pointer;
      font-size: 14px;
      padding: 0 4px;
      line-height: 1;
    }
    .kline-devpanel__close:hover {
      color: rgba(255, 255, 255, 0.8);
    }

    .kline-devpanel__section {
      padding: 8px 12px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    }

    .kline-devpanel__section-title {
      font-size: 10px;
      color: rgba(255, 255, 255, 0.4);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 6px;
    }

    .kline-devpanel__row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 2px 0;
    }

    .kline-devpanel__label {
      color: rgba(255, 255, 255, 0.5);
    }

    .kline-devpanel__value {
      color: #00b894;
      font-variant-numeric: tabular-nums;
    }

    .kline-devpanel__shortcuts {
      display: grid;
      grid-template-columns: auto 1fr;
      gap: 2px 12px;
      font-size: 10px;
    }

    .kline-devpanel__key {
      color: #e6a23c;
      text-align: right;
    }

    .kline-devpanel__desc {
      color: rgba(255, 255, 255, 0.45);
    }

    .kline-devpanel__drop-zone {
      margin: 4px 0;
      padding: 16px 8px;
      border: 2px dashed rgba(255, 255, 255, 0.15);
      border-radius: 8px;
      text-align: center;
      color: rgba(255, 255, 255, 0.35);
      font-size: 11px;
      transition: border-color 0.15s, color 0.15s;
    }

    .kline-devpanel__drop-zone.drag-over {
      border-color: #00b894;
      color: #00b894;
    }

    .kline-devpanel__drop-zone input[type="file"] {
      display: none;
    }

    .kline-devpanel__status-msg {
      margin-top: 4px;
      font-size: 10px;
      color: rgba(255, 255, 255, 0.4);
      min-height: 14px;
    }

    .kline-devpanel__status-msg.error {
      color: #e74c3c;
    }

    .kline-devpanel__status-msg.success {
      color: #00b894;
    }

    .kline-devpanel__btn-row {
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
    }

    .kline-devpanel__fixture-btn {
      padding: 4px 10px;
      border-radius: 6px;
      border: 1px solid rgba(255, 255, 255, 0.12);
      background: rgba(255, 255, 255, 0.06);
      color: rgba(255, 255, 255, 0.7);
      font-family: inherit;
      font-size: 11px;
      cursor: pointer;
      transition: background 0.15s, border-color 0.15s;
    }
    .kline-devpanel__fixture-btn:hover {
      background: rgba(255, 255, 255, 0.12);
      border-color: rgba(255, 255, 255, 0.2);
    }
    .kline-devpanel__fixture-btn.is-active {
      background: rgba(0, 184, 148, 0.2);
      border-color: #00b894;
      color: #00b894;
    }
  `;

  class KlineDevPanel {
    constructor(engine) {
      if (!engine) throw new Error('KlineDevPanel requires a KlineEngine instance.');
      this.engine = engine;
      this._destroyed = false;
      this._unsubs = [];

      this._injectCSS();
      this._buildDOM();
      this._bindEvents();
      this._updateState();
    }

    // ── CSS injection ──────────────────────────────────

    _injectCSS() {
      if (document.querySelector('[data-kline-devpanel-css]')) return;
      this._styleEl = document.createElement('style');
      this._styleEl.setAttribute('data-kline-devpanel-css', '');
      this._styleEl.textContent = PANEL_CSS;
      document.head.appendChild(this._styleEl);
    }

    // ── DOM ─────────────────────────────────────────────

    _buildDOM() {
      this.el = document.createElement('div');
      this.el.className = 'kline-devpanel';
      this.el.innerHTML = `
        <div class="kline-devpanel__header">
          <span class="kline-devpanel__title">Dev Panel</span>
          <button class="kline-devpanel__close" title="Close">&times;</button>
        </div>

        <div class="kline-devpanel__section" data-section="state">
          <div class="kline-devpanel__section-title">Engine State</div>
          <div data-role="state-rows"></div>
        </div>

        <div class="kline-devpanel__section" data-section="fixtures" data-role="fixtures-section" style="display:none">
          <div class="kline-devpanel__section-title">Demo Fixtures</div>
          <div class="kline-devpanel__btn-row" data-role="fixture-buttons"></div>
        </div>

        <div class="kline-devpanel__section" data-section="import">
          <div class="kline-devpanel__section-title">Data Import</div>
          <div class="kline-devpanel__drop-zone" data-role="drop-zone">
            Drop JSON here or click to select
            <input type="file" accept=".json,.csv" data-role="file-input">
          </div>
          <div class="kline-devpanel__status-msg" data-role="import-status"></div>
        </div>

        <div class="kline-devpanel__section" data-section="shortcuts">
          <div class="kline-devpanel__section-title">Keyboard Shortcuts</div>
          <div class="kline-devpanel__shortcuts">
            <span class="kline-devpanel__key">Space</span><span class="kline-devpanel__desc">Play / Pause</span>
            <span class="kline-devpanel__key">&larr; &rarr;</span><span class="kline-devpanel__desc">Step back / forward</span>
            <span class="kline-devpanel__key">1 / 5</span><span class="kline-devpanel__desc">Switch timeframe</span>
          </div>
        </div>
      `;

      document.body.appendChild(this.el);

      this._stateRows = this.el.querySelector('[data-role="state-rows"]');
      this._fixturesSection = this.el.querySelector('[data-role="fixtures-section"]');
      this._fixtureButtons = this.el.querySelector('[data-role="fixture-buttons"]');
      this._dropZone = this.el.querySelector('[data-role="drop-zone"]');
      this._fileInput = this.el.querySelector('[data-role="file-input"]');
      this._importStatus = this.el.querySelector('[data-role="import-status"]');
      this._closeBtn = this.el.querySelector('.kline-devpanel__close');
    }

    // ── Events ──────────────────────────────────────────

    _bindEvents() {
      // Close button
      this._closeBtn.addEventListener('click', () => this.destroy());

      // Engine events → update state display
      const onViewport = () => this._updateState();
      const onTick = () => this._updateState();
      const onData = () => this._updateState();
      this._unsubs.push(this.engine.on('viewport:changed', onViewport));
      this._unsubs.push(this.engine.on('playback:tick', onTick));
      this._unsubs.push(this.engine.on('playback:state', onTick));
      this._unsubs.push(this.engine.on('data:loaded', onData));

      // File drop
      this._dropZone.addEventListener('click', () => this._fileInput.click());
      this._dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        this._dropZone.classList.add('drag-over');
      });
      this._dropZone.addEventListener('dragleave', () => {
        this._dropZone.classList.remove('drag-over');
      });
      this._dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        this._dropZone.classList.remove('drag-over');
        const file = e.dataTransfer?.files?.[0];
        if (file) this._handleFile(file);
      });
      this._fileInput.addEventListener('change', () => {
        const file = this._fileInput.files?.[0];
        if (file) this._handleFile(file);
        this._fileInput.value = '';
      });

      // Fixture buttons — auto-detect from window.__klineEngineV2Fixtures
      this._buildFixtureButtons();

      // Draggable header
      this._bindDrag();
    }

    _bindDrag() {
      const header = this.el.querySelector('.kline-devpanel__header');
      let startX, startY, startLeft, startTop;

      const onMove = (e) => {
        this.el.style.right = 'auto';
        this.el.style.bottom = 'auto';
        this.el.style.left = (startLeft + e.clientX - startX) + 'px';
        this.el.style.top = (startTop + e.clientY - startY) + 'px';
      };
      const onUp = () => {
        document.removeEventListener('mousemove', onMove);
        document.removeEventListener('mouseup', onUp);
      };

      header.addEventListener('mousedown', (e) => {
        startX = e.clientX;
        startY = e.clientY;
        const rect = this.el.getBoundingClientRect();
        startLeft = rect.left;
        startTop = rect.top;
        document.addEventListener('mousemove', onMove);
        document.addEventListener('mouseup', onUp);
      });
    }

    // ── Fixture switching ────────────────────────────────

    _buildFixtureButtons() {
      const fixtures = window.__klineEngineV2Fixtures;
      if (!fixtures || typeof fixtures !== 'object') return;

      const names = Object.keys(fixtures);
      if (names.length === 0) return;

      this._fixturesSection.style.display = '';
      this._activeFixture = null;

      names.forEach(name => {
        const btn = document.createElement('button');
        btn.className = 'kline-devpanel__fixture-btn';
        btn.textContent = name;
        btn.addEventListener('click', () => {
          this._activeFixture = name;
          this.engine.loadData(fixtures[name]);
          this._updateFixtureHighlight();
          this._setImportStatus(`Loaded fixture "${name}"`, 'success');
        });
        this._fixtureButtons.appendChild(btn);
      });
    }

    _updateFixtureHighlight() {
      this._fixtureButtons.querySelectorAll('.kline-devpanel__fixture-btn').forEach(btn => {
        btn.classList.toggle('is-active', btn.textContent === this._activeFixture);
      });
    }

    // ── State display ───────────────────────────────────

    _updateState() {
      if (this._destroyed) return;

      const eng = this.engine;
      const tf = eng.getTimeframe();
      const idx = eng.getCurrentIndex();
      const playing = eng.isPlaying();
      const speed = eng.getSpeed();
      const dm = eng.dataManager;
      const vm = eng.viewportManager;
      const bars = dm.getBars(tf);

      const rows = [
        ['Timeframe', tf],
        ['Index', `${idx} / ${Math.max(0, bars.length - 1)}`],
        ['Bars', bars.length],
        ['Zoom', vm.zoomScale.toFixed(2) + 'x'],
        ['Mode', vm.followMode ? 'Follow' : 'Manual'],
        ['Playback', playing ? `Playing ${speed}x` : 'Paused'],
      ];

      this._stateRows.innerHTML = rows.map(([label, value]) =>
        `<div class="kline-devpanel__row">
          <span class="kline-devpanel__label">${label}</span>
          <span class="kline-devpanel__value">${value}</span>
        </div>`
      ).join('');
    }

    // ── File import ─────────────────────────────────────

    _handleFile(file) {
      this._setImportStatus('Loading...', '');
      const reader = new FileReader();
      reader.onload = () => {
        try {
          const json = JSON.parse(reader.result);
          this._validateAndLoad(json, file.name);
        } catch (err) {
          this._setImportStatus(`Parse error: ${err.message}`, 'error');
        }
      };
      reader.onerror = () => {
        this._setImportStatus('File read failed', 'error');
      };
      reader.readAsText(file);
    }

    _validateAndLoad(json, filename) {
      // Engine expects: { bars_1m: [...], bars_5m: [...], meta: {...} }
      const bars1m = json.bars_1m || [];
      const bars5m = json.bars_5m || [];
      const totalBars = bars1m.length + bars5m.length;

      if (totalBars === 0) {
        this._setImportStatus('Invalid format: missing bars_1m or bars_5m arrays', 'error');
        return;
      }

      // Check bar fields on first available bar
      const sample = bars1m[0] || bars5m[0];
      const hasOHLC = ['O', 'H', 'L', 'C'].every(f => f in sample);
      if (!hasOHLC) {
        this._setImportStatus('Invalid format: bars missing O/H/L/C fields', 'error');
        return;
      }

      try {
        const summary = this.engine.loadData(json);
        this._setImportStatus(`Loaded "${filename}" — ${totalBars} bars`, 'success');
      } catch (err) {
        this._setImportStatus(`Load error: ${err.message}`, 'error');
      }
    }

    _setImportStatus(msg, type) {
      this._importStatus.textContent = msg;
      this._importStatus.className = 'kline-devpanel__status-msg' + (type ? ` ${type}` : '');
    }

    // ── Lifecycle ───────────────────────────────────────

    destroy() {
      if (this._destroyed) return;
      this._destroyed = true;
      this._unsubs.forEach(unsub => unsub());
      this._unsubs = [];
      if (this.el && this.el.parentNode) {
        this.el.parentNode.removeChild(this.el);
      }
    }
  }

  window.KlineDevPanel = KlineDevPanel;
})();
