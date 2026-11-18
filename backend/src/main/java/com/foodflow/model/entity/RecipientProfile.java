package com.foodflow.model.entity;

import com.foodflow.model.enums.OrgType;
import jakarta.persistence.*;

@Entity
@Table(name = "recipient_profiles")
public class RecipientProfile {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "user_id", nullable = false, unique = true)
    private User user;

    @Column(nullable = false, length = 150)
    private String organizationName;

    @Column(nullable = false, length = 100)
    private String contactPerson;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 40)
    private OrgType orgType;

    @Column(nullable = false)
    private Double maxHandlingCapacity = 200.0;

    @Column(nullable = false)
    private Double currentDemand = 0.0;

    @Column(length = 255)
    private String acceptedCategories = "any";

    @Column(nullable = false)
    private Double historicalReceived = 0.0;

    @Column(nullable = false)
    private Integer allocationCount = 0;

    @Column(nullable = false)
    private Double priority = 1.0;

    private boolean available = true;

    private boolean verifiedByAdmin = true;

    public RecipientProfile() {
    }

    public RecipientProfile(User user, String organizationName, String contactPerson, OrgType orgType, Double maxHandlingCapacity, String acceptedCategories) {
        this.user = user;
        this.organizationName = organizationName;
        this.contactPerson = contactPerson;
        this.orgType = orgType;
        this.maxHandlingCapacity = maxHandlingCapacity != null ? maxHandlingCapacity : 200.0;
        this.acceptedCategories = (acceptedCategories != null && !acceptedCategories.isBlank()) ? acceptedCategories : "any";
        this.currentDemand = 0.0;
        this.historicalReceived = 0.0;
        this.allocationCount = 0;
        this.priority = 1.0;
        this.available = true;
        this.verifiedByAdmin = true;
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public User getUser() {
        return user;
    }

    public void setUser(User user) {
        this.user = user;
    }

    public String getOrganizationName() {
        return organizationName;
    }

    public void setOrganizationName(String organizationName) {
        this.organizationName = organizationName;
    }

    public String getContactPerson() {
        return contactPerson;
    }

    public void setContactPerson(String contactPerson) {
        this.contactPerson = contactPerson;
    }

    public OrgType getOrgType() {
        return orgType;
    }

    public void setOrgType(OrgType orgType) {
        this.orgType = orgType;
    }

    public Double getMaxHandlingCapacity() {
        return maxHandlingCapacity;
    }

    public void setMaxHandlingCapacity(Double maxHandlingCapacity) {
        this.maxHandlingCapacity = maxHandlingCapacity;
    }

    public Double getCurrentDemand() {
        return currentDemand;
    }

    public void setCurrentDemand(Double currentDemand) {
        this.currentDemand = currentDemand;
    }

    public String getAcceptedCategories() {
        return acceptedCategories;
    }

    public void setAcceptedCategories(String acceptedCategories) {
        this.acceptedCategories = acceptedCategories;
    }

    public Double getHistoricalReceived() {
        return historicalReceived;
    }

    public void setHistoricalReceived(Double historicalReceived) {
        this.historicalReceived = historicalReceived;
    }

    public Integer getAllocationCount() {
        return allocationCount;
    }

    public void setAllocationCount(Integer allocationCount) {
        this.allocationCount = allocationCount;
    }

    public Double getPriority() {
        return priority;
    }

    public void setPriority(Double priority) {
        this.priority = priority;
    }

    public boolean isAvailable() {
        return available;
    }

    public void setAvailable(boolean available) {
        this.available = available;
    }

    public boolean isVerifiedByAdmin() {
        return verifiedByAdmin;
    }

    public void setVerifiedByAdmin(boolean verifiedByAdmin) {
        this.verifiedByAdmin = verifiedByAdmin;
    }
}

