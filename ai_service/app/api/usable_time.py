from fastapi import APIRouter, Depends

from app.api.deps import require_api_key
from app.schemas.other import UsableTimeRequest
from app.services import expiry_service

router = APIRouter(prefix="/api/ai", tags=["Usable-time estimation"], dependencies=[Depends(require_api_key)])


@router.post("/usable-time-estimation", summary="Experimental remaining-usable-time estimate",
             description="Regression estimate trained on SYNTHETIC data. NOT a food-safety certification.")
def usable_time(req: UsableTimeRequest):
    return expiry_service.estimate_from_request(req)
