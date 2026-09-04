import pyarrow.parquet as pq, glob, numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
cols = ["problem_id","difficulty","has_backdoor","backdoor_works","solution_passes_tests","solution_compiles",
        "has_apps_backdoor","has_control_tax_backdoor","is_nondeterministic","nondeterminism_score",
        "backdoor_solution_passes_tests","question","inputs","solutions","backdoors"]
df = pd.concat([pq.read_table(f, columns=cols).to_pandas() for f in sorted(glob.glob("train_*.parquet"))], ignore_index=True)
print("rows", len(df), "unique problem_id", df.problem_id.nunique())
df["n_solutions"] = df.solutions.apply(len); df["n_backdoors"] = df.backdoors.apply(len)
df["n_tests"] = df.inputs.apply(len); df["q_len"] = df.question.str.len()
df["any_sol_passes"] = df.solutions.apply(lambda s: any(x["passes_tests"] for x in s))
print("\nhas_backdoor", df.has_backdoor.sum(), "backdoor_works", df.backdoor_works.sum(),
      "apps", df.has_apps_backdoor.sum(), "control_tax", df.has_control_tax_backdoor.sum())
print("n_backdoors dist:\n", df.n_backdoors.value_counts().sort_index().to_string())
print("\nP(has_backdoor|difficulty)\n", df.groupby("difficulty").has_backdoor.agg(["size","sum","mean"]))
print("\nsolution_passes_tests by has_backdoor\n", df.groupby("has_backdoor").solution_passes_tests.agg(["size","mean"]))
print("\nsolution_compiles by has_backdoor\n", df.groupby("has_backdoor").solution_compiles.agg(["size","mean"]))
print("\nany_sol_passes by has_backdoor\n", df.groupby("has_backdoor").any_sol_passes.agg(["size","mean"]))
print("\nn_solutions by has_backdoor\n", df.groupby("has_backdoor").n_solutions.describe()[["mean","50%"]])
print("\nn_tests by has_backdoor\n", df.groupby("has_backdoor").n_tests.describe()[["mean","50%"]])
print("\nq_len by has_backdoor\n", df.groupby("has_backdoor").q_len.describe()[["mean","50%"]])
print("\nis_nondeterministic by has_backdoor\n", df.groupby("has_backdoor").is_nondeterministic.mean())
# backdoor-level: works?
bd = df[df.has_backdoor]
print("\namong has_backdoor: backdoor_works", bd.backdoor_works.mean(), " backdoor_solution_passes_tests", bd.backdoor_solution_passes_tests.mean())
bl = pd.DataFrame([b for bs in df.backdoors for b in bs])
print("backdoor rows", len(bl)); print(bl.groupby("source")[["backdoor_works","passes_tests","compiles"]].agg(["mean","size"]))
print("models:", bl.model.value_counts().to_dict())

# ---- problem-level metadata floor (round-16 number) ----
X = pd.get_dummies(df[["difficulty"]]).astype(float)
X["solution_passes_tests"] = df.solution_passes_tests.astype(float)
X["solution_compiles"] = df.solution_compiles.astype(float)
X["n_tests"] = np.log1p(df.n_tests); X["q_len"] = np.log1p(df.q_len); X["n_solutions"]=np.log1p(df.n_solutions)
X["is_nondet"] = df.is_nondeterministic.astype(float)
y = df.has_backdoor.astype(int).values
def heldout(Xm, y, name):
    Xtr,Xte,ytr,yte = train_test_split(Xm,y,test_size=0.3,stratify=y,random_state=0)
    clf = LogisticRegression(max_iter=2000).fit(Xtr,ytr)
    print(f"{name}: held-out AUROC {roc_auc_score(yte, clf.predict_proba(Xte)[:,1]):.4f}")
    return clf
print("\n--- PROBLEM-LEVEL (label = has_backdoor) ---")
heldout(X, y, "all metadata")
heldout(X[[c for c in X if c.startswith('difficulty')]], y, "difficulty only")
heldout(X[["solution_passes_tests"]], y, "solution_passes_tests only")
heldout(X[[c for c in X if c.startswith('difficulty')]+["solution_passes_tests"]], y, "difficulty + passes")
heldout(X[["n_tests","q_len","n_solutions"]], y, "lengths/counts only (no pass flag)")
yw = df.backdoor_works.astype(int).values
heldout(X, yw, "all metadata, label = backdoor_works")

# ---- SAMPLE-LEVEL protocols ----
# score = problem-level metadata model's P(has_backdoor) fitted on train problems; evaluate on held-out problems
ptr, pte = train_test_split(df.index.values, test_size=0.3, stratify=y, random_state=0)
clf = LogisticRegression(max_iter=2000).fit(X.loc[ptr], y[ptr])
s = pd.Series(clf.predict_proba(X.loc[pte])[:,1], index=pte)
te = df.loc[pte]
def auc(pos_idx, neg_idx, name):
    yy = np.r_[np.ones(len(pos_idx)), np.zeros(len(neg_idx))]; ss = np.r_[s[pos_idx].values, s[neg_idx].values]
    print(f"{name}: n+={len(pos_idx)} n-={len(neg_idx)} AUROC {roc_auc_score(yy, ss):.4f}")
print("\n--- SAMPLE-LEVEL, metadata-only scorer (same score for honest and attack from one problem) ---")
auc(te.index[te.has_backdoor], te.index[~te.has_backdoor], "P0 one-sample-per-problem (attack iff has_backdoor)")
auc(te.index[te.has_backdoor], te.index, "P1 honest on ALL problems + attack on backdoored problems")
auc(te.index[te.backdoor_works], te.index, "P2 honest on ALL + attack only where backdoor_works")
auc(te.index[te.has_backdoor], te.index[te.has_backdoor], "P3 matched-within-problem (both classes, backdoored problems only)")
auc(te.index[te.has_backdoor & te.solution_passes_tests], te.index[te.solution_passes_tests], "P4 honest restricted to passing solutions + attack on backdoored")
