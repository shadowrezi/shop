import os
import smtplib
from email.mime.text import MIMEText

from dotenv import load_dotenv

load_dotenv('.env')

SMTP_SERVER = 'smtp.ukr.net'
SMTP_PORT = 465
EMAIL_ADDRESS = 'shadowshop@ukr.net'
EMAIL_PASSWORD = os.environ['EMAIL_PASSWORD']


def send_email(to_email: str, subject: str, body: str) -> None:
    message = MIMEText(body, 'plain', 'utf-8')
    
    message['Subject'] = subject
    message['From'] = EMAIL_ADDRESS
    message['To'] = to_email
    
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, to_email, message.as_string())
