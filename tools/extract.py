#!/usr/bin/env python3
"""Unpack embrae-website.html (preview bundle) into source/pages, source/assets, source/seo."""
import base64, json, re, sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
src = Path(sys.argv[1]) if len(sys.argv) > 1 else root / "embrae-website.html"
out = root / "source"
s = src.read_text(encoding="utf-8")
i = s.index('<script id="pk"'); j = s.index("</script>", i)
pack = json.loads(s[s.index(">", i) + 1:j])

EXT = {"image/jpeg": "jpg", "image/png": "png", "font/woff": "woff", "font/woff2": "woff2", "image/svg+xml": "svg", "image/webp": "webp"}
(out / "assets").mkdir(parents=True, exist_ok=True)
(out / "pages").mkdir(parents=True, exist_ok=True)
(out / "seo").mkdir(parents=True, exist_ok=True)

# Name fonts by weight using @font-face rules; everything else by index + type.
names = {}
for h in pack["p"].values():
    for w, n in re.findall(r"font-weight:(\d+);[^}]*?url\(@@A(\d+)@@\)", h):
        names[int(n)] = f"helvena-{w}"
manifest = []
for n, uri in enumerate(pack["a"]):
    mime, b64 = re.match(r"data:([^;]+);base64,(.*)", uri, re.S).groups()
    base = names.get(n, f"asset-{n:02d}")
    fn = f"{base}.{EXT.get(mime, 'bin')}"
    data = base64.b64decode(b64)
    (out / "assets" / fn).write_bytes(data)
    used = sorted(k for k, h in pack["p"].items() if f"@@A{n}@@" in h)
    manifest.append({"id": n, "file": fn, "mime": mime, "bytes": len(data), "used_in": used})

text = lambda x: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", x)).strip()
for name, h in pack["p"].items():
    page = re.sub(r"@@A(\d+)@@", lambda m: "../assets/" + manifest[int(m.group(1))]["file"], h)
    (out / "pages" / name).write_text(page, encoding="utf-8")
    m = re.search(r'<section id="backend-seo".*?</section>', h, re.S)
    seo = {"page": name, "title_tag": pack["t"].get(name)}
    d = re.search(r'<meta name="description" content="([^"]*)"', h)
    seo["meta_description"] = d.group(1) if d else None
    seo["backend_note"] = text(m.group(0)) if m else None
    note = seo["backend_note"] or ""
    hd = re.search(r"Handle:\s*(/\S+)", note) or re.search(r"(/(?:products|pages|blogs|collections)/[a-z0-9/-]+)", note)
    seo["handle"] = hd.group(1).rstrip(".") if hd else ("/" if name == "index.html" else None)
    (out / "seo" / name.replace(".html", ".json")).write_text(json.dumps(seo, indent=2, ensure_ascii=False), encoding="utf-8")

(out / "assets" / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print(f"{len(pack['p'])} pages, {len(manifest)} assets -> {out}")
