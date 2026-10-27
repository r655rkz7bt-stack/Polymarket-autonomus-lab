# `decroissance_temps` rejouée sur le passé : le OUI de « d'ici <date> » ne fond pas moins que prévu (27/10/2026)

**Verdict : ÉCARTÉE** (les deux côtés). La stratégie `decroissance_temps` (fantôme depuis le 20/10) est **coupée**.

## Pourquoi cette piste
La stratégie est née le 20/10 dans les « vingt pistes » sans test sur le passé (essai à blanc en direct seulement, `vingt_pistes.md`). L'enquête automatique la signalait (`estimation_perimee` : NON estimé 0,928, payé 0,708 le 27/10 à 6 h).
Relecture des 76 achats du fantôme (journal signé) : son prix de « il y a 6 h » se retrouve par la formule `fair = 1 − (1 − p6)^(h/(h+6))` ; dans **24 achats sur 76 (561 € sur 1 140 € misés)** le OUI avait MONTÉ d'au moins 1,5 fois en 6 h (jusqu'à 10 fois : 0,2 % → 2,1 %).
La règle « acheter le NON quand le OUI n'a pas assez fondu » achète donc surtout des **sauts de prix**, que le filtre d'actualité (`max_spike`, pics de mentions) ne voit pas. Les estimations montent à 0,93-0,97 pour des NON payés 0,71-0,85 (écart net jusqu'à 0,21) et Kelly mise en proportion.
Ce n'est pas un carnet périmé : le prix payé est le vrai prix du carnet. C'est l'estimation qui est fausse : question de test.

## Données et méthode (`experiments/decroissance_passe/scripts/`)
- `releve.py` : Gamma `/events/keyset` (curseur, jamais `offset`), événements réglés dont la date de fin va du 01/02/2026 à demain, plus ceux réglés avant leur date de fin ; hors sport, questions contenant « by » ou « before », volume du marché ≥ 3 000 $ :
  **1 876 événements, 6 080 marchés**, tous leurs vrais échanges (data-api, 1 876 fichiers). Mois de fin répartis de février à octobre (460 à 900 marchés par mois).
- `analyse.py` : à chaque horizon T = fin − H (H = 30, 21, 14, 10, 7, 5, 3, 2, 1, 0,5 jour, de 12 h à 720 h comme la stratégie), prix du OUI = dernier échange dans les 3 h avant T (prix du « milieu » du carnet), `p6` = dernier échange dans les 24 h avant T − 6 h ;
  mêmes réglages que le fantôme (OUI 0,03-0,35, écart `prix − fair ≥ 0,01`) ; **un pari par marché** (premier horizon qui déclenche, du plus loin au plus proche, comme une position ouverte qui n'est pas rachetée) ;
  prix payé = premier échange réel de preneur sur le NON dans les 6 h APRÈS T (0,03-0,97), frais du marché (`feeSchedule`) ; rien d'après T pour décider ; marchés non réglés net (≥ 0,99) écartés ; T ≤ clôture − 1 h.
- `analyse2.py` : étalonnage, réglages voisins, côté OUI, moitiés, horizons ; sorties : `resultats.txt`. **Règlement** : prix de règlement de Gamma (`outcomePrices` ≥ 0,99), la seule source de règlement des marchés « d'ici » ; pas de seconde source.

## Résultats (`resultats.txt`)
- **Règle de la stratégie : 742 paris, 460 événements, 610 gagnés pour 624,7 attendus par les prix payés (z −1,5), −2,6 % par pari (t par événement −2,60)**, 6 mois sur 14 gagnants, première moitié des mois +1,1 %, seconde **−5,6 %**. `idea_test.verdict` : **écartée**.
- **Étalonnage** : estimation moyenne du NON 0,874 ; NON réellement gagné 0,822 ; prix moyen payé 0,842. L'estimation dépasse la réalité de 5 points : c'est elle qui fait grossir les mises (Kelly 0,25 sur des écarts jusqu'à 0,2).
- Par écart : `< 0,02` −4,6 % (227) ; `0,02-0,05` −0,9 % (296) ; `0,05-0,10` +0,6 % (151) ; `≥ 0,10` **−10,8 %** (68, 47 gagnés pour 52,4) : plus la stratégie se croit sûre, moins elle l'est.
- Par saut du OUI (prix / p6) : `< 1` −15,4 % (70), `1-1,25` −2,5 % (356), `1,25-2` −0,3 % (231), `≥ 2` −0,6 % (83). Pas de zone où ça gagne.
- **Pas de « prime d'espoir »** : le NON de tous les marchés « d'ici » à OUI 3-35 %, sans règle de gap : **−3,2 %** (1 255 paris, 1 030 gagnés pour 1 061, z −2,5, t par événement −3,7). OUI 0,15-0,35 : −5,2 % ; OUI 0,03-0,15 : −1,0 %.
- Côté **OUI** (« ça arrivera ») : OUI 0,15-0,35 **+5,5 %** (635 paris, z +1,05, t par événement +1,99) mais première moitié des mois **−12,0 %**, seconde +18,5 % ; sans ses 5 meilleurs événements +1,2 % ; par horizon −21 % à +26 % ; OUI 0,03-0,15 −4,3 %. **Bruit** : rien à jouer.
- Réglages regardés : 14 (6 pour le NON, 6 pour le OUI, p6 sur 6 h et tous horizons) + 12 découpages d'écart / de saut / d'horizon.

## Ce que ça change
- `decroissance_temps` : `enabled: false` (config, tests mis à jour). Ses 60 positions ouvertes se règlent ; elles n'étaient pas copiées par le principal.
- **Leçon** : une stratégie à modèle propre ne doit entrer dans l'arène qu'après un rejeu sur le passé, ne serait-ce que sur ses prix : les « vingt pistes » du 20/10 n'en avaient eu que pour une partie. Reste à rejouer (non testées sur le passé) : `marche_neuf`, `outsiders_surcotes`, `echelle_dates` (arbitrage : voir `courbe_de_risque.md`).
- Piste « les marchés d'échéance à OUI 15-35 % » : à refaire seulement avec plus de cas (la moitié récente seule : 362 paris, +18,5 %, mais la première moitié est négative).

## Suite : les catégories de ce relevé (27/10, 16 h-17 h UTC) — IA : indice faible → fantôme `ia_oui_sorties` ; pannes de ChatGPT : marché déjà aligné
Contrôle par catégorie sur les mêmes marchés (6 catégories par mots du titre × 2 côtés, OUI et NON à 3-35 %, un pari par marché) puis relevé par étiquettes IA / tech / OpenAI / Claude depuis le 01/01/2025
(`scripts/releve_tags.py` : 512 événements et 1 514 marchés, en partie déjà dans le relevé général ; 2 084 événements et 6 511 marchés au total avec échanges ; `scripts/analyse3.py` → `resultats_categories.txt`) :
- **Seule catégorie qui sort : l'IA** (marchés qui parlent de GPT, OpenAI, Anthropic, Gemini, Claude, Grok, DeepSeek, Qwen, « AI model »…). OUI à 0,10-0,40 : 105 paris, 41 gagnés pour 26,6, **+51,2 %** (z +3,36, t par événement +2,53) ;
  **hors pannes ChatGPT et classement de l'App Store : 91 paris, 33 gagnés pour 22,2, +45 %** (z +2,72, t +1,98), première moitié +20 % (z +0,8), seconde **+68 %** (z +3,0). Le NON des mêmes marchés : **−14,5 %** (143 paris, z −4,0, t −3,76).
  Autres catégories : géopolitique −0,4 % (NON) / −2,4 % (OUI) ; personnes qui partent −14 % (NON) ; politique américaine −5,8 % (NON) ; « autre » −2,2 % / −1,2 %.
- **Fragile** : 12 comparaisons de catégories + 4 variantes regardées (le z +2,7 survit à peine à une correction) ; **échanges minces** : profondeur médiane 3,8 parts achetables à ≤ prix + 0,02 dans l'heure, ≥ 100 parts 26 paris +58 %,
  ≥ 400 parts 9 paris **+7,6 %** ; hors pannes, sans ses 5 meilleurs événements +24,5 % (t par événement +0,64) ; par horizon : 30 jours −12 %, 14 jours −22 %, 7 jours +51 %, 3 jours +64 %, 1 jour +77 % (5 à 15 paris chacun). Les paris gagnants : sorties de modèles (Claude 5, Mythos, GPT-5.6, Gemini 3.2),
  valorisations d'OpenAI et d'Anthropic. Aucun mécanisme vérifié (hypothèse : les labos livrent plus vite que les prix ne le disent en 2026).
- **Verdict : indice** (`idea_test.verdict`) → expérience audacieuse `ia_oui_sorties` (config seule, filtres sur `naive_favorite` : OUI 0,10-0,40, échéance 1 à 30 jours, mots d'IA, hors pannes et classements, Kelly entier, biais 0,08) ; marchés vus par `tag_pages` 439.
  Cycle local : 1 achat à 0,21 (« GPT Astra 6.1+ released between October 26 and November 1 »). **Pas de capital principal** : la profondeur est celle d'un ticket de 5 à 20 parts. Une perte apprendrait que l'écart vient de quelques mois (2026-06, 2026-09) ou de modèles précis.
- **Pannes de ChatGPT** (« ChatGPT Outage by… », « # of ChatGPT Outage Days in … ») : le OUI a gagné 7 fois sur 8 dans le relevé (payé 0,18-0,44) mais ce sont **8 paris** : rien à conclure. Source qui tranche lue en direct : `status.openai.com/` (page HTML : `component_impacts` des 90 derniers jours avec
  `partial_outage` / `full_outage` par composant, groupe « ChatGPT » = 16 composants ; le JSON `api/v2/incidents.json` n'a pas les composants par niveau) : **5 jours de panne en octobre (1, 7, 9, 15, 20)**, 8 jours depuis fin août. **Le marché le sait déjà** :
  « 5 outages ou plus en octobre » coté 0,9875 ($ 13 555 de volume), « by October 31 » 0,345 contre 0,31 calculé (4 jours restants, 9 % de jours de panne), « by November 15 » 0,83 contre 0,83. Aucune stratégie : le lecteur n'apporterait rien aujourd'hui.

## Suite : `marche_neuf` rejouée (27/10, 17 h UTC) — écartée, stratégie coupée
`marche_neuf` (« un marché de moins de 24 h est trop prudent : renforcer le favori à 0,60-0,88 », extremize 1,15) n'avait, elle aussi, jamais été rejouée sur le passé (80 paris en direct : 64,5 gagnés pour 63,5, +28 € portés par la taille des mises ; non copiée par le principal).
`scripts/marche_neuf.py` sur les marchés du relevé (hors sport, 6 511 marchés avec échanges) : à création + h, prix du favori (≥ 0,5) dans [0,60 ; 0,88], achat au premier échange réel de preneur dans les 6 h, frais payés, un pari par marché
(`resultats_marche_neuf.txt`) :

| h après la création | paris | gagnés / attendus | rendement | t par événement | favori OUI | favori NON |
|---|---|---|---|---|---|---|
| 2 h | 530 | 389 / 406,0 (z −1,8) | −4,5 % | −1,64 | −0,4 % | −6,6 % |
| 6 h | 862 | 635 / 661,1 (z −2,2) | −4,3 % | −2,53 | −3,4 % | −4,8 % |
| 12 h | 993 | 741 / 755,5 (z −1,1) | −2,3 % | −1,65 | −0,1 % | −3,4 % |
| 23 h | 879 | 640 / 666,2 (z −2,1) | −4,3 % | −2,30 | +0,4 % | −7,1 % |

Quatre réglages, tous négatifs : **le favori d'un marché neuf n'est pas sous-coté** (c'est plutôt l'inverse, surtout pour le NON), l'hypothèse de Princeton (pente de recalibrage 1,11) ne se vérifie pas sur ces marchés (le sport, où naissent la plupart des marchés neufs, est couvert par `favoris_avant_match.md` : −1 à −5 %).
Limite : seulement les marchés « d'ici / avant » (mots du titre), pas les marchés neufs de politique ou de culture en général. **Verdict : écartée ; `marche_neuf` coupée** (`enabled: false`, tests mis à jour).
