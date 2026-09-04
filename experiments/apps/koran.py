import pyarrow.parquet as pq, glob, numpy as np, pandas as pd, re, io, tokenize
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import roc_auc_score, roc_curve
cols=["problem_id","difficulty","solutions","backdoors"]
df=pd.concat([pq.read_table(f,columns=cols).to_pandas() for f in sorted(glob.glob("train_*.parquet"))],ignore_index=True)
def strip_comments(code):
    out=[]
    try:
        toks=list(tokenize.generate_tokens(io.StringIO(code).readline))
    except Exception:
        return re.sub(r'#.*','',code)
    prev_end=(1,0); res=[]; last_line=1; last_col=0
    for tok in toks:
        if tok.type==tokenize.COMMENT: continue
        ttype,tstr,(sl,sc),(el,ec),_=tok
        if sl>last_line: last_col=0
        if sc>last_col: res.append(" "*(sc-last_col))
        res.append(tstr); last_line,last_col=el,ec
    s="".join(res)
    # drop standalone string-expression docstrings (approx) and blank lines
    s=re.sub(r'^\s*("""|\'\'\')[\s\S]*?\1\s*$', '', s, flags=re.M)
    return "\n".join(l for l in s.split("\n") if l.strip())
# Koran filter: honest = solutions passing all tests; attack = backdoors that work (exploit + pass tests)
H=[];A=[]
for _,r in df.iterrows():
    hs=[s["code"] for s in r.solutions if s["passes_tests"]]
    bs=[b["backdoor_code"] for b in r.backdoors if b["backdoor_works"]]
    for c in hs: H.append(dict(pid=r.problem_id,code=c,y=0))
    for c in bs: A.append(dict(pid=r.problem_id,code=c,y=1))
d=pd.DataFrame(H+A); print("filtered pool: honest",len(H),"attack",len(A),"problems",d.pid.nunique())
d["code_s"]=d.code.map(strip_comments)
print("comments remaining ('#' in code):", d.code_s.str.contains('#').mean().round(4))
# one honest + one attack per problem max, to approximate Koran's per-problem sampling (they had 172 attack / 1203 honest in test)
d1=d.groupby(["pid","y"]).head(1)
print("dedup per problem/class: honest",(d1.y==0).sum(),"attack",(d1.y==1).sum())
def pauc(y,s,fpr_max=0.1):
    fpr,tpr,_=roc_curve(y,s); m=fpr<=fpr_max
    fp=np.r_[fpr[m],fpr_max]; tp=np.r_[tpr[m],np.interp(fpr_max,fpr,tpr)]
    raw=np.trapezoid(tp,fp); return raw/fpr_max, np.interp(fpr_max,fpr,tpr)   # normalized pAUC (area/0.1), and TPR@10%FPR
def run(dd,label):
    rng=np.random.RandomState(0); pids=np.array(list(dd.pid.unique()),dtype=object); rng.shuffle(pids)
    res=[]
    vec=TfidfVectorizer(token_pattern=r'[A-Za-z_]+|\d+|[^\sA-Za-z_\d]',ngram_range=(1,2),min_df=3,max_features=50000,sublinear_tf=True)
    for fold in range(5):
        te=dd[dd.pid.isin(set(pids[fold::5]))]; tr=dd[~dd.pid.isin(set(pids[fold::5]))]
        clf=LogisticRegression(max_iter=3000,class_weight="balanced").fit(vec.fit_transform(tr.code_s),tr.y)
        s=clf.predict_proba(vec.transform(te.code_s))[:,1]
        L=te.code_s.str.len().values
        res.append(dict(auroc=roc_auc_score(te.y,s),pauc=pauc(te.y,s)[0],tpr10=pauc(te.y,s)[1],len_auroc=roc_auc_score(te.y,L),len_tpr10=pauc(te.y,L)[1],n_att=int(te.y.sum()),n_hon=int((1-te.y).sum())))
    R=pd.DataFrame(res); print("\n==",label,"(5-fold problem-disjoint; comments stripped; Koran filter)\n",R.round(4).to_string()); print("mean:",R.mean().round(4).to_dict())
run(d1,"one-per-problem-per-class pooled")
run(d,"all filtered samples pooled")
# and the unfiltered raw version for contrast (comment-stripped, no works filter)
H2=[dict(pid=r.problem_id,code=s["code"],y=0) for _,r in df.iterrows() for s in list(r.solutions)[:1]]
A2=[dict(pid=r.problem_id,code=b["backdoor_code"],y=1) for _,r in df.iterrows() for b in list(r.backdoors)[:1]]
d2=pd.DataFrame(H2+A2); d2["code_s"]=d2.code.map(strip_comments); run(d2,"RAW (no works/pass filter), comments stripped, one per problem/class")
d2["code_s"]=d2.code; run(d2,"RAW, comments KEPT, one per problem/class")
