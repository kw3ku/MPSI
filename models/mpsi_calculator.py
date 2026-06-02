"""
Hybrid MPSI Calculator
Combines FinBERT sentiment + Policy-specific keywords
More accurate for Fed monetary policy documents
"""

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
    Detect monetary policy stance using keyword analysis
    """
    
    # Hawkish keywords (tightening policy)
    HAWKISH_KEYWORDS = [
        'tighten', 'tightening', 'raise rates', 'raising rates', 
        'increase rates', 'increasing rates', 'rate increase',
        'reduce accommodation', 'removing accommodation', 'withdraw',
        'restrict', 'restrictive', 'restrictive policy',
        'inflation risk', 'inflation risks', 'overheating', 
        'elevated inflation', 'high inflation', 'rising inflation',
        'appropriate to raise', 'appropriate to increase',
        'gradually raising', 'gradual increases',
        'balance sheet reduction', 'quantitative tightening',
        'runoff', 'reducing holdings', 'expedite', 'front-load'
    ]
    
    # Dovish keywords (easing policy)
    DOVISH_KEYWORDS = [
        'ease', 'easing', 'lower rates', 'lowering rates',
        'decrease rates', 'decreasing rates', 'rate decrease', 'rate cut',
        'accommodate', 'accommodation', 'accommodative',
        'support', 'supportive', 'highly accommodative',
        'downside risk', 'downside risks', 'economic weakness',
        'subdued inflation', 'low inflation', 'below target',
        'appropriate to maintain', 'maintain rates',
        'asset purchases', 'purchase assets', 'quantitative easing',
        'remain patient', 'patient approach', 'patient stance',
        'considerable time', 'extended period'
    ]
    
    # Neutral/assessment keywords (informational, not directional)
    NEUTRAL_KEYWORDS = [
        'monitor', 'monitoring', 'assess', 'assessing',
        'evaluate', 'evaluating', 'review', 'reviewing',
        'consider', 'considering', 'data-dependent',
        'flexible', 'appropriate', 'outlook'
    ]
    
    def count_keywords(self, text):
        """Count policy keyword occurrences"""
        
        text_lower = text.lower()
        
        hawkish_count = sum(1 for kw in self.HAWKISH_KEYWORDS if kw in text_lower)
        dovish_count = sum(1 for kw in self.DOVISH_KEYWORDS if kw in text_lower)
        neutral_count = sum(1 for kw in self.NEUTRAL_KEYWORDS if kw in text_lower)
        
        return {
            'hawkish': hawkish_count,
            'dovish': dovish_count,
            'neutral': neutral_count,
            'total': hawkish_count + dovish_count + neutral_count
        }
    
    def calculate_keyword_mpsi(self, text):
        """Calculate MPSI from keywords alone"""
        
        counts = self.count_keywords(text)
        
        if counts['total'] == 0:
            return 0  # No policy keywords found, return neutral
        
        # MPSI = (Hawkish - Dovish) / Total * 100
        mpsi = ((counts['hawkish'] - counts['dovish']) / counts['total']) * 100
        
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
        Calculate MPSI using hybrid approach:
        - 70% weight on keyword-based (more accurate for policy)
        - 30% weight on FinBERT sentiment (captures overall tone)
        """
        
        # Get FinBERT sentiment
        finbert_sentiment = self.analyze_with_finbert(text)
        finbert_mpsi = (finbert_sentiment['positive'] - finbert_sentiment['negative']) * 100
        
        # Get keyword-based MPSI
        keyword_mpsi = self.keyword_detector.calculate_keyword_mpsi(text)
        keyword_counts = self.keyword_detector.count_keywords(text)
        
        # Hybrid MPSI (70% keywords, 30% FinBERT)
        # Keyword method is more reliable for policy stance
        if keyword_counts['total'] > 0:
            # If we have policy keywords, weight them heavily
            hybrid_mpsi = (0.70 * keyword_mpsi) + (0.30 * finbert_mpsi)
        else:
            # If no policy keywords, rely more on FinBERT
            hybrid_mpsi = finbert_mpsi
        
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