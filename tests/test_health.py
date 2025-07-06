import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["api"] == "ok"
    assert "dummyjson" in data
    assert "redis" in data
