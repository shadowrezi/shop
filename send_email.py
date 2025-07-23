import requests
import os

from dotenv import load_dotenv

load_dotenv('.env')


RESEND_API_KEY = os.environ['RESEND_API_KEY']
FROM_EMAIL = 'onboarding@resend.dev'


def send_email(to_email, subject, html):
    url = 'https://api.resend.com/emails'
    headers = {
        'Authorization': f'Bearer {RESEND_API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        "from": "Your App <onboarding@resend.dev>",
        'to': [to_email],
        'subject': subject,
        'html': html
    }
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code in [200, 202]:
        print('Email sent!')
    else:
        print(f"error\n{response.text}")
