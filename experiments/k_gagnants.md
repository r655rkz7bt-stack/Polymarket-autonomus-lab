# Piste « k gagnants » : la somme des prix OUI d'un événement vaut k (23/10/2026, soir)

**Verdict : écartée pour l'instant, preuve insuffisante (pas d'écart exploitable mesuré ; 13 à 24 événements utilisables sur 121).**

## Question
Dans un événement où exactement k marchés finissent OUI (top 8, relégués, qualifiés, équipes en huitièmes, top 10 de l'Eurovision…), la somme des prix OUI doit valoir k.
Si elle s'en écarte (par exemple 1,15 k, les acheteurs surpayant le OUI), renormaliser p' = p·k/Σp donne de meilleures probabilités que le prix, et on peut acheter le NON des cases trop chères
(ou le OUI des cases trop bon marché). `outsiders_surcotes` ne le fait que pour k = 1.

## Données
- `public-search` de Gamma, 25 requêtes, 2 046 événements clos trouvés, 904 de 4 à 80 marchés, 870 réglés proprement (tous les marchés à 0/1) ; k de 0 à 32.
- Retenus : k ≥ 2, volume ≥ 20 000 $, sans les marchés « price hit / say / views / tweets » : **121 événements, 3 713 marchés** (Coupe du monde 2026, NBA, NFL, Premier League, Ligue des champions, Eurovision, primaires américaines, tournois d'e-sport…).
- Prix OUI : `prices-history` du CLOB (pas de 12 h) ; vrais échanges des preneurs : `data-api …/trades?eventId=` (≤ 10 000 derniers échanges par événement).
- Scripts : `experiments/k_gagnants/scripts/` (`releve_evenements.py`, `releve_prix.py`, `releve_echanges.py`, `analyse.py`, `test_passe.py`). Données dans `donnees/` (ignoré par Git).

## Premier relevé trompeur (prix du CLOB seuls)
Sur les prix `prices-history` : Σp/k médian 1,03 à J-1/J-3, **1,08 à J-7, 1,13 à J-14, 1,15 à J-30** (62 % des événements à J-14 au-dessus de 1,05), tranche 0,40-0,60 à J-3 : 83 gagnés pour 132,7 attendus (z −6,1).
C'est le défaut déjà connu (fiche du 22/10, `queues_tranches.md`) : un carnet vide ou très écarté donne un « milieu » à 0,50 sans aucun échange. Les événements à nombreux marchés peu échangés (golf, tennis de table, primaires) gonflent la somme.

## Avec les vrais échanges
Prix de décision = dernier échange des 3 jours précédents (OUI, ou 1 − NON) ; sans échange, le prix du CLOB n'est accepté qu'aux extrêmes (≤ 0,05 ou ≥ 0,95). Événements gardés si ≥ 90 % des marchés ont un prix :
**24 événements à J-3, 19 à J-7, 13 à J-14** (les anciens échanges manquent : la data-api refuse un décalage au-delà de 10 000).

| Point | Σp/k médian | Σp/k > 1,05 | log-score prix | log-score renormalisé |
|---|---|---|---|---|
| J-3 | 1,002 | 8/24 | −0,1744 | −0,1701 |
| J-7 | 1,033 | 7/19 | −0,2094 | −0,1973 |
| J-14 | 1,025 | 6/13 | −0,1891 | −0,1887 |

Les prix échangés sont cohérents (médiane 1,00 à 1,03) ; renormaliser ne gagne que 0,0004 à 0,012 de log-score (marché contre modèle : le modèle ne bat pas nettement le marché).

## Achats simulés (premier échange preneur dans les 6 h après la décision, frais du marché, tenus jusqu'au règlement)
27 réglages (J-3/7/14 × écart 0,03/0,06/0,10 × NON/OUI/les deux). Sur 27, 2 ont plus de 30 paris, aucun plus de 13 événements ; le seul « indice » : J-3, écart 0,03, les deux côtés, 46 paris, +31,5 % par pari,
13 événements, confiance par événement +0,85, 3 mois sur 7 gagnants, z des prix +0,81 : « indice » au sens d'`idea_test.verdict`, mais choisi parmi 27 et sans réplique à J-7 (−1,9 %, t −1,25) ni à J-14 (+5 %, t −0,48).
Les écarts plus grands ont 3 à 12 paris : aucun sens statistique.

## Conclusion
- Pas d'écart de cohérence exploitable mesuré aux prix échangés ; l'« écart » vu au premier relevé est un artefact de prix de carnet vide (même mécanisme que `queues_tranches` et `lissage_tranches`).
- Limite : ces événements s'échangent peu (long tir, 20-60 marchés dont la moitié à moins de 2 cents) et la data-api n'en rend que les 10 000 derniers échanges : le test ne peut pas conclure à l'inverse non plus.
- Rien ajouté à l'arène. À refaire si on trouve une source d'échanges plus ancienne ou si l'on relève les carnets en direct (événements à 8-36 marchés sur 30 jours, k connu : Ligue des champions « top 8 », relégation).
