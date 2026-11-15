# Piste n° 61 : l'historique de « beat » de chaque société contre le prix (15/11/2026, passage de 1 h)

Suite de la piste n° 17 (`battre_resultats.md`, 22/10 : marché calibré sur 1 391 marchés, « piste de rechange non testée :
l'historique par société »). Idée : l'historique de chaque société est GRATUIT et sans regard vers le futur dans Polymarket
lui-même (ses trimestres précédents réglés). Une société qui bat toujours est-elle sous-cotée ? Une qui rate souvent, surcotée ?

## Données (`battre_historique/`)
- `releve.py` : étiquette Gamma `earnings` (1013) par `/events/keyset` (jamais `offset`) : 1 602 événements réglés,
  **1 588 marchés « Will <société> (<ticker>) beat quarterly earnings? » réglés net** (septembre 2025 → novembre 2026) ; prix
  milieu du CLOB (dernier point horaire des 12 h avant T0) à T0 = fermeture − 1, 3 et 7 jours. ≈ 25 s.
- Historique d'une société à T0 = ses marchés réglés au moins 1 jour avant T0 (règlement officiel Polymarket : c'est la valeur
  même qui règle, aucun contrôle externe à faire ; seule la société est rapprochée par le ticker du titre).
- `releve_echanges.py` : 223 255 vrais échanges (data-api v2, filtre `condition`) des 1 488 marchés cotés 0,25-0,92. ≈ 36 s.

## 1. L'historique par société (`analyse.py 1|3|7`) : **écartée**
À T-1 j (1 567 marchés ; 802 avec au moins 2 trimestres passés) :

| historique | marchés | OUI réalisés | prix moyen | réalisé − prix |
|---|---|---|---|---|
| aucun trimestre passé | 412 | 310 | 0,717 | +0,036 (z +1,8) |
| toujours battu (n ≥ 2) | 432 | 363 | 0,808 | +0,032 (z +1,9) |
| un seul raté (n ≥ 2) | 226 | 159 | 0,663 | +0,040 (z +1,4) |
| au moins deux ratés | 144 | 76 | 0,441 | +0,087 (z +2,4) |

Toutes les cases ont le même petit écart positif : l'historique ne SÉPARE rien (le marché le paie déjà : 0,808 contre 0,441).
Log-score, coefficient de l'historique appris sur la première moitié du temps, jugé sur la seconde : **0,0 à T-1 j** (prix −0,4580
= prix + historique −0,4580), −0,1 à T-3 j (−0,4641 contre −0,4649), +0,2 à T-7 j (−0,4594 contre −0,4570, gain négligeable).

## 2. Le OUI en général, aux prix milieu (`biais_oui.py`) puis aux vrais échanges (`echanges_oui.py`) : **écartée**
Aux prix milieu (écart 0,01, frais du marché) le OUI 0,30-0,70 rend +7,6 % (T-1, 459 paris, 12 mois sur 15), +5,9 % (T-3),
+7,1 % (T-7) : mieux que le 22/10. **Aux vrais échanges** (premiers preneurs qui achètent le OUI dans les 12 h après T0, à
≤ milieu + 0,03, prix moyen pondéré sur N parts) le gain dépend de la profondeur :

| cellule | 10 parts | 50 parts | 200 parts |
|---|---|---|---|
| T-1, OUI 0,30-0,70 | 240 paris, +10,3 % (13/15 mois) | 178, +4,0 % | 94, −2,8 % |
| T-1, OUI 0,30-0,90 | 642, +3,1 % | 512, +1,5 % (conf. 0,45) | 312, −1,0 % |
| T-3, OUI 0,30-0,90 | 557, +5,7 % | 373, −1,7 % | 167, −3,8 % |
| T-7, OUI 0,30-0,90 | 322, +4,1 % | 196, +8,0 % (conf. 1,54, z des prix 1,53, 8/14 mois) | 78, +12,4 % (z 1,27) |
| T-7, OUI 0,50-0,85 | 202, +4,5 % | 128, +7,6 % (z 1,0) | 50, +10,2 % |

À T-1 et T-3 jours, le gain s'efface dès 50 parts (règle « profondeur à tester avant d'écrire exécutable », 27/10). À T-7 jours
il tient avec la profondeur mais à z ≈ 1,0-1,5 seulement, 8 à 10 mois sur 14, et c'est la meilleure de **≈ 63 cellules
regardées** (3 horizons × 4 tranches × 2 écarts au milieu, 3 × 3 × 3 aux échanges, plus l'historique) : attendu par le hasard
de la sélection. Pas de fantôme (biais de prix, pas d'information ; l'arène est au-dessus de sa cible de ~20).

**Verdict : écartée** (historique : rien au-delà du prix ; OUI général : non exécutable à J-1/J-3, indice trop faible à J-7).
À refaire seulement avec deux trimestres de plus (février 2027) pour la cellule T-7 j ≥ 50 parts, sans autre réglage.
