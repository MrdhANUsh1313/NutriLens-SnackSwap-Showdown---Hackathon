"""
Open Food Facts API Service & Local Product Catalog Fallback.
Provides offline resilience for hackathons while querying live API when reachable.
"""

import json
import os
import urllib.request
import urllib.error
from .scoring import calculate_health_score

SEED_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "seed_snacks.json")
if not os.path.exists(SEED_DATA_PATH):
    # Try alternate location
    alt_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "seed_snacks.json")
    if os.path.exists(alt_path):
        SEED_DATA_PATH = alt_path

def load_local_products() -> list:
    if os.path.exists(SEED_DATA_PATH):
        with open(SEED_DATA_PATH, "r", encoding="utf-8") as f:
            products = json.load(f)
            # Pre-compute scoring for each product
            for p in products:
                scoring = calculate_health_score(p)
                p.update(scoring)
            return products
    return []

LOCAL_PRODUCTS = load_local_products()

def get_product_by_barcode(barcode: str) -> dict:
    # 1. First check local catalog (instant response)
    for p in LOCAL_PRODUCTS:
        if str(p.get("barcode")) == str(barcode) or str(p.get("id")) == str(barcode):
            return p

    # 2. Try fetching from Open Food Facts API
    api_url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
    req = urllib.request.Request(
        api_url,
        headers={"User-Agent": "NutriLens-Hackathon-App/1.0 (hackathon@nutrilens.dev)"}
    )
    try:
        with urllib.request.urlopen(req, timeout=4.0) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                if data.get("status") == 1 and "product" in data:
                    raw = data["product"]
                    nutriments = raw.get("nutriments", {})

                    # Extract sodium in mg
                    salt_g = nutriments.get("salt_100g", nutriments.get("salt", 0.0))
                    sodium_mg = nutriments.get("sodium_100g", 0.0)
                    if sodium_mg:
                        sodium_mg = float(sodium_mg) * 1000.0
                    elif salt_g:
                        sodium_mg = float(salt_g) * 400.0
                    else:
                        sodium_mg = 0.0

                    product = {
                        "id": str(barcode),
                        "barcode": str(barcode),
                        "name": raw.get("product_name", "Unknown Food Product"),
                        "brand": raw.get("brands", "Generic Brand"),
                        "category": raw.get("categories", "Packaged Food").split(",")[0],
                        "serving_size_g": 100.0,
                        "calories": float(nutriments.get("energy-kcal_100g", nutriments.get("energy-kcal", 0.0)) or 0.0),
                        "sugar": float(nutriments.get("sugars_100g", nutriments.get("sugars", 0.0)) or 0.0),
                        "saturated_fat": float(nutriments.get("saturated-fat_100g", nutriments.get("saturated-fat", 0.0)) or 0.0),
                        "total_fat": float(nutriments.get("fat_100g", nutriments.get("fat", 0.0)) or 0.0),
                        "protein": float(nutriments.get("proteins_100g", nutriments.get("proteins", 0.0)) or 0.0),
                        "fiber": float(nutriments.get("fiber_100g", nutriments.get("fiber", 0.0)) or 0.0),
                        "sodium_mg": round(sodium_mg, 1),
                        "ingredients": raw.get("ingredients_text", "Ingredients not specified on packaging"),
                        "price_inr": 25,
                        "image_url": raw.get("image_front_url", "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=600&auto=format&fit=crop&q=80")
                    }
                    scoring = calculate_health_score(product)
                    product.update(scoring)
                    return product
    except Exception:
        pass

    # If barcode not found in local or remote, return nearest local or dummy match
    return None

def search_products(query: str) -> list:
    query = query.lower().strip()
    matches = [
        p for p in LOCAL_PRODUCTS
        if query in p.get("name", "").lower() or query in p.get("brand", "").lower() or query in p.get("category", "").lower()
    ]
    return matches
