"""Fairness-aware allocation of a pooled food supply among recipients.

Weighted max-min ("water-filling") allocation
---------------------------------------------
Recipient i has a cap  c_i = min(demand_i, capacity_i), a priority weight p_i >= 1 and an *effective
history* h_i = historical_received_i + lambda * allocation_count_i  (lambda = portions charged per past
allocation, default 5 - an assumption; set 0 to ignore frequency).

We look for the common level L such that
        x_i(L) = clip(p_i * L - h_i, 0, c_i)       and       sum_i x_i(L) = min(S, sum_i c_i)
i.e. recipients with the least history-per-priority are filled first, until everybody that is not
saturated has the same cumulative received amount per priority weight (h_i + x_i)/p_i.
This is the (weighted) max-min fair solution of: maximise the minimum (h_i + x_i)/p_i subject to
0 <= x_i <= c_i and sum x_i <= S.  L is found by bisection because sum_i x_i(L) is monotone in L.

Reference ("ordinary") allocations for comparison
    proportional : x_i = S * c_i / sum c_j  (demand-proportional, ignores history/priority)
    fcfs         : fill recipients in the order given (first-come-first-served)

Metrics
    Jain's index  J(y) = (sum y)^2 / (n * sum y^2),  1/n <= J <= 1  (1 = perfectly equal). Reported on
      * current fulfilment  y_i = x_i / demand_i       (how equally demand is met this round)
      * cumulative received y_i = (h_i^raw + x_i)/p_i  (how equally food is shared over time)
    unmet demand = sum (demand_i - x_i); Gini of cumulative received; min/max fulfilment.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional

import numpy as np


@dataclass
class FairRecipient:
    id: str
    name: str
    demand: float
    capacity: float
    historical_received: float = 0.0
    allocation_count: int = 0
    priority: float = 1.0

    @property
    def cap(self) -> float:
        return max(0.0, min(self.demand, self.capacity))


def jain_index(values) -> float:
    """Jain's fairness index. Returns 1.0 for empty or all-zero input (nothing to be unfair about)."""
    v = np.asarray(list(values), dtype=float)
    if v.size == 0:
        return 1.0
    denom = v.size * float(np.sum(v ** 2))
    if denom == 0:
        return 1.0
    return float(np.sum(v) ** 2 / denom)


def gini(values) -> float:
    v = np.sort(np.asarray(list(values), dtype=float))
    if v.size == 0 or v.sum() == 0:
        return 0.0
    n = v.size
    return float((2 * np.sum((np.arange(1, n + 1)) * v) / (n * v.sum())) - (n + 1) / n)


def _eff_history(r: FairRecipient, lam: float) -> float:
    return r.historical_received + lam * r.allocation_count


def max_min_allocation(supply: float, recipients: List[FairRecipient], freq_penalty: float = 5.0) -> Dict:
    if supply < 0:
        raise ValueError("supply must be non-negative")
    caps = np.array([r.cap for r in recipients])
    h = np.array([_eff_history(r, freq_penalty) for r in recipients])
    p = np.array([max(r.priority, 1e-9) for r in recipients])
    if len(recipients) == 0:
        return {"x": np.array([]), "level": 0.0}
    if supply >= caps.sum():
        return {"x": caps.copy(), "level": float(np.max((h + caps) / p))}
    lo, hi = 0.0, float(np.max((h + caps) / p))
    for _ in range(100):
        mid = (lo + hi) / 2
        total = np.clip(p * mid - h, 0, caps).sum()
        lo, hi = (mid, hi) if total < supply else (lo, mid)
    x = np.clip(p * hi - h, 0, caps)
    # numerical clean-up so that sum(x) == supply exactly and never exceeds it
    s = x.sum()
    if s > 0:
        x = x * (supply / s) if s > supply else x
    return {"x": x, "level": float(hi)}


def proportional_allocation(supply: float, recipients: List[FairRecipient]) -> np.ndarray:
    caps = np.array([r.cap for r in recipients])
    if caps.sum() == 0:
        return np.zeros_like(caps)
    return np.minimum(caps, supply * caps / caps.sum()) if supply < caps.sum() else caps.copy()


def fcfs_allocation(supply: float, recipients: List[FairRecipient]) -> np.ndarray:
    x, left = [], supply
    for r in recipients:
        t = min(r.cap, left)
        x.append(t)
        left -= t
    return np.array(x)


def metrics(x: np.ndarray, recipients: List[FairRecipient]) -> Dict:
    demand = np.array([r.demand for r in recipients])
    hist = np.array([r.historical_received for r in recipients])
    p = np.array([max(r.priority, 1e-9) for r in recipients])
    fulfil = np.divide(x, demand, out=np.zeros_like(x, dtype=float), where=demand > 0)
    cumulative = (hist + x) / p
    return {
        "allocated_total": float(x.sum()),
        "unmet_demand_total": float(np.sum(np.maximum(demand - x, 0))),
        "jain_current_fulfilment": jain_index(fulfil[demand > 0]),
        "jain_cumulative_per_priority": jain_index(cumulative),
        "gini_cumulative_per_priority": gini(cumulative),
        "min_fulfilment": float(fulfil[demand > 0].min()) if np.any(demand > 0) else 0.0,
        "max_fulfilment": float(fulfil.max()) if len(fulfil) else 0.0,
    }


def explain_priority(recipients: List[FairRecipient], x: np.ndarray, level: float, supply: float,
                     freq_penalty: float) -> List[Dict]:
    h = np.array([_eff_history(r, freq_penalty) / max(r.priority, 1e-9) for r in recipients])
    order = np.argsort(h)
    rank = {int(i): k + 1 for k, i in enumerate(order)}
    out = []
    for i, r in enumerate(recipients):
        reasons = []
        reasons.append(f"Effective history per priority = {h[i]:.1f} (rank {rank[i]} of {len(recipients)}, "
                       f"1 = lowest history, served first)")
        if x[i] >= r.cap - 1e-6:
            reasons.append(f"Received its full cap of {r.cap:.1f} portions (min of demand {r.demand:.1f} "
                           f"and capacity {r.capacity:.1f})")
        elif x[i] <= 1e-9:
            reasons.append(f"Received nothing: its history per priority ({h[i]:.1f}) is above the fairness "
                           f"level {level:.1f} reached when supply {supply:.1f} ran out")
        else:
            reasons.append(f"Filled up to the common fairness level {level:.1f} (cumulative received per priority)")
        if r.priority > 1:
            reasons.append(f"Priority weight {r.priority:.1f} increases its share")
        out.append({"recipient_id": r.id, "reasons": reasons})
    return out


def allocate_fairly(supply: float, recipients: List[FairRecipient], freq_penalty: float = 5.0,
                    compare: bool = True) -> Dict:
    res = max_min_allocation(supply, recipients, freq_penalty)
    x = res["x"]
    out = {
        "supply": supply,
        "fairness_level": res["level"],
        "allocations": [{"recipient_id": r.id, "name": r.name, "allocated": round(float(x[i]), 4),
                         "demand": r.demand, "fulfilment_ratio": round(float(x[i] / r.demand), 4) if r.demand > 0 else 0.0}
                        for i, r in enumerate(recipients)],
        "metrics": metrics(x, recipients),
        "explanations": explain_priority(recipients, x, res["level"], supply, freq_penalty),
        "method": "weighted max-min (water-filling) on cumulative received per priority",
    }
    if compare:
        out["comparison"] = {}
        for name, fn in (("proportional", proportional_allocation), ("fcfs", fcfs_allocation)):
            xo = fn(supply, recipients)
            out["comparison"][name] = {"allocations": [round(float(v), 4) for v in xo], "metrics": metrics(xo, recipients)}
    return out
