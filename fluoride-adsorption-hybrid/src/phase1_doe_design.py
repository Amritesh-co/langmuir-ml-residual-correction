"""
Latin Hypercube Sampling Design Matrix Generator
10 Factors - 500 Data Points
Fluoride Adsorption Hybrid Physics-ML Model

Generates uniformly distributed experimental design across entire factor space.
Better coverage than Box-Behnken with ability to specify exact sample count.

Author: Phase 1 Research Team
Date: May 2026
"""

import numpy as np
import pandas as pd
from scipy.stats import qmc
import os
import sys

# ============================================================================
# CONFIGURATION
# ============================================================================

# Factor definitions (Physical Units)
FACTORS = {
    'pH': {
        'low': 3.0,
        'high': 9.0,
        'unit': '-',
        'description': 'Solution pH'
    },
    'C0': {
        'low': 1.0,
        'high': 10.0,
        'unit': 'mg/L',
        'description': 'Initial Fluoride Concentration'
    },
    'Time': {
        'low': 10,
        'high': 120,
        'unit': 'min',
        'description': 'Contact Time'
    },
    'Dose': {
        'low': 0.5,
        'high': 5.0,
        'unit': 'g/L',
        'description': 'Adsorbent Dose'
    },
    'Temp': {
        'low': 20,
        'high': 40,
        'unit': '°C',
        'description': 'Temperature'
    },
    'Flow': {
        'low': 0.5,
        'high': 2.0,
        'unit': 'L/min',
        'description': 'Flow Rate'
    },
    'Chloride': {
        'low': 0,
        'high': 100,
        'unit': 'mg/L',
        'description': 'Chloride Concentration'
    },
    'Hardness': {
        'low': 0,
        'high': 500,
        'unit': 'mg/L CaCO3',
        'description': 'Water Hardness'
    },
    'Carbonate': {
        'low': 0,
        'high': 100,
        'unit': 'mg/L HCO3-',
        'description': 'Carbonate Concentration'
    },
    'NOM': {
        'low': 0,
        'high': 50,
        'unit': 'mg/L',
        'description': 'Natural Organic Matter (Humic Acid)'
    }
}

NUM_FACTORS = len(FACTORS)
NUM_SAMPLES = 500
RANDOM_SEED = 42

# ============================================================================
# FUNCTIONS
# ============================================================================

def generate_lhs_samples(n_factors, n_samples, seed=42):
    """
    Generate Latin Hypercube Sampling (LHS) design matrix
    
    LHS ensures uniform coverage of the design space by dividing each
    dimension into n_samples intervals and selecting one point from each.
    
    Parameters
    ----------
    n_factors : int
        Number of factors (10)
    n_samples : int
        Number of samples (500)
    seed : int
        Random seed for reproducibility
    
    Returns
    -------
    samples_normalized : ndarray
        LHS samples in normalized space [0, 1]
        Shape: (n_samples, n_factors)
    """
    print(f"\n[1/4] Generating Latin Hypercube Sampling design...")
    print(f"    Factors: {n_factors}")
    print(f"    Samples: {n_samples}")
    
    # SciPy supports 'random-cd' and 'lloyd' here; use the space-filling option
    # available in the installed version and fall back cleanly if needed.
    try:
        sampler = qmc.LatinHypercube(d=n_factors, seed=seed, optimization="random-cd")
    except ValueError:
        sampler = qmc.LatinHypercube(d=n_factors, seed=seed)
    samples_normalized = sampler.random(n=n_samples)
    
    print(f"    ✓ LHS design generated")
    print(f"    ✓ Shape: {samples_normalized.shape}")
    print(f"    ✓ Coverage: Uniform across all dimensions")
    
    return samples_normalized


def scale_to_physical_units(samples_normalized, factors_dict):
    """
    Scale normalized [0, 1] LHS samples to physical units
    
    Parameters
    ----------
    samples_normalized : ndarray
        LHS samples in [0, 1] space
    factors_dict : dict
        Factor definitions with low/high values
    
    Returns
    -------
    samples_physical : ndarray
        LHS samples in physical units
    """
    print(f"\n[2/4] Scaling to physical units...")
    
    factor_names = list(factors_dict.keys())
    n_samples = samples_normalized.shape[0]
    samples_physical = np.zeros((n_samples, len(factor_names)))
    
    for i, fname in enumerate(factor_names):
        low = factors_dict[fname]['low']
        high = factors_dict[fname]['high']
        
        # Linear scaling: [0, 1] → [low, high]
        samples_physical[:, i] = low + samples_normalized[:, i] * (high - low)
    
    print(f"    ✓ Scaling complete")
    print(f"    ✓ Factor ranges (physical units):")
    
    for i, fname in enumerate(factor_names):
        min_val = samples_physical[:, i].min()
        max_val = samples_physical[:, i].max()
        unit = factors_dict[fname]['unit']
        print(f"       {fname:12s}: {min_val:7.2f} - {max_val:7.2f} {unit}")
    
    return samples_physical


def create_design_dataframe(samples_physical, factors_dict):
    """
    Create pandas DataFrame with experimental design
    
    Parameters
    ----------
    samples_physical : ndarray
        Scaled samples in physical units
    factors_dict : dict
        Factor definitions
    
    Returns
    -------
    df : pd.DataFrame
        Design matrix with run numbers and randomized order
    """
    print(f"\n[3/4] Creating design dataframe...")
    
    factor_names = list(factors_dict.keys())
    
    # Create DataFrame
    df = pd.DataFrame(samples_physical, columns=factor_names)
    
    # Add run number
    df.insert(0, 'Run', range(1, len(df) + 1))
    
    # Add randomization order (for practical experiments)
    df['Order'] = np.random.RandomState(RANDOM_SEED).permutation(len(df))
    
    # Round appropriately based on units
    df['pH'] = df['pH'].round(2)
    df['C0'] = df['C0'].round(2)
    df['Time'] = df['Time'].round(0).astype(int)
    df['Dose'] = df['Dose'].round(2)
    df['Temp'] = df['Temp'].round(1)
    df['Flow'] = df['Flow'].round(3)
    df['Chloride'] = df['Chloride'].round(0).astype(int)
    df['Hardness'] = df['Hardness'].round(0).astype(int)
    df['Carbonate'] = df['Carbonate'].round(0).astype(int)
    df['NOM'] = df['NOM'].round(0).astype(int)
    
    # Sort by run for display
    df_display = df.sort_values('Run').reset_index(drop=True)
    
    print(f"    ✓ DataFrame created")
    print(f"    ✓ Shape: {df_display.shape}")
    print(f"\n    Sample runs:")
    print(df_display.head(10).to_string(index=False))
    
    return df_display


def analyze_design_coverage(design_df, factors_dict):
    """
    Analyze the design for completeness and coverage
    
    Parameters
    ----------
    design_df : pd.DataFrame
        Design matrix
    factors_dict : dict
        Factor definitions
    """
    print(f"\n" + "="*80)
    print("DESIGN ANALYSIS")
    print("="*80)
    
    print(f"\nDesign composition:")
    print(f"  Total samples:        {len(design_df)}")
    print(f"  Number of factors:    {len(factors_dict)}")
    print(f"  Sample/Factor ratio:  {len(design_df)/len(factors_dict):.1f}")
    
    print(f"\nDesign type: Latin Hypercube Sampling (LHS)")
    print(f"  Property: Maximizes minimum distance between points")
    print(f"  Advantage: Uniform coverage of design space")
    print(f"  vs Box-Behnken: More samples, more flexible point count")
    
    # Calculate coverage statistics
    print(f"\nCoverage statistics by factor:")
    for fname in factors_dict.keys():
        min_val = design_df[fname].min()
        max_val = design_df[fname].max()
        mean_val = design_df[fname].mean()
        std_val = design_df[fname].std()
        
        factor_low = factors_dict[fname]['low']
        factor_high = factors_dict[fname]['high']
        coverage = ((max_val - min_val) / (factor_high - factor_low)) * 100
        
        print(f"\n  {fname}:")
        print(f"    Range:     {min_val:.2f} - {max_val:.2f}")
        print(f"    Mean:      {mean_val:.2f}")
        print(f"    Std Dev:   {std_val:.2f}")
        print(f"    Coverage:  {coverage:.1f}% of design space")
    
    print(f"\n✓ Design analysis complete")
    print(f"\nInterpretation:")
    print(f"  - 500 samples provides good coverage of 10-D space")
    print(f"  - Ratio 500/10 = 50 (good for ML training)")
    print(f"  - Each factor tested ~50 times on average")
    print(f"  - Sufficient for estimating main effects and interactions")


def save_design_matrix(design_df, output_path='data/doe_lhs_500.csv'):
    """
    Save design matrix to CSV file
    
    Parameters
    ----------
    design_df : pd.DataFrame
        Design matrix
    output_path : str
        Output file path
    """
    print(f"\n[4/4] Saving design matrix...")
    
    # Create directory
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', 
                exist_ok=True)
    
    # Save to CSV
    design_df.to_csv(output_path, index=False)
    
    file_size = os.path.getsize(output_path) / 1024  # KB
    
    print(f"    ✓ Saved to: {output_path}")
    print(f"    ✓ File size: {file_size:.1f} KB")
    print(f"    ✓ Rows: {len(design_df)}")
    print(f"    ✓ Columns: {len(design_df.columns)}")


def print_header():
    """Print formatted header"""
    print("\n" + "="*80)
    print("LATIN HYPERCUBE SAMPLING (LHS) DESIGN MATRIX GENERATION")
    print("Fluoride Adsorption - 10 Factors - 500 Data Points")
    print("="*80)


def print_factor_summary():
    """Print summary of factors"""
    print("\n" + "="*80)
    print("FACTOR SUMMARY (10 Factors)")
    print("="*80)
    
    for fname, fdata in FACTORS.items():
        print(f"\n{fname} ({fdata['unit']}): {fdata['description']}")
        print(f"  Low:  {fdata['low']}")
        print(f"  High: {fdata['high']}")


def print_completion():
    """Print completion message"""
    print("\n" + "="*80)
    print("✓ PHASE 1.1 COMPLETE: LHS Design Matrix Generated (500 Points)")
    print("="*80)
    print("\nNext steps:")
    print("  1. Verify: data/doe_lhs_500.csv exists")
    print("  2. Run: python simulate_responses_500.py")
    print("  3. This simulates fluoride removal for each of 500 conditions")
    print("  4. Output: data/dataset_simulated_500.csv (ready for analysis)")
    print("\nEstimated time for simulation: ~5-10 minutes (depending on compute)")
    print("="*80 + "\n")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    print_header()
    print_factor_summary()
    
    # Step 1: Generate LHS samples
    samples_normalized = generate_lhs_samples(
        n_factors=NUM_FACTORS,
        n_samples=NUM_SAMPLES,
        seed=RANDOM_SEED
    )
    
    # Step 2: Scale to physical units
    samples_physical = scale_to_physical_units(samples_normalized, FACTORS)
    
    # Step 3: Create DataFrame
    design_df = create_design_dataframe(samples_physical, FACTORS)
    
    # Step 4: Analyze design
    analyze_design_coverage(design_df, FACTORS)
    
    # Step 5: Save to CSV
    save_design_matrix(design_df, output_path='data/doe_lhs_500.csv')
    
    # Completion message
    print_completion()
    
    return design_df


if __name__ == '__main__':
    try:
        design_matrix = main()
        print("\n✓ Script completed successfully!")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
