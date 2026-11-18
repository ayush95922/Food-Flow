import random

import pytest

from app.algorithms.route_optimizer import (DistanceProvider, Pickup, RoadGraph, compare_routes, improved_route,
                                            nearest_neighbor, optimal_route, simulate)

START, DEST = (22.72, 75.82), (22.75, 75.88)


def instance(seed, n=6, tight=1.0):
    rnd = random.Random(seed)
    return [Pickup(f"P{i}", (22.68 + rnd.random() * 0.1, 75.78 + rnd.random() * 0.12), rnd.uniform(25, 120) * tight, rnd.random(), 10) for i in range(n)]


def test_improved_has_no_missed_deadlines_and_valid_route():
    dp = DistanceProvider()
    for s in range(15):
        pk = {p.id: p for p in instance(s, 7, 0.6)}
        r = improved_route(START, DEST, pk, dp)
        assert r.missed == [] and set(r.order) <= set(pk) and len(set(r.order)) == len(r.order)
        assert set(r.completed) == set(r.order)
        assert set(r.unserved) == set(pk) - set(r.order)


def test_improved_not_worse_than_nearest_neighbour_on_completed_pickups():
    dp = DistanceProvider()
    worse = 0
    for s in range(30):
        pk = {p.id: p for p in instance(s, 6, 0.5)}
        nn, im = nearest_neighbor(START, DEST, pk, dp), improved_route(START, DEST, pk, dp)
        worse += len(im.completed) < len(nn.completed)
    assert worse == 0


def test_close_to_exact_optimum_on_small_instances():
    dp = DistanceProvider()
    gaps = []
    for s in range(12):
        pk = {p.id: p for p in instance(s, 6, 0.6)}
        im, opt = improved_route(START, DEST, pk, dp), optimal_route(START, DEST, pk, dp)
        assert len(im.completed) <= len(opt.completed)           # optimum is an upper bound
        gaps.append(len(opt.completed) - len(im.completed))
    assert sum(gaps) <= 3                                          # heuristic is rarely off (documented, not guaranteed)


def test_loose_deadlines_distance_not_worse_than_nn():
    dp = DistanceProvider()
    pk = {p.id: p for p in instance(5, 7, 100)}
    assert improved_route(START, DEST, pk, dp).total_distance_km <= nearest_neighbor(START, DEST, pk, dp).total_distance_km + 1e-9


def test_simulate_deadline_logic():
    dp = DistanceProvider(speed_kmph=30)
    pk = {"A": Pickup("A", (22.72, 75.82), 5), "B": Pickup("B", (22.90, 75.82), 5)}     # B ~ 20+ km away
    r = simulate("t", START, DEST, pk, ["A", "B"], dp)
    assert "A" in r.completed and "B" in r.missed


def test_usable_time_at_destination_counts():
    dp = DistanceProvider()
    pk = {"A": Pickup("A", (22.72, 75.83), 60, usable_min=1)}
    r = simulate("t", START, DEST, pk, ["A"], dp)
    assert r.expired_en_route == ["A"] and r.completed == []


def grid(n=5, step=0.01):
    nodes = {f"{i}-{j}": (22.7 + i * step, 75.8 + j * step) for i in range(n) for j in range(n)}
    from app.utils.geo import haversine_km
    edges = [(a, b, haversine_km(nodes[a], nodes[b]) * 1.2) for a in nodes for b in nodes
             if a < b and abs(int(a[0]) - int(b[0])) + abs(int(a[2]) - int(b[2])) == 1]
    return nodes, edges


def test_dijkstra_equals_astar_and_matches_known_graph():
    nodes, edges = grid()
    d, a = RoadGraph(nodes, edges, "dijkstra"), RoadGraph(nodes, edges, "astar")
    for u, v in [("0-0", "4-4"), ("0-3", "3-0"), ("2-2", "2-2")]:
        assert d.node_distance(u, v) == pytest.approx(a.node_distance(u, v))
    tiny = RoadGraph({"a": (0, 0), "b": (0, 0.01), "c": (0, 0.02)}, [("a", "b", 1.0), ("b", "c", 2.0), ("a", "c", 10.0)])
    assert tiny.node_distance("a", "c") == pytest.approx(3.0)


def test_graph_mode_and_api(client):
    nodes, edges = grid()
    body = {"volunteer_location": {"lat": 22.70, "lon": 75.80}, "destination": {"lat": 22.74, "lon": 75.84}, "mode": "graph",
            "pickups": [{"id": "P1", "location": {"lat": 22.72, "lon": 75.81}, "deadline_minutes": 90},
                        {"id": "P2", "location": {"lat": 22.73, "lon": 75.83}, "deadline_minutes": 90}],
            "road_graph": {"nodes": [{"id": k, "lat": v[0], "lon": v[1]} for k, v in nodes.items()],
                           "edges": [{"u": a, "v": b, "distance_km": w} for a, b, w in edges], "algorithm": "astar"}}
    j = client.post("/api/ai/routes/optimize", json=body).json()
    assert j["mode"] == "graph" and j["routes"]["improved"]["completed_count"] == 2
    assert client.post("/api/ai/routes/optimize", json={**body, "road_graph": None}).status_code == 422


def test_api_simulated_mode_labelled(client):
    body = {"volunteer_location": {"lat": 22.72, "lon": 75.82}, "destination": {"lat": 22.75, "lon": 75.88},
            "pickups": [{"id": f"P{i}", "location": {"lat": 22.7 + i * 0.01, "lon": 75.8 + i * 0.01}, "deadline_minutes": 90, "urgency": 0.5} for i in range(4)]}
    j = client.post("/api/ai/routes/optimize", json=body).json()
    assert j["mode"] == "simulated" and "SIMULATED" in j["assumptions"][0]
    assert set(j["routes"]) == {"nearest_neighbor", "improved", "optimal_reference"}
