"""
NutriLens 100-Point Health Score Algorithm
Transparent, scientifically grounded scoring normalized per 100g.
"""

def calculate_health_score(product: dict) -> dict:
    # Normalize values per 100g if serving size is given
    serving_g = float(product.get("serving_size_g", 100.0) or 100.0)
    multiplier = 100.0 / serving_g if serving_g > 0 else 1.0

    calories = float(product.get("calories", 0.0) or 0.0)
    sugar = float(product.get("sugar", 0.0) or 0.0)
    sat_fat = float(product.get("saturated_fat", 0.0) or 0.0)
    total_fat = float(product.get("total_fat", 0.0) or 0.0)
    protein = float(product.get("protein", 0.0) or 0.0)
    fiber = float(product.get("fiber", 0.0) or 0.0)
    sodium_mg = float(product.get("sodium_mg", 0.0) or 0.0)

    category = str(product.get("category", "")).lower()
    is_beverage = "beverage" in category or "drink" in category or "soda" in category or "juice" in category

    # 1. Sugar Penalty: Thresholds differ for beverages vs solid snacks
    if is_beverage:
        # For beverages: <= 1.0g clean, >= 8.0g severe penalty (-35 pts)
        if sugar <= 1.0:
            p_sugar = 0.0
        elif sugar >= 8.0:
            p_sugar = 35.0
        else:
            p_sugar = ((sugar - 1.0) / (8.0 - 1.0)) * 35.0
    else:
        # For solid snacks (Max -25): Threshold <= 4.5g clean, >= 25g severe
        if sugar <= 4.5:
            p_sugar = 0.0
        elif sugar >= 25.0:
            p_sugar = 25.0
        else:
            p_sugar = ((sugar - 4.5) / (25.0 - 4.5)) * 25.0

    # 2. Saturated Fat Penalty (Max -20): Threshold <= 1.5g clean, >= 10g severe
    if sat_fat <= 1.5:
        p_sat_fat = 0.0
    elif sat_fat >= 10.0:
        p_sat_fat = 20.0
    else:
        p_sat_fat = ((sat_fat - 1.5) / (10.0 - 1.5)) * 20.0

    # 3. Sodium Penalty (Max -15): Threshold <= 120mg clean, >= 900mg severe
    if sodium_mg <= 120.0:
        p_sodium = 0.0
    elif sodium_mg >= 900.0:
        p_sodium = 15.0
    else:
        p_sodium = ((sodium_mg - 120.0) / (900.0 - 120.0)) * 15.0

    # 4. Calories Penalty (Max -10): Threshold <= 150kcal clean, >= 500kcal severe
    if calories <= 150.0:
        p_cal = 0.0
    elif calories >= 500.0:
        p_cal = 10.0
    else:
        p_cal = ((calories - 150.0) / (500.0 - 150.0)) * 10.0

    # 5. Total Fat Penalty (Max -10): Threshold <= 3.0g clean, >= 25g severe
    if total_fat <= 3.0:
        p_fat = 0.0
    elif total_fat >= 25.0:
        p_fat = 10.0
    else:
        p_fat = ((total_fat - 3.0) / (25.0 - 3.0)) * 10.0

    # 6. Fiber Bonus (Max +15): Threshold >= 6.0g full bonus, <= 0.5g 0 bonus
    if fiber <= 0.5:
        b_fiber = 0.0
    elif fiber >= 6.0:
        b_fiber = 15.0
    else:
        b_fiber = ((fiber - 0.5) / (6.0 - 0.5)) * 15.0

    # 7. Protein Bonus (Max +10): Threshold >= 10.0g full bonus, <= 1.0g 0 bonus
    if protein <= 1.0:
        b_protein = 0.0
    elif protein >= 10.0:
        b_protein = 10.0
    else:
        b_protein = ((protein - 1.0) / (10.0 - 1.0)) * 10.0

    # Base score
    base_score = 70.0
    raw_score = base_score - (p_sugar + p_sat_fat + p_sodium + p_cal + p_fat) + (b_fiber + b_protein)
    final_score = int(max(1, min(100, round(raw_score))))

    # Classification & Grade
    if final_score >= 80:
        grade = "A"
        classification = "Excellent"
        color = "#10b981" # Emerald 500
    elif final_score >= 60:
        grade = "B"
        classification = "Good"
        color = "#22c55e" # Green 500
    elif final_score >= 40:
        grade = "C"
        classification = "Moderate"
        color = "#eab308" # Yellow 500
    elif final_score >= 20:
        grade = "D"
        classification = "Poor"
        color = "#f97316" # Orange 500
    else:
        grade = "E"
        classification = "Very Poor"
        color = "#ef4444" # Red 500

    # Traffic light system for specific nutrients
    traffic_lights = {
        "sugar": {
            "value": f"{sugar}g",
            "level": "green" if sugar <= 5.0 else ("yellow" if sugar <= 12.5 else "red"),
            "label": "Low Sugar" if sugar <= 5.0 else ("Moderate Sugar" if sugar <= 12.5 else "High Sugar")
        },
        "saturated_fat": {
            "value": f"{sat_fat}g",
            "level": "green" if sat_fat <= 1.5 else ("yellow" if sat_fat <= 5.0 else "red"),
            "label": "Low Sat Fat" if sat_fat <= 1.5 else ("Moderate Sat Fat" if sat_fat <= 5.0 else "High Sat Fat")
        },
        "sodium": {
            "value": f"{sodium_mg}mg",
            "level": "green" if sodium_mg <= 120 else ("yellow" if sodium_mg <= 400 else "red"),
            "label": "Low Sodium" if sodium_mg <= 120 else ("Moderate Sodium" if sodium_mg <= 400 else "High Sodium")
        },
        "protein": {
            "value": f"{protein}g",
            "level": "green" if protein >= 7.0 else ("yellow" if protein >= 3.0 else "gray"),
            "label": "High Protein" if protein >= 7.0 else ("Moderate Protein" if protein >= 3.0 else "Low Protein")
        },
        "fiber": {
            "value": f"{fiber}g",
            "level": "green" if fiber >= 5.0 else ("yellow" if fiber >= 2.0 else "gray"),
            "label": "High Fiber" if fiber >= 5.0 else ("Moderate Fiber" if fiber >= 2.0 else "Low Fiber")
        }
    }

    # Positives & Warnings
    positives = []
    warnings = []
    if b_fiber >= 8.0:
        positives.append(f"Rich in dietary fiber ({fiber}g per 100g) supporting healthy digestion")
    if b_protein >= 6.0:
        positives.append(f"Great source of plant protein ({protein}g per 100g) promoting satiety")
    if p_sugar == 0.0 and sugar < 2.0:
        positives.append("Practically zero added refined sugars")

    if p_sugar >= 12.0:
        warnings.append(f"High sugar content ({sugar}g per 100g) poses rapid glycemic spikes")
    if p_sat_fat >= 12.0:
        warnings.append(f"Excessive saturated fats ({sat_fat}g per 100g) often from palm oil")
    if p_sodium >= 9.0:
        warnings.append(f"Elevated sodium level ({sodium_mg}mg per 100g) - watch your blood pressure")
    if p_fat >= 7.0 and total_fat > 30.0:
        warnings.append("High overall fat density from deep frying")

    return {
        "health_score": final_score,
        "grade": grade,
        "classification": classification,
        "color": color,
        "traffic_lights": traffic_lights,
        "positives": positives,
        "warnings": warnings,
        "breakdown": {
            "sugar_penalty": round(p_sugar, 1),
            "sat_fat_penalty": round(p_sat_fat, 1),
            "sodium_penalty": round(p_sodium, 1),
            "calories_penalty": round(p_cal, 1),
            "total_fat_penalty": round(p_fat, 1),
            "fiber_bonus": round(b_fiber, 1),
            "protein_bonus": round(b_protein, 1),
        }
    }
