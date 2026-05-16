"""Monetary Policy Sentiment Index (MPSI) scoring utilities."""

from __future__ import annotations

import re
from typing import Dict, List

_HAWKISH_WEIGHTS = {
    "inflation": 2,
    "tightening": 2,
    "restrictive": 2,
    "elevated": 1,
    "strong": 1,
    "increase": 1,
    "higher": 1,
}

_DOVISH_WEIGHTS = {
    "accommodative": -2,
    "easing": -2,
    "cut": -2,
    "weaker": -1,
    "decline": -1,
    "lower": -1,
    "softening": -1,
}

_BASELINE_SCORE = 50.0
_SCALE_FACTOR = 25.0


def score_statement(statement: str) -> Dict[str, object]:
    """Score an FOMC statement and return normalized sentiment details.

    Returns a dictionary with:
    - raw_score: weighted score from matched lexicon terms
    - normalized_score: score on a 0-100 scale
    - label: dovish / neutral / hawkish
    - matched_terms: list of matched terms used in scoring
    """

    if not isinstance(statement, str):
        raise TypeError("statement must be a string")

    tokens = re.findall(r"[a-z]+(?:'[a-z]+)?", statement.lower())
    matched_terms: List[str] = []
    raw_score = 0

    for token in tokens:
        if token in _HAWKISH_WEIGHTS:
            raw_score += _HAWKISH_WEIGHTS[token]
            matched_terms.append(token)
        elif token in _DOVISH_WEIGHTS:
            raw_score += _DOVISH_WEIGHTS[token]
            matched_terms.append(token)

    if not matched_terms:
        normalized_score = _BASELINE_SCORE
    else:
        # `matched_terms` is guaranteed non-empty in this branch.
        avg_weight = raw_score / len(matched_terms)
        normalized_score = max(
            0.0, min(100.0, _BASELINE_SCORE + (avg_weight * _SCALE_FACTOR))
        )

    if normalized_score > 55:
        label = "hawkish"
    elif normalized_score < 45:
        label = "dovish"
    else:
        label = "neutral"

    return {
        "raw_score": raw_score,
        # Keep a stable, human-readable score precision for reporting.
        "normalized_score": round(normalized_score, 2),
        "label": label,
        "matched_terms": matched_terms,
    }
