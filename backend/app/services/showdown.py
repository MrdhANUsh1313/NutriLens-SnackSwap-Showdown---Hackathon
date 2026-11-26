"""
SnackSwap Showdown Service
Evaluates two food products in a head-to-head nutritional battle.
"""

from .scoring import calculate_health_score

def compare_snacks(snack_a: dict, snack_b: dict) -> dict:
    if "health_score" not in snack_a:
        snack_a.update(calculate_health_score(snack_a))
    if "health_score" not in snack_b:
        snack_b.update(calculate_health_score(snack_b))

    score_a = snack_a["health_score"]
    score_b = snack_b["health_score"]

    diff_score = abs(score_a - score_b)

    # Determine Winner
    if score_a > score_b:
        winner = snack_a
        loser = snack_b
        winner_id = snack_a.get("id")
        winner_tag = "A"
    elif score_b > score_a:
        winner = snack_b
        loser = snack_a
        winner_id = snack_b.get("id")
        winner_tag = "B"
    else:
        # Tie-breaker on lower sugar + sodium
        harm_a = float(snack_a.get("sugar", 0)) * 2 + float(snack_a.get("sodium_mg", 0)) / 100
        harm_b = float(snack_b.get("sugar", 0)) * 2 + float(snack_b.get("sodium_mg", 0)) / 100
        if harm_a <= harm_b:
            winner = snack_a
            loser = snack_b
            winner_id = snack_a.get("id")
            winner_tag = "A"
        else:
            winner = snack_b
            loser = snack_a
            winner_id = snack_b.get("id")
            winner_tag = "B"

    # Compute metric deltas (Positive means Winner has better attribute)
    cal_delta = loser.get("calories", 0) - winner.get("calories", 0)
    sugar_delta = loser.get("sugar", 0) - winner.get("sugar", 0)
    fat_delta = loser.get("total_fat", 0) - winner.get("total_fat", 0)
    sat_fat_delta = loser.get("saturated_fat", 0) - winner.get("saturated_fat", 0)
    prot_delta = winner.get("protein", 0) - loser.get("protein", 0)
    fib_delta = winner.get("fiber", 0) - loser.get("fiber", 0)
    sod_delta = loser.get("sodium_mg", 0) - winner.get("sodium_mg", 0)

    # Human-readable rationale bullets
    reasons = []
    if sugar_delta > 3:
        reasons.append(f"Contains {round(sugar_delta, 1)}g less sugar ({round((sugar_delta / (loser.get('sugar', 1) or 1)) * 100)}% sugar reduction)")
    if prot_delta > 1.5:
        reasons.append(f"Provides {round(prot_delta, 1)}g more muscle-building protein")
    if fib_delta > 1.5:
        reasons.append(f"Packs {round(fib_delta, 1)}g more dietary fiber for improved gut health and fullness")
    if sat_fat_delta > 2:
        reasons.append(f"Has {round(sat_fat_delta, 1)}g less saturated fat (drastically cleaner oil profile)")
    if sod_delta > 150:
        reasons.append(f"Slashes sodium by {round(sod_delta)}mg (much safer for heart and hydration)")
    if cal_delta > 50:
        reasons.append(f"Saves {round(cal_delta)} calories per 100g")

    if not reasons:
        reasons.append(f"Higher overall nutrient density and fewer synthetic additives")

    # Overall percentage advantage
    if loser.get("health_score", 1) > 0:
        advantage_pct = round(((winner["health_score"] - loser["health_score"]) / max(1, loser["health_score"])) * 100)
    else:
        advantage_pct = 100

    return {
        "snack_a": snack_a,
        "snack_b": snack_b,
        "winner_tag": winner_tag,
        "winner_id": winner_id,
        "winner_name": winner.get("name"),
        "winner_score": winner.get("health_score"),
        "loser_score": loser.get("health_score"),
        "score_diff": diff_score,
        "advantage_pct": max(5, advantage_pct),
        "reasons": reasons,
        "comparison_metrics": [
            {"nutrient": "Calories", "a": f"{snack_a.get('calories')} kcal", "b": f"{snack_b.get('calories')} kcal", "winner": "A" if snack_a.get('calories', 0) < snack_b.get('calories', 0) else "B"},
            {"nutrient": "Protein", "a": f"{snack_a.get('protein')}g", "b": f"{snack_b.get('protein')}g", "winner": "A" if snack_a.get('protein', 0) > snack_b.get('protein', 0) else "B"},
            {"nutrient": "Dietary Fiber", "a": f"{snack_a.get('fiber')}g", "b": f"{snack_b.get('fiber')}g", "winner": "A" if snack_a.get('fiber', 0) > snack_b.get('fiber', 0) else "B"},
            {"nutrient": "Total Sugar", "a": f"{snack_a.get('sugar')}g", "b": f"{snack_b.get('sugar')}g", "winner": "A" if snack_a.get('sugar', 0) < snack_b.get('sugar', 0) else "B"},
            {"nutrient": "Saturated Fat", "a": f"{snack_a.get('saturated_fat')}g", "b": f"{snack_b.get('saturated_fat')}g", "winner": "A" if snack_a.get('saturated_fat', 0) < snack_b.get('saturated_fat', 0) else "B"},
            {"nutrient": "Sodium", "a": f"{snack_a.get('sodium_mg')}mg", "b": f"{snack_b.get('sodium_mg')}mg", "winner": "A" if snack_a.get('sodium_mg', 0) < snack_b.get('sodium_mg', 0) else "B"},
        ]
    }
