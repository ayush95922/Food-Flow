from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, model_validator

from app.schemas.common import Location, unique_ids


class DonationIn(BaseModel):
    id: str = Field(..., min_length=1, examples=["D-101"])
    food_category: str = Field(..., examples=["cooked_meal"], description="Donation category (or Food-101 dish category, mapped automatically)")
    quantity: float = Field(..., gt=0, description="Portions available")
    location: Location
    pickup_deadline_minutes: float = Field(..., gt=0, description="Minutes from now until the donor deadline")
    remaining_usable_minutes: float = Field(..., gt=0, description="ESTIMATED usable minutes left (see usable-time endpoint)")
    urgency: Optional[float] = Field(None, ge=0, le=1, description="0..1; derived from remaining usable time if omitted")


class RecipientIn(BaseModel):
    id: str = Field(..., min_length=1, examples=["NGO-7"])
    name: str
    location: Location
    accepted_categories: List[str] = Field(default_factory=lambda: ["any"])
    demand_remaining: float = Field(..., ge=0)
    capacity: float = Field(..., ge=0)
    available: bool = True
    available_in_minutes: float = Field(0, ge=0)
    historical_received: float = Field(0, ge=0)
    allocation_count: int = Field(0, ge=0)
    priority: float = Field(1.0, ge=1.0, le=10.0)


class WeightsIn(BaseModel):
    demand: Optional[float] = Field(None, ge=0)
    quantity: Optional[float] = Field(None, ge=0)
    distance: Optional[float] = Field(None, ge=0)
    urgency: Optional[float] = Field(None, ge=0)
    usable_time: Optional[float] = Field(None, ge=0)
    capacity: Optional[float] = Field(None, ge=0)
    compatibility: Optional[float] = Field(None, ge=0)
    pickup_feasibility: Optional[float] = Field(None, ge=0)
    fairness: Optional[float] = Field(None, ge=0)


class MatchingOptionsIn(BaseModel):
    speed_kmph: float = Field(25.0, gt=0, le=120)
    detour_factor: float = Field(1.3, ge=1.0, le=3.0)
    max_radius_km: float = Field(15.0, gt=0, le=500)
    max_chunks: int = Field(3, ge=1, le=10)
    top_n: int = Field(5, ge=1, le=50)
    include_rejected: bool = True


class MatchingRequest(BaseModel):
    donations: List[DonationIn] = Field(..., min_length=1, max_length=200)
    recipients: List[RecipientIn] = Field(..., min_length=1, max_length=500)
    strategy: Literal["nearest", "rule_based", "dynamic"] = "dynamic"
    weights: Optional[WeightsIn] = None
    options: MatchingOptionsIn = Field(default_factory=MatchingOptionsIn)
    compare_strategies: bool = False

    @model_validator(mode="after")
    def _ids(self):
        unique_ids(self.donations, "donation")
        unique_ids(self.recipients, "recipient")
        return self


class CandidateOut(BaseModel):
    recipient_id: str
    recipient_name: str
    rank: Optional[int] = None
    feasible: bool
    total_score: Optional[float] = None
    factor_scores: Dict[str, float] = {}
    weighted_contributions: Dict[str, float] = {}
    distance_km: float
    pickup_eta_minutes: float
    delivery_eta_minutes: float
    acceptable_quantity: float
    rejection_codes: List[str] = []
    rejection_reasons: List[str] = []


class AllocationOut(BaseModel):
    recipient_id: str
    recipient_name: str
    quantity: float
    distance_km: float
    pickup_eta_minutes: float
    delivery_eta_minutes: float
    score: float
    chunk: int
    explanation: Optional[dict] = None


class DonationResult(BaseModel):
    donation_id: str
    status: Literal["fully_allocated", "partially_allocated", "unallocated"]
    allocations: List[AllocationOut]
    unallocated_quantity: float
    ranked_candidates: List[CandidateOut]
    rejected_candidates: List[CandidateOut]


class MatchingResponse(BaseModel):
    strategy: str
    weights_used: Optional[Dict[str, float]] = None
    processing_order: List[str]
    results: List[DonationResult]
    summary: dict
    updated_recipient_states: List[dict]
    comparison: Optional[dict] = None
    assumptions: List[str]
