package com.foodflow.controller;

import com.foodflow.dto.request.UpdateDeliveryStatusRequest;
import com.foodflow.dto.response.ApiResponse;
import com.foodflow.dto.response.DeliveryResponse;
import com.foodflow.model.entity.User;
import com.foodflow.service.VolunteerService;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/volunteer")
public class VolunteerController {

    private final VolunteerService volunteerService;

    public VolunteerController(VolunteerService volunteerService) {
        this.volunteerService = volunteerService;
    }

    @GetMapping("/deliveries")
    public ResponseEntity<ApiResponse<List<DeliveryResponse>>> getAssignedDeliveries(
            @AuthenticationPrincipal User user) {
        List<DeliveryResponse> list = volunteerService.getDeliveriesForVolunteer(user);
        return ResponseEntity.ok(ApiResponse.ok(list));
    }

    @GetMapping("/deliveries/all")
    public ResponseEntity<ApiResponse<List<DeliveryResponse>>> getAllDeliveries() {
        List<DeliveryResponse> list = volunteerService.getAllDeliveries();
        return ResponseEntity.ok(ApiResponse.ok(list));
    }

    @PutMapping("/deliveries/{id}/status")
    public ResponseEntity<ApiResponse<DeliveryResponse>> updateStatus(
            @PathVariable Long id,
            @Valid @RequestBody UpdateDeliveryStatusRequest req,
            @AuthenticationPrincipal User user) {
        DeliveryResponse res = volunteerService.updateDeliveryStatus(id, req.getStatus(), req.getNotes(), user);
        return ResponseEntity.ok(ApiResponse.ok("Delivery status updated to " + req.getStatus(), res));
    }
}

