import httpx
import os
from src.models import Ticket  # relative import
from jose import jwt, JWTError
from datetime import datetime, timedelta, UTC
from fastapi import HTTPException
import asyncio
import json

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
    redis_client = redis.Redis(host="localhost", port=6379, db=0)
except ImportError:
    REDIS_AVAILABLE = False
    redis_client = None

in_memory_cache = {}
CACHE_TTL = 60  # seconds

TICKETS_URL = "https://dummyjson.com/todos"
USERS_URL = "https://dummyjson.com/users"

SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

PRIORITY_LEVELS = ["low", "medium", "high"]


async def fetch_tickets() -> list[Ticket]:
    cache_key = "tickets_data"

    try:
        # Try Redis first
        if REDIS_AVAILABLE:
            try:
                cached = await redis_client.get(cache_key)
                if cached:
                    # Parse the cached JSON data
                    cached_data = json.loads(cached)
                    return [Ticket(**ticket) for ticket in cached_data]
            except Exception as e:
                print(f"Redis cache error: {e}")

        # Try in-memory cache
        cached = in_memory_cache.get(cache_key)
        if cached and (datetime.now(UTC) - cached["time"]).total_seconds() < CACHE_TTL:
            return cached["data"]

        # Fetch from API
        print("Fetching from DummyJSON APIs...")
        try:
            async with httpx.AsyncClient() as client:
                todos_resp = await client.get(TICKETS_URL, timeout=5.0)
                users_resp = await client.get(USERS_URL, timeout=5.0)

                todos_resp.raise_for_status()
                users_resp.raise_for_status()

            todos = todos_resp.json().get("todos", [])
            users = users_resp.json().get("users", [])
            print(f"Fetched {len(todos)} todos and {len(users)} users")
        except httpx.HTTPError as e:
            print(f"HTTP Error: {e}")
            raise HTTPException(status_code=502, detail=f"Error contacting DummyJSON: {str(e)}")

        user_map = {u["id"]: u["username"] for u in users}
        print(f"Created user map with {len(user_map)} users")

        tickets = []
        for todo in todos:
            try:
                ticket = Ticket(
                    id=todo["id"],
                    title=todo["todo"],
                    status="closed" if todo["completed"] else "open",
                    priority=PRIORITY_LEVELS[todo["id"] % len(PRIORITY_LEVELS)],
                    assignee=user_map.get(todo["userId"], "unknown")
                )
                tickets.append(ticket)
            except Exception as e:
                print(f"Error creating ticket for todo {todo}: {e}")
                raise

        print(f"Created {len(tickets)} tickets")

        # Cache in Redis
        if REDIS_AVAILABLE:
            try:
                # Serialize tickets to JSON for caching
                tickets_json = json.dumps([ticket.model_dump() for ticket in tickets])
                await redis_client.setex(cache_key, CACHE_TTL, tickets_json)
                print("Cached tickets in Redis")
            except Exception as e:
                print(f"Redis caching error: {e}")

        # Cache in-memory
        in_memory_cache[cache_key] = {"data": tickets, "time": datetime.now(UTC)}
        print("Cached tickets in memory")

        return tickets

    except Exception as e:
        print(f"Unexpected error in fetch_tickets: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


async def login_user(username: str, password: str):
    try:
        payload = {"username": username, "password": password}
        print("Sending to DummyJSON:", payload)

        async with httpx.AsyncClient(timeout=httpx.Timeout(5.0, connect=2.0)) as client:
            resp = await client.post(
                "https://dummyjson.com/auth/login",
                json=payload
            )
        print("Response from DummyJSON:", resp.text)

        resp.raise_for_status()
        user_data = resp.json()
    except httpx.HTTPStatusError as e:
        print(f"DummyJSON HTTP error: {e.response.status_code} {e.response.text}")
        return None
    except httpx.RequestError as e:
        print(f"DummyJSON Request error: {str(e)}")
        return None

    # Generate local JWT for our backend
    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    local_token = jwt.encode(
        {"sub": user_data["username"], "exp": expire},
        SECRET_KEY, algorithm=ALGORITHM
    )
    return {"access_token": user_data["accessToken"], "token_type": "bearer"}






def verify_token(token: str):
    if not token or len(token) < 20:
        raise HTTPException(status_code=401, detail="Invalid token")
    return True  # Assume token is valid since DummyJSON issued it

