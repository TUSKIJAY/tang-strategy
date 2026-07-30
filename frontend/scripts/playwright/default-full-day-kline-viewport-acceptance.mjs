/**
 * Focused browser acceptance for the Default Full-Day K-Line Viewport plan
 * (docs/exec-plans/active/2026-07-30-tang-strategy-default-full-day-kline-viewport-plan.md).
 * Exercises every row of plan §4's acceptance table against real running
 * backend/frontend instances and a COPIED (never the tracked) SQLite DB.
 * Receipts under untracked output/playwright/default-full-day-kline-viewport-<timestamp>/
 */
import { spawn, execSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { chromium } from '../../node_modules/playwright/index.mjs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
// frontend/scripts/playwright → repo root is three levels up
const repoRoot = path.resolve(__dirname, '../../..');

const timestamp = new Date().toISOString().replace(/[-:TZ.]/g, '').slice(0, 14);
const outputDir = path.join(repoRoot, 'output', 'playwright', `default-full-day-kline-viewport-${timestamp}`);
fs.mkdirSync(outputDir, { recursive: true });

const trackedDbPath = path.join(repoRoot, 'data', 'sqlite', 'tang_strategy_live_extended.db');
const tempDbPath = path.join(outputDir, `temp_acceptance_${Date.now()}.db`);
const trackedDbShaBefore = sha256File(trackedDbPath);
fs.copyFileSync(trackedDbPath, tempDbPath);

const backendPort = 8045;
const frontendPort = 5215;
const staticFrontendPort = 5216;
const DESKTOP = { width: 1672, height: 941 };

const pythonBin = fs.existsSync(path.join(repoRoot, 'backend', '.venv', 'bin', 'python'))
  ? path.join(repoRoot, 'backend', '.venv', 'bin', 'python')
  : 'python3';

console.log(`Starting acceptance… Output: ${outputDir}`);

function sha256File(filePath) {
  const digest = crypto.createHash('sha256');
  digest.update(fs.readFileSync(filePath));
  return digest.digest('hex');
}

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
    await passwordInput.fill('readonly-change-me');
    await page.click('button[type="submit"]');
  }
  await page.waitForSelector('.sidebar', { timeout: 20000 });
}

async function openReview(page) {
  const reviewNav = page.locator('button.nav-item', { hasText: 'Review' });
  await reviewNav.click();
  await page.waitForSelector('.unified-kline-engine', { timeout: 30000 });
  await page.waitForFunction(() => {
    const el = document.querySelector('.unified-kline-engine');
    return Boolean(el && el.__klineEngine && typeof el.__klineEngine.getViewportDebug === 'function');
  }, null, { timeout: 30000 });
  // Wait for the first real bar payload (not the empty 0-bar boot state).
  await page.waitForFunction(() => {
    const el = document.querySelector('.unified-kline-engine');
    return (el?.__klineEngine?.dataManager?.getBars?.('1m')?.length || 0) > 0;
  }, null, { timeout: 30000 });
}

async function readEngineDebug(page) {
  return page.evaluate(() => {
    const el = document.querySelector('.unified-kline-engine');
    if (!el?.__klineEngine?.getViewportDebug) return null;
    return el.__klineEngine.getViewportDebug();
  });
}

async function readBarCounts(page) {
  return page.evaluate(() => {
    const el = document.querySelector('.unified-kline-engine');
    const engine = el.__klineEngine;
    return {
      bars1m: engine.dataManager.getBars('1m').length,
      bars5m: engine.dataManager.getBars('5m').length,
    };
  });
}

async function clickTimeframe(page, tf) {
  await page.locator(`.kline-engine__button[data-action="timeframe"][data-timeframe="${tf}"]`).first().click();
  await page.waitForTimeout(120);
}

async function run() {
  const receipts = [];
  const toRepoPath = (value) =>
    (path.isAbsolute(value) ? path.relative(repoRoot, value).split(path.sep).join('/') : value);

  const record = (id, title, status, details = {}) => {
    const portable = typeof details.path === 'string' ? { ...details, path: toRepoPath(details.path) } : details;
    receipts.push({ id, title, status, details: portable, ts: new Date().toISOString() });
    console.log(`[RECEIPT] ${id}: ${title} -> ${status}`);
  };

  const assertViewport = (label, debug, expected) => {
    if (!debug) throw new Error(`${label}: getViewportDebug returned null`);
    if (debug.start !== expected.start || debug.end !== expected.end || debug.count !== expected.count) {
      throw new Error(
        `${label}: expected {start:${expected.start},end:${expected.end},count:${expected.count}}, `
        + `got {start:${debug.start},end:${debug.end},count:${debug.count}}`,
      );
    }
  };

  try {
    await waitUrl(`http://127.0.0.1:${backendPort}/openapi.json`);
    await waitUrl(`http://127.0.0.1:${frontendPort}/`);
    console.log('Backend & Frontend ready');

    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({ viewport: DESKTOP });
    const page = await context.newPage();

    await login(page, `http://127.0.0.1:${frontendPort}`);
    await openReview(page);

    // --- Row 1/2: Review 1m/5m first paint fits every available bar ---
    const counts = await readBarCounts(page);
    const debug1m = await readEngineDebug(page);
    assertViewport('Review 1m first paint', debug1m, { start: 0, end: counts.bars1m - 1, count: counts.bars1m });
    record('Review-1m-first-paint', 'Review 1m first paint fits every available bar', 'PASS', {
      bars1m: counts.bars1m,
      debug: debug1m,
    });

    await clickTimeframe(page, '5m');
    const debug5m = await readEngineDebug(page);
    assertViewport('Review 5m first paint (via TF switch)', debug5m, { start: 0, end: counts.bars5m - 1, count: counts.bars5m });
    record('Review-5m-first-paint', 'Review 5m (timeframe switch) fits every available bar', 'PASS', {
      bars5m: counts.bars5m,
      debug: debug5m,
    });

    const v1Path = path.join(outputDir, 'v1-review-5m-full-day.png');
    await page.screenshot({ path: v1Path, fullPage: false });
    record('V1', 'Review 5m full-day first paint', 'PASS', { path: v1Path });

    await clickTimeframe(page, '1m');
    const debug1mAgain = await readEngineDebug(page);
    assertViewport('Review 1m after switching back', debug1mAgain, { start: 0, end: counts.bars1m - 1, count: counts.bars1m });
    record('Review-1m-after-tf-roundtrip', '1m -> 5m -> 1m roundtrip still fits every bar', 'PASS', { debug: debug1mAgain });

    // --- Row 6: manual zoom can still narrow the viewport ---
    const zoomInBtn = page.locator('.kline-engine__button[data-action="zoom-in"]').first();
    await zoomInBtn.click();
    await zoomInBtn.click();
    await zoomInBtn.click();
    await page.waitForTimeout(120);
    const debugZoomed = await readEngineDebug(page);
    if (debugZoomed.count >= counts.bars1m) {
      throw new Error(`manual zoom-in did not narrow the viewport: count=${debugZoomed.count} (total=${counts.bars1m})`);
    }
    record('Manual-zoom-narrows', 'Manual +Zoom produces a narrower viewport than full-day', 'PASS', { debug: debugZoomed });

    const v2Path = path.join(outputDir, 'v2-review-zoomed-in.png');
    await page.screenshot({ path: v2Path, fullPage: false });
    record('V2', 'Review after manual zoom-in (narrower than full day)', 'PASS', { path: v2Path });

    // --- Row 3: Overview restores every available bar after a manual zoom ---
    const overviewBtn = page.locator('.kline-engine__button[data-action="overview"]').first();
    await overviewBtn.click();
    await page.waitForTimeout(120);
    const debugAfterOverview = await readEngineDebug(page);
    assertViewport('Overview after manual zoom', debugAfterOverview, { start: 0, end: counts.bars1m - 1, count: counts.bars1m });
    record('Overview-restores-full-day', 'Overview restores the full day after a manual zoom', 'PASS', { debug: debugAfterOverview });

    const v3Path = path.join(outputDir, 'v3-review-after-overview.png');
    await page.screenshot({ path: v3Path, fullPage: false });
    record('V3', 'Review after clicking Overview (restored full day)', 'PASS', { path: v3Path });

    // --- Row 5: variable (non-390/78) payload length via the real Ext-K toggle ---
    // The toggle lives inside the collapsible "Review 工具" utility panel.
    await page.locator('.dr-review-utility-trigger').first().click();
    await page.waitForTimeout(120);
    const extKToggle = page.locator('.dr-toggle-switch', { hasText: 'Ext K' }).first();
    await extKToggle.click();
    await page.waitForTimeout(300);
    const extKCounts = await readBarCounts(page);
    const debugExtK = await readEngineDebug(page);
    if (extKCounts.bars1m === counts.bars1m) {
      throw new Error(`Ext-K toggle did not change the 1m bar count (still ${extKCounts.bars1m}); cannot exercise a variable-length payload`);
    }
    assertViewport('Ext-K variable-length payload', debugExtK, { start: 0, end: extKCounts.bars1m - 1, count: extKCounts.bars1m });
    record('Variable-length-fits-actual-count', 'A non-390/78 payload (Ext-K window) fits its own actual bar count, not a fixed 390/78', 'PASS', {
      rthBars1m: counts.bars1m,
      extKBars1m: extKCounts.bars1m,
      debug: debugExtK,
    });
    await extKToggle.click();
    await page.waitForTimeout(300);

    // --- Row 5b: synthetic non-standard payload loaded directly, for a fully controlled oracle ---
    const syntheticDebug = await page.evaluate(() => {
      const el = document.querySelector('.unified-kline-engine');
      const engine = el.__klineEngine;
      function makeBars(n) {
        const bars = [];
        for (let i = 0; i < n; i += 1) {
          const minute = 30 + i;
          const hh = String(9 + Math.floor(minute / 60)).padStart(2, '0');
          const mm = String(minute % 60).padStart(2, '0');
          bars.push({ t: `${hh}:${mm}`, O: 100 + i, H: 101 + i, L: 99 + i, C: 100.5 + i, V: 1000 + i });
        }
        return bars;
      }
      const N1M = 53;
      const N5M = 11;
      engine.loadData({
        meta: { date: '2026-07-27', initial_timeframe: '1m', initial_index_1m: N1M - 1, initial_index_5m: N5M - 1 },
        bars_1m: makeBars(N1M),
        bars_5m: makeBars(N5M),
        annotations_1m: [],
        annotations_5m: [],
      });
      const first1m = engine.getViewportDebug();
      engine.setTimeframe('5m');
      const after5m = engine.getViewportDebug();
      return { N1M, N5M, first1m, after5m };
    });
    assertViewport('Synthetic 53-bar 1m payload', syntheticDebug.first1m, { start: 0, end: syntheticDebug.N1M - 1, count: syntheticDebug.N1M });
    assertViewport('Synthetic 11-bar 5m payload', syntheticDebug.after5m, { start: 0, end: syntheticDebug.N5M - 1, count: syntheticDebug.N5M });
    record('Variable-length-synthetic', 'A synthetic 53/11-bar payload fits its exact actual length (no 390/78 hard-coding)', 'PASS', syntheticDebug);

    // Reload the real Review payload for the rest of the run (synthetic loadData above replaced it in-place).
    await page.reload();
    await openReview(page);

    // --- Row 4: Static Review parity ---
    console.log('Exporting static reviews for Static parity…');
    execSync(
      `${JSON.stringify(pythonBin)} backend/scripts/export_static_reviews.py --output frontend/public/reviews --limit 20 --strategy-families v3,v4,v5`,
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
    await staticPage.setViewportSize(DESKTOP);
    await staticPage.goto(`http://127.0.0.1:${staticFrontendPort}/#spy-2026-07-27-extended`);
    await staticPage.waitForSelector('.unified-kline-engine', { timeout: 30000 });
    await staticPage.waitForFunction(() => {
      const el = document.querySelector('.unified-kline-engine');
      return Boolean(el && el.__klineEngine && typeof el.__klineEngine.getViewportDebug === 'function'
        && (el.__klineEngine.dataManager.getBars('1m').length > 0));
    }, null, { timeout: 30000 });

    const staticCounts = await staticPage.evaluate(() => {
      const el = document.querySelector('.unified-kline-engine');
      const engine = el.__klineEngine;
      return { bars1m: engine.dataManager.getBars('1m').length, bars5m: engine.dataManager.getBars('5m').length };
    });
    const staticDebug1m = await staticPage.evaluate(() => document.querySelector('.unified-kline-engine').__klineEngine.getViewportDebug());
    assertViewport('Static Review 1m first paint', staticDebug1m, { start: 0, end: staticCounts.bars1m - 1, count: staticCounts.bars1m });

    await staticPage.locator('.kline-engine__button[data-action="timeframe"][data-timeframe="5m"]').first().click();
    await staticPage.waitForTimeout(120);
    const staticDebug5m = await staticPage.evaluate(() => document.querySelector('.unified-kline-engine').__klineEngine.getViewportDebug());
    assertViewport('Static Review 5m (timeframe switch)', staticDebug5m, { start: 0, end: staticCounts.bars5m - 1, count: staticCounts.bars5m });

    await staticPage.locator('.kline-engine__button[data-action="zoom-in"]').first().click();
    await staticPage.locator('.kline-engine__button[data-action="zoom-in"]').first().click();
    await staticPage.waitForTimeout(120);
    const staticDebugZoomed = await staticPage.evaluate(() => document.querySelector('.unified-kline-engine').__klineEngine.getViewportDebug());
    if (staticDebugZoomed.count >= staticCounts.bars5m) {
      throw new Error(`Static Review manual zoom did not narrow the viewport: count=${staticDebugZoomed.count}`);
    }
    await staticPage.locator('.kline-engine__button[data-action="overview"]').first().click();
    await staticPage.waitForTimeout(120);
    const staticDebugOverview = await staticPage.evaluate(() => document.querySelector('.unified-kline-engine').__klineEngine.getViewportDebug());
    assertViewport('Static Review Overview restore', staticDebugOverview, { start: 0, end: staticCounts.bars5m - 1, count: staticCounts.bars5m });

    const v4Path = path.join(outputDir, 'v4-static-review-full-day.png');
    await staticPage.screenshot({ path: v4Path, fullPage: false });
    record('V4', 'Static Review full-day parity (1m/5m first paint, zoom, Overview)', 'PASS', { path: v4Path });
    record('Static-parity', 'Static Review matches interactive Review for first paint, TF switch, zoom, and Overview', 'PASS', {
      staticCounts,
      staticDebug1m,
      staticDebug5m,
      staticDebugZoomed,
      staticDebugOverview,
    });

    await staticPage.close();
    stopProcessTree(staticFrontendProc);
    staticFrontendProc = null;
    fs.rmSync(path.join(repoRoot, 'frontend', 'public', 'reviews'), { recursive: true, force: true });

    // --- Row 7: Teaching keeps its reveal-cutoff/follow behavior ---
    const teachingNav = page.locator('button.nav-item', { hasText: 'Teaching' });
    await teachingNav.click();
    await page.waitForSelector('.unified-kline-engine', { timeout: 30000 });
    await page.waitForFunction(() => {
      const el = document.querySelector('.unified-kline-engine');
      return Boolean(el?.__klineEngine?.dataManager?.getBars?.('1m')?.length);
    }, null, { timeout: 30000 });

    const teachingState = await page.evaluate(() => {
      const el = document.querySelector('.unified-kline-engine');
      const engine = el.__klineEngine;
      const bars = engine.dataManager.getBars('1m');
      return {
        totalBars: bars.length,
        revealCutoff1m: engine.revealCutoff['1m'],
        currentIndex: engine.currentIndex,
        options: engine.options.initialViewport,
      };
    });
    if (teachingState.options !== 'default') {
      throw new Error(`Teaching engine.options.initialViewport expected 'default', got '${teachingState.options}'`);
    }
    if (teachingState.revealCutoff1m == null || teachingState.revealCutoff1m >= teachingState.totalBars - 1) {
      throw new Error(
        `Teaching reveal cutoff not bounding future bars: cutoff=${teachingState.revealCutoff1m}, totalBars=${teachingState.totalBars}`,
      );
    }
    if (teachingState.currentIndex > teachingState.revealCutoff1m) {
      throw new Error(`Teaching currentIndex (${teachingState.currentIndex}) exceeds reveal cutoff (${teachingState.revealCutoff1m})`);
    }
    record('Teaching-reveal-cutoff-preserved', 'Teaching keeps its default engine options, reveal cutoff, and bounded current index', 'PASS', teachingState);

    const advanceBtn = page.locator('button', { hasText: 'Advance one bar' }).first();
    await advanceBtn.click();
    await page.waitForTimeout(150);
    const teachingAfterAdvance = await page.evaluate(() => {
      const el = document.querySelector('.unified-kline-engine');
      const engine = el.__klineEngine;
      return { revealCutoff1m: engine.revealCutoff['1m'], currentIndex: engine.currentIndex };
    });
    if (teachingAfterAdvance.revealCutoff1m <= teachingState.revealCutoff1m) {
      throw new Error(
        `Advance one bar did not move the reveal cutoff forward: before=${teachingState.revealCutoff1m}, after=${teachingAfterAdvance.revealCutoff1m}`,
      );
    }
    if (teachingAfterAdvance.currentIndex > teachingAfterAdvance.revealCutoff1m) {
      throw new Error('Teaching currentIndex exceeded reveal cutoff after Advance one bar');
    }
    record('Teaching-step-bounded', 'Advance one bar moves the cutoff forward and keeps currentIndex bounded by it', 'PASS', teachingAfterAdvance);

    const v5Path = path.join(outputDir, 'v5-teaching-reveal-cutoff.png');
    await page.screenshot({ path: v5Path, fullPage: false });
    record('V5', 'Teaching replay reveal-cutoff intact after the viewport change', 'PASS', { path: v5Path });

    // --- Row 8: Data safety — tracked DB untouched throughout the run ---
    const trackedDbShaAfter = sha256File(trackedDbPath);
    if (trackedDbShaAfter !== trackedDbShaBefore) {
      throw new Error(`Tracked SQLite DB hash changed during acceptance: before=${trackedDbShaBefore} after=${trackedDbShaAfter}`);
    }
    record('Data-safety-db-hash-unchanged', 'Tracked SQLite DB SHA-256 unchanged across the acceptance run', 'PASS', {
      sha256: trackedDbShaAfter,
    });

    await browser.close();
    fs.writeFileSync(path.join(outputDir, 'receipts.json'), JSON.stringify(receipts, null, 2), 'utf8');
    console.log(`All acceptance rows PASS. Receipts: ${path.join(outputDir, 'receipts.json')}`);
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
    // Scratch DB dies with the run; receipts.json and screenshots are the durable evidence.
    for (const stale of [tempDbPath, `${tempDbPath}.write.lock`]) {
      fs.rmSync(stale, { force: true });
    }
  }
}

run()
  .then((code) => process.exit(code || 0))
  .catch(() => process.exit(1));
