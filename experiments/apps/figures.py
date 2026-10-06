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


# --- Figure 2: the floors among the monitors ------------------------------------------------

def fig2_floors():
    aurocs = sorted(m["test_auroc"] for m in json.load(open("monitor-summary.json")))
    n = len(aurocs)
    fig, ax = plt.subplots(figsize=(TEXT_W, 1.25))
    fig.subplots_adjust(left=0.03, right=0.97, top=0.97, bottom=0.33)
    style(ax, grid=None)
    ax.spines["left"].set_visible(False)
    ax.set_yticks([])

    # dot histogram: monitors in bins of 0.02, stacked upwards
    width, step = 0.02, 1.0
    stacks = {}
    for a in aurocs:
        b = round(math.floor(a / width) * width + width / 2, 4)
        stacks[b] = stacks.get(b, 0) + 1
        ax.scatter([b], [stacks[b] * step], s=40, color=MONITOR, lw=0, zorder=3)
    top = max(stacks.values()) + 0.9

    ax.axvline(0.5, color=MUTED, lw=0.7, ls=(0, (2, 2)), zorder=1)
    ax.text(0.5, top + 0.25, "chance", ha="center", va="bottom", fontsize=FS - 0.5, color=MUTED)
    for v, c, lab, ha, dx in ((META_FLOOR, META, f"metadata classifier {r3(META_FLOOR)}", "right", -0.006),
                              (LEX_FLOOR, LEX, f"lexical classifier {r3(LEX_FLOOR)}", "left", 0.006)):
        ax.plot([v, v], [0.3, top], color=c, lw=1.6, zorder=4, solid_capstyle="butt")
        ax.text(v + dx, top + 0.25, lab, ha=ha, va="bottom", fontsize=FS, color=c)
    below = sum(a < LEX_FLOOR for a in aurocs)
    ax.set_xlim(0.40, 1.0); ax.set_ylim(0.2, top + 1.1)
    ax.set_xticks([0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    ax.set_xlabel("AUROC on the filtered test split (1,375 programs, comments removed)",
                  fontsize=FS, color=INK)
    save(fig, "fig2-floors.pdf")
    print(f"Fig 2: {n} monitors, median {statistics.median(aurocs):.3f}, max {aurocs[-1]:.3f}, "
          f"{below} below the lexical floor, {sum(a < META_FLOOR for a in aurocs)} below metadata")


# --- Figure 3: stored against rebuilt, and the audit budget --------------------------------

ROW_NAMES = {
    ("all attempts", "Sonnet"): "Sonnet 5, all attempts",
    ("all attempts, shared prompt", "Sonnet"): "Sonnet 5, all attempts, shared prompt",
    ("verified", "Sonnet"): "Sonnet 5, working backdoors",
    ("verified, shared prompt", "Sonnet"): "Sonnet 5, working, shared prompt",
    ("all attempts", "Haiku"): "Haiku 4.5, all attempts",
    ("all attempts, shared prompt", "Haiku"): "Haiku 4.5, all attempts, shared prompt",
}
MON_NAMES = {
    ("all attempts", "Sonnet"): "Sonnet 5 monitor, all attempts",
    ("verified", "Sonnet"): "Sonnet 5 monitor, working backdoors",
    ("verified", "Haiku"): "Haiku 4.5 monitor, working backdoors",
}


def fig3_rebuilt():
    audit = {(r["monitor"], r["row"], r["pairs"]): r
             for r in json.load(open("audit_budget.json"))["rows"]}
    fig = plt.figure(figsize=(TEXT_W, 2.7))
    ax = fig.add_axes([0.375, 0.15, 0.28, 0.74])
    axc = fig.add_axes([0.775, 0.15, 0.215, 0.74])

    # (a) dumbbells: stored AUROC to rebuilt AUROC, one row per comparison
    rows = [("Lexical classifier", None, None)]
    rows += [(None, ROW_NAMES[(r[0], r[1])], r) for r in CLF_ROWS]
    rows += [("LLM monitor", None, None)]
    rows += [(None, MON_NAMES[(r[0], r[1])], r) for r in MON_ROWS]
    n = len(rows)
    style(ax, grid="x")
    ax.spines["left"].set_visible(False)
    ax.axvline(0.5, color=MUTED, lw=0.7, ls=(0, (2, 2)), zorder=1)
    ticks, labels = [], []
    for i, (grp, name, r) in enumerate(rows):
        y = n - 1 - i
        if grp:
            ax.text(-0.03, y - 0.1, grp, transform=ax.get_yaxis_transform(), ha="right",
                    va="center", fontsize=FS, color=INK, weight="bold")
            continue
        b, s = r[2], r[3]
        ax.plot([s[0], b[0]], [y, y], color="#c9cdd3", lw=2.2, zorder=2, solid_capstyle="round")
        ax.scatter([b[0]], [y], s=30, color=STORED, lw=0, zorder=3)
        ax.scatter([s[0]], [y], s=30, color=SONNET, lw=0, zorder=3)
        ticks.append(y); labels.append(name)
    ax.set_yticks(ticks); ax.set_yticklabels(labels, fontsize=FS - 0.5, color=INK)
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(0.45, 1.0); ax.set_ylim(-0.6, n - 0.4)
    ax.set_xticks([0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    ax.set_xlabel("AUROC", fontsize=FS, color=INK)
    ax.text(0.505, -0.55, "chance", ha="left", va="bottom", fontsize=FS - 1.5, color=MUTED)
    from matplotlib.lines import Line2D
    handles = [Line2D([], [], marker="o", ls="", color=STORED, markersize=5.5, label="stored pairs"),
               Line2D([], [], marker="o", ls="", color=SONNET, markersize=5.5, label="rebuilt pairs")]
    leg = fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.515, 1.0), ncol=2,
                     frameon=False, fontsize=FS - 0.5, handletextpad=0.3, columnspacing=1.6)
    for t in leg.get_texts():
        t.set_color(INK)
    tag(ax, "a", x=-1.30, y=1.02)

    # (b) catch rate against audit budget, Sonnet 5 monitor
    style(axc)
    for key, c, ls, lab, ly in ((("sonnet5", "strict", "stored"), STORED, "-", "stored, verified", None),
                                (("sonnet5", "strict", "samegen"), SONNET, "-", "rebuilt, verified", None),
                                (("sonnet5", "headline", "stored"), STORED, (0, (2, 1.5)), "stored, all", None),
                                (("sonnet5", "headline", "samegen"), SONNET, (0, (2, 1.5)), "rebuilt, all", None)):
        cur = audit[key]["curve"]
        x = [100 * p["budget"] for p in cur]
        y = [p["point"] for p in cur]
        if ls == "-":
            axc.fill_between(x, [p["ci95"][0] for p in cur], [p["ci95"][1] for p in cur],
                             color=c, alpha=0.14, lw=0, zorder=1)
        axc.plot(x, y, color=c, lw=1.4 if ls == "-" else 1.0, ls=ls, zorder=3)
    axc.set_xlim(1, 20); axc.set_ylim(0, 1)
    axc.set_xticks([1, 5, 10, 20]); axc.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    axc.set_yticklabels(["0", "25%", "50%", "75%", "100%"])
    axc.set_xlabel("audit budget (%)", fontsize=FS, color=INK)
    axc.set_ylabel("backdoors caught", fontsize=FS, color=INK, labelpad=2)
    tag(axc, "b", x=-0.42, y=1.02)
    save(fig, "fig3-rebuilt.pdf")
    v = (audit[("sonnet5", "strict", "stored")]["catch@0.05"],
         audit[("sonnet5", "strict", "samegen")]["catch@0.05"])
    print(f"Fig 3: catch at 5%: stored {v[0]['point']:.3f} {v[0]['ci95']}, "
          f"rebuilt {v[1]['point']:.3f} {v[1]['ci95']}")


# --- Appendix figure: agentic settings -----------------------------------------------------

AGENTIC = [("bash", 0.5044), ("shade", 0.6022), ("iac", 0.7041), ("rogue_eval", 0.6158),
           ("agentdojo", 0.8020)]


def figA1_agentic():
    nulls = json.load(open("../agentic/within_task_null.json"))
    rows = AGENTIC[::-1]
    fig, ax = plt.subplots(figsize=(0.82 * TEXT_W, 1.5))
    fig.subplots_adjust(left=0.27, right=0.96, top=0.97, bottom=0.24)
    style(ax, grid="x")
    ax.spines["left"].set_visible(False)
    for i, (s, v) in enumerate(rows):
        p95 = nulls[s]["null_p95"]
        ax.fill_between([0.5, p95], i - 0.22, i + 0.22, color=SHADE, lw=0, zorder=1)
        ax.scatter([v], [i], s=28, color=LEX, lw=0, zorder=3)
        ax.text(max(v, p95) + 0.01, i, r3(v), va="center", fontsize=FS - 0.5, color=INK)
    ax.axvline(0.5, color=MUTED, lw=0.7, ls=(0, (2, 2)), zorder=2)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([f"{s.replace('_', ' ')}  ({nulls[s]['n_tasks']} tasks)" for s, _ in rows],
                       fontsize=FS - 0.5, color=INK)
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(0.45, 0.90); ax.set_ylim(-0.6, len(rows) - 0.4)
    ax.set_xlabel("AUROC from transcript length alone, within each task", fontsize=FS, color=INK)
    save(fig, "figA1-agentic.pdf")
    print("Fig A1: " + ", ".join(f"{s} {v:.3f} (p {nulls[s]['p']:.3f})" for s, v in AGENTIC))


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
        "the last group. The last column counts the 24 published monitors that score below the "
        "baseline on the same test set. Rows with comments kept are shown only for contrast.}",
        "\\label{tab:baselines}",
        "\\begin{tabular}{@{}l c r r@{}}",
        "\\toprule",
        "Baseline & Comments & Value & Monitors below \\\\",
        "\\midrule",
    ]
    first = True
    for g, b, c, v, m in BASELINES:
        if g:
            if not first:
                lines.append("\\addlinespace[3pt]")
            lines.append(f"\\multicolumn{{4}}{{@{{}}l}}{{\\emph{{{g}}}}} \\\\")
            first = False
        else:
            lines.append(f"\\quad {b} & {c} & {v} & {m} \\\\")
    lines += ["\\bottomrule", "\\end{tabular}", "\\end{table}"]
    open(f"{OUT}/tabA-baselines.tex", "w").write("\n".join(lines) + "\n")


def tab_rebuilt():
    def ci(t):
        return f"{r3(t[0])} {{\\color{{gray}}\\scriptsize[{r2(t[1])}, {r2(t[2])}]}}"
    lines = [
        "% generated by experiments/apps/figures.py; do not edit by hand",
        "\\begin{table}[h]\\centering\\small",
        "\\caption{\\textbf{The lexical classifier on stored and rebuilt pairs of the same "
        "problems.} \\emph{Working} counts backdoors that change the output on their trigger. Brackets are 95\\% "
        "bootstrap intervals over problems.}",
        "\\label{tab:rebuilt}",
        "\\setlength{\\tabcolsep}{4pt}",
        "\\begin{tabular}{@{}l l r r l l l@{}}",
        "\\toprule",
        "Writer & Backdoors & Pairs & Working & Stored $B'$ & Rebuilt $S$ & Retained $\\rho$ \\\\",
        "\\midrule",
    ]
    prev = None
    for lab, gen, b, s, rho, n, fire in CLF_ROWS:
        if prev and gen != prev:
            lines.append("\\addlinespace[3pt]")
        name = {"Sonnet": "Sonnet 5", "Haiku": "Haiku 4.5"}[gen] if gen != prev else ""
        shown = lab.replace("verified", "working backdoors").replace("working backdoors, shared", "working, shared")
        lines.append(f"{name} & {shown} & {n} & {fire if fire is not None else ''} & {ci(b)} & "
                     f"{ci(s)} & {ci(rho)} \\\\")
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
