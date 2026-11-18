"""FastAPI entry point. Run: uvicorn app.main:app --reload --port 8000"""
import logging
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import food_recognition, forecasting, fairness, matching, research, routing, usable_time
from app.config import get_settings
from app.services import expiry_service, food_service
from app.utils.errors import AIServiceError

log = logging.getLogger("ai_service")
VERSION = "1.0.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    for name, loader in (("usable-time model", expiry_service.get_estimator), ("food classifier", food_service.get_recognizer)):
        try:
            loader()
            log.info("%s loaded", name)
        except AIServiceError as e:
            log.warning("%s not loaded: %s", name, e.message)
        except Exception:  # pragma: no cover
            log.exception("%s failed to load", name)
    yield


def create_app() -> FastAPI:
    s = get_settings()
    app = FastAPI(title=s.app_name, version=VERSION, lifespan=lifespan,
                  description="AI/ML service for dynamic, fairness-aware surplus food redistribution. "
                              "Matching is a transparent weighted-scoring algorithm; the usable-time model is an "
                              "experimental estimate trained on synthetic data; none of it certifies food safety.")
    app.add_middleware(CORSMiddleware, allow_origins=s.cors_origin_list, allow_credentials=True,
                       allow_methods=["*"], allow_headers=["*"])

    @app.exception_handler(AIServiceError)
    async def _svc(_: Request, e: AIServiceError):
        return JSONResponse(status_code=e.status_code, content={"error": {"code": e.code, "message": e.message, "details": e.details}})

    @app.exception_handler(RequestValidationError)
    async def _val(_: Request, e: RequestValidationError):
        details = [{"field": ".".join(str(x) for x in err["loc"]), "message": err["msg"]} for err in e.errors()]
        return JSONResponse(status_code=422, content={"error": {"code": "VALIDATION_ERROR", "message": "Invalid request", "details": details}})

    @app.exception_handler(Exception)
    async def _any(_: Request, e: Exception):
        log.exception("unhandled error")
        return JSONResponse(status_code=500, content={"error": {"code": "INTERNAL_ERROR", "message": "Unexpected server error", "details": None}})

    for r in (food_recognition, usable_time, matching, fairness, routing, forecasting, research):
        app.include_router(r.router)

    @app.get("/api/ai/health", tags=["Health"], summary="Service and model status")
    def health():
        return {"status": "ok", "version": VERSION, "time": datetime.now(timezone.utc).isoformat(),
                "models": {
                    "food_recognition": {"files_present": food_service.model_files_present(),
                                         "loaded": food_service.get_recognizer.cache_info().currsize > 0,
                                         "note": "Must be trained on Colab and copied to saved_models/food_classifier"},
                    "groq_fallback": {"configured": bool(s.groq_api_key), "model": s.groq_model, "backend_mode": s.food_backend},
                    "usable_time": {"files_present": (s.resolve(s.usable_time_model_dir) / "usable_time_model.joblib").is_file(),
                                    "loaded": expiry_service.get_estimator.cache_info().currsize > 0,
                                    "data_source": "SYNTHETIC"}},
                "algorithms": ["nearest_recipient", "rule_based", "dynamic_multi_factor", "weighted_max_min_fairness",
                               "nearest_neighbor_routing", "improved_routing", "forecasting_baselines_and_ml"]}

    return app


app = create_app()
