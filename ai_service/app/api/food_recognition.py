from typing import Optional

from fastapi import APIRouter, Depends, File, UploadFile
from pydantic import BaseModel, Field

from app.api.deps import require_api_key
from app.config import get_settings
from app.services import food_service
from app.services.food_service import ImageRejected

router = APIRouter(prefix="/api/ai", tags=["Food recognition"], dependencies=[Depends(require_api_key)])
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/bmp", "image/gif"}


@router.post("/food-recognition", summary="Classify a food photo (food type only)",
             description="Returns top-3 Food-101 predictions, a food category, a donation category and a "
                         "`needs_manual_verification` flag. It does NOT estimate quantity, freshness or food safety.")
async def food_recognition(file: UploadFile = File(..., description="JPEG/PNG/WEBP/BMP/GIF image")):
    limit = get_settings().max_upload_mb * 1024 * 1024
    if file.content_type and file.content_type.lower() not in ALLOWED_TYPES:
        err = ImageRejected(f"Unsupported content type '{file.content_type}'.", "UNSUPPORTED_FILE_TYPE")
        err.status_code = 415
        raise err
    data = await file.read(limit + 1)            # never read more than limit+1 bytes
    if len(data) > limit:
        err = ImageRejected(f"File exceeds the {get_settings().max_upload_mb} MB limit.", "FILE_TOO_LARGE")
        err.status_code = 413
        raise err
    return food_service.recognize(data)


class CorrectionRequest(BaseModel):
    original_result: dict = Field(..., description="The JSON returned by /food-recognition")
    corrected_food: str = Field(..., min_length=1, max_length=120, description="Any text; not limited to Food-101 classes")
    corrected_category: Optional[str] = None
    corrected_donation_category: Optional[str] = None


@router.post("/food-recognition/correct", summary="Record a donor's manual correction of a prediction")
def correct(req: CorrectionRequest):
    return food_service.correct(req.original_result, req.corrected_food, req.corrected_category, req.corrected_donation_category)
