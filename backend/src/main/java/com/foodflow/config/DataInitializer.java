package com.foodflow.config;

import com.foodflow.model.entity.*;
import com.foodflow.model.enums.*;
import com.foodflow.repository.*;
import com.foodflow.service.DonationService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;

@Component
public class DataInitializer implements CommandLineRunner {

    private static final Logger log = LoggerFactory.getLogger(DataInitializer.class);

    private final UserRepository userRepository;
    private final DonorProfileRepository donorProfileRepository;
    private final RecipientProfileRepository recipientProfileRepository;
    private final RecipientDemandRepository demandRepository;
    private final DonationRepository donationRepository;
    private final PasswordEncoder passwordEncoder;
    private final DonationService donationService;

    public DataInitializer(UserRepository userRepository,
                           DonorProfileRepository donorProfileRepository,
                           RecipientProfileRepository recipientProfileRepository,
                           RecipientDemandRepository demandRepository,
                           DonationRepository donationRepository,
                           PasswordEncoder passwordEncoder,
                           DonationService donationService) {
        this.userRepository = userRepository;
        this.donorProfileRepository = donorProfileRepository;
        this.recipientProfileRepository = recipientProfileRepository;
        this.demandRepository = demandRepository;
        this.donationRepository = donationRepository;
        this.passwordEncoder = passwordEncoder;
        this.donationService = donationService;
    }

    @Override
    public void run(String... args) {
        if (userRepository.count() > 0) {
            log.info("Database already contains data, skipping initialization.");
            return;
        }

        log.info("Seeding initial research demo data...");

        // 1. Admin
        User admin = new User(
                "admin@foodflow.org",
                passwordEncoder.encode("admin123"),
                Role.ROLE_ADMIN,
                "System Administrator",
                "+91-9876543210",
                "Administrative Complex, Main Road",
                "Indore",
                22.7196,
                75.8577
        );
        userRepository.save(admin);

        // 2. Donors
        User donor1User = new User(
                "donor@greenhotel.com",
                passwordEncoder.encode("donor123"),
                Role.ROLE_DONOR,
                "The Grand Palace Hotel",
                "+91-9823456780",
                "45 Ring Road, Scheme 54",
                "Indore",
                22.7533,
                75.8937
        );
        userRepository.save(donor1User);

        DonorProfile donor1 = new DonorProfile(
                donor1User,
                "The Grand Palace Hotel & Banquet",
                "Hotel / Banquet Hall",
                "FSSAI-112233445566",
                "5-star hotel banquet facility with daily surplus high-quality cooked meals and baked items."
        );
        donorProfileRepository.save(donor1);

        User donor2User = new User(
                "canteen@collegename.edu",
                passwordEncoder.encode("donor123"),
                Role.ROLE_DONOR,
                "University Campus Canteen",
                "+91-9898765432",
                "Student Activity Center, South Campus",
                "Indore",
                22.6868,
                75.8654
        );
        userRepository.save(donor2User);

        DonorProfile donor2 = new DonorProfile(
                donor2User,
                "University Campus Central Canteen",
                "College Canteen",
                "FSSAI-998877665544",
                "Prepares bulk fresh food daily for over 2,000 university students and faculty."
        );
        donorProfileRepository.save(donor2);

        // 3. Receivers
        User rec1User = new User(
                "receiver@hopeorphanage.org",
                passwordEncoder.encode("receiver123"),
                Role.ROLE_RECEIVER,
                "Sister Teresa Sharma",
                "+91-9755512345",
                "12 Anand Nagar, Near Old Bus Stand",
                "Indore",
                22.7244,
                75.8711
        );
        userRepository.save(rec1User);

        RecipientProfile rec1 = new RecipientProfile(
                rec1User,
                "Hope Child Care & Orphanage",
                "Sister Teresa Sharma",
                OrgType.ORPHANAGE,
                150.0,
                "cooked_meal,bakery,produce,dairy"
        );
        rec1.setHistoricalReceived(40.0);
        rec1.setAllocationCount(2);
        rec1.setPriority(2.0);
        recipientProfileRepository.save(rec1);

        User rec2User = new User(
                "ngo@annasandesh.org",
                passwordEncoder.encode("receiver123"),
                Role.ROLE_RECEIVER,
                "Dr. Alok Verma",
                "+91-9826098765",
                "78 Malwa Mills Colony",
                "Indore",
                22.7380,
                75.8850
        );
        userRepository.save(rec2User);

        RecipientProfile rec2 = new RecipientProfile(
                rec2User,
                "Anna Sandesh Food Rescue Network",
                "Dr. Alok Verma",
                OrgType.FOOD_BANK,
                300.0,
                "any"
        );
        rec2.setHistoricalReceived(180.0);
        rec2.setAllocationCount(6);
        rec2.setPriority(1.5);
        recipientProfileRepository.save(rec2);

        // 4. Volunteer
        User volUser = new User(
                "volunteer@foodflow.org",
                passwordEncoder.encode("volunteer123"),
                Role.ROLE_VOLUNTEER,
                "Rahul Verma",
                "+91-9123456789",
                "22 Vijay Nagar Square",
                "Indore",
                22.7530,
                75.8900
        );
        userRepository.save(volUser);

        // 5. Demands
        RecipientDemand demand1 = new RecipientDemand(
                rec1,
                "cooked_meal",
                80.0,
                DemandPriority.HIGH,
                LocalDateTime.now().plusHours(4),
                "Lunch meals needed for 80 children."
        );
        demandRepository.save(demand1);
        rec1.setCurrentDemand(80.0);
        recipientProfileRepository.save(rec1);

        RecipientDemand demand2 = new RecipientDemand(
                rec2,
                "any",
                150.0,
                DemandPriority.MEDIUM,
                LocalDateTime.now().plusHours(6),
                "Evening distribution for slum cluster community kitchens."
        );
        demandRepository.save(demand2);
        rec2.setCurrentDemand(150.0);
        recipientProfileRepository.save(rec2);

        // 6. Initial Seed Donations
        Donation don1 = new Donation();
        don1.setDonor(donor1);
        don1.setFoodName("Vegetable Dum Biryani & Raita");
        don1.setFoodCategory("cooked_meal");
        don1.setFoodDescription("Prepared for banquet lunch at 1:00 PM. High quality basmati rice and vegetables kept in thermal containers.");
        don1.setQuantity(60.0);
        don1.setQuantityUnit("portions");
        don1.setPreparationTime(LocalDateTime.now().minusHours(1));
        don1.setStorageCondition(StorageCondition.WARM);
        don1.setTemperatureC(65.0);
        don1.setPackaging("sealed_container");
        don1.setPickupAddress(donor1User.getAddress());
        don1.setLatitude(donor1User.getLatitude());
        don1.setLongitude(donor1User.getLongitude());
        don1.setAvailableFrom(LocalDateTime.now());
        don1.setPickupDeadline(LocalDateTime.now().plusHours(3));
        don1.setRemainingUsableMinutes(180.0);
        don1.setUrgencyScore(0.65);
        don1.setAiPredictedFood("Vegetable Dum Biryani");
        don1.setAiConfidence(0.94);
        don1.setAiVerifiedByDonor(true);
        don1.setStatus(DonationStatus.AVAILABLE);
        donationRepository.save(don1);

        donationService.generateAllocationsForDonation(don1);

        log.info("Demo data seeding completed successfully! Users ready: admin@foodflow.org, donor@greenhotel.com, receiver@hopeorphanage.org, volunteer@foodflow.org");
    }
}

