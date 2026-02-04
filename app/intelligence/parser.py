import re

def extract_intelligence(text: str):
    return {
        "upi_ids": re.findall(r"\b[\w.-]+@[a-zA-Z]+\b", text),
        "bank_accounts": re.findall(r"\b\d{9,18}\b", text),
        "urls": re.findall(r"https?://\S+", text)
    }
