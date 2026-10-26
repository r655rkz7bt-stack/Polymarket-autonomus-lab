# Sous-marchés du football : le nul et la mi-temps (26/10/2026)

**Verdict : écartée.** Aucun côté (Oui / Non), aucun rôle (équipe / nul), aucun délai ne bat ses prix de façon répétée ; le seul indice (« nul Oui » une heure avant) ne se répète pas d'une période à l'autre.

## Question
Dans un 1X2 de football (trois marchés Oui/Non : victoire A, nul, victoire B) et dans le « résultat à la mi-temps », y a-t-il un côté mal payé ? Piste jamais testée : les totaux (`totaux_sports.md`), les handicaps (`ecarts_sports.md`), « les deux marquent » (`btts.md`) et le score exact (`score_exact.md`) l'étaient ; le 1X2 ne l'avait été que comme « favori » (`avant_match_50_50.md`).

## Données
- Gamma, 17 ligues de football (`series_id`), événements dont le coup d'envoi est entre le 01/02 et le 26/10/2026 : 6 427 événements, 19 281 marchés `moneyline` ou `soccer_halftime_result` (`scripts/releve_evenements.py`).
- Vrais échanges (data-api, `market=<conditionId>`) des 13 322 marchés réglés à plus de 1 000 $ de volume (`scripts/releve_echanges.py`, deux processus, ≈ 35 minutes). Après filtre : 4 354 événements avec au moins 2 marchés échangés, **47 285 paris**.
- Règlement : prix finaux Gamma ; les 0,5/0,5 sont comptés 0,5 (aucun marché écarté pour cela). Pas de regard vers le futur : on achète au premier échange preneur dans les 30 minutes après T − d (d = 1, 3, 6, 12, 24 h), prix réel du côté acheté (ou 1 − prix de la vente de l'autre côté), frais `feeSchedule` du marché. Un pari par (marché, délai, côté), prix 0,05-0,95.
- Contrôle du règlement : la lecture des prix finaux donne un résultat net {0 ; 1} ou {0,5 ; 0,5} pour tous les marchés gardés (les autres seraient comptés dans « écartés » : aucun « prix final étrange »). Non relu un par un sur le site (limite).

## Résultats (rendement par pari après frais, t par événement)
- **Équipe, Oui** : −5,0 / −4,4 / −5,4 / −2,9 / −5,2 % à 1 / 3 / 6 / 12 / 24 h (6 107 … 1 767 paris, t −3,4 à −1,3) : le coût d'achat d'un favori ou d'un outsider (frais + écart), pas un biais exploitable de l'autre côté.
- **Équipe, Non** : +0,7 / 0,0 / −2,1 / −0,3 / +1,3 % (t +1,3 à −1,7).
- **Nul, Oui** : +3,4 / +0,3 / −1,9 / +0,3 / −5,1 % (t +0,9 … −0,6). **Nul, Non** : −3,1 / −0,4 / −3,3 / −0,3 / −1,4 %.
- Mi-temps : « nul Oui » 1 h avant +8,0 % (258 paris, t +1,0), tous les autres < 110 paris ou négatifs.
- Bandes de prix (3 h) : seules deux cases passent 2 z, toutes deux négatives (équipe Oui 0,25-0,35 : −12,7 %, 908 paris, t −2,6 ; équipe Non 0,80-0,95 : −3,8 %, 754 paris, t −2,4).
- `idea_test.verdict` du meilleur découpage (nul Oui, 1 h) : « indice » (+3,4 %, 2 509 paris, z des prix +1,5, 5 mois sur 9).
- **Refait sur deux périodes** (leçon du 26/10) : nul Oui à 1 h : **+6,5 % avant le 15/08 (1 503 paris, t +1,4), −1,2 % depuis (1 006 paris, t −0,2)** ; à 3 h : +6,0 % puis −9,7 %. L'indice ne se répète pas.
- Environ 60 découpages regardés (2 types × 2 rôles × 2 côtés × 5 délais, plus 28 bandes de prix).

## Conclusion
Le 1X2 de football est calibré aux prix réellement payables : les écarts sont de l'ordre des frais et du hasard. Rien dans l'arène. Le chiffre est dans `PISTES.md`.
Scripts : `experiments/sous_marches_football/scripts/` (données dans `donnees/`, ignorées par Git).
