import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from google.cloud import firestore

from app.core.security import get_current_user
from app.services.firestore_client import get_firestore_client
from app.services.state_machine import apply_status_transition, InvalidStateTransitionError

router = APIRouter(prefix="/applications", tags=["Applications"])
logger = logging.getLogger(__name__)

class StatusUpdate(BaseModel):
    status: str = Field(..., description="Target status: applied, interview, offer, rejected")

class ApplicationCreate(BaseModel):
    company: str
    role: str
    jobDescription: str = ""
    applicationDate: Optional[str] = None
    status: str = "applied"

class ApplicationUpdate(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    jobDescription: Optional[str] = None
    applicationDate: Optional[str] = None

@router.get("", response_model=List[Dict[str, Any]])
async def list_applications(
    status_filter: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Lists all job applications for the authenticated user, optionally filtered by status.
    """
    uid = current_user["uid"]
    db = get_firestore_client()
    apps_ref = db.collection("users").document(uid).collection("applications")

    if status_filter:
        query = apps_ref.where(filter=firestore.FieldFilter("status", "==", status_filter))
    else:
        query = apps_ref

    results = []
    for doc in query.stream():
        data = doc.to_dict()
        data["id"] = doc.id
        results.append(data)

    # Sort in memory by createdAt ascending (first-come basis)
    results.sort(key=lambda x: x.get("createdAt", x.get("updatedAt", "")), reverse=False)
    return results

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_application(
    payload: ApplicationCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Creates a new job application record for the authenticated user.
    """
    uid = current_user["uid"]
    db = get_firestore_client()
    apps_ref = db.collection("users").document(uid).collection("applications")

    now_iso = datetime.now(timezone.utc).isoformat()
    app_date = payload.applicationDate or datetime.now(timezone.utc).date().isoformat()

    doc_ref = apps_ref.document()
    app_data = {
        "company": payload.company,
        "role": payload.role,
        "jobDescription": payload.jobDescription,
        "applicationDate": app_date,
        "status": payload.status,
        "statusHistory": [{"status": payload.status, "changedAt": now_iso}],
        "nextNudgeAt": None,
        "createdAt": now_iso,
        "updatedAt": now_iso
    }
    doc_ref.set(app_data)
    app_data["id"] = doc_ref.id
    return app_data

@router.get("/{app_id}")
async def get_application(
    app_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieves a single application by ID for the authenticated user.
    """
    uid = current_user["uid"]
    db = get_firestore_client()
    doc_ref = db.collection("users").document(uid).collection("applications").document(app_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    data = doc.to_dict()
    data["id"] = doc.id
    return data

@router.patch("/{app_id}/status")
async def update_application_status(
    app_id: str,
    payload: StatusUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Validates and updates the state of an application according to the state machine.
    Rejects illegal jumps with HTTP 409 Conflict.
    """
    uid = current_user["uid"]
    db = get_firestore_client()
    user_ref = db.collection("users").document(uid)
    app_ref = user_ref.collection("applications").document(app_id)
    doc = app_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    app_data = doc.to_dict()
    try:
        updates, side_effects = apply_status_transition(app_ref, app_data, payload.status, user_ref)
    except InvalidStateTransitionError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    # Apply application updates
    app_ref.update(updates)

    # Process side effects (such as cancelling or scheduling nudges)
    for effect in side_effects:
        if effect["action"] == "cancel_pending_nudges":
            nudges_query = user_ref.collection("nudges").where(
                filter=firestore.FieldFilter("applicationId", "==", app_id)
            ).where(
                filter=firestore.FieldFilter("status", "==", "pending")
            )
            for n_doc in nudges_query.stream():
                n_doc.reference.update({"status": "cancelled"})

        elif effect["action"] == "create_nudge":
            nudge_ref = user_ref.collection("nudges").document()
            nudge_ref.set({
                "applicationId": app_id,
                "scheduledFor": effect["scheduledFor"],
                "status": "pending",
                "message": effect["message"],
                "createdAt": datetime.now(timezone.utc).isoformat(),
                "sentAt": None
            })

    updated_doc = app_ref.get().to_dict()
    updated_doc["id"] = app_id
    return updated_doc

@router.delete("/{app_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application(
    app_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Deletes an application and its subcollections for the authenticated user.
    """
    uid = current_user["uid"]
    db = get_firestore_client()
    app_ref = db.collection("users").document(uid).collection("applications").document(app_id)

    if not app_ref.get().exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    # Delete drafts
    for draft in app_ref.collection("drafts").stream():
        draft.reference.delete()

    app_ref.delete()
    return None
