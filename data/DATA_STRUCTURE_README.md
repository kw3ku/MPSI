# MPSI Project Data Structure

## Overview
This data structure emphasizes **US Federal Reserve sources (70%)** with Ghana Bank of Ghana as comparative validation (30%), aligned with NIW EB2 strategy.

---

## Directory Structure

```
data/
├── us_fed/                          # 70% - PRIMARY US SOURCES (Target: 250-280 documents)
│   ├── fomc_statements/             # FOMC post-meeting statements (2020-2024)
│   │   └── fomc_statement_YYYYMMDD.txt
│   │   └── metadata.csv
│   │
│   ├── fomc_minutes/                # FOMC meeting minutes (detailed)
│   │   └── fomc_minutes_YYYYMMDD.txt
│   │
│   ├── fed_chair_speeches/          # Jerome Powell speeches & testimonies
│   │   └── powell_speech_YYYYMMDD_topic.txt
│   │
│   ├── monetary_policy_reports/     # Semi-annual reports to Congress
│   │   └── mpr_YYYYMM.txt
│   │
│   ├── fed_governor_speeches/       # Other FOMC member speeches
│   │   └── [governor_name]_speech_YYYYMMDD.txt
│   │
│   └── press_conference_transcripts/ # Post-FOMC Q&A transcripts
│       └── press_conf_YYYYMMDD.txt
│
├── ghana_bog/                       # 30% - SECONDARY COMPARATIVE SOURCES (Target: 70-85 docs)
│   ├── mpc_press_releases/          # Monetary Policy Committee releases
│   │   └── mpc_release_YYYYMMDD.txt
│   │
│   ├── governor_speeches/           # Bank of Ghana Governor speeches
│   │   └── bog_speech_YYYYMMDD_topic.txt
│   │
│   └── monetary_policy_reports/     # BoG policy reports
│       └── bog_report_YYYYMM.txt
│
├── processed/                       # Processed data & MPSI scores
│   ├── mpsi_scores/
│   │   ├── us_fed_mpsi.csv          # All US Fed MPSI scores
│   │   ├── ghana_bog_mpsi.csv       # All Ghana BoG MPSI scores
│   │   └── combined_mpsi.csv        # Combined dataset
│   │
│   └── metadata/
│       ├── us_fed_metadata.csv      # US document metadata
│       ├── ghana_bog_metadata.csv   # Ghana document metadata
│       └── collection_log.csv       # Data collection tracking
│
└── external/                        # External data sources
    ├── market_data/                 # US financial market data
    │   ├── sp500_daily.csv
    │   ├── treasury_yields_daily.csv
    │   ├── vix_daily.csv
    │   └── dxy_daily.csv
    │
    └── economic_data/               # US economic indicators (FRED)
        ├── cpi_monthly.csv
        ├── unemployment_monthly.csv
        ├── gdp_quarterly.csv
        └── consumer_sentiment_monthly.csv

results/
├── us_analysis/                     # PRIMARY US-FOCUSED ANALYSIS
│   ├── market_impact/               # Module 1: Financial markets
│   │   ├── correlation_results.csv
│   │   ├── lagged_effects.csv
│   │   ├── event_study_results.csv
│   │   └── granger_causality.csv
│   │
│   ├── economic_indicators/         # Module 2: Macroeconomic analysis
│   │   ├── inflation_analysis.csv
│   │   ├── unemployment_analysis.csv
│   │   ├── gdp_analysis.csv
│   │   └── predictive_regressions.csv
│   │
│   ├── crisis_detection/            # Module 3: Crisis events
│   │   ├── covid_2020_analysis.csv
│   │   ├── inflation_surge_2021_2023.csv
│   │   └── banking_stress_2023.csv
│   │
│   └── policy_transparency/         # Module 4: Fed communication
│       ├── mpsi_volatility.csv
│       ├── communication_clarity.csv
│       └── consistency_analysis.csv
│
├── ghana_analysis/                  # SECONDARY: Ghana validation
│   └── ghana_results.csv
│
├── comparative_analysis/            # Cross-country comparison
│   ├── methodology_validation.csv
│   └── us_ghana_comparison.csv
│
├── figures/                         # Visualizations
│   ├── publication_quality/         # For paper/presentations
│   │   ├── fig1_mpsi_timeseries.pdf
│   │   ├── fig2_market_correlation.pdf
│   │   └── fig3_crisis_detection.pdf
│   │
│   └── exploratory/                 # Working visualizations
│       └── *.png
│
└── tables/                          # Statistical tables
    ├── table1_summary_statistics.csv
    ├── table2_correlation_matrix.csv
    └── table3_regression_results.csv
```

---

## File Naming Conventions

### US Federal Reserve Documents

| Document Type | Naming Convention | Example |
|---------------|-------------------|---------|
| FOMC Statements | `fomc_statement_YYYYMMDD.txt` | `fomc_statement_20240131.txt` |
| FOMC Minutes | `fomc_minutes_YYYYMMDD.txt` | `fomc_minutes_20240131.txt` |
| Powell Speeches | `powell_speech_YYYYMMDD_topic.txt` | `powell_speech_20230825_jackson_hole.txt` |
| Monetary Policy Reports | `mpr_YYYYMM.txt` | `mpr_202402.txt` |
| Governor Speeches | `[lastname]_speech_YYYYMMDD_topic.txt` | `waller_speech_20230615_inflation.txt` |
| Press Conferences | `press_conf_YYYYMMDD.txt` | `press_conf_20240131.txt` |

### Ghana Bank of Ghana Documents

| Document Type | Naming Convention | Example |
|---------------|-------------------|---------|
| MPC Releases | `mpc_release_YYYYMMDD.txt` | `mpc_release_20240125.txt` |
| Governor Speeches | `bog_speech_YYYYMMDD_topic.txt` | `bog_speech_20230810_inflation.txt` |
| Policy Reports | `bog_report_YYYYMM.txt` | `bog_report_202401.txt` |

### Processed Data

| Data Type | Naming Convention | Example |
|-----------|-------------------|---------|
| MPSI Scores | `[source]_mpsi.csv` | `us_fed_mpsi.csv` |
| Metadata | `[source]_metadata.csv` | `us_fed_metadata.csv` |
| Analysis Results | `[module]_[analysis].csv` | `market_impact_correlation.csv` |

---

## Data Collection Tracking

### US Federal Reserve (Target: 250-280 documents)

| Document Type | Target Count | Priority | Time Estimate | Status |
|---------------|--------------|----------|---------------|--------|
| FOMC Statements | 40 (8/year × 5 years) | ⭐⭐⭐ Critical | 2-3 hours | ⬜ Pending |
| FOMC Minutes | 40 | ⭐⭐⭐ High | 4-5 hours | ⬜ Pending |
| Fed Chair Speeches | 80-100 | ⭐⭐ High | 6-8 hours | ⬜ Pending |
| Monetary Policy Reports | 10 (2/year × 5 years) | ⭐⭐ Medium | 1-2 hours | ⬜ Pending |
| Fed Governor Speeches | 40-50 | ⭐ Medium | 4-6 hours | ⬜ Pending |
| Press Conference Transcripts | 40 | ⭐ Medium | 4-5 hours | ⬜ Pending |
| **TOTAL US** | **250-280** | | **~16-20 hours** | |

### Ghana Bank of Ghana (Target: 70-85 documents)

| Document Type | Target Count | Priority | Time Estimate | Status |
|---------------|--------------|----------|---------------|--------|
| MPC Press Releases | 30-35 (6-7/year × 5 years) | ⭐⭐ High | 2-3 hours | ⬜ Pending |
| Governor Speeches | 30-40 | ⭐ Medium | 3-4 hours | ⬜ Pending |
| Monetary Policy Reports | 10 (2/year × 5 years) | ⭐ Medium | 1-2 hours | ⬜ Pending |
| **TOTAL GHANA** | **70-85** | | **~6-9 hours** | |

**Total Data Collection Time: 22-29 hours**

---

## Metadata Schema

### us_fed_metadata.csv

```csv
doc_id,date,year,doc_type,source,url,filename,text_length,word_count,speaker,event_type,fomc_decision,notes
1,2024-01-31,2024,fomc_statement,fomc,https://...,fomc_statement_20240131.txt,2847,489,FOMC,"Regular Meeting","Held rates at 5.25-5.50%",""
2,2024-01-31,2024,press_conference,fomc,https://...,press_conf_20240131.txt,15234,2567,"Jerome Powell","Post-FOMC Press Conference","",""
```

### ghana_bog_metadata.csv

```csv
doc_id,date,year,doc_type,source,url,filename,text_length,word_count,speaker,event_type,mpc_decision,notes
1,2024-01-25,2024,mpc_release,bog,https://...,mpc_release_20240125.txt,1823,312,MPC,"MPC Meeting","Raised rate to 29%",""
```

### MPSI Scores Schema (us_fed_mpsi.csv)

```csv
doc_id,date,year,doc_type,filename,mpsi_score,hawkish_prob,dovish_prob,neutral_prob,confidence,stance_label,text_snippet
1,2024-01-31,2024,fomc_statement,fomc_statement_20240131.txt,32.5,0.663,0.337,0.124,0.89,moderately_hawkish,"Recent indicators suggest..."
```

---

## Quick Start Commands

### 1. Create Directory Structure
```bash
# Already created with mkdir commands above
```

### 2. Start Data Collection
```bash
# Automated collection (FOMC statements)
python collect_fed_statements.py

# Check what was collected
ls -lh data/us_fed/fomc_statements/
cat data/us_fed/fomc_statements/metadata.csv
```

### 3. Calculate MPSI Scores
```bash
# After collecting documents
python calculate_mpsi.py --source us_fed --input data/us_fed/ --output data/processed/mpsi_scores/

# For Ghana documents
python calculate_mpsi.py --source ghana_bog --input data/ghana_bog/ --output data/processed/mpsi_scores/
```

### 4. Run Analysis Modules
```bash
# US market impact analysis
python us_market_impact_analysis.py --mpsi data/processed/mpsi_scores/us_fed_mpsi.csv --output results/us_analysis/market_impact/

# US economic indicators analysis
python us_economic_indicators_analysis.py --mpsi data/processed/mpsi_scores/us_fed_mpsi.csv --output results/us_analysis/economic_indicators/
```

---

## Data Sources & URLs

### US Federal Reserve

| Source | URL | Notes |
|--------|-----|-------|
| FOMC Calendars | https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm | Years 2020-2024 |
| Fed Speeches | https://www.federalreserve.gov/newsevents/speeches.htm | Filter by speaker |
| Monetary Policy Reports | https://www.federalreserve.gov/monetarypolicy/mpr_default.htm | Semi-annual |
| Press Conferences | https://www.federalreserve.gov/mediacenter/fomcpresconf.htm | Post-FOMC |
| FRED Economic Data | https://fred.stlouisfed.org/ | API available |

### Ghana Bank of Ghana

| Source | URL | Notes |
|--------|-----|-------|
| MPC Press Releases | https://www.bog.gov.gh/monetary-policy/ | Meeting outcomes |
| Governor Speeches | https://www.bog.gov.gh/news/speeches/ | Select major speeches |
| Policy Reports | https://www.bog.gov.gh/publications/ | Semi-annual |

---

## Data Quality Checklist

### Before MPSI Calculation:

- [ ] All files follow naming conventions
- [ ] Metadata CSVs populated with dates, sources, URLs
- [ ] Text files cleaned (no HTML tags, proper encoding)
- [ ] Duplicate documents removed
- [ ] File counts match targets (70/30 split maintained)
- [ ] US documents: 250-280 (minimum 200)
- [ ] Ghana documents: 70-85 (minimum 50)

### After MPSI Calculation:

- [ ] MPSI scores within valid range [-100, +100]
- [ ] Confidence scores > 0.7 for most documents
- [ ] No missing values in mpsi_score column
- [ ] Stance labels consistent with scores
- [ ] Time series visualization shows reasonable patterns
- [ ] Metadata matches between raw files and MPSI scores

---

## NIW EB2 Documentation

This data structure supports the NIW EB2 application by:

1. **70/30 Split Evidence**: Clear directory separation shows US emphasis
2. **Comprehensive Coverage**: 250+ US Fed documents demonstrate thorough analysis
3. **Systematic Organization**: Professional data management shows technical competency
4. **Reproducibility**: Clear documentation enables independent verification
5. **US Focus**: Primary analysis results stored separately from comparative work

---

## Next Steps

1. **This Week:**
   - [ ] Run `collect_fed_statements.py` to collect FOMC statements (40 docs)
   - [ ] Verify files in `data/us_fed/fomc_statements/`
   - [ ] Review metadata CSV for completeness

2. **Next 2 Weeks:**
   - [ ] Collect FOMC minutes (40 docs)
   - [ ] Collect Powell speeches (80-100 docs)
   - [ ] Begin Ghana BoG collection (30-35 MPC releases)

3. **Month 1-2:**
   - [ ] Complete all US Fed collection (250+ docs)
   - [ ] Complete Ghana BoG collection (70+ docs)
   - [ ] Calculate MPSI scores for all documents
   - [ ] Create time series visualizations

---

## Contact & Maintenance

**Last Updated:** January 11, 2026
**Maintained By:** MPSI Project Team
**Purpose:** NIW EB2 Immigration Petition - US National Interest Research

For questions about data collection or structure, refer to:
- [US_FOCUSED_PROJECT_PLAN.md](../US_FOCUSED_PROJECT_PLAN.md)
- [collect_fed_statements.py](../collect_fed_statements.py)
- [MPSI_Research_Paper.md](../MPSI_Research_Paper.md)
