#!/usr/bin/env python3
"""Load the Our Ingredients library (source/pages/our-ingredients.html) into embrae_ingredient metaobjects.

Additive: adds the inci/what/why/products fields to the definition if missing, then upserts one entry per row
(handle = slug of the name). Existing entries used by product pages keep their other fields.
Usage: python3 tools/setup_ingredients.py [--dry-run]
"""
import json, re
from links import parse, root
from shop import DRY, check, gql

slug = lambda s: re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
txt = lambda e: re.sub(r"\s+", " ", e.get_text(" ", strip=True)) if e else ""

d = gql('{ metaobjectDefinitionByType(type:"embrae_ingredient"){ id fieldDefinitions{ key } } }')["metaobjectDefinitionByType"]
have = {f["key"] for f in d["fieldDefinitions"]}
new = [
    {"key": "inci", "name": "INCI name", "type": "single_line_text_field"},
    {"key": "what", "name": "What it is", "type": "multi_line_text_field", "description": "Shown in the ingredient library; entries without it are hidden there"},
    {"key": "why", "name": "Why we use it", "type": "multi_line_text_field"},
    {"key": "products", "name": "Found in", "type": "list.product_reference"},
]
ops = [{"create": f} for f in new if f["key"] not in have]
if ops:
    r = gql("""mutation($id: ID!, $d: MetaobjectDefinitionUpdateInput!){ metaobjectDefinitionUpdate(id:$id, definition:$d){
      metaobjectDefinition{ id } userErrors{ field message code } } }""", {"id": d["id"], "d": {"fieldDefinitions": ops}}, mutation=True)
    if not DRY: check(r["metaobjectDefinitionUpdate"]); print("added fields", [o["create"]["key"] for o in ops])

products = {n["handle"]: n["id"] for n in gql('{ products(first:50, query:"vendor:EMBRAE"){ nodes{ id handle } } }')["products"]["nodes"]}
UPSERT = """mutation($h: MetaobjectHandleInput!, $m: MetaobjectUpsertInput!){ metaobjectUpsert(handle:$h, metaobject:$m){
  metaobject{ handle } userErrors{ field message code } } }"""
rows = parse((root / "source/pages/our-ingredients.html").read_text()).select(".ix-row")
for row in rows:
    name = txt(row.h3)
    inci = row.select_one(".ix-n p")
    if inci and inci.span: inci.span.extract()
    cells = {c["data-l"]: c for c in row.select(".ix-c[data-l]")}
    found = [products[a["href"].removesuffix(".html")] for a in cells["Found in"].select("a")]
    fields = {"name": name, "inci": txt(inci), "what": txt(cells["What it is"]), "why": txt(cells["Why we use it"]),
              "products": json.dumps(found)}
    r = gql(UPSERT, {"h": {"type": "embrae_ingredient", "handle": slug(name)},
                     "m": {"fields": [{"key": k, "value": v} for k, v in fields.items() if v]}}, mutation=True)
    if not DRY: check(r["metaobjectUpsert"])
print(len(rows), "ingredients upserted")
