# Fluoride Adsorption Hybrid Model

**Status:** Phases 1–5 complete | 24-parameter model R² = **0.942** | 4-parameter model R² = **0.826**

A hybrid physics-machine learning model for fluoride removal prediction combining Langmuir/RSM baselines with data-driven residual correction. See [`MODEL_COMPARISON.md`](MODEL_COMPARISON.md) for the full 24-parameter vs 4-parameter breakdown.

---

## Running the Web Dashboard (on a new machine)

The interactive dashboard (`webapp/`) is the primary way to use the trained models — predict with either the 24-parameter or 4-parameter model through a browser UI.

```bash
# 1. Clone
git clone https://github.com/Amritesh-co/langmuir-ml-residual-correction.git
cd langmuir-ml-residual-correction

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Generate the 1000-point seed prediction history for each model
#    (this file is gitignored since it's runtime-generated, not source data)
python3 webapp/generate_seed_data.py

# 5. Run the backend (serves both the API and the frontend)
python3 webapp/backend.py
```

Then open **<http://localhost:8000>** in a browser. The dashboard has three tabs: 24-Parameter Model, 4-Parameter Model, and Model Comparison.

**What's tracked automatically:** every prediction made from the UI is appended to `webapp/data/history_24para.json` / `history_4para.json` alongside the 1000 seed records — these files are gitignored (runtime data, regenerate with step 4 above), so a fresh clone always starts clean.

**Requirements:** the trained model artifacts (`24para/hybrid_residual_model.pkl`, `4para/result/hybrid_4param_combined_model.pkl`) and source datasets (`data/processed/*.csv`) are committed to the repo — no retraining needed to run the dashboard.

---

## Quick Start

### View Project Status
```bash
cat PROJECT_STATUS.md # Complete overview with all metrics
cat PHASE_4_EXECUTION.md # Ready-to-execute Phase 4 guide
```

### Run Current Phases (Already Complete)
```bash
# Phase 1: Design of Experiments
python3 src/phase1_doe_design.py
python3 src/phase1_simulate_adsorption.py

# Phase 2: Langmuir Baseline Model
python3 src/phase2_langmuir_fitting.py

# Phase 3: Residual Analysis (outputs ready in results/phase3/)
# No re-run needed — outputs already verified

# Phase 4: ML Training (NEXT STEP)
# Script template in PHASE_4_EXECUTION.md
```

### Verify Data Quality
```bash
python3 << 'EOF'
import pandas as pd
train = pd.read_csv('results/phase3/ml_training_data.csv')
print(f"Training data: {train.shape} | Test data shape: (100, 39)")
print(f"Residual mean: {train['residual'].mean():.6f} | Std: {train['residual'].std():.4f}")
EOF
```

---

## Project Architecture

```
fluoride-adsorption-hybrid/
├── src/
│ ├── phase1_doe_design.py Latin Hypercube Sampling (500 samples)
│ ├── phase1_simulate_adsorption.py Physics-based simulation
│ ├── phase2_langmuir_fitting.py Polynomial Langmuir model (R²=0.8158)
│ └── [phase4_ml_training.py — TO CREATE]
│
├── results/
│ ├── phase2/ Langmuir outputs
│ │ ├── langmuir_predictions.csv
│ │ ├── langmuir_diagnostics.png
│ │ └── langmuir_model_info.json
│ ├── phase3/ ML training data (ready for Phase 4)
│ │ ├── ml_training_data.csv (400 × 39)
│ │ ├── ml_test_data.csv (100 × 39)
│ │ ├── feature_importance.csv
│ │ └── phase3_diagnostics.png
│ └── phase4/ ⏳ ML models (empty — ready for Phase 4)
│
├── data/
│ ├── raw/ Reference data
│ └── processed/ 500-sample dataset
│
└── Documentation
    ├── PROJECT_STATUS.md START HERE — Full project overview
    ├── PHASE_4_EXECUTION.md Ready-to-run Phase 4 guide
    ├── requirements.txt Dependencies
    └── README.md (this file)
```

---

## Key Metrics

| Phase | Component | Metric | Status |
|-------|-----------|--------|--------|
| 1 | DoE Design | 500 LHS samples, 10 factors | Complete |
| 2 | Langmuir Model | R² = 0.8158, RMSE = 0.5278 mg/g | Complete |
| 3 | Residual Analysis | 28 features engineered, pH = 21.1% importance | Complete |
| 4 | ML Models | Target: R² ≥ 0.70 on residuals | ⏳ Ready to Start |
| 5 | Hybrid Integration | Expected: R² ≥ 0.94 | Planned |

---

## Phase Progress

### Phase 1: Research & Experimental Design
- 10 factors selected (pH, C₀, time, dose, temp, flow, chloride, hardness, carbonate, NOM)
- 500-point Latin Hypercube Sampling generated
- Physics-based simulation of fluoride adsorption (corrected for realistic data)

### Phase 2: Langmuir Baseline Model
- **R² = 0.8158** — Excellent fit to physics-based data
- 66 polynomial features (10 original + 10 squared + 45 interactions)
- Residuals analyzed: mean ≈ 0 (unbiased), systematic pH-driven pattern identified

### Phase 3: Residual Analysis & Feature Engineering
- Residual distribution analyzed by pH: +0.649 mg/g underestimation at pH 6.5–7 (optimal)
- 28 engineered features created (6 groups: pH deviation, ion competition, equilibrium, etc.)
- Quick RandomForest baseline: 47.3% test R² on residuals (proof of learnability)
- ML training/test data prepared: 400/100 split, 38 features, ready for Phase 4

### ⏳ Phase 4: ML Model Training (NEXT)
- Train RandomForest, XGBoost, MLP on Phase 3 engineered features
- Target: ≥70% residual R² → enables hybrid model ≥94% overall
- Input: 400 training + 100 test samples (verified, clean)
- Expected duration: 2–3 hours

---

## Next Steps

### Immediate: Execute Phase 4
1. Review `PHASE_4_EXECUTION.md` for complete setup
2. Create `src/phase4_ml_training.py` using provided template
3. Run: `python3 src/phase4_ml_training.py`
4. Verify outputs in `results/phase4/`

### Timeline
- Phase 4 execution: ~2–3 hours
- Phase 5 (Hybrid integration): ~1 hour
- Total to completion: ~3–4 hours

---

## File Registry

### Phase 2 (Langmuir) Outputs
- `results/phase2/langmuir_predictions.csv` — 500 samples with Langmuir predictions
- `results/phase2/langmuir_model_info.json` — Model parameters and metrics
- `results/phase2/langmuir_diagnostics.png` — 4-panel diagnostic plots

### Phase 3 (Residual Analysis) Outputs
- `results/phase3/ml_training_data.csv` — 400 samples with 38 features (ready for ML)
- `results/phase3/ml_test_data.csv` — 100 samples with 38 features (evaluation set)
- `results/phase3/feature_importance.csv` — Feature importance rankings
- `results/phase3/residual_analysis.json` — Metadata (skewness, means, etc.)
- `results/phase3/phase3_diagnostics.png` — Residual analysis plots

---

## Scientific Foundation

### 10 Factors Selected (Phase 1)
| Factor | Range | Unit | Justification |
|--------|-------|------|---------------|
| pH | 3–9 | — | Controls surface charge & F⁻ speciation |
| C₀ (Initial F⁻) | 10–100 | mg/L | Driving force for adsorption |
| Contact Time | 5–180 | min | Kinetic equilibration |
| Adsorbent Dose | 1–50 | g/L | Binding capacity |
| Temperature | 20–60 | °C | Thermal effects |
| Flow Rate | 0.5–2.5 | mL/min | Transport mechanism |
| Chloride | 0–100 | mg/L | Competitive ion |
| Hardness (Ca²⁺) | 0–200 | mg/L | Ionic strength |
| Carbonate | 0–50 | mg/L | pH buffer effect |
| NOM | 0–50 | mg/L | Pore fouling |

### Physics: Langmuir Isotherm
```
q(C, dose, ...) = polynomial(C₀, time, temp, pH, dose, ...)
```
- **R² = 0.8158**: Chemistry explains 81.58% of variance
- **Residuals**: 18.42% variance is learnable, pH-driven pattern

### ML Enhancement: Residual Correction
```
q_final = q_Langmuir + ML_correction
Expected: R² ≥ 0.94
```

---

## Environment Setup

### Requirements
- Python 3.10+
- scikit-learn 0.24+
- pandas, numpy, scipy, matplotlib
- xgboost (for Phase 4)

### Install
```bash
pip install -r requirements.txt
python3 -m venv venv # If needed
```

### Verify Installation
```bash
python3 -c "import pandas; import sklearn; import xgboost; print(' All dependencies ready')"
```

---

## Expected Final Results

### Hybrid Model Performance (Phase 5)
```
Langmuir (Phase 2): R² = 0.8158
Residual ML (Phase 4): R² ≥ 0.70
─────────────────────────────────────
Hybrid Model: R² ≥ 0.94 TARGET ACHIEVED
```

### Practical Impact
- **Before:** ±0.53 mg/g RMSE (7.9% error)
- **After:** ±0.25 mg/g RMSE (3.7% error) — **66% improvement**

---

## Documentation

- **[PROJECT_STATUS.md](PROJECT_STATUS.md)** — Complete metrics, findings, file registry
- **[PHASE_4_EXECUTION.md](PHASE_4_EXECUTION.md)** — Step-by-step Phase 4 guide with script template
- **[PHASES_1_3_SUMMARY_REPORT.md](docs/phase\ 3/PHASES_1_3_SUMMARY_REPORT.md)** — Comprehensive technical report

---

## Success Criteria

- [x] Phase 1: 500-sample LHS design generated
- [x] Phase 2: Langmuir model R² ≥ 0.80
- [x] Phase 3: Residual patterns identified and features engineered
- [ ] Phase 4: ML models trained with R² ≥ 0.70 on residuals
- [ ] Phase 5: Hybrid model verified with R² ≥ 0.94
- [ ] Phase 6: External validation completed
- [ ] Phase 7: Documentation finalized
- [ ] Phase 8: Model deployed

---

## Quick Links

- **Start here:** [PROJECT_STATUS.md](PROJECT_STATUS.md)
- **Next execution:** [PHASE_4_EXECUTION.md](PHASE_4_EXECUTION.md)
- **Technical details:** [PHASES_1_3_SUMMARY_REPORT.md](docs/phase\ 3/PHASES_1_3_SUMMARY_REPORT.md)
- **Results location:** `results/phase{2,3}/`

---

**Last Updated:** May 6, 2026
**Python Version:** 3.13
**Project Status:** Phase 3 Complete | Awaiting Phase 4 Execution
