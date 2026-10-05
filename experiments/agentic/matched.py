"""Structural-feature AUROCs on the five ControlArena agentic settings, pooled and within task.

For each setting: a gradient-boosted model on six transcript counts (characters, lines, words,
assistant/tool/tool-call turns) under 5-fold CV with ungrouped folds, the same under folds
grouped by main task, and a within-task Mann-Whitney AUROC on character count alone, pooled
over tasks weighted by pair count. The within-task chars-only column (bash 0.504 to agentdojo
0.802) is the appendix figure on the agentic corpora. AUROCs are reported direction-free,
max(a, 1 - a).

Usage:
    python matched.py    # needs ca_<setting>.parquet from fetch_scan.py
"""
import pandas as pd, numpy as np
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.ensemble import GradientBoostingClassifier
def cvg(X,y,g,seed=0):
    X=np.asarray(X,float); oof=np.zeros(len(y))
    for tr,te in GroupKFold(5).split(X,y,g):
        oof[te]=GradientBoostingClassifier(random_state=seed).fit(X[tr],y[tr]).predict_proba(X[te])[:,1]
    return roc_auc_score(y,oof)
print(f"{'setting':11s} {'pooled':>8} {'task-grouped CV':>16} {'within-task AUROC':>18} {'#tasks used':>12}")
for s in ["bash","shade","iac","rogue_eval","agentdojo"]:
    df=pd.read_parquet(f"ca_{s}.parquet",columns=["transcript","ground_truth","extra_info"])
    ei=pd.json_normalize(df["extra_info"]); y=df["ground_truth"].astype(int).values
    t=df["transcript"].fillna("").astype(str)
    F=pd.DataFrame({"chars":t.str.len(),"lines":t.str.count("\n"),"words":t.str.count(r"\S+"),
                    "na":t.str.count(r"\[ASSISTANT\]"),"nt":t.str.count(r"\[TOOL\]"),"ntc":t.str.count(r"\[TOOL CALLS\]")})
    task=ei["main_task_description"].fillna("").values
    pooled=cvg(F.values,y,np.arange(len(y))%5)  # ungrouped folds (row index mod 5)
    grouped=cvg(F.values,y,task)
    # within-task: Mann-Whitney AUROC on chars, computed per task, weighted by pair count
    num=0.0; den=0.0; used=0
    d=pd.DataFrame({"task":task,"y":y,"x":F["chars"].values})
    for tk,g in d.groupby("task"):
        a=g[g.y==1]["x"].values; b=g[g.y==0]["x"].values
        if len(a)==0 or len(b)==0: continue
        w=(a[:,None]>b[None,:]).sum()+0.5*(a[:,None]==b[None,:]).sum()
        num+=w; den+=len(a)*len(b); used+=1
    wt = num/den if den else float('nan')
    print(f"{s:11s} {pooled:8.4f} {grouped:16.4f} {max(wt,1-wt):18.4f} {used:12d}")
