from app.algorithms.route_optimizer import DistanceProvider, Pickup, RoadGraph, compare_routes
from app.utils.errors import ValidationFailed


def _res(r) -> dict:
    return {"algorithm": r.algorithm, "visit_order": r.order, "completed_pickups": r.completed, "missed_deadline": r.missed,
            "unserved": r.unserved, "expired_en_route": r.expired_en_route,
            "total_distance_km": r.total_distance_km, "estimated_total_time_minutes": r.total_time_min,
            "destination_arrival_minutes": r.destination_arrival_min, "completed_count": len(r.completed),
            "completed_quantity": r.completed_quantity, "arrival_times_minutes": {k: round(v, 2) for k, v in r.arrival_times.items()},
            "legs": r.legs}


def optimize(req) -> dict:
    graph = None
    if req.mode == "graph":
        g = req.road_graph
        nodes = {n.id: (n.lat, n.lon) for n in g.nodes}
        try:
            graph = RoadGraph(nodes, [(e.u, e.v, e.distance_km) for e in g.edges], g.algorithm)
        except ValueError as e:
            raise ValidationFailed(str(e))
    dp = DistanceProvider(req.speed_kmph, req.detour_factor, graph)
    pk = [Pickup(p.id, p.location.t(), p.deadline_minutes, p.urgency, p.quantity, p.service_minutes, p.usable_minutes) for p in req.pickups]
    res = compare_routes(req.volunteer_location.t(), req.destination.t(), pk, dp, req.include_optimal_reference)
    out = {"mode": dp.mode, "routes": {k: _res(v) for k, v in res.items()}}
    nn, im = res["nearest_neighbor"], res["improved"]
    out["comparison"] = {"distance_saved_km": round(nn.total_distance_km - im.total_distance_km, 3),
                         "time_saved_minutes": round(nn.total_time_min - im.total_time_min, 2),
                         "extra_completed_pickups": len(im.completed) - len(nn.completed)}
    if "optimal_reference" in res:
        out["comparison"]["improved_completed_vs_optimal"] = f"{len(im.completed)}/{len(res['optimal_reference'].completed)}"
    out["assumptions"] = ["SIMULATED travel estimates" if dp.mode == "simulated" else
                          f"Distances from the supplied road graph via {req.road_graph.algorithm}; points snapped to nearest node.",
                          "A pickup is completed only if the volunteer arrives before its deadline (and food is usable at the destination if usable_minutes is given).",
                          "optimal_reference is exhaustive search and only runs for <= 7 pickups."]
    return out
