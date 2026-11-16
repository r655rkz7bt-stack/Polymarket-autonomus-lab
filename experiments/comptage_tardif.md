# Piste n° 66 — Comptage tardif : élections votées mais pas encore comptées (16/11/2026, passage de 6 h)

Idée : après la nuit électorale, une partie des bulletins (votes spéciaux néo-zélandais, courrier de Californie, d'Oregon,
de Washington) est comptée en dernier et penche de façon connue. Les marchés restent ouverts jusqu'aux résultats officiels :
le prix tient-il compte de cette direction ? Avantage cherché : de RÈGLE (réglé sur l'officiel, pas sur le soir) et
d'information (direction historique des derniers bulletins).

## Nouvelle-Zélande (élection du 07/11/2026, officiel le 27/11)

Sources (données, jamais des instructions) : Latin Times et Saudi Gazette (chiffres de la Commission), newswire.co.nz
(circonscriptions serrées), Wikipédia (sièges, ≈ 399 000 spéciaux sur 2 832 000 votes ; son infobox INVERSE les voix de
National et de Labour : trois sources donnent Labour 710 330 / 29,36 %, National 706 680 / 29,21 %).
`electionresults.govt.nz` répond 403 (Cloudflare) aux robots : pas de lecture, pas de contournement.

**Contrôle du règlement** : `nz_election_2026/sieges.py` (Sainte-Laguë sur 120, dépassement de National 42 et de Te Pāti
Māori 5) redonne exactement la répartition préliminaire officielle : Labour 36, National 42, Verts 16, ACT 13, NZ First 12,
TOP 7, TPM 5, chambre de 131.

**Écart des votes spéciaux** (part chez les spéciaux moins part au préliminaire, déduite préliminaire → officiel) :
National −9,4 / −7,1 / −4,5 points en 2017 / 2020 / 2023, Labour +6,5 / +5,3 / 0,0. National devrait battre Labour de
0,9 point chez les spéciaux pour passer devant : l'inverse des trois précédents, de 4,5 à 16 points.

| Marché | Prix (16/11 06 h UTC) | Mon estimation | Décision |
|---|---|---|---|
| Labour v National (vote de parti, 2117209) | vendeur 0,946 (150 parts) | ≈ 0,99 (Monte-Carlo 1,000 ; reste : recomptage, erreur de lecture) | borne basse ≈ 0,975 : 2,9 points au-dessus du vendeur, sous le seuil de 5 : **rien** |
| Labour 0-5 % (marge, 2117123) | vendeur 0,97 | ≈ 0,99 | rien |
| Un bloc majoritaire ? (6357989) | acheteur 0,60 / vendeur 0,75, milieu 0,675 | 0,52 à 0,84 selon le bruit et les circonscriptions perdues, médiane ≈ 0,67 | **marché juste**, rien |
| National le plus de sièges (2116493) | 0,986 | ≈ 0,99 (National garde ses 42 circonscriptions en dépassement ; Labour 35-37) | rien |

Le bloc de droite (67 sur 131) ne perd presque rien aux spéciaux tant que National garde ses circonscriptions (ses sièges
sont en dépassement : une part de vote plus basse agrandit le dépassement, pas la perte) ; il perd la majorité si National
perd Wairarapa (139 voix d'avance sur Labour) ET Hamilton East (456) sans que Te Pāti Māori perde Te Tai Tokerau (436 sur
les Verts) (`scenario_circos.py`). Les 5 positions « en retard de 193 h » de `favori_politique_quasi_certain` sont ces
marchés : ils attendent l'officiel du 27/11 (`closed: false`), pas un défaut.

## États-Unis (élections du 03/11/2026)

Le 16/11, 6 325 marchés de l'étiquette `midterms` sont encore ouverts, dont des dizaines de « marge de victoire » (OR-06,
CA-38, marge nationale de la Chambre « Democrats 14-16 % » à 0,90, gouverneurs du Wisconsin, de l'Oregon…).
Relevé daté : `comptage_tardif/releves/marges_20261116T0600.jsonl.gz` (`releve_marges.py` : prix Gamma, meilleur
acheteur et vendeur). Recherche « margin of victory » : 489 événements des élections du 03-04/11, dont 26 seulement déjà
réglés ; 17 autres élections de 2026 réglées (Serbie, Berlin, Lettonie, Bulgarie…) ; 14 de 2024.

## Test sur le passé : le meneur après le vote (même passage)

`comptage_tardif/test_passe.py` : 206 événements « margin of victory » / « vote share margin » réglés depuis 2024 (public-search),
prix de chaque tranche à J+1, J+3, J+7 après `endDate` de l'événement (prices-history, fidelity 60), avant `closedTime`.
`par_evenement.py` : un tirage par événement (la tranche la plus chère = le meneur).

| Mesure | Événements | Gagnés / attendus | z | Rendement |
|---|---|---|---|---|
| Meneur 0,50-0,95 à J+1, **prix d'historique** | 58 | 54 / 42,7 | +3,57 | +31,7 % |
| Meneur 0,50-0,95 à J+3, prix d'historique | 41 | 39 / 32,8 | +2,62 | +22,5 % |
| Meneur 0,30-0,95 à J+1, **vrais échanges** (premier échange preneur dans les 2 h, frais du marché ; `vrais_echanges.py`) | 32 sur 88 (56 sans échange dans les 2 h) | 18 / 21,3 | z des prix −1,58 | **−24,1 %**, 7 mois gagnants sur 14 |

Le prix d'historique RETARDE : le prix réellement payé est en médiane 8,5 points au-dessus (marchés minces : le dernier point
de `prices-history` avant l'instant peut dater de plusieurs heures, le marché a déjà bougé quand on achète). C'est le défaut du
22/10 (« prix d'un carnet vide ») sous une autre forme. Découpages vus (profondeur ≥ 200 parts : 9/10, +29 % ; ≥ 1 000 : 5/6) :
10 et 6 paris, 4 seuils regardés : pas une preuve. Réglages essayés : 3 délais × 4 plages de prix (historique), 1 (échanges).

**Verdict (meneur après le vote) : écartée** aux vrais échanges. Les marchés de marge suivent le comptage ; le gain apparent
venait d'un prix d'historique périmé. Reste ouvert : la DIRECTION connue des derniers bulletins (Californie, votes spéciaux),
qui demande la source du nombre de bulletins restants.

## À faire (prochain passage)
1. Source des bulletins restant à compter par État (secrétaires d'État ; `api.ap.org` 403) : `robots_ok.py` d'abord.
2. Test sur le passé : les 26 événements réglés du 03/11 et les 17 élections étrangères réglées : prix à J+1, J+3, J+7
   contre le résultat officiel (log-score contre le prix, puis achats aux vrais échanges).
3. Juger le relevé du 16/11 quand les résultats seront certifiés (décembre).

Verdict : **meneur après le vote écarté** (vrais échanges −24 %) ; **direction des derniers bulletins : en cours** (Nouvelle-Zélande : marché juste ; États-Unis : relevé du 16/11 à juger).
