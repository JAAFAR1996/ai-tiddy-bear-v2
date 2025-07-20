## فحص مفاتيح API المكشوفة
```bash
grep -rn --include='*.py' --exclude-dir=.venv --exclude-dir=venv --exclude-dir=__pycache__ --exclude-dir=build --exclude-dir=dist --exclude-dir=.mypy_cache --exclude-dir=node_modules --exclude-dir=.git -E 'api_key|API_KEY|secret_key' src
```

```
src/application/services/ai/main_service.py:35:    def __init__(self, openai_api_key: str, redis_cache=None, settings=None) -> None:
src/application/services/ai/main_service.py:36:        if not openai_api_key:
src/application/services/ai/main_service.py:38:        self.client = AsyncOpenAI(api_key=openai_api_key)
src/application/services/ai/modules/response_generator.py:36:    def __init__(self, api_key: str | None = None, model: str = "gpt-4") -> None:
src/application/services/ai/modules/response_generator.py:43:        if OPENAI_AVAILABLE and api_key:
src/application/services/ai/modules/response_generator.py:45:                self.client = AsyncOpenAI(api_key=api_key)
src/common/constants.py:96:    "api_key",
src/infrastructure/ai/chatgpt/client.py:37:    def __init__(self, api_key: str = None) -> None:
src/infrastructure/ai/chatgpt/client.py:38:        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
src/infrastructure/ai/chatgpt/client.py:39:        if not self.api_key:
src/infrastructure/ai/chatgpt/client.py:42:                "Set OPENAI_API_KEY environment variable or pass api_key parameter."
src/infrastructure/ai/chatgpt/client.py:45:        self.client = OpenAI(api_key=self.api_key)
src/infrastructure/ai/real_ai_service.py:39:        openai_api_key = self.settings.ai.OPENAI_API_KEY
src/infrastructure/ai/real_ai_service.py:40:        if not openai_api_key:
src/infrastructure/ai/real_ai_service.py:42:        self.client = AsyncOpenAI(api_key=openai_api_key)
src/infrastructure/config/ai_settings.py:8:    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
src/infrastructure/config/ai_settings.py:13:    ELEVENLABS_API_KEY: str | None = Field(None, env="ELEVENLABS_API_KEY")
src/infrastructure/config/env_security.py:32:    OPENAI_API_KEY = "OPENAI_API_KEY"
src/infrastructure/config/infrastructure_settings.py:57:    datadog_api_key: str | None = None
src/infrastructure/config/infrastructure_settings.py:68:    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
src/infrastructure/config/production_check.py:21:        "OPENAI_API_KEY",
src/infrastructure/config/production_settings.py:116:                "OPENAI_API_KEY",
src/infrastructure/config/secure_settings.py:78:def generate_new_secret_key() -> str:
src/infrastructure/config/secure_settings.py:92:    new_secret = generate_new_secret_key()
src/infrastructure/config/settings.py:107:            if not self.ai.OPENAI_API_KEY or not self.ai.OPENAI_API_KEY.startswith(
src/infrastructure/config/settings.py:111:                    "OPENAI_API_KEY must be a valid OpenAI API key in production.",
src/infrastructure/config/startup_validator.py:74:        if not self.settings.ai.OPENAI_API_KEY:
src/infrastructure/config/startup_validator.py:75:            self._add_error("❌ OPENAI_API_KEY is required but not set")
src/infrastructure/config/startup_validator.py:76:        elif not self.settings.ai.OPENAI_API_KEY.startswith("sk-"):
src/infrastructure/config/startup_validator.py:78:                "❌ OPENAI_API_KEY must be a valid OpenAI API key (starts with 'sk-')",
src/infrastructure/config/startup_validator.py:81:            logger.debug("✅ OPENAI_API_KEY configured")
src/infrastructure/config/startup_validator.py:104:        secret_key = self.settings.security.SECRET_KEY
src/infrastructure/config/startup_validator.py:116:            if dangerous.lower() in secret_key.lower():
src/infrastructure/config/validators.py:13:    def validate_secret_key(cls, v: str) -> str:
src/infrastructure/config/voice_settings.py:8:    VOICE_API_KEY: str | None = Field(None, env="VOICE_API_KEY")
src/infrastructure/di/di_components/service_factory.py:40:            if not hasattr(settings, "OPENAI_API_KEY") or not settings.OPENAI_API_KEY:
src/infrastructure/di/di_components/service_factory.py:41:                raise ValueError("OPENAI_API_KEY is required")
src/infrastructure/di/di_components/service_factory.py:42:            return OpenAIClient(api_key=settings.OPENAI_API_KEY)
src/infrastructure/di/di_components/service_factory.py:48:            logger.critical(f"CRITICAL ERROR: Missing OPENAI_API_KEY in settings: {e}")
src/infrastructure/di/di_components/service_factory.py:49:            raise ValueError("OPENAI_API_KEY configuration required") from e
src/infrastructure/di/di_components/service_factory.py:62:                not hasattr(settings, "ELEVENLABS_API_KEY")
src/infrastructure/di/di_components/service_factory.py:63:                or not settings.ELEVENLABS_API_KEY
src/infrastructure/di/di_components/service_factory.py:65:                raise ValueError("ELEVENLABS_API_KEY is required")
src/infrastructure/di/di_components/service_factory.py:66:            return ElevenLabsClient(api_key=settings.ELEVENLABS_API_KEY)
src/infrastructure/di/di_components/service_factory.py:75:                f"CRITICAL ERROR: Missing ELEVENLABS_API_KEY in settings: {e}",
src/infrastructure/di/di_components/service_factory.py:77:            raise ValueError("ELEVENLABS_API_KEY configuration required") from e
src/infrastructure/external_apis/azure_speech_client.py:5:    def __init__(self, api_key: str, region: str) -> None:
src/infrastructure/external_apis/azure_speech_client.py:6:        self.api_key = api_key
src/infrastructure/external_apis/azure_speech_client.py:13:            "Ocp-Apim-Subscription-Key": self.api_key,
src/infrastructure/external_apis/azure_speech_client.py:39:            "Ocp-Apim-Subscription-Key": self.api_key,
src/infrastructure/external_apis/chatgpt_client.py:28:    def __init__(self, api_key: str = None) -> None:
src/infrastructure/external_apis/chatgpt_client.py:30:        self.api_key = api_key or self.settings.OPENAI_API_KEY
src/infrastructure/external_apis/chatgpt_client.py:31:        if not self.api_key:
src/infrastructure/external_apis/chatgpt_client.py:33:        self.client = AsyncOpenAI(api_key=self.api_key)
src/infrastructure/external_apis/chatgpt_client.py:187:    # This requires OPENAI_API_KEY to be set in the environment or a .env file
src/infrastructure/external_apis/chatgpt_client.py:220:    # OPENAI_API_KEY="your_key_here"
src/infrastructure/external_apis/elevenlabs_client.py:6:    def __init__(self, api_key: SecretStr) -> None:
src/infrastructure/external_apis/elevenlabs_client.py:7:        self.api_key = api_key.get_secret_value()
src/infrastructure/external_apis/elevenlabs_client.py:11:            "xi-api-key": self.api_key,
src/infrastructure/external_apis/openai_client.py:21:    def __init__(self, api_key: str) -> None:
src/infrastructure/external_apis/openai_client.py:22:        self.client = AsyncOpenAI(api_key=api_key)
src/infrastructure/health/checks.py:97:                headers={"Authorization": f"Bearer {settings.ai.OPENAI_API_KEY}"},
src/infrastructure/security/environment_validator.py:45:        "OPENAI_API_KEY": {
src/infrastructure/security/environment_validator.py:48:            "no_defaults": ["REQUIRED", "your_api_key"],
src/infrastructure/security/environment_validator.py:63:        "PARENT_VERIFICATION_API_KEY": {
src/infrastructure/security/environment_validator.py:211:                    elif var_name == "OPENAI_API_KEY":
src/infrastructure/security/hardening/csrf_protection.py:22:    secret_key: str
src/infrastructure/security/hardening/csrf_protection.py:43:        if not config.secret_key or len(config.secret_key) < 32:
src/infrastructure/security/hardening/csrf_protection.py:61:                self.config.secret_key.encode(),
src/infrastructure/security/hardening/csrf_protection.py:322:            secret_key=secrets.token_urlsafe(32),
src/infrastructure/security/hardening/csrf_protection.py:332:def init_csrf_protection(secret_key: str, **kwargs) -> CSRFProtection:
src/infrastructure/security/hardening/csrf_protection.py:335:    config = CSRFConfig(secret_key=secret_key, **kwargs)
src/infrastructure/security/hardening/secure_settings.py:35:    secret_key: SecretStr = Field(
src/infrastructure/security/hardening/secure_settings.py:63:    openai_api_key: SecretStr = Field(..., description="OpenAI API key")
src/infrastructure/security/hardening/secure_settings.py:64:    anthropic_api_key: SecretStr | None = Field(
src/infrastructure/security/hardening/security_tests/encryption_tests.py:88:            (r'api_key\s*=\s*".*"', "Hardcoded API key"),
src/infrastructure/security/hardening/security_tests/encryption_tests.py:89:            (r'secret_key\s*=\s*".*"', "Hardcoded secret key"),
src/infrastructure/security/logging_security_monitor.py:32:            "api_key": r"\b[A-Za-z0-9]{32,}\b",
src/infrastructure/security/log_sanitization_config.py:25:            r"api_key",
src/infrastructure/security/log_sanitization_config.py:44:            "secret_key",
src/infrastructure/security/log_sanitization_config.py:45:            "api_key",
src/infrastructure/security/log_sanitization_config.py:65:            r"api_key",
src/infrastructure/security/log_sanitization_config.py:85:            "secret_key",
src/infrastructure/security/log_sanitization_config.py:86:            "api_key",
src/infrastructure/security/main_security_service.py:146:        secret_key = self.settings.security.SECRET_KEY
src/infrastructure/security/main_security_service.py:150:            if dangerous.lower() in secret_key.lower():
src/infrastructure/security/secure_logger.py:201:            r"api_key[=:\s]+\S+": lambda m: "api_key=[REDACTED]",
src/infrastructure/security/secure_logger.py:347:            r"password", r"secret", r"token", r"api_key", r"private_key",
src/infrastructure/security/secure_logger.py:355:            "password", "secret_key", "api_key", "private_key", "token",
src/infrastructure/security/security_manager.py:73:    def generate_file_signature(file_content: bytes, secret_key: str) -> str:
src/infrastructure/security/security_manager.py:78:            secret_key: A secret key to use for generating the signature.
src/infrastructure/security/security_manager.py:85:            secret_key.encode("utf-8"),
src/infrastructure/security/token_service.py:18:        self.secret_key = self.settings.security.SECRET_KEY
src/infrastructure/security/token_service.py:27:        if not self.secret_key or len(self.secret_key) < 32:
src/infrastructure/security/token_service.py:43:                to_encode, self.secret_key, algorithm=self.algorithm
src/infrastructure/security/token_service.py:64:                to_encode, self.secret_key, algorithm=self.algorithm
src/infrastructure/security/token_service.py:77:                token, self.secret_key, algorithms=[self.algorithm]
src/presentation/api/middleware/request_logging.py:46:            "api_key",

```

**ملخص النتائج:** تم العثور على 98 نتيجة

⏱️ الوقت المستغرق: 2.19 ثانية

⏱️ الوقت المستغرق: 2.19 ثانية


---

