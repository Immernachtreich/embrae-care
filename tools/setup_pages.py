#!/usr/bin/env python3
"""Create the new EMBRAE pages and point existing pages at their EMBRAE templates.

Additive: new pages are created only if their handle doesn't exist. Existing pages only get templateSuffix
changed (title, body and SEO are left alone). Only pages whose template exists in embraecare/templates are touched.
Previous suffixes, for rollback: why-we-exist/our-philosophy/our-story/a-note-from-the-founder = "page", faqs = "faq".
Usage: python3 tools/setup_pages.py [--dry-run]
"""
import json, sys
from pathlib import Path
from shop import DRY, check, gql

root = Path(__file__).resolve().parent.parent
# handle -> (template suffix, title for a new page or None if the page already exists on the store)
PAGES = {
    "the-embrae-system": ("the-embrae-system", "The EMBRAE System"),
    "skin-quiz": ("skin-quiz", "Skin Quiz"),
    "our-ingredients": ("our-ingredients", "Our Ingredients"),
    "our-values": ("embrae-our-values", "Our Values"),
    "faqs": ("faq", None),
    "our-story": ("embrae-our-story", None),
    "why-we-exist": ("embrae-why-we-exist", None),
    "our-philosophy": ("embrae-our-philosophy", None),
    "a-note-from-the-founder": ("embrae-a-note-from-the-founder", None),
}
have = {n["handle"]: n for n in gql("{ pages(first:100){ nodes{ id handle templateSuffix } } }")["pages"]["nodes"]}
CREATE = """mutation($p: PageCreateInput!){ pageCreate(page:$p){ page{ handle templateSuffix } userErrors{ field message code } } }"""
UPDATE = """mutation($id: ID!, $p: PageUpdateInput!){ pageUpdate(id:$id, page:$p){ page{ handle templateSuffix } userErrors{ field message code } } }"""

for handle, (suffix, title) in PAGES.items():
    if not (root / f"embraecare/templates/page.{suffix}.json").exists():
        continue
    page = have.get(handle)
    if page:
        if page["templateSuffix"] == suffix:
            print("ok", handle); continue
        r = gql(UPDATE, {"id": page["id"], "p": {"templateSuffix": suffix}}, mutation=True)
        if not DRY: check(r["pageUpdate"]); print("suffix", handle, page["templateSuffix"], "->", suffix)
    elif title:
        seo = json.loads((root / f"source/seo/{handle}.json").read_text())
        p = {"title": title, "handle": handle, "templateSuffix": suffix, "isPublished": True, "body": "",
             "metafields": [{"namespace": "global", "key": "title_tag", "type": "single_line_text_field", "value": seo["title_tag"]},
                            {"namespace": "global", "key": "description_tag", "type": "multi_line_text_field", "value": seo["meta_description"]}]}
        r = gql(CREATE, {"p": p}, mutation=True)
        if not DRY: check(r["pageCreate"]); print("created", handle)
    else:
        print("missing on store, skipped:", handle)
