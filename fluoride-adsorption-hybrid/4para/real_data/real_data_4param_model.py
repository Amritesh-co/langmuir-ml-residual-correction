#!/usr/bin/env python3
"""
4-Parameter Response Surface Model on REAL experimental CCD data.

Dataset: 30-run Central Composite Design (Design-Expert), 4 factors:
  A: pH, B: Adsorbent dose (g/100 mL), C: Initial fluoride concentration (ppm),
  D: Contact time (min) -> Response: % fluoride removal.

Only 30 samples exist (real experiment, not simulated), so a large ML stacking
ensemble (as used on the 500-point simulated dataset) would badly overfit.
Instead this fits the standard RSM approach for CCD data:
  - Full second-order (quadratic) polynomial regression on standardized factors
  - Reports R2 / Adjusted R2 (in-sample)
  - Reports Leave-One-Out Cross-Validated R2 (honest generalization estimate
    for n=30)

Seed = 42.
"""
from pathlib import Path
import json
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import LeaveOneOut, cross_val_predict
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

SEED = 42
ROOT = Path(__file__).parent.parent
OUT = ROOT / "results" / "real_data_4para"; OUT.mkdir(parents=True, exist_ok=True)
IMG = ROOT / "images"; IMG.mkdir(exist_ok=True)

FACT4 = ["pH", "Dose", "C0", "Time"]
RESPONSE = "Removal_pct"


def M(y, p, n_params=None):
    r2 = r2_score(y, p)
    rmse = float(np.sqrt(mean_squared_error(y, p)))
    mae = float(mean_absolute_error(y, p))
    out = dict(r2=float(r2), rmse=rmse, mae=mae)
    if n_params is not None:
        n = len(y)
        out["adj_r2"] = float(1 - (1 - r2) * (n - 1) / (n - n_params - 1))
    return out


# -------- Load real data --------
df = pd.read_csv(ROOT / "data" / "processed" / "real_ccd_dataset.csv")
X = df[FACT4].values
y = df[RESPONSE].values
print(f"[Data] {len(df)} real experimental runs, factors={FACT4}")

# -------- Full quadratic RSM (degree 2, main + interaction + squared terms) --------
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
poly = PolynomialFeatures(degree=2, include_bias=False)
X_poly = poly.fit_transform(X_scaled)
term_names = poly.get_feature_names_out(FACT4)
print(f"[Model] Quadratic RSM: {X_poly.shape[1]} terms from {X_poly.shape[0]} runs")

linreg = LinearRegression().fit(X_poly, y)
y_pred_insample = linreg.predict(X_poly)
insample_m = M(y, y_pred_insample, n_params=X_poly.shape[1])
print(f"[In-sample] R2={insample_m['r2']:.4f}  Adj-R2={insample_m['adj_r2']:.4f}  RMSE={insample_m['rmse']:.4f}")

# -------- Leave-one-out CV (honest estimate for n=30) --------
loo = LeaveOneOut()
y_pred_loo = cross_val_predict(LinearRegression(), X_poly, y, cv=loo, n_jobs=-1)
loo_m = M(y, y_pred_loo)
print(f"[LOOCV]     R2={loo_m['r2']:.4f}  RMSE={loo_m['rmse']:.4f}  MAE={loo_m['mae']:.4f}")

# -------- Coefficient / term importance table --------
coef_df = pd.DataFrame({"term": term_names, "coefficient": linreg.coef_}).sort_values("coefficient", key=abs, ascending=False)

# -------- Save results --------
pd.DataFrame({
    "Run": df["Run"], "pH": df["pH"], "Dose": df["Dose"], "C0": df["C0"], "Time": df["Time"],
    "Removal_actual": y, "Removal_pred_insample": y_pred_insample, "Removal_pred_LOOCV": y_pred_loo
}).to_csv(OUT / "real_4param_predictions.csv", index=False)

coef_df.to_csv(OUT / "real_4param_coefficients.csv", index=False)

json.dump({
    "source": "Real experimental CCD dataset (30 runs, Design-Expert)",
    "factors_used": FACT4,
    "n_samples": len(df),
    "model": "Full quadratic response surface (2nd-order polynomial regression)",
    "n_terms": int(X_poly.shape[1]),
    "in_sample": insample_m,
    "loocv": loo_m,
    "note": "LOOCV R2 is the honest generalization metric given only 30 real samples; in-sample R2/Adj-R2 reflects RSM fit quality typical for CCD/ANOVA reporting."
}, open(OUT / "real_4param_summary.json", "w"), indent=2)

# -------- Figure --------
fig, ax = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle("Real Data (n=30 CCD) — 4-Parameter Quadratic RSM Model", fontsize=14, fontweight="bold")

a = ax[0]
a.scatter(y, y_pred_insample, s=60, alpha=0.75, color="#2a9d8f", label=f"In-sample fit (R2={insample_m['r2']:.3f})", edgecolors="k", linewidths=0.4)
a.scatter(y, y_pred_loo, s=60, alpha=0.75, color="#e76f51", marker="^", label=f"LOOCV prediction (R2={loo_m['r2']:.3f})", edgecolors="k", linewidths=0.4)
lo, hi = y.min() - 2, y.max() + 2
a.plot([lo, hi], [lo, hi], "r--", lw=1.4, label="1:1 line")
a.set_xlabel("Actual % fluoride removal"); a.set_ylabel("Predicted % fluoride removal")
a.set_title("(a) Predicted vs Actual"); a.legend(fontsize=9, loc="upper left"); a.grid(True, alpha=0.3, ls="--")

b = ax[1]
top = coef_df.head(10).iloc[::-1]
b.barh(top["term"], top["coefficient"], color=["#2a9d8f" if c > 0 else "#e76f51" for c in top["coefficient"]], edgecolor="black")
b.set_xlabel("Standardized coefficient"); b.set_title("(b) Top 10 RSM Terms by |coefficient|")
b.grid(True, alpha=0.3, ls="--", axis="x")

plt.tight_layout(rect=[0, 0, 1, 0.94])
plt.savefig(IMG / "fig8_real_data_4param_rsm.png", dpi=200, bbox_inches="tight")
plt.close()

print("\nDone. Outputs written to results/real_data_4para/ and images/fig8_real_data_4param_rsm.png")
