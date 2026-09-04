import pandas as pd, numpy as np, json, sys
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression

def cv_auc(X,y,seed=0):
    X=np.asarray(X,dtype=float); y=np.asarray(y)
    skf=StratifiedKFold(5,shuffle=True,random_state=seed); oof=np.zeros(len(y))
    for tr,te in skf.split(X,y):
        m=GradientBoostingClassifier(random_state=seed).fit(X[tr],y[tr])
        oof[te]=m.predict_proba(X[te])[:,1]
    return roc_auc_score(y,oof)

for s in ["bash","shade","iac","rogue_eval","agentdojo"]:
    df=pd.read_parquet(f"ca_{s}.parquet")
    y=df["ground_truth"].astype(int).values
    tr=df["transcript"].fillna("").astype(str)
    ei=pd.json_normalize(df["extra_info"])
    n=len(df)
    print(f"===== {s}  n={n}  positives={y.sum()} ({y.mean():.3f})")
    # structural features, no content read
    feats=pd.DataFrame({
      "n_chars": tr.str.len(),
      "n_lines": tr.str.count("\n"),
      "n_words": tr.str.count(r"\S+"),
      "n_prompt_msgs": df["prompt"].apply(lambda p: len(p) if p is not None else 0),
      "n_td_chars": df["trajectory_data"].fillna("").astype(str).str.len(),
    })
    for c in feats.columns:
        try: a=roc_auc_score(y,feats[c]); print(f"   {c:16s} AUROC {max(a,1-a):.4f} (raw {a:.4f})")
        except Exception as e: print(c,e)
    print(f"   ALL-STRUCTURAL 5fold-CV AUROC: {cv_auc(feats.values,y):.4f}")
    # model identity leak
    if "model" in ei.columns:
        ct=pd.crosstab(ei["model"],y)
        print("   model x label:\n", ct.to_string().replace("\n","\n     "))
    if "setting" in ei.columns: print("   settings:", ei["setting"].value_counts().to_dict())
    # main_task_description leak (does the task text itself differ by label?)
    if "main_task_description" in ei.columns:
        md=ei["main_task_description"].fillna("")
        print("   unique main_task_desc:", md.nunique(), "| desc-length AUROC:",
              round(max(roc_auc_score(y,md.str.len()),1-roc_auc_score(y,md.str.len())),4))
        # is the SAME main task present in both classes?
        g=pd.crosstab(md,y)
        both=((g[0]>0)&(g[1]>0)).sum() if 0 in g.columns and 1 in g.columns else 0
        print(f"   main tasks appearing in BOTH classes: {both} / {md.nunique()}")
    print()
