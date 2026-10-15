# Proposition — audit indépendant, sauvegarde, réalisme, clés optionnelles (points 1, 3, 4, 6)

Date : 15/10/2026. Demandée par Etienne (« Lance les points 1-6 »). Touche le noyau protégé :
`cycle.yml`, `execution_simulator.py`, `tests/test_execution_simulator.py`, `PROTECTED_PATHS.txt`,
`tests/test_guard.py`, et deux nouveaux fichiers protégés : `scripts/audit_fills.py`,
`tests/test_audit_fills.py`. La règle n°1, le journal (`ledger.py`), le contrôleur, les frais et
les deux mots de passe ne changent pas.

## 1. Audit indépendant des exécutions (le risque n°1)

Le code qui transmet une exécution au journal (`main.py`) est libre : il pourrait inscrire un
prix qui n'a jamais existé. Nouveau job `audit` dans le workflow `cycle`, sur une **machine
neuve** où aucun code libre n'a tourné : `scripts/audit_fills.py` (protégé, bibliothèque standard
+ `ledger.py`, lancé avec `python -I -S`) vérifie les signatures puis compare chaque achat et vente
(principal et fantômes) à l'historique **public** des prix de Polymarket (±30 min) : achat plus de
0,05 sous le plus bas prix observé, ou vente plus de 0,05 au-dessus du plus haut = anomalie.
Résultat dans la branche data (`audit/etat.json`), sur le tableau de bord, et **e-mail** (échec
du job) à chaque nouvelle anomalie. Essai sur les 80 premières exécutions réelles : 80 cohérentes.

## 3. Sauvegarde de la base

Une fois par jour, l'essentiel de la base (ordres posés, ancrage anti-troncature, avis Gemini,
caches ; sans les instantanés volumineux) est compressé dans la branche data (`backup/`, ~ quelques
Ko à quelques Mo). Si le cache GitHub a disparu, le cycle repart de cette sauvegarde. Bibliothèque
standard seulement (`python -I -S`). Testé : sauvegarde, saut si déjà faite, restauration.

## 4. Simulation plus réaliste (plus prudente)

D'autres acheteurs passent avant nous et notre ordre part après la lecture du carnet : on ne
compte plus que **25 %** de la quantité affichée au meilleur prix et **50 %** aux niveaux suivants
(et pour les ordres posés). Les ordres d'un **même portefeuille** pendant un cycle ne réutilisent
plus la même liquidité. Les fantômes restent indépendants (chacun est le scénario « et si cette
stratégie tradait seule ») : les faire partager fausserait l'arène. Conséquence : moins de parts
exécutées par ordre, résultats simulés moins flatteurs, donc plus proches du réel.

## 6. Clés optionnelles des sources gratuites

`cycle.yml` transmet au cycle 11 clés optionnelles (vides tant qu'Etienne ne les ajoute pas dans
l'environnement `production`) : GUARDIAN_API_KEY, FOOTBALL_DATA_KEY, ODDS_API_KEY,
BALLDONTLIE_API_KEY, PANDASCORE_API_KEY, FRED_API_KEY, DATA_GOV_API_KEY, YOUTUBE_API_KEY,
TMDB_API_KEY, COINGECKO_API_KEY, ETHERSCAN_API_KEY. Le chercheur peut ensuite écrire les sources.

## Limites honnêtes

- L'audit détecte un prix **impossible** (hors de tout ce que le marché a fait), pas une petite
  triche de quelques centimes, ni une quantité exagérée. Les marchés sans échange sont « non
  vérifiables ».
- La sauvegarde a jusqu'à 24 h de retard : en cas de restauration, quelques ordres posés peuvent
  revenir (les exécutions déjà au journal ne sont jamais refaites).

## Ce qu'Etienne doit faire

`guard` bloque cette pull request. Comme la dernière fois : désactiver un instant `protection-main`,
fusionner, réactiver.
