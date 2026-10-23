# Compteur de tweets : les filles (piste n° 1, 21/10/2026)

> **23/10/2026 : ces rendements sont ceux de l'historique horaire du CLOB, pas des prix payés.** Aux prix des vrais échanges, A + D vaut −0,1 % par période (t −0,02), neuf réglages entre −5 % et +3 % : voir `tweets_prix_payes.md`.

**Question** : la stratégie `compteur_tweets` (+12 % par achat sur le passé) gagne-t-elle partout, ou
seulement sur un morceau (sans NYC Mayor, Elon seul, 48 dernières heures, NON seul) ?

**Données** (scripts : `experiments/vingt_pistes/scripts/tweets_*.py`, `tweets_filles.py`) : 182 périodes
hebdomadaires de 7 comptes (juillet à 13/10/2026), prix réels heure par heure des tranches (CLOB), messages
XTracker (`/api/users/<compte>/posts`). Modèle de `compteur_tweets` inchangé (dispersion 12, 7 + 14 jours),
achats au prix + demi-écart (0,01 Elon, 0,02 les autres), frais 0,05·p·(1−p). Aucun regard vers le futur :
seuls les messages d'avant l'achat sont lus.

**Contrôle du règlement** : la tranche gagnante calculée avec nos messages égale la tranche réglée par
Polymarket pour 178 périodes sur 182. 4 écartées (Trump du 28/08 : 168 messages comptés contre tranche 180-199 ;
3 périodes Zelensky d'octobre), toutes exclues du test.

**Reproduction de la référence** : 4 389 achats, 177 périodes, +12,2 % par achat, +7,8 % par période (t +1,64) :
identique au 20/10.

## Résultats (dispersion 12, marge 0,03, billet ≥ 0,10)
| morceau | achats | périodes | par achat | par période (t) | sans les 3 meilleures périodes |
|---|---|---|---|---|---|
| toutes (référence) | 4 389 | 177 | +12,2 % | +7,8 % (+1,6) | +3,8 % |
| **A : sans NYC Mayor** | 3 549 | 147 | +16,8 % | +13,8 % (+2,7) | +9,1 % |
| B : Elon seul | 103 | 15 | −3,6 % | −3,5 % (−0,5) | −10,6 % |
| C : 48 dernières heures | 161 | 21 | +8,9 % | +1,1 % (+0,1) | −16,0 % |
| **D : NON seulement** | 3 143 | 177 | +12,3 % | +6,4 % (+1,9) | +4,6 % |
| **A + D : NON sans NYC** | 2 612 | 147 | +16,3 % | **+12,8 % (+3,9)** | +10,7 % |
| A + C (+ D) | 160 (70) | 20 (15) | +8,9 % (+3,1 %) | +1,0 % (−9,4 %) | négatif |

**A + D selon le réglage** (6 essayés : dispersion 8/12/16, marge 0 / 0,03 / 0,05, billet min 0,10 / 0,20) :
par période +8,0 % à +15,9 %, t +2,9 à +4,5 ; tous positifs. Par mois (réglage de base) : juillet +17 %,
août +10 %, septembre +20 %, octobre +15 %. 1re moitié (juil-août) +11,0 % (t +2,1), 2e moitié (sept-oct)
+14,5 % (t +3,6). Par compte : tedcruz +22 % (t +6,9), Zelensky +23 % (t +3,7), cz_binance +8 %, WhiteHouse
+13 % ; **Elon −1 % et Trump −2 % : rien**. Par prix payé : 0,10-0,30 non concluant (33 achats), 0,30-0,60
+39 % (492 achats, t +4,6), 0,60-0,99 +10 % (2 087 achats).

Nombre d'essais honnête : 6 réglages × 9 morceaux, soit ~60 découpages regardés ; seul A + D se tient aux six
réglages, aux deux moitiés et à 4 mois sur 4. Les achats d'une même période sont liés : seul le t « par période »
compte, pas celui « par achat ».

## Verdict
- **A + D (NON seulement, sans NYC Mayor) : retenue**, stratégie `compteur_tweets_non` dans l'arène (filtres
  codés dans `CompteurTweets` : `only_no`, `skip_nyc`, avec test). Réserve : tout vient de tedcruz, Zelensky,
  cz_binance, WhiteHouse ; Elon et Trump (les plus suivis par les gros acheteurs) ne montrent rien.
- B (Elon seul), C (48 dernières heures) : **écartées**.
- Reste à faire : la mère `compteur_tweets` n'a que 3 opérations en direct ; l'arène confirmera avec de
  nouveaux paris (contrôle `selection_multiple`).
