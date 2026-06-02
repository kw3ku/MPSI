# MPSI Paper — Official Statistics Reference
> Source: Dompreh (2026) — Final Paper May 2026

---

## Core Validation Statistics

| Metric | Value | Table/Section |
|---|---|---|
| Pearson r (MPSI vs FFR) | **0.689** | Table 15 |
| R-squared | **0.475** | Table 15 |
| p-value | **< 0.001** | Table 15 |
| Regression slope (β₁) | **0.102** | Table 15 |
| Regression intercept (β₀) | **3.320** | Table 15 |
| Regression equation | FFR = 3.320 + 0.102 × MPSI | Table 15 |
| Sample (months) | **74** | Table 15 |
| Sample (documents) | **119** unique (228 collected) | Table 3 |
| Period | **2020.Q1 – 2026.Q1** | Section 4.2 |

---

## Out-of-Sample Performance (Table 11)

| Period | r₆ | DA₆ (%) | IC | p-value |
|---|---|---|---|---|
| 2022 — inflation surge | 0.78 | 83.3 | 0.75 | 0.002 |
| 2023 — policy pause | 0.71 | 75.0 | 0.68 | 0.008 |
| 2024–2026 — normalization | 0.69 | 81.7 | 0.71 | 0.001 |
| **Overall 2022–2026** | **0.73** | **80.0** | **0.71** | **<0.001** |

---

## Lead-Lag Analysis (Section 5.3)

| Lag | r | Interpretation |
|---|---|---|
| –6 months | 0.194 | FFR leads MPSI |
| –3 months | 0.363 | FFR leads MPSI |
| 0 months | 0.601 | Concurrent |
| +2–3 months | **Peak** | MPSI leads FFR — optimal predictive window |

> Note: Paper states correlation **peaks at 2–3 month forward lag** (Section 5.3).
> Figure 6 caption states "Maximum r = 0.808 at lag -6" — this appears to be
> a figure label inconsistency. Use **Section 5.3 text** for NIW purposes: peak at +2–3 months.

---

## Granger Causality Tests (Table 18)

| Null Hypothesis | F-stat | p-value | Conclusion |
|---|---|---|---|
| MPSI does NOT Granger-cause ΔFFR | 8.42 | < 0.001*** | **Reject** |
| ΔFFR does NOT Granger-cause MPSI | 1.73 | 0.168 | Fail to reject |
| MPSI does NOT Granger-cause Market Exp. | 6.18 | 0.002** | **Reject** |
| Market Exp. does NOT Granger-cause MPSI | 2.33 | 0.082 | Fail to reject |

---

## Event Study Results (Table 19)

| Market Variable | β (per 10-pt MPSI surprise) | t-stat | R² |
|---|---|---|---|
| 2-Year Treasury Yield | **+42.3 bps** | 5.82 | 0.41 |
| 10-Year Treasury Yield | **+28.7 bps** | 4.11 | 0.28 |
| S&P 500 Return | **–5.2%** | –2.34 | 0.11 |
| VIX Change | +1.18 pts | 2.01 | 0.08 |

---

## Model Diagnostics (Section 5.7)

| Test | Statistic | Result |
|---|---|---|
| Breusch-Pagan (homoscedasticity) | χ² = 2.14, p = 0.14 | ✅ Pass |
| Shapiro-Wilk (normality) | W = 0.976, p = 0.08 | ✅ Pass |
| Durbin-Watson (autocorrelation) | 1.89 | ✅ Pass |
| Mean residual | 0.02 | ✅ No bias |

---

## Benchmark Comparison (Table 20)

| Method | r with FFR | R² | Lead (months) |
|---|---|---|---|
| **MPSI Hybrid** | **0.689*** | **0.475** | **2–3** |
| Loughran-McDonald | 0.482** | 0.232 | 0 |
| VADER | 0.413** | 0.171 | 0 |
| Generic FinBERT | 0.587*** | 0.345 | 1 |
| Keywords Only | 0.621*** | 0.386 | 2 |
| FinBERT Only | 0.534** | 0.285 | 1 |
| Shadow Rate (Wu-Xia) | 0.756*** | 0.572 | N/A |
| Taylor Rule | 0.691*** | 0.477 | 0 |

> MPSI outperforms all text-based methods.
> MPSI competitive with Taylor Rule but provides **2–3 month lead time**.

---

## Ablation Study (Table 13)

| Configuration | r₆ | DA₆ (%) |
|---|---|---|
| Keywords only (wK = 1.0) | 0.65 | 75.0 |
| FinBERT only (wF = 1.0) | 0.51 | 65.0 |
| Equal weights (0.5/0.5) | 0.69 | 73.3 |
| **Optimal weights (0.70/0.30)** | **0.73** | **80.0** |

---

## FinBERT Performance (Table 9)

| Metric | Hawkish | Neutral | Dovish |
|---|---|---|---|
| Precision | 0.89 | 0.76 | 0.87 |
| Recall | 0.85 | 0.81 | 0.83 |
| F1-Score | 0.87 | 0.78 | 0.85 |
| **Overall Accuracy** | | **84.2%** | |
| **Macro F1** | | **0.833** | |

---

## Signal Quality & Optimal Weights (Table 10)

| Component | βᵢ | σ²ᵤ | SNR |
|---|---|---|---|
| Keyword (SK) | 0.0284*** | 520/1.12 | 2.34 |
| FinBERT (SF) | 0.0189*** | 320/1.58 | 0.98 |
| **Implied weights** | **w*K = 0.70** | **w*F = 0.30** | |

> Empirical variance estimates: σ²K = 0.036, σ²F = 0.074

---

## MPSI Summary by Year (Table 16)

| Year | N | Mean | Median | SD | Min | Max |
|---|---|---|---|---|---|---|
| 2020 | 48 | –26.8 | –27.1 | 10.2 | –48.2 | –5.3 |
| 2021 | 42 | –19.7 | –19.9 | 9.5 | –36.8 | –2.1 |
| 2022 | 48 | +5.8 | +6.2 | 12.8 | –21.3 | +26.4 |
| 2023 | 52 | +13.4 | +13.2 | 8.7 | –5.2 | +25.1 |
| 2024 | 48 | –10.3 | –10.8 | 9.1 | –28.5 | +8.7 |
| 2025 | 38 | –13.6 | –14.2 | 7.8 | –27.4 | +3.9 |
| 2026 | 8 | –18.2 | –16.5 | 12.4 | –48.7 | –7.8 |
| **Overall** | **284** | **–7.9** | **–6.2** | **17.6** | **–48.7** | **+26.4** |

---

## MPSI by Document Type (Table 17)

| Document Type | N | Mean MPSI | Stance |
|---|---|---|---|
| FOMC Minutes | 48 | –12.8 | Most Dovish |
| Fed Chair Speeches | 38 | –9.2 | Moderately Dovish |
| FOMC Statements | 96 | –3.2 | Neutral-Dovish |
| Economic Outlook | 102 | –1.8 | Neutral |

---

## Performance by Document Type (Table 14)

| Document Type | N | r₆ | DA₆ (%) |
|---|---|---|---|
| FOMC Statements | 48 | 0.81 | 85.4 |
| FOMC Minutes | 48 | 0.72 | 77.1 |
| Chair Speeches | 72 | 0.68 | 76.4 |
| Monetary Policy Reports | 12 | 0.75 | 83.3 |

---

## Welfare: Term Premia Effect (Table 21)

| Variable | Coefficient | Interpretation |
|---|---|---|
| \|MPSI\| | **–0.018*** | 10-pt clearer signal → **–18 bps term premium** |
| VIX | +0.032*** | Volatility raises premia |
| ΔCPI | +0.104** | Inflation raises premia |
| R² | 0.562 | |

> Economic magnitude: During peak tightening (MPSI = +25),
> term premia ~45 bps lower → ~**$12 billion** reduced Treasury borrowing costs annually.

---

## Financial Markets Application (Section 6.2)

- **Predictive lead**: 2–3 months
- **Backtested Sharpe ratio**: **0.82** (2020–2024 bond strategy)
- **MPSI parsed within**: 30 seconds of FOMC release

---

## Data Sources (Tables 3 & 4)

| Document Type | Count | Source |
|---|---|---|
| FOMC Statements | 48 | federalreserve.gov/monetarypolicy |
| FOMC Minutes | 48 | Federal Reserve Board |
| Chair Speeches | 72 | BIS Central Bank Speeches Database |
| Monetary Policy Reports | 12 | Congressional Testimony |
| **Total (after dedup)** | **119** | |

| Variable | FRED Code | Frequency |
|---|---|---|
| Federal Funds Rate | DFF | Daily |
| CPI Inflation (YoY) | CPIAUCSL | Monthly |
| Unemployment Rate | UNRATE | Monthly |
| 10-Year Treasury Yield | DGS10 | Daily |
| Core PCE Inflation | PCEPILFE | Monthly |

---

## Hybrid Formula (Official)

```
MPSIt = 0.70 × Keywordt + 0.30 × FinBERTt

Keywordt   = 100 × tanh(Weighted Score / σ_score)
FinBERTt   = (1/Nt) × Σ sⱼ × 100
```

---

## MPSI Score Interpretation Scale (Section 4.5.2)

| MPSI Range | Stance |
|---|---|
| > +50 | Strongly Hawkish — aggressive tightening |
| +10 to +50 | Moderately Hawkish |
| –10 to +10 | Neutral |
| –50 to –10 | Moderately Dovish |
| < –50 | Strongly Dovish — aggressive easing |

---

## NIW Key Claims — Paper-Backed

| Claim | Evidence | Location |
|---|---|---|
| Outperforms all text-based benchmarks | r=0.689 vs next best 0.621 | Table 20 |
| Predicts Fed action 2–3 months ahead | Peak lead-lag correlation | Section 5.3 |
| Granger-causes FFR changes | F=8.42, p<0.001 | Table 18 |
| 80% out-of-sample directional accuracy | DA=80%, p<0.001 | Table 11 |
| Reduces Treasury term premia | –18 bps per 10-pt clarity | Table 21 |
| Market impact confirmed | +42.3 bps 2Y yield per surprise | Table 19 |
| Open-source + live dashboard | github.com/kw3ku/MPSI + fedmpsi.com | Section 7.1 |

---

*Dompreh, F. (2026). Automated Monetary Policy Sentiment Index (MPSI):
A FinBERT-Driven Framework for Interpreting Central Bank Communications
in the United States. May 2026.*