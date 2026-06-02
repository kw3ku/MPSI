# Quick Action Plan: MPSI Project Improvements

## CRITICAL ISSUES TO FIX IMMEDIATELY

### 1. **Test for Negation Handling** (2 hours)
```python
# Add this test to verify the problem:
test_cases = [
    "We will not raise rates" → Should be DOVISH, probably shows HAWKISH
    "Inflation is not elevated" → Should be DOVISH/NEUTRAL
    "We will raise rates" → Should be HAWKISH
]

# Run: python test_negation.py
```

### 2. **Validate Against Fed Funds Rate** (1 day)
- Download Fed Funds Rate data (FRED: DFF)
- Calculate correlation between MPSI and rate changes
- Create scatter plot and report correlation coefficient
- **Expected correlation:** 0.60-0.75 if working well

### 3. **Test Weight Sensitivity** (3 hours)
```python
# Test different keyword/FinBERT weight combinations:
weights = [(50,50), (60,40), (70,30), (80,20), (90,10), (100,0)]

for kw_w, fb_w in weights:
    results = process_all_docs(keyword_weight=kw_w, finbert_weight=fb_w)
    print(f"{kw_w}/{fb_w}: Correlation = {correlation_with_fed_rate}")
```

### 4. **Add Confidence Intervals** (1 day)
- Use bootstrap resampling on text chunks
- Report: mean ± std dev for each MPSI score
- This is MINIMUM for any statistical claim

### 5. **Fix June 2020 False Positive** (Investigation needed)
```csv
fomc_st_20200610.txt:
  Context: Still 0% rates, massive QE (very dovish period)
  Your finbert_mpsi: +53.07 (WRONG!)
  Your hybrid_mpsi: -4.08 (barely caught it)
```
→ This proves FinBERT is unreliable for Fed documents

## RECOMMENDED QUICK WINS (2-3 weeks)

### Week 1: Validation
- [ ] Get Fed Funds Rate data
- [ ] Calculate correlations
- [ ] Create validation report
- [ ] Test specific known events (March 2020, Sept 2022)

### Week 2: Robustness
- [ ] Test weight sensitivity
- [ ] Test keyword list variations
- [ ] Add confidence intervals
- [ ] Document limitations

### Week 3: Improvements
- [ ] Add negation handling OR
- [ ] Increase keyword weight to 85-90% (easier fix)
- [ ] Add visualizations comparing MPSI to Fed Funds Rate
- [ ] Write methodology document

## STOPPING RULES

**Don't pursue academic publication IF:**
- You find correlation with Fed Funds Rate < 0.50
- You can't explain why 70/30 weights are optimal
- You don't have time for 6+ months of validation work

**DO pursue IF:**
- Correlation > 0.65
- You can get market data (Fed Funds Futures)
- You have advisor/collaborator with finance expertise

## HONEST ASSESSMENT

**Current state:** Prototype that "looks right" but isn't proven
**Time to publishable:** 6-9 months of validation work
**Time to usable tool:** 2-3 weeks of basic validation

**Your choice:** Academic rigor vs practical tool

## IMMEDIATE NEXT STEP

Run this validation script I'll create for you...
