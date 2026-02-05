from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import uvicorn
from datetime import datetime

from honeypot_agent import HoneypotAgent
from config import HONEYPOT_API_KEY

app = FastAPI(
    title="Agentic Honeypot API",
    description="AI-powered scam detection and intelligence extraction system",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the honeypot agent
agent = HoneypotAgent()

# Request/Response Models
class ScamAnalysisRequest(BaseModel):
    message: str = Field(..., description="The message to analyze for scam content")
    conversation_id: Optional[str] = Field(None, description="Unique ID to track conversation thread")

class ScamAnalysisResponse(BaseModel):
    status: str
    timestamp: str
    is_scam: bool
    confidence: float
    scam_type: str
    ai_response: str
    persona_used: Optional[str]
    extracted_intelligence: dict
    reasoning: str
    conversation_turn: int
    total_intelligence_collected: dict

# Endpoints
@app.get("/")
def root():
    """API status and information"""
    return {
        "service": "Agentic Honeypot API",
        "status": "operational",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "test": "/test",
            "analyze": "/api/honeypot/analyze",
            "docs": "/docs"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "honeypot-api"
    }

@app.api_route("/test", methods=["GET", "POST"])
async def test_authentication(request: Request, x_api_key: str = Header(None, alias="x-api-key")):
    """
    Test endpoint for validation - supports both GET and POST
    Verifies API authentication and endpoint availability
    """
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing API key. Include 'x-api-key' in headers."
        )
    
    if x_api_key != HONEYPOT_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    
    return {
        "status": "success",
        "message": "Honeypot endpoint is reachable and authenticated",
        "authenticated": True,
        "timestamp": datetime.utcnow().isoformat(),
        "method": request.method
    }

@app.post("/api/honeypot/analyze", response_model=ScamAnalysisResponse)
def analyze_scam_message(
    request: ScamAnalysisRequest,
    x_api_key: str = Header(None, alias="x-api-key")
):
    """
    Main honeypot endpoint
    
    Analyzes incoming messages for scam content and generates
    believable responses to engage scammers and extract intelligence.
    """
    # Authenticate
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing API key. Include 'x-api-key' in headers."
        )
    
    if x_api_key != HONEYPOT_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    
    # Validate input
    if not request.message or len(request.message.strip()) == 0:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty"
        )
    
    try:
        # Analyze the message
        result = agent.analyze_message(
            message=request.message,
            conversation_id=request.conversation_id
        )
        
        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            **result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )

@app.get("/api/conversation/{conversation_id}")
def get_conversation_history(
    conversation_id: str,
    x_api_key: str = Header(None, alias="x-api-key")
):
    """
    Retrieve conversation history and aggregated intelligence
    """
    if not x_api_key or x_api_key != HONEYPOT_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    history = agent.conversation_history.get(conversation_id, [])
    
    if not history:
        raise HTTPException(
            status_code=404,
            detail=f"No conversation found with ID: {conversation_id}"
        )
    
    return {
        "conversation_id": conversation_id,
        "total_turns": len(history),
        "history": history,
        "aggregated_intelligence": agent._aggregate_intelligence(conversation_id)
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
