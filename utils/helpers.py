"""
Shared helper utilities used across multiple blueprints.
"""

from datetime import datetime
from werkzeug.utils import secure_filename


def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """Return True if the filename has an allowed extension."""
    return (
        '.' in filename
        and filename.rsplit('.', 1)[1].lower() in allowed_extensions
    )


def enrich_result(result: dict, filename: str, text: str) -> dict:
    """Attach display-friendly fields to a raw calculator result dict."""
    result = dict(result)   # don't mutate the original

    result['filename']     = secure_filename(filename)
    result['timestamp']    = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    result['text_preview'] = text[:500] + '…' if len(text) > 500 else text

    # Stance colour (Bootstrap / CSS class)
    stance = result.get('stance', 'Neutral')
    if stance == 'Hawkish':
        result['stance_color'] = 'danger'
    elif stance == 'Dovish':
        result['stance_color'] = 'primary'
    else:
        result['stance_color'] = 'secondary'

    # Confidence label
    score = abs(result.get('mpsi_score', 0))
    if score > 20:
        result['confidence'] = 'High'
    elif score > 10:
        result['confidence'] = 'Medium'
    else:
        result['confidence'] = 'Low'

    # Derived counts
    text_preview = result.get('text_preview', '')
    result['word_count'] = len(text_preview.split()) if text_preview else 0
    result['total_keywords'] = (
        result.get('hawkish_keywords', 0)
        + result.get('dovish_keywords', 0)
        + result.get('neutral_keywords', 0)
    )

    return result
