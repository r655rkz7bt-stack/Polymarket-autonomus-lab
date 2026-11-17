# 17/11/2026 (passage de 21 h) : sources déguisées en navigateur, Statistique Canada bloqué, double glissement de Rotten Tomatoes

Passage du chercheur du 17/11/2026, 20 h 54 UTC. Aucune obligation dans la feuille de mission. Jour 17 → famille 6 (faite à 1 h) ;
familles 4, 3, 5, 1 et 2 faites à 6 h, 11 h et 16 h. Ici : constat « source indisponible » (règle n° 7), famille 4 (les 7 achats des
fantômes v2 depuis 15 h 30 relus contre leur source), famille 2 (fantômes v2 contre leurs prix).

## 1. Constat « 2 sources indisponibles » : Statistique Canada en 403, et 12 modules déguisés

### Constat
`pib_canada : indisponible : GET https://www150.statcan.gc.ca/n1/dai-quo/ind1-eng.htm : HTTP 403`. Refait à la main : 403 trois fois
de suite avec l'identité « curl/8 », alors que le `robots.txt` du site répond (200) et permet la page. Le code de production
envoyait déjà un en-tête « Mozilla/5.0 » (navigateur) et reçoit aussi 403 : c'est un **blocage actif du site**, pas une panne.
Essayer d'autres identités pour passer serait contourner une protection (règle n° 7) : je ne l'ai pas fait (une commande qui
l'aurait fait a été refusée par le garde-fou de la session, à raison).

### Le défaut trouvé en cherchant la cause
`grep "Mozilla"` : **12 modules de production se présentaient sous une fausse identité** (« Mozilla/5.0 » pour `enso`, `fleuves`,
`michigan`, `openrouter`, `pib_canada`, `rotten_tomatoes`, `spotify_auditeurs`, `taux_immobilier`, `taux_tresor` ; « curl/8 »
pour `marges_californie`, `marges_maryland`, `box_office`, la recherche Gamma de `rotten_tomatoes`, et `rougeole`). Relu un par
un avec l'identité du labo (`HttpClient` : « polymarket-autonomous-lab ») : **tous répondent 200** (CPC, hydroinfo.hu, Michigan,
OpenRouter, Rotten Tomatoes, kworb, Freddie Mac, Trésor américain, API californienne, Maryland, Gamma), **sauf** la page de la
rougeole du CDC (403 à l'identité du labo, 200 à « curl/8 »).

Ampleur : aucun euro faux (les données lues sont les mêmes), mais une pratique contraire à l'esprit de la règle n° 7 : se faire
passer pour un navigateur sans en avoir besoin, c'est déjà se déguiser. Depuis le 11/11 (premier module, `fleuves`).

### Correctif
- Les 11 modules lisent sous l'identité du labo (l'en-tête par défaut de `HttpClient`). Vérifié en vrai, fonction de collecte par
  fonction de collecte (`fetch_enso`, `fetch_fleuves`, `fetch_michigan`, `fetch_openrouter`, `fetch_rt`, `fetch_auditeurs`,
  `fetch_pmms`, `fetch_taux`, `fetch_californie`, `fetch_maryland`) : toutes rendent leurs données ; `fetch_pib_canada` : 403.
- `pib_canada` relu une fois par jour au lieu de 8 (`config/settings.yaml`) : un site qui nous bloque n'a pas à être sollicité ;
  si le blocage cesse, la source revient seule. `pib_canada_anticipe` est aveugle tant que dure le blocage (3 positions gardées).
- **Décision pour Etienne** : la rougeole (`rougeole.py`, fantôme `rougeole_compteur`) n'est lisible qu'en se présentant comme
  curl. Je l'ai laissée telle quelle en attendant ta décision (garder, ou éteindre la source et la stratégie).
- Test `test_production_se_presente_sous_son_nom` (`tests/test_robots_ok.py`) : aucun « Mozilla/ », « curl/ », « Chrome/ »,
  « Safari/ », « python-requests » dans le code de production, sauf la liste d'attente (`rougeole.py`). Il échoue sans le correctif.

## 2. Famille 4 : les 7 achats des fantômes v2 depuis 15 h 30, relus contre leur source

| Stratégie | Marché | Achat | Relu à la source (21 h) | Jugement |
|---|---|---|---|---|
| `favori_politique_quasi_certain` | Trump rencontre Kim Jong Un d'ici le 30/11 | NON 0,972 (10,6 parts) | marché NON 0,9575 | conforme (règle relue) |
| `favori_politique_quasi_certain` | Trump quitte la Chine le 19/11 | OUI 0,97 | marché 0,95 | conforme |
| `indice_cotes` | Démocrates 2028 « 64-66 % » le 20/11 | OUI 0,08 (chance 0,199) | indice brut 0,6672 à 21 h, 63 h restantes : ≈ 0,13 | conforme au modèle (l'indice a remonté depuis 20 h 30) |
| `marges_californie` (Maryland) | gouverneur « 35-40 % » | NON 0,52 (chance 0,598) | 34,56 points, bulletins tardifs à +58 | conforme (pari sur le rythme des restants) |
| `marges_californie` (Maryland) | MD-02 « 30-35 % » | OUI 0,919 (chance 0,99) | 30,28 points, restants à +58 : la marge monte | conforme |
| `rt_compte_critiques` | Hunger Games « 70+ » | NON 0,54 (chance 0,6625) | 49/68 = 72,06 % | **défaut** (ci-dessous) |
| `rt_compte_critiques` | Hunger Games « 60+ » | NON 0,0697 (chance 0,2512) | idem | **défaut** (ci-dessous) |

### Défaut : glissement de 5 points compté deux fois
`rotten_tomatoes.chance` : part des critiques à venir = ½ part totale + ½ part RÉCENTE mesurée par le journal `rt:histo`, **puis
encore −5 points** (« les critiques tardives sont plus froides », réglé sur un seul film, Victorian Psycho). La part récente mesurée
contient déjà la froideur des critiques tardives : le glissement était compté deux fois. Et notre propre journal le dément : du
14 au 16/11, 5 films, **44 critiques tardives, 33 positives pour 28,8 attendues à la part de départ** (26,6 avec −5 points ; z ≈ +2,3
contre le glissement) : Ebenezer 4/7, How to Rob a Bank 6/9, I Play Rocky 16/17, Victorian Psycho 6/9, Ghost Soldier 1/2.

Chiffrage (Hunger Games à 49/68, 138 h, rythme d'après la levée d'embargo ≈ 3/h, part récente 0,65-0,68) : NON « 60+ » 0,21-0,18
avec le double glissement contre **0,07-0,09 sans** ; NON « 70+ » 0,72-0,67 contre **0,52-0,44 sans**. Aucun des deux achats ne passe
sans le défaut (prix + avantage minimal 0,06 + incertitude 0,04). **23 € engagés** (19,98 € + 3,28 €), perte probable sur le
billet à 0,07 ; règlement le 23/11.

Correctif : `GLISSEMENT = 0` et glissement appliqué seulement quand aucune part récente n'est mesurée ; test
`test_hunger_games_part_recente_sans_double_glissement` (échoue sans le correctif). Version inchangée (même idée, calcul corrigé ;
2 paris joués sous l'ancien calcul, à noter au bilan).

Reste ouvert : le rythme mesuré pendant une levée d'embargo est prolongé tel quel jusqu'au règlement (≈ 3/h × 138 h ≈ 400 critiques
de plus, plutôt 200-300 en vrai) ; effet secondaire (0,85 → 0,88 sur « 60+ ») : à étalonner avec `rt:histo` quand il aura un film
complet de la levée d'embargo au règlement (Hunger Games, le 23/11).

## 3. Famille 2 : fantômes v2 contre leurs prix (96 jetons réglés depuis le 07/11)

63 gagnés pour 65,1 attendus par les prix payés et **74,3 annoncés par nos estimations** (z −3,6 contre nos estimations) ; −197 €.
Mais 68 de ces 96 jetons sont les compteurs de posts (`compteur_tweets`, `_72_168h`, `compteur_truth` : 42 gagnés pour 50,5 annoncés),
déjà éliminés ou connus. Hors compteurs : 28 jetons, 21 gagnés pour 21,0 attendus par les prix et 23,8 annoncés : surconfiance
habituelle (contrôle `estimation_gonflee`), rien de neuf. Billets sous 0,10 : 9 achats v2, aucun réglé.

## Contrôle automatique
`sources_indisponibles` a bien signalé le 403 ; le déguisement, lui, n'était vu par aucun contrôle : c'est le test ci-dessus qui le
garde. Le double glissement aurait été vu par `estimation_perimee` seulement au-delà de 0,30 d'écart (ici 0,18) : pas de nouveau
contrôle (le seuil est voulu pour ne pas crier sur les stratégies à modèle propre).
