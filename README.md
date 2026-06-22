# Research — OULAD Motivation Proxy Index (MPI) for Fairness-Aware, Explainable Early Prediction

This repository accompanies the manuscript **"A Theory-Grounded Motivation Proxy Index for Fairness-Aware and Explainable Early Prediction of Academic Failure in Online Higher Education"** (Universidad Pablo de Olavide).

It studies academic failure/dropout on the **Open University Learning Analytics Dataset (OULAD)** by building a theory-grounded **Motivation Proxy Index (MPI)** from Virtual Learning Environment (VLE) behaviour — anchored in Self-Determination Theory, Expectancy-Value Theory and Self-Regulated Learning — and embedding it in an **explainable, fairness-aware, temporally-resolved** prediction pipeline.

## Key findings (computed from OULAD, N = 32,593)
- **Behaviour, not demographics, drives risk.** In a leakage-safe Random Forest, the top ten drivers are all behavioural/MPI; no demographic feature enters. Engagement (proportion of active weeks) is the single strongest signal.
- **Honest theory test.** Of the four MPI dimensions, engagement consistency and assessment timeliness validate; resource diversity reverses sign (r = −0.140) and persistence-after-difficulty is null (r ≈ 0).
- **MPI lift is small but reliable.** Logistic-model ROC-AUC rises +0.013 with the MPI (5×5-fold CV, p < 0.001, 95% CI [0.013, 0.014]).
- **Early warning.** A leakage-safe week-cumulative model reaches ROC-AUC ≥ 0.90 by **week 20** (usable triage by week 16).
- **Fairness.** The model satisfies equalised odds for students with disabilities (gap 0.015). A TPR-driven gap for repeat-attempt students (0.077) is reduced to equal opportunity by a **group-aware threshold** (gap → 0.047; 0.2 pp accuracy cost).

## Contents
- `Manuscrito_MPI_OULAD.docx` / `MANUSCRITO_MPI_OULAD.md` — the manuscript (main text ≈ 6,100 words).
- `MARCO_CONCEPTUAL_Y_GAP.md` — conceptual framework and the identified research gap (built from a multi-paper corpus).
- `Variables_Fuentes_APA.txt` — variable→source mapping and APA 7 references.
- `Motivation and OULAD Papers.xlsx` — bibliography of OULAD-method and MPI-motivation sources.
- `scripts_results/` — reproducible Python scripts and result tables/JSON/figure:
  - `01_build_mpi.py`, `02_analysis.py`, `03_early.py` — MPI construction, descriptives/models/XAI/fairness, early prediction.
  - `04_reviewer_addendum.py`, `05_mitigation_threshold.py` — leakage-safe re-analysis, CV significance, fairness mitigation.
  - `tab_*.csv`, `results*.json`, `tab3_leakage_safe_importance.csv`, `fig_early_auc.png` — outputs.
  - `mpi_features.csv` — the engineered MPI feature table (student × module × presentation).
- `corpus/` — JSON manifests of the literature corpus (DOIs/OA links). The downloaded PDFs are **not** redistributed here for copyright reasons.

## Data
OULAD is openly available under CC-BY 4.0: https://analyse.kmi.open.ac.uk/open_dataset (Kuzilek, Hlosta & Zdrahal, 2017). Place the raw tables alongside the scripts to reproduce. Companion sites: https://upocuantitativo.github.io/Educational_Interaction/ and https://upocuantitativo.github.io/motivationlearn/.

## Reproduce
```bash
python scripts_results/01_build_mpi.py        # build MPI from raw OULAD tables
python scripts_results/02_analysis.py         # descriptives, models, SHAP/permutation, fairness
python scripts_results/03_early.py            # week-by-week early prediction
python scripts_results/04_reviewer_addendum.py
python scripts_results/05_mitigation_threshold.py
```

_Generated as part of the manuscript preparation pipeline._
