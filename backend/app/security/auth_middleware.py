"""
Authentication & Security Middleware
Validates Firebase Authentication JWT tokens and enforces tenant isolation.
"""

from fastapi import Header, HTTPException, status, Depends
from typing import Optional, Dict, Any
from app.firebase.firebase_service import firebase_manager

async def get_current_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """
    Extracts and verifies Firebase ID token from Authorization header.
    In Demo Mode, transparently validates demo tokens.
    """
    if not authorization:
        # Check if Demo Mode allows fallback user
        if firebase_manager.demo_mode:
            return {
                "uid": "user_demo_manish_123",
                "email": "manish@aicallagent.com",
                "name": "Manish Kumar"
            }
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization scheme. Bearer token required."
        )

    token = parts[1]
    decoded = await firebase_manager.verify_id_token(token)
    if not decoded:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token"
        )

    return decoded
