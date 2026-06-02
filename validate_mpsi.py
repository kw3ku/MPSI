"""
Quick Validation Tests for MPSI Calculator
Run this to identify immediate issues
"""

from models.mpsi_calculator import HybridMPSICalculator
import pandas as pd

def test_negation_handling():
    """Test if negation is handled correctly"""
    print("\n" + "="*70)
    print("TEST 1: NEGATION HANDLING")
    print("="*70)
    
    calculator = HybridMPSICalculator()
    
    test_cases = [
        ("We will raise rates to combat inflation", "HAWKISH"),
        ("We will not raise rates at this time", "DOVISH/NEUTRAL"),
        ("Inflation is elevated and rising", "HAWKISH"),
        ("Inflation is not elevated", "DOVISH/NEUTRAL"),
        ("We are removing accommodation", "HAWKISH"),
        ("We are not removing accommodation", "DOVISH"),
    ]
    
    print("\nExpected behavior: Negation should flip sentiment")
    print("-" * 70)
    
    issues_found = 0
    for text, expected in test_cases:
        result = calculator.calculate_hybrid_mpsi(text)
        
        # Check if "not" is present
        has_negation = "not" in text.lower()
        
        print(f"\nText: {text}")
        print(f"Expected: {expected}")
        print(f"MPSI Score: {result['mpsi_score']}")
        print(f"Stance: {result['stance']}")
        print(f"Hawkish KW: {result['hawkish_keywords']}, Dovish KW: {result['dovish_keywords']}")
        
        # Flag potential issues
        if has_negation and result['hawkish_keywords'] > 0:
            print("⚠️  WARNING: Hawkish keywords detected despite negation!")
            issues_found += 1
        elif has_negation and result['dovish_keywords'] == 0:
            print("⚠️  WARNING: Negation not interpreted as dovish signal!")
            issues_found += 1
    
    print("\n" + "="*70)
    print(f"RESULT: {issues_found} potential negation handling issues found")
    print("="*70)
    return issues_found


def test_known_events():
    """Test against known policy events"""
    print("\n" + "="*70)
    print("TEST 2: KNOWN POLICY EVENTS VALIDATION")
    print("="*70)
    
    # Load processed data
    df = pd.read_csv('data/processed/mpsi_hybrid_scores.csv')
    
    test_events = [
        {
            'date': '2020-03-15',
            'event': 'COVID Emergency Cut (0% rates, unlimited QE)',
            'expected_stance': 'Very Dovish',
            'expected_range': (-50, -25)
        },
        {
            'date': '2022-09-21',
            'event': 'Aggressive Tightening (75bp hike)',
            'expected_stance': 'Hawkish',
            'expected_range': (0, 30)
        },
        {
            'date': '2020-06-10',
            'event': 'Still dovish period (0% maintained)',
            'expected_stance': 'Dovish',
            'expected_range': (-40, -5)
        }
    ]
    
    print("\nChecking if MPSI captures known policy stances...")
    print("-" * 70)
    
    validation_score = 0
    for event in test_events:
        matching_rows = df[df['date'] == event['date']]
        
        if len(matching_rows) == 0:
            print(f"\n⚠️  Date {event['date']} not found in dataset")
            continue
        
        for _, row in matching_rows.iterrows():
            print(f"\n{event['date']}: {event['event']}")
            print(f"Expected: {event['expected_stance']} ({event['expected_range'][0]} to {event['expected_range'][1]})")
            print(f"Actual: {row['stance']} (MPSI: {row['mpsi_hybrid']})")
            
            # Check if in expected range
            if event['expected_range'][0] <= row['mpsi_hybrid'] <= event['expected_range'][1]:
                print("✅ PASS: MPSI in expected range")
                validation_score += 1
            else:
                print("❌ FAIL: MPSI outside expected range")
            
            # Check specific issue: June 2020
            if event['date'] == '2020-06-10' and row['filename'] == 'fomc_st_20200610.txt':
                print(f"\n🔍 CRITICAL CHECK: June 2020 False Positive")
                print(f"   FinBERT MPSI: {row['mpsi_finbert']} (should be negative!)")
                print(f"   Keyword MPSI: {row['mpsi_keywords']} (correct)")
                if row['mpsi_finbert'] > 20:
                    print("   ❌ FinBERT shows false positive (dovish period detected as positive)")
    
    print("\n" + "="*70)
    print(f"RESULT: {validation_score}/{len(test_events)} events correctly captured")
    print("="*70)
    return validation_score


def test_weight_sensitivity():
    """Test different keyword/FinBERT weight combinations"""
    print("\n" + "="*70)
    print("TEST 3: WEIGHT SENSITIVITY ANALYSIS")
    print("="*70)
    
    calculator = HybridMPSICalculator()
    
    # Use a sample Fed statement
    sample_text = """
    The Federal Reserve decided to raise the federal funds rate by 75 basis points.
    Inflation remains elevated and the Committee is highly attentive to inflation risks.
    The Committee is committed to returning inflation to its 2 percent objective.
    """
    
    # Test different weight combinations
    weights = [(50, 50), (60, 40), (70, 30), (80, 20), (90, 10)]
    
    print("\nTesting MPSI with different keyword/FinBERT weight combinations...")
    print("Sample text: Fed raising rates, inflation elevated (clearly HAWKISH)")
    print("-" * 70)
    
    finbert_result = calculator.analyze_with_finbert(sample_text)
    keyword_detector = calculator.keyword_detector
    
    finbert_mpsi = (finbert_result['positive'] - finbert_result['negative']) * 100
    keyword_mpsi = keyword_detector.calculate_keyword_mpsi(sample_text)
    
    print(f"\nComponent scores:")
    print(f"  Keyword MPSI: {keyword_mpsi:.2f}")
    print(f"  FinBERT MPSI: {finbert_mpsi:.2f}")
    print()
    
    results = []
    for kw_w, fb_w in weights:
        hybrid = (kw_w/100 * keyword_mpsi) + (fb_w/100 * finbert_mpsi)
        results.append((kw_w, fb_w, hybrid))
        print(f"Weights {kw_w}/{fb_w}: MPSI = {hybrid:>6.2f}")
    
    # Check variability
    mpsi_scores = [r[2] for r in results]
    variability = max(mpsi_scores) - min(mpsi_scores)
    
    print("\n" + "="*70)
    print(f"RESULT: MPSI ranges from {min(mpsi_scores):.2f} to {max(mpsi_scores):.2f}")
    print(f"        Variability: {variability:.2f} points")
    if variability > 10:
        print("⚠️  WARNING: High sensitivity to weight choice!")
        print("    Need empirical justification for 70/30 split")
    print("="*70)
    return variability


def test_document_length_bias():
    """Test if shorter documents get extreme scores"""
    print("\n" + "="*70)
    print("TEST 4: DOCUMENT LENGTH BIAS")
    print("="*70)
    
    df = pd.read_csv('data/processed/mpsi_hybrid_scores.csv')
    
    # Compare short vs long documents
    short_docs = df[df['word_count'] < 500]
    long_docs = df[df['word_count'] > 3000]
    
    print(f"\nShort documents (< 500 words): n={len(short_docs)}")
    print(f"  Mean MPSI: {short_docs['mpsi_hybrid'].mean():.2f}")
    print(f"  Std Dev:   {short_docs['mpsi_hybrid'].std():.2f}")
    print(f"  Range:     [{short_docs['mpsi_hybrid'].min():.2f}, {short_docs['mpsi_hybrid'].max():.2f}]")
    
    print(f"\nLong documents (> 3000 words): n={len(long_docs)}")
    print(f"  Mean MPSI: {long_docs['mpsi_hybrid'].mean():.2f}")
    print(f"  Std Dev:   {long_docs['mpsi_hybrid'].std():.2f}")
    print(f"  Range:     [{long_docs['mpsi_hybrid'].min():.2f}, {long_docs['mpsi_hybrid'].max():.2f}]")
    
    # Check if short docs more extreme
    short_std = short_docs['mpsi_hybrid'].std()
    long_std = long_docs['mpsi_hybrid'].std()
    
    print("\n" + "="*70)
    if short_std > long_std * 1.5:
        print("⚠️  WARNING: Short documents show higher variance")
        print("    This suggests keyword density bias")
        print(f"    Short doc std: {short_std:.2f} vs Long doc std: {long_std:.2f}")
    else:
        print("✅ PASS: No strong length bias detected")
    print("="*70)


def main():
    """Run all validation tests"""
    print("\n" + "="*70)
    print("MPSI VALIDATION TEST SUITE")
    print("="*70)
    print("Running comprehensive validation checks...")
    print("This will identify methodological issues that reviewers will find")
    
    results = {}
    
    # Run tests
    results['negation_issues'] = test_negation_handling()
    results['validation_score'] = test_known_events()
    results['weight_sensitivity'] = test_weight_sensitivity()
    test_document_length_bias()
    
    # Summary
    print("\n" + "="*70)
    print("OVERALL VALIDATION SUMMARY")
    print("="*70)
    
    total_issues = 0
    
    print(f"\n1. Negation Handling: {results['negation_issues']} issues found")
    if results['negation_issues'] > 0:
        print("   ❌ CRITICAL: Implement negation detection")
        total_issues += 1
    
    print(f"\n2. Known Events: {results['validation_score']}/3 correctly captured")
    if results['validation_score'] < 3:
        print("   ⚠️  WARNING: Not all known events correctly identified")
        total_issues += 1
    
    print(f"\n3. Weight Sensitivity: {results['weight_sensitivity']:.1f} point variability")
    if results['weight_sensitivity'] > 10:
        print("   ⚠️  WARNING: Results highly sensitive to weight choice")
        print("      Need to justify 70/30 split empirically")
        total_issues += 1
    
    print("\n" + "="*70)
    print(f"TOTAL CRITICAL ISSUES: {total_issues}")
    print("="*70)
    
    if total_issues == 0:
        print("\n✅ All validation tests passed!")
        print("   Your MPSI methodology appears sound")
        print("   Next step: Correlate with Fed Funds Rate changes")
    else:
        print(f"\n❌ Found {total_issues} critical issues")
        print("   These MUST be addressed before publication")
        print("   See EXPERT_ANALYSIS.md for detailed recommendations")
    
    print("\n" + "="*70)
    print("Validation complete. See EXPERT_ANALYSIS.md for full report.")
    print("="*70)


if __name__ == "__main__":
    main()
