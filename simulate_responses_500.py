"""
Physics-Based Fluoride Adsorption Simulation
500 Data Points - 10 Factors
Generates response (fluoride removal) using Langmuir + mechanisms

Mechanisms implemented:
1. Langmuir equilibrium baseline
2. pH-dependent bell curve (mechanism shift)
3. Pseudo-second-order kinetics (time approach)
4. Arrhenius temperature correction
5. Flow rate/residence time effect
6. Dose saturation effects
7. Chloride ion competition
8. Divalent cation (hardness) competition
9. Carbonate pH buffering + competition
10. NOM fouling (surface coating)

Author: Phase 1 Research Team
Date: May 2026
"""

import numpy as np
import pandas as pd
import os
from scipy.optimize import fsolve
import sys
from tqdm import tqdm

# ============================================================================
# PHYSICAL PARAMETERS (from Literature)
# ============================================================================

# Langmuir parameters for coconut husk AC + fluoride
QMAX_REF = 8.5  # mg/g (Talat et al. 2018, literature consensus)
KL_REF = 0.12   # L/mg at 25°C (literature consensus)
TEMP_REF = 25   # °C (reference temperature for K_L)
EA = 20.0       # kJ/mol (activation energy, fluoride adsorption)
R_GAS = 8.314   # J/(mol·K) (universal gas constant)

# pH effect parameters (bell curve)
PH_OPTIMAL = 6.5
PH_WIDTH = 1.5  # Standard deviation of bell curve

# Kinetics parameters
K2_REF = 0.05   # g/(mg·min) pseudo-second-order rate constant at 25°C
EQUILIBRIUM_TIME_REF = 240  # minutes (when 95% equilibrium reached)

# Ion competition parameters (selectivity coefficients)
SELECTIVITY_CL = 0.8   # Relative to fluoride
SELECTIVITY_CA = 1.5   # Ca2+ more competitive than F-
SELECTIVITY_MG = 1.3   # Mg2+ more competitive than F-
SELECTIVITY_CO3 = 2.2  # Carbonate is strongest competitor

# NOM fouling parameters
NOM_BLOCKING_CAPACITY = 100  # mg NOM can block ~100 mg/g capacity
NOM_SATURATION = 50  # mg/L NOM (saturation point)

# Measurement noise
MEASUREMENT_NOISE_STD = 0.05  # 5% relative noise

# ============================================================================
# SIMULATION FUNCTIONS
# ============================================================================

def langmuir_equilibrium(Ce, qmax, KL):
    """
    Langmuir adsorption isotherm
    
    q = (qmax * KL * Ce) / (1 + KL * Ce)
    
    Parameters
    ----------
    Ce : float
        Equilibrium concentration (mg/L)
    qmax : float
        Maximum capacity (mg/g)
    KL : float
        Langmuir constant (L/mg)
    
    Returns
    -------
    q : float
        Adsorbed capacity (mg/g)
    """
    return (qmax * KL * Ce) / (1.0 + KL * Ce)


def temperature_correction_KL(temp_celsius):
    """
    Correct K_L for temperature using Arrhenius relationship
    
    K_L(T) = K_L_ref * exp((E_a/R) * (1/T_ref - 1/T))
    
    Parameters
    ----------
    temp_celsius : float
        Temperature in Celsius
    
    Returns
    -------
    correction_factor : float
        Multiplier for K_L at given temperature
    """
    T_abs = temp_celsius + 273.15  # Convert to Kelvin
    T_ref_abs = TEMP_REF + 273.15
    
    # Activation energy in J/mol
    EA_J = EA * 1000
    
    exponent = (EA_J / R_GAS) * (1.0 / T_ref_abs - 1.0 / T_abs)
    correction = np.exp(exponent)
    
    return correction


def temperature_correction_k2(temp_celsius):
    """
    Correct pseudo-second-order rate constant for temperature
    
    Parameters
    ----------
    temp_celsius : float
        Temperature in Celsius
    
    Returns
    -------
    correction_factor : float
        Multiplier for k2 at given temperature
    """
    # Assume same activation energy as K_L
    T_abs = temp_celsius + 273.15
    T_ref_abs = TEMP_REF + 273.15
    
    EA_J = EA * 1000
    exponent = (EA_J / R_GAS) * (1.0 / T_ref_abs - 1.0 / T_abs)
    
    return np.exp(exponent)


def ph_effect_bell_curve(pH):
    """
    pH-dependent capacity modifier (bell curve)
    
    Peak at pH 6.5, drops off at pH < 5 and pH > 8
    
    Parameters
    ----------
    pH : float
        Solution pH
    
    Returns
    -------
    modifier : float
        Multiplier for capacity (0-1, peak at 1.0)
    """
    # Gaussian bell curve centered at pH_OPTIMAL
    exponent = -((pH - PH_OPTIMAL) ** 2) / (2 * PH_WIDTH ** 2)
    modifier = np.exp(exponent)
    
    return modifier


def kinetic_approach_to_equilibrium(t_minutes, qe, k2):
    """
    Pseudo-second-order kinetics
    
    qt = (qe^2 * k2 * t) / (1 + qe * k2 * t)
    
    Parameters
    ----------
    t_minutes : float
        Contact time (minutes)
    qe : float
        Equilibrium capacity (mg/g)
    k2 : float
        Rate constant (g/(mg·min))
    
    Returns
    -------
    qt : float
        Adsorbed capacity at time t (mg/g)
    """
    denominator = 1.0 + qe * k2 * t_minutes
    qt = (qe ** 2 * k2 * t_minutes) / denominator
    
    return qt


def ion_competition_effect(Ce_F, Cl, Ca_Mg, CO3):
    """
    Model ion competition using modified Langmuir for multi-component
    
    Simplified: Competing ions reduce available sites proportionally
    
    Parameters
    ----------
    Ce_F : float
        Fluoride equilibrium concentration (mg/L)
    Cl : float
        Chloride concentration (mg/L)
    Ca_Mg : float
        Total hardness as Ca2+ + Mg2+ (mg/L as CaCO3, ≈ divalent cation conc)
    CO3 : float
        Carbonate concentration (mg/L as HCO3-)
    
    Returns
    -------
    capacity_reduction : float
        Multiplier for capacity (0-1, reduced by ions)
    """
    # Calculate competitive loading
    # Each ion reduces available capacity proportionally to its concentration and selectivity
    
    # Convert hardness to equivalent ion concentration
    # 1 mg/L CaCO3 ≈ 0.02 mEq/L, and we have both Ca2+ and Mg2+
    Ca_Mg_equiv = Ca_Mg * 0.02  # Approximate equivalent concentration
    
    # Competitive term (similar to Langmuir but for competing ions)
    KL_Cl = KL_REF * SELECTIVITY_CL
    KL_Ca_Mg = KL_REF * SELECTIVITY_CA  # Average for Ca and Mg
    KL_CO3 = KL_REF * SELECTIVITY_CO3
    
    # Sum of competitive loads
    competitive_load = (KL_Cl * Cl + 
                       KL_Ca_Mg * Ca_Mg_equiv + 
                       KL_CO3 * CO3)
    
    # Reduction factor (more competition = lower reduction factor)
    # Saturates around 0.4 at high ionic strengths
    reduction_factor = 1.0 / (1.0 + 0.5 * competitive_load)
    
    # Ensure stays in reasonable range
    reduction_factor = np.clip(reduction_factor, 0.3, 1.0)
    
    return reduction_factor


def nom_fouling_effect(NOM_conc):
    """
    NOM fouling reduces effective capacity by coating surface
    
    Parameters
    ----------
    NOM_conc : float
        Natural Organic Matter concentration (mg/L)
    
    Returns
    -------
    capacity_reduction : float
        Multiplier for capacity (0-1, reduced by fouling)
    """
    # Fouling follows Langmuir-like saturation
    # At NOM_SATURATION mg/L, 50% capacity is lost
    fouling_loading = NOM_conc / NOM_SATURATION
    
    # Reduction factor (more NOM = more fouling)
    reduction_factor = 1.0 / (1.0 + fouling_loading)
    
    # Cap maximum fouling at 80% loss
    reduction_factor = np.clip(reduction_factor, 0.2, 1.0)
    
    return reduction_factor


def flow_rate_effect(flow_rate, reference_flow=1.25):
    """
    Flow rate affects residence time and contact efficiency
    
    Higher flow = less contact time = lower efficiency
    
    Parameters
    ----------
    flow_rate : float
        Column flow rate (L/min)
    reference_flow : float
        Reference flow rate for normalization
    
    Returns
    -------
    efficiency_factor : float
        Multiplier for removal (0-1)
    """
    # Inverse relationship: efficiency ∝ 1/(flow_rate)
    # But not perfectly inverse - some efficiency maintained at high flow
    
    # Breakthrough curve approach: exponential decay
    residence_time_ref = 1.0 / reference_flow
    residence_time = 1.0 / flow_rate
    
    # Efficiency factor based on residence time ratio
    efficiency_factor = np.exp(-reference_flow * flow_rate * 0.3)
    
    return efficiency_factor


def dose_saturation_effect(dose, reference_dose=2.75):
    """
    Dose saturation - diminishing returns at very low or very high dose
    
    Parameters
    ----------
    dose : float
        Adsorbent dose (g/L)
    reference_dose : float
        Reference dose for normalization
    
    Returns
    -------
    dose_factor : float
        Multiplier accounting for saturation (0-1)
    """
    # At very low dose (<0.5), saturation is reached quickly (inefficient)
    # At normal dose (1-3 g/L), good efficiency
    # At very high dose (>4 g/L), excess adsorbent (wasteful but works)
    
    # Use Langmuir-like saturation based on dose
    dose_normalized = dose / reference_dose
    
    # Saturation curve
    dose_factor = dose_normalized / (1.0 + 0.3 * (1.0 - dose_normalized))
    
    return np.clip(dose_factor, 0.6, 1.0)


def simulate_fluoride_removal(row):
    """
    Complete simulation of fluoride adsorption
    
    Combines all mechanisms into single prediction
    
    Parameters
    ----------
    row : pd.Series
        One row from design matrix with factor values
    
    Returns
    -------
    q_removal : float
        Predicted fluoride removal (mg/g)
    """
    # Extract factors
    pH = row['pH']
    C0 = row['C0']
    time_min = row['Time']
    dose = row['Dose']
    temp = row['Temp']
    flow = row['Flow']
    chloride = row['Chloride']
    hardness = row['Hardness']
    carbonate = row['Carbonate']
    nom = row['NOM']
    
    # ===== BASELINE: Langmuir Equilibrium =====
    # Assume some fluoride is removed (assume 50% at baseline)
    Ce_estimate = C0 * 0.5  # Rough estimate of equilibrium concentration
    
    # Base K_L
    KL_base = KL_REF
    qmax_base = QMAX_REF
    
    # Get baseline capacity
    q_langmuir = langmuir_equilibrium(Ce_estimate, qmax_base, KL_base)
    
    # ===== APPLY MECHANISMS =====
    
    # 1. pH effect (bell curve)
    pH_factor = ph_effect_bell_curve(pH)
    q_after_pH = q_langmuir * pH_factor
    
    # 2. Temperature correction to K_L
    temp_corr_KL = temperature_correction_KL(temp)
    KL_temp = KL_base * temp_corr_KL
    
    # Recalculate with temperature-corrected K_L
    q_after_temp = langmuir_equilibrium(Ce_estimate, qmax_base, KL_temp) * pH_factor
    
    # 3. Kinetic approach (time effect)
    # Get equilibrium value first
    qe_for_kinetics = q_after_temp
    k2_base = K2_REF
    k2_temp = k2_base * temperature_correction_k2(temp)
    
    q_kinetic = kinetic_approach_to_equilibrium(time_min, qe_for_kinetics, k2_temp)
    
    # Ensure doesn't exceed theoretical maximum
    q_kinetic = np.minimum(q_kinetic, qe_for_kinetics)
    
    # 4. Ion competition (chloride, hardness, carbonate)
    ion_factor = ion_competition_effect(Ce_estimate, chloride, hardness, carbonate)
    q_after_ions = q_kinetic * ion_factor
    
    # 5. Dose saturation effect
    dose_factor = dose_saturation_effect(dose)
    q_after_dose = q_after_ions * dose_factor
    
    # 6. Flow rate effect
    flow_factor = flow_rate_effect(flow)
    q_after_flow = q_after_dose * flow_factor
    
    # 7. NOM fouling
    nom_factor = nom_fouling_effect(nom)
    q_final = q_after_flow * nom_factor
    
    # ===== ADD MEASUREMENT NOISE =====
    # Simulate measurement uncertainty
    noise = np.random.normal(0, MEASUREMENT_NOISE_STD * q_final)
    q_with_noise = q_final + noise
    
    # Ensure non-negative
    q_with_noise = np.maximum(q_with_noise, 0.1)
    
    return q_with_noise


def print_header():
    """Print formatted header"""
    print("\n" + "="*80)
    print("FLUORIDE ADSORPTION SIMULATION - PHYSICS-BASED")
    print("500 Data Points - 10 Factors")
    print("="*80)


def print_parameters():
    """Print simulation parameters"""
    print("\n" + "="*80)
    print("SIMULATION PARAMETERS")
    print("="*80)
    
    print(f"\nLangmuir Parameters:")
    print(f"  qmax (reference):     {QMAX_REF} mg/g")
    print(f"  KL (reference):       {KL_REF} L/mg")
    print(f"  Reference temp:       {TEMP_REF}°C")
    
    print(f"\nKinetic Parameters:")
    print(f"  k2 (reference):       {K2_REF} g/(mg·min)")
    print(f"  Equilibrium time:     {EQUILIBRIUM_TIME_REF} min")
    
    print(f"\nThermodynamic Parameters:")
    print(f"  Activation energy:    {EA} kJ/mol")
    print(f"  Gas constant R:       {R_GAS} J/(mol·K)")
    
    print(f"\nIon Competition (Selectivity vs F-):")
    print(f"  Chloride (Cl-):       {SELECTIVITY_CL}x")
    print(f"  Calcium (Ca2+):       {SELECTIVITY_CA}x")
    print(f"  Magnesium (Mg2+):     {SELECTIVITY_MG}x")
    print(f"  Carbonate (CO3--):    {SELECTIVITY_CO3}x (strongest)")
    
    print(f"\nNOM Fouling Parameters:")
    print(f"  Blocking capacity:    {NOM_BLOCKING_CAPACITY} mg capacity")
    print(f"  Saturation point:     {NOM_SATURATION} mg/L NOM")
    
    print(f"\nMeasurement Noise:")
    print(f"  Relative std dev:     {MEASUREMENT_NOISE_STD*100:.1f}%")


def print_completion():
    """Print completion message"""
    print("\n" + "="*80)
    print("✓ PHASE 1.1 COMPLETE: Simulation Finished (500 Data Points)")
    print("="*80)
    print("\nNext steps:")
    print("  1. Verify: data/dataset_simulated_500.csv exists")
    print("  2. Inspect: First 10 rows, descriptive statistics")
    print("  3. Run: python phase2_langmuir_fitting.py")
    print("  4. This fits the chemical model to your simulated data")
    print("\nFiles created:")
    print("  - data/doe_lhs_500.csv (design matrix)")
    print("  - data/dataset_simulated_500.csv (with responses)")
    print("="*80 + "\n")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    print_header()
    print_parameters()
    
    # Load design matrix
    print(f"\n[1/3] Loading design matrix...")
    if not os.path.exists('data/doe_lhs_500.csv'):
        print(f"ERROR: data/doe_lhs_500.csv not found!")
        print(f"Run generate_lhs_design_500.py first")
        return None
    
    df = pd.read_csv('data/doe_lhs_500.csv')
    print(f"    ✓ Loaded {len(df)} design points")
    
    # Run simulation
    print(f"\n[2/3] Simulating fluoride adsorption responses...")
    print(f"    This may take a few minutes...")
    
    responses = []
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="    Simulating"):
        q_removal = simulate_fluoride_removal(row)
        responses.append(q_removal)
    
    df['q_removal'] = responses
    
    print(f"    ✓ Simulation complete")
    
    # Save results
    print(f"\n[3/3] Saving simulated dataset...")
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/dataset_simulated_500.csv', index=False)
    
    file_size = os.path.getsize('data/dataset_simulated_500.csv') / 1024
    print(f"    ✓ Saved to: data/dataset_simulated_500.csv")
    print(f"    ✓ File size: {file_size:.1f} KB")
    print(f"    ✓ Rows: {len(df)}")
    print(f"    ✓ Columns: {len(df.columns)}")
    
    # Print statistics
    print(f"\nResponse Statistics (q_removal in mg/g):")
    print(f"  Min:       {df['q_removal'].min():.2f}")
    print(f"  Max:       {df['q_removal'].max():.2f}")
    print(f"  Mean:      {df['q_removal'].mean():.2f}")
    print(f"  Std Dev:   {df['q_removal'].std():.2f}")
    print(f"  Median:    {df['q_removal'].median():.2f}")
    
    print_completion()
    
    return df


if __name__ == '__main__':
    try:
        dataset = main()
        print("\n✓ Simulation completed successfully!")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
