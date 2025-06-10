from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

app = FastAPI(
    title="Activate BrowserUse API",
    description="Simple API to manage activation state",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://localhost:8000",
        "http://localhost:8080",
        "https://your-frontend-domain.com",  # Add your production domain here
        "*"  # Allow all origins - remove this in production for security
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

@app.get("/value")
async def get_value():
    """Get just the activation value (0 or 1)"""
    return activation_state["value"]

@app.post("/reschedule", response_model=ActivationResponse)
async def reschedule():
    """Set activation state to 1"""
    activation_state["value"] = 1
    return ActivationResponse(value=1, message="Service activated successfully (rescheduled)")

@app.post("/reroute", response_model=ActivationResponse)
async def reroute():
    """Set activation state to 2"""
    activation_state["value"] = 2
    return ActivationResponse(value=2, message="Service activated successfully (rerouted)")

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