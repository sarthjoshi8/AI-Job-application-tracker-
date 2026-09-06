import os
import sys
from datetime import datetime, timezone, timedelta
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "job-tracker-prod")
    firebase_admin.initialize_app(options={"projectId": project_id})

db = firestore.client()

SAMPLE_POSTINGS = [
    {
        "externalId": "job-001",
        "company": "Google Cloud",
        "role": "Staff Solutions Architect",
        "jobDescription": "Architecting multi-region enterprise solutions using Vertex AI, Cloud Run, and BigQuery. Partnering with strategic global accounts.",
        "status": "applied",
        "daysAgo": 12
    },
    {
        "externalId": "job-002",
        "company": "Stripe",
        "role": "Staff Backend Engineer",
        "jobDescription": "Building ultra-reliable, high-throughput payment settlement infrastructure with Python, Go, and Spanner.",
        "status": "interview",
        "daysAgo": 10
    },
    {
        "externalId": "job-003",
        "company": "DeepMind",
        "role": "AI Research Engineer",
        "jobDescription": "Designing novel agent evaluation loops, distributed reasoning frameworks, and multimodal inference pipelines.",
        "status": "applied",
        "daysAgo": 7
    },
    {
        "externalId": "job-004",
        "company": "OpenAI",
        "role": "Applied AI Engineer",
        "jobDescription": "Building production pipelines around LLM context reasoning, function calling, and structured outputs.",
        "status": "offer",
        "daysAgo": 15
    },
    {
        "externalId": "job-005",
        "company": "Figma",
        "role": "Senior WebAssembly Engineer",
        "jobDescription": "Building high-performance rendering engines and collaborative canvas subsystems in C++ and TypeScript.",
        "status": "applied",
        "daysAgo": 1
    },
    {
        "externalId": "job-006",
        "company": "Anthropic",
        "role": "Distributed Systems Engineer",
        "jobDescription": "Scaling distributed training clusters, fault tolerance systems, and high performance TPU/GPU interconnects.",
        "status": "interview",
        "daysAgo": 8
    },
    {
        "externalId": "job-007",
        "company": "Datadog",
        "role": "Cloud Observability Engineer",
        "jobDescription": "Designing telemetry ingestion pipelines handling billions of spans per second.",
        "status": "rejected",
        "daysAgo": 20
    },
    {
        "externalId": "job-008",
        "company": "Vercel",
        "role": "Edge Infrastructure Engineer",
        "jobDescription": "Building globally distributed edge compute runtime and optimized streaming asset delivery.",
        "status": "applied",
        "daysAgo": 6
    },
    {
        "externalId": "job-009",
        "company": "Linear",
        "role": "Full Stack Product Engineer",
        "jobDescription": "Crafting keyboard-first, ultra-responsive issue tracking and sync engines in TypeScript and React.",
        "status": "interview",
        "daysAgo": 4
    },
    {
        "externalId": "job-010",
        "company": "Supabase",
        "role": "Database Systems Engineer",
        "jobDescription": "Extending PostgreSQL extensions, real-time replication workers, and automated migration tooling.",
        "status": "applied",
        "daysAgo": 9
    }
]

SAMPLE_DRAFTS = [
    {
        "jobExternalId": "job-001",
        "type": "cover_letter",
        "contents": "Dear Google Cloud Hiring Team,\n\nI am writing to express my strong enthusiasm for the Staff Solutions Architect role. Having architected large-scale enterprise deployments on GCP with Vertex AI, I have firsthand experience scaling resilient cloud topologies that deliver business impact...\n\nBest regards,\nCandidate",
        "status": "sent"
    },
    {
        "jobExternalId": "job-002",
        "type": "cover_letter",
        "contents": "Dear Stripe Engineering Team,\n\nWith a track record in building fault-tolerant distributed ledger pipelines and microservices, I am excited to apply for the Staff Backend Engineer position...\n\nSincerely,\nCandidate",
        "status": "sent"
    },
    {
        "jobExternalId": "job-003",
        "type": "cover_letter",
        "contents": "Dear DeepMind Team,\n\nI am deeply inspired by DeepMind's pioneering research. My background in orchestrating autonomous AI agent loops and optimizing inference makes this AI Research Engineer role an ideal fit...\n\nBest,\nCandidate",
        "status": "draft"
    },
    {
        "jobExternalId": "job-004",
        "type": "cover_letter",
        "contents": "Dear OpenAI Team,\n\nI am thrilled to apply for the Applied AI Engineer position to scale cutting-edge LLM applications with structured output and function-calling reliability...\n\nWarmly,\nCandidate",
        "status": "sent"
    },
    {
        "jobExternalId": "job-005",
        "type": "cover_letter",
        "contents": "Dear Figma Team,\n\nI have followed Figma's engineering excellence in WebAssembly and browser performance for years. I would be thrilled to bring my frontend systems background to the core canvas team...\n\nBest regards,\nCandidate",
        "status": "draft"
    },
    {
        "jobExternalId": "job-006",
        "type": "follow_up_email",
        "contents": "Hi Anthropic Team,\n\nThank you for the fantastic technical conversation earlier this week. I enjoyed discussing distributed cluster interconnects and look forward to the next steps.\n\nBest,\nCandidate",
        "status": "sent"
    },
    {
        "jobExternalId": "job-007",
        "type": "cover_letter",
        "contents": "Dear Datadog Team,\n\nI am applying for the Cloud Observability Engineer position to contribute to your high-throughput ingestion platform...\n\nSincerely,\nCandidate",
        "status": "archived"
    },
    {
        "jobExternalId": "job-008",
        "type": "cover_letter",
        "contents": "Dear Vercel Team,\n\nAs a developer who loves building performant web apps, I would relish the opportunity to work on Vercel's global edge runtime...\n\nBest regards,\nCandidate",
        "status": "draft"
    },
    {
        "jobExternalId": "job-009",
        "type": "follow_up_email",
        "contents": "Hi Linear Team,\n\nJust following up on our recent interview session. I am very energized by the product vision and look forward to hearing about the next steps.\n\nThanks,\nCandidate",
        "status": "sent"
    },
    {
        "jobExternalId": "job-010",
        "type": "cover_letter",
        "contents": "Dear Supabase Team,\n\nI am applying for the Database Systems Engineer position. Building open source database tooling and real-time syncing engines is my greatest engineering passion...\n\nBest regards,\nCandidate",
        "status": "draft"
    }
]

def seed_data_for_user(uid: str = "test-candidate-1"):
    print(f"🌱 Seeding sample postings and drafts for user: {uid}...")
    user_ref = db.collection("users").document(uid)

    # 1. Set user profile
    now = datetime.now(timezone.utc)
    user_ref.set({
        "name": "Alex Johnson",
        "email": f"{uid}@example.com",
        "resumeSummary": "Senior Staff Software Engineer with 9+ years experience building distributed GCP systems, AI agent workflows, and high-concurrency microservices.",
        "keySkills": ["Python", "FastAPI", "React", "TypeScript", "Google Cloud", "Vertex AI", "Firestore", "Kubernetes"],
        "nudgeCadenceDays": 5,
        "createdAt": now.isoformat(),
        "updatedAt": now.isoformat()
    })

    apps_ref = user_ref.collection("applications")
    batch = db.batch()
    created_app_map = {}

    # 2. Seed 10 Job Postings
    for post in SAMPLE_POSTINGS:
        app_ref = apps_ref.document()
        app_date = (now - timedelta(days=post["daysAgo"])).isoformat()
        updated_date = (now - timedelta(days=post["daysAgo"])).isoformat()
        
        data = {
            "company": post["company"],
            "role": post["role"],
            "jobDescription": post["jobDescription"],
            "applicationDate": app_date,
            "status": post["status"],
            "statusHistory": [
                {"status": "applied", "changedAt": app_date},
                *([] if post["status"] == "applied" else [{"status": post["status"], "changedAt": updated_date}])
            ],
            "externalId": post["externalId"],
            "nextNudgeAt": None,
            "createdAt": app_date,
            "updatedAt": updated_date
        }
        batch.set(app_ref, data)
        created_app_map[post["externalId"]] = app_ref

    batch.commit()
    print(f"✅ Created {len(SAMPLE_POSTINGS)} application postings.")

    # 3. Seed 10 Drafts linked to the postings
    draft_batch = db.batch()
    for draft in SAMPLE_DRAFTS:
        target_app_ref = created_app_map.get(draft["jobExternalId"])
        if target_app_ref:
            draft_ref = target_app_ref.collection("drafts").document()
            draft_data = {
                "type": draft["type"],
                "contents": draft["contents"],
                "status": draft["status"],
                "generatedBy": "ai",
                "generationModel": "gemini-2.5-flash",
                "createdAt": now.isoformat(),
                "updatedAt": now.isoformat()
            }
            draft_batch.set(draft_ref, draft_data)

    draft_batch.commit()
    print(f"✅ Created {len(SAMPLE_DRAFTS)} linked drafts.")
    print("🚀 Seeding completed successfully!")

if __name__ == "__main__":
    target_uid = sys.argv[1] if len(sys.argv) > 1 else "test-candidate-1"
    seed_data_for_user(target_uid)
