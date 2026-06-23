# Research — OULAD Motivation Proxy Index (MPI) for Fairness-Aware, Explainable Early Prediction

> 🎯 **Interactive decision-support dashboard:** <https://upocuantitativo.github.io/research_oulad_prediction/>
> Explore the results interactively — an early-warning simulator (when to intervene), the leakage-safe risk drivers,
> the MPI motivational profile by outcome, and the fairness/mitigation trade-offs. Runs entirely in the browser.

This repository accompanies the manuscript **"A Theory-Grounded Motivation Proxy Index for Fairness-Aware and Explainable Early Prediction of Academic Failure in Online Higher Education"** (Universidad Pablo de Olavide).

It studies academic failure/dropout on the **Open University Learning Analytics Dataset (OULAD)** by building a theory-grounded **Motivation Proxy Index (MPI)** from Virtual Learning Environment (VLE) behaviour — anchored in Self-Determination Theory, Expectancy-Value Theory and Self-Regulated Learning — and embedding it in an **explainable, fairness-aware, temporally-resolved** prediction pipeline.

## Key findings (computed from OULAD, N = 32,593)
- **Behaviour, not demographics, drives risk.** In a leakage-safe Random Forest, the top ten drivers are all behavioural/MPI; no demographic feature enters. Engagement (proportion of active weeks) is the single strongest signal.
- **Honest theory test.** Of the four MPI dimensions, engagement consistency and assessment timeliness validate; resource diversity reverses sign (r = −0.140) and persistence-after-difficulty is null (r ≈ 0).
- **MPI lift is small but reliable.** Logistic-model ROC-AUC rises +0.013 with the MPI (5×5-fold CV, p < 0.001, 95% CI [0.013, 0.014]).
- **Early warning.** A leakage-safe week-cumulative model reaches ROC-AUC ≥ 0.90 by **week 20** (usable triage by week 16).
- **Fairness.** The model satisfies equalised odds for students with disabilities (gap 0.015). A TPR-driven gap for repeat-attempt students (0.077) is reduced to equal opportunity by a **group-aware threshold** (gap → 0.047; 0.2 pp accuracy cost).

## Contents
- `Variables_Fuentes_APA.txt` — variable→source mapping and APA 7 references.
- `Motivation and OULAD Papers.xlsx` — bibliography of OULAD-method and MPI-motivation sources.
- `scripts_results/` — reproducible Python scripts and **aggregate** result tables/JSON/figures:
  - `01_build_mpi.py`, `02_analysis.py`, `03_early.py` — MPI construction, descriptives/models/XAI/fairness, early prediction.
  - `04_reviewer_addendum.py`, `05_mitigation_threshold.py` — leakage-safe re-analysis, CV significance, fairness mitigation.
  - `tab_*.csv`, `results*.json`, `tab3_leakage_safe_importance.csv`, `fig_*.png` — summary outputs only.
- `corpus/` — JSON manifests of the literature corpus (DOIs/OA links). PDFs are **not** redistributed for copyright reasons.

> **Not included here.** The manuscript and the underlying student-level dataset are **not** distributed in this
> repository. Only code and aggregate summary outputs are shared. The interactive dashboard uses aggregate figures only.

## Data
This study uses the third-party Open University Learning Analytics Dataset (OULAD; Kuzilek, Hlosta & Zdrahal, 2017),
which is **not** redistributed here. The processed student-level feature table is intentionally withheld; only
aggregate results are shared. To reproduce, obtain OULAD from its official owners and place the raw tables alongside the scripts.

## Reproduce
```bash
python scripts_results/01_build_mpi.py        # build MPI from raw OULAD tables
python scripts_results/02_analysis.py         # descriptives, models, SHAP/permutation, fairness
python scripts_results/03_early.py            # week-by-week early prediction
python scripts_results/04_reviewer_addendum.py
python scripts_results/05_mitigation_threshold.py
```

_Generated as part of the manuscript preparation pipeline._
