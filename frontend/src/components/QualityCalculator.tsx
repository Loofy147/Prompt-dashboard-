import React from 'react';

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
      <div className="p-6 bg-white rounded-lg border border-gray-200 shadow-sm animate-pulse">
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
      <div className="p-6 bg-white rounded-lg border border-gray-200 shadow-sm text-center">
        <p className="text-gray-500 italic">Enter some text to see quality analysis</p>
      </div>
    );
  }

  const WEIGHTS = { P: 0.18, T: 0.22, F: 0.20, S: 0.18, C: 0.12, R: 0.10 };

  const Q = Object.entries(scores).reduce((acc, [key, val]) => {
    return acc + (val * (WEIGHTS[key as keyof QualityScores] || 0));
  }, 0);

  const getLevel = (score: number) => {
    if (score >= 0.90) return { label: 'Excellent', color: 'text-green-600', bg: 'bg-green-100', bar: 'bg-green-500' };
    if (score >= 0.80) return { label: 'Good', color: 'text-blue-600', bg: 'bg-blue-100', bar: 'bg-blue-500' };
    if (score >= 0.70) return { label: 'Fair', color: 'text-yellow-600', bg: 'bg-yellow-100', bar: 'bg-yellow-500' };
    return { label: 'Poor', color: 'text-red-600', bg: 'bg-red-100', bar: 'bg-red-500' };
  };

  const level = getLevel(Q);

  const dimensions = [
    { key: 'P', name: 'Persona', weight: 0.18 },
    { key: 'T', name: 'Tone', weight: 0.22 },
    { key: 'F', name: 'Format', weight: 0.20 },
    { key: 'S', name: 'Specificity', weight: 0.18 },
    { key: 'C', name: 'Constraints', weight: 0.12 },
    { key: 'R', name: 'Context', weight: 0.10 },
  ];

  return (
    <div className="p-6 bg-white rounded-lg border border-gray-200 shadow-sm">
      <div className="flex justify-between items-end mb-6">
        <div>
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">Quality Score (Q)</h2>
          <div className="text-4xl font-bold mt-1">{Q.toFixed(4)}</div>
        </div>
        <div className={`px-3 py-1 rounded-full text-xs font-bold uppercase ${level.bg} ${level.color}`}>
          {level.label}
        </div>
      </div>

      <div className="space-y-4">
        {dimensions.map(dim => {
          const score = scores[dim.key as keyof QualityScores];
          const dimLevel = getLevel(score);
          return (
            <div key={dim.key}>
              <div className="flex justify-between text-xs mb-1">
                <span className="font-medium text-gray-700">{dim.name}</span>
                <span className="text-gray-500">{score.toFixed(2)} × {dim.weight}</span>
              </div>
              <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className={`h-full transition-all duration-500 ${dimLevel.bar}`}
                  style={{ width: `${score * 100}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-8 pt-6 border-t border-gray-100">
        <h3 className="text-xs font-semibold text-gray-500 uppercase mb-3">Formula Breakdown</h3>
        <div className="text-[10px] font-mono text-gray-400 break-all">
          Q = {dimensions.map((dim, i) => (
            <span key={dim.key}>
              (0.18×{scores[dim.key as keyof QualityScores].toFixed(2)})
              {i < dimensions.length - 1 ? ' + ' : ''}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};

export default QualityCalculator;
