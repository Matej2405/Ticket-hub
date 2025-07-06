import pytest
from httpx import AsyncClient
from src.main import app
from src.services import login_user

@pytest.mark.asyncio
async def test_stats():
    token = await login_user("emilys", "emilyspass")
    assert token, "Login failed: no token returned"
    headers = {"Authorization": f"Bearer {token['access_token']}"}

    async with AsyncClient(base_url="http://localhost:8000") as ac:
        response = await ac.get("/stats", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_tickets" in data
    assert "open" in data
    assert "closed" in data
    assert "priority_distribution" in data
    assert "top_assignee" in data

@pytest.mark.asyncio
async def test_stats_unauthorized():
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        response = await ac.get("/stats")
    assert response.status_code == 401
