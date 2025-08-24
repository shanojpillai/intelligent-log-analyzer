from fastapi import APIRouter
from .endpoints import analysis, jobs, exports

router = APIRouter()

# Include all endpoint routers
router.include_router(analysis.router, tags=["analysis"])
router.include_router(jobs.router, tags=["jobs"])
router.include_router(exports.router, tags=["exports"])
