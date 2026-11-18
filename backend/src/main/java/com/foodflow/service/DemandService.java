package com.foodflow.service;

import com.foodflow.dto.request.CreateDemandRequest;
import com.foodflow.dto.response.DemandResponse;
import com.foodflow.exception.BadRequestException;
import com.foodflow.exception.ResourceNotFoundException;
import com.foodflow.model.entity.RecipientDemand;
import com.foodflow.model.entity.RecipientProfile;
import com.foodflow.model.entity.User;
import com.foodflow.model.enums.DemandStatus;
import com.foodflow.repository.RecipientDemandRepository;
import com.foodflow.repository.RecipientProfileRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class DemandService {

    private final RecipientDemandRepository demandRepository;
    private final RecipientProfileRepository recipientProfileRepository;

    public DemandService(RecipientDemandRepository demandRepository,
                         RecipientProfileRepository recipientProfileRepository) {
        this.demandRepository = demandRepository;
        this.recipientProfileRepository = recipientProfileRepository;
    }

    @Transactional
    public DemandResponse createDemand(CreateDemandRequest req, User recipientUser) {
        RecipientProfile profile = recipientProfileRepository.findByUser(recipientUser)
                .orElseThrow(() -> new BadRequestException("Recipient profile not found for user: " + recipientUser.getEmail()));

        RecipientDemand demand = new RecipientDemand(
                profile,
                req.getFoodCategory(),
                req.getQuantityRequired(),
                req.getPriority(),
                req.getRequiredBefore(),
                req.getNotes()
        );
        demand = demandRepository.save(demand);

        // Update recipient current active demand
        profile.setCurrentDemand(profile.getCurrentDemand() + req.getQuantityRequired());
        recipientProfileRepository.save(profile);

        return toResponse(demand);
    }

    @Transactional(readOnly = true)
    public List<DemandResponse> getDemandsByRecipient(Long recipientProfileId) {
        List<RecipientDemand> list = demandRepository.findByRecipientId(recipientProfileId);
        return list.stream().map(this::toResponse).toList();
    }

    @Transactional(readOnly = true)
    public List<DemandResponse> getAllActiveDemands() {
        List<RecipientDemand> list = demandRepository.findByStatusNot(DemandStatus.FULFILLED);
        return list.stream().map(this::toResponse).toList();
    }

    public DemandResponse toResponse(RecipientDemand d) {
        DemandResponse res = new DemandResponse();
        res.setId(d.getId());
        res.setRecipientProfileId(d.getRecipient().getId());
        res.setRecipientOrganizationName(d.getRecipient().getOrganizationName());
        res.setFoodCategory(d.getFoodCategory());
        res.setQuantityRequired(d.getQuantityRequired());
        res.setQuantityReceived(d.getQuantityReceived());
        res.setRemainingQuantity(d.getRemainingQuantity());
        res.setPriority(d.getPriority());
        res.setRequiredBefore(d.getRequiredBefore());
        res.setStatus(d.getStatus());
        res.setNotes(d.getNotes());
        res.setCreatedAt(d.getCreatedAt());
        return res;
    }
}

