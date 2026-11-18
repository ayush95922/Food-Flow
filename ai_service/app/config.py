"""Central configuration (environment variables / .env)."""
from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Surplus Food AI Service"
    environment: str = "development"
    cors_origins: str = "http://localhost:3000,http://localhost:8080"
    api_key: str = ""                       # empty => authentication disabled
    max_upload_mb: int = 10
    food_model_dir: str = "saved_models/food_classifier"
    usable_time_model_dir: str = "saved_models/usable_time"
    # Food recognition backend: auto = local MobileNetV2 if installed else Groq; local = never Groq; groq = always Groq
    food_backend: str = "auto"
    groq_api_key: str = ""
    groq_model: str = "meta-llama/llama-4-scout-17b-16e-instruct"   # check Groq docs for the current vision model
    groq_timeout_s: float = 30.0
    groq_on_uncertain: bool = False         # in auto mode, also ask Groq when the local model is unsure
    default_speed_kmph: float = 25.0        # ASSUMPTION for simulated travel time
    detour_factor: float = 1.3              # ASSUMPTION: road distance ~ 1.3 x straight line
    max_radius_km: float = 15.0             # service radius used as a feasibility bound

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    def resolve(self, p: str) -> Path:
        path = Path(p)
        return path if path.is_absolute() else BASE_DIR / path


@lru_cache
def get_settings() -> Settings:
    return Settings()
