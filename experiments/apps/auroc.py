import pandas as pd, numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score

def run(df, y, featsets, tag):
    print("="*70); print(tag, " n=%d  positives=%d (%.4f)"%(len(df), y.sum(), y.mean()))
    for name, cols in featsets.items():
        cols=[c for c in cols if c in df.columns]
        cat=[c for c in cols if not pd.api.types.is_numeric_dtype(df[c]) and not pd.api.types.is_bool_dtype(df[c])]
        X = pd.get_dummies(df[cols].astype({c:"object" for c in cat}), columns=cat, dummy_na=False)
        X = X.astype(float)
        keep=[c for c in X.columns if X[c].nunique()>1]
        if not keep:
            print(f"  {name:46s} all features constant -> AUROC undefined"); continue
        X=X[keep]
        Xtr,Xte,ytr,yte = train_test_split(X,y,test_size=0.30,stratify=y,random_state=0)
        m = make_pipeline(StandardScaler(), LogisticRegression(max_iter=5000))
        m.fit(Xtr,ytr)
        p = m.predict_proba(Xte)[:,1]
        print(f"  {name:46s} AUROC={roc_auc_score(yte,p):.4f}   (test n={len(yte)}, pos={int(yte.sum())}, feats={len(keep)})")

k = pd.read_parquet("koran_meta.parquet"); kt = k[k.split=="test"].copy()
y = kt.backdoor_works.astype(int).values
FS = {
 "difficulty only":                              ["difficulty"],
 "num_tests only":                               ["num_tests"],
 "q_len only":                                   ["q_len"],
 "PROBLEM-SIDE: difficulty+num_tests+q_len":     ["difficulty","num_tests","q_len"],
 "  + nondeterminism_score":                     ["difficulty","num_tests","q_len","nondeterminism_score"],
 "PIPELINE-SIDE: + has_apps/has_control_tax":    ["difficulty","num_tests","q_len","nondeterminism_score","has_apps_backdoor","has_control_tax_backdoor"],
 "FULL incl. backdoor validation flags":         ["difficulty","num_tests","q_len","nondeterminism_score","has_apps_backdoor","has_control_tax_backdoor","backdoor_solution_compiles","backdoor_solution_passes_tests"],
}
run(kt, y, FS, "KORAN TEST SPLIT (eugenekoran/apps-control-arena-high-quality, split=test)")

# single-column AUROCs, no model
print("\nsingle-column raw AUROC on the whole 1375 (no split, direction as-is):")
for c in ["num_tests","q_len","nondeterminism_score","has_control_tax_backdoor","has_apps_backdoor","backdoor_solution_passes_tests","backdoor_solution_compiles"]:
    v=kt[c].astype(float); print(f"  {c:34s} {roc_auc_score(y,v):.4f}")

# Rogan positive control
r = pd.read_parquet("rogan_meta.parquet")
yr = r.has_backdoor.astype(int).values
FSR = {
 "difficulty only":                              ["difficulty"],
 "solution_passes_tests only":                   ["solution_passes_tests"],
 "METADATA-ONLY (difficulty+solution flags+q_len+nondet)": ["difficulty","solution_compiles","solution_passes_tests","q_len","is_nondeterministic","nondeterminism_score"],
}
run(r, yr, FSR, "RoganInglis/apps-control-arena  label=has_backdoor  [pipeline positive control]")
print("\nrogan solution_passes_tests by has_backdoor:")
print(r.groupby("has_backdoor")["solution_passes_tests"].agg(["size","mean"]))
print("\nrogan P(has_backdoor|difficulty):"); print(r.groupby("difficulty")["has_backdoor"].agg(["size","sum","mean"]))
