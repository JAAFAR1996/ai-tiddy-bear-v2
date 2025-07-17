"""Domain constants for AI Teddy Bear application.
This module contains all domain-level constants to eliminate magic numbers
and improve code maintainability.
"""

# COPPA Compliance Constants
COPPA_AGE_THRESHOLD = 13  # Children under 13 require parental consent
MINIMUM_CHILD_AGE = 2  # Minimum supported child age
MAXIMUM_CHILD_AGE = 13  # Maximum child age before different handling

# Data Retention Constants
COPPA_MAX_RETENTION_DAYS = 90  # Maximum data retention for COPPA compliance
DEFAULT_RETENTION_DAYS = 30  # Default retention period
MINIMUM_RETENTION_DAYS = 1  # Minimum retention period

# Age Group Boundaries
TODDLER_MAX_AGE = 3  # 2-3 years
PRESCHOOL_MAX_AGE = 5  # 4-5 years
EARLY_CHILD_MAX_AGE = 8  # 6-8 years
MIDDLE_CHILD_MAX_AGE = 11  # 9-11 years
PRETEEN_MAX_AGE = 13  # 12-13 years

# Session and Interaction Limits
MAX_SESSION_MINUTES_TODDLER = 10  # Maximum session for 2-3 years
MAX_SESSION_MINUTES_PRESCHOOL = 15  # Maximum session for 4-5 years
MAX_SESSION_MINUTES_EARLY = 30  # Maximum session for 6-8 years
MAX_SESSION_MINUTES_MIDDLE = 45  # Maximum session for 9-11 years
MAX_SESSION_MINUTES_PRETEEN = 60  # Maximum session for 12-13 years

# Content Safety Constants
MAX_RESPONSE_LENGTH = 500  # Maximum response length for children
MAX_NEGATIVE_INDICATORS = 3  # Maximum negative words in response
MIN_CHILD_VOCABULARY_SIZE = 50  # Minimum expected vocabulary
VOCABULARY_WORDS_PER_MONTH = 10  # Expected vocabulary growth rate

# Rate Limiting Constants
RATE_LIMIT_RETRY_AFTER_SECONDS = 60  # Retry after for rate limiting
MAX_REQUESTS_PER_HOUR = 100  # Maximum requests per hour per child
MAX_REQUESTS_PER_DAY = 500  # Maximum requests per day per child

# File Size and Validation Constants
MAX_AUDIO_FILE_SIZE_MB = 10  # Maximum audio file size in MB
MAX_AUDIO_FILE_SIZE_BYTES = MAX_AUDIO_FILE_SIZE_MB * 1024 * 1024

# Database and Logging Constants
LOG_RETENTION_DAYS = 30  # Keep logs for 30 days
BACKUP_COUNT_DAYS = 90  # Keep 90 days of backups
MAX_LOG_FILE_SIZE_MB = 10  # Maximum log file size
MAX_LOG_FILE_SIZE_BYTES = MAX_LOG_FILE_SIZE_MB * 1024 * 1024

# HTTP Status and Content Rating
PG_RATING_AGE = 13  # PG-13 content rating threshold
RETRY_AFTER_SECONDS = 60  # HTTP retry after header value

# Emotion and Analytics Constants
EMOTION_ANALYSIS_WINDOW = 10  # Last N interactions to analyze
EMOTION_NEUTRAL_BASELINE = 0.5  # Neutral emotion score
SPEECH_ANALYSIS_DAYS = 30  # Days of speech data to analyze
CLARITY_THRESHOLD_LOW = 0.7  # Speech clarity threshold
REPETITION_THRESHOLD_LOW = 0.3  # Speech repetition threshold
