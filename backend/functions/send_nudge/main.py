import base64
import json
import logging
import os
from datetime import datetime, timezone
import functions_framework
from google.cloud import firestore, secretmanager
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_secret(secret_id: str, project_id: str, default: str = "") -> str:
    env_val = os.getenv(secret_id.upper().replace("-", "_"))
    if env_val:
        return env_val
    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        logger.warning(f"Could not load secret {secret_id}: {e}")
        return default

def send_email_notification(to_email: str, subject: str, message: str, sendgrid_key: str):
    """
    Sends email via SendGrid API if key is available, or logs for in-app delivery.
    """
    if not sendgrid_key or not to_email:
        logger.info(f"[In-App Only Nudge] To: {to_email} | Subject: {subject}")
        return True

    url = "https://api.sendgrid.com/v3/mail/send"
    headers = {
        "Authorization": f"Bearer {sendgrid_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "personalizations": [{"to": [{"email": to_email}]}],
        "from": {"email": "no-reply@jobtracker.app", "name": "AI Job Application Tracker"},
        "subject": subject,
        "content": [{"type": "text/plain", "value": message}]
    }
    try:
        res = requests.post(url, json=payload, headers=headers, timeout=10)
        return res.status_code in [200, 202]
    except Exception as e:
        logger.error(f"SendGrid delivery error: {e}")
        return False

@functions_framework.cloud_event
def send_nudge(cloud_event):
    """
    Pub/Sub event consumer Cloud Function (2nd gen).
    Idempotent: Uses appId_YYYY-MM-DD deduplication document key.
    """
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "job-tracker-prod")
    sendgrid_key = get_secret("sendgrid-api-key", project_id)
    
    # 1. Parse Pub/Sub message
    try:
        pubsub_data = cloud_event.data["message"]["data"]
        payload_str = base64.b64decode(pubsub_data).decode("utf-8")
        payload = json.loads(payload_str)
    except Exception as e:
        logger.error(f"Invalid Pub/Sub message payload: {e}")
        return

    uid = payload.get("uid")
    app_id = payload.get("applicationId")
    company = payload.get("company", "Company")
    role = payload.get("role", "Role")
    days_stale = payload.get("daysStale", 5)

    if not uid or not app_id:
        logger.error(f"Missing required fields in payload: {payload}")
        return

    db = firestore.Client(project=project_id)
    now = datetime.now(timezone.utc)
    today_str = now.strftime("%Y-%m-%d")
    
    # 2. Idempotency Check: Deterministic document ID prevents duplicate sends on Pub/Sub retries
    nudge_doc_id = f"{app_id}_{today_str}"
    nudge_ref = db.collection("users").document(uid).collection("nudges").document(nudge_doc_id)

    if nudge_ref.get().exists:
        logger.info(f"Nudge {nudge_doc_id} already processed for app {app_id}. Skipping duplicate send.")
        return

    # 3. Retrieve user email
    user_doc = db.collection("users").document(uid).get()
    user_data = user_doc.to_dict() if user_doc.exists else {}
    user_email = user_data.get("email")

    subject = f"Time to follow up on your {company} ({role}) application!"
    message = f"Hi! It has been {days_stale} days since any activity on your {role} application at {company}. Log in to generate a tailored follow-up email in one click!"

    # 4. Attempt delivery
    email_sent = send_email_notification(user_email, subject, message, sendgrid_key)

    # 5. Write nudge doc
    nudge_ref.set({
        "applicationId": app_id,
        "company": company,
        "role": role,
        "scheduledFor": now.isoformat(),
        "status": "pending",
        "message": message,
        "deliveredViaEmail": email_sent,
        "sentAt": now.isoformat(),
        "createdAt": now.isoformat()
    })

    logger.info(f"Successfully processed and recorded nudge {nudge_doc_id} for user {uid}.")
