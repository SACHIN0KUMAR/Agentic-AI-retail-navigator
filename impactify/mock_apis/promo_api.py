# api/promo_api.py

from typing import Dict, List


MOCK_PROMOS = [
    {
        "id": "PROMO_MILK_BREAD",
        "description": "Buy Milk 1L + Bread and get 10% off on combo",
        "required_skus": ["MILK1L", "BREAD01"],
        "discount_pct": 10,
    },
    {
        "id": "PROMO_DET_EGG",
        "description": "Detergent small + Eggs 6pc combo save ₹20",
        "required_skus": ["DET_SMALL", "EGG6"],
        "flat_discount": 20,
    },
]


def get_applicable_promos(cart_items: List[Dict]) -> List[Dict]:
    """
    Given a cart (list of items with sku, price, qty), return applicable promos.
    """
    skus_in_cart = {item["sku"] for item in cart_items}
    applicable = []

    for promo in MOCK_PROMOS:
        required = set(promo["required_skus"])
        if required.issubset(skus_in_cart):
            applicable.append(promo)

    return applicable


def apply_promos(cart_items: List[Dict]) -> Dict:
    """
    Calculate total price and discounted price, along with which promos applied.
    """
    base_total = sum(item["price"] * item["qty"] for item in cart_items)
    promos = get_applicable_promos(cart_items)
    discount_total = 0

    for promo in promos:
        if "discount_pct" in promo:
            # Percentage discount on the items involved
            involved_items = [
                item for item in cart_items if item["sku"] in promo["required_skus"]
            ]
            sub_total = sum(i["price"] * i["qty"] for i in involved_items)
            discount_total += sub_total * promo["discount_pct"] / 100.0
        elif "flat_discount" in promo:
            discount_total += promo["flat_discount"]

    final_total = max(base_total - discount_total, 0)
    return {
        "base_total": base_total,
        "discount_total": round(discount_total, 2),
        "final_total": round(final_total, 2),
        "applied_promos": promos,
    }
