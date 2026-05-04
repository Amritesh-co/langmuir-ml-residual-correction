# LANGMUIR'S SIX CASES: QUICK REFERENCE TABLE

## Summary of All Adsorption Classifications (1918)

| Case | Name | Key Feature | Equation | n-value | When to Use | Fluoride Relevance |
|------|------|-------------|----------|---------|-------------|-------------------|
| **I** | Single-Site Langmuir (SSL) | 1 molecule = 1 site | θ = KP/(1+KP) | n = 1 | Homogeneous surface, low coverage | ✅ PRIMARY MODEL |
| **II** | Multi-Site Langmuir (MSL) | 1 molecule = n sites | θ = (KP)^(1/n)/(1+(KP)^(1/n)) | n > 1 | Large molecules, polymers | ⚠️ If F⁻ aggregates |
| **IIa** | Dual-Site Langmuir (DSL) | 2 site types (strong+weak) | θ = θ₁ + θ₂ | - | Heterogeneous surface | ✅ LIKELY for coconut husk |
| **III** | Generalized Langmuir (GL) | Mobile molecules | Complex (partition function) | - | High T, weak binding | ❌ Not relevant |
| **IV** | Cooperative Adsorption (CA) | Neighbor interactions | θ = (KP)ⁿ/(1+(KP)ⁿ) | n ≠ 1 | Self-assembly, proteins | ⚠️ pH-induced repulsion? |
| **V** | Dissociative Adsorption (DA) | Molecule splits (A₂→2A) | θ = (KP)^(1/2)/(1+(KP)^(1/2)) | n = 1/2 | H₂, O₂ on metals | ❌ F⁻ doesn't dissociate |
| **VI** | Multilayer Adsorption (MLA) | Stacking layers | θ₁ = K₁P/(1+K₁P+K₁K₂P²+...) | - | High P, condensation | ❌ Low conc. range |

---

## Decision Tree: Which Langmuir Model to Use?

```
START: Fluoride on Coconut Husk
│
├─ Is coverage < 70%?
│  ├─ YES → Try Case I (SSL) first ✅
│  └─ NO → Consider multilayer (unlikely at mg/L range)
│
├─ Does residual plot show patterns?
│  ├─ NO → SSL is sufficient ✅
│  └─ YES → Check which pattern:
│      ├─ Bimodal → Try DSL (Case IIa) ✅
│      ├─ pH-correlated → SSL won't work, need hybrid 🔧
│      └─ Time-dependent → Kinetic model needed 🔧
│
└─ Is R² < 0.85 for SSL?
   ├─ YES → Surface is heterogeneous or pH matters
   │        → Use Hybrid (SSL + ML corrections) ✅
   └─ NO → SSL is adequate, celebrate! 🎉
```

---

## Parameter Extraction Guide

### From Case I (SSL) Fit:

```python
from scipy.optimize import curve_fit

def langmuir(Ce, qmax, KL):
    return (qmax * KL * Ce) / (1 + KL * Ce)

# Fit
params, cov = curve_fit(langmuir, Ce_data, qe_data)
qmax, KL = params

# Extract uncertainties
perr = np.sqrt(np.diag(cov))
qmax_err, KL_err = perr

# Calculate R²
from sklearn.metrics import r2_score
qe_pred = langmuir(Ce_data, qmax, KL)
r2 = r2_score(qe_data, qe_pred)

print(f"qmax = {qmax:.2f} ± {qmax_err:.2f} mg/g")
print(f"KL = {KL:.4f} ± {KL_err:.4f} L/mg")
print(f"R² = {r2:.4f}")
```

### From Case IIa (DSL) Fit:

```python
def dual_site_langmuir(Ce, qmax1, KL1, qmax2, KL2):
    site1 = (qmax1 * KL1 * Ce) / (1 + KL1 * Ce)
    site2 = (qmax2 * KL2 * Ce) / (1 + KL2 * Ce)
    return site1 + site2

# Fit with initial guesses
p0 = [qmax1_guess, KL1_guess, qmax2_guess, KL2_guess]
params, cov = curve_fit(dual_site_langmuir, Ce_data, qe_data, p0=p0)
qmax1, KL1, qmax2, KL2 = params

print(f"Strong sites: qmax1 = {qmax1:.2f} mg/g, KL1 = {KL1:.4f} L/mg")
print(f"Weak sites: qmax2 = {qmax2:.2f} mg/g, KL2 = {KL2:.4f} L/mg")
```

---

## Interpretation Checklist

After fitting Langmuir, ask these questions:

### ✅ Goodness of Fit
- [ ] R² > 0.85? (acceptable)
- [ ] R² > 0.90? (good)
- [ ] R² > 0.95? (excellent)

### ✅ Physical Reasonableness
- [ ] qmax in literature range? (6-10 mg/g for coconut)
- [ ] KL in literature range? (0.08-0.15 L/mg)
- [ ] RL between 0 and 1? (favorable)

### ✅ Residual Analysis
- [ ] Residuals normally distributed?
- [ ] No correlation with pH?
- [ ] No correlation with time?
- [ ] No correlation with temperature?

### ✅ When to Use Dual-Site (DSL)
- [ ] Single SSL fit poor (R² < 0.85)?
- [ ] Residuals show two populations?
- [ ] Expect surface heterogeneity (edges + basal)?
- [ ] DSL improves R² significantly (>0.05)?

---

## Langmuir vs. Your Hybrid Model

| Aspect | Pure Langmuir (Case I) | Hybrid (SSL + ML) |
|--------|----------------------|-------------------|
| **Physics** | ✅ Full (equilibrium) | ✅ Full (baseline) |
| **pH effects** | ❌ Not modeled | ✅ ML learns |
| **Kinetics** | ❌ Assumes equilibrium | ✅ ML learns |
| **Temperature** | ⚠️ Needs K(T) fit | ✅ ML learns |
| **Interpretability** | ✅ Excellent | ✅ Good (decomposed) |
| **Extrapolation** | ⚠️ Risky | ⚠️ Risky (but constrained) |
| **Data needed** | Low (~20 points) | Medium (~50-80 points) |
| **Complexity** | Low (2 params) | Medium (2 + 8-12 features) |
| **R² expected** | 0.85-0.90 | 0.90-0.95 |

---

## Historical Timeline

```
1907  Freundlich isotherm (empirical)
↓
1916  Langmuir begins adsorption studies
↓
1918  ★ LANGMUIR PUBLISHES 42-PAGE PAPER ★
      - 6 cases defined
      - Kinetic derivation
      - Experimental validation
↓
1932  Langmuir wins Nobel Prize
↓
1938  BET theory (multilayer extension)
↓
1940s Temkin isotherm (heat of adsorption)
↓
1960s Dubinin-Radushkevich (micropores)
↓
1990s Sips/Langmuir-Freundlich (hybrid)
↓
2000s Machine learning + physics hybrids
↓
2024  YOUR PROJECT: SSL + ML residuals ✨
```

---

## Common Mistakes to Avoid

### ❌ Mistake 1: Linearizing the Equation
**Wrong:**
```python
# DON'T DO THIS!
y = Ce / qe
x = Ce
slope, intercept = np.polyfit(x, y, 1)
```

**Right:**
```python
# DO THIS!
params, cov = curve_fit(langmuir, Ce, qe)
```

**Why?** Linear transforms distort error structure and give wrong parameter uncertainties.

### ❌ Mistake 2: Mixing pH Values
**Wrong:**
```python
# Fit all data together regardless of pH
params = curve_fit(langmuir, Ce_all, qe_all)
```

**Right:**
```python
# Fit separately per pH or include pH in model
for pH_val in [3, 5, 7, 9]:
    data_at_pH = df[df['pH'] == pH_val]
    params = curve_fit(langmuir, data_at_pH['Ce'], data_at_pH['qe'])
    print(f"pH {pH_val}: qmax={params[0]:.2f}, KL={params[1]:.4f}")
```

### ❌ Mistake 3: Over-Interpreting R²
**Wrong thinking:**
"R² = 0.92, so Langmuir is perfect!"

**Right thinking:**
"R² = 0.92 means 92% of variance explained. Check residuals for systematic patterns that ML could learn."

### ❌ Mistake 4: Ignoring Uncertainty
**Wrong:**
```python
print(f"qmax = {qmax}")  # No error bars!
```

**Right:**
```python
perr = np.sqrt(np.diag(cov))
print(f"qmax = {qmax:.2f} ± {perr[0]:.2f} mg/g")
```

---

**End of Quick Reference Table**

Use this table to decide which Langmuir variant to use and how to interpret results!
