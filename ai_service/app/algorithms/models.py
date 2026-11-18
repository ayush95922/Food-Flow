"""Plain-Python domain objects used by every algorithm (independent of FastAPI/Pydantic)."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

LatLon = Tuple[float, float]
ANY_CATEGORY = "any"


@dataclass
class Donation:
    id: str
    category: str
    quantity: float                      # portions (1 portion ~ 1 meal); unit is project-defined
    location: LatLon
    pickup_deadline_min: float           # minutes from "now" after which the donor can no longer hand over
    remaining_usable_min: float          # ESTIMATED minutes of remaining usable time (from ML module or donor)
    urgency: Optional[float] = None      # 0..1; if None it is derived from the remaining usable time

    def urgency_value(self, horizon_min: float = 360.0) -> float:
        """Derived urgency u = 1 - min(1, remaining_usable / horizon). Horizon (6 h) is an assumption."""
        if self.urgency is not None:
            return min(1.0, max(0.0, float(self.urgency)))
        return min(1.0, max(0.0, 1.0 - self.remaining_usable_min / horizon_min))


@dataclass
class Recipient:
    id: str
    name: str
    location: LatLon
    demand_remaining: float              # unmet demand (portions)
    capacity: float                      # receiving capacity left (portions)
    accepted_categories: List[str] = field(default_factory=lambda: [ANY_CATEGORY])
    available: bool = True
    available_in_min: float = 0.0        # minutes until the recipient can send someone / receive
    historical_received: float = 0.0     # portions received in the look-back window
    allocation_count: int = 0            # number of past allocations in the window
    priority: float = 1.0                # >= 1; larger = higher need/priority (set by operator)

    def accepts(self, category: str) -> float:
        """Food-compatibility score: 1.0 exact match, 0.7 wildcard, 0.0 not accepted."""
        cats = {c.lower() for c in self.accepted_categories} if self.accepted_categories else {ANY_CATEGORY}
        if category.lower() in cats:
            return 1.0
        if ANY_CATEGORY in cats:
            return 0.7
        return 0.0

    def acceptable_qty(self, enforce_capacity: bool = True) -> float:
        if not self.available:
            return 0.0
        q = max(0.0, self.demand_remaining)
        return min(q, max(0.0, self.capacity)) if enforce_capacity else q


@dataclass
class Candidate:
    recipient_id: str
    recipient_name: str
    feasible: bool
    rejection_reasons: List[str] = field(default_factory=list)
    distance_km: float = 0.0
    pickup_eta_min: float = 0.0          # time until the food is collected from the donor
    delivery_eta_min: float = 0.0        # time until the food reaches the recipient
    acceptable_qty: float = 0.0
    proposed_qty: float = 0.0
    factor_scores: Dict[str, float] = field(default_factory=dict)      # each in [0, 1]
    weighted_contributions: Dict[str, float] = field(default_factory=dict)
    total_score: float = 0.0


@dataclass
class Allocation:
    donation_id: str
    recipient_id: str
    recipient_name: str
    quantity: float
    distance_km: float
    pickup_eta_min: float
    delivery_eta_min: float
    score: float
    strategy: str
    rank: int = 1
    explanation: Optional[dict] = None


@dataclass
class AllocationResult:
    donation_id: str
    strategy: str
    allocations: List[Allocation]
    unallocated_qty: float
    candidates: List[Candidate]         # first-pass ranking (feasible first, then rejected)
