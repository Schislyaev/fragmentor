import requests
import json

url = "https://api.cryptocloud.plus/v2/invoice/create"
headers = {
    "Authorization": "Token eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1dWlkIjoiTWpBMU56az0iLCJ0eXBlIjoicHJvamVjdCIsInYiOiJmNTc5ZmViZTFjNTllMGY3NDJjMDVkNjgyOTQ4YzUzZDU0YTQwMGRlZjdkMDIxNTM2NzM2ZTI1MmNkZWRjMjFkIiwiZXhwIjo4ODExMjkzNTU0NH0.Rb7g5OykMFhf2q69Toi9bPWCzWFULQQvC-plqOmTvhk",
    "Content-Type": "application/json"
}

data = {
    "amount": 100,
    "shop_id": "YHQP9kl1HXlf3PdR",
    "currency": "RUB"
}

response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    data = response.json().get('result').get('link')
    print("Success:", response.json())
else:
    print("Fail:", response.status_code, response.text)
