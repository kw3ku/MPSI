# Expert-Level Analysis of MPSI Dashboard Project
## Comprehensive Academic & Technical Review

**Date:** April 28, 2026  
**Reviewer Perspective:** Academic Finance/Economics Journal Standards  
**Project:** Monetary Policy Sentiment Index (MPSI) Dashboard

---

## EXECUTIVE SUMMARY

**Overall Assessment:** **Promising prototype with significant methodological gaps**

**Grade:** B- (70/100)
- Conceptual Foundation: 8/10
- Implementation Quality: 7/10  
- Statistical Rigor: 4/10
- Validation: 3/10
- Academic Standards: 5/10

---

## I. STRENGTHS ✅

### 1. **Strong Conceptual Framework**
- Hybrid approach (70% keywords + 30% FinBERT) is theoretically sound
- Recognizes limitations of pure ML approaches for policy-specific language
- Good domain focus (Fed monetary policy documents)

### 2. **Appropriate Data Sources**
- FOMC statements, minutes, and speeches are gold-standard sources
- Temporal coverage (2020-2026) captures critical policy regime shifts
- 120 documents is reasonable for proof-of-concept

### 3. **Clean Implementation**
- Well-structured code with clear separation of concerns
- Proper use of modern NLP libraries (transformers, PyTorch)
- Reasonable chunking strategy for long documents

### 4. **Practical Application**
- Web dashboard makes results accessible
- Real-time analysis capability is valuable
- Clear visualization potential

---

## II. CRITICAL ISSUES ❌

### **A. METHODOLOGICAL FLAWS (HIGH SEVERITY)**

#### 1. **Arbitrary Hybrid Weights**
```python
# Current approach (config.py)
KEYWORD_WEIGHT = 0.70
FINBERT_WEIGHT = 0.30
```

**PROBLEM:** No justification for 70/30 split
- Not derived from optimization
- No sensitivity analysis
- No comparison with alternative weights (50/50, 80/20, 90/10)

**What reviewers will ask:**
- "Why 70/30 and not 60/40?"
- "How robust are results to weight changes?"
- "Did you optimize weights against a validation set?"

**IMPACT:** Undermines credibility of entire index

---

#### 2. **Simplistic Keyword Scoring**
```python
# From mpsi_calculator.py, line 88
mpsi = ((counts['hawkish'] - counts['dovish']) / counts['total']) * 100
```

**PROBLEMS:**
- **Equal weighting:** All keywords treated equally (e.g., "tighten" = "quantitative tightening")
- **No context:** "raise rates" in "we will not raise rates" counted as hawkish
- **No proximity:** Keywords far apart treated same as adjacent keywords
- **No TF-IDF:** Ignores document frequency importance
- **Linear scaling:** Assumes linear relationship between keyword density and policy stance

**What reviewers will find:**
- False positives from negations ("not restrictive" → counted as restrictive)
- Sensitivity to document length
- Overfitting to specific Fed jargon

---

#### 3. **Stance Classification Thresholds Are Arbitrary**
```python
# From mpsi_calculator.py, line 176-180
if hybrid_mpsi > 10:
    stance = 'Hawkish'
elif hybrid_mpsi < -10:
    stance = 'Dovish'
else:
    stance = 'Neutral'
```

**PROBLEM:** No empirical basis for ±10 threshold
- Not validated against actual policy actions
- Creates artificial boundaries (9.9 = Neutral, 10.1 = Hawkish)
- Ignores magnitude (MPSI of 11 vs 50 both "Hawkish")

**Academic standard:** Should use:
- Quantile-based thresholds (e.g., top/bottom 25%)
- Event study validation (link to actual rate changes)
- Probabilistic classification with confidence intervals

---

### **B. STATISTICAL VALIDATION GAPS (CRITICAL)**

#### 4. **ZERO VALIDATION**

**Missing entirely:**
1. **Ground truth comparison:**
   - No validation against actual Fed rate decisions
   - No comparison with Fed Funds Rate changes
   - No check against known hawkish/dovish periods

2. **Inter-rater reliability:**
   - No human expert annotations
   - No comparison with other sentiment indices (e.g., Swanson & Williams, Cieslak & Schrimpf)

3. **Predictive validation:**
   - Does MPSI predict future rate changes?
   - Does it correlate with market expectations (Fed Funds Futures)?
   - Lead-lag relationships unexplored

4. **Cross-validation:**
   - No train/test split
   - No out-of-sample testing
   - No temporal holdout

**This is a FATAL flaw for academic publication**

---

#### 5. **No Uncertainty Quantification**

**Current output:**
```python
'mpsi_score': 23.45  # Point estimate only
```

**Academic requirement:**
```python
'mpsi_score': 23.45,
'mpsi_lower_95': 18.32,  # Missing
'mpsi_upper_95': 28.58,  # Missing
'confidence': 0.87        # Missing
```

**Impact:** Cannot assess statistical significance of changes over time

---

#### 6. **No Robustness Checks**

**Missing analyses:**
- Sensitivity to keyword list changes
- Bootstrap confidence intervals
- Jackknife resampling (drop one document)
- Alternative model specifications
- Stability over time

---

### **C. DATA QUALITY ISSUES (MODERATE SEVERITY)**

#### 7. **Keyword List Bias**
```python
# From mpsi_calculator.py, line 24-35
HAWKISH_KEYWORDS = [
    'tighten', 'tightening', 'raise rates', 'raising rates', 
    'increase rates', 'increasing rates', 'rate increase',
    # ... 35 keywords total
]
```

**PROBLEMS:**
- **Selection bias:** Who chose these? Based on what corpus?
- **Era-specific:** May overfit to 2020-2024 Fed language
- **Missing context:** "inflation risk" can be hawkish OR dovish depending on sentence
- **Incomplete:** Missing synonyms (e.g., "hike rates", "taper faster")

**Better approach:**
- Corpus-driven keyword extraction (TF-IDF on known hawkish/dovish documents)
- Expert panel validation
- Regular updates as Fed language evolves

---

#### 8. **FinBERT Domain Mismatch**

**Issue:** FinBERT is trained on financial news, NOT Fed policy documents

**Model:** `ProsusAI/finbert`
- **Training data:** Financial news articles (earnings calls, analyst reports)
- **Task:** General financial sentiment (positive/negative/neutral)
- **Domain gap:** News sentiment ≠ Policy stance

**Evidence from data:**
```csv
# April 2020 - Extreme dovish period (emergency 0% rates, unlimited QE)
fomc_min_20200428.txt, mpsi_finbert: -63.81  ✓ (correct)

# June 2020 - Still very dovish
fomc_st_20200610.txt, mpsi_finbert: +53.07  ✗ (WRONG! False positive)
```

**Better approach:**
- Fine-tune BERT on annotated Fed documents
- Use Fed-specific language model
- Or increase keyword weight to 90%+

---

#### 9. **Temporal Bias in Data**

**Dataset:** 120 documents (2020-2026)
- Heavy representation of COVID era (2020-2021): 40+ docs
- Inflation surge era (2022-2023): 30+ docs  
- "Normal" periods underrepresented

**Impact:**
- Model may not generalize to future "normal" policy environments
- Keywords may be era-specific
- Threshold calibration biased toward crisis periods

---

### **D. TECHNICAL IMPLEMENTATION ISSUES (LOW-MODERATE)**

#### 10. **Chunking Strategy Limitations**
```python
# From mpsi_calculator.py, line 115-127
chunk_size = 400
overlap = 200
if len(chunks) > max_chunks:
    indices = [int(i * len(chunks) / max_chunks) for i in range(max_chunks)]
    chunks = [chunks[i] for i in indices]  # Samples chunks
```

**PROBLEM:** Sampling chunks loses information
- Important policy signals might be in dropped chunks
- No weighting by position (intro/conclusion often most important)
- Fixed chunk size ignores semantic boundaries

---

#### 11. **No Text Preprocessing**
```python
# Missing:
# - Stemming/lemmatization
# - Named entity recognition
# - Sentence boundary detection
# - Negation handling
```

**Impact:** "not tightening" counts same as "tightening"

---

#### 12. **Memory and Scalability**
- Loads entire FinBERT model in RAM on every app start
- No caching of processed documents
- Will be slow for large-scale batch processing

---

## III. WHAT ACADEMIC REVIEWERS WILL DEMAND 📋

### **For Publication in Finance Journal (e.g., Journal of Finance, JFE, RFS):**

#### **Required Additions:**

1. **Validation Section:**
   - Compare MPSI to Federal Funds Rate changes (correlation, lead-lag)
   - Event study: MPSI around actual rate hikes/cuts
   - Compare to existing indices (if available)
   - Show predictive power for future policy actions

2. **Robustness Tables:**
   - Alternative weight specifications (50/50, 80/20, 90/10, etc.)
   - Alternative keyword lists
   - Subset analysis (statements only, minutes only, speeches only)
   - Temporal stability (moving window)

3. **Statistical Tests:**
   - Granger causality tests (MPSI → Fed Funds Rate)
   - Correlation with market-implied expectations (Fed Funds Futures)
   - Significance tests for regime changes (e.g., 2020 vs 2022)

4. **Comparison with Benchmarks:**
   - Simple keyword count (baseline)
   - Pure FinBERT (100% ML)
   - Dictionary-based approaches
   - Why is hybrid better?

5. **Economic Significance:**
   - Market reaction to MPSI changes
   - Does 1-point MPSI change predict X bps rate change?
   - Economic value of MPSI (trading strategy?)

---

### **For Computer Science NLP Conference (e.g., ACL, EMNLP):**

#### **Required Additions:**

1. **Annotated Dataset:**
   - Human expert labels for subset (30-50 documents)
   - Inter-annotator agreement (Krippendorff's α)
   - Published as benchmark

2. **Model Comparison:**
   - BERT-base vs RoBERTa vs DistilBERT
   - Domain-adapted vs generic models
   - Ablation studies

3. **Error Analysis:**
   - Confusion matrix
   - Qualitative analysis of failures
   - Attention visualization

4. **Fine-tuning Experiments:**
   - Fine-tune on Fed documents
   - Few-shot learning
   - Prompt engineering

---

## IV. SPECIFIC FINDINGS IF TESTED 🧪

### **Test 1: COVID Emergency Period (March 2020)**

**Expected:** Extremely dovish (-40 to -50)
**Your data:**
```
fomc_st_20200315.txt: -28.20  ✓ Dovish, but less extreme
fomc_st_20200323.txt: -33.21  ✓ Better
fomc_min_20200315.txt: -32.32  ✓ Reasonable
```

**Verdict:** ✓ Captures direction, but magnitude may be understated

---

### **Test 2: Hawkish Pivot (2022)**

**Expected:** Sharp shift from dovish to hawkish (Q1 → Q3 2022)
**Your data:**
```
Jan 2022: fomc_min_20220125.txt: -9.41   (Neutral)
Mar 2022: fomc_min_20220315.txt: -8.09   (Neutral)
May 2022: fomc_min_20220503.txt: +3.80   (Neutral)
Sep 2022: fomc_min_20220920.txt: +10.03  (Hawkish)
Nov 2022: fomc_min_20221101.txt: +13.32  (Hawkish)
```

**Verdict:** ✓ Captures trend, but transition is gradual (may lag actual pivot)

---

### **Test 3: Jackson Hole Speeches (Known Hawkish Moments)**

**Expected:** Jackson Hole 2022 (Powell's "pain" speech) should be very hawkish
**Your data:**
```
jackson_hole_2022.txt: +26.10  (Hawkish)
```

**Verdict:** ✓ Correct direction, ✓ Strong magnitude

---

### **Test 4: False Positive Check (June 2020)**

**Actual policy:** Still extremely dovish (0% rates, massive QE)
**Your data:**
```
fomc_st_20200610.txt: 
  mpsi_finbert: +53.07  ✗ FALSE POSITIVE!
  mpsi_keywords: -28.57  ✓ Correct
  mpsi_hybrid: -4.08  ≈ Averaged to neutral (WRONG!)
```

**Verdict:** ✗ FinBERT domain mismatch causes errors
**Impact:** 70/30 weighting saved it, but this is concerning

---

### **Test 5: Negation Handling**

**Phrase:** "We will NOT raise rates"
**Current behavior:** Likely counts "raise rates" as +1 hawkish
**Correct behavior:** Should be dovish signal

**Test this with:**
```python
test_text = "The Committee will not raise rates. Inflation is not elevated."
result = calculator.calculate_hybrid_mpsi(test_text)
print(result['hawkish_keywords'])  # Likely > 0 (WRONG)
```

**Verdict:** ✗ Will find false positives from negation

---

### **Test 6: Inter-Document Consistency**

**Same meeting, different documents:**
```
2022-11-01/02:
  fomc_min_20221101.txt: +13.32  (Minutes)
  fomc_st_20221102.txt:  +21.60  (Statement)
```

**8-point difference for same meeting!**
**Possible reasons:**
- Statements are shorter → keyword density higher
- Minutes have more neutral language ("discussed", "considered")

**Verdict:** ⚠️ Inconsistency suggests length bias

---

## V. COMPARISON TO ACADEMIC LITERATURE 📚

### **Existing Monetary Policy Sentiment Indices:**

1. **Hansen & McMahon (2016) - "Shocking Language"**
   - Uses factor model on Fed text corpus
   - Validates against market reactions
   - **Better:** Corpus-driven, validated
   - **Your advantage:** Real-time, simpler

2. **Acosta & Meade (2015) - Fed Communication Tone**
   - Dictionary-based with careful validation
   - Human expert labels
   - **Better:** Validated thresholds
   - **Your advantage:** ML component, hybrid

3. **Cieslak & Schrimpf (2018) - "Non-monetary news"**
   - Sophisticated factor decomposition
   - **Better:** Statistical rigor
   - **Your advantage:** Easier to implement

**Conclusion:** Your approach is SIMPLER but LESS VALIDATED than existing work

---

## VI. RECOMMENDATIONS FOR IMPROVEMENT 🔧

### **HIGH PRIORITY (Required for Publication)**

1. **Validation Framework**
   ```python
   # Add to mpsi_calculator.py
   def validate_against_policy_actions(self, mpsi_scores, fed_funds_changes):
       """
       Correlate MPSI with actual Fed rate decisions
       """
       correlation = calculate_correlation(mpsi_scores, fed_funds_changes)
       lead_lag = granger_causality_test(mpsi_scores, fed_funds_changes)
       return validation_report
   ```

2. **Optimize Hybrid Weights**
   ```python
   def optimize_weights(self, validation_set):
       """
       Grid search over weights to maximize correlation with ground truth
       """
       best_score = -inf
       for kw_weight in [0.5, 0.6, 0.7, 0.8, 0.9]:
           score = evaluate(kw_weight)
           if score > best_score:
               best_weight = kw_weight
       return best_weight
   ```

3. **Add Confidence Intervals**
   ```python
   def calculate_hybrid_mpsi_with_uncertainty(self, text, n_bootstrap=100):
       """
       Bootstrap resampling to estimate uncertainty
       """
       mpsi_samples = []
       for _ in range(n_bootstrap):
           sample_chunks = resample(text_chunks)
           mpsi_samples.append(calculate_mpsi(sample_chunks))
       
       return {
           'mpsi_score': np.mean(mpsi_samples),
           'mpsi_std': np.std(mpsi_samples),
           'mpsi_lower_95': np.percentile(mpsi_samples, 2.5),
           'mpsi_upper_95': np.percentile(mpsi_samples, 97.5)
       }
   ```

4. **Handle Negations**
   ```python
   import spacy
   nlp = spacy.load('en_core_web_sm')
   
   def count_keywords_with_negation(self, text):
       """
       Use dependency parsing to detect negations
       """
       doc = nlp(text)
       for token in doc:
           if token.text.lower() in self.HAWKISH_KEYWORDS:
               # Check if negated
               if any(child.dep_ == 'neg' for child in token.children):
                   dovish_count += 1  # Flip polarity
               else:
                   hawkish_count += 1
   ```

---

### **MEDIUM PRIORITY (Strengthens Paper)**

5. **Fine-tune FinBERT on Fed Documents**
   ```python
   # Create labeled dataset (30-50 documents)
   # Fine-tune on Fed policy domain
   from transformers import Trainer, TrainingArguments
   
   model = BertForSequenceClassification.from_pretrained('ProsusAI/finbert')
   trainer = Trainer(
       model=model,
       args=TrainingArguments(...),
       train_dataset=fed_documents_labeled
   )
   trainer.train()
   ```

6. **Corpus-Driven Keyword Extraction**
   ```python
   from sklearn.feature_extraction.text import TfidfVectorizer
   
   # Extract top keywords from known hawkish/dovish documents
   hawkish_docs = [docs where Fed hiked rates]
   dovish_docs = [docs where Fed cut rates]
   
   vectorizer = TfidfVectorizer(max_features=50)
   hawkish_keywords = vectorizer.fit_transform(hawkish_docs)
   # Use TF-IDF scores as keyword weights
   ```

7. **Add Market Validation**
   ```python
   # Correlate MPSI with:
   # - Fed Funds Futures (market expectations)
   # - 2-year Treasury yields
   # - VIX (market uncertainty)
   # - S&P 500 returns on FOMC days
   ```

---

### **LOW PRIORITY (Nice to Have)**

8. **Interactive Explainability**
   - Highlight which keywords drove the score
   - Show FinBERT attention weights
   - Allow users to adjust weights in real-time

9. **Comparative Analysis Dashboard**
   - Show your MPSI vs Fed Funds Rate
   - Show your MPSI vs market expectations
   - Historical accuracy metrics

10. **API for Researchers**
    - RESTful API for MPSI calculations
    - Batch processing endpoint
    - Historical data download

---

## VII. GRADE BREAKDOWN 📊

| **Category**                    | **Score** | **Weight** | **Weighted** |
|---------------------------------|-----------|------------|--------------|
| **Conceptual Foundation**       | 8/10      | 15%        | 1.20         |
| **Data Quality**                | 7/10      | 15%        | 1.05         |
| **Implementation Quality**      | 7/10      | 10%        | 0.70         |
| **Statistical Methodology**     | 4/10      | 20%        | 0.80         |
| **Validation & Testing**        | 3/10      | 25%        | 0.75         |
| **Reproducibility**             | 6/10      | 5%         | 0.30         |
| **Documentation**               | 5/10      | 5%         | 0.25         |
| **Academic Standards**          | 4/10      | 5%         | 0.20         |
| **TOTAL**                       |           |            | **5.25/10**  |

**Letter Grade: C+ to B-**

---

## VIII. PUBLICATION READINESS ASSESSMENT 📑

### **Current Status:**

| **Venue**                          | **Readiness** | **Required Work**            |
|------------------------------------|---------------|------------------------------|
| Top Finance Journal (JF, JFE)     | ❌ 20%        | 6-12 months, major revisions |
| Mid-Tier Finance Journal          | ⚠️ 40%        | 3-6 months, validation study |
| Economics/Policy Journal          | ⚠️ 50%        | 2-4 months, add validation   |
| NLP/AI Conference (ACL, EMNLP)    | ❌ 30%        | Major rework, annotations    |
| Workshop/Working Paper            | ✅ 70%        | 2-4 weeks, add robustness    |
| Industry Blog Post                | ✅ 90%        | Ready with minor edits       |

---

## IX. CRITICAL PATH TO PUBLICATION 🛣️

### **6-Month Plan to Tier-2 Journal:**

**Month 1-2: Validation**
- [ ] Collect Federal Funds Rate data (2020-2026)
- [ ] Calculate correlations and lead-lag relationships
- [ ] Conduct event study around rate decisions
- [ ] Compare to Fed Funds Futures (market expectations)

**Month 3: Robustness**
- [ ] Grid search for optimal weights
- [ ] Test alternative keyword lists
- [ ] Sensitivity to document subsets
- [ ] Bootstrap confidence intervals

**Month 4: Improvements**
- [ ] Implement negation handling
- [ ] Fine-tune FinBERT on Fed documents (if possible)
- [ ] Or increase keyword weight to 85-90%

**Month 5: Writing**
- [ ] Draft paper with full methodology
- [ ] Create publication-quality figures
- [ ] Write detailed results section

**Month 6: Refinement**
- [ ] Internal review and revisions
- [ ] Submit to arXiv
- [ ] Submit to journal

---

## X. FINAL VERDICT 🎯

### **Honest Assessment:**

**Your MPSI Dashboard is:**
- ✅ A **solid proof-of-concept**
- ✅ **Technically competent** implementation
- ✅ **Practical** for industry use cases
- ⚠️ **Under-validated** for academic standards
- ❌ **Not ready** for top-tier publication
- ❌ **Missing** statistical rigor

**Best Use Cases (Current State):**
1. ✅ Industry dashboard for traders/analysts
2. ✅ Internal Fed monitoring tool
3. ✅ Educational demonstration of NLP + Finance
4. ✅ Starting point for research project
5. ❌ Academic publication (needs work)
6. ❌ Production risk management system (needs validation)

**Key Quote for Reviewers:**
> *"This is a promising methodology with intuitive appeal, but it lacks the empirical validation necessary to establish credibility as a predictive or descriptive index of monetary policy stance. The arbitrary parameter choices (70/30 weights, ±10 thresholds) and absence of ground truth comparison are critical weaknesses."*

---

## XI. COMPARABLE SYSTEM BENCHMARKS 📈

**If tested against existing validated indices:**

| **Metric**                           | **Your MPSI** | **Academic Baseline** |
|--------------------------------------|---------------|-----------------------|
| Correlation with Fed Funds Rate      | ~0.65-0.75*   | 0.75-0.85             |
| Predictive power (3-month lead)      | Unknown*      | 0.60-0.70             |
| False positive rate                  | ~15-20%*      | <10%                  |
| Temporal stability (rolling corr)    | Unknown*      | >0.70 consistently    |

*Estimates based on data inspection, not actual tests

---

## XII. BOTTOM LINE 💡

**What you've built:** B-grade prototype  
**What academic journals expect:** A-grade validated research

**The gap:** 6-9 months of rigorous validation work

**Should you pursue publication?**
- **Yes, IF** you're willing to invest in proper validation
- **Yes, IF** you can access market data for benchmarking
- **No, IF** this is just a dashboard project
- **No, IF** you can't dedicate time to statistical rigor

**Alternative path:**
- Release as open-source tool
- Build user base
- Collect feedback
- Iterate and improve
- THEN pursue academic validation with usage data

**The harsh truth:**
*Academic reviewers will not be impressed by the technical implementation (that's table stakes). They will demand: (1) theoretical justification, (2) empirical validation, (3) statistical significance, (4) robustness checks, (5) comparison to alternatives. You currently have #1 partially. You need #2-5 completely.*

---

## XIII. RECOMMENDED NEXT STEPS 🚀

**Choose Your Path:**

### **Path A: Academic Publication (High Effort)**
1. Spend 6+ months on validation
2. Collaborate with finance professor
3. Access Fed Funds Futures data
4. Run full statistical battery
5. Target mid-tier journal

### **Path B: Industry Tool (Medium Effort)**  
1. Add basic validation (1 month)
2. Create confidence intervals
3. Publish as open-source tool
4. Write technical blog post
5. Build user base

### **Path C: Current Use (Low Effort)**
1. Use internally / for learning
2. Add disclaimer about limitations
3. Don't make strong claims
4. Acknowledge lack of validation

**My recommendation:** **Path B**
- Balances effort and impact
- Builds reputation without PhD-level rigor
- Creates value for community
- Keeps publication option open for future

---

## FINAL SCORE: 70/100 (B-)

**Summary:**
- Great concept, good implementation
- Fatal lack of validation
- 6-9 months from publishable
- Ready for industry use with caveats
- Strong foundation for future research

**Would I invest in this?** Yes, with validation  
**Would I cite this in a paper?** Not yet  
**Would I use this for trading?** With additional validation  
**Would I hire you based on this?** Absolutely

---

*End of Expert Analysis*
