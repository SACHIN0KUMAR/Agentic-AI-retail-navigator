# api/store_api.py

from typing import List, Dict

MOCK_STORES = [
    {
        "id": "store_1",
        "name": "Impactify Mart - Central",
        "pincode": "110001",
        "supports_pickup": True,
        "supports_delivery": True,
    },
    {
        "id": "store_2",
        "name": "Impactify Mart - West",
        "pincode": "110008",
        "supports_pickup": True,
        "supports_delivery": False,
    },
]


def find_nearby_store(pincode: str) -> Dict:
    """
    Very naive: pick first store whose pincode matches or is 'nearby'.
    """
    for store in MOCK_STORES:
        if store["pincode"] == pincode:
            return store

    # fallback: return first store as 'closest'
    return MOCK_STORES[0]


def get_store_by_id(store_id: str) -> Dict:
    for store in MOCK_STORES:
        if store["id"] == store_id:
            return store
    return MOCK_STORES[0]
