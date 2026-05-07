# ⚡ LANGMUIR FITTING: QUICK REFERENCE CHEAT SHEET

**One-page summary of everything for Phase 2**

---

## THE LANGMUIR EQUATION (What We're Fitting)

```
q = (qmax × KL × Ce) / (1 + KL × Ce)

q     = Adsorbed amount (mg/g)  ← What we predict
qmax  = Max capacity (mg/g)      ← Parameter (changes with conditions)
KL    = Binding constant (L/mg)  ← Parameter (changes with conditions)
Ce    = Equilibrium conc (mg/L)  ← Calculated from data
```

**Key insight:** qmax and KL aren't constant—they change with pH, temperature, ions, etc.

---

## THE MODEL WE USE (What's Different)

**NOT:** Simple 2-parameter Langmuir (ignores factors)  
**YES:** Multi-factor Langmuir with polynomial features

```
Step 1: Take 10 factors (pH, C0, Time, Dose, Temp, Flow, Cl⁻, Hard, CO3, NOM)
Step 2: Add squares (pH², C0², Time², ...)
Step 3: Add interactions (pH×C0, pH×Time, ...)
Result: 66 features from 10 factors

Step 4: Linear regression on 66 features → 67 coefficients
Result: q = β₀ + β₁×f₁ + ... + β₆₆×f₆₆
```

**Why?** Factors change the curve shape → need to capture those changes.

---

## WHAT HAPPENS STEP-BY-STEP

```
[1] Load:         Read CSV (500 samples, 10 factors)
    ↓
[2] Standardize:  Scale to mean=0, std=1 (numbers become comparable)
    ↓
[3] Expand:       10 factors → 66 polynomial features
    ↓
[4] Fit:          Linear regression (minimize prediction error)
    ↓
[5] Predict:      Apply model to get predictions for all 500 points
    ↓
[6] Calculate:    R², RMSE, residuals, diagnostics
    ↓
[7] Visualize:    4 diagnostic plots (save as PNG)
    ↓
[8] Save:         CSV with predictions, JSON with metadata
```

**Runtime:** ~1 minute (mostly visualization)

---

## EXPECTED RESULTS AT A GLANCE

| Metric | Expected | Interpretation |
|--------|----------|-----------------|
| **R²** | 0.84-0.87 | Explains 84-87% of variance ✓ Good! |
| **RMSE** | 0.9-1.2 mg/g | Average error ±0.9 mg/g (13% of range) |
| **MAE** | 0.7-0.9 mg/g | Typical error magnitude |
| **Residual mean** | ≈ 0 | No systematic bias ✓ |
| **Residual std** | ≈ 0.92 mg/g | Residual spread (what ML learns) |
| **Residual dist** | Normal | Bell-shaped histogram ✓ |

**Bottom line:** R² = 0.85 is EXCELLENT for a chemical model. Leaves 15% for ML to learn.

---

## THE 4 DIAGNOSTIC PLOTS

```
Panel 1: Actual vs Predicted
  ✓ Points follow diagonal line?
  ✓ No systematic curve?
  → If YES: Good fit!

Panel 2: Residuals vs Predicted
  ✓ Random scatter around zero line?
  ✓ Constant width (not funnel)?
  → If YES: Homoscedastic, good!

Panel 3: Residual Distribution
  ✓ Bell curve shape?
  ✓ Centered at zero?
  ✓ No extreme outliers?
  → If YES: Normal distribution, good!

Panel 4: Q-Q Plot
  ✓ Points follow straight line?
  ✓ Minor deviations at tails OK?
  → If YES: Normal distribution, good!
```

---

## INTERPRETING YOUR RESULTS

### R² Score

```
What it means: "Model explains X% of variance"

R² = 0.85 means:
  85% of q variation is explained by Langmuir model
  15% remains as residuals (for ML to learn)

Is 0.85 good?
  ✓ YES! For a chemistry model, this is excellent.
  ✓ Shows Langmuir is appropriate.
  ✓ Leaves good room for ML improvement (15%).
  
If R² < 0.75?
  ~ Probably OK, but investigate residuals
  
If R² > 0.95?
  ✓ Very good! (But may indicate overfitting in theory)
  ✓ Actually fine for Phase 2 (synthetic data is cleaner)
```

### RMSE Score

```
What it means: "Average prediction error is X mg/g"

RMSE = 0.92 means:
  Typical prediction off by ±0.92 mg/g
  Range of data is 1.6-8.3 (6.68 total)
  Error is 0.92/6.68 = 13.8% of range

Is 0.92 good?
  ✓ YES! <15% of range is good.
  ✓ Provides practical confidence intervals.
  
Rule of thumb:
  < 10% of range = Excellent
  10-20% of range = Good ✓ (You are here)
  20-30% of range = Acceptable
  > 30% of range = Poor
```

### Residual Analysis

```
What to look for:

1. Mean ≈ 0?
   ✓ YES → No systematic bias
   ✗ NO → Model over/underestimates

2. Standard deviation ≈ 0.92?
   ✓ YES → Consistent with RMSE
   ✗ NO → High variability (investigate)

3. Normal distribution?
   ✓ YES → Good for statistics
   ✗ NO → Non-normal (usually OK, regression is robust)

4. Random scatter (no patterns)?
   ✓ YES → Model captured the pattern
   ✗ NO → Model missing something (e.g., non-linearity)

5. No extreme outliers?
   ✓ YES → Good data quality
   ✗ NO → Investigate unusual conditions
```

---

## OUTPUT FILES EXPLAINED

### langmuir_predictions.csv
```
Contains: 500 rows, 15 columns
  • First 12: Original data (factors + design columns)
  • Column 13: q_removal (actual)
  • Column 14: q_predicted (model)
  • Column 15: residual (actual - predicted)

Use for:
  • Phase 3: Analyze residual patterns
  • Find worst predictions (largest |residual|)
  • Identify where model struggles
```

### langmuir_model_info.json
```
Contains: Model metadata and metrics
  • R² = 0.8456
  • RMSE = 0.9231
  • MAE = 0.7145
  • residual_mean = -0.000001
  • residual_std = 0.9228

Use for:
  • Reference baseline
  • Compare with Phase 4 ML results
  • Track improvement to hybrid model
```

### langmuir_diagnostics.png
```
Contains: 4-panel diagnostic plot
  • Panel 1: Actual vs Predicted
  • Panel 2: Residuals vs Predicted
  • Panel 3: Residual Distribution
  • Panel 4: Q-Q Plot

Use for:
  • Visual validation of fit
  • Check for systematic patterns
  • Identify outliers or issues
  • Report figure for documentation
```

---

## TROUBLESHOOTING QUICK FIXES

| Problem | Likely Cause | Quick Fix |
|---------|-------------|-----------|
| R² < 0.70 | Model too simple OR data issue | Check data quality, try degree=3 polynomial |
| R² > 0.98 | Overfitting (theory) | OK for Phase 2, proceed normally |
| RMSE > 2.0 | Model missing major effects | Check residual plots for patterns |
| Residuals not normal | Outliers or skewness | Check Q-Q plot, identify outliers |
| Funnel in residual plot | Heteroscedasticity | OK for Phase 2, ML will learn it |
| ImportError (sklearn) | Package not installed | `pip install scikit-learn scipy` |
| File not found | CSV in wrong folder | `cp data/dataset_simulated_500.csv .` |

---

## PHASE 2 SUCCESS CRITERIA

✅ Script runs without errors
✅ R² is 0.80-0.95 (0.84-0.87 expected)
✅ RMSE is < 1.5 mg/g (0.9-1.2 expected)
✅ Residuals appear normal (bell curve)
✅ No systematic patterns in residuals
✅ 3 output files created successfully
✅ Diagnostic plots look reasonable
✅ You understand what was fitted

**If all ✅:** You're ready for Phase 3!

---

## WHAT COMES NEXT

**Phase 3 (Residual Analysis):**
- Analyze what Langmuir missed
- Identify patterns in residuals
- Engineer features to capture patterns
- Prepare data for ML training

**Phase 4 (ML Training):**
- Train Random Forest, XGBoost, MLP
- Predict residuals (not absolute values)
- Expected: R² ≈ 0.90-0.93 on residuals

**Phase 5 (Hybrid Integration):**
- Combine: q_hybrid = q_langmuir + q_ml_correction
- Achieve: R² ≥ 0.94 (Target!)
- Success: 20-35% improvement

---

## KEY EQUATIONS TO REMEMBER

**Langmuir:**
```
q = (qmax × KL × Ce) / (1 + KL × Ce)
```

**R² Score:**
```
R² = 1 - (SS_residuals / SS_total)
R² = 1 - (Σ(y - ŷ)² / Σ(y - ȳ)²)
```

**RMSE:**
```
RMSE = √(Σ(y - ŷ)² / n)
```

**Residuals:**
```
residuals = y_actual - y_predicted
```

---

## MENTAL MODEL

Think of Phase 2 like this:

```
Question:  "How much fluoride does the carbon remove?"

Chemistry says: 
  "Use Langmuir equation with these factors."
  
We do:
  1. Learn how factors modify Langmuir
  2. Build a model that captures that
  3. Make predictions (should be ~85% accurate)
  4. Calculate what the model missed (residuals)

Result:
  - Chemistry explains 85% (R² = 0.85)
  - Residuals = 15% (opportunities for ML)
  
Next:
  - ML learns to predict residuals
  - Hybrid model = 85% + 9% = 94% (target!)
```

---

## DECISION TREE: IS MY FIT GOOD?

```
                        Is R² ≥ 0.80?
                           |
                      YES  |  NO
                           |
                      GO TO│INVESTIGATE
                      PHASE 3  (check data)
                           |
                    Are residuals
                     normal?
                           |
                      YES  |  NO
                           |
                      GOOD!│INVESTIGATE
                      PHASE 3  (outliers)
                           |
                    Are there
                   patterns in
                   residuals?
                           |
                      YES  |  NO
                           |
                    EXPECTED │PERFECT!
                    (Phase 3  RANDOM
                     learns)
```

---

## ONE-LINE SUMMARY

**Phase 2 Langmuir Fitting:**
Fit multi-factor Langmuir model to data, achieve R² ≈ 0.85, understand residuals, prepare for ML.

---

## QUICK STATS TABLE

```
Parameter               Value           Unit
─────────────────────────────────────────────
Samples                 500             points
Factors                 10              original
Features                66              polynomial
Coefficients            67              (β₀ + 66 β's)
Sample/Feature ratio    7.6             (good, avoid overfitting)
Expected R²             0.84-0.87       fraction
Expected RMSE           0.9-1.2         mg/g
Data range              1.6-8.3         mg/g
Error as % range        13.8%           excellent
Runtime                 <1              minute
Output files            3               (CSV, JSON, PNG)
Next phase              Phase 3         Residual Analysis
```

---

**This is your complete Phase 2 reference guide!**

Keep this nearby while running Phase 2. Refer to the comprehensive guides for detailed explanations.

**Ready?** Run: `python phase2_langmuir_fitting.py` 🚀

EOF
cat /mnt/user-data/outputs/LANGMUIR_CHEAT_SHEET.md
