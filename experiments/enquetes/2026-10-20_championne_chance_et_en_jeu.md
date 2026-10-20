# 20/10/2026 (soir) : la championne est-elle chanceuse ? (obligation « le 18/10 fait 88 % du gain »)

Passage chercheur ~15 h UTC. Journaux publiés du 20/10 14:50 UTC, `nf_sport_patiente_v1.0.0` (fantôme
copié par le principal) : 93 paris réglés, +276 €, 6 471 € misés au total (rendement +4,3 % par mise).

## Constat (chiffres)
1. **Le 18/10 fait +298 € sur +276 €** : 29 paris, 29 gagnés pour 24,5 attendus par les prix ;
   probabilité de gagner les 29 aux prix payés = 0,7 %. Les trois autres jours : −101 / −40 / +119 €.
   Sans le 18/10 la championne est à −22 €. Sans ses 3 meilleurs paris : +178 € (le gain ne tient pas
   à 3 paris, il tient à une journée de série).
2. **Elle gagne à peine plus souvent que ses prix** : 86 gagnés pour 79,8 attendus (z = +1,86).
   Parmi les 35 stratégies de plus de 15 paris, le z maximal attendu sans aucun avantage est ≈ 2,1 :
   **la championne est le « meilleur de 35 »**, pas une avance prouvée (P(hasard) corrigée ≈ 1,0).
   Les variantes non patientes ont le même rendement : `nf_sport` +4,3 % (36 gagnés / 35,9), `nf_court`
   +4,0 %, `naive_favorite` +6,7 %. L'ordre posé n'a donc rien prouvé ; le « P(hasard) 0,06-0,08 » du
   moteur d'apprentissage ne tient pas compte du nombre de stratégies essayées.
3. **84 % des achats ont lieu après le coup d'envoi** (74 sur 88 dont l'heure est connue, 5,6 k€ sur
   6,2 k€ misés) alors que son « horizon » affiché vaut 165 h en médiane : c'est l'échéance placeholder
   de Gamma (ex. match du 20/10, `endDate` 27/10). Le règlement réel arrive en médiane 2,2 h après
   l'achat (84 achats sur 93 en moins de 6 h). Rendement selon le moment : avant le début +6,8 % (10),
   0-1 h après +11,7 % (16), plus d'1 h après +2,9 % (58), sans heure +15,8 % (5) : rien de significatif.
   Conséquence : les filles « délai 72-168 h » / « 6-24 h » (`echeance_*`, `delai` du pareto) ne mesurent
   pas un délai mais la convention de date de fin de chaque sport (tennis : +7 jours).
4. **Les deux camps d'un même match** : Team Falcons (0,918, 222 €, −223 €) puis BetBoom (0,871, 22 €)
   le 17/10 ; Safiullin (0,912, 70 €, perdu) puis Shimabukuro (0,853, 85 €, gagné) le 20/10. Quatre paris,
   −275 € nets. Seules les variantes à ordre posé (`patiente_*`, `tennis_prix_bas`) le font : un ordre posé
   se remplit quand le prix tombe, donc souvent quand le favori s'effondre en jeu. Pas de défaut de
   règlement : 10 paris tirés au hasard relus sur Gamma (famille 3), résolution, camp et type de pari
   (moneyline, spread, carte gagnée) tous conformes au journal.
5. **Copie à 100 % sur exécution partielle** (constat « à regarder » de l'enquête automatique, mené
   jusqu'au bout) : sur les 32 paris de la championne copiés par le principal depuis le 19/10, 30 sont à
   33-38 % de la taille du fantôme (c'est l'échelle voulue : capital du principal / capital du fantôme) ;
   2 sont à 100 % (Mannarino 5,32 parts le 19/10, Lynn Vision 33,34 parts le 20/10). Cause : un ordre posé
   du fantôme (97,7 parts demandées, 33,3 obtenues) est recopié par le principal à sa taille *demandée* ×
   0,35 (34 parts), et non à sa taille *obtenue* × 0,35 (11,7) ; le carnet mince donne alors aux deux la
   même quantité (`Principal._copy` → `limit_orders`, `main.py`). Ampleur : 2 paris sur 32, 33 € au lieu de
   ≈ 11 € pour Lynn Vision (3,5 % du capital), gagnants tous les deux. Non corrigé : le principal reposte
   l'ordre et laisse le carnet décider, une copie « à la taille obtenue » demanderait de suivre les
   exécutions partielles d'un cycle à l'autre ; le contrôle `copie_fidele` le signale déjà.

## Cause
Pas de bug de calcul : une série de chance sélectionnée (meilleur de 35 sur une période de 3,2 jours),
plus un champ (`horizon_hours`) qui ne dit rien du moment réel du pari. Le journal ne contenait pas
l'heure du coup d'envoi : impossible de savoir, après coup, si l'achat était avant ou pendant le jeu.

## Correction
- `main.py` (`_depuis_coup_d_envoi`) : chaque achat inscrit `depuis_coup_d_envoi_h` (heures depuis le
  coup d'envoi Gamma, négatif avant) dans `extra`, pour les achats directs et les ordres posés.
- `enquete.py` : trois contrôles, `selection_multiple` (z corrigé du nombre de stratégies, sur les
  stratégies copiées), `deux_camps` (deux camps achetés ≥ 0,70), `achats_en_jeu` (part d'achats après le
  coup d'envoi, à partir du nouveau champ).
- Tests (`tests/test_enquete.py`) : la série de 29 gagnés ne passe pas le seuil corrigé, les deux matchs
  Falcons/BetBoom et Safiullin/Shimabukuro reproduits, journaux anciens sans le champ sans erreur.
- Aucun changement du noyau ni du comportement des stratégies (le changement de comportement serait
  d'exclure les paris en jeu ou d'agir sur le camp opposé : à décider sur données ; voir « reste ouvert »).

## Ce qu'il faut en conclure
Ne pas croire que `nf_sport_patiente` « a un avantage » : sur 93 paris, elle fait ce que ses prix
promettent (+4 % de rendement comme sa mère) avec une série chanceuse. Le test honnête sera : ses
paris à partir du 21/10 (pas de sélection sur eux).
