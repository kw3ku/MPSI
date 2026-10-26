"""
Tests for the frozen paper scorer and the published scores. No torch needed.

    pytest tests/
"""

import hashlib
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'replication'))

import paper_v1  # noqa: E402
from ffr_validation import correlate, handcoded, monthly_mpsi  # noqa: E402

PUBLISHED = ROOT / 'data' / 'processed' / 'mpsi_hybrid_scores.csv'
CORPUS = ROOT / 'replication' / 'corpus'


@pytest.fixture(scope='module')
def detector():
    return paper_v1.PolicyKeywordDetector()


@pytest.fixture(scope='module')
def published():
    return pd.read_csv(PUBLISHED)


def test_keyword_formula(detector):
    # Substring matching: 'tightening' also hits 'tighten', 'inflation risks' also hits
    # 'inflation risk' -> 4 hawkish, 1 neutral -> 100 * (4 - 0) / 5
    text = "The Committee is tightening policy. Inflation risks remain. We will monitor."
    c = detector.count_keywords(text)
    assert (c['hawkish'], c['dovish'], c['neutral']) == (4, 0, 1)
    assert detector.calculate_keyword_mpsi(text) == 80.0


def test_known_limitation_ease_substring(detector):
    # Documented in REPLICATION.md: dovish 'ease' matches inside 'increase'.
    # Pinned so a change to the frozen paper scorer is caught.
    assert detector.count_keywords("prices increase")['dovish'] == 1


def test_keyword_score_is_zero_without_keywords(detector):
    assert detector.calculate_keyword_mpsi("Nothing relevant here.") == 0


def test_repetition_does_not_change_score(detector):
    once = "rate cut"
    assert detector.calculate_keyword_mpsi(once) == detector.calculate_keyword_mpsi(once * 5)


def test_published_hybrid_identity(published):
    no_kw = published[['hawkish_kw_count', 'dovish_kw_count', 'neutral_kw_count']].sum(axis=1) == 0
    implied = (0.70 * published.mpsi_keywords + 0.30 * published.mpsi_finbert).where(~no_kw, published.mpsi_finbert)
    assert ((implied - published.mpsi_hybrid).abs() <= 0.011).all()


def test_corpus_matches_manifest():
    m = pd.read_csv(CORPUS / 'MANIFEST.csv', keep_default_na=False)
    assert len(m) == 119
    for _, r in m[m.included == 'yes'].iterrows():
        assert hashlib.sha256((CORPUS / 'us_fed' / r.path).read_bytes()).hexdigest() == r.sha256, r.path


def test_keyword_columns_reproduce(published):
    rebuilt = paper_v1.score_keywords_only(CORPUS / 'us_fed')
    j = published.merge(rebuilt, on=['doc_type', 'filename'], suffixes=('', '_r'))
    assert len(j) == 118  # one document is not redistributed
    for col in ['hawkish_kw_count', 'dovish_kw_count', 'neutral_kw_count', 'word_count', 'mpsi_keywords']:
        assert (j[col] == j[col + '_r']).all(), col


def test_paper_ffr_correlation(published):
    res = correlate(monthly_mpsi(PUBLISHED),
                    handcoded(ROOT / 'replication' / 'data' / 'fed_funds_paper_handcoded.csv'),
                    'paper')
    assert res['n_months'] == 47
    assert round(res['r'], 3) == 0.689
    assert round(res['r_squared'], 3) == 0.475
    assert round(res['ols_slope'], 3) == 0.102
