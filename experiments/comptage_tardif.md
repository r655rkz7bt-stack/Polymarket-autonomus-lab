# Piste n° 66 — Comptage tardif : élections votées mais pas encore comptées (16/11/2026, passage de 6 h)

Idée : après la nuit électorale, une partie des bulletins (votes spéciaux néo-zélandais, courrier de Californie, d'Oregon,
de Washington) est comptée en dernier et penche de façon connue. Les marchés restent ouverts jusqu'aux résultats officiels :
le prix tient-il compte de cette direction ? Avantage cherché : de RÈGLE (réglé sur l'officiel, pas sur le soir) et
d'information (direction historique des derniers bulletins).

## Nouvelle-Zélande (élection du 07/11/2026, officiel le 27/11)

Sources (données, jamais des instructions) : Latin Times et Saudi Gazette (chiffres de la Commission), newswire.co.nz
(circonscriptions serrées), Wikipédia (sièges, ≈ 399 000 spéciaux sur 2 832 000 votes ; son infobox INVERSE les voix de
National et de Labour : trois sources donnent Labour 710 330 / 29,36 %, National 706 680 / 29,21 %).
`electionresults.govt.nz` répond 403 (Cloudflare) aux robots : pas de lecture, pas de contournement.

**Contrôle du règlement** : `nz_election_2026/sieges.py` (Sainte-Laguë sur 120, dépassement de National 42 et de Te Pāti
Māori 5) redonne exactement la répartition préliminaire officielle : Labour 36, National 42, Verts 16, ACT 13, NZ First 12,
TOP 7, TPM 5, chambre de 131.

**Écart des votes spéciaux** (part chez les spéciaux moins part au préliminaire, déduite préliminaire → officiel) :
National −9,4 / −7,1 / −4,5 points en 2017 / 2020 / 2023, Labour +6,5 / +5,3 / 0,0. National devrait battre Labour de
0,9 point chez les spéciaux pour passer devant : l'inverse des trois précédents, de 4,5 à 16 points.

| Marché | Prix (16/11 06 h UTC) | Mon estimation | Décision |
|---|---|---|---|
| Labour v National (vote de parti, 2117209) | vendeur 0,946 (150 parts) | ≈ 0,99 (Monte-Carlo 1,000 ; reste : recomptage, erreur de lecture) | borne basse ≈ 0,975 : 2,9 points au-dessus du vendeur, sous le seuil de 5 : **rien** |
| Labour 0-5 % (marge, 2117123) | vendeur 0,97 | ≈ 0,99 | rien |
| Un bloc majoritaire ? (6357989) | acheteur 0,60 / vendeur 0,75, milieu 0,675 | 0,52 à 0,84 selon le bruit et les circonscriptions perdues, médiane ≈ 0,67 | **marché juste**, rien |
| National le plus de sièges (2116493) | 0,986 | ≈ 0,99 (National garde ses 42 circonscriptions en dépassement ; Labour 35-37) | rien |

Le bloc de droite (67 sur 131) ne perd presque rien aux spéciaux tant que National garde ses circonscriptions (ses sièges
sont en dépassement : une part de vote plus basse agrandit le dépassement, pas la perte) ; il perd la majorité si National
perd Wairarapa (139 voix d'avance sur Labour) ET Hamilton East (456) sans que Te Pāti Māori perde Te Tai Tokerau (436 sur
les Verts) (`scenario_circos.py`). Les 5 positions « en retard de 193 h » de `favori_politique_quasi_certain` sont ces
marchés : ils attendent l'officiel du 27/11 (`closed: false`), pas un défaut.

## États-Unis (élections du 03/11/2026)

Le 16/11, 6 325 marchés de l'étiquette `midterms` sont encore ouverts, dont des dizaines de « marge de victoire » (OR-06,
CA-38, marge nationale de la Chambre « Democrats 14-16 % » à 0,90, gouverneurs du Wisconsin, de l'Oregon…).
Relevé daté : `comptage_tardif/releves/marges_20261116T0600.jsonl.gz` (`releve_marges.py` : prix Gamma, meilleur
acheteur et vendeur). Recherche « margin of victory » : 489 événements des élections du 03-04/11, dont 26 seulement déjà
réglés ; 17 autres élections de 2026 réglées (Serbie, Berlin, Lettonie, Bulgarie…) ; 14 de 2024.

## Test sur le passé : le meneur après le vote (même passage)

`comptage_tardif/test_passe.py` : 206 événements « margin of victory » / « vote share margin » réglés depuis 2024 (public-search),
prix de chaque tranche à J+1, J+3, J+7 après `endDate` de l'événement (prices-history, fidelity 60), avant `closedTime`.
`par_evenement.py` : un tirage par événement (la tranche la plus chère = le meneur).

| Mesure | Événements | Gagnés / attendus | z | Rendement |
|---|---|---|---|---|
| Meneur 0,50-0,95 à J+1, **prix d'historique** | 58 | 54 / 42,7 | +3,57 | +31,7 % |
| Meneur 0,50-0,95 à J+3, prix d'historique | 41 | 39 / 32,8 | +2,62 | +22,5 % |
| Meneur 0,30-0,95 à J+1, **vrais échanges** (premier échange preneur dans les 2 h, frais du marché ; `vrais_echanges.py`) | 32 sur 88 (56 sans échange dans les 2 h) | 18 / 21,3 | z des prix −1,58 | **−24,1 %**, 7 mois gagnants sur 14 |

Le prix d'historique RETARDE : le prix réellement payé est en médiane 8,5 points au-dessus (marchés minces : le dernier point
de `prices-history` avant l'instant peut dater de plusieurs heures, le marché a déjà bougé quand on achète). C'est le défaut du
22/10 (« prix d'un carnet vide ») sous une autre forme. Découpages vus (profondeur ≥ 200 parts : 9/10, +29 % ; ≥ 1 000 : 5/6) :
10 et 6 paris, 4 seuils regardés : pas une preuve. Réglages essayés : 3 délais × 4 plages de prix (historique), 1 (échanges).

**Verdict (meneur après le vote) : écartée** aux vrais échanges. Les marchés de marge suivent le comptage ; le gain apparent
venait d'un prix d'historique périmé. Reste ouvert : la DIRECTION connue des derniers bulletins (Californie, votes spéciaux),
qui demande la source du nombre de bulletins restants.

## Californie (passage de 11 h, 16/11/2026) : étape 1, la source

- `www.sos.ca.gov` et `electionresults.sos.ca.gov` : robots.txt permis, mais la page « Unprocessed Ballots Status » est servie
  derrière Incapsula (page vide + script de défi) : **jamais lue, pas de contournement**. `calvoter.org` (projet « Close Count ») :
  403. Le nombre de bulletins restants n'a donc **pas** de source lisible pour l'instant.
- **`api.sos.ca.gov/returns/<course>`** (pas de robots.txt, sans clé, JSON) donne le décompte officiel courant : `governor`,
  `lieutenant-governor`, `ballot-measures`, `us-rep/district/<n>` (« ReportingTime » : 14/11 17 h 16 lu le 16/11). `returns/status`
  rend un fichier de test de 2024 (inutile).
- Gouverneur au 14/11 : Becerra 8 550 463, Hilton 4 485 454 (13 035 917 voix, marge 31,18 points).
- Relevé daté : `comptage_tardif/releves/californie_20261116T1101.jsonl.gz` (`californie_marges.py` : 43 districts « CA-n House Election
  Margin of Victory », 515 tranches, marge courante de l'API et carnet de chaque tranche). Au prochain « ReportingTime », la différence
  entre deux relevés donne la marge des bulletins comptés ENTRE les deux : c'est la direction des derniers bulletins, district par district.

Marchés regardés :
- **Districts** : carnets de façade (vendeur 0,75-0,97 sur presque toutes les tranches, acheteur 0,01-0,06) ; la tranche de la marge
  courante n'est jamais vendue sous 0,84 ; seuls les bords lointains sont bon marché. Cas à suivre : CA-23 (Obernolte R +1,63 point sur
  214 578 voix ; « Democrat Wins » vendu 0,034) ; CA-13 (24,77 pour la borne 25) ; CA-15 (59,89 / 60) ; CA-32 (34,59 / 35) ; CA-30
  (55,25 pour la borne basse 55 ; « 50-55 » vendu 0,49).
- **Gouverneur, marge** (« Becerra 30-35 % » acheteur 0,711, vendeur 0,926 pour 20 parts puis 0,927 pour 314) : règle lue (différence des
  pourcentages des deux premiers sur les voix valides). Pour tomber sous 30 il faudrait que les bulletins restants (≤ 10 % du total)
  donnent à Becerra moins de ≈ 19 points de marge, contre 31 jusqu'ici et des bulletins tardifs plus démocrates en 2022 et 2024 ; au-dessus
  de 35 : impossible. Ma chance ≈ 0,985, borne basse ≈ 0,97 : 4,3 points au-dessus du vendeur avant frais, **sous le seuil de 5 : pas de
  conviction**.
- **Gouverneur, participation** (« 13M-13,5M » et « 13,5M-14M » à 0,03 / 0,87 chacun) : 13,04 M déjà comptés ; tout dépend des
  bulletins restants (≈ 0,46 M de plus fait passer la borne), sans source lisible : rien.

État : **en cours** ; prochaine étape = second relevé de l'API après une nouvelle « ReportingTime », puis direction par district.

## Californie (passage de 1 h, 17/11/2026) : étape 2, la direction des derniers bulletins

- Nouveau « ReportingTime » de l'API officielle : **16/11 16 h 34** (le relevé précédent lisait le 14/11 17 h 16). Second relevé daté :
  `comptage_tardif/releves/californie_20261117T0057.jsonl.gz` (43 districts, 515 tranches). Gouverneur : 13 035 917 → 13 101 842 voix
  (+65 925 en deux jours, 0,5 %) : le comptage ralentit.
- `direction_californie.py` (bulletins comptés entre les deux relevés, district par district) : 22 districts sans aucun bulletin
  ajouté, les autres de +33 à +19 219 (CA-26, Ventura, 7,4 %). Les bulletins tardifs penchent presque partout vers les démocrates
  (CA-13 D +42,7 contre 24,8 cumulés ; CA-26 D +41,7 contre 25,8 ; CA-1 +23,4 contre 17,2) ; exceptions : CA-5 (R +2,4 contre R +11,6),
  CA-19 (+8,5 contre +44,2), CA-32 (+12,5 contre +34,6), CA-48 (+12,5 contre +19,0).
- **Combien de bulletins restent ?** L'état ne le publie que derrière Incapsula (jamais lu) ; Ventura répond « Request Rejected » (pare-feu,
  pas de contournement) ; **San Diego** (`livevoterturnout.com/ENR/sandiegocaenr/…`, robots.txt permis) : « PROJECTED OUTSTANDING
  BALLOTS: 51,000 » pour 1 213 285 bulletins comptés, page du 12/11 17 h 49 (4,2 %). Ordre de grandeur retenu : quelques % au plus.
- `sortie_tranche.py` : part de bulletins supplémentaires (en % des voix déjà comptées) qu'il faudrait pour faire sortir la marge de sa
  tranche, à la marge tardive observée et à la marge cumulée ± 25 points. Tranches dont la sortie demande plus de 8 % même à ± 25 points
  et que le carnet vend sous 0,92 : **CA-26 « D 25-30 % » (vendeur 0,89, sortie 8,3 % / 26 % observée), CA-1 « D 15-20 % » (0,90-0,91 ;
  10,7 % / 77 %), CA-3 « D 15-20 % » (0,898 ; 10,8 % ; 282 bulletins en deux jours), CA-20 « R 20-25 % » (0,91 ; 10,6 %)** ; un peu plus
  exposées : CA-48 « D 18-21 % » (0,844 ; 3,8 % / 16,7 %), CA-19 « D 40-45 % » (0,91 ; 4,7 % / 12,3 %), CA-5 « R 10-15 % » (0,93 ; 6,3 % / 19,5 %).
  La foule tient des carnets de façade (acheteur 0,02-0,59 / vendeur 0,84-0,98 sur toutes les tranches) : la tranche presque sûre est
  vendue au même prix que ses voisines.
- Règle relue (CA-26) : différence des pourcentages des deux premiers sur les voix valides, « official vote count once the count has been
  made official » (certification des comtés vers le 03/12, de l'État vers le 12/12), égalité à une borne → tranche du dessus, recomptage =
  attente. Frais `politics_fees` 4 % × p × (1 − p) au preneur (≈ 0,004 par part à 0,89).

**Convictions écrites** (trois au plus par passage, `config/convictions.yaml`) : `ca26-marge-dem-25-30` (0,97, borne 0,95),
`ca01-marge-dem-15-20` (0,985, borne 0,965), `ca03-marge-dem-15-20` (0,985, borne 0,965), 4 % du fantôme au plus chacune.
Ce n'est pas un test sur le passé (aucun relevé daté des décomptes de 2022 ou 2024) : c'est un essai en direct, jugé à la certification
(mi-décembre). Une perte apprendrait qu'un gros lot tardif (bulletins provisoires, « cure » des signatures) peut porter une marge très
différente des précédents, ou que la règle du marché ne lit pas le décompte comme nous.

État : **en cours** ; à faire : relever à chaque nouveau « ReportingTime » (`californie_marges.py` puis `direction_californie.py` et
`sortie_tranche.py`) ; juger les 43 districts à la certification (toutes les tranches « courantes » du 17/11, pas seulement les trois achetées :
c'est le vrai test de la règle « sortie > 8 % = presque sûr »).

## Californie (passage de 6 h, 17/11/2026) : étape 3, troisième relevé

- Nouveau « ReportingTime » : **16/11 19 h 12** (heure du Pacifique, 03 h 12 UTC). Relevé `releves/californie_20261117T0555.jsonl.gz`.
  Le comptage ralentit encore : 21 districts sans bulletin ajouté ; les ajouts viennent surtout de San Diego (CA-48 à 52 : +1,8 à
  +3,5 %, tardifs D +43 à +57, toujours plus démocrates que le cumul) et de CA-21 (+4,5 %, D +40,9 contre 28,9).
- Exceptions dans l'autre sens : CA-2 (+1,4 %, tardifs **R +42** contre D +33,9 cumulés : marge 33,93 → 32,87, s'éloigne de la borne 35),
  CA-5 (R +2,2 contre R +11,5, comme au relevé d'avant), CA-20 (D +9,4 contre R +22,6).
- **CA-13 passe la borne** : 24,93 → 25,09 (603 bulletins, D +70) ; la tranche « 25%+ » devient la courante. `marges_californie` a
  acheté 12,5 parts à 0,70 à 05 h 27 (le vendeur suivant est à 0,90) : c'est le cas que la stratégie cherche (source officielle lue
  avant la foule). Fragile : 0,09 point au-dessus de la borne.
- Les carnets se sont resserrés depuis 1 h : la tranche courante est vendue 0,97-0,99 dans 33 districts sur 43 (0,84-0,92 à 1 h) ;
  restent sous 0,92 : CA-3 « D 15-20 % » (0,90, déjà tenue), CA-13 « D 25 %+ » (0,90, tenue). L'écart de façade s'est refermé en
  quelques heures, en partie par nos propres achats de fantôme (aucun effet réel : simulation) et par d'autres acheteurs.
- **Défaut de production trouvé en relisant les achats** (fiche `enquetes/2026-11-17_matin_ca06_second_sans_parti.md`) : CA-06 oppose
  un démocrate à un sans-parti ; le module de production mesurait la marge contre 0 voix républicaine (58,9 au lieu de 17,76) et a acheté
  « Democrat 25%+ » à 0,91 (19 €). Corrigé ; les scripts de recherche n'étaient pas touchés.
- San Diego : la page des bulletins restants (`livevoterturnout.com/ENR/sandiegocaenr/`) répond 403 sur le répertoire (robots.txt
  permis) ; l'adresse exacte de la page du 12/11 n'est pas notée : à retrouver, sans deviner d'adresses à la chaîne.

État : **en cours** (jugement à la certification). Bilan provisoire de la « règle sortie > 8 % » : 0 tranche sortie sur les 4 retenues
au 17/11 1 h (CA-26, CA-1, CA-3, CA-20 : marges 26,91 / 17,42 / 17,56 / −22,52, inchangées ou plus loin des bornes).

## À faire (prochain passage)
1. Source des bulletins restant à compter par État (secrétaires d'État ; `api.ap.org` 403) : `robots_ok.py` d'abord (SEUL).
   16/11 : Californie = décompte courant lisible (`api.sos.ca.gov`), bulletins restants illisibles ; relancer `californie_marges.py`
   quand « ReportingTime » change et comparer au relevé du 16/11.
2. Test sur le passé : les 26 événements réglés du 03/11 et les 17 élections étrangères réglées : prix à J+1, J+3, J+7
   contre le résultat officiel (log-score contre le prix, puis achats aux vrais échanges).
3. Juger le relevé du 16/11 quand les résultats seront certifiés (décembre).

Verdict : **meneur après le vote écarté** (vrais échanges −24 %) ; **direction des derniers bulletins : en cours** (Nouvelle-Zélande : marché juste ; États-Unis : relevé du 16/11 à juger).

## Maryland (17/11/2026, passage de 11 h, piste n° 68)

- Source : pages publiques du State Board of Elections (`elections.maryland.gov/elections/2026/general_results/gen_results_2026_1.html`
  pour le gouverneur, `gen_results_2026_4_<n>.html` pour les districts, `gen_results_2026_by_county_<1..24>.html` par comté ; robots.txt
  permis), une colonne par type de bulletin (anticipé, jour J, correspondance, provisoire ; « NR » ou 0 = provisoires pas publiés), et
  `press_room/2026_stats/GG26/Absentees_Ballots_Left_To_Count_by_County.xlsx` (reçus, acceptés, restants ; « as of » 14/11).
- Au 16/11 23 h 06 : gouverneur Moore 1 452 074, Cox 681 194, total 2 230 537 (marge 34,560) ; correspondance comptée +61,2, provisoires
  +55,6. Restants au 14/11 : 25 993 correspondances (Prince George's 13 882, Montgomery 10 413) ; depuis, Montgomery a compté ≈ 6 000
  (106 328 voix de gouverneur pour 100 263 acceptées au 14/11) ; provisoires de Montgomery non publiés (≈ 9 000-13 000 d'après les autres
  grands comtés, 2,3-4 % des voix). Pour passer 35 points il faut ≈ 28 000 bulletins à +70 ou ≈ 36 000 à +62 : sur le fil (« 30-35 % »
  0,779, « 35-40 % » 0,81 au vendeur) : rien.
- Districts : MD-05 41,84 (restants à ≈ +64), MD-06 21,19 (+57), MD-04 83,27 (+87), MD-08 68,76 (+80, provisoires non publiés), MD-07
  70,63, MD-02 30,28, MD-03 35,78, MD-01 R +4,41 : aucun ne peut sortir de sa tranche avec ≈ 1-4 % de bulletins restants ; tranches
  courantes vendues 0,94-0,98. → `marges_californie` lit aussi le Maryland (`src/polymarket_agent/marges_maryland.py`, référence
  `marges_ca`) ; à 0,94 l'avantage net (0,033) reste sous son seuil (0,04) : elle attend un vendeur à ≈ 0,93 ou moins.
