# graph/payment_agent.py

from typing import Dict, Any, List
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from impactify.mock_apis.payment_api import initiate_payment, confirm_payment
from impactify.config import get_llm



SYSTEM_PROMPT = """
You are the PAYMENT AGENT of Impactify Retail Navigator.

Your responsibilities:
- Initiate payment.
- Confirm payment.
- Explain results in short, friendly language.
- Do NOT mention JSON, code, or internal logic.
"""


def payment_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handles payment initiation and confirmation.
    Must always return the same state dict.
    """

    llm = get_llm()

    # --- Compute final amount ---
    pricing = state.get("pricing", {})
    final_amount = pricing.get("final_total")

    if final_amount is None:
        # Fallback: compute from cart
        cart = state.get("cart", [])
        final_amount = sum(item["price"] * item["qty"] for item in cart)

    # --- Get User ID ---
    user_id = state.get("user_profile", {}).get("user_id", "user_1")

    # --- Start payment ---
    payment_init = initiate_payment(final_amount, user_id)
    payment_id = payment_init["payment_id"]

    # --- Confirm payment (mock) ---
    payment_result = confirm_payment(payment_id)

    # --- Build assistant summary using LLM ---
    msg_prompt = f"""
Payment attempt for {final_amount} by user {user_id}.
Payment status: {payment_result['status']}.
Write a short friendly response for the user.
"""

    chat_messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=msg_prompt),
    ]

    llm_resp = llm.invoke(chat_messages)
    reply_text = llm_resp.content if hasattr(llm_resp, "content") else str(llm_resp)

    # --- Update state ---
    state.setdefault("messages", []).append(AIMessage(content=reply_text))

    if payment_result["status"] == "SUCCESS":
        state["order_status"] = "CONFIRMED"
        state["done"] = True
        state["route"] = "END"
    else:
        state["order_status"] = "FAILED"
        # Payment failed → allow BOSS to retry or ask user
        state["route"] = "PAYMENT"

    return state
