"""
Shared application state — initialized once at startup, imported by blueprints.
"""

import pandas as pd

# Populated in init_extensions()
mpsi_calculator  = None
historical_df    = pd.DataFrame()
analysis_history = []          # in-memory session store; replace with DB in production


def init_extensions(app):
    """Load heavy objects once when the Flask app is created."""
    global mpsi_calculator, historical_df

    from models.mpsi_calculator import HybridMPSICalculator

    print("\n" + "=" * 70)
    print("MPSI DASHBOARD — INITIALIZING")
    print("=" * 70)

    print("\n⏳ Loading HybridMPSICalculator …")
    mpsi_calculator = HybridMPSICalculator()
    print("✅ Calculator ready")

    try:
        historical_df = pd.read_csv(app.config['HISTORICAL_DATA_PATH'])
        print(f"✅ Loaded {len(historical_df)} historical MPSI records")
    except Exception as exc:
        historical_df = pd.DataFrame()
        print(f"⚠️  No historical data loaded: {exc}")
