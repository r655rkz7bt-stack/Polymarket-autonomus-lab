# Audace : ce que nos pertes apprennent, et où miser plus gros (27/10/2026)

Demande d'Etienne (27/10/2026) : « Je voudrais plus de liberté quand même pour le tout, fais ce que tu sembles juste et le
plus profitable, ne sois pas paralysé par les pertes, mais vois-les comme des essais et des expériences pour améliorer et
aller chercher de plus gros gains. Ne sois pas paralysé par la peur de perdre mais regarde l'objectif plutôt que la mort
prochaine. »

Scripts : `experiments/audace/` (journaux publiés du 15/10 12 h au 26/10 23 h 35 UTC, `bash scripts/fetch_data.sh` d'abord).
Les fantômes font souvent les mêmes paris (filles, variantes) : quand on regroupe des stratégies, les z sont trop forts.

## Le point de départ
- Principal : 746,79 € réalisés (−253 €), 756 € en comptant les positions. Plus haut 1 049 € le 18/10 ; depuis le 23/10 il
  ne bouge presque plus (755 à 787 €) : **16 % de son argent est engagé (124 €), 84 % attend**.
- Arène : 36 stratégies sur 78 qui ont tradé gagnent de l'argent ; la première (`nf_sport_patiente_prix_850_875`) +577 €.

La question : faut-il simplement miser plus ?

## 1. Miser plus partout : non, le rejeu le dit (`rejeu_regles.py`, `kelly_retreci.py`)
À chaque heure, une règle choisit des stratégies d'après leur seul passé ; le principal simulé copie leurs paris suivants.

| règle (38 réglages essayés en tout) | paris | 1re moitié | 2e moitié | total |
|---|---|---|---|---|
| **règle en vigueur** (mise du fantôme, plafond 5 %) | 477 | +90 € | −144 € | **−54 €** |
| la même, 10 € par pari | 477 | +15 € | −217 € | −202 € |
| tout copier (≥ 15 opérations), 10 € par pari | 3 930 | −307 € | −1 075 € | −1 382 € |
| choisir sur la confiance t ≥ 1 à 2 (6 réglages), 10 € | 107-594 | | | −46 à −198 € |
| choisir sur « gagnés contre attendus » z ≥ 1, 30 opérations, 10 € | 453 | −38 € | +215 € | +177 € |
| la même avec z ≥ 1,5 / z ≥ 2 | 157 / 38 | | | −101 € / +87 € |
| la même **sans les deux fantômes « contrer » de la crypto** | 315 | +7 € | −96 € | **−89 €** |
| la même à la mise du fantôme (pas 10 €) | 453 | +6 € | −110 € | −104 € |
| Kelly sur l'avantage mesuré et rétréci (4 réglages par familles de prix) | 322-326 | −244 à −518 € | +368 à +842 € | +105 à +324 €, **replis de 56 à 137 %** |
| règle en vigueur, familles qui perdent contre leurs prix écartées | 214 | −15 € | −274 € | −290 € |

Lecture :
- Copier plus, ou miser plus, sur les stratégies d'aujourd'hui fait **perdre plus** : leurs paris ne battent pas leurs prix.
- Tous les résultats positifs viennent d'**un seul endroit**, les deux fantômes « contrer » de la crypto ; sans eux, tout
  est négatif. Les mises de Kelly qui les exploitent à fond auraient tué le principal dans la première moitié (repli > 50 %).
- Écarter la famille des favoris fait pire (−290 €) : les remplaçantes (`apres_echeance` −189 €, une fille de favori
  restée hors de la famille −82 €) étaient pires. Dans la règle en vigueur, les favoris copiés (plafond 5 %) sont à
  l'équilibre : +6 € sur 4 394 € misés ; les remplacer par du cash donnait −59 € au lieu de −54 €. Réponse à la question
  du passage de la nuit (garder 28,7 % sur un favori sans avantage ?) : rien à gagner à les retirer aujourd'hui.

## 2. Les favoris : 58 stratégies, un seul et même tirage (`heterogeneite.py`)
Avantage de chaque stratégie = (gagnés − Σ prix payés) / paris, frais compris ; 87 stratégies de 15 opérations ou plus
(sans tenue de marché ni `market_structure`).
- Moyenne **−1,46 point par pari** ; Q = 102,6 pour 86 degrés de liberté : presque tout l'écart entre stratégies est du hasard.
- **Favoris (prix moyen ≥ 0,80) : 58 stratégies, −1,61 point, Q 58,7 pour 57 : aucun écart réel entre elles.** Les
  championnes de cette famille sont les gagnantes d'un tirage. La famille `naive_favorite` (67 stratégies, 3 698 paris) :
  −1,71 point par pari, −3 418 € cumulés dans ses fantômes (`plat_contre_kelly.py`).
- Le passage du 27/10 (nuit) arrive au même verdict sur le passé : favori avant le match, 50 232 paris, 25 cases sur 35
  négatives (`favoris_avant_match.md`).
- Conséquence : découper encore les favoris (l'entonnoir en proposait **61 filles** le 27/10) ne trouve que du bruit.

## 3. Où est l'avantage : le prix payé (`tranches_de_prix.py`)
Toute l'arène, par tranche du prix payé :

| prix | paris | gagnés / attendus | z | mise plate | 1re moitié | 2e moitié |
|---|---|---|---|---|---|---|
| < 0,10 | 214 | 3 / 10,8 | −2,46 | −74 % | −64 % | −88 % |
| 0,10-0,20 | 172 | 34 / 25,3 | +1,88 | +36 % | +39 % | +32 % |
| 0,20-0,30 | 101 | 30 / 24,5 | +1,27 | +24 % | +72 % | −62 % |
| 0,30-0,45 | 203 | 75 / 73,8 | +0,18 | +4 % | −8 % | +19 % |
| 0,45-0,60 | 355 | 179 / 190,6 | −1,24 | −5 % | −15 % | +9 % |
| 0,60-0,80 | 390 | 253 / 278,6 | −2,90 | −9 % | −14 % | −1 % |
| 0,80-0,90 | 2 089 | 1 725 / 1 781,0 | −3,47 | −3 % | 0 % | −4 % |
| 0,90-0,95 | 1 789 | 1 646 / 1 657,0 | −1,00 | −1 % | −2 % | 0 % |
| ≥ 0,95 | 318 | 300 / 307,2 | −2,22 | −2 % | +2 % | −6 % |

- **Les billets sous 0,10 sont surcotés partout** (biais favori-outsider : 2 gagnés pour 5,2 attendus hors crypto, 1 pour 5,6 chez
  les deux « contrer ») : ne jamais en acheter sans une source qui tranche.
- Le gain des tranches 0,10-0,45 vient **entièrement des deux fantômes « contrer » de la crypto** : sans eux, 0,10-0,20 fait
  13 gagnés pour 13,3 attendus, 0,30-0,45 52 pour 55,3.
- Chez eux, **0,10-0,45 : 58 gagnés pour 39,3 attendus sur 174 paris** (posé : 33 pour 21,6 sur 92 ; au comptant : 25 pour
  17,7 sur 82 ; 0,10-0,20 chez le posé : 12 pour 5,9). Leur perte en euros (−94 €) venait des billets sous 0,10 et de la
  taille des mises, pas de leurs choix.
- Les grosses mises des fantômes (Kelly sur un avantage supposé) font un peu moins bien : pondérer par la mise fait pire
  que la mise plate chez 50 stratégies sur 91 ; le cinquième des paris les plus gros rend −6,8 %, le plus petit −2,0 %.
- Tranche 0,10-0,45 choisie **après** avoir regardé les données : c'est une hypothèse forte, pas une preuve. L'arène tranche.

## 4. Ce qui change (et pourquoi)
1. **Deux expériences audacieuses** : `contrer_crypto_audace` (au comptant) et `contrer_crypto_patiente_audace` (posée) :
   seulement 0,10-0,45, Kelly entier avec un avantage supposé de 0,08 (la mère : quart de Kelly, 0,05). Au même pari
   (NON à 0,30 sur 1 000 €), la fille mise 52 € avant la prudence du fantôme, la mère 5,8 € (test
   `test_bold_crypto_daughters_play_only_the_cheap_contrarian_band_with_bigger_stakes`). Si l'avantage est réel, la
   croissance se verra en quelques jours ; sinon la perte du fantôme est le prix de la leçon (la santé du fantôme ramène
   d'elle-même la mise au quart si ses prévisions font moins bien que les prix).
2. **L'entonnoir 80/20 cherche ce qui bat ses prix**, plus les euros de la chance (`config/promotion.yaml` → `entonnoir`,
   `pareto.py`) : un morceau doit battre ses prix avec z ≥ 2 ; une stratégie qui bat ses prix (z ≥ 1,5) est disséquée même
   si elle perd en euros ; les prix bas sont découpés (une seule tranche 0-0,80 cachait les billets sous 0,10). Sur les
   journaux du 27/10 : **4 filles proposées au lieu de 61**, dont le morceau 0,10-0,20 de `contrer_crypto_patiente`
   (z +3,19), trouvé tout seul, et trois morceaux de `compteur_tweets` (z +2,4 à +3,1 par pari ; par événement c'est
   moins : tranches d'un même compteur) (`entonnoir_avant_apres.py`).
3. **L'enquête automatique ne réclame plus d'obligation pour « chance » et « championne sans avantage »** (`enquete.py`) :
   ce ne sont pas des défauts et le principal mise déjà à proportion de l'avantage mesuré. Le 27/10, 7 obligations sur 9
   de la feuille de mission venaient d'eux, à chaque passage, avec la même réponse.
4. **Le principal peut miser plus gros sur ce qui prouve son avantage** : renfort jusqu'à ×3 (au lieu de ×2) et une stratégie
   peut porter tout le capital (au lieu de 70 %), seulement après 30 opérations, une confiance par jour ≥ 80 % et plus
   d'avantage mesuré que supposé. **Défaut trouvé en chemin** : depuis le 21/10, ce renfort était coupé par un `min(1.0, …)`
   dans `main._trade` (écrit le 17/10 pour la période d'essai) : le principal n'a jamais misé plus que sa part sur une
   gagnante (fiche `enquetes/2026-10-27_renfort_annule_et_entonnoir.md`, correctif `main._engaged_shares`). Aujourd'hui
   aucune championne n'y a droit (mises mesurées 0,20 à 1,00). En face, une **réserve de liquidités de 3 %** (`principal.reserve_liquidites`) : la faillite
   tombe dès que le solde DISPONIBLE touche 0, même avec des positions qui valent quelque chose. Dans le test
   (`test_principal_keeps_a_cash_reserve_so_no_bet_can_empty_it`), un pari laissait 0,07 € disponibles ; avec la réserve, 30 €.
5. **La méthode et la routine du chercheur** passent à « cap sur l'objectif » (`docs/METHODE.md`, `docs/ROUTINE_CHERCHEUR.md`) :
   une perte de fantôme est une expérience payée qui doit rapporter une leçon chiffrée (`experiments/carnet_experiences.md`) ;
   un frein se prouve par un rejeu comme une stratégie ; une expérience audacieuse par passage.

## 5. Ce qui n'a pas été fait, et pourquoi
- Mise plate ou choix « gagnés contre attendus » pour le principal : positif seulement grâce à une stratégie.
- Kelly sur l'avantage rétréci : replis mortels (56 à 137 %) dans la première moitié.
- Écarter les favoris du principal : pire au rejeu (−290 € contre −54 €).
- Moins de « paris fictifs » dans la mise sur l'avantage mesuré : cela miserait surtout plus sur des favoris chanceux.

## 6. Limites et suite
- Onze jours, une seule période ; paris en double entre fantômes ; tranche 0,10-0,45 choisie dans l'échantillon.
- **Dans une semaine** (vers le 03/11) : relancer `experiments/audace/*.py` ; juger les deux filles « audace » sur leurs
  nouveaux paris (gagnés contre attendus, et par jour) ; si l'avantage tient, la règle d'entrée en vigueur les fera entrer
  au principal toute seule (12 opérations, croissance ≥ 0,02, t ≥ 1).
