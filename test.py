import requests

url = 'http://127.0.0.1:5000/gumroad_webhook'  # або твоя продакшн-URL

data = {
    'permalink': 'kvmaa',         # це має відповідати product.payment_id
    'email': 'urijozimko4@gmail.com'   # це має бути email користувача в базі
}

response = requests.post(url, data=data)

print('Status code:', response.status_code)
print('Redirected to:', response.url)