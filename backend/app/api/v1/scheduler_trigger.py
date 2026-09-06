import logging
from fastapi import APIRouter, HTTPException, status
from app.services.nudge_service import check_stale_applications_and_publish

router = APIRouter(prefix="/scheduler", tags=["Cloud Scheduler Triggers"])
logger = logging.getLogger(__name__)

@router.post("/check-stale-applications")
async def trigger_stale_check():
    """
    HTTP target endpoint called by Cloud Scheduler (or local tests) to inspect
    stale applications across Firestore and dispatch Pub/Sub nudge events.
    """
    try:
        result = check_stale_applications_and_publish()
        return result
    except Exception as e:
        logger.error(f"Error in scheduler stale application check: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process stale applications: {str(e)}"
        )
