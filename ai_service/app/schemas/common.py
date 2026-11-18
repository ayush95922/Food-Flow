from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Location(BaseModel):
    lat: float = Field(..., ge=-90, le=90, description="Latitude (WGS84)")
    lon: float = Field(..., ge=-180, le=180, description="Longitude (WGS84)")

    def t(self):
        return (self.lat, self.lon)


class ErrorBody(BaseModel):
    code: str
    message: str
    details: Optional[object] = None


class ErrorResponse(BaseModel):
    error: ErrorBody


def unique_ids(items, what: str):
    ids = [i.id for i in items]
    if len(ids) != len(set(ids)):
        raise ValueError(f"duplicate {what} ids")
