from fastapi import APIRouter

from app.api.v1.applications import router as applications_router
from app.api.v1.drafts import router as drafts_router
from app.api.v1.import_data import router as import_router
from app.api.v1.nudges import router as nudges_router
from app.api.v1.user_profile import router as user_profile_router
from app.api.v1.scheduler_trigger import router as scheduler_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(applications_router)
api_v1_router.include_router(drafts_router)
api_v1_router.include_router(import_router)
api_v1_router.include_router(nudges_router)
api_v1_router.include_router(user_profile_router)
api_v1_router.include_router(scheduler_router)
