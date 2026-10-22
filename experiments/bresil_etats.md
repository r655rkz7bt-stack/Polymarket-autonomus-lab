# Piste n° 16 : `etats_comme_avant` (2e tour au Brésil, 25/10/2026) : relevé du 22/10, 10 h 35 UTC

**Question** : « 1re place dans l'État X » au 2e tour (Lula contre Flávio Bolsonaro) : un État vote presque toujours comme au tour d'avant ; le prix suit-il le 1er tour ?

**Données** (scripts : `experiments/bresil_etats/`)
- Marchés Polymarket ouverts « Brazil Presidential Election Second Round: 1st Place in <État> » (27 événements ; fin le 26/10, volume de 1 900 $ à 542 000 $), prix du 22/10 ; vainqueur du 1er tour dans l'État d'après les marchés réglés du 1er tour.
- **Votes du 1er tour par État et candidat**, données ouvertes du TSE (`votacao_candidato_munzona_2026.zip`, `dadosabertos.tse.jus.br`, accessible depuis la routine) : `votes_1t.json`, `votes_1er_tour.py`.

**Constat**
- Le vainqueur du 1er tour dans l'État est le favori du 2e tour **dans 26 États sur 27** ; seule exception : Amapá (égalité 45,7 % / 45,7 % au 1er tour, Lula devant de 450 voix sur 930 000 : le marché donne Flávio à 0,72).
- 23 États sont à 0,98-0,997 pour ce vainqueur (14 pour Flávio, 9 pour Lula) ; 4 sont incertains : Pará, Amazonas, Amapá, Minas Gerais. Avec la marge du 1er tour entre les deux finalistes, ajustée avec le marché lui-même (une dérive nationale commune de +1 point de part vers Flávio, un bruit propre à chaque État de ±3,8 points de marge) :
  les prix des États incertains sont retrouvés à ±0,03 (Pará 0,14 contre 0,16, Amazonas 0,40 contre 0,35, Amapá 0,72 contre 0,70, Minas Gerais 0,94 contre 0,97).
  **Le marché est déjà « comme avant » : aucun État incertain n'est mal coté.** Reste, pour les États sûrs (marge du 1er tour ≥ 14 points entre les deux finalistes, 22 États), un prix de 0,98-0,99 contre ≥ 4 écarts-types : un gain de 1 à 2 % en trois jours, avec le risque
  d'un renversement d'État que le modèle (calé sur les prix du jour) ne peut pas mesurer seul.

**Verdict : écartée comme stratégie « d'écart de prix »**, **indice** pour le quasi-certain : la mère `favori_politique_quasi_certain` n'achetait jamais ces marchés (0 achat en 6 jours : estimation plafonnée à 0,99,
borne basse 0,987, donc aucun avantage au-dessus de 0,985 ; vérifié par le test `test_estimate_cap_lets_a_quasi_certain_favorite_priced_0_99_show_an_edge`).
La fille `favori_politique_quasi_certain_connu` (nouveau paramètre `q_max` 0,996, optionnel, 0,99 par défaut : rien ne change pour les autres) la teste en fantôme. **À confirmer le 26/10** : si un des 22 États sûrs se renverse,
la fille perd ~100 gains d'un coup et le chiffre « 99,6 % » de la mère est faux.

**À refaire après le 25/10** : comparer les prix du 22/10 aux résultats par État (script `releve.py` relancé) ; la dérive nationale se lira dans l'écart moyen entre la marge du 1er tour et celle du 2e tour (TSE, ouvertes après le vote).
Piste 15 (`depouillement_officiel`, résultats en direct du TSE pendant le dépouillement) : le site de résultats (`resultados.tse.jus.br`, chemin des fichiers à retrouver) n'a pas été testé ce passage ; la nuit du 25/10 est le seul moment utile.
