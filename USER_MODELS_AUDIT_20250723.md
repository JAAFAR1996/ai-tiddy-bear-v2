# USER_MODELS_AUDIT_20250723.md

**Timestamp:** 2025-07-23
**Analyst:** GitHub Copilot

---

## Classification Table

| Class Name         | File Path                                                        | Type         | Used By (Imports)                                                                 | Risk if Deleted | Migration Required |
|--------------------|------------------------------------------------------------------|--------------|-----------------------------------------------------------------------------------|-----------------|-------------------|
| User               | src/infrastructure/security/auth/jwt_auth.py                     | SQLAlchemy   | persistence/models/__init__.py, persistence/repositories/user_repository.py        | HIGH            | Yes (update imports, verify ORM usage) |
| UserModel          | src/infrastructure/persistence/models/user_model.py              | SQLAlchemy   | security/auth/real_auth_service.py                                                | HIGH            | Yes (update imports, verify ORM usage) |
| User               | src/domain/models/user.py                                        | Pydantic     | presentation/api/esp32_endpoints.py, security/core/real_auth_service.py           | MEDIUM          | Yes (update API validation) |
| User               | src/domain/entities/user.py                                      | Python class | presentation/api/endpoints/*, interfaces/repository_interfaces.py, di/fastapi_dependencies.py | MEDIUM          | Yes (update business logic references) |

---

## Import Locations

- `jwt_auth.User` (aliased as UserModel):
  - src/infrastructure/persistence/models/__init__.py (line 3)
  - src/infrastructure/persistence/repositories/user_repository.py (line 16)
- `user_model.UserModel`:
  - src/infrastructure/security/auth/real_auth_service.py (line 14)
- `domain/models/user.User`:
  - src/presentation/api/esp32_endpoints.py (line 17)
  - src/infrastructure/security/core/real_auth_service.py (line 10)
- `domain/entities/user.User`:
  - src/presentation/api/endpoints/dashboard.py (line 5)
  - src/presentation/api/endpoints/coppa_notices.py (line 9)
  - src/presentation/api/endpoints/children/route_handlers.py (line 12)
  - src/presentation/api/endpoints/children/routes.py (line 9)
  - src/presentation/api/endpoints/children/get_children.py (line 11)
  - src/presentation/api/endpoints/children/create_child.py (line 11)
  - src/domain/interfaces/repository_interfaces.py (line 10)
  - src/infrastructure/di/fastapi_dependencies.py (line 16)

---

## Deletion Impact Analysis

### Class: User (jwt_auth.py)
- Imported by: 
  - src/infrastructure/persistence/models/__init__.py (line 3)
  - src/infrastructure/persistence/repositories/user_repository.py (line 16)
- Required changes:
  - Update imports to use UserModel from user_model.py
  - Verify method compatibility and ORM usage
- Risk: HIGH - Core authentication and persistence affected

---

## Pre-deletion Checklist
- [x] Audit report saved to USER_MODELS_AUDIT_20250723.md
- [x] All imports documented
- [ ] Archive created with copies (pending)
- [x] Vulture/analysis results reviewed
- [ ] Team notification sent (if applicable)
- [ ] Rollback plan documented

---

**Execution ready?**
Awaiting approval. No deletions performed until explicit approval of the audit report.

---

## Notes
- User class in jwt_auth.py will be deleted and imports updated to use UserModel from user_model.py.
- Domain layer User classes are retained for API and business logic separation.
- System will be verified for startup errors after changes.
