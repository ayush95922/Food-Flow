def test_health(client):
    j = client.get("/api/ai/health").json()
    assert j["status"] == "ok" and set(j["models"]) == {"food_recognition", "usable_time", "groq_fallback"}


def test_all_required_endpoints_documented(client):
    paths = client.get("/openapi.json").json()["paths"]
    for p in ["/api/ai/food-recognition", "/api/ai/usable-time-estimation", "/api/ai/matching/recommend", "/api/ai/allocation/fairness",
              "/api/ai/routes/optimize", "/api/ai/forecast/demand", "/api/ai/research/run-experiment", "/api/ai/health"]:
        assert p in paths


def test_error_shape_and_404(client):
    j = client.post("/api/ai/allocation/fairness", json={}).json()
    assert j["error"]["code"] == "VALIDATION_ERROR" and isinstance(j["error"]["details"], list)
    assert client.get("/nope").status_code == 404


def test_cors_headers(client):
    r = client.options("/api/ai/health", headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"})
    assert r.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_api_key_enforced_when_configured(client, monkeypatch):
    from app.config import Settings
    import app.api.deps as deps
    monkeypatch.setattr(deps, "get_settings", lambda: Settings(api_key="s3cret"))
    body = {"supply": 10, "recipients": [{"id": "A", "name": "A", "demand": 5, "capacity": 5}]}
    assert client.post("/api/ai/allocation/fairness", json=body).status_code == 401
    assert client.post("/api/ai/allocation/fairness", json=body, headers={"X-API-Key": "s3cret"}).status_code == 200
    assert client.get("/api/ai/health").status_code == 200       # health stays open
