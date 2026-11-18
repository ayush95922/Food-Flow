package com.foodflow.model.entity;

import com.foodflow.model.enums.AllocationStatus;
import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "allocations", indexes = {
    @Index(name = "idx_alloc_status", columnList = "status"),
    @Index(name = "idx_alloc_donation", columnList = "donation_id"),
    @Index(name = "idx_alloc_recipient", columnList = "recipient_id")
})
public class Allocation {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "donation_id", nullable = false)
    private Donation donation;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "recipient_id", nullable = false)
    private RecipientProfile recipient;

    @Column(nullable = false)
    private Double quantityAllocated;

    @Column(nullable = false)
    private Double matchingScore = 0.0;

    private Double distanceKm = 0.0;

    private Double pickupEtaMinutes = 0.0;

    private Double deliveryEtaMinutes = 0.0;

    private Integer ranking = 1;

    @Column(columnDefinition = "TEXT")
    private String explanationJson;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 30)
    private AllocationStatus status = AllocationStatus.PROPOSED;

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;

    public Allocation() {
    }

    public Allocation(Donation donation, RecipientProfile recipient, Double quantityAllocated, Double matchingScore, Double distanceKm, Double pickupEtaMinutes, Double deliveryEtaMinutes, Integer ranking, String explanationJson) {
        this.donation = donation;
        this.recipient = recipient;
        this.quantityAllocated = quantityAllocated;
        this.matchingScore = matchingScore;
        this.distanceKm = distanceKm;
        this.pickupEtaMinutes = pickupEtaMinutes;
        this.deliveryEtaMinutes = deliveryEtaMinutes;
        this.ranking = ranking;
        this.explanationJson = explanationJson;
        this.status = AllocationStatus.PROPOSED;
    }

    @PrePersist
    protected void onCreate() {
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
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

    public Donation getDonation() {
        return donation;
    }

    public void setDonation(Donation donation) {
        this.donation = donation;
    }

    public RecipientProfile getRecipient() {
        return recipient;
    }

    public void setRecipient(RecipientProfile recipient) {
        this.recipient = recipient;
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

    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(LocalDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }
}

