package com.foodflow.controller;

import com.foodflow.dto.response.ApiResponse;
import com.foodflow.model.entity.ResearchExperiment;
import com.foodflow.service.ResearchService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/research")
public class ResearchController {

    private final ResearchService researchService;

    public ResearchController(ResearchService researchService) {
        this.researchService = researchService;
    }

    @GetMapping("/benchmark")
    public ResponseEntity<ApiResponse<Map<String, Object>>> getBenchmarkData() {
        Map<String, Object> data = researchService.getBenchmarkComparison();
        return ResponseEntity.ok(ApiResponse.ok("Research evaluation benchmarks", data));
    }

    @PostMapping("/experiments/run")
    public ResponseEntity<ApiResponse<Map<String, Object>>> runExperiment(@RequestBody(required = false) Map<String, Object> req) {
        if (req == null) req = Map.of("experiments", List.of("baselines", "ablation", "dynamic_timeline"), "n_seeds", 10);
        Map<String, Object> res = researchService.runExperiment(req);
        return ResponseEntity.ok(ApiResponse.ok("Research experiment simulation executed", res));
    }

    @GetMapping("/history")
    public ResponseEntity<ApiResponse<List<ResearchExperiment>>> getExperimentHistory() {
        List<ResearchExperiment> history = researchService.getExperimentHistory();
        return ResponseEntity.ok(ApiResponse.ok("Historical experiment runs", history));
    }
}

