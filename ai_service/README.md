# Surplus Food AI Service

Python/FastAPI AI subsystem for **Dynamic AI-Assisted Surplus Food Redistribution Under Time and Demand Uncertainty**
(React → Spring Boot → **this service**). Modular, research-oriented, free/open-source stack.

## Honest status (read first)
| Module | Code | Executed here | Real-data / accuracy status |
|---|---|---|---|
| Food image recognition (Food-101, MobileNetV2) | ✅ notebook + `scripts/train_food_classifier.py` + inference + API | Export/inference pipeline verified on **synthetic** data only | ❌ **Not trained** (needs Colab GPU + 4.6 GB download). No accuracy claimed. API uses the Groq fallback if a key is set, otherwise returns `503` until artifacts are installed. |
| Usable-time regression | ✅ | ✅ trained | ⚠️ **Synthetic data** from documented assumptions. Metrics only show the pipeline works. Not a safety check. |
| Matching (Nearest / Rule-based / Proposed) | ✅ | ✅ simulated | Hand-weighted scoring (not ML). Results are simulator results. |
| Fairness allocation | ✅ | ✅ | Algorithmic (weighted max-min). |
| Route optimisation | ✅ | ✅ | **Simulated** distances unless you supply a road graph (OSM export). |
| Forecasting | ✅ pipeline | ✅ on synthetic demo series | ❌ No real history → API returns `insufficient_data`; nothing fabricated. |
| Research simulation, ablation, dynamic timeline | ✅ | ✅ (`reports/`) | Synthetic scenarios. |
| Tests | ✅ 99 tests | ✅ pass | Unit tests ≠ model accuracy. |

## Food recognition without training: Groq fallback
Set `GROQ_API_KEY` (and optionally `GROQ_MODEL`, `FOOD_BACKEND`) in `.env`. With `FOOD_BACKEND=auto` (default) the service uses the local
MobileNetV2 model when installed and **falls back to Groq's vision model** when it is missing or fails; `GROQ_ON_UNCERTAIN=true` also asks Groq
when the local model is unsure. Responses carry `source` (`local_mobilenetv2` | `groq_vlm`) and keep the same schema. Invalid images are rejected
before any call to Groq. The key stays server-side. Groq's confidence is a coarse self-reported label, not calibrated, and the photo is sent to a
third party. The Groq logic is tested with a mocked HTTP layer only; it has not been called live from the delivery environment, and the default
model name may need updating to whatever vision model Groq currently offers.

## Install & run
```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt                          # use tensorflow-cpu on servers without GPU
cp .env.example .env                                     # optional
python scripts/train_usable_time.py                      # creates saved_models/usable_time (synthetic)
uvicorn app.main:app --host 0.0.0.0 --port 8000          # docs: http://localhost:8000/docs
pytest -q                                                # full test-suite
python scripts/run_experiments.py --seeds 30             # regenerates reports/
python scripts/generate_api_docs.py                      # regenerates docs/API.md from the live app
```

## Train the food classifier (Colab, GPU)
1. Upload `notebooks/food_recognition.ipynb` to Colab → *Runtime → T4 GPU*.
2. First run with `SMOKE_TEST = True` (pipeline check), then set `False` and run all cells (Food-101 download ≈ 4.6 GB).
3. The last cell creates `food_classifier_artifacts.zip`. Unzip into `saved_models/food_classifier/`
   (`food_classifier_best.keras`, `class_labels.json`, `food_category_mapping.json`, `model_config.json`; a mapping file is already included).
4. Restart the service; `GET /api/ai/health` should show `food_recognition.loaded: true`.
Alternative CLI: `python scripts/train_food_classifier.py --out-dir /content/food_model_artifacts` (same logic).
Then fill the real metrics into `reports/MODEL_EVALUATION.md`.

## Layout
```
app/ main.py config.py | api/ (routers) | services/ (glue, ML inference, training) | algorithms/ (pure algorithms)
     experiments/ (simulator, baselines, ablation, dynamic timeline, metrics) | schemas/ | utils/
notebooks/ scripts/ tests/ docs/ reports/ saved_models/ datasets/
```
See `docs/ARCHITECTURE.md`, `docs/METHODOLOGY.md` (all formulas/assumptions), `docs/API.md`, `reports/`.

## Limitations (also state them in the thesis)
- Image recognition cannot determine quantity, freshness or safety; Food-101 lacks many local dishes (e.g. dal, roti, biryani) → manual correction path is essential.
- Usable-time output is an experimental estimate, never a food-safety certification.
- Travel distances/times are simulated estimates unless a real road graph is supplied.
- Matching weights are untuned design parameters; simulation results do not prove real-world impact.
