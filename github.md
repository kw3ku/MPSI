# 🛠️ MPSI Build Plan
**fedmpsi.com + github.com/kw3ku/MPSI**

---

## Step 1 — GitHub Repository Structure

```
📁 MPSI/                          ← public repo
├── README.md
├── requirements.txt
├── LICENSE
├── .gitignore
│
├── 📁 src/
│   ├── mpsi_calculator.py
│   ├── keyword_scorer.py
│   ├── finbert_model.py
│   ├── preprocessing.py
│   └── hybrid_weights.py
│
├── 📁 data/
│   ├── hawkish_keywords.csv
│   ├── dovish_keywords.csv
│   └── README_data.md
│
├── 📁 notebooks/
│   ├── 01_data_collection.ipynb
│   ├── 02_keyword_scoring.ipynb
│   ├── 03_finbert_finetuning.ipynb
│   ├── 04_hybrid_mpsi.ipynb
│   ├── 05_validation.ipynb
│   └── 06_figures.ipynb
│
├── 📁 results/
│   ├── mpsi_scores.csv
│   ├── correlation_results.csv
│   └── granger_results.csv
│
└── 📁 paper/
    └── MPSI_SSRN_6859459.pdf
```

---

## Step 2 — README.md Template

```markdown
# Automated Monetary Policy Sentiment Index (MPSI)

A hybrid NLP framework combining FinBERT transformers 
with Taylor Rule keywords to measure Federal Reserve 
communication stance in real time.

## Paper
Dompreh, F. (2026). "Automated Monetary Policy Sentiment 
Index (MPSI)." SSRN Working Paper 6859459.
https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6859459

## Dashboard
https://fedmpsi.com

## Key Results
- r = 0.689 with Federal Funds Rate (p<0.001)
- Explains 47.5% of FFR variance
- Granger-causes FFR changes 2–3 months ahead
- 10-pt surprise → 42.3 bps on 2Y Treasury yields
- Outperforms benchmarks by 17–67%

## Installation
pip install -r requirements.txt

## Usage
from src.mpsi_calculator import calculate_mpsi
score = calculate_mpsi("your fed document text here")
print(score)

## Citation
@techreport{dompreh2026mpsi,
  title={Automated Monetary Policy Sentiment Index (MPSI)},
  author={Dompreh, Foster},
  year={2026},
  institution={University of Wisconsin - Madison},
  note={SSRN Working Paper 6859459}
}

## License
MIT License — see LICENSE file
```

---

## Step 3 — requirements.txt

```
transformers==4.40.0
torch==2.3.0
pandas==2.2.0
numpy==1.26.0
scikit-learn==1.4.0
scipy==1.13.0
statsmodels==0.14.0
matplotlib==3.8.0
seaborn==0.13.0
plotly==5.20.0
requests==2.31.0
beautifulsoup4==4.12.0
nltk==3.8.1
huggingface_hub==0.22.0
streamlit==1.33.0
python-dotenv==1.0.0
```

---

## Step 4 — .gitignore

```
# Model weights — use HuggingFace instead
*.pt
*.bin
*.pkl
models/

# Raw data — copyright
data/raw/
data/pdfs/

# Environment
.env
.env.local
.env.production
credentials.json
secrets/

# Python
__pycache__/
*.pyc
*.pyo
.Python
env/
venv/
.venv/

# Mac
.DS_Store
.AppleDouble

# LaTeX source — wait for journal acceptance
*.tex
*.aux
*.log
*.out
*.synctex.gz

# NIW private files
NIW_Evidence/

# Jupyter checkpoints
.ipynb_checkpoints/
```

---

## Step 5 — Dashboard Stack (fedmpsi.com)

### Recommended: Streamlit (fastest to build)

```
Private repo: github.com/kw3ku/MPSI-dashboard

📁 MPSI-dashboard/
├── app.py               ← main Streamlit app
├── requirements.txt
├── .env                 ← API keys — NEVER push
├── .gitignore
│
├── 📁 components/
│   ├── mpsi_chart.py    ← time series plot
│   ├── live_score.py    ← current MPSI value
│   ├── correlation.py   ← FFR correlation chart
│   └── doc_breakdown.py ← by document type
│
└── 📁 data/
    └── mpsi_scores.csv  ← pull from public repo
```

### app.py Skeleton

```python
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="MPSI Dashboard — fedmpsi.com",
    page_icon="🏦",
    layout="wide"
)

st.title("Monetary Policy Sentiment Index (MPSI)")
st.markdown("""
**Real-time Federal Reserve communication tracker**  
[Paper](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6859459) | 
[Code](https://github.com/kw3ku/MPSI) | 
[ORCID](https://orcid.org/0009-0003-2566-2238)
""")

# Load data
df = pd.read_csv("data/mpsi_scores.csv")

# MPSI Time Series
st.subheader("MPSI Over Time (2020–2026)")
fig = px.line(df, x="date", y="mpsi_score",
              title="MPSI — Hawkish (+) vs Dovish (-)")
fig.add_hline(y=0, line_dash="dash", line_color="gray")
st.plotly_chart(fig, use_container_width=True)

# Current Score
col1, col2, col3 = st.columns(3)
col1.metric("Current MPSI", f"{df['mpsi_score'].iloc[-1]:.1f}")
col2.metric("Current FFR", "5.25%")
col3.metric("Correlation r", "0.689")

# Download data
st.download_button(
    label="Download MPSI Data (CSV)",
    data=df.to_csv(index=False),
    file_name="mpsi_scores.csv",
    mime="text/csv"
)
```

### Deploy to Streamlit Cloud (Free)

```
1. Push MPSI-dashboard to GitHub (private is fine)
2. Go to: share.streamlit.io
3. Connect GitHub account
4. Select repo: kw3ku/MPSI-dashboard
5. Main file: app.py
6. Click Deploy
7. Point fedmpsi.com DNS to Streamlit URL
```

---

## Step 6 — HuggingFace Model Upload

```python
# Run once to upload your fine-tuned FinBERT
from huggingface_hub import HfApi

api = HfApi()
api.upload_folder(
    folder_path="./models/finbert_mpsi",
    repo_id="kw3ku/finbert-mpsi",
    repo_type="model",
    commit_message="MPSI FinBERT v1.0 — SSRN 6859459"
)

# Your model will be at:
# https://huggingface.co/kw3ku/finbert-mpsi
```

---

## Step 7 — Terminal Commands for Tomorrow

```bash
# Navigate to project
cd /Users/kddv/py_works/nlp_finance

# Check what files exist
ls -la

# Initialize git if needed
git init

# Create .gitignore first
nano .gitignore    # paste Step 4 content

# Stage only safe files
git add README.md
git add requirements.txt
git add LICENSE
git add src/
git add data/hawkish_keywords.csv
git add data/dovish_keywords.csv
git add notebooks/
git add results/
git add paper/MPSI_SSRN_6859459.pdf

# Check what you are about to push
git status

# Commit and push
git commit -m "MPSI v1.0 — public release — SSRN 6859459"
git branch -M main
git remote add origin https://github.com/kw3ku/MPSI
git push -u origin main
```

---

## Tomorrow's Build Order

```
Morning:
□ 1. Create .gitignore
□ 2. Write README.md
□ 3. Create requirements.txt
□ 4. Run git status — check nothing sensitive
□ 5. Push to github.com/kw3ku/MPSI

Afternoon:
□ 6. Create MPSI-dashboard repo (private)
□ 7. Build app.py with Streamlit skeleton
□ 8. Test locally: streamlit run app.py
□ 9. Deploy to Streamlit Cloud
□ 10. Point fedmpsi.com DNS to deployment

Evening:
□ 11. Upload FinBERT model to HuggingFace
□ 12. Add HuggingFace link to README
□ 13. Final check — visit fedmpsi.com
□ 14. Screenshot everything for NIW evidence
```

---

*Build plan created: May 30, 2026*
*SSRN: 6859459 | GitHub: kw3ku/MPSI | Dashboard: fedmpsi.com*