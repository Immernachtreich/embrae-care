(function () {
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  function initNav() {
    $$('.nav>li').forEach(function (li) {
      var link = $('.nav-link', li), mega = $('.mega', li);
      if (!mega || li.dataset.bound) return;
      li.dataset.bound = '1';
      link.addEventListener('click', function (e) {
        if (window.matchMedia('(hover:none)').matches && !li.classList.contains('open')) {
          e.preventDefault();
          $$('.nav>li.open').forEach(function (x) { x.classList.remove('open'); });
          li.classList.add('open');
        }
      });
    });
    var burger = $('.burger'), mnav = $('#mnav');
    if (burger && mnav && !burger.dataset.bound) {
      burger.dataset.bound = '1';
      burger.addEventListener('click', function () {
        var o = mnav.classList.toggle('open');
        burger.setAttribute('aria-expanded', o);
      });
      $$('button.top', mnav).forEach(function (b) {
        b.addEventListener('click', function () {
          var o = b.parentNode.classList.toggle('open');
          b.setAttribute('aria-expanded', o);
          $('span', b).textContent = o ? '−' : '+';
        });
      });
    }
  }

  function closeMenus() {
    $$('.nav>li.open').forEach(function (x) { x.classList.remove('open'); });
    var mnav = $('#mnav'), burger = $('.burger');
    if (mnav) mnav.classList.remove('open');
    if (burger) burger.setAttribute('aria-expanded', 'false');
  }

  document.addEventListener('click', function (e) { if (!e.target.closest('.nav')) $$('.nav>li.open').forEach(function (x) { x.classList.remove('open'); }); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { closeMenus(); Cart.close(); } });

  var io = 'IntersectionObserver' in window ? new IntersectionObserver(function (es) {
    es.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } });
  }, { threshold: 0.12 }) : null;
  function initReveal(root) {
    $$('.reveal:not(.in)', root).forEach(function (el) { if (io) io.observe(el); else el.classList.add('in'); });
  }

  var Cart = {
    el: function () { return $('#CartDrawer'); },
    open: function () {
      var d = this.el(); if (!d) { window.location.href = window.Shopify && Shopify.routes ? Shopify.routes.root + 'cart' : '/cart'; return; }
      d.classList.add('open'); d.setAttribute('aria-hidden', 'false'); document.documentElement.classList.add('cart-open');
      var f = $('.cd-close', d); if (f) f.focus();
    },
    close: function () {
      var d = this.el(); if (!d || !d.classList.contains('open')) return;
      d.classList.remove('open'); d.setAttribute('aria-hidden', 'true'); document.documentElement.classList.remove('cart-open');
    },
    root: function () { return (window.Shopify && Shopify.routes && Shopify.routes.root) || '/'; },
    refresh: function () {
      var d = this.el(); if (!d) return Promise.resolve();
      var id = d.closest('[id^="shopify-section-"]').id.replace('shopify-section-', '');
      return fetch(this.root() + '?sections=' + id).then(function (r) { return r.json(); }).then(function (json) {
        var doc = new DOMParser().parseFromString(json[id], 'text/html');
        var fresh = $('#CartDrawer', doc);
        $('.cd-panel', d).replaceWith($('.cd-panel', fresh));
        $$('[data-cart-count]').forEach(function (c) {
          var n = fresh.getAttribute('data-count');
          c.textContent = n; c.hidden = n === '0';
        });
      });
    },
    add: function (items, checkout) {
      var self = this;
      return fetch(this.root() + 'cart/add.js', {
        method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({ items: items })
      }).then(function (r) { return r.json().then(function (j) { if (!r.ok) throw j; return j; }); })
        .then(function () {
          if (checkout) { window.location.href = self.root() + 'checkout'; return; }
          return self.refresh().then(function () { self.open(); });
        });
    },
    change: function (key, qty) {
      var self = this, d = this.el(); if (d) d.classList.add('busy');
      return fetch(this.root() + 'cart/change.js', {
        method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({ id: key, quantity: qty })
      }).then(function () { return self.refresh(); }).finally(function () { if (d) d.classList.remove('busy'); });
    }
  };
  window.EmbraeCart = Cart;

  document.addEventListener('click', function (e) {
    var t = e.target.closest('[data-cart-open]');
    if (t && Cart.el()) { e.preventDefault(); Cart.open(); return; }
    if (e.target.closest('[data-cart-close]')) { Cart.close(); return; }
    var q = e.target.closest('[data-qty]');
    if (q) { Cart.change(q.getAttribute('data-key'), parseInt(q.getAttribute('data-qty'), 10)); }
  });

  document.addEventListener('submit', function (e) {
    var f = e.target;
    if (!f.matches('form[action$="/cart/add"]')) return;
    var btn = e.submitter || f.querySelector('[type="submit"]'), buyNow = btn && btn.hasAttribute('data-buy-now');
    if (!buyNow && !Cart.el()) return;
    e.preventDefault();
    // Routine add-ons are checkboxes named "addon" tied to the form (form="…"); they take the same quantity.
    var fd = new FormData(f), qty = parseInt(fd.get('quantity') || '1', 10);
    var items = [{ id: fd.get('id'), quantity: qty }].concat(fd.getAll('addon').map(function (id) { return { id: id, quantity: qty }; }));
    if (btn) btn.setAttribute('aria-busy', 'true');
    Cart.add(items, buyNow)
      .catch(function (err) { alert((err && err.description) || 'Could not add to cart.'); })
      .finally(function () { if (btn) btn.removeAttribute('aria-busy'); });
  });

  /* Hero carousel: auto-advance, dots, arrow keys, swipe; pauses on hover/focus and reduced motion */
  function initHero(root) {
    $$('[data-hero]', root).forEach(function (hero) {
      if (hero._hero) return;
      var slides = $$('.slide', hero), dots = $$('.hdots button', hero), n = slides.length, idx = 0, timer = null;
      var DUR = parseInt(hero.getAttribute('data-interval'), 10) || 5000;
      var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches, held = false;
      function show(i) {
        idx = (i + n) % n;
        slides.forEach(function (s, k) { s.classList.toggle('on', k === idx); s.setAttribute('aria-hidden', k === idx ? 'false' : 'true'); });
        dots.forEach(function (d, k) { d.classList.toggle('on', k === idx); d.setAttribute('aria-selected', k === idx); });
        schedule();
      }
      function schedule() { clearTimeout(timer); if (reduce || held || n < 2 || document.hidden || !hero.isConnected) return; timer = setTimeout(function () { show(idx + 1); }, DUR); }
      function setHeld(v) { held = v; if (v) clearTimeout(timer); else schedule(); }
      dots.forEach(function (d, k) { d.addEventListener('click', function () { show(k); }); });
      hero.addEventListener('mouseenter', function () { setHeld(true); });
      hero.addEventListener('mouseleave', function () { setHeld(false); });
      hero.addEventListener('focusin', function () { setHeld(true); });
      hero.addEventListener('focusout', function () { setHeld(false); });
      hero.addEventListener('keydown', function (e) { if (e.key === 'ArrowRight') show(idx + 1); if (e.key === 'ArrowLeft') show(idx - 1); });
      var sx = null;
      hero.addEventListener('touchstart', function (e) { sx = e.touches[0].clientX; }, { passive: true });
      hero.addEventListener('touchend', function (e) { if (sx === null) return; var dx = e.changedTouches[0].clientX - sx; if (Math.abs(dx) > 45) show(idx + (dx < 0 ? 1 : -1)); sx = null; }, { passive: true });
      document.addEventListener('visibilitychange', schedule);
      hero._hero = { show: function (el) { var k = slides.indexOf(el); if (k > -1) { held = true; show(k); } }, release: function () { setHeld(false); } };
      show(0);
    });
  }

  /* Sunrise / Moonlight routine toggle */
  function initDayNight(root) {
    $$('[data-daynight]', root).forEach(function (dn) {
      if (dn._dn) return; dn._dn = true;
      var label = $('.routine-label', dn), btns = $$('.toggle button', dn);
      $$('.tg-side', dn).forEach(function (b) { b.addEventListener('click', function () { var t = $('.toggle button[data-mode="' + b.getAttribute('data-mode') + '"]', dn); if (t) t.click(); }); });
      btns.forEach(function (b) {
        b.addEventListener('click', function () {
          var mode = b.getAttribute('data-mode'); if (dn.getAttribute('data-theme') === mode) return;
          dn.setAttribute('data-theme', mode);
          btns.forEach(function (x) { x.setAttribute('aria-pressed', x === b); });
          $$('.dn-panel', dn).forEach(function (p) { p.classList.toggle('on', p.getAttribute('data-panel') === mode); });
          label.classList.add('swap');
          setTimeout(function () { label.textContent = label.getAttribute('data-' + mode); label.classList.remove('swap'); }, 200);
        });
      });
    });
  }

  function init(root) {
    // nav listeners bind globally, so only re-run them when the header itself reloads
    if (root === document || $('.nav, #mnav', root)) initNav();
    initReveal(root); initHero(root); initDayNight(root);
  }
  document.addEventListener('shopify:block:select', function (e) {
    var hero = e.target.closest('[data-hero]'); if (hero && hero._hero) hero._hero.show(e.target);
  });
  document.addEventListener('shopify:block:deselect', function (e) {
    var hero = e.target.closest('[data-hero]'); if (hero && hero._hero) hero._hero.release();
  });
  document.addEventListener('DOMContentLoaded', function () { init(document); });
  document.addEventListener('shopify:section:load', function (e) { init(e.target); });
})();
