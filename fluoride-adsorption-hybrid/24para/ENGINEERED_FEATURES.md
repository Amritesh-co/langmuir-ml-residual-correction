# How the 14 Engineered Features Are Calculated (24-Parameter Model)

The 24-parameter model's residual-ML stage uses **24 total features**: the
10 raw measured factors, plus **14 features derived automatically from those
same 10 values**. This document explains exactly how each of the 14 is
computed.

Source of truth: [`24para/phase4_phase5_final.py`](phase4_phase5_final.py),
function `aug()`. The Gradio app (`gradio_app.py`, function `_aug24()`)
reproduces the identical formulas.

---

## The 10 raw inputs (for reference)

`pH`, `C0` (initial fluoride concentration), `Time` (contact time), `Dose`
(adsorbent dose), `Temp`, `Flow`, `Chloride`, `Hardness`, `Carbonate`, `NOM`

## Step 0: the pH-optimality kernel `g`

Almost every engineered feature builds on one core idea: fluoride adsorption
on this adsorbent peaks around **pH ≈ 6.5** and falls off as pH moves away
from that optimum in either direction. This is captured with a Gaussian bell
curve:

```
g = exp( -(pH - 6.5)^2 / 4.5 )
```

- `g = 1.0` when pH is exactly 6.5 (optimal)
- `g` decays smoothly toward 0 as pH moves away from 6.5 (in either direction)
- The divisor `4.5` controls how wide the "good pH" zone is (a wider divisor
  = more forgiving of pH being off-center)

`g` itself is feature #1. The next several features multiply `g` by other
raw variables, so the model can learn effects that only "switch on" when pH
is near its optimum.

---

## The 14 features

| # | Feature | Formula | What it represents |
|---|---|---|---|
| 1 | `g` | `exp(-(pH-6.5)^2 / 4.5)` | pH-optimality score (1.0 = ideal pH, →0 = far from ideal) |
| 2 | `g_Dose` | `g * Dose` | Dose's effect, weighted by how favorable the pH is |
| 3 | `g_Time` | `g * Time` | Contact time's effect, weighted by pH favorability |
| 4 | `g_C0` | `g * C0` | Initial concentration's effect, weighted by pH favorability |
| 5 | `g_DoseTime` | `g * Dose * Time` | Combined dose×time effect, weighted by pH favorability |
| 6 | `kin` | `1 - exp(-0.01 * Dose * Time)` | Pseudo-kinetic saturation curve — approaches 1 as Dose×Time grows large, modeling that adsorption approaches equilibrium/saturation over time and with more adsorbent |
| 7 | `g_kin` | `g * kin` | Kinetic saturation, weighted by pH favorability |
| 8 | `base_cap` | `g * kin * Dose` | An approximate "effective adsorption capacity" signal combining pH favorability, kinetic saturation, and how much adsorbent is present |
| 9 | `ion_load` | `Chloride/100 + Hardness/500 + Carbonate/100` | A single combined score for competing-ion interference (each ion normalized to a roughly comparable 0–1ish scale before summing) |
| 10 | `g_ion` | `g * ion_load` | Competing-ion interference, weighted by pH favorability |
| 11 | `nom_pen` | `NOM / 50` | Natural Organic Matter, scaled down to a smaller "penalty" range |
| 12 | `pH_dev` | `pH - 6.5` | Signed distance from optimal pH (negative = too acidic, positive = too basic) |
| 13 | `pH_abs_dev` | `\|pH - 6.5\|` | Absolute distance from optimal pH (direction doesn't matter, only how far off) |
| 14 | `pH_dev_sq` | `(pH - 6.5)^2` | Squared distance from optimal pH — penalizes large deviations more steeply than `pH_abs_dev` |

---

## Why engineer these instead of just using the 10 raw values?

A plain linear/polynomial model struggles to represent a sharp bell-curve
relationship (like pH-optimality) using only raw pH terms. By pre-computing
`g` and its interactions, the residual model is handed the *shape* of the
known physical relationship directly, instead of having to reconstruct it
purely from data. This is standard practice for hybridizing domain knowledge
(the physics of adsorption) with a flexible ML model (which then only has to
learn what the physics-based baseline *couldn't* explain — the residual).

All 14 are fully determined by the 10 raw inputs — there is no additional
information content, no extra measurements needed, and no randomness. Given
the same 10 raw values, these 14 will always compute to exactly the same
numbers.
