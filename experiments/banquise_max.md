# Maximum de la banquise arctique 2026-2027 (piste n° 72, 21/11/2026, passage de 1 h, notée sans conviction)

**Marché** : « Arctic sea ice max in winter 2026-2027? » (événement 1412821, 4 tranches, ≈ 8 k$ de liquidité, réglé le
02/04/2027). Règle : plus grande étendue quotidienne du 01/12/2026 au 01/04/2027 dans l'onglet « NH-Daily-Extent » du tableur
`Sea_Ice_Index_Daily_Extent_G02135_v4.0.xlsx` du NSIDC (version 4 telle qu'à la création du marché) ; borne = tranche du dessus.
Carnets du 21/11 (acheteur / vendeur) : < 14,2 : 0,18 / 0,19 ; 14,2-14,5 : 0,27 / 0,28 ; 14,5-14,8 : 0,25 / 0,27 ; ≥ 14,8 : 0,17 / 0,30.

**Source** : le tableur et les CSV quotidiens sont sur `noaadata.apps.nsidc.org`, dont le `robots.txt` interdit tout (`Disallow: /`,
vérifié avec `scripts/robots_ok.py`) : **aucune lecture automatique**. Les analyses du NSIDC (`nsidc.org/sea-ice-today/analyses/…`,
permises) donnent les maxima dans leur texte.

**Fréquence de base** (analyse du 27/03/2025, tableau des 10 plus bas maxima, version 3) : 2025 14,33 ; 2017 14,41 ; 2018 14,47 ;
2016 14,51 ; 2015 14,52 ; 2023 14,62 ; 2011 14,67 ; 2006 14,68 ; 2007 14,77 ; 2021 14,78 ; les autres années récentes sont plus
hautes (2019, 2020, 2022, 2024 ≥ 14,78 de mémoire, à confirmer). 2026 : tranche « 14,2-14,4 » réglée OUI sur Polymarket
(événement 86415). Sur 2015-2026 (12 hivers) : < 14,2 : 0 ; 14,2-14,5 : 4 ; 14,5-14,8 : 4-5 ; ≥ 14,8 : 3-4.

**Lecture** : avec deux hivers de suite au plus bas (2025, 2026), une tendance d'environ −0,04 par an et le changement de capteur
(SSMIS → AMSR2 annoncé en juillet 2025, « même de petits changements peuvent modifier les classements »), ma chance de « < 14,2 »
est ≈ 0,10-0,13 contre 0,18-0,19 au marché. Rapprochée du prix (méthode `prevoir-un-marche`) : NON ≈ 0,85, borne basse ≈ 0,82
pour un vendeur à 0,82 et 4,5 mois d'immobilisation : **pas de conviction**. Le reste de la loi est proche du marché.

**À reprendre** : en février-mars 2027, quand l'étendue du jour (analyses du NSIDC, deux fois par mois) borne déjà le maximum
(même mécanisme que les compteurs : la valeur partielle est connue avant la fin). Le marché d'été (« Min Arctic sea ice extent »,
105 k$ en 2026) est plus liquide.
