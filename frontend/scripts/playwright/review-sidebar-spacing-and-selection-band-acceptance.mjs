/**
 * Mandatory B-carriers for the Review Sidebar Spacing + K-line Selection Band plan.
 * Carriers: B-Sidebar-layout, B-Group-band-cancel, B-Event-focus-cancel + V1–V3.
 * Receipts under untracked output/playwright/review-sidebar-spacing-selection-band-<timestamp>/
 *
 * Independent oracle constants (Phase 0 freeze, evidence under
 * output/phase0-sidebar-spacing-oracle/): computed offline from the pure
 * groupBarSpan / eventFocusPayload helpers against the tracked-DB export for
 * QQQ 2026-07-17 (RTH window, 390 1m bars). Highlight storage is never read
 * to define expectations — after select it must be EMPTY (OPT-002).
 */
import { spawn, execSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from '../../node_modules/playwright/index.mjs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
// frontend/scripts/playwright → repo root is three levels up
const repoRoot = path.resolve(__dirname, '../../..');

const timestamp = new Date().toISOString().replace(/[-:TZ.]/g, '').slice(0, 14);
const outputDir = path.join(repoRoot, 'output', 'playwright', `review-sidebar-spacing-selection-band-${timestamp}`);
fs.mkdirSync(outputDir, { recursive: true });

const trackedDbPath = path.join(repoRoot, 'data', 'sqlite', 'tang_strategy_live_extended.db');
const tempDbPath = path.join(outputDir, `temp_acceptance_${Date.now()}.db`);
fs.copyFileSync(trackedDbPath, tempDbPath);

const backendPort = 8036;
const frontendPort = 5207;
const staticFrontendPort = 5208;
const DESKTOP = { width: 1672, height: 941 };

// --- Frozen fixture + independent oracle constants (Phase 0) ---
const GROUP_ID = 'tg_20260717_vordin_qqq_002';
const EVENT_ROW_INDEX = 1; // timeline row: 09:50 PART tg_20260717_vordin_qqq_002_l1_e2
const EXPECTED_SPAN_START = 12; // bar 09:42
const EXPECTED_SPAN_END = 31; // bar 10:01
const EXPECTED_EVENT_BAR = 20; // bar 09:50
const RTH_BAR_COUNT = 390;
const GAP_TARGET = 20;
const GAP_TOLERANCE = 2;

const pythonBin = fs.existsSync(path.join(repoRoot, 'backend', '.venv', 'bin', 'python'))
  ? path.join(repoRoot, 'backend', '.venv', 'bin', 'python')
  : 'python3';

console.log(`Starting acceptance… Output: ${outputDir}`);

const backendEnv = {
  ...process.env,
  PYTHONPATH: path.join(repoRoot, 'backend'),
  TANG_DB_PATH: tempDbPath,
};
const backendProc = spawn(
  pythonBin,
  ['-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', String(backendPort)],
  { cwd: path.join(repoRoot, 'backend'), env: backendEnv, stdio: 'inherit' },
);

const frontendEnv = {
  ...process.env,
  TANG_API_PROXY_TARGET: `http://127.0.0.1:${backendPort}`,
};
const frontendProc = spawn(
  'npm',
  ['--prefix', 'frontend', 'run', 'dev', '--', '--host', '127.0.0.1', '--port', String(frontendPort), '--strictPort'],
  { cwd: repoRoot, env: frontendEnv, stdio: 'inherit', shell: true },
);

let staticFrontendProc = null;

async function waitUrl(url, timeoutMs = 90000) {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    try {
      const res = await fetch(url);
      if (res.ok || res.status === 404) return true;
    } catch (_) {}
    await new Promise((r) => setTimeout(r, 250));
  }
  throw new Error(`Timeout waiting for ${url}`);
}

function stopProcessTree(proc) {
  if (!proc || proc.killed) return;
  if (process.platform === 'win32') {
    try {
      execSync(`taskkill /PID ${proc.pid} /T /F`, { stdio: 'ignore' });
    } catch (_) {}
    return;
  }
  try {
    process.kill(-proc.pid, 'SIGTERM');
  } catch (_) {
    try { proc.kill('SIGTERM'); } catch (_) {}
  }
}

async function login(page, base) {
  await page.goto(`${base}/`);
  const passwordInput = page.locator('input[type="password"]');
  if (await passwordInput.isVisible({ timeout: 8000 }).catch(() => false)) {
    await passwordInput.fill('admin-change-me');
    await page.click('button[type="submit"]');
  }
  await page.waitForSelector('.sidebar', { timeout: 20000 });
}

async function openQqqReview(page) {
  const reviewNav = page.locator('button.nav-item', { hasText: 'Review' });
  await reviewNav.click();
  await page.waitForSelector('.trade-filter-panel', { timeout: 20000 });
  const qqqTab = page.getByRole('tab', { name: 'QQQ', exact: true }).first();
  if (!(await qqqTab.isVisible())) throw new Error('QQQ tab unavailable');
  await qqqTab.click();
  await page.waitForFunction(() => (
    document.querySelector('[role="tab"][aria-selected="true"]')?.textContent?.trim() === 'QQQ'
  ));
  await page.waitForSelector('.trade-group-card', { timeout: 25000 });
  // Prefer 2026-07-17 if a day chip is available.
  const dayChip = page.locator('button', { hasText: /17/ }).first();
  if (await dayChip.isVisible().catch(() => false)) {
    await dayChip.click().catch(() => {});
    await page.waitForTimeout(400);
  }
  await page.waitForSelector('.unified-kline-engine', { timeout: 30000 });
  await page.waitForFunction(() => {
    const el = document.querySelector('.unified-kline-engine');
    return Boolean(el && el.__klineEngine && typeof el.__klineEngine.getViewportDebug === 'function');
  }, null, { timeout: 30000 });
}

async function readEngineDebug(page) {
  return page.evaluate(() => {
    const el = document.querySelector('.unified-kline-engine');
    if (!el?.__klineEngine?.getViewportDebug) return null;
    return el.__klineEngine.getViewportDebug();
  });
}

async function readHighlights(page) {
  return page.evaluate(() => {
    const el = document.querySelector('.unified-kline-engine');
    if (!el?.__klineEngine?.getHighlightRanges) return null;
    return el.__klineEngine.getHighlightRanges();
  });
}

async function measureSidebarLayout(page) {
  return page.evaluate(() => {
    const list = document.querySelector('.dr-sidebar .dr-signal-list');
    if (!list) return null;
    const tools = list.querySelector(':scope > .trade-filter-panel');
    const trades = list.querySelector(':scope > .trade-record-list');
    const signals = list.querySelector(':scope > .dr-signal-stack');
    if (!tools || !trades || !signals) {
      return { missing: { tools: !tools, trades: !trades, signals: !signals } };
    }
    const captionInfo = (host) => {
      const caption = host.querySelector(':scope > .stack-caption');
      if (!caption) return null;
      const hairline = getComputedStyle(caption, '::after');
      return {
        text: caption.textContent.trim(),
        hairlineWidth: hairline.borderTopWidth,
        hairlineStyle: hairline.borderTopStyle,
      };
    };
    const toolsRect = tools.getBoundingClientRect();
    const tradesRect = trades.getBoundingClientRect();
    const signalsRect = signals.getBoundingClientRect();
    return {
      gapToolsTrades: tradesRect.top - toolsRect.bottom,
      gapTradesSignals: signalsRect.top - tradesRect.bottom,
      tradesCaption: captionInfo(trades),
      signalsCaption: captionInfo(signals),
      toolsTitleCount: list.querySelectorAll('.trade-tools-title').length,
      toolsHeadCount: list.querySelectorAll('.trade-tools-head').length,
      downloadCount: list.querySelectorAll('.trade-export-button').length,
      toolsPanelText: tools.innerText,
      tradersLabelCount: tools.querySelectorAll('.trade-filter-label').length,
    };
  });
}

function assertSidebarLayout(layout, surfaceLabel) {
  if (!layout) throw new Error(`${surfaceLabel}: .dr-sidebar .dr-signal-list missing`);
  if (layout.missing) {
    throw new Error(`${surfaceLabel}: mid-stack wrappers missing ${JSON.stringify(layout.missing)}`);
  }
  for (const [name, gap] of [['gapToolsTrades', layout.gapToolsTrades], ['gapTradesSignals', layout.gapTradesSignals]]) {
    if (!Number.isFinite(gap)) throw new Error(`${surfaceLabel}: ${name} not finite`);
    if (Math.abs(gap - GAP_TARGET) > GAP_TOLERANCE) {
      throw new Error(`${surfaceLabel}: ${name} ${gap.toFixed(2)}px outside ${GAP_TARGET}±${GAP_TOLERANCE}px`);
    }
  }
  if (!layout.tradesCaption || !/交易者/.test(layout.tradesCaption.text) || !/Trades/.test(layout.tradesCaption.text)) {
    throw new Error(`${surfaceLabel}: 交易者 caption missing (${layout.tradesCaption?.text || 'none'})`);
  }
  if (!layout.signalsCaption || !/策略讲解/.test(layout.signalsCaption.text) || !/Signals/.test(layout.signalsCaption.text)) {
    throw new Error(`${surfaceLabel}: 策略讲解 caption missing (${layout.signalsCaption?.text || 'none'})`);
  }
  for (const [name, caption] of [['trades', layout.tradesCaption], ['signals', layout.signalsCaption]]) {
    if (caption.hairlineWidth !== '1px' || caption.hairlineStyle !== 'solid') {
      throw new Error(`${surfaceLabel}: ${name} caption hairline ${caption.hairlineWidth}/${caption.hairlineStyle}`);
    }
  }
  if (layout.toolsTitleCount !== 0) throw new Error(`${surfaceLabel}: Trade tools title still rendered`);
  if (/Trade tools/i.test(layout.toolsPanelText)) throw new Error(`${surfaceLabel}: "Trade tools" text in filter panel`);
  if (layout.downloadCount !== 0 || layout.toolsHeadCount !== 0) {
    throw new Error(`${surfaceLabel}: Download/export head present in sidebar stack (download=${layout.downloadCount}, head=${layout.toolsHeadCount})`);
  }
  if (layout.tradersLabelCount !== 1) {
    throw new Error(`${surfaceLabel}: expected single Traders label, got ${layout.tradersLabelCount}`);
  }
  return layout;
}

function assertWindowContains(debug, startIndex, endIndex, surfaceLabel, tag) {
  if (!debug) throw new Error(`${surfaceLabel}: ${tag} getViewportDebug returned null`);
  if (debug.timeframe !== '1m') throw new Error(`${surfaceLabel}: ${tag} timeframe ${debug.timeframe} !== 1m`);
  if (startIndex < debug.start || endIndex > debug.end) {
    throw new Error(
      `${surfaceLabel}: ${tag} window [${debug.start},${debug.end}] does not contain `
      + `expected [${startIndex},${endIndex}]`,
    );
  }
}

async function runGroupBandCancelFlow(page, surfaceLabel) {
  const card = page.locator(`[data-trade-group-id="${GROUP_ID}"]`).first();
  if (!(await card.isVisible().catch(() => false))) {
    throw new Error(`${surfaceLabel}: frozen group card ${GROUP_ID} not visible`);
  }
  await card.locator('.trade-group-summary').click();
  await page.waitForTimeout(250);

  // Empty-highlight rule: no selection band paint after group select.
  const highlights = await readHighlights(page);
  if (!Array.isArray(highlights)) throw new Error(`${surfaceLabel}: getHighlightRanges unavailable`);
  if (highlights.length !== 0) {
    throw new Error(`${surfaceLabel}: highlight band painted after group select: ${JSON.stringify(highlights)}`);
  }

  // Independent span oracle: viewport must contain the frozen expected span.
  const debug1 = await readEngineDebug(page);
  assertWindowContains(debug1, EXPECTED_SPAN_START, EXPECTED_SPAN_END, surfaceLabel, 'group-select');

  // No post-fit recenter: window must be stable and still contain the span.
  await page.waitForTimeout(400);
  const debug2 = await readEngineDebug(page);
  assertWindowContains(debug2, EXPECTED_SPAN_START, EXPECTED_SPAN_END, surfaceLabel, 'group-select(stable)');
  if (debug1.start !== debug2.start || debug1.end !== debug2.end) {
    throw new Error(
      `${surfaceLabel}: viewport moved after fitRange ([${debug1.start},${debug1.end}] → `
      + `[${debug2.start},${debug2.end}]) — post-fit recenter suspected`,
    );
  }
  const highlightsAfter = await readHighlights(page);
  if (highlightsAfter.length !== 0) {
    throw new Error(`${surfaceLabel}: highlight band appeared after settle: ${JSON.stringify(highlightsAfter)}`);
  }
  return { viewport: { start: debug2.start, end: debug2.end }, expectedSpan: [EXPECTED_SPAN_START, EXPECTED_SPAN_END], highlights: 0 };
}

async function runEventFocusCancelFlow(page, surfaceLabel) {
  const card = page.locator(`[data-trade-group-id="${GROUP_ID}"]`).first();
  if (!(await card.isVisible().catch(() => false))) {
    throw new Error(`${surfaceLabel}: frozen group card ${GROUP_ID} not visible (event focus)`);
  }
  const toggle = card.locator('.trade-drilldown-toggle');
  if (await toggle.isVisible().catch(() => false)) {
    if ((await toggle.getAttribute('aria-expanded')) !== 'true') await toggle.click();
  }
  await card.locator('.trade-timeline-row').first().waitFor({ timeout: 5000 });
  const rows = card.locator('.trade-timeline-row');
  const rowCount = await rows.count();
  if (rowCount <= EVENT_ROW_INDEX) {
    throw new Error(`${surfaceLabel}: timeline rows ${rowCount} <= frozen index ${EVENT_ROW_INDEX}`);
  }
  await rows.nth(EVENT_ROW_INDEX).click();
  await page.waitForTimeout(250);

  // Empty-highlight rule: no band/dot overlay after event-row focus.
  const highlights = await readHighlights(page);
  if (!Array.isArray(highlights) || highlights.length !== 0) {
    throw new Error(`${surfaceLabel}: highlight painted after event focus: ${JSON.stringify(highlights)}`);
  }

  // Independent single-bar oracle: focused bar inside a non-full-day window.
  const debug = await readEngineDebug(page);
  assertWindowContains(debug, EXPECTED_EVENT_BAR, EXPECTED_EVENT_BAR, surfaceLabel, 'event-focus');
  const windowSize = debug.end - debug.start + 1;
  if (windowSize > 120) {
    throw new Error(`${surfaceLabel}: event focus looks full-day (window=${windowSize} > 120)`);
  }
  const highlightsAfter = await readHighlights(page);
  if (highlightsAfter.length !== 0) {
    throw new Error(`${surfaceLabel}: highlight appeared after event settle: ${JSON.stringify(highlightsAfter)}`);
  }
  return { viewport: { start: debug.start, end: debug.end }, expectedBar: EXPECTED_EVENT_BAR, windowSize, highlights: 0 };
}

async function run() {
  const receipts = [];
  const record = (id, title, status, details = {}) => {
    receipts.push({ id, title, status, details, ts: new Date().toISOString() });
    console.log(`[RECEIPT] ${id}: ${title} -> ${status}`);
  };

  try {
    await waitUrl(`http://127.0.0.1:${backendPort}/openapi.json`);
    await waitUrl(`http://127.0.0.1:${frontendPort}/`);
    console.log('Backend & Frontend ready');

    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({ viewport: DESKTOP });
    const page = await context.newPage();

    await login(page, `http://127.0.0.1:${frontendPort}`);
    await openQqqReview(page);

    // --- B-Sidebar-layout (Review) + V1 ---
    const reviewLayout = assertSidebarLayout(await measureSidebarLayout(page), 'Review');
    const sidebarEl = page.locator('.dr-sidebar').first();
    const v1Path = path.join(outputDir, 'v1-review-sidebar-mid-stack.png');
    await sidebarEl.screenshot({ path: v1Path });
    record('V1', 'Interactive Review sidebar mid-stack', 'PASS', { path: v1Path });

    // --- B-Group-band-cancel (Review) + V2 ---
    const reviewGroup = await runGroupBandCancelFlow(page, 'Review');
    const v2Path = path.join(outputDir, 'v2-review-chart-after-group-select.png');
    await page.screenshot({ path: v2Path, fullPage: false });
    record('V2', 'Interactive Review chart after group select (no band)', 'PASS', { path: v2Path, ...reviewGroup });

    // --- B-Event-focus-cancel (Review) ---
    const reviewEvent = await runEventFocusCancelFlow(page, 'Review');
    record('B-Event-focus-cancel', 'Review event-row focus: empty highlights, single-bar locate', 'PASS', {
      surface: 'Review',
      ...reviewEvent,
    });
    record('B-Group-band-cancel', 'Review group select: empty highlights, span-fit retained', 'PASS', {
      surface: 'Review',
      ...reviewGroup,
    });
    record('B-Sidebar-layout', 'Review 20px gaps, captions+hairlines, no title/Download', 'PASS', {
      surface: 'Review',
      ...reviewLayout,
      toolsPanelText: undefined,
    });

    // --- Static surface ---
    console.log('Exporting static reviews for Static carriers…');
    execSync(
      `${JSON.stringify(pythonBin)} backend/scripts/export_static_reviews.py --output frontend/public/reviews --limit 8 --strategy-families v3,v4,v5`,
      {
        cwd: repoRoot,
        env: {
          ...process.env,
          PYTHONPATH: path.join(repoRoot, 'backend'),
          TANG_DB_PATH: tempDbPath,
        },
        stdio: 'inherit',
        shell: true,
      },
    );

    staticFrontendProc = spawn(
      'npm',
      ['--prefix', 'frontend', 'run', 'dev', '--', '--host', '127.0.0.1', '--port', String(staticFrontendPort), '--strictPort'],
      {
        cwd: repoRoot,
        env: { ...process.env, VITE_STATIC_REVIEWS: 'true' },
        stdio: 'inherit',
        shell: true,
      },
    );
    await waitUrl(`http://127.0.0.1:${staticFrontendPort}/`);

    const staticPage = await context.newPage();
    await staticPage.goto(`http://127.0.0.1:${staticFrontendPort}/#qqq-2026-07-17-extended`);
    await staticPage.waitForSelector('.trade-filter-panel', { timeout: 30000 });
    await staticPage.waitForSelector('.unified-kline-engine', { timeout: 30000 });
    await staticPage.waitForFunction(() => {
      const el = document.querySelector('.unified-kline-engine');
      return Boolean(el && el.__klineEngine && typeof el.__klineEngine.getViewportDebug === 'function');
    }, null, { timeout: 30000 });
    await staticPage.waitForSelector('.trade-group-card', { timeout: 30000 });

    // --- B-Sidebar-layout (Static) ---
    const staticLayout = assertSidebarLayout(await measureSidebarLayout(staticPage), 'Static');
    record('B-Sidebar-layout-static', 'Static 20px gaps, captions+hairlines, no title/Download', 'PASS', {
      surface: 'Static',
      ...staticLayout,
      toolsPanelText: undefined,
    });

    // --- B-Group-band-cancel (Static) + V3 ---
    const staticGroup = await runGroupBandCancelFlow(staticPage, 'Static');
    record('B-Group-band-cancel-static', 'Static group select: empty highlights, span-fit retained', 'PASS', {
      surface: 'Static',
      ...staticGroup,
    });
    const v3Path = path.join(outputDir, 'v3-static-sidebar-and-chart-after-group-select.png');
    await staticPage.screenshot({ path: v3Path, fullPage: false });
    record('V3', 'Static sidebar + chart after group select (parity)', 'PASS', { path: v3Path, ...staticGroup });

    // --- B-Event-focus-cancel (Static) ---
    const staticEvent = await runEventFocusCancelFlow(staticPage, 'Static');
    record('B-Event-focus-cancel-static', 'Static event-row focus: empty highlights, single-bar locate', 'PASS', {
      surface: 'Static',
      ...staticEvent,
    });

    await staticPage.close();
    stopProcessTree(staticFrontendProc);
    staticFrontendProc = null;
    fs.rmSync(path.join(repoRoot, 'frontend', 'public', 'reviews'), { recursive: true, force: true });

    await browser.close();
    fs.writeFileSync(path.join(outputDir, 'receipts.json'), JSON.stringify(receipts, null, 2), 'utf8');
    console.log(`All B-carriers + V1–V3 PASS. Receipts: ${path.join(outputDir, 'receipts.json')}`);
    return 0;
  } catch (err) {
    console.error('ACCEPTANCE FAILED:', err);
    fs.writeFileSync(
      path.join(outputDir, 'failure.json'),
      JSON.stringify({ error: String(err?.stack || err), receipts }, null, 2),
      'utf8',
    );
    throw err;
  } finally {
    stopProcessTree(staticFrontendProc);
    stopProcessTree(frontendProc);
    stopProcessTree(backendProc);
  }
}

run()
  .then((code) => process.exit(code || 0))
  .catch(() => process.exit(1));
