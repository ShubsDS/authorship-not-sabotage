import pandas as pd, numpy as np, re
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.ensemble import GradientBoostingClassifier

def cv_auc(X,y,seed=0):
    X=np.asarray(X,float); y=np.asarray(y); skf=StratifiedKFold(5,shuffle=True,random_state=seed)
    oof=np.zeros(len(y))
    for tr,te in skf.split(X,y):
        oof[te]=GradientBoostingClassifier(random_state=seed).fit(X[tr],y[tr]).predict_proba(X[te])[:,1]
    return roc_auc_score(y,oof)

rows=[]
for s in ["bash","shade","iac","rogue_eval","agentdojo"]:
    df=pd.read_parquet(f"ca_{s}.parquet", columns=["transcript","ground_truth","extra_info","id"])
    y=df["ground_truth"].astype(int).values
    t=df["transcript"].fillna("").astype(str)
    F=pd.DataFrame({
      "chars":      t.str.len(),
      "lines":      t.str.count("\n"),
      "words":      t.str.count(r"\S+"),
      "n_assistant":t.str.count(r"\[ASSISTANT\]"),
      "n_tool":     t.str.count(r"\[TOOL\]"),
      "n_toolcalls":t.str.count(r"\[TOOL CALLS\]"),
    })
    singles={c: round(max(roc_auc_score(y,F[c]),1-roc_auc_score(y,F[c])),4) for c in F}
    cv=round(cv_auc(F.values,y),4)
    # null: label permutation
    rng=np.random.default_rng(0); nulls=[cv_auc(F.values,rng.permutation(y),seed=1) for _ in range(3)]
    print(f"{s:11s} n={len(df)} pos={y.mean():.2f} | " + " ".join(f"{k}={v}" for k,v in singles.items()))
    print(f"{'':11s} STRUCTURAL-ONLY (transcript, 5f-CV, GBM) AUROC = {cv}   perm-null mean={np.mean(nulls):.4f}")
    rows.append((s,len(df),cv,np.mean(nulls),singles))
print()
print("| setting | n | structural-only AUROC | perm null |")
for s,n,cv,nl,_ in rows: print(f"| {s} | {n} | {cv:.4f} | {nl:.4f} |")
