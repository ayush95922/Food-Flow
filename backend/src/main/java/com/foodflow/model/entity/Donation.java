package com.foodflow.model.entity;

import com.foodflow.model.enums.DonationStatus;
import com.foodflow.model.enums.StorageCondition;
import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "donations", indexes = {
    @Index(name = "idx_donation_status", columnList = "status"),
    @Index(name = "idx_donation_category", columnList = "foodCategory"),
    @Index(name = "idx_donation_deadline", columnList = "pickupDeadline")
})
public class Donation {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "donor_profile_id", nullable = false)
    private DonorProfile donor;

    @Column(nullable = false, length = 120)
    private String foodName;

    @Column(nullable = false, length = 60)
    private String foodCategory;

    @Column(columnDefinition = "TEXT")
    private String foodDescription;

    @Column(nullable = false)
    private Double quantity;

    @Column(nullable = false, length = 30)
    private String quantityUnit = "portions";

    @Column(nullable = false)
    private LocalDateTime preparationTime;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 30)
    private StorageCondition storageCondition = StorageCondition.ROOM_TEMP;

    private Double temperatureC;

    @Column(length = 60)
    private String packaging = "covered";

    @Column(nullable = false, length = 255)
    private String pickupAddress;

    @Column(nullable = false)
    private Double latitude;

    @Column(nullable = false)
    private Double longitude;

    private LocalDateTime availableFrom;

    @Column(nullable = false)
    private LocalDateTime pickupDeadline;

    private Double remainingUsableMinutes = 240.0;

    private Double urgencyScore = 0.5;

    @Column(length = 500)
    private String imageUrl;

    @Column(length = 100)
    private String aiPredictedFood;

    private Double aiConfidence;

    private Boolean aiVerifiedByDonor = false;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 30)
    private DonationStatus status = DonationStatus.AVAILABLE;

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;

    public Donation() {
    }

    @PrePersist
    protected void onCreate() {
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
        if (this.availableFrom == null) {
            this.availableFrom = LocalDateTime.now();
        }
        if (this.status == null) {
            this.status = DonationStatus.AVAILABLE;
        }
    }

    @PreUpdate
    protected void onUpdate() {
        this.updatedAt = LocalDateTime.now();
    }

    // Getters and Setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public DonorProfile getDonor() {
        return donor;
    }

    public void setDonor(DonorProfile donor) {
        this.donor = donor;
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

    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(LocalDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }
}

