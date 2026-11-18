package com.foodflow.controller;

import com.foodflow.dto.request.LoginRequest;
import com.foodflow.dto.request.RegisterDonorRequest;
import com.foodflow.dto.request.RegisterReceiverRequest;
import com.foodflow.dto.request.RegisterVolunteerRequest;
import com.foodflow.dto.response.ApiResponse;
import com.foodflow.dto.response.AuthResponse;
import com.foodflow.model.entity.User;
import com.foodflow.service.AuthService;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
public class AuthController {

    private final AuthService authService;

    public AuthController(AuthService authService) {
        this.authService = authService;
    }

    @PostMapping("/register/donor")
    public ResponseEntity<ApiResponse<AuthResponse>> registerDonor(@Valid @RequestBody RegisterDonorRequest req) {
        AuthResponse res = authService.registerDonor(req);
        return ResponseEntity.ok(ApiResponse.ok("Donor registered successfully", res));
    }

    @PostMapping("/register/receiver")
    public ResponseEntity<ApiResponse<AuthResponse>> registerReceiver(@Valid @RequestBody RegisterReceiverRequest req) {
        AuthResponse res = authService.registerReceiver(req);
        return ResponseEntity.ok(ApiResponse.ok("Receiver organization registered successfully", res));
    }

    @PostMapping("/register/volunteer")
    public ResponseEntity<ApiResponse<AuthResponse>> registerVolunteer(@Valid @RequestBody RegisterVolunteerRequest req) {
        AuthResponse res = authService.registerVolunteer(req);
        return ResponseEntity.ok(ApiResponse.ok("Volunteer registered successfully", res));
    }

    @PostMapping("/login")
    public ResponseEntity<ApiResponse<AuthResponse>> login(@Valid @RequestBody LoginRequest req) {
        AuthResponse res = authService.login(req);
        return ResponseEntity.ok(ApiResponse.ok("Login successful", res));
    }

    @GetMapping("/me")
    public ResponseEntity<ApiResponse<User>> getCurrentUser(@AuthenticationPrincipal User user) {
        return ResponseEntity.ok(ApiResponse.ok("User profile retrieved", user));
    }
}

