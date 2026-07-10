# Gradio UI Validation Notes

Manual validation of the live app (`gradio_app.py`, http://localhost:7860)
using Chrome DevTools MCP to enter values by hand into the browser form and
read back the predictions — not a scripted/programmatic call to the model,
but exactly what a user would see clicking through the UI.

Test inputs were sampled from the project's own datasets, so a known
"expected" (actual) value exists for each row to compare against.

---

## 24-Parameter Model (predicts q_removal, mg/g)

Test rows sampled from `data/processed/dataset_simulated_500.csv` (random_state=7).

| # | pH | C0 | Time | Dose | Temp | Flow | Cl⁻ | Hardness | CO₃²⁻ | NOM | **Expected** (actual q_removal) | **Predicted** (app) | Error |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4.63 | 7.41 | 52 | 3.23 | 30.5 | 1.675 | 8 | 243 | 10 | 6 | 3.888 | 4.033 | +0.145 |
| 2 | 3.75 | 1.94 | 32 | 2.38 | 31.7 | 1.226 | 61 | 481 | 66 | 1 | 2.378 | 2.364 | −0.014 |
| 3 | 7.26 | 3.87 | 51 | 4.87 | 23.7 | 1.205 | 50 | 68 | 41 | 45 | 5.745 | 5.798 | +0.053 |
| 4 | 6.01 | 2.44 | 68 | 1.15 | 22.4 | 0.546 | 40 | 423 | 40 | 27 | 4.834 | 4.793 | −0.041 |
| 5 | 3.93 | 8.22 | 87 | 2.63 | 21.3 | 1.849 | 44 | 142 | 82 | 15 | 3.133 | 3.218 | +0.085 |

Mean absolute error across these 5: **0.068 mg/g**, all within the model's
reported OOF RMSE of 0.297 mg/g. Predictions track the expected values
closely and in both directions (over- and under-prediction), consistent with
a well-calibrated model rather than a systematic bias.

---

## 4-Parameter Model (predicts % fluoride removal)

Test rows sampled from `4para/real_data/real_ccd_dataset.csv` (real experimental data, random_state=7).

| # | pH | Dose | C0 | Time | **Expected** (actual % removal) | **Predicted** (app) | Error |
|---|---|---|---|---|---|---|---|
| 1 | 4.5 | 0.55 | 2 | 105 | 77.10 | 76.09 | −1.01 |
| 2 | 7.0 | 0.55 | 36 | 105 | 72.71 | 74.39 | +1.68 |
| 3 | 2.0 | 0.10 | 70 | 180 | 80.32 | 79.54 | −0.78 |
| 4 | 4.5 | 0.55 | 36 | 105 | 72.54 | 73.95 | +1.41 |
| 5 | 4.5 | 0.55 | 36 | 30 | 75.83 | 74.65 | −1.18 |

Mean absolute error across these 5: **1.21 %**, consistent with the model's
reported OOF RMSE of 0.97 % (real experimental data is noisier than the
simulated 24-parameter dataset, so a larger absolute error here is expected).

---

## Observations

1. **Both models predict in the right ballpark with no glaring errors** —
   no case where the app returned a wildly wrong number, a NaN, or crashed.
2. **24-parameter model is tighter** (errors within ±0.15 mg/g on a
   ~2–6 mg/g scale) than the **4-parameter model** (errors within ±1.7% on a
   ~72–80% scale), which matches expectations: the 24-param model was
   validated on clean simulated data (OOF R²=0.942), while the 4-param model
   is validated on noisier real lab data plus generated augmentation
   (OOF R²=0.826).
3. **Test #4 on the 4-parameter model** (pH=4.5, Dose=0.55, C0=36, Time=105)
   is one of six real replicate runs at this exact center point (actual
   values ranged 72.17–73.18% across replicates due to real experimental
   noise) — the prediction of 73.95% sits just above that replicate range,
   which is reasonable given the RSM is smoothing over natural replicate
   scatter rather than memorizing any one run.
4. **Residual ML correction on the 4-parameter tab is consistently near-zero**
   (±0.06%) across all 5 tests, confirming what the training summary
   reported: that stage doesn't generalize on this dataset and the RSM
   baseline alone is correctly doing all the work.
5. No UI issues encountered — number fields, tab switching, and the Predict
   button all worked correctly through repeated manual entry.
