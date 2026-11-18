package com.foodflow.repository;

import com.foodflow.model.entity.Delivery;
import com.foodflow.model.entity.User;
import com.foodflow.model.enums.DeliveryStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface DeliveryRepository extends JpaRepository<Delivery, Long> {
    List<Delivery> findByVolunteer(User volunteer);
    List<Delivery> findByVolunteerId(Long volunteerUserId);
    List<Delivery> findByStatus(DeliveryStatus status);
    Optional<Delivery> findByAllocationId(Long allocationId);
    long countByStatus(DeliveryStatus status);
}

