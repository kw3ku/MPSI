mpsi_dash/
├── app.py                          ← Main Flask app
├── config.py                       ← Configuration
├── .env                            ← Environment vars (exists!)
├── models/
│   └── mpsi_calculator.py          ← Core MPSI engine ✅
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── dashboard.html
│   ├── upload.html
│   ├── results.html
│   ├── all_results.html
│   ├── about.html
│   ├── tem.html / tem2.html / tem3.html  ← Draft templates
├── data/
│   ├── processed/
│   │   └── mpsi_hybrid_scores.csv  ← REAL scores exist! ✅
│   ├── us_fed/
│   │   ├── fomc_statements/        ← 50+ statements 2020–2026 ✅
│   │   ├── fomc_minutes/           ← 50+ minutes 2020–2026 ✅
│   │   ├── fed_chair_speeches/     ← Jackson Hole 2021–2025 ✅
│   │   └── economic_outlook/       ← Additional docs ✅
│   └── visualizations/
│       ├── mpsi_time_series.png    ✅
│       ├── mpsi_validation_comprehensive.png ✅
│       ├── mpsi_by_year.png        ✅
│       ├── mpsi_rolling_average.png ✅
│       └── mpsi_by_doctype.png     ✅
└── venv/                           ← Python 3.9 venv ✅