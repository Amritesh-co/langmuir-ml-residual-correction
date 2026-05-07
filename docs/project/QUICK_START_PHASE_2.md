# ⚡ QUICK START: PHASE 2 LANGMUIR FITTING

**Ready to proceed?** Copy/paste these commands:

---

## STEP 1: Setup (1 minute)

```bash
# Navigate to your project directory
cd fluoride-hybrid-physics-ml

# Create data and results directories if needed
mkdir -p data results

# Make sure your CSV files are in the data/ folder
ls data/*.csv
# Should show:
# - doe_lhs_500.csv
# - dataset_simulated_500.csv
```

---

## STEP 2: Install Dependencies (2 minutes)

```bash
# Activate your Python environment
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Install required packages
pip install scikit-learn scipy matplotlib pandas numpy
```

---

## STEP 3: Run Phase 2 (30-60 minutes)

```bash
# Copy the script to your project
cp phase2_langmuir_fitting.py your_project_dir/

# Run it
python phase2_langmuir_fitting.py
```

**What you'll see:**

```
================================================================================
PHASE 2: LANGMUIR FITTING - MULTI-FACTOR ANALYSIS
Fluoride Adsorption on Coconut Husk Activated Carbon
================================================================================

[1/6] Loading dataset...
    ✓ Loaded 500 samples
    ✓ Response range: 1.644 - 8.316 mg/g

[2/6] Preparing features...
    ✓ Features: 10 factors
    ✓ Samples: 500 data points

[3/6] Fitting multi-factor Langmuir model...
    ✓ Model fitted

[4/6] Evaluating model performance...
    
    Model Performance Metrics:
    ────────────────────────────────────────
    R² (Coefficient of Determination): 0.8456 (84.56%)
    RMSE (Root Mean Squared Error):     0.9231 mg/g
    MAE (Mean Absolute Error):          0.7145 mg/g

[5/6] Saving results...
    ✓ Saved: results/langmuir_predictions.csv
    ✓ Saved: results/langmuir_model_info.json

[6/6] Creating diagnostic plots...
    ✓ Saved: results/langmuir_diagnostics.png

================================================================================
✅ PHASE 2 COMPLETE: LANGMUIR FITTING
================================================================================
```

---

## STEP 4: Verify Results (5 minutes)

```bash
# Check that all output files were created
ls -lh results/
# Should show:
# - langmuir_predictions.csv (40-50 KB)
# - langmuir_model_info.json (0.5-1 KB)
# - langmuir_diagnostics.png (50-100 KB)

# Preview the predictions
head -5 results/langmuir_predictions.csv

# View the model info
cat results/langmuir_model_info.json

# View the diagnostic plot (open in image viewer)
open results/langmuir_diagnostics.png  # macOS
# or
xdg-open results/langmuir_diagnostics.png  # Linux
# or
start results/langmuir_diagnostics.png  # Windows
```

---

## WHAT TO EXPECT

### R² Value
- **Expected:** 0.84-0.87 (good!)
- **Meaning:** Chemical model explains 84-87% of variance
- **Interpretation:** ✓ Langmuir is appropriate

### RMSE Value
- **Expected:** 0.90-1.20 mg/g
- **Meaning:** Average prediction error is ~1 mg/g
- **Interpretation:** ✓ Acceptable baseline

### Diagnostic Plots (4 panels)
1. **Actual vs Predicted:** Should follow diagonal line ✓
2. **Residual Plot:** Should show random scatter around 0 ✓
3. **Residual Distribution:** Should be roughly bell-shaped ✓
4. **Q-Q Plot:** Should be roughly linear ✓

---

## TROUBLESHOOTING

### ImportError: No module named 'sklearn'
```bash
pip install scikit-learn
```

### FileNotFoundError: data/dataset_simulated_500.csv
```bash
# Make sure CSV files are in data/ folder
ls data/dataset_simulated_500.csv  # Should exist
```

### Script runs but no results folder created
```bash
mkdir -p results
python phase2_langmuir_fitting.py
```

### Plot file is very small or blank
- Check that matplotlib backend is working
- Try: `python -c "import matplotlib; print(matplotlib.get_backend())"`

---

## NEXT STEPS AFTER PHASE 2

✅ **Phase 2 Complete** → What's next?

### Option A: Proceed to Phase 3 (Recommended)
```bash
# Phase 3: Residual Analysis
python phase3_residual_analysis.py
```

### Option B: Explore Phase 2 Results First
```bash
# Analyze the predictions
python -c "
import pandas as pd
df = pd.read_csv('results/langmuir_predictions.csv')
print('Summary Statistics:')
print(df[['q_removal', 'q_predicted', 'residual']].describe())
"
```

### Option C: Create Custom Analysis
```bash
# Jupyter notebook for deep dive
jupyter notebook
# Then open a new notebook and import:
# import pandas as pd
# results = pd.read_csv('results/langmuir_predictions.csv')
```

---

## SUCCESS CHECKLIST

- [ ] Phase 2 script runs without errors
- [ ] Output files created in results/ folder
- [ ] R² value is 0.80-0.90 (good baseline)
- [ ] RMSE is < 1.5 mg/g
- [ ] Diagnostic plots look reasonable
- [ ] Residuals appear randomly distributed
- [ ] You understand what Langmuir model captures
- [ ] You're ready for ML training (Phase 4)

---

## TYPICAL TIMELINE

| Step | Time | Status |
|------|------|--------|
| Setup | 1 min | ⚡ |
| Install packages | 2 min | ⚡ |
| Run script | 45 min | 🔄 |
| Verify results | 5 min | ⚡ |
| **Total** | **~1 hour** | ✅ |

---

## KEY NUMBERS TO REMEMBER

After Phase 2 completes, write down these numbers:

```
R² = _________     (aim for 0.84+)
RMSE = _________   (aim for <1.2)
MAE = _________    (aim for <0.8)
Residual Std = ___ (this is what ML learns to predict)
```

These become your **baseline** for Phase 4-5.

---

## FINAL NOTES

**You're on track!** 🚀

Phase 1 ✅ → Phase 2 (NOW) → Phase 3-8 (coming)

After Phase 2, you'll have:
- ✅ Baseline chemical model
- ✅ Residuals to analyze
- ✅ Clear ML opportunities
- ✅ Foundation for hybrid model

**Ready?** Run the script above! 🎯

---

**Still have questions?** 
See: `PHASE_2_LANGMUIR_GUIDE.md` for complete documentation

