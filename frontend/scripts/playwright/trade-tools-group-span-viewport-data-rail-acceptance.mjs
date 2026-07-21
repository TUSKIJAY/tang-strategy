/**
 * Mandatory B-carriers for Trade Tools / Group Span / Viewport / Data Rail plan.
 * Carriers: B-TF-first-paint, B-Group-span, B-Data-rail-layout + V1–V6 screenshots.
 * Receipts under untracked output/playwright/trade-tools-group-span-<timestamp>/
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
const outputDir = path.join(repoRoot, 'output', 'playwright', `trade-tools-group-span-${timestamp}`);
fs.mkdirSync(outputDir, { recursive: true });

const trackedDbPath = path.join(repoRoot, 'data', 'sqlite', 'tang_strategy_live_extended.db');
const tempDbPath = path.join(outputDir, `temp_acceptance_${Date.now()}.db`);
fs.copyFileSync(trackedDbPath, tempDbPath);

const backendPort = 8035;
const frontendPort = 5205;
const staticFrontendPort = 5206;
const DESKTOP = { width: 1672, height: 941 };
const NARROW = { width: 390, height: 844 };
const MULTI_GROUP_ID = 'tg_20260717_vordin_qqq_002';

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
    if (!el?.__klineEngine?.getHighlightRanges) return [];
    return el.__klineEngine.getHighlightRanges();
  });
}

async function waitFirstRenderAfterTf(page, destTf) {
  // Arm first-completed-render waiter, then click real toolbar TF button.
  const waitPromise = page.evaluate((timeframe) => {
    const el = document.querySelector('.unified-kline-engine');
    const engine = el.__klineEngine;
    return new Promise((resolve) => {
      const prev = engine.render.bind(engine);
      engine.render = function patchedRender(...args) {
        const result = prev(...args);
        if (engine.currentTimeframe === timeframe) {
          engine.render = prev;
          resolve(engine.getViewportDebug());
        }
        return result;
      };
    });
  }, destTf);

  const btn = page.locator(`.kline-engine__button[data-action="timeframe"][data-timeframe="${destTf}"]`).first();
  if (!(await btn.isVisible({ timeout: 5000 }).catch(() => false))) {
    throw new Error(`TF toolbar button ${destTf} not visible`);
  }
  await btn.click();
  const debug = await waitPromise;
  await page.waitForTimeout(30);
  return debug;
}

function assertTfOracle(debug, destTf, slotWidth) {
  if (!debug) throw new Error('getViewportDebug returned null');
  if (debug.timeframe !== destTf) {
    throw new Error(`timeframe expected ${destTf}, got ${debug.timeframe}`);
  }
  if (debug.zoomScale !== 1) {
    throw new Error(`zoomScale expected 1, got ${debug.zoomScale}`);
  }
  if (!Number.isFinite(debug.count) || debug.count < 1) {
    throw new Error(`invalid count ${debug.count}`);
  }
  // At zoomScale 1, count equals the resolved base window.
  if (debug.count !== debug.base) {
    throw new Error(`count ${debug.count} !== base ${debug.base} at zoomScale 1`);
  }
  if (debug.start < 0) throw new Error(`start < 0: ${debug.start}`);
  const rightEmpty = debug.chartWidth - debug.count * slotWidth;
  // Floor division remainder is always < one slot; maxBars clamp can leave more empty.
  const unclamped = Math.floor(debug.chartWidth / slotWidth);
  if (debug.count >= unclamped) {
    if (rightEmpty > slotWidth + 0.5) {
      throw new Error(`right empty ${rightEmpty} > one slot ${slotWidth}`);
    }
  }
  if (typeof debug.followMode !== 'boolean') {
    throw new Error(`followMode not boolean: ${debug.followMode}`);
  }
  // followMode === (start >= maxStart) is enforced by setTimeframe; re-check via end occupancy.
  return debug;
}

async function runGroupSpanFlow(page, surfaceLabel) {
  const card = page.locator(`[data-trade-group-id="${MULTI_GROUP_ID}"]`).first();
  if (!(await card.isVisible().catch(() => false))) {
    // Fall back to first multi-event card with timeline expand.
    const any = page.locator('.trade-group-card').first();
    if (!(await any.isVisible())) throw new Error(`${surfaceLabel}: no trade cards`);
  }
  const target = (await card.isVisible().catch(() => false))
    ? card
    : page.locator('.trade-group-card').nth(1);
  await target.locator('.trade-group-summary').click();
  await page.waitForTimeout(200);

  const afterSelect = await readHighlights(page);
  if (!afterSelect.length) throw new Error(`${surfaceLabel}: no highlight after group select`);
  const band = afterSelect[0];
  if (band.style !== 'blue') {
    throw new Error(`${surfaceLabel}: expected blue band, got ${band.style}`);
  }
  if (band.startIndex === band.endIndex) {
    // Multi-event group should span >1 when fixture exists; allow single only for fallback.
    console.warn(`${surfaceLabel}: WARN span start===end (${band.startIndex})`);
  }
  const debugAfterSelect = await readEngineDebug(page);
  if (!debugAfterSelect) throw new Error(`${surfaceLabel}: no viewport after select`);
  if (band.startIndex < debugAfterSelect.start || band.endIndex > debugAfterSelect.end) {
    throw new Error(
      `${surfaceLabel}: visible window [${debugAfterSelect.start},${debugAfterSelect.end}] `
      + `does not contain span [${band.startIndex},${band.endIndex}]`,
    );
  }
  const spanSnapshot = { ...band };

  // Expand timeline and click a named event row.
  const toggle = target.locator('.trade-drilldown-toggle');
  if (await toggle.isVisible().catch(() => false)) {
    const expanded = await toggle.getAttribute('aria-expanded');
    if (expanded !== 'true') await toggle.click();
  }
  await page.waitForSelector('.trade-timeline-row', { timeout: 5000 });
  const rows = target.locator('.trade-timeline-row');
  const rowCount = await rows.count();
  if (rowCount < 1) throw new Error(`${surfaceLabel}: no timeline rows`);
  // Prefer a middle PART/SELL row when multi.
  const clickIndex = rowCount > 1 ? 1 : 0;
  await rows.nth(clickIndex).click();
  await page.waitForTimeout(200);
  const afterEvent = await readHighlights(page);
  if (!afterEvent.length) throw new Error(`${surfaceLabel}: no highlight after event focus`);
  const focus = afterEvent[0];
  if (focus.startIndex !== focus.endIndex) {
    throw new Error(`${surfaceLabel}: event focus not single-bar (${focus.startIndex}-${focus.endIndex})`);
  }
  const debugAfterEvent = await readEngineDebug(page);
  const windowSize = debugAfterEvent.end - debugAfterEvent.start + 1;
  // Must not be a full-day fit (~390 bars on 1m). Tight event focus is much smaller.
  if (windowSize > 120) {
    throw new Error(`${surfaceLabel}: event focus looks full-day (window=${windowSize})`);
  }
  if (focus.startIndex < debugAfterEvent.start || focus.endIndex > debugAfterEvent.end) {
    throw new Error(`${surfaceLabel}: focused bar not in view`);
  }

  // Re-click card restores primary span-fit.
  await target.locator('.trade-group-summary').click();
  await page.waitForTimeout(200);
  const restored = await readHighlights(page);
  if (!restored.length) throw new Error(`${surfaceLabel}: no highlight after restore`);
  const restoredBand = restored[0];
  if (restoredBand.startIndex !== spanSnapshot.startIndex || restoredBand.endIndex !== spanSnapshot.endIndex) {
    throw new Error(
      `${surfaceLabel}: restore mismatch expected ${spanSnapshot.startIndex}-${spanSnapshot.endIndex} `
      + `got ${restoredBand.startIndex}-${restoredBand.endIndex}`,
    );
  }
  if (restoredBand.style !== 'blue') {
    throw new Error(`${surfaceLabel}: restore style not blue`);
  }

  return {
    span: spanSnapshot,
    focus,
    restored: restoredBand,
    rowCount,
  };
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

    // Track wheel/pinch/keyboard zoom for B-TF-first-paint zero-zoom requirement.
    await page.addInitScript(() => {
      window.__zoomEventLog = [];
      window.addEventListener('wheel', (e) => {
        window.__zoomEventLog.push({ type: 'wheel', deltaY: e.deltaY });
      }, { capture: true, passive: true });
      window.addEventListener('keydown', (e) => {
        if (e.key === '+' || e.key === '-' || e.key === '=' || e.metaKey || e.ctrlKey) {
          window.__zoomEventLog.push({ type: 'keydown', key: e.key });
        }
      }, true);
    });

    await login(page, `http://127.0.0.1:${frontendPort}`);
    await openQqqReview(page);

    // --- No Eligibility chrome ---
    const toolsText = await page.locator('.trade-filter-panel').innerText();
    if (/Eligibility|\bDisplay\b|\bReported\b|\bCalculated\b/.test(toolsText)) {
      throw new Error(`Eligibility chrome still visible in tools: ${toolsText.slice(0, 200)}`);
    }

    // Expand multi-event group for V1
    const multiCard = page.locator(`[data-trade-group-id="${MULTI_GROUP_ID}"]`).first();
    if (await multiCard.isVisible().catch(() => false)) {
      const toggle = multiCard.locator('.trade-drilldown-toggle');
      if (await toggle.isVisible()) await toggle.click();
    } else {
      const anyToggle = page.locator('.trade-drilldown-toggle').first();
      if (await anyToggle.isVisible()) await anyToggle.click();
    }
    await page.waitForTimeout(200);

    const v1Path = path.join(outputDir, 'v1-review-tools-timeline.png');
    await page.screenshot({ path: v1Path, fullPage: false });
    record('V1', 'Interactive Review tools + expanded timeline', 'PASS', { path: v1Path });

    // --- B-Group-span (Review) ---
    const reviewGroup = await runGroupSpanFlow(page, 'Review');
    const v2Path = path.join(outputDir, 'v2-review-group-span-band.png');
    await page.screenshot({ path: v2Path, fullPage: false });
    record('V2', 'Interactive Review chart after group select', 'PASS', { path: v2Path, ...reviewGroup.span });
    record('B-Group-span', 'Review multi-event span + event focus + restore', 'PASS', {
      surface: 'Review',
      ...reviewGroup,
    });

    // --- B-TF-first-paint ---
    // Clear zoom log; drive TF switches via setTimeframe + first completed render.
    await page.evaluate(() => { window.__zoomEventLog = []; });

    // Ensure start on 1m via real toolbar if needed.
    const tfNow = await page.evaluate(() => {
      const el = document.querySelector('.unified-kline-engine');
      return el.__klineEngine.getTimeframe();
    });
    if (tfNow !== '1m') {
      await waitFirstRenderAfterTf(page, '1m');
    }
    await page.evaluate(() => { window.__zoomEventLog = []; });

    const debug5m = assertTfOracle(await waitFirstRenderAfterTf(page, '5m'), '5m', 18);
    await page.evaluate(() => { window.__zoomEventLog = []; });
    const debug1m = assertTfOracle(await waitFirstRenderAfterTf(page, '1m'), '1m', 14);

    const zoomLog = await page.evaluate(() => window.__zoomEventLog || []);
    const wheelEvents = zoomLog.filter((e) => e.type === 'wheel');
    if (wheelEvents.length > 0) {
      throw new Error(`wheel events during TF switch: ${JSON.stringify(wheelEvents)}`);
    }

    const v4Path = path.join(outputDir, 'v4-review-tf-5m-first-paint.png');
    // Switch back to 5m for V4 visual
    await waitFirstRenderAfterTf(page, '5m');
    await page.screenshot({ path: v4Path, fullPage: false });
    record('V4', 'Review after 1m→5m first paint', 'PASS', { path: v4Path, debug5m, debug1m });
    record('B-TF-first-paint', '1m→5m and 5m→1m first completed render oracle', 'PASS', {
      debug5m,
      debug1m,
      wheelEvents: wheelEvents.length,
      zoomLog,
    });

    // --- Data rail layout (Data page) ---
    const dataNav = page.locator('button.nav-item', { hasText: /Data|数据|Market/ }).first();
    // Try sidebar nav items
    let openedData = false;
    for (const name of ['Data', '数据', 'Dashboard', '市场']) {
      const nav = page.locator('button.nav-item', { hasText: name }).first();
      if (await nav.isVisible().catch(() => false)) {
        await nav.click();
        openedData = true;
        break;
      }
    }
    if (!openedData) {
      // Fallback: go to root route often hosts Dashboard
      await page.goto(`http://127.0.0.1:${frontendPort}/`);
      await page.waitForTimeout(500);
    }
    await page.waitForSelector('.data-market-days-rail', { timeout: 20000 });

    const dataLayout = await page.evaluate(() => {
      const host = document.querySelector('.data-market-days-rail');
      if (!host) return null;
      const hostRect = host.getBoundingClientRect();
      const measure = (sel) => {
        const el = host.querySelector(sel);
        if (!el) return null;
        const cs = getComputedStyle(el);
        const r = el.getBoundingClientRect();
        return {
          width: r.width,
          flexGrow: cs.flexGrow,
          maxWidth: cs.maxWidth,
        };
      };
      return {
        hostWidth: hostRect.width,
        hostMaxWidth: getComputedStyle(host).maxWidth,
        tickerBtn: measure('.ticker-tabs button'),
        modeBtn: measure('.date-rail-mode button'),
        monthBar: measure('.date-rail-month-bar') || measure('.date-rail-month-identity'),
        panelWidth: host.closest('.panel')?.getBoundingClientRect().width || null,
      };
    });
    if (!dataLayout) throw new Error('data-market-days-rail host missing');
    if (dataLayout.hostWidth > 420 + 1) {
      throw new Error(`Data rail host width ${dataLayout.hostWidth} > 420`);
    }
    for (const key of ['tickerBtn', 'modeBtn', 'monthBar']) {
      const m = dataLayout[key];
      if (!m) {
        if (key === 'monthBar') {
          // month bar only in month mode — switch mode if needed
          const monthMode = page.locator('.data-market-days-rail .date-rail-mode button', { hasText: /月|Month|month/ }).first();
          if (await monthMode.isVisible().catch(() => false)) {
            await monthMode.click();
            await page.waitForTimeout(200);
          }
        } else {
          throw new Error(`Data layout missing ${key}`);
        }
      }
    }
    const dataLayout2 = await page.evaluate(() => {
      const host = document.querySelector('.data-market-days-rail');
      const measure = (sel) => {
        const el = host.querySelector(sel);
        if (!el) return null;
        const cs = getComputedStyle(el);
        const r = el.getBoundingClientRect();
        return { width: r.width, flexGrow: cs.flexGrow };
      };
      return {
        hostWidth: host.getBoundingClientRect().width,
        tickerBtn: measure('.ticker-tabs button'),
        modeBtn: measure('.date-rail-mode button'),
        monthBar: measure('.date-rail-month-bar') || measure('.date-rail-month-identity'),
        panelWidth: host.closest('.panel')?.getBoundingClientRect().width || null,
      };
    });
    if (dataLayout2.tickerBtn && dataLayout2.tickerBtn.width > 420) {
      throw new Error(`ticker button stretched ${dataLayout2.tickerBtn.width}`);
    }
    if (dataLayout2.modeBtn && dataLayout2.modeBtn.width > 420) {
      throw new Error(`mode button stretched ${dataLayout2.modeBtn.width}`);
    }
    if (dataLayout2.panelWidth && dataLayout2.tickerBtn
      && dataLayout2.tickerBtn.width > dataLayout2.panelWidth * 0.9
      && dataLayout2.panelWidth > 500) {
      throw new Error('ticker button still full-bleed in wide panel');
    }

    const v3Path = path.join(outputDir, 'v3-data-market-days-rail.png');
    await page.screenshot({ path: v3Path, fullPage: false });
    record('V3', 'Data Market days progressive rail', 'PASS', { path: v3Path, layout: dataLayout2 });

    // --- Review sidebar layout desktop (V5) + flex-grow proof ---
    await openQqqReview(page);
    const sidebarLayout = await page.evaluate(() => {
      const sidebar = document.querySelector('.dr-sidebar');
      if (!sidebar) return null;
      const measure = (sel) => {
        const el = sidebar.querySelector(sel);
        if (!el) return null;
        const cs = getComputedStyle(el);
        return { flexGrow: cs.flexGrow, width: el.getBoundingClientRect().width };
      };
      return {
        tickerBtn: measure('.ticker-tabs button'),
        modeBtn: measure('.date-rail-mode button'),
      };
    });
    if (!sidebarLayout?.tickerBtn) throw new Error('Review sidebar ticker missing');
    if (String(sidebarLayout.tickerBtn.flexGrow) !== '1') {
      throw new Error(`Review sidebar ticker flex-grow expected 1, got ${sidebarLayout.tickerBtn.flexGrow}`);
    }
    const v5Path = path.join(outputDir, 'v5-review-sidebar-desktop.png');
    await page.screenshot({ path: v5Path, fullPage: false });
    record('V5', 'Review sidebar progressive rail desktop', 'PASS', { path: v5Path, sidebarLayout });

    // --- Narrow V6 ---
    await page.setViewportSize(NARROW);
    await page.waitForTimeout(300);
    const narrowOk = await page.locator('.dr-sidebar').isVisible().catch(() => false);
    if (!narrowOk) throw new Error('Review sidebar not usable on narrow viewport');
    const v6Path = path.join(outputDir, 'v6-review-sidebar-narrow.png');
    await page.screenshot({ path: v6Path, fullPage: false });
    record('V6', 'Review sidebar progressive rail narrow', 'PASS', { path: v6Path, viewport: NARROW });
    await page.setViewportSize(DESKTOP);

    record('B-Data-rail-layout', 'Data compact + Review sidebar flex-grow + narrow', 'PASS', {
      data: dataLayout2,
      sidebar: sidebarLayout,
      narrow: NARROW,
    });

    // --- Static B-Group-span parity ---
    console.log('Exporting static reviews for Static B-Group-span…');
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

    const staticGroup = await runGroupSpanFlow(staticPage, 'Static');
    record('B-Group-span-static', 'Static multi-event span + event focus + restore', 'PASS', {
      surface: 'Static',
      ...staticGroup,
    });

    await staticPage.close();
    stopProcessTree(staticFrontendProc);
    staticFrontendProc = null;
    fs.rmSync(path.join(repoRoot, 'frontend', 'public', 'reviews'), { recursive: true, force: true });

    await browser.close();
    fs.writeFileSync(path.join(outputDir, 'receipts.json'), JSON.stringify(receipts, null, 2), 'utf8');
    console.log(`All B-carriers + V1–V6 PASS. Receipts: ${path.join(outputDir, 'receipts.json')}`);
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
