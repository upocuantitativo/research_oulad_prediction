"""
04_reviewer_addendum.py
Reviewer revision recomputations (REAL numbers, seed=42 everywhere):
 1) Leakage-safe RF feature importance (perm 10 reps + mean|SHAP|) -> new Table 3
 2) Full equalized-odds fairness per group, framed on the AT-RISK (fail/withdraw) class
 3) Significance of MPI AUC lift via repeated stratified k-fold + paired test/bootstrap CI
 4) Mitigation: compound-group reweighting on leakage-safe RF, gap before/after
 Optional: per-domain (STEM vs social) sign of D2 correlation
Outputs CSVs + JSON into scripts_results/.
"""
import numpy as np, pandas as pd, os, json, warnings
warnings.filterwarnings("ignore")
from sklearn.model_selection import train_test_split, RepeatedStratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import (accuracy_score, f1_score, roc_auc_score,
                             confusion_matrix, recall_score)
from sklearn.inspection import permutation_importance
from scipy import stats

SEED = 42
np.random.seed(SEED)
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(BASE, "scripts_results")
KEY  = ["code_module", "code_presentation", "id_student"]
R = {}

# ---------------- load & merge ----------------
m = pd.read_csv(os.path.join(BASE, "oulad_master.csv"))
m["imd_band"] = m["imd_band"].astype(str).str.replace("%", "", regex=False).str.strip()
m.loc[m["imd_band"] == "nan", "imd_band"] = np.nan
mpi = pd.read_csv(os.path.join(OUT, "mpi_features.csv"))
df = m.merge(mpi, on=KEY, how="left")

# pass label (1 = Pass/Distinction)
y_pass = df["passed"].astype(int)
# at-risk label (positive = Fail OR Withdrawn) -- reframed for fairness
y_risk = ((df["final_result"] == "Fail") | (df["final_result"] == "Withdrawn")).astype(int)

# ---------------- LEAKAGE-SAFE FEATURE SET ----------------
# DROPPED (encode the full-course outcome): mean_submit_delay, date_unregistration,
#   withdrew, final_result, outcome_ordinal, AND full-course grade aggregates
#   (mean/median/std/min/max_score, mean_score_TMA/CMA/Exam) which define pass/fail.
# KEPT leakage-safe behavioural: volume/cadence of activity + MPI dimensions.
behav_safe = ["n_submissions", "n_banked",
              "total_clicks", "prop_active_weeks", "consistency_inv_cv",
              "resource_entropy", "n_activity_types",
              "on_time_rate", "mean_lead_days", "n_assess"]
mpidims    = ["D1_engagement", "D2_diversity", "D3_timeliness", "D4_persistence", "MPI"]
demo       = ["num_of_prev_attempts", "studied_credits", "age_midpoint",
              "education_level", "imd_numeric"]
FEATS = behav_safe + mpidims + demo
R["leakage_dropped"] = ["mean_submit_delay","date_unregistration","withdrew",
    "final_result","outcome_ordinal","mean_score","median_score","std_score",
    "min_score","max_score","mean_score_TMA","mean_score_CMA","mean_score_Exam"]
R["features_kept"] = FEATS

def build_X(frame, cols):
    X = frame[cols].apply(pd.to_numeric, errors="coerce")
    return X.fillna(X.median())

X = build_X(df, FEATS)

# tag each feature as behavioural / MPI / demographic for the dominance question
def fam(c):
    if c in demo: return "demographic"
    if c in mpidims: return "MPI"
    return "behavioural"

# =================================================================
# 1) LEAKAGE-SAFE RF  + permutation importance (10 reps) + mean|SHAP|
# =================================================================
Xtr, Xte, ytr, yte = train_test_split(X, y_pass, test_size=0.25,
                                      stratify=y_pass, random_state=SEED)
rf = RandomForestClassifier(n_estimators=400, class_weight="balanced",
                            random_state=SEED, n_jobs=-1).fit(Xtr, ytr)
pp = rf.predict_proba(Xte)[:, 1]; pr = (pp >= 0.5).astype(int)
R["leakage_safe_RF_perf"] = dict(
    acc=round(accuracy_score(yte, pr), 4),
    f1=round(f1_score(yte, pr, average="macro"), 4),
    auc=round(roc_auc_score(yte, pp), 4))

perm = permutation_importance(rf, Xte, yte, n_repeats=10,
                              random_state=SEED, n_jobs=-1)
perm_mean = pd.Series(perm.importances_mean, index=FEATS)
perm_sd   = pd.Series(perm.importances_std,  index=FEATS)

# SHAP
shap_imp = None
try:
    import shap
    Xs = Xte.sample(min(1500, len(Xte)), random_state=SEED)
    expl = shap.TreeExplainer(rf)
    sv = expl.shap_values(Xs)
    arr = sv[1] if isinstance(sv, list) else (sv[..., 1] if sv.ndim == 3 else sv)
    shap_imp = pd.Series(np.abs(arr).mean(0), index=FEATS)
    R["shap_ok"] = True
except Exception as e:
    R["shap_ok"] = False; R["shap_err"] = str(e)

tab3 = pd.DataFrame({"family": [fam(c) for c in FEATS],
                     "perm_importance": perm_mean.round(5),
                     "perm_sd": perm_sd.round(5)})
if shap_imp is not None:
    tab3["mean_abs_shap"] = shap_imp.round(5)
tab3 = tab3.sort_values("perm_importance", ascending=False)
tab3.to_csv(os.path.join(OUT, "tab3_leakage_safe_importance.csv"))
R["table3_top10"] = tab3.head(10).reset_index().rename(columns={"index":"feature"}).to_dict("records")

# (a) behavioural vs demographic dominance, (b) D1 rank
ranked = list(tab3.index)
R["D1_rank_perm"] = ranked.index("D1_engagement") + 1
top10_fams = tab3.head(10)["family"].tolist()
R["top10_family_counts"] = {f: top10_fams.count(f) for f in ["behavioural","MPI","demographic"]}
R["top_feature"] = ranked[0]
R["top_feature_family"] = fam(ranked[0])

# =================================================================
# 2) FULL EQUALIZED ODDS  (pass-model predictions, two framings)
#    positive (pass) for TPR/FPR/PPV; failure-class recall reframed.
# =================================================================
te_idx = Xte.index
fdf = pd.DataFrame({"y_pass": yte.values, "pred_pass": pr}, index=te_idx)
fdf["disability"] = df.loc[te_idx, "disability"].values
fdf["prev"] = (df.loc[te_idx, "num_of_prev_attempts"] > 0).astype(int).values
# at-risk view: positive = fail/withdraw  => y_risk = 1-y_pass ; pred_risk = 1-pred_pass
fdf["y_risk"] = 1 - fdf["y_pass"]
fdf["pred_risk"] = 1 - fdf["pred_pass"]

def rates(sub):
    """return TPR,FPR,PPV for the PASS positive class + recall on FAILURE class."""
    cm = confusion_matrix(sub["y_pass"], sub["pred_pass"], labels=[0,1])
    tn, fp, fn, tp = cm.ravel()
    tpr = tp/(tp+fn) if (tp+fn) else np.nan          # recall pass
    fpr = fp/(fp+tn) if (fp+tn) else np.nan
    ppv = tp/(tp+fp) if (tp+fp) else np.nan
    sel = sub["pred_pass"].mean()
    fail_recall = recall_score(sub["y_risk"], sub["pred_risk"]) if sub["y_risk"].nunique()>1 else np.nan
    return dict(n=int(len(sub)), selection_rate=round(float(sel),4),
                TPR_pass=round(float(tpr),4), FPR_pass=round(float(fpr),4),
                PPV_pass=round(float(ppv),4),
                failure_class_recall=round(float(fail_recall),4))

def fairness_block(col, dis_val, adv_val):
    d = rates(fdf[fdf[col]==dis_val]); a = rates(fdf[fdf[col]==adv_val])
    dTPR = a["TPR_pass"]-d["TPR_pass"]
    dFPR = a["FPR_pass"]-d["FPR_pass"]
    dp   = a["selection_rate"]-d["selection_rate"]
    eo_gap = max(abs(dTPR), abs(dFPR))
    return dict(disadvantaged=d, advantaged=a,
                demographic_parity_diff=round(dp,4),
                equal_opportunity_dTPR=round(dTPR,4),
                dFPR=round(dFPR,4),
                equalized_odds_gap=round(eo_gap,4))

R["fairness_disability"]   = fairness_block("disability", "Y", "N")
R["fairness_prevattempts"] = fairness_block("prev", 1, 0)

# =================================================================
# 3) SIGNIFICANCE OF MPI LIFT  (LogReg, repeated stratified 5x5 CV)
# =================================================================
# leakage-safe behavioural+demo WITHOUT vs WITH MPI dimensions, same folds.
base_cols = behav_safe + demo
X_no  = build_X(df, base_cols)
X_yes = build_X(df, base_cols + mpidims)
yv = y_pass.values
rskf = RepeatedStratifiedKFold(n_splits=5, n_repeats=5, random_state=SEED)
auc_no, auc_yes = [], []
def lr(): return Pipeline([("s",StandardScaler()),
            ("c",LogisticRegression(max_iter=2000,class_weight="balanced",random_state=SEED))])
for tr,te in rskf.split(X_no, yv):
    a = lr().fit(X_no.iloc[tr], yv[tr]).predict_proba(X_no.iloc[te])[:,1]
    b = lr().fit(X_yes.iloc[tr], yv[tr]).predict_proba(X_yes.iloc[te])[:,1]
    auc_no.append(roc_auc_score(yv[te], a))
    auc_yes.append(roc_auc_score(yv[te], b))
auc_no=np.array(auc_no); auc_yes=np.array(auc_yes); diff=auc_yes-auc_no
t_stat,p_val = stats.ttest_rel(auc_yes, auc_no)
# bootstrap CI on mean paired diff across the 25 folds
rng=np.random.default_rng(SEED)
boot=[rng.choice(diff,size=len(diff),replace=True).mean() for _ in range(10000)]
ci=(float(np.percentile(boot,2.5)), float(np.percentile(boot,97.5)))
R["mpi_cv_significance"]=dict(
    n_folds=len(diff),
    auc_without_mpi=dict(mean=round(auc_no.mean(),4), sd=round(auc_no.std(ddof=1),4)),
    auc_with_mpi=dict(mean=round(auc_yes.mean(),4), sd=round(auc_yes.std(ddof=1),4)),
    mean_delta=round(float(diff.mean()),4),
    paired_t=round(float(t_stat),3), p_value=float(p_val),
    boot95_CI_delta=[round(ci[0],4),round(ci[1],4)],
    reliable=bool(p_val<0.05 and ci[0]>0))
pd.DataFrame({"fold":range(len(diff)),"auc_no_mpi":auc_no,
             "auc_with_mpi":auc_yes,"delta":diff}).round(5).to_csv(
             os.path.join(OUT,"tab_mpi_cv_auc.csv"),index=False)

# =================================================================
# 4) MITIGATION  -- compound-group reweighting on leakage-safe RF
#    target: shrink prior-attempts equalized-odds gap.
# =================================================================
# compound group = (prev_attempts>0) x (true pass label) on TRAIN only.
prev_tr = (df.loc[Xtr.index,"num_of_prev_attempts"]>0).astype(int).values
# reweight so each (group x class) cell has equal total mass (classic EO-ish reweighting)
wdf = pd.DataFrame({"g":prev_tr,"yy":ytr.values})
cell = wdf.groupby(["g","yy"]).size()
n = len(wdf)
w = np.array([ n/(len(cell)*cell.loc[(g,c)]) for g,c in zip(wdf.g,wdf.yy) ])
rf_mit = RandomForestClassifier(n_estimators=400, random_state=SEED,
                                n_jobs=-1).fit(Xtr, ytr, sample_weight=w)
pp_m = rf_mit.predict_proba(Xte)[:,1]; pr_m=(pp_m>=0.5).astype(int)

def eo_gap_prev(pred_pass):
    f=pd.DataFrame({"y_pass":yte.values,"pred_pass":pred_pass},index=te_idx)
    f["prev"]=(df.loc[te_idx,"num_of_prev_attempts"]>0).astype(int).values
    def rr(sub):
        cm=confusion_matrix(sub["y_pass"],sub["pred_pass"],labels=[0,1]); tn,fp,fn,tp=cm.ravel()
        return (tp/(tp+fn) if tp+fn else np.nan, fp/(fp+tn) if fp+tn else np.nan,
                sub["pred_pass"].mean())
    dT,dF,ds=rr(f[f.prev==1]); aT,aF,asr=rr(f[f.prev==0])
    return dict(dTPR=round(aT-dT,4), dFPR=round(aF-dF,4),
                eo_gap=round(max(abs(aT-dT),abs(aF-dF)),4),
                dp_diff=round(asr-ds,4))

before = eo_gap_prev(pr)
after  = eo_gap_prev(pr_m)
R["mitigation_prevattempts"]=dict(
    method="compound (prev_attempts x class) reweighting on leakage-safe RF",
    before=before, after=after,
    acc_before=round(accuracy_score(yte,pr),4), acc_after=round(accuracy_score(yte,pr_m),4),
    auc_before=round(roc_auc_score(yte,pp),4),  auc_after=round(roc_auc_score(yte,pp_m),4))

# =================================================================
# OPTIONAL: per-domain sign of D2 (resource diversity) correlation
# =================================================================
STEM = {"AAA","BBB","CCC","DDD","EEE","FFF","GGG"}  # placeholder; refine by known OULAD domains
# Known OULAD: STEM modules = CCC,DDD,EEE,FFF,GGG ; Social Science = AAA,BBB
stem_modules = {"CCC","DDD","EEE","FFF","GGG"}
soc_modules  = {"AAA","BBB"}
sub = df.dropna(subset=["D2_diversity"]).copy()
sub["domain"]=np.where(sub["code_module"].isin(stem_modules),"STEM",
               np.where(sub["code_module"].isin(soc_modules),"Social","Other"))
d2dom={}
for dom,g in sub.groupby("domain"):
    if g["passed"].nunique()>1:
        r=float(np.corrcoef(g["D2_diversity"], g["passed"])[0,1])
        d2dom[dom]=dict(n=int(len(g)), r_D2_passed=round(r,4))
d2dom["pooled"]=dict(n=int(len(sub)),
                     r_D2_passed=round(float(np.corrcoef(sub["D2_diversity"],sub["passed"])[0,1]),4))
R["D2_by_domain"]=d2dom

json.dump(R, open(os.path.join(OUT,"results_addendum.json"),"w"), indent=2, default=str)
print("=== TABLE 3 (leakage-safe) top10 ===")
print(tab3.head(10).to_string())
print("\n=== FAIRNESS disability ==="); print(json.dumps(R["fairness_disability"],indent=2))
print("\n=== FAIRNESS prev attempts ==="); print(json.dumps(R["fairness_prevattempts"],indent=2))
print("\n=== MPI CV significance ==="); print(json.dumps(R["mpi_cv_significance"],indent=2))
print("\n=== MITIGATION ==="); print(json.dumps(R["mitigation_prevattempts"],indent=2))
print("\n=== D2 by domain ==="); print(json.dumps(R["D2_by_domain"],indent=2))
print("\nleakage_safe RF perf:", R["leakage_safe_RF_perf"])
print("D1 rank:", R["D1_rank_perm"], "top10 families:", R["top10_family_counts"])
