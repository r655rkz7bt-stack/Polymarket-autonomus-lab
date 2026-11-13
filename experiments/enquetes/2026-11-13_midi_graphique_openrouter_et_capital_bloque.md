# Enquête du 13/11/2026 (passage de 11 h) : graphique OpenRouter, parts de marché, principal à l'arrêt, capital bloqué

Jour 13 → famille 2 (faite à 1 h) ; ce passage : familles 3 (la donnée n'est pas celle qu'on croit), 1 et 5. Aucune obligation dans
la feuille de mission. Constats « à regarder » de l'enquête automatique relus : `estimation_perimee` de `taux_tresor_barriere`
(désaccord voulu, élucidé à 1 h), muettes (`lid_agenda`, `suivre_inities` : élucidées), positions néo-zélandaises « après
échéance » (résultats le 27/11), `capital_bloque` (ci-dessous).

## 1. Famille 3 : le graphique OpenRouter n'est pas « jours finis » au sens strict (pas de défaut chiffré)

Constat : la semaine du 9/11 du graphique `model-rankings-chart` valait 134,43 T à 06 h 00 UTC (passage de 6 h) et **141,16 T** de
10 h 53 à 11 h 18 (relevés toutes les 5 minutes, `experiments/openrouter/graphique_en_direct_2026-11-13.txt`), sans nouveau jour
fini dans les vues « jour » (12/11 : 32,63) et « 7 jours » (209,67). Le jeudi n'était donc pas complet à 06 h.
Cause dans le code : `openrouter.projection` suppose que le graphique contient exactement les k jours finis.
Ampleur : **nulle sur la projection** (total = P × semaine précédente / (semaine précédente − 7 jours + P) : 209,75 avec P = 134,43
comme avec 141,16, parce que les deux semaines se ressemblent) ; seules les composantes « fin / début » changent (75,24 / 134,28 →
68,51 / 141,01). Aucun achat touché (5 parts + 5,25 parts à 09 h 17). Pas de correctif ; documenté dans `experiments/openrouter.md`.
Le journal `openrouter:histo` (premier et dernier partiel du jour) mesurera le retard du graphique.

## 2. Famille 3 : l'API « parts de marché » d'OpenRouter n'est pas le graphique du règlement (erreur évitée)

En cherchant une conviction sur « #2 / #3 AI lab by OpenRouter market share week of November 9 » (OpenAI 0,985, Google 0,987),
l'API `rankings/author-market-share` donnait Tencent n° 2 (10,6 %) et Google 8e (3,2 %). Avant d'écrire quoi que ce soit : les 10
semaines réglées (31/08 → 02/11) donnent toutes OpenAI / Google en n° 2-3, que l'API ne reproduit pas (26/10 : Google 9e dans
l'API, réglé 3e). Le graphique du règlement mesure autre chose. **Rien écrit, rien acheté** ; règle notée : un rattachement à une
source se vérifie sur les événements réglés AVANT toute conviction (même leçon que Carbon et GISTEMP).

## 3. Famille 1 : le principal ne joue rien depuis le 07/11

Journal du principal : dernier achat le 07/11 à 15 h 17 ; « le champion ne bat plus « ne rien faire » » le 07/11 à 18 h 21 ;
remise à zéro « Départ du labo v2 » le 12/11 à 13 h 54 ; depuis, 1 000 € disponibles, aucun ordre. Cause : aucune stratégie v2 n'a
les 12 opérations clôturées exigées (`promotion.min_closed_trades`) ; la meilleure (`convictions_claude`, +3,4 %) en a 3 ;
`validated_strategies` est vide (aucun test aux prix payés pour les stratégies v2, qui sont des expériences). Ce n'est pas un défaut
de code : le principal attend une preuve. À surveiller : au rythme actuel (3 à 20 clôtures en 6 jours), la première stratégie
qualifiable arrivera fin novembre.

## 4. Famille 5 : `favori_politique_quasi_certain`, tout le capital dans 23 favoris

0,06 € disponibles, 1 001 € immobilisés dans 23 positions à 0,969-0,983 (achats du 07 au 13/11) : 553 € échus en novembre (dont
les 5 positions néo-zélandaises, résultats le 27/11), 448 € le 30/11-01/12. Plusieurs jambes liées (Hegseth « by 14/11 / 21/11 /
30/11 », trêve Israël-Iran « 15/11 / 18/11 », diesel russe « 15/11 / 30/11 ») achetées avant le correctif `_held_per_event` du 13/11
(1 h), qui ne couvre que 4 classes à échelles. Effet sur la mesure : le fantôme ne teste plus rien jusqu'au 16/11 ; son classement
(1 001 €, +0,1 %) compare un portefeuille plein à des fantômes vides. Comportement voulu d'un Kelly complet sur des favoris à 3 %
de gain (pas de défaut de code) ; le contrôle `capital_bloque` le signale déjà.

## 5. Revente des convictions sur une probabilité périmée (à regarder, pas de défaut)

`convictions_claude` a revendu 63,67 parts du OUI « Danube avant le 15/11 » à 0,97 le 13/11 à 08 h 32 (achat 0,292 : +43 €) parce
que la conviction v4 (0,59, écrite à 01 h) était sous le prix offert ; la prévision OVF de 08 h 44 (93 ± 2 cm le 14/11 à 7 h, 121
le 15/11) rend le passage presque sûr : garder aurait rapporté ≈ 1,3 € de plus. La règle « revendre quand ma probabilité est sous le
prix offert » agit sur la DERNIÈRE probabilité écrite, même périmée : sur un marché qui bouge vite, une conviction non relue peut
faire revendre un gagnant au rabais. Pas de correctif (la revente a ici protégé le Rhin, revendu 0,49 le 12/11 avant sa chute à
0,05) ; méthode : une conviction sur un marché rapide porte une date limite courte et se relit à chaque passage.

## Contrôle automatique

Aucun ajouté : les cas 1 et 5 n'ont aucun effet chiffré, le cas 2 n'a rien produit, le cas 4 est déjà couvert par `capital_bloque`.
