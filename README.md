# 🥑 NutriLens: SnackSwap Showdown – Web Application

> **Category**: HealthTech | FoodTech | AI/ML | Web Application  
> *AI-powered smart food analysis, 100-point transparent health score, and healthy snack recommendation showdown.*

---

## 🌟 Overview & Web Application Architecture

NutriLens is designed as a responsive, modern web application running seamlessly across desktop, tablet, and mobile browsers.

**Core Web Modules:**
1. **Desktop & Mobile Responsive Dashboard**: Overview of scanned snacks, health score dial, traffic light nutrient badges, and active streak.
2. **Smart Web Scanner**: Real-time webcam barcode scanning (`getUserMedia`), packaging photo upload for OCR, and 1-click test catalog.
3. **⚔️ SnackSwap Showdown Arena**: Widescreen dual-column arena pitting everyday snacks against healthy replacements with live metric differentials and victory rationales.
4. **Curated Healthy Swaps Catalog**: Full-page explorer of Indian alternatives (roasted makhana, chana, millet bhel, tender coconut water) filterable by nutrition goals (High Protein, Low Sugar, High Fiber).
5. **Gamification & Habit Tracker**: Levels, badges, daily streaks, and live community weekly leaderboard.
6. **AI Nutrition Coach**: Intelligent ingredient explainer addressing palm oil, maltodextrin, and hidden sugars powered by Google Gemini.

---

## 🏗️ Architecture & Tech Stack

- **Frontend**: React.js (Vite + Tailwind CSS + Lucide Icons + Canvas-Confetti)
- **Mobile Container**: Capacitor for Android APK packaging (`@capacitor/android`)
- **Backend API**: Python FastAPI + zero-dependency Standalone HTTP Server fallback
- **Data & AI**: Open Food Facts API, Transparent 100-pt Algorithmic Engine, Gemini AI Assistant
- **Database**: SQLite / Supabase

```
NutriLens/
├── backend/
│   ├── app/
│   │   ├── services/
│   │   │   ├── scoring.py          # 100-Point Health Score Engine
│   │   │   ├── food_facts.py       # Open Food Facts API & local fallback
│   │   │   ├── showdown.py         # Head-to-Head Comparison Matrix
│   │   │   ├── recommendations.py  # Indian & Global Healthy Swaps
│   │   │   └── ai_coach.py         # Gemini AI & Nutrition Explainer
│   │   ├── standalone_server.py    # Zero-dependency Python API
│   │   └── main.py                 # FastAPI Application
│   ├── data/
│   │   └── seed_snacks.json        # Pre-seeded catalog (Lay's, Makhana, Bhujia, Chana...)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/             # Navbar, HealthScoreDial, ShowdownArena, ScannerModal...
│   │   ├── pages/                  # Home, ShowdownPage, RewardsPage
│   │   ├── services/api.js         # Unified client with offline mock fallback
│   │   ├── App.jsx
│   │   └── index.css
│   ├── capacitor.config.json       # Android packaging config
│   └── package.json
├── start_all.bat                   # 1-click launcher for both servers
├── run_backend.ps1                 # Backend runner
└── run_frontend.ps1                # Frontend runner
```

---

## 🧮 100-Point Health Score Formula

$$\text{Base Score} = 70$$
$$\text{Score} = 70 - (\text{Penalties}_{\text{sugar}} + \text{Penalties}_{\text{sat\_fat}} + \text{Penalties}_{\text{sodium}} + \text{Penalties}_{\text{cal}} + \text{Penalties}_{\text{fat}}) + (\text{Bonuses}_{\text{fiber}} + \text{Bonuses}_{\text{protein}})$$

### Classification & Traffic Light Grades:
- **80 – 100**: 🟢 **Grade A (Excellent)** — Clean nutrition / superfoods
- **60 – 79**: 🟢 **Grade B (Good)** — Healthy everyday option
- **40 – 59**: 🟡 **Grade C (Moderate)** — Eat in moderation
- **20 – 39**: 🟠 **Grade D (Poor)** — Ultra-processed, high fat/sugar/salt
- **0 – 19**: 🔴 **Grade E (Very Poor)** — Extreme sugar / junk

---

## ⚡ Quick Start Guide

### 1. Launch Backend API (Port 8000)
```powershell
.\run_backend.ps1
# Or: & "python" backend/app/standalone_server.py 8000
```

### 2. Launch Frontend (Port 5173)
```powershell
.\run_frontend.ps1
```

### 3. Or 1-Click Launch Everything:
Double click `start_all.bat`.

---

## 📱 Build Native Android APK (Capacitor)

```bash
cd frontend
npm run build
npx cap add android
npx cap copy
npx cap open android
```
*In Android Studio, click **Build > Build Bundle(s) / APK(s) > Build APK(s)** to generate `app-debug.apk`.*

---

## 🎤 2-Minute Hackathon Winning Pitch Script

1. **The Hook (0:00 - 0:25)**:
   > *"Judges, when you buy a bag of chips or cookies, you aren't told that 40% of its calories come from cheap palm oil and hidden sugars under 50 different names. Nutrition tables are dense, confusing, and uninspiring."*

2. **The Solution (0:25 - 0:55)**:
   > *"Introducing **NutriLens: SnackSwap Showdown**. We don't just calculate boring calories. Our mobile app scans your snack and instantly translates deceptive labels into a transparent 100-Point Health Score with traffic-light alerts."*

3. **The 'Wow' Factor: Showdown Arena (0:55 - 1:30)**:
   > *"*(Live Demo)* Watch this: We pit Lay's Magic Masala against Roasted Peri-Peri Makhana in the **SnackSwap Showdown Arena**. Boom! Makhana wins by +56 points because it provides 3x more fiber, 70% less fat, and 60% less sodium. With one tap, I claim my swap, earn +20 XP, unlock the 'Sodium Slasher' badge, and level up my daily streak!"*

4. **The Impact & Wrap-up (1:30 - 2:00)**:
   > *"By focusing on culturally accessible swaps like makhana, roasted chana, and millet bhel, NutriLens makes healthier eating actionable, budget-conscious, and addictive. Thank you!"*
