package com.foodflow.service;

import com.foodflow.dto.response.AllocationResponse;
import com.foodflow.exception.BadRequestException;
import com.foodflow.exception.ResourceNotFoundException;
import com.foodflow.model.entity.*;
import com.foodflow.model.enums.AllocationStatus;
import com.foodflow.model.enums.DeliveryStatus;
import com.foodflow.model.enums.DemandStatus;
import com.foodflow.model.enums.DonationStatus;
import com.foodflow.repository.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Random;

@Service
public class MatchingService {

    private final AllocationRepository allocationRepository;
    private final DonationRepository donationRepository;
    private final RecipientProfileRepository recipientProfileRepository;
    private final RecipientDemandRepository recipientDemandRepository;
    private final DeliveryRepository deliveryRepository;
    private final UserRepository userRepository;
    private final DonationService donationService;

    public MatchingService(AllocationRepository allocationRepository,
                           DonationRepository donationRepository,
                           RecipientProfileRepository recipientProfileRepository,
                           RecipientDemandRepository recipientDemandRepository,
                           DeliveryRepository deliveryRepository,
                           UserRepository userRepository,
                           DonationService donationService) {
        this.allocationRepository = allocationRepository;
        this.donationRepository = donationRepository;
        this.recipientProfileRepository = recipientProfileRepository;
        this.recipientDemandRepository = recipientDemandRepository;
        this.deliveryRepository = deliveryRepository;
        this.userRepository = userRepository;
        this.donationService = donationService;
    }

    @Transactional(readOnly = true)
    public List<AllocationResponse> getAllocationsForDonation(Long donationId) {
        List<Allocation> list = allocationRepository.findByDonationId(donationId);
        return list.stream().map(this::toResponse).toList();
    }

    @Transactional(readOnly = true)
    public List<AllocationResponse> getAllocationsForRecipient(Long recipientProfileId) {
        List<Allocation> list = allocationRepository.findByRecipientId(recipientProfileId);
        return list.stream().map(this::toResponse).toList();
    }

    @Transactional
    public List<AllocationResponse> recalculateMatching(Long donationId, String strategy) {
        Donation d = donationRepository.findById(donationId)
                .orElseThrow(() -> new ResourceNotFoundException("Donation not found: " + donationId));
        donationService.generateAllocationsForDonation(d);
        return getAllocationsForDonation(donationId);
    }

    @Transactional
    public AllocationResponse acceptAllocation(Long allocationId, User receiverUser) {
        Allocation alloc = allocationRepository.findById(allocationId)
                .orElseThrow(() -> new ResourceNotFoundException("Allocation not found: " + allocationId));

        if (!alloc.getRecipient().getUser().getId().equals(receiverUser.getId())) {
            throw new BadRequestException("You are not authorized to accept this allocation");
        }

        if (alloc.getStatus() == AllocationStatus.ACCEPTED) {
            throw new BadRequestException("Allocation is already accepted");
        }

        Donation donation = alloc.getDonation();
        if (donation.getStatus() == DonationStatus.DELIVERED || donation.getStatus() == DonationStatus.CANCELLED) {
            throw new BadRequestException("Donation is no longer available (status: " + donation.getStatus() + ")");
        }

        // Concurrency lock: mark allocation accepted
        alloc.setStatus(AllocationStatus.ACCEPTED);
        alloc = allocationRepository.save(alloc);

        donation.setStatus(DonationStatus.ACCEPTED);
        donationRepository.save(donation);

        // Update recipient state
        RecipientProfile profile = alloc.getRecipient();
        double allocatedQty = alloc.getQuantityAllocated();
        profile.setCurrentDemand(Math.max(0.0, profile.getCurrentDemand() - allocatedQty));
        profile.setHistoricalReceived(profile.getHistoricalReceived() + allocatedQty);
        profile.setAllocationCount(profile.getAllocationCount() + 1);
        recipientProfileRepository.save(profile);

        // Update matching open demand
        List<RecipientDemand> openDemands = recipientDemandRepository.findByRecipient(profile);
        for (RecipientDemand d : openDemands) {
            if (d.getStatus() != DemandStatus.FULFILLED &&
                    (d.getFoodCategory().equalsIgnoreCase(donation.getFoodCategory()) || d.getFoodCategory().equalsIgnoreCase("any"))) {
                double needed = d.getRemainingQuantity();
                double fulfill = Math.min(needed, allocatedQty);
                d.setQuantityReceived(d.getQuantityReceived() + fulfill);
                if (d.getQuantityReceived() >= d.getQuantityRequired()) {
                    d.setStatus(DemandStatus.FULFILLED);
                } else {
                    d.setStatus(DemandStatus.PARTIALLY_FULFILLED);
                }
                recipientDemandRepository.save(d);
                break;
            }
        }

        // Automatically assign or prepare a Delivery record for volunteers
        List<User> volunteers = userRepository.findByRole(com.foodflow.model.enums.Role.ROLE_VOLUNTEER);
        User volunteer = !volunteers.isEmpty() ? volunteers.get(0) : receiverUser; // Fallback to current user if no volunteer exists yet

        Delivery delivery = new Delivery();
        delivery.setAllocation(alloc);
        delivery.setVolunteer(volunteer);
        delivery.setStatus(DeliveryStatus.ASSIGNED);
        delivery.setDistanceKm(alloc.getDistanceKm());
        delivery.setPickupEta(LocalDateTime.now().plusMinutes(alloc.getPickupEtaMinutes().longValue()));
        delivery.setDeliveryEta(LocalDateTime.now().plusMinutes(alloc.getDeliveryEtaMinutes().longValue()));
        delivery.setPickupOtp(String.format("%04d", new Random().nextInt(10000)));
        delivery.setDeliveryOtp(String.format("%04d", new Random().nextInt(10000)));
        deliveryRepository.save(delivery);

        donation.setStatus(DonationStatus.PICKUP_ASSIGNED);
        donationRepository.save(donation);

        return toResponse(alloc);
    }

    @Transactional
    public AllocationResponse rejectAllocation(Long allocationId, User receiverUser) {
        Allocation alloc = allocationRepository.findById(allocationId)
                .orElseThrow(() -> new ResourceNotFoundException("Allocation not found: " + allocationId));

        if (!alloc.getRecipient().getUser().getId().equals(receiverUser.getId())) {
            throw new BadRequestException("You are not authorized to reject this allocation");
        }

        alloc.setStatus(AllocationStatus.REJECTED);
        alloc = allocationRepository.save(alloc);
        return toResponse(alloc);
    }

    public AllocationResponse toResponse(Allocation a) {
        AllocationResponse res = new AllocationResponse();
        res.setId(a.getId());
        res.setDonationId(a.getDonation().getId());
        res.setFoodName(a.getDonation().getFoodName());
        res.setFoodCategory(a.getDonation().getFoodCategory());
        res.setDonationQuantity(a.getDonation().getQuantity());
        res.setRecipientId(a.getRecipient().getId());
        res.setRecipientOrganizationName(a.getRecipient().getOrganizationName());
        res.setRecipientContactPerson(a.getRecipient().getContactPerson());
        res.setRecipientAddress(a.getRecipient().getUser().getAddress());
        res.setQuantityAllocated(a.getQuantityAllocated());
        res.setMatchingScore(a.getMatchingScore());
        res.setDistanceKm(a.getDistanceKm());
        res.setPickupEtaMinutes(a.getPickupEtaMinutes());
        res.setDeliveryEtaMinutes(a.getDeliveryEtaMinutes());
        res.setRanking(a.getRanking());
        res.setExplanationJson(a.getExplanationJson());
        res.setStatus(a.getStatus());
        res.setCreatedAt(a.getCreatedAt());
        return res;
    }
}

