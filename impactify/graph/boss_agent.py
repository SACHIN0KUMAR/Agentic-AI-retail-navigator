# graph/boss_agent.py

from typing import Literal, Dict, Any, List, cast
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from impactify.config import get_llm


# -------------------------
# 1. THE SCHEMA
# -------------------------
class BossDecision(BaseModel):
    """Decide the next step in the retail conversation."""
    next_action: Literal["RECOMMENDATION", "STOCK_CHECK", "PROMO", "PICKUP", "PAYMENT", "END"]
    assistant_reply: str = Field(
        default="Processing your request...",
        description="A natural language reply to the user explaining what you are doing."
    )
    product_query: str = Field(
        default="",
        description="The product the user is looking for, e.g. 'milk', 'bread'. Empty if not applicable."
    )


# -------------------------
# 2. THE PROMPT
# -------------------------
SYSTEM_PROMPT = """
You are the Boss Agent of Impactify Retail Navigator.
Analyze the user input and decide the next action.
You MUST respond with a valid JSON object matching the requested schema.

ROUTING RULES:
- User mentions a product name WITHOUT a quantity (e.g. "milk", "I want milk"): RECOMMENDATION
- User says 'add', 'buy', 'get me', or mentions a quantity (e.g. "add 2 milk", "buy 1 bread"): STOCK_CHECK
- User asks about discounts/offers: PROMO
- User asks about delivery/pickup: PICKUP
- User wants to checkout/pay: PAYMENT
- User says goodbye/finished/done: END

PRODUCT QUERY RULES:
- Extract the core product name (e.g. "milk", "bread", "eggs").
- If user says "show me recommendations" without a product, use the last product they mentioned.
- If no product is mentioned, leave product_query empty.

IMPORTANT: When in doubt between RECOMMENDATION and STOCK_CHECK, always choose RECOMMENDATION first.
"""


# -------------------------
# 3. THE NODE FUNCTION
# -------------------------
def boss_decide(state: Dict[str, Any]) -> Dict[str, Any]:
    llm = get_llm()

    messages = state.get("messages", [])
    user_last = state.get("last_user_message", "")

    chat: List[BaseMessage] = [SystemMessage(content=SYSTEM_PROMPT)]
    chat.extend(messages)
    chat.append(HumanMessage(content=f"User said: {user_last}"))

    structured_llm = llm.with_structured_output(BossDecision)

    try:
        raw_result = structured_llm.invoke(chat)
        decision = cast(BossDecision, raw_result)
        raw_action = decision.next_action
        reply_content = decision.assistant_reply
        product_query = decision.product_query
    except Exception as e:
        print(f"LLM Error in BOSS: {e}")
        raw_action = "END"
        reply_content = "I'm having a bit of trouble connecting. Let's try again in a moment."
        product_query = ""

    state["route"] = raw_action
    state["done"] = raw_action == "END"
    state["product_query"] = product_query  # ← passed to recommendation agent

    state.setdefault("messages", []).append(AIMessage(content=reply_content))

    return state