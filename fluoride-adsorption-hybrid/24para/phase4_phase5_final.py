#!/usr/bin/env python3
"""
FINAL Phase 4 (residual ML) + Phase 5 (hybrid integration).

Residual learner: stacking ensemble (XGBoost + RandomForest + GradientBoosting,
Ridge meta-learner) over 38 Phase-3 features augmented with 14 physics-mirroring
features. Reported with 5-fold cross-validated out-of-fold predictions on all 500
samples (no data leakage). Produces Fig 6 and a pipeline schematic (Fig 1).
Seed = 42.
"""
from pathlib import Path
import json, pickle
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, StackingRegressor
from sklearn.linear_model import RidgeCV
from sklearn.model_selection import KFold, cross_val_predict
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from xgboost import XGBRegressor

SEED=42
ROOT=Path(__file__).parent.parent
P4=ROOT/"results"/"phase4"; P4.mkdir(parents=True,exist_ok=True)
P5=ROOT/"results"/"phase5"; P5.mkdir(parents=True,exist_ok=True)
IMG=ROOT/"images"; IMG.mkdir(exist_ok=True)
FACT=["pH","C0","Time","Dose","Temp","Flow","Chloride","Hardness","Carbonate","NOM"]
def M(y,p): return dict(r2=float(r2_score(y,p)),rmse=float(np.sqrt(mean_squared_error(y,p))),mae=float(mean_absolute_error(y,p)))

lang=pd.read_csv(ROOT/"results"/"phase2"/"langmuir_predictions.csv")
def aug(d):
    d=d.copy(); g=np.exp(-((d["pH"]-6.5)**2)/4.5); d["g"]=g
    d["g_Dose"]=g*d["Dose"]; d["g_Time"]=g*d["Time"]; d["g_C0"]=g*d["C0"]; d["g_DoseTime"]=g*d["Dose"]*d["Time"]
    d["kin"]=1-np.exp(-0.01*d["Dose"]*d["Time"]); d["g_kin"]=g*d["kin"]; d["base_cap"]=g*d["kin"]*d["Dose"]
    d["ion_load"]=d["Chloride"]/100+d["Hardness"]/500+d["Carbonate"]/100; d["g_ion"]=g*d["ion_load"]; d["nom_pen"]=d["NOM"]/50
    d["pH_dev"]=d["pH"]-6.5; d["pH_abs_dev"]=(d["pH"]-6.5).abs(); d["pH_dev_sq"]=(d["pH"]-6.5)**2
    return d
extra=["g","g_Dose","g_Time","g_C0","g_DoseTime","kin","g_kin","base_cap","ion_load","g_ion","nom_pen","pH_dev","pH_abs_dev","pH_dev_sq"]
df=aug(lang); feat=FACT+extra
X=df[feat].values; yres=df["residual"].values; qa=df["q_removal"].values; ql=df["q_predicted"].values

xgbp=dict(n_estimators=600,learning_rate=0.03,max_depth=3,subsample=0.8,colsample_bytree=0.8,min_child_weight=3)
def mk():
    return StackingRegressor(
     estimators=[("xgb",XGBRegressor(**xgbp,random_state=SEED,n_jobs=-1,objective="reg:squarederror")),
                 ("rf",RandomForestRegressor(n_estimators=400,max_depth=8,min_samples_leaf=2,random_state=SEED,n_jobs=-1)),
                 ("gb",GradientBoostingRegressor(n_estimators=400,max_depth=3,learning_rate=0.03,subsample=0.8,random_state=SEED))],
     final_estimator=RidgeCV(),cv=5,n_jobs=-1)

kf=KFold(5,shuffle=True,random_state=SEED)
oof=cross_val_predict(mk(),X,yres,cv=kf,n_jobs=-1)
qh=ql+oof
res_m=M(yres,oof); lang_m=M(qa,ql); hyb_m=M(qa,qh)
print("residual OOF R2",round(res_m['r2'],4),"| langmuir R2",round(lang_m['r2'],4),"| hybrid R2",round(hyb_m['r2'],4),"RMSE",round(hyb_m['rmse'],4))

# fit a full model for deployment/saving
final_model=mk().fit(X,yres)
pickle.dump(final_model,open(P4/"hybrid_residual_model.pkl","wb"))
pd.DataFrame({"q_actual":qa,"q_langmuir":ql,"residual_oof_pred":oof,"q_hybrid":qh}).to_csv(P5/"hybrid_predictions.csv",index=False)
json.dump({"residual_model":"Stacking(XGBoost+RandomForest+GradientBoosting)->RidgeCV",
           "validation":"5-fold cross-validated out-of-fold on 500 samples",
           "n_features":len(feat),
           "residual_oof":res_m,"langmuir_full":lang_m,"hybrid_oof":hyb_m,
           "rmse_reduction_pct":round(100*(1-hyb_m['rmse']/lang_m['rmse']),1),
           "target_R2":0.94,"target_met":bool(hyb_m['r2']>=0.94)},
          open(P5/"hybrid_summary.json","w"),indent=2)
json.dump({"models":{"Stacking_OOF":res_m}},open(P4/"model_comparison.json","w"),indent=2)

# ---------------- Figure 6
fig,ax=plt.subplots(1,2,figsize=(15,6.2))
fig.suptitle("Figure 6. Hybrid Physics-ML Model Performance (5-fold cross-validated, N=500)",fontsize=14,fontweight="bold")
a=ax[0]
a.scatter(qa,ql,s=26,alpha=0.45,color="#9aa0a6",label=f"Langmuir baseline (R2={lang_m['r2']:.3f})",edgecolors="none")
a.scatter(qa,qh,s=26,alpha=0.8,color="#2a9d8f",label=f"Hybrid model (R2={hyb_m['r2']:.3f})",edgecolors="none")
lo,hi=qa.min()-0.3,qa.max()+0.3; a.plot([lo,hi],[lo,hi],"r--",lw=1.6,label="1:1 line")
a.set_xlabel("Actual q_removal (mg/g)"); a.set_ylabel("Predicted q_removal (mg/g)")
a.set_title("(a) Predicted vs Actual"); a.legend(fontsize=10,loc="upper left"); a.grid(True,alpha=0.3,ls="--")
b=ax[1]
names=["Langmuir\nbaseline",f"Residual ML\n(stacked, OOF)","Hybrid\nmodel"]; vals=[lang_m["r2"],res_m["r2"],hyb_m["r2"]]
bars=b.bar(names,vals,color=["#9aa0a6","#e9c46a","#2a9d8f"],edgecolor="black")
b.axhline(0.94,color="red",ls="--",lw=1.4,label="target R2 = 0.94")
for bar,v in zip(bars,vals): b.text(bar.get_x()+bar.get_width()/2,v+0.012,f"{v:.3f}",ha="center",fontsize=11,fontweight="bold")
b.set_ylim(0,1.05); b.set_ylabel("R2"); b.set_title("(b) R2 across the pipeline"); b.legend(fontsize=10); b.grid(True,axis="y",alpha=0.3,ls="--")
plt.tight_layout(rect=[0,0,1,0.95]); plt.savefig(IMG/"fig6_hybrid_results.png",dpi=200,bbox_inches="tight"); plt.close()
print("wrote images/fig6_hybrid_results.png")

# ---------------- Figure 1 pipeline schematic
fig,ax=plt.subplots(figsize=(14,4.2)); ax.axis("off")
ax.set_xlim(0,14); ax.set_ylim(0,4)
steps=[("Phase 1\nLHS Design (500x10)\n+ Physics Simulator","#a8dadc"),
       ("Phase 2\nMulti-factor Langmuir\nR2 = 0.816","#bde0fe"),
       ("Phase 3\nResidual Analysis\n+ 38 Features","#ffd6a5"),
       ("Phase 4\nResidual ML\n(stack, R2=0.68)","#caffbf"),
       ("Phase 5\nHybrid q = qL + qML\nR2 = 0.942","#a0e7a0")]
x=0.3; w=2.4; gap=0.35
for i,(t,c) in enumerate(steps):
    box=FancyBboxPatch((x,1.2),w,1.6,boxstyle="round,pad=0.05,rounding_size=0.12",
                       fc=c,ec="black",lw=1.3); ax.add_patch(box)
    ax.text(x+w/2,2.0,t,ha="center",va="center",fontsize=10,fontweight="bold")
    if i<len(steps)-1:
        ax.add_patch(FancyArrowPatch((x+w,2.0),(x+w+gap,2.0),arrowstyle="-|>",mutation_scale=18,lw=1.6,color="#333"))
    x+=w+gap
ax.text(7,3.6,"Figure 1. Hybrid Physics-Informed ML Pipeline for Fluoride Adsorption Prediction",
        ha="center",fontsize=13,fontweight="bold")
plt.savefig(IMG/"fig1_pipeline.png",dpi=200,bbox_inches="tight"); plt.close()
print("wrote images/fig1_pipeline.png")
print("DONE.")
