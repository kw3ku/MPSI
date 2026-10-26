#!/usr/bin/env bash
# Rebuild the MPSI scores from the corpus and reproduce the Fed Funds validation.
#   bash replication/run_all.sh            # keyword half only (fast, no torch)
#   bash replication/run_all.sh --full     # also rebuild FinBERT scores (~440 MB download)
set -euo pipefail
cd "$(dirname "$0")/.."

python replication/paper_v1.py --keywords-only
if [[ "${1:-}" == "--full" ]]; then
    python replication/paper_v1.py
fi
python replication/verify_scores.py
python replication/ffr_validation.py
python -m pytest -q tests
