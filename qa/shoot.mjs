// Screenshot source pages (file://) and the preview theme at desktop + mobile widths.
// Usage: bun shoot.mjs [page ...]   (page = source file stem; "index" maps to "/")
import puppeteer from 'puppeteer-core';
import { mkdirSync, readFileSync } from 'node:fs';

const STORE = 'https://embraecare.myshopify.com';
const THEME = '189665706142';
const PASSWORD = process.env.STORE_PASSWORD;
if (!PASSWORD) throw new Error('set STORE_PASSWORD');
const SRC = 'http://127.0.0.1:8765/pages/'; // served over HTTP: CSS masks don't load from file://
const PRODUCTS = ['reset-cleanser', 'urban-defense-serum', 'climate-adapt-moisturizer', 'daily-shield-sunscreen', 'daily-urban-defense-routine'];
const pages = process.argv.slice(2).length ? process.argv.slice(2) : ['index', ...PRODUCTS];
const WIDTHS = { d: 1440, m: 390 };
// journal articles = pages using the shared article CSS group
const ARTICLES = readFileSync(new URL('../source/css/shared-12p-01.css', import.meta.url), 'utf8').split('\n')[0]
  .replace('/* used by:', '').replace('*/', '').split(',').map((x) => x.trim().replace('.html', ''));
const path = (p) => p === 'index' ? '/' : p === 'journal' ? '/blogs/journal' : ARTICLES.includes(p) ? `/blogs/journal/${p}`
  : PRODUCTS.includes(p) ? `/products/${p}` : `/pages/${p}`;
const url = (p) => `${STORE}${path(p)}?preview_theme_id=${THEME}`;

mkdirSync('shots', { recursive: true });
const browser = await puppeteer.launch({ executablePath: '/usr/bin/chromium', headless: true, args: ['--no-sandbox'] });
const page = await browser.newPage();

await page.goto(`${STORE}/password`, { waitUntil: 'networkidle2' });
// Post the storefront password from inside the page so the session cookie lands in the browser.
await page.evaluate(async (pw) => {
  const body = new URLSearchParams({ form_type: 'storefront_password', utf8: '✓', password: pw });
  await fetch('/password', { method: 'POST', body, credentials: 'include' });
}, PASSWORD);

// Freeze the page: show every .reveal, drop Shopify's preview bar, stop animations so both sides compare fairly.
const settle = async () => {
  await page.evaluate(async () => {
    document.querySelectorAll('.reveal').forEach((e) => e.classList.add('in'));
    document.querySelectorAll('#preview-bar-iframe, #PBarNextFrameWrapper, .review-toggle, #reviewBtn, #backend-seo').forEach((e) => e.remove());
    const st = document.createElement('style');
    st.textContent = '*,*::before,*::after{animation-play-state:paused!important;transition:none!important;caret-color:transparent!important}';
    document.head.appendChild(st);
    await document.fonts.ready;
  });
  await new Promise((r) => setTimeout(r, 600));
};

for (const p of pages) {
  for (const [tag, width] of Object.entries(WIDTHS)) {
    await page.setViewport({ width, height: 900 });
    for (const [side, target] of [['src', `${SRC}${p}.html`], ['shop', url(p)]]) {
      await page.goto(target, { waitUntil: 'networkidle2', timeout: 90000 });
      await settle();
      await page.screenshot({ path: `shots/${p}.${tag}.${side}.png`, fullPage: true });
    }
    console.log('shot', p, tag);
  }
}
await browser.close();
