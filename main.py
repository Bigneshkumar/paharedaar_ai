from fastapi import FastAPI, Header, HTTPException
import re

API_KEY = "PAHAREDAAR_SECRET_123"

app = FastAPI(title="Paharedaar AI")

@app.get("/")
def health():
    return {"status": "ok", "service": "Paharedaar AI"}

@app.post("/paharedaar/process")
def process_message(
    payload: dict,
    x_api_key: str = Header(...)
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    text = payload.get("message", "")

    upi = re.findall(r"\b[\w.-]+@[a-zA-Z]+\b", text)
    bank = re.findall(r"\b\d{9,18}\b", text)
    urls = re.findall(r"https?://\S+", text)

    return {
        "response": "Please explain again, I am confused about the payment.",
        "state": "TRUST_BUILDING",
        "extracted_intelligence": {
            "upi_ids": upi,
            "bank_accounts": bank,
            "urls": urls
        }
    }
