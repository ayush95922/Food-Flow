package com.foodflow.dto.response;

import com.foodflow.model.enums.DonationStatus;
import com.foodflow.model.enums.StorageCondition;
import java.time.LocalDateTime;

public class DonationResponse {
    private Long id;
    private Long donorProfileId;
    private String donorOrganizationName;
    private String donorContactPhone;
    private String foodName;
    private String foodCategory;
    private String foodDescription;
    private Double quantity;
    private String quantityUnit;
    private LocalDateTime preparationTime;
    private StorageCondition storageCondition;
    private Double temperatureC;
    private String packaging;
    private String pickupAddress;
    private Double latitude;
    private Double longitude;
    private LocalDateTime availableFrom;
    private LocalDateTime pickupDeadline;
    private Double remainingUsableMinutes;
    private Double urgencyScore;
    private String imageUrl;
    private String aiPredictedFood;
    private Double aiConfidence;
    private Boolean aiVerifiedByDonor;
    private DonationStatus status;
    private LocalDateTime createdAt;

    public DonationResponse() {
    }

    // Getters and Setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getDonorProfileId() {
        return donorProfileId;
    }

    public void setDonorProfileId(Long donorProfileId) {
        this.donorProfileId = donorProfileId;
    }

    public String getDonorOrganizationName() {
        return donorOrganizationName;
    }

    public void setDonorOrganizationName(String donorOrganizationName) {
        this.donorOrganizationName = donorOrganizationName;
    }

    public String getDonorContactPhone() {
        return donorContactPhone;
    }

    public void setDonorContactPhone(String donorContactPhone) {
        this.donorContactPhone = donorContactPhone;
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

    public DonationStatus getStatus() {
        return status;
    }

    public void setStatus(DonationStatus status) {
        this.status = status;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
}

