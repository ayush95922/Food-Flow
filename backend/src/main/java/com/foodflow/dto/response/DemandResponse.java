package com.foodflow.dto.response;

import com.foodflow.model.enums.DemandPriority;
import com.foodflow.model.enums.DemandStatus;
import java.time.LocalDateTime;

public class DemandResponse {
    private Long id;
    private Long recipientProfileId;
    private String recipientOrganizationName;
    private String foodCategory;
    private Double quantityRequired;
    private Double quantityReceived;
    private Double remainingQuantity;
    private DemandPriority priority;
    private LocalDateTime requiredBefore;
    private DemandStatus status;
    private String notes;
    private LocalDateTime createdAt;

    public DemandResponse() {
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getRecipientProfileId() {
        return recipientProfileId;
    }

    public void setRecipientProfileId(Long recipientProfileId) {
        this.recipientProfileId = recipientProfileId;
    }

    public String getRecipientOrganizationName() {
        return recipientOrganizationName;
    }

    public void setRecipientOrganizationName(String recipientOrganizationName) {
        this.recipientOrganizationName = recipientOrganizationName;
    }

    public String getFoodCategory() {
        return foodCategory;
    }

    public void setFoodCategory(String foodCategory) {
        this.foodCategory = foodCategory;
    }

    public Double getQuantityRequired() {
        return quantityRequired;
    }

    public void setQuantityRequired(Double quantityRequired) {
        this.quantityRequired = quantityRequired;
    }

    public Double getQuantityReceived() {
        return quantityReceived;
    }

    public void setQuantityReceived(Double quantityReceived) {
        this.quantityReceived = quantityReceived;
    }

    public Double getRemainingQuantity() {
        return remainingQuantity;
    }

    public void setRemainingQuantity(Double remainingQuantity) {
        this.remainingQuantity = remainingQuantity;
    }

    public DemandPriority getPriority() {
        return priority;
    }

    public void setPriority(DemandPriority priority) {
        this.priority = priority;
    }

    public LocalDateTime getRequiredBefore() {
        return requiredBefore;
    }

    public void setRequiredBefore(LocalDateTime requiredBefore) {
        this.requiredBefore = requiredBefore;
    }

    public DemandStatus getStatus() {
        return status;
    }

    public void setStatus(DemandStatus status) {
        this.status = status;
    }

    public String getNotes() {
        return notes;
    }

    public void setNotes(String notes) {
        this.notes = notes;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
}

