import React from 'react';
import { Scan, Sparkles, ArrowRight, ShieldCheck, AlertTriangle, AlertCircle, Swords, HeartHandshake, Zap, Check, Trophy } from 'lucide-react';
import HealthScoreDial from '../components/HealthScoreDial';
import RecommendationCard from '../components/RecommendationCard';

export default function Home({
  selectedProduct,
  recommendations,
  onOpenScanner,
  onStartShowdown,
  onOpenCoach,
  points,
  streak,
  swapsCompleted
}) {
  return (
    <div className="space-y-6 pb-16">
      {/* Web Hero Dashboard Banner */}
      <div className="glass-card rounded-3xl p-6 sm:p-8 border border-slate-700/60 relative overflow-hidden">
        {/* Ambient Gradient Glows */}
        <div className="absolute -top-24 -left-24 w-72 h-72 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-24 -right-24 w-72 h-72 bg-teal-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
          <div className="max-w-xl">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-xs font-bold mb-3 shadow-sm">
              <Sparkles className="w-3.5 h-3.5" />
              NutriLens Smart Food Platform
            </div>
            <h1 className="font-display font-black text-2xl sm:text-4xl text-white tracking-tight leading-tight">
              Stop guessing nutrition labels.<br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400">
                Showdown your everyday snacks.
              </span>
            </h1>
            <p className="text-xs sm:text-sm text-slate-300 mt-2.5 leading-relaxed">
              Scan any packaged food barcode or label. Expose hidden palm oils and maltodextrin with our transparent 100-Point Health Score, and discover delicious, culturally relevant Indian snack alternatives.
            </p>

            <div className="mt-5 flex flex-wrap items-center gap-3">
              <button
                onClick={onOpenScanner}
                className="py-3 px-5 rounded-2xl bg-gradient-to-r from-emerald-500 to-teal-400 hover:from-emerald-400 hover:to-teal-300 text-slate-950 font-display font-extrabold text-xs sm:text-sm flex items-center justify-center gap-2 shadow-lg shadow-emerald-500/25 active:scale-95 transition-all"
              >
                <Scan className="w-4 h-4 stroke-[2.5]" />
                Scan Product Barcode
              </button>
              <button
                onClick={onOpenCoach}
                className="py-3 px-4 rounded-2xl bg-slate-900/80 hover:bg-slate-800 text-slate-200 text-xs sm:text-sm font-bold border border-slate-700 transition-all active:scale-95 flex items-center gap-2"
              >
                Ask AI Assistant
              </button>
            </div>
          </div>

          {/* Quick Metrics Cards */}
          <div className="grid grid-cols-3 gap-3 w-full lg:w-auto shrink-0">
            <div className="p-3.5 sm:p-4 rounded-2xl bg-slate-900/80 border border-slate-800 text-center min-w-[95px]">
              <span className="text-[10px] text-slate-400 font-semibold block uppercase">Health XP</span>
              <span className="font-display font-extrabold text-lg sm:text-xl text-emerald-400">+{points}</span>
            </div>
            <div className="p-3.5 sm:p-4 rounded-2xl bg-slate-900/80 border border-slate-800 text-center min-w-[95px]">
              <span className="text-[10px] text-slate-400 font-semibold block uppercase">Streak</span>
              <span className="font-display font-extrabold text-lg sm:text-xl text-amber-400">🔥 {streak}d</span>
            </div>
            <div className="p-3.5 sm:p-4 rounded-2xl bg-slate-900/80 border border-slate-800 text-center min-w-[95px]">
              <span className="text-[10px] text-slate-400 font-semibold block uppercase">Swaps</span>
              <span className="font-display font-extrabold text-lg sm:text-xl text-teal-300">{swapsCompleted}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main 2-Column Responsive Web Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Active Scanned Food Card & Health Score (7 Cols) */}
        {selectedProduct && (
          <div className="lg:col-span-7 space-y-5">
            <div className="glass-card rounded-3xl p-6 border border-slate-700/60 space-y-5 shadow-xl">
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <div className="flex items-center gap-4">
                  <img
                    src={selectedProduct.image_url}
                    alt={selectedProduct.name}
                    className="w-16 h-16 sm:w-20 sm:h-20 rounded-2xl object-cover border border-slate-700/80 shrink-0 shadow-md"
                  />
                  <div>
                    <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-400 bg-emerald-500/10 px-2.5 py-0.5 rounded-full border border-emerald-500/20">
                      {selectedProduct.category}
                    </span>
                    <h2 className="font-display font-extrabold text-lg sm:text-xl text-white mt-1 leading-snug">
                      {selectedProduct.name}
                    </h2>
                    <p className="text-xs text-slate-400 font-medium mt-0.5">
                      Brand: <span className="text-slate-200">{selectedProduct.brand}</span> • Serving: {selectedProduct.serving_size_g}g
                    </p>
                  </div>
                </div>

                <button
                  onClick={onOpenScanner}
                  className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-bold text-slate-300 hover:text-white border border-slate-700 transition-all self-end sm:self-auto shrink-0 flex items-center gap-1.5"
                >
                  <Scan className="w-3.5 h-3.5" /> Scan Another
                </button>
              </div>

              {/* Health Score Radial Dial & Classification Banner */}
              <div className="py-4 px-6 rounded-2xl bg-slate-900/70 border border-slate-800/80 flex flex-col sm:flex-row items-center justify-around gap-4 text-center sm:text-left">
                <HealthScoreDial
                  score={selectedProduct.health_score}
                  grade={selectedProduct.grade}
                  classification={selectedProduct.classification}
                  size={140}
                />
                <div className="max-w-xs space-y-1">
                  <h4 className="font-display font-bold text-sm text-white">
                    NutriLens 100-Point Score
                  </h4>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    Evaluated across sugar, saturated fats, sodium density, dietary fiber, and protein per 100g.
                  </p>
                  <div className="pt-1">
                    <span className={`inline-block text-xs font-bold ${
                      selectedProduct.health_score >= 70 ? 'text-emerald-400' : 'text-orange-400'
                    }`}>
                      {selectedProduct.health_score >= 70
                        ? '✓ Clean Nutritional Profile'
                        : '⚠ Highly Processed Snack — Consider a Swap!'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Traffic Light Nutrient Breakdown Grid */}
              <div className="space-y-2">
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">
                  Nutritional Traffic Light (per 100g)
                </span>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
                  {/* Sugar */}
                  <div className={`p-3 rounded-xl border ${
                    selectedProduct.sugar <= 5 ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' :
                    selectedProduct.sugar <= 12 ? 'bg-amber-500/10 border-amber-500/30 text-amber-400' :
                    'bg-red-500/10 border-red-500/30 text-red-400'
                  }`}>
                    <span className="text-[10px] block opacity-80">Total Sugar</span>
                    <span className="font-extrabold text-sm">{selectedProduct.sugar}g</span>
                  </div>

                  {/* Saturated Fat */}
                  <div className={`p-3 rounded-xl border ${
                    selectedProduct.saturated_fat <= 2 ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' :
                    selectedProduct.saturated_fat <= 6 ? 'bg-amber-500/10 border-amber-500/30 text-amber-400' :
                    'bg-red-500/10 border-red-500/30 text-red-400'
                  }`}>
                    <span className="text-[10px] block opacity-80">Saturated Fat</span>
                    <span className="font-extrabold text-sm">{selectedProduct.saturated_fat}g</span>
                  </div>

                  {/* Sodium */}
                  <div className={`p-3 rounded-xl border ${
                    selectedProduct.sodium_mg <= 150 ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' :
                    selectedProduct.sodium_mg <= 500 ? 'bg-amber-500/10 border-amber-500/30 text-amber-400' :
                    'bg-red-500/10 border-red-500/30 text-red-400'
                  }`}>
                    <span className="text-[10px] block opacity-80">Sodium</span>
                    <span className="font-extrabold text-sm">{selectedProduct.sodium_mg}mg</span>
                  </div>

                  {/* Fiber */}
                  <div className="p-3 rounded-xl border bg-slate-900 border-slate-800 text-emerald-400">
                    <span className="text-[10px] block opacity-80 text-slate-400">Dietary Fiber</span>
                    <span className="font-extrabold text-sm">{selectedProduct.fiber}g</span>
                  </div>

                  {/* Protein */}
                  <div className="p-3 rounded-xl border bg-slate-900 border-slate-800 text-emerald-400">
                    <span className="text-[10px] block opacity-80 text-slate-400">Protein</span>
                    <span className="font-extrabold text-sm">{selectedProduct.protein}g</span>
                  </div>

                  {/* Calories */}
                  <div className="p-3 rounded-xl border bg-slate-900 border-slate-800 text-slate-200">
                    <span className="text-[10px] block opacity-80 text-slate-400">Energy (kcal)</span>
                    <span className="font-extrabold text-sm">{selectedProduct.calories} kcal</span>
                  </div>
                </div>
              </div>

              {/* Ingredients & Additive Warning Tag */}
              {selectedProduct.ingredients && (
                <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 text-xs space-y-1.5">
                  <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
                    Ingredients Transparency Check:
                  </span>
                  <p className="text-slate-300 text-xs leading-relaxed">
                    {selectedProduct.ingredients}
                  </p>
                  {selectedProduct.ingredients.toLowerCase().includes('palmolein') || selectedProduct.ingredients.toLowerCase().includes('palm oil') ? (
                    <div className="mt-2 p-2.5 rounded-xl bg-orange-500/10 border border-orange-500/30 flex items-center gap-2 text-xs text-orange-400 font-semibold">
                      <AlertTriangle className="w-4 h-4 shrink-0" />
                      Contains Palm Oil / Palmolein — High in atherogenic palmitic acid.
                    </div>
                  ) : null}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Right Column: Recommended Healthy Swaps (5 Cols) */}
        <div className="lg:col-span-5 space-y-4">
          <div className="glass-card rounded-3xl p-6 border border-slate-700/60 space-y-4 shadow-xl">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="p-2 rounded-xl bg-emerald-500/15 text-emerald-400">
                  <HeartHandshake className="w-5 h-5" />
                </span>
                <div>
                  <h3 className="font-display font-extrabold text-base text-white">Recommended Swaps</h3>
                  <p className="text-xs text-slate-400">Smarter Indian Alternatives</p>
                </div>
              </div>
              <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-slate-800 text-slate-300">
                {recommendations.length} Matches
              </span>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed">
              Click the sword icon on any snack below to immediately launch a head-to-head battle in the <strong>Showdown Arena</strong>!
            </p>

            <div className="space-y-3">
              {recommendations.map((rec) => (
                <RecommendationCard
                  key={rec.id}
                  recommendation={rec}
                  onStartShowdown={() => onStartShowdown(selectedProduct, rec)}
                />
              ))}
            </div>

            {/* Battle Selected vs Top Recommendation CTA */}
            {recommendations.length > 0 && (
              <div className="pt-2">
                <button
                  onClick={() => onStartShowdown(selectedProduct, recommendations[0])}
                  className="w-full py-3.5 px-4 rounded-2xl bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-400 hover:to-orange-400 text-slate-950 font-display font-extrabold text-xs sm:text-sm flex items-center justify-center gap-2 shadow-lg shadow-amber-500/20 active:scale-98 transition-all"
                >
                  <Swords className="w-4 h-4" />
                  <span>Battle {selectedProduct.name.split(' ')[0]} vs {recommendations[0].name.split(' ')[0]}</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
