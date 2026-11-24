# MPSI Replication Guide

This document records how the scores and validation results in

> Dompreh, F. (2026). *Automated Monetary Policy Sentiment Index (MPSI): A FinBERT-Driven Framework for Interpreting Central Bank Communications in the United States.* SSRN Working Paper 6859459.

were produced, which of them can be reproduced from this repository, and what is still missing. It was written by tracing the research scripts that generated `data/processed/mpsi_hybrid_scores.csv` and re-running them.

---

## Quick start

```bash
pip install -r requirements.txt

bash replication/run_all.sh          # keyword scores + validation + tests (no FinBERT, ~30 s)
bash replication/run_all.sh --full   # also re-runs FinBERT on all documents (~440 MB model download, ~12 min on CPU)
```

Expected output of the validation step:

```
              spec  n_months   first    last      r  r_squared  ols_slope
 A_paper_handcoded        47 2020-01 2025-03 0.6893     0.4752     0.1016
B_fred_same_months        47 2020-01 2025-03 0.6808     0.4635     0.1009
 C_fred_all_months        55 2020-01 2026-01 0.6014     0.3616     0.0890
```

Row A is the paper's result (r = 0.689, R² = 0.475, slope = 0.102).

---

## What is in `replication/`

| Path | Purpose |
|---|---|
| `paper_v1.py` | Frozen copy of the scorer that produced the published CSV. The two classes are verbatim from the research script `01-mpsi_hybrid.py`; adds a `--keywords-only` mode that needs no torch. |
| `verify_scores.py` | Checks corpus checksums, rebuilt keyword columns, the 70/30 hybrid identity, and (if rebuilt) the FinBERT column against the published CSV. |
| `ffr_validation.py` | Monthly MPSI vs Fed Funds Rate: correlation table (specs A–C) and lead/lag table. |
| `granger_ffr.py` | Granger tests between monthly MPSI and ΔFFR, lags 1–6, four specifications. |
| `yield_event_study.py` | 2-year Treasury yield response to MPSI surprises on FOMC statement days (three surprise definitions, two windows). |
| `fetch_fred.py` | Downloads a fresh copy of FRED series `DFF`. |
| `run_all.sh` | Runs everything above plus `pytest tests/`. |
| `corpus/us_fed/` | 118 of the 119 scored Fed documents (plain text). |
| `corpus/MANIFEST.csv` | All 119 documents with SHA-256, word count, and notes. |
| `data/fed_funds_paper_handcoded.csv` | The monthly Fed Funds table typed into the research script `03-validate_mpsi_fix.py` (2020-01 to 2025-04). This is the series behind the paper's r = 0.689. |
| `data/fred_dff_snapshot_2026-03-19.csv` | FRED `DFF` (daily effective FFR) as downloaded on 2026-03-19, kept so results do not drift. |
| `data/fred_dgs2_snapshot_2026-11-22.csv` | FRED `DGS2` (daily 2-year Treasury yield) as downloaded on 2026-11-22. |
| `output/` | Generated files (git-ignored). |

---

## The process, step by step

### 1. Corpus collection

Documents were saved as UTF-8 text from federalreserve.gov into four folders:

| Folder | `doc_type` | Docs | File-name date? |
|---|---|---|---|
| `fomc_statements/` | FOMC Statements | 53 | yes (`fomc_st_YYYYMMDD`) |
| `fomc_minutes/` | FOMC Minutes | 51 | yes (`fomc_min_YYYYMMDD`) |
| `fed_chair_speeches/` | Fed Chair Speeches | 6 | no |
| `economic_outlook/` | Economic Outlook | 9 | no |

119 documents in total; files under 50 words are skipped (one empty file, `fomc_st_2023.txt`, was dropped this way).

Not redistributed: `fed_chair_speeches/jackson_hole_2021.txt` is a third-party transcript (timestamped, includes the Kansas City Fed president's introduction), not the federalreserve.gov text. Its checksum is in the manifest; the replication reports 118/119 for that reason. The official text of the same speech is on federalreserve.gov (27 Aug 2021).

### 2. Scoring each document (`paper_v1.py`)

For each document *t*:

1. **Keyword score.** For each of three phrase lists (29 hawkish, 30 dovish, 14 neutral), count how many distinct phrases appear anywhere in the lower-cased text (substring test: presence, not frequency).

   Keyword_t = 100 × (H_t − D_t) / (H_t + D_t + N_t), or 0 if no phrase appears.

2. **FinBERT score.** Split the text into 400-word chunks with 200-word overlap (chunks ≤ 50 words dropped; at most 10 chunks, evenly sampled). Run stock `ProsusAI/finbert` on each chunk (truncated at 512 tokens), average the class probabilities.

   FinBERT_t = 100 × (P(positive) − P(negative))

3. **Hybrid.** MPSI_t = 0.70 × Keyword_t + 0.30 × FinBERT_t; if no keyword phrase appears, MPSI_t = FinBERT_t.

4. **Stance.** Hawkish if MPSI > 10, Dovish if MPSI < −10, else Neutral. Scale is −100 to +100 (published range −45.5 to +26.1).

5. **Date.** Taken from an 8-digit `YYYYMMDD` in the file name; documents without one get no date.

### 3. Validation against the Fed Funds Rate (`ffr_validation.py`)

1. Drop undated documents. This leaves the 104 FOMC statements and minutes; the 15 speeches and outlook documents do not enter the time series.
2. Average MPSI within each calendar month (55 months, 2020-01 to 2026-01).
3. Pair with the monthly Fed Funds Rate and compute Pearson r, R², two-sided t-test p-value, and the OLS slope of FFR on MPSI.

---

## Reproduction status

| Claim | Status | Notes |
|---|---|---|
| 119 scored documents | ✅ reproduced | 118 redistributed + 1 verified by checksum. |
| Keyword columns (counts, word counts, Keyword_t) | ✅ exact, 118/118 | `verify_scores.py` step 2. |
| FinBERT column | ✅ exact, 118/118 (max difference 0.00) | Requires `--full`; stock `ProsusAI/finbert`, transformers 4.39.3, torch 2.2.2. About 12 min on a CPU-only Intel i7 Mac mini. |
| MPSI = 0.70 × Keyword + 0.30 × FinBERT | ✅ 119/119 | |
| r = 0.689, R² = 0.475, slope 0.102, p < 0.001 | ✅ exact | Spec A: 47 months, hand-entered FFR. |
| MPSI leads FFR by 2–3 months; Granger causality (F = 8.42, p < 0.001) | ❌ not reproduced | No original script found. `granger_ffr.py` gives F between 0.03 and 1.80 (p ≥ 0.16) for MPSI → ΔFFR at every lag 1–6 in every specification; the reverse direction is significant. See below. |
| 10-point MPSI surprise → 42.3 bps on 2-year Treasury (t = 5.82, R² = 0.41) | ❌ not reproduced | No original script or surprise definition found. `yield_event_study.py` gives −0.1 to +2.7 bps per 10 points, |t| ≤ 1.3, R² ≤ 0.03 across all definitions tried. See below. |
| Outperforms Romer-Romer, Hansen-McMahon, Taylor Rule | ⚠️ not reproducible from this repo | No benchmark-comparison code found. |
| Weight sensitivity (w_K = 0.5…0.9, peak at 0.70) | ⚠️ not reproducible from this repo | Table appears in notes; no generating script found. |

### Lead/lag (FRED DFF, full monthly calendar)

corr(MPSI_t, FFR_{t+k}); k > 0 means MPSI leads.

| k | −6 | −3 | −1 | 0 | +1 | +2 | +3 | +4 | +5 | +6 |
|---|---|---|---|---|---|---|---|---|---|---|
| r | 0.22 | 0.42 | 0.54 | 0.60 | 0.64 | 0.68 | 0.73 | 0.76 | 0.77 | 0.79 |

The correlation keeps rising through k = 6 rather than peaking at 2–3 months. Both series are highly persistent in levels over 2020–2026 (one easing-hiking-holding cycle), so a level correlation that grows with the lead is expected and is not by itself evidence of predictive content. A Granger test on changes (ΔFFR) with lag selection is the appropriate check.

### Granger causality (`granger_ffr.py`)

Monthly calendar, FRED DFF monthly mean, MPSI carried forward through the 18 of 72 months with no dated document, all lag orders estimated on 2020-08 to 2026-01 (n = 66). The paper does not state its lag order or sample.

| Lags | 1 | 2 | 3 | 4 | 5 | 6 | Paper |
|---|---|---|---|---|---|---|---|
| MPSI → ΔFFR, F | 0.03 | 0.07 | 1.55 | 1.08 | 1.19 | 0.98 | 8.42 |
| p | 0.87 | 0.93 | 0.21 | 0.38 | 0.33 | 0.45 | < 0.001 |
| ΔFFR → MPSI, F | 7.32 | 4.49 | 4.88 | 4.63 | 4.68 | 4.56 | 1.73 |
| p | 0.009 | 0.015 | 0.004 | 0.003 | 0.001 | 0.001 | 0.168 |

BIC selects 1 lag and AIC 5 lags for MPSI → ΔFFR. The pattern is the reverse of the paper's Table 18: lagged MPSI does not help predict rate changes, while lagged rate changes do help predict MPSI. The same holds with statements only, with MPSI in first differences (reverse direction weaker, p = 0.006 to 0.11), and with the paper's hand-entered FFR table. The F-statistics match `statsmodels.tsa.stattools.grangercausalitytests` on the same sample.

### 2-year yield event study (`yield_event_study.py`)

Events are the dated documents under `fomc_statements/` (52 usable; 46 after dropping six that are not scheduled post-meeting statements). The yield change is the FRED `DGS2` close-to-close change in basis points. The paper does not define an MPSI surprise, so three definitions are reported.

| Surprise | Window | n | bps per 10 points | t (OLS) | R² |
|---|---|---|---|---|---|
| change from previous statement | 1 day | 52 | 0.95 | 0.70 | 0.010 |
| change from previous statement | 2 days | 52 | 2.38 | 1.24 | 0.030 |
| deviation from mean of previous 3 | 1 day | 50 | 0.18 | 0.15 | 0.000 |
| deviation from mean of previous 3 | 2 days | 50 | 1.30 | 0.73 | 0.011 |
| AR(1) residual | 1 day | 52 | 0.18 | 0.13 | 0.000 |
| AR(1) residual | 2 days | 52 | 0.97 | 0.48 | 0.005 |
| **Paper Table 19** | | | **42.3** | **5.82** | **0.41** |

The mean absolute statement-to-statement change in MPSI is 6.0 points and the mean absolute 1-day move in the 2-year yield on these days is 6.4 bps. A coefficient of 42.3 bps per 10 points would imply typical moves of about 25 bps.

---

## Differences between the paper text and the code that produced its numbers

These are listed so readers and reviewers are not surprised; deciding how to resolve them is up to the author.

1. **FinBERT is not fine-tuned in the published scores.** The paper describes FinBERT fine-tuned on 1,500 Fed sentences. Both the research script and this repository load the stock `ProsusAI/finbert` checkpoint. The local fine-tuned checkpoints were not used to produce `mpsi_hybrid_scores.csv`. They were trained from `yiyanghkust/finbert-tone` (not `ProsusAI/finbert`) on `fin_data.csv`, which has the size and label mix of the Financial PhraseBank (4,846 company-news sentences), not Fed text.
2. **Keyword weighting (paper Eq. 4–5) is not what produced the numbers.** The paper describes ω_w-weighted keyword counts with tanh normalisation. The published scores use the unweighted ratio (H − D)/(H + D + N) above. The weighted/tanh version is implemented in `models/mpsi_calculator.py` (the dashboard scorer), which therefore gives different scores from the paper.
3. **Hybrid weights.** The paper and `paper_v1.py` use exactly 0.70/0.30. `models/mpsi_calculator.py` computes 0.074/0.110 = 0.673 and 0.327 without rounding.
4. **Fed Funds data and sample window.** The paper's correlation uses a hand-entered monthly table that ends in 2025-04 (so the sample stops at 2025-03, 47 months). Four months differ from FRED by more than 10 bp (2024-09: 4.83 vs 5.13; 2024-12: 4.33 vs 4.48; 2025-03 and 2025-04: 4.08 vs 4.33). With FRED over the same months r = 0.681; over every month with data (through 2026-01) r = 0.601. The paper's statistics reference gives the sample as 74 months, but the reported r, slope (0.102) and intercept (3.320) are reproduced only by the 47-month sample. The paper's lead/lag table starts from r = 0.601 at lag 0, which is the full-sample FRED value, so the two tables use different samples.

---

## Known data and method limitations

- **Substring matching.** Keywords are matched as substrings, so dovish `ease` fires inside "increase", "decrease" and "release". In this corpus `ease` is counted in 102 of 118 documents, but the word "ease" appears in only 38. This biases Keyword_t toward dovish. Overlapping phrases also double-count: "restrictive" fires both `restrict` and `restrictive`, "inflation risks" fires both `inflation risk` and `inflation risks`. Pinned by `tests/test_paper_v1.py::test_known_limitation_ease_substring`.
- **Presence, not frequency.** Repeating a phrase does not change the score.
- **Undated documents excluded from the time series.** All 15 speeches and outlook documents have no date in their file names, so only statements and minutes enter the monthly analysis.
- **Duplicate document.** `economic_outlook/rv_ec_out_2024.txt` is byte-identical to `fed_chair_speeches/jackson_hole_2024.txt`.
- **Minutes are dated by meeting date, not release date.** FOMC minutes are published about three weeks after the meeting, so assigning them to the meeting month uses information before it was public. This matters for any lead/forecast claim.
- **Misdated statement.** `fomc_statements/fomc_st_20211216.txt` contains a 2020 pandemic-era statement, not a December 2021 one; the file-name date puts it in the wrong month of the time series.
- **Mixed document types under `fomc_minutes/`.** It includes the 2026-01-28 press conference and transcript files.

---

## Using a fine-tuned FinBERT in the dashboard

`models/mpsi_calculator.py` reads the checkpoint from `MPSI_FINBERT_MODEL` (default `ProsusAI/finbert`):

```bash
export MPSI_FINBERT_MODEL=kw3ku/mpsi-finbert     # Hugging Face id, or a local folder
```

Probabilities are mapped by label name from the model's `id2label`, so checkpoints with a different label order work, **provided `id2label` in their `config.json` is correct**. Check this before using a local checkpoint. The local `financial_sentiment_model/` and `models/checkpoint-500/` were trained with `negative = 0, neutral = 1, positive = 2`, but their configs still carry the base model's `0 = Neutral, 1 = Positive, 2 = Negative`; fix `id2label`/`label2id` before use. The `finbert_finetuned/` copies already have the correct mapping. `paper_v1.py` is unaffected and always uses the stock model.

To publish the fine-tuned model: `huggingface-cli login`, then `huggingface-cli upload kw3ku/mpsi-finbert <local_model_dir>`.

---

## Still to do

- [x] Add a Granger-causality script (ΔFFR on lagged MPSI, with lag selection). Done: `granger_ffr.py`; it does not reproduce the paper's Table 18.
- [x] Add a 2-year Treasury event study (FRED `DGS2`). Done: `yield_event_study.py`; it does not reproduce the paper's Table 19.
- [ ] Locate the original code or specification (lag order, sample, surprise definition, event window) behind Tables 18 and 19, or revise those claims in the paper and README.
- [ ] Add the benchmark comparison (Romer-Romer, Hansen-McMahon, Taylor Rule) and the weight-sensitivity script.
- [ ] Publish the fine-tuned FinBERT and the 1,500-sentence training set, or state in the paper that the stock model was used.
- [ ] Archive a tagged release on Zenodo for a citable DOI.
