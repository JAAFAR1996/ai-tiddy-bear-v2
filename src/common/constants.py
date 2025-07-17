"""Production Constants for AI Teddy Bear
All magic numbers and constant values in one place for easy maintenance.
"""

from enum import Enum

# Child Safety Constants
MAX_CHILD_AGE = 13
MIN_CHILD_AGE = 3
DEFAULT_SAFETY_SCORE = 0.95
MIN_SAFETY_THRESHOLD = 0.7

# Database Connection Constants
DEFAULT_DB_POOL_SIZE = 20
DEFAULT_DB_MAX_OVERFLOW = 0
DEFAULT_DB_POOL_RECYCLE = 300
DEFAULT_CONNECTION_TIMEOUT = 30

# Rate Limiting Constants
DEFAULT_REQUESTS_PER_MINUTE = 60
DEFAULT_REQUESTS_PER_HOUR = 600
DEFAULT_REQUESTS_PER_DAY = 5000
DEFAULT_BURST_LIMIT = 10
DEFAULT_BLOCK_DURATION_MINUTES = 60

# AI Response Constants
MAX_AI_RESPONSE_TOKENS = 200
MAX_STORY_TOKENS = 500
DEFAULT_AI_TIMEOUT = 30.0
MAX_CONVERSATION_HISTORY = 10

# Session Management Constants
DEFAULT_SESSION_TIMEOUT = 1800
MAX_CONCURRENT_SESSIONS = 100
SESSION_CLEANUP_INTERVAL = 300

# File Upload Constants
MAX_FILE_SIZE_MB = 5
MAX_AUDIO_DURATION_SECONDS = 60
ALLOWED_AUDIO_FORMATS = ["wav", "mp3", "m4a"]
ALLOWED_IMAGE_FORMATS = ["jpg", "jpeg", "png"]

# COPPA Compliance Constants
DATA_RETENTION_DAYS = 90
PARENTAL_CONSENT_VALIDITY_DAYS = 365
AUDIT_LOG_RETENTION_DAYS = 2555
MIN_PARENT_AGE = 18

# Performance Monitoring Constants
METRICS_COLLECTION_INTERVAL = 30
PERFORMANCE_ALERT_THRESHOLD = 80
MAX_MEMORY_USAGE_MB = 1000
MAX_CPU_USAGE_PERCENT = 80

# Cache Configuration Constants
DEFAULT_CACHE_TTL = 3600
FREQUENT_DATA_CACHE_TTL = 300
REDIS_MAX_CONNECTIONS = 100
CACHE_KEY_PREFIX = "ai_teddy"

# Security Constants
JWT_EXPIRATION_HOURS = 24
REFRESH_TOKEN_DAYS = 7
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_ATTEMPTS = 5
ACCOUNT_LOCKOUT_MINUTES = 60

# API Response Constants
MAX_RESPONSE_SIZE_KB = 100
API_VERSION = "v1"
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Content Filtering Constants
PROFANITY_FILTER_STRICTNESS = "high"
CONTENT_MODERATION_THRESHOLD = 0.9
VIOLENCE_DETECTION_THRESHOLD = 0.8
INAPPROPRIATE_CONTENT_THRESHOLD = 0.9

# Logging Constants
LOG_ROTATION_SIZE_MB = 100
LOG_RETENTION_DAYS = 30
LOG_LEVEL_PRODUCTION = "WARNING"
LOG_LEVEL_DEVELOPMENT = "DEBUG"
SENSITIVE_LOG_INTERACTION_KEYS = [
    "full_message_content",
    "raw_audio_data",
]  # Define keys to be excluded from child interaction logs.

# Error Handling Constants
MAX_ERROR_MESSAGE_LENGTH = 500
ERROR_RETRY_ATTEMPTS = 3
ERROR_RETRY_DELAY_SECONDS = 1
CIRCUIT_BREAKER_FAILURE_THRESHOLD = 5

# Event Store Constants
class EventStoreType(Enum):
    KAFKA = "kafka"
    POSTGRES = "postgres"


# Health Check Constants
HEALTH_CHECK_TIMEOUT = 10
DEPENDENCY_CHECK_TIMEOUT = 5
HEALTH_CHECK_INTERVAL = 30

# API Routing Constants
API_PREFIX_ESP32 = "/api/esp32"
API_TAG_ESP32 = "ESP32"
API_PREFIX_DASHBOARD = "/api/dashboard"
API_TAG_DASHBOARD = "Dashboard"
API_PREFIX_HEALTH = "/api/health"
API_TAG_HEALTH = "Health"
API_PREFIX_CHATGPT = "/api"
API_TAG_CHATGPT = "ChatGPT"
API_PREFIX_AUTH = "/api"
API_TAG_AUTH = "Auth"

# Child Safety Endpoints Constants
CHILD_SPECIFIC_API_ENDPOINTS = ["/api/v1/conversation", "/api/v1/voice"]

# OpenAPI Documentation Constants
OPENAPI_TITLE = "AI Teddy Bear API"
OPENAPI_VERSION = "1.0.0"
OPENAPI_DESCRIPTION = """## AI Teddy Bear - Child-Safe AI Companion API
Production-ready API for AI Teddy Bear - A COPPA-compliant AI companion for children.
### 🌟 Key Features
- **Child-Safe AI Interactions**: Content filtering and age-appropriate responses
- **COPPA Compliance**: Full compliance with Children's Online Privacy Protection Act
- **Real-time Voice**: Voice interactions with safety monitoring
- **Parental Controls**: Comprehensive controls and monitoring
- **Educational Content**: Story generation and learning activities
### 🔒 Security Features
- JWT authentication with refresh tokens
- Rate limiting on all endpoints (60 requests/minute)
- Data encryption for all PII
- Comprehensive audit logging
- Account lockout protection
### 📊 API Standards
- RESTful design principles
- Consistent error responses with tracking IDs
- Pagination support on list endpoints
- Request/response validation
- CORS support for web clients
### 🚀 Getting Started
1. Register a parent account at `/auth/register`
2. Login to receive JWT tokens at `/auth/login`
3. Submit COPPA consent at `/coppa/consent`
4. Create child profiles at `/children`
5. Start conversations at `/conversations/chat`
### 📝 Rate Limiting
All endpoints are rate-limited to prevent abuse:
- Standard endpoints: 60 requests/minute
- Auth endpoints: 5 requests/minute
- File uploads: 10 requests/minute
### 🔍 Error Handling
All errors include:
- Unique `error_id` for tracking
- Human-readable `message`
- Optional `detail` for debugging
- HTTP status codes following standards
### 📖 Additional Resources
- [API Status Page](https://status.aiteddybear.com]
- [Developer Documentation](https://docs.aiteddybear.com]
- [Support](mailto:support@aiteddybear.com)        """
OPENAPI_SERVERS = [
    {"url": "https://api.aiteddybear.com/v1", "description": "Production"},
    {
        "url": "https://staging-api.aiteddybear.com/v1",
        "description": "Staging",
    },
    {"url": "http://localhost:8000/api/v1", "description": "Development"},
]
OPENAPI_TAGS = [
    {
        "name": "Authentication",
        "description": "User authentication and authorization endpoints",
    },
    {
        "name": "Children",
        "description": "Child profile management - Create, read, update, and delete child profiles",
    },
    {
        "name": "Conversations",
        "description": "AI chat interactions - Send messages and manage conversations",
    },
    {
        "name": "COPPA",
        "description": "COPPA compliance endpoints - Consent management and data privacy",
    },
    {
        "name": "Safety",
        "description": "Safety monitoring - Events, alerts, and parental notifications",
    },
    {
        "name": "Admin",
        "description": "Administrative endpoints - Health checks and system management",
    },
]
OPENAPI_EXTERNAL_DOCS = {
    "description": "Full API Documentation",
    "url": "https://docs.aiteddybear.com/api",
}
OPENAPI_LICENSE_INFO = {
    "name": "Proprietary",
    "url": "https://aiteddybear.com/license",
}
OPENAPI_CONTACT_INFO = {
    "name": "API Support Team",
    "url": "https://support.aiteddybear.com",
    "email": "api-support@aiteddybear.com",
}
OPENAPI_COMMON_RESPONSES = {
    "BadRequest": {
        "description": "Bad request - Invalid input data",
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "error_id": {"type": "string", "format": "uuid"},
                        "message": {"type": "string"},
                        "detail": {"type": "string"},
                        "timestamp": {"type": "string", "format": "date-time"},
                    },
                },
            },
        },
    },
    "Unauthorized": {
        "description": "Unauthorized - Invalid or missing authentication",
        "content": {
            "application/json": {
                "schema": {"$ref": "#/components/schemas/Error"}
            },
        },
    },
    "Forbidden": {
        "description": "Forbidden - Insufficient permissions",
        "content": {
            "application/json": {
                "schema": {"$ref": "#/components/schemas/Error"}
            },
        },
    },
    "NotFound": {
        "description": "Not found - Resource does not exist",
        "content": {
            "application/json": {
                "schema": {"$ref": "#/components/schemas/Error"}
            },
        },
    },
    "TooManyRequests": {
        "description": "Too many requests - Rate limit exceeded",
        "headers": {
            "X-RateLimit-Limit": {
                "description": "Request limit per minute",
                "schema": {"type": "integer"},
            },
            "X-RateLimit-Remaining": {
                "description": "Remaining requests in current window",
                "schema": {"type": "integer"},
            },
            "X-RateLimit-Reset": {
                "description": "Time when the rate limit resets (Unix timestamp)",
                "schema": {"type": "integer"},
            },
        },
        "content": {
            "application/json": {
                "schema": {"$ref": "#/components/schemas/Error"}
            },
        },
    },
}

OPENAPI_BEARER_DESCRIPTION = (
    "JWT Authorization header using the Bearer scheme. "
    "Example: 'Authorization: Bearer <token>'"
)