# Piste « fatigue NBA » (20/10/2026, 20 h UTC) : écartée

**Question** : le prix d'un match NBA tient-il compte du repos (dos-à-dos, 3 matchs en 4 soirs, jours de repos
d'écart) ? Si l'équipe fatiguée gagne moins souvent que son prix, acheter l'adversaire reposé rapporte.

**Données** (scripts : `experiments/nba/scripts/`, données dans `donnees/`, ignoré par Git)
- Calendrier et scores 2025-26 : basketball-reference.com (pages mensuelles, via curl : `requests` y est refusé en 403) →
  1 322 matchs.
- Marchés « vainqueur » réglés de Polymarket (Gamma, `series_id` 10345) : 1 479 ; 1 231 rattachés à un match.
- **Contrôle du règlement** : le jeton « visiteur » vaut 1 exactement quand le visiteur a gagné, 1 231 sur 1 231.
- Prix : dernier point du CLOB `prices-history` (pas de 10 min) au moins 1 h avant le coup d'envoi (1 222 matchs entre 0,05 et 0,95).
  Repos calculé sur le calendrier complet (jamais de regard vers le futur : seulement les matchs avant la date).
- Frais : 5 % × p(1−p) (feuille `feeSchedule` du marché), écart achat-vente 0,01.

**Résultats** (équipe « fatiguée » = celle qui a le moins de repos ; gain = acheter l'adversaire reposé)

| Cas | n | prix fatiguée | gagnés | z | gain par mise | verdict |
|---|---|---|---|---|---|---|
| visiteur dos-à-dos, domicile reposé | 137 | 0,403 | 0,474 | +1,89 | −19,0 % | écartée (sens inverse) |
| domicile dos-à-dos, visiteur reposé | 130 | 0,504 | 0,477 | −0,69 | +12,4 % | indice (t événement +0,89, 5 mois sur 7) |
| les deux dos-à-dos | 66 | 0,506 | 0,561 | +0,99 | −22,6 % | écartée |
| visiteur 3 matchs en 4 soirs | 189 | 0,416 | 0,402 | −0,43 | −2,0 % | écartée |
| domicile 3 matchs en 4 soirs | 204 | 0,502 | 0,500 | −0,07 | −9,7 % | écartée |
| visiteur ≥ 2 j de repos de plus | 40 | 0,527 | 0,450 | −1,15 | +38,3 % | indice (40 matchs seulement) |
| domicile ≥ 2 j de repos de plus | 57 | 0,385 | 0,386 | +0,01 | −1,1 % | écartée |

- Régression résultat − prix sur l'écart de repos : pente +0,0074 par jour (t +0,47) ; 1re moitié de saison +0,017, 2e
  moitié −0,003 : pas d'effet régulier.
- 7 découpages essayés (et 3 réglages de repos) : les deux « indices » vont dans des sens opposés (la fatigue du visiteur
  ne paie pas, celle du domicile paie) et ne résistent pas à un contrôle de sélection (7 cas, 2 positifs sans cohérence).
- Rappel favoris NBA : 0,80-0,95 → prix 0,864, gagnés 0,848 (n 282) ; 0,50-0,65 → prix 0,576, gagnés 0,537 (n 510) : le
  favori ne gagne pas plus que son prix (cohérent avec « autres sports » de `tennis.md`).

**Verdict : écartée.** Le marché tient compte du repos. Rien dans l'arène. (Contrairement à la NHL, où l'indice était +6 %,
t +1,2 sur 2 saisons.) Piste à ne pas refaire sans donnée nouvelle (fatigue de voyage, absences de joueurs).
