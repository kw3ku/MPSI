"""
Additional descriptive checks on the published scores (no new modelling):
  1. correlation with the Fed Funds Rate for keyword-only, FinBERT-only and hybrid scores
  2. sensitivity of that correlation to the keyword weight w_K (0.0 ... 1.0)
  3. correlation by document type and average score by policy period
Uses the same monthly averaging and the same three FFR specifications as ffr_validation.py.
Usage: python replication/component_checks.py
"""
from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats
from ffr_validation import monthly_fred, handcoded

HERE = Path(__file__).resolve().parent; ROOT = HERE.parent
df = pd.read_csv(ROOT/'data'/'processed'/'mpsi_hybrid_scores.csv', parse_dates=['date']).dropna(subset=['date'])
hand = handcoded(HERE/'data'/'fed_funds_paper_handcoded.csv')
fred = monthly_fred(HERE/'data'/'fred_dff_snapshot_2026-03-19.csv')

def monthly(d, col): return d.set_index('date').resample('ME')[col].mean().dropna().to_period('M')
def corr(m, f):
    d = pd.DataFrame({'m': m, 'f': f}).dropna(); n = len(d); r = d.m.corr(d.f)
    t = r*np.sqrt(n-2)/np.sqrt(1-r**2); p = 2*(1-stats.t.cdf(abs(t), n-2))
    return n, round(r,3), float(f"{p:.2g}")
handA = hand[hand.index <= '2025-03']
specs = {'A_paper_47m': handA, 'B_fred_47m': fred[fred.index <= '2025-03'], 'C_fred_55m': fred}

rows=[]
for name,col in [('keyword_only','mpsi_keywords'),('finbert_only','mpsi_finbert'),('hybrid_70_30','mpsi_hybrid')]:
    for s,f in specs.items(): rows.append((name,s)+corr(monthly(df,col),f))
comp=pd.DataFrame(rows,columns=['score','spec','n','r','p']); print(comp.to_string(index=False)); comp.to_csv(HERE/'output'/'component_correlations.csv',index=False)

rows=[]
for w in np.arange(0,1.01,0.1):
    d=df.assign(x=w*df.mpsi_keywords+(1-w)*df.mpsi_finbert)
    rows.append((round(w,1),)+tuple(corr(monthly(d,'x'),f)[1] for f in specs.values()))
ws=pd.DataFrame(rows,columns=['w_keyword']+list(specs)); print(ws.to_string(index=False)); ws.to_csv(HERE/'output'/'weight_sensitivity.csv',index=False)

rows=[]
for t,g in df.groupby('doc_type'):
    for s,f in specs.items(): rows.append((t,s)+corr(monthly(g,'mpsi_hybrid'),f))
dt=pd.DataFrame(rows,columns=['doc_type','spec','n','r','p']); print(dt.to_string(index=False)); dt.to_csv(HERE/'output'/'doc_type_correlations.csv',index=False)

m=monthly(df,'mpsi_hybrid'); per={'2020-01..2021-12 (pandemic easing)':('2020-01','2021-12'),'2022-01..2023-07 (tightening)':('2022-01','2023-07'),'2023-08..2024-08 (hold at peak)':('2023-08','2024-08'),'2024-09..2026-01 (easing)':('2024-09','2026-01')}
rows=[(k,len(m[a:b]),round(m[a:b].mean(),1),round(fred[a:b].mean(),2)) for k,(a,b) in per.items()]
pr=pd.DataFrame(rows,columns=['period','months_with_docs','mean_mpsi','mean_ffr']); print(pr.to_string(index=False)); pr.to_csv(HERE/'output'/'period_means.csv',index=False)
all_=pd.read_csv(ROOT/'data'/'processed'/'mpsi_hybrid_scores.csv')
print(all_.groupby('doc_type').mpsi_hybrid.agg(['count','mean','min','max']).round(1)); print(all_.stance.value_counts())
