# Promotion du champion : des preuves, pas du hasard (17/10/2026, AMELIORATION n°1)

**Constat.** `meteo_prevision` a été promu champion le 17/10 à 08:32 UTC (20 opérations, +3,1 %),
destitué à 15:27 (capital retombé sous 1 000), puis suspendu (les frais mangent son avantage). Le
capital principal a gardé ses 41 paris météo : 54 % du capital, −64 de gains latents le soir même.

**Le score de confiance.** Pour chaque stratégie : résultats de ses opérations clôturées, moyenne
divisée par l'erreur type (t de Student). Au-dessus de 2, il est peu probable que ce soit du hasard.

| Stratégie (au moment indiqué) | opérations | résultat | confiance t |
|---|---|---|---|
| meteo_prevision, 17/10 08:32 (promu) | 20 | +31,90 | **0,61** (hasard) |
| naive_favorite, 17/10 17:28 | 11 | +93,16 | 2,39 |
| nf_sport_patiente, 17/10 17:28 | 12 | +89,09 | 1,09 |
| news_momentum, 17/10 17:28 | 11 | +6,26 | 0,55 |

**Rejeu de l'arène** (`experiments/promotion/rejouer.py`, 56 journaux fantômes, 15/10 12:17 →
17/10 17:28) : avec la règle actuelle, une seule promotion (meteo_prevision) ; avec t ≥ 1,0, 1,5 ou
2,0, aucune. Le rejeu « copie » la valeur des fantômes heure par heure ; il ne reproduit pas les
achats réels du principal (il donne même un léger gain pour meteo_prevision, alors que les paris
réellement achetés par le principal perdent). **Une seule promotion en 2,5 jours : trop peu pour
chiffrer un gain moyen.** Ce qui est sûr : la règle t ≥ 1,5 aurait refusé une promotion fondée sur
du hasard.

**Décision (config/promotion.yaml).**
- `min_t_stat: 1.5` en plus des 20 opérations et des +2 % ;
- période d'essai : la part engagée croît avec les opérations clôturées (25 % au départ, entière
  à 60) ;
- tenue de marché jugée sur ses journées de récompenses (3 au moins, part plafonnée à 30 %) ;
- favori politique jugé sur la valeur de ses positions au prix du carnet (3 jours au moins, part
  plafonnée à 20 %).

**Limites.** Le t de Student suppose des résultats indépendants (plusieurs marchés d'un même
événement ne le sont pas) ; une stratégie aux gains réguliers et rares pertes énormes (favoris à
0,95) peut afficher un t élevé avant sa première grosse perte : la période d'essai limite ce risque.
