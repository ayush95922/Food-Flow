# Architecture
```
React  ──REST/JSON──►  Spring Boot (auth, users, donations, recipients, MySQL)  ──REST/JSON (X-API-Key)──►  FastAPI AI service
```
**Java owns** authentication, authorization, persistence, donation/recipient CRUD. **This service is stateless** and owns
image classification, usable-time estimation, matching, fairness, routing, forecasting and experiments. Java sends current
state (recipient demand/capacity/history, donation data) in each request and persists results; calling again after any change
in supply, demand or availability *is* the recalculation mechanism. `updated_recipient_states` in the matching response lets Java verify/persist state.

Layers: `api/` (HTTP, validation, status codes) → `services/` (schema↔domain conversion, model caching) → `algorithms/` (pure Python, no web/ML framework dependency) ; `experiments/` reuse the same algorithms.
Models are loaded lazily and cached (`lru_cache`), pre-loaded at startup if present; a missing model yields a clear `503`.
Errors: unified `{"error":{code,message,details}}`. CORS via `CORS_ORIGINS`. Optional `X-API-Key`.
MySQL: not accessed directly; request fields map 1:1 to typical columns (see `docs/API.md`). Spring Boot: use snake_case Jackson naming.
Deployment: `uvicorn app.main:app` (one worker per CPU; TensorFlow model ~11 MB). Docker is not included.
