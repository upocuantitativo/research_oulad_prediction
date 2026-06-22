"""
03_early.py -- early prediction: cumulative features up to course week w.
Features at cutoff w (no leakage from future): cumulative clicks, active weeks,
n distinct activity types, n assessments submitted, mean score so far, on-time rate.
Train RF at each w; report test ROC-AUC (passed) by week. Find earliest w with AUC>=0.90.
studentVle read in chunks. seed=42.
"""
import numpy as np, pandas as pd, os, json, warnings
warnings.filterwarnings("ignore")
from collections import defaultdict
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
SEED=42; np.random.seed(SEED)
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUL=os.path.join(BASE,"1_OULAD"); OUT=os.path.join(BASE,"scripts_results")
KEY=["code_module","code_presentation","id_student"]
WEEKS=[4,8,12,16,20,24,28,32]
MAXDAY=max(WEEKS)*7

m=pd.read_csv(os.path.join(BASE,"oulad_master.csv"))
y=m.set_index(KEY)["passed"].astype(int)
vle=pd.read_csv(os.path.join(OUL,"vle.csv"))[["id_site","code_module","code_presentation","activity_type"]]

# accumulate per (key, week_bucket): clicks; per (key) set of activity types up to each week
# Build: clicks_by_week[key][week]=clicks ; acttypes_by_week[key][week]=set
clicks_w=defaultdict(lambda: defaultdict(int))
act_w=defaultdict(lambda: defaultdict(set))
cols=["code_module","code_presentation","id_student","id_site","date","sum_click"]
for ch in pd.read_csv(os.path.join(OUL,"studentVle.csv"),usecols=cols,chunksize=2_000_000):
    ch=ch[(ch["date"]>=0)&(ch["date"]<MAXDAY)]
    if len(ch)==0: continue
    ch["week"]=(ch["date"]//7).astype(int)
    ch=ch.merge(vle,on=["id_site","code_module","code_presentation"],how="left")
    g=ch.groupby(["code_module","code_presentation","id_student","week"]).agg(
        clk=("sum_click","sum"),acts=("activity_type",lambda s:set(s.dropna()))).reset_index()
    for r in g.itertuples():
        k=(r.code_module,r.code_presentation,r.id_student)
        clicks_w[k][r.week]+=int(r.clk)
        act_w[k][r.week]|=r.acts
print("vle done")

# assessments up to week w
sa=pd.read_csv(os.path.join(OUL,"studentAssessment.csv"))
asm=pd.read_csv(os.path.join(OUL,"assessments.csv"))
sa=sa.merge(asm[["id_assessment","code_module","code_presentation","date"]],on="id_assessment",how="left")
sa=sa.rename(columns={"date":"due"}).dropna(subset=["due"])
sa["on_time"]=(sa["due"]-sa["date_submitted"]>=0).astype(int)

rows_per_week={}
for w in WEEKS:
    wd=w*7
    # vle cumulative
    feats=[]
    keys=set(clicks_w.keys())
    sa_w=sa[sa["date_submitted"]<=wd]
    sag=sa_w.groupby(KEY).agg(mscore=("score","mean"),nass=("score","size"),
                              ontime=("on_time","mean"))
    sag_idx=sag.to_dict("index")
    for k in keys:
        cum=sum(v for wk,v in clicks_w[k].items() if wk<w)
        active=sum(1 for wk,v in clicks_w[k].items() if wk<w and v>0)
        atypes=set()
        for wk,s in act_w[k].items():
            if wk<w: atypes|=s
        a=sag_idx.get(k,{})
        feats.append((*k,cum,active,len(atypes),
                      a.get("mscore",np.nan),a.get("nass",0),a.get("ontime",np.nan)))
    F=pd.DataFrame(feats,columns=KEY+["cum_clicks","active_weeks","n_act_types",
                                      "mscore_sofar","n_assess_sofar","ontime_sofar"])
    rows_per_week[w]=F

res={}
for w in WEEKS:
    F=rows_per_week[w].set_index(KEY)
    df=F.join(y,how="inner").dropna(subset=["passed"])
    X=df[["cum_clicks","active_weeks","n_act_types","mscore_sofar","n_assess_sofar","ontime_sofar"]]
    X=X.fillna(X.median())
    yy=df["passed"].astype(int)
    Xtr,Xte,ytr,yte=train_test_split(X,yy,test_size=0.25,stratify=yy,random_state=SEED)
    rf=RandomForestClassifier(n_estimators=300,class_weight="balanced",random_state=SEED,n_jobs=-1).fit(Xtr,ytr)
    pp=rf.predict_proba(Xte)[:,1]
    a=roc_auc_score(yte,pp)
    res[w]=dict(auc=round(float(a),4),n=int(len(df)))
    print(f"week {w}: AUC={a:.4f} n={len(df)}")

reached=[w for w in WEEKS if res[w]["auc"]>=0.90]
out=dict(by_week=res,
         earliest_week_auc90=(min(reached) if reached else None),
         max_auc=max(res[w]["auc"] for w in WEEKS),
         max_auc_week=max(WEEKS,key=lambda w:res[w]["auc"]))
json.dump(out,open(os.path.join(OUT,"results_early.json"),"w"),indent=2)
pd.DataFrame(res).T.to_csv(os.path.join(OUT,"tab_early_auc.csv"))
print(json.dumps(out,indent=2))
