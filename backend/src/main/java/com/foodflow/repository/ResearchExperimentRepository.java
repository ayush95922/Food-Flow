package com.foodflow.repository;

import com.foodflow.model.entity.ResearchExperiment;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ResearchExperimentRepository extends JpaRepository<ResearchExperiment, Long> {
    List<ResearchExperiment> findByStrategy(String strategy);
    List<ResearchExperiment> findAllByOrderByCreatedAtDesc();
}

