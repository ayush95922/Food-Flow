"""Scenario generator + online (static-information) allocation simulator.

Everything generated here is SYNTHETIC. The documented generator assumptions:
  * recipients/donors are uniformly placed in a disc of `city_radius_km` around `city_center`;
  * total recipient demand = `demand_supply_ratio` x total donated quantity (lognormal split);
  * true remaining usable time follows the same assumption model as the usable-time module
    (base life x temperature x storage x packaging x noise - elapsed), floored at 12 minutes;
  * the matcher only sees an ESTIMATE = truth x lognormal(0, estimate_noise); execution is judged on the TRUTH.
Donations are processed one by one in arrival order (online greedy), each strategy on its own copy of the state.
"""
import time
from copy import deepcopy
from dataclasses import dataclass, field, replace
from typing import Callable, Dict, List, Optional

import numpy as np

from app.algorithms import dynamic_matching as dm
from app.algorithms import nearest_recipient as nr
from app.algorithms import rule_based as rb
from app.algorithms.matching_core import MatchingOptions, TravelModel
from app.algorithms.models import ANY_CATEGORY, Donation, Recipient
from app.experiments.metrics import summarize_run
from app.services import expiry_training as ET

CATEGORIES = list(ET.BASE_LIFE_H)
STORAGES = list(ET.STORAGE_FACTOR)


@dataclass
class ScenarioConfig:
    n_donations: int = 40
    n_recipients: int = 12
    categories: List[str] = field(default_factory=lambda: list(CATEGORIES))
    qty_min: float = 20.0
    qty_max: float = 200.0
    demand_supply_ratio: float = 1.0
    city_center: tuple = (22.7196, 75.8577)          # synthetic city centre (Indore, IN) - no real addresses
    city_radius_km: float = 8.0
    deadline_min_range: tuple = (30.0, 180.0)
    storage_conditions: List[str] = field(default_factory=lambda: list(STORAGES))
    capacity_factor_range: tuple = (0.5, 1.2)        # capacity = demand x factor
    horizon_min: float = 480.0                       # donations arrive over this window
    estimate_noise: float = 0.15
    speed_kmph: float = 25.0
    detour_factor: float = 1.3
    max_radius_km: float = 15.0
    # dynamic-timeline parameters
    n_demand_events: int = 6
    n_unavailable_events: int = 4
    unavailable_duration_min: tuple = (60.0, 180.0)
    accept_prob: float = 0.85
    response_delay_range: tuple = (10.0, 30.0)


@dataclass
class SimDonation:
    donation: Donation                 # what the matcher sees (estimated usable time)
    arrival_min: float
    true_usable_min: float
    response_delay: float = 0.0
    accept_draw: float = 0.0


@dataclass
class Scenario:
    config: ScenarioConfig
    seed: int
    donations: List[SimDonation]
    recipients: List[Recipient]
    events: List[dict] = field(default_factory=list)


def _point(rng, center, radius_km):
    r = radius_km * np.sqrt(rng.random())
    th = rng.random() * 2 * np.pi
    dlat = (r * np.sin(th)) / 111.0
    dlon = (r * np.cos(th)) / (111.0 * np.cos(np.radians(center[0])))
    return (float(center[0] + dlat), float(center[1] + dlon))


def generate_scenario(cfg: ScenarioConfig, seed: int) -> Scenario:
    rng = np.random.default_rng(seed)
    dons: List[SimDonation] = []
    for i in range(cfg.n_donations):
        cat = str(rng.choice(cfg.categories))
        stor = str(rng.choice(cfg.storage_conditions))
        pack = str(rng.choice(list(ET.PACKAGING_FACTOR)))
        temp = ET.STORAGE_DEFAULT_TEMP.get(stor, 25.0) + rng.normal(0, 2.5)
        life = ET.BASE_LIFE_H.get(cat, 6.0) * 2.0 ** ((ET.T_REF - temp) / 10.0) * ET.STORAGE_FACTOR[stor] \
            * ET.PACKAGING_FACTOR[pack] * rng.lognormal(0, 0.15)
        elapsed = rng.uniform(0.1, 1.0) * min(life, 24.0)
        true_usable = max(12.0, (life - elapsed) * 60.0)
        est = true_usable * rng.lognormal(0, cfg.estimate_noise)
        qty = float(np.round(rng.uniform(cfg.qty_min, cfg.qty_max)))
        urgency = float(np.clip(1.0 - est / 360.0 + rng.normal(0, 0.1), 0, 1))
        d = Donation(f"D{i:03d}", cat, qty, _point(rng, cfg.city_center, cfg.city_radius_km),
                     float(rng.uniform(*cfg.deadline_min_range)), float(est), urgency)
        dons.append(SimDonation(d, float(rng.uniform(0, cfg.horizon_min)), float(true_usable),
                                float(rng.uniform(*cfg.response_delay_range)), float(rng.random())))
    dons.sort(key=lambda s: s.arrival_min)
    total_supply = sum(s.donation.quantity for s in dons)
    raw = rng.lognormal(0, 0.6, cfg.n_recipients)
    demand = raw / raw.sum() * total_supply * cfg.demand_supply_ratio
    recs: List[Recipient] = []
    for j in range(cfg.n_recipients):
        k = int(rng.integers(3, max(4, len(cfg.categories)) + 1))
        accepted = [ANY_CATEGORY] if rng.random() < 0.25 else list(rng.choice(cfg.categories, size=min(k, len(cfg.categories)), replace=False))
        hist = float(rng.lognormal(4.0, 1.0))
        recs.append(Recipient(
            f"R{j:02d}", f"Recipient {j:02d}", _point(rng, cfg.city_center, cfg.city_radius_km),
            float(np.round(demand[j])), float(np.round(demand[j] * rng.uniform(*cfg.capacity_factor_range))),
            [str(a) for a in accepted], bool(rng.random() < 0.92), float(rng.uniform(0, 30)),
            float(np.round(hist)), int(rng.poisson(hist / 50.0)), float(rng.choice([1.0, 1.0, 1.0, 2.0]))))
    sc = Scenario(cfg, seed, dons, recs)
    sc.events = _generate_events(cfg, rng, recs)
    return sc


def _generate_events(cfg: ScenarioConfig, rng, recs) -> List[dict]:
    ev = []
    for _ in range(cfg.n_demand_events):
        ev.append({"t": float(rng.uniform(0, cfg.horizon_min)), "type": "demand_change",
                   "recipient": recs[int(rng.integers(len(recs)))].id, "factor": float(rng.choice([0.3, 0.5, 1.5, 2.0]))})
    for _ in range(cfg.n_unavailable_events):
        t = float(rng.uniform(0, cfg.horizon_min))
        rid = recs[int(rng.integers(len(recs)))].id
        ev.append({"t": t, "type": "unavailable", "recipient": rid})
        ev.append({"t": t + float(rng.uniform(*cfg.unavailable_duration_min)), "type": "available", "recipient": rid})
    return sorted(ev, key=lambda e: e["t"])


def options_from(cfg: ScenarioConfig, **kw) -> MatchingOptions:
    return MatchingOptions(max_radius_km=cfg.max_radius_km, travel=TravelModel(cfg.speed_kmph, cfg.detour_factor), **kw)


Strategy = Callable[[Donation, List[Recipient], MatchingOptions], object]

STRATEGIES: Dict[str, Callable] = {
    "A_nearest_recipient": lambda d, r, o: nr.allocate(d, r, o),
    "B_rule_based": lambda d, r, o: rb.allocate(d, r, o),
    "C_dynamic_multi_factor": lambda d, r, o: dm.allocate(d, r, o),
}


def run_online(scenario: Scenario, strategy: Strategy, opts: Optional[MatchingOptions] = None,
               truth_enforce_capacity: bool = True) -> Dict[str, float]:
    """Process donations in arrival order; plan with the (estimate-based) engine view, execute against truth."""
    cfg = scenario.config
    opts = opts or options_from(cfg)
    t_run = time.perf_counter()
    plan = {r.id: deepcopy(r) for r in scenario.recipients}
    truth_demand = {r.id: r.demand_remaining for r in scenario.recipients}
    truth_cap = {r.id: r.capacity for r in scenario.recipients}
    initial_demand = dict(truth_demand)
    delivered = {r.id: 0.0 for r in scenario.recipients}
    donated = delivered_total = km_w = match_time = 0.0
    for sd in scenario.donations:
        d = sd.donation
        donated += d.quantity
        t0 = time.perf_counter()
        res = strategy(d, list(plan.values()), opts)
        match_time += time.perf_counter() - t0
        for a in res.allocations:
            r = plan[a.recipient_id]
            r.demand_remaining -= a.quantity
            r.capacity -= a.quantity
            r.allocation_count += 1
            r.historical_received += a.quantity
            ok = a.delivery_eta_min <= sd.true_usable_min and a.pickup_eta_min <= d.pickup_deadline_min
            if not ok:
                continue
            take = min(a.quantity, truth_demand[a.recipient_id])
            if truth_enforce_capacity:
                take = min(take, truth_cap[a.recipient_id])
            take = max(0.0, take)
            truth_demand[a.recipient_id] -= take
            truth_cap[a.recipient_id] -= take
            delivered[a.recipient_id] += take
            delivered_total += take
            km_w += take * a.distance_km
    return summarize_run(donated, delivered, initial_demand, km_w, delivered_total, match_time,
                         time.perf_counter() - t_run, len(scenario.donations))
