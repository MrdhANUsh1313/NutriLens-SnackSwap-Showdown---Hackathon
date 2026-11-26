"""
NutriLens Zero-Dependency Standalone API Server
Runs directly on Python standard library (http.server) with zero external pip dependencies!
Supports full CORS and all hackathon API routes.
"""

import sys
import os
import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

# Add app parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.food_facts import LOCAL_PRODUCTS, get_product_by_barcode, search_products
from app.services.scoring import calculate_health_score
from app.services.showdown import compare_snacks
from app.services.recommendations import get_recommendations_for_product
from app.services.ai_coach import ask_nutrition_ai

# In-memory user gamification state for demo
USER_STATE = {
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

class NutriLensRequestHandler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def _send_json(self, status_code: int, data: dict or list):
        payload = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status_code)
        self._send_cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path == "/api/health" or path == "/":
            self._send_json(200, {
                "status": "healthy",
                "app": "NutriLens: SnackSwap Showdown API",
                "version": "1.0.0",
                "products_count": len(LOCAL_PRODUCTS)
            })

        elif path == "/api/products":
            self._send_json(200, LOCAL_PRODUCTS)

        elif path.startswith("/api/products/"):
            barcode = path.split("/api/products/")[1].strip()
            product = get_product_by_barcode(barcode)
            if product:
                self._send_json(200, product)
            else:
                self._send_json(404, {"error": f"Product with barcode '{barcode}' not found"})

        elif path == "/api/search":
            q = query.get("q", [""])[0]
            matches = search_products(q)
            self._send_json(200, matches)

        elif path.startswith("/api/recommendations/"):
            barcode = path.split("/api/recommendations/")[1].strip()
            product = get_product_by_barcode(barcode)
            if not product:
                self._send_json(404, {"error": "Target snack not found"})
                return
            recs = get_recommendations_for_product(product)
            self._send_json(200, {
                "target_snack": product,
                "recommendations": recs
            })

        elif path == "/api/gamification":
            self._send_json(200, USER_STATE)

        elif path == "/api/leaderboard":
            leaderboard = [
                {"rank": 1, "name": "Priya Sharma", "points": 380, "streak": 12, "badge": "Nutrition Guru"},
                {"rank": 2, "name": "Rahul Verma", "points": 290, "streak": 8, "badge": "Fiber Fanatic"},
                {"rank": 3, "name": USER_STATE["name"], "points": USER_STATE["points"], "streak": USER_STATE["streak_days"], "badge": "Snack Swapper"},
                {"rank": 4, "name": "Ananya Sen", "points": 120, "streak": 3, "badge": "Rookie"},
                {"rank": 5, "name": "Karan Patel", "points": 95, "streak": 2, "badge": "Explorer"}
            ]
            self._send_json(200, leaderboard)

        else:
            self._send_json(404, {"error": f"Endpoint '{path}' not found"})

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else "{}"
        try:
            payload = json.loads(body)
        except Exception:
            payload = {}

        if path == "/api/score":
            result = calculate_health_score(payload)
            self._send_json(200, result)

        elif path == "/api/showdown":
            id_a = payload.get("snack_a_id")
            id_b = payload.get("snack_b_id")

            snack_a = payload.get("snack_a") or get_product_by_barcode(id_a)
            snack_b = payload.get("snack_b") or get_product_by_barcode(id_b)

            if not snack_a or not snack_b:
                self._send_json(400, {"error": "Both snack_a and snack_b must be provided"})
                return

            showdown_result = compare_snacks(snack_a, snack_b)
            self._send_json(200, showdown_result)

        elif path == "/api/gamification/swap":
            # Reward user for making a healthy swap
            pts = int(payload.get("points", 20))
            USER_STATE["points"] += pts
            USER_STATE["swaps_completed"] += 1
            if USER_STATE["points"] >= 200:
                USER_STATE["level"] = 3

            swap_record = {
                "original": payload.get("original_name", "Unhealthy Snack"),
                "swapped_to": payload.get("swap_name", "Healthy Snack"),
                "score_gain": payload.get("score_gain", 40),
                "points_earned": pts
            }
            USER_STATE["history"].insert(0, swap_record)

            self._send_json(200, {
                "success": True,
                "earned_points": pts,
                "current_points": USER_STATE["points"],
                "level": USER_STATE["level"],
                "swaps_completed": USER_STATE["swaps_completed"],
                "message": f"Awesome choice! +{pts} XP added to your NutriLens profile!"
            })

        elif path == "/api/chat":
            question = payload.get("question", "")
            context = payload.get("context_product")
            answer = ask_nutrition_ai(question, context)
            self._send_json(200, answer)

        else:
            self._send_json(404, {"error": f"Endpoint '{path}' not found"})

def run_server(port=8000):
    server_address = ("", port)
    httpd = HTTPServer(server_address, NutriLensRequestHandler)
    print(f"🚀 NutriLens Standalone Backend running on http://127.0.0.1:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    port = 8000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    run_server(port)
