# 🚀 PHASE 3: COMPLETE STEP-BY-STEP EXECUTION GUIDE

**12 detailed steps — from prerequisites to Phase 4 preparation**

---

## BEFORE YOU START

```
Total time estimate:
  Setup:           5 minutes
  Execution:       2 minutes
  Interpretation:  30 minutes
  ──────────────────────────
  Total:           ~40 minutes

What you need:
  ✅ langmuir_predictions.csv (from Phase 2)
  ✅ Python 3.8+ installed
  ✅ scikit-learn, scipy, matplotlib, pandas, numpy
  ✅ phase3_residual_analysis.py script
```

---

## STEP 1: VERIFY PHASE 2 OUTPUT FILE

**What to do:**
```bash
ls -lh data/langmuir_predictions.csv
# OR if in a different location:
ls -lh /path/to/langmuir_predictions.csv
```

**What you should see:**
```
-rw-r--r-- 1 user group 43K May 3 12:45 data/langmuir_predictions.csv
```

**Quick sanity check:**
```bash
python3 -c "
import pandas as pd
df = pd.read_csv('data/langmuir_predictions.csv')
print(f'Rows: {len(df)}')
print(f'Cols: {list(df.columns)}')
print(f'Residual range: {df.residual.min():.3f} to {df.residual.max():.3f}')
"
```

**Expected:**
```
Rows: 500
Cols: ['Run', 'pH', 'C0', 'Time', 'Dose', 'Temp', 'Flow', 
       'Chloride', 'Hardness', 'Carbonate', 'NOM', 'Order', 
       'q_removal', 'q_predicted', 'residual']
Residual range: -1.101 to 2.210
```

**If file is missing:**
```bash
# Copy from your Phase 2 output folder
cp /path/to/phase2_outputs/langmuir_predictions.csv data/
```

---

## STEP 2: INSTALL DEPENDENCIES

```bash
pip install scikit-learn scipy matplotlib pandas numpy
```

**Verify:**
```bash
python3 -c "
import sklearn, scipy, matplotlib, pandas, numpy
print(f'sklearn: {sklearn.__version__}')
print(f'scipy:   {scipy.__version__}')
print(f'pandas:  {pandas.__version__}')
print('All OK!')
"
```

**Expected:**
```
sklearn: 1.x.x
scipy:   1.x.x
pandas:  2.x.x
All OK!
```

---

## STEP 3: CREATE DIRECTORY STRUCTURE

```bash
mkdir -p data results
ls -la
```

**Expected structure:**
```
project/
├── data/
│   └── langmuir_predictions.csv  ← Phase 2 output
├── results/                      ← Phase 3 will write here
└── phase3_residual_analysis.py   ← The script
```

---

## STEP 4: RUN THE SCRIPT

```bash
python3 phase3_residual_analysis.py
```

**Expected runtime:** 1–2 minutes (most time is the Random Forest with 200 trees)

---

## STEP 5: MONITOR STEP [1/7] — DATA LOADING

**What you see:**
```
================================================================================
PHASE 3: RESIDUAL ANALYSIS & FEATURE ENGINEERING
Fluoride Adsorption on Coconut Husk Activated Carbon
================================================================================

[1/7] Loading Phase 2 results...
    ✓ Loaded 500 samples, 15 columns
    ✓ q_removal range: 1.417 - 8.316 mg/g
    ✓ Residuals: mean=-0.000000, std=0.5283 mg/g
    ✓ Residuals: min=-1.1008, max=2.2100 mg/g
    ✓ Skewness: 0.6008  |  Kurtosis: 0.1135
```

**What to check:**
- ✅ 500 samples loaded (not 499, not 501)
- ✅ Residual mean ≈ 0 (should be < 1e-6 in magnitude)
- ✅ Std ≈ 0.528 (matches Phase 2 RMSE)
- ✅ Skewness positive (+0.60) = right-skewed as expected

**If you see fewer rows:**
→ Data file may be corrupted or truncated. Re-copy from Phase 2 output.

---

## STEP 6: MONITOR STEP [2/7] — PATTERN ANALYSIS

**What you see:**
```
[2/7] Residual pattern analysis by factor...
    ✓ pH pattern analysis:
      pH Range    Mean Res   Std    Count   Pattern
      ─────────────────────────────────────────────
      pH 3-4      +0.248    0.492   84     ↑ underest.
      pH 4-5      -0.525    0.290   83     ↓ overest.
      pH 5-6      -0.117    0.394   84       random
      pH 6-6.5    +0.471    0.448   41     ↑ underest.
      pH 6.5-7    +0.649    0.502   42     ↑ underest.
      pH 7-7.5    +0.208    0.418   41     ↑ underest.
      pH 7.5-8    -0.176    0.271   42       random
      pH 8-9      -0.182    0.336   83       random

    ✓ Time pattern: {...} → No significant pattern
    ✓ Dose pattern: {...} → Minor pattern at low doses
    ✓ Temp pattern: {...} → No pattern (Arrhenius works)

    ✓ Linear correlations with residuals (all ~zero = expected):
      Max |corr|: 8.91e-16  (polynomial regression removed all linear signal)

    ✓ Large residuals (|res| > 1.057 = 2σ):
      Positive (model underestimates): 17 points (3.4%)
      Negative (model overestimates):  1 points (0.2%)
      Mean pH at large positive: 6.11  (near optimal 6.5-7)
      Mean pH at large negative: 4.34  (slightly acidic 4-5)
```

**What to check:**
- ✅ pH 6.5-7 shows +0.649 (biggest positive bar)
- ✅ pH 4-5 shows –0.525 (biggest negative bar)
- ✅ Time, Temp show near-zero means (no pattern)
- ✅ Linear correlations all ~ machine epsilon (~1e-16)
- ✅ 17 large positive outliers at mean pH 6.11

**The big finding:** pH 6.5-7 has mean residual +0.649 — this is your ML goldmine.

---

## STEP 7: MONITOR STEP [3/7] — FEATURE ENGINEERING

**What you see:**
```
[3/7] Engineering new features...
    ✓ Original factors kept:  10
    ✓ New features created:   28
    ✓ Total features for ML:  38
    Feature groups:
      pH deviation:       5 features
      Ion competition:    5 features
      Equilibrium/load:   5 features
      Log transforms:     5 features
      Interactions:       5 features
      Composite:          3 features
```

**What to check:**
- ✅ 28 new features created
- ✅ Total = 38 features

---

## STEP 8: MONITOR STEP [4/7] — CORRELATIONS

**What you see:**
```
[4/7] Engineered feature correlations with residuals...
    Top 10 features correlated with residuals:
       1. pH_optimal                r = +0.4837  ████████████████████████
       2. high_perf_flag            r = +0.3523  █████████████████
       3. pH_gaussian               r = +0.2231  ███████████
       4. pH_abs_dev                r = -0.1998  █████████
       5. optimal_pH_score          r = +0.1806  █████████
       6. ion_pH_interaction        r = -0.1708  ████████
       7. adsorbent_excess          r = -0.0376  █
       8. C0_Dose_ratio             r = +0.0354  █
       9. fouling_impact            r = +0.0205  █
      10. ion_ratio                 r = -0.0128  
```

**What to check:**
- ✅ pH_optimal has largest correlation (+0.48)
- ✅ Top features are pH-related
- ✅ Correlations are NOT near machine epsilon (unlike original factors)

**Why pH_abs_dev shows negative correlation here:**
```
pH_abs_dev = |pH - 6.5|

When pH is near optimal (6-7): pH_abs_dev is SMALL → residual is POSITIVE
When pH is far from optimal:   pH_abs_dev is LARGE → residual is NEGATIVE

So higher pH_abs_dev → lower residual → negative correlation!
This still makes it USEFUL for ML — it's a valid signal.
```

---

## STEP 9: MONITOR STEP [5/7] — TRAIN/TEST SPLIT

**What you see:**
```
[5/7] Preparing ML training dataset...
    ✓ Train set: 400 samples  (80%)
    ✓ Test set:  100 samples  (20%)
    ✓ Feature matrix: 38 features
    ✓ Target: residual  (mean=0.0106, std=0.5416)
```

**What to check:**
- ✅ 400 train + 100 test = 500 total
- ✅ 38 features (10 original + 28 engineered)
- ✅ Target variable is 'residual'
- ✅ mean ≈ 0 (slight deviation due to random split is normal)

---

## STEP 10: MONITOR STEP [6/7] — QUICK RANDOM FOREST

**What you see (takes ~60-90 seconds):**
```
[6/7] Quick Random Forest — feature importance ranking...
    ✓ RF train R² (on residuals): 0.9157
    ✓ RF test  R² (on residuals): 0.4697
    ✓ RF test RMSE:               0.3415 mg/g

    Top 15 features:
    Rank  Feature                        Importance  Cum%
    ───────────────────────────────────────────────────────
    1     pH_abs_dev                       0.2204   22.0%
    2     pH_dev_sq                        0.2078   42.8%
    3     pH_gaussian                      0.0994   52.8%
    4     pH                               0.0745   60.2%
    5     pH_dev                           0.0605   66.3%
    ...
```

**What to check:**
- ✅ Train R² > 0.85 (confirms features are useful)
- ✅ Test R² > 0.35 (confirms generalisation exists)
- ✅ Top 3 features are all pH-related
- ✅ pH_abs_dev and pH_dev_sq are #1 and #2

**Understanding the train-test gap (0.9157 vs 0.4697):**
```
Gap = 0.45 → looks large but is EXPECTED because:
  1. No hyperparameter tuning yet (Phase 4 will fix this)
  2. Quick RF uses max_depth=8 → overfits
  3. Residual prediction is inherently harder than q prediction
  4. Phase 4 with CV and tuning will close this gap
  
Bottom line: test R² = 0.47 is still meaningful!
```

---

## STEP 11: MONITOR STEP [7/7] — SAVING OUTPUTS

**What you see:**
```
[7/7] Saving results and creating visualisations...
    ✓ Saved: results/ml_training_data.csv  ((400, 39))
    ✓ Saved: results/ml_test_data.csv       ((100, 39))
    ✓ Saved: results/feature_importance.csv ((38, 4))
    ✓ Saved: results/residual_analysis.json
    ✓ Saved: results/phase3_diagnostics.png  (6-panel plot)
```

**Then the final summary:**
```
================================================================================
✅  PHASE 3 COMPLETE: RESIDUAL ANALYSIS & FEATURE ENGINEERING
================================================================================

Key Findings:
  → pH is the dominant residual driver
  → pH 4-5:   mean residual = -0.525 mg/g  (model overestimates)
  → pH 6.5-7: mean residual = +0.649 mg/g  (model underestimates — ML goldmine)
  → 28 new features engineered from 10 original factors
  → Top feature: pH_abs_dev  (importance=0.2204)
  → Quick RF on residuals: train R²=0.9157, test R²=0.4697

Output Files:
  ✓ results/ml_training_data.csv   (400 samples × 38 features)
  ✓ results/ml_test_data.csv        (100 samples × 38 features)
  ✓ results/feature_importance.csv  (38 features ranked)
  ✓ results/residual_analysis.json  (full metadata)
  ✓ results/phase3_diagnostics.png  (6-panel diagnostics)
```

---

## STEP 12: VERIFY OUTPUT FILES

**Check all 5 files created:**
```bash
ls -lh results/
```

**Expected:**
```
-rw-r--r-- 1 user group 186K May 5 13:20 results/ml_training_data.csv
-rw-r--r-- 1 user group  47K May 5 13:20 results/ml_test_data.csv
-rw-r--r-- 1 user group   2K May 5 13:20 results/feature_importance.csv
-rw-r--r-- 1 user group   1K May 5 13:20 results/residual_analysis.json
-rw-r--r-- 1 user group 500K May 5 13:20 results/phase3_diagnostics.png
```

**Verify CSV structure:**
```python
import pandas as pd, json

train = pd.read_csv('results/ml_training_data.csv')
test  = pd.read_csv('results/ml_test_data.csv')
feat  = pd.read_csv('results/feature_importance.csv')

print(f"Train: {train.shape}  (expected 400 × 39)")
print(f"Test:  {test.shape}   (expected 100 × 39)")
print(f"Feat:  {feat.shape}   (expected 38 × 4)")
print(f"Train residual std: {train['residual'].std():.4f}")
print(f"Top feature: {feat.iloc[0]['feature']} ({feat.iloc[0]['importance']:.4f})")

with open('results/residual_analysis.json') as f:
    meta = json.load(f)
print(f"Top feature from JSON: {meta['key_findings']['top_feature']}")
print(f"pH 6.5-7 mean residual: {meta['key_findings']['pH_6p5_7_mean_residual']:.4f}")
```

**Expected:**
```
Train: (400, 39)  ✓
Test:  (100, 39)  ✓
Feat:  (38, 4)    ✓
Train residual std: 0.54xx
Top feature: pH_abs_dev (0.2204)
Top feature from JSON: pH_abs_dev
pH 6.5-7 mean residual: 0.6491
```

**Open diagnostic plot:**
```bash
# Linux/Mac
open results/phase3_diagnostics.png
# OR
display results/phase3_diagnostics.png
```

---

## COMPLETE SUCCESS CHECKLIST

**Setup:**
- ☑ Phase 2 CSV loaded (500 rows, 15 columns)
- ☑ Dependencies installed (sklearn, scipy, matplotlib)
- ☑ data/ and results/ directories exist
- ☑ Script in working directory

**Execution:**
- ☑ All 7 steps complete without errors
- ☑ pH pattern confirmed (6.5-7 highest positive bar)
- ☑ 38 features created (10 original + 28 engineered)
- ☑ pH_optimal correlation > 0.40
- ☑ Top features are pH-based
- ☑ Train R² > 0.85, Test R² > 0.35

**Outputs:**
- ☑ ml_training_data.csv (400 × 39) ✓
- ☑ ml_test_data.csv (100 × 39) ✓
- ☑ feature_importance.csv (38 × 4) ✓
- ☑ residual_analysis.json ✓
- ☑ phase3_diagnostics.png (6 panels) ✓

**Understanding:**
- ☑ You know why pH is the dominant signal
- ☑ You understand why linear correlations are all zero
- ☑ You understand the train/test gap (overfitting = normal at Phase 3)
- ☑ You know how Phase 4 will improve the RF results
- ☑ You know the hybrid model path to R² ≥ 0.94

**IF ALL CHECKED: ✅ PHASE 3 COMPLETE!**

---

## TROUBLESHOOTING

| Error | Cause | Fix |
|-------|-------|-----|
| `FileNotFoundError: data/langmuir_predictions.csv` | Wrong path | `mkdir -p data && cp /path/to/file data/` |
| `ModuleNotFoundError: sklearn` | Not installed | `pip install scikit-learn` |
| `TypeError: cut() got unexpected argument 'q'` | Older script version | Use qcut() instead of cut() for quartiles |
| Train R² < 0.70 | Features not computed right | Print first 5 rows of engineered features |
| Test R² < 0.20 | Severe overfitting | Reduce max_depth to 4 in Quick RF |
| Missing output files | Permission error | `chmod 755 results/` and re-run |
| Plot looks empty | Matplotlib backend | Add `matplotlib.use('Agg')` before imports |

---

## PREPARING FOR PHASE 4

**Files you'll use:**
```
results/ml_training_data.csv  → X_train + y_train
results/ml_test_data.csv      → X_test + y_test
results/feature_importance.csv → Feature selection guidance
results/residual_analysis.json → Baseline metrics reference
```

**What Phase 4 does:**
```
1. Loads ml_training_data.csv and ml_test_data.csv
2. Trains Random Forest with 5-fold CV and hyperparameter tuning
3. Trains XGBoost with 5-fold CV
4. Trains MLP Neural Network
5. Selects best model (expected winner: XGBoost)
6. Produces residual predictions for all 500 points
7. Passes to Phase 5 for hybrid combination

Expected Phase 4 improvements:
  Phase 3 Quick RF test R²: 0.4697
  Phase 4 tuned RF test R²: 0.65–0.70
  Phase 4 XGBoost test R²:  0.68–0.75  ← likely winner
  Phase 4 MLP test R²:      0.55–0.68
```

**Phase 5 projection:**
```
If Phase 4 achieves R²(residuals) = 0.72:
  Additional variance = 0.72 × 18.42% = 13.3%
  Hybrid R² = 0.8158 + 0.133 = 0.949 → EXCEEDS 0.94!
```

---

🎉 **Phase 3 Complete! You're 50% through the 8-phase project.**

EOF
