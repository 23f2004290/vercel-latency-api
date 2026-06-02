from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

with open("q-vercel-latency.json") as f:
    DATA = json.load(f)


@app.post("/")
async def metrics(body: dict):

    threshold = body["threshold_ms"]

    result = []

    for region in body["regions"]:

        rows = [
            r for r in DATA
            if r["region"] == region
        ]

        lat = [r["latency_ms"] for r in rows]
        up = [r["uptime_pct"] for r in rows]

        result.append({
            "region": region,
            "avg_latency": round(sum(lat)/len(lat),2),
            "p95_latency": round(float(np.percentile(lat,95)),2),
            "avg_uptime": round(sum(up)/len(up),2),
            "breaches": sum(
                1
                for r in rows
                if r["latency_ms"] > threshold
            )
        })

    return result
