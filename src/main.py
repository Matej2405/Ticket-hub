from src.api.routes import router as api_router
from src.services import fetch_tickets
from src.extensions import limiter
from dotenv import load_dotenv
from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
# Load .env variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="🎟️ TicketHub API",
    description="A REST API for managing tickets with DummyJSON integration.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)
app.include_router(api_router)

# Rate limiting setup
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/")
async def root():
    return {"message": "Welcome to TicketHub API"}


@app.get("/tickets-debug")
async def tickets_debug():
    tickets = await fetch_tickets()
    return [t.model_dump() for t in tickets[:5]]  # vraća prvih 5 ticketa za provjeru
