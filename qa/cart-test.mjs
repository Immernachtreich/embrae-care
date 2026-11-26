// End-to-end cart run-through on the preview theme: product add (with an add-on), quantity change, bundle add,
// article add-to-cart button, remove, cart page, and the hand-off to checkout (stops at the checkout page).
// Usage: STORE_PASSWORD=... bun cart-test.mjs
import puppeteer from 'puppeteer-core';

const STORE = 'https://embraecare.myshopify.com';
const THEME = '189665706142';
const PASSWORD = process.env.STORE_PASSWORD;
if (!PASSWORD) throw new Error('set STORE_PASSWORD');
const u = (p) => `${STORE}${p}${p.includes('?') ? '&' : '?'}preview_theme_id=${THEME}`;

const browser = await puppeteer.launch({ executablePath: '/usr/bin/chromium', headless: true, args: ['--no-sandbox'] });
const page = await browser.newPage();
await page.setViewport({ width: 390, height: 900 });
const errors = [];
page.on('pageerror', (e) => errors.push(String(e.message || e)));
// Log in outside the browser (the in-page POST gets throttled with 429 after many runs) and hand the cookies over.
const login = await fetch(`${STORE}/password`, { method: 'POST', redirect: 'manual', body: new URLSearchParams({ form_type: 'storefront_password', password: PASSWORD }) });
if (login.status !== 302) throw new Error(`password login failed: ${login.status}`);
await page.setCookie(...login.headers.getSetCookie().map((c) => { const [nv] = c.split(';'); const i = nv.indexOf('='); return { name: nv.slice(0, i), value: nv.slice(i + 1), domain: 'embraecare.myshopify.com', path: '/' }; }));

let fails = 0;
const cart = () => page.evaluate(() => fetch('/cart.js').then(async (r) => { const t = await r.text(); try { return JSON.parse(t); } catch { throw new Error(`cart.js ${r.status} at ${location.href}: ${t.slice(0, 120)}`); } }));
const check = (name, ok, info = '') => { if (!ok) fails++; console.log(`${ok ? 'ok' : '!!'} ${name}${info ? '  ' + info : ''}`); };
const summary = (c) => c.items.map((i) => `${i.product_title}×${i.quantity}`).join(', ') + ` = ${c.total_price / 100}`;
const drawerOpen = () => page.waitForSelector('#CartDrawer.open', { timeout: 10000 }).then(() => true, () => false);
const count = () => page.$eval('[data-cart-count]', (e) => (e.hidden ? '0' : e.textContent.trim()));
const closeDrawer = async () => { await page.keyboard.press('Escape'); await new Promise((r) => setTimeout(r, 400)); };

await page.goto(u('/cart/clear'), { waitUntil: 'load' });
check('cart starts empty', (await cart()).item_count === 0);

// 1. Product page: tick the first add-on, then Add to cart
await page.goto(u('/products/urban-defense-serum'), { waitUntil: 'networkidle2' });
const addon = await page.$('input[name="addon"]:not([disabled])');
if (addon) await page.evaluate((e) => e.closest('label').click(), addon);
await page.evaluate(() => [...document.querySelectorAll('button[type="submit"]')].find((b) => b.offsetParent && /add to cart/i.test(b.textContent)).click());
check('product add opens drawer', await drawerOpen());
let c = await cart();
check('product + add-on in cart', c.item_count === (addon ? 2 : 1), summary(c));
check('header count matches', (await count()) === String(c.item_count), `badge=${await count()}`);

// 2. Quantity +
await page.click('#CartDrawer .cd-item .cd-qty button:last-child');
await page.waitForFunction((n) => document.querySelector('#CartDrawer .cd-item .cd-qty span')?.textContent.trim() === '2', { timeout: 10000 }).catch(() => {});
c = await cart();
check('quantity + updates', c.items[0]?.quantity === 2, summary(c));
const shown = await page.$eval('#CartDrawer .cd-total span:last-child', (e) => e.textContent.trim());
check('drawer subtotal matches cart', shown.replace(/[^\d]/g, '') === String(c.total_price / 100), `drawer=${shown}`);

// 3. Remove the first line
const before = c.items.length;
await page.click('#CartDrawer .cd-remove');
await page.waitForFunction((n) => document.querySelectorAll('#CartDrawer .cd-item').length === n, { timeout: 10000 }, before - 1).catch(() => {});
c = await cart();
check('remove deletes the line', c.items.length === before - 1, summary(c));
await closeDrawer();

// 4. Bundle page
await page.goto(u('/products/daily-urban-defense-routine'), { waitUntil: 'networkidle2' });
await page.evaluate(() => [...document.querySelectorAll('button[type="submit"]')].find((b) => b.offsetParent && /add to cart/i.test(b.textContent)).click());
check('bundle add opens drawer', await drawerOpen());
c = await cart();
check('bundle in cart', c.items.some((i) => i.handle === 'daily-urban-defense-routine'), summary(c));
await closeDrawer();

// 5. Article inline add-to-cart button
await page.goto(u('/blogs/journal/what-goes-first-serum-or-moisturizer'), { waitUntil: 'networkidle2' });
const n0 = (await cart()).item_count;
const hasBtn = await page.evaluate(() => { const b = document.querySelector('.ar-body [data-add], [data-add]'); if (b) b.click(); return !!b; });
if (hasBtn) { check('article button opens drawer', await drawerOpen()); check('article button adds', (await cart()).item_count === n0 + 1); await closeDrawer(); }
else console.log('-- no article add button on this article');

// 6. Cart page
await page.goto(u('/cart'), { waitUntil: 'networkidle2' });
c = await cart();
const lines = await page.$$eval('main [data-key], main .cart-item, main tr, main li', (els) => els.length);
check('cart page renders lines', lines > 0 && !(await page.content()).includes('Liquid error'), `${c.items.length} lines in cart.js`);

// 7. Checkout hand-off (stops on the checkout page; nothing is paid)
await page.goto(u('/products/reset-cleanser'), { waitUntil: 'networkidle2' });
await page.evaluate(() => window.EmbraeCart.refresh().then(() => window.EmbraeCart.open()));
await drawerOpen();
await Promise.all([page.waitForNavigation({ waitUntil: 'load', timeout: 60000 }).catch(() => {}), page.click('#CartDrawer .cd-checkout')]);
check('checkout button reaches checkout', /\/checkouts?\//.test(page.url()), page.url().replace(/\?.*/, ''));
await page.screenshot({ path: 'shots/checkout.png' });

await page.goto(u('/cart/clear'), { waitUntil: 'load' });
check('no JS errors', errors.length === 0, errors.slice(0, 3).join(' | '));
console.log(fails ? `${fails} failed` : 'all passed');
await browser.close();
