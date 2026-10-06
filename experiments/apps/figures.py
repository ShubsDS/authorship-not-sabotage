"""Build the paper's figures and appendix table into ../../paper/fig/.

    fig1-overview.pdf          Figure 1: (a) two floors against the 24 monitors, (b) what survives
                               when one model writes both classes
    fig2-rho.pdf               Figure 2: retained separability rho for every arm, classifier and
                               monitor, against the bands fixed before any arm ran
    figA1-agentic.pdf          Appendix: the structural floor in five agentic settings
    tabA1-protocol-baseline.tex  Appendix: the protocol x baseline table

Every plotted value is a named constant below. Before drawing, check() asserts each one against the
\\newcommand macros in ../../paper/main.tex, so a figure cannot disagree with the text. Figure 1(a)
also reads the 24 monitor AUROCs from monitor-summary.json (written by fetch_inputs.py), and the
appendix figure reads ../agentic/within_task_null.json.

All S, B' and rho values are pooled out-of-fold estimates with 95% bootstrap intervals over
problems (rho: S and B' resampled jointly), the estimator the paper uses throughout.

Figures are sized at the width main.tex includes them at, so font sizes are the printed sizes.

Usage (from experiments/apps):
    python figures.py
"""

from __future__ import annotations

import json
import math
import os
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Nimbus Roman", "Times New Roman", "Times", "STIXGeneral", "DejaVu Serif"],
    "mathtext.fontset": "stix",
    "pdf.fonttype": 42,          # TrueType, not Type 3
    "axes.linewidth": 0.6,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
})

OUT = "../../paper/fig"
PDF_METADATA = {"CreationDate": None}
TEXT_W = 5.5                     # the NeurIPS text block, in inches

# --- theme ---------------------------------------------------------------------------------
INK, INK2, MUTED, GRID = "#1f2328", "#57606a", "#8c959f", "#e4e7eb"
BLUE, BLUE_L = "#1f5fa8", "#8fb4de"          # the bag-of-words classifier (ours)
ORANGE = "#d4651c"                           # the LLM monitor
STORED = "#b7bcc3"                           # stored pairs
BAND_C, BAND_P, BAND_N = "#f1f5fb", "#ffffff", "#fbf3ec"   # band shading: authorship / partial / content
FS = 7.5                                     # base font size at print width

# --- measured values (as reported in main.tex) ----------------------------------------------
TFIDF_FLOOR = 0.8063                         # Koran paired train -> 1,375-item test split
NOCODE_FLOOR = 0.7715                        # 5x5 CV within the test split
NOCODE_HELDOUT = 0.7163

# Figure 1(b): pooled out-of-fold AUROC with 95% CI; B' on the same problems as S.
GENERATORS = [
    # name,       B' (stored),              S (same writer),          S matched (same writer and prompt)
    ("Sonnet 5", (0.8646, 0.8482, 0.8811), (0.7504, 0.7295, 0.7713), (0.6411, 0.6179, 0.6621)),
    ("Haiku 4.5", (0.8564, 0.8392, 0.8726), (0.5344, 0.5159, 0.5531), (0.5391, 0.5197, 0.5581)),
]

# Figure 2: (group, label, rho, lo, hi, kind). kind: clf | mon | one
RHO_ROWS = [
    ("Bag-of-words classifier", None, None, None, None, None),
    (None, "Sonnet 5, all attempts (n = 623)", 0.687, 0.625, 0.755, "clf"),
    (None, "Sonnet 5, verified attacks (n = 99)", 0.861, 0.662, 1.089, "clf"),
    (None, "Sonnet 5, prompt-matched (n = 586)", 0.390, 0.326, 0.454, "clf"),
    (None, "Sonnet 5, verified, prompt-matched (n = 96)", 0.662, 0.494, 0.856, "clf"),
    (None, "Haiku 4.5, all attempts (n = 611)", 0.097, 0.044, 0.150, "clf"),
    (None, "Haiku 4.5, prompt-matched (n = 562)", 0.110, 0.055, 0.165, "clf"),
    ("LLM monitor", None, None, None, None, None),
    (None, "Sonnet 5 monitor, all attempts", 0.145, 0.111, 0.182, "mon"),
    (None, "Sonnet 5 monitor, verified attacks", 0.717, 0.601, 0.832, "mon"),
    (None, "Haiku 4.5 monitor, all attempts", 0.151, 0.063, 0.242, "mon"),
    (None, "Haiku 4.5 monitor, verified attacks", 0.766, 0.588, 0.963, "mon"),
]
BANDS = (0.33, 0.72)


def style(ax):
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(MUTED)
    ax.tick_params(axis="x", colors=INK2, labelsize=FS, length=2.5)
    ax.tick_params(axis="y", colors=INK, labelsize=FS, length=0)
    ax.grid(axis="x", color=GRID, lw=0.5, zorder=0)
    ax.set_axisbelow(True)


def panel_label(ax, s, x=-0.02):
    ax.text(x, 1.07, s, transform=ax.transAxes, fontsize=FS + 1, weight="bold", color=INK,
            ha="left", va="bottom")


def save(fig, name):
    fig.savefig(f"{OUT}/{name}", metadata=PDF_METADATA)
    plt.close(fig)


# --- Figure 1 --------------------------------------------------------------------------------

def fig1_overview():
    aurocs = sorted(m["test_auroc"] for m in json.load(open("monitor-summary.json")))
    n = len(aurocs)
    fig = plt.figure(figsize=(TEXT_W, 2.15))
    ax = fig.add_axes([0.075, 0.20, 0.40, 0.66])
    bx = fig.add_axes([0.585, 0.20, 0.405, 0.66])

    # (a) monitors as a sorted strip, floors as rules labelled in place
    style(ax)
    below = sum(a < TFIDF_FLOOR for a in aurocs)
    ax.axvspan(0.5, TFIDF_FLOOR, color=BAND_C, lw=0, zorder=0)
    ax.scatter(aurocs, range(1, n + 1), s=11, color=INK2, lw=0, zorder=4)
    for v, c, lab, dy in ((NOCODE_FLOOR, ORANGE, f"reads no code\n{v_(NOCODE_FLOOR)}", 0),
                          (TFIDF_FLOOR, BLUE, f"bag of words\n{v_(TFIDF_FLOOR)}", 0)):
        ax.plot([v, v], [0, n + 1], color=c, lw=1.3, zorder=3)
    ax.text(NOCODE_FLOOR - 0.008, n + 1.6, f"reads no code {v_(NOCODE_FLOOR)}", color=ORANGE,
            fontsize=FS - 0.5, ha="right", va="bottom")
    ax.text(TFIDF_FLOOR + 0.008, n + 1.6, f"bag of words {v_(TFIDF_FLOOR)}", color=BLUE,
            fontsize=FS - 0.5, ha="left", va="bottom")
    ax.plot([0.5, 0.5], [0, n + 1], color=MUTED, lw=0.7, ls=(0, (2, 2)), zorder=2)
    ax.text(0.505, 0.6, "chance", color=MUTED, fontsize=FS - 1, ha="left", va="bottom")
    ax.text(0.405, n - 1.5, f"{below} of {n} monitors\nbelow both floors", fontsize=FS - 0.5,
            color=INK, ha="left", va="top", linespacing=1.2)
    ax.set_xlim(0.40, 1.0); ax.set_ylim(0, n + 4.2)
    ax.set_xticks([0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    ax.set_yticks([1, n]); ax.set_yticklabels(["1", str(n)], color=INK2)
    ax.set_ylabel("monitor rank", fontsize=FS, color=INK, labelpad=1)
    ax.set_xlabel("AUROC, filtered comment-stripped test split", fontsize=FS, color=INK)
    panel_label(ax, "a", x=-0.15)

    # (b) bars start at chance, so a bar's height is above-chance separability and the ratio of
    # two bars is rho.
    bx.spines[["top", "right"]].set_visible(False)
    bx.spines[["left", "bottom"]].set_color(MUTED)
    bx.tick_params(colors=INK2, labelsize=FS, length=2.5)
    bx.grid(axis="y", color=GRID, lw=0.5, zorder=0); bx.set_axisbelow(True)
    w = 0.26
    cols = (STORED, BLUE_L, BLUE)
    labels = ("stored pairs (human vs. model)", "one model writes both",
              "one model, one prompt")
    for g, (name, *vals) in enumerate(GENERATORS):
        for k, (pt, lo, hi) in enumerate(vals):
            x = g + (k - 1) * (w + 0.03)
            bx.bar(x, pt - 0.5, w, bottom=0.5, color=cols[k], lw=0, zorder=3,
                   label=labels[k] if g == 0 else None)
            bx.plot([x, x], [lo, hi], color=INK, lw=0.7, zorder=4)
            bx.text(x, hi + 0.008, f"{pt:.2f}", ha="center", va="bottom", fontsize=FS - 1,
                    color=INK)
    bx.set_xticks([0, 1]); bx.set_xticklabels([g[0] for g in GENERATORS], color=INK, fontsize=FS)
    bx.set_xlim(-0.55, 1.55); bx.set_ylim(0.5, 1.13)
    bx.set_yticks([0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    bx.spines["left"].set_bounds(0.5, 1.0)
    bx.set_ylabel("bag-of-words AUROC", fontsize=FS, color=INK, labelpad=2)
    bx.set_xlabel("generator of the rebuilt corpus", fontsize=FS, color=INK)
    leg = bx.legend(loc="upper center", fontsize=FS - 1, frameon=False, handlelength=1.0,
                    handleheight=0.8, labelspacing=0.25, borderaxespad=0.0)
    for t in leg.get_texts():
        t.set_color(INK)
    panel_label(bx, "b", x=-0.17)
    save(fig, "fig1-overview.pdf")
    print(f"Fig 1: {n} monitors, median {statistics.median(aurocs):.3f}, max {aurocs[-1]:.3f}, "
          f"{below} below bag of words, {sum(a < NOCODE_FLOOR for a in aurocs)} below no code")


def v2(x):
    """Two decimals, rounding half up (0.145 prints as 0.15, as in the text)."""
    return f"{math.floor(x * 100 + 0.5) / 100:.2f}"


def v_(x):
    """Three decimals, rounding half up (the paper prints 0.7715 as 0.772)."""
    return f"{math.floor(x * 1000 + 0.5) / 1000:.3f}"


# --- Figure 2 --------------------------------------------------------------------------------

def fig2_rho():
    rows = RHO_ROWS
    fig, ax = plt.subplots(figsize=(TEXT_W, 2.45))
    fig.subplots_adjust(left=0.37, right=0.835, top=0.92, bottom=0.15)
    style(ax)
    XMAX = 1.12
    n = len(rows)
    ys = [n - 1 - i for i in range(n)]
    lo, hi = BANDS
    for x0, x1, c in ((0, lo, BAND_C), (hi, XMAX, BAND_N)):
        ax.axvspan(x0, x1, color=c, lw=0, zorder=0)
    for b in BANDS:
        ax.axvline(b, color=MUTED, lw=0.6, zorder=1)
    ax.axvline(1.0, color=MUTED, lw=0.6, ls=(0, (2, 2)), zorder=1)
    for x, t in ((lo / 2, "mostly authorship"), ((lo + hi) / 2, "partial"),
                 ((hi + 1.0) / 2, "mostly content")):
        ax.text(x, n - 0.45, t, ha="center", va="bottom", fontsize=FS - 1, color=INK2)
    ax.text(1.03, n - 0.45, r"$\rho$ [95% CI]", transform=ax.get_yaxis_transform(),
            ha="left", va="bottom", fontsize=FS - 1, color=INK2)
    ticks, labels = [], []
    for y, (grp, lab, r, l, h, kind) in zip(ys, rows):
        if grp:
            ax.text(-0.012, y, grp, transform=ax.get_yaxis_transform(), ha="right", va="center",
                    fontsize=FS, color=INK, weight="bold")
            continue
        ticks.append(y); labels.append(lab)
        c = BLUE if kind == "clf" else ORANGE
        ax.plot([l, h], [y, y], color=c, lw=1.4, alpha=0.45, solid_capstyle="round", zorder=3)
        ax.scatter([r], [y], s=18, color=c, marker="o" if kind == "clf" else "s", lw=0, zorder=4)
        ax.text(1.03, y, f"{v2(r)} [{v2(l)}, {v2(h)}]", transform=ax.get_yaxis_transform(),
                ha="left", va="center", fontsize=FS - 1, color=INK)
    ax.set_yticks(ticks); ax.set_yticklabels(labels)
    ax.set_ylim(-0.6, n + 0.3); ax.set_xlim(0, XMAX)
    ax.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_xlabel("retained separability  ρ = (S − 0.5) / (B′ − 0.5)",
                  fontsize=FS, color=INK)
    save(fig, "fig2-rho.pdf")
    print(f"Fig 2: {sum(1 for r in rows if r[5])} rows")


# --- Appendix figure: agentic settings -------------------------------------------------------

AGENTIC = [("bash", 0.5044), ("shade", 0.6022), ("iac", 0.7041), ("rogue_eval", 0.6158),
           ("agentdojo", 0.8020)]


def figA1_agentic():
    nulls = json.load(open("../agentic/within_task_null.json"))
    rows = AGENTIC[::-1]
    fig, ax = plt.subplots(figsize=(0.80 * TEXT_W, 2.0))
    fig.subplots_adjust(left=0.27, right=0.97, top=0.86, bottom=0.20)
    style(ax)
    for i, (s, v) in enumerate(rows):
        nm, p95 = nulls[s]["null_mean"], nulls[s]["null_p95"]
        ax.plot([0.5, p95], [i, i], color=GRID, lw=5, solid_capstyle="butt", zorder=2)
        ax.scatter([nm], [i], s=14, marker="|", color=MUTED, zorder=3)
        ax.scatter([v], [i], s=22, color=BLUE, lw=0, zorder=4)
        ax.text(max(v, p95) + 0.012, i, f"{v:.3f}", va="center", fontsize=FS - 0.5, color=INK)
    ax.axvline(0.5, color=MUTED, lw=0.6, ls=(0, (2, 2)), zorder=1)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([f"{s} ({nulls[s]['n_tasks']} tasks)" for s, _ in rows])
    ax.set_xlim(0.45, 0.90); ax.set_ylim(-0.6, len(rows) - 0.4)
    ax.set_xlabel("within-task AUROC from character count alone", fontsize=FS, color=INK)
    ax.plot([], [], color=GRID, lw=5, label="permutation null, up to its 95th percentile")
    ax.scatter([], [], s=22, color=BLUE, label="observed")
    leg = ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, fontsize=FS - 0.5,
                    frameon=False, handlelength=1.4, columnspacing=1.2, borderaxespad=0.2)
    for t in leg.get_texts():
        t.set_color(INK)
    save(fig, "figA1-agentic.pdf")
    print("Fig A1: " + ", ".join(f"{s} {v:.3f} (p {nulls[s]['p']:.3f})" for s, v in AGENTIC))


# --- Appendix table: protocol x baseline -----------------------------------------------------
# Pairwise accuracies get three decimals (one pair is 1/2,641); AUROCs get four.
TAB_ROWS = [
    ("AUROC", "Filtered split, 1{,}375 test items", "bag of words, word 1--2-grams", "0.8063",
     "stripped", "above 20 of 24"),
    ("AUROC", "\\quad same", "bag of words, word 1--2-grams", "0.8914", "kept", "above 22 of 24"),
    ("AUROC", "\\quad same", "bag of words, character 3--5-grams", "0.7830", "stripped",
     "above 20 of 24"),
    ("AUROC", "\\quad same, 5$\\times$5 CV in test", "no code: difficulty, tests, length",
     "0.7715", "no code", "above 20 of 24"),
    ("AUROC", "\\quad same, held-out 30\\%", "no code: difficulty, tests, length", "0.7163",
     "no code", "above 18 of 24"),
    ("AUROC", "\\quad same", "code length", "0.4726", "stripped", "chance"),
    ("AUROC", "\\quad same", "count of \\texttt{\\#}", "0.4983", "stripped", "chance"),
    ("AUROC", "\\quad same", "count of \\texttt{\\#}", "0.6957", "kept", ""),
    ("AUROC", "Full artifact, per problem", "all metadata", "0.8917", "no code", ""),
    ("AUROC", "\\quad same", "difficulty", "0.6823", "no code", ""),
    ("AUROC", "\\quad same", "\\texttt{solution\\_passes\\_tests}", "0.7881", "no code", ""),
    ("AUROC", "Both classes per problem", "all metadata", "0.5000", "no code", "by construction"),
    ("pairwise", "Matched pairs, 5 splits", "bag of words", "0.897", "stripped",
     "monitor 0.69 to 0.81"),
    ("pairwise", "\\quad working backdoors", "bag of words", "0.935", "stripped", ""),
    ("pairwise", "\\quad inert backdoors", "bag of words", "0.879", "stripped", ""),
    ("pairwise", "\\quad across generators", "bag of words", "0.969", "stripped", ""),
    ("pairwise", "\\quad all pairs", "bag of words", "0.962", "kept", ""),
    ("pairwise", "\\quad working backdoors", "bag of words", "0.979", "kept", ""),
    ("pairwise", "\\quad inert backdoors", "bag of words", "0.955", "kept", ""),
    ("pairwise", "\\quad across generators", "bag of words", "0.994", "kept", ""),
    ("pairwise", "\\quad full artifact", "code length", "0.826", "kept", ""),
]


def tabA1():
    col = ("@{}>{\\raggedright\\arraybackslash}p{0.27\\linewidth}"
           ">{\\raggedright\\arraybackslash}p{0.30\\linewidth}r"
           ">{\\raggedright\\arraybackslash}p{0.09\\linewidth}"
           ">{\\raggedright\\arraybackslash}p{0.17\\linewidth}@{}")

    def body(rows):
        return [" & ".join((r[1], r[2], r[3], r[4], r[5])) + " \\\\" for r in rows]

    lines = [
        "% generated by experiments/apps/figures.py; do not edit by hand",
        "\\begin{table}[h]\\centering\\footnotesize",
        "\\setlength{\\tabcolsep}{4pt}",
        "\\caption{\\textbf{Every baseline we ran on the stored pairs.} Rows are measured under "
        "the protocol in the first column and are not comparable across protocols. "
        "\\emph{Comments} says whether comments were stripped before the baseline read the code; "
        "\\emph{no code} marks baselines that never read the program. Rows with comments kept "
        "are inflated by the comment channel and are shown for contrast. Matched-pair rows are "
        "problem-disjoint and are compared with a DSPy tutorial monitor on the same pairs.}",
        "\\label{tab:protocol-baseline}",
        "\\begin{tabular}{" + col + "}",
        "\\toprule",
        "Protocol & Baseline & Value & Comments & Compared with \\\\",
        "\\midrule",
        "\\multicolumn{5}{@{}l}{\\emph{AUROC}} \\\\",
    ]
    lines += body([r for r in TAB_ROWS if r[0] == "AUROC"])
    lines += ["\\addlinespace", "\\multicolumn{5}{@{}l}{\\emph{Pairwise accuracy}} \\\\"]
    lines += body([r for r in TAB_ROWS if r[0] != "AUROC"])
    lines += ["\\bottomrule", "\\end{tabular}", "\\end{table}"]
    with open(f"{OUT}/tabA1-protocol-baseline.tex", "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"Table A1: {len(TAB_ROWS)} rows")


# --- check(): every plotted value against main.tex -------------------------------------------
PAPER_TEX = "../../paper/main.tex"


def _macros(path=PAPER_TEX):
    import re
    out = {}
    for name, val in re.findall(r"\\newcommand\{\\(\w+)\}\{([^{}]*)\}", open(path).read()):
        try:
            out[name] = float(val.replace("{,}", ""))
        except ValueError:
            pass
    return out


def check():
    m = _macros()
    bad = []

    def eq(macro, got, dp=None):
        if macro not in m:
            bad.append(f"{macro}: absent from main.tex"); return
        got_r = math.floor(got * 10 ** dp + 0.5) / 10 ** dp if dp else got
        if abs(m[macro] - got_r) > 5e-4:
            bad.append(f"{macro}: main.tex {m[macro]} vs figures.py {got_r}")

    eq("tfidfKoran", TFIDF_FLOOR, 3); eq("nocodeCV", NOCODE_FLOOR, 3)
    eq("nocodeHeldout", NOCODE_HELDOUT, 3)
    (_, bs, ss, ms), (_, hb, hs, hm) = GENERATORS
    eq("sameGenBprime", bs[0], 3); eq("sameGenS", ss[0], 3); eq("matchedS", ms[0], 3)
    eq("haikuBprime", hb[0], 3); eq("haikuS", hs[0], 3); eq("haikuSMatched", hm[0], 3)
    r = {row[1]: row[2:5] for row in RHO_ROWS if row[1]}
    for lab, mac in (("Sonnet 5, all attempts (n = 623)", "sameGenRho"),
                     ("Sonnet 5, verified attacks (n = 99)", "strictRho"),
                     ("Sonnet 5, prompt-matched (n = 586)", "matchedRho"),
                     ("Sonnet 5, verified, prompt-matched (n = 96)", "matchedStrictRho"),
                     ("Haiku 4.5, all attempts (n = 611)", "haikuRho"),
                     ("Haiku 4.5, prompt-matched (n = 562)", "haikuMatchedRho"),
                     ("Sonnet 5 monitor, all attempts", "monRhoHead"),
                     ("Sonnet 5 monitor, verified attacks", "monRhoStrict"),
                     ("Haiku 4.5 monitor, all attempts", "monHaikuRhoHead"),
                     ("Haiku 4.5 monitor, verified attacks", "monHaikuRhoStrict")):
        eq(mac, r[lab][0], 3); eq(mac + "Lo", r[lab][1], 3); eq(mac + "Hi", r[lab][2], 3)
    eq("bashFloor", AGENTIC[0][1], 3); eq("agentdojoFloor", AGENTIC[-1][1], 3)
    if os.path.exists("monitor-summary.json"):
        a = sorted(x["test_auroc"] for x in json.load(open("monitor-summary.json")))
        eq("monN", float(len(a))); eq("monMedian", statistics.median(a), 3); eq("monMax", a[-1], 3)
        eq("tfidfKoranCount", float(sum(x < TFIDF_FLOOR for x in a)))
        eq("nocodeCVCount", float(sum(x < NOCODE_FLOOR for x in a)))
    if bad:
        raise SystemExit("CHECK FAILED against main.tex:\n  " + "\n  ".join(bad))
    print(f"CHECK: {len(m)} numeric macros read from main.tex; every figure value agrees")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    check()
    tabA1()
    fig1_overview()
    fig2_rho()
    figA1_agentic()
    print(f"\nwrote to {os.path.abspath(OUT)}")
