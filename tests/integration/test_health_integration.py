import pytest
from httpx import AsyncClient

from src.main import app

@pytest.mark.asyncio
async def test_health_endpoint_integration():
    """Test the /health endpoint for basic integration."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "AI Teddy Bear server is running"} # ✅ 
