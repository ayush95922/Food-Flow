package com.foodflow.dto.response;

public class DashboardStatsResponse {
    private long totalUsers;
    private long totalDonors;
    private long totalReceivers;
    private long totalVolunteers;
    private long totalDonations;
    private long availableDonations;
    private long matchedDonations;
    private long deliveredDonations;
    private long expiredDonations;
    private double totalPortionsRedistributed;
    private double totalUnmetDemand;
    private double currentFairnessIndex;

    public DashboardStatsResponse() {
    }

    public long getTotalUsers() {
        return totalUsers;
    }

    public void setTotalUsers(long totalUsers) {
        this.totalUsers = totalUsers;
    }

    public long getTotalDonors() {
        return totalDonors;
    }

    public void setTotalDonors(long totalDonors) {
        this.totalDonors = totalDonors;
    }

    public long getTotalReceivers() {
        return totalReceivers;
    }

    public void setTotalReceivers(long totalReceivers) {
        this.totalReceivers = totalReceivers;
    }

    public long getTotalVolunteers() {
        return totalVolunteers;
    }

    public void setTotalVolunteers(long totalVolunteers) {
        this.totalVolunteers = totalVolunteers;
    }

    public long getTotalDonations() {
        return totalDonations;
    }

    public void setTotalDonations(long totalDonations) {
        this.totalDonations = totalDonations;
    }

    public long getAvailableDonations() {
        return availableDonations;
    }

    public void setAvailableDonations(long availableDonations) {
        this.availableDonations = availableDonations;
    }

    public long getMatchedDonations() {
        return matchedDonations;
    }

    public void setMatchedDonations(long matchedDonations) {
        this.matchedDonations = matchedDonations;
    }

    public long getDeliveredDonations() {
        return deliveredDonations;
    }

    public void setDeliveredDonations(long deliveredDonations) {
        this.deliveredDonations = deliveredDonations;
    }

    public long getExpiredDonations() {
        return expiredDonations;
    }

    public void setExpiredDonations(long expiredDonations) {
        this.expiredDonations = expiredDonations;
    }

    public double getTotalPortionsRedistributed() {
        return totalPortionsRedistributed;
    }

    public void setTotalPortionsRedistributed(double totalPortionsRedistributed) {
        this.totalPortionsRedistributed = totalPortionsRedistributed;
    }

    public double getTotalUnmetDemand() {
        return totalUnmetDemand;
    }

    public void setTotalUnmetDemand(double totalUnmetDemand) {
        this.totalUnmetDemand = totalUnmetDemand;
    }

    public double getCurrentFairnessIndex() {
        return currentFairnessIndex;
    }

    public void setCurrentFairnessIndex(double currentFairnessIndex) {
        this.currentFairnessIndex = currentFairnessIndex;
    }
}

