def next_state(current_state: str, intel: dict):
    if intel["upi_ids"] or intel["bank_accounts"]:
        return "VERIFICATION"
    if current_state == "INIT":
        return "TRUST_BUILDING"
    return current_state

def generate_response(state: str):
    responses = {
        "INIT": "Sorry, I didn’t understand.",
        "TRUST_BUILDING": "I’m not familiar with this. Can you explain?",
        "VERIFICATION": "Let me confirm the details once."
    }
    return responses.get(state, "Okay.")
