from fastapi import FastAPI
from pydantic import BaseModel
import os

app = FastAPI(
    title="Activate BrowserUse API",
    description="Simple API to manage activation state",
    version="1.0.0"
)

# Simple in-memory state (starts at 0)
activation_state = {"value": 0}

class StatusResponse(BaseModel):
    value: int
    status: str

class ActivationResponse(BaseModel):
    value: int
    message: str

@app.get("/", response_model=StatusResponse)
async def root():
    """Get current activation status"""
    status = "inactive" if activation_state["value"] == 0 else "active"
    return StatusResponse(value=activation_state["value"], status=status)

@app.get("/status", response_model=StatusResponse)
async def get_status():
    """Get current activation status"""
    status = "inactive" if activation_state["value"] == 0 else "active"
    return StatusResponse(value=activation_state["value"], status=status)

@app.post("/activate", response_model=ActivationResponse)
async def activate():
    """Set activation state to 1"""
    activation_state["value"] = 1
    return ActivationResponse(value=1, message="Service activated successfully")

@app.post("/deactivate", response_model=ActivationResponse)
async def deactivate():
    """Set activation state to 0"""
    activation_state["value"] = 0
    return ActivationResponse(value=0, message="Service deactivated successfully")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "activation_value": activation_state["value"]}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)