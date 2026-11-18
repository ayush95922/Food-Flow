from datetime import date, datetime
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, model_validator

from app.schemas.common import Location, unique_ids


# ------------------------------------------------------------------ usable time
class UsableTimeRequest(BaseModel):
    food_category: str = Field(..., examples=["cooked_meal"])
    food_type: Optional[str] = Field(None, examples=["chicken curry"], description="Informational only: the model uses the category")
    elapsed_minutes: Optional[float] = Field(None, ge=0, description="Minutes since preparation")
    prepared_at: Optional[datetime] = Field(None, description="Alternative to elapsed_minutes (ISO-8601)")
    current_time: Optional[datetime] = Field(None, description="Defaults to server time when prepared_at is used")
    storage_condition: str = Field(..., examples=["refrigerated"])
    temperature_c: Optional[float] = Field(None, ge=-40, le=100)
    packaging: Optional[str] = Field(None, examples=["sealed_container"])

    @model_validator(mode="after")
    def _need_time(self):
        if self.elapsed_minutes is None and self.prepared_at is None:
            raise ValueError("provide elapsed_minutes or prepared_at")
        return self


# ------------------------------------------------------------------ fairness
class FairRecipientIn(BaseModel):
    id: str
    name: str
    demand: float = Field(..., ge=0)
    capacity: float = Field(..., ge=0)
    historical_received: float = Field(0, ge=0)
    allocation_count: int = Field(0, ge=0)
    priority: float = Field(1.0, ge=1.0, le=10.0)


class FairnessRequest(BaseModel):
    supply: float = Field(..., ge=0)
    recipients: List[FairRecipientIn] = Field(..., min_length=1, max_length=500)
    frequency_penalty: float = Field(5.0, ge=0, description="Portions charged per past allocation (assumption)")
    compare: bool = True

    @model_validator(mode="after")
    def _ids(self):
        unique_ids(self.recipients, "recipient")
        return self


# ------------------------------------------------------------------ routing
class PickupIn(BaseModel):
    id: str
    location: Location
    deadline_minutes: float = Field(..., gt=0)
    urgency: float = Field(0.5, ge=0, le=1)
    quantity: float = Field(1.0, gt=0)
    service_minutes: float = Field(5.0, ge=0)
    usable_minutes: Optional[float] = Field(None, gt=0, description="Food must reach the destination before this")


class GraphNode(BaseModel):
    id: str
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)


class GraphEdge(BaseModel):
    u: str
    v: str
    distance_km: float = Field(..., ge=0)


class RoadGraphIn(BaseModel):
    nodes: List[GraphNode] = Field(..., min_length=2, max_length=5000)
    edges: List[GraphEdge] = Field(..., min_length=1, max_length=20000)
    algorithm: Literal["dijkstra", "astar"] = "dijkstra"


class RouteRequest(BaseModel):
    volunteer_location: Location
    destination: Location
    pickups: List[PickupIn] = Field(..., min_length=1, max_length=30)
    mode: Literal["simulated", "graph"] = "simulated"
    road_graph: Optional[RoadGraphIn] = Field(None, description="OpenStreetMap-derived graph; required when mode='graph'")
    speed_kmph: float = Field(25.0, gt=0, le=120)
    detour_factor: float = Field(1.3, ge=1.0, le=3.0)
    include_optimal_reference: bool = True

    @model_validator(mode="after")
    def _chk(self):
        unique_ids(self.pickups, "pickup")
        if self.mode == "graph" and self.road_graph is None:
            raise ValueError("road_graph is required when mode='graph'")
        return self


# ------------------------------------------------------------------ forecasting
class HistoryRecord(BaseModel):
    date: date
    supply_qty: float = Field(..., ge=0)
    demand_qty: float = Field(..., ge=0)
    category: Optional[str] = None


class ForecastRequest(BaseModel):
    records: List[HistoryRecord] = Field(default_factory=list, max_length=100000)
    horizon_days: int = Field(7, ge=1, le=30)
    by_category: bool = True


# ------------------------------------------------------------------ research
class ResearchConfig(BaseModel):
    n_donations: int = Field(40, ge=2, le=300)
    n_recipients: int = Field(12, ge=2, le=100)
    categories: Optional[List[str]] = None
    qty_min: float = Field(20, gt=0)
    qty_max: float = Field(200, gt=0)
    demand_supply_ratio: float = Field(1.0, gt=0, le=5)
    city_radius_km: float = Field(8.0, gt=0, le=100)
    deadline_min_range: List[float] = Field([30.0, 180.0], min_length=2, max_length=2)
    storage_conditions: Optional[List[str]] = None
    capacity_factor_range: List[float] = Field([0.5, 1.2], min_length=2, max_length=2)
    estimate_noise: float = Field(0.15, ge=0, le=1)
    n_demand_events: int = Field(6, ge=0, le=50)
    n_unavailable_events: int = Field(4, ge=0, le=50)
    accept_prob: float = Field(0.85, ge=0, le=1)


class ResearchRequest(BaseModel):
    config: ResearchConfig = Field(default_factory=ResearchConfig)
    n_seeds: int = Field(10, ge=1, le=50)
    base_seed: int = Field(0, ge=0)
    experiments: List[Literal["baselines", "ablation", "dynamic_timeline"]] = ["baselines", "ablation", "dynamic_timeline"]
    include_per_seed: bool = False
