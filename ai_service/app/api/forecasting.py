from fastapi import APIRouter, Depends

from app.api.deps import require_api_key
from app.schemas.other import ForecastRequest
from app.services import forecasting_service

router = APIRouter(prefix="/api/ai", tags=["Forecasting"], dependencies=[Depends(require_api_key)])


@router.post("/forecast/demand", summary="Supply/demand forecast from caller-supplied history (never fabricates data)")
def forecast(req: ForecastRequest):
    recs = [{"date": r.date.isoformat(), "supply_qty": r.supply_qty, "demand_qty": r.demand_qty, "category": r.category}
            for r in req.records]
    if recs and all(r["category"] is None for r in recs):
        for r in recs:
            r.pop("category")
    else:
        for r in recs:
            r["category"] = r["category"] or "uncategorised"
    return forecasting_service.run_forecast(recs, req.horizon_days, req.by_category)
