import hmac

from fastapi import Header, HTTPException

from app.config import get_settings


def require_api_key(x_api_key: str = Header(default="", alias="X-API-Key")):
    """Optional shared-secret auth between Spring Boot and this service (enabled when API_KEY is set)."""
    key = get_settings().api_key
    if key and not hmac.compare_digest(x_api_key, key):
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key")
