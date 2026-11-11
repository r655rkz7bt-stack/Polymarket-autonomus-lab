# Première neige par ville (piste n° 27, 11/11/2026, passage de 16 h) : notée, pas de conviction

« First snow of the 2026 season » (événement 956007, 60 k$) : une question OUI/NON par ville et par date (« by November 15 / 30 »),
réglée sur le PREMIER rapport climatologique quotidien du NWS (trace « T » comprise), station précise (KBOS, KBUF, KORD, KNYC…).

- Fréquence de base (`premiere_neige/base.py`, RCC-ACIS `data.rcc-acis.org/StnData`, sans clé, hivers 1991-2025 sans neige au 11/11) :
  P(première neige du 12 au 15/11) 0,06-0,29 (Boston 0,29, New York 0,29, Philadelphie 0,27, Chicago 0,17, Kansas City 0,19) ;
  P(d'ici le 30/11) 0,22 (Nashville) à 0,83 (Chicago). Échantillons petits (8-32 hivers selon la ville) ; Buffalo, Minneapolis,
  Pittsburgh et Salt Lake City n'ont presque jamais attendu le 11/11 (1-5 hivers sur 35). **Saison 2026 : aucune neige lue au 11/11
  dans les 16 villes** (automne d'El Niño très chaud).
- Prévision NWS (`api.weather.gov/points/…/forecast`, 7 jours) relue à 16 h 50 UTC : pluie et neige « likely » jeudi soir à Buffalo,
  « slight chance » de neige vendredi-samedi à Pittsburgh et jeudi à Chicago ; rien ailleurs (minima 24-47 °F).
- Prix : écarts achat-vente énormes (Boston 15/11 : 0,17/0,95 ; Detroit 0,15/0,93 ; Minneapolis 0,01/0,90), liquidité 18-320 $.
  Les carnets serrés sont justes (Kansas City 15/11 : 0,06/0,08 pour ≈ 0,02 ; Buffalo 0,62/0,87 pour ≈ 0,85 ; Chicago 0,26/0,59 pour
  ≈ 0,25 ; Pittsburgh 0,62/0,81 pour ≈ 0,45). Après rapprochement de moitié vers le milieu, aucune borne basse ne dépasse le vendeur de
  5 points. Le milieu d'un carnet 0,17/0,95 ne dit rien : la règle de rapprochement est faite pour un vrai prix.
- À reprendre si un vendeur se trompe franchement : un fantôme « prévision NWS + climatologie » qui n'achète que sous le vendeur réel
  (pas le milieu) ; marchés minces (≤ 300 $), à ne tenter qu'avec des mises minimes.
