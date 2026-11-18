"""Generate docs/API.md with REAL request/response pairs captured from the running app (TestClient)."""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from fastapi.testclient import TestClient
from app.main import app
c = TestClient(app)

def trunc(o, n=70):
    s = json.dumps(o, indent=2)
    L = s.split("\n")
    return s if len(L) <= n else "\n".join(L[:n]) + "\n  ... (truncated)"

rec = {"id": "NGO-A", "name": "NGO A", "location": {"lat": 22.73, "lon": 75.87}, "demand_remaining": 80, "capacity": 100,
       "accepted_categories": ["cooked_meal"], "historical_received": 500, "allocation_count": 5}
calls = [
 ("GET", "/api/ai/health", None, "Service and model status."),
 ("POST", "/api/ai/usable-time-estimation", {"food_category": "cooked_meal", "food_type": "veg pulao", "elapsed_minutes": 90, "storage_condition": "room_temp", "temperature_c": 28, "packaging": "covered"}, "Experimental estimate; trained on SYNTHETIC data."),
 ("POST", "/api/ai/matching/recommend", {"donations": [{"id": "D-101", "food_category": "cooked_meal", "quantity": 100, "location": {"lat": 22.72, "lon": 75.86}, "pickup_deadline_minutes": 120, "remaining_usable_minutes": 240}],
   "recipients": [rec, {**rec, "id": "NGO-B", "name": "NGO B", "location": {"lat": 22.78, "lon": 75.90}, "demand_remaining": 150, "capacity": 200, "accepted_categories": ["any"], "historical_received": 20, "allocation_count": 1}],
   "strategy": "dynamic", "options": {"top_n": 3}}, "Rank feasible recipients, propose allocations, explain them."),
 ("POST", "/api/ai/allocation/fairness", {"supply": 150, "recipients": [{"id": "A", "name": "A", "demand": 100, "capacity": 100, "historical_received": 500, "allocation_count": 10}, {"id": "B", "name": "B", "demand": 100, "capacity": 100, "historical_received": 0}, {"id": "C", "name": "C", "demand": 100, "capacity": 100, "historical_received": 100, "allocation_count": 2, "priority": 2}]}, "Weighted max-min allocation vs proportional / FCFS."),
 ("POST", "/api/ai/routes/optimize", {"volunteer_location": {"lat": 22.72, "lon": 75.82}, "destination": {"lat": 22.75, "lon": 75.88}, "pickups": [{"id": f"P{i}", "location": {"lat": 22.70 + i * 0.012, "lon": 75.79 + (i % 3) * 0.02}, "deadline_minutes": 40 + 15 * i, "urgency": 0.5, "quantity": 20} for i in range(5)]}, "SIMULATED routing (no road graph supplied)."),
 ("POST", "/api/ai/forecast/demand", {"records": [{"date": "2026-01-01", "supply_qty": 100, "demand_qty": 120}], "horizon_days": 7}, "With too little history the service reports the missing-data requirement and fabricates nothing."),
 ("POST", "/api/ai/research/run-experiment", {"config": {"n_donations": 12, "n_recipients": 5}, "n_seeds": 2, "experiments": ["baselines"]}, "Synthetic simulation (small run shown)."),
]
md = ["# API reference with real captured examples\n",
      "Interactive docs: `/docs` (Swagger UI) and `/redoc`. All errors use `{\"error\": {\"code\", \"message\", \"details\"}}`. "
      "Optional auth header `X-API-Key` when `API_KEY` is set. Fields are `snake_case` (Spring Boot: `spring.jackson.property-naming-strategy=SNAKE_CASE`).\n",
      "Status codes: 200 OK, 400 unreadable image, 401 bad API key, 413 file too large, 415 unsupported type, 422 validation/insufficient input, 503 model not installed, 500 unexpected.\n"]
for m, p, body, desc in calls:
    r = c.get(p) if m == "GET" else c.post(p, json=body)
    md.append(f"\n## {m} {p}\n{desc}\n\n**Request**\n```json\n{trunc(body) if body else '(none)'}\n```\n**Response {r.status_code}** (captured from this build)\n```json\n{trunc(r.json())}\n```")
md.append("""
## POST /api/ai/food-recognition  (multipart/form-data, field `file`)
```bash
curl -X POST http://localhost:8000/api/ai/food-recognition -F "file=@pizza.jpg;type=image/jpeg"
```
Requires the trained model in `saved_models/food_classifier/`. **Illustrative response format** (this is NOT a real model output - the classifier has not been trained in the delivery environment):
```json
{"status": "ok", "predicted_label": "pizza", "predicted_food": "pizza", "food_category": "pizza",
 "donation_category": "ready_to_eat_snack", "category_needs_review": false, "confidence": 0.0,
 "top_predictions": [{"label": "...", "display_name": "...", "confidence": 0.0}, "... 3 entries ..."],
 "needs_manual_verification": true, "uncertainty_reasons": ["low_confidence"],
 "confidence_note": "...", "disclaimer": "...", "manual_correction_allowed": true}
```
Without the model: `503 {"error": {"code": "MODEL_NOT_AVAILABLE", ...}}`.

## POST /api/ai/food-recognition/correct
```json
{"original_result": {"...": "JSON returned above"}, "corrected_food": "Veg pulao", "corrected_donation_category": "cooked_meal"}
```
Returns the result with `user_correction`, `verified_by_donor: true`, `needs_manual_verification: false`. Persisting corrections is the Java backend's job.

## Spring Boot client sketch
```java
RestClient ai = RestClient.builder().baseUrl("http://ai-service:8000").defaultHeader("X-API-Key", key).build();
MatchingResponse r = ai.post().uri("/api/ai/matching/recommend").body(req).retrieve().body(MatchingResponse.class);
// image: MultipartBodyBuilder -> ai.post().uri("/api/ai/food-recognition").contentType(MULTIPART_FORM_DATA)...
```
""")
(ROOT / "docs" / "API.md").write_text("\n".join(md))
print("wrote docs/API.md")
