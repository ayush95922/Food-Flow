package com.foodflow.service;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.foodflow.dto.request.UsableTimeEstimateRequest;
import com.foodflow.model.entity.Donation;
import com.foodflow.model.entity.RecipientProfile;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.MediaType;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestClient;

import java.time.Duration;
import java.time.LocalDateTime;
import java.util.*;

@Service
public class AiIntegrationService {

    private static final Logger log = LoggerFactory.getLogger(AiIntegrationService.class);

    @Value("${ai.service.base-url:http://localhost:8000}")
    private String aiServiceBaseUrl;

    @Value("${ai.service.api-key:}")
    private String aiApiKey;

    private final RestClient restClient;
    private final ObjectMapper objectMapper;

    public AiIntegrationService(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(Duration.ofSeconds(4));
        factory.setReadTimeout(Duration.ofSeconds(15));
        this.restClient = RestClient.builder()
                .requestFactory(factory)
                .build();
    }

    public boolean isAiServiceHealthy() {
        try {
            Map<?, ?> response = restClient.get()
                    .uri(aiServiceBaseUrl + "/api/ai/health")
                    .retrieve()
                    .body(Map.class);
            return response != null && "ok".equals(response.get("status"));
        } catch (Exception e) {
            log.debug("AI service health probe failed: {}", e.getMessage());
            return false;
        }
    }

    // 1. Food Image Recognition
    public Map<String, Object> recognizeFoodImage(byte[] imageBytes, String filename) {
        try {
            MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
            ByteArrayResource resource = new ByteArrayResource(imageBytes) {
                @Override
                public String getFilename() {
                    return filename != null ? filename : "food_upload.jpg";
                }
            };
            body.add("file", resource);

            var req = restClient.post()
                    .uri(aiServiceBaseUrl + "/api/ai/food-recognition")
                    .contentType(MediaType.MULTIPART_FORM_DATA)
                    .body(body);
            if (aiApiKey != null && !aiApiKey.isBlank()) {
                req.header("X-API-Key", aiApiKey);
            }

            @SuppressWarnings("unchecked")
            Map<String, Object> response = (Map<String, Object>) req.retrieve().body(Map.class);
            if (response != null) {
                return response;
            }
        } catch (Exception e) {
            log.warn("FastAPI food recognition call failed, using heuristic baseline: {}", e.getMessage());
        }

        // Heuristic Baseline
        Map<String, Object> fallback = new HashMap<>();
        String name = filename != null ? filename.toLowerCase() : "";
        String predictedFood = "Cooked Meal";
        String category = "cooked_meal";
        double confidence = 0.88;

        if (name.contains("rice") || name.contains("biryani") || name.contains("pulao")) {
            predictedFood = "Vegetable Rice / Biryani";
            category = "cooked_meal";
        } else if (name.contains("bread") || name.contains("roti") || name.contains("chapati")) {
            predictedFood = "Roti / Flatbread";
            category = "bakery";
        } else if (name.contains("curry") || name.contains("dal") || name.contains("paneer")) {
            predictedFood = "Mixed Curry / Dal";
            category = "cooked_meal";
        } else if (name.contains("fruit") || name.contains("veg") || name.contains("salad")) {
            predictedFood = "Fresh Produce / Salad";
            category = "produce";
        }

        fallback.put("food", predictedFood);
        fallback.put("category", category);
        fallback.put("confidence", confidence);
        fallback.put("source", "heuristic_fallback");
        fallback.put("manual_correction_allowed", true);
        fallback.put("needs_manual_verification", true);
        fallback.put("disclaimer", "Image recognition estimate. Please verify details before publishing.");
        return fallback;
    }

    // 2. Usable Time Estimation
    public Map<String, Object> estimateUsableTime(UsableTimeEstimateRequest req) {
        try {
            Map<String, Object> payload = new HashMap<>();
            payload.put("food_category", req.getFoodCategory());
            payload.put("food_type", req.getFoodType());
            payload.put("storage_condition", req.getStorageCondition());
            payload.put("temperature_c", req.getTemperatureC());
            payload.put("packaging", req.getPackaging());
            payload.put("elapsed_minutes", req.getElapsedMinutes() != null ? req.getElapsedMinutes() : 60.0);

            var request = restClient.post()
                    .uri(aiServiceBaseUrl + "/api/ai/usable-time-estimation")
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(payload);
            if (aiApiKey != null && !aiApiKey.isBlank()) {
                request.header("X-API-Key", aiApiKey);
            }

            @SuppressWarnings("unchecked")
            Map<String, Object> response = (Map<String, Object>) request.retrieve().body(Map.class);
            if (response != null) {
                return response;
            }
        } catch (Exception e) {
            log.warn("FastAPI usable time call failed, using research regression equation: {}", e.getMessage());
        }

        // Research formula: base[category] * 2^((20 - T)/10) * storageFactor - elapsedMinutes
        Map<String, Double> baseHours = Map.of(
                "cooked_meal", 5.0,
                "produce", 48.0,
                "bakery", 24.0,
                "dairy", 8.0,
                "packaged_goods", 168.0,
                "any", 6.0
        );
        double catBase = baseHours.getOrDefault(req.getFoodCategory().toLowerCase(), 5.0);

        double temp = req.getTemperatureC() != null ? req.getTemperatureC() : 25.0;
        double storageMult = switch (req.getStorageCondition().toLowerCase()) {
            case "refrigerated" -> 3.5;
            case "frozen" -> 15.0;
            case "heated", "warm" -> 1.8;
            default -> 1.0;
        };

        double elapsed = req.getElapsedMinutes() != null ? req.getElapsedMinutes() : 60.0;
        double totalLifespanMinutes = (catBase * Math.pow(2.0, (20.0 - temp) / 10.0) * storageMult) * 60.0;
        double remaining = Math.max(0.0, totalLifespanMinutes - elapsed);
        double conservative = Math.max(0.0, remaining * 0.75);

        Map<String, Object> result = new HashMap<>();
        result.put("estimated_remaining_minutes", Math.round(remaining * 10.0) / 10.0);
        result.put("conservative_remaining_minutes", Math.round(conservative * 10.0) / 10.0);
        result.put("interval_minutes", List.of(Math.round(conservative), Math.round(remaining * 1.25)));
        result.put("uncertainty_level", remaining < 90 ? "high" : "moderate");
        result.put("model", "research_regression_formula");
        result.put("data_source", "DOCUMENTED_ASSUMPTIONS");
        result.put("disclaimer", "Experimental estimate based on storage and thermal factors. Not a food-safety certificate.");
        return result;
    }

    // 3. Dynamic Multi-Factor Matching Engine
    public Map<String, Object> recommendMatches(Donation donation, List<RecipientProfile> recipients, String strategy, int topN) {
        try {
            Map<String, Object> payload = new HashMap<>();
            payload.put("strategy", strategy != null ? strategy : "dynamic");

            Map<String, Object> donMap = new HashMap<>();
            donMap.put("id", "D-" + donation.getId());
            donMap.put("food_category", donation.getFoodCategory());
            donMap.put("quantity", donation.getQuantity());
            donMap.put("location", Map.of("lat", donation.getLatitude(), "lon", donation.getLongitude()));

            long deadlineMinutes = Math.max(30L, Duration.between(LocalDateTime.now(), donation.getPickupDeadline()).toMinutes());
            donMap.put("pickup_deadline_minutes", (double) deadlineMinutes);
            donMap.put("remaining_usable_minutes", donation.getRemainingUsableMinutes() != null ? donation.getRemainingUsableMinutes() : 240.0);
            donMap.put("urgency", donation.getUrgencyScore() != null ? donation.getUrgencyScore() : 0.5);

            payload.put("donations", List.of(donMap));

            List<Map<String, Object>> recList = new ArrayList<>();
            for (RecipientProfile r : recipients) {
                if (!r.isAvailable()) continue;
                Map<String, Object> rm = new HashMap<>();
                rm.put("id", "REC-" + r.getId());
                rm.put("name", r.getOrganizationName());
                rm.put("location", Map.of("lat", r.getUser().getLatitude(), "lon", r.getUser().getLongitude()));
                rm.put("demand_remaining", r.getCurrentDemand() > 0 ? r.getCurrentDemand() : 100.0);
                rm.put("capacity", r.getMaxHandlingCapacity());
                rm.put("accepted_categories", List.of(r.getAcceptedCategories().split(",")));
                rm.put("historical_received", r.getHistoricalReceived());
                rm.put("allocation_count", r.getAllocationCount());
                rm.put("priority", r.getPriority() != null ? r.getPriority() : 1.0);
                recList.add(rm);
            }
            payload.put("recipients", recList);
            payload.put("options", Map.of("top_n", topN));

            var request = restClient.post()
                    .uri(aiServiceBaseUrl + "/api/ai/matching/recommend")
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(payload);
            if (aiApiKey != null && !aiApiKey.isBlank()) {
                request.header("X-API-Key", aiApiKey);
            }

            @SuppressWarnings("unchecked")
            Map<String, Object> response = (Map<String, Object>) request.retrieve().body(Map.class);
            if (response != null) {
                return response;
            }
        } catch (Exception e) {
            log.warn("FastAPI matching call failed, running local Dynamic Multi-Factor algorithm: {}", e.getMessage());
        }

        // Run local research matching algorithm
        return computeLocalMatching(donation, recipients, strategy, topN);
    }

    private Map<String, Object> computeLocalMatching(Donation donation, List<RecipientProfile> recipients, String strategy, int topN) {
        double dLat = donation.getLatitude();
        double dLon = donation.getLongitude();
        double dQty = donation.getQuantity();
        long deadlineMin = Math.max(30L, Duration.between(LocalDateTime.now(), donation.getPickupDeadline()).toMinutes());
        double usableMin = donation.getRemainingUsableMinutes() != null ? donation.getRemainingUsableMinutes() : 240.0;

        double maxDemand = 1.0;
        double maxHist = 1.0;
        double maxFreq = 1.0;

        for (RecipientProfile r : recipients) {
            if (r.getCurrentDemand() > maxDemand) maxDemand = r.getCurrentDemand();
            double histNorm = r.getHistoricalReceived() / Math.max(r.getPriority(), 0.1);
            if (histNorm > maxHist) maxHist = histNorm;
            if (r.getAllocationCount() > maxFreq) maxFreq = r.getAllocationCount();
        }

        List<Map<String, Object>> candidateScores = new ArrayList<>();

        for (RecipientProfile r : recipients) {
            if (!r.isAvailable()) continue;
            double rLat = r.getUser().getLatitude() != null ? r.getUser().getLatitude() : dLat;
            double rLon = r.getUser().getLongitude() != null ? r.getUser().getLongitude() : dLon;

            double distKm = haversine(dLat, dLon, rLat, rLon) * 1.3;
            double speed = 25.0; // km/h
            double pickupEtaMin = (distKm / speed) * 60.0;
            double deliveryEtaMin = pickupEtaMin * 2.0;

            // Check hard constraints
            if (pickupEtaMin > deadlineMin || deliveryEtaMin > usableMin) {
                continue; // Deadline exceeded
            }

            // Factor scores (0..1)
            double sDemand = Math.min(1.0, (r.getCurrentDemand() > 0 ? r.getCurrentDemand() : 80.0) / maxDemand);
            double sQuantity = Math.min(1.0, Math.min(dQty, r.getMaxHandlingCapacity()) / dQty);
            double sDistance = Math.max(0.0, 1.0 - (distKm / 15.0));
            double sUrgency = (donation.getUrgencyScore() != null ? donation.getUrgencyScore() : 0.5) * Math.max(0.0, 1.0 - (pickupEtaMin / deadlineMin));
            double sUsableTime = Math.max(0.0, (usableMin - deliveryEtaMin) / usableMin);
            double sCapacity = Math.min(1.0, r.getMaxHandlingCapacity() / dQty);
            double sCompat = r.getAcceptedCategories().contains("any") || r.getAcceptedCategories().contains(donation.getFoodCategory()) ? 1.0 : 0.7;
            double sPickupFeas = Math.max(0.0, 1.0 - (pickupEtaMin / deadlineMin));
            double histNorm = r.getHistoricalReceived() / Math.max(r.getPriority(), 0.1);
            double sFairness = 0.5 * (1.0 - histNorm / maxHist) + 0.5 * (1.0 - (double) r.getAllocationCount() / maxFreq);

            double score;
            if ("nearest".equalsIgnoreCase(strategy)) {
                score = sDistance;
            } else if ("rule_based".equalsIgnoreCase(strategy)) {
                score = 0.40 * sDistance + 0.35 * sDemand + 0.25 * sQuantity;
            } else {
                // Dynamic Multi-Factor (Formula 9)
                score = 0.15 * sDemand + 0.10 * sQuantity + 0.12 * sDistance + 0.10 * sUrgency
                        + 0.10 * sUsableTime + 0.08 * sCapacity + 0.08 * sCompat + 0.12 * sPickupFeas + 0.15 * sFairness;
            }

            Map<String, Object> candidate = new HashMap<>();
            candidate.put("recipient_id", "REC-" + r.getId());
            candidate.put("profile_id", r.getId());
            candidate.put("recipient_name", r.getOrganizationName());
            candidate.put("contact_person", r.getContactPerson());
            candidate.put("address", r.getUser().getAddress());
            candidate.put("distance_km", Math.round(distKm * 100.0) / 100.0);
            candidate.put("pickup_eta_minutes", Math.round(pickupEtaMin * 10.0) / 10.0);
            candidate.put("delivery_eta_minutes", Math.round(deliveryEtaMin * 10.0) / 10.0);
            candidate.put("quantity", Math.min(dQty, r.getMaxHandlingCapacity()));
            candidate.put("score", Math.round(score * 10000.0) / 10000.0);

            // Factor explanation
            Map<String, Object> explanation = new HashMap<>();
            explanation.put("recommended_recipient", r.getOrganizationName());
            explanation.put("total_score", Math.round(score * 10000.0) / 10000.0);
            List<String> reasons = new ArrayList<>();
            if (sDemand >= 0.7) reasons.add("High unmet demand relative to other organizations");
            if (sQuantity >= 0.7) reasons.add("Can absorb substantial portions of the offered surplus");
            if (sDistance >= 0.7) reasons.add(String.format("Close geographical proximity (%.1f km)", distKm));
            if (sFairness >= 0.7) reasons.add("High fairness priority due to low recent allocations");
            if (sUsableTime >= 0.7) reasons.add("Safe delivery ETA within usable-time window");
            if (reasons.isEmpty()) reasons.add("Best balanced multi-factor trade-off");
            explanation.put("reasons", reasons);

            Map<String, Double> factorScores = new HashMap<>();
            factorScores.put("demand", Math.round(sDemand * 100.0) / 100.0);
            factorScores.put("quantity", Math.round(sQuantity * 100.0) / 100.0);
            factorScores.put("distance", Math.round(sDistance * 100.0) / 100.0);
            factorScores.put("urgency", Math.round(sUrgency * 100.0) / 100.0);
            factorScores.put("usable_time", Math.round(sUsableTime * 100.0) / 100.0);
            factorScores.put("capacity", Math.round(sCapacity * 100.0) / 100.0);
            factorScores.put("fairness", Math.round(sFairness * 100.0) / 100.0);
            explanation.put("factor_scores", factorScores);

            candidate.put("explanation", explanation);
            candidateScores.add(candidate);
        }

        candidateScores.sort((a, b) -> Double.compare((Double) b.get("score"), (Double) a.get("score")));

        if (candidateScores.size() > topN) {
            candidateScores = candidateScores.subList(0, topN);
        }

        Map<String, Object> result = new HashMap<>();
        result.put("strategy", strategy);
        result.put("donation_id", "D-" + donation.getId());
        result.put("results", List.of(Map.of(
                "donation_id", "D-" + donation.getId(),
                "status", candidateScores.isEmpty() ? "unallocated" : "fully_allocated",
                "allocations", candidateScores
        )));
        return result;
    }

    public static double haversine(double lat1, double lon1, double lat2, double lon2) {
        final int R = 6371; // Earth radius in km
        double latDistance = Math.toRadians(lat2 - lat1);
        double lonDistance = Math.toRadians(lon2 - lon1);
        double a = Math.sin(latDistance / 2) * Math.sin(latDistance / 2)
                + Math.cos(Math.toRadians(lat1)) * Math.cos(Math.toRadians(lat2))
                * Math.sin(lonDistance / 2) * Math.sin(lonDistance / 2);
        double c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        return R * c;
    }
}
