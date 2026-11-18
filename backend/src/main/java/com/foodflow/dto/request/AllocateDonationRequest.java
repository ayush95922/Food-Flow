package com.foodflow.dto.request;

import jakarta.validation.constraints.NotNull;

public class AllocateDonationRequest {
    @NotNull
    private Long donationId;

    private String strategy = "dynamic"; // "nearest", "rule_based", "dynamic"

    private Integer topN = 5;

    public AllocateDonationRequest() {
    }

    public AllocateDonationRequest(Long donationId, String strategy, Integer topN) {
        this.donationId = donationId;
        this.strategy = strategy;
        this.topN = topN;
    }

    public Long getDonationId() {
        return donationId;
    }

    public void setDonationId(Long donationId) {
        this.donationId = donationId;
    }

    public String getStrategy() {
        return strategy;
    }

    public void setStrategy(String strategy) {
        this.strategy = strategy;
    }

    public Integer getTopN() {
        return topN;
    }

    public void setTopN(Integer topN) {
        this.topN = topN;
    }
}

