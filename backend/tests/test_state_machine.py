import pytest
from app.services.state_machine import validate_state_transition, apply_status_transition, InvalidStateTransitionError

class MockDocRef:
    def __init__(self, id_val):
        self.id = id_val

def test_legal_transitions():
    # applied -> interview
    assert validate_state_transition("applied", "interview") is True
    # interview -> offer
    assert validate_state_transition("interview", "offer") is True
    # applied -> rejected
    assert validate_state_transition("applied", "rejected") is True
    # interview -> rejected
    assert validate_state_transition("interview", "rejected") is True
    # same status is idempotent
    assert validate_state_transition("applied", "applied") is True

def test_illegal_transitions():
    # applied cannot jump directly to offer
    assert validate_state_transition("applied", "offer") is False
    # offer cannot transition back to applied or interview
    assert validate_state_transition("offer", "applied") is False
    assert validate_state_transition("offer", "interview") is False
    # rejected is terminal
    assert validate_state_transition("rejected", "interview") is False

def test_apply_status_transition_interview_side_effects():
    app_ref = MockDocRef("app-123")
    user_ref = MockDocRef("user-456")
    app_data = {
        "company": "Google",
        "role": "Cloud Architect",
        "status": "applied",
        "statusHistory": [{"status": "applied", "changedAt": "2026-08-01T00:00:00Z"}]
    }

    updates, side_effects = apply_status_transition(app_ref, app_data, "interview", user_ref)
    assert updates["status"] == "interview"
    assert len(updates["statusHistory"]) == 2
    assert updates["statusHistory"][-1]["status"] == "interview"

    # Verify side effects: cancel pending nudges + schedule thank-you nudge (+2 days)
    assert len(side_effects) == 2
    actions = [s["action"] for s in side_effects]
    assert "cancel_pending_nudges" in actions
    assert "create_nudge" in actions

def test_apply_status_transition_illegal_raises():
    app_ref = MockDocRef("app-123")
    user_ref = MockDocRef("user-456")
    app_data = {"status": "applied"}

    with pytest.raises(InvalidStateTransitionError):
        apply_status_transition(app_ref, app_data, "offer", user_ref)
