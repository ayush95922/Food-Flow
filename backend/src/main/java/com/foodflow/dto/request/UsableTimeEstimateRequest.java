package com.foodflow.dto.request;

import jakarta.validation.constraints.NotBlank;
import java.time.LocalDateTime;

public class UsableTimeEstimateRequest {
    @NotBlank
    private String foodCategory;

    private String foodType;

    private Double elapsedMinutes;

    private LocalDateTime preparedAt;

    private String storageCondition = "room_temp";

    private Double temperatureC;

    private String packaging = "covered";

    public UsableTimeEstimateRequest() {
    }

    public String getFoodCategory() {
        return foodCategory;
    }

    public void setFoodCategory(String foodCategory) {
        this.foodCategory = foodCategory;
    }

    public String getFoodType() {
        return foodType;
    }

    public void setFoodType(String foodType) {
        this.foodType = foodType;
    }

    public Double getElapsedMinutes() {
        return elapsedMinutes;
    }

    public void setElapsedMinutes(Double elapsedMinutes) {
        this.elapsedMinutes = elapsedMinutes;
    }

    public LocalDateTime getPreparedAt() {
        return preparedAt;
    }

    public void setPreparedAt(LocalDateTime preparedAt) {
        this.preparedAt = preparedAt;
    }

    public String getStorageCondition() {
        return storageCondition;
    }

    public void setStorageCondition(String storageCondition) {
        this.storageCondition = storageCondition;
    }

    public Double getTemperatureC() {
        return temperatureC;
    }

    public void setTemperatureC(Double temperatureC) {
        this.temperatureC = temperatureC;
    }

    public String getPackaging() {
        return packaging;
    }

    public void setPackaging(String packaging) {
        this.packaging = packaging;
    }
}

