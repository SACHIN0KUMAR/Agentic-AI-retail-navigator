# graph/recommend_agent.py

from typing import Dict, Any, List
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from impactify.config import get_llm
from impactify.mock_apis.stock_api import search_product


SYSTEM_PROMPT = """
You are the RECOMMENDATION AGENT for Impactify Retail Navigator.

Your job:
- Understand what the user wants to buy (from their last message).
- Use the given product list to suggest up to 3 SKUs.
- Mention product name, price, and availability clearly.
- Ask the user how many units they want, then tell them to type:
  add <item name> <qty>  (e.g. add milk 1L 1, add milk 1L 3)

Be short, clear, and friendly.
If the product list is empty, politely say the item is not available and suggest browsing other categories.
"""

def recommendation_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Uses LLM + stock search to suggest SKUs and add them to 'suggested_items'.
    Always returns the updated state.
    """
    llm = get_llm()
    store_id = state.get("store", {}).get("id", "store_1")

    # ← use product_query first, fallback to last_user_message
    user_last = state.get("product_query") or state.get("last_user_message", "")

    # 1) Search products using the mock API
    search_results: List[Dict[str, Any]] = search_product(store_id, user_last)

    # 2) Build messages for LLM
    messages = [
    SystemMessage(content=SYSTEM_PROMPT),
    HumanMessage(
        content=(
            f"User is looking for: {user_last}\n"
            f"Store ID: {store_id}\n"
            f"Available products (JSON list): {search_results}\n"
            "Based on this, recommend up to 3 options. "
            "If the list is empty, say the item is unavailable. "
            "When showing the add format, use a concrete example like: add milk 1L 2"  # ← add this
        )
    ),
]

    # 3) Call LLM
    resp = llm.invoke(messages)
    explanation = resp.content if hasattr(resp, "content") else str(resp)

    # 4) Update state
    state["suggested_items"] = search_results
    state.setdefault("messages", []).append(AIMessage(content=explanation))
    state["route"] = "END"

    return state