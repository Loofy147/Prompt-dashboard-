import React, { useState, useEffect, useCallback } from 'react';
import { debounce } from 'lodash';
import QualityCalculator from './QualityCalculator';
import OptimizationPanel from './OptimizationPanel';
import { Zap, Sparkles, Save, XCircle } from 'lucide-react';

interface PromptEditorProps {
  initialText?: string;
  initialTags?: string[];
  parentId?: number;
  onSave?: (data: { text: string; tags: string[] }) => void;
  onCancel?: () => void;
}

interface QualityScores {
  P: number; // Persona
  T: number; // Tone
  F: number; // Format
  S: number; // Specificity
  C: number; // Constraints
  R: number; // Context
}

const PromptEditor: React.FC<PromptEditorProps> = ({
  initialText = '',
  initialTags = [],
  parentId,
  onSave,
  onCancel
}) => {
  const [text, setText] = useState(initialText);
  const [tags, setTags] = useState<string[]>(initialTags);
  const [newTag, setNewTag] = useState('');
  const [qualityScores, setQualityScores] = useState<QualityScores | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [refinement, setRefinement] = useState<{
    weakest_dimension: string;
    actionable_instruction: string;
  } | null>(null);
  const [isRefining, setIsRefining] = useState(false);
  const [showActiveOptimizer, setShowActiveOptimizer] = useState(false);

  // Debounced quality analysis when text changes
  const analyzeQuality = useCallback(
    debounce(async (promptText: string) => {
      if (!promptText.trim()) {
        setQualityScores(null);
        return;
      }

      setIsAnalyzing(true);
      try {
        // Call backend API to analyze prompt
        const response = await fetch('/api/analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: promptText })
        });

        const data = await response.json();
        setQualityScores(data.features);
      } catch (error) {
        console.error('Quality analysis failed:', error);
      } finally {
        setIsAnalyzing(false);
      }
    }, 250), // Bolt ⚡ faster debounce
    []
  );

  // Trigger analysis when text changes
  useEffect(() => {
    analyzeQuality(text);
    setRefinement(null); // Reset refinement when text changes
  }, [text, analyzeQuality]);

  const handleRefine = async () => {
    if (!text.trim()) return;
    setIsRefining(true);
    try {
      const response = await fetch('/api/prompts/refine', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      });
      const data = await response.json();
      setRefinement(data);
    } catch (error) {
      console.error('Refinement failed:', error);
    } finally {
      setIsRefining(false);
    }
  };

  // Character counter
  const charCount = text.length;
  const maxChars = 10000;
  const charPercentage = (charCount / maxChars) * 100;

  // Handle tag addition
  const handleAddTag = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && newTag.trim()) {
      e.preventDefault();
      if (!tags.includes(newTag.trim()) && tags.length < 10) {
        setTags([...tags, newTag.trim()]);
        setNewTag('');
      }
    }
  };

  // Handle tag removal
  const removeTag = (tagToRemove: string) => {
    setTags(tags.filter(tag => tag !== tagToRemove));
  };

  // Save handler
  const handleSave = async () => {
    try {
      const response = await fetch('/api/prompts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text,
          tags,
          parent_id: parentId
        })
      });

      if (response.ok) {
        if (onSave) {
          onSave({ text, tags });
        }
        setLastSaved(new Date());
      }
    } catch (error) {
      console.error('Failed to save prompt:', error);
    }
  };

  // Keyboard shortcut for save (Cmd+S / Ctrl+S)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 's') {
        e.preventDefault();
        handleSave();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [text, tags]);

  const WEIGHTS = { P: 0.18, T: 0.22, F: 0.20, S: 0.18, C: 0.12, R: 0.10 };
  const currentQ = qualityScores ? Object.entries(qualityScores).reduce((acc, [key, val]) => {
    return acc + (val * (WEIGHTS[key as keyof typeof WEIGHTS] || 0));
  }, 0) : 0;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full relative">
      {/* Left: Editor */}
      <div className="lg:col-span-2 flex flex-col">
        <div className="mb-2 flex justify-between items-center">
          <label htmlFor="prompt-text" className="text-sm font-medium text-gray-700">
            Prompt Text ({charCount.toLocaleString()}/{maxChars.toLocaleString()} chars)
          </label>
          <div className="w-32 h-1.5 bg-gray-200 rounded-full overflow-hidden">
            <div
              className={`h-full transition-all ${
                charPercentage > 90 ? 'bg-red-500' :
                charPercentage > 75 ? 'bg-yellow-500' :
                'bg-green-500'
              }`}
              style={{ width: `${Math.min(charPercentage, 100)}%` }}
            />
          </div>
        </div>

        <textarea
          id="prompt-text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Enter your prompt here..."
          maxLength={maxChars}
          className="flex-1 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 font-mono text-sm resize-none min-h-[300px]"
          aria-label="Prompt text editor"
        />

        {/* Tags */}
        <div className="mt-4">
          <label className="text-sm font-medium text-gray-700 mb-2 block">Tags</label>
          <div className="flex flex-wrap gap-2 mb-2">
            {tags.map(tag => (
              <span
                key={tag}
                className="inline-flex items-center gap-1 px-3 py-1 bg-indigo-100 text-indigo-800 rounded-full text-sm"
              >
                {tag}
                <button
                  onClick={() => removeTag(tag)}
                  className="hover:bg-indigo-200 rounded-full p-0.5"
                  aria-label={`Remove ${tag} tag`}
                >
                  ×
                </button>
              </span>
            ))}
          </div>
          <input
            type="text"
            value={newTag}
            onChange={(e) => setNewTag(e.target.value)}
            onKeyDown={handleAddTag}
            placeholder="Add tag (press Enter)"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500"
            disabled={tags.length >= 10}
          />
          <p className="text-xs text-gray-500 mt-1">{tags.length}/10 tags</p>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap gap-3 mt-6">
          <button
            onClick={handleSave}
            disabled={!text.trim()}
            className="flex items-center gap-2 px-6 py-2.5 bg-palette-primary text-white rounded-xl hover:bg-palette-primary/90 disabled:bg-gray-300 disabled:cursor-not-allowed font-bold shadow-lg shadow-palette-primary/20 transition-all active:scale-95"
          >
            <Save size={18} /> {parentId ? 'SAVE VERSION' : 'SAVE PROMPT'}
          </button>
          <button
            onClick={() => setShowActiveOptimizer(true)}
            disabled={!text.trim()}
            className="flex items-center gap-2 px-6 py-2.5 bg-palette-dark text-white rounded-xl hover:bg-palette-dark/90 disabled:opacity-50 font-bold shadow-lg shadow-palette-dark/20 transition-all active:scale-95 border border-white/10"
          >
            <Sparkles size={18} /> ACTIVE OPTIMIZE
          </button>
          <button
            onClick={handleRefine}
            disabled={!text.trim() || isRefining}
            className="flex items-center gap-2 px-6 py-2.5 bg-white text-palette-primary border border-palette-primary/20 rounded-xl hover:bg-gray-50 disabled:opacity-50 font-bold transition-all active:scale-95"
          >
            <Zap size={18} className={isRefining ? 'animate-pulse' : ''} /> {isRefining ? 'ANALYZING...' : 'BOLT TIP'}
          </button>
          <button
            onClick={onCancel}
            className="flex items-center gap-2 px-6 py-2.5 bg-white text-gray-400 border border-gray-100 rounded-xl hover:bg-gray-50 font-bold transition-all"
          >
            <XCircle size={18} /> Cancel
          </button>
        </div>

        {refinement && (
          <div className="mt-6 p-4 bg-indigo-50 border border-indigo-100 rounded-xl shadow-sm animate-in fade-in slide-in-from-top-2 duration-300">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-5 h-5 bg-indigo-600 rounded-full flex items-center justify-center">
                <span className="text-white text-[10px] font-bold">!</span>
              </div>
              <h4 className="text-sm font-bold text-indigo-900">
                Optimization Tip: {refinement.weakest_dimension}
              </h4>
            </div>
            <p className="text-sm text-indigo-700 leading-relaxed">
              {refinement.actionable_instruction}
            </p>
          </div>
        )}

        {lastSaved && (
          <p className="text-sm text-gray-500 mt-2">
            Last saved: {lastSaved.toLocaleTimeString()}
          </p>
        )}
      </div>

      {/* Right: Quality Calculator */}
      <div className="lg:col-span-1">
        <QualityCalculator
          scores={qualityScores}
          isLoading={isAnalyzing}
        />

        {/* Active Optimizer Modal Overlay */}
        {showActiveOptimizer && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-palette-dark/60 backdrop-blur-sm animate-in fade-in duration-300">
            <div className="w-full max-w-4xl max-h-[90vh] overflow-y-auto">
              <OptimizationPanel
                promptId={parentId || null}
                promptText={text}
                currentQ={currentQ}
                onOptimized={(newText) => {
                  setText(newText);
                  // Optionally keep panel open to see results, or close it
                  // setShowActiveOptimizer(false);
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
