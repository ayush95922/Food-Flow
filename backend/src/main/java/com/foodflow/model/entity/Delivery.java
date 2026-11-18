package com.foodflow.model.entity;

import com.foodflow.model.enums.DeliveryStatus;
import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "deliveries", indexes = {
    @Index(name = "idx_deliv_status", columnList = "status"),
    @Index(name = "idx_deliv_volunteer", columnList = "volunteer_user_id")
})
public class Delivery {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "allocation_id", nullable = false, unique = true)
    private Allocation allocation;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "volunteer_user_id", nullable = false)
    private User volunteer;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 30)
    private DeliveryStatus status = DeliveryStatus.ASSIGNED;

    private Integer routeSequence = 1;

    private Double distanceKm = 0.0;

    private LocalDateTime pickupEta;

    private LocalDateTime deliveryEta;

    private LocalDateTime actualPickupTime;

    private LocalDateTime actualDeliveryTime;

    @Column(length = 10)
    private String pickupOtp;

    @Column(length = 10)
    private String deliveryOtp;

    @Column(columnDefinition = "TEXT")
    private String notes;

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;

    public Delivery() {
    }

    public Delivery(Allocation allocation, User volunteer, Integer routeSequence, Double distanceKm, LocalDateTime pickupEta, LocalDateTime deliveryEta) {
        this.allocation = allocation;
        this.volunteer = volunteer;
        this.routeSequence = routeSequence;
        this.distanceKm = distanceKm;
        this.pickupEta = pickupEta;
        this.deliveryEta = deliveryEta;
        this.status = DeliveryStatus.ASSIGNED;
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

    public Allocation getAllocation() {
        return allocation;
    }

    public void setAllocation(Allocation allocation) {
        this.allocation = allocation;
    }

    public User getVolunteer() {
        return volunteer;
    }

    public void setVolunteer(User volunteer) {
        this.volunteer = volunteer;
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

    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(LocalDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }
}

