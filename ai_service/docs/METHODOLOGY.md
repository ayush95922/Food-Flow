# Research methodology, formulas and assumptions

## 1. Travel model (SIMULATED)
road_km = haversine(a,b) × δ (δ=1.3, assumed); minutes = km / v × 60 (v=25 km/h, assumed). With a supplied road graph, distances are Dijkstra/A* shortest paths (points snapped to nearest node); the A* heuristic is scaled by min(edge/haversine) so it stays admissible.
Collection model: recipient team becomes free after `available_in`, travels to donor (pickup ETA P) and returns (delivery ETA E = P + travel).

## 2. Hard feasibility constraints (all strategies)
available; category accepted; demand>0; capacity>0 (switchable); distance ≤ R_max; P ≤ pickup deadline; E ≤ estimated usable time (switchable). Infeasible recipients are rejected with explicit reasons.

## 3. Strategies
A **Nearest**: ascending distance. B **Rule-based**: 0.40·dist + 0.35·demand + 0.25·quantity. C **Proposed dynamic multi-factor** (simple additive weighting, *not ML*):
score = Σ w_k s_k / Σ w_k with s ∈ [0,1]:
demand = d_i/max d; quantity = min(q,a_i)/q (a_i=min(demand,capacity)); distance = 1−D/R; urgency = u·(1−P/T_p); usable_time = (T_u−E)/T_u; capacity = min(1,cap/q); compatibility = 1 exact, 0.7 wildcard; pickup_feasibility = 1−P/T_p; fairness = ½(1−rec/max rec)+½(1−freq/max freq) with rec = history/priority.
Default weights (sum 1): demand .15, quantity .10, distance .12, urgency .10, usable_time .10, capacity .08, compatibility .08, pickup .12, fairness .15 — design choices, **not tuned**; sensitivity analysis is future work.
Allocation: greedy, ≤3 chunks, re-ranking after each chunk with reduced demand/capacity; never exceeds donation or recipient acceptable quantity.
Urgency if not given: u = 1 − min(1, T_u/360 min).

## 4. Fairness allocation
Weighted max-min (water-filling): x_i = clip(p_i·L − h_i, 0, c_i), Σx = min(S, Σc), h_i = history + λ·count (λ=5 portions, assumed), c_i = min(demand, capacity). Jain J=(Σy)²/(nΣy²) on fulfilment x/d and on cumulative (h+x)/p; also Gini, unmet demand, min/max fulfilment. Compared with demand-proportional and FCFS. Explanations state each recipient's history rank and level.

## 5. Routing
Nearest-neighbour baseline (ignores deadlines, drives everywhere) vs improved heuristic (multi-start: deadline-aware insertion ×2, EDF order, NN order; 2-opt + relocate local search; objective = urgency-weighted completed pickups, then time; late stops are skipped) vs exhaustive optimum (≤7 stops) as reference. Completed = arrive before deadline and (if given) food still usable at destination.

## 6. Usable-time regression (SYNTHETIC)
life = base[cat]·2^((20−T)/10)·storage·packaging·LogNormal(0,0.15), remaining = max(0,life−elapsed); base hours are assumptions (not validated limits). Features: elapsed, temperature (imputed from storage default), elapsed/base ratio, category, storage, packaging (mode-imputed). Models: Linear, Random Forest, Gradient Boosting; 70/15/15 split; selection by validation RMSE; interval = q90 of validation |residual|. The learners recover the generator, so high R² ≠ real accuracy.

## 7. Forecasting
Needs ≥56 daily records. Baselines: naive, 7-day moving average, seasonal-naive; ML: linear/RF on lag1/7/14, rolling mean, weekday, trend; Holt-Winters. Chronological 70/15/15, walk-forward 7-day blocks, MAE/RMSE/sMAPE/MASE, selection by validation MAE, band ±1.645·val-RMSE.

## 8. Simulation
Synthetic city (disc, 8 km), lognormal demand scaled to ratio×supply, capacity = demand×U(0.5,1.2), lognormal history, true usable time from §6 model, engine sees truth×LogNormal(0,0.15). Donations processed online; execution judged on truth (deadline, true usable time, true demand, capacity). Metrics: donated, redistributed, wastage, unmet demand, beneficiaries (1 portion = 1 meal), recipients served, mean km (quantity-weighted), Jain on delivered/initial-demand, matching time, total time. Seeds 0–29, paired Wilcoxon tests (no multiple-comparison correction).
Ablations remove one factor's weight; "without usable time" also drops the usable-time constraint and "without capacity" drops the capacity cap (still enforced at execution).
Dynamic timeline: events = donation arrival, demand change, unavailable/available, accept/reject, delivery. Static = decide once; dynamic = withdraw invalid proposals and re-match, queue unmatched donations and retry.
