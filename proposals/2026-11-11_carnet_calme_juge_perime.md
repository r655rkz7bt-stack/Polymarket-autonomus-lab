# Proposition : un carnet CALME n'est pas un carnet PÉRIMÉ (11/11/2026, chercheur de 6 h)

**Pour Etienne, en simple.** Avant chaque achat simulé, le labo relit le carnet d'ordres du marché et le contrôleur de sécurité
(noyau protégé) refuse l'achat si ce carnet a « plus de 120 secondes ». Le problème : pour l'âge du carnet, `main.py` prend l'heure
que Polymarket écrit dans le carnet, qui est l'heure de sa **dernière modification**, pas l'heure où on l'a lu. Sur un petit marché
où personne n'a bougé ses ordres depuis une heure, le carnet que l'on vient de lire est pourtant le carnet d'aujourd'hui : un
acheteur réel serait servi à ces prix. Le labo le traite comme « vieux de 1 heure » et refuse l'achat.

**Constat (cycle local du 11/11 à 06 h 14 UTC).** Nouvelle stratégie `seismes_pays` : 1 proposition (NON d'un marché « séisme ≥ 6
aux États-Unis en novembre »), refusée « carnet périmé (24 996 s > 120 s) » juste après la relecture. Carnet relu à 06 h 14 :
horodatage Polymarket 05 h 10 (dernier changement) ; le carnet du marché séismes de la semaine, lui, avait changé 20 s plus tôt.
Toute stratégie qui vise des marchés minces et calmes (pays, lids, mots, tranches peu suivies) est donc presque sourde, sans que
ses abstentions le disent (« rejet après relecture » n'apparaît que dans le journal du cycle).

**Ce qui est en jeu.** Le code fautif n'est pas protégé (`main.py`, ligne `book_time=min(book.timestamp, book.fetched_at)`), mais
il alimente directement le contrôle « on n'achète pas à un prix passé » du contrôleur (noyau). Le changer seul reviendrait à
assouplir une règle du jeu sans ton accord : je ne l'ai pas fait.

**Proposition.** Pour la RELECTURE faite juste avant l'exécution seulement (`_reread_book`), prendre comme âge du carnet l'heure de
lecture (`fetched_at`) quand la lecture a moins de 120 s. Le carnet du début de cycle garde la règle actuelle. Le contrôle continue
de bloquer un carnet qu'on n'a pas pu relire, ou relu trop tôt. Test à écrire : carnet relu à l'instant, horodatage Polymarket
d'il y a 1 h → accepté ; carnet relu il y a 10 min → refusé.

**Risque.** Si Polymarket servait un carnet en cache (vieux mais présenté comme actuel), on achèterait à un prix passé. Je n'ai vu
aucun cas : l'horodatage avance bien dès qu'un ordre change (marché de la semaine : 20 s).

**Ta décision** : oui / non. Rien d'autre à faire de ton côté ; si oui, dis-le dans une conversation et le chercheur fera le
changement avec son test.

**Nouveau cas (12/11/2026, 21 h UTC).** La conviction `dette-us-41000-avant-2027` (NON à 0,54 pour une chance de 0,70, 4 % du
fantôme, `experiments/dette_us.md`) est refusée à chaque cycle local : « carnet périmé (1 369 s > 120 s) », puis « 6 125 s ». Ce
marché n'a presque aucun échange : son carnet ne bouge pas pendant des heures, donc ce genre de conviction (là où une recherche vaut
le plus) ne peut jamais être jouée tant que la règle reste telle quelle. Même cycle : 3 autres refus « carnet périmé » (248 à 511 s)
sur des marchés minces d'autres fantômes.
