#!/usr/bin/env python3
"""
Generates 1000 tracked prediction records for the 24-parameter model and
1000 for the 4-parameter model, by sampling their input spaces via Latin
Hypercube Sampling and running each sample through the real, deployed
model (webapp/models.py -- the same code the FastAPI backend uses).

Output: webapp/data/history_24para.json, webapp/data/history_4para.json
Each record: {id, source: "seed", timestamp, input: {...}, output: {...}}

These files double as the initial dataset for the dashboard's "Graphs" tab,
and the backend appends new records to them (source: "user") every time
someone submits a prediction from the UI.

Run: python3 webapp/generate_seed_data.py
"""
from pathlib import Path
import json, datetime
import numpy as np
from scipy.stats import qmc

import models

SEED = 42
N = 1000
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)


def gen_records(fact_names, bounds, predict_fn, n):
    sampler = qmc.LatinHypercube(d=len(fact_names), seed=SEED)
    u = sampler.random(n=n)
    lo = np.array([bounds[f][0] for f in fact_names])
    hi = np.array([bounds[f][1] for f in fact_names])
    X = qmc.scale(u, lo, hi)

    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    records = []
    for i, row in enumerate(X):
        v = {f: round(float(val), 4) for f, val in zip(fact_names, row)}
        out = predict_fn(v)
        records.append({"id": i + 1, "source": "seed", "timestamp": now, "input": v, "output": out})
    return records


def main():
    print(f"Generating {N} seed records for 24-parameter model...")
    recs24 = gen_records(models.FACT10, models.BOUNDS24, models.predict24, N)
    (DATA_DIR / "history_24para.json").write_text(json.dumps(recs24, indent=None))
    print(f"  -> {DATA_DIR / 'history_24para.json'} ({len(recs24)} records)")

    print(f"Generating {N} seed records for 4-parameter model...")
    recs4 = gen_records(models.FACT4, models.BOUNDS4, models.predict4, N)
    (DATA_DIR / "history_4para.json").write_text(json.dumps(recs4, indent=None))
    print(f"  -> {DATA_DIR / 'history_4para.json'} ({len(recs4)} records)")


if __name__ == "__main__":
    main()
