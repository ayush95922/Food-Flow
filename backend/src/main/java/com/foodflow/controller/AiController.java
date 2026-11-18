package com.foodflow.controller;

import com.foodflow.dto.request.UsableTimeEstimateRequest;
import com.foodflow.dto.response.ApiResponse;
import com.foodflow.service.AiIntegrationService;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/ai")
public class AiController {

    private final AiIntegrationService aiIntegrationService;

    public AiController(AiIntegrationService aiIntegrationService) {
        this.aiIntegrationService = aiIntegrationService;
    }

    @PostMapping(value = "/recognize-food", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<ApiResponse<Map<String, Object>>> recognizeFood(
            @RequestParam("file") MultipartFile file) throws IOException {
        if (file.isEmpty()) {
            return ResponseEntity.badRequest().body(ApiResponse.error("Please provide a valid food image"));
        }
        Map<String, Object> result = aiIntegrationService.recognizeFoodImage(file.getBytes(), file.getOriginalFilename());
        return ResponseEntity.ok(ApiResponse.ok("AI food prediction generated", result));
    }

    @PostMapping("/estimate-usability")
    public ResponseEntity<ApiResponse<Map<String, Object>>> estimateUsability(
            @RequestBody UsableTimeEstimateRequest req) {
        Map<String, Object> result = aiIntegrationService.estimateUsableTime(req);
        return ResponseEntity.ok(ApiResponse.ok("Usable time estimation generated", result));
    }

    @GetMapping("/health")
    public ResponseEntity<ApiResponse<Map<String, Object>>> getAiStatus() {
        boolean healthy = aiIntegrationService.isAiServiceHealthy();
        Map<String, Object> status = Map.of(
                "service_online", healthy,
                "engine", healthy ? "FastAPI Python Microservice" : "Integrated Spring Algorithmic Engine",
                "algorithms", List.of("dynamic_multi_factor", "rule_based", "nearest_recipient", "jain_fairness", "usable_time_regression")
        );
        return ResponseEntity.ok(ApiResponse.ok("AI Subsystem Status", status));
    }
}
