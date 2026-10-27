# 27/10/2026 (16 h) : une stratégie à modèle propre jamais rejouée sur le passé (`decroissance_temps`) et une stratégie « muette » qui ne l'est pas

Point de départ : aucune « Enquête obligatoire » grave dans la feuille de mission (seulement `cycle_arrete` après relecture d'un cycle vieux d'une heure : les journaux étaient lus à 15 h 56, pas de défaut).
Les constats « à regarder » : `copie_fidele` (Team Yandex, déjà élucidé le 26/10), `champion_sans_avantage` / `chance` (pas des défauts, décision du 27/10), et **`estimation_perimee` : `decroissance_temps`, NON estimé 0,928 payé 0,708 (+0,21 d'écart net, 6 h)**.
Famille du jour (27 mod 6 + 1 = 4, « le filtre ne filtre pas ») puis famille 6 (« ce qui ne tourne plus »).

## 1. `decroissance_temps` : l'écart n'est pas un carnet périmé, c'est un modèle sans test
- **Constat** (journal signé, 76 achats du 20 au 27/10, 9 réglés : 7 gagnés pour 7,7 attendus, +2,5 €). En retrouvant le prix « d'il y a 6 h » de chaque achat par la formule de la stratégie (`fair = 1 − (1 − p6)^(h/(h+6))`), **24 achats sur 76 (561 € sur 1 140 € misés) ont eu le OUI en HAUSSE d'au moins 1,5 fois en 6 h**
  (de 0,2 % à 2,1 %, de 7,4 % à 29,2 %). La règle « le OUI n'a pas assez fondu » achète surtout des sauts de prix que le filtre d'actualité (`max_spike`, pics de mentions) ne voit pas. Le prix payé est bien celui du carnet : c'est l'estimation qui est fausse.
- **Cause** : la stratégie est née le 20/10 dans les « vingt pistes » avec un essai à blanc en direct, jamais un test sur le passé (`vingt_pistes.md` : 31 candidats, 1 proposition). Tout ce qui a suivi (Kelly 0,25 sur des écarts de 0,05 à 0,21) reposait sur une thèse non mesurée.
- **Mesure** (`experiments/decroissance_passe.md`, 6 080 marchés « d'ici / avant » réglés, vrais échanges, frais payés) : règle de la stratégie **742 paris, 610 gagnés pour 624,7, −2,6 %** (t par événement −2,60) ; estimation moyenne du NON 0,874 pour 0,822 réalisé ; écart ≥ 0,10 : −10,8 % ; NON de tous les marchés à OUI 3-35 % : −3,2 % (z −2,5). Pas de « prime d'espoir ».
- **Correctif** : stratégie coupée (`enabled: false`, tests mis à jour) ; ses 60 positions ouvertes se règlent (le principal ne la copiait pas : 0 achat dans son journal). Ligne au carnet d'expériences.
- **Contrôle ajouté** (`enquete.sans_test_passe`, « à regarder ») : une stratégie qui achète (≥ 20 achats) sans que son nom ou sa classe figure dans un compte rendu d'`experiments/` (hors journal, listes de pistes, carnet, enquêtes, « vingt pistes ») est signalée ; les filles héritent du test de leur mère.
  Tests `test_a_strategy_with_buys_but_no_written_test_on_the_past_is_a_lead` et `test_read_experiments_skips_the_journal_the_pistes_lists_and_the_enquiries`. Aujourd'hui il ne signale plus rien (decroissance_temps coupée et rejouée) : il est là pour la prochaine.

## 2. `moins_de_kills` : « abstentions {} » alors que 5 marchés passaient le filtre
- Cycle local : 477 marchés « hors du filtre titre_contient », 5 qui passent le filtre (événements de LoL) mais **aucune raison notée** pour ces 5 : `propose` sautait sans trace les marchés qui ne sont pas des totaux de kills. Ce n'était pas une stratégie sourde : à 16 h UTC, les marchés de kills des parties 1 du 28-30/10 n'existent pas encore.
- Créés quand ? 399 marchés `kill_over_under_game` des 40 derniers événements de LoL : `createdAt` médian **0,28 h APRÈS** le coup d'envoi du match (les parties 2 et 3 sont créées pendant la série) ; seuls ~1/3 sont créés ≥ 2,5 h avant, ceux de la partie 1 vers 22 h la veille (ex. match du 26/10 à 21 h : créé le 25/10 à 22 h 06). La fenêtre de la stratégie (12 h → 2 h avant) ne voit donc que la **partie 1**, créée la veille au soir : premier achat attendu le 28/10 en matinée UTC.
- **Correctif** : abstentions « pas un total de kills d'une partie » / « hors de la fenêtre avant le match » (cycle local : 5 comptés) ; test.

## 3. Ce qui a été vérifié et n'était pas un défaut
- Filtre de plage de prix et d'échéance de `decroissance_temps` : horizons 15 à 641 h (fenêtre 12-720 h), OUI 0,02-0,35 ; l'achat à OUI 0,021 (NON payé 0,979) est le prix d'achat, le milieu du carnet était ≥ 0,03.
- Les achats sont tous des « NON » (une seule direction), sans jambe jumelle ni deux camps.
- `refus_principal` (49 refus « taille inférieure au minimum du marché (5) » en 48 h) : la sauvegarde `essentiel.sqlite.gz` ne contient pas la table des décisions, donc pas de date par refus ; la fenêtre sera entièrement postérieure au plancher de copie (26/10 16 h 34) demain à 16 h 34 UTC : à relire alors.
