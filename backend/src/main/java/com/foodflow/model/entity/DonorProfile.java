package com.foodflow.model.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "donor_profiles")
public class DonorProfile {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "user_id", nullable = false, unique = true)
    private User user;

    @Column(nullable = false, length = 150)
    private String organizationName;

    @Column(length = 100)
    private String donorType; // Restaurant, Hotel, Hostel, Caterer, Individual

    @Column(length = 80)
    private String foodLicenseNumber;

    @Column(columnDefinition = "TEXT")
    private String description;

    public DonorProfile() {
    }

    public DonorProfile(User user, String organizationName, String donorType, String foodLicenseNumber, String description) {
        this.user = user;
        this.organizationName = organizationName;
        this.donorType = donorType;
        this.foodLicenseNumber = foodLicenseNumber;
        this.description = description;
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

    public String getDonorType() {
        return donorType;
    }

    public void setDonorType(String donorType) {
        this.donorType = donorType;
    }

    public String getFoodLicenseNumber() {
        return foodLicenseNumber;
    }

    public void setFoodLicenseNumber(String foodLicenseNumber) {
        this.foodLicenseNumber = foodLicenseNumber;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }
}

