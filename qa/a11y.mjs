// Run axe-core (WCAG 2.1 AA) on every built page of the preview theme, at desktop and mobile widths.
// Usage: STORE_PASSWORD=... bun a11y.mjs [path ...]   Writes a11y.json; prints violations grouped by rule.
import puppeteer from 'puppeteer-core';
import { readFileSync, readdirSync, writeFileSync } from 'node:fs';

const STORE = 'https://embraecare.myshopify.com';
const THEME = '189665706142';
const PASSWORD = process.env.STORE_PASSWORD;
if (!PASSWORD) throw new Error('set STORE_PASSWORD');
const seoDir = new URL('../source/seo/', import.meta.url);
const all = readdirSync(seoDir).map((f) => JSON.parse(readFileSync(new URL(f, seoDir))).handle).filter(Boolean).sort();
const paths = process.argv.slice(2).length ? process.argv.slice(2) : all;
const axe = readFileSync(new URL('./node_modules/axe-core/axe.min.js', import.meta.url), 'utf8');

const browser = await puppeteer.launch({ executablePath: '/usr/bin/chromium', headless: true, args: ['--no-sandbox'] });
const page = await browser.newPage();
await page.goto(`${STORE}/password`, { waitUntil: 'networkidle2' });
await page.evaluate(async (pw) => {
  await fetch('/password', { method: 'POST', body: new URLSearchParams({ form_type: 'storefront_password', password: pw }), credentials: 'include' });
}, PASSWORD);

const byRule = {};
for (const p of paths) {
  for (const width of [1440, 390]) {
    await page.setViewport({ width, height: 900 });
    await page.goto(`${STORE}${p}?preview_theme_id=${THEME}&cb=${Math.random()}`, { waitUntil: 'networkidle2', timeout: 90000 });
    await page.evaluate(() => {
      document.querySelectorAll('.reveal').forEach((e) => e.classList.add('in'));
      document.querySelectorAll('#preview-bar-iframe, #PBarNextFrameWrapper').forEach((e) => e.remove());
    });
    await new Promise((r) => setTimeout(r, 800)); // let reveal transitions finish so contrast reads final colours
    await page.evaluate(axe);
    const res = await page.evaluate(() => axe.run(document, { runOnly: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'best-practice'] }));
    for (const v of res.violations) {
      const r = (byRule[v.id] ??= { impact: v.impact, help: v.help, pages: {}, samples: {} });
      r.pages[p] = (r.pages[p] || 0) + v.nodes.length;
      if (v.id === 'color-contrast') for (const n of v.nodes) { const d = n.any[0]?.data || {}; const k = `${d.fgColor} on ${d.bgColor} (${d.contrastRatio}) ${d.fontSize} ${d.fontWeight}`; (r.pairs ??= {})[k] ??= []; if (r.pairs[k].length < 4) r.pairs[k].push(n.target.join(' ')); }
      for (const n of v.nodes.slice(0, v.id === "color-contrast" ? 3 : 20)) r.samples[n.target.join(' ')] ??= (n.failureSummary || '').split('\n').slice(0, 2).join(' | ');
    }
    console.error('done', p, width, res.violations.length);
  }
}
await browser.close();
writeFileSync('a11y.json', JSON.stringify(byRule, null, 2));
const order = { critical: 0, serious: 1, moderate: 2, minor: 3 };
for (const [id, r] of Object.entries(byRule).sort((a, b) => order[a[1].impact] - order[b[1].impact])) {
  console.log(`\n[${r.impact}] ${id}: ${r.help} — ${Object.keys(r.pages).length} pages, ${Object.values(r.pages).reduce((a, b) => a + b, 0)} nodes`);
  for (const [t, s] of Object.entries(r.samples).slice(0, 6)) console.log(`   ${t}  ::  ${s}`);
}
