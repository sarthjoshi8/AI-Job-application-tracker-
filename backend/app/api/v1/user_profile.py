import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.security import get_current_user
from app.services.firestore_client import get_firestore_client

router = APIRouter(prefix="/user", tags=["User Profile & Settings"])
logger = logging.getLogger(__name__)

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    resumeSummary: Optional[str] = None
    keySkills: Optional[List[str]] = None
    nudgeCadenceDays: Optional[int] = None

@router.get("/profile")
async def get_user_profile(
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieves the user's profile and settings document.
    """
    uid = current_user["uid"]
    db = get_firestore_client()
    doc_ref = db.collection("users").document(uid)
    doc = doc_ref.get()

    if not doc.exists:
        # Create default profile doc
        default_profile = {
            "name": current_user.get("name", "Job Seeker"),
            "email": current_user.get("email", ""),
            "resumeSummary": "Experienced Software Engineer with a passion for building resilient, scalable systems.",
            "keySkills": ["Python", "FastAPI", "React", "TypeScript", "Google Cloud", "Firestore"],
            "nudgeCadenceDays": 5,
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "updatedAt": datetime.now(timezone.utc).isoformat()
        }
        doc_ref.set(default_profile)
        default_profile["uid"] = uid
        return default_profile

    data = doc.to_dict()
    data["uid"] = uid
    return data

@router.put("/profile")
async def update_user_profile(
    payload: ProfileUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Updates the user's profile, resume context, key skills, or nudge cadence.
    """
    uid = current_user["uid"]
    db = get_firestore_client()
    doc_ref = db.collection("users").document(uid)

    updates = {"updatedAt": datetime.now(timezone.utc).isoformat()}
    if payload.name is not None:
        updates["name"] = payload.name
    if payload.resumeSummary is not None:
        updates["resumeSummary"] = payload.resumeSummary
    if payload.keySkills is not None:
        updates["keySkills"] = payload.keySkills
    if payload.nudgeCadenceDays is not None:
        updates["nudgeCadenceDays"] = payload.nudgeCadenceDays

    doc_ref.set(updates, merge=True)
    data = doc_ref.get().to_dict()
    data["uid"] = uid
    return data
