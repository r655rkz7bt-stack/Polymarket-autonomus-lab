# App Store en direct : lire le classement qui tranche (27/10/2026, chantier n°8)

**Verdict : expérience audacieuse en fantôme `classement_appstore`** (pas un test sur le passé : Apple n'archive pas le classement ; une idée neuve et plausible entre dans l'arène pendant que son étalonnage commence, `docs/METHODE.md`, « Cap sur l'objectif »).

## L'idée
Les marchés « #1 Free App in the US Apple App Store on <date> ? » et « #1 Paid App… » (**un événement par semaine, le vendredi** : 64 gratuits et 61 payants réglés depuis octobre 2025, créés ~7 jours avant ; ~1 400 $ de liquidité et ~5 000 $ de volume par événement, 0 frais : `feesEnabled` faux)
se règlent sur le classement « Top Charts » de l'App Store américain **à 12 h, heure de l'Est, du jour visé** (description du marché). Apple publie ce classement (`rss.applemarketingtools.com/api/v2/us/apps/top-free/10/apps.json`, sans clé,
identique à `itunes.apple.com/us/rss/topfreeapplications/limit=10/json` relu le 27/10 à 16 h UTC ; le robot `rss.marketingtools.apple.com` expire depuis la routine). C'est la même logique que le chantier n°0 (lire la source qui tranche).
Quelques heures avant midi, le n°1 du moment le reste presque toujours : on achète son OUI quand le marché le cote moins que cette chance.

## Ce qui a été relevé aujourd'hui (27/10, 16 h UTC)
- Gagnants des vendredis récents : gratuit Muse from Meta (4 fois de suite en septembre-octobre), ChatGPT, MapQuest, TikTok Pro - Events, puis Capital One Mobile le 23/10 ; **payant : Shadowrocket 11 fois sur 12** (« another app » le 18/09). Le prochain règlement est le vendredi 30/10 à 12 h ET (16 h UTC) : la stratégie n'a donc une chance d'acheter que les vendredis, de 10 h à 15 h 45 UTC.
- Gratuit : 1. TikTok Pro - Events, 2. Vinted, 3. Muse from Meta, 4. ChatGPT, 5. Capital One Mobile. Payant : 1. Minecraft: Play with Friends!, 2. Shadowrocket.
- Le marché du 30/10 cote Vinted 0,52 (n°2 aujourd'hui), TikTok Pro 0,31 (n°1), Muse 0,20 ; payant : Shadowrocket 0,89 alors qu'il n'est que n°2 aujourd'hui. À trois jours, les prix ne disent rien du classement de ce soir : c'est pourquoi la stratégie ne joue que les 6 dernières heures.
- Ce que `familles_tranches.md` avait déjà montré sur l'archive des marchés (182 événements réglés) : le gagnant de la semaine précédente, coté 0,74-0,80, gagne 48 fois pour 59,3 attendues à 24 h (z des prix −4,1) : le marché surcote la stabilité du classement.

## Ce que fait la stratégie (`ClassementAppStore`, `appstore.py`, `sources/appstore.py`, tests `tests/test_appstore.py`)
- Source `appstore` (10 minutes) : top 10 gratuit et payant ; mode dégradé si Apple ne répond pas (la stratégie s'abstient : « classement pas à jour » après 30 minutes).
- Rattachement `references["appstore"]` : rang de l'application du marché, n°1 du moment, heures avant midi de l'Est (heure d'été ou d'hiver via `zoneinfo`), chance de rester n°1 : **0,95 dans l'heure, 0,90 à 3 h, 0,85 à 6 h, rien au-delà (hypothèses, aucune mesure)**.
- Achat du OUI du n°1 si l'ask est entre 0,30 et 0,90 et au moins 0,04 sous la chance supposée (moins une marge de 0,02) ; jamais dans le dernier quart d'heure ; Kelly entier, le carnet limite la quantité.
- Journal du classement `appstore:histo` dans la base (5 premiers gratuit et payant toutes les 30 minutes, 21 jours, sauvegardé avec `essentiel.sqlite.gz`) : c'est lui qui permettra d'**étalonner** les 0,95 / 0,90 / 0,85 (combien de fois le n°1 de 6 h / 3 h / 1 h avant midi l'était encore à midi) dès qu'il y aura une dizaine de jours.

## Ce qu'une perte apprendrait / suite
- Une perte dirait que le classement bouge plus vite que les hypothèses (lancements, promotions comme « TikTok Pro - Events » qui n'est pas une vraie appli grand public) ou que le flux d'Apple retarde sur l'App Store ; le journal chiffrera lequel.
- Premier jugement vers le 03/11 (les événements du 30, 31/10, 1-2/11), puis étalonnage de la chance de rester n°1 sur le journal, puis seulement une mise franche.
- Vérification à faire au premier achat : le prix payé réel contre le carnet, et le classement lu à midi contre le règlement Gamma.
