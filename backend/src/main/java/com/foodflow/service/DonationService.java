package com.foodflow.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.foodflow.dto.request.CreateDonationRequest;
import com.foodflow.dto.request.UsableTimeEstimateRequest;
import com.foodflow.dto.response.DonationResponse;
import com.foodflow.exception.BadRequestException;
import com.foodflow.exception.ResourceNotFoundException;
import com.foodflow.model.entity.Allocation;
import com.foodflow.model.entity.Donation;
import com.foodflow.model.entity.DonorProfile;
import com.foodflow.model.entity.RecipientProfile;
import com.foodflow.model.entity.User;
import com.foodflow.model.enums.DonationStatus;
import com.foodflow.model.enums.Role;
import com.foodflow.repository.AllocationRepository;
import com.foodflow.repository.DonationRepository;
import com.foodflow.repository.DonorProfileRepository;
import com.foodflow.repository.RecipientProfileRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Duration;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@Service
public class DonationService {

    private final DonationRepository donationRepository;
    private final DonorProfileRepository donorProfileRepository;
    private final RecipientProfileRepository recipientProfileRepository;
    private final AllocationRepository allocationRepository;
    private final AiIntegrationService aiIntegrationService;
    private final ObjectMapper objectMapper;

    public DonationService(DonationRepository donationRepository,
                           DonorProfileRepository donorProfileRepository,
                           RecipientProfileRepository recipientProfileRepository,
                           AllocationRepository allocationRepository,
                           AiIntegrationService aiIntegrationService,
                           ObjectMapper objectMapper) {
        this.donationRepository = donationRepository;
        this.donorProfileRepository = donorProfileRepository;
        this.recipientProfileRepository = recipientProfileRepository;
        this.allocationRepository = allocationRepository;
        this.aiIntegrationService = aiIntegrationService;
        this.objectMapper = objectMapper;
    }

    @Transactional
    public DonationResponse createDonation(CreateDonationRequest req, User donorUser) {
        DonorProfile profile = donorProfileRepository.findByUser(donorUser)
                .orElseThrow(() -> new BadRequestException("Donor profile not found for user: " + donorUser.getEmail()));

        Donation donation = new Donation();
        donation.setDonor(profile);
        donation.setFoodName(req.getFoodName());
        donation.setFoodCategory(req.getFoodCategory());
        donation.setFoodDescription(req.getFoodDescription());
        donation.setQuantity(req.getQuantity());
        donation.setQuantityUnit(req.getQuantityUnit() != null ? req.getQuantityUnit() : "portions");
        donation.setPreparationTime(req.getPreparationTime());
        donation.setStorageCondition(req.getStorageCondition());
        donation.setTemperatureC(req.getTemperatureC());
        donation.setPackaging(req.getPackaging() != null ? req.getPackaging() : "covered");
        donation.setPickupAddress(req.getPickupAddress());
        donation.setLatitude(req.getLatitude());
        donation.setLongitude(req.getLongitude());
        donation.setAvailableFrom(req.getAvailableFrom() != null ? req.getAvailableFrom() : LocalDateTime.now());
        donation.setPickupDeadline(req.getPickupDeadline());
        donation.setImageUrl(req.getImageUrl());
        donation.setAiPredictedFood(req.getAiPredictedFood());
        donation.setAiConfidence(req.getAiConfidence());
        donation.setAiVerifiedByDonor(req.getAiVerifiedByDonor() != null ? req.getAiVerifiedByDonor() : false);
        donation.setStatus(DonationStatus.AVAILABLE);

        // Usable time prediction if not explicitly provided
        if (req.getRemainingUsableMinutes() == null) {
            UsableTimeEstimateRequest utReq = new UsableTimeEstimateRequest();
            utReq.setFoodCategory(donation.getFoodCategory());
            utReq.setFoodType(donation.getFoodName());
            utReq.setPreparedAt(donation.getPreparationTime());
            utReq.setStorageCondition(donation.getStorageCondition().name().toLowerCase());
            utReq.setTemperatureC(donation.getTemperatureC());
            utReq.setPackaging(donation.getPackaging());
            long elapsed = Math.max(0, Duration.between(donation.getPreparationTime(), LocalDateTime.now()).toMinutes());
            utReq.setElapsedMinutes((double) elapsed);

            Map<String, Object> utEstimate = aiIntegrationService.estimateUsableTime(utReq);
            if (utEstimate != null && utEstimate.containsKey("estimated_remaining_minutes")) {
                Number n = (Number) utEstimate.get("estimated_remaining_minutes");
                donation.setRemainingUsableMinutes(n.doubleValue());
            } else {
                donation.setRemainingUsableMinutes(240.0);
            }
        } else {
            donation.setRemainingUsableMinutes(req.getRemainingUsableMinutes());
        }

        // Calculate initial urgency
        double usableHours = donation.getRemainingUsableMinutes() / 60.0;
        double urgency = Math.max(0.1, Math.min(1.0, 1.0 - (usableHours / 8.0)));
        donation.setUrgencyScore(urgency);

        donation = donationRepository.save(donation);

        // Compute initial AI recommendations immediately
        generateAllocationsForDonation(donation);

        return toResponse(donation);
    }

    @Transactional
    public void generateAllocationsForDonation(Donation donation) {
        List<RecipientProfile> recipients = recipientProfileRepository.findByAvailableTrue();
        if (recipients.isEmpty()) return;

        Map<String, Object> matchResult = aiIntegrationService.recommendMatches(donation, recipients, "dynamic", 5);
        if (matchResult != null && matchResult.containsKey("results")) {
            List<?> resultsList = (List<?>) matchResult.get("results");
            if (!resultsList.isEmpty()) {
                Map<?, ?> firstRes = (Map<?, ?>) resultsList.get(0);
                List<?> allocs = (List<?>) firstRes.get("allocations");
                if (allocs != null) {
                    int rank = 1;
                    for (Object item : allocs) {
                        Map<?, ?> am = (Map<?, ?>) item;
                        String recIdStr = (String) am.get("recipient_id");
                        Long recId = null;
                        if (am.containsKey("profile_id")) {
                            recId = ((Number) am.get("profile_id")).longValue();
                        } else if (recIdStr != null && recIdStr.startsWith("REC-")) {
                            recId = Long.parseLong(recIdStr.substring(4));
                        }

                        if (recId != null) {
                            var recOpt = recipientProfileRepository.findById(recId);
                            if (recOpt.isPresent()) {
                                Allocation alloc = new Allocation();
                                alloc.setDonation(donation);
                                alloc.setRecipient(recOpt.get());
                                Number qtyNum = (Number) am.get("quantity");
                                alloc.setQuantityAllocated(qtyNum != null ? qtyNum.doubleValue() : donation.getQuantity());
                                Number scNum = (Number) am.get("score");
                                alloc.setMatchingScore(scNum != null ? scNum.doubleValue() : 0.85);
                                Number distNum = (Number) am.get("distance_km");
                                alloc.setDistanceKm(distNum != null ? distNum.doubleValue() : 2.5);
                                Number pEta = (Number) am.get("pickup_eta_minutes");
                                alloc.setPickupEtaMinutes(pEta != null ? pEta.doubleValue() : 15.0);
                                Number dEta = (Number) am.get("delivery_eta_minutes");
                                alloc.setDeliveryEtaMinutes(dEta != null ? dEta.doubleValue() : 30.0);
                                alloc.setRanking(rank++);

                                Object expl = am.get("explanation");
                                try {
                                    alloc.setExplanationJson(expl != null ? objectMapper.writeValueAsString(expl) : null);
                                } catch (Exception ignored) {}

                                allocationRepository.save(alloc);
                            }
                        }
                    }
                    donation.setStatus(DonationStatus.MATCHED);
                    donationRepository.save(donation);
                }
            }
        }
    }

    @Transactional(readOnly = true)
    public List<DonationResponse> getDonationsByDonor(Long donorProfileId) {
        List<Donation> list = donationRepository.findByDonorId(donorProfileId);
        return list.stream().map(this::toResponse).toList();
    }

    @Transactional(readOnly = true)
    public List<DonationResponse> getAllAvailableDonations() {
        List<Donation> list = donationRepository.findByStatusIn(List.of(DonationStatus.AVAILABLE, DonationStatus.MATCHED));
        return list.stream().map(this::toResponse).toList();
    }

    @Transactional(readOnly = true)
    public DonationResponse getDonationById(Long id) {
        Donation d = donationRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Donation not found: " + id));
        return toResponse(d);
    }

    @Transactional
    public DonationResponse cancelDonation(Long id, User currentUser) {
        Donation d = donationRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Donation not found: " + id));

        if (currentUser.getRole() != Role.ROLE_ADMIN && !d.getDonor().getUser().getId().equals(currentUser.getId())) {
            throw new BadRequestException("You are not authorized to cancel this donation");
        }

        if (d.getStatus() == DonationStatus.DELIVERED) {
            throw new BadRequestException("Cannot cancel already delivered donation");
        }

        d.setStatus(DonationStatus.CANCELLED);
        d = donationRepository.save(d);
        return toResponse(d);
    }

    public DonationResponse toResponse(Donation d) {
        DonationResponse res = new DonationResponse();
        res.setId(d.getId());
        res.setDonorProfileId(d.getDonor().getId());
        res.setDonorOrganizationName(d.getDonor().getOrganizationName());
        res.setDonorContactPhone(d.getDonor().getUser().getPhoneNumber());
        res.setFoodName(d.getFoodName());
        res.setFoodCategory(d.getFoodCategory());
        res.setFoodDescription(d.getFoodDescription());
        res.setQuantity(d.getQuantity());
        res.setQuantityUnit(d.getQuantityUnit());
        res.setPreparationTime(d.getPreparationTime());
        res.setStorageCondition(d.getStorageCondition());
        res.setTemperatureC(d.getTemperatureC());
        res.setPackaging(d.getPackaging());
        res.setPickupAddress(d.getPickupAddress());
        res.setLatitude(d.getLatitude());
        res.setLongitude(d.getLongitude());
        res.setAvailableFrom(d.getAvailableFrom());
        res.setPickupDeadline(d.getPickupDeadline());
        res.setRemainingUsableMinutes(d.getRemainingUsableMinutes());
        res.setUrgencyScore(d.getUrgencyScore());
        res.setImageUrl(d.getImageUrl());
        res.setAiPredictedFood(d.getAiPredictedFood());
        res.setAiConfidence(d.getAiConfidence());
        res.setAiVerifiedByDonor(d.getAiVerifiedByDonor());
        res.setStatus(d.getStatus());
        res.setCreatedAt(d.getCreatedAt());
        return res;
    }
}

