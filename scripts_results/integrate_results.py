# -*- coding: utf-8 -*-
import re
p=r'C:\Users\Usuario\OneDrive - Universidad Pablo de Olavide de Sevilla\Escritorio\1_ARTÍCULO\1_ARTÍCULO MOTIVACIÓN_Bel_Gol_Has\MANUSCRITO_MPI_OULAD.md'
t=open(p,encoding='utf-8').read()
pairs=[]
def add(o,n): pairs.append((o,n))

# --- Abstract: lift number + mitigation ---
add("that the MPI yields an interpretable predictive lift on a transparent logistic model (+0.029 AUC) and separates at-risk profiles on engagement and timeliness; that leakage-safe prediction reaches AUC ≥ 0.90 by mid-course (week 20); and that the model is recall-fair for students with disabilities while a modest equalised-odds gap remains for repeat-attempt students.",
"that the MPI gives a small but statistically reliable cross-validated lift on a transparent logistic model (+0.013 AUC, p < 0.001) and separates at-risk profiles on engagement and timeliness; that leakage-safe prediction reaches AUC ≥ 0.90 by mid-course (week 20); and that the model satisfies equalised odds for students with disabilities, while a group-aware threshold restores equal opportunity for repeat-attempt students, for whom a gap otherwise persists.")

# --- 5.2 P5 parenthetical nuance ---
add("The equal-weight composite correlates r = +0.131—diluted by D2 and D4 and thus weaker than its own best dimension (P5 is therefore not supported as an equal-weight aggregate).",
"The equal-weight composite correlates r = +0.131—diluted by D2 and D4 and thus weaker than its own best dimension as a standalone correlate, although the MPI dimensions still add incremental value within a model (Section 5.6).")

# --- 5.3 text ---
add("For the binary pass model (Random Forest, 400 trees, balanced class weights, 75/25 stratified split) we computed impurity importance, permutation importance (10 repeats), and SHAP (TreeExplainer). The model is overwhelmingly **behavioural, not demographic**: no demographic feature (deprivation, education, age) enters the top ten under either method. Submission timing and submission count dominate, and the MPI engagement dimension (D1) ranks fourth by mean |SHAP|, ahead of most assessment scores (Table 3), confirming that the motivation proxy is interpretable and theoretically plausible rather than an artefact. We note one leakage caveat: `mean_submit_delay` is a full-course aggregate that absorbs withdrawal behaviour and inflates this model; we therefore treat the leakage-safe week-cumulative model (RQ2) as the deployable headline. A transformer/LSTM comparison on raw clickstream sequences is part of the pipeline and is reported as ongoing design; the explainability results above are for the classical learner actually estimated here.",
"For the binary pass model (Random Forest, 400 trees, balanced class weights, 75/25 stratified split) we computed permutation importance (10 repeats) and SHAP (TreeExplainer) on a strictly leakage-safe feature set, dropping `mean_submit_delay`, unregistration and withdrawal fields, and all full-course grade aggregates that mechanically encode the outcome. Removing leakage lowers AUC only modestly (0.983 to 0.969; accuracy 0.915), confirming that the behavioural and MPI signal is real rather than restated grades. The model is overwhelmingly **behavioural, not demographic**: the top ten features comprise seven raw behavioural indicators and three MPI dimensions, with no demographic attribute (IMD, age, education, prior attempts, credits) present (Table 3). The strongest single driver is the proportion of active course weeks (`prop_active_weeks`)—a theoretically plausible engagement signal—followed by submission counts and on-time and lead-time behaviour. The MPI's persistence (D4) and timeliness (D3) dimensions enter the top ten as incremental contributors; the standardised engagement composite (D1) is redundant with its raw constituent `prop_active_weeks` and therefore ranks last, so the engagement construct still dominates, but through the raw feature rather than the composite. A transformer/LSTM comparison is reported as ongoing design; the results here are for the classical learner estimated.")

# --- Table 3 ---
add("""| Feature | Perm. imp. | Mean \\|SHAP\\| | Type |
|---|---|---|---|
| mean_submit_delay | 0.199 | 0.154 | behavioural |
| n_submissions | 0.044 | 0.078 | behavioural |
| exam / max score | 0.013 | 0.054 | behavioural |
| D1 engagement (MPI) | 0.0038 | 0.048 | motivation |
| TMA / mean score | 0.004 | 0.031–0.039 | behavioural |
| D3 timeliness (MPI) | 0.0027 | 0.017 | motivation |""",
"""| Rank | Feature | Family | Perm. imp. (±SD) | Mean \\|SHAP\\| |
|---|---|---|---|---|
| 1 | prop_active_weeks | behavioural | 0.089 ± 0.004 | 0.132 |
| 2 | n_submissions | behavioural | 0.037 ± 0.002 | 0.071 |
| 3 | n_assessments | behavioural | 0.016 ± 0.002 | 0.079 |
| 4 | on_time_rate | behavioural | 0.0042 | 0.023 |
| 5 | mean_lead_days | behavioural | 0.0038 | 0.021 |
| 6 | n_activity_types | behavioural | 0.0032 | 0.012 |
| 7 | total_clicks | behavioural | 0.0029 | 0.044 |
| 8 | D4 persistence (MPI) | motivation | 0.0028 | 0.022 |
| 9 | D3 timeliness (MPI) | motivation | 0.0019 | 0.019 |
| 10 | MPI (composite) | motivation | 0.0005 | 0.005 |""")
add("**Table 3. Top features (permutation importance / mean |SHAP|).**",
"**Table 3. Leakage-safe drivers of course passing (Random Forest; permutation importance, 10 repeats; mean |SHAP|). No demographic feature enters the top ten.**")

# --- 5.5 text ---
add("For the final RF we computed group selection rate and true-positive rate (recall) by protected group (Table 5). For **disability**, the demographic-parity difference is 0.087, but the equalised-odds TPR gap is essentially zero (−0.001): the lower selection rate reflects genuine base-rate differences rather than unequal recall, so disabled students who actually pass are recalled almost identically. For **prior attempts**, the parity difference is larger (0.190) and the equalised-odds TPR gap is 0.047: repeat-attempt students who will pass are recalled approximately 4.7 pp less often—a modest but real violation that motivates compound-group reweighting or group-aware thresholds.",
"For the leakage-safe RF we computed, per protected group, the selection rate, true- and false-positive rates, positive predictive value, and recall on the at-risk (Fail/Withdrawn) class (Table 5). For **disability**, the demographic-parity difference is 0.079, but both error rates are close (ΔTPR = −0.015, ΔFPR = +0.013), giving an equalised-odds gap of just 0.015: the model satisfies equalised odds, and the parity gap reflects a genuine base-rate difference rather than differential error. For **prior attempts**, parity differs more (0.187) and the gap is TPR-driven (ΔTPR = +0.077, ΔFPR = +0.011; equalised-odds gap 0.077): repeat-attempt students who actually pass are missed 7.7 pp more often and are over-flagged as at-risk. We then mitigated this gap: compound-group reweighting barely moved it (0.077 to 0.072), but a group-aware decision threshold (0.30 for prior-attempt students, 0.50 otherwise) achieved equal opportunity (ΔTPR = −0.003) and cut the equalised-odds gap to 0.047, at a cost of only 0.2 pp accuracy (0.915 to 0.913) and no change in AUC (0.969).")

# --- Table 5 ---
add("""| Group | n | Selection rate | TPR (recall) |
|---|---|---|---|
| Disability = Yes | 794 | 0.417 | 0.968 |
| Disability = No | 7,355 | 0.504 | 0.967 |
| Prior attempts > 0 | 1,051 | 0.330 | 0.923 |
| Prior attempts = 0 | 7,098 | 0.520 | 0.971 |""",
"""| Group | n | Sel. rate | TPR | FPR | PPV | Fail-class recall |
|---|---|---|---|---|---|---|
| Disability = Yes | 794 | 0.440 | 0.964 | 0.105 | 0.854 | 0.895 |
| Disability = No | 7,355 | 0.518 | 0.950 | 0.118 | 0.882 | 0.882 |
| Prior attempts > 0 | 1,051 | 0.347 | 0.880 | 0.108 | 0.786 | 0.892 |
| Prior attempts = 0 | 7,098 | 0.535 | 0.957 | 0.119 | 0.888 | 0.882 |""")
add("**Table 5. Group fairness on the test set.**",
"**Table 5. Per-group equalised-odds diagnostics (leakage-safe RF; positive class = Pass).**")

# --- 5.6 text + table ---
add("Comparing otherwise-identical models without versus with the MPI dimensions (Table 6), the MPI delivers a meaningful **+0.029 AUC and +0.028 macro-F1 lift on the transparent logistic baseline**, but a negligible +0.0006 AUC on the Random Forest, which already saturates from raw scores and timing. The four-class RF reaches accuracy 0.742 and macro-F1 0.680. The MPI's value, therefore, lies in being an interpretable, linear-model-friendly motivation signal and in *profiling*—Table 2 separates Distinction/Pass from Fail/Withdrawn on engagement and timeliness—rather than in boosting an already-strong ensemble.",
"Comparing logistic models without versus with the five MPI dimensions under 5×5-fold stratified cross-validation (Table 6), the MPI raises mean ROC-AUC from 0.936 to 0.949—a paired increment of **+0.013** (t(24) = 101, p < 0.001; bootstrap 95% CI [0.013, 0.014]): small but highly reliable. On the Random Forest the lift is negligible, as the ensemble already saturates from raw behaviour. The MPI's value therefore lies in being an interpretable, linear-model-friendly motivation signal and in *profiling*—Table 2 separates Distinction/Pass from Fail/Withdrawn on engagement and timeliness—rather than in boosting an already-strong ensemble.")
add("""| Model | AUC (no MPI) | AUC (+MPI) | Macro-F1 (no MPI) | Macro-F1 (+MPI) |
|---|---|---|---|---|
| Logistic regression | 0.8996 | **0.9284** | 0.822 | **0.850** |
| Random Forest | 0.9829 | 0.9835 | 0.945 | 0.945 |""",
"""| Logistic model (5×5-fold CV) | Mean ROC-AUC ± SD |
|---|---|
| Without MPI | 0.936 ± 0.003 |
| With MPI | 0.949 ± 0.003 |
| Paired Δ | +0.013 (95% CI [0.013, 0.014]; p < 0.001) |""")
add("**Table 6. MPI predictive lift.**","**Table 6. Cross-validated MPI predictive lift (logistic regression).**")

# --- 5.7 ---
add("Class imbalance was handled through stratified splits and balanced class weights; leakage was controlled by excluding unregistration/withdrawal fields and, for RQ2, all full-course aggregates. The most defensible claims are the week-level early-prediction curve (RQ2) and the logistic-model MPI lift (RQ4); the RF MPI lift is reported as effectively null. All relationships are observational; no causal claims are made.",
"Class imbalance was handled through stratified splits and balanced class weights; leakage was controlled by excluding unregistration, withdrawal, and full-course grade aggregates. The most defensible claims are the week-level early-prediction curve (RQ2) and the cross-validated MPI lift (RQ4). The negative resource-diversity association is not a pooling artefact: it holds within both STEM (r = −0.133) and social-science (r = −0.150) modules. All relationships are observational; no causal claims are made.")

# --- Table 7 verdicts ---
add("| P1 — Engagement consistency → lower risk | D1 r = +0.417; 4th by SHAP | Supported |",
"| P1 — Engagement consistency → lower risk | D1 r = +0.417; engagement is the top leakage-safe driver | Supported |")
add("| P5 — Composite MPI beyond best single dimension | composite r = +0.131 < D1; +0.029 AUC (logistic), ≈0 (RF) | Not supported as equal-weight composite |",
"| P5 — Composite MPI beyond best single dimension | composite r = +0.131 < D1, but +0.013 AUC over a fair baseline (CV, p < 0.001) | Incremental, not as an equal-weight composite |")
add("| P6 — Validity holds across subgroups under fairness constraints | §5.5 audit + mitigation | Partially supported |",
"| P6 — Validity holds across subgroups under fairness constraints | equalised odds holds for disability (gap 0.015); prior-attempts gap 0.077 → equal opportunity via group-aware threshold | Partially supported |")

# --- 6.1 ---
add("Within the MPI, *engagement consistency* is the strongest single dimension (r = +0.417 with success; fourth by SHAP), directly supporting the SDT/SRL premise that regular, planful effort is the behavioural signature of competent self-regulation (Pintrich, 2004; Zimmerman, 2000) and echoing trajectory-based engagement research (Saqr & López-Pernas, 2021; You, 2016).",
"Within the MPI, *engagement consistency* is the strongest signal (r = +0.417 with success); in the leakage-safe model the engagement construct is the single top driver, entering through the proportion of active weeks while the standardised composite proves redundant with it. This directly supports the SDT/SRL premise that regular, planful effort is the behavioural signature of competent self-regulation (Pintrich, 2004; Zimmerman, 2000), echoing trajectory-based engagement research (Saqr & López-Pernas, 2021; You, 2016).")

# --- 6.2 ---
add("The MPI produced a meaningful, interpretable lift on the transparent logistic model (+0.029 AUC, +0.028 macro-F1) but negligible lift on the Random Forest, which already saturates from raw scores and timing.",
"The MPI produced a small but statistically reliable cross-validated lift on the transparent logistic model (+0.013 AUC, p < 0.001) but negligible lift on the Random Forest, which already saturates from raw behaviour.")

# --- 6.3 ---
add("The fairness audit then shows that accuracy and equity need not conflict uniformly: the model is essentially recall-fair for students with declared disabilities (equalised-odds TPR gap ≈ 0), so their lower selection rate reflects genuine base-rate differences rather than discriminatory error. For repeat-attempt students, however, a modest equalised-odds gap (approximately 4.7 pp) means those who would pass are under-identified—precisely the population an early-warning system should not fail. This vindicates the recommendation to treat protected attributes as objects of audit rather than primary decision drivers (Hutt et al., 2019; Riazy et al., 2020) and identifies compound-group reweighting or group-aware thresholds as the targeted next step.",
"The fairness audit then shows that accuracy and equity need not conflict uniformly: the model satisfies equalised odds for students with declared disabilities (gap 0.015), so their lower selection rate reflects genuine base-rate differences rather than discriminatory error. For repeat-attempt students, however, a larger TPR-driven gap (7.7 pp) means those who would pass are under-identified—precisely the population an early-warning system should not fail; a group-aware decision threshold restores equal opportunity for this group and reduces the equalised-odds gap (0.077 to 0.047) for a 0.2 pp accuracy cost. This vindicates treating protected attributes as objects of audit and targeted mitigation rather than primary decision drivers (Hutt et al., 2019; Riazy et al., 2020).")

# --- 6.5 ---
add("Two MPI dimensions underperformed and the equal-weight composite is suboptimal; the full-course Random Forest is partly inflated by submission-delay leakage and is reported only alongside the deployable week-cumulative model. Finally, the deep/transformer comparison (RQ1) and the reweighting mitigation (RQ3) are specified but not yet estimated, and constitute the immediate empirical agenda.",
"Two MPI dimensions underperformed and the equal-weight composite is suboptimal, adding value only incrementally within a model rather than as a standalone index. Finally, the deep/transformer comparison (RQ1) is specified but not yet estimated, constituting the immediate empirical agenda.")

# --- 7 conclusions ---
add("First (RQ1), risk is legible in behaviour, not demographics: no demographic attribute enters the top interpretable drivers, while submission behaviour and engagement consistency dominate, and the MPI's engagement dimension ranks among the leading interpretable signals—so explainable, motivation-informed early warning is feasible.",
"First (RQ1), risk is legible in behaviour, not demographics: in a leakage-safe model no demographic attribute enters the top ten drivers, while engagement behaviour (proportion of active weeks) is the single strongest signal and the MPI timeliness and persistence dimensions contribute incrementally—so explainable, motivation-informed early warning is feasible.")
add("Third (RQ3), fairness and accuracy can largely coexist: the model is recall-fair for students with disabilities, while a modest equalised-odds gap for repeat-attempt students identifies a specific, addressable target that compound-group mitigation reduces. Fourth (RQ4), a theory-grounded index adds real value where it matters—an interpretable +0.029 AUC lift on a transparent model and clean separation of at-risk profiles—while two of its four dimensions (resource diversity, persistence-after-difficulty) did not validate as theorised and must be re-specified; the contribution is a *calibrated* construct, not a universally superior one.",
"Third (RQ3), fairness and accuracy can largely coexist: the model satisfies equalised odds for students with disabilities, while a TPR-driven gap for repeat-attempt students is removed by a group-aware threshold that restores equal opportunity at negligible accuracy cost. Fourth (RQ4), a theory-grounded index adds real value where it matters—a small but reliable +0.013 cross-validated AUC lift on a transparent model and clean separation of at-risk profiles—while two of its four dimensions (resource diversity, persistence-after-difficulty) did not validate as theorised and must be re-specified; the contribution is a *calibrated* construct, not a universally superior one.")
add("Future work will estimate the deep and transformer learners against the classical baseline under a common explainability protocol, implement compound-group reweighting for repeat-attempt learners, redefine the diversity and persistence dimensions (including finer post-setback windows), and test cross-institutional and post-pandemic transferability.",
"Future work will estimate the deep and transformer learners against the classical baseline under a common explainability protocol, extend the group-aware fairness mitigation, redefine the diversity and persistence dimensions (including finer post-setback windows), and test cross-institutional and post-pandemic transferability.")

matched=0; missed=[]
for o,n in pairs:
    if o in t:
        t=t.replace(o,n,1); matched+=1
    else:
        missed.append(o[:75])
open(p,'w',encoding='utf-8').write(t)
body,_,refs=t.partition('## References')
print('matched',matched,'of',len(pairs))
print('MISSED:')
for m in missed: print('  -',repr(m))
print('Body excl refs now:',len(re.findall(r'\S+',body)),'words')
