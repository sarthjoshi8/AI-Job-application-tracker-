import logging
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status, Request
from pydantic import BaseModel

from app.core.security import get_current_user
from app.services.importer import import_postings_for_user, import_drafts_for_user, extract_text_from_file

router = APIRouter(prefix="/import", tags=["Bulk Ingestion"])
logger = logging.getLogger(__name__)

@router.post("/postings")
async def import_postings(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Imports postings from CSV, JSON, PDF, DOCX, TXT or image uploads.
    """
    uid = current_user["uid"]
    content_type = request.headers.get("content-type", "")

    if "multipart/form-data" in content_type:
        form = await request.form()
        file = form.get("file")
        if not file:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file provided in form")
        raw_bytes = await file.read()
        filename = getattr(file, "filename", "upload.txt")
        raw_content = extract_text_from_file(raw_bytes, filename)
        fmt = "json" if filename.endswith(".json") else "doc"
    else:
        body = await request.body()
        raw_content = body.decode("utf-8", errors="ignore")
        fmt = "json" if "application/json" in content_type else "csv"
        filename = "raw.txt"

    report = await import_postings_for_user(uid, raw_content, content_type=fmt, filename=filename)
    return report

@router.post("/drafts")
async def import_drafts(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Imports drafts or resumes from CSV, JSON, PDF, DOCX, TXT or image uploads.
    """
    uid = current_user["uid"]
    content_type = request.headers.get("content-type", "")

    if "multipart/form-data" in content_type:
        form = await request.form()
        file = form.get("file")
        if not file:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file provided in form")
        raw_bytes = await file.read()
        filename = getattr(file, "filename", "upload.txt")
        raw_content = extract_text_from_file(raw_bytes, filename)
        fmt = "json" if filename.endswith(".json") else "doc"
    else:
        body = await request.body()
        raw_content = body.decode("utf-8", errors="ignore")
        fmt = "json" if "application/json" in content_type else "csv"
        filename = "raw.txt"

    report = await import_drafts_for_user(uid, raw_content, content_type=fmt, filename=filename)
    return report
