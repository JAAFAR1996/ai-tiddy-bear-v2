# DEPENDENCY MAPPING REPORT 🗺️

**ANALYSIS DATE:** 2025-07-23  
**SCOPE:** Authentication Service Dependencies  
**STATUS:** Complete Mapping  

## 🔍 IMPORT ANALYSIS

### RealAuthService Dependencies:
**LOCATION:** `src/infrastructure/security/auth/real_auth_service.py`

**INCOMING DEPENDENCIES (Who imports it):**
1. `src/presentation/api/auth_endpoints.py:10`
   ```python
   from src.infrastructure.security.auth.real_auth_service import RealAuthService
   ```

**OUTGOING DEPENDENCIES (What it imports):**
- `sqlalchemy` - Database ORM
- `src.infrastructure.config.settings` - Configuration
- `src.infrastructure.logging_config` - Logging
- `src.infrastructure.persistence.models.user_model` - User model
- `src.infrastructure.security.auth.token_service` - JWT handling
- `src.infrastructure.security.password_hasher` - Password hashing

### ProductionAuthService Dependencies:
**LOCATION:** `src/infrastructure/security/core/real_auth_service.py`

**INCOMING DEPENDENCIES (Who imports it - 5 files):**
1. `src/infrastructure/di/fastapi_dependencies.py:15`
2. `src/infrastructure/security/core/main_security_service.py:13`
3. `src/presentation/api/dependencies/auth.py:7`
4. `src/presentation/api/endpoints/conversations.py:19`
5. `src/presentation/api/endpoints/children/route_handlers.py:15`

**OUTGOING DEPENDENCIES (What it imports):**
- `datetime` - Time handling
- `bcrypt` - Password hashing (direct)
- `jwt` - JWT tokens (direct)
- `sqlalchemy` - Database ORM
- `src.domain.models.user` - Domain user model
- `src.infrastructure.config` - Configuration
- `src.infrastructure.logging_config` - Logging

## 🚨 CRITICAL IMPORT CONFLICTS

### **SAME MODULE, DIFFERENT PATHS:**
Both services are imported from paths containing `real_auth_service.py`:
- `/auth/real_auth_service.py` → RealAuthService
- `/core/real_auth_service.py` → ProductionAuthService

### **DEPENDENCY CONFUSION DETECTED:**
Multiple files importing `from src.infrastructure.security.auth.real_auth_service` but expecting **ProductionAuthService**:

**⚠️ BROKEN IMPORTS:**
- `src/infrastructure/di/fastapi_dependencies.py:15` - Imports ProductionAuthService from `/auth/` path (WRONG!)
- `src/infrastructure/security/core/main_security_service.py:13` - Same issue
- `src/presentation/api/dependencies/auth.py:7` - Same issue
- `src/presentation/api/endpoints/conversations.py:19` - Same issue
- `src/presentation/api/endpoints/children/route_handlers.py:15` - Same issue

## 🔧 SHARED DEPENDENCY ANALYSIS

### **OTHER AUTH-RELATED IMPORTS:**
Files also importing other functions from the same module:

**From auth module (`__init__.py` exports):**
- `src/infrastructure/security/__init__.py:16` - get_current_user, get_current_parent
- `src/infrastructure/security/auth/__init__.py:3` - get_current_user, get_current_parent
- `src/presentation/api/parental_dashboard.py:19` - UserInfo, get_current_parent
- `src/presentation/api/endpoints/audio.py:8` - UserInfo, get_current_user
- `src/presentation/api/endpoints/auth.py:13` - Multiple imports
- `src/presentation/api/esp32_endpoints.py:32` - Multiple imports
- `src/presentation/api/endpoints/dashboard.py:57` - Multiple imports

## 📊 RISK ASSESSMENT

### **HIGH RISK - IMPORT CONFUSION:**
- 5 files importing ProductionAuthService from WRONG PATH
- They expect `/auth/real_auth_service.py` but that contains RealAuthService
- **THESE IMPORTS ARE CURRENTLY BROKEN!**

### **CRITICAL DISCOVERY:**
The import path confusion means:
1. **ProductionAuthService is in `/core/`** (306 lines)
2. **But 5 files import it from `/auth/`** (where RealAuthService lives)
3. **This means those 5 files might be broken!**

## 🎯 RESOLUTION STRATEGY

### **OPTION 1: Fix Import Paths**
Update 5 files to import from correct path:
```python
# Change from:
from src.infrastructure.security.auth.real_auth_service import ProductionAuthService

# Change to:
from src.infrastructure.security.core.real_auth_service import ProductionAuthService
```

### **OPTION 2: Move ProductionAuthService** 
Move ProductionAuthService to `/auth/` and remove RealAuthService

### **OPTION 3: Rename and Consolidate**
Merge both services into single comprehensive service

## ✅ RECOMMENDED ACTION

**IMMEDIATE:** Check if those 5 files are actually working or broken due to import confusion.

**PHASE 3:** Fix import paths before any deletions to avoid breaking production system!
