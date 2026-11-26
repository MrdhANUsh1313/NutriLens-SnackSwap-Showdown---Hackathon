"""
NutriLens AI Nutrition Assistant & Label Explainer
Integrates Google Gemini API when configured, with expert nutritional fallback rules.
"""

import os
import json
import urllib.request
import urllib.error

FALLBACK_KNOWLEDGE_BASE = {
    "palm oil": "Palmolein / Palm Oil is high in saturated palmitic acid (~50%), which raises LDL (bad) cholesterol and triggers arterial inflammation. Snack manufacturers prefer it because it is cheap and shelf-stable, but choosing snacks roasted in olive oil, mustard oil, or dry-roasted is dramatically healthier.",
    "maltodextrin": "Maltodextrin is a highly processed polysaccharide often added as a filler or texture enhancer. It has a glycemic index (GI) of 105–110—even higher than table sugar! This causes rapid insulin spikes, contributing to sugar crashes and visceral fat accumulation.",
    "makhana": "Foxnuts (Makhana) are popped lotus seeds. They are naturally gluten-free, low in calories (~350 kcal/100g), high in magnesium, potassium, and phosphorus, with zero trans-fat. When lightly roasted with rock salt, they are an ideal replacement for fried potato chips.",
    "sodium": "The WHO recommends a daily sodium limit under 2,000 mg (~1 tsp salt). A single 35g bag of commercial namkeen or chips can contain 40% of this entire daily quota! Excessive sodium causes water retention and long-term hypertension.",
    "sugar": "Hidden sugars appear under 50+ aliases: high-fructose corn syrup, dextrose, invert syrup, malt extract, and sucrose. Aim for snacks with under 5g total sugar per 100g.",
    "diabetic": "For diabetic-friendly snacking, focus on low-glycemic, high-fiber options: roasted chana (Bengal gram), plain makhana, sprouted moong chaat, walnuts, and cucumbers with chaat masala.",
    "protein": "High-protein snacks like roasted chickpeas, edamame, paneer cubes, or sprouted moong stimulate peptide YY and GLP-1 hormones, keeping hunger suppressed for 3–4 hours."
}

def ask_nutrition_ai(question: str, context_product: dict = None) -> dict:
    q_lower = question.lower()
    gemini_key = os.environ.get("GEMINI_API_KEY", "")

    # Try Gemini API if key is present
    if gemini_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
            sys_context = "You are NutriLens AI, an encouraging, scientifically rigorous nutrition coach. Answer in 2-3 concise paragraphs with bullet points. Explain food labels, ingredients, and healthy swaps."
            if context_product:
                sys_context += f" Current snack in view: {context_product.get('name')} (Score: {context_product.get('health_score')}/100, Sugar: {context_product.get('sugar')}g, Sodium: {context_product.get('sodium_mg')}mg)."
            
            payload = {
                "contents": [{
                    "parts": [{"text": f"{sys_context}\n\nUser Question: {question}"}]
                }]
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                    return {"response": text, "source": "gemini-1.5-flash"}
        except Exception:
            pass

    # Contextual Smart Fallback
    matched_responses = []
    for keyword, response in FALLBACK_KNOWLEDGE_BASE.items():
        if keyword in q_lower:
            matched_responses.append(response)

    if matched_responses:
        return {
            "response": " ".join(matched_responses),
            "source": "nutrilens-expert-engine"
        }

    # Default insightful answer
    if context_product:
        p_name = context_product.get("name", "this snack")
        score = context_product.get("health_score", 50)
        return {
            "response": f"Regarding **{p_name}** (Health Score: {score}/100):\n\n"
                        f"• **Nutritional Balance**: Contains {context_product.get('sugar', 0)}g sugar and {context_product.get('sodium_mg', 0)}mg sodium per 100g.\n"
                        f"• **Coach Recommendation**: {'This is a nutritious choice for sustained energy!' if score >= 70 else 'Consider swapping this with a fiber-rich alternative like roasted makhana or chana to avoid empty calories.'}\n"
                        f"• **Label Tip**: Always check the first 3 ingredients on the label—they make up the bulk of the product!",
            "source": "nutrilens-expert-engine"
        }

    return {
        "response": "Here is a NutriLens Golden Rule: Look for snacks with **Fiber > 5g**, **Protein > 6g**, and **Sugar < 5g** per 100g. Whenever you're craving crunch, choose roasted legumes or nuts over deep-fried flour crisps!",
        "source": "nutrilens-expert-engine"
    }
