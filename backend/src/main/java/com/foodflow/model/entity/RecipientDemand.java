package com.foodflow.model.entity;

import com.foodflow.model.enums.DemandPriority;
import com.foodflow.model.enums.DemandStatus;
import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "recipient_demands", indexes = {
    @Index(name = "idx_demand_status", columnList = "status"),
    @Index(name = "idx_demand_category", columnList = "foodCategory")
})
public class RecipientDemand {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "recipient_profile_id", nullable = false)
    private RecipientProfile recipient;

    @Column(nullable = false, length = 60)
    private String foodCategory;

    @Column(nullable = false)
    private Double quantityRequired;

    @Column(nullable = false)
    private Double quantityReceived = 0.0;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private DemandPriority priority = DemandPriority.MEDIUM;

    @Column(nullable = false)
    private LocalDateTime requiredBefore;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 30)
    private DemandStatus status = DemandStatus.OPEN;

    @Column(columnDefinition = "TEXT")
    private String notes;

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;

    public RecipientDemand() {
    }

    public RecipientDemand(RecipientProfile recipient, String foodCategory, Double quantityRequired, DemandPriority priority, LocalDateTime requiredBefore, String notes) {
        this.recipient = recipient;
        this.foodCategory = foodCategory;
        this.quantityRequired = quantityRequired;
        this.quantityReceived = 0.0;
        this.priority = priority != null ? priority : DemandPriority.MEDIUM;
        this.requiredBefore = requiredBefore;
        this.status = DemandStatus.OPEN;
        this.notes = notes;
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

    public Double getRemainingQuantity() {
        return Math.max(0.0, this.quantityRequired - this.quantityReceived);
    }

    // Getters and Setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public RecipientProfile getRecipient() {
        return recipient;
    }

    public void setRecipient(RecipientProfile recipient) {
        this.recipient = recipient;
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

    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(LocalDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }
}

