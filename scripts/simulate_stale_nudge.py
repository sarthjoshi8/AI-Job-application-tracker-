import os
import sys
from datetime import datetime, timezone, timedelta
import firebase_admin
from firebase_admin import firestore

if not firebase_admin._apps:
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "job-tracker-prod")
    firebase_admin.initialize_app(options={"projectId": project_id})

db = firestore.client()

def backdate_application_to_stale(uid: str = "test-candidate-1", days_back: int = 14):
    print(f"⏳ Backdating an 'applied' application for user {uid} to {days_back} days ago...")
    user_ref = db.collection("users").document(uid)
    apps_ref = user_ref.collection("applications")

    stale_date = (datetime.now(timezone.utc) - timedelta(days=days_back)).isoformat()

    # Find the first 'applied' application
    query = apps_ref.where(filter=firestore.FieldFilter("status", "==", "applied")).limit(1)
    docs = list(query.stream())

    if not docs:
        print("Creating a new test application to backdate...")
        new_ref = apps_ref.document()
        new_ref.set({
            "company": "Simulated Tech Corp",
            "role": "Lead Architect",
            "jobDescription": "Full-stack cloud engineering with GCP & Gemini.",
            "applicationDate": stale_date,
            "status": "applied",
            "statusHistory": [{"status": "applied", "changedAt": stale_date}],
            "updatedAt": stale_date,
            "createdAt": stale_date
        })
        app_id = new_ref.id
    else:
        app_doc = docs[0]
        app_doc.reference.update({
            "updatedAt": stale_date
        })
        app_id = app_doc.id

    print(f"✅ Application {app_id} is now backdated to {stale_date} (Stale: {days_back} days).")
    print("Run the scheduler endpoint (POST /api/v1/scheduler/check-stale-applications) to trigger the nudge event chain!")

if __name__ == "__main__":
    backdate_application_to_stale()
