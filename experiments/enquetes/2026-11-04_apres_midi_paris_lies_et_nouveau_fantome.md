# 04/11 (16 h) — famille 5 : paris liés des compteurs de posts, et le nouveau fantôme « rythme long »

**Question** : les fantômes `compteur_*` jouent-ils tous le même pari (donc un seul tirage compté plusieurs fois) et le principal
y est-il exposé ? Le fantôme `compteur_truth_rythme_long_audace` (créé à 11 h) estime-t-il bien plus bas que sa mère ?

**Relevé** (journaux signés publiés, positions non réglées de 21 fantômes `compteur_t*`) :
- Événement Trump « posts du 6 au 13/11 » (1305849, marché « 200+ » 6625358) : 7 fantômes ont acheté le même jeton « Oui » (606 € investis au total).
  À 12 h 22, `compteur_tweets_12_18h` l'a pris à 0,602 sur une estimation de 0,968 ; `compteur_truth_rythme_long_audace` le même jeton, même prix,
  mais sur une estimation de **0,814** (mère : 0,968 ; dispersion 6 : 0,949). Le correctif est donc bien là, et le fantôme achète quand même parce que 0,81 > 0,60.
- Événement Trump « 25-31/10 ou 1-7/11 » (1286700) : 21 lignes de fantômes, 1 494 € de coût cumulé sur 3 marchés.
- Événement Maison-Blanche (1263843) : 477 € ; (1263838) : 450 €.
- Principal : 20,4 € sur 1286700 (3 % du capital), 28,3 € sur 1263843 ; rien sur 1305849 au-delà de 4 €. Pas de surexposition.

**Cause** : pas un défaut de code, la conséquence du modèle commun (une seule formule, sept habillages). Les 7 fantômes comptent comme
**un** pari lié pour le jugement (`enquete._z_by_event` le fait déjà).

**Conclusion** : aucun défaut. Le règlement de 1305849 (13/11) donne une observation de plus pour comparer les trois formules sur la même période.
Rien à corriger, pas de nouveau contrôle (le contrôle `selection_multiple` compte déjà par événement).
