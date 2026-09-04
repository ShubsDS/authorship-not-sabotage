import pandas as pd, numpy as np
pd.set_option("display.width",200)

k = pd.read_parquet("koran_meta.parquet")
r = pd.read_parquet("rogan_meta.parquet")

print("="*70); print("A. LINEAGE: is the Koran artifact a subset of RoganInglis?")
kp=set(k.problem_id); rp=set(r.problem_id)
print("koran rows", len(k), "unique pid", len(kp))
print("rogan rows", len(r), "unique pid", len(rp))
print("koran pids inside rogan:", len(kp & rp), "/", len(kp))
print("koran pids NOT in rogan:", len(kp - rp))
# do shared columns agree row-for-row?
m = k.merge(r, on="problem_id", suffixes=("_k","_r"))
shared=[c for c in k.columns if c in r.columns and c not in ("problem_id","split")]
print("merged rows", len(m))
for c in shared:
    a,b = m[c+"_k"], m[c+"_r"]
    if a.dtype==float: eq=(np.isclose(a,b)|(a.isna()&b.isna())).mean()
    else: eq=(a.astype(str)==b.astype(str)).mean()
    print(f"  {c:38s} identical fraction = {eq:.4f}")

print("="*70); print("B. KORAN TEST SPLIT: label = backdoor_works  (per challenger-panels src/data.py)")
kt = k[k.split=="test"].copy()
kt["label"] = kt.backdoor_works.astype(int)
print("test rows", len(kt), " attack", int(kt.label.sum()), " honest", int((1-kt.label).sum()))
print("\ntop_backdoor_model among attack rows:")
print(kt[kt.label==1].top_backdoor_model.value_counts(dropna=False))
ktr = k[k.split=="train"].copy()
print("\ntrain rows", len(ktr), "backdoor_works", int(ktr.backdoor_works.sum()),
      "solution_passes_tests", int(ktr.solution_passes_tests.sum()))

print("="*70); print("C. METADATA MARGINALS ON THE KORAN TEST SPLIT")
for c in ["difficulty","nondeterminism_category","has_apps_backdoor","has_control_tax_backdoor",
          "solution_compiles","solution_passes_tests","backdoor_solution_compiles",
          "backdoor_solution_passes_tests","is_nondeterministic"]:
    g = kt.groupby(c)["label"].agg(["size","sum","mean"])
    print(f"\nP(attack | {c}):\n{g}")
for c in ["q_len","num_tests","nondeterminism_score"]:
    print(f"\n{c} by label:\n{kt.groupby('label')[c].describe()[['count','mean','50%','std']]}")

print("="*70); print("D. 'BACKDOOR DOES NOT WORK' ISSUE IN THE KORAN ARTIFACT")
for name,df in [("koran ALL",k),("koran test",kt),("koran train",ktr)]:
    print(f"{name:12s} has_backdoor={int(df.has_backdoor.sum()):5d}  "
          f"backdoor_solution_passes_tests={int(df.backdoor_solution_passes_tests.sum()):5d}  "
          f"backdoor_works={int(df.backdoor_works.sum()):5d}  n={len(df)}")
print("rogan ALL   has_backdoor=%d backdoor_works=%d n=%d"%(r.has_backdoor.sum(),r.backdoor_works.sum(),len(r)))
