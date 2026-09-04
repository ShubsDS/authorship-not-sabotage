import pandas as pd, numpy as np
k = pd.read_parquet("koran_meta.parquet"); kt=k[k.split=="test"].copy()
kt["label"]=kt.backdoor_works.astype(int)
print("test: n=%d attack=%d honest=%d base_rate=%.4f"%(len(kt),kt.label.sum(),(1-kt.label).sum(),kt.label.mean()))
print("test rows carrying >=1 labelled backdoor (has_backdoor):", int(kt.has_backdoor.sum()))
print("  of which the backdoor WORKS (-> labelled attack):", int((kt.has_backdoor&kt.backdoor_works).sum()))
print("  of which NO backdoor works (-> relabelled HONEST):", int((kt.has_backdoor&~kt.backdoor_works).sum()))
print("fraction of labelled backdoors in test that do not work: %.4f"%(1-kt.backdoor_works.sum()/kt.has_backdoor.sum()))
print("honest test items that are backdoor-authored problems: %d / %d = %.4f"%(
   (kt.has_backdoor&~kt.backdoor_works).sum(), (1-kt.label).sum(),
   (kt.has_backdoor&~kt.backdoor_works).sum()/(1-kt.label).sum()))
print()
print("whole koran artifact: has_backdoor=%d backdoor_works=%d -> %.4f do not work"%(
   k.has_backdoor.sum(), k.backdoor_works.sum(), 1-k.backdoor_works.sum()/k.has_backdoor.sum()))
r=pd.read_parquet("rogan_meta.parquet")
print("rogan: has_backdoor=%d backdoor_works=%d -> %.4f do not work"%(
   r.has_backdoor.sum(), r.backdoor_works.sum(), 1-r.backdoor_works.sum()/r.has_backdoor.sum()))
print()
from sklearn.model_selection import RepeatedStratifiedKFold, cross_val_score, train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
X=pd.get_dummies(kt[["difficulty","num_tests","q_len"]].astype({"difficulty":"object"}),columns=["difficulty"]).astype(float)
y=kt.label.values
m=make_pipeline(StandardScaler(),LogisticRegression(max_iter=5000))
cv=RepeatedStratifiedKFold(n_splits=5,n_repeats=5,random_state=0)
s=cross_val_score(m,X,y,cv=cv,scoring="roc_auc")
print("PROBLEM-SIDE metadata, 5x5 repeated stratified CV AUROC on all 1375: mean=%.4f sd=%.4f"%(s.mean(),s.std()))
m.fit(X,y); from sklearn.metrics import roc_auc_score
print("in-sample AUROC on all 1375: %.4f"%roc_auc_score(y,m.predict_proba(X)[:,1]))
print("\nnum_tests direction-flipped single-column AUROC on all 1375: %.4f"%roc_auc_score(y,-kt.num_tests.astype(float)))
print("q_len direction-flipped single-column AUROC on all 1375: %.4f"%roc_auc_score(y,-kt.q_len.astype(float)))
