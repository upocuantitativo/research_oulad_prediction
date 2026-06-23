/* Embedded study results for the OULAD MPI decision-support dashboard.
   Generated from scripts_results/results*.json and tab3_leakage_safe_importance.csv.
   All numbers are real outputs of the reproducible pipeline (seed = 42). */
window.DATA = {
  n_total: 32593,
  n_mpi: 28563,
  adverse_rate: 52.8,
  auc_leakage_safe: 0.969,
  final_result: { Pass: 37.93, Withdrawn: 31.16, Fail: 21.64, Distinction: 9.28 },
  final_counts: { Pass: 12361, Withdrawn: 10156, Fail: 7052, Distinction: 3024 },

  early: {
    weeks: [4, 8, 12, 16, 20, 24, 28, 32],
    auc:  [0.678, 0.7831, 0.8316, 0.8709, 0.9065, 0.9304, 0.9414, 0.9557],
    n: 28497, week90: 20, week_triage: 16, max: 0.9557
  },

  mpi: {
    dims: ["Engagement (D1)", "Diversity (D2)", "Timeliness (D3)", "Persistence (D4)"],
    outcomes: {
      Distinction: [0.366, -0.228, 0.223, -0.080],
      Pass:        [0.181, -0.105, 0.098,  0.013],
      Fail:        [-0.246, 0.131, -0.117, 0.048],
      Withdrawn:   [-0.261, 0.170, -0.169, -0.036]
    },
    corr_passed: { D1: 0.4172, D2: -0.1396, D3: 0.1637, D4: -0.006, MPI: 0.1306 }
  },

  drivers: [
    { f: "prop_active_weeks", fam: "behavioural", shap: 0.13243, perm: 0.08916 },
    { f: "n_assessments",     fam: "behavioural", shap: 0.07912, perm: 0.01603 },
    { f: "n_submissions",     fam: "behavioural", shap: 0.07136, perm: 0.03729 },
    { f: "total_clicks",      fam: "behavioural", shap: 0.04347, perm: 0.00288 },
    { f: "D1 engagement",     fam: "MPI",         shap: 0.03718, perm: -0.00075 },
    { f: "consistency_inv_cv",fam: "behavioural", shap: 0.02528, perm: 0.00018 },
    { f: "on_time_rate",      fam: "behavioural", shap: 0.02340, perm: 0.00421 },
    { f: "D4 persistence",    fam: "MPI",         shap: 0.02199, perm: 0.00281 },
    { f: "mean_lead_days",    fam: "behavioural", shap: 0.02117, perm: 0.00378 },
    { f: "D3 timeliness",     fam: "MPI",         shap: 0.01923, perm: 0.00194 },
    { f: "n_activity_types",  fam: "behavioural", shap: 0.01191, perm: 0.00320 },
    { f: "resource_entropy",  fam: "behavioural", shap: 0.00915, perm: -0.00027 }
  ],

  cv: { no_mpi: 0.9357, with_mpi: 0.9490, lift: 0.0132, p: "< 0.001" },

  fairness: {
    disability: {
      dis: { label: "Disability = Yes", n: 794,  sel: 0.4169, tpr: 0.9676 },
      adv: { label: "Disability = No",  n: 7355, sel: 0.5040, tpr: 0.9666 },
      dp: 0.0871, eo: 0.001
    },
    prevattempts: {
      dis: { label: "Prior attempts > 0", n: 1051, sel: 0.3302, tpr: 0.9233 },
      adv: { label: "Prior attempts = 0", n: 7098, sel: 0.5200, tpr: 0.9707 },
      dp: 0.1898, eo: 0.0474
    }
  },

  mitigation: {
    method: "Group-aware threshold (0.30 for prior-attempt students, 0.50 otherwise)",
    before: { eo: 0.077, dp: 0.1874, tpr_dis: 0.8804, tpr_adv: 0.9574 },
    after:  { eo: 0.047, dp: 0.1227, tpr_dis: 0.9601, tpr_adv: 0.9574 },
    acc_before: 0.9152, acc_after: 0.9132, auc: 0.9691
  },

  disparity: {
    "Highest education": [
      ["No formal quals", 0.7032], ["Lower than A Level", 0.6115],
      ["A Level / equiv.", 0.4797], ["HE qualification", 0.4383],
      ["Postgraduate", 0.3450]
    ],
    "Deprivation (IMD decile)": [
      ["0-10 (most)", 0.6484], ["10-20", 0.6138], ["20-30", 0.5925],
      ["30-40", 0.5309], ["40-50", 0.5341], ["50-60", 0.5122],
      ["60-70", 0.4809], ["70-80", 0.4849], ["80-90", 0.4594],
      ["90-100 (least)", 0.4247]
    ]
  }
};
