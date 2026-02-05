import re
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict

# --- INITIALIZATION ---
app = FastAPI(title="Paharedaar_API")

# --- CONFIGURATION ---
# As per your requirement
REQUIRED_API_KEY = "Paharedaar_Api_au2026b"

# --- DATA MODELS (Ensures structured JSON output) ---
class Intelligence(BaseModel):
    upi_ids: List[str] = []
    bank_accounts: List[str] = []
    links: List[str] = []

class ScamResponse(BaseModel):
    response: str
    extracted_intelligence: Intelligence
    status: str  # ENGAGING, EXTRACTED, or TERMINATED

class ScamRequest(BaseModel):
    session_id: str
    message: str

# Memory to track the conversation stage for each session
# Stage 0: Naive Intro, Stage 1: Baiting (Asking for UPI), Stage 2: Error Verification
session_stages: Dict[str, int] = {}

# --- 1. DETECTION GATEWAY ---
def is_malicious(text: str) -> bool:
    """Identify if the incoming message is a scam attempt."""
    keywords = ["win", "lottery", "prize", "bank", "account", "click", "urgent", "kyc", "blocked", "customer care"]
    return any(word in text.lower() for word in keywords)

# --- 2. INTELLIGENCE PARSER (Regex) ---
def extract_intelligence(text: str) -> Intelligence:
    """Scrapes financial details using Regular Expressions."""
    upi_regex = r'[a-zA-Z0-9.\-_]+@[a-zA-Z]{3,}'
    bank_regex = r'\b\d{9,18}\b'
    url_regex = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
    
    return Intelligence(
        upi_ids=re.findall(upi_regex, text),
        bank_accounts=re.findall(bank_regex, text),
        links=re.findall(url_regex, text)
    )

# --- 3. STATE MACHINE AGENT (Paharedaar AI Logic) ---
def get_paharedaar_reply(user_msg: str, session_id: str, intel: Intelligence) -> str:
    """
    Simulates the Paharedaar AI persona:
    - Feigns ignorance
    - Uses Bait and Switch
    - Verifies with Errors
    """
    stage = session_stages.get(session_id, 0)
    msg = user_msg.lower()

    # STRATEGY: Verify with Errors (If data is found)
    if intel.upi_ids or intel.bank_accounts:
        data = intel.upi_ids[0] if intel.upi_ids else intel.bank_accounts[0]
        # Create a fake version with a wrong digit to trigger the "Verify with Error" strategy
        fake_data = data[:-1] + ("1" if data[-1] != "1" else "2")
        session_stages[session_id] = 2
        return f"Wait, my eyes are quite weak. Is the account/ID {fake_data}? I want to make sure I don't send the money to the wrong place."

    # STRATEGY: Bait and Switch (If a link is sent)
    if "http" in msg or intel.links:
        session_stages[session_id] = 1
        return "I tried clicking that link but my phone says 'System Blocked'. It is a very old phone. Can you just give me your UPI ID or Bank Account number instead? I'll type it in manually."

    # STRATEGY: Feign Ignorance (Stage 0)
    if stage == 0:
        session_stages[session_id] = 1
        return "Oh! Thank you for contacting me. I was worried about my account. How can I start the process? I'm not very good with these things."

    # DEFAULT: Stall the conversation
    return "I'm sorry, I got a bit confused. Could you explain that again? What do I need to do next?"

# --- THE API ENDPOINT ---

@app.post("/paharedaar_API/detect", response_model=ScamResponse)
async def paharedaar_endpoint(
    request: ScamRequest, 
    x_api_key: Optional[str] = Header(None, alias="x-api-key")
):
    # 1. Security Authentication Check
    if x_api_key != REQUIRED_API_KEY:
        raise HTTPException(
            status_code=401, 
            detail="Unauthorized: Invalid Paharedaar API Key"
        )

    # 2. Run Detection Gateway
    # If the message isn't malicious and we haven't started yet, ask who they are.
    if not is_malicious(request.message) and request.session_id not in session_stages:
        return ScamResponse(
            response="Hello? Who is this and why are you messaging me?",
            extracted_intelligence=Intelligence(),
            status="ENGAGING"
        )

    # 3. Intelligence Parsing
    intel = extract_intelligence(request.message)

    # 4. Generate AI Persona Response via State Machine
    ai_reply = get_paharedaar_reply(request.message, request.session_id, intel)

    # 5. Determine Current Status
    current_status = "ENGAGING"
    if intel.upi_ids or intel.bank_accounts:
        current_status = "EXTRACTED"
    
    # Optional termination logic
    if "goodbye" in ai_reply.lower() or "take care" in ai_reply.lower():
        current_status = "TERMINATED"

    # 6. Return Structured JSON
    return ScamResponse(
        response=ai_reply,
        extracted_intelligence=intel,
        status=current_status
    )

# TO RUN: uvicorn main:app --host 0.0.0.0 --port 8000