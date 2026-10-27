"""Familles « à initiés » reconnues au titre de l'événement (relu à la main sur des échantillons, 27/10/2026).
Ne sont PAS des familles à initiés : ce qui se lit en direct (vues de vidéos, classement de l'App Store du jour, nombre de
tweets), les votes (primaires), les paroles en direct (« What will X say »)."""

from __future__ import annotations

import re

FAMILLES = {
    "prix": re.compile(
        r"ballon d.or|nobel (peace|prize|literature|physics|chemistry|economics|medicine)|nobel prize|person of the year|"
        r"oscars|academy awards?|\bbest (picture|actor|actress|director|supporting|original|adapted|international|animated)|"
        r"grammys?|emmys?|golden globes?|bafta|tony awards?|palme d.or|cannes|golden boy|kopa|the best fifa|laureus|"
        r"booker prize|pulitzer|game awards|game of the year|\bmvp\b|cy young|heisman|rookie of the year|coach of the year|"
        r"player of the year|hart trophy|vezina|calder|norris trophy|time 100|word of the year|pantone|michelin|razzies?|"
        r"golden raspberry award|miss universe|mr\. olympia", re.I),
    "donnees_entreprise": re.compile(
        r"searched .*on google|year in search|#\d+ searched|spotify|wrapped|billboard|most streamed|halftime show|"
        r"eurovision|apple event|iphone \d+|release date", re.I),
    "emission": re.compile(
        r"survivor|bachelor(ette)?\b|love island|big brother|the traitors|masked singer|dancing with the stars|the voice|"
        r"american idol|top chef|drag race|beast games", re.I),
    "decision": re.compile(
        r"\bdraft\b.*(pick|overall|drafted|first)|first (overall )?pick|no\. ?1 pick|\bnew pope\b|\bnext pope\b|\bpope\b.*(elected|name)|"
        r"conclave|running mate|fed chair|who will trump nominate|nominate[sd]? .*(supreme court|fed|secretary|ambassador)|"
        r"\bpardon|host city|olympics host|world cup host", re.I),
}
EXCLURE = re.compile(r"what will .* say|\bsay\b.*during|announcers|# of views|views of|app store|primary winner|"
                     r"\bvs\.? |tweets?\b|posts?\b|mention", re.I)


def famille(titre: str) -> str | None:
    if EXCLURE.search(titre or ""):
        return None
    return next((nom for nom, motif in FAMILLES.items() if motif.search(titre or "")), None)
