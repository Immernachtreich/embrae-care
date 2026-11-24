// End-to-end: answer every quiz question (first option), add the recommended routine to the cart, check cart.js, clear it.
import puppeteer from 'puppeteer-core';
const STORE = 'https://embraecare.myshopify.com';
const b = await puppeteer.launch({ executablePath: '/usr/bin/chromium', headless: true, args: ['--no-sandbox'] });
const p = await b.newPage(); await p.setViewport({ width: 1280, height: 900 });
const errors = []; p.on('pageerror', (e) => errors.push(e.stack || e.message));
await p.goto(`${STORE}/password`);
await p.evaluate(async (pw) => { await fetch('/password', { method: 'POST', body: new URLSearchParams({ form_type: 'storefront_password', password: pw }) }); }, process.env.STORE_PASSWORD);
await p.goto(`${STORE}/pages/skin-quiz?preview_theme_id=189665706142`, { waitUntil: 'networkidle2' });
for (let i = 0; i < 15; i++) {
  if (await p.$('#qz-res.on')) break;
  await p.click('#qz-opts .qz-opt'); // a real click auto-advances after 260 ms
  await new Promise((r) => setTimeout(r, 600));
}
const result = await p.$eval('#qz-res', (e) => e.innerText.slice(0, 400));
console.log('RESULT:', result.replace(/\n+/g, ' | '));
await p.click('#qz-cta');
await new Promise((r) => setTimeout(r, 3000));
console.log('MSG:', await p.$eval('#qz-cartmsg', (e) => e.innerText));
console.log('DRAWER OPEN:', await p.evaluate(() => !!document.querySelector('#CartDrawer.open')));
const cart = await p.evaluate(async () => (await fetch('/cart.js')).json());
console.log('CART:', cart.items.map((i) => `${i.title} x${i.quantity}`).join(', '), 'total', cart.total_price / 100);
await p.evaluate(async () => fetch('/cart/clear.js', { method: 'POST' }));
console.log('JS errors:', errors.length ? errors : 'none');
await b.close();
