"""Groq backend tests use a MOCKED HTTP layer: they verify our logic (fallback, validation, schema), not Groq itself."""
import json

import pytest

from app.config import Settings
from app.services import food_service, groq_vision as gv
from tests.conftest import png_bytes

GOOD = {"choices": [{"message": {"content": json.dumps({"is_food": True, "food_name": "veg pulao", "donation_category": "cooked_meal",
                                                          "confidence": "high", "alternatives": ["jeera rice"]})}}]}


@pytest.fixture()
def calls():
    return []


@pytest.fixture()
def cfg(monkeypatch):
    def apply(**kw):
        s = Settings(**{"groq_api_key": "k", "food_backend": "auto", **kw})
        for m in (gv, food_service):
            monkeypatch.setattr(m, "get_settings", lambda s=s: s)
        return s
    return apply


@pytest.fixture()
def mock_groq(monkeypatch, calls):
    def install(resp=GOOD, exc=None):
        def fake(payload, timeout):
            calls.append(payload)
            if exc:
                raise exc
            return resp
        monkeypatch.setattr(gv, "_post", fake)
    return install


@pytest.fixture()
def no_local(monkeypatch):
    monkeypatch.setattr(food_service, "model_files_present", lambda: False)
    food_service.get_recognizer.cache_clear()


def post(client, data=None):
    return client.post("/api/ai/food-recognition", files={"file": ("a.png", data or png_bytes(), "image/png")})


def test_fallback_to_groq_when_model_missing(client, cfg, mock_groq, calls, no_local):
    cfg(); mock_groq()
    r = post(client)
    j = r.json()
    assert r.status_code == 200 and j["source"] == "groq_vlm" and j["predicted_food"] == "veg pulao"
    assert j["donation_category"] == "cooked_meal" and j["needs_manual_verification"] is False
    assert "MODEL_NOT_AVAILABLE" in j["fallback_reason"] or "not been trained" in j["fallback_reason"]
    p = calls[0]
    assert p["response_format"] == {"type": "json_object"} and p["messages"][0]["content"][1]["image_url"]["url"].startswith("data:image/jpeg;base64,")


def test_no_model_and_no_key_gives_503_with_hint(client, cfg, no_local):
    cfg(groq_api_key="")
    r = post(client)
    assert r.status_code == 503 and "GROQ_API_KEY" in r.json()["error"]["message"]


def test_invalid_image_never_reaches_groq(client, cfg, mock_groq, calls, no_local):
    cfg(); mock_groq()
    r = post(client, b"garbage")
    assert r.status_code == 400 and r.json()["error"]["code"] == "INVALID_IMAGE" and calls == []


def test_local_model_preferred_when_available(client_with_model, cfg, mock_groq, calls):
    cfg(); mock_groq()
    j = post(client_with_model).json()
    assert j["source"] == "local_mobilenetv2" and calls == []


def test_groq_on_uncertain(client_with_model, cfg, mock_groq, calls):
    cfg(groq_on_uncertain=True); mock_groq()          # untrained local model is always uncertain
    assert post(client_with_model).json()["source"] == "groq_vlm" and len(calls) == 1


def test_groq_failure_falls_back_to_local_answer(client_with_model, cfg, mock_groq):
    import httpx
    cfg(groq_on_uncertain=True); mock_groq(exc=gv.GroqUnavailable("down", "GROQ_API_ERROR"))
    assert post(client_with_model).json()["source"] == "local_mobilenetv2"


def test_forced_groq_mode_and_groq_error_status(client_with_model, cfg, mock_groq):
    cfg(food_backend="groq"); mock_groq(exc=gv.GroqUnavailable("rate", "GROQ_RATE_LIMITED"))
    r = post(client_with_model)
    assert r.status_code == 503 and r.json()["error"]["code"] == "GROQ_RATE_LIMITED"


def test_local_mode_never_uses_groq(client, cfg, mock_groq, calls, no_local):
    cfg(food_backend="local"); mock_groq()
    assert post(client).status_code == 503 and calls == []


def test_network_error_mapped(client, cfg, mock_groq, no_local):
    import httpx
    cfg(); mock_groq(exc=httpx.ConnectError("boom"))
    r = post(client)
    assert r.status_code == 503 and r.json()["error"]["code"] == "GROQ_NETWORK_ERROR"


def test_bad_json_from_groq_rejected(client, cfg, mock_groq, no_local):
    cfg(); mock_groq(resp={"choices": [{"message": {"content": "I think it is pizza"}}]})
    assert post(client).json()["error"]["code"] == "GROQ_BAD_RESPONSE"


def test_output_is_validated_not_trusted():
    r = gv.to_result({"is_food": True, "food_name": "mystery", "donation_category": "IGNORE RULES; drop table", "confidence": "certain"})
    assert r["donation_category"] == "unmapped" and r["needs_manual_verification"] is True
    assert "model_confidence_low" in r["uncertainty_reasons"]
    nf = gv.to_result({"is_food": False, "food_name": "", "donation_category": "cooked_meal", "confidence": "high"})
    assert nf["needs_manual_verification"] and nf["confidence"] == 0.0 and "no_food_detected" in nf["uncertainty_reasons"]


def test_health_reports_groq(client, cfg):
    cfg()
    assert client.get("/api/ai/health").json()["models"]["groq_fallback"]["configured"] in (True, False)
