/**
 * NutriLens API Service Client
 * Connects to Python FastAPI / Standalone backend with automatic offline mock fallback.
 */

const API_BASE = 'http://localhost:8000/api';

// Fallback embedded dataset for 100% offline hackathon resilience
export const MOCK_PRODUCTS = [
  {
    id: "8901491101837",
    barcode: "8901491101837",
    name: "Lay's India's Magic Masala Potato Chips",
    brand: "Lay's",
    category: "Chips & Crisps",
    serving_size_g: 30.0,
    calories: 544.0,
    sugar: 3.8,
    saturated_fat: 15.0,
    total_fat: 33.7,
    protein: 7.0,
    fiber: 3.2,
    sodium_mg: 790.0,
    health_score: 31,
    grade: "D",
    classification: "Poor",
    color: "#f97316",
    price_inr: 20,
    image_url: "https://images.unsplash.com/photo-1566478989037-eec170784d0b?w=600&auto=format&fit=crop&q=80",
    ingredients: "Potato, Edible Vegetable Oil (Palmolein), Seasoning (Spices, Salt, Maltodextrin, Sugar)"
  },
  {
    id: "8904256701123",
    barcode: "8904256701123",
    name: "Organic Roasted Peri-Peri Foxnuts (Makhana)",
    brand: "Farmley",
    category: "Healthy Puffs",
    serving_size_g: 30.0,
    calories: 350.0,
    sugar: 0.8,
    saturated_fat: 1.2,
    total_fat: 4.5,
    protein: 9.7,
    fiber: 7.6,
    sodium_mg: 180.0,
    health_score: 87,
    grade: "A",
    classification: "Excellent",
    color: "#10b981",
    price_inr: 35,
    image_url: "https://images.unsplash.com/photo-1621996346565-e3d5d6281699?w=600&auto=format&fit=crop&q=80",
    ingredients: "Foxnuts (Makhana 82%), Cold-Pressed Olive Oil, Peri Peri Spices, Himalayan Pink Salt"
  },
  {
    id: "8904004400115",
    barcode: "8904004400115",
    name: "Haldiram's Aloo Bhujia",
    brand: "Haldiram's",
    category: "Namkeen & Savouries",
    serving_size_g: 35.0,
    calories: 582.0,
    sugar: 2.1,
    saturated_fat: 17.5,
    total_fat: 42.0,
    protein: 9.2,
    fiber: 3.0,
    sodium_mg: 860.0,
    health_score: 32,
    grade: "D",
    classification: "Poor",
    color: "#f97316",
    price_inr: 20,
    image_url: "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=600&auto=format&fit=crop&q=80",
    ingredients: "Potato Flakes, Edible Vegetable Oil (Palmolein), Besan, Spices, Iodised Salt"
  },
  {
    id: "8906012345678",
    barcode: "8906012345678",
    name: "Slow-Roasted Masala Bengal Gram (Chana)",
    brand: "Snackible",
    category: "Roasted Pulses",
    serving_size_g: 35.0,
    calories: 368.0,
    sugar: 1.5,
    saturated_fat: 0.8,
    total_fat: 5.2,
    protein: 19.5,
    fiber: 15.0,
    sodium_mg: 240.0,
    health_score: 85,
    grade: "A",
    classification: "Excellent",
    color: "#10b981",
    price_inr: 25,
    image_url: "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=600&auto=format&fit=crop&q=80",
    ingredients: "Bengal Gram (Chickpeas 92%), Mustard Oil, Black Salt, Cumin, Amchur"
  },
  {
    id: "7622210817007",
    barcode: "7622210817007",
    name: "Oreo Original Vanilla Creme Cookies",
    brand: "Cadbury",
    category: "Biscuits & Cookies",
    serving_size_g: 30.0,
    calories: 483.0,
    sugar: 38.5,
    saturated_fat: 9.8,
    total_fat: 20.0,
    protein: 5.1,
    fiber: 2.5,
    sodium_mg: 460.0,
    health_score: 12,
    grade: "E",
    classification: "Very Poor",
    color: "#ef4444",
    price_inr: 30,
    image_url: "https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=600&auto=format&fit=crop&q=80",
    ingredients: "Refined Wheat Flour, Sugar, Palm Oil, Invert Sugar, Cocoa Powder"
  },
  {
    id: "8908009988776",
    barcode: "8908009988776",
    name: "Rolled Oats, Chia & Jaggery Cookies",
    brand: "True Elements",
    category: "Healthy Biscuits",
    serving_size_g: 30.0,
    calories: 395.0,
    sugar: 11.2,
    saturated_fat: 2.1,
    total_fat: 9.8,
    protein: 11.0,
    fiber: 9.2,
    sodium_mg: 95.0,
    health_score: 75,
    grade: "B",
    classification: "Good",
    color: "#22c55e",
    price_inr: 40,
    image_url: "https://images.unsplash.com/photo-1499636136210-6f4ee915583e?w=600&auto=format&fit=crop&q=80",
    ingredients: "Rolled Oats (45%), Whole Wheat, Jaggery, Chia Seeds, Flaxseeds, Desi Ghee"
  },
  {
    id: "5449000000996",
    barcode: "5449000000996",
    name: "Coca-Cola Original Taste Can",
    brand: "Coca-Cola",
    category: "Beverages",
    serving_size_g: 100.0,
    calories: 44.0,
    sugar: 10.6,
    saturated_fat: 0.0,
    total_fat: 0.0,
    protein: 0.0,
    fiber: 0.0,
    sodium_mg: 12.0,
    health_score: 35,
    grade: "D",
    classification: "Poor",
    color: "#f97316",
    price_inr: 40,
    image_url: "https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=600&auto=format&fit=crop&q=80",
    ingredients: "Carbonated Water, Sugar, Acidity Regulator 338, Caramel Color 150d"
  },
  {
    id: "8901765112233",
    barcode: "8901765112233",
    name: "Tender Coconut Water (Unsweetened)",
    brand: "Raw Pressery",
    category: "Natural Hydration",
    serving_size_g: 100.0,
    calories: 19.0,
    sugar: 3.7,
    saturated_fat: 0.0,
    total_fat: 0.1,
    protein: 0.7,
    fiber: 1.1,
    sodium_mg: 28.0,
    health_score: 72,
    grade: "B",
    classification: "Good",
    color: "#22c55e",
    price_inr: 50,
    image_url: "https://images.unsplash.com/photo-1525385133512-2f3bdd039054?w=600&auto=format&fit=crop&q=80",
    ingredients: "100% Pure Tender Coconut Water, Vitamin C"
  }
];

export async function fetchProducts() {
  try {
    const res = await fetch(`${API_BASE}/products`);
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn("Using offline products catalog:", err);
  }
  return MOCK_PRODUCTS;
}

export async function fetchProductByBarcode(barcode) {
  try {
    const res = await fetch(`${API_BASE}/products/${barcode}`);
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn("Falling back to local product lookup");
  }
  const found = MOCK_PRODUCTS.find(p => p.barcode === barcode || p.id === barcode);
  return found || null;
}

export async function runShowdown(snackA, snackB) {
  try {
    const res = await fetch(`${API_BASE}/showdown`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ snack_a: snackA, snack_b: snackB })
    });
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn("Showdown fallback calculation:", err);
  }

  // Client-side showdown fallback
  const scoreA = snackA.health_score || 50;
  const scoreB = snackB.health_score || 50;
  const winner = scoreA >= scoreB ? snackA : snackB;
  const loser = scoreA >= scoreB ? snackB : snackA;
  const diff = Math.abs(scoreA - scoreB);

  return {
    snack_a: snackA,
    snack_b: snackB,
    winner_tag: scoreA >= scoreB ? "A" : "B",
    winner_id: winner.id,
    winner_name: winner.name,
    winner_score: winner.health_score,
    loser_score: loser.health_score,
    score_diff: diff,
    advantage_pct: Math.round((diff / Math.max(1, loser.health_score)) * 100),
    reasons: [
      `Delivers significantly more fiber and cleaner plant protein`,
      `Slashes unhealthy saturated palm oil and refined sugar`,
      `Much lower sodium footprint per serving`
    ],
    comparison_metrics: [
      { nutrient: "Calories", a: `${snackA.calories} kcal`, b: `${snackB.calories} kcal`, winner: snackA.calories < snackB.calories ? "A" : "B" },
      { nutrient: "Protein", a: `${snackA.protein}g`, b: `${snackB.protein}g`, winner: snackA.protein > snackB.protein ? "A" : "B" },
      { nutrient: "Dietary Fiber", a: `${snackA.fiber}g`, b: `${snackB.fiber}g`, winner: snackA.fiber > snackB.fiber ? "A" : "B" },
      { nutrient: "Total Sugar", a: `${snackA.sugar}g`, b: `${snackB.sugar}g`, winner: snackA.sugar < snackB.sugar ? "A" : "B" },
      { nutrient: "Saturated Fat", a: `${snackA.saturated_fat}g`, b: `${snackB.saturated_fat}g`, winner: snackA.saturated_fat < snackB.saturated_fat ? "A" : "B" },
      { nutrient: "Sodium", a: `${snackA.sodium_mg}mg`, b: `${snackB.sodium_mg}mg`, winner: snackA.sodium_mg < snackB.sodium_mg ? "A" : "B" }
    ]
  };
}

export async function fetchRecommendations(barcode) {
  try {
    const res = await fetch(`${API_BASE}/recommendations/${barcode}`);
    if (res.ok) return await res.json();
  } catch (err) {}
  // Offline fallback
  const target = MOCK_PRODUCTS.find(p => p.barcode === barcode) || MOCK_PRODUCTS[0];
  const recs = MOCK_PRODUCTS.filter(p => p.health_score > target.health_score).slice(0, 3);
  return {
    target_snack: target,
    recommendations: recs.map(r => ({
      ...r,
      score_gain: r.health_score - target.health_score,
      swap_headline: `+${r.health_score - target.health_score} Score Boost`,
      benefits: [`${Math.max(1, Math.round(r.fiber - target.fiber))}g more fiber`, `${Math.max(1, Math.round(target.sugar - r.sugar))}g less sugar`]
    }))
  };
}

export async function claimSwapReward(origName, swapName, scoreGain, points = 20) {
  try {
    const res = await fetch(`${API_BASE}/gamification/swap`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        original_name: origName,
        swap_name: swapName,
        score_gain: scoreGain,
        points: points
      })
    });
    if (res.ok) return await res.json();
  } catch (err) {}
  return {
    success: true,
    earned_points: points,
    current_points: 160,
    level: 2,
    message: `+${points} XP Awarded for Choosing Better Food!`
  };
}

export async function askAIChat(question, contextProduct) {
  try {
    const res = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, context_product: contextProduct })
    });
    if (res.ok) return await res.json();
  } catch (err) {}
  return {
    response: `**NutriLens AI Coach**: When evaluating snacks like ${contextProduct ? contextProduct.name : 'packaged foods'}, always verify the **Fiber-to-Sugar ratio**. If a snack has more sugar than fiber, it triggers rapid blood sugar fluctuations. Choose roasted seeds, nuts, and popped grains for lasting afternoon energy!`,
    source: "nutrilens-coach-offline"
  };
}
