import os
import asyncio
import logging
import time
import random
from typing import Any, Dict, List, Optional

# Safe import for Google GenAI
try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except Exception as e:
    genai = None
    types = None
    HAS_GENAI = False

from app.core.config import settings
from app.core.secret_manager import get_secret
from app.services.gemini_prompts import SYSTEM_INSTRUCTION

logger = logging.getLogger(__name__)

# In-memory rate limiting map: {uid: [timestamp, ...]}
_rate_limits: Dict[str, List[float]] = {}

class RateLimitError(Exception):
    """Raised when a user exceeds the allowed request rate."""
    pass

def check_rate_limit(uid: str, limit: int = settings.RATE_LIMIT_PER_MINUTE) -> bool:
    """
    Checks and enforces per-user rate limit (e.g. 10/minute).
    Returns True if the request is allowed, False otherwise.
    """
    now = time.time()
    if uid not in _rate_limits:
        _rate_limits[uid] = []
    
    # Keep only timestamps from the last 60 seconds
    _rate_limits[uid] = [t for t in _rate_limits[uid] if now - t < 60]
    
    if len(_rate_limits[uid]) >= limit:
        return False
    
    _rate_limits[uid].append(now)
    return True

def _get_fallback_draft(prompt: str) -> str:
    """Contextual fallback response tailor-made for AI/ML & Cloud jobs."""
    prompt_lower = prompt.lower()
    if "interview_prep" in prompt_lower or "prep" in prompt_lower:
        return (
            "### 🛰️ Gemini AI Orbit: Technical Interview & Architecture Strategy\n\n"
            "**1. Core System Design & Latency Architecture**\n"
            "- Prepare for questions on scaling LLM context windows, KV-cache management, and multi-tenant vector databases.\n"
            "- Highlight experience with asynchronous event queues (GCP Pub/Sub), Cloud Run concurrency, and rate-limiting safeguards.\n\n"
            "**2. AI Agentic Workflows & Safety**\n"
            "- Discuss structured output guarantees (JSON schema validation) and tool/function-calling error recovery.\n"
            "- Explain how you handle hallucinations and implement grounding with Firestore and Vertex AI Embeddings.\n\n"
            "**3. Behavioral & Domain Fit**\n"
            "- Emphasize end-to-end ownership: from prompt engineering and evaluation metrics to production cloud infrastructure deployment."
        )
    elif "cover letter" in prompt_lower or "task:\nwrite a compelling" in prompt_lower:
        return (
            "Dear Hiring Team,\n\n"
            "I am writing to express my strong enthusiasm for this engineering role. With deep expertise in architecting "
            "AI agent systems, production LLM pipelines with Vertex AI / Gemini, and distributed cloud microservices on Google Cloud, "
            "I am confident in my ability to accelerate your team's mission.\n\n"
            "In my recent projects, I designed and deployed high-throughput generative AI workflows, structured data extraction engines, "
            "and resilient event-driven architectures with Firestore and Pub/Sub. I excel at bridging cutting-edge foundational model capabilities "
            "with mission-critical production reliability, low latency, and rock-solid system design.\n\n"
            "I would love the opportunity to discuss how my hands-on background in full-stack AI engineering can drive immediate impact for your organization.\n\n"
            "Warm regards,\nCandidate"
        )
    else:
        return (
            "Subject: Following up on Application & AI Engineering Opportunities\n\n"
            "Dear Hiring Team,\n\n"
            "I hope you are having a productive week. I am following up on my application submitted recently. "
            "I remain extremely enthusiastic about the prospect of joining your team and contributing my experience in generative AI orchestration, "
            "cloud infrastructure, and scalable system design.\n\n"
            "Please let me know if you need any additional portfolio artifacts, code samples, or architecture diagrams. I look forward to hearing "
            "about the next steps in the interview loop.\n\n"
            "Best regards,\nCandidate"
        )

async def generate_draft_with_gemini(
    prompt: Optional[str] = None,
    uid: Optional[str] = None,
    system_instruction: str = SYSTEM_INSTRUCTION,
    max_retries: int = 5
) -> str:
    """Generate a draft using Gemini with robust retry & overload handling."""
    if prompt is not None and uid is None and not prompt.startswith("mock-user") and not prompt.startswith("user-") and len(prompt) > 50:
        effective_prompt = prompt
        effective_uid = "anonymous"
    elif uid is not None and prompt is not None:
        effective_prompt = prompt
        effective_uid = uid
    else:
        effective_prompt = prompt or ""
        effective_uid = uid or "anonymous"

    # Enforce per-user rate limit
    if not check_rate_limit(effective_uid):
        raise RateLimitError(f"User {effective_uid} exceeded rate limit of {settings.RATE_LIMIT_PER_MINUTE} requests per minute")

    # If google-genai package is not available or MOCK_MODE is enabled, return fallback
    if not HAS_GENAI or settings.MOCK_MODE:
        return _get_fallback_draft(effective_prompt)

    api_key = get_secret(settings.GEMINI_API_KEY_SECRET_NAME) or os.getenv("GEMINI_API_KEY")
    if not api_key:
        return _get_fallback_draft(effective_prompt)

    # Helper to invoke the Gemini client with exponential backoff and jitter
    async def _invoke_gemini(client: Any) -> str:
        backoff = 1.0
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(
                    f"Invoking Gemini model {settings.GEMINI_MODEL} (attempt {attempt}/{max_retries}) for user {effective_uid}"
                )
                response = client.models.generate_content(
                    model=settings.GEMINI_MODEL,
                    contents=effective_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.7,
                    ),
                )
                if response and getattr(response, "text", None):
                    return response.text.strip()
                raise ValueError("Empty response returned from Gemini API")
            except Exception as e:
                overload_signals = ["overloaded", "429", "RateLimit", "quota"]
                if any(sig.lower() in str(e).lower() for sig in overload_signals):
                    logger.warning(f"Gemini overload detected on attempt {attempt}: {e}")
                else:
                    logger.warning(f"Gemini generation attempt {attempt} failed: {e}")
                if attempt == max_retries:
                    raise e
                jitter = random.uniform(0, 0.5)
                await asyncio.sleep(backoff + jitter)
                backoff *= 2.0
        raise RuntimeError("Exceeded retries without returning a response")

    try:
        client = genai.Client(api_key=api_key)
        return await _invoke_gemini(client)
    except Exception as outer_err:
        logger.warning(f"Live Gemini API invocation error ({outer_err}). Falling back to canned response.")
        return _get_fallback_draft(effective_prompt)
