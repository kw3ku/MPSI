"""
MPSI scorer exactly as used for the SSRN paper (Working Paper 6859459).

This file is a frozen copy of the scorer that produced
data/processed/mpsi_hybrid_scores.csv. The two classes below are copied
verbatim from the research script (01-mpsi_hybrid.py); do not edit them,
or the published scores will no longer reproduce.

What this version actually does (see REPLICATION.md for discussion):
    Keyword_t = 100 * (H_t - D_t) / (H_t + D_t + N_t)
        H, D, N = number of distinct hawkish / dovish / neutral phrases
        present in the document (presence, not frequency; no omega_w weights)
    FinBERT_t = 100 * (P(positive) - P(negative)), averaged over up to 10
        400-word chunks, using the stock ProsusAI/finbert checkpoint
    MPSI_t    = 0.70 * Keyword_t + 0.30 * FinBERT_t
        (MPSI_t = FinBERT_t when no keyword is present)

The dashboard scorer in models/mpsi_calculator.py is a later version and
gives different numbers.

Usage:
    python replication/paper_v1.py --keywords-only   # no torch needed
    python replication/paper_v1.py                   # full hybrid (downloads FinBERT)
"""

import argparse
import re
import warnings
from pathlib import Path

import pandas as pd
from tqdm import tqdm

try:
    import torch
    from transformers import BertTokenizer, BertForSequenceClassification
except ImportError:  # keyword-only replication does not need them
    torch = None

warnings.filterwarnings('ignore')

HERE = Path(__file__).resolve().parent
DEFAULT_CORPUS = HERE / 'corpus' / 'us_fed'


# ---------------------------------------------------------------------------
# Verbatim from 01-mpsi_hybrid.py (paper version) — do not modify
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# End of verbatim section
# ---------------------------------------------------------------------------

CATEGORIES = {
    'FOMC Statements': 'fomc_statements',
    'FOMC Minutes': 'fomc_minutes',
    'Fed Chair Speeches': 'fed_chair_speeches',
    'Economic Outlook': 'economic_outlook',
}


def score_keywords_only(base_dir):
    """Same document filter and metadata as process_all_documents, keyword columns only."""
    detector = PolicyKeywordDetector()
    rows = []
    for doc_type, folder in CATEGORIES.items():
        folder_path = Path(base_dir) / folder
        if not folder_path.exists():
            continue
        for file in sorted(folder_path.glob("*.txt")):
            text = file.read_text(encoding='utf-8')
            if len(text.split()) < 50:
                continue
            counts = detector.count_keywords(text)
            date_match = re.search(r'(\d{4})(\d{2})(\d{2})', file.stem)
            year_match = re.search(r'(202[0-6])', file.stem)
            rows.append({
                'filename': file.name,
                'doc_type': doc_type,
                'year': int(year_match.group(1)) if year_match else None,
                'date': f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}" if date_match else None,
                'mpsi_keywords': detector.calculate_keyword_mpsi(text),
                'hawkish_kw_count': counts['hawkish'],
                'dovish_kw_count': counts['dovish'],
                'neutral_kw_count': counts['neutral'],
                'word_count': len(text.split()),
            })
    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[1])
    parser.add_argument('--corpus', default=str(DEFAULT_CORPUS))
    parser.add_argument('--keywords-only', action='store_true',
                        help='skip FinBERT; output keyword columns only')
    parser.add_argument('--out', default=None)
    args = parser.parse_args()

    if args.keywords_only:
        df = score_keywords_only(args.corpus)
        out = args.out or HERE / 'output' / 'rebuilt_keyword_scores.csv'
    else:
        if torch is None:
            raise SystemExit("torch/transformers not installed; use --keywords-only or pip install -r requirements.txt")
        df = HybridMPSICalculator().process_all_documents(args.corpus)
        out = args.out or HERE / 'output' / 'rebuilt_hybrid_scores.csv'

    df = df.sort_values(['date', 'doc_type', 'filename'], na_position='last')
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"Scored {len(df)} documents -> {out}")


if __name__ == "__main__":
    main()
