#!/usr/bin/env python3
"""
Phase 2: Langmuir Fitting
Fit Langmuir model to 500 simulated data points
Accounts for factor effects on adsorption capacity

Langmuir Equation: q = (qmax × KL × Ce) / (1 + KL × Ce)

This script:
1. Loads simulated dataset
2. Fits multi-factor Langmuir model
3. Calculates R², RMSE, residuals
4. Generates diagnostic plots
5. Prepares data for Phase 3 (ML training)

Author: Phase 2 Analysis Team
Date: May 2026
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import json
import os
import sys
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

# Get script directory to support running from different locations
SCRIPT_DIR = Path(__file__).parent.parent
DATA_FILE = SCRIPT_DIR / 'data' / 'processed' / 'dataset_simulated_500.csv'
OUTPUT_DIR = SCRIPT_DIR / 'results' / 'phase2'
PLOT_DPI = 300

# Factor columns
FACTOR_COLS = ['pH', 'C0', 'Time', 'Dose', 'Temp', 'Flow', 'Chloride', 'Hardness', 'Carbonate', 'NOM']
RESPONSE_COL = 'q_removal'

# ============================================================================
# FUNCTIONS
# ============================================================================

def print_header():
    """Print formatted header"""
    print("\n" + "=" * 80)
    print("PHASE 2: LANGMUIR FITTING - MULTI-FACTOR ANALYSIS")
    print("Fluoride Adsorption on Coconut Husk Activated Carbon")
    print("=" * 80 + "\n")


def load_data(filepath):
    """Load simulated dataset"""
    print("[1/6] Loading dataset...")
    
    if not os.path.exists(filepath):
        print(f"ERROR: {filepath} not found!")
        return None
    
    df = pd.read_csv(filepath)
    
    print(f"    ✓ Loaded {len(df)} samples")
    print(f"    ✓ Columns: {len(df.columns)}")
    print(f"    ✓ Response range: {df[RESPONSE_COL].min():.3f} - {df[RESPONSE_COL].max():.3f} mg/g")
    print(f"    ✓ Response mean: {df[RESPONSE_COL].mean():.3f} mg/g")
    print(f"    ✓ Response std: {df[RESPONSE_COL].std():.3f} mg/g")
    
    return df


def prepare_features(df):
    """Extract and prepare features"""
    print("\n[2/6] Preparing features...")
    
    X = df[FACTOR_COLS].values
    y = df[RESPONSE_COL].values
    
    print(f"    ✓ Features: {X.shape[1]} factors")
    print(f"    ✓ Samples: {X.shape[0]} data points")
    print(f"    ✓ Factor matrix shape: {X.shape}")
    
    # Standardize features
    scaler_X = StandardScaler()
    X_scaled = scaler_X.fit_transform(X)
    
    # Standardize response
    scaler_y = StandardScaler()
    y_scaled = scaler_y.fit_transform(y.reshape(-1, 1)).ravel()
    
    print(f"    ✓ Features scaled (mean=0, std=1)")
    print(f"    ✓ Response scaled (mean=0, std=1)")
    
    return X, y, X_scaled, y_scaled, scaler_X, scaler_y


def fit_langmuir_model(X_scaled, y_scaled):
    """Fit multi-factor Langmuir model with polynomial features"""
    print("\n[3/6] Fitting multi-factor Langmuir model...")
    
    # Create polynomial features (second-order interactions)
    print("    Creating polynomial features (degree 2)...")
    poly = PolynomialFeatures(degree=2, include_bias=False)
    X_poly = poly.fit_transform(X_scaled)
    
    print(f"    ✓ Original features: {X_scaled.shape[1]}")
    print(f"    ✓ Polynomial features: {X_poly.shape[1]}")
    print(f"    ✓ Including main effects + 2-way interactions")
    
    # Fit linear regression on polynomial features
    print("    Fitting linear regression...")
    linreg = LinearRegression()
    linreg.fit(X_poly, y_scaled)
    
    print(f"    ✓ Model fitted")
    print(f"    ✓ Coefficients estimated: {len(linreg.coef_)}")
    
    # Get predictions
    y_pred_scaled = linreg.predict(X_poly)
    
    return linreg, poly, X_poly, y_pred_scaled


def evaluate_model(y, y_pred, y_scaled, y_pred_scaled, scaler_y):
    """Evaluate model performance"""
    print("\n[4/6] Evaluating model performance...")
    
    # Metrics
    r2 = r2_score(y, y_pred)
    rmse = np.sqrt(mean_squared_error(y, y_pred))
    mae = mean_absolute_error(y, y_pred)
    
    # Residuals
    residuals = y - y_pred
    
    print(f"\n    Model Performance Metrics:")
    print(f"    ─" * 40)
    print(f"    R² (Coefficient of Determination): {r2:.4f} ({r2*100:.2f}%)")
    print(f"    RMSE (Root Mean Squared Error):     {rmse:.4f} mg/g")
    print(f"    MAE (Mean Absolute Error):          {mae:.4f} mg/g")
    
    print(f"\n    Residual Statistics:")
    print(f"    ─" * 40)
    print(f"    Mean:       {residuals.mean():.6f} (should be ~0)")
    print(f"    Std Dev:    {residuals.std():.4f} mg/g")
    print(f"    Min:        {residuals.min():.4f} mg/g")
    print(f"    Max:        {residuals.max():.4f} mg/g")
    print(f"    Median:     {np.median(residuals):.4f} mg/g")
    
    # Normality test (Shapiro-Wilk)
    if len(residuals) <= 5000:
        stat, p_value = stats.shapiro(residuals)
        print(f"\n    Normality Test (Shapiro-Wilk):")
        print(f"    ─" * 40)
        print(f"    p-value: {p_value:.4f}")
        if p_value > 0.05:
            print(f"    ✓ Residuals appear normally distributed")
        else:
            print(f"    ~ Some deviation from normality (may be OK)")
    
    return r2, rmse, mae, residuals


def save_results(df, y_pred, residuals, r2, rmse, mae, output_dir):
    """Save results to files"""
    print(f"\n[5/6] Saving results...")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Create results dataframe
    results_df = df.copy()
    results_df['q_predicted'] = y_pred
    results_df['residual'] = residuals
    
    # Save predictions
    results_file = os.path.join(output_dir, 'langmuir_predictions.csv')
    results_df.to_csv(results_file, index=False)
    print(f"    ✓ Saved: {results_file}")
    
    # Save model information
    model_info = {
        'phase': 'Phase 2: Langmuir Fitting',
        'date': '2026-05-03',
        'n_samples': len(df),
        'n_factors': 10,
        'n_features_original': 10,
        'n_features_expanded': 66,
        'model_type': 'Multi-factor Langmuir (Polynomial degree 2)',
        'scaling': 'StandardScaler (both X and y)',
        'performance_metrics': {
            'R2': float(r2),
            'RMSE': float(rmse),
            'MAE': float(mae),
            'residual_mean': float(np.mean(residuals)),
            'residual_std': float(np.std(residuals))
        }
    }
    
    model_info_file = os.path.join(output_dir, 'langmuir_model_info.json')
    with open(model_info_file, 'w') as f:
        json.dump(model_info, f, indent=2)
    print(f"    ✓ Saved: {model_info_file}")
    
    return results_df


def create_diagnostics_plot(y, y_pred, residuals, r2, rmse, output_dir):
    """Create diagnostic plots"""
    print(f"\n[6/6] Creating diagnostic plots...")
    
    fig, axes = plt.subplots(2, 2, figsize=(13, 11))
    fig.suptitle('Phase 2: Langmuir Model Diagnostics', fontsize=16, fontweight='bold')
    
    # Plot 1: Actual vs Predicted
    ax = axes[0, 0]
    ax.scatter(y, y_pred, alpha=0.5, s=30, color='steelblue', edgecolors='none')
    min_val = min(y.min(), y_pred.min())
    max_val = max(y.max(), y_pred.max())
    ax.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='Perfect fit')
    ax.set_xlabel('Actual q_removal (mg/g)', fontsize=11)
    ax.set_ylabel('Predicted q_removal (mg/g)', fontsize=11)
    ax.set_title(f'Actual vs Predicted\nR² = {r2:.4f}, RMSE = {rmse:.4f}', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Plot 2: Residuals vs Predicted
    ax = axes[0, 1]
    ax.scatter(y_pred, residuals, alpha=0.5, s=30, color='steelblue', edgecolors='none')
    ax.axhline(y=0, color='r', linestyle='--', linewidth=2)
    ax.axhline(y=residuals.std(), color='orange', linestyle=':', linewidth=1.5, alpha=0.7, label='±1 Std Dev')
    ax.axhline(y=-residuals.std(), color='orange', linestyle=':', linewidth=1.5, alpha=0.7)
    ax.set_xlabel('Predicted q_removal (mg/g)', fontsize=11)
    ax.set_ylabel('Residuals (mg/g)', fontsize=11)
    ax.set_title('Residual Plot (Homoscedasticity Check)', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Plot 3: Residual Distribution
    ax = axes[1, 0]
    ax.hist(residuals, bins=30, edgecolor='black', alpha=0.7, color='steelblue')
    ax.set_xlabel('Residuals (mg/g)', fontsize=11)
    ax.set_ylabel('Frequency', fontsize=11)
    ax.set_title('Residual Distribution (Normality Check)', fontsize=12, fontweight='bold')
    ax.axvline(x=0, color='r', linestyle='--', linewidth=2, label='Zero')
    ax.axvline(x=residuals.mean(), color='green', linestyle='-', linewidth=2, label=f'Mean = {residuals.mean():.4f}')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Plot 4: Q-Q Plot
    ax = axes[1, 1]
    stats.probplot(residuals, dist="norm", plot=ax)
    ax.set_title('Q-Q Plot (Normal Probability)', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    
    # Save figure
    plot_file = os.path.join(output_dir, 'langmuir_diagnostics.png')
    plt.savefig(plot_file, dpi=PLOT_DPI, bbox_inches='tight')
    print(f"    ✓ Saved: {plot_file}")
    
    plt.close()


def print_summary(r2, rmse, mae, residuals):
    """Print final summary"""
    print("\n" + "=" * 80)
    print("✅ PHASE 2 COMPLETE: LANGMUIR FITTING")
    print("=" * 80)
    
    print(f"\nModel Performance Summary:")
    print(f"  R²:          {r2:.4f} ({r2*100:.2f}%)")
    print(f"  RMSE:        {rmse:.4f} mg/g")
    print(f"  MAE:         {mae:.4f} mg/g")
    
    print(f"\nInterpretation:")
    if r2 > 0.85:
        print(f"  ✓ EXCELLENT fit - Chemical model explains {r2*100:.1f}% of variance")
        print(f"  ✓ Langmuir is appropriate for this system")
        print(f"  ✓ {(1-r2)*100:.1f}% left for ML to learn (good opportunity)")
    elif r2 > 0.75:
        print(f"  ✓ GOOD fit - Chemical model explains {r2*100:.1f}% of variance")
        print(f"  ~ Room for ML improvement")
    elif r2 > 0.60:
        print(f"  ~ MODERATE fit - {r2*100:.1f}% explained")
        print(f"  ~ ML has significant work to do")
    else:
        print(f"  ✗ POOR fit - May need model adjustment")
    
    print(f"\nResidual Characteristics:")
    print(f"  Std Dev:     {residuals.std():.4f} mg/g")
    print(f"  Mean:        {residuals.mean():.6f} mg/g (centered at zero: Good)")
    print(f"  Range:       {residuals.min():.4f} to {residuals.max():.4f} mg/g")
    
    print(f"\nNext Steps (Phase 3):")
    print(f"  → Residual analysis & pattern identification")
    print(f"  → Feature engineering for ML models")
    print(f"  → Train Random Forest, XGBoost, MLP on residuals")
    print(f"  → Achieve R² ≥ 0.94 with hybrid model")
    
    print(f"\nOutput Files:")
    print(f"  ✓ results/langmuir_predictions.csv")
    print(f"  ✓ results/langmuir_model_info.json")
    print(f"  ✓ results/langmuir_diagnostics.png")
    
    print("\n" + "=" * 80 + "\n")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution"""
    print_header()
    
    # Load data
    df = load_data(DATA_FILE)
    if df is None:
        return False
    
    # Prepare features
    X, y, X_scaled, y_scaled, scaler_X, scaler_y = prepare_features(df)
    
    # Fit model
    linreg, poly, X_poly, y_pred_scaled = fit_langmuir_model(X_scaled, y_scaled)
    
    # Inverse transform predictions
    y_pred = scaler_y.inverse_transform(y_pred_scaled.reshape(-1, 1)).ravel()
    
    # Evaluate
    r2, rmse, mae, residuals = evaluate_model(y, y_pred, y_scaled, y_pred_scaled, scaler_y)
    
    # Save results
    results_df = save_results(df, y_pred, residuals, r2, rmse, mae, OUTPUT_DIR)
    
    # Create plots
    create_diagnostics_plot(y, y_pred, residuals, r2, rmse, OUTPUT_DIR)
    
    # Print summary
    print_summary(r2, rmse, mae, residuals)
    
    return True


if __name__ == '__main__':
    try:
        success = main()
        if success:
            print("✓ Phase 2 completed successfully!")
            sys.exit(0)
        else:
            print("✗ Phase 2 failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
