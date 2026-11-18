package com.foodflow.dto.request;

import com.foodflow.model.enums.DemandPriority;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import java.time.LocalDateTime;

public class CreateDemandRequest {
    @NotBlank
    private String foodCategory;

    @NotNull
    private Double quantityRequired;

    private DemandPriority priority = DemandPriority.MEDIUM;

    @NotNull
    private LocalDateTime requiredBefore;

    private String notes;

    public CreateDemandRequest() {
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

    public String getNotes() {
        return notes;
    }

    public void setNotes(String notes) {
        this.notes = notes;
    }
}
