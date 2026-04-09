# graph/promo_agent.py

from typing import Dict, Any, List
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from impactify.mock_apis.promo_api import apply_promos
from impactify.config import get_llm



SYSTEM_PROMPT = """
You are the PROMO AGENT of Impactify Retail Navigator.
Your tasks:
- Analyze cart items.
- Apply discount rules and bundle offers.
- Explain promos in a short, friendly way.
- Never mention JSON, internal functions, or implementation details.
"""


def promo_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Applies promotion rules and explains discount summary to user.
    Always returns the SAME updated state dict.
    """
    llm = get_llm()
    cart: List[Dict[str, Any]] = state.get("cart", [])

    # No cart → no promos
    if not cart:
        state.setdefault("messages", []).append(
            AIMessage(content="Your cart is empty — add items to check available discounts!")
        )
        state["route"] = "BOSS"
        return state

    # Apply promo rules via mock API
    promo_result = apply_promos(cart)
    state["pricing"] = promo_result

    # Prepare an LLM explanation
    msg_prompt = f"""
Cart: {cart}
Promotion Results: {promo_result}

Explain:
- Discounts applied
- Bundle savings
- Final total
Do it in a friendly, simple style.
"""

    chat_messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=msg_prompt),
    ]

    llm_resp = llm.invoke(chat_messages)
    reply_text = llm_resp.content if hasattr(llm_resp, "content") else str(llm_resp)

    # Add message to state
    state.setdefault("messages", []).append(AIMessage(content=reply_text))

    # Return control to BOSS agent
    state["route"] = "BOSS"
    return state
