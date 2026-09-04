import fsspec, pyarrow.parquet as pq, pandas as pd, numpy as np, re
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, GroupKFold
from sklearn.ensemble import GradientBoostingClassifier
fs=fsspec.filesystem("https")
u="https://huggingface.co/datasets/AISafety-Student/labeled-bashBench/resolve/main/data/train-00000-of-00001.parquet"
df=pq.ParquetFile(fs.open(u)).read().to_pandas()
print("n",len(df),"label dist",df["label"].value_counts().to_dict())
print("split",df["split"].value_counts().to_dict())
print("action_type x label\n",pd.crosstab(df["action_type"].fillna("NA"),df["label"]).head(20))
print("danger_level x label\n",pd.crosstab(df["danger_level"],df["label"]))
print("side_task empty by label:", df.groupby("label")["side_task"].apply(lambda s: (s.fillna("").str.len()==0).mean()).to_dict())
y=df["label"].astype(int).values
tl=df["trajectory"].map(lambda t: len(t) if t is not None else 0)
fi=df["formatted_input"].fillna("").astype(str)
F=pd.DataFrame({"n_steps":tl,"step_index":df["step_index"],"tool_call_index":df["tool_call_index"],
                "progress":df["main_task_progress_pct"],"is_exec":df["is_executed"].astype(int),
                "fi_chars":fi.str.len(),"fi_lines":fi.str.count("\n"),
                "traj_chars":df["trajectory"].map(lambda t: sum(len(s.get("assistant_visible_text") or "") for s in (t or [])))})
for c in F.columns:
    a=roc_auc_score(y,F[c]); print(f"  {c:14s} {max(a,1-a):.4f}")
def cvg(X,y,g,seed=0):
    X=np.asarray(X,float); oof=np.zeros(len(y))
    for tr,te in GroupKFold(5).split(X,y,g):
        oof[te]=GradientBoostingClassifier(random_state=seed).fit(X[tr],y[tr]).predict_proba(X[te])[:,1]
    return roc_auc_score(y,oof)
g=df["task_id"].values
print(f"STRUCTURAL-ONLY (task-grouped 5f-CV) AUROC = {cvg(F.values,y,g):.4f}")
rng=np.random.default_rng(0); print(f"perm-null = {cvg(F.values,rng.permutation(y),g,seed=1):.4f}")
