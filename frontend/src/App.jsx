import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import ScannerModal from './components/ScannerModal';
import AICoachModal from './components/AICoachModal';
import Home from './pages/Home';
import ShowdownPage from './pages/ShowdownPage';
import AlternativesPage from './pages/AlternativesPage';
import RewardsPage from './pages/RewardsPage';
import { MOCK_PRODUCTS, runShowdown, fetchRecommendations, claimSwapReward } from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('home');
  const [isScannerOpen, setIsScannerOpen] = useState(false);
  const [isCoachOpen, setIsCoachOpen] = useState(false);

  // Current active snack (Default: Lay's Magic Masala Chips)
  const [selectedProduct, setSelectedProduct] = useState(MOCK_PRODUCTS[0]);
  const [recommendations, setRecommendations] = useState([MOCK_PRODUCTS[1], MOCK_PRODUCTS[3]]);
  const [showdownData, setShowdownData] = useState(null);

  // User Gamification stats
  const [points, setPoints] = useState(140);
  const [streak, setStreak] = useState(4);
  const [swapsCompleted, setSwapsCompleted] = useState(7);
  const [history, setHistory] = useState([]);

  // Initialize Showdown Data with default match (Lay's vs Peri-Peri Makhana)
  useEffect(() => {
    async function initShowdown() {
      const data = await runShowdown(MOCK_PRODUCTS[0], MOCK_PRODUCTS[1]);
      setShowdownData(data);
    }
    initShowdown();
  }, []);

  // When a product is scanned/selected
  const handleSelectProduct = async (product) => {
    setSelectedProduct(product);
    // Fetch smart recommendations
    const recData = await fetchRecommendations(product.barcode || product.id);
    if (recData && recData.recommendations) {
      setRecommendations(recData.recommendations);
      // Run showdown against top recommendation
      if (recData.recommendations.length > 0) {
        const show = await runShowdown(product, recData.recommendations[0]);
        setShowdownData(show);
      }
    }
    setActiveTab('home');
  };

  // Launch showdown between two specific products
  const handleStartShowdown = async (snackA, snackB) => {
    const data = await runShowdown(snackA, snackB);
    setShowdownData(data);
    setActiveTab('showdown');
  };

  // Global search from top bar
  const handleSearch = (query) => {
    const q = query.toLowerCase();
    const found = MOCK_PRODUCTS.find(p =>
      p.name.toLowerCase().includes(q) ||
      p.brand.toLowerCase().includes(q) ||
      p.barcode === q
    );
    if (found) {
      handleSelectProduct(found);
    } else {
      setIsScannerOpen(true);
    }
  };

  // Claim swap reward
  const handleClaimSwap = async (origName, swapName, scoreGain, pts) => {
    setPoints(prev => prev + pts);
    setSwapsCompleted(prev => prev + 1);
    await claimSwapReward(origName, swapName, scoreGain, pts);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-between selection:bg-emerald-500 selection:text-slate-950">
      {/* Top Navigation Bar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenScanner={() => setIsScannerOpen(true)}
        onOpenCoach={() => setIsCoachOpen(true)}
        onSearch={handleSearch}
        points={points}
        streak={streak}
      />

      {/* Main Full-Width Web Application Container */}
      <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {activeTab === 'home' && (
          <Home
            selectedProduct={selectedProduct}
            recommendations={recommendations}
            onOpenScanner={() => setIsScannerOpen(true)}
            onStartShowdown={handleStartShowdown}
            onOpenCoach={() => setIsCoachOpen(true)}
            points={points}
            streak={streak}
            swapsCompleted={swapsCompleted}
          />
        )}

        {activeTab === 'showdown' && (
          <ShowdownPage
            showdownData={showdownData}
            onRunShowdown={handleStartShowdown}
            onClaimSwap={handleClaimSwap}
          />
        )}

        {activeTab === 'alternatives' && (
          <AlternativesPage
            onStartShowdown={handleStartShowdown}
            currentSelectedSnack={selectedProduct}
          />
        )}

        {activeTab === 'rewards' && (
          <RewardsPage
            points={points}
            streak={streak}
            swapsCompleted={swapsCompleted}
            history={history}
          />
        )}
      </main>

      {/* Web Application Footer */}
      <footer className="w-full glass-panel border-t border-slate-800/80 py-6 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-400">
          <div className="flex items-center gap-2">
            <span className="text-base">🥑</span>
            <span className="font-bold text-white">NutriLens: SnackSwap Showdown</span>
            <span>• HealthTech Hackathon 2026</span>
          </div>

          <div className="flex items-center gap-4 text-slate-400">
            <span>Powered by Open Food Facts & Gemini AI</span>
            <span>•</span>
            <button
              onClick={() => setIsCoachOpen(true)}
              className="text-emerald-400 hover:underline font-semibold"
            >
              Ask AI Nutritionist
            </button>
          </div>
        </div>
      </footer>

      {/* Smart Food Scanner Modal */}
      <ScannerModal
        isOpen={isScannerOpen}
        onClose={() => setIsScannerOpen(false)}
        onSelectProduct={handleSelectProduct}
      />

      {/* AI Nutrition Assistant Modal */}
      <AICoachModal
        isOpen={isCoachOpen}
        onClose={() => setIsCoachOpen(false)}
        currentProduct={selectedProduct}
      />
    </div>
  );
}
