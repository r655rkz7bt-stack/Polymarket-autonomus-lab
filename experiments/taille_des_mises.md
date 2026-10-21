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
