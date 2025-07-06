import httpx
from .models import Ticket

TICKETS_URL = "https://dummyjson.com/todos"
USERS_URL = "https://dummyjson.com/users"

async def fetch_tickets() -> list[Ticket]:
    async with httpx.AsyncClient() as client:
        todos_resp = await client.get(TICKETS_URL)
        users_resp = await client.get(USERS_URL)

    todos = todos_resp.json().get("todos", [])
    users = users_resp.json().get("users", [])

    user_map = {u["id"]: u["username"] for u in users}

    tickets = []
    for todo in todos:
        ticket = Ticket(
            id=todo["id"],
            title=todo["todo"],
            status="closed" if todo["completed"] else "open",
            priority=["low", "medium", "high"][todo["id"] % 3],
            assignee=user_map.get(todo["userId"], "unknown")
        )
        tickets.append(ticket)

    return tickets
