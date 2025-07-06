from fastapi import FastAPI, Request
from .services import fetch_tickets  
from .api.routes import router as api_router
from dotenv import load_dotenv
load_dotenv()
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

app = FastAPI(title="TicketHub", version="1.0")
app.include_router(api_router)

# Rate limiter setup
limiter = Limiter(key_func=lambda request: request.client.host)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/")
async def root():
    return {"message": "Welcome to TicketHub API 🎟️"}

@app.get("/tickets-debug")
async def tickets_debug():
    tickets = await fetch_tickets()
    return [t.dict() for t in tickets[:5]]  # vraća prvih 5 ticketa za provjeru
