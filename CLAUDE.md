# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **AI Teddy Bear** backend - an enterprise-grade, child-safe AI interaction platform built with Hexagonal Architecture. The system prioritizes child safety (COPPA compliance), secure AI responses, and parental controls.

## Core Commands

```bash
# Development mode (no external dependencies)
cd src && python3 main.py

# Production mode (requires FastAPI)
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000

# Run tests
python3 -m pytest tests/ -v --cov=src

# Code quality checks
python3 -m flake8 src/
python3 -m mypy src/
python3 -m black src/

# Core feature testing
cd src && python3 CORE_FEATURES_TEST.py
```

## Architecture (Hexagonal/Clean Architecture)

The codebase follows strict Hexagonal Architecture with 4 layers:

```
src/
├── domain/           # Business logic ONLY (no external dependencies)
├── application/      # Use cases and application services
├── infrastructure/   # External concerns (DB, APIs, security)
└── presentation/     # API endpoints and middleware
```

**Critical Import Rules:**
- Always import settings from `src.infrastructure.config.settings`
- Always import DI container from `src.infrastructure.di.container`
- Dependencies flow inward only (infrastructure → application → domain)

## Child Safety Requirements

This system handles children's data and must maintain:
- **COPPA compliance** at all times
- **Content filtering** for all AI responses
- **Parental consent** for data collection
- Data retention policy: 90 days (configurable via application settings; reference formal policy document for details).
- **Encrypted storage** for all PII

## Key Features Status

- ✅ **Child Safety Protection** (100% working)
- ✅ **AI Intelligence** (100% working) 
- ✅ **Parental Controls** (100% working)
- ✅ **Security Features** (100% working)
- API Endpoints: Core routes fully implemented and functional; advanced features undergoing performance testing.

## Development Guidelines

### Code Quality Standards
- **No files over 300 lines**
- **Type hints mandatory** on all functions
- **No `print()` statements** in production code
- **Comprehensive error handling** required
- **Security-first approach** for all implementations

### Testing Strategy
- Unit tests in `tests/unit/`
- Integration tests in `tests/integration/`
- Security tests in `tests/security/`
- E2E tests in `tests/e2e/`
- **Minimum 80% code coverage**

### Security Rules
- **Never hardcode secrets** - use environment variables
- **Implement robust API key management and rotation policies** - API keys should be regularly rotated and managed using secure secrets management solutions (e.g., AWS Secrets Manager, Azure Key Vault, HashiCorp Vault) rather than being stored directly in environment variables for long periods.
- **Always validate input** with Pydantic models
- **Rate limiting** on all API endpoints
- **JWT authentication** with refresh tokens
- **Audit logging** for all sensitive operations
- **Never use user-controlled input to construct file paths** - Always sanitize or validate file paths to prevent directory traversal vulnerabilities, especially when serving static files or handling file uploads.

## External Dependencies

**Production Stack:**
- `fastapi` - Web framework
- `pydantic` - Data validation (REQUIRED, no fallbacks)
- `sqlalchemy` - Database ORM
- `redis` - Caching and sessions
- `openai` - AI services
- `bcrypt` - Password hashing

**Development Tools:**
- `pytest` - Testing framework
- `black` - Code formatting
- `mypy` - Type checking
- `flake8` - Linting

## File Structure Highlights

```
src/
├── domain/
│   ├── entities/child.py              # Core child entity
│   ├── value_objects/safety_level.py  # Safety enums
│   └── services/safety_validator.py   # Safety business logic
├── application/
│   ├── use_cases/generate_ai_response.py  # Main AI use case
│   └── services/consent_service.py       # COPPA compliance
├── infrastructure/
│   ├── ai/production_ai_service.py       # Real OpenAI integration
│   ├── security/comprehensive_security_service.py  # Security
│   └── config/settings.py               # Environment configuration
└── presentation/
    └── api/                             # FastAPI routes
```

## Common Issues and Solutions

### Missing Dependencies
If you see import errors for `
### Database Issues
- For connection issues, verify `DATABASE_URL` environment variable is correctly set and network access to PostgreSQL is permitted.
- Consult internal runbook for advanced database troubleshooting steps or common error scenarios.