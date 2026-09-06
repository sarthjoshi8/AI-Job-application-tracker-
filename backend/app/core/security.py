import logging
from typing import Optional
from fastapi import Header, HTTPException, status
import firebase_admin
from firebase_admin import auth, credentials
from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
try:
    if not firebase_admin._apps:
        # If in Cloud Run or with ADC, default credentials will be used
        firebase_admin.initialize_app()
except Exception as e:
    logger.warning(f"Firebase Admin SDK initialization warning: {e}")

async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """
    Verifies Firebase Auth ID token from the Bearer Authorization header.
    Returns decoded token dictionary containing 'uid', 'email', etc.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header. Expected Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.split("Bearer ")[1].strip()

    # Special handler for local testing/mock mode if enabled
    if settings.MOCK_MODE and token.startswith("mock-user-"):
        uid = token.replace("mock-user-", "")
        return {"uid": uid, "email": f"{uid}@example.com", "name": f"User {uid}"}

    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired authentication token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
