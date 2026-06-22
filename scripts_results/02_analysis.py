"""
02_analysis.py  -- descriptives, predictive modeling, XAI, fairness.
Reproducible: seed=42 everywhere. Leakage controls: date_unregistration & withdrew
excluded as features. Outputs CSV tables to scripts_results/.
"""
import numpy as np, pandas as pd, os, json, warnings
warnings.filterwarnings("ignore")
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_predict
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.metrics import (accuracy_score, f1_score, roc_auc_score,
                             roc_auc_score as auc, confusion_matrix, recall_score)
from sklearn.inspection import permutation_importance
SEED=42; np.random.seed(SEED)
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT=os.path.join(BASE,"scripts_results")
KEY=["code_module","code_presentation","id_student"]
R={}

m=pd.read_csv(os.path.join(BASE,"oulad_master.csv"))
# normalize imd_band labels (10-20 vs 10-20%)
m["imd_band"]=m["imd_band"].astype(str).str.replace("%","",regex=False).str.strip()
m.loc[m["imd_band"]=="nan","imd_band"]=np.nan

# ============ 1. DESCRIPTIVES ============
fr=m["final_result"].value_counts()
frp=(fr/len(m)*100).round(2)
desc=pd.DataFrame({"count":fr,"pct":frp})
desc.to_csv(os.path.join(OUT,"tab_final_result.csv"))
R["n_total"]=int(len(m))
R["final_result"]={k:[int(fr[k]),float(frp[k])] for k in fr.index}

m["failed_or_withdrew"]=((m["final_result"]=="Fail")|(m["final_result"]=="Withdrawn")).astype(int)
def grp_rates(col):
    g=m.groupby(col).agg(n=("failed_or_withdrew","size"),
                         fail_wd_rate=("failed_or_withdrew","mean"),
                         withdraw_rate=("withdrew","mean")).round(4)
    return g
gap={}
for col in ["imd_band","disability","highest_education","age_band","num_of_prev_attempts"]:
    g=grp_rates(col); g.to_csv(os.path.join(OUT,f"tab_rate_{col}.csv"))
    gap[col]=float(g["fail_wd_rate"].max()-g["fail_wd_rate"].min())
R["disparity_gap_failwd"]=gap

# ============ 2. MPI correlations ============
mpi=pd.read_csv(os.path.join(OUT,"mpi_features.csv"))
df=m.merge(mpi,on=KEY,how="left")
dims=["D1_engagement","D2_diversity","D3_timeliness","D4_persistence","MPI"]
mpi_by_fr=df.groupby("final_result")[dims].mean().round(3)
mpi_by_fr.to_csv(os.path.join(OUT,"tab_mpi_by_final_result.csv"))
corr={}
sub=df.dropna(subset=["MPI"])
for d in dims:
    corr[d]=float(np.corrcoef(sub[d].fillna(0), sub["passed"])[0,1])
R["mpi_corr_passed"]={k:round(v,4) for k,v in corr.items()}
R["mpi_by_final_result"]=mpi_by_fr.to_dict()
R["n_mpi_matched"]=int(df["MPI"].notna().sum())

# ============ 3+4. PREDICTIVE MODELING + XAI ============
# behavioural features from master (no leakage): scores, submissions, delays
behav=["mean_score","median_score","std_score","min_score","max_score",
       "n_submissions","n_banked","mean_submit_delay",
       "mean_score_TMA","mean_score_CMA","mean_score_Exam"]
demo=["num_of_prev_attempts","studied_credits","age_midpoint","education_level","imd_numeric"]
mpidims=["D1_engagement","D2_diversity","D3_timeliness","D4_persistence","MPI"]
# LEAKAGE CONTROL: exclude date_unregistration, withdrew, final_result, outcome_ordinal
df_model=df.copy()
y=df_model["passed"].astype(int)

def build_X(cols):
    X=df_model[cols].apply(pd.to_numeric,errors="coerce")
    return X.fillna(X.median())

def run_models(cols, tag):
    X=build_X(cols)
    Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=0.25,stratify=y,random_state=SEED)
    res={}
    # Logistic baseline
    lr=Pipeline([("s",StandardScaler()),("c",LogisticRegression(max_iter=2000,
                  class_weight="balanced",random_state=SEED))]).fit(Xtr,ytr)
    p=lr.predict(Xte); pp=lr.predict_proba(Xte)[:,1]
    res["LogReg"]=dict(acc=accuracy_score(yte,p),f1=f1_score(yte,p,average="macro"),
                       auc=roc_auc_score(yte,pp))
    # Random Forest
    rf=RandomForestClassifier(n_estimators=400,class_weight="balanced",
                              random_state=SEED,n_jobs=-1).fit(Xtr,ytr)
    p=rf.predict(Xte); pp=rf.predict_proba(Xte)[:,1]
    res["RF"]=dict(acc=accuracy_score(yte,p),f1=f1_score(yte,p,average="macro"),
                   auc=roc_auc_score(yte,pp))
    return res, rf, (Xtr,Xte,ytr,yte), cols

# WITHOUT MPI
res_no,_,_,_=run_models(behav+demo,"no_mpi")
# WITH MPI
res_yes,rf_final,split,cols_final=run_models(behav+demo+mpidims,"with_mpi")
R["model_without_mpi"]=res_no
R["model_with_mpi"]=res_yes
R["mpi_lift_auc_RF"]=round(res_yes["RF"]["auc"]-res_no["RF"]["auc"],4)
R["mpi_lift_f1_RF"]=round(res_yes["RF"]["f1"]-res_no["RF"]["f1"],4)

# 4-class
y4=df_model["outcome_ordinal"].astype(int)
X4=build_X(behav+demo+mpidims)
Xtr,Xte,ytr,yte=train_test_split(X4,y4,test_size=0.25,stratify=y4,random_state=SEED)
rf4=RandomForestClassifier(n_estimators=400,class_weight="balanced",random_state=SEED,n_jobs=-1).fit(Xtr,ytr)
p4=rf4.predict(Xte)
R["model_4class_RF"]=dict(acc=accuracy_score(yte,p4),f1=f1_score(yte,p4,average="macro"))

# XAI: permutation importance + RF impurity (with-MPI model)
Xtr,Xte,ytr,yte=split
imp=pd.Series(rf_final.feature_importances_,index=cols_final).sort_values(ascending=False)
perm=permutation_importance(rf_final,Xte,yte,n_repeats=10,random_state=SEED,n_jobs=-1)
perms=pd.Series(perm.importances_mean,index=cols_final).sort_values(ascending=False)
impdf=pd.DataFrame({"rf_impurity":imp,"perm_importance":perms}).sort_values("perm_importance",ascending=False)
impdf.round(5).to_csv(os.path.join(OUT,"tab_feature_importance.csv"))
R["top10_perm_importance"]=perms.head(10).round(5).to_dict()
R["top10_impurity"]=imp.head(10).round(5).to_dict()

# SHAP global (sample for speed)
try:
    import shap
    Xs=Xte.sample(min(1500,len(Xte)),random_state=SEED)
    expl=shap.TreeExplainer(rf_final)
    sv=expl.shap_values(Xs)
    arr=sv[1] if isinstance(sv,list) else (sv[...,1] if sv.ndim==3 else sv)
    shap_imp=pd.Series(np.abs(arr).mean(0),index=cols_final).sort_values(ascending=False)
    shap_imp.round(5).to_csv(os.path.join(OUT,"tab_shap_importance.csv"))
    R["top10_shap"]=shap_imp.head(10).round(5).to_dict()
    R["shap_ok"]=True
except Exception as e:
    R["shap_ok"]=False; R["shap_err"]=str(e)

# ============ 6. FAIRNESS ============
proba=rf_final.predict_proba(Xte)[:,1]; pred=(proba>=0.5).astype(int)
te_idx=Xte.index
fdf=pd.DataFrame({"y":yte.values,"pred":pred},index=te_idx)
fdf["disability"]=df_model.loc[te_idx,"disability"].values
fdf["prev"]=(df_model.loc[te_idx,"num_of_prev_attempts"]>0).astype(int).values
def fairness(group_col, dis_val, adv_val, name):
    out={}
    for lbl,val in [("disadvantaged",dis_val),("advantaged",adv_val)]:
        sub=fdf[fdf[group_col]==val]
        sel=sub["pred"].mean()          # selection rate (predicted pass)
        pos=sub[sub["y"]==1]
        tpr=recall_score(sub["y"],sub["pred"]) if sub["y"].nunique()>1 else np.nan
        out[lbl]=dict(n=int(len(sub)),selection_rate=round(float(sel),4),tpr=round(float(tpr),4))
    out["dp_diff"]=round(out["advantaged"]["selection_rate"]-out["disadvantaged"]["selection_rate"],4)
    out["eo_tpr_diff"]=round(out["advantaged"]["tpr"]-out["disadvantaged"]["tpr"],4)
    return out
R["fairness_disability"]=fairness("disability","Y","N","disability")
R["fairness_prevattempts"]=fairness("prev",1,0,"prev_attempts")

json.dump(R,open(os.path.join(OUT,"results.json"),"w"),indent=2,default=str)
print("DONE. Key numbers:")
print(json.dumps({k:R[k] for k in ["mpi_corr_passed","model_without_mpi","model_with_mpi",
      "mpi_lift_auc_RF","top10_perm_importance","fairness_disability","fairness_prevattempts"]},
      indent=2,default=str))
