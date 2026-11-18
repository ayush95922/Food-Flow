package com.foodflow.dto.request;

import com.foodflow.model.enums.DeliveryStatus;
import jakarta.validation.constraints.NotNull;

public class UpdateDeliveryStatusRequest {
    @NotNull
    private DeliveryStatus status;

    private String notes;

    private String otp;

    public UpdateDeliveryStatusRequest() {
    }

    public DeliveryStatus getStatus() {
        return status;
    }

    public void setStatus(DeliveryStatus status) {
        this.status = status;
    }

    public String getNotes() {
        return notes;
    }

    public void setNotes(String notes) {
        this.notes = notes;
    }

    public String getOtp() {
        return otp;
    }

    public void setOtp(String otp) {
        this.otp = otp;
    }
}

