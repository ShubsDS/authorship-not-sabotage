"""Re-run the matched-protocol and transfer numbers WITH the field's comment stripper.

Why this script exists (2026-09-11). `matched.py`, `exact.py` and `transfer.py` never call
`strip_comments`, so six reported numbers are measured on code with comments left in:

    TF-IDF AUROC 0.9425 · pairwise 0.9621 · working 0.9787 vs inert 0.9543
    surface-7 0.8302 · length 0.8255 within-pair · transfer 0.9935 (and the three cross-model rows)

Two of those - the inert-vs-working contrast and the cross-generator transfer - are two of the
three legs the paper's "authorship, not sabotage" reading stands on when the same-generator
control is absent. The field's own published check says a detector reading nothing but the
number of '#' characters scores 0.6957 before stripping and 0.4983 after (Jha, `--leak-check`).
So a reviewer can read those two legs as resting on the one channel the field already patched.
This script settles it: the identical protocol, stripped and unstripped, side by side.

Protocol is copied from `matched.py` / `transfer.py` line for line (same pair construction,
same RandomState(0) problem-disjoint 30% split, same vectorizer, same LR), with two additions:
`strip_comments` from `data.py` (Jha's own port of the anchor's stripper) applied to BOTH
classes, and an optional `--seeds N` to repeat the split so the pairwise numbers carry a spread.

    python strip_recheck.py              # both preprocessings, seed 0 - the like-for-like table
    python strip_recheck.py --seeds 5    # adds mean +/- sd over five problem-disjoint splits

Needs the three `train_*.parquet` shards from `fetch.py`. CPU, a few minutes.
NOT yet run on the real shards in the session that wrote it (HuggingFace was unreachable
from that sandbox); it was exercised end to end on a synthetic shard with the same schema.
"""
import argparse, glob, re
import numpy as np, pandas as pd, pyarrow.parquet as pq
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from data import strip_comments


def load_pairs(shard_glob="train_*.parquet"):
    cols = ["problem_id", "difficulty", "solutions", "backdoors", "solution_passes_tests"]
    df = pd.concat([pq.read_table(f, columns=cols).to_pandas()
                    for f in sorted(glob.glob(shard_glob))], ignore_index=True)
    rows = []
    for _, r in df.iterrows():
        for src in ["control_tax", "apps"]:
            bds = [b for b in r.backdoors if b["source"] == src]
            # zip(solutions, backdoors) is the DSPy tutorial's pairing, as in matched.py/transfer.py
            for sol, bd in zip(r.solutions, bds):
                rows.append(dict(pid=str(r.problem_id), src=src, honest=sol["code"],
                                 attack=bd["backdoor_code"], bd_works=bool(bd["backdoor_works"]),
                                 model=bd["model"]))
    return pd.DataFrame(rows)


def preprocess(p, strip):
    if not strip:
        return p
    q = p.copy()
    q["honest"] = [strip_comments(c) for c in q.honest]
    q["attack"] = [strip_comments(c) for c in q.attack]
    return q


def make_vec():
    return TfidfVectorizer(token_pattern=r'[A-Za-z_]+|\d+|[^\sA-Za-z_\d]', ngram_range=(1, 2),
                           min_df=3, max_features=50000, sublinear_tf=True)


def surface(code):
    return [len(code), code.count("\n"), len(re.findall(r'\bif\b', code)),
            len(re.findall(r'\d{3,}', code)), code.count("=="), code.count("%"),
            len(re.findall(r'#', code))]


def longform(d):
    X = np.array([surface(c) for c in list(d.honest) + list(d.attack)], float)
    y = np.r_[np.zeros(len(d)), np.ones(len(d))]
    return X, y


def matched_protocol(ct, seed):
    """matched.py's block, parameterised by seed. Returns a dict of the six numbers."""
    rng = np.random.RandomState(seed)
    pids = np.array(list(ct.pid.unique()), dtype=object); rng.shuffle(pids)
    te_p = set(pids[:int(0.3 * len(pids))])
    te, tr = ct[ct.pid.isin(te_p)], ct[~ct.pid.isin(te_p)]
    Xtr, ytr = longform(tr); Xte, yte = longform(te)
    out = {"n_test_pairs": len(te),
           "length_within_pair": float((te.attack.str.len() > te.honest.str.len()).mean()),
           "length_auroc": float(roc_auc_score(yte, Xte[:, 0]))}
    clf = LogisticRegression(max_iter=3000).fit(np.log1p(Xtr), ytr)
    out["surface7_auroc"] = float(roc_auc_score(yte, clf.predict_proba(np.log1p(Xte))[:, 1]))
    vec = make_vec()
    Ttr = vec.fit_transform(list(tr.honest) + list(tr.attack))
    Tte = vec.transform(list(te.honest) + list(te.attack))
    clf2 = LogisticRegression(max_iter=3000, C=1.0).fit(Ttr, ytr)
    out["tfidf_auroc"] = float(roc_auc_score(yte, clf2.predict_proba(Tte)[:, 1]))
    sa = clf2.predict_proba(vec.transform(list(te.attack)))[:, 1]
    sh = clf2.predict_proba(vec.transform(list(te.honest)))[:, 1]
    m = te.bd_works.values
    out["pairwise_all"] = float((sa > sh).mean())
    out["pairwise_working"] = float((sa[m] > sh[m]).mean()) if m.sum() else float("nan")
    out["pairwise_inert"] = float((sa[~m] > sh[~m]).mean()) if (~m).sum() else float("nan")
    out["n_working"], out["n_inert"] = int(m.sum()), int((~m).sum())
    return out


def transfer_protocol(p):
    """transfer.py's block: train control_tax -> test apps-source, plus three cross-model rows."""
    ct, ap = p[p.src == "control_tax"], p[p.src == "apps"]

    def fit(tr):
        vec = make_vec()
        X = vec.fit_transform(list(tr.honest) + list(tr.attack))
        y = np.r_[np.zeros(len(tr)), np.ones(len(tr))]
        return vec, LogisticRegression(max_iter=3000).fit(X, y)

    def pairacc(vec, clf, te):
        sa = clf.predict_proba(vec.transform(list(te.attack)))[:, 1]
        sh = clf.predict_proba(vec.transform(list(te.honest)))[:, 1]
        return float((sa > sh).mean())

    out = {}
    tr = ct[~ct.pid.isin(set(ap.pid))]
    if len(tr) and len(ap):
        out["control_tax->apps_gpt4"] = (pairacc(*fit(tr), ap), len(tr), len(ap))
    for a, b in [("openai/o3-mini", "anthropic/claude-3-7-sonnet-latest"),
                 ("anthropic/claude-3-7-sonnet-latest", "openai/o3-mini"),
                 ("openai/o1-mini", "google/gemini-2.0-flash")]:
        tr = ct[ct.model == a]; te = ct[(ct.model == b) & (~ct.pid.isin(set(tr.pid)))]
        if len(tr) and len(te):
            out[f"{a}->{b}"] = (pairacc(*fit(tr), te), len(tr), len(te))
    return out


def style_markers(ct):
    def style(code):
        return dict(has_hash=('#' in code), has_def=bool(re.search(r'\bdef\b', code)),
                    has_main=('__main__' in code), n_blank=code.count('\n\n'),
                    has_typehint=bool(re.search(r'->|: int|: str|: list', code)),
                    input_style=('sys.stdin' in code))
    S = pd.DataFrame([dict(cls='honest', **style(c)) for c in ct.honest] +
                     [dict(cls='attack', **style(c)) for c in ct.attack])
    return S.groupby('cls').mean().round(3).T


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=1, help="repeat the 30%% split over seeds 0..N-1")
    ap.add_argument("--shards", default="train_*.parquet")
    args = ap.parse_args()

    p_raw = load_pairs(args.shards)
    ct_raw = p_raw[p_raw.src == "control_tax"]
    print(f"control_tax pairs {len(ct_raw)} over {ct_raw.pid.nunique()} problems; "
          f"apps-source pairs {(p_raw.src == 'apps').sum()}")

    results = {}
    for strip in (False, True):
        p = preprocess(p_raw, strip)
        ct = p[p.src == "control_tax"]
        per_seed = [matched_protocol(ct, s) for s in range(args.seeds)]
        results[strip] = {"matched": per_seed, "transfer": transfer_protocol(p),
                          "style": style_markers(ct)}

    keys = ["tfidf_auroc", "pairwise_all", "pairwise_working", "pairwise_inert",
            "surface7_auroc", "length_auroc", "length_within_pair"]
    print("\n=== MATCHED PROTOCOL (control_tax pairs, problem-disjoint 30% test) ===")
    print(f"{'quantity':22s} {'unstripped':>22s} {'stripped':>22s} {'delta':>8s}")
    for k in keys:
        u = np.array([r[k] for r in results[False]["matched"]])
        s = np.array([r[k] for r in results[True]["matched"]])
        if args.seeds > 1:
            us, ss = f"{u.mean():.4f} +/- {u.std():.4f}", f"{s.mean():.4f} +/- {s.std():.4f}"
        else:
            us, ss = f"{u[0]:.4f}", f"{s[0]:.4f}"
        print(f"{k:22s} {us:>22s} {ss:>22s} {s.mean() - u.mean():+8.4f}")
    r0 = results[True]["matched"][0]
    print(f"(seed 0: n_test_pairs {r0['n_test_pairs']}, working {r0['n_working']}, inert {r0['n_inert']})")
    print("pairwise accuracies: report to THREE decimals (resolution 1/n_test_pairs).")

    print("\n=== TRANSFER (pairwise accuracy; n_train, n_test) ===")
    for k in results[False]["transfer"]:
        u, ntr, nte = results[False]["transfer"][k]
        s = results[True]["transfer"].get(k, (float("nan"),) * 3)[0]
        print(f"{k:60s} unstripped {u:.4f}  stripped {s:.4f}  delta {s - u:+.4f}  (n {ntr}/{nte})")

    print("\n=== STYLE MARKERS, control_tax pairs (mean per class) ===")
    print("unstripped:\n", results[False]["style"])
    print("stripped:\n", results[True]["style"])
    print("\nReading: has_hash must go to ~0 after stripping by construction. What matters is whether"
          "\nthe inert-vs-working contrast and the transfer rows hold once it is gone.")


if __name__ == "__main__":
    main()
