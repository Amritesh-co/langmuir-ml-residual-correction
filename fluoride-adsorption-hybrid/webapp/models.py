#!/usr/bin/env python3
"""
Shared model-loading and prediction logic for both the FastAPI backend
(webapp/backend.py) and the seed-data generator (webapp/generate_seed_data.py),
so the two never drift out of sync.
"""
from pathlib import Path
import pickle
import numpy as np, pandas as pd
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.linear_model import LinearRegression

ROOT = Path(__file__).parent.parent

# =====================================================================
# ---------------------------- 24-PARAMETER ----------------------------
# =====================================================================
FACT10 = ["pH", "C0", "Time", "Dose", "Temp", "Flow", "Chloride", "Hardness", "Carbonate", "NOM"]
BOUNDS24 = {"pH": (3.0, 9.0), "C0": (1.0, 10.0), "Time": (10, 120), "Dose": (0.5, 5.0),
            "Temp": (20, 40), "Flow": (0.5, 2.0), "Chloride": (0, 100), "Hardness": (1, 500),
            "Carbonate": (0, 100), "NOM": (0, 50)}

sim_df = pd.read_csv(ROOT / "data" / "processed" / "dataset_simulated_500.csv")

_scaler_X10 = StandardScaler().fit(sim_df[FACT10].values)
_scaler_y10 = StandardScaler().fit(sim_df["q_removal"].values.reshape(-1, 1))
_poly10 = PolynomialFeatures(degree=2, include_bias=False).fit(_scaler_X10.transform(sim_df[FACT10].values))
_X10_poly = _poly10.transform(_scaler_X10.transform(sim_df[FACT10].values))
_y10_scaled = _scaler_y10.transform(sim_df["q_removal"].values.reshape(-1, 1)).ravel()
_langmuir10 = LinearRegression().fit(_X10_poly, _y10_scaled)

with open(ROOT / "24para" / "hybrid_residual_model.pkl", "rb") as f:
    _residual_model_24 = pickle.load(f)

Q_MIN, Q_MAX = float(sim_df["q_removal"].min()), float(sim_df["q_removal"].max())


def _aug24(v):
    d = pd.DataFrame([v])
    g = np.exp(-((d["pH"] - 6.5) ** 2) / 4.5)
    d["g"] = g
    d["g_Dose"] = g * d["Dose"]; d["g_Time"] = g * d["Time"]; d["g_C0"] = g * d["C0"]
    d["g_DoseTime"] = g * d["Dose"] * d["Time"]
    d["kin"] = 1 - np.exp(-0.01 * d["Dose"] * d["Time"])
    d["g_kin"] = g * d["kin"]; d["base_cap"] = g * d["kin"] * d["Dose"]
    d["ion_load"] = d["Chloride"] / 100 + d["Hardness"] / 500 + d["Carbonate"] / 100
    d["g_ion"] = g * d["ion_load"]; d["nom_pen"] = d["NOM"] / 50
    d["pH_dev"] = d["pH"] - 6.5; d["pH_abs_dev"] = (d["pH"] - 6.5).abs(); d["pH_dev_sq"] = (d["pH"] - 6.5) ** 2
    feat = FACT10 + ["g", "g_Dose", "g_Time", "g_C0", "g_DoseTime", "kin", "g_kin", "base_cap",
                      "ion_load", "g_ion", "nom_pen", "pH_dev", "pH_abs_dev", "pH_dev_sq"]
    return d[feat].values


def predict24(v: dict) -> dict:
    """v must contain the 10 FACT10 keys."""
    X_raw = np.array([[v["pH"], v["C0"], v["Time"], v["Dose"], v["Temp"], v["Flow"],
                        v["Chloride"], v["Hardness"], v["Carbonate"], v["NOM"]]])
    X_poly = _poly10.transform(_scaler_X10.transform(X_raw))
    q_langmuir = float(_scaler_y10.inverse_transform(_langmuir10.predict(X_poly).reshape(-1, 1)).ravel()[0])

    X24 = _aug24(v)
    residual_pred = float(_residual_model_24.predict(X24)[0])
    q_hybrid = q_langmuir + residual_pred

    return {
        "q_langmuir": round(q_langmuir, 4),
        "residual": round(residual_pred, 4),
        "q_hybrid": round(q_hybrid, 4),
        "range": [Q_MIN, Q_MAX],
        "r2": 0.942, "rmse": 0.297,
    }


# =====================================================================
# ---------------------------- 4-PARAMETER ----------------------------
# =====================================================================
FACT4 = ["pH", "Dose", "C0", "Time"]
BOUNDS4 = {"pH": (2.0, 7.0), "Dose": (0.1, 1.0), "C0": (2.0, 70.0), "Time": (30, 180)}

with open(ROOT / "4para" / "result" / "hybrid_4param_combined_model.pkl", "rb") as f:
    _bundle4 = pickle.load(f)

_scaler4 = _bundle4["scaler_X"]
_poly4 = _bundle4["poly"]
_baseline4 = _bundle4["baseline_linreg"]
_residual_model_4 = _bundle4["residual_model"]
_feat4 = _bundle4["features"]


def _aug4(pH, Dose, C0, Time):
    d = pd.DataFrame([{"pH": pH, "Dose": Dose, "C0": C0, "Time": Time}])
    g = np.exp(-((d["pH"] - 6.5) ** 2) / 4.5)
    d["g"] = g
    d["g_Dose"] = g * d["Dose"]; d["g_Time"] = g * d["Time"]; d["g_C0"] = g * d["C0"]
    d["g_DoseTime"] = g * d["Dose"] * d["Time"]
    d["kin"] = 1 - np.exp(-0.01 * d["Dose"] * d["Time"])
    d["g_kin"] = g * d["kin"]; d["base_cap"] = g * d["kin"] * d["Dose"]
    d["C0_Dose_ratio"] = d["C0"] / d["Dose"] if d["Dose"].iloc[0] != 0 else 0
    d["pH_dev"] = d["pH"] - 6.5; d["pH_abs_dev"] = (d["pH"] - 6.5).abs(); d["pH_dev_sq"] = (d["pH"] - 6.5) ** 2
    return d[_feat4].values


def predict4(v: dict) -> dict:
    """v must contain the 4 FACT4 keys."""
    X_raw = np.array([[v["pH"], v["Dose"], v["C0"], v["Time"]]])
    X_poly = _poly4.transform(_scaler4.transform(X_raw))
    q_baseline = float(_baseline4.predict(X_poly)[0])

    X4 = _aug4(v["pH"], v["Dose"], v["C0"], v["Time"])
    residual_pred = float(_residual_model_4.predict(X4)[0])
    final_pred = float(np.clip(q_baseline, 0, 100))

    return {
        "q_baseline": round(q_baseline, 4),
        "residual": round(residual_pred, 4),
        "final": round(final_pred, 4),
        "range": [0, 100],
        "r2": 0.826, "rmse": 0.97,
    }
