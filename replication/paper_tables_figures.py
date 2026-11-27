"""
Generates the descriptive tables and figures used in the revised working paper
from the published scores. Usage: python replication/paper_tables_figures.py
Outputs: replication/output/paper/*.csv, *.png, weights.txt, keywords.txt
"""
from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ffr_validation import monthly_fred, handcoded
from paper_v1 import PolicyKeywordDetector as KeywordMPSI  # noqa

HERE = Path(__file__).resolve().parent; ROOT = HERE.parent
OUT = HERE/'output'/'paper'; OUT.mkdir(parents=True, exist_ok=True)
all_ = pd.read_csv(ROOT/'data'/'processed'/'mpsi_hybrid_scores.csv', parse_dates=['date'])
df = all_.dropna(subset=['date'])
hand = handcoded(HERE/'data'/'fed_funds_paper_handcoded.csv'); handA = hand[hand.index <= '2025-03']
fred = monthly_fred(HERE/'data'/'fred_dff_snapshot_2026-03-19.csv')
mon = lambda d, c: d.set_index('date').resample('ME')[c].mean().dropna().to_period('M')

# by year (all 119 documents; year column from file)
by = all_.groupby('year').mpsi_hybrid.agg(['count','mean','median','std','min','max']).round(1)
by.loc['All'] = all_.mpsi_hybrid.agg(['count','mean','median','std','min','max']).round(1)
by.to_csv(OUT/'by_year.csv'); print(by)
st = pd.crosstab(all_.year, all_.stance); st.to_csv(OUT/'stance_by_year.csv'); print(st)
print(all_[['mpsi_hybrid','mpsi_keywords','mpsi_finbert','word_count','hawkish_kw_count','dovish_kw_count','neutral_kw_count']].describe().round(1))
print('corr kw/finbert docs', round(all_.mpsi_keywords.corr(all_.mpsi_finbert),3))

# regression, main sample
d = pd.DataFrame({'m': mon(df,'mpsi_hybrid'), 'f': handA}).dropna()
lr = stats.linregress(d.m, d.f); print('OLS', round(lr.intercept,3), round(lr.slope,4), round(lr.rvalue,4), lr.pvalue, round(lr.stderr,4), len(d))

# precision weights from residual variances (theory section procedure)
lines=[]
for name, f in [('A_paper_47m', handA), ('B_fred_47m', fred[fred.index <= '2025-03']), ('C_fred_55m', fred)]:
    x = pd.DataFrame({'k': mon(df,'mpsi_keywords'), 'b': mon(df,'mpsi_finbert'), 'f': f}).dropna()
    rk = stats.linregress(x.k, x.f); rb = stats.linregress(x.b, x.f)
    sk = np.mean((x.f-(rk.intercept+rk.slope*x.k))**2); sb = np.mean((x.f-(rb.intercept+rb.slope*x.b))**2)
    lines.append(f"{name}: n={len(x)} beta_K={rk.slope:.4f} beta_F={rb.slope:.4f} sigma2_K={sk:.3f} sigma2_F={sb:.3f} w_K={sb/(sk+sb):.3f} w_F={sk/(sk+sb):.3f}")
(OUT/'weights.txt').write_text('\n'.join(lines)); print('\n'.join(lines))

# keyword lists
try:
    K = KeywordMPSI
    txt = f"HAWKISH ({len(K.HAWKISH_KEYWORDS)}): " + ', '.join(K.HAWKISH_KEYWORDS) + f"\nDOVISH ({len(K.DOVISH_KEYWORDS)}): " + ', '.join(K.DOVISH_KEYWORDS) + f"\nNEUTRAL ({len(K.NEUTRAL_KEYWORDS)}): " + ', '.join(K.NEUTRAL_KEYWORDS)
    (OUT/'keywords.txt').write_text(txt); print(txt)
except Exception as e: print('keywords', e)

# figures
plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})
col = {'FOMC Statements':'#1f4e79','FOMC Minutes':'#c55a11'}
fig, ax = plt.subplots(figsize=(8,3.8))
for t,g in df.groupby('doc_type'): ax.scatter(g.date, g.mpsi_hybrid, s=16, color=col.get(t,'#666'), label=t, alpha=.8)
ax.axhline(10, color='#999', lw=.7, ls='--'); ax.axhline(-10, color='#999', lw=.7, ls='--'); ax.axhline(0, color='#444', lw=.6)
ax.set_ylabel('MPSI'); ax.legend(frameon=False); fig.tight_layout(); fig.savefig(OUT/'fig_mpsi_documents.png', dpi=200); plt.close(fig)

m = mon(df,'mpsi_hybrid'); fig, ax = plt.subplots(figsize=(8,3.8)); ax2 = ax.twinx(); ax2.spines['right'].set_visible(True)
ax.plot(m.index.to_timestamp(), m.values, color='#1f4e79', marker='o', ms=3, lw=1.2, label='MPSI (monthly mean, left)')
f = fred[(fred.index >= '2020-01') & (fred.index <= '2026-01')]; ax2.plot(f.index.to_timestamp(), f.values, color='#c00000', lw=1.4, label='Federal funds rate, % (right)')
ax.set_ylabel('MPSI'); ax2.set_ylabel('Percent'); h1,l1 = ax.get_legend_handles_labels(); h2,l2 = ax2.get_legend_handles_labels(); ax.legend(h1+h2, l1+l2, frameon=False, loc='upper left'); fig.tight_layout(); fig.savefig(OUT/'fig_mpsi_vs_ffr.png', dpi=200); plt.close(fig)

fig, ax = plt.subplots(figsize=(5.2,4)); ax.scatter(d.m, d.f, s=18, color='#1f4e79'); xs = np.linspace(d.m.min(), d.m.max(), 50); ax.plot(xs, lr.intercept+lr.slope*xs, color='#c00000', lw=1.2)
ax.set_xlabel('MPSI (monthly mean)'); ax.set_ylabel('Federal funds rate, %'); fig.tight_layout(); fig.savefig(OUT/'fig_scatter.png', dpi=200); plt.close(fig)

ws = pd.read_csv(HERE/'output'/'weight_sensitivity.csv'); fig, ax = plt.subplots(figsize=(5.2,3.6))
for c,lab in [('A_paper_47m','Main sample (47 months)'),('C_fred_55m','FRED, all months (55)')]: ax.plot(ws.w_keyword, ws[c], marker='o', ms=3, label=lab)
ax.axvline(0.7, color='#999', ls='--', lw=.8); ax.axhline(0, color='#444', lw=.6); ax.set_xlabel('Keyword weight $w_K$'); ax.set_ylabel('Correlation with federal funds rate'); ax.legend(frameon=False); fig.tight_layout(); fig.savefig(OUT/'fig_weight_sensitivity.png', dpi=200); plt.close(fig)
