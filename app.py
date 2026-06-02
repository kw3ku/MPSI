"""
MPSI Dashboard — Flask application entry point.

Usage:
    python app.py              (dev server)
    flask run                  (via FLASK_APP=app:create_app)
"""

import os
from flask import Flask
from config import Config


def create_app(config_class=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure required directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['DATABASE_DIR'],  exist_ok=True)

    # Initialise shared extensions (MPSI calculator + historical data)
    from extensions import init_extensions
    init_extensions(app)

    # Register blueprints
    from routes.dashboard import dashboard_bp
    from routes.analyze   import analyze_bp
    from routes.api       import api_bp

    app.register_blueprint(dashboard_bp)          # /  /history  /about
    app.register_blueprint(analyze_bp)            # /upload  /results
    app.register_blueprint(api_bp)                # /api/...

    return app


if __name__ == '__main__':
    application = create_app()

    print("\n" + "=" * 70)
    print("MPSI DASHBOARD — STARTING")
    print("=" * 70)
    print("\n📊  Dashboard : http://localhost:5000")
    print("📤  Upload    : http://localhost:5000/upload")
    print("📈  History   : http://localhost:5000/history")
    print("📖  About     : http://localhost:5000/about")
    print("🔌  API       : http://localhost:5000/api/analyze")
    print("\n✅  Ready to analyse Fed documents!\n")

    application.run(
        debug=True,
        host=application.config.get('HOST', '0.0.0.0'),
        port=application.config.get('PORT', 5000),
    )
