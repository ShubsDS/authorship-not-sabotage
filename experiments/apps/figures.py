"""Build the paper's figures and the F1 table into ../../paper/fig/.

    F1  protocol x baseline table  -> f1-protocol-baseline.tex
    F2  agentic-setting floors     -> f2-corpus-floors.pdf
    F3  monitors vs our floors     -> f3-monitors-vs-floors.pdf
    F4  the three constructions    -> f4-constructions.pdf

Every plotted value is a named constant below. Before drawing, check() asserts each one against the
\newcommand macros in ../../paper/main.tex, so a figure cannot disagree with the text. F3 also reads
the 24 monitor AUROCs from monitor-summary.json (written by fetch_inputs.py).

Figures are sized at the width main.tex includes them at, so font sizes are the printed sizes. The
paper sets in Times; Nimbus Roman (or Times New Roman) matches its metrics. Output is deterministic:
the PDF creation date is not stamped.

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
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch  # noqa: E402

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Nimbus Roman", "Times New Roman", "Times", "STIXGeneral", "DejaVu Serif"],
    "mathtext.fontset": "stix",
    "pdf.fonttype": 42,      # TrueType, not Type 3, which some camera-ready checkers reject
})

OUT = "../../paper/fig"

# No /CreationDate, so rebuilds are byte-identical.
PDF_METADATA = {"CreationDate": None}

# The 5.5in NeurIPS text block, and the widths main.tex includes each figure at.
TEXT_W = 5.5
W_F2, W_F3, W_F4 = 0.86 * TEXT_W, 0.64 * TEXT_W, 1.00 * TEXT_W

# --- ink -----------------------------------------------------------------------------------
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8c8b86", "#e3e2dd"
BLUE, ORANGE = "#2a78d6", "#eb6834"
CONNECT = "#d3d2cc"

# Card and badge palette.
OK_BG, OK_EC, OK_TX = "#f0fdf4", "#86efac", "#166534"      # controlled / honest
BAD_BG, BAD_EC, BAD_TX = "#fff1f2", "#fda4af", "#9f1239"   # confounded / attack
TGT_BG, TGT_TX = "#eef2ff", "#3730a3"                      # the target signal
TINT = "#f4f8fd"                                           # the two constructions we build
PANEL_BG, PANEL_EC = "#fafafa", "#d1d5db"

# Measured values, as reported in main.tex.
TFIDF_FLOOR = 0.8063                       # Koran paired train -> their 1,375-item test split
TFIDF_CI = (0.7704, 0.8409)                # bootstrap over problems
TFIDF_NULL = 0.5465                        # permutation null, 95th pct; p = 0.004975
NOCODE_FLOOR, NOCODE_SD = 0.7715, 0.0389   # 5x5 CV within the test split; clears 20 of 24
NOCODE_CI = (0.7319, 0.8005)               # CI of the pooled out-of-fold AUROC (0.7658)
NOCODE_NULL = 0.5545
NOCODE_HELDOUT = 0.7163                    # single 413-item held-out slice; clears 18 of 24

# Agentic settings (agentic/matched.py, agentic/floors2.py): within-task chars-only AUROC,
# permutation null, and the number of task groups the within-task AUROC averages over.
SCAN = [
    ("bash",       0.5044, 0.4896, 247),
    ("shade",      0.6022, 0.5079, 5),
    ("iac",        0.7041, 0.4841, 5),
    ("rogue_eval", 0.6158, 0.4801, 25),
    ("agentdojo",  0.8020, 0.5118, 16),
]

# F4: the classifier's AUROC on each construction's own pairs (B, S and the prompt-matched S).
# Each is measured on different problems, so they are a ladder, not a paired comparison.
CONSTRUCTIONS = [
    dict(key="stored",  title="stored benchmark",  n="1,444 pairs", auroc=0.871, ours=False,
         writer="confounded", prompt="confounded",
         pill=(BAD_BG, "#fecdd3", "#be123c")),
    dict(key="samegen", title="same-generator",    n="623 pairs",   auroc=0.751, ours=True,
         writer="controlled", prompt="confounded",
         pill=("#eff6ff", "#bfdbfe", "#1d4ed8")),
    dict(key="matched", title="prompt-matched",    n="586 pairs",   auroc=0.642, ours=True,
         writer="controlled", prompt="controlled",
         pill=(OK_BG, "#bbf7d0", "#15803d")),
]

BADGE = {"confounded": (BAD_BG, BAD_TX), "controlled": (OK_BG, OK_TX), "target": (TGT_BG, TGT_TX)}


def f3dp(x):
    """Three decimals, rounding half up (format() rounds 0.7715 to 0.771; the paper prints 0.772)."""
    return f"{math.floor(x * 1000 + 0.5) / 1000:.3f}"


def style(ax, base=8):
    """Hairline axes and a faint x grid."""
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(axis="x", colors=INK2, labelsize=base, length=3, width=0.7)
    ax.tick_params(axis="y", colors=INK2, labelsize=base, length=0)
    ax.grid(axis="x", color=GRID, lw=0.5, zorder=0)
    ax.set_axisbelow(True)


def save(fig, name):
    fig.savefig(f"{OUT}/{name}", metadata=PDF_METADATA)
    plt.close(fig)


# F4: how a stored pair is built, and how we rebuild it. One panel per construction; each row is
# a property of the pair and whether the two classes differ in it.

def _measure(ax, t):
    ax.figure.canvas.draw()
    return t.get_window_extent().transformed(ax.transData.inverted())


def _badge(ax, x_right, y, text, bg, tx, fs=6.0):
    """Pill badge, right-aligned to x_right. Text first, box measured to it, so it cannot crop."""
    t = ax.text(0, y, text, ha="center", va="center", fontsize=fs, color=tx, zorder=6)
    bb = _measure(ax, t)
    padx, pady = 1.5, 1.7
    t.set_x(x_right - padx - bb.width / 2)
    bb = _measure(ax, t)
    ax.add_patch(FancyBboxPatch((bb.x0 - padx, bb.y0 - pady), bb.width + 2 * padx,
                                bb.height + 2 * pady,
                                boxstyle="round,pad=0,rounding_size=1.4",
                                fc=bg, ec="none", zorder=5))


def _card(ax, x, y, w, h, title, bg, ec, tc, fs=7.5, lw=0.9, r=1.0):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                                fc=bg, ec=ec, lw=lw, zorder=3))
    ax.text(x + w / 2, y + h / 2, title, ha="center", va="center", fontsize=fs,
            color=tc, weight="bold", zorder=4)


def fig4_constructions():
    # Layout constants are in axis units (0-100) of a 2.45in-tall canvas; one y-unit is 1.764pt.
    # Changing figsize means re-deriving them, because type does not scale with the canvas.
    fig, ax = plt.subplots(figsize=(W_F4, 2.45))
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")
    fig.subplots_adjust(left=0.002, right=0.998, top=0.998, bottom=0.002)

    PW = (98.0 - 2 * 2.2) / 3
    XS = [1.0 + i * (PW + 2.2) for i in range(3)]
    Y_PANEL, H_PANEL = 2.0, 93.0
    Y_HEAD, Y_N = 95.0, 87.8
    Y_PROB, H_PROB = 73.0, 10.8
    Y_CARD, H_CARD = 55.5, 12.5
    Y_RULE = 52.0
    ROW_Y, ROW_H = (40.5, 30.3, 20.1), 8.5
    Y_PILL, H_PILL = 3.4, 13.6

    for col, x in zip(CONSTRUCTIONS, XS):
        cx = x + PW / 2
        lx, rx = x + PW * 0.26, x + PW * 0.74      # the honest and attack half-columns

        ax.add_patch(FancyBboxPatch((x, Y_PANEL), PW, H_PANEL,
                                    boxstyle="round,pad=0,rounding_size=1.6",
                                    fc=TINT if col["ours"] else PANEL_BG, ec=PANEL_EC,
                                    lw=1.0, zorder=1))

        # header pill, sitting on the top border
        t = ax.text(cx, Y_HEAD, col["title"], ha="center", va="center", fontsize=8.5,
                    color=INK, weight="bold", zorder=6)
        bb = _measure(ax, t)
        ax.add_patch(FancyBboxPatch((bb.x0 - 3.0, bb.y0 - 2.2), bb.width + 6.0, bb.height + 4.4,
                                    boxstyle="round,pad=0,rounding_size=2.2",
                                    fc="#ffffff", ec="#9ca3af", lw=1.0, zorder=5))
        ax.text(cx, Y_N, col["n"], ha="center", va="center", fontsize=6.5, color=MUTED, zorder=4)

        # the shared problem, as a stacked deck
        pw = PW * 0.62
        for dx, fc, ec in ((1.1, "#e5e7eb", "#cbd5e1"), (0.55, "#f3f4f6", "#cbd5e1")):
            ax.add_patch(FancyBboxPatch((cx - pw / 2 + dx, Y_PROB - dx), pw, H_PROB,
                                        boxstyle="round,pad=0,rounding_size=0.9",
                                        fc=fc, ec=ec, lw=0.7, zorder=2))
        _card(ax, cx - pw / 2, Y_PROB, pw, H_PROB, "problem $i$", "#ffffff", "#9ca3af", INK,
              fs=7.5, lw=1.0, r=0.9)

        for tx in (lx, rx):
            ax.add_patch(FancyArrowPatch((cx + (tx - cx) * 0.22, Y_PROB - 0.4),
                                         (tx, Y_CARD + H_CARD + 0.6),
                                         arrowstyle="-|>", mutation_scale=6, color=MUTED,
                                         lw=0.8, zorder=2, shrinkA=0, shrinkB=0))

        cw = PW * 0.40
        _card(ax, lx - cw / 2, Y_CARD, cw, H_CARD, "honest", OK_BG, OK_EC, OK_TX)
        _card(ax, rx - cw / 2, Y_CARD, cw, H_CARD, "attack", BAD_BG, BAD_EC, BAD_TX)
        ax.plot([x + 1.6, x + PW - 1.6], [Y_RULE, Y_RULE], color=GRID, lw=0.8, zorder=2)

        rows = (("writer", col["writer"]), ("prompt", col["prompt"]), ("backdoor", "target"))
        for ry, (name, status) in zip(ROW_Y, rows):
            ax.add_patch(FancyBboxPatch((x + 1.6, ry), PW - 3.2, ROW_H,
                                        boxstyle="round,pad=0,rounding_size=0.7",
                                        fc="#ffffff", ec="#e5e7eb", lw=0.8, zorder=2))
            yc = ry + ROW_H / 2
            ax.text(x + 3.0, yc, name, ha="left", va="center", fontsize=6.8,
                    color=INK, weight="bold", zorder=4)
            _badge(ax, x + PW - 3.0, yc, status, *BADGE[status])

        pbg, pec, ptc = col["pill"]
        ax.add_patch(FancyBboxPatch((x + 1.6, Y_PILL), PW - 3.2, H_PILL,
                                    boxstyle="round,pad=0,rounding_size=1.1",
                                    fc=pbg, ec=pec, lw=1.0, zorder=2))
        ax.text(cx, Y_PILL + 9.4, "AUROC", ha="center", va="center", fontsize=6.0,
                color=MUTED, zorder=3)
        ax.text(cx, Y_PILL + 4.4, f"{col['auroc']:.3f}", ha="center", va="center", fontsize=10.0,
                color=ptc, weight="bold", zorder=3)

    save(fig, "f4-constructions.pdf")
    conf = [sum(1 for k in ("writer", "prompt") if c[k] == "confounded") for c in CONSTRUCTIONS]
    print(f"F4: {' / '.join(map(str, conf))} confounded rows left to right; AUROC ladder "
          + " / ".join(f"{c['auroc']:.3f}" for c in CONSTRUCTIONS))


# F3: the 24 monitors ranked on the filtered split against our two floors, with their bootstrap
# CIs and permutation nulls.

def fig3_monitors():
    aurocs = sorted(m["test_auroc"] for m in json.load(open("monitor-summary.json")))
    n = len(aurocs)

    fig, ax = plt.subplots(figsize=(W_F3, 2.50))
    style(ax, base=7.0)

    # Rules and spans stop at the top of the data so they do not run through the legend.
    top = n + 0.8
    for (a, b), c in ((NOCODE_CI, ORANGE), (TFIDF_CI, BLUE)):
        ax.fill_betweenx([-0.4, top], a, b, color=c, alpha=0.10, lw=0, zorder=1)
    ax.plot([NOCODE_FLOOR] * 2, [-0.4, top], color=ORANGE, lw=1.4, zorder=3,
            label=f"reads no code  {f3dp(NOCODE_FLOOR)} $\\pm$ {NOCODE_SD:.3f}")
    ax.plot([TFIDF_FLOOR] * 2, [-0.4, top], color=BLUE, lw=1.4, zorder=3,
            label=f"bag-of-words  {f3dp(TFIDF_FLOOR)}")
    for v in (TFIDF_NULL, NOCODE_NULL):
        ax.plot([v] * 2, [-0.4, top], color=MUTED, lw=0.7, ls=(0, (1, 2)), zorder=2)
    ax.plot([], [], color=MUTED, lw=0.7, ls=(0, (1, 2)),
            label=f"permutation nulls  {TFIDF_NULL:.3f}, {NOCODE_NULL:.3f}")
    ax.plot([0.5] * 2, [-0.4, top], color=MUTED, lw=0.8, ls=(0, (3, 3)), zorder=2,
            label="chance  0.500")

    ax.scatter(aurocs, range(1, n + 1), s=15, facecolor=INK2, edgecolor="white",
               linewidth=0.6, zorder=4, label=f"{n} open-weight monitors")

    ax.set_yticks([1, 12, n]); ax.set_yticklabels(["1", "12", str(n)])
    ax.set_ylim(-0.4, n + 6.4)          # headroom for the key, above where the rules stop
    ax.set_xlim(0.40, 0.98)
    ax.set_xticks([0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
    ax.set_xlabel("AUROC on the 1,375-item test split", fontsize=8.0, color=INK)
    ax.set_ylabel("monitor rank (sorted)", fontsize=8.0, color=INK)
    leg = ax.legend(loc="upper left", fontsize=6.2, frameon=False, handlelength=1.5,
                    handletextpad=0.5, labelspacing=0.35, borderaxespad=0.15)
    for t in leg.get_texts():
        t.set_color(INK)
    fig.tight_layout(pad=0.35)
    save(fig, "f3-monitors-vs-floors.pdf")
    print(f"F3: {n} monitors, median {statistics.median(aurocs):.4f}, max {aurocs[-1]:.3f}; "
          f"below bag-of-words {sum(a < TFIDF_FLOOR for a in aurocs)}/{n}, "
          f"below no-code CV {sum(a < NOCODE_FLOOR for a in aurocs)}/{n}, "
          f"below no-code held-out {sum(a < NOCODE_HELDOUT for a in aurocs)}/{n}")


# F2: the structural floor in the five same-generator agentic settings. A thin connector runs from
# each permutation null to the measured value.

def fig2_corpora():
    rows = SCAN[::-1]
    names = [f"{r[0]}\n({r[3]} tasks)" for r in rows]
    vals, nulls = [r[1] for r in rows], [r[2] for r in rows]
    y = list(range(len(rows)))

    fig, ax = plt.subplots(figsize=(W_F2, 2.60))
    style(ax, base=8.0)
    ax.axvline(0.5, color=MUTED, lw=0.8, ls=(0, (3, 3)), zorder=2)
    ax.text(0.503, -0.62, "chance", ha="left", va="center", fontsize=7.0, color=MUTED)

    for i, (v, nv) in enumerate(zip(vals, nulls)):
        ax.plot([nv, v], [i, i], color=CONNECT, lw=1.1, zorder=3, solid_capstyle="round")
    ax.scatter(nulls, y, marker="d", s=26, facecolor=ORANGE, edgecolor="white", linewidth=0.7,
               zorder=5, label="permutation null")
    ax.scatter(vals, y, s=30, facecolor=BLUE, edgecolor="white", linewidth=0.7, zorder=6,
               label="within-task, character count only")
    for i, v in enumerate(vals):
        ax.text(v + 0.010, i, f"{v:.3f}", va="center", fontsize=8.0, color=INK)

    ax.set_yticks(y); ax.set_yticklabels(names, fontsize=8.0, color=INK, linespacing=1.3)
    ax.set_ylim(-0.9, len(rows) - 0.35)
    ax.set_xlim(0.44, 0.90)
    ax.set_xlabel("AUROC", fontsize=8.5, color=INK)
    leg = ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, fontsize=8.0,
                    frameon=False, handletextpad=0.35, columnspacing=1.2)
    for t in leg.get_texts():
        t.set_color(INK)
    fig.tight_layout(pad=0.35)
    save(fig, "f2-corpus-floors.pdf")
    print("F2: 5 settings, bash 0.504 (247 tasks) to agentdojo 0.802 (16 tasks); "
          "nulls 0.480-0.512, three of five below chance")


# F1: protocol x baseline, emitted as a LaTeX table that main.tex \inputs.
# Columns: protocol, baseline, metric, value, preprocessing, against. Preprocessing says whether
# comments were stripped before the baseline read the code ("stripped" / "kept"), or whether the
# baseline reads no code at all. Pairwise accuracies get three decimals (one pair is 1/2,641);
# AUROCs get four.
F1_ROWS = [
    ("Koran's exact split", "TF-IDF word 1--2gram", "AUROC", "0.8063", "stripped",
     "above 20 of 24"),
    ("\\quad same", "TF-IDF word 1--2gram", "AUROC", "0.8914", "kept", "above 22 of 24"),
    ("\\quad same, reads no code", "difficulty $+$ \\#tests $+$ $|q|$", "AUROC",
     "0.7715 $\\pm$ 0.0389", "no code", "above 20 of 24"),
    ("\\quad same, held-out slice", "difficulty $+$ \\#tests $+$ $|q|$", "AUROC",
     "0.7163", "no code", "above 18 of 24"),
    ("\\quad same", "code length only", "AUROC", "0.4726", "stripped", "chance"),
    ("\\quad same", "\\#-count detector", "AUROC", "0.4983", "stripped", "chance"),
    ("\\quad same", "\\#-count detector", "AUROC", "0.6957", "kept", "---"),
    ("Raw artifact, problem level", "all metadata", "AUROC", "0.8917", "no code", "---"),
    ("\\quad same", "difficulty only", "AUROC", "0.6823", "no code", "---"),
    ("\\quad same", "\\texttt{solution\\_passes\\_tests}", "AUROC", "0.7881", "no code", "---"),
    ("Matched pairs (P3)", "all metadata", "AUROC", "0.5000", "no code", "by construction"),
    # Matched protocol: mean over five problem-disjoint splits. Comments-kept rows are for contrast.
    ("DSPy matched pairs", "TF-IDF word 1--2gram", "pairwise", "0.897", "stripped",
     "monitor 0.69--0.81"),
    ("\\quad working backdoors only", "TF-IDF word 1--2gram", "pairwise", "0.935", "stripped",
     "---"),
    ("\\quad \\textbf{inert} backdoors only", "TF-IDF word 1--2gram", "pairwise", "0.879",
     "stripped", "not sabotage"),
    ("\\quad transfer, cross-generator", "TF-IDF word 1--2gram",
     "pairwise", "0.969", "stripped", "---"),
    ("\\quad all pairs, comments kept", "TF-IDF word 1--2gram", "pairwise", "0.962", "kept", "---"),
    ("\\quad working, comments kept", "TF-IDF word 1--2gram", "pairwise", "0.979", "kept", "---"),
    ("\\quad inert, comments kept", "TF-IDF word 1--2gram", "pairwise", "0.955", "kept", "---"),
    ("\\quad transfer, comments kept", "TF-IDF word 1--2gram", "pairwise", "0.994", "kept", "---"),
    ("\\quad same, raw artifact", "code length only", "pairwise", "0.826", "kept", "---"),
]


def fig1_table():
    """Write F1 as a LaTeX table that fits the 5.5in text block.

    Rows are grouped under AUROC / pairwise subheadings instead of a metric column; the text
    columns are p{} so long cells wrap. Needs \\usepackage{array} for >{\\raggedright}.
    """
    auroc = [r for r in F1_ROWS if r[2] == "AUROC"]
    pairw = [r for r in F1_ROWS if r[2] != "AUROC"]

    def body(rows):
        # drop the metric cell (index 2); it is carried by the group heading now
        return [" & ".join((r[0], r[1], r[3], r[4], r[5])) + " \\\\" for r in rows]

    # Widths are tuned to the 5.5in block. Column 2 must fit \texttt{solution_passes_tests},
    # which cannot break, so do not narrow it.
    col = ("@{}"
           ">{\\raggedright\\arraybackslash}p{0.255\\linewidth}"
           ">{\\raggedright\\arraybackslash}p{0.225\\linewidth}"
           "r"
           ">{\\raggedright\\arraybackslash}p{0.090\\linewidth}"
           ">{\\raggedright\\arraybackslash}p{0.170\\linewidth}"
           "@{}")

    lines = [
        "% F1 - generated by experiments/apps/figures.py, do not hand-edit",
        "\\begin{table}[h]\\centering\\footnotesize",
        "\\setlength{\\tabcolsep}{4pt}",
        "\\caption{What the field's preprocessing leaves behind. Every row is measured under the "
        "protocol named in column one; rows are not comparable across protocols. "
        "\\emph{Prep.} says whether comments were stripped before the baseline read the code; "
        "\\emph{no code} means the baseline never reads the program. The comments-kept rows are "
        "inflated by the comment channel and are given for contrast, not as results. The matched "
        "rows are problem-disjoint and scored against the DSPy tutorial monitor; the transfer "
        "row runs Control Tax to the GPT-4-era set. "
        "Pairwise accuracies are given to three decimals, their resolution over the pair count.}",
        "\\label{tab:protocol-baseline}",
        "\\begin{tabular}{" + col + "}",
        "\\toprule",
        "Protocol & Baseline & Value & Prep. & Against \\\\",
        "\\midrule",
        "\\multicolumn{5}{@{}l}{\\emph{AUROC}} \\\\",
    ]
    lines += body(auroc)
    lines += ["\\addlinespace",
              "\\multicolumn{5}{@{}l}{\\emph{Pairwise accuracy}} \\\\"]
    lines += body(pairw)
    lines += ["\\bottomrule", "\\end{tabular}", "\\end{table}"]
    with open(f"{OUT}/f1-protocol-baseline.tex", "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"F1: {len(F1_ROWS)} rows ({len(auroc)} AUROC, {len(pairw)} pairwise), "
          f"5 columns, sized to fit a 5.5in text block")


# check(): assert every plotted value against main.tex's \newcommand macros.
PAPER_TEX = "../../paper/main.tex"


def _macros(path=PAPER_TEX):
    import re
    out = {}
    for name, val in re.findall(r"\\newcommand\{\\(\w+)\}\{([^{}]*)\}", open(path).read()):
        try:
            out[name] = float(val)
        except ValueError:
            pass
    return out


def check():
    m = _macros()
    if not m:
        raise SystemExit(f"CHECK: no macros parsed from {PAPER_TEX}")
    bad = []

    def eq(macro, got, dp=None):
        # Round half up, as the paper does.
        if macro not in m:
            bad.append(f"{macro}: absent from main.tex"); return
        want = m[macro]
        got_r = math.floor(got * 10 ** dp + 0.5) / 10 ** dp if dp else got
        if abs(want - got_r) > 5e-4:
            bad.append(f"{macro}: main.tex {want} vs figures.py {got_r}")

    # F4's ladder. None of the three is the Koran-split floor.
    eq("baselineB", CONSTRUCTIONS[0]["auroc"])
    eq("sameGenS", CONSTRUCTIONS[1]["auroc"], 3)
    eq("matchedS", CONSTRUCTIONS[2]["auroc"], 3)
    if abs(CONSTRUCTIONS[0]["auroc"] - TFIDF_FLOOR) < 5e-3:
        bad.append("F4 panel 1 is the Koran floor; main.tex's caption says it is not")

    # F3's two floors, their intervals and their nulls.
    eq("tfidfKoran", TFIDF_FLOOR, 3); eq("tfidfKoranLo", TFIDF_CI[0]); eq("tfidfKoranHi", TFIDF_CI[1])
    eq("tfidfKoranNull", TFIDF_NULL)
    eq("nocodeCV", NOCODE_FLOOR, 3); eq("nocodeCVsd", NOCODE_SD, 3)
    eq("nocodeCVLo", NOCODE_CI[0]); eq("nocodeCVHi", NOCODE_CI[1]); eq("nocodeCVNull", NOCODE_NULL)
    eq("nocodeHeldout", NOCODE_HELDOUT, 3)

    # F2's two named settings.
    scan = {r[0]: r[1] for r in SCAN}
    eq("bashFloor", scan["bash"], 3); eq("agentdojoFloor", scan["agentdojo"], 3)

    # F3's monitor count and the two summary values the caption quotes.
    if os.path.exists("monitor-summary.json"):
        a = sorted(x["test_auroc"] for x in json.load(open("monitor-summary.json")))
        eq("monN", float(len(a))); eq("monMedian", statistics.median(a), 3)
        eq("monMax", a[-1], 3)

    if bad:
        raise SystemExit("CHECK FAILED against main.tex:\n  " + "\n  ".join(bad))
    print(f"CHECK: {len(m)} macros read from main.tex; every figure value agrees")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    check()
    fig1_table()
    fig2_corpora()
    fig3_monitors()
    fig4_constructions()
    print(f"\nwrote to {os.path.abspath(OUT)}")
