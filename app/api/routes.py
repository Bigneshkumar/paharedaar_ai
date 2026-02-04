from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.security.api_key import verify_api_key
from app.intelligence.parser import extract_intelligence
from app.agent.state_machine import next_state, generate_response

router = APIRouter()

class InboundMessage(BaseModel):
    message: str
    state: str = "INIT"

@router.post("/process")
def process_message(
    payload: InboundMessage,
    _: str = Depends(verify_api_key)
):
    intel = extract_intelligence(payload.message)
    new_state = next_state(payload.state, intel)
    response = generate_response(new_state)

    return {
        "response": response,
        "state": new_state,
        "extracted_intelligence": intel
    }
