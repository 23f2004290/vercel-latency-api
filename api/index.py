from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

with open("q-vercel-latency.json", "r") as f:
    DATA = json.load(f)


@app.options("/")
async def preflight():
    return {"ok": True}


@app.post("/")
async def analyze(payload: dict):

    regions = payload["regions"]
    threshold = payload["threshold_ms"]

    output = []

    for region in regions:

        rows = [x for x in DATA if x["region"] == region]

        latency = [x["latency_ms"] for x in rows]
        uptime = [x["uptime_pct"] for x in rows]

        output.append({
            "region": region,
            "avg_latency": round(sum(latency)/len(latency), 2),
            "p95_latency": round(float(np.percentile(latency, 95)), 2),
            "avg_uptime": round(sum(uptime)/len(uptime), 2),
            "breaches": sum(
                1 for x in rows
                if x["latency_ms"] > threshold
            )
        })

    return output
