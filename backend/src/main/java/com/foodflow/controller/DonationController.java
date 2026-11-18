package com.foodflow.controller;

import com.foodflow.dto.request.CreateDonationRequest;
import com.foodflow.dto.response.ApiResponse;
import com.foodflow.dto.response.DonationResponse;
import com.foodflow.model.entity.User;
import com.foodflow.service.DonationService;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/donations")
public class DonationController {

    private final DonationService donationService;

    public DonationController(DonationService donationService) {
        this.donationService = donationService;
    }

    @PostMapping
    public ResponseEntity<ApiResponse<DonationResponse>> createDonation(
            @Valid @RequestBody CreateDonationRequest req,
            @AuthenticationPrincipal User user) {
        DonationResponse res = donationService.createDonation(req, user);
        return ResponseEntity.ok(ApiResponse.ok("Donation posted and matched with eligible recipients", res));
    }

    @GetMapping
    public ResponseEntity<ApiResponse<List<DonationResponse>>> getAllAvailableDonations() {
        List<DonationResponse> list = donationService.getAllAvailableDonations();
        return ResponseEntity.ok(ApiResponse.ok(list));
    }

    @GetMapping("/donor/{donorProfileId}")
    public ResponseEntity<ApiResponse<List<DonationResponse>>> getDonationsByDonor(
            @PathVariable Long donorProfileId) {
        List<DonationResponse> list = donationService.getDonationsByDonor(donorProfileId);
        return ResponseEntity.ok(ApiResponse.ok(list));
    }

    @GetMapping("/{id}")
    public ResponseEntity<ApiResponse<DonationResponse>> getDonationById(@PathVariable Long id) {
        DonationResponse res = donationService.getDonationById(id);
        return ResponseEntity.ok(ApiResponse.ok(res));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<ApiResponse<DonationResponse>> cancelDonation(
            @PathVariable Long id,
            @AuthenticationPrincipal User user) {
        DonationResponse res = donationService.cancelDonation(id, user);
        return ResponseEntity.ok(ApiResponse.ok("Donation cancelled", res));
    }
}

