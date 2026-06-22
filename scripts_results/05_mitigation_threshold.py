"""05_mitigation_threshold.py
Group-aware threshold mitigation on the SAME leakage-safe RF (seed=42),
to close the prior-attempts equalized-odds gap more aggressively than reweighting.
We lower the pass-threshold for the disadvantaged group (prev>0) so its TPR
matches the advantaged group's TPR (equal-opportunity calibration), then
report TPR/FPR gaps + accuracy/AUC before vs after.
"""
import numpy as np, pandas as pd, os, json, warnings
warnings.filterwarnings("ignore")
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, roc_auc_score, confusion_matrix
SEED=42; np.random.seed(SEED)
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT=os.path.join(BASE,"scripts_results"); KEY=["code_module","code_presentation","id_student"]
m=pd.read_csv(os.path.join(BASE,"oulad_master.csv"))
mpi=pd.read_csv(os.path.join(OUT,"mpi_features.csv"))
df=m.merge(mpi,on=KEY,how="left"); y=df["passed"].astype(int)
behav=["n_submissions","n_banked","total_clicks","prop_active_weeks","consistency_inv_cv",
 "resource_entropy","n_activity_types","on_time_rate","mean_lead_days","n_assess"]
mpidims=["D1_engagement","D2_diversity","D3_timeliness","D4_persistence","MPI"]
demo=["num_of_prev_attempts","studied_credits","age_midpoint","education_level","imd_numeric"]
F=behav+mpidims+demo
X=df[F].apply(pd.to_numeric,errors="coerce"); X=X.fillna(X.median())
Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=0.25,stratify=y,random_state=SEED)
rf=RandomForestClassifier(n_estimators=400,class_weight="balanced",random_state=SEED,n_jobs=-1).fit(Xtr,ytr)
pp=rf.predict_proba(Xte)[:,1]; ti=Xte.index
prev=(df.loc[ti,"num_of_prev_attempts"]>0).astype(int).values
def gap(pred):
    f=pd.DataFrame({"y":yte.values,"p":pred,"g":prev})
    def rr(s):
        tn,fp,fn,tp=confusion_matrix(s["y"],s["p"],labels=[0,1]).ravel()
        return tp/(tp+fn),fp/(fp+tn),s["p"].mean()
    dT,dF,ds=rr(f[f.g==1]); aT,aF,asr=rr(f[f.g==0])
    return dict(dTPR=round(aT-dT,4),dFPR=round(aF-dF,4),
                eo_gap=round(max(abs(aT-dT),abs(aF-dF)),4),dp_diff=round(asr-ds,4),
                TPR_dis=round(dT,4),TPR_adv=round(aT,4))
base=(pp>=0.5).astype(int)
# find disadvantaged threshold giving TPR ~ advantaged TPR at 0.5
adv_T=gap(base)["TPR_adv"]
best=0.5
for thr in np.arange(0.50,0.05,-0.01):
    pred=np.where(prev==1, (pp>=thr).astype(int), (pp>=0.5).astype(int))
    f=pd.DataFrame({"y":yte.values,"p":pred,"g":prev}); s=f[f.g==1]
    tn,fp,fn,tp=confusion_matrix(s["y"],s["p"],labels=[0,1]).ravel(); tprd=tp/(tp+fn)
    if tprd>=adv_T: best=round(float(thr),2); break
mit=np.where(prev==1,(pp>=best).astype(int),(pp>=0.5).astype(int))
R=dict(method="group-aware threshold (disadvantaged prev>0 thr=%.2f, advantaged 0.50)"%best,
       chosen_threshold=best,
       before=gap(base),after=gap(mit),
       acc_before=round(accuracy_score(yte,base),4),acc_after=round(accuracy_score(yte,mit),4),
       auc=round(roc_auc_score(yte,pp),4))
json.dump(R,open(os.path.join(OUT,"results_mitigation_threshold.json"),"w"),indent=2)
print(json.dumps(R,indent=2))
