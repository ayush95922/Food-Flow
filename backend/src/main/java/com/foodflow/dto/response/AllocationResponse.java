package com.foodflow.dto.response;

import com.foodflow.model.enums.AllocationStatus;
import java.time.LocalDateTime;

public class AllocationResponse {
    private Long id;
    private Long donationId;
    private String foodName;
    private String foodCategory;
    private Double donationQuantity;
    private Long recipientId;
    private String recipientOrganizationName;
    private String recipientContactPerson;
    private String recipientAddress;
    private Double quantityAllocated;
    private Double matchingScore;
    private Double distanceKm;
    private Double pickupEtaMinutes;
    private Double deliveryEtaMinutes;
    private Integer ranking;
    private String explanationJson;
    private AllocationStatus status;
    private LocalDateTime createdAt;

    public AllocationResponse() {
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getDonationId() {
        return donationId;
    }

    public void setDonationId(Long donationId) {
        this.donationId = donationId;
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

    public Double getDonationQuantity() {
        return donationQuantity;
    }

    public void setDonationQuantity(Double donationQuantity) {
        this.donationQuantity = donationQuantity;
    }

    public Long getRecipientId() {
        return recipientId;
    }

    public void setRecipientId(Long recipientId) {
        this.recipientId = recipientId;
    }

    public String getRecipientOrganizationName() {
        return recipientOrganizationName;
    }

    public void setRecipientOrganizationName(String recipientOrganizationName) {
        this.recipientOrganizationName = recipientOrganizationName;
    }

    public String getRecipientContactPerson() {
        return recipientContactPerson;
    }

    public void setRecipientContactPerson(String recipientContactPerson) {
        this.recipientContactPerson = recipientContactPerson;
    }

    public String getRecipientAddress() {
        return recipientAddress;
    }

    public void setRecipientAddress(String recipientAddress) {
        this.recipientAddress = recipientAddress;
    }

    public Double getQuantityAllocated() {
        return quantityAllocated;
    }

    public void setQuantityAllocated(Double quantityAllocated) {
        this.quantityAllocated = quantityAllocated;
    }

    public Double getMatchingScore() {
        return matchingScore;
    }

    public void setMatchingScore(Double matchingScore) {
        this.matchingScore = matchingScore;
    }

    public Double getDistanceKm() {
        return distanceKm;
    }

    public void setDistanceKm(Double distanceKm) {
        this.distanceKm = distanceKm;
    }

    public Double getPickupEtaMinutes() {
        return pickupEtaMinutes;
    }

    public void setPickupEtaMinutes(Double pickupEtaMinutes) {
        this.pickupEtaMinutes = pickupEtaMinutes;
    }

    public Double getDeliveryEtaMinutes() {
        return deliveryEtaMinutes;
    }

    public void setDeliveryEtaMinutes(Double deliveryEtaMinutes) {
        this.deliveryEtaMinutes = deliveryEtaMinutes;
    }

    public Integer getRanking() {
        return ranking;
    }

    public void setRanking(Integer ranking) {
        this.ranking = ranking;
    }

    public String getExplanationJson() {
        return explanationJson;
    }

    public void setExplanationJson(String explanationJson) {
        this.explanationJson = explanationJson;
    }

    public AllocationStatus getStatus() {
        return status;
    }

    public void setStatus(AllocationStatus status) {
        this.status = status;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
}

