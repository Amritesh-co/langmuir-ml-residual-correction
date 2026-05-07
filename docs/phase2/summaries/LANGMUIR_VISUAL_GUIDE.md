# 📊 LANGMUIR FITTING: VISUAL & FLOWCHART GUIDE

**Diagrams, flowcharts, and visual explanations for Phase 2**

---

## 1. OVERALL PHASE 2 WORKFLOW

```
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 2: LANGMUIR FITTING                    │
│                     Input: 500 Samples Data                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    [1] LOAD DATA (500 × 13)                     │
│                                                                 │
│  Columns: Run, pH, C0, Time, Dose, Temp, Flow, Cl, Hard, CO3,  │
│           NOM, Order, q_removal                                 │
│                                                                 │
│  Data: 500 samples × 13 columns                                 │
│  Response: q_removal (1.6 - 8.3 mg/g)                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              [2] STANDARDIZE FEATURES & RESPONSE                │
│                                                                 │
│  Input X: 500 × 10 (factors)                                    │
│  Input y: 500 × 1 (q_removal)                                   │
│                                                                 │
│  X_scaled = (X - mean) / std  →  mean=0, std=1                 │
│  y_scaled = (y - mean) / std  →  mean=0, std=1                 │
│                                                                 │
│  Output: X_scaled (500 × 10), y_scaled (500 × 1)               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│         [3] CREATE POLYNOMIAL FEATURES (Degree 2)               │
│                                                                 │
│  Input:  10 factors (pH, C0, Time, ...)                         │
│  Add:    10 squared terms (pH², C0², Time², ...)                │
│  Add:    45 interaction terms (pH×C0, pH×Time, ...)             │
│                                                                 │
│  Output: 66 polynomial features                                 │
│  Ratio:  500 samples / 66 features = 7.6 (good!)              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│         [4] FIT LINEAR REGRESSION MODEL                         │
│                                                                 │
│  Minimize: Σ(y_scaled - ŷ)²                                    │
│                                                                 │
│  Method: Ordinary Least Squares (OLS)                           │
│  β = (X^T X)^(-1) X^T y                                         │
│                                                                 │
│  Output: 67 coefficients (β₀ + 66 β's)                         │
│          (Linear regression model fitted!)                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              [5] MAKE PREDICTIONS                               │
│                                                                 │
│  ŷ_scaled = X_poly @ β  (matrix multiplication)                │
│                                                                 │
│  ŷ = scaler_y.inverse_transform(ŷ_scaled)                      │
│     (Convert back to original units: mg/g)                      │
│                                                                 │
│  Output: 500 predictions (in mg/g)                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│            [6] CALCULATE PERFORMANCE METRICS                    │
│                                                                 │
│  R² = 1 - (SS_res / SS_tot)           Expected: 0.84-0.87      │
│  RMSE = √(Σ(y - ŷ)² / n)             Expected: 0.9-1.2 mg/g  │
│  MAE = Σ|y - ŷ| / n                  Expected: 0.7-0.9 mg/g  │
│  Residuals = y - ŷ                   Expected: Normal, σ≈0.92 │
│                                                                 │
│  Output: Metrics + Residuals (500 values)                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│            [7] CREATE DIAGNOSTIC PLOTS                          │
│                                                                 │
│  Panel 1: Actual vs Predicted                                   │
│  Panel 2: Residuals vs Predicted                                │
│  Panel 3: Residual Distribution                                 │
│  Panel 4: Q-Q Plot                                              │
│                                                                 │
│  Output: 4-panel PNG image                                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 2 COMPLETE ✅                          │
│                                                                 │
│  Output Files:                                                  │
│  ✓ langmuir_predictions.csv (500 × 15 columns)                │
│  ✓ langmuir_model_info.json (metadata)                         │
│  ✓ langmuir_diagnostics.png (4 plots)                          │
│                                                                 │
│  Results:                                                       │
│  ✓ R² ≈ 0.85 (Langmuir baseline)                               │
│  ✓ RMSE ≈ 0.92 mg/g (prediction error)                         │
│  ✓ Residuals analyzed (ready for Phase 3)                      │
│                                                                 │
│  Next: Phase 3 - Residual Analysis & Feature Engineering       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. DATA TRANSFORMATION PIPELINE

```
STAGE 1: INPUT DATA
┌──────────────────────────────┐
│  500 samples × 13 columns    │
├──────────────────────────────┤
│ Run | pH  | C0  | Time | ... │ q_removal
├──────────────────────────────┤
│ 1   | 4.4 | 2.7 | 87   | ... │ 4.23
│ 2   | 4.1 | 3.0 | 97   | ... │ 3.87
│ ... | ... | ... | ...  | ... │ ...
│ 500 | 7.5 | 7.0 | 33   | ... │ 3.49
└──────────────────────────────┘
                ↓
STAGE 2: EXTRACT FACTORS & RESPONSE
┌──────────────────────────┐
│ X: 500 × 10 (factors)    │
│ y: 500 × 1 (response)    │
└──────────────────────────┘
                ↓
STAGE 3: STANDARDIZE (ZERO MEAN, UNIT VARIANCE)
┌──────────────────────────────────────────────┐
│ X_scaled = (X - X.mean()) / X.std()          │
│ y_scaled = (y - y.mean()) / y.std()          │
│                                              │
│ Before: pH ∈ [3, 9],  C0 ∈ [1, 10]          │
│ After:  pH ∈ [-2, 2], C0 ∈ [-2, 2]          │
│ (All factors now have mean=0, std=1)         │
└──────────────────────────────────────────────┘
                ↓
STAGE 4: CREATE POLYNOMIAL FEATURES
┌─────────────────────────────────────────────────────┐
│ Input: 10 factors                                   │
│ ↓                                                   │
│ Add main effects: 10 features                       │
│ Add squared terms: 10 features (pH², C0², ...)      │
│ Add interactions: 45 features (pH×C0, ...)          │
│ ↓                                                   │
│ Output: 66 polynomial features                      │
│                                                     │
│ X_poly shape: 500 × 66                              │
└─────────────────────────────────────────────────────┘
                ↓
STAGE 5: FIT REGRESSION MODEL
┌─────────────────────────────────────────────────────┐
│ LinearRegression().fit(X_poly, y_scaled)            │
│                                                     │
│ Learns: 67 coefficients (β₀ + 66 β's)             │
│                                                     │
│ Model: ŷ_scaled = β₀ + β₁×X_poly₁ + ...           │
└─────────────────────────────────────────────────────┘
                ↓
STAGE 6: MAKE PREDICTIONS
┌─────────────────────────────────────────────────────┐
│ ŷ_scaled = model.predict(X_poly)                    │
│ ŷ = scaler_y.inverse_transform(ŷ_scaled)           │
│                                                     │
│ Output: 500 predictions in original units (mg/g)    │
└─────────────────────────────────────────────────────┘
                ↓
STAGE 7: CALCULATE RESIDUALS
┌─────────────────────────────────────────────────────┐
│ residuals = y - ŷ                                   │
│                                                     │
│ Output: 500 residual values                         │
│ Expected: mean ≈ 0, std ≈ 0.92 mg/g                │
└─────────────────────────────────────────────────────┘
```

---

## 3. THE LANGMUIR MODEL EXPLAINED

### The Equation

```
                qmax × KL × Ce
            q = ──────────────────
                  1 + KL × Ce


Where:
  q    = Amount adsorbed at equilibrium (mg/g)
  qmax = Maximum adsorption capacity (mg/g)
  KL   = Langmuir binding constant (L/mg)
  Ce   = Equilibrium concentration (mg/L)
```

### Shape of the Curve

```
Adsorption Amount (q)
       ▲
       │     ╱─────────────────  qmax (saturation)
       │    ╱
    qmax/2 ├ ─ ─ ─ ┐
       │          ╱│
       │         ╱ │
       │        ╱  │
       │       ╱   │
       │      ╱    │ KL = slope at origin
       │     ╱     │      (higher KL = steeper)
       │    ╱      │
       │   ╱       │
       │  ╱        │
       │ ╱         │
       │╱__________|____▶ Ce (Equilibrium concentration)
       └────────────────
              1/KL
                        (Ce at qmax/2)

Key Points:
  • At Ce = 0: q = 0 (no fluoride in solution = none adsorbs)
  • At Ce = 1/KL: q = qmax/2 (half-saturation point)
  • At Ce → ∞: q → qmax (approaches maximum)

Interpretation:
  • qmax: How much carbon can hold (capacity)
  • KL: How eager carbon is to adsorb (affinity)
  • High KL: Steep curve (better binding)
  • Low KL: Gradual curve (weaker binding)
```

### How Factors Change the Curve

```
Base condition: pH=6.5, temp=25°C, no ions
                    ▲ q
                    │
          qmax=8.5  ├─────────────
                    │ ╱
                    │╱
                    └──────────▶ Ce

Effect of HIGH pH (pH=8):
                    ▲ q
                    │
          qmax=5.0  ├───────
                    │ ╱
                    │╱
                    └──────────▶ Ce
          (qmax decreased, KL decreased)

Effect of HIGH TEMPERATURE (temp=40°C):
                    ▲ q
                    │
          qmax=8.5  ├─────────────
                    │   ╱
                    │  ╱
                    │ ╱
                    │╱
                    └──────────▶ Ce
          (qmax same, KL increased, steeper curve)

Effect of HIGH IONS (Cl⁻=100 mg/L):
                    ▲ q
                    │
          qmax=6.5  ├──────
                    │ ╱
                    │╱
                    └──────────▶ Ce
          (both qmax and KL decreased)
```

---

## 4. FEATURE EXPANSION VISUALIZATION

### From 10 Factors to 66 Features

```
ORIGINAL 10 FACTORS:
┌──────────────────────────────────────────┐
│ 1. pH                                    │
│ 2. C0 (initial concentration)            │
│ 3. Time                                  │
│ 4. Dose                                  │
│ 5. Temperature                           │
│ 6. Flow Rate                             │
│ 7. Chloride                              │
│ 8. Hardness                              │
│ 9. Carbonate                             │
│ 10. NOM (Natural Organic Matter)         │
└──────────────────────────────────────────┘
                   ↓
EXPAND TO 66 FEATURES:

GROUP 1: MAIN EFFECTS (10 features)
├─ pH
├─ C0
├─ Time
├─ Dose
├─ Temperature
├─ Flow Rate
├─ Chloride
├─ Hardness
├─ Carbonate
└─ NOM

GROUP 2: SQUARED TERMS (10 features)
├─ pH²           (captures bell curve: optimal at 6.5)
├─ C0²           (captures saturation effect)
├─ Time²         (captures approach to equilibrium)
├─ Dose²         (captures saturation)
├─ Temperature²  (captures curvature)
├─ Flow Rate²
├─ Chloride²
├─ Hardness²
├─ Carbonate²
└─ NOM²

GROUP 3: INTERACTION TERMS (45 features)
├─ pH × C0         (does concentration matter more at extreme pH?)
├─ pH × Time       (does time matter more at extreme pH?)
├─ pH × Dose       (does dose matter more at extreme pH?)
├─ ... [42 more]
└─ Carbonate × NOM (do ions and fouling interact?)

TOTAL: 1 (intercept) + 10 + 10 + 45 = 66 features
```

### Why Each Type Matters

```
MAIN EFFECTS (pH, C0, Time, ...)
┌───────────────────────────────────────┐
│ Linear relationship with response     │
│                                       │
│ Example: ∂q/∂pH                       │
│ = "How much does q change per unit pH"│
│                                       │
│ Captures: Direct effect of each       │
│ Factor magnitude and direction        │
└───────────────────────────────────────┘

SQUARED TERMS (pH², C0², Time², ...)
┌───────────────────────────────────────┐
│ Non-linear (curved) relationships     │
│                                       │
│ Example: pH²                          │
│ = "pH effect is stronger far from 6.5"│
│                                       │
│ Captures: Bell curves, saturation,    │
│ Inflection points, curvature          │
└───────────────────────────────────────┘

INTERACTION TERMS (pH×C0, pH×Time, ...)
┌───────────────────────────────────────┐
│ One factor modifies another's effect  │
│                                       │
│ Example: pH × Time                    │
│ = "Effect of pH depends on time"      │
│                                       │
│ Meaning: At short times, pH matters    │
│ less. At long times, pH matters more. │
│                                       │
│ Captures: When one factor's effect    │
│ depends on another factor's value     │
└───────────────────────────────────────┘
```

---

## 5. MODEL FITTING VISUALIZATION

### Before and After Scaling

```
BEFORE SCALING (Original Units):
┌─────────────────────────────────────┐
│ Factor values span different ranges: │
│                                      │
│ pH:    3 to 9        (range = 6)     │
│ C0:    1 to 10       (range = 9)     │
│ Time:  10 to 120     (range = 110)   │
│ Temp:  20 to 40      (range = 20)    │
│ NOM:   0 to 50       (range = 50)    │
│                                      │
│ Problem:                             │
│ • Can't compare coefficients directly │
│ • Optimization is slow & unstable    │
│ • Some coefficients are tiny (pH)    │
│   others are large (Time)            │
└─────────────────────────────────────┘
                ↓
AFTER SCALING (Standardized):
┌─────────────────────────────────────┐
│ All factors have same range:         │
│                                      │
│ pH_scaled:    -2 to 2   (std=1)      │
│ C0_scaled:    -2 to 2   (std=1)      │
│ Time_scaled:  -2 to 2   (std=1)      │
│ Temp_scaled:  -2 to 2   (std=1)      │
│ NOM_scaled:   -2 to 2   (std=1)      │
│                                      │
│ Benefit:                             │
│ • Coefficients are comparable        │
│ • Optimization is fast & stable      │
│ • Can see relative importance        │
└─────────────────────────────────────┘

EXAMPLE COEFFICIENTS (Scaled):
┌──────────────────────────────────┐
│ β_pH = 0.15    (moderate effect) │
│ β_C0 = 0.42    (strong effect)   │
│ β_Time = 0.58  (strongest effect)│
│ β_Temp = 0.08  (weak effect)     │
│                                  │
│ Interpretation:                  │
│ Time is 5.8× more important      │
│ than Temperature (per std dev)   │
└──────────────────────────────────┘
```

### The Fitting Process

```
INITIALIZATION:
┌─────────────────────────────────┐
│ Random initial guess for β's    │
│ Model prediction very poor      │
│ Error (SSE) is huge             │
└─────────────────────────────────┘
        ↓ [Fit using OLS]
ITERATION 1:
┌─────────────────────────────────┐
│ Update β's to minimize error    │
│ Error decreases                 │
│ (Closed-form solution, so done  │
│  in 1 step! Not iterative.)     │
└─────────────────────────────────┘
        ↓ [Final β's found]
CONVERGENCE:
┌─────────────────────────────────┐
│ Final β coefficients found      │
│ Error minimized                 │
│ R² calculated                   │
│ Done! (Happens in milliseconds) │
└─────────────────────────────────┘
```

---

## 6. EXPECTED PERFORMANCE METRICS

### R² Interpretation

```
R² = 0.85 (Expected)

    Explained Variance    85%
    ┌─────────────────────────────────────────────────────────┐
    │██████████████████████████████████████████████░░░░░░░░░░│
    │                                                          │
    │ Langmuir explains this much (good for Phase 2)          │
    │                                                          │
    │                    Residual Variance     15%            │
    │                    ▲                                    │
    │                    │ (ML will learn this in Phase 4)    │
    └─────────────────────────────────────────────────────────┘


Comparison to Other Models:
┌────────────────────────────────────┐
│ Simple average (q_mean):      R²=0 │
│ Simple 2-param Langmuir:      R²≈0.50 │
│ Our multi-factor Langmuir:    R²≈0.85 ✓ (Expected)
│ After ML correction:          R²≈0.94 (Phase 5 target)
│ Perfect fit:                  R²=1.00 │
└────────────────────────────────────┘
```

### RMSE Interpretation

```
RMSE = 0.92 mg/g (Expected)

Your data range: 1.64 - 8.32 mg/g
              ▲
           8.5│                     ┌─ Maximum value
              │                     │
           7.0│          ╱‾‾‾‾╲     │
              │         ╱      ╲    │
           5.5│        │  Data  │   │ Range = 6.68 mg/g
              │        │ Range  │   │
           4.0│         ╲      ╱    │
              │          ╲____╱     │
           2.5│                     │
              │                     │
           1.0└─────────────────────│─ Minimum value
              └──────────────────────▶


RMSE = 0.92 represents average prediction error

If prediction is 4.2 mg/g:
  Actual could be: 4.2 ± 0.92 = [3.28 to 5.12] mg/g
  (68% confidence, ±1σ)

Or: 4.2 ± 1.84 = [2.36 to 6.04] mg/g
    (95% confidence, ±2σ)


Error as % of range:
┌─────────────────────────────────┐
│ RMSE / Range = 0.92 / 6.68      │
│              = 13.8%            │
│                                 │
│ Interpretation:                 │
│ ✓ Excellent (< 10%): Ultra-precise
│ ✓ Good (10-20%): Our range ✓
│ ~ Acceptable (20-30%): Workable
│ ✗ Poor (> 30%): Needs improvement
└─────────────────────────────────┘
```

---

## 7. DIAGNOSTIC PLOTS INTERPRETATION

### Panel 1: Actual vs Predicted

```
GOOD FIT:                          BAD FIT:
Predicted                          Predicted
   ▲                                  ▲
 8 │    ╱╱╱╱╱╱╱╱                   8 │        ╱
   │   ╱  ●●●●●●●                   │       ╱●
 6 │  ╱  ●●●●●●●                   6 │      ╱  ●●
   │ ╱  ●●●●●●●                     │     ╱    ●●
 4 │╱   ●●●●●●●   (follows line)   4 │╱ ●●●● ╱   (above line)
   │    ●●●●●●● ╱                   │ ●●●●   ╱
 2 │     ●●●●╱ ╱                   2 │●●  ╱ ╱
   │        ╱╱                       │   ╱╱
 0 └────────────────▶ Actual       0 └──────────────▶ Actual
   0      2    4   6    8            0    2  4   6   8

Points close to line = Good predictions
Points far from line = Poor predictions
```

### Panel 2: Residuals vs Predicted

```
GOOD (Random scatter):           BAD (Funnel shape):
Residual                         Residual
   ▲                                ▲
 2 │     ●     ●                  2 │  ●    ●
   │   ●   ●     ● ●                │    ●     ●
 0 │──●───●───●───●──────          0 │─●──●─────────
   │   ●   ●     ● ●                │    ●     ●●
-2 │     ●     ●                  -2 │  ●  ●●●●●
   │                                │
 -4 └──────────────────▶ Predicted -4 └──────────────────▶ Predicted
     0    2   4   6   8               0    2   4   6   8

GOOD:                            BAD:
• Random around zero ✓           • Error increases with size ✗
• Constant width ✓               • Funnel pattern ✗
• No patterns ✓                  • Heteroscedasticity ✗
• No curvature ✓                 • May indicate model issue ✗
```

### Panel 3: Residual Distribution

```
GOOD (Normal distribution):      BAD (Skewed):
Frequency                        Frequency
    ▲                                ▲
 60 │       ╱╲                    60 │    ╱╲
    │      ╱  ╲                      │   ╱  ╲╱
 40 │     ╱    ╲                  40 │  ╱    ╲
    │    ╱      ╲                    │ ╱      ╲
 20 │   ╱        ╲                20 │╱        ╲
    │  ╱          ╲                  │          ╲
  0 └─────────────────              │           ╲___
    -2   -1   0   1   2                -2  -1  0  1   2
           Residuals                         Residuals

GOOD:                            BAD:
• Bell shape ✓                   • Skewed right ✗
• Centered at 0 ✓                • Long tail ✗
• Symmetric ✓                    • May indicate outliers ✗
• No extreme outliers ✓          • Need investigation ✗
```

### Panel 4: Q-Q Plot

```
GOOD (Linear):                   BAD (S-shaped):
Sample                           Sample
   ▲                                ▲
 3 │         ●●                  3 │      ●●
   │      ●●  ●                    │    ●●
 2 │   ●●      ●                2 │  ●●    ●
   │ ●●        │                   │●●      │
 1 │●         ●                 1 │         ●
   │●          │                   │        ●│
 0 ├──────────────                0 ├──●────────
   │          ●                    │    ●●●  │
-1 │        ●  ●                -1 │   ●    ●
   │    ●●    ●                    │  ●     ●
-2 │  ●●                        -2 │ ●
   │●                              │●●
-3 └──────────────────▶ Theoretical-3 └──────────────────▶ Theoretical

GOOD:                            BAD:
• Points follow line ✓           • S-shape ✗
• Minor tail deviations OK       • Non-normal ✗
• Linear ✓                       • Heavy tails ✗
• Approximately normal ✓         • May need transformation ✗
```

---

## 8. EXPECTED OUTPUT FILES

### File 1: langmuir_predictions.csv

```
Structure: 500 rows × 15 columns

Sample rows:
┌────┬──────┬─────┬──────┬──────┬──────┬──────┬──────┬─────┬───┬─────┬──────┬──────┬──────────┬────────┐
│Run │  pH  │ C0  │Time  │Dose  │Temp  │Flow  │Cl    │Hard │CO3│ NOM │Order │q_rem │q_pred  │residual│
├────┼──────┼─────┼──────┼──────┼──────┼──────┼──────┼─────┼───┼─────┼──────┼──────┼──────────┼────────┤
│1   │ 4.39 │2.65 │87    │2.48  │34.2  │0.709 │0     │49   │7   │11   │361   │4.231 │ 4.148  │-0.083  │
│2   │ 4.12 │2.99 │97    │4.1   │35.7  │0.651 │63    │280  │1   │15   │73    │3.872 │ 3.923  │+0.051  │
│3   │ 8.17 │4.68 │92    │1.72  │36.0  │0.537 │18    │23   │40  │24   │374   │0.985 │ 1.132  │+0.147  │
│..  │ ...  │...  │...   │...   │...   │...   │...   │...  │... │...  │...   │...   │ ...    │ ...    │
│500 │ 7.51 │7.02 │33    │2.75  │28.5  │1.725 │61    │376  │55  │16   │102   │3.487 │ 3.542  │+0.055  │
└────┴──────┴─────┴──────┴──────┴──────┴──────┴──────┴─────┴───┴─────┴──────┴──────┴──────────┴────────┘

Use in Phase 3:
  • Identify patterns in residuals
  • Find where model struggles (largest |residual|)
  • Analyze by pH, time, dose, etc.
```

### File 2: langmuir_model_info.json

```
{
  "phase": "Phase 2: Langmuir Fitting",
  "date": "2026-05-03",
  "n_samples": 500,
  "n_factors": 10,
  "n_features_original": 10,
  "n_features_expanded": 66,
  "model_type": "Multi-factor Langmuir (Polynomial degree 2)",
  "scaling": "StandardScaler (both X and y)",
  "performance_metrics": {
    "R2": 0.8456,           ← Most important
    "RMSE": 0.9231,         ← Prediction error
    "MAE": 0.7145,          ← Mean absolute error
    "residual_mean": -0.000001,  ← Should be ~0
    "residual_std": 0.9228  ← Residual spread
  }
}

Use in Phase 3-5:
  • Reference baseline metrics
  • Compare with Phase 4 ML model
  • Track improvement to hybrid model
```

### File 3: langmuir_diagnostics.png

```
4-panel diagnostic plot showing:

Panel 1: Actual vs Predicted       Panel 2: Residuals vs Predicted
  (Should follow diagonal)           (Should scatter around 0)
      8│     ╱                           2│     ●
       │    ╱ ●                          │   ●   ●
       │   ╱ ●●●                       0│──●───●───●──
       │  ╱ ●●●                         │   ●   ●
    0  │ ╱●                            -2│     ●
       └──────────▶                      └──────────▶

Panel 3: Residual Distribution    Panel 4: Q-Q Plot
  (Should be bell curve)           (Should be linear)
       │   ╱╲                          │       ●●
       │  ╱  ╲                         │     ●●
       │ ╱    ╲                        │   ●●
       │╱      ╲                       │  ●
       └─────────                      │ ●
       -2  0   2                       └───────────▶
```

---

## 9. SUMMARY TABLE

```
┌─────────────────────────────────────────────────────────────────┐
│                      PHASE 2 SUMMARY                            │
├─────────────────────────┬───────────────────────────────────────┤
│ ASPECT                  │ DETAILS                               │
├─────────────────────────┼───────────────────────────────────────┤
│ INPUT                   │ 500 samples, 10 factors, q_removal    │
│ PROCESS                 │ Standardize → Polynomial → Fit        │
│ MODEL                   │ Multi-factor Langmuir (66 features)   │
│ METHOD                  │ Linear Regression (OLS)               │
│ PARAMETERS              │ 67 coefficients (β₀ + β₁...β₆₆)      │
│ EXPECTED R²             │ 0.84-0.87 (84-87% explained)         │
│ EXPECTED RMSE           │ 0.9-1.2 mg/g                          │
│ EXPECTED MAE            │ 0.7-0.9 mg/g                          │
│ RESIDUALS               │ Normal, random, σ≈0.92 mg/g           │
│ OUTPUT FILES            │ CSV, JSON, PNG                        │
│ RUNTIME                 │ < 1 minute (mostly for visualization) │
│ STATUS                  │ Baseline model (R² ≈ 0.85)            │
│ NEXT PHASE              │ Phase 3: Residual Analysis            │
└─────────────────────────┴───────────────────────────────────────┘
```

---

## 10. PHASE 2 → PHASE 3 TRANSITION

```
After Phase 2:
┌─────────────────────────────────────────────────────────────┐
│                    BASELINE ESTABLISHED                     │
├─────────────────────────────────────────────────────────────┤
│ ✅ Langmuir model fitted                                    │
│ ✅ R² = 0.85 (What chemistry can do)                        │
│ ✅ Residuals = 0.92 mg/g (What ML needs to learn)           │
│ ✅ 500 predictions made                                     │
│ ✅ Diagnostic plots created                                │
│                                                             │
│ Question for Phase 3:                                       │
│ "Where are the patterns in residuals?"                     │
│ "What is the model missing?"                               │
│ "What can ML learn?"                                        │
└─────────────────────────────────────────────────────────────┘
                          ↓
                    PHASE 3 WORK:
        Analyze residuals by factor combinations
        Find non-linear patterns chemistry missed
        Engineer features to capture those patterns
        Prepare training data for ML models
                          ↓
                   PHASE 4 WORK:
        Train Random Forest, XGBoost, MLP on residuals
        Cross-validate (5-fold CV)
        Select best model
        Expected: R² ≈ 0.90-0.93 on residual prediction
                          ↓
                   PHASE 5 WORK:
        Hybrid = Langmuir + ML residual prediction
        Combine: q_hybrid = q_langmuir + q_ml_correction
        Achieve: R² ≥ 0.94 (Target!)
                          ↓
        🎉 SUCCESS: Hybrid model 20-35% better than chemistry!
```

---

**End of Visual & Flowchart Guide**

This document provides visual representations, flowcharts, and diagrams for understanding Phase 2 Langmuir fitting.

EOF
cat /mnt/user-data/outputs/LANGMUIR_VISUAL_GUIDE.md
