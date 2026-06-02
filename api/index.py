# api/index.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import os
import json
import statistics

app = FastAPI()

# Enable CORS for POST requests from any origin
@app.post("/api/analytics")
async def analytics_endpoint(request_data: Dict[str, Any]):
    # Get regions and threshold from request
    regions = request_data.get("regions", [])
    threshold_ms = request_data.get("threshold_ms", 180)
    
    if not regions:
        raise HTTPException(status_code=400, detail="Missing 'regions' in request")
    
    # Load telemetry data (replace with actual file loading or API call)
    # For this example, we'll simulate loading from a JSON file
    try:
        with open("q-vercel-latency.json", "r") as f:
            telemetry_data = json.load(f)
    except FileNotFoundError:
        # If file doesn't exist locally, use sample data
        telemetry_data = []
    
    # Calculate per-region metrics
    results = {}
    
    for region in regions:
        # Filter data for this region
        region_data = [record for record in telemetry_data if record.get("region") == region]
        
        if not region_data:
            results[region] = {
                "avg_latency": 0,
                "p95_latency": 0,
                "avg_uptime": 0,
                "breaches": 0
            }
            continue
        
        # Extract latencies and uptimes
        latencies = [record.get("latency_ms", 0) for record in region_data]
        uptimes = [record.get("uptime", 0) for record in region_data]
        
        # Calculate metrics
        avg_latency = statistics.mean(latencies) if latencies else 0
        
        # Calculate p95 (95th percentile)
        sorted_latencies = sorted(latencies)
        p95_index = int(len(sorted_latencies) * 0.95)
        p95_latency = sorted_latencies[p95_index] if sorted_latencies else 0
        
        avg_uptime = statistics.mean(uptimes) if uptimes else 0
        
        # Count breaches (records above threshold)
        breaches = sum(1 for latency in latencies if latency > threshold_ms)
        
        results[region] = {
            "avg_latency": round(avg_latency, 2),
            "p95_latency": round(p95_latency, 2),
            "avg_uptime": round(avg_uptime, 2),
            "breaches": breaches
        }
    
    return {"results": results}

# Root endpoint for testing
@app.get("/")
def read_root():
    return {"message": "Analytics endpoint is live!"}
