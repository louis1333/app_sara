import os
import requests

BREVO_API_KEY = os.environ.get("BREVO_API_KEY")
FROM_EMAIL = "louis.alejo133@gmail.com"
FROM_NAME = "App Koalita"

def send_email(subject, html_content, to):
    if not BREVO_API_KEY:
        print("BREVO_API_KEY not set, skipping email")
        return

    response = requests.post(
        "https://api.brevo.com/v3/smtp/email",
        headers={
            "api-key": BREVO_API_KEY,
            "Content-Type": "application/json"
        },
        json={
            "sender": {"name": FROM_NAME, "email": FROM_EMAIL},
            "to": [{"email": to}],
            "subject": subject,
            "htmlContent": html_content
        },
        timeout=10
    )
    response.raise_for_status()
