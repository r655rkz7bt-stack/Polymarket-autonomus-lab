Relevés du 26/10/2026 (versionnés : `donnees/` est ignoré par Git). Pour rejouer les analyses :
`mkdir -p experiments/rallies_trump/donnees && for f in marches mentions; do gunzip -c experiments/rallies_trump/releves/$f.json.gz > experiments/rallies_trump/donnees/$f.json; done`
- `marches.json.gz` : 1 371 marchés de 69 meetings de Trump (2024 et 2026), prix horaires du OUI.
- `mentions.json.gz` : 16 214 marchés « What will X say… » (hors meetings), 884 événements, prix horaires du OUI sur 4 jours après l'ouverture.
Prolonger : relancer `scripts/releve.py` et `scripts/releve_mentions.py` (≈ 2 et 12 minutes).
