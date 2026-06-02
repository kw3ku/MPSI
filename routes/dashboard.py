"""
Dashboard blueprint — public-facing pages: home, historical chart, about.

  GET  /          → index   (dashboard overview)
  GET  /history   → history (historical MPSI time-series)
  GET  /about     → about   (methodology)
"""

import pandas as pd
from flask import Blueprint, render_template, flash, redirect, url_for

import extensions

dashboard_bp = Blueprint('dashboard', __name__)


# ─────────────────────────────────────────────
# Home / overview
# ─────────────────────────────────────────────

@dashboard_bp.route('/')
def index():
    history = extensions.analysis_history

    if history:
        df    = pd.DataFrame(history)
        stats = {
            'total_analyzed': len(df),
            'avg_mpsi':       round(df['mpsi_score'].mean(), 2),
            'hawkish_count':  int((df['stance'] == 'Hawkish').sum()),
            'dovish_count':   int((df['stance'] == 'Dovish').sum()),
            'neutral_count':  int((df['stance'] == 'Neutral').sum()),
        }
    else:
        stats = {
            'total_analyzed': 0,
            'avg_mpsi':       0,
            'hawkish_count':  0,
            'dovish_count':   0,
            'neutral_count':  0,
        }

    recent      = history[-5:][::-1] if history else []
    total_docs  = stats['total_analyzed']
    stance_counts = {
        'Hawkish': stats['hawkish_count'],
        'Dovish':  stats['dovish_count'],
        'Neutral': stats['neutral_count'],
    }

    return render_template(
        'index.html',
        stats=stats,
        recent=recent,
        total_docs=total_docs,
        stance_counts=stance_counts,
        time_series=None,
        year_data=None,
    )


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
    return render_template('about.html')
