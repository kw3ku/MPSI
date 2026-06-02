"""
API blueprint — JSON endpoints consumed by the frontend and external callers.

  POST /api/analyze         → analyse uploaded file, return JSON
  GET  /api/stats           → aggregate stats from session history
  POST /api/fetch-latest    → pull + analyse most-recent FOMC statement
  GET  /api/check-new       → check whether new Fed docs exist
"""

from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

import extensions
from utils.helpers import allowed_file, enrich_result
from utils.fed_fetcher import FedDocumentFetcher

api_bp = Blueprint('api', __name__, url_prefix='/api')

_fed_fetcher = FedDocumentFetcher()


# ─────────────────────────────────────────────
# Analyse an uploaded document
# ─────────────────────────────────────────────

@api_bp.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']

    if not file.filename:
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename, current_app.config['ALLOWED_EXTENSIONS']):
        return jsonify({'error': 'Invalid file type'}), 400

    try:
        content = file.read().decode('utf-8', errors='ignore')
        raw     = extensions.mpsi_calculator.calculate_hybrid_mpsi(content)
        result  = enrich_result(raw, file.filename, content)
        extensions.analysis_history.append(result)

        return jsonify({'success': True, 'result': result})

    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


# ─────────────────────────────────────────────
# Aggregate statistics
# ─────────────────────────────────────────────

@api_bp.route('/stats')
def stats():
    history = extensions.analysis_history

    if not history:
        return jsonify({
            'total_documents':    0,
            'avg_mpsi':           0,
            'stance_distribution': {},
        })

    import pandas as pd
    df = pd.DataFrame(history)

    return jsonify({
        'total_documents':    len(df),
        'avg_mpsi':           round(df['mpsi_score'].mean(), 2),
        'stance_distribution': df['stance'].value_counts().to_dict(),
        'recent_analyses':    history[-10:][::-1],
    })


# ─────────────────────────────────────────────
# Fetch & analyse the latest FOMC statement
# ─────────────────────────────────────────────

@api_bp.route('/fetch-latest', methods=['POST'])
def fetch_latest():
    try:
        latest = _fed_fetcher.get_latest_statement()
        if not latest:
            return jsonify({'error': 'Could not fetch Fed website'}), 503

        newest             = latest[0]
        save_path, text    = _fed_fetcher.fetch_and_save(newest['url'])

        if not text:
            return jsonify({'error': 'Could not download document'}), 503

        raw    = extensions.mpsi_calculator.calculate_hybrid_mpsi(text)
        result = enrich_result(raw, f"fomc_st_{newest['date']}.txt", text)
        extensions.analysis_history.append(result)

        # Compare against historical baseline
        comparison = {}
        hdf = extensions.historical_df
        if not hdf.empty and 'mpsi_hybrid' in hdf.columns:
            hist_avg  = round(hdf['mpsi_hybrid'].mean(), 2)
            hist_last = round(hdf.tail(5)['mpsi_hybrid'].mean(), 2)
            new_score = result['mpsi_score']
            comparison = {
                'historical_avg':     hist_avg,
                'recent_5_avg':       hist_last,
                'new_score':          new_score,
                'change_from_avg':    round(new_score - hist_avg, 2),
                'change_from_recent': round(new_score - hist_last, 2),
                'trend': (
                    'More Hawkish than recent trend' if new_score > hist_last + 5 else
                    'More Dovish than recent trend'  if new_score < hist_last - 5 else
                    'In line with recent trend'
                ),
            }

        return jsonify({
            'success':    True,
            'result':     result,
            'comparison': comparison,
            'source_url': newest['url'],
        })

    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


# ─────────────────────────────────────────────
# Check for new documents (non-destructive)
# ─────────────────────────────────────────────

@api_bp.route('/check-new')
def check_new():
    try:
        latest = _fed_fetcher.get_latest_statement()

        known_dates: set = set()
        hdf = extensions.historical_df
        if not hdf.empty and 'date' in hdf.columns:
            known_dates = set(hdf['date'].dropna().tolist())

        new_docs = []
        for doc in latest:
            d = doc['date']
            date_fmt = f"{d[:4]}-{d[4:6]}-{d[6:]}" if len(d) == 8 else d
            if date_fmt not in known_dates:
                new_docs.append(doc)

        return jsonify({
            'new_documents_available': len(new_docs) > 0,
            'count':                   len(new_docs),
            'documents':               new_docs,
        })

    except Exception as exc:
        return jsonify({'error': str(exc)}), 500
