from pydantic import BaseModel

class Ticket(BaseModel):
    id: int
    title: str
    status: str  # "open" ili "closed"
    priority: str  # "low", "medium", "high"
    assignee: str  # korisničko ime
