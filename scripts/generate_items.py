#!/usr/bin/env python3
"""
Regenerates items.json + images.json from ByMykel/CSGO-API data.

Usage (from the repo root):
    python3 scripts/generate_items.py
    git add -A && git commit -m "Update item database" && git push

The CSFolio app checks these files daily and picks up changes automatically —
no App Store update needed.

Output format:
  items.json  — sorted JSON array of market hash names
  images.json — dict of market hash name -> Steam CDN image URL

StatTrak / Souvenir skin variants are constructed from flags, matching
Steam market naming: "StatTrak™ X", "★ StatTrak™ X", "Souvenir X".
"""

import json
import os
import urllib.request

BASE = "https://raw.githubusercontent.com/ByMykel/CSGO-API/main/public/api/en"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SOURCES = ["skins_not_grouped", "music_kits", "crates", "stickers", "agents",
           "patches", "graffiti", "collectibles", "keychains", "keys"]


def fetch(name):
    print(f"fetching {name}.json ...")
    with urllib.request.urlopen(f"{BASE}/{name}.json") as r:
        return json.load(r)


out = {}


def add(name, image):
    if name and image and name not in out:
        out[name] = image


for source in SOURCES:
    for e in fetch(source):
        n = e.get("market_hash_name") or e.get("name")
        img = e.get("image")
        add(n, img)
        # StatTrak / Souvenir variants only exist on skin entries. Some source
        # entries already carry the prefix in market_hash_name while also
        # setting the flag — prefixing those again produced bogus names like
        # "Souvenir Souvenir AWP | ...", so skip when it's already present.
        if source == "skins_not_grouped":
            if e.get("stattrak") and "StatTrak™" not in n:
                if n.startswith("★ "):
                    add("★ StatTrak™ " + n[2:], img)
                else:
                    add("StatTrak™ " + n, img)
            if e.get("souvenir") and not n.startswith("Souvenir "):
                add("Souvenir " + n, img)

items = sorted(out.keys())

with open(os.path.join(REPO_ROOT, "items.json"), "w") as f:
    json.dump(items, f, ensure_ascii=False)
with open(os.path.join(REPO_ROOT, "images.json"), "w") as f:
    json.dump(out, f, ensure_ascii=False)

print(f"done: {len(items)} items")
