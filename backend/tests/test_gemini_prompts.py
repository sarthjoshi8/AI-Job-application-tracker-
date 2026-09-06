from app.services.gemini_prompts import build_cover_letter_prompt, build_follow_up_prompt

def test_build_cover_letter_prompt():
    user_profile = {
        "name": "Jane Doe",
        "keySkills": ["Python", "FastAPI", "GCP"],
        "resumeSummary": "Senior Cloud Architect with 8 years building distributed pipelines."
    }
    past_drafts = [
        {"contents": "Dear hiring manager, I am writing to express my strong enthusiasm..."}
    ]

    prompt = build_cover_letter_prompt(
        company="Anthropic",
        role="Systems Engineer",
        job_description="Looking for an engineer to optimize latency on distributed clusters.",
        user_profile=user_profile,
        past_drafts=past_drafts
    )

    assert "Jane Doe" in prompt
    assert "Anthropic" in prompt
    assert "Systems Engineer" in prompt
    assert "Senior Cloud Architect" in prompt
    assert "PAST DRAFTS FOR TONE/VOICE REFERENCE" in prompt

def test_build_follow_up_prompt():
    user_profile = {"name": "Jane Doe"}
    prior_cover_letter = "Original submission highlighting distributed systems skills."
    
    prompt = build_follow_up_prompt(
        company="OpenAI",
        role="Research Engineer",
        job_description="Build inference pipelines.",
        days_elapsed=10,
        user_profile=user_profile,
        prior_cover_letter=prior_cover_letter
    )

    assert "10 days" in prompt
    assert "Prior Cover Letter Sent to OpenAI" in prompt
    assert "Original submission highlighting" in prompt
