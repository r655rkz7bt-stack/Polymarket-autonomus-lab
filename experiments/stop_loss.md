# Stop-loss « intelligents » : testés sur les 9 879 vrais paris de l'arène (01/11/2026)

Demande d'Etienne (01/11/2026) : « faire comme dans le trading réel, mettre des stop loss, se dire à cette valeur-là je sors,
mais évaluer les stop loss intelligemment ; trouve la meilleure solution, teste ce qui marche le mieux sur le passé ».

## Données
- `stop_loss/scripts/releve.py` : toutes les positions RÉGLÉES des fantômes (journaux signés publiés, 15/10 → 01/11) :
  9 879 positions, 3 932 jetons, 415 452 € misés ; prix payé (frais compris), borne basse de la stratégie, coup d'envoi.
- Historique du CLOB (`prices-history`, pas de 5 minutes) de 24 h avant l'achat jusqu'au règlement.
- `stop_loss/scripts/rejeu.py` : à chaque point de prix, la règle ne regarde que le passé ; si elle se déclenche, vente au
  prix du moment moins un glissement (écart achat-vente + frais : 0,015 ; refait à 0) ; sinon paiement réel au règlement.
  Résultats complets : `stop_loss/resultats_glisse_0015.txt`, `stop_loss/resultats_glisse_0.txt`.

## Le fait qui décide : après une chute, le marché est trop pessimiste
| prix tombé sous le prix payé de | positions | gagnées ensuite | prix du moment | écart |
|---|---|---|---|---|
| 0,05 | 6 512 | 0,642 | 0,618 | **+0,024** (±0,012) |
| 0,10 | 5 208 | 0,587 | 0,558 | **+0,029** (±0,013) |
| 0,20 | 3 577 | 0,488 | 0,464 | **+0,024** (±0,016) |
| 0,30 | 2 758 | 0,401 | 0,378 | **+0,023** (±0,018) |

Un stop-loss ne rapporte que s'il y a de l'inertie (ce qui baisse continue de baisser, Kaminski et Lo). Ici c'est l'inverse :
au moment où le stop vendrait, la position vaut en moyenne 2 à 3 points de PLUS que le prix auquel on la vendrait.

## Résultats (écart au « garder jusqu'au règlement », −8 095 € pour l'arène entière)
| règle (21 essayées) | sorties | écart, vente à −0,015 | écart, vente gratuite | moitiés (−0,015) |
|---|---|---|---|---|
| stop fixe −0,05 / −0,10 / −0,15 / −0,20 / −0,30 | 28-66 % | −10 685 / −10 259 / −7 495 / −4 152 / −5 158 € | −6 018 à −1 755 € | toutes négatives |
| stop relatif −20 % / −35 % / −50 % | 32-48 % | −6 807 / −5 984 / −1 705 € | −3 737 / −3 598 / **+122 €** | négatives |
| sous la borne basse de la stratégie −0,05 / −0,10 / −0,20 | 41-78 % | −11 224 / −11 203 / −7 810 € | | négatives |
| volatilité : −2 / −3 / −4 écarts-types des 24 h d'avant | 47-59 % | −10 568 / −9 234 / −8 427 € | −6 246 à −4 903 € | négatives |
| stop suiveur −0,10 / −0,20 depuis le plus haut | 44-61 % | −10 828 / −6 206 € | −6 658 / −3 386 € | négatives |
| stop −0,10 / −0,20 avant le coup d'envoi seulement | 0,6-1,3 % | −537 / −243 € | −458 / −211 € | +53 puis −590 |
| stop −0,10 / −0,20 pendant le match seulement | 21-29 % | −4 706 / −1 248 € | −2 396 / **+307 €** | −225 puis −1 023 |
| stop −0,10 par tranche de prix payé (5 tranches) | | −16,2 % à −1,8 % par euro | | toutes négatives |

**Verdict : écartés, tous.** Aucune règle ne bat le « garder » une fois le coût de la vente compté ; les deux seules proches
de zéro à vente gratuite (−50 % du prix ; −0,20 en match) redeviennent négatives avec le vrai coût, et l'une perd sur la 2e
moitié. Cela confirme sur 9 879 paris de toutes sortes le test du 20/10 sur le tennis (`achat_echelonne.md` : −5,6 à −7,6 %).

## Ce qu'on en fait
- Rien à changer dans le labo : aucune stratégie active n'a de stop-loss ; les positions sont gardées jusqu'au règlement.
- La vraie protection reste la taille des mises (plafonds de `settings.yaml`, mise mesurée, réserve de liquidités) et la
  règle n°1, pas la sortie anticipée.
- Piste ouverte (l'inverse d'un stop) : racheter après une chute (+2 à +3 points bruts au-dessus du prix). Le coût d'achat
  (écart achat-vente, frais) en mange une bonne partie et « renforcer en baisse » perdait sur le tennis le 20/10 : à tester
  à part, par famille, avant tout fantôme.

Limites : prix du CLOB = prix moyen par pas de 5 minutes (pas la profondeur réelle du carnet) ; positions de fantômes
choisies par nos stratégies (surtout des favoris de sport à 0,80-0,95) ; 17 jours.
