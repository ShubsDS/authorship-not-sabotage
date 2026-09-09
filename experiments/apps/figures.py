"""The paper's figures. `python figures.py` writes into ../../paper/fig/.

F1  protocol x baseline    -> LaTeX booktabs table (it is >7 rows of labelled values, which is a
                              table, not a chart)
F2  per-corpus floors      -> horizontal bars with the permutation null marked on every bar
F3  monitors vs our floors -> dot plot of 24 monitors against the two floors

Colour: slots 1 and 2 of the reference palette (blue #2a78d6, orange #eb6834) in their documented
order, which that palette certifies for the adjacent pairlist in light mode. Monitors and bars carry
one hue because they are one population - identity is not the job, magnitude is - and colour never
encodes rank. Text stays in ink colours, never the series colour.
"""

from __future__ import annotations

import json
import os
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

OUT = "../../paper/fig"
BLUE, ORANGE = "#2a78d6", "#eb6834"
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#8c8b86"
GRID = "#e3e2dd"

# Verified on this machine 2026-09-04; see ../REPRODUCED.md
TFIDF_FLOOR = 0.8063          # trained on Koran's paired train split, scored on their 1,375 test
NOCODE_FLOOR, NOCODE_SD = 0.7715, 0.0389   # 5x5 CV *within* the test split - a real caveat
NOCODE_HELDOUT = 0.7163                    # single 413-item held-out slice; clears 18 of 24
# Never pair 0.7715 with "above 18": that count belongs to 0.7163. 0.7715 clears 20 of 24.
# Mixing them is exactly R18's companion error, and it reached the README before this was caught.

# scan/ within-task floors and permutation nulls. Re-run on this machine 2026-09-04 by
# scan/matched.py: all five within-task values reproduce exactly. The fourth column is the number
# of task groups the within-task AUROC is averaged over, and it is not uniform - shade and iac rest
# on FIVE groups each, which the paper has to say out loud.
SCAN = [
    ("bash",       0.504, 0.490, 247),
    ("shade",      0.602, 0.508, 5),
    ("iac",        0.704, 0.484, 5),
    ("rogue_eval", 0.616, 0.480, 25),
    ("agentdojo",  0.802, 0.512, 16),
]


def style(ax):
    ax.spines[["top", "right"]].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID)
    ax.tick_params(colors=INK2, labelsize=8, length=3, width=0.8)
    ax.grid(axis="x", color=GRID, lw=0.6, zorder=0)
    ax.set_axisbelow(True)


def fig3_monitors():
    """24 monitors on Koran's exact split, against the two floors measured on that same split."""
    mon = json.load(open("monitor-summary.json"))
    aurocs = sorted(m["test_auroc"] for m in mon)
    n = len(aurocs)
    below_tfidf = sum(a < TFIDF_FLOOR for a in aurocs)
    below_nocode = sum(a < NOCODE_FLOOR for a in aurocs)

    fig, ax = plt.subplots(figsize=(5.5, 2.9))
    style(ax)
    # No +-sd band: that spread is across CV folds, not a CI on the mean, and drawn as a band it
    # visually swallows the bag-of-words floor 0.04 away. The sd goes in the legend text instead.
    ax.axvline(NOCODE_FLOOR, color=ORANGE, lw=2, zorder=3,
               label=f"reads no code  0.772 $\\pm$ 0.039  ({below_nocode} of {n} below)")
    ax.axvline(TFIDF_FLOOR, color=BLUE, lw=2, zorder=3,
               label=f"bag-of-words  {TFIDF_FLOOR:.3f}  ({below_tfidf} of {n} below)")
    ax.axvline(0.5, color=MUTED, lw=1, ls=(0, (4, 3)), zorder=2)
    ax.text(0.5, n + 0.4, "chance", ha="center", va="bottom", fontsize=7, color=MUTED)
    below_heldout = sum(a < NOCODE_HELDOUT for a in aurocs)

    ax.scatter(aurocs, range(1, n + 1), s=34, facecolor=INK2, edgecolor="white",
               linewidth=0.8, zorder=4)
    ax.set_yticks([])
    ax.set_ylim(0, n + 2.2)
    ax.set_xlim(0.40, 0.98)
    ax.set_xlabel("AUROC on the 1,375-item test split", fontsize=8.5, color=INK)
    ax.set_ylabel(f"{n} open-weight monitors\n(sorted)", fontsize=8.5, color=INK)
    leg = ax.legend(loc="lower right", fontsize=7.5, frameon=True, framealpha=1,
                    edgecolor=GRID, borderpad=0.5, borderaxespad=0.8)
    for t in leg.get_texts():
        t.set_color(INK)
    fig.tight_layout(pad=0.4)
    fig.savefig(f"{OUT}/f3-monitors-vs-floors.pdf")
    plt.close(fig)
    print(f"F3: {n} monitors, median {statistics.median(aurocs):.4f}, max {aurocs[-1]:.3f}")
    print(f"    below bag-of-words 0.8063:      {below_tfidf}/{n}")
    print(f"    below no-code 5x5 CV 0.7715:    {below_nocode}/{n}")
    print(f"    below no-code held-out 0.7163:  {below_heldout}/{n}")


def fig2_corpora():
    """Five same-generator agentic settings: the content-blind floor against its permutation null.

    A dumbbell, not bars. Bars imply length measured from zero, and zero is not the reference for an
    AUROC - 0.5 is. Dots carry position without implying area, so the axis can start near chance
    where the data actually lives.
    """
    rows = SCAN[::-1]
    names = [f"{r[0]}\n({r[3]} tasks)" for r in rows]
    vals = [r[1] for r in rows]
    nulls = [r[2] for r in rows]
    y = list(range(len(names)))

    fig, ax = plt.subplots(figsize=(5.5, 2.7))
    style(ax)
    ax.axvline(0.5, color=MUTED, lw=1, ls=(0, (4, 3)), zorder=2)
    ax.text(0.5, len(names) - 0.35, "chance", ha="center", va="bottom", fontsize=7, color=MUTED)

    for i, (v, nv) in enumerate(zip(vals, nulls)):
        ax.plot([nv, v], [i, i], color=GRID, lw=2.5, zorder=3, solid_capstyle="round")
    ax.scatter(nulls, y, s=40, facecolor=ORANGE, edgecolor="white", linewidth=0.8, zorder=5,
               label="permutation null")
    ax.scatter(vals, y, s=48, facecolor=BLUE, edgecolor="white", linewidth=0.8, zorder=6,
               label="within-task, character count only")
    for i, v in enumerate(vals):
        ax.text(v + 0.011, i, f"{v:.3f}", va="center", fontsize=7.5, color=INK)

    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=8, color=INK, linespacing=1.35)
    ax.set_ylim(-0.6, len(names) - 0.1)
    ax.set_xlim(0.44, 0.87)
    ax.set_xlabel("AUROC", fontsize=8.5, color=INK)
    leg = ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, fontsize=7.5,
                    frameon=False, handletextpad=0.4, columnspacing=1.4)
    for t in leg.get_texts():
        t.set_color(INK)
    fig.tight_layout(pad=0.4)
    fig.savefig(f"{OUT}/f2-corpus-floors.pdf")
    plt.close(fig)
    print("F2: 5 settings; bash 0.504 (clean, 247 tasks) to agentdojo 0.802 (leaky, 16 tasks); "
          "nulls 0.480-0.512. shade and iac rest on 5 task groups each.")


F1_ROWS = [
    ("Koran's exact split, comments stripped", "TF-IDF word 1--2gram", "AUROC", "0.8063",
     "above 20 of 24"),
    ("\\quad same, comments kept", "TF-IDF word 1--2gram", "AUROC", "0.8914", "above 22 of 24"),
    # 0.7715 is the 5x5 CV value and it clears 20, not 18. The "above 18" count belongs to
    # the 0.7163 held-out slice (see NOCODE_HELDOUT above and fig/CAPTIONS.md). Pairing them
    # is R18's companion error committed against ourselves; it shipped in this table once.
    ("\\quad same, reads no code", "difficulty $+$ \\#tests $+$ $|q|$", "AUROC",
     "0.7715 $\\pm$ 0.0389", "above 20 of 24"),
    ("\\quad same, held-out slice", "difficulty $+$ \\#tests $+$ $|q|$", "AUROC",
     "0.7163", "above 18 of 24"),
    ("\\quad same", "code length only", "AUROC", "0.4726", "chance"),
    ("\\quad same", "\\#-count detector", "AUROC", "0.4983", "chance (0.6957 unstripped)"),
    ("Raw artifact, problem level", "all metadata", "AUROC", "0.8917", "---"),
    ("\\quad same", "difficulty only", "AUROC", "0.6823", "---"),
    ("\\quad same", "\\texttt{solution\\_passes\\_tests}", "AUROC", "0.7881", "---"),
    ("Matched pairs (P3)", "all metadata", "AUROC", "0.5000", "exactly chance by construction"),
    ("DSPy matched, problem-disjoint", "TF-IDF word 1--2gram", "pairwise", "0.9621",
     "tutorial monitor 0.69--0.81"),
    ("\\quad working backdoors only", "TF-IDF word 1--2gram", "pairwise", "0.9787", "---"),
    ("\\quad \\textbf{inert} backdoors only", "TF-IDF word 1--2gram", "pairwise", "0.9543",
     "the signal is not sabotage"),
    ("\\quad same", "code length only", "pairwise", "0.8255", "and 0.4726 once filtered"),
]


def fig1_table():
    """Emit F1 as a LaTeX table that FITS NeurIPS's 5.5in text block.

    The first version of this table was 5 columns of `l` and overflowed the text block by
    ~104pt, with the rules running off the page edge. Three things fix it, and all three
    have to stay:
      - the Metric column is gone; rows are grouped under an AUROC / pairwise subheading
        instead, which is also a clearer statement of "not comparable across protocols";
      - Protocol, Baseline and Against are p{} columns, so long cells wrap instead of
        pushing the table wider;
      - \\footnotesize plus @{} at both edges reclaims the outer tabcolsep.
    Requires \\usepackage{array} in the preamble for the >{\\raggedright} column.
    """
    auroc = [r for r in F1_ROWS if r[2] == "AUROC"]
    pairw = [r for r in F1_ROWS if r[2] != "AUROC"]

    def body(rows):
        # drop the metric cell (index 2); it is carried by the group heading now
        return [" & ".join((r[0], r[1], r[3], r[4])) + " \\\\" for r in rows]

    # Widths tuned against the actual 5.5in block, and both constraints are tight:
    #   col 1 must hold "Koran's exact split, comments stripped" on one line, else
    #          "stripped" orphans onto a second;
    #   col 2 must hold \texttt{solution_passes_tests}, which is unbreakable and was
    #          7.7pt too wide at 0.205. The slack comes out of col 4, which wraps freely.
    col = ("@{}"
           ">{\\raggedright\\arraybackslash}p{0.345\\linewidth}"
           ">{\\raggedright\\arraybackslash}p{0.225\\linewidth}"
           "r"
           ">{\\raggedright\\arraybackslash}p{0.170\\linewidth}"
           "@{}")

    lines = [
        "% F1 - generated by experiments/apps/figures.py, do not hand-edit",
        "\\begin{table}[t]\\centering\\footnotesize",
        "\\setlength{\\tabcolsep}{4pt}",
        "\\caption{What the field's preprocessing leaves behind. Every row is measured under the "
        "protocol named in column one; rows are not comparable across protocols.}",
        "\\label{tab:protocol-baseline}",
        "\\begin{tabular}{" + col + "}",
        "\\toprule",
        "Protocol & Baseline & Value & Against \\\\",
        "\\midrule",
        "\\multicolumn{4}{@{}l}{\\emph{AUROC}} \\\\",
    ]
    lines += body(auroc)
    lines += ["\\addlinespace",
              "\\multicolumn{4}{@{}l}{\\emph{Pairwise accuracy}} \\\\"]
    lines += body(pairw)
    lines += ["\\bottomrule", "\\end{tabular}", "\\end{table}"]
    with open(f"{OUT}/f1-protocol-baseline.tex", "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"F1: {len(F1_ROWS)} rows ({len(auroc)} AUROC, {len(pairw)} pairwise), "
          f"4 columns, sized to fit a 5.5in text block")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    fig1_table()
    fig2_corpora()
    fig3_monitors()
    print(f"\nwrote to {os.path.abspath(OUT)}")
