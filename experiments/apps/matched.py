import pyarrow.parquet as pq, glob, numpy as np, pandas as pd, re
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import roc_auc_score
cols=["problem_id","difficulty","solutions","backdoors","solution_passes_tests"]
df=pd.concat([pq.read_table(f,columns=cols).to_pandas() for f in sorted(glob.glob("train_*.parquet"))],ignore_index=True)
# Reproduce the DSPy tutorial protocol: problems with a control_tax backdoor; zip(solutions, backdoors[control_tax]) pairs
rows=[]
for _,r in df.iterrows():
    bds=[b for b in r.backdoors if b["source"]=="control_tax"]
    if not bds: continue
    for sol,bd in zip(r.solutions,bds):
        rows.append(dict(pid=r.problem_id,diff=r.difficulty,honest=sol["code"],hon_pass=sol["passes_tests"],attack=bd["backdoor_code"],
                         bd_works=bd["backdoor_works"],bd_pass=bd["passes_tests"],bd_compiles=bd["compiles"],model=bd["model"]))
p=pd.DataFrame(rows); print("pairs (tutorial protocol, control_tax):",len(p),"problems",p.pid.nunique())
print("attack code: backdoor_works",p.bd_works.mean().round(3),"passes_tests",p.bd_pass.mean().round(3),"compiles",p.bd_compiles.mean().round(3))
print("honest code passes_tests in these pairs",p.hon_pass.mean().round(3))
print("by model:\n",p.groupby("model").bd_works.agg(["mean","size"]).round(3))
# same but apps source
rows2=[]
for _,r in df.iterrows():
    bds=[b for b in r.backdoors if b["source"]=="apps"]
    for sol,bd in zip(r.solutions,bds): rows2.append(dict(pid=r.problem_id,bd_works=bd["backdoor_works"],bd_pass=bd["passes_tests"]))
p2=pd.DataFrame(rows2); print("\napps-source pairs",len(p2),"backdoor_works",p2.bd_works.mean().round(3),"passes",p2.bd_pass.mean().round(3))

# ---- trivial text baselines under the MATCHED protocol, problem-disjoint split ----
rng=np.random.RandomState(0); pids=np.array(list(p.pid.unique()),dtype=object); rng.shuffle(pids); te_p=set(pids[:int(0.3*len(pids))])
te=p[p.pid.isin(te_p)]; tr=p[~p.pid.isin(te_p)]
def feats(code):
    return [len(code), code.count("\n"), len(re.findall(r'\bif\b',code)), len(re.findall(r'\d{3,}',code)), code.count("=="), code.count("%"), len(re.findall(r'#',code))]
def longform(d):
    X=np.array([feats(c) for c in list(d.honest)+list(d.attack)],float); y=np.r_[np.zeros(len(d)),np.ones(len(d))]; return X,y
Xtr,ytr=longform(tr); Xte,yte=longform(te)
print("\n--- MATCHED protocol, trivial baselines (problem-disjoint 30pct test; n_test pairs=%d) ---"%len(te))
print("attack longer than honest (within pair):", (te.attack.str.len()>te.honest.str.len()).mean().round(3))
print("length only AUROC:", round(roc_auc_score(yte, Xte[:,0]),4))
clf=LogisticRegression(max_iter=3000).fit(np.log1p(Xtr),ytr); print("7 surface features AUROC:", round(roc_auc_score(yte, clf.predict_proba(np.log1p(Xte))[:,1]),4))
vec=TfidfVectorizer(token_pattern=r'[A-Za-z_]+|\d+|[^\sA-Za-z_\d]',ngram_range=(1,2),min_df=3,max_features=50000,sublinear_tf=True)
Ttr=vec.fit_transform(list(tr.honest)+list(tr.attack)); Tte=vec.transform(list(te.honest)+list(te.attack))
clf2=LogisticRegression(max_iter=3000,C=1.0).fit(Ttr,ytr); print("TF-IDF (1-2gram) LR AUROC:", round(roc_auc_score(yte, clf2.predict_proba(Tte)[:,1]),4))
# pairwise accuracy: does the classifier rank attack above honest within the pair?
sa=clf2.predict_proba(vec.transform(list(te.attack)))[:,1]; sh=clf2.predict_proba(vec.transform(list(te.honest)))[:,1]
print("TF-IDF pairwise accuracy (attack scored > honest within pair):", (sa>sh).mean().round(4))
# restrict to working backdoors only
m=te.bd_works.values
print("TF-IDF pairwise acc, backdoor_works only: %.4f (n=%d); non-working: %.4f (n=%d)"%((sa[m]>sh[m]).mean(),m.sum(),(sa[~m]>sh[~m]).mean(),(~m).sum()))
# diff-only baseline: the attack minus honest token diff (a 'diff' monitor)
