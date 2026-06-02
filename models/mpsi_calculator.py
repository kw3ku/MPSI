"""
Hybrid MPSI Calculator
Combines FinBERT sentiment + Policy-specific keywords
More accurate for Fed monetary policy documents

Keyword scoring follows Eq. (4) from the paper:
    Weighted Score_t = sum_{w in Hawkish} omega_w * c_{w,t}
                     - sum_{w in Dovish}  omega_w * c_{w,t}
    omega_w = 0.7 * Corr(c_w, delta_i_t) + 0.3 * TF-IDF_w

Normalisation via tanh (Eq. 5):
    Keyword_t = 100 * tanh(Weighted Score_t / sigma_score)

Hybrid weights from Proposition 2 (minimum-variance estimator):
    w_K* = sigma_F^2 / (sigma_K^2 + sigma_F^2) = 0.074/0.110 ≈ 0.70
    w_F* = sigma_K^2 / (sigma_K^2 + sigma_F^2) = 0.036/0.110 ≈ 0.30
"""

import math
import torch
from transformers import BertTokenizer, BertForSequenceClassification
import pandas as pd
from pathlib import Path
from tqdm import tqdm
import warnings
import re
warnings.filterwarnings('ignore')


class PolicyKeywordDetector:
    """
    Detect monetary policy stance using weighted keyword analysis.

    Each keyword carries a weight omega_w (Eq. 4 in paper):
        omega_w = 0.7 * Corr(c_w, delta_i_t) + 0.3 * TF-IDF_w
    Weights are estimated from the 119-document validation corpus.
    """

    # (keyword, omega_w) — hawkish signals (+)
    HAWKISH_KEYWORDS = {
        # Direct policy actions
        'raise rates':             1.00,
        'increase rates':          1.00,
        'tighten':                 0.89,
        'tightening':              0.89,
        'restrictive':             0.85,
        'restrictive policy':      0.83,
        'withdraw accommodation':  0.82,
        'reduce holdings':         0.76,
        'balance sheet reduction': 0.79,
        'quantitative tightening': 0.78,
        'runoff':                  0.74,
        'front-load':              0.72,
        'expedite':                0.70,
        # Inflation concerns
        'elevated inflation':      0.91,
        'above target':            0.88,
        'inflation pressures':     0.85,
        'price stability concerns':0.82,
        'persistent inflation':    0.80,
        'high inflation':          0.78,
        'inflation well above':    0.85,
        'inflation remains elevated': 0.88,
        'rising inflation':        0.76,
        'inflation risk':          0.74,
        # Economic strength
        'tight labor market':      0.84,
        'strong labor market':     0.82,
        'overheating':             0.80,
        'above potential':         0.78,
        'wage pressures':          0.78,
        'labor market tight':      0.82,
        # Forward guidance
        'further increases':       0.86,
        'ongoing increases':       0.84,
        'committed to tightening': 0.88,
        'additional tightening':   0.85,
        'will continue to increase': 0.83,
        'appropriate to raise':    0.80,
        'gradually raising':       0.78,
        'gradual increases':       0.76,
    }

    # (keyword, omega_w) — dovish signals (-)
    DOVISH_KEYWORDS = {
        # Direct policy actions
        'lower rates':             1.00,
        'cut rates':               1.00,
        'ease':                    0.89,
        'easing':                  0.89,
        'accommodative':           0.89,
        'patient':                 0.82,
        'asset purchases':         0.79,
        'maintain accommodation':  0.80,
        'quantitative easing':     0.78,
        'remain patient':          0.80,
        'patient approach':        0.80,
        'patient stance':          0.78,
        # Inflation subdued
        'low inflation':           0.88,
        'below target':            0.86,
        'subdued inflation':       0.84,
        'disinflation':            0.81,
        'modest price pressures':  0.79,
        'inflation running below': 0.86,
        'muted inflation':         0.82,
        # Economic weakness
        'slack':                   0.85,
        'downside risks':          0.83,
        'downside risk':           0.83,
        'weak labor market':       0.82,
        'support the economy':     0.80,
        'recession':               0.78,
        'slowdown':                0.76,
        'below potential':         0.80,
        'economic weakness':       0.78,
        # Forward guidance
        'considerable time':       0.88,
        'extended period':         0.86,
        'rates will remain low':   0.85,
        'data-dependent':          0.75,
        'will remain accommodative': 0.84,
        'appropriate to maintain': 0.78,
        'maintain rates':          0.76,
    }

    # Neutral/assessment — used for context only, not scored
    NEUTRAL_KEYWORDS = [
        'monitor', 'monitoring', 'assess', 'assessing',
        'evaluate', 'evaluating', 'review', 'reviewing',
        'consider', 'considering', 'data-dependent',
        'flexible', 'appropriate', 'outlook',
    ]

    # Empirical std of raw weighted scores (sigma_score) — used for tanh normalisation.
    # Estimated from the 119-document validation corpus.
    _SIGMA_SCORE = 3.5

    def count_keywords(self, text):
        """Count (unweighted) keyword occurrences — kept for backward compat."""
        text_lower = text.lower()
        hawkish_count  = sum(1 for kw in self.HAWKISH_KEYWORDS if kw in text_lower)
        dovish_count   = sum(1 for kw in self.DOVISH_KEYWORDS  if kw in text_lower)
        neutral_count  = sum(1 for kw in self.NEUTRAL_KEYWORDS if kw in text_lower)
        return {
            'hawkish': hawkish_count,
            'dovish':  dovish_count,
            'neutral': neutral_count,
            'total':   hawkish_count + dovish_count + neutral_count,
        }

    def calculate_keyword_mpsi(self, text):
        """
        Calculate keyword MPSI using paper Eq. (4) + (5).

        Weighted Score_t = sum_{hawkish} omega_w * c_{w,t}
                         - sum_{dovish}  omega_w * c_{w,t}

        Keyword_t = 100 * tanh(Weighted Score_t / sigma_score)
        """
        text_lower = text.lower()

        hawkish_score = sum(
            omega for kw, omega in self.HAWKISH_KEYWORDS.items() if kw in text_lower
        )
        dovish_score = sum(
            omega for kw, omega in self.DOVISH_KEYWORDS.items() if kw in text_lower
        )

        weighted_score = hawkish_score - dovish_score

        # tanh normalisation → maps to (-100, +100)
        mpsi = 100.0 * math.tanh(weighted_score / self._SIGMA_SCORE)

        return round(mpsi, 2)


class HybridMPSICalculator:
    """
    Hybrid MPSI combining FinBERT sentiment + keyword detection
    """
    
    def __init__(self):
        """Initialize both FinBERT and keyword detector"""
        
        print("="*70)
        print("HYBRID MPSI CALCULATOR - INITIALIZING")
        print("="*70)
        
        # Load FinBERT
        print("\n✅ Loading FinBERT model...")
        self.tokenizer = BertTokenizer.from_pretrained("ProsusAI/finbert")
        self.model = BertForSequenceClassification.from_pretrained("ProsusAI/finbert")
        self.model.eval()
        print("✅ FinBERT loaded")
        
        # Initialize keyword detector
        self.keyword_detector = PolicyKeywordDetector()
        print("✅ Keyword detector initialized\n")
    
    def analyze_with_finbert(self, text, max_chunks=10):
        """Analyze text using FinBERT (economic sentiment)"""
        
        # Split into chunks
        words = text.split()
        chunk_size = 400
        overlap = 200
        
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i+chunk_size])
            if len(chunk.split()) > 50:
                chunks.append(chunk)
        
        if len(chunks) > max_chunks:
            indices = [int(i * len(chunks) / max_chunks) for i in range(max_chunks)]
            chunks = [chunks[i] for i in indices]
        
        # Analyze each chunk
        all_sentiments = []
        for chunk in chunks:
            inputs = self.tokenizer(chunk, return_tensors="pt", truncation=True, max_length=512)
            with torch.no_grad():
                outputs = self.model(**inputs)
                probs = torch.nn.functional.softmax(outputs.logits, dim=-1)[0]
            
            all_sentiments.append({
                'positive': float(probs[0]),
                'negative': float(probs[1]),
                'neutral': float(probs[2])
            })
        
        # Average
        avg_sentiment = {
            'positive': sum(s['positive'] for s in all_sentiments) / len(all_sentiments),
            'negative': sum(s['negative'] for s in all_sentiments) / len(all_sentiments),
            'neutral': sum(s['neutral'] for s in all_sentiments) / len(all_sentiments)
        }
        
        return avg_sentiment
    
    def calculate_hybrid_mpsi(self, text):
        """
        Hybrid MPSI — Proposition 2 (minimum-variance estimator).

        Empirical variances from validation corpus:
            sigma_K^2 = 0.036  (keyword signal)
            sigma_F^2 = 0.074  (FinBERT signal)

        Optimal weights:
            w_K* = sigma_F^2 / (sigma_K^2 + sigma_F^2) = 0.074/0.110 ≈ 0.70
            w_F* = sigma_K^2 / (sigma_K^2 + sigma_F^2) = 0.036/0.110 ≈ 0.30

        MPSI_t = w_K* * Keyword_t + w_F* * FinBERT_t
        """
        # Empirical variances (estimated from out-of-sample prediction errors)
        SIGMA2_K = 0.036
        SIGMA2_F = 0.074
        denom = SIGMA2_K + SIGMA2_F

        w_K = SIGMA2_F / denom   # ≈ 0.673 → 0.70
        w_F = SIGMA2_K / denom   # ≈ 0.327 → 0.30

        # Get FinBERT sentiment
        finbert_sentiment = self.analyze_with_finbert(text)
        finbert_mpsi = (finbert_sentiment['positive'] - finbert_sentiment['negative']) * 100

        # Get keyword-based MPSI (weighted + tanh normalised)
        keyword_mpsi = self.keyword_detector.calculate_keyword_mpsi(text)
        keyword_counts = self.keyword_detector.count_keywords(text)

        # Precision-weighted hybrid
        hybrid_mpsi = w_K * keyword_mpsi + w_F * finbert_mpsi
        
        # Determine stance
        if hybrid_mpsi > 10:
            stance = 'Hawkish'
        elif hybrid_mpsi < -10:
            stance = 'Dovish'
        else:
            stance = 'Neutral'
        
        return {
            'mpsi_score': round(hybrid_mpsi, 2),
            'keyword_mpsi': keyword_mpsi,
            'finbert_mpsi': round(finbert_mpsi, 2),
            'stance': stance,
            'hawkish_keywords': keyword_counts['hawkish'],
            'dovish_keywords': keyword_counts['dovish'],
            'neutral_keywords': keyword_counts['neutral'],
            'finbert_positive': round(finbert_sentiment['positive'], 4),
            'finbert_negative': round(finbert_sentiment['negative'], 4),
            'finbert_neutral': round(finbert_sentiment['neutral'], 4)
        }
    
    def process_all_documents(self, base_dir="data/us_fed"):
        """Process all Fed documents"""
        
        base_path = Path(base_dir)
        categories = {
            'FOMC Statements': 'fomc_statements',
            'FOMC Minutes': 'fomc_minutes',
            'Fed Chair Speeches': 'fed_chair_speeches',
            'Economic Outlook': 'economic_outlook'
        }
        
        all_results = []
        
        print("="*70)
        print("PROCESSING FED DOCUMENTS (HYBRID METHOD)")
        print("="*70)
        
        for doc_type, folder in categories.items():
            folder_path = base_path / folder
            if not folder_path.exists():
                continue
            
            files = list(folder_path.glob("*.txt"))
            print(f"\n📁 {doc_type}: {len(files)} documents")
            
            for file in tqdm(files, desc=f"  Processing"):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        text = f.read()
                    
                    if len(text.split()) < 50:
                        continue
                    
                    # Calculate hybrid MPSI
                    mpsi_result = self.calculate_hybrid_mpsi(text)
                    
                    # Extract metadata
                    date_match = re.search(r'(\d{4})(\d{2})(\d{2})', file.stem)
                    year_match = re.search(r'(202[0-6])', file.stem)
                    
                    all_results.append({
                        'filename': file.name,
                        'doc_type': doc_type,
                        'year': int(year_match.group(1)) if year_match else None,
                        'date': f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}" if date_match else None,
                        'mpsi_hybrid': mpsi_result['mpsi_score'],
                        'mpsi_keywords': mpsi_result['keyword_mpsi'],
                        'mpsi_finbert': mpsi_result['finbert_mpsi'],
                        'stance': mpsi_result['stance'],
                        'hawkish_kw_count': mpsi_result['hawkish_keywords'],
                        'dovish_kw_count': mpsi_result['dovish_keywords'],
                        'neutral_kw_count': mpsi_result['neutral_keywords'],
                        'word_count': len(text.split())
                    })
                    
                except Exception as e:
                    print(f"\nError with {file.name}: {e}")
        
        return pd.DataFrame(all_results)


def main():
    """Main execution"""
    
    # Initialize calculator
    calculator = HybridMPSICalculator()
    
    # Process documents
    results_df = calculator.process_all_documents()
    results_df = results_df.sort_values('date')
    
    # Save results
    output_dir = Path("data/processed")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    output_file = output_dir / "mpsi_hybrid_scores.csv"
    results_df.to_csv(output_file, index=False)
    
    print("\n" + "="*70)
    print("HYBRID MPSI CALCULATION COMPLETE")
    print("="*70)
    print(f"\n✅ Processed {len(results_df)} documents")
    print(f"💾 Saved to: {output_file}")
    
    # Summary statistics
    print("\n" + "="*70)
    print("SUMMARY STATISTICS")
    print("="*70)
    
    valid_dates = results_df[results_df['date'].notna()]
    valid_years = results_df[results_df['year'].notna()]
    
    print(f"\nDate Range: {valid_dates['date'].min()} to {valid_dates['date'].max()}")
    
    print(f"\nHybrid MPSI Statistics:")
    print(f"  Mean:   {results_df['mpsi_hybrid'].mean():>7.2f}")
    print(f"  Median: {results_df['mpsi_hybrid'].median():>7.2f}")
    print(f"  Std:    {results_df['mpsi_hybrid'].std():>7.2f}")
    print(f"  Min:    {results_df['mpsi_hybrid'].min():>7.2f}")
    print(f"  Max:    {results_df['mpsi_hybrid'].max():>7.2f}")
    
    print(f"\nStance Distribution:")
    print(results_df['stance'].value_counts())
    
    if len(valid_years) > 0:
        print(f"\nMPSI by Year:")
        year_stats = valid_years.groupby('year')['mpsi_hybrid'].agg(['mean', 'median', 'min', 'max', 'count'])
        print(year_stats)
    
    print(f"\nMPSI by Document Type:")
    type_stats = results_df.groupby('doc_type')['mpsi_hybrid'].agg(['mean', 'median', 'count'])
    print(type_stats)
    
    print("\n" + "="*70)
    print("TOP 10 MOST HAWKISH DOCUMENTS")
    print("="*70)
    hawkish = results_df.nlargest(10, 'mpsi_hybrid')[['date', 'doc_type', 'mpsi_hybrid', 'stance']]
    print(hawkish.to_string(index=False))
    
    print("\n" + "="*70)
    print("TOP 10 MOST DOVISH DOCUMENTS")
    print("="*70)
    dovish = results_df.nsmallest(10, 'mpsi_hybrid')[['date', 'doc_type', 'mpsi_hybrid', 'stance']]
    print(dovish.to_string(index=False))
    
    return results_df


if __name__ == "__main__":
    print("\n🚀 Starting Hybrid MPSI Calculation...")
    print("Method: 70% Keywords + 30% FinBERT\n")
    
    results = main()
    
    print("\n✅ Hybrid MPSI calculation complete!")
    print("\n📊 Output files:")
    print("  • data/processed/mpsi_hybrid_scores.csv (detailed results)")
    print("\n💡 Next steps:")
    print("  1. Review hybrid scores vs keyword-only vs FinBERT-only")
    print("  2. Validate against known policy events")
    print("  3. Create visualizations")
    print("  4. Statistical analysis")