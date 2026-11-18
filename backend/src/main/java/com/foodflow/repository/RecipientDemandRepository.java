package com.foodflow.repository;

import com.foodflow.model.entity.RecipientDemand;
import com.foodflow.model.entity.RecipientProfile;
import com.foodflow.model.enums.DemandStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface RecipientDemandRepository extends JpaRepository<RecipientDemand, Long> {
    List<RecipientDemand> findByRecipient(RecipientProfile recipient);
    List<RecipientDemand> findByRecipientId(Long recipientProfileId);
    List<RecipientDemand> findByStatus(DemandStatus status);
    List<RecipientDemand> findByStatusNot(DemandStatus status);
    List<RecipientDemand> findByFoodCategoryIgnoreCase(String foodCategory);
}

