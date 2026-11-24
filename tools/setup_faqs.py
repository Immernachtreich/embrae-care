#!/usr/bin/env python3
"""Load the FAQs (source/pages/faqs.html) into embrae_faq metaobjects.

Additive: creates the definition if missing, then upserts faq-001… in source order.
topic = the tab (general or a product handle); category = group heading within General.
Usage: python3 tools/setup_faqs.py [--dry-run]
"""
import json, re
from links import parse, root
from shop import DRY, check, gql

TYPE = "embrae_faq"
txt = lambda e: re.sub(r"\s+", " ", e.get_text(" ", strip=True)) if e else ""


def rich(p):
    """<p> with text and <a> -> Shopify rich_text_field JSON."""
    kids = []
    for c in p.children:
        if getattr(c, "name", None) == "a":
            kids.append({"type": "link", "url": c["href"], "children": [{"type": "text", "value": c.get_text()}]})
        elif getattr(c, "name", None) is None:
            kids.append({"type": "text", "value": str(c)})
        else:
            raise ValueError(f"unexpected tag in FAQ answer: {c.name}")
    return {"type": "paragraph", "children": kids}


if not gql('{ metaobjectDefinitionByType(type:"%s"){ id } }' % TYPE)["metaobjectDefinitionByType"]:
    r = gql("""mutation($d: MetaobjectDefinitionCreateInput!){ metaobjectDefinitionCreate(definition:$d){
      metaobjectDefinition{ id } userErrors{ field message code } } }""", {"d": {
        "type": TYPE, "name": "EMBRAE FAQ", "displayNameKey": "question", "access": {"storefront": "PUBLIC_READ"},
        "fieldDefinitions": [
            {"key": "question", "name": "Question", "type": "single_line_text_field", "required": True},
            {"key": "answer", "name": "Answer", "type": "rich_text_field", "required": True},
            {"key": "topic", "name": "Topic", "type": "single_line_text_field",
             "description": "FAQ page tab: general, or a product handle such as reset-cleanser"},
            {"key": "category", "name": "Category", "type": "single_line_text_field", "description": "Group heading (General tab)"},
            {"key": "product", "name": "Product", "type": "product_reference"},
            {"key": "sort", "name": "Sort order", "type": "number_integer"},
        ]}}, mutation=True)
    if not DRY: check(r["metaobjectDefinitionCreate"]); print("created definition", TYPE)

products = {n["handle"]: n["id"] for n in gql('{ products(first:50, query:"vendor:EMBRAE"){ nodes{ id handle } } }')["products"]["nodes"]}
UPSERT = """mutation($h: MetaobjectHandleInput!, $m: MetaobjectUpsertInput!){ metaobjectUpsert(handle:$h, metaobject:$m){
  metaobject{ handle } userErrors{ field message code } } }"""
n = 0
for panel in parse((root / "source/pages/faqs.html").read_text()).select(".fpanel"):
    topic = panel["id"].removeprefix("fp-")
    for grp in panel.select(".fq-grp"):
        cat = txt(grp.select_one(".fq-cat"))
        for fq in grp.select("details.fq"):
            n += 1
            ps = fq.select(".fa > p")
            fields = {"question": txt(fq.summary), "answer": json.dumps({"type": "root", "children": [rich(p) for p in ps]}),
                      "topic": topic, "category": cat, "product": products.get(topic), "sort": str(n)}
            r = gql(UPSERT, {"h": {"type": TYPE, "handle": f"faq-{n:03d}"},
                             "m": {"fields": [{"key": k, "value": v} for k, v in fields.items() if v]}}, mutation=True)
            if not DRY: check(r["metaobjectUpsert"])
print(n, "FAQs upserted")
