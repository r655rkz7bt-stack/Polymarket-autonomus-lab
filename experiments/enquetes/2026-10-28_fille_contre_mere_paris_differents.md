# 28/10/2026 : la championne `nf_sport_patiente_prix_850_875` ne joue pas « sa mère filtrée »

Famille 5 (comparaisons faussées : jour 28 → 28 mod 6 + 1). Scripts : `scripts/fille_contre_mere_28_10.py`, `scripts/fille_contre_mere_cash_28_10.py`
(journaux signés du 28/10 à 0 h 50 UTC, `charge_fantome.charger`).

## Constat
`nf_sport_patiente_prix_850_875` (n° 1 de l'arène, 1 566 €, 74 opérations depuis le 20/10) est une fille de `nf_sport_patiente` avec le seul filtre « prix 0,85-0,875 ».
Elle devrait donc jouer un SOUS-ENSEMBLE des paris de sa mère. Ce n'est pas le cas :
- la mère a 20 paris dans cette plage de prix depuis la naissance de la fille, la fille en a 74 ; **59 paris de la fille n'existent pas chez la mère**, 15 sont communs, 5 sont chez la mère seule ;
- sur les 15 paris communs, les deux rendent pareil (+16,3 % et +16,3 %) : le code est cohérent, c'est le CHOIX des paris qui diffère ;
- les 59 paris de la fille seule : +324 € sur 7 414 € misés (+4,4 %), contre −38 € (−16,5 %) pour les 5 de la mère seule ;
- cause en partie vue : la mère (Kelly entier) manquait d'argent disponible pour 12 des 37 paris de la fille seule pour lesquels un battement la précède (cash médian de la mère 331 €, mise médiane de la fille 122 €) ;
  pour 11 autres la mère a joué un AUTRE pari dans les 15 minutes (une mise par cycle, le meilleur de la mère n'est pas dans la plage) ; les 14 restants ne s'expliquent pas avec le journal seul
  (la table `decisions` n'est pas dans la sauvegarde) ;
- aucun cycle n'a plus d'un pari, ni chez la mère ni chez la fille.

## Ce que valent les +565 € de la fille
- 74 paris : 68 gagnés pour 62,9 attendus par les prix payés, **z +1,66** (59 paris de la fille seule : 53 pour 50,1, z +1,07) ; la mère hors plage : 98,5 pour 98,0 (z +0,14).
- Sans ses 3 meilleurs paris elle fait encore +416 € ; deux jours (21 et 24/10, puis 27/10) font l'essentiel (+117, +207, +170). Choisie parmi ~90 stratégies (z attendu ≈ 2 sans avantage) : rien ne distingue cet écart du hasard.
- Markout des ordres posés servis à la résolution (`ordres_poses`) : fille +0,0117 (59 cas), mère −0,02 (53 cas). Direction juste, taille minuscule.

## Conclusion
Pas de défaut de code. Défaut de lecture : « la fille bat sa mère » compare deux portefeuilles qui ne jouent pas les mêmes paris (argent disponible, meilleur pari du cycle). Le classement n° 1 est un indice faible (z +1,66), à ne pas
promouvoir sur sa seule place. Le principal copie la mère (`nf_sport_patiente`), pas la fille : pas d'effet sur l'argent.

## Correctif et contrôle
`enquete.filles_periode` indique maintenant, quand plus de la moitié des paris d'une fille (au moins 5) n'existent pas dans le journal de sa mère, « dont N paris absents de la mère (rendement à eux seuls) » ; test
`test_daughter_is_compared_with_her_mother_on_the_same_period`.

## Reste ouvert
Rejouer la mère avec l'argent de la fille (`rejeu_cash_25_10.py` comme modèle) pour savoir si c'est l'argent qui manquait : les 14 paris inexpliqués restent à lire dans la table `decisions` d'une base complète.
