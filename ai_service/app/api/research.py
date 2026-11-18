from fastapi import APIRouter, Depends

from app.api.deps import require_api_key
from app.schemas.other import ResearchRequest
from app.services import research_service

router = APIRouter(prefix="/api/ai", tags=["Research"], dependencies=[Depends(require_api_key)])


@router.post("/research/run-experiment", summary="Run baseline comparison, ablation and/or dynamic-timeline simulations (synthetic data)")
def run_experiment(req: ResearchRequest):
    return research_service.run_research(req)
