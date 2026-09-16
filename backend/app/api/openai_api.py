"""
FastAPI Router for OpenAI Integration
Provides:
- GET /api/openai/status: Safe configuration and readiness inspection (never reveals API keys)
- GET /api/openai/health: Health check reporting configured status
- POST /api/openai/test: Server-side test completion to verify connectivity and credential validity
"""

import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter
from pydantic import BaseModel, Field
from ..services.openai_service import openai_service

logger = logging.getLogger("openai_api")

router = APIRouter(tags=["OpenAI"])


class OpenAITestRequest(BaseModel):
    prompt: Optional[str] = Field("Hello, this is a test from AI Call Agent. Reply with a short greeting.", description="Prompt for test completion")


@router.get("/api/openai/status")
@router.get("/openai/status")
async def get_openai_status():
    """
    Safe backend health/configuration endpoint reporting:
    - configured: true/false
    - status: READY/NOT_CONFIGURED
    Never returns the actual API key.
    """
    is_valid, config_err = openai_service.validate_configuration()
    
    return {
        "configured": is_valid,
        "status": "READY" if is_valid else "NOT_CONFIGURED",
        "model": openai_service.model,
        "timeout_seconds": openai_service.timeout_seconds,
        "message": "OpenAI API service is configured and ready." if is_valid else config_err
    }


@router.get("/api/openai/health")
@router.get("/openai/health")
async def get_openai_health():
    """
    Lightweight health endpoint for OpenAI integration.
    """
    is_valid, _ = openai_service.validate_configuration()
    return {
        "configured": is_valid,
        "status": "READY" if is_valid else "NOT_CONFIGURED"
    }


@router.post("/api/openai/test")
@router.post("/openai/test")
async def test_openai_completion(payload: Optional[OpenAITestRequest] = None):
    """
    Tests server-side OpenAI connectivity.
    Does not expose keys, headers, or internal tokens.
    """
    is_valid, config_err = openai_service.validate_configuration()
    if not is_valid:
        return {
            "success": False,
            "configured": False,
            "status": "NOT_CONFIGURED",
            "message": config_err
        }

    test_prompt = payload.prompt if payload and payload.prompt else "Hello, please confirm you are connected."
    messages = [
        {"role": "system", "content": "You are a helpful assistant. Keep your response under 20 words."},
        {"role": "user", "content": test_prompt}
    ]

    result = await openai_service.chat_completion(
        messages=messages,
        max_tokens=60,
        temperature=0.2
    )

    if not result.get("success"):
        return {
            "success": False,
            "configured": True,
            "status": result.get("status", "FAILED"),
            "error": result.get("error", "OpenAI call failed.")
        }

    return {
        "success": True,
        "configured": True,
        "status": "READY",
        "model": result.get("model"),
        "response": result.get("content")
    }
