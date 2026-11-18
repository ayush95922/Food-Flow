package com.foodflow.repository;

import com.foodflow.model.entity.Allocation;
import com.foodflow.model.entity.Donation;
import com.foodflow.model.entity.RecipientProfile;
import com.foodflow.model.enums.AllocationStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface AllocationRepository extends JpaRepository<Allocation, Long> {
    List<Allocation> findByDonation(Donation donation);
    List<Allocation> findByDonationId(Long donationId);
    List<Allocation> findByRecipient(RecipientProfile recipient);
    List<Allocation> findByRecipientId(Long recipientProfileId);
    List<Allocation> findByStatus(AllocationStatus status);
    Optional<Allocation> findByDonationIdAndRecipientId(Long donationId, Long recipientId);
}

