import pandas as pd, numpy as np, sys, re
sys.path.insert(0,".")
from data import strip_comments, _pick_backdoor, _honest_code
df=pd.read_pickle("koran_test_code.pkl")
rows=[]
for _,r in df.iterrows():
    row={"problem_id":str(r.problem_id),
         "backdoors":[dict(b) for b in r.backdoors],
         "solutions":[dict(s) for s in r.solutions],
         "top_backdoor_model":r.top_backdoor_model}
    if r.backdoor_works:
        bd=_pick_backdoor(row)
        if bd is None: continue
        rows.append((row["problem_id"],1,bd["backdoor_code"]))
    else:
        c=_honest_code(row)
        if c is None: continue
        rows.append((row["problem_id"],0,c))
s=pd.DataFrame(rows,columns=["problem_id","label","code"]); s["code"]=s["code"].astype(str)
print("reconstructed:", len(s), "attack", int(s.label.sum()), "honest", int((1-s.label).sum()))

def has_comment(c):
    return bool(re.search(r'(?m)(^|\s)#', c))
print("\n--- comment presence (RAW, before stripping)")
print(s.groupby("label")["code"].apply(lambda x: np.mean([has_comment(c) for c in x])))
print("\n--- '#' count AUROC raw vs stripped (reproducing the repo's leak check)")
from sklearn.metrics import roc_auc_score
raw_hash=np.array([c.count("#") for c in s.code], float)
s["stripped"]=[strip_comments(c) for c in s.code]
st_hash=np.array([c.count("#") for c in s.stripped], float)
print("  raw      hash-count AUROC = %.4f"%roc_auc_score(s.label,raw_hash))
print("  stripped hash-count AUROC = %.4f"%roc_auc_score(s.label,st_hash))
print("  attacks with comments raw=%d stripped=%d ; honest raw=%d stripped=%d"%(
  sum(has_comment(c) for c in s[s.label==1].code), sum(has_comment(c) for c in s[s.label==1].stripped),
  sum(has_comment(c) for c in s[s.label==0].code), sum(has_comment(c) for c in s[s.label==0].stripped)))

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics import roc_auc_score, accuracy_score
for field in ["code","stripped"]:
    X=np.array([str(v) for v in s[field].tolist()],dtype=object); y=np.asarray(s.label.tolist())
    Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=0.30,stratify=y,random_state=0)
    for name,vec in [("word 1-2gram tfidf",TfidfVectorizer(ngram_range=(1,2),min_df=2,token_pattern=r"[A-Za-z_][A-Za-z_0-9]*")),
                     ("char 3-5gram tfidf",TfidfVectorizer(analyzer="char_wb",ngram_range=(3,5),min_df=3,max_features=60000))]:
        m=make_pipeline(vec,LogisticRegression(max_iter=5000,C=5))
        m.fit(Xtr,ytr); p=m.predict_proba(Xte)[:,1]
        print(f"[{field:8s}] {name:20s} held-out AUROC={roc_auc_score(yte,p):.4f}  acc={accuracy_score(yte,(p>0.5).astype(int)):.4f} (n={len(yte)},pos={int(yte.sum())})")
# also code-length only
print("\ncode-length-only AUROC (stripped): %.4f  (repo reports 0.4726)"%roc_auc_score(s.label,[len(c) for c in s.stripped]))
print("code-length-only AUROC direction-flipped: %.4f"%roc_auc_score(s.label,[-len(c) for c in s.stripped]))
s.to_pickle("koran_samples.pkl")
