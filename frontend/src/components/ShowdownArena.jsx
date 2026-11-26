import React, { useState } from 'react';
import { Trophy, Swords, Sparkles, CheckCircle2, ChevronRight, Share2, Flame } from 'lucide-react';
import confetti from 'canvas-confetti';

export default function ShowdownArena({ showdownData, onClaimSwap }) {
  const [swapped, setSwapped] = useState(false);

  if (!showdownData) return null;

  const { snack_a, snack_b, winner_tag, winner_name, score_diff, advantage_pct, reasons, comparison_metrics } = showdownData;
  const winner = winner_tag === 'A' ? snack_a : snack_b;
  const loser = winner_tag === 'A' ? snack_b : snack_a;

  const handleSwapClick = () => {
    if (swapped) return;
    setSwapped(true);

    // Fire celebratory confetti!
    confetti({
      particleCount: 80,
      spread: 70,
      origin: { y: 0.6 }
    });

    if (onClaimSwap) {
      onClaimSwap(loser.name, winner.name, score_diff, 20);
    }
  };

  return (
    <div className="space-y-4">
      {/* Showdown Header Banner */}
      <div className="glass-card rounded-3xl p-5 border border-slate-700/60 relative overflow-hidden">
        {/* Glow backdrop */}
        <div className="absolute -top-12 -left-12 w-40 h-40 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-12 -right-12 w-40 h-40 bg-amber-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <span className="p-2 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20">
              <Swords className="w-5 h-5 animate-vs" />
            </span>
            <div>
              <h2 className="font-display font-extrabold text-lg text-white">SnackSwap Showdown</h2>
              <p className="text-xs text-slate-400">Head-to-Head Nutritional Clash</p>
            </div>
          </div>
          <span className="text-[11px] font-bold px-2.5 py-1 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
            {advantage_pct}% Healthier
          </span>
        </div>

        {/* Dual Snack Face-off Cards */}
        <div className="relative grid grid-cols-2 gap-3 items-stretch">
          {/* Snack A */}
          <div className={`p-3 rounded-2xl flex flex-col justify-between transition-all ${
            winner_tag === 'A'
              ? 'bg-emerald-950/40 border-2 border-emerald-500/80 shadow-lg shadow-emerald-950/50'
              : 'bg-slate-900/60 border border-slate-800'
          }`}>
            <div>
              <div className="relative mb-2">
                <img src={snack_a.image_url} alt={snack_a.name} className="w-full h-24 object-cover rounded-xl" />
                {winner_tag === 'A' && (
                  <span className="absolute top-2 left-2 px-2 py-0.5 rounded-full bg-emerald-500 text-slate-950 text-[10px] font-extrabold uppercase tracking-wider flex items-center gap-1 shadow-md">
                    <Trophy className="w-3 h-3" /> Winner
                  </span>
                )}
              </div>
              <h4 className="font-bold text-xs text-white line-clamp-2">{snack_a.name}</h4>
              <p className="text-[10px] text-slate-400">{snack_a.brand}</p>
            </div>

            <div className="mt-3 pt-2 border-t border-slate-800 flex items-center justify-between">
              <span className="text-[10px] text-slate-400 font-medium">Score</span>
              <span className={`text-base font-extrabold ${winner_tag === 'A' ? 'text-emerald-400' : 'text-slate-300'}`}>
                {snack_a.health_score}<span className="text-[10px] font-normal text-slate-500">/100</span>
              </span>
            </div>
          </div>

          {/* Central VS Emblem */}
          <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-10 w-9 h-9 rounded-full bg-slate-900 border-2 border-slate-700 flex items-center justify-center shadow-xl">
            <span className="font-display font-extrabold text-xs text-amber-400">VS</span>
          </div>

          {/* Snack B */}
          <div className={`p-3 rounded-2xl flex flex-col justify-between transition-all ${
            winner_tag === 'B'
              ? 'bg-emerald-950/40 border-2 border-emerald-500/80 shadow-lg shadow-emerald-950/50'
              : 'bg-slate-900/60 border border-slate-800'
          }`}>
            <div>
              <div className="relative mb-2">
                <img src={snack_b.image_url} alt={snack_b.name} className="w-full h-24 object-cover rounded-xl" />
                {winner_tag === 'B' && (
                  <span className="absolute top-2 left-2 px-2 py-0.5 rounded-full bg-emerald-500 text-slate-950 text-[10px] font-extrabold uppercase tracking-wider flex items-center gap-1 shadow-md">
                    <Trophy className="w-3 h-3" /> Winner
                  </span>
                )}
              </div>
              <h4 className="font-bold text-xs text-white line-clamp-2">{snack_b.name}</h4>
              <p className="text-[10px] text-slate-400">{snack_b.brand}</p>
            </div>

            <div className="mt-3 pt-2 border-t border-slate-800 flex items-center justify-between">
              <span className="text-[10px] text-slate-400 font-medium">Score</span>
              <span className={`text-base font-extrabold ${winner_tag === 'B' ? 'text-emerald-400' : 'text-slate-300'}`}>
                {snack_b.health_score}<span className="text-[10px] font-normal text-slate-500">/100</span>
              </span>
            </div>
          </div>
        </div>

        {/* Winner Announcement Card */}
        <div className="mt-4 p-3.5 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 flex items-start gap-3">
          <div className="p-2 rounded-xl bg-emerald-500 text-slate-950 shrink-0 font-extrabold">
            <Trophy className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold uppercase tracking-wider text-emerald-400">🏆 Showdown Victor:</span>
              <span className="text-xs font-bold text-white">{winner.name}</span>
            </div>
            <p className="text-xs text-slate-300 mt-1">
              Wins by <span className="font-bold text-emerald-400">+{score_diff} points</span> over {loser.name}.
            </p>
          </div>
        </div>
      </div>

      {/* Side-by-Side Nutritional Breakdown Matrix */}
      <div className="glass-card rounded-3xl p-5 border border-slate-700/60 space-y-3">
        <h3 className="font-display font-bold text-sm text-white flex items-center justify-between">
          <span>Nutrient Face-Off (per 100g)</span>
          <span className="text-[10px] text-slate-400 font-normal">Green indicates superior</span>
        </h3>

        <div className="space-y-2">
          {comparison_metrics.map((row, idx) => (
            <div key={idx} className="flex items-center justify-between p-2.5 rounded-xl bg-slate-900/60 border border-slate-800/80 text-xs">
              {/* Snack A Value */}
              <span className={`w-1/3 text-left font-semibold ${row.winner === 'A' ? 'text-emerald-400 font-bold' : 'text-slate-400'}`}>
                {row.a}
              </span>

              {/* Metric Name */}
              <span className="w-1/3 text-center text-slate-300 font-medium text-[11px]">
                {row.nutrient}
              </span>

              {/* Snack B Value */}
              <span className={`w-1/3 text-right font-semibold ${row.winner === 'B' ? 'text-emerald-400 font-bold' : 'text-slate-400'}`}>
                {row.b}
              </span>
            </div>
          ))}
        </div>

        {/* AI Explainer Bullets */}
        <div className="mt-4 pt-3 border-t border-slate-800 space-y-1.5">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Why it won:</span>
          {reasons.map((r, i) => (
            <div key={i} className="flex items-start gap-2 text-xs text-slate-300">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
              <span>{r}</span>
            </div>
          ))}
        </div>

        {/* Instant Healthy Swap Action CTA */}
        <div className="pt-2">
          <button
            onClick={handleSwapClick}
            disabled={swapped}
            className={`w-full py-3.5 px-4 rounded-2xl font-display font-bold text-sm flex items-center justify-center gap-2 transition-all shadow-lg ${
              swapped
                ? 'bg-slate-800 text-emerald-400 border border-emerald-500/40 cursor-default'
                : 'bg-gradient-to-r from-emerald-500 to-teal-400 hover:from-emerald-400 hover:to-teal-300 text-slate-950 shadow-emerald-500/25 active:scale-98'
            }`}
          >
            {swapped ? (
              <>
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span>Swap Completed! +20 XP Earned</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>I'll Swap to {winner.name.split(' ')[0]}! (+20 XP)</span>
                <ChevronRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
