import pytest
from httpx import AsyncClient

from src.main import app


@pytest.mark.asyncio
async def test_health_endpoint_no_sensitive_info():
    """Test that the health endpoint does not expose sensitive information."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert "version" in response.json()
    assert "status" in response.json()
    assert "debug" not in response.json()  # ✅
    assert "secret" not in response.json()  # ✅
