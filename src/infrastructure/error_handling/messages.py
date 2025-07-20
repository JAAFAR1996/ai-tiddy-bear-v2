ERROR_MESSAGES: dict[str, str] = {
    "VALIDATION_ERROR": "Invalid input provided. Please check your data and try again.",
    "AUTHENTICATION_ERROR": "Authentication failed. Please check your credentials.",
    "AUTHORIZATION_ERROR": "You don't have permission to access this resource.",
    "NOT_FOUND_ERROR": "The requested resource could not be found.",
    "CONFLICT_ERROR": "A conflict occurred with the existing resource. Please review and try again.",
    "EXTERNAL_SERVICE_ERROR": "A required external service is temporarily unavailable. Please try again later.",
    "RATE_LIMIT_EXCEEDED": "Too many requests. Please try again after some time.",
    "CHILD_SAFETY_VIOLATION": "Content not appropriate for children. The interaction has been flagged.",
    "DATABASE_ERROR": "A database error occurred. Please try again.",
    "DATABASE_CONNECTION_ERROR": "Failed to connect to the database. Please try again later.",
    "SYSTEM_ERROR": "An unexpected system error occurred. Please contact support.",
    "CONFIGURATION_ERROR": "A critical configuration error occurred. Please check system settings.",
    "PARENTAL_CONSENT_REQUIRED": "Parental consent is required for this action.",
    "CHILD_NOT_FOUND": "Child profile not found.",
    "CONVERSATION_LIMIT_EXCEEDED": "Daily conversation limit reached. Please try again tomorrow.",
    "FILE_UPLOAD_ERROR": "Failed to upload file. Please check the file and try again.",
    "UNSUPPORTED_FILE_TYPE": "Unsupported file type. Please upload a valid file.",
    "FILE_SIZE_EXCEEDED": "File size exceeds the maximum allowed limit.",
    "INVALID_FILENAME": "Invalid filename. Please use a safe filename.",
    "AUTHENTICATION_TOKEN_EXPIRED": "Authentication token has expired. Please log in again.",
    "AUTHENTICATION_TOKEN_INVALID": "Invalid authentication token. Please log in again.",
    "SERVICE_UNAVAILABLE": "Service is temporarily unavailable. Please try again later.",
    "UNKNOWN_ERROR": "An unknown error occurred. Please try again.",
}


def get_error_message(error_code: str) -> str:
    """Retrieves a standardized error message for a given error code."""
    return ERROR_MESSAGES.get(error_code, ERROR_MESSAGES["UNKNOWN_ERROR"])
