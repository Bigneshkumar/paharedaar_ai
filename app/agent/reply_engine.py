def generate_reply(message_text: str) -> str:
    keywords = ["blocked", "verify", "account", "urgent", "bank"]

    if any(k in message_text.lower() for k in keywords):
        return "Why is my account being suspended?"

    return "Can you explain that again? I’m not very familiar with this."
