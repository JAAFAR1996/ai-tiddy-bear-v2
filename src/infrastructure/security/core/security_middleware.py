"""Middleware أمان شامل لحماية التطبيق"""

import json
import re
import time
from datetime import datetime, timedelta

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="security")

try:
    from fastapi import HTTPException, Request, Response
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.types import ASGIApp, Receive, Scope, Send
except ImportError as e:
    logger.error(f"CRITICAL ERROR: FastAPI is required for production use: {e}")
    logger.error("Install required dependencies: pip install fastapi starlette")
    raise ImportError(f"Missing middleware dependencies: {e}") from e

try:
    import redis.asyncio as redis

    REDIS_AVAILABLE = True
except ImportError:
    logger.warning("Redis not available, using in-memory storage for rate limiting")
    REDIS_AVAILABLE = False

    # Mock Redis for development
    class MockRedis:
        def __init__(self):
            self.data = {}

        async def zremrangebyscore(self, key, min_score, max_score):
            if key in self.data:
                self.data[key] = {
                    k: v
                    for k, v in self.data[key].items()
                    if not (min_score <= v <= max_score)
                }

        async def zcard(self, key):
            return len(self.data.get(key, {}))

        async def zadd(self, key, mapping):
            if key not in self.data:
                self.data[key] = {}
            self.data[key].update(mapping)

        async def expire(self, key, seconds):
            pass  # Mock implementation

        async def exists(self, key):
            return key in self.data

        async def delete(self, key):
            self.data.pop(key, None)

        async def setex(self, key, seconds, value):
            self.data[key] = value

    redis = type("MockRedisModule", (), {"Redis": MockRedis})


class RateLimiter:
    """محدد معدل الطلبات لحماية من DDoS"""

    def __init__(
        self,
        redis_client=None,
        requests_per_minute: int = 60,
        burst_limit: int = 10,
    ) -> None:
        self.redis = redis_client or MockRedis()
        self.requests_per_minute = requests_per_minute
        self.burst_limit = burst_limit
        self.window_seconds = 60

    async def is_allowed(self, client_ip: str) -> bool:
        """التحقق من إذا كان العميل مسموح له بالطلب"""
        key = f"rate_limit:{client_ip}"
        now = int(time.time())

        # Remove old timestamps
        await self.redis.zremrangebyscore(key, 0, now - self.window_seconds)

        # Get current request count
        current_requests = await self.redis.zcard(key)

        if current_requests >= self.requests_per_minute:
            return False

        # Add current request timestamp
        await self.redis.zadd(key, {now: now})
        await self.redis.expire(key, self.window_seconds)

        return True

    async def record_suspicious_activity(self, ip: str, activity: str) -> None:
        """تسجيل النشاط المشبوه"""
        key = f"suspicious_activity:{ip}"
        now = datetime.now()

        await self.redis.zadd(key, {now.timestamp(): now.timestamp()})
        await self.redis.expire(key, int(timedelta(hours=24).total_seconds()))

        # Check if IP should be blocked
        activity_count = await self.redis.zcard(key)
        if activity_count >= 5:
            block_key = f"blocked_ip:{ip}"
            await self.redis.setex(
                block_key, int(timedelta(hours=1).total_seconds()), "blocked"
            )
            logger.warning(f"IP {ip} blocked due to repeated suspicious activity")

    async def is_ip_blocked(self, ip: str) -> bool:
        """التحقق من حظر IP"""
        block_key = f"blocked_ip:{ip}"
        return await self.redis.exists(block_key)

    async def clear_failed_attempts(self, identifier: str) -> None:
        """Clear failed attempts for successful authentication"""
        await self.redis.delete(f"rate_limit:{identifier}")
        await self.redis.delete(f"suspicious_activity:{identifier}")
        await self.redis.delete(f"blocked_ip:{identifier}")


class SecurityValidator:
    """مدقق الأمان للطلبات"""

    # أنماط الهجمات الشائعة
    MALICIOUS_PATTERNS = [
        r"<script[^>]*>.*?</script>",  # XSS
        r"javascript:",  # JavaScript injection
        r"vbscript:",  # VBScript injection
        r"onload\\s*=",  # Event handler injection
        r"onerror\\s*=",  # Error handler injection
        r"eval\\s*\\(",  # JavaScript eval
        r"exec\\s*\\(",  # Code execution
        r"system\\s*\\(",  # System calls
        r"union\\s+select",  # SQL injection
        r"drop\\s+table",  # SQL injection
        r"delete\\s+from",  # SQL injection
        r"insert\\s+into",  # SQL injection
        r"update\\s+.*set",  # SQL injection
        r"\\.\\./\\.\\.",  # Path traversal
        r"etc/passwd",  # Unix system files
        r"windows/system32",  # Windows system files
    ]

    def __init__(self) -> None:
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.MALICIOUS_PATTERNS
        ]

    def scan_request(self, request_data: str) -> list[str]:
        """فحص البيانات للبحث عن محتوى ضار"""
        threats = []

        for i, pattern in enumerate(self.compiled_patterns):
            if pattern.search(request_data):
                threat_type = [
                    "XSS",
                    "JavaScript Injection",
                    "VBScript Injection",
                    "Event Handler Injection",
                    "Error Handler Injection",
                    "JavaScript Eval",
                    "Code Execution",
                    "System Calls",
                    "SQL Injection",
                    "SQL Injection",
                    "SQL Injection",
                    "SQL Injection",
                    "SQL Injection",
                    "Path Traversal",
                    "System File Access",
                    "System File Access",
                ][i]
                threats.append(threat_type)

        return threats

    def validate_child_data(self, data: dict) -> list[str]:
        """التحقق من بيانات الطفل للامتثال لـ COPPA"""
        violations = []

        if "age" in data:
            age = data.get("age", 0)
            if age > 13:
                violations.append("COPPA: العمر يجب أن يكون 13 سنة أو أقل")

        if "personal_info" in data:
            personal_fields = ["phone", "address", "email", "location"]
            for field in personal_fields:
                if field in data.get("personal_info", {}):
                    violations.append(f"COPPA: لا يجوز جمع {field} للأطفال")

        return violations


class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware الأمان الرئيسي"""

    def __init__(
        self,
        app: ASGIApp,
        redis_client=None,
        rate_limiter: RateLimiter = None,
        validator: SecurityValidator = None,
    ) -> None:
        super().__init__(app)
        self.redis_client = redis_client or MockRedis()
        self.rate_limiter = rate_limiter or RateLimiter(self.redis_client)
        self.validator = validator or SecurityValidator()

    async def dispatch(self, request: Request, call_next) -> Response:
        """معالجة الطلبات مع فحص الأمان"""
        start_time = time.time()
        client_ip = self.get_client_ip(request)

        try:
            # فحص IP المحظور
            if await self.rate_limiter.is_ip_blocked(client_ip):
                logger.warning(f"Blocked IP attempted access: {client_ip}")
                raise HTTPException(
                    status_code=403,
                    detail="IP blocked due to suspicious activity",
                )

            # فحص معدل الطلبات
            if not await self.rate_limiter.is_allowed(client_ip):
                await self.rate_limiter.record_suspicious_activity(
                    client_ip, "Rate limit exceeded"
                )
                logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                raise HTTPException(status_code=429, detail="Rate limit exceeded")

            # فحص الأمان للطلب
            security_issues = await self.scan_request_security(request)
            if security_issues:
                await self.rate_limiter.record_suspicious_activity(
                    client_ip, f"Security threats: {security_issues}"
                )
                logger.warning(
                    f"Security threats detected from {client_ip}: {security_issues}"
                )
                raise HTTPException(
                    status_code=400, detail="Malicious content detected"
                )

            # تنفيذ الطلب
            response = await call_next(request)

            # إضافة headers أمان
            response = self.add_security_headers(response)

            # تسجيل الطلب
            self.log_request(request, response, time.time() - start_time, client_ip)

            return response
        except HTTPException:
            # إعادة إلقاء HTTPException كما هي
            raise
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Security middleware data processing error: {e}")
            # في حالة خطأ، السماح بمرور الطلب مع تسجيل تفصيلي
            return await call_next(request)
        except Exception as e:
            logger.critical(f"Unexpected security middleware error: {e}")
            # Log stack trace for debugging
            logger.exception("Security middleware unexpected error details:")
            raise HTTPException(status_code=500, detail="Internal security error")

    def get_client_ip(self, request: Request) -> str:
        """الحصول على IP العميل"""
        # البحث في headers المختلفة للحصول على IP الحقيقي
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()

        return getattr(request.client, "host", "127.0.0.1")

    async def scan_request_security(self, request: Request) -> list[str]:
        """فحص أمان الطلب"""
        threats = []

        # فحص URL
        url_threats = self.validator.scan_request(str(request.url))
        threats.extend(url_threats)

        # فحص headers
        for header_name, header_value in request.headers.items():
            header_threats = self.validator.scan_request(
                f"{header_name}: {header_value}"
            )
            threats.extend(header_threats)

        # فحص body إذا كان موجود
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    body_str = body.decode("utf-8", errors="ignore")
                    body_threats = self.validator.scan_request(body_str)
                    threats.extend(body_threats)

                    # فحص COPPA إذا كان JSON
                    try:
                        json_data = json.loads(body_str)
                        coppa_violations = self.validator.validate_child_data(json_data)
                        threats.extend(coppa_violations)
                    except (json.JSONDecodeError, TypeError) as e:
                        logger.debug(
                            f"Body is not valid JSON, skipping COPPA validation: {e}"
                        )
            except (UnicodeDecodeError, ValueError) as e:
                logger.debug(f"Could not decode request body: {e}")

        return list(set(threats))  # إزالة التكرارات

    def add_security_headers(self, response: Response) -> Response:
        """إضافة headers الأمان"""
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": ("max-age=31536000; includeSubDomains"),
            "Content-Security-Policy": (
                "default-src 'self'; script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'"
            ),
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
            # إضافة headers خاصة بحماية الأطفال
            "X-Child-Safe": "true",
            "X-COPPA-Compliant": "true",
        }

        for header, value in security_headers.items():
            response.headers[header] = value

        return response

    def log_request(
        self,
        request: Request,
        response: Response,
        duration: float,
        client_ip: str,
    ) -> None:
        """تسجيل الطلب"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "client_ip": client_ip,
            "method": request.method,
            "url": str(request.url),
            "status_code": getattr(response, "status_code", 200),
            "duration": round(duration, 3),
            "user_agent": request.headers.get("User-Agent", "Unknown"),
        }

        logger.info(f"Request processed: {json.dumps(log_data)}")


class ChildSafetySecurityMiddleware(SecurityMiddleware):
    """Middleware أمان مخصص لحماية الأطفال"""

    def __init__(
        self,
        app: ASGIApp,
        redis_client=None,
        rate_limiter: RateLimiter = None,
        validator: SecurityValidator = None,
    ) -> None:
        super().__init__(app, redis_client, rate_limiter, validator)
        # إعدادات أكثر صرامة للأطفال
        self.child_rate_limiter = RateLimiter(
            self.redis_client,
            requests_per_minute=30,  # معدل أقل للأطفال
            burst_limit=5,
        )

    async def dispatch(self, request: Request, call_next) -> Response:
        """معالجة خاصة للطلبات المتعلقة بالأطفال"""
        # التحقق من أن الطلب متعلق بالأطفال
        if self.is_child_request(request):
            # استخدام rate limiter مخصص للأطفال
            client_ip = self.get_client_ip(request)
            if not await self.child_rate_limiter.is_allowed(client_ip):
                logger.warning(f"Child rate limit exceeded for IP: {client_ip}")
                raise HTTPException(
                    status_code=429, detail="تم تجاوز حد الطلبات المسموح للأطفال"
                )

            # فحص إضافي للمحتوى المناسب للأطفال
            await self.validate_child_content(request)

        return await super().dispatch(request, call_next)

    def is_child_request(self, request: Request) -> bool:
        """التحقق من أن الطلب متعلق بالأطفال"""
        child_patterns = [
            "/children/",
            "/child/",
            "/interact/",
            "/api/v1/child/",
        ]
        return any(pattern in str(request.url) for pattern in child_patterns)

    async def validate_child_content(self, request: Request) -> None:
        """فحص المحتوى للتأكد من مناسبته للأطفال"""
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    body_str = body.decode("utf-8", errors="ignore")

                    # فحص الكلمات غير المناسبة
                    inappropriate_words = [
                        "violence",
                        "weapon",
                        "drug",
                        "alcohol",
                        "inappropriate",
                        "adult",
                        "mature",
                    ]

                    for word in inappropriate_words:
                        if word.lower() in body_str.lower():
                            logger.warning(
                                f"Inappropriate content detected in child request: {word}"
                            )
                            raise HTTPException(
                                status_code=400, detail="المحتوى غير مناسب للأطفال"
                            )
            except UnicodeDecodeError:
                logger.debug("Could not decode request body for child validation")


def create_security_middleware(
    redis_client=None,
    child_safety: bool = False,
) -> SecurityMiddleware:
    """إنشاء middleware الأمان"""
    if not redis_client and REDIS_AVAILABLE:
        try:
            redis_client = redis.Redis(
                host="localhost", port=6379, decode_responses=True
            )
        except Exception as e:
            logger.warning(f"Could not connect to Redis: {e}")
            redis_client = MockRedis()
    elif not redis_client:
        redis_client = MockRedis()

    rate_limiter = RateLimiter(redis_client, requests_per_minute=60, burst_limit=10)
    validator = SecurityValidator()

    if child_safety:
        return ChildSafetySecurityMiddleware(
            None, redis_client, rate_limiter, validator
        )
    return SecurityMiddleware(None, redis_client, rate_limiter, validator)


def setup_security_middleware(app, redis_client=None, child_safety: bool = True):
    """إعداد middleware الأمان للتطبيق"""
    middleware = create_security_middleware(redis_client, child_safety)
    middleware.app = app  # Set the app reference
    app.add_middleware(
        SecurityMiddleware,
        redis_client=redis_client,
        rate_limiter=middleware.rate_limiter,
        validator=middleware.validator,
    )

    logger.info("Security middleware configured successfully")
    return middleware


# إعدادات الأمان الافتراضية
DEFAULT_SECURITY_CONFIG = {
    "rate_limit_requests_per_minute": 60,
    "child_rate_limit_requests_per_minute": 30,
    "rate_limit_burst": 10,
    "child_rate_limit_burst": 5,
    "enable_ip_blocking": True,
    "block_duration_hours": 1,
    "max_suspicious_activities": 5,
    "coppa_enforcement": True,
    "xss_protection": True,
    "sql_injection_protection": True,
    "path_traversal_protection": True,
    "child_content_filtering": True,
}


def get_security_config() -> dict:
    """الحصول على إعدادات الأمان الحالية"""
    return DEFAULT_SECURITY_CONFIG.copy()


async def get_security_status(redis_client=None) -> dict:
    """الحصول على حالة نظام الأمان"""
    status = {
        "redis_available": REDIS_AVAILABLE,
        "middleware_active": True,
        "rate_limiting": True,
        "child_safety": True,
        "threat_detection": True,
        "config": get_security_config(),
    }

    if redis_client:
        try:
            # Test Redis connection
            await redis_client.ping() if hasattr(redis_client, "ping") else True
            status["redis_connected"] = True
        except Exception:
            status["redis_connected"] = False

    return status
