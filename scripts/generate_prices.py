#!/usr/bin/env python3
"""
Builds prices.json — a multi-market CS2 price snapshot — from csgotrader.app's
per-market dumps (community-maintained, updated daily, all prices in USD).

Output format:
  {
    "AK-47 | Redline (Field-Tested)": {
      "steam": 43.51,      # Steam Market, last-24h sales average
      "csfloat": 28.35,    # lowest buy-now listing
      "buff163": 29.58,    # lowest listing
      "skinport": 30.53,   # lowest listing
      "csmoney": 32.85,    # site price
      "marketcsgo": 32.0   # lowest listing (Market.CSGO / csgotm)
    },
    ...
  }

Markets with no price for an item are omitted; items with no prices at all
are dropped.

Run by .github/workflows/update-prices.yml on a schedule; the result is
force-pushed to the single-commit `prices` branch so repo history stays small.
"""

import gzip
import json
import os
import urllib.request

BASE = "https://prices.csgotrader.app/latest"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def fetch(name):
    print(f"fetching {name}.json ...")
    with urllib.request.urlopen(f"{BASE}/{name}.json") as r:
        raw = r.read()
    # CloudFront serves these objects gzip-encoded regardless of request headers.
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return json.loads(raw)


def num(value):
    """Positive float or None."""
    if isinstance(value, (int, float)) and value > 0:
        return round(float(value), 2)
    return None


# market key in output -> (source file, extractor for one entry)
MARKETS = {
    "steam":      ("steam",    lambda e: num(e.get("last_24h")) or num(e.get("last_7d"))
                                          or num(e.get("last_30d")) or num(e.get("last_90d"))),
    "csfloat":    ("csfloat",  lambda e: num(e.get("price"))),
    "buff163":    ("buff163",  lambda e: num((e.get("starting_at") or {}).get("price"))),
    "skinport":   ("skinport", lambda e: num(e.get("starting_at"))),
    "csmoney":    ("csmoney",  lambda e: num(e.get("price"))),
    "marketcsgo": ("csgotm",   lambda e: num(e)),
}

out = {}
for market, (source, extract) in MARKETS.items():
    data = fetch(source)
    count = 0
    for name, entry in data.items():
        if entry is None:
            continue
        try:
            price = extract(entry)
        except (TypeError, AttributeError):
            price = None
        if price is not None:
            out.setdefault(name, {})[market] = price
            count += 1
    print(f"  {market}: {count} prices")

with open(os.path.join(REPO_ROOT, "prices.json"), "w") as f:
    json.dump(out, f, ensure_ascii=False)

print(f"done: {len(out)} items")
