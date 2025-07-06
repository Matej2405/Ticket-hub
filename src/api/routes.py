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

@router.get("/stats")
async def get_stats():
    tickets = await fetch_tickets()

    total = len(tickets)
    open_tickets = len([t for t in tickets if t.status == "open"])
    closed_tickets = total - open_tickets

    priority_counts = {"low": 0, "medium": 0, "high": 0}
    assignee_counts = {}

    for t in tickets:
        priority_counts[t.priority] += 1
        assignee_counts[t.assignee] = assignee_counts.get(t.assignee, 0) + 1

    top_assignee = max(assignee_counts.items(), key=lambda x: x[1])[0]

    return {
        "total_tickets": total,
        "open": open_tickets,
        "closed": closed_tickets,
        "priority_distribution": priority_counts,
        "top_assignee": top_assignee
    }

