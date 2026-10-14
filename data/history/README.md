# Historique des marchés résolus

Construit par `scripts/build_history.py` (reprenable). **Version 2, non biaisée** : 40 jours
d'échéance tirés au hasard (`experiments/jours_v2.txt`), tous les marchés binaires résolus
sans filtre de volume, tirage uniforme de 40 % des marchés (`experiments/PROTOCOLE_v2.md`).
Un fichier par mois d'échéance :
`markets_AAAA-MM.jsonl.gz`, une ligne JSON par marché.

| champ | sens |
|---|---|
| `id`, `event_id`, `question`, `slug`, `series`, `tags` | identification (Gamma) |
| `outcomes`, `yes_token` | issues ; jeton de l'issue n°0 dont on stocke le prix |
| `winner` | 0 si l'issue n°0 a gagné, 1 sinon (résolutions 1/0 uniquement) |
| `end`, `closed`, `start` | échéance prévue, clôture réelle, ouverture (horodatages Unix UTC) |
| `volume` | volume final : connu après l'issue, **interdit comme filtre** (biais de sélection) |
| `category`, `fee_rate` | catégorie et taux de frais taker (barème réel, ou déduit des tags) |
| `neg_risk` | marché d'un événement à plusieurs issues exclusives |
| `points` | `[décalage en secondes par rapport à min(end, closed), prix de l'issue n°0]`, horaire, 72 h |

Règles d'usage : ne jamais lire un point postérieur à l'instant de décision ; mesurer
l'horizon par rapport à `end` (connu à l'avance), jamais par rapport à `closed`.
Les marchés 50-50, annulés ou sans échange sont exclus (limite à garder en tête).
