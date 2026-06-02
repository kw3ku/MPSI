# 🎓 MPSI Post-Publication Roadmap
**Foster Dompreh — MS Financial Economics, UW-Madison 2025**
**Published: May 30, 2026**

---

## 📄 Your Paper Is Live

```
Title:    Automated Monetary Policy Sentiment Index (MPSI):
          A FinBERT-Driven Framework for Interpreting
          Central Bank Communications in the United States

SSRN ID:  6859459
URL:      https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6859459
GitHub:   https://github.com/kw3ku/MPSI
Dashboard: https://fedmpsi.com
ORCID:    https://orcid.org/0009-0003-2566-2238
Email:    fdompreh@wisc.edu
```

---

## ✅ Fix Before Recompiling LaTeX

### 1. Bibliography Style (fianl_page.tex)
```latex
% FIND:
\bibliographystyle{elsarticle-num}

% REPLACE WITH:
\bibliographystyle{plainnat}
```

### 2. Pipeline Table — Wrong N (fianl_page.tex)
```latex
% FIND:
4 & Deduplicate (Jaccard $\geq 0.85$) & scikit-learn & 119 unique docs \\

% REPLACE WITH:
4 & Deduplicate (Jaccard $\geq 0.85$) & scikit-learn & 168 unique docs \\
```

### 3. tablenotemark — Wrong Command (fianl_page.tex)
```latex
% FIND in tab:structural_breaks and tab:architectures:
\tablenotemark{Note: ...}

% REPLACE WITH:
\begin{tablenotes}
\footnotesize
\item Note: MPSI remains predictive across all three 
      regime breaks, validating cross-regime robustness.
\end{tablenotes}
```

---

## 🔴 Week 1–2: Do These Immediately

### 1. Update GitHub README
```markdown
## Citation
Dompreh, F. (2026). Automated Monetary Policy Sentiment 
Index (MPSI): A FinBERT-Driven Framework for Interpreting 
Central Bank Communications in the United States. 
SSRN Working Paper 6859459.
https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6859459
```

### 2. Update Your CV
```
Dompreh, F. (2026). "Automated Monetary Policy Sentiment 
Index (MPSI)." SSRN Working Paper 6859459.
Available at: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6859459
```

### 3. Check JIMF Status
```
Log into Elsevier Editorial Manager:
https://www.editorialmanager.com/jimf

Check status:
- "With Editor"               → not yet sent to reviewers
- "Under Review"              → reviewers have it
- "Required Reviews Complete" → decision coming soon
```

### 4. Send JIMF Status Inquiry Email
```
To: Handling editor (shown in your portal)
Subject: Status Inquiry — Manuscript [your ID]

Dear Professor [Name],

I am writing to inquire about the status of my 
manuscript submitted approximately six months ago.

Manuscript ID: [your JIMF ID]

Thank you for your time.

Sincerely,
Foster Dompreh
University of Wisconsin - Madison
fdompreh@wisc.edu
```

### 5. Email the Minneapolis Fed Representative
```
Subject: MPSI Working Paper — Follow-up from 
         UW-Madison Talk (2024)

Dear [Dr./Professor Name],

I hope this message finds you well. I attended your 
talk at UW-Madison in 2024 and found your work on 
[mention something specific] particularly insightful.

I am writing to share a working paper I have just 
published that I believe may be of interest:

"Automated Monetary Policy Sentiment Index (MPSI)"
SSRN Working Paper 6859459
https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6859459

Key findings:
→ r = 0.689 correlation with Federal Funds Rate
→ Granger-causes FFR changes 2–3 months ahead
→ Hybrid FinBERT + Taylor Rule architecture
→ Open-source toolkit: github.com/kw3ku/MPSI

I would welcome any feedback or the opportunity 
to discuss the paper. I am also actively exploring 
research positions and would be grateful for any 
guidance you might offer.

Thank you for your time.

Best regards,
Foster Dompreh
MS Financial Economics, UW-Madison 2025
fdompreh@wisc.edu
ORCID: 0009-0003-2566-2238
```

### 6. Email Your Advisor
```
Subject: New Working Paper Published — MPSI

Dear Professor [Name],

I am pleased to share my new working paper:

"Automated Monetary Policy Sentiment Index (MPSI)"
SSRN Working Paper 6859459
https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6859459

The paper develops a hybrid NLP framework combining 
FinBERT transformers with Taylor Rule keywords to 
measure Federal Reserve communication stance.

I would welcome any feedback as I prepare to 
submit to a journal.

Best regards,
Foster Dompreh
```

---

## 📱 Social Media — Post Today

### LinkedIn Post
```
🚀 New working paper out today!

"Automated Monetary Policy Sentiment Index (MPSI): 
A FinBERT-Driven Framework for Interpreting Central 
Bank Communications in the United States"

Key findings:
→ r = 0.689 correlation with Federal Funds Rate
→ Granger-causes FFR changes 2–3 months ahead
→ 10-point MPSI surprise = 42.3 bps yield increase
→ Hybrid FinBERT + Taylor Rule architecture
→ Explains 47.5% of FFR variance

Full paper: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6859459
Code: https://github.com/kw3ku/MPSI
Dashboard: https://fedmpsi.com

#MonetaryPolicy #NLP #FinBERT #FederalReserve 
#Economics #MacroEconomics #CentralBanking
```

### Twitter / X Post (Thread)

**Tweet 1:**
```
🚀 New paper alert!

"Automated Monetary Policy Sentiment Index (MPSI)"

Can we quantify how hawkish or dovish the Fed is 
from their words alone?

Yes — and it predicts rate changes 2–3 months ahead.

Thread 🧵👇

SSRN: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6859459
```

**Tweet 2:**
```
The problem:
Fed communications use domain-specific jargon 
that general NLP tools systematically misread.

"Not restrictive" ≠ hawkish
"Heightened vigilance" ≠ "close monitoring"

Standard sentiment tools miss this entirely. 🧵2/
```

**Tweet 3:**
```
The solution: MPSI

70% Taylor Rule keywords (explicitly mapped to 
inflation gap φπ and output gap φy)

30% Fine-tuned FinBERT (handles negation, 
conditionality, tone shifts)

Weights derived via information-theoretic 
precision weighting. 🧵3/
```

**Tweet 4:**
```
Results on 168 Fed documents (2020–2026):

✅ r = 0.689 with Federal Funds Rate (p<0.001)
✅ Explains 47.5% of FFR variance
✅ Granger-causes FFR changes up to 3 months ahead
✅ 10-pt surprise → 42.3 bps on 2Y Treasury yields
✅ Outperforms benchmarks by 17–67% 🧵4/
```

**Tweet 5:**
```
Three policy eras captured perfectly:

📉 2020–2021: Mean MPSI = -23.3 (dovish)
📈 2022–2023: Mean MPSI = +9.6 (hawkish)  
📊 2024–2026: Mean MPSI = -13.1 (normalizing)

The index turned hawkish 4–6 months before the 
first rate hike in March 2022. 🧵5/
```

**Tweet 6:**
```
Everything is open source:

📄 Paper: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6859459
💻 Code: https://github.com/kw3ku/MPSI
🌐 Dashboard: https://fedmpsi.com

Feedback welcome! 🧵6/6

#MonetaryPolicy #NLP #FinBERT #FederalReserve #FOMC
```

---

## 🟡 Month 1–2: Journal Submission

### Target Journals (In Order)

| Tier | Journal | Fit | Notes |
|------|---------|-----|-------|
| 1 — Stretch | Journal of Monetary Economics (JME) | ⭐⭐⭐⭐⭐ | Best fit |
| 1 — Stretch | Journal of Financial Economics (JFE) | ⭐⭐⭐⭐ | Market impact angle |
| 2 — Target | Journal of Money, Credit and Banking (JMCB) | ⭐⭐⭐⭐⭐ | Perfect fit |
| 2 — Target | Journal of International Money & Finance (JIMF) | ⭐⭐⭐⭐ | You already have paper there |
| 2 — Target | Journal of Macroeconomics | ⭐⭐⭐⭐ | Good fit |
| 3 — Safe | Economics Letters | ⭐⭐⭐ | Fast turnaround |
| 3 — Safe | Finance Research Letters | ⭐⭐⭐ | NLP angle |

### Submission Checklist
```
Before submitting to any journal:
□ Fix bibliography style (elsarticle-num → plainnat)
□ Fix pipeline table (119 → 168)
□ Fix tablenotemark commands
□ Recompile full PDF
□ Check journal word/page limits
□ Prepare cover letter
□ Prepare highlights (3–5 bullet points)
```

### Cover Letter Template
```
Dear Editors,

I am submitting my manuscript "Automated Monetary 
Policy Sentiment Index (MPSI): A FinBERT-Driven 
Framework for Interpreting Central Bank Communications 
in the United States" for consideration.

This paper makes four contributions:
1. Theoretically-grounded hybrid NLP framework 
   anchored to Taylor Rule components
2. Optimal signal fusion via information-theoretic 
   precision weighting (70/30 keyword-FinBERT)
3. Comprehensive validation across three Fed regimes
4. Welfare channel through information revelation

Key results: r = 0.689 with FFR, Granger-causality 
confirmed, 42.3 bps market impact per 10-point surprise.

The paper is available as SSRN Working Paper 6859459.
I confirm this manuscript is not under review elsewhere.

Sincerely,
Foster Dompreh
University of Wisconsin - Madison
fdompreh@wisc.edu
ORCID: 0009-0003-2566-2238
```

---

## 🟡 Month 2–3: Conference Submissions

```
1. AEA Annual Meeting 2027
   Deadline: ~February 2026 ← CHECK NOW
   Submit to: Macroeconomics session

2. Midwest Economics Association 2027
   Deadline: ~October 2026
   Location: Annual meeting

3. Federal Reserve System Committee on 
   Financial Structure & Regulation
   Deadline: ~January 2027

4. Society for Economic Dynamics (SED)
   Deadline: ~February 2027

5. European Economic Association (EEA)
   Deadline: ~February 2027
```

---

## 🟢 Month 3–6: Paper Extensions

### Extension 1: MPSI-Global
```
Extend to ECB, Bank of England, Bank of Japan
Target: Journal of International Economics
Key question: Do weights differ across central banks?
```

### Extension 2: MPSI Real-Time API
```
Build practitioner API
Monetization opportunity
Partner with financial data providers
```

### Extension 3: MPSI + Asset Pricing
```
Use MPSI surprises as pricing factor
Target: Journal of Finance
Key question: Does MPSI carry risk premium?
```

---

## 🟢 Month 6–12: Career Applications

```
With SSRN paper live + journal submission:

Federal Reserve positions:
□ Fed Board of Governors — Research Assistant
□ Federal Reserve Bank of Minneapolis
□ Federal Reserve Bank of New York
□ Federal Reserve Bank of Chicago

International organizations:
□ IMF Young Economist Program
□ World Bank Research Department
□ BIS Research Department

Academia:
□ PhD program applications (if pursuing)
□ Postdoctoral positions
□ Visiting researcher positions
```

---

## 📊 Track Your Impact

```
Check weekly:
□ SSRN downloads: 
  https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6859459
□ Google Scholar citations (set up alert)
□ GitHub stars: github.com/kw3ku/MPSI

Set up Google Scholar Alert:
→ scholar.google.com → My profile → Create profile
→ Link SSRN paper 6859459
→ Set citation alerts
```

---

## 📋 Your Two Papers Summary

| | Paper 1 | Paper 2 |
|---|---|---|
| Title | Dollarization, Exchange Rate Volatility... | MPSI |
| Journal | JIMF (under review) | SSRN live — submit to JME/JMCB |
| Status | 6 months — send inquiry | Published May 30, 2026 |
| SSRN | Already posted | 6859459 |
| Action | Email editor this week | Submit to journal within 60 days |

---

## 🏆 What You Have Accomplished

```
✅ MS Financial Economics — UW-Madison 2025
✅ Paper 1 — Under review at JIMF
✅ Paper 2 — SSRN 6859459 published May 30, 2026
✅ Open-source toolkit — github.com/kw3ku/MPSI
✅ Interactive dashboard — fedmpsi.com
✅ ORCID — 0009-0003-2566-2238
✅ Two working papers before finishing degree
```

---

*Roadmap prepared: May 30, 2026*
*Next review date: June 30, 2026*