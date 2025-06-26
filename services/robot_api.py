from fastapi import FastAPI
import subprocess

app = FastAPI(title="Lab Robot API")

@app.post("/run_aliquot")
async def run_aliquot():
    # run the protocol in simulation and return first 20 log lines
    log = subprocess.check_output([
        "opentrons_simulate", "scripts/ot2_aliquot.py"
    ], text=True)
    return {"status": "ok", "log": log.splitlines()[:20]}
