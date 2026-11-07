# Bilan du labo v1 (14/10 → 07/11/2026) : ce qui n'a pas marché, ce qui a marché

Demande d'Etienne (07/11/2026) : « Ça ne marche pas. Arrêter ce labo, faire un compte rendu de ce qui ne marche pas, et
repartir avec beaucoup plus de liberté pour Claude et le chercheur. » Chiffres : tableau de bord publié le 07/11 17 h 57 UTC.

## Les chiffres
- **Capital principal : 1 000 → 651 € estimés (681 € réalisés), −35 %** ; plus haut 1 049 € le 18/10 ; repli maximal 39 % ;
  aucun palier depuis 23 jours.
- **Arène : 190 stratégies** créées, 97 éliminées ou retirées, 13 532 opérations de fantômes. Somme des écarts au capital de
  départ : **−9 793 €** (favoris : 89 stratégies, −5 359 € ; autres : 101 stratégies, −4 434 €). Capital médian des
  stratégies actives qui ont tradé : 998,7 € (= le hasard moins les frais).
- **Recherche : 96 pistes testées sur le passé** : 64 écartées, 24 « indices », 4 retenues ; 86 enquêtes ; 123 entrées de
  journal ; 22 expériences coûteuses au carnet (`carnet_experiences.md`).
- **Les 3 meilleures stratégies du jour** (nf_sport, nf_sport_prix_haut, naive_favorite : 1 220-1 232 €) ont le verdict
  « indéterminée (le résultat peut être dû au hasard) » ; la n° 1 de la semaine dernière (nf_sport_patiente_prix_850_875,
  1 566 € le 27/10) est retombée à 1 061 € deux jours plus tard.

## Pourquoi ça n'a pas marché (diagnostic)
1. **Presque toutes les stratégies jouaient la même idée sans avantage** : acheter le favori. 89 variantes de favoris, qui ne
   diffèrent pas réellement entre elles (un seul tirage, −1,6 point par pari). Sur le passé, 50 232 paris de favoris :
   aucune tranche régulièrement gagnante. Les marchés liquides de Polymarket sont bien calés ; frais et écart achat-vente
   suffisent à faire perdre une stratégie sans information.
2. **Trop de fantômes = la chance se fait passer pour du talent.** Parmi 190 stratégies, la meilleure a un z ≈ 2 par pur
   hasard. Le principal suivait les meilleures du moment (souvent la chance) puis les lâchait au premier creux (corrigé le
   01/11 : −51 € → +32 € au rejeu, mais trop tard et trop petit).
3. **Aucun avantage de vitesse** : un cycle de 5 minutes contre des robots à la milliseconde. Les stratégies « nouvelles »,
   « momentum », « tenue de marché » ont perdu (−140 €, −800 €) ; les ordres posés sont servis surtout quand on a tort
   (sélection adverse : −9,8 % par pari quand ils sont servis en match).
4. **Les vrais avantages trouvés étaient petits, rares et lents** : compteurs de tweets (`compteur_tweets`, seule stratégie
   « prometteuse » solide : 108 opérations, +20 %), NON des marchés crypto (un pari à la baisse déguisé), cartes et kills
   d'e-sport (Under), drames improbables. Le principal leur donnait trop peu (plafonds, mise mesurée, période d'essai).
5. **La recherche cherchait surtout des biais statistiques dans les prix** (favori, momentum, calibration, tranches) : 64
   pistes écartées pour la même raison (le prix contenait déjà l'information). Peu de recherche sur **l'information que le
   marché n'a pas encore** (source de résolution lue avant le marché, règlement mal compris, nouvelles lentes à arriver).
6. **Trop de prudence empilée** : plafonds, période d'essai, garde-fou par jour, mise mesurée à 0, retrait rapide, seuils
   d'entrée : le principal n'engageait que 16-20 % de son argent, sur les stratégies les moins mauvaises du moment.
7. **Stop-loss et sorties anticipées** : testés sur 9 879 positions, tous perdants (le marché sur-réagit après une chute).

## Ce qui a marché (à garder)
- L'**infrastructure honnête** : journal signé, règle n°1, simulateur sur vrais carnets avec frais, audit indépendant,
  tableau de bord, cycle sur GitHub Actions + cron-job.org, sauvegardes. Aucun incident de triche ni de perte de journal.
- Le **protocole de test sur le passé** (vrais échanges, prix payés, confiance par événement, deux moitiés) : il a évité
  beaucoup de fausses bonnes idées (stop-loss, momentum, totaux de sport, copie des « baleines »).
- Les **indices réels** : compteurs de tweets / Truth Social, Under des cartes et kills d'e-sport, NON des drames, lecture
  des sources de résolution (App Store, USGS, ensembles météo), comptes suspects (Ballon d'Or).
- L'**arène** comme outil de mesure en direct (gratuite), à condition de ne pas la remplir de variantes.

## Leçons pour la v2
- Moins de stratégies, plus profondes ; jamais une variante sans raison nouvelle.
- Chercher un **avantage d'information ou de règle**, pas un biais de prix : lire la source de résolution avant le marché,
  modéliser ce que le marché ignore, lire les règles mieux que la foule.
- Laisser Claude **prendre position lui-même** sur des marchés qu'il a étudiés à fond (prévision écrite, vérifiable).
- Miser franchement sur ce qui est prouvé, pas un peu sur tout.
