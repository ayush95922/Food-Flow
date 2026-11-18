package com.foodflow.controller;

import com.foodflow.dto.request.AllocateDonationRequest;
import com.foodflow.dto.response.AllocationResponse;
import com.foodflow.dto.response.ApiResponse;
import com.foodflow.model.entity.User;
import com.foodflow.service.MatchingService;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/matching")
public class MatchingController {

    private final MatchingService matchingService;

    public MatchingController(MatchingService matchingService) {
        this.matchingService = matchingService;
    }

    @GetMapping("/recommendations/{donationId}")
    public ResponseEntity<ApiResponse<List<AllocationResponse>>> getRecommendationsForDonation(
            @PathVariable Long donationId) {
        List<AllocationResponse> list = matchingService.getAllocationsForDonation(donationId);
        return ResponseEntity.ok(ApiResponse.ok(list));
    }

    @GetMapping("/recipient/{recipientProfileId}")
    public ResponseEntity<ApiResponse<List<AllocationResponse>>> getAllocationsForRecipient(
            @PathVariable Long recipientProfileId) {
        List<AllocationResponse> list = matchingService.getAllocationsForRecipient(recipientProfileId);
        return ResponseEntity.ok(ApiResponse.ok(list));
    }

    @PostMapping("/recalculate")
    public ResponseEntity<ApiResponse<List<AllocationResponse>>> recalculateMatching(
            @RequestBody AllocateDonationRequest req) {
        List<AllocationResponse> list = matchingService.recalculateMatching(req.getDonationId(), req.getStrategy());
        return ResponseEntity.ok(ApiResponse.ok("Recommendations recalculated dynamically", list));
    }

    @PostMapping("/accept/{allocationId}")
    public ResponseEntity<ApiResponse<AllocationResponse>> acceptAllocation(
            @PathVariable Long allocationId,
            @AuthenticationPrincipal User user) {
        AllocationResponse res = matchingService.acceptAllocation(allocationId, user);
        return ResponseEntity.ok(ApiResponse.ok("Donation accepted successfully and pickup scheduled", res));
    }

    @PostMapping("/reject/{allocationId}")
    public ResponseEntity<ApiResponse<AllocationResponse>> rejectAllocation(
            @PathVariable Long allocationId,
            @AuthenticationPrincipal User user) {
        AllocationResponse res = matchingService.rejectAllocation(allocationId, user);
        return ResponseEntity.ok(ApiResponse.ok("Allocation proposal declined", res));
    }
}

