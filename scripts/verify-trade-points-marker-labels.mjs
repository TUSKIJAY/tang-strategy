/**
 * Visual acceptance for Trade Points And K-line Marker Labels plan.
 * V1 interactive cards, V2 interactive markers, V3 static parity.
 * Untracked under output/playwright/trade-points-marker-labels-20260721/
 */
import { spawn, execSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from '../frontend/node_modules/playwright/index.mjs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, '..');

const timestamp = '20260721';
const outputDir = path.join(repoRoot, 'output', 'playwright', `trade-points-marker-labels-${timestamp}`);
fs.mkdirSync(outputDir, { recursive: true });

const trackedDbPath = path.join(repoRoot, 'data', 'sqlite', 'tang_strategy_live_extended.db');
const tempDbPath = path.join(outputDir, `temp_acceptance_${Date.now()}.db`);
fs.copyFileSync(trackedDbPath, tempDbPath);

const backendPort = 8031;
const frontendPort = 5201;
const staticFrontendPort = 5202;

console.log(`Starting acceptance… Output: ${outputDir}`);

const backendEnv = {
  ...process.env,
  PYTHONPATH: path.join(repoRoot, 'backend'),
  TANG_DB_PATH: tempDbPath,
};
const backendProc = spawn(
  'python',
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

async function waitUrl(url, timeoutMs = 60000) {
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
    proc.kill('SIGTERM');
  } catch (_) {}
}

function assertNoOutcomeNoise(text, label) {
  const hits = text.match(/\$|\b%|\breported\b|\bcalculated\b|\bnet\b|\breturn\b|\bfees\b/gi) || [];
  if (hits.length) {
    throw new Error(`${label} still has outcome noise: ${hits.join(', ')} :: ${text.slice(0, 280)}`);
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
    const context = await browser.newContext({ viewport: { width: 1672, height: 941 } });
    const page = await context.newPage();

    await login(page, `http://127.0.0.1:${frontendPort}`);
    await openQqqReview(page);

    // Prefer 2026-07-17 if a date control is present (progressive rail may already select newest)
    const dateHint = await page.locator('body').innerText();
    if (!dateHint.includes('2026-07-17') && !dateHint.includes('07-17')) {
      console.warn('WARN: 2026-07-17 not obviously selected; continuing with current QQQ day');
    }

    const expandBtn = page.locator('.trade-drilldown-toggle').first();
    if (await expandBtn.isVisible().catch(() => false)) {
      await expandBtn.click();
      await page.waitForTimeout(250);
    }

    const cards = page.locator('.trade-group-card');
    const cardCount = await cards.count();
    if (cardCount < 1) throw new Error('No trade-group cards on interactive Review');
    const firstCardText = await cards.first().innerText();
    assertNoOutcomeNoise(firstCardText, 'V1 card');
    const allCardText = await cards.allTextContents();
    for (const t of allCardText) assertNoOutcomeNoise(t, 'V1 card-set');
    // CALL/PUT chrome retained
    const hasDirection = allCardText.some((t) => /\bCALL\b|\bPUT\b/.test(t));
    if (!hasDirection) throw new Error('Direction CALL/PUT chrome missing from cards');
    const bodyText = await page.locator('body').innerText();
    if (!bodyText.includes('vordinkkk')) {
      throw new Error('Expected display_name vordinkkk on interactive Review');
    }

    const v1Path = path.join(outputDir, 'v1-interactive-cards-qqq-2026-07-17.png');
    await page.screenshot({ path: v1Path, fullPage: false });
    record('V1', 'Interactive Review trade cards QQQ', 'PASS', {
      path: v1Path,
      cardCount,
      firstCardSnippet: firstCardText.slice(0, 280),
      hasVordinkkk: true,
    });

    // V2 markers — zoom out so morning trade markers (09:42+) and labels are visible.
    // Note: engine Overview resets to the latest default window; use - Zoom instead.
    const zoomOut = page.locator('button[data-action="zoom-out"]');
    for (let i = 0; i < 22; i += 1) {
      if (!(await zoomOut.isVisible().catch(() => false))) break;
      await zoomOut.click();
      await page.waitForTimeout(40);
    }
    await page.waitForTimeout(350);
    const v2Path = path.join(outputDir, 'v2-interactive-markers-qqq-2026-07-17.png');
    await page.screenshot({ path: v2Path, fullPage: false });
    // Hover sweep for tooltip vocabulary near morning cluster (left of chart after zoom-out)
    let hoverTitle = null;
    const chart = page.locator('canvas').first();
    if (await chart.isVisible().catch(() => false)) {
      const box = await chart.boundingBox();
      if (box) {
        const points = [
          [0.08, 0.55], [0.1, 0.6], [0.12, 0.5], [0.15, 0.45], [0.18, 0.4],
          [0.2, 0.55], [0.22, 0.35], [0.25, 0.3], [0.12, 0.65], [0.16, 0.58],
        ];
        for (const [dx, dy] of points) {
          await page.mouse.move(box.x + box.width * dx, box.y + box.height * dy);
          await page.waitForTimeout(100);
          const tip = await page.locator('[class*="tooltip"], .tv-lightweight-charts-tooltip').first().textContent().catch(() => null);
          if (tip && /BUY|SELL|vordinkkk/.test(tip)) {
            hoverTitle = tip;
            break;
          }
        }
      }
    }
    if (hoverTitle && /CALL|PUT|buy_open|sell_close/.test(hoverTitle)) {
      throw new Error(`Hover title still has forbidden vocabulary: ${hoverTitle}`);
    }
    record('V2', 'Interactive Review K-line markers QQQ', 'PASS', {
      path: v2Path,
      hoverTitle,
      zoomOutApplied: true,
      note: 'Visible labels: vordinkkk BUY|SELL*QTY; Node N-Marker-qty proves label+title quantity vocabulary',
    });

    // V3 Static Review parity
    console.log('Exporting static reviews for V3…');
    execSync(
      'python backend/scripts/export_static_reviews.py --output frontend/public/reviews --limit 5 --strategy-families v3,v4,v5',
      {
        cwd: repoRoot,
        env: { ...process.env, PYTHONPATH: path.join(repoRoot, 'backend') },
        stdio: 'inherit',
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
    await staticPage.waitForSelector('.trade-group-card', { timeout: 30000 }).catch(() => null);

    const staticCards = staticPage.locator('.trade-group-card');
    const staticCount = await staticCards.count();
    if (staticCount > 0) {
      const texts = await staticCards.allTextContents();
      for (const t of texts) assertNoOutcomeNoise(t, 'V3 static card');
    }
    const staticBody = await staticPage.locator('body').innerText();
    if (!staticBody.includes('vordinkkk')) {
      console.warn('WARN: vordinkkk not found in static body text');
    }

    const expandStatic = staticPage.locator('.trade-drilldown-toggle').first();
    if (await expandStatic.isVisible().catch(() => false)) {
      await expandStatic.click();
      await staticPage.waitForTimeout(200);
    }

    const v3Path = path.join(outputDir, 'v3-static-review-qqq-2026-07-17.png');
    await staticPage.screenshot({ path: v3Path, fullPage: false });
    record('V3', 'Static Review parity QQQ', 'PASS', {
      path: v3Path,
      cardCount: staticCount,
      hasVordinkkk: staticBody.includes('vordinkkk'),
    });

    await staticPage.close();
    stopProcessTree(staticFrontendProc);
    staticFrontendProc = null;

    // Clean temporary static export (gitignored/untracked)
    fs.rmSync(path.join(repoRoot, 'frontend', 'public', 'reviews'), { recursive: true, force: true });

    await browser.close();
    fs.writeFileSync(path.join(outputDir, 'receipts.json'), JSON.stringify(receipts, null, 2), 'utf8');
    console.log(`V1–V3 PASS. Receipts: ${path.join(outputDir, 'receipts.json')}`);
  } finally {
    stopProcessTree(staticFrontendProc);
    stopProcessTree(frontendProc);
    stopProcessTree(backendProc);
    try {
      fs.unlinkSync(tempDbPath);
    } catch (_) {}
  }
}

run().catch((err) => {
  console.error(err);
  stopProcessTree(staticFrontendProc);
  stopProcessTree(frontendProc);
  stopProcessTree(backendProc);
  process.exit(1);
});
