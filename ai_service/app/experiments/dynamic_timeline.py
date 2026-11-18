"""Dynamic timeline simulation: static one-shot allocation vs event-driven re-matching.

Both modes use the SAME proposed matcher (dynamic multi-factor). They differ only in how they react to events:
  static  : an allocation is decided when the donation arrives and is never revised. Rejections, recipients
            that become unavailable and demand drops are only discovered at delivery time (food is lost).
  dynamic : on every event (new donation, demand change, recipient unavailable/available, allocation rejected)
            proposals that are no longer valid are withdrawn and re-matched, and donations that found no
            recipient wait in a queue and are retried while their pickup/usable windows remain.
Event types: donation arrival, demand_change, unavailable, available, recipient response (accept / reject),
delivery. Once a recipient has accepted, the food is in transit and can no longer be re-routed (both modes).
Truth is checked at delivery time: recipient available, pickup deadline, TRUE usable time, remaining demand, capacity.
All inputs are synthetic (see simulator.py).
"""
import heapq
import time
from dataclasses import replace
from typing import Dict, List, Optional

import numpy as np

from app.algorithms import dynamic_matching as dm
from app.experiments.metrics import summarize_run
from app.experiments.simulator import Scenario, options_from


def run_timeline(scenario: Scenario, mode: str, weights: Optional[dm.Weights] = None) -> Dict[str, float]:
    assert mode in ("static", "dynamic")
    cfg, opts = scenario.config, options_from(scenario.config)
    t_run, match_time = time.perf_counter(), 0.0
    rec = {r.id: r for r in scenario.recipients}
    base = {rid: r.demand_remaining for rid, r in rec.items()}
    cap_total = {rid: r.capacity for rid, r in rec.items()}
    factor = {rid: 1.0 for rid in rec}
    got = {rid: 0.0 for rid in rec}
    avail = {rid: r.available for rid, r in rec.items()}
    n_alloc = {rid: r.allocation_count for rid, r in rec.items()}
    reserved = {rid: 0.0 for rid in rec}
    allocs: Dict[int, dict] = {}
    waiting: List[dict] = []
    excluded: Dict[str, set] = {}
    acc_rng = np.random.default_rng(scenario.seed + 999)
    counters = {"rejections": 0, "rematches": 0, "failed_delivery_qty": 0.0}
    delivered_total = km_w = 0.0
    heap, seq = [], 0

    def push(t, kind, payload):
        nonlocal seq
        heapq.heappush(heap, (t, seq, kind, payload))
        seq += 1

    for sd in scenario.donations:
        push(sd.arrival_min, "donation", sd)
    for e in scenario.events:
        push(e["t"], e["type"], e)

    def view(excl):
        out = []
        for rid, r in rec.items():
            if rid in excl:
                continue
            out.append(replace(r, demand_remaining=max(0.0, base[rid] * factor[rid] - got[rid] - reserved[rid]),
                               capacity=max(0.0, cap_total[rid] - got[rid] - reserved[rid]), available=avail[rid],
                               available_in_min=0.0, historical_received=r.historical_received + got[rid],
                               allocation_count=n_alloc[rid]))
        return out

    def plan(t, sd, qty):
        nonlocal match_time
        d0 = sd.donation
        age = t - sd.arrival_min
        dl = d0.pickup_deadline_min - age - sd.response_delay
        us = d0.remaining_usable_min - age - sd.response_delay
        if dl <= 0 or us <= 0 or qty < opts.min_chunk:
            return qty, False                            # window closed
        d = replace(d0, quantity=qty, pickup_deadline_min=dl, remaining_usable_min=us)
        t0 = time.perf_counter()
        res = dm.allocate(d, view(excluded.get(d0.id, set())), opts, weights)
        match_time += time.perf_counter() - t0
        for a in res.allocations:
            aid = len(allocs)
            allocs[aid] = {"sd": sd, "rid": a.recipient_id, "qty": a.quantity, "state": "proposed", "a": a,
                           "t": t, "draw": float(acc_rng.random())}
            reserved[a.recipient_id] += a.quantity
            n_alloc[a.recipient_id] += 1
            push(t + sd.response_delay, "response", aid)
        return res.unallocated_qty, True

    def handle_leftover(t, sd, left, still_open):
        if left >= opts.min_chunk and still_open and mode == "dynamic":
            waiting.append({"sd": sd, "qty": left})

    def retry_waiting(t):
        items, waiting[:] = waiting[:], []
        for w in items:
            left, open_ = plan(t, w["sd"], w["qty"])
            handle_leftover(t, w["sd"], left, open_)

    def withdraw(aid):
        a = allocs[aid]
        a["state"] = "cancelled"
        reserved[a["rid"]] -= a["qty"]
        n_alloc[a["rid"]] -= 1
        return a

    def rematch(t, cancelled: List[dict]):
        for a in cancelled:
            counters["rematches"] += 1
            excluded.setdefault(a["sd"].donation.id, set()).add(a["rid"])
            left, open_ = plan(t, a["sd"], a["qty"])
            handle_leftover(t, a["sd"], left, open_)

    while heap:
        t, _, kind, p = heapq.heappop(heap)
        if kind == "donation":
            left, open_ = plan(t, p, p.donation.quantity)
            handle_leftover(t, p, left, open_)
        elif kind == "response":
            a = allocs[p]
            if a["state"] != "proposed":
                continue
            if a["draw"] < cfg.accept_prob:
                a["state"] = "in_transit"
                push(t + a["a"].delivery_eta_min, "delivery", p)
            else:
                counters["rejections"] += 1
                withdraw(p)
                if mode == "dynamic":
                    rematch(t, [a])
        elif kind == "delivery":
            a = allocs[p]
            sd, rid = a["sd"], a["rid"]
            reserved[rid] -= a["qty"]
            a["state"] = "done"
            pickup_abs = a["t"] + sd.response_delay + a["a"].pickup_eta_min
            ok = (avail[rid] and pickup_abs <= sd.arrival_min + sd.donation.pickup_deadline_min
                  and t <= sd.arrival_min + sd.true_usable_min)
            take = max(0.0, min(a["qty"], base[rid] * factor[rid] - got[rid], cap_total[rid] - got[rid])) if ok else 0.0
            counters["failed_delivery_qty"] += a["qty"] - take
            got[rid] += take
            delivered_total += take
            km_w += take * a["a"].distance_km
        elif kind == "demand_change":
            factor[p["recipient"]] = p["factor"]
            if mode == "dynamic":
                rid, cancelled = p["recipient"], []
                for aid in sorted((i for i, x in allocs.items() if x["rid"] == rid and x["state"] == "proposed"), reverse=True):
                    if reserved[rid] <= max(0.0, base[rid] * factor[rid] - got[rid]) + 1e-9:
                        break
                    cancelled.append(withdraw(aid))
                rematch(t, cancelled)
                retry_waiting(t)
        elif kind == "unavailable":
            avail[p["recipient"]] = False
            if mode == "dynamic":
                rematch(t, [withdraw(i) for i, x in list(allocs.items()) if x["rid"] == p["recipient"] and x["state"] == "proposed"])
        elif kind == "available":
            avail[p["recipient"]] = True
            if mode == "dynamic":
                retry_waiting(t)

    donated = sum(s.donation.quantity for s in scenario.donations)
    final_demand = {rid: base[rid] * factor[rid] for rid in rec}
    return summarize_run(donated, got, final_demand, km_w, delivered_total, match_time, time.perf_counter() - t_run,
                         len(scenario.donations), extra=counters)
