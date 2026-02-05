import re
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict

app = FastAPI(title="Paharedaar_API")

# --- CONFIGURATION ---
REQUIRED_API_KEY = "Paharedaar_Api_au2026b"

# --- DATA MODELS ---
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

# Memory to track the stage of the conversation
session_stages: Dict[str, int] = {}

# --- 1. DETECTION GATEWAY (Keyword Classifier) ---
def is_malicious(text: str) -> bool:
    keywords = ["win", "prize", "lottery", "bank", "account", "click", "urgent", "kyc", "limit", "blocked"]
    return any(word in text.lower() for word in keywords)

# --- 2. INTELLIGENCE PARSER (Regex Scraper) ---
def extract_intelligence(text: str) -> Intelligence:
    upi_regex = r'[a-zA-Z0-9.\-_]+@[a-zA-Z]{3,}'
    bank_regex = r'\b\d{9,18}\b'
    url_regex = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
    
    return Intelligence(
        upi_ids=re.findall(upi_regex, text),
        bank_accounts=re.findall(bank_regex, text),
        links=re.findall(url_regex, text)
    )

# --- 3. STATE MACHINE AGENT (Paharedaar AI Persona) ---
def get_paharedaar_reply(user_msg: str, session_id: str, intel: Intelligence) -> str:
    stage = session_stages.get(session_id, 0)
    msg = user_msg.lower()

    # Strategy: Verify with Errors (If info is found)
    if intel.upi_ids or intel.bank_accounts:
        data = intel.upi_ids[0] if intel.upi_ids else intel.bank_accounts[0]
        # Flip the last two digits to act confused
        corrupted = data[:-2] + data[-1] + data[-2] if len(data) > 2 else data
        session_stages[session_id] = 2
        return f"Wait, my eyes are blurry. Is the account number {corrupted}? I want to be sure I don't send it to the wrong person."

    # Strategy: Bait and Switch (If link is sent)
    if "http" in msg or intel.links:
        session_stages[session_id] = 1
        return "I tried clicking that link but my phone says 'System Blocked'. It's very old. Do you have a UPI ID or a Bank Account number I can use instead?"

    # Strategy: Feign Ignorance
    if stage == 0:
        session_stages[session_id] = 1
        return "Oh! Thank you for reaching out. I really need help with my account. How do I start the process? I'm not good with phones."

    return "I'm a bit confused. Could you explain that again? I have my pen and paper ready to write down the steps."

# --- API ENDPOINT ---
@app.post("/paharedaar_API/detect", response_model=ScamResponse)
async def paharedaar_endpoint(
    request: ScamRequest, 
    x_api_key: Optional[str] = Header(None, alias="x-api-key")
):
    # Security Authentication
    if x_api_key != REQUIRED_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid API Key")

    # Detection Gateway
    if not is_malicious(request.message) and request.session_id not in session_stages:
        return ScamResponse(
            response="Hello? Who is this?",
            extracted_intelligence=Intelligence(),
            status="ENGAGING"
        )

    # Intelligence Extraction
    intel = extract_intelligence(request.message)

    # State Machine Response
    ai_reply = get_paharedaar_reply(request.message, request.session_id, intel)

    # Determine Status
    current_status = "ENGAGING"
    if intel.upi_ids or intel.bank_accounts:
        current_status = "EXTRACTED"
    if "goodbye" in ai_reply.lower():
        current_status = "TERMINATED"

    return ScamResponse(
        response=ai_reply,
        extracted_intelligence=intel,
        status=current_status
    )