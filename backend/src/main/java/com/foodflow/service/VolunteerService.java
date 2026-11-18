package com.foodflow.service;

import com.foodflow.dto.response.DeliveryResponse;
import com.foodflow.exception.BadRequestException;
import com.foodflow.exception.ResourceNotFoundException;
import com.foodflow.model.entity.Allocation;
import com.foodflow.model.entity.Delivery;
import com.foodflow.model.entity.Donation;
import com.foodflow.model.entity.User;
import com.foodflow.model.enums.AllocationStatus;
import com.foodflow.model.enums.DeliveryStatus;
import com.foodflow.model.enums.DonationStatus;
import com.foodflow.repository.AllocationRepository;
import com.foodflow.repository.DeliveryRepository;
import com.foodflow.repository.DonationRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

@Service
public class VolunteerService {

    private final DeliveryRepository deliveryRepository;
    private final DonationRepository donationRepository;
    private final AllocationRepository allocationRepository;

    public VolunteerService(DeliveryRepository deliveryRepository,
                            DonationRepository donationRepository,
                            AllocationRepository allocationRepository) {
        this.deliveryRepository = deliveryRepository;
        this.donationRepository = donationRepository;
        this.allocationRepository = allocationRepository;
    }

    @Transactional(readOnly = true)
    public List<DeliveryResponse> getDeliveriesForVolunteer(User volunteer) {
        List<Delivery> list = deliveryRepository.findByVolunteerId(volunteer.getId());
        return list.stream().map(this::toResponse).toList();
    }

    @Transactional(readOnly = true)
    public List<DeliveryResponse> getAllDeliveries() {
        List<Delivery> list = deliveryRepository.findAll();
        return list.stream().map(this::toResponse).toList();
    }

    @Transactional
    public DeliveryResponse updateDeliveryStatus(Long deliveryId, DeliveryStatus newStatus, String notes, User volunteer) {
        Delivery delivery = deliveryRepository.findById(deliveryId)
                .orElseThrow(() -> new ResourceNotFoundException("Delivery not found: " + deliveryId));

        delivery.setStatus(newStatus);
        if (notes != null && !notes.isBlank()) {
            delivery.setNotes(notes);
        }

        Allocation alloc = delivery.getAllocation();
        Donation donation = alloc.getDonation();

        if (newStatus == DeliveryStatus.PICKED_UP) {
            delivery.setActualPickupTime(LocalDateTime.now());
            donation.setStatus(DonationStatus.PICKED_UP);
            donationRepository.save(donation);
        } else if (newStatus == DeliveryStatus.DELIVERED) {
            delivery.setActualDeliveryTime(LocalDateTime.now());
            donation.setStatus(DonationStatus.DELIVERED);
            alloc.setStatus(AllocationStatus.FULFILLED);
            donationRepository.save(donation);
            allocationRepository.save(alloc);
        } else if (newStatus == DeliveryStatus.CANCELLED) {
            donation.setStatus(DonationStatus.AVAILABLE);
            alloc.setStatus(AllocationStatus.REJECTED);
            donationRepository.save(donation);
            allocationRepository.save(alloc);
        }

        delivery = deliveryRepository.save(delivery);
        return toResponse(delivery);
    }

    public DeliveryResponse toResponse(Delivery d) {
        DeliveryResponse res = new DeliveryResponse();
        res.setId(d.getId());
        res.setAllocationId(d.getAllocation().getId());
        res.setDonationId(d.getAllocation().getDonation().getId());
        res.setFoodName(d.getAllocation().getDonation().getFoodName());
        res.setFoodCategory(d.getAllocation().getDonation().getFoodCategory());
        res.setQuantity(d.getAllocation().getQuantityAllocated());
        res.setQuantityUnit(d.getAllocation().getDonation().getQuantityUnit());

        res.setDonorOrganizationName(d.getAllocation().getDonation().getDonor().getOrganizationName());
        res.setPickupAddress(d.getAllocation().getDonation().getPickupAddress());
        res.setPickupLat(d.getAllocation().getDonation().getLatitude());
        res.setPickupLon(d.getAllocation().getDonation().getLongitude());

        res.setRecipientOrganizationName(d.getAllocation().getRecipient().getOrganizationName());
        res.setRecipientContactPerson(d.getAllocation().getRecipient().getContactPerson());
        res.setDeliveryAddress(d.getAllocation().getRecipient().getUser().getAddress());
        res.setDeliveryLat(d.getAllocation().getRecipient().getUser().getLatitude());
        res.setDeliveryLon(d.getAllocation().getRecipient().getUser().getLongitude());

        res.setVolunteerId(d.getVolunteer().getId());
        res.setVolunteerName(d.getVolunteer().getFullName());
        res.setVolunteerPhone(d.getVolunteer().getPhoneNumber());

        res.setStatus(d.getStatus());
        res.setRouteSequence(d.getRouteSequence());
        res.setDistanceKm(d.getDistanceKm());
        res.setPickupEta(d.getPickupEta());
        res.setDeliveryEta(d.getDeliveryEta());
        res.setActualPickupTime(d.getActualPickupTime());
        res.setActualDeliveryTime(d.getActualDeliveryTime());
        res.setPickupOtp(d.getPickupOtp());
        res.setDeliveryOtp(d.getDeliveryOtp());
        res.setNotes(d.getNotes());
        res.setCreatedAt(d.getCreatedAt());
        return res;
    }
}

