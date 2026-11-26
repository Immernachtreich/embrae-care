// Cross-browser check: load every built page in Chromium and Firefox at phone/tablet/desktop widths and report
// JS errors, horizontal overflow, and page heights that differ between engines (a sign of a layout break).
// Usage: STORE_PASSWORD=... bun xbrowser.mjs [path ...]   Screenshots of flagged pages go to shots/xb/.
import puppeteer from 'puppeteer-core';
import { mkdirSync, readFileSync, readdirSync } from 'node:fs';

const STORE = 'https://embraecare.myshopify.com';
const THEME = '189665706142';
const PASSWORD = process.env.STORE_PASSWORD;
if (!PASSWORD) throw new Error('set STORE_PASSWORD');
const seoDir = new URL('../source/seo/', import.meta.url);
const all = readdirSync(seoDir).map((f) => JSON.parse(readFileSync(new URL(f, seoDir))).handle).filter(Boolean).sort();
const paths = process.argv.slice(2).length ? process.argv.slice(2) : all;
const WIDTHS = [390, 768, 1440];
mkdirSync('shots/xb', { recursive: true });

const ENGINES = { chromium: { executablePath: '/usr/bin/chromium', args: ['--no-sandbox'] }, firefox: { browser: 'firefox', executablePath: '/usr/bin/firefox' } };
const res = {};
for (const [name, opts] of Object.entries(ENGINES)) {
  const browser = await puppeteer.launch({ headless: true, ...opts });
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', (e) => { const m = String(e.message || e); if (!/^Cookie /.test(m)) errors.push(m.slice(0, 160)); }); // Firefox reports Shopify's cookie rejections as errors
  await page.goto(`${STORE}/password`, { waitUntil: 'load' });
  await page.evaluate(async (pw) => {
    await fetch('/password', { method: 'POST', body: new URLSearchParams({ form_type: 'storefront_password', password: pw }), credentials: 'include' });
  }, PASSWORD);
  for (const p of paths) {
    for (const w of WIDTHS) {
      await page.setViewport({ width: w, height: 900 });
      errors.length = 0;
      await page.goto(`${STORE}${p}?preview_theme_id=${THEME}`, { waitUntil: 'load', timeout: 90000 });
      await new Promise((r) => setTimeout(r, 1500));
      const m = await page.evaluate(() => {
        document.querySelectorAll('.reveal').forEach((e) => e.classList.add('in'));
        document.querySelectorAll('#preview-bar-iframe, #PBarNextFrameWrapper').forEach((e) => e.remove());
        const vw = document.documentElement.clientWidth;
        // elements poking past the viewport (ignoring ones inside horizontal scrollers or clipped parents)
        const wide = [...document.querySelectorAll('body *')].filter((e) => {
          const r = e.getBoundingClientRect(); if (r.width === 0 || r.right <= vw + 1) return false;
          for (let a = e.parentElement; a && a !== document.body; a = a.parentElement) { const o = getComputedStyle(a).overflowX; if (o !== 'visible') return false; }
          return true;
        }).slice(0, 3).map((e) => e.tagName.toLowerCase() + (e.className && typeof e.className === 'string' ? '.' + e.className.split(' ')[0] : ''));
        return { h: document.documentElement.scrollHeight, over: document.documentElement.scrollWidth > vw + 1, wide };
      });
      (res[`${p}@${w}`] ??= {})[name] = { ...m, errors: [...new Set(errors)] };
      if (name === 'firefox') await page.screenshot({ path: `shots/xb/${p.replaceAll('/', '_')}.${w}.firefox.png`, fullPage: true }).catch(() => {});
    }
    console.error(name, p);
  }
  await browser.close();
}

let bad = 0;
for (const [k, v] of Object.entries(res)) {
  const c = v.chromium, f = v.firefox; if (!c || !f) continue;
  const dh = Math.abs(c.h - f.h) / c.h;
  const issues = [];
  if (dh > 0.03) issues.push(`height chromium=${c.h} firefox=${f.h}`);
  for (const [n, e] of [['chromium', c], ['firefox', f]]) {
    if (e.over) issues.push(`${n} horizontal scroll (${e.wide.join(', ')})`);
    if (e.errors.length) issues.push(`${n} JS: ${e.errors.join(' | ')}`);
  }
  if (issues.length) { bad++; console.log(`!! ${k}\n   ${issues.join('\n   ')}`); }
}
console.log(`checked ${Object.keys(res).length} page×width combos, ${bad} with issues`);
