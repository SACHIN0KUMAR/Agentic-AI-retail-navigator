# api/payment_api.py

from typing import Dict
import random


def initiate_payment(amount: float, user_id: str) -> Dict:
    """
    Mock payment gateway initiation.
    Returns a payment_id and a fake payment_link.
    """
    payment_id = f"PAY-{random.randint(100000, 999999)}"
    return {
        "payment_id": payment_id,
        "status": "PENDING",
        "amount": amount,
        "payment_link": f"https://mockpay.example.com/pay/{payment_id}",
        "user_id": user_id,
    }


def confirm_payment(payment_id: str) -> Dict:
    """
    Randomly approve/decline payment to test retries in boss-agent.
    """
    approved = random.random() > 0.2  # 80% success
    return {
        "payment_id": payment_id,
        "status": "SUCCESS" if approved else "DECLINED",
    }
