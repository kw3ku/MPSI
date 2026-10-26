"""
Download the daily effective Federal Funds Rate (FRED series DFF) from 2020-01-01.

The paper's validation used a hand-entered monthly table instead
(data/fed_funds_paper_handcoded.csv); a snapshot of DFF fetched on 2026-03-19 is
kept in data/fred_dff_snapshot_2026-03-19.csv so results do not drift.

Usage:
    python replication/fetch_fred.py            # writes data/fred_dff_latest.csv
"""

from pathlib import Path

import pandas as pd

URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DFF"
OUT = Path(__file__).resolve().parent / 'data' / 'fred_dff_latest.csv'


def main():
    df = pd.read_csv(URL)
    df.columns = ['date', 'fed_funds_rate']
    df['date'] = pd.to_datetime(df['date'])
    df = df[df['date'] >= '2020-01-01']
    df.to_csv(OUT, index=False)
    print(f"Saved {len(df)} rows ({df['date'].min().date()} to {df['date'].max().date()}) -> {OUT}")


if __name__ == '__main__':
    main()
