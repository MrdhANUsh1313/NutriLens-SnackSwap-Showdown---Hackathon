import React, { useState } from 'react';
import { X, Bot, Send, Sparkles, User } from 'lucide-react';
import { askAIChat } from '../services/api';

export default function AICoachModal({ isOpen, onClose, currentProduct }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      text: "👋 Hey there! I'm your NutriLens AI Coach. Ask me anything about food labels, deceptive ingredients (like maltodextrin or palm oil), or finding healthier Indian snacks!"
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const quickPrompts = [
    "Why is Palm Oil so common in chips?",
    "What does Maltodextrin do to blood sugar?",
    "Suggest a high-protein 4 PM Indian snack",
    "How to spot hidden sugars on labels?"
  ];

  const handleSend = async (questionText) => {
    const q = questionText || input;
    if (!q.trim() || loading) return;

    const userMsg = { role: 'user', text: q };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await askAIChat(q, currentProduct);
      setMessages(prev => [...prev, { role: 'assistant', text: res.response }]);
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        text: "I couldn't fetch an online answer right now, but remember: prioritize snacks with high fiber (>5g) and low added sugar (<5g) per 100g!"
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
      <div className="w-full max-w-md glass-card rounded-3xl overflow-hidden border border-slate-700/60 flex flex-col h-[85vh]">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-slate-800">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 text-slate-950">
              <Bot className="w-5 h-5 font-bold" />
            </div>
            <div>
              <h3 className="font-display font-bold text-sm text-white">NutriLens AI Assistant</h3>
              <p className="text-[11px] text-emerald-400 font-medium">Smart Nutrition & Ingredient Explainer</p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 rounded-full bg-slate-800 text-slate-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Chat message stream */}
        <div className="flex-1 p-4 overflow-y-auto space-y-3">
          {messages.map((m, idx) => (
            <div key={idx} className={`flex gap-2.5 ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              {m.role === 'assistant' && (
                <div className="w-7 h-7 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center shrink-0 text-xs font-bold mt-1">
                  🥑
                </div>
              )}
              <div className={`p-3 rounded-2xl text-xs max-w-[85%] leading-relaxed ${
                m.role === 'user'
                  ? 'bg-emerald-500 text-slate-950 font-medium rounded-tr-none'
                  : 'bg-slate-900 border border-slate-800 text-slate-200 rounded-tl-none whitespace-pre-line'
              }`}>
                {m.text}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex items-center gap-2 text-xs text-slate-400 italic">
              <Sparkles className="w-4 h-4 text-emerald-400 animate-spin" />
              NutriLens AI is analyzing nutrition facts...
            </div>
          )}
        </div>

        {/* Quick prompt pills */}
        <div className="p-2.5 border-t border-slate-800/80 bg-slate-900/40 flex gap-2 overflow-x-auto no-scrollbar">
          {quickPrompts.map((p, i) => (
            <button
              key={i}
              onClick={() => handleSend(p)}
              className="text-[10px] whitespace-nowrap px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 hover:bg-slate-700 hover:text-emerald-400 border border-slate-700/60 transition-all shrink-0"
            >
              {p}
            </button>
          ))}
        </div>

        {/* Input box */}
        <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="p-3 border-t border-slate-800 flex gap-2">
          <input
            type="text"
            placeholder="Ask about ingredients, oils, or swaps..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="flex-1 bg-slate-900 border border-slate-700 rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="p-2.5 bg-emerald-500 hover:bg-emerald-600 disabled:opacity-40 text-slate-950 rounded-xl transition-all"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
}
