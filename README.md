# Automated Monetary Policy Sentiment Index (MPSI)

A hybrid NLP framework combining a FinBERT transformer with Taylor Rule-grounded keyword scoring to measure Federal Reserve communication stance in real time.

## Paper

Dompreh, F. (2026). *Automated Monetary Policy Sentiment Index (MPSI): A FinBERT-Driven Framework for Interpreting Central Bank Communications in the United States.* SSRN Working Paper 6859459.  
https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6859459

## Dashboard

[https://fedmpsi.com](https://fedmpsi.com) — live interactive visualization of MPSI scores (2020–2026)

## Key Results

Reproduced from this repository (`bash replication/run_all.sh`):

- **r = 0.689** between the monthly MPSI and the Federal Funds Rate over the paper's 47 months (p < 0.001, R² = 0.475)
- **r = 0.60** over all 55 months that have a document, using FRED data

Under revision, because the scripts added here do not reproduce them:

- The paper reports that MPSI Granger-causes FFR changes 2–3 months ahead. `replication/granger_ffr.py` finds no such lead, and finds instead that past rate changes predict the index.
- The paper reports a 42.3 bps response of the 2-year Treasury yield to a 10-point MPSI surprise. `replication/yield_event_study.py` finds a response between −0.1 and +2.7 bps, not statistically different from zero.
- The benchmark comparison (Romer-Romer, Hansen-McMahon, Taylor Rule) and the weight-sensitivity analysis do not yet have scripts.

In short, the published index describes the policy stance but has not been shown to lead it. See [REPLICATION.md](REPLICATION.md) for the status of each claim and [ROADMAP.md](ROADMAP.md) for the work in progress on a second version.

## Method

The MPSI uses a two-component hybrid architecture:

| Component | Weight | Role |
|-----------|--------|------|
| Policy Keyword Scorer (Taylor Rule-grounded dictionary) | 0.70 | Explicit stance detection |
| FinBERT (`ProsusAI/finbert`) | 0.30 | Contextual tone & negation |

**Final formula:** `MPSI_t = 0.70 × Keyword_t + 0.30 × FinBERT_t`, on a scale of −100 (most dovish) to +100 (most hawkish); |MPSI| ≤ 10 is Neutral.

Weights are derived from the information-theoretic minimum-variance estimator (precision weighting), confirmed by sensitivity analysis across 119 Fed documents spanning 2020 Q1–2026 Q1.

## Installation

```bash
pip install -r requirements.txt
```

## Quick Usage

```python
from models.mpsi_calculator import HybridMPSICalculator

calc = HybridMPSICalculator()
result = calc.calculate_hybrid_mpsi("The Committee decided to raise the target range...")
print(result)
# {'mpsi_score': ..., 'keyword_mpsi': ..., 'finbert_mpsi': ..., 'stance': 'Hawkish', ...}
```

## Repository Structure

```
MPSI/
├── models/
│   └── mpsi_calculator.py      ← core MPSI hybrid scorer
├── routes/                     ← Flask Blueprint API routes
├── utils/
│   ├── helpers.py
│   └── fed_fetcher.py          ← live Fed document fetcher
├── templates/                  ← dashboard HTML templates
├── data/
│   └── processed/
│       └── mpsi_hybrid_scores.csv   ← 119-document scored corpus
├── app.py                      ← Flask application factory
├── config.py
├── validate_mpsi.py            ← negation and known-event spot checks
├── replication/                ← reproduces the paper's scores and FFR results
│   ├── paper_v1.py             ← frozen scorer used for the paper
│   ├── corpus/                 ← Fed document texts + checksum manifest
│   └── ffr_validation.py
├── tests/
└── requirements.txt
```

## Data

119 Fed documents (2020 Q1–2026 Q1):

| Type | Documents |
|---|---|
| FOMC Statements | 53 |
| FOMC Minutes (incl. Jan 2026 press conference) | 51 |
| Chair Speeches (Jackson Hole) | 6 |
| Economic Outlook speeches | 9 |

The texts are in `replication/corpus/us_fed/`, with checksums in `replication/corpus/MANIFEST.csv`.

Note: the dashboard scorer in `models/mpsi_calculator.py` is a later version (weighted keywords, tanh normalisation). It gives different numbers from the published scores in `data/processed/mpsi_hybrid_scores.csv`, which come from `replication/paper_v1.py`. Set `MPSI_FINBERT_MODEL` to use a different FinBERT checkpoint.

## Citation

```bibtex
@techreport{dompreh2026mpsi,
  title   = {Automated Monetary Policy Sentiment Index ({MPSI}):
             A {FinBERT}-Driven Framework for Interpreting
             Central Bank Communications in the {United States}},
  author  = {Dompreh, Foster},
  year    = {2026},
  institution = {University of Wisconsin--Madison},
  type    = {SSRN Working Paper},
  number  = {6859459},
  url     = {https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6859459}
}
```

## License

MIT License — see [LICENSE](LICENSE) file.

---

*ORCID: [0009-0003-2566-2238](https://orcid.org/0009-0003-2566-2238) · SSRN: 6859459 · Dashboard: fedmpsi.com*
