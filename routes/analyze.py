"""
Analyze blueprint — document upload, results display, PDF export.

  GET  /upload                      → upload form
  POST /upload                      → run MPSI, redirect to result
  GET  /results                     → all results list
  GET  /results/<analysis_id>       → single result detail
  GET  /results/<analysis_id>/pdf   → download PDF report
"""

import io
from datetime import datetime

from flask import (
    Blueprint, render_template, request,
    flash, redirect, url_for, send_file, current_app,
)
from werkzeug.utils import secure_filename

import extensions
from utils.helpers import allowed_file, enrich_result

analyze_bp = Blueprint('analyze', __name__)


# ─────────────────────────────────────────────
# Upload / analyze
# ─────────────────────────────────────────────

@analyze_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        return render_template('upload.html')

    # ── POST: receive and analyse the file ──
    if 'file' not in request.files:
        flash('No file uploaded', 'danger')
        return redirect(request.url)

    file = request.files['file']

    if not file.filename:
        flash('No file selected', 'warning')
        return redirect(request.url)

    if not allowed_file(file.filename, current_app.config['ALLOWED_EXTENSIONS']):
        flash(
            'Invalid file type. Accepted: .txt, .pdf, .doc, .docx',
            'danger',
        )
        return redirect(request.url)

    try:
        content = file.read().decode('utf-8', errors='ignore')

        if len(content.split()) < current_app.config.get('MIN_WORD_COUNT', 50):
            flash(
                'Document too short — please upload at least 50 words.',
                'warning',
            )
            return redirect(request.url)

        raw = extensions.mpsi_calculator.calculate_hybrid_mpsi(content)
        result = enrich_result(raw, file.filename, content)

        extensions.analysis_history.append(result)
        analysis_id = len(extensions.analysis_history) - 1

        flash(
            f'✅ Analysis complete! MPSI Score: {result["mpsi_score"]} ({result["stance"]})',
            'success',
        )
        return redirect(url_for('analyze.results', analysis_id=analysis_id))

    except Exception as exc:
        flash(f'Error analysing document: {exc}', 'danger')
        return redirect(request.url)


# ─────────────────────────────────────────────
# Results
# ─────────────────────────────────────────────

@analyze_bp.route('/results')
@analyze_bp.route('/results/<int:analysis_id>')
def results(analysis_id=None):
    history = extensions.analysis_history

    if analysis_id is not None and 0 <= analysis_id < len(history):
        return render_template(
            'results.html',
            result=history[analysis_id],
            analysis_id=analysis_id,
        )

    # No ID — show full list
    return render_template('all_results.html', results=history[::-1])


# ─────────────────────────────────────────────
# PDF export
# ─────────────────────────────────────────────

@analyze_bp.route('/results/<int:analysis_id>/pdf')
def export_pdf(analysis_id):
    history = extensions.analysis_history

    if analysis_id < 0 or analysis_id >= len(history):
        flash('Result not found', 'danger')
        return redirect(url_for('analyze.results'))

    from models.export_report import MPSIReportGenerator
    report_gen = MPSIReportGenerator()

    result = history[analysis_id]
    pdf    = report_gen.generate(result)
    fname  = (
        f"MPSI_Report_"
        f"{result.get('filename', 'analysis').replace('.txt', '')}_"
        f"{datetime.now().strftime('%Y%m%d')}.pdf"
    )

    return send_file(
        io.BytesIO(pdf),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=fname,
    )
