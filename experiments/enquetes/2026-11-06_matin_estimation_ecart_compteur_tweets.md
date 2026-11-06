# 06/11/2026 matin — constat `estimation_perimee` de `compteur_tweets` (estimé 0,968, payé 0,72)

**Question.** Le constat « à regarder » cite des achats de `compteur_tweets` où le modèle dit 0,968 et le prix payé est 0,72
(marché Trump « 200+ posts Truth Social du 30/10 au 13/11 », achat du 04/11 à 01 h, 124 parts). Carnet périmé, mauvais marché
rattaché, ou modèle qui s'emballe ?

**Vérifié.**
- Le journal signé donne les niveaux du carnet réellement lus (0,72 × 74,29 puis 0,73 × 50) : le prix payé est celui du carnet
  du cycle, pas un prix périmé. Marché relu sur Gamma (`/markets/6625358`) : bien le marché Truth Social de Trump, règle « Post Counter »
  de xtracker. Pas de mauvais rattachement.
- Écart modèle moins prix sur les 136 achats de `compteur_tweets` (96 réglés) :

| écart (estimé − payé) | paris réglés | gagnés (paiement) | attendus par les prix | attendus par le modèle | rendement |
|---|---|---|---|---|---|
| < 0,05 | 65 | 49,0 | 42,2 | 44,2 | +13,8 % |
| 0,05-0,10 | 16 | 12,0 | 10,5 | 11,7 | −12,5 % |
| 0,10-0,15 | 5 | 4,0 | 2,9 | 3,5 | +67 % |
| 0,15-0,25 | 6 | 2,0 | 2,7 | 4,0 | −26 % |
| ≥ 0,25 | 4 | 3,0 | 1,5 | 3,2 | +106 % |

Les gros écarts sont rares (10 réglés sur 96) et trop peu nombreux pour conclure dans un sens ou dans l'autre (5 gagnés pour 4,2
attendus par les prix, 7,2 par le modèle). Pas de sur-confiance démontrée.

**Verdict : aucun défaut.** Le constat est un désaccord marqué du modèle avec le marché, pas un carnet périmé. Le pari de 0,968
se règle le 13/11 : à relire alors (c'est le seul cas à 0,97 de l'historique ; la piste `compteur_truth_dispersion_6_audace`
teste justement une dispersion plus large).
