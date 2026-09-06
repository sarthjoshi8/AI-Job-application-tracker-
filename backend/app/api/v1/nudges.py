import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from google.cloud import firestore

from app.core.security import get_current_user
from app.services.firestore_client import get_firestore_client

router = APIRouter(prefix="/nudges", tags=["Nudges"])
logger = logging.getLogger(__name__)

class NudgeStatusUpdate(BaseModel):
    status: str # 'pending', 'read', 'sent', 'cancelled'

@router.get("", response_model=List[Dict[str, Any]])
async def list_nudges(
    status: Optional[str] = "pending",
    current_user: dict = Depends(get_current_user)
):
    """
    Returns nudges/notifications for the authenticated user.
    """
    uid = current_user["uid"]
    db = get_firestore_client()
    nudges_ref = db.collection("users").document(uid).collection("nudges")

    if status and status != "all":
        query = nudges_ref.where(filter=firestore.FieldFilter("status", "==", status))
    else:
        query = nudges_ref

    results = []
    for doc in query.stream():
        data = doc.to_dict()
        data["id"] = doc.id
        results.append(data)

    results.sort(key=lambda x: x.get("createdAt", x.get("scheduledFor", "")), reverse=True)
    return results

@router.post("/mark-all-read")
async def mark_all_nudges_read(
    current_user: dict = Depends(get_current_user)
):
    """
    Marks all pending notifications/nudges as read for the authenticated user.
    """
    uid = current_user["uid"]
    db = get_firestore_client()
    nudges_ref = db.collection("users").document(uid).collection("nudges")

    pending_query = nudges_ref.where(filter=firestore.FieldFilter("status", "==", "pending"))
    count = 0
    for doc in pending_query.stream():
        doc.reference.update({
            "status": "read",
            "readAt": datetime.now(timezone.utc).isoformat()
        })
        count += 1

    return {"status": "success", "marked_read_count": count}

@router.patch("/{nudge_id}")
async def update_nudge_status(
    nudge_id: str,
    payload: NudgeStatusUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Updates the status of a specific nudge (e.g. mark read, sent, cancelled).
    """
    uid = current_user["uid"]
    db = get_firestore_client()
    nudge_ref = db.collection("users").document(uid).collection("nudges").document(nudge_id)

    doc = nudge_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nudge not found")

    updates = {
        "status": payload.status,
        "updatedAt": datetime.now(timezone.utc).isoformat()
    }
    if payload.status == "sent":
        updates["sentAt"] = datetime.now(timezone.utc).isoformat()
    elif payload.status == "read":
        updates["readAt"] = datetime.now(timezone.utc).isoformat()

    nudge_ref.update(updates)
    data = nudge_ref.get().to_dict()
    data["id"] = nudge_id
    return data
