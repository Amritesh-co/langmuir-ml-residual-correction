# Minimal DoE generator placeholder
from pyDOE2 import ccdesign
import pandas as pd

FACTORS = {
    'pH': {'low': 3.0, 'center': 6.0, 'high': 9.0},
    'C0': {'low': 1.0, 'center': 5.5, 'high': 10.0},
    'Time': {'low': 10.0, 'center': 65.0, 'high': 120.0},
    'Temp': {'low': 20.0, 'center': 30.0, 'high': 40.0},
    'Flow': {'low': 0.5, 'center': 1.25, 'high': 2.0}
}

if __name__ == '__main__':
    design = ccdesign(n=5, center=6, face='face')
    # scale coded [-1,0,1] to physical ranges
    import numpy as np
    df = pd.DataFrame(design, columns=list(FACTORS.keys()))
    def scale(col, low, center, high):
        # map -1->low, 0->center, 1->high
        return np.where(col<=-0.5, low, np.where(col>=0.5, high, center))
    for k in FACTORS:
        df[k] = scale(df[k], FACTORS[k]['low'], FACTORS[k]['center'], FACTORS[k]['high'])
    df.insert(0, 'Run', range(1, len(df)+1))
    df.to_csv('data/doe_matrix.csv', index=False)
    print('Saved data/doe_matrix.csv')
