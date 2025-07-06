import pytest
from httpx import AsyncClient
from src.main import app

@pytest.mark.asyncio
async def test_login_success():
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        response = await ac.post("/auth/login", data={
            "username": "emilys",
            "password": "emilyspass"
        })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_fail():
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        response = await ac.post("/auth/login", data={
            "username": "wronguser",
            "password": "wrongpass"
        })
    assert response.status_code == 401
