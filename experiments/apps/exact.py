import pyarrow.parquet as pq, glob, numpy as np, pandas as pd, re
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import roc_auc_score
cols=["problem_id","solutions","backdoors"]
df=pd.concat([pq.read_table(f,columns=cols).to_pandas() for f in sorted(glob.glob("train_*.parquet"))],ignore_index=True)
# exact tutorial zip: zip(solutions, backdoors) with strict=False over control_tax backdoors -> min(len) pairs per problem
rows=[]
for _,r in df.iterrows():
    bds=[b for b in r.backdoors if b["source"]=="control_tax"]
    if not bds: continue
    for sol,bd in zip(list(r.solutions),bds): rows.append(dict(pid=r.problem_id,honest=sol["code"],attack=bd["backdoor_code"],bd_works=bd["backdoor_works"]))
p=pd.DataFrame(rows); print("exact tutorial pairs:",len(p),"(tutorial printed 6369)")
rng=np.random.RandomState(0); pids=np.array(list(p.pid.unique()),dtype=object); rng.shuffle(pids)
accs=[];lens=[]
vec=TfidfVectorizer(token_pattern=r'[A-Za-z_]+|\d+|[^\sA-Za-z_\d]',ngram_range=(1,2),min_df=3,max_features=50000,sublinear_tf=True)
for fold in range(5):
    te_p=set(pids[fold::5]); te=p[p.pid.isin(te_p)]; tr=p[~p.pid.isin(te_p)]
    X=vec.fit_transform(list(tr.honest)+list(tr.attack)); y=np.r_[np.zeros(len(tr)),np.ones(len(tr))]
    clf=LogisticRegression(max_iter=3000).fit(X,y)
    sa=clf.predict_proba(vec.transform(list(te.attack)))[:,1]; sh=clf.predict_proba(vec.transform(list(te.honest)))[:,1]
    accs.append((sa>sh).mean()); lens.append((te.attack.str.len()>te.honest.str.len()).mean())
print("5-fold problem-disjoint TF-IDF pairwise acc: mean %.4f  folds %s"%(np.mean(accs),np.round(accs,4)))
print("5-fold 'longer is attack': mean %.4f  folds %s"%(np.mean(lens),np.round(lens,4)))
# tiny-train regime like the tutorial: 200 train pairs, test on the rest (problem-disjoint), 5 seeds
res=[]
for seed in range(5):
    r=np.random.RandomState(seed); pp=pids.copy(); r.shuffle(pp)
    trp=set(pp[:200]); tr=p[p.pid.isin(trp)].groupby('pid').head(1); te=p[~p.pid.isin(trp)]
    X=vec.fit_transform(list(tr.honest)+list(tr.attack)); y=np.r_[np.zeros(len(tr)),np.ones(len(tr))]
    clf=LogisticRegression(max_iter=3000).fit(X,y)
    sa=clf.predict_proba(vec.transform(list(te.attack)))[:,1]; sh=clf.predict_proba(vec.transform(list(te.honest)))[:,1]; res.append((sa>sh).mean())
print("TF-IDF trained on only 200 pairs (tutorial's train size), pairwise acc on held-out problems: mean %.4f %s"%(np.mean(res),np.round(res,4)))
