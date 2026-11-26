"""
Healthy Snack Recommendation Engine
Finds culturally relevant, budget-friendly and significantly healthier alternatives.
"""

from .food_facts import LOCAL_PRODUCTS
from .scoring import calculate_health_score

CURATED_SWAP_MAPPINGS = {
    "Chips & Crisps": ["8904256701123", "8906012345678", "8909876543210"],
    "Namkeen & Savouries": ["8906012345678", "8904256701123", "8909876543210"],
    "Biscuits & Cookies": ["8908009988776", "8904321908765"],
    "Beverages": ["8901765112233"],
    "Confectionery": ["8904321908765", "8908009988776"],
    "Instant Noodles": ["8909876543210", "8906012345678"],
}

def get_recommendations_for_product(product: dict, max_results: int = 3) -> list:
    if "health_score" not in product:
        product.update(calculate_health_score(product))

    target_category = product.get("category", "")
    target_score = product.get("health_score", 50)
    target_price = product.get("price_inr", 30)

    # Check curated mappings first
    curated_ids = CURATED_SWAP_MAPPINGS.get(target_category, [])
    candidates = []

    for p in LOCAL_PRODUCTS:
        # Don't recommend the same product
        if p.get("id") == product.get("id"):
            continue

        # Must have a noticeably higher health score (+15 pts minimum)
        if p.get("health_score", 0) > target_score:
            candidates.append(p)

    # Sort candidates by:
    # 1. Is in curated mappings for category
    # 2. Highest health score
    # 3. Budget proximity (within 1.5x price)
    def rank_key(item):
        is_curated = 1 if item.get("id") in curated_ids else 0
        score_gain = item.get("health_score", 0) - target_score
        price_diff = abs(item.get("price_inr", 30) - target_price)
        return (is_curated, score_gain, -price_diff)

    candidates.sort(key=rank_key, reverse=True)
    results = candidates[:max_results]

    # Add swap highlight metadata
    enhanced = []
    for alt in results:
        alt_copy = dict(alt)
        alt_copy["score_gain"] = alt.get("health_score", 0) - target_score
        alt_copy["swap_headline"] = f"+{alt_copy['score_gain']} Score Boost"
        alt_copy["benefits"] = []

        if alt.get("protein", 0) > product.get("protein", 0):
            alt_copy["benefits"].append(f"{round(alt.get('protein', 0) - product.get('protein', 0), 1)}g more protein")
        if alt.get("sugar", 0) < product.get("sugar", 0):
            alt_copy["benefits"].append(f"{round(product.get('sugar', 0) - alt.get('sugar', 0), 1)}g less sugar")
        if alt.get("sodium_mg", 0) < product.get("sodium_mg", 0):
            alt_copy["benefits"].append(f"{round(product.get('sodium_mg', 0) - alt.get('sodium_mg', 0))}mg less sodium")
        if alt.get("fiber", 0) > product.get("fiber", 0):
            alt_copy["benefits"].append(f"{round(alt.get('fiber', 0) - product.get('fiber', 0), 1)}g more dietary fiber")

        enhanced.append(alt_copy)

    return enhanced
