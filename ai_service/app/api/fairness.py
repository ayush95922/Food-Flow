from fastapi import APIRouter, Depends

from app.api.deps import require_api_key
from app.schemas.other import FairnessRequest
from app.services import fairness_service

router = APIRouter(prefix="/api/ai", tags=["Fairness"], dependencies=[Depends(require_api_key)])


@router.post("/allocation/fairness", summary="Weighted max-min fair allocation of a food pool, compared with ordinary allocations")
def fairness(req: FairnessRequest):
    return fairness_service.run_fairness(req)
