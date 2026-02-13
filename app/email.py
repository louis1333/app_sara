import os
import resend

resend.api_key = "re_9S8d1zqR_Ap5gunc7RKhNGLRjnXnxsR6b""

def send_email(subject, html_content, to):
    resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": to,  # tu correo personal
        "subject": subject,
        "html": html_content
    })
