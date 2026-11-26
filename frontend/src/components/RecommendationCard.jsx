import React from 'react';
import { ArrowUpRight, Sparkles, Check, Swords } from 'lucide-react';

export default function RecommendationCard({ recommendation, onStartShowdown }) {
  return (
    <div className="glass-card rounded-2xl p-3.5 border border-slate-700/60 hover:border-emerald-500/40 transition-all flex items-center justify-between gap-3 group">
      {/* Product Image */}
      <img
        src={recommendation.image_url}
        alt={recommendation.name}
        className="w-16 h-16 rounded-xl object-cover shrink-0 border border-slate-800"
      />

      {/* Info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-1.5 mb-1">
          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
            {recommendation.swap_headline || `+${recommendation.score_gain || 40} Boost`}
          </span>
          <span className="text-[10px] text-slate-400 font-medium">₹{recommendation.price_inr}</span>
        </div>

        <h4 className="font-bold text-xs text-white truncate group-hover:text-emerald-400 transition-colors">
          {recommendation.name}
        </h4>
        <p className="text-[10px] text-slate-400">{recommendation.brand}</p>

        {/* Benefits tags */}
        <div className="mt-1.5 flex flex-wrap gap-1">
          {(recommendation.benefits || ["High Fiber", "Low Sodium"]).slice(0, 2).map((b, i) => (
            <span key={i} className="text-[9px] px-1.5 py-0.2 rounded bg-slate-800 text-slate-300 flex items-center gap-0.5">
              <Check className="w-2.5 h-2.5 text-emerald-400" /> {b}
            </span>
          ))}
        </div>
      </div>

      {/* Action Button: Pit in Showdown */}
      <button
        onClick={() => onStartShowdown(recommendation)}
        className="p-2.5 rounded-xl bg-slate-800 hover:bg-emerald-500 hover:text-slate-950 text-slate-300 transition-all shrink-0 active:scale-95 shadow-md group/btn"
        title="Battle in Showdown"
      >
        <Swords className="w-4 h-4 text-amber-400 group-hover/btn:text-slate-950" />
      </button>
    </div>
  );
}
