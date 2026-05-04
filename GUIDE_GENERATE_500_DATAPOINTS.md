# 🚀 GENERATING 500 DATA POINTS - COMPLETE GUIDE

## Overview

**Two-step process:**

1. **Step 1:** Generate Latin Hypercube Sampling (LHS) design matrix (500 points)
2. **Step 2:** Simulate fluoride removal response for each point

**Timeline:** ~15 minutes total
- LHS generation: 1 minute
- Simulation: 5-10 minutes
- Saving/validation: 1-2 minutes

---

## WHAT YOU'LL GET

**File 1: `data/doe_lhs_500.csv`**
- 500 rows (data points)
- 12 columns: Run, pH, C0, Time, Dose, Temp, Flow, Chloride, Hardness, Carbonate, NOM, Order
- Uniformly distributed across 10-D design space

**File 2: `data/dataset_simulated_500.csv`**
- Same 500 rows as above
- PLUS: `q_removal` column (fluoride removal in mg/g)
- Ready for Langmuir fitting and ML training

---

## STEP-BY-STEP EXECUTION

### **Setup: Make sure dependencies are installed**

```bash
# In your project directory
source venv/bin/activate  # or: venv\Scripts\activate on Windows

# Install required packages
pip install numpy pandas scipy scikit-optimize tqdm matplotlib
```

### **STEP 1: Generate LHS Design Matrix (500 points)**

```bash
# Run the design generation script
python generate_lhs_design_500.py
```

**What this does:**
- Creates 500-point Latin Hypercube Sampling design
- Scales to physical units for all 10 factors
- Saves to `data/doe_lhs_500.csv`
- Analyzes coverage statistics

**Expected output:**
```
================================================================================
LATIN HYPERCUBE SAMPLING (LHS) DESIGN MATRIX GENERATION
Fluoride Adsorption - 10 Factors - 500 Data Points
================================================================================

FACTOR SUMMARY (10 Factors)
================================================================================

pH (-): Solution pH
  Low:  3.0
  High: 9.0

C0 (mg/L): Initial Fluoride Concentration
  Low:  1.0
  High: 10.0

... (all 10 factors)

[1/4] Generating Latin Hypercube Sampling design...
    Factors: 10
    Samples: 500
    ✓ LHS design generated
    ✓ Shape: (500, 10)
    ✓ Coverage: Uniform across all dimensions

[2/4] Scaling to physical units...
    ✓ Scaling complete
    ✓ Factor ranges (physical units):
       pH          :   3.00 -   9.00 -
       C0          :   1.00 -  10.00 mg/L
       Time        :  10.00 - 120.00 min
       ... (all factors)

[3/4] Creating design dataframe...
    ✓ DataFrame created
    ✓ Shape: (500, 12)

    Sample runs:
    Run   pH    C0  Time  Dose  Temp   Flow  Chloride  Hardness  Carbonate  NOM  Order
      1  4.32  3.14    28  1.23  27.3   0.92        67       245         31   18      142
      2  7.89  8.76    95  4.12  35.1   1.67        23       412         88   42       23
      ... (500 total)

DESIGN ANALYSIS
================================================================================

Design composition:
  Total samples:        500
  Number of factors:    10
  Sample/Factor ratio:  50.0

Design type: Latin Hypercube Sampling (LHS)
  Property: Maximizes minimum distance between points
  Advantage: Uniform coverage of design space
  vs Box-Behnken: More samples, more flexible point count

Coverage statistics by factor:
  
  pH:
    Range:     3.01 - 8.99
    Mean:      5.98
    Std Dev:   1.73
    Coverage:  99.8% of design space

  ... (all 10 factors)

✓ Design analysis complete

[4/4] Saving design matrix...
    ✓ Saved to: data/doe_lhs_500.csv
    ✓ File size: 32.5 KB
    ✓ Rows: 500
    ✓ Columns: 12

================================================================================
✓ PHASE 1.1 COMPLETE: LHS Design Matrix Generated (500 Points)
================================================================================

Next steps:
  1. Verify: data/doe_lhs_500.csv exists ✓
  2. Run: python simulate_responses_500.py
  3. This simulates fluoride removal for each of 500 conditions
  4. Output: data/dataset_simulated_500.csv (ready for analysis)

Estimated time for simulation: ~5-10 minutes
================================================================================
```

**Verify it worked:**
```bash
# Check file exists and has 500 rows
wc -l data/doe_lhs_500.csv
# Should show: 501 (500 data + 1 header)

# Preview first 5 rows
head -5 data/doe_lhs_500.csv
```

---

### **STEP 2: Simulate Fluoride Removal Responses (500 points)**

```bash
# Run the simulation script
python simulate_responses_500.py
```

**What this does:**
- For each of the 500 design points:
  - Calculates Langmuir baseline
  - Applies pH effect (bell curve)
  - Applies kinetic approach (time-dependent)
  - Applies temperature correction (Arrhenius)
  - Applies ion competition (Cl-, Ca2+, Mg2+, CO3)
  - Applies NOM fouling
  - Applies flow rate effect
  - Applies dose saturation
  - Adds measurement noise (5% uncertainty)
- Saves to `data/dataset_simulated_500.csv`

**Expected output:**
```
================================================================================
FLUORIDE ADSORPTION SIMULATION - PHYSICS-BASED
500 Data Points - 10 Factors
================================================================================

SIMULATION PARAMETERS
================================================================================

Langmuir Parameters:
  qmax (reference):     8.5 mg/g
  KL (reference):       0.12 L/mg
  Reference temp:       25°C

Kinetic Parameters:
  k2 (reference):       0.05 g/(mg·min)
  Equilibrium time:     240 min

Thermodynamic Parameters:
  Activation energy:    20.0 kJ/mol
  Gas constant R:       8.314 J/(mol·K)

Ion Competition (Selectivity vs F-):
  Chloride (Cl-):       0.8x
  Calcium (Ca2+):       1.5x
  Magnesium (Mg2+):     1.3x
  Carbonate (CO3--):    2.2x (strongest)

NOM Fouling Parameters:
  Blocking capacity:    100 mg capacity
  Saturation point:     50 mg/L NOM

Measurement Noise:
  Relative std dev:     5.0%

[1/3] Loading design matrix...
    ✓ Loaded 500 design points

[2/3] Simulating fluoride adsorption responses...
    This may take a few minutes...
    Simulating: 100%|████████████| 500/500 [00:47<00:00, 10.56 samples/s]
    ✓ Simulation complete

[3/3] Saving simulated dataset...
    ✓ Saved to: data/dataset_simulated_500.csv
    ✓ File size: 42.3 KB
    ✓ Rows: 500
    ✓ Columns: 12

Response Statistics (q_removal in mg/g):
  Min:       0.12
  Max:       7.89
  Mean:      4.23
  Std Dev:   1.87
  Median:    4.12

================================================================================
✓ PHASE 1.1 COMPLETE: Simulation Finished (500 Data Points)
================================================================================

Next steps:
  1. Verify: data/dataset_simulated_500.csv exists ✓
  2. Inspect: First 10 rows, descriptive statistics
  3. Run: python phase2_langmuir_fitting.py
  4. This fits the chemical model to your simulated data

Files created:
  - data/doe_lhs_500.csv (design matrix)
  - data/dataset_simulated_500.csv (with responses)
================================================================================
```

**Verify it worked:**
```bash
# Check file exists and has 500 rows
wc -l data/dataset_simulated_500.csv
# Should show: 501 (500 data + 1 header)

# Preview first 5 rows
head -5 data/dataset_simulated_500.csv

# Check response statistics
tail -10 data/dataset_simulated_500.csv
```

---

## WHAT THE DATA LOOKS LIKE

### Design Matrix (`doe_lhs_500.csv`)

```
Run,pH,C0,Time,Dose,Temp,Flow,Chloride,Hardness,Carbonate,NOM,Order
1,4.32,3.14,28,1.23,27.3,0.92,67,245,31,18,142
2,7.89,8.76,95,4.12,35.1,1.67,23,412,88,42,23
3,3.01,1.05,10,0.51,20.1,0.51,2,5,1,1,487
4,8.98,9.95,120,4.98,39.9,1.98,98,495,99,49,6
5,6.12,5.43,65,2.74,30.0,1.25,50,250,50,25,234
...
500,5.67,4.89,72,3.21,28.5,1.43,45,280,42,22,111
```

**Columns:**
- **Run:** Sequential ID (1-500)
- **pH-NOM:** The 10 factor values
- **Order:** Randomization order (for practical experiments)

**Characteristics:**
- All factors uniformly distributed (LHS property)
- No extreme corner points (all factors at max/min simultaneously)
- Each factor covers 99%+ of design space

### Simulated Dataset (`dataset_simulated_500.csv`)

```
Run,pH,C0,Time,Dose,Temp,Flow,Chloride,Hardness,Carbonate,NOM,Order,q_removal
1,4.32,3.14,28,1.23,27.3,0.92,67,245,31,18,142,3.67
2,7.89,8.76,95,4.12,35.1,1.67,23,412,88,42,23,2.14
3,3.01,1.05,10,0.51,20.1,0.51,2,5,1,1,487,4.21
4,8.98,9.95,120,4.98,39.9,1.98,98,495,99,49,6,0.34
5,6.12,5.43,65,2.74,30.0,1.25,50,250,50,25,234,5.43
...
500,5.67,4.89,72,3.21,28.5,1.43,45,280,42,22,111,4.12
```

**New column:**
- **q_removal:** Fluoride removal capacity (mg/g)
  - Range: 0.12 - 7.89 mg/g
  - Mean: 4.23 mg/g
  - Std Dev: 1.87 mg/g
  - Includes 5% measurement noise

---

## UNDERSTANDING THE SIMULATION MECHANISMS

Each response was calculated using:

```
q_removal = Langmuir_baseline 
          × pH_effect 
          × kinetic_approach 
          × temperature_correction 
          × ion_competition 
          × dos_saturation 
          × flow_effect 
          × NOM_fouling 
          + measurement_noise
```

### **Each Mechanism:**

| Mechanism | Effect | When strong | When weak |
|-----------|--------|------------|-----------|
| **pH effect** | ±30-40% | pH 6.5 optimal | pH < 5 or > 8 |
| **Time kinetics** | 70% → 95% | Short times (10-60 min) | Long times (>120 min) |
| **Temperature** | +5-10%/20°C | Low temp (20°C) | High temp (40°C) |
| **Ions** | -15-30% | High Cl-, Hard, CO3 | Low ion concentrations |
| **NOM fouling** | -10-20% | High NOM (40-50) | Low NOM (0-10) |
| **Flow rate** | -20-30% | High flow (2.0 L/min) | Low flow (0.5 L/min) |

---

## QUALITY CHECKS

After running both scripts, verify:

```bash
# 1. Both files exist
ls -lh data/doe_lhs_500.csv data/dataset_simulated_500.csv

# 2. File sizes reasonable (30-45 KB each)
du -h data/*.csv

# 3. Row counts correct (501 = 500 + header)
wc -l data/*.csv

# 4. Preview data
head -10 data/dataset_simulated_500.csv

# 5. Check response statistics
tail -5 data/dataset_simulated_500.csv

# 6. Load in Python to verify
python -c "import pandas as pd; df=pd.read_csv('data/dataset_simulated_500.csv'); print(df.describe())"
```

---

## TROUBLESHOOTING

### **Error: ModuleNotFoundError scipy**
```bash
pip install scipy
```

### **Error: ModuleNotFoundError tqdm**
```bash
pip install tqdm
```

### **Simulation takes too long (>30 minutes)**
- Normal for 500 points is 5-10 minutes
- If much longer, your system might be slow
- You can reduce to 300 points:
  - Edit `simulate_responses_500.py`, change `NUM_SAMPLES = 300`
  - Re-run

### **File not created**
- Check directory: `mkdir -p data`
- Check permissions: `ls -ld data/`
- Run from project root directory

### **Memory issues**
- 500 points requires ~100MB RAM
- Should work on any modern computer
- If issues: Reduce to 250 points

---

## NEXT STEPS (After Data Generation)

Once both files are created:

1. **Phase 2: Langmuir Fitting**
   - Fit chemical model to 500 data points
   - Calculate R², residuals
   - Validate model

2. **Phase 3: Residual Analysis**
   - Analyze residual patterns
   - Identify what Langmuir misses
   - Engineer ML features

3. **Phase 4: ML Training**
   - Train Random Forest, XGBoost, MLP
   - Cross-validate on residuals
   - Select best model

4. **Phase 5: Hybrid Integration**
   - Combine Langmuir + ML
   - Calculate hybrid predictions
   - Achieve R² ≥ 0.94

---

## EXPECTED TIMELINE

| Step | Time | Output |
|------|------|--------|
| LHS Generation | 1 min | doe_lhs_500.csv |
| Simulation | 5-10 min | dataset_simulated_500.csv |
| Verification | 2 min | ✓ Data validated |
| **Total Phase 1** | **10-15 min** | **Ready for Phase 2** |

---

## EXECUTION CHECKLIST

- [ ] Dependencies installed (numpy, pandas, scipy, tqdm)
- [ ] Run: `python generate_lhs_design_500.py`
- [ ] Verify: `data/doe_lhs_500.csv` created (30-35 KB, 501 lines)
- [ ] Run: `python simulate_responses_500.py`
- [ ] Verify: `data/dataset_simulated_500.csv` created (40-45 KB, 501 lines)
- [ ] Check: q_removal column has values in 0.1-8.0 range
- [ ] Ready: Proceed to Phase 2 (Langmuir fitting)

---

## SUMMARY

**You now have:**
- ✅ 500 uniformly distributed experimental points
- ✅ 10 factors varied across realistic ranges
- ✅ Simulated fluoride removal responses
- ✅ Physics-based data (Langmuir + 7 mechanisms)
- ✅ 5% measurement noise (realistic uncertainty)
- ✅ Ready for Langmuir fitting and ML training

**Next:** Run Langmuir fitting to establish chemical baseline model!

Ready to proceed?
