---
name: tester-une-piste
description: Protocole du labo pour juger une idée de pari sur le passé avant l'arène (partie B de docs/ROUTINE_CHERCHEUR.md) - marchés réglés Gamma, prix sans regard vers le futur, vrais frais, vérification aux prix réellement payés, idea_test.verdict. À utiliser pour toute piste d'experiments/PISTES.md, toute idée de stratégie dont l'historique existe, et avant d'écrire qu'une idée « gagne ».
---

# Tester une piste sur le passé

Références : docs/ROUTINE_CHERCHEUR.md (partie B) et docs/METHODE.md. En cas de désaccord, ce sont eux
(et CLAUDE.md) qui priment. Exemples complets : `experiments/vingt_pistes/scripts/` (README) et
`experiments/queues_tranches/` (`prix_payes.py` : la vérification aux prix payés).

## Le protocole, dans l'ordre

1. **Une question chiffrable.** « Le NON des tranches à 0,25-0,60 trois jours avant la fin gagne-t-il plus
   souvent que son prix ? », pas « les tranches sont mal évaluées ».
2. **Déjà fait ?** Cherche dans `experiments/PISTES.md` (pistes écartées, avec leur chiffre),
   `experiments/journal_recherche.md` et `config/strategies.yaml` (`grep -n "class:"`). Une piste écartée
   ne se reprend qu'avec une raison neuve, écrite.
3. **De vraies données : plusieurs centaines de cas, plusieurs mois.**
   - marchés réglés : `idea_test.fetch_resolved` (Gamma ; le sport se trouve par `series_id`, pas par `tag_id`) ;
   - prix à un instant : `idea_test.PriceCache.price_at` (CLOB `prices-history`, jamais un point après T) ;
   - vrais échanges : `idea_test.fetch_event_trades` puis `taker_cost` ;
   - téléchargements dans `experiments/<piste>/donnees/` (ignoré par Git).
4. **Contrôle du règlement** : ta lecture des données redonne-t-elle le résultat officiel ? Chiffre-le
   (« 443 sur 444 »). Sinon, rien de ce qui suit ne vaut.
5. **Jamais de regard vers le futur** : chaque décision n'utilise que ce qui était connu avant T (prix,
   données externes, réglages). Réglage sur la première moitié des dates, jugement sur la seconde
   (`idea_test.split_by_day`).
6. **Contre le marché d'abord** : Brier ou log-score du modèle contre le prix (`idea_test.brier`,
   `log_loss`). Si le modèle ne bat pas le prix, il n'y a rien à acheter.
7. **Achats simulés avec les vrais frais** du marché (`Resolved.fee_rate`, `idea_test.fee` :
   taux × p × (1 − p) par part) et un écart achat-vente.
8. **Aux prix réellement payés, obligatoire avant tout verdict positif.** Refais les achats au premier
   échange réel après T (`taker_cost(..., after=True)`, fenêtre 2 h) et écarte les marchés sans échange.
   Un prix « milieu » d'un carnet vide n'est pas un prix : météo +28 % → −6 %, mentions +31 % → −7 %,
   trois pistes à tranches de +9/+31 % à −1/+2 % (`experiments/enquetes/README.md`).
9. **Robustesse** avec `idea_test.verdict(bets)`. Chaque pari est
   `{"gain": résultat par euro misé frais compris, "evenement": regroupement des paris liés, "mois": "AAAA-MM", "cout": prix payé}`.
   Lis la confiance PAR ÉVÉNEMENT, les mois gagnants, les tranches de prix et `z_prix` (gagne-t-il plus
   souvent que ses prix ?). Essaie au moins 3 réglages et **dis combien tu en as essayé** : un seul réglage
   gagnant sur dix ne prouve rien.
10. **Essai en direct** sur les marchés ouverts : quels marchés la règle prendrait aujourd'hui, avec les
    rattachements relus à la main.

## Verdict et traces

| `verdict` | Ce que tu fais |
|---|---|
| retenue | stratégie (skill `nouvelle-strategie`), candidate à `validated_strategies` si elle tient aux prix payés |
| indice | fantôme dans l'arène, en le disant (« indice : l'arène tranchera ») |
| écartée | rien dans l'arène ; le chiffre clé dans `experiments/PISTES.md` |

Dans tous les cas : compte rendu `experiments/<piste>.md` (question, données, contrôle du règlement,
réglages essayés, résultats aux prix historiques ET aux prix payés, verdict), scripts dans
`experiments/<piste>/`, entrée dans `experiments/journal_recherche.md`.

## Pièges déjà rencontrés
- Gain « en euros » dû à quelques gros paris : retire les 3 meilleurs, le meilleur jour, le meilleur sport.
- Statu quo à 0,9 : 12 gagnés sur 12 donnent t +6 alors que les prix seuls y arrivent 1 fois sur 4 (`z_prix`).
- Paris liés comptés comme indépendants (26 tranches d'une même semaine) : moyenne par événement.
- L'`endDate` d'un match est une date fictive (souvent +7 jours) ; l'heure réelle est `gameStartTime`.
- Gamma refuse le User-Agent de `urllib` (403) et un décalage au-delà de 2 000 (422) : `HttpClient` du
  dépôt, et découpage par fenêtres de dates. L'API des échanges s'arrête à 10 000 lignes par événement.
- Statistiques plus poussées (régression logistique de calibration, modèles hiérarchiques) : skills
  `statsmodels` et `pymc`, dans l'environnement de recherche (`requirements-recherche.txt`), jamais
  dans le cycle.
