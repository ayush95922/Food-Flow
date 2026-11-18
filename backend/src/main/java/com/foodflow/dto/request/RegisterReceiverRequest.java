package com.foodflow.dto.request;

import com.foodflow.model.enums.OrgType;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public class RegisterReceiverRequest {
    @NotBlank
    @Email
    private String email;

    @NotBlank
    private String password;

    @NotBlank
    private String fullName;

    private String phoneNumber;

    @NotBlank
    private String organizationName;

    @NotBlank
    private String contactPerson;

    @NotNull
    private OrgType orgType;

    @NotNull
    private Double maxHandlingCapacity;

    private String acceptedCategories; // comma separated: e.g. "cooked_meal,produce,bakery" or "any"

    @NotBlank
    private String address;

    @NotBlank
    private String city;

    @NotNull
    private Double latitude;

    @NotNull
    private Double longitude;

    public RegisterReceiverRequest() {
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public String getFullName() {
        return fullName;
    }

    public void setFullName(String fullName) {
        this.fullName = fullName;
    }

    public String getPhoneNumber() {
        return phoneNumber;
    }

    public void setPhoneNumber(String phoneNumber) {
        this.phoneNumber = phoneNumber;
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

    public String getAcceptedCategories() {
        return acceptedCategories;
    }

    public void setAcceptedCategories(String acceptedCategories) {
        this.acceptedCategories = acceptedCategories;
    }

    public String getAddress() {
        return address;
    }

    public void setAddress(String address) {
        this.address = address;
    }

    public String getCity() {
        return city;
    }

    public void setCity(String city) {
        this.city = city;
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
}

