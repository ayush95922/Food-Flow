"""Application-level exceptions mapped to HTTP status codes in main.py."""


class AIServiceError(Exception):
    status_code = 500
    code = "INTERNAL_ERROR"

    def __init__(self, message: str, code: str = None, details=None):
        super().__init__(message)
        self.message = message
        if code:
            self.code = code
        self.details = details


class ValidationFailed(AIServiceError):
    status_code = 422
    code = "VALIDATION_ERROR"


class ModelNotAvailable(AIServiceError):
    status_code = 503
    code = "MODEL_NOT_AVAILABLE"


class InsufficientData(AIServiceError):
    status_code = 422
    code = "INSUFFICIENT_DATA"
