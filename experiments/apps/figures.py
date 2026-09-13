"""The paper's figures. `python figures.py` writes into ../../paper/fig/.

F1  protocol x baseline     -> LaTeX booktabs table (it is >7 rows of labelled values, which is a
                               table, not a chart)
F2  per-corpus floors       -> f2-corpus-floors.pdf   (included at 0.86\\linewidth)
F3  monitors vs our floors  -> f3-monitors-vs-floors.pdf (included at 0.64\\linewidth)
F4  the three constructions -> f4-constructions.pdf   (included at \\linewidth)
F5  rho forest              -> f5-rho-forest.pdf      (NOT currently included in main.tex; the
                               paper carries these rows as Table 1. Built and tracked anyway.)

REBUILD, 2026-09-13. The card/panel/badge language, the shaded retention bands and the
null-to-value connector come from the dashboard-style draft this replaces. Three things about that
draft do not survive the port, and all three have to stay dead:

  Numbers. The draft's five permutation nulls, two rho intervals and F4's leading AUROC were not
  the measured ones. Every value below is a named constant with its ledger location beside it, and
  nothing is typed twice. See the CHECK block at the bottom, which re-asserts them at import.

  Type. The paper sets in Times (ptm). The draft set in DejaVu Sans, which is what made the old
  figures read as pasted in. Nimbus Roman is URW's Times clone and metrically identical to ptm;
  where it is missing (this Mac) Times New Roman is the same metrics again.

  Point size. Every figure is included at a FIXED fraction of the 5.5in text block, so figsize is
  that printed width and every fontsize below is the size it lands on the page. The draft was
  drawn at 11in wide, which would have delivered 4pt badges. Nothing here renders below 6pt.

Text inside a frame is a label, never a sentence: the draft's callout boxes ("Reaches 0.802 AUROC
from character count alone!", "20 of 24 monitors fall BELOW the No-Code floor") are claims, and
claims belong to the caption, which already makes both.
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

# Without this matplotlib stamps /CreationDate into the PDF and every rebuild differs from the last
# by exactly those 8 bytes - identical plots that git reports as changed, and a reproducibility
# claim no one can check by hash.
PDF_METADATA = {"CreationDate": None}

# The 5.5in NeurIPS text block, and the widths main.tex includes each figure at.
TEXT_W = 5.5
W_F2, W_F3, W_F4 = 0.86 * TEXT_W, 0.64 * TEXT_W, 1.00 * TEXT_W

# --- ink -----------------------------------------------------------------------------------
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8c8b86", "#e3e2dd"
BLUE, ORANGE = "#2a78d6", "#eb6834"
CONNECT = "#d3d2cc"

# Card and badge palette, ported from the draft and darkened where 6pt type sits on it.
OK_BG, OK_EC, OK_TX = "#f0fdf4", "#86efac", "#166534"      # controlled / honest
BAD_BG, BAD_EC, BAD_TX = "#fff1f2", "#fda4af", "#9f1239"   # confounded / attack
TGT_BG, TGT_TX = "#eef2ff", "#3730a3"                      # the target signal
TINT = "#f4f8fd"                                           # the two constructions we build
PANEL_BG, PANEL_EC = "#fafafa", "#d1d5db"

# =============================================================================================
#  MEASURED VALUES.  Every one carries where it came from. Verified on this machine 2026-09-04
#  (experiments/REPRODUCED.md); the Gate S rows re-read from RESULTS.md 2026-09-13.
# =============================================================================================

TFIDF_FLOOR = 0.8063                       # RESULTS.md 8.3; Koran paired train -> their 1,375 test
TFIDF_CI = (0.7704, 0.8409)                # bootstrap over problems
TFIDF_NULL = 0.5465                        # permutation null, 95th pct; p = 0.004975
NOCODE_FLOOR, NOCODE_SD = 0.7715, 0.0389   # 5x5 CV *within* the test split - a real caveat
NOCODE_CI = (0.7319, 0.8005)               # CI of the POOLED out-of-fold AUROC (0.7658), not of the
                                           # fold mean; RESULTS.md 8.3 says so explicitly
NOCODE_NULL = 0.5545
NOCODE_HELDOUT = 0.7163                    # single 413-item held-out slice; clears 18 of 24
# Never pair 0.7715 with "above 18": that count belongs to 0.7163. 0.7715 clears 20 of 24.
# Mixing them is exactly R18's companion error, and it reached the README before this was caught.

# scan/FINDINGS.md 2b, re-run by scan/matched.py 2026-09-04: all five within-task values reproduce
# exactly. Column 4 is the number of task groups the within-task AUROC is averaged over and it is
# NOT uniform - shade and iac rest on FIVE groups each, which the paper says out loud.
# The nulls are the measured ones: three of the five sit BELOW chance. The draft had all five above
# it (0.501/0.518/0.512/0.525/0.529), which is a set of numbers that appears nowhere in the ledger.
SCAN = [
    ("bash",       0.5044, 0.4896, 247),
    ("shade",      0.6022, 0.5079, 5),
    ("iac",        0.7041, 0.4841, 5),
    ("rogue_eval", 0.6158, 0.4801, 25),
    ("agentdojo",  0.8020, 0.5118, 16),
]

# F4's three AUROCs. main.tex's own caption warns that NONE of these is the 0.806 Koran floor - they
# are measured on the problems each construction realises, so they are a ladder, not a paired
# comparison. The draft labelled the first panel 0.806, which is the error the caption forbids.
#   0.871  \baselineB, n = \baselineBn 1,444   (apps/gate_s_baseline.json)
#   0.751  \sameGenS,  n = \sameGenN   623
#   0.642  \matchedS,  n = \matchedN   586
CONSTRUCTIONS = [
    dict(key="stored",  title="stored benchmark",  n="1,444 pairs", auroc=0.871, ours=False,
         writer=("human", "Sonnet 3.7"), prompt=("none", "attack"),
         pill=(BAD_BG, "#fecdd3", "#be123c")),
    dict(key="samegen", title="same-generator",    n="623 pairs",   auroc=0.751, ours=True,
         writer="Sonnet 5",              prompt=("solve", "attack"),
         pill=("#eff6ff", "#bfdbfe", "#1d4ed8")),
    dict(key="matched", title="prompt-matched",    n="586 pairs",   auroc=0.642, ours=True,
         writer="Sonnet 5",              prompt="same template",
         pill=(OK_BG, "#bbf7d0", "#15803d")),
]

# Every row: label, rho, lo, hi, colour. `None` bounds mean the ledger quotes no joint interval,
# and then no whisker is drawn. The draft invented one for 1.234 (1.150-1.318) and mis-set two
# more (0.113 -> 0.175 for 0.165; the edit bound -> 0.301-0.441 for 0.306-0.430).
RHO_ROWS = [
    ("head", "Bag-of-words classifier",       None,  None,  None,  None),
    ("row",  "headline",                      0.687, 0.625, 0.755, BLUE),   # main.tex \sameGenRho
    ("row",  "prompt-matched",                0.394, 0.326, 0.454, BLUE),   # \matchedRho
    ("row",  "strict (also fires)",           0.921, 0.662, 1.089, BLUE),   # \strictRho
    ("row",  "strict, prompt-matched",        0.697, 0.494, 0.856, BLUE),   # \matchedStrictRho
    ("row",  "Haiku 4.5, headline",           0.095, 0.044, 0.150, BLUE),   # \haikuRho
    ("row",  "Haiku 4.5, prompt-matched",     0.113, 0.055, 0.165, BLUE),   # RESULTS.md 15.6 (a)
    ("head", "LLM monitor, same pairs",       None,  None,  None,  None),
    ("row",  "Sonnet 5, wrote both",          0.145, 0.111, 0.182, ORANGE), # RESULTS.md 14, l.1764
    ("row",  "Sonnet 5, strict",              0.717, 0.601, 0.832, ORANGE), # l.1766
    ("row",  "Haiku 4.5, wrote neither",      0.151, 0.063, 0.242, ORANGE), # l.1765
    ("head", "Bounds",                        None,  None,  None,  None),
    ("row",  "edit arm (near-copies)",        0.371, 0.306, 0.430, MUTED),  # RESULTS.md 9.1 row 7
    ("row",  "honest half regenerated",       1.234, None,  None,  INK2),   # RESULTS.md 2; no CI
]

BANDS = (0.33, 0.72)   # pre-registered before any arm ran: collapse / partial / content


def f3dp(x):
    """Three decimals, half-UP. Python's format() is half-to-even, which prints the no-code
    floor's 0.7715 as 0.771 while the paper prints 0.772."""
    return f"{math.floor(x * 1000 + 0.5) / 1000:.3f}"


def style(ax, base=8):
    """Hairline chrome. The grid is one shade off the surface so the reference lines and the marks
    are the only things with weight."""
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(axis="x", colors=INK2, labelsize=base, length=3, width=0.7)
    ax.tick_params(axis="y", colors=INK2, labelsize=base, length=0)
    ax.grid(axis="x", color=GRID, lw=0.5, zorder=0)
    ax.set_axisbelow(True)


def save(fig, name):
    fig.savefig(f"{OUT}/{name}", metadata=PDF_METADATA)
    plt.close(fig)


# =============================================================================================
#  F4  -  how a stored pair is built, and how we rebuild it
# =============================================================================================
#
# Ported from the draft's three-panel card layout, with one structural change that the paper's
# caption depends on: a property the two classes SHARE is written once, centred across the pair;
# one they DIFFER in is written twice, once under each class. Count the merged rows and you have
# the paper: none, one, two. Cleveland & McGill put position on a common scale first and colour
# hue last, so the figure's one claim rides on position; the badge only names it.
#
# What the draft carried that is gone: the italic strap-lines under each header ("Standard
# Multi-Factor Confound", "Full Factor Isolation Control"), the per-card provenance captions, and
# "BoW: 0.806" on the first panel - a value main.tex:556 explicitly says is NOT one of these three.

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
    fig, ax = plt.subplots(figsize=(W_F4, 3.15))
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")
    fig.subplots_adjust(left=0.002, right=0.998, top=0.998, bottom=0.002)

    PW = (98.0 - 2 * 2.2) / 3
    XS = [1.0 + i * (PW + 2.2) for i in range(3)]
    Y_PANEL, H_PANEL = 2.5, 88.0
    Y_HEAD, Y_N = 90.5, 83.6
    Y_PROB, H_PROB = 72.8, 8.6
    Y_CARD, H_CARD = 55.2, 10.6
    Y_RULE = 52.6
    ROW_Y, ROW_H = (40.2, 28.2, 16.2), 11.4
    Y_PILL, H_PILL = 3.4, 10.2

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

        rows = [("writer", col["writer"]), ("prompt", col["prompt"]),
                ("backdoor", ("none", "planted"))]
        for ry, (name, val) in zip(ROW_Y, rows):
            ax.add_patch(FancyBboxPatch((x + 1.6, ry), PW - 3.2, ROW_H,
                                        boxstyle="round,pad=0,rounding_size=0.7",
                                        fc="#ffffff", ec="#e5e7eb", lw=0.8, zorder=2))
            ax.text(x + 3.0, ry + 7.9, name, ha="left", va="center", fontsize=6.8,
                    color=INK, weight="bold", zorder=4)
            if name == "backdoor":
                bg, tc, badge = TGT_BG, TGT_TX, "target"
            elif isinstance(val, tuple):
                bg, tc, badge = BAD_BG, BAD_TX, "confounded"
            else:
                bg, tc, badge = OK_BG, OK_TX, "controlled"
            _badge(ax, x + PW - 3.0, ry + 7.9, badge, bg, tc)
            if isinstance(val, tuple):          # differs: written twice, under each class
                for tx, s in ((lx, val[0]), (rx, val[1])):
                    ax.text(tx, ry + 2.9, s, ha="center", va="center", fontsize=7.0,
                            color=INK2, zorder=4)
            else:                               # held identical: written once, and tied
                ax.text(cx, ry + 3.4, val, ha="center", va="center", fontsize=7.0,
                        color=INK2, zorder=4)
                yt = ry + 1.4
                ax.plot([lx, rx], [yt, yt], color=BLUE, lw=0.8, zorder=4, solid_capstyle="butt")
                for e in (lx, rx):
                    ax.plot([e, e], [yt, yt + 1.1], color=BLUE, lw=0.8, zorder=4)

        pbg, pec, ptc = col["pill"]
        ax.add_patch(FancyBboxPatch((x + 1.6, Y_PILL), PW - 3.2, H_PILL,
                                    boxstyle="round,pad=0,rounding_size=1.1",
                                    fc=pbg, ec=pec, lw=1.0, zorder=2))
        ax.text(cx, Y_PILL + 7.2, "AUROC", ha="center", va="center", fontsize=6.0,
                color=MUTED, zorder=3)
        ax.text(cx, Y_PILL + 3.0, f"{col['auroc']:.3f}", ha="center", va="center", fontsize=10.0,
                color=ptc, weight="bold", zorder=3)

    save(fig, "f4-constructions.pdf")
    print("F4: 0 / 1 / 2 merged rows left to right; AUROC ladder "
          + " / ".join(f"{c['auroc']:.3f}" for c in CONSTRUCTIONS))


# =============================================================================================
#  F3  -  the 24 monitors against the two floors, on the split they are ranked on
# =============================================================================================
#
# The draft coloured each dot by whether it cleared the no-code floor. That is dropped: there are
# TWO floors 0.035 apart, so a dot at 0.79 is below one and above the other, and a two-tone split
# on one of them asserts a count the figure cannot support. One hue - the monitors are one
# population, and identity is not the job here, magnitude is.
#
# The two shaded spans ARE kept from the draft. They are bootstrap CIs from RESULTS.md 8.3, they
# genuinely overlap, and showing that overlap is the honest reading of "both floors clear 20 of 24".

def fig3_monitors():
    aurocs = sorted(m["test_auroc"] for m in json.load(open("monitor-summary.json")))
    n = len(aurocs)

    fig, ax = plt.subplots(figsize=(W_F3, 2.50))
    style(ax, base=7.0)

    # Every vertical rule STOPS at the top of the data. Drawn full height they run through the key.
    top = n + 0.8
    # The spans stop where the rules stop. Drawn with axvspan they run full height, straight
    # through the key - the same mistake as a full-height axvline, in a heavier weight.
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


# =============================================================================================
#  F2  -  the structural floor in five same-generator agentic settings
# =============================================================================================
#
# The draft's connector is kept: a line from the permutation null to the measured value, which is
# the quantity the reader is here for. It is drawn thin, not as a 4pt bar - at bar weight it reads
# as a bar grown from the null, and zero is not the reference for an AUROC, 0.5 is.
#
# Three of the five nulls sit BELOW chance, so the connector crosses the chance rule on those rows.
# That is the data. The draft's version had every null above chance and no row crossed.

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


# =============================================================================================
#  F5  -  every arm's retained signal against the bands fixed before any arm ran
# =============================================================================================
#
# Not currently included by main.tex - the paper carries these rows as Table 1 - but it is tracked
# in paper/fig, so it is built here and kept correct.
#
# The draft's shaded retention bands and their headers are kept; they are the reader's question.
# Its colour-by-band is not: band membership is already position, and hue is Cleveland & McGill's
# weakest channel, so hue goes to WHICH measurement instead (classifier / LLM monitor / bound).
# Rows the ledger gives no joint interval for get a point and no whisker, rather than an invented
# one. The null sits to the RIGHT of rho = 1, which is the whole point of publishing it.

def fig5_rho():
    fig, ax = plt.subplots(figsize=(TEXT_W, 3.45))
    fig.subplots_adjust(left=0.315, right=0.790, top=0.895, bottom=0.135)

    XMAX, n = 1.32, len(RHO_ROWS)
    ax.set_xlim(0, XMAX); ax.set_ylim(-0.7, n + 0.35)

    lo, hi = BANDS
    top = n - 0.42
    rule_top = top - 0.12   # every rule stops below the band headers; drawn full height with
                            # axvline they strike the header text through, and the rho = 1 rule
                            # lands exactly on "(rho > 0.72)"
    for x0, x1, fc in ((0, lo, "#fdeeee"), (lo, hi, "#fdf6e6"), (hi, XMAX, "#eef8f0")):
        ax.fill_betweenx([-0.7, rule_top], x0, x1, color=fc, lw=0, zorder=0)
    for b in BANDS:
        ax.plot([b, b], [-0.7, rule_top], color=GRID, lw=0.8, zorder=1)
    ax.plot([1.0, 1.0], [-0.7, rule_top], color=MUTED, lw=0.8, ls=(0, (3, 3)), zorder=2)

    for x, lab in ((lo / 2, f"collapse\n($\\rho \\leq$ {lo:g})"),
                   ((lo + hi) / 2, f"partial\n({lo:g} $<$ $\\rho \\leq$ {hi:g})"),
                   ((hi + XMAX) / 2, f"content\n($\\rho >$ {hi:g})")):
        ax.text(x, top, lab, ha="center", va="bottom", fontsize=7.2, color=INK2, style="italic",
                linespacing=1.25)
    ax.text(1.022, top, r"$\rho$  (95% CI, joint)", transform=ax.get_yaxis_transform(),
            ha="left", va="bottom", fontsize=8.0, color=INK, weight="bold")

    ticks, labels = [], []
    for i, (kind, label, v, clo, chi, colour) in enumerate(RHO_ROWS):
        y = n - 1 - i
        if kind == "head":
            ax.text(-0.014, y, label, transform=ax.get_yaxis_transform(), ha="right",
                    va="center", fontsize=8.6, color=INK, weight="bold")
            continue
        ticks.append(y); labels.append(label)
        if clo is not None:
            ax.plot([clo, chi], [y, y], color=colour, lw=1.5, alpha=0.40, zorder=4,
                    solid_capstyle="butt")
            for e in (clo, chi):
                ax.plot([e, e], [y - 0.17, y + 0.17], color=colour, lw=1.0, alpha=0.55, zorder=4)
        ax.scatter([v], [y], s=28, facecolor=colour, edgecolor="white", lw=0.7, zorder=6)
        txt = f"{v:.3f}" if clo is None else f"{v:.3f}  ({clo:.3f}–{chi:.3f})"
        ax.text(1.022, y, txt, transform=ax.get_yaxis_transform(), ha="left", va="center",
                fontsize=8.2, color=INK2)

    ax.set_yticks(ticks); ax.set_yticklabels(labels, fontsize=8.2, color=INK2)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(axis="x", colors=INK2, labelsize=8.5, length=3, width=0.7)
    ax.tick_params(axis="y", length=0)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0, 1.25])
    ax.set_xlabel(r"$\rho$  =  share of above-chance separability that survives",
                  fontsize=9.0, color=INK, labelpad=3)

    save(fig, "f5-rho-forest.pdf")
    rows = [r for r in RHO_ROWS if r[0] == "row"]
    print(f"F5: {len(rows)} rows, 3 bands; "
          f"{sum(1 for r in rows if r[3] is None)} with no published joint interval")


# =============================================================================================
#  F1  -  protocol x baseline, emitted as a LaTeX table (unchanged: it is >7 rows of labelled
#         values, which is a table, not a chart, and main.tex \inputs it)
# =============================================================================================
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



# =============================================================================================
#  CHECK  -  the figures against main.tex's macros
# =============================================================================================
#
# The draft this file replaces shipped five wrong permutation nulls, two wrong rho intervals, one
# invented interval and an AUROC the paper's own caption forbids. None of those was catchable by
# reading the script; all of them are catchable by asserting it against the numbers the prose
# already quotes. main.tex's \newcommand block is that independent copy, so the figures are checked
# against it at import and the run fails loudly rather than drawing a wrong number.

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
        # NB: half-up, not Python's round(), which is half-to-EVEN and turns the no-code floor's
        # 0.7715 into 0.771 while the paper prints 0.772.
        if macro not in m:
            bad.append(f"{macro}: absent from main.tex"); return
        want = m[macro]
        got_r = math.floor(got * 10 ** dp + 0.5) / 10 ** dp if dp else got
        if abs(want - got_r) > 5e-4:
            bad.append(f"{macro}: main.tex {want} vs figures.py {got_r}")

    # F4's ladder. main.tex:556 says none of the three is the Koran floor; that is what the
    # first row asserts.
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

    # F5, against Table 1's macros. The three the draft got wrong (haikuMatchedRho's upper bound,
    # the edit bound and the 1.234 row) are not in main.tex; RESULTS.md locations are on the rows.
    rho = {r[1]: r[2:5] for r in RHO_ROWS if r[0] == "row"}
    for label, stem in (("headline", "sameGen"), ("prompt-matched", "matched"),
                        ("strict (also fires)", "strict"),
                        ("strict, prompt-matched", "matchedStrict"),
                        ("Haiku 4.5, headline", "haiku")):
        v, lo, hi = rho[label]
        eq(f"{stem}Rho", v); eq(f"{stem}RhoLo", lo); eq(f"{stem}RhoHi", hi)
    eq("haikuMatchedRho", rho["Haiku 4.5, prompt-matched"][0])

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
    fig5_rho()
    print(f"\nwrote to {os.path.abspath(OUT)}")
