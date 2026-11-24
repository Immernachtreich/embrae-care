#!/usr/bin/env python3
"""Build Online Store 2.0 page templates (embraecare/templates/page.<name>.json) from the source pages.

Each page is described as a list of sections whose settings/blocks are read from source/pages/<name>.html,
so the copy lands in the theme editor instead of in code. Re-run after editing the source.
Usage: python3 tools/build_pages.py [page ...]
"""
import json, re, sys
from pathlib import Path
from links import link, parse as parse_html

root = Path(__file__).resolve().parent.parent

PRODUCT_BY_STEP = {"reset": "reset-cleanser", "defend": "urban-defense-serum",
                   "adapt": "climate-adapt-moisturizer", "protect": "daily-shield-sunscreen"}


def parse(name):
    return parse_html((root / f"source/pages/{name}.html").read_text())


def text(el):
    return re.sub(r"\s+", " ", el.get_text(" ", strip=True)).replace(" ,", ",").replace(" .", ".") if el else ""


def lines(els):
    return "\n".join(text(e) for e in els)


def template(sections):
    """[(key, type, settings, blocks)] -> template dict; blocks = [(type, settings)]."""
    out = {"sections": {}, "order": []}
    for key, typ, settings, blocks in sections:
        sec = {"type": typ, "settings": settings}
        if blocks:
            sec["blocks"] = {f"{key}-{i}": {"type": t, "settings": s} for i, (t, s) in enumerate(blocks, 1)}
            sec["block_order"] = list(sec["blocks"])
        out["sections"][key] = sec
        out["order"].append(key)
    return out


def offer_banner(sec, style=""):
    """.pd-banner closing offer -> pdp-offer-banner settings."""
    return {"heading": text(sec.h2), "text": text(sec.select_one("p.l")),
            "offer_price": text(sec.select_one(".offer-line b")), "offer_compare": text(sec.select_one(".offer-line s")),
            "button_label": text(sec.select_one("a.btn")), "button_link": link(sec.select_one("a.btn")["href"]),
            "chip": sec.select_one(".pouch-chip").decode_contents().replace("<br/>", "\n"),
            "separator": bool(sec.select_one(".ol-sep")), "style": style, "anchor": sec.get("id", "offer")}


def the_embrae_system():
    s = parse("the-embrae-system")
    hero, band = s.select_one(".sy-hero"), s.select_one(".sy-band")
    h1 = hero.h1
    sub = h1.span.extract().get_text(strip=True) if h1.span else ""
    steps = []
    for sec in s.select(".sy-sec"):
        tints = dict(re.findall(r"--(t\d):(#[0-9A-Fa-f]+)", sec["style"]))
        ct = sec.select_one(".ct")
        g = {text(d.small): text(d.b) for d in ct.select(".glance > div")}
        steps.append(("step", {
            "step": sec["id"], "product": PRODUCT_BY_STEP[sec["id"]], "tag": text(ct.select_one(".tag")),
            "role": text(ct.select_one(".role")), "feels": g.get("Feels like", ""), "use": g.get("Use", ""),
            "fits": g.get("Where it fits", ""), "points": lines(ct.select(".pts li")),
            "ingredients": "\n".join(f"{text(i.b)} | {text(i.p)}" for i in ct.select(".ings .ing")),
            "how": lines(ct.select(".how li")), "note": text(ct.select_one(".note")),
            "idea": text(ct.select_one(".idea p")), "tint_1": tints.get("t1", ""), "tint_2": tints.get("t2", "")}))
    last = s.select(".sy-sec")[-1].select_one("a.nxt")
    tl = band.select(".sy-tr")
    return template([
        ("hero", "system-hero", {"eyebrow": text(hero.select_one(".eyebrow")), "heading": text(h1), "subheading": sub,
                                 "text": text(hero.select_one(".lead")), "button_label": text(hero.select_one(".sy-acts a")),
                                 "button_link": hero.select_one(".sy-acts a")["href"]}, []),
        ("day", "system-day-night", {"eyebrow": text(band.select_one(".eyebrow")), "heading": text(band.h2),
                                     "text": text(band.select_one(".lead")),
                                     "morning": text(tl[0].select_one(".lab b")), "morning_steps": text(tl[0].select_one(".lab small")),
                                     "night": text(tl[1].select_one(".lab b")), "night_steps": text(tl[1].select_one(".lab small")),
                                     "morning_only": text(tl[1].select_one(".sy-n.off small"))}, []),
        ("steps", "system-steps", {"nav_label": s.select_one(".sy-bar")["aria-label"], "final_label": text(last),
                                   "final_link": last["href"]}, steps),
        ("routine", "pdp-offer-banner", offer_banner(s.select_one(".sy-fin"), "sy-fin"), []),
    ])


PH = {}  # placeholder illustration key -> svg markup, written to snippets/ph-art.liquid


def placeholder(page, ph):
    """Register a .ph.sc placeholder illustration; returns (key, tone letter, label)."""
    key = f"{page}-{sum(1 for k in PH if k.startswith(page + '-')) + 1}"
    PH[key] = liquidize(str(ph.select_one("svg.sc")))
    tone = next(c for c in ph["class"] if c not in ("ph", "sc"))
    return key, tone, ph.get("aria-label", "").replace("Placeholder illustration: ", "")


def liquidize(html):
    html = re.sub(r'href="([^"]+)"', lambda m: f'href="{link(m.group(1))}"', html)
    return re.sub(r"\.\./assets/(asset-\d+\.\w+)", lambda m: "{{ '" + ASSET_NAMES.get(m.group(1), m.group(1)) + "' | asset_url }}", html)


ASSET_NAMES = {"asset-04.png": "embrae-logo.png", "asset-10.jpg": "about-story.jpg", "asset-11.jpg": "about-values.jpg"}


def hero(page, sec):
    """.hx page hero -> page-hero settings."""
    key, tone, label = placeholder(page, sec.select_one(".ph.sc"))
    a = sec.select_one(".wrap a.btn")
    return {"placeholder": key, "tone": tone, "image_label": label, "eyebrow": text(sec.select_one(".wrap .eyebrow")),
            "heading": text(sec.h1), "text": text(sec.select_one(".wrap .lead")),
            "button_label": text(a), "button_link": link(a["href"]) if a else ""}


def offer_small(sec):
    """.pre.sm closing banner -> routine-offer settings (compact)."""
    a = sec.select_one("a.btn")
    return {"heading": text(sec.h2), "text": text(sec.select_one(".lead")), "offer_price": "", "offer_compare": "",
            "button_label": text(a), "button_link": link(a["href"]), "compact": True}


def skin_quiz():
    s = parse("skin-quiz")
    secs = s.select("main > section")
    how, cards = secs[1], secs[3]
    P = {**PRODUCT_BY_STEP}
    return template([
        ("hero", "page-hero", hero("skin-quiz", secs[0]), []),
        ("how", "quiz-how", {"heading": text(how.h2), "text": text(how.select_one(".sec-head .lead"))},
         [("step", {"title": text(st.b), "text": text(st.p)}) for st in how.select(".qh-step")]),
        ("quiz", "skin-quiz", {**P, "bundle": "daily-urban-defense-routine"}, []),
        ("steps", "product-steps-cards", {"heading": text(cards.h2), "text": text(cards.select_one(".sec-head .lead"))},
         [("card", {"product": P[c.select_one("use")["href"][3:]], "text": text(c.p)}) for c in cards.select(".qs-c")]),
        ("offer", "routine-offer", offer_small(secs[4]), []),
    ])


def intro(sec, style):
    return {"style": style, "heading": text(sec.h1), "text": text(sec.select_one(".lead"))}


def our_ingredients():
    s = parse("our-ingredients")
    secs = s.select("main > section")
    return template([
        ("intro", "page-intro", intro(secs[0], "ix-top"), []),
        ("library", "ingredient-library", {"heading": text(secs[1].select_one(".sec-head h2")),
                                           "products": list(PRODUCT_BY_STEP.values())}, []),
        ("offer", "routine-offer", offer_small(secs[2]), []),
    ])


def faqs():
    s = parse("faqs")
    secs = s.select("main > section")
    return template([
        ("intro", "page-intro", intro(secs[0], "fq-top"), []),
        ("faqs", "faq-tabs", {"label": s.select_one(".ftabs")["aria-label"]},
         [("tab", {"label": text(b), "topic": b["id"].removeprefix("ft-")}) for b in s.select(".ftab")]),
        ("offer", "routine-offer", offer_small(secs[2]), []),
    ])


def richtext(ps):
    """<p> elements -> richtext setting HTML (Shopify allows p/a/strong/em/br only)."""
    out = []
    for p in ps:
        for t in p.find_all(True):
            assert t.name in ("a", "strong", "b", "em", "i", "br"), f"unsupported tag in richtext: {t.name}"
            t.attrs = {"href": link(t["href"])} if t.name == "a" else {}
        out.append("<p>" + p.decode_contents().strip() + "</p>")
    return "".join(out)


def phm(page, ph):
    key, tone, label = placeholder(page, ph)
    return {"placeholder": key, "tone": tone, "image_label": label}


def about_page(page):
    """hx / split / band / pg(prose|cards|values) / pre.sm -> generic sections, in source order."""
    secs, n = [], 0
    for sec in parse(page).select("main > section"):
        n += 1
        cls, key = sec.get("class", []), f"s{n}"
        base = {"tint": "tint" in cls, "no_top": "padding-top:0" in (sec.get("style") or "")}
        cta = sec.select_one(".cta-c a.btn")
        btn = {"button_label": text(cta), "button_link": link(cta["href"])} if cta else {}
        if "hx" in cls:
            secs.append((key, "page-hero", hero(page, sec), []))
        elif "split" in cls:
            tx = sec.select_one(".tx"); a = tx.select_one("a.btn")
            secs.append((key, "page-split", {**phm(page, sec.select_one(".ph.sc")), "wide": "w" in cls, "reverse": "rev" in cls,
                         "eyebrow": text(tx.select_one(".eyebrow")), "heading": text(tx.select_one("h2")),
                         "text": richtext([p for p in tx.select(":scope > p") if "eyebrow" not in p.get("class", [])]),
                         "button_label": text(a), "button_link": link(a["href"]) if a else ""}, []))
        elif "band" in cls:
            secs.append((key, "page-band", {"eyebrow": text(sec.select_one(".eyebrow")), "heading": text(sec.select_one("h2")),
                                            "text": text(sec.select_one(".lead"))}, []))
        elif "pre" in cls:
            secs.append((key, "routine-offer", offer_small(sec), []))
        elif sec.select_one(".prose"):
            blocks, buf = [], []
            def flush():
                if buf: blocks.append(("text", {"text": richtext(buf)})); buf.clear()
            for el in sec.select_one(".prose").find_all(recursive=False):
                c = el.get("class", [])
                if el.name == "p" and el.select_one("span.em"): flush(); blocks.append(("emphasis", {"text": text(el)}))
                elif el.name == "p" and "closing" in c: flush(); blocks.append(("closing", {"text": text(el)}))
                elif el.name == "p": buf.append(el)
                elif "pull" in c: flush(); blocks.append(("pull", {"text": text(el)}))
                elif "sign" in c: flush(); blocks.append(("signature", {"name": text(el.b), "role": text(el.span)}))
                else: raise ValueError(f"{page}: unexpected prose child {el.name}.{c}")
            flush()
            side = sec.select_one(".fnd .side .ph.sc")
            secs.append((key, "page-prose", {**base, **({"portrait_side": True, **phm(page, side)} if side else {})}, blocks))
        elif sec.select_one(".vt"):
            vals = []
            for tab, panel in zip(sec.select(".vt-tab"), sec.select(".vt-panel")):
                inpr = panel.select_one(".inpr"); lab = inpr.b.extract()
                vals.append(("value", {"name": text(tab.b), "heading": text(panel.h3), "text": text(panel.select_one(".tx > p")),
                                       "routine": text(inpr), **phm(page, panel.select_one(".ph.sc"))}))
            secs.append((key, "values-tabs", {"heading": text(sec.select_one(".sec-head h2")),
                                              "label": sec.select_one(".vt-tabs")["aria-label"], "routine_label": text(lab), **btn}, vals))
        elif sec.select_one(".st4, .mg, .pr-grid"):
            style = "st4" if sec.select_one(".st4") else "mg" if sec.select_one(".mg") else "pr"
            cards = []
            for c in sec.select(".st4 > div, .mg > .mt, .pr-grid > .pr"):
                a = c.select_one(":scope > a")
                card = {"title": text(c.h3), "text": text(c.select_one(":scope > p")),
                        "link_label": text(a), "link": link(a["href"]) if a else ""}
                if style == "mg": card.update(phm(page, c.select_one(".ph.sc")))
                cards.append(("card", card))
            secs.append((key, "page-cards", {**base, "style": style, "heading": text(sec.select_one(".sec-head h2")), **btn}, cards))
        else:
            raise ValueError(f"{page}: unmapped section {cls}")
    return template(secs)


def journal_blog():
    s = parse("journal")
    most, picked = s.select_one(".jr-most"), s.select_one(".jr-picked")
    rel = lambda a: a["href"].removesuffix(".html")
    return template([
        ("intro", "page-intro", intro(s.select_one(".jr-top"), "jr-top"), []),
        ("latest", "journal-index", {"side_heading": text(s.select_one(".jr-sh")), "side_count": len(s.select(".jr-si")),
                                     "grid_heading": text(s.select_one(".jr-fresh h2")), "grid_text": text(s.select_one(".jr-fresh .lead2")),
                                     "grid_visible": len(s.select("#jr-grid .jr-card:not([hidden])")),
                                     "more_label": text(s.select_one("#jr-more")), "read_label": text(s.select_one(".jr-rd"))}, []),
        ("most", "journal-curated", {"style": "most", "heading": text(most.h2), "text": text(most.select_one(".lead2"))},
         [("article", {"article": f"journal/{rel(a)}"}) for a in most.select(".jr-rank a")]),
        ("picked", "journal-curated", {"style": "picked", "heading": text(picked.h2), "text": text(picked.select_one(".lead2")),
                                       "read_label": text(picked.select_one(".jr-rd"))},
         [("article", {"article": f"journal/{rel(a)}", "label": text(a.small)}) for a in picked.select(".jr-pk")]),
        ("offer", "routine-offer", offer_small(s.select_one(".pre.sm")), []),
    ])


def journal_article():
    s = parse("how-to-patch-test-a-new-product")  # all articles share this layout
    q, up = s.select_one(".ar-quiz"), s.select_one(".ar-ut")
    routine = text(up.p).replace("₹4,199", "[price]").replace("₹4,496", "[value]").replace("₹297", "[saving]")
    return template([
        ("main", "article-main", {"toc_label": text(s.select_one(".ar-toc > p")), **PRODUCT_BY_STEP,
                                  "bundle": "daily-urban-defense-routine"}, []),
        ("extras", "article-extras", {"quiz_eyebrow": text(q.small), "quiz_heading": text(q.h3), "quiz_button": text(q.a),
                                      "quiz_link": link(q.a["href"]), "bundle": "daily-urban-defense-routine",
                                      "routine_eyebrow": text(up.small), "routine_heading": text(up.h2), "routine_text": routine,
                                      "routine_button": text(up.select_one("a.btn")),
                                      "related_heading": text(s.select_one(".ar-related h2"))}, []),
        ("offer", "routine-offer", offer_small(s.select_one(".pre.sm")), []),
    ])


def write_ph_snippet():
    body = "".join(f"  {{%- when '{k}' -%}}{v}\n" for k, v in PH.items())
    (root / "embraecare/snippets/ph-art.liquid").write_text(
        "{% doc %}\n  Placeholder illustrations from the source pages, shown until a real image is chosen.\n"
        "  Generated by tools/build_pages.py.\n\n  @param {string} key - e.g. skin-quiz-1\n{% enddoc %}\n"
        "{%- case key -%}\n" + body + "{%- endcase -%}\n")


PAGES = {"the-embrae-system": the_embrae_system, "skin-quiz": skin_quiz, "our-ingredients": our_ingredients, "faq": faqs,
         **{f"embrae-{p}": (lambda p=p: about_page(p)) for p in
            ["our-story", "why-we-exist", "our-philosophy", "our-values", "a-note-from-the-founder"]}}



def port_quiz():
    """source skin-quiz script -> assets/embrae-quiz.js, with Shopify data (window.EmbraeQuiz) swapped in."""
    src = re.findall(r'<script(?![^>]*id="pk")[^>]*>(.*?)</script>', (root / "source/pages/skin-quiz.html").read_text(), flags=re.S)[1]
    subs = [
        (re.compile(r"(var C=\{.*?\};\n)", re.S), r"""\1/* Shopify data from sections/skin-quiz.liquid */
var X=window.EmbraeQuiz||{}, URLS=X.urls||{};
if(X.variants) C.cart.variants=X.variants;
if(X.root){ C.cart.addUrl=X.root+'cart/add.js'; C.cart.cartUrl=X.root+'cart'; }
Object.keys(X.prices||{}).forEach(function(k){ if(C.products[k]) C.products[k].price=X.prices[k]; });
"""),
        ("({reset:'reset-cleanser.html',defend:'urban-defense-serum.html',adapt:'climate-adapt-moisturizer.html',protect:'daily-shield-sunscreen.html'})", "URLS"),
        ("\\u20B94,199 instead of \\u20B94,496.", "'+money(X.bundlePrice)+' instead of '+money(X.bundleValue)+'."),
        ("document.dispatchEvent(new CustomEvent('cart:refresh'));", "if(window.EmbraeCart) EmbraeCart.refresh().then(function(){ EmbraeCart.open(); });"),
    ]
    for old, new in subs:
        n = len(old.findall(src)) if hasattr(old, "findall") else src.count(old)
        assert n >= 1, f"quiz port: pattern not found: {old}"
        src = old.sub(new, src, count=1) if hasattr(old, "sub") else src.replace(old, new)
    out = root / "embraecare/assets/embrae-quiz.js"
    out.write_text("/* Skin quiz, ported from source/pages/skin-quiz.html by tools/build_pages.py. Edit the source and re-run. */\n" + src)
    print("wrote", out.name)

if __name__ == "__main__":
    port_quiz()
    for name in sys.argv[1:] or PAGES:
        out = root / f"embraecare/templates/page.{name}.json"
        out.write_text(json.dumps(PAGES[name](), indent=2, ensure_ascii=False) + "\n")
        print("wrote", out.name)
    for name, fn in (("blog.journal", journal_blog), ("article.journal", journal_article)):
        (root / f"embraecare/templates/{name}.json").write_text(json.dumps(fn(), indent=2, ensure_ascii=False) + "\n")
        print("wrote", name + ".json")
    write_ph_snippet()
