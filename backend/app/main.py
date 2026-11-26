"""
NutriLens FastAPI Application Entry Point
High-performance asynchronous REST API for Food Scanning, 100-Point NutriScore,
SnackSwap Showdown, Recommendations, and Gamification.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from app.services.food_facts import LOCAL_PRODUCTS, get_product_by_barcode, search_products
from app.services.scoring import calculate_health_score
from app.services.showdown import compare_snacks
from app.services.recommendations import get_recommendations_for_product
from app.services.ai_coach import ask_nutrition_ai

app = FastAPI(
    title="NutriLens: SnackSwap Showdown API",
    description="AI-powered smart food analysis, 100-point health score, and healthy snack showdown arena",
    version="1.0.0"
)

# Enable CORS for React Frontend and Mobile Webviews
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class NutritionInput(BaseModel):
    name: Optional[str] = "Custom Snack"
    calories: float = 0.0
    sugar: float = 0.0
    saturated_fat: float = 0.0
    total_fat: float = 0.0
    protein: float = 0.0
    fiber: float = 0.0
    sodium_mg: float = 0.0
    serving_size_g: float = 100.0

class ShowdownRequest(BaseModel):
    snack_a_id: Optional[str] = None
    snack_b_id: Optional[str] = None
    snack_a: Optional[Dict[str, Any]] = None
    snack_b: Optional[Dict[str, Any]] = None

class SwapRewardRequest(BaseModel):
    original_name: str
    swap_name: str
    score_gain: int
    points: int = 20

class ChatRequest(BaseModel):
    question: str
    context_product: Optional[Dict[str, Any]] = None

# In-memory gamification state
user_state = {
    "user_id": "demo_user_1",
    "name": "Alex Hunter",
    "points": 140,
    "level": 2,
    "streak_days": 4,
    "swaps_completed": 7,
    "scans_count": 12,
    "badges": [
        {"id": "first_scan", "name": "First Scan", "icon": "🔍", "unlocked": True, "desc": "Scanned your first packaged food"},
        {"id": "first_swap", "name": "Snack Swapper", "icon": "🥑", "unlocked": True, "desc": "Completed your first healthy snack swap"},
        {"id": "sodium_slasher", "name": "Sodium Slasher", "icon": "🧂", "unlocked": True, "desc": "Swapped away high-sodium chips"},
        {"id": "sugar_hunter", "name": "Sugar Slayer", "icon": "🍬", "unlocked": False, "desc": "Replace 3 sugary snacks in a row"},
        {"id": "week_streak", "name": "7-Day Warrior", "icon": "🔥", "unlocked": False, "desc": "Maintain a 7-day healthy choice streak"}
    ],
    "history": []
}

@app.get("/")
@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app": "NutriLens API",
        "version": "1.0.0",
        "total_catalog_products": len(LOCAL_PRODUCTS)
    }

@app.get("/api/products")
def list_products():
    return LOCAL_PRODUCTS

@app.get("/api/products/{barcode}")
def get_product(barcode: str):
    product = get_product_by_barcode(barcode)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.get("/api/search")
def search(q: str = Query("", description="Search by snack name, brand, or category")):
    return search_products(q)

@app.post("/api/score")
def score_nutrition(payload: NutritionInput):
    return calculate_health_score(payload.model_dump())

@app.post("/api/showdown")
def showdown(req: ShowdownRequest):
    snack_a = req.snack_a or (get_product_by_barcode(req.snack_a_id) if req.snack_a_id else None)
    snack_b = req.snack_b or (get_product_by_barcode(req.snack_b_id) if req.snack_b_id else None)

    if not snack_a or not snack_b:
        raise HTTPException(status_code=400, detail="Both snacks are required for a Showdown")

    return compare_snacks(snack_a, snack_b)

@app.get("/api/recommendations/{barcode}")
def recommendations(barcode: str):
    product = get_product_by_barcode(barcode)
    if not product:
        raise HTTPException(status_code=404, detail="Target product not found")
    recs = get_recommendations_for_product(product)
    return {"target_snack": product, "recommendations": recs}

@app.get("/api/gamification")
def get_gamification():
    return user_state

@app.post("/api/gamification/swap")
def reward_swap(req: SwapRewardRequest):
    user_state["points"] += req.points
    user_state["swaps_completed"] += 1
    if user_state["points"] >= 200:
        user_state["level"] = 3

    user_state["history"].insert(0, {
        "original": req.original_name,
        "swapped_to": req.swap_name,
        "score_gain": req.score_gain,
        "points_earned": req.points
    })

    return {
        "success": True,
        "earned_points": req.points,
        "current_points": user_state["points"],
        "level": user_state["level"],
        "swaps_completed": user_state["swaps_completed"],
        "message": f"Congratulations! +{req.points} XP earned for choosing healthier food!"
    }

@app.get("/api/leaderboard")
def get_leaderboard():
    return [
        {"rank": 1, "name": "Priya Sharma", "points": 380, "streak": 12, "badge": "Nutrition Guru"},
        {"rank": 2, "name": "Rahul Verma", "points": 290, "streak": 8, "badge": "Fiber Fanatic"},
        {"rank": 3, "name": user_state["name"], "points": user_state["points"], "streak": user_state["streak_days"], "badge": "Snack Swapper"},
        {"rank": 4, "name": "Ananya Sen", "points": 120, "streak": 3, "badge": "Rookie"},
        {"rank": 5, "name": "Karan Patel", "points": 95, "streak": 2, "badge": "Explorer"}
    ]

@app.post("/api/chat")
def chat_assistant(req: ChatRequest):
    return ask_nutrition_ai(req.question, req.context_product)
