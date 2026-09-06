from typing import Any, Dict, List, Optional

SYSTEM_INSTRUCTION = """
You are an expert executive career coach and professional application strategist.
Your task is to write high-impact, persuasive, and tailored job application materials.
Follow these strict rules:
1. Ground all claims in the candidate's actual profile, resume summary, and key skills.
2. Analyze the job description deeply: address core requirements, tech stack, and responsibilities directly.
3. Match the user's authentic voice and style demonstrated in their past drafts, but DO NOT copy past draft content directly.
4. Maintain a confident, professional, and clear tone without sounding robotic or clichéd.
5. Format properly (salutation, structured paragraphs, professional sign-off).
"""

def build_cover_letter_prompt(
    company: str,
    role: str,
    job_description: str,
    user_profile: Dict[str, Any],
    past_drafts: List[Dict[str, Any]]
) -> str:
    """
    Builds the user prompt for generating a tailored cover letter.
    """
    user_name = user_profile.get("name", "Applicant")
    skills = ", ".join(user_profile.get("keySkills", []))
    resume_summary = user_profile.get("resumeSummary", "Experienced software and technology professional.")

    past_examples_str = ""
    if past_drafts:
        past_examples_str = "\n--- PAST DRAFTS FOR TONE/VOICE REFERENCE ONLY (DO NOT COPY FACTS, MATCH VOICE) ---\n"
        for i, draft in enumerate(past_drafts, 1):
            past_examples_str += f"Example {i} Content:\n{draft.get('contents', '').strip()}\n\n"

    prompt = f"""
Candidate Name: {user_name}
Target Company: {company}
Target Role: {role}

Candidate Profile & Skills:
- Resume Summary: {resume_summary}
- Core Skills: {skills}

Target Job Description:
{job_description}
{past_examples_str}
TASK:
Write a compelling, tailored, and professional Cover Letter for the role of "{role}" at "{company}".
Highlight relevant skills, demonstrate enthusiasm for the company's domain, and articulate why {user_name} is the ideal candidate for the role.
"""
    return prompt.strip()

def build_follow_up_prompt(
    company: str,
    role: str,
    job_description: str,
    days_elapsed: int,
    user_profile: Dict[str, Any],
    prior_cover_letter: Optional[str] = None,
    past_drafts: Optional[List[Dict[str, Any]]] = None
) -> str:
    """
    Builds the user prompt for generating a polite, persuasive follow-up email.
    """
    user_name = user_profile.get("name", "Applicant")

    context_cover_letter = ""
    if prior_cover_letter:
        context_cover_letter = f"\nPrior Cover Letter Sent to {company}:\n{prior_cover_letter.strip()}\n"

    past_examples_str = ""
    if past_drafts:
        past_examples_str = "\n--- PAST FOLLOW-UP DRAFTS FOR TONE REFERENCE ---\n"
        for i, draft in enumerate(past_drafts, 1):
            past_examples_str += f"Example {i}:\n{draft.get('contents', '').strip()}\n\n"

    prompt = f"""
Candidate Name: {user_name}
Target Company: {company}
Target Role: {role}
Days Elapsed Since Application: {days_elapsed} days

{context_cover_letter}
Target Job Summary:
{job_description[:800]}
{past_examples_str}
TASK:
Write a concise, professional follow-up email inquiring about the status of the "{role}" application submitted {days_elapsed} days ago.
Reiterate strong interest in {company}, reference key competencies touched upon in the prior application without re-pitching everything, and politely ask about the hiring timeline.
Keep the email tight, courteous, and actionable.
"""
    return prompt.strip()
