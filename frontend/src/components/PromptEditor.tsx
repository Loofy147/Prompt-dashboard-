import React, { useState, useEffect, useCallback } from 'react';
import {
  Save, XCircle, Zap, Sparkles, Plus, History,
  Terminal, ShieldCheck, Cpu, ArrowRight, Lightbulb
} from 'lucide-react';
import QualityCalculator from './QualityCalculator';
import OptimizationPanel from './OptimizationPanel';
import _ from 'lodash';

interface Refinement {
  weakest_dimension: string;
  actionable_instruction: string;
  estimated_delta: number;
}

interface QualityScores {
  P: number;
  T: number;
  F: number;
  S: number;
  C: number;
  R: number;
}

interface PromptEditorProps {
  initialText?: string;
  initialTags?: string[];
  parentId?: number | null;
  onSave: () => void;
  onCancel: () => void;
}

const PromptEditor: React.FC<PromptEditorProps> = ({
  initialText = '',
  initialTags = [],
  parentId = null,
  onSave,
  onCancel
}) => {
  const [text, setText] = useState(initialText);
  const [tags, setTags] = useState<string[]>(initialTags);
  const [newTag, setNewTag] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [qualityScores, setQualityScores] = useState<QualityScores | null>(null);
  const [refinement, setRefinement] = useState<Refinement | null>(null);
  const [isRefining, setIsRefining] = useState(false);
  const [showActiveOptimizer, setShowActiveOptimizer] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);

  const maxChars = 10000;
  const charPercentage = (text.length / maxChars) * 100;

  const analyzeQuality = useCallback(
    _.debounce(async (promptText: string) => {
      if (!promptText.trim()) {
        setQualityScores(null);
        return;
      }
      setIsAnalyzing(true);
      try {
        const response = await fetch('/api/analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: promptText }),
        });
        const data = await response.json();
        setQualityScores(data.features);
      } catch (error) {
        console.error('Failed to analyze prompt:', error);
      } finally {
        setIsAnalyzing(false);
      }
    }, 500),
    []
  );

  useEffect(() => {
    analyzeQuality(text);
  }, [text, analyzeQuality]);

  // Keyboard shortcut listener
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
        if (text.trim()) {
          handleSave();
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [text, tags, parentId]);

  const handleAddTag = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && newTag.trim() && !tags.includes(newTag.trim())) {
      setTags([...tags, newTag.trim()]);
      setNewTag('');
    }
  };

  const removeTag = (tagToRemove: string) => {
    setTags(tags.filter(t => t !== tagToRemove));
  };

  const handleSave = async () => {
    try {
      const response = await fetch('/api/prompts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text,
          tags,
          parent_id: parentId
        }),
      });
      if (response.ok) {
        setLastSaved(new Date());
        onSave();
      }
    } catch (error) {
      console.error('Failed to save prompt:', error);
    }
  };

  const handleRefine = async () => {
    setIsRefining(true);
    try {
      const response = await fetch('/api/prompts/1/variants', { // Mocking variant engine call
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      });
      // Logic for refinement tip would normally come from specialized endpoint
      setRefinement({
        weakest_dimension: 'Specificity (S)',
        actionable_instruction: 'Add quantified metrics like "latency < 200ms" or "exactly 5 sections" to improve clarity.',
        estimated_delta: 0.12
      });
    } catch (error) {
      console.error('Failed to get refinement:', error);
    } finally {
      setIsRefining(false);
    }
  };

  const currentQ = qualityScores ? (
    0.18 * qualityScores.P + 0.22 * qualityScores.T + 0.20 * qualityScores.F +
    0.18 * qualityScores.S + 0.12 * qualityScores.C + 0.10 * qualityScores.R
  ) : 0;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      {/* Left: Editor */}
      <div className="lg:col-span-2 flex flex-col h-full">
        {/* Version Breadcrumb */}
        <div className="flex items-center gap-2 mb-6 bg-gray-50 px-4 py-2 rounded-xl border border-gray-100 self-start">
          <History size={14} className="text-gray-400" />
          <span className="text-[10px] font-black text-gray-400 uppercase tracking-widest">Lineage:</span>
          <div className="flex items-center gap-1.5">
            {parentId && (
              <>
                <span className="text-[10px] font-bold text-indigo-400">#{parentId}</span>
                <ArrowRight size={10} className="text-gray-300" />
              </>
            )}
            <span className="text-[10px] font-black text-indigo-600 bg-indigo-50 px-1.5 py-0.5 rounded">NEW VERSION</span>
          </div>
        </div>

        {/* Auto-Insight Banner (UX Improvement) */}
        {qualityScores && currentQ < 0.85 && (
           <div className="mb-6 p-4 bg-gradient-to-r from-indigo-600 to-palette-primary rounded-2xl text-white shadow-lg shadow-indigo-200 flex items-center justify-between animate-in fade-in slide-in-from-top-4 duration-500">
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-md">
                  <Lightbulb className="text-bolt-light" size={20} />
                </div>
                <div>
                  <h4 className="text-xs font-black uppercase tracking-widest leading-none mb-1">PRO-INSIGHT: RAISE Q TO 0.90</h4>
                  <p className="text-sm font-medium opacity-90">Increase Specificity by adding quantified metrics.</p>
                </div>
              </div>
              <button
                onClick={handleRefine}
                className="bg-white text-indigo-600 px-4 py-2 rounded-lg text-xs font-black uppercase hover:bg-gray-50 transition-colors"
              >
                APPLY BOLT TIP
              </button>
           </div>
        )}

        <div className="flex items-center justify-between mb-2">
          <label htmlFor="prompt-text" className="text-[10px] font-black text-gray-500 uppercase tracking-widest flex items-center gap-1.5">
            <Terminal size={12} /> Computational Directive
          </label>
          <div className="flex items-center gap-2">
            <span className={`text-[10px] font-bold ${charPercentage > 90 ? 'text-rose-500' : 'text-gray-400'}`}>
              {text.length.toLocaleString()} / {maxChars.toLocaleString()}
            </span>
            <div className="w-20 h-1 bg-gray-100 rounded-full overflow-hidden">
              <div
                className={`h-full transition-all ${
                  charPercentage > 90 ? 'bg-rose-500' :
                  charPercentage > 75 ? 'bg-amber-500' :
                  'bg-emerald-500'
                }`}
                style={{ width: `${Math.min(charPercentage, 100)}%` }}
              />
            </div>
          </div>
        </div>

        <div className="relative flex-1 group">
          <textarea
            id="prompt-text"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Enter your prompt instructions..."
            maxLength={maxChars}
            className="w-full h-full p-6 border border-gray-200 rounded-3xl focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 font-mono text-sm resize-none min-h-[400px] shadow-inner bg-gray-50/30 transition-all group-hover:bg-white"
            aria-label="Prompt text editor"
          />
          <div className="absolute right-4 bottom-4 flex gap-2">
             <div className="px-2 py-1 bg-gray-900/5 text-[8px] font-black text-gray-400 rounded-lg uppercase tracking-tighter">
                Ctrl + Enter to Save
             </div>
          </div>
        </div>

        {/* Tags Section */}
        <div className="mt-8 bg-white p-6 rounded-3xl border border-gray-100 shadow-sm">
          <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-4 block flex items-center gap-1.5">
            <ShieldCheck size={12} /> Taxonomical Classifiers
          </label>
          <div className="flex flex-wrap gap-2 mb-4">
            {tags.map(tag => (
              <span
                key={tag}
                className="inline-flex items-center gap-2 px-3 py-1.5 bg-gray-100 text-gray-700 rounded-xl text-xs font-bold border border-gray-200"
              >
                {tag}
                <button
                  onClick={() => removeTag(tag)}
                  className="hover:bg-rose-100 hover:text-rose-600 rounded-lg p-0.5 transition-colors"
                  aria-label={`Remove ${tag} tag`}
                >
                  <XCircle size={14} />
                </button>
              </span>
            ))}
            <div className="relative">
              <input
                type="text"
                value={newTag}
                onChange={(e) => setNewTag(e.target.value)}
                onKeyDown={handleAddTag}
                placeholder="Add classification..."
                className="px-4 py-1.5 border border-dashed border-gray-300 rounded-xl text-xs font-bold focus:ring-2 focus:ring-indigo-500 outline-none w-48"
                disabled={tags.length >= 10}
              />
              <Plus size={14} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400" />
            </div>
          </div>
          <p className="text-[10px] font-bold text-gray-300 uppercase">{tags.length} / 10 slots filled</p>
        </div>

        {/* Improved Action Bar */}
        <div className="flex flex-wrap items-center gap-4 mt-8 p-2 bg-gray-50 rounded-2xl border border-gray-100">
          <button
            onClick={handleSave}
            disabled={!text.trim()}
            className="flex items-center gap-2 px-8 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed font-black text-xs uppercase shadow-xl shadow-indigo-200 transition-all active:scale-95"
          >
            <Save size={18} /> {parentId ? 'COMMIT VERSION' : 'PUBLISH PROMPT'}
          </button>

          <div className="w-px h-8 bg-gray-200"></div>

          <button
            onClick={() => setShowActiveOptimizer(true)}
            disabled={!text.trim()}
            className="flex items-center gap-2 px-6 py-3 bg-palette-dark text-white rounded-xl hover:bg-gray-900 disabled:opacity-50 font-black text-xs uppercase transition-all active:scale-95"
          >
            <Sparkles size={18} className="text-bolt-light" /> ACTIVE OPTIMIZE
          </button>

          <button
            onClick={onCancel}
            className="flex items-center gap-2 px-6 py-3 bg-white text-gray-400 border border-gray-200 rounded-xl hover:bg-gray-50 font-black text-xs uppercase transition-all"
          >
             Back to Library
          </button>
        </div>
      </div>

      {/* Right: Quality Index Panel */}
      <div className="lg:col-span-1">
        <div className="sticky top-6">
          <QualityCalculator
            scores={qualityScores}
            isLoading={isAnalyzing}
          />

          <div className="mt-6 p-6 bg-gradient-to-br from-gray-900 to-indigo-900 rounded-3xl text-white shadow-2xl shadow-indigo-100">
             <div className="flex items-center gap-3 mb-4">
                <Cpu size={24} className="text-bolt-light" />
                <h3 className="text-sm font-black uppercase tracking-[0.1em]">Engine Telemetry</h3>
             </div>
             <div className="space-y-3">
                <div className="flex justify-between text-[10px] font-bold">
                   <span className="text-gray-400 uppercase">Input Tokens (est)</span>
                   <span className="text-bolt-light font-mono">{Math.ceil(text.length / 4)}</span>
                </div>
                <div className="flex justify-between text-[10px] font-bold">
                   <span className="text-gray-400 uppercase">Inference Mode</span>
                   <span className="text-emerald-400 uppercase">BOLT-OPTIMIZED</span>
                </div>
             </div>
          </div>
        </div>

        {/* Modal Overlay */}
        {showActiveOptimizer && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-gray-900/60 backdrop-blur-md animate-in fade-in duration-300">
            <div className="w-full max-w-4xl max-h-[90vh] overflow-y-auto">
              <OptimizationPanel
                promptId={parentId || null}
                promptText={text}
                currentQ={currentQ}
                onOptimized={(newText) => {
                  setText(newText);
                }}
                onClose={() => setShowActiveOptimizer(false)}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PromptEditor;
