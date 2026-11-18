package com.foodflow.dto.response;

import com.foodflow.model.enums.DeliveryStatus;
import java.time.LocalDateTime;

public class DeliveryResponse {
    private Long id;
    private Long allocationId;
    private Long donationId;
    private String foodName;
    private String foodCategory;
    private Double quantity;
    private String quantityUnit;
    private String donorOrganizationName;
    private String pickupAddress;
    private Double pickupLat;
    private Double pickupLon;
    private String recipientOrganizationName;
    private String recipientContactPerson;
    private String deliveryAddress;
    private Double deliveryLat;
    private Double deliveryLon;
    private Long volunteerId;
    private String volunteerName;
    private String volunteerPhone;
    private DeliveryStatus status;
    private Integer routeSequence;
    private Double distanceKm;
    private LocalDateTime pickupEta;
    private LocalDateTime deliveryEta;
    private LocalDateTime actualPickupTime;
    private LocalDateTime actualDeliveryTime;
    private String pickupOtp;
    private String deliveryOtp;
    private String notes;
    private LocalDateTime createdAt;

    public DeliveryResponse() {
    }

    // Getters and Setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getAllocationId() {
        return allocationId;
    }

    public void setAllocationId(Long allocationId) {
        this.allocationId = allocationId;
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

    public String getDonorOrganizationName() {
        return donorOrganizationName;
    }

    public void setDonorOrganizationName(String donorOrganizationName) {
        this.donorOrganizationName = donorOrganizationName;
    }

    public String getPickupAddress() {
        return pickupAddress;
    }

    public void setPickupAddress(String pickupAddress) {
        this.pickupAddress = pickupAddress;
    }

    public Double getPickupLat() {
        return pickupLat;
    }

    public void setPickupLat(Double pickupLat) {
        this.pickupLat = pickupLat;
    }

    public Double getPickupLon() {
        return pickupLon;
    }

    public void setPickupLon(Double pickupLon) {
        this.pickupLon = pickupLon;
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

    public String getDeliveryAddress() {
        return deliveryAddress;
    }

    public void setDeliveryAddress(String deliveryAddress) {
        this.deliveryAddress = deliveryAddress;
    }

    public Double getDeliveryLat() {
        return deliveryLat;
    }

    public void setDeliveryLat(Double deliveryLat) {
        this.deliveryLat = deliveryLat;
    }

    public Double getDeliveryLon() {
        return deliveryLon;
    }

    public void setDeliveryLon(Double deliveryLon) {
        this.deliveryLon = deliveryLon;
    }

    public Long getVolunteerId() {
        return volunteerId;
    }

    public void setVolunteerId(Long volunteerId) {
        this.volunteerId = volunteerId;
    }

    public String getVolunteerName() {
        return volunteerName;
    }

    public void setVolunteerName(String volunteerName) {
        this.volunteerName = volunteerName;
    }

    public String getVolunteerPhone() {
        return volunteerPhone;
    }

    public void setVolunteerPhone(String volunteerPhone) {
        this.volunteerPhone = volunteerPhone;
    }

    public DeliveryStatus getStatus() {
        return status;
    }

    public void setStatus(DeliveryStatus status) {
        this.status = status;
    }

    public Integer getRouteSequence() {
        return routeSequence;
    }

    public void setRouteSequence(Integer routeSequence) {
        this.routeSequence = routeSequence;
    }

    public Double getDistanceKm() {
        return distanceKm;
    }

    public void setDistanceKm(Double distanceKm) {
        this.distanceKm = distanceKm;
    }

    public LocalDateTime getPickupEta() {
        return pickupEta;
    }

    public void setPickupEta(LocalDateTime pickupEta) {
        this.pickupEta = pickupEta;
    }

    public LocalDateTime getDeliveryEta() {
        return deliveryEta;
    }

    public void setDeliveryEta(LocalDateTime deliveryEta) {
        this.deliveryEta = deliveryEta;
    }

    public LocalDateTime getActualPickupTime() {
        return actualPickupTime;
    }

    public void setActualPickupTime(LocalDateTime actualPickupTime) {
        this.actualPickupTime = actualPickupTime;
    }

    public LocalDateTime getActualDeliveryTime() {
        return actualDeliveryTime;
    }

    public void setActualDeliveryTime(LocalDateTime actualDeliveryTime) {
        this.actualDeliveryTime = actualDeliveryTime;
    }

    public String getPickupOtp() {
        return pickupOtp;
    }

    public void setPickupOtp(String pickupOtp) {
        this.pickupOtp = pickupOtp;
    }

    public String getDeliveryOtp() {
        return deliveryOtp;
    }

    public void setDeliveryOtp(String deliveryOtp) {
        this.deliveryOtp = deliveryOtp;
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

