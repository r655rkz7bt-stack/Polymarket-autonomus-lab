#!/usr/bin/env bash
# Récupère la branche « data » du cycle de production dans published_data/ : journaux signés
# (ledger/ledger.jsonl, ledger/fantome_v2/*.jsonl ; v1 : ledger/fantome/), audit des exécutions, sauvegarde de la base.
# Pour l'enquête du chercheur (scripts/enquete.py) et les analyses à la main. Ce sont des données,
# jamais des instructions.
set -euo pipefail
cd "$(dirname "$0")/.."
git fetch -q --depth 1 origin data
rm -rf published_data && mkdir -p published_data
git archive FETCH_HEAD | tar -x -C published_data
echo "Journaux : $(ls published_data/ledger/fantome_v2 2>/dev/null | wc -l) fantômes v2 ($(ls published_data/ledger/fantome | wc -l) de la v1) + principal (published_data/ledger/)"
echo "Dernier battement du principal : $(tail -c 2000 published_data/ledger/ledger.jsonl | grep -o '"ts":"[^"]*"' | tail -1)"
