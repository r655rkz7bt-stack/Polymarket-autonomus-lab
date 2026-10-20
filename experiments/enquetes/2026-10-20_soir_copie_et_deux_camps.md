# Enquête du 20/10 (passage de 20 h UTC) : copie du principal, deux camps, cotes_bookmakers

Aucun nouveau défaut de code trouvé ; trois vérifications chiffrées (famille n° 3 du jour, « la donnée n'est pas celle qu'on croit », plus la famille 1).

## 1. Le principal copie-t-il la championne, jeton par jeton ?
Journaux publiés, `nf_sport_patiente` : principal 35 achats (33 jetons), fantôme 102 achats (87 jetons).
- Aucun jeton acheté par le principal et absent du fantôme (0 sur 33).
- Mise du principal / mise du fantôme, par jeton : médiane 0,34, de 0,21 à 0,44 (part prévue ≈ un tiers).
  Le 0,21 est Mannarino (exécution partielle déjà connue, contrôle `copie_fidele`) ; le 0,44 est un billet de
  6 € (arrondi à la taille minimale).
- 54 jetons du fantôme (4 063 € de mises) manquent au principal : tous antérieurs à la copie fidèle du 18/10 ou
  au démarrage de la copie (le principal n'a des paris copiés qu'à partir du 19/10 02 h). Pas un défaut.

## 2. Les deux camps d'un match (contrôle `deux_camps`)
11 marchés où un même portefeuille a acheté les deux camps à ≥ 0,70 (principal compris : Safiullin 0,912 puis
Shimabukuro 0,853 le 20/10, −20 € pour la paire). Le contrôle automatique ignore le principal : il ne
voyait donc pas ce cas (le fantôme `nf_sport_patiente` est dans la liste).
Chiffre qui compte : le **deuxième achat** a rapporté +5 € au principal et, sur les 9 paires hors
`market_structure`, +67 € au total (le favori qui s'effondre en jeu a souvent remonté). La perte de la paire est celle du
premier camp, pas du second. Les deux paires `market_structure` (−164 et −128 sur le deuxième camp, 15-16/10) sont des
jambes OUI/NON d'une stratégie de structure de marché, pas le même défaut. Conclusion : **on ne bloque pas** le camp
opposé (cela n'aurait rien épargné sur cet échantillon, 9 paires) ; le contrôle reste à regarder. À refaire à 30 paires.

## 3. cotes_bookmakers : muette depuis 19/10 04 h
Dernier achat le 19/10 04:24, aucun depuis (≈ 40 h). Les 15 achats du 18/10 et les 5 du 19/10 sont tous
antérieurs au correctif « vainqueur seulement » (PR #81, 19/10 11:18) : prix payés 0,03 à 0,66 pour une estimation de 0,23 à
0,86 = des paris de handicap pris pour le vainqueur (déjà chiffré : −287 €). Depuis le correctif, rien : soit le
filtre `moneyline` + écart ≤ 0,25 retire tout (cohérent), soit le rattachement des cotes ne trouve plus rien.
**Non tranché** : la clé The Odds API n'est pas dans cette session et les abstentions ne sont pas publiées. Le contrôle
`muettes` (seuil 48 h) le signalera demain si le silence continue ; vérifier alors les abstentions du cycle.
