"""
Reproduce the MPSI vs Federal Funds Rate validation (paper Table: r = 0.689, R^2 = 0.475).

Method (same as the research script 03-validate_mpsi_fix.py):
    1. Average MPSI over all dated documents in each calendar month.
    2. Pair each month with that month's Fed Funds Rate.
    3. Pearson r, R^2, two-sided t-test p-value, OLS slope of FFR on MPSI.

Three specifications are reported side by side:
    A  paper      FFR = hand-entered monthly table (data/fed_funds_paper_handcoded.csv),
                  which stops at 2025-04 — this is the specification behind the paper's numbers
    B  fred_same  FFR = FRED DFF monthly mean, restricted to the same months as A
    C  fred_full  FFR = FRED DFF monthly mean, every month that has a dated MPSI document

It also reports lead/lag correlations corr(MPSI_t, FFR_{t+k}) on a full monthly
calendar, so k counts calendar months rather than rows.

Usage:
    python replication/ffr_validation.py
    python replication/ffr_validation.py --fred replication/data/fred_dff_latest.csv
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def monthly_mpsi(scores_path):
    df = pd.read_csv(scores_path, parse_dates=['date'])
    df = df.dropna(subset=['date'])
    return df.set_index('date').resample('ME')['mpsi_hybrid'].mean().dropna().to_period('M')


def monthly_fred(fred_path):
    f = pd.read_csv(fred_path, parse_dates=['date']).sort_values('date')
    f['fed_funds_rate'] = f['fed_funds_rate'].ffill()
    return f.set_index('date').resample('ME')['fed_funds_rate'].mean().to_period('M')


def handcoded(path):
    h = pd.read_csv(path)
    return pd.Series(h['fed_funds_rate'].values, index=pd.PeriodIndex(h['year_month'], freq='M'))


def correlate(mpsi, ffr, label):
    d = pd.DataFrame({'mpsi': mpsi, 'ffr': ffr}).dropna()
    n = len(d)
    r = d['mpsi'].corr(d['ffr'])
    t = r * np.sqrt(n - 2) / np.sqrt(1 - r ** 2)
    p = 2 * (1 - stats.t.cdf(abs(t), n - 2))
    slope = stats.linregress(d['mpsi'], d['ffr']).slope
    return {'spec': label, 'n_months': n, 'first': str(d.index.min()), 'last': str(d.index.max()),
            'r': round(r, 4), 'r_squared': round(r ** 2, 4), 'p_value': float(f"{p:.3g}"),
            'ols_slope': round(slope, 4)}


def lead_lag(mpsi, ffr, max_k=6):
    cal = pd.period_range(min(mpsi.index.min(), ffr.index.min()), ffr.index.max(), freq='M')
    m = mpsi.reindex(cal)
    f = ffr.reindex(cal)
    rows = []
    for k in range(-max_k, max_k + 1):
        d = pd.DataFrame({'m': m, 'f': f.shift(-k)}).dropna()
        rows.append({'k_months': k, 'n': len(d), 'r': round(d['m'].corr(d['f']), 4)})
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--scores', default=ROOT / 'data' / 'processed' / 'mpsi_hybrid_scores.csv')
    ap.add_argument('--handcoded', default=HERE / 'data' / 'fed_funds_paper_handcoded.csv')
    ap.add_argument('--fred', default=HERE / 'data' / 'fred_dff_snapshot_2026-03-19.csv')
    ap.add_argument('--out', default=HERE / 'output')
    args = ap.parse_args()

    mpsi = monthly_mpsi(args.scores)
    hand = handcoded(args.handcoded)
    fred = monthly_fred(args.fred)
    same = mpsi.index.intersection(hand.index)

    table = pd.DataFrame([
        correlate(mpsi, hand, 'A_paper_handcoded'),
        correlate(mpsi.loc[same], fred, 'B_fred_same_months'),
        correlate(mpsi, fred, 'C_fred_all_months'),
    ])
    ll = lead_lag(mpsi, fred)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    table.to_csv(out / 'ffr_validation.csv', index=False)
    ll.to_csv(out / 'ffr_lead_lag.csv', index=False)

    pd.set_option('display.width', 120)
    print("MPSI vs Fed Funds Rate (monthly)\n")
    print(table.to_string(index=False))
    print("\nLead/lag on FRED DFF: corr(MPSI_t, FFR_{t+k}); k > 0 means MPSI leads\n")
    print(ll.to_string(index=False))
    print(f"\nSaved {out / 'ffr_validation.csv'} and {out / 'ffr_lead_lag.csv'}")


if __name__ == '__main__':
    main()
