#!/usr/bin/env python3
"""
FastAPI backend for the Fluoride Adsorption Hybrid Models web dashboard.
Serves the static frontend (webapp/static/) and exposes prediction endpoints
for the 24-parameter and 4-parameter models.

Every prediction made through /api/predict24 or /api/predict4 (including
from the live dashboard UI) is appended to webapp/data/history_24para.json /
history_4para.json with source="user", alongside the 1000 seed records each
file starts with (see generate_seed_data.py). The Graphs tab reads these
files via /api/history24 and /api/history4.

Run: python3 webapp/backend.py
Then open http://localhost:8000
"""
from pathlib import Path
import json, datetime, threading
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

import models

ROOT = Path(__file__).parent.parent
STATIC = Path(__file__).parent / "static"
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
HIST24 = DATA_DIR / "history_24para.json"
HIST4 = DATA_DIR / "history_4para.json"

_lock = threading.Lock()

app = FastAPI(title="Fluoride Adsorption Hybrid Models API")


def _append_record(path: Path, inp: dict, out: dict):
    with _lock:
        records = json.loads(path.read_text()) if path.exists() else []
        records.append({
            "id": (records[-1]["id"] + 1) if records else 1,
            "source": "user",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "input": inp,
            "output": out,
        })
        path.write_text(json.dumps(records))


class Input24(BaseModel):
    pH: float
    C0: float
    Time: float
    Dose: float
    Temp: float
    Flow: float
    Chloride: float
    Hardness: float
    Carbonate: float
    NOM: float


@app.post("/api/predict24")
def predict_24param(inp: Input24, track: bool = True):
    v = inp.model_dump()
    out = models.predict24(v)
    if track:
        _append_record(HIST24, v, out)
    return out


class Input4(BaseModel):
    pH: float
    Dose: float
    C0: float
    Time: float


@app.post("/api/predict4")
def predict_4param(inp: Input4, track: bool = True):
    v = inp.model_dump()
    out = models.predict4(v)
    if track:
        _append_record(HIST4, v, out)
    return out


@app.get("/api/history24")
def history24():
    records = json.loads(HIST24.read_text()) if HIST24.exists() else []
    return {"count": len(records), "records": records}


@app.get("/api/history4")
def history4():
    records = json.loads(HIST4.read_text()) if HIST4.exists() else []
    return {"count": len(records), "records": records}


# =====================================================================
# --------------------------- COMPARISON --------------------------------
# =====================================================================
@app.get("/api/comparison")
def comparison():
    return {
        "models": [
            {"name": "24-Parameter Hybrid", "dataset": "500 simulated samples", "response": "q_removal (mg/g)",
             "baseline_r2": 0.816, "residual_r2": 0.683, "final_r2": 0.942, "final_rmse": "0.297 mg/g"},
            {"name": "4-Parameter (current)", "dataset": "30 real + 170 generated (N=200)", "response": "% fluoride removal",
             "baseline_r2": 0.826, "residual_r2": -0.146, "final_r2": 0.826, "final_rmse": "0.97 %"},
        ]
    }


# =====================================================================
# ------------------------------ STATIC ---------------------------------
# =====================================================================
app.mount("/images", StaticFiles(directory=str(ROOT)), name="images")
app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")


@app.get("/")
def index():
    return FileResponse(str(STATIC / "index.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
