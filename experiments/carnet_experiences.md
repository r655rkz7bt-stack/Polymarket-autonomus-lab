# Carnet d'expériences : ce que chaque perte nous a appris

Décision d'Etienne (27/10/2026) : « ne sois pas paralysé par les pertes, vois-les comme des essais et des expériences pour
améliorer et aller chercher de plus gros gains ». Une stratégie qui perd dans son fantôme n'a rien coûté au capital
principal : c'est une expérience payée en argent fictif. Elle doit rapporter une **leçon chiffrée** et, si possible,
l'**expérience suivante**.

Règles du carnet (docs/METHODE.md, « Cap sur l'objectif ») :
- une ligne par expérience terminée (stratégie éliminée ou retirée, piste écartée qui avait un fantôme), dans la même pull
  request que l'entrée du journal de recherche ;
- la leçon est un fait chiffré (gagnés contre attendus, prix payés, euros), jamais une impression ;
- « Et ensuite » dit ce qu'on en fait : une expérience nouvelle, un correctif, ou « ne plus refaire ».

Chiffres : journaux publiés au 26/10/2026 23 h 35 UTC (`experiments/audace/`, `published/rapports/brief.md`), sauf mention.

| Expérience | Ce qu'elle a coûté (fantômes) | Ce qu'on a appris | Et ensuite |
|---|---|---|---|
| Favoris : `naive_favorite` et ses filles (67 stratégies) | 3 698 paris, −3 418 € cumulés | Le favori n'est pas sous-coté sur Polymarket : −1,7 point par pari, frais compris ; les 58 stratégies de favoris ne diffèrent pas réellement entre elles (Q 58,7 pour 57). Sur le passé : 50 232 paris, 25 cases sur 35 négatives (`favoris_avant_match.md`) | Plus de filles de favoris (l'entonnoir ne les propose plus) ; le principal les copie petit (plafond 5 %, à l'équilibre au rejeu) |
| Billets sous 0,10 (`loterie_meteo`, les « contrer », outsiders) | 214 paris, 3 gagnés pour 10,8 attendus, −74 % par mise | Les loteries sont surcotées partout (biais favori-outsider) | Jamais sous 0,10 sans source qui tranche ; les filles « audace » s'arrêtent à 0,10 |
| Contre-mouvement crypto (`contrer_crypto`, `contrer_crypto_patiente`) | 263 paris, −94 € | La perte cachait un avantage : 0,10-0,45 fait 58 gagnés pour 39,3 attendus ; les billets sous 0,10, 1 sur 80 ; les grosses mises perdaient | Expériences `contrer_crypto_audace` et `contrer_crypto_patiente_audace` (27/10) : 0,10-0,45, mises ×9 |
| Grosses mises du principal (copie au prorata, avant le 27/10) | principal −253 € réalisés, presque tout avant le 20/10 | Les plus grosses mises copiées (favoris à 0,90 ou plus, Kelly sur un biais supposé) perdaient −11,5 % par euro | Mise copiée plafonnée à 5 % du capital du fantôme : rejeu −262 € → −46 € (`taille_des_mises.md`) |
| Tenue de marché (`market_maker`, `market_maker_serre`) | 306 opérations, −800 € (z −8,0 et −9,5) | Nos ordres posés sont servis surtout quand on a tort (sélection adverse) ; les récompenses ne compensent pas | Pas de tenue de marché sans avantage de vitesse ou d'information |
| Carnet penché (`market_structure`, `market_structure_patiente`) | 497 opérations, −680 € | Le déséquilibre acheteurs/vendeurs du carnet ne prédit rien qui survive aux frais | Ne plus refaire |
| Météo par prévision unique (`meteo_prevision`, `_patiente`) | 200 paris, −509 € | +28 % sur l'historique, −6 % aux prix réellement payés : le marché lit déjà les modèles (`meteo_backtest.md`) | Relevé des ensembles (82 membres, `meteo_ensemble.md`) ; toujours juger aux prix payés |
| Actualités (`news_momentum`, `_patiente`) | 151 paris, −140 € | Notre cycle de 5 minutes arrive après le prix | Pas de stratégie de vitesse sur les nouvelles |
| Après l'échéance (`apres_echeance`) | 170 paris, −351 € | « Échéance passée » d'un match = coup d'envoi : paris en plein match, jusqu'à 8 jambes d'un même match (−474 € une soirée) | Corrigé (enquêtes du 23/10) ; `game_start` pour tout le sport |
| Cotes de bookmakers (`cotes_bookmakers`) | 20 paris, −375 € | Les cotes « vainqueur » étaient appliquées aux handicaps (défaut de rattachement) | Corrigé (vainqueur seulement) ; relire 10 paris à la main avant de croire une source externe |
| Copie des meilleurs portefeuilles (`smart_money.md`, sur le passé) | — | Le top 1 % copié avec le retard de notre cycle fait −9,7 % après frais | Ne plus refaire |
| Suivre l'argent neuf et concentré (`inities.md`, sur le passé, 27/10) | — | 48 réglages, aucun ne bat ses prix (référence : 94 paris, 39 gagnés pour 42,2 attendus, −9,7 %) : les comptes neufs sont surtout de nouveaux joueurs sur des outsiders ; on n'entend parler que des initiés qui ont eu raison | Expérience `suivre_inities` : seulement quand la presse ou les commentaires parlent de paris suspects, à 0,30 ou plus |
