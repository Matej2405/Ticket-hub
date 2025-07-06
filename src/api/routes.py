from fastapi import APIRouter, Query, HTTPException, Depends, Request
from typing import Optional
from src.services import fetch_tickets, login_user, verify_token, redis_client
from src.models import Ticket
from src.extensions import limiter
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
import httpx

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.get("/tickets")
@limiter.limit("10/second")
async def get_tickets(
    request: Request,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None, pattern="^(open|closed)$"),
    priority: Optional[str] = Query(None, pattern="^(low|medium|high)$"),
    token: str = Depends(oauth2_scheme)
):
    verify_token(token)
    tickets = await fetch_tickets()

    if status:
        tickets = [t for t in tickets if t.status == status]
    if priority:
        tickets = [t for t in tickets if t.priority == priority]

    start = (page - 1) * size
    end = start + size
    paginated = tickets[start:end]

    return [t.model_dump() for t in paginated]


@router.get("/tickets/{ticket_id}")
@limiter.limit("10/second")
async def get_ticket(
    request: Request,
    ticket_id: int,
    token: str = Depends(oauth2_scheme)
):
    verify_token(token)
    tickets = await fetch_tickets()
    for t in tickets:
        if t.id == ticket_id:
            return t.model_dump()
    raise HTTPException(status_code=404, detail="Ticket not found")


@router.get("/tickets/search")
@limiter.limit("10/second")
async def search_tickets(
    request: Request,
    q: str,
    token: str = Depends(oauth2_scheme)
):
    verify_token(token)
    tickets = await fetch_tickets()
    results = [t.model_dump() for t in tickets if q.lower() in t.title.lower()]
    return results


@router.get("/stats")
@limiter.limit("10/second")
async def get_stats(
    request: Request,
    token: str = Depends(oauth2_scheme)
):
    verify_token(token)
    tickets = await fetch_tickets()

    total = len(tickets)
    open_tickets = sum(1 for t in tickets if t.status == "open")
    closed_tickets = total - open_tickets
    priority_counts = {"low": 0, "medium": 0, "high": 0}
    assignee_counts = {}

    for t in tickets:
        priority_counts[t.priority] += 1
        assignee_counts[t.assignee] = assignee_counts.get(t.assignee, 0) + 1

    top_assignee = max(assignee_counts.items(), key=lambda x: x[1])[0] if assignee_counts else None

    return {
        "total_tickets": total,
        "open": open_tickets,
        "closed": closed_tickets,
        "priority_distribution": priority_counts,
        "top_assignee": top_assignee
    }


@router.post("/auth/login")
@limiter.limit("5/second")  # Stricter rate limit for login
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends()
):
    token = await login_user(form_data.username, form_data.password)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return token


@router.get("/health", include_in_schema=False)
async def health_check(request: Request):
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get("https://dummyjson.com/todos", timeout=3.0)
            resp.raise_for_status()
        dummyjson_status = "ok"
    except Exception:
        dummyjson_status = "unreachable"

    redis_status = "not configured"
    if redis_client:
        try:
            pong = await redis_client.ping()
            redis_status = "ok" if pong else "unreachable"
        except Exception:
            redis_status = "unreachable"

    return {
        "api": "ok",
        "dummyjson": dummyjson_status,
        "redis": redis_status
    }
