#!/usr/bin/env python3
"""Pair src/shop screenshots side by side in chunks and score each chunk by pixel difference.
Writes shots/cmp/<page>.<w>.<n>.png and prints a table (worst chunks first per page)."""
import sys
from pathlib import Path
from PIL import Image, ImageChops, ImageStat

CHUNK = {"d": 1400, "m": 1600}
shots = Path(__file__).parent / "shots"
out = shots / "cmp"; out.mkdir(exist_ok=True)
for f in out.glob("*.png"): f.unlink()

for src in sorted(shots.glob("*.src.png")):
    stem = src.name[:-len(".src.png")]
    page, w = stem.rsplit(".", 1)
    a, b = Image.open(src).convert("RGB"), Image.open(shots / f"{stem}.shop.png").convert("RGB")
    width = max(a.width, b.width)
    print(f"{page} [{w}] height src={a.height} shop={b.height}")
    h = max(a.height, b.height)
    for n, top in enumerate(range(0, h, CHUNK[w])):
        box = (0, top, width, top + CHUNK[w])
        ca, cb = a.crop(box), b.crop(box)
        diff = ImageStat.Stat(ImageChops.difference(ca, cb).convert("L")).mean[0]
        pair = Image.new("RGB", (width * 2 + 20, CHUNK[w]), "red")
        pair.paste(ca, (0, 0)); pair.paste(cb, (width + 20, 0))
        name = out / f"{page}.{w}.{n:02d}.png"
        pair.save(name)
        print(f"  {n:02d} y={top:>5} diff={diff:5.1f}  {name.name}")
