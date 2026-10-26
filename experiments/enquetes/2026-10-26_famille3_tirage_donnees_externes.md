# 26/10/2026 — famille 3 à la main (la donnée est-elle celle qu'on croit ?) et `seismes_marche` muette

**Tirage** (`experiments/enquetes/scripts/tirage_famille3_26_10.py`, graine 26) : 12 paris réglés tirés parmi 173 de 10 stratégies à donnée externe (tweets, mots, box-office, séismes, métaux,
CPI, cartes d'e-sport, crypto « dip »), marché relu sur Gamma (`outcomePrices`) : **12 règlements sur 12 conformes au journal.** Relus à la main : 
- `compteur_tweets_non` « Elon Musk 200-219 tweets du 20 au 27/10 » : réglé NON le 25/10 à 3 h, soit **avant** la fin de la période (le compteur avait déjà dépassé la tranche : règlement anticipé UMA, voulu) ;
- `crypto_threshold_prix_bas` « Bitcoin dip to 80 000 le 24/10 » : OUI acheté à 0,18 à 4 h 12 (estimé 0,42), réglé OUI à 14 h 39 (+224 €, le gain de la stratégie à 99 % : déjà signalé « chance » par l'enquête automatique).
Mêmes sources de règlement que celles du libellé (x.com/elonmusk, binance BTC_USDT, hltv.org) : rien d'anormal.

**`seismes_marche` « muette sans raison »** (0 achat, abstentions vides depuis 1,8 jour) : rattachement vérifié à la main sur 63 marchés Gamma de l'étiquette 103038. Les références ne sont pas posées parce que
(1) les ladders de la semaine du 26/10 au 1/11 se calculent seulement dans les 6,6 derniers jours (`WEEK_MAX_DAYS`), il en reste 7,1 ce matin ; (2) le « plus gros séisme du jour » ne se calcule qu'à partir de 6 h UTC
(`FIRST_HOUR`, pas de test sur le passé avant). **Pas un défaut** : elle verra des marchés ce soir (semaine) et à 6 h UTC (jour). Reste le manque de diagnostic (abstentions vides au lieu de « hors plage horaire testée ») :
noté, pas corrigé (le risque de masquer un vrai trou de rattachement l'emporte sur le gain).

**Les « 3 paris font X % du gain »** (obligations `chance`) : `chance_famille2_25_10.py` rejoué : 24 stratégies à gain positif, 16 le restent sans leurs 3 meilleurs paris, 11 sans leur meilleur jour ;
aucun z > 2,4 ; `nf_sport_patiente` +154 € → **+18 € sans ses 3 meilleurs**, −145 € sans son meilleur jour. Même mécanisme que les passages précédents (mises ∝ 1/(1−prix) : peu de paris font le gain).
Exemple vécu cette nuit : `nf_sport_non` affichait +243 € (3e de l'arène) ; à 0 h 51 un NON à 0,933 de 314 € (25 % de son capital, « Académico de Viseu gagne ») a perdu : **−50 € réglés** (journal rejoué : 949,8 contre 1 243).
Le classement du `brief.md` est une photo : un favori à 0,93 ne se juge pas à 50 paris.
