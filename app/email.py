import os
import resend

resend.api_key = os.getenv("RESEND_API_KEY")

def send_email(subject, html_content, to):
    resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": to,  # tu correo personal
        "subject": subject,
        "html": html_content
    })
