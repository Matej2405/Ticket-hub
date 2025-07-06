from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from ..services import fetch_tickets
from ..models import Ticket

router = APIRouter()

@router.get("/tickets")
async def get_tickets(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None, regex="^(open|closed)$"),
    priority: Optional[str] = Query(None, regex="^(low|medium|high)$")
):
    tickets = await fetch_tickets()

    # Filteriraj
    if status:
        tickets = [t for t in tickets if t.status == status]
    if priority:
        tickets = [t for t in tickets if t.priority == priority]

    # Paginacija
    start = (page - 1) * size
    end = start + size
    paginated = tickets[start:end]

    return [t.dict() for t in paginated]

@router.get("/tickets/{ticket_id}")
async def get_ticket(ticket_id: int):
    tickets = await fetch_tickets()
    for t in tickets:
        if t.id == ticket_id:
            return t.dict()
    raise HTTPException(status_code=404, detail="Ticket not found")

@router.get("/tickets/search")
async def search_tickets(q: str):
    tickets = await fetch_tickets()
    results = [t.dict() for t in tickets if q.lower() in t.title.lower()]
    return results
