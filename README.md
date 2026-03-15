# TokAccounts

**TokAccounts** is a web platform for buying digital accounts and products, supporting both **cart** and **buy now** options. Payments are securely processed via **Paystack**, and admins can manage orders and track account availability.  

---

## Features

- Add multiple accounts to cart or buy immediately  
- Checkout with user details  
- Secure payment with Paystack  
- Admin order management and status updates  

---

## Tech Stack

- **Backend:** FastAPI + SQLAlchemy + PostgreSQL  
- **Frontend:** Jinja2 templates + Bootstrap  
- **Payment:** Paystack API  

---

## Setup

1. Clone the repo and create a virtual environment:
```bash
git clone https://github.com/<your-username>/TokAccounts.git
cd TokAccounts
python3 -m venv venv
source venv/bin/activate  # macOS/Linux