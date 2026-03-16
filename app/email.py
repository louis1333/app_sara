import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

BREVO_SMTP_LOGIN = "louis.alejo133@gmail.com"
BREVO_SMTP_KEY = os.environ.get("BREVO_SMTP_KEY")

def send_email(subject, html_content, to):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = f"App Koalita <{BREVO_SMTP_LOGIN}>"
    msg['To'] = to

    msg.attach(MIMEText(html_content, 'html'))

    with smtplib.SMTP('smtp-relay.brevo.com', 587) as server:
        server.starttls()
        server.login(BREVO_SMTP_LOGIN, BREVO_SMTP_KEY)
        server.sendmail(BREVO_SMTP_LOGIN, to, msg.as_string())
