import React, { useState } from 'react';
import { Flame, Sparkles, Scan, Swords, Home, Bot, Trophy, Search, Apple, Menu, X } from 'lucide-react';

export default function Navbar({
  activeTab,
  setActiveTab,
  onOpenScanner,
  onOpenCoach,
  onSearch,
  points,
  streak,
  level = 2
}) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [searchInput, setSearchInput] = useState('');

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (onSearch && searchInput.trim()) {
      onSearch(searchInput.trim());
    }
  };

  const navLinks = [
    { id: 'home', label: 'Dashboard', icon: Home },
    { id: 'showdown', label: 'Showdown Arena', icon: Swords },
    { id: 'alternatives', label: 'Healthy Swaps', icon: Apple },
    { id: 'rewards', label: 'Rewards & Leaderboard', icon: Trophy },
  ];

  return (
    <header className="sticky top-0 z-40 w-full glass-panel border-b border-slate-800/80 transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 gap-4">
          {/* Logo & Brand */}
          <div
            className="flex items-center gap-3 cursor-pointer shrink-0"
            onClick={() => setActiveTab('home')}
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 via-teal-400 to-cyan-400 flex items-center justify-center shadow-lg shadow-emerald-500/20 text-2xl font-bold">
              🥑
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-display font-black text-xl text-white tracking-tight">
                  Nutri<span className="text-emerald-400">Lens</span>
                </span>
                <span className="hidden sm:inline-block text-[10px] font-extrabold px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 uppercase tracking-wider">
                  Showdown
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-medium hidden md:block">
                AI Food Scanner & Healthy Snack Battle
              </p>
            </div>
          </div>

          {/* Desktop Search Bar */}
          <form
            onSubmit={handleSearchSubmit}
            className="hidden md:flex items-center flex-1 max-w-xs lg:max-w-sm relative"
          >
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 pointer-events-none" />
            <input
              type="text"
              placeholder="Search snack, brand, or barcode..."
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-slate-900/80 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all"
            />
          </form>

          {/* Desktop Navigation Links */}
          <nav className="hidden lg:flex items-center gap-1">
            {navLinks.map((link) => {
              const Icon = link.icon;
              const isActive = activeTab === link.id;
              return (
                <button
                  key={link.id}
                  onClick={() => setActiveTab(link.id)}
                  className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold transition-all ${
                    isActive
                      ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 shadow-sm'
                      : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{link.label}</span>
                </button>
              );
            })}
          </nav>

          {/* User Progress, AI Assistant & Scan CTA */}
          <div className="flex items-center gap-2.5">
            {/* Daily Streak */}
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-amber-500/10 border border-amber-500/25 text-amber-400 text-xs font-bold shadow-sm" title="Daily Streak">
              <Flame className="w-4 h-4 fill-amber-400 animate-pulse" />
              <span>{streak}d</span>
            </div>

            {/* XP Badge */}
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/25 text-emerald-400 text-xs font-bold shadow-sm" title="Total Health XP">
              <Sparkles className="w-4 h-4" />
              <span>{points} XP</span>
            </div>

            {/* AI Nutrition Coach Button */}
            <button
              onClick={onOpenCoach}
              className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-bold transition-all active:scale-95 shadow-sm"
              title="Open AI Nutrition Assistant"
            >
              <Bot className="w-4 h-4 text-emerald-400" />
              <span>AI Coach</span>
            </button>

            {/* Prominent Scan Food Button */}
            <button
              onClick={onOpenScanner}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-400 hover:from-emerald-400 hover:to-teal-300 text-slate-950 text-xs font-bold shadow-lg shadow-emerald-500/20 active:scale-95 transition-all"
            >
              <Scan className="w-4 h-4 stroke-[2.5]" />
              <span className="hidden sm:inline">Scan Snack</span>
            </button>

            {/* Mobile Hamburger Menu Toggle */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="lg:hidden p-2 rounded-xl bg-slate-800 text-slate-400 hover:text-white"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {/* Mobile Dropdown Menu */}
        {mobileMenuOpen && (
          <div className="lg:hidden py-3 border-t border-slate-800 space-y-2">
            <div className="grid grid-cols-2 gap-2 pb-2">
              {navLinks.map((link) => {
                const Icon = link.icon;
                const isActive = activeTab === link.id;
                return (
                  <button
                    key={link.id}
                    onClick={() => {
                      setActiveTab(link.id);
                      setMobileMenuOpen(false);
                    }}
                    className={`flex items-center gap-2 p-2.5 rounded-xl text-xs font-semibold ${
                      isActive
                        ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                        : 'text-slate-300 bg-slate-900/60'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{link.label}</span>
                  </button>
                );
              })}
            </div>
            <button
              onClick={() => {
                onOpenCoach();
                setMobileMenuOpen(false);
              }}
              className="w-full flex items-center justify-center gap-2 p-2.5 rounded-xl bg-slate-800 text-slate-200 text-xs font-bold"
            >
              <Bot className="w-4 h-4 text-emerald-400" />
              <span>Ask AI Nutrition Coach</span>
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
