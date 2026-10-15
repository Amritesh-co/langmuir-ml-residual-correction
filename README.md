# Hybrid Physics-ML Modelling of Fluoride Adsorption

Predicting fluoride adsorption on coconut-husk activated carbon by combining a **Langmuir isotherm** (physics baseline) with a **machine-learning residual model** that learns what the isotherm misses.

## Results

| Model | R² | RMSE |
| --- | --- | --- |
| Langmuir baseline | 0.816 | 0.528 |
| **Hybrid (Langmuir + ML residual)** | **0.942** | **0.297** |

The hybrid model cuts RMSE by **43.7%** and meets the project's R² ≥ 0.94 target. Scores are 5-fold cross-validated, out-of-fold, on 500 samples.

## Approach

1. **Design of experiments** — Latin Hypercube Sampling over 12 process variables (500 samples).
2. **Physics baseline** — fit Langmuir isotherm parameters to predict adsorption capacity.
3. **Residual learning** — train a stacking ensemble (XGBoost + Random Forest + Gradient Boosting → RidgeCV) on 24 engineered features to predict the Langmuir residual.
4. **Hybrid prediction** — final output = Langmuir prediction + predicted residual.

## Repository layout

```
fluoride-adsorption-hybrid/
  4para/     # 4-parameter real-data experiments and dataset generation
  24para/    # 24-feature hybrid model, predictions, saved model, metrics
docs/        # phase-wise reports (data analysis, factor analysis, final submission)
```

## Tech stack

Python · NumPy · pandas · scikit-learn · XGBoost · Matplotlib

## Context

Interdisciplinary Project (IDP) at RV College of Engineering. The accompanying LaTeX report lives in [Amritesh-co/IDP](https://github.com/Amritesh-co/IDP).
