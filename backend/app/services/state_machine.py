import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Set, Tuple
from google.cloud import firestore

logger = logging.getLogger(__name__)

# Valid transitions state graph
# applied -> interview -> offer
# applied | interview -> rejected
VALID_TRANSITIONS: Dict[str, Set[str]] = {
    "applied": {"interview", "rejected"},
    "interview": {"offer", "rejected"},
    "offer": set(),     # Terminal success state
    "rejected": set()   # Terminal state
}

class InvalidStateTransitionError(Exception):
    def __init__(self, current_status: str, new_status: str):
        self.current_status = current_status
        self.new_status = new_status
        super().__init__(f"Invalid status transition from '{current_status}' to '{new_status}'")

def validate_state_transition(current_status: str, new_status: str) -> bool:
    """
    Validates whether the transition from current_status to new_status is permitted.
    """
    if current_status == new_status:
        return True
    
    allowed = VALID_TRANSITIONS.get(current_status, set())
    if new_status not in allowed:
        return False
    return True

def apply_status_transition(
    app_ref: firestore.DocumentReference,
    app_data: dict,
    new_status: str,
    user_ref: firestore.DocumentReference
) -> Tuple[dict, List[dict]]:
    """
    Validates and constructs updated application fields and creates automated notification messages
    for candidate status changes (Interview, Offer, Rejected, Applied).
    """
    current_status = app_data.get("status", "applied")
    if not validate_state_transition(current_status, new_status):
        raise InvalidStateTransitionError(current_status, new_status)

    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()
    company = app_data.get("company", "the company")
    role = app_data.get("role", "the role")

    status_history = list(app_data.get("statusHistory", []))
    status_history.append({
        "status": new_status,
        "changedAt": now_iso
    })

    updates = {
        "status": new_status,
        "statusHistory": status_history,
        "updatedAt": now_iso
    }

    side_effects = []

    # 1. Automatic Message for INTERVIEW loop update
    if new_status == "interview":
        thank_you_date = now + timedelta(days=2)
        side_effects.append({
            "action": "cancel_pending_nudges",
            "app_id": app_ref.id
        })
        side_effects.append({
            "action": "create_nudge",
            "app_id": app_ref.id,
            "company": company,
            "role": role,
            "scheduledFor": thank_you_date.isoformat(),
            "message": f"🎉 Exciting News! Your application for {role} at {company} has advanced to the Interview Stage! Review your AI prep strategy and send a thank-you follow-up."
        })

    # 2. Automatic Message for OFFER received
    elif new_status == "offer":
        side_effects.append({
            "action": "cancel_pending_nudges",
            "app_id": app_ref.id
        })
        side_effects.append({
            "action": "create_nudge",
            "app_id": app_ref.id,
            "company": company,
            "role": role,
            "scheduledFor": now_iso,
            "message": f"🌟 Congratulations! You received an Offer for {role} at {company}! Review compensation packages and send acceptance correspondence."
        })

    # 3. Automatic Message for REJECTED / Archived
    elif new_status == "rejected":
        side_effects.append({
            "action": "cancel_pending_nudges",
            "app_id": app_ref.id
        })
        side_effects.append({
            "action": "create_nudge",
            "app_id": app_ref.id,
            "company": company,
            "role": role,
            "scheduledFor": now_iso,
            "message": f"📋 Update on {company} ({role}): The company decided to move forward with other candidates. Your application has been archived for future re-applications."
        })

    return updates, side_effects
