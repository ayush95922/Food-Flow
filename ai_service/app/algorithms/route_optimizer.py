"""Multi-stop pickup routing for a volunteer who collects several donations and delivers to ONE recipient.

Distances are SIMULATED unless a road graph is supplied:
  * mode "simulated": road_km = haversine * detour_factor            (assumption, no real road data)
  * mode "graph"    : points are snapped to the nearest node of a supplied road graph (e.g. exported from
                      OpenStreetMap with osmnx on the Java/Colab side) and distances are shortest paths
                      computed with Dijkstra (default) or A* (haversine heuristic, scaled to stay admissible).
Algorithms
  nearest_neighbor : baseline; always drive to the closest unvisited pickup, ignores deadlines.
  improved         : deadline-aware cheapest insertion (two orderings, multi-start) + 2-opt / relocate local
                     search; pickups that cannot be served in time are reported as unserved instead of being
                     driven to pointlessly.
  optimal          : exhaustive search over visiting orders (only n <= 7) used as a reference to measure the
                     heuristic's gap; it uses the same "skip late stops" semantics as `improved`.
A pickup counts as *completed* only if (a) the volunteer arrives before its deadline and (b) the food is
still within its usable time when it reaches the destination (if `usable_min` is given).
"""
import itertools
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import networkx as nx

from app.utils.geo import haversine_km


@dataclass
class Pickup:
    id: str
    location: Tuple[float, float]
    deadline_min: float
    urgency: float = 0.5
    quantity: float = 1.0
    service_min: float = 5.0
    usable_min: Optional[float] = None


@dataclass
class RouteResult:
    algorithm: str
    order: List[str]                       # stops actually driven to (in order)
    completed: List[str]
    missed: List[str]                      # driven to but arrived after the deadline
    unserved: List[str]                    # never attempted
    expired_en_route: List[str]
    total_distance_km: float
    total_time_min: float
    destination_arrival_min: float
    arrival_times: Dict[str, float] = field(default_factory=dict)
    completed_quantity: float = 0.0
    mode: str = "simulated"
    legs: List[dict] = field(default_factory=list)


class RoadGraph:
    """Undirected road network with Dijkstra / A* shortest paths."""

    def __init__(self, nodes: Dict[str, Tuple[float, float]], edges: List[Tuple[str, str, float]],
                 algorithm: str = "dijkstra"):
        if algorithm not in ("dijkstra", "astar"):
            raise ValueError("algorithm must be 'dijkstra' or 'astar'")
        self.G = nx.Graph()
        for n, (la, lo) in nodes.items():
            self.G.add_node(n, lat=la, lon=lo)
        for u, v, w in edges:
            if u not in nodes or v not in nodes:
                raise ValueError(f"edge references unknown node: {u}-{v}")
            if w < 0:
                raise ValueError("negative edge length")
            self.G.add_edge(u, v, distance_km=float(w))
        self.nodes = nodes
        self.algorithm = algorithm
        ratios = [d["distance_km"] / max(haversine_km(nodes[u], nodes[v]), 1e-9)
                  for u, v, d in self.G.edges(data=True) if haversine_km(nodes[u], nodes[v]) > 1e-9]
        self._h_scale = min(1.0, min(ratios)) if ratios else 1.0   # keeps the A* heuristic admissible
        self._cache: Dict[Tuple[str, str], float] = {}

    def snap(self, p) -> Tuple[str, float]:
        n = min(self.nodes, key=lambda k: haversine_km(p, self.nodes[k]))
        return n, haversine_km(p, self.nodes[n])

    def node_distance(self, a: str, b: str) -> float:
        key = (a, b) if a <= b else (b, a)
        if key in self._cache:
            return self._cache[key]
        try:
            if self.algorithm == "astar":
                h = lambda u, v: self._h_scale * haversine_km(self.nodes[u], self.nodes[v])
                d = nx.astar_path_length(self.G, a, b, heuristic=h, weight="distance_km")
            else:
                d = nx.dijkstra_path_length(self.G, a, b, weight="distance_km")
        except nx.NetworkXNoPath:
            d = float("inf")
        self._cache[key] = d
        return d


class DistanceProvider:
    def __init__(self, speed_kmph=25.0, detour_factor=1.3, graph: Optional[RoadGraph] = None):
        self.speed, self.detour, self.graph = speed_kmph, detour_factor, graph
        self.mode = "graph" if graph else "simulated"

    def km(self, a, b) -> float:
        if self.graph is None:
            return haversine_km(a, b) * self.detour
        na, da = self.graph.snap(a)
        nb, db = self.graph.snap(b)
        return da + self.graph.node_distance(na, nb) + db

    def minutes(self, km: float) -> float:
        return km / self.speed * 60.0


def simulate(algorithm: str, start, dest, pickups: Dict[str, Pickup], order: List[str], dp: DistanceProvider,
             skip_late: bool = False, start_time: float = 0.0) -> RouteResult:
    """Drive through `order`. If skip_late, stops that would be reached after their deadline are skipped
    (not driven to); otherwise the volunteer drives to every stop and late arrivals are counted as missed."""
    t, pos, dist = start_time, start, 0.0
    driven, completed, missed, arrivals, legs = [], [], [], {}, []
    for pid in order:
        p = pickups[pid]
        km = dp.km(pos, p.location)
        arr = t + dp.minutes(km)
        if skip_late and arr > p.deadline_min:
            continue
        driven.append(pid)
        arrivals[pid] = arr
        legs.append({"from": "start" if not legs else driven[-2], "to": pid, "km": round(km, 3), "min": round(dp.minutes(km), 2)})
        dist += km
        if arr <= p.deadline_min:
            completed.append(pid)
            t = arr + p.service_min
        else:
            missed.append(pid)
            t = arr
        pos = p.location
    km = dp.km(pos, dest)
    dist += km
    t += dp.minutes(km)
    legs.append({"from": driven[-1] if driven else "start", "to": "destination", "km": round(km, 3), "min": round(dp.minutes(km), 2)})
    expired = [pid for pid in completed if pickups[pid].usable_min is not None and pickups[pid].usable_min < t]
    ok = [pid for pid in completed if pid not in expired]
    return RouteResult(algorithm, driven, ok, missed, [p for p in pickups if p not in driven], expired,
                       round(dist, 4), round(t - start_time, 3), round(t, 3), arrivals,
                       sum(pickups[p].quantity for p in ok), dp.mode, legs)


def _value(res: RouteResult, pickups: Dict[str, Pickup]):
    """Lexicographic objective: more (urgency-weighted) completed pickups first, then shorter time."""
    v = sum(1.0 + pickups[p].urgency for p in res.completed)
    return (v, -res.total_time_min)


def _feasible(res: RouteResult) -> bool:
    return not res.missed and not res.expired_en_route


def nearest_neighbor(start, dest, pickups: Dict[str, Pickup], dp: DistanceProvider) -> RouteResult:
    left, pos, order = set(pickups), start, []
    while left:
        nxt = min(left, key=lambda k: (dp.km(pos, pickups[k].location), k))
        order.append(nxt)
        pos = pickups[nxt].location
        left.remove(nxt)
    return simulate("nearest_neighbor", start, dest, pickups, order, dp, skip_late=False)


def _insertion(start, dest, pickups, dp, priority_order: List[str]) -> List[str]:
    """Deadline-aware cheapest insertion: only insertions that keep every stop on time are accepted."""
    route: List[str] = []
    for pid in priority_order:
        best, best_t = None, float("inf")
        for pos in range(len(route) + 1):
            cand = route[:pos] + [pid] + route[pos:]
            res = simulate("tmp", start, dest, pickups, cand, dp, skip_late=False)
            if _feasible(res) and res.total_time_min < best_t:
                best, best_t = cand, res.total_time_min
        if best is not None:
            route = best
    return route


def _local_search(start, dest, pickups, dp, order: List[str], max_iter: int = 50) -> List[str]:
    """2-opt and relocate over the FULL visiting order, evaluated with skip-late semantics, accepting a move
    only if it improves the lexicographic objective (urgency-weighted completed pickups, then total time)."""
    cur = simulate("tmp", start, dest, pickups, order, dp, skip_late=True)
    cur_v = _value(cur, pickups)
    for _ in range(max_iter):
        improved = False
        moves = []
        n = len(order)
        for i in range(n - 1):
            for j in range(i + 1, n):
                moves.append(order[:i] + order[i:j + 1][::-1] + order[j + 1:])
        for i in range(n):
            for j in range(n):
                if i != j:
                    r = order[:]
                    r.insert(j, r.pop(i))
                    moves.append(r)
        for m in moves:
            res = simulate("tmp", start, dest, pickups, m, dp, skip_late=True)
            v = _value(res, pickups)
            if v > cur_v and (v[0] > cur_v[0] + 1e-9 or v[1] > cur_v[1] + 1e-9):
                order, cur_v, improved = m, v, True
                break
        if not improved:
            break
    return order


def improved_route(start, dest, pickups: Dict[str, Pickup], dp: DistanceProvider) -> RouteResult:
    """Multi-start heuristic: seeds = deadline-aware insertion (two priority orders), earliest-deadline order and
    nearest-neighbour order; each seed is polished by local search; the best result is returned with only the
    pickups that can actually be completed (late stops are left out, not driven to)."""
    by_deadline = sorted(pickups, key=lambda k: (pickups[k].deadline_min, -pickups[k].urgency, k))
    by_priority = sorted(pickups, key=lambda k: (-pickups[k].urgency, pickups[k].deadline_min, k))
    seeds = []
    for ordr in (by_deadline, by_priority):
        ins = _insertion(start, dest, pickups, dp, ordr)
        seeds.append(ins + [p for p in ordr if p not in ins])
    seeds.append(by_deadline)
    seeds.append(nearest_neighbor(start, dest, pickups, dp).order)
    best: Optional[RouteResult] = None
    for seed in seeds:
        order = _local_search(start, dest, pickups, dp, list(seed))
        res = simulate("improved", start, dest, pickups, order, dp, skip_late=True)
        if best is None or _value(res, pickups) > _value(best, pickups):
            best = res
    return best


def optimal_route(start, dest, pickups: Dict[str, Pickup], dp: DistanceProvider, max_n: int = 7) -> Optional[RouteResult]:
    if len(pickups) > max_n:
        return None
    best = None
    for perm in itertools.permutations(pickups):
        res = simulate("optimal_reference", start, dest, pickups, list(perm), dp, skip_late=True)
        if best is None or _value(res, pickups) > _value(best, pickups):
            best = res
    return best


def compare_routes(start, dest, pickups: List[Pickup], dp: DistanceProvider, include_optimal: bool = True) -> Dict[str, RouteResult]:
    pk = {p.id: p for p in pickups}
    out = {"nearest_neighbor": nearest_neighbor(start, dest, pk, dp), "improved": improved_route(start, dest, pk, dp)}
    if include_optimal:
        opt = optimal_route(start, dest, pk, dp)
        if opt:
            out["optimal_reference"] = opt
    return out
