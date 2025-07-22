#!/usr/bin/env python3
"""
STEP 6: HTTP Integration Testing Server
=====================================
FastAPI server with all functional routers for HTTP testing.
"""

import uvicorn
from fastapi.responses import JSONResponse
from fastapi import FastAPI
import asyncio
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


# Import functional routers
try:
    from src.presentation.api.parental_dashboard import router as parental_router
    parental_available = True
except ImportError as e:
    print(f"⚠️  Parental Dashboard router unavailable: {e}")
    parental_available = False

try:
    from src.presentation.api.chatgpt_endpoints import router as chatgpt_router
    chatgpt_available = True
except ImportError as e:
    print(f"⚠️  ChatGPT router unavailable: {e}")
    chatgpt_available = False

try:
    from src.presentation.api.auth_endpoints import router as auth_router
    auth_available = True
except ImportError as e:
    print(f"⚠️  Auth router unavailable: {e}")
    auth_available = False


def create_test_app() -> FastAPI:
    """Create FastAPI app with all functional routers."""

    app = FastAPI(
        title="AI Teddy HTTP Integration Test Server",
        description="Test server for STEP 6 HTTP integration testing",
        version="1.0.0"
    )

    # Add global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        return JSONResponse(
            status_code=500,
            content={"error": "Internal Server Error", "detail": str(exc)}
        )

    # Health check endpoint
    @app.get("/")
    async def root():
        return {
            "message": "AI Teddy HTTP Test Server",
            "status": "running",
            "available_routers": {
                "parental_dashboard": parental_available,
                "chatgpt": chatgpt_available,
                "auth": auth_available
            }
        }

    # Add available routers
    routers_added = 0

    if parental_available:
        app.include_router(parental_router)
        routers_added += 1
        print("✅ Added Parental Dashboard router")

    if chatgpt_available:
        app.include_router(chatgpt_router)
        routers_added += 1
        print("✅ Added ChatGPT router")

    if auth_available:
        app.include_router(auth_router)
        routers_added += 1
        print("✅ Added Auth router")

    print(f"🎯 Test server created with {routers_added}/3 functional routers")
    return app


def main():
    """Run the test server."""
    print("🚀 Starting AI Teddy HTTP Integration Test Server...")
    print("=" * 60)

    app = create_test_app()

    print("\n🌐 Server will be available at: http://localhost:8000")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔍 Alternative docs: http://localhost:8000/redoc")
    print("\n🎯 Ready for STEP 6 HTTP Integration Testing!")
    print("=" * 60)

    # Run server
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info",
        reload=False
    )


if __name__ == "__main__":
    main()
