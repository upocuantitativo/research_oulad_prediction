# -*- coding: utf-8 -*-
"""Insert the three figures and two red decision-support callouts into the
manuscript markdown, then leave it ready for md_to_docx.py.
Usage: python 07_enhance_manuscript.py
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MD = os.path.normpath(os.path.join(HERE, "..", "manuscrito", "MANUSCRITO_MPI_OULAD.md"))

txt = open(MD, encoding="utf-8").read()

RED_TOOLS = """
:::red
**Interactive decision-support companion.** A browser-based dashboard accompanies this article and is openly available at https://upocuantitativo.github.io/research_oulad_prediction/. Designed for educators and programme managers, it turns every result reported below into an interactive triage tool: an early-warning simulator that maps the chosen intervention week to model confidence (cf. Section 5.4), the leakage-safe risk drivers behind each flag (cf. Section 5.3), the motivational MPI profile by outcome (cf. Section 5.2), and the fairness/mitigation trade-offs by protected group (cf. Section 5.5). The dashboard runs entirely in the browser -- no student data leaves the device -- and is intended to move the study's findings from static reporting to actionable, week-by-week intervention decisions.
:::
"""

RED_PRACTICE = """
:::red
**Putting it to work.** These three implications are operationalised in the interactive companion dashboard (https://upocuantitativo.github.io/research_oulad_prediction/): a tutor can set the intervention week, read the SHAP-based reason a learner is flagged, and inspect the group-specific equity gap before acting.
:::
"""

FIG_RADAR = "\n\n![Figure 1. Motivation Proxy Index (MPI) profile by final outcome (standardised dimension means). Distinction and Pass students show higher engagement (D1) and timeliness (D3); Fail and Withdrawn students invert the pattern, while diversity (D2) and persistence (D4) run against theoretical expectation.](../scripts_results/fig_mpi_radar.png)"

FIG_DRIVERS = "\n\n![Figure 2. Leakage-safe drivers of course passing (mean |SHAP|, Random Forest). Behavioural engagement features dominate; the three MPI dimensions enter as incremental contributors; no demographic attribute reaches the top tier.](../scripts_results/fig_drivers.png)"

FIG_EARLY = "\n\n![Figure 3. Early-warning performance by course week (leakage-safe cumulative model). Usable triage (AUC ~ 0.87) is available by week 16; the first week reaching the high-confidence threshold (AUC >= 0.90) is week 20.](../scripts_results/fig_early_warning.png)"

# (anchor substring, text to insert AFTER it, label)
edits = [
    ("All feature-engineering and modelling scripts are retained for reproducibility.",
     "\n" + RED_TOOLS, "red-tools"),
    ("require re-specification or re-weighting (Section 6).",
     FIG_RADAR, "fig-radar"),
    ("| 10 | MPI (composite) | motivation | 0.0005 | 0.005 |",
     FIG_DRIVERS, "fig-drivers"),
    ("| AUC | 0.678 | 0.783 | 0.832 | 0.871 | **0.907** | 0.930 | 0.941 | 0.956 |",
     FIG_EARLY, "fig-early"),
    ("with mitigation prioritised for repeat-attempt learners.",
     "\n" + RED_PRACTICE, "red-practice"),
    ("documenting the broader analysis pipeline and its reinforcement-learning extension (https://upocuantitativo.github.io/motivationlearn/).",
     " A third companion -- an interactive decision-support dashboard for this study -- is openly available at https://upocuantitativo.github.io/research_oulad_prediction/.",
     "data-avail"),
]

for anchor, insert, label in edits:
    n = txt.count(anchor)
    if n != 1:
        print(f"!! ANCHOR '{label}' matched {n} times (expected 1) -- ABORTING")
        sys.exit(1)
    # idempotency guard
    if insert.strip() and insert.strip()[:40] in txt and label.startswith("fig"):
        pass
    txt = txt.replace(anchor, anchor + insert, 1)
    print(f"ok  {label}")

open(MD, "w", encoding="utf-8").write(txt)
print("WROTE", MD)
