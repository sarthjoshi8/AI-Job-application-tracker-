import logging
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_v1_router
from app.core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Job Application Tracker API",
    description="GCP-Native Job Tracking and Gemini AI Draft Generation Engine",
    version="1.0.0"
)

# CORS middleware for frontend on Firebase Hosting
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_v1_router)

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Public health check endpoint for Cloud Run and load balancers.
    """
    return {
        "status": "healthy",
        "service": "ai-job-application-tracker-backend",
        "environment": "gcp-cloud-run"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error processing {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please check server logs."}
    )
