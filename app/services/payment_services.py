import requests
import os
from dotenv import load_dotenv
load_dotenv()
PAYSTACK_SECRET_KEY = os.getenv('PAYSTACK_SECRET_KEY')

def initialize_payment(email: str, amount: int):
    url = "https://api.paystack.co/transaction/initialize"
    
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "email": email,
        "amount": amount * 100,  
        "callback_url": "http://localhost:8910/payment/callback"
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()
def verify_payment (reference:str):
    url: str = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    return response.json()