#!/usr/bin/env python3
"""
Generate paper figures from existing project data.
Fig 2: EDA of the simulated dataset (factor distributions + response relationships)
Fig 5: Residual-prediction feature importance (top 15)
Outputs are written to ./images/ for RESEARCH_PAPER.txt.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).parent.parent
IMG = ROOT / "images"
IMG.mkdir(exist_ok=True)
DPI = 200

# ---------------------------------------------------------------- Figure 2: EDA
df = pd.read_csv(ROOT / "data" / "processed" / "dataset_simulated_500.csv")
factors = ["pH", "C0", "Time", "Dose", "Temp", "Flow",
           "Chloride", "Hardness", "Carbonate", "NOM"]
resp = "q_removal"

fig, axes = plt.subplots(3, 4, figsize=(16, 11))
fig.suptitle("Figure 2. Exploratory Data Analysis of the Simulated Dataset (N = 500)",
             fontsize=15, fontweight="bold")

# 10 factor histograms
for ax, f in zip(axes.flat[:10], factors):
    ax.hist(df[f], bins=25, color="steelblue", edgecolor="black", alpha=0.75)
    ax.set_title(f, fontsize=11, fontweight="bold")
    ax.set_ylabel("count", fontsize=9)
    ax.grid(True, alpha=0.3, linestyle="--")

# Panel 11: response distribution
ax = axes.flat[10]
ax.hist(df[resp], bins=30, color="seagreen", edgecolor="black", alpha=0.8)
ax.set_title("q_removal (response)", fontsize=11, fontweight="bold")
ax.set_xlabel("mg/g", fontsize=9)
ax.grid(True, alpha=0.3, linestyle="--")

# Panel 12: q vs pH colored by Dose (the dominant relationship)
ax = axes.flat[11]
sc = ax.scatter(df["pH"], df[resp], c=df["Dose"], cmap="viridis", s=22, alpha=0.8)
ax.set_title("q_removal vs pH  (color = Dose)", fontsize=11, fontweight="bold")
ax.set_xlabel("pH", fontsize=9); ax.set_ylabel("q_removal (mg/g)", fontsize=9)
ax.axvline(6.5, color="red", ls="--", lw=1.2, alpha=0.7, label="optimal pH 6.5")
ax.legend(fontsize=8); ax.grid(True, alpha=0.3, linestyle="--")
fig.colorbar(sc, ax=ax, fraction=0.046, pad=0.04)

plt.tight_layout(rect=[0, 0, 1, 0.97])
plt.savefig(IMG / "fig2_eda.png", dpi=DPI, bbox_inches="tight")
plt.close()
print("wrote images/fig2_eda.png")

# ------------------------------------------------ Figure 5: feature importance
fi = pd.read_csv(ROOT / "results" / "phase3" / "feature_importance.csv")
fi = fi.sort_values("importance", ascending=False).head(15).iloc[::-1]

# color pH-related features distinctly
colors = ["#d1495b" if ("pH" in f or f in ("performance_index",
          "optimal_pH_score", "high_perf_flag")) else "#30638e"
          for f in fi["feature"]]

fig, ax = plt.subplots(figsize=(10, 8))
ax.barh(fi["feature"], fi["importance"] * 100, color=colors, edgecolor="black")
ax.set_xlabel("Importance (%)", fontsize=12)
ax.set_title("Figure 5. Feature Importance for Langmuir-Residual Prediction\n"
             "(screening Random Forest; red = pH-derived / pH-composite)",
             fontsize=13, fontweight="bold")
for y, v in enumerate(fi["importance"] * 100):
    ax.text(v + 0.2, y, f"{v:.1f}%", va="center", fontsize=9)
ax.grid(True, axis="x", alpha=0.3, linestyle="--")
plt.tight_layout()
plt.savefig(IMG / "fig5_feature_importance.png", dpi=DPI, bbox_inches="tight")
plt.close()
print("wrote images/fig5_feature_importance.png")
