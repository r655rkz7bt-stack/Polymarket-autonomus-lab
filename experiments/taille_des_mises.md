# Taille des mises du capital principal : essai à blanc (21/10/2026, soir)

Demande d'Etienne : « Oui, teste les deux à blanc ». Les deux options : (1) demi-mises ;
(2) mises calculées sur l'avantage MESURÉ au lieu de l'avantage supposé. Rien n'est changé dans les
règles. Scripts : `taille_des_mises/rejouer.py` (semaine réelle) et `taille_des_mises/simuler.py`
(30 jours à venir).

Constat de départ : la championne (nf_sport_patiente) mise comme si elle avait en moyenne
5,7 points d'avantage par pari (estimation − prix payé). Elle en mesure 4,8 sur 94 paris, mais
presque tout vient du 18/10 : sans cette journée, 58 paris gagnés pour 57,7 attendus.

## 1. Rejeu de la semaine (règle « mélange », sans intérêts composés)
| Mises | Semaine réelle | Pire repli | Sans le 18/10 | Pire repli |
|---|---|---|---|---|
| actuelles | +198 € | −73 € | +62 € | −25 € |
| demi | +99 € | −37 € | +31 € | −13 € |
| sur l'avantage mesuré (k 30) | +88 € | −82 € | +54 € | −19 € |
| sur l'avantage mesuré (k 60) | +51 € | −76 € | +38 € | −15 € |

Limite : sans intérêts composés, une demi-mise donne exactement la moitié de tout ; ce rejeu ne
peut pas montrer l'usure due à des mises trop grosses. D'où la simulation suivante.

## 2. Simulation des 30 prochains jours (capital composé, départ 868 €)
Paris tirés parmi les 94 vrais paris de la championne (19 par jour, mise moyenne 7,3 % de son
capital, principal à 70 %), selon l'avantage réel, inconnu. 5 000 trajectoires par case.

| Avantage réel | Mises | Capital médian | 1 chance sur 10 sous | Passe sous 700 € |
|---|---|---|---|---|
| 0 | actuelles | 751 € | 350 € | 69 % |
| 0 | demi | 842 € | 583 € | 42 % |
| 0 | mesuré | 819 € | 715 € | 9 % |
| +1 pt | actuelles | 1 060 € | 513 € | 50 % |
| +1 pt | demi | 995 € | 700 € | 23 % |
| +1 pt | mesuré | 902 € | 745 € | 6 % |
| +2 pts | actuelles | 1 506 € | 743 € | 31 % |
| +2 pts | demi | 1 182 € | 839 € | 10 % |
| +2 pts | mesuré | 1 086 € | 801 € | 3 % |
| +3,5 pts | actuelles | 2 487 € | 1 330 € | 12 % |
| +3,5 pts | demi | 1 517 € | 1 115 € | 2 % |
| +3,5 pts | mesuré | 1 652 € | 1 038 € | 1 % |

Lecture : les mises actuelles ne paient que si l'avantage réel est grand (≥ 2 points) ; avec
0 à 1 point (le plus probable), elles font passer sous 700 € une fois sur deux ou plus. La mise
sur l'avantage mesuré s'adapte : petite tant que l'avantage n'est pas prouvé, elle grossit s'il se
confirme. Elle n'empêche pas une baisse, mais la limite fortement dans tous les cas.

Limites : paris supposés indépendants ; profil d'une seule stratégie ; 30 jours ; l'avantage
réel est supposé constant.

## 23/10/2026 : deux règles pour le principal, testées et non retenues

Question d'Etienne : « à quoi sont dues les pertes ? » (principal à 764 €, −236 € sur 187 opérations clôturées ;
143 gagnées pour 151,8 attendues par les prix payés, z −1,8 ; frais 25 €).

1. **Ne plus copier les favoris à 0,90 ou plus** (le principal y perdait −128 € sur 52 paris) : **non retenue**.
   Sur toute l'arène (un jeton = un pari), les tranches chères sont les MOINS mauvaises : 0,90-0,95 −0,9 % par mise
   (292 gagnés pour 297,3 attendus, 321 paris), ≥ 0,95 −1,5 % (203 paris) ; contre 0,80-0,85 −4,7 % (248 paris) et
   < 0,80 −12,4 % (889 paris, z −5,9). La perte du principal sur les favoris chers vient de son petit échantillon.
2. **Avantage mesuré sur une fenêtre récente** (le plus prudent de « tout l'historique » et « les N derniers paris ») :
   **non retenue**. Rejeu approché des 187 opérations (mise ∝ part copiée) : N = 20 → −196 € ; N = 30 → −247 € ;
   N = 50 → −206 € ; N = 80 → −235 € ; réel −236 €. Pas de sens régulier : 4 réglages essayés, rien de robuste.

Constat commun : aucune tranche de prix ne bat ses prix dans l'arène. Le principal perd parce qu'il copie des
stratégies sans avantage prouvé ; la règle actuelle (`part_min` 0) cesse de les copier dès que l'avantage mesuré
tombe à zéro. La vraie piste est de trouver un avantage (sources « arbitres », `experiments/veille_api_publiques.md`).

## 27/10/2026 : ce qui marchait quand on était en croissance → plafond des mises copiées

Demande d'Etienne : « regarde ce qui marchait par le passé quand on était en croissance ».

**Ce qu'on voit dans les journaux** (15 → 26/10) :
- Le principal n'a jamais vraiment été en gain : son plus haut (1 022 € le 17/10) venait de paris météo pas encore réglés,
  estimés au prix du moment ; réglés le 18/10, ils ont rapporté +27 € pendant que `nf_court` perdait −156 €.
- La seule vraie période de croissance est celle de la championne `nf_sport_patiente` (+174 € dans le rejeu, du 15 au 21/10),
  rendus et au-delà la semaine suivante (−435 €) : de la chance (z des prix ≈ 0, `experiments/enquetes/2026-10-22_championne_biais_et_mises.md`).
- Dans l'arène, beaucoup de fantômes sont au-dessus de 1 000 € (le premier, `nf_sport_patiente_prix_850_875`, à 1 533 €) ; ceux qui
  battent vraiment leurs prix sont rares : `compteur_tweets` (+47,5 % par mise, z des prix +2,2), `contrer_crypto_patiente` (+20,9 %,
  z +1,9 sur 146 paris, mais −28 € : ses grosses mises perdent), `moins_de_cartes` (+17,4 %, les deux moitiés positives).

**Rejeu de la règle d'entrée** (`experiments/regle_confiance/rejouer.py`, refait comme demandé le 21/10 avec 11 jours au lieu d'un) :
règle en vigueur −262 € (le principal réel : −263 €) ; « gagnés contre attendus » sans scepticisme −300 € ; avec scepticisme 0,5
−9 €, mais seulement 7 % du capital engagé (elle ne joue presque pas). **Aucune règle de choix ne gagne** sur la période.

**La taille des mises, elle, change tout** (`experiments/taille_des_mises/plafond_copie.py`) : avec la règle en vigueur, les paris
copiés à 0,90 ou plus, où le fantôme misait le plus (106 € en moyenne, Kelly sur un biais fixe), perdaient −11,5 % par euro ; à
0,80-0,90 (81 € en moyenne) +4,1 %, sous 0,80 (32 €) +17,3 %. Plafond de chaque mise copiée (en part du capital du fantôme) :

| plafond | misé | 1re moitié | 2e moitié | total | par euro |
|---|---|---|---|---|---|
| aucun (avant) | 9 938 € | +174 € | −435 € | −262 € | −2,6 % |
| 10 % | 7 138 € | +151 € | −285 € | −133 € | −1,9 % |
| **5 % (retenu)** | 4 662 € | +104 € | −150 € | **−46 €** | **−1,0 %** |
| 3 % | 3 014 € | +65 € | −87 € | −22 € | −0,7 % |
| 2 % | 2 095 € | +44 € | −61 € | −18 € | −0,9 % |

Le rendement **par euro** s'améliore jusqu'à 3 % : ce n'est pas seulement « miser moins », les grosses mises étaient les
mauvaises. Retenu : 5 % (`principal.mise_fantome_max`), pour garder assez d'argent engagé si une stratégie a un vrai avantage.
5 réglages essayés. Limite : un seul rejeu de 11 jours, approché (sans frais ni carnet) ; à revoir dans une semaine.
