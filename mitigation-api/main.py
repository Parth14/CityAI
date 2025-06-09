from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import httpx
import os
import json
from enum import Enum

app = FastAPI(
    title="Shipping Risk Mitigation API",
    description="API for generating shipping risk mitigation strategies using AI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class WeatherData(BaseModel):
    temperature: Optional[float] = None
    wind_speed: Optional[float] = None
    wave_height: Optional[float] = None
    visibility: Optional[float] = None
    conditions: Optional[str] = None

class WeatherConditions(BaseModel):
    risk_score: int = Field(..., ge=1, le=10, description="Risk score from 1 (lowest) to 10 (highest)")
    risk_description: str = Field(..., min_length=1, max_length=1000)
    weather_summary: str = Field(..., min_length=1, max_length=1000)
    departure_weather: WeatherData
    destination_weather: WeatherData
    estimated_travel_days: int = Field(..., ge=1, le=365)

class GeopoliticalConditions(BaseModel):
    risk_score: int = Field(..., ge=1, le=10, description="Risk score from 1 (lowest) to 10 (highest)")
    risk_description: str = Field(..., min_length=1, max_length=1000)
    geopolitical_summary: str = Field(..., min_length=1, max_length=1000)
    chokepoints: List[str] = Field(default_factory=list)
    security_zones: List[str] = Field(default_factory=list)
    shipping_lanes: str

class ShippingRequest(BaseModel):
    # Basic shipping parameters
    departure_port: str = Field(..., min_length=2, max_length=100)
    destination_port: str = Field(..., min_length=2, max_length=100)
    departure_date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}
    carrier_name: str = Field(..., min_length=2, max_length=100)
    goods_type: str = Field(..., min_length=2, max_length=100)
    
    # Weather conditions
    weather_conditions: WeatherConditions
    
    # Geopolitical conditions
    geopolitical_conditions: GeopoliticalConditions

    @validator('departure_date')
    def validate_departure_date(cls, v):
        try:
            departure_date = datetime.strptime(v, '%Y-%m-%d').date()
            today = date.today()
            if departure_date <= today:
                raise ValueError('Departure date must be in the future')
            if (departure_date - today).days > 365:
                raise ValueError('Departure date must be within 1 year')
            return v
        except ValueError as e:
            if "time data" in str(e):
                raise ValueError('Invalid date format. Use YYYY-MM-DD')
            raise e

class MitigationStrategy(BaseModel):
    strategy_type: str
    priority: str  # "High", "Medium", "Low"
    description: str
    implementation_time: str
    cost_impact: str
    risk_reduction: str

class MitigationResponse(BaseModel):
    overall_risk_assessment: str
    recommended_action: str
    strategies: List[MitigationStrategy]
    alternative_routes: Optional[List[str]] = None
    timeline_recommendations: Optional[str] = None
    compliance_checks: Optional[List[str]] = None

# Grok API Integration
class GrokClient:
    def __init__(self):
        self.api_key = os.getenv("XAI_API_KEY")
        self.base_url = "https://api.x.ai/v1"
        
        if not self.api_key:
            raise ValueError("XAI_API_KEY environment variable is required")
    
    async def generate_mitigation_strategies(self, shipping_data: ShippingRequest) -> Dict[str, Any]:
        """Generate mitigation strategies using Grok API"""
        
        prompt = self._create_prompt(shipping_data)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are a shipping logistics expert specializing in risk mitigation. Provide practical, actionable strategies for reducing shipping risks. Format your response as valid JSON with the structure specified."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "model": "grok-beta",
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Extract JSON from the response
                try:
                    # Try to parse the content as JSON directly
                    return json.loads(content)
                except json.JSONDecodeError:
                    # If that fails, try to extract JSON from markdown code blocks
                    import re
                    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group(1))
                    else:
                        # Fallback: create a structured response from the text
                        return self._parse_text_response(content, shipping_data)
                        
            except httpx.HTTPStatusError as e:
                raise HTTPException(status_code=500, detail=f"Grok API error: {e.response.text}")
            except httpx.TimeoutException:
                raise HTTPException(status_code=500, detail="Grok API timeout")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error calling Grok API: {str(e)}")
    
    def _create_prompt(self, shipping_data: ShippingRequest) -> str:
        """Create a detailed prompt for Grok"""
        
        return f"""
Analyze the following shipping scenario and provide mitigation strategies to reduce risks:

SHIPPING DETAILS:
- Route: {shipping_data.departure_port} → {shipping_data.destination_port}
- Departure Date: {shipping_data.departure_date}
- Carrier: {shipping_data.carrier_name}
- Goods Type: {shipping_data.goods_type}

WEATHER CONDITIONS (Risk Score: {shipping_data.weather_conditions.risk_score}/10):
- Summary: {shipping_data.weather_conditions.weather_summary}
- Risk Description: {shipping_data.weather_conditions.risk_description}
- Estimated Travel Days: {shipping_data.weather_conditions.estimated_travel_days}
- Departure Weather: {shipping_data.weather_conditions.departure_weather.dict()}
- Destination Weather: {shipping_data.weather_conditions.destination_weather.dict()}

GEOPOLITICAL CONDITIONS (Risk Score: {shipping_data.geopolitical_conditions.risk_score}/10):
- Summary: {shipping_data.geopolitical_conditions.geopolitical_summary}
- Risk Description: {shipping_data.geopolitical_conditions.risk_description}
- Chokepoints: {', '.join(shipping_data.geopolitical_conditions.chokepoints)}
- Security Zones: {', '.join(shipping_data.geopolitical_conditions.security_zones)}
- Shipping Lanes: {shipping_data.geopolitical_conditions.shipping_lanes}

Please provide a comprehensive risk mitigation analysis in the following JSON format:

{{
    "overall_risk_assessment": "Overall assessment of the shipping risk level and key concerns",
    "recommended_action": "Primary recommended action (e.g., proceed as planned, delay, reroute)",
    "strategies": [
        {{
            "strategy_type": "Weather Mitigation" | "Route Optimization" | "Documentation & Compliance" | "Insurance & Financial" | "Operational Adjustment",
            "priority": "High" | "Medium" | "Low",
            "description": "Detailed description of the mitigation strategy",
            "implementation_time": "Time needed to implement (e.g., 1-2 days, immediate, 1 week)",
            "cost_impact": "Estimated cost impact (e.g., minimal, moderate, significant)",
            "risk_reduction": "Expected risk reduction percentage or description"
        }}
    ],
    "alternative_routes": ["List of alternative route suggestions if applicable"],
    "timeline_recommendations": "Specific timing recommendations (e.g., delay by 3 days, depart immediately)",
    "compliance_checks": ["List of specific documents or compliance items to verify"]
}}

Focus on practical, actionable strategies that address the specific risks identified in the weather and geopolitical conditions.
"""
    
    def _parse_text_response(self, content: str, shipping_data: ShippingRequest) -> Dict[str, Any]:
        """Fallback method to parse non-JSON responses into structured format"""
        
        # Create a basic response structure if JSON parsing fails
        overall_risk = "High" if (shipping_data.weather_conditions.risk_score + shipping_data.geopolitical_conditions.risk_score) > 12 else "Medium"
        
        return {
            "overall_risk_assessment": f"{overall_risk} risk level detected based on weather (score: {shipping_data.weather_conditions.risk_score}) and geopolitical conditions (score: {shipping_data.geopolitical_conditions.risk_score})",
            "recommended_action": "Review detailed analysis and implement suggested mitigation strategies",
            "strategies": [
                {
                    "strategy_type": "Weather Mitigation",
                    "priority": "High" if shipping_data.weather_conditions.risk_score > 7 else "Medium",
                    "description": "Monitor weather conditions closely and consider route adjustments",
                    "implementation_time": "1-2 days",
                    "cost_impact": "minimal to moderate",
                    "risk_reduction": "20-40%"
                }
            ],
            "alternative_routes": [],
            "timeline_recommendations": "Review conditions 24-48 hours before departure",
            "compliance_checks": ["Verify carrier insurance", "Check cargo documentation"]
        }

# Initialize Grok client
try:
    grok_client = GrokClient()
except ValueError as e:
    grok_client = None
    print(f"Warning: {e}")

@app.get("/")
async def root():
    return {
        "message": "Shipping Risk Mitigation API",
        "version": "1.0.0",
        "endpoints": {
            "/analyze-shipping-risk": "POST - Analyze shipping risks and get mitigation strategies",
            "/health": "GET - Health check endpoint"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "grok_api_configured": grok_client is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/analyze-shipping-risk", response_model=MitigationResponse)
async def analyze_shipping_risk(request: ShippingRequest):
    """
    Analyze shipping risk and provide mitigation strategies
    """
    
    if not grok_client:
        raise HTTPException(
            status_code=500, 
            detail="Grok API not configured. Please set XAI_API_KEY environment variable."
        )
    
    try:
        # Call Grok API to generate mitigation strategies
        grok_response = await grok_client.generate_mitigation_strategies(request)
        
        # Validate and structure the response
        response = MitigationResponse(**grok_response)
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing shipping risk: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port))
    carrier_name: str = Field(..., min_length=2, max_length=100)
    goods_type: str = Field(..., min_length=2, max_length=100)
    
    # Weather conditions
    weather_conditions: WeatherConditions
    
    # Geopolitical conditions
    geopolitical_conditions: GeopoliticalConditions

    @validator('departure_date')
    def validate_departure_date(cls, v):
        try:
            departure_date = datetime.strptime(v, '%Y-%m-%d').date()
            today = date.today()
            if departure_date <= today:
                raise ValueError('Departure date must be in the future')
            if (departure_date - today).days > 365:
                raise ValueError('Departure date must be within 1 year')
            return v
        except ValueError as e:
            if "time data" in str(e):
                raise ValueError('Invalid date format. Use YYYY-MM-DD')
            raise e

class MitigationStrategy(BaseModel):
    strategy_type: str
    priority: str  # "High", "Medium", "Low"
    description: str
    implementation_time: str
    cost_impact: str
    risk_reduction: str

class MitigationResponse(BaseModel):
    overall_risk_assessment: str
    recommended_action: str
    strategies: List[MitigationStrategy]
    alternative_routes: Optional[List[str]] = None
    timeline_recommendations: Optional[str] = None
    compliance_checks: Optional[List[str]] = None

# Grok API Integration
class GrokClient:
    def __init__(self):
        self.api_key = os.getenv("XAI_API_KEY")
        self.base_url = "https://api.x.ai/v1"
        
        if not self.api_key:
            raise ValueError("XAI_API_KEY environment variable is required")
    
    async def generate_mitigation_strategies(self, shipping_data: ShippingRequest) -> Dict[str, Any]:
        """Generate mitigation strategies using Grok API"""
        
        prompt = self._create_prompt(shipping_data)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are a shipping logistics expert specializing in risk mitigation. Provide practical, actionable strategies for reducing shipping risks. Format your response as valid JSON with the structure specified."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "model": "grok-beta",
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Extract JSON from the response
                try:
                    # Try to parse the content as JSON directly
                    return json.loads(content)
                except json.JSONDecodeError:
                    # If that fails, try to extract JSON from markdown code blocks
                    import re
                    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group(1))
                    else:
                        # Fallback: create a structured response from the text
                        return self._parse_text_response(content, shipping_data)
                        
            except httpx.HTTPStatusError as e:
                raise HTTPException(status_code=500, detail=f"Grok API error: {e.response.text}")
            except httpx.TimeoutException:
                raise HTTPException(status_code=500, detail="Grok API timeout")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error calling Grok API: {str(e)}")
    
    def _create_prompt(self, shipping_data: ShippingRequest) -> str:
        """Create a detailed prompt for Grok"""
        
        return f"""
Analyze the following shipping scenario and provide mitigation strategies to reduce risks:

SHIPPING DETAILS:
- Route: {shipping_data.departure_port} → {shipping_data.destination_port}
- Departure Date: {shipping_data.departure_date}
- Carrier: {shipping_data.carrier_name}
- Goods Type: {shipping_data.goods_type}

WEATHER CONDITIONS (Risk Score: {shipping_data.weather_conditions.risk_score}/10):
- Summary: {shipping_data.weather_conditions.weather_summary}
- Risk Description: {shipping_data.weather_conditions.risk_description}
- Estimated Travel Days: {shipping_data.weather_conditions.estimated_travel_days}
- Departure Weather: {shipping_data.weather_conditions.departure_weather.dict()}
- Destination Weather: {shipping_data.weather_conditions.destination_weather.dict()}

GEOPOLITICAL CONDITIONS (Risk Score: {shipping_data.geopolitical_conditions.risk_score}/10):
- Summary: {shipping_data.geopolitical_conditions.geopolitical_summary}
- Risk Description: {shipping_data.geopolitical_conditions.risk_description}
- Chokepoints: {', '.join(shipping_data.geopolitical_conditions.chokepoints)}
- Security Zones: {', '.join(shipping_data.geopolitical_conditions.security_zones)}
- Shipping Lanes: {shipping_data.geopolitical_conditions.shipping_lanes}

Please provide a comprehensive risk mitigation analysis in the following JSON format:

{{
    "overall_risk_assessment": "Overall assessment of the shipping risk level and key concerns",
    "recommended_action": "Primary recommended action (e.g., proceed as planned, delay, reroute)",
    "strategies": [
        {{
            "strategy_type": "Weather Mitigation" | "Route Optimization" | "Documentation & Compliance" | "Insurance & Financial" | "Operational Adjustment",
            "priority": "High" | "Medium" | "Low",
            "description": "Detailed description of the mitigation strategy",
            "implementation_time": "Time needed to implement (e.g., 1-2 days, immediate, 1 week)",
            "cost_impact": "Estimated cost impact (e.g., minimal, moderate, significant)",
            "risk_reduction": "Expected risk reduction percentage or description"
        }}
    ],
    "alternative_routes": ["List of alternative route suggestions if applicable"],
    "timeline_recommendations": "Specific timing recommendations (e.g., delay by 3 days, depart immediately)",
    "compliance_checks": ["List of specific documents or compliance items to verify"]
}}

Focus on practical, actionable strategies that address the specific risks identified in the weather and geopolitical conditions.
"""
    
    def _parse_text_response(self, content: str, shipping_data: ShippingRequest) -> Dict[str, Any]:
        """Fallback method to parse non-JSON responses into structured format"""
        
        # Create a basic response structure if JSON parsing fails
        overall_risk = "High" if (shipping_data.weather_conditions.risk_score + shipping_data.geopolitical_conditions.risk_score) > 12 else "Medium"
        
        return {
            "overall_risk_assessment": f"{overall_risk} risk level detected based on weather (score: {shipping_data.weather_conditions.risk_score}) and geopolitical conditions (score: {shipping_data.geopolitical_conditions.risk_score})",
            "recommended_action": "Review detailed analysis and implement suggested mitigation strategies",
            "strategies": [
                {
                    "strategy_type": "Weather Mitigation",
                    "priority": "High" if shipping_data.weather_conditions.risk_score > 7 else "Medium",
                    "description": "Monitor weather conditions closely and consider route adjustments",
                    "implementation_time": "1-2 days",
                    "cost_impact": "minimal to moderate",
                    "risk_reduction": "20-40%"
                }
            ],
            "alternative_routes": [],
            "timeline_recommendations": "Review conditions 24-48 hours before departure",
            "compliance_checks": ["Verify carrier insurance", "Check cargo documentation"]
        }

# Initialize Grok client
try:
    grok_client = GrokClient()
except ValueError as e:
    grok_client = None
    print(f"Warning: {e}")

@app.get("/")
async def root():
    return {
        "message": "Shipping Risk Mitigation API",
        "version": "1.0.0",
        "endpoints": {
            "/analyze-shipping-risk": "POST - Analyze shipping risks and get mitigation strategies",
            "/health": "GET - Health check endpoint"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "grok_api_configured": grok_client is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/analyze-shipping-risk", response_model=MitigationResponse)
async def analyze_shipping_risk(request: ShippingRequest):
    """
    Analyze shipping risk and provide mitigation strategies
    """
    
    if not grok_client:
        raise HTTPException(
            status_code=500, 
            detail="Grok API not configured. Please set XAI_API_KEY environment variable."
        )
    
    try:
        # Call Grok API to generate mitigation strategies
        grok_response = await grok_client.generate_mitigation_strategies(request)
        
        # Validate and structure the response
        response = MitigationResponse(**grok_response)
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing shipping risk: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)