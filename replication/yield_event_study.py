"""
Event study: response of the 2-year Treasury yield to MPSI surprises on FOMC statement days.

The paper (Table 19) reports beta = +42.3 bps per 10-point MPSI surprise, t = 5.82,
R^2 = 0.41, but does not define "MPSI surprise" or the event window, and no
generating script was found. This script estimates

    dY_e (bps) = a + b * Surprise_e + u_e

over FOMC statement events under three candidate surprise definitions and two
windows, and reports all of them.

Events:
    Documents with doc_type "FOMC Statements" (public at 2 pm ET on their date).
    Minutes are excluded: they are dated by meeting day in this corpus but released
    about three weeks later. Speeches and outlook documents have no dates.
    An event on a non-trading day is moved to the next trading day.

Surprise definitions (all use only statement scores):
    change   MPSI_e - MPSI_{e-1}
    ma3      MPSI_e - mean(MPSI_{e-1}, MPSI_{e-2}, MPSI_{e-3})
    ar1      residual of MPSI_e on a constant and MPSI_{e-1} (full-sample fit)

Windows (FRED DGS2, daily close, percent):
    1d   close(t) - close(t-1)
    2d   close(t+1) - close(t-1)

Reported: beta x 10 (bps per 10-point surprise), OLS t, heteroskedasticity-robust
(HC1) t, R^2, n.

Usage:
    python replication/yield_event_study.py
    python replication/yield_event_study.py --fetch     # refresh DGS2 from FRED first
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS2&cosd=2019-12-01"


def load_yield(path):
    y = pd.read_csv(path, parse_dates=['date'])
    y['dgs2'] = pd.to_numeric(y['dgs2'], errors='coerce')   # FRED marks holidays as blank or "."
    return y.dropna().set_index('date')['dgs2'].sort_index()


def statement_events(scores_path):
    df = pd.read_csv(scores_path, parse_dates=['date']).dropna(subset=['date'])
    df = df[df['doc_type'] == 'FOMC Statements'].sort_values('date')
    e = df[['date', 'filename', 'mpsi_hybrid']].rename(columns={'mpsi_hybrid': 'mpsi'}).reset_index(drop=True)
    e['change'] = e['mpsi'].diff()
    e['ma3'] = e['mpsi'] - e['mpsi'].shift(1).rolling(3).mean()
    lag = e['mpsi'].shift(1)
    ok = lag.notna()
    slope, intercept = np.polyfit(lag[ok], e.loc[ok, 'mpsi'], 1)
    e['ar1'] = e['mpsi'] - (intercept + slope * lag)
    return e


def add_yield_changes(events, y):
    days = y.index
    pos = days.searchsorted(events['date'])          # first trading day on or after the event
    events = events[pos + 1 < len(days)].copy()
    pos = pos[pos + 1 < len(days)]
    events['trade_date'] = days[pos]
    events['dy_1d'] = (y.values[pos] - y.values[pos - 1]) * 100
    events['dy_2d'] = (y.values[pos + 1] - y.values[pos - 1]) * 100
    return events


def ols(x, yv):
    x = np.asarray(x, float)
    yv = np.asarray(yv, float)
    n = len(x)
    X = np.column_stack([np.ones(n), x])
    XtX_inv = np.linalg.inv(X.T @ X)
    b = XtX_inv @ X.T @ yv
    u = yv - X @ b
    se = np.sqrt(np.diag(XtX_inv) * (u @ u) / (n - 2))
    V_hc1 = XtX_inv @ (X.T * u ** 2) @ X @ XtX_inv * n / (n - 2)
    r2 = 1 - (u @ u) / ((yv - yv.mean()) @ (yv - yv.mean()))
    return b[1], b[1] / se[1], b[1] / np.sqrt(V_hc1[1, 1]), r2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--scores', default=ROOT / 'data' / 'processed' / 'mpsi_hybrid_scores.csv')
    ap.add_argument('--dgs2', default=HERE / 'data' / 'fred_dgs2_snapshot_2026-11-22.csv')
    ap.add_argument('--fetch', action='store_true', help='download DGS2 to data/fred_dgs2_latest.csv and use it')
    ap.add_argument('--out', default=HERE / 'output')
    args = ap.parse_args()

    if args.fetch:
        args.dgs2 = HERE / 'data' / 'fred_dgs2_latest.csv'
        raw = pd.read_csv(URL)
        raw.columns = ['date', 'dgs2']
        raw.to_csv(args.dgs2, index=False)

    events = add_yield_changes(statement_events(args.scores), load_yield(args.dgs2))

    rows = []
    for sample, ev in (('all', events), ('scheduled', events[~events['date'].isin(UNSCHEDULED)])):
        for surprise in ('change', 'ma3', 'ar1'):
            for window in ('1d', '2d'):
                d = ev[[surprise, f'dy_{window}']].dropna()
                b, t, t_hc1, r2 = ols(d[surprise], d[f'dy_{window}'])
                rows.append({'events': sample, 'surprise': surprise, 'window': window, 'n': len(d),
                             'bps_per_10pt': round(10 * b, 2), 't_ols': round(t, 2),
                             't_hc1': round(t_hc1, 2), 'r_squared': round(r2, 3)})
    table = pd.DataFrame(rows)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    events.to_csv(out / 'yield_event_study_events.csv', index=False)
    table.to_csv(out / 'yield_event_study.csv', index=False)

    pd.set_option('display.width', 140)
    print("2-year Treasury yield response to MPSI surprises on FOMC statement days")
    print("(paper Table 19: +42.3 bps per 10 points, t = 5.82, R^2 = 0.41)\n")
    print(table.to_string(index=False))
    print(f"\nMean |surprise| (change): {events['change'].abs().mean():.1f} points; "
          f"mean |1-day yield change|: {events['dy_1d'].abs().mean():.1f} bps")
    print(f"Saved {out / 'yield_event_study.csv'} and {out / 'yield_event_study_events.csv'}")


# Files under fomc_statements/ that are not scheduled post-meeting statements:
# the March 2020 emergency actions, the two framework-review announcements, and
# fomc_st_20211216.txt, whose text is a 2020 pandemic-era statement (file name misdated).
# Surprises are computed on the full sequence before this filter is applied.
UNSCHEDULED = pd.to_datetime(['2020-03-03', '2020-03-15', '2020-03-23', '2020-08-27',
                              '2021-12-16', '2025-08-22'])


if __name__ == '__main__':
    main()
