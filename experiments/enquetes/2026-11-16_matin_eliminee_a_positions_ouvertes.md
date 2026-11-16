# 16/11/2026 (passage de 6 h) — Une éliminée « à remplacer » aurait gelé ses positions ; positions néo-zélandaises

Famille du jour : 16 mod 6 + 1 = 5 (faite au passage de 1 h) ; ici familles 6 (« ce qui ne tourne plus ») et 3.

## 1. Obligation « Remplacer les stratégies éliminées encore configurées : compteur_tweets_v2.0.0 »

**Constat.** L'élimination hebdomadaire (16/11, 01 h UTC, « pire croissance de l'arène », −9,5 %, 37 opérations) a
retiré `compteur_tweets_v2.0.0`. Note : `seismes_marche` (−15,6 %) est plus bas au classement mais n'a que 3 opérations
clôturées, sous `min_closed_trades` (12) : elle n'était pas éligible — conforme à `arena.choose_elimination`.
La feuille de mission demande alors de « remplacer » la stratégie, c'est-à-dire de la sortir de la configuration.

**Défaut.** `main._open_shadows` ne charge que les stratégies `enabled` ; une stratégie éteinte n'a plus de portefeuille
dans le cycle, donc ses positions ne sont plus jamais réglées (une éliminée encore configurée, elle, ne trade plus —
`portfolio.strategies = []` — mais ses positions se règlent). `compteur_tweets_v2.0.0` a **20 positions ouvertes**
(semaines de Truth Social et de Musk, achats du 08 au 15/11). Obéir à l'obligation les aurait gelées : capital réalisé
figé, aucun règlement, mesure perdue. Même effet déjà vu le 22/10 (105 positions non réglées sur 121 appartenaient à des
fantômes éteints, `2026-10-22_apres_midi_copie_et_positions.md`) sans que la cause (l'obligation) ait été nommée.

**Cause.** `brief.build_brief` : `replace = [n for n in state.eliminated if n in active]`, sans regarder les positions.

**Correctif.** L'obligation n'apparaît qu'une fois toutes les positions de l'éliminée réglées ; d'ici là, la feuille de
mission l'affiche à part (« Éliminées gardées configurées jusqu'au règlement de leurs positions »), champ
`eliminees_en_reglement`. Commentaire dans `config/strategies.yaml` (`compteur_tweets` reste `enabled: true`).
**Test** : `tests/test_arena.py::test_brief_keeps_eliminated_strategy_with_open_positions` (cas réel ; échoue avec
l'ancien code, passe avec le nouveau). Pas de contrôle à ajouter dans `enquete.py` : c'est la feuille de mission elle-même.

**Ampleur.** 0 € perdu (l'obligation n'avait pas encore été suivie) ; 20 positions protégées.

## 2. Constat « à regarder » `positions_oubliees` : 5 positions de `favori_politique_quasi_certain` en retard de 193 h

Les 5 marchés relus sur Gamma (`/markets/<id>`) : tous de l'élection néo-zélandaise du 07/11 (« Labour 2e », « National
le plus de sièges », « Labour vote populaire »…), `closed: false`, `endDate` 08/11 04 h 59 (placeholder) ; résultats
officiels le 27/11. **Aucun défaut** : attente du règlement officiel. Ces positions sont en ligne avec les résultats
préliminaires (relus, `experiments/comptage_tardif.md`) : National 42 sièges, Labour devant au vote de parti.

## 3. Famille 3 (« la donnée n'est pas celle qu'on croit »)

En relisant les sources de l'élection : l'infobox de Wikipédia inverse les voix de National et de Labour (710 330 /
706 680) par rapport à trois autres sources (Latin Times, Saudi Gazette, résumé AP). Une stratégie qui lirait
Wikipédia se serait trompée de signe. Leçon pour toute source de résultats : deux sources indépendantes avant d'agir.
