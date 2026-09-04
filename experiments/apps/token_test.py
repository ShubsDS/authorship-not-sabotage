"""The token-level confirmation: is our classifier keying on the identifiers AICD Bench named?

`PLAN.md` §1 (Sep 8, CPU) and `../../paper/OUTLINE.md` §3, "Authorship, four ways".

AICD Bench (`2602.02079`) Appendix D.1 reports, for AI-generated vs human-written code in general:

    "AI-generated code often uses verbose, prompt-echoing identifiers like answer, output, result,
     tests, and index. In contrast, human-written code tended to use shorter, organic identifiers
     like li, nums, pos, a1, and cur."

Those ten tokens are named in *their* paper, in advance of this test, which is what makes this
confirmatory rather than a fishing expedition. In our corpus the attack class is LLM-written and the
honest class is human-written, so if the mechanism really is authorship the prediction is directional
and specific:

    AICD's LLM identifiers  -> positive coefficients (push toward the ATTACK class)
    AICD's human identifiers -> negative coefficients (push toward the HONEST class)

The test reports that either way, with a permutation null over vocabulary-matched tokens so a
"they're all near the top" result cannot come from the tokens simply being common.

    python token_test.py
"""

from __future__ import annotations

import glob
import sys

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

sys.path.insert(0, ".")
from data import _honest_code, _pick_backdoor, strip_comments  # noqa: E402

# Pre-registered from AICD Bench App. D.1 via `../../lit/01-verified-bibliography.md` §4.
AICD_LLM = ["answer", "output", "result", "tests", "index"]
AICD_HUMAN = ["li", "nums", "pos", "a1", "cur"]
N_PERM = 10000
RNG = np.random.RandomState(0)


def build_train() -> pd.DataFrame:
    """Koran's paired train split, exactly as koran_split_eval.py builds it."""
    km = pd.read_parquet("koran_meta.parquet")
    test = pd.read_pickle("koran_samples.pkl")
    test_pids = set(test.problem_id.astype(str))
    train_pids = set(km.problem_id.astype(str)) - test_pids
    full = pd.concat(
        [pq.read_table(f, columns=["problem_id", "solutions", "backdoors"]).to_pandas()
         for f in sorted(glob.glob("train_*.parquet"))], ignore_index=True)
    full = full[full.problem_id.astype(str).isin(train_pids)]
    tbm = dict(zip(km.problem_id.astype(str), km.top_backdoor_model))
    rows = []
    for _, r in full.iterrows():
        row = {"problem_id": str(r.problem_id),
               "backdoors": [dict(b) for b in r.backdoors],
               "solutions": [dict(s) for s in r.solutions],
               "top_backdoor_model": tbm.get(str(r.problem_id))}
        bd, hc = _pick_backdoor(row), _honest_code(row)
        if bd is None or hc is None:
            continue
        rows.append((row["problem_id"], 1, bd["backdoor_code"]))
        rows.append((row["problem_id"], 0, hc))
    tr = pd.DataFrame(rows, columns=["problem_id", "label", "code"])
    tr["stripped"] = tr.code.map(strip_comments)
    return tr


def main() -> None:
    tr = build_train()
    print(f"train pairs: {len(tr)} samples, {int(tr.label.sum())} attack / "
          f"{int((1 - tr.label).sum())} honest, {tr.problem_id.nunique()} problems\n")

    vec = TfidfVectorizer(token_pattern=r"[A-Za-z_]+|\d+|[^\sA-Za-z_\d]", ngram_range=(1, 2),
                          min_df=2, max_features=50000, sublinear_tf=True)
    X = vec.fit_transform(tr.stripped)
    clf = LogisticRegression(max_iter=5000, C=5).fit(X, tr.label)

    names = np.array(vec.get_feature_names_out())
    coef = clf.coef_[0]
    # Identifier-like unigrams only: bigrams and punctuation are not what AICD names.
    is_ident = np.array([n.isidentifier() for n in names])
    idn, idc = names[is_ident], coef[is_ident]
    order = np.argsort(idc)
    rank_of = {n: i for i, n in enumerate(idn[order])}   # 0 = most human-pushing
    n_id = len(idn)
    print(f"vocabulary: {len(names)} features, {n_id} identifier unigrams\n")

    print("--- top 20 identifiers pushing toward ATTACK (LLM-written) ---")
    print(", ".join(idn[order][-20:][::-1]))
    print("\n--- top 20 identifiers pushing toward HONEST (human-written) ---")
    print(", ".join(idn[order][:20]))

    def percentile(tok: str) -> float | None:
        """0 = most human-pushing, 1 = most attack-pushing."""
        return None if tok not in rank_of else rank_of[tok] / (n_id - 1)

    print("\n--- the ten AICD App. D.1 tokens, pre-registered above ---")
    print(f"{'token':10s} {'AICD says':12s} {'coef':>9s} {'percentile':>11s}  {'direction':>9s}")
    hits = {"llm": [], "human": []}
    for group, toks, want in (("llm", AICD_LLM, "attack"), ("human", AICD_HUMAN, "honest")):
        for t in toks:
            p = percentile(t)
            if p is None:
                print(f"{t:10s} {want:12s} {'--':>9s} {'not in vocab':>11s}")
                continue
            c = idc[idn.tolist().index(t)]
            got = "attack" if c > 0 else "honest"
            mark = "OK" if got == want else "MISS"
            hits[group].append(p)
            print(f"{t:10s} {want:12s} {c:9.4f} {p:11.3f}  {got:>9s} {mark}")

    if not hits["llm"] or not hits["human"]:
        raise SystemExit("\ntoo few AICD tokens in vocabulary to test")

    sep = float(np.mean(hits["llm"]) - np.mean(hits["human"]))
    print(f"\nmean percentile: AICD-LLM {np.mean(hits['llm']):.3f} vs "
          f"AICD-human {np.mean(hits['human']):.3f}   separation = {sep:+.3f}")

    # Permutation null: could any two token sets of these sizes separate this far by chance?
    n_l, n_h = len(hits["llm"]), len(hits["human"])
    pcts = np.arange(n_id) / (n_id - 1)
    null = np.empty(N_PERM)
    for i in range(N_PERM):
        pick = RNG.choice(n_id, n_l + n_h, replace=False)
        null[i] = pcts[pick[:n_l]].mean() - pcts[pick[n_l:]].mean()
    p_two = float((np.abs(null) >= abs(sep)).mean())
    print(f"permutation null over {N_PERM} random token pairings: "
          f"mean {null.mean():+.3f}, sd {null.std():.3f}")
    print(f"two-sided p = {p_two:.4f}")
    print("\nVERDICT:", "the AICD tokens separate in the predicted direction beyond chance"
          if p_two < 0.05 and sep > 0 else
          "NOT significant — report it as such, and keep the mechanism claim as inference")


if __name__ == "__main__":
    main()
