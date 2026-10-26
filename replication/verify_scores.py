"""
Check that rebuilt scores match the published data/processed/mpsi_hybrid_scores.csv.

Steps:
    1. Corpus integrity: every file in corpus/MANIFEST.csv marked included=yes
       exists and has the recorded SHA-256.
    2. Keyword columns: rebuilt keyword counts / word counts / Keyword_t match exactly.
    3. Hybrid identity: published mpsi_hybrid == 0.70*keyword + 0.30*finbert
       (or == finbert when no keyword is present), to rounding.
    4. FinBERT column (only if a rebuilt hybrid file exists): max abs difference.

Usage:
    python replication/paper_v1.py --keywords-only
    python replication/verify_scores.py
"""

import hashlib
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PUBLISHED = ROOT / 'data' / 'processed' / 'mpsi_hybrid_scores.csv'
KEY = ['doc_type', 'filename']
KW_COLS = ['hawkish_kw_count', 'dovish_kw_count', 'neutral_kw_count', 'word_count', 'mpsi_keywords']


def check_manifest():
    m = pd.read_csv(HERE / 'corpus' / 'MANIFEST.csv', keep_default_na=False)
    bad = []
    for _, r in m[m.included == 'yes'].iterrows():
        p = HERE / 'corpus' / 'us_fed' / r.path
        if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest() != r.sha256:
            bad.append(r.path)
    print(f"[1] corpus: {len(m)} documents in manifest, {(m.included == 'yes').sum()} redistributed, "
          f"{len(bad)} missing or altered")
    for b in bad:
        print('     ', b)
    return m, not bad


def check_keywords(pub, manifest):
    path = HERE / 'output' / 'rebuilt_keyword_scores.csv'
    if not path.exists():
        print(f"[2] keywords: {path.name} not found — run paper_v1.py --keywords-only first")
        return False
    reb = pd.read_csv(path)
    j = pub.merge(reb, on=KEY, how='left', suffixes=('', '_rebuilt'), indicator=True)
    not_redistributed = set(manifest.loc[manifest.included == 'no', 'path'].str.split('/').str[-1])
    missing = j[j['_merge'] == 'left_only']
    expected_missing = missing['filename'].isin(not_redistributed)
    present = j[j['_merge'] == 'both']
    diff = present[(present[KW_COLS].values != present[[c + '_rebuilt' for c in KW_COLS]].values).any(axis=1)]
    print(f"[2] keywords: {len(present) - len(diff)}/{len(pub)} documents match exactly; "
          f"{len(diff)} differ; {len(missing)} not rebuilt ({int(expected_missing.sum())} not redistributed)")
    for f in diff['filename']:
        print('      differs:', f)
    for f in missing.loc[~expected_missing, 'filename']:
        print('      unexpectedly missing:', f)
    return diff.empty and expected_missing.all()


def check_hybrid_identity(pub):
    no_kw = pub[['hawkish_kw_count', 'dovish_kw_count', 'neutral_kw_count']].sum(axis=1) == 0
    implied = (0.70 * pub.mpsi_keywords + 0.30 * pub.mpsi_finbert).where(~no_kw, pub.mpsi_finbert)
    ok = ((implied - pub.mpsi_hybrid).abs() <= 0.011).sum()
    print(f"[3] hybrid = 0.70*keyword + 0.30*finbert: holds for {ok}/{len(pub)} documents")
    return ok == len(pub)


def check_finbert(pub):
    path = HERE / 'output' / 'rebuilt_hybrid_scores.csv'
    if not path.exists():
        print("[4] finbert: skipped (run paper_v1.py without --keywords-only to rebuild)")
        return True
    reb = pd.read_csv(path)
    j = pub.merge(reb, on=KEY, suffixes=('', '_rebuilt'))
    d_f = (j.mpsi_finbert - j.mpsi_finbert_rebuilt).abs()
    d_h = (j.mpsi_hybrid - j.mpsi_hybrid_rebuilt).abs()
    print(f"[4] finbert: {len(j)} documents compared; max |diff| finbert = {d_f.max():.2f}, "
          f"hybrid = {d_h.max():.2f}; within 0.05: {(d_h <= 0.05).sum()}/{len(j)}")
    return bool((d_h <= 0.05).all())


def main():
    pub = pd.read_csv(PUBLISHED)
    manifest, ok1 = check_manifest()
    ok2 = check_keywords(pub, manifest)
    ok3 = check_hybrid_identity(pub)
    ok4 = check_finbert(pub)
    ok = ok1 and ok2 and ok3 and ok4
    print('\nRESULT:', 'published scores reproduce' if ok else 'see differences above')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
