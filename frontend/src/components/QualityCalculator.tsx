// @ts-nocheck
import React from 'react';
import {
  Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  ResponsiveContainer, Tooltip as ChartTooltip
} from 'recharts';

interface QualityScores {
  P: number;
  T: number;
  F: number;
  S: number;
  C: number;
  R: number;
}

interface QualityCalculatorProps {
  scores: QualityScores | null;
  isLoading: boolean;
}

const QualityCalculator: React.FC<QualityCalculatorProps> = ({ scores, isLoading }) => {
  if (isLoading) {
    return (
      <div className="p-6 bg-white rounded-2xl border border-gray-200 shadow-sm animate-pulse">
        <div className="h-8 bg-gray-200 rounded w-1/2 mb-6"></div>
        {[1, 2, 3, 4, 5, 6].map(i => (
          <div key={i} className="mb-4">
            <div className="h-4 bg-gray-100 rounded w-1/4 mb-2"></div>
            <div className="h-2 bg-gray-100 rounded w-full"></div>
          </div>
        ))}
      </div>
    );
  }

  if (!scores) {
    return (
      <div className="p-6 bg-white rounded-2xl border border-gray-200 shadow-sm text-center">
        <p className="text-gray-500 italic">Enter some text to see quality analysis</p>
      </div>
    );
  }

  const WEIGHTS = { P: 0.18, T: 0.22, F: 0.20, S: 0.18, C: 0.12, R: 0.10 };

  const Q = Object.entries(scores).reduce((acc, [key, val]) => {
    return acc + (val * (WEIGHTS[key as keyof QualityScores] || 0));
  }, 0);

  const getLevel = (score: number) => {
    if (score >= 0.90) return { label: 'Excellent', color: 'text-emerald-600', bg: 'bg-emerald-50', bar: 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]' };
    if (score >= 0.80) return { label: 'Good', color: 'text-indigo-600', bg: 'bg-indigo-50', bar: 'bg-indigo-500 shadow-[0_0_8px_rgba(99,102,241,0.5)]' };
    if (score >= 0.70) return { label: 'Fair', color: 'text-amber-600', bg: 'bg-amber-50', bar: 'bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.5)]' };
    return { label: 'Poor', color: 'text-rose-600', bg: 'bg-rose-50', bar: 'bg-rose-500 shadow-[0_0_8px_rgba(236,72,153,0.5)]' };
  };

  const level = getLevel(Q);

  const radarData = [
    { subject: 'Persona', A: scores.P, fullMark: 1 },
    { subject: 'Tone', A: scores.T, fullMark: 1 },
    { subject: 'Format', A: scores.F, fullMark: 1 },
    { subject: 'Specificity', A: scores.S, fullMark: 1 },
    { subject: 'Constraints', A: scores.C, fullMark: 1 },
    { subject: 'Context', A: scores.R, fullMark: 1 },
  ];

  const dimensions = [
    { key: 'P', name: 'Persona', weight: 0.18 },
    { key: 'T', name: 'Tone', weight: 0.22 },
    { key: 'F', name: 'Format', weight: 0.20 },
    { key: 'S', name: 'Specificity', weight: 0.18 },
    { key: 'C', name: 'Constraints', weight: 0.12 },
    { key: 'R', name: 'Context', weight: 0.10 },
  ];

  return (
    <div className="p-6 bg-white rounded-2xl border border-gray-100 shadow-xl shadow-gray-200/20">
      <div className="flex justify-between items-start mb-6">
        <div>
          <h2 className="text-[10px] font-black text-gray-400 uppercase tracking-widest leading-none mb-1">PES QUALITY INDEX</h2>
          <div className="text-5xl font-black bg-clip-text text-transparent bg-gradient-to-br from-gray-900 to-indigo-600 tracking-tighter">
            {Q.toFixed(4)}
          </div>
        </div>
        <div className={`px-4 py-1.5 rounded-xl text-xs font-black uppercase tracking-widest ${level.bg} ${level.color}`}>
          {level.label}
        </div>
      </div>

      {/* Radar Chart Visualization */}
      <div className="h-64 mb-8 bg-gray-50/50 rounded-2xl border border-gray-50 flex items-center justify-center p-2">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
            <PolarGrid stroke="#e5e7eb" />
            <PolarAngleAxis dataKey="subject" tick={{ fontSize: 10, fontWeight: 700, fill: '#9ca3af' }} />
            <PolarRadiusAxis angle={30} domain={[0, 1]} tick={false} axisLine={false} />
            <Radar
              name="PES Score"
              dataKey="A"
              stroke="#6366f1"
              fill="#6366f1"
              fillOpacity={0.6}
            />
            <ChartTooltip />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      <div className="space-y-4">
        {dimensions.map(dim => {
          const score = scores[dim.key as keyof QualityScores];
          const dimLevel = getLevel(score);
          return (
            <div key={dim.key}>
              <div className="flex justify-between text-[10px] mb-1">
                <span className="font-bold text-gray-600 uppercase tracking-tight">{dim.name}</span>
                <span className="text-gray-400 font-mono">{score.toFixed(2)} × {dim.weight}</span>
              </div>
              <div className="w-full h-1.5 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className={`h-full transition-all duration-700 ease-out ${dimLevel.bar}`}
                  style={{ width: `${score * 100}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-8 pt-6 border-t border-gray-100">
        <h3 className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-3">Mathematical Breakdown</h3>
        <div className="p-3 bg-gray-50 rounded-xl font-mono text-[9px] text-gray-400 leading-relaxed overflow-x-auto whitespace-nowrap">
          Q = {dimensions.map((dim, i) => (
            <span key={dim.key}>
              ({dim.weight}×<span className="text-indigo-500 font-bold">{scores[dim.key as keyof QualityScores].toFixed(2)}</span>)
              {i < dimensions.length - 1 ? ' + ' : ''}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};

export default QualityCalculator;
