package com.foodflow.repository;

import com.foodflow.model.entity.Donation;
import com.foodflow.model.entity.DonorProfile;
import com.foodflow.model.enums.DonationStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface DonationRepository extends JpaRepository<Donation, Long> {
    List<Donation> findByDonor(DonorProfile donor);
    List<Donation> findByDonorId(Long donorProfileId);
    List<Donation> findByStatus(DonationStatus status);
    List<Donation> findByStatusIn(List<DonationStatus> statuses);
    List<Donation> findByPickupDeadlineBeforeAndStatus(LocalDateTime deadline, DonationStatus status);
    long countByStatus(DonationStatus status);
}

