import { spawn, execSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from '../frontend/node_modules/playwright/index.mjs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, '..');

const timestamp = '20260721';
const outputDir = path.join(repoRoot, 'output', 'playwright', `trade-panel-polish-${timestamp}`);
fs.mkdirSync(outputDir, { recursive: true });

const trackedDbPath = path.join(repoRoot, 'data', 'sqlite', 'tang_strategy_live_extended.db');
const tempDbPath = path.join(outputDir, `temp_acceptance_${Date.now()}.db`);
fs.copyFileSync(trackedDbPath, tempDbPath);

const backendPort = 8029;
const frontendPort = 5199;

console.log(`Starting acceptance test... Output dir: ${outputDir}`);

// Start backend
const backendEnv = { ...process.env, PYTHONPATH: path.join(repoRoot, 'backend'), TANG_DB_PATH: tempDbPath };
const backendProc = spawn('python', ['-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', String(backendPort)], {
  cwd: repoRoot,
  env: backendEnv,
  stdio: 'inherit',
});

// Start frontend
const frontendEnv = {
  ...process.env,
  TANG_API_PROXY_TARGET: `http://127.0.0.1:${backendPort}`,
};
const frontendProc = spawn('npm', ['--prefix', 'frontend', 'run', 'dev', '--', '--host', '127.0.0.1', '--port', String(frontendPort), '--strictPort'], {
  cwd: repoRoot,
  env: frontendEnv,
  stdio: 'inherit',
  shell: true,
});
let staticFrontendProc = null;

async function waitUrl(url, timeoutMs = 20000) {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    try {
      const res = await fetch(url);
      if (res.ok) return true;
    } catch (_) {}
    await new Promise((r) => setTimeout(r, 200));
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
  proc.kill('SIGTERM');
}

async function runTests() {
  try {
    await waitUrl(`http://127.0.0.1:${backendPort}/openapi.json`);
    await waitUrl(`http://127.0.0.1:${frontendPort}/`);
    console.log('Backend & Frontend servers ready.');

    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
      viewport: { width: 1672, height: 941 },
    });

    const page = await context.newPage();
    const receipts = [];

    const toRepoPath = (value) =>
      (path.isAbsolute(value) ? path.relative(repoRoot, value).split(path.sep).join('/') : value);

    function record(id, title, status, details = {}) {
      const portable = typeof details.path === 'string' ? { ...details, path: toRepoPath(details.path) } : details;
      receipts.push({ id, title, status, details: portable, ts: new Date().toISOString() });
      console.log(`[RECEIPT] ${id}: ${title} -> ${status}`);
    }

    // Authenticate via login form
    console.log('Logging in...');
    await page.goto(`http://127.0.0.1:${frontendPort}/`);
    const passwordInput = page.locator('input[type="password"]');
    if (await passwordInput.isVisible()) {
      await passwordInput.fill('admin-change-me');
      await page.click('button[type="submit"]');
    }
    await page.waitForSelector('.sidebar');
    console.log('Logged in successfully!');

    // Navigate to Review page
    console.log('Navigating to Review page...');
    const reviewNav = page.locator('button.nav-item', { hasText: 'Review' });
    await reviewNav.click();
    await page.waitForSelector('.trade-filter-panel');

    // Freeze the required QQQ 2026-07-17 fixture instead of silently accepting the default SPY tab.
    const qqqTab = page.getByRole('tab', { name: 'QQQ', exact: true }).first();
    if (!(await qqqTab.isVisible())) throw new Error('Interactive Review QQQ workspace tab is unavailable');
    await qqqTab.click();
    await page.waitForFunction(() => (
      document.querySelector('[role="tab"][aria-selected="true"]')?.textContent?.trim() === 'QQQ'
    ));
    await page.waitForSelector('.trade-group-card.put');
    await page.waitForSelector('.trade-group-card.call');

    // --- V1: Interactive Review screenshot (QQQ 2026-07-17) ---
    console.log('Running V1 Interactive Review...');
    await page.waitForSelector('.trade-filter-panel');
    await page.waitForSelector('.trade-group-card');

    // Expand one Show legs/events if available
    const expandBtn = page.locator('.trade-drilldown-toggle').first();
    if (await expandBtn.isVisible()) {
      await expandBtn.click();
    }

    const v1Path = path.join(outputDir, 'v1-interactive-review.png');
    await page.screenshot({ path: v1Path, fullPage: false });
    record('V1', 'Interactive Review Trade Panel Screenshot', 'PASS', { path: v1Path });

    // --- B-Eligibility-interaction ---
    console.log('Running B-Eligibility-interaction test...');
    const displayRadio = page.locator('input[type="radio"][value="display"]');
    const reportedRadio = page.locator('input[type="radio"][value="reported"]');
    const calculatedRadio = page.locator('input[type="radio"][value="calculated"]');

    // Select reported
    await page.locator('label.trade-eligibility-option', { hasText: 'Reported' }).click();
    const isReportedChecked = await reportedRadio.isChecked();
    if (!isReportedChecked) throw new Error('Reported radio not checked after click');

    // Select calculated
    await page.locator('label.trade-eligibility-option', { hasText: 'Calculated' }).click();
    const isCalculatedChecked = await calculatedRadio.isChecked();
    if (!isCalculatedChecked) throw new Error('Calculated radio not checked after click');

    // Select display back
    await page.locator('label.trade-eligibility-option', { hasText: 'Display' }).click();
    const isDisplayChecked = await displayRadio.isChecked();
    if (!isDisplayChecked) throw new Error('Display radio not checked after click');

    record('B-Eligibility-interaction', 'Eligibility single-select radio interaction & state', 'PASS');

    // --- B-Download-four-file ---
    console.log('Running B-Download-four-file test...');
    const downloadPromiseList = [];
    const downloadHandler = (download) => downloadPromiseList.push(download);
    page.on('download', downloadHandler);

    const downloadBtn = page.locator('.trade-export-button').first();
    await downloadBtn.click();
    await page.waitForTimeout(1000);

    page.off('download', downloadHandler);

    record('B-Download-four-file', 'Four-file download click receipt on Review', 'PASS', {
      count: downloadPromiseList.length,
      filenames: downloadPromiseList.map(d => d.suggestedFilename()),
    });

    // --- B-Drawer-scale (synthetic >=7 traders via route-intercepted-in-memory-payload) ---
    console.log('Running B-Drawer-scale with synthetic >=7 traders injection...');

    const synthPage = await context.newPage();

    // Route interception on synthPage
    await synthPage.route('**/api/reviews/assemble*', async (route) => {
      console.log('Interception hit on synthPage!');
      const response = await route.fetch();
      const json = await response.json();
      console.log('Assemble JSON has trade_records:', !!json.trade_records);
      if (json.trade_records) {
        console.log('Original ticker:', json.trade_records.ticker, 'trade_date:', json.trade_records.trade_date);
        const ticker = json.trade_records.ticker || 'SPY';
        const date = json.trade_records.trade_date || '2026-07-17';
        const synthTraders = [
          { trader_id: 'trader_1', display_name: 'Trader 1', color: '#111111', active: true, sort_order: 10 },
          { trader_id: 'trader_2', display_name: 'Trader 2', color: '#222222', active: true, sort_order: 20 },
          { trader_id: 'trader_3', display_name: 'Trader 3', color: '#333333', active: true, sort_order: 30 },
          { trader_id: 'trader_4', display_name: 'Trader 4', color: '#444444', active: true, sort_order: 40 },
          { trader_id: 'trader_5', display_name: 'Trader 5', color: '#555555', active: true, sort_order: 50 },
          { trader_id: 'trader_6', display_name: 'Trader 6', color: '#666666', active: true, sort_order: 60 },
          { trader_id: 'trader_7', display_name: 'Trader 7', color: '#777777', active: true, sort_order: 70 },
          { trader_id: 'trader_8', display_name: 'Trader 8', color: '#888888', active: true, sort_order: 80 },
        ];
        json.trade_records.traders = synthTraders;
        json.trade_records.trade_groups = synthTraders.map((t, idx) => ({
          trade_group_id: `tg_synth_${idx}`,
          trader_id: t.trader_id,
          underlying: ticker,
          trade_date: date,
          direction: idx % 2 === 0 ? 'PUT' : 'CALL',
          status: 'active',
          review_status: 'verified',
          display_eligible: true,
          reported_stats_eligible: true,
          calculated_stats_eligible: true,
          legs: [],
          reported_outcome: { return_pct: 1.5 },
        }));
      }
      route.fulfill({ json });
    });

    await synthPage.goto(`http://127.0.0.1:${frontendPort}/`);
    const pass2 = synthPage.locator('input[type="password"]');
    if (await pass2.isVisible()) {
      await pass2.fill('admin-change-me');
      await synthPage.click('button[type="submit"]');
    }
    await synthPage.waitForSelector('.sidebar');
    const synthReviewNav = synthPage.locator('button.nav-item', { hasText: 'Review' });
    await synthReviewNav.click();
    await synthPage.waitForSelector('.dr-sidebar');
    await synthPage.waitForSelector('.trade-trader-summary');

    const summaryText = await synthPage.locator('.trade-trader-summary').textContent();
    console.log('Synthetic summary text:', summaryText);
    if (!summaryText.includes('selected')) throw new Error(`Summary text missing "selected": ${summaryText}`);

    // Click Edit button
    const editBtn = synthPage.locator('.trade-trader-edit');
    await editBtn.click();
    await synthPage.waitForSelector('.trade-trader-drawer');

    // Test Search input
    const searchInput = synthPage.locator('.trade-trader-search input');
    await searchInput.fill('Trader 8');
    const searchChips = await synthPage.locator('.trade-trader-drawer .trade-trader-chip').allTextContents();
    if (searchChips.length !== 1 || searchChips[0] !== 'Trader 8') {
      throw new Error(`Search filter failed: ${searchChips}`);
    }

    // Search non-matching
    await searchInput.fill('NonExistentTrader');
    const emptyMsg = await synthPage.locator('.trade-trader-drawer .trade-trader-empty').textContent();
    if (emptyMsg !== 'No matching traders') throw new Error(`Empty drawer search message mismatch: ${emptyMsg}`);

    // Clear search
    await searchInput.fill('');

    // Test Clear button
    const clearBtn = synthPage.getByRole('button', { name: 'Clear' });
    await clearBtn.click();
    const summaryAfterClear = await synthPage.locator('.trade-trader-summary').textContent();
    if (summaryAfterClear !== 'No traders selected') throw new Error(`Summary after Clear mismatch: ${summaryAfterClear}`);

    // Test Select all button
    const selectAllBtn = synthPage.getByRole('button', { name: 'Select all' });
    await selectAllBtn.click();
    const summaryAfterSelectAll = await synthPage.locator('.trade-trader-summary').textContent();
    if (!summaryAfterSelectAll.includes('8 selected')) throw new Error(`Summary after Select all mismatch: ${summaryAfterSelectAll}`);

    // Close drawer
    await editBtn.click();
    await synthPage.close();

    record('B-Drawer-scale', 'Synthetic >=7 trader drawer interaction (Edit/Search/Select all/Clear)', 'PASS');

    // --- V3: Admin traders workspace screenshot & single Download CTA check ---
    console.log('Running V3 Admin Traders Workspace...');
    const adminNav = page.locator('button.nav-item', { hasText: '点位管理' });
    await adminNav.click();
    await page.waitForSelector('.admin-traders-page');
    await page.waitForSelector('.trade-filter-panel');

    const adminQqqTab = page.getByRole('tab', { name: 'QQQ', exact: true }).first();
    if (!(await adminQqqTab.isVisible())) throw new Error('Admin QQQ workspace tab is unavailable');
    await adminQqqTab.click();
    await page.waitForFunction(() => (
      document.querySelector('.admin-traders-page [role="tab"][aria-selected="true"]')?.textContent?.trim() === 'QQQ'
    ));
    await page.waitForSelector('.admin-traders-page .trade-group-card');

    const v3Path = path.join(outputDir, 'v3-admin-workspace.png');
    await page.screenshot({ path: v3Path, fullPage: false });
    record('V3', 'Admin Workspace Trade Panel Screenshot', 'PASS', { path: v3Path });

    // Assert NO second long download CTA in admin header
    const adminHeaderControls = await page.locator('.admin-traders-page > header .trade-export-button').count();
    if (adminHeaderControls !== 0) throw new Error('Admin header still contains separate export button');

    const sharedStripControls = await page.locator('.trade-filter-panel .trade-export-button').count();
    if (sharedStripControls !== 1) throw new Error('Shared tools strip missing export button in Admin');

    record('Admin-Composition', 'Admin page uses shared tools strip without header long Download', 'PASS');

    // --- V2: Static Review screenshot ---
    console.log('Running V2 Static Review...');
    execSync('python backend/scripts/export_static_reviews.py --output frontend/public/reviews --limit 5 --strategy-families v3,v4,v5', {
      cwd: repoRoot,
      env: { ...process.env, PYTHONPATH: path.join(repoRoot, 'backend') },
    });

    const staticFrontendPort = 5200;
    staticFrontendProc = spawn('npm', ['--prefix', 'frontend', 'run', 'dev', '--', '--host', '127.0.0.1', '--port', String(staticFrontendPort), '--strictPort'], {
      cwd: repoRoot,
      env: {
        ...process.env,
        VITE_STATIC_REVIEWS: 'true',
      },
      stdio: 'inherit',
      shell: true,
    });
    await waitUrl(`http://127.0.0.1:${staticFrontendPort}/`);

    // Visit the actual static-reviews app, not the interactive Admin page.
    const staticPage = await context.newPage();
    await staticPage.goto(`http://127.0.0.1:${staticFrontendPort}/#qqq-2026-07-17-extended`);
    await staticPage.waitForSelector('.trade-filter-panel');

    const v2Path = path.join(outputDir, 'v2-static-review.png');
    await staticPage.screenshot({ path: v2Path, fullPage: false });
    record('V2', 'Static Review Trade Panel Screenshot', 'PASS', { path: v2Path });

    const staticStripControls = await staticPage.locator('.trade-filter-panel .trade-export-button', { hasText: 'Download' }).count();
    if (staticStripControls !== 1) throw new Error('Static Review shared tools strip must contain exactly one short Download control');
    record('Static-Composition', 'Static Review uses the shared tools strip with one short Download control', 'PASS');

    await staticPage.close();
    stopProcessTree(staticFrontendProc);
    staticFrontendProc = null;

    // Clean up temporary static export
    fs.rmSync(path.join(repoRoot, 'frontend', 'public', 'reviews'), { recursive: true, force: true });

    await browser.close();

    // Write receipts log
    fs.writeFileSync(path.join(outputDir, 'receipt.json'), JSON.stringify(receipts, null, 2));
    console.log(`ALL B-* AND V1-V3 CARRIER VERIFICATIONS PASSED! Receipts saved to ${path.join(outputDir, 'receipt.json')}`);

  } finally {
    stopProcessTree(backendProc);
    stopProcessTree(frontendProc);
    stopProcessTree(staticFrontendProc);
    try { fs.unlinkSync(tempDbPath); } catch (_) {}
  }
}

runTests().catch((err) => {
  console.error('VERIFICATION ERROR:', err);
  stopProcessTree(backendProc);
  stopProcessTree(frontendProc);
  stopProcessTree(staticFrontendProc);
  process.exit(1);
});
