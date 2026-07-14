# csfolio-data

CS2 item database and price feed for the [CS2Folio](https://csfolio.carrd.co) iOS app.

**`main` branch** (item database, refreshed weekly by GitHub Actions):
- `items.json` — sorted array of Steam market hash names
- `images.json` — market hash name → Steam CDN image URL

**`prices` branch** (CSFloat price snapshot, refreshed twice daily, kept as a
single commit so history stays small):
- `prices.json` — market hash name → lowest CSFloat buy-now price in USD

The app checks these files periodically and refreshes its local copies when
they change, so new items and prices reach users without App Store updates.

Both datasets can also be regenerated manually:

```
python3 scripts/generate_items.py
python3 scripts/generate_prices.py
```

Sources: [ByMykel/CSGO-API](https://github.com/ByMykel/CSGO-API) (items) and
[csgotrader.app](https://csgotrader.app) (CSFloat prices).
