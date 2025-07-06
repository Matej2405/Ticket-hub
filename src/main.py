from fastapi import FastAPI
from .services import fetch_tickets  
from .api.routes import router as api_router
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="TicketHub", version="1.0")
app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "Welcome to TicketHub API 🎟️"}

@app.get("/tickets-debug")
async def tickets_debug():
    tickets = await fetch_tickets()
    return [t.dict() for t in tickets[:5]]  # vraća prvih 5 ticketa za provjeru
