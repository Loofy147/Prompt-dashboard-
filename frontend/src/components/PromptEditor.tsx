import React, { useState, useEffect, useCallback } from 'react';
import { debounce } from 'lodash';
import QualityCalculator from './QualityCalculator';

interface PromptEditorProps {
  initialText?: string;
  initialTags?: string[];
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
  onSave,
  onCancel
}) => {
  const [text, setText] = useState(initialText);
  const [tags, setTags] = useState<string[]>(initialTags);
  const [newTag, setNewTag] = useState('');
  const [qualityScores, setQualityScores] = useState<QualityScores | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);

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
    }, 500),
    []
  );

  // Trigger analysis when text changes
  useEffect(() => {
    analyzeQuality(text);
  }, [text, analyzeQuality]);

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
  const handleSave = () => {
    if (onSave) {
      onSave({ text, tags });
      setLastSaved(new Date());
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

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full">
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
          className="flex-1 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 font-mono text-sm resize-none"
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
        <div className="flex gap-3 mt-6">
          <button
            onClick={handleSave}
            disabled={!text.trim()}
            className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed font-medium"
          >
            Save Prompt
          </button>
          <button
            onClick={onCancel}
            className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 font-medium"
          >
            Cancel
          </button>
        </div>

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
      </div>
    </div>
  );
};

export default PromptEditor;
