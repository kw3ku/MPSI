"""
Dashboard blueprint — public-facing pages: home, historical chart, about.

  GET  /          → index   (dashboard overview)
  GET  /history   → history (historical MPSI time-series)
  GET  /about     → about   (methodology)
"""

import pandas as pd
from pathlib import Path

from flask import Blueprint, render_template, flash, redirect, url_for, current_app

import extensions

dashboard_bp = Blueprint('dashboard', __name__)


# ─────────────────────────────────────────────
# Home / overview
# ─────────────────────────────────────────────

def _stance(x):
    return 'Hawkish' if x > 10 else ('Dovish' if x < -10 else 'Neutral')


def _overview():
    """Dashboard figures computed from the published score file (no hard-coded values)."""
    df = extensions.historical_df.copy()
    if df.empty:
        return None
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    dated = df.dropna(subset=['date']).sort_values('date')
    monthly = dated.set_index('date')['mpsi_hybrid'].resample('MS').mean().dropna().round(2)
    labels = monthly.index.strftime('%Y-%m').tolist()
    try:
        ffr = pd.read_csv(Path(current_app.config['HISTORICAL_DATA_PATH']).parent / 'ffr_monthly.csv')
        ffr_map = dict(zip(ffr['month'], ffr['ffr']))
    except Exception:
        ffr_map = {}
    latest = dated.iloc[-1]
    years = [{'year': int(y), 'n': len(g), 'mean': round(g['mpsi_hybrid'].mean(), 1),
              'sd': round(g['mpsi_hybrid'].std(), 1), 'stance': _stance(g['mpsi_hybrid'].mean())}
             for y, g in df.groupby('year')]
    types = [{'doc_type': t, 'n': len(g), 'mean': round(g['mpsi_hybrid'].mean(), 1),
              'stance': _stance(g['mpsi_hybrid'].mean())}
             for t, g in sorted(df.groupby('doc_type'), key=lambda kv: -len(kv[1]))]
    sc = df['stance'].value_counts().to_dict()
    return {
        'total': len(df), 'dated': len(dated), 'months': len(monthly),
        'hawkish': sc.get('Hawkish', 0), 'neutral': sc.get('Neutral', 0), 'dovish': sc.get('Dovish', 0),
        'latest_score': round(float(latest['mpsi_hybrid']), 1), 'latest_stance': latest['stance'],
        'latest_date': latest['date'].strftime('%b %d, %Y'), 'latest_type': latest['doc_type'],
        'overall_mean': round(df['mpsi_hybrid'].mean(), 1), 'overall_sd': round(df['mpsi_hybrid'].std(), 1),
        'years': years, 'types': types,
        'series': {'labels': labels, 'mpsi': monthly.tolist(), 'ffr': [ffr_map.get(l) for l in labels]},
    }


@dashboard_bp.route('/')
def index():
    return render_template('index.html', ov=_overview())


# ─────────────────────────────────────────────
# Historical data / time-series
# ─────────────────────────────────────────────

@dashboard_bp.route('/history')
def history():
    df = extensions.historical_df.copy()

    if df.empty:
        flash('No historical data available', 'warning')
        return redirect(url_for('dashboard.index'))

    # Time-series
    time_series = None
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date']).sort_values('date')
        time_series = {
            'dates':       df['date'].dt.strftime('%Y-%m-%d').tolist(),
            'mpsi_scores': df['mpsi_hybrid'].tolist(),
            'doc_types':   df['doc_type'].tolist() if 'doc_type' in df.columns else [],
        }

    # Per-year aggregation — keyed by year so template can do: for year, row in year_data.items()
    year_data = None
    if 'year' in df.columns:
        year_data = {}
        for yr, grp in df.groupby('year'):
            sc = grp['stance'].value_counts().to_dict() if 'stance' in grp.columns else {}
            year_data[int(yr)] = {
                'doc_count': len(grp),
                'avg_mpsi':  round(grp['mpsi_hybrid'].mean(), 2),
                'hawkish':   sc.get('Hawkish', 0),
                'neutral':   sc.get('Neutral', 0),
                'dovish':    sc.get('Dovish', 0),
            }

    stance_counts = (
        df['stance'].value_counts().to_dict() if 'stance' in df.columns else {}
    )

    return render_template(
        'dashboard.html',
        time_series=time_series,
        year_data=year_data,
        stance_counts=stance_counts,
        total_docs=len(df),
    )


# ─────────────────────────────────────────────
# About / methodology
# ─────────────────────────────────────────────

@dashboard_bp.route('/about')
def about():
    return render_template('about.html', ov=_overview())
