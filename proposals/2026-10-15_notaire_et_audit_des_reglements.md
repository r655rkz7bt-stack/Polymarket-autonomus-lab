# Proposition — le notaire : seule une machine protégée signe le journal (lot D)

> **Décision d'Etienne (15/10/2026) : option A.** La partie 1 (audit des règlements) est faite :
> `scripts/audit_fills.py` et `tests/test_audit_fills.py` (protégés). Essai sur les 10 vrais
> règlements du journal de production (principal et fantômes) : 10 conformes à la résolution
> officielle. La partie 2 (le notaire) n'est pas faite ; elle reste décrite ci-dessous si Etienne
> veut y revenir.

Date : 15/10/2026. Faisait partie de « Tu peux tout faire sauf le 3 ». **Rien n'est encore codé** :
ce changement touche le cœur du noyau protégé (`ledger.py`, le fichier qui signe le journal).
Pendant la session, le contrôle de sécurité de Claude a bloqué cette modification, et c'est
normal : seul Etienne peut décider de changer la façon dont le journal est signé. Ce document
explique le problème, la solution et ce qu'elle coûte. Etienne choisit ensuite.

## Le problème (ce qui est vrai aujourd'hui)

Le job `cycle` fait tourner du code **libre**, que le chercheur peut modifier : `main.py`, les
stratégies… Ce même job reçoit `LEDGER_KEY`, la clé qui signe le journal. Du code libre peut donc
écrire **n'importe quelle écriture signée**. Exemples :
- un achat à un prix qui n'a jamais existé. Le job `audit` le **repère** après coup et envoie un
  e-mail, mais l'écriture reste signée ;
- un **règlement** inventé, où un marché perdu est « payé » 1 par part. Aujourd'hui, **aucun
  contrôle** ne le voit : l'audit ne vérifie que les achats et les ventes.

Ce n'est pas une attaque probable : le chercheur suit CLAUDE.md. Mais une erreur de code peut
produire le même effet. La règle n°1 et la simulation honnête reposent donc sur la bonne
conduite du code libre, pas sur une garantie.

## La solution proposée, en deux parties

### Partie 1 — audit des règlements (petite, sans risque)

Dans `scripts/audit_fills.py` (protégé), chaque règlement (`SETTLE`) est vérifié comme les
achats et les ventes : on lit le marché sur l'API publique Gamma (`/markets/{id}`). Le marché
doit être **résolu**, et le paiement inscrit doit être **égal** au prix final officiel de
l'issue détenue (1, 0, ou 0,5 en cas d'égalité). Sinon : anomalie, inscrite dans
`audit/etat.json` et signalée par e-mail. Le marché d'un jeton se retrouve grâce à l'achat
correspondant dans le même journal.

Coût : environ 40 lignes et leurs tests ; un appel à Gamma par règlement. Cette partie peut être
faite seule, sans la partie 2.

### Partie 2 — le notaire (grosse, change la signature du journal)

1. **Le cycle ne reçoit plus `LEDGER_KEY`.** Il ouvre le journal en *brouillon* : la chaîne de
   hash et la comptabilité sont vérifiées comme aujourd'hui (`apply_entry`, règle n°1
   comprise), mais ses nouvelles écritures sont inscrites **sans signature**.
2. **Un nouveau job protégé, le « notaire »**, remplace le job `audit`. Il tourne sur une machine
   neuve, avec `python -I -S`, sans aucun code libre, et lui seul a la clé. Pour chaque écriture
   non signée, il :
   - rejoue les règles comptables (solde, parts, frais ≥ 0, faillite à 0 €) ;
   - refuse une date qui recule ou qui est dans le futur ;
   - refuse tout `RESET` ou `GENESIS` non signé (sauf le `GENESIS` d'un **nouveau fantôme**, et
     seulement avec le capital de `risk_limits.yaml`) ;
   - vérifie le prix d'un achat ou d'une vente contre l'historique public, comme l'audit actuel ;
   - vérifie un règlement contre la résolution officielle (partie 1) ;
   - **signe** l'écriture si tout est juste. Si un prix n'est pas encore publié (moins de
     10 min) ou si une API ne répond pas, l'écriture attend le passage suivant.
3. **Une écriture refusée** est retirée du journal, **avec toutes celles qui la suivent** (elles
   reposaient sur un état faux). Le refus est inscrit dans `ledger/notaire.json` et
   `audit/etat.json`, et un e-mail part. L'historique de la branche `data` garde la trace de tout.
4. **Une écriture signée suivie d'une écriture non signée** est normale. L'inverse est une
   corruption : le journal est arrêté.
5. Le verrou de faillite écrit par le cycle est d'abord non signé ; le notaire le signe. Sans clé,
   la simple présence d'un verrou suffit à arrêter le trading : dans le doute, on s'arrête.

**Résultat** : le code libre ne peut plus rendre une écriture définitive sans contrôle.
`LEDGER_KEY` n'est plus jamais présente là où tourne du code modifiable par l'IA.

### Ce que ça change ailleurs

| Fichier | Changement | Protégé ? |
|---|---|---|
| `ledger.py` | mode brouillon (`key=None`), `Ledger.open(..., pending=)`, fonction `notarize` | oui |
| `tests/test_ledger.py` | brouillon, notaire (signature, refus, attente, faux `RESET`, verrou) | oui |
| `scripts/notaire.py`, `tests/test_notaire.py` | nouveaux | à ajouter à `PROTECTED_PATHS.txt` |
| `scripts/audit_fills.py` | règlements ; s'arrête aux écritures non signées | oui |
| `.github/workflows/cycle.yml` | plus de `LEDGER_KEY` dans le cycle ni dans les rapports ; job `notaire` à la place d'`audit` | oui |
| `scripts/reset_capital.py` | retire les écritures non signées avant le `RESET` | oui |
| `main.py`, `scripts/_common.py`, tableau de bord, rapports | ouvrent le journal sans clé ; affichent « N écritures en attente de signature » ; l'ancrage anti-troncature accepte un refus inscrit par le notaire | libres |

### Les limites (à connaître)

- Le notaire ne peut pas revoir la **profondeur** du carnet au moment exact de l'ordre. Il vérifie
  que le prix a existé (±0,05), pas que la quantité était disponible. Le simulateur protégé reste
  le garant de la quantité, mais c'est le code libre qui l'appelle.
- Il ne recalcule pas les frais exacts (barème par marché) ; il vérifie seulement qu'ils ne sont
  pas négatifs. On peut l'ajouter plus tard.
- Le journal aura toujours une « queue » de 1 à 3 cycles pas encore signés, le temps que
  l'historique des prix soit publié. Le tableau de bord la montrera.
- `scripts/initialize.py` est libre mais tourne avec la clé, dans le workflow protégé
  `initialize.yml`. Ce workflow ne sert qu'une fois, à la création. À fermer aussi : le rendre
  protégé, ou refuser de tourner si le journal existe déjà.

### Risques et façon de faire

C'est le plus gros changement du noyau depuis le début : tout le journal passe par ce chemin. Une
erreur arrêterait le trading, au pire pendant quelques heures. Les données ne seraient pas en
danger : l'historique de `data` est conservé et le ruleset interdit les réécritures. Étapes
prévues :
1. coder et tester en local, avec un essai complet : cycle sans clé, puis notaire, puis cycle,
   sur une copie du vrai journal ;
2. une PR noyau, à fusionner par Etienne comme les précédentes (désactiver `protection-main`,
   fusionner, réactiver) ;
3. surveiller les premiers cycles : écritures signées, aucune en attente depuis plus de 30 min.

## Ce qu'Etienne doit décider

- **A. Partie 1 seule** (audit des règlements) : rapide, sans risque. Recommandé dans tous les cas.
- **B. Parties 1 et 2** : la vraie garantie. Il faudra autoriser Claude, dans la conversation, à
  modifier `ledger.py` pour ce chantier précis, puis fusionner la PR noyau.
- **C. Rien pour l'instant.**
