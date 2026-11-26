// Lighthouse (mobile, default throttling) on key preview pages. Usage: STORE_PASSWORD=... bun perf.mjs [path ...]
// Note: the preview bar Shopify injects with preview_theme_id adds a little weight the published theme won't have.
import puppeteer from 'puppeteer-core';
import lighthouse from 'lighthouse';
import { writeFileSync } from 'node:fs';

const STORE = 'https://embraecare.myshopify.com';
const THEME = '189665706142';
const PASSWORD = process.env.STORE_PASSWORD;
if (!PASSWORD) throw new Error('set STORE_PASSWORD');
const paths = process.argv.slice(2).length ? process.argv.slice(2) : ['/', '/products/urban-defense-serum', '/products/daily-urban-defense-routine', '/pages/skin-quiz', '/blogs/journal', '/blogs/journal/monsoon-skin-care-keep-it-simple', '/pages/our-ingredients'];

const browser = await puppeteer.launch({ executablePath: '/usr/bin/chromium', headless: true, args: ['--no-sandbox'] });
const page = await browser.newPage();
await page.goto(`${STORE}/password`, { waitUntil: 'networkidle2' });
await page.evaluate(async (pw) => {
  await fetch('/password', { method: 'POST', body: new URLSearchParams({ form_type: 'storefront_password', password: pw }), credentials: 'include' });
}, PASSWORD);
// Load the theme once so the preview cookie is set, then audit the clean URLs.
await page.goto(`${STORE}/?preview_theme_id=${THEME}`, { waitUntil: 'networkidle2' });

const out = {};
for (const p of paths) {
  const r = await lighthouse(`${STORE}${p}?preview_theme_id=${THEME}`, { onlyCategories: ['performance', 'accessibility', 'best-practices', 'seo'], disableStorageReset: true }, undefined, page);
  const L = r.lhr, a = L.audits;
  const opp = Object.values(a).filter((x) => x.details?.type === 'opportunity' && (x.details.overallSavingsMs || 0) > 150)
    .map((x) => `${x.id} ~${Math.round(x.details.overallSavingsMs)}ms`);
  const fails = Object.values(a).filter((x) => x.score !== null && x.score < 0.9 && ['diagnostics', 'insights'].some(() => true) && x.scoreDisplayMode !== 'informative' && x.scoreDisplayMode !== 'notApplicable').map((x) => x.id);
  out[p] = {
    scores: Object.fromEntries(Object.entries(L.categories).map(([k, c]) => [k, Math.round(c.score * 100)])),
    LCP: a['largest-contentful-paint'].displayValue, CLS: a['cumulative-layout-shift'].displayValue, TBT: a['total-blocking-time'].displayValue, FCP: a['first-contentful-paint'].displayValue,
    lcpEl: a['largest-contentful-paint-element']?.details?.items?.[0]?.items?.[0]?.node?.snippet || a['lcp-breakdown-insight']?.details?.items?.[0]?.node?.snippet,
    opp, fails, boot: (a['bootup-time']?.details?.items || []).slice(0, 6).map((x) => `${Math.round(x.total)}ms ${x.url.slice(0, 90)}`),
  };
  console.log(p, JSON.stringify(out[p], null, 1));
}
writeFileSync('perf.json', JSON.stringify(out, null, 2));
await browser.close();
