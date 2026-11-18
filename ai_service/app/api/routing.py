from fastapi import APIRouter, Depends

from app.api.deps import require_api_key
from app.schemas.other import RouteRequest
from app.services import routing_service

router = APIRouter(prefix="/api/ai", tags=["Routing"], dependencies=[Depends(require_api_key)])


@router.post("/routes/optimize", summary="Multi-stop pickup routing: nearest-neighbour vs improved heuristic (+ optional exact reference)")
def optimize(req: RouteRequest):
    return routing_service.optimize(req)
