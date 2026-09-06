# AI Job Application Tracker (GCP-Native)

A full-stack, enterprise-grade job application tracking and career co-pilot platform built natively on **Google Cloud Platform** and **Firebase**.

---

## 🏛️ Architecture Overview

```
                                  [ Job Seeker / Browser ]
                                              │
                                              ▼
                    [ React + Vite + Tailwind Frontend (Firebase Hosting) ]
                                              │
                     (Bearer <Firebase ID Token> in Authorization Header)
                                              ▼
                           [ FastAPI Service on Cloud Run ]
        ┌─────────────────────────────────────┼────────────────────────────────────┐
        ▼                                     ▼                                    ▼
[ Vertex AI Gemini API ]            [ Cloud Firestore ]                   [ Secret Manager ]
 • gemini-2.5-flash                  • users/{uid}                         • SendGrid API Key
 • Contextual Cover Letters          • .../applications/{appId}            • Gemini API Credentials
 • Follow-up Emails                  • .../drafts/{draftId}
 • Voice matching via past drafts    • .../nudges/{nudgeId}
        │                                     │
        └───────────────────┬─────────────────┘
                            │
              [ Hourly Check via Cloud Scheduler ]
                            │
                            ▼
               [ Pub/Sub Topic: nudge-events ]
                            │
                            ▼
          [ Cloud Function 2nd Gen: sendNudge ]
          • Idempotent deduplication (AppID + Day)
          • Email / In-App Notification Delivery
```

---

## 🚀 Key Features

1. **GCP-Native Architecture**: Zero non-GCP compute, storage, or queues. Deployed on Cloud Run, Firestore Native Mode, Cloud Functions (2nd gen), Pub/Sub, Cloud Scheduler, and Firebase Hosting.
2. **Context-Aware Gemini Draft Generation**: Generates bespoke cover letters and follow-up emails using full context: job descriptions, candidate resume summary, skills, and previous drafts for tone and voice matching.
3. **State Transition Engine**: Enforces strict state graph validation (`applied → interview → offer`, `applied|interview → rejected`) and rejects illegal jumps with HTTP 409 Conflict.
4. **Automated Follow-up Nudges**: Stale applications (no updates for $N$ days) automatically trigger Cloud Scheduler $\rightarrow$ Pub/Sub $\rightarrow$ Cloud Function nudge flow with guaranteed idempotency.
5. **Bulk Ingestion Pipeline**: Stream-parses CSV and JSON payloads, writes to Firestore in batches of $\le 500$ ops, and automatically resolves relations.
6. **Per-User Data Isolation**: Enforced at both the FastAPI layer (Firebase Admin SDK token verification) and Firestore Security Rules.

---

## 📦 Required GCP Services & APIs

Enable the following APIs in your Google Cloud Project:
```bash
gcloud services enable \
    aiplatform.googleapis.com \
    firestore.googleapis.com \
    secretmanager.googleapis.com \
    pubsub.googleapis.com \
    cloudscheduler.googleapis.com \
    cloudfunctions.googleapis.com \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com
```

---

## 🛠️ Local Development & Running

### 1. Backend (FastAPI)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run in mock/local mode
MOCK_MODE=true uvicorn app.main:app --reload --port 8080
```

### 2. Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev
```

### 3. Running Automated Tests
```bash
cd backend
pytest -v tests/
```

### 4. Seeding Sample Data
Populates $\ge 10$ applications and $\ge 10$ drafts:
```bash
python3 scripts/seed_sample_data.py test-candidate-1
```

### 5. Simulating Stale Nudge Trigger
Backdates an application to test the nudge pipeline:
```bash
python3 scripts/simulate_stale_nudge.py
curl -X POST http://localhost:8080/api/v1/scheduler/check-stale-applications
```

---

## 🚢 Deployment to Google Cloud

### Deploy Backend to Cloud Run
```bash
cd backend
gcloud run deploy job-tracker-backend \
    --source . \
    --region us-central1 \
    --allow-unauthenticated \
    --min-instances 0 \
    --max-instances 10 \
    --set-env-vars GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
```

### Deploy Nudge Cloud Function
```bash
cd backend/functions/send_nudge
gcloud functions deploy sendNudge \
    --gen2 \
    --runtime python311 \
    --region us-central1 \
    --source . \
    --entry-point send_nudge \
    --trigger-topic nudge-events
```

### Deploy Frontend to Firebase Hosting
```bash
cd frontend
npm run build
npx -y firebase-tools@latest deploy --only hosting,firestore
```
