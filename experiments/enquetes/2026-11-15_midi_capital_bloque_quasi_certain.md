# 15/11/2026 (passage de 11 h) : `favori_politique_quasi_certain` sans argent — capital bloqué et idée mal décrite

Jour 15 → famille 4 (faite à 1 h) ; ici familles 5 et 3 sur le constat `capital_bloque` de l'enquête automatique, le seul
constat « à regarder » nouveau du jour (les autres sont déjà menés au bout : `estimation_perimee` de `taux_tresor_barriere`
le 13/11, `filles_periode` le 14/11, `positions_oubliees` = Nouvelle-Zélande, `audit` = fausses alertes connues).
Aucune obligation dans la feuille de mission.

## Constat
`favori_politique_quasi_certain_v2.0.0` : 48 € disponibles sur 1 005 €, 23 positions ouvertes (954 € misés, 27 achats depuis
le 07/11). Relu sur Gamma le 15/11 vers 11 h UTC (23 marchés, `/markets/<id>`) :
- valeur au milieu du carnet 959,5 € pour 954,4 € payés (+5,1 € latents) ; horizon moyen pondéré par la mise **14,1 jours** ;
- six positions se règlent le 16/11 (≈ 350 €), le reste fin novembre ; aucune n'est « oubliée » à tort (les 5 « 174 h après
  l'échéance » sont l'élection néo-zélandaise, résultats officiels le 27/11, déjà expliqué le 15/11 à 1 h) ;
- **paris liés** : 6 événements portent 2 ou 3 marchés (Israël-Iran « trêve jusqu'au 15/11 » et « jusqu'au 18/11 », gazole russe
  « d'ici le 15/11 » et « d'ici le 30/11 », Hegseth « d'ici le 21/11 » et « le 30/11 », 4 jambes néo-zélandaises) : ils gagnent ou
  perdent ensemble ; l'arène les compte comme indépendants (le z par événement de `enquete._z_by_event` les regroupe déjà) ;
- **famille 3, la donnée n'est pas celle qu'on croit** : le commentaire de la stratégie dit « presque acquis, souvent un résultat
  connu en attente de règlement ». Sur les 27 achats, **5 seulement** (Nouvelle-Zélande, après le soir de l'élection) sont un
  résultat connu ; 765 € sur 1 082 € misés portent sur des événements À VENIR à plus de 7 jours (trêves, démissions, détroits,
  « Broad Front 6-8 sièges » de l'élection espagnole du 29/11 acheté NON à 0,971, aujourd'hui OUI 0,17-0,35).

## Cause
Pas de défaut de code : `naive_favorite` fait ce que disent ses réglages (0,97-0,995, horizon jusqu'à 720 h, demi-Kelly,
3 achats par cycle) ; en 3 jours, l'argent est entièrement placé à 14 jours. Le champ `horizon_hours` ne distingue pas un
résultat connu (Nouvelle-Zélande : 0,1 à 0,3 jour, date de fin Gamma provisoire) d'un pari à 23 jours.

## Ampleur
Aucun euro faux. La comparaison de l'arène reste juste (rendement par mise) mais ce fantôme ne teste plus rien jusqu'au 16/11.
Gain attendu au prix : ≈ +2,5 % en 14 jours, une seule perte (≈ 90 €) l'efface ; l'élection espagnole montre que « 0,97 »
à 3 semaines n'est pas « acquis ».

## Correctif
Explication et commentaire de `config/strategies.yaml` rendus exacts (ce que la stratégie achète vraiment), sans changer
ses réglages : un frein se prouve par un rejeu (`docs/METHODE.md`), et 4 opérations closes ne prouvent rien. Pas de nouveau
contrôle : `capital_bloque`, `positions_oubliees` et `_z_by_event` l'ont vu.

## Vérifié sans défaut
Rattachements des 23 positions relus (question, côté, prix payé 0,969-0,985 dans la plage 0,97-0,995 à un dixième de centime
près) ; règlements à venir datés ; aucune position au-delà de 720 h.
