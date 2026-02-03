import React, { useState } from 'react';
import { Zap, DollarSign, TrendingUp, X } from 'lucide-react';

export interface OptimizationIteration {
  iteration_number: number;
  prompt_text: string;
  features: Record<string, number>;
  q_score: number;
  improved_dimensions: string[];
  cost_usd: number;
  tokens_used: number;
  latency_ms: number;
}

export interface OptimizationResult {
  original_prompt: string;
  optimized_prompt: string;
  original_q: number;
  optimized_q: number;
  delta_q: number;
  improvement_pct: number;
  total_cost_usd: number;
  total_tokens: number;
  iterations: OptimizationIteration[];
  dimensions_improved: Record<string, [number, number]>;
}

export interface CostEstimate {
  estimated_iterations: number;
  estimated_total_tokens: number;
  estimated_cost_usd: number;
  cost_breakdown: any[];
}

export const optimizePrompt = async (
  promptId: number | null,
  promptText: string | null,
  options: {
    targetQuality?: number;
    strategy?: 'balanced' | 'cost_efficient' | 'max_quality';
    estimateOnly?: boolean;
    saveAsNew?: boolean;
  } = {}
): Promise<OptimizationResult | CostEstimate> => {
  const url = promptId ? `/api/prompts/${promptId}/optimize` : (options.estimateOnly ? '/api/optimize/estimate' : '/api/optimize');
  const body = {
    target_quality: options.targetQuality || 0.85,
    strategy: options.strategy || 'balanced',
    estimate_only: options.estimateOnly || false,
    save_as_new: options.saveAsNew || false,
    text: promptId ? undefined : promptText
  };

  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });

  if (!response.ok) {
    throw new Error('Optimization failed');
  }

  return response.json();
};

interface OptimizationPanelProps {
  promptId: number | null;
  promptText: string;
  currentQ: number;
  onOptimized?: (newText: string) => void;
  onClose?: () => void;
}

const OptimizationPanel: React.FC<OptimizationPanelProps> = ({
  promptId,
  promptText,
  currentQ,
  onOptimized,
  onClose
}) => {
  const [targetQ, setTargetQ] = useState(0.85);
  const [strategy, setStrategy] = useState<'balanced' | 'cost_efficient' | 'max_quality'>('balanced');
  const [estimate, setEstimate] = useState<CostEstimate | null>(null);
  const [result, setResult] = useState<OptimizationResult | null>(null);
  const [loading, setLoading] = useState(false);

  const handleEstimate = async () => {
    setLoading(true);
    try {
      const est = await optimizePrompt(promptId, promptText, {
        targetQuality: targetQ,
        strategy,
        estimateOnly: true
      }) as CostEstimate;
      setEstimate(est);
    } catch (error) {
      console.error('Estimation failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleOptimize = async () => {
    setLoading(true);
    try {
      const res = await optimizePrompt(promptId, promptText, {
        targetQuality: targetQ,
        strategy,
        saveAsNew: !!promptId
      }) as OptimizationResult;
      setResult(res);
      if (onOptimized) {
        onOptimized(res.optimized_prompt);
      }
    } catch (error) {
      console.error('Optimization failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-2xl p-6 border border-palette-primary/20 relative animate-in fade-in zoom-in duration-300">
      <button
        onClick={onClose}
        className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 transition-colors"
      >
        <X size={20} />
      </button>

      <div className="flex items-center gap-2 mb-6">
        <div className="w-10 h-10 bg-palette-primary/10 rounded-xl flex items-center justify-center">
          <Zap className="text-palette-primary" size={24} />
        </div>
        <div>
          <h2 className="text-xl font-black text-palette-dark tracking-tight">AI ACTIVE OPTIMIZER</h2>
          <p className="text-[10px] text-gray-400 font-bold uppercase tracking-widest">LLM-Powered Refinement Engine</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-6">
          {/* Current Quality */}
          <div className="p-4 bg-gray-50 rounded-xl border border-gray-100">
            <div className="text-[10px] text-gray-400 font-bold uppercase mb-1">Current Base Quality</div>
            <div className="text-3xl font-black text-palette-primary tracking-tighter">
              Q = {currentQ.toFixed(4)}
            </div>
          </div>

          {/* Settings */}
          <div className="space-y-4">
            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="text-sm font-bold text-gray-700">Target Quality</label>
                <span className="text-sm font-black text-palette-primary bg-palette-primary/10 px-2 py-0.5 rounded-lg">
                  {targetQ.toFixed(2)}
                </span>
              </div>
              <input
                type="range"
                min="0.70"
                max="0.95"
                step="0.05"
                value={targetQ}
                onChange={(e) => setTargetQ(parseFloat(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-palette-primary"
              />
            </div>

            <div>
              <label className="block text-sm font-bold text-gray-700 mb-2">Optimization Strategy</label>
              <select
                value={strategy}
                onChange={(e) => setStrategy(e.target.value as any)}
                className="w-full px-3 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-palette-primary outline-none font-medium text-gray-700 transition-all"
              >
                <option value="cost_efficient">💰 Cost Efficient (~$0.05)</option>
                <option value="balanced">⚖️ Balanced (~$0.20)</option>
                <option value="max_quality">🏆 Max Quality (~$0.50)</option>
              </select>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-2">
            <button
              onClick={handleEstimate}
              disabled={loading}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-gray-100 text-gray-700 rounded-xl hover:bg-gray-200 font-bold text-sm disabled:opacity-50 transition-all active:scale-95"
            >
              <DollarSign size={18} />
              ESTIMATE
            </button>

            <button
              onClick={handleOptimize}
              disabled={loading}
              className="flex-2 flex items-center justify-center gap-2 px-4 py-3 bg-palette-primary text-white rounded-xl hover:bg-palette-primary/90 font-bold text-sm shadow-xl shadow-palette-primary/30 disabled:opacity-50 transition-all active:scale-95"
            >
              <Zap size={18} className={loading ? 'animate-pulse' : ''} />
              {loading ? 'PROCESSING...' : 'START OPTIMIZATION'}
            </button>
          </div>
        </div>

        <div className="flex flex-col h-full">
          {/* Cost Estimate */}
          {estimate && !result && (
            <div className="h-full flex flex-col justify-center p-6 bg-blue-50 border border-blue-100 rounded-2xl animate-in fade-in slide-in-from-right-4 duration-500">
              <h3 className="font-black text-blue-900 mb-4 flex items-center gap-2 uppercase tracking-tighter text-lg">
                 <DollarSign size={20} className="text-blue-600" /> Pre-Flight Estimate
              </h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center pb-2 border-b border-blue-200">
                  <span className="text-sm text-blue-700 font-medium">Refinement Iterations</span>
                  <span className="font-black text-blue-900">{estimate.estimated_iterations}</span>
                </div>
                <div className="flex justify-between items-center pb-2 border-b border-blue-200">
                  <span className="text-sm text-blue-700 font-medium">Est. Token Volume</span>
                  <span className="font-black text-blue-900">{estimate.estimated_total_tokens.toLocaleString()}</span>
                </div>
                <div className="pt-2">
                  <div className="text-[10px] text-blue-400 font-bold uppercase mb-1">Total Estimated Cost</div>
                  <div className="text-3xl font-black text-blue-700 tracking-tighter">
                    ${estimate.estimated_cost_usd.toFixed(4)}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Results */}
          {result && (
            <div className="h-full p-6 bg-green-50 border border-green-100 rounded-2xl animate-in fade-in slide-in-from-right-4 duration-500 overflow-y-auto max-h-[400px]">
              <div className="flex items-center gap-2 mb-4">
                <TrendingUp className="text-green-600" size={24} />
                <h3 className="font-black text-green-900 uppercase tracking-tighter text-lg">Success!</h3>
              </div>

              <div className="grid grid-cols-2 gap-3 mb-6">
                <div className="p-3 bg-white rounded-xl border border-green-100 shadow-sm">
                  <div className="text-[10px] text-gray-400 uppercase font-black">Final Quality</div>
                  <div className="text-2xl font-black text-green-600 tracking-tighter">
                    {result.optimized_q.toFixed(4)}
                  </div>
                </div>
                <div className="p-3 bg-white rounded-xl border border-green-100 shadow-sm">
                  <div className="text-[10px] text-gray-400 uppercase font-black">Net Gain</div>
                  <div className="text-2xl font-black text-palette-primary tracking-tighter">
                    +{result.delta_q.toFixed(4)}
                  </div>
                </div>
              </div>

              <div className="space-y-2 mb-6 text-xs">
                <div className="flex justify-between text-gray-600">
                  <span className="font-medium">Actual Investment:</span>
                  <span className="font-black text-gray-900">${result.total_cost_usd.toFixed(4)}</span>
                </div>
                <div className="flex justify-between text-gray-600">
                  <span className="font-medium">Total Tokens:</span>
                  <span className="font-black text-gray-900">{result.total_tokens?.toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-gray-600">
                  <span className="font-medium">Refinement Cycles:</span>
                  <span className="font-black text-gray-900">{result.iterations.length}</span>
                </div>
              </div>

              <div className="pt-4 border-t border-green-200">
                <div className="text-[10px] font-black text-gray-400 uppercase mb-2">Optimized Directive Preview</div>
                <div className="p-3 bg-white rounded-xl border border-gray-200 text-[11px] font-mono leading-relaxed whitespace-pre-wrap max-h-40 overflow-y-auto">
                  {result.optimized_prompt}
                </div>
              </div>
            </div>
          )}

          {!estimate && !result && (
            <div className="h-full flex flex-col items-center justify-center p-8 bg-gray-50 border border-dashed border-gray-200 rounded-2xl text-center">
              <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center shadow-sm mb-4">
                <DollarSign className="text-gray-300" size={24} />
              </div>
              <h3 className="text-sm font-bold text-gray-500 mb-1">Ready for Refinement</h3>
              <p className="text-xs text-gray-400 max-w-[200px]">Adjust your target and strategy to see cost estimates.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default OptimizationPanel;
