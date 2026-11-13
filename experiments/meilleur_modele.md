# Meilleur modèle d'IA à la fin du mois : le classement officiel lu sur Hugging Face (piste n° 51, 13/11/2026, passage de 6 h)

**Fait nouveau** : arena.ai répond 403 aux robots (27/10), mais LMArena publie son classement officiel avec **tout l'historique des
instantanés** sur Hugging Face : `lmarena-ai/leaderboard-dataset` (licence CC-BY-4.0, mis à jour le 13/11 à 04 h UTC ; 23 arènes :
`text` = sans contrôle de style, `text_style_control`, `webdev`, `vision`, `search`…, chacune en `latest` et `full`). Colonnes :
`model_name`, `organization`, `rating` (et bornes), `vote_count`, `rank`, `category` (« overall », « math », « coding »…),
`leaderboard_publish_date`. Le jeu `text/full` (64 Mo, parquet) a 257 dates de publication depuis mai 2023.

**Marchés** : « Which company has the best AI model end of <mois>? » (Text Arena overall, contrôle de style DÉSACTIVÉ depuis juillet
2025 ; « AutoEval » exclus ; égalité de rang départagée par le score), et les mêmes pour Math, WebDev, etc. ; 35 k$ de liquidité sur
Google fin novembre.

## Test (`meilleur_modele/releve_marches.py`, `analyse.py`, `resume_sans_style.py` ; pandas + pyarrow hors du cycle)

379 marchés réglés relevés. Contrôle du règlement : pour les 13 mois réglés avec la règle « sans style » (juillet 2025 → octobre
2026), le meneur du dernier instantané avant la fin redonne le gagnant **13 fois sur 13** (les mois de février-mai 2025, réglés avec
contrôle de style, ne collent pas au jeu `text` : écartés).

| délai | mois | meneur garde la tête | attendu au prix | prix moyen payé |
|---|---|---|---|---|
| J-14 | 13 | 13 | 11,45 | 0,881 |
| J-10 | 13 | 13 | 11,89 | 0,915 |
| J-7 | 13 | 13 | 11,88 | 0,914 |
| J-3 | 13 | 13 | 12,08 | 0,929 |

À J-14 : +13,5 % par pari, z des prix ≈ +1,4 ; les trois meneurs les moins chers (juillet 2025 0,63, février 2026 0,709, octobre 2026
0,758) ont tous gagné. Un seul réglage essayé (le meneur, sans seuil d'écart). **Indice** (13 tirages, un par mois ; deux
changements de meneur en 15 mois, tous deux vus avant J-14).

## Aujourd'hui (instantané du 11/11)

Text overall : Gemini 4 Carbon 1538,4 (4 273 votes), Gemini 4 Argon 1529,5, Claude Opus 5.5 1513,7 → Google +24,7 points ; marché
Google 0,81 / 0,83 à J-17. **Conviction** `google-meilleur-modele-fin-novembre` (OUI 0,87, borne 0,84 : n'achète que vers 0,80).
Math : Gemini 4 Argon 1543,8 contre Claude Opus 5 1532,2 (11,6 points, intervalles larges), marché Google 0,62 / 0,67.

## Suite

Fantôme « meneur du classement » sur toutes les arènes (text, math, webdev, vision) : le cycle ne doit pas dépendre de pyarrow ;
lire `datasets-server.huggingface.co/rows?dataset=lmarena-ai/leaderboard-dataset&config=text&split=latest` (JSON ; le 13/11 à
06 h 30 : « Job has been terminated due to a temporary spike », à réessayer) ou ajouter pyarrow aux dépendances. Refaire le test sur
les autres arènes (math, webdev) avant.

## Autres arènes (même passage, `releve_math_webdev.py`, `analyse_arenes.py`)

205 marchés réglés « best (Text Arena) Math / Code Arena WebDev AI model end of <mois> » (avril-octobre 2026). Le classement
(`text` catégorie « math », `webdev` « overall ») redonne le gagnant **11 fois sur 11**. Mais le meneur à J-14 : **8 gagnés pour 8,62
attendus** (J-7 : 9 pour 8,21 ; J-3 : 11 pour 9,71) ; des marchés où les meneurs sont serrés (3-7 points, payés 0,49-0,63) et deux
rattachements de nom de société douteux (Moonshot, OpenAI en WebDev) que je n'ai pas relus. Ensemble des trois arènes à J-14 :
21 gagnés pour 20,1 attendus. **L'indice du classement général ne se répète pas ailleurs** : rester à « indice faible », pas de
fantôme avant d'avoir relu ces rattachements ; la conviction Google (achat seulement vers 0,80) reste, mais sa base est mince.
