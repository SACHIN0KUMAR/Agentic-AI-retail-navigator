# graph/stock_agent.py

from typing import Dict, Any, List
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from impactify.mock_apis.stock_api import check_stock, reserve_stock, search_product
from impactify.config import get_llm


SYSTEM_PROMPT = """
You are the STOCK AGENT for Impactify Retail Navigator.
Your job:
- Check stock availability for all items in the cart.
- If something is out of stock or partially available, explain it politely.
- Suggest alternatives or quantity adjustments.
Be concise and friendly.
"""


def parse_cart_from_message(user_message: str, store_id: str) -> List[Dict[str, Any]]:
    """
    Parses 'add milk 1L 2' or 'add milk 1L' into a cart item.
    Searches mock inventory to find the matching SKU.
    """
    words = user_message.lower().strip().split()

    # Remove 'add' from the start
    if words and words[0] == "add":
        words = words[1:]

    if not words:
        return []

    # Try to extract quantity from the last word
    qty = 1
    if words[-1].isdigit():
        qty = int(words[-1])
        words = words[:-1]

    # Remaining words form the product query
    product_query = " ".join(words)

    # Search inventory for matching product
    results = search_product(store_id, product_query)
    if not results:
        return []

    # Take the first match
    product = results[0]
    return [{
        "name": product["name"],
        "sku": product["sku"],
        "qty": qty,
        "price": product["price"],
    }]


def stock_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parses cart from user message if cart is empty, then checks stock.
    Always returns state.
    """
    llm = get_llm()
    store_id = state.get("store", {}).get("id", "store_1")
    cart: List[Dict[str, Any]] = state.get("cart", [])
    user_last = state.get("last_user_message", "")

    # ← Parse cart from user message if cart is empty
    if not cart and user_last:
        cart = parse_cart_from_message(user_last, store_id)
        state["cart"] = cart

    # If still empty after parsing
    if not cart:
        state.setdefault("messages", []).append(
            AIMessage(content="I couldn't find that product. Could you try: \"add milk 1L 2\"?")
        )
        return state

    stock_report = []
    oos_items = []

    # --- CHECK STOCK ---
    for item in cart:
        res = check_stock(store_id, item["sku"], item["qty"])
        stock_report.append(res)
        if not res["in_stock"]:
            oos_items.append(res)

    # --- BUILD MESSAGE FOR USER ---
    if not oos_items:
        cart_summary = ", ".join([f"{i['qty']}x {i['name']} (₹{i['price']})" for i in cart])
        assistant_text = f"✅ All items are in stock! Added to cart: {cart_summary}. Say 'checkout' to pay or keep shopping!"
    else:
        # Fix quantity for partially available items
        for res in oos_items:
            for item in cart:
                if item["sku"] == res["sku"]:
                    item["qty"] = res["available_qty"]

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"The following items are out of stock or limited: {oos_items}. "
                                 f"Cart after adjustment: {cart}. Provide a polite explanation.")
        ]
        resp = llm.invoke(messages)
        assistant_text = resp.content if hasattr(resp, "content") else str(resp)

    # --- RESERVE AVAILABLE STOCK ---
    for item in cart:
        if item["qty"] > 0:
            reserve_stock(store_id, item["sku"], item["qty"])

    # --- UPDATE STATE ---
    state["cart"] = cart
    state["stock_report"] = stock_report
    state.setdefault("messages", []).append(AIMessage(content=assistant_text))

    return state