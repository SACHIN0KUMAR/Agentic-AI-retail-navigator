# api/stock_api.py

from typing import Dict, List, Optional

MOCK_INVENTORY = {
    "store_1": {
        "milk 1L": {"sku": "MILK1L", "price": 60, "qty": 10},
        "bread": {"sku": "BREAD01", "price": 40, "qty": 0},
        "eggs 6pc": {"sku": "EGG6", "price": 55, "qty": 25},
        "detergent small": {"sku": "DET_SMALL", "price": 90, "qty": 5},
    },
    "store_2": {
        "milk 1L": {"sku": "MILK1L", "price": 58, "qty": 0},
        "bread": {"sku": "BREAD01", "price": 42, "qty": 15},
        "eggs 6pc": {"sku": "EGG6", "price": 57, "qty": 5},
    },
}


def search_product(store_id: str, query: str) -> List[Dict]:
    """
    Smart search: match any word in the query against product names.
    """
    store = MOCK_INVENTORY.get(store_id, {})
    query_words = query.lower().split()  # ["show", "me", "recommendations"] or ["milk"]
    results = []
    for name, item in store.items():
        name_lower = name.lower()
        # Match if ANY word in the query appears in the product name
        if any(word in name_lower for word in query_words):
            results.append({
                "name": name,
                "sku": item["sku"],
                "price": item["price"],
                "available_qty": item["qty"],
            })
    return results


def check_stock(store_id: str, sku: str, qty: int) -> Dict:
    """
    Check if requested quantity is available in the given store.
    """
    store = MOCK_INVENTORY.get(store_id, {})
    for name, item in store.items():
        if item["sku"] == sku:
            available = item["qty"]
            return {
                "sku": sku,
                "name": name,
                "requested_qty": qty,
                "available_qty": available,
                "in_stock": available >= qty,
            }
    return {
        "sku": sku,
        "name": None,
        "requested_qty": qty,
        "available_qty": 0,
        "in_stock": False,
    }


def reserve_stock(store_id: str, sku: str, qty: int) -> bool:
    """
    Deduct stock (simple optimistic reserve).
    """
    store = MOCK_INVENTORY.get(store_id, {})
    for name, item in store.items():
        if item["sku"] == sku and item["qty"] >= qty:
            item["qty"] -= qty
            return True
    return False

