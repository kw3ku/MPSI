# MPSI
An approach to quantizing Federal Research Monetary Policy. Monetary Policy Sentiment Index (MPSI) provides a scoring approach to rate FOMC statements.

## MPSI scoring

This repository now includes a minimal, lexicon-based Monetary Policy Sentiment Index implementation for FOMC statement text.

- Hawkish terms increase the score
- Dovish terms decrease the score
- Scores are normalized to a `0-100` scale
  - `<45`: dovish
  - `45-55`: neutral
  - `>55`: hawkish

## Quick usage

```python
from mpsi import score_statement

result = score_statement("Inflation remains elevated and policy may need further tightening.")
print(result["normalized_score"], result["label"])
```
