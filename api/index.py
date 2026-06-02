# api/index.py
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import statistics
import json

app = FastAPI()

# Define the request body structure
class AnalyticsRequest(BaseModel):
    regions: list[str]
    threshold_ms: int = 180

# Add CORS middleware with explicit origins (wildcard doesn't work with credentials)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://*", "*"],  # Explicit origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Explicitly include OPTIONS
    allow_headers=["*"],
)

# Handle OPTIONS preflight request explicitly
@app.options("/")
async def handle_options():
    return Response(status_code=200)

# POST endpoint at ROOT path "/"
@app.post("/")
async def analytics_endpoint(request: AnalyticsRequest):
    regions = request.regions
    threshold_ms = request.threshold_ms
    
    # Load telemetry data from JSON file
    try:
        with open("q-vercel-latency.json", "r") as f:
            telemetry_data = json.load(f)
    except FileNotFoundError:
        # Return empty results if file not found
        return {"results": {region: {"avg_latency": 0, "p95_latency": 0, "avg_uptime": 0, "breaches": 0} for region in regions}}
    
    # Calculate per-region metrics
    results = {}
    
    for region in regions:
        region_data = [record for record in telemetry_data if record.get("region") == region]
        
        if not region_data:
            results[region] = {
                "avg_latency": 0,
                "p95_latency": 0,
                "avg_uptime": 0,
                "breaches": 0
            }
            continue
        
        latencies = [record.get("latency_ms", 0) for record in region_data]
        uptimes = [record.get("uptime", 0) for record in region_data]
        
        avg_latency = statistics.mean(latencies) if latencies else 0
        
        sorted_latencies = sorted(latencies)
        p95_index = int(len(sorted_latencies) * 0.95)
        p95_index = min(p95_index, len(sorted_latencies) - 1)
        p95_latency = sorted_latencies[p95_index] if sorted_latencies else 0
        
        avg_uptime = statistics.mean(uptimes) if uptimes else 0
        breaches = sum(1 for latency in latencies if latency > threshold_ms)
        
        results[region] = {
            "avg_latency": round(avg_latency, 2),
            "p95_latency": round(p95_latency, 2),
            "avg_uptime": round(avg_uptime, 2),
            "breaches": breaches
        }
    
    return {"results": results}

# GET endpoint for testing
@app.get("/")
def read_root():
    return {"message": "Analytics endpoint is live! Use POST to send data."}
