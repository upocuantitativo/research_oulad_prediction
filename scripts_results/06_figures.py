# -*- coding: utf-8 -*-
"""Generate publication-quality figures for the manuscript and the interactive site.
Reads results_early.json, results.json, tab3_leakage_safe_importance.csv.
Outputs PNGs into scripts_results/ and ../site/assets/.
Usage: python 06_figures.py
"""
import json, os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.normpath(os.path.join(HERE, "..", "site", "assets"))
os.makedirs(SITE, exist_ok=True)

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "axes.edgecolor": "#cbd5e1",
    "axes.linewidth": 0.8,
    "figure.dpi": 200,
    "savefig.dpi": 200,
    "savefig.bbox": "tight",
})

INK = "#0f172a"
ACCENT = "#2563eb"
GOOD = "#059669"
WARN = "#d97706"
BAD = "#dc2626"


def save(fig, name):
    for d in (HERE, SITE):
        fig.savefig(os.path.join(d, name), facecolor="white")
    plt.close(fig)
    print("saved", name)


# ---------- Figure 1: Early-warning curve (AUC by week) ----------
early = json.load(open(os.path.join(HERE, "results_early.json"), encoding="utf-8"))
bw = early["by_week"]
weeks = sorted(int(w) for w in bw)
aucs = [bw[str(w)]["auc"] for w in weeks]

fig, ax = plt.subplots(figsize=(7.2, 4.3))
ax.axhspan(0.90, 1.0, color=GOOD, alpha=0.07)
ax.axhline(0.90, color=GOOD, ls="--", lw=1.2, zorder=1)
ax.plot(weeks, aucs, "-", color=ACCENT, lw=2.6, zorder=3)
for w, a in zip(weeks, aucs):
    c = GOOD if a >= 0.90 else (WARN if a >= 0.80 else BAD)
    ax.plot(w, a, "o", color=c, ms=8, zorder=4, mec="white", mew=1.2)
# annotate decision points
ax.annotate("Week 16\nusable triage (AUC 0.87)", xy=(16, 0.8709), xytext=(16, 0.74),
            ha="center", fontsize=9, color=WARN,
            arrowprops=dict(arrowstyle="->", color=WARN))
ax.annotate("Week 20\nfirst AUC ≥ 0.90", xy=(20, 0.9065), xytext=(23.5, 0.80),
            ha="center", fontsize=9, color=GOOD,
            arrowprops=dict(arrowstyle="->", color=GOOD))
ax.text(0.90, 0.905, "high-confidence zone", color=GOOD, fontsize=8.5, va="bottom")
ax.set_xlabel("Course week (cumulative behaviour only)")
ax.set_ylabel("ROC-AUC (leakage-safe early model)")
ax.set_title("When can an at-risk student be reliably flagged?", fontweight="bold", color=INK)
ax.set_xticks(weeks)
ax.set_ylim(0.62, 0.99)
ax.grid(axis="y", color="#eef2f7", lw=1)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
save(fig, "fig_early_warning.png")


# ---------- Figure 2: MPI radar by final result ----------
res = json.load(open(os.path.join(HERE, "results.json"), encoding="utf-8"))
mbf = res["mpi_by_final_result"]
dims = ["D1_engagement", "D2_diversity", "D3_timeliness", "D4_persistence"]
labels = ["Engagement\n(D1)", "Diversity\n(D2)", "Timeliness\n(D3)", "Persistence\n(D4)"]
outcomes = ["Distinction", "Pass", "Fail", "Withdrawn"]
ocol = {"Distinction": GOOD, "Pass": ACCENT, "Fail": WARN, "Withdrawn": BAD}

ang = np.linspace(0, 2 * np.pi, len(dims), endpoint=False).tolist()
ang += ang[:1]
fig = plt.figure(figsize=(6.4, 5.6))
ax = fig.add_subplot(111, polar=True)
for o in outcomes:
    vals = [mbf[d][o] for d in dims]
    vals += vals[:1]
    ax.plot(ang, vals, "-", color=ocol[o], lw=2.2, label=o)
    ax.fill(ang, vals, color=ocol[o], alpha=0.08)
ax.set_xticks(ang[:-1])
ax.set_xticklabels(labels, fontsize=9.5)
ax.set_yticks([-0.2, 0, 0.2])
ax.set_yticklabels(["-0.2", "0", "+0.2"], fontsize=8, color="#64748b")
ax.set_ylim(-0.32, 0.42)
ax.set_title("Motivation Proxy Index profile by outcome\n(standardised dimension means)",
             fontweight="bold", color=INK, pad=22)
ax.legend(loc="upper right", bbox_to_anchor=(1.22, 1.12), frameon=False, fontsize=9)
save(fig, "fig_mpi_radar.png")


# ---------- Figure 3: Leakage-safe drivers (importance by family) ----------
imp = pd.read_csv(os.path.join(HERE, "tab3_leakage_safe_importance.csv"), index_col=0)
imp = imp.sort_values("mean_abs_shap", ascending=True).tail(12)
fam_col = {"behavioural": ACCENT, "MPI": "#7c3aed", "demographic": "#94a3b8"}
colors = [fam_col[f] for f in imp["family"]]

fig, ax = plt.subplots(figsize=(7.4, 5.0))
ax.barh(imp.index, imp["mean_abs_shap"], color=colors, edgecolor="white")
ax.set_xlabel("Mean |SHAP| (leakage-safe Random Forest)")
ax.set_title("What drives the prediction? Behaviour over demographics",
             fontweight="bold", color=INK)
ax.grid(axis="x", color="#eef2f7", lw=1)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
handles = [Patch(color=c, label=f) for f, c in fam_col.items()]
ax.legend(handles=handles, title="Feature family", frameon=False, loc="lower right")
save(fig, "fig_drivers.png")

print("ALL FIGURES DONE ->", HERE, "and", SITE)
