from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import Optional
from mock_scammer import generate_reply

app = FastAPI(title="Paharedaar Honeypot API")

API_KEY = "Paharedaar_Api_au2026b"


# ----------------------------
# Request Models (STRICT)
# ----------------------------
class Message(BaseModel):
    sender: str
    text: str
    timestamp: int


class Metadata(BaseModel):
    channel: Optional[str] = None
    language: Optional[str] = None
    locale: Optional[str] = None


class HoneypotRequest(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: list
    metadata: Optional[Metadata] = None


# ----------------------------
# Health Check
# ----------------------------
@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "Paharedaar AI",
        "message": "API is live"
    }


# ----------------------------
# HONEYPOT ENDPOINT (IMPORTANT)
# ----------------------------
@app.post("/honeypot")
def honeypot_api(
    payload: HoneypotRequest,
    x_api_key: str = Header(None)
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    scam_text = payload.message.text

    reply = generate_reply(scam_text)


    return {
        "status": "success",
        "reply": reply
    }
