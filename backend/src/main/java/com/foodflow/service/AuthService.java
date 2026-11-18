package com.foodflow.service;

import com.foodflow.config.JwtTokenProvider;
import com.foodflow.dto.request.LoginRequest;
import com.foodflow.dto.request.RegisterDonorRequest;
import com.foodflow.dto.request.RegisterReceiverRequest;
import com.foodflow.dto.request.RegisterVolunteerRequest;
import com.foodflow.dto.response.AuthResponse;
import com.foodflow.exception.BadRequestException;
import com.foodflow.model.entity.DonorProfile;
import com.foodflow.model.entity.RecipientProfile;
import com.foodflow.model.entity.User;
import com.foodflow.model.enums.OrgType;
import com.foodflow.model.enums.Role;
import com.foodflow.repository.DonorProfileRepository;
import com.foodflow.repository.RecipientProfileRepository;
import com.foodflow.repository.UserRepository;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class AuthService {

    private final UserRepository userRepository;
    private final DonorProfileRepository donorProfileRepository;
    private final RecipientProfileRepository recipientProfileRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtTokenProvider tokenProvider;

    public AuthService(UserRepository userRepository,
                       DonorProfileRepository donorProfileRepository,
                       RecipientProfileRepository recipientProfileRepository,
                       PasswordEncoder passwordEncoder,
                       JwtTokenProvider tokenProvider) {
        this.userRepository = userRepository;
        this.donorProfileRepository = donorProfileRepository;
        this.recipientProfileRepository = recipientProfileRepository;
        this.passwordEncoder = passwordEncoder;
        this.tokenProvider = tokenProvider;
    }

    @Transactional
    public AuthResponse registerDonor(RegisterDonorRequest req) {
        if (userRepository.existsByEmail(req.getEmail())) {
            throw new BadRequestException("Email is already registered: " + req.getEmail());
        }

        User user = new User(
                req.getEmail(),
                passwordEncoder.encode(req.getPassword()),
                Role.ROLE_DONOR,
                req.getFullName(),
                req.getPhoneNumber(),
                req.getAddress(),
                req.getCity(),
                req.getLatitude(),
                req.getLongitude()
        );
        user = userRepository.save(user);

        DonorProfile profile = new DonorProfile(
                user,
                req.getOrganizationName(),
                req.getDonorType(),
                req.getFoodLicenseNumber(),
                req.getDescription()
        );
        profile = donorProfileRepository.save(profile);

        String token = tokenProvider.generateToken(user.getEmail(), user.getRole().name(), user.getId());
        return new AuthResponse(token, user.getId(), user.getEmail(), user.getRole().name(), user.getFullName(), profile.getId(), profile.getOrganizationName());
    }

    @Transactional
    public AuthResponse registerReceiver(RegisterReceiverRequest req) {
        if (userRepository.existsByEmail(req.getEmail())) {
            throw new BadRequestException("Email is already registered: " + req.getEmail());
        }

        User user = new User(
                req.getEmail(),
                passwordEncoder.encode(req.getPassword()),
                Role.ROLE_RECEIVER,
                req.getFullName(),
                req.getPhoneNumber(),
                req.getAddress(),
                req.getCity(),
                req.getLatitude(),
                req.getLongitude()
        );
        user = userRepository.save(user);

        RecipientProfile profile = new RecipientProfile(
                user,
                req.getOrganizationName(),
                req.getContactPerson(),
                req.getOrgType(),
                req.getMaxHandlingCapacity(),
                req.getAcceptedCategories()
        );
        profile = recipientProfileRepository.save(profile);

        String token = tokenProvider.generateToken(user.getEmail(), user.getRole().name(), user.getId());
        return new AuthResponse(token, user.getId(), user.getEmail(), user.getRole().name(), user.getFullName(), profile.getId(), profile.getOrganizationName());
    }

    @Transactional
    public AuthResponse registerVolunteer(RegisterVolunteerRequest req) {
        if (userRepository.existsByEmail(req.getEmail())) {
            throw new BadRequestException("Email is already registered: " + req.getEmail());
        }

        User user = new User(
                req.getEmail(),
                passwordEncoder.encode(req.getPassword()),
                Role.ROLE_VOLUNTEER,
                req.getFullName(),
                req.getPhoneNumber(),
                req.getAddress(),
                req.getCity(),
                req.getLatitude(),
                req.getLongitude()
        );
        user = userRepository.save(user);

        String token = tokenProvider.generateToken(user.getEmail(), user.getRole().name(), user.getId());
        return new AuthResponse(token, user.getId(), user.getEmail(), user.getRole().name(), user.getFullName(), null, null);
    }

    @Transactional(readOnly = true)
    public AuthResponse login(LoginRequest req) {
        User user = userRepository.findByEmail(req.getEmail())
                .orElseThrow(() -> new BadRequestException("Invalid email or password"));

        if (!passwordEncoder.matches(req.getPassword(), user.getPassword())) {
            throw new BadRequestException("Invalid email or password");
        }

        if (!user.isEnabled()) {
            throw new BadRequestException("Account is currently disabled. Please contact administrator.");
        }

        Long profileId = null;
        String orgName = null;

        if (user.getRole() == Role.ROLE_DONOR) {
            var dp = donorProfileRepository.findByUser(user);
            if (dp.isPresent()) {
                profileId = dp.get().getId();
                orgName = dp.get().getOrganizationName();
            }
        } else if (user.getRole() == Role.ROLE_RECEIVER) {
            var rp = recipientProfileRepository.findByUser(user);
            if (rp.isPresent()) {
                profileId = rp.get().getId();
                orgName = rp.get().getOrganizationName();
            }
        }

        String token = tokenProvider.generateToken(user.getEmail(), user.getRole().name(), user.getId());
        return new AuthResponse(token, user.getId(), user.getEmail(), user.getRole().name(), user.getFullName(), profileId, orgName);
    }
}

