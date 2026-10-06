"""Build the paper's data figures and appendix tables into ../../paper/fig/.

    fig2-floors.pdf          Figure 2: the two floors among the 24 monitors ranked on the same split
    fig3-rebuilt.pdf         Figure 3: stored against rebuilt AUROC for the classifier (a) and the
                             monitor (b), and the monitor's catch rate at each audit budget (c)
    figA1-agentic.pdf        Appendix: the structural floor in five agentic settings
    tabA-baselines.tex       Appendix table: every baseline run on the stored pairs
    tabA-rebuilt.tex         Appendix table: S, B' and rho for every rebuilt row

Figure 1 is a TikZ schematic in main.tex. Every value plotted or tabulated here is a named constant
below, and check() asserts the ones the text quotes against the \\newcommand macros in
../../paper/main.tex before anything is drawn. Figure 2 also reads monitor-summary.json, Figure 3c
reads audit_budget.json and the appendix figure reads ../agentic/within_task_null.json.

AUROCs for rebuilt and stored pairs are pooled cross-validated estimates with 95% bootstrap
intervals over problems; rho intervals resample both AUROCs jointly.

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
    "pdf.fonttype": 42,
    "axes.linewidth": 0.6,
    "xtick.major.width": 0.6, "ytick.major.width": 0.6,
    "xtick.major.size": 2.5, "ytick.major.size": 2.5,
})

OUT = "../../paper/fig"
PDF_METADATA = {"CreationDate": None}
TEXT_W = 5.5
FS = 8.5                                    # base font size at print width

# --- palette ------------------------------------------------------------------------------
INK, INK2, MUTED, GRID = "#1d2127", "#4f5661", "#8d939c", "#e7e9ec"
STORED = "#c8682c"          # stored pairs: a person wrote one class, a model the other
SONNET = "#2f66b3"          # rebuilt pairs, Claude Sonnet 5
HAIKU = "#2b9a8a"           # rebuilt pairs, Claude Haiku 4.5
LEX = "#2f66b3"             # the lexical classifier
META = "#c8682c"            # the metadata classifier
MONITOR = "#a7adb5"         # published monitors
SHADE = "#e3e7ec"

# --- measured values (as reported in main.tex) ---------------------------------------------
LEX_FLOOR = 0.8063          # trained on the split's training problems, scored on its test set
META_FLOOR = 0.7715         # 5x5 cross-validation within the test set
META_HELDOUT = 0.7163

# Rebuilt rows: label, generator, stored AUROC B' (pt, lo, hi), rebuilt AUROC S (pt, lo, hi),
# rho (pt, lo, hi), pairs, firing attacks.
CLF_ROWS = [
    ("all attempts",                 "Sonnet", (0.8646, 0.8482, 0.8811), (0.7504, 0.7295, 0.7713), (0.687, 0.625, 0.755), 623, 14),
    ("all attempts, shared prompt",  "Sonnet", (0.8614, 0.8443, 0.8782), (0.6411, 0.6179, 0.6621), (0.390, 0.326, 0.454), 586, None),
    ("verified",                     "Sonnet", (0.7889, 0.7410, 0.8339), (0.7488, 0.7016, 0.8000), (0.861, 0.662, 1.089), 99, 99),
    ("verified, shared prompt",      "Sonnet", (0.7910, 0.7475, 0.8358), (0.6926, 0.6464, 0.7453), (0.662, 0.494, 0.856), 96, 96),
    ("all attempts",                 "Haiku",  (0.8564, 0.8392, 0.8726), (0.5344, 0.5159, 0.5531), (0.097, 0.044, 0.150), 611, 2),
    ("all attempts, shared prompt",  "Haiku",  (0.8540, 0.8353, 0.8716), (0.5391, 0.5197, 0.5581), (0.110, 0.055, 0.165), 562, None),
]
MON_ROWS = [
    ("all attempts", "Sonnet", (0.9579, 0.9466, 0.9683), (0.5662, 0.5507, 0.5833), (0.145, 0.111, 0.182)),
    ("verified",     "Sonnet", (0.9437, 0.9086, 0.9724), (0.8182, 0.7630, 0.8686), (0.717, 0.601, 0.832)),
    ("verified",     "Haiku",  (0.8765, 0.8238, 0.9238), (0.7883, 0.7237, 0.8494), (0.766, 0.588, 0.963)),
]
COLOR = {"Sonnet": SONNET, "Haiku": HAIKU}


def style(ax, grid="both"):
    ax.spines[["top", "right"]].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=INK2, labelsize=FS - 0.5)
    if grid:
        ax.grid(axis=grid if grid != "both" else "both", color=GRID, lw=0.5, zorder=0)
    ax.set_axisbelow(True)


def tag(ax, s, x=-0.16, y=1.04):
    ax.text(x, y, s, transform=ax.transAxes, fontsize=FS + 1, weight="bold", color=INK,
            ha="left", va="bottom")


def save(fig, name):
    fig.savefig(f"{OUT}/{name}", metadata=PDF_METADATA)
    plt.close(fig)


def r3(x):
    return f"{math.floor(x * 1000 + 0.5) / 1000:.3f}"


def r2(x):
    return f"{math.floor(x * 100 + 0.5) / 100:.2f}"


AGENTIC = [("bash", 0.5044), ("shade", 0.6022), ("iac", 0.7041), ("rogue_eval", 0.6158),
           ("agentdojo", 0.8020)]



# ===========================================================================================
# Visual system (modelled on the figures of flagship alignment papers): one message per panel,
# values printed on the marks, a centred title naming the quantity, light grid, no spines but the
# baseline, Arial throughout to match the Helvetica of Figure 1.
# ===========================================================================================
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "Liberation Sans", "DejaVu Sans"],
    "pdf.fonttype": 42,
    "axes.linewidth": 0.8, "axes.edgecolor": "#3A3F47",
    "xtick.major.width": 0.8, "ytick.major.width": 0, "xtick.major.size": 0, "ytick.major.size": 0,
    "xtick.color": "#3A3F47", "ytick.color": "#6B7280",
})
INK, INK2, MUTED, GRID = "#1F2328", "#6B7280", "#A3A9B2", "#E9ECEF"
STORED = "#E07B39"
REBUILT = "#3567B5"
MONBAR = "#D3D8DE"
FS = 8.5


def base(ax):
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(labelsize=FS - 0.5, pad=3)
    ax.grid(axis="y", color=GRID, lw=0.8, zorder=0)
    ax.set_axisbelow(True)


def ptitle(ax, text, letter=None):
    ax.set_title(text, fontsize=FS + 0.5, weight="bold", color=INK, pad=8)
    if letter:
        from matplotlib.transforms import blended_transform_factory
        tr = blended_transform_factory(ax.figure.transFigure, ax.transAxes)
        x = ax.get_position().x0 - (0.075 if letter == "a" else 0.045)
        ax.text(x, 1.035, letter, transform=tr, fontsize=FS + 1.5, weight="bold",
                color=INK, ha="left", va="bottom")


def short(repo):
    n = repo.split("/")[-1]
    for cut in ("-Instruct-2506", "-Instruct-v0.3", "-Instruct", "-instruct", "-it", "-Chat", "-reap25"):
        n = n.replace(cut, "")
    return n


# --- Figure 2: the leaderboard ------------------------------------------------------------------

def fig2_floors():
    mons = json.load(open("monitor-summary.json"))
    rows = [(short(m["repo"]), m["test_auroc"], "mon") for m in mons]
    rows += [("Lexical classifier", LEX_FLOOR, "lex"), ("Metadata classifier", META_FLOOR, "meta")]
    rows.sort(key=lambda r: -r[1])
    fig, ax = plt.subplots(figsize=(TEXT_W, 2.05))
    fig.subplots_adjust(left=0.065, right=0.995, top=0.86, bottom=0.07)
    base(ax)
    for i, (name, v, kind) in enumerate(rows):
        col = {"mon": MONBAR, "lex": REBUILT, "meta": STORED}[kind]
        ax.bar(i, v - 0.5, bottom=0.5, width=0.74, color=col, lw=0, zorder=2)
        if kind != "mon":
            ax.text(i, v + 0.012, r3(v), ha="center", va="bottom", fontsize=FS - 0.5,
                    weight="bold", color=col)
    # direct labels for our two bars and for the strongest monitor
    lex_i = next(i for i, r in enumerate(rows) if r[2] == "lex")
    meta_i = next(i for i, r in enumerate(rows) if r[2] == "meta")
    from matplotlib.patches import Patch
    leg = ax.legend(handles=[Patch(color=REBUILT, label="lexical classifier (cannot see backdoors)"),
                             Patch(color=STORED, label="metadata classifier (never reads code)"),
                             Patch(color=MONBAR, label="24 published monitors")],
                    loc="upper right", frameon=False, fontsize=FS - 0.5, handlelength=1.0,
                    handleheight=0.9, labelspacing=0.45, borderaxespad=0.2)
    for t in leg.get_texts():
        t.set_color(INK)
    ax.axhline(0.5, color="#3A3F47", lw=0.8, zorder=3)
    ax.text(len(rows) - 0.4, 0.505, "chance", ha="right", va="bottom", fontsize=FS - 1.5, color=INK2)
    ax.set_xlim(-0.7, len(rows) - 0.3); ax.set_ylim(0.4, 1.0)
    ax.set_xticks([]); ax.spines["bottom"].set_visible(False)
    ax.set_yticks([0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    ax.set_ylabel("AUROC", fontsize=FS, color=INK, labelpad=4)
    ptitle(ax, "AUROC on the filtered test split")
    save(fig, "fig2-floors.pdf")
    a = sorted(m["test_auroc"] for m in mons)
    print(f"Fig 2: {len(a)} monitors, median {statistics.median(a):.3f}, "
          f"{sum(x < LEX_FLOOR for x in a)} below lexical, {sum(x < META_FLOOR for x in a)} below metadata")


# --- Figure 3: stored against rebuilt, and the audit budget ----------------------------------

GROUPS = [("all\nattempts", 0), ("shared\nprompt", 1), ("working\nbackdoors", 2),
          ("all\nattempts", 4), ("shared\nprompt", 5)]


def fig3_rebuilt():
    audit = {(r["monitor"], r["row"], r["pairs"]): r
             for r in json.load(open("audit_budget.json"))["rows"]}
    fig = plt.figure(figsize=(TEXT_W, 2.55))
    ax = fig.add_axes([0.095, 0.27, 0.49, 0.59])
    cx = fig.add_axes([0.70, 0.27, 0.285, 0.59])

    # (a) grouped bars from chance, value on each bar, rho under each group
    base(ax)
    w = 0.36
    for g, (lab, k) in enumerate(GROUPS):
        b, s, rho = CLF_ROWS[k][2], CLF_ROWS[k][3], CLF_ROWS[k][4]
        for dx, val, col in ((-w / 2 - 0.02, b, STORED), (w / 2 + 0.02, s, REBUILT)):
            ax.bar(g + dx, val[0] - 0.5, bottom=0.5, width=w, color=col, lw=0, zorder=2)
            ax.plot([g + dx, g + dx], [val[1], val[2]], color=INK, lw=0.7, zorder=3)
            ax.text(g + dx, val[2] + 0.012, f"{val[0]:.2f}", ha="center", va="bottom",
                    fontsize=FS - 1.2, color=INK)
        ax.text(g, 0.452, f"keeps {100 * rho[0]:.0f}%", ha="center", va="center",
                fontsize=FS - 1.2, color=INK2)
    ax.axhline(0.5, color="#3A3F47", lw=0.8, zorder=3)
    ax.set_xticks(range(len(GROUPS)))
    ax.set_xticklabels([g[0] for g in GROUPS], fontsize=FS - 1, color=INK, linespacing=1.15)
    ax.tick_params(axis="x", pad=13)
    for x0, x1, name in ((0, 2, "Claude Sonnet 5"), (3, 4, "Claude Haiku 4.5")):
        ax.annotate("", xy=(x0 - 0.38, -0.30), xytext=(x1 + 0.38, -0.30), xycoords=("data", "axes fraction"),
                    textcoords=("data", "axes fraction"),
                    arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
        ax.text((x0 + x1) / 2, -0.37, name, transform=ax.get_xaxis_transform(), ha="center",
                va="top", fontsize=FS - 0.5, color=INK, weight="bold")
    ax.set_xlim(-0.6, len(GROUPS) - 0.4); ax.set_ylim(0.43, 1.0)
    ax.set_yticks([0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    ax.spines["bottom"].set_visible(False)
    ax.set_ylabel("AUROC", fontsize=FS, color=INK, labelpad=4)
    ptitle(ax, "Lexical classifier, stored vs. rebuilt pairs", "a")
    from matplotlib.patches import Patch
    leg = ax.legend(handles=[Patch(color=STORED, label="stored pairs"),
                             Patch(color=REBUILT, label="rebuilt pairs")],
                    loc="upper right", ncol=2, frameon=False, fontsize=FS - 1,
                    handlelength=1.0, handleheight=0.8, columnspacing=1.0, borderaxespad=0.1)
    for t in leg.get_texts():
        t.set_color(INK)

    # (b) catch rate against audit budget, Sonnet 5 monitor, working backdoors
    base(cx)
    cx.grid(axis="x", color=GRID, lw=0.8, zorder=0)
    cx.spines["left"].set_visible(False)
    for key, c, lab in ((("sonnet5", "strict", "stored"), STORED, "stored pairs"),
                        (("sonnet5", "strict", "samegen"), REBUILT, "rebuilt pairs")):
        cur = audit[key]["curve"]
        x = [100 * p["budget"] for p in cur]
        y = [100 * p["point"] for p in cur]
        cx.fill_between(x, [100 * p["ci95"][0] for p in cur], [100 * p["ci95"][1] for p in cur],
                        color=c, alpha=0.14, lw=0, zorder=1)
        cx.plot(x, y, color=c, lw=1.8, zorder=3)
        cx.text(19.6, y[-1] + (5 if c == STORED else -6), lab, color=c, fontsize=FS - 1,
                va="bottom" if c == STORED else "top", ha="right", weight="bold")
    st = 100 * audit[("sonnet5", "strict", "stored")]["catch@0.05"]["point"]
    rb = 100 * audit[("sonnet5", "strict", "samegen")]["catch@0.05"]["point"]
    for v, c in ((st, STORED), (rb, REBUILT)):
        cx.scatter([5], [v], s=22, color=c, zorder=5, lw=0)
        cx.text(5.6, v + (5 if c == STORED else -5), f"{v:.0f}%", color=c, fontsize=FS - 1,
                ha="left", va="bottom" if c == STORED else "top", weight="bold")
    cx.set_xlim(0, 20); cx.set_ylim(0, 100)
    cx.set_xticks([0, 5, 10, 15, 20]); cx.set_xticklabels(["0%", "5%", "10%", "15%", "20%"])
    cx.set_yticks([0, 25, 50, 75, 100]); cx.set_yticklabels(["0", "25%", "50%", "75%", "100%"])
    cx.tick_params(axis="x", pad=3)
    cx.set_xlabel("honest programs audited", fontsize=FS - 0.5, color=INK, labelpad=3)
    ptitle(cx, "Backdoors caught", "b")
    save(fig, "fig3-rebuilt.pdf")
    print(f"Fig 3: catch at 5%: stored {st:.1f}, rebuilt {rb:.1f}")


# --- Appendix figure ---------------------------------------------------------------------

def figA1_agentic():
    nulls = json.load(open("../agentic/within_task_null.json"))
    rows = AGENTIC
    fig, ax = plt.subplots(figsize=(0.8 * TEXT_W, 1.9))
    fig.subplots_adjust(left=0.09, right=0.99, top=0.84, bottom=0.17)
    base(ax)
    for i, (s, v) in enumerate(rows):
        p95 = nulls[s]["null_p95"]
        ax.bar(i, v - 0.5, bottom=0.5, width=0.55, color=REBUILT, lw=0, zorder=2)
        ax.plot([i - 0.36, i + 0.36], [p95, p95], color=INK, lw=1.0, ls=(0, (2, 1.5)), zorder=3)
        ax.text(i, max(v, p95) + 0.008, f"{v:.3f}", ha="center", va="bottom", fontsize=FS - 1, color=INK)
    ax.axhline(0.5, color="#3A3F47", lw=0.8, zorder=3)
    ax.set_xticks(range(len(rows)))
    ax.set_xticklabels([f"{s.replace('_', ' ')}\n{nulls[s]['n_tasks']} tasks" for s, _ in rows],
                       fontsize=FS - 1, color=INK, linespacing=1.15)
    ax.spines["bottom"].set_visible(False)
    ax.set_ylim(0.45, 0.87); ax.set_yticks([0.5, 0.6, 0.7, 0.8])
    ax.set_ylabel("AUROC", fontsize=FS, color=INK, labelpad=4)
    ptitle(ax, "Transcript length alone, within each task")
    save(fig, "figA1-agentic.pdf")
    print("Fig A1 done")


# --- Appendix tables -----------------------------------------------------------------------

BASELINES = [
    # (group, baseline, comments, value, monitors below)
    ("Filtered split, trained on its training problems", None, None, None, None),
    (None, "Lexical classifier, word unigrams and bigrams", "removed", "0.806", "20 of 24"),
    (None, "Lexical classifier, character 3 to 5 grams", "removed", "0.783", "20 of 24"),
    (None, "Lexical classifier, word unigrams and bigrams", "kept", "0.891", "22 of 24"),
    ("Filtered split, cross validated within its test set", None, None, None, None),
    (None, "Metadata classifier, 5 folds repeated 5 times", "", "0.772", "20 of 24"),
    (None, "Metadata classifier, one held out 30\\% slice", "", "0.716", "18 of 24"),
    (None, "Code length", "removed", "0.473", ""),
    (None, "Count of \\texttt{\\#} characters", "removed", "0.498", ""),
    (None, "Count of \\texttt{\\#} characters", "kept", "0.696", ""),
    ("Full artifact, one row per problem", None, None, None, None),
    (None, "All problem metadata", "", "0.892", ""),
    (None, "Difficulty", "", "0.682", ""),
    (None, "Whether the shipped solution passes", "", "0.788", ""),
    (None, "All metadata, both classes from every problem", "", "0.500", ""),
    ("Paired problems, pairwise accuracy over 5 splits", None, None, None, None),
    (None, "Lexical classifier, all pairs", "removed", "0.897", ""),
    (None, "Lexical classifier, working backdoors", "removed", "0.935", ""),
    (None, "Lexical classifier, inert backdoors", "removed", "0.879", ""),
    (None, "Lexical classifier, trained on one attacker, tested on another", "removed", "0.969", ""),
    (None, "Lexical classifier, all pairs", "kept", "0.962", ""),
]


def tab_baselines():
    lines = [
        "% generated by experiments/apps/figures.py; do not edit by hand",
        "\\begin{table}[h]\\centering\\small",
        "\\caption{\\textbf{Every baseline we ran on the stored pairs.} Values are AUROC except in "
        "the last group, which reports pairwise accuracy. \\emph{Below} counts the 24 published "
        "monitors that score lower on the same test set.}",
        "\\label{tab:baselines}",
        "\\begin{tabular}{@{}l l S[table-format=1.3] r@{}}",
        "\\toprule",
        "Baseline & Comments & {Value} & Below \\\\",
        "\\midrule",
    ]
    first = True
    for g, b, c, v, m in BASELINES:
        if g:
            if not first:
                lines.append("\\addlinespace[4pt]")
            lines.append(f"\\multicolumn{{4}}{{@{{}}l}}{{\\textbf{{{g}}}}} \\\\[1pt]")
            first = False
        else:
            lines.append(f"\\quad {b} & {c} & {v} & {m} \\\\")
    lines += ["\\bottomrule", "\\end{tabular}", "\\end{table}"]
    open(f"{OUT}/tabA-baselines.tex", "w").write("\n".join(lines) + "\n")


def tab_rebuilt():
    def cell(t):
        return f"{r3(t[0])}\\,\\ci{{{r2(t[1])}}}{{{r2(t[2])}}}"
    lines = [
        "% generated by experiments/apps/figures.py; do not edit by hand",
        "\\begin{table}[h]\\centering\\small",
        "\\caption{\\textbf{The lexical classifier on stored and rebuilt pairs of the same "
        "problems.} \\emph{Working} counts backdoors that change the output on their trigger. "
        "Grey brackets are 95\\% bootstrap intervals over problems, and $\\rho$ is the share of "
        "separability above chance that survives.}",
        "\\label{tab:rebuilt}",
        "\\setlength{\\tabcolsep}{5pt}",
        "\\begin{tabular}{@{}l r r l l l@{}}",
        "\\toprule",
        " & & & \\multicolumn{2}{c}{AUROC} & \\\\",
        "\\cmidrule(lr){4-5}",
        "Backdoors & Pairs & Working & Stored $B'$ & Rebuilt $S$ & Kept $\\rho$ \\\\",
        "\\midrule",
    ]
    prev = None
    for lab, gen, b, s, rho, n, fire in CLF_ROWS:
        if gen != prev:
            if prev:
                lines.append("\\addlinespace[4pt]")
            name = {"Sonnet": "Claude Sonnet 5 writes both classes",
                    "Haiku": "Claude Haiku 4.5 writes both classes"}[gen]
            lines.append(f"\\multicolumn{{6}}{{@{{}}l}}{{\\textbf{{{name}}}}} \\\\[1pt]")
        shown = lab.replace("verified", "working backdoors").replace("working backdoors, shared", "working, shared")
        fires = "" if fire is None else str(fire)
        lines.append(f"\\quad {shown} & {n} & {fires} & {cell(b)} & {cell(s)} & {cell(rho)} \\\\")
        prev = gen
    lines += ["\\bottomrule", "\\end{tabular}", "\\end{table}"]
    open(f"{OUT}/tabA-rebuilt.tex", "w").write("\n".join(lines) + "\n")


# --- check(): quoted values against main.tex -----------------------------------------------
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

    def eq(macro, got, dp=3):
        if macro not in m:
            bad.append(f"{macro}: absent from main.tex"); return
        got_r = math.floor(got * 10 ** dp + 0.5) / 10 ** dp
        if abs(m[macro] - got_r) > 5e-4:
            bad.append(f"{macro}: main.tex {m[macro]} vs figures.py {got_r}")

    eq("lexFloor", LEX_FLOOR); eq("metaFloor", META_FLOOR); eq("metaHeldout", META_HELDOUT)
    names = ["SonAll", "SonShared", "SonVer", "SonVerShared", "HaiAll", "HaiShared"]
    for nm, (lab, gen, b, s, rho, n, fire) in zip(names, CLF_ROWS):
        eq(f"rho{nm}", rho[0]); eq(f"rho{nm}Lo", rho[1]); eq(f"rho{nm}Hi", rho[2])
    for nm, (lab, gen, b, s, rho) in zip(["MonSonAll", "MonSonVer", "MonHaiVer"], MON_ROWS):
        eq(f"stored{nm}", b[0]); eq(f"rebuilt{nm}", s[0]); eq(f"rho{nm}", rho[0])
    if os.path.exists("monitor-summary.json"):
        a = sorted(x["test_auroc"] for x in json.load(open("monitor-summary.json")))
        eq("monN", len(a), 0); eq("monMedian", statistics.median(a))
        eq("monBelow", sum(x < LEX_FLOOR for x in a), 0)
    au = {(r["monitor"], r["row"], r["pairs"]): r for r in json.load(open("audit_budget.json"))["rows"]}
    st, rb = au[("sonnet5", "strict", "stored")]["catch@0.05"], au[("sonnet5", "strict", "samegen")]["catch@0.05"]
    eq("catchStored", 100 * st["point"], 0); eq("catchStoredLo", 100 * st["ci95"][0], 0)
    eq("catchStoredHi", 100 * st["ci95"][1], 0)
    eq("catchRebuilt", 100 * rb["point"], 0); eq("catchRebuiltLo", 100 * rb["ci95"][0], 0)
    eq("catchRebuiltHi", 100 * rb["ci95"][1], 0)
    if bad:
        raise SystemExit("CHECK FAILED against main.tex:\n  " + "\n  ".join(bad))
    print(f"CHECK: {len(m)} numeric macros read from main.tex; every quoted value agrees")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    check()
    tab_baselines()
    tab_rebuilt()
    fig2_floors()
    fig3_rebuilt()
    figA1_agentic()
    print(f"\nwrote to {os.path.abspath(OUT)}")
