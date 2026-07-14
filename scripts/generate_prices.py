#!/usr/bin/env python3
"""
Flattens csgotrader.app's CSFloat price dump into prices.json.

Source: https://prices.csgotrader.app/latest/csfloat.json
        (community-maintained, updated daily, USD)

Output: prices.json — {"<market hash name>": <usd price>, ...}
Doppler phase sub-prices are dropped; the base price is kept.

Run by .github/workflows/update-prices.yml on a schedule; the result is
force-pushed to the single-commit `prices` branch so repo history stays small.
"""

import gzip
import json
import os
import urllib.request

SRC = "https://prices.csgotrader.app/latest/csfloat.json"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with urllib.request.urlopen(SRC) as r:
    raw = r.read()

# CloudFront serves this object gzip-encoded regardless of request headers.
if raw[:2] == b"\x1f\x8b":
    raw = gzip.decompress(raw)

data = json.loads(raw)

prices = {}
for name, entry in data.items():
    price = (entry or {}).get("price")
    if isinstance(price, (int, float)) and price > 0:
        prices[name] = round(float(price), 2)

with open(os.path.join(REPO_ROOT, "prices.json"), "w") as f:
    json.dump(prices, f, ensure_ascii=False)

print(f"done: {len(prices)} prices")
