# Totaux de sport, refaits sur le relevé COMPLET (27/10/2026)

**Pourquoi** : `totaux_sports.md` (26/10) concluait « écartée » (« Over » à 12 h : +10,1 % sur la découverte d'août-octobre puis −0,9 % hors échantillon de février à août). Cette contre-épreuve reposait sur un relevé
**tronqué** (Gamma refuse `offset` au-delà de ≈ 2 100 : `enquetes/2026-10-27_releves_tronques_offset.md`) : il manquait MLB, tennis, CS2, Valorant, NFL de la fenêtre février-août et le tennis d'avant le 14/09.
Relevé refait par curseur (`totaux_sports/scripts/releve_complet.py`) : 83 129 événements des 37 ligues depuis le 15/01/2026 ; vrais échanges (data-api) de 72 673 marchés de totaux (> 1 000 $, ou > 50 $ pour « Total Sets O/U 2.5 »
du tennis) : `releve_echanges_complet.py`. Même méthode que `analyse.py` (ligne principale, premier échange preneur dans les 30 minutes après la décision, frais du marché, 50-50 comptés 0,5) : `analyse_complet.py`.

## Résultats (un pari par événement, type, délai, côté)
| fenêtre | événements avec échanges | délai | « Over » | « Under » |
|---|---|---|---|---|
| février-août (hors échantillon) | 18 646 (avant : 5 879) | 1 h | −2,8 % (6 633 paris, t −1,88) | −1,2 % |
| | | 3 h | −3,0 % (3 846, t −1,74, z des prix −2,20) | −0,6 % |
| | | 6 h | −1,1 % (2 626) | −3,3 % (t −1,57) |
| | | **12 h** | **−1,3 % (1 461 paris, t −0,44)** (avant : −0,9 %, 906) | −0,3 % |
| | | 24 h | −1,9 % (386) | −7,1 % |
| août-octobre (découverte) | 6 237 (avant : 4 614) | 1 h | +1,0 % (3 065) | −6,7 % (t −3,71) |
| | | 3 h | +1,5 % (1 247) | −4,6 % |
| | | **12 h** | **+11,7 % (364 paris, t +2,03, z des prix +2,12)** (avant : +10,1 %, 312) | −13,5 % (t −2,59) |
| | | 24 h | +18,7 % (128, t +1,80) | −23,8 % |

→ **La découverte se retrouve (+11,7 % à 12 h) et la contre-épreuve aussi (−1,3 %), avec 1,6 fois plus de paris : « Over » écartée, verdict inchangé.** Le défaut des relevés n'a pas retourné la conclusion de ce jour-là.

## Le football d'août-octobre : une saison, pas une loi
Les « Over » des totaux de football gagnent plus que leur prix **depuis le 15/08/2026** (3 h : +10,5 %, 448 paris, t +1,93, z des prix +2,77 ; 12 h : +17,8 %, 130 paris) mais pas de février à août (3 h : −0,8 %, 1 121 paris, t −0,21).
Contre-épreuve sur le début de la saison PRÉCÉDENTE (1er août → 30 novembre 2025, 17 ligues, 486 événements avec échanges, `releve_saison_2025.py`) : **« Over » à 3 h −18,1 % (117 paris, t −2,01)**, 1 h +1,0 % (219), 6 h +5,6 % (68) : le signe s'inverse, rien de répété. **Écartée**.
(Basket / baseball / football américain / hockey : −6 à +3 %, rien.)

## Toutes les lignes, par tranche de prix (`analyse_lignes.py` : 38 083 paris, 3 h et 12 h)
Biais favori / outsider des marchés de totaux : de 0,03 à 0,97, **les tranches de plus de 200 paris sont toutes entre −4,3 % et +6,5 %** (seules les tranches 0,03-0,15, moins de 350 paris, sortent : −19,0 % en août-octobre à 3 h, +13,6 % en février-août à 12 h, |t| < 0,6) ; février-août, les tranches 0,45-0,55 et 0,70-0,85 perdent 1,9 % et 2,9 % à 3 h (frais et écart) ; août-octobre 0,15-0,45 à 3 h +2,7 à +6,5 % (z des prix +1,4 / +1,8). Aucun effet qui tienne sur les deux fenêtres : le marché des totaux est calibré aux frais près.

## Tennis, « Total Sets O/U 2.5 » (Under = le match se joue en 2 sets) : écartée
Marché ignoré jusqu'ici (les issues s'appellent « Over 2.5 / Under 2.5 », l'ancienne analyse exigeait « Over / Under »). 8 018 marchés réglés (> 50 $), mais très peu d'échanges dans la fenêtre de décision : 229 paris à 1 h, 101 à 3 h, 48 à 6 h (février-octobre).
« Under » **−8,3 % à 1 h (z des prix −4,35)**, −6,0 % à 3 h, −16,8 % à 6 h : le marché SURÉVALUE les matchs en deux sets (l'inverse d'e-sport) ; « Over » +9,1 % (t +1,09), −4,2 %, +29,9 % (48 paris, t +1,76) : du bruit. Six règlements sur cent sont à 50-50 (abandon). Rien à jouer.

## E-sport : la confirmation de `moins_de_cartes_lol`, sur l'échantillon complet
Totaux de cartes, ligne principale, 3 h, février-août : LoL « Under » **+13,8 % (179 paris, t +1,91, z des prix +2,36)**, « Over » −26,2 % (t −3,29) ; août-octobre +4,8 % (70 paris) ; CS2 « Under » +1,9 % (141) puis −5,9 % (44), Dota 2 +31,5 % (10), Valorant −6,6 % (15).
Même image que le 25/10 : l'indice vit dans LoL seul (la fille `moins_de_cartes_lol`), CS2 n'a rien.

## Ce qui reste vrai / ce qui change
- Totaux de sport : **écartée**, désormais sur 18 646 + 6 237 événements. Aucune stratégie, aucun fantôme.
- Les relevés par `offset` d'avant le 27/10 sont à relire avec méfiance sur la taille d'échantillon, pas sur le signe (liste dans la fiche d'enquête).
- Les vainqueurs de match ont été refaits dans la foulée sur 30 000 marchés tirés au hasard : `favoris_avant_match.md` (écartée aussi).

## Reproduire
```
python experiments/totaux_sports/scripts/releve_complet.py                      # 3 min, donnees/totaux_complet.jsonl
for i in 0 1 2 3; do PART=$i NB=4 python experiments/totaux_sports/scripts/releve_echanges_complet.py & done   # ≈ 25 min
PERIODE=avant python experiments/totaux_sports/scripts/analyse_complet.py ; PERIODE=decouverte python ...analyse_complet.py
python experiments/totaux_sports/scripts/analyse_lignes.py
python experiments/totaux_sports/scripts/releve_saison_2025.py && TOTAUX=totaux_2025.jsonl ECH=echanges_2025.jsonl SORTIE=2025 PERIODE=tout python experiments/totaux_sports/scripts/analyse_complet.py
```
Résultats complets : `totaux_sports/resultats_complet_avant.txt`, `..._decouverte.txt`, `..._lignes.txt`, `resultats_saison_2025.txt`.
