import pytest
from httpx import AsyncClient
from src.main import app
from src.services import login_user

@pytest.mark.asyncio
async def test_get_tickets():
    token = await login_user("emilys", "emilyspass")
    assert token, "Login failed: no token returned"
    headers = {"Authorization": f"Bearer {token['access_token']}"}

    async with AsyncClient(base_url="http://localhost:8000") as ac:
        response = await ac.get("/tickets", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_get_tickets_unauthorized():
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        response = await ac.get("/tickets")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_ticket_by_id():
    token = await login_user("emilys", "emilyspass")
    assert token, "Login failed: no token returned"
    headers = {"Authorization": f"Bearer {token['access_token']}"}

    async with AsyncClient(base_url="http://localhost:8000") as ac:
        response = await ac.get("/tickets/1", headers=headers)
    assert response.status_code == 200
    assert "id" in response.json()
