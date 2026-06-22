"""
01_build_mpi.py
Builds the Motivation Proxy Index (MPI) from raw OULAD tables at the
student x module x presentation level. Four dimensions:
  D1 Engagement Consistency  (weekly clicks: 1/(1+CV) + prop active weeks)
  D2 Resource Diversity      (normalized Shannon entropy of activity_type)
  D3 Assessment Timeliness   (on-time rate + mean lead days)
  D4 Persistence After Difficulty (post-low-score click ratio vs baseline)
Outputs scripts_results/mpi_features.csv
studentVle (10.6M rows) is processed in CHUNKS to keep memory manageable.
"""
import numpy as np, pandas as pd, os
np.random.seed(42)
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUL  = os.path.join(BASE, "1_OULAD")
OUT  = os.path.join(BASE, "scripts_results")
KEY  = ["code_module","code_presentation","id_student"]

def k(df): return list(zip(df.code_module, df.code_presentation, df.id_student))

# ---------- reference tables ----------
vle = pd.read_csv(os.path.join(OUL,"vle.csv"))[["id_site","code_module","code_presentation","activity_type"]]
site_act = vle.set_index(["id_site","code_module","code_presentation"])["activity_type"]

# ---------- chunked pass over studentVle ----------
# accumulators keyed by (cm,cp,id)
from collections import defaultdict
weekly = defaultdict(lambda: defaultdict(int))     # key -> week -> clicks
act    = defaultdict(lambda: defaultdict(int))     # key -> activity_type -> clicks
daily  = defaultdict(lambda: defaultdict(int))     # key -> day -> clicks (for persistence)
max_week_seen = defaultdict(int)

cols = ["code_module","code_presentation","id_student","id_site","date","sum_click"]
reader = pd.read_csv(os.path.join(OUL,"studentVle.csv"), usecols=cols,
                     chunksize=2_000_000)
nchunks=0
for ch in reader:
    nchunks+=1
    ch = ch[ch["date"]>=0]
    ch["week"] = (ch["date"]//7).astype(int)
    # weekly clicks
    g = ch.groupby(["code_module","code_presentation","id_student","week"])["sum_click"].sum()
    for (cm,cp,idn,w),v in g.items():
        weekly[(cm,cp,idn)][w]+=int(v)
    # daily clicks (persistence)
    gd = ch.groupby(["code_module","code_presentation","id_student","date"])["sum_click"].sum()
    for (cm,cp,idn,d),v in gd.items():
        daily[(cm,cp,idn)][int(d)]+=int(v)
    # activity-type clicks (join on id_site+module+pres)
    ch2 = ch.merge(vle, on=["id_site","code_module","code_presentation"], how="left")
    ga = ch2.groupby(["code_module","code_presentation","id_student","activity_type"])["sum_click"].sum()
    for (cm,cp,idn,a),v in ga.items():
        act[(cm,cp,idn)][a]+=int(v)
    print("chunk",nchunks,"done rows~",len(ch))

print("VLE chunks processed:", nchunks)

# ---------- D1 Engagement Consistency ----------
def cv(x):
    x=np.array(list(x.values()),dtype=float)
    if x.mean()==0 or len(x)==0: return np.nan
    return x.std(ddof=0)/x.mean()
rows=[]
# need course length to compute prop active weeks -> use observed max week per (cm,cp)
maxweek_cp = defaultdict(int)
for (cm,cp,idn),wk in weekly.items():
    if wk:
        maxweek_cp[(cm,cp)] = max(maxweek_cp[(cm,cp)], max(wk.keys()))

for key,wk in weekly.items():
    cm,cp,idn=key
    c=cv(wk)
    cons = 1/(1+c) if c==c else np.nan
    span = maxweek_cp[(cm,cp)]+1 if maxweek_cp[(cm,cp)]>0 else 1
    active = sum(1 for v in wk.values() if v>0)
    prop_active = active/span
    rows.append((cm,cp,idn,cons,prop_active,sum(wk.values())))
d1=pd.DataFrame(rows,columns=KEY+["consistency_inv_cv","prop_active_weeks","total_clicks"])

# ---------- D2 Resource Diversity (normalized Shannon entropy) ----------
def nshannon(d):
    v=np.array(list(d.values()),dtype=float)
    v=v[v>0]
    if v.sum()==0 or len(v)<=1: return 0.0 if len(v)==1 else np.nan
    p=v/v.sum()
    H=-(p*np.log(p)).sum()
    return H/np.log(len(v))
rows=[]
for key,a in act.items():
    rows.append((*key, nshannon(a), len([x for x in a if x==x])))
d2=pd.DataFrame(rows,columns=KEY+["resource_entropy","n_activity_types"])

# ---------- D3 Assessment Timeliness ----------
sa = pd.read_csv(os.path.join(OUL,"studentAssessment.csv"))
asm = pd.read_csv(os.path.join(OUL,"assessments.csv"))
sa = sa.merge(asm[["id_assessment","code_module","code_presentation","date","assessment_type"]],
              on="id_assessment", how="left")
sa = sa.rename(columns={"date":"due_date"})
sa = sa.dropna(subset=["due_date"])
sa["lead"] = sa["due_date"] - sa["date_submitted"]   # positive = submitted early
sa["on_time"] = (sa["lead"]>=0).astype(int)
d3 = sa.groupby(KEY).agg(on_time_rate=("on_time","mean"),
                         mean_lead_days=("lead","mean"),
                         n_assess=("on_time","size")).reset_index()

# ---------- D4 Persistence After Difficulty ----------
# first low score (<40); compare clicks in 14 days AFTER its submit date vs 14-day baseline before
sa_sorted = sa.sort_values("date_submitted")
low = sa_sorted[sa_sorted["score"]<40]
first_low = low.groupby(KEY)["date_submitted"].min().reset_index().rename(columns={"date_submitted":"low_day"})
persist_rows=[]
firstlow_map = {(r.code_module,r.code_presentation,r.id_student):int(r.low_day) for r in first_low.itertuples()}
all_keys = set(weekly.keys()) | set(d3.set_index(KEY).index.tolist())
for key in all_keys:
    if key in firstlow_map:
        ld=firstlow_map[key]
        dd=daily.get(key,{})
        after = sum(v for day,v in dd.items() if ld < day <= ld+14)
        before= sum(v for day,v in dd.items() if ld-14 <= day <= ld)
        ratio = (after+1)/(before+1)   # smoothed
        persist_rows.append((*key, ratio, 1))
    else:
        persist_rows.append((*key, np.nan, 0))  # neutral, flagged
d4=pd.DataFrame(persist_rows,columns=KEY+["persistence_ratio","had_low_score"])

# ---------- merge ----------
mpi = d1.merge(d2,on=KEY,how="outer").merge(d3,on=KEY,how="outer").merge(d4,on=KEY,how="outer")

# combine D1 sub-features into one z-mean engagement-consistency dimension
def z(s):
    s=pd.to_numeric(s,errors="coerce")
    return (s-s.mean())/s.std(ddof=0)
mpi["D1_engagement"] = z(mpi["consistency_inv_cv"]).add(z(mpi["prop_active_weeks"]),fill_value=0)/2
mpi["D2_diversity"]  = z(mpi["resource_entropy"])
mpi["D3_timeliness"] = z(mpi["on_time_rate"]).add(z(mpi["mean_lead_days"]),fill_value=0)/2
# persistence neutral fill = sample median ratio before z
pr = mpi["persistence_ratio"].copy()
pr = pr.fillna(pr.median())
mpi["D4_persistence"] = z(pr)

for c in ["D1_engagement","D2_diversity","D3_timeliness","D4_persistence"]:
    mpi[c]=mpi[c].fillna(0.0)   # missing dimension -> neutral 0 after z
mpi["MPI"] = mpi[["D1_engagement","D2_diversity","D3_timeliness","D4_persistence"]].mean(axis=1)

mpi.to_csv(os.path.join(OUT,"mpi_features.csv"),index=False)
print("MPI rows:",len(mpi))
print(mpi[["D1_engagement","D2_diversity","D3_timeliness","D4_persistence","MPI"]].describe())
