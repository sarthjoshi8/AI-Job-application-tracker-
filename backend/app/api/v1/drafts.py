import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from google.cloud import firestore

from app.core.config import settings
from app.core.security import get_current_user
from app.services.firestore_client import get_firestore_client
from app.services.gemini_prompts import build_cover_letter_prompt, build_follow_up_prompt
from app.services.gemini_service import check_rate_limit, generate_draft_with_gemini

router = APIRouter(prefix="/applications/{app_id}/drafts", tags=["Drafts"])
logger = logging.getLogger(__name__)

class GenerateDraftRequest(BaseModel):
    type: str = Field(..., description="Draft type: 'cover_letter' or 'follow_up_email'")

class UpdateDraftRequest(BaseModel):
    contents: Optional[str] = None
    status: Optional[str] = None # 'draft', 'sent', 'archived'

@router.get("", response_model=List[Dict[str, Any]])
async def list_drafts(
    app_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Lists all drafts for a given application.
    """
    uid = current_user["uid"]
    db = get_firestore_client()
    drafts_ref = db.collection("users").document(uid).collection("applications").document(app_id).collection("drafts")

    results = []
    for doc in drafts_ref.stream():
        data = doc.to_dict()
        data["id"] = doc.id
        results.append(data)

    results.sort(key=lambda x: x.get("createdAt", ""), reverse=True)
    return results

@router.post("/generate", status_code=status.HTTP_201_CREATED)
async def generate_draft(
    app_id: str,
    payload: GenerateDraftRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Assembles rich context (app, profile, prior cover letters, last 3 drafts for voice)
    and calls Gemini to generate a tailored cover letter or follow-up email.
    """
    uid = current_user["uid"]
    
    # 1. Enforce rate limiting
    if not check_rate_limit(uid):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Maximum 10 generation requests per minute."
        )

    db = get_firestore_client()
    user_ref = db.collection("users").document(uid)
    app_ref = user_ref.collection("applications").document(app_id)

    app_doc = app_ref.get()
    if not app_doc.exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    app_data = app_doc.to_dict()
    user_doc = user_ref.get()
    user_profile = user_doc.to_dict() if user_doc.exists else {}

    # 2. Query last 3 drafts of the same type across all user's applications for tone/voice matching
    past_drafts = []
    try:
        drafts_group = db.collection_group("drafts")
        # In a real Firestore setup with collection groups or per-user query:
        # We query the user's applications collection directly to keep it tightly scoped
        for other_app in user_ref.collection("applications").limit(10).stream():
            for d in other_app.reference.collection("drafts").where(
                filter=firestore.FieldFilter("type", "==", payload.type)
            ).order_by("createdAt", direction=firestore.Query.DESCENDING).limit(3).stream():
                past_drafts.append(d.to_dict())
                if len(past_drafts) >= 3:
                    break
            if len(past_drafts) >= 3:
                break
    except Exception as e:
        logger.warning(f"Could not fetch past drafts for tone reference: {e}")

    # 3. Assemble prompt
    now_iso = datetime.now(timezone.utc).isoformat()
    company = app_data.get("company", "Target Company")
    role = app_data.get("role", "Target Role")
    job_description = app_data.get("jobDescription", "")

    if payload.type == "cover_letter":
        prompt = build_cover_letter_prompt(
            company=company,
            role=role,
            job_description=job_description,
            user_profile=user_profile,
            past_drafts=past_drafts
        )
    elif payload.type == "follow_up_email":
        # Find prior cover letter for the same application if available
        prior_cover_letter = None
        cover_letter_query = app_ref.collection("drafts").where(
            filter=firestore.FieldFilter("type", "==", "cover_letter")
        ).limit(1)
        for cl_doc in cover_letter_query.stream():
            prior_cover_letter = cl_doc.to_dict().get("contents")
            break

        # Calculate days elapsed
        app_date_str = app_data.get("applicationDate")
        days_elapsed = 7
        if app_date_str:
            try:
                app_date = datetime.fromisoformat(app_date_str.split("T")[0])
                days_elapsed = max(1, (datetime.now(timezone.utc).date() - app_date.date()).days)
            except Exception:
                days_elapsed = 7

        prompt = build_follow_up_prompt(
            company=company,
            role=role,
            job_description=job_description,
            days_elapsed=days_elapsed,
            user_profile=user_profile,
            prior_cover_letter=prior_cover_letter,
            past_drafts=past_drafts
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported draft type: {payload.type}"
        )

    # 4. Generate with Gemini & handle failures
    draft_ref = app_ref.collection("drafts").document()
    try:
        generated_text = await generate_draft_with_gemini(uid=uid, prompt=prompt)
        draft_doc = {
            "type": payload.type,
            "contents": generated_text,
            "status": "draft",
            "generatedBy": "ai",
            "generationModel": settings.GEMINI_MODEL,
            "createdAt": now_iso,
            "updatedAt": now_iso
        }
        draft_ref.set(draft_doc)
        draft_doc["id"] = draft_ref.id
        return draft_doc
    except Exception as e:
        logger.error(f"Gemini generation error: {e}")
        # Persist failed record
        failed_doc = {
            "type": payload.type,
            "contents": "",
            "status": "generation_failed",
            "generatedBy": "ai",
            "generationModel": settings.GEMINI_MODEL,
            "error": str(e),
            "createdAt": now_iso,
            "updatedAt": now_iso
        }
        draft_ref.set(failed_doc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI draft generation failed: {str(e)}"
        )

@router.patch("/{draft_id}")
async def update_draft(
    app_id: str,
    draft_id: str,
    payload: UpdateDraftRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Updates draft content or status (e.g. marking as sent or archived).
    """
    uid = current_user["uid"]
    db = get_firestore_client()
    draft_ref = db.collection("users").document(uid).collection("applications").document(app_id).collection("drafts").document(draft_id)

    doc = draft_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Draft not found")

    updates = {"updatedAt": datetime.now(timezone.utc).isoformat()}
    if payload.contents is not None:
        updates["contents"] = payload.contents
    if payload.status is not None:
        updates["status"] = payload.status

    draft_ref.update(updates)
    updated = draft_ref.get().to_dict()
    updated["id"] = draft_id
    return updated
