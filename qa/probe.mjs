// Print computed layout of a selector on source vs shop at a given width.
import puppeteer from 'puppeteer-core';
const [, , pagePath, srcUrl, sel, width] = process.argv;
const b = await puppeteer.launch({ executablePath: '/usr/bin/chromium', headless: true, args: ['--no-sandbox'] });
const p = await b.newPage(); await p.setViewport({ width: +width, height: 900 });
await p.goto('https://embraecare.myshopify.com/password');
await p.evaluate(async (pw) => { await fetch('/password', { method: 'POST', body: new URLSearchParams({ form_type: 'storefront_password', password: pw }) }); }, process.env.STORE_PASSWORD);
for (const u of [srcUrl, `https://embraecare.myshopify.com${pagePath}?preview_theme_id=189665706142`]) {
  await p.goto(u, { waitUntil: 'networkidle2' });
  console.log(u.slice(0, 40), JSON.stringify(await p.evaluate((s) => [...document.querySelectorAll(s)].slice(0, 20).map((e) => { const c = getComputedStyle(e), r = e.getBoundingClientRect(); return [e.className.baseVal ?? e.className, Math.round(r.height), c.rowGap, c.marginTop, c.marginBottom, c.paddingTop, c.paddingBottom]; }), sel)));
}
await b.close();
