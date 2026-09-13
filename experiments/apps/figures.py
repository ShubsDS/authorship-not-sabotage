"""The paper's figures. `python figures.py` writes into ../../paper/fig/.

F1  protocol x baseline    -> LaTeX booktabs table (it is >7 rows of labelled values, which is a
                              table, not a chart)
F2  per-corpus floors      -> horizontal bars with the permutation null marked on every bar
F3  monitors vs our floors -> dot plot of 24 monitors against the two floors
F4  the three constructions -> the confound and the control, as a diagram
F5  rho forest             -> every arm's retained signal against the bands

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
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch  # noqa: E402

# The figures used to render in matplotlib's default sans while the paper sets in Times (ptm).
# That mismatch, not the data, was what made them read as pasted in. Nimbus Roman is the URW
# clone of Times and is metrically identical to ptm; it ships with TeX Live and ghostscript.
# fonttype 42 embeds TrueType rather than Type 3, which some camera-ready checkers reject.
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Nimbus Roman", "Times New Roman", "Times", "STIXGeneral", "DejaVu Serif"],
    "mathtext.fontset": "stix",
    "pdf.fonttype": 42,
})

OUT = "../../paper/fig"

# Without this, matplotlib stamps /CreationDate into the PDF and every rebuild differs from the
# last by exactly those 8 bytes - identical plots that git reports as changed, and a reproducibility
# claim that cannot be checked by hash. Suppressing the timestamp makes the figures bit-reproducible.
PDF_METADATA = {"CreationDate": None}
BLUE, ORANGE = "#2a78d6", "#eb6834"
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#8c8b86"
GRID = "#e3e2dd"
CONNECT = "#d3d2cc"   # dumbbell connector: visible against the surface, lighter than any mark

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


def style(ax, base=8):
    """Hairline chrome. The grid is one shade off the surface so the two reference lines and
    the marks are the only things with weight; y carries rank, not a scale, so it gets no
    spine and no tick marks."""
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(axis="x", colors=INK2, labelsize=base, length=3, width=0.7)
    ax.tick_params(axis="y", colors=INK2, labelsize=base, length=0)
    ax.grid(axis="x", color=GRID, lw=0.5, zorder=0)
    ax.set_axisbelow(True)


def fig3_monitors():
    """24 monitors on Koran's exact split, against the two floors measured on that same split."""
    mon = json.load(open("monitor-summary.json"))
    aurocs = sorted(m["test_auroc"] for m in mon)
    n = len(aurocs)
    below_tfidf = sum(a < TFIDF_FLOOR for a in aurocs)
    below_nocode = sum(a < NOCODE_FLOOR for a in aurocs)

    fig, ax = plt.subplots(figsize=(5.5, 3.0))
    style(ax, base=11)
    # Three rules about the key, each of which was learned by getting it wrong:
    #
    # 1. It goes upper-left, frameless. The sorted dots run bottom-left to top-right, so that
    #    corner is dead space. As a boxed legend in the lower right it sat on both floor rules.
    # 2. Every vertical rule STOPS at the top of the data (y = top). Drawn full height with
    #    axvline they ran straight through the key text - the same strike-through the chance
    #    label had. Above y = top there is nothing but the key.
    # 3. The labels carry the name and the value only. With "(20 of 24 below)" appended the key
    #    ran past x = 0.77 and the orange rule crossed its own entry. Both counts are 20 of 24
    #    and they are in the caption and in the body.
    #
    # No +-sd band: that spread is across CV folds, not a CI on the mean, and drawn as a band it
    # visually swallows the bag-of-words floor 0.04 away. The sd goes in the key text instead.
    top = n + 0.9
    ax.plot([NOCODE_FLOOR] * 2, [-0.4, top], color=ORANGE, lw=1.5, zorder=3,
            label="reads no code  0.772 $\\pm$ 0.039")
    ax.plot([TFIDF_FLOOR] * 2, [-0.4, top], color=BLUE, lw=1.5, zorder=3,
            label=f"bag-of-words  {TFIDF_FLOOR:.3f}")

    # Chance is a threshold, so it stays dashed - but the label used to be centred ON the line,
    # which struck the word through. It now sits to the right of the line at the foot of the
    # plot, in the gap below the lowest monitor.
    ax.plot([0.5, 0.5], [-0.4, top], color=MUTED, lw=0.8, ls=(0, (3, 3)), zorder=2)
    ax.text(0.507, 0.1, "chance", ha="left", va="bottom", fontsize=9.5, color=MUTED)
    below_heldout = sum(a < NOCODE_HELDOUT for a in aurocs)

    ax.scatter(aurocs, range(1, n + 1), s=26, facecolor=INK2, edgecolor="white",
               linewidth=0.8, zorder=4)
    ax.set_yticks([])
    ax.set_ylim(-0.4, n + 4.6)          # headroom for the key, above where the rules stop
    ax.set_xlim(0.40, 0.98)
    ax.set_xlabel("AUROC on the 1,375-item test split", fontsize=11.5, color=INK)
    ax.set_ylabel(f"{n} open-weight monitors\n(sorted)", fontsize=11.5, color=INK)
    leg = ax.legend(loc="upper left", fontsize=10.5, frameon=False,
                    handlelength=1.6, handletextpad=0.6, labelspacing=0.45,
                    borderaxespad=0.2)
    for t in leg.get_texts():
        t.set_color(INK)
    fig.tight_layout(pad=0.4)
    fig.savefig(f"{OUT}/f3-monitors-vs-floors.pdf", metadata=PDF_METADATA)
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
    style(ax, base=9.5)
    # Same fix as F3: the label used to be centred on the dashed line and was struck through by
    # it. Here every row is crowded around 0.5, so the label goes below the last row instead.
    ax.axvline(0.5, color=MUTED, lw=0.8, ls=(0, (3, 3)), zorder=2)
    ax.text(0.505, -0.55, "chance", ha="left", va="center", fontsize=8.5, color=MUTED)

    # A thin connector, not a 2.5pt bar. At the old weight it read as a bar grown from the null,
    # which is the reading the dumbbell was chosen to avoid.
    for i, (v, nv) in enumerate(zip(vals, nulls)):
        ax.plot([nv, v], [i, i], color=CONNECT, lw=1.1, zorder=3, solid_capstyle="round")
    ax.scatter(nulls, y, s=30, facecolor=ORANGE, edgecolor="white", linewidth=0.8, zorder=5,
               label="permutation null")
    ax.scatter(vals, y, s=34, facecolor=BLUE, edgecolor="white", linewidth=0.8, zorder=6,
               label="within-task, character count only")
    for i, v in enumerate(vals):
        ax.text(v + 0.012, i, f"{v:.3f}", va="center", fontsize=9, color=INK)

    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=9.5, color=INK, linespacing=1.35)
    ax.set_ylim(-0.85, len(names) - 0.35)
    ax.set_xlim(0.44, 0.90)             # 0.87 clipped agentdojo's 0.802 label against the frame
    ax.set_xlabel("AUROC", fontsize=10, color=INK)
    leg = ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, fontsize=9.5,
                    frameon=False, handletextpad=0.4, columnspacing=1.4)
    for t in leg.get_texts():
        t.set_color(INK)
    fig.tight_layout(pad=0.4)
    fig.savefig(f"{OUT}/f2-corpus-floors.pdf", metadata=PDF_METADATA)
    plt.close(fig)
    print("F2: 5 settings; bash 0.504 (clean, 247 tasks) to agentdojo 0.802 (leaky, 16 tasks); "
          "nulls 0.480-0.512. shade and iac rest on 5 task groups each.")


# Columns: protocol, baseline, metric, value, preprocessing, against.
#
# Preprocessing is a column of its own (2026-09-11) because the paper's thesis is about the
# comment channel and the table must say, row by row, whether that channel was open:
#   "stripped"  comments removed before the baseline read the code (Koran/Jha protocol)
#   "kept"      comments present. The DSPy matched pairwise rows and the raw-artifact length
#               row were measured this way (matched.py / exact.py never call strip_comments;
#               notes/06 §0.3, §1.2) and the table says so instead of hiding it.
#   "no code"   the baseline never reads the program, so preprocessing is moot.
#
# Pairwise accuracies are THREE decimals (fig/CAPTIONS.md): resolution over 2,641 pairs is
# 1/2,641 = 0.00038, so a fourth decimal is a single pair and moved by one pair between
# machines (REPRODUCED.md). AUROCs keep four.
F1_ROWS = [
    ("Koran's exact split", "TF-IDF word 1--2gram", "AUROC", "0.8063", "stripped",
     "above 20 of 24"),
    ("\\quad same", "TF-IDF word 1--2gram", "AUROC", "0.8914", "kept", "above 22 of 24"),
    # 0.7715 is the 5x5 CV value and it clears 20, not 18. The "above 18" count belongs to
    # the 0.7163 held-out slice (see NOCODE_HELDOUT above and fig/CAPTIONS.md). Pairing them
    # is R18's companion error committed against ourselves; it shipped in this table once.
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
    # RESULTS.md §6 (2026-09-11): the matched protocol re-measured with comments stripped from
    # both classes, mean over five problem-disjoint splits. The paper reports the stripped rows;
    # the comments-kept rows are the earlier values, kept here labelled as what they are.
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
    # This row used to read "0.8255 | and 0.4726 once filtered": a pairwise accuracy with an
    # AUROC from another split in its Against cell, under the pairwise heading. The 0.4726
    # contrast lives in the AUROC block above, where it belongs; this row stands alone.
    ("\\quad same, raw artifact", "code length only", "pairwise", "0.826", "kept", "---"),
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
        return [" & ".join((r[0], r[1], r[3], r[4], r[5])) + " \\\\" for r in rows]

    # Widths tuned against the actual 5.5in block. Five columns now (preprocessing added
    # 2026-09-11); the p{} widths still sum to 0.740\linewidth as they did with four, and
    # the extra column pair of \tabcolsep is what the tighter Against column pays for:
    #   col 1 no longer has to hold ", comments stripped" - that moved to the new column -
    #          so "Koran's exact split" fits at 0.255 with room; longer protocol names wrap;
    #   col 2 must hold \texttt{solution_passes_tests}, which is unbreakable and was
    #          7.7pt too wide at 0.205. Do not narrow it;
    #   col 4 (preprocessing) holds "stripped" / "kept" / "no code" on one line at 0.090;
    #   col 5 (against) wraps freely and takes the remaining slack.
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


# =====================================================================================
#  F4 and F5 are the BODY figures for the narrative rebuild: the confound and the control
#  as a diagram, and every arm's retained signal against the pre-registered bands.
#
#  Both are included at \linewidth, so - per pass 8's rule - their point sizes are given at
#  the size they render on the page. The paper's body is 10pt; nothing here is below 8pt.
#  Both set in the same serif as F2/F3 through the rcParams at the top of this file.
# =====================================================================================

def _pill(ax, x, y, text, *, fs, fc, ec, tc, padx=2.6, pady=2.1, weight="normal", lw=0.9):
    """Text first, then a rounded box measured to it, so the box can never crop the label."""
    t = ax.text(x, y, text, ha="center", va="center", fontsize=fs, color=tc,
                weight=weight, zorder=6, linespacing=1.3)
    ax.figure.canvas.draw()
    bb = t.get_window_extent().transformed(ax.transData.inverted())
    ax.add_patch(FancyBboxPatch((bb.x0 - padx, bb.y0 - pady),
                                bb.width + 2 * padx, bb.height + 2 * pady,
                                boxstyle="round,pad=0,rounding_size=0.8",
                                fc=fc, ec=ec, lw=lw, zorder=5))
    return bb.y0 - pady, bb.y1 + pady


def _arrow(ax, a, b, color=MUTED, lw=0.9):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=8, color=color,
                                 lw=lw, zorder=4, shrinkA=0, shrinkB=0))


def _chiprow(ax, xc, y, items, fs):
    """Centred row of chips. items = [(label, fill, textcolour)]. Two-pass, like _pill."""
    handles = [(ax.text(0, y, lab, ha="center", va="center", fontsize=fs, color=tc, zorder=7),
                fc) for lab, fc, tc in items]
    ax.figure.canvas.draw()
    padx, gap = 1.6, 1.6
    widths = [h.get_window_extent().transformed(ax.transData.inverted()).width + 2 * padx
              for h, _ in handles]
    x = xc - (sum(widths) + gap * (len(widths) - 1)) / 2
    for (h, fc), w in zip(handles, widths):
        h.set_x(x + w / 2)
        ax.figure.canvas.draw()
        bb = h.get_window_extent().transformed(ax.transData.inverted())
        ax.add_patch(FancyBboxPatch((x, bb.y0 - 1.3), w, bb.height + 2.6,
                                    boxstyle="round,pad=0,rounding_size=0.6",
                                    fc=fc, ec="none", zorder=6))
        x += w + gap


def fig4_constructions():
    """How a stored pair is built, and how we rebuild it: three constructions as a property grid.

    The encoding is the whole figure: each row is one property of the pair, a SPLIT row means the
    honest and attack sides differ in it, a MERGED bar means they are identical. Left to right the
    rows merge one at a time, and the separability bar under them falls. Only the backdoor row is
    still split in the third column, which is the construction this paper argues for.

    Deliberately NOT here: Haiku 4.5 and the strict rows (Table 2 carries every row), the fire
    shares, and the flow arrows the earlier version spent 60% of its ink on. The previous draft
    also labelled the panels A/B/C while printing $B$ = 0.871 inside panel A.

    TEXT BUDGET: every string on this canvas is a label, never a phrase. The row label and the
    cell form the phrase between them - "prompt" + "solve", not a cell reading "solve the
    problem" - and anything needing a clause goes in the caption. Cut here on 2026-09-13:
    "writes both" (the merged bar already says both), "of the baseline" twice, "the baseline",
    "one prompt for both classes", "written for APPS", "0.5," before "chance".
    """
    # 2.50in, not the 2.62 the tree version needed: the grid carries the same content in less
    # height, and the caption below it grew. Anything taller pushes the Discussion onto page 5.
    fig, ax = plt.subplots(figsize=(5.5, 2.50))
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")
    fig.subplots_adjust(left=0.004, right=0.996, top=0.996, bottom=0.004)

    NEUT, OTINT, BTINT = "#ffffff", "#fbdccd", "#cfe0f6"
    OT, BT = "#8a3b17", "#174a87"
    OURS_BG = "#f6f9fd"

    GUT = 11.0                                    # row-label gutter
    BLOCKS = [(13.0, 40.5), (43.0, 70.5), (73.0, 100.0)]
    SPLIT = 1.6                                   # gap between the honest and attack halves

    Y_BAND, Y_TITLE, Y_SUB = 96.5, 88.0, 79.0
    ROWS = (68.0, 55.5, 43.0)                     # writer, prompt, backdoor
    CELL_H = 11.0
    Y_BAR, Y_NUM, Y_RHO = 30.0, 18.0, 8.0

    # The tint behind columns two and three is the only thing that says which of these
    # constructions is ours. It is doing more work than any sentence in the old caption.
    ax.add_patch(FancyBboxPatch((BLOCKS[1][0] - 1.8, 3.0),
                                BLOCKS[2][1] - BLOCKS[1][0] + 3.6, 98.0 - 3.0,
                                boxstyle="round,pad=0,rounding_size=1.2",
                                fc=OURS_BG, ec="none", zorder=0))

    def cell(x0, x1, yc, text, *, fill, tc, ec, fs=7.0, weight="normal"):
        ax.add_patch(FancyBboxPatch((x0, yc - CELL_H / 2), x1 - x0, CELL_H,
                                    boxstyle="round,pad=0,rounding_size=0.9",
                                    fc=fill, ec=ec, lw=0.8, zorder=3))
        ax.text((x0 + x1) / 2, yc, text, ha="center", va="center", fontsize=fs,
                color=tc, zorder=4, linespacing=1.15, weight=weight)

    def split(bx, yc, left, right, fs=7.0):
        """The two classes differ in this property: two boxes, tinted as a difference."""
        x0, x1 = bx
        mid = (x0 + x1) / 2
        cell(x0, mid - SPLIT / 2, yc, left, fill=NEUT, tc=INK, ec=GRID, fs=fs)
        cell(mid + SPLIT / 2, x1, yc, right, fill=OTINT, tc=OT, ec="none", fs=fs)

    def merged(bx, yc, text, fs=7.0):
        """Held identical across the pair: one bar, and it says so in words."""
        cell(bx[0], bx[1], yc, text, fill=BTINT, tc=BT, ec="none", fs=fs)

    # --- headers ---------------------------------------------------------------------
    ax.text((BLOCKS[0][0] + BLOCKS[0][1]) / 2, Y_BAND, "as stored", ha="center", va="center",
            fontsize=7.5, color=MUTED, style="italic")
    ax.text((BLOCKS[1][0] + BLOCKS[2][1]) / 2, Y_BAND, "what we build", ha="center", va="center",
            fontsize=7.5, color=BT, style="italic")
    for bx, ttl in zip(BLOCKS, ("human vs model", "one model, two prompts",
                                "one model, one prompt")):
        ax.text((bx[0] + bx[1]) / 2, Y_TITLE, ttl, ha="center", va="center",
                fontsize=8.5, color=INK, weight="bold")
    for bx in BLOCKS:
        mid = (bx[0] + bx[1]) / 2
        ax.text((bx[0] + mid) / 2, Y_SUB, "honest", ha="center", va="center",
                fontsize=7.0, color=MUTED)
        ax.text((mid + bx[1]) / 2, Y_SUB, "attack", ha="center", va="center",
                fontsize=7.0, color=MUTED)

    # --- the three properties --------------------------------------------------------
    for y, lab in zip(ROWS, ("writer", "prompt", "backdoor")):
        ax.text(GUT - 1.5, y, lab, ha="right", va="center", fontsize=7.5, color=INK2)

    split(BLOCKS[0], ROWS[0], "human", "Claude 3.7")
    split(BLOCKS[0], ROWS[1], "none", "attack")
    for bx in BLOCKS[1:]:
        merged(bx, ROWS[0], "Claude Sonnet 5")
    split(BLOCKS[1], ROWS[1], "solve", "attack")
    merged(BLOCKS[2], ROWS[1], "same prompt")
    for bx in BLOCKS:
        split(bx, ROWS[2], "none", "planted")

    # --- separability, on one scale, drawn rather than only printed --------------------
    ax.text(GUT - 1.5, Y_BAR, "AUROC", ha="right", va="center", fontsize=7.5, color=INK2)
    for bx, v, hue in zip(BLOCKS, (0.871, 0.751, 0.642), (ORANGE, BLUE, BLUE)):
        x0, x1 = bx
        ax.add_patch(FancyBboxPatch((x0, Y_BAR - 2.6), x1 - x0, 5.2,
                                    boxstyle="round,pad=0,rounding_size=0.6",
                                    fc="white", ec=GRID, lw=0.8, zorder=3))
        ax.add_patch(FancyBboxPatch((x0, Y_BAR - 2.6), (x1 - x0) * (v - 0.5) / 0.5, 5.2,
                                    boxstyle="round,pad=0,rounding_size=0.6",
                                    fc=hue, ec="none", zorder=4))
    # The scale is defined once, under the first bar, where the eye starts. Repeating it under
    # all three reads as three scales; putting 1.0 under the third reads as a value of the third.
    ax.text(BLOCKS[0][0], Y_BAR - 6.4, "chance", ha="left", va="center",
            fontsize=6.5, color=MUTED)
    ax.text(BLOCKS[0][1], Y_BAR - 6.4, "1.0", ha="right", va="center",
            fontsize=6.5, color=MUTED)

    # --- the numbers ------------------------------------------------------------------
    ax.text((BLOCKS[0][0] + BLOCKS[0][1]) / 2, Y_NUM, "$B$ = 0.871", ha="center", va="center",
            fontsize=9.5, color=INK, weight="bold")

    for bx, s, r in ((BLOCKS[1], "0.751", "0.687"), (BLOCKS[2], "0.642", "0.394")):
        xc = (bx[0] + bx[1]) / 2
        ax.text(xc, Y_NUM, f"$S$ = {s}", ha="center", va="center",
                fontsize=9.5, color=INK, weight="bold")
        ax.text(xc, Y_RHO, f"$\\rho$ = {r}", ha="center", va="center",
                fontsize=7.0, color=MUTED)

    fig.savefig(f"{OUT}/f4-constructions.pdf", metadata=PDF_METADATA)
    plt.close(fig)
    print("F4: property grid, 3 constructions; rows merge left to right, AUROC 0.871 -> 0.642")


# Every row: label, rho, lo, hi, colour. `None` bounds mean the ledger quotes no joint interval.
RHO_ROWS = [
    ("head", "Bag-of-words classifier",          None,  None,  None,  None),
    ("row",  "Sonnet 5  ·  headline",       0.687, 0.625, 0.755, BLUE),
    ("row",  "prompt-matched",                   0.394, 0.326, 0.454, BLUE),
    ("row",  "strict (also fires)",              0.921, 0.662, 1.089, BLUE),
    ("row",  "strict, prompt-matched",           0.697, 0.494, 0.856, BLUE),
    ("row",  "Haiku 4.5  ·  headline",      0.095, 0.044, 0.150, BLUE),
    ("row",  "prompt-matched",                   0.113, None,  None,  BLUE),
    ("head", "LLM monitor, same pairs",          None,  None,  None,  None),
    ("row",  "wrote both  ·  headline",     0.145, 0.111, 0.182, ORANGE),
    ("row",  "strict",                           0.717, 0.601, 0.832, ORANGE),
    ("row",  "wrote neither  ·  headline †", 0.151, 0.063, 0.242, ORANGE),
    ("head", "The obvious fix",                  None,  None,  None,  None),
    ("row",  "honest half regenerated",          1.234, None,  None,  INK2),
]


def fig5_rho():
    """Every arm's retained signal against the bands that were fixed before any arm ran.

    A forest plot, because the quantity is one ratio measured eleven ways and the reader's
    question is which band each one lands in. The null sits to the RIGHT of rho = 1, which is
    the whole point of publishing it.
    """
    fig, ax = plt.subplots(figsize=(5.5, 3.30))
    fig.subplots_adjust(left=0.300, right=0.792, top=0.900, bottom=0.140)

    XMAX, n = 1.30, len(RHO_ROWS)
    ax.set_xlim(0, XMAX); ax.set_ylim(-0.7, n - 0.35)

    ax.axvspan(0, 0.33, color="#efedE8".lower(), zorder=0)
    ax.axvspan(0.33, 0.72, color="#f7f5f2", zorder=0)
    ax.axvspan(0.72, XMAX, color="#fcfbf9", zorder=0)
    for b in (0.33, 0.72):
        ax.axvline(b, color=GRID, lw=0.8, zorder=1)
    ax.axvline(1.0, color=MUTED, lw=0.8, ls=(0, (3, 3)), zorder=2)

    top = n - 0.46
    for x, lab in ((0.165, "collapse"), (0.525, "partial"), (0.855, "content")):
        ax.text(x, top, lab, ha="center", va="bottom", fontsize=8.5, color=INK2, style="italic")
    ax.text(1.015, top, r"$\rho$ = 1", ha="left", va="bottom", fontsize=8.0, color=MUTED)
    ax.text(1.022, top, r"$\rho$  (95% CI)", transform=ax.get_yaxis_transform(),
            ha="left", va="bottom", fontsize=8.5, color=INK, weight="bold")

    ticks, labels = [], []
    for i, (kind, label, v, lo, hi, colour) in enumerate(RHO_ROWS):
        y = n - 1 - i
        if kind == "head":
            ax.text(-0.014, y, label, transform=ax.get_yaxis_transform(), ha="right",
                    va="center", fontsize=8.8, color=INK, weight="bold")
            continue
        ticks.append(y); labels.append(label)
        if lo is not None:
            ax.plot([lo, hi], [y, y], color=colour, lw=1.6, alpha=0.40, zorder=4,
                    solid_capstyle="butt")
            for e in (lo, hi):
                ax.plot([e, e], [y - 0.17, y + 0.17], color=colour, lw=1.0, alpha=0.55, zorder=4)
        ax.scatter([v], [y], s=30, facecolor=colour, edgecolor="white", lw=0.8, zorder=6)
        txt = f"{v:.3f}" if lo is None else f"{v:.3f}  ({lo:.3f}–{hi:.3f})"
        ax.text(1.022, y, txt, transform=ax.get_yaxis_transform(), ha="left", va="center",
                fontsize=8.5, color=INK2)

    ax.set_yticks(ticks)
    ax.set_yticklabels(labels, fontsize=8.5, color=INK2)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(axis="x", colors=INK2, labelsize=9.0, length=3, width=0.7)
    ax.tick_params(axis="y", length=0)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0, 1.25])
    ax.set_xlabel(r"$\rho$  =  share of above-chance separability that survives",
                  fontsize=9.5, color=INK, labelpad=3)

    fig.savefig(f"{OUT}/f5-rho-forest.pdf", metadata=PDF_METADATA)
    plt.close(fig)
    print("F5: 11 rows, 3 bands; null at 1.234 sits right of rho = 1")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    fig1_table()
    fig2_corpora()
    fig3_monitors()
    fig4_constructions()
    fig5_rho()
    print(f"\nwrote to {os.path.abspath(OUT)}")
