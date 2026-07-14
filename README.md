# csfolio-data

CS2 item database for the [CS2Folio](https://csfolio.carrd.co) iOS app.

- `items.json` — sorted array of Steam market hash names
- `images.json` — market hash name → Steam CDN image URL

The app checks these files once a day and refreshes its local copy when they
change, so new CS2 items reach users without an App Store update.

## Updating after a new CS2 drop

```
python3 scripts/generate_items.py
git add -A && git commit -m "Update item database" && git push
```

Data is generated from the community-maintained
[ByMykel/CSGO-API](https://github.com/ByMykel/CSGO-API) dataset.
