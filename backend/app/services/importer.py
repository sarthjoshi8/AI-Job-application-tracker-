import csv
import io
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple
from google.cloud import firestore
from app.services.firestore_client import get_firestore_client

logger = logging.getLogger(__name__)

# Max operations allowed per Firestore batch
MAX_BATCH_OPS = 500
# Maximum number of new companies to add per import execution
MAX_COMPANIES_PER_IMPORT = 10

def extract_text_from_file(raw_bytes: bytes, filename: str) -> str:
    """
    Extracts text from PDF, DOCX, CSV, JSON, TXT or image formats.
    """
    fn_lower = filename.lower()

    # 1. PDF extraction
    if fn_lower.endswith('.pdf'):
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(raw_bytes))
            text = ""
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return raw_bytes.decode('utf-8', errors='ignore')

    # 2. DOCX extraction
    elif fn_lower.endswith('.docx') or fn_lower.endswith('.doc'):
        try:
            import docx
            doc = docx.Document(io.BytesIO(raw_bytes))
            text = "\n".join([para.text for para in doc.paragraphs])
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {e}")
            return raw_bytes.decode('utf-8', errors='ignore')

    # 3. Plain text / CSV / JSON
    else:
        return raw_bytes.decode('utf-8', errors='ignore')

def parse_postings_stream(content: str, content_type: str = "csv", filename: str = "") -> List[Dict[str, Any]]:
    """
    Parses postings from CSV, JSON, or unstructured PDF/DOC/image text.
    """
    rows = []
    trimmed = content.strip()

    # Check if JSON format
    if "json" in content_type.lower() or trimmed.startswith("["):
        try:
            data = json.loads(content)
            for item in data:
                rows.append({
                    "externalId": str(item.get("id") or item.get("externalId") or ""),
                    "company": item.get("company") or item.get("to") or item.get("from") or "Target Tech Corp",
                    "role": item.get("role") or item.get("type") or "AI / Software Engineer",
                    "applicationDate": item.get("applicationDate") or item.get("date") or datetime.now(timezone.utc).date().isoformat(),
                    "jobDescription": item.get("jobDescription") or item.get("description") or "",
                    "status": item.get("status", "applied")
                })
            return rows
        except Exception:
            pass

    # Check if CSV format
    if "," in trimmed.split("\n")[0]:
        try:
            reader = csv.DictReader(io.StringIO(trimmed))
            for row in reader:
                ext_id = row.get("id") or row.get("externalId") or ""
                company = row.get("company") or row.get("to") or row.get("from") or "Target Tech Corp"
                role = row.get("role") or row.get("type") or "AI / Software Engineer"
                app_date = row.get("applicationDate") or row.get("date") or datetime.now(timezone.utc).date().isoformat()
                desc = row.get("jobDescription") or row.get("description") or ""
                status = row.get("status") or "applied"

                rows.append({
                    "externalId": str(ext_id),
                    "company": company,
                    "role": role,
                    "applicationDate": app_date,
                    "jobDescription": desc,
                    "status": status
                })
            if rows:
                return rows
        except Exception:
            pass

    # Unstructured text from PDF / DOCX / Image / TXT job descriptions:
    lines = [line.strip() for line in trimmed.split("\n") if line.strip()]
    first_line = lines[0] if lines else "Target Company Job Posting"
    
    # Try to derive company name and role
    company = "Target AI Company"
    role = "AI / Systems Engineer"
    
    if " at " in first_line:
        parts = first_line.split(" at ")
        role = parts[0][:60]
        company = parts[1][:60]
    elif " - " in first_line:
        parts = first_line.split(" - ")
        company = parts[0][:60]
        role = parts[1][:60]

    rows.append({
        "externalId": f"doc-{int(datetime.now(timezone.utc).timestamp())}",
        "company": company,
        "role": role,
        "applicationDate": datetime.now(timezone.utc).date().isoformat(),
        "jobDescription": content[:3000],
        "status": "applied"
    })

    return rows

def parse_drafts_stream(content: str, content_type: str = "csv", filename: str = "") -> List[Dict[str, Any]]:
    """
    Parses drafts from CSV, JSON, or unstructured PDF/DOC/image cover letters.
    """
    rows = []
    trimmed = content.strip()

    if "json" in content_type.lower() or trimmed.startswith("["):
        try:
            data = json.loads(content)
            for item in data:
                rows.append({
                    "externalId": str(item.get("id") or ""),
                    "jobId": str(item.get("jobId") or item.get("applicationId") or ""),
                    "type": item.get("type") or "cover_letter",
                    "contents": item.get("contents") or item.get("content") or "",
                    "status": item.get("status") or "draft",
                    "generatedBy": item.get("generatedBy") or "human",
                    "generationModel": item.get("generationModel") or "manual"
                })
            return rows
        except Exception:
            pass

    if "," in trimmed.split("\n")[0]:
        try:
            reader = csv.DictReader(io.StringIO(trimmed))
            for row in reader:
                ext_id = row.get("id") or ""
                job_id = row.get("jobId") or row.get("applicationId") or ""
                draft_type = row.get("type") or "cover_letter"
                contents = row.get("contents") or row.get("content") or ""
                status = row.get("status") or "draft"

                rows.append({
                    "externalId": str(ext_id),
                    "jobId": str(job_id),
                    "type": draft_type,
                    "contents": contents,
                    "status": status,
                    "generatedBy": row.get("generatedBy") or "human",
                    "generationModel": row.get("generationModel") or "manual"
                })
            if rows:
                return rows
        except Exception:
            pass

    # Unstructured document (e.g. uploaded Resume or Cover Letter PDF/DOCX)
    rows.append({
        "externalId": f"doc-draft-{int(datetime.now(timezone.utc).timestamp())}",
        "jobId": "",
        "type": "cover_letter",
        "contents": content,
        "status": "draft",
        "generatedBy": "human",
        "generationModel": "document_upload"
    })

    return rows

async def import_postings_for_user(
    uid: str,
    raw_content: str,
    content_type: str = "csv",
    filename: str = ""
) -> Dict[str, Any]:
    """
    Batch-imports job postings into users/{uid}/applications/{appId}.
    """
    db = get_firestore_client()
    rows = parse_postings_stream(raw_content, content_type, filename)
    
    rows_received = len(rows)
    rows_created = 0
    rows_updated = 0
    rows_flagged = 0
    errors = []

    apps_ref = db.collection("users").document(uid).collection("applications")
    existing_by_ext_id = {}
    for doc in apps_ref.stream():
        data = doc.to_dict()
        if data.get("externalId"):
            existing_by_ext_id[str(data["externalId"])] = doc.id

    now_iso = datetime.now(timezone.utc).isoformat()
    batches = []
    current_batch = db.batch()
    current_batch_ops = 0

    companies_added = 0
    for row in rows:
        try:
            ext_id = row.get("externalId", "")
            if ext_id and ext_id in existing_by_ext_id:
                # Existing application — always update regardless of limit
                app_id = existing_by_ext_id[ext_id]
                doc_ref = apps_ref.document(app_id)
                current_batch.update(doc_ref, {
                    "company": row["company"],
                    "role": row["role"],
                    "jobDescription": row["jobDescription"],
                    "updatedAt": now_iso
                })
                rows_updated += 1
            elif companies_added < MAX_COMPANIES_PER_IMPORT:
                # New company — only add if under the per-import limit
                doc_ref = apps_ref.document()
                new_app = {
                    "company": row["company"],
                    "role": row["role"],
                    "jobDescription": row["jobDescription"],
                    "applicationDate": row["applicationDate"],
                    "status": row["status"],
                    "statusHistory": [{"status": row["status"], "changedAt": now_iso}],
                    "externalId": ext_id or doc_ref.id,
                    "nextNudgeAt": None,
                    "createdAt": now_iso,
                    "updatedAt": now_iso
                }
                current_batch.set(doc_ref, new_app)
                if ext_id:
                    existing_by_ext_id[ext_id] = doc_ref.id
                rows_created += 1
                companies_added += 1
            else:
                # Limit reached — skip new companies silently
                continue

            current_batch_ops += 1
            if current_batch_ops >= MAX_BATCH_OPS:
                batches.append(current_batch)
                current_batch = db.batch()
                current_batch_ops = 0
        except Exception as e:
            rows_flagged += 1
            errors.append(f"Row error ({row.get('company')}): {str(e)}")

    if current_batch_ops > 0:
        batches.append(current_batch)

    for b in batches:
        b.commit()

    return {
        "rows_received": rows_received,
        "rows_created": rows_created,
        "rows_updated": rows_updated,
        "rows_flagged": rows_flagged,
        "errors": errors
    }

async def import_drafts_for_user(
    uid: str,
    raw_content: str,
    content_type: str = "csv",
    filename: str = ""
) -> Dict[str, Any]:
    """
    Batch-imports drafts into users/{uid}/applications/{appId}/drafts/{draftId}.
    """
    db = get_firestore_client()
    rows = parse_drafts_stream(raw_content, content_type, filename)
    
    rows_received = len(rows)
    rows_created = 0
    rows_updated = 0
    rows_flagged = 0
    errors = []

    apps_ref = db.collection("users").document(uid).collection("applications")
    app_id_map = {}
    for doc in apps_ref.stream():
        data = doc.to_dict()
        app_id_map[doc.id] = doc.id
        if data.get("externalId"):
            app_id_map[str(data["externalId"])] = doc.id

    now_iso = datetime.now(timezone.utc).isoformat()
    batches = []
    current_batch = db.batch()
    current_batch_ops = 0

    for row in rows:
        try:
            job_id = row.get("jobId")
            target_app_id = None

            if job_id and job_id in app_id_map:
                target_app_id = app_id_map[job_id]
            else:
                stub_ref = apps_ref.document()
                stub_data = {
                    "company": "Uploaded Candidate Document",
                    "role": "Software / AI Professional",
                    "jobDescription": "Extracted from uploaded resume / document artifact.",
                    "applicationDate": datetime.now(timezone.utc).date().isoformat(),
                    "status": "applied",
                    "statusHistory": [{"status": "applied", "changedAt": now_iso}],
                    "externalId": job_id or stub_ref.id,
                    "nextNudgeAt": None,
                    "createdAt": now_iso,
                    "updatedAt": now_iso
                }
                current_batch.set(stub_ref, stub_data)
                current_batch_ops += 1
                target_app_id = stub_ref.id
                if job_id:
                    app_id_map[job_id] = target_app_id

            draft_ref = apps_ref.document(target_app_id).collection("drafts").document()
            draft_data = {
                "type": row.get("type", "cover_letter"),
                "contents": row.get("contents", ""),
                "status": row.get("status", "draft"),
                "generatedBy": row.get("generatedBy", "human"),
                "generationModel": row.get("generationModel", "manual"),
                "externalId": row.get("externalId", draft_ref.id),
                "createdAt": now_iso,
                "updatedAt": now_iso
            }
            current_batch.set(draft_ref, draft_data)
            current_batch_ops += 1
            rows_created += 1

            if current_batch_ops >= MAX_BATCH_OPS - 2:
                batches.append(current_batch)
                current_batch = db.batch()
                current_batch_ops = 0
        except Exception as e:
            rows_flagged += 1
            errors.append(f"Draft row error: {str(e)}")

    if current_batch_ops > 0:
        batches.append(current_batch)

    for b in batches:
        b.commit()

    return {
        "rows_received": rows_received,
        "rows_created": rows_created,
        "rows_updated": rows_updated,
        "rows_flagged": rows_flagged,
        "errors": errors
    }
