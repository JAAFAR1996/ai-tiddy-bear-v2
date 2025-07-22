#!/usr/bin/env python3
"""
Basic health check script for AI Teddy Bear v5
Tests core dependencies and basic FastAPI functionality
"""

import sys
print(f"✅ Python version: {sys.version}")

# Test core imports
try:
    import fastapi
    print(f"✅ FastAPI {fastapi.__version__} imported successfully")
except ImportError as e:
    print(f"❌ FastAPI import failed: {e}")
    sys.exit(1)

try:
    import uvicorn
    print(f"✅ Uvicorn imported successfully")
except ImportError as e:
    print(f"❌ Uvicorn import failed: {e}")
    sys.exit(1)

try:
    import openai
    print(f"✅ OpenAI {openai.__version__} imported successfully")
except ImportError as e:
    print(f"❌ OpenAI import failed: {e}")
    sys.exit(1)

try:
    import sqlalchemy
    print(f"✅ SQLAlchemy {sqlalchemy.__version__} imported successfully")
except ImportError as e:
    print(f"❌ SQLAlchemy import failed: {e}")
    sys.exit(1)

try:
    import redis
    print(f"✅ Redis imported successfully")
except ImportError as e:
    print(f"❌ Redis import failed: {e}")
    sys.exit(1)

try:
    import pydantic
    print(f"✅ Pydantic {pydantic.__version__} imported successfully")
except ImportError as e:
    print(f"❌ Pydantic import failed: {e}")
    sys.exit(1)

try:
    import pytest
    print(f"✅ Pytest {pytest.__version__} imported successfully")
except ImportError as e:
    print(f"❌ Pytest import failed: {e}")
    sys.exit(1)

# Test basic FastAPI app creation
print("\n🔧 Testing FastAPI app creation...")
try:
    from fastapi import FastAPI
    from pydantic import BaseModel

    app = FastAPI(
        title="AI Teddy Bear v5 - Health Check",
        description="Basic health check endpoint",
        version="5.0.0-dev"
    )

    class HealthResponse(BaseModel):
        status: str
        message: str
        python_version: str
        dependencies: dict

    @app.get("/health", response_model=HealthResponse)
    async def health_check():
        return HealthResponse(
            status="healthy",
            message="All core dependencies loaded successfully",
            python_version=sys.version,
            dependencies={
                "fastapi": fastapi.__version__,
                "openai": openai.__version__,
                "sqlalchemy": sqlalchemy.__version__,
                "pydantic": pydantic.__version__,
                "pytest": pytest.__version__
            }
        )

    print("✅ FastAPI app created successfully")
    print("✅ Health endpoint defined")

except Exception as e:
    print(f"❌ FastAPI app creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n🎉 ALL CORE DEPENDENCIES LOADED SUCCESSFULLY!")
print("🚀 Ready to start development with Python 3.11.9")
print("\nTo start the server:")
print("python -m uvicorn health_check:app --host 127.0.0.1 --port 8000 --reload")
