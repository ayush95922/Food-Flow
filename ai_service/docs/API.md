# API reference with real captured examples

Interactive docs: `/docs` (Swagger UI) and `/redoc`. All errors use `{"error": {"code", "message", "details"}}`. Optional auth header `X-API-Key` when `API_KEY` is set. Fields are `snake_case` (Spring Boot: `spring.jackson.property-naming-strategy=SNAKE_CASE`).

Status codes: 200 OK, 400 unreadable image, 401 bad API key, 413 file too large, 415 unsupported type, 422 validation/insufficient input, 503 model not installed, 500 unexpected.


## GET /api/ai/health
Service and model status.

**Request**
```json
(none)
```
**Response 200** (captured from this build)
```json
{
  "status": "ok",
  "version": "1.0.0",
  "time": "2026-11-15T05:01:45.478220+00:00",
  "models": {
    "food_recognition": {
      "files_present": false,
      "loaded": false,
      "note": "Must be trained on Colab and copied to saved_models/food_classifier"
    },
    "usable_time": {
      "files_present": true,
      "loaded": false,
      "data_source": "SYNTHETIC"
    }
  },
  "algorithms": [
    "nearest_recipient",
    "rule_based",
    "dynamic_multi_factor",
    "weighted_max_min_fairness",
    "nearest_neighbor_routing",
    "improved_routing",
    "forecasting_baselines_and_ml"
  ]
}
```

## POST /api/ai/usable-time-estimation
Experimental estimate; trained on SYNTHETIC data.

**Request**
```json
{
  "food_category": "cooked_meal",
  "food_type": "veg pulao",
  "elapsed_minutes": 90,
  "storage_condition": "room_temp",
  "temperature_c": 28,
  "packaging": "covered"
}
```
**Response 200** (captured from this build)
```json
{
  "estimated_remaining_minutes": 110.6,
  "conservative_remaining_minutes": 0.0,
  "interval_minutes": [
    0.0,
    551.1
  ],
  "uncertainty_level": "high",
  "model": "gradient_boosting",
  "data_source": "SYNTHETIC (documented assumption model) - NOT real data",
  "notes": [
    "Estimate comes from a model trained on SYNTHETIC data; real-world error is unknown.",
    "food_type is informational; the estimate is driven by food_category."
  ],
  "disclaimer": "Experimental estimate trained on SYNTHETIC data generated from documented assumptions. It is not a food-safety certification and does not confirm that food is safe to eat. Always follow local food-safety rules and the donor's/recipient's own checks.",
  "elapsed_minutes_used": 90.0
}
```

## POST /api/ai/matching/recommend
Rank feasible recipients, propose allocations, explain them.

**Request**
```json
{
  "donations": [
    {
      "id": "D-101",
      "food_category": "cooked_meal",
      "quantity": 100,
      "location": {
        "lat": 22.72,
        "lon": 75.86
      },
      "pickup_deadline_minutes": 120,
      "remaining_usable_minutes": 240
    }
  ],
  "recipients": [
    {
      "id": "NGO-A",
      "name": "NGO A",
      "location": {
        "lat": 22.73,
        "lon": 75.87
      },
      "demand_remaining": 80,
      "capacity": 100,
      "accepted_categories": [
        "cooked_meal"
      ],
      "historical_received": 500,
      "allocation_count": 5
    },
    {
      "id": "NGO-B",
      "name": "NGO B",
      "location": {
        "lat": 22.78,
        "lon": 75.9
      },
      "demand_remaining": 150,
      "capacity": 200,
      "accepted_categories": [
        "any"
      ],
      "historical_received": 20,
      "allocation_count": 1
    }
  ],
  "strategy": "dynamic",
  "options": {
    "top_n": 3
  }
}
```
**Response 200** (captured from this build)
```json
{
  "strategy": "dynamic",
  "weights_used": {
    "demand": 0.15,
    "quantity": 0.1,
    "distance": 0.12,
    "urgency": 0.1,
    "usable_time": 0.1,
    "capacity": 0.08,
    "compatibility": 0.08,
    "pickup_feasibility": 0.12,
    "fairness": 0.15
  },
  "processing_order": [
    "D-101"
  ],
  "results": [
    {
      "donation_id": "D-101",
      "status": "fully_allocated",
      "allocations": [
        {
          "recipient_id": "NGO-B",
          "recipient_name": "NGO B",
          "quantity": 100.0,
          "distance_km": 10.181,
          "pickup_eta_minutes": 24.4,
          "delivery_eta_minutes": 48.9,
          "score": 0.7583,
          "chunk": 1,
          "explanation": {
            "recommended_recipient": "NGO B",
            "total_score": 0.7583,
            "reasons": [
              "High unmet demand relative to other candidates (score 1.00)",
              "Can take 100 of 100 portions offered (score 1.00)",
              "Sufficient receiving capacity (score 1.00)",
              "Lower historical allocation than other candidates (score 0.88)",
              "Pickup can be completed well before the donor deadline (score 0.80)",
              "Food arrives with a comfortable margin before estimated expiry, delivery ETA 49 min (score 0.80)",
              "Food category matches the recipient's accepted categories (score 0.70)"
            ],
            "weaknesses": [
              "Low urgency score (0.27)"
            ],
            "top_weighted_factors": [
              {
                "factor": "demand",
                "contribution": 0.15
              },
              {
                "factor": "fairness",
                "contribution": 0.132
              },
              {
                "factor": "quantity",
                "contribution": 0.1
              }
            ],
            "factor_scores": {
              "demand": 1.0,
              "quantity": 1.0,
              "distance": 0.3212,
              "urgency": 0.2655,
              "usable_time": 0.7964,
              "capacity": 1.0,
              "compatibility": 0.7,
              "pickup_feasibility": 0.7964,
              "fairness": 0.88
            },
  ... (truncated)
```

## POST /api/ai/allocation/fairness
Weighted max-min allocation vs proportional / FCFS.

**Request**
```json
{
  "supply": 150,
  "recipients": [
    {
      "id": "A",
      "name": "A",
      "demand": 100,
      "capacity": 100,
      "historical_received": 500,
      "allocation_count": 10
    },
    {
      "id": "B",
      "name": "B",
      "demand": 100,
      "capacity": 100,
      "historical_received": 0
    },
    {
      "id": "C",
      "name": "C",
      "demand": 100,
      "capacity": 100,
      "historical_received": 100,
      "allocation_count": 2,
      "priority": 2
    }
  ]
}
```
**Response 200** (captured from this build)
```json
{
  "supply": 150.0,
  "fairness_level": 86.66666666666667,
  "allocations": [
    {
      "recipient_id": "A",
      "name": "A",
      "allocated": 0.0,
      "demand": 100.0,
      "fulfilment_ratio": 0.0
    },
    {
      "recipient_id": "B",
      "name": "B",
      "allocated": 86.6667,
      "demand": 100.0,
      "fulfilment_ratio": 0.8667
    },
    {
      "recipient_id": "C",
      "name": "C",
      "allocated": 63.3333,
      "demand": 100.0,
      "fulfilment_ratio": 0.6333
    }
  ],
  "metrics": {
    "allocated_total": 150.0,
    "unmet_demand_total": 150.0,
    "jain_current_fulfilment": 0.6509161041465765,
    "jain_cumulative_per_priority": 0.5635911185882269,
    "gini_cumulative_per_priority": 0.41729010806317546,
    "min_fulfilment": 0.0,
    "max_fulfilment": 0.8666666666666667
  },
  "explanations": [
    {
      "recipient_id": "A",
      "reasons": [
        "Effective history per priority = 550.0 (rank 3 of 3, 1 = lowest history, served first)",
        "Received nothing: its history per priority (550.0) is above the fairness level 86.7 reached when supply 150.0 ran out"
      ]
    },
    {
      "recipient_id": "B",
      "reasons": [
        "Effective history per priority = 0.0 (rank 1 of 3, 1 = lowest history, served first)",
        "Filled up to the common fairness level 86.7 (cumulative received per priority)"
      ]
    },
    {
      "recipient_id": "C",
      "reasons": [
        "Effective history per priority = 55.0 (rank 2 of 3, 1 = lowest history, served first)",
        "Filled up to the common fairness level 86.7 (cumulative received per priority)",
        "Priority weight 2.0 increases its share"
      ]
    }
  ],
  "method": "weighted max-min (water-filling) on cumulative received per priority",
  "comparison": {
    "proportional": {
      "allocations": [
        50.0,
        50.0,
        50.0
      ],
      "metrics": {
        "allocated_total": 150.0,
        "unmet_demand_total": 150.0,
  ... (truncated)
```

## POST /api/ai/routes/optimize
SIMULATED routing (no road graph supplied).

**Request**
```json
{
  "volunteer_location": {
    "lat": 22.72,
    "lon": 75.82
  },
  "destination": {
    "lat": 22.75,
    "lon": 75.88
  },
  "pickups": [
    {
      "id": "P0",
      "location": {
        "lat": 22.7,
        "lon": 75.79
      },
      "deadline_minutes": 40,
      "urgency": 0.5,
      "quantity": 20
    },
    {
      "id": "P1",
      "location": {
        "lat": 22.712,
        "lon": 75.81
      },
      "deadline_minutes": 55,
      "urgency": 0.5,
      "quantity": 20
    },
    {
      "id": "P2",
      "location": {
        "lat": 22.724,
        "lon": 75.83000000000001
      },
      "deadline_minutes": 70,
      "urgency": 0.5,
      "quantity": 20
    },
    {
      "id": "P3",
      "location": {
        "lat": 22.736,
        "lon": 75.79
      },
      "deadline_minutes": 85,
      "urgency": 0.5,
      "quantity": 20
    },
    {
      "id": "P4",
      "location": {
        "lat": 22.747999999999998,
        "lon": 75.81
      },
      "deadline_minutes": 100,
      "urgency": 0.5,
      "quantity": 20
    }
  ]
}
```
**Response 200** (captured from this build)
```json
{
  "mode": "simulated",
  "routes": {
    "nearest_neighbor": {
      "algorithm": "nearest_neighbor",
      "visit_order": [
        "P2",
        "P1",
        "P0",
        "P3",
        "P4"
      ],
      "completed_pickups": [
        "P2",
        "P1",
        "P0",
        "P3",
        "P4"
      ],
      "missed_deadline": [],
      "unserved": [],
      "expired_en_route": [],
      "total_distance_km": 25.537,
      "estimated_total_time_minutes": 86.289,
      "destination_arrival_minutes": 86.289,
      "completed_count": 5,
      "completed_quantity": 100.0,
      "arrival_times_minutes": {
        "P2": 3.49,
        "P1": 16.12,
        "P0": 28.76,
        "P3": 46.25,
        "P4": 58.88
      },
      "legs": [
        {
          "from": "start",
          "to": "P2",
          "km": 1.453,
          "min": 3.49
        },
        {
          "from": "P2",
          "to": "P1",
          "km": 3.181,
          "min": 7.64
        },
        {
          "from": "P1",
          "to": "P0",
          "km": 3.181,
          "min": 7.64
        },
        {
          "from": "P0",
          "to": "P3",
          "km": 5.204,
          "min": 12.49
        },
        {
          "from": "P3",
          "to": "P4",
          "km": 3.181,
          "min": 7.63
        },
        {
          "from": "P4",
          "to": "destination",
          "km": 9.336,
          "min": 22.41
  ... (truncated)
```

## POST /api/ai/forecast/demand
With too little history the service reports the missing-data requirement and fabricates nothing.

**Request**
```json
{
  "records": [
    {
      "date": "2026-01-01",
      "supply_qty": 100,
      "demand_qty": 120
    }
  ],
  "horizon_days": 7
}
```
**Response 200** (captured from this build)
```json
{
  "data_source": "caller-provided history",
  "horizon_days": 7,
  "status": "insufficient_data",
  "n_days": 1,
  "required_days": 56,
  "message": "At least 56 days of real, daily donation-supply and recipient-demand records are required (more is better). Export them from the platform database (date, supply_qty, demand_qty, optional category) and call the endpoint again. No forecast has been fabricated."
}
```

## POST /api/ai/research/run-experiment
Synthetic simulation (small run shown).

**Request**
```json
{
  "config": {
    "n_donations": 12,
    "n_recipients": 5
  },
  "n_seeds": 2,
  "experiments": [
    "baselines"
  ]
}
```
**Response 200** (captured from this build)
```json
{
  "synthetic_data_notice": "All scenarios are SYNTHETIC, generated from documented assumptions. Results show relative algorithm behaviour in simulation, not real-world impact.",
  "seeds": [
    0,
    1
  ],
  "baselines": {
    "config": {
      "n_donations": 12,
      "n_recipients": 5,
      "categories": [
        "cooked_meal",
        "cooked_protein_meal",
        "fresh_salad",
        "soup_liquid",
        "ready_to_eat_snack",
        "bakery_dry",
        "sweets_desserts"
      ],
      "qty_min": 20,
      "qty_max": 200,
      "demand_supply_ratio": 1.0,
      "city_center": [
        22.7196,
        75.8577
      ],
      "city_radius_km": 8.0,
      "deadline_min_range": [
        30.0,
        180.0
      ],
      "storage_conditions": [
        "room_temp",
        "refrigerated",
        "frozen",
        "hot_holding",
        "insulated_box"
      ],
      "capacity_factor_range": [
        0.5,
        1.2
      ],
      "horizon_min": 480.0,
      "estimate_noise": 0.15,
      "speed_kmph": 25.0,
      "detour_factor": 1.3,
      "max_radius_km": 15.0,
      "n_demand_events": 6,
      "n_unavailable_events": 4,
      "unavailable_duration_min": [
        60.0,
        180.0
      ],
      "accept_prob": 0.85,
      "response_delay_range": [
        10.0,
        30.0
      ]
    },
    "seeds": [
      0,
      1
    ],
    "summary": {
      "A_nearest_recipient": {
        "total_donated": {
          "mean": 1301.5,
          "std": 259.50818869546293
        },
        "redistributed": {
  ... (truncated)
```

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
