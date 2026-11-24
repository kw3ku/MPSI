"""
Granger-causality tests between monthly MPSI and changes in the Fed Funds Rate.

The paper (Table 18) reports
    MPSI does not Granger-cause dFFR     F = 8.42, p < 0.001
    dFFR does not Granger-cause MPSI     F = 1.73, p = 0.168
but gives no lag order, sample, or treatment of months without a document, and
no generating script was found. This script runs the standard test under stated
choices and reports every lag order so nothing depends on a hidden selection.

Test (lag order p):
    unrestricted   y_t = a + sum_{i=1..p} b_i y_{t-i} + sum_{i=1..p} c_i x_{t-i} + e_t
    restricted     c_1 = ... = c_p = 0
    F = ((RSS_r - RSS_u) / p) / (RSS_u / (T - 2p - 1))

Choices:
    - Monthly calendar. dFFR_t = FFR_t - FFR_{t-1} (monthly mean of FRED DFF, or the
      paper's hand-entered table).
    - MPSI_t = mean MPSI of dated documents in month t. Months without a document
      (about one in four) carry the last observed value forward.
    - Lag order p = 1..6, all estimated on the same sample (first 6 months dropped)
      so AIC/BIC are comparable. AIC and BIC choices are flagged.

Specifications:
    all_docs     statements and minutes, both dated by meeting date (the paper's series).
                 Minutes are released about three weeks after the meeting, so this
                 series uses text before it was public.
    statements   FOMC statements only (public on the day).
    d_mpsi       same as all_docs but with MPSI in first differences.
    handcoded    all_docs against the paper's hand-entered FFR table (ends 2025-04).

Usage:
    python replication/granger_ffr.py
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from ffr_validation import handcoded, monthly_fred

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MAX_LAG = 6


def monthly_mpsi(scores_path, doc_type=None):
    df = pd.read_csv(scores_path, parse_dates=['date']).dropna(subset=['date'])
    if doc_type:
        df = df[df['doc_type'] == doc_type]
    return df.set_index('date').resample('ME')['mpsi_hybrid'].mean().dropna().to_period('M')


def _rss(y, X):
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    return float(resid @ resid)


def granger(y, x, p, max_lag=MAX_LAG):
    """F-test that p lags of x add nothing to an AR(p) for y. Sample starts at max_lag."""
    y = np.asarray(y, float)
    x = np.asarray(x, float)
    T = len(y) - max_lag
    Y = y[max_lag:]
    ylags = np.column_stack([y[max_lag - i:len(y) - i] for i in range(1, p + 1)])
    xlags = np.column_stack([x[max_lag - i:len(x) - i] for i in range(1, p + 1)])
    const = np.ones((T, 1))
    rss_r = _rss(Y, np.hstack([const, ylags]))
    rss_u = _rss(Y, np.hstack([const, ylags, xlags]))
    k = 2 * p + 1
    df2 = T - k
    F = ((rss_r - rss_u) / p) / (rss_u / df2)
    return {'lags': p, 'n': T, 'F': F, 'p_value': float(stats.f.sf(F, p, df2)),
            'aic': T * np.log(rss_u / T) + 2 * k, 'bic': T * np.log(rss_u / T) + k * np.log(T)}


def run_spec(name, mpsi, ffr, diff_mpsi=False):
    cal = pd.period_range(mpsi.index.min(), min(mpsi.index.max(), ffr.index.max()), freq='M')
    d = pd.DataFrame({'mpsi': mpsi.reindex(cal).ffill(), 'ffr': ffr.reindex(cal)})
    d['dffr'] = d['ffr'].diff()
    if diff_mpsi:
        d['mpsi'] = d['mpsi'].diff()
    d = d.dropna()
    rows = []
    for direction, y, x in (('MPSI -> dFFR', d['dffr'], d['mpsi']), ('dFFR -> MPSI', d['mpsi'], d['dffr'])):
        res = [granger(y, x, p) for p in range(1, MAX_LAG + 1)]
        best_aic = min(res, key=lambda r: r['aic'])['lags']
        best_bic = min(res, key=lambda r: r['bic'])['lags']
        for r in res:
            sel = '+'.join(s for s, b in (('AIC', best_aic), ('BIC', best_bic)) if b == r['lags'])
            rows.append({'spec': name, 'direction': direction, 'first': str(d.index[MAX_LAG]),
                         'last': str(d.index[-1]), 'lags': r['lags'], 'n': r['n'],
                         'F': round(r['F'], 2), 'p_value': round(r['p_value'], 4), 'selected': sel})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--scores', default=ROOT / 'data' / 'processed' / 'mpsi_hybrid_scores.csv')
    ap.add_argument('--handcoded', default=HERE / 'data' / 'fed_funds_paper_handcoded.csv')
    ap.add_argument('--fred', default=HERE / 'data' / 'fred_dff_snapshot_2026-03-19.csv')
    ap.add_argument('--out', default=HERE / 'output')
    args = ap.parse_args()

    fred = monthly_fred(args.fred)
    # the snapshot's last month is partial; keep complete months only
    fred = fred[fred.index < fred.index.max()]
    hand = handcoded(args.handcoded)
    all_docs = monthly_mpsi(args.scores)
    statements = monthly_mpsi(args.scores, 'FOMC Statements')

    rows = []
    rows += run_spec('all_docs', all_docs, fred)
    rows += run_spec('statements', statements, fred)
    rows += run_spec('d_mpsi', all_docs, fred, diff_mpsi=True)
    rows += run_spec('handcoded', all_docs, hand)
    table = pd.DataFrame(rows)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    table.to_csv(out / 'granger_ffr.csv', index=False)

    pd.set_option('display.width', 140)
    print("Granger causality, monthly MPSI and dFFR (paper Table 18: F = 8.42 / 1.73)\n")
    for spec, g in table.groupby('spec', sort=False):
        print(f"[{spec}]  sample {g['first'].iloc[0]} to {g['last'].iloc[0]}, n = {g['n'].iloc[0]}")
        wide = g.pivot(index='lags', columns='direction', values=['F', 'p_value', 'selected'])
        wide = wide.swaplevel(axis=1).sort_index(axis=1, level=0, sort_remaining=False)
        print(wide.to_string(), "\n")
    print(f"Saved {out / 'granger_ffr.csv'}")


if __name__ == '__main__':
    main()
