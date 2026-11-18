package com.foodflow.model.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "research_experiments")
public class ResearchExperiment {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 120)
    private String experimentName;

    @Column(nullable = false, length = 50)
    private String strategy;

    private Double demandSupplyRatio;

    private Double redistributedQuantity;

    private Double potentialWastage;

    private Double unmetDemand;

    private Integer recipientsServed;

    private Double avgTransportKm;

    private Double jainFairness;

    private Double matchingTimeMs;

    @Column(columnDefinition = "LONGTEXT")
    private String resultsJson;

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    public ResearchExperiment() {
    }

    public ResearchExperiment(String experimentName, String strategy, Double demandSupplyRatio, Double redistributedQuantity, Double potentialWastage, Double unmetDemand, Integer recipientsServed, Double avgTransportKm, Double jainFairness, Double matchingTimeMs, String resultsJson) {
        this.experimentName = experimentName;
        this.strategy = strategy;
        this.demandSupplyRatio = demandSupplyRatio;
        this.redistributedQuantity = redistributedQuantity;
        this.potentialWastage = potentialWastage;
        this.unmetDemand = unmetDemand;
        this.recipientsServed = recipientsServed;
        this.avgTransportKm = avgTransportKm;
        this.jainFairness = jainFairness;
        this.matchingTimeMs = matchingTimeMs;
        this.resultsJson = resultsJson;
    }

    @PrePersist
    protected void onCreate() {
        this.createdAt = LocalDateTime.now();
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getExperimentName() {
        return experimentName;
    }

    public void setExperimentName(String experimentName) {
        this.experimentName = experimentName;
    }

    public String getStrategy() {
        return strategy;
    }

    public void setStrategy(String strategy) {
        this.strategy = strategy;
    }

    public Double getDemandSupplyRatio() {
        return demandSupplyRatio;
    }

    public void setDemandSupplyRatio(Double demandSupplyRatio) {
        this.demandSupplyRatio = demandSupplyRatio;
    }

    public Double getRedistributedQuantity() {
        return redistributedQuantity;
    }

    public void setRedistributedQuantity(Double redistributedQuantity) {
        this.redistributedQuantity = redistributedQuantity;
    }

    public Double getPotentialWastage() {
        return potentialWastage;
    }

    public void setPotentialWastage(Double potentialWastage) {
        this.potentialWastage = potentialWastage;
    }

    public Double getUnmetDemand() {
        return unmetDemand;
    }

    public void setUnmetDemand(Double unmetDemand) {
        this.unmetDemand = unmetDemand;
    }

    public Integer getRecipientsServed() {
        return recipientsServed;
    }

    public void setRecipientsServed(Integer recipientsServed) {
        this.recipientsServed = recipientsServed;
    }

    public Double getAvgTransportKm() {
        return avgTransportKm;
    }

    public void setAvgTransportKm(Double avgTransportKm) {
        this.avgTransportKm = avgTransportKm;
    }

    public Double getJainFairness() {
        return jainFairness;
    }

    public void setJainFairness(Double jainFairness) {
        this.jainFairness = jainFairness;
    }

    public Double getMatchingTimeMs() {
        return matchingTimeMs;
    }

    public void setMatchingTimeMs(Double matchingTimeMs) {
        this.matchingTimeMs = matchingTimeMs;
    }

    public String getResultsJson() {
        return resultsJson;
    }

    public void setResultsJson(String resultsJson) {
        this.resultsJson = resultsJson;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
}

