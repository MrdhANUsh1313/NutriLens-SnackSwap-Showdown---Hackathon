import React, { useState } from 'react';
import { Swords, RefreshCw, Sparkles, Trophy, ArrowRight } from 'lucide-react';
import ShowdownArena from '../components/ShowdownArena';
import { MOCK_PRODUCTS } from '../services/api';

export default function ShowdownPage({
  showdownData,
  onRunShowdown,
  onClaimSwap
}) {
  const [snackAId, setSnackAId] = useState(showdownData?.snack_a?.id || MOCK_PRODUCTS[0].id);
  const [snackBId, setSnackBId] = useState(showdownData?.snack_b?.id || MOCK_PRODUCTS[1].id);

  const handleBattle = (idA, idB) => {
    const a = MOCK_PRODUCTS.find(p => p.id === idA) || MOCK_PRODUCTS[0];
    const b = MOCK_PRODUCTS.find(p => p.id === idB) || MOCK_PRODUCTS[1];
    onRunShowdown(a, b);
  };

  return (
    <div className="space-y-6 pb-16 max-w-5xl mx-auto">
      {/* Contender Selection Header Card */}
      <div className="glass-card rounded-3xl p-6 sm:p-8 border border-slate-700/60 space-y-5 shadow-xl">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <span className="p-3 rounded-2xl bg-amber-500/15 text-amber-400 border border-amber-500/30">
              <Swords className="w-6 h-6 animate-vs" />
            </span>
            <div>
              <h1 className="font-display font-black text-xl sm:text-2xl text-white">
                SnackSwap <span className="text-amber-400">Showdown Arena</span>
              </h1>
              <p className="text-xs sm:text-sm text-slate-300">
                Pit any two snacks against each other to discover the healthier choice.
              </p>
            </div>
          </div>

          <button
            onClick={() => handleBattle(snackAId, snackBId)}
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-bold text-emerald-400 hover:text-emerald-300 border border-slate-700 transition-all flex items-center gap-2 active:scale-95 shadow-sm"
          >
            <RefreshCw className="w-4 h-4" /> Re-calculate Match
          </button>
        </div>

        {/* Dropdown Contender Selectors */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs pt-2">
          {/* Corner A */}
          <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-2">
            <label className="text-xs font-bold text-slate-300 flex items-center justify-between">
              <span>Corner A (Everyday / Junk Snack)</span>
              <span className="text-amber-400">Red Corner</span>
            </label>
            <select
              value={snackAId}
              onChange={(e) => {
                setSnackAId(e.target.value);
                handleBattle(e.target.value, snackBId);
              }}
              className="w-full bg-slate-950 border border-slate-700 text-white rounded-xl p-3 text-xs focus:outline-none focus:border-amber-500 font-medium"
            >
              {MOCK_PRODUCTS.map(p => (
                <option key={p.id} value={p.id}>
                  {p.name} ({p.brand}) — Score: {p.health_score}/100
                </option>
              ))}
            </select>
          </div>

          {/* Corner B */}
          <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-2">
            <label className="text-xs font-bold text-slate-300 flex items-center justify-between">
              <span>Corner B (Healthy Alternative)</span>
              <span className="text-emerald-400">Green Corner</span>
            </label>
            <select
              value={snackBId}
              onChange={(e) => {
                setSnackBId(e.target.value);
                handleBattle(snackAId, e.target.value);
              }}
              className="w-full bg-slate-950 border border-slate-700 text-white rounded-xl p-3 text-xs focus:outline-none focus:border-emerald-500 font-medium"
            >
              {MOCK_PRODUCTS.map(p => (
                <option key={p.id} value={p.id}>
                  {p.name} ({p.brand}) — Score: {p.health_score}/100
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Main Showdown Arena */}
      <ShowdownArena
        showdownData={showdownData}
        onClaimSwap={onClaimSwap}
      />
    </div>
  );
}
