from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="Paharedaar AI",
    description="Agentic Honeypot for Scam Detection",
    version="1.0.0"
)

@app.get("/")
def health():
    return {
        "status": "ok",
        "service": "Paharedaar AI",
        "message": "API is live"
    }

app.include_router(router, prefix="/paharedaar")
