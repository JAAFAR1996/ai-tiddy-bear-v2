"""Production Constants for AI Teddy BearAll magic numbers and constant values in one place for easy maintenance"""  # Child Safety ConstantsMAX_CHILD_AGE = 13MIN_CHILD_AGE = 3DEFAULT_SAFETY_SCORE = 0.95MIN_SAFETY_THRESHOLD = 0.7# Database Connection ConstantsDEFAULT_DB_POOL_SIZE = 20DEFAULT_DB_MAX_OVERFLOW = 0DEFAULT_DB_POOL_RECYCLE = 300DEFAULT_CONNECTION_TIMEOUT = 30# Rate Limiting ConstantsDEFAULT_REQUESTS_PER_MINUTE = 60DEFAULT_REQUESTS_PER_HOUR = 600DEFAULT_REQUESTS_PER_DAY = 5000DEFAULT_BURST_LIMIT = 10DEFAULT_BLOCK_DURATION_MINUTES = 60# AI Response ConstantsMAX_AI_RESPONSE_TOKENS = 200MAX_STORY_TOKENS = 500DEFAULT_AI_TIMEOUT = 30.0MAX_CONVERSATION_HISTORY = 10# Session Management ConstantsDEFAULT_SESSION_TIMEOUT = 1800MAX_CONCURRENT_SESSIONS = 100SESSION_CLEANUP_INTERVAL = 300# File Upload ConstantsMAX_FILE_SIZE_MB = 5MAX_AUDIO_DURATION_SECONDS = 60ALLOWED_AUDIO_FORMATS = ["wav", "mp3", "m4a"]ALLOWED_IMAGE_FORMATS = ["jpg", "jpeg", "png"]# COPPA Compliance ConstantsDATA_RETENTION_DAYS = 90PARENTAL_CONSENT_VALIDITY_DAYS = 365AUDIT_LOG_RETENTION_DAYS = 2555MIN_PARENT_AGE = 18# Performance Monitoring ConstantsMETRICS_COLLECTION_INTERVAL = 30PERFORMANCE_ALERT_THRESHOLD = 80MAX_MEMORY_USAGE_MB = 1000MAX_CPU_USAGE_PERCENT = 80# Cache Configuration ConstantsDEFAULT_CACHE_TTL = 3600FREQUENT_DATA_CACHE_TTL = 300REDIS_MAX_CONNECTIONS = 100CACHE_KEY_PREFIX = "ai_teddy"# Security ConstantsJWT_EXPIRATION_HOURS = 24REFRESH_TOKEN_DAYS = 7PASSWORD_MIN_LENGTH = 8PASSWORD_MAX_ATTEMPTS = 5ACCOUNT_LOCKOUT_MINUTES = 60# API Response ConstantsMAX_RESPONSE_SIZE_KB = 100API_VERSION = "v1"DEFAULT_PAGE_SIZE = 20MAX_PAGE_SIZE = 100# Content Filtering ConstantsPROFANITY_FILTER_STRICTNESS = "high"CONTENT_MODERATION_THRESHOLD = 0.9VIOLENCE_DETECTION_THRESHOLD = 0.8INAPPROPRIATE_CONTENT_THRESHOLD = 0.9# Logging ConstantsLOG_ROTATION_SIZE_MB = 100LOG_RETENTION_DAYS = 30LOG_LEVEL_PRODUCTION = "WARNING"LOG_LEVEL_DEVELOPMENT = "DEBUG"SENSITIVE_LOG_INTERACTION_KEYS = ["full_message_content", "raw_audio_data"] # Define keys to be excluded from child interaction logs.
# Error Handling ConstantsMAX_ERROR_MESSAGE_LENGTH = 500ERROR_RETRY_ATTEMPTS = 3ERROR_RETRY_DELAY_SECONDS = 1CIRCUIT_BREAKER_FAILURE_THRESHOLD = 5# Event Store Constants
from enum import Enum # Import Enum for new constant

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
CHILD_SPECIFIC_API_ENDPOINTS = [
    "/api/v1/conversation", 
    "/api/v1/voice"
]

# OpenAPI Documentation Constants
OPENAPI_TITLE = "AI Teddy Bear API"
OPENAPI_VERSION = "1.0.0"
OPENAPI_DESCRIPTION = """## AI Teddy Bear - Child-Safe AI Companion API\nProduction-ready API for AI Teddy Bear - A COPPA-compliant AI companion for children.\n### 🌟 Key Features\n- **Child-Safe AI Interactions**: Content filtering and age-appropriate responses\n- **COPPA Compliance**: Full compliance with Children's Online Privacy Protection Act\n- **Real-time Voice**: Voice interactions with safety monitoring\n- **Parental Controls**: Comprehensive controls and monitoring\n- **Educational Content**: Story generation and learning activities\n### 🔒 Security Features\n- JWT authentication with refresh tokens\n- Rate limiting on all endpoints (60 requests/minute)\n- Data encryption for all PII\n- Comprehensive audit logging\n- Account lockout protection\n### 📊 API Standards\n- RESTful design principles\n- Consistent error responses with tracking IDs\n- Pagination support on list endpoints\n- Request/response validation\n- CORS support for web clients\n### 🚀 Getting Started\n1. Register a parent account at `/auth/register`\n2. Login to receive JWT tokens at `/auth/login`\n3. Submit COPPA consent at `/coppa/consent`\n4. Create child profiles at `/children`\n5. Start conversations at `/conversations/chat`\n### 📝 Rate Limiting\nAll endpoints are rate-limited to prevent abuse:\n- Standard endpoints: 60 requests/minute\n- Auth endpoints: 5 requests/minute\n- File uploads: 10 requests/minute\n### 🔍 Error Handling\nAll errors include:\n- Unique `error_id` for tracking\n- Human-readable `message`\n- Optional `detail` for debugging\n- HTTP status codes following standards\n### 📖 Additional Resources\n- [API Status Page](https://status.aiteddybear.com]\n- [Developer Documentation](https://docs.aiteddybear.com]\n- [Support](mailto:support@aiteddybear.com)        """
OPENAPI_SERVERS = [
    {"url": "https://api.aiteddybear.com/v1", "description": "Production"},
    {"url": "https://staging-api.aiteddybear.com/v1", "description": "Staging"},
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
                }
            },
        },
    },
    "Unauthorized": {
        "description": "Unauthorized - Invalid or missing authentication",
        "content": {
            "application/json": {
                "schema": {
                    "$ref": "#/components/schemas/Error"
                }
            }
        },
    },
    "Forbidden": {
        "description": "Forbidden - Insufficient permissions",
        "content": {
            "application/json": {
                "schema": {
                    "$ref": "#/components/schemas/Error"
                }
            }
        },
    },
    "NotFound": {
        "description": "Not found - Resource does not exist",
        "content": {
            "application/json": {
                "schema": {
                    "$ref": "#/components/schemas/Error"
                }
            }
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
                "schema": {
                    "$ref": "#/components/schemas/Error"
                }
            }
        },
    },
}

OPENAPI_BEARER_DESCRIPTION = (
    "JWT Authorization header using the Bearer scheme. "
    "Example: 'Authorization: Bearer <token>'"
)
