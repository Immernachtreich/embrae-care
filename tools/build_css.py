#!/usr/bin/env python3
"""Split the inline page CSS into shared groups.

embraecare/assets/embrae-base.css  <- rules present on every page (minus preview-only review helpers)
source/css/<group>.css             <- rules grouped by which pages use them (reference for later sections)
"""
import collections, re
from pathlib import Path

root = Path(__file__).resolve().parent.parent
pages = sorted((root / "source/pages").glob("*.html"))
theme_assets = root / "embraecare/assets"
manifest = __import__("json").loads((root / "source/assets/manifest.json").read_text())
asset_names = {m["file"]: m["file"] for m in manifest}

def rules(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    out, depth, start = [], 0, 0
    for k, c in enumerate(css):
        if c == "{": depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                out.append(re.sub(r"\s+", " ", css[start:k + 1]).strip()); start = k + 1
    return out

R = {p.name: rules("".join(re.findall(r"<style[^>]*>(.*?)</style>", p.read_text(), flags=re.S))) for p in pages}
users = collections.defaultdict(set)
for name, rs in R.items():
    for r in rs: users[r].add(name)
n = len(pages)
PREVIEW_ONLY = re.compile(r"^(\.review-toggle|body\.review)")

def asset_ref(css):
    return re.sub(r"url\(\.\./assets/([^)]+)\)", lambda m: f"url({asset_names[m.group(1)]})", css)

def dedupe_keep_last(rs):
    seen, out = set(), []
    for r in reversed(rs):
        if r not in seen: seen.add(r); out.append(r)
    return out[::-1]

base = dedupe_keep_last([r for r in R["index.html"] if len(users[r]) == n and not PREVIEW_ONLY.match(r)])
(theme_assets / "embrae-base.css").write_text(asset_ref("\n".join(base)) + "\n")

# Reference groups: order taken from the first page that uses each signature.
groups = collections.OrderedDict()
for name, rs in R.items():
    for r in dedupe_keep_last(rs):
        sig = tuple(sorted(users[r]))
        if len(sig) == n or PREVIEW_ONLY.match(r): continue
        groups.setdefault(sig, [])
        if r not in groups[sig]: groups[sig].append(r)
out = root / "source/css"; out.mkdir(exist_ok=True)
for f in out.glob("*.css"): f.unlink()
for i, (sig, rs) in enumerate(sorted(groups.items(), key=lambda kv: -len(kv[0]))):
    label = sig[0].replace(".html", "") if len(sig) == 1 else f"shared-{len(sig)}p-{i:02d}"
    (out / f"{label}.css").write_text(f"/* used by: {', '.join(sig)} */\n" + asset_ref("\n".join(rs)) + "\n")
print(f"base rules: {len(base)}, bytes: {(theme_assets / 'embrae-base.css').stat().st_size}")
for f in sorted(out.glob("*.css")): print(f.name, f.stat().st_size, f.read_text().splitlines()[0][:150])
