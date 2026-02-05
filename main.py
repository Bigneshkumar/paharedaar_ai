import re
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict

app = FastAPI(title="Paharedaar_API")

REQUIRED_API_KEY = "Paharedaar_Api_au2026b"

class Intelligence(BaseModel):
    upi_ids: List[str] = []
    bank_accounts: List[str] = []
    links: List[str] = []

class ScamResponse(BaseModel):
    response: str
    extracted_intelligence: Intelligence
    status: str

class ScamRequest(BaseModel):
    session_id: str
    message: str

session_stages: Dict[str, int] = {}

# --- HELPER: Root path to avoid "Not Found" ---
@app.get("/")
async def root():
    return {"status": "Online", "name": "Paharedaar AI Sentinel"}

# --- 1. DETECTION GATEWAY ---
def is_malicious(text: str) -> bool:
    keywords = ["win", "prize", "lottery", "bank", "account", "click", "urgent", "kyc"]
    return any(word in text.lower() for word in keywords)

# --- 2. INTELLIGENCE PARSER ---
def extract_intelligence(text: str) -> Intelligence:
    upi_regex = r'[a-zA-Z0-9.\-_]+@[a-zA-Z]{3,}'
    bank_regex = r'\b\d{9,18}\b'
    url_regex = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
    return Intelligence(
        upi_ids=re.findall(upi_regex, text),
        bank_accounts=re.findall(bank_regex, text),
        links=re.findall(url_regex, text)
    )

# --- 3. STATE MACHINE ---
def get_paharedaar_reply(user_msg: str, session_id: str, intel: Intelligence) -> str:
    stage = session_stages.get(session_id, 0)
    if intel.upi_ids or intel.bank_accounts:
        data = intel.upi_ids[0] if intel.upi_ids else intel.bank_accounts[0]
        corrupted = data[:-1] + ("1" if data[-1] != "1" else "2")
        return f"Wait, is the account {corrupted}? My eyes are a bit blurry."
    if intel.links:
        return "The link isn't opening on my old phone. Do you have a UPI ID instead?"
    return "Oh! Thank you. How do I start? I am not good with technology."

# --- 4. THE POST ENDPOINT ---
@app.post("/paharedaar_API/detect", response_model=ScamResponse)
async def paharedaar_endpoint(request: ScamRequest, x_api_key: Optional[str] = Header(None, alias="x-api-key")):
    if x_api_key != REQUIRED_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    intel = extract_intelligence(request.message)
    ai_reply = get_paharedaar_reply(request.message, request.session_id, intel)

    return ScamResponse(
        response=ai_reply,
        extracted_intelligence=intel,
        status="EXTRACTED" if (intel.upi_ids or intel.bank_accounts) else "ENGAGING"
    )