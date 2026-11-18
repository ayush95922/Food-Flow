package com.foodflow.controller;

import com.foodflow.dto.response.ApiResponse;
import com.foodflow.dto.response.DashboardStatsResponse;
import com.foodflow.model.entity.RecipientProfile;
import com.foodflow.model.entity.User;
import com.foodflow.service.AdminService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/admin")
public class AdminController {

    private final AdminService adminService;

    public AdminController(AdminService adminService) {
        this.adminService = adminService;
    }

    @GetMapping("/stats")
    public ResponseEntity<ApiResponse<DashboardStatsResponse>> getStats() {
        DashboardStatsResponse stats = adminService.getStatistics();
        return ResponseEntity.ok(ApiResponse.ok("System statistics retrieved", stats));
    }

    @GetMapping("/users")
    public ResponseEntity<ApiResponse<List<User>>> getAllUsers() {
        List<User> list = adminService.getAllUsers();
        return ResponseEntity.ok(ApiResponse.ok(list));
    }

    @PutMapping("/users/{id}/toggle-status")
    public ResponseEntity<ApiResponse<User>> toggleUserStatus(@PathVariable Long id) {
        User u = adminService.toggleUserStatus(id);
        return ResponseEntity.ok(ApiResponse.ok("User status updated", u));
    }

    @PutMapping("/recipients/{id}/verify")
    public ResponseEntity<ApiResponse<RecipientProfile>> verifyRecipient(@PathVariable Long id) {
        RecipientProfile r = adminService.verifyRecipient(id);
        return ResponseEntity.ok(ApiResponse.ok("Organization verified successfully", r));
    }
}

