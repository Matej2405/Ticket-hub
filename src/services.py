import httpx
import os
from .models import Ticket
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import HTTPException

# URLs
TICKETS_URL = "https://dummyjson.com/todos"
USERS_URL = "https://dummyjson.com/users"

# Security config (load from .env or fallback)
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Priority levels
PRIORITY_LEVELS = ["low", "medium", "high"]

async def fetch_tickets() -> list[Ticket]:
    try:
        async with httpx.AsyncClient() as client:
            todos_resp = await client.get(TICKETS_URL, timeout=5.0)
            users_resp = await client.get(USERS_URL, timeout=5.0)

            todos_resp.raise_for_status()
            users_resp.raise_for_status()

        todos = todos_resp.json().get("todos", [])
        users = users_resp.json().get("users", [])
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Error contacting DummyJSON: {str(e)}")

    user_map = {u["id"]: u["username"] for u in users}

    tickets = []
    for todo in todos:
        ticket = Ticket(
            id=todo["id"],
            title=todo["todo"],
            status="closed" if todo["completed"] else "open",
            priority=PRIORITY_LEVELS[todo["id"] % len(PRIORITY_LEVELS)],
            assignee=user_map.get(todo["userId"], "unknown")
        )
        tickets.append(ticket)

    return tickets

async def login_user(username: str, password: str):
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post("https://dummyjson.com/auth/login", json={
                "username": username,
                "password": password
            }, timeout=5.0)

        resp.raise_for_status()
        user_data = resp.json()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Login service error: {str(e)}")
    except Exception:
        return None

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = jwt.encode({"sub": user_data["username"], "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": token, "token_type": "bearer"}

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
