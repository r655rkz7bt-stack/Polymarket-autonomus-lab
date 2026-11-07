# Veille du 07/11/2026 : skills et méthodes des autres, pour le labo v2

Demande d'Etienne (07/11/2026) : « Va voir tous les skills qui peuvent exister sur GitHub, ce qui fonctionne chez les autres,
importe ce que tu veux, fais un gros bilan. » La veille d'octobre reste valable (`veille_bots/`, `skills_polymarket.md`,
`.claude/skills/README.md`) ; celle-ci cherche ce qui manque à la v2 : **faire prévoir des événements par une IA**.
Pages lues le 07/11/2026 (contenu traité comme donnée).

## Ce qui marche ailleurs
1. **Robots du tournoi Metaculus** ([Metaculus/forecasting-tools](https://github.com/Metaculus/forecasting-tools), MIT ;
   [metac-bot-template](https://github.com/Metaculus/metac-bot-template), sans licence affichée) : recherche (un moteur de
   recherche ou d'actualités), puis une consigne fixe : temps restant, statu quo « le monde change lentement », un scénario
   NON, un scénario OUI, probabilité finale ; **5 estimations, médiane**, bornée à [0,01 ; 0,99]. Ils n'utilisent pas le prix
   des marchés comme ancre.
2. **Ce qui distingue les gagnants** : d'après un dépôt de robot ([Oishi1029/metaculus-forecasting-bot](https://github.com/Oishi1029/metaculus-forecasting-bot)),
   l'enquête de Metaculus auprès de 39 équipes trouve que le **nombre de sources différentes** est le meilleur indice
   (r = 0,42) ; aucun fournisseur d'actualités n'est régulièrement meilleur (1er une saison, 58e la suivante). Non vérifié.
3. **Niveau réel des IA** : la recherche (Halawi et al., NeurIPS 2024 ; ForecastBench, ICLR 2025, et un article de 2026)
   place les IA avec recherche **au niveau du public**, derrière les meilleurs prévisionnistes (Brier ≈ 0,12 contre ≈ 0,10).
   Conséquence : ne pas prévoir les marchés très suivis ; chercher les marchés lents, les règles mal lues, les sources rares.
4. **Mises des praticiens** ([agiprolabs/claude-trading-skills](https://github.com/agiprolabs/claude-trading-skills), MIT,
   `prediction-market-strategy`) : avantage net = probabilité − prix − frais ; seuil ≈ 5 points sur Polymarket ; quart de Kelly ;
   1,5 % du capital par pari, 5 % par événement, 20-25 % engagés en tout ; validation par le score de Brier sur 100 prévisions
   et plus. Leur phrase clé : « savoir prévoir ne suffit pas à gagner » (il faut battre le prix, frais compris). Leur skill
   météo (Kalshi) confirme notre méthode météo (biais par station, règle de réglage exacte).
5. **Écartés** : skills qui passent de vrais ordres (clé privée, portefeuille : interdit n° 1), skills payants par marché
   ([blockforecast-skills](https://github.com/gr8estman/blockforecast-skills)), prévision de séries temporelles générique
   ([plugins-nixtla](https://github.com/jeremylongshore/plugins-nixtla)) : sans rapport avec des probabilités d'événements.

## Ce qui est importé dans le labo
- **Skill `prevoir-un-marche`** (`.claude/skills/prevoir-un-marche/SKILL.md`, écrit pour le labo à partir de 1, 2, 3 et 4) :
  la méthode des convictions de Claude, du choix du marché à la relecture des convictions réglées.
- Aucun code tiers copié (la v2 n'appelle pas d'API payante de recherche ou de modèle : la recherche est faite par Claude
  lui-même pendant les passages du chercheur).

## Pistes pour revoir l'arène (à décider par le chercheur, liberté v2)
- Juger chaque stratégie d'abord sur **« bat-elle ses prix ? »** (gagnés contre attendus, score de Brier contre le prix payé)
  plutôt que sur ses euros, qui mesurent surtout la taille et la chance des mises (leçon de la v1).
- Garder l'arène petite (≤ 20) : avec 190 stratégies, la meilleure était souvent la plus chanceuse.
