#!/usr/bin/env python3
"""Pull per-product content out of the four product pages.

Writes:
  source/pdp/<handle>.json        content that goes into product metafields / metaobjects
  source/pdp/icons.json           icon key -> inner SVG markup (line icons, viewBox kept)
  source/pdp/ingredient-art.json  ingredient key -> medallion SVG (viewBox 0 0 100 100)
  embraecare/snippets/pdp-art-<step>.liquid  bespoke art/markup per product (craft tab, step tab, texture, scenes)
"""
import json, re, sys
from pathlib import Path
from bs4 import BeautifulSoup
from links import link, parse

root = Path(__file__).resolve().parent.parent
PAGES = ["reset-cleanser", "urban-defense-serum", "climate-adapt-moisturizer", "daily-shield-sunscreen"]
PRODUCTS = set(PAGES) | {"daily-urban-defense-routine"}
out = root / "source/pdp"; out.mkdir(exist_ok=True)





def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")





def liquidize(html):
    """Rewrite links and asset refs inside copied markup."""
    html = re.sub(r'href="([^"]+)"', lambda m: f'href="{link(m.group(1))}"', html)
    html = re.sub(r"\.\./assets/(asset-\d+\.\w+)", lambda m: "{{ '" + m.group(1) + "' | asset_url }}", html)
    return html


def inner(tag):
    return "".join(str(c) for c in tag.contents).strip()


def text(tag):
    return re.sub(r"\s+", " ", tag.get_text(" ", strip=True)) if tag else ""


icons, icon_by_markup = {}, {}


def icon_key(svg, label):
    # Some claims use a PNG mask (<i class="pk" style="--m:url(../assets/asset-NN.png)">) instead of an SVG.
    if svg is None or svg.name != "svg":
        pk = (svg.select_one(".pk") if svg is not None else None)
        m = re.search(r"asset-\d+\.png", pk["style"]) if pk else None
        if not m:
            raise ValueError(f"no icon for {label}")
        return m.group(0)
    markup = re.sub(r"\s+", " ", str(svg)).strip()
    if markup in icon_by_markup:
        return icon_by_markup[markup]
    k = base = slug(label)[:40] or "icon"
    n = 2
    while k in icons:
        k = f"{base}-{n}"; n += 1
    icons[k] = markup
    icon_by_markup[markup] = k
    return k


ing_art, ing_names = {}, {}


def ingredient(svg, name):
    k = slug(name)
    markup = re.sub(r"\s+", " ", str(svg)).strip()
    norm = lambda m: re.sub(r'(id="|url\(#)[^")]+', r"\1", m)  # gradient ids differ per instance
    if k in ing_art and norm(ing_art[k]) != norm(markup):
        print(f"warn: ingredient art differs for {name}", file=sys.stderr)
    ing_art.setdefault(k, markup)
    ing_names.setdefault(k, name)
    return k


for handle in PAGES:
    soup = parse((root / f"source/pages/{handle}.html").read_text())
    top = soup.select_one("section.pd-top")
    info = top.select_one(".pd-info")
    step = top.select_one(".pd-pan.pan1 svg.prod use")["href"].removeprefix("#p-")
    pans = {p["data-i"]: p for p in top.select(".pd-pan")}
    d = {"handle": handle, "step": step}
    d["eyebrow"] = text(info.select_one("p.eyebrow"))
    d["tagline"] = text(info.select_one(".pd-tag"))
    d["description"] = text(info.select_one(".pd-desc"))
    d["glance"] = [[text(x.small), text(x.b)] for x in info.select(".glance > div")]
    d["image_alt"] = pans["0"].get("aria-label", "")
    d["benefits"] = [text(li) for li in pans["1"].select("li")]
    d["gallery_ingredients"] = [ingredient(x.select_one("svg"), text(x.b)) for x in pans["2"].select(".g > div")]
    d["texture_caption"] = text(pans["3"].select_one(".cap"))
    d["key_ingredients"] = [{"key": ingredient(li.select_one(".md svg"), text(li.b)), "name": text(li.b),
                             "benefit": text(li.select_one("em")), "descriptor": text(li.small)}
                            for li in info.select(".igrid li")]
    d["quick_steps"] = [{"icon": icon_key(li.svg, text(li.b.contents[-1]) if li.b else ""),
                         "label": text(li.b).split(" ", 1)[-1]} for li in info.select(".hgrid li")]
    d["made_for"] = [{"icon": icon_key(li.svg, text(li.b)), "label": text(li.b)} for li in info.select(".mrow li")]
    rb = info.select_one(".rb")
    d["routine_heading"], d["routine_text"] = text(rb.h3), text(rb.p)

    inside = soup.select_one("#inside")
    d["tabs"] = [text(b) for b in inside.select(".itab")]
    ess = inside.select_one("#ip3")
    d["essentials_heading"] = text(ess.select_one(".sec-head h2"))
    d["claims"] = [{"icon": icon_key(li.svg or li, text(li.b)), "label": text(li.b)} for li in ess.select(".isrow li")]
    hw = ess.select_one(".hw")
    d["howto_pills"] = [text(s) for s in hw.select(".hw-pills span")]
    d["howto"] = [{"icon": icon_key(c.select_one(".hw-ic svg"), text(c.h4)), "title": text(c.h4),
                   "text": inner(c.select_one(".hw-b p"))} for c in hw.select(".hw-c")]
    det = {text(x.summary): x for x in ess.select("details")}
    d["inci"] = text(det["Full ingredients"].select_one(".inci-p"))
    d["storage"] = liquidize(inner(det["Storage and precautions"].select_one(".ab")))

    rdb = soup.select_one("#rdb")
    d["scenes"] = [{"title": text(s.select_one(".rdt b")), "text": text(s.select_one(".rdt p"))} for s in rdb.select(".rds")]

    more = soup.select_one("#more")
    d["info"] = []
    for ii in more.select(".ii"):
        label = text(ii.b)
        d["info"].append({"icon": icon_key(ii.select_one(".md svg"), label), "label": label,
                          "text": inner(ii.select_one("div > p"))})

    (out / f"{handle}.json").write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")

    # Bespoke markup kept as code, one snippet per product step.
    parts = {
        "texture": inner(pans["3"]),
        "texture_thumb": inner(top.select(".pd-th")[3]),
        "craft": inner(inside.select_one("#ip1")),
        "tab": inner(inside.select_one("#ip2")),
    }
    for i, s in enumerate(rdb.select(".rds"), 1):
        parts[f"scene{i}"] = str(s.select_one("svg"))
    body = "".join(f"  {{%- when '{k}' -%}}\n{liquidize(v)}\n" for k, v in parts.items())
    (root / f"embraecare/snippets/pdp-art-{step}.liquid").write_text(
        "{% doc %}\n  Bespoke art and interactive markup for this product, copied from the source page.\n"
        "  Generated by tools/extract_pdp.py; edit the source and re-run rather than editing by hand.\n\n"
        "  @param {string} part - texture, texture_thumb, craft, tab, scene1, scene2, scene3\n{% enddoc %}\n"
        "{%- case part -%}\n" + body + "{%- endcase -%}\n")

(out / "ingredient-names.json").write_text(json.dumps(ing_names, indent=1, ensure_ascii=False) + "\n")
(out / "ingredient-art.json").write_text(json.dumps(ing_art, indent=1, ensure_ascii=False) + "\n")
print(len(icons), "icons;", len(ing_art), "ingredients:", ", ".join(ing_art))

# Shared lookups as snippets: line icons (or PNG masks) and ingredient medallions.
qmk = parse((root / f"source/pages/{PAGES[0]}.html").read_text()).select_one("#more .qmk")
icon_cases = "".join(f"  {{%- when '{k}' -%}}{v}\n" for k, v in icons.items())
(root / "embraecare/snippets/pdp-icon.liquid").write_text(
    "{% doc %}\n  Line icons from the product pages. Generated by tools/extract_pdp.py.\n"
    "  A key ending in .png renders that theme asset as a CSS mask (claim icons from the pack artwork).\n\n"
    "  @param {string} name - Icon key, e.g. pump, cruelty-free, asset-31.png; 'quality-marks' renders the GMP/FDA/ISO marks\n{% enddoc %}\n"
    "{%- if name contains '.png' -%}\n  <i class=\"pk\" style=\"--m:url({{ name | asset_url }})\"></i>\n{%- else -%}\n"
    "{%- case name -%}\n" + icon_cases + f"  {{%- when 'quality-marks' -%}}{inner(qmk)}\n{{%- endcase -%}}\n{{%- endif -%}}\n")
art_cases = "".join(f"  {{%- when '{k}' -%}}{v}\n" for k, v in ing_art.items())
(root / "embraecare/snippets/ingredient-art.liquid").write_text(
    "{% doc %}\n  Ingredient medallion art. Generated by tools/extract_pdp.py.\n\n"
    "  @param {string} name - Ingredient art key, e.g. niacinamide\n{% enddoc %}\n"
    "{%- case name -%}\n" + art_cases + "{%- endcase -%}\n")

# Bundle page: bespoke illustrations only (its products, prices and ingredients come from the included products).
bsoup = parse((root / "source/pages/daily-urban-defense-routine.html").read_text())
bparts = {"routine": inner(bsoup.select_one("#ip1")), "ectoin": str(bsoup.select_one("#why .bd-ect"))}
for i, s in enumerate(bsoup.select("#vu .vu-s svg"), 1):
    bparts[f"scene{i}"] = str(s)
binfo = bsoup.select_one(".pd-info")
bundle = {"handle": "daily-urban-defense-routine", "step": "bundle",
          "eyebrow": text(binfo.select_one("p.eyebrow")), "tagline": text(binfo.select_one(".pd-tag")),
          "description": text(binfo.select_one(".pd-desc")),
          "claims": [{"icon": icon_key(li.svg or li, text(li.b)), "label": text(li.b)} for li in bsoup.select("#ip3 .isrow li")],
          "storage": liquidize(inner(bsoup.select("#ip3 details")[1].select_one(".ab"))),
          "info": [{"icon": icon_key(ii.select_one(".md svg"), text(ii.b)), "label": text(ii.b), "text": inner(ii.select_one("div > p"))}
                   for ii in bsoup.select("#more .ii")]}
(out / "daily-urban-defense-routine.json").write_text(json.dumps(bundle, indent=2, ensure_ascii=False) + "\n")
(root / "embraecare/snippets/pdp-art-bundle.liquid").write_text(
    "{% doc %}\n  Bespoke art for the routine bundle page, copied from the source page.\n"
    "  Generated by tools/extract_pdp.py; edit the source and re-run rather than editing by hand.\n\n"
    "  @param {string} part - routine, ectoin, scene1 … scene4\n{% enddoc %}\n"
    "{%- case part -%}\n" + "".join(f"  {{%- when '{k}' -%}}\n{liquidize(v)}\n" for k, v in bparts.items()) + "{%- endcase -%}\n")

(out / "icons.json").write_text(json.dumps(icons, indent=1, ensure_ascii=False) + "\n")
