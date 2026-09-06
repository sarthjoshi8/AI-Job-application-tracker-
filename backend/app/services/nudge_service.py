import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List
from google.cloud import pubsub_v1
from app.core.config import settings
from app.services.firestore_client import get_firestore_client

logger = logging.getLogger(__name__)

def check_stale_applications_and_publish() -> Dict[str, Any]:
    """
    Finds 'applied' applications across all users where status hasn't changed
    for >= nudgeCadenceDays (default 5) and has no pending nudge, then publishes
    messages to Pub/Sub topic 'nudge-events'.
    """
    db = get_firestore_client()
    now = datetime.now(timezone.utc)
    
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(settings.PROJECT_ID, settings.PUBSUB_NUDGE_TOPIC)

    published_events = []
    users_ref = db.collection("users")

    for user_doc in users_ref.stream():
        uid = user_doc.id
        user_data = user_doc.to_dict() or {}
        cadence_days = user_data.get("nudgeCadenceDays", 5)
        stale_cutoff = now - timedelta(days=cadence_days)

        apps_ref = user_doc.reference.collection("applications")
        # Query for applications in 'applied' status
        query = apps_ref.where(filter=firestore.FieldFilter("status", "==", "applied"))

        for app_doc in query.stream():
            app_data = app_doc.to_dict()
            app_id = app_doc.id
            
            # Check last status update time
            updated_at_str = app_data.get("updatedAt") or app_data.get("createdAt")
            if not updated_at_str:
                continue

            try:
                updated_at = datetime.fromisoformat(updated_at_str.replace("Z", "+00:00"))
            except Exception:
                continue

            if updated_at <= stale_cutoff:
                # Check if there is already a pending nudge for this application
                nudges_ref = user_doc.reference.collection("nudges")
                pending_query = nudges_ref.where(
                    filter=firestore.FieldFilter("applicationId", "==", app_id)
                ).where(
                    filter=firestore.FieldFilter("status", "==", "pending")
                ).limit(1)

                pending_docs = list(pending_query.stream())
                if not pending_docs:
                    # Message payload
                    payload = {
                        "uid": uid,
                        "applicationId": app_id,
                        "company": app_data.get("company", "Company"),
                        "role": app_data.get("role", "Role"),
                        "daysStale": (now - updated_at).days,
                        "triggeredAt": now.isoformat()
                    }

                    # Publish to Pub/Sub
                    try:
                        data_bytes = json.dumps(payload).encode("utf-8")
                        future = publisher.publish(topic_path, data=data_bytes)
                        message_id = future.result()
                        published_events.append({
                            "uid": uid,
                            "appId": app_id,
                            "pubsubMessageId": message_id
                        })
                    except Exception as e:
                        logger.error(f"Failed to publish nudge for app {app_id}: {e}")

    return {
        "status": "success",
        "published_count": len(published_events),
        "events": published_events
    }
