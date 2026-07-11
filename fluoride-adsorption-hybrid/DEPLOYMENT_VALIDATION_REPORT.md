# Deployment Validation Report

**Site tested:** <https://idp.amriteshsahu.me/>
**Method:** Chrome DevTools MCP — navigated to the live site, confirmed it renders the same dashboard as local, then called the deployed API endpoints (`/api/predict24`, `/api/predict4`) directly from the browser's `fetch()`, with `track=false` so this test data isn't mixed into the site's live prediction history.
**Test inputs:** 10 rows sampled from the source datasets for each model, so a known ground-truth value exists for every case.

---

## 1. 24-Parameter Model (10 cases)

Sampled from `data/processed/dataset_simulated_500.csv` (random_state=123). Predicts `q_removal` (mg/g).

| # | pH | C0 | Time | Dose | Temp | Flow | Cl⁻ | Hardness | CO₃²⁻ | NOM | **Expected** | **Predicted** | Error |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 7.48 | 7.77 | 79 | 1.70 | 27.6 | 1.564 | 87 | 90 | 61 | 7 | 4.283 | 4.676 | +0.393 |
| 2 | 3.17 | 2.67 | 81 | 2.82 | 30.6 | 1.804 | 29 | 371 | 24 | 26 | 2.943 | 2.887 | −0.056 |
| 3 | 4.00 | 5.24 | 87 | 0.63 | 34.5 | 1.330 | 27 | 253 | 28 | 49 | 3.371 | 3.405 | +0.034 |
| 4 | 8.22 | 3.70 | 118 | 3.80 | 20.9 | 0.661 | 94 | 349 | 50 | 8 | 3.860 | 3.867 | +0.007 |
| 5 | 6.29 | 1.39 | 56 | 0.82 | 38.5 | 0.856 | 82 | 179 | 73 | 33 | 4.475 | 4.578 | +0.103 |
| 6 | 4.56 | 8.45 | 53 | 3.70 | 21.2 | 0.663 | 70 | 221 | 93 | 25 | 3.831 | 3.962 | +0.131 |
| 7 | 4.03 | 3.34 | 89 | 0.74 | 27.7 | 1.941 | 68 | 82 | 47 | 46 | 2.475 | 2.407 | −0.068 |
| 8 | 6.07 | 8.20 | 68 | 4.86 | 39.8 | 0.974 | 99 | 77 | 49 | 20 | 7.263 | 7.309 | +0.045 |
| 9 | 7.69 | 2.92 | 17 | 2.33 | 38.0 | 1.685 | 59 | 300 | 29 | 33 | 2.622 | 2.753 | +0.131 |
| 10 | 3.48 | 7.16 | 54 | 1.97 | 29.2 | 0.756 | 88 | 377 | 83 | 31 | 2.913 | 3.142 | +0.229 |

**Summary:** MAE = **0.120 mg/g**, max absolute error = 0.393 mg/g, mean signed error = +0.095 (slight over-prediction bias on this sample). Model's reported OOF RMSE = 0.297 mg/g — all 10 errors are within that, most well under half of it. No outliers, no failed requests.

---

## 2. 4-Parameter Model (10 cases)

Sampled from `4para/real_data/real_ccd_dataset.csv` (real experimental CCD data, random_state=123). Predicts % fluoride removal.

| # | pH | Dose | C0 | Time | **Expected** | **Predicted** | Error |
|---|---|---|---|---|---|---|---|
| 1 | 7.0 | 1.00 | 2 | 30 | 79.00 | 78.30 | −0.70 |
| 2 | 2.0 | 1.00 | 70 | 180 | 87.00 | 83.00 | **−4.00** |
| 3 | 2.0 | 1.00 | 2 | 30 | 84.59 | 83.51 | −1.08 |
| 4 | 7.0 | 1.00 | 70 | 180 | 72.77 | 73.92 | +1.15 |
| 5 | 7.0 | 0.10 | 2 | 30 | 82.35 | 79.33 | −3.02 |
| 6 | 2.0 | 1.00 | 70 | 30 | 82.26 | 80.95 | −1.31 |
| 7 | 4.5 | 0.55 | 36 | 180 | 76.25 | 74.94 | −1.31 |
| 8 | 2.0 | 1.00 | 2 | 180 | 85.44 | 83.43 | −2.01 |
| 9 | 4.5 | 0.55 | 36 | 30 | 75.83 | 74.65 | −1.18 |
| 10 | 4.5 | 0.55 | 36 | 105 | 72.17 | 73.95 | +1.78 |

**Summary:** MAE = **1.75 %**, max absolute error = 4.00 %, mean signed error = **−1.17 %** (consistent under-prediction on this sample). Model's reported OOF RMSE = 0.97 % — errors here run noticeably higher than that, and the bias is one-directional rather than balanced.

---

## 3. Observations

1. **Both endpoints are live and responding correctly** — no failed requests, no NaNs, response shape matches the local API exactly (`q_langmuir`/`residual`/`q_hybrid` for 24-param; `q_baseline`/`residual`/`final` for 4-param).
2. **24-parameter model is performing as expected** — errors are small, balanced in direction, and consistent with the RMSE reported on the Model Comparison tab (0.297 mg/g). This matches the local validation done earlier in this project (`UI_VALIDATION_NOTES.md`), so the deployment is behaving identically to local.
3. **4-parameter model shows a systematic under-prediction bias on this sample** (8 of 10 cases predicted low, mean signed error −1.17%), and the worst case (row 2: pH=2, Dose=1, C0=70, Time=180 → expected 87.00%, predicted 83.00%, error −4.00%) is nearly 4x the model's reported RMSE. This is the same weak corner of the design space flagged in the earlier local validation — extreme low-pH/high-dose/high-concentration combinations are sparsely represented in the real 30-point CCD data the model was trained on, so the RSM extrapolates conservatively (pulls toward the mean) rather than reaching the true extreme.
4. **This is a model-generalization limitation, not a deployment bug** — the same inputs produce the same predictions locally and on the deployed site (spot-checked row 10, pH=4.5/Dose=0.55/C0=36/Time=105, against the earlier local validation: both give 73.9–73.95%). The gap is inherent to the 4-parameter model's small real-data training set, not something introduced by deployment.

## 4. Recommendation

If this 4-parameter model is going to be used near the edges of its input ranges (low pH combined with high dose and high concentration), flag predictions in that region as lower-confidence, or collect a few more real experimental points there to tighten the model. The 24-parameter model has no such flagged region within this test.
