import fsspec, pyarrow.parquet as pq, pandas as pd, numpy as np
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.ensemble import GradientBoostingClassifier
fs=fsspec.filesystem("https")
def read(urls, cols):
    o=[]
    for u in urls:
        pf=pq.ParquetFile(fs.open(u)); o.append(pf.read(columns=[c for c in cols if c in pf.schema_arrow.names]).to_pandas())
    return pd.concat(o,ignore_index=True)
def cv(X,y,seed=0):
    X=np.asarray(X,float);y=np.asarray(y);oof=np.zeros(len(y))
    for tr,te in StratifiedKFold(5,shuffle=True,random_state=seed).split(X,y):
        oof[te]=GradientBoostingClassifier(random_state=seed).fit(X[tr],y[tr]).predict_proba(X[te])[:,1]
    return roc_auc_score(y,oof)
C=["difficulty","solution_compiles","solution_passes_tests","is_nondeterministic","nondeterminism_score","num_tests","has_backdoor","backdoor_works","top_backdoor_model","backdoor_solution_passes_tests","problem_id"]
B="https://huggingface.co/datasets/"
df=read([f"{B}eugenekoran/apps-control-arena-high-quality/resolve/main/data/test-0000{i}-of-00002.parquet" for i in range(2)],C)
print("n=",len(df))
y=df["backdoor_works"].fillna(False).astype(int).values
print("LABEL backdoor_works:",y.sum(),"attack /",len(y)-y.sum(),"honest   <-- 2608.16190 says 172/1203")
F=pd.get_dummies(df[["solution_compiles","solution_passes_tests","is_nondeterministic","nondeterminism_score","num_tests","difficulty"]],columns=["difficulty"]).astype(float)
print("features:",list(F.columns))
print(f"METADATA-ONLY 5f-CV AUROC (y=backdoor_works) = {cv(F.values,y):.4f}")
rng=np.random.default_rng(0); print(f"perm-null = {cv(F.values,rng.permutation(y),seed=1):.4f}")
for c in F.columns:
    a=roc_auc_score(y,F[c]); print(f"   {c:28s} {max(a,1-a):.4f}")
print("\nP(attack | difficulty):"); print(df.assign(y=y).groupby("difficulty")["y"].agg(["size","sum","mean"]).round(4))
print("\nnum_tests by label:"); print(df.assign(y=y).groupby("y")["num_tests"].describe().round(2))
if "top_backdoor_model" in df: print("\ntop_backdoor_model x label:\n", pd.crosstab(df["top_backdoor_model"].fillna("NONE"), y))
# pAUC@1%FPR
from sklearn.metrics import roc_curve
fpr,tpr,_=roc_curve(y, GradientBoostingClassifier(random_state=0).fit(F.values,y).predict_proba(F.values)[:,1])
print("\n(in-sample sanity only) ")
