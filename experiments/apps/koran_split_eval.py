"""Train bag-of-words on Koran et al. (2605.15377)'s paired train split; score their exact 1,375-item test split.
Requires K1's data.py (Jha's strip_comments/_pick_backdoor/_honest_code port), koran_meta.parquet, koran_samples.pkl,
monitor-summary.json (Jha's runs/x0) and the RoganInglis parquet shards. Output on 2026-09-03:
  [stripped] word1-2: AUROC=0.8063 pAUC@10%=0.3243 TPR@10%FPR=0.4767; monitors below it: 20/24
  [stripped] char3-5: AUROC=0.7830 ... 20/24
  [code    ] word1-2: AUROC=0.8914 pAUC@10%=0.6320 TPR@10%FPR=0.7558; 22/24
  [code    ] char3-5: AUROC=0.8778 ... 22/24
"""
import pandas as pd, numpy as np, sys, json, glob, pyarrow.parquet as pq
sys.path.insert(0,".")
from data import strip_comments, _pick_backdoor, _honest_code
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, roc_curve
km=pd.read_parquet("koran_meta.parquet"); test=pd.read_pickle("koran_samples.pkl")
test_pids=set(test.problem_id.astype(str)); train_pids=set(km.problem_id.astype(str))-test_pids
full=pd.concat([pq.read_table(f,columns=["problem_id","solutions","backdoors"]).to_pandas() for f in sorted(glob.glob("train_*.parquet"))],ignore_index=True)
full=full[full.problem_id.astype(str).isin(train_pids)]
tbm=dict(zip(km.problem_id.astype(str),km.top_backdoor_model))
rows=[]
for _,r in full.iterrows():
    row={"problem_id":str(r.problem_id),"backdoors":[dict(b) for b in r.backdoors],"solutions":[dict(s) for s in r.solutions],"top_backdoor_model":tbm.get(str(r.problem_id))}
    bd=_pick_backdoor(row); hc=_honest_code(row)
    if bd is None or hc is None: continue
    rows.append((row["problem_id"],1,bd["backdoor_code"])); rows.append((row["problem_id"],0,hc))
tr=pd.DataFrame(rows,columns=["problem_id","label","code"]); tr["stripped"]=tr.code.map(strip_comments)
def pauc_tpr(y,s,f=0.1):
    fpr,tpr,_=roc_curve(y,s); m=fpr<=f; fp=np.r_[fpr[m],f]; tp=np.r_[tpr[m],np.interp(f,fpr,tpr)]
    return np.trapezoid(tp,fp)/f, np.interp(f,fpr,tpr)
mon=json.load(open("monitor-summary.json"))
aur=sorted([m.get("test_auroc") for m in (mon if isinstance(mon,list) else mon.get("monitors",mon.values())) if isinstance(m,dict) and m.get("test_auroc") is not None])
for field in ["stripped","code"]:
    for name,vec in [("word1-2",TfidfVectorizer(token_pattern=r'[A-Za-z_]+|\d+|[^\sA-Za-z_\d]',ngram_range=(1,2),min_df=2,max_features=50000,sublinear_tf=True)),
                     ("char3-5",TfidfVectorizer(analyzer="char_wb",ngram_range=(3,5),min_df=3,max_features=60000))]:
        clf=LogisticRegression(max_iter=5000,C=5).fit(vec.fit_transform(tr[field]),tr.label)
        s=clf.predict_proba(vec.transform(test[field]))[:,1]; a=roc_auc_score(test.label,s); p,t=pauc_tpr(test.label,s)
        print(f"[{field:8s}] {name}: AUROC={a:.4f} pAUC@10%={p:.4f} TPR@10%FPR={t:.4f}; monitors below it: {sum(x<a for x in aur)}/{len(aur)}")
