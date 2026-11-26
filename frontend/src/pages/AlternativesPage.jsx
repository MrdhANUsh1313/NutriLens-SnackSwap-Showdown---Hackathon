import React, { useState } from 'react';
import { Apple, Swords, Sparkles, Filter, CheckCircle2, ShieldCheck } from 'lucide-react';
import { MOCK_PRODUCTS } from '../services/api';

export default function AlternativesPage({ onStartShowdown, currentSelectedSnack }) {
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [filterPreference, setFilterPreference] = useState('all');

  const categories = ['All', 'Healthy Puffs', 'Roasted Pulses', 'Healthy Biscuits', 'Natural Hydration', 'Dark Chocolate', 'Millet Snacks'];

  // Filter healthy products (Score >= 60)
  const healthyProducts = MOCK_PRODUCTS.filter(p => p.health_score >= 60);

  const filtered = healthyProducts.filter(item => {
    if (selectedCategory !== 'All' && item.category !== selectedCategory) return false;
    if (filterPreference === 'protein' && item.protein < 8.0) return false;
    if (filterPreference === 'sugar' && item.sugar > 4.0) return false;
    if (filterPreference === 'fiber' && item.fiber < 5.0) return false;
    return true;
  });

  return (
    <div className="space-y-6 pb-16">
      {/* Page Header */}
      <div className="glass-card rounded-3xl p-6 sm:p-8 border border-slate-700/60 relative overflow-hidden">
        <div className="relative z-10 max-w-2xl">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-xs font-bold mb-3">
            <Sparkles className="w-3.5 h-3.5" />
            Curated Healthy Alternatives
          </div>
          <h1 className="font-display font-extrabold text-2xl sm:text-3xl text-white tracking-tight">
            Indian & Global <span className="text-emerald-400">Snack Swaps</span>
          </h1>
          <p className="text-xs sm:text-sm text-slate-300 mt-2 leading-relaxed">
            Replace ultra-processed snacks with nutrient-dense roasted pulses, lotus foxnuts (makhana), pure coconut water, and fiber-rich millet bhel.
          </p>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        {/* Category Pills */}
        <div className="flex gap-1.5 overflow-x-auto w-full sm:w-auto pb-1 sm:pb-0 no-scrollbar">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                selectedCategory === cat
                  ? 'bg-emerald-500 text-slate-950 font-bold shadow-md shadow-emerald-500/20'
                  : 'bg-slate-900 border border-slate-800 text-slate-300 hover:text-white hover:bg-slate-800'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Nutritional Goals Filter */}
        <div className="flex items-center gap-1.5 shrink-0 self-end sm:self-auto">
          <Filter className="w-3.5 h-3.5 text-slate-400" />
          <select
            value={filterPreference}
            onChange={(e) => setFilterPreference(e.target.value)}
            className="bg-slate-900 border border-slate-800 text-xs text-slate-200 rounded-xl px-2.5 py-1.5 focus:outline-none focus:border-emerald-500"
          >
            <option value="all">All Nutritional Profiles</option>
            <option value="protein">High Protein (≥8g)</option>
            <option value="sugar">Ultra-Low Sugar (≤4g)</option>
            <option value="fiber">High Fiber (≥5g)</option>
          </select>
        </div>
      </div>

      {/* Product Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((item) => (
          <div
            key={item.id}
            className="glass-card rounded-3xl p-5 border border-slate-700/60 hover:border-emerald-500/40 transition-all flex flex-col justify-between group"
          >
            <div>
              <div className="relative mb-3">
                <img
                  src={item.image_url}
                  alt={item.name}
                  className="w-full h-40 object-cover rounded-2xl border border-slate-800 group-hover:scale-[1.02] transition-transform duration-300"
                />
                <span className="absolute top-2.5 right-2.5 px-2.5 py-1 rounded-full bg-slate-950/80 backdrop-blur-md border border-emerald-500/30 text-emerald-400 text-xs font-extrabold flex items-center gap-1">
                  <ShieldCheck className="w-3.5 h-3.5" /> {item.health_score}/100
                </span>
                <span className="absolute bottom-2.5 left-2.5 px-2 py-0.5 rounded-full bg-slate-950/80 backdrop-blur-md text-slate-300 text-[10px] font-semibold">
                  ₹{item.price_inr} • {item.serving_size_g}g
                </span>
              </div>

              <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-400">
                {item.category}
              </span>
              <h3 className="font-display font-bold text-sm sm:text-base text-white mt-0.5 line-clamp-1 group-hover:text-emerald-400 transition-colors">
                {item.name}
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">{item.brand}</p>

              {/* Nutrition badges */}
              <div className="mt-3 grid grid-cols-3 gap-2 text-center">
                <div className="p-1.5 rounded-lg bg-slate-900 border border-slate-800">
                  <span className="text-[9px] text-slate-400 block">Protein</span>
                  <span className="text-xs font-bold text-emerald-400">{item.protein}g</span>
                </div>
                <div className="p-1.5 rounded-lg bg-slate-900 border border-slate-800">
                  <span className="text-[9px] text-slate-400 block">Fiber</span>
                  <span className="text-xs font-bold text-emerald-400">{item.fiber}g</span>
                </div>
                <div className="p-1.5 rounded-lg bg-slate-900 border border-slate-800">
                  <span className="text-[9px] text-slate-400 block">Sugar</span>
                  <span className="text-xs font-bold text-slate-300">{item.sugar}g</span>
                </div>
              </div>
            </div>

            {/* Battle Button */}
            <div className="mt-4 pt-3 border-t border-slate-800/80">
              <button
                onClick={() => onStartShowdown(currentSelectedSnack || MOCK_PRODUCTS[0], item)}
                className="w-full py-2.5 px-3 rounded-xl bg-slate-900 hover:bg-emerald-500 hover:text-slate-950 text-slate-200 border border-slate-800 hover:border-emerald-500 text-xs font-bold transition-all flex items-center justify-center gap-2 group/btn"
              >
                <Swords className="w-3.5 h-3.5 text-amber-400 group-hover/btn:text-slate-950" />
                <span>Battle in Showdown</span>
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
