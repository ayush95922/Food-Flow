from fastapi import APIRouter, Depends

from app.api.deps import require_api_key
from app.schemas.matching import MatchingRequest, MatchingResponse
from app.services import matching_service

router = APIRouter(prefix="/api/ai", tags=["Matching"], dependencies=[Depends(require_api_key)])


@router.post("/matching/recommend", response_model=MatchingResponse,
             summary="Rank feasible recipients and propose allocations (stateless; call again whenever supply, demand or availability changes)")
def recommend(req: MatchingRequest):
    return matching_service.recommend(req)
