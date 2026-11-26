#!/usr/bin/env python3
"""Fill empty SEO title/description fields (global.title_tag / global.description_tag) from source/seo/*.json.

Additive: a field is written only when it is currently empty, so nothing set on the store is overwritten.
Covers pages and the journal blog (products and articles already got theirs when they were created).
Usage: python3 tools/setup_seo.py [--dry-run]
"""
import json
from links import root
from shop import DRY, check, gql

seo = {}
for f in (root / "source/seo").glob("*.json"):
    d = json.loads(f.read_text())
    if d.get("handle"):
        seo[d["handle"]] = d

FIELDS = 't: metafield(namespace:"global",key:"title_tag"){value} d: metafield(namespace:"global",key:"description_tag"){value}'
data = gql("{ pages(first:100){ nodes{ id handle %s } } blogs(first:20){ nodes{ id handle %s } } }" % (FIELDS, FIELDS))
owners = [(f"/pages/{n['handle']}", n) for n in data["pages"]["nodes"]] + [(f"/blogs/{n['handle']}", n) for n in data["blogs"]["nodes"]]

SET = """mutation($m: [MetafieldsSetInput!]!){ metafieldsSet(metafields:$m){ metafields{ key } userErrors{ field message code } } }"""
for path, node in owners:
    src = seo.get(path)
    if not src:
        continue
    m = []
    if not node["t"]:
        m.append({"ownerId": node["id"], "namespace": "global", "key": "title_tag", "type": "single_line_text_field", "value": src["title_tag"]})
    if not node["d"]:
        m.append({"ownerId": node["id"], "namespace": "global", "key": "description_tag", "type": "multi_line_text_field", "value": src["meta_description"]})
    if not m:
        print("ok", path); continue
    r = gql(SET, {"m": m}, mutation=True)
    if not DRY: check(r["metafieldsSet"])
    print("set", path, [x["key"] for x in m])
