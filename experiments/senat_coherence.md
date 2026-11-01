# Sénat 2026 : l'échelle des sièges républicains contre les 35 courses d'État (01/11/2026)

**Verdict : écartée (le marché est cohérent), rien dans l'arène.** Suite de la piste n° 16 (`coherence_sieges.md`) : on a refait le test de cohérence sur
la famille la plus échangée (Sénat), où les deux côtés ont 0,3 à 1,2 M$ de liquidité par tranche.

## Question
« Republican Senate seats after the 2026 midterm elections? » (événement 106193, 11 tranches de ≤ 47 à 57+, 0,2 à 1,2 M$ de liquidité chacune) dit-elle la même chose que
les 35 marchés « <État> Senate Election Winner » ? Base : 31 sièges républicains qui ne sont pas renouvelés (53 − 22 sièges républicains en jeu).

## Méthode (scripts : `experiments/familles_nouvelles/senat_coherence.py`, `senat_facteur.py`)
Prix en direct du 01/11/2026 ~06 h UTC (Gamma, sans clé). Chance républicaine de chaque course = prix du candidat (R) normalisé par la somme des prix de la course (0,99 à 1,01).
1. Courses indépendantes : P(R ≥ 51) = 3,5 % contre 18,2 % au marché ; P(R ≥ 53) = 0,1 % contre 5,4 %. Écart énorme, mais sans signification : les courses bougent ensemble (vague nationale).
2. Copule gaussienne à un facteur, une seule corrélation ρ pour les 35 courses : l'écart (KL marché||modèle) passe de 0,344 (ρ = 0) à **0,031 pour ρ = 0,3**. À ρ = 0,3 le modèle rend
   ≤ 47 : 0,488 (marché 0,485) ; 48 : 0,133 (0,145) ; 49 : 0,119 (0,110) ; 50 : 0,095 (0,095) ; 51 : 0,068 (0,070) ; 52 : 0,044 (0,061) ; 53 : 0,026 (0,039) ; 54+ : 0,024 (0,015).
   Aucune tranche ne s'écarte de plus de 1,7 point (la plus grosse : « 52 », 0,044 contre 0,061).

## Lecture
Un seul paramètre de corrélation (0,3, plausible) suffit à retrouver les 11 tranches à ±1,7 point : l'échelle et les courses disent la même chose. Pas d'incohérence à acheter,
contrairement aux échelles d'État de la Chambre (Caroline du Nord −1,85 siège, liquidité de quelques k$). Conséquence pour `sieges_coherence` : les écarts de la Chambre
viennent plutôt de marchés d'échelle minces que d'une règle générale (à confirmer le 04/11 par les règlements).

## Limites
Une seule photo (pas de test sur le passé : aucune échelle de ce type n'est réglée). ρ est ajusté sur l'échelle elle-même, donc le test dit « il existe une corrélation qui rend tout cohérent »,
pas « le marché a raison ». Les 22 sièges républicains en jeu supposent la composition actuelle (53 R) : une erreur d'un siège décalerait l'échelle entière.
