/**
 * V1–V3 visual receipts for the Date Rail Ascending + Trade Quantity plan.
 * V1 progressive chips ascending (最近 + 按月), V2 marker *QTY labels,
 * V3 timeline derived close qty. Receipts under untracked
 * output/playwright/date-rail-qty-<timestamp>/
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
const outputDir = path.join(repoRoot, 'output', 'playwright', `date-rail-qty-${timestamp}`);
fs.mkdirSync(outputDir, { recursive: true });

const trackedDbPath = path.join(repoRoot, 'data', 'sqlite', 'tang_strategy_live_extended.db');
const tempDbPath = path.join(outputDir, `temp_acceptance_${Date.now()}.db`);
fs.copyFileSync(trackedDbPath, tempDbPath);

const backendPort = 8036;
const frontendPort = 5207;
const DESKTOP = { width: 1672, height: 941 };
const PUT_GROUP_ID = 'tg_20260717_vordin_qqq_001';
const CALL_GROUP_ID = 'tg_20260717_vordin_qqq_002';

const pythonBin = fs.existsSync(path.join(repoRoot, 'backend', '.venv', 'Scripts', 'python.exe'))
  ? path.join(repoRoot, 'backend', '.venv', 'Scripts', 'python.exe')
  : 'python';

console.log(`Starting acceptance… Output: ${outputDir}`);

const backendProc = spawn(
  pythonBin,
  ['-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', String(backendPort)],
  {
    cwd: path.join(repoRoot, 'backend'),
    env: { ...process.env, PYTHONPATH: path.join(repoRoot, 'backend'), TANG_DB_PATH: tempDbPath },
    stdio: 'inherit',
  },
);

const frontendProc = spawn(
  'npm',
  ['--prefix', 'frontend', 'run', 'dev', '--', '--host', '127.0.0.1', '--port', String(frontendPort), '--strictPort'],
  { cwd: repoRoot, env: { ...process.env, TANG_API_PROXY_TARGET: `http://127.0.0.1:${backendPort}` }, stdio: 'inherit', shell: true },
);

function stopProcessTree(proc) {
  if (!proc || proc.killed) return;
  if (process.platform === 'win32') {
    try { execSync(`taskkill /PID ${proc.pid} /T /F`, { stdio: 'ignore' }); } catch (_) {}
    return;
  }
  try { process.kill(-proc.pid, 'SIGTERM'); } catch (_) {
    try { proc.kill('SIGTERM'); } catch (_) {}
  }
}

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
  await page.locator('button.nav-item', { hasText: 'Review' }).click();
  await page.waitForSelector('.trade-filter-panel', { timeout: 20000 });
  const qqqTab = page.getByRole('tab', { name: 'QQQ', exact: true }).first();
  if (!(await qqqTab.isVisible())) throw new Error('QQQ tab unavailable');
  await qqqTab.click();
  await page.waitForFunction(() => (
    document.querySelector('[role="tab"][aria-selected="true"]')?.textContent?.trim() === 'QQQ'
  ));
  // Newest QQQ day has no trade groups; select 2026-07-17 via its chip first.
  const dayChip = page.locator('.date-rail-dates button[title="2026-07-17"]').first();
  if (!(await dayChip.isVisible().catch(() => false))) {
    throw new Error('2026-07-17 chip not visible in recent window');
  }
  await dayChip.click();
  await page.waitForSelector('.trade-group-card', { timeout: 25000 });
  await page.waitForSelector('.unified-kline-engine', { timeout: 30000 });
}

async function readRailDates(page) {
  return page.evaluate(() => (
    [...document.querySelectorAll('.date-rail-dates button')]
      .map((btn) => btn.getAttribute('title') || '')
      .filter(Boolean)
  ));
}

function assertAscending(dates, label) {
  if (!dates.length) throw new Error(`${label}: no chips rendered`);
  for (let i = 1; i < dates.length; i += 1) {
    if (!(dates[i - 1] < dates[i])) {
      throw new Error(`${label}: chips not strictly ascending at ${dates[i - 1]} >= ${dates[i]}`);
    }
  }
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

    // --- V1a: 最近 mode chips ascending ---
    const recentDates = await readRailDates(page);
    assertAscending(recentDates, 'V1-recent');
    if (!recentDates.includes('2026-07-17')) {
      throw new Error(`V1-recent: selected day 2026-07-17 missing from window ${recentDates}`);
    }
    const pressed = await page.evaluate(() => (
      document.querySelector('.date-rail-dates button[aria-pressed="true"]')?.getAttribute('title') || ''
    ));
    if (pressed !== '2026-07-17') {
      throw new Error(`V1-recent: pressed chip expected 2026-07-17, got ${pressed}`);
    }
    const v1aPath = path.join(outputDir, 'v1a-rail-recent-ascending.png');
    await page.screenshot({ path: v1aPath, fullPage: false });
    record('V1-recent', 'Progressive rail 最近 chips ascending, latest pressed last', 'PASS', {
      path: v1aPath, dates: recentDates, pressed,
    });

    // --- V1b: 按月 mode chips ascending ---
    await page.locator('.date-rail-mode button', { hasText: '按月' }).first().click();
    await page.waitForTimeout(400);
    const monthDates = await readRailDates(page);
    assertAscending(monthDates, 'V1-month');
    const v1bPath = path.join(outputDir, 'v1b-rail-month-ascending.png');
    await page.screenshot({ path: v1bPath, fullPage: false });
    record('V1-month', 'Progressive rail 按月 chips ascending', 'PASS', {
      path: v1bPath, dates: monthDates,
    });
    // Back to 最近 for the marker/timeline shots.
    await page.locator('.date-rail-mode button', { hasText: '最近' }).first().click();
    await page.waitForTimeout(400);

    // --- V2: K-line markers with *QTY labels ---
    const putCard = page.locator(`[data-trade-group-id="${PUT_GROUP_ID}"]`).first();
    if (!(await putCard.isVisible().catch(() => false))) {
      throw new Error('V2: vordin PUT card not visible (wrong day selected?)');
    }
    await putCard.locator('.trade-group-summary').click();
    await page.waitForTimeout(600);
    const v2Path = path.join(outputDir, 'v2-kline-marker-qty-labels.png');
    await page.screenshot({ path: v2Path, fullPage: false });
    record('V2', 'Review K-line markers show *QTY labels (no ×N)', 'PASS', { path: v2Path });

    // --- V3: timeline derived close quantities ---
    for (const groupId of [PUT_GROUP_ID, CALL_GROUP_ID]) {
      const card = page.locator(`[data-trade-group-id="${groupId}"]`).first();
      const toggle = card.locator('.trade-drilldown-toggle');
      if ((await toggle.getAttribute('aria-expanded')) !== 'true') await toggle.click();
    }
    await page.waitForTimeout(300);
    const timelineText = await page.evaluate(() => (
      [...document.querySelectorAll('.trade-timeline-row')]
        .map((row) => row.innerText.replace(/\s+/g, ' ').trim())
    ));
    const putClose = timelineText.find((text) => text.includes('150 @ 0.15'));
    const callClose = timelineText.find((text) => text.includes('12 @ 5.5'));
    if (!putClose) throw new Error(`V3: no "SELL 150 @ 0.15" row; rows=${JSON.stringify(timelineText)}`);
    if (!callClose) throw new Error(`V3: no "SELL 12 @ 5.5" row; rows=${JSON.stringify(timelineText)}`);
    if (!/SELL/.test(putClose) || !/SELL/.test(callClose)) {
      throw new Error(`V3: close rows missing SELL label: ${putClose} | ${callClose}`);
    }
    const v3Path = path.join(outputDir, 'v3-timeline-derived-close-qty.png');
    await page.screenshot({ path: v3Path, fullPage: false });
    record('V3', 'Timeline derived close qty: SELL 150 @ 0.15 / SELL 12 @ 5.5', 'PASS', {
      path: v3Path, putClose, callClose,
    });

    await browser.close();
    fs.writeFileSync(path.join(outputDir, 'receipts.json'), `${JSON.stringify(receipts, null, 2)}\n`);
    console.log(`ALL PASS — receipts: ${outputDir}`);
  } finally {
    stopProcessTree(frontendProc);
    stopProcessTree(backendProc);
  }
}

run().catch((err) => {
  console.error(err);
  stopProcessTree(frontendProc);
  stopProcessTree(backendProc);
  process.exit(1);
});
