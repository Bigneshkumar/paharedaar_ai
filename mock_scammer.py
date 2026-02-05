def generate_reply(scam_text: str) -> str:
    scam_text = scam_text.lower()

    if "account" in scam_text:
        return "Why is my account being suspended?"

    if "otp" in scam_text:
        return "I did not request any OTP. Why are you asking?"

    if "verify" in scam_text:
        return "Can you explain why verification is needed urgently?"

    if "blocked" in scam_text:
        return "My account was working fine. What happened suddenly?"

    return "Can you please provide more details?"
