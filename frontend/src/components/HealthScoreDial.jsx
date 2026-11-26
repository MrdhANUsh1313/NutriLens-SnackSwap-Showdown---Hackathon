import React from 'react';
import { ShieldCheck, AlertTriangle, AlertCircle } from 'lucide-react';

export default function HealthScoreDial({ score = 50, grade = 'C', classification = 'Moderate', size = 120 }) {
  // Determine color and status
  let strokeColor = '#eab308';
  let bgColor = 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30';
  let StatusIcon = AlertTriangle;

  if (score >= 80) {
    strokeColor = '#10b981';
    bgColor = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
    StatusIcon = ShieldCheck;
  } else if (score >= 60) {
    strokeColor = '#22c55e';
    bgColor = 'bg-green-500/10 text-green-400 border-green-500/30';
    StatusIcon = ShieldCheck;
  } else if (score >= 40) {
    strokeColor = '#eab308';
    bgColor = 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30';
    StatusIcon = AlertTriangle;
  } else if (score >= 20) {
    strokeColor = '#f97316';
    bgColor = 'bg-orange-500/10 text-orange-400 border-orange-500/30';
    StatusIcon = AlertCircle;
  } else {
    strokeColor = '#ef4444';
    bgColor = 'bg-red-500/10 text-red-400 border-red-500/30';
    StatusIcon = AlertCircle;
  }

  const radius = 45;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className="flex flex-col items-center">
      <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
        <svg className="w-full h-full -rotate-90 transform" viewBox="0 0 100 100">
          {/* Background circle track */}
          <circle
            cx="50"
            cy="50"
            r={radius}
            className="stroke-slate-800"
            strokeWidth="8"
            fill="transparent"
          />
          {/* Progress circle */}
          <circle
            cx="50"
            cy="50"
            r={radius}
            stroke={strokeColor}
            strokeWidth="8"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
            className="transition-all duration-1000 ease-out"
          />
        </svg>

        {/* Center Score & Grade */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="font-display font-extrabold text-3xl tracking-tight text-white leading-none">
            {score}
          </span>
          <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider mt-0.5">
            / 100
          </span>
        </div>
      </div>

      {/* Grade Badge */}
      <div className={`mt-2 flex items-center gap-1.5 px-3 py-1 rounded-full border text-xs font-bold ${bgColor}`}>
        <StatusIcon className="w-3.5 h-3.5" />
        <span>Grade {grade} • {classification}</span>
      </div>
    </div>
  );
}
