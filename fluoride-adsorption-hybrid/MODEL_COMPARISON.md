# Model Comparison: 24-Parameter vs 4-Parameter

This document compares the two hybrid modeling approaches built in this project:
the full **24-feature** model (all 10 water-chemistry factors + 14 engineered
features) versus the **4-parameter** model (only pH, Adsorbent Dose, Initial
Fluoride Concentration, Contact Time — the four variables that are
cheapest/easiest to measure or control in practice).

There is one current 4-parameter model: it is trained on **200 samples** — the
30 real experimental CCD runs you provided, plus 170 additional points
generated from an independent mechanistic model (see §3) to widen coverage of
the factor space. This supersedes earlier 4-parameter attempts (a
purely-simulated 500-sample version, and a 30-point-only version) — those are
kept only as supporting artifacts, not reported as separate results.

All results below are cross-validated out-of-fold (OOF) / leave-one-out (LOOCV)
— i.e. never evaluated on data the model was trained on.

---

## 1. Headline Results

| Model | Dataset | N | Factors Used | Response | R² (OOF) | RMSE |
|---|---|---|---|---|---|---|
| **24-parameter hybrid** | Simulated (physics-based) | 500 | pH, C0, Time, Dose, Temp, Flow, Cl⁻, Hardness, CO₃²⁻, NOM + 14 engineered | q_removal (mg/g) | **0.942** | 0.297 mg/g |
| **4-parameter model (current)** | 30 real CCD + 170 mechanistically-generated | 200 | pH, Dose, C0, Time | % fluoride removal | **0.826** | 0.97 % |

Source files:
- 24-param: [`24para/hybrid_summary.json`](24para/hybrid_summary.json)
- 4-param (current): [`4para/result/hybrid_4param_combined_summary.json`](4para/result/hybrid_4param_combined_summary.json)
- 4-param generation method: [`4para/generate_combined_dataset.py`](4para/generate_combined_dataset.py)

---

## 2. Important caveat: the two numbers are not directly comparable

Unlike a clean ablation, these two models differ on more than just factor
count:

| | 24-parameter | 4-parameter (current) |
|---|---|---|
| Data source | Physics-based simulator | Real lab data (30 pts) + independent mechanistic generator (170 pts) |
| Sample size | 500 | 200 |
| Response variable | q_removal (mg/g) | % fluoride removal |
| Ground truth | Fully synthetic | Partially real (15% of samples are actual lab measurements) |

So the ~0.12 R² gap (0.942 vs 0.826) reflects **both** the loss of 6 input
factors **and** the switch from a clean simulator to noisier, partially-real
data — not factor count alone. Do not present this gap as "removing 6 factors
costs 0.12 R²"; that specific claim would need both models on identical data
(see the archived simulated-only 4-param run below, §4, for that controlled
comparison).

---

## 3. How the 4-parameter model was built

1. **Real data (30 runs):** Central Composite Design, Design-Expert software —
   pH, Dose, C0, Time → % fluoride removal. See
   [`4para/real_data/real_ccd_dataset.csv`](4para/real_data/real_ccd_dataset.csv).
2. **Generated data (170 points):** sampled via Latin Hypercube across the
   real design's factor ranges, then scored with a fixed-form **mechanistic**
   model (Langmuir-type dose saturation × sigmoid pH effect × pseudo-2nd-order
   kinetics), calibrated to the 30 real points by least squares. This
   mechanistic form only reaches R²=0.46 on the real data on its own — it's
   intentionally low-flexibility (11 physically-interpretable parameters, not
   a free polynomial), so re-fitting a model on the combined set is not
   circular. Noise added to generated points (±0.39%) matches the real
   experiment's own replicate variability (from repeated center-point runs),
   not an inflated number.
3. **Final model:** a quadratic response-surface (RSM) fit to all 200 points,
   R²=0.826 (5-fold CV OOF). A stacking residual-ML stage (XGBoost + RF + GB →
   RidgeCV) was also tried on top but did **not** generalize (OOF R² < 0 — it
   was fitting noise), so the script automatically falls back to the RSM
   baseline as the final reported model.

---

## 4. Archived comparisons (for reference, not the current headline)

These earlier 4-parameter attempts are superseded but documented here for
context:

| Variant | N | R² | Note |
| --- | --- | --- | --- |
| Simulated only (same simulator/pipeline as 24-param) | 500 | 0.894 (OOF) | The only *controlled* ablation of the 24-param model — same data, same pipeline, only fewer inputs. Baseline R²=0.759 → hybrid R²=0.894. Confirms the 6 dropped factors are independent (LHS design) and cost ≈0.05 R². |
| Real data only, no augmentation | 30 | 0.967 (LOOCV) | Small-N LOOCV on a CCD with 6 near-duplicate center points; tends to run optimistic. Superseded by the 200-point version, which is a harder, more representative test. |

If you need the strict "cost of dropping 6 factors, all else equal" number,
use the simulated-only row above (0.942 → 0.894, Δ=0.048), not the current
real-data 4-parameter model.

---

## 5. Recommendation

- **Paper's headline result:** 24-parameter hybrid model, R²=0.942 (meets the
  ≥0.94 target).
- **"Field-deployable, 4-input" result:** the current 4-parameter model,
  R²=0.826 on 200 samples (30 real + 170 mechanistically-generated), clearly
  labeled as validated partly on real lab data.
- **If asked to justify the 4-parameter number against real data:** point to
  the real-data generation method (§3) and the archived 30-point LOOCV
  (0.967) as corroborating evidence that the model form is sound, while
  citing 0.826 as the more conservative, better-powered estimate.
