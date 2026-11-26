# EMBRAE → Shopify: handoff (2026-11-19)

## Goal
Rebuild `embrae-website.html` (single-file preview: 29 pages, 34 embedded assets, JSON pack in `<script id="pk">`) as a pixel-faithful custom Shopify Online Store 2.0 theme. Every section must be editable in the theme editor, and products, cart and checkout must be real Shopify objects.

Full plan (8 phases, 27 steps): `~/.claude-personal/plans/refer-embrae-website-html-we-have-valiant-clover.md`

## Store
- Domain: `embraecare.myshopify.com`. The permanent domain is **`embrae-yaf7tdei.myshopify.com`**; use it for `store auth` and `store execute`.
- CLI: always `bunx shopify <command>`. Store auth is done with scopes: read/write online_store_navigation, products, content, online_store_pages.
- The storefront is **password-protected**, so preview while logged into the admin, or use `theme dev --store-password`.
- **Rule from the user: additive changes only. Never overwrite or delete existing store content.**
- Existing content that must stay untouched:
  - Live theme "Embrae X Sanjay" (159236522142), plus unpublished Horizon and Prestige.
  - Menus: `main-menu`, `footer`, `information`, `customer-account-main-menu`.
  - 12 demo bag products (`le-*`).
  - `news` blog with 5 articles.
  - Pages: `contact`, `why-we-exist`, `our-philosophy`, `our-story`, `a-note-from-the-founder`, `faqs`. These handles match the source pages, so reuse them; don't overwrite their content.

## Done
- **Phase 0**
  - `tools/extract.py` unpacks the bundle into:
    - `source/pages/*.html`: 29 pages, asset refs rewritten to `../assets/`.
    - `source/assets/`: `asset-NN.*`, `helvena-400…800.woff`, and `manifest.json` (which pages use each asset).
    - `source/seo/*.json`: title, meta description, handle and the backend SEO note for each page.
  - Theme skeleton is in `embraecare/` (from `shopify theme init`). It is not a git repo yet.
- **Phase 1**
  - `tools/build_css.py` writes the CSS shared by all pages to `embraecare/assets/embrae-base.css` (345 rules, 37 KB; review-helper rules dropped). It also writes CSS used by only some pages to `source/css/` (e.g. `shared-22p` = inner pages, `shared-12p` = articles, `shared-6p`/`5p` = product pages, plus per-page files). **Reuse these when building each page's sections.**
  - `layout/theme.liquid`: adds the `js` class, preloads Helvena, loads the base CSS, renders `snippets/svg-sprite.liquid` (product art symbols `p-reset`, `p-defend`, `p-adapt`, `p-protect`, `p-pouch`, `lineup4`, `lineup2`, `lineup4pouch`, `leaf`), the header and footer groups, and `{% section 'cart-drawer' %}`.
  - `snippets/css-variables.liquid`: brand colours from theme settings (`config/settings_schema.json`: brand colours and social URLs).
  - `assets/embrae.js`: nav dropdowns, mobile menu, `.reveal` animations, and `window.EmbraeCart` (add/change/refresh through the Section Rendering API). It intercepts `form[action$="/cart/add"]`.
  - Assets renamed: `embrae-logo.png` (logo, rendered as a CSS mask), `about-story.jpg`, `about-values.jpg`.
- **Phase 2**
  - `sections/announcement-bar.liquid`.
  - `sections/header.liquid`: "menu" blocks, each with a link list and up to 4 tiles (built-in art or an image); account, search and cart icons, with a cart count.
  - `sections/cart-drawer.liquid`: new; includes a free-shipping bar (₹999 threshold).
  - `sections/footer.liquid`: newsletter (Shopify customer form, **email only**), link-list blocks, contact block, payment icons or fallback text, GST line, brand row.
  - `sections/header-group.json` and `footer-group.json` reproduce the source navigation.
  - `locales/en.default.json` has the new strings.
  - `bunx shopify theme check` passes with 0 issues.
- **On the store**
  - Pushed as the new unpublished theme **"EMBRAE Custom (in progress)", ID 189665706142**.
    - Preview: https://embraecare.myshopify.com?preview_theme_id=189665706142
    - Update it with `bunx shopify theme push --store embraecare.myshopify.com --theme 189665706142`.
  - Created 6 new menus with HTTP links: `shop`, `the-embrae-system`, `about-embrae`, `footer-shop`, `footer-discover`, `footer-policies`.
- `templates/index.json` is currently empty, so the home page is blank until Phase 4.
- **Phase 3 (started 2026-11-19)**
  - User decisions: EMBRAE products are created as ACTIVE; the 12 `le-*` demo products stay as they are.
  - Created 5 ACTIVE products (vendor EMBRAE). Each has a SEO title and description from `source/seo`, one variant with inventory not tracked, and an `EMB-<STEP>` SKU:
    - `reset-cleanser` (15482983612574): ₹899, 100 ml.
    - `urban-defense-serum` (15482984136862): ₹1,299, 30 ml.
    - `climate-adapt-moisturizer` (15482984628382): ₹1,099, 50 g.
    - `daily-shield-sunscreen` (15482985152670): ₹1,199, 50 g.
    - `daily-urban-defense-routine` (15482985709726): ₹4,199, sold as a fixed product and not through Shopify Bundles.
  - The products have no images yet, because approved photography is still pending. There is no compare-at price: per the SEO note, the launch shows MRP only.
  - All 5 are published to the Online Store (publication 228278403230). Store auth now also has the publications and discounts scopes.
  - `onlineStoreUrl` comes back null for every product, the demo ones too, because the storefront is password-protected.
  - Travel Pouch (user decision): it ships inside the routine set. There is no pouch product and no discount. The bundle description already says "with a free Travel Pouch".
  - Still to do: the metafield and metaobject definitions. These are deferred to Phase 5, so they can be shaped by the product page sections. Collections are not needed yet, because `/collections/all` exists by default.
- **Phase 4: home page (built 2026-11-22, pushed to 189665706142)**
  - Sections: `hero-slider`, `value-strip`, `climate-grid`, `embrae-system`, `step-videos`, `day-night`, `quiz-teaser`, `ingredients-feature` and `routine-offer`. `templates/index.json` is filled with the source copy by `build_index.py`, a throwaway script; the JSON file is now the source of truth.
  - Snippets:
    - `price`: prints ₹1,299 whatever the shop money format is. The store format is `Rs.{{amount}}`, which checkout and emails also use; changing it is the user's call.
    - `step-icon`: the step mask icons asset-24…27.
    - `step-product-card`: the `.pcard` and `.dcard` product cards, which take name, size, price and URL from the Shopify product.
    - `home-icon`: stressor and ingredient line icons.
  - `assets/embrae-sections.css` holds `source/css/shared-7p-02.css` plus `index.css`, with the hero background rules dropped. It loads only on the `index` and `product` templates, because the skin quiz uses `.steps` and `.step` differently. Add the system page template to that condition when it is built.
  - `--skin` (asset-00.jpg) is now defined in `snippets/css-variables.liquid`; it is used by the Ectoin animation.
  - `embrae.js` now has the hero carousel (`[data-hero]`, with editor block select support) and the day/night toggle (`[data-daynight]`). Nav listeners now re-bind only when the header reloads.
  - Creator videos: `video` settings on the `step-videos` blocks, uploaded through Content → Files. The placeholder note shows only in the theme editor while a video is missing.
  - Links point to `/pages/our-story`, `/pages/the-embrae-system`, `/pages/skin-quiz` and `/pages/our-ingredients`. The last three pages don't exist yet (Phase 6).
  - Verified: the page renders with no Liquid errors and the prices and sizes come from the products. It has not been compared visually with the source.
- **Phase 5: product pages (2026-11-23/24, pushed to 189665706142). Complete: the 4 single products and the bundle.**
  - User decisions:
    - Product content lives in metafields and metaobjects, not in per-product templates.
    - Reviews use a styled shell with an `@app` block slot; no reviews app yet.
  - Store auth now also has the `metaobject_definitions`, `metaobjects` and `files` scopes.
  - Metaobject types (merchant-owned, storefront `PUBLIC_READ`): `embrae_ingredient`, `embrae_icon_item`, `embrae_how_to_step` and `embrae_scene`.
  - 22 product metafield definitions in the `embrae.*` namespace, all pinned. Main fields: `step`, `eyebrow`, `tagline`, `texture`, `when_to_use`, `benefits`, `gallery_ingredients`, `key_ingredients`, `texture_caption`, `quick_steps`, `made_for`, `routine_heading`, `routine_text`, `routine_products`, `claims`, `howto_pills`, `howto`, `inci`, `storage`, `scenes`, `reels` and `info`.
  - All 4 products are filled: 96 metaobjects, plus `descriptionHtml` set from the page's `.pd-desc` text.
  - Pipeline:
    - `tools/extract_pdp.py` reads the source pages and writes:
      - `source/pdp/*.json`.
      - `snippets/pdp-icon.liquid` (line icons, PNG-mask claim icons and `quality-marks`).
      - `snippets/ingredient-art.liquid`.
      - `snippets/pdp-art-<step>.liquid`. These hold the bespoke markup for each product: texture panel and thumb, Craft tab, step tab and scenes 1–3. They are kept as code because each one is a custom interactive illustration.
    - `tools/setup_pdp_data.py` pushes that content to the store. It is additive and re-runnable: it upserts by handle and only writes `embrae.*` fields.
    - `tools/build_pdp_css.py` writes `assets/embrae-pdp-<step>.css`. Each file is that page's full CSS minus base, in source order. `theme.liquid` loads it based on `product.metafields.embrae.step`.
  - Sections:
    - `pdp-main`: gallery, buy box, routine add-ons and sticky bar.
    - `pdp-offer-banner`.
    - `pdp-inside`: Craft, step and Essentials tabs. It also holds the JS for the drag-compare, the serum stepper and the day-arc.
    - `pdp-real-days`: shows a scene's image if set, otherwise its illustration.
    - `pdp-reels`: shows the `reels` videos, otherwise placeholders.
    - `pdp-reviews`: shell plus `@app` blocks; reads `reviews.rating` if an app fills it.
    - `pdp-more`.
    - `templates/product.json` wires them together.
  - Cart: add-on checkboxes are `name="addon"` with `form="pdp-form-…"`. The global submit handler in `embrae.js` adds the main item plus the add-ons at the same quantity. Buttons with `data-buy-now` go straight to `/checkout`.
  - Verified:
    - All 4 PDPs return 200 with no Liquid errors and load the right CSS.
    - A cart add of the main product plus 2 add-ons at quantity 2 worked; the test cart was cleared afterwards.
    - The JS passes `node --check`.
    - Not compared visually with the source yet.
  - **Bundle (2026-11-24): done.**
    - The product has `templateSuffix: bundle` and uses `templates/product.bundle.json`. That template has `pdp-bundle-main`, `pdp-bundle-inside` and `pdp-bundle-why`, and reuses `pdp-reels`, `pdp-reviews` and `pdp-more`.
    - Its fields are `step=bundle`, `eyebrow`, `tagline`, `claims`, `storage` and `info`, plus `routine_products`, which lists the 4 included products in step order.
    - Calculated from `routine_products`, so they stay in sync with the products: the "What's inside" list, the sizes, the key-ingredient names, the full ingredient lists, the individual value of ₹4,496, the ₹297 saving and the value-bar width.
    - "See it in use" uses section blocks (product, text, `video`). When a video ends the next step plays. A step with no video shows its scene for 7 seconds.
    - Bespoke art is in `snippets/pdp-art-bundle.liquid`, generated by `extract_pdp.py`: the Routine tab, the Ectoin art and scenes 1–4. Its CSS is `assets/embrae-pdp-bundle.css`.
    - The buy-box JS is now in `snippets/pdp-buy-scripts.liquid`, which both `pdp-main` and `pdp-bundle-main` render.
    - Verified: HTTP 200, no Liquid errors, the values are right, and a cart add of the bundle at ₹4,199 worked (test cart cleared). Not compared visually with the source.
    - The live theme has no `product.bundle` template, so on the live theme this product falls back to its default product template. That is harmless, because the live theme is not used for EMBRAE.
- **Visual QA (2026-11-24): `qa/`**
  - Tools:
    - `qa/shoot.mjs` uses puppeteer-core with `/usr/bin/chromium`. It screenshots each source page and its preview-theme page at 1440 px and 390 px, freezes animations and removes `#backend-seo`.
    - `qa/compare.py` writes side-by-side chunks to `qa/shots/cmp/` with a diff score for each.
    - `qa/probe.mjs` prints the computed heights for a selector on both sides.
  - Run steps:
    1. Serve the source pages: `python3 -m http.server 8765 --bind 127.0.0.1 --directory source`. CSS masks don't load from `file://`.
    2. Shoot: `STORE_PASSWORD=… bun qa/shoot.mjs [pages]`.
    3. Compare: `python3 qa/compare.py`.
  - Fixed during QA:
    1. The sprite `#wmimg` (the bottle wordmark) pointed at `../assets/asset-04.png` and now uses `embrae-logo.png | asset_url`.
    2. Source HTML comments were leaking as visible text into `pdp-art-*`, because bs4 prints a Comment without `<!-- -->`. `extract_pdp.py` now strips comments via `parse()`.
    3. Cascade order. Loading `embrae-base.css` first and the page CSS after reordered rules; for example the mobile `.step-grid` row-gap was 28 px instead of 48 px. `build_pdp_css.py` now writes each page's complete CSS in source order (`embrae-sections.css` for the home page, `embrae-pdp-<step>.css` for products). `theme.liquid` loads one of these instead of base; other pages still get `embrae-base.css`.
  - Result: home and all 5 product pages match the source pixel for pixel apart from three intentional differences:
    - The placeholder-video note only shows in the editor.
    - There is no "Write a review" button, because a reviews app will supply it.
    - The footer social icons are hidden until the URLs are set in theme settings (Social links).
  - The user gave the storefront password in chat for `theme dev --store-password`. It is deliberately not written to this file.
- **Phase 6: content pages (2026-11-24, pushed to 189665706142). Complete; every page was checked against the source.**
  - Store changes:
    - User decision: the template suffix on existing pages may change. Their content is never edited.
    - New pages with SEO metafields: `the-embrae-system`, `skin-quiz`, `our-ingredients`, `our-values`.
    - Suffix changes on existing pages, all from `page`: `our-story` to `embrae-our-story`, `why-we-exist` to `embrae-why-we-exist`, `our-philosophy` to `embrae-our-philosophy`, `a-note-from-the-founder` to `embrae-a-note-from-the-founder`.
    - Why the `embrae-` prefix: the live theme has its own `page.our-philosophy`, `page.why-we-exist`, `page.faq` and other page templates, so a plain suffix would change the live site. With the prefix, the live theme falls back to `page.json`, exactly as before (it has no `page.page`).
    - `faqs` keeps its suffix `faq`. The new theme's `page.faq.json` serves it, and the live theme keeps its own `page.faq`.
    - Rollback for the 4 pages: set their suffix back to `page`.
    - New blog `journal` (blog suffix `journal`) with 12 articles (article suffix `journal`). The `news` blog is untouched. The source has 12 articles, not 16.
    - Article metafields: `embrae.read_time`, `embrae.related` (handles) and `embrae.stage`, plus the SEO fields `global.title_tag` and `global.description_tag`.
    - `embrae_ingredient` gained the fields `inci`, `what`, `why` and `products`, and now holds all 68 library entries. Entries with `what` set appear on the Our Ingredients page.
    - New metaobject type `embrae_faq` (question, rich-text answer, topic, category, product, sort) with 99 entries, `faq-001` to `faq-099`.
  - Tools:
    - `tools/links.py`: shared `link()`, `parse()` (strips comments) and `ARTICLE_PAGES`.
    - `tools/shop.py`: shared `gql()`, `check()` and `--dry-run`.
    - `tools/build_pages.py`: writes the page, blog and article templates from the source pages, plus `snippets/ph-art.liquid` (placeholder illustrations keyed `<page>-<n>`) and `assets/embrae-quiz.js`. The quiz is the source script with asserted substitutions: Shopify variants, prices and URLs come from `window.EmbraeQuiz`, and a cart add opens the drawer.
    - `tools/setup_pages.py`: creates pages and sets suffixes; additive.
    - `tools/setup_ingredients.py`, `tools/setup_faqs.py` and `tools/setup_journal.py`: fill the store. `setup_journal.py` also writes `snippets/journal-art.liquid`.
    - `tools/build_pdp_css.py`: now also writes `embrae-page-<name>.css` for the content pages and the article.
  - `theme.liquid` picks the page CSS by suffix (stripping a leading `embrae-`, from a whitelist), or by blog/article suffix `journal`.
  - Sections:
    - System page: `system-hero`, `system-day-night`, `system-steps` (sticky step bar). It reuses `pdp-offer-banner`, which gained `style: sy-fin`, `separator` and `anchor`.
    - Quiz page: `quiz-how`, `skin-quiz` (product pickers feed the cart data), `product-steps-cards`.
    - Shared: `page-hero` and `ph-media` (an image, or the placeholder illustration), `page-split`, `page-band`, `page-prose` (blocks: paragraphs, pull quote, emphasis, signature, closing; optional founder side image), `page-cards` (styles `pr`, `st4`, `mg`), `values-tabs`, `page-intro`. `routine-offer` gained `compact`, which renders `.pre.sm`.
    - `ingredient-library`: reads the metaobjects, sorts by name, and keeps the A–Z, search and product-filter JS. It fetches entries by position, because `metaobjects.type[handle]` lookups are capped per page.
    - `faq-tabs`: tabs are blocks; each shows the FAQs whose `topic` matches, grouped by `category`.
    - Journal: `journal-index` (newest note featured, the next N beside it, then the grid with "Discover more notes") and `journal-curated` (Most read or Picked, using article pickers).
    - Articles: `article-main` (header, hero, a table of contents built from `<h2 id>` in the body, the body, add-to-cart for `data-add` buttons, and live prices for the `.ar-bp` banners) and `article-extras` (quiz prompt, routine band with [price]/[value]/[saving] tokens, related articles).
  - Gotchas found during this phase:
    - Liquid `remove_first: 'embrae-'` also strips the middle of `the-embrae-system`.
    - `article.handle` includes `journal/`. Use `| split: '/' | last`, and `articles['journal/<handle>']` for lookups.
    - Don't name snippet params or variables `article` or `handle`; they collide with Liquid globals.
    - The storefront caches pages for a few seconds after a push; add a `cb=` query parameter when checking.
  - Verified:
    - All 28 pages were compared at 1440 px and 390 px against the source. They match pixel for pixel except the three intentional differences listed under QA.
    - The quiz was tested end to end in headless Chromium: 10 answers, its result, add to cart (3 products, ₹3,197) and the drawer opening.
    - The FAQ HTML matches the source for all 99 questions.

- **Phase 7: SEO (2026-11-26, pushed to 189665706142). Theme side done; the store settings checklist is waiting on the user.**
  - `snippets/meta-tags.liquid` changes:
    - The title brand check is now case-insensitive. Source titles end in "| EMBRAE" and the shop is named "Embrae", so " – Embrae" used to be appended twice.
    - `og:image` falls back to the new theme setting `share_image`.
    - Product JSON-LD moved behind the setting `product_schema`, off by default. The SEO brief says to add Product schema only once real reviews exist (the bundle: once it's live), and never to mark up a rating.
  - `snippets/structured-data.liquid`:
    - Home: Organization and WebSite, with SearchAction, `sameAs` from the social settings, and `contactPoint` from the settings `org_email`/`org_phone`.
    - FAQ page: FAQPage built from all 99 `embrae_faq` entries.
    - Journal articles: BlogPosting.
  - New theme settings group "SEO and sharing": `share_image`, `org_email`, `org_phone`, `product_schema`.
  - `tools/setup_seo.py` fills empty `global.title_tag`/`description_tag` fields from `source/seo`. It only writes fields that are blank. It filled `why-we-exist`, `our-philosophy`, `our-story`, `a-note-from-the-founder`, `faqs` and the `journal` blog. These are store-level, so the live theme shows the new titles too.
  - `qa/seo-audit.py` (`STORE_PASSWORD=… python3 qa/seo-audit.py`) checks every page: title matches `source/seo`, a meta description exists, exactly one H1, the JSON-LD parses, and there's no Liquid error. Result: 27 of 28 pages pass. The home page fails only because its title and description are store settings.
  - Gotcha: `theme push` prints "could not be pushed" on a rejected file, so check for "pushed successfully" rather than "pushed". Also, `{…}` braces inside a `{{ }}` output tag break the Liquid parser; build the string with `capture` instead.
  - **Store settings for the user to do in the admin.** There's no API for some of these, and the rest need the user's content plus extra scopes:
    1. Online Store → Preferences: set the home title to "EMBRAE | Skincare designed for real Indian life", and the meta description from `source/seo/index.json`.
    2. Settings → Policies: Refund, Terms and Shipping return 404, and the footer links to them. Only Privacy exists. The user must supply or approve the text.
    3. Settings → Shipping: an India zone, free shipping on orders of ₹999 and above, and a rate for smaller orders (amount needed from the user).
    4. Settings → Taxes: GST registration. Prices already include tax, which matches "MRP inclusive of all taxes".
    5. Settings → General → Store currency → Currency formatting: currently "Rs. {{amount}}", which checkout and emails also use. Suggested "₹{{amount_no_decimals}}".
    6. Settings → Payments: an India gateway (for example Razorpay, PayU or Shopify Payments if available) and a test order.
    7. Theme settings → Social links (the footer and `sameAs`) and a default share image.

## Open decisions (ask the user)
1. Social media URLs for the footer: Theme settings → Social links.
2. Still pending from the user:
   - Reviews app (Judge.me or Loox).
   - WhatsApp signup app, if any.
   - Approved photography and videos: upload in Content → Files and pick them in the theme editor.
   - Helvena web licence.
   - Payment methods and GST text.
   - The money format (currently `Rs.{{amount}}`; the theme shows ₹ on its own).
3. Already decided: EMBRAE products are ACTIVE; the demo `le-*` products are left alone; the Travel Pouch ships inside the bundle with no discount.

## Next steps
- Phases 0–6 are done.
- **Phase 7:** the theme side is done. The store-settings checklist above waits on the user.
- **Phase 8:** QA and launch. Accessibility pass, Lighthouse, a cross-browser check, and a checkout test with a test payment gateway. Then publish with the user's go-ahead, because publishing replaces the live theme.
- After each change: run `theme check`, then `theme push` to theme 189665706142. **Never push to the live theme.**
