#!/usr/bin/env python3
"""Create EMBRAE metaobject/metafield definitions and fill them from source/pdp/*.json.

Additive and re-runnable: definitions that already exist are reused, metaobjects are upserted
by handle, and only `embrae.*` product metafields (plus descriptionHtml of the 4 EMBRAE products) are written.
Usage: python3 tools/setup_pdp_data.py [--dry-run]
"""
import hashlib, json, re, sys
from shop import DRY, check, gql
from pathlib import Path

root = Path(__file__).resolve().parent.parent
NS = "embrae"
PAGES = ["reset-cleanser", "urban-defense-serum", "climate-adapt-moisturizer", "daily-shield-sunscreen"]


icons = json.loads((root / "source/pdp/icons.json").read_text())
art = json.loads((root / "source/pdp/ingredient-art.json").read_text())
data = {h: json.loads((root / f"source/pdp/{h}.json").read_text()) for h in PAGES}

# ---------- metaobject definitions ----------
T = lambda key, name, typ="single_line_text_field", **kw: {"key": key, "name": name, "type": typ, **kw}
choices = lambda vals: [{"name": "choices", "value": json.dumps(vals)}]
MO_DEFS = {
    "embrae_ingredient": ("EMBRAE ingredient", "name", [
        T("name", "Name", required=True),
        T("benefit", "Benefit word", description="One word shown on the product page, e.g. Balances"),
        T("descriptor", "Descriptor", description="e.g. Vitamin B3"),
        T("art", "Medallion art", validations=choices(sorted(art))),
        T("description", "Description", "multi_line_text_field", description="Used on the ingredients page"),
    ]),
    "embrae_icon_item": ("EMBRAE icon item", "label", [
        T("label", "Label", required=True),
        T("text", "Text", "multi_line_text_field", description="Line breaks are kept"),
        T("icon", "Icon", required=True, description="Icon key from snippets/pdp-icon.liquid, or an asset file name such as asset-31.png"),
    ]),
    "embrae_how_to_step": ("EMBRAE how-to step", "title", [
        T("title", "Title", required=True),
        T("text", "Text", "multi_line_text_field", description="Basic HTML such as <strong> is allowed"),
        T("icon", "Icon", required=True, validations=choices(sorted(icons))),
    ]),
    "embrae_scene": ("EMBRAE scene", "title", [
        T("title", "Title", required=True),
        T("text", "Text", "multi_line_text_field"),
        T("image", "Image", "file_reference", validations=[{"name": "file_type_options", "value": '["Image"]'}],
          description="Approved photograph. Until set, the illustrated scene is shown."),
    ]),
}
existing = {n["type"]: n["id"] for n in gql("{ metaobjectDefinitions(first:50){ nodes{ id type } } }")["metaobjectDefinitions"]["nodes"]}
MO_CREATE = """mutation($d: MetaobjectDefinitionCreateInput!){ metaobjectDefinitionCreate(definition:$d){
  metaobjectDefinition{ id type } userErrors{ field message code } } }"""
for typ, (name, display, fields) in MO_DEFS.items():
    if typ in existing: print("exists", typ); continue
    r = gql(MO_CREATE, {"d": {"type": typ, "name": name, "displayNameKey": display, "fieldDefinitions": fields,
                              "access": {"storefront": "PUBLIC_READ"}}}, mutation=True)
    if DRY: existing[typ] = f"gid://dry/{typ}"; continue
    p = r["metaobjectDefinitionCreate"]; check(p)
    existing[typ] = p["metaobjectDefinition"]["id"]; print("created", typ)

# ---------- product metafield definitions ----------
ref = lambda typ: [{"name": "metaobject_definition_id", "value": existing[typ]}]
MF = [
    ("step", "Routine step", "single_line_text_field", choices(["reset", "defend", "adapt", "protect", "bundle"]),
     "Sets the product art, page styling and the custom Craft/step tabs"),
    ("eyebrow", "Eyebrow", "single_line_text_field", [], "Short line above the product name"),
    ("tagline", "Tagline", "multi_line_text_field", [], "Line under the product name"),
    ("texture", "Texture / finish", "single_line_text_field", [], None),
    ("when_to_use", "When to use", "single_line_text_field", [], "e.g. AM + PM"),
    ("benefits", "Key benefits", "list.single_line_text_field", [], None),
    ("gallery_ingredients", "Gallery ingredients", "list.metaobject_reference", ref("embrae_ingredient"), "Ingredient panel in the image gallery"),
    ("key_ingredients", "Key ingredients", "list.metaobject_reference", ref("embrae_ingredient"), "Shown in the buy box"),
    ("texture_caption", "Texture caption", "single_line_text_field", [], None),
    ("quick_steps", "How to use (short)", "list.metaobject_reference", ref("embrae_icon_item"), "Three-step summary in the buy box"),
    ("made_for", "Made for", "list.metaobject_reference", ref("embrae_icon_item"), None),
    ("routine_heading", "Routine heading", "single_line_text_field", [], None),
    ("routine_text", "Routine text", "single_line_text_field", [], None),
    ("routine_products", "Routine add-ons", "list.product_reference", [], "Products offered as add-ons in the buy box"),
    ("claims", "Claims", "list.metaobject_reference", ref("embrae_icon_item"), "Icon row in the Essentials tab"),
    ("howto_pills", "How to use tags", "list.single_line_text_field", [], None),
    ("howto", "How to use", "list.metaobject_reference", ref("embrae_how_to_step"), None),
    ("inci", "Full ingredients", "multi_line_text_field", [], None),
    ("storage", "Storage and precautions", "multi_line_text_field", [], "Line breaks are kept; basic HTML such as <b> is allowed"),
    ("scenes", "Made for real days", "list.metaobject_reference", ref("embrae_scene"), None),
    ("reels", "Customer videos", "list.file_reference", [{"name": "file_type_options", "value": '["Video"]'}], None),
    ("info", "Additional information", "list.metaobject_reference", ref("embrae_icon_item"), None),
]
have = {n["key"] for n in gql("""{ metafieldDefinitions(first:100, ownerType:PRODUCT, namespace:"%s"){ nodes{ key } } }""" % NS)["metafieldDefinitions"]["nodes"]}
MF_CREATE = """mutation($d: MetafieldDefinitionInput!){ metafieldDefinitionCreate(definition:$d){
  createdDefinition{ id key } userErrors{ field message code } } }"""
for key, name, typ, val, desc in MF:
    if key in have: print("exists", key); continue
    d = {"namespace": NS, "key": key, "name": name, "ownerType": "PRODUCT", "type": typ, "validations": val,
         "pin": True, "access": {"storefront": "PUBLIC_READ"}}
    if desc: d["description"] = desc
    r = gql(MF_CREATE, {"d": d}, mutation=True)
    if not DRY: check(r["metafieldDefinitionCreate"]); print("created", key)

# ---------- metaobject entries ----------
UPSERT = """mutation($h: MetaobjectHandleInput!, $m: MetaobjectUpsertInput!){ metaobjectUpsert(handle:$h, metaobject:$m){
  metaobject{ id handle } userErrors{ field message code } } }"""
ids = {}


def upsert(typ, handle, fields):
    if (typ, handle) in ids: return ids[(typ, handle)]
    r = gql(UPSERT, {"h": {"type": typ, "handle": handle},
                     "m": {"fields": [{"key": k, "value": v} for k, v in fields.items() if v not in (None, "")]}}, mutation=True)
    if DRY: ids[(typ, handle)] = f"gid://dry/{handle}"; return ids[(typ, handle)]
    p = r["metaobjectUpsert"]; check(p)
    ids[(typ, handle)] = p["metaobject"]["id"]; return ids[(typ, handle)]


slug = lambda s: re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
br = lambda h: re.sub(r"\s*<br\s*/?>\s*", "\n", h).strip()

ing_meta = {}
for d in data.values():
    for k in d["key_ingredients"]:
        ing_meta[k["key"]] = k
NAMES = json.loads((root / "source/pdp/ingredient-names.json").read_text())


def ingredient(k):
    m = ing_meta.get(k, {})
    return upsert("embrae_ingredient", k, {"name": NAMES[k], "benefit": m.get("benefit"), "descriptor": m.get("descriptor"), "art": k})


def icon_item(icon, label, text=""):
    # same label can carry different icons/text across products, so key the handle on all three
    handle = f"{slug(label)[:40]}-{hashlib.md5(f'{icon}|{text}'.encode()).hexdigest()[:8]}"
    return upsert("embrae_icon_item", handle, {"label": label, "icon": icon, "text": br(text)})


SET = """mutation($m: [MetafieldsSetInput!]!){ metafieldsSet(metafields:$m){ metafields{ key } userErrors{ field message code } } }"""
PROD = """mutation($p: ProductUpdateInput!){ productUpdate(product:$p){ product{ handle } userErrors{ field message } } }"""
products = {n["handle"]: n["id"] for n in gql("""{ products(first:20, query:"vendor:EMBRAE"){ nodes{ id handle } } }""")["products"]["nodes"]}
order = ["reset", "defend", "adapt", "protect"]
by_step = {d["step"]: products[h] for h, d in data.items()}

def write(h, pid, mf, description):
    types = {k: t for k, _, t, _, _ in MF}
    metafields = [{"ownerId": pid, "namespace": NS, "key": k, "type": types[k], "value": v} for k, v in mf.items() if v]
    for i in range(0, len(metafields), 25):  # metafieldsSet takes at most 25 per call
        r = gql(SET, {"m": metafields[i:i + 25]}, mutation=True)
        if not DRY: check(r["metafieldsSet"])
    r = gql(PROD, {"p": {"id": pid, "descriptionHtml": f"<p>{description}</p>"}}, mutation=True)
    if not DRY: check(r["productUpdate"])
    print("filled", h, len(metafields), "metafields")


for h, d in data.items():
    pid = products[h]
    L = lambda xs: json.dumps(xs, ensure_ascii=False)
    glance = dict(d["glance"])
    mf = {
        "step": d["step"], "eyebrow": d["eyebrow"], "tagline": d["tagline"],
        "texture": glance.get("Texture / Finish"), "when_to_use": glance.get("When to use"),
        "benefits": L(d["benefits"]),
        "gallery_ingredients": L([ingredient(k) for k in d["gallery_ingredients"]]),
        "key_ingredients": L([ingredient(k["key"]) for k in d["key_ingredients"]]),
        "texture_caption": d["texture_caption"],
        "quick_steps": L([icon_item(x["icon"], x["label"]) for x in d["quick_steps"]]),
        "made_for": L([icon_item(x["icon"], x["label"]) for x in d["made_for"]]),
        "routine_heading": d["routine_heading"], "routine_text": d["routine_text"],
        "routine_products": L([by_step[s] for s in order if s != d["step"]]),
        "claims": L([icon_item(x["icon"], x["label"]) for x in d["claims"]]),
        "howto_pills": L(d["howto_pills"]),
        "howto": L([upsert("embrae_how_to_step", slug(f"{h}-{x['title']}"), {"title": x["title"], "text": x["text"], "icon": x["icon"]})
                    for x in d["howto"]]),
        "inci": d["inci"], "storage": br(d["storage"]),
        "scenes": L([upsert("embrae_scene", slug(f"{h}-{i}"), {"title": x["title"], "text": x["text"]})
                     for i, x in enumerate(d["scenes"], 1)]),
        "info": L([icon_item(x["icon"], x["label"], x["text"]) for x in d["info"]]),
    }
    write(h, pid, mf, d["description"])
# Bundle: only its own copy; products, prices and ingredient lists come from the included products.
b = json.loads((root / "source/pdp/daily-urban-defense-routine.json").read_text())
L = lambda xs: json.dumps(xs, ensure_ascii=False)
write(b["handle"], products[b["handle"]], {
    "step": "bundle", "eyebrow": b["eyebrow"], "tagline": b["tagline"],
    "routine_products": L([by_step[s] for s in order]),
    "claims": L([icon_item(x["icon"], x["label"]) for x in b["claims"]]),
    "storage": br(b["storage"]),
    "info": L([icon_item(x["icon"], x["label"], x["text"]) for x in b["info"]]),
}, b["description"])
print(len(ids), "metaobjects upserted")
