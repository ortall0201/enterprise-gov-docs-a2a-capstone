"""
A2A Protocol Server for Docs Translator VaaS.

This FastAPI server exposes the CrewAI Docs Translator agent via
Google ADK's A2A (Agent-to-Agent) protocol.

Based on Day 5a: Agent-to-Agent Communication from Kaggle AI Agents Intensive.

Endpoints:
- GET  /.well-known/agent-card.json  (Agent Card - "front door")
- POST /invoke                         (Non-streaming invocation)
- POST /stream                         (Streaming invocation with SSE)
- GET  /health                         (Health check)
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from agent_card import AGENT_CARD
from crew_agent import translate_document_crew
from transformers import a2a_to_crewai, crewai_to_a2a, validate_a2a_request

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Pydantic models for A2A protocol
class A2ARequest(BaseModel):
    """A2A protocol request format."""
    capability: str = Field(..., description="Capability name to invoke")
    parameters: Dict[str, Any] = Field(..., description="Parameters for the capability")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")


class A2AResponse(BaseModel):
    """A2A protocol response format."""
    status: str = Field(..., description="Request status: success or error")
    result: Optional[Dict[str, Any]] = Field(None, description="Result data")
    error: Optional[str] = Field(None, description="Error message if status is error")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Response metadata")


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown."""
    # Startup
    logger.info("🚀 Starting Docs Translator A2A VaaS Service")
    logger.info(f"   Service: {AGENT_CARD['name']} v{AGENT_CARD['version']}")
    logger.info(f"   Framework: CrewAI")
    logger.info(f"   Vendor: {AGENT_CARD['vendor']['name']}")
    logger.info(f"   Capabilities: {[cap['name'] for cap in AGENT_CARD['capabilities']]}")

    # Check required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        logger.warning("⚠️  OPENAI_API_KEY not set - translations will fail!")

    yield

    # Shutdown
    logger.info("🛑 Shutting down Docs Translator A2A service")


# Create FastAPI app
app = FastAPI(
    title="Docs Translator A2A Service",
    description="CrewAI-based document translation service exposed via A2A protocol",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware (for web-based ADK consumers)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# A2A Protocol Endpoints
# ============================================================================

@app.get("/.well-known/agent-card.json")
async def get_agent_card():
    """
    A2A Protocol: Agent Card endpoint.

    This is the "front door" for A2A - ADK RemoteA2aAgent reads this first
    to discover the agent's capabilities, parameters, and endpoints.

    Returns:
        Agent Card JSON
    """
    logger.info("📋 Agent Card requested")
    return JSONResponse(content=AGENT_CARD)


@app.post("/invoke", response_model=A2AResponse)
async def invoke(request: A2ARequest):
    """
    A2A Protocol: Non-streaming invocation endpoint.

    Executes the requested capability and returns the result synchronously.

    Args:
        request: A2A request with capability and parameters

    Returns:
        A2A response with result or error

    Raises:
        HTTPException: If request is invalid or execution fails
    """
    try:
        logger.info(f"📥 A2A invoke request: {request.capability}")

        # Validate request
        validate_a2a_request(request.capability, request.parameters)

        # Execute based on capability
        if request.capability == "translate_document":
            # Transform A2A parameters -> CrewAI inputs
            crew_inputs = a2a_to_crewai(request.parameters)

            # Execute CrewAI translation
            logger.info("🤖 Executing CrewAI translation...")
            crew_result = translate_document_crew(**crew_inputs)

            # Transform CrewAI result -> A2A response
            a2a_result = crewai_to_a2a(crew_result)

            logger.info("✅ Translation completed successfully")

            return A2AResponse(
                status="success",
                result=a2a_result,
                metadata={
                    "vendor": "Docs Translator",
                    "framework": "CrewAI",
                    "model": os.getenv("OPENAI_MODEL", "gpt-4o")
                }
            )

        else:
            # Unknown capability (should be caught by validation)
            raise HTTPException(
                status_code=400,
                detail=f"Unknown capability: {request.capability}"
            )

    except ValueError as e:
        logger.error(f"❌ Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"❌ Execution error: {e}", exc_info=True)
        return A2AResponse(
            status="error",
            error=str(e),
            metadata={"vendor": "Docs Translator"}
        )


@app.post("/stream")
async def stream(request: A2ARequest):
    """
    A2A Protocol: Streaming invocation endpoint.

    Executes the requested capability and streams results using
    Server-Sent Events (SSE).

    Args:
        request: A2A request with capability and parameters

    Returns:
        StreamingResponse with SSE events

    Event format:
        data: {"status": "processing"}
        data: {"status": "success", "result": {...}}
        data: {"status": "error", "error": "..."}
    """
    async def event_generator():
        """Generate SSE events for streaming response."""
        try:
            logger.info(f"📡 A2A stream request: {request.capability}")

            # Validate request
            validate_a2a_request(request.capability, request.parameters)

            # Send processing status
            yield f"data: {json.dumps({'status': 'processing', 'message': 'Starting translation...'})}\n\n"
            await asyncio.sleep(0.1)  # Small delay for client to connect

            # Execute translation
            if request.capability == "translate_document":
                crew_inputs = a2a_to_crewai(request.parameters)

                # Send progress update
                yield f"data: {json.dumps({'status': 'processing', 'message': 'Executing CrewAI agent...'})}\n\n"

                # Execute CrewAI (currently synchronous - would need async version for true streaming)
                crew_result = translate_document_crew(**crew_inputs)
                a2a_result = crewai_to_a2a(crew_result)

                # Send success with result
                yield f"data: {json.dumps({'status': 'success', 'result': a2a_result})}\n\n"

                logger.info("✅ Streaming translation completed")

            else:
                yield f"data: {json.dumps({'status': 'error', 'error': f'Unknown capability: {request.capability}'})}\n\n"

        except Exception as e:
            logger.error(f"❌ Streaming error: {e}", exc_info=True)
            yield f"data: {json.dumps({'status': 'error', 'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


# ============================================================================
# Utility Endpoints
# ============================================================================

@app.get("/health")
async def health():
    """
    Health check endpoint for deployment monitoring.

    Returns:
        Health status and service information
    """
    return {
        "status": "healthy",
        "service": "docs-translator-a2a",
        "version": "1.0.0",
        "framework": "CrewAI",
        "a2a_enabled": True,
        "openai_configured": bool(os.getenv("OPENAI_API_KEY"))
    }


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "Docs Translator A2A VaaS",
        "version": "1.0.0",
        "description": "CrewAI document translation service via A2A protocol",
        "agent_card": "/.well-known/agent-card.json",
        "endpoints": {
            "invoke": "/invoke",
            "stream": "/stream",
            "health": "/health"
        },
        "vendor": AGENT_CARD["vendor"]
    }


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    host = os.getenv("A2A_SERVICE_HOST", "0.0.0.0")
    port = int(os.getenv("A2A_SERVICE_PORT", "8001"))

    logger.info(f"🌐 Starting server on {host}:{port}")

    uvicorn.run(
        "a2a_server:app",
        host=host,
        port=port,
        reload=True,  # Enable auto-reload for development
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
