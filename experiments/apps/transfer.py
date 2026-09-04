import pyarrow.parquet as pq, glob, numpy as np, pandas as pd, re
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import roc_auc_score
cols=["problem_id","difficulty","solutions","backdoors"]
df=pd.concat([pq.read_table(f,columns=cols).to_pandas() for f in sorted(glob.glob("train_*.parquet"))],ignore_index=True)
rows=[]
for _,r in df.iterrows():
    for src in ["control_tax","apps"]:
        bds=[b for b in r.backdoors if b["source"]==src]
        for sol,bd in zip(r.solutions,bds):
            rows.append(dict(pid=r.problem_id,src=src,honest=sol["code"],attack=bd["backdoor_code"],bd_works=bd["backdoor_works"],model=bd["model"]))
p=pd.DataFrame(rows)
vec=TfidfVectorizer(token_pattern=r'[A-Za-z_]+|\d+|[^\sA-Za-z_\d]',ngram_range=(1,2),min_df=3,max_features=50000,sublinear_tf=True)
def fit(tr):
    X=vec.fit_transform(list(tr.honest)+list(tr.attack)); y=np.r_[np.zeros(len(tr)),np.ones(len(tr))]
    return LogisticRegression(max_iter=3000).fit(X,y)
def pairacc(clf,te):
    sa=clf.predict_proba(vec.transform(list(te.attack)))[:,1]; sh=clf.predict_proba(vec.transform(list(te.honest)))[:,1]; return (sa>sh).mean()
ct=p[p.src=="control_tax"]; ap=p[p.src=="apps"]
# problem-disjoint: apps-source problems removed from training
tr=ct[~ct.pid.isin(set(ap.pid))]
clf=fit(tr); print("train control_tax (n=%d, problems disjoint) -> test apps-source GPT-4-era backdoors (n=%d): pairwise acc %.4f"%(len(tr),len(ap),pairacc(clf,ap)))
# cross-model within control_tax, problem-disjoint
for a,b in [("openai/o3-mini","anthropic/claude-3-7-sonnet-latest"),("anthropic/claude-3-7-sonnet-latest","openai/o3-mini"),("openai/o1-mini","google/gemini-2.0-flash")]:
    tr=ct[ct.model==a]; te=ct[(ct.model==b)&(~ct.pid.isin(set(tr.pid)))]
    clf=fit(tr); print("train %s (n=%d) -> test %s (n=%d, problem-disjoint): pairwise acc %.4f"%(a,len(tr),b,len(te),pairacc(clf,te)))
# comment/docstring/whitespace style markers
def style(code): return dict(has_comment=('#' in code), has_def=bool(re.search(r'\bdef\b',code)), has_main=('__main__' in code), n_blank=code.count('\n\n'), has_typehint=bool(re.search(r'->|: int|: str|: list',code)), input_style=('sys.stdin' in code))
S=pd.DataFrame([dict(cls='honest',**style(c)) for c in ct.honest]+[dict(cls='attack',**style(c)) for c in ct.attack])
print("\nstyle markers, control_tax pairs:\n", S.groupby('cls').mean().round(3).T)
# show one pair
r=ct.iloc[7]; print("\n===== HONEST (pid %s)\n"%r.pid, r.honest[:700]); print("\n===== ATTACK (model %s, works=%s)\n"%(r.model,r.bd_works), r.attack[:900])
