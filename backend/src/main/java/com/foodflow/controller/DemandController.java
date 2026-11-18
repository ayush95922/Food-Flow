package com.foodflow.controller;

import com.foodflow.dto.request.CreateDemandRequest;
import com.foodflow.dto.response.ApiResponse;
import com.foodflow.dto.response.DemandResponse;
import com.foodflow.model.entity.User;
import com.foodflow.service.DemandService;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/demands")
public class DemandController {

    private final DemandService demandService;

    public DemandController(DemandService demandService) {
        this.demandService = demandService;
    }

    @PostMapping
    public ResponseEntity<ApiResponse<DemandResponse>> createDemand(
            @Valid @RequestBody CreateDemandRequest req,
            @AuthenticationPrincipal User user) {
        DemandResponse res = demandService.createDemand(req, user);
        return ResponseEntity.ok(ApiResponse.ok("Food demand recorded successfully", res));
    }

    @GetMapping
    public ResponseEntity<ApiResponse<List<DemandResponse>>> getAllActiveDemands() {
        List<DemandResponse> list = demandService.getAllActiveDemands();
        return ResponseEntity.ok(ApiResponse.ok(list));
    }

    @GetMapping("/recipient/{recipientProfileId}")
    public ResponseEntity<ApiResponse<List<DemandResponse>>> getDemandsByRecipient(
            @PathVariable Long recipientProfileId) {
        List<DemandResponse> list = demandService.getDemandsByRecipient(recipientProfileId);
        return ResponseEntity.ok(ApiResponse.ok(list));
    }
}

