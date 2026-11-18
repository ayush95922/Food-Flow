package com.foodflow.dto.request;

import com.foodflow.model.enums.StorageCondition;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import java.time.LocalDateTime;

public class CreateDonationRequest {
    @NotBlank
    private String foodName;

    @NotBlank
    private String foodCategory;

    private String foodDescription;

    @NotNull
    private Double quantity;

    private String quantityUnit = "portions";

    @NotNull
    private LocalDateTime preparationTime;

    private StorageCondition storageCondition = StorageCondition.ROOM_TEMP;

    private Double temperatureC;

    private String packaging = "covered";

    @NotBlank
    private String pickupAddress;

    @NotNull
    private Double latitude;

    @NotNull
    private Double longitude;

    private LocalDateTime availableFrom;

    @NotNull
    private LocalDateTime pickupDeadline;

    private Double remainingUsableMinutes;

    private Double urgencyScore;

    private String imageUrl;

    private String aiPredictedFood;

    private Double aiConfidence;

    private Boolean aiVerifiedByDonor = false;

    public CreateDonationRequest() {
    }

    public String getFoodName() {
        return foodName;
    }

    public void setFoodName(String foodName) {
        this.foodName = foodName;
    }

    public String getFoodCategory() {
        return foodCategory;
    }

    public void setFoodCategory(String foodCategory) {
        this.foodCategory = foodCategory;
    }

    public String getFoodDescription() {
        return foodDescription;
    }

    public void setFoodDescription(String foodDescription) {
        this.foodDescription = foodDescription;
    }

    public Double getQuantity() {
        return quantity;
    }

    public void setQuantity(Double quantity) {
        this.quantity = quantity;
    }

    public String getQuantityUnit() {
        return quantityUnit;
    }

    public void setQuantityUnit(String quantityUnit) {
        this.quantityUnit = quantityUnit;
    }

    public LocalDateTime getPreparationTime() {
        return preparationTime;
    }

    public void setPreparationTime(LocalDateTime preparationTime) {
        this.preparationTime = preparationTime;
    }

    public StorageCondition getStorageCondition() {
        return storageCondition;
    }

    public void setStorageCondition(StorageCondition storageCondition) {
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

    public String getPickupAddress() {
        return pickupAddress;
    }

    public void setPickupAddress(String pickupAddress) {
        this.pickupAddress = pickupAddress;
    }

    public Double getLatitude() {
        return latitude;
    }

    public void setLatitude(Double latitude) {
        this.latitude = latitude;
    }

    public Double getLongitude() {
        return longitude;
    }

    public void setLongitude(Double longitude) {
        this.longitude = longitude;
    }

    public LocalDateTime getAvailableFrom() {
        return availableFrom;
    }

    public void setAvailableFrom(LocalDateTime availableFrom) {
        this.availableFrom = availableFrom;
    }

    public LocalDateTime getPickupDeadline() {
        return pickupDeadline;
    }

    public void setPickupDeadline(LocalDateTime pickupDeadline) {
        this.pickupDeadline = pickupDeadline;
    }

    public Double getRemainingUsableMinutes() {
        return remainingUsableMinutes;
    }

    public void setRemainingUsableMinutes(Double remainingUsableMinutes) {
        this.remainingUsableMinutes = remainingUsableMinutes;
    }

    public Double getUrgencyScore() {
        return urgencyScore;
    }

    public void setUrgencyScore(Double urgencyScore) {
        this.urgencyScore = urgencyScore;
    }

    public String getImageUrl() {
        return imageUrl;
    }

    public void setImageUrl(String imageUrl) {
        this.imageUrl = imageUrl;
    }

    public String getAiPredictedFood() {
        return aiPredictedFood;
    }

    public void setAiPredictedFood(String aiPredictedFood) {
        this.aiPredictedFood = aiPredictedFood;
    }

    public Double getAiConfidence() {
        return aiConfidence;
    }

    public void setAiConfidence(Double aiConfidence) {
        this.aiConfidence = aiConfidence;
    }

    public Boolean getAiVerifiedByDonor() {
        return aiVerifiedByDonor;
    }

    public void setAiVerifiedByDonor(Boolean aiVerifiedByDonor) {
        this.aiVerifiedByDonor = aiVerifiedByDonor;
    }
}

