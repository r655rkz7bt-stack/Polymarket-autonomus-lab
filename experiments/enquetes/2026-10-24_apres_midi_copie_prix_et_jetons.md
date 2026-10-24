# 2026-10-24 (après-midi) : le principal paie-t-il ce que le fantôme croit payer ? (famille 1)

Famille du jour (24 modulo 6, plus 1) : n° 1, « le principal ne joue pas ce que l'arène mesure ». Le passage du matin avait vérifié les jetons (62 sur 62 dans le fantôme) et cherché un
biais de sélection (copiés −2,5 % contre non copiés +5,1 %, hasard). Ici : le **prix** et la **taille**, jeton par jeton, sur tous les achats du principal (journaux signés du 24/10, 14 h 52 UTC).
Script : `experiments/enquetes/scripts/copie_prix_paye.py`.

## Constat
- 217 achats du principal, 151 jetons réglés comparables. Pour chaque jeton : prix moyen payé par le principal contre prix moyen payé par le fantôme de la même stratégie.
  Écart moyen principal − fantôme : −0,0007 pour la championne (59 jetons), +0,0000 à −0,013 pour les autres : **le principal ne paie pas plus cher**, il paie un peu moins.
- Gain réalisé du principal : −243,9 € ; avec le prix du fantôme (mêmes parts) : −257,1 €. **La copie ne coûte rien de plus que l'arène** (13 € de mieux, pas de pire).
- 48 jetons du principal sont absents du fantôme de leur stratégie : `nf_sport` 35, `meteo_prevision` 11 (tous le 17/10, 09-10 h UTC), `nf_court` 2 (18/10). **Tous datent d'avant le
  18/10 22 h UTC**, c'est-à-dire d'avant la copie fidèle (PR #76, défaut du 18/10 déjà documenté : le principal relançait la stratégie avec son argent). Depuis le 18/10 22 h : 
  achats du principal sans fantôme correspondant = **0** sur 111 achats (≈ 2 000 € misés, jetons de toutes les stratégies).
- Les pertes du principal viennent donc de ce que les fantômes copiés ont perdu (`nf_court` −147 €, `meteo_prevision` −61 €, `nf_sport_patiente` −15 €), pas de la copie.

## Cause, correctif, contrôle
- Pas de défaut nouveau : rien à corriger. Le contrôle `copie_fidele` de `enquete.py` regarde déjà les jetons absents du fantôme, les prix à plus de 2 centimes d'écart et les copies à 100 % d'une exécution partielle (rien de grave au rapport du 24/10) ;
  le script ci-dessus ajoute la conséquence en euros (gain réalisé du principal au prix du fantôme) et l'écart moyen par stratégie, à relancer pour confirmer.
- Obligations « champion_sans_avantage » (`nf_sport_patiente`, `nf_sport_patiente_biais_faible` : 25 gagnés pour 26,4 et 26 pour 27,5 sur les 30 dernières opérations) et « chance » (3 paris = 90 %
  du gain de `nf_sport_patiente_6_24h`, 213 % de `nf_sport_patiente`) : **même cause que les 22 et 24/10** (mises ∝ 1/(1 − prix) à biais fixe 0,05, favoris qui gagnent comme leurs prix ; `2026-10-22_championne_biais_et_mises.md`,
  `2026-10-24_principal_contre_fantome_copie.md`). Les 30 dernières opérations d'un favori à 0,85-0,95 donnent 1 à 2 victoires de moins que prévu à un rythme de ±1 écart-type : rien à corriger dans le code.

## Ce qui reste ouvert
Aucune stratégie validée sur le passé ne tient encore en direct : le principal reste la copie du « meilleur de ~80 par chance ». Pistes prouvées : tweets (NON, écart large), détroits, séismes, SpaceX (indice faible).
