#!/usr/bin/env python3
"""Fetch every built page from the preview theme and report <title>, meta description, H1 count and JSON-LD validity.
Usage: STORE_PASSWORD=... python3 qa/seo-audit.py"""
import http.cookiejar, json, os, random, re, urllib.parse, urllib.request
from pathlib import Path

STORE, THEME = "https://embraecare.myshopify.com", "189665706142"
root = Path(__file__).resolve().parent.parent
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
op.open(f"{STORE}/password", urllib.parse.urlencode({"form_type": "storefront_password", "password": os.environ["STORE_PASSWORD"]}).encode())
seo = {json.loads(f.read_text()).get("handle"): json.loads(f.read_text()) for f in (root / "source/seo").glob("*.json")}
seo.pop(None, None)  # coming-soon has no handle
problems = 0
for path, src in sorted(seo.items()):
    if not path:
        continue
    html = op.open(f"{STORE}{path}?preview_theme_id={THEME}&cb={random.random()}").read().decode()
    title = re.sub(r"\s+", " ", re.search(r"<title>(.*?)</title>", html, re.S).group(1)).strip().replace("&ndash;", "–")
    desc = (re.search(r'<meta\s+name="description"\s+content="([^"]*)"', html) or [None, ""])[1]
    h1 = len(re.findall(r"<h1[\s>]", html))
    ld = []
    for blob in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        try:
            d = json.loads(blob); t = d.get("@type") or "+".join(x["@type"] for x in d.get("@graph", []))
            ld.append(f"{t}({len(d['mainEntity'])})" if t == "FAQPage" else t)
        except json.JSONDecodeError as e:
            ld.append(f"INVALID({e.msg})")
    ok_title = title.replace("&#39;", "'").replace("&amp;", "&") == src["title_tag"]
    issues = [n for n, bad in (("liquid-error", "Liquid error" in html), ("title", not ok_title), ("desc", not desc), ("h1", h1 != 1), ("ld", any("INVALID" in x for x in ld))) if bad]
    problems += bool(issues)
    print(f"{'!!' if issues else 'ok'} {path:<75} h1={h1} ld={ld} {issues or ''}")
    if "title" in issues: print(f"     got: {title}\n     want: {src['title_tag']}")
print("pages with issues:", problems)
