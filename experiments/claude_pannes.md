# Jours de panne de claude.ai dans le mois (piste n° 59, 14/11/2026, passage de 21 h)

**Marché** : « Will Claude go down on __ days in <mois> ? » (série mensuelle depuis mars 2026, 23-100 k$ par mois, `tech_fees`).
**Règle lue mot à mot** : un jour compte si sa case sur `status.claude.com/uptime/` (composant claude.ai seulement) a une
couleur autre que le vert une fois finalisée (le lendemain commencé). Les incidents « degraded performance » laissent la case
verte : seules les pannes partielles ou majeures (champs `p` et `m`, secondes) la colorent.

**Source** : la page d'uptime embarque ses données (`data-react-props` : mois, jours, couleur, `p`, `m`, incidents) ; `?page=N`
remonte de 3 mois en 3 mois, de décembre 2023 à aujourd'hui. `robots.txt` lu d'abord avec `scripts/robots_ok.py` :
`/uptime/` et `/history` permis, **`/api/` interdit** (jamais appelé). Relevé : `claude_pannes/releve.py` → `releves/jours.csv`
(1 080 jours, versionné).

**Règlement** : les 8 mois réglés (mars-octobre 2026 : 14, 14, 11, 7, 12, 7, 6, 6 jours non verts) redonnent la tranche
gagnante de Gamma **8 fois sur 8** (la page d'aujourd'hui ; une couleur révisée après coup n'est pas exclue, mais aucune ne
contredit un règlement).

## Fréquence de base (`claude_pannes/base.py`)
Jours non verts du 15 à la fin du mois : moyenne 3,9 (34 mois), 4,9 (12 derniers) ; « au moins 4 de plus » 9 mois sur 12, 6 sur
10 parmi les 18 derniers mois au début calme (≤ 3 au 14). Mais le régime change : jours avec incident 14-27 par mois jusqu'en
août 2026, puis 7 (septembre), 9 (octobre), 4 (1-14 novembre) ; novembre a eu 12 jours verts de suite puis 1 rouge (13/11).

## Rejeu contre le marché (`claude_pannes/rejeu.py`, `rejeu_paris.py`)
Au 14 du mois, 21 h UTC, tranche gagnante, 8 mois : log-score **marché −1,375**, Poisson au taux des 60 jours d'avant **−1,089**,
fréquence empirique des 12 mois d'avant −1,325, moitié marché / Poisson −1,186.
Paris simulés (jours 5, 10, 14, 18, 22, 26 ; prix + 0,02 d'écart ; frais 4 % × p(1−p) ; 12 réglages essayés) :

| seuil d'avantage | prix | paris | rendement | t par mois | gagnés / attendus | mois positifs |
|---|---|---|---|---|---|---|
| 0,06 | 0,05-0,95 | 40 | +27,4 % | +0,29 | 23 / 20,1 | 4/8 |
| 0,08 | 0,05-0,95 | 33 | +39,4 % | +0,52 | 20 / 16,6 | 4/8 |
| 0,08 | 0,45-0,95 | 19 | +17,5 % | +0,33 | 16 / 13,4 | 5/8 |
| 0,08 | 0,10-0,45 | 13 | −0,8 % | −0,63 | 3 / 3,1 | 1/6 |
| 0,12 | 0,10-0,45 | 9 | −78 % | −7,2 | 1 / 2,2 | 0/6 |

**Verdict : écartée en l'état** (paris), malgré un meilleur log-score : rendement porté par 4 mois sur 8, t par mois < 1, et la
tranche « audacieuse » 0,10-0,45 perd. Pas de fantôme. À refaire fin décembre (10 mois) ; ajouter alors « # of ChatGPT Outage
Days » (status.openai.com, 90 jours de `component_impacts` seulement : relever chaque mois).

## Novembre 2026 (étude de conviction, 14/11 21 h UTC)
1 jour non vert (13/11), 14/11 vert à 21 h ; « <5 » vendeur 0,80 / acheteur 0,79, « 5-7 » 0,19 / 0,20, « 8-10 » 0,029.
Cinq estimations de P(≥ 5) : Poisson 60 jours 0,28 ; Poisson 90 jours 0,32 ; empirique des débuts calmes 0,60 ; régime de
novembre seul (0,07 par jour) 0,10 ; avocat du NON (incidents en baisse depuis septembre) 0,18. Médiane 0,28, rapprochée du
prix (0,205) : 0,24, borne basse ≈ 0,21 contre un vendeur du NON de « <5 » à 0,21 : **sous le seuil de 5 points, pas de conviction**.
