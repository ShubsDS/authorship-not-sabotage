import fsspec, pyarrow.parquet as pq, pandas as pd, numpy as np, itertools
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.ensemble import GradientBoostingClassifier
fs=fsspec.filesystem("https")
def read(urls, cols):
    out=[]
    for u in urls:
        pf=pq.ParquetFile(fs.open(u))
        have=[c for c in cols if c in pf.schema_arrow.names]
        out.append(pf.read(columns=have).to_pandas())
    return pd.concat(out,ignore_index=True)
def cv(X,y,seed=0):
    X=np.asarray(X,float);y=np.asarray(y);skf=StratifiedKFold(5,shuffle=True,random_state=seed);oof=np.zeros(len(y))
    for tr,te in skf.split(X,y):
        oof[te]=GradientBoostingClassifier(random_state=seed).fit(X[tr],y[tr]).predict_proba(X[te])[:,1]
    return roc_auc_score(y,oof)
META=["difficulty","solution_compiles","solution_passes_tests","is_nondeterministic","nondeterminism_score","num_tests","has_backdoor","backdoor_works","has_apps_backdoor","has_control_tax_backdoor"]
B="https://huggingface.co/datasets/"
sets={
 "apps-control-arena(5000)": [f"{B}RoganInglis/apps-control-arena/resolve/main/data/train-0000{i}-of-00003.parquet" for i in range(3)],
 "koran-HQ-test(1375)": [f"{B}eugenekoran/apps-control-arena-high-quality/resolve/main/data/test-0000{i}-of-00002.parquet" for i in range(2)],
 "koran-HQ-train(1209)": [f"{B}eugenekoran/apps-control-arena-high-quality/resolve/main/data/train-00000-of-00001.parquet"],
}
for name,urls in sets.items():
    df=read(urls,META)
    y=df["has_backdoor"].astype(int).values
    print(f"##### {name}  n={len(df)}  P(backdoor)={y.mean():.4f}")
    F=pd.get_dummies(df[[c for c in ["difficulty","solution_compiles","solution_passes_tests","is_nondeterministic","nondeterminism_score","num_tests"] if c in df]],columns=[c for c in ["difficulty"] if c in df])
    print("   features:",list(F.columns))
    print(f"   METADATA-ONLY 5f-CV AUROC = {cv(F.values,y):.4f}")
    if "solution_passes_tests" in df:
        spt=df["solution_passes_tests"].astype(int)
        print(f"   solution_passes_tests: mean|bd=1 {spt[y==1].mean():.4f}  mean|bd=0 {spt[y==0].mean():.4f}  alone AUROC {max(roc_auc_score(y,spt),1-roc_auc_score(y,spt)):.4f}")
    if "difficulty" in df: print("   P(bd|difficulty):", df.groupby("difficulty")["has_backdoor"].agg(["size","sum","mean"]).round(4).to_dict("index"))
    if "backdoor_works" in df:
        bw=df["backdoor_works"].fillna(False).astype(int)
        print(f"   backdoor_works={bw.sum()} of has_backdoor={y.sum()}  -> inert fraction {1-bw.sum()/max(y.sum(),1):.3f}")
    rng=np.random.default_rng(0); print(f"   perm-null AUROC = {cv(F.values,rng.permutation(y),seed=1):.4f}")
    print()
