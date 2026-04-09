# graph/pickup_agent.py

from typing import Dict, Any
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from impactify.config import get_llm
from impactify.mock_apis.store_api import find_nearby_store   # ← FIXED IMPORT


SYSTEM_PROMPT = """
You are the PICKUP & DELIVERY AGENT of Impactify Retail Navigator.

Your job:
- Look at the user's location/pincode.
- Select or confirm the nearest store.
- Propose friendly pickup or delivery windows.
- Keep the message short, helpful, and conversational.
- Do NOT mention JSON, internal logic, or system structure.
"""


def pickup_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Assign store and propose pickup/delivery slots.
    Must ALWAYS return the SAME mutated state dictionary.
    """

    llm = get_llm()

    user_profile = state.get("user_profile", {})
    pincode = user_profile.get("pincode", "110001")

    # --- Find store ---
    store = find_nearby_store(pincode)
    state["store"] = store

    # --- Build LLM prompt ---
    prompt = f"""
User pincode: {pincode}
Nearest store: {store}

Suggest 2–3 reasonable pickup OR delivery time windows.
Be friendly and concise.
Ask the user which option they prefer.
"""

    chat = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=prompt)
    ]

    llm_resp = llm.invoke(chat)
    reply = llm_resp.content if hasattr(llm_resp, "content") else str(llm_resp)

    # --- Update state ---
    state.setdefault("messages", []).append(AIMessage(content=reply))
    state["route"] = "BOSS"

    return state
