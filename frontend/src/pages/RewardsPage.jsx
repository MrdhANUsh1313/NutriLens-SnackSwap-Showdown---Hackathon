import React from 'react';
import { Trophy, Flame, Sparkles, Award, ShieldCheck, Star, Users, CheckCircle2, History } from 'lucide-react';

export default function RewardsPage({ points, streak, swapsCompleted, history = [] }) {
  const nextLevelXP = 200;
  const progressPct = Math.min(100, Math.round((points / nextLevelXP) * 100));

  const badges = [
    { id: 1, name: "First Scan", icon: "🔍", desc: "Scanned your first food label", unlocked: true, date: "Nov 15" },
    { id: 2, name: "Snack Swapper", icon: "🥑", desc: "Completed your first healthy swap", unlocked: true, date: "Nov 16" },
    { id: 3, name: "Sodium Slasher", icon: "🧂", desc: "Replaced high-sodium chips with chana", unlocked: true, date: "Nov 17" },
    { id: 4, name: "Sugar Slayer", icon: "🍬", desc: "Replaced 3 sugary snacks in a row", unlocked: points >= 160, date: points >= 160 ? "Today" : "Locked" },
    { id: 5, name: "7-Day Warrior", icon: "🔥", desc: "Maintain a 7-day healthy choice streak", unlocked: false, date: "Locked" },
    { id: 6, name: "Millet Master", icon: "🌾", desc: "Swapped to an indigenous ancient grain", unlocked: false, date: "Locked" },
  ];

  const leaderboard = [
    { rank: 1, name: "Priya Sharma", points: 380, streak: 12, badge: "Nutrition Guru", avatar: "👩🏽" },
    { rank: 2, name: "Rahul Verma", points: 290, streak: 8, badge: "Fiber Fanatic", avatar: "👨🏽" },
    { rank: 3, name: "Alex Hunter (You)", points: points, streak: streak, badge: "Snack Scout", avatar: "🥑", isUser: true },
    { rank: 4, name: "Ananya Sen", points: 120, streak: 3, badge: "Rookie", avatar: "👩🏻" },
    { rank: 5, name: "Karan Patel", points: 95, streak: 2, badge: "Explorer", avatar: "👨🏻" },
  ];

  return (
    <div className="space-y-6 pb-16 max-w-6xl mx-auto">
      {/* Top Gamification Journey Banner */}
      <div className="glass-card rounded-3xl p-6 sm:p-8 border border-slate-700/60 relative overflow-hidden shadow-xl">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="space-y-2 max-w-md">
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/20 inline-block">
              Level 2 Snack Scout
            </span>
            <h1 className="font-display font-black text-2xl sm:text-3xl text-white">
              Gamified Health Habits
            </h1>
            <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
              Every healthy swap earns XP, keeps your streak alive, and unlocks badges that celebrate smarter everyday choices.
            </p>
          </div>

          {/* Quick Stats Block */}
          <div className="flex items-center gap-3 w-full md:w-auto">
            <div className="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/25 flex items-center gap-3 flex-1 md:flex-initial">
              <Flame className="w-8 h-8 fill-amber-400 text-amber-400 animate-pulse" />
              <div>
                <span className="text-[10px] text-amber-300 uppercase font-bold block">Current Streak</span>
                <span className="font-display font-extrabold text-xl text-white">{streak} Days</span>
              </div>
            </div>

            <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/25 flex items-center gap-3 flex-1 md:flex-initial">
              <Sparkles className="w-8 h-8 text-emerald-400" />
              <div>
                <span className="text-[10px] text-emerald-300 uppercase font-bold block">Total Score</span>
                <span className="font-display font-extrabold text-xl text-white">{points} XP</span>
              </div>
            </div>
          </div>
        </div>

        {/* Level Progress Bar */}
        <div className="mt-6 pt-5 border-t border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-300 font-semibold">Progress to Level 3 (Nutrition Master)</span>
            <span className="text-emerald-400 font-bold">{points} / {nextLevelXP} XP ({progressPct}%)</span>
          </div>
          <div className="w-full h-3 bg-slate-900 rounded-full overflow-hidden border border-slate-800">
            <div
              className="h-full bg-gradient-to-r from-emerald-500 via-teal-400 to-cyan-400 rounded-full transition-all duration-700 shadow-sm"
              style={{ width: `${progressPct}%` }}
            />
          </div>
        </div>
      </div>

      {/* 2-Column Layout: Badges (Left 7) & Community Leaderboard (Right 5) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Achievement Badges Showcase */}
        <div className="lg:col-span-7 space-y-5">
          <div className="glass-card rounded-3xl p-6 border border-slate-700/60 space-y-4 shadow-xl">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="p-2 rounded-xl bg-emerald-500/15 text-emerald-400">
                  <Award className="w-5 h-5" />
                </span>
                <div>
                  <h3 className="font-display font-bold text-base text-white">Achievement Badges</h3>
                  <p className="text-xs text-slate-400">Milestones unlocked along your healthy snacking journey</p>
                </div>
              </div>
              <span className="text-xs font-bold text-emerald-400 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20">
                3 of 6 Unlocked
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {badges.map((b) => (
                <div
                  key={b.id}
                  className={`p-4 rounded-2xl flex flex-col items-center text-center transition-all ${
                    b.unlocked
                      ? 'bg-slate-900/90 border border-emerald-500/40 shadow-lg shadow-emerald-950/20 hover:scale-[1.02]'
                      : 'bg-slate-900/30 border border-slate-800 opacity-40 grayscale'
                  }`}
                >
                  <div className="text-3xl mb-2">{b.icon}</div>
                  <h4 className="font-bold text-xs text-white leading-tight">{b.name}</h4>
                  <p className="text-[10px] text-slate-400 mt-1 leading-snug">{b.desc}</p>
                  <span className={`text-[9px] mt-2 px-2 py-0.5 rounded-full font-bold ${
                    b.unlocked ? 'bg-emerald-500/20 text-emerald-400' : 'bg-slate-800 text-slate-500'
                  }`}>
                    {b.date}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Weekly Community Leaderboard */}
        <div className="lg:col-span-5 space-y-5">
          <div className="glass-card rounded-3xl p-6 border border-slate-700/60 space-y-4 shadow-xl">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="p-2 rounded-xl bg-amber-500/15 text-amber-400">
                  <Users className="w-5 h-5" />
                </span>
                <div>
                  <h3 className="font-display font-bold text-base text-white">Weekly Community Board</h3>
                  <p className="text-xs text-slate-400">Top healthy snackers this week</p>
                </div>
              </div>
              <span className="text-xs font-bold text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded-full border border-amber-500/20">
                Live
              </span>
            </div>

            <div className="space-y-2.5">
              {leaderboard.map((u) => (
                <div
                  key={u.rank}
                  className={`flex items-center justify-between p-3 rounded-2xl border text-xs transition-all ${
                    u.isUser
                      ? 'bg-emerald-500/15 border-emerald-500/50 text-white shadow-md'
                      : 'bg-slate-900/70 border-slate-800 text-slate-300'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <span className={`w-6 text-center font-black text-sm ${
                      u.rank === 1 ? 'text-amber-400' : u.rank === 2 ? 'text-slate-300' : u.rank === 3 ? 'text-amber-600' : 'text-slate-500'
                    }`}>
                      #{u.rank}
                    </span>
                    <span className="text-xl">{u.avatar}</span>
                    <div>
                      <h5 className="font-bold text-white text-xs flex items-center gap-1.5">
                        {u.name}
                        {u.isUser && (
                          <span className="text-[9px] px-1.5 py-0.2 rounded bg-emerald-500 text-slate-950 font-extrabold uppercase">
                            You
                          </span>
                        )}
                      </h5>
                      <p className="text-[10px] text-slate-400">{u.badge} • 🔥 {u.streak}d streak</p>
                    </div>
                  </div>
                  <span className="font-display font-extrabold text-sm text-emerald-400">{u.points} XP</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
